#!/usr/bin/env python3
"""Capture bounded public-source link leads; never promote them into the catalog."""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, urlencode, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from urllib.robotparser import RobotFileParser

from review_pr import private_json_locations, private_text

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '.cache/public-artifact-leads'
USER_AGENT = 'AwesomeREA-Discovery/1.0 (+https://github.com/reacher-z/Awesome-REA)'
README_REPOS = ('morluto/rea', 'jammyfu/rea-atlas', 'kaixinbaba/awesome-rea')
WEB_INDEXES = ('https://reamcp.dev/zh-cn/types/x', 'https://madewithrea.com/')
X_EMBED_HOST = 'publish.x.com'
MAX_RESPONSE = 2 * 1024 * 1024
MAX_REPORT = 4 * 1024 * 1024
MAX_REQUESTS, MAX_SECONDS, MAX_LEADS = 32, 240, 3000
MAX_WEB_CASES, MAX_X_POSTS = 8, 6
SCOPE_NOTE = ('Discovery-only URL snapshot, not unique software or curated recommendations. '
              'Source following, not full-web or X keyword search. No upstream code is run.')
SLUG = re.compile(r'[A-Za-z0-9_.-]{1,100}/[A-Za-z0-9_.-]{1,100}\Z')
HEX40 = re.compile(r'[0-9a-f]{40}\Z')
HEX64 = re.compile(r'[0-9a-f]{64}\Z')
RESERVED_OWNERS = {'user-attachments', 'features', 'topics', 'collections', 'marketplace', 'settings',
                   'orgs', 'users', 'sponsors', 'codespaces', 'notifications', 'explore'}
REASONS = {'http-error', 'network-error', 'redirect-blocked', 'response-too-large', 'request-budget',
           'time-budget', 'rate-limited', 'quota-reserve', 'invalid-upstream', 'git-blob-mismatch',
           'robots-disallowed', 'robots-unavailable', 'github-token-unavailable'}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def observed_at():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def repo_slug(value):
    return isinstance(value, str) and bool(SLUG.fullmatch(value)) and all(p not in ('.', '..') for p in value.split('/'))


def web_case(url):
    p = urlsplit(url)
    return ((p.hostname == 'reamcp.dev' and re.fullmatch(r'/(?:zh-cn/)?cases/[A-Za-z0-9_-]+/?', p.path))
            or (p.hostname == 'madewithrea.com' and re.fullmatch(r'/builds/[A-Za-z0-9_-]+/?', p.path)))


def clean_url(value):
    if not isinstance(value, str) or len(value) > 1500 or re.search(r'[\x00-\x20\x7f]', value):
        return None
    try:
        p = urlsplit(value)
        if p.scheme != 'https' or not p.hostname or p.username is not None or p.password is not None or p.port not in (None, 443):
            return None
    except ValueError:
        return None
    return p


def canonical_lead(value):
    p = clean_url(value)
    if p is None:
        return None
    host = p.hostname.lower()
    parts = p.path.strip('/').split('/')
    if host == 'github.com' and len(parts) >= 2 and repo_slug('/'.join(parts[:2])) and parts[0].lower() not in RESERVED_OWNERS:
        repo = '/'.join(parts[:2]).removesuffix('.git')
        if not repo_slug(repo):
            return None
        if len(parts) >= 4 and parts[2] == 'discussions' and re.fullmatch(r'[1-9][0-9]{0,14}', parts[3]):
            result = ('github-discussion', 'https://github.com/' + repo + '/discussions/' + str(int(parts[3])))
        else:
            result = ('github-repository-link', 'https://github.com/' + repo)
    elif host in {'x.com', 'www.x.com', 'twitter.com', 'www.twitter.com'}:
        match = re.fullmatch(r'/(?:[A-Za-z0-9_]{1,15}|i/web)/status/([0-9]{10,20})(?:/(?:photo|video)/[1-9])?/?', p.path)
        if not match or not 0 < int(match[1]) < 2 ** 64:
            return None
        result = ('x-post', 'https://x.com/i/status/' + match[1])
    elif web_case(value):
        result = ('web-case-link', 'https://' + host + p.path.rstrip('/'))
    else:
        return None
    return None if private_text(result[1]) else result


