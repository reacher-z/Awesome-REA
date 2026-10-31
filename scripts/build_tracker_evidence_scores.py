#!/usr/bin/env python3
"""Score rea-tracker taxonomy entities by public evidence strength.

Reads a local rea-tracker checkout (offline snapshot data, no network) and writes
a CSV, a JSON summary and a standalone HTML viewer under docs/scores/. The score
ranks evidence strength inside the tracker's own Class 0-3 tiers; it is not a
reproduction-completeness judgment. See docs/eval-platform-scores.zh-CN.md.
"""
import argparse
import csv
import datetime as dt
import json
import re
from pathlib import Path

SCORE_SPEC_VERSION = 'evidence-strength-v1'

CLASS_BASE = {0: 8.0, 1: 6.0, 2: 3.0, 3: 0.5}
CLASS_BAND = {0: (8.0, 10.0), 1: (6.0, 7.9), 2: (3.0, 5.9), 3: (0.5, 2.9)}
RESOURCE_BAND = (0.0, 0.4)
CLASS_LABELS = {
    0: 'Class 0 · 较完整复现候选',
    1: 'Class 1 · 通过初筛',
    2: '第二类 · 仓库证据不足',
    3: '第三类 · 笔记或局部实现',
}

FIDELITY_POSITIVE = {
    '有原版对照／互通记录': 'original-evidence',
    '包含内部一致性检查': 'internal-check',
}


def clamp(value, band):
    low, high = band
    return round(min(high, max(low, value)), 2)


def score_record(record, fidelity_signals):
    """Return (score, parts) for one audit record; class stays the primary tier."""
    scope = record.get('scope', 'resource')
    klass = record.get('class')
    parts = {}
    if scope == 'resource':
        score = clamp(0.1 if record.get('available', True) else 0.0, RESOURCE_BAND)
        parts['base'] = 'resource'
        return score, parts

    score = CLASS_BASE[klass]
    parts['base'] = f'class-{klass}'

    acquisition = record.get('acquisition') or []
    kinds = {entry.get('kind') for entry in acquisition if isinstance(entry, dict)}
    if any(entry.get('assets') for entry in acquisition if isinstance(entry, dict)):
        score += 1.0
        parts['acquisition'] = 'release-assets'
    elif kinds & {'release', 'download'}:
        score += 0.5
        parts['acquisition'] = 'entry-only'
    elif 'source-install' in kinds:
        score += 0.5
        parts['acquisition'] = 'source-install'

    macos = (record.get('macos') or {}).get('status')
    if macos == 'available':
        score += 0.5
        parts['macos'] = 'available'
    elif macos == 'ci':
        score += 0.25
        parts['macos'] = 'ci'

    if record.get('manual_review'):
        score += 0.5
        parts['manual-review'] = True

    if record.get('media'):
        score += 0.25
        parts['media'] = len(record['media'])

    positive = sorted({FIDELITY_POSITIVE[tag] for tag in fidelity_signals.get(record.get('id'), [])
                       if tag in FIDELITY_POSITIVE})
    if positive:
        score += 0.25 * len(positive)
        parts['fidelity'] = positive

    warnings = record.get('warnings') or []
    if warnings:
        score -= min(0.5, 0.25 * len(warnings))
        parts['warnings'] = len(warnings)
    if record.get('archived'):
        score -= 0.5
        parts['archived'] = True
    if record.get('available') is False:
        score -= 1.0
        parts['unavailable'] = True

    return clamp(score, CLASS_BAND[klass]), parts


def read_fidelity_signals(path):
    """Map tracker record IDs to documented doc-review signal tags (108-item snapshot)."""
    signals = {}
    if not path.exists():
        return signals
    with path.open(encoding='utf-8-sig', newline='') as stream:
        for row in csv.DictReader(stream):
            tags = [tag.strip() for tag in (row.get('信号（可重叠）') or '').split('|') if tag.strip()]
            if tags:
                signals[row.get('ID', '').strip()] = tags
    return signals


