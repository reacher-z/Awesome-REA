#!/usr/bin/env python3
"""Render the repository directory as dependency-free, bilingual HTML pages."""
from __future__ import annotations

from collections import defaultdict
from html import escape
from pathlib import Path
import shutil
from urllib.parse import urlsplit

from build_discovery_pages import breadcrumb_schema, collection_page_schema, jsonld_script
from open_graph import open_graph_meta
from build_repository_index import CATEGORIES
from source_descriptions import description_fallback
from source_scope import exclusion_counts, unavailable_clause

CATEGORY_ICONS = {
    'web-analysis': 'globe', 'game-analysis': 'gamepad', 'android': 'phone',
    'managed-code': 'code', 'native-analysis': 'chip', 'dynamic-analysis': 'terminal',
    'firmware': 'layers', 'protocol-analysis': 'network', 'reverse-engineering': 'book',
}


def browse_path(language: str, category: str | None = None) -> str:
    prefix = '/zh/browse/' if language == 'zh' else '/browse/'
    return prefix + (category + '/' if category else '')


def external_url(value: str) -> str:
    """Keep upstream URLs literal while rejecting non-web destinations."""
    parsed = urlsplit(value)
    if parsed.scheme not in {'http', 'https'} or not parsed.netloc:
        raise ValueError('Repository browse links must be absolute HTTP(S) URLs')
    return escape(value, quote=True)


def icon(name: str, use_pro: bool) -> str:
    if use_pro:
        return f'<span class="icon fa-symbol fa-{name}" aria-hidden="true"></span>'
    if name == 'github':
        return '<span class="icon browse-github-fallback" aria-hidden="true">GH</span>'
    if name == 'external':
        return '<span class="browse-text-arrow" aria-hidden="true">↗</span>'
    return ''


def related_links(record: dict, language: str) -> str:
    groups = []
    for kind, labels, route in (('paper', ('Related research', '相关研究'), 'papers'),
                                 ('curated', ('Curated details', '精选资料'), 'resources')):
        links = []
        for entry in record.get('related_entries', []):
            if entry.get('kind') != kind:
                continue
            identifier = entry['id']
            href = ('/zh' if language == 'zh' else '') + f'/{route}/{identifier}/'
            if entry[f'href_{language}'] != href:
                raise ValueError('Related entry must use its internal detail page')
            links.append(f'<li><a class="source-related-link" href="{escape(href, quote=True)}">'
                         f'{escape(entry[f"title_{language}"])}</a></li>')
        if links:
            label = labels[language == 'zh']
            groups.append(f'<div class="source-related-group"><span class="source-related-label">'
                          f'{label}</span><ul class="source-related-links" aria-label="{label}">'
                          + ''.join(links) + '</ul></div>')
    return '<div class="source-related">' + ''.join(groups) + '</div>' if groups else ''


def repository_card(record: dict, language: str, use_pro: bool) -> str:
    zh = language == 'zh'
    name = record.get('full_name') or record['name']
    owner, separator, project = name.partition('/')
    title = (f'<span class="source-owner">{escape(owner)}/</span>'
             f'<span class="source-project">{escape(project)}</span>' if separator else escape(name))
    description = record[f'description_{language}'] or description_fallback(record, language)
    stars = record.get('stars')
    star_html = (f'<span class="source-stars" title="{("采集时的星标快照" if zh else "Stars at collection time")}">'
                 f'{stars:,} {("星标" if zh else "stars")}</span>' if isinstance(stars, int) else '')
    license_name = record.get('license')
    if not isinstance(license_name, str) or not license_name.strip() or license_name.upper() == 'NOASSERTION':
        license_name = '许可证未识别' if zh else 'License not identified'
    return f'''<article class="source-card browse-repository" id="{escape(record['id'], quote=True)}" data-record-id="{escape(record['id'], quote=True)}">
  <div class="source-card-head"><h2><a class="source-title-link" href="{external_url(record['url'])}" target="_blank" rel="noopener">{title}{icon('external', use_pro)}</a></h2>{star_html}</div>
  <p class="source-card-description">{escape(description)}</p>
{related_links(record, language)}
  <div class="source-card-footer"><a href="{external_url(record.get('readme_url') or record['url'])}" target="_blank" rel="noopener">README ↗</a><span class="source-card-license">{escape(license_name)}</span></div>
</article>'''


