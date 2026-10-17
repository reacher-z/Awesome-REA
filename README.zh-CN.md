# Awesome Reverse Engineering Anything

整理工具、重建案例与研究论文，帮助理解网站、游戏、应用、原生二进制、固件及通信协议。

<a href="https://awesomerea.org/zh/"><img src="assets/readme-banner.svg" alt="Awesome Reverse Engineering Anything — 覆盖六类逆向目标的工具、案例与论文" width="960"></a>

**[浏览合集 ↗](https://awesomerea.org/zh/) · [精选资源](https://awesomerea.org/zh/resources/) · [研究论文](https://awesomerea.org/zh/papers/) · [English](README.md)**

依据一手来源整理的独立合集，来源核查不代表运行验证。[了解证据、使用条件与核查方法](https://awesomerea.org/zh/about/)。

## 目录

- **目标** · [网站](#website) · [游戏](#game) · [应用](#app) · [原生二进制](#native-binary) · [固件与硬件](#firmware) · [协议](#protocol)

- [论文](#papers) · [案例](https://awesomerea.org/zh/?view=curated&kind=case-study) · [Agent 与 MCP](#agents-and-mcp) · [相关合集](#related-collections) · [学习资料](#references-and-learning) · [仓库索引](#完整仓库索引)

<a id="资源目录"></a>
<a id="resource-catalog"></a>
## 资源

按用途浏览，每条资源只收录一次，单行列出，末尾标注资源类型；论文只在[论文](#论文)部分列出。合集包含独立项目和 [REA](https://github.com/morluto/rea) 相关资源；收录不代表已接入 REA。

<!-- BEGIN GENERATED CATALOG -->
<a id="website"></a>
### Website · 网站

[↑ 返回目录](#目录)

- [**恐龙跑酷：恢复一条加速规则**](https://github.com/morluto/rea/blob/c360cfcd6d7901514b16dd6113eba2e0b0fdf422/website/evidence/calculator-and-dino.md#dinosaur-speed) - REA 的教学案例检查 HTTP 版 t-rex-runner，并重建其速度更新规则。单独进行的受控原游戏检查与新演示对比更新次数，包含浮点递增越过名义速度阈值的一步。 <sub>案例 · REA</sub>
- [**webcrack**](https://github.com/j4k0xb/webcrack) - 识别支持的 JavaScript 混淆模式，并拆解 webpack/Browserify 打包文件，改善代码可读性。 <sub>工具</sub>
- [**WABT**](https://github.com/WebAssembly/wabt) - WebAssembly 二进制与文本转换、节区检查、验证、解释执行及 C 转换工具集。 <sub>工具 · WebAssembly</sub>
- [**wasm-tools**](https://github.com/bytecodealliance/wasm-tools) - Bytecode Alliance 提供的 CLI 与 Rust 库，用于检查 WebAssembly 模块、元数据、组件和 WIT 接口。 <sub>工具 · WebAssembly</sub>
- [**Chrome DevTools MCP**](https://github.com/ChromeDevTools/chrome-devtools-mcp) - 连接智能体与 Chrome，检查实时页面、调试网络并记录性能轨迹。 <sub>集成 · 独立 MCP</sub>
- [**mitmproxy**](https://github.com/mitmproxy/mitmproxy) - 通过交互代理、Web 界面或可脚本化命令行检查和记录 HTTP 流量。 <sub>工具</sub>
- [**Playwright MCP**](https://github.com/microsoft/playwright-mcp) - 通过结构化无障碍快照驱动浏览器交互，调查可复现的网页行为。 <sub>集成 · 独立 MCP</sub>
- [**Wakaru**](https://github.com/pionxzh/wakaru) - 通过还原已识别的压缩与转译模式，从发布后的 JavaScript 包中恢复可读模块，支持拆包与现代语法恢复，便于分析生产环境前端代码。 <sub>工具</sub>
- [**Spectral**](https://github.com/spectral-mcp/spectral) - 用 LLM 分析捕获的应用 HTTP 流量，生成 MCP 工具、OpenAPI 3.1 规范或 GraphQL 模式；完成抓包与认证配置后，生成的工具可直接调用已观察到的 API。 <sub>集成 · 独立 Agent</sub>
- [**jsdeob-workbench**](https://github.com/Owl4444/jsdeob-workbench) - 在查看 JavaScript AST 和变量作用域的同时，可视化编排 Babel 转换链；保存分析项目与可复用插件，逐步简化混淆脚本。 <sub>工具</sub>
- [**Browser Reverse Engineering Toolkit 浏览器逆向工程工具集**](https://github.com/Dvurechensky/Browser.Reverse.Engineering.Toolkit) - 采集浏览器会话证据，在持久 Chromium 会话中抓取网站，并根据已保存的捕获数据生成离线架构／API 报告，以及 OpenAPI、SDK 和模拟服务器草稿。 <sub>工具</sub>

<a id="game"></a>
### Game · 游戏

[↑ 返回目录](#目录)

- [**DX-Ball：重建声音声像计算**](https://rea.tools/showcase/dx-ball/) - 根据指令与常量重建单个声像函数；上游报告 3,205 例与 63 字节匹配。 <sub>案例 · REA</sub>
- [**TH04：恢复 DOS 子弹环辅助函数**](https://rea.tools/showcase/th04/) - 检查 PC-98 DOS 的 16 位弹幕角度辅助函数，并关联固定版本重建与历史编译器检查。 <sub>案例 · REA</sub>
- [**Super Mario 64 DS：带重定位核对的匹配反编译**](https://github.com/tangosdev/sm64ds-decomp) - 将 Super Mario 64 DS 函数重建为 C/C++ 和规则允许的汇编原语，并将编译结果与用户提供的卡带转储对比。独立的重定位目标核对强化匹配检查；PC 移植中的集成进度另行统计。 <sub>案例 · 独立重建</sub>
- [**GoldenEye 007：基于反编译成果的智能体辅助原生移植**](https://github.com/jkdansereau/goldeneye-pc-port) - 在已有 GoldenEye 007 反编译成果之上构建原生 PC 移植，提供宿主平台适配层，并从用户自己的 ROM 提取资产。项目记录智能体协作、渲染对比、试玩范围和尚未解决的平台支持。 <sub>案例 · 独立重建</sub>
- [**ssbu-recomp：明确玩法边界的静态重编译**](https://github.com/Denkishi/ssbu-recomp) - 将 Super Smash Bros. Ultimate 13.0.4 的 AArch64 代码提前转换，并提供带 Vulkan/OpenGL 渲染的 Windows 运行时。项目还将部分角色脚本重建为可编辑 C++，通过差分与确定性测试对比转换代码和源码行为。 <sub>案例 · 独立重建</sub>
- [**KartPad：Mario Kart Wii 重编译的平台集成**](https://github.com/chrissotraidis/kartpad) - 围绕 WiiCompiled 对 Mario Kart Wii 的提前转换实现 Apple 与 Android 平台集成，提供原生图形、输入及可选 Retro Rewind 支持。状态和权利文档区分平台验收、未解决的设备缺陷及游戏内容要求。 <sub>案例 · 独立重建</sub>
- [**BattleShip：AI 辅助的 Super Smash Bros. 原生移植**](https://github.com/vinvirile/BattleShip) - 使用 libultraship 和 Torch 移植已有的 Super Smash Bros. N64 反编译成果。作者介绍了智能体构建的图形、音频对比工具和对照模拟器行为的差分调试，并未将其说成脱离社区既有成果、仅靠卡带自动恢复游戏。 <sub>案例 · 独立重建</sub>
- [**智能体反编译：字节匹配验收复盘**](https://momo5502.com/posts/2026-10-09-game-decompilation/) - Maurice Heumann 介绍如何用基于编译器的函数、重定位、数据和类型检查，取代看似合理的智能体输出。复盘报告 99% 的函数已进入重建源码，全部函数中 83% 达到字节一致；重建代码仍不公开。 <sub>案例 · 独立重建</sub>
- [**IsaacRecomp：将 Flash 游戏字节码转换为原生 C++**](https://github.com/whylurking/IsaacRecomp) - 将 The Binding of Isaac 的 Flash AVM1 字节码转换为 C++ 函数，并提供原生渲染与输入运行时。项目从用户自己的原游戏读取图像和音频，并记录了确定性输入、无界面运行和截图回归检查。 <sub>案例 · 独立重建</sub>
- [**Nanolathe：附研究文档的 Total Annihilation 引擎重实现**](https://github.com/nanolathe-gg/nanolathe) - 用 Go 重实现兼容 Total Annihilation 的策略游戏引擎，公开文件格式研究并提供不同玩法配置。项目区分拟复现的零售版3.1行为、社区补丁研究和有意加入的现代改动，也区分合成检查与依赖原始游戏数据的测试。 <sub>案例 · 独立重建</sub>
- [**TH08：精确源码重建与单独验证的移植**](https://github.com/N0zoM1z0/th08) - 依据原二进制和原编译器重建日版 Touhou 8 的 1.00d 版本，再将恢复的代码适配到其他平台。项目分别记录源码存在、严格函数匹配、完整可执行文件一致性和移植可玩性里程碑。 <sub>案例 · 独立重建</sub>
- [**RenderDoc**](https://github.com/baldurk/renderdoc) - 检查自己游戏或图形应用的帧捕获、绘制调用、着色器和图形资源。 <sub>工具</sub>
- [**AssetRipper**](https://github.com/AssetRipper/AssetRipper) - 分析 Unity 游戏文件，检查资源依赖并将支持的资源转换为 Unity 工程格式。 <sub>工具</sub>
- [**Cpp2IL**](https://github.com/SamboyCoding/Cpp2IL) - 结合二进制与元数据分析，从 Unity IL2CPP 构建恢复托管表示；重建能力仍在开发中。 <sub>工具</sub>
- [**Il2CppDumper**](https://github.com/Perfare/Il2CppDumper) - 恢复 IL2CPP 元数据及占位程序集，为原生分析工具生成辅助脚本；不会还原方法代码。 <sub>工具</sub>
- [**RenderDoc MCP**](https://github.com/scarletfantasy/renderdoc-mcp) - 向智能体开放已有 RenderDoc 捕获文件，分步检查帧、管线、资源和着色器。 <sub>集成 · 独立 MCP</sub>
- [**UndertaleModTool**](https://github.com/UnderminersTeam/UndertaleModTool) - 浏览和修改受支持的 GameMaker 数据文件、提取资源，以及反编译或编译 GML VM 代码；提供房间编辑、脚本化修改、CLI 和可复用的 UndertaleModLib 库。 <sub>工具</sub>
- [**frida-il2cpp-bridge**](https://github.com/vfsfitvnm/frida-il2cpp-bridge) - 在运行中的进程里检查 IL2CPP 类、方法和字段，无需提供 global-metadata.dat 即可跟踪或拦截方法调用，为静态 IL2CPP 转储工具补充运行时观察能力。 <sub>工具</sub>
- [**objdiff**](https://github.com/encounter/objdiff) - 比较参考目标文件与重新编译目标文件中的函数和数据，辅助匹配反编译；显示指令级差异、还原 C++ 符号，并可在源码变更时自动重新构建。 <sub>工具</sub>
- [**UE Explorer**](https://github.com/UE-Explorer/UE-Explorer) - 通过类、属性与依赖树浏览 Unreal 包，反编译和导出 UnrealScript 类、检查字节码，并查看结构化二进制数据。 <sub>工具</sub>
- [**GARbro**](https://github.com/morkt/GARbro) - 像浏览文件夹一样查看已识别的视觉小说资源归档，预览内容，并在提取图像或音频时转换为常用格式。 <sub>工具</sub>
- [**LASRecomp：《织梦岛》静态重编译案例**](https://github.com/peiikai/LASRecomp) - 通过静态重编译，将 2019 年 Switch 版《塞尔达传说：织梦岛》重建为原生桌面程序。作者称大部分代码、工具与逆向工作由 Claude Code 完成，人类负责指导和复核。 <sub>案例 · 独立重建</sub>
- [**Godot 逆向工程工具**](https://github.com/GDRETools/gdsdecomp) - 从已导出的游戏中恢复受支持的 Godot 工程文件、GDScript 与导入资源，提供 PCK 检查与提取、脚本反编译及资源转换，便于分析和重建工程结构。 <sub>工具</sub>
- [**UE4SS（虚幻引擎脚本系统）**](https://github.com/UE4SS-RE/RE-UE4SS) - 通过实时 UObject 属性视图、反射 C++ 头文件导出、属性映射和 Actor 转储分析虚幻引擎游戏；Lua 与 C++ API 可辅助实验和重建游戏结构。 <sub>工具</sub>
- [**FModel 游戏资源浏览器**](https://github.com/4sval/FModel) - 基于 CUE4Parse 浏览虚幻引擎游戏归档，检查资源包和属性，预览并导出资源；2026 年夏季发行版新增 USD 世界导出，可辅助重建受支持的场景内容。 <sub>工具</sub>
- [**PSP Web Recomp 浏览器游戏重编译项目**](https://github.com/snuri00/psp-web-recomp) - 将 PSP MIPS 可执行文件转换为 C++ 与 WebAssembly，配合 PSP 高层仿真运行时和 WebGL2 渲染器；原生跟踪、画面捕获及音频工具可辅助调查游戏移植中缺失的行为。 <sub>项目</sub>
- [**ArkWeb：双游戏动作与碰撞桥接实验**](https://github.com/luki-1/ArkWeb) - 同时运行《漫威蜘蛛侠：重制版》与《蝙蝠侠：阿卡姆骑士》，将哥谭碰撞数据传入蜘蛛侠的物理世界，再将其渲染画面合成到阿卡姆中。这是实验性的运行时桥接，并非恢复出的独立游戏或新引擎。 <sub>案例 · 独立重建</sub>

<a id="app"></a>
### App · 应用

[↑ 返回目录](#目录)

- [**Aegis：追踪登录验证码计算**](https://rea.tools/showcase/aegis/) - 追踪 Aegis APK 的 TOTP 计算，官方公开目标指纹与选取的调查证据。 <sub>案例 · REA</sub>
- [**Notion：追踪剪贴板桥接**](https://rea.tools/showcase/notion/) - 结合 REA 发现与独立源码阅读追踪剪贴板桥；动态包装器仍有明确限制。 <sub>案例 · REA</sub>
- [**ReaCut：视频编辑器重建案例**](https://github.com/Xiangyu-CAS/rea-capcut) - 独立视频编辑器，作者公开了利用 REA 研究剪映／CapCut 行为与项目格式的过程。实现包含本地时间线、FFmpeg 导出，以及实验性的有损草稿导入。 <sub>案例 · 混合工具流程</sub>
- [**zee-rp：重建 Axure RP 11 的受支持文档操作**](https://github.com/LilZeeCN/zee-rp) - 通过二进制记录编解码、考虑引用关系的克隆和受约束的交互写入器，读取并修改受支持的 Axure RP 11 原生文档。CLI 与 MCP 接口提供可检查的编辑操作，并区分离线结构检查和原生应用验收。 <sub>案例 · 独立重建</sub>
- [**Virtual Desktop Streamer：在 Linux 上重建平台适配层**](https://github.com/cudanexus/vd-streamer-linux) - 作者报告通过 Claude Code 与 REA，将 macOS 串流端的捕获、编码、音频和输入层替换为 Linux 实现，同时复用厂商协议库。文档中的目标是桌面串流和视频播放，而非仅 Windows 串流端提供的 VR 游戏串流。 <sub>案例 · 混合工具流程</sub>
- [**Open Claude UI：基于 REA 调查的界面参考组件**](https://github.com/Caho1/open-claude-ui) - 发布 React 组件、动效辅助模块和设计系统笔记，作者将其归因于使用 REA 调查 Claude Desktop。它可作为界面重建案例；观察结果受版本约束，不能证明已完整复刻助手应用或后端。 <sub>案例 · 混合工具流程</sub>
- [**PlxNative：重建原生 webOS 媒体客户端接口**](https://github.com/GLinnik21/plx-native) - 作者用 Ghidra 和编程智能体调查 LG webOS 原生媒体接口后构建的非官方 Plex 客户端。它自行绘制 Rust/OpenGL 界面并使用电视解码器，文档区分宿主测试、模拟器测试和实体设备测试。 <sub>案例 · 独立重建</sub>
- [**Windows Calculator：重建百分比规则**](https://github.com/morluto/rea/blob/c360cfcd6d7901514b16dd6113eba2e0b0fdf422/website/evidence/calculator-and-dino.md#windows-calculator) - REA 案例追踪已安装 Windows Calculator 的模型 DLL，解释乘除运算与其他运算中不同的百分比行为。分析人员选定函数后，对照微软公开源码解释，并通过固定输入的浏览器示例演示。 <sub>案例 · REA</sub>
- [**飞书：作者报告的隔离第二应用实例**](https://benx.ai/blog/posts/rea-reverse-engineer-feishu-dual-instance/) - 作者报告借助 Codex 与 REA 分析，修改独立的 macOS 飞书副本，为其设置不同的应用身份、数据目录和单实例锁。文章描述本地签名与隔离检查，并称原应用保持不变。 <sub>案例 · 混合工具流程</sub>
- [**JADX-AI-MCP**](https://github.com/zinja-coder/jadx-ai-mcp) - 结合 JADX 插件与 Python MCP 服务，读取 Android 反编译代码、资源、交叉引用和调试上下文。 <sub>集成 · 独立 MCP</sub>
- [**frida-mcp (yfe404)**](https://github.com/yfe404/frida-mcp) - Frida MCP 服务，提供持久插桩会话、运行时检查和 Android 静态代码与动态现场之间的导航。 <sub>集成 · 独立 MCP</sub>
- [**Super Trouper**](https://github.com/crissyfield/super-trouper) - 单个可执行文件形式的 Frida MCP 服务，用于发现设备、管理进程会话和加载插桩脚本。 <sub>集成 · 独立 MCP</sub>
- [**Frida**](https://github.com/frida/frida) - 动态插桩工具，用脚本观察和分析运行中的原生及托管进程行为。 <sub>工具</sub>
- [**JADX**](https://github.com/skylot/jadx) - 将 Dex 反编译为 Java 的 CLI/GUI 工具，提供 Android 资源解码、代码导航和引用搜索。 <sub>工具 · Android</sub>
- [**Apktool**](https://github.com/iBotPeaches/Apktool) - 将 Android 资源与 smali 解码为项目目录，并支持重新构建修改后的安装包。 <sub>工具 · Android</sub>
- [**Androguard**](https://github.com/androguard/androguard) - 用于 APK/DEX 元数据、字节码及引用分析的 Python 工具集；v5 源码分支还提供智能体技能和 MCP 文档。 <sub>工具 · Android</sub>
- [**ILSpy**](https://github.com/icsharpcode/ILSpy) - .NET 程序集浏览器与 C# 反编译器，支持完整项目导出、元数据检查和命令行处理。 <sub>工具 · .NET</sub>
- [**dnSpyEx**](https://github.com/dnSpyEx/dnSpy) - dnSpy 的社区延续项目，可在没有原始源码时调试和编辑 .NET 程序集。 <sub>工具 · .NET</sub>
- [**@electron/asar**](https://github.com/electron/asar) - Electron 官方归档工具，可列出和提取 ASAR 内容，便于检查打包后的 JavaScript 与应用资源。 <sub>工具</sub>
- [**Mobile Security Framework（MobSF）**](https://github.com/MobSF/Mobile-Security-Framework-MobSF) - 通过 Web 界面与 API 检查移动应用包，结合静态分析及受支持设备上的动态测试，分析运行时行为与网络流量。 <sub>工具 · Android</sub>
- [**Blutter**](https://github.com/worawit/blutter) - 利用匹配的 Dart 运行时分析 Flutter Android ARM64 AOT 二进制，生成带符号的汇编、对象池转储及面向目标的 Frida 脚本模板，辅助研究编译后的 Dart 应用逻辑。 <sub>工具 · Android</sub>
- [**hermes-dec**](https://github.com/P1sec/hermes-dec) - 解析、反汇编并部分反编译 React Native 的 Hermes 字节码包，展示 HBC 文件头和指令，并生成伪代码以帮助理解编译后的应用逻辑。 <sub>工具</sub>
- [**Recaf 字节码分析与编辑工具**](https://github.com/Col-E/Recaf) - 通过集成反编译器、字节码汇编、引用搜索、映射与去混淆工具检查和修改已编译的 JVM 应用；所审阅的 4.0 预览版还提供基础的只读 Android 字节码分析。 <sub>工具 · JVM</sub>
- [**nibkit 原生界面结构分析工具**](https://github.com/tokenbleed/nibkit) - 将已编译的 iOS/macOS 界面归档解码为对象树、Outlet／Action 连接、自定义类及导航关系，可导出 JSON 或 Mermaid 图，并通过 MCP 提供只读检查命令。 <sub>工具</sub>
- [**AOTopsy Flutter/Dart 静态分析工具**](https://github.com/BroNils/aotopsy) - 静态检查 Flutter/Dart AOT libapp.so 文件，恢复可用元数据、类结构、调用关系及伪代码，无需嵌入 Dart VM 或编译匹配的 SDK，提供 ARM64 与 x86_64 分析路径。 <sub>工具 · Android</sub>
- [**hbctool Hermes 字节码汇编与反汇编工具**](https://github.com/bongtrop/hbctool) - 通过 HASM 文件反汇编和重新汇编受支持的 React Native Hermes 字节码包，为明确支持的旧版 HBC 提供字节码检查与修改能力。 <sub>工具 · Android</sub>
- [**LSX II 音量修正器：重建音量行为**](https://github.com/roberdorfer/kef-lsx-volume) - 根据实测 USB 音量行为，通过 macOS 音频代理将音量键映射到 KEF LSX II 的局域网控制。项目报告音量步进更均匀，同时转发 USB 音频；扬声器固件未修改。 <sub>案例 · 独立重建</sub>

<a id="native-binary"></a>
### Native Binary · 原生二进制

[↑ 返回目录](#目录)

- [**DownUnderCTF：masked-squares 校验器**](https://rea.tools/showcase/ctf/) - 官方教育 CTF 案例：从检查函数得到方程，并记录原程序验证过程。 <sub>案例 · REA</sub>
- [**Ghidra**](https://github.com/NationalSecurityAgency/ghidra) - 开源二进制分析套件，提供反汇编、反编译、图形分析及 Java/Python 自动化接口。 <sub>工具</sub>
- [**radare2**](https://github.com/radareorg/radare2) - 可脚本化的命令行逆向框架，支持多架构二进制检查、反汇编、调试和修改。 <sub>工具</sub>
- [**Cutter**](https://github.com/rizinorg/cutter) - 基于 Rizin 的图形逆向工作台，提供可扩展视图及 Ghidra 反编译器集成。 <sub>工具</sub>
- [**Qiling**](https://github.com/qilingframework/qiling) - 在 CPU 仿真之上补充操作系统、文件系统和 API 行为的 Python 框架，用于可插桩的二进制分析。 <sub>工具</sub>
- [**Unicorn Engine**](https://github.com/unicorn-engine/unicorn) - 多架构 CPU 仿真引擎，可控制寄存器、内存和钩子，执行选定的指令片段。 <sub>工具 · 程序库</sub>
- [**angr**](https://github.com/angr/angr) - 结合控制流恢复、符号执行、数据流分析和反编译的 Python 二进制分析框架。 <sub>工具 · 程序库</sub>
- [**LIEF**](https://github.com/lief-project/LIEF) - 对 ELF、PE、Mach-O 等可执行文件格式进行结构化解析与修改的库。 <sub>工具 · 程序库</sub>
- [**Capstone**](https://github.com/capstone-engine/capstone) - 提供统一 API 和指令细节的多架构反汇编库，适合构建自定义二进制分析流程。 <sub>工具 · 程序库</sub>
- [**ImHex**](https://github.com/WerWolv/ImHex) - 带二进制模式语言、结构化数据检查及可视化功能的十六进制编辑器，适合理解文件格式。 <sub>工具</sub>
- [**x64dbg**](https://github.com/x64dbg/x64dbg) - Windows 二进制调试器，通过反汇编、内存视图和插件分析没有源码的程序。 <sub>工具</sub>
- [**GDB**](https://sourceware.org/gdb/) - 支持本地与远程调试，可控制执行并检查运行中或崩溃后的程序状态。 <sub>工具</sub>
- [**rr**](https://github.com/rr-debugger/rr) - 记录进程执行并在 GDB 下重放，便于重复检查现场和反向执行。 <sub>工具</sub>
- [**Diaphora**](https://github.com/joxeankoret/diaphora) - 基于 IDA 的二进制差异分析工具，可匹配函数并迁移名称、注释与类型信息。 <sub>工具</sub>
- [**BinDiff**](https://github.com/google/bindiff) - 比较反汇编后的二进制文件，定位不同版本中的对应函数与代码变化。 <sub>工具</sub>
- [**Detect It Easy**](https://github.com/horsicq/Detect-It-Easy) - 结合格式解析器、签名和可编程启发式规则进行文件识别与静态检查。 <sub>工具</sub>
- [**objection**](https://github.com/sensepost/objection) - 通过基于 Frida 的命令界面探索运行中的 Android 与 iOS 应用，检查应用存储、内存、运行时对象和插桩后的行为。 <sub>工具</sub>
- [**r2frida**](https://github.com/nowsecure/r2frida) - 结合 radare2 命令与 Frida 插桩，检查桌面和移动目标中本地或远程进程的内存、符号、类及运行时调用。 <sub>工具</sub>
- [**Kaitai Struct 二进制格式描述与解析工具**](https://github.com/kaitai-io/kaitai_struct) - 将已描述的二进制布局转换为可复用的文件与网络报文解析器；同一份 .ksy 规范可通过可视化工具检查，并编译为多种语言，便于把逆向获得的格式知识落实为可互操作的实现。 <sub>工具 · 程序库</sub>
- [**Wireshark 协议分析工具**](https://gitlab.com/wireshark/wireshark) - 将捕获的应用与设备流量解析为协议字段，支持过滤，并由 GUI 与 TShark 共用解析逻辑；自定义解析器可将新识别的报文格式固化下来，辅助比较协议实现。 <sub>工具</sub>

<a id="firmware"></a>
### Firmware · 固件与硬件

[↑ 返回目录](#目录)

- [**PicoPrint：LX-D02 打印机调查**](https://github.com/bigtower17/picoprint) - 作者报告以 REA 开始 Android 调查，再借助独立 Hermes 工具实现 Windows BLE 打印。 <sub>案例 · 混合工具流程</sub>
- [**Binwalk**](https://github.com/ReFirmLabs/binwalk) - 识别固件中的嵌入格式并按需提取内容，辅以熵分析帮助初步分诊。 <sub>工具</sub>
- [**unblob**](https://github.com/onekey-sec/unblob) - 递归提取二进制数据中的归档与文件系统，同时报告数据块边界和未识别区域。 <sub>工具</sub>
- [**Ghidra 固件工具集**](https://github.com/al3xtjames/ghidra-firmware-utils) - 面向 PCI Option ROM、UEFI 固件卷、Intel Flash Descriptor 和 coreboot 镜像的 Ghidra 加载器与辅助脚本。 <sub>工具</sub>
- [**EMBA**](https://github.com/e-m-b-a/emba) - 提取固件，结合静态检查与仿真分析，整理软件组件清单，并生成 Web 报告和 SBOM，供进一步调查。 <sub>工具</sub>
- [**固件分析与比较工具（FACT）**](https://github.com/fkie-cad/FACT_core) - 通过可扩展平台解包和分析固件，使用 Web 界面与 HTTP API 搜索组件内容和分析结果，并比较不同样本。 <sub>工具</sub>
- [**OFRAK**](https://github.com/redballoonsecurity/ofrak) - 通过资源树图形界面与 Python API，递归识别、解包、分析、修改和重新打包固件及二进制格式，并可接入可选反汇编后端。 <sub>工具</sub>
- [**FirmAE**](https://github.com/pr0v3rbs/FirmAE) - 仿真路由器与 IP 摄像机固件，检查网络服务和运行时行为，提供自动仿真检查，以及独立的分析、运行和调试模式。 <sub>工具</sub>
- [**PulseView 信号与协议分析工具**](https://github.com/sigrokproject/pulseview) - 通过 sigrok 的图形前端检查逻辑与模拟波形；协议解码器及分层解码可展示总线消息和更高层的设备操作，便于利用硬件通信记录开展固件与互操作性分析。 <sub>工具</sub>
- [**UEFITool 固件镜像分析工具**](https://github.com/LongSoft/UEFITool) - 将 UEFI 固件镜像解析为可检查的树状结构，并检查其结构；配套的 UEFIExtract 与 UEFIFind 可提取解析后的内容、查找模式，辅助分析固件组件与厂商格式。 <sub>工具</sub>

<a id="protocol"></a>
### Protocols · 协议

[↑ 返回目录](#目录)

- [**open-appleremote：Siri Remote 协议重建**](https://github.com/a-funk/open-appleremote) - 重建第一代 Siri Remote 在 Linux 上的蓝牙报告，解析按键、触摸与 tvOS 风格手势。Python 实现和协议文档区分实测行为、历史报告与推测含义。 <sub>案例 · 独立重建</sub>
- [**GAMEKB-K17：重建宏键盘配置协议**](https://github.com/dvdarkin/gamekb-k17) - 实现 GAMEKB-K17/HCY-K017 宏键盘的厂商 HID 配置协议，写入按键映射、固件宏和 RGB 设置后再读回核对。协议文档区分已测试命令、未确认观察和其他设备的研究结果。 <sub>案例 · 独立重建</sub>
- [**CF632BLE：基于体脂秤协议研究的本地客户端**](https://github.com/guyru/cf632ble) - 根据对厂商 Unique Health 安卓应用的研究，重实现 CF632BLE 体脂秤的 BLE 协议和体成分计算。静态 Web Bluetooth 客户端接收测量数据、管理设备档案，并将历史记录保存在浏览器中。 <sub>案例 · 独立重建</sub>
- [**cooler-lcd：Thermalright 显示屏协议实现**](https://github.com/kristjaningi/cooler-lcd) - 为 Thermalright Vision 散热器显示屏实现 USB 图像传输驱动，并用 Rust 仪表盘替代厂商显示应用。文档所述协议发送报头和 JPEG 帧，通过定期重发避免设备退回品牌标志画面。 <sub>案例 · 独立重建</sub>
- [**hw-harness：扫描仪 USB 协议调查**](https://github.com/cschalle/hw-harness) - 记录作者报告的扫描仪调查：比较厂商驱动的 USB 控制传输与 Linux 驱动的记录，推断初始化、时序及分辨率参数。公开工具负责组织参考采集与比较，并不自动恢复完整协议规范。 <sub>案例 · 独立重建</sub>
- [**Netzob 协议建模与推断框架**](https://github.com/netzob/netzob) - 对通信协议建模并从流量记录推断报文布局，通过配置主动学习来推断协议状态机。Python API 提供报文字段、符号和自动机，用于解析、流量生成及模糊测试。 <sub>工具</sub>
- [**Scapy 报文分析与构造工具**](https://github.com/secdev/scapy) - 使用 Python 编写报文解析、构造、请求／响应匹配及捕获文件分析流程；自定义报文字段与层绑定可将已理解的线格式编码为可操作模型，辅助研究协议行为。 <sub>工具</sub>

<a id="agents-and-mcp"></a>
### Agents & MCP · Agent 与集成

[↑ 返回目录](#目录)

- [**REA — Reverse Engineer Anything**](https://github.com/morluto/rea) - REA 官方 CLI 与 MCP 服务，连接分析工具并保留调查证据及限制。 <sub>项目 · REA</sub>
- [**官方 reverse-engineer-anything 技能**](https://github.com/morluto/rea/tree/main/.agents/skills/reverse-engineer-anything) - 官方面向使用者的调查技能，包含目标路由、连接恢复与证据工作流。 <sub>集成 · REA</sub>
- [**dsh-mcp-rea**](https://github.com/Ersith/dsh-mcp-rea) - 社区 MCP 适配桥，以精选工具和 CLI 转发缩小宿主需要处理的工具面。 <sub>集成 · REA</sub>
- [**rea-jev**](https://github.com/juan-viox/rea-jev) - Claude Code 社区插件，在固定版本 REA MCP 外增加 Jev 路由和证据检查。 <sub>集成 · REA</sub>
- [**rea-casebook**](https://github.com/pablodiazjorge/rea-casebook) - Claude Code mod 汇集收到的 REA Evidence、追踪 unknown，并校验发现所引用的证据 ID。 <sub>集成 · REA</sub>
- [**Hex-Rays IDA MCP**](https://github.com/HexRaysSA/ida-mcp) - Hex-Rays 官方 MCP 服务，让智能体操作 IDA 数据库，支持无界面分析和可选 GUI 联动。 <sub>集成 · 独立 MCP</sub>
- [**GhidraMCP**](https://github.com/LaurieWired/GhidraMCP) - 通过 Ghidra 扩展和 MCP 桥接提供反编译、符号导航与重命名，支持 GUI 和无界面运行。 <sub>集成 · 独立 MCP</sub>
- [**Binary Ninja MCP（官方）**](https://dev-docs.binary.ninja/guide/mcp.html) - Binary Ninja 自带的 MCP 接口向智能体提供函数、符号、反汇编、中间语言和反编译文本。 <sub>集成 · 独立 MCP</sub>
- [**Binary Ninja MCP（fosdickio）**](https://github.com/fosdickio/binary_ninja_mcp) - 社区维护的 Binary Ninja 插件与 MCP 桥接，支持在多个已打开的二进制目标间切换。 <sub>集成 · 独立 MCP</sub>
- [**IDA Pro MCP（mrexodia）**](https://github.com/mrexodia/ida-pro-mcp) - 已有工作流可参考的社区 IDA 集成；维护者目前推荐迁移到 Hex-Rays 官方 MCP 服务。 <sub>集成 · 独立 MCP</sub>
- [**Radare2 MCP Server**](https://github.com/radareorg/radare2-mcp) - 基于 radare2 原生接口的 MCP 服务，提供二进制分析、会话复用和可配置的只读访问。 <sub>集成 · 独立 MCP</sub>
- [**r2ai**](https://github.com/radareorg/r2ai) - 在 radare2 内使用本地或远程模型，辅助解释函数、改善命名和反编译结果。 <sub>集成 · 独立 Agent</sub>
- [**DAILA**](https://github.com/mahaloz/DAILA) - 跨 IDA、Ghidra、Binary Ninja 与 angr-management 的 AI 助手，用于函数摘要和命名辅助。 <sub>集成 · 独立 Agent</sub>
- [**RevEng.AI Ghidra 插件**](https://github.com/RevEngAI/plugin-ghidra) - 将 Ghidra 接入 RevEng.AI，用于函数相似性匹配、名称恢复、AI 解释及辅助标注。 <sub>集成 · 独立 Agent</sub>
- [**LLDB MCP**](https://lldb.llvm.org/use/mcp.html) - LLDB 官方 MCP 接口提供调试会话与命令，使智能体可以设置断点、检查内存和单步执行。 <sub>集成 · 独立 MCP</sub>
- [**Claude 逆向工程技能**](https://github.com/EncidXVII/claude-reverse-engineering-skill) - 社区智能体技能，覆盖分诊、无界面导出和证据报告，并明确说明 REA 及其他 MCP 服务的工作流。 <sub>集成 · 独立 Agent</sub>
- [**SpecterOps 逆向工程技能**](https://github.com/SpecterOps/skills/tree/main/plugins/reverse-engineering) - 针对 Binary Ninja 与 Ghidra 的分析技能，提供 MCP 工具使用、分析步骤和标注方法。 <sub>集成 · 独立 Agent</sub>

<a id="related-collections"></a>
### Related Collections · 相关合集

[↑ 返回目录](#目录)

- [**Awesome Reverse Engineering**](https://github.com/morluto/awesome-reverse-engineering) - REA 维护者整理的通用逆向资源目录，适合查找基础知识与相邻工具。 <sub>合集</sub>
- [**Awesome REA Cases**](https://github.com/songshikang0111/awesome-REA-cases) - 中英双语的 REA 与其他 AI 辅助逆向案例合集，附来源并区分作者报告、进行中的工作和复现状态。 <sub>合集</sub>
- [**awesome-rea（yibie）：关注验证的项目与实践报告**](https://github.com/yibie/awesome-rea) - 围绕明确的验收检查整理 AI 辅助游戏反编译、原生移植、静态重编译和工具，并另设实践文章与讨论分类。适合寻找一手报告，比较不同项目如何定义正确性。 <sub>合集</sub>
- [**Awesome REA/Decompiled Games：按游戏组织的重建项目目录**](https://github.com/HaozheH3/awesome-rea-games) - 按原游戏整理反编译、源码重建、重编译、原生移植和演示，通过对照表链接相关项目，并区分启动器、引擎工作、作者分享的展示与源码重建成果。 <sub>合集</sub>

<a id="references-and-learning"></a>
### References & Learning · 文档与学习资料

[↑ 返回目录](#目录)

- [**安装与客户端配置**](https://github.com/morluto/rea/blob/main/docs/installation.md) - 安装、客户端配置、分析引擎依赖及按任务检查就绪状态的官方入口。 <sub>文档 · REA</sub>
- [**CLI 与 Evidence**](https://github.com/morluto/rea/blob/main/docs/cli.md) - 保存完整 Evidence，再提取摘要或模块视图，适合脚本与可复现记录。 <sub>文档 · REA</sub>
- [**MCP 接口约定与生成目录**](https://github.com/morluto/rea/blob/main/docs/mcp-contracts.md#generated-catalog) - 官方工具协议、能力发现和 Evidence 语义；适合集成与核对实际工具边界。 <sub>文档 · REA</sub>
- [**原生二进制调查**](https://github.com/morluto/rea/blob/main/docs/native-investigation.md) - 从函数清单到指令、伪代码和引用链的原生二进制调查流程。 <sub>文档 · REA</sub>
- [**跨层 JavaScript 应用工作流**](https://github.com/morluto/rea/blob/main/docs/javascript-application-workflows.md) - 从 JavaScript 应用图追踪功能、比较版本，同时保留静态分析的不确定性。 <sub>文档 · REA</sub>
- [**Android APK 静态分析**](https://github.com/morluto/rea/blob/main/docs/android-analysis.md) - 经 REA 的 JADX 集成检查 APK、类、方法与引用；结果不等于运行时验证。 <sub>文档 · REA</sub>
- [**托管代码分析**](https://github.com/morluto/rea/blob/main/docs/managed-code-analysis.md) - 静态读取 .NET 元数据与 CIL，比较成员并检查声明的原生代码边界。 <sub>文档 · REA</sub>
- [**历史网站网络记录**](https://github.com/morluto/rea/blob/main/docs/web-network-captures.md) - 离线检查已有 HAR、SAZ 等网页流量记录；不会自动抓包或访问记录中的 URL。 <sub>文档 · REA</sub>
- [**固件分析**](https://github.com/morluto/rea/blob/main/docs/firmware-analysis.md) - 用 Binwalk 检查固件区域、用 Unblob 显式提取，并记录工具与制品身份。 <sub>文档 · REA</sub>
- [**浏览器观察指南**](https://rea.tools/guides/browser/) - 通过官方 Notes 示例关联用户点击、导出请求与下载结果；REA 负责观察。 <sub>文档 · REA</sub>
- [**JavaScript 与 Electron：追踪 CSV 导出**](https://rea.tools/guides/javascript/) - 官方自建 Notes 样例，从 renderer、preload、IPC 到 CSV 导出建立证据链。 <sub>文档 · REA</sub>
- [**rea-playbook**](https://github.com/jinshi666888/rea-playbook) - 提供 Electron 练习目标、Evidence 提取与 MCP 探测，区分离线展示和真正调用 REA。 <sub>学习资料</sub>
- [**rea-lab**](https://github.com/pablodiazjorge/rea-lab) - Windows REA/Ghidra 实验室，提供已知答案挑战、公开研究、上游贡献与限制说明。 <sub>研究</sub>
- [**OpenSecurityTraining2**](https://ost2.fyi/) - 免费的自主学习课程，提供逆向工程、固件和系统基础等学习路线。 <sub>学习资料</sub>
- [**pwn.college：逆向工程**](https://pwn.college/program-security/reverse-engineering/) - 包含托管练习的逆向工程课程，覆盖函数、数据访问、静态工具和动态工具。 <sub>学习资料</sub>
- [**逆向工程入门**](https://beginners.re/) - Dennis Yurichev 编写的免费逆向入门书，以汇编与编译后程序理解为核心，提供多语言版本。 <sub>学习资料</sub>
- [**radare2 官方手册**](https://book.rada.re/) - radare2 官方实践参考，覆盖分析、反汇编、脚本、调试及相关插件。 <sub>学习资料</sub>
<!-- END GENERATED CATALOG -->

<!-- BEGIN GENERATED PAPERS -->
<a id="papers"></a>
## 论文

收录 **31 篇论文**，涵盖逆向工程智能体评测、反编译、协议推断、固件分析，以及网站、游戏和应用重建。部分论文也出现在精选资源目录中，两者数量不可相加。发表状态与研究范围分别标注，中文标题为译名。

[浏览论文目录](https://awesomerea.org/zh/papers/) · [完整书目 JSON](data/papers.json) · [推荐论文](https://github.com/reacher-z/Awesome-REA/issues/new?template=paper.yml)

### 逆向工程智能体评测

- [人类与机器：AI 智能体在软件逆向工程中的对比研究](https://arxiv.org/abs/2610.14960) - 比较人类与 LLM 智能体在相同静态逆向挑战中的理解和导航方式，并研究二进制表示如何占用上下文窗口。 <sub>**2026 · arXiv · 预印本** · Samuele Doria 等 · [PDF](https://arxiv.org/pdf/2610.14960)</sub>

  <sub>**范围与限制:** 理解能力仅在两个紧凑挑战上评分；另一个包含 4,000 个二进制文件的实验测量上下文容量，并非解题准确率。接口为不含动态执行的静态 IDA/MCP，模型曾接触挑战源码的可能性仍是作者承认的有效性威胁。</sub>

- [智能体网络安全的下一项挑战：真实场景且无训练数据污染的逆向工程基准](https://arxiv.org/abs/2608.11469) - 提出 SRE-Bench，使用私有编写的程序及带保护机制的二进制变体，研究智能体恢复程序语义的能力，并减少训练数据污染。 <sub>**2026 · arXiv · 预印本** · Jeremy Spence 等 · [PDF](https://arxiv.org/pdf/2608.11469)</sub>

  <sub>**范围与限制:** 修订版研究报告 19 个程序、262 个二进制实例和 1,572 个评分任务。二进制与任务实例未公开发布，只能通过评估服务访问。污染控制是作者的方法论主张，并非独立保证。</sub>

- [CrackMeBench：面向智能体的二进制逆向工程基准](https://arxiv.org/abs/2605.10597) - 用可执行程序判定结果的 CrackMe 任务评估智能体：从二进制推断验证逻辑，提交可被接受的输入或产物，并记录工具使用、耗时与评分尝试。 <sub>**2026 · arXiv · 预印本** · Isaac David 等 · [PDF](https://arxiv.org/pdf/2605.10597)</sub>

  <sub>**范围与限制:** v0 研究使用 12 个生成任务和 8 个公开校准任务，限定 Linux x86-64 ELF、Shell 接口和五分钟预算。紧凑的教学任务不能证明大型应用上的表现。未确认论文直接关联的公开研究产物 URL。</sub>

- [ProgramBench：语言模型能否从零重建程序？](https://arxiv.org/abs/2605.03546) - 通过 200 项任务评估黑盒程序重建：智能体运行可执行文件进行探测并阅读文档，再独立实现代码库，由生成的测试检查其行为。 <sub>**2026 · NeurIPS 2026 · 已接收** · John Yang 等 · [PDF](https://arxiv.org/pdf/2605.03546v1) · [代码](https://github.com/facebookresearch/ProgramBench)</sub>

  <sub>**范围与限制:** 推理阶段禁止检查二进制内容、反编译和访问互联网。通过有限测试不能证明完整行为等价或恢复了原始源码。实时榜单中的后续运行结果应与所审阅 arXiv 版本的结果区分。</sub>

- [CREBench：评估大语言模型的密码二进制逆向工程能力](https://arxiv.org/abs/2604.03750) - 通过 432 个受控挑战，评估密码二进制逆向中的算法识别、密钥或 IV 提取、包装层重建及标志恢复。 <sub>**2026 · COLM 2026 · 已接收** · Baicheng Chen 等 · [PDF](https://arxiv.org/pdf/2604.03750) · [代码](https://github.com/wangyu-ovo/CREBench)</sub>

  <sub>**范围与限制:** 语料组合 48 种算法、三类不安全密钥使用场景和三个难度等级。它不覆盖 Tigress、O-LLVM 等专业混淆器，结果不应推广到任意重度保护的二进制文件。</sub>

### 反编译与符号恢复

- [DecompileBench：面向真实场景的反编译器综合评测基准](https://aclanthology.org/2025.findings-acl.1194/) - 利用真实程序中的函数、运行时行为检查，以及 LLM 辅助的代码可理解性评估，比较传统反编译器与基于 LLM 的方法。 <sub>**2025 · Findings of ACL 2025 · 会议论文** · Zeyu Gao 等 · [PDF](https://aclanthology.org/2025.findings-acl.1194.pdf) · [代码](https://github.com/vul337/DecompileBench)</sub>

  <sub>**范围与限制:** 评估语料包含 130 个程序中的 23,400 个函数。基于模糊测试的检查覆盖有限，可理解性评分部分依赖 LLM 评审器。研究产物说明，重新构建的 OSS-Fuzz 项目可能与论文版本不同。</sub>

- [Decompile-Bench：面向真实二进制反编译的百万级二进制与源码函数对](https://papers.nips.cc/paper_files/paper/2025/hash/079cf13ae174c31f148207d94d213bdc-Abstract-Datasets_and_Benchmarks_Track.html) - 通过 Compile-Trace-Filter 流程构建 200 万组 C/C++ 二进制与源码函数对，并提供涵盖转写为 C/C++ 的 HumanEval、MBPP 任务及近期 GitHub 函数的评测集。 <sub>**2025 · NeurIPS 2025 Datasets and Benchmarks · 会议论文** · Hanzhuo Tan 等 · [PDF](https://papers.nips.cc/paper_files/paper/2025/file/079cf13ae174c31f148207d94d213bdc-Paper-Datasets_and_Benchmarks_Track.pdf) · [代码](https://github.com/albertan017/LLM4Decompile)</sub>

  <sub>**范围与限制:** 该工作研究函数级反编译。重新执行测试覆盖 HumanEval、MBPP；GitHub2025 未提供单元测试。内联可能使二进制与源码无法一一对应，微调实验仅使用 10% 的语料。这些结果不能证明整程序恢复能力。</sub>

- [LLM4Decompile：使用大语言模型反编译二进制代码](https://aclanthology.org/2024.emnlp-main.203/) - 训练语言模型将汇编反编译为 C，并改进 Ghidra 伪代码，以恢复函数能否重新编译并正确执行为评估目标。 <sub>**2024 · EMNLP 2024 · 会议论文** · Hanzhuo Tan 等 · [PDF](https://aclanthology.org/2024.emnlp-main.203.pdf) · [代码](https://github.com/albertan017/LLM4Decompile)</sub>

  <sub>**范围与限制:** 论文实验限定于 x86 平台的 C 代码和函数级基准。通过抽样测试重新执行，不代表整程序等价或恢复了原始源码。仓库后续版本应与 2024 年论文区分。</sub>

- [ReSym：利用大语言模型恢复去符号二进制中的变量与数据结构符号](https://doi.org/10.1145/3658644.3670340) - 结合两个微调语言模型与基于 Prolog 的跨函数推理，从去符号二进制的反编译结果中推断局部变量符号及用户自定义数据结构。 <sub>**2024 · ACM CCS 2024 · 会议论文** · Danning Xie 等 · [PDF](https://www.cs.purdue.edu/homes/lintan/publications/resym-ccs24.pdf) · [代码](https://github.com/lt-asset/resym)</sub>

  <sub>**范围与限制:** 该方法依赖底层反编译结果及针对 C/C++ 数据学习的预测。交叉检查可减少预测冲突，但不能证明恢复的名称或布局与缺失源码完全一致。公开研究产物包含模型、处理后的数据与评估代码。</sub>

- [利用学习得到的变量名称与类型增强反编译输出](https://www.usenix.org/conference/usenixsecurity22/presentation/chen-qibin) - 提出 Transformer 模型 DIRTY，根据反编译代码和布局信息推荐变量名与类型，并提供用于训练和评估的 DIRT 语料。 <sub>**2022 · USENIX Security 2022 · 会议论文** · Qibin Chen 等 · [PDF](https://arxiv.org/pdf/2108.06363) · [代码](https://github.com/CMUSTRUDEL/DIRTY)</sub>

  <sub>**范围与限制:** 原始流程围绕 C 程序和 Hex-Rays 输出构建。预测名称与类型是模型推断，不保证与原始符号一致。正式论文发表于 2022 年，arXiv 预印本首次提交于 2021 年。</sub>

- [DIRE：基于神经网络的反编译标识符命名方法](https://arxiv.org/abs/1909.09029) - 结合反编译输出中的词法与结构信息预测有意义的变量名，并使用编译 C 项目构建训练和评估语料。 <sub>**2019 · ASE 2019 · 会议论文** · Jeremy Lacomis 等 · [PDF](https://arxiv.org/pdf/1909.09029) · [代码](https://github.com/pcyin/dire)</sub>

  <sub>**范围与限制:** 该工作研究学习式标识符命名，并非完整源码重建或自主智能体。报告结果针对 x86-64 C 代码语料，并依赖反编译器输出。原作者仓库已标记弃用，并指向后续项目。</sub>

### 网站重建

- [Vision2Web：采用智能体验证的分层视觉网站开发基准](https://proceedings.mlr.press/v306/he26n.html) - 基于视觉原型和文字需求评测网站开发，包含 100 项静态页面、66 项交互前端与 27 项全栈任务，将基于工作流的功能检查与模型进行的视觉比较结合。 <sub>**2026 · ICML 2026 · 会议论文** · Zehai He 等 · [PDF](https://raw.githubusercontent.com/mlresearch/v306/main/assets/he26n/he26n.pdf) · [代码](https://github.com/zai-org/Vision2Web)</sub>

  <sub>**范围与限制:** 全栈层级由明确规格驱动，并非仅通过探索运行中的网站进行重建。工作流测试状态管理与增删改查结果，但有限的智能体判断不能证明后端或数据库持久性的精确等价。当前公开评测器在每个工作流内保持浏览器会话，并允许检查本地业务 API；这不构成通用的持久化证明。</sub>

- [ProgramDistill：将交互式 Web 应用转化为可验证的参考驱动软件工程任务](https://arxiv.org/abs/2609.18805) - 评测智能体从源码不可见的运行参考中恢复 Web 应用行为的能力，提供覆盖 26 个应用的 4,063 项功能恢复任务，以及独立的 12 应用重建设置，通过重放具有依赖关系的浏览器工作流评分。 <sub>**2026 · arXiv · 预印本** · Jeonghye Kim 等 · [PDF](https://arxiv.org/pdf/2609.18805v1) · [代码](https://huggingface.co/datasets/microsoft/ProgramDistill)</sub>

  <sub>**范围与限制:** 测试限于自包含应用（包括 SaaS 克隆）中由模型挖掘的有限行为。重放工作流可发现持久化失败，但通过测试不能证明全部后端或数据库不变量成立。被评测智能体接收不含截图的结构化浏览器观察，未衡量视觉保真度。公开验证器与参考解答也不构成抗污染测试集。</sub>

- [Dashboard2Code：评估多模态模型重建交互式仪表盘的能力](https://aclanthology.org/2026.acl-long.1750/) - 评估智能体主动探索运行中的仪表盘后，重建其外观与交互逻辑的能力。DashboardMimic 提供 180 个 Plotly+Dash 示例，并以代码语义分析和动态交互测试评估生成的实现。 <sub>**2026 · ACL 2026 · 会议论文** · Tianhao Niu 等 · [PDF](https://aclanthology.org/2026.acl-long.1750.pdf) · [代码](https://github.com/nth2000/Dashboard2Code)</sub>

  <sub>**范围与限制:** 限定于 Plotly+Dash 仪表盘，包含经模型扩充的示例。部分设置提供 DOM 信息，评估使用模型评审器。它并非通用后端恢复基准。链接的数据集需要接受访问条件并共享联系信息。</sub>

- [IWR-Bench：大型视觉语言模型能否根据用户交互视频重建可交互网页？](https://proceedings.iclr.cc/paper_files/paper/2026/hash/55bfedfd31489e5ae83c9ce8eec7b0e1-Abstract-Conference.html) - 测试模型利用用户交互视频和提供的静态资源重建可交互网页的能力。其 113 项任务通过重放标注的操作序列，评估已观察页面状态的视觉保真度与功能行为。 <sub>**2026 · ICLR 2026 · 会议论文** · Yang Chen 等 · [PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/55bfedfd31489e5ae83c9ce8eec7b0e1-Paper-Conference.pdf) · [代码](https://github.com/SIGMME/IWR-Bench)</sub>

  <sub>**范围与限制:** 要求输出单个 HTML 文件；论文明确要求用 JavaScript 静态数据模拟隐含的后端逻辑。轨迹覆盖和模型评审均不能证明完整网站或后端等价。</sub>

- [Interaction2Code：从交互原型生成网页代码的多模态大语言模型评测基准](https://doi.org/10.1109/ASE63991.2025.00028) - 评测模型根据交互前后的截图重建可交互网页的能力。最终研究涵盖 127 个网页、374 项交互，并比较渲染外观、自动交互检查与人工可用性判断。 <sub>**2025 · ASE 2025 · 会议论文** · Jingyu Xiao 等 · [PDF](https://arxiv.org/pdf/2411.03292v3) · [代码](https://github.com/WebPAI/Interaction2Code)</sub>

  <sub>**范围与限制:** 输入描述单项交互的状态变化，并非自主探索完整网站。测试不能证明长流程、服务端行为或原始源码等价；交互能够被检测到，也不代表它可用。</sub>

- [WebUIBench：评估多模态大语言模型从网页界面生成代码能力的综合基准](https://aclanthology.org/2025.findings-acl.815/) - 通过视觉感知、HTML 编程、图像与 HTML 对应理解，以及截图重建任务，诊断从网页界面生成代码的能力；利用来自真实网站的问答对，分别考察各项基础技能。 <sub>**2025 · Findings of ACL 2025 · 会议论文** · Zhiyu Lin 等 · [PDF](https://aclanthology.org/2025.findings-acl.815.pdf)</sub>

  <sub>**范围与限制:** 主要评估视觉与 HTML 重建技能。论文虽含初步交互研究，但并非完整流程或后端等价评测。官方仓库目前提供 README 和图片，未提供说明中提及的评估脚本。</sub>

- [Design2Code：面向自动化前端工程的多模态代码生成评测](https://aclanthology.org/2025.naacl-long.199/) - 使用真实网页参考、视觉元素和布局指标及人工评估，测试从网页截图重建前端代码的能力。 <sub>**2025 · NAACL 2025 · 会议论文** · Chenglei Si 等 · [PDF](https://aclanthology.org/2025.naacl-long.199.pdf) · [代码](https://github.com/NoviScl/Design2Code)</sub>

  <sub>**范围与限制:** 该工作属于网站视觉重建，不涉及二进制反编译，也不恢复后端行为或交互工作流。主基准含 484 个使用占位图的网页，代码与数据分别采用各自的许可条款。</sub>

### 游戏重建与逆向工程

- [GameReplica：视觉语言智能体的黑盒视觉游戏复刻基准](https://arxiv.org/abs/2609.22308) - 通过来自 25 款网页游戏、各设五个难度级别的 125 个任务，评估视觉语言智能体能否通过截图和主动交互推断隐藏规则，并构建可运行的单文件 HTML 游戏复刻。 <sub>**2026 · arXiv · 预印本** · Boyu Qiao 等 · [PDF](https://arxiv.org/pdf/2609.22308v1)</sub>

  <sub>**范围与限制:** 任务覆盖以规则为核心的网页解谜和棋盘游戏，不代表原生或商业游戏重建能力。规则、实现和视觉评分使用 LLM 评审，不能证明行为等价。官方网站提供演示，尚未核实基准代码仓库。</sub>

- [Tycho：面向 ARC-AGI-3 的程序化世界模型主动抽象](https://arxiv.org/abs/2607.28287) - Tycho 根据陌生 ARC-AGI-3 游戏中的动作与观察历史，构建可编辑的 Python 模型，描述游戏状态、状态转移、渲染与结果。它将模型预测与已记录的转移进行核对，并在规划时选择使用、修复或绕过这些模型。 <sub>**2026 · arXiv · 预印本** · Jens Lehmann 等 · [PDF](https://arxiv.org/pdf/2607.28287v1) · [代码](https://github.com/NIMI-research/Tycho)</sub>

  <sub>**范围与限制:** 评估针对 25 个公开游戏、183 个关卡，每种配置仅进行一次随机运行；其中五个游戏曾用于开发智能体框架。模型可以不预测部分像素格，或接受有限的渲染变体。转移回放和游戏分数不能证明完整引擎重建、目标识别正确、未见状态保真度、未见游戏泛化或多次运行的可靠性；智能体也可以绕过建模。</sub>

- [RevengeBench：通过行为实验逆向恢复代码形式的策略](https://arxiv.org/abs/2606.26094) - 使用五种游戏环境中的 75 个合成策略，测试智能体能否通过行为轨迹和自行设计的对手探测恢复可执行决策策略，并衡量留出状态上的动作一致性及后续对抗价值。 <sub>**2026 · arXiv · 预印本** · Babak Rahmani 等 · [PDF](https://arxiv.org/pdf/2606.26094v1) · [代码](https://github.com/bethgelab/revenge-bench)</sub>

  <sub>**范围与限制:** 目标是固定的合成策略，不是完整游戏或自适应对手。有限评测状态上的动作一致性不能唯一确定源码，部分环境的方差较大。公开包未包含部分仅用于论文的绘图与消融实验；复现还需要 CodeClash、容器运行时和模型访问。</sub>

- [SPRITE：从静态设计稿重建可用于游戏引擎的界面](https://doi.org/10.1145/3772363.3798742) - 通过层级化 YAML、视觉定位、素材提取和 Unity UXML／USS 生成，将游戏界面截图转化为可编辑的引擎资源，并在精选游戏界面基准上评估，由三位资深 UI／UX 设计师进行审阅。 <sub>**2026 · CHI EA 2026 (poster/extended abstract) · 会议论文** · Yunshu Bai 等 · [PDF](https://baiyunshu.github.io/sprite.github.io/Source/chiea26-516.pdf)</sub>

  <sub>**范围与限制:** 生成的交互覆盖基本悬停、切换和点击行为，复杂时序与拖放逻辑仍不在范围内；半透明重叠元素或边界不明确的场景内界面可能处理失败。这是游戏界面原型重建，不是完整玩法重建；官方页面仍标注代码即将发布。</sub>

### 应用重建与分析

- [DeclarUI：以自动生成声明式界面代码连接设计与开发](https://doi.org/10.1145/3715726) - 结合视觉组件提取、多模态模型、页面跳转图与迭代检查，从设计稿或截图重建多页面移动界面代码，并在 React Native、Flutter 和 ArkUI 上评测。 <sub>**2025 · Proceedings of the ACM on Software Engineering · 期刊论文** · Ting Zhou 等 · [PDF](https://xinyi-hou.github.io/files/zhou2024bridging.pdf) · [代码](https://github.com/security-pride/DeclarUI)</sub>

  <sub>**范围与限制:** 人员需审核并修正推断出的导航图。评测覆盖 50 组各含五页的界面；页面跳转覆盖率与编译成功不代表恢复了完整业务逻辑或后端。各框架结果存在差异，视觉指标也不能完全反映人眼感知的保真度。脚本与数据已公开，但核查的提交中未发现项目级许可证。</sub>

- [基于机器学习的移动应用图形用户界面原型生成](https://doi.org/10.1109/TSE.2018.2844788) - ReDraw 通过组件检测、CNN 控件类型分类及数据驱动的近邻层级组装，将截图或设计稿转换为原生 Android 图形界面原型。 <sub>**2020 · IEEE Transactions on Software Engineering · 期刊论文** · Kevin Moran 等 · [PDF](https://arxiv.org/pdf/1802.02312v2)</sub>

  <sub>**范围与限制:** 实现覆盖 15 类 Android 组件，每次生成单个屏幕；多屏需要人工组合，层级构建受采集时屏幕尺寸约束。评估关注外观和视图层级，不代表恢复原始应用逻辑或后端。实验以截图和重新制作的设计稿代替真实设计产物；本目录未独立复现实验。</sub>

- [pix2code：从图形用户界面截图生成代码](https://doi.org/10.1145/3220134.3220135) - 学习从界面截图生成领域专用语言（DSL），再编译为原生 Android XML、iOS Storyboard 或网页 HTML/CSS 界面代码。 <sub>**2018 · EICS 2018 · 会议论文** · Tony Beltramelli · [PDF](https://arxiv.org/pdf/1705.07962v2) · [代码](https://github.com/tonybeltramelli/pix2code)</sub>

  <sub>**范围与限制:** 评测采用合成的截图与代码配对，每个平台含 1,500 个训练实例和 250 个测试实例。报告的准确率针对 DSL 词元，不代表完整应用或行为复现成功率。方法忽略文本标签内容，并以相同架构分别训练各平台模型；范围是布局、组件及其关系，不包括应用逻辑或后端恢复。仓库将其定位为教育用途的研究原型；本条目未对其较旧依赖进行运行测试。</sub>

- [从 UI 设计图到 GUI 骨架：辅助启动移动界面实现的神经机器翻译器](https://doi.org/10.1145/3180155.3180240) - UI2code 使用神经编码器—解码器，将移动 UI 图像转换为 Android 组件层级与布局骨架。论文评估了结构预测，并通过小规模开发者实验研究如何基于生成的骨架实现布局。 <sub>**2018 · ICSE 2018 · 会议论文** · Chunyang Chen 等 · [PDF](https://chunyang-chen.github.io/publication/ui2code.pdf) · [代码](https://github.com/ccywch/UI2code)</sub>

  <sub>**范围与限制:** 输出仅覆盖单张图像中的组件类型与层级；详细样式和文本仍需开发者补充。结构标记准确率以及针对五张截图、由八名参与者开展的实验，不能证明完整视觉保真度，也不代表恢复了导航、应用逻辑或后端。主数据集按截图划分；独立评估使用了 20 个未见应用的 1,208 张图像，提供了有限的泛化证据。</sub>

- [使用 REMAUI 逆向重建移动应用用户界面](https://ieeexplore.ieee.org/abstract/document/7372013) - 利用 OCR、计算机视觉和布局启发式规则，从截图或设计位图重建原生 Android 界面代码，并使用来自 100 多款 Android 与 iOS 应用的 488 张截图评估视觉相似性和视图层级。 <sub>**2015 · ASE 2015 · 会议论文** · Tuan Anh Nguyen 等 · [PDF](https://c.csallner.org/papers/nguyen15reverse.pdf) · [代码](https://github.com/soumikmohianuta/pixtoapp)</sub>

  <sub>**范围与限制:** 输出为 Android 界面代码；iOS 截图属于输入，不代表生成原生 iOS 代码。方法不恢复原始逻辑和后端行为，多屏切换当时仍属后续工作。OCR／布局启发式规则可能误识别内容。所链接的 REMAUI v2 仓库采用较旧依赖，并非已核实的 2015 年原始产物。</sub>

### 固件分析与重托管

- [Fuzzware：利用精确的 MMIO 建模提升固件模糊测试效果](https://www.usenix.org/conference/usenixsecurity22/presentation/scharnowski) - 重托管单体 ARM Cortex-M 固件以开展模糊测试，利用局部符号执行为内存映射 I/O 访问建模，使输入变异集中于影响固件逻辑的值。 <sub>**2022 · USENIX Security 2022 · 会议论文** · Tobias Scharnowski 等 · [PDF](https://www.usenix.org/system/files/sec22-scharnowski.pdf) · [代码](https://github.com/fuzzware-fuzzer/fuzzware)</sub>

  <sub>**范围与限制:** 面向 Cortex-M3/M4 的产物需要配置内存映射，且不会自动为 DMA 建模。对硬件的抽象可能产生真实设备上不可能出现的崩溃。该工作构建分析环境，不代表恢复原始源码或忠实重建完整设备。</sub>

- [FirmAE：面向动态分析的物联网固件大规模仿真](https://doi.org/10.1145/3427228.3427294) - 在 Firmadyne 基础上，针对启动、网络、NVRAM、内核行为及其他运行失败加入经验性干预，使 Linux 路由器与 IP 摄像机固件的 Web 服务能够运行并接受动态分析。 <sub>**2020 · ACSAC 2020 · 会议论文** · Mingeun Kim 等 · [PDF](https://syssec.kaist.ac.kr/pub/2020/kim_acsac2020.pdf) · [代码](https://github.com/pr0v3rbs/FirmAE)</sub>

  <sub>**范围与限制:** 仲裁式干预会有意改变执行过程，目标是运行 Web 界面，而非完整复现物理设备行为。评测覆盖路由器与 IP 摄像机的 ARM 小端、MIPS 小端及大端固件；启发式规则可能不适用于未见过的设备或配置。该方法复用固件二进制，并不恢复其源码。</sub>

### 协议推断与分析

- [NetPlier：基于报文记录的概率网络协议逆向工程](https://www.ndss-symposium.org/ndss-paper/netplier-probabilistic-network-protocol-reverse-engineering-from-message-traces/) - 通过多序列比对与概率式关键字段推断，按类型对网络报文聚类，并在十种协议上评测及开展后续格式与状态机分析。 <sub>**2021 · NDSS 2021 · 会议论文** · Yapeng Ye 等 · [PDF](https://www.ndss-symposium.org/wp-content/uploads/ndss2021_4A-5_24531_paper.pdf) · [代码](https://github.com/yapengye/NetPlier)</sub>

  <sub>**范围与限制:** 需要未加密的报文记录，无法恢复从未出现的报文类型。较大的比对、亚字节关键字段及单向流量可能降低准确性。格式／有限状态机推断属于下游评测而非主要贡献；一个案例中的状态语义由人工标注。这些模型不能证明已完整重建应用／设备。</sub>

- [NEMESYS：通过分析单条报文的内在结构逆向推断网络报文语法](https://www.usenix.org/conference/woot18/presentation/kleber) - 根据单条二进制协议报文内比特一致性的变化，推断近似字段边界，并提出格式匹配分数，将推断的分段结果与已知协议解析器进行比较。 <sub>**2018 · 12th USENIX Workshop on Offensive Technologies (WOOT 18) · 会议论文** · Stephan Kleber 等 · [PDF](https://www.usenix.org/system/files/conference/woot18/woot18-paper-kleber.pdf) · [代码](https://github.com/vs-uulm/nemesys)</sub>

  <sub>**范围与限制:** 需要明文载荷。评测覆盖 DNS、DHCP 和 NTP，并针对各协议调节参数。方法无法推断单字节字段；全零字段、字符序列和伪随机值可能导致误差。FMS 验证需要已知字段边界。输出是近似报文分段，不是字段语义、状态机或完整应用／设备行为。</sub>
<!-- END GENERATED PAPERS -->

<a id="搜索目录"></a>
## 完整仓库索引

<!-- BEGIN REPOSITORY INDEX SUMMARY -->
已读取 **3,000** 个仓库的 README，当前提供 **2,864** 个浏览条目，明确超出范围的 136 个条目保留在扫描数据中。自动发现的项目与上方精选资源分别维护，未逐项执行测试。

[按分类在 GitHub 浏览](docs/repositories/README.zh-CN.md) · [网站搜索](https://awesomerea.org/?view=source-index&lang=zh) · [完整双语索引 JSON](https://awesomerea.org/source-index.json) · [精选目录 JSON](https://awesomerea.org/catalog.json)
<!-- END REPOSITORY INDEX SUMMARY -->

上面的资源清单依据一手来源整理。详细前置条件、原始来源与审阅日期保存在[目录数据](data/README.md)中。

## 参与贡献

欢迎完善条目或分享有用来源。请先阅读[贡献指南](CONTRIBUTING.md)，再[推荐资源](https://github.com/reacher-z/Awesome-REA/issues/new?template=resource.yml)、[推荐论文](https://github.com/reacher-z/Awesome-REA/issues/new?template=paper.yml)、[修正翻译](https://github.com/reacher-z/Awesome-REA/issues/new?template=translation.yml)或[报告过时条目](https://github.com/reacher-z/Awesome-REA/issues/new?template=broken-resource.yml)。

## 贡献者

[Yuxuan Zhang](https://yuxuan.world/) — **负责人（Lead）**。

[Haozhe Wang](https://haozheh3.github.io/) — 游戏重建资源集合整理与推荐：[awesome-rea-games](https://github.com/HaozheH3/awesome-rea-games)。

## 关于

本项目是独立社区资源合集。原创说明和代码使用 [MIT 许可证](LICENSE)，外部项目保留各自的许可证。

如需查找 AI 参与开发的软件，以及 Agent 训练和评测资料，可浏览 [AI Can What?](https://aicanwhat.com/zh/) 的游戏、网站和应用目录。

---

[目录格式](data/README.md) · [扫描方法](docs/source-scan.md) · [构建状态](https://github.com/reacher-z/Awesome-REA/actions/workflows/validate.yml) · [返回顶部](#awesome-reverse-engineering-anything)
