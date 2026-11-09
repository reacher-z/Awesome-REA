#!/usr/bin/env python3
"""Compare scripts/validate_site_old.py (the base branch) with scripts/validate_site.py on one built site.

Writes equivalence/old/* and equivalence/new/*; the two trees must be identical:
  parsers.txt   canonical state (or error) of every parser on every built HTML file
  main-*.txt    the outcome and output of main() on the clean build and on each seeded-bad copy
"""
import contextlib
import hashlib
import io
import json
import multiprocessing
import os
from pathlib import Path
import re
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from html.parser import HTMLParser  # noqa: E402
import validate_site_old as old  # noqa: E402
import validate_site as new  # noqa: E402
from sitemaps import sitemap_urls  # noqa: E402

DIST = ROOT / 'dist'
COPY = ROOT / 'dist-seeded'
OUT = ROOT / 'equivalence'
TOKENIZER = {*vars(HTMLParser()), '_HTMLParser__starttag_text'}
NAMES = ('Page', 'VisibleBreadcrumb', 'FooterLinks', 'Stylesheets', 'DocumentTitle', 'PageResources')


def canonical(value):
    if isinstance(value, dict):
        if all(isinstance(k, str) for k in value):
            return {k: canonical(value[k]) for k in sorted(value)}
        return {'dict': sorted(([canonical(k), canonical(v)] for k, v in value.items()), key=repr)}
    if isinstance(value, (list, tuple)):
        return [canonical(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return {'set': sorted((canonical(item) for item in value), key=repr)}
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return repr(value)


def describe(parser, error):
    if error is not None:
        return f'error {type(error).__name__}: {error}'
    state = {key: value for key, value in vars(parser).items() if key not in TOKENIZER}
    return 'state ' + hashlib.sha256(json.dumps(canonical(state), sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def old_parse(job):
    path, sitemap_page = job
    lines = []
    for name in NAMES:
        if name == 'Page' and not sitemap_page:
            continue
        try:
            parser, error = getattr(old, name)(path.read_text(encoding='utf-8')), None
        except Exception as caught:
            parser, error = None, caught
        lines.append(f'{path.relative_to(DIST)} {name} {describe(parser, error)}')
    return lines


def new_parse(job):
    path, sitemap_page = job
    _, results = new._parse_file(job)
    return [f'{path.relative_to(DIST)} {name} {describe(*results[getattr(new, name)])}'
            for name in NAMES if name != 'Page' or sitemap_page]


def parser_states():
    urls = sitemap_urls(DIST, new.ORIGIN)
    sitemap_files = {DIST / new.urlsplit(url).path.lstrip('/') / 'index.html' for url in urls}
    jobs = [(path, path in sitemap_files) for path in sorted({*DIST.rglob('*.html'), *sitemap_files})]
    with multiprocessing.get_context('fork').Pool() as pool:
        for side, function in (('old', old_parse), ('new', new_parse)):
            started = time.monotonic()
            lines = [line for chunk in pool.imap(function, jobs, chunksize=64) for line in chunk]
            (OUT / side / 'parsers.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
            print(f'{side} parsers: {len(jobs)} files, {len(lines)} parses, {time.monotonic() - started:.0f}s', flush=True)


def run_main(module, output):
    module.OUTPUT = output
    captured = io.StringIO()
    started = time.monotonic()
    try:
        with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(captured):
            module.main()
        outcome = 'passed'
    except BaseException as error:  # noqa: BLE001 - the outcome is what is compared
        outcome = f'{type(error).__name__}: {error}'
    return outcome, captured.getvalue().replace(str(output), '<dist>'), time.monotonic() - started


def replace(path, text):
    """Write a seeded file without touching the hard-linked original."""
    temporary = path.with_name(path.name + '.seeded')
    temporary.write_text(text, encoding='utf-8')
    os.replace(temporary, path)


def sub_once(pattern, replacement, text, flags=0):
    changed, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    assert count == 1, f'Seed pattern not found: {pattern}'
    return changed


def resource_pages():
    return sorted(path for path in (COPY / 'resources').glob('*/index.html'))


def seeds():
    """(name, file, new text or None for a new file, created text) for each seeded-bad copy."""
    first, second = resource_pages()[:2]
    page = first.read_text(encoding='utf-8')
    other = second.read_text(encoding='utf-8')
    not_found = (COPY / '404.html').read_text(encoding='utf-8')
    stylesheet = sorted((COPY / 'assets').glob('*.css'))[0]
    title = re.search(r'<title>.*?</title>', page, re.S)[0]
    yield 'unresolved-template', first, sub_once(r'</main>', '{{SEEDED}}</main>', page)
    yield 'duplicate-attribute', first, sub_once(r'<main\b', '<main data-seed="1" data-seed="2"', page)
    yield 'inline-style', first, sub_once(r'<p>', '<p style="color:red">', page)
    yield 'asset-content', stylesheet, stylesheet.read_text(encoding='utf-8') + '/* seeded */\n'
    yield 'breadcrumb-text', first, sub_once(r'(<nav aria-label="Breadcrumb">.*?<a [^>]*>)([^<]+)', r'\g<1>\g<2> seeded', page, re.S)
    yield 'unlinked-stylesheet', COPY / 'seeded.css', 'p{}\n'
    yield 'duplicate-title', second, sub_once(r'<title>.*?</title>', title.replace('\\', '\\\\'), other, re.S)
    yield 'footer-text', COPY / '404.html', sub_once(r'(<footer class="site-footer".*?<a [^>]*>)([^<]+)', r'\g<1>\g<2> seeded', not_found, re.S)
    yield 'footer-parser-error', COPY / '404.html', sub_once(r'<footer class="site-footer"', '<footer class></footer><footer class="site-footer"', not_found)
    yield 'stylesheet-parser-error', COPY / '404.html', sub_once(r'</head>', '<link rel></head>', not_found)


def main():
    for side in ('old', 'new'):
        (OUT / side).mkdir(parents=True, exist_ok=True)
    parser_states()
    shutil.rmtree(COPY, ignore_errors=True)
    os.system(f'cp -al "{DIST}" "{COPY}"')
    scenarios = [('clean', None, None)] + list(seeds())
    for name, path, text in scenarios:
        existed = path is not None and path.exists()
        if path is not None:
            replace(path, text)
        try:
            for side, module in (('old', old), ('new', new)):
                outcome, output, seconds = run_main(module, COPY)
                (OUT / side / f'main-{name}.txt').write_text(outcome + '\n' + output, encoding='utf-8')
                print(f'{name} {side} {seconds:.0f}s: {outcome[:200]}', flush=True)
        finally:
            if path is not None:
                path.unlink()
                if existed:
                    os.link(DIST / path.relative_to(COPY), path)


if __name__ == '__main__':
    main()
