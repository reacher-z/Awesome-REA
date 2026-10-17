#!/usr/bin/env python3
"""Review catalog PRs with trusted base-branch code; never execute PR code."""
import fnmatch
import json
import html
import os
from pathlib import Path
import re
import sys
import urllib.parse
import urllib.request

from validate import validate_benchmarks, validate_resources, validate_source_index, public_https_error
from validate_papers import validate_papers
from localization import LOCALE_FILES, validate_localizations
from source_scope import validate_scope
from case_coverage import validate_case_coverage

ROOT = Path(__file__).resolve().parents[1]
MARKER = '<!-- awesome-rea-automated-review -->'
CATALOGS = ('data/rea-resources.json', 'data/tool-resources.json')
SOURCE_INDEX = 'data/source-index.json'
SOURCE_SCOPE = 'data/source-scope.json'
SOURCE_INPUTS = (SOURCE_INDEX, SOURCE_SCOPE, *LOCALE_FILES)
CASE_COVERAGE = 'data/case-coverage.json'
CASE_INPUTS = (CASE_COVERAGE, *CATALOGS, 'data/papers.json')
REVIEW_FILES = frozenset((*CATALOGS, 'data/benchmarks.json', 'data/papers.json', *SOURCE_INPUTS, CASE_COVERAGE))
LOCALE_FIELDS = {'description_en', 'description_zh', 'english_retains_name', 'technical_only'}
SENSITIVE = re.compile(r'gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16}|-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY(?: BLOCK)?-----')
# Personal paths: macOS/Linux homes, Windows or WSL profiles with either separator, /root, ~ and $HOME.
# Matches stop before the next separator.
_NAME = r'[^\s/\\"\'`<>{}()\[\]|:;,*?]'
_SEGMENT = _NAME + '+'
_SEP = r'(?:/|\\+)'
_PROFILE = _SEP + '(?i:users)' + _SEP + _SEGMENT
LOCAL_PATH = re.compile('|'.join((
    r'/(?:Users|home)/' + _SEGMENT + '(?=' + _SEP + ')',
    # The other forms must start at a path boundary, so URLs and prose such as login/root/premium do not match.
    r'/(?<![\w.~$%-]/)(?:(?:Users|home)/' + _SEGMENT + '|(?i:users|home)/' + _SEGMENT + '(?=' + _SEP + ')'
    r'|(?:mnt/)?[A-Za-z]' + _PROFILE + '|root(?=/' + _NAME + '))',
    r'[A-Za-z]:(?<![\w.~$%-]..)' + _PROFILE,
    r'~(?<![\w.~$%/\\-]~)(?=' + _SEP + _NAME + ')',
    r'\$(?<![\w.~$%/\\-]\$)(?:HOME|\{HOME\})(?=' + _SEP + _NAME + ')',
)))
JSON_ESCAPE = re.compile(r'\\(?:u([0-9A-Fa-f]{4})|([\\/]))')
SAFE_LABEL = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.:/-]{0,99}')
# File-name rules cover every .gitignore pattern (tests/test_review_pr.py checks this) plus keys, captures and fonts.
PRIVATE_NAMES = ('.env', '.env.*', 'secrets.json', 'credentials*.json', '*.local.json', '*.pem', '*.key',
                 'id_rsa', 'id_dsa', 'id_ecdsa', 'id_ed25519', '*.har', '*.pcap', '*.pcapng')
PRIVATE_DIRS = {'.cloudflare', '.wrangler'}
GENERATED_NAMES = ('*.py[cod]', '.ds_store', '*.woff', '*.woff2')
GENERATED_DIRS = {'__pycache__', '.cache', '.venv', 'dist', 'node_modules', 'output'}
PUBLIC_NAMES = {'.env.example'}
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_OMITTED_FILES = 20
MAX_REVIEW_PAGES = 10


