"""Requirement text above the documented soft budget is reported in one warning, without failing validation."""
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from catalog import RESOURCE_FILES
import validate
from validate import REQUIREMENTS_BUDGET, requirement_budget_warning

# Trimmed from more than 2,500 characters; they stay within the budget in both languages with unchanged item counts.
TRIMMED = ('baocut-slides-editor-case', 'leanrea-skill', 'pocket-tasks-reconstruction-case',
           'destiny2-build-86657-reconstruction-report-case', 'baocut-design-canvas-case',
           'crashlens-rea-crash-triage', 'hermes-rea-plugin', 'njfe-ear-camera-bridge-case',
           'universal-modder-agent-toolkit')


class RequirementBudgetTests(unittest.TestCase):
    def test_records_over_the_budget_are_named_longest_first_on_one_line(self):
        records = [{'id': 'short', 'requirements': ['x' * 200]},
                   {'id': 'at-budget', 'requirements': ['x' * (REQUIREMENTS_BUDGET - 100), 'y' * 100]},
                   {'id': 'long', 'requirements': ['x' * 1000, 'y' * 1000]},
                   {'id': 'longest-string', 'requirements': 'z' * 3000},
                   'not a record', {'id': 'no-requirements'}]
        warning = requirement_budget_warning(records)
        self.assertEqual(warning, '2 curated records exceed the 1,500-character requirements budget in '
                                  'data/README.md: longest-string (3,000), long (2,000)')
        self.assertNotIn('\n', warning)
        self.assertIsNone(requirement_budget_warning(records[:2]))

    def test_trimmed_records_stay_within_the_budget_in_both_languages(self):
        records = {record['id']: record for path in RESOURCE_FILES
                   for record in json.loads(path.read_text(encoding='utf-8'))}
        chinese = json.loads((ROOT / 'site/translations.zh-CN.json').read_text(encoding='utf-8'))
        for identifier in TRIMMED:
            with self.subTest(identifier=identifier):
                english = records[identifier]['requirements']
                self.assertLessEqual(sum(map(len, english)), REQUIREMENTS_BUDGET)
                # The Chinese list translates the same items, so it is shorter and has as many entries.
                self.assertEqual(len(chinese[identifier]['requirements']), len(english))
                self.assertLess(sum(map(len, chinese[identifier]['requirements'])), REQUIREMENTS_BUDGET)

    def test_validation_prints_the_warning_and_still_passes(self):
        stderr = io.StringIO()
        with patch.object(validate, 'requirement_budget_warning', return_value='fixture warning'), \
                contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(io.StringIO()):
            status = validate.main()
        self.assertEqual(status, 0, stderr.getvalue())
        self.assertIn('Warning: fixture warning', stderr.getvalue())


if __name__ == '__main__':
    unittest.main()
