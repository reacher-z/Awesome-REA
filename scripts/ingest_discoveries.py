#!/usr/bin/env python3
"""Ingest a scheduled scan's verified discoveries through a checked pull request, without a person.

``prepare`` writes one discovery batch (see scripts/discoveries.py) from a validated checkpoint into
the working tree. ``run`` is the scheduled-workflow path. It restores and validates this run's
checkpoint artifact with the scanner's own checks, prepares the batch on the current default branch,
runs the repository validators, commits only ``data/discoveries/<batch>.json`` to the
``automation/discovery-ingest`` branch through the Git data API, opens or updates the pull request,
dispatches the required ``validate`` and ``review`` checks, and squash-merges once both pass on the
head commit. If the default branch moves first, it rebuilds the batch on the new commit and repeats,
up to a bounded number of attempts. It never changes any other file, curated record or scan record.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import discoveries  # noqa: E402

BRANCH = discoveries.INGEST_BRANCH
CACHE = '.cache/discovery-ingest'
MAX_ATTEMPTS = 3
CHECK_NAMES = ('validate', 'review')
CHECK_WAIT_SECONDS = 14 * 60
# GitHub recomputes a pull request's mergeability asynchronously after its last check completes; a merge
# requested before that answers 405 although nothing changed. Wait for a mergeable state, bounded.
MERGEABLE_STATES = frozenset({'clean', 'unstable', 'has_hooks'})
MERGEABILITY_WAIT_SECONDS = 4 * 60
MERGE_POLL_SECONDS = 10
MERGE_REQUESTS = 3
# The job has 30 minutes; a new attempt (prepare, validate, checks, merge) needs about 12 of them.
JOB_SECONDS = 28 * 60
ATTEMPT_SECONDS = 12 * 60
POLL_SECONDS = 20
API_TIMEOUT = 30
MAX_API_BYTES = 12 * 1024 * 1024
LABEL = 'Ingest {count} unreviewed discovery records from scan run {run}'


class Retry(Exception):
    """The default branch moved or the head changed; rebuild on the new commit."""


def log(message: str) -> None:
    print(message, flush=True)


def output(name: str, value) -> None:
    path = os.environ.get('GITHUB_OUTPUT')
    if path:
        with open(path, 'a', encoding='utf-8') as stream:
            stream.write(f'{name}={value}\n')


def step_summary(lines: list[str]) -> None:
    path = os.environ.get('GITHUB_STEP_SUMMARY')
    if path:
        with open(path, 'a', encoding='utf-8') as stream:
            stream.write('\n'.join(lines) + '\n')


class GitHub:
    """Minimal REST client: the workflow token stays in memory and is sent only to api.github.com."""

    def __init__(self, repository: str, token: str):
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
            raise ValueError('Invalid repository identity')
        self.repository, self.token = repository, token

    def call(self, method: str, endpoint: str, payload=None, *, expected=(200, 201, 204)):
        url = f'https://api.github.com/repos/{self.repository}/{endpoint}' if endpoint else f'https://api.github.com/repos/{self.repository}'
        data = None if payload is None else json.dumps(payload).encode('utf-8')
        request = urllib.request.Request(url, data=data, method=method, headers={
            'Authorization': f'Bearer {self.token}', 'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'awesome-rea-discovery-ingest',
            **({'Content-Type': 'application/json'} if data is not None else {})})
        try:
            with urllib.request.urlopen(request, timeout=API_TIMEOUT) as response:
                status, body = response.status, response.read(MAX_API_BYTES + 1)
        except urllib.error.HTTPError as error:
            status, body = error.code, error.read(64 * 1024)
            error.close()
        if len(body) > MAX_API_BYTES:
            raise ValueError('GitHub API response exceeds its size bound')
        value = json.loads(body) if body.strip() else None
        if status not in expected:
            message = value.get('message', '') if isinstance(value, dict) else ''
            raise ApiError(status, f'{method} {endpoint.split("?")[0]} returned HTTP {status}: {message[:200]}')
        return status, value

    def get(self, endpoint: str):
        return self.call('GET', endpoint)[1]


class ApiError(RuntimeError):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.run(['git', *args], cwd=cwd, check=True, capture_output=True, encoding='utf-8').stdout.strip()


# --- checkpoint restore -------------------------------------------------------------------------

def restore_checkpoint(repository: str, token: str, run_id: int, run_attempt: int, directory: Path):
    """Download and validate this run's newest checkpoint artifact with the scanner's checks."""
    from scheduled_source_scan import ActionsAPI, MAX_ARCHIVE_BYTES, unpack_checkpoint
    api = ActionsAPI(repository, token, deadline=time.monotonic() + 300)
    artifacts = api.get(f'actions/runs/{run_id}/artifacts?per_page=100')['artifacts']
    candidates = []
    for artifact in artifacts:
        match = re.fullmatch(r'readme-scan-checkpoint-([1-9][0-9]*)', artifact.get('name', ''))
        if match and int(match[1]) <= run_attempt and not artifact.get('expired'):
            candidates.append((int(match[1]), artifact))
    if not candidates:
        raise ValueError('This run saved no checkpoint artifact')
    attempt, artifact = max(candidates, key=lambda item: item[0])
    if (artifact.get('workflow_run', {}).get('id') != run_id
            or not 0 < artifact.get('size_in_bytes', 0) <= MAX_ARCHIVE_BYTES):
        raise ValueError('Checkpoint artifact is not bound to this run or exceeds its bounds')
    run = api.get(f'actions/runs/{run_id}/attempts/{attempt}')
    if run.get('path') != discoveries.WORKFLOW_PATH or run.get('head_repository', {}).get('full_name') != repository:
        raise ValueError('Checkpoint artifact does not come from the scheduled scan workflow')
    archive = directory / 'artifact.zip'
    api.download(f"actions/artifacts/{artifact['id']}/zip", archive)
    receipt = {}
    document, _, _ = unpack_checkpoint(archive, artifact, run, directory / 'checkpoint', receipt_out=receipt)
    receipt_bytes = directory / 'receipt.json'
    with zipfile.ZipFile(archive) as bundle:
        receipt_bytes.write_bytes(bundle.read('receipt.json'))
    source = {
        'repository': repository, 'workflow_path': discoveries.WORKFLOW_PATH,
        'workflow_id': run['workflow_id'], 'run_id': run_id, 'run_attempt': attempt,
        'event': run['event'], 'head_sha': run['head_sha'], 'artifact_id': artifact['id'],
        'artifact_name': artifact['name'], 'artifact_digest': artifact['digest'],
        'checkpoint_sha256': receipt['checkpoint_sha256'],
        'receipt_sha256': hashlib.sha256(receipt_bytes.read_bytes()).hexdigest(),
    }
    (directory / 'source.json').write_text(json.dumps(source, indent=2) + '\n', encoding='utf-8')
    (directory / 'receipt-parsed.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    return document, receipt, source


# --- prepare --------------------------------------------------------------------------------------

def prepare(checkpoint: Path, receipt_path: Path, source_path: Path, *, root: Path = ROOT,
            ingested_at: str | None = None) -> tuple[Path | None, str, int]:
    """Write the batch for this checkpoint into ``root``; return (path, status, record count)."""
    import strict_json
    document = strict_json.load_path(checkpoint)
    receipt = strict_json.load_path(receipt_path)
    source = strict_json.load_path(source_path)
    batches, problems = discoveries.load_batches(root)
    if problems:
        raise ValueError('Existing discovery batches are invalid: ' + '; '.join(problems[:3]))
    name = f"run-{source['run_id']}-{source['run_attempt']}"
    if any(batch['batch_id'] == name for batch in batches):
        return None, 'already-ingested', 0
    existing = discoveries.existing_identities(root, batches)
    batch, status = discoveries.build_batch(document, receipt, source, existing, discoveries.curated_urls(root),
                                            ingested_at=ingested_at or discoveries.utc_now())
    if batch is None:
        return None, status, 0
    problems = discoveries.validate_batch(batch, batch['batch_id'])
    if problems:
        raise ValueError('Prepared batch failed validation: ' + '; '.join(problems[:3]))
    path = Path(root) / discoveries.DIRECTORY / f"{batch['batch_id']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(discoveries.batch_bytes(batch))
    return path, status, len(batch['resources'])


def run_validators(root: Path) -> None:
    """The repository validators, plus any privacy regression test, before anything is committed."""
    commands = [[sys.executable, 'scripts/validate.py'], [sys.executable, 'scripts/discoveries.py']]
    privacy_tests = sorted(path.stem for path in (root / 'tests').glob('test_privacy*.py'))
    if privacy_tests:
        commands.append([sys.executable, '-m', 'unittest', *(f'tests.{name}' for name in privacy_tests)])
    for command in commands:
        result = subprocess.run(command, cwd=root, capture_output=True, encoding='utf-8')
        if result.returncode:
            tail = (result.stderr or result.stdout).strip().splitlines()[-15:]
            raise RuntimeError(f"{' '.join(command[1:])} failed:\n" + '\n'.join(tail))


# --- pull request ---------------------------------------------------------------------------------

def commit_batch(github: GitHub, base_sha: str, path: Path, message: str) -> str:
    """Create one commit on ``base_sha`` that adds the batch file, and point the branch at it."""
    relative = path.relative_to(ROOT).as_posix()
    if not re.fullmatch(r'data/discoveries/run-[0-9]+-[0-9]+\.json', relative):
        raise ValueError('The ingest commits only a discovery batch file')
    base_commit = github.get(f'git/commits/{base_sha}')
    blob = github.call('POST', 'git/blobs', {'content': base64.b64encode(path.read_bytes()).decode('ascii'),
                                             'encoding': 'base64'})[1]
    tree = github.call('POST', 'git/trees', {'base_tree': base_commit['tree']['sha'], 'tree': [
        {'path': relative, 'mode': '100644', 'type': 'blob', 'sha': blob['sha']}]})[1]
    commit = github.call('POST', 'git/commits', {'message': message, 'tree': tree['sha'], 'parents': [base_sha]})[1]
    status, _ = github.call('PATCH', f'git/refs/heads/{BRANCH}', {'sha': commit['sha'], 'force': True},
                            expected=(200, 422))
    if status == 422:
        github.call('POST', 'git/refs', {'ref': f'refs/heads/{BRANCH}', 'sha': commit['sha']})
    return commit['sha']


def pull_request_body(count: int, source: dict, batch_path: Path, attempt: int) -> str:
    run_url = f"https://github.com/{source['repository']}/actions/runs/{source['run_id']}"
    return '\n'.join([
        f'Automated discovery ingest from [scan run {source["run_id"]}]({run_url}) (attempt {source["run_attempt"]}).',
        '',
        f'Adds `{batch_path.relative_to(ROOT).as_posix()}` with {count} exact README capture records copied unchanged '
        'from the validated checkpoint artifact. Each has an explicit Git blob hash match, passes the '
        f'`{discoveries.POLICY}` topic screen and the publication record checks, and is new to the source index, '
        'the public supplements, the curated catalog and earlier discovery batches. The records stay '
        '`automated-readme-scan` and `unreviewed`: no source review, translation, curation, runtime test or '
        'endorsement is implied, and no other file changes.',
        '',
        f'Provenance: artifact `{source["artifact_name"]}` ({source["artifact_digest"]}), checkpoint SHA-256 '
        f'`{source["checkpoint_sha256"]}`, scanner commit `{source["head_sha"][:12]}`.',
        '',
        '## Validation',
        '',
        '- [x] `python3 scripts/validate.py` and `python3 scripts/discoveries.py` on the default branch plus this batch, before committing.',
        '- [x] The required `validate` and `review` checks are dispatched on this head commit; the ingest merges only after both pass.',
        '',
        f'Ingest attempt {attempt} of {MAX_ATTEMPTS}. This pull request is opened, checked and squash-merged by the '
        '`Scheduled README discovery` workflow under the repository\'s automated discovery path (docs/automation.md).',
    ])


def open_or_update_pull(github: GitHub, default_branch: str, title: str, body: str) -> int:
    owner = github.repository.split('/')[0]
    pulls = github.get(f'pulls?state=open&head={owner}:{BRANCH}&base={default_branch}&per_page=10')
    if pulls:
        number = pulls[0]['number']
        github.call('PATCH', f'pulls/{number}', {'title': title, 'body': body})
        return number
    return github.call('POST', 'pulls', {'title': title, 'head': BRANCH, 'base': default_branch, 'body': body})[1]['number']


def dispatch_checks(github: GitHub, default_branch: str, number: int, head_sha: str) -> None:
    github.call('POST', 'actions/workflows/validate.yml/dispatches', {'ref': BRANCH})
    github.call('POST', 'actions/workflows/review.yml/dispatches',
                {'ref': default_branch, 'inputs': {'pr_number': str(number), 'head_sha': head_sha}})


def check_results(github: GitHub, sha: str) -> dict:
    """Each required check's state on ``sha``, from the commit status its dispatched run reports.

    Branch protection counts those statuses, not the check runs of dispatched workflows. A completed check
    run that failed without reporting a status still ends the wait.
    """
    statuses = {}
    # The combined status lists the newest status per context first; keep the first one for each context.
    for status in github.get(f'commits/{sha}/status').get('statuses', []):
        statuses.setdefault(status['context'], status['state'])
    results = {}
    for name in CHECK_NAMES:
        state = statuses.get(name)
        if state == 'success':
            results[name] = ('completed', 'success')
        elif state in ('failure', 'error'):
            results[name] = ('completed', 'failure')
        else:
            runs = github.get(f'commits/{sha}/check-runs?check_name={name}&per_page=30')['check_runs']
            # GitHub Actions is the app branch protection requires for both checks.
            runs = [run for run in runs if (run.get('app') or {}).get('slug') == 'github-actions']
            latest = max(runs, key=lambda run: run['id']) if runs else None
            if latest and latest['status'] == 'completed' and latest['conclusion'] != 'success':
                results[name] = ('completed', latest['conclusion'])
            else:
                results[name] = ('pending' if latest else 'missing', None)
    return results


def wait_for_checks(github: GitHub, sha: str, default_branch: str, base_sha: str) -> dict:
    deadline = time.monotonic() + CHECK_WAIT_SECONDS
    while True:
        results = check_results(github, sha)
        if all(status == 'completed' for status, _ in results.values()):
            return results
        if github.get(f'branches/{default_branch}')['commit']['sha'] != base_sha:
            raise Retry('the default branch moved while the checks ran')
        if time.monotonic() >= deadline:
            raise RuntimeError(f'Required checks did not finish in time: {results}')
        time.sleep(POLL_SECONDS)


def wait_until_mergeable(github: GitHub, number: int, sha: str, default_branch: str, base_sha: str) -> str:
    """Wait for GitHub to finish computing mergeability after the checks; rebuild only if the branch is stale."""
    deadline = time.monotonic() + MERGEABILITY_WAIT_SECONDS
    while True:
        pull = github.get(f'pulls/{number}')
        state = pull.get('mergeable_state')
        if pull['head']['sha'] != sha:
            raise Retry('the pull request head changed')
        if state in MERGEABLE_STATES:
            return state
        if state in ('behind', 'dirty') or github.get(f'branches/{default_branch}')['commit']['sha'] != base_sha:
            raise Retry(f'the pull request is {state} or the default branch moved')
        if time.monotonic() >= deadline:
            raise RuntimeError(f'Pull request #{number} stayed {state!r} for {MERGEABILITY_WAIT_SECONDS} s after both required '
                               'checks passed on its up-to-date head; branch protection did not accept them.')
        time.sleep(MERGE_POLL_SECONDS)


def merge(github: GitHub, number: int, sha: str, title: str, default_branch: str | None = None,
          base_sha: str | None = None) -> str:
    """Squash-merge exactly ``sha``. A refusal while the branch is still current is retried a few times."""
    for request in range(1, MERGE_REQUESTS + 1):
        try:
            _, value = github.call('PUT', f'pulls/{number}/merge', {
                'merge_method': 'squash', 'sha': sha, 'commit_title': f'{title} (#{number})',
                'commit_message': 'Automated discovery ingest; the records stay unreviewed automated README scans.'})
            return value['sha']
        except ApiError as error:
            if error.status not in (405, 409):
                raise
            moved = default_branch is None or github.get(f'branches/{default_branch}')['commit']['sha'] != base_sha
            if moved or error.status == 409 or request == MERGE_REQUESTS:
                raise Retry(str(error)) from None
            log(f'MERGE_REFUSED request={request}: {error}; the branch is current, asking again')
            time.sleep(MERGE_POLL_SECONDS * request)
    raise AssertionError('unreachable')


def close_pull(github: GitHub, number: int, reason: str) -> None:
    github.call('POST', f'issues/{number}/comments', {'body': reason})
    github.call('PATCH', f'pulls/{number}', {'state': 'closed'})


def refresh_tree(default_branch: str) -> str:
    """Move the checkout to the default branch's current commit; nothing in it is kept."""
    git('fetch', '--quiet', '--depth=1', 'origin', default_branch)
    sha = git('rev-parse', 'FETCH_HEAD')
    git('checkout', '--quiet', '--force', '--detach', sha)
    git('clean', '-fdq', '--', discoveries.DIRECTORY)
    return sha


