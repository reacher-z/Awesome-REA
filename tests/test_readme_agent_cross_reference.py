"""Agents and MCP points to the agent integrations that README sections file under a target."""
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_readme import collection_section, render_catalog
from catalog import load_resources
from validate_papers import read_papers


def resource(**changes):
    record = deepcopy(json.loads((ROOT / 'data/tool-resources.json').read_text(encoding='utf-8'))[0])
    record.update(kind='integration', category='agent-mcp', relationship='independent-agent-integration',
                  targets=['binary'])
    record.update(changes)
    return record


def agents_section(rendered):
    return rendered.split('<a id="agents-and-mcp"></a>', 1)[1].split('<a id="', 1)[0]


def is_agent_integration(record):
    return record['category'] == 'agent-mcp' or record['relationship'] == 'independent-agent-integration'


class AgentCrossReferenceTest(unittest.TestCase):
    def test_lists_agent_integrations_from_target_sections_by_entry_page(self):
        records = [
            resource(id='hub-mcp', name='Hub MCP', url='https://example.com/hub'),
            resource(id='chrome-devtools-mcp', name='Browser MCP', name_zh='浏览器 MCP', targets=['website'],
                     url='https://example.com/browser'),
            resource(id='web-agent', name='Web agent', category='web-analysis', targets=['website'],
                     url='https://example.com/web-agent'),
            resource(id='web-tool', name='Web tool', category='web-analysis', relationship='foundation',
                     kind='tool', targets=['website'], url='https://example.com/web-tool'),
        ]
        before = deepcopy(records)
        self.assertEqual([collection_section(record) for record in records],
                         ['agents-and-mcp', 'website', 'website', 'website'])
        en = render_catalog(records, 'en')
        self.assertIn('[↑ Contents](#contents)\n\n**Also in target sections:** [Website](#website): '
                      '[Browser MCP](https://awesomerea.org/resources/chrome-devtools-mcp/), '
                      '[Web agent](https://awesomerea.org/resources/web-agent/)\n\n- [**Hub MCP**]', en)
        zh = render_catalog(records, 'zh')
        self.assertIn('**其他分区中的智能体集成：** [网站](#website)：'
                      '[浏览器 MCP](https://awesomerea.org/zh/resources/chrome-devtools-mcp/)、'
                      '[Web agent](https://awesomerea.org/zh/resources/web-agent/)\n', zh)
        for rendered in (en, zh):
            self.assertNotIn('web-tool/', agents_section(rendered))
            for record in records:
                self.assertEqual(rendered.count(f']({record["url"]})'), 1)
        self.assertEqual(records, before)

    def test_no_line_when_every_agent_integration_is_in_agents_and_mcp(self):
        rendered = render_catalog([resource(id='hub-mcp', url='https://example.com/hub')], 'en')
        self.assertNotIn('Also in target sections', rendered)

    def test_generated_readmes_list_exactly_the_integrations_filed_elsewhere(self):
        paper_urls = {paper['url'] for paper in read_papers(ROOT)}
        listed = [record for record in load_resources() if record['url'] not in paper_urls]
        expected = {record['id'] for record in listed
                    if is_agent_integration(record) and collection_section(record) != 'agents-and-mcp'}
        self.assertTrue(expected)
        for name, prefix in (('README.md', ''), ('README.zh-CN.md', 'zh/')):
            with self.subTest(readme=name):
                text = (ROOT / name).read_text(encoding='utf-8')
                section = agents_section(text)
                line = next(line for line in section.splitlines() if line.startswith('**'))
                linked = re.findall(rf'\(https://awesomerea\.org/{prefix}resources/([a-z0-9-]+)/\)', line)
                self.assertEqual(Counter(linked), Counter(expected))
                entries = Counter(re.findall(r'^- \[\*\*.*?\*\*\]\((\S+?)\) - ', text, re.M))
                self.assertTrue(all(entries[record['url']] == 1 for record in listed))


if __name__ == '__main__':
    unittest.main()
