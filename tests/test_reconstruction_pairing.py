"""Independent reconstruction projects and the reconstruction-cases category are validated as a pair."""
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


class ReconstructionPairingTests(unittest.TestCase):
    def test_either_value_without_the_other_is_rejected_with_the_resource_id(self):
        case = next(record for record in curated_records() if record['relationship'] == 'independent-reconstruction')
        for changes, message in (
            ({'id': 'reconstruction-game-fixture', 'category': 'game-analysis'},
             "relationship 'independent-reconstruction' requires category 'reconstruction-cases'"),
            ({'id': 'reconstruction-tool-fixture', 'relationship': 'foundation', 'kind': 'tool'},
             "category 'reconstruction-cases' requires relationship 'independent-reconstruction'"),
        ):
            with self.subTest(changes=changes):
                record = deepcopy(case) | changes
                before = deepcopy(record)
                errors = []
                validate_resources([record], errors)
                self.assertEqual(errors, [f"resource {changes['id']!r}: {message}"])
                # Neither value is inferred or rewritten.
                self.assertEqual(record, before)
        # The trusted pull-request review applies the same shared validator.
        self.assertIs(review_pr.validate_resources, validate_resources)

    def test_current_curated_records_pass_unchanged(self):
        records = curated_records()
        before = deepcopy(records)
        errors = []
        validate_resources(records, errors)
        self.assertEqual([error for error in errors if 'reconstruction' in error], [])
        self.assertEqual(records, before)
        cases = [record for record in records if record['relationship'] == 'independent-reconstruction']
        self.assertTrue(cases)
        self.assertEqual(cases, [record for record in records if record['category'] == 'reconstruction-cases'])


if __name__ == '__main__':
    unittest.main()
