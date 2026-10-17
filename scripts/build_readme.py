#!/usr/bin/env python3
"""Render readable resource entries and research papers into both READMEs."""
import argparse
import html
import json
import sys
from collections import defaultdict

from catalog import ROOT, load_resources
from validate_papers import read_papers


BEGIN = '<!-- BEGIN GENERATED CATALOG -->'
END = '<!-- END GENERATED CATALOG -->'
PAPERS_BEGIN = '<!-- BEGIN GENERATED PAPERS -->'
PAPERS_END = '<!-- END GENERATED PAPERS -->'
CATEGORIES = {
    'core': ('Official REA: core and setup', 'REA 官方：核心与配置'),
    'workflow-guides': ('Official REA: investigation guides', 'REA 官方：调查指南'),
    'official-case-studies': ('Official REA: case studies', 'REA 官方：案例'),
    'community-integrations': ('Community REA integrations', 'REA 社区集成'),
    'community-labs': ('Community REA labs', 'REA 社区练习'),
    'community-case-studies': ('Community REA investigations', 'REA 社区调查案例'),
    'reconstruction-cases': ('Independent reconstruction cases', '独立重建案例'),
    'agent-mcp': ('Independent MCP integrations', '独立 MCP 集成'),
    'agent-workflows': ('Independent agent workflows', '独立 Agent 工作流'),
    'game-analysis': ('Game analysis tools', '游戏分析工具'),
    'web-analysis': ('Website analysis tools', '网站分析工具'),
    'protocol-analysis': ('Protocol analysis tools', '协议分析工具'),
    'native-analysis': ('Native analysis tools', '原生分析工具'),
    'dynamic-analysis': ('Debugging and dynamic analysis', '调试与动态分析'),
    'android': ('Android tools', 'Android 工具'),
    'dotnet': ('.NET tools', '.NET 工具'),
    'jvm': ('JVM bytecode tools', 'JVM 字节码工具'),
    'javascript-electron': ('JavaScript and Electron tools', 'JavaScript 与 Electron 工具'),
    'webassembly': ('WebAssembly tools', 'WebAssembly 工具'),
    'firmware': ('Firmware tools', '固件工具'),
    'binary-libraries': ('Binary analysis libraries', '二进制分析库'),
    'binary-diffing': ('Binary comparison tools', '二进制对比工具'),
    'learning': ('Learning resources', '学习资源'),
    'related-lists': ('Related resource lists', '相关资源目录'),
}
RELATIONSHIPS = {
    'official-core': ('Official REA project', 'REA 官方项目'),
    'official-skill': ('Official REA skill', 'REA 官方技能'),
    'official-documentation': ('Official REA documentation', 'REA 官方文档'),
    'official-guide': ('Official REA guide', 'REA 官方指南'),
    'official-case-study': ('Official REA case study', 'REA 官方案例'),
    'community-integration': ('Community REA integration', 'REA 社区集成'),
    'community-learning-resource': ('Community REA learning resource', 'REA 社区学习资源'),
    'community-reported-mixed-workflow': ('Author-reported mixed workflow', '作者报告的混合工具流程'),
    'upstream-maintainer-companion-list': ('REA maintainer companion list', 'REA 维护者的相关目录'),
    'independent-agent-integration': ('Independent agent integration', '独立 Agent 集成'),
    'independent-reconstruction': ('Independent reconstruction project', '独立重建项目'),
    'foundation': ('Foundation tool', '基础工具'),
    'learning': ('Learning resource', '学习资源'),
}
TARGETS = {
    'website': ('Website', '网站'),
    'game': ('Game', '游戏'),
    'app': ('App', '应用'),
    'binary': ('Binary', '二进制'),
    'firmware': ('Firmware', '固件'),
    'protocol': ('Protocol', '协议'),
}


def plain_text(value):
    """Keep contributed text on one line and avoid HTML or link-label markup."""
    text = html.escape(' '.join(value.split()), quote=False)
    return text.replace('\\', '\\\\').replace('[', '\\[').replace(']', '\\]')


def requirements_text(value):
    """Both supported source formats render as ordinary prose."""
    if isinstance(value, str):
        return plain_text(value)
    return plain_text(' '.join(value))


