"""Collection pages give an entry's title, full-entry and evidence links the same destinations and labels."""
from html.parser import HTMLParser
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from build_discovery_pages import PRIMARY_SOURCE_LABEL, build_discovery_pages
from build_entry_pages import build_entry_pages
from homepage_locales import _ui_strings
from test_case_pages import resource

APP = (ROOT / 'site/app.js').read_text(encoding='utf-8')


class Links(HTMLParser):
    """Links per record: (href, visible text, inside the h3 title)."""
    def __init__(self):
        super().__init__()
        self.records, self.current, self.depth, self.h3, self.link = {}, None, 0, False, None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'article':
            self.depth += 1
            if 'data-resource-id' in attrs:
                self.current, self.depth = attrs['data-resource-id'], 1
                self.records[self.current] = []
        elif tag == 'h3':
            self.h3 = True
        elif tag == 'a' and self.current:
            self.link = [attrs.get('href'), '', self.h3]

    def handle_endtag(self, tag):
        if tag == 'article' and self.current:
            self.depth -= 1
            if not self.depth:
                self.current = None
        elif tag == 'h3':
            self.h3 = False
        elif tag == 'a' and self.link:
            self.link[1] = ' '.join(self.link[1].split())
            self.records[self.current].append(tuple(self.link))
            self.link = None

    def handle_data(self, data):
        if self.link:
            self.link[1] += data


class EntryLinkTargetTests(unittest.TestCase):
    def test_titles_entries_and_primary_sources_match_on_every_collection_page(self):
        records = [resource('link-case'), resource('link-tool', kind='tool')]
        with TemporaryDirectory() as directory:
            output = Path(directory)
            (output / 'index.html').write_text('<link rel="stylesheet" href="https://awesome-rea.pages.dev/fontawesome.css">')
            (output / 'cases.css').write_bytes((ROOT / 'site/cases.css').read_bytes())
            build_discovery_pages(output, {'resources': records, 'meta': {'site_url': 'https://awesomerea.org'}}, None)
            build_entry_pages(output, records, [])
            for prefix, zh in (('', False), ('zh/', True)):
                source = PRIMARY_SOURCE_LABEL[zh]
                for page, expected in (('resources', records), ('cases', records[:1])):
                    parser = Links()
                    parser.feed((output / prefix / page / 'index.html').read_text(encoding='utf-8'))
                    self.assertEqual(set(parser.records), {record['id'] for record in expected})
                    for record in expected:
                        with self.subTest(page=prefix + page, record=record['id']):
                            links = parser.records[record['id']]
                            self.assertEqual([href for href, _, title in links if title], [record['url']])
                            self.assertEqual([text for href, text, _ in links if href == record['url']],
                                             [(record['name_zh'] if zh else record['name']) + '↗'])
                            self.assertEqual([text for href, text, _ in links if href == record['evidence_url']], [source + ' ↗'])
                            self.assertEqual([text for href, text, _ in links if href == f"/{prefix}resources/{record['id']}/"],
                                             ['完整条目' if zh else 'Full entry'])
                            # Additional sources and requirements are on the entry page, linked from its requirements section.
                            self.assertLessEqual({record['url'], record['evidence_url'], f"/{prefix}resources/{record['id']}/#entry-requirements"},
                                                 {href for href, _, _ in links})
                for record in records:
                    html = (output / prefix / 'resources' / record['id'] / 'index.html').read_text(encoding='utf-8')
                    self.assertIn(f'href="{record["evidence_url"]}"', html)
                    self.assertIn(f'>{source} <span', html)

    def test_homepage_evidence_link_uses_the_same_label(self):
        strings = _ui_strings(APP)
        self.assertEqual((strings['en']['readSource'], strings['zh']['readSource']), PRIMARY_SOURCE_LABEL)


if __name__ == '__main__':
    unittest.main()
