#!/usr/bin/env python3
"""Persistent bounded search partitions; discovery identities are never README successes.

Integration contract
--------------------
state = new_frontier(approved_queries=QUERY_BASES, until='2026-10-18T00:00:00Z')
request = next_request(state)  # pure; None means no currently runnable partition
result = api.json(request['path'], search=True)  # existing scanner rate limiter
record_response(state, request, result, known_ids=durable_attempted_repository_ids)
save_frontier(cache_path, state)  # commit page cursor AND pending identities together
batch = pending_candidates(state, limit=100)
# Fetch/hash READMEs, durably save the actual scanner checkpoint, then:
acknowledge_candidates(state, ids, checkpoint_sha256=durable_checkpoint_sha256)
save_frontier(cache_path, state)
# Retry/ineligible candidates stay pending, with bounded backoff and fair rotation:
defer_candidates(state, unresolved_ids, reason='retry', retry_after_seconds=60)
# Use reason='ineligible', retry_after_seconds=86400 for eligibility rechecks.

Only the caller performs network requests and chooses a bounded per-run request/time
budget. On rate limits it calls record_failure with a retry time, saves, and stops.
On restart, load_frontier preserves page cursors and pending candidates. A request
whose response was never saved may be fetched again; its IDs are deduplicated.

add_queries accepts only explicitly approved scope bases. extend_until adds new
created-time intervals without reopening older traversals. Search results mutate;
'complete' means the observed page traversal finished, never an exhaustive census.
An overflow or incomplete response splits into narrower disjoint UTC intervals.
A saturated one-second interval is blocked visibly, not silently truncated.

Primary API behavior: https://docs.github.com/en/rest/search/search#about-search
Timestamp qualifiers: https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories
"""
from __future__ import annotations

import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlencode

from scan_sources import QUERY_BASES
from review_pr import parse_json

ROOT = Path(__file__).resolve().parents[1]
MAX_STATE_BYTES = 256 * 1024 * 1024
MAX_CANDIDATES = 200_000
MAX_PARTITIONS = 50_000
MAX_OBSERVATIONS = 50_000
MAX_ROOTS = 128
GATES = 'is:public fork:false archived:false'
DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
STATUSES = {'pending', 'complete', 'split', 'blocked'}
DEFER_REASONS = {'ineligible', 'retry', 'deferred', 'not-found', 'rate-limited', 'network-failure', 'readme-unavailable'}


def utc_seconds(value):
    if not isinstance(value, str):
        raise ValueError('Expected a UTC timestamp')
    parsed = dt.datetime.strptime(value, DATE_FORMAT).replace(tzinfo=dt.timezone.utc)
    if parsed.strftime(DATE_FORMAT) != value:
        raise ValueError('UTC timestamp must use exact second precision')
    return int(parsed.timestamp())


def checked_run_id(value):
    """Preserve the scanner's UTC run identity, including subsecond precision."""
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z', value):
        raise ValueError('Expected a UTC scanner run identity')
    dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    return value


def timestamp(value):
    return dt.datetime.fromtimestamp(value, dt.timezone.utc).strftime(DATE_FORMAT)


def current_seconds():
    return int(dt.datetime.now(dt.timezone.utc).timestamp())


def checked_base(base):
    if (not isinstance(base, str) or not base.strip() or base != base.strip() or len(base) > 160
            or any(ord(char) < 32 for char in base)
            or re.search(r'(?i)(?:^|\s)(?:created|pushed|is|fork|archived):|\b(?:OR|NOT)\b', base)):
        raise ValueError('Scope bases must not override generated range or eligibility qualifiers')
    return base


def partition_id(root, low, high):
    return hashlib.sha256(f'{root}:{low}:{high}'.encode()).hexdigest()[:24]


def partition(root, low, high, sequence=0):
    return {'id': partition_id(root, low, high), 'root': root, 'low': low, 'high': high,
            'page': 1, 'revision': 0, 'status': 'pending', 'count': None, 'seen_ids': [],
            'not_before': 0, 'last_sequence': sequence, 'failures': 0, 'reason': None}


