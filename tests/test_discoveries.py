"""The unreviewed discovery queue: selection, exact-capture validation, budgets and trusted PR review."""
from copy import deepcopy
import datetime as dt
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import discoveries
import ingest_discoveries
import review_pr
from test_review_pr import NUMBER, REPOSITORY, SHA, FakeGitHub, run_review

TEMPLATE = next(row for row in json.loads((ROOT / 'data/source-supplements/public-cloud-39323601991-batch-01.json')
                                          .read_text(encoding='utf-8'))['resources']
                if row.get('readme_transport') == 'github-graphql-blob')
NOW = dt.datetime(2026, 11, 5, 21, tzinfo=dt.timezone.utc)


def capture(number, *, observed='2026-11-05T16:30:00.000000Z', name=None, **changes):
    """A valid verified capture with a fresh numeric identity, repository name and README hash."""
    record = deepcopy(TEMPLATE)
    full_name = name or f'example-owner/re-tool-{number}'
    commit = record['readme_commit_sha']
    record.update(id=f'scan-{9_000_000_000 + number}', name=full_name, full_name=full_name,
                  url=f'https://github.com/{full_name}',
                  readme_url=f'https://github.com/{full_name}/blob/{commit}/{record["readme_path"]}',
                  readme_sha256=hashlib.sha256(f'readme {number}'.encode()).hexdigest(),
                  metadata_observed_at=observed, observed_at=observed)
    record.update(changes)
    return record


def receipt():
    return {'started_at': '2026-11-05T09:00:31.812022+00:00', 'completed_at': '2026-11-05T09:30:39.744560+00:00',
            'outcome': 'partial',
            'counts': {'successful_readme_scans': 10, 'failed': 0, 'attempted_readme_scans': 10, 'unique_repos': 10,
                       'unattempted_candidates': 0},
            'integrity_counts': {'qualified': 10, 'legacy_unknown': 0, 'mismatched': 0}}


def source(run_id=42063733237, attempt=1):
    return {'repository': discoveries.REPOSITORY, 'workflow_path': discoveries.WORKFLOW_PATH, 'workflow_id': 388449544,
            'run_id': run_id, 'run_attempt': attempt, 'event': 'schedule', 'head_sha': 'a' * 40,
            'artifact_id': 13434907571, 'artifact_name': f'readme-scan-checkpoint-{attempt}',
            'artifact_digest': 'sha256:' + 'b' * 64, 'checkpoint_sha256': 'c' * 64, 'receipt_sha256': 'd' * 64}


def empty_existing():
    return {'ids': set(), 'names': {}, 'readmes': set(), 'records': 0, 'bytes': 0}


def make_batch(records, *, run_id=42063733237, existing=None, ingested='2026-11-05T17:00:00Z'):
    batch, status = discoveries.build_batch({'resources': records}, receipt(), source(run_id), existing or empty_existing(),
                                            set(), ingested_at=ingested)
    assert status == 'selected', status
    return batch


