"""A raw legacy capture cannot consume the verified-README campaign quota."""
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import scheduled_source_scan as scheduled
from test_scheduled_source_scan import FakeAPI, artifact, paired_archive, record, run, small_frontier, snapshot
from test_scan_seed import SeedFixture


def mixed_snapshot():
    document = snapshot(range(1, 1502))
    document['resources'][0] = record(1, integrity=None)
    document['resources'][1] = record(2, integrity=False)
    return document


def qualification_receipt(document, *, bootstrap=False):
    integrity = scheduled.integrity_counts(document)
    return {'goal_basis': scheduled.GOAL_BASIS, 'retained_counts': scheduled.counts(document),
            'counts': scheduled.counts(document), 'retained_integrity_counts': integrity,
            'integrity_counts': dict(integrity), 'new_qualified_successful_scans': 0,
            'new_successful_scans': 0, 'planned_new_successes': 0 if bootstrap else 2,
            'global_target_successes': 1501, 'new_success_limit': 1000,
            'global_target_reached': False, 'target_reached': bootstrap,
            'run_target_reached': bootstrap, 'outcome': 'bootstrap-imported' if bootstrap else 'partial'}


class QualificationTests(unittest.TestCase):
    def test_raw_160k_including_unknown_and_mismatch_still_needs_50_verified_reads(self):
        # Exercise the actual 160k boundary; no source records or flags are changed.
        document = {'resources': ([{'readme_git_sha_matches_content': True}] * 159950
                                  + [{}] * 49 + [{'readme_git_sha_matches_content': False}])}
        self.assertEqual(len(document['resources']), 160000)
        result = scheduled.integrity_counts(document)
        self.assertEqual(result, {'qualified': 159950, 'legacy_unknown': 49, 'mismatched': 1})
        self.assertEqual(scheduled.planned_successes(result['qualified']), 50)
        self.assertEqual(scheduled.planned_successes(160000), 0)
        for invalid in (1, 0, None, 'true'):
            with self.subTest(flag=invalid), self.assertRaises(ValueError):
                scheduled.integrity_counts({'resources': [{'readme_git_sha_matches_content': invalid}]})

    def test_new_receipt_is_all_or_none_and_rejects_forged_qualification_arithmetic(self):
        document = mixed_snapshot()
        good = qualification_receipt(document)
        scheduled.validate_integrity_receipt(good, document)
        scheduled.validate_integrity_receipt({'counts': scheduled.counts(document)}, document)
        mutations = {
            'partial group': lambda value: value.pop('retained_integrity_counts'),
            'unknown basis': lambda value: value.update(goal_basis='raw-captures'),
            'negative count': lambda value: value['integrity_counts'].update(legacy_unknown=-1),
            'boolean count': lambda value: value['integrity_counts'].update(mismatched=True),
            'missing count': lambda value: value['integrity_counts'].pop('legacy_unknown'),
            'extra count': lambda value: value['integrity_counts'].update(unchecked=0),
            'false global completion': lambda value: value.update(global_target_reached=True),
            'raw-count stop': lambda value: value.update(planned_new_successes=0, target_reached=True, run_target_reached=True),
            'invented qualified addition': lambda value: value.update(new_qualified_successful_scans=1),
            'synthetic legacy upgrade': lambda value: value['integrity_counts'].update(qualified=1500, legacy_unknown=0),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                changed = copy.deepcopy(good)
                mutate(changed)
                with self.assertRaises(ValueError):
                    scheduled.validate_integrity_receipt(changed, document)

    def test_receipt_counts_cannot_disagree_with_actual_checkpoint_flags(self):
        document = mixed_snapshot()
        receipt = qualification_receipt(document, bootstrap=True)
        for key in ('retained_integrity_counts', 'integrity_counts'):
            receipt[key].update(qualified=1500, legacy_unknown=0)
        # Arithmetic alone is coherent, but the frozen checkpoint has only 1499.
        scheduled.validate_integrity_receipt(receipt)
        with self.assertRaisesRegex(ValueError, 'checkpoint records'):
            scheduled.validate_integrity_receipt(receipt, document)


class RuntimeQualificationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / 'data').mkdir()
        self.document = mixed_snapshot()
        scheduled.write_json(self.root / 'data/source-index.json', self.document)
        self.environment = {'GITHUB_REPOSITORY': 'example/catalog', 'DEFAULT_BRANCH': 'main',
                            'GITHUB_REF': 'refs/heads/main', 'GITHUB_RUN_ID': '20', 'GITHUB_RUN_ATTEMPT': '1',
                            'GITHUB_SHA': 'd' * 40, 'GH_TOKEN': 'ephemeral-offline-test',
                            'GITHUB_OUTPUT': str(self.root / 'outputs'), 'GITHUB_STEP_SUMMARY': str(self.root / 'summary')}

    def legacy_pair(self):
        def raw_goal(receipt):
            receipt.update(global_target_successes=1501, global_target_reached=True,
                           planned_new_successes=0, new_successful_scans=0, target_reached=True)
        raw = paired_archive(self.document, small_frontier(1, acknowledged=True), mutate_receipt=raw_goal)
        previous_artifact = artifact(digest='sha256:' + hashlib.sha256(raw).hexdigest(),
                                     expires_at='2099-01-01T00:00:00Z')
        api = FakeAPI([], {})
        api.download = lambda suffix, path: path.write_bytes(raw)
        return api, previous_artifact

    def orchestrate(self, child, *, name='run', target=1501):
        api, previous_artifact = self.legacy_pair()
        directory = self.root / '.cache' / name
        with patch.dict(os.environ, self.environment), patch.object(scheduled, 'ROOT', self.root), \
                patch.object(scheduled.search_frontier, 'ROOT', self.root), patch.object(scheduled, 'GLOBAL_TARGET', target), \
                patch.object(scheduled, 'ActionsAPI', return_value=api), \
                patch.object(scheduled, 'select_checkpoint', return_value=(run(), previous_artifact)), \
                patch.object(scheduled.subprocess, 'Popen', side_effect=child):
            result = scheduled.orchestrate(directory)
        return result, directory

    def test_legacy_raw_at_goal_pair_still_collects_two_and_preserves_original_evidence(self):
        def child(command, **kwargs):
            seed = json.loads(Path(command[command.index('--seed') + 1]).read_text())
            self.assertEqual(seed['resources'], self.document['resources'])
            final = snapshot(range(1, 1504))
            final['resources'][:1501] = copy.deepcopy(seed['resources'])
            scheduled.write_json(Path(command[command.index('--output') + 1]), final)
            return SimpleNamespace(wait=lambda timeout: 0)
        result, directory = self.orchestrate(child)
        self.assertEqual(result, 0)
        receipt = json.loads((directory / 'checkpoint/receipt.json').read_text())
        self.assertEqual(receipt['counts']['successful_readme_scans'], 1503)
        self.assertEqual(receipt['retained_integrity_counts'], {'qualified': 1499, 'legacy_unknown': 1, 'mismatched': 1})
        self.assertEqual(receipt['integrity_counts'], {'qualified': 1501, 'legacy_unknown': 1, 'mismatched': 1})
        self.assertEqual(receipt['planned_new_successes'], 2)
        self.assertEqual(receipt['new_qualified_successful_scans'], 2)
        self.assertTrue(receipt['global_target_reached'])
        final = json.loads((directory / 'checkpoint/checkpoint.json').read_text())
        self.assertEqual(final['resources'][:1501], self.document['resources'])
        cursor = json.loads((directory / 'checkpoint/frontier.json').read_text())
        self.assertEqual(cursor['candidates']['1']['checkpoint_sha256'], 'a' * 64)
        self.assertIn('legacy integrity unknown: **1**', (self.root / 'summary').read_text())

    def test_at_qualified_goal_reuses_pair_without_changing_unknown_or_mismatched_records(self):
        def no_child(*args, **kwargs):
            raise AssertionError('No child should start once qualified captures reach the goal')
        result, directory = self.orchestrate(no_child, target=1499)
        self.assertEqual(result, 0)
        receipt = json.loads((directory / 'summary.json').read_text())
        self.assertEqual(receipt['integrity_counts'], {'qualified': 1499, 'legacy_unknown': 1, 'mismatched': 1})
        self.assertEqual(receipt['counts']['successful_readme_scans'], 1501)
        self.assertTrue(receipt['global_target_reached'])
        self.assertEqual(receipt['new_qualified_successful_scans'], 0)
        self.assertFalse((directory / 'checkpoint').exists())
        self.assertEqual((self.root / 'outputs').read_text(), 'checkpoint_ready=false\n')
        restored = json.loads((directory / 'restored/checkpoint.json').read_text())
        self.assertEqual(restored, self.document)

    def test_new_unqualified_success_is_rejected_before_artifact_is_enabled(self):
        def child(command, **kwargs):
            final = snapshot(range(1, 1503))
            final['resources'][:1501] = copy.deepcopy(self.document['resources'])
            final['resources'][-1] = record(1502, integrity=None)
            scheduled.write_json(Path(command[command.index('--output') + 1]), final)
            return SimpleNamespace(wait=lambda timeout: 1)
        with self.assertRaisesRegex(ValueError, 'without explicit verified'):
            self.orchestrate(child)
        self.assertFalse((self.root / 'outputs').exists())
        self.assertFalse((self.root / '.cache/run/checkpoint/receipt.json').exists())

    def test_child_target_uses_raw_plus_qualified_remaining_and_keeps_seed_bytes(self):
        seed = self.root / 'data/source-index.json'
        cursor = self.root / '.cache/frontier.json'
        output = self.root / '.cache/output.json'
        scheduled.write_json(cursor, small_frontier())
        before = seed.read_bytes()
        with patch.dict(os.environ, self.environment), patch.object(scheduled, 'GLOBAL_TARGET', 1501), \
                patch.object(scheduled, 'run_scan', return_value=1) as scan:
            self.assertEqual(scheduled.scanner_child(seed, output, cursor), 1)
        args = scan.call_args.args[1]
        self.assertEqual(args.target, 1503)
        self.assertEqual(scan.call_args.args[2]['resources'], self.document['resources'])
        self.assertEqual(seed.read_bytes(), before)


