# Repository description localization

These files provide English and Simplified Chinese descriptions for the collection's 3,000 scanned repositories. They are AI-assisted translations of upstream repository descriptions, not repository reviews or compatibility tests.

## Source and output

- [source-index.json](../source-index.json) preserves the upstream snapshot and explicit omission evidence. Its historical `description_en` field contains the original text in any source language; `description_zh` mirrors that original with status `not-translated`.
- [repositories-1.json](repositories-1.json), [repositories-2.json](repositories-2.json), and [repositories-3.json](repositories-3.json) contain derived descriptions, keyed by the exact source record `id`. Every ID belongs to exactly one file.
- [build_site.py](../../scripts/build_site.py) merges the translations into `dist/source-index.json`. Generated records retain available upstream text in `description_original`, label their description language as `bilingual`, and identify localization as `ai-assisted-translation`. Generated metadata separates the upstream description policy from the localized output policy. Source scan evidence and review status remain unchanged.

Each locale entry contains `description_en` and `description_zh` strings. Preserve natural English originals; translate other source languages into English. Translate every nonempty description into Simplified Chinese, preserving project names, technical identifiers, versions, limitations, and qualifiers. Do not substitute generic descriptions or add unsupported capabilities. If the source description is empty, keep both strings empty so the interface can show its localized fallback. Records with `description_omission` also keep both strings empty and display a separate omission explanation; do not copy or translate the omitted payload.

## Source fingerprints

[locale-source-fingerprints.json](../locale-source-fingerprints.json) binds each translation to the source text it was written from. Under policy `source-description-sha256-v1`, a fingerprint is the SHA-256 of the canonical JSON object holding the source record's `description_en` and `description_omission`, so an empty description and an omission each have one. When either value changes, validation reports that translation as stale until both languages are reviewed and the fingerprint is recorded again. A fingerprint for an ID without a source record or translation is an error. A translation without a fingerprint is only a warning. `scripts/localization.py` writes only this file; it never rewrites source text or locale values.

The initial fingerprints, recorded on 2026-10-19, bind all 3,000 existing translations to the source text in that snapshot. They record the existing pairing and are not a new translation review.

## Maintain the collection

1. Add or refresh repository metadata in the source index through the [scan workflow](../../docs/source-scan.md). Keep retained upstream descriptions intact; oversized new captures use the documented fingerprint-only omission policy.
2. Add each new ID to one locale file with both languages. When upstream text changes, review both translations; remove locale IDs that no longer exist in the source snapshot. File membership is organizational, not a category or ranking.
3. After reviewing a new or revised translation, record its source fingerprint with `python3 scripts/localization.py --bind <id>`. For several new IDs, `--bind-unbound` binds every translation that has none yet; it never rebinds a stale one. Run the script without options for a count of bound, stale, unbound and unknown fingerprints.
4. Run `python3 scripts/validate.py` from the repository root. It checks exact ID coverage, duplicate IDs, required text, language signals and source fingerprints. An intentional retained Chinese proper name in English may use `english_retains_name: true`; an identifier-only description may use `technical_only: true`. Use these exceptions only after reviewing the text.
5. Build with `python3 scripts/build_site.py` and follow the [website preview checks](../../docs/website.md#build-and-preview). Verify both descriptions and surrounding interface text switch language, including after searching, filtering, and loading more results.

These files cover scanned repository descriptions. The [Chinese terminology glossary](../../CONTRIBUTING.zh-CN.md#术语对照) applies to interface text and generated labels, and where practical to curated descriptions; it does not apply to these upstream-derived translations. Curated descriptions remain in [rea-resources.json](../rea-resources.json) and [tool-resources.json](../tool-resources.json); their Chinese display names and prerequisites use [translations.zh-CN.json](../../site/translations.zh-CN.json). Full upstream READMEs are not translated or republished here.
