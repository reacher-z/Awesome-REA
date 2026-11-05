#!/usr/bin/env python3
"""Follow the registered public sources and keep what they list as unreviewed leads.

``collect`` reads data/discovery-sources.json, fetches every due source at its current revision (a pinned
commit for GitHub lists and registries, a versioned arXiv page), parses its listings, applies the source's
registered scope rules, resolves GitHub repositories to numeric IDs and writes every in-scope candidate to
``.cache/discovery-leads/candidates.json``. ``prepare`` selects the candidates that are new to every repository
layer (scripts/discovery_leads.py) and writes one batch under data/discoveries/leads/. ``run`` is the
scheduled-workflow path: it prepares the batch on the default branch's current commit, runs the validators,
commits only that batch file through the Git data API, opens or updates the pull request on
``automation/discovery-leads``, dispatches the required checks and rebase-merges once both pass.

No upstream code is run, nothing is installed, and no lead is ever curated, translated or marked
source-reviewed. Upstream text is reduced to link labels, section headings and bounded metadata.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter
import datetime as dt
import hashlib
from html import unescape
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
import xml.etree.ElementTree as ElementTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import discovery_leads as leads  # noqa: E402

CACHE = ROOT / '.cache/discovery-leads'
USER_AGENT = 'AwesomeREA-Discovery/1.0 (+https://github.com/reacher-z/Awesome-REA)'
MAX_RESPONSE = 8 * 1024 * 1024
MAX_GRAPHQL_RESPONSE = 16 * 1024 * 1024
MAX_REQUESTS, MAX_SECONDS = 600, 18 * 60
QUOTA_RESERVE = 200
# Minimum seconds between requests to one host: arXiv's robots.txt asks for a 15-second crawl delay on
# arxiv.org and its API terms for one request every three seconds.
HOST_INTERVALS = {'arxiv.org': 15.0, 'export.arxiv.org': 3.0, 'api.semanticscholar.org': 1.5, 'huggingface.co': 0.5}
GRAPHQL_CHUNK = 50
ERRORS = ('http-error', 'network-error', 'redirect-blocked', 'response-too-large', 'request-budget', 'time-budget',
          'rate-limited', 'quota-reserve', 'invalid-upstream', 'git-blob-mismatch', 'token-unavailable', 'not-found')
REPOSITORY_FIELDS = ('databaseId nameWithOwner isPrivate isFork isArchived stargazerCount pushedAt description '
                     'homepageUrl licenseInfo { spdxId } parent { nameWithOwner } '
                     'repositoryTopics(first: 20) { nodes { topic { name } } }')
DROP_URL = re.compile(r'(awesome\.re|sindresorhus/awesome(\b|$)|/blob/[^ ]*(CONTRIBUTING|LICENSE|code-of-conduct)|'
                      r'/issues/new|/pulls?$|/compare/|#readme$)', re.I)
DEFUNCT = re.compile(r'^\s*(?:[-*+]|\d+\.)?\s*~~')
KIND_PRIORITY = ('research', 'case-study', 'integration', 'collection', 'learning-resource', 'documentation', 'project', 'tool')
NAME_LIMIT = 200


class SourceError(Exception):
    def __init__(self, reason: str, status: int | None = None):
        assert reason in ERRORS
        self.reason, self.status = reason, status
        super().__init__(reason)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, newurl):
        return None


def allowed(url: str, method: str = 'GET') -> bool:
    """Only the API and page routes the source types need; the GitHub token goes to api.github.com alone."""
    try:
        parts = urlsplit(url)
    except ValueError:
        return False
    if parts.scheme != 'https' or parts.username or parts.password or parts.port not in (None, 443) or parts.fragment:
        return False
    host, path = parts.hostname, parts.path
    if host == 'api.github.com':
        return ((method == 'POST' and path == '/graphql' and not parts.query)
                or (method == 'GET' and bool(re.fullmatch(r'/repos/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/git/blobs/[0-9a-f]{40}', path))
                    and not parts.query))
    if method != 'GET':
        return False
    if host == 'arxiv.org':
        return bool(re.fullmatch(r'/html/\d{4}\.\d{4,5}(?:v\d{1,3})?/?', path)) and not parts.query
    if host == 'export.arxiv.org':
        return path == '/api/query'
    if host == 'api.semanticscholar.org':
        return bool(re.fullmatch(r'/graph/v1/paper/arXiv:\d{4}\.\d{4,5}/references', path))
    if host == 'huggingface.co':
        return path in ('/api/models', '/api/datasets')
    return False


class Client:
    """Bounded HTTPS client: allowlisted routes, no automatic redirects, size and time limits, polite pacing."""

    def __init__(self, token: str = '', *, opener=None, clock=time.monotonic, sleep=time.sleep,
                 max_requests: int = MAX_REQUESTS, max_seconds: int = MAX_SECONDS):
        self.token, self.opener, self.clock, self.sleep = token, opener or build_opener(NoRedirect()), clock, sleep
        self.deadline, self.requests, self.max_requests, self.max_seconds = clock() + max_seconds, 0, max_requests, max_seconds
        self.halted, self.last, self.remaining = set(), {}, None

    def fetch(self, url: str, *, data: bytes | None = None, limit: int = MAX_RESPONSE) -> bytes:
        method = 'POST' if data is not None else 'GET'
        for _ in range(3):
            if not allowed(url, method):
                raise SourceError('redirect-blocked')
            host = urlsplit(url).hostname
            if self.clock() >= self.deadline:
                raise SourceError('time-budget')
            if self.requests >= self.max_requests:
                raise SourceError('request-budget')
            if host in self.halted:
                raise SourceError('rate-limited', 429)
            if host == 'api.github.com':
                if not self.token:
                    raise SourceError('token-unavailable')
                if self.remaining is not None and self.remaining < QUOTA_RESERVE:
                    raise SourceError('quota-reserve')
            wait = HOST_INTERVALS.get(host, 0) - (self.clock() - self.last.get(host, -1e9))
            if wait > 0:
                if self.clock() + wait >= self.deadline:
                    raise SourceError('time-budget')
                self.sleep(wait)
            headers = {'User-Agent': USER_AGENT}
            if host == 'api.github.com':
                headers.update({'Accept': 'application/vnd.github+json', 'Authorization': 'Bearer ' + self.token,
                                'X-GitHub-Api-Version': '2022-11-28'})
                if data is not None:
                    headers['Content-Type'] = 'application/json'
            self.requests += 1
            self.last[host] = self.clock()
            try:
                with self.opener.open(Request(url, data=data, headers=headers, method=method),
                                      timeout=max(1.0, min(30.0, self.deadline - self.clock()))) as response:
                    chunks, size = [], 0
                    while True:
                        chunk = response.read(min(65536, limit + 1 - size))
                        if not chunk:
                            break
                        chunks.append(chunk)
                        size += len(chunk)
                        if size > limit:
                            raise SourceError('response-too-large')
                    remaining = response.headers.get('X-RateLimit-Remaining')
                    if host == 'api.github.com' and remaining is not None and remaining.isdigit():
                        self.remaining = int(remaining)
                    return b''.join(chunks)
            except HTTPError as error:
                code, location = error.code, error.headers.get('Location', '')
                retry_after, remaining = error.headers.get('Retry-After'), error.headers.get('X-RateLimit-Remaining')
                error.close()
                if code in (301, 302, 303, 307, 308) and data is None:
                    target = urljoin(url, location)
                    if urlsplit(target).hostname != host:
                        raise SourceError('redirect-blocked') from None
                    url = target
                    continue
                if code == 429 or (code == 403 and (retry_after or remaining == '0')):
                    self.halted.add(host)
                    raise SourceError('rate-limited', code) from None
                raise SourceError('not-found' if code in (404, 410) else 'http-error', code) from None
            except (URLError, OSError):
                raise SourceError('network-error') from None
        raise SourceError('redirect-blocked')

    def json(self, url: str, *, data: bytes | None = None, limit: int = MAX_RESPONSE):
        try:
            return json.loads(self.fetch(url, data=data, limit=limit))
        except (ValueError, UnicodeError, RecursionError):
            raise SourceError('invalid-upstream') from None

    def graphql(self, query: str) -> dict:
        """The data of a GraphQL query; only NOT_FOUND errors (a missing repository) leave a null in it."""
        result = self.json('https://api.github.com/graphql', data=json.dumps({'query': query}).encode(),
                           limit=MAX_GRAPHQL_RESPONSE)
        if not isinstance(result, dict) or not isinstance(result.get('data'), dict):
            raise SourceError('invalid-upstream')
        errors = result.get('errors') or []
        kinds = {error.get('type') if isinstance(error, dict) else None for error in errors}
        if kinds - {'NOT_FOUND'}:
            raise SourceError('rate-limited' if 'RATE_LIMITED' in kinds else 'invalid-upstream')
        return result['data']


def log(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


# --- text helpers -----------------------------------------------------------------------------------

def single_line(value, limit: int) -> str:
    text = re.sub(r'[\x00-\x1f\x7f]+', ' ', str(value or ''))
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > limit:
        text = text[:limit - 1].rstrip() + '…'
    return text


def clean_doi(value) -> str | None:
    doi = leads.doi_clean(str(value)) if value else ''
    return doi if re.fullmatch(r'10\.\d{4,9}/\S{1,300}', doi) else None


def clean_arxiv(value) -> str | None:
    identifier = str(value or '').strip().lower()
    return identifier if leads.ARXIV_RE.fullmatch('arxiv:' + identifier) else None


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def repository_literal(full_name: str) -> str:
    owner, name = full_name.split('/', 1)
    if not leads.FULL_NAME.fullmatch(full_name):
        raise ValueError('unsafe repository name')
    return f'owner: {json.dumps(owner)}, name: {json.dumps(name)}'


def github_file(client: Client, repository: str, path: str) -> tuple[bytes, str, str]:
    """Bytes of ``path`` at the default branch's current commit, verified against its Git blob ID."""
    query = (f'query {{ repository({repository_literal(repository)}) {{ isPrivate defaultBranchRef {{ target {{ '
             f'... on Commit {{ oid file(path: {json.dumps(path)}) {{ oid object {{ ... on Blob {{ byteSize isBinary '
             f'isTruncated text }} }} }} }} }} }} }} }}')
    data = client.graphql(query)
    node = data.get('repository')
    if not node or node.get('isPrivate') is not False:
        raise SourceError('not-found')
    target = (node.get('defaultBranchRef') or {}).get('target') or {}
    entry = target.get('file')
    if not entry or not re.fullmatch(r'[0-9a-f]{40}', str(target.get('oid'))) or not re.fullmatch(r'[0-9a-f]{40}', str(entry.get('oid'))):
        raise SourceError('not-found')
    blob = entry.get('object') or {}
    raw = None
    if blob.get('isBinary') is False and blob.get('isTruncated') is False and isinstance(blob.get('text'), str):
        raw = blob['text'].encode('utf-8')
        if git_blob_sha(raw) != entry['oid']:
            raw = None  # the text was re-encoded (BOM, invalid UTF-8); read the exact bytes instead
    if raw is None:
        if type(blob.get('byteSize')) is not int or blob['byteSize'] > MAX_RESPONSE:
            raise SourceError('response-too-large')
        response = client.json(f"https://api.github.com/repos/{repository}/git/blobs/{entry['oid']}", limit=MAX_RESPONSE * 2)
        try:
            raw = base64.b64decode(''.join(str(response['content']).split()), validate=True)
        except (KeyError, TypeError, ValueError):
            raise SourceError('invalid-upstream') from None
    if git_blob_sha(raw) != entry['oid']:
        raise SourceError('git-blob-mismatch')
    return raw, target['oid'], entry['oid']


