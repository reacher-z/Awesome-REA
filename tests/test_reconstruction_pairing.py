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
from validate import RECONSTRUCTION_FILE, validate_resource_file, validate_resources


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


class ReconstructionFileTests(unittest.TestCase):
    def test_every_reconstruction_case_lives_in_the_tool_catalog(self):
        self.assertEqual(RECONSTRUCTION_FILE, 'data/tool-resources.json')
        for path in RESOURCE_FILES:
            records = json.loads(path.read_text(encoding='utf-8'))
            errors = []
            validate_resource_file(path.relative_to(ROOT).as_posix(), records, errors)
            self.assertEqual(errors, [])
            cases = [record['id'] for record in records if record['relationship'] == 'independent-reconstruction']
            self.assertEqual(bool(cases), path.name == 'tool-resources.json', path.name)

    def test_a_reconstruction_case_in_the_rea_catalog_is_rejected_locally_and_in_review(self):
        case = next(record for record in curated_records() if record['relationship'] == 'independent-reconstruction')
        errors = []
        validate_resource_file('data/rea-resources.json', [case, {'relationship': 'official-guide'}, 'not a record'], errors)
        self.assertEqual(errors, [f"resource {case['id']!r}: relationship 'independent-reconstruction' records belong in "
                                  "data/tool-resources.json, not data/rea-resources.json"])
        # Catalog changes also recheck the case ledger's mappings, which read the bibliography.
        contents = {name: (ROOT / name).read_text(encoding='utf-8')
                    for name in (*review_pr.CATALOGS, 'data/papers.json', review_pr.CASE_COVERAGE)}
        rea = json.loads(contents['data/rea-resources.json'])
        tool = [record for record in json.loads(contents['data/tool-resources.json']) if record['id'] != case['id']]
        moved = contents | {'data/rea-resources.json': json.dumps(rea + [case]), 'data/tool-resources.json': json.dumps(tool)}
        review_errors, _ = review_pr.review_data(moved, {'data/rea-resources.json', 'data/tool-resources.json'})
        self.assertEqual(review_errors, errors[:1])
        review_errors, _ = review_pr.review_data(contents, {'data/rea-resources.json'})
        self.assertEqual(review_errors, [])


if __name__ == '__main__':
    unittest.main()