def api(repository, endpoint, token, method='GET', payload=None, raw=False):
    url = f'https://api.github.com/repos/{repository}/{endpoint}'
    headers = {'Accept': 'application/vnd.github.raw+json' if raw else 'application/vnd.github+json',
               'Authorization': f'Bearer {token}', 'X-GitHub-Api-Version': '2022-11-28',
               'User-Agent': 'awesome-rea-catalog-review'}
    body = json.dumps(payload).encode() if payload is not None else None
    if body is not None:
        headers['Content-Type'] = 'application/json'
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=45) as response:
        data = response.read(MAX_FILE_BYTES + 1)
    if len(data) > MAX_FILE_BYTES:
        raise ValueError('API response exceeds the review size limit')
    return data.decode('utf-8') if raw else json.loads(data)


def raw_text_at(repository, filename, sha, token):
    path = urllib.parse.quote(filename, safe='/')
    return api(repository, f'contents/{path}?ref={sha}', token, raw=True)


def content_at(repository, filename, sha, token):
    # Contributor files are retrieved only as text from this exact data allowlist.
    if filename not in REVIEW_FILES:
        raise ValueError('File is not an allowed review data input')
    return raw_text_at(repository, filename, sha, token)


def omitted_text_at(repository, filename, sha, token):
    # Only for a changed file whose diff GitHub omitted: its text is pattern-checked as
    # size-bounded data and is never executed, parsed as code, or echoed.
    if filename in REVIEW_FILES or path_rule(filename) or any(part in ('', '.', '..') for part in filename.split('/')):
        raise ValueError('File is not an allowed omitted-diff input')
    text = raw_text_at(repository, filename, sha, token)
    if '\x00' in text:
        raise UnicodeError('Binary file')
    return text


def private_text(text):
    """Pattern backstop on raw text and on the same text with JSON-style escapes decoded."""
    values = [text]
    if '\\' in text:
        values.append(JSON_ESCAPE.sub(lambda match: chr(int(match[1], 16)) if match[1] else match[2], text))
    return any(pattern.search(value) for value in values for pattern in (SENSITIVE, LOCAL_PATH))


def path_rule(path):
    *directories, name = path.lower().split('/')
    if ((name not in PUBLIC_NAMES and any(fnmatch.fnmatchcase(name, rule) for rule in PRIVATE_NAMES))
            or PRIVATE_DIRS.intersection(directories)):
        return 'private configuration, keys, and raw captures should not be committed.'
    if any(fnmatch.fnmatchcase(name, rule) for rule in GENERATED_NAMES) or GENERATED_DIRS.intersection(directories):
        return 'generated, raw, or licensed production assets do not belong in this public source repository.'
    return None


def private_json_locations(value, record=None, field=None, top=True):
    """Return (record ID, field) for decoded JSON keys and strings that match the privacy patterns."""
    if isinstance(value, str):
        return [(record, field)] if private_text(value) else []
    found = []
    if isinstance(value, dict):
        if isinstance(value.get('id'), str):
            record = value['id']
        for key, item in value.items():
            if private_text(key):
                found.append((record, None))
            # Locale and scope files are objects keyed by resource ID.
            found += private_json_locations(item, key if top and isinstance(item, dict) else record, key, False)
    elif isinstance(value, list):
        for item in value:
            found += private_json_locations(item, record, field, False)
    return found


def json_privacy_findings(filename, text):
    # GitHub can omit or truncate a large file's patch, and JSON escapes change raw text but
    # not the published value, so check the fetched text and its decoded strings.
    try:
        locations = list(dict.fromkeys(private_json_locations(parse_json(text))))
    except (ValueError, TypeError, RecursionError):
        locations = []
    if not locations:
        return [f'{filename}: full JSON content contains a credential-like value or personal path; inspect locally. The value is omitted here.'] if private_text(text) else []
    findings = []
    for record, field in locations[:5]:
        where = [f'{name} {value}' for name, value in (('record', record), ('field', field))
                 if isinstance(value, str) and SAFE_LABEL.fullmatch(value) and not private_text(value)]
        findings.append(f'{filename}: a decoded JSON string{" in " + ", ".join(where) if where else ""} contains a credential-like value or personal path; inspect locally. The value is omitted here.')
    if len(locations) > 5:
        findings.append(f'{filename}: {len(locations) - 5} more decoded JSON strings match these patterns.')
    return findings


