# REA 生态研究与首发内容建议

> **存档快照**：本文记录 2026-10-15 合集首发时的调研，其中的数量与判断以当时为准，不随目录更新。当前收录数量请看 [README 目录](../README.zh-CN.md#目录)中的计数，或运行 `python3 scripts/catalog.py`；其他文档见[文档索引](README.zh-CN.md)。

采集日期：2026-10-15（America/Los_Angeles）。本报告复查上游仓库、官方案例的原始证据说明、社区项目 README 和作者讨论帖。它不是第三方软件运行报告。

2026-10-15 的首轮复查覆盖下文清单中的 25 条记录：18 条官方项目、文档或案例，6 条社区集成、练习或案例，以及 1 条上游维护者的相关目录。文档和案例分别计数，不能宣传成 25 个独立 REA 项目。这些记录的 verification 均为 source-reviewed；本次未安装、执行或独立复现这些外部项目。

机器可读数据见 [rea-resources.json](../data/rea-resources.json)，该文件在首轮复查后继续增补。目录还收录与 REA 没有已确认关联的独立重建案例（`relationship: independent-reconstruction`），这类记录统一存放在 [tool-resources.json](../data/tool-resources.json) 中，放在 rea-resources.json 会被校验拒绝。它们不是本文讨论的 REA 生态项目，也不计入上述 25 条。

官方文件证据固定于 [808339f0b1cf3837445f392b5d5f1f362d64a27d](https://github.com/morluto/rea/tree/808339f0b1cf3837445f392b5d5f1f362d64a27d)。目录的访问链接指向当前文档，evidence_url 保留此次复查版本。社区文档使用各自原始仓库链接和复查日期。

## 核心判断

Awesome-REA 值得做成“选对工作流、跑通小实验、检查证据”的入口。单纯收集通用逆向工具，或转述几篇 REA 热门案例，已经有相近目录覆盖。差异化应落在可复现的小目标、版本与环境记录、失败或未知结果，以及不同平台的真实使用边界上。2K Star 是传播目标，当前资料不能保证达到它。

上游已经不是一个 2K 级的新项目。GitHub API 在 2026-10-16 00:45:49 UTC 的采集快照显示 morluto/rea 有 270,067 Stars；这是当时的计数，不是预测或持续更新值。[原始仓库 API](https://api.github.com/repos/morluto/rea)

## 官方已经提供什么

官方核心定位是把 CLI/MCP、目标分析工具和 Evidence 连接起来。已有的公开内容足以支撑首发，不需要把每一种普通反编译工具都包装成 REA 插件。

| 已有内容 | 复查结果 | 对本项目的含义 |
| --- | --- | --- |
| 用户技能 | 当前树中的 reverse-engineer-anything 负责目标路由与证据工作流；安装技能本身不注册 MCP、不安装分析引擎。 | “安装技能”和“能调用 REA”必须分开说明。 |
| 开发者技能 | rea-tool-design、rea-changelog-update、rea-ci-tests-audit 分别服务于上游工具设计、发版和 CI 审计。 | 不把上游维护技能当作普通用户的 3 个新功能来凑数。 |
| 入门指南 | 官方提供原生函数、Electron CSV 导出、浏览器点击观察三条图解路径。 | 我们应补环境矩阵、可执行检查与迁移经验，避免重写一遍已有文章。 |
| 官方案例 | Aegis、DownUnderCTF、DX-Ball、Notion、TH04 均有具体分析对象和证据说明。 | 首页可以精选展示，但把“作者/上游验证”与“本目录复现”分开。 |
| 深度工作流 | 文档覆盖 JS、native、.NET、Android、浏览器、历史流量、固件等；实际依赖和平台范围不同。 | 按输入制品和任务路由，提供准确依赖，而不是一个笼统“全平台支持”。 |

依据：[用户技能](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/.agents/skills/reverse-engineer-anything/SKILL.md)、[技能目录](https://github.com/morluto/rea/tree/808339f0b1cf3837445f392b5d5f1f362d64a27d/.agents/skills)、[指南](https://rea.tools/guides/)、[案例](https://rea.tools/showcase/)、[工作流索引](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/docs/index.md)。

发布包与 main 也需要分开。此次 npm 查询得到 rea-agents 6.5.0，Node.js 范围为 ^22.19.0、^24.11.0 或 >=26.0.0。目录应记录测试所用固定版本，不能因为主分支已经有某个功能，就声称旧客户端已经能用。[固定版本包元数据](https://registry.npmjs.org/rea-agents/6.5.0)、[发布包边界说明](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/docs/installation.md#released-package-and-main)

## 已有相近目录

| 项目 | 采集时可见定位 | 已经覆盖 | 可补的内容 |
| --- | --- | --- | --- |
| [awesomerea.com](https://awesomerea.com/) | 独立逆向与替代软件目录；页面自报 51 条、6 类 | 重实现、兼容项目、工具与资源；有来源和限制字段，明确不要求全部使用 REA | 面向 REA 使用者的操作路线、固定版本实验，以及对快速变化的上游逐条更新 |
| [jyjyxt/awesome-rea](https://github.com/jyjyxt/awesome-rea) | 多语言调查案例集；README 自报 13 条 | 原帖、调查过程、证据类型；含中文、英文、日文材料 | 可下载的小目标、预期输出、失败条件与独立复现记录 |
| [morluto/awesome-reverse-engineering](https://github.com/morluto/awesome-reverse-engineering) | REA 维护者整理的通用逆向目录 | 基础学习、native、动态分析、移动端、协议、固件等工具 | 聚焦 REA 的实际工作流，把相邻工具留在有具体用途的补充位置 |

这些是本次可见样本，不是全网穷尽清单。目录存在并不等于其用户需求已经充分满足；上表“可补的内容”是本项目的编辑判断。

一次逐条回源已经发现可维护价值：

- awesomerea.com 仍把 rea-lab 的证据面板描述为计划项；[rea-lab 当前 README](https://github.com/pablodiazjorge/rea-lab/blob/main/README.md) 已列出 rea-casebook 1.0.4 和完成的 F5。我们应引用项目当日状态，而不是复制聚合站摘要。
- 旧的 [Devaretanmay/rea-investigate](https://github.com/Devaretanmay/rea-investigate) 链接此次重定向至 [Proofwork](https://github.com/Devaretanmay/proofwork)。新首页定位于通用调查技能，旧名称不应直接作为一个已核验的 REA 原生集成收录。本次暂未收入资源 JSON。
- [dsh-mcp-rea README](https://github.com/Ersith/dsh-mcp-rea/blob/main/README.md) 的适配方式值得收录，但其中某些 Windows/IDA 范围描述与当前上游已不同。依赖和平台说明应以对应版本的 [上游 IDA 文档](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/docs/ida-provider.md) 为准，不能继承适配器作者的所有概括。

## 首发资源清单

详细依赖和逐条证据链接保留在 [JSON 数据](../data/rea-resources.json)。以下是发现入口；“官方”指材料由上游发布，不表示我们实跑过。

| # | 资源 | 与 REA 的关系 | 收录价值 |
| --- | --- | --- | --- |
| 1 | [REA — Reverse Engineer Anything](https://github.com/morluto/rea) | official-core | REA 官方 CLI 与 MCP 服务，连接分析工具并保留调查证据及限制。 |
| 2 | [Official reverse-engineer-anything skill](https://github.com/morluto/rea/tree/main/.agents/skills/reverse-engineer-anything) | official-skill | 官方面向使用者的调查技能，包含目标路由、连接恢复与证据工作流。 |
| 3 | [Installation and client setup](https://github.com/morluto/rea/blob/main/docs/installation.md) | official-documentation | 安装、客户端配置、分析引擎依赖及按任务检查就绪状态的官方入口。 |
| 4 | [CLI and Evidence](https://github.com/morluto/rea/blob/main/docs/cli.md) | official-documentation | 保存完整 Evidence，再提取摘要或模块视图，适合脚本与可复现记录。 |
| 5 | [MCP contracts and generated catalog](https://github.com/morluto/rea/blob/main/docs/mcp-contracts.md#generated-catalog) | official-documentation | 官方工具协议、能力发现和 Evidence 语义；适合集成与核对实际工具边界。 |
| 6 | [Native binary investigation](https://github.com/morluto/rea/blob/main/docs/native-investigation.md) | official-documentation | 从函数清单到指令、伪代码和引用链的原生二进制调查流程。 |
| 7 | [Cross-layer JavaScript application workflows](https://github.com/morluto/rea/blob/main/docs/javascript-application-workflows.md) | official-documentation | 从 JavaScript 应用图追踪功能、比较版本，同时保留静态分析的不确定性。 |
| 8 | [Static Android APK analysis](https://github.com/morluto/rea/blob/main/docs/android-analysis.md) | official-documentation | 经 REA 的 JADX 集成检查 APK、类、方法与引用；结果不等于运行时验证。 |
| 9 | [Managed-code analysis](https://github.com/morluto/rea/blob/main/docs/managed-code-analysis.md) | official-documentation | 静态读取 .NET 元数据与 CIL，比较成员并检查声明的 native 边界。 |
| 10 | [Historical web network captures](https://github.com/morluto/rea/blob/main/docs/web-network-captures.md) | official-documentation | 离线检查已有 HAR、SAZ 等网页流量记录；不会自动抓包或访问记录中的 URL。 |
| 11 | [Firmware analysis](https://github.com/morluto/rea/blob/main/docs/firmware-analysis.md) | official-documentation | 用 Binwalk 检查固件区域、用 Unblob 显式提取，并记录工具与制品身份。 |
| 12 | [Browser observation guide](https://rea.tools/guides/browser/) | official-guide | 通过官方 Notes 示例关联用户点击、导出请求与下载结果；REA 负责观察。 |
| 13 | [Aegis: trace a login-code calculation](https://rea.tools/showcase/aegis/) | official-case-study | 追踪 Aegis APK 的 TOTP 计算，官方公开目标指纹与选取的调查证据。 |
| 14 | [DownUnderCTF: masked-squares flag checker](https://rea.tools/showcase/ctf/) | official-case-study | 官方教育 CTF 案例：从检查函数得到方程，并记录原程序验证过程。 |
| 15 | [DX-Ball: reconstruct sound panning](https://rea.tools/showcase/dx-ball/) | official-case-study | 根据指令与常量重建单个声像函数；上游报告 3,205 例与 63 字节匹配。 |
| 16 | [Notion: trace the clipboard bridge](https://rea.tools/showcase/notion/) | official-case-study | 结合 REA 发现与独立源码阅读追踪剪贴板桥；动态包装器仍有明确限制。 |
| 17 | [TH04: recover a DOS bullet-ring helper](https://rea.tools/showcase/th04/) | official-case-study | 检查 PC-98 DOS 的 16 位弹幕角度辅助函数，并关联固定版本重建与历史编译器检查。 |
| 18 | [JavaScript and Electron: follow a CSV export](https://rea.tools/guides/javascript/) | official-guide | 官方自建 Notes 样例，从 renderer、preload、IPC 到 CSV 导出建立证据链。 |
| 19 | [rea-playbook](https://github.com/jinshi666888/rea-playbook) | community-learning-resource | 提供 Electron 练习目标、Evidence 提取与 MCP 探测，区分离线展示和真正调用 REA。 |
| 20 | [dsh-mcp-rea](https://github.com/Ersith/dsh-mcp-rea) | community-integration | 社区 MCP 适配桥，以精选工具和 CLI 转发缩小宿主需要处理的工具面。 |
| 21 | [rea-jev](https://github.com/juan-viox/rea-jev) | community-integration | Claude Code 社区插件，在固定版本 REA MCP 外增加 Jev 路由和证据检查。 |
| 22 | [rea-lab](https://github.com/pablodiazjorge/rea-lab) | community-learning-resource | Windows REA/Ghidra 实验室，提供已知答案挑战、公开研究、上游贡献与限制说明。 |
| 23 | [rea-casebook](https://github.com/pablodiazjorge/rea-casebook) | community-integration | Claude Code mod 汇集收到的 REA Evidence、追踪 unknown，并校验发现所引用的证据 ID。 |
| 24 | [PicoPrint: LX-D02 printer investigation](https://github.com/bigtower17/picoprint) | community-reported-mixed-workflow | 作者报告以 REA 开始 Android 调查，再借助独立 Hermes 工具实现 Windows BLE 打印。 |
| 25 | [Awesome Reverse Engineering](https://github.com/morluto/awesome-reverse-engineering) | upstream-maintainer-companion-list | REA 维护者整理的通用逆向资源目录，适合查找基础知识与相邻工具。 |

## 三个值得保留的具体边界

**Notion 案例不是完整 IPC 自动恢复的证明。** 官方原始说明指出，REA 找到了 bridge 与动态 invoke 的位置，但指定 clipboard channel 的图追踪没有匹配；完整解释还使用了对包装器的独立阅读。这个案例适合讲“静态工具的结果怎样与人工/agent 阅读组合”，而不是讲“一键恢复所有跨进程调用”。[官方证据说明](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/website/evidence/notion-clipboard.md)

**真实社区案例可以是混合工具工作流。** PicoPrint 作者明确写到 REA 6.5.0 参与 readiness、ADB 发现和 Android 调查，Hermes v98 的函数反编译由 hermes-dec 完成。项目源码与作者说明都值得链接，但不能据此宣传 REA 已原生覆盖完整 Hermes 路径。[作者讨论](https://github.com/morluto/rea/discussions/4152)、[项目 README](https://github.com/bigtower17/picoprint/blob/main/README.md)

**证据保存和任务成功率是不同问题。** rea-lab 公开了包含负面结果的对照研究：其第一项小型 Windows crackme 研究中，有/无 REA 的解题数相同，作者报告 REA 组用时和成本更高。这是特定任务、模型和实验设置下的作者结果，不能外推为所有 REA 调查的表现。目录应容纳这类可检查的研究，而不只摘成功案例。[研究入口与限制](https://github.com/pablodiazjorge/rea-lab/blob/main/README.md)

## 建议优先制作的 8 个教程

以下是后续教程规划和验收目标，不是本次已执行结果。它们应使用自有或明确可分发的练习材料，保留原始输出；本仓库其他实验的实际状态以各自运行记录为准。

| 顺序 | 教程主题 | 目标与产出 | 建议验收 | 条件与原始参考 |
| --- | --- | --- | --- | --- |
| P0-1 | 第一个静态 JS 调查 | 自建小型 Electron 风格目标；输出完整 Evidence、摘要、API/IPC 与 file:line 证据 | 固定 REA 版本；预先写好的目标事实与实际输出相符；至少一条不能确认的关系被保留 | 支持的 Node.js；Linux 还需 procps-compatible `ps`；[官方 Electron 指南](https://rea.tools/guides/javascript/) |
| P0-2 | 同一功能的 v1/v2 比较 | 自建两个包，只改变一个 IPC channel 或导出格式；给出变化清单 | 对照已知变更；声明哪些差异是静态推断；未修改文件不能被误报成语义等价证明 | 已保存的 JS Evidence；[比较工作流](https://github.com/morluto/rea/blob/main/docs/javascript-application-workflows.md) |
| P0-3 | 离线 HAR 到请求地图 | 自建本地页面生成脱敏 HAR；输出域名、路径、响应类型及缺失字段 | 结果可追溯到记录序号；标明 body 未记录的情况；分析过程中不访问捕获 URL | 现成 HAR；[历史网络捕获](https://github.com/morluto/rea/blob/main/docs/web-network-captures.md) |
| P1-4 | 从 .NET DLL 找到一个解析器 | 自建 PE/CLI 样例；输出类型、成员、CIL 与 v1/v2 差异 | 不加载目标程序集；以源代码作为独立答案；不把 NativeAOT 当普通托管程序集 | 构建样例需 .NET SDK，读取元数据不需 native engine；[托管分析](https://github.com/morluto/rea/blob/main/docs/managed-code-analysis.md) |
| P1-5 | Aegis 的 30 秒验证码 | 对照官方固定 APK 案例，追踪时间步长、HMAC 与截断逻辑 | 记录 APK/JAR 指纹与工具版本；只使用测试密钥；区分静态路径与另行计算的测试向量 | JDK 与 JADX provider；[官方 Aegis 案例](https://rea.tools/showcase/aegis/) |
| P1-6 | 一段 C 函数的二进制重建 | 自编译小函数，去除部分符号后用 Ghidra/REA 分析；重建函数并对比输入输出 | 公开编译选项、架构与二进制哈希；边界输入和失败样本可重跑；只声称测试覆盖到的范围 | 本地编译器、Ghidra/JDK；[官方 native 指南](https://rea.tools/guides/native/) |
| P2-7 | 浏览器点击与下载的证据链 | 在自有本地 Notes 页面，由操作者或独立控制器点击；REA 记录观察窗口 | 明确 endpoint、origin、窗口、外部动作；把捕获到的请求与下载内容对照 | Chrome-family/CDP 与显式允许的 origin；[官方 browser 指南](https://rea.tools/guides/browser/) |
| P2-8 | 小型固件包的区域与提取 | 自建含已知压缩区的样例；输出区域清单、提取目录与嵌入文件指纹 | 比较预先已知布局；新目录承接提取结果；区域识别与实际可运行性分开 | Linux x64、Binwalk/Unblob；[固件分析](https://github.com/morluto/rea/blob/main/docs/firmware-analysis.md) |

建议每篇保持同一结构：问题、输入与哈希、环境版本、命令、关键输出、独立检查、剩余未知、失败排查。预计用时应在实际记录后再填；先不要宣传“5 分钟必成功”。

第一篇可使用以下已在官方文档中核对的命令形态；这里给的是写作起点，不是本报告执行记录：

    npx -y rea-agents@6.5.0 analyze-javascript-application /absolute/path/to/app --json > app-evidence.json

后续把完整输出放进 source.kind=inline 的 inspect-analysis-view 请求，再读 summary 或一个模块。不要为了在 README 中展示，删掉源 Evidence 中的 limitations、unknowns 或覆盖范围。[CLI 与 Evidence](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/docs/cli.md)

## 可执行的内容缺口

1. **按任务选择入口。** 用户拿到的是 APK、DLL、ASAR、HAR、固件或本地程序；首页先问“你有什么”，再列第一步与依赖。普通源代码库阅读仍可用常规工具，无需强行引入 REA。
2. **版本化环境记录。** 记录操作系统、架构、Node.js、REA 版本、provider 版本和目标指纹。把源码主分支支持、发布包包含、实际环境跑通分开。
3. **输出阅读能力。** REA 的完整 JS Evidence 可能很大；贡献摘要提取、模块导航和未知项解释示例，比再增加一百个无关系链接更有用。不要声称第三方 adapter 的旧 schema 大小就是当前 REA 的大小。
4. **覆盖成功与失败。** 已知答案的小目标、动态字符串、未配对 IPC、缺失 provider、空结果和跨版本变化，都可以成为练习。用户能知道工具在哪一步停止，比一个漂亮但不可追踪的结果更有价值。
5. **保留项目关系的精度。** 官方能力、社区适配、作者报告使用、混合工具案例、相邻工具是不同关系。只有仓库里出现 REA 文件，不能证明整款软件由 REA 重建。
6. **做持续回源。** 改名、重定向、过时依赖和从计划到已发布的变化值得更新。先把首轮复查的 25 条维护好，再扩到更多条目。

## 收录和维护约定

- 每条至少包含原始项目或文章链接、关系分类、双语描述、证据链接、复查日期、依赖和复查级别。具体字段与当前数据一致。
- source-reviewed 只表示阅读并核查了原始材料；不表示成功安装、代码安全审计、平台兼容性测试或成果复现。当前不收录运行或复现结果；如需讨论相关实验，可在 issue 中提供信息供审查，但不将其作为验证结论发布。
- 作者报告的统计、硬件成功、性能和功能完整性必须归属于作者；如引用独立复现报告，也应明确报告者，并链接其版本、目标指纹和公开日志，不将其表述为本目录的运行验证。
- 不从聚合目录直接继承描述。聚合目录用于发现，再回到项目 README、固定提交、官方案例证据或原作者讨论。
- 固定证据链接解释“当时为什么收录”；当前访问链接帮助读者找到后续变化。重定向与重大版本更新要重新核对。
- 标明练习材料、源代码、游戏资源、截图与文档各自许可。列表的许可不会替代被收录内容的许可。

本次只做公开来源阅读与本地研究文件整理，没有联系作者、提交上游内容或安装这些社区集成。
