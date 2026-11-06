#!/usr/bin/env python3
"""Followed-source leads: links that registered public sources list, kept as unreviewed discovery records.

The README scanner (scripts/discoveries.py) adds verified README captures of GitHub repositories. This layer
adds what the scanner cannot see or select: entries of other reverse-engineering lists, GitHub topic
searches, machine-readable registries, survey bibliographies, an arXiv query and Hugging Face searches,
including websites, books and papers. The sources and their scope rules are registered in
``data/discovery-sources.json``; ``scripts/collect_discovery_leads.py`` follows them.

A lead records where it was listed (pinned evidence), a stable identity, a name and a kind hint taken from
the listing section, and for GitHub repositories, papers and Hugging Face repositories a metadata snapshot.
It is ``automated-source-lead`` and ``unreviewed``: nobody has read its sources, and being listed by a
secondary source is never evidence for curation (AGENTS.md). Batches are immutable files
``data/discoveries/leads/<YYYY-MM>/leads-<run id>-<attempt>.json``.

Run without options to validate the registry and every lead batch and print the queue size and budget.
"""
from __future__ import annotations

import argparse
from collections import Counter
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import parse_qs, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = 'data/discoveries/leads'
REGISTRY = 'data/discovery-sources.json'
REPOSITORY = 'reacher-z/Awesome-REA'
WORKFLOW_PATH = '.github/workflows/discovery-leads.yml'
INGEST_BRANCH = 'automation/discovery-leads'
INGEST_AUTHOR = 'github-actions[bot]'
KIND = 'automated-lead-batch'
REGISTRY_KIND = 'discovery-source-registry'
REVIEW_STATUS = 'unreviewed'
VERIFICATION = 'automated-source-lead'
POLICY = 'followed-source-leads-v1'
ORDER = 'source-round-robin'
BATCH_NAME = re.compile(r'leads-([1-9][0-9]{0,19})-([1-9][0-9]{0,2})')
MONTH_NAME = re.compile(r'20[0-9]{2}-(?:0[1-9]|1[0-2])')
# Growth budget. A run adds at most MAX_BATCH_RECORDS leads; at the totals the ingest stops and reports it.
MAX_BATCH_RECORDS = 2_000
MAX_TOTAL_RECORDS = 30_000
MAX_BATCH_BYTES = 4 * 1024 * 1024
MAX_TOTAL_BYTES = 48 * 1024 * 1024
MAX_LISTINGS = 12
KINDS = ('project', 'tool', 'integration', 'case-study', 'collection', 'documentation', 'learning-resource', 'research')
SOURCE_TYPES = ('github-readme-list', 'github-topic', 'github-json-registry', 'github-directory', 'survey-references',
                'arxiv-query', 'huggingface-search')
SKIP_REASONS = ('already-curated', 'already-indexed', 'already-discovered', 'already-lead', 'case-lead',
                'scope-excluded', 'unavailable', 'privacy', 'invalid', 'over-limit')
# Why a registered scope rule leaves a listed link out. CONTRIBUTING.md and data/source-scope.json define scope.
EXCLUSION_REASONS = ('security-testing', 'detection-only', 'forensics-only', 'development-tool', 'protection-tool',
                     'malware-samples', 'distribution-site', 'community-or-event', 'general-security',
                     'cheat-or-evasion', 'game-or-engine', 'linking-policy', 'unrelated', 'not-re-subject')
SOURCE_STATUSES = ('captured', 'error', 'not-due')
BATCH_FIELDS = {'schema_version', 'kind', 'batch_id', 'review_status', 'collected_at', 'provenance', 'selection',
                'sources', 'leads'}
PROVENANCE_FIELDS = {'repository', 'workflow_path', 'run_id', 'run_attempt', 'event', 'head_sha', 'registry_sha256'}
SELECTION_FIELDS = {'policy', 'order', 'record_limit', 'eligible_count', 'selected_count', 'selected_ids',
                    'record_sha256', 'skipped_counts'}
SOURCE_RESULT_FIELDS = {'id', 'type', 'evidence_url', 'revision', 'content_sha256', 'status', 'error', 'links',
                        'in_scope'}
LEAD_FIELDS = {'id', 'identity', 'aliases', 'url', 'name', 'kind_hint', 'listings', 'observed_at', 'verification',
               'review_status'}
OPTIONAL_LEAD_FIELDS = {'github', 'paper', 'huggingface'}
LISTING_FIELDS = {'source_id', 'section', 'label', 'evidence_url'}
GITHUB_FIELDS = {'id', 'full_name', 'description', 'topics', 'stars', 'pushed_at', 'archived', 'fork', 'parent',
                 'license', 'homepage'}
PAPER_FIELDS = {'title', 'year', 'venue', 'arxiv_id', 'doi', 'semantic_scholar_id'}
HUGGINGFACE_FIELDS = {'repo_type', 'id', 'downloads', 'likes', 'last_modified'}
TIMESTAMP = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z')
IDENTITY = re.compile(r'(?:github:[1-9][0-9]{0,19}|huggingface:(?:model|dataset)/[A-Za-z0-9][A-Za-z0-9_.-]{0,95}/'
                      r'[A-Za-z0-9][A-Za-z0-9_.-]{0,95}|[a-z]{1,12}:\S{1,600})')
EVIDENCE_HOSTS = ('github.com', 'arxiv.org', 'export.arxiv.org', 'huggingface.co')
SOURCE_ID = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+){0,12}')
FULL_NAME = re.compile(r'[A-Za-z0-9_.-]{1,100}/[A-Za-z0-9_.-]{1,100}')


# --- identity -------------------------------------------------------------------------------------

GH_RESERVED = {
    'topics', 'features', 'marketplace', 'sponsors', 'orgs', 'settings', 'about', 'login', 'apps', 'collections',
    'trending', 'search', 'site', 'pricing', 'enterprise', 'explore', 'issues', 'pulls', 'notifications',
    'security', 'readme', 'contact', 'join', 'new', 'organizations', 'customer-stories', 'team', 'events',
    'github', 'resources', 'solutions', 'codespaces', 'copilot', 'mobile', 'stars', 'watching', 'users', 'advisories',
}
SOCIAL_HOSTS = (
    'twitter.com', 'x.com', 'mobile.twitter.com', 'linkedin.com', 'facebook.com', 'instagram.com', 'discord.gg',
    'discord.com', 'discordapp.com', 't.me', 'telegram.me', 'patreon.com', 'ko-fi.com', 'buymeacoffee.com',
    'paypal.me', 'paypal.com', 'twitch.tv', 'mastodon.social', 'infosec.exchange', 'bsky.app', 'weibo.com',
    'opencollective.com', 'liberapay.com', 'tiktok.com', 'threads.net', 'stackoverflow.com', 'ycombinator.com',
)
NOISE_HOSTS = (
    'shields.io', 'img.shields.io', 'awesome.re', 'creativecommons.org', 'opensource.org', 'choosealicense.com',
    'star-history.com', 'api.star-history.com', 'contrib.rocks', 'forthebadge.com', 'badge.fury.io',
    'travis-ci.org', 'travis-ci.com', 'circleci.com', 'codecov.io', 'gitter.im', 'goo.gl', 'bit.ly',
    'cdn.rawgit.com', 'raw.githubusercontent.com', 'user-images.githubusercontent.com', 'camo.githubusercontent.com',
    'avatars.githubusercontent.com', 'github-readme-stats.vercel.app', 'visitor-badge.laobi.icu', 'komarev.com',
    'en.wikipedia.org', 'wikipedia.org',
)
ARXIV_RE = re.compile(r'(?:arxiv\.org/(?:abs|pdf|html|format)/|arxiv:)\s*((?:\d{4}\.\d{4,5})|'
                      r'(?:[a-z\-]+(?:\.[A-Z]{2})?/\d{7}))(?:v\d+)?', re.I)
