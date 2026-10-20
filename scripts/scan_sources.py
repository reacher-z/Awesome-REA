#!/usr/bin/env python3
"""Discover public GitHub RE repositories and actually read/hash each accepted README.

Uses only the Python standard library and an existing gh login. Authentication
stays in memory and is sent only to api.github.com. No repository code is run.
"""
from __future__ import annotations

import argparse
import base64
import copy
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
import datetime as dt
import hashlib
from functools import lru_cache
import json
from pathlib import Path
import re
import subprocess
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from source_descriptions import SOURCE_DESCRIPTION_POLICY, capture_description
from source_scope import DUPLICATE_README_REASON, read_scope
import strict_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / 'data/source-index.json'
QUERY_BASES = [
    '"reverse engineering" in:name,description',
    'topic:reverse-engineering',
    'topic:binary-analysis',
    'topic:ghidra',
    'topic:ida-plugin',
    'topic:frida',
    'topic:decompiler',
    'topic:disassembler',
    'topic:firmware-analysis',
    'topic:android-reverse-engineering',
    'topic:apk-analysis',
    'topic:game-reversing',
    'topic:game-decompilation',
    'topic:decompilation',
    'topic:javascript-deobfuscation',
    'topic:deobfuscation',
    'topic:protocol-analysis',
    'topic:binary-diffing',
    'topic:radare2',
    'topic:reversing',
    'topic:reverse-engineering-tools',
    'topic:il2cpp',
    'topic:jadx',
    'topic:binwalk',
    'topic:unpacking',
    'topic:memory-forensics',
    'topic:malware-analysis',
    'topic:ghidra-plugin',
    'topic:idapro',
    'topic:frida-script',
    'topic:wasm topic:reverse-engineering',
    '"firmware" "analysis" in:description',
    '"protocol" "reverse engineering" in:description',
    '"deobfuscator" in:name,description',
    '"disassembler" in:name,description',
    '"decompiler" in:name,description',
]
QUERIES = [query + ' is:public fork:false archived:false' for query in QUERY_BASES]
MAX_README_BYTES = 8 * 1024 * 1024
MAX_API_BYTES = 12 * 1024 * 1024
# Version 3 matches topics separately, ignores omitted descriptions and leaves curated labels to the build.
# Version 4 adds the protocol target from the same explicit signal as the protocol-analysis category.
CLASSIFICATION_ENGINE_VERSION = 4
CLASSIFICATION_POLICY = ('Automatic labels use repository names, URL-stripped published descriptions and explicit topics, with primary-function precedence. '
                         'Engine 3 matches each topic separately and never classifies an omitted description, so labels are a pure function of the published fields; '
                         'records it captures carry classification_engine_version. Engine 4 assigns the protocol target and the protocol-analysis category from one '
                         'explicit protocol-analysis signal; MCP, REST API and mitmproxy mentions alone do not qualify. Curated cross-references are derived when the site and directories are built, '
                         'not at scan time; retained records keep their stored labels. Labels do not establish REA compatibility. Empty targets mean insufficient metadata.')
# Explicit communication-format or traffic analysis. Model Context Protocol wording is removed before matching;
# REST API usage and mitmproxy as a toolkit component remain website signals only.
PROTOCOL_TOPICS = frozenset({'protocol-analysis', 'protocol-analyser', 'packet-analysis', 'pcap', 'wireshark', 'network-forensics'})
PROTOCOL_WORDING = r'\bpcap\b|\bwireshark\b|\bnetwork[- ]protocol\b|\bprotocol[- ](?:analy|revers)'
MCP_WORDING = r'model[\s-]*context[\s-]*protocol|\bmodelcontextprotocol\b|\bmcp\b'


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z')


class ScanError(Exception):
    def __init__(self, reason, status=None):
        super().__init__(reason)
        self.reason, self.status = reason, status


def is_api_origin(url):
    """Credentials may only follow redirects within GitHub's HTTPS API origin."""
    try:
        parsed = urlsplit(url)
        return (parsed.scheme == 'https' and parsed.hostname == 'api.github.com'
                and parsed.port in (None, 443)
                and parsed.username is None and parsed.password is None)
    except ValueError:
        return False


class APIOnlyRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        if not is_api_origin(new_url):
            raise ScanError('refused-non-github-api-redirect', code)
        return super().redirect_request(request, fp, code, message, headers, new_url)


class GitHub:
    def __init__(self, token, requests_per_second=12):
        self._token = token
        self._lock = threading.Lock()
        self._next_request = 0.0
        self._next_search = 0.0
        self._pause_until = 0.0
        self._interval = 1.0 / requests_per_second
        self.rate = {}

    def _throttle(self, search):
        with self._lock:
            current = time.monotonic()
            slot = max(current, self._next_request, self._pause_until,
                       self._next_search if search else 0)
            self._next_request = slot + self._interval
            if search:
                self._next_search = slot + 2.1
        while time.monotonic() < slot:
            time.sleep(min(5, slot - time.monotonic()))
        # A later response may have announced a shared secondary-limit pause.
        while True:
            with self._lock:
                delay = self._pause_until - time.monotonic()
            if delay <= 0:
                break
            time.sleep(min(5, delay))

    def _record_headers(self, headers):
        resource = headers.get('X-RateLimit-Resource')
        if resource:
            with self._lock:
                self.rate[resource] = {
                    'remaining': int(headers.get('X-RateLimit-Remaining', 0)),
                    'limit': int(headers.get('X-RateLimit-Limit', 0)),
                    'reset': int(headers.get('X-RateLimit-Reset', 0)),
                }

    def get(self, path, accept='application/vnd.github+json', search=False):
        url = 'https://api.github.com' + path
        if not path.startswith('/') or not is_api_origin(url):
            raise ScanError('invalid-api-endpoint')
        for attempt in range(4):
            self._throttle(search)
            request = Request(url, headers={
                'Authorization': 'Bearer ' + self._token,
                'Accept': accept,
                'X-GitHub-Api-Version': '2022-11-28',
                'User-Agent': 'Awesome-REA-source-index',
            })
            try:
                # Each worker owns its request/connection; redirects cannot send credentials elsewhere.
                with build_opener(APIOnlyRedirect()).open(request, timeout=30) as response:
                    self._record_headers(response.headers)
                    content = response.read(MAX_API_BYTES + 1)
                    if len(content) > MAX_API_BYTES:
                        raise ScanError('api-response-too-large')
                    return content
            except HTTPError as error:
                self._record_headers(error.headers)
                status = error.code
                body = error.read(4096).decode('utf-8', errors='replace').lower()
                retry_header = error.headers.get('Retry-After')
                remaining = error.headers.get('X-RateLimit-Remaining')
                reset = error.headers.get('X-RateLimit-Reset')
                error.close()
                limited = status == 429 or (status == 403 and (
                    remaining == '0' or 'rate limit' in body or retry_header))
                if limited and attempt < 3:
                    if remaining == '0' and reset:
                        pause = max(1, int(reset) - time.time() + 1)
                    else:
                        pause = float(retry_header) if retry_header and retry_header.isdigit() else 60
                    with self._lock:
                        self._pause_until = max(self._pause_until, time.monotonic() + pause)
                    print(f'RATE_LIMIT resource={"search" if search else "core"} retry_seconds={int(pause)}', flush=True)
                    continue
                if status in {500, 502, 503, 504} and attempt < 3:
                    time.sleep(min(5, 2 ** attempt))
                    continue
                raise ScanError('http-' + str(status), status) from None
            except (URLError, TimeoutError, OSError):
                if attempt < 3:
                    time.sleep(min(5, 2 ** attempt))
                    continue
                raise ScanError('network-failure') from None
        raise ScanError('retry-limit')

    def json(self, path, search=False):
        try:
            return json.loads(self.get(path, search=search))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ScanError('invalid-api-json') from None


@lru_cache(maxsize=1)
def curated_references():
    """Seed explicit curated GitHub repositories; labels are derived at build time."""
    result = {}
    for filename in ('rea-resources.json', 'tool-resources.json'):
        path = ROOT / 'data' / filename
        if not path.exists():
            continue
        for record in json.loads(path.read_text(encoding='utf-8')):
            parsed = urlsplit(record['url'])
            parts = parsed.path.strip('/').split('/')
            if parsed.hostname != 'github.com' or len(parts) < 2:
                continue
            key = '/'.join(parts[:2]).casefold()
            result.setdefault(key, {'ids': []})['ids'].append(record['id'])
    return result


