from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from open_graph import open_graph_meta, website_node  # noqa: E402
from structured_data import (catalog_node, dataset_id, dataset_node, evidence_urls, organization_node,  # noqa: E402
                             publisher_reference, resource_entity)

SITE = 'https://awesomerea.org'
REPOSITORY = 'https://github.com/reacher-z/Awesome-REA'
UNSUPPORTED_CLAIMS = {'author', 'creator', 'datePublished', 'license', 'programmingLanguage', 'aggregateRating', 'review'}


def entity(kind, url):
    return resource_entity({'kind': kind, 'url': url}, 'entity-id', 'Name', 'Description')


class ResourceEntityTests(unittest.TestCase):
    def test_repository_kinds_on_github_are_source_code(self):
        for kind in ('tool', 'integration', 'project', 'case-study'):
            node = entity(kind, 'https://github.com/owner/repository')
            self.assertEqual(node['@type'], 'SoftwareSourceCode', kind)
            self.assertEqual(node['codeRepository'], 'https://github.com/owner/repository')

    def test_a_link_into_a_repository_is_not_named_as_the_repository(self):
        node = entity('tool', 'https://github.com/owner/repository/tree/main/tool')
        self.assertEqual(node['@type'], 'CreativeWork')
        self.assertNotIn('codeRepository', node)

    def test_other_kinds_follow_the_mapping(self):
        self.assertEqual(entity('case-study', 'https://example.org/write-up')['@type'], 'TechArticle')
        self.assertEqual(entity('case-study', 'https://example.org/write-up')['headline'], 'Name')
        self.assertEqual(entity('learning-resource', 'https://example.org/course')['@type'], 'LearningResource')
        self.assertEqual(entity('research', 'https://example.org/paper')['@type'], 'ScholarlyArticle')
        self.assertEqual(entity('collection', 'https://github.com/owner/awesome-list')['@type'], 'CreativeWork')
        self.assertEqual(entity('tool', 'https://example.org/tool')['@type'], 'CreativeWork')

    def test_no_claim_beyond_the_record(self):
        for kind in ('tool', 'case-study', 'learning-resource', 'research', 'collection'):
            self.assertFalse(UNSUPPORTED_CLAIMS.intersection(entity(kind, 'https://github.com/owner/repository')), kind)

    def test_evidence_urls_drop_repeats_and_keep_the_order(self):
        record = {'url': 'https://a.example/', 'evidence_url': 'https://b.example/',
                  'additional_evidence_urls': ['https://b.example/', 'https://c.example/']}
        self.assertEqual(evidence_urls(record), ['https://b.example/', 'https://c.example/'])
        paper = {'url': 'https://a.example/', 'evidence_urls': ['https://a.example/', 'https://d.example/']}
        self.assertEqual(evidence_urls(paper), ['https://a.example/', 'https://d.example/'])

    def test_the_resource_page_can_be_the_only_evidence(self):
        record = {'url': 'https://a.example/', 'evidence_url': 'https://a.example/'}
        self.assertEqual(evidence_urls(record), ['https://a.example/'])


class SiteNodeTests(unittest.TestCase):
    def test_organization_is_the_project_and_names_no_person(self):
        node = organization_node(SITE, REPOSITORY)
        self.assertEqual(node['@id'], SITE + '/#organization')
        self.assertEqual(node['sameAs'], [REPOSITORY, 'https://huggingface.co/datasets/TIGER-Lab/AwesomeREA'])
        self.assertEqual(node['alternateName'], ['Awesome Reverse Engineering Anything', 'AwesomeREA'])
        self.assertEqual(set(node), {'@type', '@id', 'name', 'alternateName', 'url', 'logo', 'sameAs'})
        self.assertEqual(publisher_reference(SITE), {'@id': node['@id']})

    def test_website_names_its_publisher_and_search(self):
        node = website_node(SITE, REPOSITORY)
        self.assertEqual(node['publisher'], publisher_reference(SITE))
        action = node['potentialAction']
        self.assertEqual(action['target']['urlTemplate'], SITE + '/?q={search_term_string}')
        self.assertEqual(action['query-input'], 'required name=search_term_string')

    def test_catalog_points_at_the_dataset_on_about(self):
        self.assertEqual(catalog_node(SITE)['dataset'], {'@id': SITE + '/about/#dataset'})

    def test_dataset_follows_the_search_requirements(self):
        for language, url in (('en', SITE + '/about/'), ('zh', SITE + '/zh/about/')):
            node = dataset_node(SITE, language, '2026-11-01')
            self.assertEqual(node['@id'], dataset_id(SITE, language))
            self.assertEqual(node['url'], url)
            self.assertTrue(50 <= len(node['description']) <= 5000, language)
            self.assertEqual(node['license'], 'https://spdx.org/licenses/MIT.html')
            self.assertEqual(node['creator'], publisher_reference(SITE))
            self.assertEqual(node['dateModified'], '2026-11-01')
            self.assertEqual(node['includedInDataCatalog'], {'@id': SITE + '/#catalog'})
            formats = {download['contentUrl']: download['encodingFormat'] for download in node['distribution']}
            self.assertEqual(formats[SITE + '/api/v1/resources.csv'], 'text/csv')
            self.assertEqual(formats[SITE + '/downloads/awesome-rea-data.zip'], 'application/zip')
            self.assertTrue(all(download['@type'] == 'DataDownload' for download in node['distribution']))

    def test_dataset_without_a_date_claims_none(self):
        self.assertNotIn('dateModified', dataset_node(SITE, 'en', None))


class OpenGraphHookTests(unittest.TestCase):
    def meta(self, **options):
        return open_graph_meta(language='en', title='Title', description='Description', image_url=SITE + '/social-card.png',
                               url=SITE + '/', **options)

    def test_pages_are_websites_by_default(self):
        self.assertIn('property="og:type" content="website"', self.meta())

    def test_entry_pages_can_be_articles(self):
        self.assertIn('property="og:type" content="article"', self.meta(og_type='article'))

    def test_a_page_with_its_own_card_describes_it(self):
        html = self.meta(image_alt='A card about firmware')
        self.assertEqual(html.count('content="A card about firmware"'), 2)


if __name__ == '__main__':
    unittest.main()
