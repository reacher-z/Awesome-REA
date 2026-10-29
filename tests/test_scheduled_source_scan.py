"""Scheduled discovery must retain evidence without promoting partial scans."""
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import scheduled_source_scan as scheduled
from validate import validate_source_index


def record(identifier, *, failed=False, name=None, integrity=True):
    name = name or f'example/repository-{identifier}'
    result = {'id': f'scan-{identifier}', 'full_name': name, 'url': 'https://github.com/' + name,
              'scan_status': 'failed' if failed else 'readme-scanned', 'observed_at': '2026-10-18T00:00:00Z'}
    if failed:
        result.update(reason='http-404', http_status=404)
    else:
        body = b'# Synthetic fixture\n'
        oid = hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()
        result.update(verification='automated-readme-scan', readme_url='https://github.com/' + name + '#readme',
                      readme_sha256=hashlib.sha256(body).hexdigest(), readme_bytes=len(body), targets=[], stars=0)
        if integrity is not None:
            result.update(readme_git_sha=oid if integrity else 'f' * 40,
                          readme_content_git_sha=oid, readme_git_sha_matches_content=integrity)
    return result


def snapshot(success=(1,), failed=(), pending=(), status='complete'):
    known = sorted(set(success) | set(failed) | set(pending))
    return {'meta': {'schema_version': 1, 'status': status, 'queries': [],
                     'successful_readme_scans': len(success), 'failed': len(failed),
                     'attempted_readme_scans': len(success) + len(failed),
                     'unique_repos': len(known), 'unattempted_candidates': len(known) - len(success) - len(failed),
                     'requested_successful_scans': len(success),
                     'discovered_repository_ids': [f'scan-{i}' for i in known]},
            'resources': [record(i) for i in success], 'failures': [record(i, failed=True) for i in failed]}


def run(identifier=12, attempt=1, **changes):
    return {'id': identifier, 'run_attempt': attempt, 'workflow_id': 42, 'status': 'completed',
            'head_branch': 'main', 'event': 'schedule', 'head_repository': {'full_name': 'example/catalog'},
            'head_sha': 'b' * 40, **changes}


def artifact(identifier=12, attempt=1, **changes):
    return {'id': 73, 'name': scheduled.ARTIFACT + '-' + str(attempt), 'expired': False,
            'size_in_bytes': 500, 'workflow_run': {'id': identifier}, **changes}


class FakeAPI:
    repository = 'example/catalog'

    def __init__(self, runs, artifacts, attempts=None):
        self.runs, self.artifacts, self.attempts, self.calls = runs, artifacts, attempts or {}, []

    def get(self, path):
        self.calls.append(path)
        if path == 'actions/workflows/source-scan.yml':
            return {'id': 42}
        if '/attempts/' in path:
            return self.attempts[int(path.rsplit('/', 1)[-1])]
        if '/runs?' in path:
            return {'workflow_runs': self.runs}
        if '/artifacts?' in path:
            identifier = int(path.split('/')[2])
            return {'artifacts': self.artifacts.get(identifier, [])}
        raise AssertionError(path)


