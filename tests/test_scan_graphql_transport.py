"""Offline contracts for authenticated, bounded README GraphQL reads."""
import hashlib
from http.client import IncompleteRead
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.request import Request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import scan_graphql_transport as transport

TOKEN = 'example-token-for-offline-tests'
COMMIT = 'a' * 40
ROOT_TREE = 'b' * 40
DIRECTORY_TREE = 'c' * 40
CONTENT = '# Demo\r\n\nUTF-8: 证据 and café.\n'.encode('utf-8')


def git_sha(content):
    return hashlib.sha1(b'blob ' + str(len(content)).encode('ascii') + b'\0' + content).hexdigest()


def entry(name='README.md', content=CONTENT, **changes):
    return {'name': name, 'type': 'blob', 'mode': 0o100644,
            'oid': git_sha(content), **changes}


def tree(entries, oid=ROOT_TREE):
    return {'__typename': 'Tree', 'oid': oid, 'entries': entries}


def repository(identifier=1, name='example/demo', content=CONTENT, **changes):
    return {'__typename': 'Repository', 'databaseId': identifier, 'id': 'Repository-' + str(identifier),
            'nameWithOwner': name, 'isPrivate': False, 'isFork': False, 'isArchived': False,
            'url': 'https://github.com/' + name, 'description': 'A public reverse engineering tool.',
            'stargazerCount': 7, 'updatedAt': '2026-10-18T10:00:00Z', 'pushedAt': '2026-10-17T10:00:00Z',
            'licenseInfo': {'spdxId': 'MIT'}, 'repositoryTopics': {
                'nodes': [{'topic': {'name': 'reverse-engineering'}}], 'pageInfo': {'hasNextPage': False}},
            'defaultBranchRef': {'name': 'main', 'target': {'__typename': 'Commit', 'oid': COMMIT,
                                                         'tree': tree([entry(content=content)])}},
            'githubDirectory': None, 'docsDirectory': None, **changes}


def blob_result(identifier=1, name='example/demo', content=CONTENT, **blob_changes):
    return {'__typename': 'Repository', 'databaseId': identifier, 'nameWithOwner': name,
            'isPrivate': False, 'isFork': False, 'isArchived': False,
            'readme': {'__typename': 'Blob', 'oid': git_sha(content), 'byteSize': len(content),
                       'isBinary': False, 'isTruncated': False, 'text': content.decode('utf-8'), **blob_changes}}


def probe_result(*args, **kwargs):
    result = blob_result(*args, **kwargs)
    del result['readme']['text']
    return result


def envelope(*values, errors=None, remaining=4000):
    data = {f'r{i}': value for i, value in enumerate(values)}
    data['rateLimit'] = {'cost': 1, 'remaining': remaining, 'limit': 5000, 'resetAt': '2026-10-18T12:00:00Z'}
    return {'data': data, **({'errors': errors} if errors is not None else {})}


class FakeClock:
    def __init__(self):
        self.time = 1792321200.0  # 2026-10-18 11:00 UTC
        self.sleeps = []

    def __call__(self):
        return self.time

    def sleep(self, value):
        self.sleeps.append(value)
        self.time += value


class Response:
    def __init__(self, value, headers=None, status=200):
        self.body = value if isinstance(value, bytes) else json.dumps(value).encode('utf-8')
        self.headers, self.status = headers or {}, status
        self.closed, self.read_sizes = False, []

    def read(self, size):
        self.read_sizes.append(size)
        return self.body[:size]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.closed = True


class Opener:
    def __init__(self, *responses):
        self.responses = [value if isinstance(value, (Response, Exception)) else Response(value) for value in responses]
        self.requests = []

    def open(self, request, timeout):
        self.requests.append((request, timeout))
        if not self.responses:
            raise AssertionError('Unexpected additional network request')
        value = self.responses.pop(0)
        if isinstance(value, Exception):
            raise value
        return value


def client(*responses, **kwargs):
    clock = FakeClock()
    opener = Opener(*responses)
    instance = transport.GraphQLReadmeTransport(TOKEN, opener=opener, clock=clock,
                                               monotonic=clock, sleep=clock.sleep, **kwargs)
    return instance, opener, clock


