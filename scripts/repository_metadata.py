#!/usr/bin/env python3
"""GitHub repository facts for curated resource pages: stars, last default-branch commit, primary language and detected license.

data/repository-metadata.json holds one dated observation per GitHub repository that a curated record's `url`
names. The page builders only read it; a missing file, a missing repository or a malformed entry leaves that fact
off the page, so a build never depends on GitHub. Refresh the snapshot with

    python3 scripts/repository_metadata.py --refresh

which reads GITHUB_TOKEN (or `gh auth token`) and sends one GraphQL query per 50 repositories. The detected
license is GitHub's signal, not a license review (docs/artifact-evidence.md), so pages label it as such and
structured data never carries it.

The daily `Repository metadata refresh` workflow runs `python3 scripts/repository_metadata.py publish`: it reads
the snapshot again with the workflow token and, when any fact changed, commits it through a pull request that it
checks and merges itself, as the discovery ingest does (docs/automation.md#repository-metadata-refresh). A run
that fails anywhere leaves the committed snapshot unchanged.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
from functools import lru_cache
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / 'data/repository-metadata.json'
CATALOGS = (ROOT / 'data/tool-resources.json', ROOT / 'data/rea-resources.json')
BATCH = 50
# A bounded run: at most MAX_REPOSITORIES / BATCH GraphQL queries, and it stops, writing nothing, when the
# token's GraphQL budget gets low or GitHub reports an error other than a repository it cannot resolve.
MAX_REPOSITORIES = 10_000
MIN_RATE_REMAINING = 100
# A refresh that resolves fewer than this share of the catalog's GitHub repositories is refused.
MIN_KEPT = 0.9
BRANCH = 'automation/repository-metadata'
TITLE = 'Refresh GitHub facts for {count} curated repositories'
NAME = re.compile(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})/[A-Za-z0-9._-]{1,100}')
SPDX = re.compile(r'[A-Za-z0-9.+-]{1,64}')
DATETIME = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z')


def repository_key(url: str) -> str | None:
    """`owner/name` in lower case when ``url`` is a GitHub repository root, else None."""
    match = re.fullmatch(r'https://github\.com/([^/?#]+)/([^/?#]+?)(?:\.git)?/?', url or '')
    if not match:
        return None
    key = f'{match[1]}/{match[2]}'
    return key.lower() if NAME.fullmatch(key) else None


def _clean(entry) -> dict:
    """Keep only well-formed facts; anything else is dropped rather than shown."""
    if not isinstance(entry, dict):
        return {}
    facts = {}
    if type(entry.get('stars')) is int and entry['stars'] >= 0:
        facts['stars'] = entry['stars']
    if isinstance(entry.get('committed_at'), str) and DATETIME.fullmatch(entry['committed_at']):
        facts['committed_at'] = entry['committed_at']
    if isinstance(entry.get('language'), str) and 0 < len(entry['language']) <= 40 and '<' not in entry['language']:
        facts['language'] = entry['language']
    if isinstance(entry.get('license'), str) and SPDX.fullmatch(entry['license']) and entry['license'] != 'NOASSERTION':
        facts['license'] = entry['license']
    if entry.get('archived') is True:
        facts['archived'] = True
    return facts


@lru_cache(maxsize=4)
def _snapshot(path: str) -> tuple[str | None, dict]:
    try:
        document = json.loads(Path(path).read_text(encoding='utf-8'))
        observed = document['observed_at']
        repositories = document['repositories']
    except (OSError, ValueError, KeyError, TypeError):
        return None, {}
    if not (isinstance(observed, str) and DATETIME.fullmatch(observed)) or not isinstance(repositories, dict):
        return None, {}
    return observed, repositories


def repository_facts(record: dict, path: Path = SNAPSHOT) -> dict:
    """The record's repository facts plus `observed_at`, or {} when the snapshot has none."""
    key = repository_key(record.get('url', ''))
    if not key:
        return {}
    observed, repositories = _snapshot(str(path))
    facts = _clean(repositories.get(key))
    return {**facts, 'observed_at': observed} if facts else {}


