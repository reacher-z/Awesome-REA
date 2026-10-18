"""Exercise homepage URL behavior through the actual app in the offline VM."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class HomepageURLTests(unittest.TestCase):
    def check_group(self, group):
        result = subprocess.run(['node', str(ROOT / 'tests/homepage_url_ui.cjs'), group],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Homepage URL state passed: ' + group, result.stdout)

    def test_bare_defaults_and_literal_queries(self):
        self.check_group('defaults')

    def test_rejected_values_normalize_once_after_load(self):
        self.check_group('rejected')

    def test_legacy_language_view_layout_and_sort_links(self):
        self.check_group('legacy')

    def test_valid_inactive_filters_and_unrelated_url_parts(self):
        self.check_group('inactive')

    def test_language_links_follow_url_state_and_fragment(self):
        self.check_group('languageLinks')

    def test_same_query_repository_handoff_and_reset(self):
        self.check_group('handoff')


if __name__ == '__main__':
    unittest.main()
