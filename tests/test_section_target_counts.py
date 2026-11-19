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
from build_discovery_pages import SECTION_TARGETS, build_discovery_pages
from build_readme import collection_section
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
ROUTES = ('/cases/', '/zh/cases/')
# A top-level section starts at its own heading; sub-group sections are labelled by two IDs and stay inside it.
SECTION = re.compile(r'<section (?:class="case-section" id="cases-([a-z-]+)"|aria-labelledby="heading-([a-z-]+)")')
# The visible number of a count line, per language: entries carrying the tag.
VISIBLE = {'en': r'^(\d+) (?:entry|entries|case|cases) tagged ', 'zh': r'^(\d+) (?:项|个案例)带“'}
# More entries than one screen of links would hold, so the fixture also covers a long tail.
MANY = 9


def build(resources):
    with TemporaryDirectory() as directory:
        output = Path(directory)
        build_discovery_pages(output, {'meta': {}, 'resources': resources}, None)
        validate_section_target_counts(output, resources)
        # /cases/ and its later static pages, joined so each section's cards add up across them.
        return {route: [(output / route.lstrip('/') / 'index.html').read_text()]
                + [path.read_text() for path in sorted((output / route.lstrip('/') / 'page').glob('*/index.html'), key=lambda path: int(path.parent.name))]
                for route in ROUTES}


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
    """Each top-level section's key, heading count, card count and count line (target, numbers, plain text).

    Given the static pages of one listing, a section's cards add up across them and its line comes from its first page.
    """
    if isinstance(html, list):
        merged = {}
        for part in html:
            for key, row in section_rows(part).items():
                if key in merged:
                    assert merged[key]['heading'] == row['heading'] and not (merged[key]['line'] and row['line']), key
                    merged[key] = {**merged[key], 'cards': merged[key]['cards'] + row['cards'], 'line': merged[key]['line'] or row['line']}
                else:
                    merged[key] = row
        return merged
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
        *[record(f'app-tracer-{index}', ['app'], 'tool', 'dynamic-analysis', 'foundation') for index in range(MANY + 1)],
        record('protocol-case', ['protocol']),
        record('app-case', ['app', 'protocol']),
        record('protocol-tool', ['protocol', 'binary'], 'tool', 'protocol-analysis', 'foundation'),
        record('native-tool', ['binary'], 'tool', 'native-analysis', 'foundation'),
        *[record(f'game-tool-{index}', ['game', 'binary'], 'tool', 'game-analysis', 'foundation') for index in range(MANY + 1)],
        record('reference', ['website'], 'documentation', 'learning', 'learning'),
    ]


class SectionTargetCountTests(unittest.TestCase):
    def setUp(self):
        self.resources = fixture()
        # The fixture fits on one static page.
        self.html = {route: pages[0] for route, pages in build(self.resources).items() if len(pages) == 1}
        self.assertEqual(set(self.html), set(ROUTES))

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
        self.assertEqual(self.lines('/cases/')['protocol'][:3], (2, 1, 0))
        self.assertEqual(self.lines('/cases/')['website'][:3], (1, 0, 1))

    def test_each_line_states_the_count_and_links_the_matching_homepage_filter(self):
        for route in self.html:
            zh, cases = route.startswith('/zh/'), '/cases/' in route
            for target, (tagged, elsewhere, untagged, body) in self.lines(route).items():
                hrefs = [unescape(href) for href in re.findall(r'href="([^"]+)"', body)]
                self.assertEqual(len(hrefs), 1, (route, target))
                filter_url = urlsplit(hrefs[0])
                self.assertEqual(filter_url.path, '/zh/' if zh else '/')
                self.assertEqual(filter_url.fragment, 'catalog')
                query = {key: values[0] for key, values in parse_qs(filter_url.query).items()}
                self.assertEqual(query, {'view': 'curated', 'target': target, **({'kind': 'case-study'} if cases else {}),
                                         **({} if zh else {'lang': 'en'})})
        chinese = self.lines('/zh/cases/')['protocol'][3]
        self.assertTrue(chinese.startswith('2 个案例带“协议”标签 · <a '), chinese)
        self.assertIn('查看全部 2 个 →', chinese)

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
    tagged, minus filed elsewhere, plus listed here without the tag, as the attributes state; the line shows the tagged count."""

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
                    self.assertEqual(int(re.match(VISIBLE[language], text)[1]), tagged, text)

    def test_fixture_sections_reconcile(self):
        self.assert_reconciled(build(fixture()), fixture())

    def test_current_catalog_sections_reconcile(self):
        resources = current_resources()
        pages = build(resources)
        self.assert_reconciled(pages, resources)


if __name__ == '__main__':
    unittest.main()
