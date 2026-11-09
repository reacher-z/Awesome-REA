"""Publish the unreviewed discovery queue: list pages, Atom feeds, a JSON export and status files.

Records come from the validated batches in data/discoveries/ (scripts/discoveries.py). They are
automated README scans: every output labels them unreviewed and never as curated or source-reviewed.
A record that has since entered the reviewed repository index, or that a reviewer has curated, excluded or held,
is counted, not listed again.
"""
from __future__ import annotations

from datetime import datetime
from html import escape
import json
from pathlib import Path
import re
from xml.sax.saxutils import escape as xml_escape, quoteattr

from artifact_links import with_artifact_links
from build_browse_pages import repository_card
from build_discovery_pages import _IconStylesheet, _asset, _document, collection_page_schema
from source_descriptions import description_fallback
import discoveries
import discovery_classes
import discovery_reviews
from data_classes import DATA_CLASSES

PAGE_PATHS = {'en': '/discoveries/', 'zh': '/zh/discoveries/'}
FEED_PATHS = {'en': '/discoveries/feed.xml', 'zh': '/zh/discoveries/feed.xml'}
EXPORT_PATH = '/discoveries.json'
STATUS_PATH = '/discoveries/status.json'
BADGE_PATH = '/discoveries/badge.json'
REVIEWS_PATH = '/discoveries/reviews.json'
# each Data class shows its newest records up to this many, so every class appears on the page; a class with
# more has its own page listing every record, which the list page links and loads on demand
CLASS_RECORDS = 60
CLASS_PAGE_PATH = '/discoveries/{}/'
FEED_RECORDS = 100
# The index export lists the newest records; every listed record is also in its batch's own file.
EXPORT_RECORDS = 1_000
BATCH_EXPORT_DIRECTORY = '/discoveries/batches/'
MAIN_FEED_BATCHES = 10
STALE_AFTER_HOURS = 9
FEED_TERM = 'unreviewed-discovery'
FEED_LABELS = ('Unreviewed data point', '未审核的数据点')
TITLES = ('Recently discovered data points', '最新发现的数据点')
FEED_TITLES = ('AwesomeREA.org: recently discovered data points', 'AwesomeREA.org：最新发现的数据点')
EXPORT_FIELDS = ('id', 'full_name', 'url', 'topics', 'targets', 'category', 'stars', 'license', 'pushed_at',
                 'observed_at', 'readme_url', 'readme_sha256', 'readme_git_sha')
NOTE = ('Data points found in automated README scans, grouped by Data class.',
        '自动扫描 README 发现的数据点，按数据类别分组。')


def timestamp(value: str) -> str:
    """Normalize a recorded UTC timestamp to whole seconds with a Z suffix."""
    return discoveries.parse_time(value).strftime('%Y-%m-%dT%H:%M:%SZ')


def published_identities(published_document: dict | None) -> tuple[set[str], dict[str, str]]:
    rows = (published_document or {}).get('resources', [])
    return ({row.get('id') for row in rows},
            {str(row.get('full_name', '')).casefold(): row.get('id') for row in rows})


def discovery_queue(root: Path, published_document: dict | None, papers: list[dict], resources: list[dict]) -> dict:
    """Validated batches as a queue: listed records newest first, plus status and counts."""
    batches, problems = discoveries.load_batches(root)
    if problems:
        raise ValueError('Discovery batches failed validation: ' + '; '.join(problems[:3]))
    published_ids, published_names = published_identities(published_document)
    rows = [{**record, 'batch_id': batch['batch_id'], 'ingested_at': timestamp(batch['ingested_at'])}
            for batch in reversed(batches) for record in batch['resources']]
    curated = {str(record.get('url', '')).rstrip('/').casefold(): record['id'] for record in resources}
    pending, decided = discovery_reviews.split_queue(rows, discovery_reviews.read_reviews(root), curated)
    classes = discovery_classes.read_classes(root)
    listed, since_published = [], 0
    for record in pending:
        name = record['full_name'].casefold()
        if record['id'] in published_ids or published_names.get(name, record['id']) != record['id']:
            since_published += 1
        else:
            if record['id'] in classes:
                classification = classes[record['id']]
                record['data_decision'] = classification['decision']
                if classification['decision'] == 'data':
                    record['class'] = classification['class']
                    record['reproduced'] = classification['reproduced']
            listed.append(record)
    listed = with_artifact_links(listed, papers, resources)
    latest = batches[-1] if batches else None
    return {
        'batches': batches, 'listed': listed, 'decided': decided, 'since_published': since_published,
        'record_count': sum(len(batch['resources']) for batch in batches),
        'latest': latest,
    }


