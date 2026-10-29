"""Transport changes must preserve evidence and avoid counting deferred metadata."""
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
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from scan_sources import ScanError, run_scan, save

BODY = b'# Example\n\n## Usage\nRead a public protocol trace.\n'
OID = hashlib.sha1(b'blob ' + str(len(BODY)).encode() + b'\0' + BODY).hexdigest()
QUERY = 'topic:reverse-engineering is:public fork:false archived:false'


def repository():
    return {'id': 42, 'full_name': 'example/protocol',
            'html_url': 'https://github.com/example/protocol', 'private': False,
            'visibility': 'public', 'archived': False, 'fork': False,
            'description': 'A protocol analysis tool', 'topics': ['protocol-analysis'],
            'stargazers_count': 3, 'default_branch': 'main',
            '_metadata_observed_at': '2026-10-18T12:00:00Z'}


class API:
    def __init__(self):
        self.readme_calls = 0

    def json(self, path, search=False):
        if search:
            return {'items': [repository()], 'total_count': 1, 'incomplete_results': False}
        if path.startswith('/repositories/'):
            return repository()
        self.readme_calls += 1
        return {'type': 'file', 'path': 'README.md', 'sha': OID, 'size': len(BODY),
                'html_url': repository()['html_url'] + '/blob/main/README.md',
                'encoding': 'base64', 'content': base64.b64encode(BODY).decode()}


class Transport:
    batch_size = 8

    def __init__(self, status):
        self.status = status

    def fetch_batch(self, repositories):
        return {r['id']: {'status': self.status, 'repository': repository(), 'content': BODY,
                         'metadata': {'path': 'README.md', 'sha': OID, 'size': len(BODY),
                                      'commit_oid': 'a' * 40,
                                      'html_url': repository()['html_url'] + '/blob/' + 'a' * 40 + '/README.md'}}
                for r in repositories}


