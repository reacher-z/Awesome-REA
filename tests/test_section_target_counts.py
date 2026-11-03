"""Target sections on /resources/ and /cases/ count every entry carrying their tag, link the filtered view,
and reconcile with the section count: tagged, minus filed elsewhere, plus listed here without the tag."""
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
from build_readme import TARGETS, collection_section
from build_site import default_targets
from catalog import load_resources
from curated_translations import read_curated_translations
from validate_site import Page, validate_case_outputs, validate_section_target_counts


def record(identifier, targets, kind='case-study', category='reconstruction-cases', relationship='independent-reconstruction'):
    return {'id': identifier, 'name': 'Example ' + identifier, 'name_zh': '示例 ' + identifier,
            'url': 'https://example.org/' + identifier, 'category': category, 'kind': kind,
            'relationship': relationship, 'targets': targets,
            'description_en': 'Documents one behavior; equivalence is untested.', 'description_zh': '记录一个行为；尚未测试等价性。',
            'requirements': ['Requires the original input.'], 'requirements_zh': ['需要原始输入。'],
            'evidence_url': 'https://example.org/evidence/' + identifier,
            'verified_at': '2026-10-16T12:30:00Z', 'verification': 'source-reviewed'}


LINE = re.compile(r'<p class="section-target-count" data-section-target="([a-z]+)" data-target-tagged="(\d+)" '
                  r'data-target-elsewhere="(\d+)" data-target-untagged-here="(\d+)">(.*?)</p>', re.S)
ROUTES = ('/resources/', '/zh/resources/', '/cases/', '/zh/cases/')
# A top-level section starts at its own heading; sub-group sections are labelled by two IDs and stay inside it.
SECTION = re.compile(r'<section (?:class="case-section" id="cases-([a-z-]+)"|aria-labelledby="heading-([a-z-]+)")')
# The visible numbers of a count line, per language: tagged, filed elsewhere, listed here without the tag.
VISIBLE = {
    'en': (r'^(\d+) (?:entry|entries|case|cases) tagged ', r' · (\d+) filed in (?:another section|other sections)',
           r' · (\d+) listed here by category without the (.+?) tag'),
    'zh': (r'^(\d+) (?:项|个案例)带“', r' · 其中 (\d+) (?:项|个)归入其他(?:分区|主题)',
           r' · 另有 (\d+) (?:项|个)按分类列于本节但不带“(.+?)”标签'),
}


def build(resources):
    with TemporaryDirectory() as directory:
        output = Path(directory)
        build_discovery_pages(output, {'meta': {}, 'resources': resources}, None)
        validate_section_target_counts(output, resources)
        return {route: (output / route.lstrip('/') / 'index.html').read_text() for route in ROUTES}


def current_resources():
    """The curated records with the Chinese names, requirements and targets build_site.py gives them."""
    translations, resources = read_curated_translations(), []
    for original in load_resources():
        row = dict(original)
        localized = translations.get(row['id'], {})
        row['name_zh'] = row.get('name_zh') or localized.get('name', row['name'])
        row['requirements_zh'] = row.get('requirements_zh') or localized.get('requirements', row['requirements'])
        row['targets'] = sorted(set(row.get('targets') or default_targets(row)))
        resources.append(row)
    return resources


def section_rows(html):
    """Each top-level section's key, heading count, card count and count line (target, numbers, plain text)."""
    html = html.split('</main>', 1)[0]
    starts = list(SECTION.finditer(html))
    rows = {}
    for start, end in zip(starts, [*starts[1:], None]):
        body = html[start.start():end.start() if end else None]
        line = LINE.search(body)
        rows[start[1] or start[2]] = {
            'heading': int(re.search(r'<div class="browse-topline">.*?<p>(\d+) ', body, re.S)[1]),
            'cards': len(re.findall(r'data-resource-id=', body)),
            'line': line and (line[1], *map(int, line.groups()[1:4]), unescape(re.sub(r'<[^>]+>', '', line[5]))),
        }
    return rows


