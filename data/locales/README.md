# Repository description localization

These files provide English and Simplified Chinese descriptions for the collection's 3,000 scanned repositories. They are AI-assisted translations of upstream repository descriptions, not repository reviews or compatibility tests.

## Source and output

- [source-index.json](../source-index.json) preserves the upstream snapshot and explicit omission evidence. Its historical `description_en` field contains the original text in any source language; `description_zh` mirrors that original with status `not-translated`.
- [repositories-1.json](repositories-1.json), [repositories-2.json](repositories-2.json), and [repositories-3.json](repositories-3.json) contain derived descriptions, keyed by the exact source record `id`. Every ID belongs to exactly one file.
- [build_site.py](../../scripts/build_site.py) merges the translations into `dist/source-index.json`. Generated records retain available upstream text in `description_original`, label their description language as `bilingual`, and identify localization as `ai-assisted-translation`. Generated metadata separates the upstream description policy from the localized output policy. Source scan evidence and review status remain unchanged.

Each locale entry contains `description_en` and `description_zh` strings. Preserve natural English originals; translate other source languages into English. Translate every nonempty description into Simplified Chinese, preserving project names, technical identifiers, versions, limitations, and qualifiers. Do not substitute generic descriptions or add unsupported capabilities. If the source description is empty, keep both strings empty so the interface can show its localized fallback. Records with `description_omission` also keep both strings empty and display a separate omission explanation; do not copy or translate the omitted payload.

## Maintain the collection

1. Add or refresh repository metadata in the source index through the [scan workflow](../../docs/source-scan.md). Keep retained upstream descriptions intact; oversized new captures use the documented fingerprint-only omission policy.
2. Add each new ID to one locale file with both languages. When upstream text changes, review both translations; remove locale IDs that no longer exist in the source snapshot. File membership is organizational, not a category or ranking.
3. Run `python3 scripts/validate.py` from the repository root. It checks exact ID coverage, duplicate IDs, required text, and language signals. An intentional retained Chinese proper name in English may use `english_retains_name: true`; an identifier-only description may use `technical_only: true`. Use these exceptions only after reviewing the text.
4. Build with `python3 scripts/build_site.py` and follow the [website preview checks](../../docs/website.md#build-and-preview). Verify both descriptions and surrounding interface text switch language, including after searching, filtering, and loading more results.

These files cover scanned repository descriptions. The [Chinese terminology glossary](../../CONTRIBUTING.zh-CN.md#术语对照) applies to interface text and generated labels, and where practical to curated descriptions; it does not apply to these upstream-derived translations. Curated descriptions remain in [rea-resources.json](../rea-resources.json) and [tool-resources.json](../tool-resources.json); their Chinese display names and prerequisites use [translations.zh-CN.json](../../site/translations.zh-CN.json). Full upstream READMEs are not translated or republished here.

## Literal review

`python3 scripts/locale_literals.py` prints an advisory JSON report of technical literals that a translation drops or changes, keyed by source ID and field. It reports:
- a source URL missing from a translation, or a URL the translation adds;
- a version with a `v` prefix or at least two dots that is missing;
- a source identifier that is missing or changed only in case: letters with digits such as `IL2CPP`, snake_case or dotted names, compared verbatim, so a translation that keeps an unusual source spelling passes;
- a number whose value is missing, or a number the translation adds.

Numbers compare by value. Thousands separators, K/M/B suffixes, Chinese numerals, 万 and 亿, short years such as `NDSS'14`, month names and 100% rendered as 完全 or 全部 count as equivalent. Findings are review prompts, not errors. The command exits 0, is not part of `validate.py`, and never translates or rewrites text.

Record an accepted difference in [locale-literal-exceptions.json](../locale-literal-exceptions.json), keyed by source ID, with the exact `field`, `kind` and `literal` plus a `reason` and `reviewed_at` date. The report counts excepted findings separately. It also lists exceptions that no longer match a finding, for example after the source text changes.
