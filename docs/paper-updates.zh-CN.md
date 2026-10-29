# 论文被接收或正式发表后如何更新

[English](paper-updates.md) · [中文贡献指南](../CONTRIBUTING.zh-CN.md#推荐论文) · [论文字段（英文）](../data/README.md)

[papers.json](../data/papers.json) 中的预印本之后可能被接收、收入会议论文集或成为期刊论文。此时应原地更新已有记录：论文保留稳定的 ID，预印本阶段的记录也继续保留。本页以一次真实的更新为例：`paper-crebench` 从 `conference-accepted` 改为 `conference-paper`。

## 1. 确认是同一项工作

把新发表的版本与记录比较：标题、完整作者名单、摘要以及报告的评测。标题略有差异仍可能是同一篇论文：`paper-dire` 就注明出版方和 arXiv 标题用 “Naming”，会议日程则用 “Renaming”。如果是同一项工作，就更新这条记录。不要因为论文取得 DOI、论文集页码或期刊版本就新增第二条记录；校验器会拒绝重复的论文 ID、arXiv ID、DOI 或规范论文链接。

真正不同的论文另立记录：标题和标识符都不同，并提出新的方法、数据集或评测，例如 `paper-dire` 之后的 `paper-dirty`。较早记录的标识符、日期和研究产物保持原样。无法判断后来的文章是否为同一工作时，请在 issue 中说明，不要合并或重复记录。

## 2. 保留 ID 和预印本证据

`id` 保持不变，这样 `/papers/<id>/` 页面和引用都保持稳定。保留 `arxiv_id` 和 `first_arxiv_date`：它们记录这项工作首次出现的时间，发表后仍然成立。`arxiv_version_reviewed` 是你实际阅读的 arXiv 版本，只有复核了更新的版本时才修改，并在 `metadata_notes` 中说明原因。`evidence_urls` 中保留 arXiv 摘要页。

## 3. 只添加已核实的发表信息

| 字段 | 如何修改 |
| --- | --- |
| `publication_status` | 已核实接收、但论文集尚未核实时用 `conference-accepted`；核实正式发表版本后用 `conference-paper` 或 `journal-article`。 |
| `venue` | 会议、研讨会或期刊名称；期刊论文填期刊名。 |
| `doi` | 论文本身的 DOI，绝不能用软件或数据集 DOI。出版方未分配 DOI 时保持 `null`。 |
| `url` | 正式发表的规范页面，例如 DOI 链接或官方论文集、评审记录页面。 |
| `citation` | 可选的出版物名称、卷、页码或文章编号，只能抄录自出版方来源。 |
| `evidence_urls` | 添加你核对过的出版方、DOI 或 Crossref 页面；保留原有证据。 |
| `verified_at` | 本次复核的日期。 |

修改任何英文文本字段时，同步更新对应的 `_zh` 字段。

## 4. 说明日期依据

`publication_date` 和 `date_precision` 只记录发表来源能够证实的内容，`date_basis` 写明该来源。出版方登记的发表日期可以精确到日或月。会议举办日期、接收公告或评审网站的时间戳都不是发表日期；需要时可以写在 `metadata_notes` 中，但不能记为发表日期。只能核实年份时，保持 `date_precision: year` 和 `publication_date: null`。不要编造具体日期。

## 5. 复核有变化的全文

阅读正式发表版或最终版（camera-ready）全文，而不只是落地页。方法、结果或范围有变化时，更新 `description`、`scope_limitations` 和 `why_fits`，并把 `pdf_url` 指向你复核的版本。无法读取出版方全文时，在 `metadata_notes` 中说明你读的是哪个版本。

## 6. 区分研究产物的版本

`code_url` 和 `project_url` 仍是作者提供的研究产物。评测之后有改动的仓库，或之后发布的代码版本，除非作者明确说明（例如注明标签或提交），否则都不是论文评测时使用的那一版。请在 `scope_limitations` 或 `metadata_notes` 中保留这一限制。`paper-dire` 就注明其原始代码仓库已弃用并指向后继项目，而不暗示仍受支持。

## 完整示例：CREBench

2026-10-17，[PR #203](https://github.com/reacher-z/Awesome-REA/pull/203) 在 CREBench 的 COLM 2026 记录出现在 OpenReview 上之后更新了 `paper-crebench`。

| 字段 | 更新前（2026-10-16 复核） | 更新后（2026-10-17 复核） |
| --- | --- | --- |
| `id` | `paper-crebench` | `paper-crebench`，不变 |
| `publication_status` | `conference-accepted` | `conference-paper` |
| `url` | `https://arxiv.org/abs/2604.03750` | `https://openreview.net/forum?id=tLYdf8hWJB` |
| `pdf_url` | `https://arxiv.org/pdf/2604.03750` | `https://arxiv.org/pdf/2604.03750v2`，即项目所称的最终版 |
| `arxiv_id`、`first_arxiv_date`、`arxiv_version_reviewed` | `2604.03750`、`2026-04-04`、`v2` | 不变 |
| `doi` | `null` | `null`；未核实到 DOI |
| `date_precision`、`publication_date` | `year`、`null` | `year`、`null` |
| `date_basis` | 由 arXiv 备注和作者项目确认会议；论文集日期未核实 | 年份来自官方 OpenReview 记录及其 BibTeX；不声称更精确的日期 |
| `evidence_urls` | arXiv 摘要页与 v2 HTML、作者仓库和项目页 | 新增 OpenReview 记录、COLM 录用论文页与会议页以及 arXiv v2 PDF；原有链接保留 |

新的 `metadata_notes` 说明了判断依据：OpenReview 记录的标题、七位作者和摘要与 arXiv v2 一致；OpenReview 的 2026-07-08 时间戳与接收公告同日，不作为发表日期；2026 年 10 月 6—9 日的会议及其海报场次属于会议信息；仓库中的 BibTeX 仍引用 arXiv。没有新增第二条记录；由于没有来源给出更精确的发表日期，仍只精确到年份。

## 检查并重新生成

```sh
python3 scripts/validate_papers.py
python3 scripts/build_readme.py
python3 -m unittest discover -s tests
python3 scripts/build_production.py
```

README 生成命令会更新两个 README 中的论文列表，请与 `data/papers.json` 一并提交。生产构建会在 Git 忽略的 `dist/` 中重新生成论文目录、详情页和 BibTeX 下载。与所有论文记录一样，`runtime_tested` 保持 `false`：更新只复核来源，不复现实验结果。
