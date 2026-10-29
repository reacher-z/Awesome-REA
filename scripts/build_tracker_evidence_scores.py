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
<title>rea-tracker 条目证据强度分</title>
<style>
:root { color-scheme: light dark; }
body { font-family: -apple-system, "PingFang SC", "Segoe UI", sans-serif; margin: 0; padding: 1.5rem; }
h1 { font-size: 1.3rem; margin: 0 0 .5rem; }
p.lede { color: #555; max-width: 72ch; margin: .25rem 0 1rem; }
.controls { display: flex; flex-wrap: wrap; gap: .5rem; margin-bottom: .75rem; }
.controls select, .controls input { font: inherit; padding: .3rem .5rem; }
table { border-collapse: collapse; width: 100%; font-size: .85rem; }
th, td { text-align: left; padding: .35rem .5rem; border-bottom: 1px solid rgba(128,128,128,.25); vertical-align: top; }
th { position: sticky; top: 0; background: #f6f6f6; cursor: pointer; white-space: nowrap; }
@media (prefers-color-scheme: dark) { th { background: #222; } }
td.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.badge { display: inline-block; border-radius: .6rem; padding: .05rem .5rem; font-size: .75rem; border: 1px solid currentColor; }
.c0 { color: #0b62a4; } .c1 { color: #3f83b8; } .c2 { color: #7a7a7a; } .c3 { color: #9a6a2f; } .cr { color: #888; }
.meta { color: #777; font-size: .8rem; }
footer { margin-top: 1.5rem; font-size: .8rem; color: #777; max-width: 80ch; }
</style>
</head>
<body>
<h1>rea-tracker 条目证据强度分（__SPEC__）</h1>
<p class="lede">分数只衡量<b>公开证据强度</b>（demo 证据、获取入口、macOS 包、人工复核等），
在同一 Class 内部排序；<b>不是复现完成度分</b>。类别（Class 0–3 / 资源附录）始终以 tracker 原分类为准。
跨 Class 的分差反映证据档位，不代表完成度差距；资源附录不与实体比较。</p>
<div class="controls">
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
<table id="tbl"><thead><tr>
  <th data-k="score">分数</th><th data-k="tracker_class">类别</th><th data-k="name">条目</th>
  <th data-k="macos_status">macOS</th><th data-k="media_count">demo</th><th data-k="scope">scope</th>
</tr></thead><tbody></tbody></table>
<footer>数据：rea-tracker <code>taxonomy.html</code> 快照（__GENERATED__ 生成，上游 Awesome-REA <code>__AWESOME__</code>）。
评分口径见 <code>docs/eval-platform-scores.zh-CN.md</code>。所有条目仅公开证据初筛，未安装、启动或验证；Class 0 亦非验收认证。</footer>
<script>
const DATA = __DATA__;
const rows = DATA.records.map(r => ({...r, resource: r.scope === 'resource'}));
const badge = r => r.resource ? '<span class="badge cr">附录</span>'
  : `<span class="badge c${r.tracker_class}">C${r.tracker_class}</span>`;
const state = { k: 'score', asc: false };
function apply() {
  const cls = document.getElementById('f-class').value;
  const mac = document.getElementById('f-macos').value;
  const q = document.getElementById('f-q').value.trim().toLowerCase();
  let out = rows.filter(r =>
    (!cls || (cls === 'r' ? r.resource : String(r.tracker_class) === cls && !r.resource)) &&
    (!mac || r.macos_status === mac) &&
    (!q || (r.name + ' ' + r.id).toLowerCase().includes(q)));
  const k = state.k;
  out.sort((a, b) => {
    const va = a[k] ?? '', vb = b[k] ?? '';
    const c = typeof va === 'number' && typeof vb === 'number' ? va - vb : String(va).localeCompare(String(vb));
    return state.asc ? c : -c;
  });
  const tb = document.querySelector('#tbl tbody');
  tb.innerHTML = out.map(r => `<tr>
    <td class="num">${r.score.toFixed(2)}</td><td>${badge(r)}</td>
    <td><a href="${r.url}" target="_blank" rel="noopener">${r.name}</a><br><span class="meta">${r.id}</span></td>
    <td class="meta">${r.macos_status || '—'}</td><td class="num">${r.media_count || 0}</td>
    <td class="meta">${r.scope}</td></tr>`).join('');
  document.getElementById('count').textContent = `${out.length} / ${rows.length} 条`;
}
document.querySelectorAll('#tbl th').forEach(th => th.addEventListener('click', () => {
  const k = th.dataset.k;
  state.asc = state.k === k ? !state.asc : false;
  state.k = k; apply();
}));
['f-class', 'f-macos'].forEach(id => document.getElementById(id).addEventListener('change', apply));
document.getElementById('f-q').addEventListener('input', apply);
apply();
</script>
</body>
</html>
"""


def write_html(rows, meta, path):
    awesome_commit = next((s.get('commit', '') for s in meta.get('tracker_sources', [])
                           if s.get('id') == 'awesome'), '')
    html = (HTML_TEMPLATE
            .replace('__SPEC__', SCORE_SPEC_VERSION)
            .replace('__GENERATED__', meta['generated_at'][:10])
            .replace('__AWESOME__', awesome_commit[:12] or 'unknown')
            .replace('__DATA__', json.dumps({'records': [
                {k: row[k] for k in ('id', 'name', 'url', 'scope', 'tracker_class', 'score',
                                     'macos_status', 'media_count')} for row in rows
                if row['scope'] != 'resource']}, ensure_ascii=False)))
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