QUERY_FIELDS = ('stargazerCount isArchived primaryLanguage { name } licenseInfo { spdxId } '
                'defaultBranchRef { target { ... on Commit { committedDate } } }')


def _token() -> str:
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if not token:
        token = subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True, encoding='utf-8', check=False).stdout.strip()
    if not token:
        raise SystemExit('Set GITHUB_TOKEN or sign in with gh to refresh repository metadata.')
    return token


def _missing_repository(error, data: dict) -> bool:
    if not isinstance(error, dict):
        return False
    path = error.get('path')
    return (error.get('type') == 'NOT_FOUND' and isinstance(path, list) and len(path) == 1 and isinstance(path[0], str)
            and re.fullmatch(r'r\d+', path[0]) is not None and path[0] in data and data[path[0]] is None)


def observed_at(path: Path = SNAPSHOT) -> str | None:
    return _snapshot(str(path))[0]


def _query(token: str, keys: list[str]) -> dict:
    parts = []
    for index, key in enumerate(keys):
        owner, name = key.split('/')
        parts.append(f'r{index}: repository(owner: {json.dumps(owner)}, name: {json.dumps(name)}) {{ {QUERY_FIELDS} }}')
    parts.append('rateLimit { cost remaining }')
    body = json.dumps({'query': '{ ' + ' '.join(parts) + ' }'}).encode('utf-8')
    request = Request('https://api.github.com/graphql', data=body, method='POST',
                      headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json',
                               'User-Agent': 'awesome-rea-metadata'})
    for attempt in range(3):
        try:
            with urlopen(request, timeout=60) as response:
                document = json.load(response)
            break
        except OSError as error:
            if attempt == 2:
                # Stop before writing: a partial snapshot would drop these repositories from their pages.
                raise SystemExit(f'A GitHub batch failed three times ({error}); the snapshot is unchanged.')
            time.sleep(5 * (attempt + 1))
    data = document.get('data') or {}
    # A repository GitHub cannot resolve is a top-level NOT_FOUND error on its alias, whose node is null; any other
    # error stops the refresh (the same rule as scan_graphql_transport._only_missing_repositories).
    errors = [error for error in document.get('errors') or [] if not _missing_repository(error, data)]
    if errors or not data:
        first = errors[0] if errors and isinstance(errors[0], dict) else {}
        raise SystemExit(f"GitHub returned {first.get('type') or first.get('message') or 'an error' if errors else 'no data'} "
                         'for a batch; the snapshot is unchanged.')
    remaining = (data.get('rateLimit') or {}).get('remaining')
    if type(remaining) is int and remaining < MIN_RATE_REMAINING:
        raise SystemExit(f'Only {remaining} GraphQL points are left; the snapshot is unchanged.')
    found = {}
    for index, key in enumerate(keys):
        node = data.get(f'r{index}')
        if not node:
            continue
        found[key] = _clean({'stars': node.get('stargazerCount'), 'committed_at': ((node.get('defaultBranchRef') or {}).get('target') or {}).get('committedDate'),
                             'language': (node.get('primaryLanguage') or {}).get('name'),
                             'license': (node.get('licenseInfo') or {}).get('spdxId'),
                             'archived': node.get('isArchived')})
    return found


def catalog_keys() -> list[str]:
    return sorted({key for catalog in CATALOGS for record in json.loads(catalog.read_text(encoding='utf-8'))
                   if (key := repository_key(record.get('url', '')))})


