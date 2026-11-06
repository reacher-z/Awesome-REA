"""Every text pair of the Terra & Slate palette meets WCAG AA, computed from the tokens in site/shell.css."""
import re
import unittest
from pathlib import Path

SHELL = (Path(__file__).resolve().parents[1] / 'site/shell.css').read_text(encoding='utf-8')
AA = 4.5
LARGE = 3.0  # type of 24 px or larger, control borders


def tokens(block: str) -> dict[str, str]:
    return dict(re.findall(r'--([\w-]+):\s*(#[0-9A-Fa-f]{6})\b', block))


def block(selector: str) -> str:
    start = SHELL.index(selector + ' {')
    return SHELL[start:SHELL.index('color-scheme:', start)]


SHARED = tokens(SHELL[SHELL.index(':root {'):SHELL.index('@media (max-width: 767px)')])
LIGHT = {**SHARED, **tokens(block(':root[data-site="rea"]'))}
DARK = {**LIGHT, **tokens(block(':root[data-site="rea"][data-theme="dark"]'))}
SYSTEM_DARK = {**LIGHT, **tokens(block(':root[data-site="rea"]:not([data-theme="light"])'))}


def luminance(value: str) -> float:
    channels = [int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    r, g, b = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(one: str, two: str) -> float:
    high, low = sorted((luminance(one), luminance(two)), reverse=True)
    return (high + 0.05) / (low + 0.05)


# (foreground, background, minimum) for the tokens that change with the theme.
THEME_PAIRS = [(text, ground, AA) for text in ('ink-strong', 'ink', 'ink-2', 'brand-ink', 'label-case', 'callno', 'ok-fg', 'info-fg')
               for ground in ('bg', 'bg-raised')]
THEME_PAIRS += [(text, ground, AA) for text in ('ink-strong', 'ink', 'ink-2-panel', 'brand-ink') for ground in ('surface', 'surface-2')]
THEME_PAIRS += [('ink-strong', 'secondary-soft', AA), ('ink-2', 'secondary-soft', AA), ('mark-ink', 'mark', AA), ('btn-ink', 'btn-bg', AA),
                ('btn-ink', 'brand-strong', AA), ('accent-ink', 'accent', AA), ('stamp-case-ink', 'stamp-case-bg', AA), ('ok-ink', 'ok-bg', AA),
                ('info-ink', 'info-bg', AA), ('art-label', 'bg', AA), ('accent-display', 'bg', LARGE), ('brand', 'bg', LARGE),
                ('border-input', 'bg', LARGE), ('focus', 'bg', LARGE), ('ink', 'bg-pop', AA)]
# Fixed panels look the same in both themes.
FIXED_PAIRS = [('ink-fixed', 'terracotta', AA), ('ink-fixed', 'butter', AA), ('ink-fixed', 'eggshell-raised', AA), ('ink-fixed-2', 'eggshell-raised', AA),
               ('terracotta-link', 'eggshell-raised', AA), ('eggshell', 'slate', AA), ('eggshell-soft', 'slate', AA), ('eggshell-note', 'slate', AA),
               ('butter', 'slate', AA), ('slate-deeper', 'terracotta', AA), ('eggshell', 'slate-deep', AA), ('stone', 'slate-deep', AA), ('lift', 'slate-deep', AA),
               ('stone', 'slate-deeper', AA), ('lift', 'slate-deeper', AA), ('eggshell-soft', 'slate-deeper', AA)]


class PaletteContrastTests(unittest.TestCase):
    def test_theme_pairs_meet_aa_in_light_and_dark(self):
        for name, theme in (('light', LIGHT), ('dark', DARK), ('system dark', SYSTEM_DARK)):
            for text, ground, minimum in THEME_PAIRS:
                with self.subTest(theme=name, text=text, ground=ground):
                    self.assertGreaterEqual(contrast(theme[text], theme[ground]), minimum)

    def test_fixed_panels_meet_aa(self):
        for text, ground, minimum in FIXED_PAIRS:
            with self.subTest(text=text, ground=ground):
                self.assertGreaterEqual(contrast(LIGHT[text], LIGHT[ground]), minimum)

    def test_both_dark_blocks_match(self):
        self.assertEqual(tokens(block(':root[data-site="rea"][data-theme="dark"]')), tokens(block(':root[data-site="rea"]:not([data-theme="light"])')))

    def test_the_footer_wordmark_stays_visible_on_slate(self):
        self.assertGreater(contrast(LIGHT['slate-word'], LIGHT['slate']), 1.15)


if __name__ == '__main__':
    unittest.main()
