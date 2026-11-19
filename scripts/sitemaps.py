"""Sitemap index, per-section sitemaps and the data dates behind each page's lastmod.

``/sitemap.xml`` is a sitemap index of four sitemaps at the site root, where each may list any page of the
site (https://www.sitemaps.org/protocol.html#location): pages, resources, papers and categories. A section
without pages, such as categories when the repository index is absent, is left out of the index.

Every URL lists its English, Chinese and x-default alternates, as the page's own hreflang links do. Its
``lastmod`` comes from the records the page shows, never from the build time, so rebuilding a commit gives
the same files: an entry page uses the later of its record's ``added_at`` and ``verified_at``, a listing the
newest of its records, the repository pages the selection's publication time, the discovery list its latest
ingest, the survey its version date, the catalog-wide pages (home, about, contribute) the newest of all of those, and
the API guide the newest of those and both unreviewed queues, like the API's own generated_at.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape as xml_escape, quoteattr

SITEMAP_INDEX = 'sitemap.xml'
SECTIONS = ('pages', 'resources', 'papers', 'categories')
SECTION_FILES = {section: f'sitemap-{section}.xml' for section in SECTIONS}
SITEMAP_NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'
XHTML_NS = 'http://www.w3.org/1999/xhtml'
MAX_URLS = 50_000
# Pages that summarize the whole catalog: their counts and dates change with any curated, paper or repository data.
CATALOG_PAGES = ('/', '/about/', '/contribute/')
DATE = re.compile(r'\d{4}-\d{2}-\d{2}')
DATETIME = re.compile(r'(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})(?:\.\d+)?(Z|[+-]\d{2}:\d{2})')


def english_path(path: str) -> str:
    return path.removeprefix('/zh') if path.startswith('/zh/') else path


LISTING_PAGE = re.compile(r'(/(?:resources|cases)/)page/[1-9][0-9]*/')


def dated_path(path: str) -> str:
    """The English path whose date a page carries: a later static listing page takes its listing's date."""
    english = english_path(path)
    match = LISTING_PAGE.fullmatch(english)
    return match[1] if match else english


def section_for(path: str) -> str:
    """The sitemap that lists a root-relative page path."""
    english = english_path(path)
    if english in ('/resources/', '/cases/') or english.startswith(('/resources/', '/cases/page/')):
        return 'resources'
    if english.startswith('/papers/'):
        return 'papers'
    if english.startswith('/browse/'):
        return 'categories'
    return 'pages'


def normalized_date(value) -> str | None:
    """A recorded date or UTC timestamp in W3C Datetime form; whole seconds, ``Z`` for UTC."""
    if not isinstance(value, str):
        return None
    if DATE.fullmatch(value):
        return value
    match = DATETIME.fullmatch(value)
    if not match:
        return None
    zone = 'Z' if match[3] in ('Z', '+00:00', '-00:00') else match[3]
    return f'{match[1]}T{match[2]}{zone}'


def instant(value: str) -> datetime:
    """Order dates and timestamps together: a date counts as the start of its UTC day."""
    if DATE.fullmatch(value):
        return datetime.fromisoformat(value + 'T00:00:00+00:00')
    return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone.utc)


def latest(values) -> str | None:
    """The latest of the recorded dates, keeping its own precision; None when nothing is dated."""
    dated = [date for date in (normalized_date(value) for value in values) if date]
    return max(dated, key=lambda date: (instant(date), len(date))) if dated else None


def record_date(record: dict) -> str | None:
    """When a curated entry's page last changed: its inclusion or its latest source review."""
    return latest((record.get('added_at'), record.get('verified_at')))


def page_dates(*, resources: list[dict], papers: list[dict], repository_document: dict | None = None,
               discovery_batches: list[dict] | None = None, lead_batches: list[dict] | None = None,
               survey_date: str | None = None, discovery_class_pages: list[str] = ()) -> dict[str, str]:
    """Map every dated English page path to its lastmod; the /zh/ page of a pair shares its date."""
    dates: dict[str, str] = {}
    for record in resources:
        if record_date(record):
            dates[f"/resources/{record['id']}/"] = record_date(record)
    for paper in papers:
        if record_date(paper):
            dates[f"/papers/{paper['id']}/"] = record_date(paper)
    curated = latest(record_date(record) for record in resources)
    cases = latest(record_date(record) for record in resources if record.get('kind') == 'case-study')
    research = latest(record_date(paper) for paper in papers)
    for path, value in (('/resources/', curated), ('/cases/', cases), ('/papers/', research)):
        if value:
            dates[path] = value
    meta = (repository_document or {}).get('meta', {})
    published = meta.get('kind') == 'published-repository-selection'
    repositories = normalized_date(meta.get('published_at' if published else 'completed_at'))
    if repositories:
        # Every repository page shows records and the date of this one selection or scan snapshot.
        dates['/browse/'] = repositories
        from build_browse_pages import CATEGORIES
        dates.update({f'/browse/{category}/': repositories for category in CATEGORIES})
    discoveries = latest(batch.get('ingested_at') for batch in discovery_batches or [])
    if discoveries:
        dates['/discoveries/'] = discoveries
        # A class page lists records of the same batches as the list page.
        dates.update(dict.fromkeys(discovery_class_pages, discoveries))
    if normalized_date(survey_date):
        dates['/survey/'] = normalized_date(survey_date)
    catalog = latest((curated, research, repositories))
    if catalog:
        for path in CATALOG_PAGES:
            dates[path] = catalog
    # The API guide shows the API's generated_at: the newest of the catalog and both unreviewed queues.
    api = latest((catalog, discoveries, latest(batch.get('collected_at') for batch in lead_batches or [])))
    if api:
        dates['/api/'] = api
    return dates


