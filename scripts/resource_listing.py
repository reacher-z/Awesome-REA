"""The /resources/ listing: every curated record as an index-card row, with search, filters and section links.

Sections, targets, kinds and categories all come from the catalogue's own label tables, so changing the major
categories there changes this page without touching its layout.
"""
from __future__ import annotations

from collections import Counter
from html import escape

from build_home import FEATURED, KIND_ORDER, PINNED, _folder_tabs, _ordered_targets, evidence_legend, index_card, stored_targets
from build_readme import CATEGORIES, KIND_LABELS
from site_shell import icon

# Rows per page, for the static pages and for filtered results alike.
PER_PAGE = 100
TEXT = {
    'en': {
        'crumbs': 'Breadcrumb', 'home': 'Home', 'title': 'Curated reverse engineering resources', 'search_label': 'Filter resources', 'placeholder': 'Filter by name, tool or target',
        'sections': 'Filed under', 'sections_note': 'Each record is filed once. Tabs count every target it covers.', 'filters': 'Filters', 'clear': 'Clear all', 'close': 'Close filters', 'show': 'Show results', 'kind': 'Kind', 'category': 'Category',
        'show_all': 'Show all {n}', 'all': 'All <strong>{n}</strong> resources', 'results': 'Results', 'sort': 'Sort', 'featured': 'Featured', 'reviewed': 'Recently reviewed',
        'added': 'Recently added', 'name': 'Name A–Z', 'suggest': 'Suggest a resource', 'data': 'Download the data', 'evidence_class': 'Evidence class', 'all_classes': 'All classes', 'unknown': 'Unknown',
        'range': 'Showing <strong>{a}–{b}</strong> of <strong>{n}</strong>', 'pages': 'Pages', 'previous': 'Previous', 'next': 'Next', 'page_title': 'page {n}',
    },
    'zh': {
        'crumbs': '当前位置', 'home': '首页', 'title': '精选逆向工程资源', 'search_label': '筛选资源', 'placeholder': '按名称、工具或目标筛选',
        'sections': '归类', 'sections_note': '每条记录只归入一处；标签页统计它涉及的所有目标。', 'filters': '筛选', 'clear': '清除全部', 'close': '关闭筛选', 'show': '查看结果', 'kind': '类型', 'category': '类别',
        'show_all': '显示全部 {n} 项', 'all': '共 <strong>{n}</strong> 项资源', 'results': '结果', 'sort': '排序', 'featured': '精选', 'reviewed': '最近复核',
        'added': '最近新增', 'name': '名称 A–Z', 'suggest': '推荐资源', 'data': '下载数据', 'evidence_class': '证据档位', 'all_classes': '全部档位', 'unknown': '未知',
        'range': '显示第 <strong>{a}–{b}</strong> 项，共 <strong>{n}</strong> 项', 'pages': '分页', 'previous': '上一页', 'next': '下一页', 'page_title': '第 {n} 页',
    },
}


def _count(number: int) -> str:
    return f'{number:,}'


def in_section_order(records: list[dict]) -> list[dict]:
    """Pinned and featured records, then by kind (tools before case studies), keeping the catalogue's order inside each kind."""
    rank = {identifier: position for position, identifier in enumerate(PINNED + FEATURED)}
    return sorted(records, key=lambda record: (rank.get(record['id'], len(rank)), KIND_ORDER.index(record['kind'])))


def facet(name: str, legend: str, options: list[tuple[str, str, int]], language: str, more_after: int | None = None) -> str:
    def option(value: str, label: str, number: int) -> str:
        return (f'<label class="opt"><input type="checkbox" name="{name}" value="{escape(value, quote=True)}">'
                f'<span class="opt-box" aria-hidden="true">{icon("check")}</span><span class="opt-l">{escape(label)}</span>'
                f'<span class="opt-n">{_count(number)}</span></label>')
    head, tail = (options[:more_after], options[more_after:]) if more_after else (options, [])
    body = ''.join(option(*item) for item in head)
    if tail:
        more = TEXT[language]['show_all'].format(n=len(options))
        body += f'<details class="opt-more"><summary>{more}</summary>{"".join(option(*item) for item in tail)}</details>'
    return f'<fieldset class="facet" data-facet="{name}"><legend>{legend}</legend>{body}</fieldset>'


def page_path(page: int, language: str = 'en') -> str:
    """/resources/ is page 1; later pages live at /resources/page/<n>/."""
    prefix = '/zh' if language == 'zh' else ''
    return f'{prefix}/resources/' if page == 1 else f'{prefix}/resources/page/{page}/'


