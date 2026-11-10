"""Check the agent formats of a built site: page twins, the static API, JSON feeds and the llms files.

validate_site.py calls ``validate_agent_formats`` after its page checks; each function here also runs on
its own in the tests.
"""
from __future__ import annotations

import csv
import hashlib
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from agent_formats import (COLLECTION_JSON, MARKDOWN, MARKDOWN_TYPE, JSON_TYPE, json_text, paper_record,
                           record_json_route, resource_record)
from build_api import API_PATH, API_VERSION, CSV_COLUMNS, ENDPOINTS, paper_api_record, snapshot_time
from build_feed import FEED_PATHS, JSON_FEED_PATHS, JSON_FEED_VERSION
from build_paper_pages import AUTHORS_OMITTED, authors_omitted
from json_schema_check import errors as schema_errors

ORIGIN = 'https://awesomerea.org'
LLMS_LIMIT = 50_000
# Pages whose twins the site promises: every listing, category and entry page in both languages.
TWIN_LISTINGS = ('/resources/', '/cases/', '/papers/', '/browse/', '/api/')
EXPECTED_HEADERS = {
    '/api/*': {'access-control-allow-origin': '*', 'cache-control': 'no-cache, must-revalidate'},
    '/api/v1/*.csv': {'content-type': 'text/csv; charset=utf-8'},
    '/*/index.md': {'link': '<https://awesomerea.org/:splat/>; rel="canonical"'},
    '/AGENTS.md': {'content-type': 'text/markdown; charset=utf-8'},
    '/agents.md': {'content-type': 'text/markdown; charset=utf-8'},
    '/agents.txt': {'content-type': 'text/plain; charset=utf-8'},
    '/llms-full.txt': {'content-type': 'text/plain; charset=utf-8'},
    '/zh/llms-full.txt': {'content-type': 'text/plain; charset=utf-8'},
    '/feed.json': {'content-type': 'application/feed+json; charset=utf-8'},
    '/zh/feed.json': {'content-type': 'application/feed+json; charset=utf-8'},
}


class Alternates(HTMLParser):
    """The format alternates a page's <head> declares: (type, href) pairs without hreflang."""

    def __init__(self, text):
        super().__init__()
        self.formats = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'link' and values.get('rel') == 'alternate' and 'hreflang' not in values and values.get('type') in (MARKDOWN_TYPE, JSON_TYPE):
            self.formats.append((values['type'], values.get('href')))


def expected_twins(routes, resources, papers):
    """Map each page route that must have twins to its (Markdown path, JSON path or None)."""
    expected = {}
    for prefix in ('', '/zh'):
        for kind, records in (('resource', resources), ('paper', papers)):
            for record in records:
                expected[f"{prefix}/{kind}s/{record['id']}/"] = (f"{prefix}/{kind}s/{record['id']}/{MARKDOWN}", record_json_route(kind, record['id']))
        for listing in TWIN_LISTINGS:
            expected[prefix + listing] = (prefix + listing + MARKDOWN, None)
    for route in routes:
        match = re.fullmatch(r'(?:/zh)?/browse/([a-z0-9-]+)/', route)
        if match:
            expected[route] = (route + MARKDOWN, f'/browse/{match[1]}/{COLLECTION_JSON}')
    return {route: twins for route, twins in expected.items() if route in routes or not route.startswith(('/browse/', '/zh/browse/'))}


