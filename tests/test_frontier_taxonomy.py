"""FrontierCUA pilot: hierarchy integrity, Class 0 coverage and field references."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))


class FrontierTaxonomyTests(unittest.TestCase):
    def setUp(self):
        self.taxonomy = json.loads((ROOT / 'data' / 'frontier-taxonomy.json').read_text(encoding='utf-8'))
        self.mapping = json.loads((ROOT / 'data' / 'frontier-taxonomy-map.json').read_text(encoding='utf-8'))
        self.classes = json.loads((ROOT / 'data' / 'evidence-classes.json').read_text(encoding='utf-8'))

    def test_hierarchy_has_fifteen_realms_and_one_hundred_twenty_fields(self):
        nodes = self.taxonomy['nodes']
        self.assertEqual(len(nodes), 135)
        ids = [node['id'] for node in nodes]
        self.assertEqual(len(ids), len(set(ids)))
        realms = [node for node in nodes if node['level'] == 1]
        fields = [node for node in nodes if node['level'] == 2]
        self.assertEqual(len(realms), 15)
        self.assertEqual(len(fields), 120)
        for node in nodes:
            if node['level'] == 2:
                self.assertIn(node['parent'], {realm['id'] for realm in realms})

    def test_pilot_covers_every_class_zero_record_exactly_once(self):
        class_zero = {entry['id'] for entry in self.classes['entries'] if entry['evidence_class'] == 0}
        mapped = [entry['id'] for entry in self.mapping['entries']]
        self.assertEqual(set(mapped), class_zero)
        self.assertEqual(len(mapped), len(set(mapped)))

    def test_every_field_exists_and_is_a_second_level_node(self):
        fields = {node['id']: node for node in self.taxonomy['nodes'] if node['level'] == 2}
        for entry in self.mapping['entries']:
            self.assertIn(entry['field'], fields, entry['id'])
            self.assertEqual(entry['field_name'], fields[entry['field']]['name'], entry['id'])
            self.assertTrue(entry['reason'].strip(), entry['id'])
            self.assertTrue(entry['source'].startswith('https://github.com/ruoxining/rea-tracker/'), entry['id'])

    def test_mapping_is_pinned_and_scoped(self):
        self.assertEqual(self.mapping['scope'], 'Class 0 records in data/evidence-classes.json')
        self.assertTrue(self.mapping['source'].startswith('https://github.com/ruoxining/rea-tracker/'))
        self.assertEqual(self.mapping['taxonomy'], 'frontier-taxonomy.json')
        self.assertEqual(self.taxonomy['meta']['version'], '1.1')


if __name__ == '__main__':
    unittest.main()