def build_rows(tracker_root):
    page = json.loads((tracker_root / 'data/taxonomy_page.json').read_text(encoding='utf-8'))
    fidelity = read_fidelity_signals(tracker_root / 'data/audit/fidelity/document_review.csv')
    manifest = json.loads((tracker_root / 'data/audit/source_manifest.json').read_text(encoding='utf-8'))
    rows = []
    for record in page['audit']['records']:
        score, parts = score_record(record, fidelity)
        macos = (record.get('macos') or {}).get('status') or ''
        rows.append({
            'id': record['id'],
            'name': record.get('name', ''),
            'url': record.get('url', ''),
            'scope': record.get('scope', ''),
            'tracker_class': record.get('class') if record.get('scope') != 'resource' else '',
            'class_label': CLASS_LABELS.get(record.get('class'), '') if record.get('scope') != 'resource' else '资源附录',
            'score': score,
            'macos_status': macos,
            'available': record.get('available', True),
            'archived': record.get('archived', False),
            'manual_review': bool(record.get('manual_review')),
            'media_count': len(record.get('media') or []),
            'fidelity_signals': '|'.join(FIDELITY_POSITIVE.get(tag, '') for tag in fidelity.get(record['id'], []) if tag in FIDELITY_POSITIVE),
            'parts': parts,
            'domain': record.get('domain', ''),
        })
    meta = {
        'spec_version': SCORE_SPEC_VERSION,
        'generated_at': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),
        'tracker_sources': manifest.get('sources', []),
        'tracker_page_generated_at': page.get('generated_at'),
        'tracker_audit_checked_at': page.get('audit', {}).get('checked_at'),
        'tracker_counts': page.get('audit', {}).get('counts'),
        'note': 'Scores rank public evidence strength within tracker classes; not a completeness judgment.',
    }
    return rows, meta


def write_csv(rows, path):
    fields = ['id', 'name', 'url', 'scope', 'tracker_class', 'class_label', 'score',
              'macos_status', 'available', 'archived', 'manual_review', 'media_count',
              'fidelity_signals', 'domain', 'parts']
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, 'parts': json.dumps(row['parts'], ensure_ascii=False, sort_keys=True)})


def write_json(rows, meta, path):
    slim_keys = ('id', 'name', 'url', 'scope', 'tracker_class', 'class_label', 'score',
                 'macos_status', 'available', 'archived', 'manual_review', 'media_count',
                 'fidelity_signals', 'domain')
    payload = {'meta': meta, 'records': [{key: row[key] for key in slim_keys} for row in rows]}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>rea-tracker 条目证据强度分 · 可视化</title>
<style>
.viz-root {
  color-scheme: light;
  --surface-1: #fcfcfb; --page: #f9f9f7;
  --ink: #0b0b0b; --ink-2: #52514e; --ink-muted: #898781;
  --grid: #e1e0d9; --axis: #c3c2b7; --ring: rgba(11,11,11,0.10);
  --s1: #2a78d6; --s2: #eb6834; --s3: #1baf7a; --s4: #eda100; --sx: #898781;
}
@media (prefers-color-scheme: dark) {
  :root:where(:not([data-theme="light"])) .viz-root {
    color-scheme: dark;
    --surface-1: #1a1a19; --page: #0d0d0d;
    --ink: #f0efec; --ink-2: #c3c2b7; --ink-muted: #898781;
    --grid: #2c2c2a; --axis: #383835; --ring: rgba(255,255,255,0.10);
    --s1: #3987e5; --s2: #d95926; --s3: #199e70; --s4: #c98500; --sx: #898781;
  }
}
:root[data-theme="dark"] .viz-root {
  color-scheme: dark;
  --surface-1: #1a1a19; --page: #0d0d0d;
  --ink: #f0efec; --ink-2: #c3c2b7; --ink-muted: #898781;
  --grid: #2c2c2a; --axis: #383835; --ring: rgba(255,255,255,0.10);
  --s1: #3987e5; --s2: #d95926; --s3: #199e70; --s4: #c98500; --sx: #898781;
}
body { font-family: system-ui, -apple-system, "PingFang SC", "Segoe UI", sans-serif;
       background: var(--page); color: var(--ink); margin: 0; }