@lru_cache(maxsize=1)
def paper_references():
    """Seed only explicit bibliography artifact links, without changing labels."""
    result = {}
    path = ROOT / 'data/papers.json'
    if not path.exists():
        return result
    for paper in json.loads(path.read_text(encoding='utf-8')):
        for field in ('code_url', 'project_url'):
            url = paper.get(field)
            if not isinstance(url, str):
                continue
            parsed = urlsplit(url)
            parts = parsed.path.strip('/').split('/')
            if (parsed.scheme != 'https' or parsed.hostname != 'github.com'
                    or parsed.netloc != 'github.com' or len(parts) < 2):
                continue
            name = '/'.join(parts[:2]).removesuffix('.git').casefold()
            if not re.fullmatch(r'[a-z0-9-]+/[a-z0-9_.-]+', name):
                continue
            reference = result.setdefault(name, {'ids': [], 'artifacts': []})
            if paper['id'] not in reference['ids']:
                reference['ids'].append(paper['id'])
            reference['artifacts'].append({'paper_id': paper['id'], 'field': field, 'url': url})
    return result


def repository_ineligibility(repo):
    """Do not retain names, URLs or descriptions from private API responses."""
    if not isinstance(repo, dict):
        raise ScanError('invalid-repository-metadata')
    if repo.get('private') is True:
        return 'private'
    if repo.get('private') is not False:
        return 'public-status-unconfirmed'
    if repo.get('fork') is True:
        return 'fork'
    if repo.get('archived') is True:
        return 'archived'
    if repo.get('fork') is not False or repo.get('archived') is not False:
        return 'eligibility-unconfirmed'
    return None


def classification_segments(repo):
    """Return the lowercased topics, name-and-description text and separately matched segments."""
    topics = {topic.lower() for topic in repo.get('topics', [])}
    description = re.sub(r'https?://[^\s<>]+', ' ', repo.get('description') or '', flags=re.I)
    purpose = (repo['full_name'] + ' ' + description).lower()
    # Each topic is matched alone, so adjacency patterns cannot join two unrelated topics.
    return topics, purpose, (purpose, *sorted(topics))


def protocol_signals(repo):
    """List the explicit protocol-analysis evidence that sets both the target and the category."""
    topics, purpose, _ = classification_segments(repo)
    signals = ['topic:' + topic for topic in sorted(topics & PROTOCOL_TOPICS)]
    # Model Context Protocol is an agent interface, not evidence of network-protocol analysis.
    text = re.sub(MCP_WORDING, ' ', purpose)
    signals += ['text:' + match for match in sorted({match[0] for match in re.finditer('(?:' + PROTOCOL_WORDING + r')\w*', text)})]
    signals += ['topic:' + topic for topic in sorted(topics - PROTOCOL_TOPICS)
                if re.search(PROTOCOL_WORDING, re.sub(MCP_WORDING, ' ', topic))]
    return signals


def classify(repo):
    """Label one capture from its name, published description and topics alone."""
    topics, purpose, segments = classification_segments(repo)

    def mentions(pattern, values=segments):
        return any(re.search(pattern, value) for value in values)

    targets = set()
    managed = bool(topics & {'csharp', 'c-sharp', 'managed-code', 'ilspy', 'dnspy'} or
                   any(t == 'dotnet' or t.startswith('dotnet-') for t in topics) or
                   mentions(r'(?<![\w./-])\.net\b|\bdotnet\b|\bcsharp\b|\bc-sharp\b|\bcil\b|\bilspy\b|\bdnspy\b'))
    android = mentions(r'\bandroid\b|\bapk\b|\bjadx\b|\bdex\b')
    native = bool(topics & {'binary-analysis', 'binary-diffing', 'ghidra', 'ida-plugin', 'idapro',
                           'frida', 'radare2', 'rizin', 'disassembler', 'memory-forensics', 'debugger'} or
                  mentions(r'\bbinar(?:y|ies)\b|\bdisassembl|\bghidra\b|\bida\b|\bradare2\b|\brizin\b|\bcutter\b|\bx64dbg\b|\bgdb\b|\blldb\b|\belf\b|\bmach-o\b|\bnative\b|\bassembly\b|\bx86\b|\bx64\b|\barm(?:32|64)?\b|\bavr\b|\brisc-v\b|\briscv\b|\bmips\b'))
    native_primary = bool(re.search(r'\bbinar(?:y|ies)\b|\bdisassembl|\bghidra\b|\bida\b|\bradare2\b|\brizin\b|\bcutter\b|\bx64dbg\b|\bgdb\b|\blldb\b|\bassembly\b|\bx86\b|\bx64\b|\barm(?:32|64)?\b|\bavr\b|\brisc-v\b|\briscv\b|\bmips\b', purpose))
    dynamic = bool(topics & {'frida', 'frida-script', 'memory-forensics', 'debugger'} or
                   re.search(r'\bdebugger\b|\binstrument(?:ation|able)\b', purpose))
    web_explicit = bool(topics & {'javascript-deobfuscation', 'web-reversing', 'website-clone',
                                  'web-scraping', 'browser', 'mitmproxy', 'openapi', 'swagger', 'rest-api'} or
                        re.search(r'\bwebsite\b|\bweb-site\b|\bbrowser\b|\belectron\b|\brest[- ]apis?\b|\bmitmproxy\b|\bweb\b|javascript.{0,30}(?:deobfuscat|decompil)|(?:deobfuscat|decompil).{0,30}javascript', purpose))
    if web_explicit or (topics & {'webassembly', 'wasm'} and not native_primary):
        targets.add('website')
    if topics & {'game-reversing', 'game-decompilation', 'il2cpp', 'unity-reverse-engineering', 'galgame', 'visual-novel'} or mentions(r'\bgames?\b|\bunity\b|\bunreal\b|\bplaystation\b|\btouhou\b|\bgamecube\b|\bvisual novel\b'):
        targets.add('game')
    if managed or android or mentions(r'\bios\b|\bipados\b|\belectron\b|\bmobile\b|\bdesktop\b|\bapp(?:lication)?s?\b|java[- ](?:bytecode|decompiler)'):
        targets.add('app')
    if mentions(r'\bfirmware\b|\bbinwalk\b|\bunblob\b|\buefi\b|\bbios\b'):
        targets.add('firmware')
    if native:
        targets.add('binary')
    # The protocol target and the protocol-analysis category share one qualifying signal.
    protocol = bool(protocol_signals(repo))
    if protocol:
        targets.add('protocol')
    collection = bool(topics & {'awesome', 'awesome-list', 'awesome-lists', 'references'} or
                      re.search(r'\b(?:collection|list|reference)\b', purpose))
    if managed:
        category = 'managed-code'
    elif native_primary:
        category = 'dynamic-analysis' if dynamic else 'native-analysis'
    elif collection:
        category = 'reverse-engineering'
    elif android:
        category = 'android'
    elif 'firmware' in targets:
        category = 'firmware'
    elif 'game' in targets:
        category = 'game-analysis'
    elif protocol:
        category = 'protocol-analysis'
    elif 'website' in targets:
        category = 'web-analysis'
    elif dynamic:
        category = 'dynamic-analysis'
    elif native:
        category = 'native-analysis'
    else:
        category = 'reverse-engineering'
    return sorted(targets), category


def published_fields(record):
    """Rebuild the classifier input from a retained record; omitted descriptions stay empty."""
    description = '' if record.get('description_omission') else record.get('description_en') or ''
    return {'full_name': record['full_name'], 'description': description, 'topics': record.get('topics', [])}


def relabel_report(document):
    """List retained automatic labels that this engine would change; nothing is rewritten."""
    differences, compared, skipped = [], 0, 0
    for record in document['resources']:
        if record.get('classification_origin') != 'automatic-metadata':
            skipped += 1
            continue
        compared += 1
        targets, category = classify(published_fields(record))
        if targets != sorted(record.get('targets', [])) or category != record.get('category'):
            differences.append({
                'id': record['id'], 'full_name': record['full_name'],
                'stored_engine_version': record.get('classification_engine_version'),
                'stored': {'targets': record.get('targets', []), 'category': record.get('category')},
                'rederived': {'targets': targets, 'category': category},
            })
    return {'classification_engine_version': CLASSIFICATION_ENGINE_VERSION,
            'compared_automatic_records': compared, 'skipped_cross_referenced_records': skipped,
            'differing_records': len(differences), 'records': differences}


