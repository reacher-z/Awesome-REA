"""Build public, script-free collection, provenance, and navigation pages."""
from __future__ import annotations

from collections import defaultdict
import hashlib
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
from urllib.parse import unquote, urlsplit

from build_readme import KIND_LABELS, RELATIONSHIPS, REQUIREMENTS_LABEL, TARGETS, collection_section
from open_graph import open_graph_meta, website_reference
from requirement_facets import item_html, ordered_items
from source_scope import exclusion_counts, unavailable_clause


# The upstream project that the collection's name echoes.
REA_REPOSITORY_URL = 'https://github.com/morluto/rea'
# Collection pages share one link pattern: the title opens the original resource, “Full entry” the detail page,
# and this label marks the link to a record's evidence_url (homepage strings in site/app.js repeat it).
PRIMARY_SOURCE_LABEL = ('Primary source', '一手来源')
SECTIONS = {
    'website': ('Websites', '网站'),
    'game': ('Games', '游戏'),
    'app': ('Apps', '应用'),
    'native-binary': ('Native binaries', '原生二进制'),
    'firmware': ('Firmware and hardware', '固件与硬件'),
    'protocol': ('Protocols', '协议'),
    'agents-and-mcp': ('Agents and MCP', '智能体与 MCP'),
    'related-collections': ('Related collections', '相关资源合集'),
    'references-and-learning': ('References and learning', '文档与学习资源'),
}


def jsonld_script(value: dict) -> str:
    """Serialize JSON-LD without allowing upstream strings to close the script."""
    payload = json.dumps(value, ensure_ascii=False, separators=(',', ':'))
    for character, encoded in (('&', '\\u0026'), ('<', '\\u003c'), ('>', '\\u003e'),
                               ('\u2028', '\\u2028'), ('\u2029', '\\u2029')):
        payload = payload.replace(character, encoded)
    return f'<script type="application/ld+json">{payload}</script>'


def collection_page_schema(canonical: str, name: str, description: str,
                           language: str, items: list[dict], site_url: str) -> dict:
    """Describe precisely the rendered main list; positions follow DOM order."""
    return {
        '@context': 'https://schema.org',
        '@type': 'CollectionPage',
        '@id': canonical + '#collection',
        'url': canonical,
        'name': name,
        'description': description,
        'inLanguage': language,
        'isPartOf': website_reference(site_url),
        'mainEntity': {
            '@type': 'ItemList',
            'numberOfItems': len(items),
            'itemListElement': [
                {'@type': 'ListItem', 'position': position, **item}
                for position, item in enumerate(items, 1)
            ],
        },
    }


def breadcrumb_schema(canonical: str, trail: list[tuple[str, str]]) -> dict:
    """Mirror a visible breadcrumb as (name, absolute URL) pairs ending with the page itself."""
    return {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        '@id': canonical + '#breadcrumb',
        'itemListElement': [
            {'@type': 'ListItem', 'position': position, 'name': name, 'item': url}
            for position, (name, url) in enumerate(trail, 1)
        ],
    }


