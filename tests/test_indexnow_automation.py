"""The unattended IndexNow run: waiting for the deployment, receipts, the automatic delta and the workflow."""
from contextlib import redirect_stdout
import hashlib
import io
from io import StringIO
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import indexnow_automation as automation
import submit_indexnow as indexnow

SHA = 'a' * 40
NEWER = 'b' * 40


class FakeGitHub:
    def __init__(self, *, checks=(), head=SHA, runs=(), artifacts=None, archives=None):
        self.checks, self.head, self.runs = list(checks), head, list(runs)
        self.artifacts, self.archives, self.calls = artifacts or {}, archives or {}, []

    def get(self, suffix):
        self.calls.append(suffix)
        if suffix == '':
            return {'default_branch': 'main'}
        if suffix == 'branches/main':
            return {'commit': {'sha': self.head}}
        if suffix.startswith('commits/'):
            state = self.checks.pop(0) if len(self.checks) > 1 else (self.checks[0] if self.checks else None)
            if state is None:
                return {'check_runs': []}
            status, conclusion = ('in_progress', None) if state == 'pending' else ('completed', state)
            return {'check_runs': [{'id': 5, 'app': {'slug': 'cloudflare-workers-and-pages'}, 'status': status, 'conclusion': conclusion},
                                   {'id': 9, 'app': {'slug': 'other-app'}, 'status': 'completed', 'conclusion': 'failure'}]}
        if suffix.startswith('actions/workflows/indexnow.yml/runs'):
            return {'workflow_runs': self.runs}
        match = re.fullmatch(r'actions/runs/(\d+)/artifacts\?per_page=30', suffix)
        if match:
            return {'artifacts': self.artifacts.get(int(match[1]), [])}
        raise AssertionError(suffix)

    def download(self, suffix, path):
        self.calls.append(suffix)
        path.write_bytes(self.archives[suffix])


class Clock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


def receipt_archive(manifest: bytes, *, extra=None, digest=None):
    buffer = io.BytesIO()
    receipt = {'schema_version': 1, 'site': indexnow.ORIGIN, 'manifest_sha256': digest or hashlib.sha256(manifest).hexdigest(),
               'mode': 'delta', 'recorded_at': '2026-11-05T23:00:00Z'}
    with zipfile.ZipFile(buffer, 'w') as bundle:
        bundle.writestr('receipt.json', json.dumps(receipt))
        bundle.writestr('build-manifest.json', manifest)
        if extra:
            bundle.writestr(extra, b'x')
    return buffer.getvalue()


class WaitTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.dist = Path(self.temporary.name)
        self.manifest = b'{"files": {}}\n'
        (self.dist / 'build-manifest.json').write_bytes(self.manifest)

    def wait(self, github, served, **kwargs):
        clock = Clock()
        responses = list(served)

        def fetch(url, limit):
            self.assertEqual(url, 'https://awesomerea.org/build-manifest.json')
            value = responses.pop(0) if len(responses) > 1 else responses[0]
            if isinstance(value, Exception):
                raise value
            return value
        with redirect_stdout(StringIO()):
            return automation.wait_for_deployment(SHA, self.dist, github=github, fetch=fetch, clock=clock,
                                                  sleep=clock.sleep, **kwargs)

    def test_live_as_soon_as_the_deployment_serves_this_build(self):
        github = FakeGitHub(checks=['pending'])
        self.assertEqual(self.wait(github, [self.manifest]), 'live')
        self.assertEqual(github.calls, [])
        old = b'{"files": {"old": 1}}\n'
        self.assertEqual(self.wait(FakeGitHub(checks=['pending', 'pending', 'success']),
                                   [old, OSError('reset'), old, self.manifest]), 'live')

    def test_a_newer_commit_supersedes_and_a_failed_deployment_stops(self):
        old = b'{"files": {"old": 1}}\n'
        self.assertEqual(self.wait(FakeGitHub(checks=['success'], head=NEWER), [old]), 'superseded')
        self.assertEqual(self.wait(FakeGitHub(checks=['cancelled'], head=NEWER), [old]), 'superseded')
        with self.assertRaisesRegex(ValueError, 'failed deployment'):
            self.wait(FakeGitHub(checks=['failure']), [old])

    def test_a_deployment_that_does_not_reproduce_this_build_or_never_lands_fails(self):
        other = b'{"files": {"other": 1}}\n'
        with self.assertRaisesRegex(ValueError, 'reproducible'):
            self.wait(FakeGitHub(checks=['success']), [other])
        with self.assertRaisesRegex(ValueError, 'did not go live'):
            self.wait(FakeGitHub(checks=['pending']), [other], wait_seconds=120)
        with self.assertRaises(ValueError):
            automation.wait_for_deployment('main', self.dist, github=FakeGitHub())


