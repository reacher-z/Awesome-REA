"""Run the offline repository-browser logic checks for site/app.js in Node, as CI does for other UI fixtures."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AppLogicTests(unittest.TestCase):
    def test_integrity_guard_related_entries_sorts_topics_and_show_more(self):
        result = subprocess.run(['node', str(ROOT / 'tests/app_logic_ui.cjs')], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Repository browser logic passed', result.stdout)


if __name__ == '__main__':
    unittest.main()
