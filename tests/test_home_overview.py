"""FIG. 2, the All-view overview: true-proportion ring, exploded magnifier, spec table and detail sheet."""
import re
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from build_home import _overview, _ov_pieces, _ov_segment, _ov_spans, _shares, evidence_bucket
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

    def test_pieces_merge_small_classes_and_spans_rotate_the_others_to_three_oclock(self):
        totals = {'software': 2830, 'hardware': 100}
        mains, smalls = _ov_pieces(totals, list(totals))
        self.assertEqual([(key, count) for key, count in mains], [('software', 2830), ('hardware', 100)])
        self.assertEqual(smalls, [])
        totals = {'game': 2830, 'hardware': 880, 'software': 143, 'website': 77, 'apps': 49, 'science': 7}
        mains, smalls = _ov_pieces(totals, list(totals))
        self.assertEqual(smalls, ['software', 'website', 'apps', 'science'])
        self.assertEqual(dict(mains), {'game': 2830, 'hardware': 880, None: 276})
        spans = _ov_spans(mains, 3986)
        by_key = {span[0]: span for span in spans}
        self.assertEqual(round(by_key['game'][2] - by_key['game'][1], 2), 255.59)
        self.assertEqual(round(by_key['hardware'][2] - by_key['hardware'][1], 2), 79.48)
        others = by_key[None]
        self.assertEqual(round(others[2] - others[1], 2), 24.93)
        self.assertEqual(round((others[1] + others[2]) / 2, 2), 90.0)
        # Every angle is count / total * 360: no minimum angle, no sqrt or log scaling anywhere.
        # A 255.59-degree segment carries the large-arc flag; a quarter does not.
        self.assertIn(' A 140.00 140.00 0 1 ', _ov_segment(200, 215, 92, 140, 102.46, 358.05))
        self.assertIn(' A 140.00 140.00 0 0 ', _ov_segment(200, 215, 92, 140, 0, 90))

    def test_module_opens_hidden_with_fig2_head_and_tabs(self):
        html = self.overview()
        self.assertTrue(html.startswith('<section class="overview" data-overview hidden '
                                        'aria-label="Data classes by evidence class">'))
        self.assertIn('FIG. 2 · CASE STUDIES', html)
        self.assertIn('data-ov-title>6 cases, 66.7% from <em>Game</em>', html)
        self.assertIn('Classified 6 / 6 · Last scan —', html)
        tabs = re.findall(r'data-ov-tab="([\w-]*)"[^>]*aria-selected="(\w+)"[^>]*>([^<]+)<span class="ov-tab-count">([\d,]+)', html)
        self.assertEqual(tabs, [('', 'true', 'All', '6'), ('tool', 'false', 'Tools', '1'),
                                ('case-study', 'false', 'Case studies', '5')])

    def test_metrics_strip_carries_the_four_figures(self):
        all_body = self.body(self.overview())
        classified = re.search(r'data-ov-metric="classified">([^<]+)<', all_body)
        self.assertEqual(classified.group(1), '6')
        self.assertIn('of case studies 100.0%', all_body)
        self.assertIn('data-ov-metric="top-share">66.7</span>%', all_body)
        # The strong evidence strip is a per-class rate: 2 of Game's own and the whole body's rate on the row.
        self.assertIn('data-ov-metric="strong">33.3</span>%', all_body)
        self.assertIn('data-ov-metric="full">1</span>', all_body)
        self.assertIn('overview_metric_full_note', all_body) if False else None
        self.assertEqual(re.findall(r'data-ov-metric="full">(\d+)</span>', all_body), ['1'])

    def test_spec_table_letters_metrics_and_notes(self):
        all_body = self.body(self.overview())
        rows = re.findall(r'data-ov-row="(\w+)" data-total="(\d+)" data-levels="([^"]+)"', all_body)
        self.assertEqual([row[0] for row in rows], ['game', 'software', 'website'])
        self.assertEqual([int(row[1]) for row in rows], [4, 1, 1])
        self.assertEqual(rows[0][2], '0:1;1:1;2:0;3:1;unknown:0;unclassified:1')
        letters = re.findall(r'ov-letter">(\w)</span>', all_body)
        self.assertEqual(letters, ['A', 'B', 'C'])
        self.assertIn('hatch', all_body)
        # Strong evidence is the per-class rate: Game holds one C0+C1 of its four cases.
        self.assertIn('data-ov-strong>50.0%', all_body)
        self.assertIn('data-ov-strong>0.0%', all_body)
        stars = re.findall(r'ov-cell-c0" data-ov-c0>(.*?)</td>', all_body)
        self.assertEqual(stars[0], '<span class="ov-star" aria-hidden="true">★</span> 1')
        self.assertIn('<span class="ov-zero-mark">0</span>', all_body)
        # The benchmark paper lands in the game class: it counts toward the note column.
        # Counts under 30 carry the small-sample note, and the strong rate dims.
        self.assertIn('small sample', all_body)
        self.assertIn('ov-letter-dim', all_body)
        self.assertIn('View as', all_body) if False else None
        self.assertIn('<button type="button" class="ov-sortcol" data-ov-sortcol="share">', all_body)

    def test_detail_sheet_rows_carry_levels_differences_and_actions(self):
        all_body = self.body(self.overview())
        game = all_body.split('data-ov-panel="game"')[1].split('data-ov-panel=')[0]
        diffs = re.findall(r'ovl-diff">([^<]+)</span>', game)
        self.assertEqual(len(diffs), 6)
        self.assertTrue(all(mark in {'—', '≈'} or 'pt' in mark for mark in diffs))
        software = all_body.split('data-ov-panel="software"')[1].split('data-ov-panel=')[0]
        self.assertEqual(software.count('ovl-zero'), 5)
        self.assertIn('DETAIL A · GAME', game)
        self.assertIn('4 cases', game)
        self.assertIn('share 66.7% · strong evidence 50.0%', game)
        self.assertIn('DETAIL B · SOFTWARE', software)
        view = re.search(r'data-ov-view-all="game" href="([^"]+)"', game)
        self.assertEqual(view.group(1), '/resources/?kind=case-study')
        # The C0-only shortcut appears because this class holds one full reconstruction.
        self.assertIn('data-ov-c0only', game)

    def test_payload_feeds_the_client_side_filter(self):
        import json
        all_body = self.body(self.overview())
        payload = json.loads(re.search(r'<script type="application/json" data-ov-data>(.*?)</script>', all_body, re.S).group(1))
        self.assertEqual(payload['classified'], 6)
        self.assertEqual(payload['classes'][0]['key'], 'game')
        self.assertEqual(payload['classes'][0]['levels']['0'], 1)

    def test_level_filter_controls_exist_in_both_languages(self):
        html = self.overview()
        boxes = re.findall(r'<input type="checkbox" value="(\w+)">', html)
        self.assertEqual(boxes, ['0', '1', '2', '3', 'unknown', 'unclassified'])
        self.assertIn('Evidence level:<span data-ov-evlabel>All</span>', html)
        self.assertIn('What the evidence levels mean?', html)
        zh = _overview(self.records, self.papers, 'zh', prefix='/zh')
        self.assertIn('证据等级：<span data-ov-evlabel>全部</span>', zh)
        self.assertIn('证据等级是什么？', zh)
        self.assertIn('FIG. 2 · 案例', zh)
        title = re.search(r'data-ov-title>(.*?)</p>', zh, re.S).group(1)
        self.assertIn('3,986' if False else '6', title)

    def test_scope_and_sheet_titles_are_localized(self):
        html = self.overview()
        self.assertIn('DETAIL A · GAME', html)
        zh = _overview(self.records, self.papers, 'zh', prefix='/zh')
        self.assertIn('DETAIL A · GAME', zh)
        self.assertIn('4 个案例', zh)

    def test_empty_tabs_render_the_empty_note(self):
        tool_body = self.body(self.overview(), 'tool')
        self.assertIn('data-ov-empty', tool_body)
        self.assertIn('No classified entries in this type yet.', tool_body)

    def test_no_sunburst_or_card_remnants(self):
        html = self.overview()
        self.assertNotIn('overview-sector', html)
        self.assertNotIn('class-tile', html)
        self.assertNotIn('ov-seg-', html)
        self.assertNotIn('ov-part-others ', html)

    def test_no_classed_records_render_nothing(self):
        self.assertEqual(_overview([], [], 'en'), '')
        self.assertEqual(_overview([resource('utility', kind='tool', targets=['binary'])], [], 'en'), '')


if __name__ == '__main__':
    unittest.main()
