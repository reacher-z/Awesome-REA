"""The generated totals line above README Contents is derived from the data, never hand-maintained."""
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_readme import (COLLECTION_SECTIONS, CONTENTS_BEGIN, CONTENTS_END, browsable_index_count, render_contents,
                          render_totals, replace_contents)
from catalog import load_resources
from validate_papers import read_papers


def resource(**changes):
    record = deepcopy(json.loads((ROOT / 'data/tool-resources.json').read_text(encoding='utf-8'))[0])
    record.update(id='totals-fixture', kind='tool', url='https://example.com/tool', verified_at='2026-01-02')
    record.update(changes)
    return record


def paper(**changes):
    record = deepcopy(json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))[0])
    record.update(url='https://example.com/paper', verified_at='2026-01-01')
    record.update(changes)
    return record


class ReadmeTotalsTest(unittest.TestCase):
    def test_counts_cases_index_and_newest_review_date(self):
        records = [resource(), resource(id='case', kind='case-study', url='https://example.com/case',
                                        verified_at='2026-03-04T05:06:07Z'),
                   resource(id='paper-copy', kind='research', url='https://example.com/paper')]
        papers = [paper(), paper(id='second', url='https://example.com/second', verified_at='2026-02-01')]
        before = deepcopy((records, papers))
        self.assertEqual(render_totals(records, papers, 2836, 'en'),
                         '3 curated resources (1 cases) · 2 papers · 2,836 indexed repositories · '
                         'latest source review 2026-03-04. Section counts add up to 2 because '
                         '1 of these appear only under Papers.\n\n')
        self.assertEqual(render_totals(records, papers, 2836, 'zh'),
                         '3 项精选资源（1 个案例）· 2 篇论文 · 2,836 个已索引仓库 · 最近来源复核 2026-03-04。'
                         '其中 1 项仅列于论文部分，因此各分区计数合计 2。\n\n')
        self.assertEqual((records, papers), before)
        # A paper reviewed after every resource sets the date; without overlaps there is no note.
        latest = [paper(verified_at='2026-05-06')]
        self.assertEqual(render_totals([resource()], latest, 1, 'en'),
                         '1 curated resources (0 cases) · 1 papers · 1 indexed repositories · '
                         'latest source review 2026-05-06.\n\n')

    def test_section_sum_in_the_note_matches_contents(self):
        records, papers = load_resources(), read_papers(ROOT)
        contents = render_contents(records, papers, 0, 'en')
        listed = sum(int(count.replace(',', '')) for section, count in re.findall(r'\]\(#([a-z-]+)\) \(([\d,]+)\)', contents)
                     if section in COLLECTION_SECTIONS)
        line = render_totals(records, papers, 0, 'en')
        if listed == len(records):
            self.assertNotIn('only under Papers', line)
        else:
            self.assertIn(f'Section counts add up to {listed:,} because {len(records) - listed:,} of these appear '
                          'only under Papers.', line)

    def test_generated_readmes_carry_the_current_line_and_go_stale_with_the_data(self):
        records, papers, index_count = load_resources(), read_papers(ROOT), browsable_index_count()
        for name, language in (('README.md', 'en'), ('README.zh-CN.md', 'zh')):
            with self.subTest(readme=name):
                text = (ROOT / name).read_text(encoding='utf-8')
                block = text.split(CONTENTS_BEGIN + '\n', 1)[1].split(CONTENTS_END, 1)[0]
                line = render_totals(records, papers, index_count, language)
                self.assertTrue(block.startswith(line), block[:200])
                newer = deepcopy(records)
                newer[0]['verified_at'] = '2999-01-01'
                stale = render_totals(newer, papers, index_count, language)
                self.assertNotEqual(stale, line)
                regenerated = replace_contents(text, stale + render_contents(records, papers, index_count, language))
                self.assertNotEqual(regenerated, text)
                self.assertNotEqual(render_totals(records, papers, index_count + 1, language), line)


if __name__ == '__main__':
    unittest.main()
