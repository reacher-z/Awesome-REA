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
from build_paper_pages import TARGET_LABELS, bibtex_text, papers_newest_first
from validate_papers import read_papers
from artifact_links import with_artifact_links, with_curated_labels
from source_descriptions import description_fallback
from localization import localized_records, read_localizations
from source_scope import apply_scope, read_scope
from source_browser import BROWSER_FILENAME, FULL_EXPORT_FILENAME, validate_source_browser
from validate_discovery import expected_entry_routes, validate_route_inventory
from build_readme import collection_section
from homepage_locales import _ui_strings
from open_graph import OG_LOCALES, SOCIAL_IMAGE_ALT, png_size
from build_entry_pages import entry_path, section_siblings

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'dist'
ORIGIN = 'https://awesomerea.org'
ARROWS = re.compile('[\u2190-\u21ff\u27f0-\u27ff\u2900-\u297f]')
PRELOAD_DIRECTIVES = {'fetch': 'connect-src', 'script': 'script-src', 'style': 'style-src', 'font': 'font-src', 'image': 'img-src'}
VOID_TAGS = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.canonicals, self.ids, self.schemas, self.alternates = [], [], [], [], []
        self.anchor_names = []
        self.section_links, self._in_related = None, False
        self.noindex, self.lang, self.json_script = False, None, None
        self.paper_ids, self.paper_texts, self.paper_links = [], {}, {}
        self.current_paper = None
        self.current_record, self.current_related_link = None, None
        self.record_ids, self.related_links, self.record_links = [], {}, {}
        self.detail_links, self.entry_markers, self.entry_contents, self.meta = [], [], [], {}
        self.meta_keys, self.h1_texts, self._h1, self._h1_stack = [], [], None, []
        self.current_detail_link = None
        self.current_entry, self.entry_heading, self.entry_time = None, None, None
        self.entry_article_depth = 0
        self.case_rows, self.current_case = [], None
        self.case_heading, self.case_time = None, None
        self._case_sections = []
        self.raw_text_tag = None
        self.paper_groups, self._section_stack = [], []
        self._div_depth = 0
        self._group_summary, self._group_heading = None, None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        assert len(values) == len(attrs), f'Duplicate HTML attributes on {tag}'
        classes = values.get('class', '').split()
        if tag == 'section' and 'entry-related' in classes:
            self.section_links, self._in_related = [], True
        if tag == 'section':
            self._case_sections.append({'section': values.get('data-case-section'), 'anchor': values.get('id')}
                                       if 'case-section' in classes else None)
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
        if tag == 'a' and values.get('name'):
            self.anchor_names.append(values['name'])
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
            self.record_links[identifier] = []
            self.current_record = identifier
        if tag == 'article' and 'data-case-id' in values:
            assert self.current_case is None, 'Nested case articles are invalid'
            case_section = next((section for section in reversed(self._case_sections) if section is not None), {})
            self.current_case = {'id': values['data-case-id'], 'anchor': values.get('id'),
                                 'section': values.get('data-case-section'), 'text': [],
                                 'headings': [], 'times': [], 'links': [],
                                 'parent_section': case_section.get('section'),
                                 'parent_anchor': case_section.get('anchor')}
            self.case_rows.append(self.current_case)
        if self.current_case is not None and tag == 'h3':
            self.case_heading = []
            self.current_case['headings'].append(self.case_heading)
        if self.current_case is not None and tag == 'time':
            self.case_time = {'datetime': values.get('datetime'), 'text': []}
            self.current_case['times'].append(self.case_time)
        if tag == 'article' and self.current_entry is not None:
            self.entry_article_depth += 1
        if tag == 'article' and ('data-entry-kind' in values or 'data-entry-id' in values):
            assert self.current_entry is None, 'Nested marked entry articles are invalid'
            self.entry_markers.append((values.get('data-entry-kind'), values.get('data-entry-id')))
            self.current_entry = {'text': [], 'headings': [], 'times': [], 'links': []}
            self.entry_contents.append(self.current_entry)
            self.entry_article_depth = 1
        if self.current_entry is not None and tag == 'h1':
            self.entry_heading = []
            self.current_entry['headings'].append(self.entry_heading)
        if self.current_entry is not None and tag == 'time':
            self.entry_time = {'datetime': values.get('datetime'), 'text': []}
            self.current_entry['times'].append(self.entry_time)
        if tag == 'a' and 'entry-detail-link' in classes:
            self.current_detail_link = {'id': values.get('data-entry-link'), 'href': values.get('href'),
                                        'target': values.get('target'), 'aria_label': values.get('aria-label'),
                                        'text': [], 'container_id': self.current_paper or self.current_record}
            self.detail_links.append(self.current_detail_link)
        if tag in ('a', 'link') and values.get('href'):
            self.links.append(values['href'])
            if self._in_related and tag == 'a':
                self.section_links.append(values['href'])
            if self.current_case is not None:
                self.current_case['links'].append(values['href'])
            if self.current_paper:
                self.paper_links[self.current_paper].append(values['href'])
            if self.current_record:
                self.record_links[self.current_record].append(values['href'])
            if self.current_entry is not None:
                self.current_entry['links'].append(values['href'])
            if self.current_record and 'source-related-link' in values.get('class', '').split():
                self.current_related_link = {'href': values['href'], 'text': '', 'target': values.get('target')}
                self.related_links[self.current_record].append(self.current_related_link)
        if tag == 'link' and values.get('rel') == 'canonical':
            self.canonicals.append(values.get('href'))
        if tag == 'link' and values.get('rel') == 'alternate' and values.get('hreflang'):
            self.alternates.append((values['hreflang'], values['href']))
        if tag == 'meta' and values.get('name') == 'robots' and 'noindex' in values.get('content', ''):
            self.noindex = True
        if tag == 'meta':
            self.meta[values.get('name') or values.get('property')] = values.get('content')
            self.meta_keys.append(values.get('name') or values.get('property'))
        # Visible H1 text, without decorative aria-hidden descendants such as the title dot.
        if self._h1 is not None and tag not in VOID_TAGS:
            self._h1_stack.append((tag, values.get('aria-hidden') == 'true'))
        if tag == 'h1' and self._h1 is None:
            self._h1, self._h1_stack = [], []
        if tag in ('script', 'style'):
            self.raw_text_tag = tag
        if tag == 'script' and values.get('type') == 'application/ld+json':
            self.json_script = ''

    def handle_data(self, data):
        if self._h1 is not None and not any(hidden for _, hidden in self._h1_stack):
            self._h1.append(data)
        if self.raw_text_tag is None:
            if self.current_case is not None:
                self.current_case['text'].append(data)
            if self.case_heading is not None:
                self.case_heading.append(data)
            if self.case_time is not None:
                self.case_time['text'].append(data)
            if self.current_entry is not None:
                self.current_entry['text'].append(data)
            if self.entry_heading is not None:
                self.entry_heading.append(data)
            if self.entry_time is not None:
                self.entry_time['text'].append(data)
            if self.current_detail_link is not None:
                self.current_detail_link['text'].append(data)
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
        if tag == self.raw_text_tag:
            self.raw_text_tag = None
        if tag == 'article':
            self.current_case, self.case_heading, self.case_time = None, None, None
            self.current_paper = None
            self.current_record = None
            if self.current_entry is not None:
                self.entry_article_depth -= 1
                if self.entry_article_depth == 0:
                    self.current_entry, self.entry_heading, self.entry_time = None, None, None
        if tag == 'h1':
            self.entry_heading = None
        if self._h1 is not None:
            if self._h1_stack and self._h1_stack[-1][0] == tag:
                self._h1_stack.pop()
            elif tag == 'h1':
                self.h1_texts.append(' '.join(''.join(self._h1).split()))
                self._h1 = None
        if tag == 'time':
            self.entry_time = None
            self.case_time = None
        if tag == 'h3':
            self.case_heading = None
        if tag == 'a':
            self.current_related_link = None
            self.current_detail_link = None
        if tag == 'h2':
            self._group_heading = None
        if tag == 'div':
            if self._group_summary is not None and self._group_summary['depth'] == self._div_depth:
                self._group_summary = None
            self._div_depth -= 1
        if tag == 'section':
            self._in_related = False
        if tag == 'section' and self._section_stack:
            self._section_stack.pop()
        if tag == 'section' and self._case_sections:
            self._case_sections.pop()


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


