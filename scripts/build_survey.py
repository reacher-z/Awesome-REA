"""Render an editorial survey with checked citations and complete static locales."""
from __future__ import annotations

from collections import defaultdict
from datetime import date
from html import escape
import hashlib
import json
from pathlib import Path
import re

from build_discovery_pages import jsonld_script
from build_paper_pages import STATUS_LABELS, bibtex_text, icon
from open_graph import THEME_COLOR_META, open_graph_meta, website_reference

ROOT = Path(__file__).resolve().parents[1]
TITLES = ('Reverse Engineering Anything: An Evidence-Centered Survey',
          '逆向工程万物：基于证据的软件重建综述')
CITATION = re.compile(r'\[\[([a-z0-9]+(?:-[a-z0-9]+)*)\]\]')


def read_survey():
    return json.loads((ROOT / 'data/survey.json').read_text(encoding='utf-8'))


def cited_ids(text):
    if '[[' in CITATION.sub('', text) or ']]' in CITATION.sub('', text):
        raise ValueError('Malformed survey citation')
    return CITATION.findall(text)


def public_url(value):
    from validate import public_https_error
    if public_https_error(value):
        raise ValueError('Survey references require public HTTPS URLs')
    return escape(value, quote=True)


def validate_survey(document, papers, resources):
    """A frozen editorial corpus must not silently grow with the live collection."""
    known = {r['id'] for r in [*papers, *resources]}
    paper_ids = {p['id'] for p in papers}
    assert document['schema_version'] == 1
    assert re.fullmatch(r'\d+\.\d+', document['version'])
    assert re.fullmatch(r'\d{4}-\d{2}-\d{2}', document['date'])
    date.fromisoformat(document['date'])
    assert re.fullmatch(r'[a-f0-9]{40}', document['snapshot']['revision'])
    corpus = document['paper_ids']
    assert len(corpus) == len(set(corpus)) == document['snapshot']['papers']
    assert set(corpus) <= paper_ids
    assert all(isinstance(i, str) and re.fullmatch(r'paper-[a-z0-9]+(?:-[a-z0-9]+)*', i) for i in corpus)
    for key in ('papers', 'cases', 'resources', 'selected_cases'):
        assert type(document['snapshot'][key]) is int and document['snapshot'][key] > 0
    assert 0 < document['snapshot']['cases'] <= document['snapshot']['resources']
    identifiers = [section['id'] for section in document['sections']]
    assert len(identifiers) == len(set(identifiers))
    assert not set(identifiers) & {'abstract', 'references', 'citation', 'survey-content'}
    for identifier in identifiers:
        assert re.fullmatch(r'[a-z][a-z0-9-]*', identifier)
        assert not identifier.startswith(('heading-', 'ref-', 'cite-', 'table-'))

    def pair(pair, *, citations=True):
        assert set(pair) == {'en', 'zh'}
        assert all(isinstance(v, str) and v.strip() for v in pair.values())
        assert re.search(r'[\u3400-\u9fff]', pair['zh']), 'Missing Chinese survey text'
        en, zh = cited_ids(pair['en']), cited_ids(pair['zh'])
        assert set(en) == set(zh), 'Survey translation changes citation coverage'
        assert set(en) <= known, 'Unknown survey citation'
        assert set(en) & paper_ids <= set(corpus), 'Citation outside the frozen survey corpus'
        assert citations or not (en or zh), 'Citations are not supported in this plain-text field'

    for key in ('subtitle', 'description', 'disclosure', 'reference_note'):
        pair(document[key], citations=False)
    for key in ('abstract', 'figure_caption'):
        pair(document[key])
    for item in document['findings']:
        pair(item)
    for item in document['pipeline']:
        pair(item['title'], citations=False); pair(item['text'], citations=False)
    used_tables = []
    for section in document['sections']:
        pair(section['title'], citations=False)
        if 'nav_title' in section:
            pair(section['nav_title'], citations=False)
        assert section['paragraphs'], 'Empty survey section'
        for paragraph in section['paragraphs']:
            pair(paragraph)
        for item in section.get('bullets', []):
            pair(item)
        if 'table' in section:
            assert section['table'] in document['tables']
            used_tables.append(section['table'])
    assert len(used_tables) == len(set(used_tables)) and set(used_tables) == set(document['tables'])
    for key, table in document['tables'].items():
        assert re.fullmatch(r'[a-z][a-z0-9-]*', key), 'Unsafe survey table key'
        pair(table['caption'])
        assert table['rows']
        assert len({row['reference'] for row in table['rows']}) == len(table['rows'])
        for header in table['headers']:
            pair(header, citations=False)
        for row in table['rows']:
            assert row['reference'] in known
            assert row['reference'] not in paper_ids or row['reference'] in corpus
            pair(row['label'])
            assert len(row['cells']) == len(table['headers']) - 1
            for cell in row['cells']:
                pair(cell)
    frozen = document['reference_records']
    assert isinstance(frozen, list) and len({r['id'] for r in frozen}) == len(frozen)
    required = set(reference_order(document))
    assert {r['id'] for r in frozen} == required
    assert required <= known
    case_rows = document['tables']['cases']['rows']
    cases = {r['id'] for r in frozen if r['kind'] == 'case-study'}
    assert len(case_rows) == document['snapshot']['selected_cases']
    assert {r['reference'] for r in case_rows} <= cases
    for record in frozen:
        assert record['id'] in known
        for key in ('url', 'pdf_url', 'code_url', 'evidence_url'):
            if record.get(key):
                public_url(record[key])