def new_frontier(*, until, since='1970-01-01T00:00:00Z', approved_queries=None):
    roots = list(QUERY_BASES if approved_queries is None else approved_queries)
    low, high = utc_seconds(since), utc_seconds(until)
    if low < 0 or high < low or high > current_seconds() or not 0 < len(roots) <= MAX_ROOTS or len(set(roots)) != len(roots):
        raise ValueError('Invalid initial scope, UTC interval or root count')
    for base in roots:
        checked_base(base)
    return {'schema_version': 1, 'roots': roots, 'since': low, 'until': high, 'request_count': 0,
            'partitions': [partition(i, low, high) for i in range(len(roots))],
            'candidates': {}, 'observations': []}


def request_for(state, item):
    query = state['roots'][item['root']] + ' ' + GATES + ' created:' + timestamp(item['low']) + '..' + timestamp(item['high'])
    return {'partition_id': item['id'], 'revision': item['revision'], 'query': query,
            'page': item['page'], 'per_page': 100, 'path': '/search/repositories?' + urlencode({
                'q': query, 'per_page': 100, 'page': item['page'], 'sort': 'stars', 'order': 'desc'})}


def next_request(state, *, now=None):
    """Return one request without reserving it or resetting completed cursors."""
    instant = current_seconds() if now is None else now
    available = [p for p in state['partitions'] if p['status'] == 'pending' and p['not_before'] <= instant]
    if not available or len(state['observations']) >= MAX_OBSERVATIONS:
        return None
    item = min(available, key=lambda p: (p['last_sequence'], p['root'], p['low']))
    return request_for(state, item)


def active_partition(state, request):
    item = next((p for p in state['partitions'] if p['id'] == request.get('partition_id')), None)
    if item is None or item['status'] != 'pending' or request != request_for(state, item):
        raise ValueError('Stale or altered search request; no cursor was changed')
    if len(state['observations']) >= MAX_OBSERVATIONS:
        raise ValueError('Observation budget reached; preserve this frontier for review')
    return item


def public_identity(repo, item):
    if not isinstance(repo, dict) or any(repo.get(key) is not False for key in ('private', 'fork', 'archived')):
        return None
    if repo.get('visibility', 'public') != 'public':
        return None
    identifier, name, node = repo.get('id'), repo.get('full_name'), repo.get('node_id')
    if (type(identifier) is not int or not 0 < identifier < 2 ** 63
            or not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9-]+/[A-Za-z0-9_.-]+', name)
            or len(name) > 200 or repo.get('html_url') != 'https://github.com/' + name
            or node is not None and (not isinstance(node, str) or not re.fullmatch(r'[A-Za-z0-9_=-]{1,128}', node))):
        return None
    try:
        created = utc_seconds(repo.get('created_at'))
    except (ValueError, TypeError):
        return None
    if not item['low'] <= created <= item['high']:
        return None
    return {'id': identifier, 'full_name': name, 'node_id': node, 'created_at': timestamp(created)}


def split_or_block(state, item, reason):
    if item['low'] == item['high'] or len(state['partitions']) + 2 > MAX_PARTITIONS:
        item.update(status='blocked', reason='one-second-' + reason if item['low'] == item['high'] else 'partition-budget')
        return
    midpoint = (item['low'] + item['high']) // 2
    children = [partition(item['root'], item['low'], midpoint, state['request_count']),
                partition(item['root'], midpoint + 1, item['high'], state['request_count'])]
    item.update(status='split', reason=reason)
    state['partitions'].extend(children)


