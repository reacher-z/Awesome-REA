"""Listing and directory pages publish a BreadcrumbList matching their visible breadcrumb."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from build_browse_pages import CATEGORIES, build_browse_pages
from build_discovery_pages import build_discovery_pages
from build_entry_pages import build_entry_pages
from build_paper_pages import build_paper_pages
from test_site_metadata import CARD, ORIGIN, resource
from test_source_browser import full_export
from validate_site import Page, schema_entities, validate_breadcrumbs


class BreadcrumbSchemaTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.output = Path(directory.name)
        papers = json.loads((ROOT / 'data/papers.json').read_text())
        build_browse_pages(self.output, full_export(), curated_count=1, site_url=ORIGIN,
                           repository_url='https://github.com/reacher-z/Awesome-REA', styles_href='/styles.css',
                           browse_styles_href='/browse.css', favicon_href='/favicon.svg',
                           social_image_href=CARD, data_revision='0' * 16)
        build_discovery_pages(self.output, {'resources': [resource()], 'meta': {}}, None)
        build_paper_pages(self.output, papers, social_image_href=CARD)
        build_entry_pages(self.output, [resource()], papers[:1], social_image_href=CARD)
        self.pages = {'/' + path.parent.relative_to(self.output).as_posix() + '/': Page(path.read_text(encoding='utf-8'))
                      for path in self.output.rglob('index.html')}

    def trail(self, route):
        items = next(schema_entities(self.pages[route].schemas, 'BreadcrumbList'))['itemListElement']
        return [(item['name'], item['item']) for item in items]

    def test_every_visible_breadcrumb_has_a_matching_list(self):
        validate_breadcrumbs(self.output, self.pages)
        self.assertEqual(self.trail('/browse/web-analysis/'), [
            ('Home', ORIGIN + '/'), ('All categories', ORIGIN + '/browse/'),
            (CATEGORIES['web-analysis'][0], ORIGIN + '/browse/web-analysis/')])
        self.assertEqual(self.trail('/zh/browse/web-analysis/'), [
            ('首页', ORIGIN + '/zh/'), ('全部分类', ORIGIN + '/zh/browse/'),
            (CATEGORIES['web-analysis'][1], ORIGIN + '/zh/browse/web-analysis/')])
        self.assertEqual(self.trail('/zh/browse/'), [('首页', ORIGIN + '/zh/'), ('全部分类', ORIGIN + '/zh/browse/')])
        self.assertEqual(self.trail('/papers/'), [('Home', ORIGIN + '/'), ('Reverse engineering papers & benchmarks', ORIGIN + '/papers/')])
        for route in ('/resources/', '/zh/cases/', '/about/'):
            trail = self.trail(route)
            self.assertEqual(len(trail), 2)
            self.assertEqual(trail[-1][1], ORIGIN + route)
        # The CollectionPage keeps its own JSON-LD block and contents.
        page = self.pages['/browse/web-analysis/']
        self.assertEqual([schema['@type'] for schema in page.schemas], ['CollectionPage', 'BreadcrumbList'])
        self.assertNotIn('breadcrumb', page.schemas[0])

    def test_validator_rejects_missing_or_mismatched_lists(self):
        for route, mutate in (('/browse/web-analysis/', lambda schemas: schemas.pop()),
                              ('/zh/browse/firmware/', lambda schemas: schemas[1]['itemListElement'][1].update(name='All categories')),
                              ('/papers/', lambda schemas: schemas[1]['itemListElement'][0].update(item=ORIGIN + '/zh/')),
                              ('/about/', lambda schemas: schemas[1]['itemListElement'].reverse())):
            pages = deepcopy(self.pages)
            mutate(pages[route].schemas)
            with self.subTest(route=route), self.assertRaises(AssertionError):
                validate_breadcrumbs(self.output, pages)


if __name__ == '__main__':
    unittest.main()
