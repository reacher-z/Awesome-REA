#!/usr/bin/env python3
"""List requirement sentences that describe this catalog's review instead of the project.

Visitors read `requirements` on every entry page, so the items state what the project needs and what it is:
data/README.md keeps notes about what this catalog ran, built or did not establish out of them. The review date
and `verification` field carry the review status, and `relationship` records the REA connection. The report is
advisory, so a reviewer decides which listed sentences to drop; it always exits 0.
"""
import json
import re

from catalog import ROOT, RESOURCE_FILES

SELF_EN = re.compile(
    r'\bthis (?:source review|collection|review|catalog|entry|record|listing|index)\b'
    r'|\bfor this (?:review|catalog|collection|entry|record|listing)\b|\bin this review\b'
    r'|\breviewed sources? (?:establish|state|mention|document|show|report)s? no\b'
    r'|\bno (?:REA|AI|runtime reproduction)\b[^.;]*\b(?:established|stated|documented|claimed)\b'
    r'|\bnothing was (?:built|run|installed|executed|tested|downloaded)\b',
    re.IGNORECASE)
SELF_ZH = re.compile(r'本合集|本目录|本次|本条目|本记录|本清单|本索引|不主张')

# Exact phrasings that only ever describe this catalog's own review. validate.py rejects them.
BANNED_EN = re.compile(
    r'\bthis collection (?:did not|didn[\'’]t|ran|read|recorded|deployed|installed|built)\b'
    r'|\bno runtime reproduction is claimed\b'
    r'|\bnot run or reproduced for this catalog\b'
    r'|\bno (?:AI or )?REA (?:use|connection|workflow) is (?:established|claimed)\b',
    re.IGNORECASE)
BANNED_ZH = re.compile(r'本合集未|本目录未')


def sentences(text, chinese=False):
    pattern = r'(?<=[。；])' if chinese else r'(?<=[.;])\s+'
    return [part.strip() for part in re.split(pattern, text) if part.strip()]


def findings(records, translations):
    """Return (record id, language, item index, sentence) for every self-referring requirement sentence."""
    found = []
    for record in records:
        identifier = record['id']
        english = record['requirements'] if isinstance(record['requirements'], list) else [record['requirements']]
        chinese = translations.get(identifier, {}).get('requirements', [])
        for language, items, pattern in (('en', english, SELF_EN), ('zh', chinese, SELF_ZH)):
            for index, item in enumerate(items):
                for sentence in sentences(item, language == 'zh'):
                    if pattern.search(sentence):
                        found.append((identifier, language, index, sentence))
    return found


def banned_sentences(records, translations, papers):
    """Return (record id, field, text) for each record text using a banned phrasing."""
    def strings(value):
        items = value if isinstance(value, list) else [value]
        return [item for item in items if isinstance(item, str)]

    found = []
    for record in records:
        identifier = record.get('id')
        for item in strings(record.get('requirements')):
            if BANNED_EN.search(item):
                found.append((identifier, 'requirements', item))
        translation = translations.get(identifier) if isinstance(identifier, str) else None
        for item in strings(translation.get('requirements')) if isinstance(translation, dict) else ():
            if BANNED_ZH.search(item):
                found.append((identifier, 'requirements (zh)', item))
    for paper in papers:
        for field, pattern in (('metadata_notes', BANNED_EN), ('scope_limitations_en', BANNED_EN),
                               ('metadata_notes_zh', BANNED_ZH), ('scope_limitations_zh', BANNED_ZH)):
            for item in strings(paper.get(field)):
                if pattern.search(item):
                    found.append((paper.get('id'), field, item))
    return found


def main():
    records = [record for path in RESOURCE_FILES for record in json.loads(path.read_text(encoding='utf-8'))]
    translations = json.loads((ROOT / 'site/translations.zh-CN.json').read_text(encoding='utf-8'))
    found = findings(records, translations)
    for identifier, language, index, sentence in found:
        print(f'{identifier} [{language} {index}] {sentence}')
    print(f'{len(found)} requirement sentences in {len({item[0] for item in found})} records refer to this '
          "catalog's review; state project facts only (see data/README.md).")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
