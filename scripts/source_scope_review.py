#!/usr/bin/env python3
"""Re-read the exact scanned README of explicitly named records and write a scope review receipt.

Opt-in and bounded: it runs only when invoked with a token in GH_TOKEN or
GITHUB_TOKEN and with up to MAX_IDS source IDs, uses the scanner's guarded API
client and reads only the recorded immutable Git blob. A record yields scope
evidence only when those bytes match its captured byte count and SHA-256. The
receipt keeps URLs, hashes and short notes, never README text, and no upstream
code is run. Scope decisions remain a separate reviewed change.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
from urllib.parse import quote

from scan_sources import MAX_README_BYTES, GitHub, ScanError, load_resume, now, repository_ineligibility
from source_availability import CountedAPI, GONE_STATUSES, HIDDEN_REASONS, public_repository, write_report


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / 'data/source-index.json'
MAX_IDS = 50
SOURCE_ID = r'scan-[1-9][0-9]*'
GIT_SHA = r'[0-9a-f]{40}'
OUTCOMES = ('match', 'mismatch', 'not-scanned', 'identity-changed', 'unavailable', 'ineligible', 'inconclusive')
NOTES = {
    'match': 'The recorded Git blob matches the captured byte count and SHA-256; usable as scope review evidence.',
    'mismatch': 'The recorded Git blob differs from the captured bytes; not usable as scope review evidence.',
    'not-scanned': 'No successful README scan has this ID; nothing was requested.',
    'identity-changed': 'The ID now resolves to another name; run the availability recheck before any scope review.',
    'unavailable': 'The ID no longer resolves; see the availability recheck and the upstream-unavailable reason.',
    'ineligible': 'The ID does not resolve to a confirmed public repository; nothing further was requested.',
    'inconclusive': 'The check could not finish; retry later before relying on this record.',
}
POLICY = ('Explicit-ID review receipts. Only the requested IDs that are successful scans are checked: one repository '
          'metadata request by numeric ID confirms the recorded public name, then one request reads the recorded '
          'advertised Git blob. Only a blob whose bytes match the captured byte count and SHA-256 yields scope evidence; '
          'a mismatch is recorded and never accepted automatically. Advertised and computed Git identifiers are reported '
          'separately. No README text is stored, no upstream code is run, and no source record or scope decision is written.')


def blob_digests(content):
    return {'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest(),
            'git_sha': hashlib.sha1(b'blob ' + str(len(content)).encode('ascii') + b'\0' + content).hexdigest()}


def receipt(record, outcome, **details):
    entry = {'id': record['id'], 'recorded_full_name': record['full_name'], 'readme_url': record.get('readme_url'),
             'advertised_git_sha': record.get('readme_git_sha'),
             'captured_content_git_sha': record.get('readme_content_git_sha'),
             'captured_bytes': record.get('readme_bytes'), 'captured_sha256': record.get('readme_sha256'),
             'observed_at': now(), 'outcome': outcome, **details, 'note': NOTES[outcome]}
    if outcome == 'match':
        # Exactly the fields a source-scope.json decision binds to the scanned snapshot.
        entry['scope_evidence'] = {'readme_sha256': record['readme_sha256'], 'evidence_url': record['readme_url']}
    return entry


def review_record(api, record):
    """Return (receipt, verified README bytes or None) for one successful scan."""
    identifier, recorded, oid = record['id'], record['full_name'], record.get('readme_git_sha')
    if not isinstance(oid, str) or not re.fullmatch(GIT_SHA, oid):
        return receipt(record, 'inconclusive', reason='invalid-recorded-git-sha'), None
    try:
        repo = api.json('/repositories/' + identifier[5:])
    except ScanError as error:
        outcome = 'unavailable' if error.status in GONE_STATUSES else 'inconclusive'
        return receipt(record, outcome, reason=error.reason, http_status=error.status), None
    if isinstance(repo, dict) and repository_ineligibility(repo) in HIDDEN_REASONS:
        return receipt(record, 'ineligible', reason=repository_ineligibility(repo)), None
    public = public_repository(repo)
    if public is None or public[0] != identifier:
        return receipt(record, 'inconclusive', reason='repository-identity-unconfirmed'), None
    if public[1] != recorded:
        return receipt(record, 'identity-changed', current_full_name=public[1]), None
    # An archived or fork repository stays public; the reviewer sees its status beside the bytes.
    status = {'repository_status': repository_ineligibility(repo)} if repository_ineligibility(repo) else {}
    blob_path = '/repos/' + quote(recorded, safe='/') + '/git/blobs/' + oid
    blob_url = 'https://api.github.com' + blob_path
    try:
        blob = api.json(blob_path)
    except ScanError as error:
        return receipt(record, 'inconclusive', reason=error.reason, http_status=error.status, blob_api_url=blob_url), None
    content = None
    if (isinstance(blob, dict) and blob.get('sha') == oid and type(blob.get('size')) is int
            and 0 <= blob['size'] <= MAX_README_BYTES and blob.get('encoding') == 'base64'
            and isinstance(blob.get('content'), str)):
        try:
            content = base64.b64decode(re.sub(r'\s', '', blob['content']), validate=True)
        except ValueError:
            content = None
    observed = blob_digests(content) if content is not None else None
    # The object must be the one requested before its bytes can say anything about the capture.
    if observed is None or observed['git_sha'] != oid or observed['bytes'] != blob['size']:
        return receipt(record, 'inconclusive', reason='invalid-readme-blob', blob_api_url=blob_url), None
    details = {**status, 'blob_api_url': blob_url, 'blob_bytes': observed['bytes'], 'blob_sha256': observed['sha256'],
               'blob_content_git_sha': observed['git_sha']}
    if observed['bytes'] != record.get('readme_bytes') or observed['sha256'] != record.get('readme_sha256'):
        return receipt(record, 'mismatch', **details), None
    return receipt(record, 'match', **details), content


def run_review(api, document, source_sha256, identifiers, source_label, show=None):
    """Check the requested IDs in the given order; the source document is only read."""
    records = {record['id']: record for record in document['resources']}
    report = {
        'report': 'source-scope-review-receipts', 'policy': POLICY,
        'source': {'path': source_label, 'sha256': source_sha256, 'completed_at': document['meta'].get('completed_at')},
        'started_at': now(), 'completed_at': None, 'requested_ids': list(identifiers),
        'requests': 0, 'counts': dict.fromkeys(OUTCOMES, 0), 'receipts': [],
    }
    api = CountedAPI(api)
    for identifier in identifiers:
        record = records.get(identifier)
        if record is None:
            # Failed attempts and unknown IDs are not README scans; nothing is requested for them.
            entry, content = {'id': identifier, 'observed_at': now(), 'outcome': 'not-scanned',
                              'note': NOTES['not-scanned']}, None
        else:
            entry, content = review_record(api, record)
        report['receipts'].append(entry)
        report['counts'][entry['outcome']] += 1
        if show is not None and content is not None:
            show(entry, content)
    report['requests'] = api.requests
    report['completed_at'] = now()
    return report


def print_readme(entry, content):
    """Show verified bytes to the reviewer only; they are untrusted upstream text and are never written."""
    try:
        text = content.decode('utf-8')
    except UnicodeDecodeError:
        print(f'README {entry["id"]} is not UTF-8 text; not shown.', flush=True)
        return
    print(f'----- BEGIN README {entry["id"]} sha256={entry["blob_sha256"]} (untrusted upstream text) -----', flush=True)
    print(text, flush=True)
    print(f'----- END README {entry["id"]} -----', flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ids', nargs='+', metavar='scan-ID', help=f'Source IDs to review, at most {MAX_IDS}')
    parser.add_argument('--source', type=Path, default=DEFAULT_SOURCE, help='Retained scan snapshot to read; it is never written')
    parser.add_argument('--output', type=Path, help='Receipt path outside data/; defaults to .cache/source-scope-review-<UTC date>.json')
    parser.add_argument('--print-readme', action='store_true', help='Print each verified README to standard output; it is not saved')
    parser.add_argument('--requests-per-second', type=float, default=5)
    args = parser.parse_args(argv)
    if (len(args.ids) > MAX_IDS or len(set(args.ids)) != len(args.ids)
            or not all(re.fullmatch(SOURCE_ID, identifier) for identifier in args.ids)):
        parser.error(f'name 1..{MAX_IDS} distinct source IDs such as scan-123')
    if not 0 < args.requests_per_second <= 10:
        parser.error('requests-per-second must be in (0,10]')
    date = dt.datetime.now(dt.timezone.utc).date().isoformat()
    args.output = args.output or ROOT / '.cache' / f'source-scope-review-{date}.json'
    output, data = args.output.resolve(), (ROOT / 'data').resolve()
    if output == args.source.resolve() or output.is_relative_to(data):
        parser.error('write the receipt outside data/; scan evidence is never rewritten')
    try:
        document, source_sha256 = load_resume(args.source)
    except (OSError, ValueError, TypeError, KeyError):
        print('Source snapshot could not be read or has inconsistent identities/counts.', flush=True)
        return 2
    source = args.source.resolve()
    source_label = source.relative_to(ROOT).as_posix() if source.is_relative_to(ROOT) else source.name
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if not token:
        print('Set GH_TOKEN or GITHUB_TOKEN, for example GH_TOKEN="$(gh auth token)"; nothing was requested.', flush=True)
        return 2
    api = GitHub(token, args.requests_per_second)
    del token
    report = run_review(api, document, source_sha256, args.ids, source_label,
                        print_readme if args.print_readme else None)
    write_report(args.output, report)
    for entry in report['receipts']:
        print(' '.join(str(value) for value in (entry['outcome'], entry['id'], entry.get('recorded_full_name'),
                                                entry.get('reason') or entry.get('current_full_name')) if value), flush=True)
    print(f'RECEIPT {args.output} requests={report["requests"]} '
          + ' '.join(f'{outcome}={count}' for outcome, count in report['counts'].items() if count), flush=True)
    return 0 if report['counts']['match'] == len(args.ids) else 1


if __name__ == '__main__':
    raise SystemExit(main())