def fetch(keys: list[str]) -> dict:
    """A new snapshot document for ``keys``; raises SystemExit, having written nothing, if the read is incomplete."""
    if len(keys) > MAX_REPOSITORIES:
        raise SystemExit(f'{len(keys)} repositories exceed the {MAX_REPOSITORIES} per-run cap; the snapshot is unchanged.')
    token = _token()
    observed = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    repositories = {}
    for start in range(0, len(keys), BATCH):
        repositories.update(_query(token, keys[start:start + BATCH]))
        print(f'{min(start + BATCH, len(keys))} of {len(keys)}', file=sys.stderr, flush=True)
    if len(repositories) < MIN_KEPT * len(keys):
        raise SystemExit(f'GitHub resolved {len(repositories)} of {len(keys)} repositories; the snapshot is unchanged.')
    # Every fact carries the one observation date; a repository the API did not return is left out.
    return {'observed_at': observed, 'source': 'GitHub GraphQL API', 'repositories': dict(sorted(repositories.items()))}


def snapshot_bytes(document: dict) -> bytes:
    return (json.dumps(document, indent=1, ensure_ascii=False, sort_keys=False) + '\n').encode('utf-8')


def refresh(path: Path = SNAPSHOT) -> tuple[int, int]:
    keys = catalog_keys()
    document = fetch(keys)
    path.write_bytes(snapshot_bytes(document))
    return len(document['repositories']), len(keys)


def changed(document: dict, path: Path = SNAPSHOT) -> bool:
    """Whether any repository fact differs from the snapshot at ``path``; the observation date alone does not count."""
    try:
        current = json.loads(path.read_text(encoding='utf-8')).get('repositories')
    except (OSError, ValueError, AttributeError):
        return True
    return current != document['repositories']


def commit_snapshot(github, base_sha: str, content: bytes, message: str) -> str:
    """One commit on ``base_sha`` that replaces the snapshot; the refresh branch is pointed at it."""
    base_commit = github.get(f'git/commits/{base_sha}')
    blob = github.call('POST', 'git/blobs', {'content': base64.b64encode(content).decode('ascii'), 'encoding': 'base64'})[1]
    tree = github.call('POST', 'git/trees', {'base_tree': base_commit['tree']['sha'], 'tree': [
        {'path': SNAPSHOT.relative_to(ROOT).as_posix(), 'mode': '100644', 'type': 'blob', 'sha': blob['sha']}]})[1]
    commit = github.call('POST', 'git/commits', {'message': message, 'tree': tree['sha'], 'parents': [base_sha]})[1]
    status, _ = github.call('PATCH', f'git/refs/heads/{BRANCH}', {'sha': commit['sha'], 'force': True}, expected=(200, 422))
    if status == 422:
        github.call('POST', 'git/refs', {'ref': f'refs/heads/{BRANCH}', 'sha': commit['sha']})
    return commit['sha']


def pull_request_body(document: dict, total: int, run_url: str, attempt: int) -> str:
    return '\n'.join([
        f'Automated repository metadata refresh from [run]({run_url}).',
        '',
        f"Replaces `data/repository-metadata.json` with GitHub's current stars, last default-branch commit, primary "
        f"language, detected license and archive flag for {len(document['repositories'])} of the {total} GitHub "
        f"repositories that curated records name, observed at {document['observed_at']}. No other file changes.",
        '',
        '## Validation',
        '',
        '- [x] `python3 scripts/validate.py` on the default branch plus this snapshot, before committing.',
        '- [x] The required `validate` and `review` checks are dispatched on this head commit; the job merges only after both pass.',
        '',
        f'Attempt {attempt}. This pull request is opened, checked and rebase-merged by the `Repository metadata refresh` '
        'workflow (docs/automation.md#repository-metadata-refresh).',
    ])