class VerifiedReadmeTests(unittest.TestCase):
    def test_actual_unicode_bytes_and_hash_are_pinned_to_commit_and_public_id(self):
        instance, opener, clock = client(envelope(repository()), envelope(probe_result()), envelope(blob_result()))
        output = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo', 'description': 'UNTRUSTED OLD VALUE'}])[1]
        self.assertEqual(output['status'], 'ok')
        self.assertEqual(output['content'], CONTENT)
        self.assertEqual(output['metadata'], {
            'type': 'file', 'path': 'README.md', 'size': len(CONTENT), 'sha': git_sha(CONTENT),
            'commit_oid': COMMIT, 'html_url': f'https://github.com/example/demo/blob/{COMMIT}/README.md'})
        self.assertEqual(output['provenance']['content_sha256'], hashlib.sha256(CONTENT).hexdigest())
        self.assertTrue(output['provenance']['content_git_sha_matches_blob'])
        self.assertEqual(output['repository']['stargazers_count'], 7)
        self.assertEqual(output['repository']['license'], {'spdx_id': 'MIT'})
        self.assertEqual(output['repository']['topics'], ['reverse-engineering'])
        self.assertEqual(output['repository']['_metadata_observed_at'], '2026-10-18T11:00:00Z')
        self.assertNotIn('UNTRUSTED', output['repository']['description'])
        self.assertNotIn('readme_api_url', output['metadata'])
        self.assertNotIn('readme_api_url', output['provenance'])
        self.assertEqual(len(opener.requests), 3)
        self.assertEqual(clock.sleeps, [1.0, 1.0])
        for request, timeout in opener.requests:
            self.assertEqual(request.full_url, transport.GRAPHQL_URL)
            self.assertEqual(request.method, 'POST')
            self.assertEqual(request.get_header('Authorization'), 'Bearer ' + TOKEN)
            self.assertNotIn(TOKEN, request.data.decode())
            self.assertLessEqual(timeout, 60)
        payloads = [json.loads(request.data) for request, _ in opener.requests]
        self.assertNotRegex(payloads[0]['query'], r'\bsize\b|\bbyteSize\b|\btext\b')
        self.assertIn('entries { name type mode oid }', payloads[0]['query'])
        for payload in payloads[1:]:
            self.assertEqual(payload['variables']['expression0'], COMMIT + ':README.md')
        self.assertNotRegex(payloads[1]['query'], r'\btext\b')
        self.assertIn('byteSize isBinary isTruncated', payloads[1]['query'])
        self.assertRegex(payloads[2]['query'], r'\btext\b')
        self.assertEqual([row['phase'] for row in instance.last_batch_receipts], ['metadata', 'preflight', 'blob'])
        receipt_json = json.dumps(instance.last_batch_receipts)
        self.assertNotIn(TOKEN, receipt_json)
        self.assertNotIn('café', receipt_json)
        self.assertNotIn('text', receipt_json)
        self.assertEqual(instance.rate_limit['remaining'], 4000)

    def test_batch_results_are_bound_to_ids_not_response_order_or_input_metadata(self):
        instance, opener, _ = client(envelope(repository(2, 'o/two'), repository(1, 'o/one')),
                                     envelope(probe_result(2, 'o/two'), probe_result(1, 'o/one')),
                                     envelope(blob_result(2, 'o/two'), blob_result(1, 'o/one')))
        result = instance.fetch_batch([{'id': 2, 'full_name': 'o/two'}, {'id': 1, 'full_name': 'o/one'}])
        self.assertEqual(set(result), {1, 2})
        self.assertEqual(result[1]['repository']['full_name'], 'o/one')
        self.assertEqual(result[2]['repository']['full_name'], 'o/two')
        self.assertTrue(all(value['status'] == 'ok' for value in result.values()))
        self.assertEqual(len(opener.requests), 3)

    def test_same_id_rename_between_phases_updates_public_url(self):
        instance, _, _ = client(envelope(repository()), envelope(probe_result(name='example/intermediate')),
                                envelope(blob_result(name='example/renamed')))
        result = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])[1]
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['repository']['full_name'], 'example/renamed')
        self.assertIn('/example/renamed/blob/', result['metadata']['html_url'])

    def test_stored_node_id_survives_slug_rename_but_never_bypasses_numeric_binding(self):
        queued = {'id': 1, 'full_name': 'example/old', 'node_id': 'Repository-1'}
        instance, opener, _ = client(envelope(repository(name='example/renamed')),
                                     envelope(probe_result(name='example/renamed')),
                                     envelope(blob_result(name='example/renamed')))
        result = instance.fetch_batch([queued])[1]
        self.assertEqual(result['status'], 'ok')
        for request, _ in opener.requests:
            payload = json.loads(request.data)
            self.assertEqual(payload['variables']['node0'], 'Repository-1')
            self.assertIn('node(id: $node0)', payload['query'])
            self.assertNotIn('owner0', payload['variables'])
        instance, opener, _ = client(envelope(repository(identifier=99)))
        result = instance.fetch_batch([queued])[1]
        self.assertEqual((result['status'], result['reason']), ('rejected', 'repository-id-mismatch'))
        self.assertEqual(len(opener.requests), 1)

    def test_fresh_metadata_is_returned_for_rest_selection_fallback(self):
        value = repository()
        value['defaultBranchRef']['target']['tree']['entries'].append(entry('README.rst'))
        instance, opener, _ = client(envelope(value))
        result = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])[1]
        self.assertEqual(result['status'], 'fallback')
        self.assertEqual(result['reason'], 'ambiguous-readme-selection')
        self.assertEqual(result['repository']['id'], 1)
        self.assertIsNone(result['content'])
        self.assertEqual(len(opener.requests), 1)

    def test_github_root_docs_priority_and_pinned_directory_identity(self):
        for prefix in ('.github', '', 'docs'):
            with self.subTest(prefix=prefix):
                value = repository()
                if prefix:
                    root_entries = [entry(prefix, type='tree', mode=0o040000, oid=DIRECTORY_TREE)]
                    if prefix == '.github':
                        root_entries.append(entry())  # A lower-priority root README must not win.
                    value['defaultBranchRef']['target']['tree'] = tree(root_entries)
                    field = 'githubDirectory' if prefix == '.github' else 'docsDirectory'
                    value[field] = tree([entry('ReadMe.md')], DIRECTORY_TREE)
                instance, _, _ = client(envelope(value), envelope(probe_result()), envelope(blob_result()))
                result = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])[1]
                self.assertEqual(result['status'], 'ok')
                self.assertEqual(result['metadata']['path'], prefix + '/ReadMe.md' if prefix else 'README.md')

    def test_head_directory_must_match_the_pinned_root_tree(self):
        value = repository()
        value['defaultBranchRef']['target']['tree']['entries'].append(
            entry('.github', type='tree', mode=0o040000, oid=DIRECTORY_TREE))
        value['githubDirectory'] = tree([entry()], 'd' * 40)
        instance, opener, _ = client(envelope(value))
        result = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])[1]
        self.assertEqual(result['reason'], 'readme-directory-commit-race')
        self.assertEqual(result['status'], 'fallback')
        self.assertEqual(len(opener.requests), 1)

    def test_symlinks_and_submodules_are_not_treated_as_readme_text(self):
        for changes in ({'mode': 0o120000}, {'type': 'commit', 'mode': 0o160000}):
            with self.subTest(changes=changes):
                value = repository()
                value['defaultBranchRef']['target']['tree']['entries'] = [entry(**changes)]
                instance, _, _ = client(envelope(value))
                result = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])[1]
                self.assertEqual(result['status'], 'fallback')
                self.assertEqual(result['reason'], 'unsupported-readme-file')

    def test_unknown_readme_or_empty_repository_goes_to_rest_without_success(self):
        for name in ('README.fr.md', 'not-readme.md'):
            value = repository()
            value['defaultBranchRef']['target']['tree']['entries'] = [entry(name)]
            instance, _, _ = client(envelope(value))
            result = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])[1]
            self.assertEqual((result['status'], result['reason']), ('fallback', 'no-recognized-readme'))
        instance, _, _ = client(envelope(repository(defaultBranchRef=None)))
        self.assertEqual(instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])[1]['status'], 'fallback')

    def test_blob_boundaries_never_yield_success_or_partial_bytes(self):
        changes = [
            ({'isBinary': True}, 'binary-unknown-or-truncated-readme'),
            ({'isBinary': None}, 'binary-unknown-or-truncated-readme'),
            ({'isTruncated': True}, 'binary-unknown-or-truncated-readme'),
            ({'text': None}, 'readme-text-unavailable'),
            ({'text': '\ud800'}, 'invalid-readme-utf8'),
            ({'byteSize': True}, 'readme-byte-size-mismatch'),
            ({'byteSize': len(CONTENT) - 1}, 'readme-byte-size-mismatch'),
            ({'oid': 'f' * 40}, 'readme-blob-identity-mismatch'),
            ({'text': CONTENT.decode('utf-8').replace('Demo', 'Fake')}, 'readme-content-git-sha-mismatch'),
        ]
        for fields, reason in changes:
            with self.subTest(fields=fields):
                instance, _, _ = client(envelope(repository()), envelope(probe_result()), envelope(blob_result(**fields)))
                result = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])[1]
                self.assertEqual((result['status'], result['reason']), ('fallback', reason))
                self.assertIsNone(result['content'])
                self.assertEqual(result['provenance'], {})

    def test_preflight_requires_the_selected_blob_and_measured_text_size(self):
        changes = [
            ({'__typename': 'Tree'}, 'readme-blob-identity-mismatch'),
            ({'oid': 'f' * 40}, 'readme-blob-identity-mismatch'),
            ({'isBinary': True}, 'binary-unknown-or-truncated-readme'),
            ({'isBinary': None}, 'binary-unknown-or-truncated-readme'),
            ({'isTruncated': True}, 'binary-unknown-or-truncated-readme'),
            ({'byteSize': None}, 'readme-byte-size-mismatch'),
            ({'byteSize': True}, 'readme-byte-size-mismatch'),
            ({'byteSize': -1}, 'readme-byte-size-mismatch'),
            ({'byteSize': 0}, 'empty-or-nontext-readme'),
            ({'byteSize': transport.MAX_README_BYTES + 1}, 'readme-exceeds-graphql-byte-budget'),
        ]
        for fields, reason in changes:
            with self.subTest(fields=fields):
                instance, opener, _ = client(envelope(repository()), envelope(probe_result(**fields)))
                result = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])[1]
                self.assertEqual((result['status'], result['reason']), ('fallback', reason))
                self.assertIsNone(result['content'])
                self.assertEqual(result['provenance'], {})
                self.assertEqual(len(opener.requests), 2)
                self.assertNotRegex(json.loads(opener.requests[1][0].data)['query'], r'\btext\b')

    def test_final_bytes_must_match_the_size_observed_in_preflight(self):
        instance, opener, _ = client(envelope(repository()), envelope(probe_result(byteSize=len(CONTENT) + 1)),
                                     envelope(blob_result()))
        result = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])[1]
        self.assertEqual((result['status'], result['reason']), ('fallback', 'readme-byte-size-mismatch'))
        self.assertIsNone(result['content'])
        self.assertEqual(len(opener.requests), 3)

    def test_renamed_public_identity_is_refreshed_before_probe_or_text_fallback(self):
        for phase, fields in (('preflight', {'isBinary': True}),
                              ('preflight', {'byteSize': transport.MAX_README_BYTES + 1}),
                              ('blob', {'byteSize': len(CONTENT) + 1})):
            with self.subTest(phase=phase, fields=fields):
                responses = [envelope(repository())]
                if phase == 'blob':
                    responses.append(envelope(probe_result()))
                result_row = probe_result if phase == 'preflight' else blob_result
                instance, _, _ = client(*responses, envelope(result_row(name='example/renamed', **fields)))
                result = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])[1]
                self.assertEqual(result['status'], 'fallback')
                self.assertEqual(result['repository']['full_name'], 'example/renamed')
                self.assertEqual(result['repository']['name'], 'renamed')
                self.assertEqual(result['repository']['html_url'], 'https://github.com/example/renamed')
                self.assertIsNone(result['content'])

    def test_empty_and_nul_blobs_cannot_be_successful_reads(self):
        for body in (b'', b'a\0b'):
            instance, _, _ = client(envelope(repository(content=body)), envelope(probe_result(content=body)),
                                    envelope(blob_result(content=body)))
            result = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])[1]
            self.assertEqual((result['status'], result['reason']), ('fallback', 'empty-or-nontext-readme'))

    def test_literal_replacement_character_is_kept_when_bytes_and_blob_agree(self):
        body = 'An actual replacement character: \ufffd'.encode()
        instance, _, _ = client(envelope(repository(content=body)), envelope(probe_result(content=body)),
                                envelope(blob_result(content=body)))
        result = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])[1]
        self.assertEqual((result['status'], result['content']), ('ok', body))


