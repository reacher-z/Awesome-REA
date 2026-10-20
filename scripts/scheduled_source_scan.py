#!/usr/bin/env python3
"""Bounded, data-only checkpoint orchestration for the scheduled README scanner."""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import stat
import subprocess
import sys
import time
import zipfile
from types import SimpleNamespace
from urllib.error import HTTPError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from review_pr import parse_json, private_json_locations
from scan_sources import GitHub, QUERY_BASES, run_scan
import search_frontier
from validate import validate_source_index

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = 'source-scan.yml'
ARTIFACT = 'readme-scan-checkpoint'
MAX_SCAN_BYTES = 512 * 1024 * 1024
MAX_FRONTIER_BYTES = 256 * 1024 * 1024
MAX_API_BYTES = 12 * 1024 * 1024
MAX_ARCHIVE_BYTES = 512 * 1024 * 1024
MAX_RECEIPT_BYTES = 8 * 1024 * 1024
MAX_TOTAL_BYTES = MAX_SCAN_BYTES + MAX_FRONTIER_BYTES + MAX_RECEIPT_BYTES
CHUNK_BYTES = 1024 * 1024
NEW_SUCCESSES = 2000
GLOBAL_TARGET = 160000
SCAN_SECONDS = 38 * 60
APPROVED_QUERIES = [*QUERY_BASES,
                    'topic:screenshot-to-code', 'topic:website-clone',
                    '"website" "reconstruction" in:description', '"pixel-perfect" "clone" in:description',
                    'topic:game-recreation', 'topic:game-reimplementation',
                    '"game" "reimplementation" in:description', '"UI" "reconstruction" in:description',
                    'topic:app-clone', '"reverse engineering" in:readme', '"pixel perfect" "clone" in:readme',
                    '逆向 in:readme', '"clean room" in:readme', '"game" "reimplementation" in:readme',
                    '"网页" "复刻" in:readme', '"游戏" "复刻" in:readme']
RECORD_FIELDS = set('archived category classification_origin classification_reference_ids classification_engine_version '
                    'description_capture_policy description_en description_language description_omission description_origin '
                    'description_zh description_zh_status discovery_methods full_name id license matched_queries '
                    'metadata_observed_at name observed_at pushed_at readme_api_url readme_blob_api_url readme_bytes readme_content_git_sha '
                    'readme_git_sha readme_git_sha_matches_content readme_heading_count readme_integrity_review readme_lines '
                    'readme_path readme_sha256 readme_signals readme_url requirements scan_status seed_paper_ids '
                    'seed_paper_references seed_reference_ids stars targets topics updated_at url verification '
                    'readme_transport readme_graphql_endpoint readme_commit_sha'.split())
FAILURE_FIELDS = set('full_name http_status id observed_at reason scan_status url'.split())
META_FIELDS = set('attempted_readme_scans classification_engine_version classification_policy completed_at current_run '
                  'description_policy discovered_repository_ids failed last_checkpoint_at limitations limits method '
                  'queries readme_heading_count_policy requested_successful_scans resume_history resume_observation_policy '
                  'resume_observations schema_version seed_observations started_at status successful_readme_scans '
                  'target_reached unattempted_candidates unique_repos unique_repos_policy checkpoint_reconciliations'.split())


# Explicit schemas are maintained alongside the scanner's serialization contract.
# Never infer allowed keys from the restored artifact or the current input file.
def fields(names, schema):
    return dict.fromkeys(names.split(), schema)


def nullable(schema):
    return ('nullable', schema)


COUNTS_SCHEMA = fields('successful_readme_scans failed attempted_readme_scans unique_repos unattempted_candidates', int)
INTEGRITY_COUNTS_SCHEMA = fields('qualified legacy_unknown mismatched', int)
GOAL_BASIS = 'explicit-git-blob-sha-match'
INTEGRITY_RECEIPT_FIELDS = {'goal_basis', 'retained_integrity_counts', 'integrity_counts',
                            'new_qualified_successful_scans'}
SEED_IMPORT_SCHEMA = {
    **fields('kind imported_at manifest_sha256 checkpoint_sha256 selected_frontier_sha256 '
             'frontier_policy worker_commit', str),
    'evidence_frontier_sha256': [str],
    'imported_counts': COUNTS_SCHEMA,
}
EXECUTION_SOURCE_SCHEMA = fields('repository commit', str)
LIMITS_SCHEMA = {**fields('workers max_readme_bytes max_pages_per_query per_page', int),
                 **fields('requests_per_second search_interval_seconds', (int, float))}
TRANSPORT_SCHEMA = {
    'method': str, 'batch_size': int, 'outcomes': fields('ok fallback rejected retry deferred', int),
    **fields('request_count response_bytes reported_query_cost queries_with_cost queries_without_cost', int),
    'elapsed_seconds': (int, float), 'last_rate_limit': fields('cost remaining limit reset_at_epoch', int),
}
RUN_SCHEMA = {
    **fields('run_id started_at mode status', str), 'completed_at': nullable(str),
    **fields('query_start_index retained_successful_readme_scans retained_failed_readme_scans '
             'requested_new_successful_scans readme_queue_candidates classification_engine_version '
             'retained_unattempted_repository_ids seed_observation_start_index resume_observation_start_index '
             'query_count seed_observation_count resume_observation_count new_successful_readme_scans '
             'new_failed_readme_scans', int),
    **fields('seed_curated seed_papers', bool), 'query_plan': [str], 'held_repository_ids': [str],
    'readme_transport': TRANSPORT_SCHEMA,
    'scanner_provenance': {'policy': str, **fields('implementation seed_inputs', [{**fields('path sha256', str), 'bytes': int}])},
}
ARTIFACT_REFERENCE_SCHEMA = fields('paper_id field url', str)
QUERY_SCHEMA = {
    **fields('query observed_at run_id status reason', str),
    **fields('page per_page total_count returned retained_attempts_skipped name_collisions_skipped invalid_items_skipped rejected_items '
             'held_candidates_skipped deferred_candidates_skipped', int),
    'http_status': nullable(int), 'incomplete_results': bool,
    'invalid_item_reasons': fields('invalid-repository-metadata', int),
}
OBSERVATION_SCHEMA = {**fields('repository_id observed_at run_id method status reason', str), 'http_status': nullable(int)}
SEED_SCHEMA = {**OBSERVATION_SCHEMA, 'full_name': str, 'reference_ids': [str],
               'artifact_references': [ARTIFACT_REFERENCE_SCHEMA]}
