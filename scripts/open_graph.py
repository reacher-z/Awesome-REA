"""Shared Open Graph and Twitter card metadata for every generated HTML page."""
from __future__ import annotations

from html import escape
from pathlib import Path

SOCIAL_CARD = Path(__file__).resolve().parents[1] / 'site' / 'social-card.png'
# One site name for og:site_name and the homepage WebSite node, which every other page
# references by @id; alternates follow in order of preference
# (https://developers.google.com/search/docs/appearance/site-names).
SITE_NAME = 'Awesome Reverse Engineering Anything'
SITE_ALTERNATE_NAMES = ['AwesomeREA.org', 'Awesome REA']
OG_LOCALES = {'en': 'en_US', 'zh': 'zh_CN'}
# og:image:alt describes the shared card itself (https://ogp.me/), never the page title.
SOCIAL_IMAGE_ALT = {
    'en': 'AwesomeREA.org card showing the heading “Awesome Reverse Engineering Anything”, the tagline “Tools, projects, and resources” and six target labels: Website, Game, App, Native Binary, Firmware and Protocol.',
    'zh': 'AwesomeREA.org 分享图：英文标题“Awesome Reverse Engineering Anything”和标语“Tools, projects, and resources”，右侧列出六个目标领域：Website、Game、App、Native Binary、Firmware 和 Protocol。',
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
            'alternateName': SITE_ALTERNATE_NAMES, 'inLanguage': ['en', 'zh-CN'], 'sameAs': repository_url}


def website_reference(site_url: str) -> dict:
    return {'@id': site_url + '/#website'}


def open_graph_meta(*, language: str, title: str, description: str, image_url: str,
                    url: str | None, paired: bool = True, card: Path = SOCIAL_CARD) -> str:
    """Emit the Open Graph and Twitter card block shared by every generated page.

    Pages without a canonical address (the 404 template) pass ``url=None``; ``paired``
    pages also name their counterpart's locale. Image facts are read from the card.
    """
    width, height = png_size(card)
    tags = [('property', 'og:type', 'website'), ('property', 'og:site_name', SITE_NAME),
            ('property', 'og:locale', OG_LOCALES[language])]
    if paired:
        tags.append(('property', 'og:locale:alternate', OG_LOCALES['en' if language == 'zh' else 'zh']))
    tags += [('property', 'og:title', title), ('property', 'og:description', description)]
    if url:
        tags.append(('property', 'og:url', url))
    tags += [('property', 'og:image', image_url), ('property', 'og:image:type', 'image/png'),
             ('property', 'og:image:width', str(width)), ('property', 'og:image:height', str(height)),
             ('property', 'og:image:alt', SOCIAL_IMAGE_ALT[language]),
             ('name', 'twitter:card', 'summary_large_image'), ('name', 'twitter:title', title),
             ('name', 'twitter:description', description), ('name', 'twitter:image', image_url),
             ('name', 'twitter:image:alt', SOCIAL_IMAGE_ALT[language])]
    return '\n  '.join(f'<meta {kind}="{key}" content="{escape(value, quote=True)}">' for kind, key, value in tags)