class IdentityAndPrivacyTests(unittest.TestCase):
    def test_private_mismatched_and_ineligible_metadata_is_not_exposed(self):
        for fields in ({'isPrivate': True}, {'isPrivate': None}, {'databaseId': 2}, {'databaseId': True},
                       {'isFork': True}, {'isArchived': True}, {'isFork': None}):
            with self.subTest(fields=fields):
                value = repository(name='private/secret-name', description='SECRET', **fields)
                instance, opener, _ = client(envelope(value))
                result = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])[1]
                self.assertEqual(result['status'], 'rejected')
                self.assertIsNone(result['repository'])
                self.assertNotIn('SECRET', json.dumps(result))
                self.assertNotIn('secret-name', json.dumps(result))
                self.assertEqual(len(opener.requests), 1)

    def test_both_probe_and_text_queries_recheck_public_flags_and_numeric_id(self):
        for fields in ({'isPrivate': True}, {'databaseId': 999}, {'isFork': True}, {'isArchived': True}):
            for phase in ('preflight', 'blob'):
                with self.subTest(fields=fields, phase=phase):
                    value = probe_result() if phase == 'preflight' else blob_result()
                    value.update(fields, nameWithOwner='private/secret-name')
                    responses = [envelope(repository())]
                    if phase == 'blob':
                        responses.append(envelope(probe_result()))
                    instance, opener, _ = client(*responses, envelope(value))
                    result = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])[1]
                    self.assertEqual(result['status'], 'rejected')
                    self.assertIsNone(result['repository'])
                    self.assertIsNone(result['content'])
                    self.assertNotIn('secret-name', json.dumps(result))
                    self.assertEqual(len(opener.requests), 2 if phase == 'preflight' else 3)

    def test_invalid_repository_metadata_is_retry_without_copied_fields(self):
        for fields in ({'url': 'https://evil.invalid/example/demo'}, {'stargazerCount': True},
                       {'description': {'unexpected': 'object'}}, {'updatedAt': 'yesterday'},
                       {'repositoryTopics': {'nodes': [], 'pageInfo': {'hasNextPage': True}}}):
            instance, _, _ = client(envelope(repository(**fields)))
            result = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])[1]
            self.assertEqual(result['status'], 'retry')
            self.assertIsNone(result['repository'])

    def test_one_top_level_not_found_does_not_poison_other_ids(self):
        response = envelope(None, repository(2, 'o/two'), errors=[
            {'type': 'NOT_FOUND', 'path': ['r0'], 'message': 'Repository unavailable'}])
        instance, opener, _ = client(response, envelope(probe_result(2, 'o/two')), envelope(blob_result(2, 'o/two')))
        result = instance.fetch_batch([{'id': 1, 'full_name': 'o/one'}, {'id': 2, 'full_name': 'o/two'}])
        self.assertEqual(result[1]['status'], 'rejected')
        self.assertEqual(result[2]['status'], 'ok')
        self.assertEqual(json.loads(opener.requests[1][0].data)['variables']['node0'], 'Repository-2')

    def test_redirects_are_all_refused_even_on_api_origin(self):
        request = Request(transport.GRAPHQL_URL, headers={'Authorization': 'Bearer ' + TOKEN})
        for url in ('https://evil.invalid/graphql', 'http://api.github.com/graphql',
                    'https://api.github.com/graphql?redirect=1', 'https://api.github.com@evil.invalid/'):
            self.assertIsNone(transport.NoRedirect().redirect_request(request, None, 302, 'redirect', {}, url))

    def test_invalid_inputs_and_oversized_batches_never_send_requests(self):
        bad = [[{'id': True, 'full_name': 'o/r'}], [{'id': 0, 'full_name': 'o/r'}],
               [{'id': 1, 'full_name': 'o/r', 'node_id': 'unsafe\nquery'}],
               [{'id': 1, 'full_name': 'o/r\nquery'}], [{'id': 1, 'full_name': 'o/../r'}],
               [{'id': 1, 'full_name': 'o/r'}, {'id': 1, 'full_name': 'o/s'}],
               [{'id': number + 1, 'full_name': 'o/r'} for number in range(9)]]
        for value in bad:
            instance, opener, _ = client()
            with self.assertRaises(ValueError):
                instance.fetch_batch(value)
            self.assertEqual(opener.requests, [])
        instance, opener, _ = client()
        self.assertEqual(instance.fetch_batch([]), {})
        self.assertEqual(opener.requests, [])


