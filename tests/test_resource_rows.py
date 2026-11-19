"""/resources/: one index-card row per record, filters and sections drawn from the data, nothing that needs a script to read."""
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from collections import Counter

from build_discovery_pages import SECTIONS, build_discovery_pages
from build_home import search_index, search_row_id
from build_readme import CATEGORIES, KIND_LABELS, collection_section
from resource_listing import in_section_order


def record(identifier, kind='tool', category='native-analysis', relationship='foundation', targets=('binary',)):
    return {'id': identifier, 'name': 'Example ' + identifier, 'name_zh': '示例 ' + identifier, 'url': 'https://example.org/' + identifier,
            'category': category, 'kind': kind, 'relationship': relationship, 'targets': list(targets),
            'description_en': 'Does one thing. Then another.', 'description_zh': '做一件事。',
            'requirements': ['One requirement.'], 'requirements_zh': ['一项要求。'], 'evidence_url': 'https://example.org/evidence/' + identifier,
            'verified_at': '2026-10-16T12:30:00Z', 'verification': 'source-reviewed'}


RECORDS = [record('websitebench', 'project', 'web-analysis', 'learning', ('website',)),
           record('web-tool', 'tool', 'web-analysis', targets=('website',)),
           record('case-a', 'case-study', 'reconstruction-cases', 'independent-reconstruction', ('game',)),
           record('tool-a', 'tool', 'game-analysis', targets=('game',)),
           record('ghidra'),
           record('tool-b')]


class ResourceRowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with TemporaryDirectory() as directory:
            output = Path(directory)
            build_discovery_pages(output, {'meta': {}, 'resources': RECORDS}, None)
            cls.pages = {language: (output / route / 'index.html').read_text(encoding='utf-8') for language, route in (('en', 'resources'), ('zh', 'zh/resources'))}

    def test_every_record_is_one_row_with_its_legacy_anchor(self):
        for language, html in self.pages.items():
            with self.subTest(language=language):
                self.assertEqual(sorted(re.findall(r'data-record-id="([^"]+)"', html)), sorted(row['id'] for row in RECORDS))
                for row in RECORDS:
                    self.assertEqual(html.count(f' id="{row["id"]}"'), 1)
                    self.assertIn(f'href="{row["evidence_url"]}"', html)

    def test_sections_come_from_the_records(self):
        sections = {collection_section(row) for row in RECORDS}
        for language, html in self.pages.items():
            with self.subTest(language=language):
                self.assertEqual(set(re.findall(r'<a href="#heading-([a-z-]+)" data-section-link data-section="\1">', html)), sections)
                self.assertEqual(set(re.findall(r'<h2 id="heading-([a-z-]+)">', html)), sections)
                self.assertLess(set(SECTIONS) & sections, set(SECTIONS))

    def test_filters_list_only_values_the_records_use(self):
        html = self.pages['en']
        self.assertEqual(set(re.findall(r'name="kind" value="([^"]+)"', html)), {row['kind'] for row in RECORDS})
        self.assertEqual(set(re.findall(r'name="category" value="([^"]+)"', html)), {row['category'] for row in RECORDS})
        self.assertIn(f'<span class="opt-l">{CATEGORIES["native-analysis"][0]}</span><span class="opt-n">2</span>', html)
        self.assertIn(f'<span class="opt-l">{KIND_LABELS["case-study"][0]}</span><span class="opt-n">1</span>', html)
        self.assertIn(f'<span class="opt-l">{KIND_LABELS["case-study"][1]}</span>', self.pages['zh'])

    def test_rows_put_pinned_and_featured_records_and_tools_before_case_studies(self):
        by_id = {row['id']: row for row in RECORDS}
        order = in_section_order([by_id['case-a'], by_id['tool-b'], by_id['ghidra'], by_id['websitebench']])
        self.assertEqual([row['id'] for row in order], ['websitebench', 'ghidra', 'tool-b', 'case-a'])

    def test_a_pinned_record_opens_its_section_marked_featured(self):
        for language, label in (('en', 'Featured'), ('zh', '精选')):
            html = self.pages[language]
            self.assertEqual(re.findall(r'data-record-id="([^"]+)"', html)[0], 'websitebench')
            self.assertEqual(re.findall(r'class="row-mark">([^<]+)<', html), [label])

    def test_every_section_is_a_link_with_its_count_and_key(self):
        html = self.pages['en']
        groups = Counter(collection_section(row) for row in RECORDS)
        for key, number in groups.items():
            self.assertRegex(html, rf'<a href="#heading-{key}" data-section-link data-section="{key}">[^<]+<span class="count">{number}</span>')

    def test_search_index_carries_each_records_section_and_the_pinned_ids(self):
        catalogued = [dict(row, name_zh=row['name_zh']) for row in RECORDS]
        index = search_index(catalogued, [], 'en', {'website': [], 'game': [], 'app': [], 'binary': [], 'firmware': [], 'protocol': []})
        self.assertEqual(index['pinned'], ['websitebench'])
        self.assertEqual({search_row_id(row): index['sections'][row[11]] for row in index['r']}, {row['id']: collection_section(row) for row in RECORDS})

    def test_structured_list_follows_the_rows_without_repeating_descriptions(self):
        for language, html in self.pages.items():
            schema = next(json.loads(block) for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S) if '"CollectionPage"' in block)
            items = schema['mainEntity']['itemListElement']
            prefix = '/zh' if language == 'zh' else ''
            self.assertEqual([item['url'].removeprefix('https://awesomerea.org') for item in items], [f'{prefix}/resources/{identifier}/' for identifier in re.findall(r'data-record-id="([^"]+)"', html)])
            self.assertTrue(all('description' not in item for item in items))

    def test_one_link_to_the_suggestion_form_and_no_inline_styles(self):
        for html in self.pages.values():
            self.assertEqual(html.count('/issues/new?template=resource.yml'), 1)
            self.assertNotIn(' style="', html)


if __name__ == '__main__':
    unittest.main()
