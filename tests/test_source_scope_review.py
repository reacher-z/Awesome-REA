"""Scope review receipts re-read only named scans' recorded blobs and accept only byte-identical captures."""
import base64
import contextlib
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import source_scope_review
from scan_sources import ScanError
from source_scope import validate_scope
from source_scope_review import main, review_record, run_review

TOKEN = 'unit-test-token-sentinel'
TEXT = b'# Tool\n\nA README marker that must never reach a receipt.\n'


def git_sha(content):
    return hashlib.sha1(b'blob ' + str(len(content)).encode('ascii') + b'\0' + content).hexdigest()


def repo(identifier, full_name, **changes):
    return {'id': identifier, 'full_name': full_name, 'html_url': 'https://github.com/' + full_name,
            'private': False, 'fork': False, 'archived': False, **changes}


def scan(identifier, full_name, content=TEXT, **changes):
    return {'id': f'scan-{identifier}', 'full_name': full_name, 'url': 'https://github.com/' + full_name,
            'scan_status': 'readme-scanned', 'readme_url': f'https://github.com/{full_name}/blob/main/README.md',
            'readme_git_sha': git_sha(content), 'readme_bytes': len(content),
            'readme_sha256': hashlib.sha256(content).hexdigest(), 'observed_at': '2026-10-16T01:35:25Z', **changes}


def blob(data, **changes):
    return {'sha': git_sha(data), 'size': len(data), 'encoding': 'base64',
            'content': base64.encodebytes(data).decode('ascii'), **changes}


class FakeAPI:
    """Answer listed paths only; any other request fails the test."""
    def __init__(self, responses):
        self.responses, self.paths = responses, []

    def json(self, path):
        self.paths.append(path)
        if path not in self.responses:
            raise AssertionError('unexpected request ' + path)
        response = self.responses[path]
        if isinstance(response, ScanError):
            raise response
        return copy.deepcopy(response)


def blob_path(record):
    return f'/repos/{record["full_name"]}/git/blobs/{record["readme_git_sha"]}'


def document(*records, failures=()):
    return {'meta': {'completed_at': '2026-10-16T11:55:19Z'}, 'resources': list(records), 'failures': list(failures)}