def parse_json(text):
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON key')
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError('Non-JSON numeric constant')

    return json.loads(text, object_pairs_hook=unique_object, parse_constant=invalid_constant)


def review_localizations(records, contents, errors):
    translations = {}
    for filename in LOCALE_FILES:
        if filename not in contents:
            errors.append(f'{filename}: required localization data is missing.')
            continue
        try:
            entries = parse_json(contents[filename])
        except (ValueError, TypeError):
            errors.append(f'{filename}: expected valid JSON without duplicate keys.')
            continue
        if not isinstance(entries, dict):
            errors.append(f'{filename}: expected an object keyed by resource ID.')
            continue
        overlap = translations.keys() & entries.keys()
        if overlap:
            errors.append(f'{filename}: {len(overlap)} localization IDs also occur in another locale file.')
        for identifier, entry in entries.items():
            if not isinstance(entry, dict):
                errors.append(f'{filename}: localization {identifier!r} must be an object.')
                continue
            if set(entry) - LOCALE_FIELDS:
                errors.append(f'{filename}: localization {identifier!r} has unsupported fields.')
            for flag in ('english_retains_name', 'technical_only'):
                if flag in entry and type(entry[flag]) is not bool:
                    errors.append(f'{filename}: localization {identifier!r} has a non-boolean {flag}.')
            translations[identifier] = entry
    validate_localizations(records, translations, errors)
    return len(translations)


def load_review_contents(repository, sha, token, files, changed, errors):
    needed = set(changed & REVIEW_FILES)
    if set(CATALOGS) & changed:
        needed.update(CATALOGS)
    if set(SOURCE_INPUTS) & changed:
        needed.update(SOURCE_INPUTS)
    if set(CASE_INPUTS) & changed:
        needed.update(CASE_INPUTS)
    removed = {entry['filename'] for entry in files if entry['status'] == 'removed'}
    removed.update(entry['previous_filename'] for entry in files
                   if entry['status'] == 'renamed' and 'previous_filename' in entry)
    contents = {}
    for filename in sorted(needed):
        if filename in removed:
            errors.append(f'{filename}: removing or renaming catalog, localization, or scope data requires maintainer review.')
            continue
        try:
            if filename in changed:
                contents[filename] = content_at(repository, filename, sha, token)
            else:
                # Unchanged source, locale, and scope dependencies come from the trusted base.
                contents[filename] = (ROOT / filename).read_text(encoding='utf-8')
            if filename in changed:
                errors.extend(json_privacy_findings(filename, contents[filename]))
        except (OSError, UnicodeError, ValueError):
            errors.append(f'{filename}: could not safely retrieve required JSON data for this review.')
    return contents


