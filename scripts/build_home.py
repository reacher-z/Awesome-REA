"""The homepage: masthead, search, target tabs and the index-card drawer, rendered from the curated catalog.

Every number comes from the records passed in. Scan-only discoveries are shown as their own labelled count,
never in the curated totals. The page works without JavaScript: the tabs and cards are links and the search
form opens the full listing. site.js adds search in place from the lazily loaded /search-index.json.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from html import escape
import hashlib
import json
import math
from pathlib import Path
import re
from urllib.parse import urlsplit

from asset_paths import fingerprinted_href
from build_readme import CATEGORIES, KIND_LABELS, TARGETS, collection_section, lead_sentence, paper_section, papers_newest_first
from data_classes import DATA_CLASSES
from home_art import exploded_view
from site_footer import site_footer
from repository_stats import REPOSITORY, compact_count, repository_stars
from site_shell import announcement_bar, header, head_early, icon, mobile_bar, palette, plain_language_link, shell_assets, sprite, star_button, star_count

ROOT = Path(__file__).resolve().parents[1]
# Short domain and kind codes form the call number on every card, such as BIN·TOOL.
DOMAIN_CODES = {'website': 'WEB', 'game': 'GAME', 'app': 'APP', 'binary': 'BIN', 'firmware': 'FIRM', 'protocol': 'PROTO'}
DOMAIN_ORDER = ('website', 'game', 'app', 'binary', 'firmware', 'protocol')
KIND_CODES = {'tool': 'TOOL', 'case-study': 'CASE', 'integration': 'INTEG', 'learning-resource': 'LEARN',
              'collection': 'LIST', 'documentation': 'DOCS', 'research': 'RSRCH', 'project': 'PROJ'}
KIND_ORDER = tuple(KIND_CODES)
KIND_PLURAL = {'tool': ('Tools', '工具'), 'case-study': ('Case studies', '案例'), 'integration': ('Integrations', '集成'),
               'learning-resource': ('Learning', '学习资源'), 'collection': ('Collections', '合集'),
               'documentation': ('Docs', '文档'), 'research': ('Research', '研究'), 'project': ('Projects', '项目')}
# The drawer's opening rows: flagship records across the six domains. Collections that point to individuals'
# repositories are deliberately not featured.
FEATURED = ('ghidra', 'hex-rays-ida-mcp', 'frida', 'jadx', 'chrome-devtools-mcp', 'il2cppdumper', 'binwalk',
            'mitmproxy', 'renderdoc', 'even-g2-ble-protocol-case')
DRAWER_ROWS = 7
# Records that open their section and lead the Featured order, marked Featured.
PINNED = ('websitebench',)
# The /resources/ section each target tab opens until /resources/<target>/ pages exist.
TARGET_ANCHORS = {'website': 'website', 'game': 'game', 'app': 'app', 'binary': 'native-binary', 'firmware': 'firmware', 'protocol': 'protocol'}
CONNECTIONS = {
    'official': (('Official REA', 'REA 官方'), ('official-core', 'official-skill', 'official-documentation', 'official-guide', 'official-case-study', 'upstream-maintainer-companion-list')),
    'community': (('Community REA work', 'REA 社区'), ('community-integration', 'community-learning-resource', 'community-reported-mixed-workflow')),
    'independent': (('Independent projects', '独立项目'), ('independent-agent-integration', 'independent-reconstruction')),
    'foundation': (('Foundation tools', '基础工具'), ('foundation',)),
    'learning': (('Learning', '学习资源'), ('learning',)),
}
CONNECTION_OF = {relationship: key for key, (_, relationships) in CONNECTIONS.items() for relationship in relationships}
# C0–C3 on the homepage cards; the legend on /explore/ carries the same wording.
EVIDENCE_DETAIL = {
    0: ('full software reconstruction', '完整软件复现'),
    1: ('partial scope or analysis entry', '部分范围或分析条目'),
    2: ('code & docs, no demo or download', '有代码和文档，缺演示或下载'),
    3: ('notes only', '仅笔记'),
}
# The All view's overview adds the buckets the card badges leave implicit: unreadable sources and classless papers.
OVERVIEW_EVIDENCE = {
    '0': ('C0', 'full software reconstruction', '完整软件复现', 'card-class-0'),
    '1': ('C1', 'partial scope or analysis entry', '部分范围或非复现条目', 'card-class-1'),
    '2': ('C2', 'code & docs, no demo or download', '有代码和文档，缺演示或下载', 'card-class-2'),
    '3': ('C3', 'notes only', '仅笔记或进度记录', 'card-class-3'),
    'unknown': ('?', 'source unavailable or unreadable', '来源不可达或不可读', 'card-class-unknown'),
    'unclassified': ('–', 'benchmark & dataset papers', '基准与数据集论文', 'card-class-none'),
}
OVERVIEW_ORDER = tuple(OVERVIEW_EVIDENCE)
# Short aria names for the two buckets that have no C code; the order matches OVERVIEW_EVIDENCE's.
OVERVIEW_ARIA = {'0': ('C0', 'C0'), '1': ('C1', 'C1'), '2': ('C2', 'C2'), '3': ('C3', 'C3'),
                 'unknown': ('unknown', '未知'), 'unclassified': ('benchmark papers', '基准论文')}
# Search-index rows carry the data class as this order's index, so the drawer can filter by it.
DATA_CLASS_ORDER = tuple(DATA_CLASSES)
COPY = {
    'en': {
        'h1': 'Reverse Engineering <em>Anything</em>',
        'lede': 'Awesome REA (Awesome Reverse Engineering Anything) is a bilingual catalog of {res} source-reviewed tools, projects and case studies and {pap} research papers for taking apart binaries, games, apps, firmware, protocols and websites{stars}. Every entry links the primary source it was checked against.',
        'search_label': 'Search the catalogue', 'placeholder': 'Try Ghidra, IL2CPP or BLE', 'clear': 'Clear search', 'focus': 'Press / to focus',
        'stats': '<span class="s-lg"><strong>{res}</strong> curated resources and <strong>{pap}</strong> papers, each reviewed against its source. Plus <a href="/discoveries/"><strong>{idx}</strong> unreviewed discoveries</a> from the scans.</span><span class="s-sm"><strong>{res}</strong> resources, <strong>{pap}</strong> papers, <a href="/discoveries/"><strong>{idx}</strong> unreviewed</a></span>',
        'updated': 'Last scan', 'all': 'All', 'domains': 'Target domains', 'catalogue': 'Catalogue',
        'kind': 'Kind', 'all_kinds': 'All kinds', 'sort': 'Sort', 'featured': 'Featured', 'recent': 'Recently reviewed', 'az': 'Name A–Z',
        'showing': 'Showing <strong>{n}</strong> featured of <strong>{total}</strong>', 'show_all': 'Show all {n} resources',
        'drawer_note': 'Each card links to its entry: description, requirements and the primary source it was reviewed against.',
        'reviewed': 'Reviewed', 'targets': 'Targets', 'licence': 'Original content: MIT. Linked projects keep their own licenses.',
        'class_label': 'Evidence class', 'class_unknown': 'Unknown · source unavailable',
        'all_classes': 'All classes', 'class_unknown_short': 'Unknown', 'class_info_label': 'What the evidence classes mean',
        'class_guide': 'How classes are assigned',
        'unknown_title': 'Source unavailable or unreadable at review time',
        'overview_eyebrow': 'FIG. 2 · BY TARGET DOMAIN',
        'overview_title': 'Cases by target <em>domain</em>',
        'overview_meta': '{total} entries · Last scan {scan} ·', 'overview_meta_json': 'Download JSON ↓',
        'overview_metric_entries': 'Entries',
        'overview_metric_domains': 'Domains',
        'overview_metric_strong': 'Strong evidence (C0+C1)', 'overview_strong_label': 'C0+C1',
        'overview_metric_full': 'Full reconstructions (C0)', 'overview_metric_full_note': 'manually reviewed',
        'overview_metrics_label': 'Key figures',
        'overview_h_num': '#', 'overview_h_domain': 'Domain', 'overview_h_cases': 'Cases', 'overview_h_share': 'Share',
        'overview_h_strong': 'Strong', 'overview_strong_label': 'C0+C1', 'overview_full': 'Full C0',
        'overview_all_row': 'All', 'overview_note_small': 'small sample',
        'overview_sheet_title': 'DETAIL {letter} · {name}', 'overview_sheet_cases': '{count} cases',
        'overview_sheet_sub': 'of all {share} · strong evidence {strong}%',
        'overview_levels_title': '证据等级构成',
        'overview_col_level': 'Level', 'overview_col_desc': 'Description', 'overview_col_share': 'Of the class', 'overview_col_all': 'All',
        'overview_view': 'View all {count} cases', 'overview_view_full': '★ C0 only ({count})',
        'overview_download': 'Download JSON ↓',
        'overview_whatis': 'What the evidence levels mean?',
        'overview_empty': 'No classified entries in this type yet.',
        'overview_tooltip': '{name} · {count} entries · {share}%',
        'overview_aria_unit': 'entries', 'overview_aria_unit_one': 'entry',
        'overview_label': 'Cases by target domain', 'overview_total': 'entries',
        'overview_note': 'C0 needs a manual full-reconstruction review. C1–C3 follow the public repository evidence.',
        'overview_evsel': '证据等级', 'overview_evsel_all': '全部',
        'overview_sort': 'Sort', 'overview_sort_order': 'Domain order', 'overview_sort_count': 'Count', 'overview_sort_name': 'Name A–Z',
        'overview_filtered_meta': '{codes}: {total} entries',

        'preview_image_alt': "Demo screenshot from the project's public documentation",
        'preview_video_alt': "Demo video thumbnail from the project's public documentation",
        'preview_full_label': 'Full-size demo screenshot: {name}',
        'demo_note': 'Demo available · no screenshot',
    },
    'zh': {
        'h1': '逆向<em>工程</em>',
        'lede': 'Awesome REA（Awesome Reverse Engineering Anything）是中英双语目录，收录 {res} 项经来源复核的工具、项目与案例，以及 {pap} 篇研究论文，涵盖二进制、游戏、应用、固件、协议与网站的逆向{stars}。每个条目都链接其核查所依据的一手来源。',
        'search_label': '搜索目录', 'placeholder': '试试 Ghidra、IL2CPP 或 BLE', 'clear': '清除搜索', 'focus': '按 / 键聚焦',
        'stats': '<span class="s-lg"><strong>{res}</strong> 项精选资源与 <strong>{pap}</strong> 篇论文，均已对照来源复核。另有 <a href="/zh/discoveries/"><strong>{idx}</strong> 条未审核发现</a>来自自动扫描。</span><span class="s-sm"><strong>{res}</strong> 项资源、<strong>{pap}</strong> 篇论文、<a href="/zh/discoveries/"><strong>{idx}</strong> 条未审核</a></span>',
        'updated': '最近扫描', 'all': '全部', 'domains': '目标领域', 'catalogue': '目录',
        'kind': '类型', 'all_kinds': '全部类型', 'sort': '排序', 'featured': '精选', 'recent': '最近复核', 'az': '名称 A–Z',
        'showing': '显示 <strong>{n}</strong> 条精选 / 共 <strong>{total}</strong> 条', 'show_all': '查看全部 {n} 项资源',
        'drawer_note': '每张卡片都链接到完整条目：说明、使用条件，以及复核所依据的原始来源。',
        'reviewed': '已复核', 'targets': '目标', 'licence': '原创内容采用 MIT 许可。链接项目保留各自的许可。',
        'class_label': '证据档位', 'class_unknown': '未知 · 来源不可读',
        'all_classes': '全部档位', 'class_unknown_short': '未知', 'class_info_label': '证据档位说明',
        'class_guide': '档位判定方法',
        'unknown_title': '复核时来源不可达或不可读',
        'overview_label': '数据类别与证据档位', 'overview_total': '数据点',
        'overview_note': 'C0 需人工复核完整复现。C1–C3 依据公开仓库证据。',
        'overview_eyebrow': 'FIG. 2 · BY TARGET DOMAIN',
        'overview_title': '按目标<em>领域</em>分布',
        'overview_meta': '{total} entries · Last scan {scan} ·', 'overview_meta_json': 'Download JSON ↓',
        'overview_metric_entries': 'Entries',
        'overview_metric_domains': 'Domains',
        'overview_metric_strong': 'Strong evidence (C0+C1)', 'overview_strong_label': 'C0+C1',
        'overview_metric_full': 'Full reconstructions (C0)', 'overview_metric_full_note': 'manually reviewed',
        'overview_metrics_label': 'Key figures',
        'overview_h_num': '#', 'overview_h_domain': 'Domain', 'overview_h_cases': 'Cases', 'overview_h_share': 'Share',
        'overview_h_strong': 'Strong', 'overview_strong_label': 'C0+C1', 'overview_full': 'Full C0',
        'overview_all_row': 'All', 'overview_note_small': 'small sample',
        'overview_sheet_title': 'DETAIL {letter} · {name}', 'overview_sheet_cases': '{count} cases',
        'overview_sheet_sub': 'of all {share} · strong evidence {strong}%',
        'overview_levels_title': '证据等级构成',
        'overview_col_level': 'Level', 'overview_col_desc': 'Description', 'overview_col_share': 'Of the class', 'overview_col_all': 'All',
        'overview_view': 'View all {count} cases', 'overview_view_full': '★ C0 only ({count})',
        'overview_download': 'Download JSON ↓',
        'overview_whatis': 'What the evidence levels mean?',
        'overview_empty': 'No classified entries in this type yet.',
        'overview_tooltip': '{name} · {count} entries · {share}%',
        'overview_aria_unit': 'entries', 'overview_aria_unit_one': 'entry',
        'overview_label': 'Cases by target domain', 'overview_total': 'entries',
        'overview_note': 'C0 needs a manual full-reconstruction review. C1–C3 follow the public repository evidence.',
        'overview_evsel': '证据等级', 'overview_evsel_all': '全部',
        'overview_sort': 'Sort', 'overview_sort_order': 'Domain order', 'overview_sort_count': 'Count', 'overview_sort_name': 'Name A–Z',
        'overview_filtered_meta': '{codes}: {total} entries',

        'preview_image_alt': '项目公开文档中的演示截图',
        'preview_video_alt': '项目公开文档中演示视频的封面',
        'preview_full_label': '完整演示截图：{name}',
        'demo_note': '有 demo · 暂无截图',
    },
}


def _e(value) -> str:
    return escape(str(value), quote=True)


def _count(value: int) -> str:
    return f'{value:,}'


def stored_targets() -> dict[str, list[str]]:
    """Each record's targets in their stored order; the first one names its call number. catalog.json sorts them."""
    order = {}
    for filename in ('rea-resources.json', 'tool-resources.json'):
        for record in json.loads((ROOT / 'data' / filename).read_text(encoding='utf-8')):
            if record.get('targets'):
                order[record['id']] = list(record['targets'])
    return order


