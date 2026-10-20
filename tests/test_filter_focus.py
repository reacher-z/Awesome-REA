"""Run the keyboard-focus checks for topic filtering and resets through the actual homepage script."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FilterFocusTests(unittest.TestCase):
    def check_group(self, group):
        result = subprocess.run(['node', str(ROOT / 'tests/filter_focus_ui.cjs'), group],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Filter focus passed: ' + group, result.stdout)

    def test_keyboard_topic_chip_focuses_the_topic_field(self):
        self.check_group('topicChipFocusesTheTopicField')

    def test_keyboard_resets_return_to_the_collection_search(self):
        self.check_group('resetsReturnToTheCollectionSearch')

    def test_show_more_keeps_its_own_behaviour(self):
        self.check_group('showMoreKeepsItsOwnBehaviour')


if __name__ == '__main__':
    unittest.main()
