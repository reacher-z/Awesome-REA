#!/usr/bin/env python3
"""Validate the separate, source-reviewed research-paper catalog without network access."""
import argparse
import datetime as dt
import json
from pathlib import Path
import re
import sys
from urllib.parse import parse_qsl, unquote, urlsplit

from review_dates import review_date_is_future


ROOT = Path(__file__).resolve().parents[1]
STATUSES = {'conference-paper', 'conference-accepted', 'journal-article', 'preprint'}
TARGETS = {'website', 'game', 'app', 'binary', 'firmware', 'protocol'}
TEXT_FIELDS = {
    'id', 'title', 'title_zh', 'date_precision', 'date_basis', 'date_basis_zh',
    'venue', 'publication_status', 'url', 'pdf_url', 'description_en',
    'description_zh', 'scope_limitations_en', 'scope_limitations_zh',
    'why_fits_en', 'why_fits_zh', 'metadata_notes', 'metadata_notes_zh',
    'kind', 'verified_at', 'verification',
}
FIELDS = TEXT_FIELDS | {
    'authors', 'year', 'publication_date', 'arxiv_id', 'arxiv_version_reviewed',
    'first_arxiv_date', 'doi', 'code_url', 'project_url', 'targets',
    'evidence_urls', 'runtime_tested',
}
# Optional publisher container metadata for published papers; omitted when unverified.
OPTIONAL_FIELDS = {'citation'}
CITATION_PATTERNS = {
    'container_title': None, 'publisher': None, 'series': None,
    'volume': re.compile(r'[1-9]\d*'), 'issue': re.compile(r'[A-Za-z0-9]+'),
    'pages': re.compile(r'([1-9]\d*)(?:-([1-9]\d*))?'), 'article_number': re.compile(r'[A-Za-z0-9]+'),
}
ARXIV_ID = re.compile(r'\d{4}\.\d{4,5}')
ARXIV_URL_PATH = re.compile(r'/(?:abs|pdf|html)/(\d{4}\.\d{4,5})(v[1-9]\d*)?(?:\.pdf)?')
DOI_RESOLVERS = {'doi.org', 'dx.doi.org', 'www.doi.org'}


def read_papers(root=ROOT):
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Paper catalog contains a duplicate JSON key')
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError('Paper catalog contains a non-JSON numeric constant')

    return json.loads((Path(root) / 'data/papers.json').read_text(encoding='utf-8'),
                      object_pairs_hook=unique_object, parse_constant=invalid_constant)


def canonical_paper_url(value):
    parsed = urlsplit(value)
    host, path = parsed.netloc.casefold(), parsed.path.rstrip('/')
    if host in {'doi.org', 'dx.doi.org'}:
        host, path = 'doi.org', path.casefold()
    elif host in {'arxiv.org', 'www.arxiv.org'}:
        match = re.fullmatch(r'/(?:abs|pdf|html)/(\d{4}\.\d{4,5})(?:v\d+)?(?:\.pdf)?', path)
        if match:
            host, path = 'arxiv.org', '/abs/' + match[1]
    elif host == 'aclanthology.org':
        path = path.removesuffix('.pdf')
    elif host in {'openreview.net', 'www.openreview.net'}:
        # OpenReview identifies a paper by its id query parameter rather than its path.
        host, path = 'openreview.net', f"{path}?id={dict(parse_qsl(parsed.query)).get('id', '')}"
    return parsed.scheme.casefold(), host, path