def validate_homepage_destinations(pages, app_source=None):
    """Homepage ItemList names repeat each destination's H1, never arrowed UI link text."""
    strings = _ui_strings(app_source if app_source is not None else (ROOT / 'site/app.js').read_text(encoding='utf-8'))
    for route, language in (('/', 'en'), ('/zh/', 'zh')):
        lists = [entity['mainEntity'] for entity in schema_entities(pages[route].schemas, 'CollectionPage')
                 if isinstance(entity.get('mainEntity'), dict) and entity['mainEntity'].get('@type') == 'ItemList']
        assert len(lists) == 1 and lists[0]['itemListElement'], f'Homepage needs one destination ItemList: {route}'
        for item in lists[0]['itemListElement']:
            name, destination = item.get('name'), urlsplit(item.get('url', '')).path
            assert isinstance(name, str) and name.strip(), f'Homepage ItemList item needs a name: {route}'
            assert not ARROWS.search(name), f'Homepage ItemList name contains an arrow: {name!r} ({route})'
            assert name not in strings[language].values(), f'Homepage ItemList name reuses interface link text: {name!r} ({route})'
            assert destination in pages and pages[destination].h1_texts == [name], f'Homepage ItemList name differs from the H1 of {destination}: {name!r}'


def validate_open_graph(route, page, card_size):
    """Every page publishes the shared social block; ``route=None`` is the uncanonical 404 template."""
    assert len(page.meta_keys) == len(set(page.meta_keys)), f'Duplicate meta tags: {route}'
    meta, language = page.meta, 'zh' if route and route.startswith('/zh/') else 'en'
    expected = {'og:type': 'website', 'og:site_name': 'AwesomeREA.org', 'og:locale': OG_LOCALES[language],
                'og:image:type': 'image/png', 'og:image:width': str(card_size[0]), 'og:image:height': str(card_size[1]),
                'og:image:alt': SOCIAL_IMAGE_ALT[language], 'twitter:card': 'summary_large_image',
                'twitter:image:alt': SOCIAL_IMAGE_ALT[language]}
    if route is not None:
        expected.update({'og:locale:alternate': OG_LOCALES['en' if language == 'zh' else 'zh'], 'og:url': ORIGIN + route})
    assert {key: meta.get(key) for key in expected} == expected, f'Open Graph block differs from the shared generator: {route}'
    if route is None:
        assert 'og:url' not in meta and 'og:locale:alternate' not in meta, 'The 404 template must not publish an og:url or counterpart'
    image = urlsplit(meta.get('og:image') or '')
    assert (image.scheme, image.netloc, image.path) == ('https', 'awesomerea.org', '/social-card.png') and meta.get('twitter:image') == meta['og:image'], f'Social image URL mismatch: {route}'
    assert meta['og:image:alt'] not in {meta.get('og:title'), meta.get('twitter:title')}, f'og:image:alt repeats the page title: {route}'


