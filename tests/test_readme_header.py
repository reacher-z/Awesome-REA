"""Keep both README openings in the shape awesome-lint expects: the title first, then the compact badge."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
TITLE = '# Awesome Reverse Engineering Anything'
BANNERS = ('assets/brand/wordmark-light.svg', 'assets/brand/wordmark-dark.svg')


class ReadmeHeaderTest(unittest.TestCase):
    def test_wordmark_is_the_title_and_has_distinct_light_and_dark_files(self):
        for name, home in (('README.md', 'https://awesomerea.org/'), ('README.zh-CN.md', 'https://awesomerea.org/zh/')):
            with self.subTest(readme=name):
                text = (ROOT / name).read_text(encoding='utf-8')
                # The banner is the page title: one H1 holds the picture, so no text heading repeats the banner.
                self.assertTrue(text.startswith('<h1 align="center"><a href="' + home + '"><picture>'), text[:200])
                self.assertEqual(len(re.findall(r'^# ', text, re.MULTILINE)), 0)
                banner = text.split('\n', 1)[0]
                self.assertIn(f'<source media="(prefers-color-scheme: dark)" srcset="{BANNERS[1]}">', banner)
                self.assertIn(f'<img src="{BANNERS[0]}" alt="Awesome Reverse Engineering Anything', banner)
                self.assertTrue(banner.endswith('</picture></a></h1>'), banner[-80:])
                for path in BANNERS:
                    self.assertTrue((ROOT / path).is_file(), path)
                    self.assertLessEqual((ROOT / path).stat().st_size, 60_000, path)
                self.assertIn('assets/brand/tagline-dark.svg', text.split('</div>', 1)[0])
        self.assertNotEqual((ROOT / BANNERS[0]).read_bytes(), (ROOT / BANNERS[1]).read_bytes())

    def test_find_by_task_table_pipes_line_up(self):
        for name, heading in (('README.md', '## Find by task'), ('README.zh-CN.md', '## 按任务查找')):
            with self.subTest(readme=name):
                text = (ROOT / name).read_text(encoding='utf-8')
                rows = text.split(f'\n{heading}\n\n', 1)[1].split('\n\n', 1)[0].splitlines()
                self.assertGreater(len(rows), 2)
                # remark-lint's table-pipe-alignment compares character offsets, so every row has its pipes there.
                pipes = [[index for index, character in enumerate(row) if character == '|'] for row in rows]
                self.assertEqual(len({tuple(positions) for positions in pipes}), 1, rows)
                self.assertRegex(rows[1], r'^\| -+ \| -+ \|$')


if __name__ == '__main__':
    unittest.main()
