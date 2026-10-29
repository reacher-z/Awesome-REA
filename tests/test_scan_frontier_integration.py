"""Resume boundaries keep backoff, pending identities and README provenance honest."""
import contextlib
import hashlib
from copy import deepcopy
import io
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import scan_sources as scanner
import search_frontier as frontier
from validate import validate_source_index

BASE = 'topic:reverse-engineering'
QUERY = BASE + ' is:public fork:false archived:false'
OBSERVED = '2026-10-18T12:00:00Z'


def arguments(output, *, target=1):
    return SimpleNamespace(target=target, workers=1, requests_per_second=1,
                           max_pages=1, candidate_buffer=0, seed_curated=False,
                           seed_papers=False, queries=[], output=output)


def public_repository(identifier):
    name = f'example/project-{identifier}'
    return {'id': identifier, 'node_id': f'R_public_{identifier}', 'full_name': name,
            'html_url': 'https://github.com/' + name, 'private': False,
            'fork': False, 'archived': False, 'created_at': '2026-10-01T00:00:00Z'}


class NoRequests:
    def json(self, *args, **kwargs):
        raise AssertionError('No REST or search request expected')


class FrontierRetryTests(unittest.TestCase):
    def test_hour_backoff_survives_reload_for_deferred_and_suppressed_fallback(self):
        state = frontier.new_frontier(until='2026-10-18T00:00:00Z', approved_queries=[BASE])
        request = frontier.next_request(state)
        frontier.record_response(state, request,
            {'items': [public_repository(41), public_repository(42)],
             'total_count': 2, 'incomplete_results': False},
            observed_at='2026-10-18T01:00:00Z', run_id='2026-10-18T01:00:00Z')

        class MixedTransport:
            batch_size = 8

            def fetch_batch(self, rows):
                # The persisted node identity must reach the rename-safe transport.
                assert {r['node_id'] for r in rows} == {'R_public_41', 'R_public_42'}
                return {41: {'status': 'fallback'},
                        42: {'status': 'deferred', 'reason': 'graphql-rate-limit', 'retry_after': 3600}}

        cache = ROOT / '.cache'
        cache.mkdir(exist_ok=True)
        instant = frontier.utc_seconds(OBSERVED)
        with TemporaryDirectory(dir=cache) as temporary:
            output, state_path = Path(temporary) / 'scan.json', Path(temporary) / 'frontier.json'
            with contextlib.redirect_stdout(io.StringIO()), patch.object(frontier, 'current_seconds', return_value=instant):
                code = scanner.run_scan(NoRequests(), arguments(output, target=2),
                                        readme_transport=MixedTransport(),
                                        frontier=(state, state_path, [BASE]))
                restored = frontier.load_frontier(state_path, approved_queries=[BASE])
            document = json.loads(output.read_text(encoding='utf-8'))
        self.assertEqual(code, 1)
        self.assertEqual(document['resources'], [])
        self.assertEqual(document['failures'], [])
        self.assertEqual(document['meta']['status'], 'in-progress')
        self.assertEqual(document['meta']['attempted_readme_scans'], 0)
        self.assertEqual(document['meta']['unattempted_candidates'], 2)
        for candidate in restored['candidates'].values():
            self.assertEqual(candidate['next_attempt_at'] - candidate['last_attempt_at'], 3600)
            self.assertEqual(candidate['attempts'], 1)
            self.assertIsNone(candidate['checkpoint_sha256'])
        self.assertEqual(frontier.pending_candidates(restored, now=instant + 3599), [])
        self.assertEqual({r['id'] for r in frontier.pending_candidates(restored, now=instant + 3600)}, {41, 42})


