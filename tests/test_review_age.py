"""The source-review age queue groups records by review age as of a supplied date and never edits them."""
import contextlib
import copy
import datetime as dt
import io
import json
from pathlib import Path
import socket
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from review_age import CATALOGS, main, read_catalogs, review_queue, text_lines

AS_OF = dt.date(2027, 4, 1)


def resource(identifier, verified_at):
    return {'id': identifier, 'verified_at': verified_at, 'verification': 'source-reviewed',
            'evidence_url': f'https://github.com/owner/{identifier}/blob/{"a" * 40}/README.md'}


def paper(identifier, verified_at, status='preprint'):
    return {'id': identifier, 'verified_at': verified_at, 'publication_status': status, 'runtime_tested': False,
            'evidence_urls': [f'https://arxiv.org/abs/{identifier}', 'https://example.org/paper.pdf']}


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.catalogs = [
            ('resource', 'data/rea-resources.json', [resource('recent', '2027-03-30')]),
            ('resource', 'data/tool-resources.json', [resource('older', '2026-10-15'), resource('zoned', '2026-12-31T23:30:00-05:00'),
                                                      resource('future', '2027-04-02')]),
            ('paper', 'data/papers.json', [paper('paper-a', '2026-10-15', 'conference-paper'), paper('paper-b', '2027-01-01')]),
        ]
        self.scans = [{'id': 'scan-1', 'observed_at': '2025-01-01T00:00:00Z', 'verification': 'automated-readme-scan'},
                      {'id': 'scan-2', 'observed_at': '2027-04-01T12:00:00Z'}]

    def test_records_are_grouped_by_age_and_type_oldest_first_with_ids_dates_and_evidence(self):
        report = review_queue(self.catalogs, self.scans, AS_OF)
        self.assertEqual(report['as_of'], '2027-04-01')
        self.assertEqual(report['bands'], ['0-29 days', '30-89 days', '90-179 days', '180-364 days', '365+ days'])
        rows = [(entry['record_type'], entry['id'], entry['review_date'], entry['age_days'], entry['band'])
                for entry in report['records']]
        self.assertEqual(rows, [('paper', 'paper-a', '2026-10-15', 168, '90-179 days'),
                                ('resource', 'older', '2026-10-15', 168, '90-179 days'),
                                ('paper', 'paper-b', '2027-01-01', 90, '90-179 days'),
                                ('resource', 'zoned', '2027-01-01', 90, '90-179 days'),
                                ('resource', 'recent', '2027-03-30', 2, '0-29 days')])
        self.assertEqual(report['counts']['resource'], {'0-29 days': 1, '30-89 days': 0, '90-179 days': 2,
                                                        '180-364 days': 0, '365+ days': 0})
        self.assertEqual(report['counts']['paper']['90-179 days'], 2)
        entries = {entry['id']: entry for entry in report['records']}
        self.assertEqual(entries['paper-a']['evidence_url'], 'https://arxiv.org/abs/paper-a')
        self.assertEqual(entries['older']['evidence_url'], self.catalogs[1][2][0]['evidence_url'])
        # The recorded value is kept beside its UTC date.
        self.assertEqual(entries['zoned']['verified_at'], '2026-12-31T23:30:00-05:00')
        self.assertEqual([entry['id'] for entry in report['reviewed_after_as_of']], ['future'])

    def test_bands_are_configurable(self):
        report = review_queue(self.catalogs, self.scans, AS_OF, (7, 100))
        self.assertEqual(report['bands'], ['0-6 days', '7-99 days', '100+ days'])
        self.assertEqual([entry['band'] for entry in report['records']],
                         ['100+ days', '100+ days', '7-99 days', '7-99 days', '0-6 days'])

    def test_aging_reads_records_without_changing_status_or_inferring_abandonment(self):
        before = copy.deepcopy((self.catalogs, self.scans))
        report = review_queue(self.catalogs, self.scans, AS_OF)
        self.assertEqual((self.catalogs, self.scans), before)
        self.assertEqual(len(report['records']) + len(report['reviewed_after_as_of']), 6)
        for entry in report['records']:
            self.assertEqual(set(entry), {'id', 'record_type', 'catalog', 'verified_at', 'review_date',
                                          'age_days', 'evidence_url', 'band'})
        # Entries carry no status or verdict, only review dates; the policy says so explicitly.
        listed = json.dumps([report['records'], report['reviewed_after_as_of'], report['counts']])
        for value in ('publication_status', 'conference-paper', 'preprint', 'verification', 'stale', 'dead'):
            self.assertNotIn(value, listed)
        self.assertIn('publication status is unchanged', report['policy'])
        self.assertIn('not evidence that a description is outdated or that a project is abandoned', report['policy'])

    def test_scan_observations_stay_separate_from_source_reviews(self):
        report = review_queue(self.catalogs, self.scans, AS_OF)
        self.assertFalse([entry for entry in report['records'] if entry['id'].startswith('scan-')])
        scans = report['automated_readme_scans']
        self.assertEqual((scans['date_field'], scans['records'], scans['earliest'], scans['latest']),
                         ('observed_at', 2, '2025-01-01', '2027-04-01'))
        self.assertEqual((scans['counts']['365+ days'], scans['counts']['0-29 days']), (1, 1))
        self.assertNotIn('scan-', '\n'.join(text_lines(report)))
        self.assertIn('not source reviews', '\n'.join(text_lines(report)))

    def test_text_lists_the_requested_type_and_minimum_age(self):
        lines = list(text_lines(review_queue(self.catalogs, self.scans, AS_OF), 'paper', 100))
        listed = [line.split()[1] for line in lines if line.startswith(('paper ', 'resource '))]
        self.assertEqual(listed, ['paper-a'])
        self.assertIn('for 4 curated resources and 2 papers', lines[0])


class CommandTests(unittest.TestCase):
    def run_main(self, argv):
        output = io.StringIO()
        blocked = AssertionError('network access in a unit test')
        with contextlib.redirect_stdout(output), patch.object(socket.socket, 'connect', side_effect=blocked), \
                patch.object(socket, 'getaddrinfo', side_effect=blocked):
            status = main(argv)
        return status, output.getvalue()

    def test_command_reads_the_catalogs_offline_with_a_supplied_date(self):
        paths = [ROOT / path for _, path in CATALOGS] + [ROOT / 'data/source-index.json']
        before = [path.read_bytes() for path in paths]
        status, text = self.run_main(['--as-of', '2027-04-01', '--json'])
        self.assertEqual(status, 0)
        report = json.loads(text)
        catalogs, scans = read_catalogs()
        self.assertEqual(len(report['records']) + len(report['reviewed_after_as_of']),
                         sum(len(records) for _, _, records in catalogs))
        self.assertEqual(report['automated_readme_scans']['records'], len(scans))
        self.assertEqual([path.read_bytes() for path in paths], before)

    def test_command_rejects_invalid_dates_and_bands(self):
        for argv in (['--as-of', '2027-02-30'], ['--bands', '30,30'], ['--bands', '0,30'], ['--bands', 'x'],
                     ['--min-age-days', '-1']):
            with self.subTest(argv=argv), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                self.run_main(argv)


if __name__ == '__main__':
    unittest.main()
