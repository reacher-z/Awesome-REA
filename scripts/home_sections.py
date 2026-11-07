"""The homepage sections below the drawer: guides, case files, recent additions, categories, papers and developer data.

Every number comes from the records passed in, and links open pages or filtered views that exist today. Nothing reads the
clock: "recently added" counts back from the newest record, so the same commit always builds the same bytes.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, timedelta
from html import escape

from build_readme import (AGENT_EVALUATION_PAPERS, CATEGORIES, METHOD_HEADINGS, PAPER_TOPIC_LABELS, collection_section, method_groups,
                          paper_groups, papers_newest_first)
from home_art import vignette
from site_shell import icon

TEXT = {
    'en': {
        'start': 'Start here', 'start_intro': 'Pick the job you have; each opens a filtered list.',
        'latest': 'Recently added', 'scans': 'Found by the scans',
        'scans_note': 'The scheduled scan matched these to reverse-engineering topics. Nobody has read their sources yet.',
        'unreviewed': 'Unreviewed', 'browse_scans': 'All {n} unreviewed discoveries', 'browse_index': 'The repository directory', 'all_additions': 'Newest first',
        'categories': 'Browse by category', 'all_resources': 'All {n} resources', 'more': 'and {n} more', 'day_more': '{n} more that day',
        'papers': 'Papers', 'all_papers': 'All {n} papers', 'by_year': 'Papers by year', 'topics': 'By topic', 'earlier': 'Earlier',
        'dev': 'For agents and developers', 'dev_intro': 'The same records as this site, in formats a script or an agent can read in one request.',
        'contribute': 'Contribute', 'contribute_intro': 'Records are added through reviewed pull requests. Each suggestion needs a public primary source; the forms ask for exactly what review checks.',
        'copy': 'Copy', 'guide': 'Contribution guide', 'agents': 'Instructions for agents',
        'case_kicker': 'Case files', 'case_stamp': 'CASE', 'case_head': '<span class="cb-n">{n}</span> reconstructions', 'and_others': ' and others', 'join': ', ',
        'case_note': 'Game decompilations, static recompilations, ports and protocol investigations, grouped by method and traced to their sources.',
    },
    'zh': {
        'start': '从这里开始', 'start_intro': '按你要做的事选择，每一项都会打开筛选好的列表。',
        'latest': '最近新增', 'scans': '扫描新发现',
        'scans_note': '定时扫描按逆向工程主题匹配到这些仓库，尚无人阅读其来源。',
        'unreviewed': '未审核', 'browse_scans': '全部 {n} 条未审核发现', 'browse_index': '仓库目录', 'all_additions': '最新在前',
        'categories': '按类别浏览', 'all_resources': '全部 {n} 项资源', 'more': '另有 {n} 项', 'day_more': '当天另有 {n} 项',
        'papers': '论文', 'all_papers': '全部 {n} 篇论文', 'by_year': '按年份', 'topics': '按主题', 'earlier': '更早',
        'dev': '面向智能体与开发者', 'dev_intro': '与本站相同的记录，以脚本或智能体一次请求即可读取的格式提供。',
        'contribute': '参与贡献', 'contribute_intro': '记录通过经过审核的拉取请求加入。每条建议都需要公开的原始来源；表单只询问审核会检查的内容。',
        'copy': '复制', 'guide': '贡献指南', 'agents': '智能体说明',
        'case_kicker': '案例档案', 'case_stamp': '案例', 'case_head': '<span class="cb-n">{n}</span> 个重建案例', 'and_others': '等', 'join': '、',
        'case_note': '游戏反编译、静态重编译、移植与协议调查，按重建方式分组，每项都附原始来源。',
    },
}
CATEGORY_NOTES = {
    'reconstruction-cases': ('Decompilations, recompilations, ports and engine rewrites with public evidence.', '有公开证据的反编译、重编译、移植与引擎重写。'),
    'native-analysis': ('Disassemblers, decompilers and frameworks for executables and libraries.', '面向可执行文件与库的反汇编器、反编译器和分析框架。'),
    'android': ('Decompilers, unpackers and instrumentation for APKs and Dex bytecode.', '面向 APK 与 Dex 字节码的反编译、解包与插桩工具。'),
    'firmware': ('Extraction, emulation and analysis of firmware images and devices.', '固件镜像与设备的提取、仿真和分析。'),
    'dynamic-analysis': ('Debuggers, tracers and instrumentation for running processes.', '面向运行中进程的调试、跟踪与插桩。'),
    'game-analysis': ('Asset extractors, engine tooling and graphics debuggers for games.', '游戏资源提取、引擎工具与图形调试器。'),
    'protocol-analysis': ('Capture, decoding and inference of network, radio and bus protocols.', '网络、无线与总线协议的抓取、解码和推断。'),
    'learning': ('Courses, books, references and background reading.', '课程、书籍、参考资料与延伸阅读。'),
    'community-case-studies': ('Third-party investigations whose authors report using REA with other tools.', '作者报告结合 REA 与其他工具完成的第三方调查。'),
    'agent-mcp': ('MCP servers that connect agents to IDA, Ghidra, Frida and more.', '把智能体连接到 IDA、Ghidra、Frida 等工具的 MCP 服务。'),
    'related-lists': ('Other curated lists that cover reverse engineering.', '其他涵盖逆向工程的精选目录。'),
    'agent-workflows': ('Agent skills and workflows for reverse-engineering tasks.', '面向逆向工程任务的智能体技能与工作流。'),
    'web-analysis': ('Deobfuscators, proxies and tooling for web apps and JavaScript.', '面向网页应用与 JavaScript 的反混淆、代理与分析工具。'),
    'binary-libraries': ('Libraries for parsing, lifting and emulating binaries.', '解析、提升与模拟二进制文件的库。'),
}


def split_case_name(name: str) -> tuple[str, str]:
    """Case names are '<lead>: <summary>' (or '<lead> — <summary>' when the lead has a colon), data/README.md.
    Many leads still contain a colon ("Animal Crossing: Wild World: matching …"), so split at the last ': ' whose
    summary starts in lower case, and fall back to the first ': '."""
    if ' — ' in name:
        lead, rest = name.split(' — ', 1)
        return lead, rest
    parts = name.split(': ')
    for i in range(len(parts) - 1, 0, -1):
        if parts[i][:1].islower():
            return ': '.join(parts[:i]), ': '.join(parts[i:])
    if len(parts) > 1:
        return parts[0], ': '.join(parts[1:])
    return name, ''


def _e(value) -> str:
    return escape(str(value), quote=True)


def _name(record: dict, language: str) -> str:
    return record.get('name_zh') or record['name'] if language == 'zh' else record['name']


def guides(resources: list[dict], papers: list[dict], language: str) -> str:
    zh = language == 'zh'
    prefix = '/zh' if zh else ''
    text = TEXT[language]
    tools = [record for record in resources if record['kind'] == 'tool']
    game_cases = [record for record in resources if record['kind'] == 'case-study' and collection_section(record) == 'game']
    n_binary = sum('binary' in record['targets'] for record in tools)
    n_app = sum('app' in record['targets'] for record in tools)
    n_firmware = sum('firmware' in record['targets'] for record in tools)
    n_integrations = sum(record['kind'] == 'integration' and 'binary' in record['targets'] for record in resources)
    n_benchmarks = sum(paper['id'] in AGENT_EVALUATION_PAPERS for paper in papers)
    items = (
        ('BIN·TOOL', ('Decompile and analyse a native binary', '反编译并分析原生二进制'), (f'{n_binary} tools', f'{n_binary} 项工具'), f'{prefix}/?target=binary&amp;kind=tool#catalog', 'hex'),
        ('APP·TOOL', ('Inspect or instrument a running app', '检查或插桩运行中的应用'), (f'{n_app} tools', f'{n_app} 项工具'), f'{prefix}/?target=app&amp;kind=tool#catalog', 'tree'),
        ('GAM·CASE', ('See how a game was rebuilt', '看一款游戏如何被重建'), (f'{len(game_cases)} case studies', f'{len(game_cases)} 个案例'), f'{prefix}/cases/#cases-game', 'cart'),
        ('BIN·INTG', ('Connect an agent to IDA or Ghidra', '把智能体接入 IDA 或 Ghidra'), (f'{n_integrations} integrations', f'{n_integrations} 项集成'), f'{prefix}/?target=binary&amp;kind=integration#catalog', 'plug'),
        ('FMW·TOOL', ('Dump and analyse firmware', '提取并分析固件'), (f'{n_firmware} tools', f'{n_firmware} 项工具'), f'{prefix}/?target=firmware&amp;kind=tool#catalog', 'pins'),
        ('RSCH·BENCH', ('Benchmark a reverse-engineering agent', '评测逆向工程智能体'), (f'{n_benchmarks} papers', f'{n_benchmarks} 篇论文'), f'{prefix}/papers/#research-agent-evaluation', 'trace'),
    )
    cards = ''.join(f'<li><a class="guide" href="{href}"><span class="guide-tab">{code}</span><span class="guide-task">{task[zh]}</span>'
                    f'<span class="guide-count">{count[zh]}</span>{vignette(art)}</a></li>' for code, task, count, href, art in items)
    return (f'<section class="section wrap" aria-labelledby="start-title"><div class="section-head"><h2 id="start-title">{text["start"]}</h2></div>'
            f'<p class="section-intro">{text["start_intro"]}</p><ul class="guides">{cards}</ul></section>')


def case_band(resources: list[dict], language: str) -> str:
    """The page's colour moment: the case count and the three largest game reconstruction methods."""
    zh = language == 'zh'
    prefix = '/zh' if zh else ''
    text = TEXT[language]
    cases = [record for record in resources if record['kind'] == 'case-study']
    game = [record for record in cases if collection_section(record) == 'game']
    methods = sorted(((method, records) for method, records in method_groups(game) if method != 'other'), key=lambda item: -len(item[1]))[:3]
    folders = []
    for method, records in methods:
        names = sorted((split_case_name(_name(record, language))[0] for record in records), key=str.casefold)[:2]
        folders.append(f'<li class="cb-folder"><p class="cb-tab">GAM·CASE</p><span class="cb-stamp" aria-hidden="true">{text["case_stamp"]}</span>'
                       f'<h3><a class="stretch" href="{prefix}/cases/#cases-game-{method}">{_e(METHOD_HEADINGS[method][zh])}</a></h3>'
                       f'<p class="cb-count">{len(records)}</p><p class="cb-names">{_e(text["join"].join(names))}{text["and_others"]}</p></li>')
    return (f'<section class="caseband" aria-labelledby="cases-title"><div class="wrap"><p class="cb-kicker">{text["case_kicker"]}</p>'
            f'<div class="cb-head"><h2 id="cases-title"><a href="{prefix}/cases/">{text["case_head"].format(n=len(cases))}</a></h2><p class="cb-note">{text["case_note"]}</p></div>'
            f'<ul class="cb-folders">{"".join(folders)}</ul></div></section>')


