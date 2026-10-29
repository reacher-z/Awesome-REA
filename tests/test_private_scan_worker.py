"""A public-source pin must never turn private seed files into public artifacts."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import private_scan_worker as worker


class WorkerIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.scanner, self.private = self.root / 'scanner', self.root / 'worker'
        for directory in (self.scanner, self.private):
            directory.mkdir()
            subprocess.run(['git', 'init', '-q', str(directory)], check=True)
        (self.scanner / 'tracked.py').write_text('# exact public source\n')
        self.scanner_sha = self.commit(self.scanner)
        self.config = self.private / 'scanner.json'
        self.value = {'schema_version': 1, 'scanner_repository': 'reacher-z/Awesome-REA',
                      'scanner_revision': self.scanner_sha, 'worker_repository': 'example/private-worker',
                      'worker_repository_id': 1234}
        self.config.write_text(json.dumps(self.value))
        (self.private / 'bootstrap').mkdir()
        filenames = ['scan-seed-checkpoint.json.gz', 'scan-seed-frontier.json.gz']
        (self.private / 'bootstrap/manifest.json').write_text(json.dumps({'files': {name: {} for name in filenames}}))
        for name in filenames:
            (self.private / 'bootstrap' / name).write_bytes(b'offline fixture; orchestrator is mocked')
        self.worker_sha = self.commit(self.private)
        self.environment = {'GITHUB_REPOSITORY': 'example/private-worker', 'GITHUB_REPOSITORY_ID': '1234',
                            'GITHUB_EVENT_NAME': 'workflow_dispatch', 'DEFAULT_BRANCH': 'main',
                            'GITHUB_REF': 'refs/heads/main', 'GITHUB_SHA': self.worker_sha,
                            'GH_TOKEN': 'ephemeral-offline-test'}
        self.actual = {'id': 1234, 'full_name': 'example/private-worker', 'private': True,
                       'archived': False, 'disabled': False, 'default_branch': 'main'}

    def commit(self, directory):
        subprocess.run(['git', '-C', str(directory), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(directory), '-c', 'user.name=Offline test', '-c',
                        'user.email=offline@example.invalid', 'commit', '-qm', 'Fixture'], check=True)
        return worker.git_value(directory, 'rev-parse', 'HEAD')

    def invoke(self, *, seed=False, bootstrap=False):
        with patch.dict(os.environ, self.environment), patch.object(worker.scheduled, 'ROOT', self.scanner), \
                patch.object(worker.scheduled, 'ActionsAPI') as api, \
                patch.object(worker.scheduled, 'orchestrate', return_value=0) as orchestrate:
            api.return_value.get.return_value = self.actual
            code = worker.run_worker(self.config, self.scanner / '.cache/run',
                                     seed_manifest=self.private / 'bootstrap/manifest.json' if seed else None,
                                     bootstrap_only=bootstrap)
            return code, api, orchestrate

    def test_clean_pinned_checkouts_and_actual_private_id_are_required_before_import(self):
        code, api, orchestrate = self.invoke(seed=True, bootstrap=True)
        self.assertEqual(code, 0)
        self.assertEqual(api.call_args.args, ('example/private-worker', self.environment['GH_TOKEN']))
        self.assertEqual(api.return_value.get.call_args.args, ('',))
        self.assertEqual(orchestrate.call_args.kwargs, {
            'manual_seed': self.private / 'bootstrap/manifest.json', 'bootstrap_only': True,
            'execution_source': {'repository': 'reacher-z/Awesome-REA', 'commit': self.scanner_sha}})
        self.assertNotIn(self.environment['GH_TOKEN'], str(orchestrate.call_args))

    def test_public_reassigned_archived_or_wrong_default_repository_never_runs(self):
        for changed in ({'private': False}, {'private': None}, {'id': 5678}, {'id': True},
                        {'full_name': 'other/worker'}, {'archived': True}, {'disabled': True}, {'default_branch': 'other'}):
            with self.subTest(changed=changed):
                original = self.actual; self.actual = {**original, **changed}
                with self.assertRaises(ValueError):
                    self.invoke(seed=True)
                self.actual = original

    def test_dirty_source_dirty_config_or_unpinned_checkout_stops_before_api(self):
        with patch.object(worker.scheduled, 'ActionsAPI', side_effect=AssertionError('No API request permitted')):
            (self.scanner / 'tracked.py').write_text('# changed\n')
            with self.assertRaisesRegex(ValueError, 'clean pinned'):
                with patch.dict(os.environ, self.environment), patch.object(worker.scheduled, 'ROOT', self.scanner):
                    worker.run_worker(self.config, self.scanner / '.cache/run')
            (self.scanner / 'tracked.py').write_text('# exact public source\n')
            self.config.write_text(json.dumps(self.value) + '\n')
            with self.assertRaisesRegex(ValueError, 'clean run'):
                with patch.dict(os.environ, self.environment), patch.object(worker.scheduled, 'ROOT', self.scanner):
                    worker.run_worker(self.config, self.scanner / '.cache/run')
            self.config.write_text(json.dumps({**self.value, 'scanner_revision': 'a' * 40}))
            with self.assertRaisesRegex(ValueError, 'clean pinned'):
                with patch.dict(os.environ, self.environment), patch.object(worker.scheduled, 'ROOT', self.scanner):
                    worker.run_worker(self.config, self.scanner / '.cache/run')

    def test_schedule_cannot_import_and_nondefault_or_wrong_worker_context_stops(self):
        for changes in ({'GITHUB_EVENT_NAME': 'pull_request'}, {'GITHUB_REF': 'refs/heads/other'},
                        {'GITHUB_REPOSITORY_ID': '5678'}, {'GITHUB_REPOSITORY': 'other/worker'},
                        {'GITHUB_SHA': 'a' * 40}, {'GITHUB_EVENT_NAME': 'schedule'}):
            with self.subTest(changes=changes):
                original = self.environment; self.environment = {**original, **changes}
                with self.assertRaises(ValueError):
                    self.invoke(seed=True)
                self.environment = original

    def test_manifest_location_runtime_cache_and_bootstrap_flag_are_bounded(self):
        with patch.dict(os.environ, self.environment), patch.object(worker.scheduled, 'ROOT', self.scanner), \
                patch.object(worker.scheduled, 'ActionsAPI', side_effect=AssertionError('No API request permitted')):
            with self.assertRaisesRegex(ValueError, 'bootstrap manifest'):
                worker.run_worker(self.config, self.scanner / '.cache/run', seed_manifest=self.private / 'other.json')
            with self.assertRaisesRegex(ValueError, 'requires a seed'):
                worker.run_worker(self.config, self.scanner / '.cache/run', bootstrap_only=True)
            with self.assertRaisesRegex(ValueError, 'ignored scanner cache'):
                worker.run_worker(self.config, self.scanner / 'data/run')

    def test_config_unknown_duplicate_or_placeholder_values_fail_without_echoing(self):
        for changes in ({'scanner_revision': None}, {'scanner_revision': 'main'}, {'worker_repository_id': True},
                        {'scanner_repository': 'other/code'}, {'token': 'hidden-value'}, {'schema_version': True}):
            with self.subTest(changes=list(changes)):
                self.config.write_text(json.dumps({**self.value, **changes}))
                with self.assertRaises(ValueError) as raised:
                    worker.validate_config(self.config)
                self.assertNotIn('hidden-value', str(raised.exception))
        self.config.write_text('{"schema_version":1,"schema_version":1}')
        with self.assertRaises(ValueError):
            worker.validate_config(self.config)

    def test_untracked_scanner_code_or_ignored_worker_seed_cannot_claim_pinned_origin(self):
        (self.scanner / 'shadow.py').write_text('# must not run\n')
        with self.assertRaisesRegex(ValueError, 'clean pinned'):
            self.invoke(seed=True)
        (self.scanner / 'shadow.py').unlink()
        # Even ignored untracked files must be bound to a tracked HEAD object.
        (self.private / '.gitignore').write_text('scanner.json\nbootstrap/\n')
        subprocess.run(['git', '-C', str(self.private), 'rm', '-q', '--cached', 'scanner.json'], check=True)
        self.environment['GITHUB_SHA'] = self.commit(self.private)
        with self.assertRaises(subprocess.CalledProcessError):
            self.invoke(seed=True)

    def test_gzip_and_manifest_must_be_tracked_even_if_ignored(self):
        (self.private / '.gitignore').write_text('bootstrap/\n')
        subprocess.run(['git', '-C', str(self.private), 'rm', '-q', '--cached',
                        'bootstrap/scan-seed-checkpoint.json.gz'], check=True)
        self.environment['GITHUB_SHA'] = self.commit(self.private)
        with self.assertRaises(subprocess.CalledProcessError):
            self.invoke(seed=True)


if __name__ == '__main__':
    unittest.main()
