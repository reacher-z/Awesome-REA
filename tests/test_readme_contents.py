"""Keep README Contents counts tied to the sections the catalog actually renders."""
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_readme import (BADGES_BEGIN, BADGES_END, BEGIN, CONTENTS_BEGIN, CONTENTS_END, PAPERS_BEGIN, lead_sentence,
                         plain_text, render_badges, replace_badges, render_catalog, render_contents, render_papers)
from build_repository_index import SUMMARY_BEGIN


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
    def test_badges_keep_overlapping_resource_case_and_paper_counts_separate(self):
        listed = paper(url='https://example.com/paper')
        records = [resource(), resource(id='case', kind='case-study'),
                   resource(id='paper-copy', kind='research', url=listed['url'])]
        before = deepcopy((records, [listed]))
        en = render_badges(records, [listed], 'en')
        self.assertIn('/badge/resources-3-', en)
        self.assertIn('/badge/cases-1-', en)
        self.assertIn('/badge/papers-1-', en)
        self.assertIn('](LICENSE)', en)
        self.assertNotRegex(en.lower(), r'runtime|reproduced|verified|total-4')
        zh = render_badges(records, [listed], 'zh')
        for route in ('resources/', 'cases/', 'papers/'):
            self.assertIn('](https://awesomerea.org/zh/' + route + ')', zh)
        self.assertIn('精选资源: 3', zh)
        self.assertIn('案例: 1', zh)
        self.assertIn('论文: 1', zh)
        self.assertEqual((records, [listed]), before)

    def test_badges_have_no_ci_badge_and_the_footer_keeps_the_build_link(self):
        workflow = 'https://github.com/reacher-z/Awesome-REA/actions/workflows/validate.yml'
        for language, name, footer in (('en', 'README.md', 'Build status'), ('zh', 'README.zh-CN.md', '构建状态')):
            with self.subTest(language=language):
                rendered = render_badges([resource()], [paper()], language)
                self.assertNotIn('/actions/', rendered)
                self.assertNotIn('badge.svg', rendered)
                self.assertEqual(rendered.count('[!['), 5)
                text = (ROOT / name).read_text(encoding='utf-8')
                self.assertNotRegex(text, r'actions/workflows/[^)\s]*badge\.svg')
                self.assertIn(f'[{footer}]({workflow})', text.split(BADGES_END, 1)[1])

    def test_badge_generation_preserves_authored_header_and_rejects_ambiguous_markers(self):
        prefix = '<img src="featured.svg">\n# Collection\n<img src="banner.svg">\n'
        suffix = '\n**Primary navigation**\n'
        document = prefix + BADGES_BEGIN + '\nstale\n' + BADGES_END + suffix
        rendered = render_badges([resource()], [paper()], 'en')
        expected = prefix + BADGES_BEGIN + '\n' + rendered + BADGES_END + suffix
        self.assertEqual(replace_badges(document, rendered), expected)
        self.assertEqual(replace_badges(expected, rendered), expected)
        for invalid in ('', BADGES_BEGIN, BADGES_END + BADGES_BEGIN,
                        document + BADGES_BEGIN, document + BADGES_END):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                replace_badges(invalid, rendered)

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
        self.assertIn('[All cases](https://awesomerea.org/cases/) (1)', rendered)
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
        self.assertIn('https://awesomerea.org/zh/cases/', rendered)

    def test_resource_line_keeps_title_opening_sentence_tags_and_full_entry(self):
        record = resource(name='Fixture [tool]', name_zh='测试 [工具]',
                          description_en='Recovers a readable view of the interface, not the original backend. Requires A & B.',
                          description_zh='恢复已发布界面的可读视图，但并非原始后端实现。需要 A & B。')
        before = deepcopy(record)
        for language, title, description, label, prefix in [
            ('en', r'Fixture \[tool\]', 'Recovers a readable view of the interface, not the original backend.', 'Full entry', ''),
            ('zh', r'测试 \[工具\]', '恢复已发布界面的可读视图，但并非原始后端实现。', '完整条目', 'zh/'),
        ]:
            with self.subTest(language=language):
                rendered = render_catalog([record], language)
                tag = '工具' if language == 'zh' else 'Tool'
                line = (f'- [**{title}**]({record["url"]}) - {description} '
                        f'<sub>{tag} · [{label}](https://awesomerea.org/{prefix}resources/{record["id"]}/)</sub>')
                self.assertEqual(rendered.splitlines().count(line), 1, rendered)
                # The remaining sentences, like requirements and evidence, stay on the entry page.
                self.assertNotIn('A &amp; B', rendered)
        self.assertEqual(record, before)

    def test_paper_line_keeps_source_publication_and_full_entry(self):
        record = paper(id='paper-readme-fixture', targets=['website'], code_url='https://example.com/code')
        before = deepcopy(record)
        for language, label, prefix in [('en', 'Full entry', ''), ('zh', '完整条目', 'zh/')]:
            with self.subTest(language=language):
                rendered = render_papers([record], language)
                line = next(line for line in rendered.splitlines() if line.startswith('- [**'))
                description = plain_text(lead_sentence(record[f'description_{language}'], language))
                self.assertIn(f']({record["url"]}) - {description} <sub>', line)
                self.assertIn(f'[PDF]({record["pdf_url"]})', line)
                self.assertIn('](https://example.com/code)', line)
                self.assertTrue(line.endswith(f' · [{label}](https://awesomerea.org/{prefix}papers/paper-readme-fixture/)</sub>'), line)
                self.assertIn(str(record['year']), line)
                self.assertIn(plain_text(record['venue']), line)
                self.assertIn(plain_text(record['authors'][0]), line)
                # Scope and limitations are on the paper's entry page, not in the README.
                self.assertNotIn(plain_text(record[f'scope_limitations_{language}']), rendered)
                self.assertNotIn('<details>', rendered)
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

    def test_each_generated_block_names_its_generator_and_existing_sources(self):
        blocks = ((BADGES_BEGIN, 'build_readme.py'), (CONTENTS_BEGIN, 'build_readme.py'), (BEGIN, 'build_readme.py'),
                  (PAPERS_BEGIN, 'build_readme.py'), (SUMMARY_BEGIN, 'build_repository_index.py'))
        for name in ('README.md', 'README.zh-CN.md'):
            text = (ROOT / name).read_text(encoding='utf-8')
            for marker, script in blocks:
                with self.subTest(readme=name, marker=marker):
                    note = text.split(marker + '\n', 1)[1].split('\n', 1)[0]
                    self.assertRegex(note, rf'^<!-- Generated by scripts/{re.escape(script)} from \S.* '
                                           r'do not edit this block by hand\. -->$')
                    sources = re.findall(r'(?:data|site)/[\w.-]+(?:\.json|/)', note)
                    self.assertTrue(sources)
                    for source in sources:
                        self.assertTrue((ROOT / source).exists(), source)
        zh = (ROOT / 'README.zh-CN.md').read_text(encoding='utf-8').split(BEGIN + '\n', 1)[1]
        self.assertIn('site/translations.zh-CN.json', zh.split('\n', 1)[0])


if __name__ == '__main__':
    unittest.main()