def protocol_report(document):
    """List retained automatic records whose protocol labels this engine would change, with the qualifying evidence."""
    rows, compared, skipped = [], 0, 0
    counts = {'adds-protocol-target': 0, 'enters-protocol-analysis': 0, 'leaves-protocol-analysis': 0}
    for record in document['resources']:
        if record.get('classification_origin') != 'automatic-metadata':
            skipped += 1
            continue
        compared += 1
        fields = published_fields(record)
        targets, category = classify(fields)
        stored_targets, stored_category = record.get('targets', []), record.get('category')
        changes = []
        if 'protocol' in targets and 'protocol' not in stored_targets:
            changes.append('adds-protocol-target')
        if (category == 'protocol-analysis') != (stored_category == 'protocol-analysis'):
            changes.append('enters-protocol-analysis' if category == 'protocol-analysis' else 'leaves-protocol-analysis')
        if not changes:
            continue
        for change in changes:
            counts[change] += 1
        rows.append({
            'id': record['id'], 'full_name': record['full_name'], 'changes': changes,
            'protocol_signals': protocol_signals(fields),
            'stored_engine_version': record.get('classification_engine_version'),
            'stored': {'targets': stored_targets, 'category': stored_category},
            'rederived': {'targets': targets, 'category': category},
        })
    return {'classification_engine_version': CLASSIFICATION_ENGINE_VERSION,
            'policy': 'Offline comparison only. Retained records keep their stored labels; adding the protocol target to any of them is a separate reviewed change.',
            'compared_automatic_records': compared, 'skipped_cross_referenced_records': skipped,
            'changes': counts, 'differing_records': len(rows), 'records': rows}


def duplicate_readme_report(document, scope):
    """Group successful scans by README SHA-256 and propose scope reviews only for same-named copies."""
    resources = document['resources']
    groups = {}
    for record in resources:
        groups.setdefault(record['readme_sha256'], []).append(record)
    rows, proposals = [], 0
    for digest, members in groups.items():
        if len(members) < 2:
            continue
        members = sorted(members, key=lambda record: int(record['id'][5:]))
        by_name = {}
        for record in members:
            by_name.setdefault(record['full_name'].split('/', 1)[1].casefold(), []).append(record)
        copies = []
        for same_name in by_name.values():
            # The lowest repository ID is the earliest created; stars never choose the related record.
            related = same_name[0]
            for record in same_name[1:]:
                existing = scope.get(record['id'])
                proposal = None
                if existing is None:
                    proposals += 1
                    proposal = {
                        'decision': 'exclude', 'reason_code': DUPLICATE_README_REASON,
                        'reason_en': (f"The README is byte-identical to the scan of the earlier same-named repository {related['id']} "
                                      f"({related['full_name']}); it does not show what this copy contains."),
                        'reason_zh': (f"其 README 与更早创建的同名仓库 {related['id']}（{related['full_name']}）的扫描结果逐字节相同，"
                                      '无法说明此副本本身的内容。'),
                        'readme_sha256': record['readme_sha256'], 'evidence_url': record['readme_url'],
                        'reviewed_at': None,
                    }
                copies.append({'id': record['id'], 'full_name': record['full_name'],
                               'related_source_id': related['id'], 'related_full_name': related['full_name'],
                               'existing_reason_code': existing.get('reason_code') if existing else None,
                               'proposed_scope_decision': proposal})
        rows.append({
            'readme_sha256': digest, 'readme_bytes': members[0]['readme_bytes'],
            'shared_repository_names': sorted(name for name, same in by_name.items() if len(same) > 1),
            'records': [{'id': record['id'], 'full_name': record['full_name'], 'repository_id': int(record['id'][5:]),
                         'stars': record.get('stars'), 'pushed_at': record.get('pushed_at'),
                         'observed_at': record.get('observed_at'), 'readme_url': record['readme_url'],
                         'scope_status': 'excluded' if record['id'] in scope else 'browsable',
                         'scope_reason_code': scope.get(record['id'], {}).get('reason_code')} for record in members],
            'copy_reviews': copies,
        })
    rows.sort(key=lambda row: row['records'][0]['repository_id'])
    return {
        'policy': ('Offline grouping of successful scans by README SHA-256; nothing is rewritten or excluded. Only repositories that also share '
                   'a repository name receive a proposed scope review, citing the same-named record with the lowest GitHub repository ID, '
                   'which increases with creation time. Stars, push times and README size are recorded for the reviewer but select nothing. '
                   'A proposal keeps reviewed_at null until a reviewer confirms the copy; validation rejects it until then.'),
        'successful_readme_scans': len(resources),
        'distinct_repository_ids': len({record['id'] for record in resources}),
        'distinct_readme_sha256': len(groups),
        'identical_readme_groups': len(rows), 'proposed_scope_reviews': proposals, 'groups': rows,
    }


