#!/usr/bin/env python3
"""Check generated canonical pages, structured data, local links and ownership files."""
from collections import Counter, defaultdict
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET

from build_manifest import read_build_manifest
from build_paper_pages import TARGET_LABELS, bibtex_text
from validate_papers import read_papers
from artifact_links import with_artifact_links
from source_descriptions import description_fallback
from localization import localized_records, read_localizations
from source_scope import apply_scope, read_scope
from source_browser import BROWSER_FILENAME, FULL_EXPORT_FILENAME, validate_source_browser

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'dist'
ORIGIN = 'https://awesomerea.org'


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.canonicals, self.ids, self.schemas, self.alternates = [], [], [], [], []
        self.noindex, self.lang, self.json_script = False, None, None
        self.paper_ids, self.paper_texts, self.paper_links = [], {}, {}
        self.current_paper = None
        self.current_record, self.current_related_link = None, None
        self.record_ids, self.related_links = [], {}
        self.paper_groups, self._section_stack = [], []
        self._div_depth = 0
        self._group_summary, self._group_heading = None, None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        assert len(values) == len(attrs), f'Duplicate HTML attributes on {tag}'
        classes = values.get('class', '').split()
        if tag == 'section':
            group = None
            if 'paper-section' in classes:
                group = {'anchor': values.get('aria-labelledby'), 'paper_ids': [],
                         'headings': [], 'summaries': []}
                self.paper_groups.append(group)
            self._section_stack.append(group)
        current_group = next((group for group in reversed(self._section_stack) if group is not None), None)
        if tag == 'div':
            self._div_depth += 1
            if current_group is not None and 'paper-section-heading' in classes:
                self._group_summary = {'depth': self._div_depth, 'text': []}
                current_group['summaries'].append(self._group_summary)
        if tag == 'h2' and current_group is not None and self._group_summary is not None:
            self._group_heading = {'id': values.get('id'), 'text': []}
            current_group['headings'].append(self._group_heading)
        if tag == 'html':
            self.lang = values.get('lang')
        if values.get('id'):
            self.ids.append(values['id'])
        if tag == 'article' and 'data-paper-id' in values:
            assert self.current_paper is None, 'Nested paper articles are invalid'
            identifier = values['data-paper-id']
            assert values.get('id') == identifier, 'Paper fragment and data-paper-id differ'
            self.paper_ids.append(identifier)
            self.paper_texts[identifier], self.paper_links[identifier] = [], []
            self.current_paper = identifier
            if current_group is not None:
                current_group['paper_ids'].append(identifier)
        if tag == 'article' and 'data-record-id' in values:
            identifier = values['data-record-id']
            self.record_ids.append(identifier)
            self.related_links[identifier] = []
            self.current_record = identifier
        if tag in ('a', 'link') and values.get('href'):
            self.links.append(values['href'])
            if self.current_paper:
                self.paper_links[self.current_paper].append(values['href'])
            if self.current_record and 'source-related-link' in values.get('class', '').split():
                self.current_related_link = {'href': values['href'], 'text': '', 'target': values.get('target')}
                self.related_links[self.current_record].append(self.current_related_link)
        if tag == 'link' and values.get('rel') == 'canonical':
            self.canonicals.append(values.get('href'))
        if tag == 'link' and values.get('rel') == 'alternate' and values.get('hreflang'):
            self.alternates.append((values['hreflang'], values['href']))
        if tag == 'meta' and values.get('name') == 'robots' and 'noindex' in values.get('content', ''):
            self.noindex = True
        if tag == 'script' and values.get('type') == 'application/ld+json':
            self.json_script = ''

    def handle_data(self, data):
        if self.json_script is not None:
            self.json_script += data
        elif self.current_paper:
            self.paper_texts[self.current_paper].append(data)
        if self.current_related_link is not None:
            self.current_related_link['text'] += data
        if self._group_summary is not None:
            self._group_summary['text'].append(data)
        if self._group_heading is not None:
            self._group_heading['text'].append(data)

    def handle_endtag(self, tag):
        if tag == 'script' and self.json_script is not None:
            self.schemas.append(json.loads(self.json_script))
            self.json_script = None
        if tag == 'article':
            self.current_paper = None
            self.current_record = None
        if tag == 'a':
            self.current_related_link = None
        if tag == 'h2':
            self._group_heading = None
        if tag == 'div':
            if self._group_summary is not None and self._group_summary['depth'] == self._div_depth:
                self._group_summary = None
            self._div_depth -= 1
        if tag == 'section' and self._section_stack:
            self._section_stack.pop()


def structured_checks(value):
    if isinstance(value, list):
        for child in value:
            structured_checks(child)
    elif isinstance(value, dict):
        if value.get('@type') == 'ItemList':
            assert value['numberOfItems'] == len(value['itemListElement']), 'Structured item count mismatch'
        assert 'aggregateRating' not in value, 'Do not misrepresent stars as ratings'
        for child in value.values():
            structured_checks(child)