# --- Markdown lists ---------------------------------------------------------------------------------

LINK = re.compile(r'\[((?:[^\[\]]|\[[^\]]*\])*)\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)')
HREF = re.compile(r'<a\s[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', re.I | re.S)
BARE = re.compile(r'(?<![\(\[<"\'=])\bhttps?://[^\s<>\)\]"\'`|]+')
REFDEF = re.compile(r'^\s*\[([^\]]+)\]:\s*(\S+)')
IMAGE = re.compile(r'\.(png|jpe?g|gif|svg|webp)(\?|$)|//(img\.)?shields\.io|//badgen\.net|//badge\.fury\.io|'
                   r'/badges?/[^/]*\.svg|awesome\.re/badge', re.I)


def markdown_links(text: str) -> list[dict]:
    """Every http(s) link with its line, heading path, label and line context; code blocks and badges skipped."""
    text = re.sub(r'<!--.*?-->', lambda match: '\n' * match.group(0).count('\n'), text, flags=re.S)
    heads, found_links, in_code = [], [], False
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        heading = re.match(r'^(#{1,6})\s+(.*)$', stripped)
        html_heading = re.match(r'^<h([1-6])[^>]*>(.*?)</h\1>', stripped, re.I)
        if heading or html_heading:
            level = len(heading.group(1)) if heading else int(html_heading.group(1))
            title = heading.group(2) if heading else html_heading.group(2)
            title = LINK.sub(lambda match: match.group(1), re.sub(r'<[^>]+>', '', title)).strip(' #')
            heads = heads[:level - 1] + [''] * max(0, level - 1 - len(heads))
            heads = heads[:level - 1] + [title]
            continue
        found = [(match.group(2), match.group(1)) for match in LINK.finditer(line)]
        found += [(unescape(match.group(1)), re.sub(r'<[^>]+>', '', match.group(2))) for match in HREF.finditer(line)]
        definition = REFDEF.match(line)
        if definition:
            found.append((definition.group(2), definition.group(1)))
        rest = LINK.sub(' ', HREF.sub(' ', line))
        found += [(match.group(0).rstrip('.,;:'), '') for match in BARE.finditer(rest)]
        plain = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', LINK.sub(lambda match: match.group(1), line))).strip()
        for url, label in found:
            if re.match(r'https?://', url) and not IMAGE.search(url):
                found_links.append({'line': number, 'section': ' > '.join(head for head in heads if head), 'url': url,
                                    'label': re.sub(r'\s+', ' ', label).strip(), 'context': plain[:400]})
    return found_links


def quote_subsections(text: str) -> dict[int, str]:
    """Lines under a ``> Name`` quote line that some lists use as an unmarked subsection heading."""
    result, current = {}, ''
    for number, line in enumerate(text.splitlines(), 1):
        if re.match(r'^#{1,6}\s', line):
            current = ''
        match = re.match(r'^\s*>\s+([^\[\]()]{2,60})$', line)
        if match:
            current = match.group(1).strip()
        result[number] = current
    return result


def excluded(key: str, scope: dict) -> str | None:
    for rule in scope.get('rules', scope.get('exclude', [])):
        if re.search(rule['pattern'], key, re.I):
            return rule['reason']
    return None


def kind_for(scope: dict, section: str, subsection: str = '') -> str:
    kind = scope.get('default_kind', 'tool')
    for pattern, value in scope.get('kind_rules', []):
        if re.search(pattern, section, re.I) or (subsection and re.search(pattern, subsection, re.I)):
            kind = value
    return kind


def readme_listings(source: dict, text: str, revision: str) -> tuple[list[dict], Counter]:
    """One item per list line: its first resolvable link, inside the source's in-scope sections."""
    scope, counts = source.get('scope', {}), Counter()
    repository = source['repository'].lower()
    subsections = quote_subsections(text) if 'include_subsections' in scope else None
    evidence = f"https://github.com/{source['repository']}/blob/{revision}/{source['path']}"
    seen_lines, found = set(), []
    for link in markdown_links(text):
        counts['links'] += 1
        section = link['section']
        parts = section.split(' > ')
        inner = ' > '.join(parts[1:]) if len(parts) > 1 else section
        if 'exclude_sections' in scope and re.search(scope['exclude_sections'], inner, re.I):
            continue
        if not (re.search(scope.get('include_sections', '.'), inner, re.I) or re.search(scope.get('include_sections', '.'), section, re.I)):
            continue
        subsection = ''
        if subsections is not None:
            subsection = subsections.get(link['line'], '')
            if not re.search(scope['include_subsections'], subsection, re.I):
                continue
        if link['line'] in seen_lines or DROP_URL.search(link['url']):
            continue
        key, link_type, flags = leads.url_key(link['url'])
        if key is None or key in ('gh:' + repository, 'ghorg:' + repository.split('/')[0]):
            continue
        if 'keyword' in scope and not re.search(scope['keyword'], link['context'] + ' ' + link['url'], re.I):
            seen_lines.add(link['line'])
            continue
        seen_lines.add(link['line'])
        if DEFUNCT.match(link['context']):
            counts['excluded:defunct'] += 1  # the list strikes the entry through as dead or abandoned
            continue
        full_section = inner + (' > ' + subsection if subsection else '')
        reason = excluded(key, scope) or (excluded('section:' + full_section, scope))
        if reason:
            counts['excluded:' + reason] += 1
            continue
        kind = kind_for(scope, inner, subsection)
        if link_type == 'paper':
            kind = 'research'
        elif link_type == 'video' and kind == 'tool':
            kind = 'learning-resource'
        label = link['label']
        if not label or label.lower().startswith('http'):
            label = key.split(':', 1)[1].split('/')[-1] if key.startswith('gh:') else link['context'][:80]
        found.append({'source_id': source['id'], 'url': link['url'], 'key': key, 'flags': flags, 'kind': kind,
                      'label': single_line(label, NAME_LIMIT), 'section': single_line(full_section, 300),
                      'evidence_url': f"{evidence}#L{link['line']}"})
        counts['in_scope'] += 1
    return found, counts


