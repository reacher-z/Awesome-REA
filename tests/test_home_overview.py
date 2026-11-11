"""The All-tab overview: class totals, evidence splits and the selectable donut."""
import re
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from build_home import _overview, evidence_bucket
from data_classes import DATA_CLASSES
from test_case_pages import resource


class OverviewTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            resource('game-full', **{'class': 'game'}, evidence_class=0, evidence_status='observed'),
            resource('game-partial', **{'class': 'game'}, evidence_class=1, evidence_status='observed'),
            resource('game-notes', **{'class': 'game'}, evidence_class=3, evidence_status='observed'),
            resource('website-docs', targets=['website'], **{'class': 'website'}, evidence_class=2, evidence_status='observed'),
            resource('software-gone', **{'class': 'software'}, evidence_class=None, evidence_status='unknown'),
            # A benchmark paper is a classed record without a source class.
            {'id': 'paper-game-benchmark', 'name': 'Benchmark', 'name_zh': '基准', 'class': 'game', 'kind': 'research',
             'targets': ['game'], 'url': 'https://example.org/benchmark', 'verified_at': '2026-10-17'},
        ]

    def test_evidence_bucket_separates_unreadable_and_unclassified_records(self):
        self.assertEqual(evidence_bucket(self.records[0]), '0')
        self.assertEqual(evidence_bucket(self.records[3]), '2')
        self.assertEqual(evidence_bucket(self.records[4]), 'unknown')
        self.assertEqual(evidence_bucket(self.records[5]), 'unclassified')

    def test_overview_counts_classes_and_evidence_splits(self):
        html = _overview(self.records, 'en', '')
        tiles = dict(re.findall(r'<span class="ct-name">(.*?)</span><span class="ct-count">(\d+)</span>', html))
        self.assertEqual(tiles, {'Software': '1', 'Game': '4', 'Website': '1'})
        self.assertIn('class="overview-total" x="320" y="314" text-anchor="middle">6</text>', html)
        # Present classes keep DATA_CLASSES order; each class's bands are its non-empty evidence buckets.
        self.assertEqual(re.findall(r'class="overview-band overview-(\w+)"', html),
                         ['unknown', '0', '1', '3', 'unclassified', '2'])
        self.assertIn('aria-label="Game: 4 data points. C0 1, C1 1, C2 0, C3 1, ? 0, – 1"', html)

    def test_details_show_every_evidence_bucket_and_link_the_class_page(self):
        html = _overview(self.records, 'en', '')
        self.assertEqual(html.count('data-overview-detail='), 3)
        self.assertRegex(html, r'data-overview-detail="software">')
        for label in ('full software reconstruction', 'partial scope or analysis entry', 'code &amp; docs, no demo or download',
                      'notes only', 'source unavailable or unreadable', 'benchmark &amp; dataset papers'):
            self.assertIn(f'<span class="od-label">{label}</span>', html)
        self.assertIn('href="/data/software/">Browse Software', html)
        self.assertIn('class="card-class card-class-none">–</span>', html)

    def test_first_class_is_selected_and_chinese_copy_links_chinese_pages(self):
        for language, prefix, browse in (('en', '', 'Browse Software'), ('zh', '/zh', '查看软件')):
            html = _overview(self.records, language, prefix)
            self.assertEqual(re.findall(r'data-overview-tile="(\w+)" aria-controls="overview-detail-\w+" aria-pressed="(true|false)"', html),
                             [('software', 'true'), ('game', 'false'), ('website', 'false')])
            self.assertIn(f'href="{prefix}/data/software/">{browse}', html)
        html = _overview(self.records, 'zh', '/zh')
        self.assertIn('数据点', html)
        self.assertIn('基准与数据集论文', html)

    def test_no_classed_records_render_nothing(self):
        self.assertEqual(_overview([], 'en', ''), '')
        self.assertEqual(_overview([resource('utility', kind='tool', targets=['binary'])], 'en', ''), '')


if __name__ == '__main__':
    unittest.main()
