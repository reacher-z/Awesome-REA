"""The static read-only API under /api/v1/ and its documentation page /api/.

Files: resources, papers, categories, candidates and changes, each as JSON and CSV, plus a JSON Schema
(schema.json) and an index of every file with its size and SHA-256. Every JSON file carries ``version`` (the
API's semantic version), ``generated_at`` and ``schema`` (its definition in schema.json); every CSV row
carries the same ``version`` and ``generated_at`` columns. Record IDs are the catalog's stable IDs.

``generated_at`` is the newest timestamp of the data in the snapshot (curated inclusion and review dates,
the repository selection, discovery and lead batches), not the build time, so rebuilding a commit
reproduces every file byte for byte and the IndexNow and build-manifest checks stay exact. ``changes.json``
lists the 30 days that end at that time.

Candidates are the unreviewed discovery and lead queues, labelled so, never curated records.
``_headers`` serves /api/ with ``Access-Control-Allow-Origin: *``; Cloudflare Pages adds the ETag.
"""
from __future__ import annotations

import csv
from datetime import datetime, timedelta, timezone
import hashlib
from html import escape
import io
import json
from pathlib import Path

from agent_formats import (MARKDOWN, RECORD_JSON, alternate_links, collection_markdown, json_text, paper_record,
                           resource_record)
from build_readme import CATEGORIES, KIND_LABELS, RELATIONSHIPS, TARGETS, collection_section
from data_downloads import CITATION_FIELDS
from data_classes import DATA_CLASSES
from requirement_facets import FACETS
from review_pr import private_json_locations
from sitemaps import instant, latest, normalized_date
from site_footer import HUGGING_FACE_URL
from structured_data import dataset_id, publisher_reference

API_VERSION = '1.0.0'
API_PATH = '/api/v1/'
DOCS_PATH = '/api/'
CHANGE_DAYS = 30
CANDIDATE_LIMIT = 1_000
ENDPOINTS = ('resources', 'papers', 'categories', 'candidates', 'changes')
TITLES = ('Static JSON and CSV API', '静态 JSON 与 CSV API')
REVIEW_NOTE = ('Curated resources and papers are source-reviewed: descriptions were checked against primary '
               'documentation.',
               '精选资源与论文均经来源复核：说明已依据一手文档核对。')
CANDIDATE_NOTE = ('Unreviewed candidates: automated README scans and links that followed public lists name. Promoting '
                  'one means writing a new source-reviewed record.',
                  '未审核的候选：自动 README 扫描结果，以及所关注的公开列表中列出的链接。收录某项需另写一条经来源审核的记录。')
CSV_COLUMNS = {
    'resources': ('id', 'name', 'name_zh', 'kind', 'category', 'relationship', 'targets', 'url', 'evidence_url',
                  'description_en', 'description_zh', 'requirements', 'requirements_zh', 'added_at', 'verified_at',
                  'verification', 'entry_url', 'entry_url_zh', 'json_url'),
    'papers': ('id', 'title', 'title_zh', 'authors', 'authors_omitted', 'year', 'publication_date', 'venue',
               'publication_status', 'doi', 'arxiv_id', 'url', 'pdf_url', 'code_url', 'project_url', 'targets',
               'description_en', 'description_zh', 'added_at', 'verified_at', 'verification', 'entry_url',
               'entry_url_zh', 'json_url', 'bibtex_url'),
    'categories': ('scope', 'id', 'label', 'label_zh', 'count', 'url', 'url_zh'),
    'candidates': ('candidate_type', 'id', 'name', 'url', 'description', 'category', 'targets', 'topics', 'stars',
                   'license', 'pushed_at', 'observed_at', 'batch_id', 'review_status', 'verification'),
    'changes': ('date', 'change', 'record_type', 'id', 'name', 'url', 'json_url'),
}


def utc_timestamp(value: str) -> str:
    """A recorded date or time as a UTC timestamp; a bare date is the start of its day."""
    return instant(value).strftime('%Y-%m-%dT%H:%M:%SZ')


