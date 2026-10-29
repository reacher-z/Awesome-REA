"""The site declares light and dark color schemes and restates every palette token for dark mode."""
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from open_graph import THEME_COLOR_META
from validate_site import Page, validate_theme_color

DARK = '@media (prefers-color-scheme: dark)'


def token_blocks(css):
    """Return the light :root tokens declared before the dark media query and the tokens it redefines."""
    dark_at = css.index(DARK)
    depth, end = 0, None
    for index in range(css.index('{', dark_at), len(css)):
        depth += {'{': 1, '}': -1}.get(css[index], 0)
        if depth == 0:
            end = index
            break
    pattern = r'(--[\w-]+):\s*([^;}]+)'
    return dict(re.findall(pattern, css[:dark_at])), dict(re.findall(pattern, css[dark_at:end]))


class ColorSchemeTests(unittest.TestCase):
    def test_every_color_token_has_a_dark_value(self):
        styles = (ROOT / 'site/styles.css').read_text(encoding='utf-8')
        self.assertIn('color-scheme:light dark;', styles.split('}', 1)[0])
        for name in ('styles.css', 'papers.css', 'survey.css'):
            with self.subTest(stylesheet=name):
                light, dark = token_blocks((ROOT / 'site' / name).read_text(encoding='utf-8'))
                colors = {key for key, value in light.items() if value.strip().startswith('#')}
                self.assertTrue(colors)
                self.assertEqual(colors, set(dark), 'each light color token needs exactly one dark value')
                self.assertTrue(all(re.fullmatch(r'#[0-9a-f]{6}(?:[0-9a-f]{2})?', value.strip()) for value in dark.values()))

    def test_components_use_tokens_for_text_on_ink(self):
        # Ink-filled controls turn light in dark mode, so their text must follow --on-ink, never a fixed white.
        for name in ('styles.css', 'browse.css', 'entry.css', 'papers.css', 'survey.css', 'cases.css'):
            css = (ROOT / 'site' / name).read_text(encoding='utf-8')
            screen = re.sub(r'@media print\s*\{.*?\n\}', '', css, flags=re.S)
            with self.subTest(stylesheet=name):
                self.assertNotRegex(screen, r'(?<![\w-])(?:color|background):#fff\b')

    def test_theme_color_follows_the_page_canvas_in_both_schemes(self):
        _, dark = token_blocks((ROOT / 'site/styles.css').read_text(encoding='utf-8'))
        self.assertEqual(re.findall(r'content="(#[0-9a-f]{6})" media="\(prefers-color-scheme: (light|dark)\)"', THEME_COLOR_META),
                         [('#ffffff', 'light'), (dark['--paper'].strip(), 'dark')])
        index = (ROOT / 'site/index.html').read_text(encoding='utf-8')
        for tag in re.findall(r'<meta[^>]+>', THEME_COLOR_META):
            self.assertIn(tag, index)
        self.assertEqual(index.count('name="theme-color"'), 2)
        validate_theme_color('/', Page(f'<html><head>{THEME_COLOR_META}</head></html>'))
        for head in ('<meta name="theme-color" content="#ffffff">', THEME_COLOR_META.split('>')[0] + '>', ''):
            with self.subTest(head=head), self.assertRaises(AssertionError):
                validate_theme_color('/', Page(f'<html><head>{head}</head></html>'))


if __name__ == '__main__':
    unittest.main()
