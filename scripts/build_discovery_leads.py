"""Publish the followed-source lead queue as JSON: /discoveries/leads.json plus one file per batch.

Records come from the validated batches in data/discoveries/leads/ (scripts/discovery_leads.py). They are
links that registered public sources list, kept unreviewed: every output says so, and no lead becomes a
page, a curated entry or a count of curated resources. A lead that the repository has since curated,
indexed, scanned or excluded is counted, not listed again.
"""
from __future__ import annotations

import json
from pathlib import Path

import discovery_leads as leads

EXPORT_PATH = '/discoveries/leads.json'
BATCH_EXPORT_DIRECTORY = '/discoveries/leads/'
EXPORT_RECORDS = 1_000
NOTE = ('Followed-source leads, not reviewed: links that the registered public lists, registries, topic searches, '
        'survey bibliographies, arXiv query and Hugging Face searches list inside their in-scope sections. Being listed '
        'by a secondary source is not evidence: nobody has read these resources, translated, run or judged them, and '
        'promoting one means writing a new source-reviewed record under the promotion worksheet.')


def lead_queue(root: Path) -> dict:
    """Validated lead batches as a queue: listed leads newest batch first, plus counts."""
    batches, problems = leads.load_batches(root)
    if problems:
        raise ValueError('Lead batches failed validation: ' + '; '.join(problems[:3]))
    registry, registry_problems = leads.load_registry(root)
    if registry_problems and batches:
        raise ValueError('The source registry failed validation: ' + '; '.join(registry_problems[:3]))
    # What the other layers hold now; earlier lead batches are not part of it.
    held = leads.existing_keys(root, [])['known'] if batches else {}
    listed, since_held = [], 0
    for batch in reversed(batches):
        for lead in batch['leads']:
            if leads.lead_keys(lead) & held.keys():
                since_held += 1
                continue
            listed.append({**lead, 'batch_id': batch['batch_id'], 'collected_at': batch['collected_at']})
    return {'batches': batches, 'listed': listed, 'since_held': since_held, 'registry': registry,
            'record_count': sum(len(batch['leads']) for batch in batches), 'latest': batches[-1] if batches else None}


def run_url(batch: dict) -> str:
    return f"https://github.com/{leads.REPOSITORY}/actions/runs/{batch['provenance']['run_id']}"


def batch_export_path(batch_id: str) -> str:
    return f'{BATCH_EXPORT_DIRECTORY}{batch_id}.json'


def export_document(queue: dict, site_url: str, repository_url: str) -> dict:
    latest = queue['latest']
    records = queue['listed'][:EXPORT_RECORDS]
    return {
        'version': 1, 'kind': 'followed-source-lead-queue',
        'generated_at': latest['collected_at'] if latest else None,
        'last_successful_collection_at': latest['collected_at'] if latest else None,
        'review_status': leads.REVIEW_STATUS, 'verification': leads.VERIFICATION, 'description': NOTE,
        'selection_policy': leads.POLICY,
        'counts': {'batches': len(queue['batches']), 'leads': queue['record_count'], 'listed': len(queue['listed']),
                   'exported': len(records), 'since_held_by_other_layers': queue['since_held']},
        'pagination': ('resources lists the newest listed leads; batches[].records_url lists every listed lead of '
                       'each batch, so together they cover the whole queue.'),
        'budget': {'leads_per_batch': leads.MAX_BATCH_RECORDS, 'leads': leads.MAX_TOTAL_RECORDS,
                   'bytes': leads.MAX_TOTAL_BYTES},
        'sources': [{'id': source['id'], 'type': source['type'], 'why': source['why'],
                     **({'repository': source['repository']} if 'repository' in source else {}),
                     **({'topic': source['topic']} if 'topic' in source else {})}
                    for source in (queue['registry'] or {}).get('sources', [])],
        'registry_url': f'{repository_url}/blob/main/{leads.REGISTRY}',
        'batches': [{'batch_id': batch['batch_id'], 'collected_at': batch['collected_at'],
                     'lead_count': len(batch['leads']),
                     'listed_count': sum(record['batch_id'] == batch['batch_id'] for record in queue['listed']),
                     'records_url': site_url + batch_export_path(batch['batch_id']), 'run_url': run_url(batch),
                     'source_file': f"{repository_url}/blob/main/{leads.DIRECTORY}/{batch['collected_at'][:7]}/{batch['batch_id']}.json"}
                    for batch in reversed(queue['batches'])],
        'resources': records,
    }


def batch_export(queue: dict, batch: dict) -> dict:
    return {'version': 1, 'kind': 'followed-source-lead-batch-export', 'batch_id': batch['batch_id'],
            'collected_at': batch['collected_at'], 'review_status': leads.REVIEW_STATUS,
            'verification': leads.VERIFICATION,
            'resources': [record for record in queue['listed'] if record['batch_id'] == batch['batch_id']]}


def write_lead_exports(site_dir: Path, catalog: dict, *, root: Path = leads.ROOT) -> dict | None:
    """Write the lead queue exports when lead batches exist; return the queue."""
    queue = lead_queue(root)
    if not queue['batches']:
        return None
    metadata = catalog['meta']
    site_url, repository_url = metadata['site_url'].rstrip('/'), metadata['repository_url'].rstrip('/')
    compact = {'ensure_ascii': False, 'separators': (',', ':')}
    site_dir = Path(site_dir)
    (site_dir / EXPORT_PATH.lstrip('/')).parent.mkdir(parents=True, exist_ok=True)
    (site_dir / EXPORT_PATH.lstrip('/')).write_text(
        json.dumps(export_document(queue, site_url, repository_url), **compact) + '\n', encoding='utf-8')
    exports = site_dir / BATCH_EXPORT_DIRECTORY.strip('/')
    exports.mkdir(parents=True, exist_ok=True)
    for batch in queue['batches']:
        (site_dir / batch_export_path(batch['batch_id']).lstrip('/')).write_text(
            json.dumps(batch_export(queue, batch), **compact) + '\n', encoding='utf-8')
    return queue


def llms_section(queue: dict | None, site_url: str) -> str:
    if not queue or not queue['batches']:
        return ''
    return '\n'.join([
        '## Followed-source leads (unreviewed)', '',
        f'Links that registered public reverse-engineering lists, registries, topic searches, survey bibliographies, an '
        f'arXiv query and Hugging Face searches list; not reviewed, curated, translated or run. {len(queue["listed"]):,} '
        f'are listed; last collection {queue["latest"]["collected_at"]}.', '',
        f'- [Lead queue JSON]({site_url}{EXPORT_PATH}): The newest {EXPORT_RECORDS:,} leads with review_status=unreviewed, '
        'pinned listing evidence and batch provenance; batches[].records_url lists every lead of each batch.',
    ]) + '\n'
