"""The sitemap index, its section sitemaps and data-derived lastmod dates."""
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from sitemaps import (SECTION_FILES, latest, normalized_date, page_dates, read_sitemaps, record_date, section_for,
                      sitemap_files, sitemap_urls, write_sitemaps)

ORIGIN = 'https://awesomerea.org'
RESOURCES = [
    {'id': 'ghidra', 'kind': 'tool', 'added_at': '2026-10-16', 'verified_at': '2026-10-20'},
    {'id': 'case-a', 'kind': 'case-study', 'added_at': '2026-11-02', 'verified_at': '2026-10-30'},
    {'id': 'late-review', 'kind': 'tool', 'added_at': '2026-10-16', 'verified_at': '2026-11-03T08:15:00Z'},
]
PAPERS = [{'id': 'paper-x', 'added_at': '2026-10-18', 'verified_at': '2026-10-17'}]
REPOSITORIES = {'meta': {'kind': 'published-repository-selection', 'published_at': '2026-10-20T10:49:31Z'}}
BATCHES = [{'ingested_at': '2026-11-05T22:36:35Z'}, {'ingested_at': '2026-11-05T20:10:02Z'}]


def dates():
    return page_dates(resources=RESOURCES, papers=PAPERS, repository_document=REPOSITORIES,
                      discovery_batches=BATCHES, survey_date='2026-10-18')


class PageDateTests(unittest.TestCase):
    def test_entry_pages_use_the_later_of_inclusion_and_review(self):
        self.assertEqual(record_date(RESOURCES[0]), '2026-10-20')
        self.assertEqual(record_date(RESOURCES[1]), '2026-11-02')
        self.assertEqual(record_date(RESOURCES[2]), '2026-11-03T08:15:00Z')
        self.assertIsNone(record_date({'id': 'undated'}))

    def test_listings_repositories_discoveries_survey_and_catalog_pages(self):
        value = dates()
        self.assertEqual(value['/resources/'], '2026-11-03T08:15:00Z')
        self.assertEqual(value['/cases/'], '2026-11-02')
        self.assertEqual(value['/papers/'], '2026-10-18')
        self.assertEqual(value['/browse/'], '2026-10-20T10:49:31Z')
        self.assertEqual(value['/browse/firmware/'], value['/browse/'])
        self.assertEqual(value['/discoveries/'], '2026-11-05T22:36:35Z')
        self.assertEqual(value['/survey/'], '2026-10-18')
        # Catalog-wide pages follow curated, paper and repository data, not the discovery queue.
        self.assertEqual(value['/'], '2026-11-03T08:15:00Z')
        self.assertEqual(value['/about/'], value['/'])
        # No dated record describes the contribution guide.
        self.assertNotIn('/contribute/', value)
        # The API guide follows both unreviewed queues as well, like the API's generated_at.
        self.assertEqual(value['/api/'], '2026-11-05T22:36:35Z')
        with_leads = page_dates(resources=RESOURCES, papers=PAPERS, discovery_batches=BATCHES,
                                lead_batches=[{'collected_at': '2026-11-05T23:01:00Z'}])
        self.assertEqual(with_leads['/api/'], '2026-11-05T23:01:00Z')
        self.assertEqual(with_leads['/'], value['/resources/'])

    def test_date_normalization_and_ordering(self):
        self.assertEqual(normalized_date('2026-10-16T11:55:19.172701Z'), '2026-10-16T11:55:19Z')
        self.assertEqual(normalized_date('2026-10-16T11:55:19+00:00'), '2026-10-16T11:55:19Z')
        self.assertEqual(normalized_date('2026-10-16T11:55:19+08:00'), '2026-10-16T11:55:19+08:00')
        self.assertIsNone(normalized_date('yesterday'))
        self.assertIsNone(normalized_date(None))
        # A timestamp later on the same day beats the bare date; equal instants keep the more precise value.
        self.assertEqual(latest(['2026-11-05', '2026-11-05T01:00:00Z']), '2026-11-05T01:00:00Z')
        self.assertEqual(latest(['2026-11-05', '2026-11-04T23:00:00Z']), '2026-11-05')
        self.assertEqual(latest(['2026-11-05T00:00:00Z', '2026-11-05']), '2026-11-05T00:00:00Z')
        self.assertIsNone(latest([None, 'x']))

    def test_page_sections(self):
        for path, section in (('/', 'pages'), ('/zh/about/', 'pages'), ('/discoveries/', 'pages'), ('/api/', 'pages'),
                              ('/resources/', 'resources'), ('/zh/cases/', 'resources'), ('/resources/ghidra/', 'resources'),
                              ('/papers/', 'papers'), ('/zh/papers/paper-x/', 'papers'),
                              ('/browse/', 'categories'), ('/zh/browse/firmware/', 'categories')):
            self.assertEqual(section_for(path), section, path)