class ReconciliationTests(unittest.TestCase):
    def test_canonical_supersession_keeps_per_id_old_hashes_once_in_scan_metadata(self):
        previous = snapshot((1,))
        canonical = snapshot((1, 2))
        canonical['resources'][0]['stars'] = 5
        merged, receipt = scheduled.reconcile(canonical, previous, 'a' * 64, 'b' * 64)
        self.assertEqual(receipt['mode'], 'canonical-covers-checkpoint')
        self.assertTrue(scheduled.retain_superseded_hashes(merged, receipt))
        stored = merged['meta']['checkpoint_reconciliations'][0]
        self.assertEqual(stored['superseded'][0]['checkpoint_record_sha256'], scheduled.digest(previous['resources'][0]))
        self.assertFalse(scheduled.retain_superseded_hashes(merged, {**receipt, 'checkpoint_sha256': 'c' * 64}))
        compact = scheduled.compact_reconciliation(receipt)
        self.assertNotIn('superseded', compact)
        self.assertEqual(compact['superseded_count'], 1)

    def test_canonical_only_if_all_successes_and_pending_ids_are_covered(self):
        published, checkpoint = snapshot((1, 2), pending=(3,)), snapshot((1,), pending=(4,))
        merged, receipt = scheduled.reconcile(published, checkpoint, 'c', 'p')
        self.assertEqual(receipt['mode'], 'union')
        self.assertEqual(scheduled.known_ids(merged), {'scan-1', 'scan-2', 'scan-3', 'scan-4'})
        self.assertEqual(merged['meta']['successful_readme_scans'], 2)
        self.assertEqual(merged['meta']['unattempted_candidates'], 2)
        covered, receipt = scheduled.reconcile(published, snapshot((1,), pending=(3,)), 'c', 'p')
        self.assertEqual(receipt['mode'], 'canonical-covers-checkpoint')
        self.assertEqual(covered, published)

    def test_union_preserves_unpublished_objects_and_prefers_success_to_failure(self):
        canonical = snapshot((1, 2), failed=(3,), pending=(5,))
        previous = snapshot((1, 3, 4), failed=(2,), pending=(6,))
        previous['resources'][0]['stars'] = 10
        before = copy.deepcopy(previous)
        merged, receipt = scheduled.reconcile(canonical, previous, 'c', 'p')
        self.assertEqual(previous, before)
        self.assertEqual({r['id'] for r in merged['resources']}, {'scan-1', 'scan-2', 'scan-3', 'scan-4'})
        self.assertEqual(merged['failures'], [])
        self.assertEqual(next(r for r in merged['resources'] if r['id'] == 'scan-4'), previous['resources'][2])
        self.assertEqual(next(r for r in merged['resources'] if r['id'] == 'scan-1'), canonical['resources'][0])
        self.assertEqual(len(receipt['superseded']), 3)
        self.assertEqual(merged['meta']['attempted_readme_scans'], 4)
        self.assertEqual(merged['meta']['unattempted_candidates'], 2)
        self.assertNotIn('current_run', merged['meta'])
        self.assertEqual(merged['meta']['status'], 'in-progress')

    def test_observation_union_retains_old_run_identity_and_deduplicates(self):
        first, second = snapshot((1, 3)), snapshot((1, 2))
        observation = {'query': 'example', 'status': 'ok', 'run_id': 'old'}
        first['meta']['queries'] = [observation]
        second['meta']['queries'] = [observation, {'query': 'other', 'status': 'ok', 'run_id': 'new'}]
        second['meta']['current_run'] = {'run_id': 'new', 'new_successful_readme_scans': 1}
        merged, receipt = scheduled.reconcile(first, second, 'c', 'p')
        self.assertEqual(merged['meta']['queries'], second['meta']['queries'])
        self.assertEqual(receipt['checkpoint_current_run'], second['meta']['current_run'])
        self.assertNotIn('current_run', merged['meta'])

    def test_reassigned_names_are_detected_even_in_superseded_versions(self):
        canonical, previous = snapshot((1, 2)), snapshot((1, 3))
        previous['resources'][0]['full_name'] = canonical['resources'][1]['full_name']
        with self.assertRaisesRegex(ValueError, 'same name'):
            scheduled.reconcile(canonical, previous, 'c', 'p')

    def test_partial_checkpoint_is_not_publishable_by_default(self):
        doc = snapshot(range(1, 1502), status='in-progress')
        errors = []; validate_source_index(doc, errors)
        self.assertTrue(any('incomplete checkpoint' in e for e in errors))
        errors = []; validate_source_index(doc, errors, allow_incomplete=True)
        self.assertEqual(errors, [])
        self.assertEqual(doc['meta']['status'], 'in-progress')


class SelectionTests(unittest.TestCase):
    def test_only_same_workflow_default_branch_and_repository_are_trusted(self):
        invalid = [run(15, event='pull_request'), run(14, head_repository={'full_name': 'fork/catalog'}),
                   run(13, workflow_id=99), run(11, head_branch='feature')]
        api = FakeAPI(invalid + [run()], {12: [artifact()]})
        selected, _ = scheduled.select_checkpoint(api, 'main', 20)
        self.assertEqual(selected['id'], 12)
        self.assertEqual(len([c for c in api.calls if '/artifacts?' in c]), 1)

    def test_failed_terminal_runs_with_valid_checkpoints_are_resumable(self):
        api = FakeAPI([run(conclusion='failure')], {12: [artifact()]})
        self.assertIsNotNone(scheduled.select_checkpoint(api, 'main', 20))

    def test_rerun_resumes_previous_attempt_instead_of_losing_its_increment(self):
        api = FakeAPI([run(10)], {12: [artifact(12)]}, attempts={1: run(12)})
        selected, _ = scheduled.select_checkpoint(api, 'main', 12, 2)
        self.assertEqual((selected['id'], selected['run_attempt']), (12, 1))

    def test_expired_newest_checkpoint_stops_instead_of_silently_starting_over(self):
        api = FakeAPI([run()], {12: [artifact(expired=True)]})
        with self.assertRaisesRegex(ValueError, 'expired'):
            scheduled.select_checkpoint(api, 'main', 20)

    def test_missing_all_previous_artifacts_is_not_an_implicit_fresh_start(self):
        with self.assertRaisesRegex(ValueError, 'no recoverable checkpoint'):
            scheduled.select_checkpoint(FakeAPI([run()], {}), 'main', 20)
        self.assertIsNone(scheduled.select_checkpoint(FakeAPI([], {}), 'main', 20))


