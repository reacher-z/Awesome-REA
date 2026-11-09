"""Curated records reject misspelled field names and flag other unlisted fields as advisory."""
from copy import deepcopy
import datetime as dt
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import review_pr
from validate import unknown_field_warnings, validate_resources

NOW = dt.datetime(2026, 10, 1, tzinfo=dt.timezone.utc)
RECORD = {
    'id': 'field-fixture', 'name': 'Field fixture', 'url': 'https://github.com/example/field-fixture',
    'category': 'native-analysis', 'relationship': 'foundation', 'kind': 'tool', 'targets': ['binary'],
    'description_en': 'A fixture.', 'description_zh': '测试记录。',
    'evidence_url': 'https://github.com/example/field-fixture/blob/0123456789abcdef0123456789abcdef01234567/README.md',
    'additional_evidence_urls': ['https://example.org/docs'],
    'verified_at': '2026-09-30', 'verification': 'source-reviewed', 'requirements': ['Python 3'],
    'requirement_facets': ['prerequisites'], 'added_at': '2026-09-30',
}


def errors_for(record):
    errors = []
    validate_resources([record], errors, now=NOW)
    return errors


class CuratedFieldTests(unittest.TestCase):
    def test_supported_fields_including_optional_ones_pass(self):
        self.assertEqual(errors_for(deepcopy(RECORD)), [])
        optional = {'additional_evidence_urls', 'added_at', 'requirement_facets'}
        without_optional = {key: value for key, value in RECORD.items() if key not in optional}
        self.assertEqual(errors_for(without_optional), [])
        self.assertEqual(unknown_field_warnings([RECORD, without_optional]), [])

    def test_misspelled_fields_fail_with_resource_id_and_field_name(self):
        for misspelled, intended in (('requirementz', 'requirements'), ('verifed_at', 'verified_at'),
                                     ('target', 'targets'), ('addtional_evidence_url', 'additional_evidence_urls'),
                                     ('evidence_urls', 'evidence_url')):
            with self.subTest(misspelled):
                record = deepcopy(RECORD) | {misspelled: RECORD.get(intended, ['https://example.org/more'])}
                self.assertEqual(errors_for(record),
                                 [f"resource 'field-fixture'.{misspelled}: unknown field; did you mean {intended}?"])
                self.assertEqual(unknown_field_warnings([record]), [])

    def test_misspelling_that_replaces_a_required_field_reports_both(self):
        record = deepcopy(RECORD)
        record['requirementz'] = record.pop('requirements')
        self.assertEqual(errors_for(record), [
            "resource 'field-fixture'.requirementz: unknown field; did you mean requirements?",
            "resource 'field-fixture': missing fields requirements",
        ])

    def test_other_new_fields_are_advisory_and_grouped(self):
        records = [deepcopy(RECORD) | {'id': f'field-fixture-{index}', 'url': f'https://example.org/{index}',
                                       'mirror_urls': [], 'archived_at': '2026-09-30'}
                   for index in range(3)]
        errors = []
        validate_resources(records, errors, now=NOW)
        self.assertEqual(errors, [])
        self.assertEqual(unknown_field_warnings(records), [
            f"resource 'field-fixture-0'.{field}: unsupported field (in 3 record(s)); add it to the "
            'catalog format guide and validator, or remove it'
            for field in ('archived_at', 'mirror_urls')
        ])

    def test_source_unavailable_records_a_checked_http_status(self):
        check = {'checked_at': '2026-09-30T18:00:00Z', 'outcome': 'not-found', 'http_status': 404}
        self.assertEqual(errors_for(deepcopy(RECORD) | {'source_unavailable': check}), [])
        self.assertEqual(errors_for(deepcopy(RECORD) | {'source_unavailable': check | {'outcome': 'blocked', 'http_status': 451}}), [])
        where = "resource 'field-fixture'.source_unavailable: "
        for value, problem in (
                ('gone', 'use an object with exactly checked_at, http_status, outcome'),
                ({'checked_at': '2026-09-30T18:00:00Z', 'outcome': 'not-found'}, 'use an object with exactly checked_at, http_status, outcome'),
                (check | {'outcome': 'archived'}, 'outcome must be one of not-found, blocked'),
                (check | {'http_status': 403}, 'http_status must be 404 or 410 for outcome not-found'),
                (check | {'http_status': '404'}, 'http_status must be 404 or 410 for outcome not-found'),
                (check | {'checked_at': '2026-09-30'}, 'checked_at must be a timezone-aware ISO timestamp'),
                (check | {'checked_at': '2026-10-03T00:00:00Z'}, 'checked_at is in the future'),
                (check | {'checked_at': '2026-09-29T23:00:00Z'}, 'checked_at must not precede verified_at; the source was read at review')):
            with self.subTest(value=value):
                self.assertEqual(errors_for(deepcopy(RECORD) | {'source_unavailable': value}), [where + problem])
        self.assertEqual(unknown_field_warnings([deepcopy(RECORD) | {'source_unavailable': check}]), [])

    def test_pull_request_review_applies_the_same_rule(self):
        self.assertIs(review_pr.validate_resources, validate_resources)


if __name__ == '__main__':
    unittest.main()