HISTORY_SCHEMA = {
    **fields('started_at completed_at last_checkpoint_at status method description_policy classification_policy', nullable(str)),
    **{key: nullable(value) for key, value in COUNTS_SCHEMA.items()},
    **fields('requested_successful_scans classification_engine_version', nullable(int)),
    **fields('query_count known_repository_ids', int), 'source_sha256': nullable(str),
    'candidate_ids_retained': bool, 'limits': nullable(LIMITS_SCHEMA), 'run': nullable(RUN_SCHEMA),
}
RECONCILIATION_SCHEMA = {
    **fields('mode reconciled_at canonical_sha256 checkpoint_sha256', str),
    **fields('canonical_counts checkpoint_counts', COUNTS_SCHEMA),
    **fields('canonical_current_run checkpoint_current_run', nullable(RUN_SCHEMA)),
    'superseded': [fields('id selected canonical_record_sha256 checkpoint_record_sha256 canonical_status checkpoint_status', str)],
    'checkpoint_observation_counts': fields('queries seed_observations resume_observations', int),
}
RECORD_SCHEMA = {
    **dict.fromkeys(RECORD_FIELDS, str),
    **fields('archived readme_git_sha_matches_content', bool),
    **fields('classification_engine_version stars readme_bytes readme_lines readme_heading_count', int),
    **fields('license updated_at pushed_at readme_path readme_git_sha', nullable(str)),
    **fields('classification_reference_ids discovery_methods matched_queries readme_signals seed_paper_ids '
             'seed_reference_ids targets topics', [str]),
    'seed_paper_references': [ARTIFACT_REFERENCE_SCHEMA],
    'description_omission': {**fields('reason original_sha256', str),
                             **fields('original_characters original_utf8_bytes limit_characters', int)},
    'readme_integrity_review': {**fields('reviewed_at method advertised_blob_sha256', str), 'advertised_blob_bytes': int},
}
META_SCHEMA = {
    **dict.fromkeys(META_FIELDS, str), **COUNTS_SCHEMA,
    **fields('schema_version classification_engine_version requested_successful_scans', int),
    'target_reached': bool, 'completed_at': nullable(str), 'current_run': RUN_SCHEMA,
    'limits': LIMITS_SCHEMA, 'limitations': [str], 'discovered_repository_ids': [str],
    'queries': [QUERY_SCHEMA], 'seed_observations': [SEED_SCHEMA],
    'resume_observations': [OBSERVATION_SCHEMA], 'resume_history': [HISTORY_SCHEMA],
    'checkpoint_reconciliations': [RECONCILIATION_SCHEMA],
}
SNAPSHOT_SCHEMA = {'meta': META_SCHEMA, 'resources': [RECORD_SCHEMA],
                   'failures': [{**dict.fromkeys(FAILURE_FIELDS, str), 'http_status': nullable(int)}]}
RECEIPT_SCHEMA = {
    **fields('schema_version run_id run_attempt new_success_limit scan_seconds workflow_id '
             'restored_run_id restored_artifact_id scanner_exit_code new_successful_scans', int),
    **fields('source_commit started_at completed_at outcome checkpoint_sha256', str),
    **fields('retained_counts counts', COUNTS_SCHEMA), 'reconciliation': RECONCILIATION_SCHEMA,
    'target_reached': bool,
}
FILE_SCHEMA = {'sha256': str, 'bytes': int}
FRONTIER_SUMMARY_SCHEMA = {**fields('requests_recorded candidate_identities pending_candidates', int),
                         'partitions': fields('pending complete split blocked', int),
                         **fields('traversal_finished global_completeness_established readme_successes_measured_here', bool)}
RECEIPT_V2_SCHEMA = {
    **RECEIPT_SCHEMA,
    **fields('global_target_successes planned_new_successes', int),
    **fields('run_target_reached global_target_reached', bool),
    'files': {'checkpoint.json': FILE_SCHEMA, 'frontier.json': FILE_SCHEMA},
    'frontier': FRONTIER_SUMMARY_SCHEMA, 'transport': nullable(TRANSPORT_SCHEMA),
    'reconciliation': {**RECONCILIATION_SCHEMA, 'superseded_count': int, 'superseded_sha256': str},
    'manual_seed_import': SEED_IMPORT_SCHEMA, 'execution_source': EXECUTION_SOURCE_SCHEMA,
    'bootstrap_origins': [SEED_IMPORT_SCHEMA],
    'goal_basis': str, 'retained_integrity_counts': INTEGRITY_COUNTS_SCHEMA,
    'integrity_counts': INTEGRITY_COUNTS_SCHEMA, 'new_qualified_successful_scans': int,
}


def validate_shape(value, schema):
    """Reject unexpected nested keys/containers without echoing untrusted values."""
    if isinstance(schema, tuple) and schema and schema[0] == 'nullable':
        if value is not None:
            validate_shape(value, schema[1])
        return
    if isinstance(schema, dict):
        if not isinstance(value, dict) or set(value) - set(schema):
            raise ValueError('Checkpoint contains unexpected nested fields or object shape; values withheld')
        for key, item in value.items():
            validate_shape(item, schema[key])
    elif isinstance(schema, list):
        if not isinstance(value, list):
            raise ValueError('Checkpoint contains an unexpected nested array shape; values withheld')
        for item in value:
            validate_shape(item, schema[0])
    elif type(value) not in (schema if isinstance(schema, tuple) else (schema,)):
        raise ValueError('Checkpoint contains an unexpected nested value type; values withheld')
    elif isinstance(value, float) and not math.isfinite(value):
        raise ValueError('Checkpoint contains a non-finite numeric value')


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    with temporary.open('w', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    temporary.replace(path)


def file_info(path, bound):
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= bound:
        raise ValueError('Evidence must be a bounded regular file')
    fingerprint = hashlib.sha256()
    size = 0
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(CHUNK_BYTES), b''):
            size += len(block)
            if size > bound:
                raise ValueError('Evidence exceeded its streaming bound')
            fingerprint.update(block)
    return {'sha256': fingerprint.hexdigest(), 'bytes': size}


def validate_resume_identities(document):
    """Validate the scanner's identity contract without parsing the file twice."""
    identities, names = set(), set()
    for field, status in (('resources', 'readme-scanned'), ('failures', 'failed')):
        for row in document[field]:
            identifier, name = row.get('id'), row.get('full_name')
            if (row.get('scan_status') != status or not isinstance(identifier, str)
                    or not re.fullmatch(r'scan-[0-9]+', identifier) or identifier in identities
                    or not isinstance(name, str) or not name or name.casefold() in names):
                raise ValueError('Checkpoint contains inconsistent retained identities')
            identities.add(identifier); names.add(name.casefold())
    meta = document['meta']
    if meta['attempted_readme_scans'] != len(identities):
        raise ValueError('Checkpoint attempted count disagrees with identities')
    if 'discovered_repository_ids' not in meta and (meta['unique_repos'] < len(identities)
            or meta['unattempted_candidates'] != meta['unique_repos'] - len(identities)):
        raise ValueError('Legacy checkpoint discovery counts are inconsistent')