def scan_candidates(queue: dict | None, resources: list[dict], language: str, count: int = 3) -> list[dict]:
    """The most-starred unreviewed discoveries with a description. They stay labelled unreviewed and outside every curated count."""
    curated = {record['url'].rstrip('/').lower() for record in resources}
    items = []
    for record in (queue or {}).get('listed', []):
        description = record.get('description_zh' if language == 'zh' else 'description_en') or ''
        if record['url'].rstrip('/').lower() in curated or not description or (language == 'en' and not description.isascii()):
            continue
        items.append({'full_name': record['full_name'], 'url': record['url'], 'stars': record.get('stars') or 0,
                      'description': description if len(description) < 110 else description[:107].rsplit(' ', 1)[0] + '…'})
    return sorted(items, key=lambda item: (-item['stars'], item['full_name']))[:count]


def latest(resources: list[dict], queue: dict | None, language: str, callno) -> str:
    zh = language == 'zh'
    prefix = '/zh' if zh else ''
    text = TEXT[language]
    dates = [record['added_at'] for record in resources if record.get('added_at')]
    if not dates:
        return ''
    since = (date.fromisoformat(max(dates)) - timedelta(days=14)).isoformat()
    by_day = defaultdict(list)
    for record in resources:
        if (record.get('added_at') or '') >= since:
            by_day[record['added_at']].append(record)
    all_link = f'{prefix}/?sort=added#catalog'
    days = []
    for day, rows in sorted(by_day.items(), reverse=True)[:3]:
        moment = date.fromisoformat(day)
        label = f'{moment.month} 月 {moment.day} 日' if zh else f'{moment.day} {moment:%b}'
        rows = sorted(rows, key=lambda record: (record['kind'] != 'tool', record['kind'] != 'integration', _name(record, language).casefold()))
        items = ''.join(f'<li><span class="lt-call">{callno(record)}</span><a href="{prefix}/resources/{_e(record["id"])}/">{_e(_name(record, language))}</a></li>' for record in rows[:3])
        if len(rows) > 3:
            items += f'<li class="lt-more"><span class="lt-call"></span><a href="{all_link}">{text["day_more"].format(n=len(rows) - 3)}</a></li>'
        days.append(f'<li class="lt-day"><time datetime="{day}">{label}</time><ul>{items}</ul></li>')
    scans = ''.join(f'<li><span class="stamp-info">{icon("info")}{text["unreviewed"]}</span><a href="{_e(item["url"])}" rel="noopener">{_e(item["full_name"])}</a>'
                    f'<span class="sc-desc">{_e(item["description"])}</span></li>' for item in scan_candidates(queue, resources, language))
    browse_scans = text['browse_scans'].format(n=f"{(queue or {}).get('record_count', 0):,}")
    return (f'<section class="section wrap" aria-labelledby="latest-title"><div class="section-head"><h2 id="latest-title">{text["latest"]}</h2>'
            f'<a class="more" href="{all_link}">{text["all_additions"]}</a></div><div class="latest"><ol class="lt-feed">{"".join(days)}</ol>'
            f'<div class="scans"><h3>{text["scans"]}</h3><p class="scans-note">{text["scans_note"]}</p><ul>{scans}</ul>'
            f'<p class="scans-links"><a href="{prefix}/discoveries/">{browse_scans}</a>'
            f'<a href="{prefix}/browse/">{text["browse_index"]}</a></p></div></div></section>')


