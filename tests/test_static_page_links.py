"""Keep static Chinese navigation on /zh/ routes and BibTeX months in macro form."""
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from build_browse_pages import build_browse_pages
from build_discovery_pages import build_discovery_pages
from build_paper_pages import bibtex_text, build_paper_pages
from test_source_browser import full_export
from validate_site import Page, validate_language_links


def dated_paper(publication_date):
    record = deepcopy(json.loads((ROOT / 'data/papers.json').read_text())[0])
    record.update(id='paper-month-fixture', title='Month fixture', authors=['Ada Example', 'Bo Example'],
                  year=2020, publication_date=publication_date, venue='Example Journal',
                  publication_status='journal-article', doi=None, arxiv_id=None,
                  url='https://example.org/paper')
    return record


def navigation(html):
    wordmark = re.search(r'<a class="wordmark" href="([^"]+)"', html)[1]
    breadcrumb = re.search(r'<nav class="(?:browse|papers)-breadcrumbs"[^>]*><a href="([^"]+)"', html)[1]
    return wordmark, breadcrumb


class BibtexMonthTests(unittest.TestCase):
    def test_month_and_day_precision_emit_unbraced_month_macros(self):
        expected = ('@article{paper-month-fixture,\n'
                    '  title = {{Month fixture}},\n'
                    '  author = {{Ada Example} and {Bo Example}},\n'
                    '  year = {2020},\n'
                    '  url = {https://example.org/paper},\n'
                    '  journal = {Example Journal},\n'
                    '  month = feb\n'
                    '}\n')
        self.assertEqual(bibtex_text(dated_paper('2020-02')), expected)
        # Day precision still cites only the month; BibTeX has no day field here.
        self.assertEqual(bibtex_text(dated_paper('2020-02-27')), expected)
        self.assertIn('  month = nov\n}', bibtex_text(dated_paper('2020-11-03')))

    def test_year_only_records_have_no_month(self):
        citation = bibtex_text(dated_paper(None))
        self.assertNotIn('month =', citation)
        self.assertTrue(citation.endswith('  journal = {Example Journal}\n}\n'))

    def test_invalid_month_is_rejected(self):
        for value in ('2020-00', '2020-13'):
            with self.assertRaises(ValueError):
                bibtex_text(dated_paper(value))


class LanguageLinkTests(unittest.TestCase):
    def test_validator_rejects_links_that_select_chinese_on_english_routes(self):
        for href in ('/?lang=zh', '/?view=curated&amp;lang=zh', 'https://awesomerea.org/?lang=zh',
                     '/browse/?lang=zh', '/zh/?lang=en'):
            with self.subTest(href=href), self.assertRaises(AssertionError):
                validate_language_links('/zh/about/', Page(f'<a href="{href}">首页</a>'))
        accepted = ''.join(f'<a href="{href}">link</a>' for href in (
            '/zh/', '/zh/?view=source-index', '/zh/?view=curated', '/?view=source-index&amp;lang=en',
            '/', 'https://example.org/?lang=zh', '#content'))
        validate_language_links('/zh/about/', Page(accepted))

    def test_generated_chinese_pages_link_home_and_search_to_zh_routes(self):
        resource = deepcopy(json.loads((ROOT / 'data/tool-resources.json').read_text())[0])
        resource['requirements_zh'] = ['测试前置条件']
        papers = json.loads((ROOT / 'data/papers.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build_browse_pages(output, full_export(), curated_count=1, site_url='https://awesomerea.org',
                               repository_url='https://github.com/reacher-z/Awesome-REA', styles_href='/styles.css',
                               browse_styles_href='/browse.css', favicon_href='/favicon.svg',
                               social_image_href='https://awesomerea.org/social-card.png', data_revision='0' * 16)
            build_discovery_pages(output, {'resources': [resource], 'meta': {}}, None)
            build_paper_pages(output, papers)
            searches = {'browse': ('/zh/?view=source-index', '/?view=source-index&amp;lang=en'),
                        'resources': ('/zh/?view=curated', '/?view=curated&amp;lang=en')}
            for route in ('browse/', 'browse/android/', 'resources/', 'about/', 'papers/'):
                for language, prefix, home in (('zh', 'zh/', '/zh/'), ('en', '', '/')):
                    with self.subTest(route=route, language=language):
                        html = (output / prefix / route / 'index.html').read_text()
                        self.assertEqual(navigation(html), (home, home))
                        self.assertNotIn('lang=zh', html)
                        validate_language_links('/' + prefix + route, Page(html))
                        search = searches.get(route.split('/')[0])
                        if search:
                            # Category pages add their own &source-category= (tests/test_source_category.py).
                            self.assertIn(f'href="{search[language == "en"]}', html)


if __name__ == '__main__':
    unittest.main()
