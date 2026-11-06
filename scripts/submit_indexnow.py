#!/usr/bin/env python3
"""Notify IndexNow of the deployed owned-site sitemap; dry run unless --submit."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from build_manifest import (CONTROL_FILES, FONT_SUFFIXES, HTML_NORMALIZATION, MANIFEST_NAME,
                            PRIVATE_NAMES, html_digest, read_build_manifest)
from sitemaps import sitemap_files, sitemap_urls

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://awesomerea.org'
ENDPOINT = 'https://api.indexnow.org/indexnow'
MAX_HTML_BYTES = 16 * 1024 * 1024
LIVE_WORKERS = 4
MAX_PREVIOUS_MANIFEST_BYTES = 8_000_000


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
    # The sitemap index and every section sitemap it names.
    for name in sitemap_files(output, ORIGIN):
        if fetch_bytes(ORIGIN + '/' + name, 8_000_000).strip() != (output / name).read_bytes().strip():
            raise ValueError('The deployed sitemap differs from this build: /' + name)
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


def read_previous_manifest(path, expected_sha256):
    """Read one explicitly pinned baseline; never open its referenced file paths."""
    if not re.fullmatch(r'[a-f0-9]{64}', expected_sha256 or ''):
        raise ValueError('Previous manifest requires an explicit SHA-256 digest')
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError('Previous manifest must be a regular file, not a symbolic link')
    with path.open('rb') as handle:
        raw = handle.read(MAX_PREVIOUS_MANIFEST_BYTES + 1)
    if len(raw) > MAX_PREVIOUS_MANIFEST_BYTES:
        raise ValueError('Previous manifest exceeds the size limit')
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError('Previous manifest does not match its expected SHA-256')

    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Previous manifest contains duplicate JSON keys')
            result[key] = value
        return result

    def invalid_constant(_):
        raise ValueError('Previous manifest contains a non-JSON number')

    try:
        manifest = json.loads(raw.decode('utf-8'), object_pairs_hook=unique, parse_constant=invalid_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError):
        raise ValueError('Previous manifest must be valid UTF-8 JSON') from None
    if (not isinstance(manifest, dict)
            or set(manifest) != {'schema_version', 'algorithm', 'html_normalization', 'files'}
            or type(manifest['schema_version']) is not int or manifest['schema_version'] != 1
            or manifest['algorithm'] != 'sha256' or manifest['html_normalization'] != HTML_NORMALIZATION
            or not isinstance(manifest['files'], dict)):
        raise ValueError('Previous manifest schema or HTML normalization is incompatible')
    files = manifest['files']
    if not {'index.html', 'sitemap.xml'} <= files.keys():
        raise ValueError('Previous manifest lacks its homepage or sitemap entry')
    for name, item in files.items():
        relative = PurePosixPath(name)
        if (not re.fullmatch(r'[A-Za-z0-9_-]+(?:[A-Za-z0-9_./-]*[A-Za-z0-9_-])?', name)
                or relative.as_posix() != name or relative.is_absolute()
                or any(part.startswith('.') or part in {'node_modules', '__pycache__'} for part in relative.parts)
                or PRIVATE_NAMES.fullmatch(relative.name) or name in CONTROL_FILES or name == MANIFEST_NAME
                or relative.suffix.lower() in FONT_SUFFIXES | {'.pem', '.key', '.p12', '.pfx'}):
            raise ValueError('Previous manifest contains an unsafe public file path')
        required = {'sha256', 'bytes'} | ({'html_sha256'} if relative.suffix.lower() == '.html' else set())
        if (not isinstance(item, dict) or set(item) != required
                or type(item['bytes']) is not int or item['bytes'] < 0
                or any(not isinstance(item[key], str) or not re.fullmatch(r'[a-f0-9]{64}', item[key])
                       for key in required - {'bytes'})):
            raise ValueError('Previous manifest contains invalid file hashes or sizes')
    return manifest


def source_revision():
    """Report checkout context without paths/account details or claiming it binds a dirty build."""
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, stderr=subprocess.DEVNULL).decode().strip()
        if not re.fullmatch(r'[a-f0-9]{40}', commit):
            return None
        status = subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, stderr=subprocess.DEVNULL)
        return {'commit': commit, 'worktree_clean': not bool(status)}
    except (OSError, subprocess.CalledProcessError):
        return None


def manifest_delta(manifest, previous, urls):
    """Select only current canonical URLs; removed manifest files are not historical URLs."""
    current, before = manifest['files'], previous['files']
    added, updated, unchanged = [], [], []
    canonical_files = {canonical_html_file(url) for url in urls}
    for url in sorted(urls):
        name = canonical_html_file(url)
        if name not in before:
            added.append(url)
        elif current[name]['html_sha256'] != before[name]['html_sha256']:
            updated.append(url)
        else:
            unchanged.append(url)
    non_html = {'added': [], 'updated': [], 'removed': []}
    other_html = {'added': [], 'updated': []}
    for name in sorted(set(current) | set(before)):
        if PurePosixPath(name).suffix.lower() == '.html':
            if name in current and name not in canonical_files:
                if name not in before:
                    other_html['added'].append(name)
                elif current[name]['html_sha256'] != before[name]['html_sha256']:
                    other_html['updated'].append(name)
        elif name not in before:
            non_html['added'].append(name)
        elif name not in current:
            non_html['removed'].append(name)
        elif current[name] != before[name]:
            non_html['updated'].append(name)
    selected = sorted(added + updated)
    review_assets = not selected and any(non_html.values())
    return {
        'mode': 'delta', 'status': 'non-html-changes-require-review' if review_assets else
        'ready' if selected else 'no-current-canonical-html-changes',
        'counts': {'current_canonical': len(urls), 'added': len(added), 'updated': len(updated),
                   'unchanged': len(unchanged), 'selected': len(selected)},
        'added': added, 'updated': updated, 'unchanged': unchanged, 'selected': selected,
        'removed_html_candidates': sorted(name for name in set(before) - set(current)
                                          if PurePosixPath(name).suffix.lower() == '.html'),
        'other_current_html_changes': other_html, 'non_html_changes': non_html,
        'non_html_changes_require_review': review_assets,
        'removed_candidate_policy': 'File names only; prior canonical identity and live deletion/redirect status are unknown. No removal notifications are inferred.',
    }


def write_receipt(path, *, manifest_sha256, sitemap_sha256, mode, selected, status):
    """Record what this run notified, so the next automatic run can diff against this build."""
    if path is None:
        return
    receipt = {'schema_version': 1, 'site': ORIGIN, 'manifest_sha256': manifest_sha256, 'sitemap_sha256': sitemap_sha256,
               'mode': mode, 'submitted_urls': len(selected), 'indexnow_status': status,
               'recorded_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'source_checkout': source_revision()}
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--submit', action='store_true', help='Verify deployed ownership, manifest and canonical HTML, then submit their URLs')
    parser.add_argument('--previous-manifest', type=Path, help='Optional reviewed previous build-manifest JSON')
    parser.add_argument('--previous-manifest-sha256', help='Expected SHA-256 from the reviewed baseline receipt')
    parser.add_argument('--dist', type=Path, default=ROOT / 'dist', help='Built site to verify and notify (default: dist/)')
    parser.add_argument('--automatic', action='store_true', help='Unattended run: non-HTML changes alone notify nothing and succeed')
    parser.add_argument('--receipt', type=Path, help='Write a JSON receipt of a completed submission or of an empty delta')
    args = parser.parse_args()
    if (args.previous_manifest is None) != (args.previous_manifest_sha256 is None):
        parser.error('--previous-manifest and --previous-manifest-sha256 must be supplied together')
    # This is intentionally public ownership proof, not an account credential.
    key = (ROOT / 'site/indexnow.txt').read_text(encoding='utf-8').strip()
    if not re.fullmatch(r'[a-f0-9]{32}', key):
        raise ValueError('Invalid public IndexNow verification key')
    output = args.dist
    manifest = read_build_manifest(output)
    manifest_sha256 = hashlib.sha256((output / MANIFEST_NAME).read_bytes()).hexdigest()
    manifest_id = manifest_sha256[:16]
    sitemap = b''.join((output / name).read_bytes() for name in sitemap_files(output, ORIGIN))
    urls = sitemap_urls(output, ORIGIN)
    if not urls or len(urls) > 10000 or len(urls) != len(set(urls)):
        raise ValueError('Sitemap URL count or uniqueness is invalid')
    for url in urls:
        relative = canonical_html_file(url)
        if 'html_sha256' not in manifest['files'].get(relative, {}):
            raise ValueError('A sitemap page is missing from the local build manifest')
    selected = urls
    if args.previous_manifest is not None:
        previous = read_previous_manifest(args.previous_manifest, args.previous_manifest_sha256)
        report = manifest_delta(manifest, previous, urls)
        report.update(current_manifest_sha256=manifest_sha256,
                      previous_manifest_sha256=args.previous_manifest_sha256,
                      current_sitemap_sha256=hashlib.sha256(sitemap).hexdigest(),
                      source_checkout=source_revision(), dry_run=not args.submit)
        selected = report['selected']
        # Keep large unchanged inventories and the duplicate selected list out of CLI output.
        summary = {key: value for key, value in report.items() if key not in {'unchanged', 'selected'}}
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        if not args.submit:
            return 0
        if not selected:
            print('No current canonical HTML changes selected; no notification sent.')
            if report['non_html_changes_require_review'] and not args.automatic:
                print('Non-HTML changes require review of affected pages; full-sitemap mode remains available.')
                return 1
            if args.receipt is not None:
                # A receipt makes this build the next baseline, so the deployment must be this build.
                verify_live_build(output, urls, manifest, key)
                write_receipt(args.receipt, manifest_sha256=manifest_sha256, sitemap_sha256=hashlib.sha256(sitemap).hexdigest(),
                              mode='delta', selected=[], status=None)
            return 0
    elif not args.submit:
        print(f'Dry run: {len(urls)} canonical URLs; manifest {manifest_id}. Use --submit after deployment.')
        return 0
    payload = {'host': 'awesomerea.org', 'key': key, 'keyLocation': ORIGIN + '/indexnow.txt', 'urlList': selected}
    # Delta mode narrows only the notification, never the deployed-build preflight.
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
    print(f'IndexNow HTTP {status}: {len(selected)} URLs submitted for manifest {manifest_id}. ' + ('Key validation pending. ' if status == 202 else '') + 'Receipt does not confirm indexing.')
    write_receipt(args.receipt, manifest_sha256=manifest_sha256, sitemap_sha256=hashlib.sha256(sitemap).hexdigest(),
                  mode='delta' if args.previous_manifest is not None else 'full', selected=selected, status=status)
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
