"""Resource detail pages link other entries of their README section, deterministically."""
from copy import deepcopy
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_entry_pages import build_entry_pages, entry_path, section_siblings

TEMPLATE = json.loads((ROOT / 'data/tool-resources.json').read_text(encoding='utf-8'))[0]


def resource(identifier, *, category='firmware', kind='tool', relationship='foundation', **changes):
    record = deepcopy(TEMPLATE)
    record.update(id=identifier, name=f'Tool {identifier}', name_zh=f'工具 {identifier}', url=f'https://example.org/{identifier}',
                  category=category, kind=kind, relationship=relationship, targets=['firmware'],
                  requirements=['Original input is required.'], requirements_zh=['需要原始输入。'], **changes)
    record.pop('additional_evidence_urls', None)
    return record


def case(identifier):
    return resource(identifier, category='reconstruction-cases', kind='case-study', relationship='independent-reconstruction')


class SectionLinks(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.heading, self._inside, self._h2 = None, '', False, False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'section' and 'entry-siblings' in values.get('class', '').split():
            self.links, self._inside = [], True
        elif self._inside and tag == 'a':
            self.links.append(values['href'])
        self._h2 = self._inside and tag == 'h2'

    def handle_data(self, data):
        if self._h2:
            self.heading += data

    def handle_endtag(self, tag):
        if tag == 'section':
            self._inside = False
        if tag == 'h2':
            self._h2 = False


class SectionSiblingTests(unittest.TestCase):
    def test_selection_follows_readme_order_wraps_and_stops_at_six(self):
        records = [resource(f'tool-{index}') for index in range(8)] + [case('case-a'), resource('lone', category='protocol-analysis')]
        related = section_siblings(records)
        # Case studies lead the section, as in the READMEs; the rest keep catalog order.
        self.assertEqual([r['id'] for r in related['case-a']['siblings']], [f'tool-{index}' for index in range(6)])
        self.assertEqual([r['id'] for r in related['tool-5']['siblings']], ['tool-6', 'tool-7', 'case-a', 'tool-0', 'tool-1', 'tool-2'])
        self.assertEqual((related['tool-0']['section'], related['tool-0']['count'], related['tool-0']['cases']), ('firmware', 9, 1))
        self.assertEqual(related['lone']['siblings'], [])
        self.assertEqual(section_siblings(list(records)), related)
        small = section_siblings([resource('a'), resource('b')])
        self.assertEqual([r['id'] for r in small['b']['siblings']], ['a'])

    def test_pages_link_localized_siblings_and_section_anchors(self):
        records = [case('case-a'), resource('tool-a'), resource('tool-b'), resource('lone', category='protocol-analysis')]
        paper = next(p for p in json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8')) if p['id'] == 'paper-fuzzware')
        outputs = []
        for _ in range(2):
            with TemporaryDirectory() as directory:
                root = Path(directory)
                build_entry_pages(root, records, [paper])
                read = lambda kind, identifier, language: (root / entry_path(kind, identifier, language).lstrip('/') / 'index.html').read_text(encoding='utf-8')
                outputs.append(read('resource', 'tool-a', 'en'))
                english, chinese = SectionLinks(read('resource', 'tool-a', 'en')), SectionLinks(read('resource', 'case-a', 'zh'))
                self.assertEqual(english.heading, 'More in Firmware and hardware')
                self.assertEqual(english.links, ['/resources/tool-b/', '/resources/case-a/', '/resources/#heading-firmware'])
                self.assertEqual(chinese.heading, '同分区更多条目：固件与硬件')
                self.assertEqual(chinese.links, ['/zh/resources/tool-a/', '/zh/resources/tool-b/', '/zh/resources/#heading-firmware', '/zh/cases/#cases-firmware'])
                self.assertIn('工具 tool-a</a>', read('resource', 'case-a', 'zh'))
                self.assertIsNone(SectionLinks(read('resource', 'lone', 'en')).links)
                self.assertIsNone(SectionLinks(read('paper', paper['id'], 'en')).links)
        self.assertEqual(outputs[0], outputs[1])


if __name__ == '__main__':
    unittest.main()
