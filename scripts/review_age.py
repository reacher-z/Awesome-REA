#!/usr/bin/env python3
"""List curated resources and papers by the age of their last source review, as of a chosen date.

An offline planning aid for rechecks. Age is the number of days since a record's
`verified_at` source review; it does not mean a record is wrong or a project is
unmaintained. The report reads the catalogs only: it never edits or removes a
record, and it never changes a paper's publication status. Automated README scan
observation times are summarized separately and never count as source reviews.
"""
import argparse
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOGS = (('resource', 'data/rea-resources.json'), ('resource', 'data/tool-resources.json'), ('paper', 'data/papers.json'))
SOURCE_INDEX = 'data/source-index.json'
DEFAULT_BANDS = (30, 90, 180, 365)
RECORD_TYPES = ('resource', 'paper')
POLICY = ('Recheck planning queue keyed by stable IDs. Age is days from the last recorded source review (verified_at) to the '
          'as-of date; it is not evidence that a description is outdated or that a project is abandoned. Nothing is deleted, '
          'edited or relabeled, and publication status is unchanged. Automated README scan observations (observed_at) are '
          'counted separately and are not source reviews.')


def utc_date(value):
    """Return the UTC calendar date of an ISO date or timezone-aware timestamp."""
    if len(value) == 10:
        return dt.date.fromisoformat(value)
    parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('timestamps must include a timezone')
    return parsed.astimezone(dt.timezone.utc).date()


def band_labels(bands):
    """Name the half-open day ranges [0, b1), [b1, b2), ... and the open-ended last range."""
    edges = (0, *bands)
    labels = [f'{low}-{high - 1} days' for low, high in zip(edges, bands)]
    return labels + [f'{bands[-1]}+ days']


def band_of(age, bands, labels):
    for edge, label in zip(bands, labels):
        if age < edge:
            return label
    return labels[-1]


def review_queue(catalogs, scans, as_of, bands=DEFAULT_BANDS):
    """Build the report from (record type, catalog path, records) triples and scan records; inputs are only read."""
    labels = band_labels(bands)
    counts = {kind: dict.fromkeys(labels, 0) for kind in RECORD_TYPES}
    entries, ahead = [], []
    for kind, catalog, records in catalogs:
        for record in records:
            reviewed = utc_date(record['verified_at'])
            # A paper's evidence list starts with its canonical page; resources name one primary source.
            evidence = record['evidence_urls'][0] if kind == 'paper' else record['evidence_url']
            entry = {'id': record['id'], 'record_type': kind, 'catalog': catalog, 'verified_at': record['verified_at'],
                     'review_date': reviewed.isoformat(), 'age_days': (as_of - reviewed).days, 'evidence_url': evidence}
            if entry['age_days'] < 0:
                # Reviewed after the as-of date, for example when reporting on an earlier date.
                ahead.append(entry)
                continue
            entry['band'] = band_of(entry['age_days'], bands, labels)
            counts[kind][entry['band']] += 1
            entries.append(entry)
    entries.sort(key=lambda entry: (-entry['age_days'], entry['record_type'], entry['id']))
    observed = [utc_date(record['observed_at']) for record in scans]
    scan_counts = dict.fromkeys(labels, 0)
    for day in observed:
        if day <= as_of:
            scan_counts[band_of((as_of - day).days, bands, labels)] += 1
    return {
        'report': 'source-review-age', 'policy': POLICY, 'as_of': as_of.isoformat(), 'bands': labels,
        'counts': counts, 'records': entries,
        'reviewed_after_as_of': sorted(ahead, key=lambda entry: (entry['record_type'], entry['id'])),
        'automated_readme_scans': {
            'date_field': 'observed_at', 'records': len(observed), 'counts': scan_counts,
            'observed_after_as_of': sum(day > as_of for day in observed),
            'earliest': min(observed).isoformat() if observed else None,
            'latest': max(observed).isoformat() if observed else None,
            'note': 'README retrieval times of the automated index, not source reviews; they are not in the queue.',
        },
    }


def read_catalogs(root=ROOT):
    catalogs = [(kind, path, json.loads((root / path).read_text(encoding='utf-8'))) for kind, path in CATALOGS]
    scans = json.loads((root / SOURCE_INDEX).read_text(encoding='utf-8'))['resources']
    return catalogs, scans


def text_lines(report, record_type=None, min_age=0):
    counts, ahead = report['counts'], report['reviewed_after_as_of']
    totals = {kind: sum(counts[kind].values()) + sum(entry['record_type'] == kind for entry in ahead) for kind in RECORD_TYPES}
    yield f'Source-review age as of {report["as_of"]} UTC for {totals["resource"]} curated resources and {totals["paper"]} papers.'
    yield 'Age counts days since verified_at. It plans rechecks; it is not a staleness, accuracy or maintenance claim.'
    for label in report['bands']:
        yield f'  {label}: {counts["resource"][label]} resources, {counts["paper"][label]} papers'
    if ahead:
        yield f'  reviewed after the as-of date: {len(ahead)}'
    scans = report['automated_readme_scans']
    if scans['records']:
        later = f', {scans["observed_after_as_of"]} after the as-of date' if scans['observed_after_as_of'] else ''
        yield (f'Automated README scans (observed_at, not source reviews): {scans["records"]} records observed '
               f'{scans["earliest"]} to {scans["latest"]}{later}; not listed below.')
    selected = [entry for entry in report['records']
                if entry['age_days'] >= min_age and record_type in (None, entry['record_type'])]
    band = None
    for entry in selected:
        if entry['band'] != band:
            band = entry['band']
            yield f'\n{band}'
        yield f'{entry["record_type"]:<8} {entry["id"]}  {entry["review_date"]}  {entry["age_days"]}d  {entry["evidence_url"]}'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--as-of', help='Report date as YYYY-MM-DD; defaults to the current UTC date')
    parser.add_argument('--bands', default=','.join(map(str, DEFAULT_BANDS)),
                        help='Increasing day boundaries for age groups (default %(default)s)')
    parser.add_argument('--type', choices=RECORD_TYPES, help='List only this record type; counts still cover both')
    parser.add_argument('--min-age-days', type=int, default=0, help='List only records at least this many days since review')
    parser.add_argument('--json', action='store_true', help='Print the full JSON report instead of text')
    args = parser.parse_args(argv)
    try:
        as_of = dt.date.fromisoformat(args.as_of) if args.as_of else dt.datetime.now(dt.timezone.utc).date()
        bands = tuple(int(value) for value in args.bands.split(','))
    except ValueError:
        parser.error('use --as-of YYYY-MM-DD and comma-separated whole-day --bands')
    if not bands or bands[0] <= 0 or any(low >= high for low, high in zip(bands, bands[1:])) or args.min_age_days < 0:
        parser.error('bands must be positive and increasing, and min-age-days nonnegative')
    report = review_queue(*read_catalogs(), as_of, bands)
    if args.json:
        report['records'] = [entry for entry in report['records']
                             if entry['age_days'] >= args.min_age_days and args.type in (None, entry['record_type'])]
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print('\n'.join(text_lines(report, args.type, args.min_age_days)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
