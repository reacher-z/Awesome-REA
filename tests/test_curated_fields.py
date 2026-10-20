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
}


def errors_for(record):
    errors = []
    validate_resources([record], errors, now=NOW)
    return errors


class CuratedFieldTests(unittest.TestCase):
    def test_supported_fields_including_additional_evidence_pass(self):
        self.assertEqual(errors_for(deepcopy(RECORD)), [])
        without_optional = {key: value for key, value in RECORD.items() if key != 'additional_evidence_urls'}
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
                                       'requirement_facets': [], 'added_at': '2026-09-30'}
                   for index in range(3)]
        errors = []
        validate_resources(records, errors, now=NOW)
        self.assertEqual(errors, [])
        self.assertEqual(unknown_field_warnings(records), [
            f"resource 'field-fixture-0'.{field}: unsupported field (in 3 record(s)); add it to the "
            'catalog format guide and validator, or remove it'
            for field in ('added_at', 'requirement_facets')
        ])

    def test_pull_request_review_applies_the_same_rule(self):
        self.assertIs(review_pr.validate_resources, validate_resources)


if __name__ == '__main__':
    unittest.main()
