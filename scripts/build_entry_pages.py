"""Render bilingual detail pages for reviewed catalog records, never scan records."""
from __future__ import annotations

from collections import defaultdict
from html import escape
from pathlib import Path
import re
from urllib.parse import urlsplit

from artifact_links import github_repository
from build_discovery_pages import PRIMARY_SOURCE_LABEL, jsonld_script, publication_keys
from build_paper_pages import STATUS_LABELS, formatted_date, scholarly_article
from build_readme import CATEGORIES, KIND_LABELS, RELATIONSHIPS, TARGETS
from open_graph import open_graph_meta

MARKER = '<!-- Generated curated entry page. -->'


def entry_path(kind: str, identifier: str, language: str = 'en') -> str:
    if kind not in {'resource', 'paper'} or language not in {'en', 'zh'}:
        raise ValueError('Unknown entry kind or language')
    if not isinstance(identifier, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', identifier):
        raise ValueError('Entry IDs must be safe lowercase path identifiers')
    if kind == 'paper' and not identifier.startswith('paper-'):
        raise ValueError('Paper IDs must use the paper- prefix')
    return ('/zh' if language == 'zh' else '') + f'/{kind}s/{identifier}/'


def _text(record: dict, key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{record.get("id")}: missing {key}')
    return value


def _requirements(record: dict, language: str) -> list[str]:
    value = record.get('requirements_zh' if language == 'zh' else 'requirements')
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list) or not value or not all(isinstance(v, str) and v.strip() for v in value):
        raise ValueError(f'{record.get("id")}: missing localized requirements')
    return value


def _public_url(value: str) -> str:
    # Import lazily to keep all pipeline scripts independently importable.
    from validate import public_https_error
    if public_https_error(value):
        raise ValueError('Entry sources must be public HTTPS URLs without credentials')
    return escape(value, quote=True)


def _asset_url(value: str) -> str:
    if isinstance(value, str) and value.startswith('/') and not value.startswith('//'):
        if '\\' not in value and not any(c.isspace() or c in '<>"' for c in value):
            return escape(value, quote=True)
    return _public_url(value)


def _link(url: str, label: str, *, primary: bool = False) -> str:
    cls = 'entry-link entry-link-primary' if primary else 'entry-link'
    return f'<a class="{cls}" href="{_public_url(url)}" target="_blank" rel="noopener noreferrer">{escape(label)} <span aria-hidden="true">↗</span></a>'


def _sources(urls: list[str], language: str) -> str:
    links = []
    for url in dict.fromkeys(urls):
        href, label, context = _public_url(url), url, ''
        parsed = urlsplit(url)
        parts = parsed.path.lstrip('/').split('/', 4)
        # Only immutable GitHub file/directory links get a compact display label.
        # The full source URL, revision and any line anchor remain in the link.
        if (parsed.netloc == 'github.com' and not parsed.query and len(parts) == 5
                and parts[0] and parts[1] and parts[4]
                and parts[2] in {'blob', 'tree'} and re.fullmatch(r'[a-f0-9]{40}', parts[3])):
            owner, repository, _, revision, path = parts
            label = path + ('#' + parsed.fragment if parsed.fragment else '')
            revision_label = '修订' if language == 'zh' else 'Revision'
            context = (f' <span class="entry-source-context">GitHub · {escape(owner + "/" + repository)}'
                       f' · {revision_label} <span title="{revision}">{revision[:7]}</span></span>')
        links.append(f'<li><a href="{href}" title="{href}" target="_blank" rel="noopener noreferrer">{escape(label)}</a>{context}</li>')
    return f'<section class="entry-section" aria-labelledby="entry-sources"><h2 id="entry-sources">{("一手来源" if language == "zh" else "Primary sources")}</h2><ol class="entry-sources">{"".join(links)}</ol></section>'


def _definitions(items: list[tuple[str, str]]) -> str:
    return '<dl class="entry-facts">' + ''.join(f'<dt>{escape(label)}</dt><dd>{escape(value)}</dd>' for label, value in items) + '</dl>'


def _survey_discussion(sections: list[dict], language: str) -> str:
    if not sections:
        return ''
    prefix = '/zh' if language == 'zh' else ''
    links = []
    for section in sections:
        identifier = section['section']
        if not isinstance(identifier, str) or not re.fullmatch(r'[a-z][a-z0-9-]*', identifier):
            raise ValueError('Survey discussion links require safe section IDs')
        title = section['title'][language]
        if not isinstance(title, str) or not title.strip():
            raise ValueError('Survey discussion links require localized titles')
        links.append(f'<li><a href="{prefix}/survey/#{identifier}">{escape(title)}</a></li>')
    heading = '综述中的讨论' if language == 'zh' else 'Discussed in the survey'
    return (f'<section class="entry-section" aria-labelledby="entry-survey"><h2 id="entry-survey">{heading}</h2>'
            f'<ul class="entry-sources">{"".join(links)}</ul></section>')


def matching_entries(resources: list[dict], papers: list[dict]) -> dict[tuple[str, str], list[tuple[str, dict]]]:
    """Pair a resource and a paper only when both describe the same work.

    A match is the resource URL's exact GitHub repository root equalling a paper's code or
    project repository, or a shared DOI, arXiv ID or URL key. Names and evidence URLs that
    merely cite a paper never match.
    """
    matches = defaultdict(list)
    for paper in sorted(papers, key=lambda row: row['id']):
        repositories = {github_repository(paper.get(field), artifact=True) for field in ('code_url', 'project_url')} - {None}
        keys = publication_keys(paper)
        for resource in sorted(resources, key=lambda row: row['id']):
            repository = github_repository(resource.get('url'))
            if (repository and repository in repositories) or keys & publication_keys(resource):
                matches[('resource', resource['id'])].append(('paper', paper))
                matches[('paper', paper['id'])].append(('resource', resource))
    return dict(matches)


def _related_entries(entries: list[tuple[str, dict]], language: str) -> str:
    """Link the same work's detail page in the other directory, in the page language."""
    if not entries:
        return ''
    zh = language == 'zh'
    links = []
    for kind, record in entries:
        if kind == 'paper':
            title, context = record['title_zh' if zh else 'title'], ('研究论文' if zh else 'Research paper')
        else:
            title, context = (record.get('name_zh') or record['name']) if zh else record['name'], ('精选资源' if zh else 'Curated resource')
        links.append(f'<li><a href="{entry_path(kind, record["id"], language)}">{escape(title)}</a>'
                     f' <span class="entry-source-context">{context}</span></li>')
    heading = '相关条目' if zh else 'Related entries'
    note = '依据相同的代码仓库或论文标识关联。' if zh else 'Matched by the same code repository or publication identifier.'
    return (f'<section class="entry-section" aria-labelledby="entry-related"><h2 id="entry-related">{heading}</h2>'
            f'<p>{note}</p><ul class="entry-sources">{"".join(links)}</ul></section>')


def _output_path(root: Path, relative: str) -> Path:
    current = root
    for part in ('', *Path(relative).parts):
        current /= part
        if current.is_symlink():
            raise ValueError('Entry output paths must not be symlinks')
    return current


def _resource_content(record: dict, language: str, discussion: str = '') -> tuple[str, str, str]:
    zh = language == 'zh'
    label = lambda en, cn: cn if zh else en
    title = _text(record, 'name_zh' if zh else 'name')
    description = _text(record, f'description_{language}')
    kind = KIND_LABELS[record['kind']][int(zh)]
    facts = [(label('Type', '类型'), kind),
             (label('Category', '类别'), CATEGORIES[record['category']][int(zh)]),
             (label('Relationship', '关联'), RELATIONSHIPS[record['relationship']][int(zh)]),
             (label('Targets', '目标'), ' · '.join(TARGETS[t][int(zh)] for t in record['targets']))]
    requirements = ''.join(f'<li>{escape(item)}</li>' for item in _requirements(record, language))
    links = [_link(record['url'], label('Visit original resource', '访问原始资源'), primary=True)]
    if record['evidence_url'] != record['url']:
        links.append(_link(record['evidence_url'], label(*PRIMARY_SOURCE_LABEL)))
    content = f'''<header class="entry-heading"><p class="entry-eyebrow">{escape(kind)}</p><h1>{escape(title)}</h1>
  <p class="entry-description">{escape(description)}</p></header>
<nav class="entry-actions" aria-label="{label('Resource links', '资源链接')}">{''.join(links)}</nav>
<section class="entry-section" aria-labelledby="entry-requirements"><h2 id="entry-requirements">{label('Requirements and limitations', '使用条件与局限')}</h2><ul class="entry-requirements">{requirements}</ul></section>
<section class="entry-section" aria-labelledby="entry-review"><h2 id="entry-review">{label('About this entry', '关于此条目')}</h2>{_definitions(facts)}
<p class="entry-reviewed">{label('Sources reviewed', '来源复核于')} <time datetime="{escape(record['verified_at'], quote=True)}">{escape(record['verified_at'][:10])}</time></p>
<p class="entry-review-note">{label('The description was reviewed against primary sources. This does not establish runtime testing, security auditing or verified compatibility.', '说明已依据一手来源复核；这不代表已运行验证、经过安全审计或确认兼容。')}</p></section>
{discussion}{_sources([record['evidence_url'], *record.get('additional_evidence_urls', [])], language)}'''
    return title, description, content


def _paper_content(paper: dict, language: str, discussion: str = '') -> tuple[str, str, str]:
    zh = language == 'zh'
    label = lambda en, cn: cn if zh else en
    title = _text(paper, 'title_zh' if zh else 'title')
    description = _text(paper, f'description_{language}')
    status = STATUS_LABELS[paper['publication_status']][int(zh)]
    original = f'<p class="entry-original-title" lang="en">{escape(paper["title"])}</p>' if zh else ''
    links = [_link(paper['url'], label('Original paper', '原始论文'), primary=True), _link(paper['pdf_url'], 'PDF')]
    for field, en, cn in (('code_url', 'Code', '代码'), ('project_url', 'Project', '项目')):
        if paper.get(field):
            links.append(_link(paper[field], label(en, cn)))
    links.append(f'<a class="entry-link" href="/papers/citations/{paper["id"]}.bib" download="{paper["id"]}.bib" type="application/x-bibtex">BibTeX ↓</a>')
    facts = [(label('Venue', '发表载体'), paper['venue']),
             (label('Status', '发表状态'), status),
             (label('Publication / posting date', '出版／提交日期'), formatted_date(paper.get('publication_date'), language, paper['year'])),
             (label('Date source', '日期依据'), paper['date_basis_zh' if zh else 'date_basis'])]
    for field, en, cn in (('first_arxiv_date', 'First arXiv submission', 'arXiv 首次提交'),
                           ('arxiv_id', 'arXiv', 'arXiv'), ('arxiv_version_reviewed', 'Reviewed arXiv version', '已复核的 arXiv 版本'), ('doi', 'DOI', 'DOI')):
        if paper.get(field):
            facts.append((label(en, cn), formatted_date(paper[field], language) if field == 'first_arxiv_date' else paper[field]))
    content = f'''<header class="entry-heading"><p class="entry-eyebrow">{paper['year']} · {escape(status)}</p><h1>{escape(title)}</h1>{original}
<p class="entry-authors" lang="en">{escape('; '.join(paper['authors']))}</p><p class="entry-description">{escape(description)}</p></header>
<nav class="entry-actions" aria-label="{label('Paper and citation links', '论文与引文链接')}">{''.join(links)}</nav>
<section class="entry-section entry-scope" aria-labelledby="entry-scope"><h2 id="entry-scope">{label('Scope and limitations', '研究范围与局限')}</h2><p>{escape(paper[f'scope_limitations_{language}'])}</p></section>
<section class="entry-section" aria-labelledby="entry-relevance"><h2 id="entry-relevance">{label('Why it fits this collection', '与本合集的关联')}</h2><p>{escape(paper[f'why_fits_{language}'])}</p></section>
<section class="entry-section" aria-labelledby="entry-citation"><h2 id="entry-citation">{label('Publication and review details', '发表与复核详情')}</h2>{_definitions(facts)}
<p>{escape(paper['metadata_notes_zh' if zh else 'metadata_notes'])}</p>
<p class="entry-reviewed">{label('Sources reviewed', '来源复核于')} <time datetime="{escape(paper['verified_at'], quote=True)}">{escape(paper['verified_at'][:10])}</time></p>
<p class="entry-review-note">{label('Source review only; experiments were not rerun for this collection. Cite the original authors using the linked paper or BibTeX.', '本合集仅做来源复核，未重新运行论文实验。请通过原始论文或 BibTeX 引用原作者。')}</p></section>
{discussion}{_sources(paper['evidence_urls'], language)}'''
    return title, description, content


def _document(record, kind, language, *, site_url, repository_url, styles_href, entry_styles_href,
              favicon_href, social_image_href, icon_stylesheet_href, survey_discussions, related_entries):
    zh = language == 'zh'
    label = lambda en, cn: cn if zh else en
    locale, prefix = ('zh-CN', '/zh') if zh else ('en', '')
    path = entry_path(kind, record['id'], language)
    english, chinese = (site_url + entry_path(kind, record['id'], lang) for lang in ('en', 'zh'))
    canonical = site_url + path
    counterpart = entry_path(kind, record['id'], 'en' if zh else 'zh')
    listing = f'{prefix}/{kind}s/'
    list_name = label('Curated resources', '精选资源') if kind == 'resource' else label('Research papers', '研究论文')
    discussion = (_related_entries(related_entries.get((kind, record['id']), []), language)
                  + _survey_discussion(survey_discussions.get(record['id'], []), language))
    title, description, content = (_resource_content if kind == 'resource' else _paper_content)(record, language, discussion)
    # Resource names such as rr or GDB are often identical in both languages; the localized
    # category gives each <title> topic and language context. H1, og:title and JSON-LD keep the name.
    document_title = f'{title} · {CATEGORIES[record["category"]][int(zh)]}' if kind == 'resource' else title
    entity_id = canonical + ('#resource' if kind == 'resource' else '#paper')
    entity = ({'@type': 'CreativeWork', '@id': entity_id, 'url': record['url'], 'name': title, 'description': description}
              if kind == 'resource' else {**scholarly_article(record, language), '@id': entity_id})
    schema = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'WebPage', '@id': canonical + '#webpage', 'url': canonical, 'name': title,
         'description': description, 'inLanguage': locale, 'isPartOf': {'@id': site_url + '/#website'},
         'mainEntity': {'@id': entity_id}, 'breadcrumb': {'@id': canonical + '#breadcrumb'}},
        {'@type': 'BreadcrumbList', '@id': canonical + '#breadcrumb', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': label('Home', '首页'), 'item': site_url + prefix + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': list_name, 'item': site_url + listing},
            {'@type': 'ListItem', 'position': 3, 'name': title, 'item': canonical}]}, entity]}
    _public_url(social_image_href)  # The shared social block escapes but does not vet the URL.
    icon_css = f'<link rel="stylesheet" href="{_asset_url(icon_stylesheet_href)}">' if icon_stylesheet_href else ''
    github_icon = ('<span class="icon fa-symbol fa-github" aria-hidden="true"></span>' if icon_stylesheet_href
                   else '<span class="icon entry-github-fallback" aria-hidden="true">GH</span>')
    return f'''<!doctype html>
{MARKER}
<html lang="{locale}"{(' data-icon-set="fontawesome"' if icon_stylesheet_href else '')}>
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#ffffff">
  <title>{escape(document_title)} · AwesomeREA.org</title><meta name="description" content="{escape(description, quote=True)}">
  <link rel="canonical" href="{_public_url(canonical)}">
  <link rel="alternate" hreflang="en" href="{_public_url(english)}"><link rel="alternate" hreflang="zh-CN" href="{_public_url(chinese)}"><link rel="alternate" hreflang="x-default" href="{_public_url(english)}">
  {open_graph_meta(language=language, title=title, description=description, image_url=social_image_href, url=canonical)}
  <link rel="icon" href="{_asset_url(favicon_href)}" type="image/svg+xml"><link rel="stylesheet" href="{_asset_url(styles_href)}"><link rel="stylesheet" href="{_asset_url(entry_styles_href)}">{icon_css}
  {jsonld_script(schema)}
</head><body>
<a class="skip-link" href="#entry-content">{label('Skip to content', '跳到内容')}</a>
<header class="site-header"><div class="shell header-inner"><a class="wordmark" href="{prefix}/" aria-label="{label('AwesomeREA.org home', 'AwesomeREA.org 首页')}"><img class="brand-mark" src="{_asset_url(favicon_href)}" alt="" width="33" height="33" aria-hidden="true"><span>Awesome<span class="wordmark-rea">REA</span><span class="wordmark-domain">.org</span></span></a>
<nav class="header-nav" aria-label="{label('Main navigation', '主导航')}"><a class="entry-language" href="{counterpart}" lang="{('en' if zh else 'zh-CN')}" hreflang="{('en' if zh else 'zh-CN')}">{label('简体中文', 'English')}</a><a class="github-link" href="{_public_url(repository_url)}" target="_blank" rel="noopener noreferrer" aria-label="GitHub">{github_icon}<span>GitHub</span></a></nav></div></header>
<main class="shell entry-main" id="entry-content"><nav class="entry-breadcrumbs" aria-label="{label('Breadcrumb', '当前位置')}"><a href="{prefix}/">{label('Home', '首页')}</a><span aria-hidden="true">/</span><a href="{listing}">{list_name}</a><span aria-hidden="true">/</span><span aria-current="page">{escape(title)}</span></nav>
<article class="entry-article" data-entry-kind="{kind}" data-entry-id="{record['id']}">{content}</article>
<nav class="entry-return" aria-label="{label('Collection navigation', '合集导航')}"><a href="{listing}#{record['id']}">← {label('View in the directory', '在目录中查看')}</a><a href="{listing}">{list_name}</a><a href="{prefix}/">{label('Search the collection', '搜索合集')}</a></nav></main>
<footer class="site-footer"><div class="shell footer-top"><p>{label('An independent, source-reviewed collection.', '依据一手来源整理的独立合集。')}</p><nav class="footer-links" aria-label="{label('More from the collection', '更多合集内容')}"><a href="{prefix}/resources/">{label('Curated resources', '精选资源')}</a><a href="{prefix}/papers/">{label('Research papers', '研究论文')}</a><a href="{prefix}/about/">{label('About and sources', '关于与来源')}</a></nav></div><div class="shell footer-bottom">{label('Original editorial content: MIT. Linked projects, papers and assets retain their own rights and licenses.', '原创说明采用 MIT 许可；外部项目、论文与素材保留各自的权利和许可。')}</div></footer>
</body></html>
'''