def run() -> int:
    repository, token = os.environ['GITHUB_REPOSITORY'], os.environ['GH_TOKEN']
    default_branch = os.environ['DEFAULT_BRANCH']
    if os.environ.get('GITHUB_REF') != f'refs/heads/{default_branch}':
        raise ValueError('The ingest runs only from the default branch')
    run_id, run_attempt = int(os.environ['GITHUB_RUN_ID']), int(os.environ['GITHUB_RUN_ATTEMPT'])
    github = GitHub(repository, token)
    cache = ROOT / CACHE
    cache.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    _, receipt, source = restore_checkpoint(repository, token, run_id, run_attempt, cache)
    checkpoint = cache / 'checkpoint' / 'checkpoint.json'
    log(f"CHECKPOINT run={source['run_id']} attempt={source['run_attempt']} outcome={receipt['outcome']} "
        f"new_verified={receipt.get('new_qualified_successful_scans')}")
    number = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        if attempt > 1 and time.monotonic() - started > JOB_SECONDS - ATTEMPT_SECONDS:
            raise RuntimeError(f'The default branch kept moving and no time is left for attempt {attempt} (PR #{number}); '
                               'the next scheduled run ingests these records again.')
        base_sha = refresh_tree(default_branch)
        # The batch is prepared by the default branch's current code, in a separate process.
        result = subprocess.run([sys.executable, 'scripts/ingest_discoveries.py', 'prepare',
                                 '--checkpoint', str(checkpoint), '--receipt', str(cache / 'receipt-parsed.json'),
                                 '--source', str(cache / 'source.json')], cwd=ROOT, capture_output=True, encoding='utf-8')
        if result.returncode:
            raise RuntimeError('prepare failed:\n' + '\n'.join((result.stderr or result.stdout).splitlines()[-15:]))
        prepared = json.loads(result.stdout.strip().splitlines()[-1])
        log(f"PREPARE attempt={attempt} base={base_sha[:12]} status={prepared['status']} records={prepared['records']}")
        if prepared['path'] is None:
            output('status', prepared['status'])
            step_summary([f"Discovery ingest: {prepared['status']} (scan run {source['run_id']})."])
            if prepared['status'] == 'budget-reached':
                raise RuntimeError('The discovery budget is reached; raising it is a reviewed change (data/discoveries/README.md).')
            return 0
        run_validators(ROOT)
        path = ROOT / prepared['path']
        title = LABEL.format(count=prepared['records'], run=source['run_id'])
        head_sha = commit_batch(github, base_sha, path, title)
        number = open_or_update_pull(github, default_branch, title,
                                     pull_request_body(prepared['records'], source, path, attempt))
        log(f'PULL_REQUEST number={number} head={head_sha[:12]} merge_state='
            f"{github.get(f'pulls/{number}').get('mergeable_state')}")
        dispatch_checks(github, default_branch, number, head_sha)
        try:
            results = wait_for_checks(github, head_sha, default_branch, base_sha)
            log(f'CHECKS {results}')
            if any(conclusion != 'success' for _, conclusion in results.values()):
                raise RuntimeError(f'Required checks failed on {head_sha[:12]}: {results}')
            state = wait_until_mergeable(github, number, head_sha, default_branch, base_sha)
            log(f'MERGE_STATE before merge: {state}')
            merged = merge(github, number, head_sha, title, default_branch, base_sha)
        except Retry as reason:
            log(f'RETRY attempt={attempt}: {reason}')
            continue
        # Cloudflare Pages builds production from the new main commit through its own Git integration.
        github.call('DELETE', f'git/refs/heads/{BRANCH}', expected=(204, 422))
        elapsed = round(time.monotonic() - started)
        log(f"MERGED number={number} sha={merged} records={prepared['records']} elapsed_seconds={elapsed}")
        for name, value in (('status', 'merged'), ('pr', number), ('merge_sha', merged), ('records', prepared['records'])):
            output(name, value)
        step_summary([f"Discovery ingest merged #{number} ({merged[:12]}): {prepared['records']} unreviewed records "
                      f"from scan run {source['run_id']} in {elapsed} s."])
        return 0
    raise RuntimeError(f'The pull request could not be merged after {MAX_ATTEMPTS} attempts (PR #{number}); see the RETRY lines above.')


