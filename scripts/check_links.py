#!/usr/bin/env python3
"""Check catalog and benchmark sources; report inconclusive network results separately."""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import json
from pathlib import Path
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urldefrag, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from catalog import ROOT, load_resources
from validate import public_https_error


USER_AGENT = 'Awesome-REA-source-check/1.0 (+https://github.com/reacher-z/Awesome-REA)'
MAX_REDIRECTS = 5


class RedirectRefused(Exception):
    """A redirect that was not followed; nothing was requested from its target."""
    def __init__(self, reason, status, from_url, target):
        super().__init__(reason)
        self.reason, self.status, self.from_url, self.target = reason, status, from_url, target


def without_credentials(url):
    """Drop user information so a refused redirect never copies credentials into a report."""
    try:
        parsed = urlsplit(url)
        return urlunsplit((parsed.scheme, parsed.netloc.rpartition('@')[2], parsed.path, parsed.query, ''))
    except ValueError:
        return None


class PublicRedirect(HTTPRedirectHandler):
    """Apply the catalog's public HTTPS URL check to each redirect target before requesting it.

    The check is syntactic: hostnames are not resolved, so it does not detect a public
    name that resolves to a private address and is no protection against DNS rebinding.
    """
    def redirect_request(self, request, fp, code, message, headers, new_url):
        hops = getattr(request, 'redirect_hops', 0) + 1
        problem = public_https_error(new_url)
        if problem or hops > MAX_REDIRECTS:
            fp.close()
            reason = f'redirect target {problem}' if problem else f'more than {MAX_REDIRECTS} redirects'
            raise RedirectRefused(reason, code, request.full_url, without_credentials(new_url))
        new_request = super().redirect_request(request, fp, code, message, headers, new_url)
        if new_request is not None:
            new_request.redirect_hops = hops
        return new_request


def request_url(original):
    """Use the exact GitHub file revision while avoiding HTML blob endpoints."""
    url = urldefrag(original)[0]
    parsed = urlsplit(url)
    parts = parsed.path.strip('/').split('/')
    if parsed.hostname == 'github.com' and len(parts) >= 5 and parts[2] == 'blob':
        path = '/' + '/'.join(parts[:2] + parts[3:])
        return urlunsplit(('https', 'raw.githubusercontent.com', path, '', ''))
    return url


def source_urls():
    references = defaultdict(list)
    for record in load_resources():
        for field in ('url', 'evidence_url'):
            references[record[field]].append(f"resource:{record['id']}:{field}")
        for url in record.get('additional_evidence_urls', []):
            references[url].append(f"resource:{record['id']}:additional_evidence_urls")
    benchmarks = json.loads((ROOT / 'data/benchmarks.json').read_text(encoding='utf-8'))
    for record in benchmarks:
        for field, urls in [('url', [record['url']]), ('evidence_urls', record['evidence_urls'])]:
            for url in urls:
                references[url].append(f"benchmark:{record['full_name']}:{field}")
    for record in json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8')):
        for field in ('url', 'pdf_url', 'code_url', 'project_url'):
            if record.get(field):
                references[record[field]].append(f"paper:{record['id']}:{field}")
        for url in record['evidence_urls']:
            references[url].append(f"paper:{record['id']}:evidence_urls")
    return references


def fetch_once(url, timeout):
    request = Request(url, headers={'User-Agent': USER_AGENT}, method='GET')
    try:
        with build_opener(PublicRedirect()).open(request, timeout=timeout) as response:
            # Status checking does not require downloading PDFs, archives or full HTML.
            response.read(1)
            return {'http_status': response.status, 'final_url': response.url}
    except RedirectRefused as error:
        # final_url is the last URL actually requested; the refused target was not contacted.
        return {'http_status': error.status, 'final_url': error.from_url,
                'redirect_refused': error.reason, 'refused_redirect_url': error.target}
    except HTTPError as error:
        result = {'http_status': error.code, 'final_url': error.url, 'error': error.reason}
        error.close()
        return result
    except (URLError, TimeoutError, OSError, ValueError) as error:
        return {'http_status': None, 'error': str(error)}


def check_url(original, timeout=15):
    problem = public_https_error(original)
    if problem:
        return {'url': original, 'checked_url': original, 'status': 'inconclusive',
                'reason': problem, 'attempts': []}
    target = request_url(original)
    attempts = [fetch_once(target, timeout)]
    first_status = attempts[0]['http_status']
    if first_status in {404, 410}:
        time.sleep(0.25)
        attempts.append(fetch_once(target, timeout))
    last_status = attempts[-1]['http_status']
    if len(attempts) == 2 and all(attempt['http_status'] in {404, 410} for attempt in attempts):
        status, reason = 'dead', 'HTTP 404/410 confirmed by a second request'
    elif last_status is not None and 200 <= last_status < 300:
        status, reason = 'ok', 'HTTP response received'
    elif 'redirect_refused' in attempts[-1]:
        status, reason = 'inconclusive', 'Redirect not followed: ' + attempts[-1]['redirect_refused']
    else:
        status, reason = 'inconclusive', 'Access restrictions, rate limits or network/server failure do not establish a dead link'
    return {'url': original, 'checked_url': target, 'status': status,
            'http_status': last_status, 'reason': reason, 'attempts': attempts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', dest='json_path', metavar='PATH', type=Path,
                        help='Write a machine-readable report to PATH')
    parser.add_argument('--workers', type=int, default=8, help='Concurrent checks, from 1 to 32 (default: 8)')
    parser.add_argument('--timeout', type=float, default=15, help='Timeout per request in seconds (default: 15)')
    args = parser.parse_args()
    if not 1 <= args.workers <= 32 or not 0 < args.timeout <= 60:
        parser.error('workers must be 1..32 and timeout must be greater than 0 and at most 60')
    try:
        references = source_urls()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'Cannot load source links: {error}', file=sys.stderr)
        return 1
    urls = sorted(references)
    started_at = dt.datetime.now(dt.timezone.utc).isoformat()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(lambda url: check_url(url, args.timeout), urls))
    for result in results:
        result['references'] = references[result['url']]
    counts = Counter(result['status'] for result in results)
    report = {
        'started_at': started_at,
        'finished_at': dt.datetime.now(dt.timezone.utc).isoformat(),
        'checked': len(results),
        'counts': {key: counts[key] for key in ('ok', 'dead', 'inconclusive')},
        'complete': counts['inconclusive'] == 0,
        'all_links_responded': counts['ok'] == len(results),
        'results': results,
    }
    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for result in results:
        if result['status'] != 'ok':
            code = result.get('http_status') or 'network'
            print(f"{result['status'].upper()} [{code}] {result['url']}")
    print(f"Checked {len(results)} links: {counts['ok']} responded, {counts['dead']} confirmed dead, {counts['inconclusive']} inconclusive.")
    if counts['inconclusive']:
        print('Inconclusive links require review; this result is not an all-links-passed claim.')
    if args.json_path:
        print(f'Report: {args.json_path}')
    # Network restrictions are informational; only confirmed 404/410 links fail CI.
    return 1 if counts['dead'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
