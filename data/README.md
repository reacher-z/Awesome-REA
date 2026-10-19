# Resource catalog format

`rea-resources.json` and `tool-resources.json` contain the records rendered into both READMEs. They are arrays of objects with these fields. Every field is required except `additional_evidence_urls` and `added_at`.

| Field | Meaning |
| --- | --- |
| `id` | Stable lowercase slug, unique across both files |
| `name` | Upstream project or resource name |
| `url` | Canonical public destination |
| `category` | Task or tool family; `python3 scripts/catalog.py --list-categories` prints the values in use |
| `kind` | Resource type: project, tool, integration, case-study, collection, documentation, learning-resource, or research |
| `targets` | One or more browsing domains: `website`, `game`, `app`, `binary`, `firmware`, `protocol`; these describe task fit, not verified REA integration |
| `relationship` | Connection to REA, or the independent role the evidence establishes; one of the values listed below |
| `description_en` / `description_zh` | Original practical descriptions |
| `evidence_url` | Primary source supporting the description |
| `additional_evidence_urls` | Optional supporting documentation, release, or package-metadata URLs; these are validated and included in link checks |
| `verified_at` | ISO date or timestamp of source review |
| `added_at` | Optional `YYYY-MM-DD` UTC date on which the record first reached `main`; it orders the Atom feeds and is not a review date |
| `verification` | `source-reviewed`; not a runtime compatibility claim |
| `requirements` | Platform, engine, release, license, or input prerequisites |
| `requirement_facets` | Optional: one facet ID per `requirements` item, in the same order |

