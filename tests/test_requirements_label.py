"""Every requirements disclosure carries the one bilingual label from build_readme.REQUIREMENTS_LABEL."""
from html import escape
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
from build_readme import REQUIREMENTS_LABEL, render_catalog
from test_case_pages import resource
from validate_site import validate_requirements_label

APP = (ROOT / 'site/app.js').read_text(encoding='utf-8')
OLD_LABELS = ('Requirements & evidence', 'Requirements and evidence', 'Details & requirements', 'Details and requirements',
              'Details & limits', 'Requirements and limitations', '使用条件与证据', '详情与使用条件', '详情与局限')


class RequirementsLabelTests(unittest.TestCase):
    def setUp(self):
        self.records = [resource('label-case'), resource('label-tool', kind='tool')]

    def test_listing_disclosures_and_entry_headings_use_the_label(self):
        with TemporaryDirectory() as directory:
            output = Path(directory)
            (output / 'index.html').write_text('<link rel="stylesheet" href="https://awesome-rea.pages.dev/fontawesome.css">')
            (output / 'cases.css').write_bytes((ROOT / 'site/cases.css').read_bytes())
            build_discovery_pages(output, {'resources': self.records, 'meta': {'site_url': 'https://awesomerea.org'}}, None)
            build_entry_pages(output, self.records, [])
            for prefix, label in (('', REQUIREMENTS_LABEL[0]), ('zh/', REQUIREMENTS_LABEL[1])):
                for page, count in (('resources', 2), ('cases', 1)):
                    with self.subTest(page=prefix + page):
                        html = (output / prefix / page / 'index.html').read_text(encoding='utf-8')
                        self.assertEqual(re.findall(r'<summary>([^<]*)</summary>', html)[-count:], [escape(label)] * count)
                for record in self.records:
                    with self.subTest(entry=prefix + record['id']):
                        html = (output / prefix / 'resources' / record['id'] / 'index.html').read_text(encoding='utf-8')
                        self.assertIn(f'<h2 id="entry-requirements">{escape(label)}</h2>', html)

    def test_readme_links_and_intro_use_the_label(self):
        for language, readme, label in (('en', 'README.md', REQUIREMENTS_LABEL[0]), ('zh', 'README.zh-CN.md', REQUIREMENTS_LABEL[1])):
            with self.subTest(language=language):
                self.assertIn(f'[{label}](', render_catalog(self.records, language))
                text = (ROOT / readme).read_text(encoding='utf-8')
                self.assertIn(f'“{label}”', text)
                self.assertFalse([old for old in OLD_LABELS if old in text])

    def test_homepage_strings_must_match(self):
        validate_requirements_label(APP)
        self.assertFalse([old for old in OLD_LABELS if f'"{old}"' in APP])
        for old, new in (('"requirements": "Requirements & limits"', '"requirements": "Details & requirements"'),
                         ('"requirementsShort": "使用条件与局限"', '"requirementsShort": "详情与局限"')):
            with self.subTest(change=new), self.assertRaises(AssertionError):
                validate_requirements_label(APP.replace(old, new))


if __name__ == '__main__':
    unittest.main()
