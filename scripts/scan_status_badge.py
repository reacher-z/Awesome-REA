#!/usr/bin/env python3
"""Write the shields.io endpoint badge for the last successful README discovery scan.

The README shows this file through https://img.shields.io/endpoint. The scan-status workflow rewrites it on
the `status` branch every hour and after every scan, so the badge turns the warning colour once the last
successful scan of `main` is more than six hours old. A successful scan is a run of
.github/workflows/source-scan.yml on `main` that concluded `success`; a run that finds nothing to ingest
skips its ingest job and still counts.

    GH_TOKEN=... GITHUB_REPOSITORY=reacher-z/Awesome-REA python3 scripts/scan_status_badge.py scan-status.json
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import sys
import urllib.request

WORKFLOW = 'source-scan.yml'
STALE_AFTER = timedelta(hours=6)
LABEL = 'last discovery scan'
COLOR = '6B5159'
WARNING_COLOR = 'B7791F'
LABEL_COLOR = '2B2F3A'
API_TIMEOUT = 30


def parse_time(value: str) -> datetime:
    return datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)


def badge(completed: datetime | None, now: datetime) -> dict:
    """The endpoint document: the time of the last successful scan, in the warning colour once it is stale."""
    if completed is None:
        message, stale = 'none yet', True
    else:
        message, stale = completed.strftime('%Y-%m-%d %H:%M UTC'), now - completed > STALE_AFTER
    return {'schemaVersion': 1, 'label': LABEL, 'message': message,
            'color': WARNING_COLOR if stale else COLOR, 'labelColor': LABEL_COLOR}


def last_successful_scan(repository: str, token: str) -> datetime | None:
    request = urllib.request.Request(
        f'https://api.github.com/repos/{repository}/actions/workflows/{WORKFLOW}/runs?branch=main&status=success&per_page=1',
        headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json',
                 'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'Awesome-REA-scan-status'})
    with urllib.request.urlopen(request, timeout=API_TIMEOUT) as response:
        runs = json.load(response)['workflow_runs']
    return parse_time(runs[0]['updated_at']) if runs else None


def document_bytes(document: dict) -> bytes:
    return (json.dumps(document, sort_keys=True) + '\n').encode('utf-8')


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('output', type=Path, help='endpoint JSON file to write when its content changes')
    args = parser.parse_args(argv)
    repository = os.environ['GITHUB_REPOSITORY']
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        raise SystemExit('Invalid repository identity')
    document = badge(last_successful_scan(repository, os.environ['GH_TOKEN']), datetime.now(timezone.utc))
    content = document_bytes(document)
    changed = not args.output.is_file() or args.output.read_bytes() != content
    if changed:
        args.output.write_bytes(content)
    print(f'Last successful scan: {document["message"]} ({"warning" if document["color"] == WARNING_COLOR else "current"}); '
          f'{"updated" if changed else "unchanged"} {args.output.name}.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
