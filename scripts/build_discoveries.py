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
import discovery_reviews

PAGE_PATHS = {'en': '/discoveries/', 'zh': '/zh/discoveries/'}
FEED_PATHS = {'en': '/discoveries/feed.xml', 'zh': '/zh/discoveries/feed.xml'}
EXPORT_PATH = '/discoveries.json'
STATUS_PATH = '/discoveries/status.json'
BADGE_PATH = '/discoveries/badge.json'
REVIEWS_PATH = '/discoveries/reviews.json'
PAGE_RECORDS = 100
FEED_RECORDS = 100
# The index export lists the newest records; every listed record is also in its batch's own file.
EXPORT_RECORDS = 1_000
BATCH_EXPORT_DIRECTORY = '/discoveries/batches/'
MAIN_FEED_BATCHES = 10
STALE_AFTER_HOURS = 4
FEED_TERM = 'unreviewed-discovery'
FEED_LABELS = ('Unreviewed automated discovery', '未审核的自动发现')
TITLES = ('Recently discovered repositories (unreviewed)', '最新发现的仓库（未审核）')
FEED_TITLES = ('AwesomeREA.org: recently discovered repositories (unreviewed)', 'AwesomeREA.org：最新发现的仓库（未审核）')
EXPORT_FIELDS = ('id', 'full_name', 'url', 'topics', 'targets', 'category', 'stars', 'license', 'pushed_at',
                 'observed_at', 'readme_url', 'readme_sha256', 'readme_git_sha')
NOTE = ('Automated README scans, not reviewed: each record passed this collection’s capture checks and topic screen, '
        'but nobody has read its sources, translated it, run it or judged its quality. Curated entries are reviewed '
        'separately; promoting a discovery means writing a new source-reviewed record.',
        '这些是自动 README 扫描结果，尚未审核：每条记录都通过了本合集的采集校验和主题筛选，但还没有人阅读其来源、翻译、运行或评估质量。'
        '精选条目另行审核；收录某个发现需要另写一条经来源审核的记录。')


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
    listed, since_published = [], 0
    for record in pending:
        name = record['full_name'].casefold()
        if record['id'] in published_ids or published_names.get(name, record['id']) != record['id']:
            since_published += 1
        else:
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


def export_record(record: dict) -> dict:
    value = {key: record[key] for key in EXPORT_FIELDS if key in record}
    value['description'] = record['description_en']
    value['description_language'] = 'upstream-original'
    if record.get('description_omission'):
        value['description_omitted'] = True
    value.update(verification='automated-readme-scan', review_status=discoveries.REVIEW_STATUS,
                 batch_id=record['batch_id'], ingested_at=record['ingested_at'])
    if record.get('related_entries'):
        value['related_entries'] = [{key: entry[key] for key in ('kind', 'id', 'href_en', 'href_zh') if key in entry}
                                    for entry in record['related_entries']]
    return value