def lead_id(kind, url):
    return digest((url.casefold() if kind.startswith('github-') else url).encode())


def select_case_pages(urls, timestamp):
    """Share the budget across sites and rotate pages each UTC eight-hour slot."""
    point = dt.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    cycle = point.toordinal() * 3 + point.hour // 8
    groups = {}
    for url in sorted(set(urls)):
        groups.setdefault(urlsplit(url).hostname, []).append(url)
    width = max(1, MAX_WEB_CASES // max(1, len(groups)))
    for host, rows in groups.items():
        offset = cycle * width % len(rows)
        groups[host] = rows[offset:] + rows[:offset]
    selected = []
    while len(selected) < MAX_WEB_CASES and any(groups.values()):
        for host in sorted(groups):
            if groups[host] and len(selected) < MAX_WEB_CASES:
                selected.append(groups[host].pop(0))
    return selected


def allowed_fetch(value):
    p = clean_url(value)
    if p is None or p.fragment:
        return False
    if p.hostname == 'api.github.com':
        query = parse_qs(p.query)
        return (p.path == '/graphql' and not p.query) or (
            re.fullmatch(r'/repos/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/readme', p.path)
            and set(query) == {'ref'} and len(query['ref']) == 1 and HEX40.fullmatch(query['ref'][0]))
    if p.hostname in {'publish.twitter.com', X_EMBED_HOST}:
        query = parse_qs(p.query)
        return (p.path == '/oembed' and set(query) == {'url', 'omit_script', 'dnt'}
                and query['omit_script'] == ['true'] and query['dnt'] == ['true']
                and len(query['url']) == 1 and canonical_lead(query['url'][0]) == ('x-post', query['url'][0]))
    return p.hostname in {'reamcp.dev', 'madewithrea.com'} and not p.query and (
        value in WEB_INDEXES or p.path == '/robots.txt' or bool(web_case(value)))


class SourceError(Exception):
    def __init__(self, reason, status=None):
        assert reason in REASONS
        self.reason, self.status = reason, status
        super().__init__(reason)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, newurl):
        return None


class PublicClient:
    """No implicit redirects; credentials are constructed only for the GitHub API."""
    def __init__(self, token='', *, opener=None, clock=time.monotonic):
        self.token, self.opener, self.clock = token, opener or build_opener(NoRedirect()), clock
        self.deadline, self.requests = clock() + MAX_SECONDS, 0
        self.halted, self.remaining = set(), {}

    def fetch(self, url, *, data=None):
        if not allowed_fetch(url) or data is not None and url != 'https://api.github.com/graphql':
            raise SourceError('redirect-blocked')
        for redirect in range(3):
            p = urlsplit(url)
            if self.clock() >= self.deadline:
                raise SourceError('time-budget')
            if self.requests >= MAX_REQUESTS:
                raise SourceError('request-budget')
            if p.hostname in self.halted:
                raise SourceError('rate-limited', 429)
            resource = 'graphql' if p.path == '/graphql' else 'core'
            if p.hostname == 'api.github.com' and self.remaining.get(resource, 100) < 100:
                raise SourceError('quota-reserve')
            headers = {'User-Agent': USER_AGENT}
            if p.hostname == 'api.github.com':
                headers['Accept'] = 'application/vnd.github+json'
                if self.token:
                    headers['Authorization'] = 'Bearer ' + self.token
                if data is not None:
                    headers['Content-Type'] = 'application/json'
            request = Request(url, headers=headers, data=data)
            self.requests += 1
            try:
                with self.opener.open(request, timeout=max(0.1, min(15, self.deadline - self.clock()))) as response:
                    chunks, size = [], 0
                    while True:
                        if self.clock() >= self.deadline:
                            raise SourceError('time-budget')
                        chunk = response.read1(min(65536, MAX_RESPONSE + 1 - size))
                        if not chunk:
                            break
                        chunks.append(chunk); size += len(chunk)
                        if size > MAX_RESPONSE:
                            raise SourceError('response-too-large')
                    raw = b''.join(chunks)
                    remaining = response.headers.get('X-RateLimit-Remaining')
                    if p.hostname == 'api.github.com' and remaining is not None and remaining.isdigit():
                        self.remaining[resource] = int(remaining)
                    if len(raw) > MAX_RESPONSE:
                        raise SourceError('response-too-large')
                    return raw
            except HTTPError as error:
                error.close()
                if error.code in (301, 302, 303, 307, 308):
                    target = urljoin(url, error.headers.get('Location', ''))
                    if (data is not None or redirect == 2 or not allowed_fetch(target)
                            or urlsplit(target).netloc != p.netloc):
                        raise SourceError('redirect-blocked') from None
                    url = target
                    continue
                if error.code == 429 or error.code == 403 and (
                        error.headers.get('Retry-After') or error.headers.get('X-RateLimit-Remaining') == '0'):
                    self.halted.add(p.hostname)
                    raise SourceError('rate-limited', error.code) from None
                raise SourceError('http-error', error.code) from None
            except (URLError, OSError):
                raise SourceError('network-error') from None
        raise SourceError('redirect-blocked')

    def json(self, url, *, data=None):
        try:
            return json.loads(self.fetch(url, data=data))
        except (ValueError, UnicodeError, RecursionError):
            raise SourceError('invalid-upstream') from None


