"""The discovery report summarizes retained query evidence per run without inventing attribution."""
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
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import scan_sources as scanner

GATES = ' is:public fork:false archived:false'
FIRST, SECOND, THIRD = ('topic:ghidra' + GATES, 'topic:firmware-analysis' + GATES, 'topic:pcap' + GATES)
BODY = b'# Example\n\n## Usage\nInspect a firmware image.\n'
OID = hashlib.sha1(b'blob ' + str(len(BODY)).encode() + b'\0' + BODY).hexdigest()


def repository(number):
    return {'id': number, 'full_name': f'example/tool-{number}', 'html_url': f'https://github.com/example/tool-{number}',
            'private': False, 'visibility': 'public', 'archived': False, 'fork': False,
            'description': f'Firmware analysis tool {number}', 'topics': ['firmware-analysis'],
            'stargazers_count': number, 'default_branch': 'main'}


class API:
    """Offline search results per query; README 404s and failed searches are configurable."""
    def __init__(self, results, missing=(), failing=()):
        self.results, self.missing, self.failing = results, set(missing), set(failing)

    def json(self, path, search=False):
        if search:
            query = parse_qs(urlsplit(path).query)['q'][0]
            if query in self.failing:
                raise scanner.ScanError('http-422', 422)
            numbers, total, incomplete = self.results[query]
            return {'items': [repository(number) for number in numbers], 'total_count': total,
                    'incomplete_results': incomplete}
        if path.startswith('/repositories/'):
            return repository(int(path.rsplit('/', 1)[1]))
        number = int(path.split('/')[3].split('?')[0].rsplit('-', 1)[1])
        if number in self.missing:
            raise scanner.ScanError('http-404', 404)
        return {'type': 'file', 'path': 'README.md', 'sha': OID, 'size': len(BODY),
                'html_url': repository(number)['html_url'] + '/blob/main/README.md',
                'encoding': 'base64', 'content': base64.b64encode(BODY).decode()}


def scan(directory, name, api, queries, target, resume=None):
    output = Path(directory) / name
    args = SimpleNamespace(target=target, workers=1, requests_per_second=1, max_pages=1, candidate_buffer=10,
                           seed_curated=False, seed_papers=False, queries=queries, output=output)
    resumed, digest = (json.loads(resume.read_bytes()), hashlib.sha256(resume.read_bytes()).hexdigest()) if resume else (None, None)
    with contextlib.redirect_stdout(io.StringIO()):
        scanner.run_scan(api, args, resumed, digest)
    return output


def query_row(run, query):
    return next(row for row in run['queries'] if row['query'] == query)


class DiscoveryReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as directory:
            first = scan(directory, 'first.json', API({FIRST: ([1, 2], 2, False)}), [FIRST], 2)
            api = API({FIRST: ([1, 2, 3], 3, False), SECOND: ([3, 4, 5, 6], 1500, True)},
                      missing={6}, failing={THIRD})
            second = scan(directory, 'second.json', api, [FIRST, SECOND, THIRD], 6, resume=first)
            cls.document = json.loads(second.read_text())

    def test_runs_are_split_by_recorded_resume_counts(self):
        report = scanner.discovery_report(self.document)
        self.assertEqual(report['run_segmentation'], 'resume-history-counts')
        first, second = report['runs']
        # The first run recorded its own current_run, which the resume kept in resume_history.
        self.assertEqual((first['mode'], first['run_id']), ('fresh', self.document['meta']['resume_history'][0]['run']['run_id']))
        self.assertEqual(second['mode'], 'resume')
        self.assertEqual(second['run_id'], self.document['meta']['current_run']['run_id'])
        self.assertEqual((first['search_requests'], first['new_successful_readme_scans'], first['new_failed_readme_scans']), (1, 2, 0))
        self.assertEqual((second['search_requests'], second['new_successful_readme_scans'], second['new_failed_readme_scans']), (3, 3, 1))

    def test_overlapping_memberships_are_separate_from_the_distinct_union(self):
        second = scanner.discovery_report(self.document)['runs'][1]
        # Repository 3 matched both queries; repositories 4 and 5 matched only the capped one.
        self.assertEqual(query_row(second, FIRST)['successes'], 1)
        self.assertEqual(query_row(second, FIRST)['skipped'], {'retained_attempts': 2})
        capped = query_row(second, SECOND)
        self.assertEqual((capped['successes'], capped['exclusive_successes'], capped['returned']), (3, 2, 4))
        self.assertEqual((capped['capped'], capped['incomplete_requests'], capped['unrequested_within_cap']), (True, 1, 996))
        self.assertEqual((second['query_memberships'], second['successes_with_matched_query'],
                          second['overlapping_memberships']), (4, 3, 1))
        self.assertEqual((second['capped_queries'], second['incomplete_search_requests']), (1, 1))

    def test_readme_failures_are_never_attributed_to_queries(self):
        second = scanner.discovery_report(self.document)['runs'][1]
        self.assertEqual(self.document['failures'][0]['id'], 'scan-6')
        self.assertEqual(second['new_failed_readme_scans'], 1)
        for row in second['queries']:
            self.assertNotIn('failures', row)
        self.assertEqual(sum(row['successes'] for row in second['queries']), second['query_memberships'])
        failed = query_row(second, THIRD)
        self.assertEqual((failed['failed_requests'], failed['failure_reasons'], failed['successes']), (1, {'http-422': 1}, 0))
        self.assertIsNone(failed['successes_per_returned'])

    def test_legacy_positions_and_unknown_runs_are_handled_without_invention(self):
        document = copy.deepcopy(self.document)
        for entry in document['meta']['queries'][:1]:
            entry.pop('run_id', None)
        document['meta']['queries'].append({**document['meta']['queries'][-1], 'run_id': 'unrecorded-run'})
        report = scanner.discovery_report(document)
        self.assertEqual(report['runs'][0]['search_requests'], 1)
        self.assertEqual(report['unattributed_query_observations'], 1)
        self.assertEqual(report['runs'][1]['search_requests'], 3)

    def test_reconciled_unions_fall_back_to_one_segment(self):
        document = copy.deepcopy(self.document)
        document['meta']['checkpoint_reconciliations'] = [{'mode': 'union'}]
        report = scanner.discovery_report(document)
        self.assertTrue(report['run_segmentation'].startswith('unavailable: a checkpoint union'))
        self.assertEqual(len(report['runs']), 1)
        self.assertEqual(report['runs'][0]['new_successful_readme_scans'], 5)
        self.assertEqual(report['runs'][0]['search_requests'], 4)

    def test_command_prints_the_report_offline(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'scan.json'
            path.write_text(json.dumps(self.document))
            output = io.StringIO()
            with patch.object(sys, 'argv', ['scan_sources.py', '--discovery-report', str(path)]), \
                    patch.object(scanner.subprocess, 'run', side_effect=AssertionError('no gh call')), \
                    contextlib.redirect_stdout(output):
                self.assertEqual(scanner.main(), 0)
        self.assertEqual(len(json.loads(output.getvalue())['runs']), 2)


if __name__ == '__main__':
    unittest.main()
