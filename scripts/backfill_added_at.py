#!/usr/bin/env python3
"""Derive each curated record's and paper's ``added_at`` from Git history: the UTC date it first reached main.

``added_at`` is the date a record first reached ``main`` (data/README.md). For records without it, this
script walks the first-parent history of the default branch, oldest first, reads every version of the
two curated catalogs and the bibliography, and takes the committer date of the first ``main`` commit
whose file contains the record's ID. Squash merges are the commits that put records on ``main``, so
that date is the merge date. The walk is deterministic: the same history always gives the same dates.

It reads ``origin/main`` by default and refuses a ref that is not on main's history, because a branch
commit is not the day a record reached main. By default the script only reports. ``--write`` adds the missing dates after ``verified_at``, keeping
every other key and value; existing dates are never changed, and ones that disagree with the history
are listed for a reviewer instead. Shallow clones are refused because their history is incomplete.
"""
from __future__ import annotations

import argparse
from collections import OrderedDict
import datetime as dt
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RESOURCE_FILES = ('data/rea-resources.json', 'data/tool-resources.json')
PAPER_FILE = 'data/papers.json'
# Record IDs sit at the top level of each array element; nested objects in these files carry no "id".
ID_PATTERN = re.compile(rb'^[ ]{2,8}"id": *"([^"\\]+)"', re.MULTILINE)


def git(*args: str, root: Path = ROOT, data: bytes | None = None) -> bytes:
    return subprocess.run(['git', *args], cwd=root, input=data, check=True, capture_output=True).stdout


def first_parent_commits(ref: str, paths: tuple[str, ...], root: Path = ROOT) -> list[tuple[str, int]]:
    """Commits on the first-parent line of ``ref`` that touch ``paths``, oldest first, with committer times."""
    output = git('log', '--first-parent', '--reverse', '--format=%H %ct', ref, '--', *paths, root=root)
    return [(sha, int(stamp)) for sha, stamp in (line.split() for line in output.decode().splitlines())]


def file_versions(commits: list[tuple[str, int]], path: str, root: Path = ROOT):
    """Yield (commit position, bytes) for ``path`` at each commit from one streaming ``git cat-file --batch``."""
    process = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=root, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        for position, (sha, _) in enumerate(commits):
            process.stdin.write(f'{sha}:{path}\n'.encode())
            process.stdin.flush()
            header = process.stdout.readline().split()
            if len(header) == 2 and header[1] == b'missing':
                continue
            content = process.stdout.read(int(header[2]))
            process.stdout.read(1)
            yield position, content
    finally:
        process.stdin.close()
        process.stdout.close()
        process.wait()


def first_appearances(ref: str, files: tuple[str, ...], root: Path = ROOT) -> dict[str, str]:
    """Map each record ID to the UTC date of the first first-parent commit whose files list it.

    "First" follows commit order, never timestamps, which need not increase along the history.
    """
    commits = first_parent_commits(ref, files, root)
    seen: dict[str, int] = {}
    for path in files:
        for position, content in file_versions(commits, path, root):
            for match in ID_PATTERN.finditer(content):
                identifier = match[1].decode('utf-8')
                if position < seen.get(identifier, len(commits)):
                    seen[identifier] = position
    return {identifier: dt.datetime.fromtimestamp(commits[position][1], dt.timezone.utc).date().isoformat()
            for identifier, position in seen.items()}


def check_ref(ref: str, root: Path = ROOT) -> None:
    """Only main's history dates records: a branch commit is not the day a record reached main."""
    for target in ('origin/main', 'main'):
        if subprocess.run(['git', 'rev-parse', '--verify', '--quiet', target], cwd=root, capture_output=True).returncode:
            continue
        # A side-branch commit merged without squashing is an ancestor but not a commit that reached main.
        sha = git('rev-parse', '--verify', f'{ref}^{{commit}}', root=root).decode().strip()
        if sha not in git('rev-list', '--first-parent', target, root=root).decode().split():
            raise SystemExit(f'{ref} is not on the first-parent history of {target}; date records only from main.')
        return
    raise SystemExit('No main branch to check the ref against; fetch main first.')


def with_added_at(record: OrderedDict, date: str) -> OrderedDict:
    """Insert added_at after verified_at, the position the existing dated records use."""
    result = OrderedDict()
    for key, value in record.items():
        result[key] = value
        if key == 'verified_at':
            result['added_at'] = date
    if 'added_at' not in result:
        result['added_at'] = date
    return result


def backfill(root: Path = ROOT, ref: str = 'origin/main', *, write: bool = False) -> dict:
    if git('rev-parse', '--is-shallow-repository', root=root).strip() == b'true':
        raise SystemExit('A shallow clone lacks the history that dates the records; fetch the full history first.')
    check_ref(ref, root)
    report = {'ref': git('rev-parse', ref, root=root).decode().strip(), 'files': {}}
    for files in (RESOURCE_FILES, (PAPER_FILE,)):
        dates = first_appearances(ref, files, root)
        for path in files:
            records = json.loads((root / path).read_text(encoding='utf-8'), object_pairs_hook=OrderedDict)
            added, disagreements, undated = 0, [], []
            for index, record in enumerate(records):
                date = dates.get(record['id'])
                if date is None:
                    undated.append(record['id'])
                elif 'added_at' not in record:
                    records[index] = with_added_at(record, date)
                    added += 1
                elif record['added_at'] != date:
                    disagreements.append({'id': record['id'], 'recorded': record['added_at'], 'history': date})
            if write and added:
                (root / path).write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            report['files'][path] = {'records': len(records), 'added': added, 'already_dated': sum('added_at' in r for r in records) - added,
                                     'not_on_ref': undated, 'disagreements': disagreements}
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--ref', default='origin/main', help="main's history to read (default: origin/main); "
                        'a ref outside it is refused')
    parser.add_argument('--write', action='store_true', help='add the missing dates to the data files')
    args = parser.parse_args()
    report = backfill(ROOT, args.ref, write=args.write)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
