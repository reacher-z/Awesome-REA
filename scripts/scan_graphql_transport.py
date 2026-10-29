"""Bounded, read-only GitHub GraphQL transport for actual README bytes.

``GraphQLReadmeTransport(token).fetch_batch([{'id': 1, 'full_name': 'o/r'}])``
returns a mapping keyed by numeric repository ID. An ``ok`` result contains
ephemeral ``content`` bytes, fresh REST-shaped ``repository`` metadata, README
``metadata`` and body-free ``provenance``. Discard content after the scanner has
hashed/analyzed it; never serialize the whole result. Other statuses:

* fallback: public identity verified, but REST must resolve/verify the README;
* rejected: unavailable, ineligible or mismatched identity; do not read via REST;
* retry / deferred: transient failure / rate limit; keep pending, no REST escape.

No request is retried automatically. ``last_batch_receipts`` and ``rate_limit``
contain only allowlisted operational fields, never response bodies or credentials.
The caller must coordinate this instance with any other authenticated API traffic.

Selection follows GitHub's .github, root, docs priority. The first query captures
the default-branch commit's root tree and directory listings. Directory OIDs must
match that pinned root; a branch race therefore falls back instead of selecting
from a different commit. A second query measures only the selected blob at that
commit; bounded third-phase groups then read its text. Unrelated tree entries
never request sizes. Multiple recognized README files are left to REST.

Primary references:
https://docs.github.com/en/graphql/reference/git
https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api
https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes
"""
from __future__ import annotations

import datetime as dt
from email.utils import parsedate_to_datetime
import hashlib
from http.client import HTTPException
import json
import math
import re
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import HTTPRedirectHandler, Request, build_opener
from scan_diagnostics import failure_event


GRAPHQL_URL = 'https://api.github.com/graphql'
DEFAULT_BATCH_SIZE = 8
MAX_BATCH_SIZE = 16
MAX_RESPONSE_BYTES = 12 * 1024 * 1024
MAX_README_BYTES = 8 * 1024 * 1024
MAX_TREE_ENTRIES = 10000
# A JSON string can use six wire bytes per input byte. Leave room for metadata.
TEXT_RESPONSE_BUDGET = MAX_RESPONSE_BYTES - 128 * 1024
NAME_RE = re.compile(r'[A-Za-z0-9-]+/[A-Za-z0-9_.-]+\Z')
NODE_ID_RE = re.compile(r'[A-Za-z0-9_=/+:-]{1,256}\Z')
OID_RE = re.compile(r'[0-9a-f]{40}\Z')
README_RE = re.compile(r'readme(?:\.(?:md|markdown|mdown|mkdn|mkd|rst|txt|textile|rdoc|org|wiki|mediawiki|adoc|asciidoc))?\Z', re.I)
IDENTITY_FIELDS = '__typename databaseId nameWithOwner isPrivate isFork isArchived'
TREE_FIELDS = '__typename oid ... on Tree { entries { name type mode oid } }'
METADATA_FIELDS = IDENTITY_FIELDS + '''
  id url description stargazerCount updatedAt pushedAt licenseInfo { spdxId }
  repositoryTopics(first: 100) { nodes { topic { name } } pageInfo { hasNextPage } }
  defaultBranchRef { name target { __typename oid ... on Commit {
    tree { ''' + TREE_FIELDS + ''' }
  } } }
  githubDirectory: object(expression: "HEAD:.github") { ''' + TREE_FIELDS + ''' }
  docsDirectory: object(expression: "HEAD:docs") { ''' + TREE_FIELDS + ''' }
'''