.viz-root { max-width: 1000px; margin: 0 auto; padding: 1.5rem; }
h1 { font-size: 1.25rem; margin: 0; }
.lede { color: var(--ink-2); max-width: 74ch; font-size: .9rem; margin: .4rem 0 0; }
.bar-top { display: flex; justify-content: space-between; align-items: baseline; gap: 1rem; }
button.ghost { font: inherit; font-size: .8rem; color: var(--ink-2); background: transparent;
               border: 1px solid var(--ring); border-radius: 6px; padding: .25rem .6rem; cursor: pointer; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: .75rem; margin: 1.1rem 0; }
.tile { background: var(--surface-1); border: 1px solid var(--ring); border-radius: 10px; padding: .7rem .9rem; }
.tile b { display: block; font-size: 1.45rem; font-weight: 600; }
.tile span { color: var(--ink-2); font-size: .78rem; }
figure { background: var(--surface-1); border: 1px solid var(--ring); border-radius: 10px;
         margin: 1rem 0; padding: .9rem 1rem .6rem; }
figcaption { font-size: .88rem; font-weight: 600; margin-bottom: .15rem; }
figure .sub { color: var(--ink-muted); font-size: .75rem; margin-bottom: .5rem; }
svg text { font-family: inherit; }
.legend { display: flex; flex-wrap: wrap; gap: 1rem; margin: .5rem 0 .2rem; font-size: .78rem; color: var(--ink-2); }
.legend i { display: inline-block; width: 10px; height: 10px; border-radius: 3px; margin-right: 5px; }
#tip { position: fixed; pointer-events: none; z-index: 5; display: none;
       background: var(--surface-1); border: 1px solid var(--ring); border-radius: 6px;
       box-shadow: 0 2px 8px rgba(0,0,0,.18); padding: .35rem .55rem; font-size: .78rem; color: var(--ink); }
.controls { display: flex; flex-wrap: wrap; gap: .5rem; margin: .6rem 0; align-items: center; }
.controls select, .controls input { font: inherit; font-size: .85rem; padding: .28rem .5rem;
       background: var(--surface-1); color: var(--ink); border: 1px solid var(--ring); border-radius: 6px; }
