import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from schema_org_vocabulary import load  # noqa: E402
from validate_schema_org import Vocabulary, page_errors, validate_site  # noqa: E402

ORIGIN = 'https://awesomerea.org'


def page(*nodes, context='https://schema.org'):
    return ''.join(f'<script type="application/ld+json">{json.dumps({"@context": context, **node})}</script>' for node in nodes)


class SchemaOrgValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vocabulary = Vocabulary(load())

    def errors(self, *nodes, known_ids=frozenset(), known_pages=frozenset(), **options):
        return page_errors(self.vocabulary, page(*nodes, **options), '/page/', set(known_ids), frozenset(known_pages))

    def test_a_valid_graph_has_no_errors(self):
        self.assertEqual(self.errors({'@graph': [
            {'@type': 'WebPage', '@id': ORIGIN + '/page/#webpage', 'url': ORIGIN + '/page/', 'name': 'Page', 'lastReviewed': '2026-10-15',
             'mainEntity': {'@id': ORIGIN + '/page/#code'}},
            {'@type': 'SoftwareSourceCode', '@id': ORIGIN + '/page/#code', 'name': 'Code', 'codeRepository': 'https://github.com/owner/repository'},
        ]}), [])

    def test_unknown_type_is_an_error(self):
        self.assertIn('unknown type', ' '.join(self.errors({'@type': 'SoftwareThing', 'name': 'Name'})))

    def test_unknown_property_is_an_error(self):
        self.assertIn('unknown property', ' '.join(self.errors({'@type': 'WebPage', 'reviewedOn': '2026-10-15'})))

    def test_property_of_another_type_is_an_error(self):
        self.assertIn('does not apply', ' '.join(self.errors({'@type': 'Organization', 'codeRepository': 'https://example.org/'})))

    def test_value_outside_the_range_is_an_error(self):
        self.assertTrue(self.errors({'@type': 'WebPage', 'lastReviewed': 'last week'}))
        self.assertTrue(self.errors({'@type': 'Dataset', 'isAccessibleForFree': 'perhaps'}))

    def test_typed_value_of_the_wrong_type_is_an_error(self):
        self.assertTrue(self.errors({'@type': 'Dataset', 'distribution': {'@type': 'Person', 'name': 'Name'}}))

    def test_unresolved_reference_is_an_error(self):
        node = {'@type': 'WebPage', 'publisher': {'@id': ORIGIN + '/#organization'}}
        self.assertTrue(self.errors(node))
        self.assertEqual(self.errors(node, known_ids={ORIGIN + '/#organization'}), [])

    def test_reference_to_a_sitemap_page_resolves(self):
        node = {'@type': 'WebPage', 'about': {'@id': ORIGIN + '/zh/about/'}}
        self.assertEqual(self.errors(node, known_pages={'/zh/about/'}), [])

    def test_fragment_must_name_a_defined_node_even_on_a_known_page(self):
        node = {'@type': 'WebPage', 'about': {'@id': ORIGIN + '/zh/about/#datset'}}
        self.assertTrue(self.errors(node, known_pages={'/zh/about/'}))
        node = {'@type': 'WebPage', 'about': {'@id': ORIGIN + '/zh/about/#dataset'}}
        self.assertEqual(self.errors(node, known_ids={ORIGIN + '/zh/about/#dataset'}, known_pages={'/zh/about/'}), [])

    def test_action_annotation_belongs_on_an_action(self):
        self.assertEqual(self.errors({'@type': 'SearchAction', 'target': {'@type': 'EntryPoint', 'urlTemplate': ORIGIN + '/?q={term}'},
                                      'query-input': 'required name=term'}), [])
        self.assertIn('belongs on an Action', ' '.join(self.errors({'@type': 'WebPage', 'query-input': 'required name=term'})))

    def test_page_without_json_ld_or_context_is_an_error(self):
        self.assertIn('no JSON-LD', ' '.join(page_errors(self.vocabulary, '<p>Nothing</p>', '/page/', set())))
        self.assertIn('@context', ' '.join(self.errors({'@type': 'WebPage'}, context='http://example.org')))
        self.assertIn('needs @type', ' '.join(self.errors({'name': 'Untyped'})))


class SiteValidationTests(unittest.TestCase):
    def build(self, directory, home_nodes):
        (Path(directory) / 'index.html').write_text(page(*home_nodes), encoding='utf-8')

    def test_a_download_must_be_a_published_file(self):
        node = {'@type': 'Dataset', 'distribution': {'@type': 'DataDownload', 'contentUrl': ORIGIN + '/catalog.json', 'encodingFormat': 'application/json'}}
        with tempfile.TemporaryDirectory() as directory:
            self.build(directory, [node])
            _, errors = validate_site(Path(directory), ['/'])
            self.assertIn('is not a published file', ' '.join(errors))
            (Path(directory) / 'catalog.json').write_text('{}', encoding='utf-8')
            count, errors = validate_site(Path(directory), ['/'])
            self.assertEqual((count, errors), (1, []))

    def test_a_node_any_page_defines_resolves_and_a_missing_one_does_not(self):
        with tempfile.TemporaryDirectory() as directory:
            self.build(directory, [{'@type': 'WebPage', 'about': {'@id': ORIGIN + '/page/#thing'}}])
            child = Path(directory) / 'page'
            child.mkdir()
            (child / 'index.html').write_text(page({'@type': 'Thing', '@id': ORIGIN + '/page/#other', 'name': 'Thing'}), encoding='utf-8')
            self.assertIn('#thing', ' '.join(validate_site(Path(directory), ['/', '/page/'])[1]))
            (child / 'index.html').write_text(page({'@type': 'Thing', '@id': ORIGIN + '/page/#thing', 'name': 'Thing'}), encoding='utf-8')
            self.assertEqual(validate_site(Path(directory), ['/', '/page/'])[1], [])

    def test_homepage_nodes_resolve_on_other_pages(self):
        with tempfile.TemporaryDirectory() as directory:
            self.build(directory, [{'@type': 'Organization', '@id': ORIGIN + '/#organization', 'name': 'Project'}])
            child = Path(directory) / 'page'
            child.mkdir()
            (child / 'index.html').write_text(page({'@type': 'WebPage', 'publisher': {'@id': ORIGIN + '/#organization'}}), encoding='utf-8')
            self.assertEqual(validate_site(Path(directory), ['/', '/page/'])[1], [])


class VendoredVocabularyTests(unittest.TestCase):
    def test_vocabulary_holds_the_terms_the_site_uses(self):
        vocabulary = load()
        self.assertTrue({'SoftwareSourceCode', 'Dataset', 'DataDownload', 'DataCatalog', 'Organization', 'BreadcrumbList'} <= set(vocabulary['types']))
        self.assertTrue({'codeRepository', 'lastReviewed', 'distribution', 'isBasedOn', 'dataset'} <= set(vocabulary['properties']))


if __name__ == '__main__':
    unittest.main()