def schema_entities(value, type_name):
    if isinstance(value, list):
        for item in value:
            yield from schema_entities(item, type_name)
    elif isinstance(value, dict):
        if value.get('@type') == type_name:
            yield value
        for item in value.values():
            yield from schema_entities(item, type_name)


def validate_language_links(route, page):
    """Link Chinese navigation to /zh/ routes, never to English routes with ?lang=zh."""
    for link in page.links:
        target = urlsplit(urljoin(ORIGIN + route, link))
        if target.netloc != 'awesomerea.org':
            continue
        served = 'zh' if target.path == '/zh' or target.path.startswith('/zh/') else 'en'
        requested = parse_qs(target.query).get('lang', [])
        assert all(value == served for value in requested), f'Link selects a language its route does not serve on {route}: {link}'


def validate_paper_groups(page, papers, language):
    """Check visible section membership and headings against primary targets."""
    expected = defaultdict(list)
    for paper in papers:
        expected[paper['targets'][0]].append(paper['id'])
    assert set(expected) <= set(TARGET_LABELS), 'Unknown primary paper target'
    anchors = [group['anchor'] for group in page.paper_groups]
    assert Counter(anchors) == Counter('research-' + target for target in expected), f'Paper section coverage mismatch ({language})'
    normalize = lambda parts: ' '.join(' '.join(parts).split())
    for group in page.paper_groups:
        target = group['anchor'].removeprefix('research-')
        identifiers = expected[target]
        assert Counter(group['paper_ids']) == Counter(identifiers), f'Paper primary-target grouping mismatch: {target} ({language})'
        label = TARGET_LABELS[target][language == 'zh']
        assert len(group['headings']) == 1 and group['headings'][0]['id'] == group['anchor'], f'Paper section heading anchor mismatch: {target} ({language})'
        assert normalize(group['headings'][0]['text']) == label, f'Paper section label mismatch: {target} ({language})'
        count = len(identifiers)
        count_label = f'{count} ' + ('篇论文' if language == 'zh' else ('paper' if count == 1 else 'papers'))
        assert len(group['summaries']) == 1 and normalize(group['summaries'][0]['text']) == label + ' ' + count_label, f'Paper section count mismatch: {target} ({language})'


