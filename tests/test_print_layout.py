"""Static pages print as plain documents with an explicit disclosure policy, and the print rules leave screens alone."""
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_site

CSS = (ROOT / 'site/styles.css').read_text(encoding='utf-8')


def print_block(css):
    """Return the body of the single top-level @media print block, checking that its braces close."""
    start = css.index('@media print{') + len('@media print{')
    depth, index = 1, start
    while depth:
        depth += {'{': 1, '}': -1}.get(css[index], 0)
        index += 1
    return css[start:index - 1]


class PrintLayoutTests(unittest.TestCase):
    def test_stylesheet_braces_balance_so_screen_rules_survive(self):
        # A stray brace after the print block once dropped the following screen rule; strings hold no braces here.
        without_comments = re.sub(r'/\*.*?\*/', '', CSS, flags=re.S)
        self.assertEqual(without_comments.count('{'), without_comments.count('}'))
        self.assertEqual(CSS.count('@media print{'), 1)
        block = print_block(CSS)
        after = CSS[CSS.index(block) + len(block) + 1:]
        self.assertFalse(after.lstrip().startswith('}'), 'a stray closing brace follows the print block')

    def test_policy_rules(self):
        block = print_block(CSS)
        for rule in ('.site-header{position:static!important',
                     '.skip-link,.header-nav,.site-footer .footer-links,.browse-actions,.papers-actions,.paper-search,',
                     'details:not([open]):not(.browse-provenance,.cases-note,.paper-details){display:none!important}',
                     ':is(.browse-provenance,.cases-note,.paper-details:not([open]))::details-content{content-visibility:visible!important;display:block!important}',
                     '.paper-details:not([open])>:not(.paper-scope){display:none!important}',
                     'main :is(a,dd,code){overflow-wrap:anywhere!important}', '[href^="http"]::after{content:" <" attr(href) ">"',
                     ':is(.card-heading,.source-card-head,.paper-card>header,.case-heading,.source-card,li,dt,dd){break-inside:avoid}'):
            with self.subTest(rule=rule):
                self.assertIn(rule, block)
        # Both languages state the policy on the listings whose entries have disclosures.
        notes = re.findall(r'content:"(打印说明|Printed listing)[^"]*"', block)
        self.assertEqual(sorted(notes), ['Printed listing', 'Printed listing', '打印说明', '打印说明'])

    def test_print_selectors_match_the_built_pages(self):
        block = print_block(CSS)
        classes = set(re.findall(r'\.([a-z][a-z0-9-]*)', re.sub(r'content:"[^"]*"', '', block)))
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'dist'
            build_site.build_site(output)
            pages = {route: (output / route / 'index.html').read_text(encoding='utf-8') for route in (
                '', 'resources', 'cases', 'about', 'browse', 'browse/android', 'papers', 'resources/ghidra', 'papers/paper-dire',
                'zh/resources', 'zh/papers')}
        used = set()
        for html in pages.values():
            for attribute in re.findall(r'class="([^"]*)"', html):
                used.update(attribute.split())
        self.assertEqual(sorted(classes - used), [], 'print rules name classes that no static page uses')
        # The content the policy keeps is where the rules expect it.
        self.assertIn('<details class="paper-details"><summary>', pages['papers'])
        self.assertIn('<div class="paper-scope"><h4>Scope & limitations</h4>', pages['papers'])
        self.assertIn('<div class="paper-scope"><h4>研究范围与局限</h4>', pages['zh/papers'])
        for route in ('resources', 'cases', 'browse/android'):
            self.assertRegex(pages[route], r'<details class="(browse-provenance|cases-note)"><summary>')
        self.assertIn('<details class="requirements"><summary>', pages['resources'])
        # Detail pages have no disclosures, so they print every requirement and source.
        for route in ('resources/ghidra', 'papers/paper-dire'):
            self.assertNotIn('<details', pages[route].split('<main', 1)[1])


if __name__ == '__main__':
    unittest.main()