def _ordered_targets(record: dict, order: dict[str, list[str]]) -> list[str]:
    stored = [target for target in order.get(record['id'], []) if target in record['targets']]
    return stored + [target for target in record['targets'] if target not in stored]


def evidence_label(url: str) -> dict:
    """owner/repo and the pinned commit from a GitHub or GitLab file link; host and path for anything else."""
    parts = urlsplit(url)
    segments = [segment for segment in parts.path.split('/') if segment]
    if parts.netloc in ('github.com', 'gitlab.com') and len(segments) >= 4 and segments[2] in ('blob', 'tree', '-'):
        if segments[2] == '-':
            segments = segments[:2] + segments[3:]
        revision = segments[3] if len(segments) > 3 else ''
        return {'repo': f'{segments[0]}/{segments[1]}', 'sha': revision[:7] if re.fullmatch(r'[0-9a-f]{7,40}', revision) else '', 'host': parts.netloc}
    if parts.netloc == 'github.com' and len(segments) >= 2:
        return {'repo': f'{segments[0]}/{segments[1]}', 'sha': '', 'host': parts.netloc}
    host = parts.netloc.removeprefix('www.')
    path = parts.path.rstrip('/')
    return {'repo': host + (path if len(path) < 40 else path[:38] + '…'), 'sha': '', 'host': host}


def _lead(record: dict, language: str) -> str:
    return lead_sentence(record[f'description_{language}'], language)


