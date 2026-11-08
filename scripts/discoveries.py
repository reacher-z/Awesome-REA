#!/usr/bin/env python3
"""Automated discovery batches: exact verified README captures published as an unreviewed queue.

A scheduled scan checkpoint holds tens of thousands of verified README captures. After each scan,
the ingest selects a bounded batch of captures that pass this repository's own checks, copies each
capture object unchanged into ``data/discoveries/run-<run id>-<attempt>.json`` and records the
scan run, artifact and checkpoint it came from. The records stay ``automated-readme-scan``: they are
not reviewed, translated, curated, run or endorsed, and the website lists them as unreviewed
discoveries. Curating one still follows docs/promotion-worksheet.md and never edits the batch.

Run without options to validate every batch and print the queue size and budget.
"""
from __future__ import annotations

import argparse
from collections import Counter
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = 'data/discoveries'
DOCUMENTATION = frozenset({'README.md'})
# Followed-source lead batches have their own directory and validator (scripts/discovery_leads.py).
LEAD_DIRECTORY = 'leads'
REPOSITORY = 'reacher-z/Awesome-REA'
WORKFLOW_PATH = '.github/workflows/source-scan.yml'
KIND = 'automated-discovery-batch'
REVIEW_STATUS = 'unreviewed'
POLICY = 'strong-reverse-engineering-topics-v1'
ORDER = 'newest-capture-first'
BATCH_NAME = re.compile(r'run-([1-9][0-9]{0,19})-([1-9][0-9]{0,2})')
# Growth budget. Each run adds at most MAX_BATCH_RECORDS records. Once the totals are reached the
# ingest stops and reports it instead of growing Git further; raising them is a reviewed change.
MAX_BATCH_RECORDS = 300
MAX_TOTAL_RECORDS = 25_000
MAX_BATCH_BYTES = 2 * 1024 * 1024
MAX_TOTAL_BYTES = 64 * 1024 * 1024
SKIP_REASONS = ('already-listed', 'already-curated', 'name-conflict', 'duplicate-readme', 'privacy', 'over-limit')
BATCH_FIELDS = {'schema_version', 'kind', 'batch_id', 'review_status', 'ingested_at', 'selection', 'source', 'resources'}
SELECTION_FIELDS = {'policy', 'order', 'record_limit', 'eligible_count', 'selected_count', 'selected_ids',
                    'record_sha256', 'skipped_counts'}
SOURCE_FIELDS = {'repository', 'workflow_path', 'workflow_id', 'run_id', 'run_attempt', 'event', 'head_sha',
                 'artifact_id', 'artifact_name', 'artifact_digest', 'checkpoint_sha256', 'receipt_sha256',
                 'scan_started_at', 'scan_completed_at', 'scan_outcome', 'capture_counts', 'integrity_counts'}
COUNT_FIELDS = {'successful_readme_scans', 'failed', 'attempted_readme_scans', 'unique_repos', 'unattempted_candidates'}
INTEGRITY_FIELDS = {'qualified', 'legacy_unknown', 'mismatched'}
# Every outcome with which the scheduled scanner saves a validated checkpoint (scheduled_source_scan.orchestrate).
SCAN_OUTCOMES = ('target-reached', 'partial', 'time-budget', 'global-target-already-reached', 'bootstrap-imported')
INGEST_BRANCH = 'automation/discovery-ingest'
INGEST_AUTHOR = 'github-actions[bot]'
TIMESTAMP = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|\+00:00)')


def strong_topics():
    from public_source_supplements import STRONG_TOPICS
    return STRONG_TOPICS


def data_asset_query_match(record: dict) -> bool:
    from scan_sources import DATA_ASSET_QUERY_BASES
    queries = record.get('matched_queries')
    if not isinstance(queries, list):
        return False
    return any(isinstance(query, str) and any(query.startswith(base + ' ') or query == base
               for base in DATA_ASSET_QUERY_BASES) for query in queries)


