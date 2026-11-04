"""The paper listings stay light: entry pages hold each paper's sources and details, and an advisory budget warns,
without failing, before /papers/ or /zh/papers/ grows heavy again."""
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_paper_pages
from build_paper_pages import LISTING_SIZE_BUDGET, build_paper_pages as build, listing_size_warning, listing_size_warnings
import validate_site

# The bibliography had 206 papers when the budget was set. The fixture keeps that many records from
# data/papers.json, so new papers never fail this test; a change that makes every card heavier does.
FIXTURE_PAPERS = 206
ICONS = 'https://awesome-rea.pages.dev/fontawesome.css'


def listing_sizes(papers, icons=ICONS):
    with TemporaryDirectory() as directory:
        output = Path(directory)
        build(output, papers, icon_stylesheet_href=icons)
        return {route: (output / route.lstrip('/') / 'index.html').stat().st_size for route in ('/papers/', '/zh/papers/')}


class PaperListingSizeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.papers = json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))[:FIXTURE_PAPERS]

    def test_fixed_bibliography_fits_the_budget_in_both_languages(self):
        self.assertEqual(len(self.papers), FIXTURE_PAPERS)
        self.assertEqual(LISTING_SIZE_BUDGET, 900_000)
        # Production pages use the icon font; the fallback glyphs are measured too.
        for icons in (ICONS, None):
            for route, size in listing_sizes(self.papers, icons).items():
                with self.subTest(route=route, icons=bool(icons)):
                    self.assertLess(size, LISTING_SIZE_BUDGET, f'{route} is {size:,} bytes for {FIXTURE_PAPERS} papers')

    def test_budget_warning_is_advisory_and_names_the_page(self):
        self.assertIsNone(listing_size_warning('/papers/', LISTING_SIZE_BUDGET))
        note = listing_size_warning('/zh/papers/', LISTING_SIZE_BUDGET + 1)
        self.assertIn('/zh/papers/ is 900,001 bytes', note)
        self.assertIn('900,000-byte budget', note)
        with TemporaryDirectory() as directory:
            output = Path(directory)
            for route, size in (('papers', 10), ('zh/papers', LISTING_SIZE_BUDGET + 5)):
                (output / route).mkdir(parents=True)
                (output / route / 'index.html').write_bytes(b'a' * size)
            notes = listing_size_warnings(output)
        self.assertEqual(len(notes), 1)
        self.assertTrue(notes[0].startswith('/zh/papers/ is 900,005 bytes'), notes[0])

    def test_validator_reports_sizes_and_never_fails_on_size(self):
        with TemporaryDirectory() as directory:
            output = Path(directory)
            build(output, self.papers[:3])
            # Budgets far above and far below the pages, so the test does not depend on how big they are now.
            for budget in (10 * LISTING_SIZE_BUDGET, 1_000):
                with self.subTest(budget=budget):
                    stdout, stderr = io.StringIO(), io.StringIO()
                    with patch.object(build_paper_pages, 'LISTING_SIZE_BUDGET', budget), \
                            patch.object(validate_site, 'LISTING_SIZE_BUDGET', budget), \
                            redirect_stdout(stdout), redirect_stderr(stderr):
                        validate_site.report_listing_sizes(output)
                    self.assertRegex(stdout.getvalue(), r'Paper listings: /papers/ [\d,]+ bytes, /zh/papers/ [\d,]+ bytes')
                    warned = stderr.getvalue().count('Warning: ')
                    self.assertEqual(warned, 0 if budget > LISTING_SIZE_BUDGET else 2)

    def test_cards_link_the_entry_page_instead_of_inlining_sources(self):
        # A source URL stays off the listing unless some card links it as a paper, PDF, code or project link.
        shown = {paper.get(field) for paper in self.papers for field in ('url', 'pdf_url', 'code_url', 'project_url')}
        with TemporaryDirectory() as directory:
            output = Path(directory)
            build(output, self.papers)
            for language, route in (('en', 'papers/index.html'), ('zh', 'zh/papers/index.html')):
                html = (output / route).read_text(encoding='utf-8').replace('&amp;', '&')
                prefix = '/zh' if language == 'zh' else ''
                for paper in self.papers:
                    for url in set(paper['evidence_urls']) - shown:
                        self.assertNotIn(f'"{url}"', html, paper['id'])
                    self.assertIn(f'href="{prefix}/papers/{paper["id"]}/#entry-sources"', html)
                self.assertNotIn('ScholarlyArticle', html)


if __name__ == '__main__':
    unittest.main()