def _name(record: dict, language: str) -> str:
    return record.get('name_zh') or record['name'] if language == 'zh' else record['name']


def _target_label(target: str, language: str) -> str:
    return TARGETS[target][language == 'zh']


def evidence_chip(record: dict, language: str) -> str:
    """The C0–C3 badge carried by the catalogue cards; site.js renders the same one from the search index."""
    text = COPY[language]
    if record.get('evidence_status') == 'unknown':
        return f'<span class="card-class card-class-unknown" title="{_e(text["unknown_title"])}">?</span>'
    value = record.get('evidence_class')
    if value is None:
        return ''
    detail = EVIDENCE_DETAIL[int(value)][language == 'zh']
    return f'<span class="card-class card-class-{int(value)}" title="{_e(text["class_label"])} {int(value)} · {_e(detail)}">C{int(value)}</span>'


def evidence_guide_url(language: str, repository_url: str = 'https://github.com/reacher-z/Awesome-REA') -> str:
    return f'{repository_url}/blob/main/docs/evidence-classes{".zh-CN" if language == "zh" else ""}.md'


def evidence_legend(language: str) -> str:
    text = COPY[language]
    items = ''.join(f'<li><span class="card-class card-class-{value}">C{value}</span>{_e(details[language == "zh"])}</li>'
                    for value, details in EVIDENCE_DETAIL.items())
    items += f'<li><span class="card-class card-class-unknown">?</span>{_e(text["unknown_title"])}</li>'
    guide = f'<a class="evidence-guide" href="{_e(evidence_guide_url(language))}" rel="noopener">{text["class_guide"]}{icon("external")}</a>'
    return f'<div class="evidence-legend"><strong>{text["class_label"]}</strong><ul>{items}</ul>{guide}</div>'


def evidence_bucket(record: dict) -> str:
    """The overview's evidence bucket for a data point: C0–C3, unreadable, or a classless paper record."""
    if record.get('evidence_status') == 'unknown':
        return 'unknown'
    value = record.get('evidence_class')
    return 'unclassified' if value is None else str(int(value))


