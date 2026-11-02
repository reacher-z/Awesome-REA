"""Every section heading row on /resources/ and /cases/ links back to the section index above the first section."""
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_discovery_pages import build_discovery_pages

INDEXES = {'/resources/': 'resource-categories', '/zh/resources/': 'resource-categories',
           '/cases/': 'case-subjects', '/zh/cases/': 'case-subjects'}
LABELS = {'/resources/': 'All sections', '/zh/resources/': '全部分类',
          '/cases/': 'All sections', '/zh/cases/': '全部主题'}


def record(identifier, targets, kind='case-study'):
    return {'id': identifier, 'name': 'Example ' + identifier, 'name_zh': '案例 ' + identifier,
            'url': 'https://example.org/' + identifier, 'category': 'reconstruction-cases',
            'kind': kind, 'relationship': 'independent-reconstruction', 'targets': targets,
            'description_en': 'Reconstructs one observed behavior; complete equivalence is untested.',
            'description_zh': '重建一个观测行为；完整等价尚未测试。',
            'requirements': ['Requires the original input; no runtime was executed.'],
            'requirements_zh': ['需要原始输入；没有执行上游程序。'],
            'evidence_url': 'https://example.org/evidence/' + identifier,
            'verified_at': '2026-10-16T12:30:00Z', 'verification': 'source-reviewed'}


class HeadingRows(HTMLParser):
    """Collect the nav ids and, for each section heading row, its heading id, count text and links."""

    def __init__(self, text):
        super().__init__()
        self.navs, self.rows, self._row, self._field = [], [], None, None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'nav':
            self.navs.append(values.get('id'))
        if tag == 'div' and values.get('class') == 'browse-topline':
            self._row = {'heading': None, 'count': '', 'links': []}
            self.rows.append(self._row)
        if self._row is None:
            return
        if tag == 'h2':
            self._row['heading'] = values.get('id')
        elif tag == 'p':
            self._field = 'count'
        elif tag == 'a' and values.get('href'):
            self._row['links'].append({'href': values['href'], 'class': values.get('class'), 'text': ''})
            self._field = 'link'

    def handle_endtag(self, tag):
        if tag == 'div' and self._row is not None:
            self._row = None
        if tag in ('p', 'a'):
            self._field = None

    def handle_data(self, data):
        if self._row is None or self._field is None:
            return
        if self._field == 'count':
            self._row['count'] += data
        else:
            self._row['links'][-1]['text'] += data


class SectionIndexLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        resources = [record('web-case', ['website']), record('game-case', ['game']),
                     record('firmware-tool', ['firmware'], 'tool')]
        with TemporaryDirectory() as directory:
            output = Path(directory)
            build_discovery_pages(output, {'meta': {}, 'resources': resources}, None)
            cls.pages = {route: HeadingRows((output / route.strip('/') / 'index.html').read_text(encoding='utf-8'))
                         for route in INDEXES}

    def test_every_section_row_links_once_to_the_page_index(self):
        for route, index in INDEXES.items():
            page = self.pages[route]
            with self.subTest(route=route):
                self.assertEqual(page.navs.count(index), 1)
                self.assertGreaterEqual(len(page.rows), 2)
                for row in page.rows:
                    back = [link for link in row['links'] if link['class'] == 'section-index-link']
                    self.assertEqual(len(back), 1, row)
                    self.assertEqual(back[0]['href'], '#' + index)
                    self.assertEqual(back[0]['text'].replace('↑', '').strip(), LABELS[route])

    def test_headings_ids_and_counts_are_unchanged(self):
        expected = {'/resources/': [('heading-website', '1 resources'), ('heading-game', '1 resources'),
                                    ('heading-native-binary', '1 resources')],
                    '/zh/resources/': [('heading-website', '1 项资源'), ('heading-game', '1 项资源'),
                                       ('heading-native-binary', '1 项资源')],
                    '/cases/': [('case-heading-website', '1 case'), ('case-heading-game', '1 case')],
                    '/zh/cases/': [('case-heading-website', '1 个案例'), ('case-heading-game', '1 个案例')]}
        for route, rows in expected.items():
            with self.subTest(route=route):
                self.assertEqual([(row['heading'], row['count']) for row in self.pages[route].rows], rows)

    def test_link_is_underlined_and_keeps_the_count_style(self):
        css = (ROOT / 'site' / 'browse.css').read_text(encoding='utf-8')
        link = re.search(r'\.section-index-link\{([^}]*)\}', css)
        self.assertIsNotNone(link)
        self.assertIn('text-decoration:underline', link.group(1))
        self.assertIn('white-space:nowrap', link.group(1))
        # The count keeps its 14px size now that it is no longer the row's last child.
        self.assertIn('.browse-topline p:last-of-type{font-size:14px}', css)
        self.assertNotIn('.browse-topline p:last-child', css)
        styles = (ROOT / 'site' / 'styles.css').read_text(encoding='utf-8')
        self.assertRegex(styles, r'a:focus-visible[^{]*\{outline:3px solid var\(--link\)')


if __name__ == '__main__':
    unittest.main()