def url_identifier_error(record, field):
    """Offline check that an arXiv or DOI-resolver `url`/`pdf_url` names this record's identifiers.

    Publisher landing pages and other hosts are not interpreted. Code, project and evidence links
    can name software or dataset DOIs, so they are never compared with the paper DOI.
    """
    parsed = urlsplit(record[field])
    host = (parsed.hostname or '').casefold()
    arxiv, doi = record.get('arxiv_id'), record.get('doi')
    if host in {'arxiv.org', 'www.arxiv.org'}:
        match = ARXIV_URL_PATH.fullmatch(parsed.path.rstrip('/'))
        if not match:
            return None
        named, version = match.groups()
        reviewed = record.get('arxiv_version_reviewed')
        if named != arxiv:
            return f'{field}: links arXiv {named}, but arxiv_id is {arxiv!r}'
        # An unversioned link follows the latest version; a versioned one must be the reviewed version.
        if version and isinstance(reviewed, str) and version != reviewed:
            return f'{field}: links arXiv {named}{version}, but arxiv_version_reviewed is {reviewed}'
    elif host in DOI_RESOLVERS:
        named = unquote(parsed.path).strip('/')
        # arXiv registers 10.48550/arXiv.<arxiv_id> for every paper, recorded in `doi` or not.
        arxiv_doi = re.fullmatch(r'10\.48550/arxiv\.(\d{4}\.\d{4,5})', named, re.IGNORECASE)
        if named.casefold() != str(doi).casefold() and not (arxiv_doi and arxiv_doi[1] == arxiv):
            return f'{field}: resolves DOI {named}, but doi is {doi!r}'
    return None


def has_reviewed_publisher_identity(record, evidence):
    """Recognize reviewed USENIX Security and WOOT proceedings URL/PDF profiles.

    This checks a source-review contract, not publication authenticity. Additional
    publisher profiles require review; a software-artifact DOI is not a paper ID.
    WOOT 19 final PDFs use a reviewed underscore form outside conference/woot19/;
    suffixed copies such as woot19-paper_oflynn_0.pdf need their own exact review.
    USENIX Security 2024 final PDFs use a reviewed usenixsecurity24- prefix; other
    years keep the secYY- form until their naming is reviewed separately.
    """
    if record.get('publication_status') != 'conference-paper':
        return False
    landing, pdf = record.get('url'), record.get('pdf_url')
    if not isinstance(landing, str) or not isinstance(pdf, str):
        return False
    match = re.fullmatch(
        r'https://www\.usenix\.org/conference/(usenixsecurity|woot)([0-9]{2})/'
        r'presentation/([a-z0-9]+(?:-[a-z0-9]+)*)', landing)
    if not match or type(record.get('year')) is not int:
        return False
    series, year, presenter = match.groups()
    if series == 'usenixsecurity' and year == '24':
        expected_pdf = f'https://www.usenix.org/system/files/usenixsecurity24-{presenter}.pdf'
    elif series == 'usenixsecurity':
        expected_pdf = f'https://www.usenix.org/system/files/sec{year}-{presenter}.pdf'
    elif year == '19':
        expected_pdf = f'https://www.usenix.org/system/files/woot19-paper_{presenter}.pdf'
    else:
        expected_pdf = f'https://www.usenix.org/system/files/conference/woot{year}/woot{year}-paper-{presenter}.pdf'
    return (record['year'] == 2000 + int(year)
            and pdf == expected_pdf
            and landing in evidence and pdf in evidence)


