[![Awesome REA — 理解软件行为，用证据支撑重建](assets/readme-banner.svg)](https://awesomerea.org)

# Awesome Reverse Engineering Anything

**Agent 辅助逆向工程资源指南：选工具、追踪行为、保留证据。**

[![目录检查](https://github.com/reacher-z/Awesome-REA/actions/workflows/validate.yml/badge.svg)](https://github.com/reacher-z/Awesome-REA/actions/workflows/validate.yml)
[![MIT 许可证](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[English](README.md) · 简体中文

**[访问 AwesomeREA.org](https://awesomerea.org)** — 按 Website、Game、App、Binary、Firmware 浏览资源。

**81 条精选资源 · [1,600 个已扫描仓库 README](https://awesomerea.org/?view=source-index#catalog) · 7 类任务流程。** 自动扫描索引与人工审阅目录分开展示；扫描不等于运行测试或兼容性背书。[扫描方法与记录](docs/source-scan.md)。

从 [REA — Reverse Engineer Anything](https://github.com/morluto/rea) 入门，按目标选择独立 Agent 集成、基础工具和学习资源。本项目是独立社区整理的资源库；每条记录包含原始来源、前置条件、与 REA 的关系和审阅日期。

**[运行原创练习](labs/electron-notes/README.md) · [按任务选择流程](docs/playbooks.md) · [搜索目录](#搜索目录) · [参与贡献](CONTRIBUTING.md)**

## 从你的目标开始

| 想研究什么 | 入口 | 应拿到的结果 |
| --- | --- | --- |
| **Website 网站** — 页面交互与请求 | [官方浏览器指南](https://rea.tools/guides/browser/) | 观察到的操作、捕获请求与对应脚本 |
| **Game 游戏** — 计算、资源格式或图形帧 | [游戏流程](docs/playbooks.md#game-behavior) | 有证据支撑的局部行为或渲染说明 |
| **App 应用** — Electron 功能和 IPC 路径 | [Notes 导出练习](labs/electron-notes/README.md)、[官方 JS 指南](https://rea.tools/guides/javascript/) | renderer → preload → IPC → main 的调用链和文件位置 |
| 原生二进制中的一个函数 | [原生函数流程](docs/playbooks.md#native-function-recovery) | 伪代码、指令证据、行为验证样例 |
| Android APK | [Android 流程](docs/playbooks.md#android-apk) | Manifest 事实、类和方法的追踪路径 |
| .NET 程序集 | [.NET 流程](docs/playbooks.md#dotnet-assembly) | 类型及成员清单、CIL 支撑的解释 |
| 保存的 HTTP 流量 | [离线捕获流程](docs/playbooks.md#saved-network-capture) | 带原始记录位置的请求序列 |
| 固件镜像 | [固件流程](docs/playbooks.md#firmware-image) | 区域清单、提取边界和嵌套结构 |
| Agent 应接哪个工具 | [资源目录](#资源目录) | 基于分析引擎、平台、许可证和目标的选择 |

## 跑通第一个调查

仓库自带一个原创 [Electron 结构的 Notes 样例](labs/electron-notes/README.md)：追踪 CSV 导出路径，再用 3 个可执行测试核对转换行为。静态练习无需下载目标应用，也无需商业反编译器。

```sh
git clone https://github.com/reacher-z/Awesome-REA.git
cd Awesome-REA
node --test labs/electron-notes/app/csv.test.cjs
mkdir -p labs/electron-notes/output
npx -y rea-agents@6.5.0 analyze-javascript-application "$PWD/labs/electron-notes/app" --json > labs/electron-notes/output/rea-evidence.json
python3 scripts/verify_evidence.py labs/electron-notes/output/rea-evidence.json
```

此固定 REA 版本要求 Node.js `^22.19.0`、`^24.11.0` 或 `>=26.0.0`。首次执行 `npx` 会下载 REA 及其依赖；完整步骤和实际验证范围见[练习记录](labs/electron-notes/README.md)。配置 Agent 请使用独立的[官方安装指南](https://github.com/morluto/rea/blob/main/docs/installation.md)。

## 搜索目录

需要 Python 3.10+，无第三方 Python 依赖：

```sh
python3 scripts/catalog.py electron --language zh
python3 scripts/catalog.py --target game --language zh
python3 scripts/catalog.py ghidra --language zh
python3 scripts/catalog.py --relationship independent-agent-integration
python3 scripts/catalog.py --list-categories
python3 scripts/catalog.py android --json
python3 scripts/catalog.py ghidra --source-index
```

[JSON 目录](data/README.md) 是条目的维护入口，Agent 也可直接读取，无需安装新的 skill 或 MCP 服务。

## 收录标签说明

- **REA 官方资源**：上游能力、工具要求和使用指南。
- **REA 社区资源**：明确使用 REA 的案例或扩展；可能同时依赖其他工具。
- **独立 Agent 集成**：自行连接其他工具，收录不代表已经接入 REA。
- **基础工具与学习资源**：帮助完成具体逆向任务的配套资源。

`source-reviewed` 仅表示已阅读一手文档，不表示已安装、做过安全审计或验证所有平台。实际运行结果单独写入练习记录。Star 数不作为收录门槛。

## 资源目录

<!-- BEGIN GENERATED CATALOG -->
按任务整理的 81 条资源；条目数不代表独立项目数。

每条附一手证据与来源审阅日期。来源审阅不等于运行验证；完整记录见 [JSON 目录](data/README.md)。

REA 资源直接展开；独立工具按类别折叠，展开可见条目、依赖与来源，也可[搜索全部记录](#搜索目录)。

### REA 官方：核心与配置

- **[REA — Reverse Engineer Anything](https://github.com/morluto/rea)** — REA 官方 CLI 与 MCP 服务，连接分析工具并保留调查证据及限制。

  REA 官方项目 · 网站 / 游戏 / 应用 / 二进制 / 固件 · [一手来源](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/README.md) · 来源审阅：2026-10-15。
  前提与范围：rea-agents 6.5.0 was the published npm version at review time. Node.js ^22.19.0 || ^24.11.0 || &gt;=26.0.0; additional tools depend on the target.

- **[Official reverse-engineer-anything skill](https://github.com/morluto/rea/tree/main/.agents/skills/reverse-engineer-anything)** — 官方面向使用者的调查技能，包含目标路由、连接恢复与证据工作流。

  REA 官方技能 · 网站 / 游戏 / 应用 / 二进制 / 固件 · [一手来源](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/.agents/skills/reverse-engineer-anything/SKILL.md) · 来源审阅：2026-10-15。
  前提与范围：Installing the skill provides instructions; it does not by itself register MCP or install analysis engines. Use the connected server's actual tool schemas; repository main may be ahead of an installed release.

- **[Installation and client setup](https://github.com/morluto/rea/blob/main/docs/installation.md)** — 安装、客户端配置、分析引擎依赖及按任务检查就绪状态的官方入口。

  REA 官方文档 · 网站 / 游戏 / 应用 / 二进制 / 固件 · [一手来源](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/docs/installation.md) · 来源审阅：2026-10-15。
  前提与范围：Supported Node.js and npm. Setup previews client configuration changes; native engines have separate prerequisites.

- **[CLI and Evidence](https://github.com/morluto/rea/blob/main/docs/cli.md)** — 保存完整 Evidence，再提取摘要或模块视图，适合脚本与可复现记录。

  REA 官方文档 · 网站 / 游戏 / 应用 / 二进制 / 固件 · [一手来源](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/docs/cli.md) · 来源审阅：2026-10-15。
  前提与范围：Installed REA CLI or an explicitly pinned package runner. CLI processes are separate; retain result files for later operations.

- **[MCP contracts and generated catalog](https://github.com/morluto/rea/blob/main/docs/mcp-contracts.md#generated-catalog)** — 官方工具协议、能力发现和 Evidence 语义；适合集成与核对实际工具边界。

  REA 官方文档 · 网站 / 游戏 / 应用 / 二进制 / 固件 · [一手来源](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/docs/mcp-contracts.md) · 来源审阅：2026-10-15。
  前提与范围：A compatible MCP client for live use. Discover the live catalog before relying on tools documented on main.


### REA 官方：调查指南

- **[Native binary investigation](https://github.com/morluto/rea/blob/main/docs/native-investigation.md)** — 从函数清单到指令、伪代码和引用链的原生二进制调查流程。

  REA 官方文档 · 二进制 / 游戏 · [一手来源](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/docs/native-investigation.md) · 来源审阅：2026-10-15。
  前提与范围：A target binary and a configured supported provider such as Ghidra, Hopper or IDA. Host, architecture and provider support are scoped separately; pseudocode is not original source.

- **[Cross-layer JavaScript application workflows](https://github.com/morluto/rea/blob/main/docs/javascript-application-workflows.md)** — 从 JavaScript 应用图追踪功能、比较版本，同时保留静态分析的不确定性。

  REA 官方文档 · 网站 / 应用 · [一手来源](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/docs/javascript-application-workflows.md) · 来源审阅：2026-10-15。
  前提与范围：Evidence from analyze_javascript_application or supported runtime reconciliation. No native engine is required for the static JavaScript path; keep the complete parent Evidence.

- **[Static Android APK analysis](https://github.com/morluto/rea/blob/main/docs/android-analysis.md)** — 经 REA 的 JADX 集成检查 APK、类、方法与引用；结果不等于运行时验证。

  REA 官方文档 · 应用 · [一手来源](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/docs/android-analysis.md) · 来源审阅：2026-10-15。
  前提与范围：Full JDK 17 or newer and caller-supplied jadx-headless-mcp 0.7.1 with the documented digest check. Linux requires a procps-compatible ps for provider process ownership.

- **[Managed-code analysis](https://github.com/morluto/rea/blob/main/docs/managed-code-analysis.md)** — 静态读取 .NET 元数据与 CIL，比较成员并检查声明的 native 边界。

  REA 官方文档 · 应用 · [一手来源](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/docs/managed-code-analysis.md) · 来源审阅：2026-10-15。
  前提与范围：A supported PE/CLI assembly; no native engine is required for metadata/CIL inspection. NativeAOT, IL2CPP and packaged single-file deployments have different boundaries.

- **[Historical web network captures](https://github.com/morluto/rea/blob/main/docs/web-network-captures.md)** — 离线检查已有 HAR、SAZ 等网页流量记录；不会自动抓包或访问记录中的 URL。

  REA 官方文档 · 网站 / 应用 · [一手来源](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/docs/web-network-captures.md) · 来源审阅：2026-10-15。
  前提与范围：A supported existing capture and an explicit format selection. PCAP/TShark workflows are separate and have different host/tool requirements.

- **[Firmware analysis](https://github.com/morluto/rea/blob/main/docs/firmware-analysis.md)** — 用 Binwalk 检查固件区域、用 Unblob 显式提取，并记录工具与制品身份。

  REA 官方文档 · 固件 · [一手来源](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/docs/firmware-analysis.md) · 来源审阅：2026-10-15。
  前提与范围：Caller-supplied Binwalk 3.1.x for inspection; Unblob 26.6.x for extraction. The documented verification scope is Linux x64; extraction needs a new caller-selected output directory.

- **[Browser observation guide](https://rea.tools/guides/browser/)** — 通过官方 Notes 示例关联用户点击、导出请求与下载结果；REA 负责观察。

  REA 官方指南 · 网站 · [一手来源](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/website/evidence/guide-examples.md) · 来源审阅：2026-10-15。
  前提与范围：A user-owned Chrome-family browser, loopback CDP connection and explicitly allowed origins. The recorded upstream example used a separate controller to click; REA did not perform the click.

- **[JavaScript and Electron: follow a CSV export](https://rea.tools/guides/javascript/)** — 官方自建 Notes 样例，从 renderer、preload、IPC 到 CSV 导出建立证据链。

  REA 官方指南 · 应用 · [一手来源](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/website/evidence/guide-examples.md) · 来源审阅：2026-10-15。
  前提与范围：Supported Node.js and REA; no native engine is required for this static fixture. The fixture is source-owned teaching material, not an installed Electron distribution; static findings do not prove execution.


### REA 官方：案例

- **[Aegis: trace a login-code calculation](https://rea.tools/showcase/aegis/)** — 追踪 Aegis APK 的 TOTP 计算，官方公开目标指纹与选取的调查证据。

  REA 官方案例 · 应用 · [一手来源](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/website/evidence/aegis-login-code.md) · 来源审阅：2026-10-15。
  前提与范围：Upstream case: Aegis 3.4.3, REA 6.1.0, jadx-headless-mcp 0.7.1 and OpenJDK 21 on Linux x64. Use the matching official APK for reproduction; this listing did not rerun the case.

- **[DownUnderCTF: masked-squares flag checker](https://rea.tools/showcase/ctf/)** — 官方教育 CTF 案例：从检查函数得到方程，并记录原程序验证过程。

  REA 官方案例 · 二进制 · [一手来源](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/website/evidence/ctf-masked-squares.md) · 来源审阅：2026-10-15。
  前提与范围：Upstream case: public DownUnderCTF 2023 challenge, REA 4.1.0 and Ghidra 12.1.4 on Linux x64. Target hash and source revision are documented; author-reported execution was not repeated here.

- **[DX-Ball: reconstruct sound panning](https://rea.tools/showcase/dx-ball/)** — 根据指令与常量重建单个声像函数；上游报告 3,205 例与 63 字节匹配。

  REA 官方案例 · 游戏 / 二进制 · [一手来源](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/website/evidence/dx-ball-sound-pan.md) · 来源审阅：2026-10-15。
  前提与范围：The matching DX-Ball 1.07 executable and the documented native-analysis environment. The cited reconstruction checks concern one function, not full-game equivalence; no checks were rerun here.

- **[Notion: trace the clipboard bridge](https://rea.tools/showcase/notion/)** — 结合 REA 发现与独立源码阅读追踪剪贴板桥；动态包装器仍有明确限制。

  REA 官方案例 · 应用 · [一手来源](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/website/evidence/notion-clipboard.md) · 来源审阅：2026-10-15。
  前提与范围：Upstream case uses Notion Desktop 7.6.1 packaged JavaScript and REA 4.1.0. The full clipboard route was not automatically paired or observed as a desktop execution.

- **[TH04: recover a DOS bullet-ring helper](https://rea.tools/showcase/th04/)** — 检查 PC-98 DOS 的 16 位弹幕角度辅助函数，并关联固定版本重建与历史编译器检查。

  REA 官方案例 · 游戏 / 二进制 · [一手来源](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/website/evidence/th04-bullet-ring.md) · 来源审阅：2026-10-15。
  前提与范围：The matching original TH04 MAIN.EXE and the documented Ghidra DOS load profile. The showcase covers one helper; full-game reconstruction claims are outside its scope.


### REA 社区集成

- **[dsh-mcp-rea](https://github.com/Ersith/dsh-mcp-rea)** — 社区 MCP 适配桥，以精选工具和 CLI 转发缩小宿主需要处理的工具面。

  REA 社区集成 · 网站 / 游戏 / 应用 / 二进制 / 固件 · [一手来源](https://github.com/Ersith/dsh-mcp-rea/blob/main/README.md) · 来源审阅：2026-10-15。
  前提与范围：Requires REA and the relevant analysis providers; distributed as a local bundle rather than a public npm package. Use the documented REA_ENTRY mode for direct execution; PATH fallback invokes a shell. Its README's provider/platform claims may lag upstream; no installation or security audit was performed.

- **[rea-jev](https://github.com/juan-viox/rea-jev)** — Claude Code 社区插件，在固定版本 REA MCP 外增加 Jev 路由和证据检查。

  REA 社区集成 · 应用 / 网站 · [一手来源](https://github.com/juan-viox/rea-jev/blob/main/README.md) · 来源审阅：2026-10-15。
  前提与范围：Claude Code, supported Node.js and the plugin's documented macOS/Linux environment. Optional Jev service credentials enable external model calls; excerpts may be sent to that service. Hooks fail open on provider failure; they are not a security guarantee.

- **[rea-casebook](https://github.com/pablodiazjorge/rea-casebook)** — Claude Code mod 汇集收到的 REA Evidence、追踪 unknown，并校验发现所引用的证据 ID。

  REA 社区集成 · 二进制 · [一手来源](https://github.com/pablodiazjorge/rea-casebook/blob/main/README.md) · 来源审阅：2026-10-15。
  前提与范围：README requires Claude Code 2.1.296 or newer and an MCP server registered under the name rea. Developed with REA 6.4.0 and Ghidra 12.1 on Windows; broader behavior was not tested here. Evidence IDs being present does not itself prove a conclusion is correct.


### REA 社区练习

- **[rea-playbook](https://github.com/jinshi666888/rea-playbook)** — 提供 Electron 练习目标、Evidence 提取与 MCP 探测，区分离线展示和真正调用 REA。

  REA 社区学习资源 · 二进制 · [一手来源](https://github.com/jinshi666888/rea-playbook/blob/main/README.md) · 来源审阅：2026-10-15。
  前提与范围：README pins the real-analysis path to rea-agents 6.3.0 and lists supported Node.js versions. The offline demo reads bundled results without running REA; its tests were not rerun here.

- **[rea-lab](https://github.com/pablodiazjorge/rea-lab)** — Windows REA/Ghidra 实验室，提供已知答案挑战、公开研究、上游贡献与限制说明。

  REA 社区学习资源 · 二进制 · [一手来源](https://github.com/pablodiazjorge/rea-lab/blob/main/README.md) · 来源审阅：2026-10-15。
  前提与范围：The documented environment uses Windows 11, REA 6.4.0 and Ghidra 12.1.4. Study results are author-reported and task/model-specific, not independently reproduced by this index. Code and documentation use different licenses; inspect the relevant repository notices.


### REA 社区调查案例

- **[PicoPrint: LX-D02 printer investigation](https://github.com/bigtower17/picoprint)** — 作者报告以 REA 开始 Android 调查，再借助独立 Hermes 工具实现 Windows BLE 打印。

  作者报告的混合工具流程 · 应用 / 固件 · [一手来源](https://github.com/morluto/rea/discussions/4152) · 来源审阅：2026-10-15。
  前提与范围：Project README lists Windows 10/11, Bluetooth LE, an LX-D02 printer and Go 1.25+ to build. REA's stated role was readiness/device discovery and investigation framing; hermes-dec handled Hermes v98. Hardware behavior and author-reported results were not reproduced here.


### 独立 MCP 集成

<details>
<summary>展开 13 条资源</summary>

- **[Hex-Rays IDA MCP](https://github.com/HexRaysSA/ida-mcp)** — Hex-Rays 官方 MCP 服务，让 agent 操作 IDA 数据库，支持无界面分析和可选 GUI 联动。

  独立 Agent 集成 · 二进制 · [一手来源](https://github.com/HexRaysSA/ida-mcp/blob/main/README.md) · 来源审阅：2026-10-15。
  前提与范围：IDA 9.4+ with idalib, Python 3.11+, Git and uv; the GUI plugin is optional for headless use.

- **[GhidraMCP](https://github.com/LaurieWired/GhidraMCP)** — 通过 Ghidra 扩展和 MCP 桥接提供反编译、符号导航与重命名，支持 GUI 和无界面运行。

  独立 Agent 集成 · 二进制 · [一手来源](https://github.com/LaurieWired/GhidraMCP/blob/main/README.md) · 来源审阅：2026-10-15。
  前提与范围：Match the extension to the documented Ghidra release; Python 3.10+ for the bridge, with additional PyGhidra requirements for headless mode.

- **[Binary Ninja MCP (official)](https://dev-docs.binary.ninja/guide/mcp.html)** — Binary Ninja 自带的 MCP 接口向 agent 提供函数、符号、反汇编、中间语言和反编译文本。

  独立 Agent 集成 · 二进制 · [一手来源](https://dev-docs.binary.ninja/guide/mcp.html) · 来源审阅：2026-10-15。
  前提与范围：Reviewed in the development manual: use a build containing MCP. GUI server uses HTTP; headless stdio requires Commercial or Ultimate on macOS/Linux.

- **[Binary Ninja MCP (fosdickio)](https://github.com/fosdickio/binary_ninja_mcp)** — 社区维护的 Binary Ninja 插件与 MCP 桥接，支持在多个已打开的二进制目标间切换。

  独立 Agent 集成 · 二进制 · [一手来源](https://github.com/fosdickio/binary_ninja_mcp/blob/main/README.md) · 来源审阅：2026-10-15。
  前提与范围：Binary Ninja, Python 3.12+ and an MCP client; install the plugin separately from the client bridge.

- **[IDA Pro MCP (mrexodia)](https://github.com/mrexodia/ida-pro-mcp)** — 已有工作流可参考的社区 IDA 集成；维护者目前推荐迁移到 Hex-Rays 官方 MCP 服务。

  独立 Agent 集成 · 二进制 · [一手来源](https://github.com/mrexodia/ida-pro-mcp/blob/main/README.md) · 来源审阅：2026-10-15。
  前提与范围：IDA Pro rather than IDA Free, Python 3.11+ and an MCP client; consult the upstream migration notice before choosing a new setup.

- **[Radare2 MCP Server](https://github.com/radareorg/radare2-mcp)** — 基于 radare2 原生接口的 MCP 服务，提供二进制分析、会话复用和可配置的只读访问。

  独立 Agent 集成 · 二进制 · [一手来源](https://github.com/radareorg/radare2-mcp/blob/main/README.md) · 来源审阅：2026-10-15。
  前提与范围：A compatible radare2 build and r2pm, plus an MCP client; advanced HTTP session features depend on the radare2 ABI.

- **[JADX-AI-MCP](https://github.com/zinja-coder/jadx-ai-mcp)** — 结合 JADX 插件与 Python MCP 服务，读取 Android 反编译代码、资源、交叉引用和调试上下文。

  独立 Agent 集成 · 应用 · [一手来源](https://github.com/zinja-coder/jadx-ai-mcp/blob/jadx-ai/README.md) · 来源审阅：2026-10-15。
  前提与范围：JADX with the plugin and the separate JADX MCP Server component; upstream lists Java 11+ and Python 3.10+.

- **[frida-mcp (yfe404)](https://github.com/yfe404/frida-mcp)** — Frida MCP 服务，提供持久插桩会话、运行时检查和 Android 静态代码与动态现场之间的导航。

  独立 Agent 集成 · 应用 / 游戏 · [一手来源](https://github.com/yfe404/frida-mcp/blob/main/README.md) · 来源审阅：2026-10-15。
  前提与范围：Node.js 20+, Frida 17 and an accessible target; on-device operations require the documented device/frida-server setup.

- **[Super Trouper](https://github.com/crissyfield/super-trouper)** — 单个可执行文件形式的 Frida MCP 服务，用于发现设备、管理进程会话和加载插桩脚本。

  独立 Agent 集成 · 应用 / 游戏 · [一手来源](https://github.com/crissyfield/super-trouper/blob/main/README.md) · 来源审阅：2026-10-15。
  前提与范围：Published host binaries target macOS/Linux; target connectivity must support Frida. Source builds need Go, CGO and a matching Frida Core DevKit.

- **[LLDB MCP](https://lldb.llvm.org/use/mcp.html)** — LLDB 官方 MCP 接口提供调试会话与命令，使 agent 可以设置断点、检查内存和单步执行。

  独立 Agent 集成 · 二进制 / 应用 · [一手来源](https://lldb.llvm.org/use/mcp.html) · 来源审阅：2026-10-15。
  前提与范围：An LLDB distribution/build containing lldb-mcp and a compatible stdio MCP client; debug-target access follows the host platform's requirements.

- **[RenderDoc MCP](https://github.com/scarletfantasy/renderdoc-mcp)** — 向 Agent 开放已有 RenderDoc 捕获文件，分步检查帧、管线、资源和着色器。

  独立 Agent 集成 · 游戏 / 应用 · [一手来源](https://github.com/scarletfantasy/renderdoc-mcp/blob/main/README.md) · 来源审阅：2026-10-16T01:05:01Z。
  前提与范围：Windows and replayable .rdc capture; maintainer baseline is RenderDoc 1.43. Optional native Python backend needs a source-built binding.

- **[Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp)** — 连接 Agent 与 Chrome，检查实时页面、调试网络并记录性能轨迹。

  独立 Agent 集成 · 网站 · [一手来源](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/README.md) · 来源审阅：2026-10-16T01:05:01Z。
  前提与范围：Supported Node.js LTS, Chrome, and an MCP client; selected browser profile and target must be available locally.

- **[Playwright MCP](https://github.com/microsoft/playwright-mcp)** — 通过结构化无障碍快照驱动浏览器交互，调查可复现的网页行为。

  独立 Agent 集成 · 网站 · [一手来源](https://github.com/microsoft/playwright-mcp/blob/main/README.md) · 来源审阅：2026-10-16T01:05:01Z。
  前提与范围：Node.js 18+ and an MCP client; the upstream also offers a separate CLI-and-skills approach for coding agents.

</details>


### 独立 Agent 工作流

<details>
<summary>展开 5 条资源</summary>

- **[r2ai](https://github.com/radareorg/r2ai)** — 在 radare2 内使用本地或远程模型，辅助解释函数、改善命名和反编译结果。

  独立 Agent 集成 · 二进制 · [一手来源](https://github.com/radareorg/r2ai/blob/master/README.md) · 来源审阅：2026-10-15。
  前提与范围：radare2 with the matching r2ai/decai plugins; configure a local model or the credentials required by the selected remote provider.

- **[DAILA](https://github.com/mahaloz/DAILA)** — 跨 IDA、Ghidra、Binary Ninja 与 angr-management 的 AI 助手，用于函数摘要和命名辅助。

  独立 Agent 集成 · 二进制 · [一手来源](https://github.com/mahaloz/DAILA/blob/main/README.md) · 来源审阅：2026-10-15。
  前提与范围：A supported decompiler and dailalib; configure a model backend. Ghidra requires the documented PyGhidra setup.

- **[RevEng.AI Ghidra Plugin](https://github.com/RevEngAI/plugin-ghidra)** — 将 Ghidra 接入 RevEng.AI，用于函数相似性匹配、名称恢复、AI 解释及辅助标注。

  独立 Agent 集成 · 二进制 · [一手来源](https://github.com/RevEngAI/plugin-ghidra/blob/main/README.md) · 来源审阅：2026-10-15。
  前提与范围：A compatible Ghidra/Java build and a RevEng.AI API key; creating service-side analysis uploads the selected binary.

- **[Claude Reverse Engineering Skill](https://github.com/EncidXVII/claude-reverse-engineering-skill)** — 社区 agent skill，覆盖分诊、无界面导出和证据报告，并明确说明 REA 及其他 MCP 服务的工作流。

  独立 Agent 集成 · 应用 / 二进制 · [一手来源](https://github.com/EncidXVII/claude-reverse-engineering-skill/blob/main/README.md) · 来源审阅：2026-10-15。
  前提与范围：An Agent Skills-compatible client and Python 3.8+ for bundled scripts; analysis engines and MCP servers are configured separately.

- **[SpecterOps Reverse Engineering Skills](https://github.com/SpecterOps/skills/tree/main/plugins/reverse-engineering)** — 针对 Binary Ninja 与 Ghidra 的分析 skills，提供 MCP 工具使用、分析步骤和标注方法。

  独立 Agent 集成 · 二进制 · [一手来源](https://github.com/SpecterOps/skills/blob/main/plugins/reverse-engineering/README.md) · 来源审阅：2026-10-15。
  前提与范围：Configure the chosen Binary Ninja or Ghidra MCP integration separately; the skill package does not install or wrap those servers.

</details>


### 游戏分析工具

<details>
<summary>展开 4 条资源</summary>

- **[RenderDoc](https://github.com/baldurk/renderdoc)** — 检查自己游戏或图形应用的帧捕获、绘制调用、着色器和图形资源。

  基础工具 · 游戏 / 应用 · [一手来源](https://github.com/baldurk/renderdoc/blob/v1.x/README.md) · 来源审阅：2026-10-16T01:05:01Z。
  前提与范围：Supported graphics API and replay platform; upstream supports captures of your own, open-source, or free projects. Metal is not supported.

- **[AssetRipper](https://github.com/AssetRipper/AssetRipper)** — 分析 Unity 游戏文件，检查资源依赖并将支持的资源转换为 Unity 工程格式。

  基础工具 · 游戏 · [一手来源](https://github.com/AssetRipper/AssetRipper/blob/master/README.md) · 来源审阅：2026-10-16T01:05:01Z。
  前提与范围：Unity 3.5.0–6000.4.X coverage varies by version; GPL-3.0 open-source edition, with separate premium features.

- **[Cpp2IL](https://github.com/SamboyCoding/Cpp2IL)** — 结合二进制与元数据分析，从 Unity IL2CPP 构建恢复托管表示；重建能力仍在开发中。

  基础工具 · 游戏 / 应用 / 二进制 · [一手来源](https://github.com/SamboyCoding/Cpp2IL/blob/development/README.md) · 来源审阅：2026-10-16T01:05:01Z。
  前提与范围：Compatible Unity build and metadata; current development branch is a major rewrite and primarily targets .NET 9.0.

- **[Il2CppDumper](https://github.com/Perfare/Il2CppDumper)** — 恢复 IL2CPP 元数据及占位程序集，为原生分析工具生成辅助脚本；不会还原方法代码。

  基础工具 · 游戏 / 应用 / 二进制 · [一手来源](https://github.com/Perfare/Il2CppDumper/blob/master/README.md) · 来源审阅：2026-10-16T01:05:01Z。
  前提与范围：Matching IL2CPP executable and global-metadata.dat; documented Unity support is 5.3–2022.2.

</details>


### 网站分析工具

<details>
<summary>展开 1 条资源</summary>

- **[mitmproxy](https://github.com/mitmproxy/mitmproxy)** — 通过交互代理、Web 界面或可脚本化命令行检查和记录 HTTP 流量。

  基础工具 · 网站 / 应用 · [一手来源](https://github.com/mitmproxy/mitmproxy/blob/main/README.md) · 来源审阅：2026-10-16T01:05:01Z。
  前提与范围：Configure the client proxy; HTTPS inspection requires the appropriate local trust configuration. Saved captures and live interception are distinct workflows.

</details>


### 原生分析工具

<details>
<summary>展开 5 条资源</summary>

- **[Ghidra](https://github.com/NationalSecurityAgency/ghidra)** — 开源二进制分析套件，提供反汇编、反编译、图形分析及 Java/Python 自动化接口。

  基础工具 · 二进制 / 游戏 / 固件 · [一手来源](https://github.com/NationalSecurityAgency/ghidra/blob/master/README.md) · 来源审阅：2026-10-15。
  前提与范围：An official Ghidra release and its required JDK; extension and script compatibility must match the installed release.

- **[radare2](https://github.com/radareorg/radare2)** — 可脚本化的命令行逆向框架，支持多架构二进制检查、反汇编、调试和修改。

  基础工具 · 二进制 / 游戏 · [一手来源](https://github.com/radareorg/radare2/blob/master/README.md) · 来源审阅：2026-10-15。
  前提与范围：Use the release/build for your host; decompilers and other optional functionality may require separate plugins.

- **[Cutter](https://github.com/rizinorg/cutter)** — 基于 Rizin 的图形逆向工作台，提供可扩展视图及 Ghidra 反编译器集成。

  基础工具 · 二进制 / 游戏 · [一手来源](https://github.com/rizinorg/cutter/blob/dev/README.md) · 来源审阅：2026-10-15。
  前提与范围：Desktop builds are available for Linux, macOS and Windows; use plugins compatible with the selected Cutter release.

- **[ImHex](https://github.com/WerWolv/ImHex)** — 带二进制模式语言、结构化数据检查及可视化功能的十六进制编辑器，适合理解文件格式。

  基础工具 · 二进制 / 游戏 / 固件 · [一手来源](https://github.com/WerWolv/ImHex/blob/master/README.md) · 来源审阅：2026-10-15。
  前提与范围：Desktop build or web edition; some data sources and features depend on the platform and selected build.

- **[Detect It Easy](https://github.com/horsicq/Detect-It-Easy)** — 结合格式解析器、签名和可编程启发式规则进行文件识别与静态检查。

  基础工具 · 二进制 / 游戏 · [一手来源](https://github.com/horsicq/Detect-It-Easy/blob/master/README.md) · 来源审阅：2026-10-15。
  前提与范围：Use the project-linked DIE-engine releases for the host platform; identification results require analyst interpretation.

</details>


### 调试与动态分析

<details>
<summary>展开 5 条资源</summary>

- **[Frida](https://github.com/frida/frida)** — 动态插桩工具，用脚本观察和分析运行中的原生及托管进程行为。

  基础工具 · 应用 / 游戏 · [一手来源](https://github.com/frida/frida/blob/main/README.md) · 来源审阅：2026-10-15。
  前提与范围：Host bindings or CLI tools and a supported target setup; mobile/server/Gadget and signing requirements vary by platform.

- **[Qiling](https://github.com/qilingframework/qiling)** — 在 CPU 仿真之上补充操作系统、文件系统和 API 行为的 Python 框架，用于可插桩的二进制分析。

  基础工具 · 二进制 / 固件 · [一手来源](https://github.com/qilingframework/qiling/blob/master/README.md) · 来源审阅：2026-10-15。
  前提与范围：A supported Python environment and the target's required root filesystem/libraries; emulation coverage varies by platform.

- **[x64dbg](https://github.com/x64dbg/x64dbg)** — Windows 二进制调试器，通过反汇编、内存视图和插件分析没有源码的程序。

  基础工具 · 二进制 · [一手来源](https://github.com/x64dbg/x64dbg/blob/development/README.md) · 来源审阅：2026-10-15。
  前提与范围：Windows; choose x32dbg or x64dbg according to the executable's architecture.

- **[GDB](https://sourceware.org/gdb/)** — 支持本地与远程调试，可控制执行并检查运行中或崩溃后的程序状态。

  基础工具 · 二进制 / 游戏 · [一手来源](https://www.sourceware.org/gdb/) · 来源审阅：2026-10-15。
  前提与范围：A GDB build supporting the target architecture and a permitted local process, core dump, simulator or remote debug endpoint.

- **[rr](https://github.com/rr-debugger/rr)** — 记录进程执行并在 GDB 下重放，便于重复检查现场和反向执行。

  基础工具 · 二进制 · [一手来源](https://github.com/rr-debugger/rr/blob/master/README.md) · 来源审阅：2026-10-15。
  前提与范围：Linux with supported CPU performance counters; VM use depends on counter virtualization and the project's hardware requirements.

</details>


### Android 工具

<details>
<summary>展开 3 条资源</summary>

- **[JADX](https://github.com/skylot/jadx)** — 将 Dex 反编译为 Java 的 CLI/GUI 工具，提供 Android 资源解码、代码导航和引用搜索。

  基础工具 · 应用 · [一手来源](https://github.com/skylot/jadx/blob/master/README.md) · 来源审阅：2026-10-15。
  前提与范围：64-bit Java 11+ unless using a bundled runtime; decompilation can be incomplete and should be checked against bytecode.

- **[Apktool](https://github.com/iBotPeaches/Apktool)** — 将 Android 资源与 smali 解码为项目目录，并支持重新构建修改后的安装包。

  基础工具 · 应用 · [一手来源](https://github.com/iBotPeaches/Apktool/blob/main/README.md) · 来源审阅：2026-10-15。
  前提与范围：A supported Java runtime and the release-specific launcher; rebuilding is distinct from recovering original Java source.

- **[Androguard](https://github.com/androguard/androguard)** — 用于 APK/DEX 元数据、字节码及引用分析的 Python 工具集；v5 源码分支还提供 agent skills 和 MCP 文档。

  基础工具 · 应用 · [一手来源](https://github.com/androguard/androguard/blob/master/README.md) · 来源审阅：2026-10-15。
  前提与范围：Version-sensitive: the reviewed README distinguishes the v5 source tree from PyPI 4.1.4; v5 extras require additional Rust/Python components.

</details>


### .NET 工具

<details>
<summary>展开 2 条资源</summary>

- **[ILSpy](https://github.com/icsharpcode/ILSpy)** — .NET 程序集浏览器与 C# 反编译器，支持完整项目导出、元数据检查和命令行处理。

  基础工具 · 应用 · [一手来源](https://github.com/icsharpcode/ILSpy/blob/master/README.md) · 来源审阅：2026-10-15。
  前提与范围：Choose a desktop or ILSpyCmd release and its matching .NET runtime; frontend and operating-system support are release-dependent.

- **[dnSpyEx](https://github.com/dnSpyEx/dnSpy)** — dnSpy 的社区延续项目，可在没有原始源码时调试和编辑 .NET 程序集。

  基础工具 · 应用 · [一手来源](https://github.com/dnSpyEx/dnSpy/blob/master/README.md) · 来源审阅：2026-10-15。
  前提与范围：Windows desktop workflow; Unity debugging requires the companion runtime setup documented by the project.

</details>


### JavaScript 与 Electron 工具

<details>
<summary>展开 2 条资源</summary>

- **[@electron/asar](https://github.com/electron/asar)** — Electron 官方归档工具，可列出和提取 ASAR 内容，便于检查打包后的 JavaScript 与应用资源。

  基础工具 · 应用 / 网站 · [一手来源](https://github.com/electron/asar/blob/main/README.md) · 来源审阅：2026-10-15。
  前提与范围：The reviewed release requires Node.js 22.12+; extraction reveals archive contents, not missing source maps or original source names.

- **[webcrack](https://github.com/j4k0xb/webcrack)** — 识别支持的 JavaScript 混淆模式，并拆解 webpack/Browserify bundle，改善代码可读性。

  基础工具 · 应用 / 网站 · [一手来源](https://github.com/j4k0xb/webcrack/blob/master/README.md) · 来源审阅：2026-10-15。
  前提与范围：The reviewed README specifies Node.js 22 or 24; results depend on the obfuscator/bundler patterns present in the input.

</details>


### WebAssembly 工具

<details>
<summary>展开 2 条资源</summary>

- **[WABT](https://github.com/WebAssembly/wabt)** — WebAssembly 二进制与文本转换、节区检查、验证、解释执行及 C 转换工具集。

  基础工具 · 网站 / 二进制 · [一手来源](https://github.com/WebAssembly/wabt/blob/main/README.md) · 来源审阅：2026-10-15。
  前提与范围：Select a release supporting the module's WebAssembly features; optional proposals may require explicit flags.

- **[wasm-tools](https://github.com/bytecodealliance/wasm-tools)** — Bytecode Alliance 提供的 CLI 与 Rust 库，用于检查 WebAssembly 模块、元数据、组件和 WIT 接口。

  基础工具 · 网站 / 二进制 · [一手来源](https://github.com/bytecodealliance/wasm-tools/blob/main/README.md) · 来源审阅：2026-10-15。
  前提与范围：Use prebuilt release artifacts or a Rust toolchain; proposal/component support depends on the selected release.

</details>


### 固件工具

<details>
<summary>展开 3 条资源</summary>

- **[Binwalk](https://github.com/ReFirmLabs/binwalk)** — 识别固件中的嵌入格式并按需提取内容，辅以熵分析帮助初步分诊。

  基础工具 · 固件 · [一手来源](https://github.com/ReFirmLabs/binwalk/blob/master/README.md) · 来源审阅：2026-10-15。
  前提与范围：The current v3 implementation is Rust-based; extraction needs the appropriate external tools or the documented container environment.

- **[unblob](https://github.com/onekey-sec/unblob)** — 递归提取二进制数据中的归档与文件系统，同时报告数据块边界和未识别区域。

  基础工具 · 固件 · [一手来源](https://github.com/onekey-sec/unblob/blob/main/README.md) · 来源审阅：2026-10-15。
  前提与范围：Python package plus external extractors, or the bundled Docker image; check the project's dependency inventory for the formats needed.

- **[Ghidra Firmware Utilities](https://github.com/al3xtjames/ghidra-firmware-utils)** — 面向 PCI Option ROM、UEFI 固件卷、Intel Flash Descriptor 和 coreboot 镜像的 Ghidra 加载器与辅助脚本。

  基础工具 · 固件 · [一手来源](https://github.com/al3xtjames/ghidra-firmware-utils/blob/master/README.md) · 来源审阅：2026-10-15。
  前提与范围：The reviewed build instructions require Ghidra 12.0+ and JDK 21+; build against the same Ghidra/JRE environment used for analysis.

</details>


### 二进制分析库

<details>
<summary>展开 4 条资源</summary>

- **[Unicorn Engine](https://github.com/unicorn-engine/unicorn)** — 多架构 CPU 仿真引擎，可控制寄存器、内存和 hook，执行选定的指令片段。

  基础工具 · 二进制 / 游戏 / 固件 · [一手来源](https://github.com/unicorn-engine/unicorn/blob/master/README.md) · 来源审阅：2026-10-15。
  前提与范围：Use a supported binding and explicitly supply the CPU state and memory model; it is a CPU emulator rather than a complete OS environment.

- **[angr](https://github.com/angr/angr)** — 结合控制流恢复、符号执行、数据流分析和反编译的 Python 二进制分析框架。

  基础工具 · 二进制 · [一手来源](https://github.com/angr/angr/blob/master/README.md) · 来源审阅：2026-10-15。
  前提与范围：A compatible Python 3 environment; useful results require an appropriate model of program inputs, state and external functions.

- **[LIEF](https://github.com/lief-project/LIEF)** — 对 ELF、PE、Mach-O 等可执行文件格式进行结构化解析与修改的库。

  基础工具 · 二进制 · [一手来源](https://github.com/lief-project/LIEF/blob/main/README.md) · 来源审阅：2026-10-15。
  前提与范围：C++, Python or Rust integration; check the distinction between core and extended features for the selected distribution.

- **[Capstone](https://github.com/capstone-engine/capstone)** — 提供统一 API 和指令细节的多架构反汇编库，适合构建自定义二进制分析流程。

  基础工具 · 二进制 · [一手来源](https://github.com/capstone-engine/capstone/blob/next/README.md) · 来源审阅：2026-10-15。
  前提与范围：Select a library/binding release supporting the target ISA and mode; the next branch can differ from stable releases.

</details>


### 二进制对比工具

<details>
<summary>展开 2 条资源</summary>

- **[Diaphora](https://github.com/joxeankoret/diaphora)** — 基于 IDA 的二进制差异分析工具，可匹配函数并迁移名称、注释与类型信息。

  基础工具 · 二进制 / 游戏 · [一手来源](https://github.com/joxeankoret/diaphora/blob/master/README.md) · 来源审阅：2026-10-15。
  前提与范围：IDA with Python 3 support; richer pseudocode and microcode comparisons depend on the corresponding decompiler capabilities.

- **[BinDiff](https://github.com/google/bindiff)** — 比较反汇编后的二进制文件，定位不同版本中的对应函数与代码变化。

  基础工具 · 二进制 / 游戏 · [一手来源](https://github.com/google/bindiff/blob/main/README.md) · 来源审阅：2026-10-15。
  前提与范围：Requires a separate supported disassembler/export pipeline; upstream documents IDA Pro, Binary Ninja and Ghidra configurations.

</details>


### 学习资源

<details>
<summary>展开 4 条资源</summary>

- **[OpenSecurityTraining2](https://ost2.fyi/)** — 免费的自主学习课程，提供逆向工程、固件和系统基础等学习路线。

  学习资源 · 二进制 · [一手来源](https://ost2.fyi/Learning-Paths.html) · 来源审阅：2026-10-15。
  前提与范围：Browser access; choose classes according to their published prerequisites and lab requirements.

- **[pwn.college: Reverse Engineering](https://pwn.college/program-security/reverse-engineering/)** — 包含托管练习的逆向工程课程，覆盖函数、数据访问、静态工具和动态工具。

  学习资源 · 二进制 · [一手来源](https://pwn.college/program-security/reverse-engineering/) · 来源审阅：2026-10-15。
  前提与范围：Browser access and the platform's account/environment setup for interactive challenges.

- **[Reverse Engineering for Beginners](https://beginners.re/)** — Dennis Yurichev 编写的免费逆向入门书，以汇编与编译后程序理解为核心，提供多语言版本。

  学习资源 · 二进制 · [一手来源](https://beginners.re/) · 来源审阅：2026-10-15。
  前提与范围：A browser or PDF reader; use the toolchains relevant to the exercises being followed.

- **[The Official Radare2 Book](https://book.rada.re/)** — radare2 官方实践参考，覆盖分析、反汇编、脚本、调试及相关插件。

  学习资源 · 二进制 · [一手来源](https://book.rada.re/) · 来源审阅：2026-10-15。
  前提与范围：Upstream lists radare2 5.8.x as the minimum and recommends a current release for following the examples.

</details>


### 相关资源目录

- **[Awesome Reverse Engineering](https://github.com/morluto/awesome-reverse-engineering)** — REA 维护者整理的通用逆向资源目录，适合查找基础知识与相邻工具。

  REA 维护者的相关目录 · 网站 / 游戏 / 应用 / 二进制 / 固件 · [一手来源](https://github.com/morluto/awesome-reverse-engineering/blob/main/README.md) · 来源审阅：2026-10-15。
  前提与范围：Individual tools retain their own requirements and licenses. Inclusion in this companion list does not establish REA integration or compatibility.

- **[Awesome REA Cases](https://github.com/songshikang0111/awesome-REA-cases)** — 中英双语的 REA 与其他 AI 辅助逆向案例合集，附来源并区分作者报告、进行中的工作和复现状态。

  REA 社区学习资源 · 网站 / 游戏 / 应用 / 二进制 / 固件 · [一手来源](https://github.com/songshikang0111/awesome-REA-cases/blob/main/README.md) · 来源审阅：2026-10-16T01:08:16Z。
  前提与范围：A discovery index; review each case's original source, redistribution rights, and evidence status before reproducing it.
<!-- END GENERATED CATALOG -->

## 相关项目与调研

广泛的逆向索引可看 [morluto/awesome-reverse-engineering](https://github.com/morluto/awesome-reverse-engineering)。其他 REA 目录包括 [kaixinbaba/awesome-rea](https://github.com/kaixinbaba/awesome-rea) 和 [jyjyxt/awesome-rea](https://github.com/jyjyxt/awesome-rea)。本仓库重点提供任务选择、明确的工具关系和可运行的入门样例。

首批筛选依据见[高 Star 仓库对标](docs/benchmark-research.zh-CN.md)、[REA 生态调研](docs/rea-ecosystem.zh-CN.md)和[工具全景](docs/tool-landscape.zh-CN.md)。数据附采集时间，增长目标见[路线图](docs/roadmap.md)。

欢迎补充有用资源、纠正过时条件，或贡献小型可复现实验。请先看[贡献指南](CONTRIBUTING.md)。本仓库原创说明、脚本和样例使用 [MIT 许可证](LICENSE)，外部项目保留原许可证。请使用自己拥有或获准分析的目标。