DOI_RE = re.compile(r'\b(10\.\d{4,9}/[^\s"<>]+)', re.I)


def clean_host(host):
    host = (host or '').lower().strip('.')
    if host.startswith('www.'):
        host = host[4:]
    if host.startswith('m.') and host[2:] in ('youtube.com', 'wikipedia.org'):
        host = host[2:]
    return host


def unwrap_archive(url):
    """A Wayback Machine link names the archived page; its identity is that page."""
    match = re.match(r'https?://web\.archive\.org/web/[0-9a-z_*]+/(.+)$', url, re.I)
    if match:
        inner = match.group(1)
        return (inner if re.match(r'https?://', inner) else 'http://' + inner), True
    return url, False


def arxiv_from(text):
    match = ARXIV_RE.search(text or '')
    return match.group(1).lower() if match else None


def doi_clean(doi):
    doi = unquote(doi).strip().rstrip('.,;)]}')
    doi = re.sub(r'(\.pdf|/full|/abstract|/epdf|/pdf)$', '', doi, flags=re.I)
    return doi.lower()


def norm_title(title):
    title = (title or '').lower()
    title = re.sub(r'[‘’“”"\'`]', '', title)
    title = re.sub(r'[^a-z0-9]+', ' ', title)
    return re.sub(r'\s+', ' ', title).strip()


def title_key(title):
    compact = norm_title(title).replace(' ', '')
    return 'title:' + compact if len(compact) >= 12 else None


def url_key(url):
    """(identity key, link type, flags) for a listed URL; the key is None for profiles, badges and site pages.

    Whitespace that a decoded path contains is written as %20, so a key is one token.
    """
    key, kind, flags = _url_key(url)
    return (re.sub(r'\s', '%20', key) if key else key), kind, flags


def _url_key(url):
    """(identity key, link type, flags) for a listed URL; the key is None for profiles, badges and site pages.

    Keys: gh:<owner>/<repo>, ghorg:<owner>, arxiv:<id>, doi:<doi>, ieee:<n>, openreview:<id>, yt:<video>,
    ytlist:<list>, gist:<id>, gl:/bb:/cb:/srht:/sf: for other code hosts, package and store keys, and url:<host><path>.
    """
    url = (url or '').strip().strip('<>').rstrip('.,;:')
    url, archived = unwrap_archive(url)
    try:
        parts_ = urlsplit(url)
        host = clean_host(parts_.hostname)
    except ValueError:
        return None, 'invalid', {'reason': 'invalid-url'}
    path = re.sub(r'/+', '/', unquote(parts_.path or '/'))
    parts = [part for part in path.split('/') if part]
    flags = {'archived_link': archived}
    if not host:
        return None, 'invalid', {'reason': 'no-host'}
    query = parse_qs(parts_.query)
    identifier = arxiv_from(url)
    if identifier and 'arxiv.org' in host:
        return 'arxiv:' + identifier, 'paper', flags
    if host in ('doi.org', 'dx.doi.org') and parts:
        return 'doi:' + doi_clean('/'.join(parts)), 'paper', flags
    if host in ('dl.acm.org', 'link.springer.com', 'onlinelibrary.wiley.com', 'tandfonline.com', 'journals.sagepub.com'):
        match = DOI_RE.search(path)
        if match:
            return 'doi:' + doi_clean(match.group(1)), 'paper', flags
    if host == 'ieeexplore.ieee.org':
        match = (re.search(r'/(?:document|abstract/document|stamp/stamp\.jsp)/?(\d+)', path + '?' + (parts_.query or ''))
                 or re.search(r'arnumber=(\d+)', parts_.query or ''))
        if match:
            return 'ieee:' + match.group(1), 'paper', flags
    if host == 'openreview.net' and query.get('id'):
        return 'openreview:' + query['id'][0], 'paper', flags
    if any(host == social or host.endswith('.' + social) for social in SOCIAL_HOSTS):
        if host in ('twitter.com', 'x.com', 'mobile.twitter.com') and len(parts) >= 3 and parts[1] == 'status':
            return 'x:' + parts[2], 'post', flags
        return None, 'social', {'reason': 'social-profile-or-community'}
    if any(host == noise or host.endswith('.' + noise) for noise in NOISE_HOSTS):
        return None, 'noise', {'reason': 'badge-license-or-reference-page'}
    if host in ('reddit.com', 'old.reddit.com'):
        if len(parts) >= 4 and parts[2] == 'comments':
            return 'reddit:' + parts[3], 'post', flags
        return None, 'social', {'reason': 'social-profile-or-community'}
    if host in ('youtube.com', 'youtu.be', 'youtube-nocookie.com'):
        if host == 'youtu.be' and parts:
            return 'yt:' + parts[0], 'video', flags
        if query.get('v'):
            return 'yt:' + query['v'][0], 'video', flags
        if parts and parts[0] == 'playlist' and query.get('list'):
            return 'ytlist:' + query['list'][0], 'video', flags
        if parts and parts[0] in ('embed', 'shorts', 'live') and len(parts) > 1:
            return 'yt:' + parts[1], 'video', flags
        return None, 'social', {'reason': 'video-channel-profile'}
    if host == 'github.com':
        if not parts or parts[0].lower() in GH_RESERVED:
            return None, 'noise', {'reason': 'github-site-page'}
        if len(parts) == 1:
            return 'ghorg:' + parts[0].lower(), 'org', flags
        owner, repo = parts[0], re.sub(r'\.git$', '', re.sub(r'https?:.*$', '', parts[1]))
        if owner.lower() == 'sponsors':
            return None, 'noise', {'reason': 'sponsor-page'}
        flags['gh_subpath'] = '/'.join(parts[2:])
        return f'gh:{owner.lower()}/{repo.lower()}', 'repo', flags
    if host == 'gist.github.com':
        if len(parts) >= 2:
            return 'gist:' + parts[1].lower(), 'gist', flags
        if len(parts) == 1 and re.fullmatch(r'[0-9a-f]{20,}', parts[0]):
            return 'gist:' + parts[0].lower(), 'gist', flags
        return None, 'profile', {'reason': 'gist-profile'}
    if host == 'gitlab.com' and len(parts) >= 2:
        end = parts.index('-') if '-' in parts else len(parts)
        return 'gl:' + re.sub(r'\.git$', '', '/'.join(parts[:end]).lower()), 'repo', flags
    if host in ('bitbucket.org', 'codeberg.org', 'git.sr.ht', 'sr.ht') and len(parts) >= 2:
        prefix = {'bitbucket.org': 'bb', 'codeberg.org': 'cb', 'git.sr.ht': 'srht', 'sr.ht': 'srht'}[host]
        return f'{prefix}:{parts[0].lower()}/{re.sub(r"[.]git$", "", parts[1].lower())}', 'repo', flags
    if host == 'sourceforge.net' and len(parts) >= 2 and parts[0] in ('projects', 'p'):
        return 'sf:' + parts[1].lower(), 'repo', flags
    if host.endswith('.sourceforge.net') or host.endswith('.sourceforge.io'):
        return 'sf:' + host.split('.')[0], 'repo', flags
    if host == 'pypi.org' and len(parts) >= 2 and parts[0] == 'project':
        return 'pypi:' + parts[1].lower().replace('_', '-'), 'package', flags
    if host == 'npmjs.com' and len(parts) >= 2 and parts[0] == 'package':
        return 'npm:' + '/'.join(parts[1:3] if parts[1].startswith('@') else parts[1:2]).lower(), 'package', flags
    if host == 'crates.io' and len(parts) >= 2 and parts[0] == 'crates':
        return 'crate:' + parts[1].lower(), 'package', flags
    if host == 'play.google.com' and query.get('id'):
        return 'gplay:' + query['id'][0].lower(), 'app', flags
    if host in ('chromewebstore.google.com', 'chrome.google.com'):
        return 'url:' + host + path.rstrip('/').lower(), 'web', flags
    if host == 'marketplace.visualstudio.com' and query.get('itemName'):
        return 'vsm:' + query['itemName'][0].lower(), 'package', flags
    if host == 'huggingface.co' and parts:
        if parts[0] == 'datasets' and len(parts) >= 3:
            return f'huggingface:dataset/{parts[1]}/{parts[2]}', 'dataset', flags
        if parts[0] not in ('datasets', 'spaces', 'papers', 'docs', 'blog', 'models') and len(parts) >= 2:
            return f'huggingface:model/{parts[0]}/{parts[1]}', 'model', flags
    if host.endswith('.github.io'):
        user = host[:-len('.github.io')]
        # Only project pages (user.github.io/<repo>[/page]) alias to a repository; user sites and posts do not.
        if parts and len(parts) <= 2 and not re.match(r'^(blog|posts?|articles?|writeups?|p|\d{4})$', parts[0], re.I):
            flags['ghpages_alias'] = f'gh:{user}/{parts[0].lower()}'
    trimmed = re.sub(r'/(index|default)\.(html?|php|aspx?)$', '/', path, flags=re.I).rstrip('/')
    if parts_.query and re.search(r'\.(php|aspx?|cgi|jsp|cfm|pl)$', path, re.I) and not query:
        return 'url:' + host + path.lower() + '?' + parts_.query.lower(), 'web', flags
    keep = ''
    for name in ('id', 'p', 'page_id', 'doi', 'v', 'arnumber', 'paper', 't'):
        if name in query:
            keep = f'?{name}={query[name][0]}'
            break
    return 'url:' + host + trimmed.lower() + keep, 'web', flags


