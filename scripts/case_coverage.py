"""Validate case-inventory coverage separately from repository scans and project counts."""
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
STATES = {'already-curated', 'pending', 'insufficient-evidence'}
LEVELS = {'inventory-only', 'catalog-mapped', 'primary-source-reviewed'}
TOP_FIELDS = {'schema_version', 'reviewed_at', 'catalog_revision', 'runtime_reproduced',
              'project_identity_resolution', 'collections', 'aliases', 'entries', 'counts'}
ENTRY_FIELDS = {'id', 'unit_id', 'collection_id', 'title', 'collection_urls', 'reported_source_urls',
                'state', 'review_level', 'reviewed_at', 'reason_en', 'reason_zh',
                'primary_evidence_urls', 'catalog_matches'}
MATCH_FIELDS = {'catalog', 'id', 'kind', 'scope'}
SCOPES = {'full', 'partial', 'related'}
PRIVATE = re.compile(r'/(?:Users|home)/[^/\s]+/|\.cache/|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')


def read_case_coverage(root=ROOT):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError('Duplicate coverage JSON key')
            value[key] = item
        return value

    def invalid(_):
        raise ValueError('Non-JSON coverage number')

    return json.loads((Path(root) / 'data/case-coverage.json').read_text(encoding='utf-8'),
                      object_pairs_hook=unique, parse_constant=invalid)


def coverage_counts(entries):
    """Count occurrences and report units; project identity is deliberately unresolved."""
    units = {entry['unit_id']: entry['state'] for entry in entries}
    matches = [match for entry in entries for match in entry['catalog_matches']]
    return {
        'occurrences': len(entries), 'inventory_units': len(units),
        'alias_merges': len(entries) - len(units),
        'occurrences_by_state': dict(sorted(Counter(entry['state'] for entry in entries).items())),
        'units_by_state': dict(sorted(Counter(units.values()).items())),
        'primary_reviewed_units': len({entry['unit_id'] for entry in entries
                                       if entry['review_level'] == 'primary-source-reviewed'}),
        'catalog_linked_occurrences': sum(bool(entry['catalog_matches']) for entry in entries),
        'distinct_resource_ids': len({match['id'] for match in matches if match['catalog'] == 'resource'}),
        'distinct_paper_ids': len({match['id'] for match in matches if match['catalog'] == 'paper'}),
        'unique_projects': None,
    }


def catalog_revision_warning(document, root=ROOT):
    """Advisory: name a catalog_revision that is not on the checked-out history, or None.

    Squash merges discard branch commits, so the revision must be a commit already on main. The check
    needs full Git history; it is skipped without Git, outside a work tree and in shallow clones.
    """
    revision = document.get('catalog_revision') if isinstance(document, dict) else None
    if not isinstance(revision, str) or not re.fullmatch(r'[a-f0-9]{40}', revision):
        return None  # validate_case_coverage reports the format.

    def git(*arguments):
        return subprocess.run(['git', '-C', str(root), *arguments], capture_output=True, encoding='utf-8', check=False)

    try:
        shallow = git('rev-parse', '--is-shallow-repository')
        if shallow.returncode or shallow.stdout.strip() != 'false':
            return None
        if git('cat-file', '-e', revision + '^{commit}').returncode:
            return f'catalog_revision {revision} is not a commit in this clone; use a commit on main'
        if git('merge-base', '--is-ancestor', revision, 'HEAD').returncode:
            return f'catalog_revision {revision} is not an ancestor of HEAD; use a commit on main'
    except OSError:
        return None
    return None


