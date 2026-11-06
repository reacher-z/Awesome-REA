#!/usr/bin/env python3
"""Validate every JSON-LD block of the built site against the schema.org vocabulary.

For each node with an ``@type``, the type must exist; every property must exist and apply to that type
(its ``domainIncludes`` holds the type or an ancestor); every value must fit the property's
``rangeIncludes``: a typed node whose type is a range type or a subtype, a reference ``{"@id": ...}``, or a
literal that a range data type accepts (an absolute URL also stands for a referenced thing). ``@id``
references within the site must resolve to a node some page defines; a bare URL may name a page. Action annotations
such as ``query-input`` follow the schema.org ``-input``/``-output`` convention.

The vocabulary is the vendored projection of one schema.org release (schema_org_vocabulary.py). The
check reports errors, never warnings; ``main`` exits 1 when any page has one.
"""
from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from schema_org_vocabulary import load  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'dist'
ORIGIN = 'https://awesomerea.org'
CONTEXT = 'https://schema.org'
KEYWORDS = {'@context', '@id', '@type', '@graph'}
DATE = re.compile(r'\d{4}(?:-\d{2}(?:-\d{2})?)?')
DATETIME = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2})?')
URL = re.compile(r'https?://[^\s<>"]+')


class _Blocks(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.blocks, self._buffer = [], None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        if tag == 'script' and dict(attrs).get('type') == 'application/ld+json':
            self._buffer = []

    def handle_data(self, data):
        if self._buffer is not None:
            self._buffer.append(data)

    def handle_endtag(self, tag):
        if tag == 'script' and self._buffer is not None:
            self.blocks.append(json.loads(''.join(self._buffer)))
            self._buffer = None


class Vocabulary:
    def __init__(self, data: dict):
        self.types, self.properties, self.release = data['types'], data['properties'], data.get('release')
        self._ancestors = {}

    def ancestors(self, name: str) -> set[str]:
        if name not in self._ancestors:
            seen, stack = set(), [name]
            while stack:
                current = stack.pop()
                if current in seen:
                    continue
                seen.add(current)
                stack.extend(self.types.get(current, []))
            self._ancestors[name] = seen
        return self._ancestors[name]

    def is_a(self, name: str, other: str) -> bool:
        return other in self.ancestors(name)


def literal_fits(vocabulary: Vocabulary, value, ranges: list[str]) -> bool:
    """Whether a JSON literal fits one of the data-type ranges, or is an absolute URL naming a thing."""
    if isinstance(value, bool):
        return 'Boolean' in ranges
    if isinstance(value, (int, float)):
        return any(vocabulary.is_a(kind, 'Number') or kind == 'Number' for kind in ranges) or 'Text' in ranges
    if not isinstance(value, str):
        return False
    for kind in ranges:
        if kind == 'Text' or vocabulary.is_a(kind, 'Text'):
            if kind == 'URL' and not URL.fullmatch(value):
                continue
            return True
        if kind == 'Date' and DATE.fullmatch(value):
            return True
        if kind == 'DateTime' and (DATETIME.fullmatch(value) or DATE.fullmatch(value)):
            return True
        if kind in ('Number', 'Integer', 'Float') and re.fullmatch(r'-?\d+(?:\.\d+)?', value):
            return True
    # A URL string for a property that expects a thing identifies that thing (Google's BreadcrumbList item).
    return bool(URL.fullmatch(value)) and any(kind not in ('Text', 'Date', 'DateTime', 'Number', 'Integer', 'Boolean') for kind in ranges)


def node_errors(vocabulary: Vocabulary, node: dict, where: str, defined: set[str], known_ids: set[str],
                known_pages: frozenset = frozenset()) -> list[str]:
    errors = []
    kinds = node.get('@type')
    kinds = [kinds] if isinstance(kinds, str) else kinds or []
    for kind in kinds:
        if kind not in vocabulary.types:
            errors.append(f'{where}: unknown type {kind}')
    for key, value in node.items():
        if key in KEYWORDS:
            continue
        if re.fullmatch(r'[A-Za-z]+-(?:input|output)', key):
            # Action annotations (https://schema.org/docs/actions.html): "<property>-input".
            if not isinstance(value, str) or not any(vocabulary.is_a(kind, 'Action') for kind in kinds):
                errors.append(f'{where}: {key} belongs on an Action as a text specification')
            continue
        definition = vocabulary.properties.get(key)
        if definition is None:
            errors.append(f'{where}: unknown property {key}')
            continue
        if kinds and not any(vocabulary.is_a(kind, domain) for kind in kinds for domain in definition['domains']):
            errors.append(f'{where}: {key} does not apply to {"/".join(kinds)}')
        for index, item in enumerate(value if isinstance(value, list) else [value]):
            at = f'{where}.{key}' + (f'[{index}]' if isinstance(value, list) else '')
            if isinstance(item, dict):
                item_kinds = item.get('@type')
                item_kinds = [item_kinds] if isinstance(item_kinds, str) else item_kinds or []
                if not item_kinds:
                    if set(item) != {'@id'}:
                        errors.append(f'{at}: an untyped node may only reference an @id')
                    elif (item['@id'].startswith(ORIGIN) and item['@id'] not in defined and item['@id'] not in known_ids
                          and not (urlsplit(item['@id']).path in known_pages and not urlsplit(item['@id']).fragment)):
                        # A fragment names a node some page defines; a bare URL may name a page itself.
                        errors.append(f'{at}: reference to an undefined node {item["@id"]}')
                    continue
                if not any(vocabulary.is_a(kind, expected) for kind in item_kinds for expected in definition['ranges']):
                    errors.append(f'{at}: {"/".join(item_kinds)} is not a {" or ".join(definition["ranges"])}')
                errors += node_errors(vocabulary, item, at, defined, known_ids, known_pages)
            elif not literal_fits(vocabulary, item, definition['ranges']):
                errors.append(f'{at}: {item!r} does not fit {" or ".join(definition["ranges"])}')
    return errors


def nodes(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from nodes(item)
    elif isinstance(value, list):
        for item in value:
            yield from nodes(item)


def defined_ids(blocks: list[dict]) -> set[str]:
    """The @id of each node that says something; a node holding only an @id is a reference."""
    return {node['@id'] for block in blocks for node in nodes(block) if isinstance(node.get('@id'), str) and len(node) > 1}


def page_errors(vocabulary: Vocabulary, html: str, where: str, known_ids: set[str],
                known_pages: frozenset = frozenset()) -> list[str]:
    return block_errors(vocabulary, _Blocks(html).blocks, where, known_ids, known_pages)


def block_errors(vocabulary: Vocabulary, blocks: list[dict], where: str, known_ids: set[str],
                 known_pages: frozenset = frozenset()) -> list[str]:
    errors = [] if blocks else [f'{where}: no JSON-LD']
    defined = defined_ids(blocks)
    for number, block in enumerate(blocks):
        if block.get('@context') != CONTEXT:
            errors.append(f'{where}[{number}]: @context must be {CONTEXT}')
        roots = block['@graph'] if isinstance(block.get('@graph'), list) else [block]
        for index, root in enumerate(roots):
            if not root.get('@type'):
                errors.append(f'{where}[{number}].{index}: a top-level node needs @type')
            errors += node_errors(vocabulary, root, f'{where}[{number}].{index}', defined, known_ids, known_pages)
    return errors


def validate_site(output: Path, routes: list[str]) -> tuple[int, list[str]]:
    """Validate each route's JSON-LD; a reference may name a node that any page of the site defines."""
    vocabulary = Vocabulary(load())
    output = Path(output)
    pages = {route: _Blocks((output / route.lstrip('/') / 'index.html').read_text(encoding='utf-8')).blocks for route in routes}
    known_ids = set().union(*(defined_ids(blocks) for blocks in pages.values()))
    known_pages = frozenset(routes)
    errors, count = [], 0
    for route, blocks in pages.items():
        errors += block_errors(vocabulary, blocks, route, known_ids, known_pages)
        count += len(blocks)
        errors += [f'{route}: DataDownload {node["contentUrl"]} is not a published file' for block in blocks for node in nodes(block)
                   if node.get('@type') == 'DataDownload' and not (output / urlsplit(node['contentUrl']).path.lstrip('/')).is_file()]
    return count, errors


def main() -> int:
    from sitemaps import sitemap_urls
    routes = [urlsplit(url).path for url in sitemap_urls(OUTPUT, ORIGIN)]
    vocabulary = load()
    count, errors = validate_site(OUTPUT, routes)
    for error in errors[:50]:
        print(error)
    if errors:
        print(f'schema.org validation failed: {len(errors)} errors in {count} JSON-LD blocks on {len(routes)} pages (release {vocabulary["release"]}).')
        return 1
    print(f'schema.org validation passed: {count} JSON-LD blocks on {len(routes)} pages, 0 errors (schema.org {vocabulary["release"]}).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
