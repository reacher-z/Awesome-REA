"""Quality evaluation data schema: candidates and generated results."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import validate_quality_scoring as quality  # noqa: E402


def candidate():
    return {
        'id': 'candidate-case',
        'name': 'Candidate',
        'url': 'https://github.com/acme/candidate',
        'category': 'reconstruction-cases',
        'relationship': 'independent-reconstruction',
        'description_en': 'A documented reconstruction.',
        'description_zh': '一个有记录的复现。',
        'evidence_url': 'https://github.com/acme/candidate/blob/abc123/README.md',
        'verified_at': '2026-11-03',
        'verification': 'source-reviewed',
        'requirements': ['Requires Rust 1.94 or newer.'],
        'targets': ['app'],
        'kind': 'case-study',
        'source_index_id': 'scan-1',
        'selection_reason': 'Selected for rule-based scoring.',
        'evidence': {
            'evidence_class': None,
            'basis': 'source-index',
            'evidence_status': 'observed',
            'signals': {
                'code': True, 'code_basis': 'repo', 'docs': True, 'docs_bytes': 100,
                'docs_full': True, 'download': None, 'download_links': [],
                'release_count': 0, 'release_asset_count': 0, 'demo': ['image'],
                'media_count': 1, 'archived': False, 'unavailable': False,
            },
        },
    }


def candidate_document():
    return {
        'schema_version': 1,
        'meta': {'spec': 'evaluation-candidates-v1', 'purpose': 'Test candidates.', 'updated_at': '2026-11-03'},
        'entries': [candidate()],
    }


def evaluation():
    return {
        'id': 'candidate-case',
        'url': 'https://github.com/acme/candidate',
        'profile': {
            'entry_id': 'candidate-case',
            'url': 'https://github.com/acme/candidate',
            'name': 'Candidate',
            'catalog_status': 'candidate',
            'kind': 'case-study',
            'targets': ['app'],
            'category': 'reconstruction-cases',
            'software': True,
            'evidence_class': None,
            'source': {'code': True, 'basis': 'source-index', 'repo': 'acme/candidate',
                       'tests_declared': False, 'build_manifests': [], 'license': None},
            'docs': {'docs': True, 'docs_full': True, 'bytes': 100},
            'demo': ['image'],
            'artifacts': [],
            'interfaces': ['cli'],
            'sandbox': {'name': 'docker-linux', 'image': 'local/image:1', 'network': False,
                        'timeout_seconds': 60, 'supported': True, 'reason': None},
            'rule_pack': 'candidate-case',
        },
        'route': {'level': 'L4-functional-rules', 'tools': ['rule-pack'], 'blocked': [],
                  'reason': 'test route'},
        'results': [
            {'id': 'version', 'dimension': 'correctness', 'status': 'pass',
             'reason': 'expectation met', 'evidence': {}},
        ],
        'score': {
            'score': 100.0,
            'formula': '100 * mean(dimension_fraction) * level_weight',
            'level_weight': 1.0,
            'quality_fraction': 1.0,
            'coverage': 1.0,
            'pass_rate': 1.0,
            'all_applicable_pass': True,
            'verdict': 'verified',
            'counts': {'passed': 1, 'failed': 0, 'blocked': 0,
                       'evaluated_dimensions': 1, 'applicable_dimensions': 1},
            'dimensions': {
                'correctness': {
                    'status': 'pass', 'fraction': 1.0,
                    'rules': [{'id': 'version', 'status': 'pass', 'reason': 'expectation met'}],
                },
            },
        },
        'limitations': [],
        'evidence_files': {},
    }


def evaluation_document():
    return {
        'schema_version': 1,
        'meta': {
            'spec_version': 'quality-eval-v1',
            'generated_at': '2026-11-03T00:00:00+00:00',
            'mode': 'score',
            'entry_count': 1,
            'candidate_count': 1,
            'route_counts': {'L4-functional-rules': 1},
            'verdict_counts': {'verified': 1},
            'method': 'test fixture',
        },
        'entries': [evaluation()],
    }


class CandidateSchemaTests(unittest.TestCase):
    def test_valid_candidate_passes(self):
        self.assertEqual(quality.validate_candidates(candidate_document(), set()), [])

    def test_candidate_id_cannot_shadow_a_curated_record(self):
        errors = quality.validate_candidates(candidate_document(), {'candidate-case'})
        self.assertTrue(any('duplicates a curated catalog record' in error for error in errors))

    def test_candidate_requires_the_preliminary_signals(self):
        document = candidate_document()
        del document['entries'][0]['evidence']['signals']['code']
        errors = quality.validate_candidates(document, set())
        self.assertTrue(any('missing required keys' in error for error in errors))

    def test_candidate_requires_a_reviewed_source(self):
        document = candidate_document()
        document['entries'][0]['verification'] = 'automated-readme-scan'
        errors = quality.validate_candidates(document, set())
        self.assertTrue(any('verification must be source-reviewed' in error for error in errors))


class EvaluationSchemaTests(unittest.TestCase):
    def test_valid_evaluation_passes(self):
        self.assertEqual(quality.validate_evaluations(evaluation_document(), {'candidate-case'}), [])

    def test_hand_edited_score_is_rejected(self):
        document = evaluation_document()
        document['entries'][0]['score']['score'] = 99.0
        errors = quality.validate_evaluations(document, {'candidate-case'})
        self.assertTrue(any('expected 100.0' in error for error in errors))

    def test_dimension_status_must_match_results(self):
        document = evaluation_document()
        document['entries'][0]['score']['dimensions']['correctness']['status'] = 'fail'
        errors = quality.validate_evaluations(document, {'candidate-case'})
        self.assertTrue(any('status' in error and 'recomputed' in error for error in errors))

    def test_unknown_entry_id_is_rejected(self):
        errors = quality.validate_evaluations(evaluation_document(), set())
        self.assertTrue(any('neither curated nor a candidate' in error for error in errors))

    def test_counts_must_match_results(self):
        document = evaluation_document()
        document['entries'][0]['score']['counts']['passed'] = 99
        errors = quality.validate_evaluations(document, {'candidate-case'})
        self.assertTrue(any('counts.passed' in error for error in errors))


class PairTests(unittest.TestCase):
    def test_no_quality_data_is_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'data').mkdir()
            self.assertEqual(quality.validate_quality_data(root), [])

    def test_a_lone_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'data').mkdir()
            (root / 'data' / 'evaluation-candidates.json').write_text(
                json.dumps(candidate_document()), encoding='utf-8')
            errors = quality.validate_quality_data(root)
            self.assertTrue(any('must exist together' in error for error in errors))


if __name__ == '__main__':
    unittest.main()