def snapshot_time(resources, papers, repository_document=None, discovery_queue=None, lead_queue=None) -> str:
    """The newest recorded time in the data: the API's deterministic ``generated_at``."""
    meta = (repository_document or {}).get('meta', {})
    values = [*(record.get(key) for record in (*resources, *papers) for key in ('added_at', 'verified_at')),
              meta.get('published_at'), meta.get('completed_at'),
              *(batch.get('ingested_at') for batch in (discovery_queue or {}).get('batches', [])),
              *(batch.get('collected_at') for batch in (lead_queue or {}).get('batches', []))]
    newest = latest(values)
    if newest is None:
        raise ValueError('The API needs at least one dated record')
    return utc_timestamp(newest)


def envelope(kind: str, generated_at: str, site_url: str, definition: str, **content) -> dict:
    return {'version': API_VERSION, 'generated_at': generated_at, 'kind': kind,
            'schema': f'{site_url}{API_PATH}schema.json#/$defs/{definition}', 'docs': site_url + DOCS_PATH,
            'site_url': site_url + '/', 'license': 'Original collection text: MIT. Linked works retain their own licenses.',
            **content}


def paper_api_record(paper: dict, site_url: str) -> dict:
    value = paper_record(paper, site_url)
    if isinstance(value.get('citation'), dict):
        value['citation'] = {key: item for key, item in value['citation'].items() if key in CITATION_FIELDS}
    return value


def categories_document(resources, repository_records, site_url, generated_at, snapshot) -> dict:
    from build_discovery_pages import SECTIONS
    from build_repository_index import CATEGORIES as REPOSITORY_CATEGORIES
    count = lambda field, value: sum((value in record[field]) if isinstance(record[field], list) else record[field] == value
                                     for record in resources)
    labelled = lambda mapping, field, url=None: [
        {'id': key, 'label': labels[0], 'label_zh': labels[1], 'count': count(field, key),
         **(url(key) if url else {})} for key, labels in mapping.items()]
    sections = {key: sum(collection_section(record) == key for record in resources) for key in SECTIONS}
    curated = {
        'categories': [item for item in labelled(CATEGORIES, 'category') if item['count']],
        'sections': [{'id': key, 'label': labels[0], 'label_zh': labels[1], 'count': sections[key],
                      'url': f'{site_url}/resources/#heading-{key}', 'url_zh': f'{site_url}/zh/resources/#heading-{key}'}
                     for key, labels in SECTIONS.items() if sections[key]],
        'kinds': [item for item in labelled(KIND_LABELS, 'kind') if item['count']],
        'targets': labelled(TARGETS, 'targets'),
        'relationships': [item for item in labelled(RELATIONSHIPS, 'relationship') if item['count']],
    }
    repositories = [{'id': key, 'label': labels[0], 'label_zh': labels[1],
                     'count': sum(record.get('category') == key for record in repository_records),
                     'url': f'{site_url}/browse/{key}/', 'url_zh': f'{site_url}/zh/browse/{key}/',
                     'markdown_url': f'{site_url}/browse/{key}/{MARKDOWN}', 'json_url': f'{site_url}/browse/{key}/index.json'}
                    for key, labels in REPOSITORY_CATEGORIES.items()] if repository_records else []
    return envelope('awesome-rea-categories', generated_at, site_url, 'categoriesFile', curated=curated,
                    repositories={'verification': 'automated-readme-scan', 'snapshot': snapshot,
                                  'count': len(repository_records), 'categories': repositories})


def candidates_document(discovery_queue, lead_queue, site_url, generated_at) -> dict:
    from build_discoveries import export_record
    discoveries = [{'candidate_type': 'repository-discovery', **export_record(record)}
                   for record in (discovery_queue or {}).get('listed', [])[:CANDIDATE_LIMIT]]
    # Leads still awaiting review: data points and leads not yet classified, not other captures
    awaiting = [record for record in (lead_queue or {}).get('listed', []) if record.get('data_decision') != 'outside']
    leads = [{'candidate_type': 'followed-source-lead', **record} for record in awaiting[:CANDIDATE_LIMIT]]
    # Newest batch first across both queues; the sort is stable, so each queue keeps its own order within a batch.
    candidates = sorted(discoveries + leads, key=lambda row: instant(normalized_date(row.get('ingested_at') or row.get('collected_at'))),
                        reverse=True)
    return envelope(
        'awesome-rea-candidates', generated_at, site_url, 'candidatesFile', review_status='unreviewed',
        note=CANDIDATE_NOTE[0], note_zh=CANDIDATE_NOTE[1],
        counts={'repository_discoveries': len((discovery_queue or {}).get('listed', [])), 'followed_source_leads': len(awaiting),
                'exported_repository_discoveries': len(discoveries), 'exported_followed_source_leads': len(leads)},
        pagination=f'candidates lists at most the newest {CANDIDATE_LIMIT:,} of each type; the full queues are '
                   f'{site_url}/discoveries.json and {site_url}/discoveries/leads.json with their batch files.',
        candidates=candidates)


