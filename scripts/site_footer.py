"""The footer every generated page shares: the same sections, one name per download, then GitHub.

site/index.html repeats the links with data-i18n keys, because the full explorer is localized from app.js strings.
"""
from __future__ import annotations

from html import escape

# Section links, in footer order: (path below the language prefix, English, Chinese).
SECTION_LINKS = (
    ('/resources/', 'Curated resources', '精选资源'),
    ('/cases/', 'Case studies', '案例合集'),
    ('/papers/', 'Research papers', '研究论文'),
    ('/browse/', 'Repository directory', '仓库目录'),
    ('/survey/', 'Editorial survey', '专题综述'),
    ('/about/', 'About and sources', '关于与来源'),
    ('/contribute/', 'Contribute', '投稿与贡献'),
)
# Each site-wide download keeps one English and one Chinese name wherever it is offered: footers,
# hero buttons and /about/. validate_site.py fails when the same file appears under a second label.
DOWNLOADS = {
    '/catalog.json': ('awesomerea-curated-catalog.json', 'application/json', 'Curated catalog JSON ↓', '精选目录 JSON ↓'),
    '/source-published.json': ('awesomerea-repository-index.json', 'application/json', 'Repository selection JSON ↓', '仓库选集 JSON ↓'),
    '/source-index.json': ('awesomerea-repository-index.json', 'application/json', 'Repository index JSON ↓', '仓库索引 JSON ↓'),
    '/papers.json': ('awesomerea-papers.json', 'application/json', 'Paper metadata JSON ↓', '论文元数据 JSON ↓'),
    '/papers/references.bib': ('awesomerea-papers.bib', 'application/x-bibtex', 'Paper BibTeX ↓', '论文 BibTeX ↓'),
}
REPOSITORY_EXPORTS = ('source-index.json', 'source-published.json')
TAGLINE = ('A resource collection, updated in public.', '资源合集，在公开协作中持续更新。')
HUGGING_FACE_URL = 'https://huggingface.co/datasets/AgPerry/awesome-rea'
FOOTER_TEXT = (
    {'sections': 'More from the collection', 'catalogue': 'Catalogue', 'data': 'Data', 'project': 'Project',
     'discoveries': 'Unreviewed discoveries', 'feed': 'Atom feed', 'dataset': 'Hugging Face dataset', 'cite': 'Cite',
     'licence': 'Licence', 'last_scan': 'Last scan', 'scan_fallback': 'Scan status', 'review': 'Review', 'method': 'Method',
     'sheet': 'Sitemap', 'sister': 'Sister catalogue', 'cua': 'Computer-Use Agents'},
    {'sections': '更多合集内容', 'catalogue': '目录', 'data': '数据', 'project': '项目',
     'discoveries': '未审核发现', 'feed': 'Atom 订阅', 'dataset': 'Hugging Face 数据集', 'cite': '引用',
     'licence': '许可', 'last_scan': '最近扫描', 'scan_fallback': '扫描状态', 'review': '审核', 'method': '方法',
     'sheet': '站点地图', 'sister': '姊妹目录', 'cua': '计算机使用智能体'},
)


def download_label(path: str, language: str) -> str:
    return DOWNLOADS[path][3 if language == 'zh' else 2]


def download_link(path: str, language: str, *, css_class: str = '', query: str = '') -> str:
    """One site-wide download, with its shared filename, media type and localized name."""
    filename, media_type, _, _ = DOWNLOADS[path]
    attribute = f' class="{escape(css_class, quote=True)}"' if css_class else ''
    return (f'<a{attribute} href="{path}{escape(query, quote=True)}" download="{filename}" type="{media_type}">'
            f'{escape(download_label(path, language))}</a>')


def footer_downloads(repository_export: str) -> tuple[str, ...]:
    if repository_export not in REPOSITORY_EXPORTS:
        raise ValueError('Unsupported repository export route')
    return ('/catalog.json', '/' + repository_export, '/papers.json', '/papers/references.bib')


def site_footer(language: str, *, note: str, repository_url: str,
                repository_export: str = 'source-index.json') -> str:
    """Render the shared footer, an engineering-drawing title block; ``note`` is the page's escaped licence line.

    site.js fills the last-scan cell from /discoveries/status.json, so that a new scan does not change the
    bytes of every page; without JavaScript the cell links to the discovery queue, which shows the time.
    """
    if language not in ('en', 'zh'):
        raise ValueError('Footer language must be en or zh')
    zh = language == 'zh'
    prefix = '/zh' if zh else ''
    text = FOOTER_TEXT[zh]
    sections = ''.join(f'<li><a href="{prefix}{path}">{chinese if zh else english}</a></li>' for path, english, chinese in SECTION_LINKS)
    downloads = ''.join(f'<li>{download_link(path, language)}</li>' for path in footer_downloads(repository_export))
    repository = escape(repository_url, quote=True)
    github = f'<li><a href="{repository}" target="_blank" rel="noopener">GitHub ↗</a></li>'
    extra_data = ''.join(f'<li><a href="{href}">{label}</a></li>' for href, label in (
        (f'{prefix}/api/', 'JSON API'), ('/llms.txt', 'llms.txt'), (f'{prefix}/feed.xml', text['feed'])))
    hugging_face = f'<li><a href="{HUGGING_FACE_URL}" rel="noopener">{text["dataset"]}</a></li>'
    discoveries = f'<li><a href="{prefix}/discoveries/">{text["discoveries"]}</a></li>'
    return (f'<footer class="site-footer"><div class="wrap"><div class="titleblock">'
            f'<div class="tb-cell tb-brand"><p class="tb-word"><svg class="i brand-mark" aria-hidden="true" focusable="false"><use href="#i-reg"/></svg><span>Awesome <span>REA</span></span></p>'
            f'<p class="tb-tag">{TAGLINE[zh]}</p><p class="tb-note">{note}</p></div>'
            f'<nav class="tb-cell tb-links" aria-label="{text["sections"]}"><h2 class="tb-label">{text["catalogue"]}</h2><ul>{sections}{discoveries}</ul></nav>'
            f'<nav class="tb-cell tb-links" aria-label="{text["data"]}"><h2 class="tb-label">{text["data"]}</h2><ul>{downloads}{extra_data}{hugging_face}</ul></nav>'
            f'<nav class="tb-cell tb-links" aria-label="{text["project"]}"><h2 class="tb-label">{text["project"]}</h2><ul>{github}<li><a href="{repository}/blob/main/CITATION.cff" rel="noopener">{text["cite"]}</a></li></ul></nav>'
            f'<dl class="tb-strip"><div class="tb-cell"><dt>{text["licence"]}</dt><dd>MIT</dd></div>'
            f'<div class="tb-cell"><dt>{text["last_scan"]}</dt><dd><a href="{prefix}/discoveries/"><span data-last-scan>{text["scan_fallback"]}</span></a></dd></div>'
            f'<div class="tb-cell"><dt>{text["review"]}</dt><dd><a href="{prefix}/about/">{text["method"]}</a></dd></div>'
            f'<div class="tb-cell"><dt>{text["sheet"]}</dt><dd><a href="/sitemap.xml">sitemap.xml</a></dd></div>'
            f'<div class="tb-cell tb-sister"><dt>{text["sister"]}</dt><dd><a href="https://awesomecua.com/">Awesome CUA <span class="tb-sub">{text["cua"]}</span></a></dd></div></dl>'
            f'</div></div><p class="colophon-word" aria-hidden="true"></p></footer>')