class PathBoundaryTests(unittest.TestCase):
    def test_cli_rejects_resolved_path_collisions_before_authentication_or_writes(self):
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            shared, other = directory / 'shared.json', directory / 'other.json'
            shared.write_bytes(b'preserve this input')
            alias = directory / 'subdir' / '..' / shared.name
            cases = [
                ['--frontier', str(shared), '--output', str(alias)],
                ['--frontier', str(alias), '--resume', str(shared), '--output', str(other)],
            ]
            for flags in cases:
                with self.subTest(flags=flags), patch.object(sys, 'argv', ['scan_sources.py', '--transport', 'graphql', *flags]), \
                        patch.object(scanner.subprocess, 'run') as authentication, \
                        patch.object(scanner, 'load_resume') as load, contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as raised:
                        scanner.main()
                    self.assertEqual(raised.exception.code, 2)
                    authentication.assert_not_called()
                    load.assert_not_called()
                    self.assertEqual(shared.read_bytes(), b'preserve this input')
                    self.assertFalse(other.exists())

    def test_direct_scanner_rejects_frontier_output_collision_before_checkpoint_write(self):
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / 'same.json'
            path.write_bytes(b'preserve frontier')
            state = frontier.new_frontier(until='2026-10-18T00:00:00Z', approved_queries=[BASE])
            with self.assertRaisesRegex(ValueError, 'different paths'):
                scanner.run_scan(NoRequests(), arguments(path), readme_transport=object(),
                                 frontier=(state, path, [BASE]))
            self.assertEqual(path.read_bytes(), b'preserve frontier')


class LegacyPendingTests(unittest.TestCase):
    def test_default_200_lookup_budget_rotates_past_unavailable_ids_on_next_run(self):
        identifiers = [f'scan-{i}' for i in range(1, 406)]
        original = {'meta': {'schema_version': 1, 'status': 'complete', 'queries': [],
                            'successful_readme_scans': 0, 'failed': 0, 'attempted_readme_scans': 0,
                            'unique_repos': len(identifiers), 'unattempted_candidates': len(identifiers),
                            'requested_successful_scans': 0, 'discovered_repository_ids': identifiers},
                    'resources': [], 'failures': []}

        class UnavailableIDs:
            def __init__(self):
                self.lookups = []

            def json(self, path, search=False):
                assert not search and path.startswith('/repositories/')
                self.lookups.append(int(path.rsplit('/', 1)[-1]))
                raise scanner.ScanError('http-404', 404)

        documents, attempts = [], []
        resumed = original
        with TemporaryDirectory() as temporary:
            for index, timestamp in enumerate(('2026-10-18T12:00:00Z', '2026-10-18T12:01:00Z')):
                api = UnavailableIDs()
                path = Path(temporary) / f'run-{index}.json'
                with contextlib.redirect_stdout(io.StringIO()), patch.object(scanner, 'now', return_value=timestamp):
                    self.assertEqual(scanner.run_scan(api, arguments(path), resumed, 'a' * 64), 1)
                resumed = json.loads(path.read_text(encoding='utf-8'))
                documents.append(resumed)
                attempts.append(api.lookups)
        self.assertEqual(attempts[0], list(range(1, 201)))
        self.assertEqual(attempts[1], list(range(201, 401)))
        for document in documents:
            self.assertEqual(document['meta']['current_run']['resume_observation_count'], 200)
            self.assertEqual(document['meta']['unattempted_candidates'], 405)
            self.assertEqual(document['meta']['attempted_readme_scans'], 0)
            self.assertEqual(document['meta']['discovered_repository_ids'], identifiers)
            self.assertEqual(document['resources'], [])
            self.assertEqual(document['failures'], [])
        self.assertNotIn('resume_observations', original['meta'])


class GraphQLRecordValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads((ROOT / 'data/source-index.json').read_text(encoding='utf-8'))
        cls.record_index = 0
        row = cls.document['resources'][cls.record_index]
        row.pop('readme_api_url', None)
        row.pop('readme_integrity_review', None)
        # Synthetic, internally consistent blob evidence for validator behavior.
        body = b'# Synthetic README fixture\n'
        oid = hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()
        row.update(readme_path='README.md', readme_git_sha=oid, readme_content_git_sha=oid,
                   readme_git_sha_matches_content=True, readme_sha256=hashlib.sha256(body).hexdigest(),
                   readme_bytes=len(body), readme_lines=1, readme_heading_count=1)
        row.update(readme_transport='github-graphql-blob',
                   readme_graphql_endpoint='https://api.github.com/graphql', readme_commit_sha='a' * 40)
        row['readme_url'] = row['url'] + '/blob/' + row['readme_commit_sha'] + '/' + quote(row['readme_path'], safe='/')

    def test_matching_graphql_evidence_is_valid_without_a_rest_request_claim(self):
        errors = []
        validate_source_index(self.document, errors)
        self.assertEqual(errors, [])

    def test_fabricated_rest_url_and_unbound_commit_are_rejected(self):
        changes = {
            'fabricated REST read': lambda row: row.update(readme_api_url='https://api.github.com/repos/' + row['full_name'] + '/readme'),
            'different commit in metadata': lambda row: row.update(readme_commit_sha='b' * 40),
            'mutable branch URL': lambda row: row.update(readme_url=row['url'] + '/blob/main/' + row['readme_path']),
            'different GraphQL endpoint': lambda row: row.update(readme_graphql_endpoint='https://api.github.com/other'),
        }
        for label, mutate in changes.items():
            with self.subTest(case=label):
                document = deepcopy(self.document)
                mutate(document['resources'][self.record_index])
                errors = []
                validate_source_index(document, errors)
                self.assertTrue(any('GraphQL README evidence' in error for error in errors), errors)


class FreshFrontierQueryTests(unittest.TestCase):
    def test_new_search_preserves_microsecond_run_identity(self):
        run_id = '2026-10-18T12:00:00.123456Z'
        state = frontier.new_frontier(until='2026-10-18T00:00:00Z', approved_queries=[BASE])
        body = b'# Synthetic README from a newly discovered repository\n'
        blob = hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()

        class OneSearch:
            def __init__(self):
                self.calls = []

            def json(self, path, search=False):
                assert search and path.startswith('/search/repositories?')
                self.calls.append(path)
                return {'items': [public_repository(42)], 'total_count': 1, 'incomplete_results': False}

        class VerifiedTransport:
            batch_size = 8

            def fetch_batch(self, rows):
                return {row['id']: {'status': 'ok', 'repository': dict(row), 'content': body,
                    'metadata': {'path': 'README.md', 'sha': blob, 'size': len(body), 'commit_oid': 'a' * 40,
                                 'html_url': row['html_url'] + '/blob/' + 'a' * 40 + '/README.md'}}
                        for row in rows}

        api = OneSearch()
        cache = ROOT / '.cache'
        cache.mkdir(exist_ok=True)
        with TemporaryDirectory(dir=cache) as temporary:
            output, state_path = Path(temporary) / 'scan.json', Path(temporary) / 'frontier.json'
            with contextlib.redirect_stdout(io.StringIO()), patch.object(scanner, 'now', return_value=run_id):
                code = scanner.run_scan(api, arguments(output), readme_transport=VerifiedTransport(),
                                        frontier=(state, state_path, [BASE]))
            document = json.loads(output.read_text(encoding='utf-8'))
            restored = frontier.load_frontier(state_path, approved_queries=[BASE])
        self.assertEqual((code, len(api.calls)), (0, 1))
        self.assertEqual(document['meta']['current_run']['run_id'], run_id)
        self.assertEqual(document['meta']['current_run']['query_count'], 1)
        self.assertEqual(document['meta']['queries'][0]['run_id'], run_id)
        self.assertEqual(restored['observations'][0]['run_id'], run_id)
        self.assertEqual(document['meta']['successful_readme_scans'], 1)
        self.assertEqual(document['resources'][0]['readme_sha256'], hashlib.sha256(body).hexdigest())


if __name__ == '__main__':
    unittest.main()