class NoRedirect(HTTPRedirectHandler):
    """Even same-origin redirects are refused; the authenticated POST is fixed."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _utc(epoch):
    return dt.datetime.fromtimestamp(epoch, dt.timezone.utc).isoformat().replace('+00:00', 'Z')


def _integer(value, minimum=0):
    return type(value) is int and value >= minimum


def _oid(value):
    return isinstance(value, str) and bool(OID_RE.fullmatch(value))


def _json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate-json-key')
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError('non-finite-json-value')


def _identity(value, expected_id):
    # Check identity and public flags before using ANY returned name or metadata.
    if value is None:
        return 'repository-unavailable'
    if not isinstance(value, dict) or value.get('__typename') != 'Repository':
        return 'invalid-repository-metadata'
    if type(value.get('databaseId')) is not int or value['databaseId'] != expected_id:
        return 'repository-id-mismatch'
    if value.get('isPrivate') is not False:
        return 'public-status-unconfirmed'
    if value.get('isFork') is not False or value.get('isArchived') is not False:
        return 'repository-ineligible'
    if not isinstance(value.get('nameWithOwner'), str) or not NAME_RE.fullmatch(value['nameWithOwner']):
        return 'invalid-repository-metadata'
    return None


def _repository(value, observed_at):
    name = value['nameWithOwner']
    topics = value.get('repositoryTopics')
    license_info = value.get('licenseInfo')
    if (value.get('url') != 'https://github.com/' + name
            or not _integer(value.get('stargazerCount'))
            or not isinstance(value.get('id'), str) or not NODE_ID_RE.fullmatch(value['id'])
            or not isinstance(topics, dict) or not isinstance(topics.get('nodes'), list)
            or len(topics['nodes']) > 100
            or not isinstance(topics.get('pageInfo'), dict)
            or topics['pageInfo'].get('hasNextPage') is not False
            or (value.get('description') is not None and not isinstance(value['description'], str))
            or (license_info is not None and (not isinstance(license_info, dict)
                or (license_info.get('spdxId') is not None
                    and not isinstance(license_info['spdxId'], str))))):
        raise ValueError('invalid-repository-metadata')
    topic_names = []
    for node in topics['nodes']:
        topic = node.get('topic') if isinstance(node, dict) else None
        name_value = topic.get('name') if isinstance(topic, dict) else None
        if not isinstance(name_value, str) or not re.fullmatch(r'[a-z0-9-]{1,50}', name_value):
            raise ValueError('invalid-repository-topics')
        topic_names.append(name_value)
    for field in ('updatedAt', 'pushedAt'):
        timestamp = value.get(field)
        if timestamp is not None:
            if not isinstance(timestamp, str):
                raise ValueError('invalid-repository-timestamp')
            try:
                parsed = dt.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                if parsed.tzinfo is None:
                    raise ValueError
            except ValueError:
                raise ValueError('invalid-repository-timestamp') from None
    branch = value.get('defaultBranchRef')
    branch_name = branch.get('name') if isinstance(branch, dict) else None
    if branch_name is not None and (not isinstance(branch_name, str) or len(branch_name) > 1024):
        raise ValueError('invalid-default-branch')
    return {'id': value['databaseId'], 'node_id': value['id'], 'full_name': name,
            'name': name.split('/')[1], 'html_url': value['url'],
            'private': False, 'fork': False, 'archived': False,
            'description': value.get('description'), 'topics': sorted(set(topic_names)),
            'stargazers_count': value['stargazerCount'],
            'license': {'spdx_id': license_info.get('spdxId')} if license_info else None,
            'updated_at': value.get('updatedAt'), 'pushed_at': value.get('pushedAt'),
            'default_branch': branch_name, '_metadata_observed_at': observed_at}


def _entries(tree):
    if (not isinstance(tree, dict) or tree.get('__typename') != 'Tree'
            or not _oid(tree.get('oid')) or not isinstance(tree.get('entries'), list)
            or len(tree['entries']) > MAX_TREE_ENTRIES):
        raise ValueError('invalid-or-large-readme-tree')
    entries = {}
    for item in tree['entries']:
        if (not isinstance(item, dict) or not isinstance(item.get('name'), str)
                or not item['name'] or '/' in item['name'] or '\x00' in item['name']
                or item['name'] in ('.', '..') or item['name'] in entries
                or not _oid(item.get('oid')) or type(item.get('mode')) is not int
                or item.get('type') not in ('blob', 'tree', 'commit')):
            raise ValueError('invalid-readme-tree-entry')
        entries[item['name']] = item
    return entries


def _select_readme(value):
    branch = value.get('defaultBranchRef')
    target = branch.get('target') if isinstance(branch, dict) else None
    if not isinstance(target, dict) or target.get('__typename') != 'Commit' or not _oid(target.get('oid')):
        raise ValueError('default-branch-commit-unavailable')
    root = _entries(target.get('tree'))
    directories = {}
    for path, field in (('.github', 'githubDirectory'), ('docs', 'docsDirectory')):
        entry = root.get(path)
        if entry is None:
            directories[path] = {}
        elif entry['type'] != 'tree' or entry['mode'] != 0o040000:
            # Do not follow a directory symlink or submodule.
            raise ValueError('unsupported-readme-directory')
        else:
            tree = value.get(field)
            if not isinstance(tree, dict) or tree.get('oid') != entry['oid']:
                raise ValueError('readme-directory-commit-race')
            directories[path] = _entries(tree)
    for prefix, entries in (('.github', directories['.github']), ('', root), ('docs', directories['docs'])):
        candidates = [item for name, item in entries.items() if README_RE.fullmatch(name)]
        if not candidates:
            continue
        if len(candidates) != 1:
            raise ValueError('ambiguous-readme-selection')
        item = candidates[0]
        if item['type'] != 'blob' or item['mode'] not in (0o100644, 0o100755):
            raise ValueError('unsupported-readme-file')
        return {'path': (prefix + '/' if prefix else '') + item['name'],
                'sha': item['oid'], 'commit_oid': target['oid']}
    raise ValueError('no-recognized-readme')


class GraphQLReadmeTransport:
    """Sequential, bounded queries. Use one shared instance per scan process."""
    def __init__(self, token, *, batch_size=DEFAULT_BATCH_SIZE, interval=1.0,
                 timeout=30, opener=None, clock=time.time, monotonic=time.monotonic,
                 sleep=time.sleep, capture_diagnostics=False):
        if not isinstance(token, str) or not token or any(c in token for c in '\r\n'):
            raise ValueError('A nonempty in-memory token is required')
        if type(batch_size) is not int or not 1 <= batch_size <= MAX_BATCH_SIZE:
            raise ValueError('batch_size must be between 1 and 16')
        if (not isinstance(interval, (int, float)) or isinstance(interval, bool)
                or not math.isfinite(interval) or not 1 <= interval <= 60):
            raise ValueError('interval must be between 1 and 60 seconds')
        if type(timeout) not in (int, float) or not math.isfinite(timeout) or not 0 < timeout <= 60:
            raise ValueError('timeout must be positive and at most 60 seconds')
        self._token = token
        self.batch_size, self.interval, self.timeout = batch_size, interval, timeout
        self._opener = opener if opener is not None else build_opener(NoRedirect())
        self._clock, self._monotonic, self._sleep = clock, monotonic, sleep
        self._lock = threading.Lock()
        self._last_request = None
        self._blocked_until = 0
        self.last_batch_receipts = []
        self.last_batch_diagnostics = []
        self._capture_diagnostics = capture_diagnostics
        self.rate_limit = {}

    def _diagnose(self, receipt, reason, *, request_attempted=True, repository_count=None):
        if self._capture_diagnostics:
            event = failure_event(receipt, reason, request_attempted=request_attempted,
                                  repository_count=repository_count)
            if event is not None:
                self.last_batch_diagnostics.append(event)

    def _delay(self, headers, rate, secondary=False):
        delay = 60 if secondary else 1
        retry = headers.get('Retry-After')
        if retry is not None:
            try:
                candidate = float(retry)
                if math.isfinite(candidate):
                    delay = max(delay, candidate)
            except (ValueError, TypeError):
                try:
                    delay = max(delay, parsedate_to_datetime(retry).timestamp() - self._clock())
                except (ValueError, TypeError, OverflowError):
                    pass
        reset = headers.get('X-RateLimit-Reset')
        if rate and rate.get('remaining') == 0:
            reset = rate.get('reset_at_epoch', reset)
        if headers.get('X-RateLimit-Remaining') == '0' or (rate and rate.get('remaining') == 0):
            try:
                value = float(reset)
                if math.isfinite(value):
                    delay = max(delay, value - self._clock() + 1)
            except (ValueError, TypeError):
                delay = max(delay, 60)
        return max(1, math.ceil(delay))

    def _rate(self, data, headers):
        source = data.get('rateLimit') if isinstance(data, dict) else None
        result = {}
        if isinstance(source, dict):
            for name in ('cost', 'remaining', 'limit'):
                if _integer(source.get(name)):
                    result[name] = source[name]
            reset = source.get('resetAt')
            if isinstance(reset, str):
                try:
                    parsed = dt.datetime.fromisoformat(reset.replace('Z', '+00:00'))
                    if parsed.tzinfo is not None:
                        result['reset_at_epoch'] = int(parsed.timestamp())
                except (ValueError, OverflowError):
                    pass
        for header, key in (('X-RateLimit-Remaining', 'remaining'), ('X-RateLimit-Limit', 'limit'),
                            ('X-RateLimit-Reset', 'reset_at_epoch')):
            value = headers.get(header)
            if isinstance(value, str) and re.fullmatch(r'\d{1,12}', value):
                result[key] = int(value)
        self.rate_limit = result
        return result

    def _request(self, query, variables, phase, count):
        receipt = {'phase': phase, 'repository_count': count, 'endpoint': GRAPHQL_URL,
                   'method': 'POST', 'observed_at': _utc(self._clock())}
        remaining_delay = math.ceil(self._blocked_until - self._monotonic())
        if remaining_delay > 0:
            self._diagnose(receipt, 'graphql-rate-limit', request_attempted=False)
            return None, {'status': 'deferred', 'reason': 'graphql-rate-limit', 'retry_after': remaining_delay}, receipt
        if self._last_request is not None:
            wait = self.interval - (self._monotonic() - self._last_request)
            if wait > 0:
                self._sleep(wait)
        receipt['observed_at'] = _utc(self._clock())
        body = json.dumps({'query': query, 'variables': variables}, ensure_ascii=True).encode('utf-8')
        if len(body) > 128 * 1024:
            raise ValueError('GraphQL request exceeds fixed request budget')
        request = Request(GRAPHQL_URL, data=body, method='POST', headers={
            'Authorization': 'Bearer ' + self._token, 'Content-Type': 'application/json',
            'Accept': 'application/vnd.github+json', 'User-Agent': 'Awesome-REA-source-index',
            'X-GitHub-Api-Version': '2022-11-28', 'Accept-Encoding': 'identity'})
        self._last_request = self._monotonic()
        headers, status, raw = {}, None, b''
        try:
            with self._opener.open(request, timeout=self.timeout) as response:
                status = response.status
                headers = response.headers
                raw = response.read(MAX_RESPONSE_BYTES + 1)
        except HTTPError as error:
            status, headers = error.code, error.headers
            try:
                raw = error.read(4096)
            finally:
                error.close()
        except (URLError, TimeoutError, OSError, HTTPException):
            receipt['reason'] = 'graphql-network-error'
            # Status may have arrived before a response-read exception. Keep
            # this context in the sidecar only; existing receipt metrics stay exact.
            self._diagnose({**receipt, 'http_status': status}, receipt['reason'])
            self.last_batch_receipts.append(receipt)
            return None, {'status': 'retry', 'reason': receipt['reason']}, receipt
        receipt['http_status'] = status
        receipt['response_bytes'] = len(raw)
        parsed = None
        if len(raw) <= MAX_RESPONSE_BYTES:
            try:
                parsed = json.loads(raw.decode('utf-8'), object_pairs_hook=_json_object,
                                    parse_constant=_reject_constant)
            except (UnicodeDecodeError, ValueError, RecursionError):
                pass
        data = parsed.get('data') if isinstance(parsed, dict) else None
        errors = parsed.get('errors') if isinstance(parsed, dict) else None
        rate = self._rate(data, headers)
        receipt['rate_limit'] = dict(rate)
        rate_error = status == 429
        if isinstance(errors, list):
            for error in errors:
                if isinstance(error, dict):
                    message = error.get('message', '')
                    kind = error.get('type')
                    extensions = error.get('extensions')
                    code = extensions.get('code') if isinstance(extensions, dict) else None
                    if (kind in ('RATE_LIMITED', 'ABUSE_DETECTED') or code in ('RATE_LIMITED', 'ABUSE_DETECTED')
                            or (isinstance(message, str) and any(term in message.lower()
                                for term in ('rate limit', 'rate_limit', 'secondary limit', 'abuse detection')))):
                        rate_error = True
        if status == 403 and (headers.get('Retry-After') is not None or b'rate limit' in raw.lower()
                              or b'secondary limit' in raw.lower()):
            rate_error = True
        exhausted = rate.get('remaining') == 0
        if rate_error or exhausted:
            delay = self._delay(headers, rate, secondary=rate_error and not exhausted)
            self._blocked_until = self._monotonic() + delay
            receipt['retry_after'] = delay
        # Metadata/preflight at zero remaining cannot initiate a text query or
        # an ambiguity fallback through a different API.
        if rate_error or (exhausted and (errors or phase in ('metadata', 'preflight'))):
            failure = {'status': 'deferred', 'reason': 'graphql-rate-limit', 'retry_after': delay}
        elif status in (401, 403):
            failure = {'status': 'deferred', 'reason': 'graphql-access-denied'}
        elif status is None or status >= 500:
            failure = {'status': 'retry', 'reason': 'graphql-server-error'}
        elif status != 200:
            failure = {'status': 'retry', 'reason': 'graphql-http-error'}
        elif len(raw) > MAX_RESPONSE_BYTES:
            failure = {'status': 'retry', 'reason': 'graphql-response-too-large'}
        elif not isinstance(data, dict):
            failure = {'status': 'retry', 'reason': 'invalid-graphql-response'}
        elif errors and not self._only_missing_repositories(errors, data):
            # Even partial data is not counted; retry at a smaller batch if necessary.
            failure = {'status': 'retry', 'reason': 'graphql-query-error'}
        else:
            failure = None
        if failure:
            receipt['reason'] = failure['reason']
            self._diagnose(receipt, failure['reason'])
        self.last_batch_receipts.append(receipt)
        return data if failure is None else None, failure, receipt

    @staticmethod
    def _only_missing_repositories(errors, data):
        # An unavailable alias must not poison every healthy repository in its
        # batch. Only a top-level NOT_FOUND with a null alias is safe to isolate.
        if not isinstance(errors, list):
            return False
        for error in errors:
            path = error.get('path') if isinstance(error, dict) else None
            if (not isinstance(path, list) or len(path) != 1
                    or not isinstance(path[0], str) or not re.fullmatch(r'r\d+', path[0])
                    or error.get('type') != 'NOT_FOUND' or path[0] not in data
                    or data[path[0]] is not None):
                return False
        return True

    @staticmethod
    def _query(repositories, selections=None, *, include_text=True):
        definitions, fields, variables = [], [], {}
        for index, repo in enumerate(repositories):
            if repo.get('node_id'):
                # A stored public node ID survives repository renames. Numeric
                # databaseId is still checked before exposing any returned data.
                definitions.append(f'$node{index}: ID!')
                variables[f'node{index}'] = repo['node_id']
                lookup = f'node(id: $node{index})'
            else:
                owner, name = repo['full_name'].split('/')
                definitions += [f'$owner{index}: String!', f'$name{index}: String!']
                variables.update({f'owner{index}': owner, f'name{index}': name})
                lookup = f'repository(owner: $owner{index}, name: $name{index})'
            if selections is None:
                selection = METADATA_FIELDS
            else:
                definitions.append(f'$expression{index}: String!')
                chosen = selections[repo['id']]
                variables[f'expression{index}'] = chosen['commit_oid'] + ':' + chosen['path']
                blob_fields = 'byteSize isBinary isTruncated' + (' text' if include_text else '')
                selection = IDENTITY_FIELDS + f''' readme: object(expression: $expression{index}) {{
                    __typename oid ... on Blob {{ {blob_fields} }}
                }}'''
            if repo.get('node_id'):
                selection = '... on Repository { ' + selection + ' }'
            fields.append(f'r{index}: {lookup} {{ {selection} }}')
        return ('query ReadmeBatch(' + ', '.join(definitions) + ') { ' + ' '.join(fields)
                + ' rateLimit { cost remaining limit resetAt } }'), variables

    @staticmethod
    def _result(status, reason=None, repository=None, metadata=None, content=None, provenance=None, **extra):
        return {'status': status, 'reason': reason, 'repository': repository, 'metadata': metadata,
                'content': content, 'provenance': provenance or {}, **extra}

    def fetch_batch(self, repositories):
        """Read at most batch_size queued public IDs; do not count non-ok results.

        Raises ValueError for invalid/duplicate inputs before any request. No queue
        metadata is trusted or copied into returned metadata. Callers can combine
        their own discovery provenance after checking the returned numeric ID.
        """
        repos = list(repositories)
        if len(repos) > self.batch_size:
            raise ValueError('Batch exceeds configured repository limit')
        seen = set()
        for repo in repos:
            if (not isinstance(repo, dict) or not _integer(repo.get('id'), 1)
                    or not isinstance(repo.get('full_name'), str) or not NAME_RE.fullmatch(repo['full_name'])
                    or (repo.get('node_id') is not None and (not isinstance(repo['node_id'], str)
                        or not NODE_ID_RE.fullmatch(repo['node_id'])))
                    or repo['id'] in seen):
                raise ValueError('Invalid or duplicate queued public repository ID/name')
            seen.add(repo['id'])
        with self._lock:
            self.last_batch_receipts = []
            self.last_batch_diagnostics = []
            return self._fetch(repos) if repos else {}

    def _fetch(self, repos):
        query, variables = self._query(repos)
        data, failure, receipt = self._request(query, variables, 'metadata', len(repos))
        if failure:
            return {repo['id']: self._result(**failure) for repo in repos}
        outcomes, selected, eligible = {}, {}, []
        for index, queued in enumerate(repos):
            key = queued['id']
            value = data.get(f'r{index}')
            identity_error = _identity(value, key)
            if identity_error:
                outcomes[key] = self._result('rejected', identity_error)
                continue
            try:
                repo = _repository(value, receipt['observed_at'])
            except ValueError as error:
                self._diagnose(receipt, str(error), repository_count=1)
                outcomes[key] = self._result('retry', str(error))
                continue
            try:
                chosen = _select_readme(value)
            except ValueError as error:
                outcomes[key] = self._result('fallback', str(error), repository=repo)
                continue
            selected[key] = chosen
            eligible.append(repo)
        batch_failure = None
        measured = []
        if eligible:
            query, variables = self._query(eligible, selected, include_text=False)
            data, batch_failure, receipt = self._request(query, variables, 'preflight', len(eligible))
            for index, repo in enumerate(eligible):
                key = repo['id']
                if batch_failure:
                    outcomes[key] = self._result(**batch_failure, repository=repo)
                    continue
                value = data.get(f'r{index}')
                identity_error = _identity(value, key)
                if identity_error:
                    outcomes[key] = self._result('rejected', identity_error)
                    continue
                chosen = selected[key]
                blob = value.get('readme')
                reason = None
                if (not isinstance(blob, dict) or blob.get('__typename') != 'Blob'
                        or blob.get('oid') != chosen['sha']):
                    reason = 'readme-blob-identity-mismatch'
                elif blob.get('isBinary') is not False or blob.get('isTruncated') is not False:
                    reason = 'binary-unknown-or-truncated-readme'
                elif not _integer(blob.get('byteSize')):
                    reason = 'readme-byte-size-mismatch'
                elif blob['byteSize'] > MAX_README_BYTES or blob['byteSize'] * 6 + 4096 > TEXT_RESPONSE_BUDGET:
                    reason = 'readme-exceeds-graphql-byte-budget'
                elif not blob['byteSize']:
                    reason = 'empty-or-nontext-readme'
                current_name = value['nameWithOwner']
                repo = {**repo, 'full_name': current_name, 'name': current_name.split('/')[1],
                        'html_url': 'https://github.com/' + current_name}
                if reason:
                    outcomes[key] = self._result('fallback', reason, repository=repo)
                    continue
                selected[key] = {**chosen, 'size': blob['byteSize']}
                measured.append(repo)
        # Response budget also applies to the aggregate, not only each blob.
        groups, group, budget = [], [], 0
        for repo in measured:
            estimate = selected[repo['id']]['size'] * 6 + 4096
            if group and budget + estimate > TEXT_RESPONSE_BUDGET:
                groups.append(group)
                group, budget = [], 0
            group.append(repo)
            budget += estimate
        if group:
            groups.append(group)
        for group in groups:
            if batch_failure:
                data, failure = None, batch_failure
            else:
                query, variables = self._query(group, selected)
                data, failure, receipt = self._request(query, variables, 'blob', len(group))
                batch_failure = failure
            for index, repo in enumerate(group):
                key = repo['id']
                if failure:
                    outcomes[key] = self._result(**failure, repository=repo)
                    continue
                value = data.get(f'r{index}')
                identity_error = _identity(value, key)
                if identity_error:
                    # Visibility/identity can change at any phase.
                    outcomes[key] = self._result('rejected', identity_error)
                    continue
                current_name = value['nameWithOwner']
                repo = {**repo, 'full_name': current_name, 'name': current_name.split('/')[1],
                        'html_url': 'https://github.com/' + current_name}
                chosen = selected[key]
                blob = value.get('readme')
                reason = None
                if (not isinstance(blob, dict) or blob.get('__typename') != 'Blob'
                        or blob.get('oid') != chosen['sha']):
                    reason = 'readme-blob-identity-mismatch'
                elif blob.get('isBinary') is not False or blob.get('isTruncated') is not False:
                    reason = 'binary-unknown-or-truncated-readme'
                elif not isinstance(blob.get('text'), str):
                    reason = 'readme-text-unavailable'
                else:
                    try:
                        content = blob['text'].encode('utf-8', errors='strict')
                    except UnicodeEncodeError:
                        reason = 'invalid-readme-utf8'
                    else:
                        if (not _integer(blob.get('byteSize')) or len(content) != blob['byteSize']
                                or len(content) != chosen['size'] or len(content) > MAX_README_BYTES):
                            reason = 'readme-byte-size-mismatch'
                        elif not content or b'\x00' in content:
                            reason = 'empty-or-nontext-readme'
                        elif hashlib.sha1(b'blob ' + str(len(content)).encode('ascii') + b'\0' + content).hexdigest() != blob['oid']:
                            reason = 'readme-content-git-sha-mismatch'
                if reason:
                    outcomes[key] = self._result('fallback', reason, repository=repo)
                    continue
                metadata = {**chosen, 'type': 'file', 'html_url': repo['html_url'] + '/blob/'
                            + chosen['commit_oid'] + '/' + quote(chosen['path'], safe='/')}
                provenance = {'transport': 'github-graphql', 'endpoint': GRAPHQL_URL, 'method': 'POST',
                              'observed_at': receipt['observed_at'], 'commit_oid': chosen['commit_oid'],
                              'blob_oid': chosen['sha'], 'content_sha256': hashlib.sha256(content).hexdigest(),
                              'content_git_sha_matches_blob': True,
                              'selection': 'github-readme-locations-single-candidate'}
                outcomes[key] = self._result('ok', repository=repo, metadata=metadata,
                                             content=content, provenance=provenance)
        if batch_failure is None and self.rate_limit.get('remaining') == 0:
            batch_failure = {'status': 'deferred', 'reason': 'graphql-rate-limit',
                             'retry_after': max(1, math.ceil(self._blocked_until - self._monotonic()))}
            if any(result['status'] == 'fallback' for result in outcomes.values()):
                self._diagnose(receipt, batch_failure['reason'])
        if batch_failure:
            # A fallback discovered before a sibling's rate/network failure must
            # not become an API escape route. Verified ok bytes remain usable.
            for key, result in outcomes.items():
                if result['status'] == 'fallback':
                    outcomes[key] = self._result(**batch_failure, repository=result['repository'])
        return outcomes
