#!/usr/bin/env python3
"""Project the official schema.org vocabulary onto the facts validate_schema_org.py checks.

The vendored ``schema_org_vocabulary.json`` holds every type with its parents and every property with the
types it applies to (``domainIncludes``) and the types its values take (``rangeIncludes``), from one
schema.org release. Refresh it from a downloaded release file, then commit the result:

    curl -sL -o schemaorg.jsonld https://schema.org/version/latest/schemaorg-current-https.jsonld
    python3 scripts/schema_org_vocabulary.py schemaorg.jsonld --version 30.1
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

VOCABULARY = Path(__file__).resolve().parent / 'schema_org_vocabulary.json'
SOURCE_URL = 'https://schema.org/version/latest/schemaorg-current-https.jsonld'


def _ids(value) -> list[str]:
    values = value if isinstance(value, list) else [value] if value else []
    return sorted({item['@id'].removeprefix('schema:') for item in values if isinstance(item, dict) and str(item.get('@id', '')).startswith('schema:')})


def project(document: dict) -> dict:
    types, properties = {}, {}
    for node in document['@graph']:
        kinds = node.get('@type')
        kinds = kinds if isinstance(kinds, list) else [kinds]
        name = str(node.get('@id', ''))
        if not name.startswith('schema:'):
            continue
        name = name.removeprefix('schema:')
        if 'rdf:Property' in kinds:
            properties[name] = {'domains': _ids(node.get('schema:domainIncludes')), 'ranges': _ids(node.get('schema:rangeIncludes'))}
        elif 'rdfs:Class' in kinds or 'schema:DataType' in kinds:
            types[name] = _ids(node.get('rdfs:subClassOf'))
        else:
            # Enumeration members are instances of their enumeration type.
            enumerations = [kind.removeprefix('schema:') for kind in kinds if isinstance(kind, str) and kind.startswith('schema:')]
            if enumerations:
                types.setdefault(name, sorted(enumerations))
    return {'types': dict(sorted(types.items())), 'properties': dict(sorted(properties.items()))}


def load() -> dict:
    return json.loads(VOCABULARY.read_text(encoding='utf-8'))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('source', type=Path, help='schemaorg-current-https.jsonld from a schema.org release')
    parser.add_argument('--version', required=True, help='The schema.org release number, e.g. 30.1')
    args = parser.parse_args()
    raw = args.source.read_bytes()
    value = {'release': args.version, 'source': SOURCE_URL, 'source_sha256': hashlib.sha256(raw).hexdigest(),
             **project(json.loads(raw))}
    VOCABULARY.write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':'), sort_keys=True) + '\n', encoding='utf-8')
    print(f"schema.org {args.version}: {len(value['types'])} types, {len(value['properties'])} properties")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
