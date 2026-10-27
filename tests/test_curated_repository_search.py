"""Check that curated homepage search finds entries by their GitHub owner/repo."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CuratedRepositorySearchTests(unittest.TestCase):
    def check_group(self, group):
        result = subprocess.run(['node', str(ROOT / 'tests/curated_repository_search_ui.cjs'), group],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Curated repository search passed: ' + group, result.stdout)

    def test_owner_and_repository_queries_without_visible_text(self):
        self.check_group('fixtures')

    def test_published_catalog_owner_and_repository_queries(self):
        self.check_group('catalog')


if __name__ == '__main__':
    unittest.main()
