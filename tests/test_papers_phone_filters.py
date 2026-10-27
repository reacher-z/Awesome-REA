"""On phones the /papers/ search form packs into three rows and research areas scroll in one row."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_paper_pages import build_paper_pages

CSS = (ROOT / 'site/papers.css').read_text(encoding='utf-8')


def media_block(query):
    """The body of one top-level @media block (blocks here do not nest)."""
    start = CSS.index('@media(' + query + '){') + len('@media(' + query + '){')
    depth, index = 1, start
    while depth:
        depth += {'{': 1, '}': -1}.get(CSS[index], 0)
        index += 1
    return CSS[start:index - 1]


def declarations(block, selector):
    rules = re.findall(r'([^{}]+)\{([^{}]*)\}', block)
    matches = [body for selectors, body in rules if selector in [item.strip() for item in selectors.split(',')]]
    return dict(item.split(':', 1) for body in matches for item in body.split(';') if item.strip())


class FormChildren(HTMLParser):
    def __init__(self):
        super().__init__()
        self.children, self.depth = [], 0

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if attributes.get('id') == 'paper-search':
            self.depth = 1
            return
        if self.depth:
            if self.depth == 1:
                self.children.append((tag, attributes.get('id'), attributes.get('class')))
            if tag not in {'input', 'br', 'img'}:
                self.depth += 1

    def handle_endtag(self, tag):
        if self.depth and tag not in {'input', 'br', 'img'}:
            self.depth -= 1


class PhonePaperFilterTests(unittest.TestCase):
    def test_phone_grid_places_each_form_child(self):
        phone = media_block('max-width:600px')
        self.assertEqual(declarations(phone, '.paper-search')['grid-template-columns'], 'minmax(0,1fr) auto')
        for selector, placement in (
            ('.paper-search-query', {'grid-column': '1/-1'}),
            ('.paper-search>.paper-search-field:nth-child(2)', {'grid-column': '1', 'grid-row': '2'}),
            ('.paper-search-more', {'grid-column': '2', 'grid-row': '2'}),
            ('.paper-search-more[open]', {'grid-column': '1/-1', 'grid-row': '3'}),
            ('.paper-search-results', {'grid-column': '1', 'grid-row': '4'}),
            ('.paper-search .button', {'grid-column': '2', 'grid-row': '4'}),
        ):
            with self.subTest(selector=selector):
                rules = declarations(phone, selector)
                for key, value in placement.items():
                    self.assertEqual(rules.get(key), value)
        # The closed panel's row has no height, so spacing comes from margins rather than a row gap.
        self.assertEqual(declarations(phone, '.paper-search')['row-gap'], '0')
        self.assertEqual(declarations(phone, '.paper-search>:not(.paper-search-query)')['margin-top'], '10px')
        topics = declarations(phone, '.papers-topic-nav')
        self.assertEqual((topics['flex-wrap'], topics['overflow-x']), ('nowrap', 'auto'))
        self.assertNotIn('display:none', phone.replace(' ', ''), 'every control and label stays visible')

    def test_controls_keep_their_touch_height(self):
        for selector in ('.paper-search-field input', '.paper-search .button', '.paper-search-more>summary', '.papers-topic-nav a'):
            heights = [body for selectors, body in re.findall(r'([^{}]+)\{([^{}]*)\}', CSS)
                       if selector in [item.strip() for item in selectors.split(',')] and 'min-height:44px' in body]
            self.assertTrue(heights, selector)

    def test_form_children_keep_the_order_the_phone_grid_expects(self):
        papers = json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build_paper_pages(output, papers)
            for path in ('papers/index.html', 'zh/papers/index.html'):
                parser = FormChildren()
                parser.feed((output / path).read_text(encoding='utf-8'))
                self.assertEqual([(tag, identifier) for tag, identifier, _ in parser.children], [
                    ('div', None), ('div', None), ('details', 'paper-more-filters'), ('button', 'paper-clear'), ('p', 'paper-results')])
                self.assertEqual([classes for _, _, classes in parser.children][:2],
                                 ['paper-search-field paper-search-query', 'paper-search-field'])


if __name__ == '__main__':
    unittest.main()
