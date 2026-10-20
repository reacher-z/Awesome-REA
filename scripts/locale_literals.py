#!/usr/bin/env python3
"""Advisory review of technical literals between scanned source descriptions and their translations.

Lists URLs, versions, identifiers and numbers in a source description that a translation drops or
changes, keyed by the stable source ID. Numbers are compared by value, so thousands separators,
K/M/B suffixes, Chinese numerals and the 万/亿 units match their equivalents. Identifiers are
compared verbatim, so a translation that keeps an unusual source spelling passes. Reviewed
exceptions are honored. Nothing is translated or rewritten, and findings never fail validation.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path
import re
import sys

from localization import read_localizations

ROOT = Path(__file__).resolve().parents[1]
EXCEPTIONS_FILE = 'data/locale-literal-exceptions.json'
FIELDS = ('description_en', 'description_zh')
KINDS = ('url-missing', 'url-added', 'version-missing', 'identifier-missing', 'identifier-case-changed',
         'number-missing', 'number-added')
EXCEPTION_FIELDS = {'field', 'kind', 'literal', 'reason', 'reviewed_at'}
URL = r'https?://[^\s<>"\'()（）\[\]，。、；！？]+'
# ASCII boundaries: CJK text often touches a literal without a space, and a sentence may end right after one.
BEFORE, AFTER = r'(?<![A-Za-z0-9_.])', r'(?![A-Za-z0-9_]|\.[A-Za-z0-9])'
# A version has a v prefix or at least two dots; a single-dot value such as 5.8 is compared as a number.
VERSION = (BEFORE + r'(?:[vV]\d+(?:\.\d+)*|\d+(?:\.\d+){2,})'
           r'(?:-(?:alpha|beta|rc|dev|pre)[0-9.]*|\+[0-9A-Za-z.]+)?' + AFTER)
NUMBER = BEFORE + r'(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d+))?(?:\s*([kKmMbB](?![A-Za-z])|万|亿|千)|(?:st|nd|rd|th)\b)?' + AFTER
TOKEN = r'[A-Za-z0-9][A-Za-z0-9_.+#]*[A-Za-z0-9+#]|[A-Za-z0-9]'
SUFFIXES = {'k': 1000, 'm': 10 ** 6, 'b': 10 ** 9, '万': 10 ** 4, '亿': 10 ** 8, '千': 1000}
CHINESE_DIGITS = {'零': 0, '〇': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
CHINESE_UNITS = {'十': 10, '百': 100, '千': 1000}
ENGLISH_NUMBERS = {word: value for value, word in enumerate(
    'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen '
    'seventeen eighteen nineteen twenty'.split())} | {'thirty': 30, 'forty': 40, 'fifty': 50, 'hundred': 100,
                                                     'thousand': 1000, 'million': 10 ** 6, 'first': 1, 'second': 2, 'third': 3,
                                                     'single': 1, 'once': 1, 'double': 2, 'dual': 2, 'twice': 2}
ENGLISH_NUMBERS |= {month: index for index, month in enumerate('jan feb mar apr may jun jul aug sep oct nov dec'.split(), 1)}
# Single characters that state a count in compounds such as 单文件 (single-file), 首本 (first) and 双向 (two-way).
CHINESE_COUNTS = {'单': 1, '首': 1, '双': 2}
# A whole-percentage claim is often rendered as 完全 or 全部 rather than a figure.
WHOLE = ('100%', '100 %')
WHOLE_WORDS = ('完全', '全部', '百分之百', 'entirely', 'fully', 'completely')


def chinese_value(text):
    """Value of a Chinese numeral such as 十二, 两百, 六 or 三万; callers pass spans with a digit or unit."""
    total, section, digit = 0, 0, None
    for char in text:
        if char in CHINESE_DIGITS:
            digit = CHINESE_DIGITS[char]
        elif char in CHINESE_UNITS:
            section += (1 if digit is None else digit) * CHINESE_UNITS[char]
            digit = None
        elif char in ('万', '亿'):
            total = (total + section + (digit or 0)) * (10 ** 4 if char == '万' else 10 ** 8)
            section, digit = 0, None
    return total + section + (digit or 0)


def without(text, pattern):
    return re.sub(pattern, ' ', text)


def literals(text):
    """Extract URLs, versions, identifiers and Arabic-numeral values from one description."""
    urls = [match.rstrip('.,;:!?') for match in re.findall(URL, text)]
    rest = without(text, URL)
    versions = re.findall(VERSION, rest)
    rest = without(rest, VERSION)
    identifiers = []
    # Hyphens split tokens, so radare2-based keeps radare2 and 10-phase or video-to-3D add nothing.
    for token in re.findall(TOKEN, rest):
        # Identifiers start with a letter: digit-first tokens such as 64bit, 4x or 3D are units, often translated.
        # Letters with digits (IL2CPP, x64dbg), snake_case and dotted names (Node.js) are kept verbatim.
        if ('_' in token or re.match(r'[A-Za-z]', token) and (re.search(r'\d', token)
                or re.fullmatch(r'[A-Za-z0-9]{2,}(?:\.[A-Za-z0-9]{2,})+', token))):
            identifiers.append(token)
    numbers = []
    for whole, fraction, suffix in re.findall(NUMBER, without(rest, r'[A-Za-z]+\d[\w.+#-]*|\d+[A-Za-z]{2,}\w*')):
        value = Fraction(whole.replace(',', '') + ('.' + fraction if fraction else ''))
        numbers.append(value * SUFFIXES.get(suffix.lower() if suffix else '', 1))
    return {'urls': urls, 'versions': versions, 'identifiers': identifiers, 'numbers': numbers}


def all_values(text):
    """Every numeric value a text expresses, including Chinese numerals and common English number words."""
    values = set(literals(text)['numbers'])
    values.update(chinese_value(match) for match in re.findall(r'[零〇一二两三四五六七八九十百千]+[万亿]?', text)
                  if any(char in CHINESE_DIGITS or char in CHINESE_UNITS for char in match))
    values.update(ENGLISH_NUMBERS[word] for word in re.findall(r'[a-z]+', text.lower()) if word in ENGLISH_NUMBERS)
    values.update(value for char, value in CHINESE_COUNTS.items() if char in text)
    # Identifiers such as x64, W8.1 or Win32 still state their digits.
    values.update(Fraction(match) for match in re.findall(r'\d+(?:\.\d+)?', text))
    return values


def year_aliases(text):
    """Two-digit years written as NDSS'14, CCS24 or 2000-01 also stand for the full year."""
    aliases = {}
    for match in re.finditer(r"(?:['’]|(?<=[A-Z]{2}))(\d{2})\b", text):
        value = int(match[1])
        aliases[Fraction(value)] = {Fraction(1900 + value), Fraction(2000 + value)}
    for century, start, end in re.findall(r'\b(\d{2})(\d{2})[-–—](\d{2})\b', text):
        aliases[Fraction(int(end))] = {Fraction(int(century + end))}
    return aliases


