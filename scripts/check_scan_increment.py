#!/usr/bin/env python3
"""Compare a proposed source-index increment with its frozen baseline, offline.

Source mode checks that every retained success, failure and observation is
unchanged, that any resume or reconciliation entry naming the baseline's SHA-256
agrees with it, and that the new IDs, counts and discovery ledger add up.
Publication mode also requires a finished run, translations for every record
with existing locale memberships and values unchanged, and scope decisions
bound to the scanned README hashes. Nothing is fetched or rewritten.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

from localization import LOCALE_FILES, validate_localizations
from source_descriptions import capture_description
from source_scope import SCOPE_FILE, validate_scope
from validate import parse_iso


ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = 'data/source-index.json'
SCAN_ID = r'scan-[0-9]+'
OBSERVATION_FIELDS = ('queries', 'seed_observations', 'resume_observations', 'resume_history', 'checkpoint_reconciliations')
COUNT_FIELDS = ('successful_readme_scans', 'failed', 'attempted_readme_scans', 'unique_repos', 'unattempted_candidates')
INTEGRITY_REVIEW_FIELDS = {'reviewed_at', 'method', 'advertised_blob_sha256', 'advertised_blob_bytes'}
INTEGRITY_REVIEW_METHOD = 'readme-json-and-raw-match-captured-sha256'
POLICY = ('Offline comparison of a candidate snapshot with the frozen baseline it extends. Retained success, failure, observation '
          'and run-history objects must be unchanged, except for a description omission that reproduces bounded-upstream-v1 '
          'from the retained text or a README integrity review added to a record whose advertised Git blob did not match. '
          'Counts are recomputed from the recorded entries; no batch size is assumed and nothing is rewritten.')


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()


def snapshot(raw, label):
    """Parse a snapshot without trusting its counters; structural problems are fatal."""
    document = json.loads(raw)
    if (not isinstance(document, dict) or not isinstance(document.get('meta'), dict)
            or not isinstance(document.get('resources'), list) or not isinstance(document.get('failures', []), list)):
        raise ValueError(f'{label} must contain meta, resources and failures')
    document.setdefault('failures', [])
    for status, entries in (('readme-scanned', document['resources']), ('failed', document['failures'])):
        for entry in entries:
            if (not isinstance(entry, dict) or entry.get('scan_status') != status
                    or not isinstance(entry.get('id'), str) or not re.fullmatch(SCAN_ID, entry['id'])):
                raise ValueError(f'{label} contains an entry without a valid scan status and repository ID')
    return document


def accounting_errors(document, label):
    """Recompute counters and ledger arithmetic from the recorded entries."""
    meta, records, failures = document['meta'], document['resources'], document['failures']
    attempted = [entry['id'] for entry in records + failures]
    errors = []
    if len(set(attempted)) != len(attempted):
        errors.append(f'{label}: a repository ID has more than one recorded README attempt.')
    for field, actual in (('successful_readme_scans', len(records)), ('failed', len(failures)),
                          ('attempted_readme_scans', len(attempted))):
        if meta.get(field) != actual:
            errors.append(f'{label}: meta.{field} is {meta.get(field)!r}, but {actual} entries are recorded.')
    ledger = meta.get('discovered_repository_ids')
    if ledger is None:
        return errors
    if not isinstance(ledger, list) or any(not isinstance(value, str) or not re.fullmatch(SCAN_ID, value) for value in ledger):
        return errors + [f'{label}: discovered_repository_ids must be an array of scan IDs.']
    known = set(ledger)
    if len(known) != len(ledger):
        errors.append(f'{label}: the discovery ledger repeats an ID.')
    if not set(attempted) <= known:
        errors.append(f'{label}: {len(set(attempted) - known)} attempted IDs are missing from the discovery ledger.')
    if meta.get('unique_repos') != len(known):
        errors.append(f'{label}: meta.unique_repos is {meta.get("unique_repos")!r}, but the ledger has {len(known)} IDs.')
    if meta.get('unattempted_candidates') != len(known - set(attempted)):
        errors.append(f'{label}: meta.unattempted_candidates is {meta.get("unattempted_candidates")!r}, '
                      f'but {len(known - set(attempted))} ledger IDs have no README attempt.')
    run = meta.get('current_run')
    if isinstance(run, dict):
        for retained, added, total in (('retained_successful_readme_scans', 'new_successful_readme_scans', len(records)),
                                       ('retained_failed_readme_scans', 'new_failed_readme_scans', len(failures))):
            values = run.get(retained), run.get(added)
            if any(value is not None for value in values) and (
                    any(type(value) is not int for value in values) or sum(values) != total):
                errors.append(f'{label}: current_run {retained} plus {added} does not equal {total} recorded entries.')
    return errors


def integrity_review_error(review, old):
    """A review may only explain a retained mismatch with complete, ordered evidence."""
    if old.get('readme_git_sha_matches_content') is not False:
        return 'a README integrity review needs a retained Git blob mismatch'
    if (not isinstance(review, dict) or set(review) != INTEGRITY_REVIEW_FIELDS
            or review.get('method') != INTEGRITY_REVIEW_METHOD
            or not re.fullmatch(r'[0-9a-f]{64}', str(review.get('advertised_blob_sha256', '')))
            or review['advertised_blob_sha256'] == old.get('readme_sha256')
            or type(review.get('advertised_blob_bytes')) is not int or review['advertised_blob_bytes'] <= 0):
        return 'the README integrity review does not follow its fixed evidence format'
    try:
        if parse_iso(review['reviewed_at'], require_time=True) < parse_iso(old.get('observed_at'), require_time=True):
            return 'the README integrity review predates the retained capture'
    except (TypeError, ValueError):
        return 'the README integrity review needs timezone-aware timestamps'
    return None


def annotation(old, new):
    """Return the annotation kinds that deterministically turn the retained record into the candidate copy."""
    expected, kinds = dict(old), []
    if 'description_omission' in new and 'description_omission' not in old:
        try:
            capture = capture_description(old.get('description_en'))
        except ValueError:
            return None, 'the retained description is not text'
        if 'description_omission' not in capture:
            return None, 'the retained description is within the bounded-upstream-v1 limit'
        expected.update(capture)
        kinds.append('description-omission')
    if 'readme_integrity_review' in new and 'readme_integrity_review' not in old:
        problem = integrity_review_error(new['readme_integrity_review'], old)
        if problem:
            return None, problem
        expected['readme_integrity_review'] = new['readme_integrity_review']
        kinds.append('readme-integrity-review')
    if not kinds or expected != new:
        return None, 'other fields changed'
    return kinds, None


def missing_items(old, new):
    """Count retained observations absent from the candidate, as a multiset so order may differ after a union."""
    remaining = Counter(fingerprint(item) for item in new)
    missing = 0
    for item in old:
        digest = fingerprint(item)
        if remaining[digest]:
            remaining[digest] -= 1
        else:
            missing += 1
    return missing


def baseline_binding(baseline, candidate, baseline_sha256):
    """Find where the candidate names the baseline bytes and confirm the counts it recorded for them."""
    base_meta, meta = baseline['meta'], candidate['meta']
    counts = {field: base_meta.get(field) for field in COUNT_FIELDS}
    for index, history in enumerate(meta.get('resume_history') or []):
        if isinstance(history, dict) and history.get('source_sha256') == baseline_sha256:
            recorded = {field: history.get(field) for field in COUNT_FIELDS}
            if recorded != counts or history.get('run') != base_meta.get('current_run'):
                return f'resume_history[{index}]', 'resume history for the baseline disagrees with its counts or run'
            return f'resume_history[{index}]', None
    for index, receipt in enumerate(meta.get('checkpoint_reconciliations') or []):
        if isinstance(receipt, dict) and receipt.get('canonical_sha256') == baseline_sha256:
            recorded = receipt.get('canonical_counts') or {}
            if ({field: recorded.get(field) for field in COUNT_FIELDS} != counts
                    or receipt.get('canonical_current_run') != base_meta.get('current_run')):
                return f'checkpoint_reconciliations[{index}]', 'reconciliation for the baseline disagrees with its counts or run'
            return f'checkpoint_reconciliations[{index}]', None
    return None, None


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key')
        result[key] = value
    return result


def read_shards(read):
    """Read locale shards as {filename: {id: entry}}, rejecting duplicate keys."""
    shards = {}
    for filename in LOCALE_FILES:
        text = read(filename)
        entries = {} if text is None else json.loads(text, object_pairs_hook=unique_object)
        if not isinstance(entries, dict):
            raise ValueError(f'{filename}: expected an object keyed by resource ID')
        shards[filename] = entries
    return shards


def check_increment(baseline, candidate, baseline_sha256, *, candidate_sha256=None, publication=False,
                    base_shards=None, shards=None, scope=None):
    """Return a report whose errors list is empty when the candidate only extends the baseline."""
    errors = accounting_errors(candidate, 'candidate')
    base_meta, meta = baseline['meta'], candidate['meta']
    old = {entry['id']: entry for entry in baseline['resources'] + baseline['failures']}
    new = {entry['id']: entry for entry in candidate['resources'] + candidate['failures']}
    annotations = []
    for identifier, entry in old.items():
        current = new.get(identifier)
        if current is None:
            errors.append(f'{identifier}: retained README attempt is missing from the candidate.')
        elif current['scan_status'] != entry['scan_status']:
            errors.append(f'{identifier}: retained {entry["scan_status"]} attempt became {current["scan_status"]}.')
        elif current != entry:
            kinds, problem = annotation(entry, current) if entry['scan_status'] == 'readme-scanned' else (None, 'other fields changed')
            if kinds is None:
                errors.append(f'{identifier}: retained {entry["scan_status"]} object changed ({problem}).')
            else:
                annotations.append({'id': identifier, 'kinds': kinds})
    for field in OBSERVATION_FIELDS:
        retained, current = base_meta.get(field) or [], meta.get(field) or []
        if not isinstance(retained, list) or not isinstance(current, list):
            errors.append(f'meta.{field} must be an array in both snapshots.')
        elif missing := missing_items(retained, current):
            errors.append(f'meta.{field}: {missing} retained entries are missing or changed.')
    binding, problem = (('identical-bytes', None) if candidate_sha256 == baseline_sha256
                        else baseline_binding(baseline, candidate, baseline_sha256))
    warnings = []
    if problem:
        errors.append(f'Baseline binding: {problem}.')
    elif binding is None:
        # A scheduled seed can be rewritten before resuming, so content preservation above remains the gate.
        warnings.append('The candidate does not name the baseline SHA-256 as a resume or reconciliation input; '
                        'retained content was compared directly.')
    base_known = set(base_meta.get('discovered_repository_ids') or []) | set(old)
    known = set(meta.get('discovered_repository_ids') or [])
    if 'discovered_repository_ids' not in meta:
        errors.append('The candidate must persist discovered_repository_ids.')
    elif lost := base_known - known:
        errors.append(f'Discovery ledger: {len(lost)} baseline IDs are missing from the candidate.')
    new_successes = [entry['id'] for entry in candidate['resources'] if entry['id'] not in old]
    new_failures = [entry['id'] for entry in candidate['failures'] if entry['id'] not in old]
    attempted = set(new)
    if publication:
        if meta.get('status') != 'complete' or not meta.get('completed_at'):
            errors.append('Publication requires a complete scan; the candidate is an in-progress checkpoint.')
        translations = {}
        for entries in shards.values():
            if translations.keys() & entries.keys():
                errors.append('A localization ID appears in more than one locale shard.')
            translations.update(entries)
        validate_localizations(candidate['resources'], translations, errors)
        for filename, entries in base_shards.items():
            for identifier, entry in entries.items():
                if shards[filename].get(identifier) != entry:
                    errors.append(f'{identifier}: existing translation in {filename} was moved or changed.')
        validate_scope(candidate['resources'], scope, errors)
    return {
        'policy': POLICY, 'mode': 'publication' if publication else 'source',
        'baseline_sha256': baseline_sha256, 'candidate_sha256': candidate_sha256, 'baseline_binding': binding,
        'retained': {'successful': len(baseline['resources']), 'failed': len(baseline['failures']),
                     'annotated': len(annotations)},
        'new': {'successful': len(new_successes), 'failed': len(new_failures),
                'discovered_ids': len(known - base_known)},
        'candidate': {'status': meta.get('status'), 'successful': len(candidate['resources']),
                      'failed': len(candidate['failures']), 'known_ids': len(known),
                      'unattempted_ids': len(known - attempted)},
        'annotations': annotations, 'warnings': warnings, 'errors': errors,
    }


def git_reader(ref):
    """Read committed files from the local object store; a missing path reads as None."""
    def read(path):
        result = subprocess.run(['git', 'show', f'{ref}:{path}'], cwd=ROOT, capture_output=True, check=False)
        return result.stdout if result.returncode == 0 else None
    return read


def directory_reader(directory):
    def read(path):
        file = Path(directory) / Path(path).name
        return file.read_bytes() if file.exists() else None
    return read


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    base = parser.add_mutually_exclusive_group(required=True)
    base.add_argument('--baseline-ref', help='Git revision whose data/source-index.json and locale shards form the baseline, such as origin/main')
    base.add_argument('--baseline', type=Path, help='Baseline snapshot file')
    parser.add_argument('--baseline-locales', type=Path, help='Directory holding the baseline repositories-N.json shards (with --baseline)')
    parser.add_argument('--candidate', type=Path, default=ROOT / SOURCE_FILE, help='Candidate snapshot; defaults to the working tree index')
    parser.add_argument('--candidate-locales', type=Path, default=ROOT / 'data/locales', help='Directory holding the candidate locale shards')
    parser.add_argument('--scope', type=Path, default=ROOT / SCOPE_FILE, help='Candidate scope decisions')
    parser.add_argument('--publication', action='store_true', help='Also require a complete run, full translations and hash-bound scope decisions')
    args = parser.parse_args(argv)
    if args.baseline_ref is not None and (not args.baseline_ref or args.baseline_ref.startswith('-')):
        parser.error('baseline ref must be a revision name')
    if args.publication and args.baseline is not None and args.baseline_locales is None:
        parser.error('publication mode with --baseline also needs --baseline-locales')
    read_base = git_reader(args.baseline_ref) if args.baseline_ref else directory_reader(args.baseline_locales or '.')
    try:
        raw = read_base(SOURCE_FILE) if args.baseline_ref else args.baseline.read_bytes()
        if raw is None:
            raise ValueError('baseline source index is missing at that revision')
        baseline = snapshot(raw, 'baseline')
        if problems := accounting_errors(baseline, 'baseline'):
            raise ValueError(problems[0])
        candidate_raw = args.candidate.read_bytes()
        candidate = snapshot(candidate_raw, 'candidate')
        base_shards = shards = scope = None
        if args.publication:
            base_shards = read_shards(read_base)
            shards = read_shards(directory_reader(args.candidate_locales))
            scope = json.loads(args.scope.read_text(encoding='utf-8'), object_pairs_hook=unique_object) if args.scope.exists() else {}
    except (OSError, ValueError) as error:
        print(f'Snapshots could not be compared: {error}', file=sys.stderr)
        return 2
    report = check_increment(baseline, candidate, hashlib.sha256(raw).hexdigest(),
                             candidate_sha256=hashlib.sha256(candidate_raw).hexdigest(), publication=args.publication,
                             base_shards=base_shards, shards=shards, scope=scope)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