def readme_record(repo, metadata, content, *, api_url=None):
    """Extract shared document evidence from actual bytes; never retain README text."""
    if not content:
        raise ScanError('empty-readme')
    if len(content) > MAX_README_BYTES:
        raise ScanError('readme-too-large')
    if type(metadata.get('size')) is not int or metadata['size'] != len(content):
        raise ScanError('readme-size-mismatch')
    content_git_sha = hashlib.sha1(b'blob ' + str(len(content)).encode('ascii') + b'\0' + content).hexdigest()
    if not re.fullmatch('[0-9a-f]{40}', str(metadata.get('sha', ''))) or metadata['sha'] != content_git_sha:
        raise ScanError('readme-git-sha-mismatch')
    try:
        text = content.decode('utf-8')
    except UnicodeDecodeError:
        raise ScanError('non-utf8-readme') from None
    if '\x00' in text or text.count('\ufffd') > max(20, len(text) // 50):
        raise ScanError('nontext-readme')
    # These are automatic document features, not endorsements or compatibility claims.
    headings = []
    for match in re.finditer(r'^#{1,6}\s+(.+?)\s*#*\s*$', text, re.MULTILINE):
        title = re.sub(r'\s+', ' ', match[1]).strip()[:80]
        if title and title not in headings:
            headings.append(title)
        if len(headings) == 6:
            break
    signals = []
    for label, pattern in [
        ('installation', r'(?im)^#{1,6}\s*.*(?:install|setup|getting.started|安装)'),
        ('usage', r'(?im)^#{1,6}\s*.*(?:usage|quick.start|how.to|使用|用法)'),
        ('requirements', r'(?im)^#{1,6}\s*.*(?:requirements|prerequisites|dependenc|依赖|环境要求)'),
        ('examples', r'(?im)^#{1,6}\s*.*(?:examples|demo|tutorial|示例|教程)'),
        ('license-section', r'(?im)^#{1,6}\s*.*(?:licen[sc]e|copyright|许可)'),
    ]:
        if re.search(pattern, text):
            signals.append(label)
    try:
        description_fields = capture_description(repo.get('description'))
    except ValueError:
        raise ScanError('invalid-repository-description') from None
    # Labels use only the published description, never text omitted from the record.
    targets, category = classify({**repo, 'description': description_fields['description_en']})
    record = {
        'id': 'scan-' + str(repo['id']),
        'name': repo['full_name'],
        'full_name': repo['full_name'],
        'url': repo['html_url'],
        **description_fields,
        'description_language': 'upstream-original',
        'description_zh_status': 'not-translated',
        'description_origin': 'github-repository-description',
        'topics': repo.get('topics', []),
        'stars': repo.get('stargazers_count', 0),
        'license': (repo.get('license') or {}).get('spdx_id'),
        'archived': repo.get('archived', False),
        'updated_at': repo.get('updated_at'),
        'pushed_at': repo.get('pushed_at'),
        'metadata_observed_at': repo['_metadata_observed_at'],
        'observed_at': now(),
        'readme_url': metadata.get('html_url') or repo['html_url'] + '#readme',
        'readme_path': metadata.get('path'),
        'readme_git_sha': metadata.get('sha'),
        'readme_content_git_sha': content_git_sha,
        'readme_sha256': hashlib.sha256(content).hexdigest(),
        'readme_bytes': len(content),
        'readme_lines': len(text.splitlines()),
        'readme_heading_count': len(headings),
        'readme_signals': signals,
        'scan_status': 'readme-scanned',
        'verification': 'automated-readme-scan',
        'requirements': 'See upstream requirements; not manually reviewed.',
        'targets': targets,
        'category': category,
        'classification_origin': 'automatic-metadata',
        'classification_reference_ids': [],
        'classification_engine_version': CLASSIFICATION_ENGINE_VERSION,
        'matched_queries': repo['_matched_queries'],
        'discovery_methods': repo.get('_discovery_methods', ['github-search']),
    }
    record['readme_git_sha_matches_content'] = record['readme_git_sha'] == record['readme_content_git_sha']
    if repo.get('_seed_reference_ids'):
        record['seed_reference_ids'] = repo['_seed_reference_ids']
    if repo.get('_seed_paper_ids'):
        record['seed_paper_ids'] = repo['_seed_paper_ids']
        record['seed_paper_references'] = repo['_seed_paper_references']
    if api_url is not None:
        record['readme_api_url'] = api_url
    return record


def scan_readme(api, repo):
    path = '/repos/' + repo['full_name'] + '/readme'
    ref = repo.get('default_branch')
    if ref:
        path += '?' + urlencode({'ref': ref})
    try:
        # Queued REST metadata may be old. Confirm the numeric identity and
        # current public status before fetching any document bytes.
        try:
            current = api.json('/repositories/' + str(repo['id']))
        except ScanError as error:
            if error.status in (404, 410):
                raise ScanError('readme-repository-unavailable', error.status) from None
            raise
        if (not isinstance(current, dict) or type(current.get('id')) is not int or current.get('id') != repo['id']
                or current.get('full_name') != repo['full_name']
                or current.get('html_url') != repo['html_url'] or repository_ineligibility(current)):
            raise ScanError('readme-repository-identity-unconfirmed')
        metadata = api.json(path)
        if not isinstance(metadata, dict) or metadata.get('type') != 'file':
            raise ScanError('not-a-readme-file')
        size, oid = metadata.get('size'), metadata.get('sha')
        if type(size) is not int or size < 0 or not isinstance(oid, str) or not re.fullmatch('[0-9a-f]{40}', oid):
            raise ScanError('invalid-readme-metadata')
        if size > MAX_README_BYTES:
            raise ScanError('readme-too-large')
        readme_path = metadata.get('path')
        if (not isinstance(readme_path, str) or not readme_path or '\\' in readme_path
                or any(part in ('', '.', '..') for part in readme_path.split('/'))
                or any(ord(char) < 32 for char in readme_path)):
            raise ScanError('invalid-readme-path')
        url = metadata.get('html_url')
        parsed = urlsplit(url) if isinstance(url, str) else None
        if (parsed is None or not url.startswith(repo['html_url'] + '/blob/')
                or any(ord(char) < 32 for char in url) or parsed.query or parsed.fragment
                or not unquote(parsed.path).endswith('/' + readme_path)
                or any(part in ('.', '..') for part in unquote(parsed.path).split('/'))):
            raise ScanError('invalid-readme-url')
        content = None
        if metadata.get('encoding') == 'base64' and isinstance(metadata.get('content'), str):
            try:
                content = base64.b64decode(re.sub(r'\s', '', metadata['content']), validate=True)
            except ValueError:
                raise ScanError('invalid-readme-encoding') from None
        elif metadata.get('encoding') != 'none':
            raise ScanError('invalid-readme-encoding')
        blob_path = None
        if (content is None or len(content) != size
                or hashlib.sha1(b'blob ' + str(len(content)).encode('ascii') + b'\0' + content).hexdigest() != oid):
            # The README endpoint can truncate or transcode its inline body.
            # Read the immutable advertised blob once. API failures propagate;
            # never escape backpressure by
            # requesting another representation or a third-party download URL.
            blob_path = '/repos/' + repo['full_name'] + '/git/blobs/' + oid
            blob = api.json(blob_path)
            if (not isinstance(blob, dict) or blob.get('sha') != oid or type(blob.get('size')) is not int
                    or not 0 <= blob['size'] <= MAX_README_BYTES or blob.get('encoding') != 'base64'
                    or not isinstance(blob.get('content'), str)):
                raise ScanError('invalid-readme-blob')
            try:
                content = base64.b64decode(re.sub(r'\s', '', blob['content']), validate=True)
            except ValueError:
                raise ScanError('invalid-readme-encoding') from None
            metadata = {**metadata, 'size': blob['size']}
        record = readme_record(repo, metadata, content, api_url='https://api.github.com' + path)
        if blob_path is not None:
            record['readme_blob_api_url'] = 'https://api.github.com' + blob_path
        return record, None
    except ScanError as error:
        return None, {
            'id': 'scan-' + str(repo['id']), 'full_name': repo['full_name'],
            'url': repo['html_url'], 'observed_at': now(),
            'scan_status': 'failed', 'reason': error.reason,
            'http_status': error.status,
        }


def save(output, meta, records, failures, complete=False):
    # Only these two mappings change below. Retained observations and records
    # stay shared while the single writer serializes the checkpoint.
    meta = {**meta, 'current_run': dict(meta['current_run'])}
    checkpoint = now()
    attempted = len(records) + len(failures)
    known_ids = meta.get('discovered_repository_ids', [])
    attempted_ids = [record['id'] for record in records + failures]
    if (len(known_ids) != len(set(known_ids)) or len(set(attempted_ids)) != attempted
            or not set(attempted_ids).issubset(known_ids)):
        raise ValueError('Inconsistent repository discovery accounting')
    meta.update({
        'unique_repos': len(known_ids),
        'attempted_readme_scans': attempted,
        'successful_readme_scans': len(records),
        'failed': len(failures),
        'unattempted_candidates': len(known_ids) - attempted,
        'target_reached': len(records) >= meta['requested_successful_scans'],
        'completed_at': checkpoint if complete else None,
        'last_checkpoint_at': checkpoint,
        'status': 'complete' if complete else 'in-progress',
    })
    run = meta['current_run']
    run.update({
        'completed_at': checkpoint if complete else None,
        'status': meta['status'],
        'query_count': len(meta['queries']) - run['query_start_index'],
        'seed_observation_count': len(meta.get('seed_observations', [])) - run['seed_observation_start_index'],
        'resume_observation_count': len(meta.get('resume_observations', [])) - run['resume_observation_start_index'],
        'new_successful_readme_scans': len(records) - run['retained_successful_readme_scans'],
        'new_failed_readme_scans': len(failures) - run['retained_failed_readme_scans'],
    })
    document = {'meta': meta, 'resources': records, 'failures': failures}
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + '.tmp')
    with temporary.open('w', encoding='utf-8') as stream:
        # Avoid a second, potentially hundreds-of-megabytes Unicode document.
        json.dump(document, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    temporary.replace(output)


def load_resume(path):
    """Validate retained evidence before any authentication or network access."""
    raw = path.read_bytes()
    try:
        document = strict_json.loads(raw)
    except ValueError as error:
        raise ValueError(f'{path}: {error}') from error
    if not isinstance(document, dict):
        raise ValueError('Resume snapshot must be an object')
    meta, records, failures = document.get('meta'), document.get('resources'), document.get('failures', [])
    if not isinstance(meta, dict) or not isinstance(records, list) or not isinstance(failures, list):
        raise ValueError('Resume snapshot requires meta, resources, and failures')
    if not isinstance(meta.get('queries'), list):
        raise ValueError('Resume snapshot must retain its query observations')
    identifiers, names = set(), set()
    for entries, status in ((records, 'readme-scanned'), (failures, 'failed')):
        for record in entries:
            if not isinstance(record, dict) or record.get('scan_status') != status:
                raise ValueError('Invalid retained scan status')
            identifier, name = record.get('id'), record.get('full_name')
            if not isinstance(identifier, str) or not re.fullmatch(r'scan-[0-9]+', identifier):
                raise ValueError('Resume snapshot contains an invalid repository ID')
            if identifier in identifiers or not isinstance(name, str) or not name or name.casefold() in names:
                raise ValueError('Resume snapshot contains duplicate or missing repository identities')
            identifiers.add(identifier)
            names.add(name.casefold())
    if (meta.get('successful_readme_scans') != len(records) or meta.get('failed') != len(failures)
            or meta.get('attempted_readme_scans') != len(identifiers)):
        raise ValueError('Resume snapshot scan counts do not match retained evidence')
    known = meta.get('discovered_repository_ids')
    if known is not None:
        if (not isinstance(known, list) or any(not isinstance(value, str) or not re.fullmatch(r'scan-[0-9]+', value) for value in known)
                or len(set(known)) != len(known) or not identifiers.issubset(known)
                or meta.get('unique_repos') != len(known)
                or meta.get('unattempted_candidates') != len(known) - len(identifiers)):
            raise ValueError('Resume snapshot discovery ID ledger is inconsistent')
    elif (not isinstance(meta.get('unique_repos'), int) or meta['unique_repos'] < len(identifiers)
          or meta.get('unattempted_candidates') != meta['unique_repos'] - len(identifiers)):
        raise ValueError('Legacy resume snapshot candidate counts are inconsistent')
    return document, hashlib.sha256(raw).hexdigest()


def initial_meta(args, started):
    return {
        'schema_version': 1,
        'classification_engine_version': CLASSIFICATION_ENGINE_VERSION,
        'started_at': started,
        'completed_at': None,
        'requested_successful_scans': args.target,
        'queries': [],
        'method': 'Public, non-fork, non-archived GitHub repository discovery through search, retained unattempted repository-ID lookups on resume, and optional curated-resource or bibliography-artifact metadata lookups, followed by an actual authenticated GET of each repository README. README bytes are decoded, analyzed for document features, SHA-256 hashed and discarded.',
        'description_policy': SOURCE_DESCRIPTION_POLICY,
        'readme_heading_count_policy': 'Count of distinct heading-like lines encountered, capped at six; a count of six means at least six. Heading text is not retained.',
        'classification_policy': CLASSIFICATION_POLICY,
        'limits': {
            'workers': args.workers, 'requests_per_second': args.requests_per_second,
            'search_interval_seconds': 2.1, 'max_readme_bytes': MAX_README_BYTES,
            'max_pages_per_query': args.max_pages, 'per_page': 100,
        },
        'limitations': [
            'Automated README scanning is distinct from the curated source-reviewed catalog.',
            'No repository code, binaries, installers, tests or linked commands are executed.',
            'Search membership and README availability do not establish quality, safety, licensing permission, REA compatibility, or successful operation.',
            'Stars, topics, license identifiers and timestamps come from GitHub repository metadata and are snapshots.',
            'Upstream repository descriptions are attributed source text, not original editorial summaries. README text is not retained.',
            'Repositories without a readable nonempty README, oversized README files and failed requests do not count as successful sources.',
            'Search results are relevance-limited by queries, sorted by stars within each query, and capped by GitHub pagination; this is not an exhaustive census.',
            'README URLs can change after collection; content hashes and Git blob identifiers record the observed bytes.',
        ],
    }


def held_repository_ids(values):
    """Administrative IDs are explicit inputs, never fabricated scan outcomes."""
    if (not isinstance(values, (list, tuple)) or len(values) > 1000
            or any(not isinstance(value, str) or not re.fullmatch(r'[1-9][0-9]*', value) for value in values)):
        raise ValueError('Held repository IDs must be at most 1000 canonical positive decimal strings')
    return frozenset('scan-' + value for value in values)


def run_scan(api, args, resumed=None, resume_sha256=None, *, readme_transport=None, frontier=None,
             diagnostics=None):
    """Extend evidence without refreshing or retrying any retained repository."""
    held_ids = held_repository_ids(getattr(args, 'hold_repository_ids', []))
    if diagnostics is not None and readme_transport is None:
        raise ValueError('Transport diagnostics require the GraphQL README transport')
    frontier_api = None
    if frontier is not None:
        if readme_transport is None:
            raise ValueError('Partitioned discovery requires the identity-checking README transport')
        import search_frontier as frontier_api
        frontier_state, frontier_path, frontier_queries = frontier
        if frontier_path.resolve() == args.output.resolve():
            raise ValueError('Frontier and scan output must use different paths')
    started = now()
    if diagnostics is not None:
        diagnostics.start(started)
    fresh_meta = initial_meta(args, started)
    if readme_transport is not None:
        fresh_meta['method'] = ('Public, non-fork, non-archived GitHub discovery followed by actual README blob reads '
            'through GraphQL at a pinned commit, with repository-ID, UTF-8 byte size and Git blob SHA verification. '
            'Unsupported or ambiguous documents use the repository README REST endpoint. Rate-limited requests stay '
            'pending. Content is analyzed for document features, SHA-256 hashed and discarded.')
    records = list(resumed['resources']) if resumed else []
    failures = list(resumed.get('failures', [])) if resumed else []
    retained_successes, retained_failures = len(records), len(failures)
    attempted_ids = {record['id'] for record in records + failures}
    pending_delivery_blocked = False
    if frontier_api is not None:
        acknowledged = {'scan-' + key for key, item in frontier_state['candidates'].items()
                        if item['checkpoint_sha256'] is not None}
        if not acknowledged <= attempted_ids:
            raise ValueError('Discovery frontier acknowledges repositories absent from this scan checkpoint')
        pending_delivery_blocked |= any(item['checkpoint_sha256'] is None
                                        and item['next_attempt_at'] > frontier_api.current_seconds()
                                        for item in frontier_state['candidates'].values())
    retained_names = {record['full_name'].casefold() for record in records + failures}
    meta = copy.deepcopy(resumed['meta']) if resumed else fresh_meta
    known_ids = set(meta.get('discovered_repository_ids', attempted_ids))
    pending_delivery_blocked |= bool((held_ids & known_ids) - attempted_ids)
    if resumed:
        prior = {key: copy.deepcopy(meta.get(key)) for key in (
            'started_at', 'completed_at', 'last_checkpoint_at', 'status',
            'requested_successful_scans', 'unique_repos', 'attempted_readme_scans',
            'successful_readme_scans', 'failed', 'unattempted_candidates', 'limits', 'method', 'description_policy',
            'classification_engine_version', 'classification_policy',
        )}
        prior.update({'source_sha256': resume_sha256, 'query_count': len(meta['queries']),
                      'candidate_ids_retained': 'discovered_repository_ids' in meta,
                      'known_repository_ids': len(known_ids)})
        if 'current_run' in meta:
            prior['run'] = copy.deepcopy(meta['current_run'])
        meta.setdefault('resume_history', []).append(prior)
        meta['requested_successful_scans'] = args.target
        meta['limits'] = fresh_meta['limits']
    meta['method'] = fresh_meta['method']
    meta['description_policy'] = fresh_meta['description_policy']
    meta['classification_engine_version'] = fresh_meta['classification_engine_version']
    meta['classification_policy'] = fresh_meta['classification_policy']
    meta['unique_repos_policy'] = ('Distinct persisted repository IDs from retained attempts and discovery observations. '
                                   'Administrative hold configuration alone does not establish a discovered identity. '
                                   'Historical count-only unattempted candidates are not added to this union unless rediscovered; '
                                   'their original counts remain in resume_history.')
    meta['current_run'] = {
        'run_id': started, 'started_at': started, 'completed_at': None,
        'mode': 'resume' if resumed else 'fresh', 'query_start_index': len(meta['queries']),
        'retained_successful_readme_scans': retained_successes,
        'retained_failed_readme_scans': retained_failures,
        'requested_new_successful_scans': max(0, args.target - retained_successes),
        'readme_queue_candidates': 0, 'seed_curated': args.seed_curated,
        'seed_papers': args.seed_papers,
        'classification_engine_version': CLASSIFICATION_ENGINE_VERSION,
        'retained_unattempted_repository_ids': len(known_ids - attempted_ids),
        'query_plan': list(args.queries),
        'held_repository_ids': sorted(held_ids, key=lambda value: int(value[5:])),
    }
    candidates, candidate_names, exhausted = {}, set(), set()
    meta.setdefault('seed_observations', [])
    meta['current_run']['seed_observation_start_index'] = len(meta['seed_observations'])
    meta.setdefault('resume_observations', [])
    meta['current_run']['resume_observation_start_index'] = len(meta['resume_observations'])
    meta['resume_observation_policy'] = ('Metadata-only lookups of retained unattempted repository IDs. '
                                         'Failed or ineligible lookups remain in the discovery ledger, '
                                         'do not count as README attempts, and expose no private repository metadata.')
    candidate_goal = max(0, args.target - retained_successes) + args.candidate_buffer

    def checkpoint(complete=False):
        meta['discovered_repository_ids'] = sorted(known_ids, key=lambda value: int(value[5:]))
        meta['current_run']['readme_queue_candidates'] = len(candidates)
        save(args.output, meta, records, failures, complete)
        if frontier_api is not None:
            durable = [int(identifier[5:]) for identifier in attempted_ids
                       if identifier[5:] in frontier_state['candidates']
                       and frontier_state['candidates'][identifier[5:]]['checkpoint_sha256'] is None]
            if durable:
                frontier_api.acknowledge_candidates(frontier_state, durable,
                    checkpoint_sha256=hashlib.sha256(args.output.read_bytes()).hexdigest())
            frontier_api.save_frontier(frontier_path, frontier_state, approved_queries=frontier_queries)

    def sync_frontier_observations():
        existing = {(event.get('query'), event.get('page'), event.get('observed_at'), event.get('status'))
                    for event in meta['queries']}
        partitions = {item['id']: item for item in frontier_state['partitions']}
        for event in frontier_state['observations']:
            query = frontier_api.request_for(frontier_state, partitions[event['partition_id']])['query']
            key = (query, event['page'], event['observed_at'], event['status'])
            if key in existing:
                continue
            entry = {'query': query, 'page': event['page'], 'per_page': 100,
                     'observed_at': event['observed_at'], 'run_id': event.get('run_id', event['observed_at']), 'status': event['status']}
            if event['status'] == 'ok':
                entry.update({field: event[field] for field in ('total_count', 'returned', 'incomplete_results')})
            else:
                entry.update(reason=event['reason'], http_status=None)
            meta['queries'].append(entry)
            existing.add(key)

    def delivery_block(identifier):
        nonlocal pending_delivery_blocked
        if identifier in held_ids:
            pending_delivery_blocked = True
            return 'held'
        if frontier_api is not None:
            entry = frontier_state['candidates'].get(identifier[5:])
            if entry is not None and entry['next_attempt_at'] > frontier_api.current_seconds():
                pending_delivery_blocked = True
                return 'frontier-deferred'
        return None

    def add_candidate(repo, observed_at, query=None, seed_ids=None, paper=None, resumed_id=None):
        if repository_ineligibility(repo):
            return 'ineligible'
        if (type(repo.get('id')) is not int or repo['id'] <= 0
                or not isinstance(repo.get('full_name'), str)
                or not re.fullmatch(r'[A-Za-z0-9-]+/[A-Za-z0-9_.-]+', repo['full_name'])
                or repo.get('html_url') != 'https://github.com/' + repo['full_name']):
            raise ScanError('invalid-repository-metadata')
        identifier = 'scan-' + str(repo['id'])
        if resumed_id is not None and identifier != resumed_id:
            raise ScanError('repository-id-mismatch')
        known_ids.add(identifier)
        if identifier in attempted_ids:
            return 'retained-attempt'
        blocked = delivery_block(identifier)
        if blocked:
            return blocked
        if identifier not in candidates:
            name = repo['full_name'].casefold()
            if name in retained_names or name in candidate_names:
                return 'name-collision'
            candidate = dict(repo)
            candidate.update({'_metadata_observed_at': observed_at, '_matched_queries': [], '_discovery_methods': []})
            candidates[identifier] = candidate
            candidate_names.add(name)
        candidate = candidates[identifier]
        if query is not None:
            if query not in candidate['_matched_queries']:
                candidate['_matched_queries'].append(query)
            if 'github-search' not in candidate['_discovery_methods']:
                candidate['_discovery_methods'].append('github-search')
        if seed_ids is not None:
            references = candidate.setdefault('_seed_reference_ids', [])
            references.extend(value for value in seed_ids if value not in references)
            if 'curated-reference' not in candidate['_discovery_methods']:
                candidate['_discovery_methods'].append('curated-reference')
        if paper is not None:
            references = candidate.setdefault('_seed_paper_ids', [])
            references.extend(value for value in paper['ids'] if value not in references)
            artifacts = candidate.setdefault('_seed_paper_references', [])
            artifacts.extend(value for value in paper['artifacts'] if value not in artifacts)
            if 'paper-artifact-reference' not in candidate['_discovery_methods']:
                candidate['_discovery_methods'].append('paper-artifact-reference')
        if resumed_id is not None and 'retained-repository-id' not in candidate['_discovery_methods']:
            candidate['_discovery_methods'].append('retained-repository-id')
        return 'candidate'

    if frontier_api is not None:
        # Recover historical query evidence saved before a crash, without claiming a new request.
        sync_frontier_observations()
        meta['current_run']['query_start_index'] = len(meta['queries'])
    print(f'START target={args.target} retained_success={retained_successes} retained_failed={retained_failures}', flush=True)
    checkpoint()
    if frontier_api is not None:
        known_ids.update('scan-' + key for key in frontier_state['candidates'])
        # Freeze eligibility until all pages are loaded; no ACK or deferral mutates
        # the queue before the checkpoint below.
        pending_now, pending_offset = frontier_api.current_seconds(), 0
        while len(candidates) < candidate_goal:
            page_limit = min(1000, candidate_goal - len(candidates))
            pending_page = frontier_api.pending_candidates(
                frontier_state, limit=page_limit, offset=pending_offset, now=pending_now)
            if not pending_page:
                break
            pending_offset += len(pending_page)
            for pending in pending_page:
                public = {'id': pending['id'], 'node_id': pending.get('node_id'), 'full_name': pending['full_name'],
                          'html_url': 'https://github.com/' + pending['full_name'],
                          'private': False, 'fork': False, 'archived': False, 'visibility': 'public'}
                for query in pending['_matched_queries']:
                    add_candidate(public, pending['observed_at'], query=query)
            if len(pending_page) < page_limit:
                break
        checkpoint()
    if resumed:
        pending_legacy = known_ids - attempted_ids - set(candidates) - held_ids
        if frontier_api is not None:
            pending_legacy -= {'scan-' + key for key in frontier_state['candidates']}
        last_lookup = {entry['repository_id']: entry['observed_at'] for entry in meta['resume_observations']
                       if entry.get('repository_id') in pending_legacy and entry.get('observed_at')}
        ordered_pending = sorted(pending_legacy, key=lambda value: (last_lookup.get(value, ''), int(value[5:])))
        # Bound metadata work and rotate stale identities instead of starving README reads.
        for identifier in ordered_pending[:getattr(args, 'pending_metadata_budget', 200)]:
            if len(candidates) >= candidate_goal:
                break
            entry = {'repository_id': identifier, 'observed_at': now(), 'run_id': started,
                     'method': 'retained-repository-id'}
            try:
                repo = api.json('/repositories/' + identifier[5:])
                entry['status'] = add_candidate(repo, entry['observed_at'], resumed_id=identifier)
                if entry['status'] == 'ineligible':
                    entry['reason'] = repository_ineligibility(repo)
            except ScanError as error:
                entry.update({'status': 'failed', 'reason': error.reason, 'http_status': error.status})
            meta['resume_observations'].append(entry)
            if (len(meta['resume_observations']) - meta['current_run']['resume_observation_start_index']) % 25 == 0:
                checkpoint()
        print(f'RESUME_METADATA_COMPLETE observations={len(meta["resume_observations"]) - meta["current_run"]["resume_observation_start_index"]} new_readme_candidates={len(candidates)}', flush=True)
        checkpoint()
    seed_groups = []
    if args.seed_curated:
        seed_groups.append(('curated-repository-reference', curated_references()))
    if args.seed_papers:
        seed_groups.append(('paper-artifact-reference', paper_references()))
    for method, references in seed_groups:
        for name, reference in sorted(references.items()):
            if name in retained_names:
                continue
            entry = {'full_name': name, 'observed_at': now(), 'run_id': started,
                     'method': method, 'reference_ids': list(reference['ids'])}
            paper = reference if method == 'paper-artifact-reference' else None
            if paper is not None:
                entry['artifact_references'] = copy.deepcopy(paper['artifacts'])
            try:
                repo = api.json('/repos/' + quote(name, safe='/'))
                entry['status'] = add_candidate(repo, entry['observed_at'],
                                                seed_ids=reference['ids'] if paper is None else None, paper=paper)
                if entry['status'] != 'ineligible':
                    entry['repository_id'] = 'scan-' + str(repo['id'])
                else:
                    entry['reason'] = repository_ineligibility(repo)
            except ScanError as error:
                entry.update({'status': 'failed', 'reason': error.reason, 'http_status': error.status})
            meta['seed_observations'].append(entry)
        print(f'SEEDS_COMPLETE observations={len(meta["seed_observations"]) - meta["current_run"]["seed_observation_start_index"]} new_readme_candidates={len(candidates)}', flush=True)
        checkpoint()
    def discovery_requests():
        if frontier_api is not None:
            for _ in range(getattr(args, 'search_request_budget', 120)):
                request = frontier_api.next_request(frontier_state)
                if request is None:
                    break
                yield request['query'], request['page'], request
        else:
            for page in range(1, args.max_pages + 1):
                for query in args.queries:
                    if query not in exhausted:
                        yield query, page, None

    for query, page, request in discovery_requests():
        if len(candidates) >= candidate_goal:
            break
        entry = {'query': query, 'page': page, 'per_page': 100, 'observed_at': now(), 'run_id': started}
        params = urlencode({'q': query, 'per_page': 100, 'page': page, 'sort': 'stars', 'order': 'desc'})
        try:
            result = api.json(request['path'] if request is not None else '/search/repositories?' + params, search=True)
            if frontier_api is not None:
                frontier_api.record_response(frontier_state, request, result,
                    known_ids=[int(identifier[5:]) for identifier in attempted_ids], run_id=started)
                frontier_api.save_frontier(frontier_path, frontier_state, approved_queries=frontier_queries)
            if (not isinstance(result, dict) or not isinstance(result.get('items'), list)
                    or type(result.get('total_count')) is not int or result['total_count'] < 0):
                raise ScanError('invalid-search-response')
            items = result.get('items', [])
            entry.update({'status': 'ok', 'total_count': result.get('total_count'),
                          'returned': len(items), 'incomplete_results': result.get('incomplete_results', False)})
            skipped_attempted, skipped_names, skipped_held, skipped_deferred = 0, 0, 0, 0
            invalid_reasons = {}
            for repo in items:
                try:
                    outcome = add_candidate(repo, entry['observed_at'], query=query)
                except ScanError as error:
                    # A bad item does not erase the successfully observed search response
                    # or the provenance of valid items already accepted from that response.
                    invalid_reasons[error.reason] = invalid_reasons.get(error.reason, 0) + 1
                    continue
                skipped_attempted += outcome == 'retained-attempt'
                skipped_names += outcome == 'name-collision'
                skipped_held += outcome == 'held'
                skipped_deferred += outcome == 'frontier-deferred'
            entry.update({'retained_attempts_skipped': skipped_attempted, 'name_collisions_skipped': skipped_names,
                          'held_candidates_skipped': skipped_held, 'deferred_candidates_skipped': skipped_deferred})
            if invalid_reasons:
                entry.update({'invalid_items_skipped': sum(invalid_reasons.values()),
                              'invalid_item_reasons': invalid_reasons})
            if len(items) < 100 or page * 100 >= min(result.get('total_count', 0), 1000):
                exhausted.add(query)
        except ScanError as error:
            if frontier_api is not None:
                frontier_api.record_failure(frontier_state, request, reason=error.reason, run_id=started)
                frontier_api.save_frontier(frontier_path, frontier_state, approved_queries=frontier_queries)
            entry.update({'status': 'failed', 'reason': error.reason, 'http_status': error.status})
        if frontier_api is not None:
            entry['observed_at'] = frontier_state['observations'][-1]['observed_at']
        meta['queries'].append(entry)
        new_queries = len(meta['queries']) - meta['current_run']['query_start_index']
        print(f'DISCOVERY new_queries={new_queries} new_readme_candidates={len(candidates)} known_repositories={len(known_ids)} page={page}', flush=True)
        if new_queries % 5 == 0:
            checkpoint()
        if len(candidates) >= candidate_goal:
            break
    print(f'DISCOVERY_COMPLETE known_repositories={len(known_ids)} new_readme_candidates={len(candidates)}; starting actual README reads', flush=True)
    checkpoint()
    deferred = False
    def delivery_candidates():
        for candidate in candidates.values():
            if not delivery_block('scan-' + str(candidate['id'])):
                yield candidate

    if readme_transport is not None:
        # GraphQL responses contain ephemeral bytes. Only document features and
        # verified identifiers enter the retained source snapshot.
        source = iter(delivery_candidates())
        transport_counts = {'ok': 0, 'fallback': 0, 'rejected': 0, 'retry': 0, 'deferred': 0}
        meta['current_run']['readme_transport'] = {
            'method': 'github-graphql-verified-blob-with-rest-fallback',
            'batch_size': readme_transport.batch_size, 'outcomes': transport_counts,
            'request_count': 0, 'response_bytes': 0, 'reported_query_cost': 0,
            'queries_with_cost': 0, 'queries_without_cost': 0, 'elapsed_seconds': 0.0, 'last_rate_limit': {}}
        checkpoint_attempts = len(attempted_ids)
        while len(records) < args.target:
            batch = []
            for _ in range(min(readme_transport.batch_size, args.target - len(records))):
                item = next(source, None)
                if item is not None:
                    batch.append(item)
            if not batch:
                break
            batch_clock = time.monotonic()
            results = readme_transport.fetch_batch(batch)
            batch_seconds = time.monotonic() - batch_clock
            if diagnostics is not None:
                diagnostics.record_batch(getattr(readme_transport, 'last_batch_diagnostics', []))
            transport_receipt = meta['current_run']['readme_transport']
            receipts = getattr(readme_transport, 'last_batch_receipts', [])
            transport_receipt['elapsed_seconds'] += batch_seconds
            transport_receipt['request_count'] += len(receipts)
            transport_receipt['queries_with_cost'] += sum('cost' in (row.get('rate_limit') or {}) for row in receipts)
            transport_receipt['queries_without_cost'] += sum('cost' not in (row.get('rate_limit') or {}) for row in receipts)
            transport_receipt['response_bytes'] += sum(row.get('response_bytes', 0) for row in receipts)
            transport_receipt['reported_query_cost'] += sum((row.get('rate_limit') or {}).get('cost', 0) for row in receipts)
            transport_receipt['last_rate_limit'] = dict(getattr(readme_transport, 'rate_limit', {}))
            batch_paused = any(results.get(item['id'], {'status': 'retry'}).get('status') in ('retry', 'deferred') for item in batch)
            batch_retry_after = max([60] + [int(value.get('retry_after') or 60) for value in results.values()])
            for candidate in batch:
                result = results.get(candidate['id'], {'status': 'retry'})
                status = result.get('status')
                if status not in transport_counts:
                    raise ValueError('Unexpected README transport outcome')
                transport_counts[status] += 1
                if status in ('retry', 'deferred') or status == 'fallback' and batch_paused:
                    deferred = True
                    if frontier_api is not None and str(candidate['id']) in frontier_state['candidates']:
                        frontier_api.defer_candidates(frontier_state, [candidate['id']], reason='deferred',
                            retry_after_seconds=max(60, min(604800, batch_retry_after)))
                    continue
                if status == 'rejected':
                    if frontier_api is not None and str(candidate['id']) in frontier_state['candidates']:
                        frontier_api.defer_candidates(frontier_state, [candidate['id']], reason='ineligible', retry_after_seconds=86400)
                    continue  # Eligibility is metadata evidence, not a README attempt.
                repo = dict(result['repository'])
                repo.update({key: value for key, value in candidate.items() if key.startswith('_')})
                repo['_metadata_observed_at'] = result['repository']['_metadata_observed_at']
                if (repository_ineligibility(repo) or repo['id'] != candidate['id']
                        or repo['full_name'].casefold() in retained_names):
                    raise ValueError('README transport returned inconsistent repository identity')
                if status == 'fallback':
                    record, failure = scan_readme(api, repo)
                    if failure and failure['reason'] in ('readme-repository-identity-unconfirmed', 'readme-repository-unavailable'):
                        pending_delivery_blocked = True
                        if frontier_api is not None and str(candidate['id']) in frontier_state['candidates']:
                            reason = 'not-found' if failure['reason'] == 'readme-repository-unavailable' else 'ineligible'
                            frontier_api.defer_candidates(frontier_state, [candidate['id']], reason=reason,
                                                          retry_after_seconds=86400)
                        continue  # Only public-identity metadata was requested; no README attempt.
                    if failure and (failure.get('http_status') in (401, 403, 408, 429)
                                    or (failure.get('http_status') or 0) >= 500
                                    or failure['reason'] in ('network-failure', 'retry-limit', 'rate-limited', 'invalid-api-json')):
                        # An exhausted REST retry must not become a permanent
                        # source failure or trigger another sibling fallback.
                        deferred = batch_paused = True
                        if frontier_api is not None and str(candidate['id']) in frontier_state['candidates']:
                            frontier_api.defer_candidates(frontier_state, [candidate['id']], reason='deferred',
                                retry_after_seconds=max(60, min(604800, batch_retry_after)))
                        continue
                else:
                    try:
                        record = readme_record(repo, result['metadata'], result['content'])
                    except ScanError as error:
                        record, failure = None, {
                            'id': 'scan-' + str(repo['id']), 'full_name': repo['full_name'],
                            'url': repo['html_url'], 'observed_at': now(), 'scan_status': 'failed',
                            'reason': error.reason, 'http_status': error.status}
                    else:
                        record['readme_transport'] = 'github-graphql-blob'
                        record['readme_graphql_endpoint'] = 'https://api.github.com/graphql'
                        record['readme_commit_sha'] = result['metadata']['commit_oid']
                        if record['readme_git_sha_matches_content'] is not True:
                            raise ValueError('GraphQL README bytes do not match the immutable blob')
                        failure = None
                observed = record or failure
                if observed['id'] in attempted_ids:
                    raise ValueError('Duplicate repository attempt')
                attempted_ids.add(observed['id'])
                retained_names.add(observed['full_name'].casefold())
                (records if record else failures).append(observed)
            if len(attempted_ids) - checkpoint_attempts >= 100 or deferred:
                checkpoint()
                checkpoint_attempts = len(attempted_ids)
                print(f'README_PROGRESS success={len(records)} failed={len(failures)} transport=graphql', flush=True)
            if deferred:
                break  # Do not evade rate/backpressure by switching transports.
    else:
        source = iter(delivery_candidates())
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            pending = {}
            for _ in range(min(args.workers, max(0, args.target - len(records)))):
                repo = next(source, None)
                if repo is not None:
                    pending[pool.submit(scan_readme, api, repo)] = repo
            while pending:
                completed, _ = wait(pending, return_when=FIRST_COMPLETED)
                for future in completed:
                    repo = pending.pop(future)
                    try:
                        record, failure = future.result()
                    except Exception as error:
                        record, failure = None, {
                            'id': 'scan-' + str(repo['id']), 'full_name': repo['full_name'],
                            'url': repo['html_url'], 'observed_at': now(),
                            'scan_status': 'failed', 'reason': 'worker-' + type(error).__name__,
                            'http_status': None,
                        }
                    metadata_only = failure and failure['reason'] in ('readme-repository-identity-unconfirmed', 'readme-repository-unavailable')
                    if metadata_only:
                        pending_delivery_blocked = True
                    else:
                        result = record or failure
                        if result['id'] in attempted_ids:
                            raise ValueError('Duplicate repository attempt')
                        attempted_ids.add(result['id'])
                        (records if record else failures).append(result)
                        new_attempts = len(records) + len(failures) - retained_successes - retained_failures
                        if new_attempts % 100 == 0:
                            print(f'README_PROGRESS success={len(records)} failed={len(failures)} new_attempts={new_attempts}', flush=True)
                            checkpoint()
                    if len(records) + len(pending) < args.target:
                        following = next(source, None)
                        if following is not None:
                            pending[pool.submit(scan_readme, api, following)] = following
    # Keep the prior snapshot as an unchanged prefix; order only the new evidence.
    records[retained_successes:] = sorted(records[retained_successes:], key=lambda record: (-record['stars'], record['full_name'].casefold()))
    failures[retained_failures:] = sorted(failures[retained_failures:], key=lambda record: record['full_name'].casefold())
    checkpoint(complete=not deferred and not (len(records) < args.target and pending_delivery_blocked))
    reached = len(records) >= args.target
    print(f'COMPLETE successful_readme_scans={len(records)} failed={len(failures)} unique_repos={len(known_ids)} target_reached={reached}', flush=True)
    return 0 if reached else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--transport', choices=('rest', 'graphql'), default='rest')
    parser.add_argument('--graphql-batch-size', type=int, default=8)
    parser.add_argument('--transport-diagnostics', type=Path,
                        help='Optional new .cache JSONL file for bounded failure diagnostics; requires graphql and an existing parent directory')
    parser.add_argument('--frontier', type=Path, help='Ignored cache path for persistent partitioned search; requires graphql')
    parser.add_argument('--search-request-budget', type=int, default=120)
    parser.add_argument('--pending-metadata-budget', type=int, default=200)
    parser.add_argument('--target', type=int, default=1600, help='Combined number of successfully read README sources to seek')
    parser.add_argument('--workers', type=int, default=16)
    parser.add_argument('--requests-per-second', type=float, default=12)
    parser.add_argument('--candidate-buffer', type=int, default=400)
    parser.add_argument('--max-pages', type=int, default=5, help='Pages per query; GitHub permits at most 10')
    parser.add_argument('--resume', type=Path, help='Retain an existing snapshot/checkpoint and resolve its unattempted repository IDs')
    parser.add_argument('--seed-curated', action='store_true', help='Discover missing curated GitHub repositories before search candidates')
    parser.add_argument('--seed-papers', action='store_true', help='Discover GitHub roots from bibliography code_url/project_url fields before search candidates')
    parser.add_argument('--hold-repository-id', action='append', dest='hold_repository_ids', default=[],
                        help='Keep this positive numeric repository ID pending for this run; repeat for more IDs')
    parser.add_argument('--query', action='append', help='Ordered search base; repeat to replace defaults. Public/non-fork/non-archived gates are always added.')
    parser.add_argument('--output', type=Path, help='Output snapshot; defaults to .cache/source-index-next.json when resuming')
    parser.add_argument('--relabel-report', type=Path, help='Offline: print retained automatic labels that differ from this engine, without rewriting the snapshot')
    parser.add_argument('--protocol-report', type=Path, help='Offline: print retained automatic records whose protocol target or category this engine would change')
    parser.add_argument('--duplicate-readme-report', type=Path, help='Offline: group successful scans by README hash and propose scope reviews for same-named copies')
    args = parser.parse_args()
    try:
        held_repository_ids(args.hold_repository_ids)
    except ValueError:
        parser.error('hold-repository-id requires canonical positive numeric IDs (at most 1000 entries)')
    if (args.target < 1 or not 1 <= args.workers <= 32 or not 1 <= args.max_pages <= 10
            or not 0 < args.requests_per_second <= 14 or args.candidate_buffer < 0):
        parser.error('target must be positive, workers 1..32, max-pages 1..10, requests-per-second (0,14], and candidate-buffer nonnegative')
    if not 1 <= args.graphql_batch_size <= 16:
        parser.error('GraphQL batch size must be 1..16')
    if not 1 <= args.search_request_budget <= 1000 or not 0 <= args.pending_metadata_budget <= 1000:
        parser.error('search request budget must be 1..1000; pending metadata budget 0..1000')
    if args.frontier and args.transport != 'graphql':
        parser.error('partitioned discovery requires --transport graphql')
    if args.transport_diagnostics and args.transport != 'graphql':
        parser.error('transport diagnostics require --transport graphql')
    if args.query and any(not value.strip() for value in args.query):
        parser.error('query bases must be nonempty')
    args.queries = [value.strip() + ' is:public fork:false archived:false' for value in args.query] if args.query else QUERIES
    for path, report in ((args.relabel_report, relabel_report), (args.protocol_report, protocol_report),
                         (args.duplicate_readme_report, lambda document: duplicate_readme_report(document, read_scope()))):
        if not path:
            continue
        try:
            document, _ = load_resume(path)
        except (OSError, ValueError, TypeError, KeyError):
            print('Report snapshot could not be read or has inconsistent identities/counts.', flush=True)
            return 2
        print(json.dumps(report(document), ensure_ascii=False, indent=2), flush=True)
        return 0
    args.output = args.output or (ROOT / '.cache/source-index-next.json' if args.resume or args.transport == 'graphql' else DEFAULT_OUTPUT)
    if args.transport_diagnostics:
        from scan_diagnostics import validate_destination
        try:
            validate_destination(args.transport_diagnostics, ROOT / '.cache',
                                 protected_paths=(args.output, args.resume, args.frontier))
        except (OSError, ValueError):
            parser.error('transport diagnostics require a separate new .cache/*.jsonl file with existing, non-symlink parents')
    if args.frontier and (args.frontier.resolve() == args.output.resolve()
                          or args.resume and args.frontier.resolve() == args.resume.resolve()):
        parser.error('frontier, resume input and scan output must use different paths')
    resumed, resume_sha256 = None, None
    if args.resume:
        if args.resume.resolve() == args.output.resolve():
            parser.error('resume input and output must be different paths to preserve the source snapshot')
        try:
            resumed, resume_sha256 = load_resume(args.resume)
        except (OSError, ValueError, TypeError, KeyError):
            print('Resume snapshot could not be read or has inconsistent identities/counts.', flush=True)
            return 2
        if len(resumed['resources']) >= args.target:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(args.resume.read_bytes())
            print(f'ALREADY_COMPLETE successful_readme_scans={len(resumed["resources"])} target={args.target}; snapshot copied without new requests', flush=True)
            return 0
    token_result = subprocess.run(['gh', 'auth', 'token'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    token = token_result.stdout.decode().strip()
    if token_result.returncode or not token:
        print('An existing authenticated gh login is required.', flush=True)
        return 2
    api = GitHub(token, args.requests_per_second)
    transport = None
    if args.transport == 'graphql':
        from scan_graphql_transport import GraphQLReadmeTransport
        transport = GraphQLReadmeTransport(token, batch_size=args.graphql_batch_size, interval=1.0,
                                          capture_diagnostics=args.transport_diagnostics is not None)
    del token, token_result
    diagnostics = None
    if args.transport_diagnostics:
        from scan_diagnostics import DiagnosticSidecar
        try:
            diagnostics = DiagnosticSidecar(args.transport_diagnostics, ROOT / '.cache')
        except (OSError, ValueError):
            print('Transport diagnostic destination could not be created; no scan started.', flush=True)
            return 2
    try:
        frontier = None
        if args.frontier:
            import search_frontier
            approved = [value.strip() for value in args.query] if args.query else QUERY_BASES
            state = (search_frontier.load_frontier(args.frontier, approved_queries=approved) if args.frontier.exists()
                     else search_frontier.new_frontier(until=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                                                      approved_queries=approved))
            search_frontier.save_frontier(args.frontier, state, approved_queries=approved)
            frontier = state, args.frontier, approved
        return run_scan(api, args, resumed, resume_sha256, readme_transport=transport, frontier=frontier,
                        diagnostics=diagnostics)
    finally:
        if diagnostics is not None:
            diagnostics.close()


if __name__ == '__main__':
    raise SystemExit(main())
