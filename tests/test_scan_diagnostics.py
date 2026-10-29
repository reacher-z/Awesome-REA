"""Offline diagnostics must explain failures without changing capture evidence."""
import contextlib
from copy import deepcopy
import io
import json
import os
from pathlib import Path
import stat
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from urllib.error import URLError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import scan_diagnostics as diagnostics
import scan_sources as scanner
import search_frontier as frontier
from test_scan_graphql_transport import (CONTENT, Response, blob_result, client,
                                         envelope, probe_result, repository)
from test_scan_frontier_integration import (BASE, OBSERVED, NoRequests, arguments,
                                            public_repository)

QUEUED = [{'id': 1, 'full_name': 'example/demo'}]
EVENT = {'phase': 'metadata', 'reason': 'graphql-server-error', 'repository_count': 1,
         'observed_at': OBSERVED, 'request_attempted': True,
         'http_status': 502, 'response_bytes': 12}


class TransportDiagnosticTests(unittest.TestCase):
    def test_request_failures_explain_each_phase_without_payload_or_quota(self):
        failures = [
            (lambda: URLError('TOKEN /private/home secret body'), 'graphql-network-error', None),
            (lambda: Response(b'TOKEN', status=429, headers={'Retry-After': '60'}), 'graphql-rate-limit', 429),
            (lambda: Response(b'TOKEN', status=403), 'graphql-access-denied', 403),
            (lambda: Response(b'TOKEN', status=502), 'graphql-server-error', 502),
            (lambda: Response(b'TOKEN', status=418), 'graphql-http-error', 418),
            (lambda: Response(b'TOKEN' * 3000000), 'graphql-response-too-large', 200),
            (lambda: Response(b'{TOKEN'), 'invalid-graphql-response', 200),
            (lambda: envelope(errors=[{'type': 'INTERNAL', 'message': 'TOKEN /private/home'}]),
             'graphql-query-error', 200),
        ]
        for phase in ('metadata', 'preflight', 'blob'):
            for make_failure, reason, status in failures:
                with self.subTest(phase=phase, reason=reason):
                    prefix = [envelope(repository()), envelope(probe_result())][:
                        {'metadata': 0, 'preflight': 1, 'blob': 2}[phase]]
                    instance, opener, _ = client(*prefix, make_failure(), capture_diagnostics=True)
                    result = instance.fetch_batch(QUEUED)[1]
                    self.assertIn(result['status'], ('retry', 'deferred'))
                    self.assertEqual(result['reason'], reason)
                    event, = instance.last_batch_diagnostics
                    self.assertEqual((event['phase'], event['reason'], event['request_attempted']),
                                     (phase, reason, True))
                    self.assertEqual(event.get('http_status'), status)
                    if reason == 'graphql-network-error':
                        self.assertNotIn('response_bytes', event)
                    else:
                        self.assertLessEqual(event['response_bytes'], diagnostics.MAX_RESPONSE_BYTES)
                    self.assertEqual(len(opener.requests), len(prefix) + 1)
                    for forbidden in ('TOKEN', '/private/', 'remaining', 'Authorization', 'message', 'variables'):
                        self.assertNotIn(forbidden, json.dumps(event))

    def test_disabled_capture_and_early_backoff_preserve_request_receipts(self):
        for enabled in (False, True):
            instance, opener, _ = client(envelope(repository(), remaining=0), capture_diagnostics=enabled)
            first = instance.fetch_batch(QUEUED)
            self.assertEqual(first[1]['status'], 'deferred')
            self.assertEqual(len(instance.last_batch_receipts), 1)
            self.assertEqual(len(instance.last_batch_diagnostics), int(enabled))
            second = instance.fetch_batch(QUEUED)
            self.assertEqual(second[1]['reason'], 'graphql-rate-limit')
            self.assertEqual(len(opener.requests), 1)
            self.assertEqual(instance.last_batch_receipts, [])
            if enabled:
                event, = instance.last_batch_diagnostics
                self.assertFalse(event['request_attempted'])
                self.assertNotIn('http_status', event)
                self.assertNotIn('response_bytes', event)
            else:
                self.assertEqual(instance.last_batch_diagnostics, [])
            instance.fetch_batch([])
            self.assertEqual(instance.last_batch_diagnostics, [])

    def test_metadata_validation_retries_keep_only_fixed_reason_codes(self):
        cases = [
            ({'description': {'secret': 'TOKEN'}}, 'invalid-repository-metadata'),
            ({'repositoryTopics': {'nodes': [{'topic': {'name': 'TOKEN'}}],
                                  'pageInfo': {'hasNextPage': False}}}, 'invalid-repository-topics'),
            ({'updatedAt': 'TOKEN'}, 'invalid-repository-timestamp'),
            ({'defaultBranchRef': {'name': {'secret': 'TOKEN'}}}, 'invalid-default-branch'),
        ]
        for fields, reason in cases:
            with self.subTest(reason=reason):
                instance, _, _ = client(envelope(repository(**fields)), capture_diagnostics=True)
                result = instance.fetch_batch(QUEUED)[1]
                self.assertEqual((result['status'], result['reason']), ('retry', reason))
                event, = instance.last_batch_diagnostics
                self.assertEqual((event['reason'], event['phase'], event['http_status']), (reason, 'metadata', 200))
                self.assertNotIn('TOKEN', json.dumps(event))

    def test_read_exception_has_known_status_but_no_invented_byte_count(self):
        class BrokenRead(Response):
            def read(self, size):
                raise OSError('TOKEN /private/home/body')

        instance, _, _ = client(BrokenRead(b'body'), capture_diagnostics=True)
        instance.fetch_batch(QUEUED)
        event, = instance.last_batch_diagnostics
        self.assertEqual(event['http_status'], 200)
        self.assertNotIn('response_bytes', event)
        self.assertNotIn('http_status', instance.last_batch_receipts[0])

    def test_success_results_provenance_and_existing_receipts_are_byte_identical(self):
        outputs = []
        for enabled in (False, True):
            instance, _, _ = client(envelope(repository()), envelope(probe_result()),
                                    envelope(blob_result()), capture_diagnostics=enabled)
            result = instance.fetch_batch(QUEUED)
            self.assertEqual(instance.last_batch_diagnostics, [])
            outputs.append((result, instance.last_batch_receipts, instance.rate_limit))
        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(outputs[0][0][1]['content'], CONTENT)


