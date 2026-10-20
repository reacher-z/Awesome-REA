"""Paper search data carries each paper's venue, and both languages say venues are searchable."""
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_paper_pages import build_paper_pages


class PaperVenueSearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.papers = json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build_paper_pages(output, cls.papers)
            cls.html = {language: (output / path).read_text(encoding='utf-8')
                        for language, path in (('en', 'papers/index.html'), ('zh', 'zh/papers/index.html'))}

    def test_search_data_includes_every_venue(self):
        venues = {paper['id']: paper['venue'] for paper in self.papers}
        for language, html in self.html.items():
            projection = json.loads(re.search(r'<script id="paper-search-data" type="application/json">(.*?)</script>', html, re.S)[1])
            with self.subTest(language=language):
                self.assertEqual({row['id']: row['venue'] for row in projection['papers']}, venues)

    def test_search_hints_mention_venues_in_both_languages(self):
        expected = {'en': ('placeholder="Title, author, venue, DOI or arXiv ID"', 'Search titles, authors, summaries and venues'),
                    'zh': ('placeholder="标题、作者、出处、DOI 或 arXiv 编号"', '支持中英文搜索标题、作者、摘要及会议或期刊名称')}
        for language, needles in expected.items():
            for needle in needles:
                with self.subTest(language=language, needle=needle):
                    self.assertIn(needle, self.html[language])

    def test_venue_matching_in_the_shipped_module(self):
        result = subprocess.run(['node', str(ROOT / 'tests/paper_venue_search_ui.cjs')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)


if __name__ == '__main__':
    unittest.main()
