#!/usr/bin/env python3
"""Discover public GitHub RE repositories and actually read/hash each accepted README.

Uses only the Python standard library and an existing gh login. Authentication
stays in memory and is sent only to api.github.com. No repository code is run.
"""
from __future__ import annotations

import argparse
import base64
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import subprocess
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


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


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z')


class ScanError(Exception):
    def __init__(self, reason, status=None):
        super().__init__(reason)
        self.reason, self.status = reason, status


class APIOnlyRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        if urlsplit(new_url).scheme != 'https' or urlsplit(new_url).hostname != 'api.github.com':
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
        if not path.startswith('/') or urlsplit(url).hostname != 'api.github.com':
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


def classify(repo):
    topics = {topic.lower() for topic in repo.get('topics', [])}
    text = ' '.join([repo['full_name'], repo.get('description') or '', *topics]).lower()
    targets = set()
    if topics & {'javascript-deobfuscation', 'web-reversing', 'webassembly', 'wasm'} or re.search(r'javascript|electron|browser|webassembly', text):
        targets.add('website')
    if topics & {'game-reversing', 'game-decompilation', 'il2cpp', 'unity-reverse-engineering'} or re.search(r'\bgames?\b|\bunity\b|\bunreal\b|\bplaystation\b|\btouhou\b|\bgamecube\b', text):
        targets.add('game')
    if re.search(r'\bandroid\b|\bapk\b|\bios\b|\belectron\b|\bdotnet\b|\.net\b|\bjava\b|\bjadx\b|\bil2cpp\b|\bmobile\b', text):
        targets.add('app')
    if re.search(r'\bfirmware\b|\bbinwalk\b|\bunblob\b|\buefi\b|\bbios\b', text):
        targets.add('firmware')
    if topics & {'binary-analysis', 'binary-diffing', 'ghidra', 'ida-plugin', 'idapro', 'frida', 'radare2', 'decompiler', 'disassembler', 'memory-forensics'} or re.search(r'\bbinar(?:y|ies)\b|\bdisassembl|\bghidra\b|\bida\b|\bradare2\b|\bx64dbg\b|\belf\b|\bmach-o\b|\bnative\b', text):
        targets.add('binary')
    if 'firmware' in targets:
        category = 'firmware'
    elif 'game' in targets:
        category = 'game-analysis'
    elif re.search(r'\bandroid\b|\bapk\b|\bjadx\b', text):
        category = 'android'
    elif re.search(r'\bdotnet\b|\.net\b|\bcil\b|\bilspy\b|\bdnspy\b', text):
        category = 'managed-code'
    elif re.search(r'protocol-analysis|\bprotocol\b|\bpcap\b|\bwireshark\b', text):
        category = 'protocol-analysis'
    elif 'website' in targets:
        category = 'web-analysis'
    elif topics & {'frida', 'frida-script', 'memory-forensics', 'debugger'} or re.search(r'\bdebugger\b|\binstrumentation\b', text):
        category = 'dynamic-analysis'
    elif 'binary' in targets:
        category = 'native-analysis'
    else:
        category = 'reverse-engineering'
    return sorted(targets), category


