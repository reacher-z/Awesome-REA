"""One WebSite node and one site name across the homepage, listing, survey and detail pages."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from build_browse_pages import build_browse_pages
from build_discovery_pages import build_discovery_pages
from build_entry_pages import build_entry_pages
from build_paper_pages import build_paper_pages
from build_survey import build_survey
from open_graph import SITE_ALTERNATE_NAMES, SITE_NAME, open_graph_meta, website_node
from test_site_metadata import CARD, ORIGIN, resource, social_page
from test_source_browser import full_export
from validate_site import Page, validate_open_graph, validate_website_identity

REPOSITORY = 'https://github.com/reacher-z/Awesome-REA'


def homepage(node):
    graph = {'@context': 'https://schema.org', '@graph': [node, {
        '@type': 'CollectionPage', '@id': ORIGIN + '/#collection', 'isPartOf': {'@id': ORIGIN + '/#website'}}]}
    return Page(f'<script type="application/ld+json">{json.dumps(graph)}</script>')


class WebsiteIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        papers = json.loads((ROOT / 'data/papers.json').read_text())
        resources = (json.loads((ROOT / 'data/rea-resources.json').read_text())
                     + json.loads((ROOT / 'data/tool-resources.json').read_text()))
        cls.pages = {'/': homepage(website_node(ORIGIN, REPOSITORY)), '/zh/': homepage(website_node(ORIGIN, REPOSITORY))}
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build_browse_pages(output, full_export(), curated_count=1, site_url=ORIGIN, repository_url=REPOSITORY,
                               styles_href='/styles.css', browse_styles_href='/browse.css', favicon_href='/favicon.svg',
                               social_image_href=CARD, data_revision='0' * 16)
            build_discovery_pages(output, {'resources': [resource()], 'meta': {}}, None)
            build_paper_pages(output, papers, social_image_href=CARD)
            build_entry_pages(output, [resource()], papers[:1], social_image_href=CARD)
            build_survey(output, papers, resources, social_image_href=CARD)
            for path in output.rglob('index.html'):
                route = '/' + path.parent.relative_to(output).as_posix() + '/'
                cls.pages[route] = Page(path.read_text(encoding='utf-8'))
        assert {'/browse/', '/zh/browse/android/', '/resources/', '/cases/', '/zh/about/', '/papers/', '/zh/papers/',
                '/survey/', '/zh/survey/', f'/resources/{resource()["id"]}/'} <= set(cls.pages)

    def test_site_name_is_shared_by_open_graph_and_the_homepage_node(self):
        node = website_node(ORIGIN, REPOSITORY)
        self.assertEqual((node['name'], node['alternateName'], node['@id']), (SITE_NAME, SITE_ALTERNATE_NAMES, ORIGIN + '/#website'))
        self.assertNotIn(SITE_NAME, SITE_ALTERNATE_NAMES)
        page = Page(open_graph_meta(language='en', title='T', description='D', image_url=CARD, url=ORIGIN + '/x/'))
        self.assertEqual(page.meta['og:site_name'], SITE_NAME)
        with self.assertRaises(AssertionError):
            validate_open_graph('/papers/', social_page('/papers/', **{f'content="{SITE_NAME}"': 'content="AwesomeREA.org"'}), (1200, 630))

    def test_generated_pages_reference_the_homepage_node(self):
        validate_website_identity(self.pages)

    def test_validator_rejects_inline_websites_and_divergent_homepages(self):
        inline = deepcopy(self.pages)
        inline['/papers/'].schemas[0]['@graph'][0]['isPartOf'] = {'@type': 'WebSite', 'name': 'AwesomeREA.org', 'url': ORIGIN + '/'}
        renamed = dict(self.pages, **{'/zh/': homepage({**website_node(ORIGIN, REPOSITORY), 'name': 'AwesomeREA.org'})})
        unlinked = deepcopy(self.pages)
        del unlinked['/survey/'].schemas[0]['@graph'][0]['isPartOf']
        for name, pages in (('inline WebSite', inline), ('renamed homepage', renamed), ('no reference', unlinked)):
            with self.subTest(case=name), self.assertRaises(AssertionError):
                validate_website_identity(pages)


if __name__ == '__main__':
    unittest.main()
