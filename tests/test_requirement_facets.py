"""Requirement facets: a fixed vocabulary shared by both languages, rendered with prerequisites first."""
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from build_discovery_pages import build_discovery_pages
from build_entry_pages import build_entry_pages
from catalog import load_resources
from homepage_locales import _ui_strings
from requirement_facets import FACETS, facet_errors, item_html, ordered_items
from test_case_pages import resource
from validate import validate_requirement_facets

APP = (ROOT / 'site/app.js').read_text(encoding='utf-8')
TRANSLATIONS = json.loads((ROOT / 'site/translations.zh-CN.json').read_text(encoding='utf-8'))


def faceted(identifier='facet-case', **changes):
    record = resource(identifier, requirements=['Results are author-reported.', 'Provide your own <source> & ROM.'],
                      requirements_zh=['结果来自作者报告。', '自行提供 <原始> 与 ROM。'], requirement_facets=['testing', 'prerequisites'])
    record.update(changes)
    return record


class RequirementFacetTests(unittest.TestCase):
    def test_vocabulary_and_parity_are_validated(self):
        self.assertEqual(facet_errors(faceted(), faceted()['requirements_zh']), [])
        cases = {
            'unknown facet': ({'requirement_facets': ['testing', 'setup']}, 'unknown facet'),
            'too few facets': ({'requirement_facets': ['testing']}, '1 facets for 2 English'),
            'Chinese items differ': ({'requirements_zh': ['结果来自作者报告。']}, '1 Chinese requirements items for 2 English'),
            'not a list': ({'requirement_facets': 'testing'}, 'nonempty list'),
        }
        for name, (changes, message) in cases.items():
            with self.subTest(case=name):
                record = faceted(**changes)
                errors = facet_errors(record, record['requirements_zh'])
                self.assertTrue(errors and message in errors[0], errors)
        # The field is optional: unlabelled case studies and other records pass and render as plain lists.
        for kind in ('case-study', 'tool'):
            plain = resource('facet-' + kind, kind=kind)
            self.assertEqual(facet_errors(plain, plain['requirements_zh']), [])
            self.assertEqual(ordered_items(plain, plain['requirements']), [(None, item) for item in plain['requirements']])

    def test_validator_reads_chinese_items_from_translations(self):
        record = faceted()
        del record['requirements_zh']
        errors = []
        validate_requirement_facets([record], {record['id']: {'requirements': ['只有一项。']}}, errors)
        self.assertEqual(errors, ["resource 'facet-case'.requirement_facets: 1 Chinese requirements items for 2 English ones, so facets cannot match both languages"])
        errors = []
        validate_requirement_facets([record], {record['id']: {'requirements': ['一。', '二。']}}, errors)
        self.assertEqual(errors, [])

    def test_labelled_records_validate_without_changing_their_text(self):
        labelled = [record for record in load_resources() if 'requirement_facets' in record]
        self.assertTrue(labelled)
        for record in labelled:
            with self.subTest(record=record['id']):
                chinese = record.get('requirements_zh') or TRANSLATIONS[record['id']]['requirements']
                self.assertEqual(facet_errors(record, chinese), [])
                english = record['requirements'] if isinstance(record['requirements'], list) else [record['requirements']]
                self.assertEqual(sorted(text for _, text in ordered_items(record, english)), sorted(english))

    def test_prerequisites_lead_and_other_items_keep_their_order(self):
        record = faceted(requirements=['a', 'b', 'c', 'd'], requirement_facets=['scope', 'prerequisites', 'limits', 'prerequisites'])
        self.assertEqual(ordered_items(record, record['requirements']),
                         [('prerequisites', 'b'), ('prerequisites', 'd'), ('scope', 'a'), ('limits', 'c')])
        self.assertEqual(ordered_items({}, ['x']), [(None, 'x')])
        self.assertEqual(item_html('license', 'MIT & <more>', 'en'), '<li><strong class="requirement-facet">License: </strong>MIT &amp; &lt;more&gt;</li>')
        self.assertEqual(item_html('license', 'MIT', 'zh'), '<li><strong class="requirement-facet">许可：</strong>MIT</li>')
        self.assertEqual(item_html(None, 'x', 'en'), '<li>x</li>')

    def test_entry_and_case_pages_show_facets_first(self):
        record = faceted()
        with TemporaryDirectory() as directory:
            output = Path(directory)
            (output / 'index.html').write_text('<link rel="stylesheet" href="https://awesome-rea.pages.dev/fontawesome.css">')
            (output / 'cases.css').write_bytes((ROOT / 'site/cases.css').read_bytes())
            build_discovery_pages(output, {'resources': [record], 'meta': {'site_url': 'https://awesomerea.org'}}, None)
            build_entry_pages(output, [record], [])
            for prefix, labels, texts in (('', ('Prerequisites: ', 'Testing evidence: '), record['requirements']),
                                          ('zh/', ('前提条件：', '测试证据：'), record['requirements_zh'])):
                expected = [f'<li><strong class="requirement-facet">{labels[0]}</strong>{texts[1].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}</li>',
                            f'<li><strong class="requirement-facet">{labels[1]}</strong>{texts[0]}</li>']
                for page in ('resources', 'cases', f'resources/{record["id"]}'):
                    with self.subTest(page=prefix + page):
                        html = (output / prefix / page / 'index.html').read_text(encoding='utf-8')
                        self.assertIn(''.join(expected), html)

    def test_homepage_labels_match_the_vocabulary(self):
        strings = _ui_strings(APP)
        for facet, (english, chinese) in FACETS.items():
            key = 'facet' + facet[0].upper() + facet[1:]
            self.assertEqual((strings['en'][key], strings['zh'][key]), (english, chinese))
        self.assertEqual(len([key for key in strings['en'] if re.fullmatch(r'facet[A-Z]\w*', key)]), len(FACETS))


if __name__ == '__main__':
    unittest.main()
