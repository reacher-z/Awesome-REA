"""Run the removable active-filter checks through the actual homepage script in the offline VM."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ActiveFilterTests(unittest.TestCase):
    def check_group(self, group):
        result = subprocess.run(['node', str(ROOT / 'tests/active_filters_ui.cjs'), group],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Active filters passed: ' + group, result.stdout)

    def test_curated_chips_remove_one_constraint_and_move_focus(self):
        self.check_group('curatedChipsRemoveOneConstraint')

    def test_chinese_labels_and_language_switch(self):
        self.check_group('chineseLabelsAndLanguageSwitch')

    def test_zero_results_keep_every_constraint(self):
        self.check_group('zeroResultsKeepEveryConstraint')

    def test_repository_chips_keep_sort_and_other_filters(self):
        self.check_group('repositoryChipsKeepSortAndOtherFilters')

    def test_both_views_have_a_labelled_chip_list(self):
        html = (ROOT / 'site/index.html').read_text(encoding='utf-8')
        for identifier in ('active-filters', 'source-active-filters'):
            self.assertIn(f'<ul id="{identifier}" class="active-filters" aria-label="Active filters" '
                          'data-i18n-aria="activeFilters" hidden></ul>', html)


if __name__ == '__main__':
    unittest.main()
