#!/usr/bin/env python3
"""Render compact READMEs and complete case and paper lists."""
import argparse
import html
import json
import re
import sys
from collections import Counter, defaultdict
from urllib.parse import quote

from catalog import ROOT, load_resources
from data_classes import DATA_CLASSES, FEATURED_DATA, FEATURED_LABEL, NON_DATA_HEADING, TAGS, record_tags
from build_paper_pages import AUTHORS_OMITTED, STATUS_LABELS as PAPER_STATUSES, authors_omitted, papers_newest_first
from source_scope import apply_scope, read_scope
from validate_papers import read_papers


BEGIN = '<!-- BEGIN GENERATED CATALOG -->'
END = '<!-- END GENERATED CATALOG -->'
PAPERS_BEGIN = '<!-- BEGIN GENERATED PAPERS -->'
PAPERS_END = '<!-- END GENERATED PAPERS -->'
FINDER_BEGIN = '<!-- BEGIN GENERATED FINDER -->'
FINDER_END = '<!-- END GENERATED FINDER -->'
CONTENTS_BEGIN = '<!-- BEGIN GENERATED CONTENTS -->'
CONTENTS_END = '<!-- END GENERATED CONTENTS -->'
BADGES_BEGIN = '<!-- BEGIN GENERATED BADGES -->'
BADGES_END = '<!-- END GENERATED BADGES -->'
READMES = {'en': 'README.md', 'zh': 'README.zh-CN.md'}
# The full paper list, one generated file per language. Each README keeps its Papers section compact: topic
# links into these files and the RECENT_PAPERS newest lines, so paper growth no longer counts against the
# README's GitHub rendering limit.
PAPER_FILES = {'en': 'docs/papers.md', 'zh': 'docs/papers.zh-CN.md'}
CASE_FILES = {'en': 'docs/cases.md', 'zh': 'docs/cases.zh-CN.md'}
CASES_BEGIN = '<!-- BEGIN GENERATED CASES -->'
CASES_END = '<!-- END GENERATED CASES -->'
RECENT_PAPERS = 10
RECENT_CASES = 10
RESOURCE_SOURCES = ('data/rea-resources.json', 'data/tool-resources.json')
INDEX_SOURCES = ('data/source-index.json', 'data/source-scope.json', 'data/source-supplements/')
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
# Same link label as the website's collection pages; the entry page holds what a README line leaves out.
FULL_ENTRY = ('Full entry', '完整条目')
# GitHub truncates a README's rendered view after 500 KiB. The builder warns well before that so a
# reduction can be planned; the warning never fails a build, so open pull requests keep passing.
GITHUB_README_LIMIT = 512_000
README_SIZE_WARNING = 420_000
# Every generated case page stays below this, apart from the README budget, so changing one leaves the other alone.
CASE_PAGE_BUDGET = 420_000
# One name for each entry's requirements disclosure: homepage cards, /resources/, /cases/ and entry pages.
# README lines link the entry page as "Full entry" instead. site/app.js repeats the label in its UI
# strings; validate_site.py checks that copy.
REQUIREMENTS_LABEL = ('Requirements & limits', '使用条件与局限')
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


# A period after these words does not end an English sentence ("Super Smash Bros. Melee", "SmackDown vs. Raw").
ABBREVIATIONS = {'al', 'approx', 'bros', 'cf', 'dr', 'e.g', 'etc', 'fig', 'i.e', 'jr', 'mr', 'mrs', 'ms', 'no', 'sr',
                 'st', 'u.s', 'vol', 'vs'}
# Sentence punctuation plus any closing quotes or brackets. English sentences may start with a lowercase
# project name ("... two libraries. ultramodern reimplements ..."), so only the following space is required.
SENTENCE_END = {
    'en': re.compile(r'(?P<word>\S*?)[.!?]+[”"’)]*(?=\s)'),
    'zh': re.compile(r'(?P<word>)[。！？]+[”」）)]*(?=.)'),
}
PAIRS = ('()', '（）', '“”', '「」', '[]')
# Shorter openings ("ExeBench is a dataset, not a decompiler." is 40) read as fragments and keep the next sentence.
LEAD_MINIMUM = {'en': 40, 'zh': 16}


def lead_sentence(text, language):
    """README lines show a description's opening sentence; the linked entry page keeps the full text."""
    text = ' '.join(text.split())
    for match in SENTENCE_END[language].finditer(text):
        word = re.sub(r'^\W+', '', match['word']).lower()
        if word in ABBREVIATIONS:
            continue
        # An initial after a capitalized name ("Eric S. Raymond") does not end a sentence; "decompiled to C." does.
        before = text[:match.start()].split()
        if re.fullmatch(r'[a-z]', word) and before and before[-1][:1].isupper():
            continue
        lead = text[:match.end()]
        if any(lead.count(opening) != lead.count(closing) for opening, closing in PAIRS):
            continue
        if len(lead) >= LEAD_MINIMUM[language]:
            return lead
    return text


# English and Chinese section names. Headings and Contents both use these labels so they cannot drift;
# Chinese headings keep the English name as a prefix. Chinese terms follow the glossary in CONTRIBUTING.zh-CN.md.
# Data comes first: one section per class, in the classes' order. The other sections follow under their own heading.
COLLECTION_SECTIONS = {
    **DATA_CLASSES,
    'tools': ('Tools', '工具'),
    'agents-and-mcp': ('Agents and MCP', '智能体与 MCP'),
    'related-collections': ('Related Collections', '相关合集'),
    'references-and-learning': ('References and Learning', '文档与学习资源'),
}
OTHER_SECTIONS = tuple(section for section in COLLECTION_SECTIONS if section not in DATA_CLASSES)
# The filter tab each section outside Data belongs to. Every paper sits under Paper, on /papers/.
SECTION_TABS = {'tools': 'tools', 'agents-and-mcp': 'tools', 'related-collections': 'tutorial', 'references-and-learning': 'tutorial'}
INDEX_HEADINGS = ('Full Repository Index', '完整仓库索引')
# The authored second-level headings Contents lists around the generated Data and Papers sections.
README_HEADINGS = {
    'find-by-task': ('Find by task', '按任务查找'),
    'data': ('Use the data', '使用数据'),
    'resources': ('Data', '数据'),
    'other': NON_DATA_HEADING,
    'papers': ('Papers', '论文'),
    'index': INDEX_HEADINGS,
    'about': ('About', '关于'),
    'star-history': ('Star History', 'Star 历史'),
}
# The one ### heading under Papers: the newest papers, before the paper files' full lists.
RECENT_HEADING = ('Most recent papers', '最新论文')


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
    """Each resource appears once: a data point under its class, anything else under its primary purpose."""
    if 'class' in record:
        return record['class']
    category, relationship = record['category'], record['relationship']
    kind = record.get('kind', '')
    if kind == 'collection' or category == 'related-lists':
        return 'related-collections'
    # A case study outside Data reports on or modifies its target, so it reads as learning material.
    if kind in {'documentation', 'learning-resource', 'research', 'case-study'} or category in {'workflow-guides', 'learning', 'community-labs'} or relationship in {'official-documentation', 'official-guide'}:
        return 'references-and-learning'
    if category in {'core', 'agent-mcp', 'agent-workflows', 'community-integrations'}:
        return 'agents-and-mcp'
    return 'tools'


