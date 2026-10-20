"""Load and validate the curated Chinese resource names and requirements used by the builders."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURATED_TRANSLATIONS = 'site/translations.zh-CN.json'
TRANSLATION_FIELDS = {'name', 'requirements'}
MAX_LISTED_IDS = 10


def read_curated_translations(root=ROOT):
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'{CURATED_TRANSLATIONS}: duplicate JSON key')
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError(f'{CURATED_TRANSLATIONS}: non-JSON numeric constant')

    return json.loads((Path(root) / CURATED_TRANSLATIONS).read_text(encoding='utf-8'),
                      object_pairs_hook=unique_object, parse_constant=invalid_constant)


def nonempty_text(value):
    return isinstance(value, str) and bool(value.strip())


def listed(identifiers):
    shown = ', '.join(repr(value) for value in identifiers[:MAX_LISTED_IDS])
    return shown + (f' and {len(identifiers) - MAX_LISTED_IDS} more' if len(identifiers) > MAX_LISTED_IDS else '')


def validate_curated_translations(records, translations, errors, *, known_ids=frozenset()):
    """Pair each curated record with one entry and check the shapes the builders read.

    A name may repeat the English proper name. Requirements are one string or a list of strings,
    like the English field. The trusted PR review combines changed files from the PR head with
    unchanged files from the base branch, so it passes the base catalog IDs as `known_ids`:
    those are not reported as missing or unknown, and a branch made before a newer record still
    passes. Local validation of one checkout passes none and checks complete coverage.
    """
    if not isinstance(translations, dict):
        errors.append(f'{CURATED_TRANSLATIONS}: expected an object keyed by curated resource ID')
        return
    ids = {record['id'] for record in records if isinstance(record, dict) and isinstance(record.get('id'), str)}
    missing = sorted(ids - translations.keys() - known_ids)
    unknown = sorted(translations.keys() - ids - known_ids)
    if missing:
        errors.append(f'{CURATED_TRANSLATIONS}: no Chinese name/requirements entry for {len(missing)} '
                      f'curated resource(s): {listed(missing)}')
    if unknown:
        errors.append(f'{CURATED_TRANSLATIONS}: {len(unknown)} entry ID(s) name no curated resource: {listed(unknown)}')
    for identifier, entry in translations.items():
        where = f'{CURATED_TRANSLATIONS}: entry {identifier!r}'
        if not isinstance(entry, dict):
            errors.append(f'{where} must be an object')
            continue
        unsupported = sorted(set(entry) - TRANSLATION_FIELDS)
        if unsupported:
            errors.append(f"{where} has unsupported fields {', '.join(unsupported)}")
        if 'name' in entry and not nonempty_text(entry['name']):
            errors.append(f'{where}.name must be a nonempty string')
        requirements = entry.get('requirements')
        if not (nonempty_text(requirements) or (isinstance(requirements, list) and requirements
                                                and all(nonempty_text(item) for item in requirements))):
            errors.append(f'{where}.requirements must be a nonempty string or list of nonempty strings')