class SitemapFileTests(unittest.TestCase):
    PATHS = ['/', '/zh/', '/about/', '/zh/about/', '/contribute/', '/zh/contribute/', '/resources/', '/zh/resources/',
             '/resources/ghidra/', '/zh/resources/ghidra/', '/papers/', '/zh/papers/', '/papers/paper-x/', '/zh/papers/paper-x/']

    def test_index_lists_only_written_sections_with_their_newest_date(self):
        with TemporaryDirectory() as directory:
            output = Path(directory)
            written = write_sitemaps(output, ORIGIN, self.PATHS, dates())
            # No repository pages were given, so the categories sitemap is not written.
            self.assertEqual(list(written), ['pages', 'resources', 'papers'])
            self.assertFalse((output / SECTION_FILES['categories']).exists())
            sitemaps, pages = read_sitemaps(output, ORIGIN)
            self.assertEqual(list(sitemaps), [ORIGIN + '/sitemap-pages.xml', ORIGIN + '/sitemap-resources.xml',
                                              ORIGIN + '/sitemap-papers.xml'])
            self.assertEqual(sitemaps[ORIGIN + '/sitemap-resources.xml']['lastmod'], '2026-11-03T08:15:00Z')
            self.assertEqual(sitemaps[ORIGIN + '/sitemap-papers.xml']['lastmod'], '2026-10-18')
            self.assertEqual(sitemap_urls(output, ORIGIN), [ORIGIN + path for path in (
                '/', '/zh/', '/about/', '/zh/about/', '/contribute/', '/zh/contribute/', '/resources/', '/zh/resources/',
                '/resources/ghidra/', '/zh/resources/ghidra/', '/papers/', '/zh/papers/', '/papers/paper-x/', '/zh/papers/paper-x/')])
            self.assertEqual(sitemap_files(output, ORIGIN), ['sitemap.xml', 'sitemap-pages.xml', 'sitemap-resources.xml', 'sitemap-papers.xml'])
            ghidra = pages[ORIGIN + '/zh/resources/ghidra/']
            self.assertEqual(ghidra['lastmod'], '2026-10-20')
            self.assertEqual(ghidra['alternates'], {'en': ORIGIN + '/resources/ghidra/', 'zh-CN': ORIGIN + '/zh/resources/ghidra/',
                                                    'x-default': ORIGIN + '/resources/ghidra/'})
            # Undated pages are listed without a lastmod rather than with the build time.
            self.assertIsNone(pages[ORIGIN + '/contribute/']['lastmod'])
            text = (output / 'sitemap-pages.xml').read_text(encoding='utf-8')
            self.assertIn('xmlns:xhtml="http://www.w3.org/1999/xhtml"', text)
            self.assertEqual(text.count('<lastmod>'), 4)

    def test_paths_must_be_unique_directory_paths(self):
        with TemporaryDirectory() as directory:
            for paths in (['/', '/'], ['/llms.txt'], ['resources/'], ['//x/']):
                with self.assertRaises(ValueError):
                    write_sitemaps(Path(directory), ORIGIN, paths, {})

    def test_legacy_urlset_and_foreign_index_entries(self):
        with TemporaryDirectory() as directory:
            output = Path(directory)
            (output / 'sitemap.xml').write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                                f'<url><loc>{ORIGIN}/</loc></url></urlset>', encoding='utf-8')
            self.assertEqual(sitemap_urls(output, ORIGIN), [ORIGIN + '/'])
            self.assertEqual(sitemap_files(output, ORIGIN), ['sitemap.xml'])
            for loc in ('https://example.com/sitemap-pages.xml', ORIGIN + '/nested/sitemap-pages.xml', ORIGIN + '/feed.xml'):
                (output / 'sitemap.xml').write_text('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                                    f'<sitemap><loc>{loc}</loc></sitemap></sitemapindex>', encoding='utf-8')
                with self.assertRaises(ValueError):
                    read_sitemaps(output, ORIGIN)


class BuiltSitemapTests(unittest.TestCase):
    """The validator recomputes every lastmod from the published data and rejects a build-time date."""

    def test_validator_rejects_a_changed_lastmod(self):
        from validate_discovery import validate_sitemaps
        import json
        with TemporaryDirectory() as directory:
            output = Path(directory)
            (output / 'source-published.json').write_text(json.dumps(REPOSITORIES), encoding='utf-8')
            (output / 'discoveries.json').write_text(json.dumps({'batches': BATCHES}), encoding='utf-8')
            survey = json.loads((ROOT / 'data/survey.json').read_text(encoding='utf-8'))
            values = page_dates(resources=RESOURCES, papers=PAPERS, repository_document=REPOSITORIES,
                                discovery_batches=BATCHES, survey_date=survey['date'])
            paths = [prefix + path for path in ('/', '/resources/', '/resources/ghidra/', '/resources/case-a/',
                                                '/resources/late-review/', '/papers/', '/papers/paper-x/', '/browse/')
                     for prefix in ('', '/zh')]
            write_sitemaps(output, ORIGIN, paths, values)
            self.assertEqual(len(validate_sitemaps(output, RESOURCES, PAPERS)), len(paths))
            target = output / 'sitemap-resources.xml'
            original = target.read_text(encoding='utf-8')
            target.write_text(original.replace('<lastmod>2026-10-20</lastmod>', '<lastmod>2026-11-06T00:00:00Z</lastmod>', 1), encoding='utf-8')
            with self.assertRaises(AssertionError):
                validate_sitemaps(output, RESOURCES, PAPERS)
            target.write_text(original.replace('hreflang="zh-CN" href="https://awesomerea.org/zh/resources/ghidra/"',
                                               'hreflang="zh-CN" href="https://awesomerea.org/zh/resources/other/"'), encoding='utf-8')
            with self.assertRaises(AssertionError):
                validate_sitemaps(output, RESOURCES, PAPERS)


if __name__ == '__main__':
    unittest.main()
