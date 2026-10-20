#!/usr/bin/env python3
"""Validate catalog data, benchmark snapshots, local Markdown links and generated READMEs."""
import datetime as dt
import html
import ipaddress
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
from urllib.parse import unquote, urlsplit

from build_readme import CATEGORIES, RELATIONSHIPS, TARGETS
from catalog import ROOT, RESOURCE_FILES
from localization import read_localizations, validate_localizations
from requirement_facets import facet_errors
from source_scope import read_scope, validate_scope
from validate_papers import validate_papers
from review_dates import review_date_is_future
from source_descriptions import validate_description_capture
from case_coverage import read_case_coverage, validate_case_coverage


RESOURCE_FIELDS = {
    'id', 'name', 'url', 'category', 'relationship', 'description_en',
    'description_zh', 'evidence_url', 'verified_at', 'verification', 'requirements', 'targets', 'kind',
}
BENCHMARK_FIELDS = {
    'id', 'full_name', 'url', 'category', 'stars', 'stars_display',
    'stars_precision', 'observed_at', 'description_zh', 'mechanisms',
    'evidence_urls', 'license', 'license_notes', 'created_at', 'pushed_at',
    'readme_blob_sha',
}
BENCHMARK_CATEGORIES = {
    'upstream_tool', 'distribution_reference', 'direct_catalog',
    'adjacent_catalog', 'official_skill_reference', 'workflow_product',
    'mature_re_tool', 'agent_re_tool',
}
IGNORED_DIRS = {'.git', 'node_modules', 'dist', 'output', '.cache', '.wrangler', '.venv', 'venv', '__pycache__'}


def nonempty_string(value):
    return isinstance(value, str) and bool(value.strip())


def string_list(value):
    return isinstance(value, list) and bool(value) and all(nonempty_string(item) for item in value)


def public_https_error(value):
    """Offline URL-shape check; public reachability is checked separately."""
    if not isinstance(value, str) or any(character.isspace() for character in value):
        return 'must be an HTTPS URL without whitespace'
    try:
        parsed = urlsplit(value)
        host = parsed.hostname
        parsed.port
    except ValueError:
        return 'has an invalid URL authority or port'
    if parsed.scheme != 'https' or not host or parsed.username or parsed.password:
        return 'must be a public HTTPS URL without embedded credentials'
    host = host.rstrip('.').lower()
    if host == 'localhost' or host.endswith(('.localhost', '.local', '.internal', '.invalid', '.test', '.example')):
        return 'must not name a local or reserved host'
    try:
        if not ipaddress.ip_address(host).is_global:
            return 'must not use a non-public IP address'
    except ValueError:
        # inet_aton recognizes legacy numeric IPv4 forms without resolving DNS.
        # Reject them even when global so consumers cannot reinterpret the host.
        try:
            socket.inet_aton(host)
        except OSError:
            pass  # An ordinary hostname, rather than a numeric IPv4 literal.
        except ValueError:
            return 'has an invalid hostname'
        else:
            return 'must use canonical dotted-decimal IPv4 notation'
        if '.' not in host:
            return 'must use a public hostname'
    return None


def parse_iso(value, require_time=False):
    if not isinstance(value, str):
        raise ValueError('expected an ISO date or timestamp')
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', value) and not require_time:
        return dt.datetime.combine(dt.date.fromisoformat(value), dt.time(), dt.timezone.utc)
    parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('timestamps must include a timezone')
    return parsed.astimezone(dt.timezone.utc)


def normalized_url(value):
    parsed = urlsplit(value)
    path = parsed.path.rstrip('/')
    if parsed.hostname and parsed.hostname.lower() == 'github.com':
        parts = path.split('/')
        parts[:3] = [part.lower() for part in parts[:3]]
        path = '/'.join(parts)
    return parsed.scheme.lower(), parsed.netloc.lower(), path, parsed.query, parsed.fragment


def evidence_pin_warnings(records):
    """Advisory only: evidence that cannot show the reviewed revision.

    A GitHub wiki page without its `/<revision>` suffix, or a bare repository root, always shows the
    current text. These are warnings rather than errors so records already in review keep passing.
    """
    warnings = []
    for record in records:
        if not isinstance(record, dict):
            continue
        where = f"resource {record.get('id')!r}"
        additional = record.get('additional_evidence_urls')
        links = [('evidence_url', record.get('evidence_url'))]
        links += [('additional_evidence_urls', url) for url in additional] if isinstance(additional, list) else []
        for field, url in links:
            if not isinstance(url, str):
                continue
            try:
                parsed = urlsplit(url)
                host = (parsed.hostname or '').lower()
            except ValueError:
                continue  # validate_resources reports malformed URLs.
            parts = [part for part in parsed.path.split('/') if part]
            if (host == 'github.com' and len(parts) >= 3 and parts[2] == 'wiki'
                    and not re.fullmatch(r'[0-9a-f]{40}', parts[-1])):
                warnings.append(f'{where}.{field}: GitHub wiki evidence should end in the reviewed page revision: {url}')
            elif ((host in {'github.com', 'codeberg.org'} and len(parts) == 2)
                  or (host == 'gitlab.com' and len(parts) >= 2 and '-' not in parts)):
                warnings.append(f'{where}.{field}: link the README or tree at the reviewed commit, not the repository root: {url}')
    return warnings


