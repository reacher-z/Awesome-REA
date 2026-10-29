"""The paper directory keeps three navigation landmarks however many papers it lists."""
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_paper_pages import build_paper_pages


class Landmarks(HTMLParser):
    """Collect navigation landmark names and, per paper card, the link texts inside its link list."""
    def __init__(self):
        super().__init__()
        self.navs, self.cards, self.stack = [], {}, []
        self.card = self.list_depth = None
        self.text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'nav' or attrs.get('role') == 'navigation':
            self.navs.append(attrs.get('aria-label'))
        if tag == 'article' and 'data-paper-id' in attrs:
            self.card = attrs['data-paper-id']; self.cards[self.card] = []
        if tag == 'ul' and attrs.get('class') == 'paper-links':
            self.list_depth = 0
        if self.list_depth is not None:
            if tag == 'li':
                self.list_depth += 1
            if tag == 'a':
                self.text = []

    def handle_endtag(self, tag):
        if self.list_depth is not None and tag == 'a':
            self.cards[self.card].append(''.join(self.text).strip())
        if self.list_depth is not None and tag == 'ul':
            self.list_depth = None

    def handle_data(self, data):
        self.text.append(data)


class PaperLandmarkTests(unittest.TestCase):
    def test_links_are_a_plain_list_not_a_landmark_per_paper(self):
        papers = json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build_paper_pages(output, papers)
            for path, names, zh in (
                    ('papers/index.html', ['Main navigation', 'Breadcrumb', 'Research areas'], False),
                    ('zh/papers/index.html', ['主导航', '当前位置', '研究方向'], True)):
                parser = Landmarks()
                parser.feed((output / path).read_text(encoding='utf-8'))
                self.assertEqual(parser.navs, names, path)
                self.assertEqual(set(parser.cards), {paper['id'] for paper in papers})
                for paper in papers:
                    # External links end with the fallback ↗ icon text; order and labels are unchanged. The title
                    # links to the paper and BibTeX sits in the card's details, so neither is in this list.
                    expected = ['PDF↗', '完整条目' if zh else 'Full entry']
                    expected += [label + '↗' for field, label in (('code_url', '代码' if zh else 'Code'),
                                                                  ('project_url', '项目' if zh else 'Project')) if paper.get(field)]
                    self.assertEqual(parser.cards[paper['id']], expected, paper['id'])


if __name__ == '__main__':
    unittest.main()