def publish() -> int:
    """The scheduled path: read once, then commit, check and merge on the current default branch if anything changed."""
    import ingest_discoveries as ingest
    repository, token = os.environ['GITHUB_REPOSITORY'], os.environ['GH_TOKEN']
    default_branch = os.environ['DEFAULT_BRANCH']
    if os.environ.get('GITHUB_REF') != f'refs/heads/{default_branch}':
        raise ValueError('The metadata refresh runs only from the default branch')
    run_url = f"https://github.com/{repository}/actions/runs/{os.environ['GITHUB_RUN_ID']}"
    started, number = time.monotonic(), None
    keys = catalog_keys()
    # The snapshot this run read against; if main gets a different one meanwhile, this run's older read must not replace it.
    starting = SNAPSHOT.read_bytes() if SNAPSHOT.is_file() else None
    document = fetch(keys)
    if not changed(document, SNAPSHOT):
        ingest.output('status', 'unchanged')
        ingest.step_summary([f"Repository metadata: no fact changed for {len(document['repositories'])} repositories."])
        return 0
    content = snapshot_bytes(document)
    github = ingest.GitHub(repository, token)
    title = TITLE.format(count=len(document['repositories']))
    for attempt in range(1, ingest.MAX_ATTEMPTS + 1):
        if attempt > 1 and time.monotonic() - started > ingest.JOB_SECONDS - ingest.ATTEMPT_SECONDS:
            raise RuntimeError(f'The default branch kept moving and no time is left for attempt {attempt} (PR #{number}).')
        base_sha = ingest.refresh_tree(default_branch)
        if (SNAPSHOT.read_bytes() if SNAPSHOT.is_file() else None) != starting:
            raise RuntimeError('The snapshot on the default branch changed during this run; the next run refreshes from it.')
        SNAPSHOT.write_bytes(content)
        try:
            ingest.run_validators(ROOT)
        finally:
            subprocess.run(['git', 'checkout', '--quiet', '--', SNAPSHOT.relative_to(ROOT).as_posix()], cwd=ROOT, check=True)
        head_sha = commit_snapshot(github, base_sha, content, title)
        owner = repository.split('/')[0]
        body = pull_request_body(document, len(keys), run_url, attempt)
        pulls = github.get(f'pulls?state=open&head={owner}:{BRANCH}&base={default_branch}&per_page=10')
        if pulls:
            number = pulls[0]['number']
            github.call('PATCH', f'pulls/{number}', {'title': title, 'body': body})
        else:
            number = github.call('POST', 'pulls', {'title': title, 'head': BRANCH, 'base': default_branch, 'body': body})[1]['number']
        ingest.log(f'PULL_REQUEST number={number} head={head_sha[:12]}')
        github.call('POST', 'actions/workflows/validate.yml/dispatches', {'ref': BRANCH})
        github.call('POST', 'actions/workflows/review.yml/dispatches',
                    {'ref': default_branch, 'inputs': {'pr_number': str(number), 'head_sha': head_sha}})
        try:
            results = ingest.wait_for_checks(github, head_sha, default_branch, base_sha)
            ingest.log(f'CHECKS {results}')
            if any(conclusion != 'success' for _, conclusion in results.values()):
                raise RuntimeError(f'Required checks failed on {head_sha[:12]}: {results}')
            ingest.wait_until_mergeable(github, number, head_sha, default_branch, base_sha)
            merged = ingest.merge(github, number, head_sha, title, default_branch, base_sha)
        except ingest.Retry as reason:
            ingest.log(f'RETRY attempt={attempt}: {reason}')
            continue
        github.call('DELETE', f'git/refs/heads/{BRANCH}', expected=(204, 422))
        for name, value in (('status', 'merged'), ('pr', number), ('merge_sha', merged)):
            ingest.output(name, value)
        ingest.step_summary([f"Repository metadata merged #{number} ({merged[:12]}): {len(document['repositories'])} "
                             f"repositories observed at {document['observed_at']}."])
        return 0
    raise RuntimeError(f'The default branch kept moving; gave up after {ingest.MAX_ATTEMPTS} attempts (PR #{number}).')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--refresh', action='store_true', help='read every curated GitHub repository and rewrite the snapshot')
    parser.add_argument('command', nargs='?', choices=('publish',),
                        help='publish: the scheduled workflow path, committing a changed snapshot through a checked pull request')
    args = parser.parse_args()
    if args.command == 'publish':
        return publish()
    if not args.refresh:
        observed, repositories = _snapshot(str(SNAPSHOT))
        print(f'{len(repositories)} repositories observed at {observed}.')
        return 0
    read, total = refresh()
    print(f'Read {read} of {total} repositories.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
