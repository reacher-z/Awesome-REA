# Documentation

[简体中文](README.zh-CN.md) · [Collection README](../README.md)

Guides describe the current process. Research notes are dated snapshots, kept for their evidence and reasoning; their counts and plans are not current catalog statistics. For current totals, use the [README Contents](../README.md#contents) counts or `python3 scripts/catalog.py`.

## Contributing and data

| Document | Language | Status | Covers |
| --- | --- | --- | --- |
| [Contribution guide](../CONTRIBUTING.md) | English | Current, authoritative | Suggestions, catalog fields, papers, validation and review |
| [Chinese contribution quick start](../CONTRIBUTING.zh-CN.md) | Chinese | Current summary | Main contribution rules and the Chinese terminology glossary |
| First resource walkthrough: [English](first-resource.md), [Chinese](first-resource.zh-CN.md) | English, Chinese | Current | One existing record traced through each edited and generated file, checks and the pull request |
| [Security policy](../SECURITY.md) | English, with a Chinese summary | Current | Private reporting of security problems |
| Paper update guide: [English](paper-updates.md), [Chinese](paper-updates.zh-CN.md) | English, Chinese | Current | Updating a preprint record in place after acceptance or publication, with a worked example |
| [Catalog format](../data/README.md) | English | Current | Curated, paper, benchmark, scan and case-coverage data |
| Artifact and license evidence: [English](artifact-evidence.md), [Chinese](artifact-evidence.zh-CN.md) | English, Chinese | Current | Wording for unavailable, gated or demo-only artifacts, version differences and conflicting licenses |
| [Repository locales](../data/locales/README.md) | English | Current | English and Chinese descriptions of scanned repositories |
| Index-to-curated review worksheet: [English](promotion-worksheet.md), [Chinese](promotion-worksheet.zh-CN.md) | English, Chinese | Current | Tracing a scanned repository to a curated record or a hold, with a completed example |

## Maintenance guides

| Document | Language | Status | Covers |
| --- | --- | --- | --- |
| [Repository automation](automation.md) | English | Current | Pull request review and CI |
| [Website maintenance](website.md) | English | Current | Site build, preview and hosting |
| [Search discovery](search-discovery.md) | English | Current | Search and answer-engine discovery, submission and limits |
| [Community outreach](community-outreach.md) | English | Current, rules reviewed 2026-10-20 | Checklist for posting to public communities such as Hacker News and Reddit |
| [Discovery observations](discovery/README.md) | English | Current | Versioned queries and a manual observation template |
| [Source scan method](source-scan.md) | English | Current | How the automated repository index is collected |
| Case coverage: [English](case-coverage.md), [Chinese](case-coverage.zh-CN.md) | English, Chinese | Generated | Inventory of pinned upstream case collections |
| Scanned repository index: [English](repositories/README.md), [Chinese](repositories/README.zh-CN.md) | English, Chinese | Generated | Repository index by category |
| [Collection roadmap](roadmap.md) | English | Current | Collection priorities |

## Launch research snapshots

These Chinese-only notes record research from the collection's launch on 2026-10-15 and 2026-10-16. They stay public as archived notes because the catalog format guide refers to the benchmark study, and they keep their evidence links. They are not maintained as current statistics.

| Document | Language | Status | Covers |
| --- | --- | --- | --- |
| [REA ecosystem study](rea-ecosystem.zh-CN.md) | Chinese | Snapshot, collected 2026-10-15 | First review of 25 REA-related records, similar catalogs and proposed tutorials |
| [Tools by task](tool-landscape.zh-CN.md) | Chinese | Snapshot, first review 2026-10-15 | Selection notes for the 47 first-round tool records and 8 launch additions |
| [Benchmark study and first-month plan](benchmark-research.zh-CN.md) | Chinese | Snapshot, observed 2026-10-16 UTC | Comparison of 19 repositories, and the launch plan and Star target |

The benchmark study explains [benchmarks.json](../data/benchmarks.json): one GitHub REST API observation of 19 repositories (2 designated anchors and 17 comparison repositories) between 2026-10-16T00:47:46Z and 00:47:48Z. The repositories were chosen deliberately to cover high-profile references and direct neighbors, not sampled at random, so the data supports neither causal comparisons nor growth estimates. Its Star target and 30-day plan are archived launch proposals, not forecasts or the current plan; current priorities are in the roadmap.
