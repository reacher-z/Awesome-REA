"""The about pages define REA with the same wording and upstream link as the README About sections."""
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_discovery_pages import REA_REPOSITORY_URL, build_discovery_pages


class FactCards(HTMLParser):
    """Collect each about-page card as (heading, visible paragraph text, paragraph links)."""

    def __init__(self, content):
        super().__init__(convert_charrefs=True)
        self.cards, self.field = [], None
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == 'section' and 'source-card' in (attributes.get('class') or '').split():
            self.cards.append({'heading': '', 'text': '', 'links': []})
        elif self.cards and tag in ('h2', 'p'):
            self.field = 'heading' if tag == 'h2' else 'text'
        elif self.cards and tag == 'a' and self.field == 'text':
            self.cards[-1]['links'].append(attributes.get('href'))

    def handle_endtag(self, tag):
        if tag in ('h2', 'p'):
            self.field = None

    def handle_data(self, data):
        if self.field:
            self.cards[-1][self.field] += data


def readme_definition(name, heading):
    about = (ROOT / name).read_text(encoding='utf-8').split(f'\n## {heading}\n', 1)[1].split('\n## ', 1)[0]
    paragraph = next(line for line in about.splitlines() if 'github.com/morluto/rea' in line)
    label, url, rest = re.fullmatch(r'\[([^\]]+)\]\(([^)]+)\)(.*)', paragraph).groups()
    return label + rest, url


class AboutPageReaTests(unittest.TestCase):
    def test_about_pages_define_rea_before_other_facts(self):
        resource = {'id': 'fixture', 'name': 'Fixture', 'name_zh': '测试', 'url': 'https://example.org/fixture',
                    'description_en': 'A fixture.', 'description_zh': '测试条目。', 'category': 'core',
                    'relationship': 'foundation', 'targets': ['app'], 'kind': 'tool',
                    'requirements': ['None.'], 'requirements_zh': ['无。'],
                    'evidence_url': 'https://example.org/fixture/evidence', 'verified_at': '2026-10-17',
                    'verification': 'source-reviewed'}
        with TemporaryDirectory() as directory:
            output = Path(directory)
            (output / 'index.html').write_text('<!doctype html>', encoding='utf-8')
            build_discovery_pages(output, {'resources': [resource], 'meta': {}}, None)
            for route, readme, heading, title, caveat in (
                ('about', 'README.md', 'About', 'REA and this collection', 'REA integration'),
                ('zh/about', 'README.zh-CN.md', '关于', '与 REA 的关系', 'REA 集成'),
            ):
                with self.subTest(route=route):
                    cards = FactCards((output / route / 'index.html').read_text(encoding='utf-8')).cards
                    expected_text, expected_url = readme_definition(readme, heading)
                    self.assertEqual(cards[0]['heading'], title)
                    self.assertEqual(cards[0]['text'], expected_text)
                    self.assertEqual(cards[0]['links'], [REA_REPOSITORY_URL])
                    self.assertEqual(expected_url, REA_REPOSITORY_URL)
                    # The existing caveat that inclusion does not establish REA integration remains.
                    self.assertTrue(any(caveat in card['text'] for card in cards[1:]))
                    # Every card link sits in prose that browse.css underlines (WCAG 1.4.1).
                    page = (output / route / 'index.html').read_text(encoding='utf-8')
                    self.assertIn('<main id="discovery-content" class="shell browse-main">', page)
                    self.assertEqual(len(re.findall(r'<p class="card-description">[^<]*<a ', page)),
                                     sum(len(card['links']) for card in cards))

    def test_card_prose_links_are_underlined_in_the_link_colour(self):
        styles = (ROOT / 'site/browse.css').read_text(encoding='utf-8')
        rule = re.search(r'(?m)^\.browse-main \.card-description a,[^{]*\{([^}]*)\}', styles)
        self.assertIsNotNone(rule)
        declarations = dict(part.split(':', 1) for part in rule[1].split(';') if part)
        self.assertEqual(declarations['color'], 'var(--link)')
        self.assertEqual(declarations['text-decoration'], 'underline')
        # Homepage cards are styled from styles.css and stay unchanged.
        self.assertNotIn('.card-description a', (ROOT / 'site/styles.css').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
