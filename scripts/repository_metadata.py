#!/usr/bin/env python3
"""GitHub repository facts for curated resource pages: stars, last default-branch commit, primary language and detected license.

data/repository-metadata.json holds one dated observation per GitHub repository that a curated record's `url`
names. The page builders only read it; a missing file, a missing repository or a malformed entry leaves that fact
off the page, so a build never depends on GitHub. Refresh the snapshot with

    python3 scripts/repository_metadata.py --refresh

which reads GITHUB_TOKEN (or `gh auth token`) and sends one GraphQL query per 50 repositories. The detected
license is GitHub's signal, not a license review (docs/artifact-evidence.md), so pages label it as such and
structured data never carries it.
"""
from __future__ import annotations

import argparse
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


def _query(token: str, keys: list[str]) -> dict:
    parts = []
    for index, key in enumerate(keys):
        owner, name = key.split('/')
        parts.append(f'r{index}: repository(owner: {json.dumps(owner)}, name: {json.dumps(name)}) {{ {QUERY_FIELDS} }}')
    body = json.dumps({'query': '{ ' + ' '.join(parts) + ' }'}).encode('utf-8')
    request = Request('https://api.github.com/graphql', data=body, method='POST',
                      headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json',
                               'User-Agent': 'awesome-rea-metadata'})
    for attempt in range(3):
        try:
            with urlopen(request, timeout=60) as response:
                data = json.load(response).get('data') or {}
            break
        except OSError as error:
            if attempt == 2:
                # Stop before writing: a partial snapshot would drop these repositories from their pages.
                raise SystemExit(f'A GitHub batch failed three times ({error}); the snapshot is unchanged.')
            time.sleep(5 * (attempt + 1))
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


def refresh(path: Path = SNAPSHOT) -> tuple[int, int]:
    keys = sorted({key for catalog in CATALOGS for record in json.loads(catalog.read_text(encoding='utf-8'))
                   if (key := repository_key(record.get('url', '')))})
    token = _token()
    observed = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    repositories = {}
    for start in range(0, len(keys), BATCH):
        repositories.update(_query(token, keys[start:start + BATCH]))
        print(f'{min(start + BATCH, len(keys))} of {len(keys)}', file=sys.stderr, flush=True)
    # Every fact carries the one observation date; a repository the API did not return is left out.
    document = {'observed_at': observed, 'source': 'GitHub GraphQL API', 'repositories': dict(sorted(repositories.items()))}
    path.write_text(json.dumps(document, indent=1, ensure_ascii=False, sort_keys=False) + '\n', encoding='utf-8')
    return len(repositories), len(keys)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--refresh', action='store_true', help='read every curated GitHub repository and rewrite the snapshot')
    args = parser.parse_args()
    if not args.refresh:
        observed, repositories = _snapshot(str(SNAPSHOT))
        print(f'{len(repositories)} repositories observed at {observed}.')
        return 0
    read, total = refresh()
    print(f'Read {read} of {total} repositories.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
