"""Markdown and JSON twins of the HTML pages, and the full-catalog Markdown for agents.

Every curated resource and paper page ``/<kind>s/<id>/`` (and its ``/zh/`` counterpart) has an ``index.md``
beside it in the page language, and one bilingual ``record.json`` at the English path. Collection and
category pages have an ``index.md`` and, where one exists, a JSON alternate. Each HTML page advertises its
twins with ``<link rel="alternate">`` (``alternate_links``), the convention llms.txt v2 names
(https://llmstxt.org/). ``_headers`` serves the Markdown as ``text/markdown; charset=utf-8`` with a
``Link: <page>; rel="canonical"`` header, so the twin never competes with its page in search.

Twins are built only from recorded fields, like the pages: no ratings, authors, licenses or runtime claims.
A paper with ``authors_omitted`` lists no names and points to the paper instead.
"""
from __future__ import annotations

import json
from html import escape
import re

from build_paper_pages import AUTHORS_OMITTED, STATUS_LABELS, authors_omitted, bibtex_text, formatted_date
from build_readme import CATEGORIES, KIND_LABELS, RELATIONSHIPS, REQUIREMENTS_LABEL, TARGETS
from data_classes import placement_facts
from requirement_facets import FACETS, ordered_items

MARKDOWN = 'index.md'
RECORD_JSON = 'record.json'
COLLECTION_JSON = 'index.json'
MARKDOWN_TYPE = 'text/markdown'
JSON_TYPE = 'application/json'
# The same fields the public download bundle publishes, plus the inclusion date and requirement labels.
RESOURCE_FIELDS = ('id', 'name', 'name_zh', 'url', 'kind', 'class', 'category', 'group', 'relationship', 'targets',
                   'description_en', 'description_zh', 'requirements', 'requirements_zh', 'requirement_facets',
                   'reconstruction_method', 'evidence_url', 'additional_evidence_urls', 'added_at', 'verified_at',
                   'verification', 'source_unavailable', 'evidence_class', 'evidence_status', 'scope', 'preview_kind')
PAPER_FIELDS = ('id', 'title', 'title_zh', 'authors', 'authors_omitted', 'year', 'publication_date', 'date_precision',
                'date_basis', 'date_basis_zh', 'venue', 'publication_status', 'arxiv_id', 'arxiv_version_reviewed',
                'first_arxiv_date', 'doi', 'url', 'pdf_url', 'code_url', 'project_url', 'targets', 'kind', 'class',
                'description_en', 'description_zh', 'scope_limitations_en', 'scope_limitations_zh', 'why_fits_en',
                'why_fits_zh', 'metadata_notes', 'metadata_notes_zh', 'citation', 'evidence_urls', 'added_at',
                'verified_at', 'verification', 'runtime_tested')
REVIEW_NOTES = {
    'resource': ('The description was reviewed against primary sources.',
                 '说明已依据一手来源复核。'),
    'paper': ('Reviewed against the paper and its primary sources. Cite the original authors using '
              'the linked paper or BibTeX.', '已依据论文及一手来源复核。请通过原始论文或 BibTeX 引用原作者。'),
}
LICENSE_NOTE = ('Original editorial content: MIT. Linked projects, papers and assets retain their own rights and licenses.',
                '原创说明采用 MIT 许可；外部项目、论文与素材保留各自的权利和许可。')


def source_status(record: dict, language: str) -> str | None:
    """The source-status fact for a record whose source no longer resolves, or None."""
    check = record.get('source_unavailable')
    if not check:
        return None
    day, status = check['checked_at'][:10], check['http_status']
    return f'无法访问 · {day} 返回 HTTP {status}' if language == 'zh' else f'Unavailable · HTTP {status} on {day}'


def page_prefix(language: str) -> str:
    return '/zh' if language == 'zh' else ''


def entry_route(kind: str, identifier: str, language: str = 'en') -> str:
    return f'{page_prefix(language)}/{kind}s/{identifier}/'


def record_json_route(kind: str, identifier: str) -> str:
    """One bilingual JSON twin per entry, at the English path; both language pages advertise it."""
    return f'/{kind}s/{identifier}/{RECORD_JSON}'


def alternate_links(*, markdown: str | None = None, json_href: str | None = None) -> str:
    """The <head> links that advertise a page's Markdown and JSON twins (no hreflang: they are formats)."""
    links = []
    if markdown:
        links.append(f'<link rel="alternate" type="{MARKDOWN_TYPE}" href="{escape(markdown, quote=True)}" title="Markdown">')
    if json_href:
        links.append(f'<link rel="alternate" type="{JSON_TYPE}" href="{escape(json_href, quote=True)}" title="JSON">')
    return ''.join(links)