# How a case study reconstructs its game (`reconstruction_method`), in README and /cases/ order, with each group's
# English and Chinese heading. The field is recommended for case studies in METHOD_SECTIONS and optional for
# validation; a value must be one of these (validate.py), and data/README.md defines them.
RECONSTRUCTION_METHODS = {
    'matching-decompilation': ('Matching decompilations and disassemblies', '匹配反编译与反汇编'),
    'decompilation': ('Non-matching decompilations', '非匹配反编译'),
    'static-recompilation': ('Static recompilations', '静态重编译'),
    'port': ('Ports of reconstructed source', '基于重建源码的移植'),
    'engine-reimplementation': ('Engine reimplementations', '引擎重实现'),
    'other': ('Other methods and analyses', '其他方法与分析'),
}
# Cases that name no method form a final group (anchor slug only; never a valid field value).
UNASSIGNED_METHOD = 'unassigned'
METHOD_HEADINGS = {**RECONSTRUCTION_METHODS, UNASSIGNED_METHOD: ('Other reconstruction methods', '其他重建方式')}
METHOD_SECTIONS = ('game',)


def case_order(record):
    """Locale-independent order inside a method group, the same in both languages: English name ignoring case, then id."""
    return record['name'].casefold(), record['id']


def case_method(record):
    """The method group of a case study: its reconstruction_method, or the final group when the field is absent."""
    if 'reconstruction_method' not in record:
        return UNASSIGNED_METHOD
    method = record['reconstruction_method']
    if method not in RECONSTRUCTION_METHODS:
        raise ValueError(f"{record['id']}: reconstruction_method must be one of {', '.join(RECONSTRUCTION_METHODS)}")
    return method


def method_groups(cases):
    """(method, cases) pairs in METHOD_HEADINGS order (cases without a method last), without empty groups, each
    ordered by case_order."""
    groups = {method: [] for method in METHOD_HEADINGS}
    for record in cases:
        groups[case_method(record)].append(record)
    return [(method, sorted(entries, key=case_order)) for method, entries in groups.items() if entries]


def recent_cases(cases):
    """Newest cases in a section, with case_order breaking equal dates."""
    return sorted(cases, key=lambda record: (-int(record.get('added_at', '0000')[:10].replace('-', '')), case_order(record)))[:RECENT_CASES]


def section_order(section, records):
    """One section's entries in README order: case studies first (by method group in METHOD_SECTIONS), then the
    other entries in catalog order. Entry pages' "More in" links and the agent cross-reference follow it."""
    cases = [record for record in records if record['kind'] == 'case-study']
    if section in METHOD_SECTIONS:
        cases = [record for _, block in method_groups(cases) for record in block]
    return cases + [record for record in records if record['kind'] != 'case-study']


def other_targets(record, section, language):
    """A data point has one class, so it shows only the Protocol tag; other sections list every target."""
    index = 0 if language == 'en' else 1
    if section in DATA_CLASSES:
        return ''.join(' · ' + TAGS[tag][index] for tag in record_tags(record))
    labels = [names[index] for target, names in TARGETS.items() if target in record.get('targets', [])]
    if not labels:
        return ''
    return ' · ' + ('Targets: ', '目标：')[index] + ('、' if index else ', ').join(labels)


def entry_type(record, language):
    index = 0 if language == 'en' else 1
    kind = record.get('kind', 'tool')
    if kind not in KIND_LABELS:
        raise ValueError(f'Unknown resource kind: {kind}')
    tags = [KIND_LABELS[kind][index]]
    relation, category = record['relationship'], record['category']
    if relation == 'independent-agent-integration':
        tags.append(('Independent MCP' if category == 'agent-mcp' else 'Independent agent') if language == 'en' else ('独立 MCP' if category == 'agent-mcp' else '独立智能体'))
    elif relation.startswith('official-'):
        tags.append('Official REA' if language == 'en' else 'REA 官方')
    elif relation in {'community-integration', 'community-learning-resource'}:
        tags.append('Community REA' if language == 'en' else 'REA 社区')
    elif relation == 'upstream-maintainer-companion-list':
        tags.append('REA maintainer' if language == 'en' else 'REA 维护者')
    elif relation == 'community-reported-mixed-workflow':
        tags.append('Mixed workflow' if language == 'en' else '混合工具流程')
    elif relation == 'independent-reconstruction':
        tags.append('Independent reconstruction' if language == 'en' else '独立重建')
    # Platform hints come after the relationship tag, never in its place.
    if category == 'android':
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


# Every tag entry_type can render after the type, in legend order: (Chinese tag, English and Chinese definition).
# Tags that share a definition are listed together.
TAG_DEFINITIONS = {
    'Official REA': ('REA 官方', 'published by the REA project', '由 REA 项目发布'),
    'Community REA': ('REA 社区', 'third-party REA work', '基于 REA 的第三方工作'),
    'REA maintainer': ('REA 维护者', "an REA maintainer's list", 'REA 维护者整理的目录'),
    'Independent MCP': ('独立 MCP', 'no established REA connection', '未确认与 REA 有关联'),
    'Independent agent': ('独立智能体', 'no established REA connection', '未确认与 REA 有关联'),
    'Mixed workflow': ('混合工具流程', 'REA plus other tools, per the author', '作者报告 REA 与其他工具并用'),
    'Independent reconstruction': ('独立重建', 'no established REA connection', '未确认与 REA 有关联'),
    'Android': ('Android', 'platform', '平台'),
    '.NET': ('.NET', 'platform', '平台'),
    'JVM': ('JVM', 'platform', '平台'),
    'WebAssembly': ('WebAssembly', 'platform', '平台'),
    'Library': ('程序库', 'code library', '供编程调用的库'),
}