def categories(resources: list[dict], language: str, featured: tuple[str, ...]) -> str:
    zh = language == 'zh'
    prefix = '/zh' if zh else ''
    text = TEXT[language]
    counts = Counter(record['category'] for record in resources)
    rank = {identifier: position for position, identifier in enumerate(featured)}
    blocks = []
    for key, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:12]:
        href = f'{prefix}/explore/?view=curated&amp;category={key}'
        members = sorted((record for record in resources if record['category'] == key), key=lambda record: (rank.get(record['id'], 99), record['kind'] != 'tool', record['name'].casefold()))
        top = members[:2]
        names = text['join'].join(f'<a href="{prefix}/resources/{_e(record["id"])}/">{_e(split_case_name(_name(record, language))[0] if record["kind"] == "case-study" else _name(record, language))}</a>' for record in top)
        more = f'{"，" if zh else ", "}<a class="cat-more" href="{href}">{text["more"].format(n=count - len(top))}</a>' if count > len(top) else ''
        blocks.append(f'<li class="cat"><h3><a href="{href}">{_e(CATEGORIES[key][zh])}</a> <span class="count">{count}</span></h3>'
                      f'<p class="cat-note">{_e(CATEGORY_NOTES.get(key, ("", ""))[zh])}</p><p class="cat-items">{names}{more}</p></li>')
    return (f'<section class="section wrap" aria-labelledby="categories-title"><div class="section-head"><h2 id="categories-title">{text["categories"]}</h2>'
            f'<span class="count">{len(counts)}</span><a class="more" href="{prefix}/resources/">{text["all_resources"].format(n=f"{len(resources):,}")}</a></div>'
            f'<ul class="cats">{"".join(blocks)}</ul></section>')


