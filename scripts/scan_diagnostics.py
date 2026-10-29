"""Optional private transport diagnostics; never a capture or publication input.

JSONL contains one run header, at most 256 failure events and one truncation
marker. A process interruption can leave an incomplete final line. Response
sizes describe the associated request, not unique bytes or README counts.
"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import re

MAX_EVENTS = 256
MAX_LINE_BYTES = 1024
MAX_RESPONSE_BYTES = 12 * 1024 * 1024 + 1
PHASES = frozenset({'metadata', 'preflight', 'blob'})
REASONS = frozenset({
    'graphql-network-error', 'graphql-rate-limit', 'graphql-access-denied',
    'graphql-server-error', 'graphql-http-error', 'graphql-response-too-large',
    'invalid-graphql-response', 'graphql-query-error',
    'invalid-repository-metadata', 'invalid-repository-topics',
    'invalid-repository-timestamp', 'invalid-default-branch',
})
UTC_RE = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z\Z')


def _utc(value):
    if not isinstance(value, str) or not UTC_RE.fullmatch(value):
        return False
    try:
        return dt.datetime.fromisoformat(value.replace('Z', '+00:00')).utcoffset() == dt.timedelta(0)
    except ValueError:
        return False


def failure_event(receipt, reason, *, request_attempted, repository_count=None):
    """Project only closed fields; never copy exception text or whole receipts."""
    if not isinstance(receipt, dict) or not isinstance(reason, str) or reason not in REASONS:
        return None
    count = receipt.get('repository_count') if repository_count is None else repository_count
    if (not isinstance(receipt.get('phase'), str) or receipt['phase'] not in PHASES
            or not _utc(receipt.get('observed_at'))
            or type(count) is not int or not 1 <= count <= 16
            or type(request_attempted) is not bool):
        return None
    event = {'phase': receipt['phase'], 'reason': reason,
             'repository_count': count, 'observed_at': receipt['observed_at'],
             'request_attempted': request_attempted}
    for key, lower, upper in (('http_status', 100, 599), ('response_bytes', 0, MAX_RESPONSE_BYTES)):
        value = receipt.get(key)
        if value is not None:
            if type(value) is not int or not lower <= value <= upper:
                return None
            event[key] = value
    if not request_attempted and ('http_status' in event or 'response_bytes' in event):
        return None
    return event


def _parent(path, cache_root):
    """Open existing cache ancestors without following symlinks (including cache)."""
    path, cache_root = Path(os.path.abspath(path)), Path(os.path.abspath(cache_root))
    try:
        relative = path.relative_to(cache_root)
    except ValueError:
        raise ValueError('Diagnostics must use a new file inside the ignored cache') from None
    if not relative.parts or relative.suffix != '.jsonl':
        raise ValueError('Diagnostics require a new .jsonl file')
    descriptor = os.open(cache_root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in relative.parts[:-1]:
            following = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = following
        return descriptor, relative.name
    except BaseException:
        os.close(descriptor)
        raise


def validate_destination(path, cache_root, *, protected_paths=()):
    """Read-only preflight before authentication, capture writes or discovery."""
    if any(Path(path).resolve() == Path(item).resolve() for item in protected_paths if item is not None):
        raise ValueError('Diagnostics must be separate from scan inputs and outputs')
    descriptor, name = _parent(path, cache_root)
    try:
        try:
            os.stat(name, dir_fd=descriptor, follow_symlinks=False)
        except FileNotFoundError:
            return
        raise ValueError('Diagnostics destination already exists')
    finally:
        os.close(descriptor)


class DiagnosticSidecar:
    """Exclusive private file; write failures disable diagnostics, not capture."""
    def __init__(self, path, cache_root):
        descriptor, name = _parent(path, cache_root)
        try:
            output = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                             0o600, dir_fd=descriptor)
        finally:
            os.close(descriptor)
        self._file = os.fdopen(output, 'wb')
        self._count = 0
        self._truncated = False
        self._started = False
        self._disabled = False

    def _write(self, rows):
        if self._disabled or not rows:
            return
        try:
            encoded = [(json.dumps(row, ensure_ascii=True, separators=(',', ':')) + '\n').encode('ascii')
                       for row in rows]
            if any(len(line) > MAX_LINE_BYTES for line in encoded):
                raise ValueError('Diagnostic line exceeds bound')
            self._file.write(b''.join(encoded))
            self._file.flush()
            os.fsync(self._file.fileno())
        except (OSError, ValueError):
            self._disabled = True
            try:
                print('TRANSPORT_DIAGNOSTICS_DISABLED: diagnostic write failed; capture continues unchanged.', flush=True)
            except (OSError, ValueError):
                pass  # A closed stdout must not make this optional warning fatal.

    def start(self, run_started_at):
        if self._started:
            raise ValueError('A diagnostic sidecar belongs to exactly one run')
        if not _utc(run_started_at):
            raise ValueError('Diagnostic run timestamp must be UTC')
        self._started = True
        self._write([{'schema_version': 1, 'kind': 'private-transport-diagnostics',
                      'run_started_at': run_started_at, 'event_limit': MAX_EVENTS}])

    def record_batch(self, events):
        if not self._started or self._disabled or self._truncated:
            return
        # A real transport batch can produce at most 16 metadata-validation
        # failures plus bounded request failures. Refuse arbitrary bulk inputs.
        if not isinstance(events, list) or len(events) > 32:
            return
        rows = []
        for item in events:
            if not isinstance(item, dict):
                continue
            event = failure_event(item, item.get('reason'), request_attempted=item.get('request_attempted'))
            if event is None:
                continue
            if self._count >= MAX_EVENTS:
                rows.append({'kind': 'diagnostic-event-limit', 'event_limit': MAX_EVENTS})
                self._truncated = True
                break
            rows.append(event)
            self._count += 1
        self._write(rows)

    def close(self):
        try:
            self._file.close()
        except OSError:
            # Buffered writes were already flushed in _write; do not turn a
            # diagnostic-only failure into a different capture exit status.
            pass