def build_browse_pages(
    output: Path,
    source_document: dict | None,
    *,
    curated_count: int,
    site_url: str,
    repository_url: str,
    styles_href: str,
    browse_styles_href: str,
    favicon_href: str,
    social_image_href: str,
    data_revision: str,
    icon_stylesheet_href: str | None = None,
) -> list[str]:
    """Write two indexes plus nine category pairs and return their canonical URLs."""
    owned_directories = (output / 'browse', output / 'zh' / 'browse')
    if not source_document:
        for directory in owned_directories:
            if directory.exists():
                shutil.rmtree(directory)
        return []

    scanned = [record for record in source_document.get('resources', []) if record.get('scan_status') == 'readme-scanned']
    records = [record for record in scanned if record.get('scope_status') != 'excluded']
    out_of_scope, unavailable = exclusion_counts(scanned)
    identifiers = [record['id'] for record in records]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError('Duplicate repository IDs in browse pages')
    groups: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        if record['category'] not in CATEGORIES:
            raise ValueError(f"Unknown repository browse category: {record['category']}")
        for field in ('description_en', 'description_zh'):
            if not isinstance(record.get(field), str):
                raise ValueError(f"{record['id']}: missing localized browse description")
        groups[record['category']].append(record)
    for category_records in groups.values():
        category_records.sort(key=lambda record: (-(record.get('stars') or 0), record['full_name'].casefold()))

    use_pro = icon_stylesheet_href is not None
    published = source_document.get('meta', {}).get('kind') == 'published-repository-selection'
    scan_date = str(source_document.get('meta', {}).get('published_at' if published else 'completed_at') or '')[:10]
    canonical_urls = []
    rendered = {}
    for language in ('en', 'zh'):
        zh = language == 'zh'
        locale = 'zh-CN' if zh else 'en'
        language_index = 1 if zh else 0
        root_link = '/zh/' if zh else '/'
        search_link = '/zh/?view=source-index' if zh else '/?view=source-index&amp;lang=en'
        curated_link = '/zh/resources/' if zh else '/resources/'
        scope_note = (f'共扫描 {len(scanned):,} 个仓库，提供 {len(records):,} 个浏览条目；{out_of_scope} 个超出范围的条目{unavailable_clause(unavailable, zh)}仍保留在完整 JSON 中。'
                      if zh else f'{len(records):,} repositories are available to browse from {len(scanned):,} successful README scans. The {out_of_scope} out-of-scope records{unavailable_clause(unavailable, zh)} remain in the full JSON.')
        provenance = ('这是自动发现的仓库索引，未逐项精选或运行验证。分类依据元数据；简介提供 AI 辅助中英翻译。星标为采集时快照。'
                      if zh else 'This automatically discovered repository index has not been individually curated or execution-tested. Categories come from metadata; descriptions have AI-assisted translations. Stars are collection-time snapshots.')
        if published:
            scope_note = (f'此发布选集包含 {len(scanned):,} 条已采集仓库记录，提供 {len(records):,} 个浏览条目；{out_of_scope} 个范围排除条目{unavailable_clause(unavailable, zh)}保留在发布 JSON 中。各原始扫描的累计数量保留在 JSON 来源信息中。'
                          if zh else f'This published selection contains {len(scanned):,} captured repository records and {len(records):,} browsable entries. The {out_of_scope} scope-excluded entries{unavailable_clause(unavailable, zh)} remain in the published JSON. Original capture totals remain separate in the JSON provenance.')
        for category in (None, *CATEGORIES):
            path = browse_path(language, category)
            canonical = site_url + path
            english_url = site_url + browse_path('en', category)
            chinese_url = site_url + browse_path('zh', category)
            counterpart = browse_path('en' if zh else 'zh', category)
            label = CATEGORIES[category][language_index] if category else ('按分类浏览仓库' if zh else 'Browse repositories by category')
            title = (f'{label} · 逆向工程仓库 · AwesomeREA.org' if zh else f'{label} · Reverse engineering repositories · AwesomeREA.org')
            if category:
                count = len(groups[category])
                description = (f'浏览 {count:,} 个{label}相关仓库，查看项目简介、原始链接与许可证信息。'
                               if zh else f'Browse {count:,} repositories with project descriptions, upstream links, and license information.')
                count_text = f'{count:,} 个仓库' if zh else f'{count:,} repositories'
            else:
                description = (f'按网站、游戏、应用、二进制、固件与协议等分类浏览 {len(records):,} 个逆向工程仓库。'
                               if zh else f'Browse {len(records):,} reverse engineering repositories across websites, games, apps, binaries, firmware, and protocols.')
                count_text = f'{len(CATEGORIES)} 个分类 · {len(records):,} 个仓库' if zh else f'{len(CATEGORIES)} categories · {len(records):,} repositories'
            date_text = ((f'选集发布：{scan_date} UTC' if zh else f'Selection published: {scan_date} UTC')
                         if published else (f'扫描快照：{scan_date} UTC' if zh else f'Scan snapshot: {scan_date} UTC')) if scan_date else ''
            category_links = []
            for slug, category_labels in CATEGORIES.items():
                active = ' aria-current="page"' if category == slug else ''
                category_links.append(f'<a href="{browse_path(language, slug)}"{active}>{escape(category_labels[language_index])}<span>{len(groups[slug]):,}</span></a>')
            if category:
                content = '<div class="source-results browse-results">\n' + '\n'.join(repository_card(record, language, use_pro) for record in groups[category]) + '\n</div>'
                schema_items = [
                    {'name': record.get('full_name') or record['name'], 'url': record['url'],
                     'description': record[f'description_{language}'] or description_fallback(record, language)}
                    for record in groups[category]
                ]
                if not groups[category]:
                    content = '<p class="browse-empty">' + ('该分类暂无仓库。' if zh else 'No repositories in this category.') + '</p>'
            else:
                cards = []
                schema_items = []
                for slug, category_labels in CATEGORIES.items():
                    count_label = f'{len(groups[slug]):,} 个仓库' if zh else f'{len(groups[slug]):,} repositories'
                    cards.append(f'''<a class="browse-category-card" href="{browse_path(language, slug)}">{icon(CATEGORY_ICONS[slug], use_pro)}<div class="browse-category-copy"><h2>{escape(category_labels[language_index])}</h2><p>{count_label}</p></div><span class="browse-category-arrow" aria-hidden="true">→</span></a>''')
                    schema_items.append({'name': category_labels[language_index], 'url': site_url + browse_path(language, slug), 'description': count_label})
                content = '<div class="browse-category-grid">\n' + '\n'.join(cards) + '\n</div>'
            structured_data = jsonld_script(collection_page_schema(canonical, label, description, locale, schema_items, site_url))
            trail = [('首页' if zh else 'Home', site_url + root_link), ('全部分类' if zh else 'All categories', site_url + browse_path(language))]
            breadcrumb_data = jsonld_script(breadcrumb_schema(canonical, trail + ([(label, canonical)] if category else [])))
            breadcrumbs = (f'<a href="{root_link}">{("首页" if zh else "Home")}</a><span aria-hidden="true">/</span>'
                           + (f'<a href="{browse_path(language)}">{("全部分类" if zh else "All categories")}</a><span aria-hidden="true">/</span><span aria-current="page">{escape(label)}</span>'
                              if category else f'<span aria-current="page">{("全部分类" if zh else "All categories")}</span>'))
            icon_css = f'<link rel="stylesheet" href="{escape(icon_stylesheet_href, quote=True)}">' if use_pro else ''
            document = f'''<!doctype html>
<html lang="{locale}"{(' data-icon-set="fontawesome"' if use_pro else '')}>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#ffffff">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description, quote=True)}">
  <link rel="canonical" href="{canonical}">
  <link rel="alternate" hreflang="en" href="{english_url}">
  <link rel="alternate" hreflang="zh-CN" href="{chinese_url}">
  <link rel="alternate" hreflang="x-default" href="{english_url}">
  {open_graph_meta(language=language, title=title, description=description, image_url=social_image_href, url=canonical)}
  <link rel="icon" href="{escape(favicon_href, quote=True)}" type="image/svg+xml">
  <link rel="stylesheet" href="{escape(styles_href, quote=True)}">
  <link rel="stylesheet" href="{escape(browse_styles_href, quote=True)}">
  {icon_css}
  {structured_data}
  {breadcrumb_data}
</head>
<body>
<a class="skip-link" href="#browse-content">{('跳到仓库目录' if zh else 'Skip to the directory')}</a>
<header class="site-header"><div class="shell header-inner">
  <a class="wordmark" href="{root_link}" aria-label="{('AwesomeREA.org 首页' if zh else 'AwesomeREA.org home')}"><img class="brand-mark" src="{escape(favicon_href, quote=True)}" alt="" width="33" height="33" aria-hidden="true"><span>Awesome<span class="wordmark-rea">REA</span><span class="wordmark-domain">.org</span></span></a>
  <nav class="header-nav" aria-label="{('主导航' if zh else 'Main navigation')}">
    <a class="browse-language" href="{counterpart}" lang="{('en' if zh else 'zh-CN')}" hreflang="{('en' if zh else 'zh-CN')}" aria-label="{('切换为英文' if zh else 'Switch to Simplified Chinese')}">{icon('globe', use_pro)}<span>{('English' if zh else '简体中文')}</span></a>
    <a class="github-link" href="{escape(repository_url, quote=True)}" target="_blank" rel="noopener" aria-label="GitHub">{icon('github', use_pro)}<span>GitHub</span></a>
  </nav>
</div></header>
<main id="browse-content" class="shell browse-main">
  <nav class="browse-breadcrumbs" aria-label="{('当前位置' if zh else 'Breadcrumb')}">{breadcrumbs}</nav>
  <section class="collection-intro browse-intro" aria-labelledby="browse-title">
    <p class="eyebrow">{('逆向工程仓库目录' if zh else 'THE REPOSITORY DIRECTORY')}</p>
    <h1 id="browse-title">{escape(label)}<span class="title-dot" aria-hidden="true">.</span></h1>
    <p>{escape(description)}</p>
  </section>
  <div class="browse-actions"><a class="button button-primary" href="{search_link}">{icon('search', use_pro)}{('搜索仓库' if zh else 'Search repositories')}</a><a class="button button-outline" href="{curated_link}">{('精选资源' if zh else 'Curated resources')} <span class="browse-count">{curated_count:,}</span></a><a class="browse-download" href="/source-index.json?v={data_revision}" download="awesomerea-repository-index.json" type="application/json">{('下载完整 JSON ↓' if zh else 'Download full JSON ↓')}</a></div>
  <details class="browse-provenance"><summary>{('关于这个索引' if zh else 'About this index')}</summary><p>{escape(scope_note)}</p><p>{escape(provenance)}</p><p><a href="{escape(repository_url, quote=True)}/blob/main/docs/source-scan.md">{('扫描方法（英文）↗' if zh else 'Scan methodology ↗')}</a> · <a href="{escape(repository_url, quote=True)}/blob/main/data/source-scope.json">{('范围排除记录 ↗' if zh else 'Scope exclusions ↗')}</a></p></details>
  {('<nav class="browse-category-nav" aria-label="' + ('仓库分类' if zh else 'Repository categories') + '">' + ''.join(category_links) + '</nav>' if category else '')}
  <div class="browse-topline"><p>{count_text}</p><p>{date_text}</p></div>
  {content}
</main>
<footer class="site-footer"><div class="shell footer-top"><p>{('独立的资源集合，在公开协作中持续更新。' if zh else 'An independent resource collection, updated in public.')}</p><div class="footer-links"><a href="{browse_path(language)}">{('全部分类' if zh else 'All categories')}</a><a href="{curated_link}">{('精选资源' if zh else 'Curated resources')}</a><a href="{('/zh' if zh else '')}/papers/">{('研究论文' if zh else 'Research papers')}</a><a href="{('/zh' if zh else '')}/about/">{('关于与来源' if zh else 'About and sources')}</a><a href="/source-index.json?v={data_revision}" download="awesomerea-repository-index.json" type="application/json">{('仓库索引 JSON ↓' if zh else 'Repository index JSON ↓')}</a><a href="/catalog.json?v={data_revision}" download="awesomerea-curated-catalog.json" type="application/json">{('精选目录 JSON ↓' if zh else 'Curated catalog JSON ↓')}</a></div></div><div class="shell footer-bottom">{('原创内容采用 MIT 许可。链接项目保留各自的许可。' if zh else 'Original content: MIT. Linked projects keep their own licenses.')}</div></footer>
</body>
</html>
'''
            if published:
                document = document.replace('/source-index.json?v=', '/source-published.json?v=')
                evidence_links = ' · '.join(
                    f'<a href="{escape(entry["archive_url"], quote=True)}">{("原始公开采集证据" if zh else "Original public capture evidence")} {entry["run"]["id"]}</a>'
                    for entry in source_document['meta']['capture_sources'])
                document = document.replace('</details>', '<p>' + evidence_links + '</p></details>', 1)
            rendered[path.lstrip('/') + 'index.html'] = document
            canonical_urls.append(canonical)

    # Clear only this generator's output, preventing stale category pages across builds.
    for directory in owned_directories:
        if directory.exists():
            shutil.rmtree(directory)
    for relative, document in rendered.items():
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(document, encoding='utf-8')
    return canonical_urls