class Links(HTMLParser):
    def __init__(self, text, base):
        super().__init__(convert_charrefs=True)
        self.base, self.urls = base, set()
        self.feed(text)
        self.urls.update(unescape(url) for url in re.findall(r'https://[^\s<>"\]\)]+', text))

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            href = dict(attrs).get('href')
            if href:
                self.urls.add(urljoin(self.base, href))


def capture(identifier, url, channel, raw=None, error=None):
    return {'id': identifier, 'url': url, 'channel': channel, 'status': 'error' if error else 'captured',
            'content_sha256': digest(raw) if raw is not None else None,
            'content_bytes': len(raw) if raw is not None else 0,
            'error': error.reason if error else None, 'http_status': error.status if error else 200}


class Collector:
    def __init__(self, client):
        self.client, self.sources, self.leads, self.robots = client, [], {}, {}

    def add_links(self, text, source, base=None):
        for value in sorted(Links(text, base or source['url']).urls):
            lead = canonical_lead(value)
            if lead is None:
                continue
            kind, url = lead
            identifier = lead_id(kind, url)
            if identifier not in self.leads and len(self.leads) >= MAX_LEADS:
                continue
            item = self.leads.setdefault(identifier, {'id': identifier, 'url': url, 'kind': kind,
                                                     'verification': 'discovery-only', 'source_ids': []})
            if source['id'] not in item['source_ids']:
                item['source_ids'].append(source['id'])

    def github(self):
        if not self.client.token:
            self.sources.append(capture('github-index', 'https://api.github.com/graphql', 'github',
                                        error=SourceError('github-token-unavailable')))
            return
        query = 'query {'
        for index, repo in enumerate(README_REPOS):
            owner, name = repo.split('/')
            query += f'r{index}:repository(owner:"{owner}",name:"{name}") {{ nameWithOwner isPrivate defaultBranchRef {{ target {{ oid }} }} }} '
        query += ('upstream:repository(owner:"morluto",name:"rea") { isPrivate '
                  'discussions(first:30,orderBy:{field:UPDATED_AT,direction:DESC}) { nodes { number body } } '
                  'newest:discussions(first:30,orderBy:{field:CREATED_AT,direction:DESC}) { nodes { number body } } } }')
        try:
            result = self.client.json('https://api.github.com/graphql', data=json.dumps({'query': query}).encode())
            if not isinstance(result.get('data'), dict):
                raise SourceError('invalid-upstream')
        except (SourceError, AttributeError) as error:
            self.sources.append(capture('github-index', 'https://api.github.com/graphql', 'github',
                                        error=error if isinstance(error, SourceError) else SourceError('invalid-upstream')))
            return
        if result.get('errors'):
            self.sources.append(capture('github-partial-query', 'https://api.github.com/graphql', 'github',
                                        error=SourceError('invalid-upstream')))
        for index in range(len(README_REPOS)):
            identifier, url = 'readme-' + str(index), 'https://api.github.com/graphql'
            try:
                node = result['data']['r' + str(index)]
                repo, revision = node['nameWithOwner'], node['defaultBranchRef']['target']['oid']
                if node['isPrivate'] is not False or not repo_slug(repo) or not HEX40.fullmatch(revision):
                    raise SourceError('invalid-upstream')
                response = self.client.json(f'https://api.github.com/repos/{repo}/readme?ref={revision}')
                path = response['path']
                if not re.fullmatch(r'[A-Za-z0-9_./-]+', path) or any(p in ('', '.', '..') for p in path.split('/')):
                    raise SourceError('invalid-upstream')
                url = f'https://github.com/{repo}/blob/{revision}/{path}'
                raw = base64.b64decode(''.join(response['content'].split()), validate=True)
                if len(raw) > MAX_RESPONSE:
                    raise SourceError('response-too-large')
                if hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() != response['sha']:
                    raise SourceError('git-blob-mismatch')
                source = capture(identifier, url, 'github', raw)
                text = raw.decode('utf-8')
                self.add_links(text, source)
                self.sources.append(source)
            except (SourceError, KeyError, TypeError, ValueError, UnicodeError, AttributeError) as error:
                self.sources.append(capture(identifier, url, 'github', error=error if isinstance(error, SourceError) else SourceError('invalid-upstream')))
        nodes = []
        for ordering in ('discussions', 'newest'):
            try:
                upstream = result['data']['upstream']
                if upstream['isPrivate'] is not False:
                    raise TypeError
                rows = upstream[ordering]['nodes']
                if not isinstance(rows, list):
                    raise TypeError
                nodes.extend(rows[:30])
            except (KeyError, TypeError):
                self.sources.append(capture('github-' + ordering, 'https://api.github.com/graphql', 'github',
                                            error=SourceError('invalid-upstream')))
        seen = set()
        for node in nodes:
            if not isinstance(node, dict) or type(node.get('number')) is not int or node['number'] <= 0 or not isinstance(node.get('body'), str):
                continue
            if node['number'] in seen:
                continue
            seen.add(node['number'])
            url = 'https://github.com/morluto/rea/discussions/' + str(node['number'])
            source = capture('discussion-' + str(node['number']), url, 'github', node['body'].encode())
            self.add_links(node['body'] + '\n' + url, source)
            self.sources.append(source)

    def web_page(self, url, identifier):
        host = urlsplit(url).hostname
        if host not in self.robots:
            policy_url = 'https://' + host + '/robots.txt'
            try:
                raw = self.client.fetch(policy_url)
                parser = RobotFileParser(); parser.parse(raw.decode('utf-8').splitlines())
                self.robots[host] = parser
                self.sources.append(capture('robots-' + host, policy_url, 'policy', raw))
            except SourceError as error:
                self.robots[host] = error.status == 404
                self.sources.append(capture('robots-' + host, policy_url, 'policy', error=error))
            except UnicodeError:
                self.robots[host] = False
        policy = self.robots[host]
        try:
            if policy is False:
                raise SourceError('robots-unavailable')
            if policy is not True and not policy.can_fetch(USER_AGENT, url):
                raise SourceError('robots-disallowed')
            raw = self.client.fetch(url)
            source = capture(identifier, url, 'web', raw)
            text = raw.decode('utf-8')
            self.add_links(text, source, url)
            self.sources.append(source)
        except (SourceError, UnicodeError, ValueError) as error:
            self.sources.append(capture(identifier, url, 'web', error=error if isinstance(error, SourceError) else SourceError('invalid-upstream')))

    def collect(self):
        started = observed_at()
        self.github()
        for index, url in enumerate(WEB_INDEXES):
            self.web_page(url, 'web-index-' + str(index))
        pages = {item['url'] for item in self.leads.values() if item['kind'] == 'web-case-link'}
        for url in select_case_pages(pages, started):
            self.web_page(url, 'web-case-' + digest(url.encode())[:16])
        posts = sorted((item['url'] for item in self.leads.values() if item['kind'] == 'x-post'),
                       key=lambda url: int(url.rsplit('/', 1)[-1]), reverse=True)[:MAX_X_POSTS]
        for url in posts:
            identifier = 'x-excerpt-' + url.rsplit('/', 1)[-1]
            endpoint = 'https://' + X_EMBED_HOST + '/oembed?' + urlencode({'url': url, 'omit_script': 'true', 'dnt': 'true'})
            try:
                raw = self.client.fetch(endpoint)
                data = json.loads(raw)
                author = clean_url(data.get('author_url'))
                if (data.get('type') != 'rich' or author is None or author.hostname not in {'x.com', 'twitter.com'}
                        or not isinstance(data.get('html'), str) or not re.search(r'<p\b', data['html'])
                        or '/status/' + url.rsplit('/', 1)[-1] not in data['html']):
                    raise SourceError('invalid-upstream')
                source = capture(identifier, endpoint, 'x', raw)
                self.sources.append(source)
                self.add_links(data['html'] + '\n' + url, source)
            except (SourceError, ValueError, TypeError, AttributeError) as error:
                self.sources.append(capture(identifier, endpoint, 'x', error=error if isinstance(error, SourceError) else SourceError('invalid-upstream')))
        leads = sorted(self.leads.values(), key=lambda item: (item['url'].casefold(), item['url']))
        for item in leads:
            item['source_ids'].sort()
        report = {'schema_version': 1, 'method': 'bounded-public-source-following', 'scope_note': SCOPE_NOTE,
                  'observed_at': started, 'source_commit': os.environ.get('GITHUB_SHA'),
                  'runtime_tested': False, 'sources': self.sources, 'leads': leads}
        report['counts'] = counts(report)
        report['status'] = 'empty' if not leads else 'partial' if report['counts']['source_errors'] else 'captured'
        validate_report(report)
        return report


