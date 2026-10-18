# Awesome Reverse Engineering Anything

独立整理的工具、案例与研究论文合集，涵盖网站、游戏、应用、原生二进制、固件和通信协议。

[English](README.md) · **简体中文**

<a href="https://awesomerea.org/zh/"><img src="assets/readme-banner.svg" alt="Awesome Reverse Engineering Anything — 覆盖六类逆向目标的工具、案例与论文" width="960"></a>

**[搜索与筛选](https://awesomerea.org/zh/)** · **[浏览案例](https://awesomerea.org/zh/cases/)** · **[研究论文](https://awesomerea.org/zh/papers/)** · **[HTML 综述](https://awesomerea.org/zh/survey/)**

**来源核查不代表运行验证。** [核查方法](https://awesomerea.org/zh/about/)

## 目录

<!-- BEGIN GENERATED CONTENTS -->
**按目标找工具与案例**

- [网站](#website) (16) · [游戏](#game) (44) · [应用](#app) (42)
- [原生二进制](#native-binary) (20) · [固件与硬件](#firmware) (12) · [协议](#protocol) (11)

**论文与工作流**

- [论文](#papers) (53) · [智能体与 MCP](#agents-and-mcp) (21) · [文档与学习资源](#references-and-learning) (22)

**更多浏览方式**

- [全部案例](https://awesomerea.org/zh/cases/) (58) · [相关合集](#related-collections) (4) · [完整仓库索引](#完整仓库索引) (2,836)
<!-- END GENERATED CONTENTS -->

## 按任务查找

| 任务 | 相关分类 |
| --- | --- |
| 检查网站或应用界面 | [网站](#website) · [应用](#app) |
| 重建游戏或检查代码匹配 | [游戏](#game) · [游戏案例](https://awesomerea.org/zh/cases/#cases-game) |
| 分析编译后代码或恢复符号 | [原生二进制](#native-binary) · [智能体与 MCP](#agents-and-mcp) |
| 研究固件或设备协议 | [固件](#firmware) · [协议](#protocol) |
| 比较方法与评测证据 | [论文](#papers) · [综述中的对比分析](https://awesomerea.org/zh/survey/#comparative-studies) |

<a id="资源目录"></a>
<a id="resource-catalog"></a>
## 资源

名称链接指向原始来源。完整说明后列出类型、关系，以及包含使用前提、限制与核查来源的“使用条件与证据”链接。

每项资源按主要用途列出一次，案例复用这些条目；[研究论文单独列出](#papers)。[浏览精选资源目录](https://awesomerea.org/zh/resources/)。

REA 标签指向单独维护的[上游 CLI 与 MCP 项目](https://github.com/morluto/rea)，收录不代表已接入 REA。[关于本独立合集](#关于)。

<!-- BEGIN GENERATED CATALOG -->
<a id="website"></a>
### Website · 网站

[↑ 返回目录](#目录)

#### 案例

- [**恐龙跑酷：恢复一条加速规则**](https://github.com/morluto/rea/blob/c360cfcd6d7901514b16dd6113eba2e0b0fdf422/website/evidence/calculator-and-dino.md#dinosaur-speed)

  REA 的教学案例检查 HTTP 版 t-rex-runner，并重建其速度更新规则。单独进行的受控原游戏检查与新演示对比更新次数，包含浮点递增越过名义速度阈值的一步。

  案例 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-dinosaur-speed-case/)

- [**rauchg.com：根据捕获的 Flight 输出重建 RSC 博客**](https://github.com/boyang-hu/website-rebuild-skill/blob/ac60c9d8a2ab40045a89b5403c3457f1404e92b3/skills/website-rebuild/references/rsc-reconstruction.md)

  记录 website-rebuild-skill 的一个案例：解码浏览器收到的 React 服务端组件 Flight 流，重建可构建的 Next 项目，再与捕获站点的输出比较。作者报告的 rauchg.com 重建过程采用路由树比较与模块引用映射；新服务端源码由可观察输出推断。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/rauchg-rsc-reconstruction-case/)

- [**BaoCut Slides：交互式网页编辑器改编**](https://github.com/JimLiu/baocut/tree/b8585e0c8d7a82bdee9f0ed019cf6edb075e41c1/packages/slides-runtime)

  记录 BaoCut 交互式幻灯片编辑器，作者称其实现借鉴自 Claude Slides。它为浏览器与桌面宿主加入本地文稿存储、HTML/CSS 编译器及标注到智能体的桥接；设计说明报告了 Web 流程检查，但未确立原有后端恢复或完整行为一致性。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/baocut-slides-editor-case/)

#### 工具、项目与集成

- [**webcrack**](https://github.com/j4k0xb/webcrack)

  识别支持的 JavaScript 混淆模式，并拆解 webpack/Browserify 打包文件，改善代码可读性。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/webcrack/)

- [**humanify JavaScript 标识符重命名工具**](https://github.com/jehna/humanify)

  借助 LLM 为压缩后的 JavaScript 标识符建议名称，并通过遵循作用域的 AST 改写完成重命名，程序结构保持不变。新名称是模型给出的推测，并非恢复出的原始标识符。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/humanify/)

- [**WABT**](https://github.com/WebAssembly/wabt)

  WebAssembly 二进制与文本转换、节区检查、验证、解释执行及 C 转换工具集。

  工具 · WebAssembly · [使用条件与证据](https://awesomerea.org/zh/resources/wabt/)

- [**wasm-tools**](https://github.com/bytecodealliance/wasm-tools)

  Bytecode Alliance 提供的 CLI 与 Rust 库，用于检查 WebAssembly 模块、元数据、组件和 WIT 接口。

  工具 · WebAssembly · [使用条件与证据](https://awesomerea.org/zh/resources/wasm-tools/)

- [**Chrome DevTools MCP**](https://github.com/ChromeDevTools/chrome-devtools-mcp)

  连接智能体与 Chrome，检查实时页面、调试网络并记录性能轨迹。

  集成 · 独立 MCP · [使用条件与证据](https://awesomerea.org/zh/resources/chrome-devtools-mcp/)

- [**mitmproxy**](https://github.com/mitmproxy/mitmproxy)

  通过交互代理、Web 界面或可脚本化命令行检查和记录 HTTP 流量。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/mitmproxy/)

- [**Playwright MCP**](https://github.com/microsoft/playwright-mcp)

  通过结构化无障碍快照驱动浏览器交互，调查可复现的网页行为。

  集成 · 独立 MCP · [使用条件与证据](https://awesomerea.org/zh/resources/playwright-mcp/)

- [**Burp Suite MCP Server 扩展**](https://github.com/PortSwigger/mcp-server)

  PortSwigger 官方 Burp Suite 扩展，提供 MCP 端点并附带 stdio 代理，使智能体可以查询代理中的 HTTP 与 WebSocket 历史记录、发送 HTTP/1.1 或 HTTP/2 请求，并打开 Repeater 或 Intruder 标签页。

  集成 · 独立 MCP · [使用条件与证据](https://awesomerea.org/zh/resources/burp-suite-mcp-server/)

- [**Wakaru**](https://github.com/pionxzh/wakaru)

  通过还原已识别的压缩与转译模式，从发布后的 JavaScript 包中恢复可读模块，支持拆包与现代语法恢复，便于分析生产环境前端代码。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/wakaru/)

- [**Spectral**](https://github.com/spectral-mcp/spectral)

  用 LLM 分析捕获的应用 HTTP 流量，生成 MCP 工具、OpenAPI 3.1 规范或 GraphQL 模式；完成抓包与认证配置后，生成的工具可直接调用已观察到的 API。

  集成 · 独立智能体 · [使用条件与证据](https://awesomerea.org/zh/resources/spectral-mcp/)

- [**jsdeob-workbench**](https://github.com/Owl4444/jsdeob-workbench)

  在查看 JavaScript AST 和变量作用域的同时，可视化编排 Babel 转换链；保存分析项目与可复用插件，逐步简化混淆脚本。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/jsdeob-workbench/)

- [**Browser Reverse Engineering Toolkit 浏览器逆向工程工具集**](https://github.com/Dvurechensky/Browser.Reverse.Engineering.Toolkit)

  采集浏览器会话证据，在持久 Chromium 会话中抓取网站，并根据已保存的捕获数据生成离线架构／API 报告，以及 OpenAPI、SDK 和模拟服务器草稿。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/browser-reverse-engineering-toolkit/)

- [**screenshot-to-code 截图转前端代码工具**](https://github.com/abi/screenshot-to-code)

  借助多模态模型，根据截图、设计稿、Figma 设计或屏幕录像生成 HTML/CSS、Tailwind、React、Vue、Bootstrap 或 Ionic 前端代码；可选的无头浏览器预览可让模型渲染并自查输出。结果是对界面外观的视觉重建，并非恢复原始源码或后端行为。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/screenshot-to-code/)

<a id="game"></a>
### Game · 游戏

[↑ 返回目录](#目录)

#### 案例

- [**DX-Ball：重建声音声像计算**](https://rea.tools/showcase/dx-ball/)

  根据指令与常量重建单个声像函数；上游报告 3,205 例与 63 字节匹配。

  案例 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-dxball-case/)

- [**TH04：恢复 DOS 子弹环辅助函数**](https://rea.tools/showcase/th04/)

  检查 PC-98 DOS 的 16 位弹幕角度辅助函数，并关联固定版本重建与历史编译器检查。

  案例 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-th04-case/)

- [**Super Mario 64 DS：带重定位核对的匹配反编译**](https://github.com/tangosdev/sm64ds-decomp)

  将 Super Mario 64 DS 函数重建为 C/C++ 和规则允许的汇编原语，并将编译结果与用户提供的卡带转储对比。独立的重定位目标核对强化匹配检查；PC 移植中的集成进度另行统计。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/sm64ds-decomp-case/)

- [**GoldenEye 007：基于反编译成果的智能体辅助原生移植**](https://github.com/jkdansereau/goldeneye-pc-port)

  在已有 GoldenEye 007 反编译成果之上构建原生 PC 移植，提供宿主平台适配层，并从用户自己的 ROM 提取资产。项目记录智能体协作、渲染对比、试玩范围和尚未解决的平台支持。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/goldeneye-pc-port-case/)

- [**ssbu-recomp：明确玩法边界的静态重编译**](https://github.com/Denkishi/ssbu-recomp)

  将 Super Smash Bros. Ultimate 13.0.4 的 AArch64 代码提前转换，并提供带 Vulkan/OpenGL 渲染的 Windows 运行时。项目还将部分角色脚本重建为可编辑 C++，通过差分与确定性测试对比转换代码和源码行为。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/ssbu-recomp-case/)

- [**KartPad：Mario Kart Wii 重编译的平台集成**](https://github.com/chrissotraidis/kartpad)

  围绕 WiiCompiled 对 Mario Kart Wii 的提前转换实现 Apple 与 Android 平台集成，提供原生图形、输入及可选 Retro Rewind 支持。状态和权利文档区分平台验收、未解决的设备缺陷及游戏内容要求。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/kartpad-case/)

- [**BattleShip：AI 辅助的 Super Smash Bros. 原生移植**](https://github.com/JRickey/BattleShip)

  使用 libultraship 和 Torch 移植已有的 Super Smash Bros. N64 反编译成果。作者早期的 README 介绍了智能体构建的图形、音频对比工具和对照模拟器行为的差分调试，并未将其说成脱离社区既有成果、仅靠卡带自动恢复游戏。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/battleship-port-case/)

- [**智能体反编译：字节匹配验收复盘**](https://momo5502.com/posts/2026-10-09-game-decompilation/)

  Maurice Heumann 介绍如何用基于编译器的函数、重定位、数据和类型检查，取代看似合理的智能体输出。复盘报告 99% 的函数已进入重建源码，全部函数中 83% 达到字节一致；重建代码仍不公开。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/agent-decompilation-oracle-case/)

- [**Snowboard Kids 2：大模型辅助的 N64 匹配反编译**](https://github.com/cdlewis/snowboardkids2-decomp)

  N64 游戏 Snowboard Kids 2 的公开匹配反编译项目，2024 年借助社区反编译工具启动。作者在按日期发布的文章中记录了 Claude、Codex 和 GLM 的使用流程，包括无界面的一次性匹配循环、按函数相似度安排任务，以及由钩子约束、经哈希校验的构建，直至报告全部函数完成匹配。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/snowboardkids2-decomp-case/)

- [**IsaacRecomp：将 Flash 游戏字节码转换为原生 C++**](https://github.com/whylurking/IsaacRecomp)

  将 The Binding of Isaac 的 Flash AVM1 字节码转换为 C++ 函数，并提供原生渲染与输入运行时。项目从用户自己的原游戏读取图像和音频，并记录了确定性输入、无界面运行和截图回归检查。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/isaacrecomp-case/)

- [**Nanolathe：附研究文档的 Total Annihilation 引擎重实现**](https://github.com/nanolathe-gg/nanolathe)

  用 Go 重实现兼容 Total Annihilation 的策略游戏引擎，公开文件格式研究并提供不同玩法配置。项目区分拟复现的零售版3.1行为、社区补丁研究和有意加入的现代改动，也区分合成检查与依赖原始游戏数据的测试。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/nanolathe-case/)

- [**TH08：精确源码重建与单独验证的移植**](https://github.com/N0zoM1z0/th08)

  依据原二进制和原编译器重建日版 Touhou 8 的 1.00d 版本，再将恢复的代码适配到其他平台。项目分别记录源码存在、严格函数匹配、完整可执行文件一致性和移植可玩性里程碑。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/th08-reconstruction-case/)

- [**Zelda 64: Recompiled：无需完整源码反编译的《姆吉拉的假面》原生移植**](https://github.com/Zelda64Recomp/Zelda64Recomp)

  通过 N64Recomp 将《姆吉拉的假面》转为原生应用，并使用 RT64 渲染。项目区分静态重编译与源码反编译，同时借用反编译项目的头文件和部分函数实现补丁与增强功能。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/zelda64recomp-case/)

- [**OpenGOAL：恢复 GOAL 代码并重建 Jak 系列游戏**](https://github.com/open-goal/jak-project)

  从 Jak 原二进制重建可读的 GOAL 代码，再用新编写的 GOAL 编译器为现代 PC 编译。流程结合专用反编译器、人工补充的类型信息、素材提取和交互式开发运行时。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/opengoal-jak-case/)

- [**LEGO Island：源码重建与单独记录的精确重构建**](https://github.com/isledecomp/isle)

  针对英文版 LEGO Island 1.1 的原始 32 位 Windows 目标重建源码。项目区分函数对比报告、ReproBit 报告的零售版逐字节一致重构建，以及普通开发构建；现代跨平台适配位于另一仓库。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/lego-island-decomp-case/)

- [**Snowball War：范围明确的 REA 辅助小游戏重建**](https://github.com/tuunanet/rea-ski-or-die-reconstruction)

  作者通过 REA 的 Ghidra 工作流调查 DOS 版 Ski or Die 二进制，记录 Snowball War 的规则，再用 Rust 与 SDL2 重建这一小游戏。公开笔记区分恢复的数据表和机制、近似实现以及有意调整的表现效果。

  案例 · 混合工具流程 · [使用条件与证据](https://awesomerea.org/zh/resources/snowball-war-rea-case/)

- [**SpaceCadetPinball：将反编译游戏逻辑适配到 SDL2**](https://github.com/k4zmu2a/SpaceCadetPinball)

  将逆向分析后的 Space Cadet 弹球游戏转为可编译的 C++，面向桌面平台。README 标明 Windows XP 可执行文件及公开 PDB、Full Tilt 可执行文件，并描述恢复结构、命名变量和适配反编译例程的工作。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/space-cadet-pinball-case/)

- [**Super Mario 64：带明确比较开关的 ROM 重建**](https://github.com/n64decomp/sm64)

  为日版、北美版、欧洲版、Shindou 版和 iQue 版 Super Mario 64 重建源码。构建文件区分原 ROM 哈希比较与非匹配或修改配置；源码命名和文档工作仍在推进。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/sm64-decomp-case/)

- [**Unleashed Recompiled：转换 Xbox 360 游戏代码与着色器**](https://github.com/hedge-dev/UnleashedRecomp)

  使用 XenonRecomp 静态重编译 Xbox 360 PowerPC 代码，并用 XenosRecomp 转换 Xenos 着色器，构建非官方 Sonic Unleashed PC 移植。项目增加现代显示与模组选项，同时记录原引擎限制和仍存在的兼容性问题。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/unleashed-recompiled-case/)

- [**OpenMW：复用原内容并替代 Morrowind 引擎**](https://github.com/OpenMW/openmw)

  提供用于运行 Morrowind 的独立引擎和替代编辑器 OpenMW-CS，通过自己的运行时加载原游戏内容，并记录脚本及模组兼容性差异。这是引擎替代实现，而非恢复出的 Bethesda 源码树。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/openmw-engine-case/)

- [**REDRIVER2：借助 PlayStation 兼容层重建 Driver 2**](https://github.com/OpenDriver2/REDRIVER2)

  将逆向分析的 Driver 2 MIPS 例程转为 C/C++，并用 Psy-X/Psy-Cross 将 PlayStation 接口适配到桌面系统。项目记录借助符号的 Ghidra/IDA 分析，同时明确包含有意修复的错误和玩法改动。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/redriver2-case/)

- [**DevilutionX：移植重建后的 Diablo 引擎**](https://github.com/diasurgical/DevilutionX)

  基于 Devilution 重建成果提供现代平台上的 Diablo 与 Hellfire 移植，加入平台支持、错误修复及可选便利功能。项目记录了早期借助符号信息的重建过程，并包含特定地牢生成与存档回归检查。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/devilutionx-case/)

- [**LASRecomp：《织梦岛》静态重编译案例**](https://github.com/peiikai/LASRecomp)

  通过静态重编译，将 2019 年 Switch 版《塞尔达传说：织梦岛》重建为原生桌面程序。作者称大部分代码、工具与逆向工作由 Claude Code 完成，人类负责指导和复核。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/lasrecomp/)

- [**ArkWeb：双游戏动作与碰撞桥接实验**](https://github.com/luki-1/ArkWeb)

  同时运行《漫威蜘蛛侠：重制版》与《蝙蝠侠：阿卡姆骑士》，将哥谭碰撞数据传入蜘蛛侠的物理世界，再将其渲染画面合成到阿卡姆中。这是实验性的运行时桥接，并非恢复出的独立游戏或新引擎。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/arkweb-two-game-case/)

- [**Perfect Dark：生成一致 ROM 的 Nintendo 64 反编译重建**](https://github.com/n64decomp/perfect_dark)

  重建 Perfect Dark 的 Nintendo 64 代码，并提供生成一致 ROM 的构建流程。项目将重建源码与使用者自备原 ROM 中的素材结合，再检查各版本产物的哈希。这是可复现构建研究案例，与独立的原生 PC 移植不同；此处的一致性结果仍为项目报告。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/perfect-dark-matching-decomp-case/)

- [**PSPRecomp：将 GTA: Vice City Stories 静态重编译为原生 Windows 构建**](https://github.com/jessicanataliagta/PSPRecomp)

  提供 PSP 静态重编译框架，分析 Allegrex／MIPS 可执行文件并生成 C++，交由原生宿主运行时执行，不使用解释器或 JIT。其 Vice City Stories 配置档收录针对美版 ULUS-10160 可执行文件生成的代码，以及 HLE、Direct3D 12 渲染、音频与输入层。已解密的可执行文件和游戏数据需来自使用者自己的副本，项目未公布游戏运行状态。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/psprecomp-vice-city-stories-case/)

#### 工具、项目与集成

- [**RenderDoc**](https://github.com/baldurk/renderdoc)

  检查自己游戏或图形应用的帧捕获、绘制调用、着色器和图形资源。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/renderdoc/)

- [**AssetRipper**](https://github.com/AssetRipper/AssetRipper)

  分析 Unity 游戏文件，检查资源依赖并将支持的资源转换为 Unity 工程格式。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/assetripper/)

- [**Cpp2IL**](https://github.com/SamboyCoding/Cpp2IL)

  结合二进制与元数据分析，从 Unity IL2CPP 构建恢复托管表示；重建能力仍在开发中。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/cpp2il/)

- [**Il2CppDumper**](https://github.com/Perfare/Il2CppDumper)

  恢复 IL2CPP 元数据及占位程序集，为原生分析工具生成辅助脚本；不会还原方法代码。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/il2cppdumper/)

- [**RenderDoc MCP**](https://github.com/scarletfantasy/renderdoc-mcp)

  向智能体开放已有 RenderDoc 捕获文件，分步检查帧、管线、资源和着色器。

  集成 · 独立 MCP · [使用条件与证据](https://awesomerea.org/zh/resources/renderdoc-mcp/)

- [**UndertaleModTool**](https://github.com/UnderminersTeam/UndertaleModTool)

  浏览和修改受支持的 GameMaker 数据文件、提取资源，以及反编译或编译 GML VM 代码；提供房间编辑、脚本化修改、CLI 和可复用的 UndertaleModLib 库。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/undertalemodtool/)

- [**frida-il2cpp-bridge**](https://github.com/vfsfitvnm/frida-il2cpp-bridge)

  在运行中的进程里检查 IL2CPP 类、方法和字段，无需提供 global-metadata.dat 即可跟踪或拦截方法调用，为静态 IL2CPP 转储工具补充运行时观察能力。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/frida-il2cpp-bridge/)

- [**objdiff**](https://github.com/encounter/objdiff)

  比较参考目标文件与重新编译目标文件中的函数和数据，辅助匹配反编译；显示指令级差异、还原 C++ 符号，并可在源码变更时自动重新构建。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/objdiff/)

- [**decomp-permuter**](https://github.com/simonlindholm/decomp-permuter)

  随机或系统地改写单个 C 函数，逐个重新编译变体并与目标文件评分对比，以寻找与原编译输出一致的写法。可用 PERM 宏指定手动备选写法，可选的 permuter<span>@</span>home 模式能把运行分发给其他工作节点。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/decomp-permuter/)

- [**asm-differ**](https://github.com/simonlindholm/asm-differ)

  对比单个函数或 ROM 地址的原始汇编与重新编译后的汇编，辅助匹配反编译；监视模式可在源码变更时重新运行 make。README 称它是 decomp.me 的默认差异查看器，并推荐 objdiff 作为现代替代方案。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/asm-differ/)

- [**UE Explorer**](https://github.com/UE-Explorer/UE-Explorer)

  通过类、属性与依赖树浏览 Unreal 包，反编译和导出 UnrealScript 类、检查字节码，并查看结构化二进制数据。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/ue-explorer/)

- [**GARbro**](https://github.com/morkt/GARbro)

  像浏览文件夹一样查看已识别的视觉小说资源归档，预览内容，并在提取图像或音频时转换为常用格式。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/garbro/)

- [**Godot 逆向工程工具**](https://github.com/GDRETools/gdsdecomp)

  从已导出的游戏中恢复受支持的 Godot 工程文件、GDScript 与导入资源，提供 PCK 检查与提取、脚本反编译及资源转换，便于分析和重建工程结构。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/godot-re-tools/)

- [**UE4SS（虚幻引擎脚本系统）**](https://github.com/UE4SS-RE/RE-UE4SS)

  通过实时 UObject 属性视图、反射 C++ 头文件导出、属性映射和 Actor 转储分析虚幻引擎游戏；Lua 与 C++ API 可辅助实验和重建游戏结构。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/ue4ss/)

- [**FModel 游戏资源浏览器**](https://github.com/4sval/FModel)

  基于 CUE4Parse 浏览虚幻引擎游戏归档，检查资源包和属性，预览并导出资源；2026 年夏季发行版新增 USD 世界导出，可辅助重建受支持的场景内容。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/fmodel/)

- [**PSP Web Recomp 浏览器游戏重编译项目**](https://github.com/snuri00/psp-web-recomp)

  将 PSP MIPS 可执行文件转换为 C++ 与 WebAssembly，配合 PSP 高层仿真运行时和 WebGL2 渲染器；原生跟踪、画面捕获及音频工具可辅助调查游戏移植中缺失的行为。

  项目 · [使用条件与证据](https://awesomerea.org/zh/resources/psp-web-recomp/)

- [**N64: Recompiled**](https://github.com/N64Recomp/N64Recomp)

  依据符号元数据将 N64 MIPS 二进制静态重编译为 C 函数，并生成函数查找与重定位宏，供运行时处理静态链接和可重定位的覆盖段。输出需配合 N64ModernRuntime 等运行时；仓库还包含 RSP 微码重编译与模组工具。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/n64recomp/)

- [**XenonRecomp**](https://github.com/hedge-dev/XenonRecomp)

  将 Xbox 360 PowerPC 可执行文件转换为可在其他平台编译的 C++ 代码，配套的 XenonAnalyse 负责检测跳转表和函数边界。输出是逐条指令的直译而非反编译代码，并需要项目本身不提供的运行时。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/xenonrecomp/)

<a id="app"></a>
### App · 应用

[↑ 返回目录](#目录)

#### 案例

- [**Aegis：追踪登录验证码计算**](https://rea.tools/showcase/aegis/)

  追踪 Aegis APK 的 TOTP 计算，官方公开目标指纹与选取的调查证据。

  案例 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-aegis-case/)

- [**Notion：追踪剪贴板桥接**](https://rea.tools/showcase/notion/)

  结合 REA 发现与独立源码阅读追踪剪贴板桥；动态包装器仍有明确限制。

  案例 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-notion-case/)

- [**PicoPrint：LX-D02 打印机调查**](https://github.com/bigtower17/picoprint)

  作者报告以 REA 开始 Android 调查，再借助独立 Hermes 工具实现 Windows BLE 打印。

  案例 · 混合工具流程 · [使用条件与证据](https://awesomerea.org/zh/resources/picoprint-rea-investigation/)

- [**ReaCut：视频编辑器重建案例**](https://github.com/Xiangyu-CAS/rea-capcut)

  独立视频编辑器，作者公开了利用 REA 研究剪映／CapCut 行为与项目格式的过程。实现包含本地时间线、FFmpeg 导出，以及实验性的有损草稿导入。

  案例 · 混合工具流程 · [使用条件与证据](https://awesomerea.org/zh/resources/reacut-reconstruction/)

- [**CF632BLE：基于体脂秤协议研究的本地客户端**](https://github.com/guyru/cf632ble)

  根据对厂商 Unique Health 安卓应用的研究，重实现 CF632BLE 体脂秤的 BLE 协议和体成分计算。静态 Web Bluetooth 客户端接收测量数据、管理设备档案，并将历史记录保存在浏览器中。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/cf632ble-case/)

- [**zee-rp：重建 Axure RP 11 的受支持文档操作**](https://github.com/LilZeeCN/zee-rp)

  通过二进制记录编解码、考虑引用关系的克隆和受约束的交互写入器，读取并修改受支持的 Axure RP 11 原生文档。CLI 与 MCP 接口提供可检查的编辑操作，并区分离线结构检查和原生应用验收。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/zee-rp-case/)

- [**Virtual Desktop Streamer：在 Linux 上重建平台适配层**](https://github.com/cudanexus/vd-streamer-linux)

  作者报告通过 Claude Code 与 REA，将 macOS 串流端的捕获、编码、音频和输入层替换为 Linux 实现，同时复用厂商协议库。文档中的目标是桌面串流和视频播放，而非仅 Windows 串流端提供的 VR 游戏串流。

  案例 · 混合工具流程 · [使用条件与证据](https://awesomerea.org/zh/resources/vd-streamer-linux-case/)

- [**Open Claude UI：基于 REA 调查的界面参考组件**](https://github.com/Caho1/open-claude-ui)

  发布 React 组件、动效辅助模块和设计系统笔记，作者将其归因于使用 REA 调查 Claude Desktop。它可作为界面重建案例；观察结果受版本约束，不能证明已完整复刻助手应用或后端。

  案例 · 混合工具流程 · [使用条件与证据](https://awesomerea.org/zh/resources/open-claude-ui-case/)

- [**PlxNative：重建原生 webOS 媒体客户端接口**](https://github.com/GLinnik21/plx-native)

  作者用 Ghidra 和编程智能体调查 LG webOS 原生媒体接口后构建的非官方 Plex 客户端。它自行绘制 Rust/OpenGL 界面并使用电视解码器，文档区分宿主测试、模拟器测试和实体设备测试。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/plx-native-case/)

- [**Windows Calculator：重建百分比规则**](https://github.com/morluto/rea/blob/c360cfcd6d7901514b16dd6113eba2e0b0fdf422/website/evidence/calculator-and-dino.md#windows-calculator)

  REA 案例追踪已安装 Windows Calculator 的模型 DLL，解释乘除运算与其他运算中不同的百分比行为。分析人员选定函数后，对照微软公开源码解释，并通过固定输入的浏览器示例演示。

  案例 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-calculator-percent-case/)

- [**飞书：作者报告的隔离第二应用实例**](https://benx.ai/blog/posts/rea-reverse-engineer-feishu-dual-instance/)

  作者报告借助 Codex 与 REA 分析，修改独立的 macOS 飞书副本，为其设置不同的应用身份、数据目录和单实例锁。文章描述本地签名与隔离检查，并称原应用保持不变。

  案例 · 混合工具流程 · [使用条件与证据](https://awesomerea.org/zh/resources/feishu-dual-instance-case/)

- [**PhotoCraft：编辑流程重建与 PSD 往返边界**](https://github.com/storytold/photocraft)

  作者将这款 Rust 图像编辑器描述为 Photoshop 风格流程的净室重实现。文档引擎、界面与自动化接口共用编辑命令；源码区分编辑器中的 PSD 往返处理与独立文件编解码器的字节保留。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/photocraft-case/)

- [**WordCraft：文档流程重建与有限范围 DOCX 兼容**](https://github.com/storytold/wordcraft)

  作者将 WordCraft 描述为以 Rust 净室重实现熟悉的 Microsoft Word 流程。项目提供自己的文档模型、排版引擎和 DOCX 读写器，以及桌面与浏览器界面；源码测试覆盖选定的编辑与文件保留行为。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/wordcraft-case/)

- [**GridCraft：电子表格流程重建与 XLSX 往返边界**](https://github.com/storytold/gridcraft)

  作者将 GridCraft 描述为以 Rust 净室重实现 Excel 风格的电子表格流程。工作簿模型、公式解析器与依赖驱动的重新计算连接到 XLSX 读写，以及供桌面、浏览器和自动化接口共用的编辑命令层。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/gridcraft-case/)

- [**DeckCraft：演示文稿流程重建与有限范围 PPTX 交换**](https://github.com/storytold/deckcraft)

  作者将 DeckCraft 描述为以 Rust 净室重实现 PowerPoint 风格的演示文稿流程。其幻灯片模型、渲染与命令层支撑桌面／浏览器编辑及 PPTX 交换；所审阅源码测试检查构造的文稿和选定的保留包部件。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/deckcraft-case/)

- [**Ledger Reborn：基于 QuickBooks 研究的独立记账实现**](https://github.com/lxistired/ledger-reborn)

  维护者报告使用 REA 与 Ghidra 研究 QuickBooks Desktop for Mac 的选定行为，随后独立实现本地记账应用。Python／SQLite 引擎持久保存复式分录、发票、库存和付款；公开合成样例检查有限范围的记账与回滚行为。

  案例 · 混合工具流程 · [使用条件与证据](https://awesomerea.org/zh/resources/ledger-reborn-accounting-case/)

- [**Pocket Tasks：重建任务状态与持久保存行为**](https://github.com/ShadowSwaps/REA-Reconstruction-Companion/tree/main/evals/reference/reconstruction)

  此教学案例明确披露作者先前接触过源码，将一次 REA 辅助的小型命令行应用调查推进为另行编写的 Node 实现。它保留所观察到的任务编辑、持久保存及选择行为，再将限定范围的输出与固定期望值及捕获的参考会话比较。

  案例 · 混合工具流程 · [使用条件与证据](https://awesomerea.org/zh/resources/pocket-tasks-reconstruction-case/)

- [**Open Scrantic：重建 Johnny Castaway 屏幕保护程序引擎**](https://github.com/glauberlima/open-scrantic)

  以 Rust 重建 Johnny Castaway 屏幕保护程序引擎，作者明确披露使用 REA 与 Claude Code。它读取原始文件，在现代桌面上运行恢复的动画脚本及按日历推进的故事状态；文档保留实现差异与有限测试范围，未确立完整行为等价。

  案例 · 混合工具流程 · [使用条件与证据](https://awesomerea.org/zh/resources/open-scrantic-screensaver-case/)

- [**LSX II 音量修正器：重建音量行为**](https://github.com/roberdorfer/kef-lsx-volume)

  根据实测 USB 音量行为，通过 macOS 音频代理将音量键映射到 KEF LSX II 的局域网控制。项目报告音量步进更均匀，同时转发 USB 音频；扬声器固件未修改。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/kef-lsx-volume-case/)

- [**Linux 上的 UU 远程：非官方协议实现**](https://github.com/VallierDev/uu-remote-linux)

  实现网易 UU 远程的非官方原生 Linux 被控端；维护者称协议行为来自对官方客户端流量及已发布程序的调查。Rust 实现将选定的桌面、输入和辅助工具通道连接到 Linux 服务，另有仍处于实验阶段的 Linux 控制端。作者将开发归因于 Claude 与 Codex，未确立 REA 使用。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/uu-remote-linux-protocol-case/)

- [**TCLimate：重建选定的 TCL Home 云端控制**](https://github.com/umarz317/TCLimate)

  在原生 macOS 菜单栏应用中实现选定的 TCL Home 空调控制与用电量报告。项目改编既有社区协议实现，并记录通过调查 Android 模块恢复另一条统计请求的过程。报告的验证检查云端状态，不等于独立核实设备实际运行或完整设备等价性。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/tclimate-cloud-controls-case/)

- [**Browserbase 插件：将 Claude in Chrome 浏览器桥接转接到云端**](https://github.com/browserbase/claude-code-plugin)

  在 Claude Code 本地浏览器桥接中替代 Claude in Chrome 扩展一端，把请求的操作交给 Browserbase 云端浏览器执行。作者的帖子串描述了逆向得到的消息格式，即每条 JSON 工具调用前加 4 字节小端长度；插件则将 17 个具名工具映射为 Stagehand／CDP 操作。这是已归档的互操作适配层，部分工具仅为占位实现，并非恢复出的 Anthropic 代码，也未经验证与扩展等价。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/browserbase-claude-chrome-bridge-case/)

#### 工具、项目与集成

- [**JADX-AI-MCP**](https://github.com/zinja-coder/jadx-ai-mcp)

  结合 JADX 插件与 Python MCP 服务，读取 Android 反编译代码、资源、交叉引用和调试上下文。

  集成 · 独立 MCP · [使用条件与证据](https://awesomerea.org/zh/resources/jadx-ai-mcp/)

- [**apktool-mcp-server Apktool MCP 服务**](https://github.com/zinja-coder/apktool-mcp-server)

  基于 Python 的 MCP 服务，调用本地安装的 Apktool，使智能体能够解码 APK，列出、读取、搜索和修改 smali 与资源文件，读取 AndroidManifest.xml 与 apktool.yml，并重新构建项目。

  集成 · 独立 MCP · [使用条件与证据](https://awesomerea.org/zh/resources/apktool-mcp-server/)

- [**frida-mcp (yfe404)**](https://github.com/yfe404/frida-mcp)

  Frida MCP 服务，提供持久插桩会话、运行时检查和 Android 静态代码与动态现场之间的导航。

  集成 · 独立 MCP · [使用条件与证据](https://awesomerea.org/zh/resources/frida-mcp-yfe404/)

- [**Super Trouper**](https://github.com/crissyfield/super-trouper)

  单个可执行文件形式的 Frida MCP 服务，用于发现设备、管理进程会话和加载插桩脚本。

  集成 · 独立 MCP · [使用条件与证据](https://awesomerea.org/zh/resources/super-trouper/)

- [**Frida**](https://github.com/frida/frida)

  动态插桩工具，用脚本观察和分析运行中的原生及托管进程行为。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/frida/)

- [**JADX**](https://github.com/skylot/jadx)

  将 Dex 反编译为 Java 的 CLI/GUI 工具，提供 Android 资源解码、代码导航和引用搜索。

  工具 · Android · [使用条件与证据](https://awesomerea.org/zh/resources/jadx/)

- [**Apktool**](https://github.com/iBotPeaches/Apktool)

  将 Android 资源与 smali 解码为项目目录，并支持重新构建修改后的安装包。

  工具 · Android · [使用条件与证据](https://awesomerea.org/zh/resources/apktool/)

- [**Androguard**](https://github.com/androguard/androguard)

  用于 APK/DEX 元数据、字节码及引用分析的 Python 工具集；v5 源码分支还提供智能体技能和 MCP 文档。

  工具 · Android · [使用条件与证据](https://awesomerea.org/zh/resources/androguard/)

- [**ILSpy**](https://github.com/icsharpcode/ILSpy)

  .NET 程序集浏览器与 C# 反编译器，支持完整项目导出、元数据检查和命令行处理。

  工具 · .NET · [使用条件与证据](https://awesomerea.org/zh/resources/ilspy/)

- [**dnSpyEx**](https://github.com/dnSpyEx/dnSpy)

  dnSpy 的社区延续项目，可在没有原始源码时调试和编辑 .NET 程序集。

  工具 · .NET · [使用条件与证据](https://awesomerea.org/zh/resources/dnspyex/)

- [**<span>@</span>electron/asar**](https://github.com/electron/asar)

  Electron 官方归档工具，可列出和提取 ASAR 内容，便于检查打包后的 JavaScript 与应用资源。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/electron-asar/)

- [**Mobile Security Framework（MobSF）**](https://github.com/MobSF/Mobile-Security-Framework-MobSF)

  通过 Web 界面与 API 检查移动应用包，结合静态分析及受支持设备上的动态测试，分析运行时行为与网络流量。

  工具 · Android · [使用条件与证据](https://awesomerea.org/zh/resources/mobsf/)

- [**objection**](https://github.com/sensepost/objection)

  通过基于 Frida 的命令界面探索运行中的 Android 与 iOS 应用，检查应用存储、内存、运行时对象和插桩后的行为。

  工具 · Android · [使用条件与证据](https://awesomerea.org/zh/resources/objection/)

- [**Grapefruit 移动应用动态插桩工具**](https://github.com/ChiChou/grapefruit)

  通过基于 Frida 的 Web 界面检查并 Hook 运行中的 iOS 与 Android 应用，提供方法与加密 API 拦截、文件系统与 SQLite 浏览、iOS 钥匙串与界面层级查看，以及常见网络库的 HTTP 流量捕获。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/grapefruit/)

- [**Blutter**](https://github.com/worawit/blutter)

  利用匹配的 Dart 运行时分析 Flutter Android ARM64 AOT 二进制，生成带符号的汇编、对象池转储及面向目标的 Frida 脚本模板，辅助研究编译后的 Dart 应用逻辑。

  工具 · Android · [使用条件与证据](https://awesomerea.org/zh/resources/blutter/)

- [**hermes-dec**](https://github.com/P1sec/hermes-dec)

  解析、反汇编并部分反编译 React Native 的 Hermes 字节码包，展示 HBC 文件头和指令，并生成伪代码以帮助理解编译后的应用逻辑。

  工具 · Android · [使用条件与证据](https://awesomerea.org/zh/resources/hermes-dec/)

- [**Recaf 字节码分析与编辑工具**](https://github.com/Col-E/Recaf)

  通过集成反编译器、字节码汇编、引用搜索、映射与去混淆工具检查和修改已编译的 JVM 应用；所审阅的 4.0 预览版还提供基础的只读 Android 字节码分析。

  工具 · JVM · [使用条件与证据](https://awesomerea.org/zh/resources/recaf/)

- [**nibkit 原生界面结构分析工具**](https://github.com/tokenbleed/nibkit)

  将已编译的 iOS/macOS 界面归档解码为对象树、Outlet／Action 连接、自定义类及导航关系，可导出 JSON 或 Mermaid 图，并通过 MCP 提供只读检查命令。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/nibkit/)

- [**AOTopsy Flutter/Dart 静态分析工具**](https://github.com/BroNils/aotopsy)

  静态检查 Flutter/Dart AOT libapp.so 文件，恢复可用元数据、类结构、调用关系及伪代码，无需嵌入 Dart VM 或编译匹配的 SDK，提供 ARM64 与 x86\_64 分析路径。

  工具 · Android · [使用条件与证据](https://awesomerea.org/zh/resources/aotopsy/)

- [**hbctool Hermes 字节码汇编与反汇编工具**](https://github.com/bongtrop/hbctool)

  通过 HASM 文件反汇编和重新汇编受支持的 React Native Hermes 字节码包，为明确支持的旧版 HBC 提供字节码检查与修改能力。

  工具 · Android · [使用条件与证据](https://awesomerea.org/zh/resources/hbctool/)

<a id="native-binary"></a>
### Native Binary · 原生二进制

[↑ 返回目录](#目录)

#### 案例

- [**DownUnderCTF：masked-squares 校验器**](https://rea.tools/showcase/ctf/)

  官方教育 CTF 案例：从检查函数得到方程，并记录原程序验证过程。

  案例 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-ctf-case/)

#### 工具、项目与集成

- [**Ghidra**](https://github.com/NationalSecurityAgency/ghidra)

  开源二进制分析套件，提供反汇编、反编译、图形分析及 Java/Python 自动化接口。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/ghidra/)

- [**radare2**](https://github.com/radareorg/radare2)

  可脚本化的命令行逆向框架，支持多架构二进制检查、反汇编、调试和修改。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/radare2/)

- [**Cutter**](https://github.com/rizinorg/cutter)

  基于 Rizin 的图形逆向工作台，提供可扩展视图及 Ghidra 反编译器集成。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/cutter/)

- [**Qiling**](https://github.com/qilingframework/qiling)

  在 CPU 仿真之上补充操作系统、文件系统和 API 行为的 Python 框架，用于可插桩的二进制分析。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/qiling/)

- [**Unicorn Engine**](https://github.com/unicorn-engine/unicorn)

  多架构 CPU 仿真引擎，可控制寄存器、内存和钩子，执行选定的指令片段。

  工具 · 程序库 · [使用条件与证据](https://awesomerea.org/zh/resources/unicorn/)

- [**angr**](https://github.com/angr/angr)

  结合控制流恢复、符号执行、数据流分析和反编译的 Python 二进制分析框架。

  工具 · 程序库 · [使用条件与证据](https://awesomerea.org/zh/resources/angr/)

- [**LIEF**](https://github.com/lief-project/LIEF)

  对 ELF、PE、Mach-O 等可执行文件格式进行结构化解析与修改的库。

  工具 · 程序库 · [使用条件与证据](https://awesomerea.org/zh/resources/lief/)

- [**Capstone**](https://github.com/capstone-engine/capstone)

  提供统一 API 和指令细节的多架构反汇编库，适合构建自定义二进制分析流程。

  工具 · 程序库 · [使用条件与证据](https://awesomerea.org/zh/resources/capstone/)

- [**ImHex**](https://github.com/WerWolv/ImHex)

  带二进制模式语言、结构化数据检查及可视化功能的十六进制编辑器，适合理解文件格式。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/imhex/)

- [**x64dbg**](https://github.com/x64dbg/x64dbg)

  Windows 二进制调试器，通过反汇编、内存视图和插件分析没有源码的程序。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/x64dbg/)

- [**GDB**](https://sourceware.org/gdb/)

  支持本地与远程调试，可控制执行并检查运行中或崩溃后的程序状态。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/gdb/)

- [**rr**](https://github.com/rr-debugger/rr)

  记录进程执行并在 GDB 下重放，便于重复检查现场和反向执行。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/rr/)

- [**Diaphora**](https://github.com/joxeankoret/diaphora)

  基于 IDA 的二进制差异分析工具，可匹配函数并迁移名称、注释与类型信息。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/diaphora/)

- [**BinDiff**](https://github.com/google/bindiff)

  比较反汇编后的二进制文件，定位不同版本中的对应函数与代码变化。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/bindiff/)

- [**Detect It Easy**](https://github.com/horsicq/Detect-It-Easy)

  结合格式解析器、签名和可编程启发式规则进行文件识别与静态检查。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/detect-it-easy/)

- [**r2frida**](https://github.com/nowsecure/r2frida)

  结合 radare2 命令与 Frida 插桩，检查桌面和移动目标中本地或远程进程的内存、符号、类及运行时调用。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/r2frida/)

- [**Kaitai Struct 二进制格式描述与解析工具**](https://github.com/kaitai-io/kaitai_struct)

  将已描述的二进制布局转换为可复用的文件与网络报文解析器；同一份 .ksy 规范可通过可视化工具检查，并编译为多种语言，便于把逆向获得的格式知识落实为可互操作的实现。

  工具 · 程序库 · [使用条件与证据](https://awesomerea.org/zh/resources/kaitai-struct/)

- [**GoReSym Go 符号恢复工具**](https://github.com/mandiant/GoReSym)

  从 Go 二进制中恢复构建元数据、函数名与地址范围、源文件和行号表、内嵌类型及字符串，也可处理已剥离符号以及部分经 UPX 等脱壳后结构异常的样本。JSON 输出可借助附带的 IDAPython 脚本导入 IDA Pro。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/goresym/)

- [**rev.ng 二进制分析框架与反编译器**](https://github.com/revng/revng)

  开源反编译流水线：借助 QEMU 将 x86-64、AArch64、i386、ARM 和 MIPS 代码提升为与架构无关的表示，以 LLVM 进行分析，并输出以合法、可重新编译为设计目标的 C 代码。数据布局分析可根据指针用法推断数据结构；可编辑的 YAML 模型及 Python、TypeScript 封装便于自动化。基于 VSCode 的界面是单独的产品，目前处于封闭测试阶段，并计划推出商业方案。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/revng/)

<a id="firmware"></a>
### Firmware and Hardware · 固件与硬件

[↑ 返回目录](#目录)

#### 案例

- [**ThinkPad IMX471：为 Linux 恢复相机调校信息**](https://github.com/cschalle/mipi-fixes-x1-aura)

  从 Intel Windows 驱动包中恢复选定的相机调校结构，用于修复一个 ThinkPad 型号在 Linux 下的图像采集。公开的 CPFF／AIQB 解析器、内核补丁及 libcamera 修改，配有作者报告的 Claude 辅助调查和有限范围的前后测量。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/thinkpad-imx471-camera-case/)

#### 工具、项目与集成

- [**Binwalk**](https://github.com/ReFirmLabs/binwalk)

  识别固件中的嵌入格式并按需提取内容，辅以熵分析帮助初步分诊。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/binwalk/)

- [**unblob**](https://github.com/onekey-sec/unblob)

  递归提取二进制数据中的归档与文件系统，同时报告数据块边界和未识别区域。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/unblob/)

- [**Ghidra 固件工具集**](https://github.com/al3xtjames/ghidra-firmware-utils)

  面向 PCI Option ROM、UEFI 固件卷、Intel Flash Descriptor 和 coreboot 镜像的 Ghidra 加载器与辅助脚本。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/ghidra-firmware-utils/)

- [**EMBA**](https://github.com/e-m-b-a/emba)

  提取固件，结合静态检查与仿真分析，整理软件组件清单，并生成 Web 报告和 SBOM，供进一步调查。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/emba/)

- [**固件分析与比较工具（FACT）**](https://github.com/fkie-cad/FACT_core)

  通过可扩展平台解包和分析固件，使用 Web 界面与 HTTP API 搜索组件内容和分析结果，并比较不同样本。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/fact-core/)

- [**OFRAK**](https://github.com/redballoonsecurity/ofrak)

  通过资源树图形界面与 Python API，递归识别、解包、分析、修改和重新打包固件及二进制格式，并可接入可选反汇编后端。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/ofrak/)

- [**FirmAE**](https://github.com/pr0v3rbs/FirmAE)

  仿真路由器与 IP 摄像机固件，检查网络服务和运行时行为，提供自动仿真检查，以及独立的分析、运行和调试模式。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/firmae/)

- [**PulseView 信号与协议分析工具**](https://github.com/sigrokproject/pulseview)

  通过 sigrok 的图形前端检查逻辑与模拟波形；协议解码器及分层解码可展示总线消息和更高层的设备操作，便于利用硬件通信记录开展固件与互操作性分析。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/pulseview/)

- [**UEFITool 固件镜像分析工具**](https://github.com/LongSoft/UEFITool)

  将 UEFI 固件镜像解析为可检查的树状结构，并检查其结构；配套的 UEFIExtract 与 UEFIFind 可提取解析后的内容、查找模式，辅助分析固件组件与厂商格式。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/uefitool/)

- [**Glasgow Interface Explorer 数字接口探索工具**](https://github.com/GlasgowEmbedded/glasgow)

  借助基于 FPGA 的开源硬件和 Python 小程序（applet），读写 SPI 闪存、I2C EEPROM 及并行存储芯片，自动确定 JTAG 引脚，调试受支持的处理器，并分析实体设备上的 UART、SPI 和 QSPI 事务。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/glasgow-interface-explorer/)

- [**Penguin 固件重托管工具**](https://github.com/rehosting/penguin)

  以提取出的根文件系统为输入，生成可编辑的仿真变换配置来重托管嵌入式 Linux 固件，再借助客户机 root shell、转发到主机的网络服务和记录下的动态分析输出，逐步完善配置。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/penguin/)

<a id="protocol"></a>
### Protocol · 协议

[↑ 返回目录](#目录)

#### 案例

- [**open-appleremote：Siri Remote 协议重建**](https://github.com/a-funk/open-appleremote)

  重建第一代 Siri Remote 在 Linux 上的蓝牙报告，解析按键、触摸与 tvOS 风格手势。Python 实现和协议文档区分实测行为、历史报告与推测含义。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/open-appleremote-case/)

- [**GAMEKB-K17：重建宏键盘配置协议**](https://github.com/dvdarkin/gamekb-k17)

  实现 GAMEKB-K17/HCY-K017 宏键盘的厂商 HID 配置协议，写入按键映射、固件宏和 RGB 设置后再读回核对。协议文档区分已测试命令、未确认观察和其他设备的研究结果。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/gamekb-k17-case/)

- [**cooler-lcd：Thermalright 显示屏协议实现**](https://github.com/kristjaningi/cooler-lcd)

  为 Thermalright Vision 散热器显示屏实现 USB 图像传输驱动，并用 Rust 仪表盘替代厂商显示应用。文档所述协议发送报头和 JPEG 帧，通过定期重发避免设备退回品牌标志画面。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/cooler-lcd-case/)

- [**NJFE：用于电脑检查的 Soulear 相机协议桥接**](https://github.com/WildweaselMS/NJFE)

  在 ESP32-C3 桥接器与 Python 电脑查看器中复用 otoscope 经逆向得到的 i4season／Soulear 协议。作者将实现归功于 Claude Code 辅助，报告把一台 Hopefox Find T 的视频传到 Windows 电脑，并提供录像、方向调整及 LED 控制。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/njfe-ear-camera-bridge-case/)

- [**hw-harness：扫描仪 USB 协议调查**](https://github.com/cschalle/hw-harness)

  记录作者报告的扫描仪调查：比较厂商驱动的 USB 控制传输与 Linux 驱动的记录，推断初始化、时序及分辨率参数。公开工具负责组织参考采集与比较，并不自动恢复完整协议规范。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/hw-harness-reference-case/)

#### 工具、项目与集成

- [**Wireshark 协议分析工具**](https://gitlab.com/wireshark/wireshark)

  将捕获的应用与设备流量解析为协议字段，支持过滤，并由 GUI 与 TShark 共用解析逻辑；自定义解析器可将新识别的报文格式固化下来，辅助比较协议实现。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/wireshark/)

- [**Netzob 协议建模与推断框架**](https://github.com/netzob/netzob)

  对通信协议建模并从流量记录推断报文布局，通过配置主动学习来推断协议状态机。Python API 提供报文字段、符号和自动机，用于解析、流量生成及模糊测试。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/netzob/)

- [**Scapy 报文分析与构造工具**](https://github.com/secdev/scapy)

  使用 Python 编写报文解析、构造、请求／响应匹配及捕获文件分析流程；自定义报文字段与层绑定可将已理解的线格式编码为可操作模型，辅助研究协议行为。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/scapy/)

- [**Universal Radio Hacker（URH）无线协议分析工具**](https://github.com/jopohl/urh)

  解调并解码通过软件无线电捕获的信号，支持自动检测调制参数和自定义解码。分析者可手动标注协议字段与消息类型，或复核基于规则的字段自动推断结果；模糊测试组件面向无状态协议，仿真环境则用于有状态交互。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/universal-radio-hacker/)

- [**SavvyCAN CAN 总线分析工具**](https://github.com/collin80/SavvyCAN)

  捕获或载入 CAN 总线流量，通过嗅探、绘图、文件比对及 ISO-TP／UDS 解码视图分析帧；借助载入或由分析者编辑的 DBC 文件，将原始字节映射为具名信号。自定义发送、模糊测试和 UDS 扫描则是独立窗口，会主动向实时总线发送帧。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/savvycan/)

- [**AALpy 自动机学习库**](https://github.com/DES-Lab/AALpy)

  通用的 Python 自动机学习库，可通过主动查询或被动轨迹数据，推断黑盒系统的确定性、非确定性、随机及下推自动机模型。其 README 链接了一项独立的低功耗蓝牙（BLE）研究，该研究的仓库报告了学习得到的设备连接与传统配对（legacy pairing）状态机；该库本身不推断报文格式。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/aalpy/)

<a id="agents-and-mcp"></a>
### Agents and MCP · 智能体与 MCP

[↑ 返回目录](#目录)

- [**REA — Reverse Engineer Anything**](https://github.com/morluto/rea)

  REA 官方 CLI 与 MCP 服务，连接分析工具并保留调查证据及限制。

  项目 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-upstream/)

- [**官方 reverse-engineer-anything 技能**](https://github.com/morluto/rea/tree/main/.agents/skills/reverse-engineer-anything)

  官方面向使用者的调查技能，包含目标路由、连接恢复与证据工作流。

  集成 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-official-skill/)

- [**dsh-mcp-rea**](https://github.com/Ersith/dsh-mcp-rea)

  社区 MCP 适配桥，以精选工具和 CLI 转发缩小宿主需要处理的工具面。

  集成 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/dsh-mcp-rea/)

- [**rea-jev**](https://github.com/juan-viox/rea-jev)

  Claude Code 社区插件，在固定版本 REA MCP 外增加 Jev 路由和证据检查。

  集成 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-jev/)

- [**rea-casebook**](https://github.com/pablodiazjorge/rea-casebook)

  Claude Code mod 汇集收到的 REA Evidence、追踪 unknown，并校验发现所引用的证据 ID。

  集成 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-casebook/)

- [**Eleven**](https://github.com/Zfinix/eleven)

  以智能体为核心的桌面逆向工程应用，可打开 Mach-O、ELF、PE 二进制、Android 安装包和 GPU 内核，让任何支持 Agent Client Protocol 的智能体在同一窗口中阅读代码、重命名函数、添加笔记并提出补丁。原生代码通过内置的 REA 构建交由 Ghidra 反编译，也可改用 Rizin 和 jadx。它是围绕现有引擎的工作台，并非新的反编译器或重建案例。

  集成 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/eleven-agent-re-workbench/)

- [**Hex-Rays IDA MCP**](https://github.com/HexRaysSA/ida-mcp)

  Hex-Rays 官方 MCP 服务，让智能体操作 IDA 数据库，支持无界面分析和可选 GUI 联动。

  集成 · 独立 MCP · [使用条件与证据](https://awesomerea.org/zh/resources/hex-rays-ida-mcp/)

- [**GhidraMCP**](https://github.com/LaurieWired/GhidraMCP)

  通过 Ghidra 扩展和 MCP 桥接提供反编译、符号导航与重命名，支持 GUI 和无界面运行。

  集成 · 独立 MCP · [使用条件与证据](https://awesomerea.org/zh/resources/ghidramcp/)

- [**Binary Ninja MCP（官方）**](https://docs.binary.ninja/guide/mcp.html)

  Binary Ninja 自带的 MCP 接口向智能体提供函数、符号、反汇编、中间语言和反编译文本。

  集成 · 独立 MCP · [使用条件与证据](https://awesomerea.org/zh/resources/binary-ninja-official-mcp/)

- [**Binary Ninja MCP（fosdickio）**](https://github.com/fosdickio/binary_ninja_mcp)

  社区维护的 Binary Ninja 插件与 MCP 桥接，支持在多个已打开的二进制目标间切换。

  集成 · 独立 MCP · [使用条件与证据](https://awesomerea.org/zh/resources/binary-ninja-community-mcp/)

- [**IDA Pro MCP（mrexodia）**](https://github.com/mrexodia/ida-pro-mcp)

  已有工作流可参考的社区 IDA 集成；维护者目前推荐迁移到 Hex-Rays 官方 MCP 服务。

  集成 · 独立 MCP · [使用条件与证据](https://awesomerea.org/zh/resources/ida-pro-mcp-community/)

- [**Radare2 MCP Server**](https://github.com/radareorg/radare2-mcp)

  基于 radare2 原生接口的 MCP 服务，提供二进制分析、会话复用和可配置的只读访问。

  集成 · 独立 MCP · [使用条件与证据](https://awesomerea.org/zh/resources/radare2-mcp/)

- [**r2ai**](https://github.com/radareorg/r2ai)

  在 radare2 内使用本地或远程模型，辅助解释函数、改善命名和反编译结果。

  集成 · 独立智能体 · [使用条件与证据](https://awesomerea.org/zh/resources/r2ai/)

- [**DAILA**](https://github.com/mahaloz/DAILA)

  跨 IDA、Ghidra、Binary Ninja 与 angr-management 的 AI 助手，用于函数摘要和命名辅助。

  集成 · 独立智能体 · [使用条件与证据](https://awesomerea.org/zh/resources/daila/)

- [**RevEng.AI Ghidra 插件**](https://github.com/RevEngAI/plugin-ghidra)

  将 Ghidra 接入 RevEng.AI，用于函数相似性匹配、名称恢复、AI 解释及辅助标注。

  集成 · 独立智能体 · [使用条件与证据](https://awesomerea.org/zh/resources/revengai-ghidra/)

- [**LLDB MCP**](https://lldb.llvm.org/use/mcp.html)

  LLDB 官方 MCP 接口提供调试会话与命令，使智能体可以设置断点、检查内存和单步执行。

  集成 · 独立 MCP · [使用条件与证据](https://awesomerea.org/zh/resources/lldb-mcp/)

- [**Claude 逆向工程技能**](https://github.com/EncidXVII/claude-reverse-engineering-skill)

  社区智能体技能，覆盖分诊、无界面导出和证据报告，并明确说明 REA 及其他 MCP 服务的工作流。

  集成 · 独立智能体 · [使用条件与证据](https://awesomerea.org/zh/resources/claude-reverse-engineering-skill/)

- [**SpecterOps 逆向工程技能**](https://github.com/SpecterOps/skills/tree/main/plugins/reverse-engineering)

  针对 Binary Ninja 与 Ghidra 的分析技能，提供 MCP 工具使用、分析步骤和标注方法。

  集成 · 独立智能体 · [使用条件与证据](https://awesomerea.org/zh/resources/specterops-re-skills/)

- [**pyghidra-mcp 项目级 Ghidra MCP 服务器**](https://github.com/clearbluejar/pyghidra-mcp)

  基于 PyGhidra 的 MCP 服务器，可分析 Ghidra 项目中的全部二进制，提供反编译、交叉引用、调用图、符号与字符串搜索、基于索引的语义代码检索，以及重命名、类型和注释编辑。另附基于 HTTP 的独立命令行客户端，以及可选的图形界面模式：由服务器自行启动 Ghidra 图形界面并加以操控。

  集成 · 独立 MCP · [使用条件与证据](https://awesomerea.org/zh/resources/pyghidra-mcp/)

- [**LeanREA 命令行逆向分析技能**](https://github.com/aicodeking/leanrea)

  独立智能体技能，使用普通命令行工具开展应用与二进制调查，提供批量初查、针对性源码／反汇编阅读，以及明确的已观察／推断／未知证据标记，并附有作者报告的 REA MCP 工作流小规模对照。

  集成 · 独立智能体 · [使用条件与证据](https://awesomerea.org/zh/resources/leanrea-skill/)

- [**Universal Modder 游戏模组智能体工具包**](https://github.com/rehan-remade/universal-modder)

  为修改用户自有的 PC 游戏打包智能体技能、三份角色说明、Python 命令行工具及预配置的 fal MCP 设置。其逆向分析指南把托管代码、原生代码和数据格式工作交给外部反编译器与调试器，并要求逆向得到的文件格式先通过往返检查再投入使用；其中一个示例附带按此方法实现的 Age of Empires II 精灵写入器。它是附带智能体实践笔记的模组工具包，不是游戏反编译重建，示例结果仍为项目报告。

  集成 · 独立智能体 · [使用条件与证据](https://awesomerea.org/zh/resources/universal-modder-agent-toolkit/)

<a id="related-collections"></a>
### Related Collections · 相关合集

[↑ 返回目录](#目录)

- [**Awesome Reverse Engineering**](https://github.com/morluto/awesome-reverse-engineering)

  REA 维护者整理的通用逆向资源目录，适合查找基础知识与相邻工具。

  合集 · [使用条件与证据](https://awesomerea.org/zh/resources/morluto-awesome-re/)

- [**Awesome REA Cases**](https://github.com/songshikang0111/awesome-REA-cases)

  中英双语的 REA 与其他 AI 辅助逆向案例合集，附来源并区分作者报告、进行中的工作和复现状态。

  合集 · [使用条件与证据](https://awesomerea.org/zh/resources/awesome-rea-cases/)

- [**awesome-rea（yibie）：关注验证的项目与实践报告**](https://github.com/yibie/awesome-rea)

  围绕明确的验收检查整理 AI 辅助游戏反编译、原生移植、静态重编译和工具，并另设实践文章与讨论分类。适合寻找一手报告，比较不同项目如何定义正确性。

  合集 · [使用条件与证据](https://awesomerea.org/zh/resources/yibie-awesome-rea/)

- [**Awesome REA/Decompiled Games：按游戏组织的重建项目目录**](https://github.com/HaozheH3/awesome-rea-games)

  按原游戏整理反编译、源码重建、重编译、原生移植和演示，通过对照表链接相关项目，并区分启动器、引擎工作、作者分享的展示与源码重建成果。

  合集 · [使用条件与证据](https://awesomerea.org/zh/resources/haozhe-awesome-rea-games/)

<a id="references-and-learning"></a>
### References and Learning · 文档与学习资源

[↑ 返回目录](#目录)

- [**安装与客户端配置**](https://github.com/morluto/rea/blob/main/docs/installation.md)

  安装、客户端配置、分析引擎依赖及按任务检查就绪状态的官方入口。

  文档 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-installation/)

- [**CLI 与 Evidence**](https://github.com/morluto/rea/blob/main/docs/cli.md)

  保存完整 Evidence，再提取摘要或模块视图，适合脚本与可复现记录。

  文档 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-cli-evidence/)

- [**MCP 接口约定与生成目录**](https://github.com/morluto/rea/blob/main/docs/mcp-contracts.md#generated-catalog)

  官方工具协议、能力发现和 Evidence 语义；适合集成与核对实际工具边界。

  文档 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-mcp-contracts/)

- [**原生二进制调查**](https://github.com/morluto/rea/blob/main/docs/native-investigation.md)

  从函数清单到指令、伪代码和引用链的原生二进制调查流程。

  文档 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-native-workflow/)

- [**跨层 JavaScript 应用工作流**](https://github.com/morluto/rea/blob/main/docs/javascript-application-workflows.md)

  从 JavaScript 应用图追踪功能、比较版本，同时保留静态分析的不确定性。

  文档 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-js-workflows/)

- [**Android APK 静态分析**](https://github.com/morluto/rea/blob/main/docs/android-analysis.md)

  经 REA 的 JADX 集成检查 APK、类、方法与引用；结果不等于运行时验证。

  文档 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-android-guide/)

- [**托管代码分析**](https://github.com/morluto/rea/blob/main/docs/managed-code-analysis.md)

  静态读取 .NET 元数据与 CIL，比较成员并检查声明的原生代码边界。

  文档 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-managed-guide/)

- [**历史网站网络记录**](https://github.com/morluto/rea/blob/main/docs/web-network-captures.md)

  离线检查已有 HAR、SAZ 等网页流量记录；不会自动抓包或访问记录中的 URL。

  文档 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-web-captures/)

- [**固件分析**](https://github.com/morluto/rea/blob/main/docs/firmware-analysis.md)

  用 Binwalk 检查固件区域、用 Unblob 显式提取，并记录工具与制品身份。

  文档 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-firmware-guide/)

- [**抓包记录检查**](https://github.com/morluto/rea/blob/main/docs/packet-captures.md)

  用 TShark 字段、显示过滤器和 decode-as 规则检查已有的网络、USB 或蓝牙抓包，并可查询已安装的字段名；不抓取流量、不打开网络接口，也不控制设备。

  文档 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-packet-captures/)

- [**抓包摘要**](https://github.com/morluto/rea/blob/main/docs/pcap-analysis.md)

  把已保存 pcap/pcapng 文件中的端点、DNS 查询与地址、TLS SNI、协议栈和 HTTP URI 汇总为可分页的 Evidence 视图；不抓取流量，也不访问记录中的目标。

  文档 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-pcap-summaries/)

- [**信号记录解码**](https://github.com/morluto/rea/blob/main/docs/signal-recordings.md)

  用调用方指定的 sigrok 协议解码器（如 UART、I2C）解码已有的逻辑信号记录，并保留带采样区间的注释文本；不采集样本，也不与硬件通信。

  文档 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-signal-recordings/)

- [**浏览器观察指南**](https://rea.tools/guides/browser/)

  通过官方 Notes 示例关联用户点击、导出请求与下载结果；REA 负责观察。

  文档 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-browser-guide/)

- [**JavaScript 与 Electron：追踪 CSV 导出**](https://rea.tools/guides/javascript/)

  官方自建 Notes 样例，从 renderer、preload、IPC 到 CSV 导出建立证据链。

  文档 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-electron-guide/)

- [**rea-playbook**](https://github.com/jinshi666888/rea-playbook)

  提供 Electron 练习目标、Evidence 提取与 MCP 探测，区分离线展示和真正调用 REA。

  学习资源 · [使用条件与证据](https://awesomerea.org/zh/resources/rea-playbook/)

- [**rea-lab**](https://github.com/pablodiazjorge/rea-lab)

  Windows REA/Ghidra 实验室，提供已知答案挑战、公开研究、上游贡献与限制说明。

  研究 · [使用条件与证据](https://awesomerea.org/zh/resources/rea-lab/)

- [**Flutter 构建识别**](https://github.com/morluto/rea/blob/main/docs/flutter-analysis.md)

  通过 REA 的纯解析命令行与 MCP 工具，识别 Flutter APK 的 Dart 快照哈希、各 ABI 库摘要与引擎构建来源，再检查单个 ABI 的 AOT 快照段。字符串池输出是对 package 与 SDK URI 的有界字节模式投影，并非反序列化的 Dart 类或恢复的源码。

  文档 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-flutter-guide/)

- [**HarmonyOS 应用包静态清点**](https://github.com/morluto/rea/blob/main/docs/harmony-analysis.md)

  通过 REA 加固的 ZIP 读取器清点 HarmonyOS 的 HAP、HSP 与 App Pack 文件，并投影出无需执行的应用图：组件路径、ID 与哈希、Stage／FA 打包模型提示、运行时类别提示，以及基于路径的原生桥接假设。所有结论仅基于路径存在；清单、Ark 字节码、资源和签名均未被解码或验证。

  文档 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-harmony-guide/)

- [**OpenSecurityTraining2**](https://ost2.fyi/)

  免费的自主学习课程，提供逆向工程、固件和系统基础等学习路线。

  学习资源 · [使用条件与证据](https://awesomerea.org/zh/resources/ost2/)

- [**pwn.college：逆向工程**](https://pwn.college/program-security/reverse-engineering/)

  包含托管练习的逆向工程课程，覆盖函数、数据访问、静态工具和动态工具。

  学习资源 · [使用条件与证据](https://awesomerea.org/zh/resources/pwn-college-re/)

- [**逆向工程入门**](https://beginners.re/)

  Dennis Yurichev 编写的免费逆向入门书，以汇编与编译后程序理解为核心，提供多语言版本。

  学习资源 · [使用条件与证据](https://awesomerea.org/zh/resources/re-for-beginners/)

- [**radare2 官方手册**](https://book.rada.re/)

  radare2 官方实践参考，覆盖分析、反汇编、脚本、调试及相关插件。

  学习资源 · [使用条件与证据](https://awesomerea.org/zh/resources/radare2-book/)
<!-- END GENERATED CATALOG -->

<!-- BEGIN GENERATED PAPERS -->
<a id="papers"></a>
## 论文

**53 篇论文**，按主题分组，组内按年份从新到旧排列。每项均标明发表状态，中文标题为译名。

[浏览论文目录](https://awesomerea.org/zh/papers/) · [完整书目 JSON](data/papers.json) · [推荐论文](https://github.com/reacher-z/Awesome-REA/issues/new?template=paper.yml)

**按主题**

- [智能体评测](#papers-agent-evaluation) (5) · [反编译](#papers-decompilation) (9) · [网站](#papers-website-reconstruction) (13)
- [游戏](#papers-game-reconstruction) (6) · [应用](#papers-app-reconstruction) (6) · [固件](#papers-firmware-analysis) (5)
- [协议](#papers-protocol-analysis) (9)

展开“范围与发表信息”查看完整研究边界。部分论文也出现在精选资源目录中，两者数量不可相加。

<a id="papers-agent-evaluation"></a>
### 逆向工程智能体评测

[↑ 论文主题](#papers) · [目录](#目录)

- [**人类与机器：AI 智能体在软件逆向工程中的对比研究**](https://arxiv.org/abs/2610.14960)

  比较人类与 LLM 智能体在相同静态逆向挑战中的理解和导航方式，并研究二进制表示如何占用上下文窗口。

  2026 · 预印本 · [PDF](https://arxiv.org/pdf/2610.14960) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-humans-machines-sre/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 理解能力仅在两个紧凑挑战上评分；另一个包含 4,000 个二进制文件的实验测量上下文容量，并非解题准确率。接口为不含动态执行的静态 IDA/MCP，模型曾接触挑战源码的可能性仍是作者承认的有效性威胁。

  **发表信息:** 2026 · arXiv · 预印本 · Samuele Doria 等

  </details>

- [**智能体网络安全的下一项挑战：真实场景且无训练数据污染的逆向工程基准**](https://arxiv.org/abs/2608.11469)

  提出 SRE-Bench，使用私有编写的程序及带保护机制的二进制变体，研究智能体恢复程序语义的能力，并减少训练数据污染。

  2026 · 预印本 · [PDF](https://arxiv.org/pdf/2608.11469) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-sre-bench/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 修订版研究报告 19 个程序、262 个二进制实例和 1,572 个评分任务。二进制与任务实例未公开发布，只能通过评估服务访问。污染控制是作者的方法论主张，并非独立保证。

  **发表信息:** 2026 · arXiv · 预印本 · Jeremy Spence 等

  </details>

- [**CrackMeBench：面向智能体的二进制逆向工程基准**](https://arxiv.org/abs/2605.10597)

  用可执行程序判定结果的 CrackMe 任务评估智能体：从二进制推断验证逻辑，提交可被接受的输入或产物，并记录工具使用、耗时与评分尝试。

  2026 · 预印本 · [PDF](https://arxiv.org/pdf/2605.10597) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-crackmebench/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** v0 研究使用 12 个生成任务和 8 个公开校准任务，限定 Linux x86-64 ELF、Shell 接口和五分钟预算。紧凑的教学任务不能证明大型应用上的表现。未确认论文直接关联的公开研究产物 URL。

  **发表信息:** 2026 · arXiv · 预印本 · Isaac David 等

  </details>

- [**ProgramBench：语言模型能否从零重建程序？**](https://arxiv.org/abs/2605.03546)

  通过 200 项任务评估黑盒程序重建：智能体运行可执行文件进行探测并阅读文档，再独立实现代码库，由生成的测试检查其行为。

  2026 · 已接收 · [PDF](https://arxiv.org/pdf/2605.03546v1) · [代码](https://github.com/facebookresearch/ProgramBench) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-programbench/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 推理阶段禁止检查二进制内容、反编译和访问互联网。通过有限测试不能证明完整行为等价或恢复了原始源码。实时榜单中的后续运行结果应与所审阅 arXiv 版本的结果区分。

  **发表信息:** 2026 · NeurIPS 2026 · 已接收 · John Yang 等

  </details>

- [**CREBench：评估大语言模型的密码二进制逆向工程能力**](https://openreview.net/forum?id=tLYdf8hWJB)

  通过 432 个受控挑战，评估密码二进制逆向中的算法识别、密钥或 IV 提取、包装层重建及标志恢复。

  2026 · 会议论文 · [PDF](https://arxiv.org/pdf/2604.03750v2) · [代码](https://github.com/wangyu-ovo/CREBench) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-crebench/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 语料组合 48 种算法、三类不安全密钥使用场景和三个难度等级。它不覆盖 Tigress、O-LLVM 等专业混淆器，结果不应推广到任意重度保护的二进制文件。

  **发表信息:** 2026 · COLM 2026 · 会议论文 · Baicheng Chen 等

  </details>

<a id="papers-decompilation"></a>
### 反编译与符号恢复

[↑ 论文主题](#papers) · [目录](#目录)

- [**SK2Decompile：从骨架到皮肤的大语言模型两阶段二进制反编译**](https://proceedings.iclr.cc/paper_files/paper/2026/hash/9132583dd869acb0cafeb0ed25eb031a-Abstract-Conference.html)

  将 LLM 反编译分为两个阶段：结构恢复模型把反编译器伪代码转换为保留控制流和数据结构、但不含标识符的中间表示，并以编译器反馈作为强化学习奖励；标识符命名模型再以语义相似度为奖励恢复名称。作者报告，其在 HumanEval 上的平均可重新执行率比 GPT-5-mini 高 21.6%，在 GitHub2025 上的平均 R2I 比 Idioms 提升 29.4%。

  2026 · 会议论文 · [PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/9132583dd869acb0cafeb0ed25eb031a-Paper-Conference.pdf) · [代码](https://github.com/albertan017/LLM4Decompile/tree/85b364bf093eb2ee4f3687cfe38a203fca89f23e/sk2decompile) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-sk2decompile/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 训练和主要评测均使用函数级 C 代码，以 GCC 和 Clang 在 -O0 至 -O3 下编译为 x86-64 Linux 二进制，并以 IDA Pro 伪代码作为模型输入。可重新执行率仅在 HumanEval 和 MBPP 上测量；ExeBench 与 GitHub2025 采用 R2I 可读性指标和 GPT-5-mini 评审。附录实验扩展到 BringUpBench 项目、macOS arm64 与 Windows MSVC 构建以及 Obfuscator-LLVM，但模型仅以 C 代码训练，论文预计遇到 C++ 模板等没有 C 对应物的语言特性时效果会下降。

  **发表信息:** 2026 · ICLR 2026 · 会议论文 · Hanzhuo Tan 等

  </details>

- [**DecompileBench：面向真实场景的反编译器综合评测基准**](https://aclanthology.org/2025.findings-acl.1194/)

  利用真实程序中的函数、运行时行为检查，以及 LLM 辅助的代码可理解性评估，比较传统反编译器与基于 LLM 的方法。

  2025 · 会议论文 · [PDF](https://aclanthology.org/2025.findings-acl.1194.pdf) · [代码](https://github.com/vul337/DecompileBench) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-decompilebench/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 评估语料包含 130 个程序中的 23,400 个函数。基于模糊测试的检查覆盖有限，可理解性评分部分依赖 LLM 评审器。研究产物说明，重新构建的 OSS-Fuzz 项目可能与论文版本不同。

  **发表信息:** 2025 · Findings of ACL 2025 · 会议论文 · Zeyu Gao 等

  </details>

- [**Decompile-Bench：面向真实二进制反编译的百万级二进制与源码函数对**](https://papers.nips.cc/paper_files/paper/2025/hash/079cf13ae174c31f148207d94d213bdc-Abstract-Datasets_and_Benchmarks_Track.html)

  通过 Compile-Trace-Filter 流程构建 200 万组 C/C++ 二进制与源码函数对，并提供涵盖转写为 C/C++ 的 HumanEval、MBPP 任务及近期 GitHub 函数的评测集。

  2025 · 会议论文 · [PDF](https://papers.nips.cc/paper_files/paper/2025/file/079cf13ae174c31f148207d94d213bdc-Paper-Datasets_and_Benchmarks_Track.pdf) · [代码](https://github.com/albertan017/LLM4Decompile) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-decompile-bench/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 该工作研究函数级反编译。重新执行测试覆盖 HumanEval、MBPP；GitHub2025 未提供单元测试。内联可能使二进制与源码无法一一对应，微调实验仅使用 10% 的语料。这些结果不能证明整程序恢复能力。

  **发表信息:** 2025 · NeurIPS 2025 Datasets and Benchmarks · 会议论文 · Hanzhuo Tan 等

  </details>

- [**ReSym：利用大语言模型恢复去符号二进制中的变量与数据结构符号**](https://doi.org/10.1145/3658644.3670340)

  结合两个微调语言模型与基于 Prolog 的跨函数推理，从去符号二进制的反编译结果中推断局部变量符号及用户自定义数据结构。

  2024 · 会议论文 · [PDF](https://www.cs.purdue.edu/homes/lintan/publications/resym-ccs24.pdf) · [代码](https://github.com/lt-asset/resym) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-resym/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 该方法依赖底层反编译结果及针对 C/C++ 数据学习的预测。交叉检查可减少预测冲突，但不能证明恢复的名称或布局与缺失源码完全一致。公开研究产物包含模型、处理后的数据与评估代码。

  **发表信息:** 2024 · ACM CCS 2024 · 会议论文 · Danning Xie 等

  </details>

- [**LLM4Decompile：使用大语言模型反编译二进制代码**](https://aclanthology.org/2024.emnlp-main.203/)

  训练语言模型将汇编反编译为 C，并改进 Ghidra 伪代码，以恢复函数能否重新编译并正确执行为评估目标。

  2024 · 会议论文 · [PDF](https://aclanthology.org/2024.emnlp-main.203.pdf) · [代码](https://github.com/albertan017/LLM4Decompile) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-llm4decompile/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 论文实验限定于 x86 平台的 C 代码和函数级基准。通过抽样测试重新执行，不代表整程序等价或恢复了原始源码。仓库后续版本应与 2024 年论文区分。

  **发表信息:** 2024 · EMNLP 2024 · 会议论文 · Hanzhuo Tan 等

  </details>

- [**SLaDe：面向优化汇编的可移植小语言模型反编译器**](https://ieeexplore.ieee.org/document/10444788)

  SLaDe 使用 200M 参数的编码器—解码器模型、面向代码的分词及 PsycheC 类型补全，将函数级汇编转换为 C。研究覆盖 x86 与 ARM 的 -O0、-O3 设置，并结合生成候选与输入／输出检查。输入是汇编文本而非原始机器字节，反汇编不属于该方法。

  2024 · 会议论文 · [PDF](https://arxiv.org/pdf/2305.12520v3) · [代码](https://zenodo.org/records/10205121) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-slade/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 评测覆盖约 4,000 个 ExeBench 函数及含 112 个程序的合成基准。束宽为 5，并选择首个通过有限输入／输出测试的候选；生成函数被放回原始调用上下文。通过这些测试不代表完整程序或全部输入上的等价性。编辑相似度只是可读性的代理指标。较长函数、外部调用及错误的类型／运算符预测仍会导致失败；模型的输入和输出窗口均为 1,024 个位置。历史基线比较的覆盖范围不同，不能据此确立当前排名。

  **发表信息:** 2024 · IEEE/ACM CGO 2024 · 会议论文 · Jordi Armengol-Estapé 等

  </details>

- [**DeGPT：使用大语言模型优化反编译器输出**](https://www.ndss-symposium.org/ndss-paper/degpt-optimizing-decompiler-output-with-llm/)

  通过三个协同角色选择、提出并检查修改，改进已有的类 C 反编译输出。其流程简化代码结构、添加注释并重命名变量，在接受结构修改前，使用微代码片段语义计算比较模拟的符号值与调用。作者以四个代码库中的 620 个函数评估可读性与命名效果，并分别测试保留与剥离符号的版本。

  2024 · 会议论文 · [PDF](https://www.ndss-symposium.org/wp-content/uploads/2024-401-paper.pdf) · [代码](https://github.com/PeiweiHu/DeGPT) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-degpt/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 报告的 24.4% 降幅来自保留符号版本输出的 Halstead 工作量代理指标，并非直接测得的人力节省。62.9% 的注释结果是人工判定正确的注释中，具有非平凡信息者的平均占比。MSSC 是过程内启发式检查：调用被抽象处理，循环转化为分支；解析、别名与路径增长仍有限制。其 80 个案例的人工审查报告准确率为 84%、召回率为 85%，其中漏过三处有害修改。这支持辅助理解伪代码，不能保证二进制等价、整程序可重新编译或恢复原始源码。

  **发表信息:** 2024 · NDSS 2024 · 会议论文 · Peiwei Hu 等

  </details>

- [**利用学习得到的变量名称与类型增强反编译输出**](https://www.usenix.org/conference/usenixsecurity22/presentation/chen-qibin)

  提出 Transformer 模型 DIRTY，根据反编译代码和布局信息推荐变量名与类型，并提供用于训练和评估的 DIRT 语料。

  2022 · 会议论文 · [PDF](https://arxiv.org/pdf/2108.06363) · [代码](https://github.com/CMUSTRUDEL/DIRTY) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-dirty/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 原始流程围绕 C 程序和 Hex-Rays 输出构建。预测名称与类型是模型推断，不保证与原始符号一致。正式论文发表于 2022 年，arXiv 预印本首次提交于 2021 年。

  **发表信息:** 2022 · USENIX Security 2022 · 会议论文 · Qibin Chen 等

  </details>

- [**DIRE：基于神经网络的反编译标识符命名方法**](https://doi.org/10.1109/ASE.2019.00064)

  结合反编译输出中的词法与结构信息预测有意义的变量名，并使用编译 C 项目构建训练和评估语料。

  2019 · 会议论文 · [PDF](https://arxiv.org/pdf/1909.09029) · [代码](https://github.com/pcyin/dire) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-dire/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 该工作研究学习式标识符命名，并非完整源码重建或自主智能体。报告结果针对 x86-64 C 代码语料，并依赖反编译器输出。原作者仓库已标记弃用，并指向后续项目。

  **发表信息:** 2019 · ASE 2019 · 会议论文 · Jeremy Lacomis 等

  </details>

<a id="papers-website-reconstruction"></a>
### 网站重建

[↑ 论文主题](#papers) · [目录](#目录)

- [**Vision2Web：采用智能体验证的分层视觉网站开发基准**](https://proceedings.mlr.press/v306/he26n.html)

  基于视觉原型和文字需求评测网站开发，包含 100 项静态页面、66 项交互前端与 27 项全栈任务，将基于工作流的功能检查与模型进行的视觉比较结合。

  2026 · 会议论文 · [PDF](https://raw.githubusercontent.com/mlresearch/v306/main/assets/he26n/he26n.pdf) · [代码](https://github.com/zai-org/Vision2Web) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-vision2web/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 全栈层级由明确规格驱动，并非仅通过探索运行中的网站进行重建。工作流测试状态管理与增删改查结果，但有限的智能体判断不能证明后端或数据库持久性的精确等价。当前公开评测器在每个工作流内保持浏览器会话，并允许检查本地业务 API；这不构成通用的持久化证明。

  **发表信息:** 2026 · ICML 2026 · 会议论文 · Zehai He 等

  </details>

- [**ProgramDistill：将交互式 Web 应用转化为可验证的参考驱动软件工程任务**](https://arxiv.org/abs/2609.18805)

  评测智能体从源码不可见的运行参考中恢复 Web 应用行为的能力，提供覆盖 26 个应用的 4,063 项功能恢复任务，以及独立的 12 应用重建设置，通过重放具有依赖关系的浏览器工作流评分。

  2026 · 预印本 · [PDF](https://arxiv.org/pdf/2609.18805v1) · [代码](https://huggingface.co/datasets/microsoft/ProgramDistill) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-programdistill/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 测试限于自包含应用（包括 SaaS 克隆）中由模型挖掘的有限行为。重放工作流可发现持久化失败，但通过测试不能证明全部后端或数据库不变量成立。被评测智能体接收不含截图的结构化浏览器观察，未衡量视觉保真度。公开验证器与参考解答也不构成抗污染测试集。

  **发表信息:** 2026 · arXiv · 预印本 · Jeonghye Kim 等

  </details>

- [**UI2App：评测可执行 Web 应用生成中的视觉交互推断**](https://arxiv.org/abs/2607.06306)

  UI2App 使用来自 95 个 Web 应用的 600 张截图，评测生成的可运行 React/TypeScript 应用。它通过参考交互分类体系和公开评测流水线，分别衡量构建可执行性、视觉保真度，以及包括跨路由状态在内的截图隐含交互行为。

  2026 · 预印本 · [PDF](https://arxiv.org/pdf/2607.06306v2) · [代码](https://github.com/chenmancm169/UI2App) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-ui2app/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 静态截图无法唯一确定行为；评分规则接受多种有效实现，并不证明与原应用或后端等价。Auto IIS 在不执行工具的情况下评判生成源码和截图，人工运行验证覆盖 45 个应用的子集。跨路由状态不一定能在重新加载或会话结束后持久保存。主结果每个应用与模型组合生成一次，重复运行仅覆盖子集。

  **发表信息:** 2026 · arXiv · 预印本 · Grace Man Chen 等

  </details>

- [**Dashboard2Code：评估多模态模型重建交互式仪表盘的能力**](https://aclanthology.org/2026.acl-long.1750/)

  评估智能体主动探索运行中的仪表盘后，重建其外观与交互逻辑的能力。DashboardMimic 提供 180 个 Plotly+Dash 示例，并以代码语义分析和动态交互测试评估生成的实现。

  2026 · 会议论文 · [PDF](https://aclanthology.org/2026.acl-long.1750.pdf) · [代码](https://github.com/nth2000/Dashboard2Code) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-dashboard2code/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 限定于 Plotly+Dash 仪表盘，包含经模型扩充的示例。部分设置提供 DOM 信息，评估使用模型评审器。它并非通用后端恢复基准。链接的数据集需要接受访问条件并共享联系信息。

  **发表信息:** 2026 · ACL 2026 · 会议论文 · Tianhao Niu 等

  </details>

- [**CASCADE：谷歌基于大语言模型的 JavaScript 反混淆器**](https://doi.org/10.1145/3786583.3786873)

  利用 Gemini 定位 Obfuscator.IO 为字符串混淆插入的前置（prelude）函数，再在 JSIR 编译器中间表示上执行常量传播与内联，以确定性方式还原字符串字面量和 API 名称。

  2026 · 会议论文 · [PDF](https://arxiv.org/pdf/2507.17691v2) · [代码](https://github.com/google/jsir) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-cascade/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 该方法针对 Obfuscator.IO 的字符串混淆；控制流平坦化、其他混淆器及基于智能体的设计留待后续工作。评测以 Obfuscator.IO 的四种预设配置混淆 ETH 150k JavaScript 数据集中的 3,000 个程序，衡量前置函数识别、还原的字面量数量和运行时间，而非功能等价性。生产部署及扫描规模均为作者自述，生产环境的预筛选依赖一条未公开的 YARA 规则。

  **发表信息:** 2026 · ICSE-SEIP 2026 · 会议论文 · Shan Jiang 等

  </details>

- [**ScreenCoder：以模块化多模态智能体推进面向前端自动化的视觉到代码生成**](https://arxiv.org/abs/2507.22827)

  将截图到代码的生成分配给定位、规划和生成三个智能体，分别标注界面区域、构建层级布局树并编写 HTML/CSS。该流程还生成了用于监督微调和强化学习的 Screen-10K 训练数据；论文另提出包含 1,000 个网页的 ScreenBench。

  2026 · 已接收 · [PDF](https://arxiv.org/pdf/2507.22827v2) · [代码](https://github.com/leigest519/ScreenCoder) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-screencoder/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 输出为静态 HTML/CSS 布局，不重建交互、JavaScript 行为或后端逻辑。结果是 ScreenBench 与 Design2Code 上的视觉相似度分数（CLIP 及经 OCR 匹配的文本块），不能证明代码层面或功能上的等价。公开流程需调用托管模型 API，默认使用豆包（Doubao）。审阅文本为 arXiv v2，EMNLP 接收版本可能有所不同。

  **发表信息:** 2026 · EMNLP 2026 · 已接收 · Yilei Jiang 等

  </details>

- [**IWR-Bench：大型视觉语言模型能否根据用户交互视频重建可交互网页？**](https://proceedings.iclr.cc/paper_files/paper/2026/hash/55bfedfd31489e5ae83c9ce8eec7b0e1-Abstract-Conference.html)

  测试模型利用用户交互视频和提供的静态资源重建可交互网页的能力。其 113 项任务通过重放标注的操作序列，评估已观察页面状态的视觉保真度与功能行为。

  2026 · 会议论文 · [PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/55bfedfd31489e5ae83c9ce8eec7b0e1-Paper-Conference.pdf) · [代码](https://github.com/SIGMME/IWR-Bench) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-iwr-bench/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 要求输出单个 HTML 文件；论文明确要求用 JavaScript 静态数据模拟隐含的后端逻辑。轨迹覆盖和模型评审均不能证明完整网站或后端等价。

  **发表信息:** 2026 · ICLR 2026 · 会议论文 · Yang Chen 等

  </details>

- [**JsDeObsBench：衡量与评测大语言模型的 JavaScript 反混淆能力**](https://doi.org/10.1145/3719027.3744871)

  对附带测试用例的 Project CodeNet 程序施加 JavaScript-Obfuscator 的七种混淆变换，构建可通过执行验证的 JavaScript 反混淆基准，并从语法、执行结果、代码简化程度及与原始代码的相似度评估 LLM 和现有工具的输出。

  2025 · 会议论文 · [PDF](https://arxiv.org/pdf/2506.20170v1) · [代码](https://github.com/Ch3nYe/JsDeObsBench) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-jsdeobsbench/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 平均而言，LLM 输出通过执行检查的比例为 60.93%，两种现有反混淆工具基线为 83%。所有样本均由单一混淆器生成，原始程序是长度适中的编程竞赛解答。4,515 个经混淆的恶意代码样本没有测试用例，只能通过行为轨迹比较。

  **发表信息:** 2025 · ACM CCS 2025 · 会议论文 · Guoqiang Chen 等

  </details>

- [**Interaction2Code：从交互原型生成网页代码的多模态大语言模型评测基准**](https://doi.org/10.1109/ASE63991.2025.00028)

  评测模型根据交互前后的截图重建可交互网页的能力。最终研究涵盖 127 个网页、374 项交互，并比较渲染外观、自动交互检查与人工可用性判断。

  2025 · 会议论文 · [PDF](https://arxiv.org/pdf/2411.03292v3) · [代码](https://github.com/WebPAI/Interaction2Code) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-interaction2code/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 输入描述单项交互的状态变化，并非自主探索完整网站。测试不能证明长流程、服务端行为或原始源码等价；交互能够被检测到，也不代表它可用。

  **发表信息:** 2025 · ASE 2025 · 会议论文 · Jingyu Xiao 等

  </details>

- [**WebUIBench：评估多模态大语言模型从网页界面生成代码能力的综合基准**](https://aclanthology.org/2025.findings-acl.815/)

  通过视觉感知、HTML 编程、图像与 HTML 对应理解，以及截图重建任务，诊断从网页界面生成代码的能力；利用来自真实网站的问答对，分别考察各项基础技能。

  2025 · 会议论文 · [PDF](https://aclanthology.org/2025.findings-acl.815.pdf) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-webuibench/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 主要评估视觉与 HTML 重建技能。论文虽含初步交互研究，但并非完整流程或后端等价评测。官方仓库目前提供 README 和图片，未提供说明中提及的评估脚本。

  **发表信息:** 2025 · Findings of ACL 2025 · 会议论文 · Zhiyu Lin 等

  </details>

- [**分而治之：从截图生成界面代码**](https://doi.org/10.1145/3729364)

  沿视觉分隔线递归切分网页截图，由多模态模型为每个叶子片段生成 HTML/CSS，再将子片段代码逐级向上组装为完整页面；评估涵盖 GPT-4o、Gemini 与 Claude 系列模型以及一项小规模开发者研究。

  2025 · 期刊论文 · [PDF](https://arxiv.org/pdf/2406.16386v3) · [代码](https://github.com/WebPAI/DCGen) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-dcgen/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 该方法以 HTML/CSS 重建静态视觉布局，不重建交互、JavaScript 行为或后端逻辑。测试页面是将图片替换为占位图的自包含快照；主要评测从 348 个热门网站中抽取 111 个，另加 80 个更复杂的 GitHub Pages 页面，可用性研究仅有四名参与者。分割依赖人工设定的阈值，组装阶段仍可能错排元素。

  **发表信息:** 2025 · Proceedings of the ACM on Software Engineering · 期刊论文 · Yuxuan Wan 等

  </details>

- [**Design2Code：面向自动化前端工程的多模态代码生成评测**](https://aclanthology.org/2025.naacl-long.199/)

  使用真实网页参考、视觉元素和布局指标及人工评估，测试从网页截图重建前端代码的能力。

  2025 · 会议论文 · [PDF](https://aclanthology.org/2025.naacl-long.199.pdf) · [代码](https://github.com/NoviScl/Design2Code) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-design2code/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 该工作属于网站视觉重建，不涉及二进制反编译，也不恢复后端行为或交互工作流。主基准含 484 个使用占位图的网页，代码与数据分别采用各自的许可条款。

  **发表信息:** 2025 · NAACL 2025 · 会议论文 · Chenglei Si 等

  </details>

- [**Web2Code：面向多模态大语言模型的大规模网页转代码数据集与评估框架**](https://proceedings.nips.cc/paper_files/paper/2024/hash/cb66be286795d71f89367d596bf78ea7-Abstract-Datasets_and_Benchmarks_Track.html)

  通过指令微调和两个评测基准研究从截图重建 HTML。Web2Code 结合生成网页、经改进的 WebSight 与 pix2code 图像／代码对，以及来自 WebSRC 的问答。模型根据网页图像与指令生成 HTML，渲染输出接受视觉比较，另一个基准则测量截图理解能力。

  2024 · 会议论文 · [PDF](https://proceedings.neurips.cc/paper_files/paper/2024/file/cb66be286795d71f89367d596bf78ea7-Paper-Datasets_and_Benchmarks_Track.pdf) · [代码](https://github.com/MBZUAI-LLM/web2code) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-web2code/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 评估使用 1,198 张截图和 5,990 个是／否问题。WCGB 用 GPT-4V 评价渲染图像；其“用户界面与交互性”类别衡量元素外观，并不执行点击路径、持久状态或后端行为。合成与改进样本不能确立对任意真实 Web 应用的覆盖、与原始源码等价或代码质量。论文报告，在 1,000 项隐私抽样中，2.7% 存在联系信息问题，因此不能笼统宣称数据完全不含此类信息。

  **发表信息:** 2024 · NeurIPS 2024 Datasets and Benchmarks · 会议论文 · Sukmin Yun 等

  </details>

<a id="papers-game-reconstruction"></a>
### 游戏重建与逆向工程

[↑ 论文主题](#papers) · [目录](#目录)

- [**GameReplica：视觉语言智能体的黑盒视觉游戏复刻基准**](https://arxiv.org/abs/2609.22308)

  通过来自 25 款网页游戏、各设五个难度级别的 125 个任务，评估视觉语言智能体能否通过截图和主动交互推断隐藏规则，并构建可运行的单文件 HTML 游戏复刻。

  2026 · 预印本 · [PDF](https://arxiv.org/pdf/2609.22308v1) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-gamereplica/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 任务覆盖以规则为核心的网页解谜和棋盘游戏，不代表原生或商业游戏重建能力。规则、实现和视觉评分使用 LLM 评审，不能证明行为等价。官方网站提供演示，尚未核实基准代码仓库。

  **发表信息:** 2026 · arXiv · 预印本 · Boyu Qiao 等

  </details>

- [**Tycho：面向 ARC-AGI-3 的程序化世界模型主动抽象**](https://arxiv.org/abs/2607.28287)

  Tycho 根据陌生 ARC-AGI-3 游戏中的动作与观察历史，构建可编辑的 Python 模型，描述游戏状态、状态转移、渲染与结果。它将模型预测与已记录的转移进行核对，并在规划时选择使用、修复或绕过这些模型。

  2026 · 预印本 · [PDF](https://arxiv.org/pdf/2607.28287v1) · [代码](https://github.com/NIMI-research/Tycho) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-tycho/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 评估针对 25 个公开游戏、183 个关卡，每种配置仅进行一次随机运行；其中五个游戏曾用于开发智能体框架。模型可以不预测部分像素格，或接受有限的渲染变体。转移回放和游戏分数不能证明完整引擎重建、目标识别正确、未见状态保真度、未见游戏泛化或多次运行的可靠性；智能体也可以绕过建模。

  **发表信息:** 2026 · arXiv · 预印本 · Jens Lehmann 等

  </details>

- [**RevengeBench：通过行为实验逆向恢复代码形式的策略**](https://arxiv.org/abs/2606.26094)

  使用五种游戏环境中的 75 个合成策略，测试智能体能否通过行为轨迹和自行设计的对手探测恢复可执行决策策略，并衡量留出状态上的动作一致性及后续对抗价值。

  2026 · 预印本 · [PDF](https://arxiv.org/pdf/2606.26094v1) · [代码](https://github.com/bethgelab/revenge-bench) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-revengebench/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 目标是固定的合成策略，不是完整游戏或自适应对手。有限评测状态上的动作一致性不能唯一确定源码，部分环境的方差较大。公开包未包含部分仅用于论文的绘图与消融实验；复现还需要 CodeClash、容器运行时和模型访问。

  **发表信息:** 2026 · arXiv · 预印本 · Babak Rahmani 等

  </details>

- [**SPRITE：从静态设计稿重建可用于游戏引擎的界面**](https://doi.org/10.1145/3772363.3798742)

  通过层级化 YAML、视觉定位、素材提取和 Unity UXML／USS 生成，将游戏界面截图转化为可编辑的引擎资源，并在精选游戏界面基准上评估，由三位资深 UI／UX 设计师进行审阅。

  2026 · 会议论文 · [PDF](https://baiyunshu.github.io/sprite.github.io/Source/chiea26-516.pdf) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-sprite-game-ui/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 生成的交互覆盖基本悬停、切换和点击行为，复杂时序与拖放逻辑仍不在范围内；半透明重叠元素或边界不明确的场景内界面可能处理失败。这是游戏界面原型重建，不是完整玩法重建；官方页面仍标注代码即将发布。

  **发表信息:** 2026 · CHI EA 2026 (poster/extended abstract) · 会议论文 · Yunshu Bai 等

  </details>

- [**WorldCoder：通过编写代码并与环境交互构建世界模型的基于模型的语言智能体**](https://papers.nips.cc/paper_files/paper/2024/hash/820c61a0cd419163ccbd2c33b268816e-Abstract-Conference.html)

  WorldCoder 根据环境交互和自然语言目标学习可执行的 Python 状态转移与奖励模型，利用已记录经验和乐观规划约束修正代码，并在 Sokoban、MiniGrid 与 ALFWorld 中研究迁移和任务求解。

  2024 · 会议论文 · [PDF](https://papers.neurips.cc/paper_files/paper/2024/file/820c61a0cd419163ccbd2c33b268816e-Paper-Conference.pdf) · [代码](https://github.com/haotang1995/WorldCoder) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-worldcoder/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 假设环境动态具有确定性，状态为符号化的离散表示，并非从任意像素或二进制恢复游戏。与已观察转移一致及规划成功，不能证明完整引擎等价或所有未见状态上的正确性。评估针对有限范围的环境模型与规划，不涉及恢复原始源码或资产。

  **发表信息:** 2024 · NeurIPS 2024 · 会议论文 · Hao Tang 等

  </details>

- [**通过蒙特卡洛树搜索引导大语言模型生成代码世界模型**](https://proceedings.neurips.cc/paper_files/paper/2024/hash/6f479ea488e0908ac8b1b37b27fd134c-Abstract-Conference.html)

  GIF-MCTS 根据环境的自然语言描述与离线状态转移轨迹生成可执行的 Python 状态转移和奖励模型，并利用预测反馈生成、改进和修复代码。CWMB 评估 18 个强化学习环境及后续规划；另一个实验使用简化的 Read to Fight Monsters 网格世界。

  2024 · 会议论文 · [PDF](https://proceedings.neurips.cc/paper_files/paper/2024/file/6f479ea488e0908ac8b1b37b27fd134c-Paper-Conference.pdf) · [代码](https://github.com/nicoladainese96/code-world-models) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-code-world-models/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 假设环境动态具有确定性、状态完全可观测，并且描述足够详细；并非仅凭像素或二进制进行恢复。准确率使用合成过程中提供的回放转移，并结合规划回报评估，不能证明所有未见状态上的正确性或完整引擎等价。RTFM 在不同回合间固定手册内容，并让怪物保持静止。CWMB 也包含非游戏的控制与物理任务；部分规划回报未给出，复杂连续状态模型仍然困难。

  **发表信息:** 2024 · NeurIPS 2024 · 会议论文 · Nicola Dainese 等

  </details>

<a id="papers-app-reconstruction"></a>
### 应用重建与分析

[↑ 论文主题](#papers) · [目录](#目录)

- [**UIOrchestra：通过多智能体系统将 UI 设计转换为高保真代码**](https://aclanthology.org/2025.findings-emnlp.150/)

  UIOrchestra 通过布局描述、代码生成及渲染图像比较三个智能体，将静态移动 UI 设计转换为 React/CSS。其 APPUI 基准包含 1,101 组经人工修订的代码与渲染图像，依据 12 类中的 165 款应用截图构建。参考代码为评测而重建，并非恢复出的原始应用源码。

  2025 · 会议论文 · [PDF](https://aclanthology.org/2025.findings-emnlp.150.pdf) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-uiorchestra/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 评测视觉、组件及代码相似度，不验证原生安装包执行、交互、后端行为或应用等价性。APPUI 参考图像来自对 iOS 截图所做重建的渲染结果；无法获取的图片／图标使用占位素材。人工研究由四位标注者评估 200 个样本。差异分析提示词忽略字号／字体差异及占位图像内容。未核实模型快照、渲染依赖或可复现的运行环境，亦未重新运行实验。

  **发表信息:** 2025 · Findings of EMNLP 2025 · 会议论文 · Chuhuai Yue 等

  </details>

- [**DeclarUI：以自动生成声明式界面代码连接设计与开发**](https://doi.org/10.1145/3715726)

  结合视觉组件提取、多模态模型、页面跳转图与迭代检查，从设计稿或截图重建多页面移动界面代码，并在 React Native、Flutter 和 ArkUI 上评测。

  2025 · 期刊论文 · [PDF](https://xinyi-hou.github.io/files/zhou2024bridging.pdf) · [代码](https://github.com/security-pride/DeclarUI) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-declarui/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 人员需审核并修正推断出的导航图。评测覆盖 50 组各含五页的界面；页面跳转覆盖率与编译成功不代表恢复了完整业务逻辑或后端。各框架结果存在差异，视觉指标也不能完全反映人眼感知的保真度。脚本与数据已公开，但核查的提交中未发现项目级许可证。

  **发表信息:** 2025 · Proceedings of the ACM on Software Engineering · 期刊论文 · Ting Zhou 等

  </details>

- [**基于机器学习的移动应用图形用户界面原型生成**](https://doi.org/10.1109/TSE.2018.2844788)

  ReDraw 通过组件检测、CNN 控件类型分类及数据驱动的近邻层级组装，将截图或设计稿转换为原生 Android 图形界面原型。

  2020 · 期刊论文 · [PDF](https://arxiv.org/pdf/1802.02312v2) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-redraw/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 实现覆盖 15 类 Android 组件，每次生成单个屏幕；多屏需要人工组合，层级构建受采集时屏幕尺寸约束。评估关注外观和视图层级，不代表恢复原始应用逻辑或后端。实验以截图和重新制作的设计稿代替真实设计产物；本目录未独立复现实验。

  **发表信息:** 2020 · IEEE Transactions on Software Engineering · 期刊论文 · Kevin Moran 等

  </details>

- [**pix2code：从图形用户界面截图生成代码**](https://doi.org/10.1145/3220134.3220135)

  学习从界面截图生成领域专用语言（DSL），再编译为原生 Android XML、iOS Storyboard 或网页 HTML/CSS 界面代码。

  2018 · 会议论文 · [PDF](https://arxiv.org/pdf/1705.07962v2) · [代码](https://github.com/tonybeltramelli/pix2code) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-pix2code/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 评测采用合成的截图与代码配对，每个平台含 1,500 个训练实例和 250 个测试实例。报告的准确率针对 DSL 词元，不代表完整应用或行为复现成功率。方法忽略文本标签内容，并以相同架构分别训练各平台模型；范围是布局、组件及其关系，不包括应用逻辑或后端恢复。仓库将其定位为教育用途的研究原型；本条目未对其较旧依赖进行运行测试。

  **发表信息:** 2018 · EICS 2018 · 会议论文 · Tony Beltramelli

  </details>

- [**从 UI 设计图到 GUI 骨架：辅助启动移动界面实现的神经机器翻译器**](https://doi.org/10.1145/3180155.3180240)

  UI2code 使用神经编码器—解码器，将移动 UI 图像转换为 Android 组件层级与布局骨架。论文评估了结构预测，并通过小规模开发者实验研究如何基于生成的骨架实现布局。

  2018 · 会议论文 · [PDF](https://chunyang-chen.github.io/publication/ui2code.pdf) · [代码](https://github.com/ccywch/UI2code) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-ui2code/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 输出仅覆盖单张图像中的组件类型与层级；详细样式和文本仍需开发者补充。结构标记准确率以及针对五张截图、由八名参与者开展的实验，不能证明完整视觉保真度，也不代表恢复了导航、应用逻辑或后端。主数据集按截图划分；独立评估使用了 20 个未见应用的 1,208 张图像，提供了有限的泛化证据。

  **发表信息:** 2018 · ICSE 2018 · 会议论文 · Chunyang Chen 等

  </details>

- [**使用 REMAUI 逆向重建移动应用用户界面**](https://ieeexplore.ieee.org/abstract/document/7372013)

  利用 OCR、计算机视觉和布局启发式规则，从截图或设计位图重建原生 Android 界面代码，并使用来自 100 多款 Android 与 iOS 应用的 488 张截图评估视觉相似性和视图层级。

  2015 · 会议论文 · [PDF](https://c.csallner.org/papers/nguyen15reverse.pdf) · [代码](https://github.com/soumikmohianuta/pixtoapp) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-remaui/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 输出为 Android 界面代码；iOS 截图属于输入，不代表生成原生 iOS 代码。方法不恢复原始逻辑和后端行为，多屏切换当时仍属后续工作。OCR／布局启发式规则可能误识别内容。所链接的 REMAUI v2 仓库采用较旧依赖，并非已核实的 2015 年原始产物。

  **发表信息:** 2015 · ASE 2015 · 会议论文 · Tuan Anh Nguyen 等

  </details>

<a id="papers-firmware-analysis"></a>
### 固件分析与重托管

[↑ 论文主题](#papers) · [目录](#目录)

- [**面向 Linux 固件二进制的用户空间依赖感知重托管**](https://www.ndss-symposium.org/ndss-paper/user-space-dependency-aware-rehosting-for-linux-based-firmware-binaries/)

  FIRMWELL 通过运行初始化进程、定位阻塞依赖并修补缺失的系统层行为，重建 Linux 固件服务的执行环境。它结合容器化 QEMU-user 仿真与 QEMU-system 回退，并利用进程轨迹和二进制分析恢复目标服务所需的资源。

  2026 · 会议论文 · [PDF](https://www.ndss-symposium.org/wp-content/uploads/2026-s249-paper.pdf) · [代码](https://github.com/qc9c/Firmwell) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-firmwell/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 评估针对选定网络服务，并非完整设备或硬件等价。HTTP 验收采用配置好的响应状态与错误内容检查；其他服务需要各自的判定标准。覆盖范围受解包、架构支持、初始化启发式规则和外设模型限制，符号执行路径爆炸、求解超时及复杂外设检查仍可能导致失败。论文中的修复策略避免补丁修改目标二进制；服务交互成功不能证明恢复了原始源码或全部设备功能。

  **发表信息:** 2026 · NDSS 2026 · 会议论文 · Chuan Qin 等

  </details>

- [**使用 Penguin 进行以目标为中心的固件重托管**](https://www.ndss-symposium.org/ndss-paper/auto-draft-634/)

  Penguin 以提取出的固件文件系统为输入，通过静态分析生成可编辑的仿真变换配置（如文件修改、伪文件、NVRAM 值和网络接口），用于重托管嵌入式 Linux 固件。动态分析插件揭示运行失败，便于针对具体目标完善配置；配置最小化工具则找出可用的重托管所必需的变换。

  2025 · 会议论文 · [PDF](https://www.ndss-symposium.org/wp-content/uploads/bar2025-final10.pdf) · [代码](https://github.com/rehosting/penguin) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-penguin/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 面向嵌入式 Linux 固件，沿用 Firmadyne 和 FirmAE 的思路，采用替换内核的整机仿真；实现支持 x86、ARM 和 MIPS，并依赖 Linux 系统调用 ABI。与 FirmAE 对比时，判定成功的标准是有进程绑定 80 或 443 端口，更严格的检查是 HTTP 返回非空响应；作者指出两者都不代表系统功能完整。比 FirmAE 多出 75% 的结果由作者在其自建语料（13,649 个取自厂商网站的镜像）上报告。完善配置仍需分析人员参与；运行结果不完全确定，作者对配置最多重复运行十次。该工作构建的是分析环境，不代表忠实复现设备或恢复源代码。

  **发表信息:** 2025 · Workshop on Binary Analysis Research (BAR) 2025 · 会议论文 · Andrew Fasano 等

  </details>

- [**Fuzzware：利用精确的 MMIO 建模提升固件模糊测试效果**](https://www.usenix.org/conference/usenixsecurity22/presentation/scharnowski)

  重托管单体 ARM Cortex-M 固件以开展模糊测试，利用局部符号执行为内存映射 I/O 访问建模，使输入变异集中于影响固件逻辑的值。

  2022 · 会议论文 · [PDF](https://www.usenix.org/system/files/sec22-scharnowski.pdf) · [代码](https://github.com/fuzzware-fuzzer/fuzzware) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-fuzzware/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 面向 Cortex-M3/M4 的产物需要配置内存映射，且不会自动为 DMA 建模。对硬件的抽象可能产生真实设备上不可能出现的崩溃。该工作构建分析环境，不代表恢复原始源码或忠实重建完整设备。

  **发表信息:** 2022 · USENIX Security 2022 · 会议论文 · Tobias Scharnowski 等

  </details>

- [**FirmAE：面向动态分析的物联网固件大规模仿真**](https://doi.org/10.1145/3427228.3427294)

  在 Firmadyne 基础上，针对启动、网络、NVRAM、内核行为及其他运行失败加入经验性干预，使 Linux 路由器与 IP 摄像机固件的 Web 服务能够运行并接受动态分析。

  2020 · 会议论文 · [PDF](https://syssec.kaist.ac.kr/pub/2020/kim_acsac2020.pdf) · [代码](https://github.com/pr0v3rbs/FirmAE) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-firmae/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 仲裁式干预会有意改变执行过程，目标是运行 Web 界面，而非完整复现物理设备行为。评测覆盖路由器与 IP 摄像机的 ARM 小端、MIPS 小端及大端固件；启发式规则可能不适用于未见过的设备或配置。该方法复用固件二进制，并不恢复其源码。

  **发表信息:** 2020 · ACSAC 2020 · 会议论文 · Mingeun Kim 等

  </details>

- [**HALucinator：通过抽象层仿真实现固件重托管**](https://www.usenix.org/conference/usenixsecurity20/presentation/clements)

  HALucinator 识别单体 ARM Cortex-M 固件中的硬件抽象库函数，并用人工编写的 Python 处理函数和外设模型替换它们，从而重托管固件。LibMatch 定位库接口；QEMU/Avatar2 实现支持交互式输入输出，与论文关联的 HAL-fuzz 变体则使用 AFL-Unicorn 进行模糊测试。

  2020 · 会议论文 · [PDF](https://www.usenix.org/system/files/sec20-clements.pdf) · [代码](https://github.com/embedded-sec/halucinator) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-halucinator/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** LibMatch 需要可获取的硬件抽象层或库，以及足够相似的编译环境；编译器差异与内联会限制匹配效果。重托管还需要 QEMU 支持的架构、固件内存布局、拦截地址及人工编写的处理函数和模型。未建模的直接硬件访问可能在读取时返回零、在写入时被忽略；简化的时序与外设行为不能证明硬件等价。作者的重托管与模糊测试演示不代表普遍覆盖所有固件、完整重建设备或恢复原始源代码。

  **发表信息:** 2020 · USENIX Security 2020 · 会议论文 · Abraham A Clements 等

  </details>

<a id="papers-protocol-analysis"></a>
### 协议推断与分析

[↑ 论文主题](#papers) · [目录](#目录)

- [**ICEPRE：基于数据驱动混合符号执行的工控协议逆向工程**](https://dl.acm.org/doi/10.1145/3728982)

  在二进制协议解析器中沿具体报文引导的路径分析，再进行符号化重放，提取字节级数据流以推断报文字段边界。它依据保持原值的运算和相似处理轨迹合并字节。作者在四种公开工控协议、每组 1,000 条报文的数据集上，报告平均边界 F1 分数为 0.76、字段完美分割率为 0.67。

  2025 · 期刊论文 · [PDF](https://dl.acm.org/doi/pdf/10.1145/3728982) · [代码](https://github.com/QYbPtqyb/ICEPRE) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-icepre/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 恢复的是报文语法，并非字段语义、协议状态机或端点等价性。方法需要二进制、加载配置，以及正确识别的初始化、输入和解析函数；尤其在缺少符号时，仍需人工筛选。不支持加密协议和位级字段；被忽略或仅被复制的字节可能遭到错误合并。完美分割率衡量两端边界均正确的字段。量化实验使用四种公开协议的 50 条与 1,000 条报文集合；另行开展的专有协议研究覆盖五个固件目标中的三种协议，在三台设备上进行交互检查，并由人工建立真实标签。这些检查不能证明完整设备行为。

  **发表信息:** 2025 · Proceedings of the ACM on Software Engineering (ISSTA 2025) · 期刊论文 · Yibo Qu 等

  </details>

- [**BinPRE：增强基于二进制分析的协议逆向工程中的字段推断**](https://dl.acm.org/doi/10.1145/3658644.3690299)

  根据受插桩监测的服务端二进制及输入报文，推断协议报文的字段边界与语义。BinPRE 按处理字节的指令操作符进行分组，使用检测器识别字段类型和功能，再借助相似报文细化结果。作者在八种协议、每种 50 条报文上报告平均字段完美分割率为 0.73，类型／功能推断的 F1 分数为 0.74／0.81。

  2024 · 会议论文 · [PDF](https://tingsu.github.io/files/ccs24-BinPRE.pdf) · [代码](https://github.com/ecnusse/BinPRE) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-binpre/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 研究对象是字段推断，不是恢复协议状态机或端点的完整行为。方法需要能够访问并插桩的实现及运行时的报文处理；仅有被动捕获数据并不足够。完美分割率统计被精确分割的字段占全部真实字段的比例，而非完整恢复的协议比例。检测器库覆盖五种语义类型与六种功能。字节级污点分析无法准确解析位标志，也不确立未执行行为。真实标签依据 Wireshark 解析器与协议规范构建；三种二进制分析基线由作者重新实现。报告的模糊测试改进属于下游评估，不是实现等价性的证明。

  **发表信息:** 2024 · ACM CCS 2024 · 会议论文 · Jiayi Jiang 等

  </details>

- [**从网络协议实现提取精确格式规范及其安全应用**](https://dl.acm.org/doi/10.1145/3576915.3616614)

  NetLifter 将可获取源码的 C 协议解析器静态转换为 BNF 风格的报文文法及报文字段之间的一阶逻辑约束。它分析经过标注的 LLVM 位码，结合抽象格式图、局部路径敏感分析、展开与重排序。所得字段边界、约束与名称可用于报文生成及解析器构建。

  2023 · 会议论文 · [PDF](https://qingkaishi.github.io/public_pdfs/CCS23.pdf) · [代码](https://github.com/qingkaishi/netlifter) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-netlifter/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 需要源码／LLVM 中间表示及报文缓冲区、长度标注，并非对闭源二进制或仅凭流量进行恢复。论文面向常见的自顶向下 C 解析器，不支持 C++、内联汇编及缺少源码的库。指针和循环分析仍有近似；可识别校验和字段，但部分校验和约束会被省略，实现中忽略的字段也可能遗漏。精确率／召回率在选定的十种协议上进行人工核对。报告的模糊测试采用每次三小时、重复二十次的实验，并绕过校验和检查。方法推断的是格式，而非协议状态机或实现等价性的证明。

  **发表信息:** 2023 · ACM CCS 2023 · 会议论文 · Qingkai Shi 等

  </details>

- [**BinaryInferno：面向二进制报文格式字段推断的语义驱动方法**](https://www.ndss-symposium.org/ndss-paper/binaryinferno-a-semantic-driven-approach-to-field-inference-for-binary-message-formats/)

  无需对可执行程序插桩，即可从静态报文样本推断部分二进制报文格式。专用检测器识别浮点数、时间戳、长度、熵边界和序列化模式，再通过基于图的集成步骤协调各自的描述。作者对十种协议的样本开展评估，在每组 1,000 条报文且不使用分析者先验的设置下，报告顶层字段边界的精确率为 0.69、召回率为 0.73、假阳性率为 0.04。

  2023 · 会议论文 · [PDF](https://www.ndss-symposium.org/wp-content/uploads/2023/02/ndss2023_s131_paper.pdf) · [代码](https://github.com/binaryinferno/binaryinferno) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-binaryinferno/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 假设数据无错误、未经压缩或加密、按字节对齐，并推断起始偏移一致的共有字段或载荷区域。可选字段、联合类型字段及不支持的序列化模式仍未解决；样本多样性会影响结果。26 组封装载荷测试集依据已知真实报文类型预先分组，并非自动发现。真实标签合并了在整个样本中均保持常量的相邻字段；文中注明的平均值排除了没有推断结果的样本。BI+ 额外使用给定的字节序和捕获时间范围。这些是字段边界结果，不代表完整语义恢复、协议状态推断或行为等价。

  **发表信息:** 2023 · NDSS 2023 · 会议论文 · Jared Chandler 等

  </details>

- [**越仔细观察，学到的越多：用于协议状态机学习的灰盒方法**](https://doi.org/10.1145/3548606.3559365)

  StateInspector 将主动消息查询与运行时内存快照结合起来，学习协议的 Mealy 状态机，无需目标实现的源代码。它识别可能决定状态的堆内存位置，并通过污点分析与混合执行合并状态；作者在 TLS 1.2 和 WPA/2 实现上进行了评估。

  2022 · 会议论文 · [PDF](https://tomchothia.gitlab.io/Papers/greyboxstatelearning_ccs2022.pdf) · [代码](https://github.com/ChrisMcMStone/state-inspector) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-stateinspector/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 假设协议可抽象为有限 Mealy 状态机、已知输入字母表能到达相关状态，且决定状态的内存位于堆上并可由初始化查询触及。状态合并依赖所配置的搜索深度与符号执行前瞻上限。缺失的输入或存储在其他位置的状态可能导致行为未被建模；测试驱动程序构造的错误消息、响应抽象方式和超时也可能产生误导性转移。学习出的模型与有界检查不能证明实现完全等价，也不恢复未知消息格式或重建应用源代码。

  **发表信息:** 2022 · ACM CCS 2022 · 会议论文 · Chris McMahon Stone 等

  </details>

- [**基于自动机学习的蓝牙设备指纹识别与分析**](https://doi.org/10.1007/s10703-023-00425-y)

  通过主动自动机学习，为实体外设上的低功耗蓝牙（BLE）协议实现推断 Mealy 状态机模型。运行 SweynTooth 衍生固件的 nRF52840 中心设备发送抽象 BLE 输入，并以错误处理、重复查询和缓存应对丢包与不确定的响应。作者学习了六款设备的连接过程模型和其中三款的传统配对（legacy pairing）模型，并利用模型差异识别各设备的 SoC。

  2022 · 期刊论文 · [PDF](https://arxiv.org/pdf/2211.16074v2) · [代码](https://github.com/apferscher/ble-learning) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-ble-automata-learning/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 模型受所选抽象输入字母表限制，仅覆盖连接过程和传统配对；不推断报文格式，安全配对留待后续研究。等价性仅以每个状态少量的一致性测试近似检验，因此模型只是假设而非证明。其中一款 SoC 只能缩减输入字母表后学习，两款设备从已建立连接的状态开始学习，部分配对实验还需人工硬重置设备。所得指纹识别序列仅适用于受测 SoC。除一条会导致设备崩溃的输入序列外，作者未在学习所得模型中发现安全漏洞。

  **发表信息:** 2022 · Formal Methods in System Design · 期刊论文 · Andrea Pferscher 等

  </details>

- [**NetPlier：基于报文记录的概率网络协议逆向工程**](https://www.ndss-symposium.org/ndss-paper/netplier-probabilistic-network-protocol-reverse-engineering-from-message-traces/)

  通过多序列比对与概率式关键字段推断，按类型对网络报文聚类，并在十种协议上评测及开展后续格式与状态机分析。

  2021 · 会议论文 · [PDF](https://www.ndss-symposium.org/wp-content/uploads/ndss2021_4A-5_24531_paper.pdf) · [代码](https://github.com/yapengye/NetPlier) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-netplier/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 需要未加密的报文记录，无法恢复从未出现的报文类型。较大的比对、亚字节关键字段及单向流量可能降低准确性。格式／有限状态机推断属于下游评测而非主要贡献；一个案例中的状态语义由人工标注。这些模型不能证明已完整重建应用／设备。

  **发表信息:** 2021 · NDSS 2021 · 会议论文 · Yapeng Ye 等

  </details>

- [**无线协议自动逆向工程**](https://www.usenix.org/conference/woot19/presentation/pohl)

  从解调后的物理层捕获数据推断专有无线协议的报文格式：先依据前导码和同步字对齐报文，再结合 RSSI 与专用引擎标注长度、地址、序列号和校验和字段，并可利用已知地址或字段位置等先验信息。

  2019 · 会议论文 · [PDF](https://www.usenix.org/system/files/woot19-paper_pohl.pdf) · [代码](https://github.com/jopohl/urh) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-wireless-protocol-re/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 仅推断报文格式，即前导码、同步字、长度、地址、序列号和校验和；协议状态机推断以及开关位等载荷字段不在研究范围内。方法假设报文为紧凑的二进制格式，且每条报文只有一个前导码和同步字。准确率在 8 个生成协议上评测；3 份真实智能家居捕获（EnOcean、Homematic BidCoS 及 RWE Smarthome 使用的 eQ-3 协议）用于性能测试，作者也承认这是有限的测试集。

  **发表信息:** 2019 · 13th USENIX Workshop on Offensive Technologies (WOOT 19) · 会议论文 · Johannes Pohl 等

  </details>

- [**NEMESYS：通过分析单条报文的内在结构逆向推断网络报文语法**](https://www.usenix.org/conference/woot18/presentation/kleber)

  根据单条二进制协议报文内比特一致性的变化，推断近似字段边界，并提出格式匹配分数，将推断的分段结果与已知协议解析器进行比较。

  2018 · 会议论文 · [PDF](https://www.usenix.org/system/files/conference/woot18/woot18-paper-kleber.pdf) · [代码](https://github.com/vs-uulm/nemesys) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-nemesys/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 需要明文载荷。评测覆盖 DNS、DHCP 和 NTP，并针对各协议调节参数。方法无法推断单字节字段；全零字段、字符序列和伪随机值可能导致误差。FMS 验证需要已知字段边界。输出是近似报文分段，不是字段语义、状态机或完整应用／设备行为。

  **发表信息:** 2018 · 12th USENIX Workshop on Offensive Technologies (WOOT 18) · 会议论文 · Stephan Kleber 等

  </details>
<!-- END GENERATED PAPERS -->

<a id="搜索目录"></a>
## 完整仓库索引

<!-- BEGIN REPOSITORY INDEX SUMMARY -->
已读取 **3,000** 个仓库的 README，当前提供 **2,836** 个浏览条目，明确超出范围的 161 个条目及 3 个上游仓库已无法访问的条目保留在扫描数据中。自动发现的项目与上方精选资源分别维护，未逐项运行验证。

[按分类在 GitHub 浏览](docs/repositories/README.zh-CN.md) · [网站搜索](https://awesomerea.org/zh/?view=source-index) · [完整双语索引 JSON](https://awesomerea.org/source-index.json) · [精选目录 JSON](https://awesomerea.org/catalog.json)
<!-- END REPOSITORY INDEX SUMMARY -->

上面的资源清单依据一手来源整理。详细前置条件、原始来源与审阅日期保存在[目录数据](data/README.md)中。

## 参与贡献

欢迎完善条目或分享有用来源。请先阅读[贡献指南](CONTRIBUTING.md)，再[推荐资源](https://github.com/reacher-z/Awesome-REA/issues/new?template=resource.yml)、[推荐论文](https://github.com/reacher-z/Awesome-REA/issues/new?template=paper.yml)、[修正翻译](https://github.com/reacher-z/Awesome-REA/issues/new?template=translation.yml)或[报告过时条目](https://github.com/reacher-z/Awesome-REA/issues/new?template=broken-resource.yml)。

## 贡献者

[Yuxuan Zhang](https://yuxuan.world/) — **负责人（Lead）**。

[Haozhe Wang](https://haozheh3.github.io/) — 游戏重建资源集合整理与推荐：[awesome-rea-games](https://github.com/HaozheH3/awesome-rea-games)。

## 关于

[REA（Reverse Engineer Anything）](https://github.com/morluto/rea) 是单独维护的上游 CLI 与 MCP 项目。本合集名称与之呼应，但并非 REA 官方仓库；条目标签及“REA 官方文档”等关系标注中的 REA 均指该项目。

本项目是独立社区资源合集。原创说明和代码使用 [MIT 许可证](LICENSE)，外部项目保留各自的许可证。

引用本合集时，请使用其[引用元数据](CITATION.cff)。所列论文、工具及其他作品请按各自的一手来源引用；引用扫描统计数据时，请注明对应的提交或快照日期。

如需查找 AI 参与开发的软件，以及 Agent 训练和评测资料，可浏览 [AI Can What?](https://aicanwhat.com/zh/) 的游戏、网站和应用目录。

---

[目录格式](data/README.md) · [扫描方法](docs/source-scan.md) · [构建状态](https://github.com/reacher-z/Awesome-REA/actions/workflows/validate.yml) · [返回顶部](#awesome-reverse-engineering-anything)