def header_rules(text):
    """Parse Cloudflare Pages _headers: unindented URL patterns, indented Name: value lines."""
    rules, current = {}, None
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if not line[0].isspace():
            current = rules.setdefault(line.strip(), {})
            continue
        name, separator, value = line.strip().partition(':')
        assert current is not None and separator and value.strip(), f'Malformed _headers line {number}'
        assert name.strip().lower() not in current, f'Duplicate header in one _headers rule: line {number}'
        current[name.strip().lower()] = value.strip()
    return rules


def csp_directives(policy):
    directives = {}
    for part in policy.split(';'):
        tokens = part.split()
        if tokens:
            assert tokens[0].lower() not in directives, f'Duplicate CSP directive: {tokens[0]}'
            directives[tokens[0].lower()] = tokens[1:]
    return directives


def csp_allows(directives, directive, url, base=ORIGIN + '/'):
    """Match a resource against one fetch directive, falling back to default-src."""
    sources = directives.get(directive, directives.get('default-src', []))
    target = urlsplit(urljoin(base, url))
    origin = target.scheme + '://' + target.netloc
    return ("'self'" in sources and origin == ORIGIN) or origin in {source.rstrip('/') for source in sources}


class PageResources(HTMLParser):
    """Collect what a built page asks the browser to load or execute."""
    def __init__(self, text):
        super().__init__()
        self.scripts, self.inline_scripts, self.stylesheets, self.images = [], 0, [], []
        self.inline_styles, self.handlers, self.embeds, self.preloads = 0, [], [], []
        self.catalog_revision = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        self.handlers.extend(name for name in values if name.startswith('on'))
        self.inline_styles += 'style' in values or tag == 'style'
        if tag == 'html':
            self.catalog_revision = values.get('data-catalog-revision')
        if tag == 'script':
            if values.get('src'):
                self.scripts.append(values['src'])
            elif (values.get('type') or 'text/javascript').lower() not in {'application/ld+json', 'application/json'}:
                self.inline_scripts += 1
        if tag == 'link' and values.get('href'):
            relations = set((values.get('rel') or '').lower().split())
            if 'stylesheet' in relations:
                self.stylesheets.append(values['href'])
            elif relations & {'icon', 'apple-touch-icon'}:
                self.images.append(values['href'])
            elif 'preload' in relations:
                # fetch() requests in CORS mode with same-origin credentials; only crossorigin="anonymous" matches it.
                self.preloads.append({'as': values.get('as'), 'href': values['href'],
                                      'cors': 'crossorigin' in values and values['crossorigin'] in (None, '', 'anonymous')})
        if tag == 'img' and values.get('src'):
            self.images.append(values['src'])
        if tag in {'iframe', 'object', 'embed', 'base', 'frame'}:
            self.embeds.append(tag)


