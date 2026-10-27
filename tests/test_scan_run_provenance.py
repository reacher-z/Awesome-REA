"""Each new scan run names its scanner files and the seed inputs it read, by repository path and digest only."""
import base64
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from review_pr import private_json_locations
import scan_sources as scanner
from scan_graphql_transport import GraphQLReadmeTransport
from scheduled_source_scan import RUN_SCHEMA, validate_shape
from validate import validate_run_provenance

QUERY = 'topic:reverse-engineering is:public fork:false archived:false'
BODY = b'# Example\n\n## Usage\nInspect a firmware image.\n'
OID = hashlib.sha1(b'blob ' + str(len(BODY)).encode() + b'\0' + BODY).hexdigest()


def repository(number):
    return {'id': number, 'full_name': f'example/tool-{number}', 'html_url': f'https://github.com/example/tool-{number}',
            'private': False, 'visibility': 'public', 'archived': False, 'fork': False,
            'description': f'Firmware analysis tool {number}', 'topics': ['firmware-analysis'],
            'stargazers_count': number, 'default_branch': 'main', '_metadata_observed_at': '2026-10-19T00:00:00Z'}


class API:
    def json(self, path, search=False):
        if search:
            return {'items': [repository(1), repository(2)], 'total_count': 2, 'incomplete_results': False}
        if path.startswith('/repos/') and '/readme' not in path:
            raise scanner.ScanError('http-404', 404)  # Seed lookups find nothing.
        if path.startswith('/repositories/'):
            return repository(int(path.rsplit('/', 1)[1]))
        number = int(path.split('/')[3].split('?')[0].rsplit('-', 1)[1])
        return {'type': 'file', 'path': 'README.md', 'sha': OID, 'size': len(BODY),
                'html_url': repository(number)['html_url'] + '/blob/main/README.md',
                'encoding': 'base64', 'content': base64.b64encode(BODY).decode()}


class Wrapper:
    """A scheduled-style wrapper whose inner GraphQL reader is never called."""
    batch_size = 2

    def __init__(self):
        self.transport = GraphQLReadmeTransport('offline-test-token', batch_size=2, interval=1.0)

    def fetch_batch(self, repositories):
        return {r['id']: {'status': 'ok', 'repository': repository(r['id']), 'content': BODY,
                          'metadata': {'path': 'README.md', 'sha': OID, 'size': len(BODY), 'commit_oid': 'a' * 40,
                                       'html_url': repository(r['id'])['html_url'] + '/blob/' + 'a' * 40 + '/README.md'}}
                for r in repositories}