def validate_paper_outputs(output, pages, source_papers=None):
    """Bind both rendered bibliographies and every citation to the source JSON."""
    output = Path(output)
    source_papers = read_papers(ROOT) if source_papers is None else source_papers
    built = json.loads((output / 'papers.json').read_text(encoding='utf-8'))
    assert built == source_papers, 'Built papers.json differs from the source bibliography'
    expected = {paper['id']: paper for paper in built}
    assert len(expected) == len(built), 'Duplicate built paper IDs'
    catalog = json.loads((output / 'catalog.json').read_text(encoding='utf-8'))
    assert catalog['meta']['paper_count'] == len(expected), 'Catalog paper count differs from the bibliography'
    statuses = {'conference-paper': ('Conference paper', '会议论文'),
                'conference-accepted': ('Conference accepted', '会议已接收'),
                'journal-article': ('Journal article', '期刊论文'),
                'preprint': ('Preprint', '预印本')}
    normalize = lambda text: ' '.join(text.split())
    for route, language in (('/papers/', 'en'), ('/zh/papers/', 'zh')):
        assert route in pages, f'Paper route is missing from the sitemap: {route}'
        page = pages[route]
        assert len(page.paper_ids) == len(expected) and set(page.paper_ids) == set(expected), f'Paper DOM coverage mismatch: {route}'
        validate_paper_groups(page, built, language)
        listings = list(schema_entities(page.schemas, 'ItemList'))
        assert len(listings) == 1, f'Expected one paper ItemList: {route}'
        items = listings[0]['itemListElement']
        assert listings[0]['numberOfItems'] == len(expected), f'Paper ItemList source count mismatch: {route}'
        assert items == [
            {'@type': 'ListItem', 'position': position, 'url': ORIGIN + route + '#' + identifier,
             'item': {'@id': expected[identifier]['url']}}
            for position, identifier in enumerate(page.paper_ids, 1)
        ], f'Paper ItemList differs from visible paper order or identities: {route}'
        articles = list(schema_entities(page.schemas, 'ScholarlyArticle'))
        by_url = {article.get('@id'): article for article in articles}
        assert len(articles) == len(by_url) == len(expected) and set(by_url) == {p['url'] for p in built}, f'ScholarlyArticle coverage mismatch: {route}'
        for identifier in page.paper_ids:
            paper = expected[identifier]
            article = {
                '@type': 'ScholarlyArticle', '@id': paper['url'], 'url': paper['url'],
                'name': paper['title'], 'headline': paper['title'], 'alternateName': paper['title_zh'],
                'author': [{'@type': 'Person', 'name': name} for name in paper['authors']],
                'description': paper[f'description_{language}'],
                'creativeWorkStatus': statuses[paper['publication_status']][0],
                'isPartOf': {'@type': 'CreativeWork', 'name': paper['venue']},
                'encoding': {'@type': 'MediaObject', 'encodingFormat': 'application/pdf', 'contentUrl': paper['pdf_url']},
            }
            if paper.get('publication_date'):
                article['datePublished'] = paper['publication_date']
            identifiers = [
                {'@type': 'PropertyValue', 'propertyID': label, 'value': paper[field]}
                for field, label in (('doi', 'DOI'), ('arxiv_id', 'arXiv')) if paper.get(field)
            ]
            if identifiers:
                article['identifier'] = identifiers
            assert by_url[paper['url']] == article, f'ScholarlyArticle fields differ from source: {identifier} ({language})'
            text = normalize(' '.join(page.paper_texts[identifier]))
            phrases = [paper['title_zh'] if language == 'zh' else paper['title'],
                       '; '.join(paper['authors']), paper['venue'], statuses[paper['publication_status']][language == 'zh'],
                       paper[f'description_{language}'], paper[f'scope_limitations_{language}'], paper[f'why_fits_{language}'],
                       paper['date_basis_zh' if language == 'zh' else 'date_basis'],
                       paper['metadata_notes_zh' if language == 'zh' else 'metadata_notes']]
            if language == 'zh':
                phrases.append(paper['title'])
            assert all(normalize(phrase) in text for phrase in phrases), f'Visible paper text differs from source: {identifier} ({language})'
            links = {paper['url'], paper['pdf_url'], *paper['evidence_urls'], f'/papers/citations/{identifier}.bib'}
            links.update(paper[field] for field in ('code_url', 'project_url') if paper.get(field))
            assert links <= set(page.paper_links[identifier]), f'Visible paper source or citation link missing: {identifier} ({language})'
    citations = output / 'papers' / 'citations'
    assert {path.name for path in citations.glob('*.bib')} == {identifier + '.bib' for identifier in expected}, 'BibTeX file coverage differs from the bibliography'
    entries = []
    for paper in built:
        entry = bibtex_text(paper)
        assert (citations / (paper['id'] + '.bib')).read_text(encoding='utf-8') == entry, f'BibTeX content differs from source: {paper["id"]}'
        entries.append(entry)
    bibliography = '% Generated from source-reviewed metadata. Author names retain their listed order without inferred surname parsing.\n\n' + ''.join(entry + '\n' for entry in entries)
    assert (output / 'papers' / 'references.bib').read_text(encoding='utf-8') == bibliography, 'Combined BibTeX differs from the source bibliography'
    headers = (output / '_headers').read_text(encoding='utf-8')
    for route in ('/papers/references.bib', '/papers/citations/*.bib'):
        assert re.search(rf'(?m)^{re.escape(route)}\n[ \t]+Content-Type: application/x-bibtex; charset=utf-8[ \t]*$', headers), f'BibTeX downloads require an explicit UTF-8 content type: {route}'


def validate_artifact_links(output, pages):
    """Bind generated links to reviewed artifacts and retain source assertions."""
    source_path = ROOT / 'data/source-index.json'
    if not source_path.exists():
        return
    original = json.loads(source_path.read_text(encoding='utf-8'))
    records = [row for row in original.get('resources', []) if row.get('scan_status') == 'readme-scanned']
    if not records:
        return
    translations = json.loads((ROOT / 'site/translations.zh-CN.json').read_text(encoding='utf-8'))
    resources = []
    for filename in ('rea-resources.json', 'tool-resources.json'):
        for original_resource in json.loads((ROOT / 'data' / filename).read_text(encoding='utf-8')):
            resource = dict(original_resource)
            resource['name_zh'] = resource.get('name_zh') or translations.get(resource['id'], {}).get('name', resource['name'])
            resources.append(resource)
    projected = apply_scope(localized_records(records, read_localizations(ROOT)), read_scope(ROOT))
    expected = with_artifact_links(projected, read_papers(ROOT), resources)
    built = json.loads((Path(output) / 'source-index.json').read_text(encoding='utf-8'))
    assert built['resources'] == expected, 'Generated sources differ from localized source evidence and reviewed artifact links'
    visible = [record for record in expected if record.get('scope_status') != 'excluded']
    normalize = lambda text: ' '.join(text.split())
    for language in ('en', 'zh'):
        prefix = '/zh' if language == 'zh' else ''
        for record in visible:
            route = f'{prefix}/browse/{record["category"]}/'
            page = pages[route]
            assert record['id'] in page.record_ids, f'Missing repository card: {record["id"]} ({language})'
            expected_links = []
            for entry in record.get('related_entries', []):
                href = entry[f'href_{language}']
                destination = urlsplit(href)
                assert destination.path in pages and destination.fragment in pages[destination.path].ids, f'Missing related-entry anchor: {href}'
                expected_links.append({'href': href, 'text': normalize(entry[f'title_{language}']), 'target': None})
            actual = [{**link, 'text': normalize(link['text'])} for link in page.related_links.get(record['id'], [])]
            assert actual == expected_links, f'Related-entry navigation mismatch: {record["id"]} ({language})'
        for category in {record['category'] for record in visible}:
            page = pages[f'{prefix}/browse/{category}/']
            items = list(schema_entities(page.schemas, 'ItemList'))
            assert len(items) == 1, 'Browse category must retain one repository ItemList'
            descriptions = {item['url']: item['description'] for item in items[0]['itemListElement']}
            assert descriptions == {record['url']: record[f'description_{language}'] or description_fallback(record, language)
                                    for record in visible if record['category'] == category}, 'Related links must not replace repository schema descriptions'