def tag_legend(records, language):
    """Define each relationship and platform tag the listed entries show, and what an untagged entry is."""
    zh = language == 'zh'
    shown = {tag for record in records for tag in entry_type(record, 'en').split(' · ')[1:]}
    if shown - set(TAG_DEFINITIONS):
        raise ValueError(f'Undefined README tags: {sorted(shown - set(TAG_DEFINITIONS))}')
    groups = defaultdict(list)
    for tag, (chinese, english_definition, chinese_definition) in TAG_DEFINITIONS.items():
        if tag in shown:
            groups[chinese_definition if zh else english_definition].append(chinese if zh else tag)
    parts = [('、' if zh else ', ').join(tags) + ('：' if zh else ': ') + definition for definition, tags in groups.items()]
    if any(' · ' not in entry_type(record, 'en') for record in records):
        parts.append('仅有类型：基础工具或学习资源' if zh else 'type only: foundation tool or learning resource')
    return ('**标签：** ' if zh else '**Tags:** ') + plain_text(' · '.join(parts)) + ('。' if zh else '.')


# awesome-lint's no-repeat-item-in-description rule: a description must not open with the entry's name followed
# by a space or punctuation. The name is already the link text, so the line drops it with the words that join it.
NAME_BOUNDARY = re.compile(r'[\s.,!?:-]')
JOINED_BY_IS = re.compile(r'\s+(?:is|was)\s+(?=(?:a|an|the)\s|[A-Z0-9])')
APPOSITIVE = re.compile(r'^,\s[^,]+,(?=\s)')
VERSION = re.compile(r'^\s+v?\d[\w.]*(?=\s)')
NOT_A_VERB = {'is', 'are', 'was', 'were', 'and', 'or', 'for', 'by', 'from', 'with', 'on', 'in', 'to', 'of', 'as', 'at'}


def without_leading_name(name, text):
    """'Mesen is an NES emulator ...' -> 'An NES emulator ...'; 'gore recovers a Godot game ...' -> 'Recovers a
    Godot game ...'; 'Source 2 Decompiler, s2dc, decompiles ...' -> 'Decompiles ...'. Any other opening is kept."""
    if not text.casefold().startswith(name.casefold()):
        return text
    rest = text[len(name):]
    if not rest or not NAME_BOUNDARY.match(rest):
        return text
    rest = APPOSITIVE.sub('', rest, count=1) if rest.startswith(',') else VERSION.sub('', rest, count=1)
    joined = JOINED_BY_IS.match(rest)
    if joined:
        rest = rest[joined.end():]
    elif re.match(r'\s+[a-z]', rest) and rest.split()[0] not in NOT_A_VERB:
        rest = rest.lstrip()
    else:
        return text
    return rest[:1].upper() + rest[1:]


def resource_line(record, section, language, translations, linked=True):
    """The shared README and case-file list line."""
    index = language == 'zh'
    name = plain_text((record.get('name_zh') or translations.get(record['id'], {}).get('name') or record['name']) if index else record['name'])
    title = f'[**{name}**]({record["url"]})' if linked else f'**{name}**'
    lead = lead_sentence(record[f'description_{language}'], language)
    description = plain_text(lead if index else without_leading_name(record['name'], lead))
    featured = FEATURED_LABEL[index] + ' · ' if record['id'] in FEATURED_DATA else ''
    metadata = plain_text(featured + entry_type(record, language) + other_targets(record, section, language))
    detail_url = f"https://awesomerea.org/{'zh/' if index else ''}resources/{record['id']}/"
    return f'- {title} - {description} <sub>{metadata} · [{FULL_ENTRY[index]}]({detail_url})</sub>'


def data_papers(papers):
    """Benchmark and dataset papers by class: they are data points, listed in their class as well as under Papers."""
    groups = defaultdict(list)
    for paper in papers_newest_first([paper for paper in papers if 'class' in paper]):
        groups[paper['class']].append(paper)
    return groups