def record_response(state, request, response, *, known_ids=(), observed_at=None, run_id=None):
    """Commit discovery metadata to in-memory state; save before consuming its queue."""
    item = active_partition(state, request)
    if (not isinstance(response, dict) or type(response.get('total_count')) is not int or response['total_count'] < 0
            or type(response.get('incomplete_results')) is not bool or not isinstance(response.get('items'), list)
            or len(response['items']) > 100):
        raise ValueError('Invalid search response envelope; no cursor was changed')
    moment = current_seconds() if observed_at is None else utc_seconds(observed_at)
    recorded_run = timestamp(moment) if run_id is None else checked_run_id(run_id)
    known = set(known_ids)
    if any(type(value) is not int or value <= 0 for value in known):
        raise ValueError('Durable known IDs must be positive integers')
    accepted, rejected, ids = [], 0, set()
    for repo in response['items']:
        identity = public_identity(repo, item)
        if identity is None or identity['id'] in ids:
            rejected += 1
            continue
        accepted.append(identity); ids.add(identity['id'])
    additions = {str(r['id']) for r in accepted if r['id'] not in known} - state['candidates'].keys()
    if len(state['candidates']) + len(additions) > MAX_CANDIDATES:
        raise ValueError('Candidate budget reached; no page or candidate was discarded')
    sequence = state['request_count'] + 1
    for identity in accepted:
        identifier = str(identity['id'])
        if identity['id'] in known:
            continue
        candidate = state['candidates'].get(identifier)
        if candidate is None:
            state['candidates'][identifier] = {**identity, 'first_partition': item['id'], 'roots': [item['root']],
                                               'matched_partitions': [item['id']],
                                               'observed_at': timestamp(moment), 'checkpoint_sha256': None,
                                               'next_attempt_at': 0, 'last_attempt_at': 0, 'attempts': 0, 'defer_reason': None}
        elif item['root'] not in candidate['roots']:
            candidate['roots'].append(item['root'])
            candidate['matched_partitions'].append(item['id'])
    state['request_count'] = sequence
    observed = {'sequence': sequence, 'partition_id': item['id'], 'page': item['page'], 'observed_at': timestamp(moment), 'run_id': recorded_run,
                'status': 'ok', 'total_count': response['total_count'], 'incomplete_results': response['incomplete_results'],
                'returned': len(response['items']), 'accepted_ids': sorted(ids), 'rejected_items': rejected}
    state['observations'].append(observed)
    seen = set(item['seen_ids']) | ids
    changed_count = item['count'] is not None and item['count'] != response['total_count']
    item.update(revision=item['revision'] + 1, last_sequence=sequence, not_before=0, seen_ids=sorted(seen))
    if response['total_count'] > 1000:
        split_or_block(state, item, 'result-cap')
    elif response['incomplete_results'] or rejected or changed_count:
        split_or_block(state, item, 'incomplete-response' if response['incomplete_results'] else 'unstable-response')
    else:
        item['count'] = response['total_count']
        expected = max(0, min(100, response['total_count'] - (item['page'] - 1) * 100))
        if len(response['items']) != expected:
            split_or_block(state, item, 'page-count-mismatch')
        elif item['page'] * 100 >= response['total_count']:
            if len(seen) == response['total_count']:
                item.update(status='complete', reason=None)
            else:
                split_or_block(state, item, 'page-identity-mismatch')
        else:
            item['page'] += 1
    return {'new_candidates': len(additions), 'accepted_public_identities': len(ids),
            'rejected_items': rejected, 'partition_status': item['status']}


def record_failure(state, request, *, reason, retry_after_seconds=60, observed_at=None, run_id=None):
    """Keep the same page; retry timing belongs to the caller's actual API outcome."""
    item = active_partition(state, request)
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,60}', reason) or type(retry_after_seconds) is not int or not 1 <= retry_after_seconds <= 86400:
        raise ValueError('Failure must use a bounded outcome code and backoff')
    instant = current_seconds() if observed_at is None else utc_seconds(observed_at)
    recorded_run = timestamp(instant) if run_id is None else checked_run_id(run_id)
    state['request_count'] += 1
    state['observations'].append({'sequence': state['request_count'], 'partition_id': item['id'], 'page': item['page'],
                                  'observed_at': timestamp(instant), 'run_id': recorded_run, 'status': 'failed', 'reason': reason,
                                  'retry_after_seconds': retry_after_seconds})
    item.update(revision=item['revision'] + 1, last_sequence=state['request_count'], failures=item['failures'] + 1,
                not_before=instant + retry_after_seconds, reason=reason)


