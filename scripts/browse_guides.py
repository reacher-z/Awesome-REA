"""Repository category guides: a short definition, a comparison table and FAQs, computed from the listed records."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta
from html import escape, unescape
import re

from build_readme import TARGETS

# What each repository category holds. The scope follows the scan's classification rules (scripts/scan_sources.py).
DEFINITIONS = {
    'web-analysis': ('Repositories for inspecting, deobfuscating, scraping and rebuilding websites and web apps: JavaScript deobfuscators, browser tooling, HTTP interception and API capture, and WebAssembly analysis.',
                     '用于检查、反混淆、抓取和重建网站与 Web 应用的仓库，包括 JavaScript 反混淆工具、浏览器工具、HTTP 拦截与 API 抓取，以及 WebAssembly 分析。'),
    'game-analysis': ('Repositories for reverse engineering games: decompilation and recompilation projects, Unity and Unreal analysis, IL2CPP tooling, and console, save-file and visual-novel research.',
                      '用于游戏逆向工程的仓库，包括反编译与重编译项目、Unity 和 Unreal 分析、IL2CPP 工具，以及主机、存档和视觉小说研究。'),
    'android': ('Repositories for analyzing Android apps: APK and DEX decompilers such as jadx, unpackers, and tools for inspecting and modifying Android packages.',
                '用于分析 Android 应用的仓库，包括 jadx 等 APK 与 DEX 反编译器、脱壳工具，以及检查和修改 Android 安装包的工具。'),
    'managed-code': ('Repositories for .NET and other managed-code applications: C# and CIL decompilers such as ILSpy and dnSpy, assembly browsers and related analysis tools.',
                     '面向 .NET 等托管代码应用的仓库，包括 ILSpy、dnSpy 等 C# 与 CIL 反编译器、程序集浏览器和相关分析工具。'),
    'native-analysis': ('Repositories for static analysis of native executables: disassemblers, decompilers, Ghidra and IDA plugins, and tooling for x86, ARM, MIPS and RISC-V machine code.',
                        '用于原生可执行文件静态分析的仓库，包括反汇编器、反编译器、Ghidra 和 IDA 插件，以及面向 x86、ARM、MIPS 和 RISC-V 机器码的工具。'),
    'dynamic-analysis': ('Repositories for observing programs while they run: debuggers, Frida and other instrumentation frameworks, and memory-forensics tools.',
                         '用于在程序运行时进行观察的仓库，包括调试器、Frida 等插桩框架和内存取证工具。'),
    'firmware': ('Repositories for extracting and analyzing firmware images: binwalk and unblob style unpackers, UEFI and BIOS tooling, and embedded-device research.',
                 '用于提取和分析固件镜像的仓库，包括 binwalk、unblob 一类的解包工具、UEFI 与 BIOS 工具，以及嵌入式设备研究。'),
    'protocol-analysis': ('Repositories for analyzing communication protocols: packet capture and pcap tooling, Wireshark dissectors, network forensics and protocol reverse engineering.',
                          '用于分析通信协议的仓库，包括抓包与 pcap 工具、Wireshark 解析器、网络取证和协议逆向。'),
    'reverse-engineering': ('Reverse-engineering repositories that span several targets, together with curated lists, reference collections and learning material.',
                            '覆盖多个目标领域的逆向工程仓库，以及精选列表、参考合集和学习资料。'),
}
ROWS = 6
# The noun each category's questions use.
QUESTION_NAMES = {'web-analysis': ('website', '网站'), 'game-analysis': ('game', '游戏'), 'android': ('Android app', 'Android 应用'),
                  'managed-code': ('managed-code', '托管代码'), 'native-analysis': ('native-binary', '原生二进制'),
                  'dynamic-analysis': ('runtime and debugging', '运行时与调试'), 'firmware': ('firmware', '固件'),
                  'protocol-analysis': ('protocol', '协议'), 'reverse-engineering': ('general reverse-engineering', '通用逆向工程')}
SCAN_CLASS_TEXT = {1: ('installation and usage documented', '记录了安装与用法'),
                   2: ('installation or usage missing', '缺少安装或用法'),
                   3: ('no usable README documentation', '无可用的 README 文档')}


def n(value: int) -> str:
    return f'{value:,}'


def verb(count: int, plural: str, singular: str) -> str:
    return singular if count == 1 else plural


def series(items: list[str], zh: bool) -> str:
    if len(items) < 2:
        return ''.join(items)
    return ('、'.join(items[:-1]) + '和' + items[-1]) if zh else (', '.join(items[:-1]) + ' and ' + items[-1])


CJK = '\u3400-\u9fff'


def spaced(markup: str) -> str:
    """Chinese copy: one space between Han characters and Latin letters or digits, including at link edges."""
    markup = re.sub(f'([{CJK}])((?:<a [^>]*>)?[A-Za-z0-9])', r'\1 \2', markup)
    return re.sub(f'([A-Za-z0-9.)](?:</a>)?)([{CJK}])', r'\1 \2', markup)


def license_of(record: dict) -> str | None:
    value = record.get('license')
    return value if isinstance(value, str) and value.strip() and value.upper() != 'NOASSERTION' else None


def repo_link(record: dict) -> str:
    return f'<a href="{escape(record["url"], quote=True)}">{escape(record.get("full_name") or record["name"])}</a>'


def pushed(record: dict) -> datetime | None:
    value = record.get('pushed_at')
    if isinstance(value, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}T[^<>"&]*', value):
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    return None


def short_title(title: str) -> str:
    """The name part of a curated title such as "LibrePods: AirPods features on Android" or "REA — Reverse Engineer Anything"."""
    return re.split(r': | — ', title, maxsplit=1)[0]


def curated_entries(record: dict, zh: bool) -> list[tuple[str, str]]:
    """(name, page) for each curated entry; the English title's name part reads the same in both languages."""
    return [(short_title(entry['title_en']), entry[f'href_{"zh" if zh else "en"}'])
            for entry in record.get('related_entries', []) if entry.get('kind') == 'curated']


