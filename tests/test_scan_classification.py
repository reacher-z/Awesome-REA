"""Automatic scan labels must be a pure function of the published capture fields."""
import base64
import contextlib
import copy
import io
from itertools import permutations
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from scan_sources import CLASSIFICATION_ENGINE_VERSION, classify, initial_meta, relabel_report, run_scan, scan_readme

# Joined in some orders, these topics used to read as "java decompiler",
# "protocol reverse-engineering" or "model context protocol".
CROSSING = {'full_name': 'example/friday', 'description': 'A runtime helper.',
            'topics': ['decompiler', 'java', 'protocol', 'reverse-engineering', 'model', 'context']}
FIXTURES = [
    CROSSING,
    {'full_name': 'example/apk-kit', 'description': 'Ghidra scripts for APK triage https://example.com/docs',
     'topics': ['android', 'frida', 'game', 'pcap', 'unity']},
    {'full_name': 'example/mcp-bridge', 'description': 'A Model Context Protocol server for .NET assemblies',
     'topics': ['mcp', 'csharp', 'protocol-analysis', 'web']},
]
CLASSIFY_FIXTURES = r'''
import json, sys
sys.path.insert(0, sys.argv[1])
from scan_sources import classify
print(json.dumps([classify(fixture) for fixture in json.loads(sys.argv[2])]))
'''


def readme_api(body=b'# Example\nA small README for a test fixture.\n'):
    class FakeAPI:
        def json(self, path):
            return {'type': 'file', 'size': len(body), 'encoding': 'base64',
                    'content': base64.b64encode(body).decode(), 'sha': '0' * 40, 'path': 'README.md',
                    'html_url': 'https://github.com/example/demo/blob/main/README.md'}
    return FakeAPI()


def repository(**changes):
    return {'id': 1, 'full_name': 'example/demo', 'html_url': 'https://github.com/example/demo',
            'description': '', 'topics': [], '_metadata_observed_at': '2026-10-16T00:00:00Z',
            '_matched_queries': [], **changes}


class ClassificationDeterminismTests(unittest.TestCase):
    def test_every_topic_order_gives_the_same_labels(self):
        expected = classify(CROSSING)
        self.assertEqual(expected, ([], 'reverse-engineering'))
        for order in permutations(CROSSING['topics']):
            with self.subTest(order=order):
                self.assertEqual(classify({**CROSSING, 'topics': list(order)}), expected)

    def test_labels_do_not_depend_on_the_python_hash_seed(self):
        outputs = set()
        for seed in range(16):
            environment = {**os.environ, 'PYTHONHASHSEED': str(seed)}
            result = subprocess.run([sys.executable, '-c', CLASSIFY_FIXTURES, str(ROOT / 'scripts'), json.dumps(FIXTURES)],
                                    env=environment, capture_output=True, text=True, check=True)
            outputs.add(result.stdout)
        self.assertEqual(len(outputs), 1)
        self.assertEqual(json.loads(outputs.pop()), [list(classify(fixture)) for fixture in FIXTURES])

    def test_signals_within_one_topic_or_the_description_still_count(self):
        self.assertEqual(classify({'full_name': 'example/tool', 'description': 'A Java decompiler',
                                   'topics': []})[0], ['app'])
        self.assertEqual(classify({'full_name': 'example/tool', 'description': '',
                                   'topics': ['java-decompiler']})[0], ['app'])
        self.assertEqual(classify({'full_name': 'example/tool', 'description': '',
                                   'topics': ['protocol-reverse-engineering']}), ([], 'protocol-analysis'))
        self.assertEqual(classify({'full_name': 'example/tool', 'description': 'Network protocol reverse engineering',
                                   'topics': []})[1], 'protocol-analysis')
        self.assertEqual(classify({'full_name': 'example/tool', 'description': 'Model Context Protocol reverse engineering',
                                   'topics': []})[1], 'reverse-engineering')

    def test_omitted_description_is_never_classified(self):
        hidden = 'Android Ghidra firmware game decompiler for websites. ' * 25
        record, failure = scan_readme(readme_api(), repository(description=hidden))
        self.assertIsNone(failure)
        self.assertIn('description_omission', record)
        self.assertEqual(record['description_en'], '')
        self.assertEqual((record['targets'], record['category']), ([], 'reverse-engineering'))
        self.assertEqual((record['targets'], record['category']),
                         classify({'full_name': 'example/demo', 'description': '', 'topics': []}))
        record, _ = scan_readme(readme_api(), repository(description='Android APK triage'))
        self.assertEqual((record['targets'], record['category']), (['app'], 'android'))

    def test_new_captures_record_the_engine_and_leave_curated_labels_to_the_build(self):
        # morluto/rea is a curated repository root; the scanner must not copy its labels.
        record, _ = scan_readme(readme_api(), repository(full_name='morluto/rea', html_url='https://github.com/morluto/rea'))
        self.assertEqual(record['classification_engine_version'], CLASSIFICATION_ENGINE_VERSION)
        self.assertEqual(record['classification_origin'], 'automatic-metadata')
        self.assertEqual(record['classification_reference_ids'], [])
        self.assertEqual((record['targets'], record['category']), ([], 'reverse-engineering'))

    def test_resume_bumps_the_engine_without_rewriting_retained_records(self):
        with tempfile.TemporaryDirectory() as directory:
            args = SimpleNamespace(target=1, workers=1, requests_per_second=1, max_pages=1,
                                   candidate_buffer=0, seed_curated=False, seed_papers=False,
                                   queries=[], output=Path(directory) / 'index.json')
            meta = initial_meta(args, '2026-10-16T00:00:00Z')
            meta.update(classification_engine_version=2, classification_policy='Historical policy',
                        discovered_repository_ids=['scan-1'], successful_readme_scans=1, failed=0,
                        attempted_readme_scans=1, unique_repos=1, unattempted_candidates=0)
            retained = {'id': 'scan-1', 'full_name': 'example/retained', 'targets': ['app'],
                        'category': 'reverse-engineering', 'classification_origin': 'automatic-metadata',
                        'classification_reference_ids': [], 'scan_status': 'readme-scanned'}
            before = copy.deepcopy(retained)
            with contextlib.redirect_stdout(io.StringIO()):
                run_scan(None, args, {'meta': meta, 'resources': [retained], 'failures': []}, 'a' * 64)
            result = json.loads(args.output.read_text())
        self.assertEqual(result['resources'], [before])
        self.assertEqual(result['meta']['classification_engine_version'], CLASSIFICATION_ENGINE_VERSION)
        self.assertEqual(result['meta']['current_run']['classification_engine_version'], CLASSIFICATION_ENGINE_VERSION)
        self.assertEqual(result['meta']['resume_history'][-1]['classification_engine_version'], 2)
        self.assertEqual(result['meta']['resume_history'][-1]['classification_policy'], 'Historical policy')