def render_catalog(records, language, paper_urls=frozenset(), papers=()):
    """One list line per resource: source link, opening sentence, tags and the entry page that holds
    the full description, requirements and evidence. Bibliography overlaps appear only under Papers."""
    index = 0 if language == 'en' else 1
    translations = json.loads((ROOT / 'site/translations.zh-CN.json').read_text(encoding='utf-8')) if language == 'zh' else {}
    groups = defaultdict(list)
    for record in records:
        if record['category'] not in CATEGORIES or record['relationship'] not in RELATIONSHIPS:
            raise ValueError(f"Unknown category or relationship for {record['id']}")
        if record['url'] in paper_urls:
            continue
        groups[collection_section(record)].append(record)
    benchmarks = data_papers(papers)
    lines = [tag_legend([record for entries in groups.values() for record in entries], language), '']
    for section in COLLECTION_SECTIONS:
        if section == OTHER_SECTIONS[0] and any(groups[other] for other in OTHER_SECTIONS):
            lines.extend([f"## {README_HEADINGS['other'][index]}", ''])
        if not groups[section] and not benchmarks[section]:
            continue
        # No "back to Contents" link per section: awesome-lint flags a repeated link, and GitHub's outline menu
        # reaches every heading.
        lines.extend([f'<a id="{section}"></a>', f'### {section_heading(section, language)}', ''])
        if section == 'agents-and-mcp':
            lines.extend(agent_cross_reference(groups, language, translations))
        featured = [record for record in groups[section] if record['id'] in FEATURED_DATA]
        if featured or benchmarks[section]:
            lines.extend([f"#### {('Benchmarks and datasets', '基准与数据集')[index]}", ''])
            lines.extend(resource_line(record, section, language, translations) for record in featured)
            lines.extend(paper_line(paper, language) for paper in benchmarks[section])
            lines.append('')
        cases = [record for record in groups[section] if record['kind'] == 'case-study' and record not in featured]
        tools = [record for record in groups[section] if record['kind'] != 'case-study' and record not in featured]
        if len(cases) > RECENT_CASES:
            case_file = CASE_FILES[language]
            lines.extend([(f'**{len(cases):,} 个案例**，下方列出最新的 {RECENT_CASES} 个。'
                           f'[完整案例列表]({case_file}#{section})' if index else
                           f'**{len(cases):,} case studies**. The {RECENT_CASES} newest are below. '
                           f'[Full case list]({case_file}#{section}).'), ''])
            if section in METHOD_SECTIONS:
                methods = [f'<a id="{section}-{method}"></a>[{METHOD_HEADINGS[method][index]}]'
                           f'({case_file}#{section}-{method}) ({len(block)})'
                           for method, block in method_groups(cases)]
                lines.extend([f"**{'按重建方式：' if index else 'By method:'}** " + ' · '.join(methods), ''])
        shown_cases = recent_cases(cases)
        subgroups = [(None, shown_cases + tools)]
        if cases and tools:
            subgroups = [
                (('Case studies', '案例')[index], shown_cases),
                (('Tools, projects and integrations', '工具、项目与集成')[index], tools),
            ]
        if section == 'tools':
            # The longest section reads by what each tool works on.
            subgroups = [(CATEGORIES[category][index], [record for record in tools if record['category'] == category])
                         for category in CATEGORIES if any(record['category'] == category for record in tools)]
        for label, entries in subgroups:
            if label:
                lines.extend([f'#### {label}', ''])
            blocks = [(None, entries)]
            if section in METHOD_SECTIONS and len(cases) <= RECENT_CASES and all(record['kind'] == 'case-study' for record in entries):
                # Case studies here are grouped by reconstruction method, one level below their own heading.
                blocks = method_groups(entries)
            for method, block in blocks:
                if method:
                    heading = '#' * (5 if label else 4)
                    lines.extend([f'<a id="{section}-{method}"></a>',
                                  f'{heading} {METHOD_HEADINGS[method][index]} ({len(block):,})', ''])
                for record in block:
                    lines.append(resource_line(record, section, language, translations))
                lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def agent_cross_reference(groups, language, translations):
    """Point from Agents and MCP to agent integrations filed under a target section, via their entry pages."""
    index = 0 if language == 'en' else 1
    parts = []
    for section in (*DATA_CLASSES, 'tools'):
        names = []
        # Same order as the section renders: case studies first, then tools.
        for record in section_order(section, groups[section]):
            if record['category'] == 'agent-mcp' or record['relationship'] == 'independent-agent-integration':
                name = (record.get('name_zh') or translations.get(record['id'], {}).get('name') or record['name']) if index else record['name']
                names.append(f"[{plain_text(name)}](https://awesomerea.org/{'zh/' if index else ''}resources/{record['id']}/)")
        if names:
            # The section name is plain text: the finder table above already links each section once.
            parts.append(f'{COLLECTION_SECTIONS[section][index]}{"：" if index else ": "}'
                         + ('、' if index else ', ').join(names))
    if not parts:
        return []
    return [('**其他分区中的智能体集成：** ' if index else '**Also in other sections:** ') + ' · '.join(parts), '']


def browsable_index_count():
    from public_source_supplements import load_supplements, project_additions
    document = json.loads((ROOT / 'data/source-index.json').read_text(encoding='utf-8'))
    supplements = load_supplements(ROOT)
    scoped = apply_scope(document['resources'], read_scope(ROOT)) + project_additions(supplements)
    return sum(record.get('scope_status') != 'excluded' for record in scoped)


def heading_anchor(text):
    """GitHub's fragment for a heading: lowercase, punctuation dropped, each space a hyphen."""
    return '#' + re.sub(r'[^\w\- ]', '', text.lower()).replace(' ', '-')


def section_counts(records, papers):
    """Entries each section lists: its resources, plus the benchmark and dataset papers a class holds."""
    paper_urls = {paper['url'] for paper in papers}
    counts = Counter(collection_section(record) for record in records if record['url'] not in paper_urls)
    counts.update(paper['class'] for paper in papers if 'class' in paper)
    return counts


def render_contents(records, papers, index_count, language):
    """The README's one section map: a nested list that mirrors the ## and ### headings in order, as awesome-lint's
    ToC check expects, with each section's entry count and what it holds. Each heading is linked once, here.
    English links use the heading slugs that check resolves; Chinese headings repeat the English section name, so
    Chinese links keep the explicit section anchors (#firmware, #papers-recent). Contributing stays out of the
    list (the ToC check excludes it); the navigation row links it."""
    zh = language == 'zh'
    paper_urls = {paper['url'] for paper in papers}
    counts = section_counts(records, papers)

    def item(labels, explicit=None, count=None, blurb=None):
        label = labels[int(zh)]
        anchor = f'#{explicit}' if zh and explicit else heading_anchor(label)
        return (f'[{label}]({anchor})' + ('' if count is None else f' ({count:,})')
                + ('' if blurb is None else ' — ' + FINDER_BLURBS[blurb][int(zh)]))

    listed = lambda group: ['  - ' + item(COLLECTION_SECTIONS[section], section, counts[section], section) for section in group if counts[section]]
    # Papers counts every paper; its one subsection lists the newest, and the topics live in the paper files.
    paper_sections = [item(RECENT_HEADING, 'papers-recent', len(recent_papers(papers)))] if papers else []
    lines = ['- ' + item(README_HEADINGS['find-by-task']),
             '- ' + item(README_HEADINGS['data']),
             '- ' + item(README_HEADINGS['resources'], count=sum(counts[section] for section in DATA_CLASSES))]
    lines += listed(DATA_CLASSES)
    lines += ['- ' + item(README_HEADINGS['other'], count=sum(counts[section] for section in OTHER_SECTIONS))]
    lines += listed(OTHER_SECTIONS)
    lines += ['- ' + item(README_HEADINGS['papers'], 'papers', len(papers), 'papers')]
    lines += ['  - ' + line for line in paper_sections]
    lines += ['- ' + item(README_HEADINGS['index'], count=index_count, blurb='index'),
              '- ' + item(README_HEADINGS['about']),
              '- ' + item(README_HEADINGS['star-history'])]
    return '\n'.join(lines) + '\n'


