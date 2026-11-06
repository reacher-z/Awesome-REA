"""The one header, mobile bar, search palette and icon set every page shares.

Page builders that have not been ported to the redesign still write their own header; apply_site_shell()
replaces it on the finished page, so all of them draw the same chrome from this module. The footer comes from
site_footer.py. Everything here is a pure function of tracked data: IndexNow compares a CI rebuild with the
deployed site byte for byte, so nothing here may read the clock or the network.
"""
from __future__ import annotations

import base64
import hashlib
import json
from html import escape
from pathlib import Path
import re

from asset_paths import fingerprinted_href
from open_graph import THEME_COLOR_META
from site_footer import site_footer

ROOT = Path(__file__).resolve().parents[1]
STATS_PATH = ROOT / 'data/repository-stats.json'
LEGACY_HEADER = re.compile(r'<header class="site-header"><div class="shell header-inner">.*?</div></header>', re.S)
EXPLORER_FOOTER = re.compile(r'<footer class="site-footer"><div class="shell footer-top"><p data-i18n=.*?</footer>', re.S)
# Links into the filters of the collection, which now live on the explorer, and work there without a redirect.
EXPLORER_LINK = re.compile(r'href="(/zh)?/\?(?=view=)')
LANGUAGE_LINK = re.compile(r'<a\b(?=[^>]*\bhreflang="(en|zh-CN)")[^>]*>')
FONT_PRELOADS = ('eb-garamond-500-core.woff2', 'ibm-plex-sans-core.woff2')
# Runs before first paint, so a saved theme never flashes. site/_headers allows exactly this script by hash.
# Runs before first paint: the saved theme, and a dismissed announcement stays away without a layout shift.
THEME_SCRIPT = ("(function(d){d.className=d.className.replace('no-js','js');try{var t=localStorage.getItem('rea-theme');"
                "if(t==='light'||t==='dark')d.dataset.theme=t;if(localStorage.getItem('rea-ann-websitebench'))d.className+=' ann-off'}"
                "catch(e){}})(document.documentElement)")
WEBSITEBENCH_URL = 'https://github.com/TIGER-AI-Lab/WebsiteBench'

ICONS = {
    'search': '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5 21 21"/>',
    'close': '<path d="M6 6l12 12M18 6 6 18"/>',
    'star': '<path fill="currentColor" stroke="none" d="M12 3.2l2.7 5.6 6.1.8-4.5 4.3 1.1 6.1L12 17.1 6.6 20l1.1-6.1-4.5-4.3 6.1-.8z"/>',
    'external': '<path d="M8 16 16 8M9.5 8H16v6.5"/>',
    'arrow': '<path d="M4 12h15M14 7l5 5-5 5"/>',
    'check': '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    'chevron': '<path d="M7 10l5 5 5-5"/>',
    'copy': '<path d="M8.5 8.5h11v11h-11z"/><path d="M15.5 8.5v-4h-11v11h4"/>',
    'sun': '<circle cx="12" cy="12" r="4"/><path d="M12 2.5V5M12 19v2.5M2.5 12H5M19 12h2.5M5.3 5.3l1.8 1.8M16.9 16.9l1.8 1.8M5.3 18.7l1.8-1.8M16.9 7.1l1.8-1.8"/>',
    'moon': '<path d="M19.5 14.6A7.8 7.8 0 0 1 9.4 4.5a7.8 7.8 0 1 0 10.1 10.1z"/>',
    'system': '<circle cx="12" cy="12" r="8"/><path d="M12 4a8 8 0 0 1 0 16z" fill="currentColor" stroke="none"/>',
    'website': '<path d="M3 4.5h18v15H3z"/><path d="M3 8.5h18M5.8 6.5h1M8.3 6.5h1"/>',
    'game': '<path d="M7.5 8h9a4.5 4.5 0 0 1 4.5 4.5v2.7a2.3 2.3 0 0 1-4.2 1.3L15.5 15h-7l-1.3 1.5A2.3 2.3 0 0 1 3 15.2v-2.7A4.5 4.5 0 0 1 7.5 8z"/><path d="M8 10.3v3.4M6.3 12h3.4M15.3 11h.9M16.8 13h.9"/>',
    'app': '<path d="M7 2.5h10v19H7z"/><path d="M10.5 18.5h3"/>',
    'binary': '<path d="M4 5h3M10 5h10M4 9.7h3M10 9.7h7M4 14.3h3M10 14.3h9M4 19h3M10 19h5"/>',
    'firmware': '<path d="M7 7h10v10H7z"/><path d="M10 7V4M14 7V4M10 20v-3M14 20v-3M7 10H4M7 14H4M20 10h-3M20 14h-3M10.5 10.5h3v3h-3z"/>',
    'protocol': '<path d="M4 8.5h15M15.5 5 19 8.5 15.5 12M20 15.5H5M8.5 12 5 15.5 8.5 19"/>',
    'reg': '<circle cx="12" cy="12" r="5.5"/><path d="M12 1.5v21M1.5 12h21"/>',
    'filter': '<path d="M4 7h9.5M18.5 7H20M4 17h3.5M12.5 17H20"/><circle cx="16" cy="7" r="2.3"/><circle cx="10" cy="17" r="2.3"/>',
}
GITHUB_MARK = ('<symbol id="i-github" viewBox="0 0 16 16"><path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59'
               '.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53'
               '.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15'
               '-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16'
               ' 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46'
               '.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></symbol>')

