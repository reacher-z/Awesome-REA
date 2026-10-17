#!/usr/bin/env python3
"""Recheck scanned repositories by numeric GitHub ID and write a dated availability report.

Opt-in and metadata-only: it runs only when invoked with a token in GH_TOKEN or
GITHUB_TOKEN, uses the scanner's guarded API client, never re-reads a README and
never rewrites the source index. Outcomes are proposals for a reviewer.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
from urllib.parse import quote

from scan_sources import GitHub, ScanError, load_resume, now, repository_ineligibility


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / 'data/source-index.json'
OUTCOMES = ('available', 'renamed', 'transferred', 'ineligible', 'not-found', 'blocked', 'name-reassigned', 'inconclusive')
GONE_STATUSES = {404: 'not-found', 410: 'not-found', 451: 'blocked'}
# Private responses, and responses that do not confirm public status, expose nothing beyond the reason.
HIDDEN_REASONS = {'private', 'public-status-unconfirmed'}
FULL_NAME = r'[A-Za-z0-9-]+/[A-Za-z0-9_.-]+'
POLICY = ('Metadata-only recheck keyed by the scanned numeric repository ID. A recorded name that now leads to another ID is '
          'reported as name-reassigned, never as available. Rate limits, server errors, network failures and unexpected responses '
          'are inconclusive, never not-found. No README is read, and no source record, hash, timestamp or count is rewritten. '
          'Private responses expose no name, URL or ID. Outcomes are proposals for a separate reviewed change.')


def public_repository(repo):
    """Return a validated public repository's ID and full name, or None for anything private or malformed."""
    if (not isinstance(repo, dict) or type(repo.get('id')) is not int or repo['id'] <= 0
            or repository_ineligibility(repo) in HIDDEN_REASONS):
        return None
    name = repo.get('full_name')
    if not isinstance(name, str) or not re.fullmatch(FULL_NAME, name) or repo.get('html_url') != 'https://github.com/' + name:
        return None
    return 'scan-' + str(repo['id']), name


def recorded_name_lookup(api, full_name, identifier):
    """Report whether the scanned name still leads to the scanned ID, to another repository or to nothing."""
    try:
        repo = api.json('/repos/' + quote(full_name, safe='/'))
    except ScanError as error:
        status = {'recorded_name_http_status': error.status}
        if error.status in (404, 410):
            return {'recorded_name_status': 'not-found', **status}
        return {'recorded_name_status': 'inconclusive', 'recorded_name_reason': error.reason, **status}
    # The client returns a body only for a successful response, which this endpoint sends as 200.
    status = {'recorded_name_http_status': 200}
    if isinstance(repo, dict) and repository_ineligibility(repo) in HIDDEN_REASONS:
        return {'recorded_name_status': 'private', **status}
    public = public_repository(repo)
    if public is None:
        return {'recorded_name_status': 'inconclusive', 'recorded_name_reason': 'invalid-repository-metadata', **status}
    if public[0] == identifier:
        return {'recorded_name_status': 'redirects-to-scanned-id', **status}
    return {'recorded_name_status': 'other-repository', **status, 'recorded_name_repository_id': public[0],
            'recorded_name_current_full_name': public[1]}


def check_record(api, record):
    """Classify one retained scan record from its repository ID alone."""
    identifier, recorded = record['id'], record['full_name']
    entry = {'id': identifier, 'recorded_full_name': recorded, 'observed_at': now()}
    try:
        repo = api.json('/repositories/' + identifier[5:])
    except ScanError as error:
        if error.status not in GONE_STATUSES:
            return {**entry, 'outcome': 'inconclusive', 'reason': error.reason, 'http_status': error.status}
        entry.update({'outcome': GONE_STATUSES[error.status], 'http_status': error.status})
        entry.update(recorded_name_lookup(api, recorded, identifier))
        if entry['recorded_name_status'] == 'other-repository':
            entry['outcome'] = 'name-reassigned'
        return entry
    reason = repository_ineligibility(repo) if isinstance(repo, dict) else None
    if reason in HIDDEN_REASONS:
        return {**entry, 'outcome': 'ineligible', 'reason': reason}
    public = public_repository(repo)
    if public is None:
        return {**entry, 'outcome': 'inconclusive', 'reason': 'invalid-repository-metadata', 'http_status': None}
    if public[0] != identifier:
        return {**entry, 'outcome': 'inconclusive', 'reason': 'repository-id-mismatch', 'http_status': None}
    current = public[1]
    if reason:
        entry.update({'outcome': 'ineligible', 'reason': reason})
    elif current == recorded:
        entry['outcome'] = 'available'
    else:
        # An owner login change is a transfer or an account rename; metadata alone cannot tell which.
        same_owner = current.split('/')[0].casefold() == recorded.split('/')[0].casefold()
        entry['outcome'] = 'renamed' if same_owner else 'transferred'
    if current != recorded:
        entry.update({'current_full_name': current, 'current_url': 'https://github.com/' + current})
        entry.update(recorded_name_lookup(api, recorded, identifier))
    return entry


class CountedAPI:
    """Count the metadata requests a run makes, excluding the client's own retries."""
    def __init__(self, api):
        self.api, self.requests = api, 0

    @property
    def rate(self):
        return getattr(self.api, 'rate', {})

    def json(self, path):
        self.requests += 1
        return self.api.json(path)