def read_snapshot(path):
    fingerprint = file_info(path, MAX_SCAN_BYTES)['sha256']
    document = parse_json(path.read_text(encoding='utf-8'))
    validate_snapshot(document)
    return document, fingerprint


def validate_snapshot(document):
    """Validate an already parsed seed union without allocating another full copy."""
    if not isinstance(document, dict) or set(document) != {'meta', 'resources', 'failures'}:
        raise ValueError('Checkpoint contains unexpected top-level fields')
    if not isinstance(document['meta'], dict) or set(document['meta']) - META_FIELDS:
        raise ValueError('Checkpoint contains unexpected metadata fields')
    for field, allowed in (('resources', RECORD_FIELDS), ('failures', FAILURE_FIELDS)):
        if not isinstance(document[field], list) or any(not isinstance(row, dict) or set(row) - allowed for row in document[field]):
            raise ValueError('Checkpoint contains unexpected record fields')
    validate_shape(document, SNAPSHOT_SCHEMA)
    if private_json_locations(document):
        raise ValueError('Checkpoint contains credential-like text or a personal path; values withheld')
    if any(type(document['meta'].get(key)) is not int for key in counts(document)):
        raise ValueError('Checkpoint counters must be integers')
    validate_resume_identities(document)
    errors = []
    validate_source_index(document, errors, allow_incomplete=True)
    if errors:
        raise ValueError('Checkpoint failed source-index structure validation')
    for record in document['resources']:
        if 'readme_transport' in record or 'readme_graphql_endpoint' in record or 'readme_commit_sha' in record:
            if (record.get('readme_transport') != 'github-graphql-blob'
                    or record.get('readme_graphql_endpoint') != 'https://api.github.com/graphql'
                    or not re.fullmatch('[0-9a-f]{40}', str(record.get('readme_commit_sha', '')))
                    or record.get('readme_git_sha_matches_content') is not True):
                raise ValueError('Invalid verified GraphQL capture provenance')
    runs = [document['meta'].get('current_run')]
    runs += [entry.get('run') for entry in document['meta'].get('resume_history', [])]
    for entry in document['meta'].get('checkpoint_reconciliations', []):
        runs.extend((entry.get('canonical_current_run'), entry.get('checkpoint_current_run')))
    for run in runs:
        if isinstance(run, dict) and 'readme_transport' in run:
            validate_transport(run['readme_transport'])


def validate_seed_import(value):
    validate_shape(value, SEED_IMPORT_SCHEMA)
    if (set(value) != set(SEED_IMPORT_SCHEMA) or value['kind'] != 'manual-local-union'
            or value['frontier_policy'] != 'selected-seed-frontier'
            or not re.fullmatch('[0-9a-f]{40}', value['worker_commit'])
            or any(not re.fullmatch('[0-9a-f]{64}', value[key]) for key in
                   ('manifest_sha256', 'checkpoint_sha256', 'selected_frontier_sha256'))
            or len(value['evidence_frontier_sha256']) > 4
            or any(not re.fullmatch('[0-9a-f]{64}', item) for item in value['evidence_frontier_sha256'])):
        raise ValueError('Invalid manual seed provenance')
    instant = dt.datetime.fromisoformat(value['imported_at'].replace('Z', '+00:00'))
    if instant.tzinfo is None:
        raise ValueError('Manual seed import time must include its timezone')
    validate_seed_counts(value['imported_counts'])


def validate_seed_counts(value):
    validate_shape(value, COUNTS_SCHEMA)
    if (set(value) != set(COUNTS_SCHEMA) or any(number < 0 for number in value.values())
            or value['attempted_readme_scans'] != value['successful_readme_scans'] + value['failed']
            or value['unique_repos'] != value['attempted_readme_scans'] + value['unattempted_candidates']):
        raise ValueError('Invalid manual seed counters')


def validate_execution_source(value):
    validate_shape(value, EXECUTION_SOURCE_SCHEMA)
    if (set(value) != set(EXECUTION_SOURCE_SCHEMA) or value['repository'] != 'reacher-z/Awesome-REA'
            or not re.fullmatch('[0-9a-f]{40}', value['commit'])):
        raise ValueError('Invalid pinned scanner source')


def snapshot_view(document):
    # Capture records are immutable: copy containers/metadata, not every retained record.
    return {'meta': copy.deepcopy(document['meta']), 'resources': list(document['resources']),
            'failures': list(document['failures'])}


def validate_transport(value):
    validate_shape(value, TRANSPORT_SCHEMA)
    if (value.get('method') != 'github-graphql-verified-blob-with-rest-fallback'
            or type(value.get('batch_size')) is not int or not 1 <= value['batch_size'] <= 16
            or set(value.get('outcomes', {})) != {'ok', 'fallback', 'rejected', 'retry', 'deferred'}):
        raise ValueError('Invalid batch transport metrics')
    for key, item in value.items():
        if key not in ('method', 'outcomes', 'last_rate_limit') and (type(item) not in (int, float) or item < 0):
            raise ValueError('Invalid transport counter')
    if any(number < 0 for number in value['outcomes'].values()) or any(number < 0 for number in value.get('last_rate_limit', {}).values()):
        raise ValueError('Invalid transport quota metric')


def known_ids(document):
    return set(document['meta'].get('discovered_repository_ids', ())) | {
        row['id'] for row in document['resources'] + document.get('failures', [])}