def run_url(batch: dict) -> str:
    return f"https://github.com/{discoveries.REPOSITORY}/actions/runs/{batch['source']['run_id']}"


def batch_file_url(repository_url: str, batch: dict) -> str:
    return f"{repository_url}/blob/main/{discoveries.DIRECTORY}/{batch['batch_id']}.json"


def awaiting_review(listed: list[dict]) -> int:
    """Records still in the review queue: data points and records the Data pass has not classified. Other captures leave it."""
    return sum(record.get('data_decision') != 'outside' for record in listed)


def export_record(record: dict) -> dict:
    value = {key: record[key] for key in EXPORT_FIELDS if key in record}
    value['description'] = record['description_en']
    value['description_language'] = 'upstream-original'
    if record.get('description_omission'):
        value['description_omitted'] = True
    for key in ('data_decision', 'class', 'reproduced'):
        if key in record:
            value[key] = record[key]
    value.update(verification='automated-readme-scan', review_status=discoveries.REVIEW_STATUS,
                 batch_id=record['batch_id'], ingested_at=record['ingested_at'])
    if record.get('related_entries'):
        value['related_entries'] = [{key: entry[key] for key in ('kind', 'id', 'href_en', 'href_zh') if key in entry}
                                    for entry in record['related_entries']]
    return value


def status_document(queue: dict, site_url: str) -> dict:
    """Status counts: listed awaits review, data_points and other_captures are decisions,
    and captures_listed includes every listed capture, including unclassified records.
    """
    latest = queue['latest']
    return {
        'version': 1, 'kind': 'automated-discovery-status',
        'last_successful_ingest_at': timestamp(latest['ingested_at']) if latest else None,
        'last_batch_id': latest['batch_id'] if latest else None,
        'last_scan_run_id': latest['source']['run_id'] if latest else None,
        'last_scan_run_url': run_url(latest) if latest else None,
        'stale_after_hours': STALE_AFTER_HOURS,
        'records': queue['record_count'], 'listed': awaiting_review(queue['listed']), 'batches': len(queue['batches']),
        'data_points': sum(r.get('data_decision') == 'data' for r in queue['listed']),
        'other_captures': sum(r.get('data_decision') == 'outside' for r in queue['listed']),
        'captures_listed': len(queue['listed']),
        'reviewed': discovery_reviews.counts(queue['decided']), 'reviews': site_url + REVIEWS_PATH,
        'page': site_url + PAGE_PATHS['en'], 'export': site_url + EXPORT_PATH,
        'note': 'Times are UTC and fixed when the site is built; compare last_successful_ingest_at with the '
                'current time to judge freshness (stale after stale_after_hours).',
    }


