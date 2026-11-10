"""/resources/ is split into static pages of at most PER_PAGE rows that together list every record once."""
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from build_discovery_pages import build_discovery_pages
from resource_listing import PER_PAGE, page_path, section_href
from test_case_pages import resource
from validate_site import Page, schema_entities, validate_resource_listing, with_resource_pages

ORIGIN = 'https://awesomerea.org'


class ResourcePagesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = TemporaryDirectory()
        output = cls.output = Path(cls.directory.name)
        (output / 'cases.css').write_bytes((ROOT / 'site/cases.css').read_bytes())
        # Two sections: the first fills page 1 and spills onto page 2, where the second starts.
        cls.resources = ([resource(f'web-{index:03}', kind='tool', targets=['website'], category='web-analysis') for index in range(PER_PAGE + 20)]
                         + [resource(f'game-{index:03}', kind='tool') for index in range(PER_PAGE + 5)])
        build_discovery_pages(output, {'resources': cls.resources, 'meta': {'site_url': ORIGIN}}, None)
        cls.pages = with_resource_pages({route: Page((output / route.lstrip('/') / 'index.html').read_text(encoding='utf-8'))
                                         for route in ('/resources/', '/zh/resources/')}, output)

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def html(self, route):
        return (self.output / route.lstrip('/') / 'index.html').read_text(encoding='utf-8')

    def test_pages_hold_at_most_per_page_rows_and_every_record_once(self):
        total = len(self.resources)
        expected_pages = -(-total // PER_PAGE)
        for prefix in ('', '/zh'):
            routes = [f'{prefix}/resources/'] + [f'{prefix}/resources/page/{n}/' for n in range(2, expected_pages + 1)]
            self.assertEqual(sorted(route for route in self.pages if route.startswith(f'{prefix}/resources/')), sorted(routes))
            listed = [identifier for route in routes for identifier in self.pages[route].record_ids]
            self.assertTrue(all(len(self.pages[route].record_ids) <= PER_PAGE for route in routes))
            self.assertEqual(sorted(listed), sorted(record['id'] for record in self.resources))
            self.assertFalse((self.output / f'{prefix.lstrip("/")}/resources/page/{expected_pages + 1}'.lstrip('/')).exists())
        validate_resource_listing(self.pages, self.resources)

    def test_later_pages_are_noindex_and_list_only_their_rows(self):
        first, second = self.pages['/resources/'], self.pages['/resources/page/2/']
        self.assertFalse(first.noindex)
        self.assertTrue(second.noindex)
        items = next(schema_entities(second.schemas, 'CollectionPage'))['mainEntity']
        self.assertEqual(items['numberOfItems'], len(second.record_ids))
        self.assertIn('page 2', self.html('/resources/page/2/').split('</title>')[0])
        self.assertIn('第 2 页', self.html('/zh/resources/page/2/').split('</title>')[0])

    def test_pager_links_static_pages_without_a_script(self):
        html = self.html('/resources/')
        pager = re.search(r'<nav class="pager pager-static"[^>]*>.*?</nav>', html).group(0)
        self.assertIn('href="/resources/page/2/" data-page="2" rel="next"', pager)
        self.assertIn('aria-current="page">1</a>', pager)
        zh = re.search(r'<nav class="pager pager-static"[^>]*>.*?</nav>', self.html('/zh/resources/page/2/')).group(0)
        self.assertIn('href="/zh/resources/" data-page="1" rel="prev"', zh)

    def test_section_anchors_live_on_the_page_where_the_section_starts(self):
        first, second = self.html('/resources/'), self.html('/resources/page/2/')
        mapping = json.loads((self.output / 'resources/pages.json').read_text(encoding='utf-8'))
        starts = {key.removeprefix('heading-'): page for key, page in mapping.items() if key.startswith('heading-')}
        self.assertEqual(sorted(starts.values()), [1, 2])
        later = next(key for key, page in starts.items() if page == 2)
        earlier = next(key for key, page in starts.items() if page == 1)
        # Page 1 links the section that starts on page 2 and keeps that section's old fragment on the link.
        self.assertIn(f'href="{section_href(later, 2, "en")}" id="{later}"', first)
        self.assertNotIn(f'id="heading-{later}"', first)
        self.assertIn(f'id="heading-{later}"', second)
        self.assertIn(f'<a id="{later}"></a>', second)
        # The earlier section continues on page 2 under a heading without anchors.
        self.assertIn(f'id="heading-{earlier}"', first)
        self.assertNotIn(f'id="heading-{earlier}"', second)
        self.assertEqual(page_path(2, 'zh'), '/zh/resources/page/2/')

    def test_page_map_names_every_record(self):
        mapping = json.loads((self.output / 'resources/pages.json').read_text(encoding='utf-8'))
        for route, page in self.pages.items():
            number = 1 if 'page/' not in route else int(route.rstrip('/').rsplit('/', 1)[1])
            self.assertTrue(all(mapping[identifier] == number for identifier in page.record_ids), route)

    def test_validator_rejects_a_missing_page(self):
        pages = dict(self.pages)
        del pages['/resources/page/2/']
        with self.assertRaises(AssertionError):
            validate_resource_listing(pages, self.resources)


if __name__ == '__main__':
    unittest.main()