def validate_twins(output, routes, resources, papers):
    """Every promised twin is linked from its page, exists, names its page and matches its record."""
    output = Path(output)
    routes = set(routes)
    for route, (markdown, json_path) in expected_twins(routes, resources, papers).items():
        assert route in routes, f'A page with twins is missing from the sitemap: {route}'
        formats = Alternates((output / route.lstrip('/') / 'index.html').read_text(encoding='utf-8')).formats
        linked = dict(formats)
        assert len(formats) == len(linked), f'Duplicate format alternates: {route}'
        assert linked.get(MARKDOWN_TYPE) == markdown, f'Page must link its Markdown twin {markdown}: {route}'
        if json_path:
            assert linked.get(JSON_TYPE) == json_path, f'Page must link its JSON twin {json_path}: {route}'
        text = (output / markdown.lstrip('/')).read_text(encoding='utf-8')
        assert text.split('\n---\n\n', 1)[-1].startswith('# ') and f'<{ORIGIN}{route}>' in text, f'Markdown twin must open with a heading and name its page: {markdown}'
    # Every other indexed page links a twin too (page_twins.py writes the ones no builder does).
    for route in routes:
        page = output / route.lstrip('/') / 'index.html'
        if not route.endswith('/') or not page.is_file():
            continue
        markdown = dict(Alternates(page.read_text(encoding='utf-8')).formats).get(MARKDOWN_TYPE)
        assert markdown == route + MARKDOWN, f'Indexed page must link its Markdown twin {route}{MARKDOWN}: {route}'
        text = (output / markdown.lstrip('/')).read_text(encoding='utf-8')
        assert text.split('\n---\n\n', 1)[-1].startswith('# ') and f'<{ORIGIN}{route}>' in text, f'Markdown twin must open with a heading and name its page: {markdown}'
    resources_by_id, papers_by_id = {row['id']: row for row in resources}, {row['id']: row for row in papers}
    for kind, records, project in (('resource', resources_by_id, resource_record), ('paper', papers_by_id, paper_record)):
        for identifier, record in records.items():
            path = output / record_json_route(kind, identifier).lstrip('/')
            assert path.read_text(encoding='utf-8') == json_text(project(record, ORIGIN)), f'record.json differs from its record: {identifier}'
            for prefix, zh in (('', False), ('/zh', True)):
                text = (output / f'{prefix.lstrip("/")}/{kind}s/{identifier}/{MARKDOWN}'.lstrip('/')).read_text(encoding='utf-8')
                assert text.startswith('---\n') and '\n---\n\n# ' in text, f'Markdown twin needs YAML front matter: {prefix}/{kind}s/{identifier}/'
                text = text.split('\n---\n\n', 1)[1]
                name = (record.get('name_zh') or record['name']) if kind == 'resource' and zh else record.get('name') if kind == 'resource' else record['title_zh' if zh else 'title']
                assert text.startswith(f'# {" ".join(name.split())}\n'), f'Markdown twin heading differs from the entry: {prefix}/{kind}s/{identifier}/'
                assert ' '.join(record[f'description_{"zh" if zh else "en"}'].split()) in text, f'Markdown twin lost the description: {identifier}'
                if kind == 'paper' and authors_omitted(record):
                    assert AUTHORS_OMITTED[zh] in text, f'Markdown twin must send readers to the paper for its authors: {identifier}'
    for path in output.rglob(MARKDOWN):
        route = '/' + path.parent.relative_to(output).as_posix().strip('.').strip('/') + '/'
        route = route.replace('//', '/')
        if path.parent == output / 'downloads':
            continue
        assert route in routes, f'Markdown twin without an indexed page: /{path.relative_to(output).as_posix()}'
        if path.parent != output / 'downloads':
            head = path.read_text(encoding='utf-8').split('\n---\n', 1)[0]
            assert re.fullmatch(r'---\ntitle: ".+"\nurl: https://awesomerea\.org/\S*\nupdated: \d{4}-\d{2}-\d{2}\ntype: [a-z]+', head), f'Markdown twin needs title, url, updated and type front matter: /{path.relative_to(output).as_posix()}'
    for route in routes:
        match = re.fullmatch(r'/browse/([a-z0-9-]+)/', route)
        if match:
            document = json.loads((output / route.lstrip('/') / COLLECTION_JSON).read_text(encoding='utf-8'))
            assert document['category'] == match[1] and document['count'] == len(document['repositories']), f'Category JSON count mismatch: {route}'
            assert document['verification'] == 'automated-readme-scan', f'Category JSON must label the automatic index: {route}'


