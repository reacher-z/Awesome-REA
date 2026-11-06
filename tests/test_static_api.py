"""The static API: files, schema conformance, deterministic dates, CSV twins, change window and candidates."""
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import build_api
from build_api import API_VERSION, CSV_COLUMNS, ENDPOINTS, build_api as build, snapshot_time
from json_schema_check import errors
from test_agent_formats import PAPER, RESOURCE

ORIGIN = 'https://awesomerea.org'
OLD = {**RESOURCE, 'id': 'old-tool', 'name': 'Old tool', 'added_at': '2026-08-01', 'verified_at': '2026-08-01'}
REVIEWED = {**RESOURCE, 'id': 'reviewed-tool', 'name': 'Reviewed tool', 'added_at': '2026-10-16', 'verified_at': '2026-11-02T08:00:00Z'}
REPOSITORIES = {'meta': {'kind': 'published-repository-selection', 'published_at': '2026-10-20T10:49:31Z'},
                'resources': [{'id': 'scan-1', 'scan_status': 'readme-scanned', 'category': 'firmware'},
                              {'id': 'scan-2', 'scan_status': 'readme-scanned', 'category': 'firmware', 'scope_status': 'excluded'}]}
DISCOVERY = {'id': 'scan-9', 'full_name': 'owner/tool', 'url': 'https://github.com/owner/tool', 'description_en': 'A tool.',
             'topics': ['re'], 'targets': ['binary'], 'category': 'native-analysis', 'stars': 3, 'license': 'MIT',
             'pushed_at': '2026-11-01T00:00:00Z', 'observed_at': '2026-11-05T22:00:00Z', 'batch_id': 'run-1-1',
             'ingested_at': '2026-11-05T22:36:35Z'}
QUEUE = {'listed': [DISCOVERY], 'batches': [{'batch_id': 'run-1-1', 'ingested_at': '2026-11-05T22:36:35Z', 'resources': [DISCOVERY]}]}
LEAD = {'id': 'lead-1', 'url': 'http://example.org/tool', 'name': 'tool', 'kind_hint': 'tool', 'listings': [],
        'observed_at': '2026-11-05T22:37:27Z', 'verification': 'automated-source-lead', 'review_status': 'unreviewed',
        'github': None, 'batch_id': 'leads-1-1', 'collected_at': '2026-11-05T22:37:27Z'}
LEADS = {'listed': [LEAD], 'batches': [{'batch_id': 'leads-1-1', 'collected_at': '2026-11-05T22:37:27Z', 'leads': [LEAD]}]}


class StaticApiTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.output = Path(self.temporary.name)
        self.resources = [RESOURCE, OLD, REVIEWED]
        self.papers = [PAPER]
        self.index = build(self.output, resources=self.resources, papers=self.papers, repository_document=REPOSITORIES,
                           discovery_queue=QUEUE, lead_queue=LEADS)
        self.folder = self.output / 'api/v1'
        self.schema = json.loads((self.folder / 'schema.json').read_text())

    def load(self, name):
        return json.loads((self.folder / f'{name}.json').read_text())

    def test_every_file_follows_its_schema_definition_and_carries_version_and_time(self):
        for name in (*ENDPOINTS, 'index'):
            document = self.load(name)
            self.assertEqual(document['version'], API_VERSION)
            self.assertEqual(document['generated_at'], '2026-11-05T22:37:27Z')
            definition = document['schema'].split('#/$defs/')[1]
            self.assertEqual(errors(document, self.schema['$defs'][definition], self.schema), [], name)
        self.assertEqual(self.schema['$id'], ORIGIN + '/api/v1/schema.json')
        self.assertEqual(self.schema['$schema'], 'https://json-schema.org/draft/2020-12/schema')

    def test_generated_at_is_the_newest_data_time_not_the_build_time(self):
        self.assertEqual(snapshot_time(self.resources, self.papers, REPOSITORIES, QUEUE, LEADS), '2026-11-05T22:37:27Z')
        self.assertEqual(snapshot_time([OLD], []), '2026-08-01T00:00:00Z')
        first = {path.name: path.read_bytes() for path in self.folder.iterdir()}
        with TemporaryDirectory() as again:
            build(Path(again), resources=self.resources, papers=self.papers, repository_document=REPOSITORIES,
                  discovery_queue=QUEUE, lead_queue=LEADS)
            self.assertEqual({path.name: path.read_bytes() for path in (Path(again) / 'api/v1').iterdir()}, first)

    def test_records_categories_candidates_and_changes(self):
        resources = self.load('resources')
        self.assertEqual([row['id'] for row in resources['resources']], ['ghidra', 'old-tool', 'reviewed-tool'])
        self.assertNotIn('private_note', resources['resources'][0])
        self.assertEqual(self.load('papers')['papers'][0]['authors'], [])
        categories = self.load('categories')
        self.assertEqual(categories['curated']['categories'], [{'id': 'native-analysis', 'label': 'Native analysis tools',
                                                                'label_zh': '原生分析工具', 'count': 3}])
        firmware = next(item for item in categories['repositories']['categories'] if item['id'] == 'firmware')
        self.assertEqual(firmware['count'], 1)  # the scope-excluded record is not browsable
        candidates = self.load('candidates')['candidates']
        # Newest first across both queues: the lead batch was collected after the discovery batch.
        self.assertEqual([(row['candidate_type'], row['review_status']) for row in candidates],
                         [('followed-source-lead', 'unreviewed'), ('repository-discovery', 'unreviewed')])
        changes = self.load('changes')
        self.assertEqual(changes['window_start'], '2026-10-06T22:37:27Z')
        listed = [(row['change'], row['id']) for row in changes['changes']]
        self.assertIn(('added', 'ghidra'), listed)
        self.assertIn(('reviewed', 'reviewed-tool'), listed)
        self.assertNotIn(('added', 'old-tool'), listed)
        self.assertNotIn(('reviewed', 'ghidra'), listed)  # reviewed before it was added
        self.assertEqual(listed[0], ('leads-collected', 'leads-1-1'))
        self.assertEqual(changes['count'], len(listed))

    def test_csv_twins_repeat_version_and_time_and_match_the_json(self):
        for name in ENDPOINTS:
            rows = list(csv.reader(io.StringIO((self.folder / f'{name}.csv').read_text(encoding='utf-8'), newline='')))
            self.assertEqual(rows[0], [*CSV_COLUMNS[name], 'version', 'generated_at'])
            self.assertTrue(all(row[-2:] == [API_VERSION, '2026-11-05T22:37:27Z'] for row in rows[1:]))
        resources = list(csv.DictReader(io.StringIO((self.folder / 'resources.csv').read_text(encoding='utf-8'), newline='')))
        self.assertEqual(resources[0]['targets'], 'binary | firmware')
        self.assertEqual(resources[0]['requirements'], 'A JDK. | Release package.')
        self.assertTrue((self.folder / 'resources.csv').read_bytes().endswith(b'\r\n'))
        scopes = {row['scope'] for row in csv.DictReader(io.StringIO((self.folder / 'categories.csv').read_text(encoding='utf-8'), newline=''))}
        self.assertEqual(scopes, {'curated-category', 'curated-section', 'curated-kind', 'curated-target', 'curated-relationship',
                                  'repository-category'})

    def test_index_lists_every_file_with_its_checksum(self):
        paths = {entry['path'] for entry in self.index['files']}
        self.assertEqual(paths, {'/api/v1/schema.json', *(f'/api/v1/{name}.{suffix}' for name in ENDPOINTS for suffix in ('json', 'csv'))})
        for entry in self.index['files']:
            raw = (self.output / entry['path'].lstrip('/')).read_bytes()
            self.assertEqual((entry['bytes'], entry['sha256']), (len(raw), hashlib.sha256(raw).hexdigest()))

    def test_schema_rejects_values_outside_the_vocabulary(self):
        document = self.load('resources')
        document['resources'][0]['kind'] = 'rating'
        problems = errors(document, self.schema['$defs']['resourcesFile'], self.schema)
        self.assertTrue(any('kind' in problem for problem in problems))
        document = self.load('papers')
        document['papers'][0]['runtime_tested'] = True
        self.assertTrue(errors(document, self.schema['$defs']['papersFile'], self.schema))

    def test_a_private_value_stops_the_build(self):
        with TemporaryDirectory() as directory, patch.object(build_api, 'private_json_locations', return_value=[('ghidra', 'url')]):
            with self.assertRaisesRegex(ValueError, 'privacy'):
                build(Path(directory), resources=self.resources, papers=self.papers)

    def test_docs_page_text_names_every_endpoint(self):
        title, description, content, markdown = build_api.api_page('en', self.index, ORIGIN)
        self.assertEqual(title, 'Static JSON and CSV API')
        for name in ENDPOINTS:
            self.assertIn(f'/api/v1/{name}.json', content)
            self.assertIn(f'{ORIGIN}/api/v1/{name}.csv', markdown)
        self.assertTrue(markdown.startswith('# Static JSON and CSV API\n\n> '))
        title, description, content, markdown = build_api.api_page('zh', self.index, ORIGIN)
        self.assertEqual(title, '静态 JSON 与 CSV API')


class SchemaCheckTests(unittest.TestCase):
    def test_subset_keywords(self):
        schema = {'$defs': {'item': {'type': 'object', 'required': ['id'], 'properties': {'id': {'type': 'string', 'pattern': '^[a-z]+$'}},
                                     'additionalProperties': False}},
                  'type': 'array', 'minItems': 1, 'items': {'$ref': '#/$defs/item'}}
        self.assertEqual(errors([{'id': 'ok'}], schema), [])
        self.assertTrue(errors([], schema))
        self.assertTrue(errors([{'id': 'NO'}], schema))
        self.assertTrue(errors([{'id': 'ok', 'extra': 1}], schema))
        self.assertTrue(errors([{}], schema))
        self.assertEqual(errors(None, {'anyOf': [{'type': 'string'}, {'type': 'null'}]}), [])
        self.assertTrue(errors(3, {'anyOf': [{'type': 'string'}, {'type': 'null'}]}))
        self.assertTrue(errors(True, {'type': 'integer'}))
        self.assertTrue(errors({'k': 'x'}, {'type': 'object', 'propertyNames': {'enum': ['a']}}))


if __name__ == '__main__':
    unittest.main()