def text(value) -> str:
    """One line of plain text: collapse whitespace so a value never starts a Markdown block of its own."""
    return ' '.join(str(value).split())


def label_text(value) -> str:
    """Text inside a link label, with brackets and backslashes escaped."""
    return re.sub(r'([\\\[\]])', r'\\\1', text(value))


def link(label, url: str) -> str:
    return f'[{label_text(label)}]({url})'


def bullet_facts(facts, language: str = 'en') -> list[str]:
    separator = '：' if language == 'zh' else ': '
    return [f'- {label}{separator}{value}' for label, value in facts if value]


def json_text(value) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n'


def resource_record(record: dict, site_url: str) -> dict:
    """The bilingual JSON twin of a resource page: recorded fields plus the entry's own URLs."""
    value = {key: record[key] for key in RESOURCE_FIELDS if key in record}
    identifier = record['id']
    if record.get('preview'):
        # The documented demo screenshot or video thumbnail, served from this site.
        value['preview_url'] = site_url + record['preview']
    value.update(record_type='resource', entry_url=site_url + entry_route('resource', identifier),
                 entry_url_zh=site_url + entry_route('resource', identifier, 'zh'),
                 markdown_url=site_url + entry_route('resource', identifier) + MARKDOWN,
                 markdown_url_zh=site_url + entry_route('resource', identifier, 'zh') + MARKDOWN,
                 json_url=site_url + record_json_route('resource', identifier))
    return value


def paper_record(paper: dict, site_url: str) -> dict:
    """The bilingual JSON twin of a paper page; an omitted author list stays omitted."""
    value = {key: paper[key] for key in PAPER_FIELDS if key in paper}
    identifier = paper['id']
    value.update(record_type='paper', entry_url=site_url + entry_route('paper', identifier),
                 entry_url_zh=site_url + entry_route('paper', identifier, 'zh'),
                 markdown_url=site_url + entry_route('paper', identifier) + MARKDOWN,
                 markdown_url_zh=site_url + entry_route('paper', identifier, 'zh') + MARKDOWN,
                 json_url=site_url + record_json_route('paper', identifier),
                 bibtex_url=f'{site_url}/papers/citations/{identifier}.bib')
    return value


def _requirements(record: dict, language: str) -> list[str]:
    items = record.get('requirements_zh' if language == 'zh' else 'requirements') or []
    items = [items] if isinstance(items, str) else items
    lines = []
    for facet, item in ordered_items(record, items):
        # The closing ** must follow a non-space character to stay bold in CommonMark.
        lead = (f'**{FACETS[facet][1]}：**' if language == 'zh' else f'**{FACETS[facet][0]}:** ') if facet else ''
        lines.append(f'- {lead}{text(item)}')
    return lines


def _sources(urls: list[str]) -> list[str]:
    return [f'{number}. <{url}>' for number, url in enumerate(dict.fromkeys(urls), 1)]