def language_alternates(site_url: str, path: str) -> dict[str, str]:
    """The hreflang set every paired page declares in its <head>."""
    english = english_path(path)
    return {'en': site_url + english, 'zh-CN': site_url + '/zh' + english, 'x-default': site_url + english}


def urlset(site_url: str, paths: list[str], dates: dict[str, str]) -> str:
    rows = []
    for path in paths:
        alternates = ''.join(f'<xhtml:link rel="alternate" hreflang="{language}" href={quoteattr(url)}/>'
                             for language, url in language_alternates(site_url, path).items())
        date = dates.get(dated_path(path))
        rows.append(f'<url><loc>{xml_escape(site_url + path)}</loc>{f"<lastmod>{date}</lastmod>" if date else ""}{alternates}</url>')
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="{SITEMAP_NS}" xmlns:xhtml="{XHTML_NS}">\n'
            + '\n'.join(rows) + '\n</urlset>\n')


def write_sitemaps(output: Path, site_url: str, paths: list[str], dates: dict[str, str]) -> dict[str, list[str]]:
    """Write the index and its sitemaps; return each written section's page paths in order."""
    output, site_url = Path(output), site_url.rstrip('/')
    if len(paths) != len(set(paths)):
        raise ValueError('Duplicate sitemap paths')
    sections: dict[str, list[str]] = {section: [] for section in SECTIONS}
    for path in paths:
        if not path.startswith('/') or not path.endswith('/') or '//' in path:
            raise ValueError(f'Sitemap paths must be root-relative directory paths: {path}')
        sections[section_for(path)].append(path)
    written = {section: listed for section, listed in sections.items() if listed}
    index = []
    for section, listed in written.items():
        if len(listed) > MAX_URLS:
            raise ValueError(f'The {section} sitemap exceeds {MAX_URLS} URLs; split it')
        (output / SECTION_FILES[section]).write_text(urlset(site_url, listed, dates), encoding='utf-8')
        date = latest(dates.get(dated_path(path)) for path in listed)
        index.append(f'<sitemap><loc>{xml_escape(site_url + "/" + SECTION_FILES[section])}</loc>'
                     f'{f"<lastmod>{date}</lastmod>" if date else ""}</sitemap>')
    (output / SITEMAP_INDEX).write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="{SITEMAP_NS}">\n' + '\n'.join(index) + '\n</sitemapindex>\n',
        encoding='utf-8')
    return written


def read_sitemaps(output: Path, site_url: str = 'https://awesomerea.org') -> tuple[dict[str, dict], dict[str, dict]]:
    """Parse the index and every sitemap it names from a built site.

    Returns (sitemaps, pages): each sitemap's URL with its file, lastmod and page URLs, and each page URL
    with its sitemap, lastmod and hreflang alternates. Only sitemaps at the site root are followed. A plain
    urlset at /sitemap.xml, as older builds wrote, is read as one sitemap.
    """
    output, site_url = Path(output), site_url.rstrip('/')
    root = ET.parse(output / SITEMAP_INDEX).getroot()
    sitemaps, pages = {}, {}

    def read_urlset(element, name):
        urls = []
        for node in element.findall(f'{{{SITEMAP_NS}}}url'):
            url = node.findtext(f'{{{SITEMAP_NS}}}loc')
            if not url or url in pages:
                raise ValueError(f'Missing or duplicate sitemap URL in {name}: {url}')
            alternates = {link.get('hreflang'): link.get('href') for link in node.findall(f'{{{XHTML_NS}}}link')
                          if link.get('rel') == 'alternate'}
            pages[url] = {'sitemap': name, 'lastmod': node.findtext(f'{{{SITEMAP_NS}}}lastmod'), 'alternates': alternates}
            urls.append(url)
        return urls

    if root.tag == f'{{{SITEMAP_NS}}}urlset':
        sitemaps[site_url + '/' + SITEMAP_INDEX] = {'file': SITEMAP_INDEX, 'lastmod': None, 'urls': read_urlset(root, SITEMAP_INDEX)}
        return sitemaps, pages
    if root.tag != f'{{{SITEMAP_NS}}}sitemapindex':
        raise ValueError('sitemap.xml must be a sitemap index or a urlset')
    for node in root.findall(f'{{{SITEMAP_NS}}}sitemap'):
        url = node.findtext(f'{{{SITEMAP_NS}}}loc') or ''
        name = url.removeprefix(site_url + '/')
        if not url.startswith(site_url + '/') or '/' in name or not re.fullmatch(r'sitemap-[a-z]+\.xml', name) or url in sitemaps:
            raise ValueError(f'Sitemap index entries must be distinct sitemap-<section>.xml files at the site root: {url}')
        sitemaps[url] = {'file': name, 'lastmod': node.findtext(f'{{{SITEMAP_NS}}}lastmod'),
                         'urls': read_urlset(ET.parse(output / name).getroot(), name)}
    return sitemaps, pages


def sitemap_urls(output: Path, site_url: str = 'https://awesomerea.org') -> list[str]:
    """Every page URL the built sitemaps list, in index order."""
    sitemaps, _ = read_sitemaps(output, site_url)
    return [url for sitemap in sitemaps.values() for url in sitemap['urls']]


def sitemap_files(output: Path, site_url: str = 'https://awesomerea.org') -> list[str]:
    """The index file followed by every sitemap file it names."""
    sitemaps, _ = read_sitemaps(output, site_url)
    return [SITEMAP_INDEX, *(sitemap['file'] for sitemap in sitemaps.values() if sitemap['file'] != SITEMAP_INDEX)]
