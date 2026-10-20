"""Failed source-scan records keep the status, reason code, timestamp and HTTP status the scanner writes."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate import validate_failure_metadata, validate_source_index

FAILURE = {
    'id': 'scan-101', 'full_name': 'example/missing-readme', 'url': 'https://github.com/example/missing-readme',
    'observed_at': '2026-10-16T01:36:38.113161Z', 'scan_status': 'failed', 'reason': 'http-404', 'http_status': 404,
}
WHERE = 'source index failure 0'


def errors_for(**changes):
    # A value of ... removes that field from the fixture.
    failure = {key: value for key, value in (FAILURE | changes).items() if value is not ...}
    errors = []
    validate_failure_metadata(failure, WHERE, errors)
    return errors


class FailureMetadataTests(unittest.TestCase):
    def test_scanner_failure_shapes_pass(self):
        for changes in ({}, {'reason': 'empty-readme', 'http_status': None},
                        {'reason': 'network-failure', 'http_status': None},
                        {'reason': 'readme-repository-unavailable', 'http_status': 451},
                        {'reason': 'worker-TimeoutError', 'http_status': None},
                        {'observed_at': '2026-10-16T09:36:38+08:00'}):
            with self.subTest(changes):
                self.assertEqual(errors_for(**changes), [])

    def test_status_and_reason_are_checked(self):
        status_error = [f'{WHERE}: preserve the failed scan status']
        self.assertEqual(errors_for(scan_status='readme-scanned'), status_error)
        self.assertEqual(errors_for(scan_status=...), status_error)
        reason_error = [f'{WHERE}: reason must be a nonempty error code of at most 100 characters']
        for reason in (..., None, '', ' ', 'HTTP Error 404: Not Found', 'http-404\n', 'x' * 101, 404, 'trailing-'):
            with self.subTest(reason=reason):
                self.assertEqual(errors_for(reason=reason, http_status=None), reason_error)

    def test_http_status_is_an_integer_code_or_null(self):
        status_error = [f'{WHERE}: http_status must be an HTTP status code, or null for a transport or content failure']
        for status in (..., '404', 404.0, True, 99, 600):
            with self.subTest(status=status):
                self.assertEqual(errors_for(http_status=status), status_error)
        self.assertEqual(errors_for(http_status=None), [f'{WHERE}: http_status does not match the http-404 reason'])
        self.assertEqual(errors_for(http_status=403), [f'{WHERE}: http_status does not match the http-404 reason'])

    def test_observed_at_is_a_timezone_aware_timestamp(self):
        for value in (..., None, '2026-10-16', '2026-10-16T01:36:38', 'yesterday', 20261016):
            with self.subTest(value=value):
                self.assertEqual(errors_for(observed_at=value), [f'{WHERE}: invalid timezone-aware observed_at timestamp'])

    def test_source_index_validation_applies_the_failure_checks(self):
        document = {'meta': {'status': 'complete', 'successful_readme_scans': 0, 'failed': 1, 'attempted_readme_scans': 1},
                    'resources': [], 'failures': [FAILURE | {'scan_status': 'ok', 'observed_at': 'not a time', 'http_status': '404'}]}
        errors = []
        validate_source_index(document, errors)
        self.assertEqual([error for error in errors if error.startswith('source index failure')], [
            f'{WHERE}: preserve the failed scan status',
            f'{WHERE}: http_status must be an HTTP status code, or null for a transport or content failure',
            f'{WHERE}: invalid timezone-aware observed_at timestamp',
        ])


if __name__ == '__main__':
    unittest.main()