def digest(value) -> str:
    """The same canonical capture fingerprint as the public supplement layer."""
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def batch_bytes(batch: dict) -> bytes:
    """Repository JSON format: two-space indentation, literal non-ASCII text, trailing newline."""
    return (json.dumps(batch, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')


def parse_time(value) -> dt.datetime:
    if not isinstance(value, str) or not TIMESTAMP.fullmatch(value):
        raise ValueError('expected a UTC ISO timestamp')
    return dt.datetime.fromisoformat(value.replace('Z', '+00:00'))


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


_PRIVACY_DETECTOR = None


def privacy_detector():
    """The repository's privacy guard (scripts/privacy_guard.py), built once."""
    global _PRIVACY_DETECTOR
    if _PRIVACY_DETECTOR is None:
        from privacy_guard import PARTS, PROTECTED, SALT, Detector
        _PRIVACY_DETECTOR = Detector(SALT, PROTECTED, PARTS)
    return _PRIVACY_DETECTOR


def protected_identifier(record) -> bool:
    """Whether a capture names or links a person the maintainer asked to keep out of the collection."""
    return bool(privacy_detector().scan_text(json.dumps(record, ensure_ascii=False), 'capture'))


def record_problems(record, *, privacy: bool = True) -> list[str]:
    """The publication checks for one successful capture plus this layer's qualification and screen.

    Selection runs the privacy check separately so that it can count those skips.
    """
    from scheduled_source_scan import RECORD_SCHEMA, validate_shape
    from source_descriptions import validate_description_capture
    from validate import TARGETS, parse_iso, validate_readme_evidence
    from review_pr import private_json_locations
    if not isinstance(record, dict):
        return ['capture must be an object']
    problems = []
    try:
        validate_shape(record, RECORD_SCHEMA)
    except ValueError:
        problems.append('capture has fields or value types outside the scanner record schema')
    identifier = record.get('id')
    if not isinstance(identifier, str) or not re.fullmatch(r'scan-[1-9][0-9]*', identifier):
        problems.append('capture needs a scan-<numeric repository ID> identifier')
    if record.get('scan_status') != 'readme-scanned' or record.get('verification') != 'automated-readme-scan':
        problems.append('capture must keep its automated README scan labels')
    if (record.get('readme_git_sha_matches_content') is not True
            or record.get('readme_git_sha') != record.get('readme_content_git_sha')):
        problems.append('capture needs an explicit README Git blob hash match')
    topics = record.get('topics')
    if not isinstance(topics, list) or not (strong_topics().intersection(topics) or data_asset_query_match(record)):
        problems.append('capture needs a reverse-engineering topic or reconstruction phrase query')
    errors = []
    validate_description_capture(record, errors, 'capture')
    validate_readme_evidence(record, 'capture', errors)
    problems.extend(error.removeprefix('capture: ') for error in errors)
    if type(record.get('readme_bytes')) is not int or record['readme_bytes'] <= 0:
        problems.append('capture needs a positive README byte count')
    if not isinstance(record.get('targets'), list) or any(target not in TARGETS for target in record['targets']):
        problems.append('capture has invalid automatic target labels')
    if type(record.get('stars')) is not int or record['stars'] < 0:
        problems.append('capture stars must be a nonnegative snapshot count')
    try:
        parse_iso(record.get('observed_at'), require_time=True)
        parse_time(record.get('observed_at'))
    except (ValueError, TypeError):
        problems.append('capture needs a UTC README observation time')
    if privacy and private_json_locations(record):
        problems.append('capture contains a credential-like value or personal path')
    if privacy and protected_identifier(record):
        problems.append('capture names or links a person the collection keeps out')
    return problems


def batch_files(root: Path = ROOT) -> list[Path]:
    """Batch files in run order; anything else in the directory is an error, never silently skipped.

    ``load_batches`` returns the batches themselves in ingest order.
    """
    directory = Path(root) / DIRECTORY
    if not directory.is_dir():
        return []
    files, unexpected = [], []
    for path in directory.iterdir():
        if path.name in DOCUMENTATION and path.is_file() and not path.is_symlink():
            continue
        if path.name == LEAD_DIRECTORY and path.is_dir() and not path.is_symlink():
            continue
        match = BATCH_NAME.fullmatch(path.stem) if path.suffix == '.json' else None
        if not match or not path.is_file() or path.is_symlink():
            unexpected.append(path.name)
        else:
            files.append((int(match[1]), int(match[2]), path))
    if unexpected:
        raise ValueError(f'{DIRECTORY} contains unexpected entries: ' + ', '.join(sorted(unexpected)[:5]))
    return [path for _, _, path in sorted(files)]


def validate_batch(batch, name: str, *, now: dt.datetime | None = None) -> list[str]:
    """Return problems for one batch; record problems name the source ID, never upstream text."""
    where = f'{DIRECTORY}/{name}.json'
    if not isinstance(batch, dict) or set(batch) != BATCH_FIELDS:
        return [f'{where}: expected exactly the discovery batch fields']
    problems = []
    if type(batch['schema_version']) is not int or batch['schema_version'] != 1 or batch['kind'] != KIND:
        problems.append(f'{where}: unsupported batch schema or kind')
    if batch['batch_id'] != name:
        problems.append(f'{where}: batch_id must match the file name')
    if batch['review_status'] != REVIEW_STATUS:
        problems.append(f'{where}: automated discovery batches stay unreviewed')
    now = now or dt.datetime.now(dt.timezone.utc)
    try:
        ingested = parse_time(batch['ingested_at'])
        if ingested > now + dt.timedelta(minutes=10):
            problems.append(f'{where}: ingested_at is in the future')
    except ValueError:
        ingested = None
        problems.append(f'{where}: ingested_at must be a UTC timestamp')
    source = batch['source']
    match = BATCH_NAME.fullmatch(name)
    if not isinstance(source, dict) or set(source) != SOURCE_FIELDS:
        problems.append(f'{where}: expected exactly the scan source fields')
    else:
        positive = all(type(source[key]) is int and source[key] > 0
                       for key in ('workflow_id', 'run_id', 'run_attempt', 'artifact_id'))
        if (source['repository'] != REPOSITORY or source['workflow_path'] != WORKFLOW_PATH or not positive
                or source['event'] not in ('schedule', 'workflow_dispatch')
                or not re.fullmatch(r'[0-9a-f]{40}', str(source['head_sha']))
                or source['artifact_name'] != f"readme-scan-checkpoint-{source['run_attempt']}"
                or not re.fullmatch(r'sha256:[0-9a-f]{64}', str(source['artifact_digest']))
                or not all(re.fullmatch(r'[0-9a-f]{64}', str(source[key])) for key in ('checkpoint_sha256', 'receipt_sha256'))
                or source['scan_outcome'] not in SCAN_OUTCOMES
                or not isinstance(source['capture_counts'], dict) or set(source['capture_counts']) != COUNT_FIELDS
                or not isinstance(source['integrity_counts'], dict) or set(source['integrity_counts']) != INTEGRITY_FIELDS
                or any(type(value) is not int or value < 0
                       for value in [*source['capture_counts'].values(), *source['integrity_counts'].values()])):
            problems.append(f'{where}: invalid scan run, artifact or checkpoint provenance')
        elif not match or (int(match[1]), int(match[2])) != (source['run_id'], source['run_attempt']):
            problems.append(f'{where}: file name must name the scan run and attempt')
        try:
            started, completed = parse_time(source['scan_started_at']), parse_time(source['scan_completed_at'])
            if not started <= completed or (ingested is not None and completed > ingested):
                problems.append(f'{where}: scan times must precede ingestion')
        except (ValueError, TypeError):
            problems.append(f'{where}: invalid scan timestamps')
    records = batch['resources']
    if not isinstance(records, list) or not 0 < len(records) <= MAX_BATCH_RECORDS:
        return problems + [f'{where}: a batch holds 1 to {MAX_BATCH_RECORDS} capture records']
    identifiers = []
    for index, record in enumerate(records):
        label = record.get('id') if isinstance(record, dict) and isinstance(record.get('id'), str) else f'record {index}'
        label = label if re.fullmatch(r'scan-[0-9]+', label) else f'record {index}'
        for problem in record_problems(record):
            problems.append(f'{where}: {label}: {problem}')
        if isinstance(record, dict):
            identifiers.append(record.get('id'))
            try:
                if ingested is not None and parse_time(record.get('observed_at')) > ingested:
                    problems.append(f'{where}: {label}: capture is newer than the ingest')
            except ValueError:
                pass
    selection = batch['selection']
    if not isinstance(selection, dict) or set(selection) != SELECTION_FIELDS:
        return problems + [f'{where}: expected exactly the selection fields']
    skipped = selection['skipped_counts']
    if (selection['policy'] != POLICY or selection['order'] != ORDER
            or type(selection['record_limit']) is not int or not 0 < selection['record_limit'] <= MAX_BATCH_RECORDS
            or len(records) > selection['record_limit']
            or type(selection['selected_count']) is not int or selection['selected_count'] != len(records)
            or type(selection['eligible_count']) is not int or selection['eligible_count'] < len(records)
            or not isinstance(skipped, dict) or set(skipped) != set(SKIP_REASONS)
            or any(type(value) is not int or value < 0 for value in skipped.values())):
        problems.append(f'{where}: invalid selection policy, limit or counts')
    if selection['selected_ids'] != identifiers or len(set(identifiers)) != len(identifiers):
        problems.append(f'{where}: selected_ids must list the distinct capture IDs in order')
    if selection['record_sha256'] != {row.get('id'): digest(row) for row in records if isinstance(row, dict)}:
        problems.append(f'{where}: record_sha256 must fingerprint every exact capture object')
    return problems


def load_batches(root: Path = ROOT, *, now: dt.datetime | None = None) -> tuple[list[dict], list[str]]:
    """Read and validate every batch, plus the queue-wide identity rules and growth budget."""
    import strict_json
    problems, batches = [], []
    try:
        paths = batch_files(root)
    except ValueError as error:
        return [], [str(error)]
    total_bytes = 0
    for path in paths:
        raw = path.read_bytes()
        total_bytes += len(raw)
        if len(raw) > MAX_BATCH_BYTES:
            problems.append(f'{DIRECTORY}/{path.name}: batch exceeds {MAX_BATCH_BYTES:,} bytes')
            continue
        try:
            batch = strict_json.loads(raw.decode('utf-8'))
        except (UnicodeError, ValueError):
            problems.append(f'{DIRECTORY}/{path.name}: expected strict UTF-8 JSON')
            continue
        found = validate_batch(batch, path.stem, now=now)
        if not found and raw != batch_bytes(batch):
            found.append(f'{DIRECTORY}/{path.name}: use the repository JSON format (two-space indent, trailing newline)')
        problems.extend(found)
        if not found:
            batches.append(batch)
    # Queue order is ingest order: a rerun of an older scan run can be ingested after a newer one.
    batches.sort(key=lambda batch: (parse_time(batch['ingested_at']), batch['source']['run_id'], batch['source']['run_attempt']))
    seen_ids, seen_names, seen_readmes = set(), {}, set()
    for batch in batches:
        for record in batch['resources']:
            name = record['full_name'].casefold()
            if record['id'] in seen_ids:
                problems.append(f"{DIRECTORY}/{batch['batch_id']}.json: {record['id']}: already listed in an earlier batch")
            if seen_names.get(name, record['id']) != record['id']:
                problems.append(f"{DIRECTORY}/{batch['batch_id']}.json: {record['id']}: repository name already belongs to {seen_names[name]}")
            if record['readme_sha256'] in seen_readmes:
                problems.append(f"{DIRECTORY}/{batch['batch_id']}.json: {record['id']}: README duplicates an earlier discovery")
            seen_ids.add(record['id']); seen_names.setdefault(name, record['id']); seen_readmes.add(record['readme_sha256'])
    total = sum(len(batch['resources']) for batch in batches)
    if total > MAX_TOTAL_RECORDS or total_bytes > MAX_TOTAL_BYTES:
        problems.append(f'{DIRECTORY}: {total:,} records in {total_bytes:,} bytes exceed the discovery budget '
                        f'({MAX_TOTAL_RECORDS:,} records, {MAX_TOTAL_BYTES:,} bytes)')
    return batches, problems


def existing_identities(root: Path = ROOT, batches: list[dict] | None = None) -> dict:
    """IDs, names and README hashes already published by any repository layer."""
    import strict_json
    index = strict_json.load_path(Path(root) / 'data/source-index.json')
    rows = [*index['resources'], *index.get('failures', [])]
    registry = Path(root) / 'data/source-supplements/index.json'
    if registry.is_file():
        for name in strict_json.load_path(registry)['batches']:
            rows.extend(strict_json.load_path(Path(root) / 'data/source-supplements' / f'{name}.json')['resources'])
    if batches is None:
        batches, problems = load_batches(root)
        if problems:
            raise ValueError('Existing discovery batches are invalid: ' + '; '.join(problems[:3]))
    rows.extend(record for batch in batches for record in batch['resources'])
    names = {}
    for row in rows:
        names.setdefault(str(row.get('full_name', '')).casefold(), row.get('id'))
    return {'ids': {row.get('id') for row in rows}, 'names': names,
            'readmes': {row['readme_sha256'] for row in rows if isinstance(row.get('readme_sha256'), str)},
            'records': sum(len(batch['resources']) for batch in batches),
            'bytes': sum(len(batch_bytes(batch)) for batch in batches)}


def curated_urls(root: Path = ROOT) -> set[str]:
    import strict_json
    urls = set()
    for name in ('data/rea-resources.json', 'data/tool-resources.json'):
        for record in strict_json.load_path(Path(root) / name):
            urls.add(str(record.get('url', '')).rstrip('/').casefold())
    return urls


def newest_first(record: dict):
    return (-parse_time(record['observed_at']).timestamp(), int(record['id'][5:]))


def select_records(resources: list, existing: dict, curated: set[str], limit: int) -> tuple[list[dict], int, Counter]:
    """Choose up to ``limit`` exact captures, newest first; return them, the eligible count and skips."""
    from review_pr import private_json_locations
    skipped = Counter({reason: 0 for reason in SKIP_REASONS})
    topics, eligible = strong_topics(), []
    for record in resources:
        # Cheap qualification and query/topic screen first; the full record checks run on the remainder.
        if (not isinstance(record, dict) or record.get('scan_status') != 'readme-scanned'
                or record.get('readme_git_sha_matches_content') is not True
                or not isinstance(record.get('topics'), list)
                or not (topics.intersection(record['topics']) or data_asset_query_match(record))
                or record_problems(record, privacy=False)):
            continue
        if record['id'] in existing['ids']:
            skipped['already-listed'] += 1
            continue
        eligible.append(record)
    eligible.sort(key=newest_first)
    selected, names, readmes = [], dict(existing['names']), set(existing['readmes'])
    for record in eligible:
        name = record['full_name'].casefold()
        if record['url'].rstrip('/').casefold() in curated:
            skipped['already-curated'] += 1
        elif names.get(name, record['id']) != record['id']:
            skipped['name-conflict'] += 1
        elif record['readme_sha256'] in readmes:
            skipped['duplicate-readme'] += 1
        elif private_json_locations(record) or protected_identifier(record):
            skipped['privacy'] += 1
        elif len(selected) >= limit:
            skipped['over-limit'] += 1
        else:
            selected.append(record)
            names[name] = record['id']
            readmes.add(record['readme_sha256'])
    return selected, len(eligible), skipped


def build_batch(document: dict, receipt: dict, source: dict, existing: dict, curated: set[str], *,
                ingested_at: str) -> tuple[dict | None, str]:
    """Return (batch, status) for a validated checkpoint; status explains an empty result."""
    remaining = MAX_TOTAL_RECORDS - existing['records']
    if remaining <= 0 or existing['bytes'] >= MAX_TOTAL_BYTES:
        return None, 'budget-reached'
    limit = min(MAX_BATCH_RECORDS, remaining)
    selected, eligible, skipped = select_records(document['resources'], existing, curated, limit)
    while selected:
        batch = {
            'schema_version': 1, 'kind': KIND,
            'batch_id': f"run-{source['run_id']}-{source['run_attempt']}",
            'review_status': REVIEW_STATUS, 'ingested_at': ingested_at,
            'selection': {
                'policy': POLICY, 'order': ORDER, 'record_limit': limit, 'eligible_count': eligible,
                'selected_count': len(selected), 'selected_ids': [row['id'] for row in selected],
                'record_sha256': {row['id']: digest(row) for row in selected},
                'skipped_counts': {reason: skipped[reason] for reason in SKIP_REASONS},
            },
            'source': {**source,
                       'scan_started_at': receipt['started_at'], 'scan_completed_at': receipt['completed_at'],
                       'scan_outcome': receipt['outcome'], 'capture_counts': receipt['counts'],
                       'integrity_counts': receipt['integrity_counts']},
            'resources': selected,
        }
        size = len(batch_bytes(batch))
        if size <= MAX_BATCH_BYTES and existing['bytes'] + size <= MAX_TOTAL_BYTES:
            return batch, 'selected'
        # Shrink to the byte budget; the dropped captures remain eligible for a later run.
        drop = max(1, len(selected) // 10)
        skipped['over-limit'] += drop
        selected = selected[:-drop]
    return None, 'nothing-new' if not eligible else 'budget-reached'


def summary(root: Path = ROOT) -> dict:
    batches, problems = load_batches(root)
    records = sum(len(batch['resources']) for batch in batches)
    size = sum(path.stat().st_size for path in batch_files(root))
    latest = batches[-1] if batches else None
    return {'batches': len(batches), 'records': records, 'bytes': size, 'problems': problems,
            'record_budget': MAX_TOTAL_RECORDS, 'byte_budget': MAX_TOTAL_BYTES,
            'last_successful_ingest_at': latest['ingested_at'] if latest else None,
            'last_batch_id': latest['batch_id'] if latest else None}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--json', action='store_true', help='print the summary as JSON')
    args = parser.parse_args()
    report = summary(ROOT)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for problem in report['problems']:
            print(f'- {problem}', file=sys.stderr)
        print(f"Discovery queue: {report['records']:,} unreviewed records in {report['batches']} batch(es), "
              f"{report['bytes']:,} bytes (budget {MAX_TOTAL_RECORDS:,} records, {MAX_TOTAL_BYTES:,} bytes); "
              f"last ingest {report['last_successful_ingest_at'] or 'none'}.")
    return 1 if report['problems'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
