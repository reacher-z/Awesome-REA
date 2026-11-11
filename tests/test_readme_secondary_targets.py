"""README metadata uses a data class and Protocol tag, or every target for non-data resources."""
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_readme import CASE_FILES, TARGETS, collection_section, entry_type, other_targets, render_catalog
from catalog import load_resources
from data_classes import DATA_CLASSES, FEATURED_DATA, FEATURED_LABEL
from validate_papers import read_papers


def resource(**changes):
    record = deepcopy(json.loads((ROOT / 'data/tool-resources.json').read_text(encoding='utf-8'))[0])
    record.update(id='targets-fixture', category='native-analysis', kind='tool', relationship='foundation',
                  targets=['binary'], url='https://example.com/tool')
    record.update(changes)
    return record


class ReadmeSecondaryTargetTest(unittest.TestCase):
    def test_non_data_sections_show_every_target_in_label_order(self):
        record = resource(targets=['firmware', 'binary', 'game'])
        self.assertEqual(collection_section(record), 'tools')
        self.assertEqual(other_targets(record, 'tools', 'en'), ' · Targets: Game, Binary, Firmware')
        self.assertEqual(other_targets(record, 'tools', 'zh'), ' · 目标：游戏、二进制、固件')
        for language in ('en', 'zh'):
            self.assertIn(f'<sub>{entry_type(record, language)}{other_targets(record, "tools", language)} · [',
                          render_catalog([record], language))

    def test_data_class_shows_protocol_tag_only(self):
        record = resource(kind='project', targets=['app', 'protocol'], **{'class': 'apps'})
        self.assertEqual(collection_section(record), 'apps')
        self.assertEqual(other_targets(record, 'apps', 'en'), ' · Protocol')
        self.assertEqual(other_targets(record, 'apps', 'zh'), ' · 协议')
        record['targets'] = ['app']
        self.assertEqual(other_targets(record, 'apps', 'en'), '')

    def test_generated_readmes_keep_record_placement_and_metadata(self):
        records = load_resources()
        paper_urls = {paper['url'] for paper in read_papers(ROOT)}
        for name, language in (('README.md', 'en'), ('README.zh-CN.md', 'zh')):
            text = (ROOT / name).read_text(encoding='utf-8') + '\n'.join(path.read_text(encoding='utf-8') for path in (ROOT / 'docs/cases').glob('*.md') if path.name.endswith('.zh-CN.md' if language == 'zh' else '.md') and (language == 'zh' or not path.name.endswith('.zh-CN.md')))
            lines = text.splitlines()
            for record in records:
                if record['url'] in paper_urls:
                    continue
                with self.subTest(readme=name, record=record['id']):
                    detail = f"/resources/{record['id']}/)</sub>"
                    line = next(line for line in lines if line.endswith(detail) and line.startswith('- '))
                    section = collection_section(record)
                    suffix = other_targets(record, section, language)
                    featured = FEATURED_LABEL[language == 'zh'] + ' · ' if record['id'] in FEATURED_DATA else ''
                    self.assertTrue(line.split(' <sub>', 1)[1].startswith(f'{featured}{entry_type(record, language)}{suffix} · ['), line)
                    if section in DATA_CLASSES:
                        self.assertEqual(bool(suffix), 'protocol' in record['targets'])
                    else:
                        for target, labels in TARGETS.items():
                            self.assertEqual(labels[language == 'zh'] in suffix, target in record['targets'])


if __name__ == '__main__':
    unittest.main()
