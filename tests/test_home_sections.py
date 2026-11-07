import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import home_sections as sections  # noqa: E402


def resource(identifier, added=None, kind='tool', category='native-analysis', targets=('binary',)):
    record = {'id': identifier, 'name': identifier.title(), 'kind': kind, 'category': category, 'targets': list(targets),
              'relationship': 'independent', 'url': f'https://example.org/{identifier}'}
    return {**record, 'added_at': added} if added else record


class LatestTests(unittest.TestCase):
    def test_window_counts_back_from_the_newest_record_not_the_clock(self):
        records = [resource('new', '2020-03-20'), resource('close', '2020-03-06'), resource('old', '2020-03-05')]
        html = sections.latest(records, None, 'en', lambda record: 'BIN·TOOL')
        self.assertIn('/resources/new/', html)
        self.assertIn('/resources/close/', html)
        self.assertNotIn('/resources/old/', html)

    def test_scan_records_stay_labelled_and_never_repeat_a_curated_url(self):
        curated = resource('curated', '2020-03-20')
        queue = {'record_count': 2, 'listed': [
            {'full_name': 'someone/curated', 'url': 'https://example.org/curated/', 'stars': 9, 'description_en': 'Already listed.'},
            {'full_name': 'someone/found', 'url': 'https://example.org/found', 'stars': 1, 'description_en': 'Found by a scan.'},
        ]}
        html = sections.latest([curated], queue, 'en', lambda record: 'BIN·TOOL')
        self.assertIn('someone/found', html)
        self.assertNotIn('someone/curated', html)
        self.assertEqual(html.count('Unreviewed</span>'), 1)


class YearChartTests(unittest.TestCase):
    def test_bars_use_classes_because_csp_forbids_style_attributes(self):
        papers = [{'year': 2020}, {'year': 2022}, {'year': 2022}]
        html = sections.year_chart(papers, 'en')
        self.assertNotIn('style=', html)
        self.assertEqual(re.findall(r'yb-h(\d+)', html), ['50', '100'])
        self.assertEqual(html.count('class="yb-col"'), 3)
        self.assertIn('2 in 2022', html)

    def test_every_generated_bar_height_has_a_rule(self):
        css = (ROOT / 'site/rea.css').read_text(encoding='utf-8')
        for step in range(2, 101, 2):
            self.assertIn(f'.yb-h{step} {{', css)


class CaseBandTests(unittest.TestCase):
    def test_every_case_counts_but_only_game_methods_get_folders(self):
        cases = [resource('game', kind='case-study', targets=('game',)), resource('tool')]
        html = sections.case_band(cases, 'en')
        self.assertIn('<span class="cb-n">1</span>', html)


if __name__ == '__main__':
    unittest.main()
