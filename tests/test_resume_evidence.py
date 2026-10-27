"""A resumed scan snapshot passes the publication evidence checks before any authentication."""
import contextlib
from copy import deepcopy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import scan_sources
from validate import validate_source_index


def success(number, **changes):
    name = f'owner/repo-{number}'
    return {'id': f'scan-{number}', 'full_name': name, 'url': 'https://github.com/' + name,
            'scan_status': 'readme-scanned', 'readme_url': f'https://github.com/{name}/blob/main/README.md',
            'readme_api_url': f'https://api.github.com/repos/{name}/readme', 'readme_sha256': 'a' * 64,
            'readme_git_sha': 'b' * 40, 'readme_content_git_sha': 'b' * 40, 'readme_git_sha_matches_content': True,
            **changes}


# An in-progress checkpoint: one search-discovered success, one legacy success without provenance,
# one failure and one discovered repository that is not attempted yet.
CHECKPOINT = {
    'meta': {'status': 'in-progress', 'successful_readme_scans': 2, 'failed': 1, 'attempted_readme_scans': 3,
             'discovered_repository_ids': ['scan-1', 'scan-2', 'scan-3', 'scan-4'], 'unique_repos': 4,
             'unattempted_candidates': 1,
             'queries': [{'query': 'topic:decompiler', 'status': 'ok', 'returned': 2,
                          'observed_at': '2026-10-16T01:00:00Z'}]},
    'resources': [success(1, discovery_methods=['github-search'], matched_queries=['topic:decompiler']), success(2)],
    'failures': [{'id': 'scan-3', 'full_name': 'owner/repo-3', 'url': 'https://github.com/owner/repo-3',
                  'scan_status': 'failed', 'reason': 'http-404', 'http_status': 404}],
}


def legacy_snapshot():
    document = deepcopy(CHECKPOINT)
    del document['meta']['discovered_repository_ids']
    document['resources'][0] = success(1)  # Count-only snapshots predate per-record provenance.
    return document


def with_change(path, value):
    document = deepcopy(CHECKPOINT)
    target = document
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    return document


MALFORMED = {
    'uppercase README SHA-256': with_change(['resources', 1, 'readme_sha256'], 'A' * 64),
    'short README SHA-256': with_change(['resources', 1, 'readme_sha256'], 'a' * 63),
    'computed Git hash': with_change(['resources', 1, 'readme_content_git_sha'], 'not-a-sha'),
    'non-HTTPS README URL': with_change(['resources', 1, 'readme_url'], 'http://github.com/owner/repo-2/blob/main/README.md'),
    'README API URL for another repository': with_change(['resources', 1, 'readme_api_url'],
                                                         'https://api.github.com/repos/other/repo/readme'),
    'repository URL and name disagree': with_change(['resources', 1, 'url'], 'https://github.com/owner/other'),
    'private repository metadata': with_change(['resources', 1, 'private'], True),
    'failure URL': with_change(['failures', 0, 'url'], 'https://example.org/owner/repo-3'),
    'unobserved matched query': with_change(['resources', 0, 'matched_queries'], ['topic:never-searched']),
    'unknown discovery method': with_change(['resources', 0, 'discovery_methods'], ['guessed']),
}


def write(directory, document):
    path = Path(directory) / 'snapshot.json'
    path.write_text(json.dumps(document), encoding='utf-8')
    return path


class ResumeEvidenceTests(unittest.TestCase):
    def test_valid_checkpoints_and_legacy_snapshots_remain_resumable(self):
        for label, document in (('in-progress checkpoint', CHECKPOINT), ('legacy count-only snapshot', legacy_snapshot())):
            with self.subTest(label), tempfile.TemporaryDirectory() as directory:
                loaded, digest = scan_sources.load_resume(write(directory, document))
                self.assertEqual(loaded, document)
                self.assertRegex(digest, r'^[0-9a-f]{64}$')

    def test_malformed_hashes_urls_and_provenance_are_rejected(self):
        findings = {
            'uppercase README SHA-256': 'record 1: missing README SHA-256',
            'short README SHA-256': 'record 1: missing README SHA-256',
            'computed Git hash': 'record 1: computed README Git hash and comparison flag disagree',
            'non-HTTPS README URL': 'record 1: invalid public readme_url',
            'README API URL for another repository': 'record 1: README API URL must match the public GitHub repository',
            'repository URL and name disagree': 'record 1: repository URL and full_name disagree',
            'private repository metadata': 'record 1: repository metadata must describe a public',
            'failure URL': 'failure 0: invalid public GitHub repository URL',
            'unobserved matched query': 'record 0: search discovery needs actually observed matched queries',
            'unknown discovery method': 'record 0: invalid discovery methods',
        }
        self.assertEqual(set(findings), set(MALFORMED))
        for label, document in MALFORMED.items():
            with self.subTest(label), tempfile.TemporaryDirectory() as directory:
                with self.assertRaises(ValueError) as raised:
                    scan_sources.load_resume(write(directory, document))
                self.assertIn('Resume snapshot retains invalid evidence', str(raised.exception))
                self.assertIn('first: source index ' + findings[label], str(raised.exception))

    def test_rejection_happens_before_authentication_or_any_request(self):
        refused = AssertionError('authentication or network access before resume validation')
        for label in ('uppercase README SHA-256', 'unobserved matched query'):
            with self.subTest(label), tempfile.TemporaryDirectory() as directory:
                path = write(directory, MALFORMED[label])
                argv = ['scan_sources.py', '--resume', str(path), '--output', str(Path(directory) / 'next.json')]
                output = io.StringIO()
                with patch.object(sys, 'argv', argv), patch.object(scan_sources.subprocess, 'run', side_effect=refused), \
                        patch.object(scan_sources, 'GitHub', side_effect=refused), contextlib.redirect_stdout(output):
                    self.assertEqual(scan_sources.main(), 2)
                self.assertIn('Resume snapshot could not be read', output.getvalue())
                self.assertFalse((Path(directory) / 'next.json').exists())

    def test_publication_still_requires_a_complete_and_large_enough_snapshot(self):
        errors = []
        validate_source_index(deepcopy(CHECKPOINT), errors)
        self.assertIn('Source index is an incomplete checkpoint; finish the scan before publication.', errors)
        self.assertIn('Source index must retain more than 1,500 successful scans and matching counts.', errors)
        errors = []
        validate_source_index(deepcopy(CHECKPOINT), errors, allow_incomplete=True)
        self.assertNotIn('Source index is an incomplete checkpoint; finish the scan before publication.', errors)
        self.assertIn('Source index must retain more than 1,500 successful scans and matching counts.', errors)
        # Publication still requires the fields a resumed checkpoint may omit.
        document = deepcopy(CHECKPOINT)
        del document['resources'][1]['readme_url']
        with tempfile.TemporaryDirectory() as directory:
            scan_sources.load_resume(write(directory, document))
        errors = []
        validate_source_index(document, errors, allow_incomplete=True)
        self.assertIn('source index record 1: invalid public readme_url', errors)


if __name__ == '__main__':
    unittest.main()