def export_document(queue: dict, site_url: str, repository_url: str) -> dict:
    latest = queue['latest']
    records = queue['listed'][:EXPORT_RECORDS]
    return {
        'version': 1, 'kind': 'automated-discovery-queue',
        'generated_at': timestamp(latest['ingested_at']) if latest else None,
        'review_status': discoveries.REVIEW_STATUS, 'verification': 'automated-readme-scan',
        'description': NOTE[0],
        'selection_policy': discoveries.POLICY,
        'status': status_document(queue, site_url),
        'counts': {'batches': len(queue['batches']), 'records': queue['record_count'],
                   'listed': len(queue['listed']), 'exported': len(records),
                   'since_published_in_repository_index': queue['since_published'],
                   'reviewed': discovery_reviews.counts(queue['decided'])},
        'pagination': ('resources lists the newest listed records; batches[].records_url lists every listed '
                       'record of each batch, so together they cover the whole queue.'),
        'class_pages': [{'class': name, 'data_points': len(records), 'page': site_url + class_page_path(name)}
                        for name, _, records in class_pages(queue)],
        'budget': {'records_per_batch': discoveries.MAX_BATCH_RECORDS, 'records': discoveries.MAX_TOTAL_RECORDS,
                   'bytes': discoveries.MAX_TOTAL_BYTES},
        'batches': [{'batch_id': batch['batch_id'], 'ingested_at': timestamp(batch['ingested_at']),
                     'record_count': len(batch['resources']),
                     'listed_count': sum(record['batch_id'] == batch['batch_id'] for record in queue['listed']),
                     'records_url': site_url + batch_export_path(batch['batch_id']), 'scan_run_url': run_url(batch),
                     'artifact_name': batch['source']['artifact_name'],
                     'checkpoint_sha256': batch['source']['checkpoint_sha256'],
                     'source_file': batch_file_url(repository_url, batch)} for batch in reversed(queue['batches'])],
        'resources': [export_record(record) for record in records],
    }


def batch_export_path(batch_id: str) -> str:
    return f'{BATCH_EXPORT_DIRECTORY}{batch_id}.json'


def batch_export(queue: dict, batch: dict) -> dict:
    """Every listed record of one batch, so the index export plus these files cover the whole queue."""
    return {'version': 1, 'kind': 'automated-discovery-batch-export', 'batch_id': batch['batch_id'],
            'ingested_at': timestamp(batch['ingested_at']), 'review_status': discoveries.REVIEW_STATUS,
            'verification': 'automated-readme-scan',
            'resources': [export_record(record) for record in queue['listed'] if record['batch_id'] == batch['batch_id']]}


def badge_document(queue: dict) -> dict:
    """A shields.io endpoint badge; its colour cannot change between builds, so it states the time only."""
    latest = queue['latest']
    message = (discoveries.parse_time(latest['ingested_at']).strftime('%Y-%m-%d %H:%M UTC') if latest else 'none yet')
    return {'schemaVersion': 1, 'label': 'last discovery ingest', 'message': message, 'color': '53309C',
            'labelColor': '303447'}


def card(record: dict, language: str, use_pro: bool) -> str:
    """The repository directory's card, one heading level down inside its section."""
    html = repository_card(record, language, use_pro)
    if language != 'zh' and record.get('data_decision') == 'data':
        detail = f'<p class="source-card-description">{escape(record["reproduced"])}</p>'
        html = html.replace('</p>\n', '</p>\n  ' + detail + '\n', 1)
    html = html.replace('<div class="source-card-head"><h2>', '<div class="source-card-head"><h3>', 1)
    html = html.replace('</a></h2></div>', '</a></h3></div>', 1)
    if html.count('<h3>') != 1 or '<h2' in html:
        raise ValueError('Unexpected repository card heading')
    return html


def class_records(queue: dict) -> dict[str, list[dict]]:
    """Every listed data point by class, in class order and newest first within each class."""
    groups = {name: [] for name in DATA_CLASSES}
    for record in queue['listed']:
        if record.get('data_decision') == 'data':
            groups[record['class']].append(record)
    return groups


def page_groups(queue: dict) -> list[tuple[str, tuple[str, str], list[dict], int]]:
    """Data points in class order, newest first within each class, up to CLASS_RECORDS per class."""
    groups = class_records(queue)
    return [(name, labels, groups[name][:CLASS_RECORDS], len(groups[name]))
            for name, labels in DATA_CLASSES.items() if groups[name]]


def class_page_path(name: str, language: str = 'en') -> str:
    return ('/zh' if language == 'zh' else '') + CLASS_PAGE_PATH.format(name)


