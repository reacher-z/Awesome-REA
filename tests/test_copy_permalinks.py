"""Copy link targets exist: entry pages for curated resources and papers, category-page cards for repositories."""
from pathlib import Path
import json
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_site

SLUG = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')


class CopyPermalinkTests(unittest.TestCase):
    def test_browser_copy_actions(self):
        result = subprocess.run(['node', str(ROOT / 'tests/copy_permalinks_ui.cjs')], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Copy link checks passed', result.stdout)

    def test_every_copyable_link_resolves_in_both_languages(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'dist'
            build_site.build_site(output)
            catalog = json.loads((output / 'catalog.json').read_text(encoding='utf-8'))
            papers = json.loads((output / 'papers.json').read_text(encoding='utf-8'))
            browser = json.loads((output / 'source-browser.json').read_text(encoding='utf-8'))
            for prefix in ('', 'zh/'):
                for record in catalog['resources']:
                    self.assertTrue(SLUG.match(record['id']) and (output / prefix / 'resources' / record['id'] / 'index.html').is_file(), record['id'])
                for paper in papers:
                    self.assertTrue(paper['id'].startswith('paper-') and (output / prefix / 'papers' / paper['id'] / 'index.html').is_file(), paper['id'])
                pages = {}
                for record in browser['resources']:
                    with self.subTest(prefix=prefix, record=record['id']):
                        self.assertTrue(SLUG.match(record['id']) and SLUG.match(record['category']))
                        if record['category'] not in pages:
                            pages[record['category']] = (output / prefix / 'browse' / record['category'] / 'index.html').read_text(encoding='utf-8')
                        self.assertIn(f' id="{record["id"]}"', pages[record['category']])


if __name__ == '__main__':
    unittest.main()