class ReceiptTests(unittest.TestCase):
    def test_a_matching_blob_yields_exactly_the_scope_evidence_validation_binds(self):
        record = scan(7, 'owner/tool')
        api = FakeAPI({'/repositories/7': repo(7, 'owner/tool'), blob_path(record): blob(TEXT)})
        entry, content = review_record(api, record)
        self.assertEqual(api.paths, ['/repositories/7', blob_path(record)])
        self.assertEqual((entry['outcome'], content), ('match', TEXT))
        self.assertEqual(entry['scope_evidence'], {'readme_sha256': record['readme_sha256'],
                                                   'evidence_url': record['readme_url']})
        self.assertEqual((entry['blob_bytes'], entry['blob_sha256'], entry['blob_content_git_sha']),
                         (len(TEXT), record['readme_sha256'], record['readme_git_sha']))
        self.assertNotIn('README marker', json.dumps(entry))
        decision = {'decision': 'exclude', 'reason_code': 'unrelated-topic', 'reason_en': 'Unrelated.',
                    'reason_zh': '与主题无关。', 'reviewed_at': '2026-10-17', **entry['scope_evidence']}
        errors = []
        validate_scope([record], {record['id']: decision}, errors)
        self.assertEqual(errors, [])

    def test_a_mismatch_keeps_advertised_and_computed_identifiers_apart_and_yields_no_evidence(self):
        # The capture's own bytes hash to a different Git ID than the blob GitHub advertised.
        captured, advertised = b'captured bytes\n', b'different advertised bytes\n'
        record = scan(361197329, 'ddup-gh/recdemo', content=captured, readme_git_sha=git_sha(advertised),
                      readme_content_git_sha=git_sha(captured), readme_git_sha_matches_content=False)
        api = FakeAPI({'/repositories/361197329': repo(361197329, 'ddup-gh/recdemo'), blob_path(record): blob(advertised)})
        entry, content = review_record(api, record)
        self.assertEqual((entry['outcome'], content), ('mismatch', None))
        self.assertNotIn('scope_evidence', entry)
        self.assertEqual((entry['advertised_git_sha'], entry['blob_content_git_sha']), (git_sha(advertised),) * 2)
        self.assertEqual(entry['captured_content_git_sha'], git_sha(captured))
        self.assertNotEqual(entry['blob_sha256'], entry['captured_sha256'])
        # Same bytes but a different recorded length is still a mismatch.
        record = scan(8, 'owner/tool', readme_bytes=len(TEXT) + 1)
        entry, _ = review_record(FakeAPI({'/repositories/8': repo(8, 'owner/tool'), blob_path(record): blob(TEXT)}), record)
        self.assertEqual(entry['outcome'], 'mismatch')

    def test_identity_changes_and_private_or_missing_ids_stop_before_the_blob(self):
        record = scan(9, 'owner/tool')
        for response, outcome in ((repo(9, 'owner/tool-v2'), 'identity-changed'),
                                  (repo(9, 'secret/name', private=True), 'ineligible'),
                                  (ScanError('http-404', 404), 'unavailable'), (ScanError('http-451', 451), 'unavailable'),
                                  (ScanError('network-failure'), 'inconclusive'), (repo(10, 'owner/tool'), 'inconclusive')):
            with self.subTest(outcome=outcome, response=getattr(response, 'reason', response)):
                api = FakeAPI({'/repositories/9': response})
                entry, content = review_record(api, record)
                self.assertEqual((entry['outcome'], content, api.paths), (outcome, None, ['/repositories/9']))
                self.assertNotIn('secret', json.dumps(entry))
        entry, _ = review_record(FakeAPI({'/repositories/9': repo(9, 'owner/tool-v2')}), record)
        self.assertEqual(entry['current_full_name'], 'owner/tool-v2')

    def test_an_archived_repository_is_read_and_labeled(self):
        record = scan(11, 'owner/tool')
        api = FakeAPI({'/repositories/11': repo(11, 'owner/tool', archived=True), blob_path(record): blob(TEXT)})
        entry, _ = review_record(api, record)
        self.assertEqual((entry['outcome'], entry['repository_status']), ('match', 'archived'))

    def test_a_blob_that_is_not_the_requested_object_is_inconclusive(self):
        record = scan(12, 'owner/tool')
        for response in (blob(b'other bytes\n'), blob(TEXT, sha='0' * 40), blob(TEXT, size=len(TEXT) + 1),
                         blob(TEXT, content='***'), blob(TEXT, encoding='utf-8'), [], ScanError('http-503', 503)):
            with self.subTest(response=response):
                api = FakeAPI({'/repositories/12': repo(12, 'owner/tool'), blob_path(record): response})
                entry, content = review_record(api, record)
                self.assertEqual((entry['outcome'], content), ('inconclusive', None))
                self.assertNotIn('scope_evidence', entry)
        entry, _ = review_record(FakeAPI({}), scan(13, 'owner/tool', readme_git_sha='not-a-sha'))
        self.assertEqual((entry['outcome'], entry['reason']), ('inconclusive', 'invalid-recorded-git-sha'))


