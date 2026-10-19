"""Each paper has one JSON-LD identity per language, shared by /papers/ and its detail page."""
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from build_entry_pages import build_entry_pages, entry_path
from build_paper_pages import build_paper_pages, scholarly_article
from test_entry_pages import paper
from validate_site import Page, expected_paper_schema, schema_entities

ORIGIN = 'https://awesomerea.org'


def papers():
    return [
        paper('paper-fuzzware', id='paper-both', doi='10.1145/1234567.7654321', arxiv_id='2401.01234',
              url='https://www.usenix.org/conference/example/presentation/both'),
        paper('paper-fuzzware', id='paper-arxiv-url', doi=None, arxiv_id='2402.04321',
              url='https://arxiv.org/abs/2402.04321'),
        paper('paper-fuzzware', id='paper-unidentified', doi=None, arxiv_id=None),
    ]


class PaperJsonLdIdentityTests(unittest.TestCase):
    def test_same_as_uses_only_recorded_identifiers_and_skips_the_paper_url(self):
        both, arxiv_url, unidentified = papers()
        for language in ('en', 'zh'):
            self.assertEqual(scholarly_article(both, language)['sameAs'],
                             ['https://doi.org/10.1145/1234567.7654321', 'https://arxiv.org/abs/2401.01234'])
            self.assertNotIn('sameAs', scholarly_article(arxiv_url, language))
            self.assertNotIn('sameAs', scholarly_article(unidentified, language))
            for record in (both, arxiv_url, unidentified):
                self.assertEqual(scholarly_article(record, language), expected_paper_schema(record, language))

    def test_directory_and_detail_page_share_the_entity_and_the_list_points_at_the_detail_page(self):
        records = papers()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            build_paper_pages(root, records)
            build_entry_pages(root, [], records)
            for language, prefix in (('en', ''), ('zh', '/zh')):
                listing = Page((root / prefix.lstrip('/') / 'papers/index.html').read_text(encoding='utf-8'))
                items = next(schema_entities(listing.schemas, 'ItemList'))['itemListElement']
                directory_ids = [article['@id'] for article in schema_entities(listing.schemas, 'ScholarlyArticle')]
                self.assertEqual([item['item']['@id'] for item in items], directory_ids)
                for item in items:
                    identifier = item['url'].removeprefix(ORIGIN + prefix + '/papers/').removesuffix('/')
                    self.assertEqual(item['url'], ORIGIN + entry_path('paper', identifier, language))
                    detail = Page((root / entry_path('paper', identifier, language).lstrip('/') / 'index.html').read_text(encoding='utf-8'))
                    article = next(schema_entities(detail.schemas, 'ScholarlyArticle'))
                    self.assertEqual(article['@id'], item['item']['@id'])
                    self.assertEqual(article['@id'], ORIGIN + entry_path('paper', identifier, language) + '#paper')
                    self.assertIn(identifier, listing.paper_ids)


if __name__ == '__main__':
    unittest.main()