def validate_papers(records, errors, *, url_check, now=None):
    """Use the caller's public-HTTPS checker so importing this module cannot cycle."""
    if not isinstance(records, list) or not records:
        errors.append('Paper catalog must be a nonempty array.')
        return
    now = dt.datetime.now(dt.timezone.utc) if now is None else now.astimezone(dt.timezone.utc)
    today = now.date()
    seen = {field: set() for field in ('id', 'url', 'arxiv_id', 'doi')}
    for index, record in enumerate(records):
        where = f'paper[{index}]'
        if not isinstance(record, dict):
            errors.append(f'{where}: must be an object')
            continue
        if isinstance(record.get('id'), str) and record['id'].strip():
            where = f"paper {record['id']!r}"
        missing, unknown = FIELDS - record.keys(), record.keys() - FIELDS - OPTIONAL_FIELDS
        if missing:
            errors.append(f"{where}: missing fields {', '.join(sorted(missing))}")
        if unknown:
            errors.append(f"{where}: unknown fields {', '.join(sorted(unknown))}")
        for field in TEXT_FIELDS:
            value = record.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f'{where}.{field}: must be a nonempty string')
        identifier = record.get('id')
        if not isinstance(identifier, str) or not re.fullmatch(r'paper-[a-z0-9]+(?:-[a-z0-9]+)*', identifier):
            errors.append(f'{where}.id: use a paper-prefixed lowercase slug')
        elif identifier in seen['id']:
            errors.append(f'{where}: duplicate paper ID')
        else:
            seen['id'].add(identifier)
        authors = record.get('authors')
        if (not isinstance(authors, list) or not authors
                or any(not isinstance(author, str) or not author.strip() for author in authors)):
            errors.append(f'{where}.authors: use a nonempty author-name array')
        elif len({author.strip().casefold() for author in authors}) != len(authors):
            errors.append(f'{where}.authors: contains duplicate names')
        targets = record.get('targets')
        if (not isinstance(targets, list) or not targets
                or any(not isinstance(target, str) or target not in TARGETS for target in targets)
                or len(set(targets)) != len(targets)):
            errors.append(f'{where}.targets: use unique supported target labels')
        status = record.get('publication_status')
        if not isinstance(status, str) or status not in STATUSES:
            errors.append(f'{where}.publication_status: unknown publication status')
        if record.get('kind') != 'research' or record.get('verification') != 'source-reviewed':
            errors.append(f'{where}: preserve research/source-reviewed labels')
        if record.get('runtime_tested') is not False:
            errors.append(f'{where}.runtime_tested: this catalog records source review, not reproduced experiments')
        for english, chinese in (
                ('title', 'title_zh'), ('date_basis', 'date_basis_zh'),
                ('description_en', 'description_zh'), ('scope_limitations_en', 'scope_limitations_zh'),
                ('why_fits_en', 'why_fits_zh'), ('metadata_notes', 'metadata_notes_zh')):
            en, zh = record.get(english), record.get(chinese)
            if isinstance(zh, str) and not re.search(r'[\u3400-\u9fff]', zh):
                errors.append(f'{where}.{chinese}: needs Chinese text')
            if isinstance(en, str) and (not re.search(r'[A-Za-z]', en) or en == zh):
                errors.append(f'{where}.{english}: needs distinct English text')

        year, precision, published = record.get('year'), record.get('date_precision'), record.get('publication_date')
        if type(year) is not int or not 1900 <= year <= today.year:
            errors.append(f'{where}.year: use a plausible, non-future publication year')
        try:
            if precision == 'year':
                if published is not None:
                    raise ValueError
            else:
                pattern = r'\d{4}-\d{2}' if precision == 'month' else r'\d{4}-\d{2}-\d{2}'
                if not isinstance(precision, str) or precision not in {'month', 'day'} or not isinstance(published, str) or not re.fullmatch(pattern, published):
                    raise ValueError
                date = dt.date.fromisoformat(published + '-01' if precision == 'month' else published)
                if date.year != year or date > today:
                    raise ValueError
        except ValueError:
            errors.append(f'{where}.publication_date: must match its precision/year and not be in the future')
        for field in ('verified_at', 'first_arxiv_date'):
            value = record.get(field)
            if field == 'first_arxiv_date' and value is None:
                continue
            try:
                if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
                    raise ValueError
                reviewed = dt.date.fromisoformat(value)
                future = (review_date_is_future(reviewed, now) if field == 'verified_at'
                          else reviewed > today)
                if future:
                    raise ValueError
            except ValueError:
                expectation = ('an ISO calendar date no more than one day ahead of UTC'
                               if field == 'verified_at' else 'a non-future ISO calendar date')
                errors.append(f'{where}.{field}: use {expectation}')

        arxiv, doi, version = record.get('arxiv_id'), record.get('doi'), record.get('arxiv_version_reviewed')
        for field, value, pattern in (('arxiv_id', arxiv, ARXIV_ID), ('doi', doi, re.compile(r'10\.\d{4,9}/\S+'))):
            if value is None:
                continue
            if not isinstance(value, str) or not pattern.fullmatch(value):
                errors.append(f'{where}.{field}: invalid identifier')
                continue
            key = value.casefold()
            if key in seen[field]:
                errors.append(f'{where}: duplicate {field}')
            seen[field].add(key)
            if field == 'arxiv_id':
                paper_month = (2000 + int(value[:2]), int(value[2:4]))
                if not 1 <= paper_month[1] <= 12 or paper_month > (today.year, today.month):
                    errors.append(f'{where}.arxiv_id: invalid or future submission month')
        if version is not None and (not isinstance(version, str) or not re.fullmatch(r'v[1-9]\d*', version)):
            errors.append(f'{where}.arxiv_version_reviewed: use v followed by a positive integer or null')
        if arxiv is None and (version is not None or record.get('first_arxiv_date') is not None):
            errors.append(f'{where}: arXiv-specific metadata requires an arXiv ID')

        evidence = record.get('evidence_urls')
        if (not isinstance(evidence, list) or not evidence
                or any(not isinstance(url, str) or not url.strip() for url in evidence)):
            errors.append(f'{where}.evidence_urls: use a nonempty URL array')
            evidence = []
        if arxiv is None and doi is None and not has_reviewed_publisher_identity(record, evidence):
            errors.append(f'{where}: provide a verified arXiv ID or DOI, or a reviewed published-paper URL/PDF identity')
        for field in ('url', 'pdf_url', 'code_url', 'project_url'):
            value = record.get(field)
            if field in {'code_url', 'project_url'} and value is None:
                continue
            problem = url_check(value)
            if problem:
                errors.append(f'{where}.{field}: {problem}')
                continue
            mismatch = url_identifier_error(record, field) if field in {'url', 'pdf_url'} else None
            if mismatch:
                errors.append(f'{where}.{mismatch}')
            if field == 'url':
                key = canonical_paper_url(value)
                if key in seen['url']:
                    errors.append(f'{where}: duplicate canonical paper URL')
                seen['url'].add(key)
        for url in evidence:
            problem = url_check(url)
            if problem:
                errors.append(f'{where}.evidence_urls: {problem}')
        if 'citation' in record:
            validate_citation(record, evidence, where, errors)


