"""Keep collection scope decisions separate from the original README scan."""
from datetime import date, datetime
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SCOPE_FILE = 'data/source-scope.json'
FIELDS = {
    'decision', 'reason_code', 'reason_en', 'reason_zh',
    'readme_sha256', 'evidence_url', 'reviewed_at',
}
# A copy decision cites the one retained scan whose README bytes it shares.
DUPLICATE_README_REASON = 'duplicate-readme-copy'
SOURCE_ID_MENTION = r'(?<![A-Za-z0-9-])scan-[0-9]+(?![0-9])'


def read_scope(root=ROOT):
    """Read ID-keyed scope overrides, rejecting duplicate JSON keys."""
    path = Path(root) / SCOPE_FILE
    if not path.exists():
        return {}

    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'{SCOPE_FILE}: duplicate JSON key')
            result[key] = value
        return result

    scope = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object)
    if not isinstance(scope, dict):
        raise ValueError(f'{SCOPE_FILE}: expected an object keyed by source ID')
    return scope


def validate_scope(records, scope, errors):
    """Validate decisions against the exact recorded source snapshot."""
    if not isinstance(scope, dict):
        errors.append('Source scope must be an object keyed by source ID.')
        return
    sources = {record['id']: record for record in records}
    for identifier, entry in scope.items():
        source = sources.get(identifier)
        if source is None:
            errors.append(f'{identifier}: scope decision references an unknown source ID')
        if not isinstance(entry, dict):
            errors.append(f'{identifier}: scope decision must be an object')
            continue
        if set(entry) != FIELDS:
            errors.append(f'{identifier}: scope decision has missing or unknown fields')
        if entry.get('decision') != 'exclude':
            errors.append(f'{identifier}: unsupported scope decision')
        reason_code = entry.get('reason_code')
        if not isinstance(reason_code, str) or not re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*', reason_code):
            errors.append(f'{identifier}: invalid scope reason_code')
        for field in ('reason_en', 'reason_zh'):
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                errors.append(f'{identifier}: missing scope {field}')
        if isinstance(entry.get('reason_zh'), str) and not re.search(r'[\u4e00-\u9fff]', entry['reason_zh']):
            errors.append(f'{identifier}: scope reason_zh must contain Chinese text')
        digest = entry.get('readme_sha256')
        if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
            errors.append(f'{identifier}: invalid scope README hash')
        if source is not None:
            if source.get('scan_status') != 'readme-scanned':
                errors.append(f'{identifier}: scope decision requires a successful README scan')
            if digest != source.get('readme_sha256'):
                errors.append(f'{identifier}: scope README hash differs from the scanned snapshot')
            if entry.get('evidence_url') != source.get('readme_url'):
                errors.append(f'{identifier}: scope evidence URL differs from the scanned README URL')
        if reason_code == DUPLICATE_README_REASON:
            cited = [set(re.findall(SOURCE_ID_MENTION, entry[field])) if isinstance(entry.get(field), str) else set()
                     for field in ('reason_en', 'reason_zh')]
            related = sources.get(min(cited[0])) if len(cited[0]) == 1 else None
            if len(cited[0]) != 1 or cited[0] != cited[1] or identifier in cited[0]:
                errors.append(f'{identifier}: {DUPLICATE_README_REASON} reasons must cite the same single related source ID')
            elif (related is None or related.get('scan_status') != 'readme-scanned'
                  or related.get('readme_sha256') != digest):
                errors.append(f'{identifier}: {DUPLICATE_README_REASON} must cite a scanned source with the same README hash')
        reviewed_at = entry.get('reviewed_at')
        try:
            if not isinstance(reviewed_at, str):
                raise ValueError
            if re.fullmatch(r'\d{4}-\d{2}-\d{2}', reviewed_at):
                date.fromisoformat(reviewed_at)
            elif datetime.fromisoformat(reviewed_at.replace('Z', '+00:00')).tzinfo is None:
                raise ValueError
        except ValueError:
            errors.append(f'{identifier}: scope reviewed_at must be an ISO date or timezone-aware timestamp')


def apply_scope(records, scope):
    """Copy a complete scan and annotate exclusions without removing evidence."""
    errors = []
    validate_scope(records, scope, errors)
    if errors:
        raise ValueError('Invalid source scope: ' + '; '.join(errors))
    result = []
    for original in records:
        record = dict(original)
        entry = scope.get(record['id'])
        if entry:
            record['scope_status'] = 'excluded'
            record['scope_review'] = dict(entry)
        result.append(record)
    return result