def counts(report):
    return {'unique_url_leads': len(report['leads']), 'source_attempts': len(report['sources']),
            'successful_source_captures': sum(source['status'] == 'captured' for source in report['sources']),
            'source_errors': sum(source['status'] == 'error' for source in report['sources']),
            'github_repository_links': sum(item['kind'] == 'github-repository-link' for item in report['leads']),
            'discussion_links': sum(item['kind'] == 'github-discussion' for item in report['leads']),
            'web_case_links': sum(item['kind'] == 'web-case-link' for item in report['leads']),
            'x_post_links': sum(item['kind'] == 'x-post' for item in report['leads']),
            'x_original_excerpts': sum(source['channel'] == 'x' and source['status'] == 'captured' for source in report['sources'])}


def validate_report(report):
    assert set(report) == {'schema_version', 'method', 'scope_note', 'observed_at', 'source_commit',
                           'runtime_tested', 'sources', 'leads', 'counts', 'status'}
    assert report['schema_version'] == 1 and report['runtime_tested'] is False
    assert report['method'] == 'bounded-public-source-following' and report['scope_note'] == SCOPE_NOTE
    assert report['source_commit'] is None or HEX40.fullmatch(report['source_commit'])
    assert dt.datetime.fromisoformat(report['observed_at'].replace('Z', '+00:00')).utcoffset() == dt.timedelta(0)
    assert len(report['leads']) <= MAX_LEADS and len(report['sources']) <= 100
    source_ids = {source['id'] for source in report['sources']}
    assert len(source_ids) == len(report['sources'])
    for source in report['sources']:
        assert set(source) == {'id', 'url', 'channel', 'status', 'content_sha256', 'content_bytes', 'error', 'http_status'}
        assert isinstance(source['id'], str) and len(source['id']) <= 100
        assert source['channel'] in {'github', 'web', 'x', 'policy'} and clean_url(source['url'])
        parsed = urlsplit(source['url'])
        if source['channel'] == 'github':
            assert source['url'] == 'https://api.github.com/graphql' or (
                parsed.hostname == 'github.com' and not parsed.query and not parsed.fragment and (
                    re.fullmatch(r'/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/blob/[0-9a-f]{40}/[A-Za-z0-9_./-]+', parsed.path)
                    or canonical_lead(source['url']) == ('github-discussion', source['url'])))
        else:
            assert allowed_fetch(source['url'])
            assert (source['channel'] != 'x' or parsed.hostname in {'publish.twitter.com', X_EMBED_HOST})
            assert (source['channel'] != 'policy' or parsed.path == '/robots.txt')
        assert type(source['content_bytes']) is int and 0 <= source['content_bytes'] <= MAX_RESPONSE
        if source['status'] == 'captured':
            assert HEX64.fullmatch(source['content_sha256']) and source['error'] is None and source['http_status'] == 200
        else:
            assert source['status'] == 'error' and source['error'] in REASONS and source['content_sha256'] is None
            assert source['http_status'] is None or type(source['http_status']) is int and 100 <= source['http_status'] <= 599
    seen = set()
    for item in report['leads']:
        assert set(item) == {'id', 'url', 'kind', 'verification', 'source_ids'}
        assert canonical_lead(item['url']) == (item['kind'], item['url']) and item['verification'] == 'discovery-only'
        assert item['id'] == lead_id(item['kind'], item['url']) and item['id'] not in seen
        seen.add(item['id'])
        assert item['source_ids'] and set(item['source_ids']) <= source_ids and len(set(item['source_ids'])) == len(item['source_ids'])
    assert report['counts'] == counts(report)
    assert report['status'] == ('empty' if not report['leads'] else 'partial' if report['counts']['source_errors'] else 'captured')
    assert not private_json_locations(report), 'Private-looking data withheld'