def fixture():
    # Protocol is carried by a protocol tool, a protocol case and an app case, so the Protocol
    # section holds two entries while three carry the tag; the app case is named as filed elsewhere.
    # The WebAssembly tool and the web-analysis case sit in Websites by category without the Website tag,
    # and the dynamic-analysis app tools fall into Native binaries without the Binary tag.
    return [
        record('web-case', ['website']),
        record('wasm-case', ['app'], 'case-study', 'web-analysis'),
        record('wasm-tool', ['binary'], 'tool', 'webassembly', 'foundation'),
        *[record(f'app-tracer-{index}', ['app'], 'tool', 'dynamic-analysis', 'foundation') for index in range(NAMED_ELSEWHERE_LIMIT + 1)],
        record('protocol-case', ['protocol']),
        record('app-case', ['app', 'protocol']),
        record('protocol-tool', ['protocol', 'binary'], 'tool', 'protocol-analysis', 'foundation'),
        record('native-tool', ['binary'], 'tool', 'native-analysis', 'foundation'),
        *[record(f'game-tool-{index}', ['game', 'binary'], 'tool', 'game-analysis', 'foundation') for index in range(NAMED_ELSEWHERE_LIMIT + 1)],
        record('reference', ['website'], 'documentation', 'learning', 'learning'),
    ]


class SectionTargetCountTests(unittest.TestCase):
    def setUp(self):
        self.resources = fixture()
        self.html = build(self.resources)

    def lines(self, route):
        return {target: (int(tagged), int(elsewhere), int(untagged), body)
                for target, tagged, elsewhere, untagged, body in LINE.findall(self.html[route])}

    def test_counts_are_computed_from_every_tagged_record(self):
        for route in self.html:
            cases = '/cases/' in route
            records = [row for row in self.resources if not cases or row['kind'] == 'case-study']
            sections = {collection_section(row) for row in records}
            expected = {}
            for section, target in SECTION_TARGETS.items():
                if section in sections:
                    tagged = [row for row in records if target in row['targets']]
                    expected[target] = (len(tagged), sum(collection_section(row) != section for row in tagged),
                                        sum(target not in row['targets'] and collection_section(row) == section for row in records))
            lines = self.lines(route)
            self.assertEqual({target: values[:3] for target, values in lines.items()}, expected, route)
            # Non-target sections (here References and learning) get no tag line.
            self.assertEqual(self.html[route].count('class="section-target-count"'), len(expected))
        self.assertEqual(self.lines('/resources/')['protocol'][:3], (3, 1, 0))
        self.assertEqual(self.lines('/resources/')['binary'][:3], (NAMED_ELSEWHERE_LIMIT + 4, NAMED_ELSEWHERE_LIMIT + 3, NAMED_ELSEWHERE_LIMIT + 1))
        self.assertEqual(self.lines('/resources/')['website'][:3], (2, 1, 2))
        self.assertEqual(self.lines('/cases/')['protocol'][:3], (2, 1, 0))
        self.assertEqual(self.lines('/cases/')['website'][:3], (1, 0, 1))

    def test_links_open_the_matching_homepage_filter_and_name_few_entries(self):
        for route in self.html:
            zh, cases = route.startswith('/zh/'), '/cases/' in route
            for target, (tagged, elsewhere, untagged, body) in self.lines(route).items():
                hrefs = [unescape(href) for href in re.findall(r'href="([^"]+)"', body)]
                filter_url = urlsplit(hrefs[-1])
                self.assertEqual(filter_url.path, '/zh/' if zh else '/')
                self.assertEqual(filter_url.fragment, 'catalog')
                query = {key: values[0] for key, values in parse_qs(filter_url.query).items()}
                self.assertEqual(query, {'view': 'curated', 'target': target, **({'kind': 'case-study'} if cases else {}),
                                         **({} if zh else {'lang': 'en'})})
                section = next(key for key, value in SECTION_TARGETS.items() if value == target)
                listed = [row for row in self.resources if not cases or row['kind'] == 'case-study']
                # Few entries filed elsewhere, then few listed here without the tag, are named in that order.
                pools = ([row for row in listed if target in row['targets'] and collection_section(row) != section],
                         [row for row in listed if target not in row['targets'] and collection_section(row) == section])
                self.assertEqual((elsewhere, untagged), tuple(map(len, pools)))
                named = [('/zh' if zh else '') + f"/resources/{row['id']}/"
                         for pool in pools if len(pool) <= NAMED_ELSEWHERE_LIMIT for row in pool]
                self.assertEqual(hrefs[:-1], named, (route, target))
        english = self.lines('/resources/')['protocol'][3]
        self.assertIn('3 entries tagged Protocol · 1 filed in another section: <a href="/resources/app-case/">Example app-case</a> · <a ', english)
        self.assertIn('aria-label="Show all 3 entries tagged Protocol in search">Show all 3 →</a>', english)
        chinese = self.lines('/zh/cases/')['protocol'][3]
        self.assertIn('2 个案例带“协议”标签 · 其中 1 个归入其他主题：<a href="/zh/resources/app-case/">示例 app-case</a>', chinese)
        self.assertIn('查看全部 2 个 →', chinese)
        self.assertIn('2 entries tagged Website · 1 filed in another section: <a href="/resources/reference/">Example reference</a>'
                      ' · 2 listed here by category without the Website tag: <a href="/resources/wasm-case/">Example wasm-case</a>, '
                      '<a href="/resources/wasm-tool/">Example wasm-tool</a> · <a ', self.lines('/resources/')['website'][3])
        self.assertIn('1 个案例带“网站”标签 · 均在本节 · 另有 1 个按分类列于本节但不带“网站”标签：'
                      '<a href="/zh/resources/wasm-case/">示例 wasm-case</a> · <a ', self.lines('/zh/cases/')['website'][3])
        # More than NAMED_ELSEWHERE_LIMIT entries listed here without the tag are counted, not named.
        self.assertIn(f' · {NAMED_ELSEWHERE_LIMIT + 1} listed here by category without the Binary tag · <a ', self.lines('/resources/')['binary'][3])
        self.assertIn(f' · 另有 {NAMED_ELSEWHERE_LIMIT + 1} 项按分类列于本节但不带“二进制”标签 · <a ', self.lines('/zh/resources/')['binary'][3])

    def test_each_card_still_renders_once_and_chip_counts_match_sections(self):
        for route, text in self.html.items():
            cards = Counter(re.findall(r'data-resource-id="([^"]+)"', text))
            self.assertTrue(cards and set(cards.values()) == {1}, route)
            chips = dict(re.findall(r'<a href="#(?:cases-)?([a-z-]+)">[^<]+<span>(\d+)</span></a>', text))
            self.assertGreaterEqual(len(chips), 2, route)
            for section, count in chips.items():
                # A section's case-study and tool sub-groups are nested sections; stop at the next top-level one.
                body = re.search(rf'id="(?:cases-|heading-){section}".*?(?=<section(?! class="resource-subgroup")|</main>|$)', text, re.S)[0]
                self.assertEqual(len(re.findall(r'data-resource-id=', body)), int(count), (route, section))
        validate_case_outputs({route: Page(self.html[route]) for route in ('/cases/', '/zh/cases/')}, self.resources)



