# 参与贡献：中文快速入门

[English](CONTRIBUTING.md) · [文档索引](docs/README.zh-CN.md)

本页概述向 Awesome Reverse Engineering Anything 推荐资源、论文和修正的基本规则。完整说明见[英文贡献指南](CONTRIBUTING.md)；两者如有出入，以英文版为准。

## 推荐资源

可以使用[资源推荐表单](https://github.com/reacher-z/Awesome-REA/issues/new?template=resource.yml)，也可以直接提交 pull request。请提供：

- **名称与原始链接**：优先使用项目维护者的仓库或官网。
- **资源类型**：项目、工具、集成、案例、合集、文档、学习资源或研究。
- **目标领域**：网站、游戏、应用、二进制、固件或协议，可以多选。
- **简短说明**：用自己的话说明资源提供什么。
- **使用条件**：平台、许可、发布版本或外部工具要求会影响说明时，一并写明。
- **已有条目**：先在合集和已开启的 issue、pull request 中检索，资源推荐表单会请你确认这一点。资源已经收录时，写明其目录 ID（即 `/resources/<id>/` 页面地址的最后一段），并说明要更新的内容，而不是再申请一条新条目。
- **你与资源的关系**：说明你是否维护或参与贡献该资源、有其他关系、没有关系，或选择不透露。这与资源本身和 REA 的关系是两回事，不代表认可、官方身份或运行验证，也不需要提供真实姓名、雇主或账户信息。

提交前请先确认合集中没有重复条目。收录不设最低 Star 数；优先收录原创、仍在维护的项目，而不是复制的 fork。关于 REA 集成的说法须有项目自身文档支持。

发现中文翻译不准确时，可使用[翻译修正表单](https://github.com/reacher-z/Awesome-REA/issues/new?template=translation.yml)；链接失效或信息过时，可使用[过时条目表单](https://github.com/reacher-z/Awesome-REA/issues/new?template=broken-resource.yml)。资源、论文和修正表单目前为英文界面；重建案例表单提供双语提示。

## 推荐论文

使用[论文推荐表单](https://github.com/reacher-z/Awesome-REA/issues/new?template=paper.yml)，写明论文的规范页面或 DOI、发表状态、研究的逆向任务，以及作者提供的代码或数据链接（如有）。论文可以公开访问，不代表其基准或评测服务也已公开。

书目记录保存在 `data/papers.json`，与工具目录和自动扫描索引分开维护。提交 pull request 时，请参照[目录格式（英文）](data/README.md)中的论文字段表和已有记录，保留原始标题和作者全名；只记录已核实的日期精度，不要编造发表日期或会议日期。DOI、arXiv 标识和出版方身份等规则见英文指南的[论文部分](CONTRIBUTING.md#suggest-a-research-paper)。

## kind、relationship、category 与 targets

精选记录保存在 `data/rea-resources.json` 和 `data/tool-resources.json`。中英文描述都应简洁；网站使用的中文名称和使用条件在 `site/translations.zh-CN.json`。下面四个字段各自独立选择，一个字段不能决定另一个：

- `kind`：分享的是什么，例如工具、集成或案例。
- `relationship`：证据证明了它与 REA 是什么关系，例如 REA 官方或社区资源、独立智能体集成或基础工具。
- `category`：适合哪一类任务或工具族。
- `targets`：帮助分析或重建的对象领域。

当前可用值见[目录格式（英文）](data/README.md)。证据支持多个领域时可以选择多个 targets。为条目补充新的已复核领域时，保留原有 targets；不要自动重新归类历史扫描记录。

### 何时使用协议（protocol）

只有一手证据描述通信格式分析、流量解析、报文交互或协议状态推断（包括硬件总线）时，才使用 `protocol`。仅能联网、调用 API 或提供 MCP 接口都不符合条件。报文采用二进制编码，也不等于对可执行文件做 Binary 分析。

### 游戏与二进制（game、binary）

游戏与二进制经常重叠，应分别依据证据判断。通用二进制分析工具只有在其自身文档或其所基于引擎的文档点名游戏用途时，才标注 `game`，例如游戏机处理器、ROM 或游戏机可执行格式、游戏引擎；能打开包括游戏在内的任意可执行文件并不足够。反编译、静态重编译和移植等游戏重建案例标注 `game`，`binary` 留给它们所依赖的重编译器、提升器或反编译器条目。只有当游戏案例的证据把可执行文件分析本身（如反汇编、恢复出的函数或工具输出）作为报告结果时，才为其加注 `binary`。

### 重建案例

使用[重建案例推荐表单](https://github.com/reacher-z/Awesome-REA/issues/new?template=case-study.yml)，可用英文或简体中文填写。分别说明原始输入、重建输出与证据；部分重建或未测试的案例也可推荐。案例名称写作 `<主名称>: <重建或发现的内容>`：以项目公开使用的名称开头，并在后半部分写明游戏、应用或设备，例如 `SpeedBreaker: statically recompiling Need for Speed: Most Wanted for Xbox 360`；中文名称保留主名称，用全角冒号（：）接译文。主名称本身含冒号或没有独立项目名时的写法，见[目录格式（英文）](data/README.md)中的 `name` 一行。

案例可以使用 REA、其他智能体或独立的逆向工具。有记录的重建项目如果与 REA 没有已确认的关联，使用 `relationship: independent-reconstruction` 和 `category: reconstruction-cases`，targets 按实际涉及的领域填写。说明中要区分作者报告的结果、尚未完成的行为、平台限制，以及需要用户自备的原始资源，并可按[目录格式说明（英文）](data/README.md)为每条 `requirements` 填写可选的 `requirement_facets`；填写后页面会把前提条件排在最前。尽量提供固定版本的公开来源；不要包含专有目标二进制文件或私人抓包数据。

## 来源已复核不等于运行验证

每条记录都要有一手来源和复核日期。`source-reviewed`（来源已复核）只表示已对照项目文档核对说明，不表示已安装、审计或复现该项目。规模更大的 `data/source-index.json` 是自动建立的仓库索引，保留单独的来源记录，不属于精选资源。目录记录目前不收录运行或复现结果：所有精选记录都使用 `verification: source-reviewed`，所有论文的 `runtime_tested` 都为 false，也没有单独提交测试运行的格式。可以在 issue 中说明自己运行了什么，帮助审核者核实某个说法，但这些内容不会作为验证结果发布。

## 不要提交的内容

公开仓库中不得包含凭据、私人账户信息、个人文件系统路径、专有二进制文件、未处理的私人抓包数据，或受许可限制的 Font Awesome Pro 文件。原创贡献采用本仓库的 MIT 许可；链接的资源保留各自的许可。

Issue 和 pull request 都是公开的。粘贴日志、截图等内容前，请删除令牌、Cookie、账户标识、本地文件路径和私人抓包数据。工作流漏洞、凭据泄露或已收录资源疑似被入侵等安全问题，请按[安全策略](SECURITY.md#中文摘要)私下报告。

## 本地检查

修改目录数据后，在仓库根目录运行：

```sh
python3 scripts/build_readme.py
python3 scripts/build_repository_index.py
python3 scripts/validate.py
python3 scripts/build_site.py
node --check site/app.js
```

两个 README 中每个条目只占一行：名称链接、说明首句、标签，以及指向网站条目页的“完整条目”链接；完整说明、使用条件和证据保留在条目页上，因此说明首句应能独立概括条目。GitHub 只渲染 README 的前 500 KiB（512,000 字节），所以 `build_readme.py` 会报告两个文件的大小；任一 README 超过 420,000 字节时，它和 `validate.py` 会给出警告，但不会使检查失败。

运行全部测试（需要 Node.js，不访问网络）：

```sh
python3 -m unittest discover -s tests -v
```

修改论文记录时，再运行 `python3 scripts/validate_papers.py`，重新生成两个 README，然后运行 `python3 scripts/build_production.py`。`python3 scripts/check_links.py` 用于在线检查来源链接，限流和临时网络故障会与确认失效的链接分开报告。CI 的完整步骤见英文指南的[目录更新部分](CONTRIBUTING.md#update-the-catalog)。

## 审核与发布

Pull request 会收到由基础分支可信代码执行的[规则审核（英文）](docs/automation.md)，检查目录结构、重复项、来源字段和常见隐私问题，不运行贡献者的代码。资源是否相关、说法是否属实由维护者审核；自动检查通过不代表自动批准或合并。

快照版本在 `main` 上打 `vMAJOR.MINOR.PATCH` 标签，并在 GitHub Release 中附带数据快照。打标签前，维护者在发布提交中把 [CITATION.cff](CITATION.cff) 的 `version` 改为去掉 `v` 的标签号，`date-released` 改为发布当天的 UTC 日期；`validate.py` 会检查这两个字段同时出现、版本号符合语义化版本且日期不晚于当前。在正式取得 DOI 之前，不添加 DOI 或其他标识符。

## 术语对照

界面文字、生成器标签和 README 中手写的说明统一使用下列译法，精选条目的中文描述也尽量沿用。自动扫描仓库的中文简介按上游原文翻译，不据此批量改写。

| English | 中文 | 说明 |
| --- | --- | --- |
| source-reviewed | 来源已复核 | 已对照一手文档核对说明；名词作“来源复核”。不代表安装、运行、审计或复现。 |
| runtime-tested | 已运行验证 | 指实际运行并留有可检查记录的结果；名词作“运行验证”。目录记录目前不使用这一状态，它与“来源已复核”不能互换。 |
| requirements | 使用条件 | 平台、引擎、版本、许可或输入等要求，对应 `requirements` 字段。 |
| review date | 复核日期 | 来源复核的日期（`verified_at`），界面显示为“复核于”加日期；不是发布或测试日期。 |
| agent | 智能体 | 项目名、产品名和引用的原文保持原样。 |
| integration | 集成 | 如“独立智能体集成”“REA 社区集成”；这个词本身不表示 REA 官方集成。 |
| case study | 案例 | 对应 `kind: case-study`。 |
| requirement facets | 使用条件分面 | `requirement_facets` 的取值：Prerequisites 前提条件、Scope 范围、Limits 局限、Testing evidence 测试证据、License 许可、Attribution 署名。 |
| learning resource | 学习资源 | `kind: learning-resource` 与 `relationship: learning` 使用同一译法。 |
| curated | 精选 | 经来源复核的目录条目，即 `rea-resources.json` 与 `tool-resources.json` 中的记录。 |
| repository index (scan index) | 仓库索引 | 自动读取 README 建立的 `source-index.json`；与精选资源分开计数，条目未逐项复核。 |

目标领域依次译为网站（website）、游戏（game）、应用（app）、二进制（binary）、固件（firmware）和协议（protocol）。
