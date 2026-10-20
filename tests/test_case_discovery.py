"""Case-directory coverage must match source-backed records and retain their evidence."""
from copy import deepcopy
from html import escape
import json
import re
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_discovery_pages import build_discovery_pages
from validate_site import Page, validate_case_outputs


def record(identifier, targets, kind='case-study'):
    return {'id': identifier, 'name': 'Example ' + identifier, 'name_zh': '案例 ' + identifier,
            'url': 'https://example.org/' + identifier, 'category': 'reconstruction-cases',
            'kind': kind, 'relationship': 'independent-reconstruction', 'targets': targets,
            'description_en': 'Reconstructs one observed behavior; complete equivalence is untested.',
            'description_zh': '重建一个观测行为；完整等价尚未测试。',
            'requirements': ['Requires the original input; no runtime was executed.'],
            'requirements_zh': ['需要原始输入；没有执行上游程序。'],
            'evidence_url': 'https://example.org/evidence/' + identifier,
            'additional_evidence_urls': ['https://example.org/limits/' + identifier],
            'verified_at': '2026-10-16T12:30:00Z', 'verification': 'source-reviewed'}


class CaseDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.resources = [record('web-case', ['website', 'app']),
                          record('hardware-case', ['firmware']),
                          record('other-tool', ['binary'], 'tool')]
        with TemporaryDirectory() as directory:
            output = Path(directory)
            build_discovery_pages(output, {'meta': {}, 'resources': self.resources}, None)
            self.html = {prefix + '/cases/': (output / (prefix.lstrip('/') + '/cases/').lstrip('/') / 'index.html').read_text()
                         for prefix in ('', '/zh')}

    def validate(self, html=None):
        validate_case_outputs({route: Page(text) for route, text in (html or self.html).items()}, self.resources)

    def test_exact_bilingual_subset_full_evidence_and_source_order(self):
        before = deepcopy(self.resources)
        self.validate()
        for route, text in self.html.items():
            page = Page(text)
            self.assertEqual([row['id'] for row in page.case_rows], ['web-case', 'hardware-case'])
            self.assertNotIn('other-tool', [row['id'] for row in page.case_rows])
            if route == '/cases/':
                self.assertIn('<p>1 case</p>', text)
                self.assertNotIn('<p>1 cases</p>', text)
        self.assertEqual(self.resources, before)

    def test_missing_duplicate_unknown_or_misplaced_case_is_rejected(self):
        route = '/cases/'
        for before, after in [('data-case-id="web-case"', 'data-case-id="other-tool"'),
                              ('data-case-id="hardware-case"', 'data-case-id="web-case"'),
                              ('data-case-section="website"', 'data-case-section="game"')]:
            with self.subTest(before=before, after=after):
                broken = dict(self.html); self.assertIn(before, broken[route])
                broken[route] = broken[route].replace(before, after, 1)
                with self.assertRaises(AssertionError): self.validate(broken)
        missing = dict(self.html); missing.pop('/zh/cases/')
        with self.assertRaises(AssertionError): self.validate(missing)

    def test_script_text_or_other_language_cannot_replace_visible_case_content(self):
        route = '/zh/cases/'
        for field in ('description_zh',):
            value = self.resources[0][field]
            value = value[0] if isinstance(value, list) else value
            broken = dict(self.html)
            self.assertIn(escape(value), broken[route])
            match = re.search(r'(<article\b[^>]*data-case-id="web-case"[^>]*>)(.*?)(</article>)', broken[route], re.S)
            self.assertIsNotNone(match)
            body = match[2].replace(escape(value), '<script>' + value + '</script>', 1)
            broken[route] = broken[route][:match.start(2)] + body + broken[route][match.end(2):]
            with self.assertRaises(AssertionError): self.validate(broken)

    def test_primary_additional_detail_links_and_date_are_required(self):
        route = '/zh/cases/'
        for old in (self.resources[0]['evidence_url'], '/zh/resources/web-case/#entry-requirements',
                    '/zh/resources/web-case/'):
            with self.subTest(url=old):
                broken = dict(self.html)
                broken[route] = broken[route].replace('href="' + old + '"', 'href="https://example.org/wrong"')
                with self.assertRaises(AssertionError): self.validate(broken)
        broken = dict(self.html)
        broken[route] = broken[route].replace('datetime="2026-10-16T12:30:00Z"', 'datetime="2026-10-15"', 1)
        with self.assertRaises(AssertionError): self.validate(broken)

    def test_structured_cases_cannot_point_to_wrong_locale_or_extra_record(self):
        route = '/zh/cases/'
        for before, after in [('"url":"https://awesomerea.org/zh/resources/web-case/"',
                               '"url":"https://awesomerea.org/resources/web-case/"'),
                              ('"numberOfItems":2', '"numberOfItems":3')]:
            broken = dict(self.html); self.assertIn(before, broken[route])
            broken[route] = broken[route].replace(before, after, 1)
            with self.assertRaises(AssertionError): self.validate(broken)


if __name__ == '__main__':
    unittest.main()