def resource_markdown(record: dict, language: str, *, site_url: str, siblings: dict | None = None,
                      related: list[tuple[str, dict]] = (), standalone: bool = True) -> str:
    """The Markdown twin of a resource page, in the page language.

    ``standalone=False`` drops what llms-full.txt states once for every entry: the twin links and the review note.
    """
    zh = language == 'zh'
    choose = lambda en, cn: cn if zh else en
    identifier = record['id']
    name = (record.get('name_zh') or record['name']) if zh else record['name']
    other = 'en' if zh else 'zh'
    facts = [
        (choose('Type', '类型'), KIND_LABELS[record['kind']][zh]),
        *placement_facts(record, zh, TARGETS),
        (choose('Category', '类别'), CATEGORIES[record['category']][zh]),
        (choose('Relationship', '关联'), RELATIONSHIPS[record['relationship']][zh]),
        (choose('Sources reviewed', '来源复核于'), record['verified_at'][:10]),
        (choose('Source status', '来源状态'), source_status(record, language)),
        (choose('Added to the catalog', '收录于'), record.get('added_at')),
        (choose('Original resource', '原始资源'), f'<{record["url"]}>'),
    ]
    if record['evidence_url'] != record['url']:
        facts.append((choose('Primary source', '一手来源'), f'<{record["evidence_url"]}>'))
    facts.append((choose('Catalog page', '目录页面'), f'<{site_url}{entry_route("resource", identifier, language)}>'))
    if standalone:
        facts += [
            (choose('Record JSON', '记录 JSON'), f'<{site_url}{record_json_route("resource", identifier)}>'),
            (choose('Chinese version', '英文版'), link('简体中文' if not zh else 'English', site_url + entry_route('resource', identifier, other) + MARKDOWN)),
        ]
    lines = [f'# {text(name)}', '', f'> {text(record[f"description_{language}"])}', '', *bullet_facts(facts, language), '',
             f'## {REQUIREMENTS_LABEL[zh]}', '', *_requirements(record, language), '',
             f'## {choose("Primary sources", "一手来源")}', '',
             *_sources([record['evidence_url'], *record.get('additional_evidence_urls', [])]), '']
    if related:
        lines += [f'## {choose("Related entries", "相关条目")}', '',
                  choose('Matched by the same code repository or publication identifier.', '依据相同的代码仓库或论文标识关联。'), '']
        for kind, other_record in related:
            title = (other_record['title_zh'] if zh else other_record['title']) if kind == 'paper' else (
                (other_record.get('name_zh') or other_record['name']) if zh else other_record['name'])
            context = choose('Research paper', '研究论文') if kind == 'paper' else choose('Curated resource', '精选资源')
            lines.append(f'- {link(title, site_url + entry_route(kind, other_record["id"], language) + MARKDOWN)} · {context}')
        lines.append('')
    if siblings and siblings.get('siblings'):
        from build_discovery_pages import SECTIONS
        section = SECTIONS[siblings['section']][zh]
        lines += [f'## {choose(f"More in {section}", f"同分区更多条目：{section}")}', '']
        for sibling in siblings['siblings']:
            title = (sibling.get('name_zh') or sibling['name']) if zh else sibling['name']
            lines.append(f'- {link(title, site_url + entry_route("resource", sibling["id"], language) + MARKDOWN)} · {KIND_LABELS[sibling["kind"]][zh]}')
        lines.append('')
    if standalone:
        lines += [f'## {choose("About this entry", "关于此条目")}', '', REVIEW_NOTES['resource'][zh], LICENSE_NOTE[zh], '']
    return '\n'.join(lines)


def paper_markdown(paper: dict, language: str, *, site_url: str, related: list[tuple[str, dict]] = (),
                   standalone: bool = True) -> str:
    """The Markdown twin of a paper page; `authors_omitted` names nobody and links the paper."""
    zh = language == 'zh'
    choose = lambda en, cn: cn if zh else en
    identifier = paper['id']
    title = paper['title_zh'] if zh else paper['title']
    authors = (link(choose(*AUTHORS_OMITTED), paper['url']) if authors_omitted(paper)
               else text('; '.join(paper['authors'])))
    facts = [
        (choose('Authors', '作者'), authors),
        (choose('Original title', '原标题'), text(paper['title']) if zh else None),
        (choose('Venue', '发表载体'), text(paper['venue'])),
        (choose('Status', '发表状态'), STATUS_LABELS[paper['publication_status']][zh]),
        (choose('Publication / posting date', '出版／提交日期'), formatted_date(paper.get('publication_date'), language, paper['year'])),
        (choose('Date source', '日期依据'), text(paper['date_basis_zh' if zh else 'date_basis'])),
        (choose('First arXiv submission', 'arXiv 首次提交'), formatted_date(paper['first_arxiv_date'], language) if paper.get('first_arxiv_date') else None),
        ('arXiv', paper.get('arxiv_id')),
        (choose('Read in a terminal', '终端阅读'), f'`hf papers read {paper["arxiv_id"]}`' if paper.get('arxiv_id') else None),
        (choose('Reviewed arXiv version', '已复核的 arXiv 版本'), paper.get('arxiv_version_reviewed')),
        ('DOI', paper.get('doi')),
        (choose('Sources reviewed', '来源复核于'), paper['verified_at'][:10]),
        (choose('Added to the catalog', '收录于'), paper.get('added_at')),
        (choose('Original paper', '原始论文'), f'<{paper["url"]}>'),
        ('PDF', f'<{paper["pdf_url"]}>'),
        (choose('Code', '代码'), f'<{paper["code_url"]}>' if paper.get('code_url') else None),
        (choose('Project', '项目'), f'<{paper["project_url"]}>' if paper.get('project_url') else None),
        ('BibTeX', f'<{site_url}/papers/citations/{identifier}.bib>'),
        (choose('Catalog page', '目录页面'), f'<{site_url}{entry_route("paper", identifier, language)}>'),
    ]
    if standalone:
        facts += [
            (choose('Record JSON', '记录 JSON'), f'<{site_url}{record_json_route("paper", identifier)}>'),
            (choose('Chinese version', '英文版'), link('简体中文' if not zh else 'English', site_url + entry_route('paper', identifier, 'en' if zh else 'zh') + MARKDOWN)),
        ]
    lines = [f'# {text(title)}', '', f'> {text(paper[f"description_{language}"])}', '', *bullet_facts(facts, language), '',
             f'## {choose("Scope and limitations", "研究范围与局限")}', '', text(paper[f'scope_limitations_{language}']), '',
             f'## {choose("Why it fits this collection", "与本合集的关联")}', '', text(paper[f'why_fits_{language}']), '',
             f'## {choose("Publication and review notes", "发表与复核说明")}', '', text(paper['metadata_notes_zh' if zh else 'metadata_notes']), '',
             f'## BibTeX', '', '```bibtex', bibtex_text(paper).rstrip(), '```', '',
             f'## {choose("Primary sources", "一手来源")}', '', *_sources(paper['evidence_urls']), '']
    if related:
        lines += [f'## {choose("Related entries", "相关条目")}', '']
        for kind, record in related:
            name = (record.get('name_zh') or record['name']) if zh else record['name']
            lines.append(f'- {link(name, site_url + entry_route(kind, record["id"], language) + MARKDOWN)} · {choose("Curated resource", "精选资源")}')
        lines.append('')
    if standalone:
        lines += [f'## {choose("About this entry", "关于此条目")}', '', REVIEW_NOTES['paper'][zh], LICENSE_NOTE[zh], '']
    return '\n'.join(lines)


