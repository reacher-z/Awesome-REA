"""README entries stay one line each, and an advisory budget warns before GitHub truncates a README."""
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_readme
from build_readme import (FULL_ENTRY, GITHUB_README_LIMIT, README_SIZE_WARNING, lead_sentence,
                          readme_size_warnings, size_warning)
from catalog import load_resources
from validate_papers import read_papers


class ReadmeSizeBudgetTest(unittest.TestCase):
    def test_budget_warns_well_before_the_github_rendering_limit(self):
        self.assertEqual(GITHUB_README_LIMIT, 512_000)
        self.assertLess(README_SIZE_WARNING, GITHUB_README_LIMIT - 60_000)
        self.assertIsNone(size_warning('README.md', README_SIZE_WARNING))
        note = size_warning('README.md', README_SIZE_WARNING + 1)
        self.assertIn('README.md is 420,001 bytes', note)
        self.assertIn('420,000-byte budget', note)
        self.assertIn('91,999 bytes are left', note)
        over = size_warning('README.zh-CN.md', GITHUB_README_LIMIT + 2_500)
        self.assertIn('README.zh-CN.md is 514,500 bytes', over)
        self.assertIn('last 2,500 bytes are already cut off', over)

    def test_size_warnings_measure_utf8_bytes_on_disk(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'README.md').write_text('a' * 10, encoding='utf-8')
            # 140,001 three-byte characters are 420,003 bytes although the text has fewer characters.
            (root / 'README.zh-CN.md').write_text('文' * 140_001, encoding='utf-8')
            notes = readme_size_warnings(root)
        self.assertEqual(len(notes), 1)
        self.assertTrue(notes[0].startswith('README.zh-CN.md is 420,003 bytes'), notes[0])

    def test_builder_check_reports_sizes_and_never_fails_on_size(self):
        for warning in (README_SIZE_WARNING, 1_000):
            with self.subTest(warning=warning):
                stdout, stderr = io.StringIO(), io.StringIO()
                with patch.object(build_readme, 'README_SIZE_WARNING', warning), \
                        patch.object(sys, 'argv', ['build_readme.py', '--check']), \
                        redirect_stdout(stdout), redirect_stderr(stderr):
                    status = build_readme.main()
                self.assertEqual(status, 0, stderr.getvalue())
                self.assertRegex(stdout.getvalue(), r'README\.md [\d,]+ bytes, README\.zh-CN\.md [\d,]+ bytes')
                warnings = re.findall(r'^Warning: (README(?:\.zh-CN)?\.md) is ', stderr.getvalue(), re.M)
                self.assertEqual(warnings, [] if warning == README_SIZE_WARNING else ['README.md', 'README.zh-CN.md'])


class LeadSentenceTest(unittest.TestCase):
    def test_english_lead_skips_abbreviations_initials_and_bracketed_periods(self):
        cases = {
            'Translates Super Smash Bros. Ultimate code ahead of time into C++. It needs a dump.':
                'Translates Super Smash Bros. Ultimate code ahead of time into C++.',
            'Eric S. Raymond’s terminal port of the game, rebuilt in Rust. Second sentence.':
                'Eric S. Raymond’s terminal port of the game, rebuilt in Rust.',
            'A decompilation in which part of the code has been decompiled to C. Each build checks hashes.':
                'A decompilation in which part of the code has been decompiled to C.',
            'Runtime for static recompilations, made of two libraries. ultramodern reimplements services.':
                'Runtime for static recompilations, made of two libraries.',
            'Compares tools (e.g. Ghidra. Or IDA) on shared tasks for analysts. Results vary.':
                'Compares tools (e.g. Ghidra. Or IDA) on shared tasks for analysts.',
            'Ports WWE SmackDown vs. Raw 2011 to C++ ahead of time with a runtime. More.':
                'Ports WWE SmackDown vs. Raw 2011 to C++ ahead of time with a runtime.',
            # Openings shorter than 40 characters keep the next sentence.
            'Recompiles Banjo. The port runs natively on modern PCs.':
                'Recompiles Banjo. The port runs natively on modern PCs.',
            'One sentence without a break': 'One sentence without a break',
            '  Spaces\n and   breaks are normalized. Second sentence here.  ':
                'Spaces and breaks are normalized. Second sentence here.',
        }
        for text, lead in cases.items():
            with self.subTest(text=text):
                self.assertEqual(lead_sentence(text, 'en'), lead)

    def test_chinese_lead_uses_full_width_punctuation_outside_quotes(self):
        self.assertEqual(lead_sentence('实现宏键盘的厂商 HID 配置协议（含“写入。读取”流程）。第二句说明限制。', 'zh'),
                         '实现宏键盘的厂商 HID 配置协议（含“写入。读取”流程）。')
        self.assertEqual(lead_sentence('ExeBench 是数据集，而非反编译器。它提供可执行函数。', 'zh'),
                         'ExeBench 是数据集，而非反编译器。')
        # English periods inside Chinese text are not sentence ends, and a short opening keeps the next sentence.
        self.assertEqual(lead_sentence('支持 v1.2. 版本。很短。', 'zh'), '支持 v1.2. 版本。很短。')


class OneLineEntryTest(unittest.TestCase):
    def test_generated_readmes_list_each_entry_on_one_line_with_its_full_entry_link(self):
        papers = read_papers(ROOT)
        paper_urls = {paper['url'] for paper in papers}
        resources = [record for record in load_resources() if record['url'] not in paper_urls]
        for name, index in (('README.md', 0), ('README.zh-CN.md', 1)):
            prefix = 'zh/' if index else ''
            text = (ROOT / name).read_text(encoding='utf-8')
            lines = [line for line in text.splitlines() if line.startswith('- [**')]
            with self.subTest(readme=name):
                self.assertEqual(len(lines), len(resources) + len(papers))
                self.assertNotIn('<details>', text)
                for route, records in (('resources', resources), ('papers', papers)):
                    for record in records:
                        link = f'[{FULL_ENTRY[index]}](https://awesomerea.org/{prefix}{route}/{record["id"]}/)</sub>'
                        self.assertEqual(sum(line.endswith(link) for line in lines), 1, record['id'])


if __name__ == '__main__':
    unittest.main()
