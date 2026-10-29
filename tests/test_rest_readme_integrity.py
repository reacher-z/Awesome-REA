"""Count only complete, hash-verified text; immutable recovery cannot evade API errors."""
import base64
import copy
import hashlib
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from scan_sources import MAX_README_BYTES, ScanError, readme_record, scan_readme


def git_sha(body):
    return hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()


REPO = {'id': 42, 'full_name': 'example/recreation', 'html_url': 'https://github.com/example/recreation',
        'private': False, 'fork': False, 'archived': False, 'default_branch': 'main',
        '_metadata_observed_at': '2026-10-19T00:00:00Z', '_matched_queries': []}


class API:
    def __init__(self, full, inline=None):
        self.calls = []
        self.repository = copy.deepcopy(REPO)
        self.metadata = {'type': 'file', 'size': len(full), 'sha': git_sha(full), 'path': 'README.md',
                         'html_url': REPO['html_url'] + '/blob/main/README.md', 'encoding': 'base64',
                         'content': base64.b64encode(full if inline is None else inline).decode()}
        self.blob = {'sha': git_sha(full), 'size': len(full), 'encoding': 'base64',
                     'content': base64.b64encode(full).decode()}
        self.fail_at = None

    def json(self, path):
        self.calls.append(path)
        if len(self.calls) == self.fail_at:
            raise ScanError('rate-limited', 429)
        if path == '/repos/example/recreation/readme?ref=main':
            return self.metadata
        if path == '/repositories/42':
            return self.repository
        if path == '/repos/example/recreation/git/blobs/' + self.metadata['sha']:
            return self.blob
        raise AssertionError('Unexpected request')


class RestIntegrityTests(unittest.TestCase):
    def test_truncated_512kb_inline_body_recovers_exact_full_immutable_blob(self):
        full = b'# Recreation\n' + b'x' * 600_000
        api = API(full, full[:512000])
        record, failure = scan_readme(api, REPO)
        self.assertIsNone(failure)
        self.assertEqual(len(api.calls), 3)
        self.assertEqual(record['readme_bytes'], len(full))
        self.assertEqual(record['readme_sha256'], hashlib.sha256(full).hexdigest())
        self.assertTrue(record['readme_git_sha_matches_content'])
        self.assertEqual(record['readme_blob_api_url'], 'https://api.github.com' + api.calls[-1])
        self.assertEqual(record['readme_api_url'], 'https://api.github.com' + api.calls[1])
        self.assertEqual(record['readme_url'], api.metadata['html_url'])

    def test_matching_size_but_wrong_hash_recovers_once(self):
        full = b'# Exact\n'
        api = API(full, b'# Other\n')
        record, failure = scan_readme(api, REPO)
        self.assertIsNone(failure)
        self.assertEqual(record['readme_sha256'], hashlib.sha256(full).hexdigest())
        self.assertEqual(len(api.calls), 3)

    def test_inline_exact_bytes_need_no_recovery_or_extra_metadata_call(self):
        api = API('协议 🔎\n'.encode())
        record, failure = scan_readme(api, REPO)
        self.assertIsNone(failure)
        self.assertEqual(len(api.calls), 2)
        self.assertNotIn('readme_blob_api_url', record)

    def test_none_encoding_uses_advertised_blob_instead_of_mutable_raw_branch(self):
        api = API(b'# Full\n'); api.metadata.update(encoding='none', content='')
        record, failure = scan_readme(api, REPO)
        self.assertIsNone(failure)
        self.assertEqual(len(api.calls), 3)
        self.assertTrue(record['readme_git_sha_matches_content'])

    def test_bad_immutable_blob_is_failed_without_third_representation(self):
        for change in ({'sha': '0'*40}, {'size': 4}, {'size': True}, {'encoding': 'none'},
                       {'size': MAX_README_BYTES+1}, {'content': '???'},
                       {'content': base64.b64encode(b'# Truncated').decode()}):
            api = API(b'# Full content\n', b'bad'); api.blob.update(change)
            with self.subTest(change=change):
                record, failure = scan_readme(api, REPO)
                self.assertIsNone(record)
                self.assertIsNotNone(failure)
                self.assertEqual(len(api.calls), 3)

    def test_api_backpressure_at_any_phase_never_triggers_another_fetch(self):
        for index in (1, 2, 3):
            api = API(b'# Full content\n', b'bad'); api.fail_at = index
            record, failure = scan_readme(api, REPO)
            self.assertIsNone(record)
            self.assertEqual((failure['reason'], failure['http_status']), ('rate-limited', 429))
            self.assertEqual(len(api.calls), index)

    def test_private_renamed_or_reassigned_identity_never_fetches_blob(self):
        for change in ({'id': 43}, {'id': True}, {'private': True}, {'fork': True}, {'archived': True},
                       {'full_name': 'example/renamed'}, {'private': None}):
            api = API(b'# Full content\n', b'bad'); api.repository.update(change)
            record, failure = scan_readme(api, REPO)
            self.assertIsNone(record)
            self.assertEqual(failure['reason'], 'readme-repository-identity-unconfirmed')
            self.assertEqual(len(api.calls), 1)

    def test_invalid_metadata_cannot_start_blob_recovery(self):
        for change in ({'size': None}, {'size': True}, {'size': -1}, {'sha': '../bad'},
                       {'path': '../README.md'}, {'path': '/README.md'}, {'html_url': 'https://example.org/README'}):
            api = API(b'# Full\n'); api.metadata.update(change)
            record, failure = scan_readme(api, REPO)
            self.assertIsNone(record)
            self.assertIsNotNone(failure)
            self.assertEqual(len(api.calls), 2)

    def test_factory_rejects_incomplete_bytes_and_unsupported_text(self):
        for body, metadata, reason in [(b'# A', {'size': 4, 'sha': git_sha(b'# A')}, 'readme-size-mismatch'),
                                      (b'# A', {'size': 3, 'sha': '0'*40}, 'readme-git-sha-mismatch'),
                                      (b'\xff', {'size': 1, 'sha': git_sha(b'\xff')}, 'non-utf8-readme')]:
            with self.assertRaises(ScanError) as error:
                readme_record(REPO, metadata, body)
            self.assertEqual(error.exception.reason, reason)


if __name__ == '__main__':
    unittest.main()
