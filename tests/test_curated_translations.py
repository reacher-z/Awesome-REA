"""Curated Chinese names and requirements are validated as trusted data, locally and in PR review."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from curated_translations import CURATED_TRANSLATIONS, read_curated_translations, validate_curated_translations
import review_pr
import validate

RECORDS = [{'id': 'ghidra', 'name': 'Ghidra'}, {'id': 'rea-lab', 'name': 'rea-lab'}, {'id': 'frida', 'name': 'Frida'}]
TRANSLATIONS = {
    'ghidra': {'name': 'Ghidra 逆向工程框架', 'requirements': ['Java 21', '需要 Ghidra 11 或更高版本。']},
    'rea-lab': {'name': 'rea-lab', 'requirements': ['需要 REA。']},  # An unchanged proper name.
    'frida': {'requirements': ['需要 Python 3。']},  # Without a name, the English name is kept.
}
PIN = '0123456789abcdef0123456789abcdef01234567'


def errors_for(translations, records=RECORDS, **options):
    errors = []
    validate_curated_translations(records, translations, errors, **options)
    return errors


class CuratedTranslationValidatorTests(unittest.TestCase):
    def test_existing_shapes_pass(self):
        self.assertEqual(errors_for(TRANSLATIONS), [])

    def test_missing_and_unknown_ids_are_reported_by_id(self):
        translations = {key: value for key, value in TRANSLATIONS.items() if key != 'frida'}
        translations['ghidar'] = {'requirements': ['需要 Java。']}
        self.assertEqual(errors_for(translations), [
            f"{CURATED_TRANSLATIONS}: no Chinese name/requirements entry for 1 curated resource(s): 'frida'",
            f"{CURATED_TRANSLATIONS}: 1 entry ID(s) name no curated resource: 'ghidar'",
        ])
        many = errors_for({}, [{'id': f'tool-{index:02}'} for index in range(12)])
        self.assertEqual(len(many), 1)
        self.assertTrue(many[0].endswith("'tool-09' and 2 more"))

    def test_ids_known_to_the_base_branch_are_not_coverage_findings(self):
        stale = {key: value for key, value in TRANSLATIONS.items() if key != 'frida'}
        stale['removed-on-base'] = {'requirements': ['需要 Java。']}
        self.assertEqual(errors_for(stale, known_ids={'frida', 'removed-on-base'}), [])
        # A record the PR adds still needs its entry.
        added = [*RECORDS, {'id': 'new-tool', 'name': 'New tool'}]
        self.assertEqual(errors_for(TRANSLATIONS, added, known_ids={'ghidra', 'rea-lab', 'frida'}),
                         [f"{CURATED_TRANSLATIONS}: no Chinese name/requirements entry for 1 curated resource(s): 'new-tool'"])

    def test_malformed_entries_are_reported(self):
        where = f"{CURATED_TRANSLATIONS}: entry 'ghidra'"
        cases = {
            'not an object': (['需要 Java。'], [f'{where} must be an object']),
            'unsupported field': ({'requirements': ['需要 Java。'], 'requirementz': 'x'},
                                  [f'{where} has unsupported fields requirementz']),
            'empty name': ({'name': ' ', 'requirements': ['需要 Java。']}, [f'{where}.name must be a nonempty string']),
        }
        requirement_error = [f'{where}.requirements must be a nonempty list of nonempty strings']
        # English requirements are lists (data/README.md), so a single string is rejected here too.
        for label, value in {'missing': {}, 'string': {'requirements': '需要 Java。'}, 'empty list': {'requirements': []}, 'empty item': {'requirements': ['需要 Java。', '']},
                             'number': {'requirements': 3}, 'nested list': {'requirements': [['需要 Java。']]}}.items():
            cases[f'requirements {label}'] = (value, requirement_error)
        for label, (value, expected) in cases.items():
            with self.subTest(label):
                self.assertEqual(errors_for(TRANSLATIONS | {'ghidra': value}), expected)
        self.assertEqual(errors_for([]), [f'{CURATED_TRANSLATIONS}: expected an object keyed by curated resource ID'])

    def test_reading_is_strict(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / CURATED_TRANSLATIONS
            path.parent.mkdir()
            path.write_text('{"ghidra": {"requirements": "a"}, "ghidra": {"requirements": "b"}}', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
                read_curated_translations(directory)

    def test_local_validation_and_review_share_the_validator(self):
        self.assertIs(validate.validate_curated_translations, validate_curated_translations)
        self.assertIs(review_pr.validate_curated_translations, validate_curated_translations)
        self.assertIn(CURATED_TRANSLATIONS, review_pr.REVIEW_FILES)


class CuratedTranslationReviewTests(unittest.TestCase):
    def review(self, head):
        """Review a PR that changes only the translations, using fixture base data and no PR code."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for filename, value in ((review_pr.CATALOGS[0], RECORDS[:2]), (review_pr.CATALOGS[1], RECORDS[2:]),
                                    (CURATED_TRANSLATIONS, TRANSLATIONS)):
                (root / filename).parent.mkdir(parents=True, exist_ok=True)
                (root / filename).write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')
            errors = []
            changed = {CURATED_TRANSLATIONS}
            with patch.object(review_pr, 'ROOT', root), patch.object(review_pr, 'content_at', return_value=head) as fetch:
                contents = review_pr.load_review_contents('example/repo', PIN, 'mock', [], changed, errors)
                fetch.assert_called_once_with('example/repo', CURATED_TRANSLATIONS, PIN, 'mock')
                findings, reviewed = review_pr.review_data(contents, changed)
        return errors + findings, reviewed

    def test_valid_change_passes_and_is_reported_as_checked(self):
        findings, reviewed = self.review(json.dumps(TRANSLATIONS | {'frida': {'requirements': ['需要 Python 3.10+。']}}))
        self.assertEqual(findings, [])
        self.assertTrue(any('Chinese resource names and requirements checked' in line for line in reviewed))

    def test_unknown_ids_and_malformed_requirements_fail_review(self):
        head = TRANSLATIONS | {'frida': {'requirements': []}, 'not-a-record': {'requirements': ['需要 Java。']}}
        self.assertEqual(self.review(json.dumps(head, ensure_ascii=False))[0], [
            f"{CURATED_TRANSLATIONS}: 1 entry ID(s) name no curated resource: 'not-a-record'",
            f"{CURATED_TRANSLATIONS}: entry 'frida'.requirements must be a nonempty list of nonempty strings",
        ])

    def test_full_json_is_privacy_checked_even_without_a_diff(self):
        escaped = '\\u0067hp_' + 'A' * 36  # A token-shaped value hidden by a JSON escape.
        head = json.dumps(TRANSLATIONS, ensure_ascii=False).replace('需要 REA。', escaped)
        findings = self.review(head)[0]
        self.assertTrue(any('decoded JSON string' in finding and "record rea-lab" in finding for finding in findings), findings)
        self.assertFalse(any('ghp_' in finding for finding in findings))


if __name__ == '__main__':
    unittest.main()