# What each Contents line holds, per catalog section; wording is checked against the section's contents.
FINDER_BLURBS = {
    'software': ('Rebuilt Mac, Linux and Windows software: decompilations, reimplementations, ports and benchmarks',
                 '重建的 Mac、Linux 和 Windows 软件：反编译、重新实现、移植与基准'),
    'game': ('Rebuilt games: decompilations, recompilations, ports, engine reimplementations and private servers',
             '重建的游戏：反编译、重编译、移植、引擎重新实现与私服'),
    'apps': ('Rebuilt Android, iOS and iPadOS apps and their formats and interfaces',
             '重建的 Android、iOS 和 iPadOS 应用及其格式与接口'),
    'website': ('Rebuilt websites, web apps and private web APIs, plus benchmarks of website reproduction',
                '重建的网站、Web 应用和私有 Web API，以及网站复刻基准'),
    'science': ('Rebuilt specialist STEM software such as CAD, EDA, simulation and lab analysis packages',
                '重建的专业 STEM 软件，如 CAD、EDA、仿真与实验分析软件'),
    'hardware': ('Rebuilt firmware, drivers, device clients and device protocols for chips, IoT and consumer devices',
                 '面向芯片、物联网和消费电子设备重建的固件、驱动、设备客户端与协议'),
    'tools': ('Disassemblers, decompilers, debuggers, proxies, libraries and format tools that work across targets',
              '适用于多种目标的反汇编器、反编译器、调试器、代理、程序库与格式工具'),
    'agents-and-mcp': ('Official REA material, MCP servers, integrations and agent workflows, labelled by REA relationship',
                      'REA 官方资料、MCP 服务器、集成与智能体工作流程，按其与 REA 的关系标注'),
    'related-collections': ('Other curated lists on reverse engineering and related security topics',
                           '逆向工程及相关安全主题的其他精选合集'),
    'references-and-learning': ('Documentation, investigation guides, labs and learning resources',
                               '文档、分析指南、实验练习与学习资源'),
    'papers': ('Research bibliography, kept in generated paper lists',
              '研究论文书目，列于自动生成的论文列表'),
    'index': ('Public repositories found by README scans; unreviewed',
             '通过 README 扫描发现的公开仓库；未审核'),
}

def render_totals(records, papers, index_count, language):
    """One line of collection totals and the newest review date, above the Contents sections."""
    zh = language == 'zh'
    cases = sum(record.get('kind') == 'case-study' for record in records)
    reviewed = max(entry['verified_at'][:10] for entry in [*records, *papers])
    if zh:
        line = (f'{len(records):,} 项精选资源（{cases:,} 个案例）· {len(papers):,} 篇论文 · '
                f'{index_count:,} 个已索引仓库 · 最近来源复核 {reviewed}。')
    else:
        line = (f'{len(records):,} curated resources ({cases:,} cases) · {len(papers):,} papers · '
                f'{index_count:,} indexed repositories · latest source review {reviewed}.')
    return line + '\n\n'


SCAN_STATUS_URL = 'https://raw.githubusercontent.com/reacher-z/Awesome-REA/status/scan-status.json'


def render_badges(records, papers, language):
    """Report catalog populations, not execution verification or additive totals. Five badges, at most six. Count and
    license badges are plain images: the same pages are linked from the navigation row and the Use the data list, and
    awesome-lint flags a URL repeated in one README. The scan badge reads scan-status.json on the status branch live
    (scripts/scan_status_badge.py), so the README is not regenerated on every scan and the badge turns amber after nine
    hours without a successful scan. There is no CI badge: awesome lists must not carry one, and the footer already
    links the validate workflow's runs."""
    zh = language == 'zh'
    style = '?style=flat-square&labelColor=2B2F3A'

    def badge(label, value, color='6B5159'):
        component = lambda text: quote(str(text).replace('-', '--').replace('_', '__'), safe='')
        return f'![{label}: {value}](https://img.shields.io/badge/{component(label)}-{component(value)}-{color}{style})'

    cases = sum(record['kind'] == 'case-study' for record in records)
    labels = (('精选资源', '案例', '论文', '最近扫描', '许可') if zh
              else ('resources', 'cases', 'papers', 'last discovery scan', 'license'))
    commit = (f'https://img.shields.io/endpoint?url={quote(SCAN_STATUS_URL, safe="")}'
              f'&label={quote(labels[3])}&style=flat-square')
    return ' '.join([
        badge(labels[0], f'{len(records):,}'),
        badge(labels[1], f'{cases:,}'),
        badge(labels[2], f'{len(papers):,}'),
        f'[![{labels[3]}]({commit})](data/discoveries/README.md)',
        badge(labels[4], 'MIT', '5E6472'),
    ]) + '\n'


def source_note(*sources, script='scripts/build_readme.py', part='block'):
    """Name a block's generator and inputs so conflicts are rebuilt rather than merged by hand."""
    files = ', '.join(sources[:-1]) + ' and ' + sources[-1] if len(sources) > 1 else sources[0]
    return f'<!-- Generated by {script} from {files}. Edit the source data and rerun the script; do not edit this {part} by hand. -->\n'


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


def replace_finder(content, rendered):
    if content.count(FINDER_BEGIN) != 1 or content.count(FINDER_END) != 1:
        raise ValueError('Each README must contain exactly one BEGIN/END finder marker pair')
    before, rest = content.split(FINDER_BEGIN, 1)
    if FINDER_END not in rest:
        raise ValueError('Finder END marker must follow BEGIN')
    _, after = rest.split(FINDER_END, 1)
    return before + FINDER_BEGIN + '\n' + rendered + FINDER_END + after


def replace_catalog(content, rendered):
    if content.count(BEGIN) != 1 or content.count(END) != 1:
        raise ValueError('Each README must contain exactly one BEGIN/END catalog marker pair')
    before, rest = content.split(BEGIN, 1)
    if END not in rest:
        raise ValueError('Catalog END marker must follow BEGIN')
    _, after = rest.split(END, 1)
    return before + BEGIN + '\n' + rendered + END + after


# Paper topics in display order. The paper files and the /papers/ directory both use these, so they list the same groups.
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
    'paper-attacking-re-ai-agents',
    'paper-llm-resistant-protection',
    'paper-crackmebench', 'paper-crebench', 'paper-sre-bench', 'paper-humans-machines-sre',
    'paper-decompiling-synergy',
    'paper-programbench',
    'paper-enigma',
    'paper-nyu-ctf-bench',
    'paper-cybench',
    'paper-ctf-dojo',
    'paper-cyber-zero',
    'paper-reveree',
}


