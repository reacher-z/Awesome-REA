"""Repository category pages carry their category into the interactive search, which validates it against the same labels."""
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
from build_repository_index import CATEGORIES
from homepage_locales import localized_homepage

HTML = (ROOT / 'site/index.html').read_text(encoding='utf-8')
APP = (ROOT / 'site/app.js').read_text(encoding='utf-8')


class SourceCategoryTests(unittest.TestCase):
    def test_browser_filter(self):
        result = subprocess.run(['node', str(ROOT / 'tests/source_category_ui.cjs')], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Repository category checks passed', result.stdout)

    def test_select_is_labelled_in_both_languages(self):
        self.assertIn('<label for="source-category" data-i18n="categoryLabel">Category</label><select id="source-category"><option value="all" data-i18n="allCategories">All categories</option></select>', HTML)
        chinese = localized_homepage(HTML, APP, 'zh')
        self.assertIn('<label for="source-category" data-i18n="categoryLabel">类别</label>', chinese)
        self.assertIn('<option value="all" data-i18n="allCategories">所有类别</option>', chinese)

    def test_built_category_pages_link_to_their_category(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'dist'
            build_site.build_site(output)
            catalog = json.loads((output / 'catalog.json').read_text(encoding='utf-8'))
            self.assertEqual(catalog['source_category_labels'], {key: list(value) for key, value in CATEGORIES.items()})
            browser = json.loads((output / 'source-browser.json').read_text(encoding='utf-8'))
            self.assertTrue({record['category'] for record in browser['resources']} <= set(CATEGORIES))
            for language, prefix, search in (('en', '', '/?view=source-index&amp;lang=en'), ('zh', 'zh/', '/zh/?view=source-index')):
                overview = (output / prefix / 'browse/index.html').read_text(encoding='utf-8')
                self.assertIn(f'<a class="button button-primary" href="{search}">', overview)
                for category in CATEGORIES:
                    with self.subTest(language=language, category=category):
                        html = (output / prefix / 'browse' / category / 'index.html').read_text(encoding='utf-8')
                        links = re.findall(r'<div class="browse-actions"><a class="button button-primary" href="([^"]+)">', html)
                        self.assertEqual(links, [f'{search}&amp;source-category={category}'])


if __name__ == '__main__':
    unittest.main()