def class_pages(queue: dict) -> list[tuple[str, tuple[str, str], list[dict]]]:
    """The classes with more data points than the list page shows, each with all of its records."""
    groups = class_records(queue)
    return [(name, labels, groups[name]) for name, labels in DATA_CLASSES.items() if len(groups[name]) > CLASS_RECORDS]


def class_section(name: str, labels: tuple[str, str], records: list[dict], total: int, language: str,
                  use_pro: bool, *, more: bool) -> str:
    """One class: its heading, cards and, when the list page holds back records, the link that shows them all."""
    zh = language == 'zh'
    label = labels[int(zh)]
    heading = (f'{label} · 显示 {len(records):,} 条，共 {total:,} 条' if zh else f'{label} · {len(records):,} of {total:,}')
    full = f'{label} · 共 {total:,} 条' if zh else f'{label} · {total:,} of {total:,}'
    section_id = f'class-{name}'
    footer = ''
    if more and total > len(records):
        rest = total - len(records)
        text = f'显示全部 {total:,} 条' if zh else f'Show all {total:,}'
        shown = (f'已显示 {len(records):,} / {total:,} 条' if zh else f'{len(records):,} of {total:,} shown')
        shown_all = (f'已显示全部 {total:,} 条' if zh else f'All {total:,} shown')
        footer = (f'<div class="load-more-row discovery-more"><a class="button button-outline" href="{class_page_path(name, language)}" '
                  f'data-discovery-more="{escape(name, quote=True)}">{escape(text)}<span class="mono">+{rest:,}</span></a>'
                  f'<p class="mono" aria-live="polite" data-shown-all="{escape(shown_all, quote=True)}">{escape(shown)}</p></div>')
    return (f'<section class="discovery-batch" id="{section_id}" aria-labelledby="{section_id}-title">'
            f'<h2 id="{section_id}-title" data-heading-all="{escape(full, quote=True)}">{escape(heading)}</h2>'
            '<div class="source-results browse-results">\n'
            + '\n'.join(card(record, language, use_pro) for record in records)
            + f'\n</div>{footer}</section>')


def page_content(queue: dict, language: str, use_pro: bool, site_url: str, repository_url: str) -> str:
    zh = language == 'zh'
    latest = queue['latest']
    groups = page_groups(queue)
    shown = [record for _, _, records, _ in groups for record in records]
    when = (discoveries.parse_time(latest['ingested_at']).strftime('%Y-%m-%d %H:%M UTC') if latest else '')
    status = ((f'最近一次成功入库：<time datetime="{timestamp(latest["ingested_at"])}">{when}</time>，'
               f'来自<a href="{escape(run_url(latest), quote=True)}" target="_blank" rel="noopener">扫描运行 {latest["source"]["run_id"]}</a>。'
               f'共 {queue["record_count"]:,} 条自动发现，分 {len(queue["batches"])} 批入库。')
              if zh else
              (f'Last successful ingest: <time datetime="{timestamp(latest["ingested_at"])}">{when}</time>, from '
               f'<a href="{escape(run_url(latest), quote=True)}" target="_blank" rel="noopener">scan run {latest["source"]["run_id"]}</a>. '
               f'{queue["record_count"]:,} automated discoveries in {len(queue["batches"])} batch{"" if len(queue["batches"]) == 1 else "es"}.')
              ) if latest else ('尚无自动发现。' if zh else 'No automated discoveries yet.')
    data_count = sum(record.get('data_decision') == 'data' for record in queue['listed'])
    outside_count = sum(record.get('data_decision') == 'outside' for record in queue['listed'])
    unclassified_count = len(queue['listed']) - data_count - outside_count
    raw_download = f'<a href="{EXPORT_PATH}">{"原始数据下载" if zh else "raw download"}</a>'
    status += (f' 数据点：共 {data_count:,} 条，本页显示 <span data-discovery-shown>{len(shown):,}</span> 条；另有 {outside_count:,} 条其他采集记录和 '
               f'{unclassified_count:,} 条待分类记录，详见{raw_download}及各批次文件。' if zh else
               f' Data points: {data_count:,} listed, <span data-discovery-shown>{len(shown):,}</span> shown here. '
               f'{outside_count:,} other captures and {unclassified_count:,} not yet classified are in the '
               f'{raw_download} and its per-batch files.')
    prefix = '/zh' if zh else ''
    links = (f'<a href="{EXPORT_PATH}">{"发现队列 JSON" if zh else "Discovery queue JSON"}</a> · '
             f'<a href="{REVIEWS_PATH}">{"审核决定 JSON" if zh else "Review decisions JSON"}</a> · '
             f'<a href="{FEED_PATHS[language]}">{"Atom 订阅" if zh else "Atom feed"}</a> · '
             f'<a href="{escape(repository_url, quote=True)}/blob/main/{discoveries.DIRECTORY}/README.md">'
             f'{"入库规则（英文）↗" if zh else "Ingest rules ↗"}</a> · '
             f'<a href="{prefix}/browse/">{"仓库目录" if zh else "Repository directory"}</a>')
    parts = [f'<div class="browse-topline"><p>{status}</p></div>',
             f'<details class="browse-provenance" open><summary>{"关于这些发现" if zh else "About these discoveries"}</summary>'
             f'<p>{escape(NOTE[int(zh)])}</p>'
             f'<p>{("简介为上游原文；星标与最近推送时间为采集时快照。" if zh else "Descriptions are upstream text; stars and last-push months are capture-time snapshots.")}</p>'
             f'<p>{links}</p></details>']
    for name, labels, records, total in groups:
        parts.append(class_section(name, labels, records, total, language, use_pro, more=True))
    if not shown:
        parts.append(f'<p class="browse-empty">{"暂无数据点。" if zh else "No data points yet."}</p>')
    return '\n'.join(parts)