def validate_source_browser_output(output):
    """Keep the interactive payload exact, bounded in scope, and freshly served."""
    output = Path(output)
    full_path, browser_path = output / FULL_EXPORT_FILENAME, output / BROWSER_FILENAME
    if not full_path.exists():
        assert not browser_path.exists(), 'Stale browser source projection without a full export'
        return
    assert browser_path.is_file(), 'Browser source projection is missing'
    validate_source_browser(full_path.read_bytes(), browser_path.read_bytes())
    headers = (output / '_headers').read_text(encoding='utf-8')
    assert re.search(r'(?m)^/source-browser\.json\n[ \t]+Cache-Control: no-cache, must-revalidate[ \t]*$', headers), 'Browser source projection requires no-cache headers'


def main():
    urls = [element.text for element in ET.parse(OUTPUT / 'sitemap.xml').findall('{*}url/{*}loc')]
    assert urls and len(urls) == len(set(urls)), 'Duplicate or empty sitemap'
    pages = {}
    for url in urls:
        parsed = urlsplit(url)
        assert parsed.netloc == 'awesomerea.org' and parsed.scheme == 'https' and not parsed.query and not parsed.fragment
        path = OUTPUT / parsed.path.lstrip('/') / 'index.html'
        text = path.read_text()
        assert not re.search(r'\{\{[A-Z_]+\}\}', text), f'Unresolved template in {parsed.path}'
        page = Page(text)
        pages[parsed.path] = page
        assert page.canonicals == [url] and not page.noindex, f'Canonical/indexing mismatch: {parsed.path}'
        assert not [key for key, count in Counter(page.ids).items() if count > 1], f'Duplicate HTML IDs: {parsed.path}'
        assert page.schemas, f'Missing structured data: {parsed.path}'
        for schema in page.schemas:
            structured_checks(schema)
        if parsed.path != '/':
            english = parsed.path.removeprefix('/zh') if parsed.path.startswith('/zh/') else parsed.path
            expected = {'en': ORIGIN + english, 'zh-CN': ORIGIN + '/zh' + english, 'x-default': ORIGIN + english}
            assert len(page.alternates) == 3 and dict(page.alternates) == expected, f'Incorrect reciprocal language alternatives: {parsed.path}'
        assert page.lang == ('zh-CN' if parsed.path.startswith('/zh/') else 'en')
        validate_language_links(parsed.path, page)
        for link in page.links:
            target = urlsplit(link)
            if target.netloc not in ('', 'awesomerea.org') or target.scheme not in ('', 'https'):
                continue
            local = OUTPUT / unquote(target.path).lstrip('/') if target.path.startswith('/') else path.parent / unquote(target.path)
            if not target.path:
                local = path
            if local.is_dir():
                local /= 'index.html'
            assert local.is_file(), f'Missing local link on {parsed.path}: {link}'
    validate_paper_outputs(OUTPUT, pages)
    validate_artifact_links(OUTPUT, pages)
    validate_source_browser_output(OUTPUT)
    assert Page((OUTPUT / '404.html').read_text()).noindex, '404 must be noindex'
    assert (OUTPUT / 'llms.txt').read_text().startswith('# '), 'llms.txt must contain Markdown'
    assert re.fullmatch(r'[a-f0-9]{32}\n?', (OUTPUT / 'indexnow.txt').read_text()), 'Invalid public ownership proof'
    read_build_manifest(OUTPUT)
    print(f'Validated {len(urls)} canonical HTML pages, paper/source/citation coverage, language alternatives, JSON-LD, local links and the deployment manifest.')


if __name__ == '__main__':
    main()
