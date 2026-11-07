"""Successful seed scans retain each provenance field's accepted vocabulary."""
import base64
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import scan_sources as scanner
from validate import validate_scan_discovery


class SeedAPI:
    """Offline GitHub metadata and README responses for one public repository."""
    def json(self, path, search=False):
        repository = {
            'id': 1, 'full_name': 'example/tool-1',
            'html_url': 'https://github.com/example/tool-1',
            'private': False, 'visibility': 'public', 'fork': False, 'archived': False,
            'description': 'Firmware analysis tool', 'topics': ['firmware-analysis'],
            'stargazers_count': 1, 'default_branch': 'main',
        }
        if not search and path in ('/repos/example/tool-1', '/repositories/1'):
            return repository
        if not search and path == '/repos/example/tool-1/readme?ref=main':
            body = b'# Example\n\n## Usage\nInspect a firmware image.\n'
            oid = hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()
            return {
                'type': 'file', 'path': 'README.md', 'sha': oid, 'size': len(body),
                'html_url': repository['html_url'] + '/blob/main/README.md',
                'encoding': 'base64', 'content': base64.b64encode(body).decode(),
            }
        raise AssertionError(f'Unexpected GitHub request: {path}')


class SeedDiscoveryRegressionTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        (self.root / 'data').mkdir()
        fixtures = {
            'rea-resources.json': [
                {'id': 'example-curated-tool', 'url': 'https://github.com/example/tool-1'}],
            'tool-resources.json': [],
            'papers.json': [
                {'id': 'paper-example', 'code_url': 'https://github.com/example/tool-1'}],
            'tracker-seeds.json': {
                'schema_version': 1, 'source': 'https://github.com/example/tracker',
                'reviewed_at': '2026-11-03',
                'repositories': [{'repo': 'example/tool-1',
                                  'reference_ids': ['tracker-example-tool']}],
            },
        }
        for name, document in fixtures.items():
            (self.root / 'data' / name).write_text(json.dumps(document), encoding='utf-8')
        for references in (scanner.curated_references, scanner.paper_references, scanner.tracker_references):
            references.cache_clear()
            self.addCleanup(references.cache_clear)
        self.enterContext(patch.object(scanner, 'ROOT', self.root))
        self.enterContext(patch.dict(scanner.SEED_INPUT_DIGESTS, clear=True))

    def scan(self, *, curated=False, papers=False, tracker=False):
        args = SimpleNamespace(
            target=1, workers=1, requests_per_second=1, max_pages=1, candidate_buffer=0,
            seed_curated=curated, seed_papers=papers, seed_tracker=tracker,
            queries=[], output=self.root / 'scan.json',
        )
        with contextlib.redirect_stdout(io.StringIO()):
            scanner.run_scan(SeedAPI(), args)
        document = json.loads(args.output.read_text(encoding='utf-8'))
        self.assertEqual(document['meta']['successful_readme_scans'], 1)
        self.assertEqual(document['failures'], [])
        self.assertEqual(len(document['resources']), 1)
        self.assertEqual(document['resources'][0]['scan_status'], 'readme-scanned')
        errors = []
        validate_scan_discovery(document['meta'], document['resources'], errors)
        self.assertEqual(errors, [])
        return document

    def test_successful_curated_seed_is_accepted_without_renaming_its_observation(self):
        document = self.scan(curated=True)
        self.assertEqual(document['resources'][0]['discovery_methods'], ['curated-reference'])
        self.assertEqual(document['resources'][0]['seed_reference_ids'], ['example-curated-tool'])
        observation, = document['meta']['seed_observations']
        self.assertEqual(observation['method'], 'curated-repository-reference')
        self.assertEqual(observation['status'], 'candidate')
        self.assertEqual(observation['reference_ids'], ['example-curated-tool'])

    def test_shared_curated_paper_and_tracker_seed_keeps_distinct_provenance(self):
        document = self.scan(curated=True, papers=True, tracker=True)
        record = document['resources'][0]
        self.assertEqual(record['discovery_methods'], [
            'curated-reference', 'paper-artifact-reference', 'tracker-audit-reference'])
        self.assertEqual(record['seed_reference_ids'], ['example-curated-tool', 'tracker-example-tool'])
        self.assertEqual(record['seed_paper_ids'], ['paper-example'])
        self.assertEqual(record['seed_paper_references'], [{
            'paper_id': 'paper-example', 'field': 'code_url',
            'url': 'https://github.com/example/tool-1'}])
        self.assertEqual([entry['method'] for entry in document['meta']['seed_observations']], [
            'curated-repository-reference', 'paper-artifact-reference', 'tracker-audit-reference'])
        self.assertEqual(document['meta']['attempted_readme_scans'], 1)

    def test_paper_and_tracker_seed_methods_are_not_relabelled_as_curated(self):
        for options, method in (({'papers': True}, 'paper-artifact-reference'),
                                ({'tracker': True}, 'tracker-audit-reference')):
            with self.subTest(method=method):
                document = self.scan(**options)
                self.assertEqual(document['resources'][0]['discovery_methods'], [method])
                observation, = document['meta']['seed_observations']
                self.assertEqual(observation['method'], method)


if __name__ == '__main__':
    unittest.main()