def validate_case_coverage(document, resources, papers, errors, *, url_check):
    start = len(errors)
    def fail(message):
        errors.append('Case coverage: ' + message)

    def fields(value, expected, where):
        if not isinstance(value, dict) or set(value) != expected:
            fail(where + ' has missing or unknown fields')
            return False
        return True

    def text(value, where, chinese=False):
        if (not isinstance(value, str) or not value.strip() or len(value) > 800
                or (chinese and not re.search(r'[\u3400-\u9fff]', value))
                or (not chinese and not re.search(r'[A-Za-z]', value))):
            fail(where + ' needs bounded ' + ('Chinese ' if chinese else '') + 'text')

    def day(value, where):
        try:
            if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value) or date.fromisoformat(value) > datetime.now(timezone.utc).date():
                raise ValueError
        except ValueError:
            fail(where + ' needs a non-future ISO date')

    def urls(values, where, required=False):
        if (not isinstance(values, list) or (required and not values)
                or any(not isinstance(item, str) for item in values)):
            fail(where + ' needs a URL array')
            return False
        if len(values) != len(set(values)):
            fail(where + ' contains duplicate URLs')
        for value in values:
            if url_check(value):
                fail(where + ' contains an invalid public HTTPS URL')
        return True

    def pinned_locator(value, source):
        prefix = source['repository_url'] + '/blob/' + source['commit'] + '/'
        if not value.startswith(prefix):
            return False
        suffix = value[len(prefix):]
        return (not urlsplit(value).query and not urlsplit(value).fragment
                and bool(re.fullmatch(r'[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*', suffix))
                and all(part not in {'.', '..'} for part in suffix.split('/')))

    def string_values(value):
        return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []

    if not fields(document, TOP_FIELDS, 'document'):
        return
    if PRIVATE.search(json.dumps(document, ensure_ascii=False)):
        fail('contains a private path or credential-like value')
    if type(document['schema_version']) is not int or document['schema_version'] != 1:
        fail('unsupported schema version')
    if document['runtime_reproduced'] is not False or document['project_identity_resolution'] != 'incomplete':
        fail('inventory must not claim runtime reproduction or complete project identity resolution')
    if not isinstance(document['catalog_revision'], str) or not re.fullmatch(r'[a-f0-9]{40}', document['catalog_revision']):
        fail('catalog revision must be a full Git commit')
    day(document['reviewed_at'], 'reviewed_at')
    if any(not isinstance(document[key], list) for key in ('collections', 'aliases', 'entries')):
        fail('collections, aliases and entries must be arrays')
        return
    if not document['collections'] or not document['entries']:
        fail('inventory and collections must not be empty')
    catalogs = {'resource': {r['id']: r for r in resources if isinstance(r, dict) and isinstance(r.get('id'), str)},
                'paper': {r['id']: r for r in papers if isinstance(r, dict) and isinstance(r.get('id'), str)}}
    sources = {}
    for source in document['collections']:
        if not fields(source, {'id', 'repository_url', 'commit', 'entry_count', 'source_files', 'catalog_resource_id', 'locator_templates'}, 'collection'):
            continue
        identifier = source['id']
        if not isinstance(identifier, str) or not re.fullmatch(r'[a-z][a-z0-9-]*', identifier) or identifier in sources:
            fail('collection IDs must be unique slugs')
            continue
        repository = source['repository_url']
        if (not isinstance(repository, str) or not re.fullmatch(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository)
                or url_check(repository) or not isinstance(source['commit'], str) or not re.fullmatch(r'[a-f0-9]{40}', source['commit'])):
            fail(identifier + ' needs a public GitHub repository and pinned commit')
            continue
        sources[identifier] = source
        target = catalogs['resource'].get(source['catalog_resource_id']) if isinstance(source['catalog_resource_id'], str) else None
        if (not target or target.get('kind') != 'collection' or not isinstance(target.get('url'), str)
                or target['url'].casefold().rstrip('/') != repository.casefold()):
            fail(identifier + ' collection catalog mapping does not resolve')
        if type(source['entry_count']) is not int or source['entry_count'] <= 0 or not isinstance(source['source_files'], list) or not source['source_files']:
            fail(identifier + ' needs a positive count and source file receipts')
            continue
        paths = set()
        for receipt in source['source_files']:
            if not fields(receipt, {'path', 'url', 'git_blob_sha', 'sha256', 'bytes'}, 'source receipt'):
                continue
            path = receipt['path']
            if (not isinstance(path, str) or not re.fullmatch(r'[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*', path)
                    or any(part in {'.', '..'} for part in path.split('/')) or path in paths):
                fail(identifier + ' has an invalid or duplicate source path')
                continue
            paths.add(path)
            if receipt['url'] != repository + '/blob/' + source['commit'] + '/' + path or url_check(receipt['url']):
                fail(identifier + ' source receipt URL does not bind its path and commit')
            for field, size in (('git_blob_sha', 40), ('sha256', 64)):
                if not isinstance(receipt[field], str) or not re.fullmatch('[a-f0-9]{' + str(size) + '}', receipt[field]):
                    fail(identifier + ' has invalid source receipt hash')
            if type(receipt['bytes']) is not int or receipt['bytes'] <= 0:
                fail(identifier + ' has invalid source receipt byte count')
        templates = source['locator_templates']
        if not isinstance(templates, list) or not templates or len(templates) != len(set(string_values(templates))):
            fail(identifier + ' needs unique locator templates')
        else:
            for template in templates:
                if (not isinstance(template, str) or template.count('{entry}') > 1
                        or not pinned_locator(repository + '/blob/' + source['commit'] + '/' + template.replace('{entry}', 'example'), source)
                        or ('{entry}' not in template and template not in paths)):
                    fail(identifier + ' locator template must use one entry slug or a receipted source file')
    ids, groups, populations = set(), defaultdict(list), Counter()
    for entry in document['entries']:
        if not fields(entry, ENTRY_FIELDS, 'entry'):
            continue
        identifier = entry['id']
        if not isinstance(identifier, str) or not re.fullmatch(r'[a-z][a-z0-9-]*:[a-z0-9]+(?:-[a-z0-9]+)*', identifier) or identifier in ids:
            fail('entry IDs must be unique collection-prefixed slugs')
            continue
        ids.add(identifier)
        unit = entry['unit_id']
        if not isinstance(unit, str) or not re.fullmatch(r'[a-z][a-z0-9-]*:[a-z0-9]+(?:-[a-z0-9]+)*', unit):
            fail(identifier + ' has invalid inventory unit ID')
            continue
        groups[unit].append(entry)
        source = sources.get(entry['collection_id']) if isinstance(entry['collection_id'], str) else None
        if not source or not identifier.startswith(entry['collection_id'] + ':'):
            fail(identifier + ' collection does not resolve')
        else:
            populations[entry['collection_id']] += 1
            if urls(entry['collection_urls'], identifier + ' locators', required=True):
                if any(not pinned_locator(url, source) for url in entry['collection_urls']):
                    fail(identifier + ' locator is outside its pinned collection')
                expected = {source['repository_url'] + '/blob/' + source['commit'] + '/' + template.replace('{entry}', identifier.split(':', 1)[1])
                            for template in string_values(source['locator_templates'])}
                if not set(entry['collection_urls']).issubset(expected):
                    fail(identifier + ' locator does not match its entry or receipted category')
        text(entry['title'], identifier + ' title')
        text(entry['reason_en'], identifier + ' reason_en')
        text(entry['reason_zh'], identifier + ' reason_zh', chinese=True)
        day(entry['reviewed_at'], identifier + ' reviewed_at')
        if (not isinstance(entry['state'], str) or entry['state'] not in STATES
                or not isinstance(entry['review_level'], str) or entry['review_level'] not in LEVELS):
            fail(identifier + ' has unsupported state or review level')
        urls(entry['reported_source_urls'], identifier + ' reported links', required=True)
        urls(entry['primary_evidence_urls'], identifier + ' primary evidence', required=entry['review_level'] != 'inventory-only')
        if not isinstance(entry['catalog_matches'], list):
            fail(identifier + ' needs a catalog match array')
            continue
        matched, full = set(), False
        for match in entry['catalog_matches']:
            if not fields(match, MATCH_FIELDS, identifier + ' match'):
                continue
            catalog, key = match['catalog'], match['id']
            if not isinstance(catalog, str) or catalog not in catalogs or not isinstance(key, str):
                fail(identifier + ' has invalid catalog match identity')
                continue
            target = catalogs[catalog].get(key)
            if not target or target.get('kind') != match['kind'] or (catalog, key) in matched:
                fail(identifier + ' catalog match is missing, duplicated or has the wrong kind')
            elif isinstance(entry['primary_evidence_urls'], list):
                target_sources = ([target.get('url'), target.get('evidence_url'),
                                   *string_values(target.get('additional_evidence_urls', []))] if catalog == 'resource'
                                  else [target.get('url'), *string_values(target.get('evidence_urls', []))])
                if not any(url in entry['primary_evidence_urls'] for url in target_sources if isinstance(url, str)):
                    fail(identifier + ' catalog mapping is not bound to that record’s sources')
            matched.add((catalog, key))
            if not isinstance(match['scope'], str) or match['scope'] not in SCOPES:
                fail(identifier + ' has unsupported match scope')
            full |= match['scope'] == 'full'
        if entry['state'] == 'already-curated' and (not full or entry['review_level'] == 'inventory-only'):
            fail(identifier + ' already-curated requires reviewed full-scope catalog mapping')
        if entry['catalog_matches'] and entry['review_level'] == 'inventory-only':
            fail(identifier + ' catalog mapping requires a recorded mapping review')
    for identifier, source in sources.items():
        if populations[identifier] != source['entry_count']:
            fail(identifier + ' entry count does not match enumerated occurrences')
    duplicate_units = {key: sorted(row['id'] for row in rows) for key, rows in groups.items() if len(rows) > 1}
    alias_units = {}
    for alias in document['aliases']:
        if not fields(alias, {'unit_id', 'occurrence_ids', 'basis_en', 'basis_zh', 'evidence_urls'}, 'alias'):
            continue
        unit, members = alias['unit_id'], alias['occurrence_ids']
        if (not isinstance(unit, str) or unit in alias_units or not isinstance(members, list)
                or any(not isinstance(item, str) for item in members) or sorted(members) != duplicate_units.get(unit)):
            fail('alias must exactly explain one duplicated unit and its occurrence IDs')
            continue
        alias_units[unit] = members
        text(alias['basis_en'], 'alias basis_en'); text(alias['basis_zh'], 'alias basis_zh', chinese=True)
        if urls(alias['evidence_urls'], 'alias evidence', required=True):
            for row in groups[unit]:
                member_evidence = [value for key in ('collection_urls', 'reported_source_urls', 'primary_evidence_urls')
                                   if isinstance(row[key], list) for value in row[key] if isinstance(value, str)]
                if not set(alias['evidence_urls']).intersection(member_evidence):
                    fail('alias evidence must identify every merged occurrence')
    if set(alias_units) != set(duplicate_units):
        fail('every merged inventory unit requires one explicit alias decision')
    for unit, rows in groups.items():
        if unit not in {row['id'] for row in rows}:
            fail(unit + ' representative must belong to its own inventory unit')
        if any(row['state'] != rows[0]['state'] or row['review_level'] != rows[0]['review_level'] for row in rows):
            fail(unit + ' merged state/review levels must agree')
    if len(errors) == start:
        expected = coverage_counts(document['entries'])
        if document['counts'] != expected or type(document['counts']) is not dict:
            fail('derived counts differ; occurrences, report units and projects must remain distinct')
        elif any(type(document['counts'][key]) is not int for key in expected if key not in {'unique_projects', 'occurrences_by_state', 'units_by_state'}):
            fail('derived counts must be integers, not booleans')
        elif any(type(value) is not int for key in ('occurrences_by_state', 'units_by_state') for value in document['counts'][key].values()):
            fail('state counts must be integers, not booleans')
