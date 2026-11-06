"""The /resources/ listing: every curated record as an index-card row, with search, filters and section links.

Sections, targets, kinds and categories all come from the catalogue's own label tables, so changing the major
categories there changes this page without touching its layout.
"""
from __future__ import annotations

from collections import Counter
from html import escape

from build_home import FEATURED, KIND_ORDER, PINNED, _folder_tabs, _ordered_targets, index_card, stored_targets
from build_readme import CATEGORIES, KIND_LABELS
from site_shell import icon

PER_PAGE = 60
TEXT = {
    'en': {
        'crumbs': 'Breadcrumb', 'home': 'Home', 'title': 'Curated reverse engineering resources', 'search_label': 'Filter resources', 'placeholder': 'Filter by name, tool or target',
        'sections': 'Filed under', 'sections_note': 'Each record is filed once. Tabs count every target it covers.', 'filters': 'Filters', 'clear': 'Clear all', 'close': 'Close filters', 'show': 'Show results', 'kind': 'Kind', 'category': 'Category',
        'show_all': 'Show all {n}', 'all': 'All <strong>{n}</strong> resources', 'results': 'Results', 'sort': 'Sort', 'featured': 'Featured', 'reviewed': 'Recently reviewed',
        'added': 'Recently added', 'name': 'Name A–Z', 'suggest': 'Suggest a resource', 'data': 'Download the data',
    },
    'zh': {
        'crumbs': '当前位置', 'home': '首页', 'title': '精选逆向工程资源', 'search_label': '筛选资源', 'placeholder': '按名称、工具或目标筛选',
        'sections': '归类', 'sections_note': '每条记录只归入一处；标签页统计它涉及的所有目标。', 'filters': '筛选', 'clear': '清除全部', 'close': '关闭筛选', 'show': '查看结果', 'kind': '类型', 'category': '类别',
        'show_all': '显示全部 {n} 项', 'all': '共 <strong>{n}</strong> 项资源', 'results': '结果', 'sort': '排序', 'featured': '精选', 'reviewed': '最近复核',
        'added': '最近新增', 'name': '名称 A–Z', 'suggest': '推荐资源', 'data': '下载数据',
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


def resource_page_head(resources: list[dict], language: str) -> str:
    text = TEXT[language]
    prefix = '/zh' if language == 'zh' else ''
    return (f'<div class="page-head wrap"><nav class="crumbs" aria-label="{text["crumbs"]}"><a href="{prefix}/">{text["home"]}</a><span aria-hidden="true">/</span><span aria-current="page">{text["title"]}</span></nav>'
            f'<div class="ph-row"><div class="ph-title"><h1>{text["title"]}</h1><span class="h-count">{_count(len(resources))}</span></div>'
            f'<form class="list-search" role="search" data-list-search><label class="vh" for="lq">{text["search_label"]}</label>{icon("search")}'
            f'<input id="lq" name="q" type="search" placeholder="{text["placeholder"]}" autocomplete="off" spellcheck="false" data-list-input><kbd class="hs-kbd">/</kbd></form></div>'
            f'{_folder_tabs(resources, language, prefix)}</div>')


def resource_listing(resources: list[dict], groups: dict[str, list[dict]], section_labels: dict[str, tuple[str, str]], language: str, repository_url: str) -> str:
    """The rows in section order. Scripts narrow them in place; without scripts the section links do the work."""
    zh = language == 'zh'
    text = TEXT[language]
    prefix = '/zh' if zh else ''
    order = stored_targets()
    sections = [(key, labels[zh]) for key, labels in section_labels.items() if groups.get(key)]
    navigation = ''.join(f'<li><a href="#heading-{key}" data-section-link data-section="{key}">{escape(label)}<span class="count">{_count(len(groups[key]))}</span></a></li>' for key, label in sections)
    rows = []
    for key, label in sections:
        rows.append(f'<li class="list-section"><h2 id="heading-{key}"><a id="{key}"></a>{escape(label)}</h2><span class="count">{_count(len(groups[key]))}</span></li>')
        rows.extend(index_card(record, language, _ordered_targets(record, order), prefix=prefix, listing=True) for record in in_section_order(groups[key]))
    kinds = Counter(record['kind'] for record in resources)
    categories = Counter(record['category'] for record in resources)
    kind_options = [(kind, KIND_LABELS[kind][zh], number) for kind, number in kinds.most_common()]
    category_options = [(key, CATEGORIES[key][zh], number) for key, number in sorted(categories.items(), key=lambda item: (-item[1], item[0]))]
    sort_options = ''.join(f'<option value="{value}">{text[value]}</option>' for value in ('featured', 'reviewed', 'added', 'name'))
    return (f'<div class="wrap"><div class="drawer listing" data-listing data-per-page="{PER_PAGE}">'
            f'<div class="listing-side"><nav class="list-sections" aria-labelledby="sections-title"><h2 id="sections-title">{text["sections"]}</h2><p class="list-note">{text["sections_note"]}</p><ul>{navigation}</ul></nav>'
            f'<dialog class="facets" id="facets" aria-labelledby="facets-title" data-facets><div class="facets-head"><h2 id="facets-title">{text["filters"]}</h2>'
            f'<button class="link-btn" type="button" data-clear hidden>{text["clear"]}</button><button class="sheet-close" type="button" data-facets-close aria-label="{text["close"]}">{icon("close")}</button></div>'
            f'<form class="facets-form" data-facets-form>{facet("kind", text["kind"], kind_options, language)}{facet("category", text["category"], category_options, language, more_after=7)}</form>'
            f'<div class="sheet-foot"><button class="btn btn-primary" type="button" data-facets-close>{text["show"]}</button></div></dialog>'
            f'</div><div class="results"><div class="results-bar"><p class="results-meta" aria-live="polite" data-results-meta>{text["all"].format(n=_count(len(resources)))}</p>'
            f'<p class="listing-links"><a href="/api/v1/resources.json" download>{text["data"]}</a><a href="{escape(repository_url, quote=True)}/issues/new?template=resource.yml" rel="noopener">{text["suggest"]}{icon("external")}</a></p>'
            f'<button class="btn filters-btn" type="button" data-facets-open aria-controls="facets">{icon("filter")}{text["filters"]}<span class="badge" data-filter-count hidden>0</span></button>'
            f'<label class="select"><span class="select-label">{text["sort"]}</span><select data-sort aria-label="{text["sort"]}">{sort_options}</select>{icon("chevron")}</label></div>'
            f'<div class="active" data-active hidden></div><ul class="cards" data-cards>{"".join(rows)}</ul><nav class="pager" aria-label="{text["results"]}" data-pager></nav></div></div></div>')


def in_listing_order(groups: dict[str, list[dict]], section_labels: dict[str, tuple[str, str]]) -> list[dict]:
    return [record for key in section_labels for record in in_section_order(groups.get(key, []))]


__all__ = ['resource_listing', 'resource_page_head', 'in_listing_order', 'in_section_order']