def validate_resources(records, errors, *, now=None):
    now = dt.datetime.now(dt.timezone.utc) if now is None else now.astimezone(dt.timezone.utc)
    ids, urls = set(), set()
    for index, record in enumerate(records):
        where = f'resource[{index}]'
        if not isinstance(record, dict):
            errors.append(f'{where}: must be an object')
            continue
        where = f"resource {record.get('id', index)!r}"
        missing = RESOURCE_FIELDS - record.keys()
        if missing:
            errors.append(f"{where}: missing fields {', '.join(sorted(missing))}")
            continue
        invalid_strings = False
        for field in RESOURCE_FIELDS - {'requirements', 'targets'}:
            if not nonempty_string(record[field]):
                errors.append(f'{where}.{field}: must be a nonempty string')
                invalid_strings = True
        if invalid_strings:
            continue
        if not string_list(record['targets']):
            errors.append(f'{where}.targets: use a nonempty list of target labels')
        elif len(set(record['targets'])) != len(record['targets']) or not set(record['targets']) <= set(TARGETS):
            errors.append(f'{where}.targets: use unique labels from ' + ', '.join(TARGETS))
        identifier = record['id']
        if not isinstance(identifier, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', identifier):
            errors.append(f'{where}.id: use a lowercase hyphenated slug')
        elif identifier in ids:
            errors.append(f'{where}: duplicate id')
        else:
            ids.add(identifier)
        for field in ('url', 'evidence_url'):
            problem = public_https_error(record[field])
            if problem:
                errors.append(f'{where}.{field}: {problem}')
        if 'additional_evidence_urls' in record:
            if not string_list(record['additional_evidence_urls']):
                errors.append(f'{where}.additional_evidence_urls: use a nonempty list of source URLs')
            else:
                for evidence in record['additional_evidence_urls']:
                    problem = public_https_error(evidence)
                    if problem:
                        errors.append(f'{where}.additional_evidence_urls: {problem}')
        if public_https_error(record['url']) is None:
            canonical = normalized_url(record['url'])
            if canonical in urls:
                errors.append(f'{where}: duplicate canonical URL')
            urls.add(canonical)
        if record['category'] not in CATEGORIES:
            errors.append(f"{where}: unknown category {record['category']!r}")
        if record['kind'] not in {'project', 'tool', 'integration', 'case-study', 'collection', 'documentation', 'learning-resource', 'research'}:
            errors.append(f"{where}: unknown resource kind {record['kind']!r}")
        if record['relationship'] not in RELATIONSHIPS:
            errors.append(f"{where}: unknown relationship {record['relationship']!r}")
        # CONTRIBUTING pairs independent reconstruction projects with their category; neither is inferred.
        if record['relationship'] == 'independent-reconstruction' and record['category'] != 'reconstruction-cases':
            errors.append(f"{where}: relationship 'independent-reconstruction' requires category 'reconstruction-cases'")
        elif record['category'] == 'reconstruction-cases' and record['relationship'] != 'independent-reconstruction':
            errors.append(f"{where}: category 'reconstruction-cases' requires relationship 'independent-reconstruction'")
        if record['verification'] != 'source-reviewed':
            errors.append(f'{where}.verification: use source-reviewed; runtime and reproduction results are out of scope (see CONTRIBUTING.md)')
        if not (nonempty_string(record['requirements']) or string_list(record['requirements'])):
            errors.append(f'{where}.requirements: use a nonempty string or list of nonempty strings')
        try:
            reviewed = parse_iso(record['verified_at'])
            future = (review_date_is_future(reviewed.date(), now)
                      if re.fullmatch(r'\d{4}-\d{2}-\d{2}', record['verified_at']) else
                      reviewed > now + dt.timedelta(days=1))
            if future:
                errors.append(f'{where}.verified_at: review date is in the future')
        except (ValueError, TypeError):
            errors.append(f'{where}.verified_at: invalid ISO date or timezone-aware timestamp')


def validate_benchmarks(records, errors):
    ids, names, urls = set(), set(), set()
    for index, record in enumerate(records):
        where = f'benchmark[{index}]'
        if not isinstance(record, dict):
            errors.append(f'{where}: must be an object')
            continue
        where = f"benchmark {record.get('full_name', index)!r}"
        missing = BENCHMARK_FIELDS - record.keys()
        if missing:
            errors.append(f"{where}: missing fields {', '.join(sorted(missing))}")
            continue
        identifier = record['id']
        if type(identifier) is not int or identifier <= 0:
            errors.append(f'{where}.id: must be a positive GitHub repository ID')
        elif identifier in ids:
            errors.append(f'{where}: duplicate repository ID')
        else:
            ids.add(identifier)
        name = record['full_name']
        if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', name):
            errors.append(f'{where}.full_name: expected owner/repository')
        elif name.casefold() in names:
            errors.append(f'{where}: duplicate repository name')
        else:
            names.add(name.casefold())
        for field in ('description_zh', 'stars_display', 'license_notes'):
            if not nonempty_string(record[field]):
                errors.append(f'{where}.{field}: must be a nonempty string')
        problem = public_https_error(record['url'])
        if problem:
            errors.append(f'{where}.url: {problem}')
        else:
            canonical = normalized_url(record['url'])
            if canonical in urls:
                errors.append(f'{where}: duplicate canonical URL')
            urls.add(canonical)
            if isinstance(name, str) and record['url'].rstrip('/').casefold() != f'https://github.com/{name}'.casefold():
                errors.append(f'{where}.url: does not match full_name')
        if not isinstance(record['category'], str) or record['category'] not in BENCHMARK_CATEGORIES:
            errors.append(f'{where}: unknown benchmark category')
        if type(record['stars']) is not int or record['stars'] < 0:
            errors.append(f'{where}.stars: must be a nonnegative integer')
        if not isinstance(record['stars_precision'], str) or record['stars_precision'] not in {'exact', 'rounded'}:
            errors.append(f'{where}.stars_precision: expected exact or rounded')
        elif record['stars_precision'] == 'exact' and isinstance(record['stars_display'], str):
            if record['stars_display'].replace(',', '').strip() != str(record['stars']):
                errors.append(f'{where}: exact stars and stars_display disagree')
        elif record['stars_precision'] == 'rounded' and isinstance(record['stars_display'], str):
            if not re.fullmatch(r'\d+(?:\.\d+)?[kKmM]?', record['stars_display'].strip()):
                errors.append(f'{where}: rounded display must be numeric with an optional k or m suffix')
        if not string_list(record['mechanisms']):
            errors.append(f'{where}.mechanisms: expected a nonempty list of strings')
        if not string_list(record['evidence_urls']):
            errors.append(f'{where}.evidence_urls: expected a nonempty list of HTTPS URLs')
        else:
            for url in record['evidence_urls']:
                problem = public_https_error(url)
                if problem:
                    errors.append(f'{where}.evidence_urls: {problem}: {url}')
        if record['license'] is not None and not nonempty_string(record['license']):
            errors.append(f'{where}.license: expected text or null for unknown')
        if not isinstance(record['readme_blob_sha'], str) or not re.fullmatch(r'[0-9a-f]{40}', record['readme_blob_sha']):
            errors.append(f'{where}.readme_blob_sha: expected a 40-character lowercase SHA')
        times = {}
        for field in ('observed_at', 'created_at', 'pushed_at'):
            try:
                times[field] = parse_iso(record[field], require_time=True)
            except (ValueError, TypeError):
                errors.append(f'{where}.{field}: invalid timezone-aware ISO timestamp')
        if len(times) == 3:
            if not times['created_at'] <= times['pushed_at'] <= times['observed_at']:
                errors.append(f'{where}: timestamps must satisfy created_at <= pushed_at <= observed_at')
            if times['observed_at'] > dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=1):
                errors.append(f'{where}.observed_at: snapshot is in the future')


def scan_run_entries(meta):
    """Known run containers only; no arbitrary nested metadata is trusted."""
    yield 'current_run', meta.get('current_run')
    histories = meta.get('resume_history', [])
    for index, history in enumerate(histories if isinstance(histories, list) else []):
        if isinstance(history, dict):
            yield f'resume_history[{index}].run', history.get('run')
    reconciliations = meta.get('checkpoint_reconciliations', [])
    for index, reconciliation in enumerate(reconciliations if isinstance(reconciliations, list) else []):
        if isinstance(reconciliation, dict):
            for key in ('canonical_current_run', 'checkpoint_current_run'):
                yield f'checkpoint_reconciliations[{index}].{key}', reconciliation.get(key)