LABELS = {
    'en': {'skip': 'Skip to content', 'home': 'Awesome REA home', 'nav': 'Main', 'resources': 'Resources', 'cases': 'Cases',
           'papers': 'Papers', 'repos': 'Repositories', 'repos_short': 'Repos', 'api': 'API', 'search': 'Search',
           'search_long': 'Search the catalogue', 'lang_switch': '中文', 'lang_name': '简体中文', 'theme': 'Colour theme',
           'stars': 'stars on GitHub', 'star': 'Star', 'star_on_github': 'Star Awesome REA on GitHub',
           'ann_name': 'Announcement', 'ann_new': 'New:', 'ann_line': 'Can AI agents rebuild websites through browser exploration?',
           'ann_star': 'Star on GitHub', 'ann_close': 'Dismiss this announcement', 'placeholder': 'Search tools, cases and papers', 'move': 'move', 'open': 'open',
           'tab': 'new tab', 'results': 'Results', 'esc': 'Close search'},
    'zh': {'skip': '跳到正文', 'home': 'Awesome REA 首页', 'nav': '主导航', 'resources': '资源', 'cases': '案例',
           'papers': '论文', 'repos': '仓库', 'repos_short': '仓库', 'api': 'API', 'search': '搜索',
           'search_long': '搜索目录', 'lang_switch': 'EN', 'lang_name': 'English', 'theme': '颜色主题',
           'stars': 'GitHub 星标', 'star': 'Star', 'star_on_github': '在 GitHub 上为 Awesome REA 加星',
           'ann_name': '公告', 'ann_new': '新发布：', 'ann_line': 'AI 智能体能否通过浏览器探索重建网站？',
           'ann_star': '在 GitHub 上加星', 'ann_close': '关闭此公告', 'placeholder': '搜索工具、案例与论文', 'move': '移动', 'open': '打开',
           'tab': '新标签页', 'results': '结果', 'esc': '关闭搜索'},
}


def theme_script_hash() -> str:
    """The value site/_headers lists in script-src; validate_site.py keeps the two equal."""
    digest = hashlib.sha256(THEME_SCRIPT.encode('utf-8')).digest()
    return "'sha256-" + base64.b64encode(digest).decode('ascii') + "'"


def repository_stars(repository: str = 'reacher-z/Awesome-REA') -> int | None:
    """A repository's stars as last recorded in the tracked data file, or None when it has no recorded count."""
    try:
        stars = json.loads(STATS_PATH.read_text(encoding='utf-8'))['github_stars'][repository]
    except (OSError, KeyError, ValueError, TypeError):
        return None
    return stars if type(stars) is int and stars >= 0 else None


