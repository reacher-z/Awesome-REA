"""Shared Open Graph and Twitter card metadata for every generated HTML page."""
from __future__ import annotations

from html import escape
from pathlib import Path

from structured_data import publisher_reference, search_action

SOCIAL_CARD = Path(__file__).resolve().parents[1] / 'site' / 'social-card.png'
# One site name for og:site_name and the homepage WebSite node, which every other page
# references by @id; alternates follow in order of preference
# (https://developers.google.com/search/docs/appearance/site-names).
SITE_NAME = 'Awesome REA'
SITE_ALTERNATE_NAMES = ['Awesome Reverse Engineering Anything', 'AwesomeREA']
OG_LOCALES = {'en': 'en_US', 'zh': 'zh_CN'}
# Browser chrome follows the page canvas in each color scheme (--bg in site/shell.css, --paper in site/styles.css).
THEME_COLOR_META = ('<meta name="theme-color" content="#faf3dd" media="(prefers-color-scheme: light)">'
                    '<meta name="theme-color" content="#1c1316" media="(prefers-color-scheme: dark)">')
# og:image:alt describes the shared card itself (https://ogp.me/), never the page title.
SOCIAL_IMAGE_ALT = {
    'en': 'Awesome REA card on cream grid paper: the heading “Awesome Reverse Engineering Anything” and the line “Tools, projects and resources for websites, games, apps, binaries, firmware and protocols.”',
    'zh': 'Awesome REA 分享图，米色网格纸上写着英文标题“Awesome Reverse Engineering Anything”和一行说明：面向网站、游戏、应用、二进制、固件和协议的工具、项目与资源。',
}


def png_size(path: Path) -> tuple[int, int]:
    """Read a PNG's width and height from its IHDR chunk."""
    header = Path(path).read_bytes()[:24]
    if header[:8] != b'\x89PNG\r\n\x1a\n' or header[12:16] != b'IHDR':
        raise ValueError('The social card must be a PNG image')
    return int.from_bytes(header[16:20], 'big'), int.from_bytes(header[20:24], 'big')


def website_node(site_url: str, repository_url: str) -> dict:
    """The WebSite entity, defined only on the two homepages."""
    return {'@type': 'WebSite', '@id': site_url + '/#website', 'url': site_url + '/', 'name': SITE_NAME,
            'alternateName': SITE_ALTERNATE_NAMES, 'inLanguage': ['en', 'zh-CN'], 'sameAs': repository_url,
            'publisher': publisher_reference(site_url), 'potentialAction': search_action(site_url)}


def website_reference(site_url: str) -> dict:
    return {'@id': site_url + '/#website'}


def open_graph_meta(*, language: str, title: str, description: str, image_url: str,
                    url: str | None, paired: bool = True, card: Path = SOCIAL_CARD, og_type: str = 'website',
                    image_alt: str | None = None) -> str:
    """Emit the Open Graph and Twitter card block shared by every generated page.

    Pages without a canonical address (the 404 template) pass ``url=None``; ``paired``
    pages also name their counterpart's locale. Image facts are read from the card; a page with its own
    card under /og/ passes that card and ``image_alt``. Entry pages pass ``og_type='article'``.
    """
    width, height = png_size(card)
    image_alt = image_alt or SOCIAL_IMAGE_ALT[language]
    tags = [('property', 'og:type', og_type), ('property', 'og:site_name', SITE_NAME),
            ('property', 'og:locale', OG_LOCALES[language])]
    if paired:
        tags.append(('property', 'og:locale:alternate', OG_LOCALES['en' if language == 'zh' else 'zh']))
    tags += [('property', 'og:title', title), ('property', 'og:description', description)]
    if url:
        tags.append(('property', 'og:url', url))
    tags += [('property', 'og:image', image_url), ('property', 'og:image:type', 'image/png'),
             ('property', 'og:image:width', str(width)), ('property', 'og:image:height', str(height)),
             ('property', 'og:image:alt', image_alt),
             ('name', 'twitter:card', 'summary_large_image'), ('name', 'twitter:title', title),
             ('name', 'twitter:description', description), ('name', 'twitter:image', image_url),
             ('name', 'twitter:image:alt', image_alt)]
    return '\n  '.join(f'<meta {kind}="{key}" content="{escape(value, quote=True)}">' for kind, key, value in tags)