def reference_order(document):
    ordered = []

    def add(identifier):
        if identifier not in ordered:
            ordered.append(identifier)

    def prose(text):
        for identifier in cited_ids(text):
            add(identifier)

    prose(document['abstract']['en'])
    for finding in document['findings']:
        prose(finding['en'])
    for section in document['sections']:
        for paragraph in section['paragraphs']:
            prose(paragraph['en'])
        if section.get('figure'):
            prose(document['figure_caption']['en'])
        if section.get('table'):
            table = document['tables'][section['table']]
            prose(table['caption']['en'])
            for row in table['rows']:
                prose(row['label']['en'])
                add(row['reference'])
                for cell in row['cells']:
                    prose(cell['en'])
        for item in section.get('bullets', []):
            prose(item['en'])
    # Include the complete frozen paper corpus, with unused entries explicitly labeled.
    for identifier in document['paper_ids']:
        add(identifier)
    return ordered


def discussion_sections(document):
    """Map explicit section-prose citations to their localized discussion headings.

    Bibliography membership, table rows and front matter do not establish that a
    record is discussed in a section. The site builder supplies the same survey
    document already validated and rendered by build_survey().
    """
    discussions = {}
    for section in document['sections']:
        identifiers = []
        for paragraph in [*section['paragraphs'], *section.get('bullets', [])]:
            english = cited_ids(paragraph['en'])
            chinese = cited_ids(paragraph['zh'])
            if set(english) != set(chinese):
                raise ValueError('Survey discussion links require matching bilingual citations')
            for identifier in english:
                if identifier not in identifiers:
                    identifiers.append(identifier)
        for identifier in identifiers:
            discussions.setdefault(identifier, []).append({
                'section': section['id'], 'title': dict(section['title']),
            })
    return discussions


class Citations:
    def __init__(self, order, records, language):
        self.numbers = {identifier: n for n, identifier in enumerate(order, 1)}
        self.records, self.language = records, language
        self.backlinks = defaultdict(list)

    def text(self, value):
        pieces, previous = [], 0
        for match in CITATION.finditer(value):
            pieces.append(escape(value[previous:match.start()]))
            identifier = match[1]
            number = self.numbers[identifier]
            anchor = f'cite-{identifier}-{len(self.backlinks[identifier]) + 1}'
            self.backlinks[identifier].append(anchor)
            label = ('参考文献' if self.language == 'zh' else 'Reference') + f' {number}'
            pieces.append(f'<a class="survey-cite" id="{anchor}" href="#ref-{identifier}" aria-label="{label}">[{number}]</a>')
            previous = match.end()
        pieces.append(escape(value[previous:]))
        return ''.join(pieces)


def repository_bibtex():
    """Cite the collection; identity and author order follow CITATION.cff.

    The collection has no recorded release date or version. Do not inherit the
    editorial survey's date, version or title as repository publication metadata.
    """
    return ('@misc{awesome-rea,\n'
            '  author = {Zhang, Yuxuan and Wang, Haozhe and {Awesome REA contributors}},\n'
            '  title = {{Awesome Reverse Engineering Anything}},\n'
            '  howpublished = {GitHub repository},\n'
            '  url = {https://github.com/reacher-z/Awesome-REA}\n'
            '}\n')