def _shares(values, keys) -> dict[str, str]:
    """Percentages of the group's total, one decimal, largest-remainder so the labels sum to 100.0.

    The remainders stay integers (count × 1000 mod total), so ties resolve by the given order.
    A count that rounds to zero shows '<0.1' instead of 0; a true zero shows '0'.
    """
    total = sum(values.get(key, 0) for key in keys)
    if not total:
        return {key: '0' for key in keys}
    floors = {key: values.get(key, 0) * 1000 // total for key in keys}
    short = 1000 - sum(floors.values())
    for key in sorted(keys, key=lambda k: values.get(k, 0) * 1000 % total, reverse=True)[:short]:
        floors[key] += 1
    return {key: f'{floors[key] / 10:.1f}' if floors[key] else ('<0.1' if values.get(key, 0) else '0') for key in keys}


def _ov_aria(label: str, count: int, share: str, strong: str, language: str) -> str:
    """The spoken sentence for one row: total, share and strong-evidence rate."""
    zh = language == 'zh'
    unit = COPY[language]['overview_aria_unit_one' if count == 1 else 'overview_aria_unit']
    return (f'{label}{"，" if zh else ", "}{_count(count)} {unit}{"，" if zh else ", "}{"占 " if zh else ""}{share}%'
            f'{"，" if zh else ", "}{"强证据 " if zh else "strong evidence "}{strong}%')


def _overview_metrics(text: dict, classified: int, domains: int, strong_share: str, strong_count: int,
                      full_count: int) -> str:
    """The four-figure strip: entries, domains, strong evidence and full reconstructions."""
    return (f'<dl class="ov-metrics" aria-label="{_e(text["overview_metrics_label"])}">'
            f'<div class="ov-metric"><dt>{_e(text["overview_metric_entries"])}</dt>'
            f'<dd class="ov-metric-num"><span data-ov-metric="entries">{_count(classified)}</span></dd></div>'
            f'<div class="ov-metric"><dt>{_e(text["overview_metric_domains"])}</dt>'
            f'<dd class="ov-metric-num"><span data-ov-metric="domains">{_count(domains)}</span></dd></div>'
            f'<div class="ov-metric"><dt>{_e(text["overview_metric_strong"])}</dt>'
            f'<dd class="ov-metric-num"><span data-ov-metric="strong">{_e(strong_share)}</span>%</dd>'
            f'<dd class="ov-metric-note"><span data-ov-metric="strong-note">{_count(strong_count)}</span>'
            f' {_e(text["overview_strong_label"])}</dd></div>'
            f'<div class="ov-metric"><dt>{_e(text["overview_metric_full"])}</dt>'
            f'<dd class="ov-metric-num"><span class="ov-star" aria-hidden="true">★</span>'
            f'<span data-ov-metric="full">{_count(full_count)}</span></dd>'
            f'<dd class="ov-metric-note">{_e(text["overview_metric_full_note"])}</dd></div></dl>')


def _overview_table(ordered: list, totals: dict, mixes: dict, letters: dict, shares: dict,
                    strong_rate: dict, strong_all: str, classified: int, language: str) -> str:
    """The bar chart as a real table: #, domain, the track, cases, share and the strong column.

    The track is a hairline the bar grows from; ticks mark the quarters and the vertical grid
    lines run through every row so the eye can align them.
    """
    text = COPY[language]
    rows = []
    for class_key in ordered:
        letter = letters[class_key]
        count = totals[class_key]
        c0_count = mixes[class_key]['0']
        rate = strong_rate[class_key]
        small = count < 30
        tag = f'<span class="ov-tag">{_e(text["overview_note_small"])}</span>' if small else ''
        star = f'<span class="ov-star" aria-hidden="true">★</span> {_count(c0_count)}' if c0_count else '<span class="ov-zero-mark">0</span>'
        dim = ' ovl-zero' if not count else ''
        rows.append(
            f'<tr class="ov-row{dim}" data-ov-row="{_e(class_key)}" data-total="{count}" '
            f'data-levels="{";".join(f"{b}:{mixes[class_key][b]}" for b in OVERVIEW_ORDER)}">'
            f'<td class="ov-cell-letter"><button type="button" class="ov-letterbtn" aria-pressed="false" '
            f'aria-label="{_e(_ov_aria(DATA_CLASSES[class_key][1 if language == "zh" else 0], count, shares[class_key], rate, language))}" '
            f'data-ov-select="{_e(class_key)}"><span class="ov-letter">{letter}</span></button></td>'
            f'<td class="ov-cell-class"><span class="ov-name">{_e(DATA_CLASSES[class_key][0])}</span>'
            f'<span class="ov-name-zh">{_e(DATA_CLASSES[class_key][1])}</span></td>'
            f'<td class="ov-cell-track"><span class="ov-track" aria-hidden="true"><span class="ov-fill" '
            f'data-w="{count / max(totals.values()) * 100:.2f}"></span></span></td>'
            f'<td class="ov-cell-count" data-ov-count>{_count(count)}</td>'
            f'<td class="ov-cell-share" data-ov-share>{shares[class_key]}%</td>'
            f'<td class="ov-cell-strong{" ov-letter-dim" if small else ""}" data-ov-strong-cell>'
            f'<span class="ov-strong-label">{_e(text["overview_strong_label"])}</span> '
            f'<span class="ov-strong-pct" data-ov-strong>{rate}%</span> <span class="ov-c0" data-ov-c0>{star}</span>{tag}</td></tr>')
    full_total = sum(mixes[class_key]['0'] for class_key in ordered)
    return (f'<table class="ov-spec"><thead><tr>'
            f'<th scope="col"><span class="ov-h">{_e(text["overview_h_num"])}</span></th>'
            f'<th scope="col"><span class="ov-h">{_e(text["overview_h_domain"])}</span></th>'
            f'<th scope="col" class="ov-h-track"><span class="ov-ticks" aria-hidden="true"></span>'
            f'<span class="ov-h">{_e(text["overview_h_domain"] and "")}</span></th>'
            f'<th scope="col"><span class="ov-h">{_e(text["overview_h_cases"])}</span></th>'
            f'<th scope="col"><span class="ov-h">{_e(text["overview_h_share"])}</span></th>'
            f'<th scope="col"><span class="ov-h">{_e(text["overview_h_strong"])}</span></th>'
            f'</tr></thead><tbody>{"".join(rows)}'
            f'<tr class="ov-spec-all"><td class="ov-cell-letter">—</td>'
            f'<td class="ov-cell-class">{_e(text["overview_all_row"])}</td><td class="ov-cell-track"></td>'
            f'<td class="ov-cell-count">{_count(classified)}</td><td class="ov-cell-share">100%</td>'
            f'<td class="ov-cell-strong"><span class="ov-strong-label">{_e(text["overview_strong_label"])}</span> '
            f'<span class="ov-strong-pct">{strong_all}%</span> '
            f'<span class="ov-star" aria-hidden="true">★</span> {_count(full_total)}</td></tr></tbody></table>')


def _overview_sheet(ordered: list, totals: dict, mixes: dict, letters: dict, shares: dict,
                    strong_rate: dict, all_levels: Counter, classified: int, kinds_by_class: dict,
                    prefix: str, language: str, selected: str) -> str:
    """The right-column parts list for the selected class: one panel per class, selected visible."""
    text, zh = COPY[language], language == 'zh'
    panels = []
    for class_key in ordered:
        letter = letters[class_key]
        count = totals[class_key]
        own = _shares(dict(mixes[class_key]), OVERVIEW_ORDER)
        rows = []
        for bucket in OVERVIEW_ORDER:
            n = mixes[class_key][bucket]
            overall = all_levels[bucket] / classified * 100
            zero = '' if n else ' ovl-zero'
            rows.append(f'<li class="ovl-row{zero}">'
                        f'<span class="ovd-dot ovl-dot-{bucket}" aria-hidden="true"></span>'
                        f'<span class="ovl-code">{OVERVIEW_EVIDENCE[bucket][0]}</span>'
                        f'<span class="ovl-label">{_e(OVERVIEW_EVIDENCE[bucket][2 if zh else 1])}</span>'
                        f'<span class="ovl-leader" aria-hidden="true"></span>'
                        f'<span class="ovl-count">{_count(n)}</span>'
                        f'<span class="ovl-own">{own[bucket]}%</span>'
                        f'<span class="ovl-all">{overall:.1f}%</span></li>')
        kinds = ','.join(sorted(kinds_by_class[class_key])) or 'case-study'
        c0 = mixes[class_key]['0']
        full_button = (f'<button type="button" class="ov-c0btn" data-ov-c0only>'
                       f'{_e(text["overview_view_full"].format(count=_count(c0)))} →</button>' if c0 else '')
        panels.append(
            f'<div class="ov-sheet-panel" data-ov-panel="{_e(class_key)}" data-letter="{letter}"'
            f'{" hidden" if class_key != selected else ""}>'
            f'<p class="ovl-eyebrow">{_e(text["overview_sheet_title"].format(letter=letter, name=DATA_CLASSES[class_key][0].upper()))}</p>'
            f'<p class="ovl-cases"><span class="ovl-cases-num">{_count(count)}</span> {_e(text["overview_aria_unit"])}</p>'
            f'<p class="ovl-sub">{_e(text["overview_sheet_sub"].format(share=shares[class_key], strong=strong_rate[class_key]))}</p>'
            f'<p class="ovl-title">{_e(text["overview_levels_title"])}</p>'
            f'<div class="ovl-cols" aria-hidden="true"><span>{_e(text["overview_col_level"])}</span>'
            f'<span>{_e(text["overview_col_desc"])}</span><span></span>'
            f'<span>{_e(text["overview_h_cases"])}</span><span>{_e(text["overview_col_share"])}</span>'
            f'<span>{_e(text["overview_col_all"])}</span></div>'
            f'<ul class="ovl-list">{"".join(rows)}</ul>'
            f'<div class="ovl-actions"><a class="ov-viewbtn" data-ov-view-all="{_e(class_key)}" '
            f'href="{_e(f"{prefix}/resources/?kind={kinds}")}">{_e(text["overview_view"].format(count=_count(count)))} →</a>'
            f'{full_button}'
            f'<a class="ovl-download" href="/downloads/resources.json">{_e(text["overview_download"])}</a></div></div>')
    return (f'<div class="ov-sheet" data-ov-sheet aria-live="polite" '
            f'data-all-levels="{";".join(f"{b}:{all_levels[b]}" for b in OVERVIEW_ORDER)}">{"".join(panels)}</div>')


def _overview_body(key: str, records: list[dict], total_entries: int, language: str, prefix: str,
                   scan_date: str, *, active: bool) -> str:
    """One content type's sheet: fixed title, metrics, the bar table and the detail column."""
    text, zh = COPY[language], language == 'zh'
    totals, mixes = Counter(), defaultdict(Counter)
    kinds_by_class = defaultdict(set)
    for record in records:
        data_class = record.get('class')
        if not data_class:
            continue
        totals[data_class] += 1
        mixes[data_class][evidence_bucket(record)] += 1
        if record.get('kind') and record.get('category'):
            kinds_by_class[data_class].add(record['kind'])
    if not totals:
        return (f'<div class="ov-body" data-ov-body="{_e(key)}" data-ov-empty role="tabpanel" '
                f'aria-labelledby="ov-tab-{_e(key) or "all"}"{" hidden" if not active else ""}>'
                f'<p class="ov-empty">{_e(text["overview_empty"])}</p></div>')
    # The display order follows the data's own class order; sorting is a user choice, not a judgement.
    ordered = [class_key for class_key in DATA_CLASSES if class_key in totals]
    classified = sum(totals.values())
    shares = _shares(totals, ordered)
    all_levels = Counter()
    for class_key in ordered:
        all_levels.update(mixes[class_key])
    strong_counts = {class_key: mixes[class_key]['0'] + mixes[class_key]['1'] for class_key in ordered}
    # Strong evidence is a per-class rate, not a share of the strong pool.
    strong_rate = {class_key: f'{strong_counts[class_key] / totals[class_key] * 100:.1f}' for class_key in ordered}
    strong_total = sum(strong_counts.values())
    strong_all = f'{strong_total / classified * 100:.1f}'
    full_total = all_levels['0']
    letters = {class_key: letter for class_key, letter in zip(ordered, 'ABCDEFG')}
    max_count = max(totals[class_key] for class_key in ordered)
    title = text['overview_title']
    meta_line = text['overview_meta'].format(total=_count(classified), scan=scan_date or '—')
    payload = json.dumps({'classified': classified, 'totalEntries': total_entries, 'kind': key,
                          'classes': [{'key': class_key, 'letter': letters[class_key], 'total': totals[class_key],
                                       'name': DATA_CLASSES[class_key][0], 'nameZh': DATA_CLASSES[class_key][1],
                                       'levels': {bucket: mixes[class_key][bucket] for bucket in OVERVIEW_ORDER}}
                                      for class_key in ordered]},
                         ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    return (f'<div class="ov-body" data-ov-body="{_e(key)}" role="tabpanel" '
            f'aria-labelledby="ov-tab-{_e(key) or "all"}"{" hidden" if not active else ""}>'
            f'<header class="ov-head"><p class="ov-eyebrow" data-ov-eyebrow>FIG. 2 · {_e(text["overview_eyebrow"].split("·")[1].strip().upper() if not zh else text["overview_eyebrow"].split("·")[1].strip())}</p>'
            f'<p class="ov-title" data-ov-title>{title}</p>'
            f'<p class="ov-meta"><span data-ov-meta>{_e(meta_line)}</span> '
            f'<a class="ov-meta-json" href="/downloads/resources.json">{_e(text["overview_meta_json"])}</a></p></header>'
            f'{_overview_metrics(text, classified, len(ordered), strong_all, strong_total, full_total)}'
            f'<div class="ov-figure-row">{_overview_table(ordered, totals, mixes, letters, shares, strong_rate, strong_all, classified, language)}'
            f'{_overview_sheet(ordered, totals, mixes, letters, shares, strong_rate, all_levels, classified, kinds_by_class, prefix, language, ordered[0])}</div>'
            f'<script type="application/json" data-ov-data>{payload}</script></div>')


def _overview(resources: list[dict], papers: list[dict], language: str, prefix: str = '',
              last_scan: str | None = None) -> str:
    """The All view's opening sheet: FIG. 2, class bars drawn to scale with a parts-list detail.

    Every bar maps linearly to its class's count against the largest; the level filter and the
    sort re-aggregate the table in place. site.js draws the sheet in and keeps the ring—there is
    no ring—honest; without scripts the section stays hidden and the featured cards show.
    """
    text, zh = COPY[language], language == 'zh'
    records = list(resources) + [paper for paper in papers if 'class' in paper]
    if not any(record.get('class') for record in records):
        return ''
    kinds = Counter(record['kind'] for record in resources)
    present = [kind for kind in KIND_ORDER if kinds[kind]]
    scan_date = (last_scan or '')[:10]
    tabs = [f'<button type="button" class="ov-tab" role="tab" id="ov-tab-all" data-ov-tab="" '
            f'aria-selected="true" tabindex="0">{_e(text["all"])}<span class="ov-tab-count">{_count(len(resources))}</span></button>']
    tabs += [f'<button type="button" class="ov-tab" role="tab" id="ov-tab-{_e(kind)}" data-ov-tab="{_e(kind)}" '
             f'aria-selected="false" tabindex="-1">{_e(KIND_PLURAL[kind][zh])}'
             f'<span class="ov-tab-count">{_count(kinds[kind])}</span></button>' for kind in present]
    bodies = [_overview_body('', records, kinds.get('case-study', 0), language, prefix, scan_date, active=True)]
    bodies += [_overview_body(kind, [record for record in resources if record['kind'] == kind], kinds[kind],
                              language, prefix, scan_date, active=False) for kind in present]
    info_rows = ''.join(f'<li><span class="ovd-dot ovl-dot-{bucket}" aria-hidden="true"></span>'
                        f'<span class="ovl-code">{OVERVIEW_EVIDENCE[bucket][0]}</span>'
                        f'{_e(OVERVIEW_EVIDENCE[bucket][2 if zh else 1])}</li>' for bucket in OVERVIEW_ORDER)
    info = (f'<span class="info-wrap"><button type="button" class="info-btn" aria-expanded="false" '
            f'aria-controls="ov-class-info" data-ov-info aria-label="{text["class_info_label"]}">i</button>'
            f'<span class="info-pop" id="ov-class-info" role="tooltip" hidden><strong>{_e(text["class_label"])}</strong>'
            f'<ul>{info_rows}</ul><span class="info-note">{_e(text["overview_note"])}</span></span></span>')
    level_boxes = ''.join(f'<label class="ov-evopt"><input type="checkbox" value="{bucket}">'
                          f'<span class="ovd-dot ovl-dot-{bucket}" aria-hidden="true"></span>'
                          f'<span class="ovl-code">{OVERVIEW_EVIDENCE[bucket][0]}</span>'
                          f'{_e(OVERVIEW_EVIDENCE[bucket][2 if zh else 1])}</label>' for bucket in OVERVIEW_ORDER)
    evsel = (f'<span class="ov-evsel"><button type="button" class="ov-evbtn" aria-expanded="false" '
             f'aria-haspopup="true" aria-controls="ov-evlist">{_e(text["overview_evsel"])}{"：" if zh else ":"}'
             f'<span data-ov-evlabel>{_e(text["overview_evsel_all"])}</span></button>'
             f'<span class="ov-evpop" id="ov-evlist" hidden>{level_boxes}</span></span>')
    sort_select = (f'<label class="select ov-sort"><span class="vh">{_e(text["overview_sort"])}</span>'
                   f'<select data-ov-sort aria-label="{_e(text["overview_sort"])}">'
                   f'<option value="order">{_e(text["overview_sort_order"])}</option>'
                   f'<option value="count">{_e(text["overview_sort_count"])}</option>'
                   f'<option value="name">{_e(text["overview_sort_name"])}</option></select>{icon("chevron")}</label>')
    return (f'<section class="overview" data-overview hidden aria-label="{_e(text["overview_label"])}">'
            f'<span class="ov-cross ov-cross-tl" aria-hidden="true"></span><span class="ov-cross ov-cross-tr" aria-hidden="true"></span>'
            f'<span class="ov-cross ov-cross-bl" aria-hidden="true"></span><span class="ov-cross ov-cross-br" aria-hidden="true"></span>'
            f'<div class="ov-filterbar"><div class="ov-segments" role="tablist" aria-label="{_e(text["kind"])}">{"".join(tabs)}</div>'
            f'<div class="ov-tools">{evsel}{sort_select}{info}</div></div>'
            f'{"".join(bodies)}'
            f'<details class="ov-what" id="ov-what"><summary>{_e(text["overview_whatis"])}</summary>'
            f'<ul>{info_rows}</ul><p class="info-note">{_e(text["overview_note"])}</p></details>'
            f'<p class="ov-corner" aria-hidden="true">FIG. 2 · SCALE 1:1<br>'
            f'REV {scan_date or "—"} · N = {_count(sum(1 for record in records if record.get("class")))}</p>'
            f'</section>')


def preview_figure(record: dict, language: str, *, thumb: bool = False) -> str:
    """A documented demo preview for Class 0/1 entries; a demo without a screenshot gets a placeholder."""
    text = COPY[language]
    if record.get('preview'):
        kind = record.get('preview_kind')
        alt = text['preview_video_alt'] if kind == 'video' else text['preview_image_alt']
        play = '<span class="card-preview-play" aria-hidden="true">▶</span>' if kind == 'video' else ''
        # A /resources/ row shows the small thumbnail when there is one; a screenshot thumbnail links the full image.
        small = record.get('preview_thumb') if thumb else None
        image = f'<img src="{_e(small or record["preview"])}" alt="{_e(alt)}" loading="lazy" decoding="async">'
        if small and kind != 'video':
            name = (record.get('name_zh') or record['name']) if language == 'zh' else record['name']
            label = text['preview_full_label'].format(name=name)
            image = f'<a class="card-preview-link" href="{_e(record["preview"])}" aria-label="{_e(label)}">{image}</a>'
        return f'<figure class="card-preview">{play}{image}</figure>'
    if record.get('preview_kind') == 'demo':
        return (f'<figure class="card-preview card-preview-demo"><span class="card-preview-play" aria-hidden="true">▶</span>'
                f'<span>{_e(text["demo_note"])}</span></figure>')
    return ''


def index_card(record: dict, language: str, targets: list[str], *, prefix: str = '', listing: bool = False) -> str:
    """One catalogue row. site.js renders the same markup in cardHTML() for search results.

    Rows on /resources/ also carry the record's bare ID, the anchor older links into that page use.
    """
    text = COPY[language]
    identifier = _e(record['id'])
    kind = record['kind']
    label = f"{_target_label(targets[0], language)} · {KIND_LABELS[kind][language == 'zh']}"
    case = ' is-case' if kind == 'case-study' else ''
    evidence = evidence_label(record['evidence_url'])
    revision = f'<span class="sha">@{_e(evidence["sha"])}</span>' if evidence['sha'] else ''
    reviewed = str(record['verified_at'])[:10]
    items = ''.join(f'<li>{icon(target)}{_e(_target_label(target, language))}</li>' for target in targets[:3])
    if len(targets) > 3:
        items += f'<li class="more">+{len(targets) - 3}</li>'
    article = f' id="{identifier}" data-record-id="{identifier}" data-resource-id="{identifier}"' if listing else ''
    entry = f' entry-detail-link" data-entry-link="{identifier}' if listing else ''
    mark = f'<span class="row-mark">{text["featured"]}</span>' if record['id'] in PINNED else ''
    return (f'<li class="card{case}" id="r-{identifier}" data-id="{identifier}"><article class="card-face"{article}>'
            f'<p class="callno" title="{_e(label)}"><span class="vh">{_e(label)}: </span><span aria-hidden="true">{DOMAIN_CODES[targets[0]]}·{KIND_CODES[kind]}</span></p>'
            f'<h3 class="card-name"><a class="stretch{entry}" href="{prefix}/resources/{identifier}/">{_e(_name(record, language))}</a>{mark}{evidence_chip(record, language)}</h3>'
            f'<p class="card-desc">{_e(_lead(record, language))}</p>{preview_figure(record, language, thumb=listing)}'
            f'<ul class="card-targets" aria-label="{text["targets"]}">{items}</ul>'
            f'<p class="stamp">{icon("check")}<span>{text["reviewed"]} <time datetime="{reviewed}">{reviewed}</time></span>'
            f'<a class="ev" href="{_e(record["evidence_url"])}" rel="noopener"><span class="ev-repo">{_e(evidence["repo"])}</span>{revision}</a></p>'
            f'</article></li>')


def _folder_tabs(resources: list[dict], language: str, prefix: str) -> str:
    text = COPY[language]
    counts = Counter(target for record in resources for target in record['targets'])
    tabs = [f'<a class="folder" href="{prefix}/resources/" data-target="all" aria-current="true">{text["all"]} <span class="count">{_count(len(resources))}</span></a>']
    for target in [target for target in DOMAIN_ORDER if counts[target]] + sorted(set(counts) - set(DOMAIN_ORDER)):
        tabs.append(f'<a class="folder" href="{prefix}/resources/#{TARGET_ANCHORS.get(target, "catalog")}" data-target="{target}">{icon(target)}{_e(_target_label(target, language))} '
                    f'<span class="count">{_count(counts[target])}</span></a>')
    return f'<nav class="folders" aria-label="{text["domains"]}">{"".join(tabs)}</nav>'


def _stars_clause(language: str) -> str:
    """The repository's GitHub stars, rounded like the buttons; empty when the build has no count."""
    stars = repository_stars()
    if stars is None:
        return ''
    count = compact_count(stars)
    return f'，GitHub 星标 {count}' if language == 'zh' else f', with {count} GitHub stars'


OLD_TITLES = {'en': ('Awesome Reverse Engineering Anything · Tools, Cases &amp; Papers', 'Awesome Reverse Engineering Anything · Tools, Cases & Papers'),
              'zh': ('逆向工程资源合集 · Awesome Reverse Engineering Anything',)}


def home_title(resources: list[dict], papers: list[dict], language: str) -> str:
    """The homepage title: the brand, then the real counts (at most 60 characters)."""
    res, pap = _count(len(resources)), _count(len(papers))
    return (f'逆向工程资源大全：{res} 项工具、案例与论文' if language == 'zh'
            else f'Awesome Reverse Engineering: {res} Tools, Cases & Papers')


def _masthead(resources, papers, discovery_count, last_scan, language, prefix, repository_url) -> str:
    text = COPY[language]
    stats = text['stats'].format(res=_count(len(resources)), pap=_count(len(papers)), idx=_count(discovery_count))
    updated = (f'<p class="updated">{text["updated"]} <time datetime="{_e(last_scan)}" data-rel>{_e(last_scan[:10])}</time></p>' if last_scan else '')
    return (f'<section class="masthead" aria-labelledby="hero-title"><div class="wrap">'
            f'{icon("reg", "reg reg-tl")}{icon("reg", "reg reg-tr")}<div class="xv">{exploded_view(language)}</div>'
            f'<div class="hero-top"><h1 class="hero-title" id="hero-title"><span class="hero-brand">Awesome REA</span> {text["h1"]}</h1><p class="lede">{text["lede"].format(res=_count(len(resources)), pap=_count(len(papers)), stars=_stars_clause(language))}</p></div>'
            f'<form class="hero-search" role="search" action="{prefix}/resources/" method="get" data-home-search>'
            f'<label class="hs-label" for="q">{text["search_label"]}</label>{icon("search")}'
            f'<input id="q" name="q" type="search" placeholder="{text["placeholder"]}" autocomplete="off" autocapitalize="off" spellcheck="false" enterkeyhint="search" aria-describedby="hs-count" data-search-input>'
            f'<span class="hs-side"><span class="hs-count" id="hs-count" aria-live="polite" data-search-count></span>'
            f'<button class="hs-clear" type="button" aria-label="{text["clear"]}" data-search-clear>{icon("close")}</button>'
            f'<kbd class="hs-kbd" title="{text["focus"]}">/</kbd></span></form>'
            f'<div class="hero-meta">{star_button(language, repository_url, "hero-star")}<div class="hero-stats"><p>{stats}</p>{updated}</div></div>{_folder_tabs(resources, language, prefix)}'
            f'</div></section>')


def _drawer(resources, papers, order, language, prefix, last_scan=None) -> str:
    text = COPY[language]
    by_id = {record['id']: record for record in resources}
    featured = [by_id[identifier] for identifier in FEATURED if identifier in by_id][:DRAWER_ROWS]
    kinds = Counter(record['kind'] for record in resources)
    present = [kind for kind in KIND_ORDER if kinds[kind]]
    zh = language == 'zh'
    chips = ''.join(f'<button class="chip" type="button" data-kind="{kind}" aria-pressed="false">{icon("check")}{KIND_PLURAL[kind][zh]} <span class="count">{_count(kinds[kind])}</span></button>' for kind in present)
    options = ''.join(f'<option value="{kind}">{KIND_PLURAL[kind][zh]} ({_count(kinds[kind])})</option>' for kind in present)
    classes = Counter()
    for record in resources:
        if record.get('evidence_status') == 'unknown':
            classes['unknown'] += 1
        elif record.get('evidence_class') is not None:
            classes[str(int(record['evidence_class']))] += 1
    class_names = {str(value): f'C{value}' for value in range(4)} | {'unknown': text['class_unknown_short']}
    class_options = ''.join(f'<option value="{key}">{class_names[key]} ({_count(classes[key])})</option>'
                            for key in ('0', '1', '2', '3', 'unknown') if classes[key])
    class_rows = ''.join(f'<li><span class="card-class card-class-{value}">C{value}</span>{_e(EVIDENCE_DETAIL[value][zh])}</li>'
                         for value in sorted(EVIDENCE_DETAIL))
    class_info = (f'<span class="info-wrap"><button type="button" class="info-btn" aria-expanded="false" aria-controls="class-info" '
                  f'aria-label="{text["class_info_label"]}">i</button><span class="info-pop" id="class-info" role="tooltip">'
                  f'<strong>{text["class_label"]}</strong><ul>{class_rows}'
                  f'<li><span class="card-class card-class-unknown">?</span>{_e(text["unknown_title"])}</li></ul></span></span>')
    cards = ''.join(index_card(record, language, _ordered_targets(record, order), prefix=prefix) for record in featured)
    total = len(resources)
    return (f'<section class="wrap drawer-wrap" id="catalog" aria-labelledby="catalogue-title"><div class="drawer" id="catalogue" data-drawer>'
            f'<h2 class="vh" id="catalogue-title">{text["catalogue"]}</h2><div class="drawer-bar">'
            f'<div class="chips" role="group" aria-label="{text["kind"]}" data-kind-chips>{chips}</div>'
            f'<label class="select kind-select"><span class="vh">{text["kind"]}</span><select data-kind-select aria-label="{text["kind"]}"><option value="">{text["all_kinds"]}</option>{options}</select>{icon("chevron")}</label>'
            f'<span class="class-filter"><label class="select"><span class="select-label">{text["class_label"]}</span>'
            f'<select data-class-select aria-label="{text["class_label"]}"><option value="">{text["all_classes"]}</option>{class_options}</select>{icon("chevron")}</label>{class_info}</span>'
            f'<label class="select"><span class="select-label">{text["sort"]}</span><select data-sort aria-label="{text["sort"]}">'
            f'<option value="featured">{text["featured"]}</option><option value="reviewed">{text["recent"]}</option><option value="name">{text["az"]}</option></select>{icon("chevron")}</label>'
            f'<p class="drawer-meta" data-drawer-meta aria-live="polite">{text["showing"].format(n=len(featured), total=_count(total))}</p></div>'
            f'{_overview(resources, papers, language, prefix=prefix, last_scan=last_scan)}'
            f'<ul class="cards" data-cards>{cards}</ul><div class="drawer-foot">'
            f'<a class="btn btn-primary" href="{prefix}/resources/" data-show-all>{text["show_all"].format(n=_count(total))}{icon("arrow")}</a>'
            f'<p class="note">{text["drawer_note"]}</p></div></div></section>')


# The featured projects, WebsiteBench first. They carry no review stamp until they have catalog records.
FEATURED_PROJECTS = (
    {'name': 'WebsiteBench', 'repository': 'TIGER-AI-Lab/WebsiteBench', 'project': 'https://website-bench.com/',
     'leaderboard': 'https://website-bench.com/#results',
     'en': ('Can AI agents rebuild websites through browser exploration?',
            'Given a production-level website they can explore through a browser, agents must reverse-engineer a full-stack version that matches its appearance and behavior as closely as possible.'),
     'zh': ('AI 智能体能否通过浏览器探索重建网站？',
            '给定一个可通过浏览器探索的生产级网站，智能体需要逆向出一个全栈版本，在外观和行为上尽可能与原站一致。')},
    {'name': 'ClawBench', 'repository': 'TIGER-AI-Lab/ClawBench', 'project': 'https://claw-bench.com',
     'leaderboard': 'https://huggingface.co/spaces/TIGER-Lab/ClawBench',
     'en': ('Can AI agents complete everyday online tasks?', 'An open-source benchmark for browser AI agents on daily tasks.'),
     'zh': ('AI 智能体能否完成日常在线任务？', '面向浏览器 AI 智能体日常任务的开源基准。')},
    {'name': 'Awesome CUA', 'repository': 'reacher-z/Awesome-CUA', 'project': 'https://awesomecua.com/',
     'en': ('The sister catalogue for computer-use agents.', 'Computer-use research, data and tools, reviewed.'),
     'zh': ('计算机使用智能体的姊妹目录。', '经审核的计算机使用研究、数据与工具。')},
)
FEATURED_TEXT = {
    'en': {'label': 'Featured', 'star': 'Star {name}', 'leaderboard': 'Leaderboard', 'project': 'Project page'},
    'zh': {'label': '精选', 'star': '为 {name} 加星', 'leaderboard': '排行榜', 'project': '项目主页'},
}


def _featured_projects(language: str) -> str:
    text = FEATURED_TEXT[language]
    cards = []
    for position, project in enumerate(FEATURED_PROJECTS):
        question, detail = project[language]
        leaderboard = f'<a class="btn" href="{project["leaderboard"]}" rel="noopener">{text["leaderboard"]}</a>' if project.get('leaderboard') else ''
        count = star_count(project['repository'], 'btn-count')
        cards.append(f'<article class="promo-card{" promo-lead" if position == 0 else ""}">'
                     f'<h3 class="promo-name">{project["name"]}</h3><p class="promo-question">{_e(question)}</p><p class="promo-detail">{_e(detail)}</p>'
                     f'<p class="promo-actions"><a class="btn btn-primary" href="https://github.com/{project["repository"]}" rel="noopener">{icon("star")}{text["star"].format(name=project["name"])}{count}</a>'
                     f'{leaderboard}<a class="btn" href="{project["project"]}" rel="noopener">{text["project"]}</a></p></article>')
    return (f'<section class="wrap promo" aria-labelledby="promo-title"><div class="promo-head"><h2 class="promo-label" id="promo-title">{text["label"]}</h2>'
            f'</div><div class="promo-grid">{"".join(cards)}</div></section>')


FAQ_TEXT = {'en': ('FAQ', 'FAQ'), 'zh': ('常见问题', '常见问题')}


def faq_items(resources: list[dict], papers: list[dict], discovery_count: int, last_scan: str | None, language: str) -> list[tuple[str, str]]:
    """Visible questions and answers, built from the same counts as the page; each answer is plain text."""
    res, pap = _count(len(resources)), _count(len(papers))
    cases = _count(sum(record['kind'] == 'case-study' for record in resources))
    idx = _count(discovery_count)
    day = last_scan[:10] if last_scan else ''
    if language == 'zh':
        return [
            ('Awesome REA 是什么？', f'Awesome Reverse Engineering Anything 是中英双语的逆向工程目录，收录 {res} 项经来源复核的工具、项目、集成与案例（其中案例 {cases} 个）和 {pap} 篇研究论文，覆盖网站、游戏、应用、二进制、固件与通信协议。'),
            ('每个条目的依据是什么？', '每个条目链接一手来源，并记录来源复核日期；描述对照项目文档或论文撰写。'),
            ('怎样用命令读取单个条目？', '执行 curl -sL https://awesomerea.org/resources/<id>/index.md（论文用 /papers/<id>/index.md），返回带 YAML 头信息的 Markdown。完整目录在 /llms-full.txt，JSON 接口在 /api/v1/。'),
            ('有没有数据集或 API？', '有。/api/v1/resources.json 与 /api/v1/papers.json 提供全部条目，/downloads/records.jsonl 每行一条记录，Hugging Face 上有 TIGER-Lab/AwesomeREA 镜像，也可以克隆 GitHub 仓库。'),
            ('怎样提交新资源、案例或论文？', '在 GitHub 的 Awesome-REA 仓库使用对应的 issue 表单，或提交 pull request；投稿页 /zh/contribute/ 说明所需的一手证据。'),
            ('数据多久更新一次？', f'精选条目通过审核后的 pull request 更新。自动扫描持续加入未审核的发现，目前 {idx} 条，最近一次扫描在 {day}。' if day else '精选条目通过审核后的 pull request 更新。自动扫描持续加入未审核的发现。'),
        ]
    return [
        ('What is Awesome REA?', f'Awesome Reverse Engineering Anything is a bilingual catalog of {res} source-reviewed tools, projects, integrations and case studies ({cases} of them cases) and {pap} research papers on reverse engineering websites, games, apps, native binaries, firmware and communication protocols.'),
        ('What is each entry based on?', 'Every entry links its primary source and records the date the source was reviewed. Descriptions are written against the project documentation or the paper.'),
        ('How do I read one entry from a command line?', 'Run curl -sL https://awesomerea.org/resources/<id>/index.md, or /papers/<id>/index.md for a paper. The reply is Markdown with a YAML header. The full catalog is at /llms-full.txt and the JSON API under /api/v1/.'),
        ('Is there a dataset or an API?', 'Yes. /api/v1/resources.json and /api/v1/papers.json list every entry, /downloads/records.jsonl holds one record per line, the Hugging Face mirror is TIGER-Lab/AwesomeREA, and the GitHub repository can be cloned.'),
        ('How do I suggest a resource, case or paper?', 'Use the matching issue form in the Awesome-REA GitHub repository or open a pull request. The contribute page, /contribute/, lists the primary evidence each type needs.'),
        ('How often is the catalog updated?', f'Curated entries change through reviewed pull requests. Automated scans keep adding unreviewed discoveries, {idx} so far, and the last scan ran on {day}.' if day else 'Curated entries change through reviewed pull requests. Automated scans keep adding unreviewed discoveries.'),
    ]


def faq_markdown(items: list[tuple[str, str]], language: str) -> str:
    """The questions as a Markdown section for the agent-facing files; the homepage itself shows no FAQ."""
    return f'## {FAQ_TEXT[language][1]}\n\n' + '\n\n'.join(f'### {q}\n\n{a}' for q, a in items) + '\n'


def _homepage_head(explorer_html: str) -> str:
    """Keep the title, description, canonical, alternates, social and JSON-LD the homepage already carries."""
    head = re.search(r'<head>(.*?)</head>', explorer_html, re.S).group(1)
    head = re.sub(r'\s*<link rel="stylesheet"[^>]*>', '', head)
    head = re.sub(r'\s*<link rel="preload"[^>]*>', '', head)
    head = re.sub(r'\s*<script src=[^>]*></script>', '', head)
    return head


def render_homepage(*, site_dir: Path, explorer_html: str, resources: list[dict], papers: list[dict], discovery_count: int,
                    last_scan: str | None, language: str, repository_url: str, repository_export: str,
                    order: dict[str, list[str]]) -> str:
    zh = language == 'zh'
    prefix = '/zh' if zh else ''
    locale = 'zh-CN' if zh else 'en'
    rea_css = fingerprinted_href(site_dir, 'rea.css')
    head = _homepage_head(explorer_html)
    title = home_title(resources, papers, language)
    for old in OLD_TITLES[language]:
        head = head.replace(old, escape(title, quote=False))
    head = re.sub(r'(<meta name="viewport"[^>]*>)', lambda match: match.group(1) + head_early(), head, count=1)
    text = COPY[language]
    body = (f'<a class="skip" href="#main">{"跳到正文" if zh else "Skip to content"}</a>'
            + announcement_bar(language)
            + header(language, '', plain_language_link(language, '/' if zh else '/zh/'), repository_url)
            + mobile_bar(language, repository_url)
            + f'<main id="main">{_masthead(resources, papers, discovery_count, last_scan, language, prefix, repository_url)}{_drawer(resources, papers, order, language, prefix, last_scan)}{_featured_projects(language)}</main>'
            + site_footer(language, note=_e(text['licence']), repository_url=repository_url, repository_export=repository_export)
            + palette(language))
    return (f'<!doctype html>\n<html lang="{locale}" data-site="rea" class="no-js">\n<head>{head}\n'
            f'{shell_assets(site_dir)}<link rel="stylesheet" href="{rea_css}">\n</head>\n'
            f'<body class="page-home">{sprite()}{body}\n</body>\n</html>\n')


def _slug(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def _search_parts(record: dict, language: str) -> tuple[str, str, str, str]:
    """The repository label search matches, plus the owner and the rest of the evidence link the result row shows.

    GitHub evidence becomes owner/repo + /blob/<12-character commit>/path: the index carries the repository name and the
    text file carries the owner and the rest. Any other evidence keeps its full URL, labelled by host and path.
    """
    evidence = evidence_label(record['evidence_url'])
    short = record['evidence_url'].removeprefix('https://github.com/')
    if short == record['evidence_url'] or '/' not in short:
        return evidence['repo'], '', record['evidence_url'], evidence
    parts = short.split('/')
    if len(parts) > 3 and parts[2] in ('blob', 'tree') and len(parts[3]) == 40:
        parts[3] = parts[3][:12]
    owner, name = parts[0], parts[1]
    return name, owner, '/'.join(parts)[len(owner) + 1 + len(name):], evidence


def search_index(resources: list[dict], papers: list[dict], language: str, order: dict[str, list[str]]) -> dict:
    """The lazy index behind the palette and the home drawer: compact arrays, one file per language.

    It holds what ranking and filtering read. Row:
    [id, name, kind, targets, category, repository, featured rank, alias, connection, class, status, section, reviewed, added, data class].
    "repository" is the GitHub repository name, or the host label for other evidence. id is 0 when it is the slug of that
    repository name and 1 when it is that slug plus "-case"; alias is 1 when it is the repository name.
    Descriptions, owners, evidence paths and previews follow in search_text(), row for row; "b" pairs the two files.
    """
    zh = language == 'zh'
    kinds = list(KIND_ORDER)
    categories = sorted(CATEGORIES)
    connections = list(CONNECTIONS)
    ranks = {identifier: rank for rank, identifier in enumerate(FEATURED)}
    sections = sorted({collection_section(record) for record in resources})
    rows = []
    for record in resources:
        label, _, _, evidence = _search_parts(record, language)
        alias = evidence['repo'].split('/')[-1] if evidence['host'] == 'github.com' and evidence['repo'] else ''
        alias = alias if alias.lower() != record['name'].lower() else ''
        base = label.split('/')[-1]
        identifier = record['id']
        if base.isascii() and identifier == _slug(base):
            identifier = 0
        elif base.isascii() and identifier == _slug(base) + '-case':
            identifier = 1
        rows.append([identifier, _name(record, language), kinds.index(record['kind']),
                     ''.join(str(DOMAIN_ORDER.index(target)) for target in _ordered_targets(record, order)),
                     categories.index(record['category']), label, ranks.get(record['id'], -1),
                     1 if alias and alias == base else alias,
                     connections.index(CONNECTION_OF[record['relationship']]),
                     -1 if record.get('evidence_class') is None else int(record['evidence_class']),
                     'unknown' if record.get('evidence_status') == 'unknown' else '',
                     sections.index(collection_section(record)),
                     str(record['verified_at'])[:10], record.get('added_at') or '',
                     DATA_CLASS_ORDER.index(record['class']) if record.get('class') in DATA_CLASS_ORDER else -1])
    paper_rows = []
    for paper in papers_newest_first(papers):
        paper_rows.append([paper['id'], paper['title_zh'] if zh else paper['title'], paper['year'], paper['venue'],
                           DOMAIN_ORDER.index(paper['targets'][0]), paper.get('arxiv_id') or '', paper_section(paper)])
    return {
        'v': 2, 'lang': language, 'kinds': kinds, 'kindLabels': [KIND_LABELS[kind][zh] for kind in kinds],
        'kindPlural': [KIND_PLURAL[kind][zh] for kind in kinds], 'kindCodes': [KIND_CODES[kind] for kind in kinds],
        'classes': list(DATA_CLASS_ORDER),
        'targets': list(DOMAIN_ORDER), 'targetLabels': [_target_label(target, language) for target in DOMAIN_ORDER],
        'targetCodes': [DOMAIN_CODES[target] for target in DOMAIN_ORDER],
        'categories': categories, 'categoryLabels': [CATEGORIES[category][zh] for category in categories],
        'connections': connections, 'connectionLabels': [CONNECTIONS[key][0][zh] for key in connections],
        'sections': sections, 'pinned': list(PINNED),
        'b': search_stamp(resources), 'r': rows, 'p': paper_rows,
    }


def scan_facts(discovery_queue: dict | None) -> tuple[str | None, int]:
    """The last scan time and the number of listed discoveries the homepage states."""
    batches = (discovery_queue or {}).get('batches') or []
    last_scan = max((str(batch['ingested_at']) for batch in batches), default=None)
    if last_scan and not last_scan.endswith('Z'):
        last_scan = re.sub(r'\+00:00$', 'Z', last_scan)
    return last_scan, sum(record.get('data_decision') != 'outside' for record in (discovery_queue or {}).get('listed', ()))


def home_faq_markdown(resources: list[dict], papers: list[dict], discovery_queue: dict | None, language: str) -> str:
    last_scan, discovery_count = scan_facts(discovery_queue)
    return faq_markdown(faq_items(resources, papers, discovery_count, last_scan, language), language)

def search_row_id(row: list) -> str:
    """The record id of a search_index() row, as site.js reads it."""
    base = row[5].split('/')[-1]
    return row[0] if isinstance(row[0], str) else _slug(base) + ('-case' if row[0] == 1 else '')


def search_stamp(resources: list[dict]) -> str:
    """Short hash of the row order shared by search_index() and search_text(); the page pairs the two files by it."""
    return hashlib.sha1('\n'.join(record['id'] for record in resources).encode()).hexdigest()[:12]


def search_text(resources: list[dict], language: str) -> dict:
    """Row for row with search_index()["r"]: [description, GitHub owner, rest of the evidence link, preview, preview kind,
    preview thumbnail].

    preview is 1 when it is /previews/<id>.png, and the thumbnail 1 when it is /previews/thumbs/<id>.webp.
    """
    rows = []
    for record in resources:
        _, owner, rest, _ = _search_parts(record, language)
        lead = _lead(record, language)
        if len(lead) > 220:
            lead = lead[:217].rsplit(' ', 1)[0] + '…'
        preview = record.get('preview') or ''
        thumb = record.get('preview_thumb') or ''
        rows.append([lead, owner, rest, 1 if preview == f'/previews/{record["id"]}.png' else preview, record.get('preview_kind') or '',
                     1 if thumb == f'/previews/thumbs/{record["id"]}.webp' else thumb])
    return {'v': 2, 'lang': language, 'b': search_stamp(resources), 'n': len(rows), 't': rows}


def build_home(site_dir: Path, *, explorer_pages: dict[str, str], resources: list[dict], papers: list[dict],
               discovery_queue: dict | None, repository_url: str, repository_export: str) -> None:
    """Write /, /zh/ and their search indexes. ``explorer_pages`` holds the localized head source of each language."""
    site_dir = Path(site_dir)
    order = stored_targets()
    last_scan, discovery_count = scan_facts(discovery_queue)
    for language, route in (('en', 'index.html'), ('zh', 'zh/index.html')):
        page = site_dir / route
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(render_homepage(site_dir=site_dir, explorer_html=explorer_pages[language], resources=resources, papers=papers,
                                        discovery_count=discovery_count, last_scan=last_scan, language=language, repository_url=repository_url,
                                        repository_export=repository_export, order=order), encoding='utf-8')
        suffix = '.zh' if language == 'zh' else ''
        (site_dir / f'search-index{suffix}.json').write_text(json.dumps(search_index(resources, papers, language, order), ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
        (site_dir / f'search-text{suffix}.json').write_text(json.dumps(search_text(resources, language), ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
