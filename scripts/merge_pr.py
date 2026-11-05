#!/usr/bin/env python3
"""Check that a pull request may be merged by the `Merge a pull request` workflow; print its head commit.

The workflow merges with the workflow token and the rebase method, so commits keep their own authors and
GitHub records itself as committer; no personal account is stamped on `main`. Before that, this script
refuses unless the pull request targets the default branch, is open and not a draft, is mergeable, has
a head that contains the default branch's current commit, and has a successful `validate` and `review`
check on that head: the newest commit status of that name, which dispatched automation checks report, or
else the newest GitHub Actions check run of that name. It also waits, bounded, until GitHub reports the
pull request mergeable under branch protection, which still decides the merge itself.

It reads only through the GitHub REST API, prints the head SHA for the merge step on success and exits 1
with a reason otherwise. The token comes from GH_TOKEN and is sent only to api.github.com.
"""
from __future__ import annotations

import os
from pathlib import Path
import re
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingest_discoveries import MERGEABLE_STATES, ApiError, GitHub  # noqa: E402

REQUIRED_CHECKS = ('validate', 'review')
MERGEABILITY_WAIT_SECONDS = 120
POLL_SECONDS = 10


class Refused(Exception):
    """The pull request does not meet a merge condition; the message says which."""


def check_state(github: GitHub, sha: str, name: str) -> str:
    """'success', 'failure' or 'pending' for one required check on ``sha``.

    The newest commit status of that context decides when one exists, as for automation pull requests whose
    checks were dispatched. Otherwise the newest check run of that name from GitHub Actions decides.
    """
    for status in github.get(f'commits/{sha}/status').get('statuses', []):
        if status.get('context') == name:
            return {'success': 'success', 'failure': 'failure', 'error': 'failure'}.get(status.get('state'), 'pending')
    runs = github.get(f'commits/{sha}/check-runs?check_name={name}&per_page=30')['check_runs']
    runs = [run for run in runs if (run.get('app') or {}).get('slug') == 'github-actions']
    if not runs:
        return 'pending'
    latest = max(runs, key=lambda run: run['id'])
    if latest.get('status') != 'completed':
        return 'pending'
    return 'success' if latest.get('conclusion') == 'success' else 'failure'


def mergeable_pull(github: GitHub, number: int) -> dict:
    """The pull request once GitHub has finished computing whether it can merge, bounded.

    GitHub recomputes mergeability asynchronously after the last check completes; until then a merge can be
    refused although nothing is wrong, so wait for a mergeable state (as the discovery ingest does).
    """
    deadline = time.monotonic() + MERGEABILITY_WAIT_SECONDS
    while True:
        pull = github.get(f'pulls/{number}')
        if (pull.get('state') != 'open' or pull.get('mergeable') is False
                or pull.get('mergeable_state') in MERGEABLE_STATES | {'behind', 'dirty', 'draft'}):
            return pull
        if time.monotonic() >= deadline:
            return pull
        time.sleep(POLL_SECONDS)


def guard(github: GitHub, number: int, default_branch: str) -> str:
    """Return the head SHA that may be merged, or raise Refused."""
    pull = mergeable_pull(github, number)
    if pull.get('state') != 'open':
        raise Refused(f'pull request #{number} is not open')
    if pull.get('draft'):
        raise Refused(f'pull request #{number} is a draft')
    if (pull.get('base') or {}).get('ref') != default_branch:
        raise Refused(f'pull request #{number} does not target {default_branch}')
    if pull.get('mergeable') is not True:
        raise Refused(f'pull request #{number} is not mergeable (conflicts, or GitHub has not computed it)')
    head = pull['head']['sha']
    if not re.fullmatch(r'[0-9a-f]{40}', head):
        raise Refused('unexpected head commit')
    base = github.get(f'branches/{default_branch}')['commit']['sha']
    comparison = github.get(f'compare/{base}...{head}')
    if comparison.get('behind_by') != 0:
        raise Refused(f'pull request #{number} is behind {default_branch}; update the branch and run the checks again')
    states = {name: check_state(github, head, name) for name in REQUIRED_CHECKS}
    if any(state != 'success' for state in states.values()):
        detail = ', '.join(f'{name}: {state}' for name, state in states.items())
        raise Refused(f'required checks on {head[:12]} have not all succeeded ({detail})')
    if pull.get('mergeable_state') not in MERGEABLE_STATES:
        raise Refused(f"pull request #{number} is {pull.get('mergeable_state')!r}, not mergeable under branch protection yet")
    return head


def main() -> int:
    repository, token = os.environ['GITHUB_REPOSITORY'], os.environ['GH_TOKEN']
    default_branch = os.environ['DEFAULT_BRANCH']
    value = os.environ.get('PR', '').strip()
    if not re.fullmatch(r'[1-9][0-9]{0,9}', value):
        print('Refused: the pr input must be a positive pull request number.', file=sys.stderr)
        return 1
    try:
        head = guard(GitHub(repository, token), int(value), default_branch)
    except Refused as reason:
        print(f'Refused: {reason}.', file=sys.stderr)
        return 1
    except ApiError as error:
        print(f'Refused: {error}', file=sys.stderr)
        return 1
    print(head)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
