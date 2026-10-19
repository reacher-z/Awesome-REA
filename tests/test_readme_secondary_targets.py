"""README metadata lines name the targets that an entry's section heading does not already imply."""
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_readme import TARGETS, collection_section, entry_type, other_targets, render_catalog
from catalog import load_resources
from validate_papers import read_papers


def resource(**changes):
    record = deepcopy(json.loads((ROOT / 'data/tool-resources.json').read_text(encoding='utf-8'))[0])
    record.update(id='targets-fixture', category='native-analysis', kind='tool', relationship='foundation',
                  targets=['binary'], url='https://example.com/tool')
    record.update(changes)
    return record


class ReadmeSecondaryTargetTest(unittest.TestCase):
    def test_target_sections_show_only_other_targets_in_label_order(self):
        record = resource(targets=['firmware', 'binary', 'game'])
        before = deepcopy(record)
        self.assertEqual(collection_section(record), 'native-binary')
        self.assertEqual(other_targets(record, 'native-binary', 'en'), ' · Also: Game, Firmware')
        self.assertEqual(other_targets(record, 'native-binary', 'zh'), ' · 也适用：游戏、固件')
        for language in ('en', 'zh'):
            rendered = render_catalog([record], language)
            self.assertIn(f'  {entry_type(record, language)}{other_targets(record, "native-binary", language)} · [', rendered)
        self.assertEqual(record, before)

    def test_single_target_in_its_own_section_adds_nothing(self):
        for record, section in ((resource(), 'native-binary'),
                                (resource(category='web-analysis', targets=['website']), 'website'),
                                (resource(category='firmware', targets=['firmware']), 'firmware')):
            with self.subTest(section=section):
                self.assertEqual(collection_section(record), section)
                self.assertEqual(other_targets(record, section, 'en'), '')
                self.assertEqual(other_targets(record, section, 'zh'), '')
                self.assertIn(f'  {entry_type(record, "en")} · [Requirements & evidence]', render_catalog([record], 'en'))

    def test_sections_without_a_target_list_every_target(self):
        record = resource(category='agent-mcp', kind='integration', relationship='independent-agent-integration',
                          targets=['app', 'website'])
        self.assertEqual(collection_section(record), 'agents-and-mcp')
        self.assertEqual(other_targets(record, 'agents-and-mcp', 'en'), ' · Targets: Website, App')
        self.assertEqual(other_targets(record, 'agents-and-mcp', 'zh'), ' · 目标：网站、应用')

    def test_generated_readmes_mark_every_outside_target_once(self):
        records = load_resources()
        paper_urls = {paper['url'] for paper in read_papers(ROOT)}
        for name, language in (('README.md', 'en'), ('README.zh-CN.md', 'zh')):
            text = (ROOT / name).read_text(encoding='utf-8')
            entries = Counter(re.findall(r'^- \[\*\*.*?\*\*\]\((\S+?)\)$', text, re.M))
            for record in records:
                if record['url'] in paper_urls:
                    continue
                with self.subTest(readme=name, record=record['id']):
                    self.assertEqual(entries[record['url']], 1)
                    section = collection_section(record)
                    suffix = other_targets(record, section, language)
                    detail = f"/resources/{record['id']}/)"
                    line = next(line for line in text.splitlines() if line.endswith(detail) and line.startswith('  '))
                    self.assertTrue(line.startswith(f'  {entry_type(record, language)}{suffix} · ['), line)
                    implied = {'native-binary': 'binary'}.get(section, section)
                    for target, labels in TARGETS.items():
                        shown = labels[language == 'zh'] in suffix
                        self.assertEqual(shown, target in record['targets'] and target != implied, target)


if __name__ == '__main__':
    unittest.main()
