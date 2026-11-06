"""Resource page titles carry the localized category; names stay unchanged elsewhere."""
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from build_entry_pages import build_entry_pages, entry_path
from build_readme import CATEGORIES
from page_metadata import TITLE_MAX, page_title
from test_entry_pages import paper, resource
from validate_site import DocumentTitle, Page, validate_unique_titles


class EntryTitleTests(unittest.TestCase):
    def test_resource_titles_add_the_localized_category_only_to_the_document_title(self):
        record = resource(id='rr', name='rr', name_zh='rr', category='dynamic-analysis')
        study = paper()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            build_entry_pages(root, [record], [study])
            for language in ('en', 'zh'):
                text = (root / entry_path('resource', 'rr', language).lstrip('/') / 'index.html').read_text(encoding='utf-8')
                label = CATEGORIES['dynamic-analysis'][language == 'zh']
                self.assertEqual(DocumentTitle(text).titles, [f'rr · {label} · AwesomeREA.org'])
                page = Page(text)
                self.assertEqual(page.h1_texts, ['rr'])
                self.assertEqual(page.meta['og:title'], 'rr')
                self.assertEqual([node['name'] for node in page.schemas[0]['@graph'] if node.get('@id', '').endswith('#resource')], ['rr'])
                text = (root / entry_path('paper', study['id'], language).lstrip('/') / 'index.html').read_text(encoding='utf-8')
                title = study['title_zh' if language == 'zh' else 'title']
                self.assertEqual(DocumentTitle(text).titles, [page_title(title)])
            titles = [DocumentTitle((root / entry_path('resource', 'rr', language).lstrip('/') / 'index.html')
                                    .read_text(encoding='utf-8')).titles[0] for language in ('en', 'zh')]
            self.assertNotEqual(*titles)

    def test_long_names_are_fitted_only_in_the_document_title(self):
        name = 'A Long Resource Name With Enough Words To Run Past The Search Result Limit'
        record = resource(id='long-name', name=name, name_zh=name, category='dynamic-analysis')
        with TemporaryDirectory() as directory:
            root = Path(directory)
            build_entry_pages(root, [record], [paper()])
            for language in ('en', 'zh'):
                text = (root / entry_path('resource', 'long-name', language).lstrip('/') / 'index.html').read_text(encoding='utf-8')
                title = DocumentTitle(text).titles[0]
                self.assertLessEqual(len(title), TITLE_MAX)
                self.assertIn('…', title)
                self.assertEqual(Page(text).h1_texts, [name])
                self.assertEqual(Page(text).meta['og:title'], name)

    def test_validator_rejects_long_titles_and_other_separators(self):
        for title in ('A' * 61, 'rr | AwesomeREA.org'):
            with TemporaryDirectory() as directory:
                path = Path(directory) / 'papers/rr/index.html'
                path.parent.mkdir(parents=True)
                path.write_text(f'<html><head><title>{title}</title></head><body><h1>x</h1></body></html>', encoding='utf-8')
                with self.assertRaises(AssertionError):
                    validate_unique_titles(directory, ['/papers/rr/'])

    def test_validator_rejects_shared_titles_and_untranslated_chinese_resource_titles(self):
        def check(pages):
            with TemporaryDirectory() as directory:
                for route, title in pages.items():
                    path = Path(directory) / route.lstrip('/') / 'index.html'
                    path.parent.mkdir(parents=True)
                    path.write_text(f'<html><head><title>{title}</title></head><body><h1>x</h1></body></html>', encoding='utf-8')
                validate_unique_titles(directory, list(pages))

        check({'/resources/rr/': 'rr · Dynamic analysis · AwesomeREA.org',
               '/zh/resources/rr/': 'rr · 动态分析 · AwesomeREA.org'})
        for pages in ({'/resources/rr/': 'rr · AwesomeREA.org', '/zh/resources/rr/': 'rr · AwesomeREA.org'},
                      {'/zh/resources/rr/': 'rr · Dynamic analysis · AwesomeREA.org'},
                      {'/papers/': ''}):
            with self.subTest(pages=pages), self.assertRaises(AssertionError):
                check(pages)


if __name__ == '__main__':
    unittest.main()