def changes_document(resources, papers, discovery_queue, lead_queue, site_url, generated_at) -> dict:
    """Inclusions, later source reviews and queue batches in the 30 days that end at ``generated_at``."""
    end = instant(generated_at)
    start = end - timedelta(days=CHANGE_DAYS)
    changes = []

    def add(date, change, record_type, identifier, name, url, json_url=None):
        date = normalized_date(date)
        if date and start <= instant(date) <= end:
            changes.append({'date': date, 'change': change, 'record_type': record_type, 'id': identifier,
                            'name': name, 'url': url, **({'json_url': json_url} if json_url else {})})
    for kind, records, title in (('resource', resources, 'name'), ('paper', papers, 'title')):
        for record in records:
            route = f"{site_url}/{kind}s/{record['id']}/"
            add(record.get('added_at'), 'added', kind, record['id'], record[title], route, route + RECORD_JSON)
            # A source review after inclusion is a separate, dated change to the entry.
            if record.get('added_at') and instant(normalized_date(record['verified_at'])) > instant(record['added_at']):
                add(record['verified_at'], 'reviewed', kind, record['id'], record[title], route, route + RECORD_JSON)
    for batch in (discovery_queue or {}).get('batches', []):
        add(batch['ingested_at'], 'discovered', 'discovery-batch', batch['batch_id'],
            f"{len(batch['resources']):,} unreviewed repository discoveries", f'{site_url}/discoveries/',
            f"{site_url}/discoveries/batches/{batch['batch_id']}.json")
    for batch in (lead_queue or {}).get('batches', []):
        add(batch['collected_at'], 'leads-collected', 'lead-batch', batch['batch_id'],
            f"{len(batch['leads']):,} unreviewed followed-source leads", f'{site_url}/discoveries/leads.json',
            f"{site_url}/discoveries/leads/{batch['batch_id']}.json")
    changes.sort(key=lambda row: (instant(row['date']), row['record_type'], row['id'], row['change']), reverse=True)
    return envelope('awesome-rea-changes', generated_at, site_url, 'changesFile', window_days=CHANGE_DAYS,
                    window_start=start.strftime('%Y-%m-%dT%H:%M:%SZ'), window_end=generated_at, count=len(changes),
                    changes=changes)


def _cell(value):
    if isinstance(value, list):
        return ' | '.join(str(item) for item in value)
    if value is None:
        return ''
    if isinstance(value, bool):
        return 'true' if value else 'false'
    return str(value)