def compact_count(value: int) -> str:
    """1,032 reads 1.0k: rounded, so one more star does not change the bytes of every page."""
    return f'{value / 1000:.1f}k' if value >= 1000 else str(value)


def sprite(skip: frozenset[str] = frozenset()) -> str:
    body = ''.join(f'<symbol id="i-{name}" viewBox="0 0 24 24">{paths}</symbol>' for name, paths in ICONS.items() if name not in skip)
    mark = '' if 'github' in skip else GITHUB_MARK
    return f'<svg class="sprite" aria-hidden="true" focusable="false">{body}{mark}</svg>'


def icon(name: str, css_class: str = '') -> str:
    return f'<svg class="i{(" " + css_class) if css_class else ""}" aria-hidden="true" focusable="false"><use href="#i-{name}"/></svg>'


def _section(path: str) -> str:
    """The nav key a page path belongs to."""
    parts = path.removeprefix('zh/').split('/')
    return {'resources': 'resources', 'cases': 'cases', 'papers': 'papers', 'browse': 'repos', 'api': 'api'}.get(parts[0], '')


def header(language: str, current: str, language_link: str, repository_url: str) -> str:
    labels = LABELS[language]
    zh = language == 'zh'
    prefix = '/zh' if zh else ''
    links = []
    for key, target in (('resources', '/resources/'), ('cases', '/cases/'), ('papers', '/papers/'), ('repos', '/browse/'), ('api', '/api/')):
        # "Repositories" has a short form so the five links fit a 375-px phone without scrolling.
        text = (f'<span class="nl-long">{labels[key]}</span><span class="nl-short">{labels["repos_short"]}</span>' if key == 'repos' else labels[key])
        state = ' aria-current="page"' if key == current else ''
        links.append(f'<a href="{prefix}{target}"{state}>{text}</a>')
    stars = repository_stars()
    count = f'<span class="gh-count">{compact_count(stars)}</span>' if stars is not None else ''
    star_name = f'{labels["star_on_github"]}, {compact_count(stars)} {labels["stars"]}' if stars is not None else labels['star_on_github']
    return (f'<header class="site-header"><div class="wrap header-row">'
            f'<a class="brand" href="{prefix}/" aria-label="{labels["home"]}">{icon("reg", "brand-mark")}<span class="brand-word">Awesome <span>REA</span></span></a>'
            f'<nav class="primary-nav" aria-label="{labels["nav"]}">{"".join(links)}</nav>'
            f'<div class="header-tools">'
            f'<button class="search-trigger" type="button" data-palette-open aria-keyshortcuts="Meta+K Control+K" aria-haspopup="dialog">{icon("search")}<span class="st-label">{labels["search"]}</span><kbd class="st-kbd" data-kbd aria-hidden="true">⌘K</kbd></button>'
            f'{language_link}'
            f'<button class="theme-toggle" type="button" data-theme-toggle aria-label="{labels["theme"]}: system">{icon("system", "ti-system")}{icon("sun", "ti-light")}{icon("moon", "ti-dark")}</button>'
            f'<a class="gh" href="{escape(repository_url, quote=True)}" rel="noopener" aria-label="{star_name}">{icon("star")}<span class="gh-star">{labels["star"]}</span>{count}</a>'
            f'</div></div></header>')


def announcement_bar(language: str) -> str:
    """The one site-wide announcement. Static and reserved in the layout, so it works without JavaScript and shifts nothing."""
    labels = LABELS[language]
    stars = repository_stars('TIGER-AI-Lab/WebsiteBench')
    count = f'<span class="ann-count">{compact_count(stars)}</span>' if stars is not None else ''
    sep = '<span class="ann-sep" aria-hidden="true">·</span>'
    return (f'<aside class="ann" aria-label="{labels["ann_name"]}"><div class="wrap ann-row">'
            f'<a class="ann-link" href="{WEBSITEBENCH_URL}" rel="noopener">'
            f'<span class="ann-long"><span class="ann-new">{labels["ann_new"]}</span> <strong>WebsiteBench.</strong> {labels["ann_line"]}</span>'
            f'<span class="ann-short"><strong>WebsiteBench</strong>{sep}{labels["star"]}{sep}</span>'
            f'<span class="ann-cta">{icon("star")}<span class="ann-long">{labels["ann_star"]}</span>{count}</span></a>'
            f'<button class="ann-close" type="button" data-ann-close aria-label="{labels["ann_close"]}">{icon("close")}</button>'
            f'</div></aside>')