class SidecarBoundaryTests(unittest.TestCase):
    def test_projection_strips_extras_and_rejects_unbounded_or_untrusted_fields(self):
        supplied = {**EVENT, 'headers': {'Authorization': 'TOKEN'}, 'body': 'SECRET',
                    'rate_limit': {'remaining': 999}, 'path': '/private/home'}
        projected = diagnostics.failure_event(supplied, supplied['reason'], request_attempted=True)
        self.assertEqual(projected, EVENT)
        for field, value in (('phase', []), ('phase', 'TOKEN'), ('reason', ['secret']),
                             ('reason', 'arbitrary exception /private/home'), ('observed_at', 'yesterday'),
                             ('observed_at', '2026-10-18T12:00:00+00:00'), ('repository_count', True),
                             ('repository_count', 17), ('http_status', '502'), ('http_status', 999),
                             ('response_bytes', -1), ('response_bytes', diagnostics.MAX_RESPONSE_BYTES + 1),
                             ('request_attempted', 'true')):
            row = {**EVENT, field: value}
            with self.subTest(field=field, value=value):
                self.assertIsNone(diagnostics.failure_event(row, row['reason'],
                                  request_attempted=row['request_attempted']))
        self.assertIsNone(diagnostics.failure_event(EVENT, EVENT['reason'], request_attempted=False))

    def test_exclusive_private_bounded_jsonl_and_no_follow_or_path_escape(self):
        with TemporaryDirectory() as temporary:
            cache = Path(temporary) / '.cache'
            cache.mkdir()
            path = cache / 'diagnostic.jsonl'
            diagnostics.validate_destination(path, cache)
            writer = diagnostics.DiagnosticSidecar(path, cache)
            writer.start(OBSERVED)
            for _ in range(20):
                writer.record_batch([{**EVENT, 'secret': 'TOKEN'} for _ in range(16)])
            writer.close()
            raw = path.read_bytes()
            rows = [json.loads(line) for line in raw.splitlines()]
            self.assertEqual(len(rows), diagnostics.MAX_EVENTS + 2)
            self.assertEqual(rows[-1]['kind'], 'diagnostic-event-limit')
            self.assertLessEqual(len(raw), (diagnostics.MAX_EVENTS + 2) * diagnostics.MAX_LINE_BYTES)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertNotIn(b'TOKEN', raw)
            with self.assertRaises(ValueError):
                diagnostics.validate_destination(path, cache)
            with self.assertRaises(FileExistsError):
                diagnostics.DiagnosticSidecar(path, cache)
            self.assertEqual(path.read_bytes(), raw)
            outside = Path(temporary) / 'outside'
            outside.mkdir()
            (cache / 'linked').symlink_to(outside, target_is_directory=True)
            (cache / 'file.jsonl').symlink_to(outside / 'target.jsonl')
            for destination in (outside / 'new.jsonl', cache / '../escaped.jsonl',
                                cache / 'linked/new.jsonl', cache / 'file.jsonl', cache / 'bad.json'):
                with self.subTest(destination=destination.name), self.assertRaises((OSError, ValueError)):
                    diagnostics.validate_destination(destination, cache)
            self.assertEqual(list(outside.iterdir()), [])
            alias = Path(temporary) / 'cache-alias'
            alias.symlink_to(cache, target_is_directory=True)
            with self.assertRaises(OSError):
                diagnostics.validate_destination(alias / 'other.jsonl', alias)

    def test_io_failure_is_sanitized_once_and_does_not_escape(self):
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / 'diagnostics.jsonl'
            writer = diagnostics.DiagnosticSidecar(path, Path(temporary))
            output = io.StringIO()
            with patch.object(os, 'fsync', side_effect=OSError('TOKEN /private/home')), \
                    contextlib.redirect_stdout(output):
                writer.start(OBSERVED)
                writer.record_batch([EVENT])
            writer.close()
            self.assertEqual(output.getvalue().count('TRANSPORT_DIAGNOSTICS_DISABLED'), 1)
            self.assertNotIn('TOKEN', output.getvalue())
            self.assertNotIn('/private', output.getvalue())

    def test_diagnostic_failure_and_broken_warning_output_never_escape(self):
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / 'diagnostics.jsonl'
            writer = diagnostics.DiagnosticSidecar(path, Path(temporary))
            with patch.object(os, 'fsync', side_effect=OSError('TOKEN')), \
                    patch('builtins.print', side_effect=BrokenPipeError('PRIVATE')) as warning:
                writer.start(OBSERVED)
                writer.record_batch([EVENT])
                self.assertEqual(warning.call_count, 1)
            writer.close()
            self.assertNotIn('TOKEN', path.read_text())
            self.assertNotIn('PRIVATE', path.read_text())
            # Python's print raises ValueError for a closed text stream, rather
            # than BrokenPipeError from an open stream with a disconnected pipe.
            closed_stream = io.StringIO()
            closed_stream.close()
            writer = diagnostics.DiagnosticSidecar(Path(temporary) / 'closed.jsonl', Path(temporary))
            with patch.object(os, 'fsync', side_effect=OSError('TOKEN')), \
                    contextlib.redirect_stdout(closed_stream):
                writer.start(OBSERVED)
                writer.record_batch([EVENT])
            writer.close()

    def test_sidecar_cannot_mix_two_run_identities_or_change_its_first_header(self):
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / 'diagnostics.jsonl'
            writer = diagnostics.DiagnosticSidecar(path, Path(temporary))
            writer.start(OBSERVED)
            original = path.read_bytes()
            with self.assertRaisesRegex(ValueError, 'exactly one run'):
                writer.start('2026-10-19T12:00:00Z')
            writer.close()
            self.assertEqual(path.read_bytes(), original)

    def test_cli_invalid_destination_fails_before_authentication_or_checkpoint_writes(self):
        with TemporaryDirectory() as temporary:
            cache = Path(temporary) / '.cache'
            cache.mkdir()
            existing = cache / 'existing.jsonl'
            existing.write_bytes(b'untouched')
            shared = cache / 'shared.jsonl'
            for path, extra in ((existing, []), (Path(temporary) / 'outside.jsonl', []),
                                (shared, ['--output', str(shared)]),
                                (shared, ['--frontier', str(shared)]),
                                (shared, ['--resume', str(shared)])):
                with self.subTest(path=path, extra=extra), \
                        patch.object(scanner, 'ROOT', Path(temporary)), \
                        patch.object(sys, 'argv', ['scan_sources.py', '--transport', 'graphql',
                                      '--transport-diagnostics', str(path), *extra]), \
                        patch.object(scanner.subprocess, 'run') as authentication, \
                        patch.object(scanner, 'load_resume') as resume, \
                        contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as raised:
                        scanner.main()
                    self.assertEqual(raised.exception.code, 2)
                    authentication.assert_not_called()
                    resume.assert_not_called()
            self.assertEqual(existing.read_bytes(), b'untouched')
            self.assertFalse(shared.exists())