def validate_api(output, resources, papers, *, repository_document=None, discovery_queue=None, lead_queue=None):
    """Every API file follows schema.json, carries version and generated_at and matches the catalog."""
    folder = Path(output) / API_PATH.strip('/')
    schema = json.loads((folder / 'schema.json').read_text(encoding='utf-8'))
    generated_at = snapshot_time(resources, papers, repository_document, discovery_queue, lead_queue)
    documents = {}
    for name in (*ENDPOINTS, 'index'):
        document = json.loads((folder / f'{name}.json').read_text(encoding='utf-8'))
        assert document.get('version') == API_VERSION and document.get('generated_at') == generated_at, f'API file needs version {API_VERSION} and the data generated_at: {name}.json'
        definition = document['schema'].removeprefix(f'{ORIGIN}{API_PATH}schema.json#/$defs/')
        assert definition in schema['$defs'], f'API file names an unknown schema definition: {name}.json'
        problems = schema_errors(document, schema['$defs'][definition], schema)
        assert not problems, f'{name}.json does not follow schema.json: ' + '; '.join(problems[:5])
        documents[name] = document
    assert [row['id'] for row in documents['resources']['resources']] == [row['id'] for row in resources], 'resources.json must list every curated resource in catalog order'
    assert documents['resources']['resources'] == [resource_record(row, ORIGIN) for row in resources], 'resources.json differs from the curated records'
    assert documents['papers']['papers'] == [paper_api_record(row, ORIGIN) for row in papers], 'papers.json differs from the bibliography'
    curated = {row['id'] for row in resources} | {row['id'] for row in papers}
    assert all(row['review_status'] == 'unreviewed' and row['id'] not in curated for row in documents['candidates']['candidates']), 'Candidates must be unreviewed and never curated records'
    changes = documents['changes']
    assert changes['window_end'] == generated_at and changes['count'] == len(changes['changes']), 'changes.json window or count mismatch'
    for name in ENDPOINTS:
        rows = list(csv.reader(io.StringIO((folder / f'{name}.csv').read_text(encoding='utf-8'), newline='')))
        assert rows[0] == [*CSV_COLUMNS[name], 'version', 'generated_at'], f'{name}.csv header mismatch'
        assert all(row[-2:] == [API_VERSION, generated_at] for row in rows[1:]), f'{name}.csv rows need version and generated_at'
        listed = {'resources': 'resources', 'papers': 'papers', 'candidates': 'candidates', 'changes': 'changes'}.get(name)
        if listed:
            assert len(rows) - 1 == len(documents[name][listed]), f'{name}.csv row count differs from {name}.json'
    for entry in documents['index']['files']:
        raw = (Path(output) / entry['path'].lstrip('/')).read_bytes()
        assert entry['bytes'] == len(raw) and entry['sha256'] == hashlib.sha256(raw).hexdigest(), f'index.json checksum mismatch: {entry["path"]}'
    assert {entry['path'] for entry in documents['index']['files']} == {f'{API_PATH}{name}' for name in (
        'schema.json', *(f'{endpoint}.{suffix}' for endpoint in ENDPOINTS for suffix in ('json', 'csv')))}, 'index.json must list every API file'