class BootstrapQualificationTests(SeedFixture):
    def test_bootstrap_reports_mixed_integrity_without_scans_or_seed_byte_changes(self):
        self.doc['resources'][0] = record(1, integrity=None)
        self.doc['resources'][1] = record(2, integrity=False)
        scheduled.write_json(self.checkpoint, self.doc)
        self.package_seed()
        (self.root / 'data').mkdir()
        scheduled.write_json(self.root / 'data/source-index.json', self.doc)
        api = FakeAPI([], {})
        original_get = api.get
        api.get = lambda path: {'private': True, 'full_name': 'example/worker'} if path == '' else original_get(path)
        environment = {'GITHUB_REPOSITORY': 'example/worker', 'DEFAULT_BRANCH': 'main',
                       'GITHUB_EVENT_NAME': 'workflow_dispatch', 'GITHUB_REF': 'refs/heads/main',
                       'GITHUB_RUN_ID': '20', 'GITHUB_RUN_ATTEMPT': '1', 'GITHUB_SHA': 'd' * 40,
                       'GH_TOKEN': 'ephemeral-offline-test', 'GITHUB_OUTPUT': str(self.root / 'outputs'),
                       'GITHUB_STEP_SUMMARY': str(self.root / 'summary')}
        directory = self.root / '.cache/bootstrap'
        with patch.dict(os.environ, environment), patch.object(scheduled, 'ROOT', self.root), \
                patch.object(scheduled.search_frontier, 'ROOT', self.root), patch.object(scheduled, 'GLOBAL_TARGET', 1501), \
                patch.object(scheduled, 'ActionsAPI', return_value=api), \
                patch.object(scheduled.subprocess, 'Popen', side_effect=AssertionError('Bootstrap must not scan')):
            self.assertEqual(scheduled.orchestrate(directory, manual_seed=self.package / 'manifest.json',
                execution_source={'repository': 'reacher-z/Awesome-REA', 'commit': 'e' * 40}, bootstrap_only=True), 0)
        receipt = json.loads((directory / 'checkpoint/receipt.json').read_text())
        self.assertEqual(receipt['outcome'], 'bootstrap-imported')
        self.assertEqual(receipt['new_qualified_successful_scans'], 0)
        self.assertEqual(receipt['planned_new_successes'], 0)
        self.assertFalse(receipt['global_target_reached'])
        self.assertEqual(receipt['integrity_counts'], {'qualified': 1499, 'legacy_unknown': 1, 'mismatched': 1})
        self.assertEqual(receipt['integrity_counts'], receipt['retained_integrity_counts'])
        self.assertEqual((directory / 'checkpoint/checkpoint.json').read_bytes(), self.checkpoint.read_bytes())


if __name__ == '__main__':
    unittest.main()
