#!/usr/bin/env python3
"""Build static bilingual research directories and metadata-derived BibTeX."""
from __future__ import annotations

from collections import defaultdict
import hashlib
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from open_graph import open_graph_meta, website_reference

STATUS_LABELS = {
    'conference-paper': ('Conference paper', '会议论文'),
    'conference-accepted': ('Conference accepted', '会议已接收'),
    'journal-article': ('Journal article', '期刊论文'),
    'preprint': ('Preprint', '预印本'),
}
TARGET_LABELS = {
    'binary': ('Binary reverse engineering', '二进制逆向工程'),
    'website': ('Website reconstruction', '网站重建'),
    'app': ('App reconstruction and analysis', '应用重建与分析'),
    'game': ('Game reconstruction and reverse engineering', '游戏重建与逆向工程'),
    'firmware': ('Firmware analysis', '固件分析'),
    'protocol': ('Protocol inference and analysis', '协议推断与分析'),
}
MONTHS = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
BIBTEX_MONTHS = tuple(name[:3].lower() for name in MONTHS)


def papers_newest_first(papers: list[dict]) -> list[dict]:
    """Use the README display order without filling in unverified date parts.

    Within a year, recorded ISO date prefixes sort before year-only records;
    their relative position is a display convention, not an inferred exact date.
    English title and stable ID break ties identically in both languages.
    """
    return sorted(papers, key=lambda paper: (
        paper['year'], paper['publication_date'] or str(paper['year']),
        paper['title'].casefold(), paper['id'],
    ), reverse=True)