def class_page_content(queue: dict, name: str, labels: tuple[str, str], records: list[dict], language: str,
                       use_pro: bool) -> str:
    zh = language == 'zh'
    back = f'<a href="{PAGE_PATHS[language]}">{"全部类别的数据点" if zh else "Data points in every class"}</a>'
    status = (f'{labels[1]}类共 {len(records):,} 个数据点，按入库时间从新到旧排列。{back}' if zh
              else f'{len(records):,} {labels[0]} data points, newest first. {back}')
    return '\n'.join([f'<div class="browse-topline"><p>{status}</p></div>',
                      class_section(name, labels, records, len(records), language, use_pro, more=False)])


def feed_summary(record: dict, language: str) -> str:
    zh = language == 'zh'
    text = record['description_en'] or description_fallback(record, language)
    return text + (' — 自动 README 扫描，未审核。' if zh else ' — Automated README scan, unreviewed.')


def discovery_feed(queue: dict, language: str, site_url: str) -> str:
    zh = language == 'zh'
    feed_url, page_url = site_url + FEED_PATHS[language], site_url + PAGE_PATHS[language]
    records = [record for record in queue['listed'] if record.get('data_decision') == 'data'][:FEED_RECORDS]
    updated = timestamp(queue['latest']['ingested_at'])
    rows = []
    for record in records:
        title = ('未审核发现：' if zh else 'Unreviewed discovery: ') + record['full_name']
        rows.append(f'''  <entry>
    <id>tag:awesomerea.org,2026:discovery:{record['id']}</id>
    <title>{xml_escape(title)}</title>
    <link rel="alternate" type="text/html" href={quoteattr(record['url'])}/>
    <published>{record['ingested_at']}</published>
    <updated>{record['ingested_at']}</updated>
    <category term="{FEED_TERM}" label={quoteattr(FEED_LABELS[int(zh)])}/>
    <summary>{xml_escape(feed_summary(record, language))}</summary>
  </entry>''')
    return f'''<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="{'zh-CN' if zh else 'en'}">
  <id>{xml_escape(feed_url)}</id>
  <title>{xml_escape(FEED_TITLES[int(zh)])}</title>
  <subtitle>{xml_escape(NOTE[int(zh)])}</subtitle>
  <link rel="self" type="application/atom+xml" href={quoteattr(feed_url)}/>
  <link rel="alternate" type="text/html" href={quoteattr(page_url)}/>
  <updated>{updated}</updated>
  <author><name>Awesome REA automation</name><uri>https://github.com/{discoveries.REPOSITORY}</uri></author>
''' + '\n'.join(rows) + '\n</feed>\n'


