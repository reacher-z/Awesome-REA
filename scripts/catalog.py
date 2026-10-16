#!/usr/bin/env python3
"""Search the reviewed resource catalog using the Python standard library."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESOURCE_FILES = (ROOT / 'data/rea-resources.json', ROOT / 'data/tool-resources.json')


def load_resources():
    return [record for path in RESOURCE_FILES for record in json.loads(path.read_text())]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('query', nargs='?', default='', help='Search name, description, category, and requirements')
    parser.add_argument('--category', help='Exact category; use --list-categories to see available values')
    parser.add_argument('--relationship', help='Exact relationship to REA')
    parser.add_argument('--target', choices=['website', 'game', 'app', 'binary', 'firmware'], help='Type of target to investigate')
    parser.add_argument('--language', choices=['en', 'zh'], default='en')
    parser.add_argument('--json', action='store_true', help='Print full records with provenance')
    parser.add_argument('--source-index', action='store_true', help='Search the separate automated README scan index')
    parser.add_argument('--list-categories', action='store_true')
    args = parser.parse_args()
    records = (json.loads((ROOT / 'data/source-index.json').read_text())['resources']
               if args.source_index else load_resources())
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
    print(f'{len(records)} resources')
    for record in records:
        print(f"\n{record['name']} [{record.get('relationship', record.get('scan_status'))}]")
        print(record['url'])
        print(record[f'description_{args.language}'])
        requirements = record['requirements']
        if isinstance(requirements, list):
            requirements = ' '.join(requirements)
        print(f"Requirements: {requirements}")


if __name__ == '__main__':
    main()
