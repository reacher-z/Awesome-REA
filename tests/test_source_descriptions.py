"""Regressions for anomalous metadata and advertised README hash mismatches."""
import base64
import copy
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from source_descriptions import SOURCE_DESCRIPTION_POLICY, capture_description, description_fallback, validate_description_capture
from scan_sources import initial_meta, run_scan, scan_readme
from localization import localized_records
from build_browse_pages import repository_card


class DescriptionCaptureTests(unittest.TestCase):
    def test_resume_refreshes_policy_without_rewriting_historical_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            args = SimpleNamespace(target=1, workers=1, requests_per_second=1,
                                   max_pages=1, candidate_buffer=0, seed_curated=False,
                                   seed_papers=False, queries=[], output=Path(directory) / 'index.json')
            meta = initial_meta(args, '2026-10-16T00:00:00Z')
            meta.update(description_policy='Historical source-description policy',
                        discovered_repository_ids=['scan-1'], successful_readme_scans=1,
                        failed=0, attempted_readme_scans=1, unique_repos=1,
                        unattempted_candidates=0)
            historical = {'id': 'scan-1', 'full_name': 'example/retained',
                          'description_en': 'legacy', 'scan_status': 'readme-scanned'}
            before = copy.deepcopy(historical)
            with contextlib.redirect_stdout(io.StringIO()):
                run_scan(None, args, {'meta': meta, 'resources': [historical], 'failures': []}, 'a' * 64)
            result = json.loads(args.output.read_text())
            self.assertEqual(result['resources'], [before])
            self.assertEqual(result['meta']['description_policy'], SOURCE_DESCRIPTION_POLICY)
            self.assertEqual(result['meta']['resume_history'][-1]['description_policy'], 'Historical source-description policy')

    def test_short_originals_and_empty_values_are_preserved(self):
        for text in ('', 'A tool for app recovery.', '保留上游描述', 'x' * 1000):
            captured = capture_description(text)
            self.assertEqual(captured['description_en'], text)
            self.assertEqual(captured['description_zh'], text)
            self.assertNotIn('description_omission', captured)
            errors = []
            validate_description_capture(captured, errors, 'fixture')
            self.assertFalse(errors)
        self.assertEqual(capture_description(None)['description_en'], '')
        with self.assertRaises(ValueError):
            capture_description({'unexpected': 'object'})

    def test_oversized_text_is_replaced_only_by_fingerprint(self):
        original = '界' * 1001
        captured = capture_description(original)
        self.assertEqual((captured['description_en'], captured['description_zh']), ('', ''))
        evidence = captured['description_omission']
        self.assertEqual(evidence['original_characters'], 1001)
        self.assertEqual(evidence['original_utf8_bytes'], 3003)
        self.assertEqual(evidence['original_sha256'], hashlib.sha256(original.encode()).hexdigest())
        self.assertNotIn(original, repr(captured))
        errors = []
        validate_description_capture(captured, errors, 'fixture')
        self.assertFalse(errors)

    def test_invalid_omission_claims_are_rejected(self):
        valid = capture_description('x' * 1001)
        cases = []
        for field, value in (('original_characters', 1000), ('original_utf8_bytes', 1), ('original_sha256', 'invalid'), ('limit_characters', 2000)):
            candidate = copy.deepcopy(valid)
            candidate['description_omission'][field] = value
            cases.append(candidate)
        for field, value in (('description_en', 'replacement claim'), ('description_capture_policy', 'unknown')):
            candidate = copy.deepcopy(valid)
            candidate[field] = value
            cases.append(candidate)
        candidate = copy.deepcopy(valid)
        candidate['description_omission']['original_text'] = 'must not be retained'
        cases.append(candidate)
        candidate = copy.deepcopy(valid)
        del candidate['description_capture_policy']
        cases.append(candidate)
        for candidate in cases:
            errors = []
            validate_description_capture(candidate, errors, 'fixture')
            self.assertTrue(errors)

    def test_legacy_records_are_not_rewritten(self):
        legacy = {'description_en': 'x' * 1001, 'description_zh': 'x' * 1001}
        before = copy.deepcopy(legacy)
        errors = []
        validate_description_capture(legacy, errors, 'legacy')
        self.assertFalse(errors)
        self.assertEqual(legacy, before)

    def test_localization_and_static_cards_do_not_invent_upstream_text(self):
        record = {'id': 'scan-1', 'full_name': 'example/demo', 'url': 'https://github.com/example/demo', 'stars': 1, 'license': 'MIT', **capture_description('x' * 1001)}
        result = localized_records([record], {'scan-1': {'description_en': '', 'description_zh': ''}})[0]
        self.assertEqual(result['description_original'], '')
        self.assertEqual(result['description_omission'], record['description_omission'])
        for language in ('en', 'zh'):
            html = repository_card(result, language, False)
            self.assertIn(description_fallback(result, language), html)
            self.assertNotIn('x' * 1001, html)
        self.assertNotEqual(description_fallback(result, 'en'), description_fallback({}, 'en'))

    def test_scanner_rejects_received_content_when_advertised_blob_disagrees(self):
        body = b'# Example\nA small README for a test fixture.\n'
        actual_git_sha = hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()
        class FakeAPI:
            def __init__(self, advertised):
                self.advertised = advertised
            def json(self, path):
                if path.startswith('/repositories/'):
                    return {'id': 1, 'full_name': 'example/demo', 'html_url': 'https://github.com/example/demo',
                            'private': False, 'archived': False, 'fork': False}
                return {'type': 'file', 'size': len(body), 'encoding': 'base64', 'content': base64.b64encode(body).decode(), 'sha': self.advertised, 'path': 'README.md', 'html_url': 'https://github.com/example/demo/blob/main/README.md'}
        repository = {'id': 1, 'full_name': 'example/demo', 'html_url': 'https://github.com/example/demo', 'description': 'x' * 1001, '_metadata_observed_at': '2026-10-16T00:00:00Z', '_matched_queries': [], 'topics': []}
        for advertised in (actual_git_sha, '0' * 40):
            record, failure = scan_readme(FakeAPI(advertised), repository)
            if advertised != actual_git_sha:
                self.assertIsNone(record)
                self.assertEqual(failure['reason'], 'readme-git-sha-mismatch')
                continue
            self.assertIsNone(failure)
            self.assertEqual(record['readme_git_sha'], advertised)
            self.assertEqual(record['readme_content_git_sha'], actual_git_sha)
            self.assertEqual(record['readme_git_sha_matches_content'], advertised == actual_git_sha)
            self.assertEqual(record['readme_sha256'], hashlib.sha256(body).hexdigest())
            self.assertEqual(record['readme_bytes'], len(body))
            self.assertEqual(record['description_en'], '')
            self.assertIn('description_omission', record)


if __name__ == '__main__':
    unittest.main()
