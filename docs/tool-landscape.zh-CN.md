# REA 周边工具：按任务选型

> **存档快照**：本文保留 2026-10-15 合集首发时的选型说明，其中的数量与版本边界以当时为准，不随目录更新。当前收录数量请看 [README 目录](../README.zh-CN.md#目录)中的计数，或运行 `python3 scripts/catalog.py`；其他文档见[文档索引](README.zh-CN.md)。

本页保留首轮 **47 个资源**的选型说明：15 个独立 agent/MCP 集成、28 个基础工具和 4 个学习入口。首轮核验日期为 **2026-10-15**。每条均阅读了项目自己的 README 或官方文档，核验等级为 `source-reviewed`；本轮工具目录未安装或运行这些工具，因此不把资料核验写成兼容性测试。随后补充的 8 条 Website/Game 资源见下节；截至 2026-10-15 首发时，工具目录共 55 条，此后继续增补。

可复用数据见 [tool-resources.json](../data/tool-resources.json)。`verified_at` 表示资料检查日期。数据中的 GitHub 证据链接固定到审读时的提交；本页正文的仓库链接指向当前文档，官网页面则是访问时的地址。这些链接说明资料来源，不是执行记录。

## 与 REA 的关系

首发补充的 Website/Game 资源为 [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp)、[Playwright MCP](https://github.com/microsoft/playwright-mcp)、[mitmproxy](https://github.com/mitmproxy/mitmproxy)、[RenderDoc](https://github.com/baldurk/renderdoc)、[RenderDoc MCP](https://github.com/scarletfantasy/renderdoc-mcp)、[AssetRipper](https://github.com/AssetRipper/AssetRipper)、[Cpp2IL](https://github.com/SamboyCoding/Cpp2IL) 与 [Il2CppDumper](https://github.com/Perfare/Il2CppDumper)。其前提和原文证据已写入数据记录；它们是独立配套工具，未据此宣称 REA 已原生集成。网站按 `targets` 标签提供 Website、Game、App、Binary、Firmware、Protocol 六类入口（Protocol 于 2026-10-16 加入，定义见[目录格式（英文）](../data/README.md)），同一资源可出现在多个适用目标中。

| 数据标签 | 含义 |
| --- | --- |
| `independent-agent-integration` | 独立于 REA 的 MCP、AI 插件或 agent skill。“官方”指相应工具厂商的官方实现，不表示 REA 官方维护。 |
| `foundation` | 可辅助理解文件、代码和运行时的基础工具；收录不代表 REA 已内置或验证其集成。 |
| `learning` | 训练逆向分析能力的课程、书籍和实践入口。 |
| `independent-reconstruction` | 首发后加入的独立重建案例：有记录的重建项目，与 REA 没有已确认的关联。这类记录统一存放在 tool-resources.json 中（放在 rea-resources.json 会被校验拒绝），不属于 REA 生态项目。 |

[Claude Reverse Engineering Skill](https://github.com/EncidXVII/claude-reverse-engineering-skill/blob/main/README.md) 的作者明确提到 REA 工作流；这仍是社区项目的说明。其余资源应按各自文档配置，不能从“都支持 MCP”推导出它们与 REA 存在官方集成关系。

## 先按问题缩小范围

下面是目录的选型建议，可从最贴近目标的行开始。

| 手里的目标或问题 | 优先查看 | 希望得到的证据 |
| --- | --- | --- |
| 不知道文件类型、打包方式或内部结构 | [Detect It Easy](https://github.com/horsicq/Detect-It-Easy)、[ImHex](https://github.com/WerWolv/ImHex) | 真实头部、节区、偏移与结构，而不只看扩展名。 |
| 原生二进制中的某个功能如何实现 | [Ghidra](https://github.com/NationalSecurityAgency/ghidra)、[GhidraMCP](https://github.com/LaurieWired/GhidraMCP)、[Hex-Rays IDA MCP](https://github.com/HexRaysSA/ida-mcp) | 入口函数、调用关系、数据流与汇编对应位置。 |
| 已在 Binary Ninja 中开展分析 | [官方 MCP 文档](https://dev-docs.binary.ninja/guide/mcp.html)、[社区插件](https://github.com/fosdickio/binary_ninja_mcp) | 当前分析数据库中的函数、IL 和符号；按安装版本选择接口。 |
| 静态结果需要运行时验证 | [Frida](https://github.com/frida/frida)、[LLDB MCP](https://lldb.llvm.org/use/mcp.html)、[GDB](https://sourceware.org/gdb/) | 参数、返回值、内存、栈帧与实际执行路径。 |
| Android APK 的逻辑与资源 | [JADX](https://github.com/skylot/jadx)、[JADX-AI-MCP](https://github.com/zinja-coder/jadx-ai-mcp)、[Apktool](https://github.com/iBotPeaches/Apktool) | Java/smali 对应关系、manifest、资源与引用。 |
| .NET 程序集 | [ILSpy](https://github.com/icsharpcode/ILSpy)、[dnSpyEx](https://github.com/dnSpyEx/dnSpy) | C#、IL、元数据，以及需要时的调试现场。 |
| Electron、打包 JavaScript 或 WASM | [asar](https://github.com/electron/asar)、[webcrack](https://github.com/j4k0xb/webcrack)、[WABT](https://github.com/WebAssembly/wabt)、[wasm-tools](https://github.com/bytecodealliance/wasm-tools) | 包内文件、模块边界、导入导出及 WASM 文本/组件接口。 |
| 固件、嵌套归档或 UEFI | [Binwalk](https://github.com/ReFirmLabs/binwalk)、[unblob](https://github.com/onekey-sec/unblob)、[Ghidra Firmware Utilities](https://github.com/al3xtjames/ghidra-firmware-utils) | 容器边界、文件系统、固件模块与入口。 |
| 两个版本到底改了什么 | [BinDiff](https://github.com/google/bindiff)、[Diaphora](https://github.com/joxeankoret/diaphora) | 函数匹配、变化位置、可迁移的已有标注。 |

## MCP 与 agent 工作流

| 项目 | 能解决的问题 | 使用条件 |
| --- | --- | --- |
| [Hex-Rays IDA MCP](https://github.com/HexRaysSA/ida-mcp) | Hex-Rays 官方 MCP 服务，让 agent 操作 IDA 数据库，支持无界面分析和可选 GUI 联动。 | IDA 9.4+、idalib、Python 3.11+、Git 和 uv；GUI 插件按需安装。 [来源](https://github.com/HexRaysSA/ida-mcp/blob/main/README.md) |
| [GhidraMCP](https://github.com/LaurieWired/GhidraMCP) | 通过 Ghidra 扩展和 MCP 桥接提供反编译、符号导航与重命名，支持 GUI 和无界面运行。 | Ghidra 与扩展版本必须匹配；桥接需要 Python，无界面模式另有 PyGhidra 条件。 [来源](https://github.com/LaurieWired/GhidraMCP/blob/main/README.md) |
| [Binary Ninja MCP (official)](https://dev-docs.binary.ninja/guide/mcp.html) | Binary Ninja 自带的 MCP 接口向 agent 提供函数、符号、反汇编、中间语言和反编译文本。 | 核验的是开发版文档；GUI 使用 HTTP，无界面 stdio 需要 macOS/Linux 的 Commercial 或 Ultimate。 [来源](https://dev-docs.binary.ninja/guide/mcp.html) |
| [Binary Ninja MCP (fosdickio)](https://github.com/fosdickio/binary_ninja_mcp) | 社区维护的 Binary Ninja 插件与 MCP 桥接，支持在多个已打开的二进制目标间切换。 | 需安装 Binary Ninja 插件及客户端桥接；README 要求 Python 3.12+。 [来源](https://github.com/fosdickio/binary_ninja_mcp/blob/main/README.md) |
| [IDA Pro MCP (mrexodia)](https://github.com/mrexodia/ida-pro-mcp) | 已有工作流可参考的社区 IDA 集成；维护者目前推荐迁移到 Hex-Rays 官方 MCP 服务。 | 需要 IDA Pro；新配置先看维护者指向官方服务的迁移说明。 [来源](https://github.com/mrexodia/ida-pro-mcp/blob/main/README.md) |
| [Radare2 MCP Server](https://github.com/radareorg/radare2-mcp) | 基于 radare2 原生接口的 MCP 服务，提供二进制分析、会话复用和可配置的只读访问。 | 需要匹配的 radare2/r2pm；HTTP 多会话功能受 radare2 ABI 约束。 [来源](https://github.com/radareorg/radare2-mcp/blob/main/README.md) |
| [r2ai](https://github.com/radareorg/r2ai) | 在 radare2 内使用本地或远程模型，辅助解释函数、改善命名和反编译结果。 | 需要 radare2 插件及本地模型或远程模型服务凭据。 [来源](https://github.com/radareorg/r2ai/blob/master/README.md) |
| [DAILA](https://github.com/mahaloz/DAILA) | 跨 IDA、Ghidra、Binary Ninja 与 angr-management 的 AI 助手，用于函数摘要和命名辅助。 | 需要受支持的反编译器和模型后端；Ghidra 按文档启用 PyGhidra。 [来源](https://github.com/mahaloz/DAILA/blob/main/README.md) |
| [RevEng.AI Ghidra Plugin](https://github.com/RevEngAI/plugin-ghidra) | 将 Ghidra 接入 RevEng.AI，用于函数相似性匹配、名称恢复、AI 解释及辅助标注。 | 需要 RevEng.AI API key；创建服务端分析会上传所选二进制。 [来源](https://github.com/RevEngAI/plugin-ghidra/blob/main/README.md) |
| [JADX-AI-MCP](https://github.com/zinja-coder/jadx-ai-mcp) | 结合 JADX 插件与 Python MCP 服务，读取 Android 反编译代码、资源、交叉引用和调试上下文。 | JADX 插件和独立 Python MCP Server 都要安装；Java 11+、Python 3.10+。 [来源](https://github.com/zinja-coder/jadx-ai-mcp/blob/jadx-ai/README.md) |
| [frida-mcp (yfe404)](https://github.com/yfe404/frida-mcp) | Frida MCP 服务，提供持久插桩会话、运行时检查和 Android 静态代码与动态现场之间的导航。 | Node.js 20+、Frida 17；设备端操作需可连接的目标及 frida-server。 [来源](https://github.com/yfe404/frida-mcp/blob/main/README.md) |
| [Super Trouper](https://github.com/crissyfield/super-trouper) | 单个可执行文件形式的 Frida MCP 服务，用于发现设备、管理进程会话和加载插桩脚本。 | 预编译主机版本面向 macOS/Linux；目标需满足 Frida 连接条件。 [来源](https://github.com/crissyfield/super-trouper/blob/main/README.md) |
| [LLDB MCP](https://lldb.llvm.org/use/mcp.html) | LLDB 官方 MCP 接口提供调试会话与命令，使 agent 可以设置断点、检查内存和单步执行。 | 需要包含 lldb-mcp 的 LLDB 构建；不能默认系统预装版本已具备此接口。 [来源](https://lldb.llvm.org/use/mcp.html) |
| [Claude Reverse Engineering Skill](https://github.com/EncidXVII/claude-reverse-engineering-skill) | 社区 agent skill，覆盖分诊、无界面导出和证据报告，并明确说明 REA 及其他 MCP 服务的工作流。 | Python 3.8+；分析引擎和 MCP 服务独立配置，属于社区项目。 [来源](https://github.com/EncidXVII/claude-reverse-engineering-skill/blob/main/README.md) |
| [SpecterOps Reverse Engineering Skills](https://github.com/SpecterOps/skills/tree/main/plugins/reverse-engineering) | 针对 Binary Ninja 与 Ghidra 的分析 skills，提供 MCP 工具使用、分析步骤和标注方法。 | 只提供方法与参考，Binary Ninja/Ghidra MCP 需要另行安装配置。 [来源](https://github.com/SpecterOps/skills/blob/main/plugins/reverse-engineering/README.md) |

## 基础工具

这些工具覆盖不同分析层次。选择一个反编译器并不会替代运行时观察；选择 CPU 仿真器也不会自动获得完整的目标操作系统环境。

| 项目 | 能解决的问题 | 使用条件 |
| --- | --- | --- |
| [Ghidra](https://github.com/NationalSecurityAgency/ghidra) | 开源二进制分析套件，提供反汇编、反编译、图形分析及 Java/Python 自动化接口。 | 使用正式发行包及对应 JDK；扩展需匹配 Ghidra 版本。 [来源](https://github.com/NationalSecurityAgency/ghidra/blob/master/README.md) |
| [radare2](https://github.com/radareorg/radare2) | 可脚本化的命令行逆向框架，支持多架构二进制检查、反汇编、调试和修改。 | 按主机平台选择发行版；反编译器等能力可能来自独立插件。 [来源](https://github.com/radareorg/radare2/blob/master/README.md) |
| [Cutter](https://github.com/rizinorg/cutter) | 基于 Rizin 的图形逆向工作台，提供可扩展视图及 Ghidra 反编译器集成。 | Linux/macOS/Windows 桌面工具；插件需匹配发布版本。 [来源](https://github.com/rizinorg/cutter/blob/dev/README.md) |
| [Frida](https://github.com/frida/frida) | 动态插桩工具，用脚本观察和分析运行中的原生及托管进程行为。 | 依赖目标平台的附加、server/Gadget 或签名条件。 [来源](https://github.com/frida/frida/blob/main/README.md) |
| [JADX](https://github.com/skylot/jadx) | 将 Dex 反编译为 Java 的 CLI/GUI 工具，提供 Android 资源解码、代码导航和引用搜索。 | Java 11+ 或内置运行时；反编译不保证完整，关键结论需对照字节码。 [来源](https://github.com/skylot/jadx/blob/master/README.md) |
| [Apktool](https://github.com/iBotPeaches/Apktool) | 将 Android 资源与 smali 解码为项目目录，并支持重新构建修改后的安装包。 | 需要对应版本的 Java/启动器；重建 APK 与恢复 Java 源码是不同能力。 [来源](https://github.com/iBotPeaches/Apktool/blob/main/README.md) |
| [Androguard](https://github.com/androguard/androguard) | 用于 APK/DEX 元数据、字节码及引用分析的 Python 工具集；v5 源码分支还提供 agent skills 和 MCP 文档。 | 当前 README 区分 v5 源码与 PyPI 4.1.4；不能直接把 v5 MCP 能力归给旧包。 [来源](https://github.com/androguard/androguard/blob/master/README.md) |
| [ILSpy](https://github.com/icsharpcode/ILSpy) | .NET 程序集浏览器与 C# 反编译器，支持完整项目导出、元数据检查和命令行处理。 | 选择桌面版或 ILSpyCmd 及匹配的 .NET 运行时。 [来源](https://github.com/icsharpcode/ILSpy/blob/master/README.md) |
| [dnSpyEx](https://github.com/dnSpyEx/dnSpy) | dnSpy 的社区延续项目，可在没有原始源码时调试和编辑 .NET 程序集。 | Windows 工作流；Unity 调试另需配套运行时。 [来源](https://github.com/dnSpyEx/dnSpy/blob/master/README.md) |
| [@electron/asar](https://github.com/electron/asar) | Electron 官方归档工具，可列出和提取 ASAR 内容，便于检查打包后的 JavaScript 与应用资源。 | 当前 README 要求 Node.js 22.12+；解包本身不恢复缺失的 source map。 [来源](https://github.com/electron/asar/blob/main/README.md) |
| [webcrack](https://github.com/j4k0xb/webcrack) | 识别支持的 JavaScript 混淆模式，并拆解 webpack/Browserify bundle，改善代码可读性。 | 当前 README 指定 Node.js 22 或 24；效果取决于混淆和打包模式。 [来源](https://github.com/j4k0xb/webcrack/blob/master/README.md) |
| [WABT](https://github.com/WebAssembly/wabt) | WebAssembly 二进制与文本转换、节区检查、验证、解释执行及 C 转换工具集。 | 选择支持目标 WASM 特性的版本；部分提案需要显式选项。 [来源](https://github.com/WebAssembly/wabt/blob/main/README.md) |
| [wasm-tools](https://github.com/bytecodealliance/wasm-tools) | Bytecode Alliance 提供的 CLI 与 Rust 库，用于检查 WebAssembly 模块、元数据、组件和 WIT 接口。 | 可用预编译版本或 Rust 工具链；组件/提案支持随版本变化。 [来源](https://github.com/bytecodealliance/wasm-tools/blob/main/README.md) |
| [Binwalk](https://github.com/ReFirmLabs/binwalk) | 识别固件中的嵌入格式并按需提取内容，辅以熵分析帮助初步分诊。 | v3 为 Rust 实现；提取能力依赖外部工具或完整容器环境。 [来源](https://github.com/ReFirmLabs/binwalk/blob/master/README.md) |
| [unblob](https://github.com/onekey-sec/unblob) | 递归提取二进制数据中的归档与文件系统，同时报告数据块边界和未识别区域。 | 需 Python 包及外部解包器，或带依赖的容器镜像。 [来源](https://github.com/onekey-sec/unblob/blob/main/README.md) |
| [Ghidra Firmware Utilities](https://github.com/al3xtjames/ghidra-firmware-utils) | 面向 PCI Option ROM、UEFI 固件卷、Intel Flash Descriptor 和 coreboot 镜像的 Ghidra 加载器与辅助脚本。 | 当前构建要求 Ghidra 12.0+、JDK 21+，仍须与实际安装环境匹配。 [来源](https://github.com/al3xtjames/ghidra-firmware-utils/blob/master/README.md) |
| [Qiling](https://github.com/qilingframework/qiling) | 在 CPU 仿真之上补充操作系统、文件系统和 API 行为的 Python 框架，用于可插桩的二进制分析。 | 需为目标准备对应的根文件系统和依赖库；平台仿真覆盖有边界。 [来源](https://github.com/qilingframework/qiling/blob/master/README.md) |
| [Unicorn Engine](https://github.com/unicorn-engine/unicorn) | 多架构 CPU 仿真引擎，可控制寄存器、内存和 hook，执行选定的指令片段。 | 要自行提供 CPU 状态、内存和外部行为；不是完整操作系统模拟器。 [来源](https://github.com/unicorn-engine/unicorn/blob/master/README.md) |
| [angr](https://github.com/angr/angr) | 结合控制流恢复、符号执行、数据流分析和反编译的 Python 二进制分析框架。 | 需要 Python 环境，以及合理的输入、状态和外部函数模型。 [来源](https://github.com/angr/angr/blob/master/README.md) |
| [LIEF](https://github.com/lief-project/LIEF) | 对 ELF、PE、Mach-O 等可执行文件格式进行结构化解析与修改的库。 | C++/Python/Rust 接口；核心与扩展版功能需分别核对。 [来源](https://github.com/lief-project/LIEF/blob/main/README.md) |
| [Capstone](https://github.com/capstone-engine/capstone) | 提供统一 API 和指令细节的多架构反汇编库，适合构建自定义二进制分析流程。 | 按 ISA 和模式选择绑定/版本；开发分支与稳定版本可能不同。 [来源](https://github.com/capstone-engine/capstone/blob/next/README.md) |
| [ImHex](https://github.com/WerWolv/ImHex) | 带二进制模式语言、结构化数据检查及可视化功能的十六进制编辑器，适合理解文件格式。 | 桌面或 Web 版本；数据来源及功能可用性因平台而异。 [来源](https://github.com/WerWolv/ImHex/blob/master/README.md) |
| [x64dbg](https://github.com/x64dbg/x64dbg) | Windows 二进制调试器，通过反汇编、内存视图和插件分析没有源码的程序。 | Windows；根据目标位数选择 x32dbg 或 x64dbg。 [来源](https://github.com/x64dbg/x64dbg/blob/development/README.md) |
| [GDB](https://sourceware.org/gdb/) | 支持本地与远程调试，可控制执行并检查运行中或崩溃后的程序状态。 | 调试器需支持目标架构；可使用本地进程、core dump 或远程调试端点。 [来源](https://www.sourceware.org/gdb/) |
| [rr](https://github.com/rr-debugger/rr) | 记录进程执行并在 GDB 下重放，便于重复检查现场和反向执行。 | Linux；需要支持的 CPU 性能计数器，虚拟机另需计数器虚拟化。 [来源](https://github.com/rr-debugger/rr/blob/master/README.md) |
| [Diaphora](https://github.com/joxeankoret/diaphora) | 基于 IDA 的二进制差异分析工具，可匹配函数并迁移名称、注释与类型信息。 | 依赖 IDA 与 Python 3；伪代码/microcode 比较取决于反编译器能力。 [来源](https://github.com/joxeankoret/diaphora/blob/master/README.md) |
| [BinDiff](https://github.com/google/bindiff) | 比较反汇编后的二进制文件，定位不同版本中的对应函数与代码变化。 | 需要单独的反汇编/导出流程；官方说明覆盖 IDA、Binary Ninja 和 Ghidra。 [来源](https://github.com/google/bindiff/blob/main/README.md) |
| [Detect It Easy](https://github.com/horsicq/Detect-It-Easy) | 结合格式解析器、签名和可编程启发式规则进行文件识别与静态检查。 | 从项目指向的 DIE-engine Releases 获取程序；签名与启发式结果仍需判断。 [来源](https://github.com/horsicq/Detect-It-Easy/blob/master/README.md) |

## 学习入口

| 项目 | 能解决的问题 | 使用条件 |
| --- | --- | --- |
| [OpenSecurityTraining2](https://ost2.fyi/) | 免费的自主学习课程，提供逆向工程、固件和系统基础等学习路线。 | 按课程说明选择前置知识与实验环境。 [来源](https://ost2.fyi/Learning-Paths.html) |
| [pwn.college: Reverse Engineering](https://pwn.college/program-security/reverse-engineering/) | 包含托管练习的逆向工程课程，覆盖函数、数据访问、静态工具和动态工具。 | 托管挑战需要平台账户及其运行环境。 [来源](https://pwn.college/program-security/reverse-engineering/) |
| [Reverse Engineering for Beginners](https://beginners.re/) | Dennis Yurichev 编写的免费逆向入门书，以汇编与编译后程序理解为核心，提供多语言版本。 | 可在线阅读或下载 PDF；练习使用书中相应工具链。 [来源](https://beginners.re/) |
| [The Official Radare2 Book](https://book.rada.re/) | radare2 官方实践参考，覆盖分析、反汇编、脚本、调试及相关插件。 | 官方列出最低 radare2 5.8.x，建议使用当前发布版本。 [来源](https://book.rada.re/) |

## 配置前特别值得核对的版本边界

- **IDA：** [mrexodia 的 README](https://github.com/mrexodia/ida-pro-mcp/blob/main/README.md) 已推荐 [Hex-Rays 官方 MCP](https://github.com/HexRaysSA/ida-mcp/blob/main/README.md)。官方当前要求 IDA 9.4+ 与 idalib；旧教程中的 GUI 插件流程不应直接视为新安装的默认流程。
- **Binary Ninja：** 本次审读的是[开发版 MCP 文档](https://dev-docs.binary.ninja/guide/mcp.html)。GUI 与无界面服务的传输方式、系统及授权条件不同，应先确认手中的版本实际包含哪一个。
- **LLDB：** [官方文档](https://lldb.llvm.org/use/mcp.html) 使用 `lldb-mcp`；收录不表示任意系统附带的 LLDB 都已包含它。
- **Androguard：** [当前 README](https://github.com/androguard/androguard/blob/master/README.md) 把 v5 源码树与 PyPI 4.1.4 区分开来。文档中的 v5 MCP、skills 和新依赖需要对应源码环境。
- **Ghidra 插件：** [Ghidra](https://github.com/NationalSecurityAgency/ghidra/blob/master/README.md)、[GhidraMCP](https://github.com/LaurieWired/GhidraMCP/blob/main/README.md) 和[固件扩展](https://github.com/al3xtjames/ghidra-firmware-utils/blob/master/README.md) 的版本/JDK 要求应分别核对，不能只升级其中一个组件。
- **RevEng.AI：** [插件文档](https://github.com/RevEngAI/plugin-ghidra/blob/main/README.md) 说明创建分析会上传二进制。选择该服务前要确认目标文件可以交给所配置的服务端处理。

## 可复用的分析顺序

1. **识别目标。** 记录文件摘要、格式、架构、版本和待回答的问题。
2. **收集静态证据。** 保留函数地址、文件偏移、导入导出、交叉引用和必要的反汇编片段。
3. **缩小假设。** 将反编译器结果与分析者推断分开，明确还缺少什么证据。
4. **按需验证运行时。** 只为关键假设设计观察点，保留输入、调用栈和相关返回值。
5. **形成可复查的结论。** 写出结论、证据位置、使用的工具/版本、未覆盖的路径和下一步验证方法。

这个顺序是本目录的工作建议，不是任何工具已通过端到端验证的声明。

## 收录与维护标准

优先收录项目自身维护的一手入口，要求用途明确，且能补足一个实际逆向分析环节。同一引擎的多种接口只有在部署方式、维护归属或迁移价值不同的情况下分别保留。没有用大量通用 AI 框架、重复 fork 或不相关攻防工具增加条目数，也没有用 Star 数量代替功能判断。

更新条目时，应重新阅读功能与安装条件，确认 canonical URL、改名/迁移说明和实际发布状态，再更新 `verified_at`。只有记录了目标、工具版本、执行过程和结果之后，才能另行声明实际测试；一次页面访问不能证明可运行或兼容 REA。
