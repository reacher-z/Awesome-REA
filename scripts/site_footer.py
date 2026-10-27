"""The footer every generated page shares: the same sections, one name per download, then GitHub.

site/index.html repeats this markup with data-i18n keys, because the homepage is localized from app.js strings.
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
TAGLINE = ('An independent resource collection, updated in public.', '独立的资源集合，在公开协作中持续更新。')


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
    """Render the shared footer; ``note`` is the page's escaped licence line."""
    if language not in ('en', 'zh'):
        raise ValueError('Footer language must be en or zh')
    zh = language == 'zh'
    prefix = '/zh' if zh else ''
    sections = ''.join(f'<a href="{prefix}{path}">{chinese if zh else english}</a>' for path, english, chinese in SECTION_LINKS)
    downloads = ''.join(download_link(path, language) for path in footer_downloads(repository_export))
    github = f'<a href="{escape(repository_url, quote=True)}" target="_blank" rel="noopener">GitHub ↗</a>'
    return (f'<footer class="site-footer"><div class="shell footer-top"><p>{TAGLINE[zh]}</p>'
            f'<nav class="footer-nav" aria-label="{"更多合集内容" if zh else "More from the collection"}">'
            f'<div class="footer-links">{sections}</div><div class="footer-links">{downloads}{github}</div></nav></div>'
            f'<div class="shell footer-bottom">{note}</div></footer>')
