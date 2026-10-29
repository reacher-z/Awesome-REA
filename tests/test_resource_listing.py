"""The /resources/ ItemList identifies the site's detail pages; card titles still link upstream."""
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from build_discovery_pages import build_discovery_pages
from test_case_pages import resource
from validate_site import Page, schema_entities, validate_resource_listing

ORIGIN = 'https://awesomerea.org'


class ResourceListingTests(unittest.TestCase):
    def build(self, resources):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        output = Path(directory.name)
        (output / 'cases.css').write_bytes((ROOT / 'site/cases.css').read_bytes())
        build_discovery_pages(output, {'resources': resources, 'meta': {'site_url': ORIGIN}}, None)
        return {route: Page((output / route.lstrip('/') / 'index.html').read_text(encoding='utf-8'))
                for route in ('/resources/', '/zh/resources/')}

    def test_items_point_at_localized_detail_pages_in_card_order(self):
        resources = [resource('game-tool', kind='tool'), resource('web-case', targets=['website']),
                     resource('game-case')]
        pages = self.build(resources)
        validate_resource_listing(pages, resources)
        for language, prefix in (('en', ''), ('zh', '/zh')):
            page = pages[prefix + '/resources/']
            items = next(schema_entities(page.schemas, 'CollectionPage'))['mainEntity']['itemListElement']
            self.assertEqual([item['url'] for item in items],
                             [f'{ORIGIN}{prefix}/resources/{identifier}/' for identifier in page.record_ids])
            self.assertEqual(page.record_ids, ['web-case', 'game-tool', 'game-case'])
            for record in resources:
                # Visible title and source links keep pointing at the original resource.
                self.assertEqual(page.record_links[record['id']][0], record['url'])
                self.assertIn(record['evidence_url'], page.record_links[record['id']])

    def test_validator_rejects_upstream_or_reordered_items(self):
        resources = [resource('first'), resource('second', targets=['website'])]
        for mutate in (lambda items: items[0].update(url='https://example.org/first'),
                       lambda items: items.reverse(),
                       lambda items: items[1].update(url=ORIGIN + '/zh/resources/second/')):
            pages = self.build(resources)
            mutate(next(schema_entities(pages['/resources/'].schemas, 'CollectionPage'))['mainEntity']['itemListElement'])
            with self.assertRaises(AssertionError):
                validate_resource_listing(pages, resources)


if __name__ == '__main__':
    unittest.main()
