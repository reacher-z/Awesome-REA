# From repository index to curated entry: review worksheet

[简体中文](promotion-worksheet.zh-CN.md) · [Source scan method](source-scan.md) · [Contribution guide](../CONTRIBUTING.md)

Records in the automated [repository index](../data/source-index.json) are README scans with `verification: automated-readme-scan`. Their descriptions, targets and categories come from repository metadata, not review. Curating one of these repositories means writing a separate record from your own review of its primary sources. The scan record itself is never edited, relabeled or upgraded: it keeps its original evidence and status, and the repository directory links it to the curated entry at build time.

Use the worksheet below in the issue or pull request that proposes the entry. Fill in every row. "Unknown" is an acceptable answer, and an unknown in a material row leads to a hold.

## Worksheet

| Row | Question | Answer from |
| --- | --- | --- |
| Source ID | The scan record's `id` and recorded `full_name`. | `python3 scripts/catalog.py --source-index <name> --json` |
| Scan snapshot | Its `observed_at`, `readme_git_sha`, `readme_sha256` and `readme_bytes`, copied unchanged. | The scan record; this identifies what the scan read and is not review evidence. |
| Existing entry | Is the project already curated, or suggested in an open issue or pull request? | `python3 scripts/catalog.py <name>`, open issues and pull requests |
| Canonical project | The maintainer's own repository or website, which becomes `url`. | The project itself; prefer the original over forks and mirrors. |
| Evidence revision | The commit, release or dated page you actually read, as pinned links for `evidence_url` and `additional_evidence_urls`. | Your review |
| Review date | The date of your review, which becomes `verified_at`. | Your review |
| Supported task | What the documentation says the project does, in your own words, for `description_en` and `description_zh`. | Pinned evidence |
| Limitations | Unfinished, experimental or excluded functionality and stated scope limits. | Pinned evidence |
| Requirements | Platforms, versions, inputs and license terms for `requirements` and its Chinese translation. | Pinned evidence |
| Classification | `kind`, `relationship` and `category`, each chosen independently. | [Contribution guide](../CONTRIBUTING.md#choose-kind-relationship-category-and-targets) |
| Target rationale | Why each target applies, citing the evidence. Automatic scan labels are not a reason. | Pinned evidence |
| Decision | Curate, or hold and name the missing evidence. | The rows above |

## Curate or hold

Curate only when every material claim in the description, requirements and targets can be traced to a public primary source at the pinned revision, reviewed on the recorded date. Then add the record and its Chinese requirements as described under [update the catalog](../CONTRIBUTING.md#update-the-catalog), and leave `data/source-index.json` untouched.

Hold when the evidence is insufficient. Typical cases: the README does not say what the project does or how it is used; a capability appears only in the repository description, a scan label or a third-party post; no public source can be pinned; or the target cannot be supported. A hold adds no curated record and changes no scan record. State which row is missing in the issue so a later review can resume. Do not fill a gap with a runtime claim: catalog records do not carry runtime results, and a result you did not observe must never be reported.

A hold is not a scope exclusion. Excluding a clearly unrelated scan from browsing is a separate reviewed change to `data/source-scope.json`, described under [collection scope](source-scan.md#collection-scope).

## Completed example: capa

The scanned repository mandiant/capa is now the curated entry [`capa`](https://awesomerea.org/resources/capa/) in [tool-resources.json](../data/tool-resources.json). Its worksheet:

| Row | Answer |
| --- | --- |
| Source ID | `scan-272815213`, mandiant/capa |
| Scan snapshot | Observed 2026-10-16T01:35:34Z; README Git blob `b75190372c257abfc3822cba33ca58ef2867ce23`, SHA-256 `e3dc86527f193f95f56a405f6b2c35ef6f5102be937b03834827d908664faf11`, 25,053 bytes. Automatic labels: `binary`, `native-analysis`. |
| Existing entry | Not curated before this review. |
| Canonical project | `https://github.com/mandiant/capa` |
| Evidence revision | `README.md` at commit `7a235c46965ea0965c65be3b9ee1e21dca686f3d`, which is the same Git blob the scan recorded. The review also read that commit's installation, usage and limitations guides, plugin READMEs, `pyproject.toml` and license, plus the v10.0.0 release page and the flare-capa 10.0.0 PyPI page. The scan never reads these. |
| Review date | 2026-10-19 |
| Supported task | Reports what an executable can do by matching a YAML rule set against features extracted from PE, ELF and .NET files or shellcode, grouped into capability namespaces (README). |
| Limitations | Packed or obfuscated programs, installers and packaged programs can give misleading or incomplete results, and capabilities split across wrapper or child functions are not matched (limitations guide). Matches indicate capability; they do not confirm behavior. |
| Requirements | Standalone builds for Linux, macOS and Windows, with the Linux build needing GLIBC 2.26+; the PyPI package omits the default rules; IDA, Ghidra and Binary Ninja integrations have their own version requirements (installation guide, plugin READMEs); Apache-2.0. |
| Classification | `kind: tool`; `relationship: foundation`, because its documentation establishes no REA connection; `category: native-analysis`. |
| Target rationale | `binary`: its documented inputs are executable modules, shellcode, sandbox reports on executables and files derived from them. The evidence supports no other target. |
| Decision | Curate as `capa`, `verified_at: 2026-10-19`. |

After the change, `scan-272815213` is byte-for-byte the same record, still `automated-readme-scan`. Its line in the [native-analysis directory](repositories/native-analysis.md) gains a “Curated: capa” link only because the curated `url` is the exact repository root. Nothing was installed or run; the curated requirements state that no samples were analyzed.