class ReceiptTests(unittest.TestCase):
    def test_a_receipt_holds_exactly_its_manifest(self):
        manifest = b'{"schema_version": 1}\n'
        receipt, data = automation.read_receipt(receipt_archive(manifest))
        self.assertEqual(data, manifest)
        self.assertEqual(receipt['manifest_sha256'], hashlib.sha256(manifest).hexdigest())
        for archive in (receipt_archive(manifest, extra='other.txt'), receipt_archive(manifest, digest='0' * 64)):
            with self.assertRaises(ValueError):
                automation.read_receipt(archive)

    def test_the_newest_receipt_of_a_successful_default_branch_run_is_the_baseline(self):
        manifest = b'{"files": {}}\n'
        runs = [
            {'id': 30, 'head_branch': 'feature', 'event': 'workflow_dispatch', 'path': '.github/workflows/indexnow.yml'},
            {'id': 20, 'head_branch': 'main', 'event': 'pull_request', 'path': '.github/workflows/indexnow.yml'},
            {'id': 15, 'head_branch': 'main', 'event': 'schedule', 'path': '.github/workflows/indexnow.yml'},
            {'id': 10, 'head_branch': 'main', 'event': 'workflow_dispatch', 'path': '.github/workflows/indexnow.yml'},
        ]
        artifacts = {
            30: [{'id': 300, 'name': 'indexnow-receipt', 'expired': False, 'size_in_bytes': 10}],
            20: [{'id': 200, 'name': 'indexnow-receipt', 'expired': False, 'size_in_bytes': 10}],
            15: [{'id': 150, 'name': 'indexnow-receipt', 'expired': True, 'size_in_bytes': 10},
                 {'id': 151, 'name': 'other', 'expired': False, 'size_in_bytes': 10}],
            10: [{'id': 100, 'name': 'indexnow-receipt', 'expired': False, 'size_in_bytes': 10}],
        }
        github = FakeGitHub(runs=runs, artifacts=artifacts, archives={'actions/artifacts/100/zip': receipt_archive(manifest)})
        with TemporaryDirectory() as directory, redirect_stdout(StringIO()):
            target = Path(directory) / 'previous'
            digest = automation.previous_receipt(target, github=github, current_run='40')
            self.assertEqual(digest, hashlib.sha256(manifest).hexdigest())
            self.assertEqual((target / 'build-manifest.json').read_bytes(), manifest)
            self.assertFalse((target / 'receipt.zip').exists())
        self.assertNotIn('actions/artifacts/300/zip', github.calls)
        self.assertNotIn('actions/artifacts/200/zip', github.calls)
        with TemporaryDirectory() as directory, redirect_stdout(StringIO()):
            self.assertEqual(automation.previous_receipt(Path(directory), github=FakeGitHub(runs=[])), '')


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.text = (ROOT / '.github/workflows/indexnow.yml').read_text(encoding='utf-8')

    def test_triggers_concurrency_and_permissions(self):
        trigger = self.text.split('\non:\n', 1)[1].split('\npermissions:\n', 1)[0]
        self.assertIn('  workflow_dispatch:\n', trigger)
        self.assertRegex(trigger, r"\n  schedule:\n    - cron: '\d+ \*/3 \* \* \*'$")
        self.assertNotIn('pull_request', trigger)
        self.assertIn('\npermissions:\n  contents: read\n', self.text)
        self.assertIn('\nconcurrency:\n  group: indexnow\n  cancel-in-progress: false\n', self.text)
        job = self.text.split('\njobs:\n', 1)[1]
        permissions = re.search(r'\n    permissions:\n((?:      .*\n)+)', job)[1]
        self.assertEqual(re.findall(r'^      ([a-z-]+): ([a-z]+)$', permissions, re.MULTILINE),
                         [('contents', 'read'), ('checks', 'read'), ('actions', 'read')])
        self.assertIn("github.ref == format('refs/heads/{0}', github.event.repository.default_branch)", self.text)

    def test_builds_like_cloudflare_waits_then_submits_and_keeps_the_receipt(self):
        validate = (ROOT / '.github/workflows/validate.yml').read_text(encoding='utf-8')
        asset_url = re.search(r'build_production\.py (--fontawesome-assets-url \S+)', validate)[1]
        build = self.text.index('python3 scripts/build_site.py ' + asset_url)
        wait = self.text.index('python3 scripts/indexnow_automation.py wait "$SHA" dist')
        previous = self.text.index('python3 scripts/indexnow_automation.py previous')
        submit = self.text.index('python3 scripts/submit_indexnow.py "${args[@]}"')
        upload = self.text.index('name: indexnow-receipt')
        self.assertLess(build, wait); self.assertLess(wait, previous); self.assertLess(previous, submit); self.assertLess(submit, upload)
        self.assertIn('args=(--submit --automatic --receipt .cache/indexnow/receipt/receipt.json)', self.text)
        self.assertIn('persist-credentials: false', self.text)
        self.assertIn('git merge-base --is-ancestor HEAD "origin/$DEFAULT_BRANCH"', self.text)

    def test_inputs_reach_the_shell_only_through_env(self):
        for block in re.findall(r'run: \|\n((?:          .*\n|\n)+)', self.text) + re.findall(r'run: (.+)\n', self.text):
            self.assertNotIn('${{', block)

    def test_merges_and_ingests_start_it_with_the_merged_commit(self):
        merge = (ROOT / '.github/workflows/merge-pr.yml').read_text(encoding='utf-8')
        self.assertIn('gh workflow run indexnow.yml -R "$GITHUB_REPOSITORY" --ref "$DEFAULT_BRANCH" -f sha="$sha"', merge)
        self.assertIn("--jq 'select(.merged) | .merge_commit_sha'", merge)
        scan = (ROOT / '.github/workflows/source-scan.yml').read_text(encoding='utf-8')
        self.assertIn("if: ${{ steps.ingest.outputs.status == 'merged' }}", scan)
        self.assertIn('gh workflow run indexnow.yml -R "$GITHUB_REPOSITORY" --ref "$DEFAULT_BRANCH" -f sha="$MERGE_SHA"', scan)
        for text in (merge, scan):
            self.assertIn('|| echo "::warning::The IndexNow workflow did not start', text)


if __name__ == '__main__':
    unittest.main()
