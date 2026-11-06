"""Run the homepage Back/Forward checks through the actual app.js in the offline VM."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FilterHistoryTests(unittest.TestCase):
    def check_group(self, group):
        result = subprocess.run(['node', str(ROOT / 'tests/filter_history_ui.cjs'), group],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Filter history passed: ' + group, result.stdout)

    def test_discrete_changes_add_entries_and_traverse_in_both_views(self):
        self.check_group('discreteChangesAddEntries')

    def test_typing_topic_and_layout_replace_the_current_entry(self):
        self.check_group('typingReplacesTheCurrentEntry')

    def test_clear_and_reset_can_be_undone_with_back(self):
        self.check_group('resetsAreUndoable')

    def test_fragment_entries_keep_results(self):
        self.check_group('fragmentEntriesKeepResults')

    def test_malformed_entries_use_safe_defaults_without_new_entries(self):
        self.check_group('malformedEntriesUseSafeDefaults')


if __name__ == '__main__':
    unittest.main()