def validate_security_headers(output):
    """Keep the site-wide policy strict and sufficient for everything the built HTML loads."""
    output = Path(output)
    rules = header_rules((output / '_headers').read_text(encoding='utf-8'))
    site = rules.get('/*', {})
    assert site.get('x-frame-options') == 'DENY', 'Site pages must not be framed'
    assert site.get('permissions-policy'), 'Missing Permissions-Policy'
    hsts = site.get('strict-transport-security', '')
    assert re.fullmatch(r'max-age=[1-9]\d*', hsts), 'HSTS needs a positive max-age; includeSubDomains and preload need a documented owner decision'
    policies = [site[name] for name in ('content-security-policy', 'content-security-policy-report-only') if name in site]
    assert len(policies) == 1, 'Use one site-wide Content-Security-Policy (or its Report-Only form)'
    directives = csp_directives(policies[0])
    for directive in ('default-src', 'base-uri', 'frame-ancestors'):
        assert directives.get(directive) == ["'none'"], f'CSP {directive} must be none'
    assert 'form-action' in directives, 'CSP must restrict form submissions'
    for directive in ('script-src', 'style-src'):
        assert not {"'unsafe-inline'", "'unsafe-eval'", '*', 'data:', 'http:', 'https:'} & set(directives.get(directive, [])), f'CSP {directive} is too broad'
    assert csp_allows(directives, 'connect-src', '/catalog.json'), 'CSP must allow same-origin JSON fetches'
    # Cloudflare Web Analytics is injected at the edge on the production domain, so built pages never show it.
    assert csp_allows(directives, 'script-src', 'https://static.cloudflareinsights.com/beacon.min.js'), 'CSP must allow the Cloudflare Web Analytics beacon'
    assert csp_allows(directives, 'connect-src', 'https://cloudflareinsights.com/cdn-cgi/rum'), 'CSP must allow Cloudflare Web Analytics reports'
    for path in sorted(output.rglob('*.html')):
        page = PageResources(path.read_text(encoding='utf-8'))
        where = '/' + path.relative_to(output).as_posix()
        assert not page.inline_scripts and not page.inline_styles and not page.handlers and not page.embeds, f'Inline code, styles, handlers or embeds need a CSP review: {where}'
        for directive, urls in (('script-src', page.scripts), ('style-src', page.stylesheets), ('img-src', page.images)):
            for url in urls:
                assert csp_allows(directives, directive, url), f'CSP {directive} blocks {url} on {where}'
        for preload in page.preloads:
            directive = PRELOAD_DIRECTIVES.get(preload['as'])
            assert directive and csp_allows(directives, directive, preload['href']), f'CSP blocks the {preload["as"]} preload {preload["href"]} on {where}'
        for url in page.stylesheets:
            # The icon stylesheet loads its fonts relative to its own origin.
            if urlsplit(url).path.endswith('/fontawesome.css'):
                assert csp_allows(directives, 'font-src', url), f'CSP font-src blocks the fonts of {url}'


def validate_catalog_preload(output):
    """Each homepage preloads exactly the catalog URL app.js fetches for its data revision, and nothing else."""
    for route in ('index.html', 'zh/index.html'):
        page = PageResources((Path(output) / route).read_text(encoding='utf-8'))
        revision = page.catalog_revision
        assert revision and re.fullmatch(r'[0-9a-f]{16}', revision), f'Homepage needs a data-catalog-revision: /{route}'
        expected = [{'as': 'fetch', 'href': '/catalog.json?v=' + revision, 'cors': True}]
        assert page.preloads == expected, f'Homepage preloads must be one CORS fetch of /catalog.json?v={revision}: /{route} has {page.preloads}'