def paper_section(paper):
    """Agent benchmarks form their own topic; other papers follow their first target, binaries under decompilation."""
    if paper['id'] in AGENT_EVALUATION_PAPERS:
        return 'agent-evaluation'
    return {'website': 'website-reconstruction', 'game': 'game-reconstruction',
            'app': 'app-reconstruction', 'firmware': 'firmware-analysis',
            'protocol': 'protocol-analysis'}.get(paper['targets'][0], 'decompilation')


def paper_groups(papers):
    """Papers by topic section, in input order; Contents, the README and the paper files share this grouping."""
    groups = defaultdict(list)
    for paper in papers:
        groups[paper_section(paper)].append(paper)
    return groups


def recent_papers(papers):
    """The README's newest papers, in the order every paper list uses: year, then the recorded publication date
    (dated records before year-only ones within a year), then English title and stable ID."""
    return papers_newest_first(papers)[:RECENT_PAPERS]


def paper_line(paper, language):
    """One paper as one list line, identical in the README's recent list and in the paper files."""
    zh = language == 'zh'
    index = int(zh)
    title = plain_text(paper['title_zh'] if zh else paper['title'])
    status = PAPER_STATUSES[paper['publication_status']][index]
    if authors_omitted(paper):
        # The record lists no names: the line links the paper, which lists its authors.
        metadata = plain_text(f'{paper_venue(paper)} · {status}') + f" · [{AUTHORS_OMITTED[index]}]({paper['url']})"
    else:
        author = paper['authors'][0] + ((' 等' if zh else ' et al.') if len(paper['authors']) > 1 else '')
        metadata = plain_text(f'{paper_venue(paper)} · {status} · {author}')
    detail_url = f"https://awesomerea.org/{'zh/' if zh else ''}papers/{paper['id']}/"
    links = [f"[PDF]({paper['pdf_url']})"]
    if paper['code_url']:
        links.append(f"[{'代码' if zh else 'Code'}]({paper['code_url']})")
    links.append(f'[{FULL_ENTRY[index]}]({detail_url})')
    description = plain_text(lead_sentence(paper[f'description_{language}'], language))
    return (f"- [**{title}**]({paper['url']}) - {description} <sub>{original_title(paper) if zh else ''}{metadata} · "
            + ' · '.join(links) + '</sub>')


PAPER_DIRECTORY = ('https://awesomerea.org/papers/', 'https://awesomerea.org/zh/papers/')
SUGGEST_PAPER = 'https://github.com/reacher-z/Awesome-REA/issues/new?template=paper.yml'
PAPER_FILE_TITLES = ('Awesome REA Papers', 'Awesome REA 论文')
FULL_ENTRY_NOTE = ('Each paper’s “Full entry” holds its complete summary, scope and limitations, all authors and citation.',
                   '每篇论文的“完整条目”提供完整摘要、研究范围与局限、全部作者和引文。')


def render_papers(papers, language):
    """The body of a paper file: navigation, a topic Contents list, then every paper under its topic heading,
    newest first. Each topic keeps the explicit anchor the README used, papers-<topic>."""
    zh = language == 'zh'
    index = int(zh)
    groups = paper_groups(papers)
    switch = '[English](papers.md) · **简体中文**' if zh else '**English** · [简体中文](papers.zh-CN.md)'
    lines = [f"[{'← 返回 README' if zh else '← Back to the README'}](../{READMES[language]}#papers) · {switch}", '',
             (f'**{len(papers)} 篇论文**，按主题分组，组内按年份从新到旧排列。每行列出摘要首句、英文原题、发表场所、状态与第一作者，中文标题为译名。'
              if zh else f'**{len(papers)} papers**, grouped by topic and ordered newest first. Each line shows the study’s opening sentence, venue, publication status and first author.'), '',
             f"[{'浏览论文目录' if zh else 'Browse the paper directory'}]({PAPER_DIRECTORY[index]}) · "
             f"[{'完整书目 JSON' if zh else 'Complete bibliography JSON'}](../data/papers.json) · "
             f"[{'推荐论文' if zh else 'Suggest a paper'}]({SUGGEST_PAPER})", '',
             '## ' + ('目录' if zh else 'Contents'), '']
    # As in the README Contents, English links use the heading slugs awesome-lint's ToC check resolves.
    lines += [f"- [{labels[index]}]({f'#papers-{section}' if zh else heading_anchor(labels[0])}) ({len(groups[section])})"
              for section, labels in PAPER_SECTIONS.items() if groups[section]]
    lines += ['', FULL_ENTRY_NOTE[index], '']
    for section, labels in PAPER_SECTIONS.items():
        if not groups[section]:
            continue
        lines.extend([f'<a id="papers-{section}"></a>', '## ' + labels[index], '',
                      '[↑ 返回目录](#目录)' if zh else '[↑ Contents](#contents)', ''])
        lines.extend(paper_line(paper, language) for paper in papers_newest_first(groups[section]))
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def render_paper_file(papers, language):
    """docs/papers.md or docs/papers.zh-CN.md. The generated block is the whole file, so --check covers all of it."""
    body = f'# {PAPER_FILE_TITLES[language == "zh"]}\n\n' + render_papers(papers, language)
    return PAPERS_BEGIN + '\n' + source_note('data/papers.json', part='file') + body + PAPERS_END + '\n'


def case_groups(records, paper_urls=frozenset()):
    groups = defaultdict(list)
    for record in records:
        if record['kind'] == 'case-study' and record['url'] not in paper_urls:
            groups[collection_section(record)].append(record)
    return groups


def case_page_name(section, language, part=None):
    suffix = '.zh-CN' if language == 'zh' else ''
    return f'docs/cases/{section}{f"-{part}" if part is not None else ""}{suffix}.md'


