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

Each batch is about 0.85 MB of JSON for 300 records and about 130 KB compressed in Git. The queue is capped at **25,000 records** and **64 MiB** of batch files in total, which bounds its Git history to roughly 10 MB compressed; raw checkpoints, which grow toward 160,000 captures, are never copied into the repository. When either limit is reached the ingest stops, the workflow fails and its tracking issue says so. Raising the budget, or retiring old batches, is a separate reviewed change to [discoveries.py](../../scripts/discoveries.py) and this page.

`python3 scripts/discoveries.py` validates every batch and prints the queue size, the budget and the last ingest time. `python3 scripts/validate.py` runs the same checks; the trusted pull-request review also checks that a pull request only adds batches, never edits or removes one, and that every record is new to the base branch's layers.

## Where the records appear

- The website lists the newest records at [/discoveries/](https://awesomerea.org/discoveries/) and [/zh/discoveries/](https://awesomerea.org/zh/discoveries/), labelled unreviewed, with upstream descriptions left untranslated.
- [/discoveries.json](https://awesomerea.org/discoveries.json) exports the listed records with `review_status: unreviewed`, batch provenance and README hashes; [/discoveries/status.json](https://awesomerea.org/discoveries/status.json) gives `last_successful_ingest_at`, and [/discoveries/badge.json](https://awesomerea.org/discoveries/badge.json) is a shields.io endpoint badge with that time.
- [/discoveries/feed.xml](https://awesomerea.org/discoveries/feed.xml) and its Chinese counterpart list the newest records; the main [/feed.xml](https://awesomerea.org/feed.xml) adds one summary entry per recent batch, in an `unreviewed-discovery` category. [llms.txt](https://awesomerea.org/llms.txt) links all of them.
- A record that later enters the reviewed repository index is counted there and no longer listed as a discovery. READMEs and the repository directory pages under docs/repositories/ do not list discoveries.

## Curating a discovery

Follow the [review worksheet](../../docs/promotion-worksheet.md) exactly as for a source-index record: review the project's own sources, pin the evidence, and add a separate curated record. The batch file is never edited; once the curated record exists, the discovery list links it.

## 简体中文

本目录是**未审核的发现队列**。每个 `run-<运行 ID>-<尝试次数>.json` 文件是一批由 `Scheduled README discovery` 工作流在扫描后通过拉取请求加入的记录，该请求必须先通过仓库自身的检查。记录均为自动 README 扫描结果（`verification: automated-readme-scan`），每批都标明 `review_status: unreviewed`：没有人阅读过其来源，也没有翻译、精选、运行或评估质量。它们不属于精选目录、已审核的来源索引或公开补充批次，也从不计入精选资源数量。

入选条件沿用本仓库已有的规则：README 读取成功且 Git blob 哈希明确匹配；通过发布校验器的记录检查；至少带有一个 `strong-reverse-engineering-topics-v1` 筛选中的主题；数字 ID 不在来源索引、任何公开补充批次和更早的发现批次中；不是已精选的仓库，仓库名未被另一个数字 ID 占用，README 哈希未被其他记录发布，且没有凭据或个人路径特征。按采集时间从新到旧选取，每批最多 300 条，采集对象原样复制，不做任何改写或升级。

每批 300 条约 0.85 MB，在 Git 中压缩后约 130 KB。队列总量上限为 **25,000 条**、批次文件合计 **64 MiB**，Git 历史因此增长约 10 MB；原始 checkpoint 不会写入仓库。达到上限后入库停止，工作流失败并在追踪 issue 中说明；提高上限或归档旧批次需要单独审核。

网站在 [/zh/discoveries/](https://awesomerea.org/zh/discoveries/) 列出最新记录并标注“未审核”，简介保留上游原文、不翻译；[/discoveries.json](https://awesomerea.org/discoveries.json)、状态文件、Atom 订阅和 llms.txt 同样标明未审核。收录某个发现时，请按[审核工作表](../../docs/promotion-worksheet.zh-CN.md)另写一条精选记录，批次文件保持不变。
