"""Newest-first display order must agree across languages, search and metadata."""
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_paper_pages import build_paper_pages, papers_newest_first, formatted_date, scholarly_article, bibtex_text
from build_readme import render_papers
from validate_site import Page, validate_paper_groups


def paper(identifier, year, publication_date, title, targets=('website',)):
    row = deepcopy(json.loads((ROOT / 'data/papers.json').read_text())[0])
    row.update(id=identifier, year=year, publication_date=publication_date,
               date_precision='year' if publication_date is None else 'month' if len(publication_date) == 7 else 'day',
               publication_status='conference-accepted' if publication_date is None else 'conference-paper',
               title=title, title_zh='中文标题：' + identifier, targets=list(targets),
               url='https://example.org/papers/' + identifier, pdf_url='https://example.org/pdf/' + identifier + '.pdf',
               doi='10.1234/' + identifier, arxiv_id=None, arxiv_version_reviewed=None,
               first_arxiv_date=None, code_url=None, project_url=None)
    return row


PAPERS = [
    paper('paper-year-a', 2026, None, 'Alpha year'),
    paper('paper-protocol-old', 2018, '2018-08-13', 'Old protocol', ('protocol',)),
    paper('paper-tie-a', 2026, '2026-10-05', 'eCHO'),
    paper('paper-month', 2026, '2026-10', 'Month only'),
    paper('paper-multi', 2026, None, 'Game first', ('game', 'website')),
    paper('paper-older', 2025, '2025-12-31', 'Previous year'),
    paper('paper-year-z', 2026, None, 'Zebra year'),
    paper('paper-app', 2025, '2025-06', 'App paper', ('app',)),
    paper('paper-protocol-new', 2024, '2024-12-02', 'New protocol', ('protocol',)),
    paper('paper-tie-b', 2026, '2026-10-05', 'Echo'),
    paper('paper-day', 2026, '2026-10-06', 'Day precision'),
]
WEBSITE_ORDER = ['paper-day', 'paper-tie-b', 'paper-tie-a', 'paper-month',
                 'paper-year-z', 'paper-year-a', 'paper-older']
GROUP_ORDER = {'research-website-reconstruction': WEBSITE_ORDER, 'research-game-reconstruction': ['paper-multi'],
               'research-app-reconstruction': ['paper-app'],
               'research-protocol-analysis': ['paper-protocol-new', 'paper-protocol-old']}
DOM_ORDER = [identifier for group in GROUP_ORDER.values() for identifier in group]


class PaperOrderTests(unittest.TestCase):
    def test_recorded_precision_and_ties_without_mutating_input(self):
        original = deepcopy(PAPERS)
        website = [row for row in PAPERS if row['targets'][0] == 'website']
        self.assertEqual([row['id'] for row in papers_newest_first(website)], WEBSITE_ORDER)
        self.assertEqual([row['id'] for row in papers_newest_first(list(reversed(website)))], WEBSITE_ORDER)
        self.assertEqual(PAPERS, original)
        year_only = next(row for row in PAPERS if row['id'] == 'paper-year-z')
        month_only = next(row for row in PAPERS if row['id'] == 'paper-month')
        self.assertIsNone(year_only['publication_date'])
        self.assertNotIn('datePublished', scholarly_article(year_only, 'en'))
        self.assertNotIn('month =', bibtex_text(year_only))
        self.assertEqual(formatted_date(None, 'en', 2026), '2026 (exact date not verified)')
        self.assertEqual(formatted_date(month_only['publication_date'], 'en'), 'October 2026')
        self.assertEqual(scholarly_article(month_only, 'zh')['datePublished'], '2026-10')

    def test_bilingual_dom_itemlist_and_search_projection_share_deterministic_order(self):
        original = deepcopy(PAPERS)
        with TemporaryDirectory() as first, TemporaryDirectory() as second:
            outputs = [Path(first), Path(second)]
            for output, input_rows in zip(outputs, (PAPERS, list(reversed(PAPERS)))):
                build_paper_pages(output, input_rows)
                for language, route in [('en', 'papers/index.html'), ('zh', 'zh/papers/index.html')]:
                    html = (output / route).read_text()
                    page = Page(html)
                    validate_paper_groups(page, input_rows, language)
                    self.assertEqual(page.paper_ids, DOM_ORDER)
                    self.assertEqual({group['anchor']: group['paper_ids'] for group in page.paper_groups}, GROUP_ORDER)
                    self.assertEqual(page.paper_ids.count('paper-multi'), 1)
                    projection = json.loads(re.search(r'<script id="paper-search-data" type="application/json">(.*?)</script>', html, re.S)[1])
                    self.assertEqual([row['id'] for row in projection['papers']], DOM_ORDER)
                    graph = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)[1])['@graph']
                    listing = next(row for row in graph if row['@type'] == 'ItemList')
                    self.assertEqual([item['position'] for item in listing['itemListElement']], list(range(1, len(PAPERS) + 1)))
                    prefix = '/zh' if language == 'zh' else ''
                    self.assertEqual([item['url'] for item in listing['itemListElement']],
                                     ['https://awesomerea.org' + prefix + '/papers/' + identifier + '/' for identifier in DOM_ORDER])
                    self.assertEqual([row['@id'] for row in graph if row['@type'] == 'ScholarlyArticle'],
                                     ['https://awesomerea.org' + prefix + '/papers/' + identifier + '/#paper' for identifier in DOM_ORDER])
                    self.assertIn('各分区按年份从新到旧排列' if language == 'zh' else 'newest year first within each section', html)
                for row in input_rows:
                    self.assertEqual((output / 'papers/citations' / (row['id'] + '.bib')).read_text(), bibtex_text(row))
            for route in ('papers/index.html', 'zh/papers/index.html'):
                self.assertEqual((outputs[0] / route).read_bytes(), (outputs[1] / route).read_bytes())
            # Download order remains the canonical input order, independently of presentation order.
            expected_bib = '% Generated from source-reviewed metadata. Author names retain their listed order without inferred surname parsing.\n\n'
            expected_bib += ''.join(bibtex_text(row) + '\n' for row in PAPERS)
            self.assertEqual((outputs[0] / 'papers/references.bib').read_text(), expected_bib)
        self.assertEqual(PAPERS, original)

    def test_readme_reuses_order_without_changing_primary_or_agent_routing(self):
        for language in ('en', 'zh'):
            text = render_papers(PAPERS, language)
            for section, identifiers in [('website-reconstruction', WEBSITE_ORDER), ('game-reconstruction', ['paper-multi']),
                                         ('app-reconstruction', ['paper-app']), ('protocol-analysis', GROUP_ORDER['research-protocol-analysis'])]:
                content = text.split(f'<a id="papers-{section}"></a>', 1)[1].split('<a id="papers-', 1)[0]
                actual = re.findall(r'^- \[\*\*.*?\*\*\]\(https://example.org/papers/(paper-[a-z-]+)\) - ', content, re.M)
                self.assertEqual(actual, identifiers)
            agent = paper('paper-programbench', 2026, None, 'Agent benchmark', ('protocol',))
            special = render_papers([agent], language)
            self.assertIn('<a id="papers-agent-evaluation"></a>', special)
            self.assertNotIn('<a id="papers-protocol-analysis"></a>', special)


if __name__ == '__main__':
    unittest.main()