def display(value):
    return str(value.numerator) if value.denominator == 1 else format(float(value), 'g')


def findings_for(identifier, source, translation, field):
    """Compare one translation with its source text; every finding is a candidate for review."""
    found, have = literals(source), literals(translation)
    rows = [('url-missing', url) for url in found['urls'] if url not in translation]
    rows += [('url-added', url) for url in have['urls'] if url not in found['urls']]
    lowered = translation.casefold()
    rows += [('version-missing', version) for version in found['versions'] if version.casefold() not in lowered]
    for token in found['identifiers']:
        if token not in translation:
            rows.append(('identifier-case-changed' if token.casefold() in lowered else 'identifier-missing', token))
    values, aliases = all_values(translation), year_aliases(source)
    whole = any(literal in source for literal in WHOLE) and any(word in lowered for word in WHOLE_WORDS)
    rows += [('number-missing', display(value)) for value in found['numbers']
             if value not in values and not aliases.get(value, set()) & values and not (whole and value == 100)]
    source_values = all_values(source) | {year for years in aliases.values() for year in years}
    rows += [('number-added', display(value)) for value in have['numbers'] if value not in source_values]
    return [{'id': identifier, 'field': field, 'kind': kind, 'literal': literal}
            for kind, literal in dict.fromkeys(rows)]


def read_exceptions(path):
    """Reviewed exceptions keyed by source ID; each names the exact finding it accepts and why."""
    if not path.exists():
        return {}
    document = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(document, dict) or any(
            not isinstance(entries, list) or any(not isinstance(entry, dict) or set(entry) != EXCEPTION_FIELDS
                                                 or entry['field'] not in FIELDS or entry['kind'] not in KINDS
                                                 or not all(isinstance(entry[key], str) and entry[key].strip()
                                                            for key in EXCEPTION_FIELDS)
                                                 or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', entry['reviewed_at'])
                                                 for entry in entries)
            for entries in document.values()):
        raise ValueError(f'{EXCEPTIONS_FILE}: each exception needs field, kind, literal, reason and reviewed_at')
    return document


def literal_report(records, translations, exceptions):
    findings, excepted = [], []
    accepted = {(identifier, entry['field'], entry['kind'], entry['literal'])
                for identifier, entries in exceptions.items() for entry in entries}
    for record in sorted(records, key=lambda record: int(record['id'][5:]) if record['id'][5:].isdigit() else 0):
        source, entry = record.get('description_en') or '', translations.get(record['id'])
        if not source or not isinstance(entry, dict):
            continue  # Empty and omitted descriptions have nothing to preserve.
        for field in FIELDS:
            if isinstance(entry.get(field), str):
                for row in findings_for(record['id'], source, entry[field], field):
                    key = (row['id'], row['field'], row['kind'], row['literal'])
                    (excepted if key in accepted else findings).append(row)
    used = {(row['id'], row['field'], row['kind'], row['literal']) for row in excepted}
    return {
        'policy': ('Advisory comparison of technical literals in source descriptions and their translations. Findings are '
                   'review prompts, not errors; translations are never generated or rewritten. Numbers compare by value, '
                   'identifiers and URLs verbatim, versions case-insensitively.'),
        'counts': {kind: sum(row['kind'] == kind for row in findings) for kind in KINDS},
        'records_with_findings': len({row['id'] for row in findings}),
        'excepted': len(excepted),
        'unused_exceptions': sorted('/'.join(key) for key in accepted - used),
        'findings': findings,
    }


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--source', type=Path, default=Path(root) / 'data/source-index.json')
    parser.add_argument('--exceptions', type=Path, default=Path(root) / EXCEPTIONS_FILE)
    parser.add_argument('--id', action='append', dest='ids', help='Limit the report to this source ID; repeat for more')
    args = parser.parse_args(argv)
    try:
        records = json.loads(args.source.read_text(encoding='utf-8'))['resources']
        translations = read_localizations(Path(root))
        exceptions = read_exceptions(args.exceptions)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'Literal review inputs could not be read: {error}', file=sys.stderr)
        return 2
    if args.ids:
        records = [record for record in records if record['id'] in set(args.ids)]
    print(json.dumps(literal_report(records, translations, exceptions), ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