def _url(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme not in {'http', 'https'} or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError('Discovery pages require public web URLs without embedded credentials')
    return escape(value, quote=True)


def _asset(site_dir: Path, filename: str) -> str:
    path = site_dir / filename
    revision = hashlib.sha256(path.read_bytes()).hexdigest()[:16] if path.is_file() else ''
    return '/' + filename + ('?v=' + revision if revision else '')


def publication_keys(record: dict) -> set[tuple[str, str]]:
    """Match a paper's own canonical URL/DOI, never a tool's evidence links."""
    keys = set()
    doi = record.get('doi')
    if isinstance(doi, str) and doi.strip():
        doi = re.sub(r'^https?://(?:dx\.)?doi\.org/', '', doi.strip(), flags=re.I)
        keys.add(('doi', unquote(doi).casefold()))
    parsed = urlsplit(record.get('url') or '')
    host = (parsed.hostname or '').casefold()
    path = unquote(parsed.path).rstrip('/')
    if host in {'doi.org', 'dx.doi.org'}:
        keys.add(('doi', path.lstrip('/').casefold()))
    elif host in {'arxiv.org', 'www.arxiv.org'} and re.match(r'^/(?:abs|pdf)/', path):
        identifier = re.sub(r'^/(?:abs|pdf)/', '', path).removesuffix('.pdf')
        keys.add(('arxiv', re.sub(r'v\d+$', '', identifier).casefold()))
    elif host:
        keys.add(('url', host + path))
    return keys


def bibliography_overlap(resources: list[dict], papers: list[dict]) -> int:
    curated_keys = set().union(*(publication_keys(record) for record in resources))
    return sum(bool(publication_keys(paper) & curated_keys) for paper in papers)


class _IconStylesheet(HTMLParser):
    def __init__(self):
        super().__init__()
        self.href = None

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        href = attrs.get('href', '')
        if tag == 'link' and attrs.get('rel') == 'stylesheet' and urlsplit(href).path.endswith('fontawesome.css'):
            self.href = href if urlsplit(href).scheme or href.startswith('/') else '/' + href


def _requirements(record: dict, language: str) -> list[str]:
    key = 'requirements_zh' if language == 'zh' else 'requirements'
    value = record.get(key)
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{record.get('id')}: missing {key} for the static curated page")
    return value


def _resource_card(record: dict, language: str) -> str:
    zh = language == 'zh'
    detail_path = f"{'/zh' if zh else ''}/resources/{record['id']}/"
    name = (record.get('name_zh') or record['name']) if zh else record['name']
    detail_label = f'完整条目：{name}' if zh else f'Full entry: {name}'
    description = record[f'description_{language}']
    kind = KIND_LABELS[record['kind']][1 if zh else 0]
    targets = ' · '.join(TARGETS[target][1 if zh else 0] for target in record['targets'])
    requirements = ''.join(item_html(facet, item, language) for facet, item in ordered_items(record, _requirements(record, language)))
    additional = ''.join(
        f'<li><a href="{_url(url)}" target="_blank" rel="noopener">'
        f'{("补充来源" if zh else "Additional source")} {index} ↗</a></li>'
        for index, url in enumerate(record.get('additional_evidence_urls', []), 1)
    )
    reviewed = str(record['verified_at'])
    return f'''<article class="resource-card browse-repository" id="{escape(record['id'], quote=True)}" data-record-id="{escape(record['id'], quote=True)}" data-resource-id="{escape(record['id'], quote=True)}">
  <div class="card-heading"><h3><a class="card-title-link" href="{_url(record['url'])}" target="_blank" rel="noopener">{escape(name)}<span class="browse-text-arrow" aria-hidden="true">↗</span></a></h3><span class="resource-kind">{escape(kind)}</span></div>
  <p class="card-description">{escape(description)}</p>
  <div class="card-meta"><span>{escape(targets)}</span><a class="entry-detail-link" data-entry-link="{escape(record['id'], quote=True)}" href="{escape(detail_path, quote=True)}" aria-label="{escape(detail_label, quote=True)}">{('完整条目' if zh else 'Full entry')}</a></div>
  <details class="requirements"><summary>{escape(REQUIREMENTS_LABEL[zh])}</summary><ul>{requirements}</ul>{('<ul>' + additional + '</ul>' if additional else '')}<div class="resource-detail-meta"><span>{('来源已复核' if zh else 'Source-reviewed')}</span><time datetime="{escape(reviewed, quote=True)}">{('复核于' if zh else 'Reviewed')} {escape(reviewed[:10])}</time><a class="resource-evidence-link" href="{_url(record['evidence_url'])}" target="_blank" rel="noopener">{PRIMARY_SOURCE_LABEL[zh]} ↗</a></div></details>
</article>'''


def _case_row(record: dict, language: str, section: str) -> str:
    """Keep reported scope visible; link the original, the full entry and its primary source as /resources/ does."""
    zh = language == 'zh'
    name = (record.get('name_zh') or record['name']) if zh else record['name']
    identifier = escape(record['id'], quote=True)
    detail_path = f"{'/zh' if zh else ''}/resources/{identifier}/"
    detail_label = ('完整条目：' if zh else 'Full entry: ') + name
    relationship = RELATIONSHIPS[record['relationship']][int(zh)]
    targets = ' · '.join(TARGETS[target][int(zh)] for target in record['targets'])
    requirements = ''.join(item_html(facet, item, language) for facet, item in ordered_items(record, _requirements(record, language)))
    evidence = [(url, f'补充来源 {index}' if zh else f'Additional source {index}')
                for index, url in enumerate(record.get('additional_evidence_urls', []), 1)]
    evidence_links = ''.join(f'<li><a href="{_url(url)}" target="_blank" rel="noopener">{escape(label)} <span aria-hidden="true">↗</span></a></li>'
                             for url, label in evidence)
    reviewed = str(record['verified_at'])
    return f'''<article class="case-row" id="{identifier}" data-case-id="{identifier}" data-resource-id="{identifier}" data-case-section="{escape(section, quote=True)}">
  <div class="case-heading"><h3><a href="{_url(record['url'])}" target="_blank" rel="noopener">{escape(name)}<span class="browse-text-arrow" aria-hidden="true">↗</span></a></h3><span class="case-relationship">{escape(relationship)}</span></div>
  <p class="case-description">{escape(record[f'description_{language}'])}</p>
  <div class="case-footer"><div class="case-meta"><span class="case-targets">{escape(targets)}</span><a class="entry-detail-link" data-entry-link="{identifier}" href="{detail_path}" aria-label="{escape(detail_label, quote=True)}">{('完整条目' if zh else 'Full entry')}</a><a class="case-source" href="{_url(record['evidence_url'])}" target="_blank" rel="noopener">{PRIMARY_SOURCE_LABEL[zh]} <span aria-hidden="true">↗</span></a></div>
  <details class="case-evidence"><summary>{escape(REQUIREMENTS_LABEL[zh])}</summary><div class="case-evidence-body"><ul class="case-requirements">{requirements}</ul>{('<ul class="case-evidence-links">' + evidence_links + '</ul>' if evidence_links else '')}<p class="case-review-date"><time datetime="{escape(reviewed, quote=True)}">{('来源复核日期：' if zh else 'Source review: ')}{escape(reviewed[:10])}</time></p></div></details>
  </div>
</article>'''


def _suggest_link(repository_url: str, template: str, label: str) -> str:
    """Open an existing issue form, styled like the papers page's suggestion button."""
    return (f'<a class="button button-outline" href="{_url(repository_url + "/issues/new?template=" + template)}" '
            f'target="_blank" rel="noopener">{escape(label)} <span aria-hidden="true">↗</span></a>')


def _case_collection(resources: list[dict], language: str, site_url: str,
                     repository_url: str = 'https://github.com/reacher-z/Awesome-REA') -> tuple[str, list[dict]]:
    zh = language == 'zh'
    prefix = '/zh' if zh else ''
    groups = defaultdict(list)
    for record in resources:
        if record['kind'] == 'case-study':
            groups[collection_section(record)].append(record)
    sections, navigation, items = [], [], []
    for key, labels in SECTIONS.items():
        if not groups[key]:
            continue
        label = labels[int(zh)]
        navigation.append(f'<a href="#cases-{key}">{escape(label)}<span>{len(groups[key])}</span></a>')
        sections.append(f'<section class="case-section" id="cases-{key}" data-case-section="{key}" aria-labelledby="case-heading-{key}"><div class="browse-topline"><h2 id="case-heading-{key}">{escape(label)}</h2><p>{len(groups[key])} {("个案例" if zh else ("case" if len(groups[key]) == 1 else "cases"))}</p></div><div class="case-list">' + '\n'.join(_case_row(record, language, key) for record in groups[key]) + '</div></section>')
        for record in groups[key]:
            name = (record.get('name_zh') or record['name']) if zh else record['name']
            items.append({'name': name, 'url': f"{site_url}{prefix}/resources/{record['id']}/", 'description': record[f'description_{language}']})
    search = '/zh/?view=curated&amp;kind=case-study#catalog' if zh else '/?view=curated&amp;kind=case-study&amp;lang=en#catalog'
    note = ('案例已计入精选总数，每项按主要用途出现一次，并保留所有目标标签。来源核查不代表本合集已独立运行验证或确认 REA 参与。'
            if zh else 'These cases are part of the curated total and appear once under their primary subject, with all target labels retained. Source review does not imply independent runtime verification or REA involvement.')
    nav = f'<nav class="browse-category-nav cases-nav" aria-label="{("案例主题" if zh else "Case subjects")}">{"".join(navigation)}</nav>' if navigation else ''
    empty = '' if items else f'<p class="cases-empty">{("当前目录还没有案例条目。" if zh else "No case studies are currently listed.")}</p>'
    content = f'''<div class="cases-collection" data-case-count="{len(items)}" data-curated-count="{len(resources)}">
<div class="browse-actions"><a class="button button-primary" href="{search}">{('搜索案例' if zh else 'Search cases')}</a><a class="button button-outline" href="{prefix}/resources/">{('全部精选资源' if zh else 'All resources')}</a>{_suggest_link(repository_url, 'case-study.yml', '推荐重建案例' if zh else 'Suggest a case study')}</div>
<details class="cases-note"><summary>{('关于这些案例' if zh else 'About these cases')}</summary><p>{escape(note)}</p></details>{nav}{''.join(sections)}{empty}
</div>'''
    return content, items


def _document(*, site_url: str, repository_url: str, path: str, language: str,
              title: str, description: str, content: str, schema: dict | None,
              assets: dict, icon_stylesheet: str | None, noindex: bool = False,
              main_class: str = '', extra_styles: tuple[str, ...] = (),
              source_export: str = 'source-index.json') -> str:
    if source_export not in ('source-index.json', 'source-published.json'):
        raise ValueError('Unsupported repository export route')
    zh = language == 'zh'
    locale = 'zh-CN' if zh else 'en'
    root = '/zh/' if zh else '/'
    english_path = path.removeprefix('/zh') if zh else path
    chinese_path = '/zh' + english_path
    counterpart = english_path if zh else chinese_path
    canonical = site_url + path
    metadata = '<meta name="robots" content="noindex">' if noindex else f'''<link rel="canonical" href="{_url(canonical)}">
  <link rel="alternate" hreflang="en" href="{_url(site_url + english_path)}">
  <link rel="alternate" hreflang="zh-CN" href="{_url(site_url + chinese_path)}">
  <link rel="alternate" hreflang="x-default" href="{_url(site_url + english_path)}">'''
    globe_icon = '<span class="icon fa-symbol fa-globe" aria-hidden="true"></span>' if icon_stylesheet else ''
    github_icon = ('<span class="icon fa-symbol fa-github" aria-hidden="true"></span>' if icon_stylesheet
                   else '<span class="icon browse-github-fallback" aria-hidden="true">GH</span>')
    language_link = '' if noindex else f'<a class="browse-language" href="{counterpart}" lang="{("en" if zh else "zh-CN")}" hreflang="{("en" if zh else "zh-CN")}">{globe_icon}<span>{("English" if zh else "简体中文")}</span></a>'
    prefix = '/zh' if zh else ''
    # The bilingual 404 template has no canonical address or language counterpart.
    social = open_graph_meta(language=language, title=title + ' · AwesomeREA.org', description=description,
                             image_url=site_url + assets['social'],
                             url=None if noindex else canonical, paired=not noindex)
    footer = ('原创说明和代码采用 MIT 许可；上游描述与链接项目保留各自的许可。' if zh
              else 'Original editorial content and code: MIT. Upstream descriptions and linked projects retain their own licenses.')
    extra_css = ''.join(f'\n  <link rel="stylesheet" href="{escape(href, quote=True)}">' for href in extra_styles)
    page_class = ' ' + escape(main_class, quote=True) if main_class else ''
    return f'''<!doctype html>
<html lang="{locale}"{(' data-icon-set="fontawesome"' if icon_stylesheet else '')}>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#ffffff">
  <title>{escape(title)} · AwesomeREA.org</title>
  <meta name="description" content="{escape(description, quote=True)}">
  {metadata}
  {social}
  <link rel="icon" href="{assets['favicon']}" type="image/svg+xml">
  <link rel="stylesheet" href="{assets['styles']}">
  <link rel="stylesheet" href="{assets['browse']}">{extra_css}
  {('<link rel="stylesheet" href="' + escape(icon_stylesheet, quote=True) + '">' if icon_stylesheet else '')}
  {jsonld_script(schema) if schema else ''}
  {'' if noindex else jsonld_script(breadcrumb_schema(canonical, [('首页' if zh else 'Home', site_url + root), (title, canonical)]))}
</head>
<body>
<a class="skip-link" href="#discovery-content">{('跳到内容' if zh else 'Skip to content')}</a>
<header class="site-header"><div class="shell header-inner">
  <a class="wordmark" href="{root}" aria-label="{('AwesomeREA.org 首页' if zh else 'AwesomeREA.org home')}"><img class="brand-mark" src="{assets['favicon']}" alt="" width="33" height="33" aria-hidden="true"><span>Awesome<span class="wordmark-rea">REA</span><span class="wordmark-domain">.org</span></span></a>
  <nav class="header-nav" aria-label="{('主导航' if zh else 'Main navigation')}">{language_link}<a class="github-link" href="{_url(repository_url)}" target="_blank" rel="noopener" aria-label="GitHub">{github_icon}<span>GitHub</span></a></nav>
</div></header>
<main id="discovery-content" class="shell browse-main{page_class}">
  <nav class="browse-breadcrumbs" aria-label="{('当前位置' if zh else 'Breadcrumb')}"><a href="{root}">{('首页' if zh else 'Home')}</a><span aria-hidden="true">/</span><span aria-current="page">{escape(title)}</span></nav>
  <section class="collection-intro browse-intro"><p class="eyebrow">{('逆向工程资源集合' if zh else 'THE REVERSE ENGINEERING COLLECTION')}</p><h1>{escape(title)}<span class="title-dot" aria-hidden="true">.</span></h1><p>{escape(description)}</p></section>
  {content}
</main>
<footer class="site-footer"><div class="shell footer-top"><p>{('独立的资源集合，在公开协作中持续更新。' if zh else 'An independent resource collection, updated in public.')}</p><div class="footer-links"><a href="{prefix}/resources/">{('精选资源' if zh else 'Curated resources')}</a><a href="{prefix}/cases/">{('案例合集' if zh else 'Case studies')}</a><a href="{prefix}/browse/">{('仓库目录' if zh else 'Repository directory')}</a><a href="{prefix}/papers/">{('研究论文' if zh else 'Research papers')}</a><a href="{prefix}/about/">{('关于与来源' if zh else 'About and sources')}</a><a href="/catalog.json" download="awesomerea-curated-catalog.json">{('精选 JSON ↓' if zh else 'Curated JSON ↓')}</a><a href="/{source_export}" download="awesomerea-repository-index.json">{('仓库 JSON ↓' if zh else 'Repository JSON ↓')}</a></div></div><div class="shell footer-bottom">{footer}</div></footer>
</body>
</html>
'''


def build_discovery_pages(site_dir: Path, catalog: dict, source_index: dict | None) -> list[str]:
    """Write discovery assets and return six root-relative HTML sitemap paths.

    ``catalog`` is the built catalog object with localized names and requirements.
    ``source_index`` is the full localized/scoped scan, including excluded records.
    Copy papers.json and the normal site assets into site_dir before this call.
    """
    site_dir = Path(site_dir)
    metadata = catalog.get('meta', {})
    site_url = metadata.get('site_url', 'https://awesomerea.org').rstrip('/')
    repository_url = metadata.get('repository_url', 'https://github.com/reacher-z/Awesome-REA').rstrip('/')
    _url(site_url)
    _url(repository_url)
    resources = catalog['resources']
    case_count = sum(record['kind'] == 'case-study' for record in resources)
    if len({record['id'] for record in resources}) != len(resources):
        raise ValueError('Duplicate curated IDs in discovery pages')
    scanned = [record for record in (source_index or {}).get('resources', []) if record.get('scan_status') == 'readme-scanned']
    excluded = sum(record.get('scope_status') == 'excluded' for record in scanned)
    out_of_scope, unavailable = exclusion_counts(scanned)
    browse_count = len(scanned) - excluded
    published = (source_index or {}).get('meta', {}).get('kind') == 'published-repository-selection'
    source_export = 'source-published.json' if published else 'source-index.json'
    paper_path = site_dir / 'papers.json'
    papers = json.loads(paper_path.read_text(encoding='utf-8')) if paper_path.is_file() else []
    if not isinstance(papers, list):
        raise ValueError('papers.json must contain a separate array of paper records')
    overlapping_papers = bibliography_overlap(resources, papers)
    scan_date = str((source_index or {}).get('meta', {}).get('published_at' if published else 'completed_at') or '')[:10]
    assets = {key: _asset(site_dir, filename) for key, filename in (
        ('styles', 'styles.css'), ('browse', 'browse.css'), ('favicon', 'favicon.svg'), ('social', 'social-card.png'))}
    icons = _IconStylesheet()
    index = site_dir / 'index.html'
    if index.is_file():
        icons.feed(index.read_text(encoding='utf-8'))
    groups = defaultdict(list)
    for record in resources:
        section = collection_section(record)
        if section not in SECTIONS:
            raise ValueError(f'Unknown curated collection section: {section}')
        for language in ('en', 'zh'):
            if not isinstance(record.get(f'description_{language}'), str):
                raise ValueError(f"{record['id']}: missing localized description")
            _requirements(record, language)
        groups[section].append(record)

    rendered = {}
    paths = []
    for language in ('en', 'zh'):
        zh = language == 'zh'
        locale = 'zh-CN' if zh else 'en'
        prefix = '/zh' if zh else ''
        path = prefix + '/resources/'
        title = '精选逆向工程资源' if zh else 'Curated reverse engineering resources'
        description = (f'{len(resources):,} 项工具、项目、集成、案例与参考资源，覆盖网站、游戏、应用、原生二进制、固件及通信协议。'
                       if zh else f'{len(resources):,} tools, projects, integrations, case studies, and references for websites, games, apps, native binaries, firmware, and communication protocols.')
        note = ('“来源已复核”表示说明已依据一手文档核对，不代表已安装、执行、安全审计或验证兼容性。使用条件和复核日期随条目保留。'
                if zh else 'Source-reviewed means descriptions were checked against primary documentation. It does not mean installation, execution, security auditing, or compatibility testing. Each entry retains requirements and its review date.')
        sections, items, navigation = [], [], []
        for key, labels in SECTIONS.items():
            if not groups[key]:
                continue
            label = labels[1 if zh else 0]
            navigation.append(f'<a href="#{key}">{escape(label)}<span>{len(groups[key])}</span></a>')
            sections.append(f'<section aria-labelledby="heading-{key}"><div class="browse-topline"><h2 id="heading-{key}"><a id="{key}"></a>{escape(label)}</h2><p>{len(groups[key])} {("项资源" if zh else "resources")}</p></div><div class="resource-grid">' + '\n'.join(_resource_card(record, language) for record in groups[key]) + '</div></section>')
            for record in groups[key]:
                name = (record.get('name_zh') or record['name']) if zh else record['name']
                # Items identify the site's own entry pages, as /cases/ does; card titles still link upstream.
                items.append({'name': name, 'url': f"{site_url}{prefix}/resources/{record['id']}/", 'description': record[f'description_{language}']})
        content = f'''<div class="browse-actions"><a class="button button-primary" href="{('/zh/?view=curated' if zh else '/?view=curated&amp;lang=en')}">{('搜索与筛选' if zh else 'Search and filter')}</a><a class="button button-outline" href="{prefix}/browse/">{('浏览仓库' if zh else 'Browse repositories')}</a><a class="button button-outline" href="{prefix}/papers/">{('研究论文' if zh else 'Research papers')}</a>{_suggest_link(repository_url, 'resource.yml', '推荐资源' if zh else 'Suggest a resource')}<a class="browse-download" href="/catalog.json" download="awesomerea-curated-catalog.json">{('下载精选 JSON ↓' if zh else 'Download curated JSON ↓')}</a></div>
<details class="browse-provenance"><summary>{("来源复核与验证范围" if zh else "Source review and testing limits")}</summary><p>{escape(note)}</p></details><nav class="browse-category-nav" aria-label="{('资源分类' if zh else 'Resource categories')}">{''.join(navigation)}</nav>{''.join(sections)}'''
        rendered[path] = _document(site_url=site_url, repository_url=repository_url, path=path, language=language, title=title, description=description, content=content, schema=collection_page_schema(site_url + path, title, description, locale, items, site_url), assets=assets, icon_stylesheet=icons.href, source_export=source_export)
        paths.append(path)

        path = prefix + '/cases/'
        title = '逆向工程案例合集' if zh else 'Reverse-engineering case studies'
        content, items = _case_collection(resources, language, site_url, repository_url)
        description = (f'从 {len(resources):,} 项精选资源中筛选出的 {len(items):,} 个案例，保留重建方法、成果边界与原始证据。'
                       if zh else f'{len(items):,} case studies from {len(resources):,} curated resources, with documented reconstruction methods, scope, and original evidence.')
        rendered[path] = _document(site_url=site_url, repository_url=repository_url, path=path, language=language, title=title, description=description, content=content, schema=collection_page_schema(site_url + path, title, description, locale, items, site_url), assets=assets, icon_stylesheet=icons.href, source_export=source_export, main_class='cases-main', extra_styles=(_asset(site_dir, 'cases.css'),))
        paths.append(path)

        path = prefix + '/about/'
        title = '关于合集与数据来源' if zh else 'About the collection and its sources'
        description = ('AwesomeREA.org 是独立的逆向工程资源合集，收录工具、项目、案例和参考资料。' if zh else 'AwesomeREA.org is an independent collection of reverse-engineering tools, projects, case studies, and references.')
        summary = (f'{len(resources):,} 项精选资源；{len(scanned):,} 个实际读取 README 的仓库；{browse_count:,} 个可浏览条目。{out_of_scope} 个超出范围的条目{unavailable_clause(unavailable, zh)}保留在完整扫描数据中。'
                   if zh else f'{len(resources):,} curated resources; {len(scanned):,} repositories whose READMEs were fetched; {browse_count:,} browsable entries. The {out_of_scope} out-of-scope entries{unavailable_clause(unavailable, zh)} remain in the complete scan data.')
        if published:
            summary = (f'{len(resources):,} 项精选资源；仓库发布选集包含 {len(scanned):,} 条已采集记录，其中 {browse_count:,} 条可浏览。{out_of_scope} 个范围排除条目{unavailable_clause(unavailable, zh)}保留在发布 JSON 中。原始扫描的累计数量保留在各自的来源证据中。'
                       if zh else f'{len(resources):,} curated resources; the published repository selection contains {len(scanned):,} captured records, including {browse_count:,} browsable entries. The {out_of_scope} scope-excluded entries{unavailable_clause(unavailable, zh)} remain in the published JSON. Original capture totals remain separate in their source evidence.')
        if papers:
            summary += (f' 研究论文目录单独整理 {len(papers):,} 篇论文，其中 {overlapping_papers:,} 篇也收录于这 {len(resources):,} 项精选资源。上述数量不能相加作为独立项目总数。'
                        if zh else f' The paper bibliography lists {len(papers):,} papers; {overlapping_papers:,} of these also appear among the {len(resources):,} curated resources. Do not sum these counts as unique projects.')
        evidence = ('精选说明依据一手来源核对，并保留使用条件和复核日期。自动扫描记录来源、时间、README 字节数、Git blob 标识和 SHA-256；未执行上游代码，也不重新发布 README 正文。'
                    if zh else 'Curated descriptions are checked against primary sources, with requirements and review dates retained. Automated scans record sources, timestamps, README byte counts, Git blob identifiers, and SHA-256 hashes. Upstream code is not executed and README bodies are not republished.')
        if scan_date:
            evidence += ((f' 选集发布日期：{scan_date} UTC。' if zh else f' Selection published: {scan_date} UTC.')
                         if published else (f' 最新扫描快照：{scan_date} UTC。' if zh else f' Latest scan snapshot: {scan_date} UTC.'))
        scope = ('自动发现与精选资源分开维护。范围排除决定绑定具体 README 哈希，并保留双语原因。分类来自元数据；收录、翻译和范围判断都不等于运行验证、安全保证或 REA 集成。'
                 if zh else 'Automatic discovery remains separate from curation. Scope exclusions are tied to recorded README hashes and include bilingual reasons. Categories derive from metadata; inclusion, translation, and scope decisions do not establish runtime verification, safety, or REA integration.')
        licensing = ('本仓库原创说明和代码采用 MIT 许可。上游项目及其描述保留各自许可；许可证标识仅是采集时元数据。生成的双语索引保留 description_original 上游原文，翻译由 AI 辅助完成。'
                     if zh else 'Original editorial content and code in this repository use the MIT license. Upstream projects and their descriptions retain their own licenses; license identifiers are metadata snapshots. The generated bilingual index preserves upstream text as description_original, and translations are AI-assisted.')
        facts = [('收录范围' if zh else 'What is collected', summary), ('来源与更新' if zh else 'Evidence and updates', evidence), ('范围与复核' if zh else 'Scope and review', scope), ('语言与许可' if zh else 'Languages and licenses', licensing)]
        # Same wording as the README About sections; the label comes from the shared relationship vocabulary.
        documentation_label = RELATIONSHIPS['official-documentation'][1 if zh else 0]
        rea_text = (f'是单独维护的上游 CLI 与 MCP 项目。本合集名称与之呼应，但并非 REA 官方仓库；条目标签及“{documentation_label}”等关系标注中的 REA 均指该项目。'
                    if zh else f"is a separate upstream CLI and MCP project. This collection's name echoes it, but it is not the REA repository; “REA” in entry tags and labels such as “{documentation_label}” refers to that project.")
        rea = f'<a href="{_url(REA_REPOSITORY_URL)}">{("REA（Reverse Engineer Anything）" if zh else "REA (Reverse Engineer Anything)")}</a> {escape(rea_text)}'
        fact_cards = f'<section class="source-card browse-repository"><h2>{("与 REA 的关系" if zh else "REA and this collection")}</h2><p class="card-description">{rea}</p></section>'
        fact_cards += ''.join(f'<section class="source-card browse-repository"><h2>{escape(heading)}</h2><p class="card-description">{escape(text)}</p></section>' for heading, text in facts)
        companion_url = 'https://aicanwhat.com/zh/' if zh else 'https://aicanwhat.com/'
        companion_description = ('收录 AI 参与开发的游戏、网站与应用，以及智能体训练和评测使用的环境、基准和数据集。每个项目保留原始来源、开发方式说明和使用限制。'
                                 if zh else 'A directory of games, websites, and apps made with AI, plus environments, benchmarks, and datasets for training and evaluating agents. Each project retains original sources, development evidence, and practical limits.')
        fact_cards += f'<section class="source-card browse-repository"><h2>{("相关目录" if zh else "Companion directory")}</h2><p class="card-description"><a href="{companion_url}">AI Can What?</a> — {companion_description}</p></section>'
        links = [
            (prefix + '/resources/', '精选资源' if zh else 'Curated resources'),
            (prefix + '/browse/', '完整仓库目录' if zh else 'Repository directory'),
            (prefix + '/papers/', '研究论文目录' if zh else 'Research papers'),
            (prefix + '/survey/', '专题综述' if zh else 'Editorial survey'),
            ('/catalog.json', '精选资源 JSON' if zh else 'Curated catalog JSON'),
            ('/' + source_export, ('已发布仓库选集 JSON' if zh else 'Published repository selection JSON') if published
             else ('完整双语扫描 JSON' if zh else 'Complete bilingual scan JSON')),
            ('/papers.json', '论文元数据 JSON' if zh else 'Paper metadata JSON'),
            (repository_url + '/blob/main/' + ('README.zh-CN.md' if zh else 'README.md'), 'GitHub README'),
            (repository_url + '/blob/main/docs/source-scan.md', '扫描方法（英文）' if zh else 'Scan methodology'),
            (repository_url + '/blob/main/data/source-scope.json', '范围排除记录' if zh else 'Scope exclusion records'),
            (repository_url + '/blob/main/data/README.md', '数据格式与维护（英文）' if zh else 'Data format and maintenance'),
            (repository_url + '/blob/main/LICENSE', 'MIT 许可证' if zh else 'MIT license'),
            (repository_url + '/blob/main/' + ('CONTRIBUTING.zh-CN.md' if zh else 'CONTRIBUTING.md'), '贡献指南' if zh else 'Contribution guide'),
        ]
        if published:
            links.append(('/source-index.json', '原始规范扫描基线 JSON' if zh else 'Original canonical scan baseline JSON'))
            links.extend((entry['archive_url'], ('原始公开采集证据 ' if zh else 'Original public capture evidence ')
                          + str(entry['run']['id'])) for entry in source_index['meta']['capture_sources'])
        link_html = ''.join(f'<a href="{(_url(url) if url.startswith("http") else escape(url, quote=True))}">{escape(label)}</a>' for url, label in links)
        content = f'<div class="source-results">{fact_cards}</div><section><div class="browse-topline"><h2>{("浏览、下载与来源" if zh else "Browse, download, and inspect sources")}</h2></div><nav class="browse-category-nav" aria-label="{("来源与下载" if zh else "Sources and downloads")}">{link_html}</nav></section>'
        schema = {'@context': 'https://schema.org', '@type': 'AboutPage', 'url': site_url + path, 'name': title, 'description': description, 'inLanguage': locale, 'about': website_reference(site_url)}
        rendered[path] = _document(site_url=site_url, repository_url=repository_url, path=path, language=language, title=title, description=description, content=content, schema=schema, assets=assets, icon_stylesheet=icons.href, source_export=source_export)
        paths.append(path)

    # Remove only this generator's former route outputs; redirects belong to the site build.
    for legacy in ('curated', 'zh/curated'):
        directory = site_dir / legacy
        if directory.is_dir():
            shutil.rmtree(directory)
    for path, document in rendered.items():
        destination = site_dir / path.lstrip('/') / 'index.html'
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(document, encoding='utf-8')

    paper_summary = (f' The bibliography lists {len(papers)} research papers; {overlapping_papers} also appear among the {len(resources)} curated resources.' if papers else '')
    llms = f'''# Awesome Reverse Engineering Anything

> AwesomeREA.org is an independent bilingual collection of reverse-engineering tools, projects, integrations, case studies, and references for websites, games, apps, native binaries, firmware, and communication protocols.

The collection contains {len(resources)} source-reviewed curated resources and {browse_count} browsable repositories from {len(scanned)} successful README scans. The full scan retains {excluded} scope-excluded records and their reasons.{paper_summary} These counts describe different collections and must not be combined as unique projects.

Source review checks documentation, not successful execution, security, or REA compatibility. Repository descriptions have AI-assisted English and Simplified Chinese translations; description_original retains available upstream text. New oversized descriptions are omitted with length and SHA-256 evidence in description_omission. Upstream content keeps its own license.

## English navigation

- [Curated resources]({site_url}/resources/): All curated entries, requirements, evidence links, and review dates.
- [Case studies]({site_url}/cases/): {case_count} documented cases, a subset of the curated resources, with full descriptions and source evidence.
- [Repository directory]({site_url}/browse/): Static categories and public repository descriptions.
- [Research papers]({site_url}/papers/): A separate research bibliography.
- [Editorial survey]({site_url}/survey/): A bilingual synthesis of the collection’s evidence, methods and limits; a versioned editorial companion, not an additional research paper.
- [About and provenance]({site_url}/about/): Scope, source methods, counts, translations, and licenses.

## 简体中文

- [精选资源]({site_url}/zh/resources/): 精选条目、使用条件、来源链接与复核日期。
- [案例合集]({site_url}/zh/cases/): {case_count} 个案例，是精选资源的子集，保留完整说明与来源证据。
- [仓库目录]({site_url}/zh/browse/): 静态分类与公开项目简介。
- [研究论文]({site_url}/zh/papers/): 单独维护的研究文献目录。
- [专题综述]({site_url}/zh/survey/): 综合比较证据、方法与边界的双语编辑性综述，单独版本化，不计入研究论文数量。
- [关于与来源]({site_url}/zh/about/): 收录范围、来源方法、数量、翻译与许可。

## Public data and sources

- [Data manifest]({site_url}/data-manifest.json): Curated resources and papers only, with separate counts, file URLs, sizes and SHA-256 checksums; repository-discovery exports are listed separately below.
- [Clone the public catalog]({repository_url}): Run `git clone {repository_url}.git`, then read `data/README.md` for the curated JSON source files and Chinese translations. No installation or build is required to read the data.
- [Curated records JSONL]({site_url}/downloads/records.jsonl): One resource or paper per line; preserves source evidence, bilingual descriptions and limitations.
- [Curated catalog JSON]({site_url}/catalog.json): Curated descriptions and source evidence.
- [Full repository index JSON]({site_url}/source-index.json): All scan records, original descriptions, translations, hashes, and exclusions; omit scope_status=excluded when reconstructing the browse list.
- [Browsable repository JSON]({site_url}/source-browser.json): Compact visible records. Follow `meta.full_export` for the complete companion and verify `meta.full_export_sha256`; the metadata selects the preserved baseline or a ready published selection.
- [Paper metadata JSON]({site_url}/papers.json): The separate research bibliography.
- [Public source repository]({repository_url}): Bilingual READMEs, contribution rules, code, and data definitions.
- [Scan methodology]({repository_url}/blob/main/docs/source-scan.md): Collection and scope-review methods.

This file is a navigation aid. Crawl policy is published in [robots.txt]({site_url}/robots.txt).
'''
    if published:
        old_summary = f'The collection contains {len(resources)} source-reviewed curated resources and {browse_count} browsable repositories from {len(scanned)} successful README scans. The full scan retains {excluded} scope-excluded records and their reasons.'
        new_summary = f'The collection contains {len(resources)} source-reviewed curated resources and a published selection of {len(scanned)} captured repository records, of which {browse_count} are browsable. The {out_of_scope} scope-excluded records{unavailable_clause(unavailable, False)} remain in the published selection; original capture totals remain separate in its provenance.'
        llms = llms.replace(old_summary, new_summary)
        llms = llms.replace(f'- [Full repository index JSON]({site_url}/source-index.json): All scan records, original descriptions, translations, hashes, and exclusions; omit scope_status=excluded when reconstructing the browse list.',
            f'- [Published repository selection JSON]({site_url}/source-published.json): Published records, original descriptions, translations, hashes, exclusions and per-source capture totals; omit scope_status=excluded when reconstructing the browse list.\n- [Canonical capture baseline JSON]({site_url}/source-index.json): The preserved original complete canonical scan export.')
    (site_dir / 'llms.txt').write_text(llms, encoding='utf-8')
    content = '''<div class="empty-state"><p>This address does not match a page in the collection.</p><p lang="zh-CN">这个地址没有对应的合集页面。</p><div class="browse-actions"><a class="button button-primary" href="/">Home · 首页</a><a class="button button-outline" href="/browse/">Browse repositories</a><a class="button button-outline" href="/zh/browse/" lang="zh-CN">浏览仓库</a></div></div>'''
    (site_dir / '404.html').write_text(_document(site_url=site_url, repository_url=repository_url, path='/404.html', language='en', title='Page not found · 页面不存在', description='This page could not be found. 这个页面不存在。', content=content, schema=None, assets=assets, icon_stylesheet=icons.href, source_export=source_export, noindex=True), encoding='utf-8')
    return paths