def write_report(report, directory):
    validate_report(report)
    directory = Path(directory)
    if not directory.resolve().is_relative_to((ROOT / '.cache').resolve()):
        raise ValueError('Lead output must remain in the ignored cache')
    raw = (json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()
    if len(raw) > MAX_REPORT:
        raise ValueError('Lead report exceeds its byte bound')
    directory.mkdir(parents=True, exist_ok=True)
    temporary = directory / 'leads.json.tmp'
    temporary.write_bytes(raw); temporary.replace(directory / 'leads.json')
    receipt = {'schema_version': 1, 'report_file': 'leads.json', 'report_sha256': digest(raw),
               'report_bytes': len(raw), 'source_commit': report['source_commit'], 'observed_at': report['observed_at'],
               'verification': 'discovery-only'}
    temporary = directory / 'receipt.json.tmp'
    temporary.write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    temporary.replace(directory / 'receipt.json')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    try:
        report = Collector(PublicClient(os.environ.get('GH_TOKEN', ''))).collect()
        write_report(report, args.output)
        if os.environ.get('GITHUB_OUTPUT'):
            with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as stream:
                stream.write('artifact_ready=true\n')
        summary = (f"Public artifact leads: {report['counts']['unique_url_leads']} unique URLs; "
                   f"{report['counts']['x_original_excerpts']} X excerpts available; "
                   f"{report['counts']['source_errors']} source errors; status={report['status']}.\n")
        print(summary + SCOPE_NOTE, flush=True)
        if os.environ.get('GITHUB_STEP_SUMMARY'):
            with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as stream:
                stream.write('## Public artifact discovery\n\n' + summary + '\n' + SCOPE_NOTE + '\n')
        return 1 if report['status'] == 'empty' else 0
    except (AssertionError, ValueError, KeyError, TypeError, OSError, RecursionError):
        print('Public artifact discovery stopped: bounded-data validation failed. No catalog publication was made.', flush=True)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
