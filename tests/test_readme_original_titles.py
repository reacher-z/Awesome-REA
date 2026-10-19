"""The Chinese README keeps each paper's published title next to its translation."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_readme import plain_text, render_papers


def paper(**changes):
    record = deepcopy(json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))[0])
    record.update(changes)
    return record


class ReadmeOriginalTitleTest(unittest.TestCase):
    def test_original_title_follows_the_translated_link_in_chinese_only(self):
        record = paper(id='paper-title-fixture', title='Fixture *title*: A_B [study]', title_zh='测试论文')
        before = deepcopy(record)
        zh = render_papers([record], 'zh')
        original = plain_text(record['title'])
        self.assertIn(f'- [**测试论文**]({record["url"]})\\\n  原题：*{original}*\n\n', zh)
        self.assertEqual(zh.count(original), 1)
        en = render_papers([record], 'en')
        self.assertNotIn('原题', en)
        self.assertEqual(en.count(original), 1)
        self.assertIn(f'- [**{original}**]({record["url"]})\n\n', en)
        self.assertEqual(record, before)

    def test_generated_chinese_readme_names_every_original_title_once(self):
        zh = (ROOT / 'README.zh-CN.md').read_text(encoding='utf-8')
        en = (ROOT / 'README.md').read_text(encoding='utf-8')
        self.assertNotIn('原题', en)
        for record in json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8')):
            with self.subTest(paper=record['id']):
                original = plain_text(record['title'])
                link = f'- [**{plain_text(record["title_zh"])}**]({record["url"]})'
                self.assertEqual(zh.count(original), 1)
                self.assertIn(f'{link}\\\n  原题：*{original}*\n', zh)


if __name__ == '__main__':
    unittest.main()
