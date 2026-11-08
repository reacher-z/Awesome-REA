"""The homepage: masthead, search, target tabs and the index-card drawer, rendered from the curated catalog.

Every number comes from the records passed in. Scan-only discoveries are shown as their own labelled count,
never in the curated totals. The page works without JavaScript: the tabs and cards are links and the search
form opens the full listing. site.js adds search in place from the lazily loaded /search-index.json.
"""
from __future__ import annotations

from collections import Counter
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from asset_paths import fingerprinted_href
from build_readme import CATEGORIES, KIND_LABELS, TARGETS, collection_section, lead_sentence, paper_section, papers_newest_first
from home_art import exploded_view
from site_footer import site_footer
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
COPY = {
    'en': {
        'h1': 'Reverse engineer <em>anything</em>',
        'lede': 'Tools, case studies and papers for taking apart binaries, games, apps, firmware, protocols and websites, each checked against its source.',
        'search_label': 'Search the catalogue', 'placeholder': 'Try Ghidra, IL2CPP or BLE', 'clear': 'Clear search', 'focus': 'Press / to focus',
        'stats': '<span class="s-lg"><strong>{res}</strong> curated resources and <strong>{pap}</strong> papers, each reviewed against its source. Plus <a href="/discoveries/"><strong>{idx}</strong> unreviewed discoveries</a> from the scans.</span><span class="s-sm"><strong>{res}</strong> resources, <strong>{pap}</strong> papers, <a href="/discoveries/"><strong>{idx}</strong> unreviewed</a></span>',
        'updated': 'Last scan', 'all': 'All', 'domains': 'Target domains', 'catalogue': 'Catalogue',
        'kind': 'Kind', 'all_kinds': 'All kinds', 'sort': 'Sort', 'featured': 'Featured', 'recent': 'Recently reviewed', 'az': 'Name A–Z',
        'showing': 'Showing <strong>{n}</strong> of <strong>{total}</strong>', 'show_all': 'Show all {n} resources',
        'drawer_note': 'Each card links to its entry: description, requirements and the primary source it was reviewed against.',
        'reviewed': 'Reviewed', 'targets': 'Targets', 'licence': 'Original content: MIT. Linked projects keep their own licenses.',
    },
    'zh': {
        'h1': '逆向<em>一切</em>',
        'lede': '拆解二进制、游戏、应用、固件、协议与网站所需的工具、案例与论文，每一条都对照原始来源核查。',
        'search_label': '搜索目录', 'placeholder': '试试 Ghidra、IL2CPP 或 BLE', 'clear': '清除搜索', 'focus': '按 / 键聚焦',
        'stats': '<span class="s-lg"><strong>{res}</strong> 项精选资源与 <strong>{pap}</strong> 篇论文，均已对照来源复核。另有 <a href="/zh/discoveries/"><strong>{idx}</strong> 条未审核发现</a>来自自动扫描。</span><span class="s-sm"><strong>{res}</strong> 项资源、<strong>{pap}</strong> 篇论文、<a href="/zh/discoveries/"><strong>{idx}</strong> 条未审核</a></span>',
        'updated': '最近扫描', 'all': '全部', 'domains': '目标领域', 'catalogue': '目录',
        'kind': '类型', 'all_kinds': '全部类型', 'sort': '排序', 'featured': '精选', 'recent': '最近复核', 'az': '名称 A–Z',
        'showing': '显示 <strong>{n}</strong> / <strong>{total}</strong>', 'show_all': '查看全部 {n} 项资源',
        'drawer_note': '每张卡片都链接到完整条目：说明、使用条件，以及复核所依据的原始来源。',
        'reviewed': '已复核', 'targets': '目标', 'licence': '原创内容采用 MIT 许可。链接项目保留各自的许可。',
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
            f'<h3 class="card-name"><a class="stretch{entry}" href="{prefix}/resources/{identifier}/">{_e(_name(record, language))}</a>{mark}</h3>'
            f'<p class="card-desc">{_e(_lead(record, language))}</p>'
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


def _masthead(resources, papers, discovery_count, last_scan, language, prefix, repository_url) -> str:
    text = COPY[language]
    stats = text['stats'].format(res=_count(len(resources)), pap=_count(len(papers)), idx=_count(discovery_count))
    updated = (f'<p class="updated">{text["updated"]} <time datetime="{_e(last_scan)}" data-rel>{_e(last_scan[:10])}</time></p>' if last_scan else '')
    return (f'<section class="masthead" aria-labelledby="hero-title"><div class="wrap">'
            f'{icon("reg", "reg reg-tl")}{icon("reg", "reg reg-tr")}<div class="xv">{exploded_view(language)}</div>'
            f'<div class="hero-top"><h1 class="hero-title" id="hero-title">{text["h1"]}</h1><p class="lede">{text["lede"]}</p></div>'
            f'<form class="hero-search" role="search" action="{prefix}/resources/" method="get" data-home-search>'
            f'<label class="hs-label" for="q">{text["search_label"]}</label>{icon("search")}'
            f'<input id="q" name="q" type="search" placeholder="{text["placeholder"]}" autocomplete="off" autocapitalize="off" spellcheck="false" enterkeyhint="search" aria-describedby="hs-count" data-search-input>'
            f'<span class="hs-side"><span class="hs-count" id="hs-count" aria-live="polite" data-search-count></span>'
            f'<button class="hs-clear" type="button" aria-label="{text["clear"]}" data-search-clear>{icon("close")}</button>'
            f'<kbd class="hs-kbd" title="{text["focus"]}">/</kbd></span></form>'
            f'<div class="hero-meta">{star_button(language, repository_url, "hero-star")}<div class="hero-stats"><p>{stats}</p>{updated}</div></div>{_folder_tabs(resources, language, prefix)}'
            f'</div></section>')


def _drawer(resources, order, language, prefix) -> str:
    text = COPY[language]
    by_id = {record['id']: record for record in resources}
    featured = [by_id[identifier] for identifier in FEATURED if identifier in by_id][:DRAWER_ROWS]
    kinds = Counter(record['kind'] for record in resources)
    present = [kind for kind in KIND_ORDER if kinds[kind]]
    zh = language == 'zh'
    chips = ''.join(f'<button class="chip" type="button" data-kind="{kind}" aria-pressed="false">{icon("check")}{KIND_PLURAL[kind][zh]} <span class="count">{_count(kinds[kind])}</span></button>' for kind in present)
    options = ''.join(f'<option value="{kind}">{KIND_PLURAL[kind][zh]} ({_count(kinds[kind])})</option>' for kind in present)
    cards = ''.join(index_card(record, language, _ordered_targets(record, order), prefix=prefix) for record in featured)
    total = len(resources)
    return (f'<section class="wrap drawer-wrap" id="catalog" aria-labelledby="catalogue-title"><div class="drawer" id="catalogue" data-drawer>'
            f'<h2 class="vh" id="catalogue-title">{text["catalogue"]}</h2><div class="drawer-bar">'
            f'<div class="chips" role="group" aria-label="{text["kind"]}" data-kind-chips>{chips}</div>'
            f'<label class="select kind-select"><span class="vh">{text["kind"]}</span><select data-kind-select aria-label="{text["kind"]}"><option value="">{text["all_kinds"]}</option>{options}</select>{icon("chevron")}</label>'
            f'<label class="select"><span class="select-label">{text["sort"]}</span><select data-sort aria-label="{text["sort"]}">'
            f'<option value="featured">{text["featured"]}</option><option value="reviewed">{text["recent"]}</option><option value="name">{text["az"]}</option></select>{icon("chevron")}</label>'
            f'<p class="drawer-meta" data-drawer-meta aria-live="polite">{text["showing"].format(n=len(featured), total=_count(total))}</p></div>'
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
    head = re.sub(r'(<meta name="viewport"[^>]*>)', lambda match: match.group(1) + head_early(), head, count=1)
    text = COPY[language]
    body = (f'<a class="skip" href="#main">{"跳到正文" if zh else "Skip to content"}</a>'
            + announcement_bar(language)
            + header(language, '', plain_language_link(language, '/' if zh else '/zh/'), repository_url)
            + mobile_bar(language, repository_url)
            + f'<main id="main">{_masthead(resources, papers, discovery_count, last_scan, language, prefix, repository_url)}{_drawer(resources, order, language, prefix)}{_featured_projects(language)}</main>'
            + site_footer(language, note=_e(text['licence']), repository_url=repository_url, repository_export=repository_export)
            + palette(language))
    return (f'<!doctype html>\n<html lang="{locale}" data-site="rea" class="no-js">\n<head>{head}\n'
            f'{shell_assets(site_dir)}<link rel="stylesheet" href="{rea_css}">\n</head>\n'
            f'<body class="page-home">{sprite()}{body}\n</body>\n</html>\n')


def search_index(resources: list[dict], papers: list[dict], language: str, order: dict[str, list[str]]) -> dict:
    """The lazy index behind the palette and the home drawer: compact arrays, one file per language."""
    zh = language == 'zh'
    kinds = list(KIND_ORDER)
    categories = sorted(CATEGORIES)
    connections = list(CONNECTIONS)
    ranks = {identifier: rank for rank, identifier in enumerate(FEATURED)}
    sections = sorted({collection_section(record) for record in resources})
    rows = []
    for record in resources:
        evidence = evidence_label(record['evidence_url'])
        short = record['evidence_url'].removeprefix('https://github.com/')
        if short != record['evidence_url']:
            parts = short.split('/')
            if len(parts) > 3 and parts[2] in ('blob', 'tree') and len(parts[3]) == 40:
                parts[3] = parts[3][:12]
            short = '/'.join(parts)
        alias = evidence['repo'].split('/')[-1] if evidence['host'] == 'github.com' and evidence['repo'] else ''
        lead = _lead(record, language)
        if len(lead) > 220:
            lead = lead[:217].rsplit(' ', 1)[0] + '…'
        rows.append([record['id'], _name(record, language), kinds.index(record['kind']),
                     ''.join(str(DOMAIN_ORDER.index(target)) for target in _ordered_targets(record, order)),
                     categories.index(record['category']), lead,
                     '' if short != record['evidence_url'] else evidence['repo'], short,
                     str(record['verified_at'])[:10], record.get('added_at') or '', ranks.get(record['id'], -1),
                     alias if alias.lower() != record['name'].lower() else '',
                     connections.index(CONNECTION_OF[record['relationship']]), sections.index(collection_section(record))])
    paper_rows = []
    for paper in papers_newest_first(papers):
        paper_rows.append([paper['id'], paper['title_zh'] if zh else paper['title'], paper['year'], paper['venue'],
                           DOMAIN_ORDER.index(paper['targets'][0]), paper.get('arxiv_id') or '', paper_section(paper)])
    return {
        'v': 1, 'lang': language, 'kinds': kinds, 'kindLabels': [KIND_LABELS[kind][zh] for kind in kinds],
        'kindPlural': [KIND_PLURAL[kind][zh] for kind in kinds], 'kindCodes': [KIND_CODES[kind] for kind in kinds],
        'targets': list(DOMAIN_ORDER), 'targetLabels': [_target_label(target, language) for target in DOMAIN_ORDER],
        'targetCodes': [DOMAIN_CODES[target] for target in DOMAIN_ORDER],
        'categories': categories, 'categoryLabels': [CATEGORIES[category][zh] for category in categories],
        'connections': connections, 'connectionLabels': [CONNECTIONS[key][0][zh] for key in connections],
        'sections': sections, 'pinned': list(PINNED),
        'r': rows, 'p': paper_rows,
    }


def build_home(site_dir: Path, *, explorer_pages: dict[str, str], resources: list[dict], papers: list[dict],
               discovery_queue: dict | None, repository_url: str, repository_export: str) -> None:
    """Write /, /zh/ and their search indexes. ``explorer_pages`` holds the localized head source of each language."""
    site_dir = Path(site_dir)
    order = stored_targets()
    batches = (discovery_queue or {}).get('batches') or []
    last_scan = max((str(batch['ingested_at']) for batch in batches), default=None)
    if last_scan and not last_scan.endswith('Z'):
        last_scan = re.sub(r'\+00:00$', 'Z', last_scan)
    discovery_count = len((discovery_queue or {}).get('listed', ()))
    for language, route in (('en', 'index.html'), ('zh', 'zh/index.html')):
        page = site_dir / route
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(render_homepage(site_dir=site_dir, explorer_html=explorer_pages[language], resources=resources, papers=papers,
                                        discovery_count=discovery_count, last_scan=last_scan, language=language, repository_url=repository_url,
                                        repository_export=repository_export, order=order), encoding='utf-8')
        name = 'search-index.zh.json' if language == 'zh' else 'search-index.json'
        (site_dir / name).write_text(json.dumps(search_index(resources, papers, language, order), ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
