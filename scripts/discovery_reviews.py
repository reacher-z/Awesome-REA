"""Review decisions for automated discovery records, kept apart from the immutable scan batches.

data/discovery-reviews.json maps a scan ID to the decision a reviewer reached after reading its primary
source: `exclude` (does not belong) or `hold` (may belong, but the evidence does not support a curated
record yet). A promoted repository needs no entry: its curated record, matched by exact repository URL,
takes it off the queue. A decided record leaves the unreviewed listing and stays in its batch, so the
scheduled scan and the lead collector, which treat every batch ID as already held, never queue it again.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
import re

from review_dates import review_date_is_future
from strict_json import load_path

ROOT = Path(__file__).resolve().parents[1]
FILE = 'data/discovery-reviews.json'
FIELDS = frozenset({'decision', 'reason_code', 'reason_en', 'reason_zh', 'readme_sha256', 'evidence_url', 'reviewed_at'})
OPTIONAL_FIELDS = frozenset({'duplicate_of'})
EXCLUDE_REASONS = frozenset({
    'unrelated', 'general-application', 'general-programming-tutorial', 'general-security', 'security-testing',
    'detection-only', 'forensics-only', 'development-tool', 'protection-tool', 'malware-samples', 'distribution-site',
    'community-or-event', 'cheat-or-evasion', 'game-promotion-page', 'game-mod-no-re', 'personal-profile',
    'no-real-content', 'duplicate-curated', 'duplicate-queue', 'fork-or-mirror', 'upstream-unavailable',
})
HOLD_REASONS = frozenset({'linking-policy', 'insufficient-docs', 'capability-unclear', 'target-unsupported',
                          'needs-maintainer-decision'})
REASONS = {'exclude': EXCLUDE_REASONS, 'hold': HOLD_REASONS}
DUPLICATE_REASONS = frozenset({'duplicate-curated', 'duplicate-queue'})
PINNED_EVIDENCE = re.compile(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/(?:blob|tree)/[0-9a-f]{40}(?:/\S*)?')
CHINESE = re.compile(r'[一-鿿]')
HASH = re.compile(r'[0-9a-f]{64}')


def read_reviews(root=ROOT) -> dict:
    """The ID-keyed decisions, or an empty mapping before the first review."""
    path = Path(root) / FILE
    return load_path(path) if path.is_file() else {}


def validate_reviews(batches: list[dict], reviews, errors: list[str], *, now: datetime | None = None) -> None:
    """Each decision binds to the exact scanned README of a record in a discovery batch."""
    now = datetime.now(timezone.utc) if now is None else now.astimezone(timezone.utc)
    if not isinstance(reviews, dict):
        errors.append(f'{FILE}: expected an object keyed by scan ID.')
        return
    records = {record['id']: record for batch in batches for record in batch['resources']}
    for identifier, entry in reviews.items():
        where = f'{FILE}: {identifier}'
        record = records.get(identifier)
        if record is None:
            errors.append(f'{where}: not a record in a discovery batch')
        if not isinstance(entry, dict) or not FIELDS <= set(entry) <= FIELDS | OPTIONAL_FIELDS:
            errors.append(f'{where}: missing or unknown fields')
            continue
        decision, reason = entry['decision'], entry['reason_code']
        if not isinstance(decision, str) or decision not in REASONS:
            errors.append(f'{where}: decision must be exclude or hold')
        elif not isinstance(reason, str) or reason not in REASONS[decision]:
            errors.append(f'{where}: {reason!r} is not a {decision} reason')
        for field in ('reason_en', 'reason_zh'):
            if not isinstance(entry[field], str) or not entry[field].strip():
                errors.append(f'{where}: missing {field}')
        if isinstance(entry['reason_zh'], str) and not CHINESE.search(entry['reason_zh']):
            errors.append(f'{where}: reason_zh must contain Chinese text')
        if not isinstance(entry['readme_sha256'], str) or not HASH.fullmatch(entry['readme_sha256']):
            errors.append(f'{where}: invalid README hash')
        elif record is not None and entry['readme_sha256'] != record['readme_sha256']:
            errors.append(f'{where}: README hash differs from the scanned snapshot')
        if not isinstance(entry['evidence_url'], str) or not PINNED_EVIDENCE.fullmatch(entry['evidence_url']):
            errors.append(f'{where}: evidence_url must be a GitHub link pinned to a commit')
        if (isinstance(reason, str) and reason in DUPLICATE_REASONS) != isinstance(entry.get('duplicate_of'), str):
            errors.append(f'{where}: duplicate_of goes with a duplicate reason and only then')
        try:
            reviewed = date.fromisoformat(entry['reviewed_at'])
        except (TypeError, ValueError):
            errors.append(f'{where}: reviewed_at must be an ISO date')
            continue
        if review_date_is_future(reviewed, now):
            errors.append(f'{where}: reviewed_at is in the future')
        if record is not None:
            scanned = datetime.fromisoformat(record['observed_at'].replace('Z', '+00:00')).astimezone(timezone.utc).date()
            if reviewed < scanned - timedelta(days=1):
                errors.append(f'{where}: review precedes the README scan it reviews')


def split_queue(records: list[dict], reviews: dict, curated_urls: dict[str, str]) -> tuple[list[dict], list[dict]]:
    """(still unreviewed, decided). A decided row carries `decision`, and `curated_id` when curated."""
    pending, decided = [], []
    for record in records:
        curated = curated_urls.get(record['url'].rstrip('/').casefold())
        if curated:
            decided.append({**record, 'decision': 'curated', 'curated_id': curated})
        elif record['id'] in reviews:
            decided.append({**record, 'decision': reviews[record['id']]['decision'], 'review': reviews[record['id']]})
        else:
            pending.append(record)
    return pending, decided


def export_document(decided: list[dict], generated_at: str | None) -> dict:
    """Every decision made on a discovery record, for /discoveries/reviews.json."""
    rows = []
    for record in sorted(decided, key=lambda row: int(row['id'][5:])):
        row = {'id': record['id'], 'full_name': record['full_name'], 'url': record['url'], 'batch_id': record['batch_id'],
               'decision': record['decision']}
        if record['decision'] == 'curated':
            row['curated_id'] = record['curated_id']
        else:
            review = record['review']
            row.update({key: review[key] for key in ('reason_code', 'reason_en', 'reason_zh', 'evidence_url', 'reviewed_at')})
            if review.get('duplicate_of'):
                row['duplicate_of'] = review['duplicate_of']
        rows.append(row)
    return {'version': 1, 'kind': 'discovery-review-decisions', 'generated_at': generated_at, 'counts': counts(decided), 'decisions': rows}


def counts(decided: list[dict]) -> dict:
    return {decision: sum(row['decision'] == decision for row in decided) for decision in ('curated', 'exclude', 'hold')}


def dumps(reviews: dict) -> str:
    """The file's canonical form, sorted by numeric scan ID."""
    ordered = {key: reviews[key] for key in sorted(reviews, key=lambda value: int(value[5:]))}
    return json.dumps(ordered, ensure_ascii=False, indent=2) + '\n'
