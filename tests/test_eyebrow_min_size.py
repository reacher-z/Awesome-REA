"""Eyebrow labels and homepage count badges keep a 12px floor at every width, in both languages."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
LABELS = re.compile(r'\.eyebrow\b|\.index-mode>\.mono\b|\.more-filters-count\b')
FONT_SIZE = re.compile(r'(?:^|;)\s*font-size:\s*([\d.]+)px')
FONT_SHORTHAND = re.compile(r'(?:^|;)\s*font:\s*(?:[a-z\d]+\s+)*?([\d.]+)px')


def label_rules():
    """Yield (file, selector, declarations) for every rule, including those inside media queries, that styles a label."""
    for path in sorted((ROOT / 'site').glob('*.css')):
        text = re.sub(r'/\*.*?\*/', '', path.read_text(encoding='utf-8'), flags=re.S)
        for selector, body in re.findall(r'([^{}]+)\{([^{}]*)\}', text):
            selectors = [part.strip() for part in selector.split(',')]
            if any(LABELS.search(part) for part in selectors):
                yield path.name, selector.strip(), body


class EyebrowMinimumSizeTests(unittest.TestCase):
    def test_no_label_rule_sets_a_size_below_12px(self):
        sizes = []
        for name, selector, body in label_rules():
            for pattern in (FONT_SIZE, FONT_SHORTHAND):
                for value in pattern.findall(body):
                    sizes.append((name, selector, float(value)))
        self.assertTrue(sizes)
        self.assertEqual([item for item in sizes if item[2] < 12], [])

    def test_base_eyebrow_and_count_badges_are_12px(self):
        styles = (ROOT / 'site/styles.css').read_text(encoding='utf-8')
        self.assertRegex(styles, r'\n\.eyebrow\{[^}]*font:650 12px/1\.5 var\(--sans\)')
        self.assertRegex(styles, r'\.index-mode>\.mono\{[^}]*font:500 12px/')
        self.assertRegex(styles, r'\.more-filters-count\{[^}]*font-size:12px')

    def test_chinese_eyebrows_drop_letter_spacing(self):
        styles = (ROOT / 'site/styles.css').read_text(encoding='utf-8')
        self.assertIn('html[lang="zh-CN"] .eyebrow{letter-spacing:0}', styles)
        # The Chinese rule must outrank every scoped eyebrow rule that sets tracking.
        for name, selector, body in label_rules():
            if 'letter-spacing' in body and '.eyebrow' in selector and 'zh-CN' not in selector:
                for part in selector.split(','):
                    self.assertLessEqual(part.count('.'), 2, part)
                    self.assertNotIn('#', part)


if __name__ == '__main__':
    unittest.main()