def page_count(total: int) -> int:
    return max(1, -(-total // PER_PAGE))


def listing_pages(groups: dict[str, list[dict]], section_labels: dict[str, tuple[str, str]]) -> tuple[dict[str, int], dict[str, int]]:
    """The static page of every record, and of the first row of every section."""
    records, sections = {}, {}
    position = 0
    for key in section_labels:
        for record in in_section_order(groups.get(key, [])):
            page = position // PER_PAGE + 1
            records[record['id']] = page
            sections.setdefault(key, page)
            position += 1
    return records, sections


def record_href(identifier: str, page: int, language: str) -> str:
    return f'{page_path(page, language)}#{identifier}'


def section_href(key: str, page: int, language: str, current: int | None = None) -> str:
    return f'#heading-{key}' if page == current else f'{page_path(page, language)}#heading-{key}'


def _pager(page: int, pages: int, language: str) -> str:
    """Plain links between the static pages; site.js redraws the pager for filtered results."""
    text = TEXT[language]
    if pages == 1:
        return f'<nav class="pager" aria-label="{text["pages"]}" data-pager></nav>'
    shown = sorted({1, 2, page - 1, page, page + 1, pages - 1, pages} & set(range(1, pages + 1)))
    items, last = '', 0
    for number in shown:
        if number - last > 1:
            items += '<li class="gap" aria-hidden="true">…</li>'
        current = ' aria-current="page"' if number == page else ''
        items += f'<li><a href="{page_path(number, language)}" data-page="{number}"{current}>{number}</a></li>'
        last = number
    step = lambda number, label, rel: (f'<a class="pg-step" href="{page_path(number, language)}" data-page="{number}" rel="{rel}">{label}</a>'
                                       if 1 <= number <= pages else f'<span class="pg-step" aria-disabled="true">{label}</span>')
    return (f'<nav class="pager pager-static" aria-label="{text["pages"]}" data-pager>{step(page - 1, text["previous"], "prev")}'
            f'<ol>{items}</ol>{step(page + 1, text["next"], "next")}</nav>')


def resource_page_head(resources: list[dict], language: str, page: int = 1) -> str:
    text = TEXT[language]
    prefix = '/zh' if language == 'zh' else ''
    # A later page's trail names the listing, then the page.
    current = (f'<span aria-current="page">{text["title"]}</span>' if page == 1 else
               f'<a href="{prefix}/resources/">{text["title"]}</a><span aria-hidden="true">/</span><span aria-current="page">{text["page_title"].format(n=page).capitalize()}</span>')
    return (f'<div class="page-head wrap"><nav class="crumbs" aria-label="{text["crumbs"]}"><a href="{prefix}/">{text["home"]}</a><span aria-hidden="true">/</span>{current}</nav>'
            f'<div class="ph-row"><div class="ph-title"><h1>{text["title"]}</h1><span class="h-count">{_count(len(resources))}</span></div>'
            f'<form class="list-search" role="search" data-list-search><label class="vh" for="lq">{text["search_label"]}</label>{icon("search")}'
            f'<input id="lq" name="q" type="search" placeholder="{text["placeholder"]}" autocomplete="off" spellcheck="false" data-list-input><kbd class="hs-kbd">/</kbd></form></div>'
            f'{_folder_tabs(resources, language, prefix)}</div>')


def resource_listing(resources: list[dict], groups: dict[str, list[dict]], section_labels: dict[str, tuple[str, str]], language: str, repository_url: str,
                     page: int = 1) -> str:
    """One static page of rows in section order. Scripts filter the whole catalogue in place; the pager and section links work without them."""
    zh = language == 'zh'
    text = TEXT[language]
    prefix = '/zh' if zh else ''
    order = stored_targets()
    sections = [(key, labels[zh]) for key, labels in section_labels.items() if groups.get(key)]
    _, section_pages = listing_pages(groups, section_labels)
    total = sum(len(groups[key]) for key, _ in sections)
    pages = page_count(total)
    if not 1 <= page <= pages:
        raise ValueError(f'No resource listing page {page}')
    # A section that starts on another page keeps its old fragment here, on its link, which leads to that page.
    navigation = ''.join(f'<li><a href="{section_href(key, section_pages[key], language, page)}"{"" if section_pages[key] == page else f' id="{key}"'}'
                         f' data-section-link data-section="{key}">{escape(label)}<span class="count">{_count(len(groups[key]))}</span></a></li>'
                         for key, label in sections)
    start, end = (page - 1) * PER_PAGE, page * PER_PAGE
    rows, position = [], 0
    for key, label in sections:
        records = in_section_order(groups[key])
        shown = records[max(0, start - position):max(0, end - position)]
        if shown:
            # The heading carries its anchors only on the page where the section starts.
            anchors = f' id="heading-{key}"' if section_pages[key] == page else ''
            legacy = f'<a id="{key}"></a>' if section_pages[key] == page else ''
            rows.append(f'<li class="list-section"><h2{anchors}>{legacy}{escape(label)}</h2><span class="count">{_count(len(groups[key]))}</span></li>')
            rows.extend(index_card(record, language, _ordered_targets(record, order), prefix=prefix, listing=True) for record in shown)
        position += len(records)
    shown_count = min(end, total) - start
    meta = text['all'].format(n=_count(total)) if pages == 1 else text['range'].format(a=_count(start + 1), b=_count(start + shown_count), n=_count(total))
    kinds = Counter(record['kind'] for record in resources)
    categories = Counter(record['category'] for record in resources)
    kind_options = [(kind, KIND_LABELS[kind][zh], number) for kind, number in kinds.most_common()]
    category_options = [(key, CATEGORIES[key][zh], number) for key, number in sorted(categories.items(), key=lambda item: (-item[1], item[0]))]
    evidence_counts = Counter('unknown' if record.get('evidence_status') == 'unknown' else str(record['evidence_class'])
                              for record in resources if record.get('evidence_status') == 'unknown' or record.get('evidence_class') is not None)
    evidence_options = ''.join(f'<option value="{key}">{text["unknown"] if key == "unknown" else "C" + key} ({_count(evidence_counts[key])})</option>'
                               for key in ('0', '1', '2', '3', 'unknown') if evidence_counts[key])
    sort_options = ''.join(f'<option value="{value}">{text[value]}</option>' for value in ('featured', 'reviewed', 'added', 'name'))
    return (f'<div class="wrap"><div class="drawer listing" data-listing data-per-page="{PER_PAGE}" data-pages="{pages}" data-static-page="{page}" data-base="{page_path(page, language)}">'
            f'<div class="listing-side"><nav class="list-sections" aria-labelledby="sections-title"><h2 id="sections-title">{text["sections"]}</h2><p class="list-note">{text["sections_note"]}</p><ul>{navigation}</ul></nav>'
            f'<dialog class="facets" id="facets" aria-labelledby="facets-title" data-facets><div class="facets-head"><h2 id="facets-title">{text["filters"]}</h2>'
            f'<button class="link-btn" type="button" data-clear hidden>{text["clear"]}</button><button class="sheet-close" type="button" data-facets-close aria-label="{text["close"]}">{icon("close")}</button></div>'
            f'<form class="facets-form" data-facets-form>{facet("kind", text["kind"], kind_options, language)}{facet("category", text["category"], category_options, language, more_after=7)}</form>'
            f'<div class="sheet-foot"><button class="btn btn-primary" type="button" data-facets-close>{text["show"]}</button></div></dialog>'
            f'</div><div class="results"><div class="results-bar"><p class="results-meta" aria-live="polite" data-results-meta>{meta}</p>'
            f'<p class="listing-links"><a href="/api/v1/resources.json" download>{text["data"]}</a><a href="{escape(repository_url, quote=True)}/issues/new?template=resource.yml" rel="noopener">{text["suggest"]}{icon("external")}</a></p>'
            f'<button class="btn filters-btn" type="button" data-facets-open aria-controls="facets">{icon("filter")}{text["filters"]}<span class="badge" data-filter-count hidden>0</span></button>'
            f'<label class="select"><span class="select-label">{text["evidence_class"]}</span><select data-class-select aria-label="{text["evidence_class"]}"><option value="">{text["all_classes"]}</option>{evidence_options}</select>{icon("chevron")}</label>'
            f'<label class="select"><span class="select-label">{text["sort"]}</span><select data-sort aria-label="{text["sort"]}">{sort_options}</select>{icon("chevron")}</label></div>'
            f'{evidence_legend(language)}<div class="active" data-active hidden></div><ul class="cards" data-cards>{"".join(rows)}</ul>{_pager(page, pages, language)}</div></div></div>')


def in_listing_order(groups: dict[str, list[dict]], section_labels: dict[str, tuple[str, str]], page: int | None = None) -> list[dict]:
    """Every record in page order, or only the records of one static page."""
    records = [record for key in section_labels for record in in_section_order(groups.get(key, []))]
    return records if page is None else records[(page - 1) * PER_PAGE:page * PER_PAGE]


__all__ = ['PER_PAGE', 'resource_listing', 'resource_page_head', 'in_listing_order', 'in_section_order', 'listing_pages', 'page_count',
           'page_path', 'record_href', 'section_href']