class SelectionTest(unittest.TestCase):
    def test_reconstruction_phrase_capture_is_an_eligible_data_asset(self):
        record = capture(10, name='storytold/photocraft', topics=['game'],
                         matched_queries=['"clean-room reimplementation" in:readme,description '
                                          'is:public fork:false archived:false'])
        selected, eligible, _ = discoveries.select_records([record], empty_existing(), set(), limit=10)
        self.assertEqual((selected, eligible), ([record], 1))
        self.assertEqual(discoveries.record_problems(record), [])

    def test_newest_first_with_every_skip_reason_counted(self):
        existing = {'ids': {'scan-9000000001'}, 'names': {'other/renamed': 'scan-1'},
                    'readmes': {hashlib.sha256(b'readme 4').hexdigest()}, 'records': 0, 'bytes': 0}
        records = [
            capture(1),                                          # already listed
            capture(2, observed='2026-11-05T16:40:00.000000Z'),  # newest
            capture(3, name='other/renamed'),                    # same name, other numeric ID
            capture(4),                                          # README already published
            capture(5, observed='2026-11-04T10:00:00.000000Z'),  # older, still selected
            capture(6, name='curated-owner/curated-tool'),       # already curated
            capture(7, topics=['game']),                         # fails the topic screen
            capture(8, readme_git_sha_matches_content=False),    # no explicit hash match
            capture(9, observed='2026-11-03T10:00:00.000000Z'),  # over the limit
        ]
        selected, eligible, skipped = discoveries.select_records(
            records, existing, {'https://github.com/curated-owner/curated-tool'}, limit=2)
        self.assertEqual([row['id'] for row in selected], ['scan-9000000002', 'scan-9000000005'])
        self.assertEqual(eligible, 6)
        self.assertEqual(dict(skipped), {'already-listed': 1, 'already-curated': 1, 'name-conflict': 1,
                                         'duplicate-readme': 1, 'privacy': 0, 'over-limit': 1})
        self.assertIs(selected[0], records[1], 'capture objects are copied unchanged')

    def test_duplicates_inside_one_run_keep_the_newest_and_privacy_hits_are_skipped(self):
        shared = hashlib.sha256(b'shared').hexdigest()
        leak = ''.join(('/', 'home', '/alice/notes'))
        records = [capture(1, readme_sha256=shared), capture(2, readme_sha256=shared, observed='2026-11-05T16:31:00.000000Z'),
                   capture(3, description_en='See ' + leak, description_zh='See ' + leak)]
        selected, _, skipped = discoveries.select_records(records, empty_existing(), set(), limit=10)
        self.assertEqual([row['id'] for row in selected], ['scan-9000000002'])
        self.assertEqual((skipped['duplicate-readme'], skipped['privacy']), (1, 1))

    def test_budget_limits_stop_or_shrink_a_batch(self):
        full = {**empty_existing(), 'records': discoveries.MAX_TOTAL_RECORDS}
        self.assertEqual(discoveries.build_batch({'resources': [capture(1)]}, receipt(), source(), full, set(),
                                                 ingested_at='2026-11-05T17:00:00Z'), (None, 'budget-reached'))
        nearly = {**empty_existing(), 'records': discoveries.MAX_TOTAL_RECORDS - 2}
        batch = make_batch([capture(number) for number in range(1, 6)], existing=nearly)
        self.assertEqual((batch['selection']['record_limit'], len(batch['resources'])), (2, 2))
        size = len(discoveries.batch_bytes(make_batch([capture(number) for number in range(1, 6)])))
        bytes_left = {**empty_existing(), 'bytes': discoveries.MAX_TOTAL_BYTES - size + 100}
        shrunk = make_batch([capture(number) for number in range(1, 6)], existing=bytes_left)
        self.assertLess(len(shrunk['resources']), 5)
        self.assertEqual(shrunk['selection']['skipped_counts']['over-limit'], 5 - len(shrunk['resources']))
        self.assertEqual(discoveries.build_batch({'resources': [capture(7, topics=['game'])]}, receipt(), source(),
                                                 empty_existing(), set(), ingested_at='2026-11-05T17:00:00Z'),
                         (None, 'nothing-new'))