def reconcile(canonical, previous, canonical_sha, previous_sha):
    """Keep unique successful evidence and pending identities, without inventing a scan run."""
    if previous is None:
        return snapshot_view(canonical), {'mode': 'canonical', 'canonical_sha256': canonical_sha}
    canonical_rows = {r['id']: r for r in canonical['resources'] + canonical.get('failures', [])}
    previous_rows = {r['id']: r for r in previous['resources'] + previous.get('failures', [])}
    all_names = {}
    for row in [*previous_rows.values(), *canonical_rows.values()]:
        name = row['full_name'].casefold()
        if name in all_names and all_names[name] != row['id']:
            raise ValueError('Different repository IDs claim the same name; retain both inputs for review')
        all_names[name] = row['id']
    replaced = [{'id': identifier, 'canonical_record_sha256': digest(canonical_rows[identifier]),
                 'checkpoint_record_sha256': digest(row)} for identifier, row in previous_rows.items()
                if identifier in canonical_rows and canonical_rows[identifier] != row]
    checkpoint_covers = (known_ids(canonical) <= known_ids(previous) and set(canonical_rows) <= set(previous_rows)
                         and all(previous_rows[key] == value or previous_rows[key]['scan_status'] == 'readme-scanned'
                                 and value['scan_status'] == 'failed' for key, value in canonical_rows.items()))
    if checkpoint_covers:
        return snapshot_view(previous), {'mode': 'checkpoint-covers-canonical', 'canonical_sha256': canonical_sha,
                                         'checkpoint_sha256': previous_sha, 'canonical_counts': counts(canonical),
                                         'checkpoint_counts': counts(previous), 'superseded': replaced}
    # The published snapshot can fully supersede a checkpoint only if no success or pending ID is lost.
    covered = (known_ids(previous) <= known_ids(canonical)
               and set(previous_rows) <= set(canonical_rows)
               and all(canonical_rows[r['id']]['scan_status'] == 'readme-scanned' for r in previous['resources']))
    if covered:
        return snapshot_view(canonical), {
            'mode': 'canonical-covers-checkpoint', 'canonical_sha256': canonical_sha,
            'checkpoint_sha256': previous_sha, 'checkpoint_counts': counts(previous), 'superseded': replaced,
            'checkpoint_observation_counts': {key: len(previous['meta'].get(key, []))
                                              for key in ('queries', 'seed_observations', 'resume_observations')},
            'checkpoint_current_run': previous['meta'].get('current_run')}
    records, failures, names, superseded = [], [], {}, []
    for identifier in dict.fromkeys([*previous_rows, *canonical_rows]):
        old, published = previous_rows.get(identifier), canonical_rows.get(identifier)
        selected = published or old
        if old and published:
            if old['scan_status'] == 'readme-scanned' and published['scan_status'] == 'failed':
                selected = old
            if old != published:
                superseded.append({'id': identifier, 'selected': 'canonical' if selected is published else 'checkpoint',
                                   'canonical_record_sha256': digest(published), 'checkpoint_record_sha256': digest(old),
                                   'canonical_status': published['scan_status'], 'checkpoint_status': old['scan_status']})
        name = selected['full_name'].casefold()
        if name in names and names[name] != identifier:
            raise ValueError('Different repository IDs claim the same name; retain both inputs for review')
        names[name] = identifier
        (records if selected['scan_status'] == 'readme-scanned' else failures).append(selected)
    meta = copy.deepcopy(previous['meta'])
    previous_run = meta.pop('current_run', None)
    # Deduplicate identical observations; retain both histories, including original run IDs.
    for field in ('queries', 'seed_observations', 'resume_observations', 'resume_history'):
        values, seen = [], set()
        for item in previous['meta'].get(field, []) + canonical['meta'].get(field, []):
            fingerprint = digest(item)
            if fingerprint not in seen:
                values.append(copy.deepcopy(item)); seen.add(fingerprint)
        meta[field] = values
    ids = sorted(known_ids(canonical) | known_ids(previous), key=lambda value: int(value[5:]))
    receipt = {'mode': 'union', 'reconciled_at': now(), 'canonical_sha256': canonical_sha,
               'checkpoint_sha256': previous_sha, 'canonical_counts': counts(canonical),
               'checkpoint_counts': counts(previous), 'canonical_current_run': canonical['meta'].get('current_run'),
               'checkpoint_current_run': previous_run, 'superseded': superseded}
    meta.setdefault('checkpoint_reconciliations', []).append(receipt)
    meta.update(discovered_repository_ids=ids, unique_repos=len(ids), successful_readme_scans=len(records),
                failed=len(failures), attempted_readme_scans=len(records) + len(failures),
                unattempted_candidates=len(ids) - len(records) - len(failures),
                requested_successful_scans=len(records), target_reached=True,
                status='in-progress', completed_at=None, last_checkpoint_at=now())
    return {'meta': meta, 'resources': records, 'failures': failures}, receipt


def counts(document):
    return {key: document['meta'][key] for key in ('successful_readme_scans', 'failed', 'attempted_readme_scans',
                                                   'unique_repos', 'unattempted_candidates')}


def integrity_counts(document):
    """Partition retained captures without upgrading or removing any evidence."""
    result = dict.fromkeys(INTEGRITY_COUNTS_SCHEMA, 0)
    for record in document['resources']:
        if 'readme_git_sha_matches_content' not in record:
            result['legacy_unknown'] += 1
        elif record['readme_git_sha_matches_content'] is True:
            result['qualified'] += 1
        elif record['readme_git_sha_matches_content'] is False:
            result['mismatched'] += 1
        else:
            raise ValueError('Capture integrity flag must be an explicit boolean or absent')
    return result


def validate_integrity_receipt(receipt, document=None):
    """Old receipts remain readable; new qualification fields are inseparable."""
    present = INTEGRITY_RECEIPT_FIELDS.intersection(receipt)
    if not present:
        return  # Historical raw-count receipts never establish the current goal.
    if present != INTEGRITY_RECEIPT_FIELDS or receipt['goal_basis'] != GOAL_BASIS:
        raise ValueError('Qualified goal receipt fields are incomplete or unsupported')
    for name, raw_name in (('retained_integrity_counts', 'retained_counts'), ('integrity_counts', 'counts')):
        value = receipt[name]
        if (not isinstance(value, dict) or set(value) != set(INTEGRITY_COUNTS_SCHEMA)
                or any(type(number) is not int or number < 0 for number in value.values())
                or sum(value.values()) != receipt.get(raw_name, {}).get('successful_readme_scans')):
            raise ValueError('Integrity counts must partition the retained raw captures')
    before, after = receipt['retained_integrity_counts'], receipt['integrity_counts']
    added, planned = receipt['new_qualified_successful_scans'], receipt.get('planned_new_successes')
    target, limit = receipt.get('global_target_successes'), receipt.get('new_success_limit')
    if (type(added) is not int or type(planned) is not int or type(target) is not int or type(limit) is not int
            or min(added, planned, target, limit) < 0 or target == 0 or limit == 0
            or added != after['qualified'] - before['qualified']
            or added != receipt.get('new_successful_scans') or added > planned
            or receipt['counts']['successful_readme_scans'] - receipt['retained_counts']['successful_readme_scans'] != added
            or any(after[key] != before[key] for key in ('legacy_unknown', 'mismatched'))):
        raise ValueError('New successful captures must all have explicit verified integrity')
    expected_plan = 0 if receipt.get('outcome') == 'bootstrap-imported' else min(limit, max(0, target - before['qualified']))
    if (planned != expected_plan or type(receipt.get('global_target_reached')) is not bool
            or receipt['global_target_reached'] != (after['qualified'] >= target)
            or receipt.get('outcome') == 'global-target-already-reached' and after['qualified'] < target
            or receipt.get('run_target_reached') is not (added == planned)
            or receipt.get('target_reached') is not (added == planned)):
        raise ValueError('Goal flags must follow qualified captures, not raw totals')
    if document is not None and after != integrity_counts(document):
        raise ValueError('Receipt integrity counts do not match its checkpoint records')


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        return None


