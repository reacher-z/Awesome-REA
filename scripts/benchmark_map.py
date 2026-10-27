#!/usr/bin/env python3
"""Draw the long-task coverage map used by the README and the website.

Six targets share the 1,000-task target evenly. A purple cell is one curated
case with a shipped input and a checkable output, large enough for a
computer-use session past three hours. A gray cell is still open.
"""
import json
from html import escape
from math import ceil
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

from open_graph import open_graph_meta, website_reference

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://awesomerea.org'

SHORT = frozenset({
    'rea-dinosaur-speed-case', 'rea-dino-runner-community-case', 'rea-dxball-case', 'rea-th04-case',
    'rea-calculator-percent-case', 'rea-aegis-case', 'rea-notion-case', 'rea-ctf-case',
    'rea-engine-tictactoe-case', 'snowball-war-rea-case', 'pocket-tasks-reconstruction-case',
    'sa3-marun-ai-decomp-case', 'ultrasunnymoon-rea-case', 'screen-studio-auto-zoom-case',
    'littlebird-static-rebuild-case', 'claude-code-background-lab-case', 'feishu-dual-instance-case',
    'kef-lsx-volume-case',
})
NOT_A_TASK = frozenset({
    'rea-touhou-reconstruction-method-case', 'agent-decompilation-oracle-case',
    'noflag-rea-evidence-architecture-study', 'rea-claude-code-isolated-ab-case',
})
TARGET = 1000
FAMILIES = (
    ('game', 'Game', '游戏'),
    ('app', 'App', '应用'),
    ('protocol', 'Protocol', '协议'),
    ('firmware', 'Firmware', '固件'),
    ('website', 'Website', '网站'),
    ('binary', 'Binary', '二进制'),
)
FILLED = ('#3c348c', '#5b4ad4', '#7d6ee6', '#b7adf6')
EMPTY = '#f3f4f8'
EMPTY_EDGE = '#e4e6ee'
COPY = {
    'en': {
        'title': 'Benchmark map',
        'description': 'Coverage of concrete input-to-output tasks across website, game, app, binary, firmware and protocol, against a target of 1,000.',
        'lede': 'Each cell is one slot toward 1,000 concrete tasks. A task is a curated case with a shipped input and a checkable output, large enough for a computer-use session past three hours. Purple cells are filled. Gray cells are still open. The six targets share the target evenly, so a thin target stays visible.',
        'aside': 'Shorter cases and essays stay outside this map. Tools, papers and unreviewed leads are not tasks. The three-hour line is a scope reading, not a measured run.',
        'table': 'Long tasks by target',
        'target': 'Target',
        'filled': 'Long tasks',
        'slots': 'Slots',
        'home': 'Home',
        'resources': 'Curated resources',
        'cases': 'Case studies',
        'skip': 'Skip to the map',
        'nav': 'Main navigation',
        'crumb': 'Breadcrumb',
        'alt': 'Benchmark map. Purple cells are long tasks and gray cells are still open. Six targets share 1,000 slots.',
    },
    'zh': {
        'title': '基准图',
        'description': '网站、游戏、应用、二进制、固件和协议六类具体任务的覆盖，目标是 1,000。',
        'lede': '每一格是走向 1,000 条具体任务的一个位置。一条任务是精选案例：有已发布的输入，也有可检查的输出，并且规模足够一次超过三小时的计算机使用会话。紫色是已覆盖，灰色还空着。六个目标平分这 1,000，所以薄弱的目标仍然看得见。',
        'aside': '较短案例和综述不在这张图里。工具、论文和未审线索不是任务。三小时是对范围的判断，不是实测时长。',
        'table': '各目标的长任务',
        'target': '目标',
        'filled': '长任务',
        'slots': '位置',
        'home': '首页',
        'resources': '精选资源',
        'cases': '案例合集',
        'skip': '跳到图',
        'nav': '主导航',
        'crumb': '当前位置',
        'alt': '基准图。紫色是长任务，灰色还空着。六个目标平分 1,000 个位置。',
    },
}


def catalog_cases():
    records = []
    for name in ('data/rea-resources.json', 'data/tool-resources.json'):
        records.extend(json.loads((ROOT / name).read_text(encoding='utf-8')))
    return [record for record in records if record.get('kind') == 'case-study']


def family_slots():
    """Split the 1,000-task target across the six families. Earlier families take the remainder."""
    base, remainder = divmod(TARGET, len(FAMILIES))
    return {key: base + (1 if index < remainder else 0) for index, (key, _, _) in enumerate(FAMILIES)}


