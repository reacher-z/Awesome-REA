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

The validator accepts the category keys defined in `CATEGORIES` in [build_readme.py](../scripts/build_readme.py). It accepts exactly these `relationship` values from `RELATIONSHIPS` in the same file, shown with their English labels. REA here is the upstream [REA project](https://github.com/morluto/rea).

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

`added_at` orders the Atom feeds of curated resources and papers (`/feed.xml` and `/zh/feed.xml`); automated scan records have no feed. Set it to the UTC date the record is merged. The validator rejects malformed values and dates beyond the next UTC day, as for review dates. Records without it are left out of the feeds. Source review dates are snapshots; upstream requirements may change. GitHub file and directory evidence links (`/blob/`, `/tree/`) name the reviewed commit, so they keep showing the reviewed text, while `url` remains the moving project link. Resource and paper review dates allow at most the next UTC calendar day to accommodate reviewers ahead of UTC. Resource review timestamps retain an exact 24-hour allowance; publication and first-arXiv dates must not be in the future. A documentation link on `main` may describe functionality that is not in a released package; keep that distinction in the description or requirements.

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
| `evidence_urls` | Nonempty list of HTTPS URLs | Primary sources checked for the record |
| `metadata_notes` / `metadata_notes_zh` | Text | Notes on identifiers, dates, acceptance or artifacts |
| `kind` | `research` | Fixed value |
| `verified_at` | ISO date | Date of the bibliography review; at most one calendar day ahead of UTC for timezone differences |
| `added_at` | Optional `YYYY-MM-DD` | UTC date on which the paper first reached `main`; orders the Atom feeds, never a review or publication date |
| `verification` | `source-reviewed` | Fixed value; sources were checked, not reproduced |
| `runtime_tested` | `false` | Fixed value; reproduction results are not recorded |

`date_precision` states how much of the date a source verifies, and `publication_date` holds exactly that much: nothing for `year`, a month for `month`, a day for `day`. `year` is always recorded. `targets[0]` places the paper in one section of the READMEs and the paper directory; the agent-evaluation papers listed in `AGENT_EVALUATION_PAPERS` in [build_readme.py](../scripts/build_readme.py) form their own README section.

Search the bibliography with `python3 scripts/catalog.py --papers --target website`, add a query such as `interaction`, or use `--language zh` for Chinese output. `--json` returns matching source records for tools and agents. Paper search is separate from `--source-index` and the default curated-resource search.

The `protocol` target is available in curated, paper and source-index searches. It covers communication formats, exchanges and state, including hardware-bus protocols when those are the analysis subject. Multiple targets are allowed; paper `targets[0]` controls its single primary section. Supporting the target does not assign it to existing records. Scan classification engine 4 assigns it to new captures only from an explicit protocol-analysis signal; retained source records keep their stored labels, so generated source-index exports currently show it only through an exact curated cross-reference. See the [target guidance](../CONTRIBUTING.md#suggest-a-resource).

Paper DOI/arXiv fields may both be null only for a published conference or workshop paper matching an explicitly reviewed publisher identity profile. The USENIX Security and WOOT profiles bind a canonical presentation page to its final PDF, series, publication year and exact evidence URLs. Artifact identifiers stay in the artifact notes; they never replace a paper identifier. Citations and structured data omit unavailable identifiers. See the [paper contribution rules](../CONTRIBUTING.md#suggest-a-research-paper).

`source-index.json` contains the separate automated discovery index: 3,000 distinct repository READMEs were retrieved and hashed. It preserves collection queries, successful and failed counts, source URLs, README hashes, timestamps, metadata, and automatic topic labels. Retained upstream descriptions remain unchanged. Oversized new descriptions are omitted with length/SHA-256 evidence; historical source records are preserved. See the [scan method](../docs/source-scan.md).

The [repository locales](locales/README.md) provide derived English and Simplified Chinese descriptions for all 3,000 records. The website build combines these files with the source index and retains available upstream text as `description_original` in its generated data. New or changed source records also require locale updates. Translation helps browse the collection; it does not verify upstream claims or promote a record to `source-reviewed`.

Interactive search uses a generated `source-browser.json` projection containing only browsable records and the fields needed for search, cards, details and evidence annotations. Its order and values are checked against the complete generated `/source-index.json` export, whose URL, structure and downloadable evidence remain available. The projection is not the archival dataset; its metadata names the full export and records its SHA-256.

[source-scope.json](source-scope.json) records evidence-bound scope exclusions without deleting successful scans. The website and [bilingual GitHub directory](../docs/repositories/README.md) omit excluded records from browsing. The downloadable full index keeps all scan records and the exclusion reasons; the separate curated catalog contains only curated entries.

`case-coverage.json` is a separate inventory of entries in pinned upstream case collections. Its [English](../docs/case-coverage.md) and [Chinese](../docs/case-coverage.zh-CN.md) summaries distinguish collection occurrences, deduplicated report units, typed catalog matches, and unresolved project identities. A README scan does not establish case review or runtime reproduction. Regenerate the summaries with `python3 scripts/build_case_coverage.py`; catalog validation also checks the ledger and its mappings.
