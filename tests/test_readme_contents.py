"""Keep README Contents counts tied to the sections the catalog actually renders."""
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_readme import CONTENTS_BEGIN, CONTENTS_END, plain_text, render_catalog, render_contents, render_papers


def resource(**changes):
    record = deepcopy(json.loads((ROOT / 'data/tool-resources.json').read_text(encoding='utf-8'))[0])
    record.update(id='contents-fixture', category='web-analysis', kind='tool',
                  relationship='foundation', targets=['website'], url='https://example.com/tool')
    record.update(changes)
    return record


def paper(**changes):
    record = deepcopy(json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))[0])
    record.update(changes)
    return record


class ReadmeContentsTest(unittest.TestCase):
    def test_counts_follow_rendered_sections(self):
        listed = paper(url='https://example.com/paper')
        records = [
            resource(),
            resource(id='second-web-tool', url='https://example.com/second'),
            resource(id='case', kind='case-study', category='reconstruction-cases',
                     relationship='independent-reconstruction', targets=['game'], url='https://example.com/case'),
            resource(id='paper-copy', kind='research', category='learning', relationship='learning',
                     url=listed['url']),
        ]
        rendered = render_contents(records, [listed], 2864, 'en')
        self.assertIn('[Website](#website) (2)', rendered)
        self.assertIn('[Game](#game) (1)', rendered)
        self.assertIn('[Papers](#papers) (1)', rendered)
        self.assertIn('kind=case-study) (1)', rendered)
        self.assertIn('[Full Repository Index](#full-repository-index) (2,864)', rendered)
        # A research record listed under Papers is not rendered in Learning, so it is not counted there.
        self.assertNotIn('#references-and-learning', rendered)
        self.assertNotIn('#references-and-learning', render_catalog(records, 'en', {listed['url']}))
        # Sections without entries have no anchor, so Contents must not link to them.
        self.assertNotIn('#protocol', rendered)

    def test_chinese_contents_use_chinese_labels_and_anchors(self):
        rendered = render_contents([resource()], [paper()], 10, 'zh')
        self.assertTrue(rendered.startswith('**按目标找工具与案例**\n\n- [网站](#website) (1)'))
        self.assertIn('[完整仓库索引](#完整仓库索引) (10)', rendered)
        self.assertIn('https://awesomerea.org/zh/?view=curated&kind=case-study', rendered)

    def test_resource_title_and_full_caveat_keep_separate_bilingual_paragraphs(self):
        record = resource(name='Fixture [tool]', name_zh='测试 [工具]',
                          description_en='Recovers a view, not the original backend. Requires A & B.',
                          description_zh='恢复界面，并非原后端。需要 A & B。')
        before = deepcopy(record)
        for language, title, description, label, prefix in [
            ('en', r'Fixture \[tool\]', 'Recovers a view, not the original backend. Requires A &amp; B.',
             'Requirements & evidence', ''),
            ('zh', r'测试 \[工具\]', '恢复界面，并非原后端。需要 A &amp; B。', '使用条件与证据', 'zh/'),
        ]:
            with self.subTest(language=language):
                rendered = render_catalog([record], language)
                self.assertEqual(rendered.count(f'- [**{title}**]({record["url"]})'), 1)
                self.assertEqual(rendered.count('\n\n  ' + description + '\n'), 1)
                self.assertIn(f'[{label}](https://awesomerea.org/{prefix}resources/{record["id"]}/)', rendered)
                self.assertNotIn('<sub>', rendered)
        self.assertEqual(record, before)

    def test_paper_source_scope_and_publication_survive_detail_navigation(self):
        record = paper(id='paper-readme-fixture', targets=['website'], code_url='https://example.com/code')
        before = deepcopy(record)
        for language, label, prefix in [('en', 'Full entry & citation', ''), ('zh', '完整条目与引用', 'zh/')]:
            with self.subTest(language=language):
                rendered = render_papers([record], language)
                self.assertIn(f']({record["url"]})', rendered)
                self.assertIn(f'[PDF]({record["pdf_url"]})', rendered)
                self.assertIn('](https://example.com/code)', rendered)
                self.assertIn(f'[{label}](https://awesomerea.org/{prefix}papers/paper-readme-fixture/)', rendered)
                self.assertIn(plain_text(record[f'description_{language}']), rendered)
                self.assertIn(plain_text(record[f'scope_limitations_{language}']), rendered)
                self.assertIn(str(record['year']), rendered)
                self.assertIn(plain_text(record['venue']), rendered)
        self.assertEqual(record, before)


    def test_contents_labels_match_the_headings_they_link(self):
        for name, language in (('README.md', 'en'), ('README.zh-CN.md', 'zh')):
            text = (ROOT / name).read_text(encoding='utf-8')
            contents = text.split(CONTENTS_BEGIN, 1)[1].split(CONTENTS_END, 1)[0]
            links = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', contents)
            self.assertGreater(len(links), 8)
            for label, anchor in links:
                with self.subTest(readme=name, anchor=anchor):
                    explicit = re.search(rf'<a id="{re.escape(anchor)}"></a>\n#+ (.+)', text)
                    headings = re.findall(r'^#+ (.+)$', text, re.MULTILINE)
                    heading = explicit[1] if explicit else next(h for h in headings if h.lower().replace(' ', '-') == anchor)
                    # Chinese catalog headings keep the English section name before " · ".
                    self.assertEqual(heading.split(' · ')[-1] if language == 'zh' else heading, label)


if __name__ == '__main__':
    unittest.main()
