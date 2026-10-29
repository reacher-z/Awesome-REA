"""Recovery receipts and quota guards must describe actual bounded REST reads."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import scheduled_source_scan as scheduled
from validate import validate_source_index


class RecoveryProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads((ROOT / 'data/source-index.json').read_text(encoding='utf-8'))
        row = cls.document['resources'][0]
        for key in ('readme_integrity_review', 'readme_transport',
                    'readme_graphql_endpoint', 'readme_commit_sha'):
            row.pop(key, None)
        body = b'# Complete synthetic recovery fixture\n'
        oid = hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()
        row.update(readme_path='README.md', readme_git_sha=oid, readme_content_git_sha=oid,
                   readme_git_sha_matches_content=True, readme_sha256=hashlib.sha256(body).hexdigest(),
                   readme_bytes=len(body), readme_lines=1, readme_heading_count=1,
                   readme_url=row['url'] + '/blob/main/README.md',
                   readme_api_url='https://api.github.com/repos/' + row['full_name'] + '/readme?ref=main',
                   readme_blob_api_url='https://api.github.com/repos/' + row['full_name'] + '/git/blobs/' + oid)

    def test_verified_recovery_preserves_both_endpoints_in_strict_checkpoint(self):
        errors = []
        validate_source_index(self.document, errors)
        self.assertEqual(errors, [])
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'checkpoint.json'
            path.write_text(json.dumps(self.document), encoding='utf-8')
            restored, _ = scheduled.read_snapshot(path)
        self.assertEqual(restored['resources'][0]['readme_blob_api_url'],
                         self.document['resources'][0]['readme_blob_api_url'])
        self.assertIn('readme_api_url', restored['resources'][0])

    def test_foreign_mutable_or_unverified_recovery_provenance_is_rejected(self):
        mutations = {
            'foreign repository': lambda row: row.update(readme_blob_api_url=
                'https://api.github.com/repos/other/repository/git/blobs/' + row['readme_git_sha']),
            'foreign host': lambda row: row.update(readme_blob_api_url=
                row['readme_blob_api_url'].replace('api.github.com', 'example.invalid')),
            'different blob': lambda row: row.update(readme_blob_api_url=
                row['readme_blob_api_url'].rsplit('/', 1)[0] + '/' + 'f' * 40),
            'mutable ref': lambda row: row.update(readme_blob_api_url=
                row['readme_blob_api_url'].rsplit('/', 1)[0] + '/main'),
            'query suffix': lambda row: row.update(readme_blob_api_url=row['readme_blob_api_url'] + '?ref=main'),
            'fragment suffix': lambda row: row.update(readme_blob_api_url=row['readme_blob_api_url'] + '#readme'),
            'missing README lookup': lambda row: row.pop('readme_api_url'),
            'unverified original bytes': lambda row: row.update(readme_git_sha_matches_content=False),
            'missing hash check': lambda row: row.pop('readme_git_sha_matches_content'),
            'mixed GraphQL receipt': lambda row: row.update(readme_transport='github-graphql-blob',
                readme_graphql_endpoint='https://api.github.com/graphql', readme_commit_sha='a' * 40),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                document = copy.deepcopy(self.document)
                mutate(document['resources'][0])
                errors = []
                validate_source_index(document, errors)
                self.assertTrue(any('REST blob recovery' in error for error in errors), errors)


class RecoveryQuotaTests(unittest.TestCase):
    @staticmethod
    def policy(remaining, statuses):
        class Transport:
            batch_size = 16
            last_batch_receipts = [{'rate_limit': {'cost': 1}}]
            rate_limit = {'remaining': 1000}

            def __init__(self):
                self.calls = 0

            def fetch_batch(self, rows):
                self.calls += 1
                return {row['id']: {'status': statuses[index]} for index, row in enumerate(rows)}

        transport = Transport()
        policy = scheduled.ScheduledTransport(transport, SimpleNamespace(rate={'core': {'remaining': remaining}}))
        return policy, transport

    def test_three_request_reserve_blocks_old_two_request_budget_and_allows_exact_boundary(self):
        # Each fallback can need public identity + README + immutable blob.
        for count in (1, 2, 16):
            rows = [{'id': number + 1} for number in range(count)]
            for remaining in (100 + 2 * count, 100 + 3 * count - 1):
                with self.subTest(count=count, remaining=remaining):
                    policy, transport = self.policy(remaining, ['fallback'] * count)
                    result = policy.fetch_batch(rows)
                    self.assertEqual({row['status'] for row in result.values()}, {'deferred'})
                    self.assertEqual(policy.fallbacks, 0)
                    self.assertEqual(transport.calls, 1)
            with self.subTest(count=count, exact_boundary=True):
                policy, transport = self.policy(100 + 3 * count, ['fallback'] * count)
                result = policy.fetch_batch(rows)
                self.assertEqual({row['status'] for row in result.values()}, {'fallback'})
                self.assertEqual(policy.fallbacks, count)
                self.assertEqual(transport.calls, 1)

    def test_core_reserve_counts_only_fallbacks_and_keeps_verified_sibling(self):
        rows = [{'id': 1}, {'id': 2}]
        for remaining, expected in ((102, 'deferred'), (103, 'fallback')):
            with self.subTest(remaining=remaining):
                policy, _ = self.policy(remaining, ['fallback', 'ok'])
                result = policy.fetch_batch(rows)
                self.assertEqual(result[1]['status'], expected)
                self.assertEqual(result[2]['status'], 'ok')
                self.assertEqual(policy.fallbacks, int(expected == 'fallback'))


if __name__ == '__main__':
    unittest.main()
