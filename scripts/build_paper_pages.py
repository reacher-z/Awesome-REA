#!/usr/bin/env python3
"""Build static bilingual research directories and metadata-derived BibTeX."""
from __future__ import annotations

from collections import defaultdict
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from asset_paths import fingerprinted_href, write_fingerprinted
from open_graph import THEME_COLOR_META, open_graph_meta, website_reference
from site_footer import download_link, site_footer

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
# Fields paper-search.js matches and filters on: both languages' titles and summaries, authors, venue and identifiers.
SEARCH_FIELDS = ('id', 'title', 'title_zh', 'description_en', 'description_zh', 'authors', 'venue', 'doi', 'arxiv_id',
                 'year', 'publication_status', 'targets')
# Advisory weight for each paper listing. validate_site.py prints a warning above it and never fails, so data pull
# requests keep passing; tests check a fixed bibliography against it.
LISTING_SIZE_BUDGET = 900_000
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


def journal_title(venue: str) -> str:
    """A PACM venue names its conference issue in parentheses; the journal is the title before it."""
    match = re.fullmatch(r'(.+?) \([A-Z][A-Za-z0-9]* \d{4}\)', venue)
    return match[1] if match else venue


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
    # without it, published entries keep the short venue label, minus a journal's conference issue.
    container = paper.get('citation') or {}
    if kind in {'inproceedings', 'article'}:
        label = paper['venue'] if kind == 'inproceedings' else journal_title(paper['venue'])
        fields.append(('booktitle' if kind == 'inproceedings' else 'journal', literal(container.get('container_title') or label)))
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


def paper_entity_id(paper: dict, language: str, site_url: str = 'https://awesomerea.org') -> str:
    """Name one ScholarlyArticle per language, shared by /papers/ and the paper's detail page."""
    return f"{site_url.rstrip('/')}{'/zh' if language == 'zh' else ''}/papers/{paper['id']}/#paper"


def paper_same_as(paper: dict) -> list[str]:
    """Resolvable links built only from recorded DOI and arXiv fields, never inferred ones."""
    links = [base + paper[field] for field, base in (('doi', 'https://doi.org/'), ('arxiv_id', 'https://arxiv.org/abs/'))
             if paper.get(field)]
    return [link for link in links if link != paper['url']]


