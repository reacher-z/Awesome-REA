#!/usr/bin/env python3
"""Search the reviewed resource catalog using the Python standard library."""
import argparse
import json
from pathlib import Path

from artifact_links import with_curated_labels
from localization import localized_records, read_localizations
from source_scope import apply_scope, read_scope
from validate_papers import read_papers
from build_paper_pages import STATUS_LABELS
from source_descriptions import description_fallback

ROOT = Path(__file__).resolve().parents[1]
RESOURCE_FILES = (ROOT / 'data/rea-resources.json', ROOT / 'data/tool-resources.json')


def load_resources():
    return [record for path in RESOURCE_FILES for record in json.loads(path.read_text(encoding='utf-8'))]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('query', nargs='?', default='', help='Search name, description, category, and requirements')
    parser.add_argument('--category', help='Exact category; use --list-categories to see available values')
    parser.add_argument('--relationship', help='Exact relationship to REA')
    parser.add_argument('--target', choices=['website', 'game', 'app', 'binary', 'firmware', 'protocol'], help='Type of target to investigate')
    parser.add_argument('--language', choices=['en', 'zh'], default='en')
    parser.add_argument('--json', action='store_true', help='Print full records with provenance')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--source-index', action='store_true', help='Search the separate automated README scan index')
    mode.add_argument('--papers', action='store_true', help='Search the separate source-reviewed bibliography')
    parser.add_argument('--list-categories', action='store_true')
    args = parser.parse_args()
    if args.papers:
        if args.category or args.relationship or args.list_categories:
            parser.error('Paper searches support --target and --language; categories and relationships apply to resource catalogs.')
        records = read_papers()
    elif args.source_index:
        records = json.loads((ROOT / 'data/source-index.json').read_text(encoding='utf-8'))['resources']
        records = with_curated_labels(apply_scope(localized_records(records, read_localizations(ROOT)), read_scope(ROOT)), load_resources())
        records = [record for record in records if record.get('scope_status') != 'excluded']
    else:
        records = load_resources()
    if args.list_categories:
        print('\n'.join(sorted({record['category'] for record in records})))
        return
    terms = args.query.casefold().split()
    records = [record for record in records
               if all(term in json.dumps(record, ensure_ascii=False).casefold() for term in terms)
               and (args.category is None or record['category'] == args.category)
               and (args.target is None or args.target in record.get('targets', []))
               and (args.relationship is None or record.get('relationship') == args.relationship)]
    if args.json:
        print(json.dumps(records, ensure_ascii=False, indent=2))
        return
    noun = ('篇论文' if args.language == 'zh' else 'papers') if args.papers else ('项资源' if args.language == 'zh' else 'resources')
    print(f'{len(records)} {noun}')
    for record in records:
        if args.papers:
            zh = args.language == 'zh'
            print(f"\n{record['title_zh' if zh else 'title']} [{record['year']} · {record['venue']} · {STATUS_LABELS[record['publication_status']][int(zh)]}]")
            print(record['url'])
            print(record[f'description_{args.language}'])
            print(('研究范围与局限：' if zh else 'Scope and limits: ') + record[f'scope_limitations_{args.language}'])
            continue
        print(f"\n{record['name']} [{record.get('relationship', record.get('scan_status'))}]")
        print(record['url'])
        description = record[f'description_{args.language}']
        if args.source_index and not description:
            description = description_fallback(record, args.language)
        print(description)
        requirements = record['requirements']
        if isinstance(requirements, list):
            requirements = ' '.join(requirements)
        if not args.source_index:
            print(f"Requirements: {requirements}")


if __name__ == '__main__':
    main()