def year_chart(papers: list[dict], language: str) -> str:
    """One colour, selective labels. CSP forbids style attributes, so bar heights are classes in 2% steps (rea.css)."""
    zh = language == 'zh'
    prefix = '/zh' if zh else ''
    text = TEXT[language]
    years = Counter(paper['year'] for paper in papers)
    low, high = min(years), max(years)
    peak = max(years.values())
    bars = []
    for year in range(low, high + 1):
        count = years.get(year, 0)
        tip = f'{year} 年：{count} 篇' if zh else f'{year}: {count} paper{"s" if count != 1 else ""}'
        label = f'<span class="yb-n">{count}</span>' if (year == high or count == peak) and count else ''
        tick = f'<span class="yb-y">{year}</span>' if year in (low, high) or (year % 5 == 0 and low + 3 <= year <= high - 3) else ''
        step = max(2, round(count / peak * 50) * 2)
        bar = f'<span class="yb yb-h{step}">{label}</span>' if count else ''
        bars.append(f'<span class="yb-col" data-tip="{tip}">{bar}{tick}</span>')
    recent = [year for year in range(high, high - 4, -1) if years.get(year)]
    earlier = sum(count for year, count in years.items() if year < recent[-1])
    links = ''.join(f'<li><a href="{prefix}/papers/?year={year}">{year}</a> <span class="count">{years[year]}</span></li>' for year in recent)
    links += f'<li>{text["earlier"]} <span class="count">{earlier}</span></li>'
    summary = '；'.join(f'{year} 年 {years[year]} 篇' for year in recent) if zh else ', '.join(f'{years[year]} in {year}' for year in recent)
    alt = f'{low}–{high} 年每年收录的论文数：{summary}；更早 {earlier} 篇。' if zh else f'Papers per publication year, {low} to {high}: {summary}, and {earlier} earlier.'
    return (f'<figure class="years"><figcaption>{text["by_year"]}</figcaption><div class="yb-list" role="img" aria-label="{alt}">{"".join(bars)}</div>'
            f'<ul class="year-links">{links}</ul></figure>')