class RunTests(unittest.TestCase):
    def test_only_requested_successful_scans_are_fetched_in_the_given_order(self):
        first, second, other = scan(20, 'owner/b'), scan(10, 'owner/a'), scan(30, 'owner/c')
        failure = {'id': 'scan-40', 'full_name': 'owner/d', 'scan_status': 'failed'}
        source = document(first, second, other, failures=[failure])
        before = copy.deepcopy(source)
        api = FakeAPI({'/repositories/20': repo(20, 'owner/b'), blob_path(first): blob(TEXT),
                       '/repositories/10': repo(10, 'owner/a'), blob_path(second): blob(TEXT)})
        shown = []
        report = run_review(api, source, 'f' * 64, ['scan-20', 'scan-40', 'scan-10', 'scan-99'], 'data/source-index.json',
                            lambda entry, content: shown.append((entry['id'], content)))
        self.assertEqual(source, before)
        self.assertEqual(api.paths, ['/repositories/20', blob_path(first), '/repositories/10', blob_path(second)])
        self.assertEqual([entry['id'] for entry in report['receipts']], ['scan-20', 'scan-40', 'scan-10', 'scan-99'])
        self.assertEqual((report['counts']['match'], report['counts']['not-scanned'], report['requests']), (2, 2, 4))
        self.assertEqual(shown, [('scan-20', TEXT), ('scan-10', TEXT)])
        self.assertEqual(report['source'], {'path': 'data/source-index.json', 'sha256': 'f' * 64,
                                            'completed_at': '2026-10-16T11:55:19Z'})


class CommandTests(unittest.TestCase):
    def run_main(self, argv, environment, api=None):
        output = io.StringIO()
        blocked = AssertionError('network access in a unit test')
        with patch.dict(os.environ, environment, clear=True), contextlib.redirect_stdout(output), \
                patch.object(socket.socket, 'connect', side_effect=blocked), \
                patch.object(socket, 'getaddrinfo', side_effect=blocked), \
                patch.object(source_scope_review, 'GitHub', lambda token, rate: api):
            status = main(argv)
        return status, output.getvalue()

    def test_command_needs_a_token_and_writes_a_receipt_without_readme_text(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source-index.json'
            records = [scan(10, 'owner/a'), scan(20, 'owner/b', readme_sha256='b' * 64)]
            meta = {'completed_at': '2026-10-16T11:55:19Z', 'queries': [], 'successful_readme_scans': 2,
                    'failed': 0, 'attempted_readme_scans': 2, 'unique_repos': 2, 'unattempted_candidates': 0}
            source.write_text(json.dumps({'meta': meta, 'resources': records, 'failures': []}), encoding='utf-8')
            original = source.read_bytes()
            output = Path(directory) / 'receipt.json'
            argv = ['scan-10', 'scan-20', '--source', str(source), '--output', str(output)]
            status, text = self.run_main(argv, {})
            self.assertEqual(status, 2)
            self.assertIn('nothing was requested', text)
            self.assertFalse(output.exists())
            responses = {'/repositories/10': repo(10, 'owner/a'), blob_path(records[0]): blob(TEXT),
                         '/repositories/20': repo(20, 'owner/b'), blob_path(records[1]): blob(TEXT)}
            status, text = self.run_main(argv, {'GH_TOKEN': TOKEN}, FakeAPI(responses))
            saved = output.read_text(encoding='utf-8')
            self.assertEqual(status, 1)
            self.assertIn('match scan-10 owner/a', text)
            self.assertIn('mismatch scan-20 owner/b', text)
            self.assertNotIn('README marker', text + saved)
            self.assertNotIn(TOKEN, text + saved)
            report = json.loads(saved)
            self.assertEqual((report['counts']['match'], report['counts']['mismatch'], report['requests']), (1, 1, 4))
            status, text = self.run_main(['scan-10', '--print-readme', '--source', str(source), '--output', str(output)],
                                         {'GH_TOKEN': TOKEN}, FakeAPI(responses))
            self.assertEqual(status, 0)
            self.assertIn('README marker', text)
            self.assertNotIn('README marker', output.read_text(encoding='utf-8'))
            self.assertEqual(source.read_bytes(), original)

    def test_command_bounds_its_ids_and_refuses_to_write_into_the_data_directory(self):
        for argv in (['scan-0'], ['owner/tool'], ['scan-1', 'scan-1'],
                     [f'scan-{n}' for n in range(1, source_scope_review.MAX_IDS + 2)],
                     ['scan-1', '--output', str(ROOT / 'data/source-scope.json')],
                     ['scan-1', '--output', str(ROOT / 'data/source-index.json')]):
            with self.subTest(argv=argv[:3]), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                self.run_main(argv, {'GH_TOKEN': TOKEN})


if __name__ == '__main__':
    unittest.main()