def case_page(section, entries, language, filename, translations, seen_urls, first_methods):
    """Render one bounded section page. Entries retain the catalog's section and method order."""
    zh = language == 'zh'
    other = 'en' if zh else 'zh'
    part_match = re.search(r'-(\d+)\.(?:zh-CN\.)?md$', filename)
    other_name = case_page_name(section, other, int(part_match[1]) if part_match else None)
    lines = [f"# {section_heading(section, language)}", '',
             f"[{'← 返回案例目录' if zh else '← Back to case index'}](../cases{'.zh-CN' if zh else ''}.md#{section})",
             '', f"[{'English' if zh else '简体中文'}]({other_name.rsplit('/', 1)[1]})", '',
             f"**{len(entries):,} {'个案例' if zh else 'case studies'}**", '']
    previous = None
    for method, record in entries:
        if method != previous and method is not None:
            anchor = f'{section}-{method}'
            if method in first_methods:
                lines.append(f'<a id="{anchor}"></a>')
            lines.extend([f'## {METHOD_HEADINGS[method][zh]}', ''])
            previous = method
        lines.append(resource_line(record, section, language, translations, record['url'] not in seen_urls))
        seen_urls.add(record['url'])
    body = '\n'.join(lines).rstrip() + '\n'
    return CASES_BEGIN + '\n' + source_note(*RESOURCE_SOURCES, part='file') + body + CASES_END + '\n'


def render_case_pages(records, paper_urls=frozenset()):
    """Return both case indexes and every bounded section page."""
    groups = case_groups(records, paper_urls)
    translations = {'en': {}, 'zh': json.loads((ROOT / 'site/translations.zh-CN.json').read_text(encoding='utf-8'))}
    pages = {}
    section_parts = {}
    method_paths = {'en': {}, 'zh': {}}
    seen = {'en': set(), 'zh': set()}
    for section in COLLECTION_SECTIONS:
        cases = groups[section]
        if not cases:
            continue
        blocks = method_groups(cases) if section in METHOD_SECTIONS else [
            (None, sorted(cases, key=lambda record: (-int(record.get('added_at', '0000')[:10].replace('-', '')), case_order(record))))]
        ordered = [(method, record) for method, block in blocks for record in block]
        parts = []
        current = []
        current_bytes = 0
        for item in ordered:
            method, record = item
            line_bytes = max(len(resource_line(record, section, lang, translations[lang]).encode('utf-8'))
                             for lang in ('en', 'zh')) + (300 if method is not None else 0)
            if line_bytes + 3_000 > CASE_PAGE_BUDGET:
                raise ValueError(f'{section}: one case exceeds the {CASE_PAGE_BUDGET:,}-byte page budget')
            if current and current_bytes + line_bytes + 3_000 > CASE_PAGE_BUDGET:
                parts.append(current)
                current = []
                current_bytes = 0
            current.append(item)
            current_bytes += line_bytes
        if current:
            parts.append(current)
        section_parts[section] = len(parts)
        for number, entries in enumerate(parts, 1):
            first = {method for method, _ in entries if method is not None and method not in
                     {m for part in parts[:number - 1] for m, _ in part}}
            for language in ('en', 'zh'):
                name = case_page_name(section, language, number if len(parts) > 1 else None)
                pages[name] = case_page(section, entries, language, name, translations[language], seen[language], first)
                if len(pages[name].encode('utf-8')) > CASE_PAGE_BUDGET:
                    raise ValueError(f'{name} exceeds the {CASE_PAGE_BUDGET:,}-byte page budget')
                for method in first:
                    method_paths[language][f'{section}-{method}'] = name
    for language, name in CASE_FILES.items():
        pages[name] = render_case_file(groups, language, section_parts, method_paths[language])
        if len(pages[name].encode('utf-8')) > CASE_PAGE_BUDGET:
            raise ValueError(f'{name} exceeds the {CASE_PAGE_BUDGET:,}-byte page budget')
    return pages


def render_cases(groups, language, section_parts, method_paths):
    """The compact entry page with stable section and method anchors."""
    zh = language == 'zh'
    count = sum(map(len, groups.values()))
    switch = '[English](cases.md) · **简体中文**' if zh else '**English** · [简体中文](cases.zh-CN.md)'
    lines = [f"[{'← 返回 README' if zh else '← Back to the README'}](../{READMES[language]}#{'数据' if zh else 'data'}) · {switch}", '',
             f'**{count} 个案例**，按分区列出。' if zh else f'**{count} case studies**, grouped by section.', '',
             '## ' + ('目录' if zh else 'Contents'), '']
    lines += [f"- [{section_heading(section, language)}](#{section}) ({len(groups[section])})"
              for section in COLLECTION_SECTIONS if groups[section]]
    lines.append('')
    for section in COLLECTION_SECTIONS:
        cases = groups[section]
        if not cases:
            continue
        lines.extend([f'<a id="{section}"></a>', f'## {section_heading(section, language)} ({len(cases):,})', ''])
        names = [case_page_name(section, language, part if section_parts[section] > 1 else None)
                 for part in range(1, section_parts[section] + 1)]
        label = '案例列表' if zh else 'Case studies'
        for part, name in enumerate(names, 1):
            title = (f'{label}（第 {part} 部分）' if zh else f'{label}, part {part}') if len(names) > 1 else label
            lines.append(f'- [{title}](cases/{name.rsplit("/", 1)[1]})')
        lines.append('')
        if section in METHOD_SECTIONS:
            for method, block in method_groups(cases):
                anchor = f'{section}-{method}'
                path = method_paths[anchor].rsplit('/', 1)[1]
                lines.extend([f'<a id="{anchor}"></a>',
                              f'- [{METHOD_HEADINGS[method][zh]}](cases/{path}#{anchor}) ({len(block):,})'])
            lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def render_case_file(groups, language, section_parts, method_paths):
    body = f"# {('Awesome REA Case Studies', 'Awesome REA 案例')[language == 'zh']}\n\n" + render_cases(groups, language, section_parts, method_paths)
    return CASES_BEGIN + '\n' + source_note(*RESOURCE_SOURCES, part='file') + body + CASES_END + '\n'


