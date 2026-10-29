"""Admit public capture selections without rewriting any capture checkpoint.

Evidence is an explicitly registered public Actions archive, never an arbitrary
scan directory. Held selections are validated but do not enter published output.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from datetime import datetime, timezone
import zipfile

from localization import localized_records, validate_localizations
from review_pr import private_json_locations
from source_scope import (DUPLICATE_README_REASON, SOURCE_ID_MENTION,
                          apply_scope, read_scope, validate_scope)

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = 'reacher-z/Awesome-REA'
WORKFLOW = '.github/workflows/source-scan.yml'
PUBLISHED_FILENAME = 'source-published.json'
KIND = 'published-repository-selection'
# Admission is deliberately limited to the independently checked public run.
# Adding a different public evidence source requires a reviewed pin update.
APPROVED_SOURCE_DESCRIPTORS = frozenset({
    'f2bfb61b36496fa8c9a892c09e764c7c48d14c47cc80714581d89aa3d9929153',
})
MAX_ARCHIVE_BYTES = 16 * 1024 * 1024
MEMBER_LIMITS = {'checkpoint.json': 64 * 1024 * 1024,
                 'frontier.json': 16 * 1024 * 1024, 'receipt.json': 1024 * 1024}
STRONG_TOPICS = frozenset({
    'reverse-engineering', 'reverseengineering', 'binary-analysis', 'decompiler',
    'decompilation', 'disassembler', 'ghidra', 'frida', 'radare2', 'rizin', 'angr',
    'firmware-analysis', 'protocol-analysis', 'android-reverse-engineering',
    'apktool', 'smali', 'il2cpp',
})
COUNT_FIELDS = {'successful_readme_scans', 'failed', 'attempted_readme_scans',
                'unique_repos', 'unattempted_candidates'}
SOURCE_FIELDS = {'repository', 'workflow_path', 'run', 'artifact', 'archive_filename',
                 'files', 'snapshot_status', 'raw_counts', 'integrity_counts'}
RUN_FIELDS = {'id', 'run_attempt', 'workflow_id', 'head_sha', 'event', 'head_branch',
              'path', 'status', 'conclusion', 'head_repository'}
ARTIFACT_FIELDS = {'id', 'name', 'size_in_bytes', 'digest', 'workflow_run_id'}
BATCH_FIELDS = {'schema_version', 'batch_id', 'publication_status', 'reviewed_at',
                'baseline_sha256', 'source', 'selection', 'resources'}
SELECTION_FIELDS = {'policy', 'selected_ids', 'record_sha256', 'selected_count'}
LOCALIZED_FIELDS = frozenset({'description_en', 'description_zh', 'description_original',
                             'description_language', 'description_zh_status', 'description_localization'})
CLASSIFICATION_FIELDS = frozenset({'targets', 'category', 'classification_origin',
                                  'classification_reference_ids'})
ENRICHMENT_FIELDS = LOCALIZED_FIELDS | CLASSIFICATION_FIELDS | {
    'scan_classification', 'related_entries', 'scope_status', 'scope_review',
}


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                       allow_nan=False) + '\n').encode('utf-8')


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate key in public-source data')
            result[key] = value
        return result
    def constant(_):
        raise ValueError('Non-JSON number in public-source data')
    return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs, parse_constant=constant)


def bounded_bytes(path, limit=16 * 1024 * 1024):
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(descriptor, 'rb') as stream:
        before = os.fstat(stream.fileno())
        if before.st_size > limit:
            raise ValueError('Public-source input exceeds its byte bound')
        raw = stream.read(limit + 1)
        after = os.fstat(stream.fileno())
    if (len(raw) > limit or len(raw) != before.st_size
            or (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns)):
        raise ValueError('Public-source input changed while being read')
    return raw


def exact_keys(value, fields, label):
    if not isinstance(value, dict) or set(value) != set(fields):
        raise ValueError(f'{label}: missing or unexpected fields')


def positive(value):
    return type(value) is int and value > 0


def fingerprint(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def timestamp(value):
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (AttributeError, TypeError, ValueError):
        raise ValueError('Publication review needs a timezone-aware ISO timestamp') from None
    if parsed.tzinfo is None:
        raise ValueError('Publication review needs a timezone-aware ISO timestamp')
    return parsed


def utc_timestamp(value):
    """Canonical derived publication time; the recorded review input is retained."""
    return timestamp(value).astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def publication_timestamp(batches):
    return utc_timestamp(max((batch['reviewed_at'] for batch in batches), key=timestamp))


def owned_file(root, directory, name):
    if not isinstance(name, str) or not re.fullmatch(r'[a-z0-9][a-z0-9.-]*', name):
        raise ValueError('Unsafe public evidence filename')
    root = Path(root).resolve()
    result = root / directory / name
    current = result
    while current != root:
        if current.is_symlink():
            raise ValueError('Public-source input may not be a symlink')
        current = current.parent
    return result


def cache_output(root, value):
    """Reject lexical traversal and symlinks before any preparation work."""
    value = Path(value)
    if '..' in value.parts:
        raise ValueError('Prepared candidate destinations may not contain parent traversal')
    lexical_root = Path(root).absolute()
    canonical_root = lexical_root.resolve()
    output = value.absolute()
    try:
        relative = output.relative_to(lexical_root)
    except ValueError:
        try:
            relative = output.relative_to(canonical_root)
        except ValueError:
            raise ValueError('Prepared candidates may only be written inside ignored cache') from None
    if len(relative.parts) < 2 or relative.parts[0] != '.cache':
        raise ValueError('Prepared candidates may only be written inside ignored cache')
    # A finite component walk supports a system alias such as /var -> /private/var,
    # while refusing every symlink below the explicitly selected checkout root.
    current = canonical_root
    for component in relative.parts:
        current = current / component
        if current.is_symlink():
            raise ValueError('Prepared candidate destination may not contain symlinks')
    return current


def raw_counts(document):
    return {field: document['meta'][field] for field in sorted(COUNT_FIELDS)}


def check_counts(counts):
    exact_keys(counts, COUNT_FIELDS, 'Capture counts')
    if (any(type(n) is not int or n < 0 for n in counts.values())
            or counts['attempted_readme_scans'] != counts['successful_readme_scans'] + counts['failed']
            or counts['unique_repos'] != counts['attempted_readme_scans'] + counts['unattempted_candidates']):
        raise ValueError('Original capture count arithmetic disagrees')


def check_source(source):
    exact_keys(source, SOURCE_FIELDS, 'Public capture source')
    exact_keys(source['run'], RUN_FIELDS, 'Public run')
    exact_keys(source['artifact'], ARTIFACT_FIELDS, 'Public artifact')
    run, artifact = source['run'], source['artifact']
    if (source['repository'] != REPOSITORY or source['workflow_path'] != WORKFLOW
            or run['head_repository'] != REPOSITORY or run['path'] != WORKFLOW
            or run['head_branch'] != 'main' or run['status'] != 'completed'
            or run['event'] not in ('schedule', 'workflow_dispatch')
            or run['conclusion'] not in ('success', 'failure', 'cancelled', 'timed_out')
            or any(not positive(run[field]) for field in ('id', 'run_attempt', 'workflow_id'))
            or not isinstance(run['head_sha'], str)
            or not re.fullmatch('[0-9a-f]{40}', run['head_sha'])):
        raise ValueError('Source must identify the bounded public scan workflow')
    if (not positive(artifact['id']) or not positive(artifact['size_in_bytes'])
            or artifact['size_in_bytes'] > MAX_ARCHIVE_BYTES
            or artifact['workflow_run_id'] != run['id']
            or artifact['name'] != f'readme-scan-checkpoint-{run["run_attempt"]}'
            or not isinstance(artifact['digest'], str)
            or not re.fullmatch(r'sha256:[0-9a-f]{64}', artifact['digest'])
            or source['archive_filename'] !=
            f'run-{run["id"]}-attempt-{run["run_attempt"]}-{artifact["digest"][7:19]}.zip'):
        raise ValueError('Public artifact identity or archive binding disagrees')
    exact_keys(source['files'], MEMBER_LIMITS, 'Evidence members')
    for name, info in source['files'].items():
        exact_keys(info, {'sha256', 'bytes'}, 'Evidence member')
        if not fingerprint(info['sha256']) or not positive(info['bytes']) or info['bytes'] > MEMBER_LIMITS[name]:
            raise ValueError('Invalid public evidence member fingerprint')
    exact_keys(source['raw_counts'], COUNT_FIELDS, 'Raw capture counts')
    exact_keys(source['integrity_counts'], {'qualified', 'legacy_unknown', 'mismatched'}, 'Integrity counts')
    if any(type(n) is not int or n < 0 for n in
           [*source['raw_counts'].values(), *source['integrity_counts'].values()]):
        raise ValueError('Capture counts must be nonnegative integers')
    if source['snapshot_status'] not in ('complete', 'in-progress'):
        raise ValueError('Unknown original capture status')
    check_counts(source['raw_counts'])
    if sum(source['integrity_counts'].values()) != source['raw_counts']['successful_readme_scans']:
        raise ValueError('Original capture integrity partition disagrees')
    if private_json_locations(source):
        raise ValueError('Public source descriptor failed privacy checks')
    if digest(source) not in APPROVED_SOURCE_DESCRIPTORS:
        raise ValueError('Unapproved public evidence descriptor')


def load_evidence(root, source):
    """Recheck every member, including unselected rows and the complete frontier."""
    from scheduled_source_scan import unpack_checkpoint, integrity_counts, known_ids
    check_source(source)
    archive = owned_file(root, 'data/source-evidence', source['archive_filename'])
    raw = bounded_bytes(archive, MAX_ARCHIVE_BYTES)
    if (len(raw) != source['artifact']['size_in_bytes'] or len(raw) > MAX_ARCHIVE_BYTES
            or 'sha256:' + hashlib.sha256(raw).hexdigest() != source['artifact']['digest']):
        raise ValueError('Public evidence archive bytes differ from the approved source')
    with zipfile.ZipFile(io.BytesIO(raw)) as zipped:
        if (len(zipped.infolist()) != 3 or set(zipped.namelist()) != set(MEMBER_LIMITS)
                or any(not 0 < info.file_size <= MEMBER_LIMITS[info.filename] for info in zipped.infolist())
                or zipped.testzip() is not None):
            raise ValueError('Public evidence requires exactly three bounded JSON members with valid CRCs')
        for name, limit in MEMBER_LIMITS.items():
            member = zipped.read(name)
            if (len(member) > limit or {'bytes': len(member), 'sha256': hashlib.sha256(member).hexdigest()}
                    != source['files'][name]):
                raise ValueError('Public evidence member binding disagrees')
            if private_json_locations(strict_json(member)):
                raise ValueError('A full public evidence member failed privacy checks')
    with tempfile.TemporaryDirectory(prefix='public-source-evidence-') as directory:
        receipt = {}
        document, _, frontier = unpack_checkpoint(
            raw, source['artifact'], source['run'], Path(directory), receipt_out=receipt)
    if (raw_counts(document) != source['raw_counts']
            or integrity_counts(document) != source['integrity_counts']
            or document['meta']['status'] != source['snapshot_status']
            or {'scan-' + identifier for identifier in frontier['candidates']} - known_ids(document)):
        raise ValueError('Full source counts, capture status or frontier identity ledger disagree')
    return document


def validate_batch(batch, baseline, baseline_sha, evidence):
    exact_keys(batch, BATCH_FIELDS, 'Public source supplement')
    if (batch['schema_version'] != 1 or type(batch['schema_version']) is not int
            or not isinstance(batch['batch_id'], str)
            or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', batch['batch_id'])
            or batch['publication_status'] not in ('held-for-localization', 'held-for-review', 'ready')
            or batch['baseline_sha256'] != baseline_sha):
        raise ValueError('Invalid supplement version, state, ID or canonical binding')
    if batch['publication_status'] == 'ready':
        timestamp(batch['reviewed_at'])
    elif batch['reviewed_at'] is not None:
        timestamp(batch['reviewed_at'])
    selection = batch['selection']
    exact_keys(selection, SELECTION_FIELDS, 'Public source selection')
    records = batch['resources']
    if (selection['policy'] != 'strong-reverse-engineering-topics-v1'
            or not isinstance(records, list) or not records
            or type(selection['selected_count']) is not int
            or selection['selected_count'] != len(records)
            or not isinstance(selection['selected_ids'], list)
            or not isinstance(selection['record_sha256'], dict)):
        raise ValueError('Invalid public selection policy or counts')
    originals = {row['id']: row for row in evidence['resources']}
    existing = {row['id']: row for row in baseline['resources']}
    if any(originals.get(identifier) != row for identifier, row in existing.items()):
        raise ValueError('Public evidence does not preserve the canonical baseline objects')
    original_failures = {row['id']: row for row in evidence['failures']}
    if any(original_failures.get(row['id']) != row for row in baseline['failures']):
        raise ValueError('Public evidence does not preserve the canonical baseline failures')
    attempted = set(existing) | {row['id'] for row in baseline['failures']}
    identifiers, names = [], {row['full_name'].casefold(): row['id'] for row in baseline['resources'] + baseline['failures']}
    for record in records:
        identifier = record.get('id') if isinstance(record, dict) else None
        if (not isinstance(identifier, str) or not re.fullmatch(r'scan-[1-9][0-9]*', identifier)
                or identifier in identifiers or identifier in attempted
                or originals.get(identifier) != record):
            raise ValueError('Selection must contain distinct new exact source capture objects')
        if (record.get('readme_git_sha_matches_content') is not True
                or record.get('readme_git_sha') != record.get('readme_content_git_sha')
                or not STRONG_TOPICS.intersection(record.get('topics', []))):
            raise ValueError('Selected capture must be qualified and meet the explicit topic screen')
        if (batch['publication_status'] == 'ready'
                and timestamp(batch['reviewed_at']) < timestamp(record['observed_at'])):
            raise ValueError('Publication review must follow the selected capture')
        name = record['full_name'].casefold()
        if name in names and names[name] != identifier:
            raise ValueError('Ambiguous repository name and numeric identity')
        names[name] = identifier
        identifiers.append(identifier)
    if (selection['selected_ids'] != identifiers
            or selection['record_sha256'] != {row['id']: digest(row) for row in records}):
        raise ValueError('Selected IDs or exact record fingerprints disagree')
    if private_json_locations(batch):
        raise ValueError('Public source supplement failed privacy checks')


def apply_supplement_scope(records, scope, baseline_context):
    """Allow new-ID decisions to cite visible canonical evidence, never edit it."""
    new_ids = {row['id'] for row in records}
    baseline_ids = {row['id'] for row in baseline_context}
    if (not isinstance(scope, dict) or set(scope) - new_ids
            or len(new_ids) != len(records) or new_ids & baseline_ids):
        raise ValueError('Supplement scope may classify only its distinct new IDs')
    context = [*baseline_context, *records]
    errors = []
    validate_scope(context, scope, errors)
    if errors:
        raise ValueError('Supplement scope failed source-context validation: ' + '; '.join(errors[:3]))
    by_id = {row['id']: row for row in context}
    for identifier, entry in scope.items():
        if entry['reason_code'] == DUPLICATE_README_REASON:
            cited = next(iter(set(re.findall(SOURCE_ID_MENTION, entry['reason_en']))))
            if cited in scope or by_id[cited].get('scope_status') == 'excluded':
                raise ValueError('A duplicate README reference must remain visible in its source context')
            if (by_id[identifier]['full_name'].rsplit('/', 1)[-1].casefold()
                    != by_id[cited]['full_name'].rsplit('/', 1)[-1].casefold()):
                raise ValueError('A duplicate README decision must retain the same repository name')
    return apply_scope(context, scope)[len(baseline_context):]


def project_additions(supplements):
    return apply_supplement_scope(
        localized_records(supplements['records'], supplements['locales']),
        supplements['scope'], supplements['baseline_context'])


def load_supplements(root=ROOT):
    root = Path(root)
    registry = root / 'data/source-supplements/index.json'
    empty = {'ready': [], 'held': [], 'records': [], 'locales': {}, 'scope': {}, 'evidence': [],
             'baseline_sha256': None, 'baseline_capture': None, 'baseline_context': []}
    if not registry.exists():
        return empty
    index = strict_json(bounded_bytes(owned_file(root, 'data/source-supplements', 'index.json')))
    exact_keys(index, {'schema_version', 'batches'}, 'Supplement registry')
    if (type(index['schema_version']) is not int or index['schema_version'] != 1
            or not isinstance(index['batches'], list)
            or any(not isinstance(name, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name)
                   for name in index['batches'])
            or len(set(index['batches'])) != len(index['batches'])):
        raise ValueError('Invalid ordered supplement registry')
    baseline_bytes = bounded_bytes(owned_file(root, 'data', 'source-index.json'))
    baseline = strict_json(baseline_bytes)
    from scheduled_source_scan import validate_snapshot
    validate_snapshot(baseline)
    if baseline['meta']['status'] != 'complete':
        raise ValueError('The canonical publication baseline must remain complete')
    baseline_sha = hashlib.sha256(baseline_bytes).hexdigest()
    result = empty
    result['baseline_sha256'] = baseline_sha
    result['baseline_capture'] = {'counts': raw_counts(baseline), 'status': baseline['meta']['status'],
                                  'completed_at': baseline['meta'].get('completed_at')}
    result['baseline_context'] = apply_scope(baseline['resources'], read_scope(root))
    seen = {row['id'] for row in baseline['resources'] + baseline['failures']}
    names = {row['full_name'].casefold(): row['id'] for row in baseline['resources'] + baseline['failures']}
    evidence_cache = {}
    for name in index['batches']:
        batch = strict_json(bounded_bytes(owned_file(root, 'data/source-supplements', name + '.json')))
        if batch.get('batch_id') != name:
            raise ValueError('Supplement filename and ID disagree')
        check_source(batch['source'])
        key = digest(batch['source'])
        if key not in evidence_cache:
            evidence_cache[key] = load_evidence(root, batch['source'])
        validate_batch(batch, baseline, baseline_sha, evidence_cache[key])
        for row in batch['resources']:
            if row['id'] in seen or (row['full_name'].casefold() in names
                                    and names[row['full_name'].casefold()] != row['id']):
                raise ValueError('Duplicate or ambiguous identity across publication batches')
            seen.add(row['id'])
            names[row['full_name'].casefold()] = row['id']
        locale_path = owned_file(root, 'data/locales/source-supplements', name + '.json')
        locales = strict_json(bounded_bytes(locale_path)) if locale_path.exists() else {}
        if not isinstance(locales, dict) or set(locales) - set(batch['selection']['selected_ids']):
            raise ValueError('Unexpected supplement localization IDs')
        partial_records = [row for row in batch['resources'] if row['id'] in locales]
        errors = []
        validate_localizations(partial_records, locales, errors)
        scope_path = owned_file(root, 'data/source-supplements', name + '.scope.json')
        scope = strict_json(bounded_bytes(scope_path)) if scope_path.exists() else {}
        if private_json_locations(locales) or private_json_locations(scope):
            raise ValueError('Supplement locales or scope failed privacy checks')
        apply_supplement_scope(batch['resources'], scope, result['baseline_context'])
        if errors:
            raise ValueError('Supplement locale/scope validation failed: ' + '; '.join(errors[:3]))
        missing = set(batch['selection']['selected_ids']) - set(locales)
        if batch['publication_status'] != 'ready':
            result['held'].append({'batch_id': name, 'selected_count': len(batch['resources']),
                                   'missing_localizations': len(missing)})
            continue
        if missing:
            raise ValueError('Ready supplement is missing complete bilingual coverage')
        result['ready'].append(batch)
        result['records'].extend(batch['resources'])
        result['locales'].update(locales)
        result['scope'].update(scope)
    result['evidence'] = list({digest(b['source']): b['source'] for b in result['ready']}.values())
    return result


def prepare_batch(root, batch_id, source, identifiers):
    """Prepare a held exact selection; this performs no capture or publication."""
    if (not isinstance(identifiers, list) or not identifiers
            or any(not isinstance(identifier, str) for identifier in identifiers)):
        raise ValueError('Selection input must be a nonempty ordered ID array')
    baseline_bytes = bounded_bytes(owned_file(root, 'data', 'source-index.json'))
    baseline = strict_json(baseline_bytes)
    from scheduled_source_scan import validate_snapshot
    validate_snapshot(baseline)
    if baseline['meta']['status'] != 'complete':
        raise ValueError('The canonical publication baseline must remain complete')
    evidence = load_evidence(root, source)
    rows = {row['id']: row for row in evidence['resources']}
    if any(identifier not in rows for identifier in identifiers):
        raise ValueError('Selected ID is not a successful record in the public evidence')
    records = [rows[identifier] for identifier in identifiers]
    batch = {
        'schema_version': 1, 'batch_id': batch_id,
        'publication_status': 'held-for-localization', 'reviewed_at': None,
        'baseline_sha256': hashlib.sha256(baseline_bytes).hexdigest(), 'source': source,
        'selection': {'policy': 'strong-reverse-engineering-topics-v1',
                      'selected_ids': identifiers, 'selected_count': len(records),
                      'record_sha256': {row['id']: digest(row) for row in records}},
        'resources': records,
    }
    validate_batch(batch, baseline, batch['baseline_sha256'], evidence)
    return batch


def source_descriptor(source):
    """Only the public allowlisted proof is published, never local verifier paths."""
    return {**source, 'run_url': f'https://github.com/{REPOSITORY}/actions/runs/{source["run"]["id"]}',
            'archive_url': '/evidence/source-scans/' + source['archive_filename']}


def compose_published(canonical_export, canonical_input_sha, supplements, rendered_additions):
    if not supplements['ready']:
        return None
    baseline = strict_json(canonical_export)
    capture = {'counts': raw_counts(baseline), 'status': baseline['meta']['status'],
               'completed_at': baseline['meta'].get('completed_at')}
    if canonical_input_sha != supplements['baseline_sha256'] or capture != supplements['baseline_capture']:
        raise ValueError('Canonical export capture facts differ from the preserved source input')
    if [row['id'] for row in rendered_additions] != [row['id'] for row in supplements['records']]:
        raise ValueError('Rendered supplement order or identity changed')
    localized = project_additions(supplements)
    for original, expected, rendered in zip(supplements['records'], localized, rendered_additions):
        if set(rendered) - set(original) - ENRICHMENT_FIELDS:
            raise ValueError('Rendered capture contains an unapproved enrichment field')
        for field, value in original.items():
            if field not in LOCALIZED_FIELDS | CLASSIFICATION_FIELDS:
                if field not in rendered or rendered[field] != value:
                    raise ValueError('Rendered capture changed an original evidence or metadata field')
        for field in LOCALIZED_FIELDS | {'scope_status', 'scope_review'}:
            if (field in expected) != (field in rendered) or rendered.get(field) != expected.get(field):
                raise ValueError('Rendered capture differs from its admitted locale or scope projection')
        changed_labels = any(rendered.get(field) != original.get(field) for field in CLASSIFICATION_FIELDS)
        if changed_labels:
            if (rendered.get('scan_classification') !=
                    {field: original[field] for field in CLASSIFICATION_FIELDS if field in original}
                    or rendered.get('classification_origin') != 'curated-build-cross-reference'
                    or not isinstance(rendered.get('classification_reference_ids'), list)
                    or not rendered['classification_reference_ids']
                    or any(not isinstance(value, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]*', value)
                           for value in rendered['classification_reference_ids'])
                    or not isinstance(rendered.get('targets'), list)
                    or any(not isinstance(value, str) for value in rendered['targets'])
                    or rendered['targets'] != sorted(set(rendered['targets']))
                    or not set(original.get('targets', [])).issubset(rendered['targets'])):
                raise ValueError('Curated enrichment must preserve the complete recorded classification')
        elif 'scan_classification' in rendered and rendered.get('scan_classification') != original.get('scan_classification'):
            raise ValueError('Unexpected recorded-classification replacement')
    records = baseline['resources'] + rendered_additions
    if len({row['id'] for row in records}) != len(records):
        raise ValueError('Published selection has duplicate IDs')
    excluded = sum(row.get('scope_status') == 'excluded' for row in records)
    document = {
        'meta': {
            'schema_version': 2, 'kind': KIND, 'status': 'published-selection',
            'published_at': publication_timestamp(supplements['ready']),
            'scope': {'scanned_count': len(records), 'excluded_count': excluded, 'browse_count': len(records) - excluded},
            'canonical_export': 'source-index.json',
            'canonical_export_sha256': hashlib.sha256(canonical_export).hexdigest(),
            'canonical_input_sha256': canonical_input_sha,
            'canonical_capture': capture,
            'capture_sources': [source_descriptor(source) for source in supplements['evidence']],
            'selections': [{'batch_id': b['batch_id'], 'selected_count': len(b['resources']),
                            'checkpoint_sha256': b['source']['files']['checkpoint.json']['sha256'],
                            'selection_sha256': digest(b['selection'])} for b in supplements['ready']],
        },
        'resources': records,
    }
    validate_published_document(document)
    return document


def validate_published_document(document):
    """Validate publication semantics; capture counters remain per-source facts."""
    exact_keys(document, {'meta', 'resources'}, 'Published selection')
    meta = document['meta']
    exact_keys(meta, {'schema_version', 'kind', 'status', 'published_at', 'scope',
                     'canonical_export', 'canonical_export_sha256', 'canonical_input_sha256',
                     'canonical_capture', 'capture_sources', 'selections'}, 'Published metadata')
    if (type(meta['schema_version']) is not int or meta['schema_version'] != 2
            or meta['kind'] != KIND or meta['status'] != 'published-selection'
            or meta['canonical_export'] != 'source-index.json'
            or not fingerprint(meta['canonical_export_sha256'])
            or not fingerprint(meta['canonical_input_sha256'])):
        raise ValueError('Invalid published selection identity or baseline export binding')
    if meta['published_at'] != utc_timestamp(meta['published_at']):
        raise ValueError('Derived publication time must use canonical UTC Z form')
    exact_keys(meta['canonical_capture'], {'counts', 'status', 'completed_at'}, 'Canonical capture')
    check_counts(meta['canonical_capture']['counts'])
    if meta['canonical_capture']['status'] != 'complete':
        raise ValueError('The canonical baseline capture must remain complete')
    timestamp(meta['canonical_capture']['completed_at'])
    if (not isinstance(meta['capture_sources'], list) or not meta['capture_sources']
            or not isinstance(meta['selections'], list) or not meta['selections']
            or not isinstance(document['resources'], list)):
        raise ValueError('Published selection needs source proofs, selections and records')
    sources = set()
    for entry in meta['capture_sources']:
        exact_keys(entry, SOURCE_FIELDS | {'run_url', 'archive_url'}, 'Published source')
        original = {key: entry[key] for key in SOURCE_FIELDS}
        check_source(original)
        if source_descriptor(original) != entry:
            raise ValueError('Published source URLs differ from the closed public routes')
        key = entry['files']['checkpoint.json']['sha256']
        if key in sources:
            raise ValueError('Repeated capture source counts must not be added')
        sources.add(key)
    batches, selected = set(), 0
    used_sources = set()
    for entry in meta['selections']:
        exact_keys(entry, {'batch_id', 'selected_count', 'checkpoint_sha256', 'selection_sha256'}, 'Published batch')
        if (not isinstance(entry['batch_id'], str)
                or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', entry['batch_id'])
                or entry['batch_id'] in batches or not positive(entry['selected_count'])
                or entry['checkpoint_sha256'] not in sources or not fingerprint(entry['selection_sha256'])):
            raise ValueError('Invalid published batch identity or source binding')
        batches.add(entry['batch_id'])
        used_sources.add(entry['checkpoint_sha256'])
        selected += entry['selected_count']
    if used_sources != sources:
        raise ValueError('Unreferenced source proof in published selection')
    baseline_count = meta['canonical_capture']['counts']['successful_readme_scans']
    records = document['resources']
    if len(records) != baseline_count + selected:
        raise ValueError('Publication counts must equal baseline plus disjoint selections')
    identifiers, names = set(), set()
    for offset, row in enumerate(records):
        if (not isinstance(row, dict) or not isinstance(row.get('id'), str)
                or not re.fullmatch(r'scan-[1-9][0-9]*', row['id'])
                or row['id'] in identifiers or not isinstance(row.get('full_name'), str)
                or not re.fullmatch(r'[A-Za-z0-9-]+/[A-Za-z0-9_.-]+', row['full_name'])
                or row['full_name'].casefold() in names or row.get('scan_status') != 'readme-scanned'):
            raise ValueError('Invalid or duplicated published repository identity')
        identifiers.add(row['id'])
        names.add(row['full_name'].casefold())
        if offset >= baseline_count and (row.get('readme_git_sha_matches_content') is not True
                                        or row.get('readme_git_sha') != row.get('readme_content_git_sha')):
            raise ValueError('Newly published captures must retain explicit matching Git hashes')
    excluded = sum(row.get('scope_status') == 'excluded' for row in records)
    expected = {'scanned_count': len(records), 'excluded_count': excluded,
                'browse_count': len(records) - excluded}
    if (meta['scope'] != expected or not isinstance(meta['scope'], dict)
            or any(type(value) is not int for value in meta['scope'].values())):
        raise ValueError('Published selection scope counts disagree')
    if private_json_locations(document):
        raise ValueError('Published selection failed privacy checks')
    return document


def copy_public_evidence(root, output, supplements):
    """Copy only each explicitly admitted archive; never walk an artifact folder."""
    for source in supplements['evidence']:
        original = owned_file(root, 'data/source-evidence', source['archive_filename'])
        raw = bounded_bytes(original, MAX_ARCHIVE_BYTES)
        if 'sha256:' + hashlib.sha256(raw).hexdigest() != source['artifact']['digest']:
            raise ValueError('Evidence changed after admission')
        destination = Path(output) / 'evidence/source-scans' / source['archive_filename']
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--prepare-batch', help='Prepare a held batch in ignored cache; never register it automatically')
    parser.add_argument('--source-batch', help='Existing registered batch whose approved public evidence will be reused')
    parser.add_argument('--ids', type=Path, help='Ordered JSON array of reviewed candidate IDs')
    parser.add_argument('--output', type=Path, help='New JSON file inside this checkout’s .cache directory')
    args = parser.parse_args()
    prepare = (args.prepare_batch, args.source_batch, args.ids, args.output)
    if any(value is not None for value in prepare) and not all(value is not None for value in prepare):
        parser.error('Preparing a batch requires --prepare-batch, --source-batch, --ids and --output')
    if args.prepare_batch:
        output = cache_output(args.root, args.output)
        source_batch = strict_json(bounded_bytes(owned_file(
            args.root, 'data/source-supplements', args.source_batch + '.json')))
        batch = prepare_batch(args.root, args.prepare_batch, source_batch['source'],
                              strict_json(bounded_bytes(args.ids)))
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('xb') as stream:
            stream.write(json_bytes(batch))
        print(json.dumps({'prepared_records': len(batch['resources']),
                          'publication_status': batch['publication_status'], 'network_requests': 0}))
        return
    result = load_supplements(args.root)
    print(json.dumps({'ready_batches': len(result['ready']), 'ready_records': len(result['records']),
                      'held_batches': result['held'], 'network_requests': 0}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile):
        print('Public supplement validation failed; no capture or publication was performed.', file=sys.stderr)
        raise SystemExit(1)