def pre_list_listings(source: dict, text: str, revision: str) -> tuple[list[dict], Counter]:
    """techge/PRE-list: numbered paper references and the source-code table, as the list structures them."""
    scope, counts, found = source.get('scope', {}), Counter(), []
    evidence = f"https://github.com/{source['repository']}/blob/{revision}/{source['path']}"
    lines = text.splitlines()
    references = re.split(r'^#### \[(\d+)\]\s*$', text, flags=re.M)
    offsets = {match.group(1): text[:match.start()].count('\n') + 1 for match in re.finditer(r'^#### \[(\d+)\]\s*$', text, flags=re.M)}
    for index in range(1, len(references), 2):
        number, body = references[index], references[index + 1].strip().split('\n#', 1)[0].strip()
        counts['links'] += 1
        match = re.search(r'[“"]([^”"]{8,300})[”"]', body)
        if match:
            title = match.group(1).strip().rstrip(',.')
        else:
            other = re.search(r':\s*([A-Z][^.]{8,250})\.\s', body) or re.search(r'\)\.\s*([A-Z][^.]{8,250})\.', body)
            title = other.group(1).strip() if other else body[:120]
        doi_match = leads.DOI_RE.search(body)
        doi = clean_doi(doi_match.group(1)) if doi_match else None
        if not paper_in_scope(title, scope, always=True):
            continue
        key = 'doi:' + doi if doi else leads.title_key(title)
        if not key:
            continue
        links = re.findall(r'\((https?://[^)\s]+)\)', body)
        url = ('https://doi.org/' + doi) if doi else (links[0] if links else f'{evidence}#L{offsets.get(number, 1)}')
        found.append({'source_id': source['id'], 'url': url, 'key': key, 'flags': {}, 'kind': 'research',
                      'label': single_line(title, NAME_LIMIT), 'section': 'References',
                      'evidence_url': f'{evidence}#L{offsets.get(number, 1)}',
                      'paper': {'title': single_line(title, 400), 'doi': doi, 'arxiv_id': clean_arxiv(leads.arxiv_from(body))}})
        counts['in_scope'] += 1
    header = text.split('# Table of Contents', 1)[0]
    for number, line in enumerate(header.splitlines(), 1):
        if line.lstrip().startswith('*') and re.search(r'[“"]', line):
            match = re.search(r'[“"]([^”"]{8,300})[”"]', line)
            if not match:
                continue
            counts['links'] += 1
            title = match.group(1).strip().rstrip(',.')
            doi_match = leads.DOI_RE.search(line)
            doi = clean_doi(doi_match.group(1)) if doi_match else None
            key = 'doi:' + doi if doi else leads.title_key(title)
            if not key:
                continue
            found.append({'source_id': source['id'], 'url': ('https://doi.org/' + doi) if doi else f'{evidence}#L{number}',
                          'key': key, 'flags': {}, 'kind': 'research', 'label': single_line(title, NAME_LIMIT),
                          'section': 'Surveys the list is based on', 'evidence_url': f'{evidence}#L{number}',
                          'paper': {'title': single_line(title, 400), 'doi': doi, 'arxiv_id': None}})
            counts['in_scope'] += 1
    if '# Source Code' in text:
        start = text[:text.index('# Source Code')].count('\n')
        block = text.split('# Source Code', 1)[1].split('# References', 1)[0]
        for offset, line in enumerate(block.splitlines()):
            for url in re.findall(r'https?://[^\s|)]+', line):
                key, _, flags = leads.url_key(url)
                if not key:
                    continue
                counts['links'] += 1
                name = line.split('|')[1].strip() if line.count('|') > 2 else url
                name = re.sub(r'\[\[\d+\]\]\(#\d+\)', '', name).strip() or url
                reason = excluded(key, scope)
                if reason:
                    counts['excluded:' + reason] += 1
                    continue
                found.append({'source_id': source['id'], 'url': url, 'key': key, 'flags': flags, 'kind': 'tool',
                              'label': single_line(name, NAME_LIMIT), 'section': 'Source Code',
                              'evidence_url': f'{evidence}#L{start + offset + 1}'})
                counts['in_scope'] += 1
    del lines
    return found, counts


# --- paper screen (survey bibliographies, PRE-list, arXiv) ---------------------------------------------

PAPER_IN = re.compile(
    r'binar(y|ies)|decompil|disassembl|reverse[- ]engineer|revers(ing|e) |malware|firmware|executable|stripped|'
    r'obfuscat|deobfusc|unpack|packer|lift(ing|er)|\bIR\b.*binar|type (inference|recovery|reconstruction)|'
    r'variable (name|type)s?|function (name|boundar|signature|identification|recogni|summar)|symbol (name|recovery)|'
    r'code similarity|clone detection.*binar|patch (presence|analysis|diff)|binary diff|bindiff|'
    r'protocol (reverse|inference|format|state|message|field)|message format|network trace|packet|'
    r'rehost|emulat|embedded (system|device|firmware)|iot (device|firmware)|microcontroller|baseband|'
    r'assembly|bytecode|machine code|dalvik|android app|\bapk\b|smart contract|evm|webassembly|wasm|'
    r'control[- ]flow (recovery|structur)|structuring|goto|jump table|switch recovery|calling convention|'
    r'data structure(s)? (recovery|reverse|excavat)|\bc\+\+ class|vtable|object[- ]oriented .*binar|'
    r'source code recovery|recompil|translation validation|binary rewriting|reassembl|instrumentation|'
    r'taint|symbolic execution .*binar|program synthesis.*binar|compiler (provenance|identification)|optimization level|'
    r'code search.*binar|semantic.*binar|software composition.*binar|third-party librar(y|ies) (detection|identification)|'
    r'inverse compilation|code reconstruction|value-set|symbols are lacking|birthmark|license violation|memory (analysis|forensics)|'
    r'kernel objects|cortex-m|flirt|p-code|processor specification|sleigh|pyelftools|\belf\b|\bdwarf\b|binsync|ghidra|\bida\b|'
    r'radare|binary ninja|decompiler|chisel', re.I)
PAPER_OUT = re.compile(
    r'^(gpt-4|llama|code ?llama|qwen|deepseek|mistral|gemini|claude|starcoder|chain-of-thought|lora|attention is all|'
    r'language models are|training (language|verifiers)|scaling laws|codebert|graphcodebert|codet5|unixcoder|'
    r'evaluating large language models trained on code|competition-level|swe-bench|react:|toolformer|self-consistency|'
    r'retrieval-augmented|direct preference|proximal policy|deepseekmath|group relative)', re.I)
PAPER_MALWARE_DETECTION = re.compile(
    r'malware (detection|detector|classification|classifier)s?|classif\w* (of )?malware|detecting (evasive )?(windows )?malware|'
    r'adversarial (training|learning)?.*malware|malware.*(concept drift)|neural malware control|ransomware detection', re.I)
PAPER_FUZZING = re.compile(r'\bfuzz|exploit generation|automatic exploit|\bcve\b', re.I)


def paper_in_scope(title: str, scope: dict, *, always: bool = False) -> bool:
    """The ``re-subject-v1`` title screen: research about analysing or reconstructing software and devices.

    It drops general LLM/ML papers, ML malware detection, and fuzzing or exploitation unless the title is about
    firmware, rehosting, emulation, protocols or decompilation. ``always`` keeps a curated RE bibliography whole.
    """
    if always or scope.get('paper_screen') != 're-subject-v1':
        return True
    title = title or ''
    if PAPER_OUT.search(title) or PAPER_MALWARE_DETECTION.search(title) or not PAPER_IN.search(title):
        return False
    return not (PAPER_FUZZING.search(title) and not re.search(r'firmware|rehost|emulat|protocol|decompil|format reverse', title, re.I))