def csv_bytes(columns, rows, generated_at) -> bytes:
    """RFC 4180 CSV in UTF-8; list values are joined with " | "; every row repeats version and generated_at."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator='\r\n')
    writer.writerow([*columns, 'version', 'generated_at'])
    for row in rows:
        writer.writerow([*(_cell(row.get(column)) for column in columns), API_VERSION, generated_at])
    return buffer.getvalue().encode('utf-8')


def csv_rows(name: str, document: dict) -> list[dict]:
    if name == 'resources':
        return document['resources']
    if name == 'papers':
        return [{**row, 'authors': '; '.join(row['authors'])} for row in document['papers']]
    if name == 'categories':
        rows = [{'scope': 'curated-category', **item} for item in document['curated']['categories']]
        rows += [{'scope': 'curated-section', **item} for item in document['curated']['sections']]
        for facet in ('kinds', 'targets', 'relationships'):
            rows += [{'scope': f'curated-{facet[:-1]}', **item} for item in document['curated'][facet]]
        rows += [{'scope': 'repository-category', **item} for item in document['repositories']['categories']]
        return rows
    if name == 'candidates':
        return [{**row, 'name': row.get('full_name') or row.get('name'),
                 'description': row.get('description') or (row.get('github') or {}).get('description'),
                 'stars': row.get('stars', (row.get('github') or {}).get('stars')),
                 'license': row.get('license', (row.get('github') or {}).get('license')),
                 'pushed_at': row.get('pushed_at', (row.get('github') or {}).get('pushed_at')),
                 'topics': row.get('topics', (row.get('github') or {}).get('topics'))}
                for row in document['candidates']]
    return document['changes']


def schema_document(site_url: str) -> dict:
    """JSON Schema (2020-12) for every API file, built from the catalog's own vocabularies."""
    from build_paper_pages import STATUS_LABELS
    from build_repository_index import CATEGORIES as REPOSITORY_CATEGORIES
    string = {'type': 'string', 'minLength': 1}
    url = {'type': 'string', 'format': 'uri', 'pattern': '^https://'}
    nullable = lambda value: {'anyOf': [value, {'type': 'null'}]}
    date = {'type': 'string', 'pattern': r'^\d{4}-\d{2}-\d{2}$'}
    date_time = {'type': 'string', 'format': 'date-time', 'pattern': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$'}
    day_or_time = {'anyOf': [date, date_time]}
    strings = {'type': 'array', 'items': string}
    identifier = {'type': 'string', 'pattern': '^[a-z0-9]+(?:-[a-z0-9]+)*$'}
    meta = {'version': {'type': 'string', 'pattern': r'^1\.\d+\.\d+$'}, 'generated_at': date_time, 'kind': string,
            'schema': url, 'docs': url, 'site_url': url, 'license': string}

    def file(kind, required, **properties):
        return {'type': 'object', 'required': ['version', 'generated_at', 'kind', 'schema', *required],
                'properties': {**meta, 'kind': {'const': kind}, **properties}, 'additionalProperties': False}
    entry_urls = {'entry_url': url, 'entry_url_zh': url, 'markdown_url': url, 'markdown_url_zh': url, 'json_url': url}
    resource = {
        'type': 'object', 'additionalProperties': False,
        'required': ['id', 'record_type', 'name', 'name_zh', 'url', 'kind', 'category', 'relationship', 'targets',
                     'description_en', 'description_zh', 'requirements', 'requirements_zh', 'evidence_url', 'added_at',
                     'verified_at', 'verification', *entry_urls],
        'properties': {
            'id': identifier, 'record_type': {'const': 'resource'}, 'name': string, 'name_zh': string, 'url': url,
            'kind': {'enum': list(KIND_LABELS)}, 'class': {'enum': list(DATA_CLASSES)},
            'category': {'enum': list(CATEGORIES)}, 'group': string,
            'relationship': {'enum': list(RELATIONSHIPS)},
            'targets': {'type': 'array', 'minItems': 1, 'items': {'enum': list(TARGETS)}},
            'description_en': string, 'description_zh': string, 'requirements': strings, 'requirements_zh': strings,
            'requirement_facets': {'type': 'array', 'items': {'enum': list(FACETS)}}, 'reconstruction_method': string,
            'evidence_url': url, 'additional_evidence_urls': {'type': 'array', 'items': url},
            'added_at': date, 'verified_at': day_or_time, 'verification': {'const': 'source-reviewed'},
            'source_unavailable': {'type': 'object', 'additionalProperties': False,
                                   'required': ['checked_at', 'outcome', 'http_status'],
                                   'properties': {'checked_at': string, 'outcome': {'enum': ['not-found', 'blocked']},
                                                  'http_status': {'enum': [404, 410, 451]}}},
            **entry_urls},
    }
    paper = {
        'type': 'object', 'additionalProperties': False,
        'required': ['id', 'record_type', 'title', 'title_zh', 'authors', 'year', 'venue', 'publication_status', 'url',
                     'pdf_url', 'targets', 'description_en', 'description_zh', 'scope_limitations_en',
                     'scope_limitations_zh', 'why_fits_en', 'why_fits_zh', 'evidence_urls', 'added_at', 'verified_at',
                     'verification', 'runtime_tested', 'bibtex_url', *entry_urls],
        'properties': {
            'id': {'type': 'string', 'pattern': '^paper-[a-z0-9]+(?:-[a-z0-9]+)*$'}, 'record_type': {'const': 'paper'},
            'title': string, 'title_zh': string,
            'authors': {'type': 'array', 'items': string, 'description': 'Empty when authors_omitted is true; the paper lists them.'},
            'authors_omitted': {'const': True}, 'year': {'type': 'integer', 'minimum': 1900},
            'publication_date': nullable({'type': 'string', 'pattern': r'^\d{4}(?:-\d{2}){0,2}$'}),
            'date_precision': {'enum': ['year', 'month', 'day']}, 'date_basis': string, 'date_basis_zh': string,
            'venue': string, 'publication_status': {'enum': list(STATUS_LABELS)}, 'arxiv_id': nullable(string),
            'arxiv_version_reviewed': nullable(string), 'first_arxiv_date': nullable(date), 'doi': nullable(string),
            'url': url, 'pdf_url': url, 'code_url': nullable(url), 'project_url': nullable(url),
            'targets': {'type': 'array', 'minItems': 1, 'items': {'enum': list(TARGETS)}}, 'kind': {'const': 'research'},
            'class': {'enum': list(DATA_CLASSES)},
            'description_en': string, 'description_zh': string, 'scope_limitations_en': string,
            'scope_limitations_zh': string, 'why_fits_en': string, 'why_fits_zh': string, 'metadata_notes': string,
            'metadata_notes_zh': string, 'citation': {'type': 'object', 'propertyNames': {'enum': sorted(CITATION_FIELDS)}},
            'evidence_urls': {'type': 'array', 'minItems': 1, 'items': url}, 'added_at': date, 'verified_at': day_or_time,
            'verification': {'const': 'source-reviewed'}, 'runtime_tested': {'const': False}, 'bibtex_url': url,
            **entry_urls},
    }
    labelled = {'type': 'object', 'required': ['id', 'label', 'label_zh', 'count'],
                'properties': {'id': identifier, 'label': string, 'label_zh': string, 'count': {'type': 'integer', 'minimum': 0},
                               'url': url, 'url_zh': url, 'markdown_url': url, 'json_url': url}, 'additionalProperties': False}
    candidate = {'type': 'object', 'required': ['candidate_type', 'id', 'url', 'review_status', 'verification', 'batch_id'],
                 'properties': {'candidate_type': {'enum': ['repository-discovery', 'followed-source-lead']},
                                # Leads keep the address their listing gives, which may be plain HTTP.
                                'id': string, 'url': {'type': 'string', 'pattern': '^https?://'}, 'review_status': {'const': 'unreviewed'},
                                'verification': {'enum': ['automated-readme-scan', 'automated-source-lead']},
                                'batch_id': string}}
    change = {'type': 'object', 'additionalProperties': False, 'required': ['date', 'change', 'record_type', 'id', 'name', 'url'],
              'properties': {'date': day_or_time, 'change': {'enum': ['added', 'reviewed', 'discovered', 'leads-collected']},
                             'record_type': {'enum': ['resource', 'paper', 'discovery-batch', 'lead-batch']},
                             'id': string, 'name': string, 'url': url, 'json_url': url}}
    index_file = {'type': 'object', 'required': ['path', 'url', 'media_type', 'bytes', 'sha256'],
                  'properties': {'path': string, 'url': url, 'media_type': string, 'bytes': {'type': 'integer', 'minimum': 1},
                                 'sha256': {'type': 'string', 'pattern': '^[0-9a-f]{64}$'}, 'records': {'type': 'integer', 'minimum': 0},
                                 'schema': url}, 'additionalProperties': False}
    return {
        '$schema': 'https://json-schema.org/draft/2020-12/schema', '$id': f'{site_url}{API_PATH}schema.json',
        'title': 'Awesome REA static API v1',
        'description': 'Schema of every JSON file under /api/v1/. Each file names its definition in its schema field.',
        '$defs': {
            'resource': resource, 'paper': paper, 'label': labelled, 'candidate': candidate, 'change': change,
            'resourcesFile': file('awesome-rea-resources', ['count', 'resources'], note=string, note_zh=string,
                                  count={'type': 'integer', 'minimum': 0}, resources={'type': 'array', 'items': {'$ref': '#/$defs/resource'}}),
            'papersFile': file('awesome-rea-papers', ['count', 'papers'], note=string, note_zh=string,
                               count={'type': 'integer', 'minimum': 0}, papers={'type': 'array', 'items': {'$ref': '#/$defs/paper'}}),
            'categoriesFile': file('awesome-rea-categories', ['curated', 'repositories'],
                                   curated={'type': 'object', 'required': ['categories', 'sections', 'kinds', 'targets', 'relationships'],
                                            'additionalProperties': {'type': 'array', 'items': {'$ref': '#/$defs/label'}}},
                                   repositories={'type': 'object', 'required': ['verification', 'count', 'categories'],
                                                 'properties': {'verification': {'const': 'automated-readme-scan'}, 'snapshot': nullable(string),
                                                                'count': {'type': 'integer', 'minimum': 0},
                                                                'categories': {'type': 'array', 'items': {'$ref': '#/$defs/label'}}},
                                                 'additionalProperties': False}),
            'candidatesFile': file('awesome-rea-candidates', ['review_status', 'counts', 'candidates'],
                                   review_status={'const': 'unreviewed'}, note=string, note_zh=string,
                                   counts={'type': 'object', 'additionalProperties': {'type': 'integer', 'minimum': 0}},
                                   pagination=string, candidates={'type': 'array', 'items': {'$ref': '#/$defs/candidate'}}),
            'changesFile': file('awesome-rea-changes', ['window_days', 'window_start', 'window_end', 'count', 'changes'],
                                window_days={'const': CHANGE_DAYS}, window_start=date_time, window_end=date_time,
                                count={'type': 'integer', 'minimum': 0}, changes={'type': 'array', 'items': {'$ref': '#/$defs/change'}}),
            'indexFile': file('awesome-rea-api-index', ['files'], endpoints={'type': 'array', 'items': {'enum': list(ENDPOINTS)}},
                              files={'type': 'array', 'items': {'$ref': '#/$defs/indexFile_entry'}}),
            'indexFile_entry': index_file,
            'repositoryCategoryFile': {'type': 'object', 'required': ['kind', 'category', 'verification', 'repositories'],
                                       'properties': {'kind': {'const': 'repository-category'}, 'category': {'enum': list(REPOSITORY_CATEGORIES)},
                                                      'verification': {'const': 'automated-readme-scan'}}},
        },
    }


def build_api(output: Path, *, resources, papers, repository_document=None, discovery_queue=None, lead_queue=None,
              site_url='https://awesomerea.org') -> dict:
    """Write /api/v1/ and return its index document."""
    output, site_url = Path(output), site_url.rstrip('/')
    generated_at = snapshot_time(resources, papers, repository_document, discovery_queue, lead_queue)
    meta = (repository_document or {}).get('meta', {})
    snapshot = meta.get('published_at') or meta.get('completed_at')
    repository_records = [record for record in (repository_document or {}).get('resources', [])
                          if record.get('scan_status') == 'readme-scanned' and record.get('scope_status') != 'excluded']
    documents = {
        'resources': envelope('awesome-rea-resources', generated_at, site_url, 'resourcesFile', note=REVIEW_NOTE[0],
                              note_zh=REVIEW_NOTE[1], count=len(resources),
                              resources=[resource_record(record, site_url) for record in resources]),
        'papers': envelope('awesome-rea-papers', generated_at, site_url, 'papersFile', note=REVIEW_NOTE[0],
                           note_zh=REVIEW_NOTE[1], count=len(papers), papers=[paper_api_record(paper, site_url) for paper in papers]),
        'categories': categories_document(resources, repository_records, site_url, generated_at, snapshot),
        'candidates': candidates_document(discovery_queue, lead_queue, site_url, generated_at),
        'changes': changes_document(resources, papers, discovery_queue, lead_queue, site_url, generated_at),
    }
    if private_json_locations(documents):
        raise ValueError('API privacy check failed; values withheld')
    folder = output / API_PATH.strip('/')
    folder.mkdir(parents=True, exist_ok=True)
    files = {'schema.json': json_text(schema_document(site_url)).encode('utf-8')}
    counts = {}
    for name, document in documents.items():
        # Compact, key-sorted UTF-8 JSON; schema.json and index.json stay indented for reading.
        files[f'{name}.json'] = (json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode('utf-8')
        rows = csv_rows(name, document)
        counts[name] = len(rows)
        files[f'{name}.csv'] = csv_bytes(CSV_COLUMNS[name], rows, generated_at)
    media = {'.json': 'application/json', '.csv': 'text/csv; charset=utf-8'}
    entries = []
    for name, raw in files.items():
        stem, suffix = name.rsplit('.', 1)
        entries.append({'path': API_PATH + name, 'url': site_url + API_PATH + name, 'media_type': media['.' + suffix],
                        'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
                        **({'records': counts[stem]} if stem in counts else {}),
                        **({'schema': f'{site_url}{API_PATH}schema.json#/$defs/{stem}File'} if stem in documents and suffix == 'json' else {})})
        (folder / name).write_bytes(raw)
    index = envelope('awesome-rea-api-index', generated_at, site_url, 'indexFile', endpoints=list(ENDPOINTS), files=entries)
    (folder / 'index.json').write_text(json_text(index), encoding='utf-8')
    return index


def api_page(language: str, index: dict, site_url: str) -> tuple[str, str, str, str]:
    """(title, description, HTML content, Markdown) of the /api/ documentation page in one language."""
    zh = language == 'zh'
    choose = lambda en, cn: cn if zh else en
    title = TITLES[zh]
    records = {entry['path'].rsplit('/', 1)[1].split('.')[0]: entry.get('records') for entry in index['files']}
    description = choose(
        f"Read the curated catalog as JSON or CSV: {records['resources']:,} resources, {records['papers']:,} papers, categories, unreviewed candidates and 30 days of changes.",
        f"以 JSON 或 CSV 读取精选目录：{records['resources']:,} 项资源、{records['papers']:,} 篇论文、分类、未审核候选与最近 30 天的变更。所有文件均为静态内容，可直接下载。")
    rows = [
        ('resources', choose('Curated resources: stable IDs, bilingual names and descriptions, requirements, evidence and review dates.', '精选资源：稳定 ID、中英文名称与说明、使用条件、证据与复核日期。')),
        ('papers', choose('The research bibliography: identifiers, dates and their basis, limits, sources and recorded authors.', '研究文献：标识、日期及其依据、研究边界、来源和已记录的作者。')),
        ('categories', choose('Curated categories, sections, kinds, targets and relationships with counts, plus the repository categories.', '精选分类、分区、类型、目标与关联及其数量，以及仓库分类。')),
        ('candidates', choose('Unreviewed automated discoveries and followed-source leads, newest first.', '未审核的自动发现与关注来源线索，按时间从新到旧。')),
        ('changes', choose('Additions, later source reviews and discovery batches in the 30 days before generated_at.', 'generated_at 之前 30 天内的新增、后续来源复核与发现批次。')),
    ]
    # A list, not a table: it wraps at every width with the shared page styles.
    endpoints = ''.join(
        f'<li><a href="{API_PATH}{name}.json">{name}.json</a> · <a href="{API_PATH}{name}.csv">{name}.csv</a> '
        f'({records[name]:,}): {escape(text)}</li>' for name, text in rows)
    notes = [
        choose(f'Every file carries version ({index["version"]}), generated_at and the schema definition it follows; CSV rows repeat version and generated_at. IDs are the catalog’s stable IDs.',
               f'每个文件都带有 version（{index["version"]}）、generated_at 以及所遵循的 schema 定义；CSV 每行重复 version 与 generated_at。ID 即目录的稳定 ID。'),
        choose(f'generated_at ({index["generated_at"]}) records the newest time in the data. Rebuilding the same commit produces identical files. The files update with merged pull requests and hourly discovery ingests that add records.',
               f'generated_at（{index["generated_at"]}）记录数据中的最新时间。同一提交可重建出相同的文件。合并的 PR 和每小时新增记录的自动发现入库会更新文件。'),
        choose('Responses allow any origin (CORS *) and carry an ETag. Cache responses and send If-None-Match.',
               '响应允许任意来源（CORS *）并带 ETag。请缓存响应并发送 If-None-Match。'),
        REVIEW_NOTE[zh],
    ]
    example = f'curl -s {site_url}{API_PATH}resources.json | jq \'.resources[] | select(.targets | index("protocol")) | {{id, name, entry_url}}\''
    content = (f'<div class="source-results"><section class="source-card browse-repository" aria-labelledby="api-endpoints"><h2 id="api-endpoints">{choose("Endpoints", "端点")}</h2>'
               f'<ul class="card-description">{endpoints}</ul>'
               f'<p class="card-description"><a href="{API_PATH}schema.json">schema.json</a> · <a href="{API_PATH}index.json">index.json</a> ({choose("sizes and SHA-256 of every file", "全部文件的大小与 SHA-256")})</p>'
               f'<p class="card-description"><a href="{HUGGING_FACE_URL}">{choose("Hugging Face dataset", "Hugging Face 数据集")}</a> · Parquet · JSONL</p></section>'
               f'<section class="source-card browse-repository" aria-labelledby="api-notes"><h2 id="api-notes">{choose("Versions, freshness and reuse", "版本、更新与复用")}</h2>'
               + ''.join(f'<p class="card-description">{escape(note)}</p>' for note in notes)
               + f'<p class="card-description"><code>{escape(example)}</code></p></section></div>')
    markdown = '\n'.join([
        f'# {title}', '', f'> {description}', '',
        f'- HTML: <{site_url}{"/zh" if zh else ""}{DOCS_PATH}>', f'- {choose("Index of files", "文件索引")}: <{site_url}{API_PATH}index.json>',
        f'- JSON Schema: <{site_url}{API_PATH}schema.json>',
        f'- {choose("Hugging Face dataset", "Hugging Face 数据集")}: <{HUGGING_FACE_URL}>', '', f'## {choose("Endpoints", "端点")}', '',
        *(f'- [{name}.json]({site_url}{API_PATH}{name}.json) ({records[name]:,}; CSV: {site_url}{API_PATH}{name}.csv): {text}' for name, text in rows),
        '', f'## {choose("Versions, freshness and reuse", "版本、更新与复用")}', '',
        *(line for note in notes for line in (note, '')), '```sh', example, '```', ''])
    return title, description, content, markdown


def write_api_pages(output: Path, index: dict, *, site_url, repository_url, source_export) -> list[str]:
    """Write /api/ and /zh/api/ with the shared page template of /about/; return their paths."""
    from build_discovery_pages import _IconStylesheet, _asset, _document
    from open_graph import website_reference
    output = Path(output)
    assets = {key: _asset(output, filename) for key, filename in (
        ('styles', 'styles.css'), ('browse', 'browse.css'), ('favicon', 'favicon.svg'), ('social', 'social-card.png'))}
    icons = _IconStylesheet()
    icons.feed((output / 'index.html').read_text(encoding='utf-8'))
    icon_stylesheet = icons.href
    paths = []
    for language in ('en', 'zh'):
        path = ('/zh' if language == 'zh' else '') + DOCS_PATH
        title, description, content, markdown = api_page(language, index, site_url)
        schema = {'@context': 'https://schema.org', '@type': 'WebPage', 'url': site_url + path, 'name': title,
                  'description': description, 'inLanguage': 'zh-CN' if language == 'zh' else 'en',
                  'isPartOf': website_reference(site_url), 'publisher': publisher_reference(site_url),
                  'about': {'@id': dataset_id(site_url, language)}}
        html = _document(site_url=site_url, repository_url=repository_url, path=path, language=language, title=title,
                         description=description, content=content, schema=schema, assets=assets,
                         icon_stylesheet=icon_stylesheet, source_export=source_export,
                         alternates=alternate_links(markdown=path + MARKDOWN, json_href=API_PATH + 'index.json'))
        destination = Path(output) / path.lstrip('/')
        destination.mkdir(parents=True, exist_ok=True)
        (destination / 'index.html').write_text(html, encoding='utf-8')
        (destination / MARKDOWN).write_text(markdown, encoding='utf-8')
        paths.append(path)
    return paths