def long_by_family(cases=None):
    cases = catalog_cases() if cases is None else cases
    grouped = {key: [] for key, _, _ in FAMILIES}
    for record in cases:
        if record['id'] in SHORT or record['id'] in NOT_A_TASK:
            continue
        primary = (record.get('targets') or ['binary'])[0]
        if primary not in grouped:
            raise ValueError('Long task has no benchmark-map family: ' + record['id'])
        grouped[primary].append(record)
    for records in grouped.values():
        records.sort(key=lambda record: record['id'])
    return grouped


def render_svg(grouped=None, slots=None):
    grouped = long_by_family() if grouped is None else grouped
    slots = family_slots() if slots is None else slots
    columns = 24
    cell, gap = 10, 2
    step = cell + gap
    block_w = columns * step
    gutter, margin = 24, 24
    label_h, legend_h = 36, 46
    per_row = 3
    max_rows = max(ceil(slots[key] / columns) for key, _, _ in FAMILIES)
    block_h = label_h + max_rows * step
    width = margin * 2 + per_row * block_w + (per_row - 1) * gutter
    height = margin + legend_h + 2 * block_h + gutter + 52
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        '<title>Benchmark map of long input-to-output tasks</title>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{margin}" y="{margin + 16}" fill="#202335" font-family="ui-sans-serif,sans-serif" font-size="16" font-weight="650">Benchmark map</text>',
        f'<rect x="{margin + 176}" y="{margin + 5}" width="14" height="14" rx="2" fill="{FILLED[1]}"/>',
        f'<text x="{margin + 196}" y="{margin + 16}" fill="#525b6d" font-family="ui-sans-serif,sans-serif" font-size="13">Long task</text>',
        f'<rect x="{margin + 286}" y="{margin + 5}" width="14" height="14" rx="2" fill="{EMPTY}" stroke="{EMPTY_EDGE}"/>',
        f'<text x="{margin + 306}" y="{margin + 16}" fill="#525b6d" font-family="ui-sans-serif,sans-serif" font-size="13">Still open</text>',
    ]
    total_long = 0
    for index, (key, english, chinese) in enumerate(FAMILIES):
        column, row = index % per_row, index // per_row
        origin_x = margin + column * (block_w + gutter)
        origin_y = margin + legend_h + row * (block_h + gutter)
        filled = grouped.get(key, [])
        capacity = slots[key]
        if len(filled) > capacity:
            raise ValueError(f'{key} has more long tasks than map slots')
        total_long += len(filled)
        parts.append(
            f'<text x="{origin_x}" y="{origin_y + 16}" fill="#202335" font-family="ui-sans-serif,sans-serif" font-size="14" font-weight="650">{xml_escape(english)} · {xml_escape(chinese)}</text>'
            f'<text x="{origin_x + block_w}" y="{origin_y + 16}" fill="#525b6d" font-family="ui-sans-serif,sans-serif" font-size="13" text-anchor="end">{len(filled)}/{capacity}</text>'
        )
        for slot in range(capacity):
            x = origin_x + (slot % columns) * step
            y = origin_y + label_h + (slot // columns) * step
            if slot < len(filled):
                record = filled[slot]
                color = FILLED[slot % len(FILLED)]
                parts.append(
                    f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{color}">'
                    f'<title>{xml_escape(record["name"])}</title></rect>'
                )
            else:
                parts.append(
                    f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{EMPTY}" stroke="{EMPTY_EDGE}" stroke-width="0.8"/>'
                )
    parts.append(
        f'<text x="{margin}" y="{height - 28}" fill="#525b6d" font-family="ui-sans-serif,sans-serif" font-size="13">'
        f'{total_long} of {TARGET:,} slots have a long task. Six targets share those slots evenly.</text>'
        f'<text x="{margin}" y="{height - 10}" fill="#525b6d" font-family="ui-sans-serif,sans-serif" font-size="13">'
        f'{TARGET:,} 个位置里已有 {total_long} 条长任务。六个目标平分这些位置。</text>'
    )
    parts.append('</svg>')
    return ''.join(parts) + '\n'


def _jsonld(value):
    payload = json.dumps(value, ensure_ascii=False, separators=(',', ':'))
    for character, encoded in (('&', '\\u0026'), ('<', '\\u003c'), ('>', '\\u003e')):
        payload = payload.replace(character, encoded)
    return f'<script type="application/ld+json">{payload}</script>'


def render_page(language, grouped, slots):
    text = COPY[language]
    zh = language == 'zh'
    path = ('/zh' if zh else '') + '/benchmark-map/'
    canonical = SITE + path
    locale = 'zh-CN' if zh else 'en'
    prefix = '/zh' if zh else ''
    counterpart = ('/benchmark-map/' if zh else '/zh/benchmark-map/')
    title = text['title'] + ' · AwesomeREA.org'
    rows = ''.join(
        f'<tr><td>{escape(english if not zh else chinese)}</td><td>{len(grouped[key])}</td><td>{slots[key]}</td></tr>'
        for key, english, chinese in FAMILIES
    )
    total = sum(len(grouped[key]) for key, _, _ in FAMILIES)
    schema = {'@context': 'https://schema.org', '@graph': [{
        '@type': 'WebPage', '@id': canonical + '#page', 'url': canonical, 'name': text['title'],
        'description': text['description'], 'inLanguage': locale, 'isPartOf': website_reference(SITE),
    }]}
    social = open_graph_meta(language=language, title=title, description=text['description'],
                             image_url=SITE + '/social-card.png', url=canonical)
    return f'''<!doctype html>
<html lang="{locale}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#ffffff">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(text['description'], quote=True)}">
  <link rel="canonical" href="{canonical}">
  <link rel="alternate" hreflang="en" href="{SITE}/benchmark-map/">
  <link rel="alternate" hreflang="zh-CN" href="{SITE}/zh/benchmark-map/">
  <link rel="alternate" hreflang="x-default" href="{SITE}/benchmark-map/">
  {social}
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="/styles.css">
  <link rel="stylesheet" href="/benchmark-map.css">
  {_jsonld(schema)}
</head>
<body>
<a class="skip-link" href="#map">{escape(text['skip'])}</a>
<header class="site-header"><div class="shell header-inner">
  <a class="wordmark" href="{prefix or '/'}"><img class="brand-mark" src="/favicon.svg" alt="" width="33" height="33"><span>Awesome<span class="wordmark-rea">REA</span><span class="wordmark-domain">.org</span></span></a>
  <nav class="header-nav" aria-label="{escape(text['nav'])}">
    <a class="github-link" href="{counterpart}" lang="{'en' if zh else 'zh-CN'}" hreflang="{'en' if zh else 'zh-CN'}">{'English' if zh else '简体中文'}</a>
    <a class="github-link" href="https://github.com/reacher-z/Awesome-REA">GitHub</a>
  </nav>
</div></header>
<main class="shell benchmark-page" id="map">
  <nav class="browse-breadcrumbs" aria-label="{escape(text['crumb'])}"><a href="{prefix or '/'}">{escape(text['home'])}</a><span aria-hidden="true">/</span><span aria-current="page">{escape(text['title'])}</span></nav>
  <p class="eyebrow">COVERAGE</p>
  <h1>{escape(text['title'])}</h1>
  <p>{escape(text['lede'])}</p>
  <img src="/benchmark-map.svg" alt="{escape(text['alt'], quote=True)}" width="960">
  <p>{escape(text['aside'])}</p>
  <table class="benchmark-table">
    <caption>{escape(text['table'])}</caption>
    <thead><tr><th scope="col">{escape(text['target'])}</th><th scope="col">{escape(text['filled'])}</th><th scope="col">{escape(text['slots'])}</th></tr></thead>
    <tbody>{rows}<tr><th scope="row">{escape('Total' if not zh else '合计')}</th><td>{total}</td><td>{TARGET:,}</td></tr></tbody>
  </table>
  <p class="benchmark-links"><a href="{prefix}/resources/">{escape(text['resources'])}</a> · <a href="{prefix}/cases/">{escape(text['cases'])}</a></p>
</main>
</body>
</html>
'''


def write_maps():
    grouped, slots = long_by_family(), family_slots()
    svg = render_svg(grouped, slots)
    (ROOT / 'assets').mkdir(exist_ok=True)
    (ROOT / 'assets' / 'benchmark-map.svg').write_text(svg, encoding='utf-8')
    (ROOT / 'site' / 'benchmark-map.svg').write_text(svg, encoding='utf-8')
    for language, relative in (('en', 'site/benchmark-map/index.html'), ('zh', 'site/zh/benchmark-map/index.html')):
        destination = ROOT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(render_page(language, grouped, slots), encoding='utf-8')
    return svg


if __name__ == '__main__':
    write_maps()
    print('Wrote benchmark map')
