#!/usr/bin/env python3
"""Render readable resource entries and research papers into both READMEs."""
import argparse
import html
import json
import re
import sys
from collections import Counter, defaultdict
from urllib.parse import quote

from catalog import ROOT, load_resources
from build_paper_pages import STATUS_LABELS as PAPER_STATUSES, papers_newest_first
from source_scope import apply_scope, read_scope
from validate_papers import read_papers


BEGIN = '<!-- BEGIN GENERATED CATALOG -->'
END = '<!-- END GENERATED CATALOG -->'
PAPERS_BEGIN = '<!-- BEGIN GENERATED PAPERS -->'
PAPERS_END = '<!-- END GENERATED PAPERS -->'
CONTENTS_BEGIN = '<!-- BEGIN GENERATED CONTENTS -->'
CONTENTS_END = '<!-- END GENERATED CONTENTS -->'
BADGES_BEGIN = '<!-- BEGIN GENERATED BADGES -->'
BADGES_END = '<!-- END GENERATED BADGES -->'
CATEGORIES = {
    'core': ('Official REA: core and setup', 'REA 官方：核心与配置'),
    'workflow-guides': ('Official REA: investigation guides', 'REA 官方：调查指南'),
    'official-case-studies': ('Official REA: case studies', 'REA 官方：案例'),
    'community-integrations': ('Community REA integrations', 'REA 社区集成'),
    'community-labs': ('Community REA labs', 'REA 社区练习'),
    'community-case-studies': ('Community REA investigations', 'REA 社区调查案例'),
    'reconstruction-cases': ('Independent reconstruction cases', '独立重建案例'),
    'agent-mcp': ('Independent MCP integrations', '独立 MCP 集成'),
    'agent-workflows': ('Independent agent workflows', '独立智能体工作流'),
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
    'independent-agent-integration': ('Independent agent integration', '独立智能体集成'),
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
    """Render source text literally inside generated Markdown prose and link labels."""
    text = html.escape(' '.join(value.split()), quote=False)
    # Match emoji names before Markdown escaping introduces backslashes in them.
    text = re.sub(r':(?=[A-Za-z0-9_+\-]+:)', '<span>:</span>', text)
    text = ''.join('\\' + character if character in r"\[]*_`~" else character
                   for character in text)
    # A literal source link must not look like a template link to Markdown checks.
    text = text.replace('](', r']\(')
    # GitHub also links bare URLs/emails after parsing; escapes alone do not stop it.
    # Constant, visible delimiters split those tokens without changing their text/style.
    text = text.replace('://', '<span>:</span>//')
    text = re.sub(r'(?i)www\.', lambda match: match[0][:-1] + '<span>.</span>', text)
    text = text.replace('@', '<span>@</span>')
    text = text.replace('$', '<span>$</span>')
    # Descriptions start their own paragraph and must not introduce a block.
    text = re.sub(r'^(#{1,6})(?= |$)', lambda match: '\\' + match[0], text)
    text = re.sub(r'^(\d{1,9})([.)])(?= |$)', lambda match: match[1] + '\\' + match[2], text)
    text = re.sub(r'^([-+])(?= |$)', lambda match: '\\' + match[0], text)
    if re.fullmatch(r'-{3,}|={3,}', text):
        text = '\\' + text
    return text


def requirements_text(value):
    """Both supported source formats render as ordinary prose."""
    if isinstance(value, str):
        return plain_text(value)
    return plain_text(' '.join(value))


# English and Chinese section names. Headings and Contents both use these labels so they cannot drift;
# Chinese headings keep the English name as a prefix. Chinese terms follow the glossary in CONTRIBUTING.zh-CN.md.
COLLECTION_SECTIONS = {
    'website': ('Website', '网站'),
    'game': ('Game', '游戏'),
    'app': ('App', '应用'),
    'native-binary': ('Native Binary', '原生二进制'),
    'firmware': ('Firmware and Hardware', '固件与硬件'),
    'protocol': ('Protocol', '协议'),
    'agents-and-mcp': ('Agents and MCP', '智能体与 MCP'),
    'related-collections': ('Related Collections', '相关合集'),
    'references-and-learning': ('References and Learning', '文档与学习资源'),
}
TARGET_SECTIONS = ('website', 'game', 'app', 'native-binary', 'firmware', 'protocol')
INDEX_HEADINGS = ('Full Repository Index', '完整仓库索引')


def section_heading(section, language):
    english, chinese = COLLECTION_SECTIONS[section]
    return english if language == 'en' else f'{english} · {chinese}'


KIND_LABELS = {
    'project': ('Project', '项目'), 'tool': ('Tool', '工具'),
    'integration': ('Integration', '集成'), 'case-study': ('Case study', '案例'),
    'collection': ('Collection', '合集'), 'documentation': ('Documentation', '文档'),
    'learning-resource': ('Learning resource', '学习资源'), 'research': ('Research', '研究'),
}


def collection_section(record):
    """Each resource appears once, under its primary purpose rather than every target tag."""
    category, relationship = record['category'], record['relationship']
    kind = record.get('kind', '')
    if kind == 'collection' or category == 'related-lists':
        return 'related-collections'
    if kind in {'documentation', 'learning-resource', 'research'} or category in {'workflow-guides', 'learning', 'community-labs'} or relationship in {'official-documentation', 'official-guide'}:
        return 'references-and-learning'
    if record['id'] in {'chrome-devtools-mcp', 'playwright-mcp', 'burp-suite-mcp-server', 'webcrack', 'humanify'} or category in {'web-analysis', 'webassembly'}:
        return 'website'
    if record['id'] in {'renderdoc-mcp', 'rea-dxball-case', 'rea-th04-case'} or category == 'game-analysis':
        return 'game'
    if record['id'] in {'jadx-ai-mcp', 'apktool-mcp-server', 'frida-mcp-yfe404', 'super-trouper', 'frida', 'grapefruit', 'rea-aegis-case', 'rea-notion-case', 'nibkit'} or category in {'android', 'dotnet', 'jvm', 'javascript-electron'}:
        return 'app'
    if category == 'firmware':
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
        tags.append(('Independent MCP' if category == 'agent-mcp' else 'Independent agent') if language == 'en' else ('独立 MCP' if category == 'agent-mcp' else '独立智能体'))
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
    """Keep each source title and full description distinct; bibliography overlaps appear only there."""
    index = 0 if language == 'en' else 1
    translations = json.loads((ROOT / 'site/translations.zh-CN.json').read_text(encoding='utf-8')) if language == 'zh' else {}
    groups = defaultdict(list)
    for record in records:
        if record['category'] not in CATEGORIES or record['relationship'] not in RELATIONSHIPS:
            raise ValueError(f"Unknown category or relationship for {record['id']}")
        if record['url'] in paper_urls:
            continue
        groups[collection_section(record)].append(record)
    lines = []
    for section in COLLECTION_SECTIONS:
        if not groups[section]:
            continue
        contents = '[↑ Contents](#contents)' if language == 'en' else '[↑ 返回目录](#目录)'
        lines.extend([f'<a id="{section}"></a>', f'### {section_heading(section, language)}', '', contents, ''])
        cases = [record for record in groups[section] if record['kind'] == 'case-study']
        tools = [record for record in groups[section] if record['kind'] != 'case-study']
        subgroups = [(None, groups[section])]
        if cases and tools:
            subgroups = [
                (('Case studies', '案例')[index], cases),
                (('Tools, projects and integrations', '工具、项目与集成')[index], tools),
            ]
        for label, entries in subgroups:
            if label:
                lines.extend([f'#### {label}', ''])
            for record in entries:
                name = plain_text((record.get('name_zh') or translations.get(record['id'], {}).get('name') or record['name']) if language == 'zh' else record['name'])
                description = plain_text(record[f'description_{language}'])
                metadata = plain_text(entry_type(record, language))
                detail_url = f"https://awesomerea.org/{'zh/' if language == 'zh' else ''}resources/{record['id']}/"
                detail_label = '使用条件与证据' if language == 'zh' else 'Requirements & evidence'
                lines.extend([
                    f"- [**{name}**]({record['url']})", '',
                    f'  {description}', '',
                    f"  {metadata} · [{detail_label}]({detail_url})", '',
                ])
    return '\n'.join(lines).rstrip() + '\n'


def browsable_index_count():
    document = json.loads((ROOT / 'data/source-index.json').read_text(encoding='utf-8'))
    scoped = apply_scope(document['resources'], read_scope(ROOT))
    return sum(record.get('scope_status') != 'excluded' for record in scoped)


def render_contents(records, papers, index_count, language):
    """Contents mirror the rendered sections and show how many entries each one holds."""
    zh = language == 'zh'
    paper_urls = {paper['url'] for paper in papers}
    counts = Counter(collection_section(record) for record in records if record['url'] not in paper_urls)
    cases = sum(record.get('kind') == 'case-study' for record in records)

    def item(label, href, count):
        return f'[{label}]({href}) ({count:,})'

    def section_item(section):
        return item(COLLECTION_SECTIONS[section][int(zh)], f'#{section}', counts[section])

    targets = [section_item(section) for section in TARGET_SECTIONS if counts[section]]
    reading = [item('论文' if zh else 'Papers', '#papers', len(papers))]
    reading += [section_item(section) for section in ('agents-and-mcp', 'references-and-learning')
                if counts[section]]
    more = [item('全部案例' if zh else 'All cases',
                 f"https://awesomerea.org/{'zh/' if zh else ''}cases/", cases)]
    if counts['related-collections']:
        more.append(section_item('related-collections'))
    more.append(item(INDEX_HEADINGS[int(zh)], '#完整仓库索引' if zh else '#full-repository-index', index_count))
    lines = [f"**{'按目标找工具与案例' if zh else 'Tools and cases by target'}**", '']
    lines += ['- ' + ' · '.join(targets[start:start + 3]) for start in range(0, len(targets), 3)]
    lines += ['', f"**{'论文与工作流' if zh else 'Research and workflows'}**", '', '- ' + ' · '.join(reading)]
    lines += ['', f"**{'更多浏览方式' if zh else 'More ways to browse'}**", '', '- ' + ' · '.join(more)]
    return '\n'.join(lines) + '\n'


def render_badges(records, papers, language):
    """Report catalog populations, not execution verification or additive totals."""
    zh = language == 'zh'
    prefix = 'https://awesomerea.org/' + ('zh/' if zh else '')

    def badge(label, value, target, color='53309C'):
        component = lambda text: quote(str(text).replace('-', '--').replace('_', '__'), safe='')
        image = (f'https://img.shields.io/badge/{component(label)}-{component(value)}-{color}'
                 '?style=flat-square&labelColor=303447')
        return f'[![{label}: {value}]({image})]({target})'

    cases = sum(record['kind'] == 'case-study' for record in records)
    workflow = 'https://github.com/reacher-z/Awesome-REA/actions/workflows/validate.yml'
    labels = ('精选资源', '案例', '论文', '目录检查', '许可', '网站') if zh else (
        'resources', 'cases', 'papers', 'Catalog checks', 'license', 'website')
    return ' '.join([
        badge(labels[0], f'{len(records):,}', prefix + 'resources/'),
        badge(labels[1], f'{cases:,}', prefix + 'cases/'),
        badge(labels[2], f'{len(papers):,}', prefix + 'papers/'),
        f'[![{labels[3]}]({workflow}/badge.svg?branch=main)]({workflow})',
        badge(labels[4], 'MIT', 'LICENSE', '606779'),
        badge(labels[5], 'awesomerea.org', prefix, '6235B5'),
    ]) + '\n'


def replace_badges(content, rendered):
    if content.count(BADGES_BEGIN) != 1 or content.count(BADGES_END) != 1:
        raise ValueError('Each README must contain exactly one BEGIN/END badges marker pair')
    before, rest = content.split(BADGES_BEGIN, 1)
    if BADGES_END not in rest:
        raise ValueError('Badges END marker must follow BEGIN')
    _, after = rest.split(BADGES_END, 1)
    return before + BADGES_BEGIN + '\n' + rendered + BADGES_END + after


def replace_contents(content, rendered):
    if content.count(CONTENTS_BEGIN) != 1 or content.count(CONTENTS_END) != 1:
        raise ValueError('Each README must contain exactly one BEGIN/END contents marker pair')
    before, rest = content.split(CONTENTS_BEGIN, 1)
    if CONTENTS_END not in rest:
        raise ValueError('Contents END marker must follow BEGIN')
    _, after = rest.split(CONTENTS_END, 1)
    return before + CONTENTS_BEGIN + '\n' + rendered + CONTENTS_END + after


def replace_catalog(content, rendered):
    if content.count(BEGIN) != 1 or content.count(END) != 1:
        raise ValueError('Each README must contain exactly one BEGIN/END catalog marker pair')
    before, rest = content.split(BEGIN, 1)
    if END not in rest:
        raise ValueError('Catalog END marker must follow BEGIN')
    _, after = rest.split(END, 1)
    return before + BEGIN + '\n' + rendered + END + after


# Paper topics in display order. The /papers/ directory imports these, so both list the same groups.
PAPER_SECTIONS = {
    'agent-evaluation': ('Reverse-engineering agent evaluation', '逆向工程智能体评测'),
    'decompilation': ('Decompilation and symbol recovery', '反编译与符号恢复'),
    'website-reconstruction': ('Website reconstruction', '网站重建'),
    'game-reconstruction': ('Game reconstruction and reverse engineering', '游戏重建与逆向工程'),
    'app-reconstruction': ('App reconstruction and analysis', '应用重建与分析'),
    'firmware-analysis': ('Firmware analysis and rehosting', '固件分析与重托管'),
    'protocol-analysis': ('Protocol inference and analysis', '协议推断与分析'),
}
PAPER_TOPIC_LABELS = {
    'agent-evaluation': ('Agent evaluation', '智能体评测'),
    'decompilation': ('Decompilation', '反编译'),
    'website-reconstruction': ('Websites', '网站'),
    'game-reconstruction': ('Games', '游戏'),
    'app-reconstruction': ('Apps', '应用'),
    'firmware-analysis': ('Firmware', '固件'),
    'protocol-analysis': ('Protocols', '协议'),
}
AGENT_EVALUATION_PAPERS = {
    'paper-llm-resistant-protection',
    'paper-crackmebench', 'paper-crebench', 'paper-sre-bench', 'paper-humans-machines-sre',
    'paper-programbench',
}


def paper_section(paper):
    """Agent benchmarks form their own topic; other papers follow their first target, binaries under decompilation."""
    if paper['id'] in AGENT_EVALUATION_PAPERS:
        return 'agent-evaluation'
    return {'website': 'website-reconstruction', 'game': 'game-reconstruction',
            'app': 'app-reconstruction', 'firmware': 'firmware-analysis',
            'protocol': 'protocol-analysis'}.get(paper['targets'][0], 'decompilation')


def render_papers(papers, language):
    zh = language == 'zh'
    index = int(zh)
    directory = 'https://awesomerea.org/zh/papers/' if zh else 'https://awesomerea.org/papers/'
    lines = ['<a id="papers"></a>', '## 论文' if zh else '## Papers', '',
             (f'**{len(papers)} 篇论文**，按主题分组，组内按年份从新到旧排列。每项均标明发表状态，中文标题为译名。'
              if zh else f'**{len(papers)} papers**, grouped by topic and ordered newest first. Each entry shows its publication status.'), '',
             f"[{'浏览论文目录' if zh else 'Browse the paper directory'}]({directory}) · [{'完整书目 JSON' if zh else 'Complete bibliography JSON'}](data/papers.json) · [{'推荐论文' if zh else 'Suggest a paper'}](https://github.com/reacher-z/Awesome-REA/issues/new?template=paper.yml)", '']
    groups = defaultdict(list)
    for paper in papers:
        groups[paper_section(paper)].append(paper)
    topics = [f'[{labels[index]}](#papers-{section}) ({len(groups[section])})'
              for section, labels in PAPER_TOPIC_LABELS.items() if groups[section]]
    lines.extend([f"**{'按主题' if zh else 'By topic'}**", ''])
    lines.extend('- ' + ' · '.join(topics[start:start + 3]) for start in range(0, len(topics), 3))
    lines.extend(['',
                  ('展开“范围与发表信息”查看完整研究边界。部分论文也出现在精选资源目录中，两者数量不可相加。'
                   if zh else 'Open “Scope and publication details” for each study’s full limitations. Some papers also appear among curated resources; counts are not additive.'), ''])
    for section, labels in PAPER_SECTIONS.items():
        if not groups[section]:
            continue
        back = '[↑ 论文主题](#papers) · [目录](#目录)' if zh else '[↑ Paper topics](#papers) · [Contents](#contents)'
        lines.extend([f'<a id="papers-{section}"></a>', '### ' + labels[index], '', back, ''])
        for paper in papers_newest_first(groups[section]):
            title = plain_text(paper['title_zh'] if zh else paper['title'])
            status = PAPER_STATUSES[paper['publication_status']][index]
            metadata = plain_text(f"{paper['year']} · {paper['venue']} · {status}")
            author = plain_text(paper['authors'][0] + ((' 等' if zh else ' et al.') if len(paper['authors']) > 1 else ''))
            detail_url = f"https://awesomerea.org/{'zh/' if zh else ''}papers/{paper['id']}/"
            links = [f"[PDF]({paper['pdf_url']})"]
            if paper['code_url']:
                links.append(f"[{'代码' if zh else 'Code'}]({paper['code_url']})")
            links.append(f"[{'完整条目与引用' if zh else 'Full entry & citation'}]({detail_url})")
            lines.extend([
                f"- [**{title}**]({paper['url']})", '',
                '  ' + plain_text(paper[f'description_{language}']), '',
                f"  {paper['year']} · {status} · " + ' · '.join(links), '',
                '  <details>',
                f"  <summary>{'范围与发表信息' if zh else 'Scope and publication details'}</summary>", '',
                f"  **{'范围与限制' if zh else 'Scope and limits'}:** "
                + plain_text(paper[f'scope_limitations_{language}']), '',
                f"  **{'发表信息' if zh else 'Publication'}:** {metadata} · {author}", '',
                '  </details>', '',
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
    return content


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Report stale generated blocks without writing files')
    args = parser.parse_args()
    try:
        records = load_resources()
        papers = read_papers(ROOT)
        index_count = browsable_index_count()
        stale = []
        for name, language in [('README.md', 'en'), ('README.zh-CN.md', 'zh')]:
            path = ROOT / name
            current = path.read_text(encoding='utf-8')
            expected = replace_catalog(current, render_catalog(records, language, {paper['url'] for paper in papers}))
            expected = replace_papers(expected, render_papers(papers, language), language)
            expected = replace_contents(expected, render_contents(records, papers, index_count, language))
            expected = replace_badges(expected, render_badges(records, papers, language))
            if current != expected:
                stale.append(name)
                if not args.check:
                    path.write_text(expected, encoding='utf-8')
        if args.check and stale:
            print('Stale generated README blocks: ' + ', '.join(stale), file=sys.stderr)
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