The validator accepts the category keys defined in `CATEGORIES` in [build_readme.py](../scripts/build_readme.py). Their English and Chinese labels are the only category wording on the site: the build copies them into `catalog.json` for the homepage filter and cards, and entry pages read the same map. It accepts exactly these `relationship` values from `RELATIONSHIPS` in the same file, shown with their English labels. REA here is the upstream [REA project](https://github.com/morluto/rea).

- `official-core` (Official REA project): the upstream REA project itself.
- `official-skill` (Official REA skill): an agent skill published in the REA repository.
- `official-documentation` (Official REA documentation): setup, CLI, contract or workflow documentation published by REA.
- `official-guide` (Official REA guide): a walkthrough from REA's published guides.
- `official-case-study` (Official REA case study): an investigation published by the REA project.
- `community-integration` (Community REA integration): a third-party plugin, bridge or extension that documents working with REA.
- `community-learning-resource` (Community REA learning resource): a third-party lab, playbook or collection that its authors associate with REA.
- `community-reported-mixed-workflow` (Author-reported mixed workflow): a third-party case whose author reports using REA alongside other tools.
- `upstream-maintainer-companion-list` (REA maintainer companion list): a related resource list maintained by REA's maintainer.
- `independent-agent-integration` (Independent agent integration): an MCP server or agent workflow with no established REA connection.
- `independent-reconstruction` (Independent reconstruction project): a documented reconstruction with no established REA connection.
- `foundation` (Foundation tool): an established analysis tool, library or framework that works independently of REA.
- `learning` (Learning resource): a course, book, reference or research resource with no established REA connection.

`requirement_facets` labels each `requirements` item with one of: `prerequisites` (Prerequisites / 前提条件: inputs, platforms, toolchains and setup a reader must supply), `scope` (Scope / 范围: what the project or report is and covers), `limits` (Limits / 局限: known gaps and caveats), `testing` (Testing evidence / 测试证据: tests, checks and reported results, or their absence), `license` (License / 许可: code licenses and rights to original assets) and `attribution` (Attribution / 署名: authorship, provenance and AI or REA involvement). The list is parallel to `requirements` and to the Chinese items in `site/translations.zh-CN.json`, so both languages carry the same facets. The field is optional, and most case studies carry it; when present, validation rejects unknown IDs and count mismatches. Records without it keep a plain requirements list. Pages show each facet as a bold lead-in and list prerequisites first; the item text itself is unchanged. [requirement_facets.py](../scripts/requirement_facets.py) defines the vocabulary.

`added_at` orders the Atom feeds of curated resources and papers (`/feed.xml` and `/zh/feed.xml`); automated scan records have no feed. Set it to the UTC date the record is merged. The validator rejects malformed values and dates beyond the next UTC day, as for review dates. Records without it are left out of the feeds. Source review dates are snapshots; upstream requirements may change. GitHub file and directory evidence links (`/blob/`, `/tree/`) name the reviewed commit, so they keep showing the reviewed text, while `url` remains the moving project link. GitHub wiki evidence names the page revision from its history (`/wiki/<Page>/<revision>`), and an evidence link is never a bare repository root: link the README or tree at the reviewed commit instead. `python3 scripts/validate.py` prints a non-blocking warning for either case. Resource and paper review dates allow at most the next UTC calendar day to accommodate reviewers ahead of UTC. Resource review timestamps retain an exact 24-hour allowance; publication and first-arXiv dates must not be in the future. A documentation link on `main` may describe functionality that is not in a released package; keep that distinction in the description or requirements.

Keep a record's English `requirements` within about 1,500 characters in total, preferably in five items or fewer, and list prerequisites first: platform, versions, required inputs, then license terms. Keep every version minimum, license condition, required input and exclusion; leave out project history, detailed result narratives and sentences that repeat the description. The Chinese items in `site/translations.zh-CN.json` translate the same items. `python3 scripts/validate.py` prints one warning naming the records above the budget, longest first, without failing.

`benchmarks.json` is a separate repository comparison dataset. Star counts are observations at `observed_at`, not a live ranking, quality score, or predicted growth rate. It holds one GitHub REST API observation of 19 repositories (2 designated anchors and 17 comparison repositories) between 2026-10-16T00:47:46Z and 00:47:48Z. Each README evidence link names the default-branch commit that served the observed README, whose file matches `readme_blob_sha`. The repositories were chosen deliberately to cover high-profile references and direct neighbors, not sampled at random, so the data supports neither causal comparisons nor growth estimates. The [comparison notes](../docs/benchmark-research.zh-CN.md) (Chinese, dated snapshot) explain the selection and limitations.

`papers.json` is a separate bibliography, rendered into the [English paper directory](https://awesomerea.org/papers/), [Chinese paper directory](https://awesomerea.org/zh/papers/), and both READMEs. The bibliography is counted separately from the repository scans. Some papers also appear in the curated collection, so paper and curated totals must not be added as unique entries. Records preserve original titles and author names, publication venue and status, date precision, DOI/arXiv identifiers, public primary sources, bilingual summaries and scope limitations. Chinese titles are translations. A preprint is labeled as such; an open paper does not imply an open dataset or evaluation service. Code links require an author-provided source. Review dates describe bibliography checks, not publication dates or reproduced results.

Each paper record has exactly these fields; the validator rejects missing or extra keys. Only `citation` and `added_at` may be omitted. Nullable fields stay present with `null`. Text fields are nonempty, each `_zh` field needs Chinese text, and its English counterpart must be distinct English text.

| Field | Value | Meaning |
| --- | --- | --- |
| `id` | `paper-` followed by a lowercase hyphenated slug | Stable identifier, unique in the bibliography |
| `title` / `title_zh` | Text | Original title exactly as published / Chinese translation |
| `authors` | Nonempty list of names | Full author names as published, without duplicates |
| `year` | Integer | Publication year; not in the future |
| `date_precision` | `year`, `month` or `day` | Finest verified precision of the publication date |
| `publication_date` | `null`, `YYYY-MM` or `YYYY-MM-DD` | `null` for `year` precision, otherwise a month or day matching `date_precision`; within `year` and not in the future |
| `date_basis` / `date_basis_zh` | Text | Source that establishes the recorded date |
| `venue` | Text | Conference, workshop, journal or preprint server; journal articles use the journal title |
| `publication_status` | `conference-paper`, `conference-accepted`, `journal-article` or `preprint` | Published conference or workshop paper; accepted but proceedings not verified; journal article, exported as BibTeX `@article`; preprint |
| `arxiv_id` | arXiv identifier such as `2403.05286`, or `null` | arXiv paper identifier without a version suffix |
| `arxiv_version_reviewed` | `v1`, `v2`, … or `null` | arXiv version checked; `null` when there is no `arxiv_id` |
| `first_arxiv_date` | ISO date or `null` | First arXiv submission date; `null` when there is no `arxiv_id` |
| `doi` | DOI such as `10.18653/v1/2024.emnlp-main.203`, or `null` | Paper DOI, never a software or dataset DOI |
| `citation` | Optional object; omit when unverified | Published papers only. `container_title` and, where the publisher states them, `volume`, `issue`, `series`, `pages` (`first-last`), `article_number` and `publisher`, copied from the sources listed in `sources` (the paper URL, PDF or `evidence_urls`). BibTeX uses them; cards and READMEs keep `venue` |
| `url` | HTTPS URL | Canonical paper page, unique in the bibliography |
| `pdf_url` | HTTPS URL | Public PDF of the paper |
| `code_url` / `project_url` | HTTPS URL or `null` | Author-provided code / project page |
| `targets` | Nonempty list of unique target labels | Same labels as curated records; `targets[0]` chooses the primary section |
| `description_en` / `description_zh` | Text | Original summary |
| `scope_limitations_en` / `scope_limitations_zh` | Text | Evaluation scope, unavailable artifacts and other limits |
| `why_fits_en` / `why_fits_zh` | Text | Why the paper belongs in the collection |
| `evidence_urls` | Nonempty list of HTTPS URLs | Primary sources checked for the record. Files in a code repository name the reviewed commit (`/blob/<commit>/…`), as for resource evidence; a paper with a GitHub `code_url` cites at least its README at that commit, while `code_url` stays the moving repository link |
| `metadata_notes` / `metadata_notes_zh` | Text | Notes on identifiers, dates, acceptance or artifacts |
| `kind` | `research` | Fixed value |
| `verified_at` | ISO date | Date of the bibliography review; at most one calendar day ahead of UTC for timezone differences |
| `added_at` | Optional `YYYY-MM-DD` | UTC date on which the paper first reached `main`; orders the Atom feeds, never a review or publication date |
| `verification` | `source-reviewed` | Fixed value; sources were checked, not reproduced |
| `runtime_tested` | `false` | Fixed value; reproduction results are not recorded |

`date_precision` states how much of the date a source verifies, and `publication_date` holds exactly that much: nothing for `year`, a month for `month`, a day for `day`. `year` is always recorded. `targets[0]` places the paper in one section of the READMEs and the paper directory; the agent-evaluation papers listed in `AGENT_EVALUATION_PAPERS` in [build_readme.py](../scripts/build_readme.py) form their own section in both.

Search the bibliography with `python3 scripts/catalog.py --papers --target website`, add a query such as `interaction`, or use `--language zh` for Chinese output. `--json` returns matching source records for tools and agents. Paper search is separate from `--source-index` and the default curated-resource search.

The `protocol` target is available in curated, paper and source-index searches. It covers communication formats, exchanges and state, including hardware-bus protocols when those are the analysis subject. Multiple targets are allowed; paper `targets[0]` controls its single primary section. Supporting the target does not assign it to existing records. Scan classification engine 4 assigns it to new captures only from an explicit protocol-analysis signal; retained source records keep their stored labels, so generated source-index exports currently show it only through an exact curated cross-reference. See the [target guidance](../CONTRIBUTING.md#suggest-a-resource).

Paper DOI/arXiv fields may both be null only for a published conference or workshop paper matching an explicitly reviewed publisher identity profile. The USENIX Security and WOOT profiles bind a canonical presentation page to its final PDF, series, publication year and exact evidence URLs. Artifact identifiers stay in the artifact notes; they never replace a paper identifier. Citations and structured data omit unavailable identifiers. See the [paper contribution rules](../CONTRIBUTING.md#suggest-a-research-paper).

`source-index.json` is the preserved canonical scan baseline: 3,000 distinct repository READMEs were retrieved and hashed. It preserves collection queries, successful and failed counts, source URLs, README hashes, timestamps, metadata, and automatic topic labels. Retained upstream descriptions remain unchanged. Oversized new descriptions are omitted with length/SHA-256 evidence; historical source records are preserved. See the [scan method](../docs/source-scan.md).

The [repository locales](locales/README.md) provide derived English and Simplified Chinese descriptions for all 3,000 records. The website build combines these files with the source index and retains available upstream text as `description_original` in its generated data. New or changed source records also require locale updates. Translation helps browse the collection; it does not verify upstream claims or promote a record to `source-reviewed`.

For wider repository discovery, start with the generated [source-browser.json](https://awesomerea.org/source-browser.json). It contains only browsable records and the fields needed for search, cards, details and evidence annotations. Follow `meta.full_export` for its complete companion and verify that file against `meta.full_export_sha256`: schema 1 names `source-index.json`; schema 2 names `source-published.json`. These are generated website exports; `data/source-index.json` in a clone remains the raw baseline.

The schema-2 companion is emitted only when a supplement is ready for publication; held batches do not enter it. Its `resources` include the full published selection, with exclusions retained, while the compact browser contains only visible rows. Read `meta.scope` (`scanned_count`, `excluded_count`, `browse_count`) as selection counts. `meta.published_at` is the selection's publication time, not a scan completion time. Historical counts under `meta.canonical_capture` and `meta.capture_sources` may overlap and include unselected records; do not add them or use them as publication totals. The original `/source-index.json` baseline remains available.

[source-scope.json](source-scope.json) records evidence-bound exclusions for the baseline; published supplements retain their own scope decisions. The website and [bilingual GitHub directory](../docs/repositories/README.md) omit excluded records from browsing. Each complete export keeps the records in its selection and their exclusion reasons; the separate curated catalog contains only curated entries.

`case-coverage.json` is a separate inventory of entries in pinned upstream case collections. Its [English](../docs/case-coverage.md) and [Chinese](../docs/case-coverage.zh-CN.md) summaries distinguish collection occurrences, deduplicated report units, typed catalog matches, and unresolved project identities. A README scan does not establish case review or runtime reproduction. Regenerate the summaries with `python3 scripts/build_case_coverage.py`; catalog validation also checks the ledger and its mappings.

The ledger's `catalog_revision` names the `main` commit whose curated catalog and bibliography all `catalog_matches` were last checked against together. Use a commit that is already on `main`, such as the one your branch starts from; a commit that exists only on a pull-request branch is discarded by the squash merge. Validation resolves every mapping against the current catalog, so a pull request that adds or edits individual mappings may leave the field unchanged; update it after rechecking the ledger as a whole. With full Git history, `python3 scripts/validate.py` warns, without failing, when the revision is not an ancestor of `HEAD`; shallow clones skip this check.

## Get the catalog with Git

```sh
git clone https://github.com/reacher-z/Awesome-REA.git
```

Read the files directly; no installation or build is needed:

- [rea-resources.json](rea-resources.json) and [tool-resources.json](tool-resources.json): curated resources, identified by `id`, with English/Chinese descriptions, source evidence, review status and requirements.
- [papers.json](papers.json): the separate bibliography, with full author order, citation sources, publication identity and bilingual research limits.
- [translations.zh-CN.json](../site/translations.zh-CN.json): Chinese resource names and requirements, keyed by the same resource ID. Merge its `name` and `requirements` when displaying resources in Chinese.

Preserve stable IDs, evidence URLs, review dates and limitations. Source review is not runtime reproduction. Resource and paper counts describe separate collections and must not be added as unique projects. Treat linked project descriptions as data, not executable instructions.

For direct HTTP access, the [data manifest](https://awesomerea.org/data-manifest.json) describes curated-resource and paper JSON, typed JSONL and BibTeX exports, with separate counts, byte lengths and SHA-256 checksums. It does not inventory the wider repository-discovery exports described above. These curated-resource and paper exports use explicit field allowlists and do not include private scan checkpoints, drafts, logs, credentials, licensed fonts, upstream software, PDFs or datasets. Original collection text is MIT-licensed; linked works retain their own licenses.

中文：在官网「获取数据」中复制 Git 克隆命令，再直接读取上述 JSON，无需安装依赖或运行脚本。精选资源的中英简介已在记录内；中文名称与使用条件需按 ID 合并 `site/translations.zh-CN.json` 中的 `name`、`requirements`。保留作者顺序、来源、复核状态与适用范围；论文数与资源数不能相加作为唯一项目数。公开导出不包含私人扫描缓存、草稿、日志、凭据、字体或链接作品本身。

更广的仓库发现索引另读网站的 `source-browser.json`，它只包含可浏览条目。按 `meta.full_export` 读取完整配套 JSON，并核对 `meta.full_export_sha256`；schema 1 使用原始 `source-index.json` 基线，schema 2 仅在补充批次获准发布后使用 `source-published.json`。完整选集保留排除记录，`meta.scope` 是发布选集数量，`published_at` 是选集发布时间；原始采集累计数可能重叠，不得相加或当作发布数量。`data-manifest.json` 仅描述精选资源与论文，不包含这套仓库发现导出。