class ActionsAPI:
    def __init__(self, repository, token, deadline=None):
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
            raise ValueError('Invalid repository identity')
        self.repository, self.token, self.deadline = repository, token, deadline

    def _open(self, suffix, *, archive=False):
        remaining = 30 if self.deadline is None else min(30, self.deadline - time.monotonic())
        if remaining <= 0:
            raise ValueError('Checkpoint restore reached its time bound')
        request = Request('https://api.github.com/repos/' + self.repository + ('/' + suffix if suffix else ''), headers={
            'Authorization': 'Bearer ' + self.token, 'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'Awesome-REA-scheduled-scan'})
        try:
            return build_opener(NoRedirect()).open(request, timeout=remaining)
        except HTTPError as error:
            location, code = error.headers.get('Location', ''), error.code
            error.close()
            parsed = urlsplit(location)
            trusted_blob = (parsed.hostname or '').endswith(('.blob.core.windows.net', '.actions.githubusercontent.com'))
            if not archive or code not in (301, 302, 303, 307, 308) or parsed.scheme != 'https' or not trusted_blob or parsed.username or parsed.password:
                raise ValueError('GitHub Actions API request failed; response withheld') from None
            remaining = 30 if self.deadline is None else min(30, self.deadline - time.monotonic())
            if remaining <= 0:
                raise ValueError('Checkpoint restore reached its time bound')
            # Never forward the API authorization header to the signed blob URL.
            return build_opener(NoRedirect()).open(Request(location), timeout=remaining)

    def get(self, suffix):
        with self._open(suffix) as response:
            raw = response.read(MAX_API_BYTES + 1)
        if len(raw) > MAX_API_BYTES:
            raise ValueError('GitHub Actions JSON response exceeds its size bound')
        return parse_json(raw.decode('utf-8'))

    def download(self, suffix, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix('.download')
        try:
            with self._open(suffix, archive=True) as response, temporary.open('wb') as output:
                result = stream_copy(response, output, MAX_ARCHIVE_BYTES, deadline=self.deadline)
            temporary.replace(path)
            return result
        except Exception:
            temporary.unlink(missing_ok=True)
            raise


def stream_copy(source, output, bound, *, deadline=None):
    fingerprint, size = hashlib.sha256(), 0
    while True:
        if deadline is not None and time.monotonic() >= deadline:
            raise ValueError('Evidence transfer exceeded its wall-time budget')
        block = source.read(min(CHUNK_BYTES, bound - size + 1))
        if not block:
            break
        size += len(block)
        if size > bound:
            raise ValueError('Evidence transfer exceeded its byte budget')
        output.write(block); fingerprint.update(block)
    return {'sha256': fingerprint.hexdigest(), 'bytes': size}


def select_checkpoint(api, branch, current_run, current_attempt=1):
    workflow = api.get('actions/workflows/' + WORKFLOW)
    workflow_id = workflow['id']
    if not 1 <= current_attempt <= 10:
        raise ValueError('Run-attempt history exceeds the restore bound')
    prior_attempts = [api.get(f'actions/runs/{current_run}/attempts/{attempt}')
                      for attempt in range(current_attempt - 1, 0, -1)]
    saw_prior_run = False
    for page in range(1, 11):
        response = api.get('actions/workflows/' + WORKFLOW + '/runs?' + urlencode({
            'branch': branch, 'status': 'completed', 'per_page': 100, 'page': page}))
        runs = response['workflow_runs']
        for run in (prior_attempts if page == 1 else []) + runs:
            if ((run.get('id') == current_run and run.get('run_attempt', 0) >= current_attempt)
                    or run.get('status') != 'completed'
                    or run.get('workflow_id') != workflow_id or run.get('head_branch') != branch
                    or run.get('event') not in ('schedule', 'workflow_dispatch')
                    or run.get('head_repository', {}).get('full_name') != api.repository):
                continue
            saw_prior_run = True
            artifacts = api.get(f"actions/runs/{run['id']}/artifacts?per_page=100")
            matches = [item for item in artifacts['artifacts']
                       if item.get('name') == ARTIFACT + '-' + str(run['run_attempt'])]
            if len(matches) > 1:
                raise ValueError('Ambiguous checkpoint artifacts in a trusted run')
            if not matches:
                continue
            artifact = matches[0]
            if artifact.get('expired') or not 0 < artifact.get('size_in_bytes', 0) <= MAX_ARCHIVE_BYTES:
                raise ValueError('Latest checkpoint expired or exceeds bounds; inspect before restarting')
            if artifact.get('workflow_run', {}).get('id') != run['id']:
                raise ValueError('Checkpoint artifact is not bound to its selected run')
            return run, artifact
        if len(runs) < 100:
            if saw_prior_run:
                raise ValueError('Prior scan runs have no recoverable checkpoint; inspect before restarting')
            return None
    raise ValueError('Checkpoint search reached its history bound; inspect before restarting')


def read_frontier(path):
    file_info(path, MAX_FRONTIER_BYTES)
    state = parse_json(path.read_text(encoding='utf-8'))
    search_frontier.validate_frontier(state, approved_queries=APPROVED_QUERIES)
    if private_json_locations(state):
        raise ValueError('Frontier contains credential-like text or a personal path; values withheld')
    return state


def paired_ack_guard(document, frontier):
    attempted = {row['id'][5:] for row in document['resources'] + document['failures']}
    acknowledged = {key for key, row in frontier['candidates'].items() if row['checkpoint_sha256'] is not None}
    if not acknowledged <= attempted:
        raise ValueError('Frontier acknowledges an ID absent from the paired scan evidence')


def merge_frontier_ids(document, frontier):
    """Reconcile saved discovery IDs without claiming new reads or query requests."""
    known = known_ids(document)
    combined = known | {'scan-' + key for key in frontier['candidates']}
    if combined == known:
        return False
    document['meta'].update(discovered_repository_ids=sorted(combined, key=lambda value: int(value[5:])),
                            unique_repos=len(combined),
                            unattempted_candidates=len(combined) - len(document['resources']) - len(document['failures']))
    return True


def unpack_checkpoint(archive_source, artifact, run, directory, *, receipt_out=None):
    # Bytes are accepted for small offline tests; production uses a streamed file.
    if isinstance(archive_source, bytes):
        if len(archive_source) > MAX_ARCHIVE_BYTES:
            raise ValueError('Artifact archive exceeds its byte bound')
        archive_sha = hashlib.sha256(archive_source).hexdigest()
        source = io.BytesIO(archive_source)
    else:
        archive_sha = file_info(Path(archive_source), MAX_ARCHIVE_BYTES)['sha256']
        source = archive_source
    if artifact.get('digest') != 'sha256:' + archive_sha:
        raise ValueError('Artifact archive digest is missing or mismatched')
    bounds = {'checkpoint.json': MAX_SCAN_BYTES, 'frontier.json': MAX_FRONTIER_BYTES,
              'receipt.json': MAX_RECEIPT_BYTES}
    with zipfile.ZipFile(source) as archive:
        entries = archive.infolist()
        names = {entry.filename for entry in entries}
        if (len(entries) != len(names) or not names <= set(bounds) or 'receipt.json' not in names
                or sum(entry.file_size for entry in entries) > MAX_TOTAL_BYTES):
            raise ValueError('Checkpoint archive contains unexpected members or exceeds aggregate bounds')
        for entry in entries:
            mode = entry.external_attr >> 16
            if (entry.is_dir() or stat.S_ISLNK(mode) or stat.S_IFMT(mode) not in (0, stat.S_IFREG)
                    or entry.flag_bits & 1 or not 0 < entry.file_size <= bounds[entry.filename]):
                raise ValueError('Checkpoint archive contains an unsafe or oversized member')
        receipt = parse_json(archive.read('receipt.json').decode('utf-8'))
        version = receipt.get('schema_version')
        if version not in (1, 2):
            raise ValueError('Unsupported checkpoint receipt version')
        expected_names = {'checkpoint.json', 'receipt.json'} | ({'frontier.json'} if version == 2 else set())
        if names != expected_names:
            raise ValueError('Checkpoint archive members do not match its receipt version')
        validate_shape(receipt, RECEIPT_SCHEMA if version == 1 else RECEIPT_V2_SCHEMA)
        if 'manual_seed_import' in receipt:
            validate_seed_import(receipt['manual_seed_import'])
        if 'execution_source' in receipt:
            validate_execution_source(receipt['execution_source'])
        if len(receipt.get('bootstrap_origins', [])) > 1:
            raise ValueError('Multiple bootstrap origins require an explicit reviewed migration')
        for origin in receipt.get('bootstrap_origins', []):
            validate_seed_import(origin)
        if private_json_locations(receipt):
            raise ValueError('Checkpoint receipt contains credential-like text or a personal path; values withheld')
        if (receipt.get('run_id') != run['id'] or receipt.get('run_attempt') != run['run_attempt']
                or receipt.get('workflow_id') != run['workflow_id'] or receipt.get('source_commit') != run['head_sha']):
            raise ValueError('Checkpoint receipt provenance does not match the trusted run')
        expected_files = receipt.get('files', {})
        if version == 2 and set(expected_files) != {'checkpoint.json', 'frontier.json'}:
            raise ValueError('Paired receipt requires both file hashes and byte counts')
        directory.mkdir(parents=True, exist_ok=True)
        for name in sorted(names - {'receipt.json'}):
            destination = directory / name
            temporary = destination.with_suffix('.tmp')
            with archive.open(name) as member, temporary.open('wb') as output:
                info = stream_copy(member, output, bounds[name])
            expected = expected_files.get(name)
            if (version == 2 and info != expected or name == 'checkpoint.json'
                    and info['sha256'] != receipt.get('checkpoint_sha256')):
                temporary.unlink(missing_ok=True)
                raise ValueError('Checkpoint member bytes do not match the receipt')
            temporary.replace(destination)
    document, fingerprint = read_snapshot(directory / 'checkpoint.json')
    if receipt.get('counts') != counts(document):
        raise ValueError('Checkpoint receipt counts do not match the data')
    validate_integrity_receipt(receipt, document)
    frontier = read_frontier(directory / 'frontier.json') if version == 2 else None
    if frontier is not None:
        paired_ack_guard(document, frontier)
        if receipt.get('frontier') != search_frontier.summary(frontier):
            raise ValueError('Frontier receipt counts do not match the paired state')
    if receipt_out is not None:
        receipt_out.update(receipt)
    return document, fingerprint, frontier


class ScheduledTransport:
    """Keep the scheduled run inside bounded observed quota and fallback budgets."""
    def __init__(self, transport, rest):
        self.transport, self.rest = transport, rest
        self.batch_size = transport.batch_size
        self.last_batch_receipts, self.rate_limit = [], {}
        self.reported_cost = self.requests = self.fallbacks = 0

    def fetch_batch(self, repositories):
        remaining = self.rate_limit.get('remaining')
        if self.reported_cost >= 800 or self.requests >= 800 or remaining is not None and remaining < 100:
            self.last_batch_receipts = []
            return {row['id']: {'status': 'deferred', 'retry_after': 60} for row in repositories}
        results = self.transport.fetch_batch(repositories)
        self.last_batch_receipts = self.transport.last_batch_receipts
        self.rate_limit = dict(self.transport.rate_limit)
        self.requests += len(self.last_batch_receipts)
        self.reported_cost += sum(row.get('rate_limit', {}).get('cost', 0) for row in self.last_batch_receipts)
        fallback_ids = [identifier for identifier, value in results.items() if value['status'] == 'fallback']
        core_remaining = self.rest.rate.get('core', {}).get('remaining')
        if self.fallbacks + len(fallback_ids) > 200 or core_remaining is not None and core_remaining < 100 + 3 * len(fallback_ids):
            for identifier in fallback_ids:
                results[identifier] = {'status': 'deferred', 'retry_after': 60}
        elif not any(value['status'] in ('retry', 'deferred') for value in results.values()):
            self.fallbacks += len(fallback_ids)
        return results


def scanner_child(seed, output, frontier_path):
    from scan_graphql_transport import GraphQLReadmeTransport
    document, fingerprint = read_snapshot(seed)
    planned = planned_successes(integrity_counts(document)['qualified'])
    target = len(document['resources']) + planned
    if planned == 0:
        shutil.copyfile(seed, output)
        return 0
    token = os.environ.get('GH_TOKEN', '')
    if not token:
        raise ValueError('The ephemeral GitHub token is unavailable')
    frontier = read_frontier(frontier_path)
    paired_ack_guard(document, frontier)
    args = SimpleNamespace(target=target, workers=4, requests_per_second=2, max_pages=3,
                           candidate_buffer=min(200, max(50, (planned + 9) // 10)),
                           pending_metadata_budget=200, search_request_budget=360,
                           seed_curated=True, seed_papers=True,
                           queries=[query + ' ' + search_frontier.GATES for query in APPROVED_QUERIES], output=output)
    rest = GitHub(token, 2)
    transport = ScheduledTransport(GraphQLReadmeTransport(token, batch_size=16, interval=1.0), rest)
    return run_scan(rest, args, document, fingerprint, readme_transport=transport,
                    frontier=(frontier, frontier_path, APPROVED_QUERIES))


def compact_reconciliation(receipt):
    result = {key: value for key, value in receipt.items() if key != 'superseded'}
    superseded = receipt.get('superseded', [])
    result.update(superseded_count=len(superseded), superseded_sha256=digest(superseded))
    return result


def retain_superseded_hashes(document, reconciliation):
    """Keep per-ID version hashes once in scan evidence, not twice in a large receipt."""
    superseded = reconciliation.get('superseded', [])
    if not superseded:
        return False

    def key(entry):
        versions = sorted((row['id'], row['canonical_record_sha256'], row['checkpoint_record_sha256'])
                          for row in entry.get('superseded', []))
        return digest([entry.get('canonical_sha256'), versions])

    history = document['meta'].setdefault('checkpoint_reconciliations', [])
    decision_key = key(reconciliation)
    if any(key(entry) == decision_key for entry in history):
        return False
    history.append({**copy.deepcopy(reconciliation), 'reconciled_at': now()})
    return True


def retention_needs_refresh(artifact):
    try:
        expires = dt.datetime.fromisoformat(artifact['expires_at'].replace('Z', '+00:00'))
        return expires <= dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=48)
    except (KeyError, ValueError, TypeError):
        return True


def planned_successes(retained):
    """Plan new verified captures from the retained qualified count only."""
    if type(retained) is not int or retained < 0:
        raise ValueError('Retained successes must be a nonnegative integer')
    return min(NEW_SUCCESSES, max(0, GLOBAL_TARGET - retained))


def emit_summary(directory, receipt, *, upload):
    validate_shape(receipt, RECEIPT_V2_SCHEMA)
    validate_integrity_receipt(receipt)
    if private_json_locations(receipt):
        raise ValueError('Checkpoint receipt contains credential-like text or a personal path; values withheld')
    write_json(directory / 'summary.json', receipt)
    file_info(directory / 'summary.json', MAX_RECEIPT_BYTES)
    with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as stream:
        stream.write('checkpoint_ready=' + ('true' if upload else 'false') + '\n')
    with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as stream:
        integrity = receipt['integrity_counts']
        stream.write(f"## Scheduled README discovery\n\nNew verified README reads: **{receipt['new_qualified_successful_scans']} / "
                     f"{receipt['planned_new_successes']} planned**. Qualified total: **{integrity['qualified']}** "
                     f"of **{GLOBAL_TARGET}** goal. Raw retained captures: **{receipt['counts']['successful_readme_scans']}**; "
                     f"legacy integrity unknown: **{integrity['legacy_unknown']}**; known mismatches: **{integrity['mismatched']}**; "
                     f"failed attempts: **{receipt['counts']['failed']}**. "
                     f"Outcome: **{receipt['outcome']}**.\n\n"
                     'These are automated captures, not curated recommendations. Published data was not changed.\n')


def orchestrate(directory, *, manual_seed=None, execution_source=None, bootstrap_only=False):
    started_clock = time.monotonic()
    repository, branch = os.environ['GITHUB_REPOSITORY'], os.environ['DEFAULT_BRANCH']
    if os.environ.get('GITHUB_REF') != 'refs/heads/' + branch:
        raise ValueError('Scheduled scans run only from the default branch')
    run_id, source = int(os.environ['GITHUB_RUN_ID']), os.environ['GITHUB_SHA']
    if not re.fullmatch('[0-9a-f]{40}', source):
        raise ValueError('Invalid source revision')
    directory.mkdir(parents=True, exist_ok=True)
    receipt = {'schema_version': 2, 'run_id': run_id, 'run_attempt': int(os.environ['GITHUB_RUN_ATTEMPT']),
               'source_commit': source, 'started_at': now(), 'new_success_limit': NEW_SUCCESSES,
               'global_target_successes': GLOBAL_TARGET, 'scan_seconds': SCAN_SECONDS}
    if execution_source is not None:
        validate_execution_source(execution_source)
        receipt['execution_source'] = execution_source
    if bootstrap_only and manual_seed is None:
        raise ValueError('Bootstrap-only mode requires an explicit seed')
    canonical, canonical_sha = read_snapshot(ROOT / 'data/source-index.json')
    previous, previous_sha, frontier, artifact = None, None, None, None
    api = ActionsAPI(repository, os.environ['GH_TOKEN'], deadline=started_clock + 180)
    receipt['workflow_id'] = api.get('actions/workflows/' + WORKFLOW)['id']
    selected = select_checkpoint(api, branch, run_id, receipt['run_attempt'])
    if execution_source is not None and selected is None and manual_seed is None:
        raise ValueError('A private worker requires an explicit first seed or a trusted retained checkpoint')
    if selected:
        run, artifact = selected
        archive_path = directory / 'restored.zip'
        api.download(f"actions/artifacts/{artifact['id']}/zip", archive_path)
        restored_receipt = {}
        previous, previous_sha, frontier = unpack_checkpoint(archive_path, artifact, run, directory / 'restored',
                                                             receipt_out=restored_receipt)
        if restored_receipt.get('bootstrap_origins'):
            receipt['bootstrap_origins'] = restored_receipt['bootstrap_origins']
        receipt['restored_run_id'], receipt['restored_artifact_id'] = run['id'], artifact['id']
    if manual_seed is not None:
        if os.environ.get('GITHUB_EVENT_NAME') != 'workflow_dispatch' or execution_source is None:
            raise ValueError('Manual seed import requires an explicit private worker dispatch')
        repository_info = api.get('')
        if repository_info.get('private') is not True or repository_info.get('full_name') != repository:
            raise ValueError('Manual evidence import is restricted to the private worker repository')
        from scan_seed import import_seed
        previous, previous_sha, frontier, imported = import_seed(
            manual_seed, directory / 'manual-seed', previous, previous_sha, frontier, worker_commit=source)
        receipt['manual_seed_import'] = imported
        receipt['bootstrap_origins'] = [imported]
    try:
        seed, reconciliation = reconcile(canonical, previous, canonical_sha, previous_sha)
    except ValueError:
        write_json(directory / 'review/canonical-input.json', canonical)
        if previous is not None:
            write_json(directory / 'review/previous-input.json', previous)
        raise
    retained = len(seed['resources'])
    retained_integrity = integrity_counts(seed)
    planned = 0 if bootstrap_only else planned_successes(retained_integrity['qualified'])
    receipt.update(planned_new_successes=planned, retained_counts=counts(seed),
                   reconciliation=compact_reconciliation(reconciliation), goal_basis=GOAL_BASIS,
                   retained_integrity_counts=retained_integrity)
    was_v2 = frontier is not None
    if frontier is None:
        frontier = search_frontier.new_frontier(until=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                                               approved_queries=APPROVED_QUERIES)
    paired_ack_guard(seed, frontier)
    seed_reconciled = merge_frontier_ids(seed, frontier)
    seed_reconciled = retain_superseded_hashes(seed, reconciliation) or seed_reconciled
    # At goal, preserve a still-live paired artifact without repeatedly rewriting it.
    if (manual_seed is None and planned == 0 and was_v2 and not seed_reconciled and reconciliation['mode'] == 'checkpoint-covers-canonical'
            and not retention_needs_refresh(artifact)):
        receipt.update(completed_at=now(), outcome='global-target-already-reached', scanner_exit_code=0,
                       new_successful_scans=0, counts=counts(seed), checkpoint_sha256=previous_sha,
                       integrity_counts=retained_integrity, new_qualified_successful_scans=0,
                       target_reached=True, run_target_reached=True, global_target_reached=True,
                       files={name: file_info(directory / 'restored' / name, bound) for name, bound in
                              (('checkpoint.json', MAX_SCAN_BYTES), ('frontier.json', MAX_FRONTIER_BYTES))},
                       frontier=search_frontier.summary(frontier), transport=None)
        emit_summary(directory, receipt, upload=False)
        return 0
    if planned or bootstrap_only:
        search_frontier.add_queries(frontier, APPROVED_QUERIES, approved_queries=APPROVED_QUERIES)
        cutoff = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        if search_frontier.utc_seconds(cutoff) > frontier['until']:
            search_frontier.extend_until(frontier, cutoff)
    seed_path, output = directory / 'seed.json', directory / 'working/checkpoint.json'
    frontier_path = directory / 'working/frontier.json'
    # Persist discovery IDs even when a previous process stopped between the two saves.
    unchanged_path = ((directory / 'manual-seed/scan-seed-checkpoint.json' if manual_seed is not None
                       else directory / 'restored/checkpoint.json') if reconciliation['mode'] == 'checkpoint-covers-canonical'
                      else ROOT / 'data/source-index.json' if reconciliation['mode'] in ('canonical', 'canonical-covers-checkpoint') else None)
    if unchanged_path is not None and not seed_reconciled:
        shutil.copyfile(unchanged_path, seed_path)
    else:
        write_json(seed_path, seed)
    retained_hashes = {row['id']: digest(row) for row in seed['resources'] + seed['failures']}
    retained_known = known_ids(seed)
    receipt['retained_counts'] = counts(seed)
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(seed_path, output)
    seed_sha = file_info(seed_path, MAX_SCAN_BYTES)['sha256']
    durable = [int(key) for key, row in frontier['candidates'].items()
               if row['checkpoint_sha256'] is None and 'scan-' + key in retained_hashes]
    search_frontier.acknowledge_candidates(frontier, durable, checkpoint_sha256=seed_sha)
    search_frontier.save_frontier(frontier_path, frontier, approved_queries=APPROVED_QUERIES)
    # The child owns its own parsed state; do not retain full parent copies while it runs.
    del seed, canonical, previous, frontier, reconciliation
    if planned:
        child = subprocess.Popen([sys.executable, __file__, '--child', '--seed', str(seed_path),
                                  '--output', str(output), '--frontier', str(frontier_path)], cwd=ROOT, start_new_session=True)
        try:
            code = child.wait(timeout=max(1, SCAN_SECONDS - (time.monotonic() - started_clock)))
            outcome = 'target-reached' if code == 0 else 'partial'
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL); child.wait()
            outcome, code = 'time-budget', 124
    else:
        outcome, code = ('bootstrap-imported' if bootstrap_only else 'global-target-already-reached'), 0
    final, fingerprint = read_snapshot(output)
    frontier = read_frontier(frontier_path)
    paired_ack_guard(final, frontier)
    if merge_frontier_ids(final, frontier):
        write_json(output, final)
        fingerprint = file_info(output, MAX_SCAN_BYTES)['sha256']
    final_ids = {row['id'] for row in final['resources'] + final['failures']}
    if (not retained_known <= known_ids(final) or any(digest(row) != retained_hashes[row['id']]
            for row in final['resources'] + final['failures'] if row['id'] in retained_hashes)
            or not retained_hashes.keys() <= final_ids):
        raise ValueError('Scanner changed or lost retained evidence')
    added = len(final['resources']) - retained
    if not 0 <= added <= planned:
        raise ValueError('Scanner exceeded its remaining-success budget')
    final_integrity = integrity_counts(final)
    qualified_added = final_integrity['qualified'] - retained_integrity['qualified']
    if (qualified_added != added or any(final_integrity[key] != retained_integrity[key]
                                       for key in ('legacy_unknown', 'mismatched'))):
        raise ValueError('Scanner appended a success without explicit verified integrity')
    durable = [int(key) for key, row in frontier['candidates'].items()
               if row['checkpoint_sha256'] is None and 'scan-' + key in final_ids]
    search_frontier.acknowledge_candidates(frontier, durable, checkpoint_sha256=fingerprint)
    search_frontier.save_frontier(frontier_path, frontier, approved_queries=APPROVED_QUERIES)
    bundle = directory / 'checkpoint'
    bundle.mkdir(exist_ok=True)
    shutil.copyfile(output, bundle / 'checkpoint.json')
    shutil.copyfile(frontier_path, bundle / 'frontier.json')
    infos = {name: file_info(bundle / name, bound) for name, bound in
             (('checkpoint.json', MAX_SCAN_BYTES), ('frontier.json', MAX_FRONTIER_BYTES))}
    receipt.update(completed_at=now(), outcome=outcome, scanner_exit_code=code, new_successful_scans=added,
                   counts=counts(final), checkpoint_sha256=fingerprint, target_reached=added == planned,
                   run_target_reached=added == planned, global_target_reached=final_integrity['qualified'] >= GLOBAL_TARGET,
                   integrity_counts=final_integrity, new_qualified_successful_scans=qualified_added,
                   files=infos, frontier=search_frontier.summary(frontier),
                   transport=final['meta'].get('current_run', {}).get('readme_transport') if planned else None)
    validate_shape(receipt, RECEIPT_V2_SCHEMA)
    validate_integrity_receipt(receipt, final)
    if private_json_locations(receipt):
        raise ValueError('Checkpoint receipt contains credential-like text or a personal path; values withheld')
    write_json(bundle / 'receipt.json', receipt)  # Last file is the pair's commit marker.
    receipt_info = file_info(bundle / 'receipt.json', MAX_RECEIPT_BYTES)
    if sum(info['bytes'] for info in infos.values()) + receipt_info['bytes'] > MAX_TOTAL_BYTES:
        raise ValueError('Checkpoint pair exceeds its aggregate byte bound')
    emit_summary(directory, receipt, upload=True)
    return 0 if code == 0 else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=ROOT / '.cache/scheduled-source-scan')
    parser.add_argument('--child', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--seed', type=Path, help=argparse.SUPPRESS)
    parser.add_argument('--output', type=Path, help=argparse.SUPPRESS)
    parser.add_argument('--frontier', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        return scanner_child(args.seed, args.output, args.frontier) if args.child else orchestrate(args.directory)
    except (ValueError, KeyError, TypeError, OSError, zipfile.BadZipFile, RecursionError):
        # Never print exception values from remote JSON, signed URLs, response bodies or credentials.
        print('Scheduled scan stopped: checkpoint, provenance, privacy or API validation failed. No publication was made.', flush=True)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