class BatchValidationTest(unittest.TestCase):
    def test_built_batch_is_valid_and_keeps_exact_captures(self):
        records = [capture(1), capture(2)]
        batch = make_batch(records)
        self.assertEqual(discoveries.validate_batch(batch, batch['batch_id'], now=NOW), [])
        self.assertEqual(batch['batch_id'], 'run-42063733237-1')
        self.assertEqual(batch['review_status'], 'unreviewed')
        self.assertEqual(batch['resources'], records)
        self.assertEqual(batch['selection']['record_sha256'], {row['id']: discoveries.digest(row) for row in records})
        self.assertEqual(batch['source']['scan_outcome'], 'partial')
        self.assertTrue(discoveries.batch_bytes(batch).endswith(b'}\n'))

    def test_altered_or_upgraded_records_and_bad_provenance_are_rejected(self):
        batch = make_batch([capture(1), capture(2)])
        cases = {
            'edited capture': lambda b: b['resources'][0].update(stars=99999),
            'source-reviewed label': lambda b: b['resources'][0].update(verification='source-reviewed'),
            'reviewed batch': lambda b: b.update(review_status='source-reviewed'),
            'missing hash match': lambda b: b['resources'][1].update(readme_git_sha_matches_content=False),
            'extra field': lambda b: b['resources'][0].update(curated=True),
            'reordered IDs': lambda b: b['selection'].update(selected_ids=list(reversed(b['selection']['selected_ids']))),
            'future ingest': lambda b: b.update(ingested_at='2026-11-07T00:00:00Z'),
            'capture after ingest': lambda b: b.update(ingested_at='2026-11-05T16:20:00Z'),
            'other repository': lambda b: b['source'].update(repository='someone/fork'),
            'artifact attempt': lambda b: b['source'].update(artifact_name='readme-scan-checkpoint-2'),
            'wrong count': lambda b: b['selection'].update(selected_count=3),
        }
        for name, change in cases.items():
            with self.subTest(name):
                changed = deepcopy(batch)
                change(changed)
                self.assertTrue(discoveries.validate_batch(changed, changed['batch_id'], now=NOW))
        self.assertTrue(discoveries.validate_batch(batch, 'run-42063733237-2', now=NOW), 'file name must match')

    def test_queue_rules_files_and_budget_across_batches(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / discoveries.DIRECTORY
            folder.mkdir(parents=True)
            (folder / 'README.md').write_text('# Queue\n', encoding='utf-8')
            first = make_batch([capture(1), capture(2)], run_id=100)
            (folder / 'run-100-1.json').write_bytes(discoveries.batch_bytes(first))
            batches, problems = discoveries.load_batches(root, now=NOW)
            self.assertEqual((len(batches), problems), (1, []))
            repeat = make_batch([capture(2), capture(3)], run_id=200)
            (folder / 'run-200-1.json').write_bytes(discoveries.batch_bytes(repeat))
            _, problems = discoveries.load_batches(root, now=NOW)
            self.assertTrue(any('already listed in an earlier batch' in problem for problem in problems))
            (folder / 'run-200-1.json').unlink()
            (folder / 'run-300-1.json').write_text(json.dumps(make_batch([capture(4)], run_id=300)), encoding='utf-8')
            _, problems = discoveries.load_batches(root, now=NOW)
            self.assertTrue(any('repository JSON format' in problem for problem in problems))
            (folder / 'run-300-1.json').unlink()
            (folder / 'notes.txt').write_text('x', encoding='utf-8')
            self.assertIn('unexpected entries', discoveries.load_batches(root, now=NOW)[1][0])
            (folder / 'notes.txt').unlink()
            with patch.object(discoveries, 'MAX_TOTAL_RECORDS', 1):
                self.assertTrue(any('exceed the discovery budget' in problem
                                    for problem in discoveries.load_batches(root, now=NOW)[1]))

    def test_repository_validator_and_current_layers(self):
        report = discoveries.summary(ROOT)
        self.assertEqual(report['problems'], [])
        existing = discoveries.existing_identities(ROOT)
        self.assertIn(TEMPLATE['id'], existing['ids'])
        self.assertIn(TEMPLATE['full_name'].casefold(), existing['names'])


def prepared_root(directory):
    """A minimal checkout with the published layers the ingest compares against."""
    root = Path(directory)
    for name in ('data/source-index.json', 'data/rea-resources.json', 'data/tool-resources.json'):
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, root / name)
    shutil.copytree(ROOT / 'data/source-supplements', root / 'data/source-supplements')
    return root


class PrepareTest(unittest.TestCase):
    def test_prepare_writes_one_valid_batch_once(self):
        with tempfile.TemporaryDirectory() as directory:
            root = prepared_root(directory)
            inputs = root / 'inputs'
            inputs.mkdir()
            already = deepcopy(TEMPLATE)
            (inputs / 'checkpoint.json').write_text(json.dumps({'resources': [capture(1), capture(2), already]}), encoding='utf-8')
            (inputs / 'receipt.json').write_text(json.dumps(receipt()), encoding='utf-8')
            (inputs / 'source.json').write_text(json.dumps(source()), encoding='utf-8')
            arguments = (inputs / 'checkpoint.json', inputs / 'receipt.json', inputs / 'source.json')
            path, status, count = ingest_discoveries.prepare(*arguments, root=root, ingested_at='2026-11-05T17:00:00Z')
            self.assertEqual((path.name, status, count), ('run-42063733237-1.json', 'selected', 2))
            batch = json.loads(path.read_text(encoding='utf-8'))
            self.assertEqual(batch['selection']['skipped_counts']['already-listed'], 1)
            self.assertEqual(discoveries.load_batches(root, now=NOW)[1], [])
            self.assertEqual(ingest_discoveries.prepare(*arguments, root=root)[1:], ('already-ingested', 0))