def digest(relative, root=ROOT):
    content = (root / relative).read_bytes()
    return {'path': relative, 'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}


class ScanRunProvenanceTests(unittest.TestCase):
    def scan(self, directory, *, target=1, resumed=None, seed_curated=False, seed_papers=False, **options):
        args = SimpleNamespace(target=target, workers=1, requests_per_second=1, max_pages=1, candidate_buffer=0,
                               seed_curated=seed_curated, seed_papers=seed_papers, queries=[QUERY],
                               output=Path(directory) / f'scan-{target}.json')
        raw = json.dumps(resumed).encode() if resumed else None
        with contextlib.redirect_stdout(io.StringIO()):
            scanner.run_scan(API(), args, resumed, hashlib.sha256(raw).hexdigest() if raw else None, **options)
        return args.output.read_text(encoding='utf-8')

    def provenance_errors(self, document):
        errors = []
        validate_run_provenance(document['meta'], errors)
        return errors

    def test_rest_run_names_its_scanner_files_and_no_seed_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            text = self.scan(directory)
        document = json.loads(text)
        provenance = document['meta']['current_run']['scanner_provenance']
        self.assertEqual(provenance, {'policy': scanner.RUN_PROVENANCE_POLICY, 'seed_inputs': [],
                                      'implementation': [digest(path) for path in (
                                          'scripts/scan_sources.py', 'scripts/source_descriptions.py', 'scripts/source_scope.py',
                                          'scripts/strict_json.py')]})
        self.assertNotIn(str(ROOT), text)
        self.assertEqual(private_json_locations(document), [])
        self.assertEqual(self.provenance_errors(document), [])
        validate_shape(document['meta']['current_run'], RUN_SCHEMA)

    def test_graphql_run_also_names_the_wrapper_and_wrapped_reader_modules(self):
        with tempfile.TemporaryDirectory() as directory:
            document = json.loads(self.scan(directory, target=2, readme_transport=Wrapper()))
        paths = [row['path'] for row in document['meta']['current_run']['scanner_provenance']['implementation']]
        self.assertIn('scripts/scan_graphql_transport.py', paths)
        self.assertIn('tests/test_scan_run_provenance.py', paths)
        self.assertEqual(paths, sorted(paths))

    def test_only_enabled_seed_inputs_are_recorded_from_the_bytes_parsed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'data').mkdir()
            (root / 'data/rea-resources.json').write_text('[{"id": "a", "url": "https://github.com/example/a"}]')
            (root / 'data/tool-resources.json').write_text('[]')
            (root / 'data/papers.json').write_text('[{"id": "p", "code_url": "https://github.com/example/p"}]')
            for references in (scanner.curated_references, scanner.paper_references):
                references.cache_clear()
                self.addCleanup(references.cache_clear)
            with patch.object(scanner, 'ROOT', root), patch.dict(scanner.SEED_INPUT_DIGESTS, clear=True):
                curated = json.loads(self.scan(directory, seed_curated=True))
                expected = [digest(path, root) for path in scanner.CURATED_SEED_FILES]
                # The cached references keep their parsed bytes, so a later edit is not misattributed.
                (root / 'data/rea-resources.json').write_text('[]')
                both = json.loads(self.scan(directory, target=2, seed_curated=True, seed_papers=True))
                papers = digest('data/papers.json', root)
        self.assertEqual(curated['meta']['current_run']['scanner_provenance']['seed_inputs'], expected)
        self.assertEqual(both['meta']['current_run']['scanner_provenance']['seed_inputs'], expected + [papers])
        # The temporary root holds no scanner scripts, so only the seed rule applies here.
        self.assertNotIn('Source index current_run scanner_provenance lists a seed input the run did not enable.',
                         self.provenance_errors(both))

    def test_resume_keeps_legacy_records_and_run_metadata_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            legacy = json.loads(self.scan(directory))
            del legacy['meta']['current_run']['scanner_provenance']  # A run recorded before this field existed.
            prior = copy.deepcopy(legacy)
            document = json.loads(self.scan(directory, target=2, resumed=legacy))
        self.assertEqual(document['resources'][:1], prior['resources'])
        self.assertEqual(document['meta']['resume_history'][-1]['run'], prior['meta']['current_run'])
        self.assertNotIn('scanner_provenance', document['meta']['resume_history'][-1]['run'])
        self.assertIn('scanner_provenance', document['meta']['current_run'])
        self.assertEqual(self.provenance_errors(document), [])

    def test_validation_rejects_local_paths_unknown_fields_and_unused_seeds(self):
        with tempfile.TemporaryDirectory() as directory:
            document = json.loads(self.scan(directory))
        run = document['meta']['current_run']
        cases = [
            lambda provenance: provenance['implementation'][0].update(path=str(ROOT / 'scripts/scan_sources.py')),
            lambda provenance: provenance['implementation'].pop(0),
            lambda provenance: provenance.update(environment={'PATH': '/usr/bin'}),
            lambda provenance: provenance['seed_inputs'].append(digest('data/papers.json')),
            lambda provenance: provenance['seed_inputs'].append({**digest('data/papers.json'), 'path': '../papers.json'}),
            lambda provenance: provenance['implementation'][0].update(sha256='not-a-digest'),
        ]
        for change in cases:
            with self.subTest(change=change):
                broken = copy.deepcopy(document)
                change(broken['meta']['current_run']['scanner_provenance'])
                self.assertEqual(len(self.provenance_errors(broken)), 1)
        del run['scanner_provenance']
        self.assertEqual(self.provenance_errors(document), [])


if __name__ == '__main__':
    unittest.main()
