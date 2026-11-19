"""Data tabs, class routes, and the search index share one placement vocabulary."""
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
from build_home import _folder_tabs, search_index, search_row_id
from build_readme import SECTION_TABS
from data_classes import DATA_CLASSES, NON_DATA_TABS, listed_records
from resource_listing import resource_listing, resource_page_head
from test_case_pages import resource
from validate_site import Page


class DataTabTests(unittest.TestCase):
    def setUp(self):
        self.resources = [
            resource('older-game', added_at='2026-01-01', verified_at='2026-02-01', evidence_class=0,
                     preview='https://example.org/demo.png', preview_kind='video', **{'class': 'game'}),
            resource('newer-game', added_at='2026-03-01', verified_at='2026-03-01', **{'class': 'game'}),
            resource('web', targets=['website'], added_at='2026-02-01'),
            resource('utility', kind='tool', added_at='2026-04-01'),
        ]
        self.papers = [{'id': 'paper-game-data', 'title': 'Game dataset', 'title_zh': '游戏数据集',
                        'url': 'https://example.org/paper', 'kind': 'research', 'class': 'game',
                        'targets': ['game'], 'description_en': 'A game reconstruction dataset.',
                        'description_zh': '游戏重建数据集。', 'verified_at': '2026-04-01', 'added_at': '2026-04-01'}]

    def test_home_and_listing_tabs_have_data_only_counts_and_links(self):
        listed = listed_records(self.resources, self.papers)
        for language, prefix in [('en', ''), ('zh', '/zh')]:
            for html in (_folder_tabs(listed, language, prefix, len(self.papers)),
                         resource_page_head(listed, language, 1, len(self.papers))):
                tabs = re.findall(r'<a class="folder[^>]*?data-tab="([a-z]+)"[^>]*?>.*?<span class="count">(\d+)</span>', html)
                self.assertEqual([key for key, _ in tabs], ['all', *DATA_CLASSES, *NON_DATA_TABS])
                self.assertEqual(dict(tabs)['all'], '4')
                self.assertEqual(dict(tabs)['game'], '3')
                self.assertEqual(dict(tabs)['tools'], '1')
                self.assertEqual(dict(tabs)['paper'], '1')
                for key in DATA_CLASSES:
                    self.assertIn(f'href="{prefix}/data/{key}/" data-tab="{key}" data-link', html)

    def test_class_page_orders_resources_and_dataset_papers_by_added_date(self):
        with TemporaryDirectory() as directory:
            output = Path(directory)
            (output / 'papers.json').write_text(json.dumps(self.papers))
            build_discovery_pages(output, {'resources': self.resources, 'meta': {}}, None)
            for prefix in ('', 'zh/'):
                page = Page((output / prefix / 'data/game/index.html').read_text())
                self.assertEqual(page.record_ids, ['paper-game-data', 'newer-game', 'older-game'])
                html = (output / prefix / 'data/game/index.html').read_text()
                self.assertIn('data-tab="game" data-link aria-current="true"', html)
                self.assertIn('class="card-class card-class-0"', html)
                self.assertIn('class="card-preview"', html)
                self.assertIn('class="evidence-legend"', html)
                self.assertIn(f'href="/{prefix}papers/paper-game-data/"', html)
                self.assertIn('<h1>游戏数据</h1><span class="h-count">3 个数据点</span>' if prefix else
                              '<h1>Game data</h1><span class="h-count">3 data points</span>', html)
                if prefix:
                    description = re.search(r'<meta name="description" content="([^"]+)"', html).group(1)
                    self.assertGreaterEqual(len(re.findall(r'[\u3400-\u9fff]', description)), 50)

    def test_index_section_tabs_place_only_non_data_records(self):
        listed = listed_records(self.resources, self.papers)
        index = search_index(listed, self.papers, 'en', {})
        by_id = {record['id']: record for record in listed}
        def in_tab(row, tab):
            cls, section = row[14], row[11]
            if tab == 'all':
                return cls >= 0
            if tab in ('tools', 'tutorial'):
                return cls < 0 and index['sectionTabs'][section] == tab
            return cls >= 0 and index['classes'][cls] == tab
        for row in index['r']:
            record = by_id[search_row_id(row)]
            expected = record.get('class') or SECTION_TABS[index['sections'][row[11]]]
            self.assertEqual([tab for tab in ('all', *DATA_CLASSES, 'tools', 'tutorial') if in_tab(row, tab)],
                             ['all', expected] if 'class' in record else [expected])

    def test_listing_keeps_evidence_filter_with_data_tabs(self):
        listed = listed_records(self.resources, self.papers)
        html = resource_listing(listed, {}, {}, 'en', 'https://example.org')
        self.assertIn('data-class-select', html)
        self.assertIn('<option value="0">C0 (1)</option>', html)
        self.assertIn('class="evidence-legend"', html)