class RateAndBudgetTests(unittest.TestCase):
    def test_constructor_caps_batch_rate_and_timeout(self):
        for kwargs in ({'batch_size': 17}, {'batch_size': True}, {'interval': .5},
                       {'interval': float('nan')}, {'interval': float('inf')},
                       {'timeout': 61}, {'timeout': 0}):
            with self.assertRaises(ValueError):
                transport.GraphQLReadmeTransport(TOKEN, **kwargs)
        for token in ('', 'line\nbreak'):
            with self.assertRaises(ValueError):
                transport.GraphQLReadmeTransport(token)

    def test_primary_limit_after_metadata_defers_without_blob_or_rest_fallback(self):
        value = repository()
        value['defaultBranchRef']['target']['tree']['entries'].append(entry('README.rst'))
        response = Response(envelope(value, remaining=0), headers={
            'X-RateLimit-Remaining': '0', 'X-RateLimit-Reset': '1792324800'})
        instance, opener, clock = client(response)
        result = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])[1]
        self.assertEqual(result['status'], 'deferred')
        self.assertGreaterEqual(result['retry_after'], 3600)
        second = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])[1]
        self.assertEqual(second['status'], 'deferred')
        self.assertEqual(len(opener.requests), 1)
        self.assertEqual(clock.sleeps, [])

    def test_last_allowed_blob_is_success_but_next_batch_waits(self):
        instance, opener, _ = client(envelope(repository()), envelope(probe_result()), envelope(blob_result(), remaining=0))
        self.assertEqual(instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])[1]['status'], 'ok')
        self.assertEqual(instance.fetch_batch([{'id': 2, 'full_name': 'o/two'}])[2]['status'], 'deferred')
        self.assertEqual(len(opener.requests), 3)

    def test_zero_remaining_after_preflight_defers_text_and_sibling_rest_fallback(self):
        ambiguous = repository()
        ambiguous['defaultBranchRef']['target']['tree']['entries'].append(entry('README.rst'))
        instance, opener, _ = client(envelope(ambiguous, repository(2, 'o/two')),
                                     envelope(probe_result(2, 'o/two'), remaining=0))
        results = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}, {'id': 2, 'full_name': 'o/two'}])
        self.assertEqual({row['status'] for row in results.values()}, {'deferred'})
        self.assertEqual({row['reason'] for row in results.values()}, {'graphql-rate-limit'})
        self.assertTrue(all(row['content'] is None and row['retry_after'] >= 3600 for row in results.values()))
        self.assertEqual(len(opener.requests), 2)
        self.assertEqual([row['phase'] for row in instance.last_batch_receipts], ['metadata', 'preflight'])
        self.assertEqual(instance.fetch_batch([{'id': 2, 'full_name': 'o/two'}])[2]['status'], 'deferred')
        self.assertEqual(len(opener.requests), 2)

    def test_secondary_graphql_error_honors_retry_after_and_never_retries_automatically(self):
        response = Response(envelope(repository(), errors=[{'type': 'RATE_LIMITED', 'message': TOKEN}]),
                            headers={'Retry-After': '120'})
        instance, opener, clock = client(response)
        result = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])[1]
        self.assertEqual((result['status'], result['reason'], result['retry_after']),
                         ('deferred', 'graphql-rate-limit', 120))
        self.assertEqual(len(opener.requests), 1)
        self.assertEqual(clock.sleeps, [])
        self.assertNotIn(TOKEN, json.dumps(result) + json.dumps(instance.last_batch_receipts))

    def test_secondary_http_error_without_retry_header_waits_at_least_one_minute(self):
        body = io.BytesIO(b'{"message":"You have exceeded a secondary rate limit"}')
        error = HTTPError(transport.GRAPHQL_URL, 403, 'forbidden', {}, body)
        instance, _, _ = client(error)
        result = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])[1]
        self.assertEqual(result['status'], 'deferred')
        self.assertGreaterEqual(result['retry_after'], 60)
        self.assertTrue(body.closed)

    def test_network_server_and_query_errors_never_switch_to_rest(self):
        errors = [URLError('SECRET NETWORK DETAIL'), TimeoutError('SECRET'), IncompleteRead(b'SECRET'),
                  HTTPError(transport.GRAPHQL_URL, 502, 'SECRET', {}, io.BytesIO(b'SECRET')),
                  Response(envelope(repository(), errors=[{'type': 'INTERNAL', 'message': 'SECRET'}]))]
        for response in errors:
            with self.subTest(response=type(response).__name__):
                instance, opener, _ = client(response)
                result = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])[1]
                self.assertEqual(result['status'], 'retry')
                self.assertEqual(len(opener.requests), 1)
                self.assertNotIn('SECRET', json.dumps(result) + json.dumps(instance.last_batch_receipts))

    def test_failure_in_blob_phase_is_pending_with_verified_fresh_metadata(self):
        instance, _, _ = client(envelope(repository()), envelope(probe_result()), URLError('failed after probe'))
        result = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])[1]
        self.assertEqual(result['status'], 'retry')
        self.assertEqual(result['repository']['id'], 1)
        self.assertIsNone(result['content'])

    def test_probe_and_text_backpressure_suppress_earlier_sibling_rest_fallback(self):
        ambiguous = repository()
        ambiguous['defaultBranchRef']['target']['tree']['entries'].append(entry('README.rst'))
        for phase in ('preflight', 'blob'):
            failures = [URLError('SECRET temporary outage'), TimeoutError('SECRET timeout'),
                        Response(b'SECRET overloaded', status=503),
                        Response(envelope(None, errors=[{'type': 'RATE_LIMITED', 'message': 'SECRET rate limited'}])),
                        HTTPError(transport.GRAPHQL_URL, 429, 'slow down', {'Retry-After': '61'}, io.BytesIO())]
            for failure in failures:
                with self.subTest(phase=phase, failure=type(failure).__name__):
                    responses = [envelope(ambiguous, repository(2, 'o/two'))]
                    if phase == 'blob':
                        responses.append(envelope(probe_result(2, 'o/two')))
                    instance, opener, _ = client(*responses, failure)
                    results = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}, {'id': 2, 'full_name': 'o/two'}])
                    self.assertIn(results[2]['status'], ('retry', 'deferred'))
                    self.assertEqual(results[1]['status'], results[2]['status'])
                    self.assertEqual(results[1]['reason'], results[2]['reason'])
                    self.assertTrue(all(row['content'] is None for row in results.values()))
                    self.assertEqual(len(opener.requests), 2 if phase == 'preflight' else 3)
                    self.assertNotIn('SECRET', json.dumps(results) + json.dumps(instance.last_batch_receipts))

    def test_last_allowed_blob_keeps_success_and_suppresses_sibling_rest_fallback(self):
        ambiguous = repository()
        ambiguous['defaultBranchRef']['target']['tree']['entries'].append(entry('README.rst'))
        instance, _, _ = client(envelope(ambiguous, repository(2, 'o/two')),
                                envelope(probe_result(2, 'o/two')),
                                envelope(blob_result(2, 'o/two'), remaining=0))
        result = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}, {'id': 2, 'full_name': 'o/two'}])
        self.assertEqual(result[1]['status'], 'deferred')
        self.assertEqual(result[2]['status'], 'ok')

    def test_oversized_and_malformed_responses_are_bounded_and_closed(self):
        bodies = [b' ' * (transport.MAX_RESPONSE_BYTES + 10), b'{"data":{},"data":{}}',
                  b'{"data":NaN}', b'\xff', b'{"data":null}', b'{"data":{', b'[]']
        for body in bodies:
            response = Response(body)
            instance, _, _ = client(response)
            result = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])[1]
            self.assertEqual(result['status'], 'retry')
            self.assertTrue(response.closed)
            self.assertEqual(response.read_sizes, [transport.MAX_RESPONSE_BYTES + 1])

    def test_aggregate_byte_budget_splits_blob_queries_sequentially(self):
        body = b'x' * 2000
        instance, opener, clock = client(envelope(repository(1, 'o/one', body), repository(2, 'o/two', body)),
                                         envelope(probe_result(1, 'o/one', body), probe_result(2, 'o/two', body)),
                                         envelope(blob_result(1, 'o/one', body)), envelope(blob_result(2, 'o/two', body)))
        with patch.object(transport, 'TEXT_RESPONSE_BUDGET', 20000):
            result = instance.fetch_batch([{'id': 1, 'full_name': 'o/one'}, {'id': 2, 'full_name': 'o/two'}])
        self.assertTrue(all(row['status'] == 'ok' for row in result.values()))
        self.assertEqual(len(opener.requests), 4)
        self.assertEqual(clock.sleeps, [1.0, 1.0, 1.0])
        self.assertEqual([row['repository_count'] for row in instance.last_batch_receipts], [2, 2, 1, 1])

    def test_backpressure_stops_remaining_byte_budget_groups(self):
        body = b'x' * 2000
        instance, opener, _ = client(envelope(repository(1, 'o/one', body), repository(2, 'o/two', body)),
                                     envelope(probe_result(1, 'o/one', body), probe_result(2, 'o/two', body)),
                                     URLError('outage'))
        with patch.object(transport, 'TEXT_RESPONSE_BUDGET', 20000):
            result = instance.fetch_batch([{'id': 1, 'full_name': 'o/one'}, {'id': 2, 'full_name': 'o/two'}])
        self.assertEqual({row['status'] for row in result.values()}, {'retry'})
        self.assertEqual(len(opener.requests), 3)

    def test_successful_text_group_survives_later_group_backpressure(self):
        body = b'x' * 2000
        ambiguous = repository(3, 'o/three')
        ambiguous['defaultBranchRef']['target']['tree']['entries'].append(entry('README.rst'))
        instance, opener, _ = client(envelope(repository(1, 'o/one', body), repository(2, 'o/two', body), ambiguous),
                                     envelope(probe_result(1, 'o/one', body), probe_result(2, 'o/two', body)),
                                     envelope(blob_result(1, 'o/one', body)), TimeoutError('SECRET timeout'))
        with patch.object(transport, 'TEXT_RESPONSE_BUDGET', 20000):
            result = instance.fetch_batch([{'id': 1, 'full_name': 'o/one'}, {'id': 2, 'full_name': 'o/two'},
                                           {'id': 3, 'full_name': 'o/three'}])
        self.assertEqual(result[1]['status'], 'ok')
        self.assertEqual(result[1]['content'], body)
        self.assertEqual((result[2]['status'], result[3]['status']), ('retry', 'retry'))
        self.assertEqual(len(opener.requests), 4)
        self.assertNotIn('SECRET', json.dumps(instance.last_batch_receipts))

    def test_large_single_blob_and_tree_go_to_rest_before_text_query(self):
        value = repository()
        instance, opener, _ = client(envelope(value), envelope(probe_result(byteSize=transport.MAX_README_BYTES)))
        result = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])[1]
        self.assertEqual((result['status'], result['reason']), ('fallback', 'readme-exceeds-graphql-byte-budget'))
        self.assertEqual(len(opener.requests), 2)
        value = repository()
        value['defaultBranchRef']['target']['tree']['entries'] = [entry(str(i)) for i in range(4)]
        instance, _, _ = client(envelope(value))
        with patch.object(transport, 'MAX_TREE_ENTRIES', 3):
            result = instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])[1]
        self.assertEqual((result['status'], result['reason']), ('fallback', 'invalid-or-large-readme-tree'))

    def test_every_request_in_successive_batches_is_throttled(self):
        instance, opener, clock = client(envelope(repository()), envelope(probe_result()), envelope(blob_result()),
                                         envelope(repository()), envelope(probe_result()), envelope(blob_result()))
        instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])
        instance.fetch_batch([{'id': 1, 'full_name': 'example/demo'}])
        self.assertEqual(len(opener.requests), 6)
        self.assertEqual(clock.sleeps, [1.0] * 5)


if __name__ == '__main__':
    unittest.main()
