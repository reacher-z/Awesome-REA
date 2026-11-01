"""Entry and paper fact lists keep their label and value columns on phones instead of stacking them."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


def media_rules(css, query):
    """Return {selector: declarations} for the rules inside one @media block."""
    start = css.index('@media(' + query + '){') + len('@media(' + query + '){')
    depth, end = 1, start
    while depth:
        depth += {'{': 1, '}': -1}.get(css[end], 0)
        end += 1
    return {selector.strip(): body for selector, body in re.findall(r'([^{}]+)\{([^}]*)\}', css[start:end - 1])}


class FactListPhoneTests(unittest.TestCase):
    def test_phone_fact_lists_use_a_narrow_label_column_and_no_stacking_margin(self):
        rules = media_rules((ROOT / 'site/entry.css').read_text(), 'max-width:520px')
        columns = re.search(r'grid-template-columns:([^;]+)', rules['.entry-facts'])[1]
        # Two tracks: a label column with a readable minimum and a shrinkable value column.
        self.assertEqual(columns, 'minmax(7.5em,34%) minmax(0,1fr)')
        self.assertNotIn('.entry-facts dd+dt', rules)

    def test_values_still_wrap_inside_their_column(self):
        css = (ROOT / 'site/entry.css').read_text()
        self.assertIn('.entry-facts dd{margin:0;color:var(--body);overflow-wrap:anywhere}', css)


if __name__ == '__main__':
    unittest.main()