def validate_scan_discovery(meta, records, errors, failures=()):
    """Check optional discovery evidence without inventing legacy observations."""
    def nonnegative_integer(value):
        return type(value) is int and value >= 0

    methods = {'github-search', 'curated-reference', 'paper-artifact-reference', 'retained-repository-id'}
    statuses = {'candidate', 'retained-attempt', 'name-collision', 'ineligible', 'failed', 'held', 'frontier-deferred'}
    ledger = meta.get('discovered_repository_ids', [])
    known = {value for value in ledger if isinstance(value, str)} if isinstance(ledger, list) else set()
    held_by_run = {}
    for location, run in scan_run_entries(meta):
        if not isinstance(run, dict) or 'held_repository_ids' not in run:
            continue
        held = run['held_repository_ids']
        if (not isinstance(held, list) or len(held) > 1000
                or any(not isinstance(value, str) or not re.fullmatch(r'scan-[1-9][0-9]*', value) for value in held)
                or len(set(held)) != len(held)
                or held != sorted(held, key=lambda value: int(value[5:]))):
            errors.append(f'Source index {location} held_repository_ids must be sorted unique canonical IDs.')
            continue
        if isinstance(run.get('run_id'), str):
            held_by_run[run['run_id']] = set(held)
        if location == 'current_run':
            for rows, field in ((records, 'retained_successful_readme_scans'), (failures, 'retained_failed_readme_scans')):
                retained = run.get(field)
                if type(retained) is int and retained >= 0 and any(row.get('id') in held for row in rows[retained:] if isinstance(row, dict)):
                    errors.append('Source index current_run held IDs must not become new README attempts.')
    seeds, resumed = {}, set()
    observed_queries = set()

    def identifier_list(values, pattern):
        return (isinstance(values, list) and bool(values)
                and all(isinstance(value, str) and re.fullmatch(pattern, value) for value in values)
                and len(set(values)) == len(values))

    def github_root(url):
        if public_https_error(url):
            return None
        parsed = urlsplit(url)
        parts = parsed.path.strip('/').split('/')
        if parsed.netloc != 'github.com' or len(parts) < 2:
            return None
        name = '/'.join(parts[:2]).removesuffix('.git').casefold()
        return name if re.fullmatch(r'[a-z0-9-]+/[a-z0-9_.-]+', name) else None

    def artifact_references(values, reference_ids, where, expected_root=None):
        artifacts, paper_ids = set(), set()
        if not isinstance(values, list) or not values:
            errors.append(f'{where}: expected nonempty paper artifact references')
            return artifacts
        for item in values:
            if (not isinstance(item, dict) or set(item) != {'paper_id', 'field', 'url'}
                    or not isinstance(item.get('paper_id'), str)
                    or not re.fullmatch(r'paper-[a-z0-9]+(?:-[a-z0-9]+)*', item['paper_id'])
                    or item.get('field') not in ('code_url', 'project_url')
                    or github_root(item.get('url')) is None):
                errors.append(f'{where}: invalid public GitHub paper artifact reference')
                continue
            key = (item['paper_id'], item['field'], item['url'])
            if key in artifacts:
                errors.append(f'{where}: duplicate paper artifact reference')
            artifacts.add(key)
            paper_ids.add(item['paper_id'])
            if expected_root is not None and github_root(item['url']) != expected_root:
                errors.append(f'{where}: paper artifact URL and seed repository disagree')
        if not identifier_list(reference_ids, r'paper-[a-z0-9]+(?:-[a-z0-9]+)*') or paper_ids != set(reference_ids):
            errors.append(f'{where}: paper reference IDs must match the artifact references')
        return artifacts

    for key in ('queries', 'seed_observations', 'resume_observations'):
        observations = meta.get(key, [])
        if not isinstance(observations, list):
            errors.append(f'Source index {key} must be an array.')
            continue
        for index, entry in enumerate(observations):
            where = f'source index {key}[{index}]'
            if not isinstance(entry, dict):
                errors.append(f'{where}: expected an object')
                continue
            if key == 'queries':
                for field in ('held_candidates_skipped', 'deferred_candidates_skipped'):
                    if field in entry and (not nonnegative_integer(entry[field])
                            or not nonnegative_integer(entry.get('returned')) or entry[field] > entry['returned']):
                        errors.append(f'{where}: invalid administrative/backoff skip count')
                if entry.get('status') == 'ok' and nonempty_string(entry.get('query')):
                    observed_queries.add(entry['query'])
                continue
            for field in ('observed_at', 'run_id'):
                try:
                    parse_iso(entry.get(field), require_time=True)
                except (ValueError, TypeError):
                    errors.append(f'{where}: invalid {field} timestamp')
            allowed = {'repository_id', 'observed_at', 'run_id', 'method', 'status', 'reason', 'http_status'}
            if key == 'seed_observations':
                allowed |= {'full_name', 'reference_ids', 'artifact_references'}
            if set(entry) - allowed:
                errors.append(f'{where}: unexpected metadata fields; preserve minimal discovery evidence')
            status = entry.get('status')
            if not isinstance(status, str) or status not in statuses:
                errors.append(f'{where}: invalid metadata lookup status')
                status = None
            identifier = entry.get('repository_id')
            needs_id = key == 'resume_observations' or status in {'candidate', 'retained-attempt', 'name-collision', 'held', 'frontier-deferred'}
            if needs_id or identifier is not None:
                if (not isinstance(identifier, str) or not re.fullmatch(r'scan-[0-9]+', identifier)
                        or identifier not in known):
                    errors.append(f'{where}: repository ID must be present in the discovery ledger')
            if status == 'held' and (not isinstance(entry.get('run_id'), str)
                                     or identifier not in held_by_run.get(entry['run_id'], set())):
                errors.append(f'{where}: held metadata outcome requires an explicit hold in that run')
            if key == 'resume_observations':
                if entry.get('method') != 'retained-repository-id' or status == 'retained-attempt':
                    errors.append(f'{where}: invalid retained repository lookup provenance')
                if status == 'candidate' and isinstance(identifier, str):
                    resumed.add(identifier)
            else:
                name = entry.get('full_name')
                if not isinstance(name, str) or not re.fullmatch(r'[a-z0-9-]+/[a-z0-9_.-]+', name):
                    errors.append(f'{where}: expected a lowercase GitHub seed repository name')
                method = entry.get('method')
                if method not in ('curated-repository-reference', 'paper-artifact-reference'):
                    errors.append(f'{where}: invalid seed discovery method')
                references = entry.get('reference_ids')
                if not identifier_list(references, r'[a-z0-9]+(?:-[a-z0-9]+)*'):
                    errors.append(f'{where}: expected unique reference IDs')
                artifacts = set()
                if method == 'paper-artifact-reference':
                    artifacts = artifact_references(entry.get('artifact_references'), references, where,
                                                    name if isinstance(name, str) else None)
                elif 'artifact_references' in entry:
                    errors.append(f'{where}: curated seeds cannot claim paper artifacts')
                if status in {'failed', 'ineligible'} and identifier is not None:
                    errors.append(f'{where}: unsuccessful seed lookups must not expose repository metadata')
                if status == 'candidate' and isinstance(identifier, str):
                    evidence = seeds.setdefault(identifier, {'curated': set(), 'papers': set()})
                    if method == 'curated-repository-reference' and isinstance(references, list):
                        evidence['curated'].update(value for value in references if isinstance(value, str))
                    elif method == 'paper-artifact-reference':
                        evidence['papers'].update(artifacts)
            if status == 'failed' and not nonempty_string(entry.get('reason')):
                errors.append(f'{where}: failed lookup must retain its reason')
            if status == 'ineligible':
                reason = entry.get('reason')
                legacy_curated = key == 'seed_observations' and entry.get('method') == 'curated-repository-reference'
                if not (reason is None and legacy_curated) and (not isinstance(reason, str)
                        or reason not in {'private', 'public-status-unconfirmed', 'fork', 'archived', 'eligibility-unconfirmed'}):
                    errors.append(f'{where}: ineligible lookup needs an eligibility outcome code')
            if 'reason' in entry and (status not in {'failed', 'ineligible'}
                    or not isinstance(entry['reason'], str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', entry['reason'])):
                errors.append(f'{where}: reason must be a metadata outcome code')
            if 'http_status' in entry and (status != 'failed' or entry['http_status'] is not None
                    and (type(entry['http_status']) is not int or not 100 <= entry['http_status'] <= 599)):
                errors.append(f'{where}: invalid HTTP outcome status')

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            continue
        where = f'source index record {index}'
        discovery = record.get('discovery_methods')
        provenance_fields = {'seed_reference_ids', 'seed_paper_ids', 'seed_paper_references'}
        if discovery is None and not provenance_fields.intersection(record):
            continue  # Early snapshots predate per-record discovery provenance.
        if not identifier_list(discovery, r'[a-z]+(?:-[a-z]+)*') or not set(discovery) <= methods:
            errors.append(f'{where}: invalid discovery methods')
            continue
        identifier = record.get('id')
        evidence = seeds.get(identifier, {}) if isinstance(identifier, str) else {}
        if 'github-search' in discovery:
            queries = record.get('matched_queries')
            if not string_list(queries) or any(query not in observed_queries for query in queries):
                errors.append(f'{where}: search discovery needs actually observed matched queries')
        elif record.get('matched_queries') != []:
            errors.append(f'{where}: matched queries require search discovery')
        if 'retained-repository-id' in discovery and (not isinstance(identifier, str) or identifier not in resumed):
            errors.append(f'{where}: retained discovery needs a candidate metadata observation')
        if 'curated-reference' in discovery:
            references = record.get('seed_reference_ids')
            if (not identifier_list(references, r'[a-z0-9]+(?:-[a-z0-9]+)*')
                    or not set(references) <= evidence.get('curated', set())):
                errors.append(f'{where}: curated discovery needs matching seed observations')
        elif 'seed_reference_ids' in record:
            errors.append(f'{where}: curated reference IDs require curated discovery')
        if 'paper-artifact-reference' in discovery:
            artifacts = artifact_references(record.get('seed_paper_references'), record.get('seed_paper_ids'), where)
            if not artifacts or not artifacts <= evidence.get('papers', set()):
                errors.append(f'{where}: paper discovery needs matching seed observations')
        elif {'seed_paper_ids', 'seed_paper_references'}.intersection(record):
            errors.append(f'{where}: paper references require paper discovery')


def validate_source_index(document, errors, *, allow_incomplete=False):
    if not isinstance(document, dict) or not isinstance(document.get('meta'), dict) or not isinstance(document.get('resources'), list):
        errors.append('Source index must contain meta and resources.')
        return 0
    meta, records = document['meta'], document['resources']
    if meta.get('status') != 'complete' and not (allow_incomplete and meta.get('status') == 'in-progress'):
        errors.append('Source index is an incomplete checkpoint; finish the scan before publication.')
    if meta.get('successful_readme_scans') != len(records) or len(records) <= 1500:
        errors.append('Source index must retain more than 1,500 successful scans and matching counts.')
    failures = document.get('failures', [])
    if not isinstance(failures, list):
        errors.append('Source index failures must be an array.')
        failures = []
    if meta.get('failed') != len(failures):
        errors.append('Source index failure count does not match the recorded failures.')
    if meta.get('attempted_readme_scans') != len(records) + len(failures):
        errors.append('Source index attempted count must equal successful plus failed scans.')
    ids, urls, names = set(), set(), set()
    for index, record in enumerate(records):
        where = f'source index record {index}'
        if not isinstance(record, dict):
            errors.append(f'{where}: expected an object')
            continue
        for field, seen in [('id', ids), ('url', urls), ('full_name', names)]:
            value = record.get(field)
            if not nonempty_string(value) or value.casefold() in seen:
                errors.append(f'{where}: missing or duplicate {field}')
            else:
                seen.add(value.casefold())
        if record.get('scan_status') != 'readme-scanned' or record.get('verification') != 'automated-readme-scan':
            errors.append(f'{where}: preserve automated scan labels')
        validate_description_capture(record, errors, where)
        for field in ('url', 'readme_url'):
            if public_https_error(record.get(field)):
                errors.append(f'{where}: invalid public {field}')
        if not isinstance(record.get('full_name'), str) or not re.fullmatch(r'[A-Za-z0-9-]+/[A-Za-z0-9_.-]+', record['full_name']):
            errors.append(f'{where}: invalid GitHub repository name')
        if record.get('url') != 'https://github.com/' + str(record.get('full_name', '')):
            errors.append(f'{where}: repository URL and full_name disagree')
        if 'readme_api_url' in record:
            api_url = record['readme_api_url']
            if public_https_error(api_url):
                errors.append(f'{where}: invalid public readme_api_url')
            else:
                parsed = urlsplit(api_url)
                if (parsed.netloc != 'api.github.com'
                        or parsed.path != '/repos/' + str(record.get('full_name', '')) + '/readme'):
                    errors.append(f'{where}: README API URL must match the public GitHub repository')
        graphql_fields = {'readme_transport', 'readme_graphql_endpoint', 'readme_commit_sha'}
        if 'readme_blob_api_url' in record:
            expected = ('https://api.github.com/repos/' + str(record.get('full_name', ''))
                        + '/git/blobs/' + str(record.get('readme_git_sha', '')))
            if (record['readme_blob_api_url'] != expected or 'readme_api_url' not in record
                    or graphql_fields.intersection(record)
                    or record.get('readme_git_sha_matches_content') is not True):
                errors.append(f'{where}: REST blob recovery must identify the verified immutable GitHub blob and README lookup')
        if graphql_fields.intersection(record):
            commit = record.get('readme_commit_sha')
            path = record.get('readme_path')
            if (not graphql_fields.issubset(record) or record.get('readme_transport') != 'github-graphql-blob'
                    or record.get('readme_graphql_endpoint') != 'https://api.github.com/graphql'
                    or not isinstance(commit, str) or not re.fullmatch(r'[0-9a-f]{40}', commit)
                    or not isinstance(path, str) or not path or path.startswith('/')
                    or any(part in ('', '.', '..') for part in path.split('/'))
                    or 'readme_api_url' in record or record.get('readme_git_sha_matches_content') is not True
                    or not isinstance(record.get('readme_url'), str) or not isinstance(record.get('url'), str)
                    or unquote(record.get('readme_url', '')) != record['url'] + '/blob/' + str(commit) + '/' + str(path)):
                errors.append(f'{where}: GraphQL README evidence needs a verified blob and immutable commit URL')
        if (record.get('private', False) is not False or record.get('visibility', 'public') != 'public'
                or record.get('archived', False) is not False or record.get('fork', False) is not False):
            errors.append(f'{where}: repository metadata must describe a public, non-fork, non-archived repository')
        if not re.fullmatch(r'[0-9a-f]{64}', str(record.get('readme_sha256', ''))):
            errors.append(f'{where}: missing README SHA-256')
        if 'readme_content_git_sha' in record or 'readme_git_sha_matches_content' in record:
            content_sha = record.get('readme_content_git_sha')
            if (not isinstance(content_sha, str) or not re.fullmatch(r'[0-9a-f]{40}', content_sha)
                    or type(record.get('readme_git_sha_matches_content')) is not bool
                    or record['readme_git_sha_matches_content'] != (content_sha == record.get('readme_git_sha'))):
                errors.append(f'{where}: computed README Git hash and comparison flag disagree')
        if 'readme_integrity_review' in record:
            review = record['readme_integrity_review']
            expected = {'reviewed_at', 'method', 'advertised_blob_sha256', 'advertised_blob_bytes'}
            if (not isinstance(review, dict) or set(review) != expected
                    or review.get('method') != 'readme-json-and-raw-match-captured-sha256'
                    or record.get('readme_git_sha_matches_content') is not False
                    or not re.fullmatch(r'[0-9a-f]{64}', str(review.get('advertised_blob_sha256', '')))
                    or type(review.get('advertised_blob_bytes')) is not int or review['advertised_blob_bytes'] <= 0):
                errors.append(f'{where}: invalid README integrity review')
            else:
                try:
                    parse_iso(review['reviewed_at'], require_time=True)
                except (ValueError, TypeError):
                    errors.append(f'{where}: invalid README integrity-review timestamp')
        if type(record.get('readme_bytes')) is not int or record['readme_bytes'] <= 0:
            errors.append(f'{where}: missing positive README byte count')
        targets = record.get('targets')
        if not isinstance(targets, list) or any(target not in TARGETS for target in targets):
            errors.append(f'{where}: invalid automatic target labels')
        if type(record.get('stars')) is not int or record['stars'] < 0:
            errors.append(f'{where}: stars must be a nonnegative snapshot count')
        try:
            parse_iso(record.get('observed_at'), require_time=True)
        except (ValueError, TypeError):
            errors.append(f'{where}: invalid scan timestamp')

    failed_ids = set()
    for index, failure in enumerate(failures):
        if not isinstance(failure, dict) or not nonempty_string(failure.get('id')):
            errors.append(f'source index failure {index}: expected an object with a source ID')
            continue
        identifier = failure['id'].casefold()
        if identifier in failed_ids:
            errors.append(f'source index failure {index}: duplicate source ID')
        if identifier in ids:
            errors.append(f'source index failure {index}: source ID also has a successful scan')
        failed_ids.add(identifier)
        name = failure.get('full_name')
        if (not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9-]+/[A-Za-z0-9_.-]+', name)
                or failure.get('url') != 'https://github.com/' + name
                or public_https_error(failure.get('url'))):
            errors.append(f'source index failure {index}: invalid public GitHub repository URL')

    def nonnegative_integer(value):
        return type(value) is int and value >= 0

    # Legacy snapshots retain discovery counts without an ID ledger. Do not
    # invent identities for their historical unattempted candidates.
    if 'discovered_repository_ids' in meta:
        ledger = meta['discovered_repository_ids']
        if (not isinstance(ledger, list)
                or any(not isinstance(identifier, str) or not re.fullmatch(r'scan-[0-9]+', identifier)
                       for identifier in ledger)):
            errors.append('Source index discovery ledger must be an array of scan IDs.')
        else:
            known = set(ledger)
            if len(known) != len(ledger):
                errors.append('Source index discovery ledger contains duplicate IDs.')
            attempted_ids = [entry.get('id') for entry in records + failures if isinstance(entry, dict)]
            if any(not isinstance(identifier, str) or not re.fullmatch(r'scan-[0-9]+', identifier)
                   for identifier in attempted_ids):
                errors.append('Source index attempted repositories must have valid scan IDs.')
            elif not set(attempted_ids).issubset(known):
                errors.append('Source index attempted IDs must be present in the discovery ledger.')
            if not nonnegative_integer(meta.get('unique_repos')) or meta['unique_repos'] != len(known):
                errors.append('Source index unique repository count must match the discovery ledger.')
            if (not nonnegative_integer(meta.get('unattempted_candidates'))
                    or meta['unattempted_candidates'] != len(known) - len(records) - len(failures)):
                errors.append('Source index unattempted count must equal known IDs minus attempted repositories.')

    if 'current_run' in meta:
        run = meta['current_run']
        if not isinstance(run, dict):
            errors.append('Source index current_run must be an object.')
        else:
            for retained_key, new_key, total in (
                    ('retained_successful_readme_scans', 'new_successful_readme_scans', len(records)),
                    ('retained_failed_readme_scans', 'new_failed_readme_scans', len(failures))):
                retained, added = run.get(retained_key), run.get(new_key)
                if not nonnegative_integer(retained) or not nonnegative_integer(added):
                    errors.append(f'Source index current_run {retained_key}/{new_key} must be nonnegative integers.')
                elif retained + added != total:
                    errors.append(f'Source index current_run {retained_key} plus {new_key} does not match the snapshot total.')
            observation_counters = [
                    ('queries', 'query_start_index', 'query_count'),
                    ('seed_observations', 'seed_observation_start_index', 'seed_observation_count')]
            if ('resume_observations' in meta or 'resume_observation_start_index' in run
                    or 'resume_observation_count' in run):
                observation_counters.append(('resume_observations', 'resume_observation_start_index', 'resume_observation_count'))
            for observations_key, offset_key, count_key in observation_counters:
                observations = meta.get(observations_key, [])
                offset, count = run.get(offset_key), run.get(count_key)
                if (not isinstance(observations, list) or not nonnegative_integer(offset)
                        or not nonnegative_integer(count)):
                    errors.append(f'Source index current_run {offset_key}/{count_key} needs valid counters and an observation array.')
                elif offset + count != len(observations):
                    errors.append(f'Source index current_run {offset_key} plus {count_key} does not match {observations_key}.')
                elif any(not isinstance(entry, dict) or entry.get('run_id') != run.get('run_id')
                         for entry in observations[offset:]):
                    errors.append(f'Source index current_run {observations_key} includes observations from a different run.')
            if 'requested_new_successful_scans' in run:
                target, retained = meta.get('requested_successful_scans'), run.get('retained_successful_readme_scans')
                requested = run['requested_new_successful_scans']
                if (not nonnegative_integer(target) or not nonnegative_integer(retained)
                        or not nonnegative_integer(requested) or requested != max(0, target - retained)):
                    errors.append('Source index current_run requested new successes do not match the combined target.')
            if 'readme_queue_candidates' in run:
                queued = run['readme_queue_candidates']
                successes, failed = run.get('new_successful_readme_scans'), run.get('new_failed_readme_scans')
                if (not nonnegative_integer(queued) or not nonnegative_integer(successes)
                        or not nonnegative_integer(failed) or queued < successes + failed):
                    errors.append('Source index current_run README queue must cover all new attempted repositories.')
                retained_successes, retained_failures = (run.get('retained_successful_readme_scans'),
                                                         run.get('retained_failed_readme_scans'))
                if (all(nonnegative_integer(value) for value in (queued, retained_successes, retained_failures, meta.get('unique_repos')))
                        and queued > meta['unique_repos'] - retained_successes - retained_failures):
                    errors.append('Source index current_run README queue exceeds known unretained repository IDs.')
            for field in ('seed_curated', 'seed_papers'):
                if field in run and not isinstance(run[field], bool):
                    errors.append(f'Source index current_run {field} must be a boolean.')
            if 'retained_unattempted_repository_ids' in run:
                pending, count = run['retained_unattempted_repository_ids'], run.get('resume_observation_count')
                if not nonnegative_integer(pending) or not nonnegative_integer(count) or count > pending:
                    errors.append('Source index current_run resume lookups cannot exceed retained unattempted IDs.')
                history = meta.get('resume_history')
                if run.get('mode') == 'fresh':
                    if pending != 0 or count != 0:
                        errors.append('Source index fresh run cannot claim retained repository lookups.')
                elif run.get('mode') == 'resume' and isinstance(history, list) and history and isinstance(history[-1], dict):
                    previous = history[-1]
                    prior_known = previous.get('known_repository_ids')
                    prior_successes, prior_failed = previous.get('successful_readme_scans'), previous.get('failed')
                    if (not all(nonnegative_integer(value) for value in (prior_known, prior_successes, prior_failed))
                            or pending != prior_known - prior_successes - prior_failed
                            or run.get('retained_successful_readme_scans') != prior_successes
                            or run.get('retained_failed_readme_scans') != prior_failed):
                        errors.append('Source index current_run retained counts disagree with the prior snapshot.')
                else:
                    errors.append('Source index retained repository lookups need a valid run mode and resume history.')
                observations = meta.get('resume_observations', [])
                offset = run.get('resume_observation_start_index')
                if isinstance(observations, list) and nonnegative_integer(offset):
                    current_ids = [entry.get('repository_id') for entry in observations[offset:]
                                   if isinstance(entry, dict) and isinstance(entry.get('repository_id'), str)]
                    if len(set(current_ids)) != len(current_ids):
                        errors.append('Source index current_run repeats a retained repository metadata lookup.')
                    retained_successes, retained_failures = (run.get('retained_successful_readme_scans'),
                                                             run.get('retained_failed_readme_scans'))
                    if nonnegative_integer(retained_successes) and nonnegative_integer(retained_failures):
                        retained_ids = {entry.get('id') for entry in records[:retained_successes] + failures[:retained_failures]
                                        if isinstance(entry, dict) and isinstance(entry.get('id'), str)}
                        if retained_ids.intersection(current_ids):
                            errors.append('Source index current_run metadata lookups must exclude retained README attempts.')
    validate_scan_discovery(meta, records, errors, failures)
    return len(records)


def list_item_prefix(line):
    """Return (marker column, content column, marker) within the current container."""
    match = re.match(r'^( {0,3})([-+*]|[0-9]{1,9}[.)])(?: +(.*)|$)', line)
    if not match:
        return None
    marker_column = len(match[1])
    marker_end = marker_column + len(match[2])
    padding = len(line[marker_end:]) - len(line[marker_end:].lstrip(' '))
    # Five or more spaces leave an indented code block after one padding space.
    content_column = marker_end + (padding if 1 <= padding <= 4 else 1)
    return marker_column, content_column, match[2]


def fence_start(line):
    match = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
    if match and not (match[1][0] == '`' and '`' in match[2]):
        return match[1][0], len(match[1])
    return None


def nonparagraph_block(line, paragraph=False):
    """Block starts relevant to list laziness and indented-code interruption."""
    return bool(re.match(r'^ {0,3}(?:#{1,6}(?: |$)|>)', line)
                or re.match(r'^ {0,3}</?pre(?:[ >]|$)', line, re.IGNORECASE)
                or (paragraph and re.fullmatch(r' {0,3}(?:=+|-+) *', line))
                or any(re.fullmatch(r' {0,3}(?:' + re.escape(char) + r' *){3,}', line)
                       for char in '*_-'))


def mask_inline_code(text):
    """Mask equal-length backtick spans within one paragraph, preserving newlines."""
    runs = list(re.finditer(r'`+', text))
    parts, cursor, index = [], 0, 0
    while index < len(runs):
        opening = runs[index]
        prefix = text[:opening.start()]
        escapes = len(prefix) - len(prefix.rstrip('\\'))
        if escapes % 2:
            index += 1
            continue
        closing_index = next((following for following in range(index + 1, len(runs))
                              if len(runs[following][0]) == len(opening[0])), None)
        if closing_index is None:
            index += 1
            continue
        end = runs[closing_index].end()
        parts.append(text[cursor:opening.start()])
        parts.append(re.sub(r'[^\r\n]', ' ', text[opening.start():end]))
        cursor, index = end, closing_index + 1
    return ''.join(parts) + text[cursor:]


def prose_only(text, *, inline_code=False, include_pre_ranges=False):
    """Mask code blocks while retaining list prose, original indentation and line numbers."""
    # Items store marker/content columns, marker style, and whether they have content.
    lines, containers, fence = [], [], None
    paragraph = False
    paragraph_lines = []
    pre_base, pre_start = None, None
    pre_ranges = []

    def finish_pre():
        nonlocal pre_base, pre_start
        pre_ranges.append((pre_start, sum(map(len, lines))))
        pre_base, pre_start = None, None

    def flush_paragraph():
        value = ''.join(paragraph_lines)
        lines.append(mask_inline_code(value) if inline_code else value)
        paragraph_lines.clear()

    for raw in text.splitlines(keepends=True):
        ending = re.search(r'(\r\n|\n|\r)$', raw)
        masked = ending[0] if ending else ''
        line = raw.rstrip('\r\n').expandtabs(4)
        indent = len(line) - len(line.lstrip(' '))
        blank = not line.strip()
        if pre_base is not None:
            if blank or indent >= pre_base:
                # Keep raw HTML for links; default anchor extraction still masks indentation.
                lines.append(raw if inline_code or indent < 4 else masked)
                paragraph = False
                if re.search(r'</pre\s*>', line, re.IGNORECASE):
                    finish_pre()
                continue
            finish_pre()
        if fence:
            # An unclosed fence ends when its containing list item ends.
            if blank or indent >= fence[2]:
                closing = re.fullmatch(r' {0,3}(`{3,}|~{3,}) *', line[fence[2]:])
                if closing and closing[1][0] == fence[0] and len(closing[1]) >= fence[1]:
                    fence = None
                lines.append(masked)
                continue
            fence = None
        if blank:
            flush_paragraph()
            # A blank line ends an item that has not contained any content yet.
            while containers and not containers[-1][3]:
                containers.pop()
            paragraph = False
            lines.append(raw)
            continue

        base = containers[-1][1] if containers else 0
        if indent < base:
            outer = next((item[1] for item in reversed(containers) if item[1] <= indent), 0)
            candidate = line[outer:]
            prefix = list_item_prefix(candidate)
            starts_list = False
            if prefix:
                marker_column, content_column, marker = prefix
                sibling = any(outer + marker_column == item[0] and marker[-1] == item[2]
                              for item in containers)
                can_interrupt = marker in '-+*' or int(marker[:-1]) == 1
                starts_list = sibling or (candidate[content_column:].strip() and can_interrupt)
            interrupts = fence_start(candidate) or nonparagraph_block(candidate, paragraph) or starts_list
            if paragraph and not interrupts:
                # A lazy continuation belongs to the open list paragraph despite dedenting.
                paragraph_lines.append(raw)
                continue
            flush_paragraph()
            while containers and indent < containers[-1][1]:
                containers.pop()
            paragraph = False
            base = containers[-1][1] if containers else 0

        body = line[base:]
        if body.strip():
            containers = [(*item[:3], True) for item in containers]
        while not nonparagraph_block(body, paragraph):
            prefix = list_item_prefix(body)
            if not prefix:
                break
            marker_column, content_column, marker = prefix
            content = body[content_column:]
            can_interrupt = marker in '-+*' or int(marker[:-1]) == 1
            if paragraph and (not content.strip() or not can_interrupt):
                break
            flush_paragraph()
            containers.append((base + marker_column, base + content_column, marker[-1], bool(content.strip())))
            base += content_column
            body = line[base:]
            paragraph = False

        opening = fence_start(body)
        if re.match(r'^ {0,3}<pre(?:[ >]|$)', body, re.IGNORECASE):
            flush_paragraph()
            pre_base, pre_start = base, sum(map(len, lines))
            lines.append(raw)
            paragraph = False
            if re.search(r'</pre\s*>', body, re.IGNORECASE):
                finish_pre()
        elif opening:
            flush_paragraph()
            fence = (*opening, base)
            paragraph = False
            lines.append(masked)
        elif len(body) - len(body.lstrip(' ')) >= 4 and not paragraph:
            flush_paragraph()
            lines.append(masked)
        else:
            continues_paragraph = bool(body.strip()) and not nonparagraph_block(body, paragraph)
            if continues_paragraph:
                paragraph_lines.append(raw)
            else:
                flush_paragraph()
                lines.append(mask_inline_code(raw) if inline_code else raw)
            paragraph = continues_paragraph
    flush_paragraph()
    if pre_base is not None:
        finish_pre()
    result = ''.join(lines)
    return (result, pre_ranges) if include_pre_ranges else result


def markdown_anchors(text):
    prose = prose_only(text)
    anchors = set(re.findall(r'<[A-Za-z][^>]*\b(?:id|name)=["\']([^"\']+)["\']', prose))
    counts = {}
    lines = prose.splitlines()
    for index, line in enumerate(lines):
        match = re.match(r'^ {0,3}#{1,6}\s+(.+?)(?:\s+#+\s*)?$', line)
        heading = match[1] if match else None
        if heading is None and index + 1 < len(lines) and re.fullmatch(r' {0,3}(?:=+|-+)\s*', lines[index + 1]) and line.strip():
            heading = line.strip()
        if heading is None:
            continue
        heading = re.sub(r'!?\[([^\]]+)\]\([^)]*\)', r'\1', heading)
        heading = html.unescape(re.sub(r'<[^>]+>', '', heading))
        slug = re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        anchors.add(slug if count == 0 else f'{slug}-{count}')
    return anchors


LINK_PATTERN = re.compile(r'\]\(\s*(<[^>\n]+>|(?:\\.|[^\s()]|\([^()\n]*\))+)(?:\s+["\'][^\n]*?["\'])?\s*\)')
REFERENCE_PATTERN = re.compile(r'^ {0,3}\[[^\]\n]+\]:\s*(<[^>\n]+>|\S+)', re.MULTILINE)
HTML_LINK_PATTERN = re.compile(r'<[A-Za-z][^>]*?\b(?:href|src)=["\']([^"\']+)["\']', re.IGNORECASE)


def document_links(text):
    # Inline spans may cross lines, but never a paragraph or block boundary.
    prose, pre_ranges = prose_only(text, inline_code=True, include_pre_ranges=True)
    markdown = prose
    for start, end in reversed(pre_ranges):
        markdown = markdown[:start] + re.sub(r'[^\r\n]', ' ', markdown[start:end]) + markdown[end:]
    # Raw HTML links remain clickable inside <pre>; Markdown-like text does not.
    for pattern, content in ((LINK_PATTERN, markdown), (REFERENCE_PATTERN, markdown),
                             (HTML_LINK_PATTERN, prose)):
        for match in pattern.finditer(content):
            destination = html.unescape(match[1].strip('<>'))
            yield destination, content.count('\n', 0, match.start()) + 1


def validate_markdown(root, errors):
    documents = [path for path in root.rglob('*.md')
                 if not any(part in IGNORED_DIRS for part in path.relative_to(root).parts)]
    anchors = {}
    for path in documents:
        text = path.read_text(encoding='utf-8')
        for destination, line in document_links(text):
            parsed = urlsplit(destination)
            if parsed.scheme or parsed.netloc:
                continue
            where = f'{path.relative_to(root)}:{line}'
            local = unquote(parsed.path).replace('\\ ', ' ')
            target = (root / local.lstrip('/') if local.startswith('/') else path.parent / local).resolve() if local else path
            if not target.is_relative_to(root.resolve()):
                errors.append(f'{where}: local link escapes repository: {destination}')
                continue
            if not target.exists():
                errors.append(f'{where}: missing local link target: {destination}')
                continue
            fragment = unquote(parsed.fragment)
            if not fragment:
                continue
            if target.is_dir():
                target = target / 'README.md'
                if not target.exists():
                    errors.append(f'{where}: directory fragment has no README target: {destination}')
                    continue
            if target.suffix.lower() in {'.md', '.markdown'}:
                if target not in anchors:
                    anchors[target] = markdown_anchors(target.read_text(encoding='utf-8'))
                if fragment.removeprefix('user-content-') not in anchors[target]:
                    errors.append(f'{where}: missing Markdown anchor: {destination}')
            elif target.suffix.lower() in {'.html', '.htm'}:
                ids = set(re.findall(r'\b(?:id|name)=["\']([^"\']+)["\']', target.read_text(encoding='utf-8')))
                if fragment not in ids:
                    errors.append(f'{where}: missing HTML anchor: {destination}')
            elif re.fullmatch(r'L\d+(?:-L\d+)?', fragment):
                bounds = [int(value) for value in re.findall(r'\d+', fragment)]
                count = len(target.read_text(encoding='utf-8').splitlines())
                if not 1 <= bounds[0] <= bounds[-1] <= count:
                    errors.append(f'{where}: source line anchor is out of range: {destination}')
            else:
                errors.append(f'{where}: cannot validate fragment on this local file type: {destination}')
    return len(documents)


def validate_citation(text, errors, *, now=None):
    """Keep CITATION.cff's release fields paired, semantic and not ahead of the calendar.

    Whether they match a real tag and release date is a maintainer release step.
    """
    now = dt.datetime.now(dt.timezone.utc) if now is None else now
    fields = dict(re.findall(r'^(version|date-released):[ \t]*(.*?)[ \t]*$', text, re.MULTILINE))
    if not fields:
        return
    if set(fields) != {'version', 'date-released'}:
        errors.append('CITATION.cff: set version and date-released together, from the same release tag')
        return
    if not re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)', fields['version']):
        errors.append('CITATION.cff.version: use the release tag as MAJOR.MINOR.PATCH without a leading v')
    try:
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', fields['date-released']):
            raise ValueError
        if review_date_is_future(dt.date.fromisoformat(fields['date-released']), now):
            errors.append('CITATION.cff.date-released: release date is in the future')
    except ValueError:
        errors.append('CITATION.cff.date-released: use the unquoted YYYY-MM-DD release date')