class RelabelReportTests(unittest.TestCase):
    def test_report_lists_differences_without_rewriting_records(self):
        def stored(identifier, targets, category, **changes):
            return {'id': identifier, 'full_name': 'example/' + identifier, 'description_en': '',
                    'topics': [], 'targets': targets, 'category': category,
                    'classification_origin': 'automatic-metadata', **changes}
        document = {'resources': [
            stored('same', [], 'reverse-engineering'),
            stored('crossed', ['app'], 'reverse-engineering', topics=['decompiler', 'java']),
            stored('omitted', ['firmware'], 'firmware', description_en='',
                   description_omission={'original_characters': 1001}),
            stored('curated', ['binary'], 'native-analysis', classification_origin='curated-cross-reference'),
        ]}
        before = copy.deepcopy(document)
        report = relabel_report(document)
        self.assertEqual(document, before)
        self.assertEqual((report['compared_automatic_records'], report['skipped_cross_referenced_records'],
                          report['differing_records']), (3, 1, 2))
        self.assertEqual([(row['id'], row['stored'], row['rederived']) for row in report['records']], [
            ('crossed', {'targets': ['app'], 'category': 'reverse-engineering'},
             {'targets': [], 'category': 'reverse-engineering'}),
            ('omitted', {'targets': ['firmware'], 'category': 'firmware'},
             {'targets': [], 'category': 'reverse-engineering'}),
        ])

    def test_command_reads_the_snapshot_offline_and_leaves_it_unchanged(self):
        snapshot = ROOT / 'data/source-index.json'
        before = snapshot.read_bytes()
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/scan_sources.py'), '--relabel-report', str(snapshot)],
                                capture_output=True, text=True, check=True, env={**os.environ, 'PATH': ''})
        report = json.loads(result.stdout)
        self.assertEqual(report['classification_engine_version'], CLASSIFICATION_ENGINE_VERSION)
        self.assertEqual(report['compared_automatic_records'] + report['skipped_cross_referenced_records'],
                         len(json.loads(before)['resources']))
        self.assertEqual(snapshot.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
