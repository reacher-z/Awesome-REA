"""Automatic scan labels must be a pure function of the published capture fields."""
import base64
import contextlib
import copy
import hashlib
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
from scan_sources import (CLASSIFICATION_ENGINE_VERSION, classify, initial_meta, protocol_report, protocol_signals,
                          published_fields, relabel_report, run_scan, scan_readme)

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


def readme_api(body=b'# Example\nA small README for a test fixture.\n', full_name='example/demo'):
    class FakeAPI:
        def json(self, path):
            if path.startswith('/repositories/'):
                return {**repository(), 'full_name': full_name, 'html_url': 'https://github.com/' + full_name,
                        'private': False, 'fork': False, 'archived': False}
            return {'type': 'file', 'size': len(body), 'encoding': 'base64',
                    'content': base64.b64encode(body).decode(),
                    'sha': hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest(), 'path': 'README.md',
                    'html_url': 'https://github.com/' + full_name + '/blob/main/README.md'}
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
                                   'topics': ['protocol-reverse-engineering']}), (['protocol'], 'protocol-analysis'))
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
        record, _ = scan_readme(readme_api(full_name='morluto/rea'), repository(full_name='morluto/rea', html_url='https://github.com/morluto/rea'))
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


class ProtocolTargetTests(unittest.TestCase):
    def test_explicit_protocol_signals_add_the_target(self):
        for fixture, expected in (
            ({'description': '', 'topics': ['protocol-analysis']}, (['protocol'], 'protocol-analysis')),
            ({'description': '', 'topics': ['wireshark']}, (['protocol'], 'protocol-analysis')),
            ({'description': 'BLE protocol reverse engineering for a label printer', 'topics': []},
             (['protocol'], 'protocol-analysis')),
            ({'description': 'Network protocol fuzzing framework', 'topics': []}, (['protocol'], 'protocol-analysis')),
            # A higher-precedence category keeps its place; the target is still added.
            ({'description': 'Ghidra loader for captured traffic', 'topics': ['pcap']},
             (['binary', 'protocol'], 'native-analysis')),
        ):
            with self.subTest(fixture=fixture):
                self.assertEqual(classify({'full_name': 'example/tool', **fixture}), expected)

    def test_mcp_rest_api_and_mitmproxy_alone_do_not_qualify(self):
        for fixture, expected in (
            ({'description': 'A Model Context Protocol server', 'topics': ['mcp', 'model-context-protocol']},
             ([], 'reverse-engineering')),
            ({'description': 'Model Context Protocol reverse engineering', 'topics': []}, ([], 'reverse-engineering')),
            ({'description': 'Client for a REST API', 'topics': ['rest-api']}, (['website'], 'web-analysis')),
            ({'description': 'Certificate pinning removal', 'topics': ['mitmproxy']}, (['website'], 'web-analysis')),
        ):
            with self.subTest(fixture=fixture):
                self.assertEqual(classify({'full_name': 'example/tool', **fixture}), expected)
                self.assertEqual(protocol_signals({'full_name': 'example/tool', **fixture}), [])
        # This retained record reached protocol-analysis only through its rest-api topic.
        flight = next(record for record in json.loads((ROOT / 'data/source-index.json').read_text(encoding='utf-8'))['resources']
                      if record['id'] == 'scan-1393536781')
        self.assertEqual((flight['targets'], flight['category']), (['app', 'website'], 'protocol-analysis'))
        self.assertEqual(classify(published_fields(flight)), (['app', 'website'], 'web-analysis'))

    def test_target_and_category_share_one_signal(self):
        records = json.loads((ROOT / 'data/source-index.json').read_text(encoding='utf-8'))['resources']
        fixtures = FIXTURES + [published_fields(record) for record in records]
        tagged = 0
        for fixture in fixtures:
            targets, category = classify(fixture)
            signalled = bool(protocol_signals(fixture))
            tagged += signalled
            self.assertEqual('protocol' in targets, signalled, fixture['full_name'])
            if category == 'protocol-analysis':
                self.assertIn('protocol', targets, fixture['full_name'])
        self.assertGreater(tagged, 0)

    def test_new_captures_carry_the_protocol_target(self):
        record, _ = scan_readme(readme_api(), repository(description='Wireshark dissector', topics=['wireshark']))
        self.assertEqual(record['classification_engine_version'], CLASSIFICATION_ENGINE_VERSION)
        self.assertEqual((record['targets'], record['category']), (['protocol'], 'protocol-analysis'))


class ProtocolReportTests(unittest.TestCase):
    def test_report_lists_protocol_changes_without_rewriting_records(self):
        def stored(identifier, targets, category, **changes):
            return {'id': identifier, 'full_name': 'example/' + identifier, 'description_en': '',
                    'topics': [], 'targets': targets, 'category': category,
                    'classification_origin': 'automatic-metadata', **changes}
        document = {'resources': [
            stored('unchanged', [], 'reverse-engineering'),
            stored('capture', [], 'protocol-analysis', topics=['pcap']),
            stored('rest', ['website'], 'protocol-analysis', topics=['rest-api']),
            stored('curated', ['binary'], 'protocol-analysis', topics=['pcap'],
                   classification_origin='curated-cross-reference'),
        ]}
        before = copy.deepcopy(document)
        report = protocol_report(document)
        self.assertEqual(document, before)
        self.assertEqual((report['compared_automatic_records'], report['skipped_cross_referenced_records'],
                          report['differing_records']), (3, 1, 2))
        self.assertEqual(report['changes'], {'adds-protocol-target': 1, 'enters-protocol-analysis': 0,
                                             'leaves-protocol-analysis': 1})
        self.assertEqual([(row['id'], row['changes'], row['protocol_signals'], row['rederived']) for row in report['records']], [
            ('capture', ['adds-protocol-target'], ['topic:pcap'], {'targets': ['protocol'], 'category': 'protocol-analysis'}),
            ('rest', ['leaves-protocol-analysis'], [], {'targets': ['website'], 'category': 'web-analysis'}),
        ])

    def test_command_reads_the_snapshot_offline_and_retags_nothing(self):
        snapshot = ROOT / 'data/source-index.json'
        before = snapshot.read_bytes()
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/scan_sources.py'), '--protocol-report', str(snapshot)],
                                capture_output=True, text=True, check=True, env={**os.environ, 'PATH': ''})
        report = json.loads(result.stdout)
        self.assertEqual(snapshot.read_bytes(), before)
        # Retained records keep their stored labels; none was given the target automatically.
        self.assertFalse(any('protocol' in record['targets'] for record in json.loads(before)['resources']))
        self.assertGreater(report['changes']['adds-protocol-target'], 0)
        for row in report['records']:
            self.assertEqual('adds-protocol-target' in row['changes'], bool(row['protocol_signals']), row['id'])
        self.assertIn('scan-1393536781', [row['id'] for row in report['records'] if 'leaves-protocol-analysis' in row['changes']])


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