def main_feed_batches(queue: dict | None) -> list[dict]:
    """The newest batches as summary entries for the main feeds, each labelled unreviewed."""
    if not queue:
        return []
    listed: dict[str, list[dict]] = {}
    for record in queue['listed']:
        if record.get('data_decision') != 'data':
            continue
        listed.setdefault(record['batch_id'], []).append(record)
    entries = []
    for batch in reversed(queue['batches']):
        records = listed.get(batch['batch_id'])
        if records:
            entries.append({'batch_id': batch['batch_id'], 'ingested_at': timestamp(batch['ingested_at']),
                            'run_id': batch['source']['run_id'], 'records': records})
        if len(entries) == MAIN_FEED_BATCHES:
            break
    return entries


def write_discoveries(site_dir: Path, catalog: dict, papers: list[dict], published_document: dict | None,
                      *, root: Path = discoveries.ROOT, lead_decided: list[dict] | None = None) -> tuple[list[str], dict | None]:
    """Write every discovery output; return the two page paths for the sitemap and the queue."""
    site_dir = Path(site_dir)
    queue = discovery_queue(root, published_document, papers, catalog['resources'])
    if not queue['batches']:
        return [], None
    metadata = catalog['meta']
    site_url, repository_url = metadata['site_url'].rstrip('/'), metadata['repository_url'].rstrip('/')
    assets = {key: _asset(site_dir, filename) for key, filename in (
        ('styles', 'styles.css'), ('browse', 'browse.css'), ('favicon', 'favicon.svg'), ('social', 'social-card.png'))}
    icons = _IconStylesheet()
    index = site_dir / 'index.html'
    if index.is_file():
        icons.feed(index.read_text(encoding='utf-8'))
    source_export = metadata.get('source_index', {}).get('full_export') or 'source-index.json'
    for language, path in PAGE_PATHS.items():
        zh = language == 'zh'
        title = TITLES[int(zh)]
        data_count = sum(record.get('data_decision') == 'data' for record in queue['listed'])
        description = (f'浏览自动扫描发现的 {data_count:,} 个数据点，按数据类别分组，查看各类别中按入库时间从新到旧排列的记录，'
                       '并通过项目链接、采集时的简介和来源信息了解每项发现，还可下载完整记录及各批次文件。' if zh
                       else f'Browse {data_count:,} data points from automated README scans, grouped by Data class '
                            'and ordered newest first within each group.')
        shown = [record for _, _, records, _ in page_groups(queue) for record in records]
        schema = collection_page_schema(site_url + path, title, description, 'zh-CN' if zh else 'en', [
            {'name': record['full_name'], 'url': record['url'],
             'description': record['description_en'] or description_fallback(record, language)} for record in shown], site_url)
        document = _document(site_url=site_url, repository_url=repository_url, path=path, language=language,
                             title=title, description=description,
                             content=page_content(queue, language, icons.href is not None, site_url, repository_url),
                             schema=schema, assets=assets, icon_stylesheet=icons.href, source_export=source_export)
        feed_link = (f'<link rel="alternate" type="application/atom+xml" title="{escape(FEED_TITLES[int(zh)], quote=True)}" '
                     f'href="{FEED_PATHS[language]}">')
        if document.count('</head>') != 1:
            raise ValueError('Discovery page needs exactly one document head')
        document = document.replace('</head>', '  ' + feed_link + '\n</head>')
        destination = site_dir / path.lstrip('/') / 'index.html'
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(document, encoding='utf-8')
        (site_dir / FEED_PATHS[language].lstrip('/')).write_text(discovery_feed(queue, language, site_url), encoding='utf-8')
    paths = list(PAGE_PATHS.values())
    for name, labels, records in class_pages(queue):
        for language in PAGE_PATHS:
            zh = language == 'zh'
            path = class_page_path(name, language)
            title = f'{TITLES[int(zh)]}{"：" if zh else ": "}{labels[int(zh)]}'
            description = (f'浏览自动扫描 README 发现的全部 {len(records):,} 个{labels[1]}类数据点，按入库时间从新到旧排列，'
                           '每项附仓库链接、固定版本的 README 链接、采集时的星标数和最近推送时间，可继续查看其他数据类别。' if zh
                           else f'All {len(records):,} {labels[0]} data points found by automated README scans, newest first, '
                                'each with its repository, pinned README and capture-time stars.')
            schema = collection_page_schema(site_url + path, title, description, 'zh-CN' if zh else 'en', [
                {'name': record['full_name'], 'url': record['url'],
                 'description': record['description_en'] or description_fallback(record, language)} for record in records], site_url)
            document = _document(site_url=site_url, repository_url=repository_url, path=path, language=language,
                                 title=title, description=description,
                                 content=class_page_content(queue, name, labels, records, language, icons.href is not None),
                                 schema=schema, assets=assets, icon_stylesheet=icons.href, source_export=source_export)
            destination = site_dir / path.lstrip('/') / 'index.html'
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(document, encoding='utf-8')
            paths.append(path)
    compact = {'ensure_ascii': False, 'separators': (',', ':')}
    (site_dir / EXPORT_PATH.lstrip('/')).write_text(
        json.dumps(export_document(queue, site_url, repository_url), **compact) + '\n', encoding='utf-8')
    exports = site_dir / BATCH_EXPORT_DIRECTORY.strip('/')
    exports.mkdir(parents=True, exist_ok=True)
    for batch in queue['batches']:
        (site_dir / batch_export_path(batch['batch_id']).lstrip('/')).write_text(
            json.dumps(batch_export(queue, batch), **compact) + '\n', encoding='utf-8')
    (site_dir / STATUS_PATH.lstrip('/')).write_text(json.dumps(status_document(queue, site_url), indent=2) + '\n', encoding='utf-8')
    (site_dir / BADGE_PATH.lstrip('/')).write_text(json.dumps(badge_document(queue)) + '\n', encoding='utf-8')
    generated_at = timestamp(queue['latest']['ingested_at']) if queue['latest'] else None
    (site_dir / REVIEWS_PATH.lstrip('/')).write_text(
        json.dumps(discovery_reviews.export_document(queue['decided'], generated_at, lead_decided), **compact) + '\n', encoding='utf-8')
    return paths, queue