def scholarly_article(paper: dict, language: str, site_url: str = 'https://awesomerea.org') -> dict:
    article = {
        '@type': 'ScholarlyArticle', '@id': paper_entity_id(paper, language, site_url), 'url': paper['url'],
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
    if paper_same_as(paper):
        article['sameAs'] = paper_same_as(paper)
    return article


def paper_sources_link(paper: dict, language: str) -> str:
    """Link the entry page's source list, stating how many sources it holds and when they were checked.

    Sources are counted as the entry page lists them, each distinct URL once. The list, the publication
    details and the review notes are on the entry page only, which keeps /papers/ light. The link is an inline
    flex box, which drops spaces next to the <time> child, so the date follows a no-break space."""
    zh = language == 'zh'
    title = paper['title_zh'] if zh else paper['title']
    sources = len(dict.fromkeys(paper['evidence_urls']))
    checked = str(paper['verified_at'])
    date = f'<time datetime="{escape(checked, quote=True)}">{escape(checked[:10])}</time>'
    if zh:
        text = f'{sources} 个来源 · 复核于&nbsp;{date}'
        label = f'{title}：完整条目中的 {sources} 个来源（复核于 {checked[:10]}）'
    else:
        plural = '' if sources == 1 else 's'
        text = f'{sources} source{plural} · checked&nbsp;{date}'
        label = f'{title}: {sources} source{plural}, checked {checked[:10]}, on the full entry'
    href = f"{'/zh' if zh else ''}/papers/{paper['id']}/#entry-sources"
    return (f'<p class="paper-sources"><a href="{href}" aria-label="{escape(label, quote=True)}">'
            f'{text}<span aria-hidden="true">&nbsp;→</span></a></p>')


def paper_card(paper: dict, language: str, use_pro: bool) -> str:
    """One listing card: summary, links, a disclosure with scope and authors, and a counted link to the entry's sources."""
    zh = language == 'zh'
    label = lambda en, cn: cn if zh else en
    status = STATUS_LABELS[paper['publication_status']][1 if zh else 0]
    title = paper['title_zh'] if zh else paper['title']
    original_title = f'<p class="paper-original-title" lang="en">{escape(paper["title"])}</p>' if zh else ''
    # Every row repeats PDF, Code, Project and BibTeX; accessible names start with that text and add the title.
    named = lambda visible: escape(f'{visible}：{title}' if zh else f'{visible}: {title}', quote=True)
    links = [f'<a class="paper-link" href="{web_url(paper["pdf_url"])}" target="_blank" rel="noopener" aria-label="{named("PDF")}">PDF{icon("external", use_pro)}</a>']
    detail_path = f"{'/zh' if zh else ''}/papers/{paper['id']}/"
    detail_label = label('Full entry: ' + title, '完整条目：' + title)
    links.append(f'<a class="paper-link entry-detail-link" data-entry-link="{paper["id"]}" href="{detail_path}" aria-label="{escape(detail_label, quote=True)}">{label("Full entry", "完整条目")}</a>')
    for field, en, cn in (('code_url', 'Code', '代码'), ('project_url', 'Project', '项目')):
        if paper.get(field):
            links.append(f'<a class="paper-link" href="{web_url(paper[field])}" target="_blank" rel="noopener" aria-label="{named(label(en, cn))}">{label(en, cn)}{icon("external", use_pro)}</a>')
    citation_link = f'<a class="paper-link" href="/papers/citations/{paper["id"]}.bib" download="{paper["id"]}.bib" type="application/x-bibtex" aria-label="{named('BibTeX')}">BibTeX <span aria-hidden="true">↓</span></a>'
    return f'''<article class="paper-card" id="{paper['id']}" data-paper-id="{paper['id']}">
  <header><h3><a href="{web_url(paper['url'])}" target="_blank" rel="noopener">{escape(title)}{icon('external', use_pro)}</a></h3><div class="paper-meta"><span class="paper-year">{paper['year']}</span><span class="paper-venue" lang="en">{escape(paper['venue'])}</span><span class="paper-status paper-status-{paper['publication_status']}">{status}</span></div></header>
  <p class="paper-description">{escape(paper[f'description_{language}'])}</p>
  <ul class="paper-links">{''.join(f'<li>{link}</li>' for link in links)}</ul>
  <details class="paper-details"><summary>{label('Scope & authors', '研究范围与作者')}</summary><div class="paper-scope"><h4>{label('Scope & limitations', '研究范围与局限')}</h4><p>{escape(paper[f'scope_limitations_{language}'])}</p></div><h4>{label('Authors & citation', '作者与引文')}</h4>{original_title}<p class="paper-authors" lang="en">{escape('; '.join(paper['authors']))}</p><p class="paper-citation-download">{citation_link}</p></details>
  {paper_sources_link(paper, language)}
</article>'''


def search_index(ordered: list[dict]) -> bytes:
    """The paper-search.js index: SEARCH_FIELDS of every paper, in the listing's order."""
    return json.dumps({'schema_version': 1, 'papers': [{key: paper.get(key) for key in SEARCH_FIELDS} for paper in ordered]},
                      ensure_ascii=False, separators=(',', ':')).encode('utf-8')


def listing_size_warning(route: str, size: int) -> str | None:
    """Advisory note for a paper listing of `size` bytes, or None while it is within LISTING_SIZE_BUDGET."""
    if size <= LISTING_SIZE_BUDGET:
        return None
    return (f'{route} is {size:,} bytes of HTML, above the {LISTING_SIZE_BUDGET:,}-byte budget for the paper listings; '
            'move more card detail to the entry pages /papers/<id>/.')


def listing_size_warnings(site_dir: Path) -> list[str]:
    """Size notes for both built paper listings; validate_site.py prints them without failing."""
    notes = (listing_size_warning(route, (Path(site_dir) / route.lstrip('/') / 'index.html').stat().st_size)
             for route in ('/papers/', '/zh/papers/'))
    return [note for note in notes if note]


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
    repository_export: str = 'source-index.json',
) -> list[str]:
    """Write /papers/ and /zh/papers/, shared BibTeX files, and return sitemap URLs."""
    # The README generator imports this module, so its topic map is read when pages are built.
    from build_readme import PAPER_SECTIONS, PAPER_TOPIC_LABELS, paper_section
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
        groups[paper_section(paper)].append(paper)

    groups = {section: papers_newest_first(groups[section]) for section in PAPER_SECTIONS}
    ordered = [paper for section in PAPER_SECTIONS for paper in groups[section]]

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
    search_href = fingerprinted_href(site_dir, 'paper-search.js')
    # One content-addressed index serves both languages: fetched once, then cached like the scripts.
    search_index_href = write_fingerprinted(site_dir, 'paper-search-index', '.json', search_index(ordered))

    # The visible breadcrumb gets the same BreadcrumbList as the discovery and browse pages.
    from build_discovery_pages import breadcrumb_schema, jsonld_script
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
        title = label('Reverse engineering papers & benchmarks · AwesomeREA.org', '逆向工程论文与评测基准 · AwesomeREA.org')
        protocol_scope = label('protocol inference, ', '协议推断、') if any('protocol' in paper['targets'] for paper in papers) else ''
        description = label(f'{len(papers)} source-reviewed papers on binary reverse engineering, decompilation, agent evaluation, {protocol_scope}firmware analysis, and website, game, and app reconstruction, with citations and research limitations.', f'{len(papers)} 篇来源已复核的论文，涵盖二进制逆向、反编译、智能体评估、{protocol_scope}固件分析，以及网站、游戏和应用重建，附引文和研究边界。')
        intro = label(f'Explore {len(papers)} papers on reverse engineering and software reconstruction, newest year first within each section.', f'浏览 {len(papers)} 篇逆向工程与软件重建论文，各分区按年份从新到旧排列。')
        nav = []
        sections = []
        for section, section_labels in PAPER_SECTIONS.items():
            if not groups[section]:
                continue
            section_label = section_labels[1 if zh else 0]
            nav.append(f'<a href="#research-{section}" data-paper-topic="{section}">{PAPER_TOPIC_LABELS[section][1 if zh else 0]}<span>{len(groups[section])}</span></a>')
            articles = '\n'.join(paper_card(paper, language, use_pro) for paper in groups[section])
            count_label = f'{len(groups[section])} ' + ('篇论文' if zh else ('paper' if len(groups[section]) == 1 else 'papers'))
            sections.append(f'<section class="paper-section" aria-labelledby="research-{section}" data-paper-section="{section}"><div class="paper-section-heading"><h2 id="research-{section}">{section_label}</h2><span data-paper-section-count>{count_label}</span></div><div class="paper-grid">{articles}</div></section>')
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
                # Each item names a paper's entry page and the ScholarlyArticle that page defines; the full article
                # data is published there only, so the listing does not repeat it.
                {'@type': 'ItemList', '@id': canonical + '#paper-list', 'numberOfItems': len(ordered), 'itemListElement': [
                    {'@type': 'ListItem', 'position': index + 1, 'url': canonical + paper['id'] + '/',
                     'name': paper['title_zh'] if zh else paper['title'], 'item': {'@id': paper_entity_id(paper, language, site_url)}}
                    for index, paper in enumerate(ordered)]},
            ],
        }
        # The directory belongs to the site that only the homepages define.
        graph['@graph'][0]['isPartOf'] = website_reference(site_url)
        structured = json.dumps(graph, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
        icon_css = f'<link rel="stylesheet" href="{escape(icon_stylesheet_href, quote=True)}">' if use_pro else ''
        document = f'''<!doctype html>
<html lang="{locale}" data-paper-layout="compact"{(' data-icon-set="fontawesome"' if use_pro else '')}>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  {THEME_COLOR_META}
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
  {jsonld_script(breadcrumb_schema(canonical, [(label('Home', '首页'), site_url + home), (label('Reverse engineering papers & benchmarks', '逆向工程论文与评测基准'), canonical)]))}
  <link rel="preload" href="{search_index_href}" as="fetch" crossorigin>
  <script src="{search_href}" defer></script>
</head>
<body>
<a class="skip-link" href="#papers-content">{label('Skip to the papers', '跳到论文目录')}</a>
<header class="site-header"><div class="shell header-inner"><a class="wordmark" href="{home}" aria-label="{label('AwesomeREA.org home', 'AwesomeREA.org 首页')}"><img class="brand-mark" src="{escape(favicon_href, quote=True)}" alt="" width="33" height="33" aria-hidden="true"><span>Awesome<span class="wordmark-rea">REA</span><span class="wordmark-domain">.org</span></span></a><nav class="header-nav" aria-label="{label('Main navigation', '主导航')}"><a class="papers-language" href="{counterpart}" lang="{label('zh-CN', 'en')}" hreflang="{label('zh-CN', 'en')}">{icon('globe', use_pro)}<span>{label('简体中文', 'English')}</span></a><a class="github-link" href="{web_url(repository_url)}" target="_blank" rel="noopener" aria-label="GitHub">{icon('github', use_pro)}<span>GitHub</span></a></nav></div></header>
<main id="papers-content" class="shell papers-main">
  <nav class="papers-breadcrumbs" aria-label="{label('Breadcrumb', '当前位置')}"><a href="{home}">{label('Home', '首页')}</a><span aria-hidden="true">/</span><span aria-current="page">{label('Reverse engineering papers & benchmarks', '逆向工程论文与评测基准')}</span></nav>
  <section class="collection-intro papers-intro" aria-labelledby="papers-title"><p class="eyebrow">{label('RESEARCH & EVIDENCE', '研究与证据')}</p><h1 id="papers-title">{label('Reverse engineering papers & benchmarks', '逆向工程论文与评测基准')}<span class="title-dot" aria-hidden="true">.</span></h1><p>{escape(intro)}</p></section>
  <div class="papers-actions"><a class="button button-outline" href="{web_url(repository_url + "/issues/new?template=paper.yml")}" target="_blank" rel="noopener">{icon("document", use_pro)}{label("Suggest a paper", "推荐论文")}</a><a class="button button-outline" href="{browse}">{icon('layers', use_pro)}{label('Browse repositories', '浏览仓库')}</a>{download_link('/papers/references.bib', language, css_class='papers-bibliography')}</div>
  <p class="papers-review-policy">{label('We check primary sources; we do not rerun experiments or independently reproduce results.', '仅复核一手来源，未重新运行实验或独立复现结果。')}</p>
  <form id="paper-search" class="paper-search script-only" role="search" aria-label="{label('Search research papers', '搜索研究论文')}" data-search-index="{search_index_href}">
    <div class="paper-search-field paper-search-query"><label for="paper-query">{label('Search papers', '搜索论文')}</label><input id="paper-query" name="q" type="search" maxlength="240" autocomplete="off" placeholder="{label('Title, author, venue, DOI or arXiv ID', '标题、作者、出处、DOI 或 arXiv 编号')}" aria-describedby="paper-search-help"></div>
    <div class="paper-search-field"><label for="paper-target">{label('Target', '目标')}</label><select id="paper-target" name="target"><option value="all">{label('All targets', '全部目标')}</option>{target_options}</select></div>
    <details class="paper-search-more" id="paper-more-filters"><summary>{label('More filters', '更多筛选')}</summary><div class="paper-search-options">
    <div class="paper-search-field"><label for="paper-status">{label('Publication status', '发表状态')}</label><select id="paper-status" name="status"><option value="all">{label('All statuses', '全部状态')}</option>{status_options}</select></div>
    <div class="paper-search-field"><label for="paper-year">{label('Year', '年份')}</label><select id="paper-year" name="year"><option value="all">{label('All years', '全部年份')}</option>{year_options}</select></div>
    <div class="paper-search-field paper-layout-field"><label for="paper-layout">{label('Layout', '布局')}</label><select id="paper-layout"><option value="compact">{label('Compact list', '紧凑列表')}</option><option value="cards">{label('Cards', '卡片')}</option></select></div>
    </div>
    <p id="paper-search-help" class="paper-search-help">{label('Search titles, authors, summaries and venues in English or Chinese. Filters match every listed target; papers stay in their main section.', '支持中英文搜索标题、作者、摘要及会议或期刊名称。筛选匹配全部目标，论文仍按主要目标分组。')}</p>
    </details>
    <button id="paper-clear" class="button button-outline" type="button" disabled>{label('Clear filters', '清除筛选')}</button>
    <p id="paper-results" class="paper-search-results" role="status" aria-live="polite" aria-atomic="true">{label(f'Showing {len(papers)} of {len(papers)} papers', f'显示 {len(papers)} / {len(papers)} 篇论文')}</p>
  </form>
  <div id="paper-empty" class="paper-search-empty" hidden><p>{label('No papers match these filters.', '没有符合这些条件的论文。')}</p><button id="paper-empty-reset" class="button button-outline" type="button">{label('Clear filters and show all papers', '清除筛选并显示全部论文')}</button></div>
  <nav class="papers-topic-nav" aria-label="{label('Research areas', '研究方向')}">{''.join(nav)}</nav>
  {''.join(sections)}
</main>
{site_footer(language, note=escape(label('Paper and code links retain their own licenses. Bibliographic metadata is supplied for citation; follow the original sources for version and access details.', '论文和代码保留各自的许可。引文元数据用于引用；版本和访问详情请以原始来源为准。')), repository_url=repository_url, repository_export=repository_export)}
</body>
</html>
'''
        destination = site_dir / path.lstrip('/') / 'index.html'
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(document, encoding='utf-8')
        canonical_urls.append(canonical)
    return canonical_urls
