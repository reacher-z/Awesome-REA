"""English requirements are always a list of nonempty strings, like their Chinese translations."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from catalog import RESOURCE_FILES
import review_pr
from validate import validate_resources


def curated_records():
    return [record for path in RESOURCE_FILES for record in json.loads(path.read_text(encoding='utf-8'))]


class RequirementListTests(unittest.TestCase):
    def test_strings_and_empty_items_are_rejected_locally_and_in_review(self):
        record = next(record for record in curated_records() if record['id'] == 'ghidra')
        for value in ('Java 21', [], ['Java 21', ' '], [21]):
            with self.subTest(value=value):
                errors = []
                validate_resources([deepcopy(record) | {'requirements': value}], errors)
                self.assertEqual(errors, ["resource 'ghidra'.requirements: use a nonempty list of nonempty strings"])
        self.assertIs(review_pr.validate_resources, validate_resources)

    def test_formerly_single_string_requirements_are_one_item_lists(self):
        # Each was one string with a one-item Chinese list, so wrapping it left the rendered text unchanged.
        translations = json.loads((ROOT / 'site/translations.zh-CN.json').read_text(encoding='utf-8'))
        records = {record['id']: record for record in curated_records()}
        for identifier in ('ghidra', 'awesome-rea-cases'):
            with self.subTest(record=identifier):
                self.assertEqual(len(records[identifier]['requirements']), 1)
                self.assertEqual(len(translations[identifier]['requirements']), 1)


if __name__ == '__main__':
    unittest.main()
