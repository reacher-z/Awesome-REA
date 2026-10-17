"""The availability recheck keys on repository IDs, reports outcomes separately and never rewrites scan evidence."""
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import source_availability
from scan_sources import ScanError
from source_availability import check_record, main, run_recheck

TOKEN = 'unit-test-token-sentinel'


def repo(identifier, full_name, **changes):
    return {'id': identifier, 'full_name': full_name, 'html_url': 'https://github.com/' + full_name,
            'private': False, 'fork': False, 'archived': False, **changes}


def scan(identifier, full_name):
    return {'id': f'scan-{identifier}', 'full_name': full_name, 'url': 'https://github.com/' + full_name,
            'scan_status': 'readme-scanned', 'readme_sha256': 'a' * 64, 'observed_at': '2026-10-16T01:35:25Z'}


class FakeAPI:
    """Answer metadata paths from a table; anything else, including README endpoints, fails the test."""
    def __init__(self, responses, remaining=None):
        self.responses, self.paths = responses, []
        self.rate = {} if remaining is None else {'core': {'remaining': remaining, 'limit': 5000, 'reset': 0}}

    def json(self, path):
        self.paths.append(path)
        if path not in self.responses:
            raise AssertionError('unexpected request ' + path)
        response = self.responses[path]
        if isinstance(response, ScanError):
            raise response
        if 'core' in self.rate:
            self.rate['core']['remaining'] -= 1
        return copy.deepcopy(response)


def gone(status):
    return ScanError('http-' + str(status), status)


def arguments(**changes):
    return SimpleNamespace(**{'offset': 0, 'limit': 100, 'requests_per_second': 5, 'reserve': 0,
                              'max_consecutive_inconclusive': 10, 'source_label': 'data/source-index.json', **changes})


def document(*records):
    return {'meta': {'completed_at': '2026-10-16T11:55:19Z'}, 'resources': list(records), 'failures': []}


