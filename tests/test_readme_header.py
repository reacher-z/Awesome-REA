"""Keep both README openings in the shape awesome-lint expects: the title first, then the compact badge."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
TITLE = '# Awesome Reverse Engineering Anything'
BANNERS = ('assets/brand/readme-banner-light.svg', 'assets/brand/readme-banner-dark.svg')


class ReadmeHeaderTest(unittest.TestCase):
    def test_title_comes_first_and_the_banner_follows_it_in_light_and_dark(self):
        for name, home in (('README.md', 'https://awesomerea.org/'), ('README.zh-CN.md', 'https://awesomerea.org/zh/')):
            with self.subTest(readme=name):
                text = (ROOT / name).read_text(encoding='utf-8')
                # awesome-lint counts a leading centered HTML block with an image as a second list heading.
                self.assertTrue(text.startswith(TITLE + '\n\n'), text[:200])
                self.assertEqual(len(re.findall(r'^# ', text, re.MULTILINE)), 1)
                banner = text.split('\n\n')[1]
                self.assertTrue(banner.startswith(f'<a href="{home}"><picture>\n'), banner)
                self.assertIn(f'<source media="(prefers-color-scheme: dark)" srcset="{BANNERS[1]}">', banner)
                self.assertIn(f'<img src="{BANNERS[0]}" alt="Awesome Reverse Engineering Anything', banner)
                for path in BANNERS:
                    self.assertTrue((ROOT / path).is_file(), path)
                    self.assertLessEqual((ROOT / path).stat().st_size, 60_000, path)

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
