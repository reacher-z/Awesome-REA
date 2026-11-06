"""added_at backfill: the first main commit that lists a record's ID dates it; existing dates are kept."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import backfill_added_at as backfill


def git(root, *args, date=None):
    environment = {**os.environ, 'GIT_AUTHOR_NAME': 't', 'GIT_AUTHOR_EMAIL': 't@example.com',
                   'GIT_COMMITTER_NAME': 't', 'GIT_COMMITTER_EMAIL': 't@example.com'}
    if date:
        environment.update(GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
    return subprocess.run(['git', *args], cwd=root, env=environment, check=True, capture_output=True, text=True).stdout


def write(root, name, records):
    path = Path(root) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def resource(identifier, **extra):
    return {'id': identifier, 'name': identifier, 'verified_at': '2026-10-01', 'verification': 'source-reviewed', **extra}


class BackfillTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        git(self.root, 'init', '-q', '-b', 'main')
        write(self.root, 'data/rea-resources.json', [resource('alpha')])
        write(self.root, 'data/tool-resources.json', [])
        write(self.root, 'data/papers.json', [resource('paper-one')])
        git(self.root, 'add', '-A'); git(self.root, 'commit', '-qm', 'first', date='2026-10-16T23:30:00+00:00')
        # beta lands at 01:00 on the 18th in UTC although the committer's local date is still the 17th.
        write(self.root, 'data/tool-resources.json', [resource('beta'), resource('gamma', added_at='2026-11-01')])
        git(self.root, 'add', '-A'); git(self.root, 'commit', '-qm', 'second', date='2026-10-17T20:00:00-05:00')
        # alpha moves between files later; its first appearance still dates it.
        write(self.root, 'data/rea-resources.json', [])
        write(self.root, 'data/tool-resources.json', [resource('beta'), resource('gamma', added_at='2026-11-01'), resource('alpha')])
        git(self.root, 'add', '-A'); git(self.root, 'commit', '-qm', 'third', date='2026-10-20T10:00:00+00:00')

    def tearDown(self):
        self.directory.cleanup()

    def test_report_dates_first_appearance_in_utc_and_keeps_existing_dates(self):
        report = backfill.backfill(self.root, 'main')
        tools = report['files']['data/tool-resources.json']
        self.assertEqual((tools['added'], tools['already_dated'], tools['not_on_ref']), (2, 1, []))
        self.assertEqual(tools['disagreements'], [{'id': 'gamma', 'recorded': '2026-11-01', 'history': '2026-10-18'}])
        self.assertEqual(report['files']['data/papers.json']['added'], 1)
        # Reporting changes nothing.
        self.assertNotIn('added_at', json.loads((self.root / 'data/papers.json').read_text())[0])

    def test_write_inserts_after_verified_at_and_is_idempotent(self):
        backfill.backfill(self.root, 'main', write=True)
        tools = json.loads((self.root / 'data/tool-resources.json').read_text())
        self.assertEqual({record['id']: record['added_at'] for record in tools},
                         {'beta': '2026-10-18', 'gamma': '2026-11-01', 'alpha': '2026-10-16'})
        self.assertEqual(list(tools[0]), ['id', 'name', 'verified_at', 'added_at', 'verification'])
        paper = json.loads((self.root / 'data/papers.json').read_text())[0]
        self.assertEqual(paper['added_at'], '2026-10-16')
        before = (self.root / 'data/tool-resources.json').read_bytes()
        again = backfill.backfill(self.root, 'main', write=True)
        self.assertEqual(again['files']['data/tool-resources.json']['added'], 0)
        self.assertEqual((self.root / 'data/tool-resources.json').read_bytes(), before)

    def test_branch_history_is_refused_and_commit_order_beats_timestamps(self):
        git(self.root, 'checkout', '-qb', 'feature')
        write(self.root, 'data/papers.json', [resource('paper-one'), resource('paper-branch')])
        git(self.root, 'add', '-A'); git(self.root, 'commit', '-qm', 'branch', date='2026-10-21T10:00:00+00:00')
        with self.assertRaisesRegex(SystemExit, 'not on the first-parent history of main'):
            backfill.backfill(self.root, 'feature')
        git(self.root, 'checkout', '-q', 'main')
        # Merged without squashing, the branch commit is an ancestor of main but never was main's tip.
        git(self.root, 'merge', '-q', '--no-ff', '--no-edit', 'feature', date='2026-10-21T12:00:00+00:00')
        with self.assertRaisesRegex(SystemExit, 'not on the first-parent history of main'):
            backfill.backfill(self.root, 'feature')
        papers = backfill.backfill(self.root, 'main')['files']['data/papers.json']
        self.assertEqual(papers['added'], 2)
        # A later main commit with an earlier timestamp does not move delta's first appearance back.
        write(self.root, 'data/rea-resources.json', [resource('delta')])
        git(self.root, 'add', '-A'); git(self.root, 'commit', '-qm', 'fourth', date='2026-10-22T10:00:00+00:00')
        write(self.root, 'data/rea-resources.json', [resource('delta'), resource('epsilon')])
        git(self.root, 'add', '-A'); git(self.root, 'commit', '-qm', 'fifth', date='2026-10-02T10:00:00+00:00')
        report = backfill.backfill(self.root, 'main', write=True)
        records = {record['id']: record['added_at'] for record in json.loads((self.root / 'data/rea-resources.json').read_text())}
        self.assertEqual(records, {'delta': '2026-10-22', 'epsilon': '2026-10-02'})
        self.assertEqual(report['files']['data/rea-resources.json']['added'], 2)

    def test_records_not_yet_on_the_history_are_listed_not_dated(self):
        write(self.root, 'data/papers.json', [resource('paper-one'), resource('paper-new')])
        report = backfill.backfill(self.root, 'main', write=True)
        self.assertEqual(report['files']['data/papers.json']['not_on_ref'], ['paper-new'])
        papers = json.loads((self.root / 'data/papers.json').read_text())
        self.assertNotIn('added_at', papers[1])


if __name__ == '__main__':
    unittest.main()
