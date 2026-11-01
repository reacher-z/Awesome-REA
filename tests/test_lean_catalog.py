"""The homepage's first-render index is an exact projection of the complete catalog."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_site import CATALOG_INDEX_FIELDS, catalog_index
from validate_site import validate_catalog_index


class LeanCatalogTests(unittest.TestCase):
    def catalog(self):
        records = json.loads((ROOT / 'data/rea-resources.json').read_text(encoding='utf-8'))[:3]
        for record in records:
            # The build adds these from the group mapping and the translations file.
            record.update(group='cases', name_zh=record['name'] + '（中文）')
            record['additional_evidence_urls'] = ['https://example.org/evidence']
        return {'meta': {'repository_url': 'https://github.com/reacher-z/Awesome-REA', 'source_index': {'available': False, 'resource_count': 0}},
                'resources': records, 'topic_labels': {'reverse-engineering': {'en': 'Reverse engineering', 'zh': '逆向工程'}},
                'category_labels': {'reconstruction-cases': ['Reconstruction cases', '重建案例']}}

    def test_index_keeps_render_fields_and_drops_requirement_text(self):
        catalog = self.catalog()
        index = catalog_index(catalog)
        self.assertEqual(index['meta'], catalog['meta'])
        self.assertEqual(index['topic_labels'], catalog['topic_labels'])
        # The homepage category filter and cards read these labels on the first render.
        self.assertEqual(index['category_labels'], catalog['category_labels'])
        self.assertEqual([record['id'] for record in index['resources']], [record['id'] for record in catalog['resources']])
        for lean, full in zip(index['resources'], catalog['resources']):
            self.assertEqual(lean, {key: full[key] for key in CATALOG_INDEX_FIELDS if key in full})
            self.assertTrue({'id', 'name', 'name_zh', 'url', 'evidence_url', 'description_en', 'description_zh', 'kind',
                             'category', 'group', 'relationship', 'targets', 'verified_at'} <= set(lean))
            self.assertFalse({'requirements', 'requirements_zh', 'requirement_facets', 'additional_evidence_urls'} & set(lean))

    def test_validator_binds_the_built_index_to_the_catalog(self):
        catalog = self.catalog()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / 'catalog.json').write_text(json.dumps(catalog), encoding='utf-8')
            index = catalog_index(catalog)
            (output / 'catalog-index.json').write_text(json.dumps(index), encoding='utf-8')
            validate_catalog_index(output)
            stale = copy.deepcopy(index)
            stale['resources'][0]['description_en'] = 'Outdated description'
            reordered = copy.deepcopy(index)
            reordered['resources'].reverse()
            for changed in (stale, reordered, {**index, 'resources': index['resources'][:-1]}):
                (output / 'catalog-index.json').write_text(json.dumps(changed), encoding='utf-8')
                with self.assertRaises(AssertionError):
                    validate_catalog_index(output)

    def test_homepage_renders_first_from_the_index(self):
        result = subprocess.run(['node', str(ROOT / 'tests/lean_catalog_ui.cjs')], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