COLLECTION_SECTIONS = {
    'website': ('Website', 'Website · 网站'),
    'game': ('Game', 'Game · 游戏'),
    'app': ('App', 'App · 应用'),
    'native-binary': ('Native Binary', 'Native Binary · 原生二进制'),
    'firmware': ('Firmware and Hardware', 'Firmware · 固件与硬件'),
    'protocol': ('Protocols', 'Protocols · 协议'),
    'agents-and-mcp': ('Agents and MCP', 'Agents & MCP · Agent 与集成'),
    'related-collections': ('Related Collections', 'Related Collections · 相关合集'),
    'references-and-learning': ('References and Learning', 'References & Learning · 文档与学习资料'),
}
KIND_LABELS = {
    'project': ('Project', '项目'), 'tool': ('Tool', '工具'),
    'integration': ('Integration', '集成'), 'case-study': ('Case study', '案例'),
    'collection': ('Collection', '合集'), 'documentation': ('Documentation', '文档'),
    'learning-resource': ('Learning resource', '学习资料'), 'research': ('Research', '研究'),
}


def collection_section(record):
    """Each resource appears once, under its primary purpose rather than every target tag."""
    category, relationship = record['category'], record['relationship']
    kind = record.get('kind', '')
    if kind == 'collection' or category == 'related-lists':
        return 'related-collections'
    if kind in {'documentation', 'learning-resource', 'research'} or category in {'workflow-guides', 'learning', 'community-labs'} or relationship in {'official-documentation', 'official-guide'}:
        return 'references-and-learning'
    if record['id'] in {'chrome-devtools-mcp', 'playwright-mcp', 'webcrack'} or category in {'web-analysis', 'webassembly'}:
        return 'website'
    if record['id'] in {'renderdoc-mcp', 'rea-dxball-case', 'rea-th04-case'} or category == 'game-analysis':
        return 'game'
    if record['id'] in {'jadx-ai-mcp', 'frida-mcp-yfe404', 'super-trouper', 'frida', 'rea-aegis-case', 'rea-notion-case', 'nibkit'} or category in {'android', 'dotnet', 'jvm', 'javascript-electron'}:
        return 'app'
    if category == 'firmware' or record['id'] == 'picoprint-rea-investigation':
        return 'firmware'
    if category in {'core', 'agent-mcp', 'agent-workflows', 'community-integrations'}:
        return 'agents-and-mcp'
    if category == 'protocol-analysis':
        return 'protocol'
    if kind == 'case-study':
        # New community cases should follow their target, not silently become binaries.
        for target in ('website', 'game', 'app', 'firmware', 'protocol'):
            if target in record.get('targets', []):
                return target
    return 'native-binary'


def entry_type(record, language):
    index = 0 if language == 'en' else 1
    kind = record.get('kind', 'tool')
    if kind not in KIND_LABELS:
        raise ValueError(f'Unknown resource kind: {kind}')
    tags = [KIND_LABELS[kind][index]]
    relation, category = record['relationship'], record['category']
    if relation == 'independent-agent-integration':
        tags.append(('Independent MCP' if category == 'agent-mcp' else 'Independent agent') if language == 'en' else ('独立 MCP' if category == 'agent-mcp' else '独立 Agent'))
    elif relation.startswith('official-') or relation == 'community-integration':
        tags.append('REA')
    elif relation == 'community-reported-mixed-workflow':
        tags.append('Mixed workflow' if language == 'en' else '混合工具流程')
    elif relation == 'independent-reconstruction':
        tags.append('Independent reconstruction' if language == 'en' else '独立重建')
    elif category == 'android':
        tags.append('Android')
    elif category == 'dotnet':
        tags.append('.NET')
    elif category == 'jvm':
        tags.append('JVM')
    elif category == 'webassembly':
        tags.append('WebAssembly')
    elif category == 'binary-libraries':
        tags.append('Library' if language == 'en' else '程序库')
    return ' · '.join(tags)