class OutcomeTests(unittest.TestCase):
    def check(self, record, responses):
        api = FakeAPI(responses)
        entry = check_record(api, record)
        self.assertFalse(any('readme' in path for path in api.paths))
        return entry, api.paths

    def test_same_id_and_name_is_available_with_one_request(self):
        entry, paths = self.check(scan(7, 'owner/tool'), {'/repositories/7': repo(7, 'owner/tool')})
        self.assertEqual(entry['outcome'], 'available')
        self.assertEqual(paths, ['/repositories/7'])

    def test_renames_and_transfers_follow_the_id_and_check_the_old_name(self):
        entry, paths = self.check(scan(835681776, 'IIIImmmyyy/UnityReverseEngine'), {
            '/repositories/835681776': repo(835681776, 'IIIImmmyyy/UREngine'),
            '/repos/IIIImmmyyy/UnityReverseEngine': repo(835681776, 'IIIImmmyyy/UREngine')})
        self.assertEqual((entry['outcome'], entry['current_full_name'], entry['recorded_name_status']),
                         ('renamed', 'IIIImmmyyy/UREngine', 'redirects-to-scanned-id'))
        self.assertEqual(paths, ['/repositories/835681776', '/repos/IIIImmmyyy/UnityReverseEngine'])
        entry, _ = self.check(scan(8, 'old-owner/tool'), {
            '/repositories/8': repo(8, 'new-owner/tool'), '/repos/old-owner/tool': gone(404)})
        self.assertEqual((entry['outcome'], entry['recorded_name_status']), ('transferred', 'not-found'))
        # An owner login that differs only in case is the same account.
        entry, _ = self.check(scan(9, 'Owner/tool'), {
            '/repositories/9': repo(9, 'owner/Tool'), '/repos/Owner/tool': repo(9, 'owner/Tool')})
        self.assertEqual(entry['outcome'], 'renamed')

    def test_a_recorded_name_now_owned_by_another_id_is_reassigned_not_available(self):
        entry, _ = self.check(scan(1238268014, 'Shellghostt/De-Caffeinator'), {
            '/repositories/1238268014': gone(404),
            '/repos/Shellghostt/De-Caffeinator': repo(1244345068, 'Shellghostt/De-Caffeinator')})
        self.assertEqual(entry['outcome'], 'name-reassigned')
        self.assertEqual((entry['http_status'], entry['recorded_name_repository_id']), (404, 'scan-1244345068'))
        # A renamed repository keeps its outcome but reports that its old name now belongs to someone else.
        entry, _ = self.check(scan(10, 'owner/tool'), {
            '/repositories/10': repo(10, 'owner/tool-v2'), '/repos/owner/tool': repo(11, 'owner/tool')})
        self.assertEqual((entry['outcome'], entry['recorded_name_repository_id']), ('renamed', 'scan-11'))

    def test_missing_and_blocked_ids_are_distinguished(self):
        entry, _ = self.check(scan(1377172300, 'newliver666/apk-reverse'), {
            '/repositories/1377172300': gone(404), '/repos/newliver666/apk-reverse': gone(404)})
        self.assertEqual((entry['outcome'], entry['recorded_name_status'], entry['recorded_name_http_status']),
                         ('not-found', 'not-found', 404))
        entry, _ = self.check(scan(12, 'owner/tool'), {'/repositories/12': gone(451), '/repos/owner/tool': gone(451)})
        self.assertEqual((entry['outcome'], entry['http_status'], entry['recorded_name_status'], entry['recorded_name_http_status']),
                         ('blocked', 451, 'inconclusive', 451))

    def test_archived_and_fork_repositories_are_ineligible(self):
        entry, _ = self.check(scan(13, 'owner/tool'), {'/repositories/13': repo(13, 'owner/tool', archived=True)})
        self.assertEqual((entry['outcome'], entry['reason']), ('ineligible', 'archived'))
        entry, _ = self.check(scan(14, 'owner/tool'), {
            '/repositories/14': repo(14, 'other/tool', fork=True), '/repos/owner/tool': gone(404)})
        self.assertEqual((entry['outcome'], entry['reason'], entry['current_full_name']), ('ineligible', 'fork', 'other/tool'))

    def test_private_responses_expose_no_metadata(self):
        hidden = repo(15, 'secret/name', private=True, description='private text')
        entry, paths = self.check(scan(15, 'owner/tool'), {'/repositories/15': hidden})
        self.assertEqual(set(entry), {'id', 'recorded_full_name', 'observed_at', 'outcome', 'reason'})
        self.assertEqual((entry['outcome'], entry['reason']), ('ineligible', 'private'))
        self.assertEqual(paths, ['/repositories/15'])
        unconfirmed = repo(16, 'secret/name')
        del unconfirmed['private']
        entry, _ = self.check(scan(16, 'owner/tool'), {'/repositories/16': unconfirmed})
        self.assertEqual(entry['reason'], 'public-status-unconfirmed')
        entry, _ = self.check(scan(17, 'owner/tool'), {
            '/repositories/17': gone(404), '/repos/owner/tool': repo(99, 'secret/name', private=True)})
        self.assertEqual((entry['outcome'], entry['recorded_name_status']), ('not-found', 'private'))
        self.assertNotIn('secret', json.dumps(entry))
        self.assertNotIn('99', json.dumps({key: value for key, value in entry.items() if key != 'observed_at'}))

    def test_rate_limits_server_and_network_failures_are_inconclusive_never_not_found(self):
        for error in (ScanError('http-403', 403), ScanError('http-429', 429), ScanError('http-503', 503),
                      ScanError('network-failure'), ScanError('invalid-api-json'), ScanError('http-401', 401)):
            with self.subTest(reason=error.reason):
                entry, paths = self.check(scan(18, 'owner/tool'), {'/repositories/18': error})
                self.assertEqual((entry['outcome'], entry['reason']), ('inconclusive', error.reason))
                self.assertEqual(paths, ['/repositories/18'])
        for response in ([], repo(19, 'owner/tool'), repo(18, 'owner/tool', html_url='https://example.com/owner/tool')):
            with self.subTest(response=response):
                entry, _ = self.check(scan(18, 'owner/tool'), {'/repositories/18': response})
                self.assertEqual(entry['outcome'], 'inconclusive')