class SectionCountReconciliationTests(unittest.TestCase):
    """On both pages and in both languages, every section's count equals its cards and, for a target section,
    tagged, minus filed elsewhere, plus listed here without the tag, as both the attributes and the visible text state."""

    def assert_reconciled(self, pages, resources):
        for route, html in pages.items():
            language, cases = ('zh' if route.startswith('/zh/') else 'en'), '/cases/' in route
            records = [row for row in resources if not cases or row['kind'] == 'case-study']
            rows = section_rows(html)
            self.assertEqual(set(rows), {collection_section(row) for row in records}, route)
            for section, row in rows.items():
                with self.subTest(route=route, section=section):
                    self.assertEqual(row['heading'], row['cards'])
                    target = SECTION_TARGETS.get(section)
                    if target is None:
                        self.assertIsNone(row['line'])
                        continue
                    line_target, tagged, elsewhere, untagged, text = row['line']
                    self.assertEqual(line_target, target)
                    self.assertEqual(row['cards'], tagged - elsewhere + untagged, text)
                    first, filed, unlabelled = VISIBLE[language]
                    shown = re.search(unlabelled, text)
                    self.assertEqual((int(re.match(first, text)[1]), int((re.search(filed, text) or [0, 0])[1]),
                                      int(shown[1]) if shown else 0), (tagged, elsewhere, untagged), text)
                    if shown:
                        self.assertEqual(shown[2], TARGETS[target][language == 'zh'])

    def test_fixture_sections_reconcile(self):
        self.assert_reconciled(build(fixture()), fixture())

    def test_current_catalog_sections_reconcile(self):
        resources = current_resources()
        pages = build(resources)
        self.assert_reconciled(pages, resources)
        # The current catalog lists entries without the section's tag in at least one /resources/ section.
        self.assertTrue(any(row['line'] and row['line'][3] for row in section_rows(pages['/resources/']).values()))


if __name__ == '__main__':
    unittest.main()