def validate_citation(record, evidence, where, errors):
    """Container fields are verbatim publisher metadata from cited evidence, never inferred."""
    citation = record['citation']
    if not isinstance(citation, dict) or not citation:
        errors.append(f'{where}.citation: use a nonempty object, or omit unverified container metadata')
        return
    if record.get('publication_status') not in {'conference-paper', 'journal-article'}:
        errors.append(f'{where}.citation: container metadata applies only to published papers')
    if not {'container_title', 'sources'} <= set(citation) or set(citation) - set(CITATION_PATTERNS) - {'sources'}:
        errors.append(f'{where}.citation: needs container_title and sources, and only supported fields')
    for field, pattern in CITATION_PATTERNS.items():
        if field not in citation:
            continue
        value = citation[field]
        if not isinstance(value, str) or not value.strip() or value != value.strip() or (pattern and not pattern.fullmatch(value)):
            errors.append(f'{where}.citation.{field}: invalid value')
        elif field == 'pages':
            first, last = pattern.fullmatch(value).groups()
            if last is not None and int(last) < int(first):
                errors.append(f'{where}.citation.pages: last page precedes the first')
    if 'issue' in citation and 'volume' not in citation:
        errors.append(f'{where}.citation: an issue requires its volume')
    sources, reviewed = citation.get('sources'), {*evidence, record.get('url'), record.get('pdf_url')}
    if (not isinstance(sources, list) or not sources or len(set(map(str, sources))) != len(sources)
            or any(source not in reviewed for source in sources)):
        errors.append(f'{where}.citation.sources: cite the reviewed paper, PDF or evidence URLs that state these values')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    # Lazy import is only for standalone use. validate.py passes its checker.
    from validate import public_https_error
    errors = []
    try:
        records = read_papers()
    except (OSError, ValueError):
        print('Paper catalog could not be read as strict JSON.', file=sys.stderr)
        return 1
    validate_papers(records, errors, url_check=public_https_error)
    if errors:
        for error in errors:
            print('- ' + error, file=sys.stderr)
        return 1
    print(f'Validated {len(records)} source-reviewed research papers.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