def render_readme_papers(papers, language):
    """The README's compact Papers section: the count, links, topic links into the paper file and the newest
    papers. Its size depends on RECENT_PAPERS, not on how many papers the bibliography holds."""
    zh = language == 'zh'
    index = int(zh)
    groups = paper_groups(papers)
    recent = recent_papers(papers)
    paper_file = PAPER_FILES[language]
    lines = ['<a id="papers"></a>', '## ' + README_HEADINGS['papers'][index], '',
             (f'**{len(papers)} 篇论文**，完整列表按主题分组，组内按年份从新到旧排列。下面列出最新的 {len(recent)} 篇；每行列出摘要首句、英文原题、发表场所、状态与第一作者，中文标题为译名。'
              if zh else f'**{len(papers)} papers**, grouped by topic and ordered newest first in the full paper list. The {len(recent)} most recent are below; each line shows the study’s opening sentence, venue, publication status and first author.'), '',
             # The navigation row already links the paper directory, and Contributing links the paper form.
             f"[{'完整论文列表' if zh else 'Full paper list'}]({paper_file}) · "
             f"[{'完整书目 JSON' if zh else 'Complete bibliography JSON'}](data/papers.json)", '']
    # One paragraph rather than a list: awesome-lint reads every list after Contents as resource entries.
    # Each topic keeps its old README anchor, so links to README.md#papers-<topic> land on its link here.
    topics = [f'<a id="papers-{section}"></a>[{labels[index]}]({paper_file}#papers-{section}) ({len(groups[section])})'
              for section, labels in PAPER_TOPIC_LABELS.items() if groups[section]]
    lines.extend([f"**{'按主题：' if zh else 'By topic:'}** " + ' · '.join(topics), '', FULL_ENTRY_NOTE[index], ''])
    if recent:
        lines.extend(['<a id="papers-recent"></a>', '### ' + RECENT_HEADING[index], ''])
        lines.extend(paper_line(paper, language) for paper in recent)
    return '\n'.join(lines).rstrip() + '\n'


def paper_venue(paper):
    """Most venue names already carry the year; add it once to the rest (arXiv, journals, WOOT 18)."""
    venue = paper['venue']
    return venue if re.search(rf"(?<!\d){paper['year']}(?!\d)", venue) else f"{venue} {paper['year']}"


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


def size_warning(name, size):
    """Advisory size note for a README of `size` UTF-8 bytes, or None while it is within the budget."""
    if size <= README_SIZE_WARNING:
        return None
    if size > GITHUB_README_LIMIT:
        headroom = f'its last {size - GITHUB_README_LIMIT:,} bytes are already cut off'
    else:
        headroom = f'{GITHUB_README_LIMIT - size:,} bytes are left'
    return (f'{name} is {size:,} bytes, above the {README_SIZE_WARNING:,}-byte budget. GitHub stops rendering a README '
            f'after {GITHUB_README_LIMIT:,} bytes and {headroom}.')


def readme_size_warnings(root=ROOT):
    """Size notes for READMEs and case files on disk; validate.py prints them without failing."""
    names = (*READMES.values(), *CASE_FILES.values(), *(str(path.relative_to(root)) for path in (root / 'docs/cases').glob('*.md')))
    notes = (size_warning(name, (root / name).stat().st_size) for name in names if (root / name).is_file())
    return [note for note in notes if note]


def original_title(paper):
    """Chinese lines open their metadata with the published title, so readers can search for and cite it."""
    return f"原题：*{plain_text(paper['title'])}* · "


def rendered_files(records, papers, index_count):
    """Every file this builder owns, keyed by repository path: both READMEs, their generated blocks replaced in
    the text on disk, then both paper files."""
    files = {}
    for language, name in READMES.items():
        current = (ROOT / name).read_text(encoding='utf-8')
        names = RESOURCE_SOURCES + (('site/translations.zh-CN.json',) if language == 'zh' else ())
        expected = replace_catalog(current, source_note(*names)
                                   + render_catalog(records, language, {paper['url'] for paper in papers}, papers))
        expected = replace_papers(expected, source_note('data/papers.json') + render_readme_papers(papers, language),
                                  language)
        expected = replace_contents(expected, source_note(*RESOURCE_SOURCES, 'data/papers.json', *INDEX_SOURCES)
                                    + render_contents(records, papers, index_count, language))
        expected = replace_finder(expected, source_note(*RESOURCE_SOURCES, 'data/papers.json', *INDEX_SOURCES)
                                  + render_totals(records, papers, index_count, language))
        files[name] = replace_badges(expected, source_note(*RESOURCE_SOURCES, 'data/papers.json')
                                     + render_badges(records, papers, language))
    for language, name in PAPER_FILES.items():
        files[name] = render_paper_file(papers, language)
    files.update(render_case_pages(records, {paper['url'] for paper in papers}))
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Report stale generated files without writing them')
    args = parser.parse_args()
    try:
        records = load_resources()
        papers = read_papers(ROOT)
        files = rendered_files(records, papers, browsable_index_count())
        stale = []
        generated_case_paths = set(files) & {name for name in files if name.startswith('docs/cases/')}
        extra = sorted(str(path.relative_to(ROOT)) for path in (ROOT / 'docs/cases').glob('*.md')
                       if str(path.relative_to(ROOT)) not in generated_case_paths)
        for name, expected in files.items():
            path = ROOT / name
            if not path.is_file() or path.read_text(encoding='utf-8') != expected:
                stale.append(name)
                if not args.check:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(expected, encoding='utf-8')
        stale.extend(extra)
        if not args.check:
            for name in extra:
                (ROOT / name).unlink()
        size = {name: len(content.encode('utf-8')) for name, content in files.items()}
        for name in (*READMES.values(), *(name for name in files if name.startswith('docs/cases'))):
            note = size_warning(name, size[name])
            if note:
                print(f'Warning: {note}', file=sys.stderr)
        if args.check and stale:
            print('Stale generated files: ' + ', '.join(stale), file=sys.stderr)
            print('Run python3 scripts/build_readme.py', file=sys.stderr)
            return 1
        budget = (', '.join(f'{name} {size[name]:,} bytes' for name in READMES.values())
                  + f' (budget {README_SIZE_WARNING:,}); '
                  + ', '.join(f'{name} {size[name]:,} bytes' for name in (*PAPER_FILES.values(), CASE_FILES['en'], CASE_FILES['zh']))
                  + f'; {len(generated_case_paths)} section pages, largest {max(size[name] for name in generated_case_paths):,} bytes')
        if args.check:
            print(f'READMEs, paper files and case files match {len(records)} resources and {len(papers)} separate research papers; {budget}.')
        else:
            print(f"Rendered {len(records)} resources and {len(papers)} separate research papers into READMEs, paper files and case files; updated {len(stale)} files; {budget}.")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'Catalog generation failed: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