def pending_candidates(state, *, limit=100, offset=0, now=None):
    """Page the eligible queue; keep state and ``now`` fixed across a traversal."""
    if type(limit) is not int or not 1 <= limit <= 1000:
        raise ValueError('Candidate batch limit must be 1..1000')
    if type(offset) is not int or offset < 0:
        raise ValueError('Candidate offset must be a nonnegative integer')
    partitions = {item['id']: item for item in state['partitions']}
    instant = current_seconds() if now is None else now
    result = []
    for value in sorted(state['candidates'].values(), key=lambda item: (item['last_attempt_at'], item['id'])):
        if value['checkpoint_sha256'] is not None or value['next_attempt_at'] > instant:
            continue
        if offset:
            offset -= 1
            continue
        result.append({**copy.deepcopy(value), 'metadata_observed_at': value['observed_at'],
                       '_matched_queries': [request_for(state, partitions[identifier])['query']
                                            for identifier in value['matched_partitions']]})
        if len(result) == limit:
            break
    return result


def defer_candidates(state, identifiers, *, reason, retry_after_seconds, observed_at=None):
    """Rotate unresolved identities without pretending a README was captured."""
    if reason not in DEFER_REASONS or type(retry_after_seconds) is not int or not 60 <= retry_after_seconds <= 604800:
        raise ValueError('Candidate deferral needs a known reason and 60-second to 7-day backoff')
    instant = current_seconds() if observed_at is None else utc_seconds(observed_at)
    identifiers = list(dict.fromkeys(identifiers))
    if any(type(identifier) is not int or str(identifier) not in state['candidates'] for identifier in identifiers):
        raise ValueError('Cannot defer undiscovered identities')
    for identifier in identifiers:
        candidate = state['candidates'][str(identifier)]
        if candidate['checkpoint_sha256'] is None:
            candidate.update(last_attempt_at=instant, next_attempt_at=instant + retry_after_seconds,
                             attempts=candidate['attempts'] + 1, defer_reason=reason)


def acknowledge_candidates(state, identifiers, *, checkpoint_sha256):
    """Call only after those IDs are durably present in the caller's scan checkpoint."""
    if not isinstance(checkpoint_sha256, str) or not re.fullmatch('[0-9a-f]{64}', checkpoint_sha256):
        raise ValueError('A durable checkpoint fingerprint is required')
    identifiers = list(identifiers)
    if any(type(identifier) is not int or str(identifier) not in state['candidates'] for identifier in identifiers):
        raise ValueError('Cannot acknowledge undiscovered identities')
    for identifier in identifiers:
        state['candidates'][str(identifier)]['checkpoint_sha256'] = checkpoint_sha256


def add_queries(state, bases, *, approved_queries):
    approved = set(approved_queries)
    additions = list(dict.fromkeys(bases))
    if any(checked_base(base) not in approved for base in additions):
        raise ValueError('New queries require explicit scope approval')
    additions = [base for base in additions if base not in state['roots']]
    if len(state['roots']) + len(additions) > MAX_ROOTS or len(state['partitions']) + len(additions) > MAX_PARTITIONS:
        raise ValueError('Query or partition budget exceeded')
    for base in additions:
        root = len(state['roots']); state['roots'].append(base)
        state['partitions'].append(partition(root, state['since'], state['until'], state['request_count']))


def extend_until(state, until):
    high = utc_seconds(until)
    if high <= state['until'] or high > current_seconds() or len(state['partitions']) + len(state['roots']) > MAX_PARTITIONS:
        raise ValueError('Extension must add a bounded new UTC interval')
    for root in range(len(state['roots'])):
        state['partitions'].append(partition(root, state['until'] + 1, high, state['request_count']))
    state['until'] = high


