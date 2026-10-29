"""Private bootstrap imports must preserve bytes without inventing cloud reads."""
import copy
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import scan_seed as seed
import scheduled_source_scan as scheduled
from test_scheduled_source_scan import FakeAPI, artifact, run, small_frontier, snapshot


class SeedFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.doc = snapshot(range(1, 1502), failed=(1502,), pending=(1503,), status='in-progress')
        self.frontier = small_frontier(1, acknowledged=True)
        self.checkpoint = self.root / 'checkpoint.json'
        self.cursor = self.root / 'frontier.json'
        scheduled.write_json(self.checkpoint, self.doc)
        scheduled.write_json(self.cursor, self.frontier)
        self.package = self.root / 'package'

    def package_seed(self, extra=()):
        return seed.pack_seed(self.checkpoint, self.cursor, list(extra), self.package)

    def change_manifest(self, mutate):
        path = self.package / 'manifest.json'
        value = json.loads(path.read_text()); mutate(value); scheduled.write_json(path, value)


class PackagingTests(SeedFixture):
    def test_roundtrip_is_exact_and_retains_one_selected_frontier_without_concatenation(self):
        other = scheduled.search_frontier.new_frontier(until='2026-01-01T00:00:01Z',
                            approved_queries=['"网页" "复刻" in:readme', '"clean room" in:readme'])
        other_path = self.root / 'other.json'; scheduled.write_json(other_path, other)
        manifest = self.package_seed([other_path])
        loaded, fingerprint, restored, received, _ = seed.load_seed(self.package / 'manifest.json', self.root / 'restored')
        self.assertEqual(loaded, self.doc)
        self.assertEqual(restored, self.frontier)
        self.assertEqual(manifest, received)
        self.assertEqual(fingerprint, hashlib.sha256(self.checkpoint.read_bytes()).hexdigest())
        self.assertEqual((self.root / 'restored/scan-seed-checkpoint.json').read_bytes(), self.checkpoint.read_bytes())
        self.assertEqual(json.loads((self.root / 'restored/scan-seed-evidence-frontier-1.json').read_text()), other)
        self.assertNotIn(str(self.root), json.dumps(manifest))
        for name in manifest['files']:
            self.assertEqual((self.package / name).read_bytes()[:8], b'\x1f\x8b\x08\x00\x00\x00\x00\x00')
        with self.assertRaisesRegex(ValueError, 'empty'):
            self.package_seed()

    def test_reproducible_gzip_has_no_filename_and_changed_sources_block_manifest(self):
        self.package_seed()
        other = self.root / 'other-package'
        seed.pack_seed(self.checkpoint, self.cursor, [], other)
        self.assertEqual((self.package / seed.CHECKPOINT).read_bytes(), (other / seed.CHECKPOINT).read_bytes())
        original = seed.compress_file
        def changing(source, destination, bound):
            if source == self.cursor:
                source.write_text(source.read_text() + '\n')
            return original(source, destination, bound)
        destination = self.root / 'racy-package'
        with patch.object(seed, 'compress_file', side_effect=changing), self.assertRaisesRegex(ValueError, 'changed'):
            seed.pack_seed(self.checkpoint, self.cursor, [], destination)
        self.assertFalse((destination / 'manifest.json').exists())

    def test_compressed_hash_expanded_hash_and_expansion_limit_fail_closed(self):
        self.package_seed()
        pristine = (self.package / 'manifest.json').read_bytes()
        changes = [lambda m: m['files'][seed.CHECKPOINT]['compressed'].update(sha256='0' * 64),
                   lambda m: m['files'][seed.CHECKPOINT]['uncompressed'].update(sha256='0' * 64),
                   lambda m: m['files'][seed.CHECKPOINT]['uncompressed'].update(bytes=1)]
        for index, change in enumerate(changes):
            with self.subTest(case=index):
                (self.package / 'manifest.json').write_bytes(pristine)
                self.change_manifest(change)
                with self.assertRaises(ValueError):
                    seed.load_seed(self.package / 'manifest.json', self.root / f'bad-{index}')
        description = json.loads(pristine)['files'][seed.CHECKPOINT]
        destination = self.root / 'too-big.json'
        with self.assertRaisesRegex(ValueError, 'byte bound'):
            seed.decompress_file(self.package / seed.CHECKPOINT, destination, description, 100)
        self.assertFalse(destination.exists())
        self.assertFalse(destination.with_suffix('.tmp').exists())

    def test_concatenated_gzip_header_metadata_symlink_and_crc_are_rejected(self):
        manifest = self.package_seed()
        original = (self.package / seed.CHECKPOINT).read_bytes()
        buffer = io.BytesIO()
        with gzip.GzipFile(filename='private-source-path.json', mode='wb', mtime=0, fileobj=buffer) as stream:
            stream.write(self.checkpoint.read_bytes())
        variants = [original + gzip.compress(b'', mtime=0), buffer.getvalue(), original[:-1]]
        for index, raw in enumerate(variants):
            with self.subTest(case=index):
                path = self.root / f'invalid-{index}.gz'; path.write_bytes(raw)
                description = {**manifest['files'][seed.CHECKPOINT],
                               'compressed': {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}}
                with self.assertRaises((ValueError, seed.zlib.error)):
                    seed.decompress_file(path, self.root / f'out-{index}.json', description, scheduled.MAX_SCAN_BYTES)
        linked = self.root / 'link.gz'; linked.symlink_to(self.package / seed.CHECKPOINT)
        with self.assertRaises(ValueError):
            seed.decompress_file(linked, self.root / 'linked.json', manifest['files'][seed.CHECKPOINT], scheduled.MAX_SCAN_BYTES)

    def test_manifest_rejects_paths_unknown_fields_and_arithmetic_before_writing(self):
        self.package_seed()
        pristine = (self.package / 'manifest.json').read_bytes()
        changes = [lambda m: m.update(raw_token='do-not-expose'),
                   lambda m: m.update(evidence_frontiers=['../frontier.json.gz']),
                   lambda m: m['counts'].update(unique_repos=1),
                   lambda m: m.update(created_at='2026-01-01T00:00:00'),
                   lambda m: m['files'][seed.FRONTIER]['uncompressed'].update(bytes=scheduled.MAX_FRONTIER_BYTES + 1)]
        for index, change in enumerate(changes):
            with self.subTest(case=index):
                (self.package / 'manifest.json').write_bytes(pristine); self.change_manifest(change)
                destination = self.root / f'rejected-{index}'
                with self.assertRaises(ValueError):
                    seed.load_seed(self.package / 'manifest.json', destination)
                self.assertFalse(destination.exists())

    def test_raw_private_fields_and_frontier_ahead_of_evidence_never_package(self):
        original = copy.deepcopy(self.doc)
        for change in (lambda: self.doc['resources'][0].update(readme_body='not serialized'),
                       lambda: self.doc['resources'][0].update(description_en='/'.join(('', 'Users', 'fixture', 'private')))):
            self.doc = copy.deepcopy(original)
            change(); scheduled.write_json(self.checkpoint, self.doc)
            with self.assertRaises(ValueError):
                self.package_seed()
        self.doc = snapshot(range(1, 1502)); scheduled.write_json(self.checkpoint, self.doc)
        for acknowledged in (False, True):
            scheduled.write_json(self.cursor, small_frontier(1600, acknowledged=acknowledged))
            with self.assertRaises(ValueError):
                self.package_seed()

    def test_import_is_first_only_and_does_not_modify_source_schema(self):
        self.package_seed()
        document, _, frontier, proof = seed.import_seed(self.package / 'manifest.json', self.root / 'first',
                                                      None, None, None, worker_commit='a' * 40)
        self.assertEqual(document, self.doc)
        self.assertEqual(frontier, self.frontier)
        self.assertEqual(proof['kind'], 'manual-local-union')
        self.assertEqual(proof['imported_counts'], scheduled.counts(self.doc))
        self.assertNotIn('manual_seed_imports', document['meta'])
        with patch.object(seed, 'load_seed', side_effect=AssertionError('No import should begin')):
            for old, fingerprint, cursor in ((self.doc, None, None), (None, 'b' * 64, None), (None, None, self.frontier)):
                with self.assertRaisesRegex(ValueError, 'Later seed imports'):
                    seed.import_seed(self.package / 'manifest.json', self.root / 'later', old, fingerprint, cursor,
                                     worker_commit='a' * 40)

    def test_manifest_fingerprint_matches_parsed_bytes_if_file_changes_after_size_check(self):
        self.package_seed()
        path = self.package / 'manifest.json'
        original_info = scheduled.file_info(path, seed.MAX_MANIFEST_BYTES)
        changed = json.loads(path.read_text()); changed['created_at'] = '2026-01-01T00:00:00Z'
        raw = json.dumps(changed).encode()
        def swap(*args):
            path.write_bytes(raw)
            return original_info
        with patch.object(scheduled, 'file_info', side_effect=swap):
            parsed, fingerprint = seed.read_manifest(path)
        self.assertEqual(parsed, changed)
        self.assertEqual(fingerprint, hashlib.sha256(raw).hexdigest())
        self.assertNotEqual(fingerprint, original_info['sha256'])