def validate_json_feeds(output):
    """Each JSON Feed repeats its Atom feed: the same IDs, titles, links, dates and order."""
    atom = '{http://www.w3.org/2005/Atom}'
    output = Path(output)
    for language, path in JSON_FEED_PATHS.items():
        if not (output / FEED_PATHS[language].lstrip('/')).exists():
            assert not (output / path.lstrip('/')).exists(), f'A JSON Feed needs its Atom feed: {path}'
            continue
        feed = json.loads((output / path.lstrip('/')).read_text(encoding='utf-8'))
        root = ET.parse(output / FEED_PATHS[language].lstrip('/')).getroot()
        entries = [(entry.findtext(atom + 'id'), entry.findtext(atom + 'title'), entry.find(atom + 'link').get('href'),
                    entry.findtext(atom + 'published')) for entry in root.findall(atom + 'entry')]
        items = [(item['id'], item['title'], item['url'], item['date_published']) for item in feed['items']]
        assert feed['version'] == JSON_FEED_VERSION and feed['feed_url'] == ORIGIN + path, f'JSON Feed header mismatch: {path}'
        assert items == entries, f'JSON Feed items differ from the Atom feed: {path}'
        assert len(items) >= min(50, len(entries)), f'JSON Feed is too short: {path}'


def validate_llms(output, resources, papers):
    """llms.txt follows llmstxt.org and stays small; llms-full.txt carries every curated entry per language."""
    output = Path(output)
    raw = (output / 'llms.txt').read_bytes()
    text = raw.decode('utf-8')
    assert len(raw) <= LLMS_LIMIT, f'llms.txt exceeds {LLMS_LIMIT:,} bytes'
    lines = text.split('\n')
    assert lines[0].startswith('# ') and lines[1] == '' and lines[2].startswith('> '), 'llms.txt needs an H1 and a blockquote summary'
    assert text.count('\n## Optional\n') == 1, 'llms.txt needs one Optional section'
    for url in re.findall(r'\]\((https://awesomerea\.org/[^)\s]*)\)', text):
        path = url.removeprefix(ORIGIN).split('#')[0]
        local = output / path.lstrip('/')
        if path.endswith('/'):
            local /= 'index.html'
        assert local.is_file(), f'llms.txt links a missing file: {url}'
    for name, prefix in (('llms-full.txt', ''), ('zh/llms-full.txt', '/zh')):
        full = (output / name).read_text(encoding='utf-8')
        assert full.startswith('# '), f'{name} must be Markdown'
        for kind, records in (('resource', resources), ('paper', papers)):
            missing = [row['id'] for row in records if f'<{ORIGIN}{prefix}/{kind}s/{row["id"]}/>' not in full]
            assert not missing, f'{name} lacks entries: ' + ', '.join(missing[:5])


def validate_agent_files(output, resources, papers):
    """/AGENTS.md, /agents.md and /agents.txt are one file for agents that read the catalog."""
    output = Path(output)
    texts = {name: (output / name).read_text(encoding='utf-8') for name in ('AGENTS.md', 'agents.md', 'agents.txt')}
    assert len(set(texts.values())) == 1, 'AGENTS.md, agents.md and agents.txt must be identical'
    text = texts['AGENTS.md']
    for needed in (f'{len(resources):,} source-reviewed', f'{len(papers):,} research papers', 'curl -sL https://awesomerea.org/resources/ghidra/index.md',
                   'hf papers read', '/api/v1/resources.json', '/resources/?q=', '/llms-full.txt', '/sitemap.xml', '/downloads/records.jsonl',
                   '@misc{', 'issues/new/choose'):
        assert needed in text, f'AGENTS.md lacks: {needed}'
    assert 'https://awesomerea.org/AGENTS.md' in (output / 'llms.txt').read_text(encoding='utf-8'), 'llms.txt must link /AGENTS.md'


def validate_agent_headers(rules):
    for pattern, headers in EXPECTED_HEADERS.items():
        for name, value in headers.items():
            assert rules.get(pattern, {}).get(name) == value, f'_headers needs {pattern} {name}: {value}'


def validate_agent_formats(output, routes, resources, papers, rules, **queues):
    validate_twins(output, routes, resources, papers)
    validate_api(output, resources, papers, **queues)
    validate_json_feeds(output)
    validate_llms(output, resources, papers)
    validate_agent_files(output, resources, papers)
    validate_agent_headers(rules)