# --- failure tracking ------------------------------------------------------------------------------

TRACKERS = {
    'readme-discovery': 'Scheduled README discovery and discovery ingest are failing',
    'artifact-leads': 'Public artifact lead discovery is failing',
}
FAILED_RESULTS = {'failure', 'cancelled'}


def tracker_marker(key: str) -> str:
    return f'<!-- awesome-rea-automation-tracker:{key} -->'


def tracker_state(body: str) -> dict:
    match = re.search(r'<!-- tracker-state: (\{.*?\}) -->', body or '')
    try:
        state = json.loads(match[1]) if match else {}
    except ValueError:
        state = {}
    return state if isinstance(state, dict) else {}


def tracker_body(key: str, state: dict, results: dict, run_url: str, last_ingest: str | None,
                 repository: str = discoveries.REPOSITORY) -> str:
    rows = '\n'.join(f'| {name} job | {result} |' for name, result in results.items())
    return '\n'.join([
        tracker_marker(key),
        f'<!-- tracker-state: {json.dumps(state, sort_keys=True)} -->',
        f'{TRACKERS[key]}. The workflow updates this issue on every failed scheduled or manual run and closes it '
        'when every failed job has succeeded again; it is the one tracking issue for this automation, so further failures edit it '
        'instead of opening new issues.',
        '',
        '| | |',
        '| --- | --- |',
        f"| First failure in this streak | {state['first_failure_at']} ([run]({state['first_run_url']})) |",
        f"| Latest failure | {state['last_failure_at']} ([run]({run_url})) |",
        f"| Consecutive failed runs | {state['count']} |",
        f"| Jobs that must succeed again | {', '.join(state['failed_jobs'])} |",
        rows,
        f"| Last successful discovery ingest | {last_ingest or 'none recorded'} |",
        '',
        'Open the latest run for the failing step. Scan failures keep the previous checkpoint; an ingest failure '
        'leaves its pull request open for inspection, and the next successful run supersedes it. See '
        f'[repository automation](https://github.com/{repository}/blob/main/docs/automation.md#automated-discovery-ingest).',
    ])