def render_catalog(records, language, paper_urls=frozenset()):
    """One awesome-lint list item per resource; papers listed in the bibliography appear only there."""
    index = 0 if language == 'en' else 1
    translations = json.loads((ROOT / 'site/translations.zh-CN.json').read_text()) if language == 'zh' else {}
    groups = defaultdict(list)
    for record in records:
        if record['category'] not in CATEGORIES or record['relationship'] not in RELATIONSHIPS:
            raise ValueError(f"Unknown category or relationship for {record['id']}")
        if record['url'] in paper_urls:
            continue
        groups[collection_section(record)].append(record)
    lines = []
    for section, titles in COLLECTION_SECTIONS.items():
        if not groups[section]:
            continue
        contents = '[↑ Contents](#contents)' if language == 'en' else '[↑ 返回目录](#目录)'
        lines.extend([f'<a id="{section}"></a>', f'### {titles[index]}', '', contents, ''])
        for record in groups[section]:
            name = plain_text((record.get('name_zh') or translations.get(record['id'], {}).get('name') or record['name']) if language == 'zh' else record['name'])
            description = plain_text(record[f'description_{language}'])
            metadata = plain_text(entry_type(record, language))
            lines.append(f"- [**{name}**]({record['url']}) - {description} <sub>{metadata}</sub>")
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def replace_catalog(content, rendered):
    if content.count(BEGIN) != 1 or content.count(END) != 1:
        raise ValueError('Each README must contain exactly one BEGIN/END catalog marker pair')
    before, rest = content.split(BEGIN, 1)
    if END not in rest:
        raise ValueError('Catalog END marker must follow BEGIN')
    _, after = rest.split(END, 1)
    return before + BEGIN + '\n' + rendered + END + after


PAPER_SECTIONS = {
    'agent-evaluation': ('Reverse-engineering agent evaluation', '逆向工程智能体评测'),
    'decompilation': ('Decompilation and symbol recovery', '反编译与符号恢复'),
    'website-reconstruction': ('Website reconstruction', '网站重建'),
    'game-reconstruction': ('Game reconstruction and reverse engineering', '游戏重建与逆向工程'),
    'app-reconstruction': ('App reconstruction and analysis', '应用重建与分析'),
    'firmware-analysis': ('Firmware analysis and rehosting', '固件分析与重托管'),
    'protocol-analysis': ('Protocol inference and analysis', '协议推断与分析'),
}
PAPER_STATUSES = {
    'conference-paper': ('Conference paper', '会议论文'),
    'conference-accepted': ('Accepted', '已接收'),
    'journal-article': ('Journal article', '期刊论文'),
    'preprint': ('Preprint', '预印本'),
}
AGENT_EVALUATION_PAPERS = {
    'paper-crackmebench', 'paper-crebench', 'paper-sre-bench', 'paper-humans-machines-sre',
    'paper-programbench',
}