def table(category: str, records: list[dict], zh: bool, snapshot: str, json_href: str) -> str:
    rows = records[:ROWS]
    head = (('仓库', '星标', '许可证', '最近推送', '目标领域') if zh else ('Repository', 'Stars', 'License', 'Last push', 'Targets'))
    body = []
    for record in rows:
        stars = record.get('stars')
        when = pushed(record)
        targets = ', '.join(TARGETS[t][1 if zh else 0] for t in record.get('targets', []) if t in TARGETS)
        cells = [n(stars) if isinstance(stars, int) else '—', escape(license_of(record) or ('未识别' if zh else 'Not identified')),
                 when.strftime('%Y-%m') if when else '—', escape(targets) or '—']
        body.append('<tr><th scope="row">' + repo_link(record) + '</th>'
                    + ''.join(f'<td data-label="{label}">{value}</td>' for label, value in zip(head[1:], cells)) + '</tr>')
    caption = '怎么选' if zh else 'How to choose'
    source = (f'来源：本页按星标排在前 {len(rows)} 位的仓库，取自 <a href="{json_href}">分类 JSON</a>，{escape(snapshot)} 采集的 GitHub 元数据。'
              if zh else f'Source: the {len(rows)} most-starred repositories on this page, from the <a href="{json_href}">category JSON</a>; GitHub metadata captured {escape(snapshot)}.')
    return (f'<div class="guide-table"><table><caption id="guide-table-h">{caption}</caption><thead><tr>'
            + ''.join(f'<th scope="col">{label}</th>' for label in head) + '</tr></thead><tbody>' + ''.join(body)
            + f'</tbody></table><p class="guide-source">{source}</p></div>')


