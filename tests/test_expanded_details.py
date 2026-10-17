"""Run the homepage details-restoration contract in Node, as CI does for other UI fixtures."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ExpandedDetailsTests(unittest.TestCase):
    def test_details_restore_without_has_selector_support(self):
        result = subprocess.run(['node', str(ROOT / 'tests/expanded_details_ui.cjs')], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
