"""Verify progressive paper search preserves the complete static bibliography."""
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
from build_paper_pages import build_paper_pages, bibtex_text


class PaperSearchTests(unittest.TestCase):
    def test_real_bibliography_stays_complete_without_javascript(self):
        papers = json.loads((ROOT / 'data/papers.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build_paper_pages(output, papers)
            script = (ROOT / 'site/paper-search.js').read_bytes()
            self.assertEqual((output / 'paper-search.js').read_bytes(), script)
            for lang, path in [('en', 'papers/index.html'), ('zh', 'zh/papers/index.html')]:
                html = (output / path).read_text()
                self.assertEqual(len(re.findall(r'<article class="paper-card"', html)), len(papers))
                # The form occupies its space from first paint; only scripting:none hides it.
                form = re.search(r'<form id="paper-search"[^>]*>', html)[0]
                self.assertIn('class="paper-search script-only"', form)
                self.assertNotRegex(form, r'\bhidden\b')
                self.assertIn('@media(scripting:none){.script-only{display:none!important}}', (ROOT / 'site/styles.css').read_text())
                self.assertRegex(html, r'<button id="paper-clear"[^>]* disabled>')
                initial = f'Showing {len(papers)} of {len(papers)} papers' if lang == 'en' else f'显示 {len(papers)} / {len(papers)} 篇论文'
                self.assertIn(f'aria-atomic="true">{initial}</p>', html)
                self.assertNotRegex(html, r'<article[^>]*\bhidden\b')
                self.assertIn('/paper-search.js?v=' + hashlib.sha256(script).hexdigest()[:16], html)
                projection = json.loads(re.search(r'<script id="paper-search-data" type="application/json">(.*?)</script>', html, re.S)[1])
                self.assertEqual(projection['schema_version'], 1)
                self.assertEqual([row['id'] for row in projection['papers']], re.findall(r'data-paper-id="([^"]+)"', html))
                indexed_by_id = {row['id']: row for row in projection['papers']}
                self.assertEqual(set(indexed_by_id), {row['id'] for row in papers})
                for original in papers:
                    indexed = indexed_by_id[original['id']]
                    self.assertEqual(indexed, {key: original.get(key) for key in indexed})
                    self.assertIn(escape(original['description_' + lang]), html)
                    self.assertIn(escape(original['scope_limitations_' + lang]), html)
                    self.assertIn(escape(original['metadata_notes_zh' if lang == 'zh' else 'metadata_notes']), html)
                    self.assertIn('/papers/citations/' + original['id'] + '.bib', html)
                    self.assertEqual((output / 'papers/citations' / (original['id'] + '.bib')).read_text(), bibtex_text(original))
                self.assertIn('role="status" aria-live="polite" aria-atomic="true"', html)
                self.assertIn('aria-describedby="paper-search-help"', html)

    def test_search_projection_cannot_close_its_script_element(self):
        paper = json.loads((ROOT / 'data/papers.json').read_text())[0]
        paper['title'] = '</script><script>alert("example")</script> & title'
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build_paper_pages(output, [paper])
            html = (output / 'papers/index.html').read_text()
            encoded = re.search(r'<script id="paper-search-data" type="application/json">(.*?)</script>', html, re.S)[1]
            self.assertNotIn('<', encoded)
            self.assertEqual(json.loads(encoded)['papers'][0]['title'], paper['title'])

    def test_browser_search_and_composition_contract(self):
        result = subprocess.run(['node', str(ROOT / 'tests/paper_search_ui.cjs')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
