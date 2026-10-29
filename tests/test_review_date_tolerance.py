"""Tests for consistent one-day future tolerance on review dates."""
import datetime as dt
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate import public_https_error, validate_resources
from validate_papers import validate_papers


def minimal_resource(verified_at):
    return {
        'id': 'test-resource',
        'category': 'native-analysis',
        'kind': 'tool',
        'relationship': 'foundation',
        'targets': ['binary'],
        'name': 'Test Tool',
        'url': 'https://example.com/tool',
        'description_en': 'A test tool for reverse engineering.',
        'description_zh': '用于逆向工程的测试工具。',
        'evidence_url': 'https://example.com/evidence',
        'verified_at': verified_at,
        'verification': 'source-reviewed',
        'requirements': ['Python 3'],
    }


def minimal_paper(verified_at):
    return {
        'id': 'paper-test',
        'title': 'Test Paper on Reverse Engineering',
        'title_zh': '逆向工程测试论文',
        'authors': ['Test Author'],
        'year': 2024,
        'date_precision': 'year',
        'publication_date': None,
        'date_basis': 'publication year',
        'date_basis_zh': '出版年份',
        'venue': 'Test Conference',
        'publication_status': 'preprint',
        'url': 'https://example.com/paper',
        'pdf_url': 'https://example.com/paper.pdf',
        'description_en': 'This paper describes a reverse engineering technique.',
        'description_zh': '本文描述了一种逆向工程技术。',
        'scope_limitations_en': 'Limited to synthetic data.',
        'scope_limitations_zh': '仅限于合成数据。',
        'why_fits_en': 'It provides analysis of binary protocols.',
        'why_fits_zh': '它提供了二进制协议的分析。',
        'metadata_notes': 'Reviewed the PDF.',
        'metadata_notes_zh': '审阅了PDF。',
        'kind': 'research',
        'verified_at': verified_at,
        'verification': 'source-reviewed',
        'targets': ['binary'],
        'evidence_urls': ['https://example.com/paper'],
        'runtime_tested': False,
        'arxiv_id': '2401.00001',
        'arxiv_version_reviewed': 'v1',
        'first_arxiv_date': '2024-01-01',
        'doi': None,
        'code_url': None,
        'project_url': None,
    }


def resource_errors(value, now):
    errors = []
    validate_resources([minimal_resource(value)], errors, now=now)
    return errors


def paper_errors(value, now, **changes):
    record = minimal_paper(value)
    record.update(changes)
    errors = []
    validate_papers([record], errors, url_check=public_https_error, now=now)
    return errors


class TestReviewDateTolerance(unittest.TestCase):
    def test_consistent_calendar_dates_across_utc_midnight(self):
        for now in (dt.datetime(2026, 10, 17, 23, 59, 59, tzinfo=dt.timezone.utc),
                    dt.datetime(2026, 10, 18, 0, 0, 0, tzinfo=dt.timezone.utc),
                    dt.datetime(2026, 12, 31, 23, 0, 0, tzinfo=dt.timezone.utc)):
            for offset in (-1, 0, 1, 2):
                value = (now.date() + dt.timedelta(days=offset)).isoformat()
                for validate in (resource_errors, paper_errors):
                    with self.subTest(now=now, offset=offset, validator=validate.__name__):
                        errors = validate(value, now)
                        if offset <= 1:
                            self.assertEqual(errors, [])
                        else:
                            self.assertEqual(len(errors), 1, errors)
                            self.assertIn('.verified_at:', errors[0])

    def test_invalid_calendar_dates_fail_for_both(self):
        now = dt.datetime(2026, 10, 17, 23, tzinfo=dt.timezone.utc)
        for value in ('2026-02-30', '2026-13-01', '2026-1-01', 'not-a-date'):
            for validate in (resource_errors, paper_errors):
                with self.subTest(value=value, validator=validate.__name__):
                    errors = validate(value, now)
                    self.assertEqual(len(errors), 1, errors)
                    self.assertIn('.verified_at:', errors[0])

    def test_resource_timestamps_keep_exact_24_hour_boundary(self):
        now = dt.datetime(2026, 10, 17, 23, tzinfo=dt.timezone.utc)
        for value, accepted in (
                ('2026-10-18T23:00:00Z', True),
                ('2026-10-19T07:00:00+08:00', True),
                ('2026-10-18T23:00:00.000001Z', False),
                ('2026-10-19T07:00:00.000001+08:00', False),
                ('2026-10-18T22:00:00', False)):
            with self.subTest(value=value):
                errors = resource_errors(value, now)
                if accepted:
                    self.assertEqual(errors, [])
                else:
                    self.assertEqual(len(errors), 1, errors)
                    self.assertIn('.verified_at:', errors[0])
        # Paper review metadata remains date-only, even for an in-range timestamp.
        self.assertTrue(any('.verified_at:' in error for error in
                            paper_errors('2026-10-17T23:00:00Z', now)))

    def test_clock_offset_is_normalized_to_utc(self):
        now = dt.datetime(2026, 10, 18, 7, tzinfo=dt.timezone(dt.timedelta(hours=8)))
        for validate in (resource_errors, paper_errors):
            with self.subTest(validator=validate.__name__):
                self.assertEqual(validate('2026-10-18', now), [])
                self.assertTrue(any('.verified_at:' in error for error in validate('2026-10-19', now)))

    def test_publication_and_first_arxiv_dates_remain_strict(self):
        now = dt.datetime(2026, 10, 17, 23, tzinfo=dt.timezone.utc)
        for field in ('publication_date', 'first_arxiv_date'):
            for value, accepted in (('2026-10-17', True), ('2026-10-18', False), ('2026-02-30', False)):
                with self.subTest(field=field, value=value):
                    changes = {field: value}
                    if field == 'publication_date':
                        changes.update(year=2026, date_precision='day')
                    errors = paper_errors('2026-10-18', now, **changes)
                    if accepted:
                        self.assertEqual(errors, [])
                    else:
                        self.assertEqual(len(errors), 1, errors)
                        self.assertIn(f'.{field}:', errors[0])
        self.assertEqual(paper_errors('2026-10-18', now, year=2026,
                                     date_precision='month', publication_date='2026-10'), [])
        errors = paper_errors('2026-10-18', now, year=2026,
                              date_precision='month', publication_date='2026-11')
        self.assertEqual(len(errors), 1, errors)
        self.assertIn('.publication_date:', errors[0])


if __name__ == '__main__':
    unittest.main()
