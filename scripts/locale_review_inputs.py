#!/usr/bin/env python3
"""Emit translation review inputs for the repository IDs a finished scan adds, offline.

Reads a complete candidate source index and the baseline it extends, finds every candidate
record without a baseline translation, and assigns each one once to a locale shard. The shard
with the fewest entries goes first, ties go to the lowest shard number, and IDs are taken in
numeric order. It writes one reviewer input per shard and a manifest binding the inputs,
baseline and candidate by SHA-256. Canonical locale files are never written; existing shard
memberships and values stay as they are.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

from localization import LOCALE_FILES

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = 'data/source-index.json'
POLICY = ('Review inputs only: each new ID is assigned once to the locale shard with the fewest entries, ties to the lowest '
          'shard number, in numeric repository-ID order. Empty and omitted source descriptions need empty strings in both '
          'languages. Translations are written by reviewers into the canonical shard named here; this helper never writes them.')


def digest(content):
    return hashlib.sha256(content).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key')
        result[key] = value
    return result


def parse(raw, label):
    try:
        return json.loads(raw, object_pairs_hook=unique_object)
    except (UnicodeDecodeError, ValueError):
        raise ValueError(f'{label} is not valid JSON without duplicate keys') from None


def numeric(identifier):
    return int(identifier[5:])


def plan(candidate, baseline, shards):
    """Return {shard filename: [record, ...]} for the new IDs, or raise ValueError when the inputs disagree."""
    meta = candidate.get('meta') if isinstance(candidate, dict) else None
    if not isinstance(meta, dict) or meta.get('status') != 'complete' or not isinstance(candidate.get('resources'), list):
        raise ValueError('The candidate must be a complete scan, not an in-progress checkpoint')
    records = candidate['resources']
    ids = [record.get('id') if isinstance(record, dict) else None for record in records]
    if any(not isinstance(value, str) or not re.fullmatch(r'scan-[0-9]+', value) for value in ids) or len(set(ids)) != len(ids):
        raise ValueError('Candidate records need unique scan IDs')
    base_ids = {record['id'] for record in baseline.get('resources', [])}
    translated = {}
    for filename, entries in shards.items():
        if not isinstance(entries, dict):
            raise ValueError(f'{filename}: expected an object keyed by source ID')
        for identifier in entries:
            if identifier in translated:
                raise ValueError(f'{identifier} appears in more than one baseline locale shard')
            translated[identifier] = filename
    if set(translated) != base_ids:
        raise ValueError('Baseline locale shards must cover exactly the baseline source IDs')
    if not base_ids <= set(ids):
        raise ValueError('The candidate is missing baseline records; this helper only adds IDs')
    sizes = {filename: len(entries) for filename, entries in shards.items()}
    assigned = {filename: [] for filename in LOCALE_FILES}
    for record in sorted((record for record in records if record['id'] not in translated), key=lambda record: numeric(record['id'])):
        target = min(LOCALE_FILES, key=lambda filename: (sizes[filename], LOCALE_FILES.index(filename)))
        assigned[target].append(record)
        sizes[target] += 1
    return assigned


def review_entry(record):
    """Only source evidence for the reviewer; no draft or placeholder translation is produced."""
    entry = {'id': record['id'], 'full_name': record.get('full_name'), 'url': record.get('url'),
             'source_description': record.get('description_en') or ''}
    if record.get('description_omission'):
        entry['description_omission'] = record['description_omission']
    # Empty and omitted descriptions keep both strings empty so the interface shows its own fallback.
    entry['translation_required'] = bool(entry['source_description'])
    return entry


def write_inputs(output, assigned, *, candidate_sha256, baseline_sha256, shard_sha256):
    output.mkdir(parents=True, exist_ok=True)
    inputs, assignments = {}, {}
    for number, filename in enumerate(LOCALE_FILES, 1):
        name = f'review-repositories-{number}.json'
        document = {'shard': filename, 'entries': [review_entry(record) for record in assigned[filename]]}
        content = (json.dumps(document, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        (output / name).write_bytes(content)
        inputs[name] = digest(content)
        assignments[filename] = [record['id'] for record in assigned[filename]]
    manifest = {
        'policy': POLICY, 'candidate_sha256': candidate_sha256, 'baseline_sha256': baseline_sha256,
        'baseline_locale_sha256': shard_sha256, 'new_ids': sum(len(values) for values in assignments.values()),
        'translation_required': sum(entry['translation_required'] for records in assigned.values()
                                    for entry in map(review_entry, records)),
        'assignments': assignments, 'inputs': inputs,
    }
    (output / 'assignment-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return manifest


def git_reader(ref):
    def read(path):
        result = subprocess.run(['git', 'show', f'{ref}:{path}'], cwd=ROOT, capture_output=True, check=False)
        return result.stdout if result.returncode == 0 else None
    return read


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    base = parser.add_mutually_exclusive_group(required=True)
    base.add_argument('--baseline-ref', help='Git revision whose source index and locale shards are the baseline, such as origin/main')
    base.add_argument('--baseline', type=Path, help='Baseline source index file (with --baseline-locales)')
    parser.add_argument('--baseline-locales', type=Path, help='Directory holding the baseline repositories-N.json shards')
    parser.add_argument('--candidate', type=Path, required=True, help='Complete candidate source index')
    parser.add_argument('--output', type=Path, help='Directory for review inputs outside data/; defaults to .cache/locale-review/<candidate hash>')
    args = parser.parse_args(argv)
    if args.baseline_ref is not None and (not args.baseline_ref or args.baseline_ref.startswith('-')):
        parser.error('baseline ref must be a revision name')
    if args.baseline is not None and args.baseline_locales is None:
        parser.error('--baseline also needs --baseline-locales')
    read = (git_reader(args.baseline_ref) if args.baseline_ref else
            lambda path: (args.baseline_locales / Path(path).name).read_bytes() if (args.baseline_locales / Path(path).name).exists() else None)
    try:
        candidate_raw = args.candidate.read_bytes()
        baseline_raw = read(SOURCE_FILE) if args.baseline_ref else args.baseline.read_bytes()
        if baseline_raw is None:
            raise ValueError('The baseline source index is missing')
        shard_raw = {filename: read(filename) for filename in LOCALE_FILES}
        if any(value is None for value in shard_raw.values()):
            raise ValueError('A baseline locale shard is missing')
        assigned = plan(parse(candidate_raw, 'candidate'), parse(baseline_raw, 'baseline'),
                        {filename: parse(raw, filename) for filename, raw in shard_raw.items()})
        output = (args.output or ROOT / '.cache/locale-review' / digest(candidate_raw)[:12]).resolve()
        if output == (ROOT / 'data').resolve() or (ROOT / 'data').resolve() in output.parents:
            raise ValueError('Review inputs are not canonical data; choose an output directory outside data/')
        manifest = write_inputs(output, assigned, candidate_sha256=digest(candidate_raw), baseline_sha256=digest(baseline_raw),
                                shard_sha256={filename: digest(raw) for filename, raw in shard_raw.items()})
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f'Review inputs were not written: {error}', file=sys.stderr)
        return 2
    shown = output.relative_to(ROOT) if ROOT in output.parents else output
    print(json.dumps({'output': str(shown), 'new_ids': manifest['new_ids'],
                      'translation_required': manifest['translation_required'],
                      'per_shard': {filename: len(ids) for filename, ids in manifest['assignments'].items()}}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