def validate_language_links(route, page):
    """Link Chinese navigation to /zh/ routes, never to English routes with ?lang=zh."""
    for link in page.links:
        target = urlsplit(urljoin(ORIGIN + route, link))
        if target.netloc != 'awesomerea.org':
            continue
        served = 'zh' if target.path == '/zh' or target.path.startswith('/zh/') else 'en'
        requested = parse_qs(target.query).get('lang', [])
        assert all(value == served for value in requested), f'Link selects a language its route does not serve on {route}: {link}'


def validate_link_fragments(output, pages, links):
    """Check internal #fragments once every page is parsed, so cross-page targets are known.

    links holds (source route, href, built target file). A fragment must match an id or
    an <a name> on its HTML target, raw or percent-decoded; other file types are not
    checked. Pages outside the sitemap are parsed on demand.
    """
    output = Path(output)
    parsed = {(output / route.lstrip('/') / 'index.html').resolve(): page for route, page in pages.items()}
    missing = []
    for route, link, local in links:
        if local.suffix.lower() not in {'.html', '.htm'}:
            continue
        key = local.resolve()
        if key not in parsed:
            parsed[key] = Page(local.read_text(encoding='utf-8'))
        fragment = urlsplit(link).fragment
        if not {fragment, unquote(fragment)} & {*parsed[key].ids, *parsed[key].anchor_names}:
            missing.append(f'{route}: {link}')
    assert not missing, 'Missing link fragment targets: ' + '; '.join(missing)


def validate_paper_groups(page, papers, language):
    """Check visible section membership, newest-first order and primary-target headings."""
    expected = defaultdict(list)
    for paper in papers:
        expected[paper['targets'][0]].append(paper)
    assert set(expected) <= set(TARGET_LABELS), 'Unknown primary paper target'
    anchors = [group['anchor'] for group in page.paper_groups]
    assert Counter(anchors) == Counter('research-' + target for target in expected), f'Paper section coverage mismatch ({language})'
    normalize = lambda parts: ' '.join(' '.join(parts).split())
    for group in page.paper_groups:
        target = group['anchor'].removeprefix('research-')
        identifiers = [paper['id'] for paper in papers_newest_first(expected[target])]
        assert Counter(group['paper_ids']) == Counter(identifiers), f'Paper primary-target grouping mismatch: {target} ({language})'
        assert group['paper_ids'] == identifiers, f'Paper newest-first ordering mismatch: {target} ({language})'
        label = TARGET_LABELS[target][language == 'zh']
        assert len(group['headings']) == 1 and group['headings'][0]['id'] == group['anchor'], f'Paper section heading anchor mismatch: {target} ({language})'
        assert normalize(group['headings'][0]['text']) == label, f'Paper section label mismatch: {target} ({language})'
        count = len(identifiers)
        count_label = f'{count} ' + ('篇论文' if language == 'zh' else ('paper' if count == 1 else 'papers'))
        assert len(group['summaries']) == 1 and normalize(group['summaries'][0]['text']) == label + ' ' + count_label, f'Paper section count mismatch: {target} ({language})'


def expected_paper_schema(paper, language):
    statuses = {
        "conference-paper": ("Conference paper", "会议论文"),
        "conference-accepted": ("Conference accepted", "会议已接收"),
        "journal-article": ("Journal article", "期刊论文"),
        "preprint": ("Preprint", "预印本"),
    }
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
    return article


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
            article = expected_paper_schema(paper, language)
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
    expected = with_curated_labels(with_artifact_links(projected, read_papers(ROOT), resources), resources)
    built = json.loads((Path(output) / 'source-index.json').read_text(encoding='utf-8'))
    assert built['resources'] == expected, 'Generated sources differ from localized source evidence, reviewed artifact links and curated labels'
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
                assert destination.path in pages and not destination.fragment, f'Missing related-entry detail page: {href}'
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


