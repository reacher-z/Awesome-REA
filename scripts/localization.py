"""Load and validate the repository description localization layer."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

import strict_json

ROOT = Path(__file__).resolve().parents[1]
LOCALE_FILES = tuple(f'data/locales/repositories-{part}.json' for part in (1, 2, 3))
# Binds each reviewed translation to the source text and omission evidence it was written from.
FINGERPRINT_FILE = 'data/locale-source-fingerprints.json'
FINGERPRINT_POLICY = 'source-description-sha256-v1'
FINGERPRINT_FIELDS = ('description_en', 'description_omission')


def read_localizations(root=ROOT):
    translations = {}
    for filename in LOCALE_FILES:
        path = root / filename
        if not path.exists():
            continue
        def unique_object(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError(f'{filename}: duplicate JSON key')
                result[key] = value
            return result
        entries = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object)
        if not isinstance(entries, dict):
            raise ValueError(f'{filename}: expected an object keyed by resource ID')
        overlap = translations.keys() & entries.keys()
        if overlap:
            raise ValueError(f'{filename}: duplicate localization IDs')
        translations.update(entries)
    return translations


def validate_localizations(records, translations, errors):
    expected = {record['id'] for record in records}
    if set(translations) != expected:
        errors.append(f'Repository localization coverage: {len(expected - set(translations))} missing and {len(set(translations) - expected)} unknown IDs.')
    for record in records:
        identifier = record['id']
        entry = translations.get(identifier)
        if not isinstance(entry, dict):
            errors.append(f'{identifier}: localization must be an object')
            continue
        allowed = {'description_en', 'description_zh', 'english_retains_name', 'technical_only'}
        if set(entry) - allowed:
            errors.append(f'{identifier}: unknown localization fields')
        for flag in ('english_retains_name', 'technical_only'):
            if flag in entry and not isinstance(entry[flag], bool):
                errors.append(f'{identifier}: {flag} must be a boolean')
        for field in ('description_en', 'description_zh'):
            value = entry.get(field)
            if not isinstance(value, str):
                errors.append(f'{identifier}: missing localized {field}')
            elif record.get('description_en') and not value.strip():
                errors.append(f'{identifier}: empty localized {field}')
            elif not record.get('description_en') and value:
                errors.append(f'{identifier}: preserve an empty upstream description')
        english = entry.get('description_en', '')
        chinese = entry.get('description_zh', '')
        if isinstance(english, str) and re.search(r'[\u4e00-\u9fff]', english):
            # Names and explicitly quoted non-English identifiers may be retained.
            if entry.get('english_retains_name') is not True:
                errors.append(f'{identifier}: English description contains untranslated Chinese; mark a retained proper name explicitly if intentional.')
        if isinstance(chinese, str) and record.get('description_en') and not re.search(r'[\u4e00-\u9fff]', chinese):
            if entry.get('technical_only') is not True:
                errors.append(f'{identifier}: Chinese description needs translation or an explicit technical-only exception.')


def source_fingerprint(record):
    """SHA-256 of the retained source text and omission evidence; an empty description still has a fingerprint."""
    value = {'description_en': record.get('description_en') or '', 'description_omission': record.get('description_omission')}
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()


def read_fingerprints(root=ROOT):
    """Return the binding document, or None before any binding exists."""
    path = Path(root) / FINGERPRINT_FILE
    if not path.exists():
        return None
    try:
        return strict_json.loads(path.read_text(encoding='utf-8'))
    except ValueError as error:
        raise ValueError(f'{FINGERPRINT_FILE}: {error}') from error


def fingerprint_status(records, translations, document):
    """Classify translations as bound, stale, unbound or unknown; nothing is rewritten."""
    bindings = document.get('fingerprints', {}) if isinstance(document, dict) else {}
    sources = {record['id']: record for record in records}
    status = {'bound': [], 'stale': [], 'unbound': [], 'unknown': []}
    for identifier, digest in bindings.items():
        if identifier not in sources or identifier not in translations:
            status['unknown'].append(identifier)
        elif digest != source_fingerprint(sources[identifier]):
            status['stale'].append(identifier)
        else:
            status['bound'].append(identifier)
    status['unbound'] = [identifier for identifier in translations if identifier in sources and identifier not in bindings]
    return status


def validate_fingerprints(records, translations, document, errors, warnings):
    """Stale and unknown bindings are errors; translations that were never bound are only reported."""
    if document is None:
        return
    bindings = document.get('fingerprints') if isinstance(document, dict) else None
    if (not isinstance(document, dict) or set(document) != {'schema_version', 'policy', 'fields', 'fingerprints'}
            or document['schema_version'] != 1 or document['policy'] != FINGERPRINT_POLICY
            or document['fields'] != list(FINGERPRINT_FIELDS) or not isinstance(bindings, dict)
            or any(not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{64}', value) for value in bindings.values())):
        errors.append(f'{FINGERPRINT_FILE}: expected schema 1 with {FINGERPRINT_POLICY} SHA-256 fingerprints keyed by source ID.')
        return
    status = fingerprint_status(records, translations, document)
    for identifier in status['stale']:
        errors.append(f'{identifier}: translation is stale: the source description or omission evidence changed after it was bound. '
                      'Review both translations, then run python3 scripts/localization.py --bind ' + identifier + '.')
    for identifier in status['unknown']:
        errors.append(f'{identifier}: source fingerprint has no matching source record and translation; remove it.')
    if status['unbound']:
        warnings.append(f'{len(status["unbound"])} repository translations have no source fingerprint; '
                        'bind them after review with python3 scripts/localization.py --bind <id>.')


def localized_records(records, translations):
    result = []
    for original in records:
        record = dict(original)
        entry = translations.get(record['id'])
        if entry:
            record['description_original'] = record.get('description_en', '')
            record['description_en'] = entry.get('description_en', record['description_original'])
            record['description_zh'] = entry.get('description_zh', '')
            record['description_language'] = 'bilingual'
            record['description_zh_status'] = 'translated'
            record['description_localization'] = 'ai-assisted-translation'
        result.append(record)
    return result


def write_fingerprints(root, bindings):
    document = {'schema_version': 1, 'policy': FINGERPRINT_POLICY, 'fields': list(FINGERPRINT_FIELDS),
                'fingerprints': dict(sorted(bindings.items(), key=lambda item: int(item[0][5:]) if item[0][5:].isdigit() else -1))}
    path = Path(root) / FINGERPRINT_FILE
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description='Report or record source fingerprints for reviewed repository translations.')
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--bind', nargs='+', metavar='ID', help='Record the current source fingerprint for these reviewed translations')
    action.add_argument('--bind-unbound', action='store_true', help='Bind every translation that has no fingerprint yet; stale ones are left for review')
    args = parser.parse_args(argv)
    records = json.loads((Path(root) / 'data/source-index.json').read_text(encoding='utf-8'))['resources']
    translations = read_localizations(Path(root))
    document = read_fingerprints(root) or {'schema_version': 1, 'policy': FINGERPRINT_POLICY,
                                           'fields': list(FINGERPRINT_FIELDS), 'fingerprints': {}}
    status = fingerprint_status(records, translations, document)
    if args.bind or args.bind_unbound:
        selected = args.bind or status['unbound']
        sources = {record['id']: record for record in records}
        missing = [identifier for identifier in selected if identifier not in sources or identifier not in translations]
        if missing:
            print(f'Cannot bind {len(missing)} IDs without both a source record and a translation: {", ".join(missing[:5])}', file=sys.stderr)
            return 2
        # Only fingerprints change; source text and translations are never rewritten here.
        bindings = {**document['fingerprints'], **{identifier: source_fingerprint(sources[identifier]) for identifier in selected}}
        write_fingerprints(root, bindings)
        status = fingerprint_status(records, translations, {**document, 'fingerprints': bindings})
    print(json.dumps({key: len(value) for key, value in status.items()} | {'stale_ids': status['stale'], 'unknown_ids': status['unknown']},
                     ensure_ascii=False, indent=2))
    return 1 if status['stale'] or status['unknown'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