def scan_readme(api, repo):
    path = '/repos/' + repo['full_name'] + '/readme'
    ref = repo.get('default_branch')
    if ref:
        path += '?' + urlencode({'ref': ref})
    try:
        metadata = api.json(path)
        if not isinstance(metadata, dict) or metadata.get('type') != 'file':
            raise ScanError('not-a-readme-file')
        if metadata.get('size', 0) > MAX_README_BYTES:
            raise ScanError('readme-too-large')
        if metadata.get('encoding') == 'base64' and isinstance(metadata.get('content'), str):
            try:
                content = base64.b64decode(re.sub(r'\s', '', metadata['content']), validate=True)
            except ValueError:
                raise ScanError('invalid-readme-encoding') from None
        else:
            content = api.get(path, accept='application/vnd.github.raw+json')
        if not content:
            raise ScanError('empty-readme')
        if len(content) > MAX_README_BYTES:
            raise ScanError('readme-too-large')
        text = content.decode('utf-8', errors='replace')
        if text.count('\x00') > 0 or text.count('\ufffd') > max(20, len(text) // 50):
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
        targets, category = classify(repo)
        description = repo.get('description') or ''
        record = {
            'id': 'scan-' + str(repo['id']),
            'name': repo['full_name'],
            'full_name': repo['full_name'],
            'url': repo['html_url'],
            'description_en': description,
            'description_zh': description,
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
            'readme_sha256': hashlib.sha256(content).hexdigest(),
            'readme_bytes': len(content),
            'readme_lines': len(text.splitlines()),
            'readme_heading_count': len(headings),
            'readme_signals': signals,
            'readme_api_url': 'https://api.github.com' + path,
            'scan_status': 'readme-scanned',
            'verification': 'automated-readme-scan',
            'requirements': 'See upstream requirements; not manually reviewed.',
            'targets': targets,
            'category': category,
            'matched_queries': repo['_matched_queries'],
        }
        return record, None
    except ScanError as error:
        return None, {
            'id': 'scan-' + str(repo['id']), 'full_name': repo['full_name'],
            'url': repo['html_url'], 'observed_at': now(),
            'scan_status': 'failed', 'reason': error.reason,
            'http_status': error.status,
        }


def save(output, meta, records, failures, complete=False):
    meta = dict(meta)
    meta.update({
        'successful_readme_scans': len(records),
        'failed': len(failures),
        'completed_at': now() if complete else None,
        'last_checkpoint_at': now(),
        'status': 'complete' if complete else 'in-progress',
    })
    document = {'meta': meta, 'resources': records, 'failures': failures}
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + '.tmp')
    temporary.write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=int, default=1600, help='Number of successfully read README sources to seek')
    parser.add_argument('--workers', type=int, default=16)
    parser.add_argument('--requests-per-second', type=float, default=12)
    parser.add_argument('--candidate-buffer', type=int, default=400)
    parser.add_argument('--max-pages', type=int, default=5, help='Pages per query; GitHub permits at most 10')
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.target < 1 or not 1 <= args.workers <= 32 or not 1 <= args.max_pages <= 10 or not 0 < args.requests_per_second <= 14:
        parser.error('target must be positive, workers 1..32, max-pages 1..10 and requests-per-second (0,14]')
    token_result = subprocess.run(['gh', 'auth', 'token'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    token = token_result.stdout.decode().strip()
    if token_result.returncode or not token:
        print('An existing authenticated gh login is required.', flush=True)
        return 2
    api = GitHub(token, args.requests_per_second)
    del token, token_result
    started = now()
    initial_rate = api.json('/rate_limit')
    print('START target=' + str(args.target) + ' core_remaining=' +
          str(initial_rate['resources']['core']['remaining']), flush=True)
    meta = {
        'schema_version': 1,
        'started_at': started,
        'completed_at': None,
        'requested_successful_scans': args.target,
        'unique_repos': 0,
        'attempted_readme_scans': 0,
        'successful_readme_scans': 0,
        'failed': 0,
        'queries': [],
        'method': 'Public, non-fork, non-archived GitHub repository search followed by an actual authenticated GET of each repository README. README bytes are decoded, analyzed for document features, SHA-256 hashed and discarded.',
        'description_policy': 'Repository descriptions remain in their original upstream language. description_zh mirrors the same text and is explicitly not a translation. No LLM-written description or individual manual review is claimed.',
        'readme_heading_count_policy': 'Count of distinct heading-like lines encountered, capped at six; a count of six means at least six. Heading text is not retained.',
        'classification_policy': 'Targets and categories are conservative automatic labels from repository names, descriptions and topics. An empty targets array means insufficient metadata, not unsupported capability.',
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
    candidates = {}
    exhausted = set()
    candidate_goal = args.target + args.candidate_buffer
    for page in range(1, args.max_pages + 1):
        for query in QUERIES:
            if query in exhausted:
                continue
            entry = {'query': query, 'page': page, 'per_page': 100, 'observed_at': now()}
            params = urlencode({'q': query, 'per_page': 100, 'page': page, 'sort': 'stars', 'order': 'desc'})
            try:
                result = api.json('/search/repositories?' + params, search=True)
                items = result.get('items', [])
                entry.update({'status': 'ok', 'total_count': result.get('total_count'),
                              'returned': len(items), 'incomplete_results': result.get('incomplete_results', False)})
                for repo in items:
                    # Do not allow accessible private repositories into a public index.
                    if repo.get('private') is not False or repo.get('fork') or repo.get('archived'):
                        continue
                    identifier = repo['id']
                    if identifier in candidates:
                        if query not in candidates[identifier]['_matched_queries']:
                            candidates[identifier]['_matched_queries'].append(query)
                    else:
                        repo['_metadata_observed_at'] = entry['observed_at']
                        repo['_matched_queries'] = [query]
                        candidates[identifier] = repo
                if len(items) < 100 or page * 100 >= min(result.get('total_count', 0), 1000):
                    exhausted.add(query)
            except ScanError as error:
                entry.update({'status': 'failed', 'reason': error.reason, 'http_status': error.status})
            meta['queries'].append(entry)
            print(f'DISCOVERY queries={len(meta["queries"])} candidates={len(candidates)} page={page}', flush=True)
            if len(candidates) >= candidate_goal:
                break
        if len(candidates) >= candidate_goal:
            break
    meta['unique_repos'] = len(candidates)
    print(f'DISCOVERY_COMPLETE unique_repos={len(candidates)}; starting actual README GETs', flush=True)
    records, failures = [], []
    save(args.output, meta, records, failures)
    source = iter(candidates.values())
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        pending = {}
        for _ in range(min(args.workers, args.target)):
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
                    # No exception message or headers can leak authentication or README text.
                    record, failure = None, {
                        'id': 'scan-' + str(repo['id']), 'full_name': repo['full_name'],
                        'url': repo['html_url'], 'observed_at': now(),
                        'scan_status': 'failed', 'reason': 'worker-' + type(error).__name__,
                        'http_status': None,
                    }
                (records if record else failures).append(record or failure)
                meta['attempted_readme_scans'] = len(records) + len(failures)
                if meta['attempted_readme_scans'] % 100 == 0:
                    print(f'README_PROGRESS success={len(records)} failed={len(failures)} core_remaining={api.rate.get("core", {}).get("remaining", "unknown")}', flush=True)
                    save(args.output, meta, records, failures)
                if len(records) + len(pending) < args.target:
                    following = next(source, None)
                    if following is not None:
                        pending[pool.submit(scan_readme, api, following)] = following
    meta['target_reached'] = len(records) >= args.target
    meta['unattempted_candidates'] = len(candidates) - len(records) - len(failures)
    # Stable ordering makes review and website indexing easier.
    records.sort(key=lambda record: (-record['stars'], record['full_name'].casefold()))
    failures.sort(key=lambda record: record['full_name'].casefold())
    save(args.output, meta, records, failures, complete=True)
    print(f'COMPLETE successful_readme_scans={len(records)} failed={len(failures)} unique_repos={len(candidates)} target_reached={meta["target_reached"]}', flush=True)
    return 0 if meta['target_reached'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
