"""Source observations and scope reviews keep a possible chronology without re-dating history."""
from copy import deepcopy
import datetime as dt
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from source_scope import validate_scope
from validate import validate_scan_chronology, validate_source_index

NOW = dt.datetime(2026, 10, 18, 12, tzinfo=dt.timezone.utc)
META = {
    'started_at': '2026-10-16T01:00:00Z', 'completed_at': '2026-10-16T11:30:00Z', 'last_checkpoint_at': '2026-10-16T11:30:00Z',
    'resume_history': [{'started_at': '2026-10-16T01:00:00Z', 'completed_at': '2026-10-16T02:00:00Z'}],
    'current_run': {'started_at': '2026-10-16T11:00:00Z', 'completed_at': '2026-10-16T11:30:00Z',
                    'retained_successful_readme_scans': 1, 'retained_failed_readme_scans': 1,
                    'query_start_index': 1, 'seed_observation_start_index': 0, 'resume_observation_start_index': 1},
    'queries': [{'observed_at': '2026-10-16T01:00:01Z'}, {'observed_at': '2026-10-16T11:00:01Z'}],
    'seed_observations': [{'observed_at': '2026-10-16T11:00:02Z'}],
    'resume_observations': [{'observed_at': '2026-10-16T01:30:00Z'}, {'observed_at': '2026-10-16T11:00:03Z'}],
}
# The first success and failure are retained from the earlier run; the others are new in this run.
RECORDS = [
    {'id': 'scan-1', 'metadata_observed_at': '2026-10-16T01:10:00Z', 'observed_at': '2026-10-16T01:10:01Z',
     'readme_integrity_review': {'reviewed_at': '2026-10-17T09:00:00Z'}},  # A separate later recheck.
    {'id': 'scan-2', 'metadata_observed_at': '2026-10-16T11:10:00Z', 'observed_at': '2026-10-16T11:10:01Z'},
]
FAILURES = [{'id': 'scan-3', 'observed_at': '2026-10-16T01:20:00Z'}, {'id': 'scan-4', 'observed_at': '2026-10-16T11:20:00Z'}]


def chronology_errors(meta=None, records=None, failures=None, now=NOW):
    meta, records, failures = deepcopy(meta or META), deepcopy(records or RECORDS), deepcopy(failures or FAILURES)
    before = deepcopy((meta, records, failures))
    errors = []
    validate_scan_chronology(meta, records, failures, errors, now=now)
    assert (meta, records, failures) == before, 'validation must not rewrite evidence'
    return errors


def with_changes(value, path, new):
    value = deepcopy(value)
    target = value
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = new
    return value