class ScanTransportTests(unittest.TestCase):
    def scan(self, status, *, api=None, transport=None, target=1):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'scan.json'
            args = SimpleNamespace(target=target, workers=1, requests_per_second=1,
                                   max_pages=1, candidate_buffer=0, seed_curated=False,
                                   seed_papers=False, queries=[QUERY], output=output)
            api = api or API()
            with contextlib.redirect_stdout(io.StringIO()):
                code = run_scan(api, args, readme_transport=transport or Transport(status))
            return code, json.loads(output.read_text()), api

    def test_checkpoint_keeps_unicode_bytes_and_does_not_mutate_retained_state(self):
        _, document, _ = self.scan('ok')
        document['resources'][0]['description_en'] = '协议分析 — trace 🔎\nSecond line'
        original = copy.deepcopy(document)
        expected = (json.dumps(document, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'scan.json'
            with patch('scan_sources.now', return_value=document['meta']['last_checkpoint_at']):
                save(output, document['meta'], document['resources'], document['failures'], complete=True)
            self.assertEqual(output.read_bytes(), expected)
        self.assertEqual(document, original)

    def test_checkpoint_encoding_failure_keeps_the_previous_checkpoint(self):
        _, document, _ = self.scan('ok')
        document['resources'][0]['unserializable'] = object()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'scan.json'
            output.write_bytes(b'previous checkpoint')
            with self.assertRaises(TypeError):
                save(output, document['meta'], document['resources'], document['failures'])
            self.assertEqual(output.read_bytes(), b'previous checkpoint')

    def test_graphql_reads_have_real_hashes_and_no_fabricated_rest_request(self):
        code, document, api = self.scan('ok')
        self.assertEqual(code, 0)
        self.assertEqual(api.readme_calls, 0)
        record = document['resources'][0]
        self.assertEqual(record['readme_sha256'], hashlib.sha256(BODY).hexdigest())
        self.assertEqual(record['readme_commit_sha'], 'a' * 40)
        self.assertEqual(record['readme_transport'], 'github-graphql-blob')
        self.assertNotIn('readme_api_url', record)
        self.assertEqual(record['matched_queries'], [QUERY])
        self.assertNotIn(BODY.decode(), json.dumps(document))

    def test_fallback_performs_a_real_rest_read(self):
        code, document, api = self.scan('fallback')
        self.assertEqual((code, api.readme_calls), (0, 1))
        self.assertIn('readme_api_url', document['resources'][0])
        self.assertNotIn('readme_transport', document['resources'][0])

    def test_backpressure_stays_pending_without_rest_escape_or_false_failure(self):
        for status in ('retry', 'deferred'):
            with self.subTest(status=status):
                code, document, api = self.scan(status)
                self.assertEqual((code, api.readme_calls), (1, 0))
                self.assertEqual(document['resources'], [])
                self.assertEqual(document['failures'], [])
                self.assertEqual(document['meta']['status'], 'in-progress')
                self.assertEqual(document['meta']['unattempted_candidates'], 1)

    def test_ineligible_metadata_never_counts_as_a_readme_attempt(self):
        code, document, api = self.scan('rejected')
        self.assertEqual((code, api.readme_calls), (1, 0))
        self.assertEqual(document['meta']['attempted_readme_scans'], 0)
        self.assertEqual(document['meta']['unattempted_candidates'], 1)

    def test_later_backpressure_suppresses_earlier_sibling_rest_fallback(self):
        class TwoAPI(API):
            def json(self, path, search=False):
                if not search:
                    return super().json(path, search)
                second = {**repository(), 'id': 43, 'full_name': 'example/second',
                          'html_url': 'https://github.com/example/second'}
                return {'items': [repository(), second], 'total_count': 2, 'incomplete_results': False}

        class Mixed(Transport):
            def fetch_batch(self, repositories):
                result = super().fetch_batch(repositories)
                result[43]['status'] = 'deferred'
                return result

        code, document, api = self.scan('fallback', api=TwoAPI(), transport=Mixed('fallback'), target=2)
        self.assertEqual((code, api.readme_calls), (1, 0))
        self.assertEqual(document['meta']['attempted_readme_scans'], 0)
        self.assertEqual(document['meta']['status'], 'in-progress')

    def test_exhausted_rest_backpressure_leaves_ids_pending_and_stops_sibling_requests(self):
        class TwoAPI(API):
            def __init__(self, reason, http_status):
                super().__init__()
                self.reason, self.http_status, self.rest_calls = reason, http_status, 0

            def json(self, path, search=False):
                if search:
                    other = {**repository(), 'id': 43, 'full_name': 'example/second',
                             'html_url': 'https://github.com/example/second'}
                    return {'items': [repository(), other], 'total_count': 2, 'incomplete_results': False}
                self.rest_calls += 1
                raise ScanError(self.reason, self.http_status)

        for reason, status in [('http-429', 429), ('http-503', 503), ('network-failure', None)]:
            api = TwoAPI(reason, status)
            code, document, _ = self.scan('fallback', api=api, target=2)
            self.assertEqual(code, 1)
            self.assertEqual(api.rest_calls, 1)
            self.assertEqual(document['resources'], [])
            self.assertEqual(document['failures'], [])
            self.assertEqual(document['meta']['status'], 'in-progress')
            self.assertEqual(document['meta']['unattempted_candidates'], 2)

    def test_verified_but_nontext_blob_is_a_recorded_failed_read(self):
        class Nontext(Transport):
            def fetch_batch(self, repositories):
                result = super().fetch_batch(repositories)
                content = ('\ufffd' * 30).encode()
                for row in result.values():
                    row['content'] = content
                    row['metadata'].update(size=len(content), sha=hashlib.sha1(
                        b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest())
                return result

        code, document, api = self.scan('ok', transport=Nontext('ok'))
        self.assertEqual((code, api.readme_calls), (1, 0))
        self.assertEqual(document['meta']['successful_readme_scans'], 0)
        self.assertEqual(document['failures'][0]['reason'], 'nontext-readme')

    def test_frontier_recovers_historical_query_without_counting_a_new_request(self):
        import search_frontier as frontier
        import scan_sources
        approved = ['topic:reverse-engineering']
        state = frontier.new_frontier(until='2026-10-18T00:00:00Z', approved_queries=approved)
        request = frontier.next_request(state)
        repo = {**repository(), 'created_at': '2026-10-01T00:00:00Z'}
        old_run = '2026-10-18T01:00:00Z'
        frontier.record_response(state, request, {'items': [repo], 'total_count': 1,
                                 'incomplete_results': False}, observed_at=old_run, run_id=old_run)
        cache = scan_sources.ROOT / '.cache'
        cache.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=cache) as directory:
            output = Path(directory) / 'scan.json'
            args = SimpleNamespace(target=1, workers=1, requests_per_second=1, max_pages=1,
                                   candidate_buffer=0, seed_curated=False, seed_papers=False,
                                   queries=[QUERY], output=output)
            api = API()
            with contextlib.redirect_stdout(io.StringIO()), patch.object(api, 'json', side_effect=AssertionError('No HTTP query expected')):
                code = run_scan(api, args, readme_transport=Transport('ok'),
                                frontier=(state, Path(directory) / 'frontier.json', approved))
            document = json.loads(output.read_text())
            self.assertEqual(code, 0)
            self.assertEqual(document['meta']['current_run']['query_count'], 0)
            self.assertEqual(document['meta']['queries'][0]['run_id'], old_run)
            self.assertEqual(document['resources'][0]['matched_queries'], [request['query']])
            self.assertIsNotNone(state['candidates']['42']['checkpoint_sha256'])
            # A newer acknowledged frontier cannot silently skip evidence in an older source file.
            with self.assertRaisesRegex(ValueError, 'absent from this scan checkpoint'):
                run_scan(api, args, readme_transport=Transport('ok'),
                         frontier=(state, Path(directory) / 'frontier.json', approved))

    def test_saved_queue_over_1000_is_drained_without_new_http_discovery(self):
        import search_frontier as frontier
        import scan_sources
        approved = ['topic:reverse-engineering', 'topic:decompiler', 'topic:website-clone']
        state = frontier.new_frontier(until='2026-10-18T00:00:00Z', approved_queries=approved[:2])
        old_run = '2026-10-18T01:00:00Z'
        # Two completed queries retain 1,200 distinct identities. A third open
        # query makes an unnecessary discovery request observable to the sentinel.
        for _ in range(12):
            request = frontier.next_request(state)
            root = next(item['root'] for item in state['partitions'] if item['id'] == request['partition_id'])
            start = root * 600 + (request['page'] - 1) * 100 + 1
            items = [{**repository(), 'id': identifier, 'full_name': f'example/tool-{identifier}',
                      'html_url': f'https://github.com/example/tool-{identifier}',
                      'created_at': '2026-10-01T00:00:00Z'} for identifier in range(start, start + 100)]
            frontier.record_response(state, request, {'items': items, 'total_count': 600,
                                     'incomplete_results': False}, observed_at=old_run, run_id=old_run)
        frontier.add_queries(state, approved[2:], approved_queries=approved)
        frontier.defer_candidates(state, [1], reason='retry', retry_after_seconds=86400)
        deferred = dict(state['candidates']['1'])

        class VerifiedTransport:
            batch_size = 16

            def fetch_batch(self, repositories):
                return {row['id']: {'status': 'ok', 'repository': {**repository(), **row}, 'content': BODY,
                    'metadata': {'path': 'README.md', 'sha': OID, 'size': len(BODY), 'commit_oid': 'a' * 40,
                                 'html_url': row['html_url'] + '/blob/' + 'a' * 40 + '/README.md'}}
                        for row in repositories}

        cache = scan_sources.ROOT / '.cache'
        cache.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=cache) as directory:
            output, frontier_path = Path(directory) / 'scan.json', Path(directory) / 'frontier.json'
            frontier.save_frontier(frontier_path, state, approved_queries=approved)
            restored = frontier.load_frontier(frontier_path, approved_queries=approved)
            args = SimpleNamespace(target=1100, workers=1, requests_per_second=1, max_pages=1,
                                   candidate_buffer=0, seed_curated=False, seed_papers=False,
                                   queries=[QUERY], output=output)
            api = API()
            with contextlib.redirect_stdout(io.StringIO()), \
                    patch.object(api, 'json', side_effect=AssertionError('Saved queue must satisfy the target')) as http, \
                    patch.object(frontier, 'pending_candidates', wraps=frontier.pending_candidates) as pages:
                code = run_scan(api, args, readme_transport=VerifiedTransport(),
                                frontier=(restored, frontier_path, approved))
            document = json.loads(output.read_text())
            self.assertEqual(code, 0)
            http.assert_not_called()
            self.assertEqual([call.kwargs['offset'] for call in pages.call_args_list], [0, 1000])
            self.assertEqual([call.kwargs['limit'] for call in pages.call_args_list], [1000, 100])
            self.assertEqual(len({call.kwargs['now'] for call in pages.call_args_list}), 1)
            self.assertIsNotNone(pages.call_args_list[0].kwargs['now'])
            self.assertEqual(document['meta']['current_run']['query_count'], 0)
            self.assertEqual({row['id'] for row in document['resources']},
                             {f'scan-{identifier}' for identifier in range(2, 1102)})
            self.assertEqual(restored['request_count'], 12)
            self.assertIsNotNone(frontier.next_request(restored))
            self.assertEqual(restored['candidates']['1'], deferred)
            acknowledged = {int(key) for key, row in restored['candidates'].items() if row['checkpoint_sha256']}
            self.assertEqual(acknowledged, set(range(2, 1102)))
            self.assertEqual([row['id'] for row in frontier.pending_candidates(restored)], list(range(1102, 1201)))


if __name__ == '__main__':
    unittest.main()