def survey_listings(client: Client, source: dict, papers: dict) -> tuple[list[dict], Counter, dict]:
    """A curated survey's bibliography from its arXiv HTML page, identified through Semantic Scholar references."""
    scope, counts, found = source.get('scope', {}), Counter(), []
    paper = papers[source['paper_id']]
    arxiv_id = paper['arxiv_id']
    raw = client.fetch(f'https://arxiv.org/html/{arxiv_id}', limit=MAX_RESPONSE)
    page = raw.decode('utf-8', 'replace')
    # The page serves the latest version; its assets live under <id>v<n>/, which pins the evidence to it.
    version = re.search(re.escape(arxiv_id) + r'(v\d{1,3})\b', page)
    revision = arxiv_id + (version.group(1) if version else '')
    try:
        references = client.json(f'https://api.semanticscholar.org/graph/v1/paper/arXiv:{arxiv_id}/references?'
                                 + urlencode({'fields': 'title,externalIds,year,venue', 'limit': 1000}))
        cited = [row['citedPaper'] for row in references.get('data') or []
                 if isinstance(row, dict) and isinstance(row.get('citedPaper'), dict) and row['citedPaper'].get('title')]
    except SourceError:
        cited = []  # identifiers are optional; titles from the bibliography still identify each entry
    normalized = [(leads.norm_title(row['title']), row) for row in cited]
    used = set()
    items = re.findall(r'(<li[^>]*class="ltx_bibitem[^"]*"[^>]*>)(.*?)</li>', page, re.S)
    for opening, body in items:
        counts['links'] += 1
        anchor = (re.search(r'id="([^"]+)"', opening) or [None, None])[1]
        links = [unescape(link) for link in re.findall(r'href="([^"]+)"', body) if not link.startswith('#')]
        text = unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', body))).strip()
        text = re.sub(r'\s*Cited by:.*$', '', text)
        text_key = leads.norm_title(text)
        best = None
        for index, (title_text, _) in enumerate(normalized):
            if index not in used and len(title_text) >= 12 and title_text in text_key:
                if best is None or len(title_text) > len(normalized[best][0]):
                    best = index
        external, title, s2_id, year, venue = {}, None, None, None, None
        if best is not None:
            used.add(best)
            row = normalized[best][1]
            external, title = row.get('externalIds') or {}, row['title']
            s2_id = row.get('paperId') if re.fullmatch(r'[0-9a-f]{40}', str(row.get('paperId'))) else None
            year = row.get('year') if type(row.get('year')) is int and 1950 <= row['year'] <= 2100 else None
            venue = single_line(row.get('venue'), 200) or None
        arxiv = clean_arxiv(external.get('ArXiv') or leads.arxiv_from(text))
        doi = clean_doi(external.get('DOI'))
        if not doi:
            match = leads.DOI_RE.search(text)
            doi = clean_doi(match.group(1)) if match else None
        if doi and doi.startswith('10.48550/arxiv.'):
            arxiv, doi = arxiv or clean_arxiv(doi.split('arxiv.', 1)[1]), None
        if not title:
            match = re.search(r'<span class="ltx_text ltx_bib_title">(.*?)</span>', body, re.S)
            if match:
                title = unescape(re.sub(r'<[^>]+>', '', match.group(1))).strip().rstrip('.')
        if not title:
            match = re.search(r'[“"]([^”"]{8,300})[”"]', text)
            title = match.group(1).strip().rstrip(',.') if match else re.sub(r'^\[\d+\]\s*', '', text)[:200]
        if not paper_in_scope(title, scope):
            counts['excluded:not-re-subject'] += 1
            continue
        tool_link = None
        if not (arxiv or doi):
            for link in links:
                key, link_type, _ = leads.url_key(link)
                if key and link_type != 'paper' and re.match(r'https?://', link) and not re.search(
                        r'usenix\.org/(conference|system)|ndss-symposium\.org|dl\.acm\.org|ieeexplore\.ieee\.org|openreview\.net|'
                        r'aclanthology\.org|link\.springer\.com|sciencedirect\.com|\.pdf($|\?)', link, re.I):
                    tool_link = link
                    break
        evidence = f'https://arxiv.org/html/{revision}' + (f'#{anchor}' if anchor and re.fullmatch(r'[A-Za-z0-9_.:-]{1,80}', anchor) else '')
        if tool_link and not (arxiv or doi):
            key, _, flags = leads.url_key(tool_link)
            reason = excluded(key, scope)
            if reason:
                counts['excluded:' + reason] += 1
                continue
            found.append({'source_id': source['id'], 'url': tool_link, 'key': key, 'flags': flags, 'kind': 'tool',
                          'label': single_line(title, NAME_LIMIT), 'section': single_line(paper['title'], 300),
                          'evidence_url': evidence})
        else:
            key = ('arxiv:' + arxiv) if arxiv else ('doi:' + doi) if doi else leads.title_key(title)
            if not key:
                continue
            url = (f'https://arxiv.org/abs/{arxiv}' if arxiv else f'https://doi.org/{doi}' if doi else
                   next((link for link in links if re.match(r'https?://', link)), evidence))
            found.append({'source_id': source['id'], 'url': url, 'key': key, 'flags': {}, 'kind': 'research',
                          'label': single_line(title, NAME_LIMIT), 'section': single_line(paper['title'], 300),
                          'evidence_url': evidence,
                          'paper': {'title': single_line(title, 400), 'doi': doi, 'arxiv_id': arxiv, 'year': year,
                                    'venue': venue, 'semantic_scholar_id': s2_id}})
        counts['in_scope'] += 1
    result = {'evidence_url': f'https://arxiv.org/html/{revision}', 'revision': revision,
              'content_sha256': hashlib.sha256(raw).hexdigest()}
    return found, counts, result


# --- other source types -----------------------------------------------------------------------------

def topic_listings(client: Client, source: dict) -> tuple[list[dict], Counter, dict]:
    """The most-starred public repositories carrying a GitHub topic, screened by the source's text rules."""
    scope, counts, found, cursor, metadata = source.get('scope', {}), Counter(), [], None, {}
    page_size = 100
    while len(found) + counts['excluded'] < source['limit']:
        size = min(page_size, source['limit'] - len(found) - counts['excluded'])
        after = f', after: {json.dumps(cursor)}' if cursor else ''
        try:
            data = client.graphql(f'query {{ search(query: {json.dumps("topic:" + source["topic"] + " is:public sort:stars-desc")}, '
                                  f'type: REPOSITORY, first: {size}{after}) {{ pageInfo {{ hasNextPage endCursor }} '
                                  f'nodes {{ ... on Repository {{ {REPOSITORY_FIELDS} }} }} }} }}')
        except SourceError as error:
            # A search page that times out on GitHub's side is asked again once, half as large.
            if error.reason in ('http-error', 'invalid-upstream') and page_size > 25:
                page_size //= 2
                continue
            raise
        search = data.get('search') or {}
        nodes = search.get('nodes') or []
        for node in nodes:
            if not isinstance(node, dict) or not node.get('nameWithOwner'):
                continue
            counts['links'] += 1
            # The screen reads the name, description and other topics: the searched topic itself proves nothing.
            topics = [row['topic']['name'] for row in (node.get('repositoryTopics') or {}).get('nodes') or []
                      if row['topic']['name'] != source['topic']]
            text = ' '.join([node['nameWithOwner'], node.get('description') or '', ' '.join(topics)])
            key = 'gh:' + node['nameWithOwner'].lower()
            reason = excluded(key, scope)
            if ('require' in scope and not re.search(scope['require'], text, re.I)) or (
                    'exclude_text' in scope and re.search(scope['exclude_text'], text, re.I)):
                reason = reason or 'unrelated'
            if reason:
                counts['excluded'] += 1
                counts['excluded:' + reason] += 1
                continue
            metadata[key] = node
            found.append({'source_id': source['id'], 'url': 'https://github.com/' + node['nameWithOwner'], 'key': key,
                          'flags': {}, 'kind': scope.get('kind', 'tool'), 'label': single_line(node['nameWithOwner'], NAME_LIMIT),
                          'section': f"topic:{source['topic']} (most stars)",
                          'evidence_url': f"https://github.com/topics/{source['topic']}"})
            counts['in_scope'] += 1
        page = search.get('pageInfo') or {}
        if not nodes or not page.get('hasNextPage') or not page.get('endCursor'):
            break
        cursor = page['endCursor']
    return found, counts, {'evidence_url': f"https://github.com/topics/{source['topic']}", 'revision': None,
                           'content_sha256': None, 'metadata': metadata}


def json_registry_listings(client: Client, source: dict) -> tuple[list[dict], Counter, dict]:
    """Entries of a machine-readable registry file at the default branch's current commit."""
    scope, counts, found = source.get('scope', {}), Counter(), []
    raw, revision, _ = github_file(client, source['repository'], source['path'])
    try:
        document = json.loads(raw)
        rows = document[source['items']] if 'items' in source else document
        if not isinstance(rows, list):
            raise TypeError
    except (ValueError, KeyError, TypeError, UnicodeError):
        raise SourceError('invalid-upstream') from None
    evidence = f"https://github.com/{source['repository']}/blob/{revision}/{source['path']}"
    allowed_types = set(scope.get('include_types', []))
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get(source['url_field']), str):
            continue
        counts['links'] += 1
        if allowed_types and row.get(scope.get('type_field', 'type')) not in allowed_types:
            counts['excluded:linking-policy'] += 1
            continue
        if any(row.get(field) for field in scope.get('exclude_fields', [])):
            counts['excluded:linking-policy'] += 1
            continue
        key, _, flags = leads.url_key(row[source['url_field']])
        if not key:
            continue
        reason = excluded(key, scope)
        if reason:
            counts['excluded:' + reason] += 1
            continue
        label = single_line(row.get(source['name_field']) or key.split(':', 1)[1], NAME_LIMIT)
        section = single_line(' · '.join(str(row[field]) for field in ('type', 'platform') if isinstance(row.get(field), str)), 300)
        found.append({'source_id': source['id'], 'url': row[source['url_field']], 'key': key, 'flags': flags,
                      'kind': scope.get('kind', 'tool'), 'label': label, 'section': section, 'evidence_url': evidence})
        counts['in_scope'] += 1
    return found, counts, {'evidence_url': evidence, 'revision': revision, 'content_sha256': hashlib.sha256(raw).hexdigest()}