def _paper_row(paper: dict, language: str) -> str:
    zh = language == 'zh'
    prefix = '/zh' if zh else ''
    when = paper.get('publication_date') or str(paper['year'])
    authors = paper.get('authors') or []
    if paper.get('authors_omitted') or not authors:
        byline = '作者：见原文' if zh else 'Authors: see the paper'
    else:
        byline = ', '.join(authors[:3]) + (' et al.' if len(authors) > 3 else '')
    links = [('论文' if zh else 'Paper', paper['url'])]
    if paper.get('arxiv_id'):
        links.append(('arXiv', f'https://arxiv.org/abs/{paper["arxiv_id"]}'))
    if paper.get('code_url'):
        links.append(('代码' if zh else 'Code', paper['code_url']))
    anchors = ''.join(f'<a href="{_e(url)}" rel="noopener">{name}</a>' for name, url in links)
    return (f'<li class="paper"><time class="pp-date" datetime="{_e(when)}">{_e(when)}</time><div class="pp-body">'
            f'<h3 class="pp-title"><a href="{prefix}/papers/{_e(paper["id"])}/">{_e(paper["title_zh"] if zh else paper["title"])}</a></h3>'
            f'<p class="pp-meta"><span class="pp-venue">{_e(paper["venue"])}</span><span class="pp-by">{_e(byline)}</span></p>'
            f'<p class="pp-links">{anchors}</p></div></li>')