def run_recheck(api, document, source_sha256, args):
    """Check a bounded, ID-ordered slice of the retained scans; the document itself is only read."""
    records = sorted(document['resources'], key=lambda record: int(record['id'][5:]))
    selected = records[args.offset:args.offset + args.limit]
    report = {
        'report': 'source-availability-recheck', 'policy': POLICY,
        'source': {'path': args.source_label, 'sha256': source_sha256,
                   'completed_at': document['meta'].get('completed_at'),
                   'successful_readme_scans': len(document['resources'])},
        'started_at': now(), 'completed_at': None,
        'selection': {'order': 'numeric-repository-id', 'offset': args.offset, 'limit': args.limit,
                      'selected': len(selected), 'total_records': len(records)},
        'limits': {'requests_per_second': args.requests_per_second, 'core_reserve': args.reserve,
                   'max_consecutive_inconclusive': args.max_consecutive_inconclusive},
        'complete': False, 'stopped_reason': None, 'next_offset': None, 'metadata_requests': 0,
        'counts': dict.fromkeys(OUTCOMES, 0), 'results': [],
    }
    api = CountedAPI(api)
    streak = 0
    for position, record in enumerate(selected):
        remaining = (api.rate.get('core') or {}).get('remaining')
        # Each record needs at most two requests; stop before the shared quota reaches the reserve.
        if remaining is not None and remaining - 2 < args.reserve:
            report['stopped_reason'] = 'core-rate-limit-reserve'
        elif streak >= args.max_consecutive_inconclusive:
            report['stopped_reason'] = 'consecutive-inconclusive-results'
        if report['stopped_reason']:
            report['next_offset'] = args.offset + position
            break
        entry = check_record(api, record)
        streak = streak + 1 if entry['outcome'] == 'inconclusive' else 0
        report['results'].append(entry)
        report['counts'][entry['outcome']] += 1
        if len(report['results']) % 100 == 0:
            print(f'AVAILABILITY_PROGRESS checked={len(report["results"])} selected={len(selected)} requests={api.requests}', flush=True)
    report['complete'] = report['stopped_reason'] is None
    if report['complete'] and args.offset + len(selected) < len(records):
        report['next_offset'] = args.offset + len(selected)
    report['metadata_requests'] = api.requests
    report['completed_at'] = now()
    return report


def write_report(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def summary_lines(report):
    yield 'COUNTS ' + ' '.join(f'{outcome}={count}' for outcome, count in report['counts'].items() if count)
    for entry in report['results']:
        if entry['outcome'] == 'available':
            continue
        details = [entry.get('current_full_name'), entry.get('reason'),
                   entry.get('recorded_name_status'), entry.get('recorded_name_repository_id')]
        yield ' '.join([entry['outcome'], entry['id'], entry['recorded_full_name'], *(str(value) for value in details if value)])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=DEFAULT_SOURCE, help='Retained scan snapshot to read; it is never written')
    parser.add_argument('--output', type=Path, help='Report path outside data/; defaults to .cache/source-availability-<UTC date>.json')
    parser.add_argument('--limit', type=int, default=500, help='Maximum records to check in this run, in numeric-ID order')
    parser.add_argument('--offset', type=int, default=0, help='Start position in numeric-ID order, such as a previous report\'s next_offset')
    parser.add_argument('--requests-per-second', type=float, default=5)
    parser.add_argument('--reserve', type=int, default=1000, help='Stop before the core REST quota falls below this many requests')
    parser.add_argument('--max-consecutive-inconclusive', type=int, default=10, help='Stop after this many inconclusive records in a row')
    args = parser.parse_args(argv)
    if (not 1 <= args.limit <= 5000 or args.offset < 0 or not 0 < args.requests_per_second <= 10
            or args.reserve < 0 or args.max_consecutive_inconclusive < 1):
        parser.error('limit must be 1..5000, offset nonnegative, requests-per-second (0,10], reserve nonnegative and max-consecutive-inconclusive positive')
    date = dt.datetime.now(dt.timezone.utc).date().isoformat()
    args.output = args.output or ROOT / '.cache' / f'source-availability-{date}.json'
    output, data = args.output.resolve(), (ROOT / 'data').resolve()
    if output == args.source.resolve() or output.is_relative_to(data):
        parser.error('write the report outside data/; scan evidence is never rewritten')
    try:
        document, source_sha256 = load_resume(args.source)
    except (OSError, ValueError, TypeError, KeyError):
        print('Source snapshot could not be read or has inconsistent identities/counts.', flush=True)
        return 2
    source = args.source.resolve()
    args.source_label = source.relative_to(ROOT).as_posix() if source.is_relative_to(ROOT) else source.name
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if not token:
        print('Set GH_TOKEN or GITHUB_TOKEN, for example GH_TOKEN="$(gh auth token)"; nothing was requested.', flush=True)
        return 2
    api = GitHub(token, args.requests_per_second)
    del token
    report = run_recheck(api, document, source_sha256, args)
    write_report(args.output, report)
    for line in summary_lines(report):
        print(line, flush=True)
    print(f'REPORT {args.output} complete={report["complete"]} stopped_reason={report["stopped_reason"]} '
          f'next_offset={report["next_offset"]} requests={report["metadata_requests"]}', flush=True)
    return 0 if report['complete'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