def directory_listings(client: Client, source: dict) -> tuple[list[dict], Counter, dict]:
    """One link per file of a registry directory (such as radare2-pm's package database) at a pinned commit."""
    scope, counts, found = source.get('scope', {}), Counter(), []
    query = (f'query {{ repository({repository_literal(source["repository"])}) {{ isPrivate defaultBranchRef {{ target {{ '
             f'... on Commit {{ oid file(path: {json.dumps(source["path"])}) {{ object {{ ... on Tree {{ entries {{ name type '
             f'object {{ ... on Blob {{ oid byteSize isTruncated text }} }} }} }} }} }} }} }} }} }} }}')
    node = client.graphql(query).get('repository')
    if not node or node.get('isPrivate') is not False:
        raise SourceError('not-found')
    target = (node.get('defaultBranchRef') or {}).get('target') or {}
    entries = (((target.get('file') or {}).get('object') or {}).get('entries')) or []
    revision = str(target.get('oid', ''))
    if not re.fullmatch(r'[0-9a-f]{40}', revision) or not entries:
        raise SourceError('invalid-upstream')
    url_pattern, label_pattern = re.compile(source['url_pattern'], re.M), re.compile(source['label_pattern'], re.M)
    digest = hashlib.sha256()
    for entry in sorted(entries, key=lambda row: str(row.get('name'))):
        blob = entry.get('object') or {}
        if entry.get('type') != 'blob' or not isinstance(blob.get('text'), str) or blob.get('isTruncated'):
            continue
        name = str(entry['name'])
        if not re.fullmatch(r'[A-Za-z0-9_.+-]{1,100}', name):
            continue
        raw = blob['text'].encode('utf-8')
        if git_blob_sha(raw) != blob.get('oid'):
            raise SourceError('git-blob-mismatch')
        digest.update(name.encode() + b'\0' + raw + b'\0')
        counts['links'] += 1
        match = url_pattern.search(blob['text'])
        if not match:
            continue
        key, _, flags = leads.url_key(match.group(1))
        if not key:
            continue
        reason = excluded(key, scope)
        if reason:
            counts['excluded:' + reason] += 1
            continue
        label_match = label_pattern.search(blob['text'])
        found.append({'source_id': source['id'], 'url': match.group(1), 'key': key, 'flags': flags,
                      'kind': scope.get('kind', 'tool'), 'label': single_line(name, NAME_LIMIT),
                      'section': single_line(label_match.group(1) if label_match else '', 300),
                      'evidence_url': f"https://github.com/{source['repository']}/blob/{revision}/{source['path']}/{quote(name)}"})
        counts['in_scope'] += 1
    return found, counts, {'evidence_url': f"https://github.com/{source['repository']}/tree/{revision}/{source['path']}",
                           'revision': revision, 'content_sha256': digest.hexdigest()}


ATOM = '{http://www.w3.org/2005/Atom}'
ARXIV_NS = '{http://arxiv.org/schemas/atom}'


def arxiv_listings(client: Client, source: dict) -> tuple[list[dict], Counter, dict]:
    """The newest arXiv submissions matching a query, kept when the title passes the paper screen."""
    scope, counts, found = source.get('scope', {}), Counter(), []
    url = 'https://export.arxiv.org/api/query?' + urlencode({'search_query': source['query'], 'start': 0,
                                                              'max_results': source['limit'], 'sortBy': 'submittedDate',
                                                              'sortOrder': 'descending'})
    raw = client.fetch(url)
    if b'<!DOCTYPE' in raw[:200] or b'<!ENTITY' in raw:
        raise SourceError('invalid-upstream')
    try:
        feed = ElementTree.fromstring(raw)
    except ElementTree.ParseError:
        raise SourceError('invalid-upstream') from None
    for entry in feed.findall(ATOM + 'entry'):
        counts['links'] += 1
        identifier = leads.arxiv_from(entry.findtext(ATOM + 'id') or '')
        title = single_line(entry.findtext(ATOM + 'title'), 400)
        if not identifier or not title:
            continue
        if not paper_in_scope(title, scope):
            counts['excluded:not-re-subject'] += 1
            continue
        published = entry.findtext(ATOM + 'published') or ''
        doi = clean_doi((entry.findtext(ARXIV_NS + 'doi') or '').strip())
        found.append({'source_id': source['id'], 'url': f'https://arxiv.org/abs/{identifier}', 'key': 'arxiv:' + identifier,
                      'flags': {}, 'kind': 'research', 'label': single_line(title, NAME_LIMIT),
                      'section': 'arXiv query (newest submissions)', 'evidence_url': url,
                      'paper': {'title': title, 'doi': doi, 'arxiv_id': identifier,
                                'year': int(published[:4]) if re.match(r'\d{4}-', published) else None,
                                'venue': 'arXiv', 'semantic_scholar_id': None}})
        counts['in_scope'] += 1
    return found, counts, {'evidence_url': url, 'revision': None, 'content_sha256': hashlib.sha256(raw).hexdigest()}


def huggingface_listings(client: Client, source: dict) -> tuple[list[dict], Counter, dict]:
    """The most-downloaded Hugging Face models or datasets matching a search term."""
    scope, counts, found = source.get('scope', {}), Counter(), []
    endpoint = 'models' if source['repo_type'] == 'model' else 'datasets'
    url = f'https://huggingface.co/api/{endpoint}?' + urlencode({'search': source['search'], 'limit': source['limit'],
                                                                 'sort': 'downloads', 'direction': -1})
    raw = client.fetch(url)
    try:
        rows = json.loads(raw)
        if not isinstance(rows, list):
            raise TypeError
    except (ValueError, TypeError, UnicodeError):
        raise SourceError('invalid-upstream') from None
    for row in rows:
        identifier = row.get('id') if isinstance(row, dict) else None
        if not isinstance(identifier, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,95}/[A-Za-z0-9][A-Za-z0-9_.-]{0,95}', identifier):
            continue
        counts['links'] += 1
        text = ' '.join([identifier, ' '.join(str(tag) for tag in row.get('tags') or [] if isinstance(tag, str))])
        if ('require' in scope and not re.search(scope['require'], text, re.I)) or (
                'exclude_text' in scope and re.search(scope['exclude_text'], text, re.I)):
            counts['excluded:unrelated'] += 1
            continue
        page = f'https://huggingface.co/{identifier}' if endpoint == 'models' else f'https://huggingface.co/datasets/{identifier}'
        modified = row.get('lastModified')
        modified = modified[:19] + 'Z' if isinstance(modified, str) and re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', modified) else None
        found.append({'source_id': source['id'], 'url': page, 'key': f"huggingface:{source['repo_type']}/{identifier}",
                      'flags': {}, 'kind': scope.get('kind', 'project'), 'label': single_line(identifier, NAME_LIMIT),
                      'section': f"Hugging Face {endpoint} search: {source['search']}", 'evidence_url': url,
                      'huggingface': {'repo_type': source['repo_type'], 'id': identifier,
                                      'downloads': row.get('downloads') if type(row.get('downloads')) is int and row['downloads'] >= 0 else 0,
                                      'likes': row.get('likes') if type(row.get('likes')) is int and row['likes'] >= 0 else 0,
                                      'last_modified': modified}})
        counts['in_scope'] += 1
    return found, counts, {'evidence_url': url, 'revision': None, 'content_sha256': hashlib.sha256(raw).hexdigest()}


# --- collection -------------------------------------------------------------------------------------

