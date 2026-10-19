"""README tags separate official from community REA entries, and a generated legend defines each tag shown."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_readme
from build_readme import BEGIN, entry_type, render_catalog, tag_legend
from catalog import load_resources
from validate_papers import read_papers


def resource(**changes):
    record = deepcopy(json.loads((ROOT / 'data/tool-resources.json').read_text(encoding='utf-8'))[0])
    record.update(id='tag-fixture', category='native-analysis', kind='tool', relationship='foundation',
                  targets=['binary'], url='https://example.com/tool')
    record.update(changes)
    return record


class ReadmeTagTest(unittest.TestCase):
    def test_official_and_community_rea_entries_are_distinguishable(self):
        official = resource(kind='integration', category='core', relationship='official-skill')
        community = resource(kind='integration', category='community-integrations', relationship='community-integration')
        learning = resource(kind='learning-resource', category='community-labs', relationship='community-learning-resource')
        self.assertEqual(entry_type(official, 'en'), 'Integration · Official REA')
        self.assertEqual(entry_type(community, 'en'), 'Integration · Community REA')
        self.assertEqual(entry_type(learning, 'en'), 'Learning resource · Community REA')
        self.assertEqual(entry_type(official, 'zh'), '集成 · REA 官方')
        self.assertEqual(entry_type(community, 'zh'), '集成 · REA 社区')

    def test_platform_follows_the_relationship_tag(self):
        self.assertEqual(entry_type(resource(category='android'), 'en'), 'Tool · Android')
        agent = resource(kind='integration', category='android', relationship='independent-agent-integration')
        self.assertEqual(entry_type(agent, 'en'), 'Integration · Independent agent · Android')

    def test_legend_defines_only_the_tags_shown_in_both_languages(self):
        records = [resource(), resource(id='lib', category='binary-libraries', url='https://example.com/lib'),
                   resource(id='skill', kind='integration', category='core', relationship='official-skill',
                            url='https://example.com/skill')]
        before = deepcopy(records)
        self.assertEqual(tag_legend(records, 'en'), '**Tags:** Official REA: published by the REA project · '
                         'Library: code library · type only: foundation tool or learning resource.')
        self.assertEqual(tag_legend(records, 'zh'), '**标签：** REA 官方：由 REA 项目发布 · 程序库：供编程调用的库 · '
                         '仅有类型：基础工具或学习资源。')
        self.assertTrue(render_catalog(records, 'en').startswith(tag_legend(records, 'en') + '\n\n'))
        self.assertEqual(records, before)
        with patch.object(build_readme, 'entry_type', return_value='Tool · Unexplained'):
            with self.assertRaisesRegex(ValueError, 'Undefined README tags'):
                tag_legend(records, 'en')

    def test_generated_readmes_define_every_rendered_tag_and_never_show_a_bare_rea_tag(self):
        records = load_resources()
        paper_urls = {paper['url'] for paper in read_papers(ROOT)}
        listed = [record for record in records if record['url'] not in paper_urls]
        for name, language in (('README.md', 'en'), ('README.zh-CN.md', 'zh')):
            with self.subTest(readme=name):
                text = (ROOT / name).read_text(encoding='utf-8')
                legend = text.split(BEGIN + '\n', 1)[1].split('\n', 1)[0]
                self.assertEqual(legend, tag_legend(listed, language))
                self.assertNotRegex(text, r'(?m)^  [^\n]* · REA · \[')
                tags = {tag for record in listed for tag in entry_type(record, language).split(' · ')[1:]}
                self.assertTrue(tags)
                for tag in tags:
                    self.assertIn(tag, legend)


if __name__ == '__main__':
    unittest.main()
