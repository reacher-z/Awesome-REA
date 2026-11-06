# Automated discovery batches

[简体中文](#简体中文) · [Ingest workflow](../../docs/automation.md#automated-discovery-ingest) · [Scan method](../../docs/source-scan.md) · [Review worksheet](../../docs/promotion-worksheet.md)

This directory is the **unreviewed discovery queue**. Every file `run-<run id>-<attempt>.json` is one batch that the `Scheduled README discovery` workflow added after a scan, through a pull request that its own checks had to pass. The records are automated README scans, `verification: automated-readme-scan`, and every batch says `review_status: unreviewed`. Nobody has read their sources, translated them, curated them, run them or judged their quality. They are not part of the curated catalog, the reviewed [source index](../source-index.json) or the [public supplements](../source-supplements/README.md), and they are never counted as curated resources.

## What a batch holds

- `resources`: exact capture objects copied unchanged from the scan's validated checkpoint artifact, newest capture first. Nothing in them is rewritten, relabelled or upgraded; `record_sha256` fingerprints each object as the public supplements do.
- `source`: the scan run and attempt, the workflow, the scanner commit, the checkpoint artifact's name, ID and digest, and the SHA-256 of its checkpoint and receipt, with the receipt's capture and integrity counts. Checkpoint artifacts expire after seven days; the batch keeps the exact captures it selected.
- `selection`: the policy, the record limit, how many captures were eligible, the selected IDs in order and how many eligible captures were skipped for each reason.
- `ingested_at`: when the workflow prepared the batch. The website and its JSON give this as the time of the last successful ingest.

## Selection rules

A capture enters a batch only when all of these hold. They are this repository's own checks; no new admission rule is invented here.

1. It is a successful README read with an explicit Git blob hash match (`readme_git_sha_matches_content: true` and equal advertised and computed blob identifiers), the qualification that the scheduled scan's goal counts.
2. It passes the publication validator's record checks: scanner record schema, public non-fork non-archived repository, consistent URLs and README evidence, bounded description capture, valid automatic labels and timestamps.
3. It has at least one topic from the `strong-reverse-engineering-topics-v1` screen that the public supplements use (`reverse-engineering`, `binary-analysis`, `decompiler`, `ghidra`, `frida`, `firmware-analysis`, `protocol-analysis` and the others listed in [public_source_supplements.py](../../scripts/public_source_supplements.py)).
4. Its numeric ID is new to the source index (successes and failures), every public supplement batch, held or ready, and every earlier discovery batch.
5. It is not already a curated resource (exact repository URL), its repository name is not recorded under another numeric ID, its README SHA-256 is not already published by another record, and it raises no credential or personal-path finding.

Eligible captures are taken newest first, so a run's own new reads come before older checkpoint captures. A batch holds at most **300** records.

## Growth budget

Each batch is about 0.85 MB of JSON for 300 records and about 130 KB compressed in Git. The queue is capped at **25,000 records** and **64 MiB** of batch files in total, which bounds its Git history to roughly 10 MB compressed; raw checkpoints, which hold every capture, are never copied into the repository. When either limit is reached the ingest stops, the workflow fails and its tracking issue says so. Raising the budget, or retiring old batches, is a separate reviewed change to [discoveries.py](../../scripts/discoveries.py) and this page.

`python3 scripts/discoveries.py` validates every batch and prints the queue size, the budget and the last ingest time. `python3 scripts/validate.py` runs the same checks; the trusted pull-request review also checks that a pull request only adds batches, never edits or removes one, and that every record is new to the base branch's layers.

## Where the records appear

- The website lists the newest records at [/discoveries/](https://awesomerea.org/discoveries/) and [/zh/discoveries/](https://awesomerea.org/zh/discoveries/), labelled unreviewed, with upstream descriptions left untranslated.
- [/discoveries.json](https://awesomerea.org/discoveries.json) exports the listed records with `review_status: unreviewed`, batch provenance and README hashes; [/discoveries/status.json](https://awesomerea.org/discoveries/status.json) gives `last_successful_ingest_at`, and [/discoveries/badge.json](https://awesomerea.org/discoveries/badge.json) is a shields.io endpoint badge with that time.
- [/discoveries/feed.xml](https://awesomerea.org/discoveries/feed.xml) and its Chinese counterpart list the newest records; the main [/feed.xml](https://awesomerea.org/feed.xml) adds one summary entry per recent batch, in an `unreviewed-discovery` category. [llms.txt](https://awesomerea.org/llms.txt) links all of them.
- A record that later enters the reviewed repository index is counted there and no longer listed as a discovery. READMEs and the repository directory pages under docs/repositories/ do not list discoveries.

## Followed-source leads

The README scanner only sees GitHub repositories that its searches reach and that carry a strong reverse-engineering topic. Other reverse-engineering lists, registries and bibliographies list many more resources, including websites, books, courses and papers. The `Followed-source lead discovery` workflow ([discovery-leads.yml](../../.github/workflows/discovery-leads.yml)) follows the public sources registered in [discovery-sources.json](../discovery-sources.json) every hour and keeps what they list here as **leads**: `verification: automated-source-lead`, `review_status: unreviewed`. A listing by a secondary source is never evidence for curation ([AGENTS.md](../../AGENTS.md)); a lead only says where a resource was listed.

**Sources.** Each registry entry names its type, why it is followed and its scope rules:

| Type | What it reads | Evidence a listing pins |
| --- | --- | --- |
| `github-readme-list` | A list README at the default branch's current commit, verified against its Git blob ID; one item per list line (its first resolvable link) inside the in-scope sections | `https://github.com/<list>/blob/<commit>/<path>#L<line>` |
| `github-topic` | The most-starred public repositories carrying a topic, optionally screened by reverse-engineering terms | `https://github.com/topics/<topic>` |
| `github-json-registry` | Entries of a machine-readable registry file at a pinned commit (Binary Ninja `plugins.json`, the SubmitGame `games.json`) | `https://github.com/<repo>/blob/<commit>/<path>` |
| `github-directory` | One link per file of a registry directory at a pinned commit (the radare2-pm package database) | `https://github.com/<repo>/blob/<commit>/<path>/<file>` |
| `survey-references` | The bibliography of a curated survey's arXiv HTML page, identified through Semantic Scholar references | `https://arxiv.org/html/<id>v<n>#<entry>` |
| `arxiv-query` | The newest arXiv submissions matching a query | the exact `export.arxiv.org` query URL |
| `huggingface-search` | The most-downloaded Hugging Face models or datasets matching a term, without quantized re-uploads | the exact Hugging Face API query URL |

**Scope.** The registered rules decide what a source contributes: included and excluded sections, keyword screens, and item exclusions with reason codes from [CONTRIBUTING.md](../../CONTRIBUTING.md) (`security-testing`, `detection-only`, `forensics-only`, `development-tool`, `protection-tool`, `malware-samples`, `distribution-site`, `community-or-event`, `general-security`, `cheat-or-evasion`, `game-or-engine`, `linking-policy`, `unrelated`). Paper sources keep reverse-engineering subjects only (the `re-subject-v1` title screen). Under the linking policy, the SubmitGame registry contributes decompilations, disassemblies, engine remakes, source ports and tools, never static recompilations or browser-playable builds, and repositories that redistribute game data or commit recompiled commercial output are excluded by rule.

**Selection.** A candidate becomes a lead only when none of its identities is already held by the curated resources or papers, the source index and its failures, the public supplements, the README-scan batches, the scope exclusions, the case-coverage ledger or an earlier lead batch, and it raises no credential, personal-path or protected-name finding. GitHub repositories are resolved to their numeric ID first, so renames are not new; a repository that no longer exists or is private is skipped. A GitHub project page (`owner.github.io/<repo>`) counts as its repository, so the page of a curated or indexed repository is not a new lead. A web page that a source links for several differently named entries, such as a contest results page, becomes one lead per entry, keyed by the page plus `#<name>` (case-folded letters and digits of any script); an entry that an earlier batch already holds under the page's key alone is not added again. Sources take turns in registry order, at most **2,000** leads per run.

**Batch files** are `leads/<YYYY-MM>/leads-<run id>-<attempt>.json`, sharded by the month of collection, immutable once merged:

- `provenance`: the workflow run and attempt, its event, the collector commit and the SHA-256 of the registry it read.
- `sources`: every followed source of the run with its pinned evidence URL, revision, content SHA-256, `captured`, `error` (and the reason) or `not-due`, and how many links it listed and kept in scope.
- `selection`: the policy (`followed-source-leads-v1`), the record limit, the eligible and selected counts, the selected IDs in order, a SHA-256 per lead and how many candidates were skipped for each reason.
- `leads`: one record per resource.

**A lead** has these fields; the site exports them unchanged:

| Field | Meaning |
| --- | --- |
| `id` | `lead-` plus the first 24 hex digits of the identity's SHA-256 |
| `identity` | The primary key: `github:<repository ID>`, `huggingface:<model\|dataset>/<id>`, `arxiv:<id>`, `doi:<doi>`, `url:<host><path>`, a code-host or video key (`gl:`, `sf:`, `yt:` …), or `title:<normalized title>` for a paper without an identifier |
| `aliases` | Other keys of the same resource (`gh:<owner>/<repo>`, a former name, a title or DOI), used to keep it unique |
| `url` | The canonical link: the GitHub repository, the arXiv or DOI page, or the listed URL |
| `name` | The listing's link label or the paper title, at most 200 characters |
| `kind_hint` | A catalog kind guessed from the listing section (`tool`, `case-study`, `research`, `learning-resource` …), not a review |
| `listings` | Up to 12 sources that list it: `source_id`, `section`, `label` and the pinned `evidence_url` |
| `github` | For a repository: numeric `id`, `full_name`, upstream `description` (at most 300 characters, untranslated), `topics`, `stars`, `pushed_at`, `archived`, `fork`, `parent`, `license`, `homepage`, all as observed |
| `paper` | For a paper: `title`, `year`, `venue`, `arxiv_id`, `doi`, `semantic_scholar_id` where known; no author lists |
| `huggingface` | For a Hugging Face repository: `repo_type`, `id`, `downloads`, `likes`, `last_modified` |
| `observed_at`, `verification`, `review_status` | When it was collected, `automated-source-lead`, `unreviewed` |

**Budget.** The lead queue is capped at **30,000 leads** and **48 MiB** of batch files. The first collection of the registered sources (2026-11-05) yields about 5,600 leads in three runs, about 8 MB of batch files and about 1.5 MB compressed in Git; later runs add only what the sources newly list. At either limit the ingest stops and its tracking issue says so; raising the budget is a reviewed change to [discovery_leads.py](../../scripts/discovery_leads.py) and this page.

`python3 scripts/discovery_leads.py` validates the registry and every lead batch and prints the queue size; `python3 scripts/validate.py` runs the same checks, and the trusted pull-request review accepts lead batches only from the workflow's own pull request. [/discoveries/leads.json](https://awesomerea.org/discoveries/leads.json) exports the newest 1,000 listed leads with batch provenance, and `/discoveries/leads/<batch>.json` every listed lead of a batch; a lead that another layer has since taken up is counted there, not listed. Curating a lead follows the [review worksheet](../../docs/promotion-worksheet.md) like any other discovery.

## Curating a discovery

Follow the [review worksheet](../../docs/promotion-worksheet.md) exactly as for a source-index record: review the project's own sources, pin the evidence, and add a separate curated record. The batch file is never edited; once the curated record exists, the repository leaves the discovery list, matched by its exact URL.

## Review decisions

[data/discovery-reviews.json](../discovery-reviews.json) records what a reviewer decided about a discovery that was not curated, keyed by scan ID: `decision` (`exclude` or `hold`), `reason_code`, `reason_en`, `reason_zh`, the `readme_sha256` of the scan it reviews, a pinned `evidence_url`, `reviewed_at` and, for a duplicate, `duplicate_of`. [discovery_reviews.py](../../scripts/discovery_reviews.py) holds the reason codes and validates each decision against its batch. `exclude` means the primary source shows the repository does not belong; `hold` means it may belong, and the reason names the missing evidence or the maintainer decision it needs.

A decided record leaves the unreviewed list, feeds and exports, and appears in [/discoveries/reviews.json](https://awesomerea.org/discoveries/reviews.json) with its reason. Its batch file does not change, so the scheduled ingest and the lead collector, which treat every batch ID as already held, do not queue it again. To reverse a decision, edit its entry or remove it.

## 简体中文

本目录是**未审核的发现队列**。每个 `run-<运行 ID>-<尝试次数>.json` 文件是一批由 `Scheduled README discovery` 工作流在扫描后通过拉取请求加入的记录，该请求必须先通过仓库自身的检查。记录均为自动 README 扫描结果（`verification: automated-readme-scan`），每批都标明 `review_status: unreviewed`：没有人阅读过其来源，也没有翻译、精选、运行或评估质量。它们不属于精选目录、已审核的来源索引或公开补充批次，也从不计入精选资源数量。

入选条件沿用本仓库已有的规则：README 读取成功且 Git blob 哈希明确匹配；通过发布校验器的记录检查；至少带有一个 `strong-reverse-engineering-topics-v1` 筛选中的主题；数字 ID 不在来源索引、任何公开补充批次和更早的发现批次中；不是已精选的仓库，仓库名未被另一个数字 ID 占用，README 哈希未被其他记录发布，且没有凭据或个人路径特征。按采集时间从新到旧选取，每批最多 300 条，采集对象原样复制，不做任何改写或升级。

每批 300 条约 0.85 MB，在 Git 中压缩后约 130 KB。队列总量上限为 **25,000 条**、批次文件合计 **64 MiB**，Git 历史因此增长约 10 MB；原始 checkpoint 不会写入仓库。达到上限后入库停止，工作流失败并在追踪 issue 中说明；提高上限或归档旧批次需要单独审核。

网站在 [/zh/discoveries/](https://awesomerea.org/zh/discoveries/) 列出最新记录并标注“未审核”，简介保留上游原文、不翻译；[/discoveries.json](https://awesomerea.org/discoveries.json)、状态文件、Atom 订阅和 llms.txt 同样标明未审核。收录某个发现时，请按[审核工作表](../../docs/promotion-worksheet.zh-CN.md)另写一条精选记录，批次文件保持不变。

### 审核决定

[data/discovery-reviews.json](../discovery-reviews.json) 按扫描 ID 记录审核者对未收录发现的决定：`decision`（`exclude` 排除或 `hold` 暂缓）、`reason_code`、中英文理由、所审扫描的 `readme_sha256`、固定到提交的 `evidence_url`、`reviewed_at`，重复项另有 `duplicate_of`。已决定的记录离开未审核列表、订阅和导出，连同理由出现在 [/discoveries/reviews.json](https://awesomerea.org/discoveries/reviews.json)。批次文件不变，定时入库和线索收集会把批次中的 ID 视为已有，因此不会再次排入队列。已收录的仓库按 URL 精确匹配后自动离开列表。

### 外部来源线索

README 扫描只能看到它的搜索能触达、且带有明确逆向工程主题的 GitHub 仓库。其他逆向工程列表、注册表和综述参考文献还列出了更多资源，包括网站、书籍、课程和论文。`Followed-source lead discovery` 工作流每小时读取 [discovery-sources.json](../discovery-sources.json) 中登记的公开来源，把它们列出的条目作为**线索**保存在 `leads/<年-月>/leads-<运行 ID>-<尝试次数>.json`：`verification: automated-source-lead`，`review_status: unreviewed`。被二手来源列出从来不是收录证据；线索只说明资源在哪里被列出。每个来源都登记了类型、跟踪理由和范围规则（纳入与排除的章节、关键词筛选、带 CONTRIBUTING.md 原因代码的条目排除；论文来源只保留逆向工程主题）。按链接政策，SubmitGame 注册表只贡献反编译、反汇编、引擎重制、源码移植和工具，不含静态重编译和可在浏览器中游玩的构建。

候选条目的任一身份已存在于精选资源或论文、来源索引及其失败记录、公开补充批次、README 扫描批次、范围排除、案例覆盖台账或更早的线索批次中时不会入选；GitHub 仓库先解析为数字 ID，改名不算新条目，已不存在或私有的仓库会被跳过；含凭据、个人路径或受保护姓名的条目不收。各来源按登记顺序轮流入选，每次运行最多 **2,000** 条。每条线索记录身份键、别名、规范链接、名称、按章节推测的类型（不是审核结论）、最多 12 个列出它的来源及固定到具体提交的证据链接，以及 GitHub、论文或 Hugging Face 的元数据快照（不含作者列表）。线索队列上限为 **30,000 条**、**48 MiB**；首次收集（2026-11-05）约 5,600 条、分三次入库，批次文件约 8 MB，Git 中压缩后约 1.5 MB。网站在 [/discoveries/leads.json](https://awesomerea.org/discoveries/leads.json) 导出最新 1,000 条并按批次导出全部，均标明未审核。收录某条线索同样需要按审核工作表另写一条精选记录。