def due(source: dict, moment: dt.datetime, everything: bool) -> bool:
    """A slow source runs in one two-hour slot per period, chosen from its ID so sources spread out."""
    hours = source.get('every_hours', 2)
    if everything or hours <= 2:
        return True
    slots = hours // 2
    slot = (moment.toordinal() * 12 + moment.hour // 2) % slots
    return slot == int(hashlib.sha256(source['id'].encode()).hexdigest(), 16) % slots


def source_result(source: dict, status: str, counts: Counter | None = None, extra: dict | None = None,
                  error: str | None = None) -> dict:
    extra = extra or {}
    return {'id': source['id'], 'type': source['type'], 'evidence_url': extra.get('evidence_url'),
            'revision': extra.get('revision'), 'content_sha256': extra.get('content_sha256'), 'status': status,
            'error': error, 'links': (counts or {}).get('links', 0), 'in_scope': (counts or {}).get('in_scope', 0)}


def resolve_repositories(client: Client, names: list[str]) -> dict[str, dict | None]:
    """GitHub metadata by lower-case owner/name; None for a missing or private repository."""
    result = {}
    names = sorted({name for name in names if leads.FULL_NAME.fullmatch(name)})
    pending = [names[start:start + GRAPHQL_CHUNK] for start in range(0, len(names), GRAPHQL_CHUNK)]
    while pending:
        chunk = pending.pop(0)
        query = 'query { ' + ' '.join(f'r{index}: repository({repository_literal(name)}) {{ {REPOSITORY_FIELDS} }}'
                                       for index, name in enumerate(chunk)) + ' }'
        try:
            data = client.graphql(query)
        except SourceError as error:
            # A server-side timeout of a large query is retried in halves; a single failing lookup stops the run.
            if error.reason in ('invalid-upstream', 'http-error') and len(chunk) > 1:
                pending[:0] = [chunk[:len(chunk) // 2], chunk[len(chunk) // 2:]]
                continue
            raise
        for index, name in enumerate(chunk):
            node = data.get(f'r{index}')
            result[name.lower()] = node if isinstance(node, dict) and node.get('isPrivate') is False and node.get('databaseId') else None
    return result


def github_snapshot(node: dict) -> dict:
    topics = sorted({str(row['topic']['name']) for row in (node.get('repositoryTopics') or {}).get('nodes') or []
                     if re.fullmatch(r'[a-z0-9][a-z0-9-]{0,49}', str(((row or {}).get('topic') or {}).get('name')))})[:30]
    pushed = node.get('pushedAt')
    homepage = node.get('homepageUrl') or None
    license_id = ((node.get('licenseInfo') or {}).get('spdxId')) or None
    parent = (node.get('parent') or {}).get('nameWithOwner')
    return {'id': int(node['databaseId']), 'full_name': node['nameWithOwner'],
            'description': single_line(node.get('description'), 300), 'topics': topics,
            'stars': int(node.get('stargazerCount') or 0),
            'pushed_at': pushed[:19] + 'Z' if isinstance(pushed, str) and re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', pushed) else None,
            'archived': node.get('isArchived') is True, 'fork': node.get('isFork') is True,
            'parent': parent if isinstance(parent, str) and leads.FULL_NAME.fullmatch(parent) else None,
            'license': single_line(license_id, 64) if license_id and license_id != 'NOASSERTION' else None,
            'homepage': homepage if leads.public_url(homepage) else None}


class Keys:
    """Union-find over identity keys, so one resource listed under several keys becomes one candidate."""

    def __init__(self):
        self.parent = {}

    def find(self, key):
        self.parent.setdefault(key, key)
        while self.parent[key] != key:
            self.parent[key] = self.parent[self.parent[key]]
            key = self.parent[key]
        return key

    def union(self, first, second):
        first, second = self.find(first), self.find(second)
        if first != second:
            self.parent[second] = first


def identity_rank(key: str) -> int:
    for rank, prefix in enumerate(('github:', 'huggingface:', 'arxiv:', 'doi:', 'ieee:', 'openreview:')):
        if key.startswith(prefix):
            return rank
    return 9 if key.startswith('title:') else 6


def candidates_from(listings: list[dict], repositories: dict[str, dict | None], observed_at: str) -> tuple[list[dict], int]:
    """Merge listings into one candidate lead per resource; return them and the unavailable-repository count."""
    keys, groups, unavailable, nodes = Keys(), {}, set(), {}
    for listing in listings:
        own = {listing['key']}
        key = listing['key']
        if key.startswith('gh:'):
            node = repositories.get(key[3:])
            if node is None:
                unavailable.add(key)
                listing['skip'] = True
                continue
            own |= {f"github:{node['databaseId']}", 'gh:' + node['nameWithOwner'].lower()}
            nodes[f"github:{node['databaseId']}"] = node
        alias = (listing.get('flags') or {}).get('ghpages_alias')
        if alias and repositories.get(alias[3:]):
            node = repositories[alias[3:]]
            own |= {f"github:{node['databaseId']}", 'gh:' + node['nameWithOwner'].lower()}
            nodes[f"github:{node['databaseId']}"] = node
        paper = listing.get('paper') or {}
        if paper.get('arxiv_id'):
            own.add('arxiv:' + paper['arxiv_id'])
        if paper.get('doi'):
            own.add('doi:' + paper['doi'])
        if paper.get('title') and title_ok(paper['title']):
            own.add(leads.title_key(paper['title']))
        own.discard(None)
        listing['keys'] = own
        first = next(iter(own))
        for other in own:
            keys.union(first, other)
    for listing in listings:
        if not listing.get('skip'):
            groups.setdefault(keys.find(next(iter(listing['keys']))), []).append(listing)
    result = []
    for members in groups.values():
        all_keys = set().union(*(member['keys'] for member in members))
        identity = min(all_keys, key=lambda key: (identity_rank(key), key))
        node = nodes.get(identity)
        listings_by_source = {}
        for member in members:
            listings_by_source.setdefault(member['source_id'], {
                'source_id': member['source_id'], 'section': member['section'], 'label': member['label'],
                'evidence_url': member['evidence_url']})
        names = Counter(member['label'] for member in members if member['label'])
        kind = min((member['kind'] for member in members), key=KIND_PRIORITY.index)
        paper = merged_paper(members)
        hub = next((member['huggingface'] for member in members if member.get('huggingface')), None)
        if node is not None:
            url = 'https://github.com/' + node['nameWithOwner']
            if kind in ('tool', 'learning-resource', 'project') and (
                    re.search(r'awesome|[-_]lists?$', node['nameWithOwner'].lower())
                    or {'awesome', 'awesome-list', 'awesome-lists'} & set(github_snapshot(node)['topics'])):
                kind = 'collection'
        elif paper and paper.get('arxiv_id'):
            url = f"https://arxiv.org/abs/{paper['arxiv_id']}"
        elif paper and paper.get('doi'):
            url = f"https://doi.org/{paper['doi']}"
        else:
            url = next((member['url'] for member in members if leads.public_url(member['url'])), None)
        if url is None:
            continue
        if paper:
            kind = 'research'
        lead = {
            'id': leads.lead_id(identity), 'identity': identity, 'aliases': sorted(all_keys - {identity})[:20],
            'url': url, 'name': (paper or {}).get('title', names.most_common(1)[0][0] if names else identity)[:NAME_LIMIT],
            'kind_hint': kind, 'listings': list(listings_by_source.values())[:leads.MAX_LISTINGS],
            'observed_at': observed_at, 'verification': leads.VERIFICATION, 'review_status': leads.REVIEW_STATUS,
        }
        lead['name'] = single_line(lead['name'], NAME_LIMIT) or identity[:NAME_LIMIT]
        if node is not None:
            lead['github'] = github_snapshot(node)
        if paper:
            lead['paper'] = paper
        if hub:
            lead['huggingface'] = hub
        result.append(lead)
    return result, len(unavailable)


def title_ok(title: str) -> bool:
    return leads.title_key(title) is not None


def merged_paper(members: list[dict]) -> dict | None:
    rows = [member['paper'] for member in members if member.get('paper')]
    if not rows:
        return None
    pick = lambda field: next((row.get(field) for row in rows if row.get(field)), None)  # noqa: E731
    paper = {'title': single_line(pick('title'), 400), 'year': pick('year'), 'venue': pick('venue'),
             'arxiv_id': pick('arxiv_id'), 'doi': pick('doi'), 'semantic_scholar_id': pick('semantic_scholar_id')}
    return paper if paper['title'] else None


def collect(client: Client, root: Path = ROOT, *, everything: bool = False, now: dt.datetime | None = None) -> dict:
    """Follow every due registered source; return candidate leads and per-source results."""
    import strict_json
    registry, problems = leads.load_registry(root)
    if registry is None:
        raise ValueError('The source registry is missing or invalid: ' + '; '.join(problems[:3]))
    papers = {paper['id']: paper for paper in strict_json.load_path(Path(root) / 'data/papers.json')}
    now = now or dt.datetime.now(dt.timezone.utc)
    observed_at = now.strftime('%Y-%m-%dT%H:%M:%SZ')
    listings, results, topic_metadata = [], [], {}
    for source in registry['sources']:
        # The collector reads one list of exclusion rules: the source's own, then its shared sets.
        source = {**source, 'scope': {**source.get('scope', {}), 'rules': leads.exclusion_rules(registry, source)}}
        if not due(source, now, everything):
            results.append(source_result(source, 'not-due'))
            continue
        try:
            if source['type'] == 'github-readme-list':
                raw, revision, _ = github_file(client, source['repository'], source['path'])
                text = raw.decode('utf-8', 'replace')
                parser = pre_list_listings if source.get('parser') == 'pre-list' else readme_listings
                found, counts = parser(source, text, revision)
                extra = {'evidence_url': f"https://github.com/{source['repository']}/blob/{revision}/{source['path']}",
                         'revision': revision, 'content_sha256': hashlib.sha256(raw).hexdigest()}
            elif source['type'] == 'github-topic':
                found, counts, extra = topic_listings(client, source)
                topic_metadata.update(extra.pop('metadata'))
            elif source['type'] == 'github-json-registry':
                found, counts, extra = json_registry_listings(client, source)
            elif source['type'] == 'github-directory':
                found, counts, extra = directory_listings(client, source)
            elif source['type'] == 'survey-references':
                found, counts, extra = survey_listings(client, source, papers)
            elif source['type'] == 'arxiv-query':
                found, counts, extra = arxiv_listings(client, source)
            else:
                found, counts, extra = huggingface_listings(client, source)
        except SourceError as error:
            results.append(source_result(source, 'error', error=error.reason))
            log(f"SOURCE {source['id']} error={error.reason} requests={client.requests}")
            continue
        listings.extend(found)
        results.append(source_result(source, 'captured', counts, extra))
        log(f"SOURCE {source['id']} links={counts.get('links', 0)} in_scope={counts.get('in_scope', 0)} "
            f"requests={client.requests} seconds={round(client.clock() - client.deadline + client.max_seconds)}")
    names = {listing['key'][3:] for listing in listings if listing['key'].startswith('gh:') and listing['key'] not in topic_metadata}
    names |= {listing['flags']['ghpages_alias'][3:] for listing in listings if (listing.get('flags') or {}).get('ghpages_alias')}
    known = leads.existing_keys(root)['known']
    # Repositories already held under their listed name need no lookup; renamed ones are caught by numeric ID.
    lookup = sorted(name for name in names if 'gh:' + name not in known)
    repositories = {key[3:]: node for key, node in topic_metadata.items()}
    log(f'RESOLVE {len(lookup)} repositories ({len(names) - len(lookup)} already held by name)')
    try:
        repositories.update(resolve_repositories(client, lookup))
    except SourceError as error:
        raise ValueError(f'GitHub repository lookups failed ({error.reason}); no batch is prepared from partial identities') from None
    held = [listing for listing in listings if not (listing['key'].startswith('gh:') and listing['key'] in known
                                                    and listing['key'][3:] not in repositories)]
    skipped_known = len(listings) - len(held)
    candidates, unavailable = candidates_from(held, repositories, observed_at)
    # A curated repository renamed since its record was written is known here by numeric ID and current name.
    curated = sorted(key[3:] for key, reason in known.items() if reason == 'already-curated' and key.startswith('gh:'))
    log(f'RESOLVE {len(curated)} curated repositories for renames')
    try:
        curated_nodes = resolve_repositories(client, curated)
    except SourceError as error:
        raise ValueError(f'GitHub lookups of curated repositories failed ({error.reason})') from None
    held_keys = {}
    for node in curated_nodes.values():
        if node:
            held_keys[f"github:{node['databaseId']}"] = 'already-curated'
            held_keys['gh:' + node['nameWithOwner'].lower()] = 'already-curated'
    return {'schema_version': 1, 'collected_at': observed_at, 'sources': results, 'candidates': candidates,
            'held_keys': held_keys, 'unavailable': unavailable, 'known_by_name': skipped_known,
            'source_order': [source['id'] for source in registry['sources']],
            'registry_sha256': hashlib.sha256(leads.registry_bytes(root)).hexdigest(),
            'requests': client.requests}


# --- prepare and ingest -----------------------------------------------------------------------------

def prepare(collection: dict, provenance: dict, *, root: Path = ROOT) -> tuple[Path | None, str, int]:
    """Write the batch for this collection into ``root``; return (path, status, lead count)."""
    batches, problems = leads.load_batches(root)
    if problems:
        raise ValueError('Existing lead batches are invalid: ' + '; '.join(problems[:3]))
    # Candidates selected under other scope rules are not published: the next run collects again.
    if hashlib.sha256(leads.registry_bytes(root)).hexdigest() != collection['registry_sha256']:
        return None, 'registry-changed', 0
    name = f"leads-{provenance['run_id']}-{provenance['run_attempt']}"
    if any(batch['batch_id'] == name for batch in batches):
        return None, 'already-ingested', 0
    existing = leads.existing_keys(root, batches)
    # Identities the collection resolved for curated repositories (renames), unless a layer already names them.
    for key, reason in collection.get('held_keys', {}).items():
        existing['known'].setdefault(key, reason)
    batch, status = leads.build_batch(collection['candidates'], collection['sources'], provenance, existing,
                                      collected_at=collection['collected_at'], source_order=collection['source_order'],
                                      unavailable=collection['unavailable'])
    if batch is None:
        return None, status, 0
    problems = leads.validate_batch(batch, batch['batch_id'], batch['collected_at'][:7])
    if problems:
        raise ValueError('Prepared batch failed validation: ' + '; '.join(problems[:3]))
    path = leads.batch_path(root, batch['batch_id'], batch['collected_at'])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(leads.batch_bytes(batch))
    return path, status, len(batch['leads'])


def write_collection(collection: dict, directory: Path = CACHE) -> Path:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / 'candidates.json'
    temporary = directory / 'candidates.json.tmp'
    temporary.write_text(json.dumps(collection, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    temporary.replace(path)
    return path


def output(name: str, value) -> None:
    path = os.environ.get('GITHUB_OUTPUT')
    if path:
        with open(path, 'a', encoding='utf-8') as stream:
            stream.write(f'{name}={value}\n')


def step_summary(lines: list[str]) -> None:
    path = os.environ.get('GITHUB_STEP_SUMMARY')
    if path:
        with open(path, 'a', encoding='utf-8') as stream:
            stream.write('\n'.join(lines) + '\n')


LABEL = 'Add {count} unreviewed followed-source leads from discovery run {run}'


def commit_batch(github, base_sha: str, path: Path, message: str) -> str:
    """One commit on ``base_sha`` that adds the lead batch file; the leads branch is pointed at it."""
    relative = path.relative_to(ROOT).as_posix()
    if not re.fullmatch(r'data/discoveries/leads/20[0-9]{2}-(?:0[1-9]|1[0-2])/leads-[0-9]+-[0-9]+\.json', relative):
        raise ValueError('The lead ingest commits only a lead batch file')
    base_commit = github.get(f'git/commits/{base_sha}')
    blob = github.call('POST', 'git/blobs', {'content': base64.b64encode(path.read_bytes()).decode('ascii'),
                                             'encoding': 'base64'})[1]
    tree = github.call('POST', 'git/trees', {'base_tree': base_commit['tree']['sha'], 'tree': [
        {'path': relative, 'mode': '100644', 'type': 'blob', 'sha': blob['sha']}]})[1]
    commit = github.call('POST', 'git/commits', {'message': message, 'tree': tree['sha'], 'parents': [base_sha]})[1]
    status, _ = github.call('PATCH', f'git/refs/heads/{leads.INGEST_BRANCH}', {'sha': commit['sha'], 'force': True},
                            expected=(200, 422))
    if status == 422:
        github.call('POST', 'git/refs', {'ref': f'refs/heads/{leads.INGEST_BRANCH}', 'sha': commit['sha']})
    return commit['sha']


def pull_request_body(count: int, provenance: dict, batch_path: Path, attempt: int, collection: dict) -> str:
    run_url = f"https://github.com/{provenance['repository']}/actions/runs/{provenance['run_id']}"
    captured = sum(result['status'] == 'captured' for result in collection['sources'])
    failed = [result['id'] for result in collection['sources'] if result['status'] == 'error']
    return '\n'.join([
        f'Automated followed-source discovery from [run {provenance["run_id"]}]({run_url}) (attempt {provenance["run_attempt"]}).',
        '',
        f'Adds `{batch_path.relative_to(ROOT).as_posix()}` with {count} leads: links that the sources registered in '
        '`data/discovery-sources.json` list inside their in-scope sections, new to the curated catalog, the papers, the '
        'source index, the public supplements, the README-scan discoveries, the scope exclusions, the case-coverage '
        'ledger and earlier lead batches. Every lead stays `automated-source-lead` and `unreviewed`: a listing by a '
        'secondary source is not evidence for curation, and no review, translation, runtime test or endorsement is '
        'implied. No other file changes.',
        '',
        f'Sources followed: {captured} captured' + (f", {len(failed)} unavailable this run ({', '.join(failed[:10])})" if failed else '') + '.',
        f"Registry SHA-256 `{provenance['registry_sha256']}`, collector commit `{provenance['head_sha'][:12]}`.",
        '',
        '## Validation',
        '',
        '- [x] `python3 scripts/validate.py` and `python3 scripts/discovery_leads.py` on the default branch plus this batch, before committing.',
        '- [x] The required `validate` and `review` checks are dispatched on this head commit; the ingest merges only after both pass.',
        '',
        f'Ingest attempt {attempt}. This pull request is opened, checked and rebase-merged by the `Followed-source lead '
        'discovery` workflow under the repository\'s automated discovery path (docs/automation.md).',
    ])


def open_or_update_pull(github, default_branch: str, title: str, body: str) -> int:
    owner = github.repository.split('/')[0]
    pulls = github.get(f'pulls?state=open&head={owner}:{leads.INGEST_BRANCH}&base={default_branch}&per_page=10')
    if pulls:
        number = pulls[0]['number']
        github.call('PATCH', f'pulls/{number}', {'title': title, 'body': body})
        return number
    return github.call('POST', 'pulls', {'title': title, 'head': leads.INGEST_BRANCH, 'base': default_branch,
                                         'body': body})[1]['number']


def dispatch_checks(github, default_branch: str, number: int, head_sha: str) -> None:
    github.call('POST', 'actions/workflows/validate.yml/dispatches', {'ref': leads.INGEST_BRANCH})
    github.call('POST', 'actions/workflows/review.yml/dispatches',
                {'ref': default_branch, 'inputs': {'pr_number': str(number), 'head_sha': head_sha}})


def run_validators(root: Path) -> None:
    commands = [[sys.executable, 'scripts/validate.py'], [sys.executable, 'scripts/discovery_leads.py']]
    privacy_tests = sorted(path.stem for path in (root / 'tests').glob('test_privacy*.py'))
    if privacy_tests:
        commands.append([sys.executable, '-m', 'unittest', *(f'tests.{name}' for name in privacy_tests)])
    for command in commands:
        result = subprocess.run(command, cwd=root, capture_output=True, encoding='utf-8')
        if result.returncode:
            tail = (result.stderr or result.stdout).strip().splitlines()[-15:]
            raise RuntimeError(f"{' '.join(command[1:])} failed:\n" + '\n'.join(tail))


def run() -> int:
    """The scheduled workflow path: collect once, then prepare, check and merge on the current default branch."""
    import ingest_discoveries as ingest
    repository, token = os.environ['GITHUB_REPOSITORY'], os.environ['GH_TOKEN']
    default_branch = os.environ['DEFAULT_BRANCH']
    if os.environ.get('GITHUB_REF') != f'refs/heads/{default_branch}':
        raise ValueError('The lead ingest runs only from the default branch')
    collection_path = Path(os.environ.get('LEAD_COLLECTION', CACHE / 'candidates.json'))
    import strict_json
    collection = strict_json.load_path(collection_path)
    provenance = {'repository': repository, 'workflow_path': leads.WORKFLOW_PATH,
                  'run_id': int(os.environ['GITHUB_RUN_ID']), 'run_attempt': int(os.environ['GITHUB_RUN_ATTEMPT']),
                  'event': os.environ['GITHUB_EVENT_NAME'], 'head_sha': os.environ['GITHUB_SHA'],
                  'registry_sha256': collection['registry_sha256']}
    (CACHE / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n', encoding='utf-8')
    github = ingest.GitHub(repository, token)
    started, number = time.monotonic(), None
    for attempt in range(1, ingest.MAX_ATTEMPTS + 1):
        if attempt > 1 and time.monotonic() - started > ingest.JOB_SECONDS - ingest.ATTEMPT_SECONDS:
            raise RuntimeError(f'The default branch kept moving and no time is left for attempt {attempt} (PR #{number}); '
                               'the next scheduled run collects these leads again.')
        base_sha = ingest.refresh_tree(default_branch)
        result = subprocess.run([sys.executable, 'scripts/collect_discovery_leads.py', 'prepare',
                                 '--collection', str(collection_path), '--provenance', str(CACHE / 'provenance.json')],
                                cwd=ROOT, capture_output=True, encoding='utf-8')
        if result.returncode:
            raise RuntimeError('prepare failed:\n' + '\n'.join((result.stderr or result.stdout).splitlines()[-15:]))
        prepared = json.loads(result.stdout.strip().splitlines()[-1])
        ingest.log(f"PREPARE attempt={attempt} base={base_sha[:12]} status={prepared['status']} leads={prepared['records']}")
        if prepared['path'] is None:
            output('status', prepared['status'])
            step_summary([f"Lead ingest: {prepared['status']} (run {provenance['run_id']})."])
            if prepared['status'] == 'budget-reached':
                raise RuntimeError('The lead budget is reached; raising it is a reviewed change (data/discoveries/README.md).')
            return 0
        run_validators(ROOT)
        path = ROOT / prepared['path']
        title = LABEL.format(count=prepared['records'], run=provenance['run_id'])
        head_sha = commit_batch(github, base_sha, path, title)
        number = open_or_update_pull(github, default_branch, title,
                                     pull_request_body(prepared['records'], provenance, path, attempt, collection))
        ingest.log(f'PULL_REQUEST number={number} head={head_sha[:12]}')
        dispatch_checks(github, default_branch, number, head_sha)
        try:
            results = ingest.wait_for_checks(github, head_sha, default_branch, base_sha)
            ingest.log(f'CHECKS {results}')
            if any(conclusion != 'success' for _, conclusion in results.values()):
                raise RuntimeError(f'Required checks failed on {head_sha[:12]}: {results}')
            state = ingest.wait_until_mergeable(github, number, head_sha, default_branch, base_sha)
            ingest.log(f'MERGE_STATE before merge: {state}')
            merged = merge_pull(github, number, head_sha, default_branch, base_sha)
        except ingest.Retry as reason:
            ingest.log(f'RETRY attempt={attempt}: {reason}')
            continue
        github.call('DELETE', f'git/refs/heads/{leads.INGEST_BRANCH}', expected=(204, 422))
        elapsed = round(time.monotonic() - started)
        ingest.log(f"MERGED number={number} sha={merged} leads={prepared['records']} elapsed_seconds={elapsed}")
        for name, value in (('status', 'merged'), ('pr', number), ('merge_sha', merged), ('records', prepared['records'])):
            output(name, value)
        step_summary([f"Lead ingest merged #{number} ({merged[:12]}): {prepared['records']} unreviewed leads "
                      f"from run {provenance['run_id']} in {elapsed} s."])
        return 0
    raise RuntimeError(f'The default branch kept moving; gave up after {ingest.MAX_ATTEMPTS} attempts (PR #{number}).')


def merge_pull(github, number: int, sha: str, default_branch: str, base_sha: str) -> str:
    """Rebase-merge exactly ``sha``, so main keeps the one commit this job wrote, with its own author.

    Squash and merge commits are stamped with the merging account's display name. As in the README ingest,
    a refusal while the branch is still current is asked again a few times; otherwise the attempt is rebuilt.
    """
    import ingest_discoveries as ingest
    for request in range(1, ingest.MERGE_REQUESTS + 1):
        try:
            _, value = github.call('PUT', f'pulls/{number}/merge', {'merge_method': 'rebase', 'sha': sha})
            return value['sha']
        except ingest.ApiError as error:
            if error.status not in (405, 409):
                raise
            moved = github.get(f'branches/{default_branch}')['commit']['sha'] != base_sha
            if moved or error.status == 409 or request == ingest.MERGE_REQUESTS:
                raise ingest.Retry(str(error)) from None
            ingest.log(f'MERGE_REFUSED request={request}: {error}; the branch is current, asking again')
            time.sleep(ingest.MERGE_POLL_SECONDS * request)
    raise AssertionError('unreachable')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest='command', required=True)
    collect_parser = commands.add_parser('collect', help='follow the due sources and write the candidate leads')
    collect_parser.add_argument('--all-sources', action='store_true', help='follow slow sources even when not due')
    collect_parser.add_argument('--output', type=Path, default=CACHE)
    prepare_parser = commands.add_parser('prepare', help='write one lead batch from a collection')
    prepare_parser.add_argument('--collection', type=Path, required=True)
    prepare_parser.add_argument('--provenance', type=Path, required=True)
    commands.add_parser('run', help='the scheduled workflow path')
    args = parser.parse_args()
    import strict_json
    if args.command == 'collect':
        directory = args.output.resolve()
        if not directory.is_relative_to((ROOT / '.cache').resolve()):
            raise ValueError('Collections stay in the ignored .cache directory')
        everything = args.all_sources or os.environ.get('ALL_SOURCES') == 'true'
        collection = collect(Client(os.environ.get('GH_TOKEN', '')), ROOT, everything=everything)
        path = write_collection(collection, directory)
        errors = [result['id'] for result in collection['sources'] if result['status'] == 'error']
        captured = sum(result['status'] == 'captured' for result in collection['sources'])
        line = (f"Followed {captured} source(s), {len(errors)} unavailable; {len(collection['candidates']):,} in-scope "
                f"candidates, {collection['unavailable']} unavailable repositories, {collection['requests']} requests.")
        print(line + (f" Unavailable: {', '.join(errors)}." if errors else ''), flush=True)
        step_summary(['## Followed-source lead discovery', '', line])
        output('collection', path)
        output('collection_ready', 'true')
        return 1 if captured == 0 else 0
    if args.command == 'prepare':
        path, status, count = prepare(strict_json.load_path(args.collection), strict_json.load_path(args.provenance))
        print(json.dumps({'path': path.relative_to(ROOT).as_posix() if path else None, 'status': status, 'records': count}))
        return 0
    return run()


if __name__ == '__main__':
    raise SystemExit(main())