def status_document(queue: dict, site_url: str) -> dict:
    latest = queue['latest']
    return {
        'version': 1, 'kind': 'automated-discovery-status',
        'last_successful_ingest_at': timestamp(latest['ingested_at']) if latest else None,
        'last_batch_id': latest['batch_id'] if latest else None,
        'last_scan_run_id': latest['source']['run_id'] if latest else None,
        'last_scan_run_url': run_url(latest) if latest else None,
        'stale_after_hours': STALE_AFTER_HOURS,
        'records': queue['record_count'], 'listed': len(queue['listed']), 'batches': len(queue['batches']),
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
    """The repository directory's card, one heading level down inside its batch section."""
    html = repository_card(record, language, use_pro)
    html = html.replace('<div class="source-card-head"><h2>', '<div class="source-card-head"><h3>', 1)
    html = html.replace('</a></h2></div>', '</a></h3></div>', 1)
    if html.count('<h3>') != 1 or '<h2' in html:
        raise ValueError('Unexpected repository card heading')
    return html


def page_content(queue: dict, language: str, use_pro: bool, site_url: str, repository_url: str) -> str:
    zh = language == 'zh'
    latest = queue['latest']
    shown = queue['listed'][:PAGE_RECORDS]
    when = (discoveries.parse_time(latest['ingested_at']).strftime('%Y-%m-%d %H:%M UTC') if latest else '')
    status = ((f'最近一次成功入库：<time datetime="{timestamp(latest["ingested_at"])}">{when}</time>，'
               f'来自<a href="{escape(run_url(latest), quote=True)}" target="_blank" rel="noopener">扫描运行 {latest["source"]["run_id"]}</a>。'
               f'共 {queue["record_count"]:,} 条自动发现，分 {len(queue["batches"])} 批入库；本页显示最新的 {len(shown):,} 条。')
              if zh else
              (f'Last successful ingest: <time datetime="{timestamp(latest["ingested_at"])}">{when}</time>, from '
               f'<a href="{escape(run_url(latest), quote=True)}" target="_blank" rel="noopener">scan run {latest["source"]["run_id"]}</a>. '
               f'{queue["record_count"]:,} automated discoveries in {len(queue["batches"])} batch{"" if len(queue["batches"]) == 1 else "es"}; this page shows the newest {len(shown):,}.')
              ) if latest else ('尚无自动发现。' if zh else 'No automated discoveries yet.')
    if queue['since_published']:
        status += (f' 另有 {queue["since_published"]:,} 条已进入仓库目录，不再在此列出。' if zh
                   else f' {queue["since_published"]:,} more have since entered the repository directory and are listed there instead.')
    if queue['decided']:
        reviewed = discovery_reviews.counts(queue['decided'])
        status += (f' 已审核 {len(queue["decided"]):,} 条，不再在此列出：收录 {reviewed["curated"]:,} 条，排除 {reviewed["exclude"]:,} 条，暂缓 {reviewed["hold"]:,} 条。' if zh
                   else f' {len(queue["decided"]):,} have been reviewed and left this list: {reviewed["curated"]:,} curated, {reviewed["exclude"]:,} excluded and {reviewed["hold"]:,} held.')
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
             f'<p>{("简介为上游原文，未翻译；星标与最近推送时间为采集时快照。" if zh else "Descriptions are upstream text, not translated; stars and last-push months are capture-time snapshots.")}</p>'
             f'<p>{links}</p></details>']
    groups: dict[str, list[dict]] = {}
    for record in shown:
        groups.setdefault(record['batch_id'], []).append(record)
    batches = {batch['batch_id']: batch for batch in queue['batches']}
    for batch_id, records in groups.items():
        batch = batches[batch_id]
        moment = discoveries.parse_time(batch['ingested_at']).strftime('%Y-%m-%d %H:%M UTC')
        heading = (f'{moment} 入库 · 扫描运行 {batch["source"]["run_id"]}' if zh
                   else f'Ingested {moment} · scan run {batch["source"]["run_id"]}')
        count = (f'本批 {len(batch["resources"]):,} 条，此处显示 {len(records):,} 条' if zh
                 else f'{len(records):,} of {len(batch["resources"]):,} in this batch')
        parts.append(f'<section class="discovery-batch" id="batch-{batch_id}" aria-labelledby="batch-{batch_id}-title">'
                     f'<h2 id="batch-{batch_id}-title">{escape(heading)}</h2><p>{escape(count)}</p>'
                     '<div class="source-results browse-results">\n'
                     + '\n'.join(card(record, language, use_pro) for record in records)
                     + '\n</div></section>')
    if not shown:
        parts.append(f'<p class="browse-empty">{"暂无待审核的发现。" if zh else "No unreviewed discoveries to list."}</p>')
    return '\n'.join(parts)


def feed_summary(record: dict, language: str) -> str:
    zh = language == 'zh'
    text = record['description_en'] or description_fallback(record, language)
    return text + (' — 自动 README 扫描，未审核。' if zh else ' — Automated README scan, not reviewed.')


def discovery_feed(queue: dict, language: str, site_url: str) -> str:
    zh = language == 'zh'
    feed_url, page_url = site_url + FEED_PATHS[language], site_url + PAGE_PATHS[language]
    records = queue['listed'][:FEED_RECORDS]
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
        description = (f'{len(queue["listed"]):,} 个通过采集校验与主题筛选、但尚未审核的逆向工程仓库，按入库时间从新到旧排列。这些记录只是待审线索，不代表已收录或已验证，可通过订阅源跟踪更新。' if zh
                       else f'{len(queue["listed"]):,} reverse-engineering repositories that passed the capture checks and topic screen but are not reviewed yet, newest first.')
        shown = queue['listed'][:PAGE_RECORDS]
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
    return list(PAGE_PATHS.values()), queue


def llms_section(queue: dict | None, site_url: str, limit: int = 10) -> str:
    """The llms.txt section for the discovery queue, newest records first."""
    if not queue or not queue['batches']:
        return ''
    latest = queue['latest']
    lines = ['## Recently discovered repositories (unreviewed)', '',
             f'Automated README scans that passed capture checks and a reverse-engineering topic screen; not reviewed, '
             f'curated, translated or run. {len(queue["listed"]):,} are listed; last ingest '
             f'{timestamp(latest["ingested_at"])} from scan run {latest["source"]["run_id"]}.', '',
             f'- [Recently discovered (unreviewed)]({site_url}{PAGE_PATHS["en"]}): The newest {PAGE_RECORDS} discoveries with upstream links.',
             f'- [Discovery queue JSON]({site_url}{EXPORT_PATH}): The newest {EXPORT_RECORDS:,} records with review_status=unreviewed, batch provenance and capture hashes; batches[].records_url lists every record of each batch.',
             f'- [Discovery Atom feed]({site_url}{FEED_PATHS["en"]}): The newest {FEED_RECORDS} discoveries.',
             f'- [Ingest status JSON]({site_url}{STATUS_PATH}): last_successful_ingest_at and the scan run.']
    for record in queue['listed'][:limit]:
        text = re.sub(r'\s+', ' ', record['description_en']).strip() or 'No upstream description.'
        lines.append(f'- [{record["full_name"]}]({record["url"]}): {text[:200]} (unreviewed automated discovery)')
    return '\n'.join(lines) + '\n'
