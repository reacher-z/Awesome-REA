"""Keep collection scope decisions separate from the original README scan."""
from datetime import date, datetime, timezone
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
# A gone or reassigned upstream is bound to a scripts/source_availability.py result
# instead of a README URL that no longer serves, or never served, the scanned bytes.
UNAVAILABLE_UPSTREAM_REASON = 'upstream-unavailable'
UNAVAILABLE_FIELDS = FIELDS - {'evidence_url'} | {'availability_check'}
CHECK_FIELDS = {'id', 'recorded_full_name', 'observed_at', 'outcome', 'http_status',
                'recorded_name_status', 'recorded_name_http_status'}
# Only outcomes whose ID lookup failed qualify: (ID lookup statuses, accepted recorded-name lookups).
UNAVAILABLE_OUTCOMES = {
    'not-found': ({404, 410}, {('not-found', 404), ('not-found', 410)}),
    'blocked': ({451}, {('not-found', 404), ('not-found', 410), ('inconclusive', 451)}),
    'name-reassigned': ({404, 410}, {('other-repository', 200)}),
}


def timestamp(value):
    """Parse a timezone-aware ISO timestamp, or return None."""
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00')) if isinstance(value, str) else None
    except ValueError:
        return None
    return parsed if parsed is not None and parsed.tzinfo is not None else None


def validate_availability(identifier, entry, source, reviewed, errors):
    """Accept an unavailable-upstream decision only with a recheck that found the scanned ID unresolved."""
    prefix = f'{identifier}: {UNAVAILABLE_UPSTREAM_REASON}'
    check = entry.get('availability_check')
    if not isinstance(check, dict):
        errors.append(f'{prefix} requires an availability_check recheck result')
        return
    outcome = check.get('outcome')
    if outcome not in UNAVAILABLE_OUTCOMES:
        errors.append(f'{prefix} requires a recheck outcome in which the scanned ID no longer resolves')
        return
    expected = set(CHECK_FIELDS)
    if check.get('recorded_name_status') == 'inconclusive':
        expected.add('recorded_name_reason')
    if outcome == 'name-reassigned':
        expected |= {'recorded_name_repository_id', 'recorded_name_current_full_name'}
    if set(check) != expected:
        errors.append(f'{prefix} availability_check has missing or unknown fields')
        return
    if check['id'] != identifier or (source is not None and check['recorded_full_name'] != source.get('full_name')):
        errors.append(f'{prefix} availability_check must name the scanned ID and recorded repository name')
    id_statuses, name_lookups = UNAVAILABLE_OUTCOMES[outcome]
    if type(check['http_status']) is not int or check['http_status'] not in id_statuses:
        errors.append(f'{prefix} ID lookup status does not match the {outcome} outcome')
    if (type(check['recorded_name_http_status']) is not int
            or (check['recorded_name_status'], check['recorded_name_http_status']) not in name_lookups):
        errors.append(f'{prefix} recorded-name lookup does not match the {outcome} outcome')
    mentions = [identifier[5:], f'HTTP {check["http_status"]}', str(check['recorded_full_name'])]
    if outcome == 'name-reassigned':
        other = check['recorded_name_repository_id']
        current = check['recorded_name_current_full_name']
        if not isinstance(other, str) or not re.fullmatch(r'scan-[1-9][0-9]*', other) or other == identifier:
            errors.append(f'{prefix} must record the other repository ID that now holds the recorded name')
        else:
            mentions.append(other[5:])
        if not isinstance(current, str) or current.casefold() != str(check['recorded_full_name']).casefold():
            errors.append(f'{prefix} must record the recorded name as the other repository\'s current name')
    checked = timestamp(check['observed_at'])
    scanned = timestamp(source.get('observed_at')) if source is not None else None
    if checked is None:
        errors.append(f'{prefix} recheck observed_at must be a timezone-aware timestamp')
        return
    checked_day = checked.astimezone(timezone.utc).date()
    if scanned is not None and checked <= scanned:
        errors.append(f'{prefix} recheck must follow the README scan')
    if reviewed is not None and (checked_day > reviewed if type(reviewed) is date else checked > reviewed):
        errors.append(f'{prefix} recheck must precede the review')
    mentions.append(checked_day.isoformat())
    for field in ('reason_en', 'reason_zh'):
        if isinstance(entry.get(field), str) and not all(mention in entry[field] for mention in mentions):
            errors.append(f'{prefix} {field} must state the check date, repository IDs, ID lookup status and recorded name')


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
        reason_code = entry.get('reason_code')
        unavailable = reason_code == UNAVAILABLE_UPSTREAM_REASON
        if set(entry) != (UNAVAILABLE_FIELDS if unavailable else FIELDS):
            errors.append(f'{identifier}: scope decision has missing or unknown fields')
        if entry.get('decision') != 'exclude':
            errors.append(f'{identifier}: unsupported scope decision')
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
            if not unavailable and entry.get('evidence_url') != source.get('readme_url'):
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
        reviewed_at, reviewed = entry.get('reviewed_at'), None
        try:
            if not isinstance(reviewed_at, str):
                raise ValueError
            if re.fullmatch(r'\d{4}-\d{2}-\d{2}', reviewed_at):
                reviewed = date.fromisoformat(reviewed_at)
            elif (reviewed := timestamp(reviewed_at)) is None:
                raise ValueError
        except ValueError:
            errors.append(f'{identifier}: scope reviewed_at must be an ISO date or timezone-aware timestamp')
        if unavailable:
            validate_availability(identifier, entry, source, reviewed, errors)


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


def exclusion_counts(records):
    """Split annotated exclusions into (out of scope, upstream no longer available)."""
    reasons = [(record.get('scope_review') or {}).get('reason_code') for record in records
               if record.get('scope_status') == 'excluded']
    unavailable = reasons.count(UNAVAILABLE_UPSTREAM_REASON)
    return len(reasons) - unavailable, unavailable


def unavailable_clause(count, zh, mark=''):
    """Name unavailable upstreams after the out-of-scope count; they are not out of scope."""
    if not count:
        return ''
    number = f'{mark}{count:,}{mark}'
    return f'及 {number} 个上游仓库已无法访问的条目' if zh else f' and {number} whose upstream repository is no longer available'