class RunTests(unittest.TestCase):
    def setUp(self):
        self.records = [scan(30, 'owner/c'), scan(10, 'owner/a'), scan(20, 'owner/b')]
        self.responses = {f'/repositories/{n}': repo(n, f'owner/{name}') for n, name in ((10, 'a'), (20, 'b'), (30, 'c'))}

    def test_runs_are_bounded_in_id_order_and_leave_the_snapshot_unchanged(self):
        source = document(*self.records)
        before = copy.deepcopy(source)
        with contextlib.redirect_stdout(io.StringIO()):
            report = run_recheck(FakeAPI(self.responses), source, 'f' * 64, arguments(offset=1, limit=1))
        self.assertEqual(source, before)
        self.assertEqual([entry['id'] for entry in report['results']], ['scan-20'])
        self.assertEqual((report['complete'], report['next_offset'], report['metadata_requests']), (True, 2, 1))
        self.assertEqual(report['counts']['available'], 1)
        self.assertEqual(report['source'], {'path': 'data/source-index.json', 'sha256': 'f' * 64,
                                            'completed_at': '2026-10-16T11:55:19Z', 'successful_readme_scans': 3})

    def test_the_core_quota_reserve_stops_a_run_before_it_is_spent(self):
        api = FakeAPI(self.responses, remaining=1003)
        with contextlib.redirect_stdout(io.StringIO()):
            report = run_recheck(api, document(*self.records), 'f' * 64, arguments(reserve=1000))
        self.assertEqual(len(report['results']), 2)
        self.assertEqual((report['complete'], report['stopped_reason'], report['next_offset']),
                         (False, 'core-rate-limit-reserve', 2))

    def test_repeated_inconclusive_results_stop_the_run(self):
        responses = {path: ScanError('network-failure') for path in self.responses}
        with contextlib.redirect_stdout(io.StringIO()):
            report = run_recheck(FakeAPI(responses), document(*self.records), 'f' * 64,
                                 arguments(max_consecutive_inconclusive=2))
        self.assertEqual((report['counts']['inconclusive'], report['counts']['not-found']), (2, 0))
        self.assertEqual((report['stopped_reason'], report['next_offset']), ('consecutive-inconclusive-results', 2))


class CommandTests(unittest.TestCase):
    def run_main(self, argv, environment, api=None):
        output = io.StringIO()
        blocked = AssertionError('network access in a unit test')
        with patch.dict(os.environ, environment, clear=True), contextlib.redirect_stdout(output), \
                patch.object(socket.socket, 'connect', side_effect=blocked), \
                patch.object(socket, 'getaddrinfo', side_effect=blocked), \
                patch.object(source_availability, 'GitHub', lambda token, rate: api):
            status = main(argv)
        return status, output.getvalue()

    def test_command_needs_a_token_and_writes_a_dated_report_beside_unchanged_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source-index.json'
            meta = {'completed_at': '2026-10-16T11:55:19Z', 'queries': [], 'successful_readme_scans': 2,
                    'failed': 0, 'attempted_readme_scans': 2, 'unique_repos': 2, 'unattempted_candidates': 0}
            source.write_text(json.dumps({'meta': meta, 'resources': [scan(10, 'owner/a'), scan(20, 'owner/b')],
                                          'failures': []}), encoding='utf-8')
            original = source.read_bytes()
            output = Path(directory) / 'report.json'
            status, text = self.run_main(['--source', str(source), '--output', str(output)], {})
            self.assertEqual(status, 2)
            self.assertIn('nothing was requested', text)
            self.assertFalse(output.exists())
            api = FakeAPI({'/repositories/10': repo(10, 'owner/a'), '/repositories/20': gone(404),
                           '/repos/owner/b': gone(404)})
            status, text = self.run_main(['--source', str(source), '--output', str(output)], {'GH_TOKEN': TOKEN}, api)
            self.assertEqual(status, 0)
            self.assertIn('not-found scan-20 owner/b', text)
            self.assertNotIn(TOKEN, text + output.read_text(encoding='utf-8'))
            report = json.loads(output.read_text(encoding='utf-8'))
            self.assertEqual(report['counts']['not-found'], 1)
            self.assertTrue(report['started_at'].endswith('Z') and report['completed_at'])
            self.assertEqual(source.read_bytes(), original)

    def test_command_refuses_to_write_into_the_data_directory(self):
        for target in (ROOT / 'data/source-index.json', ROOT / 'data/source-availability.json'):
            with self.subTest(target=target), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                self.run_main(['--output', str(target)], {'GH_TOKEN': TOKEN})


if __name__ == '__main__':
    unittest.main()