def llms_section(queue: dict | None, site_url: str, limit: int = 10) -> str:
    """The llms.txt section for data points in the discovery queue, newest first."""
    if not queue or not queue['batches']:
        return ''
    latest = queue['latest']
    data_points = [record for record in queue['listed'] if record.get('data_decision') == 'data']
    lines = ['## Recently discovered data points', '',
             f'{len(data_points):,} data points from automated README scans; last ingest '
             f'{timestamp(latest["ingested_at"])} from scan run {latest["source"]["run_id"]}.', '',
             f'- [Recently discovered data points]({site_url}{PAGE_PATHS["en"]}): Grouped by Data class.',
             f'- [Discovery queue JSON]({site_url}{EXPORT_PATH}): The newest {EXPORT_RECORDS:,} records with review_status=unreviewed, batch provenance and capture hashes; batches[].records_url lists every record of each batch.',
             f'- [Discovery Atom feed]({site_url}{FEED_PATHS["en"]}): The newest {FEED_RECORDS} data points.',
             f'- [Ingest status JSON]({site_url}{STATUS_PATH}): last_successful_ingest_at and the scan run.']
    for record in data_points[:limit]:
        text = re.sub(r'\s+', ' ', record['description_en']).strip() or 'No upstream description.'
        lines.append(f'- [{record["full_name"]}]({record["url"]}): {text[:200]} (unreviewed automated discovery)')
    return '\n'.join(lines) + '\n'
