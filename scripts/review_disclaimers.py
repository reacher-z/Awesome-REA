#!/usr/bin/env python3
"""List requirement sentences that describe this catalog's review instead of the project.

data/README.md keeps such sentences out of `requirements`: every entry page already states what source review
does not establish. A record whose sources invite the opposite reading uses the one documented phrase, which this
report skips. The report is advisory, so a reviewer decides which listed sentences are specific to their record;
it always exits 0.
"""
import json
import re

from catalog import ROOT, RESOURCE_FILES

PHRASE_EN = 'Not run or reproduced for this catalog.'
PHRASE_ZH = '本目录未运行或复现。'
SELF_EN = re.compile(r'\bthis (?:source review|collection|review|catalog|entry|record|listing|index)\b', re.IGNORECASE)
SELF_ZH = re.compile(r'本合集|本目录|本次|本条目|本记录|本清单|本索引')


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
        for language, items, pattern, phrase in (('en', english, SELF_EN, PHRASE_EN),
                                                 ('zh', chinese, SELF_ZH, PHRASE_ZH)):
            for index, item in enumerate(items):
                for sentence in sentences(item, language == 'zh'):
                    if pattern.search(sentence) and phrase not in sentence:
                        found.append((identifier, language, index, sentence))
    return found


def main():
    records = [record for path in RESOURCE_FILES for record in json.loads(path.read_text(encoding='utf-8'))]
    translations = json.loads((ROOT / 'site/translations.zh-CN.json').read_text(encoding='utf-8'))
    found = findings(records, translations)
    for identifier, language, index, sentence in found:
        print(f'{identifier} [{language} {index}] {sentence}')
    print(f'{len(found)} requirement sentences in {len({item[0] for item in found})} records refer to this '
          "catalog's review; keep only those specific to their record (see data/README.md).")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
