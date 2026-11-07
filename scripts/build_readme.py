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
    # A title such as "Double Dash!!" reads the same with its repeated mark in a span; awesome-lint's repeated-punctuation
    # check reads the Markdown text and does not look inside it. A typographic apostrophe after an abbreviation or a
    # letter becomes a plain one, because the balanced-punctuation check mistakes it for an unopened closing quote.
    text = re.sub(r'(?<=!)!', '<span>!</span>', text)
    text = re.sub(r"(?<=[\w.])\u2019(?=[a-z])", "'", text)
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
# The authored second-level headings Contents lists around the generated Resources and Papers sections.
README_HEADINGS = {
    'find-by-task': ('Find by task', '按任务查找'),
    'data': ('Use the data', '使用数据'),
    'resources': ('Resources', '资源'),
    'papers': ('Papers', '论文'),
    'index': INDEX_HEADINGS,
    'about': ('About', '关于'),
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
    """Each resource appears once, under its primary purpose rather than every target tag."""
    category, relationship = record['category'], record['relationship']
    kind = record.get('kind', '')
    if kind == 'collection' or category == 'related-lists':
        return 'related-collections'
    if kind in {'documentation', 'learning-resource', 'research'} or category in {'workflow-guides', 'learning', 'community-labs'} or relationship in {'official-documentation', 'official-guide'}:
        return 'references-and-learning'
    if record['id'] in {'chrome-devtools-mcp', 'playwright-mcp', 'burp-suite-mcp-server', 'webcrack', 'humanify'} or category in {'web-analysis', 'webassembly'}:
        return 'website'
    if record['id'] in {'renderdoc-mcp', 'cheatengine-mcp-bridge', 'rea-dxball-case', 'rea-th04-case'} or category == 'game-analysis':
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
    """Targets the section heading does not imply; sections without a target of their own list every target."""
    index = 0 if language == 'en' else 1
    implied = {'native-binary': 'binary'}.get(section, section) if section in TARGET_SECTIONS else None
    labels = [names[index] for target, names in TARGETS.items()
              if target in record.get('targets', []) and target != implied]
    if not labels:
        return ''
    prefix = (('Also: ', '也适用：') if implied else ('Targets: ', '目标：'))[index]
    return ' · ' + prefix + ('、' if index else ', ').join(labels)


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



def without_leading_name(description, name):
    """Drop the item's own name from the front of its description ("Foo is a tool..." becomes "A tool..."), which
    awesome-lint's no-repeat-item-in-description rule flags. Descriptions that do not start with the name are unchanged."""
    if not description.lower().startswith(name.lower()):
        return description
    rest = description[len(name):].lstrip(' :,\u2013\u2014-')
    rest = re.sub(r'^(?:is|are) ', '', rest)
    return rest[:1].upper() + rest[1:] if rest else description


def resource_line(record, section, language, translations, linked=True):
    """The shared README and case-file list line."""
    index = language == 'zh'
    name = plain_text((record.get('name_zh') or translations.get(record['id'], {}).get('name') or record['name']) if index else record['name'])
    title = f'[**{name}**]({entry_link(record["url"])})' if linked else f'**{name}**'
    description = without_leading_name(plain_text(lead_sentence(record[f'description_{language}'], language)), name)
    metadata = plain_text(entry_type(record, language) + other_targets(record, section, language))
    detail_url = f"https://awesomerea.org/{'zh/' if index else ''}resources/{record['id']}/"
    return f'- {title} - {description} <sub>{metadata} · [{FULL_ENTRY[index]}]({detail_url})</sub>'



# About links the upstream REA project by its exact address (tests/test_about_rea.py); the catalog entry for the same
# project opens its README tab instead, so the page does not link one address twice.
README_TAB_URLS = {'https://github.com/morluto/rea'}


def entry_link(url):
    return url + '?tab=readme-ov-file' if url in README_TAB_URLS else url


def render_catalog(records, language, paper_urls=frozenset()):
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
    lines = [tag_legend([record for entries in groups.values() for record in entries], language), '']
    # awesome-lint flags a URL linked twice. A repository that several records document (a tool and its case studies)
    # is linked once; later records name it in plain text and keep their own "Full entry" page link.
    linked = set()
    for section in COLLECTION_SECTIONS:
        if not groups[section]:
            continue
        lines.extend([f'<a id="{section}"></a>', f'### {section_heading(section, language)}', ''])
        if section == 'agents-and-mcp':
            lines.extend(agent_cross_reference(groups, language, translations))
        cases = [record for record in groups[section] if record['kind'] == 'case-study']
        tools = [record for record in groups[section] if record['kind'] != 'case-study']
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
                    lines.append(resource_line(record, section, language, translations,
                                                linked=record['url'] not in linked))
                    linked.add(record['url'])
                    linked.add(record['url'])
                lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def agent_cross_reference(groups, language, translations):
    """Point from Agents and MCP to agent integrations filed under a target section, via their entry pages."""
    index = 0 if language == 'en' else 1
    parts = []
    for section in TARGET_SECTIONS:
        names = []
        # Same order as the section renders: case studies first, then tools.
        for record in section_order(section, groups[section]):
            if record['category'] == 'agent-mcp' or record['relationship'] == 'independent-agent-integration':
                name = (record.get('name_zh') or translations.get(record['id'], {}).get('name') or record['name']) if index else record['name']
                names.append(f"[{plain_text(name)}](https://awesomerea.org/{'zh/' if index else ''}resources/{record['id']}/)")
        if names:
            # The section name is plain text: Contents already links each section once, and awesome-lint flags repeats.
            parts.append(f'{COLLECTION_SECTIONS[section][index]}{"：" if index else ": "}'
                         + ('、' if index else ', ').join(names))
    if not parts:
        return []
    return [('**其他分区中的智能体集成：** ' if index else '**Also in target sections:** ') + ' · '.join(parts), '']


def browsable_index_count():
    from public_source_supplements import load_supplements, project_additions
    document = json.loads((ROOT / 'data/source-index.json').read_text(encoding='utf-8'))
    supplements = load_supplements(ROOT)
    scoped = apply_scope(document['resources'], read_scope(ROOT)) + project_additions(supplements)
    return sum(record.get('scope_status') != 'excluded' for record in scoped)


def heading_anchor(text):
    """GitHub's fragment for a heading: lowercase, punctuation dropped, each space a hyphen."""
    return '#' + re.sub(r'[^\w\- ]', '', text.lower()).replace(' ', '-')


def render_contents(records, papers, index_count, language):
    """One nested list that mirrors the ## and ### headings in order, as awesome-lint's ToC check expects, with the
    entry count of each section. English links use the heading slugs that check resolves; Chinese headings repeat
    the English section name, so Chinese links keep the explicit section anchors (#firmware, #papers-recent)."""
    zh = language == 'zh'
    paper_urls = {paper['url'] for paper in papers}
    counts = Counter(collection_section(record) for record in records if record['url'] not in paper_urls)

    def item(labels, explicit=None, count=None, blurb=None):
        label = labels[int(zh)]
        anchor = f'#{explicit}' if zh and explicit else heading_anchor(label)
        return (f'[{label}]({anchor})' + ('' if count is None else f' ({count:,})')
                + ('' if blurb is None else f' - {FINDER_BLURBS[blurb][int(zh)]}'))

    sections = [item(COLLECTION_SECTIONS[section], section, counts[section], section)
                for section in COLLECTION_SECTIONS if counts[section]]
    # Papers counts every paper; its one subsection lists the newest, and the topics live in the paper files.
    paper_sections = [item(RECENT_HEADING, 'papers-recent', len(recent_papers(papers)))] if papers else []
    lines = ['- ' + item(README_HEADINGS['find-by-task']),
             '- ' + item(README_HEADINGS['data']),
             '- ' + item(README_HEADINGS['resources'], count=sum(counts.values()))]
    lines += ['  - ' + line for line in sections]
    lines += ['- ' + item(README_HEADINGS['papers'], 'papers', len(papers), 'papers')]
    lines += ['  - ' + line for line in paper_sections]
    lines += ['- ' + item(README_HEADINGS['index'], count=index_count, blurb='index'),
              '- ' + item(README_HEADINGS['about'])]
    return '\n'.join(lines) + '\n'


# One line per catalog section for the front-page finder table; wording is checked against the section's contents.
FINDER_BLURBS = {
    'website': ('Tools and cases for inspecting, deobfuscating and rebuilding websites',
               '用于检查、反混淆和重建网站的工具与案例'),
    'game': ('Decompilations, recompilations, ports, engine reimplementations, analysis tools and cases',
            '反编译、重编译、移植、引擎重新实现，以及分析工具与案例'),
    'app': ('Analysis tools and cases for Android, .NET, JVM and Electron apps',
           '面向 Android、.NET、JVM 和 Electron 应用的分析工具与案例'),
    'native-binary': ('Disassemblers, decompilers, debuggers, binary libraries, diffing tools and native cases',
                     '反汇编器、反编译器、调试器、二进制分析库、差异比较工具及原生二进制案例'),
    'firmware': ('Firmware extraction and analysis tools, plus hardware and device-image cases',
                '固件提取与分析工具，以及硬件和设备镜像案例'),
    'protocol': ('Tools and cases for wire formats, device protocols and packet captures',
                '面向通信数据格式、设备协议和抓包数据的工具与案例'),
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


def render_badges(records, papers, language):
    """Report catalog populations, not execution verification or additive totals. Five badges, at most six. Count and
    license badges are plain images: the same pages are linked from the navigation row and the Use the data list, and
    awesome-lint flags a URL repeated in one README. The last badge reads the date of the newest commit under
    data/discoveries/ live, so the README is not regenerated on every scan. There is no CI badge: awesome lists must
    not carry one, and the footer already links the validate workflow's runs."""
    zh = language == 'zh'
    style = '?style=flat-square&labelColor=2B2F3A'

    def badge(label, value, color='6B5159'):
        component = lambda text: quote(str(text).replace('-', '--').replace('_', '__'), safe='')
        return f'![{label}: {value}](https://img.shields.io/badge/{component(label)}-{component(value)}-{color}{style})'

    cases = sum(record['kind'] == 'case-study' for record in records)
    labels = (('精选资源', '案例', '论文', '最近入库', '许可') if zh
              else ('resources', 'cases', 'papers', 'last discovery ingest', 'license'))
    commit = ('https://img.shields.io/github/last-commit/reacher-z/Awesome-REA/main?path=data%2Fdiscoveries'
              f'&label={quote(labels[3])}&color=6B5159&labelColor=2B2F3A&style=flat-square')
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


def render_cases(records, language, paper_urls=frozenset()):
    """Every case under its catalog section, grouped by method where applicable."""
    zh = language == 'zh'
    groups = defaultdict(list)
    for record in records:
        if record['kind'] == 'case-study' and record['url'] not in paper_urls:
            groups[collection_section(record)].append(record)
    translations = json.loads((ROOT / 'site/translations.zh-CN.json').read_text(encoding='utf-8')) if zh else {}
    count = sum(map(len, groups.values()))
    switch = '[English](cases.md) · **简体中文**' if zh else '**English** · [简体中文](cases.zh-CN.md)'
    lines = [f"[{'← 返回 README' if zh else '← Back to the README'}](../{READMES[language]}#{'资源' if zh else 'resources'}) · {switch}", '',
             f'**{count} 个案例**，按分区列出。' if zh else f'**{count} case studies**, grouped by section.', '',
             '## ' + ('目录' if zh else 'Contents'), '']
    # As in the paper files, English links use the heading slugs awesome-lint's ToC check resolves.
    lines += [f"- [{section_heading(section, language)}]({f'#{section}' if zh else heading_anchor(section_heading(section, 'en'))}) ({len(groups[section])})"
              for section in COLLECTION_SECTIONS if groups[section]]
    lines.append('')
    seen_urls = set()
    for section in COLLECTION_SECTIONS:
        cases = groups[section]
        if not cases:
            continue
        lines.extend([f'<a id="{section}"></a>', f'## {section_heading(section, language)}', '',
                      '[↑ 返回目录](#目录)' if zh else '[↑ Contents](#contents)', ''])
        blocks = method_groups(cases) if section in METHOD_SECTIONS else [(None, sorted(cases, key=lambda record: (-int(record.get('added_at', '0000')[:10].replace('-', '')), case_order(record))))]
        for method, block in blocks:
            if method:
                lines.extend([f'<a id="{section}-{method}"></a>',
                              f'### {METHOD_HEADINGS[method][zh]} ({len(block):,})', ''])
            for record in block:
                lines.append(resource_line(record, section, language, translations, record['url'] not in seen_urls))
                seen_urls.add(record['url'])
            lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def render_case_file(records, language, paper_urls=frozenset()):
    body = f"# {('Awesome REA Case Studies', 'Awesome REA 案例')[language == 'zh']}\n\n" + render_cases(records, language, paper_urls)
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
             f"[{'完整论文列表' if zh else 'Full paper list'}]({paper_file}) · "
             f"[{'浏览论文目录' if zh else 'Browse the paper directory'}]({PAPER_DIRECTORY[index]}) · "
             f"[{'完整书目 JSON' if zh else 'Complete bibliography JSON'}](data/papers.json) · "
             f"[{'推荐论文' if zh else 'Suggest a paper'}]({SUGGEST_PAPER})", '']
    # One paragraph rather than a list: awesome-lint reads every list after Contents as resource entries.
    # Each topic keeps its old README anchor, so links to README.md#papers-<topic> land on its link here.
    topics = [f'<a id="papers-{section}"></a>[{labels[index]}]({paper_file}#papers-{section}) ({len(groups[section])})'
              for section, labels in PAPER_TOPIC_LABELS.items() if groups[section]]
    lines.extend([f"**{'按主题：' if zh else 'By topic:'}** " + ' · '.join(topics), '', FULL_ENTRY_NOTE[index], ''])
    if recent:
        lines.extend(['<a id="papers-recent"></a>', '### ' + RECENT_HEADING[index], '',
                      '[↑ 返回目录](#目录)' if zh else '[↑ Contents](#contents)', ''])
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
    notes = (size_warning(name, (root / name).stat().st_size) for name in (*READMES.values(), *CASE_FILES.values()) if (root / name).is_file())
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
                                   + render_catalog(records, language, {paper['url'] for paper in papers}))
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
    for language, name in CASE_FILES.items():
        files[name] = render_case_file(records, language, {paper['url'] for paper in papers})
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
        for name, expected in files.items():
            path = ROOT / name
            if not path.is_file() or path.read_text(encoding='utf-8') != expected:
                stale.append(name)
                if not args.check:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(expected, encoding='utf-8')
        size = {name: len(content.encode('utf-8')) for name, content in files.items()}
        for name in (*READMES.values(), *CASE_FILES.values()):
            note = size_warning(name, size[name])
            if note:
                print(f'Warning: {note}', file=sys.stderr)
        if args.check and stale:
            print('Stale generated files: ' + ', '.join(stale), file=sys.stderr)
            print('Run python3 scripts/build_readme.py', file=sys.stderr)
            return 1
        budget = (', '.join(f'{name} {size[name]:,} bytes' for name in READMES.values())
                  + f' (budget {README_SIZE_WARNING:,}); '
                  + ', '.join(f'{name} {size[name]:,} bytes' for name in (*PAPER_FILES.values(), *CASE_FILES.values())))
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
