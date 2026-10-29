"""Project the full evidence export into a compact, ordered browser payload."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

BROWSER_FILENAME = 'source-browser.json'
FULL_EXPORT_FILENAME = 'source-index.json'
SCHEMA_VERSION = 1

# Keep the complete current search/card/detail contract, plus its provenance,
# omission and integrity annotations. Discovery and resume ledgers stay in the
# unchanged full export; new fields are never included implicitly.
RECORD_FIELDS = (
    'id', 'name', 'full_name', 'url',
    'description_en', 'description_zh', 'description_original',
    'description_language', 'description_zh_status', 'description_localization',
    'description_origin', 'description_capture_policy', 'description_omission',
    'topics', 'targets', 'category', 'stars', 'license',
    'pushed_at', 'observed_at', 'metadata_observed_at',
    'readme_url', 'readme_path', 'readme_sha256', 'readme_git_sha', 'readme_bytes',
    'readme_content_git_sha', 'readme_git_sha_matches_content', 'readme_integrity_review',
    'scan_status', 'verification', 'requirements',
    'classification_origin', 'classification_reference_ids', 'scan_classification',
    'scope_status', 'related_entries',
)
REQUIRED_FIELDS = frozenset({
    'id', 'full_name', 'url', 'description_en', 'description_zh', 'description_original',
    'topics', 'targets', 'category', 'stars', 'license',
    'pushed_at', 'observed_at', 'metadata_observed_at',
    'readme_url', 'readme_sha256', 'readme_git_sha', 'readme_bytes',
    'scan_status', 'verification',
})


def read_json_bytes(content: bytes):
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON key in source browser data')
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError('Non-JSON numeric constant in source browser data')

    return json.loads(content.decode('utf-8'), object_pairs_hook=unique_object,
                      parse_constant=invalid_constant)


def compact_json_bytes(document: dict) -> bytes:
    return (json.dumps(document, ensure_ascii=False, separators=(',', ':'),
                       allow_nan=False) + '\n').encode('utf-8')


def project_source_browser(full_export: bytes) -> dict:
    """Derive the payload and bind it to the exact complete export bytes."""
    source = read_json_bytes(full_export)
    if (not isinstance(source, dict) or not isinstance(source.get('meta'), dict)
            or not isinstance(source.get('resources'), list)
            or any(not isinstance(record, dict) for record in source['resources'])):
        raise ValueError('Full source export must contain metadata and resource objects')
    meta = source['meta']
    if (meta.get('schema_version', 1) not in (1, 2)
            or type(meta.get('schema_version', 1)) is not int):
        raise ValueError('Unsupported source export version')
    published = meta.get('schema_version') == 2
    if published:
        from public_source_supplements import validate_published_document
        validate_published_document(source)
    elif (meta.get('kind') == 'published-repository-selection'
          or meta.get('status') not in ('complete', 'in-progress')
          or 'completed_at' not in meta):
        raise ValueError('Full source export is missing browser status or completion metadata')
    scanned = [record for record in source['resources'] if record.get('scan_status') == 'readme-scanned']
    visible = [record for record in scanned if record.get('scope_status') != 'excluded']
    expected_scope = {'scanned_count': len(scanned), 'excluded_count': len(scanned) - len(visible),
                      'browse_count': len(visible)}
    scope = meta.get('scope')
    if (not isinstance(scope, dict) or scope != expected_scope
            or any(type(value) is not int for value in scope.values())):
        raise ValueError('Full source export scope counts disagree with its visible records')
    records, identifiers = [], set()
    for record in visible:
        if REQUIRED_FIELDS - record.keys():
            raise ValueError('Visible source record is missing required browser fields')
        identifier = record['id']
        if not isinstance(identifier, str) or not identifier or identifier in identifiers:
            raise ValueError('Visible source records must have unique nonempty IDs')
        identifiers.add(identifier)
        records.append({field: record[field] for field in RECORD_FIELDS if field in record})
    browser_meta = {
            'schema_version': SCHEMA_VERSION, 'status': meta['status'],
            'completed_at': meta.get('completed_at'), 'scope': scope,
            'full_export': FULL_EXPORT_FILENAME,
            'full_export_sha256': hashlib.sha256(full_export).hexdigest(),
    }
    if published:
        browser_meta = {
            'schema_version': 2, 'kind': 'published-repository-selection',
            'status': 'published-selection', 'published_at': meta['published_at'],
            'scope': scope, 'full_export': 'source-published.json',
            'full_export_sha256': hashlib.sha256(full_export).hexdigest(),
        }
    return {'meta': browser_meta, 'resources': records}


def validate_source_browser(full_export: bytes, browser_export: bytes) -> dict:
    """Reject missing evidence, reordered records, excluded rows and extra data."""
    expected = project_source_browser(full_export)
    actual = read_json_bytes(browser_export)
    if actual != expected:
        raise ValueError('Browser source projection differs from the full export contract')
    if browser_export != compact_json_bytes(expected):
        raise ValueError('Browser source projection is not deterministic compact JSON')
    return actual


def write_source_browser(output: Path, full_export: bytes | None) -> dict | None:
    """Write only the projection, or remove it when the full source is unavailable."""
    destination = Path(output) / BROWSER_FILENAME
    if full_export is None:
        destination.unlink(missing_ok=True)
        return None
    document = project_source_browser(full_export)
    destination.write_bytes(compact_json_bytes(document))
    return document