class PrivateBootstrapRuntimeTests(SeedFixture):
    def test_bootstrap_then_restore_preserves_provenance_and_reports_only_new_cloud_reads(self):
        self.package_seed()
        (self.root / 'data').mkdir()
        scheduled.write_json(self.root / 'data/source-index.json', snapshot(range(1, 1502)))
        environment = {'GITHUB_REPOSITORY': 'example/worker', 'DEFAULT_BRANCH': 'main', 'GITHUB_EVENT_NAME': 'workflow_dispatch',
                       'GITHUB_REF': 'refs/heads/main', 'GITHUB_RUN_ID': '20', 'GITHUB_RUN_ATTEMPT': '1',
                       'GITHUB_SHA': 'd' * 40, 'GH_TOKEN': 'ephemeral-test-value',
                       'GITHUB_OUTPUT': str(self.root / 'outputs'), 'GITHUB_STEP_SUMMARY': str(self.root / 'summary')}
        execution = {'repository': 'reacher-z/Awesome-REA', 'commit': 'e' * 40}
        api = FakeAPI([], {})
        original_get = api.get
        api.get = lambda path: {'private': True, 'full_name': 'example/worker'} if path == '' else original_get(path)
        directory = self.root / '.cache/first'
        with patch.dict(os.environ, environment), patch.object(scheduled, 'ROOT', self.root), \
                patch.object(scheduled.search_frontier, 'ROOT', self.root), patch.object(scheduled, 'ActionsAPI', return_value=api), \
                patch.object(scheduled.subprocess, 'Popen', side_effect=AssertionError('Bootstrap must not scan')):
            self.assertEqual(scheduled.orchestrate(directory, manual_seed=self.package / 'manifest.json',
                                                  execution_source=execution, bootstrap_only=True), 0)
        receipt = json.loads((directory / 'checkpoint/receipt.json').read_text())
        self.assertEqual(receipt['outcome'], 'bootstrap-imported')
        self.assertEqual(receipt['new_successful_scans'], 0)
        self.assertEqual(receipt['planned_new_successes'], 0)
        self.assertEqual(receipt['counts'], scheduled.counts(self.doc))
        self.assertEqual(receipt['bootstrap_origins'], [receipt['manual_seed_import']])
        self.assertEqual(receipt['source_commit'], 'd' * 40)
        self.assertEqual(receipt['execution_source'], execution)
        self.assertEqual((directory / 'checkpoint/checkpoint.json').read_bytes(), self.checkpoint.read_bytes())
        appended = json.loads((directory / 'checkpoint/frontier.json').read_text())
        self.assertEqual(appended['partitions'][0], self.frontier['partitions'][0])
        self.assertEqual(appended['observations'], self.frontier['observations'])
        self.assertEqual(len(appended['roots']), 52)
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
            for path in (directory / 'checkpoint').iterdir():
                bundle.writestr(path.name, path.read_bytes())
        raw = archive.getvalue()
        previous_run = run(20, head_sha='d' * 40, head_repository={'full_name': 'example/worker'})
        previous_artifact = artifact(20, digest='sha256:' + hashlib.sha256(raw).hexdigest())
        api = FakeAPI([previous_run], {20: [previous_artifact]}); api.repository = 'example/worker'
        api.download = lambda suffix, path: path.write_bytes(raw)
        environment.update(GITHUB_RUN_ID='21', GITHUB_SHA='f' * 40)
        second = self.root / '.cache/second'
        def child(command, **kwargs):
            output = Path(command[command.index('--output') + 1])
            next_document = copy.deepcopy(self.doc)
            # One actual mocked capture, keeping every original object and known ID.
            from test_scheduled_source_scan import record
            next_document['resources'].append(record(1503))
            next_document['meta'].update(successful_readme_scans=1502, attempted_readme_scans=1503,
                                         unattempted_candidates=0, requested_successful_scans=1502)
            scheduled.write_json(output, next_document)
            return type('Process', (), {'wait': lambda self, timeout: 0})()
        with patch.dict(os.environ, environment), patch.object(scheduled, 'ROOT', self.root), \
                patch.object(scheduled.search_frontier, 'ROOT', self.root), patch.object(scheduled, 'ActionsAPI', return_value=api), \
                patch.object(scheduled, 'GLOBAL_TARGET', 1502), patch.object(scheduled.subprocess, 'Popen', side_effect=child):
            self.assertEqual(scheduled.orchestrate(second, execution_source=execution), 0)
        resumed = json.loads((second / 'checkpoint/receipt.json').read_text())
        self.assertEqual(resumed['new_successful_scans'], 1)
        self.assertEqual(resumed['retained_counts']['successful_readme_scans'], 1501)
        self.assertEqual(resumed['bootstrap_origins'], receipt['bootstrap_origins'])
        self.assertNotIn('manual_seed_import', resumed)
        self.assertEqual(resumed['restored_run_id'], 20)

    def test_public_or_scheduled_seed_import_and_unseeded_worker_stop_before_import(self):
        (self.root / 'data').mkdir(); scheduled.write_json(self.root / 'data/source-index.json', self.doc)
        environment = {'GITHUB_REPOSITORY': 'example/worker', 'DEFAULT_BRANCH': 'main', 'GITHUB_EVENT_NAME': 'workflow_dispatch',
                       'GITHUB_REF': 'refs/heads/main', 'GITHUB_RUN_ID': '20', 'GITHUB_RUN_ATTEMPT': '1',
                       'GITHUB_SHA': 'd' * 40, 'GH_TOKEN': 'ephemeral-test-value'}
        api = FakeAPI([], {}); original_get = api.get
        api.get = lambda path: {'private': False, 'full_name': 'example/worker'} if path == '' else original_get(path)
        execution = {'repository': 'reacher-z/Awesome-REA', 'commit': 'e' * 40}
        with patch.dict(os.environ, environment), patch.object(scheduled, 'ROOT', self.root), \
                patch.object(scheduled, 'ActionsAPI', return_value=api), \
                patch.object(seed, 'import_seed', side_effect=AssertionError('No seed read permitted')):
            with self.assertRaisesRegex(ValueError, 'private worker repository'):
                scheduled.orchestrate(self.root / '.cache/public', manual_seed=self.root / 'manifest.json', execution_source=execution)
            with patch.dict(os.environ, GITHUB_EVENT_NAME='schedule'), self.assertRaisesRegex(ValueError, 'explicit'):
                scheduled.orchestrate(self.root / '.cache/cron', manual_seed=self.root / 'manifest.json', execution_source=execution)
            with self.assertRaisesRegex(ValueError, 'explicit first seed'):
                scheduled.orchestrate(self.root / '.cache/empty', execution_source=execution)


if __name__ == '__main__':
    unittest.main()
