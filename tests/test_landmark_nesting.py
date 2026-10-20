"""Complementary landmarks stay top level: the homepage shelf and the survey findings are not nested asides."""
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_survey import build_survey

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
LANDMARKS = {'main', 'nav', 'aside', 'article'}


class Landmarks(HTMLParser):
    """Record each element's landmark ancestors, its labelling heading id and every id on the page."""

    def __init__(self, text):
        super().__init__()
        self.stack, self.ids, self.nested_asides, self.elements = [], set(), [], []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get('id'):
            self.ids.add(values['id'])
        ancestors = [name for name, _ in self.stack if name in LANDMARKS]
        if tag == 'aside' and ancestors:
            self.nested_asides.append((values.get('class'), ancestors))
        self.elements.append({'tag': tag, 'class': values.get('class', ''), 'labelledby': values.get('aria-labelledby')})
        if tag not in VOID:
            self.stack.append((tag, values))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def element(self, class_name):
        return next(item for item in self.elements if class_name in item['class'].split())


def built_survey():
    resources = (json.loads((ROOT / 'data/rea-resources.json').read_text(encoding='utf-8'))
                 + json.loads((ROOT / 'data/tool-resources.json').read_text(encoding='utf-8')))
    localizations = json.loads((ROOT / 'site/translations.zh-CN.json').read_text(encoding='utf-8'))
    for record in resources:
        record.setdefault('name_zh', localizations.get(record['id'], {}).get('name', record['name']))
        record.setdefault('requirements_zh', localizations.get(record['id'], {}).get('requirements', record['requirements']))
    papers = json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))
    document = json.loads((ROOT / 'data/survey.json').read_text(encoding='utf-8'))
    with TemporaryDirectory() as directory:
        build_survey(Path(directory), papers, resources, document=document)
        return {route: (Path(directory) / route / 'index.html').read_text(encoding='utf-8') for route in ('survey', 'zh/survey')}


class LandmarkNestingTests(unittest.TestCase):
    def test_homepage_shelf_is_a_labelled_navigation_not_a_nested_aside(self):
        page = Landmarks((ROOT / 'site/index.html').read_text(encoding='utf-8'))
        self.assertEqual(page.nested_asides, [])
        shelf = page.element('collection-shelf')
        self.assertEqual(shelf['tag'], 'nav')
        self.assertEqual(shelf['labelledby'], 'shelf-title')
        self.assertIn('shelf-title', page.ids)

    def test_survey_findings_are_a_labelled_section_of_the_article(self):
        for route, html in built_survey().items():
            page = Landmarks(html)
            with self.subTest(route=route):
                self.assertEqual(page.nested_asides, [])
                findings = page.element('survey-findings')
                self.assertEqual(findings['tag'], 'section')
                self.assertIn(findings['labelledby'], page.ids)
                self.assertIn('<h2 id="survey-findings-title">' + ('主要认识' if route.startswith('zh') else 'Main findings') + '</h2>', html)


if __name__ == '__main__':
    unittest.main()
