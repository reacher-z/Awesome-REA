"""FIG. 2, the All-view overview: class bars drawn to scale, spec table and detail sheet."""
import re
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from build_home import _overview, _shares, evidence_bucket
from test_case_pages import resource


class OverviewTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            resource('game-full', **{'class': 'game'}, evidence_class=0, evidence_status='observed'),
            resource('game-partial', **{'class': 'game'}, evidence_class=1, evidence_status='observed'),
            resource('game-notes', **{'class': 'game'}, evidence_class=3, evidence_status='observed'),
            resource('website-docs', targets=['website'], **{'class': 'website'}, evidence_class=2, evidence_status='observed'),
            resource('software-gone', **{'class': 'software'}, evidence_class=None, evidence_status='unknown'),
            resource('utility', kind='tool', targets=['binary']),
        ]
        self.papers = [
            {'id': 'paper-game-benchmark', 'name': 'Benchmark', 'name_zh': '基准', 'class': 'game', 'kind': 'research',
             'targets': ['game'], 'url': 'https://example.org/benchmark', 'verified_at': '2026-10-17'},
        ]

    def overview(self, language='en'):
        return _overview(self.records, self.papers, language)

    def body(self, html, key=''):
        parts = html.split(f'data-ov-body="{key}"')
        return parts[1].split('<div class="ov-body"')[0]

    def test_evidence_bucket_separates_unreadable_and_unclassified_records(self):
        self.assertEqual(evidence_bucket(self.records[0]), '0')
        self.assertEqual(evidence_bucket(self.records[3]), '2')
        self.assertEqual(evidence_bucket(self.records[4]), 'unknown')
        self.assertEqual(evidence_bucket(self.papers[0]), 'unclassified')

    def test_shares_sum_to_one_hundred(self):
        values = {'0': 4, '1': 22, '2': 108, '3': 4, 'unknown': 0, 'unclassified': 5}
        shares = _shares(values, ('0', '1', '2', '3', 'unknown', 'unclassified'))
        self.assertEqual([shares[key] for key in ('0', '1', '2', '3', 'unclassified')],
                         ['2.8', '15.4', '75.5', '2.8', '3.5'])
        self.assertEqual(sum(float(share) for share in shares.values()), 100.0)

    def test_module_opens_hidden_with_fixed_title_and_tabs(self):
        html = self.overview()
        self.assertTrue(html.startswith('<section class="overview" data-overview hidden '))
        self.assertIn('FIG. 2 · BY TARGET DOMAIN', html)
        self.assertIn('Cases by target <em>domain</em>', html)
        self.assertIn('data-ov-tab=""', html)
        self.assertIn('data-ov-tab="case-study"', html)
        self.assertIn('data-ov-tab="tool"', html)

    def test_rows_follow_data_class_display_order_with_letters_and_fills(self):
        all_body = self.body(self.overview())
        rows = re.findall(r'data-ov-row="(\w+)" data-total="(\d+)"', all_body)
        self.assertEqual([row[0] for row in rows], ['software', 'game', 'website'])
        self.assertEqual([int(row[1]) for row in rows], [1, 4, 1])
        letters = re.findall(r'class="ov-letter">(\w)</span>', all_body)
        self.assertEqual(letters, list('ABC'))
        fills = re.findall(r'class="ov-fill" data-w="([\d.]+)"', all_body)
        self.assertEqual(fills, ['25.00', '100.00', '25.00'])
        levels = re.findall(r'data-levels="([^"]+)"', all_body)
        self.assertEqual(levels[0], '0:0;1:0;2:0;3:0;unknown:1;unclassified:0')

    def test_row_labels_carry_counts_and_strong_evidence(self):
        all_body = self.body(self.overview())
        self.assertIn('data-ov-strong>50.0%</span>', all_body)
        self.assertIn('data-ov-strong>0.0%</span>', all_body)
        self.assertIn('strong evidence', all_body)

    def test_metrics_strip_carries_the_four_figures(self):
        all_body = self.body(self.overview())
        self.assertIn('data-ov-metric="entries">6</span>', all_body)
        self.assertIn('data-ov-metric="domains">3</span>', all_body)
        self.assertIn('data-ov-metric="full">1</span>', all_body)

    def test_all_row_is_a_ledger_summary(self):
        all_body = self.body(self.overview())
        self.assertIn('ov-spec-all', all_body)
        self.assertIn('100%', all_body)

    def test_zero_class_rows_stay_visible(self):
        all_body = self.body(self.overview())
        for key in ('software', 'game', 'website'):
            self.assertIn(f'data-ov-row="{key}"', all_body)

    def test_payload_feeds_the_client_side_filter(self):
        import json
        all_body = self.body(self.overview())
        payload = json.loads(re.search(r'<script type="application/json" data-ov-data>(.*?)</script>', all_body, re.S).group(1))
        self.assertEqual(payload['classified'], 6)
        self.assertEqual(len(payload['classes']), 3)
        game = next(c for c in payload['classes'] if c['key'] == 'game')
        self.assertEqual(game['levels']['0'], 1)
        self.assertEqual(game['levels']['unclassified'], 1)

    def test_sheet_panels_carry_levels_and_actions(self):
        all_body = self.body(self.overview())
        self.assertIn('data-ov-panel=', all_body)
        self.assertIn('data-ov-view-all=', all_body)
        self.assertIn('ovl-zero', all_body)
        self.assertIn('/resources/?kind=case-study', all_body)
        self.assertIn('data-ov-c0only', all_body)

    def test_chinese_copy_is_localized(self):
        html = _overview(self.records, self.papers, 'zh', prefix='/zh')
        self.assertIn('按目标<em>领域</em>分布', html)
        self.assertIn('证据等级', html)
        self.assertIn('证据等级', html)
        link = re.search(r'data-ov-view-all="game" href="([^"]+)"', html)
        if link:
            self.assertEqual(link.group(1), '/zh/resources/?kind=case-study')

    def test_empty_tabs_render_the_empty_note(self):
        tool_body = self.body(self.overview(), 'tool')
        self.assertIn('data-ov-empty', tool_body)
        self.assertIn('No classified entries in this type yet.', tool_body)

    def test_no_sunburst_or_card_remnants(self):
        html = self.overview()
        self.assertNotIn('overview-sector', html)
        self.assertNotIn('class-tile', html)

    def test_no_classed_records_render_nothing(self):
        self.assertEqual(_overview([], [], 'en'), '')
        self.assertEqual(_overview([resource('utility', kind='tool', targets=['binary'])], [], 'en'), '')


if __name__ == '__main__':
    unittest.main()
