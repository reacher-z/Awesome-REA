#!/usr/bin/env python3
"""Notify IndexNow of the deployed owned-site sitemap; dry run unless --submit."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from build_manifest import MANIFEST_NAME, html_digest, read_build_manifest

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://awesomerea.org'
ENDPOINT = 'https://api.indexnow.org/indexnow'
MAX_HTML_BYTES = 16 * 1024 * 1024
LIVE_WORKERS = 4


def fetch_bytes(url, limit):
    request = Request(url, headers={'User-Agent': 'AwesomeREA-IndexNow/1.0',
                                   'Accept-Encoding': 'identity', 'Cache-Control': 'no-cache'})
    with urlopen(request, timeout=30) as response:
        if response.geturl() != url:
            raise ValueError('A deployed verification resource redirected away from its canonical URL')
        if response.status != 200:
            raise ValueError('A deployed verification resource did not return HTTP 200')
        content = response.read(limit + 1)
    if len(content) > limit:
        raise ValueError('A deployed verification resource exceeded its size limit')
    return content


def canonical_html_file(url):
    if not isinstance(url, str) or not url:
        raise ValueError('A sitemap URL is missing or invalid')
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or parsed.netloc != 'awesomerea.org' or parsed.query or parsed.fragment:
        raise ValueError('Only canonical HTTPS URLs on the owned domain may be submitted')
    path = unquote(parsed.path)
    if '\\' in path or '..' in PurePosixPath(path).parts:
        raise ValueError('Invalid canonical page path')
    relative = path.lstrip('/')
    if not relative or path.endswith('/'):
        return relative + 'index.html'
    if relative.endswith('.html'):
        return relative
    return relative + '/index.html'


def verify_live_build(output, urls, manifest, key):
    """Require the deployed manifest and every canonical page to match this build."""
    output = Path(output)
    expected_manifest = (output / MANIFEST_NAME).read_bytes()
    if fetch_bytes(ORIGIN + '/indexnow.txt', 1024).strip() != key.encode():
        raise ValueError('The deployed public ownership proof differs from this build')
    if fetch_bytes(ORIGIN + '/sitemap.xml', 2_000_000).strip() != (output / 'sitemap.xml').read_bytes().strip():
        raise ValueError('The deployed sitemap differs from this build')
    if fetch_bytes(ORIGIN + '/' + MANIFEST_NAME, 8_000_000) != expected_manifest:
        raise ValueError('The deployed manifest differs from this build; deploy before submitting')

    def verify_page(url):
        relative = canonical_html_file(url)
        entry = manifest['files'].get(relative)
        if not entry or 'html_sha256' not in entry:
            raise ValueError('A canonical HTML page is absent from the build manifest')
        if entry['bytes'] > MAX_HTML_BYTES:
            raise ValueError('A canonical HTML page exceeds the verification size limit')
        live = fetch_bytes(url, MAX_HTML_BYTES)
        if html_digest(live) != entry['html_sha256']:
            raise ValueError('Deployed HTML differs from this build: ' + urlsplit(url).path)

    with ThreadPoolExecutor(max_workers=LIVE_WORKERS) as pool:
        for _ in pool.map(verify_page, urls):
            pass
    if fetch_bytes(ORIGIN + '/' + MANIFEST_NAME, 8_000_000) != expected_manifest:
        raise ValueError('The deployed manifest changed during verification; retry after deployment settles')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--submit', action='store_true', help='Verify deployed ownership, manifest and canonical HTML, then submit their URLs')
    args = parser.parse_args()
    # This is intentionally public ownership proof, not an account credential.
    key = (ROOT / 'site/indexnow.txt').read_text(encoding='utf-8').strip()
    if not re.fullmatch(r'[a-f0-9]{32}', key):
        raise ValueError('Invalid public IndexNow verification key')
    output = ROOT / 'dist'
    manifest = read_build_manifest(output)
    manifest_id = hashlib.sha256((output / MANIFEST_NAME).read_bytes()).hexdigest()[:16]
    sitemap = (output / 'sitemap.xml').read_bytes()
    urls = [element.text for element in ET.fromstring(sitemap).findall('{*}url/{*}loc')]
    if not urls or len(urls) > 10000 or len(urls) != len(set(urls)):
        raise ValueError('Sitemap URL count or uniqueness is invalid')
    for url in urls:
        relative = canonical_html_file(url)
        if 'html_sha256' not in manifest['files'].get(relative, {}):
            raise ValueError('A sitemap page is missing from the local build manifest')
    payload = {'host': 'awesomerea.org', 'key': key, 'keyLocation': ORIGIN + '/indexnow.txt', 'urlList': urls}
    if not args.submit:
        print(f'Dry run: {len(urls)} canonical URLs; manifest {manifest_id}. Use --submit after deployment.')
        return 0
    verify_live_build(output, urls, manifest, key)
    request = Request(ENDPOINT, data=json.dumps(payload).encode(), method='POST', headers={'Content-Type': 'application/json; charset=utf-8', 'User-Agent': 'AwesomeREA-IndexNow/1.0'})
    try:
        with urlopen(request, timeout=30) as response:
            status = response.status
    except HTTPError as error:
        print(f'IndexNow returned HTTP {error.code}; submission was not accepted.')
        return 1
    except (URLError, TimeoutError, OSError):
        print('IndexNow receipt is unconfirmed; response unavailable. No automatic retry was attempted.')
        return 1
    if status not in (200, 202):
        print(f'IndexNow returned HTTP {status}; submission was not confirmed.')
        return 1
    print(f'IndexNow HTTP {status}: {len(urls)} URLs submitted for manifest {manifest_id}. ' + ('Key validation pending. ' if status == 202 else '') + 'Receipt does not confirm indexing.')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except HTTPError as error:
        print(f'Deployment verification returned HTTP {error.code}; no submission completed.')
        raise SystemExit(1)
    except (URLError, TimeoutError):
        print('Deployment verification could not reach a required endpoint; no submission completed.')
        raise SystemExit(1)
    except ET.ParseError:
        print('The public build sitemap is malformed; rebuild the site before submitting.')
        raise SystemExit(1)
    except (OSError, ValueError) as error:
        print(str(error) if isinstance(error, ValueError) else 'Required public build files could not be read; rebuild the site.')
        raise SystemExit(1)
