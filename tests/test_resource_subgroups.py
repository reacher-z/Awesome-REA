"""/resources/ lists each section's case studies and other kinds in two labelled sub-groups, as the README does."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_discovery_pages import build_discovery_pages


def record(identifier, kind, category, targets):
    relationship = 'independent-reconstruction' if kind == 'case-study' else 'foundation'
    return {'id': identifier, 'name': 'Example ' + identifier, 'name_zh': '示例 ' + identifier,
            'url': 'https://example.org/' + identifier, 'category': category, 'kind': kind,
            'relationship': relationship, 'targets': targets,
            'description_en': 'Describes one reviewed fixture.', 'description_zh': '描述一个已复核的测试条目。',
            'requirements': ['Requires the original input.'], 'requirements_zh': ['需要原始输入。'],
            'evidence_url': 'https://example.org/evidence/' + identifier,
            'verified_at': '2026-10-16', 'verification': 'source-reviewed'}


# Data order interleaves kinds, as the Games section does.
GAME = [record('game-case-a', 'case-study', 'reconstruction-cases', ['game']),
        record('game-tool', 'tool', 'game-analysis', ['game']),
        record('game-case-b', 'case-study', 'reconstruction-cases', ['game']),
        record('game-integration', 'integration', 'game-analysis', ['game']),
        record('game-case-c', 'case-study', 'reconstruction-cases', ['game', 'binary'])]
PROTOCOL = [record('protocol-tool', 'tool', 'protocol-analysis', ['protocol'])]


class Headings(HTMLParser):
    def __init__(self):
        super().__init__()
        self.levels, self.ids, self.in_main = [], [], False

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if tag == 'main':
            self.in_main = True
        if self.in_main and re.fullmatch(r'h[1-6]', tag):
            self.levels.append(int(tag[1]))
        if attributes.get('id'):
            self.ids.append(attributes['id'])

    def handle_endtag(self, tag):
        if tag == 'main':
            self.in_main = False


class ResourceSubgroupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with TemporaryDirectory() as directory:
            output = Path(directory)
            build_discovery_pages(output, {'meta': {}, 'resources': GAME + PROTOCOL}, None)
            cls.pages = {language: (output / route / 'index.html').read_text(encoding='utf-8')
                         for language, route in (('en', 'resources'), ('zh', 'zh/resources'))}

    def section(self, language, key):
        html = self.pages[language]
        start = html.index(f'<section aria-labelledby="heading-{key}">')
        end = html.find('<section aria-labelledby="heading-', start + 1)
        return html[start:end if end > 0 else len(html)]

    def test_mixed_sections_split_into_two_contiguous_labelled_subgroups(self):
        for language, labels, counts in (
            ('en', ['Case studies', 'Tools, projects and integrations'], ['3 case studies', '2 resources']),
            ('zh', ['案例', '工具、项目与集成'], ['3 个案例', '2 项资源']),
        ):
            with self.subTest(language=language):
                section = self.section(language, 'game')
                self.assertIn('<p>5 ' + ('项资源' if language == 'zh' else 'resources') + '</p>', section)
                headings = re.findall(r'<h3 id="(game--[a-z-]+)">([^<]+)</h3><p>([^<]+)</p>', section)
                self.assertEqual([heading[0] for heading in headings], ['game--case-studies', 'game--tools'])
                self.assertEqual([heading[1] for heading in headings], labels)
                self.assertEqual([heading[2] for heading in headings], counts)
                order = re.findall(r'data-record-id="([^"]+)"', section)
                self.assertEqual(order, ['game-case-a', 'game-case-b', 'game-case-c', 'game-tool', 'game-integration'],
                                 'case studies first in data order, then every other kind')
                groups = section.split('<section class="resource-subgroup"')[1:]
                self.assertEqual([len(re.findall(r'data-record-id=', group)) for group in groups], [3, 2],
                                 'sub-group counts add up to the section count')
                self.assertEqual(section.count('aria-labelledby="game--case-studies"'), 1)
                self.assertEqual(section.count('aria-labelledby="game--tools"'), 1)

    def test_single_kind_sections_stay_one_list(self):
        for language in ('en', 'zh'):
            section = self.section(language, 'protocol')
            self.assertNotIn('resource-subgroup', section)
            self.assertIn('<div class="card-heading"><h3>', section)

    def test_heading_levels_never_skip(self):
        for language, html in self.pages.items():
            with self.subTest(language=language):
                parser = Headings(); parser.feed(html)
                for previous, current in zip(parser.levels, parser.levels[1:]):
                    self.assertLessEqual(current, previous + 1, parser.levels)
                game = self.section(language, 'game')
                self.assertEqual(game.count('<div class="card-heading"><h4>'), 5)
                self.assertNotIn('<div class="card-heading"><h3>', game)

    def test_card_fragments_and_item_list_follow_the_rendered_order(self):
        for language, html in self.pages.items():
            with self.subTest(language=language):
                parser = Headings(); parser.feed(html)
                for item in GAME + PROTOCOL:
                    self.assertEqual(parser.ids.count(item['id']), 1, 'entry pages link /resources/#<id>')
                self.assertEqual(len(parser.ids), len(set(parser.ids)), 'sub-group IDs never collide with record IDs')
                schemas = [json.loads(payload) for payload in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
                collection = next(schema for schema in schemas if schema.get('@type') == 'CollectionPage')
                names = [element['name'] for element in collection['mainEntity']['itemListElement']]
                prefix = '示例 ' if language == 'zh' else 'Example '
                self.assertEqual(names, [prefix + identifier for identifier in
                                         ('game-case-a', 'game-case-b', 'game-case-c', 'game-tool', 'game-integration', 'protocol-tool')])


if __name__ == '__main__':
    unittest.main()