def plain_language_link(language: str, counterpart: str) -> str:
    labels = LABELS[language]
    other = 'en' if language == 'zh' else 'zh-CN'
    return f'<a class="tool-lang" href="{escape(counterpart, quote=True)}" lang="{other}" hreflang="{other}" title="{labels["lang_name"]}">{labels["lang_switch"]}</a>'


def mobile_bar(language: str) -> str:
    labels = LABELS[language]
    home = '/zh/' if language == 'zh' else '/'
    return (f'<div class="mbar" data-mbar><a class="mbar-home" href="{home}" aria-label="{labels["home"]}">{icon("reg", "brand-mark")}</a>'
            f'<button class="mbar-search" type="button" data-palette-open aria-haspopup="dialog">{icon("search")}<span>{labels["search_long"]}</span></button>'
            f'<button class="theme-toggle" type="button" data-theme-toggle aria-label="{labels["theme"]}: system">{icon("system", "ti-system")}{icon("sun", "ti-light")}{icon("moon", "ti-dark")}</button></div>')


def palette(language: str) -> str:
    labels = LABELS[language]
    return (f'<dialog class="palette" id="palette" aria-label="{labels["search_long"]}" data-palette>'
            f'<div class="pal-field">{icon("search")}'
            f'<input id="pal-q" type="search" placeholder="{labels["placeholder"]}" autocomplete="off" autocapitalize="off" spellcheck="false" enterkeyhint="go" '
            f'role="combobox" aria-expanded="false" aria-controls="pal-list" aria-autocomplete="list" aria-label="{labels["search_long"]}" data-pal-input>'
            f'<button class="pal-esc" type="button" data-pal-close><kbd>esc</kbd><span class="vh"> {labels["esc"]}</span></button></div>'
            f'<div class="pal-body" data-pal-body><div class="pal-list" id="pal-list" role="listbox" aria-label="{labels["results"]}" data-pal-list hidden></div><div class="pal-extra" data-pal-extra></div></div>'
            f'<div class="pal-foot"><span><kbd>↑</kbd><kbd>↓</kbd> {labels["move"]}</span><span><kbd>↵</kbd> {labels["open"]}</span><span><kbd data-kbd-mod>⌘</kbd><kbd>↵</kbd> {labels["tab"]}</span><span class="pal-count" aria-live="polite" data-pal-count></span></div>'
            f'</dialog>')


def head_early() -> str:
    """Theme before first paint, then the only two font files worth preloading."""
    preloads = ''.join(f'<link rel="preload" href="/fonts/{name}" as="font" type="font/woff2" crossorigin>' for name in FONT_PRELOADS)
    return f'<meta name="color-scheme" content="light dark"><script>{THEME_SCRIPT}</script>{preloads}'


def shell_assets(site_dir: Path) -> str:
    """The shared stylesheet and script; the stylesheet comes last so its tokens win over a page's own."""
    return (f'<link rel="stylesheet" href="{fingerprinted_href(site_dir, "shell.css")}">'
            f'<script src="{fingerprinted_href(site_dir, "site.js")}" defer></script>')