def build_survey(site_dir, papers, resources, *, document=None, site_url='https://awesomerea.org',
                 repository_url='https://github.com/reacher-z/Awesome-REA',
                 styles_href='/styles.css', favicon_href='/favicon.svg',
                 social_image_href='https://awesomerea.org/social-card.png', icon_stylesheet_href=None):
    document = read_survey() if document is None else document
    validate_survey(document, papers, resources)
    public_url(site_url); public_url(repository_url)
    site_dir = Path(site_dir)
    records = {r['id']: r for r in document['reference_records']}
    paper_ids = set(document['paper_ids'])
    order = reference_order(document)
    css = site_dir / 'survey.css'
    css_href = '/survey.css' + ('?v=' + hashlib.sha256(css.read_bytes()).hexdigest()[:16] if css.is_file() else '')
    bibliography = '% Frozen survey paper corpus. Project evidence is cited through its original and reviewed entry links.\n\n'
    bibliography += '\n'.join(bibtex_text(records[i]) for i in order if i in paper_ids)
    citation = repository_bibtex()
    urls = []
    for language, prefix in (('en', ''), ('zh', '/zh')):
        zh = language == 'zh'
        choose = lambda en, cn: cn if zh else en
        text = lambda value: value[language]
        title = TITLES[int(zh)]
        canonical = site_url + prefix + '/survey/'
        counterpart = '/survey/' if zh else '/zh/survey/'
        citations = Citations(order, records, language)
        prose = citations.text
        abstract = prose(text(document['abstract']))
        findings = ''.join(f'<li>{prose(text(item))}</li>' for item in document['findings'])
        toc = [f'<li><a href="#abstract">{choose("Abstract", "摘要")}</a></li>']
        sections = []
        for number, section in enumerate(document['sections'], 1):
            identifier = section['id']
            heading = f'{number}. {text(section["title"])}'
            toc_title = f'{number}. {text(section.get("nav_title", section["title"]))}'
            toc.append(f'<li><a href="#{identifier}">{escape(toc_title)}</a></li>')
            body = ''.join(f'<p>{prose(text(p))}</p>' for p in section['paragraphs'])
            if section.get('figure'):
                stages = ''.join(f'<li><strong>{escape(text(s["title"]))}</strong><span>{escape(text(s["text"]))}</span></li>' for s in document['pipeline'])
                body += f'<figure class="survey-figure"><ol class="survey-pipeline">{stages}</ol><figcaption>{prose(text(document["figure_caption"]))}</figcaption></figure>'
            if section.get('table'):
                key = section['table']; table = document['tables'][key]
                headers = ''.join(f'<th scope="col">{escape(text(h))}</th>' for h in table['headers'])
                rows = []
                for row in table['rows']:
                    label = prose(text(row['label']) + ' [[' + row['reference'] + ']]')
                    cells = ''.join(f'<td>{prose(text(cell))}</td>' for cell in row['cells'])
                    rows.append(f'<tr data-survey-reference="{row["reference"]}"><th scope="row">{label}</th>{cells}</tr>')
                caption = prose(text(table['caption']))
                body += f'<div class="survey-table-wrap" tabindex="0" role="region" aria-labelledby="table-{key}"><table class="survey-table"><caption id="table-{key}">{caption}</caption><thead><tr>{headers}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
            if section.get('bullets'):
                body += '<ul>' + ''.join(f'<li>{prose(text(item))}</li>' for item in section['bullets']) + '</ul>'
            sections.append(f'<section class="survey-section" id="{identifier}" aria-labelledby="heading-{identifier}"><h2 id="heading-{identifier}">{escape(heading)}</h2>{body}</section>')
        reference_items = []
        for identifier in order:
            record = records[identifier]
            is_paper = identifier in paper_ids
            name = record['title_zh' if zh else 'title'] if is_paper else record.get('name_zh', record['name']) if zh else record['name']
            destination = f'{prefix}/{"papers" if is_paper else "resources"}/{identifier}/'
            links = [(record['url'], choose('Original', '原始来源')), (destination, choose('Reviewed entry', '已核查条目'))]
            if is_paper:
                metadata = '; '.join(record['authors']) + f'. {record["year"]}. {record["venue"]}. ' + STATUS_LABELS[record['publication_status']][int(zh)] + '.'
                links.extend([(record['pdf_url'], 'PDF'), (f'/papers/citations/{identifier}.bib', 'BibTeX')])
                if record.get('code_url'):
                    links.append((record['code_url'], choose('Artifact', '研究产物')))
            else:
                metadata = choose('Project documentation; sources reviewed ', '项目文档；来源复核于 ') + record['verified_at'][:10] + '.'
                if record['evidence_url'] != record['url']:
                    links.append((record['evidence_url'], choose('Pinned evidence', '固定版本证据')))
            nav = ''.join(f'<a href="{escape(url, quote=True)}">{escape(label)}</a>' for url, label in links)
            backlinks = ''.join(f'<a class="survey-backlink" href="#{anchor}" aria-label="{choose("Back to citation", "返回引用位置")} {n}">↩{n}</a>' for n, anchor in enumerate(citations.backlinks[identifier], 1))
            unused = '' if backlinks else f'<span class="survey-note">{choose("Corpus bibliography", "语料文献")}</span>'
            reference_items.append(f'<li class="survey-reference" id="ref-{identifier}" data-survey-reference="{identifier}"><strong>{escape(name)}</strong><div>{escape(metadata)}</div><div class="survey-reference-links">{nav}{backlinks}{unused}</div></li>')
        toc.extend([f'<li><a href="#references">{choose("References", "参考文献")}</a></li>', f'<li><a href="#citation">{choose("Cite the repository", "引用仓库")}</a></li>'])
        snapshot = dict(document['snapshot'])
        snapshot['domains'] = len({s['id'] for s in document['sections']} & {'website', 'game', 'app', 'binary', 'firmware', 'protocol'})
        schema = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'WebPage', '@id': canonical + '#webpage', 'url': canonical, 'name': title,
             'inLanguage': 'zh-CN' if zh else 'en', 'isPartOf': website_reference(site_url), 'mainEntity': {'@id': canonical + '#article'}},
            {'@type': 'Article', '@id': canonical + '#article', 'url': canonical, 'headline': title,
             'description': text(document['description']), 'genre': 'Editorial survey', 'version': document['version'],
             'inLanguage': 'zh-CN' if zh else 'en', 'datePublished': document['date'], 'dateModified': document['date'],
             'author': {'@type': 'Organization', 'name': 'Awesome REA contributors', 'url': repository_url},
             'publisher': {'@type': 'Organization', 'name': 'AwesomeREA.org', 'url': site_url + '/'},
             'citation': [{'@type': 'CreativeWork', 'name': records[i].get('title', records[i].get('name')), 'url': records[i]['url']} for i in order]}
        ]}
        icons = f'<link rel="stylesheet" href="{escape(icon_stylesheet_href, quote=True)}">' if icon_stylesheet_href else ''
        github_icon = icon('github', bool(icons)).replace('paper-github-fallback', 'survey-github-fallback')
        quick_links = []
        for section in document['sections']:
            table_key = section.get('table')
            if table_key in {'papers', 'cases'}:
                count = len(document['tables'][table_key]['rows'])
                label = choose('study comparisons', '项研究对比') if table_key == 'papers' else choose('case comparisons', '个案例对比')
                quick_links.append(f'<a href="#{section["id"]}">{count} {label}</a>')
        quick_links = ''.join(quick_links)
        stats = ''.join(f'<div><strong>{snapshot[key]}</strong><span>{label}</span></div>' for key, label in [('papers', choose('papers in the snapshot', '快照中的论文')), ('domains', choose('domains of reconstruction', '重建领域')), ('selected_cases', choose('cases compared here', '本综述对比案例'))])
        html = f'''<!doctype html>
<html lang="{('zh-CN' if zh else 'en')}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">{THEME_COLOR_META}
<title>{escape(title)} | AwesomeREA.org</title><meta name="description" content="{escape(text(document['description']), quote=True)}">
<link rel="canonical" href="{canonical}"><link rel="alternate" hreflang="en" href="{site_url}/survey/"><link rel="alternate" hreflang="zh-CN" href="{site_url}/zh/survey/"><link rel="alternate" hreflang="x-default" href="{site_url}/survey/">
{open_graph_meta(language=language, title=title, description=text(document['description']), image_url=social_image_href, url=canonical)}
<link rel="icon" href="{escape(favicon_href, quote=True)}" type="image/svg+xml"><link rel="stylesheet" href="{escape(styles_href, quote=True)}"><link rel="stylesheet" href="{css_href}">{icons}{jsonld_script(schema)}</head>
<body class="survey-page"><a class="skip-link" href="#survey-content">{choose('Skip to the survey', '跳到综述正文')}</a>
<header class="site-header"><div class="shell header-inner"><a class="wordmark" href="{prefix}/" aria-label="{choose('AwesomeREA.org home', 'AwesomeREA.org 首页')}"><img class="brand-mark" src="{escape(favicon_href, quote=True)}" alt="" width="33" height="33" aria-hidden="true"><span>Awesome<span class="wordmark-rea">REA</span><span class="wordmark-domain">.org</span></span></a><nav class="header-nav" aria-label="{choose('Main navigation', '主导航')}"><a class="survey-language" href="{counterpart}" lang="{choose('zh-CN', 'en')}" hreflang="{choose('zh-CN', 'en')}">{icon('globe', bool(icons))}{choose('简体中文', 'English')}</a><a class="github-link" href="{repository_url}">{github_icon}<span>GitHub</span></a></nav></div></header>
<main class="shell survey-main"><header class="survey-header"><p class="survey-kicker">{choose('AWESOME REA · EDITORIAL SURVEY', 'AWESOME REA · 专题综述')}</p><h1 class="survey-title">{escape(title)}</h1><p class="survey-deck">{escape(text(document['subtitle']))}</p><p class="survey-meta">{choose('Version', '版本')} {document['version']} · <time datetime="{document['date']}">{document['date']}</time> · {choose('Awesome REA contributors', 'Awesome REA 贡献者')}</p><p class="survey-note">{escape(text(document['disclosure']))}</p><div class="survey-actions"><a class="button button-primary" href="#abstract">{choose('Read the survey', '阅读综述')}</a>{quick_links}<a class="button button-outline" href="/survey/citation.bib" download="awesome-rea.bib">{choose('Cite the repository', '引用仓库')} · BibTeX ↓</a></div><div class="survey-corpus">{stats}</div></header>
<div class="survey-layout"><nav class="survey-toc survey-toc-desktop" aria-label="{choose('Survey contents', '综述目录')}"><h2>{choose('Contents', '目录')}</h2><ol>{''.join(toc)}</ol><p><a href="#citation">{choose('Repository citation', '仓库引用信息')}</a></p></nav><details class="survey-toc-mobile"><summary>{choose('Contents', '目录')} · {len(document['sections'])} {choose('sections', '节')}</summary><nav aria-label="{choose('Survey contents', '综述目录')}"><ol>{''.join(toc)}</ol></nav></details>
<article class="survey-article" id="survey-content" data-survey-version="{document['version']}"><section class="survey-abstract" id="abstract"><h2>{choose('Abstract', '摘要')}</h2><p>{abstract}</p></section><section class="survey-findings" aria-labelledby="survey-findings-title"><h2 id="survey-findings-title">{choose('Main findings', '主要认识')}</h2><ul>{findings}</ul></section>{''.join(sections)}
<section class="survey-section" id="references"><h2>{choose('References', '参考文献')}</h2><p class="survey-note">{escape(text(document['reference_note']))}</p><p><a href="/survey/references.bib" download="awesome-rea-survey-references.bib">{choose('Download the paper references', '下载论文参考文献')} · BibTeX ↓</a></p><ol class="survey-references">{''.join(reference_items)}</ol></section>
<section class="survey-section" id="citation"><h2>{choose('Cite the repository', '引用仓库')}</h2><p>{choose('Use this citation for the Awesome REA repository. Cite individual papers and projects from their original sources.', '此条目用于引用 Awesome REA 仓库。引用单篇论文或项目时，请使用各自的原始来源。')}</p><p><a href="{repository_url}">GitHub · Awesome REA</a> · <a href="{repository_url}/blob/main/CITATION.cff">CITATION.cff</a></p><pre class="survey-citation-block"><code>{escape(citation)}</code></pre><p><a href="{repository_url}/tree/{snapshot['revision']}">{choose('Catalog snapshot used in this survey', '本综述使用的目录快照')}</a> · <a href="{repository_url}/issues">{choose('Suggest a correction', '建议修订')}</a></p></section></article></div></main>
<footer class="site-footer"><div class="shell footer-top"><p>{choose('A living companion to the Awesome REA collection.', 'Awesome REA 资源合集的持续更新专题。')}</p><div class="footer-links"><a href="{prefix}/">{choose('Search resources', '搜索资源')}</a><a href="{prefix}/cases/">{choose('Case studies', '案例合集')}</a><a href="{prefix}/papers/">{choose('Research papers', '研究论文')}</a><a href="{prefix}/about/">{choose('About and sources', '关于与来源')}</a></div></div><div class="shell footer-bottom">{choose('Original editorial synthesis: MIT. Linked publications and projects retain their own rights.', '原创综述内容采用 MIT 许可；所引论文与项目保留各自权利。')}</div></footer></body></html>'''
        destination = site_dir / prefix.lstrip('/') / 'survey/index.html'
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(html, encoding='utf-8')
        urls.append(canonical)
    (site_dir / 'survey/citation.bib').write_text(citation, encoding='utf-8')
    (site_dir / 'survey/references.bib').write_text(bibliography, encoding='utf-8')
    return urls
