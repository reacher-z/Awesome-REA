"""Local validation, trusted PR review and scan resume share one strict JSON parser."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import review_pr
import scan_sources
import strict_json
import validate

NESTED_DUPLICATE = '[{"id": "fixture", "citation": {"pages": "1", "pages": "2"}}]'
INVALID = {
    'nested duplicate key': NESTED_DUPLICATE,
    'top-level duplicate key': '{"meta": {}, "meta": {}}',
    'NaN': '[{"stars": NaN}]',
    'Infinity': '[{"stars": Infinity}]',
    'negative Infinity': '[{"stars": -Infinity}]',
}


class StrictJSONTests(unittest.TestCase):
    def test_duplicate_keys_and_non_finite_numbers_are_rejected(self):
        for label, text in INVALID.items():
            with self.subTest(label), self.assertRaises(ValueError):
                strict_json.loads(text)
        with self.assertRaisesRegex(ValueError, "duplicate JSON key 'pages'"):
            strict_json.loads(NESTED_DUPLICATE)

    def test_valid_unicode_and_repeated_keys_in_separate_objects_parse(self):
        text = '[{"name": "逆向工程", "note": "\\u9006\\u5411 \\ud83d\\udd0d café"}, {"name": "second"}]'
        self.assertEqual(strict_json.loads(text), [{'name': '逆向工程', 'note': '逆向 \U0001F50D café'}, {'name': 'second'}])
        self.assertEqual(strict_json.loads(text.encode('utf-8')), strict_json.loads(text))

    def test_file_errors_name_the_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'catalog.json'
            path.write_text(NESTED_DUPLICATE, encoding='utf-8')
            with self.assertRaisesRegex(ValueError, r'catalog\.json: duplicate JSON key'):
                strict_json.load_path(path)

    def test_local_catalog_validation_reports_the_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for label, text in INVALID.items():
                with self.subTest(label):
                    path = root / 'data' / 'tool-resources.json'
                    path.parent.mkdir(exist_ok=True)
                    path.write_text(text, encoding='utf-8')
                    errors = []
                    with patch.object(validate, 'ROOT', root):
                        self.assertEqual(validate.read_array(path, errors), [])
                    self.assertEqual(len(errors), 1)
                    self.assertTrue(errors[0].startswith('data/tool-resources.json: cannot read strict JSON: '))

    def test_pull_request_review_reports_the_file_without_echoing_its_content(self):
        for label, text in INVALID.items():
            with self.subTest(label):
                contents = {review_pr.CATALOGS[0]: '[]', review_pr.CATALOGS[1]: text}
                with self.assertRaises(review_pr.InvalidJSON) as raised:
                    review_pr.review_data(contents, {review_pr.CATALOGS[1]})
                self.assertEqual(str(raised.exception), f'{review_pr.CATALOGS[1]}: expected strict JSON without duplicate keys or NaN/Infinity.')
        # Privacy scanning still falls back to the raw text for input it cannot parse.
        self.assertEqual(review_pr.json_privacy_findings('data/papers.json', NESTED_DUPLICATE), [])

    def test_resume_snapshot_is_parsed_strictly_before_any_request(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'snapshot.json'
            path.write_text('{"meta": {"queries": []}, "resources": [], "resources": [], "failures": []}', encoding='utf-8')
            with patch.object(scan_sources, 'GitHub', side_effect=AssertionError('network client created')):
                with self.assertRaisesRegex(ValueError, r'snapshot\.json: duplicate JSON key'):
                    scan_sources.load_resume(path)


if __name__ == '__main__':
    unittest.main()