def entry_name(label) -> str:
    """An entry name for telling apart the tools that one page lists: case-folded letters, marks and digits of any script."""
    import unicodedata
    text = unicodedata.normalize('NFKC', str(label or '')).casefold()
    return ''.join(character for character in text if unicodedata.category(character)[0] in 'LMN')


def shared_page_key(page_key: str, name: str) -> str:
    """The identity of one named entry of a shared page: the page key, shortened with a digest when long, '#', the name.

    The result stays within the 600-character identity limit.
    """
    page = page_key if len(page_key) <= 550 else page_key[:530] + '~' + hashlib.sha256(page_key.encode()).hexdigest()[:16]
    entry = name if len(name) <= 40 else name[:32] + '~' + hashlib.sha256(name.encode()).hexdigest()[:7]
    return f'{page}#{entry}'


def entry_key(identity: str, name: str) -> str | None:
    """The page entry a url: record stands for, whether it is keyed by the page alone or as page#name.

    A url: key never carries a fragment (url_key drops it), so '#' only marks an entry of a shared page.
    """
    if not identity or not identity.startswith('url:'):
        return None
    if '#' in identity:
        return 'entry:' + identity[4:]
    name = entry_name(name)
    return 'entry:' + shared_page_key(identity, name)[4:] if name else None


def lead_id(identity: str) -> str:
    return 'lead-' + hashlib.sha256(identity.encode('utf-8')).hexdigest()[:24]


def lead_keys(lead: dict) -> set[str]:
    return {lead['identity'], *lead['aliases']}


def match_keys(lead: dict) -> set[str]:
    """Every key that ties a lead to a record of any layer: its identity, aliases and the entry key of each page key.

    A GitHub project page (owner.github.io/<repo>) is also known by its repository's owner/name, so a page whose
    repository another layer already holds is not a new resource. An entry of a shared page is not.
    """
    keys = lead_keys(lead)
    found = keys | {entry_key(key, lead['name']) for key in keys if key.startswith('url:')}
    if lead['identity'].startswith('url:') and '#' not in lead['identity']:
        found.add(url_key(lead['url'])[2].get('ghpages_alias'))
    return found - {None}


# --- JSON format and time ---------------------------------------------------------------------------