def review_data(contents, changed):
    errors, reviewed = [], []
    if set(CASE_INPUTS) & changed:
        case_records = []
        for filename in CATALOGS:
            data = parse_json(contents[filename])
            if not isinstance(data, list):
                errors.append(f'{filename}: expected a JSON array for coverage mappings.')
            else:
                case_records.extend(data)
        case_papers = parse_json(contents['data/papers.json'])
        if not isinstance(case_papers, list):
            errors.append('Research papers must be an array for coverage mappings.')
        else:
            validate_case_coverage(parse_json(contents[CASE_COVERAGE]), case_records,
                                   case_papers, errors, url_check=public_https_error)
            reviewed.append('Case inventory checked for pinned sources, typed catalog mappings, alias decisions and occurrence/report counts; no project count or runtime reproduction inferred.')
    if 'data/papers.json' in changed:
        papers = parse_json(contents['data/papers.json'])
        validate_papers(papers, errors, url_check=public_https_error)
        reviewed.append('Research papers checked separately for bibliography, bilingual scope, dates, duplicate identifiers and public source URLs.')
    if set(CATALOGS) & changed:
        records = []
        for filename in CATALOGS:
            data = parse_json(contents[filename])
            if not isinstance(data, list):
                errors.append(f'{filename}: expected a JSON array.')
            else:
                records.extend(data)
        validate_resources(records, errors)
        reviewed.append(f'{len(records)} curated records checked together for schema, duplicate IDs/URLs, provenance, targets, dates, and review labels.')
    if 'data/benchmarks.json' in changed:
        data = parse_json(contents['data/benchmarks.json'])
        if not isinstance(data, list):
            errors.append('Benchmarks must be an array.')
        else:
            validate_benchmarks(data, errors)
            reviewed.append(f'{len(data)} benchmark records checked for timestamp, count, and source consistency.')
    if set(SOURCE_INPUTS) & changed:
        data = parse_json(contents[SOURCE_INDEX])
        validate_source_index(data, errors)
        reviewed.append('Automated source-index records checked separately from curated resources.')
        if (isinstance(data, dict) and isinstance(data.get('resources'), list)
                and all(isinstance(record, dict) and isinstance(record.get('id'), str)
                        for record in data['resources'])):
            count = review_localizations(data['resources'], contents, errors)
            reviewed.append(f'{count} repository localizations checked across all locale files for coverage, duplicate IDs, bilingual descriptions, and explicit language exceptions.')
            if SOURCE_SCOPE not in contents:
                errors.append(f'{SOURCE_SCOPE}: required source-scope data is missing.')
            else:
                try:
                    scope = parse_json(contents[SOURCE_SCOPE])
                except (ValueError, TypeError):
                    errors.append(f'{SOURCE_SCOPE}: expected valid JSON without duplicate keys.')
                else:
                    validate_scope(data['resources'], scope, errors)
                    reviewed.append('Source-scope exclusions checked against repository IDs, README hashes, evidence links, dates, and bilingual reasons.')
    return errors, reviewed


def safe_text(value):
    # Strip controls and join whitespace before redacting, so neither can rejoin a hidden value.
    value = re.sub(r'[\x00-\x08\x0b-\x1f\x7f\u202a-\u202e\u2066-\u2069]', '', str(value))
    value = SENSITIVE.sub('[redacted credential-like value]', ' '.join(value.split()))
    value = LOCAL_PATH.sub('[redacted local path]', value)
    if private_text(value):
        value = '[redacted text with an escaped credential-like value or personal path]'
    value = value[:500].replace('@', '@\u200b')
    value = html.escape(value, quote=False)
    return re.sub(r'([\\`*_{}\[\]()#+.!|])', r'\\\1', value)


def find_existing_review(repository, number, sha, token):
    # Reviews are listed oldest first; a deleted account's review has a null user.
    for page in range(1, MAX_REVIEW_PAGES + 1):
        batch = api(repository, f'pulls/{number}/reviews?per_page=100&page={page}', token)
        for review in batch:
            user = review.get('user')
            if (isinstance(user, dict) and user.get('login') == 'github-actions[bot]' and user.get('type') == 'Bot'
                    and MARKER in (review.get('body') or '') and review.get('commit_id') == sha):
                return review
        if len(batch) < 100:
            break
    return None