def papers_block(papers: list[dict], language: str) -> str:
    zh = language == 'zh'
    prefix = '/zh' if zh else ''
    text = TEXT[language]
    groups = paper_groups(papers)
    topics = ''.join(f'<li><a href="{prefix}/papers/#research-{key}">{_e(labels[zh])}</a> <span class="count">{len(groups[key])}</span></li>'
                     for key, labels in PAPER_TOPIC_LABELS.items() if groups.get(key))
    rows = ''.join(_paper_row(paper, language) for paper in papers_newest_first(papers)[:4])
    return (f'<section class="section wrap" aria-labelledby="papers-title"><div class="section-head"><h2 id="papers-title">{text["papers"]}</h2>'
            f'<span class="count">{len(papers)}</span><a class="more" href="{prefix}/papers/">{text["all_papers"].format(n=len(papers))}</a></div>'
            f'<div class="papers-grid"><ol class="papers">{rows}</ol><div class="papers-side">{year_chart(papers, language)}'
            f'<h3 class="side-h">{text["topics"]}</h3><ul class="topics">{topics}</ul></div></div></section>')


def dev_block(language: str, repository_url: str) -> str:
    zh = language == 'zh'
    text = TEXT[language]
    items = (
        ('llms.txt', ('A plain-text map of the site for language models.', '供语言模型读取的纯文本站点地图。'), 'curl https://awesomerea.org/llms.txt', '/llms.txt'),
        ('JSON API', ('Every curated record with evidence links, versioned and CORS-enabled.', '全部精选记录及证据链接，带版本号并允许跨域。'),
         "curl -s https://awesomerea.org/api/v1/resources.json \\\n  | jq '.resources[] | select(.targets | index(\"firmware\")) | .name'", '/zh/api/' if zh else '/api/'),
        ('Hugging Face', ('The catalogue as a dataset, one config per record type.', '以数据集形式提供的目录，每种记录类型一个 config。'),
         'from datasets import load_dataset\nds = load_dataset("AgPerry/awesome-rea", "resources")', 'https://huggingface.co/datasets/AgPerry/awesome-rea'),
        ('Cite', ('Cite the catalogue as a project, not a person.', '以项目而非个人名义引用本目录。'),
         '@misc{awesome_rea,\n  title  = {Awesome Reverse Engineering Anything},\n  author = {{Awesome REA}},\n  year   = {2026},\n  url    = {https://awesomerea.org}\n}', repository_url + '/blob/main/CITATION.cff'),
    )
    tiles = ''.join(f'<li class="dev"><h3><a href="{_e(href)}">{name}</a></h3><p>{description[zh]}</p>'
                    f'<div class="code"><pre id="code-{position}" tabindex="0" aria-label="{name}"><code>{_e(code)}</code></pre>'
                    f'<button class="copy" type="button" data-copy="#code-{position}" aria-label="{text["copy"]}: {name}">{icon("copy")}<span>{text["copy"]}</span></button></div></li>'
                    for position, (name, description, code, href) in enumerate(items))
    return (f'<section class="section wrap" aria-labelledby="dev-title"><div class="section-head"><h2 id="dev-title">{text["dev"]}</h2></div>'
            f'<p class="section-intro">{text["dev_intro"]}</p><ul class="devs">{tiles}</ul></section>')


def contribute_block(language: str, repository_url: str) -> str:
    zh = language == 'zh'
    text = TEXT[language]
    forms = (('resource.yml', ('Suggest a resource', '推荐资源')), ('case-study.yml', ('Suggest a case study', '推荐案例')),
             ('paper.yml', ('Suggest a paper', '推荐论文')), ('broken-resource.yml', ('Report a broken link', '报告失效链接')))
    buttons = ''.join(f'<a class="btn{" btn-primary" if position == 0 else ""}" href="{repository_url}/issues/new?template={form}" rel="noopener">{label[zh]}{icon("external")}</a>'
                      for position, (form, label) in enumerate(forms))
    return (f'<section class="section wrap" aria-labelledby="contribute-title"><div class="contribute"><div><h2 id="contribute-title">{text["contribute"]}</h2><p>{text["contribute_intro"]}</p>'
            f'<p class="contribute-links"><a href="{repository_url}/blob/main/CONTRIBUTING.md">{text["guide"]}</a><a href="{repository_url}/blob/main/AGENTS.md">{text["agents"]}</a></p></div>'
            f'<div class="contribute-actions">{buttons}</div></div></section>')
