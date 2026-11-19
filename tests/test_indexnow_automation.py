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
import build_manifest
import indexnow_automation as automation
import submit_indexnow as indexnow

SHA = 'a' * 40
NEWER = 'b' * 40


class FakeGitHub:
    def __init__(self, *, head=SHA, runs=(), artifacts=None, archives=None):
        self.head, self.runs = head, list(runs)
        self.artifacts, self.archives, self.calls = artifacts or {}, archives or {}, []

    def get(self, suffix):
        self.calls.append(suffix)
        if suffix == '':
            return {'default_branch': 'main'}
        if suffix == 'branches/main':
            return {'commit': {'sha': self.head}}
        if suffix.startswith('actions/workflows/indexnow.yml/runs'):
            return {'workflow_runs': self.runs if suffix.endswith('&page=1') else []}
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

    def wait(self, github, polls, **kwargs):
        """polls: one dict per poll, the last repeating; 'commit' is source-commit.txt at the origin, 'origin' and
        'edge' are build-manifest.json at the origin and through the edge cache. A value may be an exception."""
        clock, uncached = Clock(), []

        def fetch(url, limit):
            state = polls[min(int(clock() // automation.POLL_SECONDS), len(polls) - 1)]
            name, _, query = url.removeprefix('https://awesomerea.org/').partition('?')
            if query:
                self.assertRegex(query, r'^indexnow=[0-9a-f]{16}$')
                uncached.append(url)
                if name.startswith('previews/'):
                    value = state.get('previews', {}).get(name, OSError('missing'))
                else:
                    value = state['commit'] if name == 'source-commit.txt' else state['origin']
            else:
                self.assertEqual(name, 'build-manifest.json', 'only the manifest is read through the edge cache')
                value = state['edge']
            if isinstance(value, Exception):
                raise value
            return value
        with redirect_stdout(StringIO()):
            state = automation.wait_for_deployment(SHA, self.dist, github=github, fetch=fetch, clock=clock,
                                                   sleep=clock.sleep, **kwargs)
        self.assertEqual(len(set(uncached)), len(uncached), 'every origin read needs a query no cache has seen')
        return state

    def served(self, commit=SHA, origin=None, edge=None):
        return {'commit': commit.encode() + b'\n' if isinstance(commit, str) else commit,
                'origin': origin, 'edge': edge if edge is not None else b'{"files": {"previous": 1}}\n'}

    def test_live_once_origin_and_edge_serve_this_build(self):
        github = FakeGitHub()
        self.assertEqual(self.wait(github, [self.served(origin=self.manifest, edge=self.manifest)]), 'live')
        self.assertEqual(github.calls, [])
        old = b'{"files": {"old": 1}}\n'
        self.assertEqual(self.wait(FakeGitHub(), [
            self.served(OSError('reset')), self.served('c' * 40), self.served(origin=old), self.served(origin=OSError('reset')),
            self.served(origin=self.manifest), self.served(origin=self.manifest, edge=self.manifest)]), 'live')

    def test_a_purge_that_never_comes_defers(self):
        self.assertEqual(self.wait(FakeGitHub(), [self.served(origin=self.manifest)], wait_seconds=120), 'pending')

    def test_another_commit_while_main_moved_on_supersedes(self):
        self.assertEqual(self.wait(FakeGitHub(head=NEWER), [self.served(NEWER)]), 'superseded')
        self.assertEqual(self.wait(FakeGitHub(head=NEWER), [self.served('c' * 40)]), 'superseded')

    def test_an_unreadable_site_never_supersedes(self):
        github = FakeGitHub(head=NEWER)
        self.assertEqual(self.wait(github, [self.served(OSError('reset'))], wait_seconds=120), 'pending')
        self.assertEqual(github.calls, [])

    def test_an_unpublished_commit_is_deferred_and_other_bytes_fail(self):
        self.assertEqual(self.wait(FakeGitHub(), [self.served('c' * 40)], wait_seconds=120), 'pending')
        other = b'{"files": {"other": 1}}\n'
        with self.assertRaisesRegex(ValueError, 'reproducible'):
            self.wait(FakeGitHub(), [self.served(origin=other)])
        # A manifest that stays unreadable is not evidence of another build.
        self.assertEqual(self.wait(FakeGitHub(), [self.served(origin=OSError('reset'))]), 'pending')
        # Other bytes that turn into this build before the propagation allowance runs out are fine.
        allowance = automation.PROPAGATION_SECONDS // automation.POLL_SECONDS
        self.assertEqual(self.wait(FakeGitHub(), [self.served(origin=other)] * allowance
                                   + [self.served(origin=self.manifest, edge=self.manifest)]), 'live')
        with self.assertRaises(ValueError):
            automation.wait_for_deployment('main', self.dist, github=FakeGitHub())

    def test_the_build_waits_until_the_site_serves_the_commit(self):
        clock, sha = Clock(), 'a' * 40
        served = [b'b' * 40, OSError('down'), sha.encode()]

        def fetch(url, limit):
            value = served[min(int(clock() // automation.POLL_SECONDS), len(served) - 1)]
            if isinstance(value, Exception):
                raise value
            return value
        self.assertTrue(automation.wait_until_served(sha, fetch=fetch, clock=clock, sleep=clock.sleep))
        clock.now = 0
        self.assertFalse(automation.wait_until_served('c' * 40, fetch=fetch, clock=clock, sleep=clock.sleep,
                                                      wait_seconds=100))

    def test_a_build_that_differs_only_in_preview_images_takes_the_served_images(self):
        (self.dist / 'index.html').write_bytes(b'<!doctype html><title>Home</title>')
        (self.dist / 'sitemap.xml').write_bytes(b'<urlset></urlset>')
        (self.dist / 'previews').mkdir()
        (self.dist / 'previews' / 'a.png').write_bytes(b'built image')
        built_manifest = build_manifest.write_build_manifest(self.dist)
        built = (self.dist / 'build-manifest.json').read_bytes()
        image = b'served image'
        served_manifest = json.loads(built)
        served_manifest['files']['previews/a.png'] = {'sha256': hashlib.sha256(image).hexdigest(), 'bytes': len(image)}
        served = build_manifest.manifest_bytes(served_manifest)

        # The edge has not caught up, the image is unreadable, or it does not match the served manifest: DIST is kept.
        for previews, edge in (({'previews/a.png': image}, None), ({}, served), ({'previews/a.png': b'other'}, served)):
            self.assertEqual(self.wait(FakeGitHub(), [{**self.served(origin=served, edge=edge), 'previews': previews}],
                                       wait_seconds=120), 'pending')
            self.assertEqual((self.dist / 'build-manifest.json').read_bytes(), built)
            self.assertEqual(build_manifest.read_build_manifest(self.dist), built_manifest)

        self.assertEqual(self.wait(FakeGitHub(), [{**self.served(origin=served, edge=served),
                                                   'previews': {'previews/a.png': image}}]), 'live')
        self.assertEqual((self.dist / 'previews' / 'a.png').read_bytes(), image)
        self.assertEqual(build_manifest.read_build_manifest(self.dist), served_manifest)

        # Any other difference, such as a page, is another build.
        (self.dist / 'previews' / 'a.png').write_bytes(b'built image')
        (self.dist / 'build-manifest.json').write_bytes(built)
        page = json.loads(served)
        page['files']['index.html']['html_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'reproducible'):
            self.wait(FakeGitHub(), [{**self.served(origin=build_manifest.manifest_bytes(page)),
                                      'previews': {'previews/a.png': image}}])
        self.assertEqual((self.dist / 'build-manifest.json').read_bytes(), built)
        self.assertFalse(automation.differs_only_in_previews(b'not json', built))
        self.assertFalse(automation.differs_only_in_previews(b'{"files": {}, "schema_version": 2}', b'{"files": {}}'))

    def test_served_thumbnails_count_as_preview_images(self):
        image = b'webp bytes'
        entry = {'sha256': hashlib.sha256(image).hexdigest(), 'bytes': len(image)}
        served = json.dumps({'files': {'previews/thumbs/a.webp': entry}}).encode()
        built = json.dumps({'files': {'previews/thumbs/a.webp': {'sha256': '0' * 64, 'bytes': 1}}}).encode()
        self.assertEqual(automation.served_previews(served, built, lambda url, limit: image), {'previews/thumbs/a.webp': image})
        nested = json.dumps({'files': {'previews/thumbs/deeper/a.webp': entry}}).encode()
        self.assertIsNone(automation.served_previews(nested, built, lambda url, limit: image))

    def test_a_deferred_wait_warns_and_succeeds(self):
        output = StringIO()
        with patch.object(automation, 'wait_for_deployment', return_value='pending'), \
                patch.object(sys, 'argv', ['indexnow_automation.py', 'wait', SHA, str(self.dist)]), \
                patch.dict('os.environ', {'GITHUB_OUTPUT': ''}), redirect_stdout(output):
            self.assertEqual(automation.main(), 0)
        self.assertIn('state=pending', output.getvalue())
        self.assertIn('::warning::', output.getvalue())


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
        manifest = json.dumps({'schema_version': 1, 'algorithm': 'sha256', 'html_normalization': automation.HTML_NORMALIZATION,
                               'files': {}}).encode()
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

    def test_the_baseline_is_found_past_a_full_page_of_runs_without_receipts(self):
        manifest = json.dumps({'schema_version': 1, 'algorithm': 'sha256', 'html_normalization': automation.HTML_NORMALIZATION,
                               'files': {}}).encode()
        empty = [{'id': 1000 + i, 'head_branch': 'main', 'event': 'workflow_dispatch', 'path': '.github/workflows/indexnow.yml'}
                 for i in range(100)]
        receipt_run = {'id': 900, 'head_branch': 'main', 'event': 'schedule', 'path': '.github/workflows/indexnow.yml'}

        class Paged(FakeGitHub):
            def get(self, suffix):
                if suffix.startswith('actions/workflows/indexnow.yml/runs'):
                    self.calls.append(suffix)
                    return {'workflow_runs': {'1': empty, '2': [receipt_run]}.get(suffix.rsplit('=', 1)[1], [])}
                return super().get(suffix)
        github = Paged(artifacts={900: [{'id': 9, 'name': 'indexnow-receipt', 'expired': False, 'size_in_bytes': 10}]},
                       archives={'actions/artifacts/9/zip': receipt_archive(manifest)})
        with TemporaryDirectory() as directory, redirect_stdout(StringIO()):
            self.assertEqual(automation.previous_receipt(Path(directory), github=github), hashlib.sha256(manifest).hexdigest())

    def test_a_baseline_in_another_manifest_format_falls_back_to_a_full_notification(self):
        older = json.dumps({'schema_version': 1, 'algorithm': 'sha256', 'html_normalization': 'cloudflare-public-html-v3',
                            'files': {}}).encode()
        runs = [{'id': 10, 'head_branch': 'main', 'event': 'schedule', 'path': '.github/workflows/indexnow.yml'}]
        github = FakeGitHub(runs=runs, artifacts={10: [{'id': 100, 'name': 'indexnow-receipt', 'expired': False, 'size_in_bytes': 10}]},
                            archives={'actions/artifacts/100/zip': receipt_archive(older)})
        output = StringIO()
        with TemporaryDirectory() as directory, redirect_stdout(output):
            self.assertEqual(automation.previous_receipt(Path(directory), github=github), '')
        self.assertIn('another manifest format', output.getvalue())


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
                         [('contents', 'read'), ('actions', 'read')])
        self.assertIn("github.ref == format('refs/heads/{0}', github.event.repository.default_branch)", self.text)

    def test_builds_like_the_publication_waits_then_submits_and_keeps_the_receipt(self):
        build = self.text.index('python3 scripts/build_production.py --publish')
        # The same pinned Pillow as the publication builds, so the preview thumbnails match.
        pillow = self.text.index('--require-hashes -r scripts/publish-requirements.txt')
        self.assertLess(pillow, build)
        self.assertRegex((ROOT / 'scripts/publish-requirements.txt').read_text(encoding='utf-8'), r'(?m)^pillow==[0-9.]+ \\$')
        wait = self.text.index('python3 scripts/indexnow_automation.py wait "$SHA" dist')
        previous = self.text.index('python3 scripts/indexnow_automation.py previous')
        submit = self.text.index('python3 scripts/submit_indexnow.py "${args[@]}"')
        upload = self.text.index('name: indexnow-receipt')
        self.assertLess(build, wait); self.assertLess(wait, previous); self.assertLess(previous, submit); self.assertLess(submit, upload)
        self.assertIn('args=(--submit --automatic --receipt .cache/indexnow/receipt/receipt.json)', self.text)
        for step in self.text[wait:].split('\n      - ')[1:]:
            self.assertIn("if: ${{ steps.deploy.outputs.state == 'live' }}", step)
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
