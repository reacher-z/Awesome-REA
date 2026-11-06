#!/usr/bin/env python3
"""Refresh the case ledger's derived counts and render its short bilingual summaries."""
import argparse
import json
from pathlib import Path
import sys

from case_coverage import coverage_counts, read_case_coverage, validate_case_coverage
from artifact_links import github_repository
from validate import public_https_error

ROOT = Path(__file__).resolve().parents[1]


def linked_repository_count(entries):
    """Count normalized repository links without merging occurrence identities."""
    return len({repository for entry in entries for url in entry['reported_source_urls']
                if (repository := github_repository(url, artifact=True))})


def render(document, resources, translations, zh=False):
    label = lambda en, cn: cn if zh else en
    c = document['counts']
    lines = [label('# Case collection coverage', '# 案例合集覆盖记录'), '',
             label('[简体中文](case-coverage.zh-CN.md) · [Machine-readable ledger](../data/case-coverage.json)',
                   '[English](case-coverage.md) · [机器可读记录](../data/case-coverage.json)'), '',
             label(f"Reviewed {document['reviewed_at']} (UTC). **{c['occurrences']} collection occurrences** become **{c['inventory_units']} inventory units** after {c['alias_merges']} documented duplicate merges. These are reports, tools, papers, discussions and ideas.",
                   f"核查日期：{document['reviewed_at']}（UTC）。**{c['occurrences']} 个合集出现项**经 {c['alias_merges']} 次有记录的重复合并后，对应 **{c['inventory_units']} 个清单单元**。其中包括报告、工具、论文、讨论和想法。"), '',
             label('The unique-project count is `null` until project identities are resolved. English/Chinese copies of one upstream entry are counted once. Separate reports about one project remain separate units unless an explicit alias decision joins them.',
                   '项目身份归并完成前，独立项目数为 `null`。同一上游条目的中英文版本只计一次。同一项目的不同报告仍分别计为清单单元，除非已有明确的别名合并决定。'), '',
             label('## Frozen sources', '## 固定来源'), '',
             label('| Collection snapshot | Occurrences | Linked GitHub repositories | Catalog record |', '| 合集快照 | 出现项 | 链接的 GitHub 仓库 | 目录记录 |'), '| --- | ---: | ---: | --- |']
    for source in document['collections']:
        name = source['repository_url'].removeprefix('https://github.com/')
        link = source['repository_url'] + '/tree/' + source['commit']
        destination = ('/zh' if zh else '') + '/resources/' + source['catalog_resource_id'] + '/'
        repository_count = linked_repository_count(entry for entry in document['entries']
                                                   if entry['collection_id'] == source['id'])
        lines.append(f"| [{name} · {source['commit'][:12]}]({link}) | {source['entry_count']} | {repository_count} | [{source['catalog_resource_id']}](https://awesomerea.org{destination}) |")
    lines += ['', label('The ledger retains pinned file URLs, Git blob IDs, SHA-256 digests and byte counts for these enumerated snapshots.',
                        '记录保留固定版本文件 URL、Git blob 标识、SHA-256 和字节数，描述这些已清点快照。'), '',
              label('Repository counts use normalized GitHub repository, tree and file links within each collection. In a game-organized table, each project row is an occurrence.',
                    '仓库数按每个合集中的 GitHub 仓库、目录及文件链接规范化后计数。在按游戏组织的表格中，每个项目行是一个出现项。'), '',
              label('## Counts and states', '## 数量与状态'), '',
              label('| State | Occurrences | Inventory units | Meaning |', '| 状态 | 出现项 | 清单单元 | 含义 |'), '| --- | ---: | ---: | --- |']
    state_labels = {
        'already-curated': ('Already curated', '已收录', 'Full-scope identity mapping to a catalog resource or paper.', '完整范围已对应目录资源或论文。'),
        'pending': ('Pending', '待核查', 'Primary review or complete catalog coverage remains pending; partial matches stay here.', '一手核查或完整目录覆盖尚待完成；部分映射也保留在此状态。'),
        'insufficient-evidence': ('Insufficient evidence', '证据不足', 'An idea, request or unsupported reconstruction claim is retained as a lead.', '将想法、请求或尚缺支持的重建说法保留为线索。'),
    }
    for state, values in state_labels.items():
        lines.append(f"| {values[zh]} (`{state}`) | {c['occurrences_by_state'].get(state, 0)} | {c['units_by_state'].get(state, 0)} | {values[2 + zh]} |")
    lines += ['', label(f"{c['catalog_linked_occurrences']} occurrences have catalog links. They reference {c['distinct_resource_ids']} distinct resource IDs and {c['distinct_paper_ids']} paper ID. Match scope is recorded separately.",
                        f"{c['catalog_linked_occurrences']} 个出现项含目录链接；共关联 {c['distinct_resource_ids']} 个不同资源 ID 和 {c['distinct_paper_ids']} 个论文 ID。映射范围单独记录。"), '',
              label(f"This ledger records a new primary-source review for {c['primary_reviewed_units']} inventory units. Other catalog-linked entries inherit the catalog’s source-review record.",
                    f"此记录为 {c['primary_reviewed_units']} 个清单单元记载了新的一手来源核查。其他已有目录链接的条目沿用目录中的来源核查记录。"), '',
              label('## Primary-reviewed cases', '## 本轮一手核查案例'), '',
              label('| Case | State | Primary evidence |', '| 案例 | 状态 | 一手证据 |'), '| --- | --- | --- |']
    seen = set()
    for entry in document['entries']:
        if entry['review_level'] != 'primary-source-reviewed' or entry['unit_id'] in seen:
            continue
        seen.add(entry['unit_id'])
        match = next((m for m in entry['catalog_matches'] if m['catalog'] == 'resource' and m['scope'] == 'full'), None)
        record = resources.get(match['id']) if match else None
        name = (translations.get(record['id'], {}).get('name', record['name']) if zh else record['name']) if record else entry['title']
        name = name.replace('|', '\\|').replace('\n', ' ')
        lines.append(f"| {name} | {state_labels[entry['state']][zh]} | [{label('Source', '来源')}]({entry['primary_evidence_urls'][0]}) |")
    lines += ['', label('## Partial coverage and aliases', '## 部分覆盖与别名'), '']
    partial = [entry for entry in document['entries']
               if any(match['scope'] in {'partial', 'related'} for match in entry['catalog_matches'])]
    if partial:
        lines += [label('Partial or related catalog mappings:', '部分或相关目录映射：'), '']
        for entry in partial:
            reason = entry['reason_zh' if zh else 'reason_en'].replace('\n', ' ')
            lines.append(f"- `{entry['id']}` — {reason}")
    else:
        lines.append(label('No partial catalog mappings are recorded.', '当前没有部分目录映射。'))
    lines += ['', label('Alias decisions:', '别名决定：'), '']
    if document['aliases']:
        for alias in document['aliases']:
            members = ', '.join('`' + identifier + '`' for identifier in alias['occurrence_ids'])
            basis = alias['basis_zh' if zh else 'basis_en'].replace('\n', ' ')
            lines.append(f"- {members} → `{alias['unit_id']}` — {basis}")
    else:
        lines.append(label('No alias merges are recorded.', '当前没有别名合并。'))
    lines += ['', label('## Updating this ledger', '## 更新此记录'), '',
              label('Review the pinned collection entry and its primary evidence before changing a state. Keep occurrence IDs stable, record explicit aliases, use typed full/partial/related catalog mappings, and leave unresolved project counts unknown.',
                    '改变状态前应核查固定版本合集条目及其一手证据。保持出现项 ID 稳定，明确记录别名，使用带类型的完整／部分／相关目录映射，并将尚未解决的项目数量保持为未知。'), '',
              '```sh', 'python3 scripts/build_case_coverage.py', 'python3 scripts/validate.py', 'python3 -m unittest discover -s tests -v', '```', '',
              label('The validator checks schemas, public URLs, pinned receipts, identifiers, aliases, catalog mappings and derived counts.',
                    '校验器检查结构、公开 URL、固定版本收据、标识、别名、目录映射和派生数量。'), '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    records = [row for filename in ('rea-resources.json', 'tool-resources.json')
               for row in json.loads((ROOT / 'data' / filename).read_text(encoding='utf-8'))]
    papers = json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))
    ledger = ROOT / 'data/case-coverage.json'
    stored = read_case_coverage(ROOT)
    document = stored
    try:
        document = {**stored, 'counts': coverage_counts(stored['entries'])}
    except (AttributeError, KeyError, TypeError):
        pass  # Malformed entries keep their stored counts; validation below reports them.
    errors = []
    validate_case_coverage(document, records, papers, errors, url_check=public_https_error)
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    translations = json.loads((ROOT / 'site/translations.zh-CN.json').read_text(encoding='utf-8'))
    resources = {row['id']: row for row in records}
    stale = []
    # Serialized comparison also treats a stored boolean count as stale; key order is ignored.
    if json.dumps(stored.get('counts'), sort_keys=True) != json.dumps(document['counts'], sort_keys=True):
        stale.append((ledger, json.dumps(document, indent=2, ensure_ascii=False) + '\n'))
    for suffix, zh in (('', False), ('.zh-CN', True)):
        path = ROOT / ('docs/case-coverage' + suffix + '.md')
        expected = render(document, resources, translations, zh)
        if not path.exists() or path.read_text(encoding='utf-8') != expected:
            stale.append((path, expected))
    if args.check and stale:
        print('Case coverage files need regeneration with python3 scripts/build_case_coverage.py: '
              + ', '.join(path.name for path, _ in stale), file=sys.stderr)
        return 1
    for path, expected in stale:
        path.write_text(expected, encoding='utf-8')
    print('Checked case coverage counts and summaries.' if args.check
          else 'Refreshed case coverage counts and generated bilingual summaries.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