class CaptureParityTests(unittest.TestCase):
    def test_sidecar_keeps_checkpoint_frontier_ack_backoff_and_exit_identical(self):
        initial = frontier.new_frontier(until='2026-10-18T00:00:00Z', approved_queries=[BASE])
        request = frontier.next_request(initial)
        frontier.record_response(initial, request,
            {'items': [public_repository(1)], 'total_count': 1, 'incomplete_results': False},
            observed_at='2026-10-18T01:00:00Z', run_id='2026-10-18T01:00:00Z')
        cache = ROOT / '.cache'
        cache.mkdir(exist_ok=True)
        for status in ('ok', 'retry', 'deferred'):
            compared = []
            with self.subTest(status=status), TemporaryDirectory(dir=cache) as temporary:
                for enabled in (False, True):
                    state = deepcopy(initial)
                    output = Path(temporary) / f'scan-{enabled}.json'
                    state_path = Path(temporary) / f'frontier-{enabled}.json'
                    sidecar_path = Path(temporary) / 'diagnostic.jsonl'
                    responses = ([envelope(repository(name='example/project-1')),
                                  envelope(probe_result(name='example/project-1')),
                                  envelope(blob_result(name='example/project-1'))] if status == 'ok'
                                 else [Response(b'NO BODY RETAINED', status=502 if status == 'retry' else 429)])
                    instance, _, _ = client(*responses, capture_diagnostics=enabled)
                    writer = diagnostics.DiagnosticSidecar(sidecar_path, cache) if enabled else None
                    with contextlib.redirect_stdout(io.StringIO()), patch.object(scanner, 'now', return_value=OBSERVED), \
                            patch.object(scanner.time, 'monotonic', return_value=100.0), \
                            patch.object(frontier, 'current_seconds', return_value=frontier.utc_seconds(OBSERVED)):
                        code = scanner.run_scan(NoRequests(), arguments(output), readme_transport=instance,
                                                frontier=(state, state_path, [BASE]), diagnostics=writer)
                    if writer:
                        writer.close()
                    compared.append((code, output.read_bytes(), state_path.read_bytes()))
                self.assertEqual(compared[0], compared[1])
                document = json.loads(compared[0][1])
                self.assertEqual(document['meta']['attempted_readme_scans'], int(status == 'ok'))
                self.assertEqual(compared[0][0], 0 if status == 'ok' else 1)
                lines = sidecar_path.read_text().splitlines()
                self.assertEqual(len(lines), 1 if status == 'ok' else 2)
                self.assertNotIn('NO BODY RETAINED', sidecar_path.read_text())


if __name__ == '__main__':
    unittest.main()
