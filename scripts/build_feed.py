"""Write Atom feeds of newly added curated entries and papers, never scan records."""
from __future__ import annotations

from html import escape
from pathlib import Path
import re
from xml.sax.saxutils import escape as xml_escape, quoteattr

from build_entry_pages import entry_path
from build_readme import KIND_LABELS

FEED_SIZE = 50
FEED_PATHS = {'en': '/feed.xml', 'zh': '/zh/feed.xml'}
# Listing pages that advertise the feed of their language: homepage, curated, cases and papers.
FEED_PAGES = ('', '/resources/', '/cases/', '/papers/')
FEED_TITLES = {'en': 'AwesomeREA.org: newly added entries', 'zh': 'AwesomeREA.org：新收录条目'}
FEED_SUBTITLES = {
    'en': 'Curated resources, case studies and research papers newly added to Awesome Reverse Engineering Anything.',
    'zh': 'Awesome Reverse Engineering Anything 新收录的精选资源、案例与研究论文。',
}
FEED_RIGHTS = {
    'en': 'Original editorial content: MIT. Linked projects and papers retain their own rights and licenses.',
    'zh': '原创说明采用 MIT 许可；外部项目与论文保留各自的权利和许可。',
}
PAPER_LABELS = ('Research paper', '研究论文')


def feed_entries(resources: list[dict], papers: list[dict], limit: int = FEED_SIZE) -> list[tuple[str, dict]]:
    """Return the newest (kind, record) pairs by inclusion date.

    Only records with ``added_at`` take part; ``verified_at`` is a review date and
    never stands in for it. Within one day, later catalog positions come first.
    """
    dated = []
    for position, (kind, record) in enumerate([*(('resource', r) for r in resources),
                                               *(('paper', p) for p in papers)]):
        added = record.get('added_at')
        if added is None:
            continue
        if not isinstance(added, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', added):
            raise ValueError(f'{record.get("id")}: added_at must be a YYYY-MM-DD date')
        dated.append((added, position, kind, record))
    dated.sort(key=lambda item: item[:2], reverse=True)
    return [(kind, record) for _, _, kind, record in dated[:limit]]


def _timestamp(date: str) -> str:
    return date + 'T00:00:00Z'


def atom_feed(entries: list[tuple[str, dict]], language: str, *, site_url: str, repository_url: str) -> str:
    """Render one localized feed; entry IDs are the stable localized detail-page URLs."""
    zh = language == 'zh'
    if not entries:
        raise ValueError('An Atom feed needs at least one dated entry')
    feed_url = site_url + FEED_PATHS[language]
    home = site_url + ('/zh/' if zh else '/')
    rows = []
    for kind, record in entries:
        url = site_url + entry_path(kind, record['id'], language)
        if kind == 'resource':
            title = (record.get('name_zh') or record['name']) if zh else record['name']
            term, label = record['kind'], KIND_LABELS[record['kind']][int(zh)]
        else:
            title = record['title_zh'] if zh else record['title']
            term, label = 'paper', PAPER_LABELS[int(zh)]
        stamp = _timestamp(record['added_at'])
        rows.append(f'''  <entry>
    <id>{xml_escape(url)}</id>
    <title>{xml_escape(title)}</title>
    <link rel="alternate" type="text/html" href={quoteattr(url)}/>
    <published>{stamp}</published>
    <updated>{stamp}</updated>
    <category term={quoteattr(term)} label={quoteattr(label)}/>
    <summary>{xml_escape(record[f'description_{language}'])}</summary>
  </entry>''')
    rows = '\n'.join(rows)
    return f'''<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="{'zh-CN' if zh else 'en'}">
  <id>{xml_escape(feed_url)}</id>
  <title>{xml_escape(FEED_TITLES[language])}</title>
  <subtitle>{xml_escape(FEED_SUBTITLES[language])}</subtitle>
  <link rel="self" type="application/atom+xml" href={quoteattr(feed_url)}/>
  <link rel="alternate" type="text/html" href={quoteattr(home)}/>
  <updated>{_timestamp(entries[0][1]['added_at'])}</updated>
  <author><name>Awesome REA contributors</name><uri>{xml_escape(repository_url)}</uri></author>
  <rights>{xml_escape(FEED_RIGHTS[language])}</rights>
{rows}
</feed>
'''


def feed_link(language: str) -> str:
    return (f'<link rel="alternate" type="application/atom+xml" title="{escape(FEED_TITLES[language], quote=True)}" '
            f'href="{FEED_PATHS[language]}">')


def build_feeds(site_dir: Path, resources: list[dict], papers: list[dict], *,
                site_url: str = 'https://awesomerea.org',
                repository_url: str = 'https://github.com/reacher-z/Awesome-REA') -> list[str]:
    """Write both feeds and link them from the listing pages; return the feed paths.

    The feed date is the newest ``added_at``, not the build time, so rebuilding a
    commit is byte-identical. Without dated records no feed or link is written.
    """
    site_dir = Path(site_dir)
    entries = feed_entries(resources, papers)
    if not entries:
        return []
    for language, path in FEED_PATHS.items():
        (site_dir / path.lstrip('/')).write_text(
            atom_feed(entries, language, site_url=site_url.rstrip('/'), repository_url=repository_url),
            encoding='utf-8')
        prefix = '/zh' if language == 'zh' else ''
        for page in FEED_PAGES:
            target = site_dir / (prefix + page).lstrip('/') / 'index.html'
            html = target.read_text(encoding='utf-8')
            if html.count('</head>') != 1:
                raise ValueError(f'Feed link needs exactly one document head: {prefix + page or "/"}')
            target.write_text(html.replace('</head>', '  ' + feed_link(language) + '\n</head>'), encoding='utf-8')
    return list(FEED_PATHS.values())
