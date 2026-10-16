# Resource catalog format

`rea-resources.json` and `tool-resources.json` contain the records rendered into both READMEs. They are arrays of objects with these required fields:

| Field | Meaning |
| --- | --- |
| `id` | Stable lowercase slug, unique across both files |
| `name` | Upstream project or resource name |
| `url` | Canonical public destination |
| `category` | Task or tool family |
| `targets` | One or more browsing domains: `website`, `game`, `app`, `binary`, `firmware`; these describe task fit, not verified REA integration |
| `relationship` | Relationship to REA, independent integration, foundation, or learning |
| `description_en` / `description_zh` | Original practical descriptions |
| `evidence_url` | Primary source supporting the description |
| `verified_at` | ISO date or timestamp of source review |
| `verification` | `source-reviewed`; not a runtime compatibility claim |
| `requirements` | Platform, engine, release, license, or input prerequisites |

Inspect available categories and relationships with `python3 scripts/catalog.py --json`. Source review dates are snapshots; upstream requirements may change. A documentation link on `main` may describe functionality that is not in a released package; keep that distinction in the description or requirements.

`benchmarks.json` is a separate repository comparison dataset. Star counts are observations at `observed_at`, not a live ranking, quality score, or predicted growth rate. The comparison notes explain the population and limitations.

`source-index.json` contains the separate automated discovery index: 1,600 distinct repository READMEs were retrieved and hashed. It preserves collection queries, successful and failed counts, source URLs, README hashes, timestamps, metadata, and automatic topic labels. Original upstream descriptions are retained in their source language; they are not editorial translations. See the [scan method](../docs/source-scan.md). These records are not promoted to `source-reviewed` by automation.