def collection_markdown(*, title: str, description: str, language: str, canonical: str, items: list[dict],
                        notes: list[str] = (), groups: list[tuple[str, list[dict]]] | None = None,
                        json_url: str | None = None, counterpart: str | None = None) -> str:
    """The Markdown twin of a listing: its summary, then each listed item as a link with a short description.

    ``items`` (or ``groups`` of items under subheadings) hold ``name``, ``url`` and optional ``description``
    and ``meta`` strings. ``url`` should be the item's own Markdown twin where one exists.
    """
    zh = language == 'zh'
    lines = [f'# {text(title)}', '', f'> {text(description)}', '']
    lines += [text(note) for note in notes if note]
    if notes:
        lines.append('')
    facts = [('HTML', f'<{canonical}>')]
    if json_url:
        facts.append(('JSON', f'<{json_url}>'))
    if counterpart:
        facts.append(('English' if zh else '简体中文', f'<{counterpart}>'))
    lines += [*bullet_facts(facts, language), '']

    def rows(entries):
        for item in entries:
            details = ' · '.join(text(part) for part in (item.get('meta'), item.get('description')) if part)
            yield f'- {link(item["name"], item["url"])}' + ((('：' if zh else ': ') + details) if details else '')
    for heading, entries in (groups if groups is not None else [(None, items)]):
        if heading:
            lines += [f'## {text(heading)}', '']
        lines += [*rows(entries), '']
    return '\n'.join(lines)


def full_catalog_markdown(resources: list[dict], papers: list[dict], language: str, *, site_url: str,
                          sections: dict, section_of, header: str) -> str:
    """llms-full.txt: every curated resource, grouped as on /resources/, then every paper, in one file."""
    zh = language == 'zh'
    choose = lambda en, cn: cn if zh else en
    # Stated once here instead of under every entry.
    lines = [header.rstrip('\n'), '', REVIEW_NOTES['resource'][zh], REVIEW_NOTES['paper'][zh], LICENSE_NOTE[zh], '']
    groups: dict[str, list[dict]] = {key: [] for key in sections}
    for record in resources:
        groups[section_of(record)].append(record)
    lines += [f'## {choose("Curated resources", "精选资源")} ({len(resources):,})', '']
    for key, labels in sections.items():
        if not groups[key]:
            continue
        lines += [f'### {labels[zh]} ({len(groups[key]):,})', '']
        for record in groups[key]:
            body = resource_markdown(record, language, site_url=site_url, standalone=False)
            # Entry headings move down two levels; the requirement and source lists stay complete.
            lines += [re.sub(r'^(#+) ', lambda match: '#' * (len(match[1]) + 3) + ' ', line) for line in body.split('\n')]
    lines += [f'## {choose("Research papers", "研究论文")} ({len(papers):,})', '']
    for paper in papers:
        body = paper_markdown(paper, language, site_url=site_url, standalone=False)
        lines += [re.sub(r'^(#+) ', lambda match: '#' * (len(match[1]) + 2) + ' ', line) for line in body.split('\n')]
    return '\n'.join(lines).rstrip('\n') + '\n'
