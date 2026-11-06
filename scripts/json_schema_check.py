"""Check a JSON value against the JSON Schema subset /api/v1/schema.json uses, without dependencies.

Supported keywords: type, enum, const, properties, required, additionalProperties (boolean or schema),
propertyNames, items, minItems, minLength, minimum, pattern, anyOf and local $ref (``#/$defs/...``).
``format`` is an annotation here, as in JSON Schema 2020-12 by default; ``pattern`` carries the checks.
"""
from __future__ import annotations

import re

TYPES = {'object': dict, 'array': list, 'string': str, 'boolean': bool, 'null': type(None)}


def _type_matches(value, name: str) -> bool:
    if name == 'integer':
        return isinstance(value, int) and not isinstance(value, bool)
    if name == 'number':
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, TYPES[name])


def errors(value, schema: dict, root: dict | None = None, path: str = '$') -> list[str]:
    """Every violation as 'path: reason'; an empty list means the value conforms."""
    root = schema if root is None else root
    if '$ref' in schema:
        reference = schema['$ref']
        if not reference.startswith('#/'):
            raise ValueError(f'Only local references are supported: {reference}')
        target = root
        for part in reference[2:].split('/'):
            target = target[part]
        return errors(value, target, root, path)
    found = []
    if 'anyOf' in schema:
        if all(errors(value, option, root, path) for option in schema['anyOf']):
            found.append(f'{path}: matches none of the allowed forms')
        return found
    kinds = schema.get('type')
    if kinds is not None:
        names = kinds if isinstance(kinds, list) else [kinds]
        if not any(_type_matches(value, name) for name in names):
            return [f'{path}: expected {"/".join(names)}']
    if 'const' in schema and value != schema['const']:
        found.append(f'{path}: must be {schema["const"]!r}')
    if 'enum' in schema and value not in schema['enum']:
        found.append(f'{path}: {value!r} is not an allowed value')
    if isinstance(value, str):
        if len(value) < schema.get('minLength', 0):
            found.append(f'{path}: shorter than {schema["minLength"]}')
        if 'pattern' in schema and not re.search(schema['pattern'], value):
            found.append(f'{path}: does not match {schema["pattern"]}')
    if isinstance(value, (int, float)) and not isinstance(value, bool) and 'minimum' in schema and value < schema['minimum']:
        found.append(f'{path}: below {schema["minimum"]}')
    if isinstance(value, list):
        if len(value) < schema.get('minItems', 0):
            found.append(f'{path}: fewer than {schema["minItems"]} items')
        if 'items' in schema:
            for index, item in enumerate(value):
                found += errors(item, schema['items'], root, f'{path}[{index}]')
    if isinstance(value, dict):
        for key in schema.get('required', []):
            if key not in value:
                found.append(f'{path}: missing {key}')
        properties = schema.get('properties', {})
        extra = schema.get('additionalProperties', True)
        for key, item in value.items():
            if 'propertyNames' in schema:
                found += errors(key, schema['propertyNames'], root, f'{path}.<key {key}>')
            if key in properties:
                found += errors(item, properties[key], root, f'{path}.{key}')
            elif extra is False:
                found.append(f'{path}: unexpected property {key}')
            elif isinstance(extra, dict):
                found += errors(item, extra, root, f'{path}.{key}')
    return found
