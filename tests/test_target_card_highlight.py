"""Keep the listing card that an entry page links to visibly marked when the page opens at its fragment."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
STYLES = re.sub(r'/\*.*?\*/', '', (ROOT / 'site' / 'styles.css').read_text(encoding='utf-8'), flags=re.S)
CARDS = ('.resource-card', '.case-row', '.paper-card')


def rules(text):
    """Return (selector, declarations) pairs, including those nested in at-rules."""
    return [(selector.strip(), body) for selector, body in re.findall(r'([^{}]+)\{([^{}]*)\}', text)]


def forced_colors_block(text):
    match = re.search(r'@media\(forced-colors:active\)\{(.*?\})\}', text.split(':target', 1)[1])
    return match.group(1) if match else ''


class TargetCardHighlightTests(unittest.TestCase):
    def test_each_listing_card_has_a_target_outline_and_tint(self):
        for card in CARDS:
            matching = [body for selector, body in rules(STYLES)
                        if f'{card}:target' in selector.split(',') and 'outline:' in body]
            with self.subTest(card=card):
                self.assertTrue(matching, f'{card}:target has no outline rule')
                self.assertIn('background:var(--tint)', matching[0])
                self.assertRegex(matching[0], r'outline:3px solid var\(--link\)')

    def test_outline_contrasts_with_the_page_and_the_tint(self):
        def luminance(name):
            value = re.search(rf'--{name}:#([0-9a-f]{{3}}|[0-9a-f]{{6}});', STYLES).group(1)
            value = ''.join(c * 2 for c in value) if len(value) == 3 else value
            channels = [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)]
            linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
            return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

        for background in ('paper', 'tint'):
            light, dark = sorted((luminance('link'), luminance(background)), reverse=True)
            with self.subTest(background=background):
                self.assertGreaterEqual((light + 0.05) / (dark + 0.05), 3)

    def test_borderless_rows_extend_the_tint_without_changing_padding(self):
        for selector, body in rules(STYLES):
            if '.case-row:target' in selector and 'box-shadow' in body:
                self.assertIn('html[data-paper-layout="compact"] .paper-card:target', selector)
                self.assertNotIn('padding', body)
                break
        else:
            self.fail('borderless target rows have no tint extension')

    def test_forced_colors_keep_a_system_color_outline(self):
        block = forced_colors_block(STYLES)
        for card in CARDS:
            with self.subTest(card=card):
                self.assertIn(f'{card}:target', block)
        self.assertIn('outline-color:Highlight', block)

    def test_target_style_does_not_animate(self):
        target_rules = [body for selector, body in rules(STYLES) if ':target' in selector]
        self.assertTrue(target_rules)
        for body in target_rules:
            self.assertNotIn('transition', body)
            self.assertNotIn('animation', body)

    def test_generated_listing_cards_carry_their_fragment_ids(self):
        discovery = (ROOT / 'scripts' / 'build_discovery_pages.py').read_text(encoding='utf-8')
        papers = (ROOT / 'scripts' / 'build_paper_pages.py').read_text(encoding='utf-8')
        self.assertIn('<article class="resource-card browse-repository" id="{escape(record[\'id\'], quote=True)}"', discovery)
        self.assertIn('<article class="case-row" id="{identifier}"', discovery)
        self.assertIn('<article class="paper-card" id="{paper[\'id\']}"', papers)


if __name__ == '__main__':
    unittest.main()
