# Software evidence scores

[简体中文](quality-scoring.zh-CN.md) · [Data format](../data/README.md#quality-evidence-and-scores) · [Score directory](https://awesomerea.org/quality/)

The catalog now carries a comparable **evidence score** for every catalogued software entry. The score answers one narrow question: how much of the nine evaluation areas in the project's software-testing guide is supported by public, reproducible evidence? It is not a runtime test result, a completeness percentage or a product-quality estimate.

## What is scored

Every catalog record whose `kind` is `tool`, `case-study`, `integration` or `project` is scored. Documentation, collections, learning resources and research records are out of scope. The score is generated only from the catalog plus the committed evidence snapshot; there is no per-entry override.

The nine dimensions are equal-weight chapters from the evaluation guide:

| Dimension | Evidence checked |
| --- | --- |
| Functional coverage | Feature documentation, usage examples, documentation depth, demo media, stated scope and limitations |
| Correctness | Test paths, tests run in CI, testing notes, fuzz/property checks, fixtures or golden data |
| Performance and capacity | Benchmark code, measured figures, profiling and numeric budgets |
| User isolation and secrets | Security policy, authorization or tenant evidence, secret and dependency handling, scanners |
| UI consistency | Screenshots or demo media, UI/visual tests, accessibility evidence, interface guidance |
| Persistence and recovery | Persistence or recovery evidence, storage or migration layer, failure handling, recovery documentation |
| Concurrency and consistency | Concurrency evidence, consistency model, load or stress evidence |
| File formats and compatibility | Import/export evidence, format validators, format fixtures, round-trip or consumer checks |
| Reproducibility and reliability | License, build manifest, lockfile, CI, install instructions, versioned release, distributable artifact, maintenance state |

A dimension that does not apply is excluded rather than counted as zero. For example, a command-line binary parser does not get a UI score, and a single-user desktop editor does not get a multi-user isolation score.

## How a score is calculated

Each check is `pass` (1), `partial` (0.5) or `missing` (0). A dimension is the mean of its checks. The total is the equal-weight mean of the applicable dimensions:

```
score = 100 × mean(applicable dimension scores)
```

The output also reports:

- `coverage`: the share of applicable checks that have any evidence (pass or partial).
- `dimension_coverage`: the share of applicable dimensions at 50 or above.
- `confidence`: `high` when a complete README and repository tree were observed; lower when the source is partial or page-only.
- `band`: `strong-evidence`, `moderate-evidence`, `limited-evidence`, `minimal-evidence` or `ungraded`.

An entry with no observable source is `ungraded` with a `null` score, never zero. A README claim or a test directory proves that evidence exists; it does not prove that a feature works or that the tests pass.

## Data files

- [`data/quality-evidence.json`](../data/quality-evidence.json) is the dated public-source snapshot.
- [`data/quality-evaluations.json`](../data/quality-evaluations.json) is generated from that snapshot and must not be edited by hand.
- [`scripts/collect_quality_evidence.py`](../scripts/collect_quality_evidence.py) refreshes the snapshot.
- [`scripts/quality_scoring.py`](../scripts/quality_scoring.py) recomputes every score offline.
- [`scripts/validate_quality_scoring.py`](../scripts/validate_quality_scoring.py) recomputes the scores and rejects hand edits.
- [`scripts/build_quality_pages.py`](../scripts/build_quality_pages.py) builds the bilingual `/quality/` directory.

## Regenerate

```sh
python3 scripts/collect_quality_evidence.py --all
python3 scripts/quality_scoring.py --all
python3 scripts/validate_quality_scoring.py
python3 scripts/build_site.py
```

The collector reads public GitHub metadata, README text, repository trees, release assets and up to two CI workflow files. Non-GitHub entries are read from their public page. It sends a token only to `api.github.com`, never downloads or runs an executable, bounds response sizes, and caches raw responses under the ignored `.cache/quality-evidence/` directory.

The snapshot records the reviewed ref, README bytes and SHA-256, the tree SHA, release asset names and the observation time. A truncated tree is recorded as truncated; a missing path is treated as absent evidence, not as proof that the practice is absent.

## Limits

- Public evidence can be incomplete, stale or marketing copy.
- The scorer cannot observe a feature, compare output with a reference implementation, measure performance or test authorization.
- A repository with a polished README can score above a less documented project that works better.
- The score is a reading of evidence coverage, not a ranking of software quality.

A later phase adds a separate measured score from downloaded artifacts and rule packs. That score will be reported separately and will not change the evidence score retroactively.

## Related

- The project's software-recreation quality evaluation guide (`软件复刻质量评测工具.md`), whose nine chapters the dimensions follow
- [Catalog format](../data/README.md)
- [Website maintenance](website.md)