table { border-collapse: collapse; width: 100%; font-size: .85rem; }
th, td { text-align: left; padding: .35rem .5rem; border-bottom: 1px solid var(--grid); vertical-align: top; }
th { position: sticky; top: 0; background: var(--surface-1); cursor: pointer; white-space: nowrap;
     color: var(--ink-2); font-weight: 600; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.badge { display: inline-block; border-radius: .6rem; padding: .05rem .5rem; font-size: .75rem; border: 1px solid currentColor; }
.meta { color: var(--ink-muted); font-size: .78rem; }
footer { margin-top: 1.4rem; font-size: .78rem; color: var(--ink-muted); max-width: 84ch; }
[hidden] { display: none !important; }
</style>
</head>
<body>
<div class="viz-root">
<div class="bar-top">
  <h1>rea-tracker 条目证据强度分（__SPEC__）</h1>
  <button class="ghost" id="theme">切换深浅</button>
</div>
<p class="lede">分数只衡量<b>公开证据强度</b>（demo 证据、获取入口、macOS 包、人工复核、文档二筛信号），
在同一 Class 内部排序；<b>不是复现完成度分</b>。类别以 tracker 原分类为准，跨档分差只反映证据档位；
资源附录（灰）不与实体比较。</p>
<div class="tiles" id="tiles"></div>
<figure>
  <figcaption>各类别分数分布</figcaption>
  <div class="sub">每格 0.5 分；虚线为档位边界（0.5 / 3 / 6 / 8）。悬停查看区间计数，峰值格直接标注。</div>
  <div id="dist"></div>
</figure>
<figure>
  <figcaption>macOS 发行包状态</figcaption>
  <div class="sub">仅 Class 0/1 共 118 项经过 macOS 包补查；其余类别该字段未查，记为空，不代表没有。</div>
  <div id="macos"></div>
</figure>
<figure>
  <figcaption>获取入口类型</figcaption>
  <div class="sub">主体 1,270 项中记录到获取入口的项目；「仅入口」指有下载或发布链接但未记录到产物文件。</div>
  <div id="acq"></div>
</figure>
<div class="controls" id="tbl-controls" hidden>
  <label>类别 <select id="f-class"><option value="">全部</option>
    <option value="0">Class 0</option><option value="1">Class 1</option>
    <option value="2">第二类</option><option value="3">第三类</option>
    <option value="r">资源附录</option></select></label>
  <label>macOS <select id="f-macos"><option value="">全部</option>
    <option value="available">有发布包</option><option value="ci">仅 CI 包</option>
    <option value="unconfirmed">未确认</option></select></label>
  <input id="f-q" type="search" placeholder="搜索名称或仓库…" style="min-width:14rem">
  <span class="meta" id="count"></span>
</div>
<div id="tbl-wrap" hidden><table id="tbl"><thead><tr>
  <th data-k="S" class="num">分数</th><th data-k="c">类别</th><th data-k="n">条目</th>
  <th data-k="m">macOS</th><th data-k="M" class="num">demo</th><th data-k="s">scope</th>
</tr></thead><tbody></tbody></table></div>
<p><button class="ghost" id="toggle">查看数据表</button></p>
<footer>数据：rea-tracker <code>taxonomy.html</code> 快照（__GENERATED__ 生成，上游 Awesome-REA <code>__AWESOME__</code>）。
评分口径见 <code>docs/eval-platform-scores.zh-CN.md</code>。所有条目仅公开证据初筛，未安装、启动或验证；Class 0 亦非验收认证。</footer>
</div>
<div id="tip"></div>
<script>
/*SCORER-START*/
const DATA = /*DATA-START*/__DATA__/*DATA-END*/;
const CLASSES = [
  { key: 0, label: 'Class 0 · 较完整复现候选', color: 'var(--s1)' },
  { key: 1, label: 'Class 1 · 通过初筛', color: 'var(--s2)' },
  { key: 2, label: '第二类 · 仓库证据不足', color: 'var(--s3)' },
  { key: 3, label: '第三类 · 笔记或局部实现', color: 'var(--s4)' },
  { key: 'r', label: '资源附录 · 不计入四类', color: 'var(--sx)' },
];
const rows = DATA.records;
const X0 = 96, X1 = 900, LO = 0, HI = 10;
const xw = v => X0 + (v - LO) / (HI - LO) * (X1 - X0);
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
function rrect(x, y, w, h, r) {
  r = Math.max(0, Math.min(r, w / 2, h / 2));
  return `M${x},${y} h${w - r} a${r},${r} 0 0 1 ${r},${r} v${h - 2 * r} a${r},${r} 0 0 1 ${-r},${-r} h${r - w} z`;
}
function histogram() {
  const bin = 0.5, nb = Math.round((HI - LO) / bin);
  const counts = CLASSES.map(() => new Array(nb).fill(0));
  for (const r of rows) {
    const k = r.s === 'resource' ? 'r' : r.c;
    const idx = CLASSES.findIndex(c => c.key === k);
    let b = Math.min(nb - 1, Math.max(0, Math.floor((r.S - LO) / bin)));
    counts[idx][b] += 1;
  }
  const rowH = 30, barH = 14, top = 8, height = top + rowH * CLASSES.length + 30;
  let svg = `<svg viewBox="-270 0 ${X1 + 20 + 270} ${height}" width="100%" role="img" aria-label="各类别分数分布直方图">`;
  for (let t = LO; t <= HI; t += 1) {
    const x = xw(t);
    svg += `<line x1="${x}" y1="${top}" x2="${x}" y2="${top + rowH * 5 + 4}" stroke="var(--grid)" stroke-width="1"/>`;
    svg += `<text x="${x}" y="${height - 8}" text-anchor="middle" font-size="10" fill="var(--ink-muted)">${t}</text>`;
  }
  for (const b of [0.5, 3, 6, 8]) {
    svg += `<line x1="${xw(b)}" y1="${top}" x2="${xw(b)}" y2="${top + rowH * 5 + 4}" stroke="var(--axis)" stroke-width="1" stroke-dasharray="3 3"/>`;
  }
  CLASSES.forEach((c, idx) => {
    const y = top + idx * rowH;
    const total = counts[idx].reduce((a, b) => a + b, 0);
    svg += `<text x="${X0 - 8}" y="${y + barH / 2 + 4}" text-anchor="end" font-size="11" fill="var(--ink-2)">${c.label}（${total}）</text>`;
    const arr = counts[idx];
    const peak = Math.max(...arr);
    arr.forEach((n, b) => {
      if (!n) return;
      const x = xw(LO + b * bin) + 1, w = xw(LO + (b + 1) * bin) - x - 1;
      const h = Math.max(2, barH * (n / peak));
      const yy = y + barH - h;
      svg += `<path d="${rrect(x, yy, w, h, 3)}" fill="${c.color}" class="hv" data-tip="${esc(LO + b * bin)}–${esc(LO + (b + 1) * bin)} 分：${n} 条"/>`;
      if (n === peak && peak > 0 && b < arr.length - 1) {
        const cx = Math.min(x + w / 2, X1 - 36);
        svg += `<text x="${cx}" y="${yy - 5}" text-anchor="middle" font-size="10" fill="var(--ink-muted)">峰值 ${n}</text>`;
      }
    });
  });
  svg += '</svg>';
  document.getElementById('dist').innerHTML = svg;
}
function macosChart() {
  const ent = rows.filter(r => r.s !== 'resource' && (r.c === 0 || r.c === 1));
  const counts = { available: 0, ci: 0, unconfirmed: 0 };
  for (const r of ent) counts[r.m] !== undefined && counts[r.m]++;
  const total = ent.length, barW = X1 - X0 - 60, y = 26, h = 26;
  const defs = [['有公开发布包', counts.available, 'var(--s1)'], ['仅 CI 包', counts.ci, 'var(--s2)'],
                ['未确认', counts.unconfirmed, 'var(--s3)']];
  let x = X0, svg = `<svg viewBox="0 0 ${X1 + 20} 96" width="100%" role="img" aria-label="macOS 发行包状态堆叠条">`;
  defs.forEach(([label, n, color]) => {
    const w = total ? (n / total) * barW : 0;
    if (w > 0) svg += `<path d="${rrect(x, y, Math.max(2, w - 2), h, 4)}" fill="${color}" class="hv" data-tip="${esc(label)}：${n} 项"/>`;
    if (w > 46) svg += `<text x="${x + (w - 2) / 2}" y="${y + h / 2 + 4}" text-anchor="middle" font-size="11" fill="#fff" style="paint-order:stroke">${n}</text>`;
    if (w > 0 && w <= 46) {
      svg += `<line x1="${x + w / 2}" y1="${y - 2}" x2="${x + w / 2}" y2="${y - 8}" stroke="var(--ink-muted)" stroke-width="1"/>`;
      svg += `<text x="${x + w / 2}" y="${y - 11}" text-anchor="middle" font-size="10" fill="var(--ink-2)">${label} ${n}</text>`;
    }
    x += w;
  });
  svg += `<line x1="${X0}" y1="${y + h + 4}" x2="${X0 + barW}" y2="${y + h + 4}" stroke="var(--axis)" stroke-width="1"/>`;
  svg += `<text x="${X0}" y="${y + h + 20}" font-size="10" fill="var(--ink-muted)">0</text>`;
  svg += `<text x="${X0 + barW}" y="${y + h + 20}" text-anchor="end" font-size="10" fill="var(--ink-muted)">${total} 项</text>`;
  svg += '</svg>';
  svg += `<div class="legend">` + defs.map(([label, n, color]) =>
    `<span><i style="background:${color}"></i>${label} ${n}</span>`).join('') + '</div>';
  document.getElementById('macos').innerHTML = svg;
}
function acqChart() {
  const counts = {};
  for (const r of rows) if (r.s !== 'resource' && r.a) counts[r.a] = (counts[r.a] || 0) + 1;
  const defs = [['release-assets', '发布包含产物文件', 'var(--s1)'],
                ['source-install', '仅源码安装说明', 'var(--s1)'],
                ['entry-only', '仅有下载／发布入口', 'var(--s1)']];
  const max = Math.max(...Object.values(counts), 1);
  const barW = X1 - X0 - 130, rowH = 30, h = 14;
  let svg = `<svg viewBox="0 0 ${X1 + 20} ${rowH * defs.length + 8}" width="100%" role="img" aria-label="获取入口类型条形图">`;
  defs.forEach(([key, label, color], idx) => {
    const n = counts[key] || 0, y = idx * rowH + 4;
    const w = (n / max) * barW;
    svg += `<text x="${X0 - 8}" y="${y + h / 2 + 4}" text-anchor="end" font-size="11" fill="var(--ink-2)">${label}</text>`;
    if (n > 0) svg += `<path d="${rrect(X0, y, Math.max(2, w), h, 4)}" fill="${color}" class="hv" data-tip="${esc(label)}：${n} 项"/>`;
    svg += `<text x="${X0 + w + 6}" y="${y + h / 2 + 4}" font-size="11" fill="var(--ink)">${n}</text>`;
  });
  svg += `<line x1="${X0}" y1="${rowH * defs.length + 2}" x2="${X0 + barW}" y2="${rowH * defs.length + 2}" stroke="var(--axis)" stroke-width="1"/>`;
  svg += '</svg>';
  document.getElementById('acq').innerHTML = svg;
}
function tiles() {
  const ent = rows.filter(r => r.s !== 'resource');
  const release = ent.filter(r => r.a === 'release-assets').length;
  const c01 = ent.filter(r => r.c === 0 || r.c === 1).length;
  const defs = [[rows.length, '条目总数（含附录）'], [ent.length, '主体实体'], [c01, 'Class 0 + Class 1'], [release, '带产物发布包']];
  document.getElementById('tiles').innerHTML = defs.map(([v, label]) =>
    `<div class="tile"><b>${v}</b><span>${label}</span></div>`).join('');
}
const tip = document.getElementById('tip');
document.addEventListener('mousemove', e => {
  const t = e.target.closest('.hv');
  if (t) {
    tip.textContent = t.dataset.tip;
    tip.style.display = 'block';
    tip.style.left = Math.min(window.innerWidth - 180, e.clientX + 14) + 'px';
    tip.style.top = (e.clientY + 16) + 'px';
  } else tip.style.display = 'none';
});
document.getElementById('theme').addEventListener('click', () => {
  const root = document.documentElement;
  const dark = matchMedia('(prefers-color-scheme: dark)').matches;
  const cur = root.dataset.theme || (dark ? 'dark' : 'light');
  root.dataset.theme = cur === 'dark' ? 'light' : 'dark';
});
if (location.hash === '#light' || location.hash === '#dark') {
  document.documentElement.dataset.theme = location.hash.slice(1);
}
const tblRows = rows.map(r => ({ ...r, resource: r.s === 'resource' }));
const badge = r => r.resource ? '<span class="badge" style="color:var(--sx)">附录</span>'
  : `<span class="badge" style="color:var(--s${r.c + 1})">C${r.c}</span>`;
const state = { k: 'S', asc: false };
function apply() {
  const cls = document.getElementById('f-class').value;
  const mac = document.getElementById('f-macos').value;
  const q = document.getElementById('f-q').value.trim().toLowerCase();
  let out = tblRows.filter(r =>
    (!cls || (cls === 'r' ? r.resource : String(r.c) === cls && !r.resource)) &&
    (!mac || r.m === mac) &&
    (!q || (r.n + ' ' + r.i).toLowerCase().includes(q)));
  const k = state.k;
  out.sort((a, b) => {
    const va = a[k] ?? '', vb = b[k] ?? '';
    const c = typeof va === 'number' && typeof vb === 'number' ? va - vb : String(va).localeCompare(String(vb));
    return state.asc ? c : -c;
  });
  document.querySelector('#tbl tbody').innerHTML = out.map(r => `<tr>
    <td class="num">${r.S.toFixed(2)}</td><td>${badge(r)}</td>
    <td><a href="${r.u}" target="_blank" rel="noopener">${esc(r.n)}</a><br><span class="meta">${esc(r.i)}</span></td>
    <td class="meta">${r.m || '—'}</td><td class="num">${r.M || 0}</td>
    <td class="meta">${esc(r.s)}</td></tr>`).join('');
  document.getElementById('count').textContent = `${out.length} / ${rows.length} 条`;
}
document.querySelectorAll('#tbl th').forEach(th => th.addEventListener('click', () => {
  const k = th.dataset.k;
  state.asc = state.k === k ? !state.asc : false;
  state.k = k; apply();
}));
['f-class', 'f-macos'].forEach(id => document.getElementById(id).addEventListener('change', apply));
document.getElementById('f-q').addEventListener('input', apply);
document.getElementById('toggle').addEventListener('click', () => {
  const show = document.getElementById('tbl-wrap').hidden;
  document.getElementById('tbl-wrap').hidden = !show;
  document.getElementById('tbl-controls').hidden = !show;
  document.getElementById('toggle').textContent = show ? '返回图表' : '查看数据表';
});
tiles(); histogram(); macosChart(); acqChart(); apply();
/*SCORER-END*/
</script>
</body>
</html>
"""


def write_html(rows, meta, path):
    awesome_commit = next((s.get('commit', '') for s in meta.get('tracker_sources', [])
                           if s.get('id') == 'awesome'), '')
    records = []
    for row in rows:
        parts = row['parts']
        records.append({
            'i': row['id'], 'n': row['name'], 'u': row['url'], 's': row['scope'],
            'c': row['tracker_class'], 'S': row['score'], 'm': row['macos_status'],
            'a': parts.get('acquisition', ''), 'M': row['media_count'],
            'f': len(parts.get('fidelity', [])), 'w': parts.get('warnings', 0),
            'v': row['available'], 'A': row['archived'],
        })
    payload = json.dumps({'records': records}, ensure_ascii=False,
                         separators=(',', ':')).replace('</', '<\\/')
    html = (HTML_TEMPLATE
            .replace('__SPEC__', SCORE_SPEC_VERSION)
            .replace('__GENERATED__', meta['generated_at'][:10])
            .replace('__AWESOME__', awesome_commit[:12] or 'unknown')
            .replace('/*DATA-START*/__DATA__/*DATA-END*/', payload))
    path.write_text(html, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tracker', type=Path, required=True,
                        help='Path to a local rea-tracker checkout')
    parser.add_argument('--out-dir', type=Path, default=Path(__file__).resolve().parents[1] / 'docs/scores')
    args = parser.parse_args()
    rows, meta = build_rows(args.tracker)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(rows, args.out_dir / 'tracker-evidence-scores.csv')
    write_json(rows, meta, args.out_dir / 'tracker-evidence-scores.json')
    write_html(rows, meta, args.out_dir / 'tracker-scores.html')
    classes = {}
    for row in rows:
        key = row['class_label'] or '资源附录'
        entry = classes.setdefault(key, {'count': 0, 'min': 10.0, 'max': 0.0})
        entry['count'] += 1
        entry['min'] = min(entry['min'], row['score'])
        entry['max'] = max(entry['max'], row['score'])
    print(f'wrote {len(rows)} rows to {args.out_dir}')
    for key, entry in sorted(classes.items()):
        print(f"  {key}: {entry['count']} rows, score {entry['min']:.2f}–{entry['max']:.2f}")


if __name__ == '__main__':
    main()
