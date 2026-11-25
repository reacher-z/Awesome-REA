"""The All-view overview: kind tabs, single-colour class rows drawn to scale, level filter and detail panels."""
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
        # A benchmark paper is a classed record that is not a catalog resource.
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
        # A count that rounds to zero stays visible as <0.1; a true zero shows 0.
        rounding = _shares({'0': 1, '1': 1, '2': 2000, '3': 0}, ('0', '1', '2', '3'))
        self.assertEqual(rounding['2'], '99.9')
        self.assertTrue(rounding['1'].startswith('<'))
        self.assertEqual(rounding['3'], '0')

    def test_module_opens_hidden_with_label_and_kind_tabs(self):
        html = self.overview()
        self.assertTrue(html.startswith('<section class="overview" data-overview hidden '
                                        'aria-label="Data classes by evidence class">'))
        tabs = re.findall(r'data-ov-tab="([\w-]*)"[^>]*aria-selected="(\w+)"[^>]*>([^<]+)<span class="ov-tab-count">([\d,]+)', html)
        self.assertEqual(tabs, [('', 'true', 'All', '6'), ('tool', 'false', 'Tools', '1'),
                                ('case-study', 'false', 'Case studies', '5')])

    def test_rows_rank_by_count_and_bars_scale_to_the_classified_total(self):
        all_body = self.body(self.overview())
        rows = re.findall(r'data-ov-row="(\w+)"[^>]*data-total="(\d+)"[^>]*data-share="([\d.]+)"[^>]*'
                          r'data-name="[^"]*" data-levels="([^"]+)"', all_body)
        self.assertEqual([(row[0], int(row[1]), row[2]) for row in rows],
                         [('game', 4, '66.7'), ('software', 1, '16.7'), ('website', 1, '16.6')])
        # The levels attribute carries every bucket for the client-side level filter.
        self.assertEqual(rows[0][3], '0:1;1:1;2:0;3:1;unknown:0;unclassified:1')
        self.assertEqual(rows[1][3], '0:0;1:0;2:0;3:0;unknown:1;unclassified:0')
        widths = re.findall(r'class="ov-fill" data-w="([\d.]+)"', all_body)
        self.assertEqual(widths, ['66.67', '16.67', '16.67'])
        # The lead number is the share; the count sits beside it in the small grey style.
        self.assertIn('<span class="ov-cell ov-cell-share" data-ov-share>66.7%</span>', all_body)
        self.assertIn('<span class="ov-cell ov-cell-count" data-ov-count>4</span>', all_body)
        self.assertNotIn('ov-seg', all_body)

    def test_row_aria_labels_carry_counts(self):
        all_body = self.body(self.overview())
        aria = re.search(r'data-ov-row="game"[^>]*aria-label="([^"]+)"', all_body)
        self.assertEqual(aria.group(1),
                         'Game, 4 entries, 66.7%. C0 1, C1 1, C2 0, C3 1, unknown 0, benchmark papers 1.')
        single = re.search(r'data-ov-row="software"[^>]*aria-label="([^"]+)"', all_body)
        self.assertIn('Software, 1 entry, 16.7%.', single.group(1))

    def test_default_selection_is_the_largest_class_with_its_panel_open(self):
        all_body = self.body(self.overview())
        self.assertIn('data-ov-row="game" aria-selected="true" tabindex="0"', all_body)
        self.assertIn('data-ov-row="website" aria-selected="false" tabindex="-1"', all_body)
        self.assertNotIn('id="ov-panel--game" role="group" aria-label="Game" hidden', all_body)
        self.assertIn('id="ov-panel--website" role="group" aria-label="Website" hidden', all_body)

    def test_panels_list_every_level_with_dots_and_no_mini_bars(self):
        all_body = self.body(self.overview())
        software = all_body.split('data-ov-panel="software"')[1].split('data-ov-panel=')[0]
        for code in ('C0', 'C1', 'C2', 'C3', '?', '–'):
            self.assertIsNotNone(re.search(f'ovd-dot[^>]*></span>\n?<span class="ovd-code">{re.escape(code)}</span>'.replace('\n?', '\\s*'),
                                           software), f'{code} row missing')
        self.assertEqual(software.count('ovd-dot-'), 6)
        self.assertNotIn('ovd-mini', software)
        self.assertEqual(software.count('ovd-zero'), 5)
        # The display number is the share; the counts follow in the sub line.
        self.assertIn('<span class="ovd-total" data-ovd-share>16.7%</span>', software)
        self.assertIn('1 of 6 entries', software)
        self.assertIn('Evidence mix', software)
        link = re.search(r'data-ov-view-all="software" href="([^"]+)"', software)
        self.assertEqual(link.group(1), '/resources/?kind=case-study')

    def test_scope_line_states_both_totals_and_the_toolbar_carries_level_filter_and_sort(self):
        html = self.overview()
        all_body = self.body(html)
        self.assertIn('Classified <strong>6</strong> of <strong>6</strong> entries', all_body)
        self.assertIn('data-ov-scope data-ov-scope-default=', all_body)
        boxes = re.findall(r'<input type="checkbox" value="(\w+)">', html)
        self.assertEqual(boxes, ['0', '1', '2', '3', 'unknown', 'unclassified'])
        self.assertIn('Evidence level：<span data-ov-evlabel>All</span>'.replace('：', ':'), html)
        options = re.findall(r'<option value="(\w+)">([^<]+)</option>', html)
        self.assertEqual(options, [('share', 'Share'), ('name', 'Name A–Z')])
        self.assertNotIn('ov-mode', html)
        tool_body = self.body(html, 'tool')
        self.assertIn('data-ov-empty', tool_body)
        self.assertIn('No classified entries in this type yet.', tool_body)

    def test_table_lists_every_class_and_bucket(self):
        all_body = self.body(self.overview())
        table = all_body.split('<details class="ov-table">')[1]
        self.assertEqual(re.findall(r'<th scope="col">([^<]+)</th>', table)[:8],
                         ['Data class', 'Total', 'C0', 'C1', 'C2', 'C3', '?', '–'])
        self.assertIn('<th scope="row">Game</th><td>4</td><td>1</td><td>1</td><td>0</td><td>1</td><td>0</td><td>1</td></tr>', table)

    def test_chinese_copy_is_localized(self):
        html = _overview(self.records, self.papers, 'zh', prefix='/zh')
        self.assertIn('已分类 <strong>6</strong> 条 · 共 <strong>6</strong> 条', html)
        self.assertIn('证据等级构成', html)
        self.assertIn('证据等级：<span data-ov-evlabel>全部</span>', html)
        self.assertIn('查看全部 4 条', html)
        aria = re.search(r'data-ov-row="game"[^>]*aria-label="([^"]+)"', html)
        self.assertEqual(aria.group(1), '游戏，4 条，占 66.7%。C0 1，C1 1，C2 0，C3 1，未知 0，基准论文 1。')
        link = re.search(r'data-ov-view-all="game" href="([^"]+)"', html)
        self.assertEqual(link.group(1), '/zh/resources/?kind=case-study')

    def test_no_donut_or_evidence_bar_remains(self):
        html = self.overview()
        self.assertNotIn('viewBox="0 0 640', html)
        self.assertNotIn('overview-sector', html)
        self.assertNotIn('ov-seg', html)
        self.assertNotIn('ov-summary-bar', html)
        self.assertNotIn('ov-legend', html)

    def test_no_classed_records_render_nothing(self):
        self.assertEqual(_overview([], [], 'en'), '')
        self.assertEqual(_overview([resource('utility', kind='tool', targets=['binary'])], [], 'en'), '')


if __name__ == '__main__':
    unittest.main()