class Stylesheets(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.hrefs = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'link' and 'stylesheet' in values.get('rel', '').lower().split() and values.get('href'):
            self.hrefs.append(values['href'])


def validate_stylesheet_references(output):
    """Ship only stylesheets that at least one generated HTML page links."""
    output = Path(output)
    linked = set()
    for page in output.rglob('*.html'):
        page_url = ORIGIN + '/' + page.relative_to(output).as_posix()
        for href in Stylesheets(page.read_text(encoding='utf-8')).hrefs:
            target = urlsplit(urljoin(page_url, href))
            if target.netloc == urlsplit(ORIGIN).netloc:
                linked.add(unquote(target.path).lstrip('/'))
    unlinked = sorted(path.relative_to(output).as_posix() for path in output.rglob('*.css')
                      if path.relative_to(output).as_posix() not in linked)
    assert not unlinked, 'Stylesheets not linked by any generated page: ' + ', '.join(unlinked)


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


def validate_case_outputs(pages, resources):
    """Bind the script-free case subset, its full evidence, and its navigation."""
    cases = {record['id']: record for record in resources if record['kind'] == 'case-study'}
    normalize = lambda value: ' '.join(value.split())
    for language, prefix in (('en', ''), ('zh', '/zh')):
        route = prefix + '/cases/'
        assert route in pages, f'Missing case directory: {route}'
        page = pages[route]
        ids = [row['id'] for row in page.case_rows]
        assert len(ids) == len(cases) and set(ids) == set(cases), f'Case subset differs from curated case records: {route}'
        collections = list(schema_entities(page.schemas, 'CollectionPage'))
        assert len(collections) == 1, f'Case directory needs one CollectionPage: {route}'
        collection = collections[0]
        assert collection.get('url') == ORIGIN + route and collection.get('inLanguage') == ('zh-CN' if language == 'zh' else 'en'), f'Case schema identity mismatch: {route}'
        items = collection.get('mainEntity', {})
        assert items.get('@type') == 'ItemList' and items.get('numberOfItems') == len(cases), f'Case schema count mismatch: {route}'
        expected_items = []
        for position, row in enumerate(page.case_rows, 1):
            record = cases[row['id']]
            name = (record.get('name_zh') or record['name']) if language == 'zh' else record['name']
            detail = f"{prefix}/resources/{row['id']}/"
            expected_items.append({'@type': 'ListItem', 'position': position, 'name': name,
                                   'url': ORIGIN + detail, 'description': record[f'description_{language}']})
            assert row['anchor'] == row['id'] and row['section'] == collection_section(record), f'Case placement mismatch: {row["id"]}'
            assert row['parent_section'] == row['section'] and row['parent_anchor'] == 'cases-' + row['section'], f'Case belongs to the wrong subject section: {row["id"]}'
            assert len(row['headings']) == 1 and normalize(name) in normalize(''.join(row['headings'][0])), f'Case heading lost localized name: {row["id"]}'
            requirements = record['requirements_zh' if language == 'zh' else 'requirements']
            requirements = requirements if isinstance(requirements, list) else [requirements]
            text = normalize(' '.join(row['text']))
            assert all(normalize(phrase) in text for phrase in [name, record[f'description_{language}'], *requirements]), f'Case directory lost full localized content: {row["id"]}'
            links = {detail, record['url'], record['evidence_url'], *record.get('additional_evidence_urls', [])}
            assert links <= set(row['links']), f'Case directory lost entry/source links: {row["id"]}'
            assert len(row['times']) == 1 and row['times'][0]['datetime'] == record['verified_at'], f'Case review timestamp mismatch: {row["id"]}'
            assert record['verified_at'][:10] in normalize(''.join(row['times'][0]['text'])), f'Case review date is missing: {row["id"]}'
        assert items.get('itemListElement') == expected_items, f'Case structured list differs from rendered entries: {route}'


def validate_entry_outputs(pages, resources, papers):
    """Bind individual pages and their ordinary listing links to reviewed records."""
    routes = expected_entry_routes(resources, papers)
    catalogs = {'resource': {row['id']: row for row in resources},
                'paper': {row['id']: row for row in papers}}
    normalize = lambda value: ' '.join(value.split())
    for kind, directory in (('resource', 'resources'), ('paper', 'papers')):
        for language, prefix in (('en', ''), ('zh', '/zh')):
            listing = pages[f'{prefix}/{directory}/']
            links = listing.detail_links
            assert len(links) == len(catalogs[kind]), f'Detail link count mismatch: {prefix}/{directory}/'
            assert {link['id'] for link in links} == set(catalogs[kind]), f'Detail link IDs mismatch: {prefix}/{directory}/'
            for link in links:
                expected = f"{prefix}/{directory}/{link['id']}/"
                assert link['href'] == expected and link['target'] is None, f'Detail link must be an ordinary same-tab localized route: {expected}'
                assert link['container_id'] == link['id'], f'Detail link belongs to the wrong listing entry: {expected}'
                assert link['id'] in listing.ids, f'Legacy listing anchor missing: {expected}'
                record = catalogs[kind][link['id']]
                if kind == 'resource':
                    title = (record.get('name_zh') or record['name']) if language == 'zh' else record['name']
                else:
                    title = record['title_zh'] if language == 'zh' else record['title']
                label = '完整条目' if language == 'zh' else 'Full entry'
                accessible = f'{label}：{title}' if language == 'zh' else f'{label}: {title}'
                assert normalize(' '.join(link['text'])) == label and link['aria_label'] == accessible, f'Detail link label must identify its localized entry: {expected}'
                upstream = {record['url'], record['evidence_url']} if kind == 'resource' else {record['url'], record['pdf_url']}
                recorded_links = listing.record_links if kind == 'resource' else listing.paper_links
                assert upstream <= set(recorded_links.get(link['id'], [])), f'External listing title/source links missing: {expected}'

    siblings = section_siblings(resources)
    for route, (kind, identifier, language) in routes.items():
        assert route in pages, f'Missing detail page: {route}'
        page, record = pages[route], catalogs[kind][identifier]
        related = siblings.get(identifier) if kind == 'resource' else None
        if related and related['siblings']:
            prefix = '/zh' if language == 'zh' else ''
            expected = [entry_path('resource', sibling['id'], language) for sibling in related['siblings']]
            expected.append(f"{prefix}/resources/#heading-{related['section']}")
            if record['kind'] == 'case-study':
                expected.append(f"{prefix}/cases/#cases-{related['section']}")
            assert 1 <= len(related['siblings']) <= 6 and identifier not in {sibling['id'] for sibling in related['siblings']}, f'Detail page needs one to six other section entries: {route}'
            assert page.section_links == expected, f'Section siblings differ from README order: {route}'
        else:
            assert page.section_links is None, f'Only resources in shared sections list section siblings: {route}'
        canonical = ORIGIN + route
        locale = 'zh-CN' if language == 'zh' else 'en'
        assert page.entry_markers == [(kind, identifier)], f'Detail page identity mismatch: {route}'
        assert page.canonicals == [canonical] and page.lang == locale and not page.noindex, f'Detail canonical/language mismatch: {route}'
        english = route.removeprefix('/zh') if language == 'zh' else route
        expected_alternates = {'en': ORIGIN + english, 'zh-CN': ORIGIN + '/zh' + english,
                               'x-default': ORIGIN + english}
        assert len(page.alternates) == 3 and dict(page.alternates) == expected_alternates, f'Detail language alternatives mismatch: {route}'
        web_pages = list(schema_entities(page.schemas, 'WebPage'))
        assert len(web_pages) == 1, f'Detail page needs one WebPage entity: {route}'
        web_page = web_pages[0]
        entity_id = canonical + ('#resource' if kind == 'resource' else '#paper')
        assert (web_page.get('@id') == canonical + '#webpage' and web_page.get('url') == canonical
                and web_page.get('inLanguage') == locale and web_page.get('mainEntity') == {'@id': entity_id}), f'Detail WebPage metadata mismatch: {route}'
        breadcrumbs = list(schema_entities(page.schemas, 'BreadcrumbList'))
        assert len(breadcrumbs) == 1 and breadcrumbs[0].get('@id') == canonical + '#breadcrumb', f'Detail breadcrumbs missing: {route}'
        items = breadcrumbs[0].get('itemListElement', [])
        assert [item.get('position') for item in items] == [1, 2, 3], f'Detail breadcrumb positions mismatch: {route}'
        destinations = [item.get('item', {}).get('@id') if isinstance(item.get('item'), dict) else item.get('item') for item in items]
        prefix = '/zh' if language == 'zh' else ''
        directory = 'resources' if kind == 'resource' else 'papers'
        assert destinations == [ORIGIN + prefix + '/', ORIGIN + prefix + '/' + directory + '/', canonical], f'Detail breadcrumb destinations mismatch: {route}'
        assert len(page.entry_contents) == 1, f'Detail page needs one marked article: {route}'
        article = page.entry_contents[0]
        text = normalize(' '.join(article['text']))
        if kind == 'resource':
            name = (record.get('name_zh') or record['name']) if language == 'zh' else record['name']
            requirements = record.get('requirements_zh', record['requirements']) if language == 'zh' else record['requirements']
            requirements = requirements if isinstance(requirements, list) else [requirements]
            phrases = [name, record[f'description_{language}'], *requirements]
            links = {record['url'], record['evidence_url'], *record.get('additional_evidence_urls', [])}
            entities = list(schema_entities(page.schemas, 'CreativeWork'))
            assert len(entities) == 1 and entities[0].get('@id') == entity_id, f'Detail resource schema identity mismatch: {route}'
            entity = entities[0]
            assert (entity.get('url') == record['url'] and entity.get('name') == name
                    and entity.get('description') == record[f'description_{language}']), f'Detail resource schema content mismatch: {route}'
            assert not {'author', 'creator', 'datePublished', 'license', 'aggregateRating', 'review'}.intersection(entity), f'Unsupported resource schema claim: {route}'
        else:
            name = record['title_zh'] if language == 'zh' else record['title']
            phrases = [record['title_zh'] if language == 'zh' else record['title'],
                       '; '.join(record['authors']), record['venue'], record[f'description_{language}'],
                       record[f'scope_limitations_{language}'], record[f'why_fits_{language}'],
                       record['date_basis_zh' if language == 'zh' else 'date_basis'],
                       record['metadata_notes_zh' if language == 'zh' else 'metadata_notes']]
            if language == 'zh':
                phrases.append(record['title'])
            links = {record['url'], record['pdf_url'], *record['evidence_urls'], f'/papers/citations/{identifier}.bib'}
            links.update(record[field] for field in ('code_url', 'project_url') if record.get(field))
            entities = list(schema_entities(page.schemas, 'ScholarlyArticle'))
            expected = {**expected_paper_schema(record, language), '@id': entity_id}
            assert entities == [expected], f'Detail paper schema differs from recorded publication: {route}'
        assert (web_page.get('name') == name and web_page.get('description') == record[f'description_{language}']), f'Detail WebPage text mismatch: {route}'
        assert (page.meta.get('description') == record[f'description_{language}']
                and page.meta.get('og:url') == canonical
                and page.meta.get('og:locale') == ('zh_CN' if language == 'zh' else 'en_US')), f'Detail social metadata mismatch: {route}'
        assert len(article['headings']) == 1 and normalize(' '.join(article['headings'][0])) == normalize(name), f'Detail article needs one correctly localized H1: {route}'
        times = article['times']
        assert (len(times) == 1 and times[0]['datetime'] == record['verified_at']
                and normalize(' '.join(times[0]['text'])) == record['verified_at'][:10]), f'Detail review time differs from the source record: {route}'
        phrases.append(record['verified_at'][:10])
        assert all(normalize(phrase) in text for phrase in phrases), f'Detail page lost localized source content: {route}'
        assert links <= set(article['links']), f'Detail article lost upstream evidence or citation links: {route}'


def main():
    urls = [element.text for element in ET.parse(OUTPUT / 'sitemap.xml').findall('{*}url/{*}loc')]
    resources = json.loads((OUTPUT / 'catalog.json').read_text(encoding='utf-8'))['resources']
    papers = json.loads((OUTPUT / 'papers.json').read_text(encoding='utf-8'))
    validate_route_inventory(urls, resources, papers, include_browse=(OUTPUT / 'source-index.json').is_file())
    pages, fragment_links = {}, []
    for url in urls:
        parsed = urlsplit(url)
        assert parsed.netloc == 'awesomerea.org' and parsed.scheme == 'https' and not parsed.query and not parsed.fragment
        path = OUTPUT / parsed.path.lstrip('/') / 'index.html'
        text = path.read_text(encoding='utf-8')
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
            if target.fragment:
                fragment_links.append((parsed.path, link, local))
        validate_open_graph(parsed.path, page, png_size(OUTPUT / 'social-card.png'))
    validate_link_fragments(OUTPUT, pages, fragment_links)
    validate_homepage_destinations(pages)
    validate_paper_outputs(OUTPUT, pages)
    validate_entry_outputs(pages, resources, papers)
    validate_case_outputs(pages, resources)
    validate_artifact_links(OUTPUT, pages)
    validate_source_browser_output(OUTPUT)
    validate_stylesheet_references(OUTPUT)
    not_found = Page((OUTPUT / '404.html').read_text(encoding='utf-8'))
    assert not_found.noindex, '404 must be noindex'
    validate_open_graph(None, not_found, png_size(OUTPUT / 'social-card.png'))
    validate_security_headers(OUTPUT)
    validate_catalog_preload(OUTPUT)
    assert (OUTPUT / 'llms.txt').read_text(encoding='utf-8').startswith('# '), 'llms.txt must contain Markdown'
    assert re.fullmatch(r'[a-f0-9]{32}\n?', (OUTPUT / 'indexnow.txt').read_text(encoding='utf-8')), 'Invalid public ownership proof'
    read_build_manifest(OUTPUT)
    print(f'Validated {len(urls)} canonical HTML pages, paper/source/citation coverage, language alternatives, JSON-LD, Open Graph, local links, linked stylesheets, security headers, the homepage catalog preload and the deployment manifest.')


if __name__ == '__main__':
    main()
