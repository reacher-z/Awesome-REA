"""Every requirements disclosure and entry-page requirements heading carries the one bilingual label from build_readme.REQUIREMENTS_LABEL."""
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

    def test_listings_link_to_entry_headings_that_use_the_label(self):
        with TemporaryDirectory() as directory:
            output = Path(directory)
            (output / 'index.html').write_text('<link rel="stylesheet" href="https://awesome-rea.pages.dev/fontawesome.css">')
            (output / 'cases.css').write_bytes((ROOT / 'site/cases.css').read_bytes())
            build_discovery_pages(output, {'resources': self.records, 'meta': {'site_url': 'https://awesomerea.org'}}, None)
            build_entry_pages(output, self.records, [])
            for prefix, label in (('', REQUIREMENTS_LABEL[0]), ('zh/', REQUIREMENTS_LABEL[1])):
                for page, records, fragment in (('resources', self.records, ''), ('cases', self.records[:1], '#entry-requirements')):
                    with self.subTest(page=prefix + page):
                        # Listings no longer disclose requirements. Each row links to the entry page; /cases/ links to its labelled section.
                        html = (output / prefix / page / 'index.html').read_text(encoding='utf-8')
                        self.assertNotIn(escape(label), re.findall(r'<summary>([^<]*)</summary>', html))
                        for record in records:
                            self.assertEqual(html.count(f'href="{"/zh" if prefix else ""}/resources/{record["id"]}/{fragment}"'), 1)
                for record in self.records:
                    with self.subTest(entry=prefix + record['id']):
                        html = (output / prefix / 'resources' / record['id'] / 'index.html').read_text(encoding='utf-8')
                        self.assertIn(f'<h2 id="entry-requirements">{escape(label)}</h2>', html)

    def test_readmes_link_full_entries_without_old_labels(self):
        # README lines link the entry page as "Full entry"; its requirements section carries the label.
        for language, readme, link in (('en', 'README.md', '[Full entry]('), ('zh', 'README.zh-CN.md', '[完整条目](')):
            with self.subTest(language=language):
                self.assertIn(link, render_catalog(self.records, language))
                text = (ROOT / readme).read_text(encoding='utf-8')
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