def main():
    token = os.environ['GITHUB_TOKEN']
    repository = os.environ['GITHUB_REPOSITORY']
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        raise ValueError('Invalid repository name')
    event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text(encoding='utf-8'))
    number = int(event['pull_request']['number'])
    pull = api(repository, f'pulls/{number}', token)
    sha = pull['head']['sha']
    if not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise ValueError('Unexpected head SHA')
    existing_review = find_existing_review(repository, number, sha, token)
    files = []
    for page in range(1, 4):
        batch = api(repository, f'pulls/{number}/files?per_page=100&page={page}', token)
        files.extend(batch)
        if len(batch) < 100:
            break
    changed = {entry['filename'] for entry in files}
    changed.update(entry['previous_filename'] for entry in files
                   if entry['status'] == 'renamed' and 'previous_filename' in entry)
    errors, reviewed, omitted, not_inspected = [], [], [], []
    if pull.get('changed_files', len(files)) > 300:
        errors.append('This PR exceeds the 300-file automatic review limit; split it for a complete review.')
    for entry in files:
        path = entry['filename']
        # Removing such a file is a cleanup, not a new commit of it.
        rule = path_rule(path) if entry['status'] != 'removed' else None
        if rule:
            # Named by path only; such files are never fetched.
            errors.append(f'{path}: {rule}')
        patch = entry.get('patch')
        if patch:
            added = '\n'.join(line[1:] for line in patch.splitlines() if line.startswith('+') and not line.startswith('+++'))
            if private_text(added):
                errors.append(f'{path}: added text contains a credential-like value or personal path; inspect locally. The value is omitted here.')
        elif entry['status'] not in ('removed', 'unchanged') and not rule and path not in REVIEW_FILES:
            # GitHub omits the patch of binary files and very large diffs.
            omitted.append(path)
        if (path.startswith('data/locales/') and path not in LOCALE_FILES
                and path != 'data/locales/README.md'):
            errors.append(f'{path}: locale file is not in the trusted review allowlist; maintainer review is required.')
    for index, path in enumerate(omitted):
        try:
            text = omitted_text_at(repository, path, sha, token) if index < MAX_OMITTED_FILES else None
        except (OSError, UnicodeError, ValueError):
            text = None
        if text is None:
            not_inspected.append(path)
        elif private_text(text):
            errors.append(f'{path}: GitHub omitted this diff, and the file text at this commit contains a credential-like value or personal path; inspect locally. The value is omitted here.')
    contents = load_review_contents(repository, sha, token, files, changed, errors)
    try:
        findings, checked = review_data(contents, changed & REVIEW_FILES)
        errors.extend(findings)
        reviewed.extend(checked)
    except (ValueError, TypeError, KeyError):
        errors.append('Required catalog, localization, or source-scope JSON could not be parsed or validated. Check its shape locally.')
    manual = any(path.startswith(('scripts/', '.github/', 'site/')) for path in changed)
    if errors:
        status = '**Changes need attention.**'
    elif not_inspected:
        status = f'**No issues found by these automatic checks, but {len(not_inspected)} changed file(s) were not inspected.**'
    else:
        status = '**No issues found by these automatic checks.**'
    body = [MARKER, '### Automated catalog review', '', f'Commit: `{sha[:12]}`.', '', status, '']
    body.extend('- ' + safe_text(item) for item in reviewed)
    if errors:
        body.extend(['', 'Findings:'])
        body.extend('- ' + safe_text(item) for item in errors[:30])
        if len(errors) > 30:
            body.append(f'- {len(errors) - 30} additional findings; run the local validator for the complete list.')
    if not_inspected:
        body.extend(['', 'Not inspected automatically: GitHub omitted the diff, and the file could not be retrieved as text within the review limits. A maintainer should check these files:'])
        body.extend('- ' + safe_text(path) for path in not_inspected[:30])
        if len(not_inspected) > 30:
            body.append(f'- {len(not_inspected) - 30} additional files.')
    if manual:
        body.extend(['', 'Code, automation, or site changes require a maintainer to review behavior and permissions.'])
    body.extend(['', 'This is a rule-based review, not a runtime compatibility test or an approval. PR code is never executed by this review job. CI checks and maintainer review remain separate.'])
    # Ensure an obsolete run does not comment against a newly pushed commit.
    if api(repository, f'pulls/{number}', token)['head']['sha'] != sha:
        print('PR head changed; the next run will review the new commit.')
        return
    if existing_review:
        api(repository, f"pulls/{number}/reviews/{int(existing_review['id'])}", token,
            method='PUT', payload={'body': '\n'.join(body)})
    else:
        api(repository, f'pulls/{number}/reviews', token, method='POST',
            payload={'commit_id': sha, 'event': 'COMMENT', 'body': '\n'.join(body)})
    print(f'Posted a rule-based review: {len(errors)} finding(s), {len(not_inspected)} file(s) not inspected; no PR code executed.')
    if errors:
        sys.exit(1)


if __name__ == '__main__':
    main()