def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def batch_bytes(batch: dict) -> bytes:
    """Repository JSON format: two-space indentation, literal non-ASCII text, trailing newline."""
    return (json.dumps(batch, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')


def parse_time(value) -> dt.datetime:
    if not isinstance(value, str) or not TIMESTAMP.fullmatch(value):
        raise ValueError('expected a UTC timestamp such as 2026-11-05T21:00:00Z')
    return dt.datetime.fromisoformat(value.replace('Z', '+00:00'))


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def batch_path(root: Path, batch_id: str, collected_at: str) -> Path:
    return Path(root) / DIRECTORY / collected_at[:7] / f'{batch_id}.json'


# --- record validation ------------------------------------------------------------------------------

def bounded_text(value, limit: int, *, empty: bool = False) -> bool:
    return (isinstance(value, str) and len(value) <= limit and (empty or value.strip() != '')
            and value == value.strip() and not re.search(r'[\x00-\x1f\x7f]', value))


def public_url(value, *, https_only: bool = False) -> bool:
    if not isinstance(value, str) or len(value) > 2000 or re.search(r'[\x00-\x20\x7f]', value):
        return False
    try:
        parts = urlsplit(value)
        port = parts.port
    except ValueError:
        return False
    schemes = ('https',) if https_only else ('http', 'https')
    return (parts.scheme in schemes and bool(parts.hostname) and parts.username is None and parts.password is None
            and port in (None, 80, 443))


def evidence_url(value) -> bool:
    if not public_url(value, https_only=True):
        return False
    parts = urlsplit(value)
    if parts.hostname not in EVIDENCE_HOSTS:
        return False
    if parts.hostname == 'github.com':
        # A list or registry pins the exact commit; a topic links its topic page.
        return bool(re.fullmatch(r'/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/(?:blob|tree)/[0-9a-f]{40}(?:/[^\s?#]*)?', parts.path)
                    or re.fullmatch(r'/topics/[a-z0-9][a-z0-9-]{0,49}', parts.path))
    return True


def privacy_findings(value) -> bool:
    """Credential-like values and personal paths (scripts/review_pr.py) or a protected name (privacy_guard.py)."""
    from review_pr import private_json_locations
    import discoveries
    return bool(private_json_locations(value)) or discoveries.protected_identifier(value)


def lead_problems(lead, *, privacy: bool = True) -> list[str]:
    """Schema problems for one lead; messages name fields, never upstream text."""
    if not isinstance(lead, dict):
        return ['lead must be an object']
    problems = []
    keys = set(lead)
    if not LEAD_FIELDS <= keys or keys - LEAD_FIELDS - OPTIONAL_LEAD_FIELDS:
        return ['lead has missing or unexpected fields']
    identity = lead['identity']
    if not isinstance(identity, str) or not IDENTITY.fullmatch(identity):
        problems.append('identity must be a typed key such as github:<numeric ID>')
    elif lead['id'] != lead_id(identity):
        problems.append('id must be derived from the identity')
    aliases = lead['aliases']
    if (not isinstance(aliases, list) or len(aliases) > 20 or aliases != sorted(set(aliases))
            or any(not isinstance(alias, str) or not IDENTITY.fullmatch(alias) or alias == identity for alias in aliases)):
        problems.append('aliases must be distinct sorted typed keys other than the identity')
    if not public_url(lead['url']):
        problems.append('url must be a public http(s) URL')
    if not bounded_text(lead['name'], 200):
        problems.append('name must be 1-200 characters of single-line text')
    if lead['kind_hint'] not in KINDS:
        problems.append('kind_hint must be a catalog kind')
    if lead['verification'] != VERIFICATION or lead['review_status'] != REVIEW_STATUS:
        problems.append('leads stay automated and unreviewed')
    try:
        parse_time(lead['observed_at'])
    except ValueError:
        problems.append('observed_at must be a UTC timestamp')
    listings = lead['listings']
    if not isinstance(listings, list) or not 0 < len(listings) <= MAX_LISTINGS:
        problems.append(f'listings must hold 1 to {MAX_LISTINGS} source listings')
    else:
        seen = set()
        for listing in listings:
            if (not isinstance(listing, dict) or set(listing) != LISTING_FIELDS
                    or not isinstance(listing['source_id'], str) or not SOURCE_ID.fullmatch(listing['source_id'])
                    or not bounded_text(listing['section'], 300, empty=True) or not bounded_text(listing['label'], 200, empty=True)
                    or not evidence_url(listing['evidence_url'])):
                problems.append('each listing needs a source ID, section, label and pinned evidence URL')
                break
            if listing['source_id'] in seen:
                problems.append('a source lists a lead once')
                break
            seen.add(listing['source_id'])
    has_github = identity.startswith('github:') if isinstance(identity, str) else False
    github = lead.get('github')
    if has_github != (github is not None):
        problems.append('a github: identity needs exactly the GitHub metadata snapshot')
    if github is not None:
        if (not isinstance(github, dict) or set(github) != GITHUB_FIELDS
                or type(github['id']) is not int or github['id'] <= 0 or identity != f"github:{github['id']}"
                or not isinstance(github['full_name'], str) or not FULL_NAME.fullmatch(github['full_name'])
                or not bounded_text(github['description'], 300, empty=True)
                or not isinstance(github['topics'], list) or len(github['topics']) > 30
                or any(not isinstance(topic, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,49}', topic) for topic in github['topics'])
                or type(github['stars']) is not int or github['stars'] < 0
                or type(github['archived']) is not bool or type(github['fork']) is not bool
                or not (github['parent'] is None or (isinstance(github['parent'], str) and FULL_NAME.fullmatch(github['parent'])))
                or not (github['license'] is None or bounded_text(github['license'], 64))
                or not (github['homepage'] is None or public_url(github['homepage']))
                or lead['url'].casefold() != f"https://github.com/{github['full_name']}".casefold()):
            problems.append('invalid GitHub metadata snapshot')
        else:
            try:
                if github['pushed_at'] is not None:
                    parse_time(github['pushed_at'])
            except ValueError:
                problems.append('GitHub pushed_at must be a UTC timestamp or null')
    paper = lead.get('paper')
    if paper is not None:
        if (not isinstance(paper, dict) or set(paper) != PAPER_FIELDS or not bounded_text(paper['title'], 400)
                or not (paper['year'] is None or (type(paper['year']) is int and 1950 <= paper['year'] <= 2100))
                or not (paper['venue'] is None or bounded_text(paper['venue'], 200))
                or not (paper['arxiv_id'] is None or (isinstance(paper['arxiv_id'], str) and ARXIV_RE.fullmatch('arxiv:' + paper['arxiv_id'])))
                or not (paper['doi'] is None or (isinstance(paper['doi'], str) and re.fullmatch(r'10\.\d{4,9}/\S{1,300}', paper['doi'])))
                or not (paper['semantic_scholar_id'] is None
                        or (isinstance(paper['semantic_scholar_id'], str) and re.fullmatch(r'[0-9a-f]{40}', paper['semantic_scholar_id'])))):
            problems.append('invalid paper metadata')
        elif lead['kind_hint'] != 'research':
            problems.append('a paper lead is research')
    hub = lead.get('huggingface')
    if (identity.startswith('huggingface:') if isinstance(identity, str) else False) != (hub is not None):
        problems.append('a huggingface: identity needs exactly the Hugging Face metadata snapshot')
    if hub is not None:
        if (not isinstance(hub, dict) or set(hub) != HUGGINGFACE_FIELDS or hub['repo_type'] not in ('model', 'dataset')
                or not isinstance(hub['id'], str) or identity != f"huggingface:{hub['repo_type']}/{hub['id']}"
                or any(type(hub[key]) is not int or hub[key] < 0 for key in ('downloads', 'likes'))):
            problems.append('invalid Hugging Face metadata snapshot')
        elif hub['last_modified'] is not None:
            try:
                parse_time(hub['last_modified'])
            except ValueError:
                problems.append('Hugging Face last_modified must be a UTC timestamp or null')
    if privacy and privacy_findings(lead):
        problems.append('lead contains a credential-like value, personal path or protected name')
    return problems


# --- batch validation -------------------------------------------------------------------------------

def validate_batch(batch, name: str, month: str | None = None, *, now: dt.datetime | None = None) -> list[str]:
    """Problems for one lead batch; record problems name the lead ID, never upstream text."""
    where = f'{DIRECTORY}/{month or "?"}/{name}.json'
    if not isinstance(batch, dict) or set(batch) != BATCH_FIELDS:
        return [f'{where}: expected exactly the lead batch fields']
    problems = []
    if type(batch['schema_version']) is not int or batch['schema_version'] != 1 or batch['kind'] != KIND:
        problems.append(f'{where}: unsupported batch schema or kind')
    if batch['batch_id'] != name:
        problems.append(f'{where}: batch_id must match the file name')
    if batch['review_status'] != REVIEW_STATUS:
        problems.append(f'{where}: lead batches stay unreviewed')
    now = now or dt.datetime.now(dt.timezone.utc)
    try:
        collected = parse_time(batch['collected_at'])
        if collected > now + dt.timedelta(minutes=10):
            problems.append(f'{where}: collected_at is in the future')
        if month is not None and batch['collected_at'][:7] != month:
            problems.append(f'{where}: a batch lives in the directory of its collection month')
    except ValueError:
        collected = None
        problems.append(f'{where}: collected_at must be a UTC timestamp')
    provenance = batch['provenance']
    match = BATCH_NAME.fullmatch(name)
    if (not isinstance(provenance, dict) or set(provenance) != PROVENANCE_FIELDS
            or provenance['repository'] != REPOSITORY or provenance['workflow_path'] != WORKFLOW_PATH
            or any(type(provenance[key]) is not int or provenance[key] <= 0 for key in ('run_id', 'run_attempt'))
            or provenance['event'] not in ('schedule', 'workflow_dispatch')
            or not re.fullmatch(r'[0-9a-f]{40}', str(provenance['head_sha']))
            or not re.fullmatch(r'[0-9a-f]{64}', str(provenance['registry_sha256']))):
        problems.append(f'{where}: invalid workflow run provenance')
    elif not match or (int(match[1]), int(match[2])) != (provenance['run_id'], provenance['run_attempt']):
        problems.append(f'{where}: file name must name the workflow run and attempt')
    sources = batch['sources']
    source_ids = set()
    if not isinstance(sources, list) or not 0 < len(sources) <= 200:
        problems.append(f'{where}: sources must list the followed sources of the run')
    else:
        for result in sources:
            if (not isinstance(result, dict) or set(result) != SOURCE_RESULT_FIELDS
                    or not isinstance(result['id'], str) or not SOURCE_ID.fullmatch(result['id']) or result['id'] in source_ids
                    or result['type'] not in SOURCE_TYPES or result['status'] not in SOURCE_STATUSES
                    or not (result['evidence_url'] is None or evidence_url(result['evidence_url']))
                    or not (result['revision'] is None or bounded_text(result['revision'], 100))
                    or not (result['content_sha256'] is None or re.fullmatch(r'[0-9a-f]{64}', str(result['content_sha256'])))
                    or (result['status'] == 'error') != (result['error'] is not None)
                    or not (result['error'] is None or re.fullmatch(r'[a-z]+(?:-[a-z]+){0,5}', str(result['error'])))
                    or any(type(result[key]) is not int or result[key] < 0 for key in ('links', 'in_scope'))):
                problems.append(f'{where}: invalid followed-source result')
                break
            source_ids.add(result['id'])
    leads = batch['leads']
    if not isinstance(leads, list) or not 0 < len(leads) <= MAX_BATCH_RECORDS:
        return problems + [f'{where}: a batch holds 1 to {MAX_BATCH_RECORDS} leads']
    identifiers, keys = [], set()
    for index, lead in enumerate(leads):
        label = lead.get('id') if isinstance(lead, dict) and isinstance(lead.get('id'), str) else f'lead {index}'
        label = label if re.fullmatch(r'lead-[0-9a-f]{24}', label) else f'lead {index}'
        for problem in lead_problems(lead):
            problems.append(f'{where}: {label}: {problem}')
        if not isinstance(lead, dict) or not isinstance(lead.get('identity'), str):
            continue
        identifiers.append(lead.get('id'))
        found = {lead['identity'], *(lead.get('aliases') or [])}
        if found & keys:
            problems.append(f'{where}: {label}: identity repeats another lead of this batch')
        keys |= found
        for listing in lead.get('listings') or []:
            if isinstance(listing, dict) and listing.get('source_id') not in source_ids:
                problems.append(f'{where}: {label}: listing names a source that the batch does not record')
                break
        try:
            if collected is not None and parse_time(lead['observed_at']) > collected:
                problems.append(f'{where}: {label}: lead is newer than its batch')
        except (ValueError, KeyError):
            pass
    selection = batch['selection']
    if not isinstance(selection, dict) or set(selection) != SELECTION_FIELDS:
        return problems + [f'{where}: expected exactly the selection fields']
    skipped = selection['skipped_counts']
    if (selection['policy'] != POLICY or selection['order'] != ORDER
            or type(selection['record_limit']) is not int or not 0 < selection['record_limit'] <= MAX_BATCH_RECORDS
            or len(leads) > selection['record_limit']
            or type(selection['selected_count']) is not int or selection['selected_count'] != len(leads)
            or type(selection['eligible_count']) is not int or selection['eligible_count'] < len(leads)
            or not isinstance(skipped, dict) or set(skipped) != set(SKIP_REASONS)
            or any(type(value) is not int or value < 0 for value in skipped.values())):
        problems.append(f'{where}: invalid selection policy, limit or counts')
    if selection['selected_ids'] != identifiers or len(set(identifiers)) != len(identifiers):
        problems.append(f'{where}: selected_ids must list the distinct lead IDs in order')
    if selection['record_sha256'] != {lead.get('id'): digest(lead) for lead in leads if isinstance(lead, dict)}:
        problems.append(f'{where}: record_sha256 must fingerprint every lead')
    return problems


def batch_files(root: Path = ROOT) -> list[tuple[str, Path]]:
    """(month, path) of every lead batch in run order; anything else in the directory is an error."""
    directory = Path(root) / DIRECTORY
    if not directory.exists():
        return []
    if not directory.is_dir() or directory.is_symlink():
        raise ValueError(f'{DIRECTORY} must be a directory')
    files, unexpected = [], []
    for month in directory.iterdir():
        if not MONTH_NAME.fullmatch(month.name) or not month.is_dir() or month.is_symlink():
            unexpected.append(month.name)
            continue
        for path in month.iterdir():
            match = BATCH_NAME.fullmatch(path.stem) if path.suffix == '.json' else None
            if not match or not path.is_file() or path.is_symlink():
                unexpected.append(f'{month.name}/{path.name}')
            else:
                files.append((int(match[1]), int(match[2]), month.name, path))
    if unexpected:
        raise ValueError(f'{DIRECTORY} contains unexpected entries: ' + ', '.join(sorted(unexpected)[:5]))
    return [(month, path) for _, _, month, path in sorted(files)]


def load_batches(root: Path = ROOT, *, now: dt.datetime | None = None) -> tuple[list[dict], list[str]]:
    """Read and validate every lead batch, plus the queue-wide identity rule and growth budget."""
    import strict_json
    problems, batches, total_bytes = [], [], 0
    try:
        paths = batch_files(root)
    except ValueError as error:
        return [], [str(error)]
    for month, path in paths:
        raw = path.read_bytes()
        total_bytes += len(raw)
        where = f'{DIRECTORY}/{month}/{path.name}'
        if len(raw) > MAX_BATCH_BYTES:
            problems.append(f'{where}: batch exceeds {MAX_BATCH_BYTES:,} bytes')
            continue
        try:
            batch = strict_json.loads(raw.decode('utf-8'))
        except (UnicodeError, ValueError):
            problems.append(f'{where}: expected strict UTF-8 JSON')
            continue
        found = validate_batch(batch, path.stem, month, now=now)
        if not found and raw != batch_bytes(batch):
            found.append(f'{where}: use the repository JSON format (two-space indent, trailing newline)')
        problems.extend(found)
        if not found:
            batches.append(batch)
    batches.sort(key=lambda batch: (parse_time(batch['collected_at']), batch['provenance']['run_id'],
                                    batch['provenance']['run_attempt']))
    seen = {}
    for batch in batches:
        for lead in batch['leads']:
            # A batch checks its own leads; an identity held by an earlier batch is a duplicate whatever its ID.
            earlier = next((seen[key] for key in sorted(match_keys(lead)) if key in seen), None)
            if earlier:
                problems.append(f"{DIRECTORY}/{batch['collected_at'][:7]}/{batch['batch_id']}.json: {lead['id']}: "
                                f'identity already belongs to {earlier[0]} in {earlier[1]}')
        for lead in batch['leads']:
            for key in match_keys(lead):
                seen.setdefault(key, (lead['id'], batch['batch_id']))
    total = sum(len(batch['leads']) for batch in batches)
    if total > MAX_TOTAL_RECORDS or total_bytes > MAX_TOTAL_BYTES:
        problems.append(f'{DIRECTORY}: {total:,} leads in {total_bytes:,} bytes exceed the lead budget '
                        f'({MAX_TOTAL_RECORDS:,} leads, {MAX_TOTAL_BYTES:,} bytes)')
    return batches, problems


# --- source registry --------------------------------------------------------------------------------

def compiled(pattern, where: str, problems: list[str]):
    if not isinstance(pattern, str) or not pattern or len(pattern) > 4000:
        problems.append(f'{where}: expected a regular expression')
        return None
    try:
        return re.compile(pattern, re.I)
    except re.error:
        problems.append(f'{where}: invalid regular expression')
        return None


SCOPE_FIELDS = {'include_sections', 'exclude_sections', 'include_subsections', 'keyword', 'default_kind', 'kind_rules',
                'exclude', 'exclusion_sets', 'require', 'exclude_text', 'include_types', 'type_field', 'exclude_fields', 'kind',
                'paper_screen'}
SOURCE_FIELDS = {
    'github-readme-list': ({'id', 'type', 'repository', 'path', 'why'}, {'scope', 'parser', 'every_hours'}),
    'github-topic': ({'id', 'type', 'topic', 'limit', 'why'}, {'scope', 'every_hours'}),
    'github-json-registry': ({'id', 'type', 'repository', 'path', 'url_field', 'name_field', 'why'},
                             {'items', 'scope', 'every_hours'}),
    'github-directory': ({'id', 'type', 'repository', 'path', 'url_pattern', 'label_pattern', 'why'}, {'scope', 'every_hours'}),
    'survey-references': ({'id', 'type', 'paper_id', 'why'}, {'scope', 'every_hours'}),
    'arxiv-query': ({'id', 'type', 'query', 'limit', 'why'}, {'scope', 'every_hours'}),
    'huggingface-search': ({'id', 'type', 'repo_type', 'search', 'limit', 'why'}, {'scope', 'every_hours'}),
}
PAPER_SCREENS = ('re-subject-v1',)


def exclusion_problems(rules, where: str, name) -> list[str]:
    problems = []
    if not isinstance(name, str) or not SOURCE_ID.fullmatch(name):
        problems.append(f'{where}: exclusion sets have slug names')
    if not isinstance(rules, list) or len(rules) > 400:
        return problems + [f'{where}: expected at most 400 rules']
    for rule in rules:
        if (not isinstance(rule, dict) or not {'pattern', 'reason'} <= set(rule) or set(rule) - {'pattern', 'reason', 'note'}
                or rule['reason'] not in EXCLUSION_REASONS or not bounded_text(rule.get('note', 'x'), 200)):
            return problems + [f'{where}: each rule has a pattern, a known reason and an optional note']
        compiled(rule['pattern'], where, problems)
    return problems


def exclusion_rules(registry: dict, source: dict) -> list[dict]:
    """A source's own exclusion rules followed by the shared sets it names."""
    scope = source.get('scope', {})
    return [*scope.get('exclude', []), *(rule for name in scope.get('exclusion_sets', []) for rule in registry['exclusion_sets'][name])]


def validate_registry(document, papers: list[dict] | None = None) -> list[str]:
    """Problems in data/discovery-sources.json: known source types, valid patterns and bounded limits."""
    where = REGISTRY
    if (not isinstance(document, dict) or set(document) != {'schema_version', 'kind', 'description', 'exclusion_sets', 'sources'}
            or document['schema_version'] != 1 or document['kind'] != REGISTRY_KIND
            or not bounded_text(document['description'], 2000) or not isinstance(document['exclusion_sets'], dict)):
        return [f'{where}: expected the source registry fields']
    problems = []
    for name, rules in document['exclusion_sets'].items():
        problems.extend(exclusion_problems(rules, f'{where}: exclusion_sets.{name}', name))
    sources = document['sources']
    if not isinstance(sources, list) or not 0 < len(sources) <= 150:
        return [f'{where}: sources must list 1 to 150 followed sources']
    seen = set()
    paper_ids = {paper.get('id'): paper for paper in papers or []}
    for index, source in enumerate(sources):
        label = f'{where}: sources[{index}]'
        if not isinstance(source, dict) or source.get('type') not in SOURCE_FIELDS:
            problems.append(f'{label}: unknown source type')
            continue
        required, optional = SOURCE_FIELDS[source['type']]
        if not required <= set(source) or set(source) - required - optional:
            problems.append(f'{label}: expected the {source["type"]} fields')
            continue
        if not isinstance(source['id'], str) or not SOURCE_ID.fullmatch(source['id']) or source['id'] in seen:
            problems.append(f'{label}: source IDs are distinct lowercase slugs')
        seen.add(source.get('id'))
        if not bounded_text(source['why'], 400):
            problems.append(f'{label}: why must say briefly why the source is followed')
        if 'repository' in source and (not isinstance(source['repository'], str) or not FULL_NAME.fullmatch(source['repository'])):
            problems.append(f'{label}: repository must be owner/name')
        if 'path' in source and (not isinstance(source['path'], str) or not re.fullmatch(r'[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*', source['path'])
                                 or any(part in ('.', '..') for part in source['path'].split('/'))):
            problems.append(f'{label}: path must be a relative repository path')
        if 'limit' in source and (type(source['limit']) is not int or not 0 < source['limit'] <= 1000):
            problems.append(f'{label}: limit must be 1 to 1000')
        if 'every_hours' in source and (type(source['every_hours']) is not int or source['every_hours'] not in (2, 6, 12, 24, 168)):
            problems.append(f'{label}: every_hours must be 2, 6, 12, 24 or 168')
        if source.get('parser') not in (None, 'markdown', 'pre-list'):
            problems.append(f'{label}: unknown parser')
        if source['type'] == 'github-topic' and (not isinstance(source['topic'], str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,49}', source['topic'])):
            problems.append(f'{label}: topic must be a GitHub topic name')
        if source['type'] == 'survey-references':
            paper = paper_ids.get(source['paper_id'])
            if papers is not None and (paper is None or not paper.get('arxiv_id')):
                problems.append(f'{label}: paper_id must name a curated paper with an arXiv ID')
        if source['type'] == 'huggingface-search' and (source['repo_type'] not in ('model', 'dataset')
                                                       or not bounded_text(source['search'], 60)):
            problems.append(f'{label}: Hugging Face searches name a repo type and a short term')
        if source['type'] == 'arxiv-query' and not bounded_text(source['query'], 1500):
            problems.append(f'{label}: query must be an arXiv API search_query')
        if source['type'] == 'github-json-registry':
            for key in ('items', 'url_field', 'name_field'):
                if key in source and (not isinstance(source[key], str) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,40}', source[key])):
                    problems.append(f'{label}: {key} must be a JSON field name')
        for key in ('url_pattern', 'label_pattern'):
            if key in source:
                pattern = compiled(source[key], f'{label}.{key}', problems)
                if pattern is not None and pattern.groups != 1:
                    problems.append(f'{label}.{key}: the pattern captures exactly one group')
        scope = source.get('scope', {})
        if not isinstance(scope, dict) or set(scope) - SCOPE_FIELDS:
            problems.append(f'{label}: unknown scope fields')
            continue
        for key in ('include_sections', 'exclude_sections', 'include_subsections', 'keyword', 'require', 'exclude_text'):
            if key in scope:
                compiled(scope[key], f'{label}.scope.{key}', problems)
        for key in ('default_kind', 'kind'):
            if key in scope and scope[key] not in KINDS:
                problems.append(f'{label}.scope.{key}: unknown kind')
        rules = scope.get('kind_rules', [])
        if not isinstance(rules, list) or any(not isinstance(rule, list) or len(rule) != 2 or rule[1] not in KINDS for rule in rules):
            problems.append(f'{label}.scope.kind_rules: expected [pattern, kind] pairs')
        else:
            for rule in rules:
                compiled(rule[0], f'{label}.scope.kind_rules', problems)
        problems.extend(exclusion_problems(scope.get('exclude', []), f'{label}.scope.exclude', source.get('id')))
        sets = scope.get('exclusion_sets', [])
        if not isinstance(sets, list) or any(name not in document['exclusion_sets'] for name in sets):
            problems.append(f'{label}.scope.exclusion_sets: name registered exclusion sets')
        if 'include_types' in scope and (not isinstance(scope['include_types'], list) or not scope['include_types']
                                         or any(not bounded_text(value, 40) for value in scope['include_types'])):
            problems.append(f'{label}.scope.include_types: expected registry type names')
        if 'type_field' in scope and (not isinstance(scope['type_field'], str) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,40}', scope['type_field'])):
            problems.append(f'{label}.scope.type_field: expected a JSON field name')
        if 'exclude_fields' in scope and (not isinstance(scope['exclude_fields'], list)
                                          or any(not isinstance(value, str) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,40}', value)
                                                 for value in scope['exclude_fields'])):
            problems.append(f'{label}.scope.exclude_fields: expected JSON field names')
        if 'paper_screen' in scope and scope['paper_screen'] not in PAPER_SCREENS:
            problems.append(f'{label}.scope.paper_screen: unknown screen')
    return problems


def registry_bytes(root: Path = ROOT) -> bytes:
    return (Path(root) / REGISTRY).read_bytes()


def load_registry(root: Path = ROOT) -> tuple[dict | None, list[str]]:
    """The validated source registry; a missing registry is a problem, since the lead workflow follows it."""
    import strict_json
    path = Path(root) / REGISTRY
    if not path.is_file():
        return None, [f'{REGISTRY}: the source registry that {WORKFLOW_PATH} follows is missing']
    try:
        document = strict_json.loads(path.read_text(encoding='utf-8'))
        papers = strict_json.load_path(Path(root) / 'data/papers.json')
    except (OSError, UnicodeError, ValueError):
        return None, [f'{REGISTRY}: expected strict UTF-8 JSON']
    problems = validate_registry(document, papers)
    if not problems and path.read_bytes() != (json.dumps(document, ensure_ascii=False, indent=2) + '\n').encode('utf-8'):
        problems.append(f'{REGISTRY}: use the repository JSON format (two-space indent, trailing newline)')
    return (None if problems else document), problems


# --- what the repository already holds --------------------------------------------------------------

def existing_keys(root: Path = ROOT, batches: list[dict] | None = None) -> dict:
    """Every identity key the repository's layers already hold, with the layer that holds it.

    Curated resources and papers, the reviewed source index and its failures, public supplements, README-scan
    discovery batches, scope exclusions, case-coverage leads and earlier lead batches. GitHub repositories are
    known both by numeric ID (github:<id>) and by name (gh:<owner>/<repo>).
    """
    import strict_json
    root = Path(root)
    known: dict[str, str] = {}

    def add(key, reason):
        if key:
            known.setdefault(key, reason)

    def add_url(url, reason):
        key, _, flags = url_key(url)
        add(key, reason)
        add(flags.get('ghpages_alias'), reason)

    for name in ('data/tool-resources.json', 'data/rea-resources.json'):
        for record in strict_json.load_path(root / name):
            add_url(str(record.get('url', '')), 'already-curated')
            # A curated page that lists several tools is also known as the entry with the record's own name.
            add(entry_key(url_key(str(record.get('url', '')))[0], record.get('name')), 'already-curated')
    for paper in strict_json.load_path(root / 'data/papers.json'):
        if paper.get('arxiv_id'):
            add('arxiv:' + str(paper['arxiv_id']).lower(), 'already-curated')
        if paper.get('doi'):
            add('doi:' + doi_clean(str(paper['doi'])), 'already-curated')
        for url in (paper.get('url'), paper.get('pdf_url')):
            if url:
                key, kind, _ = url_key(url)
                if kind == 'paper' or url == paper.get('url'):
                    add(key, 'already-curated')
        add(title_key(paper.get('title')), 'already-curated')

    def add_scan(row, reason):
        identifier = str(row.get('id', ''))
        if re.fullmatch(r'scan-[1-9][0-9]*', identifier):
            add('github:' + identifier[5:], reason)
        if isinstance(row.get('full_name'), str):
            add('gh:' + row['full_name'].lower(), reason)

    index = strict_json.load_path(root / 'data/source-index.json')
    for row in [*index.get('resources', []), *index.get('failures', [])]:
        add_scan(row, 'already-indexed')
    registry = root / 'data/source-supplements/index.json'
    if registry.is_file():
        for name in strict_json.load_path(registry)['batches']:
            for row in strict_json.load_path(root / 'data/source-supplements' / f'{name}.json')['resources']:
                add_scan(row, 'already-indexed')
    import discoveries
    scan_batches, problems = discoveries.load_batches(root)
    if problems:
        raise ValueError('README-scan discovery batches are invalid: ' + '; '.join(problems[:3]))
    for batch in scan_batches:
        for row in batch['resources']:
            add_scan(row, 'already-discovered')
    for name in ('data/source-scope.json',):
        path = root / name
        if path.is_file():
            for identifier in strict_json.load_path(path):
                if re.fullmatch(r'scan-[1-9][0-9]*', identifier):
                    add('github:' + identifier[5:], 'scope-excluded')
    coverage = root / 'data/case-coverage.json'
    if coverage.is_file():
        for entry in strict_json.load_path(coverage).get('entries', []):
            title = str(entry.get('title') or '')
            for url in [*entry.get('reported_source_urls', []), *entry.get('primary_evidence_urls', [])]:
                add_url(str(url), 'case-lead')
                # On a page that a list splits into named entries, the case is the entry named by its title's lead.
                page = url_key(str(url))[0]
                add(entry_key(page, title.split(':', 1)[0]), 'case-lead')
                add(entry_key(page, title), 'case-lead')
    if batches is None:
        batches, problems = load_batches(root)
        if problems:
            raise ValueError('Existing lead batches are invalid: ' + '; '.join(problems[:3]))
    for batch in batches:
        for lead in batch['leads']:
            for key in match_keys(lead):
                add(key, 'already-lead')
    return {'known': known, 'records': sum(len(batch['leads']) for batch in batches),
            'bytes': sum(len(batch_bytes(batch)) for batch in batches)}


# --- selection --------------------------------------------------------------------------------------

def round_robin(candidates: list[dict], source_order: list[str]) -> list[dict]:
    """Interleave candidates by their first listing source, in registry order, keeping each source's order."""
    queues: dict[str, list[dict]] = {}
    for candidate in candidates:
        queues.setdefault(candidate['listings'][0]['source_id'], []).append(candidate)
    order = [source for source in source_order if source in queues] + sorted(set(queues) - set(source_order))
    result = []
    while any(queues.get(source) for source in order):
        for source in order:
            if queues.get(source):
                result.append(queues[source].pop(0))
    return result


def select_leads(candidates: list[dict], existing: dict, limit: int, source_order: list[str]) -> tuple[list[dict], int, Counter]:
    """Choose up to ``limit`` new leads; return them, the eligible count and the skip counts."""
    skipped = Counter({reason: 0 for reason in SKIP_REASONS})
    known = existing['known']
    selected, taken, eligible = [], set(), 0
    for lead in round_robin(candidates, source_order):
        keys = match_keys(lead)
        reasons = [known[key] for key in sorted(keys) if key in known]
        if reasons:
            skipped[min(reasons, key=SKIP_REASONS.index)] += 1
            continue
        if keys & taken:
            continue  # the same resource reached the candidates twice; the first stays
        if privacy_findings(lead):
            skipped['privacy'] += 1
            continue
        problems = lead_problems(lead, privacy=False)
        if problems:
            # Upstream metadata the collector could not normalize; counted and logged, never published.
            print(f"Skipped lead {lead.get('id')}: {problems[0]}", file=sys.stderr)
            skipped['invalid'] += 1
            continue
        eligible += 1
        if len(selected) >= limit:
            skipped['over-limit'] += 1
            continue
        selected.append(lead)
        taken |= keys
    return selected, eligible, skipped


def build_batch(candidates: list[dict], sources: list[dict], provenance: dict, existing: dict, *, collected_at: str,
                source_order: list[str], unavailable: int = 0) -> tuple[dict | None, str]:
    """Return (batch, status) for one run's candidates; status explains an empty result."""
    remaining = MAX_TOTAL_RECORDS - existing['records']
    if remaining <= 0 or existing['bytes'] >= MAX_TOTAL_BYTES:
        return None, 'budget-reached'
    limit = min(MAX_BATCH_RECORDS, remaining)
    selected, eligible, skipped = select_leads(candidates, existing, limit, source_order)
    skipped['unavailable'] += unavailable
    while selected:
        batch = {
            'schema_version': 1, 'kind': KIND,
            'batch_id': f"leads-{provenance['run_id']}-{provenance['run_attempt']}",
            'review_status': REVIEW_STATUS, 'collected_at': collected_at, 'provenance': provenance,
            'selection': {
                'policy': POLICY, 'order': ORDER, 'record_limit': limit, 'eligible_count': eligible,
                'selected_count': len(selected), 'selected_ids': [lead['id'] for lead in selected],
                'record_sha256': {lead['id']: digest(lead) for lead in selected},
                'skipped_counts': {reason: skipped[reason] for reason in SKIP_REASONS},
            },
            'sources': sources, 'leads': selected,
        }
        size = len(batch_bytes(batch))
        if size <= MAX_BATCH_BYTES and existing['bytes'] + size <= MAX_TOTAL_BYTES:
            return batch, 'selected'
        # Shrink to the byte budget; the dropped leads stay eligible for a later run.
        drop = max(1, len(selected) // 10)
        skipped['over-limit'] += drop
        selected = selected[:-drop]
    return None, 'nothing-new' if not eligible else 'budget-reached'


def summary(root: Path = ROOT) -> dict:
    batches, problems = load_batches(root)
    _, registry_problems = load_registry(root)
    leads = sum(len(batch['leads']) for batch in batches)
    size = sum(path.stat().st_size for _, path in batch_files(root)) if not problems else 0
    latest = batches[-1] if batches else None
    return {'batches': len(batches), 'leads': leads, 'bytes': size, 'problems': registry_problems + problems,
            'record_budget': MAX_TOTAL_RECORDS, 'byte_budget': MAX_TOTAL_BYTES,
            'last_successful_collection_at': latest['collected_at'] if latest else None,
            'last_batch_id': latest['batch_id'] if latest else None}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--json', action='store_true', help='print the summary as JSON')
    args = parser.parse_args()
    report = summary(ROOT)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for problem in report['problems']:
            print(f'- {problem}', file=sys.stderr)
        print(f"Lead queue: {report['leads']:,} unreviewed followed-source leads in {report['batches']} batch(es), "
              f"{report['bytes']:,} bytes (budget {MAX_TOTAL_RECORDS:,} leads, {MAX_TOTAL_BYTES:,} bytes); "
              f"last collection {report['last_successful_collection_at'] or 'none'}.")
    return 1 if report['problems'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
