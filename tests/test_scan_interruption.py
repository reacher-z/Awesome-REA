"""An interrupted scan saves finished README reads once and resumes without repeating them."""
import base64
from concurrent.futures import wait as real_wait
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import scan_sources as scanner

QUERY = 'topic:reverse-engineering is:public fork:false archived:false'
BODY = b'# Example\n\n## Usage\nInspect a firmware image.\n'
OID = hashlib.sha1(b'blob ' + str(len(BODY)).encode() + b'\0' + BODY).hexdigest()


def repository(number):
    return {'id': number, 'full_name': f'example/tool-{number}', 'html_url': f'https://github.com/example/tool-{number}',
            'private': False, 'visibility': 'public', 'archived': False, 'fork': False,
            'description': f'Firmware analysis tool {number}', 'topics': ['firmware-analysis'],
            'stargazers_count': number, 'default_branch': 'main', '_metadata_observed_at': '2026-10-19T00:00:00Z'}


class API:
    """Offline search, identity and README responses; README reads are counted per repository."""
    def __init__(self, count):
        self.count, self.reads, self.lock = count, {}, threading.Lock()

    def json(self, path, search=False):
        if search:
            return {'items': [repository(number) for number in range(1, self.count + 1)],
                    'total_count': self.count, 'incomplete_results': False}
        if path.startswith('/repositories/'):
            return repository(int(path.rsplit('/', 1)[1]))
        number = int(path.split('/')[3].split('?')[0].rsplit('-', 1)[1])
        with self.lock:
            self.reads[number] = self.reads.get(number, 0) + 1
        return {'type': 'file', 'path': 'README.md', 'sha': OID, 'size': len(BODY),
                'html_url': repository(number)['html_url'] + '/blob/main/README.md',
                'encoding': 'base64', 'content': base64.b64encode(BODY).decode()}


class Transport:
    """GraphQL stand-in whose second batch is interrupted before it returns."""
    batch_size = 2

    def __init__(self):
        self.calls = 0

    def fetch_batch(self, repositories):
        self.calls += 1
        if self.calls == 2:
            raise KeyboardInterrupt
        return {r['id']: {'status': 'ok', 'repository': repository(r['id']), 'content': BODY,
                          'metadata': {'path': 'README.md', 'sha': OID, 'size': len(BODY), 'commit_oid': 'a' * 40,
                                       'html_url': repository(r['id'])['html_url'] + '/blob/' + 'a' * 40 + '/README.md'}}
                for r in repositories}


def arguments(output, target, workers=1):
    return SimpleNamespace(target=target, workers=workers, requests_per_second=1, max_pages=1, candidate_buffer=0,
                           seed_curated=False, seed_papers=False, queries=[QUERY], output=output)


def interrupt_on_call(number):
    """Interrupt the main thread's Nth wait, after every submitted read has finished."""
    calls = []

    def wait(pending, return_when):
        calls.append(1)
        if len(calls) == number:
            real_wait(pending)
            raise KeyboardInterrupt
        return real_wait(pending, return_when=return_when)
    return wait


class ScanInterruptionTests(unittest.TestCase):
    def run_scan(self, api, args, **options):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            code = scanner.run_scan(api, args, **options)
        return code, json.loads(args.output.read_text()), output.getvalue()

    def assert_unique_attempts(self, document):
        ids = [entry['id'] for entry in document['resources'] + document['failures']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(document['meta']['attempted_readme_scans'], len(ids))
        self.assertTrue(set(ids) <= set(document['meta']['discovered_repository_ids']))

    def test_interrupted_rest_reads_keep_each_finished_attempt_once(self):
        with tempfile.TemporaryDirectory() as directory:
            api = API(8)
            args = arguments(Path(directory) / 'scan.json', 8, workers=2)
            with patch.object(scanner, 'wait', interrupt_on_call(2)):
                code, document, output = self.run_scan(api, args)
        self.assertEqual(code, 130)
        self.assertIn('INTERRUPTED success=', output)
        # The first wait recorded one read; the interruption recorded the read that had finished meanwhile.
        self.assertEqual(document['meta']['successful_readme_scans'], len(document['resources']))
        self.assertEqual(sorted(int(record['id'][5:]) for record in document['resources']),
                         sorted(number for number, count in api.reads.items() if count))
        self.assertLess(len(document['resources']), 8)
        self.assertEqual((document['meta']['status'], document['meta']['completed_at']), ('in-progress', None))
        self.assertEqual(document['meta']['current_run']['status'], 'in-progress')
        self.assertIsNone(document['meta']['current_run']['completed_at'])
        self.assert_unique_attempts(document)

    def test_interruption_during_a_progress_checkpoint_does_not_duplicate_the_recorded_read(self):
        real_save, raised = scanner.save, []

        def save(output, meta, records, failures, complete=False):
            if len(records) == 100 and not raised:
                raised.append(1)
                raise KeyboardInterrupt
            return real_save(output, meta, records, failures, complete)
        with tempfile.TemporaryDirectory() as directory:
            args = arguments(Path(directory) / 'scan.json', 120)
            with patch.object(scanner, 'save', save):
                code, document, _ = self.run_scan(API(120), args)
        self.assertEqual((code, raised), (130, [1]))
        self.assertGreaterEqual(len(document['resources']), 100)
        self.assertEqual(document['meta']['status'], 'in-progress')
        self.assert_unique_attempts(document)

    def test_interrupted_graphql_batch_keeps_earlier_batches(self):
        with tempfile.TemporaryDirectory() as directory:
            args = arguments(Path(directory) / 'scan.json', 6)
            code, document, _ = self.run_scan(API(6), args, readme_transport=Transport())
        self.assertEqual(code, 130)
        self.assertEqual([record['id'] for record in document['resources']], ['scan-1', 'scan-2'])
        self.assertEqual(document['meta']['status'], 'in-progress')
        self.assertEqual(document['meta']['current_run']['readme_transport']['outcomes']['ok'], 2)
        self.assert_unique_attempts(document)

    def test_resume_reads_only_unattempted_ids_and_leaves_the_checkpoint_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = Path(directory) / 'checkpoint.json'
            with patch.object(scanner, 'wait', interrupt_on_call(3)):
                code, interrupted, _ = self.run_scan(API(6), arguments(checkpoint, 6))
            self.assertEqual(code, 130)
            retained = {record['id'] for record in interrupted['resources']}
            before = checkpoint.read_bytes()
            resumed, digest = scanner.load_resume(checkpoint)
            api = API(6)
            code, document, _ = self.run_scan(api, arguments(Path(directory) / 'next.json', 6),
                                              resumed=resumed, resume_sha256=digest)
            self.assertEqual(checkpoint.read_bytes(), before)
        self.assertEqual(code, 0)
        self.assertEqual(document['meta']['status'], 'complete')
        self.assertEqual(len(document['resources']), 6)
        self.assertEqual(document['resources'][:len(retained)], interrupted['resources'])
        self.assertFalse(retained & {f'scan-{number}' for number in api.reads})
        self.assertEqual(set(api.reads.values()), {1})
        self.assertEqual(document['meta']['resume_history'][-1]['source_sha256'], digest)
        self.assert_unique_attempts(document)


if __name__ == '__main__':
    unittest.main()
