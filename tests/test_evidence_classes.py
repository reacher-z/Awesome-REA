"""Evidence-class data coverage: observed sources carry 1-3, unavailable ones are unknown, and Class 0 needs a manual review."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import classify_evidence_classes  # noqa: E402
from classify_evidence_classes import github_api_fetch, gitlab_api_fetch, is_demo_image  # noqa: E402
SCOPES = ('full', 'partial', 'analysis', 'unknown', 'notes')


class EvidenceClassDataTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads((ROOT / 'data/evidence-classes.json').read_text(encoding='utf-8'))
        self.catalog_ids = []
        self.catalog = {}
        for filename in ('rea-resources.json', 'tool-resources.json'):
            for record in json.loads((ROOT / 'data' / filename).read_text(encoding='utf-8')):
                self.catalog_ids.append(record['id'])
                self.catalog[record['id']] = record
        self.reviews_document = json.loads((ROOT / 'data/evidence-class-zero-reviews.json').read_text(encoding='utf-8'))
        self.reviews = {entry['id']: entry for entry in self.reviews_document['entries']}

    def test_schema_and_counts_agree(self):
        self.assertEqual(self.document['schema_version'], 1)
        meta = self.document['meta']
        self.assertEqual(meta['spec_version'], 'evidence-class-v4')
        entries = self.document['entries']
        counts = {}
        for entry in entries:
            if entry['evidence_class'] is None:
                continue
            counts[entry['evidence_class']] = counts.get(entry['evidence_class'], 0) + 1
        self.assertEqual({str(key): value for key, value in counts.items()}, meta['class_counts'])
        self.assertEqual(meta['unknown_count'], sum(entry['evidence_class'] is None for entry in entries))
        self.assertEqual(meta['entry_count'], len(entries))
        self.assertEqual(meta['c0_review_count'], sum(entry['evidence_class'] == 0 for entry in entries))

    def test_every_curated_entry_has_one_state(self):
        classified = {entry['id'] for entry in self.document['entries']}
        self.assertEqual(classified, set(self.catalog_ids),
                         'data/evidence-classes.json must cover exactly the curated catalog IDs')
        for entry in self.document['entries']:
            self.assertIn(entry['basis'], ('github-rest', 'gitlab-rest', 'page-fetch', 'manual-review'), entry['id'])
            self.assertTrue(entry['reason'], entry['id'])
            self.assertIn(entry['scope'], SCOPES, entry['id'])
            self.assertEqual(entry['runtime_status'], 'not-run', entry['id'])
            self.assertIn('code', entry['signals'], entry['id'])
            if entry['evidence_status'] == 'unknown':
                self.assertIsNone(entry['evidence_class'], entry['id'])
                self.assertEqual(entry['scope'], 'unknown', entry['id'])
            else:
                self.assertEqual(entry['evidence_status'], 'observed', entry['id'])
                self.assertIn(entry['evidence_class'], (0, 1, 2, 3), entry['id'])

    def test_class_zero_requires_a_manual_review(self):
        class_zero = {entry['id'] for entry in self.document['entries'] if entry['evidence_class'] == 0}
        reviewed = {entry_id for entry_id, review in self.reviews.items() if review.get('scope') == 'full'}
        self.assertEqual(class_zero, reviewed, 'every Class 0 entry needs a scope=full review, and every full review must be Class 0')
        for entry_id, review in self.reviews.items():
            self.assertIn(entry_id, self.catalog, entry_id)
            self.assertIn(review.get('scope'), ('full', 'partial'), entry_id)
            self.assertTrue(review.get('note'), entry_id)
            self.assertTrue(review.get('reviewed_at'), entry_id)
            if review.get('scope') == 'full':
                self.assertTrue(review.get('primary_evidence'), entry_id)
                self.assertTrue(review.get('version'), entry_id)

    def test_class_zero_is_a_full_software_reconstruction(self):
        for entry in self.document['entries']:
            if entry['evidence_class'] != 0:
                continue
            record = self.catalog[entry['id']]
            self.assertEqual(record['kind'], 'case-study', entry['id'])
            self.assertNotIn('binary', record.get('targets', []), entry['id'])
            self.assertTrue(entry['signals'].get('demo'), entry['id'])
            self.assertEqual(entry['basis'], 'manual-review', entry['id'])
            self.assertIn('review', entry, entry['id'])

    def test_private_repository_is_unavailable(self):
        for repository in ({'private': True}, {'visibility': 'private'}):
            meta = github_api_fetch(_FakeClient(repository), 'acme/private-fixture')
            self.assertTrue(meta['unavailable'])
            self.assertNotIn('readme_text', meta)

    def test_private_media_is_not_demo_evidence(self):
        self.assertFalse(is_demo_image('https://private-user-images.githubusercontent.com/1/a.png', 'demo'))
        self.assertFalse(is_demo_image('https://user-images.githubusercontent.com/1/a.png?jwt=secret', 'demo'))
        self.assertTrue(is_demo_image('https://user-images.githubusercontent.com/1/a.png', 'demo'))


class GitLabReadmeTests(unittest.TestCase):
    def test_extensionless_readme_is_read(self):
        readme = 'Disassembly notes. ' * 40
        responses = {
            '/projects/group%2Fgame': {'default_branch': 'main'},
            '/projects/group%2Fgame/releases': [],
            '/projects/group%2Fgame/repository/tree?per_page=100&ref=main': [
                {'name': 'README', 'type': 'tree'}, {'name': 'README', 'type': 'blob'}, {'name': 'src', 'type': 'tree'}],
        }

        class Client:
            def get(self, url, timeout=30, page=False):
                path = url.split('/api/v4', 1)[1]
                if path == '/projects/group%2Fgame/repository/files/README/raw?ref=main':
                    return 200, readme.encode(), {}
                if path in responses:
                    return 200, json.dumps(responses[path]).encode(), {}
                return 404, b'', {}

        original = classify_evidence_classes.cached, classify_evidence_classes.store_cache
        classify_evidence_classes.cached = lambda key: None
        classify_evidence_classes.store_cache = lambda key, payload: None
        try:
            meta = gitlab_api_fetch(Client(), 'group/game')
        finally:
            classify_evidence_classes.cached, classify_evidence_classes.store_cache = original
        self.assertEqual(meta['readme_bytes'], len(readme.encode()))

    def test_readme_url_names_the_file(self):
        readme = 'Decompilation notes. ' * 40

        class Client:
            def get(self, url, timeout=30, page=False):
                path = url.split('/api/v4', 1)[1]
                if path == '/projects/group%2Fgame':
                    return 200, json.dumps({'default_branch': 'master',
                                            'readme_url': 'https://gitlab.com/group/game/-/blob/master/readme.md'}).encode(), {}
                if path == '/projects/group%2Fgame/releases':
                    return 200, b'[]', {}
                if path == '/projects/group%2Fgame/repository/files/readme.md/raw?ref=master':
                    return 200, readme.encode(), {}
                return 404, b'', {}

        original = classify_evidence_classes.cached, classify_evidence_classes.store_cache
        classify_evidence_classes.cached = lambda key: None
        classify_evidence_classes.store_cache = lambda key, payload: None
        try:
            meta = gitlab_api_fetch(Client(), 'group/game')
        finally:
            classify_evidence_classes.cached, classify_evidence_classes.store_cache = original
        self.assertEqual(meta['readme_bytes'], len(readme.encode()))


class GitLabThrottleTests(unittest.TestCase):
    def test_throttled_readme_is_not_recorded_as_missing(self):
        stored = []

        class Client:
            def get(self, url, timeout=30, page=False):
                path = url.split('/api/v4', 1)[1]
                if path == '/projects/group%2Fgame':
                    return 200, json.dumps({'default_branch': 'main'}).encode(), {}
                if path == '/projects/group%2Fgame/releases':
                    return 200, b'[]', {}
                return 429, b'', {}

        original = classify_evidence_classes.cached, classify_evidence_classes.store_cache
        classify_evidence_classes.cached = lambda key: None
        classify_evidence_classes.store_cache = lambda key, payload: stored.append(key)
        try:
            meta = gitlab_api_fetch(Client(), 'group/game')
        finally:
            classify_evidence_classes.cached, classify_evidence_classes.store_cache = original
        self.assertTrue(meta['unavailable'])
        self.assertEqual(stored, [])


class _FakeClient:
    """Just enough of the shared HttpClient to answer one repository request."""

    def __init__(self, repository):
        self.repository = repository

    def get(self, url, timeout=30, page=False):
        return 200, json.dumps(self.repository).encode(), {}


if __name__ == '__main__':
    unittest.main()