def query_observations(state, *, start=0, run_id=None):
    """Adapt newly saved page observations to the existing scanner's query ledger.

    By default original run IDs survive. The caller may pass its actual run
    timestamp for a fresh observation slice only. Do not restamp older events
    into a new current_run slice when reconciling missing historical provenance.
    """
    if run_id is not None:
        checked_run_id(run_id)
    if type(start) is not int or not 0 <= start <= len(state['observations']):
        raise ValueError('Invalid query observation offset')
    partitions = {item['id']: item for item in state['partitions']}
    result = []
    for event in state['observations'][start:]:
        item = partitions[event['partition_id']]
        row = {'query': request_for(state, item)['query'], 'page': event['page'], 'per_page': 100,
               'run_id': event['run_id'] if run_id is None else run_id, 'observed_at': event['observed_at'], 'status': event['status']}
        if event['status'] == 'ok':
            row.update({key: event[key] for key in ('total_count', 'incomplete_results', 'returned')})
            row['rejected_items'] = event['rejected_items']
        else:
            row['reason'] = event['reason']
            if re.fullmatch(r'http-[1-5][0-9]{2}', event['reason']):
                row['http_status'] = int(event['reason'][5:])
        result.append(row)
    return result


def validate_frontier(state, *, approved_queries):
    if not isinstance(state, dict) or set(state) != {'schema_version', 'roots', 'since', 'until', 'request_count', 'partitions', 'candidates', 'observations'} or state['schema_version'] != 1:
        raise ValueError('Unexpected discovery frontier schema')
    roots = state['roots']
    if not isinstance(roots, list) or not 0 < len(roots) <= MAX_ROOTS or len(set(roots)) != len(roots) or any(checked_base(base) not in approved_queries for base in roots):
        raise ValueError('Frontier scope is not approved')
    if any(type(state[key]) is not int for key in ('since', 'until', 'request_count')) or not 0 <= state['since'] <= state['until'] <= current_seconds():
        raise ValueError('Invalid frontier timestamps or request count')
    if not isinstance(state['partitions'], list) or not len(roots) <= len(state['partitions']) <= MAX_PARTITIONS:
        raise ValueError('Invalid partition population')
    ids = set()
    fields = set(partition(0, 0, 0))
    for item in state['partitions']:
        if not isinstance(item, dict) or set(item) != fields or any(type(item[key]) is not int for key in ('root', 'low', 'high', 'page', 'revision', 'not_before', 'last_sequence', 'failures')):
            raise ValueError('Invalid partition structure')
        if (not 0 <= item['root'] < len(roots) or not state['since'] <= item['low'] <= item['high'] <= state['until']
                or item['id'] != partition_id(item['root'], item['low'], item['high']) or item['id'] in ids
                or item['status'] not in STATUSES or not 1 <= item['page'] <= 10
                or min(item['revision'], item['not_before'], item['last_sequence'], item['failures']) < 0
                or item['last_sequence'] > state['request_count'] or item['count'] is not None and (type(item['count']) is not int or item['count'] < 0)
                or not isinstance(item['seen_ids'], list) or len(item['seen_ids']) > 1000
                or any(type(value) is not int or value <= 0 for value in item['seen_ids']) or len(set(item['seen_ids'])) != len(item['seen_ids'])
                or item['reason'] is not None and (not isinstance(item['reason'], str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,80}', item['reason']))):
            raise ValueError('Invalid partition cursor or identities')
        ids.add(item['id'])
    candidates = state['candidates']
    if not isinstance(candidates, dict) or len(candidates) > MAX_CANDIDATES:
        raise ValueError('Candidate population exceeds bounds')
    for key, value in candidates.items():
        fields = {'id', 'full_name', 'node_id', 'created_at', 'first_partition', 'roots', 'matched_partitions', 'observed_at', 'checkpoint_sha256',
                  'next_attempt_at', 'last_attempt_at', 'attempts', 'defer_reason'}
        if not isinstance(value, dict) or set(value) != fields or key != str(value['id']) or value['first_partition'] not in ids:
            raise ValueError('Invalid candidate identity or provenance')
        probe = {**value, 'private': False, 'fork': False, 'archived': False, 'html_url': 'https://github.com/' + str(value['full_name'])}
        if public_identity(probe, {'low': state['since'], 'high': state['until']}) is None:
            raise ValueError('Invalid stored public identity')
        if (not isinstance(value['roots'], list) or not value['roots'] or len(set(value['roots'])) != len(value['roots'])
                or any(type(root) is not int or not 0 <= root < len(roots) for root in value['roots'])
                or not isinstance(value['matched_partitions'], list) or len(value['matched_partitions']) != len(value['roots'])
                or any(identifier not in ids for identifier in value['matched_partitions'])
                or value['checkpoint_sha256'] is not None and not re.fullmatch('[0-9a-f]{64}', str(value['checkpoint_sha256']))):
            raise ValueError('Invalid candidate delivery or query provenance')
        utc_seconds(value['observed_at'])
        if (any(type(value[key]) is not int or value[key] < 0 for key in ('next_attempt_at', 'last_attempt_at', 'attempts'))
                or value['next_attempt_at'] < value['last_attempt_at']
                or value['defer_reason'] is not None and value['defer_reason'] not in DEFER_REASONS):
            raise ValueError('Invalid candidate retry state')
    if not isinstance(state['observations'], list) or len(state['observations']) > MAX_OBSERVATIONS or state['request_count'] != len(state['observations']):
        raise ValueError('Observation counts do not match requests')
    for sequence, event in enumerate(state['observations'], 1):
        if not isinstance(event, dict):
            raise ValueError('Invalid request observation')
        common = {'sequence', 'partition_id', 'page', 'observed_at', 'run_id', 'status'}
        extra = {'reason', 'retry_after_seconds'} if event.get('status') == 'failed' else {'total_count', 'incomplete_results', 'returned', 'accepted_ids', 'rejected_items'}
        if set(event) != common | extra or event['sequence'] != sequence or event['partition_id'] not in ids or type(event['page']) is not int or not 1 <= event['page'] <= 10 or event['status'] not in ('ok', 'failed'):
            raise ValueError('Invalid request observation')
        utc_seconds(event['observed_at'])
        checked_run_id(event['run_id'])
        if event['status'] == 'failed':
            if not re.fullmatch(r'[a-z][a-z0-9-]{0,60}', str(event['reason'])) or type(event['retry_after_seconds']) is not int or not 1 <= event['retry_after_seconds'] <= 86400:
                raise ValueError('Invalid failure observation')
        elif (type(event['total_count']) is not int or event['total_count'] < 0 or type(event['incomplete_results']) is not bool
              or type(event['returned']) is not int or not 0 <= event['returned'] <= 100 or type(event['rejected_items']) is not int
              or not 0 <= event['rejected_items'] <= event['returned'] or not isinstance(event['accepted_ids'], list)
              or len(event['accepted_ids']) != event['returned'] - event['rejected_items']
              or any(type(value) is not int or value <= 0 for value in event['accepted_ids']) or len(set(event['accepted_ids'])) != len(event['accepted_ids'])):
            raise ValueError('Invalid public result observation')
    by_partition = {identifier: [] for identifier in ids}
    observed_by_partition = {}
    items = {item['id']: item for item in state['partitions']}
    for event in state['observations']:
        by_partition[event['partition_id']].append(event)
    for item in state['partitions']:
        events = by_partition[item['id']]
        observed_ids = set().union(*(set(event.get('accepted_ids', [])) for event in events))
        observed_by_partition[item['id']] = observed_ids
        if item['revision'] != len(events) or set(item['seen_ids']) != observed_ids:
            raise ValueError('Partition cursor does not match retained observations')
        if events and item['last_sequence'] != events[-1]['sequence']:
            raise ValueError('Partition request sequence is inconsistent')
        if item['status'] == 'complete' and (item['count'] is None or len(observed_ids) != item['count']
                                            or item['page'] * 100 < item['count'] or not events
                                            or events[-1]['status'] != 'ok' or events[-1]['incomplete_results']):
            raise ValueError('Completed partition lacks complete observed pages')
        if item['status'] == 'split':
            midpoint = (item['low'] + item['high']) // 2
            if item['low'] == item['high'] or any(partition_id(item['root'], low, high) not in ids
                    for low, high in ((item['low'], midpoint), (midpoint + 1, item['high']))):
                raise ValueError('Split partition is missing its children')
    for root in range(len(roots)):
        cursor = state['since']
        for item in sorted((p for p in state['partitions'] if p['root'] == root and p['status'] != 'split'), key=lambda p: p['low']):
            if item['low'] != cursor:
                raise ValueError('Leaf partitions overlap or leave an unexplained date gap')
            cursor = item['high'] + 1
        if cursor != state['until'] + 1:
            raise ValueError('Leaf partitions do not cover the declared date interval')
    for value in candidates.values():
        if value['matched_partitions'][0] != value['first_partition'] or [items[identifier]['root'] for identifier in value['matched_partitions']] != value['roots']:
            raise ValueError('Candidate query provenance does not match its partitions')
        for identifier in value['matched_partitions']:
            if value['id'] not in observed_by_partition[identifier]:
                raise ValueError('Candidate lacks an observed public search identity')


def cache_path(path, cache_root=None):
    root = (ROOT / '.cache' if cache_root is None else Path(cache_root)).resolve()
    path = Path(path)
    if path.is_symlink() or not path.resolve().is_relative_to(root) or path.resolve() == root:
        raise ValueError('Discovery frontier writes are restricted to the cache directory')
    return path


def save_frontier(path, state, *, approved_queries=None, cache_root=None):
    approved = QUERY_BASES if approved_queries is None else approved_queries
    validate_frontier(state, approved_queries=approved)
    path = cache_path(path, cache_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    if temporary.is_symlink():
        raise ValueError('Refusing a symlinked temporary frontier')
    fingerprint, size = hashlib.sha256(), 0
    encoder = json.JSONEncoder(ensure_ascii=False, separators=(',', ':'))
    try:
        with temporary.open('wb') as stream:
            for chunk in encoder.iterencode(state):
                raw = chunk.encode('utf-8')
                size += len(raw)
                if size + 1 > MAX_STATE_BYTES:  # Reserve the final newline.
                    raise ValueError('Frontier exceeds the state byte bound; existing file retained')
                stream.write(raw)
                fingerprint.update(raw)
            stream.write(b'\n')
            fingerprint.update(b'\n')
        temporary.replace(path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return fingerprint.hexdigest()


def load_frontier(path, *, approved_queries=None, cache_root=None):
    path = cache_path(path, cache_root)
    if not path.is_file() or not 0 < path.stat().st_size <= MAX_STATE_BYTES:
        raise ValueError('Frontier must be a bounded regular cache file')
    state = parse_json(path.read_text(encoding='utf-8'))
    validate_frontier(state, approved_queries=QUERY_BASES if approved_queries is None else approved_queries)
    return state


def summary(state):
    counts = {status: sum(p['status'] == status for p in state['partitions']) for status in STATUSES}
    return {'requests_recorded': state['request_count'], 'candidate_identities': len(state['candidates']),
            'pending_candidates': sum(v['checkpoint_sha256'] is None for v in state['candidates'].values()),
            'partitions': counts, 'traversal_finished': not counts['pending'] and not counts['blocked'],
            'global_completeness_established': False, 'readme_successes_measured_here': False}
