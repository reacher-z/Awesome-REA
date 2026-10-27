"""Check that curated homepage search ranks name matches before text-only matches without dropping any."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CuratedSearchRankTests(unittest.TestCase):
    def check_group(self, group):
        result = subprocess.run(['node', str(ROOT / 'tests/curated_search_rank_ui.cjs'), group],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Curated search ranking passed: ' + group, result.stdout)

    def test_field_order_word_starts_whole_names_and_empty_query(self):
        self.check_group('english')

    def test_chinese_query_on_the_chinese_homepage(self):
        self.check_group('chinese')

    def test_published_catalog_queries_on_both_homepages(self):
        self.check_group('catalog')


if __name__ == '__main__':
    unittest.main()