def web_url(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme != 'https' or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError('Paper links must be public HTTPS URLs without credentials')
    return escape(value, quote=True)


def icon(name: str, use_pro: bool) -> str:
    if use_pro:
        return f'<span class="icon fa-symbol fa-{name}" aria-hidden="true"></span>'
    if name == 'github':
        return '<span class="icon paper-github-fallback" aria-hidden="true">GH</span>'
    if name == 'external':
        return '<span class="paper-text-arrow" aria-hidden="true">↗</span>'
    return ''


def formatted_date(value: str | None, language: str, year: int | None = None) -> str:
    """Display only the precision recorded in the bibliography."""
    if not value:
        return str(year) + (' 年（具体日期未核实）' if language == 'zh' else ' (exact date not verified)') if year else ('未核实' if language == 'zh' else 'Not verified')
    parts = value.split('-')
    if len(parts) == 1:
        return parts[0] + (' 年' if language == 'zh' else '')
    month = int(parts[1])
    if not 1 <= month <= 12:
        raise ValueError('Invalid bibliography month')
    if language == 'zh':
        return f'{parts[0]} 年 {month} 月' + (f' {int(parts[2])} 日' if len(parts) == 3 else '')
    return f'{MONTHS[month - 1]} ' + (f'{int(parts[2])}, ' if len(parts) == 3 else '') + parts[0]


def bibtex_text(paper: dict) -> str:
    def literal(value):
        replacements = {'\\': r'\textbackslash{}', '{': r'\{', '}': r'\}', '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'}
        return ''.join(replacements.get(character, character) for character in str(value))

    kind = {'conference-paper': 'inproceedings', 'journal-article': 'article'}.get(paper['publication_status'], 'misc')
    fields = [
        ('title', '{' + literal(paper['title']) + '}'),
        # Literal author names avoid guessing surname order or multipart surnames.
        ('author', ' and '.join('{' + literal(name) + '}' for name in paper['authors'])),
        ('year', str(paper['year'])),
        ('url', paper['url']),
    ]
    # Container fields come only from the publisher metadata cited in `citation`;
    # without it, published entries keep the short venue label.
    container = paper.get('citation') or {}
    if kind in {'inproceedings', 'article'}:
        fields.append(('booktitle' if kind == 'inproceedings' else 'journal', literal(container.get('container_title') or paper['venue'])))
        for key, field in (('volume', 'volume'), ('issue', 'number'), ('series', 'series'), ('pages', 'pages'),
                           ('article_number', 'eid'), ('publisher', 'publisher')):
            if container.get(key):
                fields.append((field, literal(container[key]).replace('-', '--') if key == 'pages' else literal(container[key])))
    else:
        # plain.bst and plainnat.bst ignore eprint, so misc entries also print the arXiv locator.
        if paper.get('arxiv_id'):
            fields.append(('howpublished', 'arXiv:' + paper['arxiv_id']))
        # Review caveats stay on the paper page; the reference states only the status.
        fields.append(('note', literal('Accepted to ' + paper['venue']) if paper['publication_status'] == 'conference-accepted' else 'Preprint'))
    if paper.get('doi'):
        fields.append(('doi', paper['doi']))
    if paper.get('arxiv_id'):
        fields.extend((('eprint', paper['arxiv_id']), ('archivePrefix', 'arXiv')))
    lines = [f'  {key} = {{{value}}}' for key, value in fields]
    if paper.get('publication_date') and len(paper['publication_date']) >= 7:
        month = int(paper['publication_date'][5:7])
        if not 1 <= month <= 12:
            raise ValueError('Invalid bibliography month')
        # Unbraced standard macros let BibTeX styles print the month name; no day is emitted.
        lines.append('  month = ' + BIBTEX_MONTHS[month - 1])
    return '@' + kind + '{' + paper['id'] + ',\n' + ',\n'.join(lines) + '\n}\n'


def scholarly_article(paper: dict, language: str) -> dict:
    article = {
        '@type': 'ScholarlyArticle', '@id': paper['url'], 'url': paper['url'],
        'name': paper['title'], 'headline': paper['title'],
        'alternateName': paper['title_zh'],
        'author': [{'@type': 'Person', 'name': name} for name in paper['authors']],
        'description': paper[f'description_{language}'],
        'creativeWorkStatus': STATUS_LABELS[paper['publication_status']][0],
        'isPartOf': {'@type': 'CreativeWork', 'name': paper['venue']},
        'encoding': {'@type': 'MediaObject', 'encodingFormat': 'application/pdf', 'contentUrl': paper['pdf_url']},
    }
    # Never manufacture a month or day for year-only acceptance records.
    if paper.get('publication_date'):
        article['datePublished'] = paper['publication_date']
    identifiers = []
    if paper.get('doi'):
        identifiers.append({'@type': 'PropertyValue', 'propertyID': 'DOI', 'value': paper['doi']})
    if paper.get('arxiv_id'):
        identifiers.append({'@type': 'PropertyValue', 'propertyID': 'arXiv', 'value': paper['arxiv_id']})
    if identifiers:
        article['identifier'] = identifiers
    return article


def paper_card(paper: dict, language: str, use_pro: bool) -> str:
    zh = language == 'zh'
    label = lambda en, cn: cn if zh else en
    status = STATUS_LABELS[paper['publication_status']][1 if zh else 0]
    title = paper['title_zh'] if zh else paper['title']
    original_title = f'<p class="paper-original-title" lang="en">{escape(paper["title"])}</p>' if zh else ''
    links = [f'<a class="paper-link paper-link-primary" href="{web_url(paper["url"])}" target="_blank" rel="noopener noreferrer">{label("Paper", "论文")}{icon("external", use_pro)}</a>',
             f'<a class="paper-link" href="{web_url(paper["pdf_url"])}" target="_blank" rel="noopener noreferrer">PDF{icon("external", use_pro)}</a>']
    detail_path = f"{'/zh' if zh else ''}/papers/{paper['id']}/"
    detail_label = label('Full entry: ' + title, '完整条目：' + title)
    links.append(f'<a class="paper-link entry-detail-link" data-entry-link="{paper["id"]}" href="{detail_path}" aria-label="{escape(detail_label, quote=True)}">{label("Full entry", "完整条目")}</a>')
    for field, en, cn in (('code_url', 'Code', '代码'), ('project_url', 'Project', '项目')):
        if paper.get(field):
            links.append(f'<a class="paper-link" href="{web_url(paper[field])}" target="_blank" rel="noopener noreferrer">{label(en, cn)}{icon("external", use_pro)}</a>')
    links.append(f'<a class="paper-link" href="/papers/citations/{paper["id"]}.bib" download="{paper["id"]}.bib" type="application/x-bibtex">BibTeX ↓</a>')
    metadata = [(label('Publication / posting date', '出版／提交日期'), formatted_date(paper.get('publication_date'), language, paper['year'])),
                (label('Date source', '日期依据'), paper['date_basis_zh' if zh else 'date_basis'])]
    if paper.get('first_arxiv_date'):
        metadata.append((label('First arXiv submission', 'arXiv 首次提交'), formatted_date(paper['first_arxiv_date'], language)))
    if paper.get('arxiv_id'):
        metadata.append(('arXiv', paper['arxiv_id']))
    if paper.get('arxiv_version_reviewed'):
        metadata.append((label('Reviewed arXiv version', '已复核的 arXiv 版本'), paper['arxiv_version_reviewed']))
    if paper.get('doi'):
        metadata.append(('DOI', paper['doi']))
    metadata.append((label('Sources checked', '来源复核日期'), formatted_date(paper['verified_at'], language)))
    details = ''.join(f'<dt>{escape(key)}</dt><dd>{escape(value)}</dd>' for key, value in metadata)
    source_links = ''.join(f'<li><a href="{web_url(url)}" target="_blank" rel="noopener noreferrer">{escape(url)}</a></li>' for url in paper['evidence_urls'])
    return f'''<article class="paper-card" id="{paper['id']}" data-paper-id="{paper['id']}">
  <header><h3><a href="{web_url(paper['url'])}" target="_blank" rel="noopener noreferrer">{escape(title)}{icon('external', use_pro)}</a></h3>{original_title}<div class="paper-meta"><span class="paper-year">{paper['year']}</span><span class="paper-venue" lang="en">{escape(paper['venue'])}</span><span class="paper-status paper-status-{paper['publication_status']}">{status}</span></div><p class="paper-authors" lang="en">{escape('; '.join(paper['authors']))}</p></header>
  <p class="paper-description">{escape(paper[f'description_{language}'])}</p>
  <div class="paper-scope"><h4>{label('Scope & limitations', '研究范围与局限')}</h4><p>{escape(paper[f'scope_limitations_{language}'])}</p></div>
  <nav class="paper-links" aria-label="{escape(label('Links for ' + paper['title'], title + '的相关链接'), quote=True)}">{''.join(links)}</nav>
  <details class="paper-details"><summary>{label('Bibliographic details & sources', '引文详情与来源')}</summary><h4>{label('Why it fits this collection', '与本合集的关联')}</h4><p>{escape(paper[f'why_fits_{language}'])}</p><dl>{details}</dl><p>{escape(paper['metadata_notes_zh' if zh else 'metadata_notes'])}</p><h4>{label('Primary sources', '一手来源')}</h4><ul>{source_links}</ul><p class="paper-review-note">{label('Source review only; experiments were not rerun for this collection.', '本合集仅做来源复核，未重新运行论文实验。')}</p></details>
</article>'''


def build_paper_pages(
    site_dir: Path,
    papers: list[dict],
    *,
    site_url: str = 'https://awesomerea.org',
    repository_url: str = 'https://github.com/reacher-z/Awesome-REA',
    styles_href: str = '/styles.css',
    papers_styles_href: str = '/papers.css',
    favicon_href: str = '/favicon.svg',
    social_image_href: str = 'https://awesomerea.org/social-card.png',
    icon_stylesheet_href: str | None = None,
) -> list[str]:
    """Write /papers/ and /zh/papers/, shared BibTeX files, and return sitemap URLs."""
    site_dir = Path(site_dir)
    site_url = site_url.rstrip('/')
    identifiers = set()
    groups = defaultdict(list)
    for paper in papers:
        identifier = paper['id']
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', identifier) or identifier in identifiers:
            raise ValueError('Paper IDs must be unique safe path identifiers')
        identifiers.add(identifier)
        if paper['publication_status'] not in STATUS_LABELS:
            raise ValueError('Unknown paper publication status')
        if not paper['targets'] or any(target not in TARGET_LABELS for target in paper['targets']):
            raise ValueError('Unknown paper target')
        if paper.get('runtime_tested') is not False:
            raise ValueError('This directory currently describes source-reviewed, unrerun research only')
        for key in ('title', 'title_zh', 'venue', 'date_basis', 'date_basis_zh', 'metadata_notes', 'metadata_notes_zh', 'description_en', 'description_zh', 'scope_limitations_en', 'scope_limitations_zh', 'why_fits_en', 'why_fits_zh'):
            if not isinstance(paper.get(key), str) or not paper[key].strip():
                raise ValueError(f'{identifier}: missing bibliography or localized text')
        for key in ('url', 'pdf_url', 'code_url', 'project_url'):
            if paper.get(key):
                web_url(paper[key])
        for url in paper['evidence_urls']:
            web_url(url)
        groups[paper['targets'][0]].append(paper)

    groups = {target: papers_newest_first(groups[target]) for target in TARGET_LABELS}
    ordered = [paper for target in TARGET_LABELS for paper in groups[target]]

    # Citation downloads preserve the original title and author names in both languages.
    citation_dir = site_dir / 'papers' / 'citations'
    citation_dir.mkdir(parents=True, exist_ok=True)
    for stale in citation_dir.glob('*.bib'):
        if stale.stem not in identifiers:
            stale.unlink()
    bibliography = '% Generated from source-reviewed metadata. Author names retain their listed order without inferred surname parsing.\n\n'
    for paper in papers:
        entry = bibtex_text(paper)
        (citation_dir / f'{paper["id"]}.bib').write_text(entry, encoding='utf-8')
        bibliography += entry + '\n'
    (site_dir / 'papers' / 'references.bib').write_text(bibliography, encoding='utf-8')

    search_script = (Path(__file__).resolve().parents[1] / 'site/paper-search.js').read_bytes()
    (site_dir / 'paper-search.js').write_bytes(search_script)
    search_href = '/paper-search.js?v=' + hashlib.sha256(search_script).hexdigest()[:16]
    search_fields = ('id', 'title', 'title_zh', 'description_en', 'description_zh', 'authors', 'doi', 'arxiv_id',
                     'year', 'publication_status', 'targets')
    search_data = json.dumps({'schema_version': 1, 'papers': [
        {key: paper.get(key) for key in search_fields} for paper in ordered
    ]}, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')

    canonical_urls = []
    use_pro = icon_stylesheet_href is not None
    for language in ('en', 'zh'):
        zh = language == 'zh'
        label = lambda en, cn: cn if zh else en
        path = '/zh/papers/' if zh else '/papers/'
        counterpart = '/papers/' if zh else '/zh/papers/'
        canonical = site_url + path
        locale = 'zh-CN' if zh else 'en'
        home = '/zh/' if zh else '/'
        browse = '/zh/browse/' if zh else '/browse/'
        curated = '/zh/resources/' if zh else '/resources/'
        about = '/zh/about/' if zh else '/about/'
        title = label('Reverse engineering papers & benchmarks · AwesomeREA.org', '逆向工程论文与评测基准 · AwesomeREA.org')
        protocol_scope = label('protocol inference, ', '协议推断、') if any('protocol' in paper['targets'] for paper in papers) else ''
        description = label(f'{len(papers)} source-reviewed papers on binary reverse engineering, decompilation, agent evaluation, {protocol_scope}firmware analysis, and website, game, and app reconstruction, with citations and research limitations.', f'{len(papers)} 篇来源已复核的论文，涵盖二进制逆向、反编译、智能体评估、{protocol_scope}固件分析，以及网站、游戏和应用重建，附引文和研究边界。')
        intro = label(f'Explore {len(papers)} papers on reverse engineering and software reconstruction, newest year first within each section.', f'浏览 {len(papers)} 篇逆向工程与软件重建论文，各分区按年份从新到旧排列。')
        nav = []
        sections = []
        for target, target_labels in TARGET_LABELS.items():
            if not groups[target]:
                continue
            target_label = target_labels[1 if zh else 0]
            nav.append(f'<a href="#research-{target}" data-paper-topic="{target}">{target_label}<span>{len(groups[target])}</span></a>')
            articles = '\n'.join(paper_card(paper, language, use_pro) for paper in groups[target])
            count_label = f'{len(groups[target])} ' + ('篇论文' if zh else ('paper' if len(groups[target]) == 1 else 'papers'))
            sections.append(f'<section class="paper-section" aria-labelledby="research-{target}" data-paper-section="{target}"><div class="paper-section-heading"><h2 id="research-{target}">{target_label}</h2><span data-paper-section-count>{count_label}</span></div><div class="paper-grid">{articles}</div></section>')
        status_options = ''.join(f'<option value="{status}">{escape(labels[int(zh)])}</option>'
                                 for status, labels in STATUS_LABELS.items()
                                 if any(paper['publication_status'] == status for paper in papers))
        year_options = ''.join(f'<option value="{year}">{year}</option>'
                               for year in sorted({paper['year'] for paper in papers}, reverse=True))
        target_options = ''.join(f'<option value="{target}">{escape(labels[int(zh)])}</option>'
                                 for target, labels in TARGET_LABELS.items()
                                 if any(target in paper['targets'] for paper in papers))
        graph = {
            '@context': 'https://schema.org',
            '@graph': [
                {'@type': 'CollectionPage', '@id': canonical, 'url': canonical, 'name': title, 'description': description, 'inLanguage': locale, 'mainEntity': {'@id': canonical + '#paper-list'}},
                {'@type': 'ItemList', '@id': canonical + '#paper-list', 'numberOfItems': len(ordered), 'itemListElement': [{'@type': 'ListItem', 'position': index + 1, 'url': canonical + '#' + paper['id'], 'item': {'@id': paper['url']}} for index, paper in enumerate(ordered)]},
                *(scholarly_article(paper, language) for paper in ordered),
            ],
        }
        # The directory belongs to the site that only the homepages define.
        graph['@graph'][0]['isPartOf'] = website_reference(site_url)
        structured = json.dumps(graph, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
        icon_css = f'<link rel="stylesheet" href="{escape(icon_stylesheet_href, quote=True)}">' if use_pro else ''
        document = f'''<!doctype html>
<html lang="{locale}"{(' data-icon-set="fontawesome"' if use_pro else '')}>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#ffffff">
  <title>{title}</title>
  <meta name="description" content="{escape(description, quote=True)}">
  <link rel="canonical" href="{canonical}">
  <link rel="alternate" hreflang="en" href="{site_url}/papers/">
  <link rel="alternate" hreflang="zh-CN" href="{site_url}/zh/papers/">
  <link rel="alternate" hreflang="x-default" href="{site_url}/papers/">
  {open_graph_meta(language=language, title=title, description=description, image_url=social_image_href, url=canonical)}
  <link rel="icon" href="{escape(favicon_href, quote=True)}" type="image/svg+xml">
  <link rel="stylesheet" href="{escape(styles_href, quote=True)}">
  <link rel="stylesheet" href="{escape(papers_styles_href, quote=True)}">
  {icon_css}
  <script type="application/ld+json">{structured}</script>
  <script src="{search_href}" defer></script>
</head>
<body>
<a class="skip-link" href="#papers-content">{label('Skip to the papers', '跳到论文目录')}</a>
<header class="site-header"><div class="shell header-inner"><a class="wordmark" href="{home}" aria-label="{label('AwesomeREA.org home', 'AwesomeREA.org 首页')}"><span class="brand-mark" aria-hidden="true">r<span>↗</span></span><span>Awesome<span class="wordmark-rea">REA</span><span class="wordmark-domain">.org</span></span></a><nav class="header-nav" aria-label="{label('Main navigation', '主导航')}"><a class="papers-language" href="{counterpart}" lang="{label('zh-CN', 'en')}" hreflang="{label('zh-CN', 'en')}">{icon('globe', use_pro)}<span>{label('简体中文', 'English')}</span></a><a class="github-link" href="{web_url(repository_url)}" target="_blank" rel="noopener noreferrer" aria-label="GitHub">{icon('github', use_pro)}<span>GitHub</span></a></nav></div></header>
<main id="papers-content" class="shell papers-main">
  <nav class="papers-breadcrumbs" aria-label="{label('Breadcrumb', '当前位置')}"><a href="{home}">{label('Home', '首页')}</a><span aria-hidden="true">/</span><span aria-current="page">{label('Reverse engineering papers & benchmarks', '逆向工程论文与评测基准')}</span></nav>
  <section class="collection-intro papers-intro" aria-labelledby="papers-title"><p class="eyebrow">{label('RESEARCH & EVIDENCE', '研究与证据')}</p><h1 id="papers-title">{label('Reverse engineering papers & benchmarks', '逆向工程论文与评测基准')}<span class="title-dot" aria-hidden="true">.</span></h1><p>{escape(intro)}</p></section>
  <div class="papers-actions"><a class="button button-outline" href="{web_url(repository_url + "/issues/new?template=paper.yml")}" target="_blank" rel="noopener noreferrer">{icon("document", use_pro)}{label("Suggest a paper", "推荐论文")}</a><a class="button button-outline" href="{browse}">{icon('layers', use_pro)}{label('Browse repositories', '浏览仓库')}</a><a class="papers-bibliography" href="/papers/references.bib" download="awesomerea-papers.bib" type="application/x-bibtex">{label('Download bibliography', '下载参考文献')} · BibTeX ↓</a></div>
  <p class="papers-review-policy">{label('We check primary sources; we do not rerun experiments or independently reproduce results.', '仅复核一手来源，未重新运行实验或独立复现结果。')}</p>
  <form id="paper-search" class="paper-search" role="search" aria-label="{label('Search research papers', '搜索研究论文')}" hidden>
    <div class="paper-search-field paper-search-query"><label for="paper-query">{label('Search papers', '搜索论文')}</label><input id="paper-query" name="q" type="search" maxlength="240" autocomplete="off" placeholder="{label('Title, author, keyword, DOI or arXiv ID', '标题、作者、关键词、DOI 或 arXiv 编号')}" aria-describedby="paper-search-help"></div>
    <div class="paper-search-field"><label for="paper-target">{label('Target', '目标')}</label><select id="paper-target" name="target"><option value="all">{label('All targets', '全部目标')}</option>{target_options}</select></div>
    <div class="paper-search-field"><label for="paper-status">{label('Publication status', '发表状态')}</label><select id="paper-status" name="status"><option value="all">{label('All statuses', '全部状态')}</option>{status_options}</select></div>
    <div class="paper-search-field"><label for="paper-year">{label('Year', '年份')}</label><select id="paper-year" name="year"><option value="all">{label('All years', '全部年份')}</option>{year_options}</select></div>
    <button id="paper-clear" class="button button-outline" type="button">{label('Clear filters', '清除筛选')}</button>
    <p id="paper-search-help" class="paper-search-help">{label('Search in English or Chinese. Filters match every listed target; papers stay in their main section.', '支持中英文搜索。筛选匹配全部目标，论文仍按主要目标分组。')}</p>
    <p id="paper-results" class="paper-search-results" role="status" aria-live="polite" aria-atomic="true"></p>
  </form>
  <div id="paper-empty" class="paper-search-empty" hidden><p>{label('No papers match these filters.', '没有符合这些条件的论文。')}</p><button id="paper-empty-reset" class="button button-outline" type="button">{label('Clear filters and show all papers', '清除筛选并显示全部论文')}</button></div>
  <nav class="papers-topic-nav" aria-label="{label('Research areas', '研究方向')}">{''.join(nav)}</nav>
  {''.join(sections)}
  <script id="paper-search-data" type="application/json">{search_data}</script>
</main>
<footer class="site-footer"><div class="shell footer-top"><p>{label('An independent resource collection, updated in public.', '独立的资源集合，在公开协作中持续更新。')}</p><div class="footer-links"><a href="{home}">{label('Interactive collection', '交互式合集')}</a><a href="{browse}">{label('Repository directory', '仓库分类目录')}</a><a href="{curated}">{label('Curated resources', '精选资源')}</a><a href="{about}">{label('About and sources', '关于与来源')}</a><a href="/papers/references.bib" download="awesomerea-papers.bib" type="application/x-bibtex">BibTeX ↓</a><a href="{web_url(repository_url)}" target="_blank" rel="noopener noreferrer">GitHub ↗</a></div></div><div class="shell footer-bottom">{label('Paper and code links retain their own licenses. Bibliographic metadata is supplied for citation; follow the original sources for version and access details.', '论文和代码保留各自的许可。引文元数据用于引用；版本和访问详情请以原始来源为准。')}</div></footer>
</body>
</html>
'''
        destination = site_dir / path.lstrip('/') / 'index.html'
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(document, encoding='utf-8')
        canonical_urls.append(canonical)
    return canonical_urls