def validate_requirement_facets(records, translations, errors):
    """Every facet comes from the vocabulary and labels the same item in English and Chinese."""
    for record in records:
        if isinstance(record, dict) and 'requirements' in record:
            chinese = record.get('requirements_zh') or translations.get(record.get('id'), {}).get('requirements')
            errors.extend(f"resource {record.get('id')!r}.{message}" for message in facet_errors(record, chinese))


def read_array(path, errors):
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        errors.append(f'{path.relative_to(ROOT)}: cannot read JSON: {error}')
        return []
    if not isinstance(value, list) or not value:
        errors.append(f'{path.relative_to(ROOT)}: expected a nonempty JSON array')
        return []
    return value


def main():
    errors = []
    records = [record for path in RESOURCE_FILES for record in read_array(path, errors)]
    benchmarks = read_array(ROOT / 'data/benchmarks.json', errors)
    papers = read_array(ROOT / 'data/papers.json', errors)
    validate_papers(papers, errors, url_check=public_https_error)
    validate_resources(records, errors)
    for warning in evidence_pin_warnings(records):
        print(f'Warning: {warning}', file=sys.stderr)
    validate_requirement_facets(records, json.loads((ROOT / 'site/translations.zh-CN.json').read_text(encoding='utf-8')), errors)
    validate_benchmarks(benchmarks, errors)
    try:
        validate_case_coverage(read_case_coverage(ROOT), records, papers, errors,
                               url_check=public_https_error)
    except (OSError, ValueError):
        errors.append('Case coverage could not be read as strict JSON.')
    scanned = 0
    index_path = ROOT / 'data/source-index.json'
    if index_path.exists():
        try:
            index_document = json.loads(index_path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            errors.append('Source index could not be read as JSON.')
        else:
            scanned = validate_source_index(index_document, errors)
            source_records = index_document.get('resources') if isinstance(index_document, dict) else None
            if (isinstance(source_records, list)
                    and all(isinstance(record, dict) and isinstance(record.get('id'), str)
                            for record in source_records)):
                try:
                    validate_localizations(source_records, read_localizations(ROOT), errors)
                except (OSError, ValueError):
                    errors.append('Repository localizations could not be read as valid JSON.')
                try:
                    validate_scope(source_records, read_scope(ROOT), errors)
                except (OSError, ValueError):
                    errors.append('Source-scope data could not be read as valid JSON.')
    validate_citation((ROOT / 'CITATION.cff').read_text(encoding='utf-8'), errors)
    count = validate_markdown(ROOT, errors)
    for script in ('build_readme.py', 'build_repository_index.py', 'build_case_coverage.py'):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts' / script), '--check'],
                                cwd=ROOT, encoding='utf-8', capture_output=True, check=False,
                                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
        if result.returncode:
            errors.append((result.stderr or result.stdout).strip() or f'{script}: generated content check failed.')
    if errors:
        print(f'Validation failed with {len(errors)} issue(s):', file=sys.stderr)
        for error in errors:
            print(f'- {error}', file=sys.stderr)
        return 1
    print(f'Validated {len(records)} curated resources, {len(papers)} research papers, {scanned} scanned sources, {len(benchmarks)} benchmark snapshots, {count} Markdown files, both generated catalogs, and the bilingual repository index.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
