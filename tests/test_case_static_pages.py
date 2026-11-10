"""/cases/ is split into static pages of at most CASE_PER_PAGE case rows that together list every case once."""
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from build_discovery_pages import CASE_PER_PAGE, build_discovery_pages, case_order, case_pages
from test_case_pages import resource
from validate_site import Page, schema_entities, validate_case_outputs, validate_section_target_counts, with_listing_pages

ORIGIN = 'https://awesomerea.org'
# The fixture's case count: CASE_PER_PAGE + 30 game cases and 40 protocol cases.
TOTAL = CASE_PER_PAGE + 70


class CaseStaticPagesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = TemporaryDirectory()
        output = cls.output = Path(cls.directory.name)
        (output / 'cases.css').write_bytes((ROOT / 'site/cases.css').read_bytes())
        # Game cases fill page 1 and spill onto page 2, where the protocol cases start.
        cls.resources = ([resource(f'game-{index:03}') for index in range(CASE_PER_PAGE + 30)]
                         + [resource(f'proto-{index:03}', targets=['protocol']) for index in range(40)]
                         + [resource('a-tool', kind='tool')])
        build_discovery_pages(output, {'resources': cls.resources, 'meta': {'site_url': ORIGIN}}, None)
        cls.pages = with_listing_pages({route: Page((output / route.lstrip('/') / 'index.html').read_text(encoding='utf-8'))
                                        for route in ('/cases/', '/zh/cases/')}, output)

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def html(self, route):
        return (self.output / route.lstrip('/') / 'index.html').read_text(encoding='utf-8')

    def test_pages_hold_at_most_per_page_rows_and_every_case_once(self):
        cases = [record['id'] for record in self.resources if record['kind'] == 'case-study']
        for prefix in ('', '/zh'):
            routes = [f'{prefix}/cases/', f'{prefix}/cases/page/2/']
            self.assertEqual(sorted(route for route in self.pages if route.startswith(f'{prefix}/cases/')), sorted(routes))
            listed = [row['id'] for route in routes for row in self.pages[route].case_rows]
            self.assertTrue(all(len(self.pages[route].case_rows) <= CASE_PER_PAGE for route in routes))
            self.assertEqual(sorted(listed), sorted(cases))
            self.assertEqual(listed, [record['id'] for _, _, record in case_order(self.resources)])
        validate_case_outputs(self.pages, self.resources)
        validate_section_target_counts(self.output, self.resources)

    def test_later_pages_are_indexed_with_their_own_address_items_and_twin(self):
        second = self.pages['/cases/page/2/']
        self.assertFalse(second.noindex or self.pages['/cases/'].noindex)
        self.assertEqual(second.canonicals, [ORIGIN + '/cases/page/2/'])
        self.assertEqual(dict(second.alternates)['zh-CN'], ORIGIN + '/zh/cases/page/2/')
        twin = (self.output / 'cases/page/2/index.md').read_text(encoding='utf-8')
        self.assertIn(f'<{ORIGIN}/cases/page/2/>', twin)
        self.assertEqual(twin.count('/index.md)'), len(second.case_rows))
        html = self.html('/cases/page/2/')
        self.assertIn('<a href="/cases/">Reverse-engineering case studies</a><span aria-hidden="true">/</span><span aria-current="page">Page 2</span>', html)
        self.assertIn('<h1>Reverse-engineering case studies<span', html)
        self.assertIn(f'Page 2 of 2, cases {CASE_PER_PAGE + 1}–{TOTAL}.', html)
        items = next(schema_entities(second.schemas, 'CollectionPage'))['mainEntity']
        self.assertEqual(items['numberOfItems'], len(second.case_rows))
        self.assertIn('· Page 2', self.html('/cases/page/2/').split('</title>')[0])
        self.assertIn('第 2 页', self.html('/zh/cases/page/2/').split('</title>')[0])

    def test_sections_keep_anchors_and_navigation_leads_to_their_page(self):
        anchors = case_pages(self.resources)
        later = next(key for key, page in anchors.items() if key.startswith('cases-') and page == 2 and key.count('-') == 1)
        first, second = self.html('/cases/'), self.html('/cases/page/2/')
        # Page 1 links the section that starts on page 2 and keeps its old fragment on that link.
        self.assertIn(f'href="/cases/page/2/#{later}" id="{later}"', first)
        self.assertIn(f'<section class="case-section" id="{later}"', second)
        # A section that runs onto page 2 keeps its anchor there; its count line stays on its first page.
        self.assertIn('id="cases-game"', second)
        self.assertEqual(first.count('data-section-target="game"'), 1)
        self.assertNotIn('data-section-target="game"', second)
        self.assertIn(f'data-section-count="{CASE_PER_PAGE + 30}"', second)

    def test_pager_and_range(self):
        first = self.html('/cases/')
        pager = re.search(r'<nav class="case-pager".*?</nav>', first).group(0)
        self.assertIn('href="/cases/page/2/" rel="next"', pager)
        self.assertIn('aria-current="page">1</a>', pager)
        self.assertIn(f'Cases 1–{CASE_PER_PAGE} of {TOTAL}', first)
        self.assertIn(f'第 {CASE_PER_PAGE + 1}–{TOTAL} 个案例，共 {TOTAL} 个', self.html('/zh/cases/page/2/'))

    def test_page_map_names_every_case(self):
        mapping = json.loads((self.output / 'cases/pages.json').read_text(encoding='utf-8'))
        for route in ('/cases/', '/cases/page/2/'):
            number = 1 if route == '/cases/' else 2
            self.assertTrue(all(mapping[row['id']] == number for row in self.pages[route].case_rows), route)

    def test_validator_checks_the_page_map(self):
        validate_case_outputs(self.pages, self.resources, self.output)
        path = self.output / 'cases/pages.json'
        original = path.read_text(encoding='utf-8')
        self.addCleanup(path.write_text, original, encoding='utf-8')
        mapping = json.loads(original)
        mapping['cases-protocol'] = 1
        path.write_text(json.dumps(mapping), encoding='utf-8')
        with self.assertRaises(AssertionError):
            validate_case_outputs(self.pages, self.resources, self.output)

    def test_validator_rejects_a_missing_page(self):
        pages = dict(self.pages)
        del pages['/zh/cases/page/2/']
        with self.assertRaises(AssertionError):
            validate_case_outputs(pages, self.resources)


if __name__ == '__main__':
    unittest.main()