class IngestPullGitHub(FakeGitHub):
    """The in-memory API with the author and branch of the pull request under review."""

    def __init__(self, *args, user='github-actions[bot]', kind='Bot', ref=discoveries.INGEST_BRANCH, **kwargs):
        super().__init__(*args, **kwargs)
        self.pull_fields = {'user': {'login': user, 'type': kind}, 'ref': ref}

    def __call__(self, repository, endpoint, token, method='GET', payload=None, raw=False):
        result = super().__call__(repository, endpoint, token, method, payload, raw)
        if method == 'GET' and endpoint == f'pulls/{NUMBER}':
            return {**result, 'user': self.pull_fields['user'], 'head': {**result['head'], 'ref': self.pull_fields['ref']}}
        return result


class TrustedReviewTest(unittest.TestCase):
    def review(self, files, contents, **pull):
        github = IngestPullGitHub(files, contents, **pull)
        status, _ = run_review(github)
        return status, github.body()

    def test_batches_from_anyone_but_the_ingest_need_a_maintainer(self):
        batch = make_batch([capture(1)])
        name = f"data/discoveries/{batch['batch_id']}.json"
        text = discoveries.batch_bytes(batch).decode()
        for pull in ({'user': 'someone', 'kind': 'User'}, {'ref': 'feature/hand-made'}):
            with self.subTest(pull):
                status, body = self.review([{'filename': name, 'status': 'added'}], {name: text}, **pull)
                self.assertEqual(status, 1)
                self.assertIn('added only by the scheduled ingest', body)
        status, body = self.review([{'filename': name, 'status': 'added'},
                                    {'filename': 'scripts/discoveries.py', 'status': 'modified', 'patch': '@@ -1 +1 @@\n+x'}],
                                   {name: text})
        self.assertEqual(status, 1)
        self.assertIn('added only by the scheduled ingest', body)

    def test_an_added_batch_is_checked_as_data_and_passes(self):
        batch = make_batch([capture(1), capture(2)])
        name = f"data/discoveries/{batch['batch_id']}.json"
        status, body = self.review([{'filename': name, 'status': 'added'}], {name: discoveries.batch_bytes(batch).decode()})
        self.assertEqual(status, 0, body)
        self.assertIn('Discovery batch run-42063733237-1: 2 automated README captures from the scheduled ingest', body)
        self.assertIn('**No issues found by these automatic checks.**', body)
        self.assertNotIn('not inspected', body)

    def test_edits_duplicates_and_upgrades_are_findings(self):
        batch = make_batch([capture(1)])
        name = f"data/discoveries/{batch['batch_id']}.json"
        text = discoveries.batch_bytes(batch).decode()
        status, body = self.review([{'filename': name, 'status': 'modified', 'patch': '@@ -1 +1 @@\n+x'}], {name: text})
        self.assertEqual(status, 1)
        self.assertIn('existing discovery batches are immutable', body)
        duplicate = make_batch([deepcopy(TEMPLATE)])
        status, body = self.review([{'filename': name, 'status': 'added'}], {name: discoveries.batch_bytes(duplicate).decode()})
        self.assertEqual(status, 1)
        self.assertIn('already in the source index', review_pr.safe_text(body).replace('\\', '') + body)
        upgraded = deepcopy(batch)
        upgraded['resources'][0]['verification'] = 'source-reviewed'
        status, body = self.review([{'filename': name, 'status': 'added'}], {name: discoveries.batch_bytes(upgraded).decode()})
        self.assertEqual(status, 1)
        self.assertIn('Findings:', body)


if __name__ == '__main__':
    unittest.main()