def build_entry_pages(site_dir: Path, resources: list[dict], papers: list[dict], *,
                      site_url: str = 'https://awesomerea.org',
                      repository_url: str = 'https://github.com/reacher-z/Awesome-REA',
                      styles_href: str = '/styles.css', entry_styles_href: str = '/entry.css',
                      favicon_href: str = '/favicon.svg', social_image_href: str = 'https://awesomerea.org/social-card.png',
                      icon_stylesheet_href: str | None = None,
                      survey_discussions: dict | None = None) -> list[str]:
    """Write only curated /resources/<id>/ and /papers/<id>/ pairs; return sitemap URLs."""
    site_dir = Path(site_dir)
    site_url = site_url.rstrip('/')
    _public_url(site_url)
    if urlsplit(site_url).query or urlsplit(site_url).fragment or urlsplit(site_url).path:
        raise ValueError('The public site URL must be an HTTPS origin')
    options = dict(site_url=site_url, repository_url=repository_url, styles_href=styles_href,
                   entry_styles_href=entry_styles_href, favicon_href=favicon_href,
                   social_image_href=social_image_href, icon_stylesheet_href=icon_stylesheet_href,
                   survey_discussions=survey_discussions or {},
                   related_entries=matching_entries(resources, papers))
    rendered = {}
    for kind, records in (('resource', resources), ('paper', papers)):
        identifiers = set()
        for record in records:
            if not isinstance(record, dict) or record.get('verification') != 'source-reviewed':
                raise ValueError('Only source-reviewed curated entries have detail pages')
            identifier = record.get('id')
            entry_path(kind, identifier)
            if identifier in identifiers:
                raise ValueError('Duplicate detail-page identifier')
            identifiers.add(identifier)
            if kind == 'paper' and record.get('runtime_tested') is not False:
                raise ValueError('Paper pages describe source review, not runtime reproduction')
            for language in ('en', 'zh'):
                path = entry_path(kind, identifier, language)
                rendered[path] = _document(record, kind, language, **options)
    # Remove only obsolete pages carrying this builder's marker, never listing pages or citations.
    destinations = {path: _output_path(site_dir, path.lstrip('/') + 'index.html') for path in rendered}
    for prefix in ('resources', 'zh/resources', 'papers', 'zh/papers'):
        directory = _output_path(site_dir, prefix)
        for stale in directory.glob('*/index.html'):
            if stale.is_symlink() or stale.parent.is_symlink():
                raise ValueError('Entry output paths must not be symlinks')
            path = '/' + stale.parent.relative_to(site_dir).as_posix() + '/'
            if path not in rendered and MARKER in stale.read_text(encoding='utf-8'):
                stale.unlink()
                if not any(stale.parent.iterdir()):
                    stale.parent.rmdir()
    for path, content in rendered.items():
        destination = destinations[path]
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding='utf-8')
    return [site_url + path for path in rendered]
