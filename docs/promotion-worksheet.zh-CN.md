# 从仓库索引到精选条目：复核工作表

[English](promotion-worksheet.md) · [扫描方法（英文）](source-scan.md) · [中文贡献指南](../CONTRIBUTING.zh-CN.md)

自动[仓库索引](../data/source-index.json)中的记录是 README 扫描结果，`verification` 为 `automated-readme-scan`。其简介、目标领域和分类来自仓库元数据，未经复核。把其中的仓库收录为精选，是根据你自己对一手来源的复核另写一条记录。扫描记录本身永远不会被修改、重新标注或升级：它保留原有证据和状态，仓库目录在构建时把它链接到精选条目。

在提议收录的 issue 或 pull request 中使用下面的工作表，并填写每一行。可以填写“未知”；关键行为未知时，结论应为暂缓。

## 工作表

| 行 | 问题 | 答案来源 |
| --- | --- | --- |
| 来源 ID | 扫描记录的 `id` 和记录的 `full_name`。 | `python3 scripts/catalog.py --source-index <名称> --json` |
| 扫描快照 | 原样抄录其 `observed_at`、`readme_git_sha`、`readme_sha256` 和 `readme_bytes`。 | 扫描记录；它说明扫描读到了什么，不是复核证据。 |
| 已有条目 | 该项目是否已收录为精选，或已在开启的 issue、pull request 中被推荐？ | `python3 scripts/catalog.py <名称>`、开启的 issue 和 pull request |
| 规范项目 | 维护者自己的仓库或网站，作为 `url`。 | 项目本身；优先原始项目，而非 fork 或镜像。 |
| 证据修订 | 你实际阅读的提交、发布版本或注明日期的页面，以固定链接填入 `evidence_url` 和 `additional_evidence_urls`。 | 你的复核 |
| 复核日期 | 你复核的日期，作为 `verified_at`。 | 你的复核 |
| 支持的任务 | 用自己的话写出文档所述的功能，作为 `description_en` 和 `description_zh`。 | 固定版本的证据 |
| 局限 | 未完成、实验性或明确不支持的功能，以及上游说明的适用范围。 | 固定版本的证据 |
| 使用条件 | 平台、版本、输入和许可条款，作为 `requirements` 及其中文翻译。 | 固定版本的证据 |
| 分类 | `kind`、`relationship` 和 `category`，分别独立选择。 | [中文贡献指南](../CONTRIBUTING.zh-CN.md#kindrelationshipcategory-与-targets) |
| 目标领域理由 | 每个目标领域成立的理由，并引用证据。自动扫描标签不能作为理由。 | 固定版本的证据 |
| 结论 | 收录为精选，或暂缓并写明缺少哪项证据。 | 以上各行 |

## 收录还是暂缓

只有当描述、使用条件和目标领域中的每个关键说法都能追溯到固定修订的公开一手来源，并在记录的日期完成复核时，才收录为精选。然后按英文指南[目录更新部分](../CONTRIBUTING.md#update-the-catalog)的说明添加记录及其中文使用条件，不要改动 `data/source-index.json`。

证据不足时应暂缓。常见情形：README 没有说明项目做什么或如何使用；某项功能只出现在仓库简介、扫描标签或第三方帖子中；找不到可固定的公开来源；或者目标领域缺乏依据。暂缓不新增精选记录，也不修改扫描记录。请在 issue 中写明缺少哪一行，便于之后继续复核。不要用运行结论填补空缺：目录记录不收录运行结果，未亲自观察到的结果绝不能写入。

暂缓不等于排除出收录范围。把明显无关的扫描结果排除出浏览，是对 `data/source-scope.json` 的另一项需复核的修改，见扫描方法中的[收录范围（英文）](source-scan.md#collection-scope)。

## 完整示例：capa

已扫描的仓库 mandiant/capa 现为 [tool-resources.json](../data/tool-resources.json) 中的精选条目 [`capa`](https://awesomerea.org/zh/resources/capa/)。其工作表如下：

| 行 | 答案 |
| --- | --- |
| 来源 ID | `scan-272815213`，mandiant/capa |
| 扫描快照 | 观察于 2026-10-16T01:35:34Z；README Git blob `b75190372c257abfc3822cba33ca58ef2867ce23`，SHA-256 `e3dc86527f193f95f56a405f6b2c35ef6f5102be937b03834827d908664faf11`，25,053 字节。自动标签：`binary`、`native-analysis`。 |
| 已有条目 | 本次复核前未收录。 |
| 规范项目 | `https://github.com/mandiant/capa` |
| 证据修订 | 提交 `7a235c46965ea0965c65be3b9ee1e21dca686f3d` 中的 `README.md`，与扫描记录的 Git blob 相同。复核还阅读了该提交中的安装、使用和局限文档、插件 README、`pyproject.toml` 与许可证，以及 v10.0.0 发布页和 flare-capa 10.0.0 的 PyPI 页面；扫描不会读取这些内容。 |
| 复核日期 | 2026-10-19 |
| 支持的任务 | 将 YAML 规则集与从 PE、ELF、.NET 文件或 shellcode 中提取的特征匹配，按功能命名空间报告可执行文件具备哪些功能（README）。 |
| 局限 | 加壳或混淆的程序、安装程序及打包程序可能导致结果有误或不完整；分散在包装函数或子函数中的功能无法匹配（局限文档）。匹配结果只是功能迹象，并非已确认的行为。 |
| 使用条件 | 提供 Linux、macOS 和 Windows 独立构建，Linux 构建需要 GLIBC 2.26+；PyPI 软件包不含默认规则；IDA、Ghidra 和 Binary Ninja 集成各有版本要求（安装文档、插件 README）；Apache-2.0 许可。 |
| 分类 | `kind: tool`；`relationship: foundation`，因为其文档没有确立与 REA 的关联；`category: native-analysis`。 |
| 目标领域理由 | `binary`：文档列出的输入是可执行模块、shellcode、针对可执行文件的沙箱报告以及由它们派生的文件。证据不支持其他目标领域。 |
| 结论 | 收录为 `capa`，`verified_at: 2026-10-19`。 |

修改之后，`scan-272815213` 逐字节保持不变，仍为 `automated-readme-scan`。它在[原生分析目录](repositories/native-analysis.zh-CN.md)中的那一行多出“精选：capa”链接，仅仅因为精选记录的 `url` 恰好是该仓库的根地址。本次没有安装或运行任何内容；精选记录的使用条件写明未分析任何样本。
