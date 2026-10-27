"""Target sections on /resources/ and /cases/ count every entry carrying their tag and link the filtered view."""
from collections import Counter
from html import unescape
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_discovery_pages import NAMED_ELSEWHERE_LIMIT, SECTION_TARGETS, build_discovery_pages
from build_readme import collection_section
from validate_site import Page, validate_case_outputs


def record(identifier, targets, kind='case-study', category='reconstruction-cases', relationship='independent-reconstruction'):
    return {'id': identifier, 'name': 'Example ' + identifier, 'name_zh': '示例 ' + identifier,
            'url': 'https://example.org/' + identifier, 'category': category, 'kind': kind,
            'relationship': relationship, 'targets': targets,
            'description_en': 'Documents one behavior; equivalence is untested.', 'description_zh': '记录一个行为；尚未测试等价性。',
            'requirements': ['Requires the original input.'], 'requirements_zh': ['需要原始输入。'],
            'evidence_url': 'https://example.org/evidence/' + identifier,
            'verified_at': '2026-10-16T12:30:00Z', 'verification': 'source-reviewed'}


LINE = re.compile(r'<p class="section-target-count" data-section-target="([a-z]+)" data-target-tagged="(\d+)" '
                  r'data-target-elsewhere="(\d+)">(.*?)</p>', re.S)


class SectionTargetCountTests(unittest.TestCase):
    def setUp(self):
        # Protocol is carried by a protocol tool, a protocol case and an app case, so the Protocol
        # section holds two entries while three carry the tag; the app case is named as filed elsewhere.
        self.resources = [
            record('protocol-case', ['protocol']),
            record('app-case', ['app', 'protocol']),
            record('protocol-tool', ['protocol', 'binary'], 'tool', 'protocol-analysis', 'foundation'),
            record('native-tool', ['binary'], 'tool', 'native-analysis', 'foundation'),
            *[record(f'game-tool-{index}', ['game', 'binary'], 'tool', 'game-analysis', 'foundation') for index in range(NAMED_ELSEWHERE_LIMIT + 1)],
            record('reference', ['website'], 'documentation', 'learning', 'learning'),
        ]
        with TemporaryDirectory() as directory:
            output = Path(directory)
            build_discovery_pages(output, {'meta': {}, 'resources': self.resources}, None)
            self.html = {route: (output / route.lstrip('/') / 'index.html').read_text()
                         for route in ('/resources/', '/zh/resources/', '/cases/', '/zh/cases/')}

    def lines(self, route):
        return {target: (int(tagged), int(elsewhere), body) for target, tagged, elsewhere, body in LINE.findall(self.html[route])}

    def test_counts_are_computed_from_every_tagged_record(self):
        for route in self.html:
            cases = '/cases/' in route
            records = [row for row in self.resources if not cases or row['kind'] == 'case-study']
            sections = {collection_section(row) for row in records}
            expected = {}
            for section, target in SECTION_TARGETS.items():
                if section in sections:
                    tagged = [row for row in records if target in row['targets']]
                    expected[target] = (len(tagged), sum(collection_section(row) != section for row in tagged))
            lines = self.lines(route)
            self.assertEqual({target: values[:2] for target, values in lines.items()}, expected, route)
            # Non-target sections (here References and learning) get no tag line.
            self.assertEqual(self.html[route].count('class="section-target-count"'), len(expected))
        self.assertEqual(self.lines('/resources/')['protocol'][:2], (3, 1))
        self.assertEqual(self.lines('/resources/')['binary'][:2], (NAMED_ELSEWHERE_LIMIT + 3, NAMED_ELSEWHERE_LIMIT + 2))
        self.assertEqual(self.lines('/cases/')['protocol'][:2], (2, 1))

    def test_links_open_the_matching_homepage_filter_and_name_few_entries(self):
        for route in self.html:
            zh, cases = route.startswith('/zh/'), '/cases/' in route
            for target, (tagged, elsewhere, body) in self.lines(route).items():
                hrefs = [unescape(href) for href in re.findall(r'href="([^"]+)"', body)]
                filter_url = urlsplit(hrefs[-1])
                self.assertEqual(filter_url.path, '/zh/' if zh else '/')
                self.assertEqual(filter_url.fragment, 'catalog')
                query = {key: values[0] for key, values in parse_qs(filter_url.query).items()}
                self.assertEqual(query, {'view': 'curated', 'target': target, **({'kind': 'case-study'} if cases else {}),
                                         **({} if zh else {'lang': 'en'})})
                named = hrefs[:-1]
                section = next(key for key, value in SECTION_TARGETS.items() if value == target)
                pool = [row for row in self.resources if (not cases or row['kind'] == 'case-study') and target in row['targets']
                        and collection_section(row) != section]
                if elsewhere <= NAMED_ELSEWHERE_LIMIT:
                    self.assertEqual(named, [('/zh' if zh else '') + f"/resources/{row['id']}/" for row in pool])
                else:
                    self.assertEqual(named, [])
        english = self.lines('/resources/')['protocol'][2]
        self.assertIn('3 entries tagged Protocol · 1 filed in another section: <a href="/resources/app-case/">Example app-case</a>', english)
        self.assertIn('aria-label="Show all 3 entries tagged Protocol in search">Show all 3 →</a>', english)
        chinese = self.lines('/zh/cases/')['protocol'][2]
        self.assertIn('2 个案例带“协议”标签 · 其中 1 个归入其他主题：<a href="/zh/resources/app-case/">示例 app-case</a>', chinese)
        self.assertIn('查看全部 2 个 →', chinese)

    def test_each_card_still_renders_once_and_chip_counts_match_sections(self):
        for route, text in self.html.items():
            cards = Counter(re.findall(r'data-resource-id="([^"]+)"', text))
            self.assertTrue(cards and set(cards.values()) == {1}, route)
            chips = dict(re.findall(r'<a href="#(?:cases-)?([a-z-]+)">[^<]+<span>(\d+)</span></a>', text))
            self.assertGreaterEqual(len(chips), 2, route)
            for section, count in chips.items():
                body = re.search(rf'id="(?:cases-|heading-){section}".*?(?=<section|</main>|$)', text, re.S)[0]
                self.assertEqual(len(re.findall(r'data-resource-id=', body)), int(count), (route, section))
        validate_case_outputs({route: Page(self.html[route]) for route in ('/cases/', '/zh/cases/')}, self.resources)


if __name__ == '__main__':
    unittest.main()
