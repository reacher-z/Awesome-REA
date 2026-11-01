#!/usr/bin/env python3
"""Strict JSON parsing shared by local validation, trusted PR review and scan resume.

Python's json module keeps the last of two duplicate object keys and accepts NaN and
Infinity, so a file another strict parser rejects could otherwise pass one of the checks.
"""
import json
from pathlib import Path


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON key {key!r}')
        result[key] = value
    return result


def _invalid_constant(value):
    raise ValueError(f'non-JSON numeric constant {value}')


def loads(text):
    """Parse JSON text or UTF-8 bytes, rejecting duplicate keys at any depth and NaN/Infinity."""
    return json.loads(text, object_pairs_hook=_unique_object, parse_constant=_invalid_constant)


def load_path(path):
    """Read a UTF-8 JSON file strictly; the error message names the file."""
    try:
        return loads(Path(path).read_text(encoding='utf-8'))
    except ValueError as error:
        raise ValueError(f'{path}: {error}') from error
