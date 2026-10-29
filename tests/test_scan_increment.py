"""The increment check accepts only additions and deterministic annotations to a frozen baseline."""
import base64
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import check_scan_increment as increment
from scan_sources import run_scan

QUERY = 'topic:reverse-engineering is:public fork:false archived:false'
BODY = b'# Example\n\n## Usage\nInspect a firmware image.\n'
OID = hashlib.sha1(b'blob ' + str(len(BODY)).encode() + b'\0' + BODY).hexdigest()
SHARDS = increment.LOCALE_FILES


def repository(number):
    return {'id': number, 'full_name': f'example/tool-{number}', 'html_url': f'https://github.com/example/tool-{number}',
            'private': False, 'visibility': 'public', 'archived': False, 'fork': False,
            'description': f'Firmware analysis tool {number}', 'topics': ['firmware-analysis'],
            'stargazers_count': number, 'default_branch': 'main'}


class API:
    """Offline search, identity and README responses for a fixed set of repositories."""
    def __init__(self, numbers):
        self.numbers = numbers

    def json(self, path, search=False):
        if search:
            return {'items': [repository(number) for number in self.numbers], 'total_count': len(self.numbers),
                    'incomplete_results': False}
        if path.startswith('/repositories/'):
            return repository(int(path.rsplit('/', 1)[1]))
        number = int(path.split('/')[3].split('?')[0].rsplit('-', 1)[1])
        return {'type': 'file', 'path': 'README.md', 'sha': OID, 'size': len(BODY),
                'html_url': repository(number)['html_url'] + '/blob/main/README.md',
                'encoding': 'base64', 'content': base64.b64encode(BODY).decode()}


def scan(directory, name, numbers, target, resume=None):
    output = Path(directory) / name
    args = SimpleNamespace(target=target, workers=1, requests_per_second=1, max_pages=1, candidate_buffer=0,
                           seed_curated=False, seed_papers=False, queries=[QUERY], output=output)
    resumed, digest = (json.loads(resume.read_bytes()), hashlib.sha256(resume.read_bytes()).hexdigest()) if resume else (None, None)
    with contextlib.redirect_stdout(io.StringIO()):
        run_scan(API(numbers), args, resumed, digest)
    return output


def locales(records):
    entries = {record['id']: {'description_en': record['description_en'], 'description_zh': '固件分析工具'}
               for record in records}
    return {SHARDS[0]: entries, SHARDS[1]: {}, SHARDS[2]: {}}


class ScanIncrementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as directory:
            base_path = scan(directory, 'base.json', [11, 12], 2)
            cand_path = scan(directory, 'next.json', [11, 12, 13, 14], 4, resume=base_path)
            cls.base_raw, cls.cand_raw = base_path.read_bytes(), cand_path.read_bytes()

    def setUp(self):
        self.baseline = increment.snapshot(self.base_raw, 'baseline')
        self.candidate = increment.snapshot(self.cand_raw, 'candidate')
        self.digest = hashlib.sha256(self.base_raw).hexdigest()

    def check(self, candidate=None, **options):
        return increment.check_increment(self.baseline, candidate or self.candidate, self.digest, **options)

    def test_actual_resumed_increment_is_bound_and_counted(self):
        report = self.check()
        self.assertEqual(report['errors'], [])
        self.assertEqual(report['baseline_binding'], 'resume_history[0]')
        self.assertEqual(report['new'], {'successful': 2, 'failed': 0, 'discovered_ids': 2})
        self.assertEqual(report['candidate']['unattempted_ids'], 0)

    def test_changed_or_missing_retained_evidence_is_rejected(self):
        changed = copy.deepcopy(self.candidate)
        changed['resources'][0]['stars'] += 1
        self.assertIn('scan-12: retained readme-scanned object changed (other fields changed).', self.check(changed)['errors'])
        changed = copy.deepcopy(self.candidate)
        changed['meta']['queries'][0]['returned'] = 1
        self.assertIn('meta.queries: 1 retained entries are missing or changed.', self.check(changed)['errors'])
        changed = copy.deepcopy(self.candidate)
        moved = changed['resources'].pop(0)
        changed['failures'].append({**{key: moved[key] for key in ('id', 'full_name', 'url', 'observed_at')},
                                    'scan_status': 'failed', 'reason': 'http-404', 'http_status': 404})
        errors = self.check(changed)['errors']
        self.assertIn('scan-12: retained readme-scanned attempt became failed.', errors)
        self.assertIn('candidate: meta.successful_readme_scans is 4, but 3 entries are recorded.', errors)

    def test_ledger_arithmetic_is_recomputed_without_a_batch_size(self):
        changed = copy.deepcopy(self.candidate)
        changed['meta']['discovered_repository_ids'].remove('scan-11')
        changed['meta']['unique_repos'] -= 1
        errors = self.check(changed)['errors']
        self.assertIn('candidate: 1 attempted IDs are missing from the discovery ledger.', errors)
        self.assertIn('Discovery ledger: 1 baseline IDs are missing from the candidate.', errors)
        changed = copy.deepcopy(self.candidate)
        changed['meta']['current_run']['new_successful_readme_scans'] = 500
        self.assertIn('candidate: current_run retained_successful_readme_scans plus new_successful_readme_scans '
                      'does not equal 4 recorded entries.', self.check(changed)['errors'])

    def test_binding_that_disagrees_with_the_baseline_is_an_error_and_absence_a_warning(self):
        changed = copy.deepcopy(self.candidate)
        changed['meta']['resume_history'][0]['successful_readme_scans'] = 3
        self.assertIn('Baseline binding: resume history for the baseline disagrees with its counts or run.',
                      self.check(changed)['errors'])
        changed['meta']['resume_history'][0]['source_sha256'] = '0' * 64
        report = increment.check_increment(self.baseline, changed, self.digest)
        self.assertIsNone(report['baseline_binding'])
        self.assertEqual(len(report['warnings']), 1)

    def test_description_omission_must_reproduce_the_bounded_policy(self):
        long_text = 'Firmware ' * 200
        self.baseline['resources'][0]['description_en'] = self.baseline['resources'][0]['description_zh'] = long_text
        for record in (self.baseline['resources'][0],):
            record.pop('description_capture_policy', None)
        changed = copy.deepcopy(self.candidate)
        record = changed['resources'][0]
        record.pop('description_capture_policy', None)
        record.update(increment.capture_description(long_text))
        report = self.check(changed)
        self.assertEqual(report['errors'], [])
        self.assertEqual(report['annotations'], [{'id': 'scan-12', 'kinds': ['description-omission']}])
        record['description_omission']['original_sha256'] = '0' * 64
        self.assertIn('scan-12: retained readme-scanned object changed (other fields changed).', self.check(changed)['errors'])

    def test_integrity_review_needs_a_retained_mismatch_and_valid_evidence(self):
        review = {'reviewed_at': '2099-01-01T00:00:00Z', 'method': increment.INTEGRITY_REVIEW_METHOD,
                  'advertised_blob_sha256': 'b' * 64, 'advertised_blob_bytes': 10}
        changed = copy.deepcopy(self.candidate)
        changed['resources'][0]['readme_integrity_review'] = review
        self.assertIn('scan-12: retained readme-scanned object changed (a README integrity review needs a retained '
                      'Git blob mismatch).', self.check(changed)['errors'])
        for document in (self.baseline, changed):
            document['resources'][0].update(readme_git_sha='c' * 40, readme_git_sha_matches_content=False)
        report = self.check(changed)
        self.assertEqual(report['errors'], [])
        self.assertEqual(report['annotations'], [{'id': 'scan-12', 'kinds': ['readme-integrity-review']}])
        changed['resources'][0]['stars'] = 0
        self.assertIn('scan-12: retained readme-scanned object changed (other fields changed).', self.check(changed)['errors'])

    def test_publication_requires_completion_translations_and_hash_bound_scope(self):
        base_shards = locales(self.baseline['resources'])
        shards = locales(self.candidate['resources'])
        options = {'publication': True, 'base_shards': base_shards, 'shards': shards, 'scope': {}}
        self.assertEqual(self.check(**options)['errors'], [])
        changed = copy.deepcopy(self.candidate)
        changed['meta']['status'] = 'in-progress'
        self.assertIn('Publication requires a complete scan; the candidate is an in-progress checkpoint.',
                      self.check(changed, **options)['errors'])
        missing = copy.deepcopy(shards)
        del missing[SHARDS[0]]['scan-14']
        self.assertIn('Repository localization coverage: 1 missing and 0 unknown IDs.',
                      self.check(**{**options, 'shards': missing})['errors'])
        moved = copy.deepcopy(shards)
        moved[SHARDS[1]]['scan-11'] = moved[SHARDS[0]].pop('scan-11')
        self.assertIn(f'scan-11: existing translation in {SHARDS[0]} was moved or changed.',
                      self.check(**{**options, 'shards': moved})['errors'])
        record = self.candidate['resources'][-1]
        scope = {record['id']: {'decision': 'exclude', 'reason_code': 'outside-scope', 'reason_en': 'Unrelated.',
                                'reason_zh': '无关。', 'readme_sha256': '0' * 64, 'evidence_url': record['readme_url'],
                                'reviewed_at': '2026-10-19'}}
        self.assertIn(f'{record["id"]}: scope README hash differs from the scanned snapshot',
                      self.check(**{**options, 'scope': scope})['errors'])

    def test_command_reads_files_and_exits_nonzero_on_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            base, cand = Path(directory) / 'base.json', Path(directory) / 'next.json'
            base.write_bytes(self.base_raw)
            cand.write_bytes(self.cand_raw)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(increment.main(['--baseline', str(base), '--candidate', str(cand)]), 0)
            self.assertEqual(json.loads(output.getvalue())['new']['successful'], 2)
            changed = json.loads(self.cand_raw)
            changed['failures'] = changed['failures'][:0]
            changed['resources'] = changed['resources'][1:]
            cand.write_text(json.dumps(changed))
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(increment.main(['--baseline', str(base), '--candidate', str(cand)]), 1)
            base.write_text('{"meta": {}, "resources": [], "failures": []} trailing')
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(increment.main(['--baseline', str(base), '--candidate', str(cand)]), 2)


if __name__ == '__main__':
    unittest.main()