def report(key: str, results: dict) -> int:
    """Keep one tracking issue per automation: open or update it on failure, close it on recovery."""
    repository, token = os.environ['GITHUB_REPOSITORY'], os.environ['GH_TOKEN']
    github = GitHub(repository, token)
    run_url = f"https://github.com/{repository}/actions/runs/{int(os.environ['GITHUB_RUN_ID'])}"
    failed = any(result in FAILED_RESULTS for result in results.values())
    marker = tracker_marker(key)
    issues = github.get('issues?state=all&creator=github-actions%5Bbot%5D&per_page=100&sort=created&direction=desc')
    tracked = [issue for issue in issues if 'pull_request' not in issue and marker in (issue.get('body') or '')]
    issue = next((item for item in tracked if item['state'] == 'open'), None) or (tracked[0] if tracked else None)
    try:
        last_ingest = discoveries.summary(ROOT)['last_successful_ingest_at']
    except (OSError, ValueError):
        last_ingest = None
    stamp = discoveries.utc_now()
    previous = tracker_state(issue['body']) if issue and issue['state'] == 'open' else {}
    if not failed:
        if issue and issue['state'] == 'open':
            # Recovery means every stage that failed in this streak has succeeded again, not merely been skipped.
            pending = [job for job in previous.get('failed_jobs', sorted(results)) if results.get(job) != 'success']
            if pending:
                log(f"TRACKER kept #{issue['number']} open; still waiting for {', '.join(pending)}")
                return 0
            github.call('POST', f"issues/{issue['number']}/comments",
                        {'body': f'Recovered: [this run]({run_url}) succeeded at {stamp} ({", ".join(f"{k}: {v}" for k, v in results.items())}). Closing.'})
            github.call('PATCH', f"issues/{issue['number']}", {'state': 'closed', 'state_reason': 'completed'})
            log(f"TRACKER closed #{issue['number']}")
        return 0
    failed_jobs = sorted(set(previous.get('failed_jobs', [])) | {job for job, result in results.items() if result in FAILED_RESULTS})
    state = {'first_failure_at': previous.get('first_failure_at', stamp), 'first_run_url': previous.get('first_run_url', run_url),
             'last_failure_at': stamp, 'count': int(previous.get('count', 0)) + 1, 'failed_jobs': failed_jobs}
    body = tracker_body(key, state, results, run_url, last_ingest, repository)
    if issue and issue['state'] == 'open':
        # Editing the body does not notify watchers; only the start of a failure streak does.
        github.call('PATCH', f"issues/{issue['number']}", {'body': body})
        log(f"TRACKER updated #{issue['number']} count={state['count']}")
    elif issue:
        github.call('PATCH', f"issues/{issue['number']}", {'state': 'open', 'body': body})
        github.call('POST', f"issues/{issue['number']}/comments", {'body': f'Failing again: [run]({run_url}) at {stamp}.'})
        log(f"TRACKER reopened #{issue['number']}")
    else:
        number = github.call('POST', 'issues', {'title': TRACKERS[key], 'body': body})[1]['number']
        log(f'TRACKER opened #{number}')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest='command', required=True)
    prepare_parser = commands.add_parser('prepare', help='write one batch from a validated checkpoint')
    prepare_parser.add_argument('--checkpoint', type=Path, required=True)
    prepare_parser.add_argument('--receipt', type=Path, required=True)
    prepare_parser.add_argument('--source', type=Path, required=True)
    prepare_parser.add_argument('--ingested-at', help='UTC timestamp to record (default: now)')
    commands.add_parser('run', help='the scheduled workflow path')
    report_parser = commands.add_parser('report', help='update the failure tracking issue for one automation')
    report_parser.add_argument('--tracker', choices=sorted(TRACKERS), required=True)
    report_parser.add_argument('--result', action='append', default=[], metavar='JOB=RESULT',
                               help='a job and its result, such as scan=success; repeat for each job')
    args = parser.parse_args()
    if args.command == 'report':
        results = {}
        for item in args.result:
            job, _, value = item.partition('=')
            if not re.fullmatch(r'[a-z-]+', job) or value not in ('success', 'failure', 'cancelled', 'skipped', ''):
                raise ValueError('Each --result is JOB=success|failure|cancelled|skipped')
            results[job] = value or 'skipped'
        return report(args.tracker, results)
    if args.command == 'prepare':
        path, status, count = prepare(args.checkpoint, args.receipt, args.source, ingested_at=args.ingested_at)
        print(json.dumps({'path': path.relative_to(ROOT).as_posix() if path else None, 'status': status, 'records': count}))
        return 0
    return run()


if __name__ == '__main__':
    raise SystemExit(main())
