"""Keep both README openings in the shape awesome-lint expects: the title first, then the compact badge."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
TITLE = '# Awesome Reverse Engineering Anything'
BADGE = 'assets/featured-by-awesome-rea-compact.svg'


class ReadmeHeaderTest(unittest.TestCase):
    def test_title_comes_first_and_the_badge_is_a_plain_line_below_it(self):
        for name, home in (('README.md', 'https://awesomerea.org/'), ('README.zh-CN.md', 'https://awesomerea.org/zh/')):
            with self.subTest(readme=name):
                text = (ROOT / name).read_text(encoding='utf-8')
                # awesome-lint counts a leading centered HTML block with an image as a second list heading.
                self.assertTrue(text.startswith(TITLE + '\n\n'), text[:200])
                self.assertEqual(len(re.findall(r'^# ', text, re.MULTILINE)), 1)
                badge = text.split('\n\n')[1]
                self.assertEqual(badge, f'<a href="{home}"><img src="{BADGE}" alt="Featured by Awesome REA" '
                                        'width="200" height="48"></a>')
                self.assertEqual(text.count(BADGE), 1)

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
