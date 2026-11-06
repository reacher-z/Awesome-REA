"""Verify progressive paper search keeps the static listing complete and loads its index from one hashed file."""
from html import escape
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_paper_pages import SEARCH_FIELDS, build_paper_pages, bibtex_text


def search_index(output, html):
    """The index file a built listing's form names and preloads."""
    href = re.search(r'<form id="paper-search"[^>]*\bdata-search-index="(/assets/paper-search-index\.[0-9a-f]{16}\.json)"', html)[1]
    return href, json.loads((Path(output) / href.lstrip('/')).read_text(encoding='utf-8'))


class PaperSearchTests(unittest.TestCase):
    def test_real_bibliography_stays_complete_without_javascript(self):
        papers = json.loads((ROOT / 'data/papers.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build_paper_pages(output, papers)
            script = (ROOT / 'site/paper-search.js').read_bytes()
            self.assertEqual((output / 'paper-search.js').read_bytes(), script)
            indexes = set()
            for lang, path in [('en', 'papers/index.html'), ('zh', 'zh/papers/index.html')]:
                html = (output / path).read_text()
                prefix = '/zh' if lang == 'zh' else ''
                self.assertEqual(len(re.findall(r'<article class="paper-card"', html)), len(papers))
                # The form occupies its space from first paint; only scripting:none hides it.
                form = re.search(r'<form id="paper-search"[^>]*>', html)[0]
                self.assertIn('class="paper-search script-only"', form)
                self.assertNotRegex(form, r'\bhidden\b')
                self.assertIn('@media(scripting:none){.script-only{display:none!important}}', (ROOT / 'site/styles.css').read_text())
                self.assertRegex(html, r'<button id="paper-clear"[^>]* disabled>')
                initial = f'Showing {len(papers)} of {len(papers)} papers' if lang == 'en' else f'显示 {len(papers)} / {len(papers)} 篇论文'
                self.assertIn(f'aria-atomic="true">{initial}</p>', html)
                self.assertRegex(html, r'<select id="paper-layout"><option value="compact">[^<]+</option><option value="cards">[^<]+</option></select>')
                self.assertNotRegex(html, r'<article[^>]*\bhidden\b')
                self.assertIn('data-paper-layout="compact"', html)
                self.assertIn('<summary>' + ('研究范围与作者' if lang == 'zh' else 'Scope & authors') + '</summary>', html)
                self.assertIn('/assets/paper-search.' + hashlib.sha256(script).hexdigest()[:16] + '.js', html)
                # The index is a content-addressed file shared by both languages and preloaded as the fetch the script makes.
                self.assertNotIn('paper-search-data', html)
                href, projection = search_index(output, html)
                self.assertEqual(href, '/assets/paper-search-index.' + hashlib.sha256((output / href.lstrip('/')).read_bytes()).hexdigest()[:16] + '.json')
                self.assertIn(f'<link rel="preload" href="{href}" as="fetch" crossorigin>', html)
                indexes.add(href)
                self.assertEqual(projection['schema_version'], 1)
                self.assertEqual([row['id'] for row in projection['papers']], re.findall(r'data-paper-id="([^"]+)"', html))
                indexed_by_id = {row['id']: row for row in projection['papers']}
                self.assertEqual(set(indexed_by_id), {row['id'] for row in papers})
                for original in papers:
                    indexed = indexed_by_id[original['id']]
                    self.assertEqual(indexed, {key: original.get(key) for key in SEARCH_FIELDS})
                    card = re.search(r'<article class="paper-card" id="' + original['id'] + r'".*?</article>', html, re.S)[0]
                    disclosure = re.search(r'<details class="paper-details">(.*?)</details>', card, re.S)[1]
                    # Scope, authors and the citation stay in the card's disclosure.
                    self.assertIn(escape(original['scope_limitations_' + lang]), disclosure)
                    self.assertIn(escape('; '.join(original['authors'])), disclosure)
                    self.assertEqual(card.count('class="paper-scope"'), 1)
                    self.assertEqual(card.count('class="paper-authors"'), 1)
                    self.assertIn(escape(original['description_' + lang]), card.split('<details', 1)[0])
                    self.assertIn('/papers/citations/' + original['id'] + '.bib', disclosure)
                    self.assertIn('href="' + escape(original['url'], quote=True) + '"', card)
                    if lang == 'zh':
                        self.assertIn(escape(original['title']), disclosure)
                    # Sources, the fit rationale, dates, identifiers and review notes are on the entry page only.
                    for field in ('why_fits_' + lang, 'metadata_notes_zh' if lang == 'zh' else 'metadata_notes',
                                  'date_basis_zh' if lang == 'zh' else 'date_basis'):
                        self.assertNotIn(escape(original[field]), card)
                    self.assertNotIn('<dl>', card)
                    hrefs = set(re.findall(r'href="([^"]+)"', card))
                    self.assertLessEqual(hrefs, {escape(original[field], quote=True) for field in ('url', 'pdf_url', 'code_url', 'project_url') if original.get(field)}
                                         | {f'/papers/citations/{original["id"]}.bib', f'{prefix}/papers/{original["id"]}/', f'{prefix}/papers/{original["id"]}/#entry-sources'})
                    sources = len(dict.fromkeys(original['evidence_urls']))
                    footer = re.search(r'<p class="paper-sources"><a href="([^"]+)" aria-label="([^"]+)">(.*?)</a></p>', card)
                    self.assertEqual(footer[1], f'{prefix}/papers/{original["id"]}/#entry-sources')
                    checked = original['verified_at'][:10]
                    time = f'<time datetime="{original["verified_at"]}">{checked}</time>'
                    self.assertEqual(footer[3], (f'{sources} 个来源 · 复核于&nbsp;{time}' if lang == 'zh'
                                                 else f'{sources} source{"" if sources == 1 else "s"} · checked&nbsp;{time}')
                                     + '<span aria-hidden="true">&nbsp;→</span>')
                    title = escape(original['title_zh' if lang == 'zh' else 'title'], quote=True)
                    self.assertTrue(footer[2].startswith(title + ('：完整条目中的 ' if lang == 'zh' else ': ')), footer[2])
                    self.assertIn(checked, footer[2])
                    self.assertEqual((output / 'papers/citations' / (original['id'] + '.bib')).read_text(), bibtex_text(original))
                self.assertIn('role="status" aria-live="polite" aria-atomic="true"', html)
                self.assertIn('aria-describedby="paper-search-help"', html)
            self.assertEqual(len(indexes), 1, 'both languages share one index')

    def test_markup_in_a_title_stays_text_in_the_page_and_data_in_the_index(self):
        paper = json.loads((ROOT / 'data/papers.json').read_text())[0]
        paper['title'] = '</script><script>alert("example")</script> & title'
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build_paper_pages(output, [paper])
            html = (output / 'papers/index.html').read_text()
            self.assertNotIn('<script>alert', html)
            self.assertIn(escape(paper['title']), html)
            self.assertEqual(search_index(output, html)[1]['papers'][0]['title'], paper['title'])

    def test_changed_search_fields_get_a_new_index_name(self):
        papers = json.loads((ROOT / 'data/papers.json').read_text())[:3]
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            build_paper_pages(Path(first), papers)
            build_paper_pages(Path(second), [{**papers[0], 'venue': papers[0]['venue'] + ' (revised)'}, *papers[1:]])
            names = [search_index(directory, (Path(directory) / 'papers/index.html').read_text())[0] for directory in (first, second)]
        self.assertNotEqual(*names)

    def test_browser_search_and_composition_contract(self):
        result = subprocess.run(['node', str(ROOT / 'tests/paper_search_ui.cjs')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