def _shell_language_link(old_header: str, language: str, counterpart: str) -> str:
    """Reuse the page's language link, which may carry attributes its scripts read; only its look changes."""
    wanted = 'en' if language == 'zh' else 'zh-CN'
    for match in LANGUAGE_LINK.finditer(old_header):
        if match.group(1) == wanted:
            # paper-search.js finds its link by this class, to carry the filters across languages.
            script_class = ' papers-language' if 'papers-language' in match.group(0) else ''
            tag = re.sub(r'\s(?:class|aria-current)="[^"]*"', '', match.group(0))
            labels = LABELS[language]
            return f'{tag[:-1]} class="tool-lang{script_class}" title="{labels["lang_name"]}">{labels["lang_switch"]}</a>'
    return plain_language_link(language, counterpart)


def apply_site_shell(site_dir: Path, *, repository_url: str, skip: frozenset[str] = frozenset()) -> int:
    """Give every generated page the shared chrome; return the number of pages changed."""
    site_dir = Path(site_dir)
    changed = 0
    assets = shell_assets(site_dir)
    for page in sorted(site_dir.rglob('*.html')):
        relative = page.relative_to(site_dir).as_posix()
        if relative in skip:
            continue
        html = page.read_text(encoding='utf-8')
        old = LEGACY_HEADER.search(html)
        if not old:
            continue
        zh = relative == 'zh' or relative.startswith('zh/')
        language = 'zh' if zh else 'en'
        counterpart = '/' if zh else '/zh/'
        path = relative.removesuffix('index.html').removesuffix('/')
        new_header = header(language, _section(path), _shell_language_link(old.group(0), language, counterpart), repository_url)
        html = html[:old.start()] + announcement_bar(language) + new_header + mobile_bar(language) + html[old.end():]
        html = _with_shared_footer(html, language, repository_url)
        html = _with_html_attributes(html)
        html = EXPLORER_LINK.sub(r'href="\1/explore/?', html)
        html = html.replace(THEME_COLOR_META, THEME_COLOR_META + head_early(), 1) if THEME_COLOR_META in html else _before_title(html)
        if html.count('</head>') != 1 or html.count('</body>') != 1:
            raise ValueError(f'{relative}: expected exactly one head and body')
        html = html.replace('</head>', assets + '\n</head>')
        existing = frozenset(re.findall(r'\bid="i-([a-z-]+)"', html))
        html = re.sub(r'(<body\b[^>]*>)', lambda match: match.group(1) + sprite(existing), html, count=1)
        html = html.replace('</body>', palette(language) + '\n</body>')
        page.write_text(html, encoding='utf-8')
        changed += 1
    return changed


def _with_shared_footer(html: str, language: str, repository_url: str) -> str:
    """The explorer's footer is localized from app.js strings; it becomes the shared one, keeping the IDs app.js sets."""
    match = EXPLORER_FOOTER.search(html)
    if not match:
        return html
    export = 'source-published.json' if '"/source-published.json"' in match.group(0) or 'href="source-published.json"' in match.group(0) else 'source-index.json'
    note = re.search(r'<div class="shell footer-bottom">(.*?)</div></footer>', match.group(0), re.S)
    footer = site_footer(language, note=re.sub(r'<[^>]+>', '', note.group(1)) if note else '', repository_url=repository_url, repository_export=export)
    footer = re.sub(r'<a href="((?:/zh)?/browse/)"', r'<a id="browse-directory" href="\1"', footer, count=1)
    footer = footer.replace('<a href="/catalog.json"', '<a id="download-curated-catalog" href="/catalog.json"', 1)
    footer = footer.replace(f'<a href="/{export}"', f'<a id="download-source-index" href="/{export}"', 1)
    return html[:match.start()] + footer + html[match.end():]


def _with_html_attributes(html: str) -> str:
    return re.sub(r'<html\b([^>]*)>', r'<html\1 data-site="rea" class="no-js">', html, count=1)


def _before_title(html: str) -> str:
    return re.sub(r'<title\b', lambda match: head_early() + match.group(0), html, count=1)


__all__ = ['apply_site_shell', 'header', 'mobile_bar', 'palette', 'sprite', 'icon', 'head_early', 'shell_assets',
           'plain_language_link', 'site_footer', 'theme_script_hash', 'repository_stars', 'compact_count']