class ScanChronologyTests(unittest.TestCase):
    def test_retained_history_and_later_rechecks_pass(self):
        self.assertEqual(chronology_errors(), [])
        # Within a day of now is tolerated for clock differences.
        self.assertEqual(chronology_errors(now=dt.datetime(2026, 10, 16, 12, tzinfo=dt.timezone.utc)), [])

    def test_future_times_fail_with_stable_ids(self):
        future = '2099-01-01T00:00:00Z'
        cases = [
            ({'records': with_changes(RECORDS, [1, 'observed_at'], future)}, 'source index record scan-2.observed_at'),
            ({'records': with_changes(RECORDS, [0, 'readme_integrity_review', 'reviewed_at'], future)},
             'source index record scan-1.readme_integrity_review.reviewed_at'),
            ({'failures': with_changes(FAILURES, [1, 'observed_at'], future)}, 'source index failure scan-4.observed_at'),
            ({'meta': with_changes(META, ['queries', 0, 'observed_at'], future)}, 'source index queries[0].observed_at'),
            ({'meta': with_changes(META, ['resume_history', 0, 'completed_at'], future)},
             'source index resume_history[0].completed_at'),
            ({'meta': with_changes(META, ['started_at'], future)}, 'source index meta.started_at'),
        ]
        for arguments, where in cases:
            with self.subTest(where):
                self.assertIn(f'{where}: recorded time is in the future', chronology_errors(**arguments))

    def test_metadata_lookup_precedes_its_readme_observation(self):
        records = with_changes(RECORDS, [0, 'metadata_observed_at'], '2026-10-16T01:10:02Z')
        self.assertEqual(chronology_errors(records=records),
                         ['source index record scan-1: metadata_observed_at follows its README observation'])

    def test_only_new_attempts_and_observations_must_fit_the_current_run(self):
        self.assertEqual(chronology_errors(records=with_changes(RECORDS, [1, 'observed_at'], '2026-10-16T11:40:00Z')),
                         ['source index record scan-2: new README attempt lies outside the current run window'])
        self.assertEqual(chronology_errors(failures=with_changes(FAILURES, [1, 'observed_at'], '2026-10-16T10:59:59Z')),
                         ['source index failure scan-4: new README attempt lies outside the current run window'])
        self.assertEqual(chronology_errors(meta=with_changes(META, ['resume_observations', 1, 'observed_at'], '2026-10-16T01:40:00Z')),
                         ['source index resume_observations[1]: current-run observation lies outside the run window'])
        # Retained rows and observations keep their earlier-run times.
        self.assertEqual(chronology_errors(meta=with_changes(META, ['current_run', 'retained_successful_readme_scans'], 2),
                                           records=with_changes(with_changes(RECORDS, [1, 'observed_at'], '2026-10-16T01:50:00Z'),
                                                                [1, 'metadata_observed_at'], '2026-10-16T01:49:00Z')), [])

    def test_an_in_progress_checkpoint_closes_its_window_at_the_last_save(self):
        meta = with_changes(with_changes(META, ['current_run', 'completed_at'], None), ['last_checkpoint_at'], '2026-10-16T11:15:00Z')
        self.assertEqual(chronology_errors(meta=meta),
                         ['source index failure scan-4: new README attempt lies outside the current run window'])
        backwards = with_changes(META, ['current_run', 'completed_at'], '2026-10-16T10:00:00Z')
        self.assertEqual(chronology_errors(meta=backwards), ['source index current_run: the run ends before it starts'])

    def test_source_index_validation_applies_the_checks(self):
        records = with_changes(RECORDS, [1, 'observed_at'], '2099-01-01T00:00:00Z')
        errors = []
        validate_source_index({'meta': deepcopy(META), 'resources': records, 'failures': deepcopy(FAILURES)}, errors)
        self.assertIn('source index record scan-2.observed_at: recorded time is in the future', errors)


SOURCE = {'id': 'scan-9', 'full_name': 'example/copy', 'scan_status': 'readme-scanned', 'readme_sha256': 'a' * 64,
          'readme_url': 'https://github.com/example/copy/blob/main/README.md', 'observed_at': '2026-10-16T01:30:00Z'}
SCOPE = {'decision': 'exclude', 'reason_code': 'not-reverse-engineering', 'reason_en': 'Unrelated template.',
         'reason_zh': '与逆向工程无关的模板。', 'readme_sha256': 'a' * 64, 'evidence_url': SOURCE['readme_url'],
         'reviewed_at': '2026-10-16T04:00:00Z'}


def scope_errors(reviewed_at):
    scope = {'scan-9': SCOPE | {'reviewed_at': reviewed_at}}
    before = deepcopy(scope)
    errors = []
    validate_scope([SOURCE], scope, errors, now=NOW)
    assert scope == before
    return errors


class ScopeChronologyTests(unittest.TestCase):
    def test_reviews_after_the_scan_and_local_calendar_dates_pass(self):
        for reviewed_at in ('2026-10-16T04:00:00Z', '2026-10-16T01:30:00Z', '2026-10-16', '2026-10-15', '2026-10-19',
                            '2026-10-19T11:00:00Z'):
            with self.subTest(reviewed_at):
                self.assertEqual(scope_errors(reviewed_at), [])

    def test_future_reviews_fail(self):
        for reviewed_at in ('2026-10-20', '2099-01-01', '2026-10-19T12:00:01Z'):
            with self.subTest(reviewed_at):
                self.assertEqual(scope_errors(reviewed_at), ['scan-9: scope reviewed_at is in the future'])

    def test_reviews_before_the_scan_fail(self):
        for reviewed_at in ('2026-10-16T01:29:59Z', '2026-10-14'):
            with self.subTest(reviewed_at):
                self.assertEqual(scope_errors(reviewed_at), ['scan-9: scope review precedes the README scan it reviews'])


if __name__ == '__main__':
    unittest.main()
