"""Keep the README's long-task count tied to an explicit case classification."""
import json
from collections import Counter
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from benchmark_map import NOT_A_TASK, SHORT, TARGET, family_slots, long_by_family, render_svg


def cases():
    records = []
    for name in ('data/rea-resources.json', 'data/tool-resources.json'):
        records.extend(json.loads((ROOT / name).read_text(encoding='utf-8')))
    return [record for record in records if record.get('kind') == 'case-study']


class LongTaskScopeTests(unittest.TestCase):
    def test_every_case_is_classified_once_and_the_readme_states_the_gap(self):
        catalog = cases()
        identifiers = {record['id'] for record in catalog}
        self.assertFalse(SHORT & NOT_A_TASK)
        self.assertLessEqual(SHORT | NOT_A_TASK, identifiers)
        long_cases = [record for record in catalog if record['id'] not in SHORT and record['id'] not in NOT_A_TASK]
        by_target = Counter((record.get('targets') or ['?'])[0] for record in long_cases)
        self.assertEqual(
            (len(catalog), len(SHORT), len(NOT_A_TASK), len(long_cases), dict(sorted(by_target.items()))),
            (225, 18, 4, 203, {
                'app': 24, 'binary': 1, 'firmware': 6, 'game': 157, 'protocol': 11, 'website': 4,
            }),
        )
        self.assertLess(len(long_cases), TARGET)
        english = (ROOT / 'README.md').read_text(encoding='utf-8')
        chinese = (ROOT / 'README.zh-CN.md').read_text(encoding='utf-8')
        self.assertIn(
            '**203** of 225 curated cases are whole-program work large enough for a computer-use session past three hours, against a target of **1,000** (game 157, app 24, protocol 11, firmware 6, website 4, native binary 1).',
            english,
        )
        self.assertIn(
            '225 条精选案例中有 **203** 条属于完整程序规模，足够一次超过三小时的计算机使用会话，目标是 **1,000**（游戏 157、应用 24、协议 11、固件 6、网站 4、原生二进制 1）。',
            chinese,
        )
        self.assertIn('assets/benchmark-map.svg', english)
        self.assertIn('https://awesomerea.org/zh/benchmark-map/', chinese)
        grouped = long_by_family(catalog)
        self.assertEqual({key: len(records) for key, records in grouped.items()}, {
            'game': 157, 'app': 24, 'protocol': 11, 'firmware': 6, 'website': 4, 'binary': 1,
        })
        self.assertEqual(family_slots(), {
            'game': 167, 'app': 167, 'protocol': 167, 'firmware': 167, 'website': 166, 'binary': 166,
        })
        svg = render_svg(grouped)
        self.assertEqual((ROOT / 'assets/benchmark-map.svg').read_text(encoding='utf-8'), svg)
        self.assertEqual((ROOT / 'site/benchmark-map.svg').read_text(encoding='utf-8'), svg)
        self.assertIn('203 of 1,000 slots have a long task', svg)
        self.assertIn('<h1>Benchmark map</h1>', (ROOT / 'site/benchmark-map/index.html').read_text(encoding='utf-8'))
        self.assertIn('<h1>基准图</h1>', (ROOT / 'site/zh/benchmark-map/index.html').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
