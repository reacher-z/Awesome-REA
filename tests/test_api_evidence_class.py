"""The v1 API and each entry's record.json carry the catalog's evidence class and demo preview."""
import csv
import io
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from agent_formats import resource_record
from build_api import build_api
from json_schema_check import errors
from test_agent_formats import RESOURCE

ORIGIN = 'https://awesomerea.org'


class ApiEvidenceClassUnitTest(unittest.TestCase):
    def test_record_carries_class_scope_and_absolute_preview_url(self):
        record = {**RESOURCE, 'evidence_class': 1, 'evidence_status': 'observed', 'scope': 'analysis',
                  'runtime_status': 'not-run', 'preview': '/previews/ghidra.png', 'preview_kind': 'image'}
        value = resource_record(record, ORIGIN)
        self.assertEqual((value['evidence_class'], value['evidence_status'], value['scope']), (1, 'observed', 'analysis'))
        self.assertEqual((value['preview_url'], value['preview_kind']), (f'{ORIGIN}/previews/ghidra.png', 'image'))
        self.assertNotIn('preview', value)
        self.assertNotIn('runtime_status', value)

    def test_unknown_class_follows_the_schema_and_bad_classes_do_not(self):
        known = {**RESOURCE, 'evidence_class': 2, 'evidence_status': 'observed', 'scope': 'unknown'}
        unknown = {**RESOURCE, 'id': 'unreadable', 'evidence_class': None, 'evidence_status': 'unknown', 'scope': 'unknown'}
        with TemporaryDirectory() as tmp:
            build_api(Path(tmp), resources=[known, unknown], papers=[])
            folder = Path(tmp) / 'api/v1'
            schema = json.loads((folder / 'schema.json').read_text(encoding='utf-8'))
            document = json.loads((folder / 'resources.json').read_text(encoding='utf-8'))
            rows = list(csv.DictReader(io.StringIO((folder / 'resources.csv').read_text(encoding='utf-8'))))
        self.assertEqual(errors(document, schema['$defs']['resourcesFile'], schema), [])
        self.assertEqual([row['evidence_class'] for row in document['resources']], [2, None])
        self.assertEqual([row['evidence_class'] for row in rows], ['2', ''])
        document['resources'][0]['evidence_class'] = 4
        self.assertTrue(errors(document, schema['$defs']['resourcesFile'], schema))


class ApiMatchesCatalogTest(unittest.TestCase):
    def test_api_and_record_json_agree_with_catalog_on_class_and_preview(self):
        from shared_build import built_site
        site = built_site()
        catalog = {row['id']: row for row in json.loads((site / 'catalog.json').read_text(encoding='utf-8'))['resources']}
        api = {row['id']: row for row in json.loads((site / 'api/v1/resources.json').read_text(encoding='utf-8'))['resources']}
        self.assertEqual(api.keys(), catalog.keys())
        for identifier, row in catalog.items():
            self.assertEqual(api[identifier].get('evidence_class'), row.get('evidence_class'), identifier)
            self.assertEqual(api[identifier].get('evidence_status'), row.get('evidence_status'), identifier)
            preview = f'{ORIGIN}{row["preview"]}' if row.get('preview') else None
            self.assertEqual(api[identifier].get('preview_url'), preview, identifier)
        self.assertTrue(any(row.get('evidence_class') is not None for row in api.values()))
        sample = next(identifier for identifier, row in catalog.items() if row.get('evidence_class') is not None)
        record = json.loads((site / f'resources/{sample}/record.json').read_text(encoding='utf-8'))
        record = record.get('record', record)
        self.assertEqual(record.get('evidence_class'), catalog[sample]['evidence_class'])


if __name__ == '__main__':
    unittest.main()
