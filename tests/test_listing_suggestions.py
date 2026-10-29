"""Static curated and case listings link the existing suggestion forms in both languages."""
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from build_discovery_pages import build_discovery_pages
# A module import keeps that file's test case out of this module's discovery.
import test_case_pages as cases
from validate_site import Page, validate_suggestion_links

FORMS = 'https://github.com/reacher-z/Awesome-REA/issues/new?template='


class ListingSuggestionTests(unittest.TestCase):
    def test_resource_and_case_listings_link_their_forms(self):
        with TemporaryDirectory() as directory:
            output = Path(directory)
            (output / 'cases.css').write_bytes((ROOT / 'site/cases.css').read_bytes())
            build_discovery_pages(output, {'resources': [cases.resource('alpha'), cases.resource('tool', kind='tool')],
                                           'meta': {'site_url': 'https://awesomerea.org'}}, None)
            expected = {
                '/resources/': ('resource.yml', 'Suggest a resource'), '/zh/resources/': ('resource.yml', '推荐资源'),
                '/cases/': ('case-study.yml', 'Suggest a case study'), '/zh/cases/': ('case-study.yml', '推荐重建案例'),
            }
            pages = {}
            for route, (template, label) in expected.items():
                text = (output / route.lstrip('/') / 'index.html').read_text(encoding='utf-8')
                pages[route] = Page(text)
                link = f'<a class="button button-outline" href="{FORMS}{template}" target="_blank" rel="noopener">{label} <span aria-hidden="true">↗</span></a>'
                self.assertEqual(text.count(link), 1, route)
                actions = text[text.index('<div class="browse-actions">'):]
                self.assertIn(link, actions[:actions.index('</div>')])
                self.assertTrue((ROOT / '.github/ISSUE_TEMPLATE' / template).is_file())
            for route in ('/papers/', '/zh/papers/'):
                pages[route] = Page(f'<a href="{FORMS}paper.yml">x</a>')
            validate_suggestion_links(pages)
            pages['/zh/cases/'] = Page('<a href="/cases/">x</a>')
            with self.assertRaisesRegex(AssertionError, '/zh/cases/'):
                validate_suggestion_links(pages)


if __name__ == '__main__':
    unittest.main()