def archive_bytes(document, *, member_name='checkpoint.json', symlink=False, duplicate=False, overrides=None):
    raw = json.dumps(document).encode()
    receipt = {'schema_version': 1, 'run_id': 12, 'run_attempt': 1, 'workflow_id': 42,
               'source_commit': 'b' * 40, 'checkpoint_sha256': hashlib.sha256(raw).hexdigest(),
               'counts': scheduled.counts(document), **(overrides or {})}
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED) as archive:
        info = zipfile.ZipInfo(member_name)
        if symlink:
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
        archive.writestr(info, raw)
        archive.writestr('receipt.json', json.dumps(receipt))
        if duplicate:
            archive.writestr('extra.json', '{}')
    return stream.getvalue()


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.doc = snapshot(range(1, 1502), status='in-progress')

    def unpack(self, raw, **changes):
        item = artifact(digest='sha256:' + hashlib.sha256(raw).hexdigest(), **changes)
        return scheduled.unpack_checkpoint(raw, item, run(), self.directory)

    def test_valid_partial_archive_retains_counts_and_status(self):
        restored, _, frontier = self.unpack(archive_bytes(self.doc))
        self.assertEqual(restored, self.doc)
        self.assertIsNone(frontier)

    def test_paths_links_unknown_members_and_provenance_mismatch_are_rejected(self):
        for options in ({'member_name': '../checkpoint.json'}, {'symlink': True}, {'duplicate': True},
                        {'overrides': {'run_id': 99}}, {'overrides': {'run_attempt': 2}},
                        {'overrides': {'workflow_id': 99}}, {'overrides': {'source_commit': 'c' * 40}},
                        {'overrides': {'checkpoint_sha256': 'f' * 64}}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                self.unpack(archive_bytes(self.doc, **options))

    def test_digest_size_and_private_payload_are_rejected_without_echoing_values(self):
        raw = archive_bytes(self.doc)
        with self.assertRaisesRegex(ValueError, 'digest'):
            scheduled.unpack_checkpoint(raw, artifact(digest='sha256:' + '0' * 64), run(), self.directory)
        with patch.object(scheduled, 'MAX_SCAN_BYTES', 100), self.assertRaises(ValueError):
            self.unpack(raw)
        token = 'gh' + 'p_' + 'a' * 36
        self.doc['resources'][0]['description_en'] = token
        with self.assertRaises(ValueError) as raised:
            self.unpack(archive_bytes(self.doc))
        self.assertNotIn(token, str(raised.exception))

    def test_unknown_record_fields_and_inconsistent_counts_are_not_trusted(self):
        self.doc['resources'][0]['readme_body'] = 'must not enter an artifact'
        with self.assertRaisesRegex(ValueError, 'unexpected record'):
            self.unpack(archive_bytes(self.doc))
        del self.doc['resources'][0]['readme_body']
        self.doc['meta']['failed'] = 42
        with self.assertRaises(ValueError):
            self.unpack(archive_bytes(self.doc))


class NestedSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.canonical_path = scheduled.ROOT / 'data/source-index.json'
        cls.canonical = json.loads(cls.canonical_path.read_text(encoding='utf-8'))

    def check(self, document):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'checkpoint.json'
            path.write_text(json.dumps(document), encoding='utf-8')
            return scheduled.read_snapshot(path)[0]

    def test_current_snapshot_and_real_resumed_serialization_keep_all_evidence(self):
        document, _ = scheduled.read_snapshot(self.canonical_path)
        self.assertEqual(document, self.canonical)
        # Exercise the real serializer, including legacy history fields that can
        # be null, while requesting no new reads and forbidding network access.
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'checkpoint.json'
            args = SimpleNamespace(target=len(document['resources']), workers=1,
                                   requests_per_second=2, max_pages=3, candidate_buffer=0,
                                   seed_curated=False, seed_papers=False, queries=[], output=path)
            with patch.object(scheduled.GitHub, 'json', side_effect=AssertionError('No network expected')):
                self.assertEqual(scheduled.run_scan(scheduled.GitHub('unused'), args, document, 'a' * 64), 0)
            resumed, _ = scheduled.read_snapshot(path)
        self.assertEqual(resumed['resources'], self.canonical['resources'])
        self.assertEqual(resumed['failures'], self.canonical['failures'])
        self.assertEqual(resumed['meta']['resume_history'][-1]['run'], self.canonical['meta']['current_run'])

    def test_nested_unknown_keys_and_disguised_containers_are_rejected_without_values(self):
        payload = 'REJECTED_BODY_SENTINEL: synthetic upstream document contents'
        mutations = {
            'current run': lambda d: d['meta']['current_run'].update(raw_readme=payload),
            'historical run': lambda d: next(item['run'] for item in d['meta']['resume_history'] if isinstance(item.get('run'), dict)).update(raw_readme=payload),
            'query observation': lambda d: d['meta']['queries'][0].update(raw_readme=payload),
            'limits': lambda d: d['meta']['limits'].update(raw_readme=payload),
            'signal object': lambda d: d['resources'][0].update(readme_signals=[{'raw_readme': payload}]),
            'topic object': lambda d: d['resources'][0].update(topics=[{'raw_readme': payload}]),
            'query plan object': lambda d: d['meta']['current_run'].update(query_plan=[{'raw_readme': payload}]),
            'reconciliation run': lambda d: d['meta'].update(checkpoint_reconciliations=[{
                'mode': 'union', 'checkpoint_current_run': {**d['meta']['current_run'], 'raw_readme': payload}}]),
            'superseded object': lambda d: d['meta'].update(checkpoint_reconciliations=[{
                'mode': 'union', 'superseded': [{'id': 'scan-1', 'raw_readme': payload}]}]),
        }
        for name, mutate in mutations.items():
            with self.subTest(location=name):
                document = copy.deepcopy(self.canonical)
                mutate(document)
                with self.assertRaisesRegex(ValueError, 'nested') as raised:
                    self.check(document)
                self.assertNotIn(payload, str(raised.exception))

    def test_nested_receipt_fields_are_checked_before_archive_files_are_written(self):
        doc = snapshot(range(1, 1502))
        raw = archive_bytes(doc, overrides={'reconciliation': {
            'mode': 'union', 'checkpoint_current_run': {'raw_readme': 'REJECTED_RECEIPT_BODY'}}})
        item = artifact(digest='sha256:' + hashlib.sha256(raw).hexdigest())
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / 'restored'
            with self.assertRaisesRegex(ValueError, 'nested') as raised:
                scheduled.unpack_checkpoint(raw, item, run(), directory)
            self.assertNotIn('REJECTED_RECEIPT_BODY', str(raised.exception))
            self.assertFalse(directory.exists())

    def test_valid_nested_evidence_and_reconciliation_shapes_are_preserved(self):
        first, second = snapshot(range(1, 1502)), snapshot(range(1, 1503), pending=(1600,))
        merged, receipt = scheduled.reconcile(first, second, 'c' * 64, 'd' * 64)
        self.assertEqual(self.check(merged), merged)
        scheduled.validate_shape(receipt, scheduled.RECONCILIATION_SCHEMA)
        # New capture fields and optional query error counts remain accepted.
        evidence = {
            'description_omission': {'reason': 'upstream-description-too-long', 'original_characters': 1001,
                                     'original_utf8_bytes': 1001, 'original_sha256': 'a' * 64,
                                     'limit_characters': 1000},
            'readme_integrity_review': {'reviewed_at': '2026-10-18T00:00:00Z',
                                       'method': 'readme-json-and-raw-match-captured-sha256',
                                       'advertised_blob_sha256': 'b' * 64, 'advertised_blob_bytes': 42},
            'seed_paper_references': [{'paper_id': 'paper-example', 'field': 'code_url',
                                      'url': 'https://github.com/example/project'}],
        }
        scheduled.validate_shape(evidence, scheduled.RECORD_SCHEMA)
        scheduled.validate_shape({'invalid_item_reasons': {'invalid-repository-metadata': 1}}, scheduled.QUERY_SCHEMA)
        for field in evidence:
            changed = copy.deepcopy(evidence)
            target = changed[field][0] if isinstance(changed[field], list) else changed[field]
            target['raw_readme'] = 'REJECTED_NESTED_BODY'
            with self.subTest(field=field), self.assertRaises(ValueError):
                scheduled.validate_shape(changed, scheduled.RECORD_SCHEMA)


class WorkflowTests(unittest.TestCase):
    def test_schedule_permissions_upload_scope_and_bounds(self):
        text = (scheduled.ROOT / '.github/workflows/source-scan.yml').read_text()
        self.assertIn("cron: '17 0,8,16 * * *'", text)
        self.assertIn('timezone: America/Los_Angeles', text)
        self.assertIn('contents: read', text); self.assertIn('actions: read', text)
        self.assertNotIn(': write', text); self.assertNotIn('pull_request', text)
        self.assertIn('timeout-minutes: 45', text)
        self.assertIn("steps.scan.outputs.checkpoint_ready == 'true'", text)
        self.assertIn('checkpoint/checkpoint.json', text)
        self.assertNotIn('path: .cache/', text.split('name: Preserve validated incremental checkpoint')[1].split('name: Preserve validated inputs')[0])
        self.assertEqual(scheduled.NEW_SUCCESSES, 2000)
        self.assertEqual(scheduled.GLOBAL_TARGET, 160000)
        self.assertIn('checkpoint/frontier.json', text)
        self.assertNotIn('retention-days: 90', text)
        self.assertIn('retention-days: 7', text)
        self.assertLess(scheduled.SCAN_SECONDS, 45 * 60)


class RuntimeBoundaryTests(unittest.TestCase):
    def test_signed_artifact_request_drops_authorization_and_rechecks_deadline(self):
        calls = []
        token = 'ephemeral-test-value'

        class Opener:
            def open(self, request, timeout):
                calls.append((request, timeout))
                if len(calls) == 1:
                    raise HTTPError(request.full_url, 302, 'redirect',
                                    {'Location': 'https://example.blob.core.windows.net/artifact?signature=fixture'}, io.BytesIO())
                return io.BytesIO(b'archive bytes')

        with tempfile.TemporaryDirectory() as temporary, patch.object(scheduled, 'build_opener', return_value=Opener()), \
                patch.object(scheduled.time, 'monotonic', side_effect=[10, 20, 21, 22]):
            path = Path(temporary) / 'archive.zip'
            result = scheduled.ActionsAPI('example/catalog', token, deadline=50).download('actions/artifacts/73/zip', path)
            self.assertEqual(path.read_bytes(), b'archive bytes')
        self.assertEqual(result['bytes'], len(b'archive bytes'))
        self.assertEqual(calls[0][0].get_header('Authorization'), 'Bearer ' + token)
        self.assertIsNone(calls[1][0].get_header('Authorization'))
        calls.clear()
        with tempfile.TemporaryDirectory() as temporary, patch.object(scheduled, 'build_opener', return_value=Opener()), patch.object(scheduled.time, 'monotonic', side_effect=[10, 51]):
            with self.assertRaisesRegex(ValueError, 'time bound'):
                scheduled.ActionsAPI('example/catalog', token, deadline=50).download('actions/artifacts/73/zip', Path(temporary) / 'archive.zip')
        self.assertEqual(len(calls), 1)

    def test_timeout_waits_for_child_and_retains_only_valid_partial_checkpoint(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); (root / 'data').mkdir()
            canonical = snapshot(range(1, 1502))
            scheduled.write_json(root / 'data/source-index.json', canonical)
            environment = {'GITHUB_REPOSITORY': 'example/catalog', 'DEFAULT_BRANCH': 'main',
                           'GITHUB_REF': 'refs/heads/main', 'GITHUB_RUN_ID': '20', 'GITHUB_RUN_ATTEMPT': '1',
                           'GITHUB_SHA': 'd' * 40, 'GH_TOKEN': 'ephemeral-test-value',
                           'GITHUB_OUTPUT': str(root / 'outputs'), 'GITHUB_STEP_SUMMARY': str(root / 'summary')}
            process = SimpleNamespace(pid=1234)
            waits = []

            def launch(command, **kwargs):
                self.assertNotIn(environment['GH_TOKEN'], ' '.join(command))
                self.assertTrue(kwargs['start_new_session'])
                path = Path(command[command.index('--output') + 1])
                partial = snapshot(range(1, 1503), pending=(1503,), status='in-progress')
                scheduled.write_json(path, partial)
                # A frontier page can be durable before its identities reach the scan checkpoint.
                cursor_path = Path(command[command.index('--frontier') + 1])
                scheduled.write_json(cursor_path, small_frontier(2000))
                return process

            def wait(timeout=None):
                waits.append(timeout)
                if len(waits) == 1:
                    raise subprocess.TimeoutExpired('scanner', timeout)
                return -15

            process.wait = wait
            with patch.dict(os.environ, environment), patch.object(scheduled, 'ROOT', root), \
                    patch.object(scheduled.search_frontier, 'ROOT', root), \
                    patch.object(scheduled, 'ActionsAPI', return_value=FakeAPI([], {})), \
                    patch.object(scheduled.subprocess, 'Popen', side_effect=launch), \
                    patch.object(scheduled.os, 'killpg') as stop:
                result = scheduled.orchestrate(root / '.cache/run')
            self.assertEqual(result, 1)
            stop.assert_called_once_with(1234, scheduled.signal.SIGTERM)
            self.assertEqual(len(waits), 2)
            receipt = json.loads((root / '.cache/run/checkpoint/receipt.json').read_text())
            self.assertEqual(receipt['outcome'], 'time-budget')
            self.assertEqual(receipt['new_successful_scans'], 1)
            self.assertFalse(receipt['target_reached'])
            self.assertEqual(receipt['counts']['unique_repos'], 1504)
            self.assertEqual(receipt['counts']['unattempted_candidates'], 2)
            final = json.loads((root / '.cache/run/checkpoint/checkpoint.json').read_text())
            self.assertEqual(final['meta']['status'], 'in-progress')
            self.assertIn('scan-2000', final['meta']['discovered_repository_ids'])
            self.assertEqual(final['meta']['queries'], [])
            self.assertEqual((root / 'outputs').read_text(), 'checkpoint_ready=true\n')
            self.assertNotIn(environment['GH_TOKEN'], json.dumps(receipt))
            self.assertEqual(json.loads((root / 'data/source-index.json').read_text()), canonical)


def small_frontier(identifier=None, acknowledged=False):
    module = scheduled.search_frontier
    state = module.new_frontier(since='2026-01-01T00:00:00Z', until='2026-01-01T00:00:01Z',
                                approved_queries=[scheduled.APPROVED_QUERIES[0]])
    if identifier is not None:
        request = module.next_request(state)
        name = f'example/repository-{identifier}'
        module.record_response(state, request, {'total_count': 1, 'incomplete_results': False,
            'items': [{'id': identifier, 'full_name': name, 'html_url': 'https://github.com/' + name,
                       'node_id': 'R_fixture', 'private': False, 'fork': False, 'archived': False,
                       'created_at': '2026-01-01T00:00:00Z'}]}, observed_at='2026-01-01T00:00:01Z')
        if acknowledged:
            module.acknowledge_candidates(state, [identifier], checkpoint_sha256='a' * 64)
    return state


def paired_archive(document, frontier, *, mutate_receipt=None, extra=None):
    scan = json.dumps(document).encode()
    cursor = json.dumps(frontier).encode()
    receipt = {'schema_version': 2, 'run_id': 12, 'run_attempt': 1, 'workflow_id': 42,
               'source_commit': 'b' * 40, 'checkpoint_sha256': hashlib.sha256(scan).hexdigest(),
               'counts': scheduled.counts(document), 'frontier': scheduled.search_frontier.summary(frontier),
               'files': {'checkpoint.json': {'sha256': hashlib.sha256(scan).hexdigest(), 'bytes': len(scan)},
                         'frontier.json': {'sha256': hashlib.sha256(cursor).hexdigest(), 'bytes': len(cursor)}}}
    if mutate_receipt:
        mutate_receipt(receipt)
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('checkpoint.json', scan)
        archive.writestr('frontier.json', cursor)
        archive.writestr('receipt.json', json.dumps(receipt))
        if extra:
            archive.writestr(*extra)
    return stream.getvalue()


class PairedCheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.doc = snapshot(range(1, 1502))

    def restore(self, raw):
        source = self.root / 'input.zip'; source.write_bytes(raw)
        return scheduled.unpack_checkpoint(source, artifact(digest='sha256:' + hashlib.sha256(raw).hexdigest()),
                                           run(), self.root / 'restored')

    def test_streamed_pair_keeps_old_ack_hash_and_pending_after_capture_crash(self):
        frontier = small_frontier(1, acknowledged=True)
        restored, _, cursor = self.restore(paired_archive(self.doc, frontier))
        self.assertEqual(restored, self.doc)
        self.assertEqual(cursor['candidates']['1']['checkpoint_sha256'], 'a' * 64)
        # A scan-save-before-ACK-save crash is safe: an already scanned identity can remain pending.
        frontier['candidates']['1']['checkpoint_sha256'] = None
        _, _, cursor = self.restore(paired_archive(self.doc, frontier))
        self.assertIsNone(cursor['candidates']['1']['checkpoint_sha256'])

    def test_ack_ahead_of_scan_and_mixed_member_hashes_fail_closed(self):
        with self.assertRaisesRegex(ValueError, 'absent'):
            self.restore(paired_archive(self.doc, small_frontier(2000, acknowledged=True)))
        for mutate in (
                lambda r: r['files']['frontier.json'].update(sha256='0' * 64),
                lambda r: r['files']['checkpoint.json'].update(bytes=1),
                lambda r: r.update(source_commit='c' * 40),
                lambda r: r['frontier'].update(candidate_identities=99)):
            with self.subTest(mutate=mutate), self.assertRaises(ValueError):
                self.restore(paired_archive(self.doc, small_frontier(), mutate_receipt=mutate))

    def test_member_aggregate_json_and_archive_bounds_are_independent(self):
        raw = paired_archive(self.doc, small_frontier())
        for name, bound in (('MAX_ARCHIVE_BYTES', 10), ('MAX_TOTAL_BYTES', 10),
                            ('MAX_SCAN_BYTES', 10), ('MAX_FRONTIER_BYTES', 10), ('MAX_RECEIPT_BYTES', 10)):
            with self.subTest(bound=name), patch.object(scheduled, name, bound), self.assertRaises(ValueError):
                self.restore(raw)
        with self.assertRaises(ValueError):
            self.restore(paired_archive(self.doc, small_frontier(), extra=('raw-readme.txt', 'must not be retained')))
        self.assertEqual(scheduled.MAX_API_BYTES, 12 * 1024 * 1024)
        self.assertEqual(scheduled.MAX_SCAN_BYTES, 512 * 1024 * 1024)
        self.assertEqual(scheduled.MAX_FRONTIER_BYTES, 256 * 1024 * 1024)

    def test_graphql_provenance_and_metrics_accept_only_the_explicit_contract(self):
        doc = copy.deepcopy(self.doc)
        doc['resources'][0].update(readme_transport='github-graphql-blob',
            readme_graphql_endpoint='https://api.github.com/graphql', readme_commit_sha='b' * 40,
            readme_git_sha='c' * 40, readme_content_git_sha='c' * 40, readme_git_sha_matches_content=True,
            readme_path='README.md', readme_url='https://github.com/example/repository-1/blob/' + 'b' * 40 + '/README.md')
        path = self.root / 'scan.json'; scheduled.write_json(path, doc)
        self.assertEqual(scheduled.read_snapshot(path)[0], doc)
        doc['resources'][0]['readme_graphql_endpoint'] = 'https://example.org/graphql'
        scheduled.write_json(path, doc)
        with self.assertRaises(ValueError):
            scheduled.read_snapshot(path)
        metrics = {'method': 'github-graphql-verified-blob-with-rest-fallback', 'batch_size': 16,
                   'outcomes': dict.fromkeys(('ok', 'fallback', 'rejected', 'retry', 'deferred'), 0),
                   'reported_query_cost': 1, 'elapsed_seconds': 0.5, 'last_rate_limit': {'remaining': 999}}
        scheduled.validate_transport(metrics)
        for bad in ({**metrics, 'raw_response': 'not retained'}, {**metrics, 'batch_size': 17},
                    {**metrics, 'elapsed_seconds': float('inf')}, {**metrics, 'reported_query_cost': -1}):
            with self.assertRaises(ValueError):
                scheduled.validate_transport(bad)

    def test_global_goal_clamps_final_increment_and_reuses_unexpired_pair(self):
        self.assertEqual(scheduled.planned_successes(159950), 50)
        self.assertEqual(scheduled.planned_successes(160000), 0)
        self.assertEqual(scheduled.planned_successes(160001), 0)
        (self.root / 'data').mkdir()
        scheduled.write_json(self.root / 'data/source-index.json', self.doc)
        raw = paired_archive(self.doc, small_frontier())
        selected_artifact = artifact(digest='sha256:' + hashlib.sha256(raw).hexdigest(), expires_at='2099-01-01T00:00:00Z')
        api = FakeAPI([], {})
        api.download = lambda suffix, path: path.write_bytes(raw)
        environment = {'GITHUB_REPOSITORY': 'example/catalog', 'DEFAULT_BRANCH': 'main',
                       'GITHUB_REF': 'refs/heads/main', 'GITHUB_RUN_ID': '20', 'GITHUB_RUN_ATTEMPT': '1',
                       'GITHUB_SHA': 'd' * 40, 'GH_TOKEN': 'ephemeral-test-value',
                       'GITHUB_OUTPUT': str(self.root / 'outputs'), 'GITHUB_STEP_SUMMARY': str(self.root / 'summary')}
        directory = self.root / '.cache/goal'
        with patch.dict(os.environ, environment), patch.object(scheduled, 'ROOT', self.root),                 patch.object(scheduled.search_frontier, 'ROOT', self.root),                 patch.object(scheduled, 'GLOBAL_TARGET', 1501), patch.object(scheduled, 'ActionsAPI', return_value=api),                 patch.object(scheduled, 'select_checkpoint', return_value=(run(), selected_artifact)),                 patch.object(scheduled.subprocess, 'Popen', side_effect=AssertionError('No child at goal')):
            self.assertEqual(scheduled.orchestrate(directory), 0)
        summary = json.loads((directory / 'summary.json').read_text())
        self.assertEqual(summary['new_successful_scans'], 0)
        self.assertTrue(summary['global_target_reached'])
        self.assertFalse((directory / 'checkpoint').exists())
        self.assertEqual((self.root / 'outputs').read_text(), 'checkpoint_ready=false\n')

    def test_first_v1_import_emits_v2_pair_and_clamps_child_target(self):
        (self.root / 'data').mkdir()
        scheduled.write_json(self.root / 'data/source-index.json', self.doc)
        raw = archive_bytes(self.doc)
        selected_artifact = artifact(digest='sha256:' + hashlib.sha256(raw).hexdigest())
        api = FakeAPI([], {})
        api.download = lambda suffix, path: path.write_bytes(raw)
        environment = {'GITHUB_REPOSITORY': 'example/catalog', 'DEFAULT_BRANCH': 'main',
                       'GITHUB_REF': 'refs/heads/main', 'GITHUB_RUN_ID': '20', 'GITHUB_RUN_ATTEMPT': '1',
                       'GITHUB_SHA': 'd' * 40, 'GH_TOKEN': 'ephemeral-test-value',
                       'GITHUB_OUTPUT': str(self.root / 'outputs'), 'GITHUB_STEP_SUMMARY': str(self.root / 'summary')}
        directory = self.root / '.cache/migration'
        def child(command, **kwargs):
            self.assertIn('--frontier', command)
            output = Path(command[command.index('--output') + 1])
            scheduled.write_json(output, snapshot(range(1, 1504)))
            return SimpleNamespace(wait=lambda timeout: 0)
        with patch.dict(os.environ, environment), patch.object(scheduled, 'ROOT', self.root),                 patch.object(scheduled.search_frontier, 'ROOT', self.root), patch.object(scheduled, 'GLOBAL_TARGET', 1503),                 patch.object(scheduled, 'ActionsAPI', return_value=api),                 patch.object(scheduled, 'select_checkpoint', return_value=(run(), selected_artifact)),                 patch.object(scheduled.subprocess, 'Popen', side_effect=child):
            self.assertEqual(scheduled.orchestrate(directory), 0)
        receipt = json.loads((directory / 'checkpoint/receipt.json').read_text())
        self.assertEqual(receipt['schema_version'], 2)
        self.assertEqual(receipt['planned_new_successes'], 2)
        self.assertEqual(receipt['new_successful_scans'], 2)
        self.assertTrue(receipt['run_target_reached']); self.assertTrue(receipt['global_target_reached'])
        self.assertEqual(set(p.name for p in (directory / 'checkpoint').iterdir()), {'checkpoint.json', 'frontier.json', 'receipt.json'})

    def test_approved_website_game_app_roots_append_without_resetting_saved_work(self):
        frontier = small_frontier(1)
        old_partition = copy.deepcopy(frontier['partitions'][0])
        old_observations = copy.deepcopy(frontier['observations'])
        scheduled.search_frontier.add_queries(frontier, scheduled.APPROVED_QUERIES,
                                             approved_queries=scheduled.APPROVED_QUERIES)
        self.assertEqual(frontier['partitions'][0], old_partition)
        self.assertEqual(frontier['observations'], old_observations)
        self.assertEqual(len(frontier['roots']), len(set(scheduled.APPROVED_QUERIES)))
        for expected in ('topic:screenshot-to-code', 'topic:website-clone', 'topic:game-reimplementation',
                         'topic:app-clone', '"reverse engineering" in:readme'):
            self.assertIn(expected, frontier['roots'])
        with self.assertRaises(ValueError):
            scheduled.search_frontier.add_queries(frontier, ['topic:unapproved'],
                                                 approved_queries=scheduled.APPROVED_QUERIES)


class ScheduledBudgetTests(unittest.TestCase):
    def test_expanded_discovery_keeps_capture_goal_surplus_and_other_budgets_bounded(self):
        document = snapshot(range(1, 1502))
        document['resources'][0] = record(1, integrity=None)
        document['resources'][1] = record(2, integrity=False)
        qualified = 1499
        for remaining, planned, surplus in ((1, 1, 50), (500, 500, 50), (501, 501, 51),
                                            (2000, 2000, 200), (9000, 2000, 200)):
            with self.subTest(remaining=remaining), \
                    patch.dict(os.environ, GH_TOKEN='offline-test-only'), \
                    patch.object(scheduled, 'GLOBAL_TARGET', qualified + remaining), \
                    patch.object(scheduled, 'read_snapshot', return_value=(document, 'a' * 64)), \
                    patch.object(scheduled, 'read_frontier', return_value=small_frontier()), \
                    patch.object(scheduled, 'run_scan', return_value=0) as scan:
                self.assertEqual(scheduled.scanner_child(Path('seed.json'), Path('output.json'), Path('frontier.json')), 0)
            args = scan.call_args.args[1]
            self.assertEqual(args.target, len(document['resources']) + planned)
            self.assertEqual(args.candidate_buffer, surplus)
            self.assertEqual((args.search_request_budget, args.pending_metadata_budget), (360, 200))
            self.assertEqual((args.workers, args.requests_per_second, args.max_pages), (4, 2, 3))
            self.assertEqual(scan.call_args.kwargs['readme_transport'].batch_size, 16)
        self.assertEqual(scheduled.SCAN_SECONDS, 38 * 60)
        self.assertEqual(scheduled.NEW_SUCCESSES, 2000)

    def test_observed_graphql_quota_and_fallback_budget_defer_without_extra_requests(self):
        calls = []
        class Transport:
            batch_size = 16
            last_batch_receipts = [{'rate_limit': {'cost': 1}}]
            rate_limit = {'remaining': 999}
            def fetch_batch(self, rows):
                calls.append(rows)
                return {row['id']: {'status': 'fallback'} for row in rows}
        policy = scheduled.ScheduledTransport(Transport(), SimpleNamespace(rate={'core': {'remaining': 105}}))
        rows = [{'id': n} for n in range(3)]
        self.assertTrue(all(r['status'] == 'deferred' for r in policy.fetch_batch(rows).values()))
        self.assertEqual(policy.fallbacks, 0)
        policy.rate_limit = {'remaining': 99}
        self.assertTrue(all(r['status'] == 'deferred' for r in policy.fetch_batch(rows).values()))
        self.assertEqual(len(calls), 1)
        policy.rate_limit = {}; policy.reported_cost = 800
        self.assertTrue(all(r['status'] == 'deferred' for r in policy.fetch_batch(rows).values()))
        self.assertEqual(len(calls), 1)
        policy.reported_cost = 0; policy.requests = 800
        self.assertTrue(all(r['status'] == 'deferred' for r in policy.fetch_batch(rows).values()))
        self.assertEqual(len(calls), 1)
        policy.requests = 0; policy.fallbacks = 200
        policy.rest.rate['core']['remaining'] = 1000
        self.assertTrue(all(r['status'] == 'deferred' for r in policy.fetch_batch(rows).values()))
        self.assertEqual(policy.fallbacks, 200)
        self.assertEqual(len(calls), 2)


if __name__ == '__main__':
    unittest.main()