def faqs(category: str, label: str, records: list[dict], scan_classes: dict, zh: bool, snapshot: str) -> list[tuple[str, str]]:
    total = len(records)
    items = []
    starred = [r for r in records if isinstance(r.get('stars'), int)][:3]
    if starred:
        names = [f'{repo_link(r)}（{n(r["stars"])} 星标）' if zh else f'{repo_link(r)} ({n(r["stars"])} stars)' for r in starred]
        items.append((f'哪些{label}类仓库的星标最多？', f'{series(names, zh)}在采集时（{escape(snapshot)}）的 GitHub 星标最多。') if zh else
                     (f'Which {label} repositories have the most stars?', f'{series(names, zh)} had the most GitHub stars when the metadata was captured ({escape(snapshot)}).'))
    spelled: dict[str, Counter] = {}
    licenses = Counter()
    for record in records:
        value = license_of(record)
        if value:
            licenses[value.casefold()] += 1
            spelled.setdefault(value.casefold(), Counter())[value] += 1
    if licenses:
        missing = sum(license_of(r) is None for r in records)
        top = [(spelled[key].most_common(1)[0][0], count) for key, count in licenses.most_common(3)]
        if zh:
            text = f'最常见的许可证标识是{series([f"{escape(name)}（{n(count)} 个）" for name, count in top], zh)}。' + (f'{n(total)} 个仓库中有 {n(missing)} 个未识别许可证。' if missing else '')
            items.append(('这些仓库使用哪些许可证？', text))
        else:
            text = f'The most common license identifiers are {series([f"{escape(name)} ({n(count)})" for name, count in top], zh)}.' + (f' {n(missing)} of {n(total)} {verb(missing, "have", "has")} no identified license.' if missing else '')
            items.append(('Which licenses do these repositories use?', text))
    curated = [r for r in records if curated_entries(r, zh)]
    if curated:
        examples = series([f'<a href="{escape(href, quote=True)}">{escape(title)}</a>' for r in curated[:3] for title, href in curated_entries(r, zh)[:1]], zh)
        items.append(('其中哪些仓库有精选条目？', f'{n(total)} 个仓库中有 {n(len(curated))} 个链接到精选条目，条目附有审阅过的说明、使用条件和证据，例如{examples}。') if zh else
                     ('Which of these repositories have a curated entry?', f'{n(len(curated))} of {n(total)} {verb(len(curated), "link", "links")} a curated entry with a reviewed description, requirements and evidence, for example {examples}.'))
    classes = Counter(scan_classes.get(r['id']) for r in records)
    if any(classes[c] for c in SCAN_CLASS_TEXT):
        c1, c2, c3 = (classes[c] for c in SCAN_CLASS_TEXT)
        rest = total - c1 - c2 - c3
        if zh:
            text = f'{n(total)} 个仓库中有 {n(c1)} 个在 README 中同时写明了安装和用法（README 扫描档位 C1）'
            text += ''.join(f'，{n(count)} 个{detail}（C{c}）' for c, count, detail in ((2, c2, '缺少其中一项'), (3, c3, '没有可用的 README 文档')) if count) + '。'
            text += f'另有 {n(rest)} 个没有 README 扫描档位。' if rest else ''
            items.append(('这些仓库中有多少在 README 中写明了安装和用法？', text))
        else:
            tail = [f'{n(count)} {verb(count, "are", "is")} missing one of the two (C2)' if c == 2 else
                    f'{n(count)} {verb(count, "have", "has")} no usable README documentation (C3)'
                    for c, count in ((2, c2), (3, c3)) if count]
            text = f'{n(c1)} of {n(total)} {verb(c1, "document", "documents")} both installation and usage in their README (scan class C1).'
            text += f' {series(tail, zh)}.' if tail else ''
            text += f' {n(rest)} {verb(rest, "have", "has")} no README scan class.' if rest else ''
            items.append(('How many of these repositories document installation and usage in their README?', text))
    times = [pushed(r) for r in records]
    captured = datetime.fromisoformat(snapshot + 'T23:59:59+00:00') if re.fullmatch(r'\d{4}-\d{2}-\d{2}', snapshot or '') else None
    if captured and any(times):
        year = sum(1 for t in times if t and t >= captured - timedelta(days=365))
        month = sum(1 for t in times if t and t >= captured - timedelta(days=30))
        items.append(('这些仓库最近更新过吗？', f'截至 {escape(snapshot)}，{n(total)} 个仓库中有 {n(year)} 个在过去 12 个月内有推送，其中 {n(month)} 个在过去 30 天内有推送。') if zh else
                     ('How recently were these repositories updated?', f'As of {escape(snapshot)}, {n(year)} of {n(total)} had a push in the previous 12 months, and {n(month)} in the previous 30 days.'))
    return [(spaced(q), spaced(a)) for q, a in items[:5]] if zh else items[:5]


def faq_html(items: list[tuple[str, str]], zh: bool) -> str:
    entries = ''.join(f'<details><summary>{escape(q)}</summary><p>{answer}</p></details>' for q, answer in items)
    return f'<div class="guide-faq"><h2 id="guide-faq-h">{"常见问题" if zh else "Questions"}</h2>{entries}</div>'


def plain(markup: str) -> str:
    return unescape(re.sub(r'<[^>]+>', '', markup))


def faq_schema(items: list[tuple[str, str]], canonical: str, locale: str) -> dict:
    return {'@context': 'https://schema.org', '@type': 'FAQPage', '@id': canonical + '#faq', 'url': canonical, 'inLanguage': locale,
            'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}} for q, a in items]}


def guide(category: str, label: str, records: list[dict], scan_classes: dict, *, zh: bool, snapshot: str,
          json_href: str, canonical: str) -> tuple[str, dict, list[tuple[str, str]]]:
    """The guide section, its FAQPage node and the question pairs for one category page; an empty category has none."""
    if not records:
        return '', None, []
    items = faqs(category, QUESTION_NAMES[category][1 if zh else 0], records, scan_classes, zh, snapshot)
    section = ('<section class="browse-guide" id="how-to-choose" aria-labelledby="guide-table-h">'
               + table(category, records, zh, snapshot, json_href) + faq_html(items, zh) + '</section>')
    return section, faq_schema(items, canonical, 'zh-CN' if zh else 'en'), items


def definition(category: str, zh: bool) -> str:
    return DEFINITIONS[category][1 if zh else 0]


def markdown_notes(items: list[tuple[str, str]], zh: bool) -> list[str]:
    return [('**' + q + '** ' + plain(a)) for q, a in items]