def render_papers(papers, language):
    zh = language == 'zh'
    index = int(zh)
    protocol_scope = ('协议推断、' if zh else 'protocol inference, ') if any('protocol' in paper['targets'] for paper in papers) else ''
    directory = 'https://awesomerea.org/zh/papers/' if zh else 'https://awesomerea.org/papers/'
    lines = ['<a id="papers"></a>', '## 论文' if zh else '## Papers', '',
             (f'收录 **{len(papers)} 篇论文**，涵盖逆向工程智能体评测、反编译、{protocol_scope}固件分析，以及网站、游戏和应用重建。部分论文也出现在精选资源目录中，两者数量不可相加。发表状态与研究范围分别标注，中文标题为译名。'
              if zh else f'A bibliography of **{len(papers)} papers** on reverse-engineering agent evaluation, decompilation, {protocol_scope}firmware analysis, and website, game, and app reconstruction. Some papers also appear among curated resources; counts are not additive. Publication status and study scope are made explicit.'), '',
             f"[{'浏览论文目录' if zh else 'Browse the paper directory'}]({directory}) · [{'完整书目 JSON' if zh else 'Complete bibliography JSON'}](data/papers.json) · [{'推荐论文' if zh else 'Suggest a paper'}](https://github.com/reacher-z/Awesome-REA/issues/new?template=paper.yml)", '']
    groups = defaultdict(list)
    for paper in papers:
        section = ('agent-evaluation' if paper['id'] in AGENT_EVALUATION_PAPERS else
                   {'website': 'website-reconstruction', 'game': 'game-reconstruction',
                    'app': 'app-reconstruction', 'firmware': 'firmware-analysis',
                    'protocol': 'protocol-analysis'}.get(paper['targets'][0], 'decompilation'))
        groups[section].append(paper)
    for section, labels in PAPER_SECTIONS.items():
        if not groups[section]:
            continue
        lines.extend(['### ' + labels[index], ''])
        for paper in sorted(groups[section], key=lambda item: (item['year'], item['publication_date'] or str(item['year']), item['title'].casefold()), reverse=True):
            title = plain_text(paper['title_zh'] if zh else paper['title'])
            status = PAPER_STATUSES[paper['publication_status']][index]
            metadata = plain_text(f"{paper['year']} · {paper['venue']} · {status}")
            author = plain_text(paper['authors'][0] + ((' 等' if zh else ' et al.') if len(paper['authors']) > 1 else ''))
            links = [f"[PDF]({paper['pdf_url']})"]
            if paper['code_url']:
                links.append(f"[{'代码' if zh else 'Code'}]({paper['code_url']})")
            lines.extend([
                f"- [{title}]({paper['url']}) - " + plain_text(paper[f'description_{language}'])
                + f" <sub>**{metadata}** · {author} · " + ' · '.join(links) + '</sub>', '',
                f"  <sub>**{'范围与限制' if zh else 'Scope and limits'}:** "
                + plain_text(paper[f'scope_limitations_{language}']) + '</sub>', '',
            ])
    return '\n'.join(lines).rstrip() + '\n'


def replace_papers(content, rendered, language):
    """Install the separate paper block once, then replace only its generated content."""
    if PAPERS_BEGIN not in content and PAPERS_END not in content:
        if content.count(END) != 1:
            raise ValueError('The paper section needs an existing catalog END marker')
        block = '\n\n' + PAPERS_BEGIN + '\n' + rendered + PAPERS_END
        content = content.replace(END, END + block, 1)
    else:
        if content.count(PAPERS_BEGIN) != 1 or content.count(PAPERS_END) != 1:
            raise ValueError('Each README must contain exactly one BEGIN/END paper marker pair')
        before, rest = content.split(PAPERS_BEGIN, 1)
        if PAPERS_END not in rest:
            raise ValueError('Paper END marker must follow BEGIN')
        _, after = rest.split(PAPERS_END, 1)
        content = before + PAPERS_BEGIN + '\n' + rendered + PAPERS_END + after
    label = '论文' if language == 'zh' else 'Papers'
    toc_entry = f'- [{label}](#papers)'
    if toc_entry not in content:
        reference_label = COLLECTION_SECTIONS['references-and-learning'][int(language == 'zh')]
        reference_entry = f'- [{reference_label}](#references-and-learning)'
        if content.count(reference_entry) != 1:
            raise ValueError('Cannot locate the references entry in the README table of contents')
        content = content.replace(reference_entry, reference_entry + '\n' + toc_entry, 1)
    if content.count(toc_entry) != 1:
        raise ValueError('README must contain one paper table-of-contents entry')
    return content


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Report stale generated blocks without writing files')
    args = parser.parse_args()
    try:
        records = load_resources()
        papers = read_papers(ROOT)
        stale = []
        for name, language in [('README.md', 'en'), ('README.zh-CN.md', 'zh')]:
            path = ROOT / name
            current = path.read_text(encoding='utf-8')
            expected = replace_catalog(current, render_catalog(records, language, {paper['url'] for paper in papers}))
            expected = replace_papers(expected, render_papers(papers, language), language)
            if current != expected:
                stale.append(name)
                if not args.check:
                    path.write_text(expected, encoding='utf-8')
        if args.check and stale:
            print('Stale generated catalog or paper section: ' + ', '.join(stale), file=sys.stderr)
            print('Run python3 scripts/build_readme.py', file=sys.stderr)
            return 1
        if args.check:
            print(f'Both READMEs match {len(records)} resources and {len(papers)} separate research papers.')
        else:
            print(f"Rendered {len(records)} resources and {len(papers)} separate research papers into both READMEs; updated {len(stale)} files.")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'Catalog generation failed: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
