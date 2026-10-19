<p align="center">
  <a href="https://awesomerea.org/zh/"><img src="assets/featured-by-awesome-rea-compact.svg" alt="Featured by Awesome REA" width="200" height="48"></a>
</p>

# Awesome Reverse Engineering Anything

独立整理的工具、案例与研究论文合集，涵盖网站、游戏、应用、原生二进制、固件和通信协议。

[English](README.md) · **简体中文**

<a href="https://awesomerea.org/zh/"><img src="assets/readme-banner.svg" alt="Awesome Reverse Engineering Anything — 覆盖六类逆向目标的工具、案例与论文" width="960"></a>

<!-- BEGIN GENERATED BADGES -->
[![精选资源: 348](https://img.shields.io/badge/%E7%B2%BE%E9%80%89%E8%B5%84%E6%BA%90-348-53309C?style=flat-square&labelColor=303447)](https://awesomerea.org/zh/resources/) [![案例: 180](https://img.shields.io/badge/%E6%A1%88%E4%BE%8B-180-53309C?style=flat-square&labelColor=303447)](https://awesomerea.org/zh/cases/) [![论文: 83](https://img.shields.io/badge/%E8%AE%BA%E6%96%87-83-53309C?style=flat-square&labelColor=303447)](https://awesomerea.org/zh/papers/) [![目录检查](https://github.com/reacher-z/Awesome-REA/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/reacher-z/Awesome-REA/actions/workflows/validate.yml) [![许可: MIT](https://img.shields.io/badge/%E8%AE%B8%E5%8F%AF-MIT-606779?style=flat-square&labelColor=303447)](LICENSE) [![网站: awesomerea.org](https://img.shields.io/badge/%E7%BD%91%E7%AB%99-awesomerea.org-6235B5?style=flat-square&labelColor=303447)](https://awesomerea.org/zh/)
<!-- END GENERATED BADGES -->

**[搜索与筛选](https://awesomerea.org/zh/)** · **[浏览案例](https://awesomerea.org/zh/cases/)** · **[研究论文](https://awesomerea.org/zh/papers/)** · **[HTML 综述](https://awesomerea.org/zh/survey/)**

**来源核查不代表运行验证。** [核查方法](https://awesomerea.org/zh/about/)

## 目录

<!-- BEGIN GENERATED CONTENTS -->
**按目标找工具与案例**

- [网站](#website) (19) · [游戏](#game) (162) · [应用](#app) (49)
- [原生二进制](#native-binary) (24) · [固件与硬件](#firmware) (15) · [协议](#protocol) (13)

**论文与工作流**

- [论文](#papers) (83) · [智能体与 MCP](#agents-and-mcp) (30) · [文档与学习资源](#references-and-learning) (27)

**更多浏览方式**

- [全部案例](https://awesomerea.org/zh/cases/) (180) · [相关合集](#related-collections) (6) · [完整仓库索引](#完整仓库索引) (2,836)
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

- [**Claude Code 中的 REA：隔离配置下的静态分析 A/B 试验**](https://zenn.dev/keigoly/articles/8738d8d241b5a1)

  一篇日文实践报告在单独的项目目录中把 REA 6.4.0 接入 Claude Code，屏蔽其 170 个工具中的 43 个以及常见的命令行启动方式，并在两个真实任务上比较启用与禁用 REA 的运行：一个 Electron 终端的分发文件，以及一份保存的 HAR 通信记录。两组都给出正确答案，而启用 REA 的一组耗时最多为 2.00 倍、按 API 计价的费用最多为 1.67 倍。这是分析评估与安全配置案例，而非重建案例。

  案例 · 混合工具流程 · [使用条件与证据](https://awesomerea.org/zh/resources/rea-claude-code-isolated-ab-case/)

- [**恐龙跑酷：经 REA 检查、由 Codex 重建的速度规则**](https://github.com/zhxunzh84/rea-dino-reverse-engineering)

  作者使用 REA 的 MCP 浏览器工具被动捕获 wayou 开源 T-Rex Runner 页面已加载的 JavaScript，再由 Codex 在一个自包含的 HTML5 Canvas 游戏中重建其加速规则。报告以 SHA-256 标识所捕获的脚本，并区分已核实的源码事实与重建选择；只主张速度规则一致，不主张完整玩法等价。

  案例 · 混合工具流程 · [使用条件与证据](https://awesomerea.org/zh/resources/rea-dino-runner-community-case/)

- [**BaoCut Design：移植重建的设计稿与设计系统编辑器**](https://github.com/JimLiu/baocut/tree/7aa049e82e1367da013b7aba80f0b79033fa04ad/packages/design-runtime)

  记录 BaoCut 的设计稿（画布）与设计系统编辑器；项目称其按 1:1 移植自 Claude Design 编辑器的 TypeScript 重建，并在智能体会话中提供标注与导出。运行时说明记录了对照原脚本修正的标识符，以及画布主页面 20463 个函数中有 19111 个结构完全一致的比对结果。未审阅的差异、未公开的重建记录及复用权利仍待确认；不主张恢复任何托管后端。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/baocut-design-canvas-case/)

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

- [**东方 Project 重建：贯穿三款游戏的智能体驱动方法**](https://rea.tools/blog/touhou-reconstruction/)

  REA 网站发表的一篇文章及其固定版本的证据说明，介绍一位作者以智能体驱动重建 TH08、TH095 与 TH04 的过程。文章依据公开提交与进度记录标注里程碑，区分精确比对与可游玩构建两类判定依据，并记录 TH08 一项检查漏查错误浮点字面量数据的问题。项目结果仍为作者报告；REA 的作用是为智能体提供分析证据，而非完成重建本身。

  案例 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-touhou-reconstruction-method-case/)

- [**TicTacToe-AI：REA 分叉对单个游戏方法的有限重建**](https://github.com/heaven-hm/re-agent/tree/develop/benchmarks/tictactoe)

  作者的 REA 分叉（发帖时名为 rea-engine，后更名为 RE-Agent）反编译 GPL 许可的 TicTacToe-AI 游戏所发布的 .NET 可执行文件，重新编译恢复出的 C# 与资源，并依据原始 IL 修复一处反编译错误。差分探针在一个状态判定方法的全部 19,683 种棋盘赋值上运行原版与重建代码，并比较六张窗体渲染图。报告只判定该方法通过，整个游戏仍属部分重建。

  案例 · 混合工具流程 · [使用条件与证据](https://awesomerea.org/zh/resources/rea-engine-tictactoe-case/)

- [**UltraSunnyMoon：以 REA 主导的部分《宝可梦 究极之日》重建**](https://github.com/tylergraydev/UltraSunnyMoon)

  作者使用固定版本的 REA 与 Ghidra，分析使用者自备的《宝可梦 究极之日》基础版可执行文件，由拆分出的对象逐字节重建该文件，并替换进两个编译后的小型 C 运行时例程。两处替换均经行为测试但与原字节不一致，其余字节均保持原样；同一段录制输入在 Azahar 模拟器中让原版与混合构建到达相同的卧室移动场景。零售编译器识别、精确匹配、模块加载及更广泛的游戏行为仍待解决。

  案例 · 混合工具流程 · [使用条件与证据](https://awesomerea.org/zh/resources/ultrasunnymoon-rea-case/)

- [**DX-Ball：借助 REA 并由 Codex 完成的函数级重建**](https://github.com/N0zoM1z0/dx-ball)

  作者让 Codex 通过 REA 的 Ghidra 工具检查英文版 DX-Ball 1.07 可执行文件并恢复为带类型的 C/C++，再用同时代的 Visual C++ 4.0 编译每个函数，在映射重定位后与原文件逐字节比较。同一套源码还可构建 MinGW Windows 游戏和可移植核心库。精确重建仍在进行中；REA 另行发布的声像展示只覆盖其中一个函数。

  案例 · 混合工具流程 · [使用条件与证据](https://awesomerea.org/zh/resources/dx-ball-rea-reconstruction-case/)

- [**re2ds：Resident Evil 2 的原生 Nintendo DS 引擎**](https://github.com/eray1605/re2ds)

  在原生 Nintendo DS 引擎中重新实现 Resident Evil 2 PS1 版的游戏规则，并用转换工具把使用者自有光盘中的数据转为 DS 格式。辅助脚本把 PS1 可执行文件包装成 ELF，供 REA 的 Ghidra 通道分析；分析笔记注明各部分所依据的 PS1 函数与数据表，链接该项目的 Reddit 帖称其借助 REA 和 Claude Code 完成。据报告 Leon 第一张光盘已可游玩，Claire 光盘、多数敌人类型和部分菜单仍未完成。

  案例 · 混合工具流程 · [使用条件与证据](https://awesomerea.org/zh/resources/re2ds-nds-engine-case/)

- [**LASRecomp：《织梦岛》静态重编译案例**](https://github.com/peiikai/LASRecomp)

  通过静态重编译，将 2019 年 Switch 版《塞尔达传说：织梦岛》重建为原生桌面程序。作者称大部分代码、工具与逆向工作由 Claude Code 完成，人类负责指导和复核。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/lasrecomp/)

- [**ArkWeb：双游戏动作与碰撞桥接实验**](https://github.com/luki-1/ArkWeb)

  同时运行《漫威蜘蛛侠：重制版》与《蝙蝠侠：阿卡姆骑士》，将哥谭碰撞数据传入蜘蛛侠的物理世界，再将其渲染画面合成到阿卡姆中。这是实验性的运行时桥接，并非恢复出的独立游戏或新引擎。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/arkweb-two-game-case/)

- [**Perfect Dark：生成一致 ROM 的 Nintendo 64 反编译重建**](https://github.com/n64decomp/perfect_dark)

  重建 Perfect Dark 的 Nintendo 64 代码，并提供生成一致 ROM 的构建流程。项目将重建源码与使用者自备原 ROM 中的素材结合，再检查各版本产物的哈希。这是可复现构建研究案例，与独立的原生 PC 移植不同；此处的一致性结果仍为项目报告。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/perfect-dark-matching-decomp-case/)

- [**Super Mario Sunshine：基于 AI 辅助反编译的原生 PC 移植**](https://github.com/chasem-dev/sms-pc-port)

  以固定版本的一致性反编译分支为基础，构建 Super Mario Sunshine 北美版的原生 PC 移植，并为图形、光盘、音频、输入和系统服务提供宿主平台层。该分支的 README 称，其代码的重建与匹配大量借助 AI；移植项目记录了脚本化回归哈希，以及与原版捕获数据的逐步对照。尚未匹配的函数仍可能与原版行为不同，游戏数据须来自使用者自己的光盘镜像。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/sms-pc-port-case/)

- [**《姆吉拉的假面》：生成一致美版 N64 ROM 的反编译重建**](https://github.com/zeldaret/mm)

  依据游戏内信息和静态或动态分析，为《塞尔达传说：姆吉拉的假面》重建 C 源码库，并重新构建美版 Nintendo 64 ROM。构建流程从使用者自备的 ROM 中取得素材和汇编，再用仓库保存的 MD5 校验输出。团队声明不会制作 PC 移植；另行收录的 Zelda 64: Recompiled 只注明借用了其头文件和部分函数。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/zelda-mm-decomp-case/)

- [**DLSSNR-AMD：为 RDNA4 重新实现 DLSS 5 神经渲染**](https://github.com/mochizuki0323/DLSSNR-AMD)

  将 NVIDIA DLSS 5 库中的神经渲染网络重新实现为面向 AMD RX 9000（RDNA4）显卡的 Vulkan 计算着色器，并通过兼容 NGX 的核心模块以及 ReShade 或 Vulkan 层等途径提供给游戏。项目不分发权重：安装程序从使用者自己的 nvngx\_dlssnr.dll 310.9.16 或 310.8.0 中提取权重并核对哈希。项目将输出与 NVIDIA DLL 在 RTX 5090 上的结果对比，报告画面接近但并非逐位一致。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/dlssnr-amd-neural-rendering-case/)

- [**《旷野之息》：Switch 主程序的逐函数一致性反编译**](https://github.com/zeldaret/botw)

  以 C++ 重新实现《塞尔达传说 旷野之息》Switch v1.5.0 主程序的部分代码，并逐个函数与原始机器码比对。项目自称是反编译与重新实现的混合体：不含游戏素材，生成的 ELF 仅包含已重新实现的函数、无法运行游戏，移植到其他平台也明确不是目标。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/botw-decomp-case/)

- [**《天空之剑》：以哈希校验重新链接的 Wii 版反编译**](https://github.com/zeldaret/ss)

  以使用者自备的 NTSC-U 1.0（SOUE01）光盘文件为起点，为《塞尔达传说 天空之剑》Wii 版的 main.dol 和 REL 模块重建 C++ 源码。标为一致的对象由源码编译，再与从原文件拆分出的其余对象链接，并以 SHA-1 哈希校验结果；仓库不含素材或汇编，也不是移植。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/skyward-sword-decomp-case/)

- [**2 Ship 2 Harkinian：基于反编译的《姆吉拉的假面》原生移植**](https://github.com/2ship2harkinian/2ship2harkinian)

  以改编自 zeldaret/mm 反编译的源码为基础，构建《塞尔达传说：姆吉拉的假面》的原生 Windows、Linux 和 macOS 版本，并由 libultraship 重新实现 N64 SDK 函数。游戏数据来自使用者自备的 ROM，打包为可被自定义素材包覆盖的存档文件。它面向带增强功能的可玩 PC 移植，而不是逐字节一致的 ROM。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/2ship2harkinian-mm-port-case/)

- [**Ship of Harkinian：基于反编译源码的《时之笛》原生移植**](https://github.com/HarbourMasters/Shipwright)

  以《时之笛》反编译项目的源码为基础，将游戏构建为原生 PC 程序，用 libultraship 替代 N64 的 libultra SDK，并以 DirectX 11、OpenGL 或 Metal 渲染。不随附游戏素材，而是从使用者自备的受支持 ROM 转换生成 .o2r 归档；移植版还加入了即时存档、替换与自定义素材等增强功能。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/ship-of-harkinian-oot-port-case/)

- [**《缩小帽》：面向五个 ROM 的 GBA 反编译重建**](https://github.com/zeldaret/tmc)

  依据游戏内信息和静态或动态分析，为《塞尔达传说：缩小帽》重建 C 源码库，可构建美版、欧版、日版及两个演示版共五个 Game Boy Advance ROM。每个版本的素材都来自使用者自备的原始 ROM，常规构建会核对产物的 SHA-1 哈希。项目仍在进行中，ROM 的部分内容可能尚不能移动。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/zelda-tmc-decomp-case/)

- [**《时之笛》：16 个版本均以 MD5 校验 ROM 构建的反编译**](https://github.com/zeldaret/oot)

  借助游戏本身的信息以及静态与动态分析，为《时之笛》重建 C 源码库，可重新构建 Nintendo 64、GameCube 和 iQue Player 共 16 个 ROM 版本。素材取自使用者自备的 ROM，默认构建会以对应版本的 MD5 校验；README 说明项目不制作 PC 移植，并仍称仓库处于开发中。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/ocarina-of-time-decomp-case/)

- [**Project Arwing：由一致性反汇编重编译的 Star Fox**](https://github.com/carlosrmz009/arwing)

  依据运行覆盖率和递归下降反汇编 Star Fox 的 65816 与 SuperFX 代码，重新汇编出与原 ROM 一致的文件，再静态翻译为 C，运行于从零编写的 SNES 运行时，支持 Windows、macOS 和 Linux。录制会话中未执行到的代码，以及与 ROM 不再一致的 RAM 代码，回退到解释器执行；README 报告两条路径的逐帧哈希一致。生成的 C 是机械翻译而非手工反编译的源码，结果仍为项目报告。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/project-arwing-star-fox-recomp-case/)

- [**Project Arwing (2)：由一致性反汇编重编译的 Star Fox 2**](https://github.com/carlosrmz009/arwing2)

  从以运行覆盖率为种子的 65816 与 SuperFX 反汇编重建 Star Fox 2：反汇编可重新汇编为与原 ROM 一致的文件，再静态翻译为 C，生成原生 Windows、macOS 和 Linux 版本。未执行到的代码及与 ROM 不一致的 RAM 代码由解释器执行，README 报告其与解释运行的逐帧哈希一致。项目接受 SNES Classic 版映像，不支持 1995 年的原型版；结果仍为项目报告。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/project-arwing-2-star-fox-2-recomp-case/)

- [**Little Planet：由一致性反汇编重编译的 Sonic CD**](https://github.com/carlosrmz009/littleplanet)

  依据运行覆盖率和递归下降，反汇编 Sonic CD 光盘上的全部可执行文件并逐字节一致地重新汇编，再将代码静态翻译为 C，运行于从零编写、以高层实现替代 BIOS 的 Mega-CD 运行时。重编译代码块只在内存仍为其来源代码时执行，并有脚本以 96 段关卡运行逐帧对照解释器。项目还以补丁加入宽屏和逐区存档；结果仍为项目报告。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/little-planet-sonic-cd-recomp-case/)

- [**vf2-decomp：经差分验证的 Virtua Fighter 2 代码恢复**](https://github.com/celsowm/vf2-decomp)

  将 Virtua Fighter 2 Version 2.1 的 Sega Model 2A i960 程序恢复为可移植、非一致性的 C17 代码，每条恢复路径须在受控边界上与参考 i960 执行器一致才被接受。仓库还提供 ROM 校验、i960 与 68000 分析工具、有限范围的 Model 2A 硬件模型，以及基于快照的差分运行器。README 说明它尚不是可游玩的移植；对战流程、格斗、物理、AI、光栅化及大部分音频仍未完成。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/vf2-decomp-differential-recovery-case/)

- [**z2rs：以模拟器对照逐步重建《塞尔达传说 II》的 Rust 项目**](https://github.com/troyedwardsjr/z2rs)

  以 Rust 重建 NES 游戏《塞尔达传说 II：林克的冒险》，逐个替换游戏的 6502 例程，可运行于桌面、浏览器和 Android。内置解释器仍执行使用者的 ROM，并把已移植例程交给 Rust 实现；验证工具将 RAM、精灵、调色板和画面与参考模拟器逐帧比较。它是参考社区反汇编、以行为为准的类净室重建，而不是反编译，也还不是独立完整的引擎。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/z2rs-zelda2-reconstruction-case/)

- [**sm64ex：基于反编译成果的 Super Mario 64 增强版 PC 移植**](https://github.com/sm64pc/sm64ex)

  基于反编译源码构建原生 Super Mario 64 可执行文件，在 n64decomp 重建成果的 sm64-port 分支之上，增加渲染器、输入、视角、存档格式和外部数据等选项。游戏素材在构建时从使用者自备的 ROM 中提取。这是非一致性的增强移植，而不是逐字节一致的 ROM 重建。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/sm64ex-pc-port-case/)

- [**Ghostship：基于 libultraship 的 Super Mario 64 原生移植**](https://github.com/HarbourMasters/Ghostship)

  将反编译风格的游戏源码编译到 libultraship 平台库上，把 Super Mario 64 构建为原生 PC、Switch 和 Android 程序。附带的提取工具会在首次启动或构建时，把使用者自备的美版或日版 ROM 转换为 O2R 存档。项目提供现代渲染器、配置菜单和模组存档加载，而不是生成一致的 ROM。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/ghostship-sm64-port-case/)

- [**Super Mario Sunshine：仍在推进的 GameCube 一致性反编译重建**](https://github.com/doldecomp/sms)

  重建 Super Mario Sunshine 的 C++ 源码，目标是让原版 Metrowerks 编译器为四个 GameCube 发行版本及 Switch 版 3D All-Stars 生成逐字节一致的目标文件。目标二进制取自使用者自备的光盘镜像，objdiff 按函数比对重建出的目标文件。工作尚未完成，仓库在人工流程之外还发布了面向 AI 智能体的贡献规则。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/sms-matching-decomp-case/)

- [**Dusklight：基于反编译的《黄昏公主》原生移植**](https://github.com/TwilitRealm/dusklight)

  以 zeldaret/tp 反编译项目和 Aurora GameCube／Wii 兼容层为基础，将《塞尔达传说 黄昏公主》重新实现为桌面与移动平台的原生应用。程序读取使用者自备的光盘镜像运行，不附带任何素材；项目力求忠于原作，同时加入新选项、增强功能和模组。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/dusklight-twilight-princess-port-case/)

- [**Metaforce：在反编译之上重建的《密特罗德 Prime》引擎重实现**](https://github.com/AxioDL/metaforce)

  Metaforce 于 2015 年作为《密特罗德 Prime》引擎的逆向重实现项目启动，现已在 PrimeDecomp 一致性反编译之上重写。其原生应用借助 Aurora GameCube 兼容层，将这些游戏代码以非一致模式编译为桌面和移动端程序，并读取使用者选择的光盘镜像。README 表示重写稳定之前暂不提供构建版本。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/metaforce-metroid-prime-case/)

- [**Super Mario Sunshine（美版）：AI 辅助的一致性反编译分支**](https://github.com/chasem-dev/sms-english)

  将 doldecomp 的 Super Mario Sunshine 反编译工作扩展到北美 GMSE01 版本。README 称大量使用了 AI，仓库中的智能体规则、工作顺序和进度文件也记录了按批次编排 Claude 与 Codex 的方式。项目报告重建的 DOL 逐字节一致，但尚未完成的目标文件仍取自使用者光盘中提取的代码。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/sms-english-gmse01-decomp-case/)

- [**Donkey Kong 64: Recompiled：基于 N64Recomp 的原生移植**](https://github.com/Rainchus/Donkey-Kong-64-Recompiled)

  使用 N64Recomp 将美版 Nintendo 64《大金刚 64》静态重编译为原生移植版，并以 RT64 作为渲染器。该移植并非基于反编译源码构建，但借用仍在进行中的 DK64 反编译项目的头文件和部分函数来实现补丁与增强。其重编译配置读取仓库内的符号转储和 ROM，而非反编译生成的 ELF。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/dk64-recompiled-case/)

- [**《黄昏公主》：GameCube 版代码完全一致的反编译**](https://github.com/zeldaret/tp)

  重建《塞尔达传说 黄昏公主》的源码，使其能重新编译出与原版一致的二进制文件；GameCube、Wii 与 Nvidia Shield 各版本通过条件编译共用同一套代码。README 报告 GameCube 版代码已完全一致，但尚未链接全部翻译单元，调试版与 Wii 版的对齐仍在进行；仓库不含素材或汇编，也不会制作移植。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/twilight-princess-decomp-case/)

- [**Castlevania: Symphony of the Night：覆盖 PlayStation、PSP 与 Saturn 版本的一致性反编译**](https://github.com/Xeeynamo/sotn-decomp)

  从《恶魔城 月下夜想曲》的 PlayStation、PSP 和 Saturn 版二进制重建 C 源码，目标是逐字节编译出与原游戏文件一致的产物。这一进行中的构建将已反编译代码与从使用者自备光盘镜像提取的素材和汇编结合，再按版本检查 SHA-1 哈希。同一仓库中的原生 PC 实验被文档说明为尚未完成，并不是已发布的移植。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/sotn-matching-decomp-case/)

- [**LEGO Island 可移植版：反编译源码的多平台移植**](https://github.com/isledecomp/isle-portable)

  将 LEGO Island 反编译源码改造为可在桌面、移动设备、游戏主机、DOS 及 Web 上构建的移植版本。项目以 SDL3、miniaudio、iniparser 和自行重新实现的 Direct3D Retained Mode 替代仅限 Windows 的子系统，并力求保持核心玩法不变。它移植的是重建源码，而不校验与原版逐字节一致的二进制文件，因此有别于精确重构建的反编译案例。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/lego-island-portable-case/)

- [**c1：PlayStation 版《古惑狼》的 C 语言移植**](https://github.com/wurlyfox/c1)

  将 PlayStation 版《古惑狼》的原始游戏代码逐函数移植为 C 语言；其编码规范要求为函数标注原实现的地址。目前只有基于 OpenGL、SDL2 和 FluidSynth 的 PC 构建可用；它读取用户自备游戏光盘中的素材文件，仅能部分游玩。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/crash-bandicoot-c1-port-case/)

- [**Metroid Prime Port：AI 辅助完成的 PrimeDecomp 反编译原生移植**](https://github.com/Odrannnn/MetroidPrimePort)

  将 PrimeDecomp 对《密特罗德 Prime》游戏与引擎代码的反编译结果编译为原生 C++20 程序，支持 Linux、Windows 和 Android，另有实验性 macOS 版本。Aurora 提供 GameCube SDK 兼容层和渲染，移植版在运行时读取使用者自备的光盘镜像。作者声明部分代码是在其监督下借助 AI 编程助手编写的。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/metroid-prime-port-case/)

- [**《风之杖》：以哈希校验重新链接的 GameCube 版反编译**](https://github.com/zeldaret/tww)

  为《塞尔达传说 风之杖》GameCube 版的可执行文件和 REL 模块重建源码，涵盖美版／韩版、PAL 版、日版及日本体验版。已匹配的单元由源码编译，再与从使用者光盘中拆分出的对象链接，并按各版本的 SHA-1 哈希校验；仓库不含素材或汇编，范围是 GameCube 版而非 HD 重制版。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/wind-waker-decomp-case/)

- [**Sonic Mania：面向 RSDKv5 引擎的游戏代码反编译重建**](https://github.com/RSDKModding/Sonic-Mania-Decompilation)

  以 C 重建《索尼克狂欢》的游戏代码，并与另行反编译的 RSDKv5 或 RSDKv5U 引擎一起构建，支持 Windows、Linux、Switch 和 Android。素材必须来自官方发行的 Sonic Mania (Plus)；项目加入了模组加载器，并可构建多个零售版本。其许可证称代码大多在功能上与原作相同，而不是逐字节一致。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/sonic-mania-decomp-case/)

- [**MediEvil Recomp：PlayStation 游戏静态重编译为 C#**](https://github.com/BlackLabelHQ/MediEvilRecomp)

  使用 RecompOne 重编译器及运行时，将北美版 PlayStation《MediEvil》静态重编译为 C# 代码。运行时代为提供 BIOS、GPU、CD-ROM 等硬件服务，项目补丁则修改渲染、宽屏和地形表现。README 强调这是重编译而非反编译，并将其标为公开测试版。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/medievil-recomp-case/)

- [**Crash Bandicoot 2 Recompiled：基于 PSXRecomp 的原生构建**](https://github.com/Zumbo06/Crash2Recomp)

  一个 Windows 启动器，借助 PSXRecomp 重编译器与运行时，将用户自备的《古惑狼 2》光盘转换为 C 代码并在本地编译，使游戏以原生代码配合模拟的 PlayStation 硬件层运行。仓库包含启动器、打过补丁的内置运行时以及详细的调试记录，不分发任何游戏代码或数据。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/crash2recomp-case/)

- [**Petari：Super Mario Galaxy 一致性反编译重建**](https://github.com/SMGCommunity/Petari)

  将 Super Mario Galaxy 的 Wii 代码重建为 C++，并以使用者从自有日版、北美版、PAL 版或韩版光盘中提取的 main.dol 为目标，逐个目标文件重建。已匹配的目标文件由源码链接，并通过 objdiff 和目标哈希检查。项目自称仍在进行中，与任何 PC 移植无关，并表示不接受 AI 生成的反编译代码。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/petari-smg-decomp-case/)

- [**Wind Waker HD Recomp：通过静态重编译实现的 Wii U 游戏原生移植**](https://github.com/ZeldaWWHDRecomp/ZeldaWWHDRecomp)

  将《塞尔达传说 风之杖 HD》Wii U 版的 PowerPC 代码预先静态重编译为 C，原生重新实现游戏所用的 Cafe OS 库，并在 Metal 或 Vulkan 上实现 GX2 图形，生成无需 Cemu 运行时的 macOS、Linux、Windows 和 Android 原生版本。所有游戏代码和数据都由使用者自己的转储在本地生成；另有仅限 macOS 的实验性构建，可改为运行独立的 ZeldaWWHDDecomp/wwhd 反编译中的函数。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/wind-waker-hd-recomp-case/)

- [**Castlevania 64: Recompiled：测试版静态重编译移植**](https://github.com/RevoSucks/CV64Recomp)

  使用 N64Recomp 将 Nintendo 64 版 Castlevania 美版 1.0 静态重编译为原生 PC 移植，并以 RT64 渲染。游戏专用的 C 补丁基于另一个 Castlevania 64 反编译项目的头文件构建。在所审提交上标记的测试版发布报告构建可用并列出已知问题，而同一提交的 README 仍称项目尚未完成。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/cv64-recompiled-case/)

- [**RSDKv5 Decompilation：重建 Retro Engine v5 与 v5U**](https://github.com/RSDKModding/RSDKv5-Decompilation)

  重建 Retro Engine（RSDK）v5 及 v5 Ultimate 运行时，即运行《索尼克狂欢》游戏代码的引擎，可构建 Windows、Linux、Switch 和 Android 版本。RSDKv5U 还能运行 RSDKv3 与 RSDKv4 游戏，例如 Sonic CD 和 Sonic 1 &amp; 2。项目增加了模组加载器、着色器编译器和额外的 Windows 后端，且不附带任何游戏数据。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/rsdkv5-engine-decomp-case/)

- [**C2C：《古惑狼 2》的混合重编译与手工反编译**](https://github.com/ughman/c2c)

  一个早期的 PlayStation《古惑狼 2》逆向工程项目：把引擎的 MIPS 机器码直接转换为一个体量巨大的 C 文件，并调用改造后的 PCSX-R 模拟器库处理硬件 I/O。转换出的函数计划逐个手工反编译为普通 C 代码，逐步替换机械转换的部分。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/c2c-crash2-hybrid-recompilation-case/)

- [**MediEvil 反编译：早期阶段、以校验值把关的 PlayStation 项目**](https://github.com/MediEvilDecompilation/medievil-decomp)

  将美版 PlayStation《MediEvil》逐步反编译为 C 源码，目标是重新生成其主程序、游戏程序及 26 个覆盖模块。splat 拆分使用者自备的光盘文件，默认构建会将全部 28 个产物与 SHA-1 校验值比较。README 称项目仍在进行中，未公布进度数据。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/medievil-decomp-case/)

- [**Conker's Bad Fur Day: Recompiled：基于 N64Recomp 的原生移植**](https://github.com/sciaschi/CBFD-Recompiled)

  使用 N64Recomp 将美版 Nintendo 64《Conker's Bad Fur Day》静态重编译为基于 N64ModernRuntime 和 RT64 的原生 Windows、Linux 与 macOS 移植版。函数名称与边界来自仓库内置、仍以汇编为主的反编译项目，而重编译的代码取自用户的 ROM，因此尚未匹配的反编译 C 代码不会改变游戏行为。作者称整个项目大量使用了 Claude Code。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/cbfd-recompiled-case/)

- [**ProjectCane：《Sly Cooper and the Thievius Raccoonus》原生 PC 移植**](https://github.com/theclub654/ProjectCane)

  将 PlayStation 2 版《Sly Cooper and the Thievius Raccoonus》美版重建为 Windows 和 Linux 上的原生 C++ 游戏，运行时使用从玩家自有光盘镜像中提取的数据。README 报告整部游戏均可游玩，同时仍在改进准确性并处理与原版的剩余差异。项目未说明其逆向工程方法，也未说明与另一个 sly1 反编译项目的关系。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/projectcane-sly1-pc-port-case/)

- [**Firefighter：将反编译的 DOS 游戏移植为 Rust**](https://gitlab.com/esr/firefighter)

  Eric S. Raymond 将 Eben Sprinsock 于 1985 年发布的 DOS 共享软件游戏 Firefighter 移植为终端游戏。项目历史记载，ChatGPT 5.5 先将 DOS 二进制反编译为 Borland Pascal，再译为 Rust；之后 Raymond 改进了界面，并修正一处计分不符。玩法未变是作者的说法；中间 Pascal 代码及任何对照运行均未公开。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/firefighter-rust-port-case/)

- [**Kingdom Hearts 358/2 Days：基于一致性反编译的原生 PC 移植**](https://github.com/Yokimitsuro/khdays-port)

  将 khdays-decomp 一致性反编译的 C 代码编译为 Windows x64 程序，并以原生平台层替代 Nintendo DS 硬件、SDK 服务及声音驱动。README 报告整款游戏无需 ARM 解释器即可运行；渲染、操作、模组支持与网络联机均为移植自身新增。这是基于反编译的移植，与其所依托的逐字节一致 DS 重建并非同一产物。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/khdays-native-pc-port-case/)

- [**ico-pc：由 PS2 反编译源码编译而成的《ICO》原生移植**](https://github.com/nathanialf/ico-pc)

  将 PlayStation 2 游戏《ICO》的反编译 C 源码原生编译到 Windows、Linux、Android、iPhone 及 Apple 芯片 Mac 上，并以宿主代码替代 PS2 硬件和 Sony 函数库。项目不解释执行或重编译任何 PS2 代码，程序在首次启动时读取玩家自备的 PAL 光盘镜像。它是另一个逐字节匹配的反编译项目的原生移植，记录了与原版的差异，并提供可选增强功能。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/ico-pc-port-case/)

- [**Sly Cooper and the Thievius Raccoonus：PlayStation 2 一致性反编译**](https://github.com/TheOnlyZac/sly1)

  将《Sly Cooper and the Thievius Raccoonus》PlayStation 2 美版可执行文件 SCUS\_971.98 重建为源码，属于进行中的一致性反编译。尚未匹配的函数仍由从使用者自备可执行文件中拆分出的汇编构建，构建会检查链接后 ELF 的 SHA-1。产物需在 PCSX2 中配合原版光盘素材运行，并不是原生 PC 移植。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/sly1-matching-decomp-case/)

- [**《宝可梦 绿宝石》：生成一致 ROM 的 Game Boy Advance 反编译重建**](https://github.com/pret/pokeemerald)

  为 Game Boy Advance 版《宝可梦 绿宝石》重建可构建的 C 源码，游戏脚本和数据以汇编指令形式保存。默认的 agbcc 构建生成 pokeemerald.gba，make compare 将其与英文原版 ROM 的 SHA-1 比对；可选的现代 GCC 构建不做哈希校验。图像和音频源文件已提交在仓库中，因此文档所述的构建流程不读取原 ROM。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/pokemon-emerald-decomp-case/)

- [**Paper Mario：覆盖四个版本的一致性 Nintendo 64 反编译**](https://github.com/pmret/papermario)

  将 Paper Mario 的 Nintendo 64 代码重建为 C 源码，可重新构建美版、日版、PAL 版和 iQue 版 ROM。构建流程从使用者自备的原 ROM 取得素材和比较输入，再将每个产物与记录的 SHA-1 比对。项目可变的进度报告显示已无未匹配函数，但 README 仍称反编译在进行中；该项目与 PaperBoat 原生移植不同。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/paper-mario-matching-decomp-case/)

- [**Budokai Tenkaichi 3：基于一致性反编译的原生 PC 移植**](https://github.com/z3xox/Tenkaichi3Decomp)

  将 Dragon Ball Z: Budokai Tenkaichi 3（PS2 美版 SLUS-21678）的反编译代码编译到 PC，运行在新的渲染、音频、输入和平台层上，而非借助模拟器。游戏代码来自独立的 BT3-Decompiled 一致性反编译项目，游戏数据从使用者自备的光盘镜像读取。README 报告完整游戏流程可运行、联网对战处于实验阶段，并称项目借助 AI 完成；这些结果仍为项目报告。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/tenkaichi3-pc-port-case/)

- [**D2R Mobile：在 Apple 设备上重新托管 Diablo II: Resurrected 的 Switch 程序**](https://github.com/jhaizhou-ops/d2r-mobile)

  在 iPhone、iPad 和 Apple 芯片 Mac 上原生运行 Nintendo Switch 版自身的 aarch64 程序，仅改写依赖 Horizon 内核的指令，并以 Metal 提供其系统服务与 NVN 图形 API。着色器由使用者自有文件离线转译，项目另行加入触控界面与终局玩法。这是重新托管的兼容层，不是反编译或重编译出的源码。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/d2r-mobile-switch-rehost-case/)

- [**Ratchet &amp; Clank：记录了代理流程的 PS2 一致性反编译**](https://github.com/OpenRAC/rac1-decomp)

  为 2002 年《Ratchet &amp; Clank》PlayStation 2 欧版 v2.00 可执行文件 SCES\_509.16 重建 C 源码，每个函数都链接在零售版的原地址。尚未反编译的函数仍由从使用者自备可执行文件生成的反汇编构建，构建会对照零售版审核函数、布局和整个映像。项目记录了由 LLM 代理执行匹配的流程，并以成文的构建保真规则界定何为匹配。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/rac1-matching-decomp-case/)

- [**Banjo: Recompiled：基于 N64Recomp 的《Banjo-Kazooie》原生移植**](https://github.com/BanjoRecomp/BanjoRecomp)

  使用 N64Recomp 将美版 1.0 Nintendo 64《Banjo-Kazooie》静态重编译为基于 N64ModernRuntime 的原生移植版，由 RT64 渲染并加入模组支持。与 Zelda 64: Recompiled 一样，它并非基于反编译源码构建；由《Banjo-Kazooie》反编译项目生成的符号仓库提供函数名称，用于在 ROM 中定位代码和编写补丁。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/banjo-recompiled-case/)

- [**《宝可梦 火红／叶绿》：生成一致 ROM 的 Game Boy Advance 反编译重建**](https://github.com/pret/pokefirered)

  为 Game Boy Advance 英文版《宝可梦 火红／叶绿》重建可构建的 C 源码，游戏脚本和数据以汇编指令形式保存。默认的 agbcc 构建可生成六个 ROM 镜像，涵盖两款游戏的 1.0 与 1.1 版本及两个标为 switch 的变体，并分别按各自的 SHA-1 清单校验。图像和音频源文件已提交在仓库中，因此文档所述的构建流程不读取原 ROM。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/pokemon-firered-leafgreen-decomp-case/)

- [**PaperBoat：基于反编译成果的 Paper Mario 原生移植**](https://github.com/HarbourMasters/PaperBoat)

  以 pmret 和 Paper Mario DX 项目为基础，将 Paper Mario 反编译源码编译为基于 libultraship 的原生美版应用。Torch 把使用者自己的 ROM 转换为本地素材归档，移植另加入多种渲染后端、增强功能和归档式模组。桌面版已有正式发布；Android、iOS 和网页构建则在开发分支中有文档说明。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/paperboat-paper-mario-port-case/)

- [**Halo 2：智能体辅助的 LTCG Xbox 版一致性反编译**](https://github.com/kirklandsig/halo2-decompiled)

  Halo 2（初代 Xbox）的进行中一致性反编译：贡献者编写 C 与 C++ 代码，由原时代编译器以链接时代码生成方式构建整个程序，须逐函数还原出零售版可执行文件的字节。README 报告游戏函数字节的匹配比例接近一半，原生移植留待后续阶段。项目披露维护者的大量工作在 Claude 与 Codex 编程智能体流水线中进行。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/halo2-matching-decomp-case/)

- [**DiabloWeb：基于 Devilution 的 WebAssembly 浏览器移植**](https://github.com/d07RiV/diabloweb)

  将社区重建 Diablo 原始源码的 Devilution 精简分支编译为 WebAssembly，并配合 React 前端，使 Diablo 可在网页浏览器中运行。该分支移除了 Storm、DiabloUI、DirectX 和 Windows 依赖，并为浏览器改写事件处理。这是基于重建成果的移植，本身未报告一致性或行为等价检查。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/diabloweb-devilution-wasm-port-case/)

- [**pokered：一致构建的《精灵宝可梦 红／蓝》反汇编**](https://github.com/pret/pokered)

  以 RGBDS 汇编重建 Game Boy 游戏《精灵宝可梦 红／蓝》，图像和数据以可编辑的源文件保存。同一源码树可构建美版／欧版红、蓝 ROM、一个蓝版调试构建以及 Virtual Console 版本的补丁，并逐一与记录的 SHA-1 比对。它是完整的反汇编项目，而非反编译为高级语言的源码。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/pokered-disassembly-case/)

- [**Lighthouse：基于反编译项目的《Banjo-Kazooie》PC 移植**](https://github.com/HarbourMasters/Lighthouse)

  一个面向 Windows、Linux 和 macOS 的《Banjo-Kazooie》原生移植，将游戏 C 源码（其中许多标注了《Banjo-Kazooie》反编译项目中的文件路径）与重新实现 N64 SDK 的 libultraship 一起编译。Torch 将用户的 ROM 提取为素材归档；移植版还加入了 Anchor 联机、ROM 修改版与语言包支持以及随机器。与 Banjo: Recompiled 不同，它基于反编译源码构建，而非对 ROM 代码进行静态重编译。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/lighthouse-banjo-kazooie-port-case/)

- [**Lost Odyssey Recomp：将 Xbox 360 角色扮演游戏静态重编译为原生移植**](https://github.com/freefrank/LostOdysseyRecomp)

  使用打过补丁的 XenonRecomp 工具转换 Lost Odyssey 的 Xbox 360 PowerPC 可执行文件，并在原生运行时上运行生成代码，经 Direct3D 12、Vulkan 或 Metal 渲染。Windows、Linux、macOS 和 Android 安装包导入使用者自己的光盘数据。维护者记录了借助 Claude Code 与 Codex CLI 的开发过程，并把每次发布与验证、验收分开记录。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/lost-odyssey-recomp-case/)

- [**Super Smash Bros. Melee：可移位构建的 GameCube 一致性反编译**](https://github.com/doldecomp/melee)

  Super Smash Bros. Melee 美版 1.02（GALE01）的一致性反编译：使用原版 Metrowerks 编译器从 C 代码重建 main.dol，并与零售版的 SHA-1 比对。decomp.dev 报告所审提交的代码已完全反编译并链接，README 称目前工作主要是命名与清理。由于构建可以移位，另有非一致性模式，供模组作者加入代码，再配合自己转储的光盘运行生成的 DOL。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/melee-matching-decomp-case/)

- [**pokecrystal：一致构建的《精灵宝可梦 水晶》反汇编**](https://github.com/pret/pokecrystal)

  以 RGBDS 汇编重建 Game Boy Color 游戏《精灵宝可梦 水晶》，图像、地图和数据以可编辑的源文件保存。同一源码树可构建国际版 1.0 与 1.1、澳大利亚版、两个调试构建以及一个 Virtual Console 补丁，并逐一与记录的 SHA-1 比对。配套文档说明脚本命令格式以及原版游戏中的已知错误。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/pokecrystal-disassembly-case/)

- [**《宝可梦 心金／魂银》：校验一致的进行中 DS 反汇编项目**](https://github.com/pret/pokeheartgold)

  以进行中的反汇编项目重建美版 Nintendo DS《宝可梦 心金／魂银》，其中部分代码已反编译为 C。每次默认构建都会按各游戏的 SHA-1 清单校验 ARM9 与 ARM7 二进制、文件系统及完整 ROM。README 提醒，由于反编译尚未完成，改变代码或数据布局的修改可能导致游戏崩溃。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/pokemon-heartgold-soulsilver-disassembly-case/)

- [**FFTARecomp：Final Fantasy Tactics Advance 的静态重编译**](https://github.com/Jorge262007/FFTARecomp)

  基于 JRickey 的 gba-recomp 工具链，将使用者自有的 Final Fantasy Tactics Advance（美版）Game Boy Advance ROM 预先重编译为可在 Windows、Linux 和 Steam Deck 上运行的原生代码。ARM 与 Thumb 代码被转译为 C 并在本地编译，Rust 运行时则模拟主机的图形、声音、DMA、定时器及 BIOS 调用。移植另行加入宽屏、缩放、快进和可重映射操作。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/fftarecomp-gba-static-recomp-case/)

- [**SymphonyRecomp：用 RecompOne 静态重编译《恶魔城：月下夜想曲》**](https://github.com/BlackLabelHQ/SymphonyRecomp)

  使用 BlackLabelHQ 的 RecompOne 将北美 PlayStation 版《恶魔城：月下夜想曲》静态重编译为 C#；其运行时模拟 BIOS、内存映射 I/O、GPU 和光驱，使游戏无需主机 BIOS 即可原生运行。按覆盖段划分的函数映射与补丁加入了宽屏、便利性改进、随机器和作弊功能。项目借助 SOTN 反编译项目的资料为函数命名，但强调它是重编译而非反编译。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/symphonyrecomp-case/)

- [**The Two Towers Recompiled：初代 Xbox 静态重编译移植**](https://github.com/Gumpolas/TooTawersRecomp)

  使用随附的 xboxrecomp 工具包，将《The Lord of the Rings: The Two Towers》（Xbox 美版，2002）的 x86 代码静态重编译为 C，生成原生 Windows、Linux 及实验性 macOS 构建。重编译源码由玩家自己的 default.xbe 在本地生成，游戏数据来自其光盘镜像或已提取的文件夹。README 报告游戏可以完整游玩，并列出画面、帧率和模组方面的问题。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/two-towers-recompiled-case/)

- [**Melee Unlocked：Melee 的 Windows 源码移植与静态重编译**](https://github.com/Hero88go/melee-unlocked)

  Super Smash Bros. Melee（NTSC 1.02）的 Windows 测试版构建，包含两套引擎：源码移植将 doldecomp 反编译编译为原生库，静态重编译则将零售版 DOL 的 PowerPC 代码及 Slippi 的 Gecko 代码转换为 C++。两者都运行在原生运行时上，提供 Direct3D 渲染、解锁的显示帧率和原生实现的 Slippi 回滚对战。全部游戏数据来自使用者自备的 ISO，README 称开发借助了 AI。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/melee-unlocked-case/)

- [**pokeruby：一致构建的《精灵宝可梦 红宝石／蓝宝石》反编译**](https://github.com/pret/pokeruby)

  以 C 源码重建 Game Boy Advance 游戏《精灵宝可梦 红宝石／蓝宝石》，使用 pret 的 agbcc 编译器构建，并附有汇编数据脚本和可编辑图像。一致构建涵盖英文版 1.0、1.1、1.2 修订版、调试构建以及德文初版，并逐一与保存的 SHA-1 比对。另有使用现代 GCC 的构建目标，不以一致为目标。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/pokeruby-decomp-case/)

- [**Vandal Hearts：基于一致性反编译的原生 PC 移植**](https://github.com/HalmyLyseas/VandalHearts-PcPort)

  以 shao113 的 PlayStation 版 Vandal Hearts 一致性反编译为基础，新增日版一致性代码树，并将两者延伸为原生 Windows 与 Linux 移植。SDL2、OpenGL 或 Metal 及 OpenAL 后端替代主机的 GPU、GTE、CD-ROM／XA、SPU、MDEC 和手柄接口，同一可执行文件可运行美版、亚洲版和日版光盘。每次修改仍须通过一致性构建检查；Tactical Mode、高清包等 PC 专属功能均为可选。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/vandal-hearts-pc-port-case/)

- [**《宝可梦 白金》：校验一致的 Nintendo DS 反编译重建**](https://github.com/pret/pokeplatinum)

  将美版 Nintendo DS《宝可梦 白金》重建为 C 源码，默认重建修订版 1，也可按需构建修订版 0。默认的 make 目标会运行 Meson 检查，按 SHA-1 清单校验代码二进制、文件系统及完整 ROM。README 仍称项目在进行中；贡献指南表示代码已全部为 C，但其中大量仍晦涩难懂，因此主要工作是文档和工具。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/pokemon-platinum-decomp-case/)

- [**Saints Reborn：基于 ReXGlue 的 Saints Row 静态重编译**](https://github.com/whompay/SaintsReborn)

  Saints Row（Xbox 360，2006）的非官方原生 Windows 移植：借助 ReXGlue SDK 将游戏的 PowerPC 可执行文件静态重编译为面向 x86-64 的 C++ 代码，该 SDK 还重新实现了主机的内核、GPU（基于 Direct3D 12）、音频与输入。重编译清单、游戏专用的函数替换和 SDK 补丁使结果得以运行，每位使用者都用自己的光盘在本地构建。README 报告游戏可完整通关、内置合作模式，并列出已知问题。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/saints-reborn-recomp-case/)

- [**Pokémon Platinum PC Port：基于 pret 反编译的原生移植**](https://github.com/cybervisi0n/pokeplatinum)

  基于 pret 反编译项目的分支，为《宝可梦 白金》构建原生 64 位 Windows 和 Linux 可执行文件，并以作者的 libntr 库替代 NitroSDK；同一源码树仍保留 DS ROM 构建和实验性的 Switch 目标。README 称游戏应可从头玩到尾，但可能出现崩溃和图形错误。预构建程序需要玩家自备美版 ROM，且该分支的默认构建不再运行 pret 的校验测试。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/pokemon-platinum-pc-port-case/)

- [**MikuPan：基于 Himuro 反编译的 Fatal Frame 原生 PC 移植**](https://github.com/Mikompilation/MikuPan)

  将 PS2 游戏 Fatal Frame（《零》）移植为无需模拟器的原生 PC 版本；仓库简介称其基于 Himuro 反编译项目。PS2 内核调用由桩函数替代，渲染、音频和界面由基于 SDL3 的新层实现，游戏数据则来自使用者自有的光盘。README 称移植仍处于很早期阶段，未发布一致性或还原度检查。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/mikupan-fatal-frame-port-case/)

- [**Starfox 64: Recompiled：基于 N64Recomp 的静态重编译移植**](https://github.com/sonicdcer/Starfox64Recomp)

  使用 N64: Recompiled 将 Nintendo 64 版 Star Fox 64 美版 1.1（Rev A）静态重编译为面向 Windows、Linux 和 macOS 的原生移植，并以 RT64 渲染。补丁与增强功能借用独立的 sf64 反编译项目中的头文件和部分函数，但移植本身并非由该反编译源码编译而成。README 报告支持高帧率、宽屏与模组，素材从使用者自备的 ROM 载入。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/starfox64-recompiled-case/)

- [**Syphon Filter: The Omega Strain：可逐字节重建 PS2 可执行文件的一致性反编译**](https://github.com/zm2283145/syphon-filter-omega-strain-decomp)

  将 Syphon Filter: The Omega Strain 北美版 PlayStation 2 可执行文件的大部分代码重建为 C；其余函数保留为拆分出的汇编，整体构建可逐字节重现零售版 SCUS\_972.64。仓库提交的 objdiff 报告以使用者自备的可执行文件为基准，追踪逐函数的匹配进度。这是一致性反编译案例，不是 PC 移植；进度数字仍为项目报告。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/syphon-filter-omega-strain-decomp-case/)

- [**Animal Crossing：基于 GameCube 反编译成果的原生 PC 移植**](https://github.com/flyngmt/ACGC-PC-Port)

  让 Animal Crossing 反编译所得的 GameCube C 代码在 32 位 x86 上原生运行，用转换层把 GX 图形 API 映射到 OpenGL 3.3，并以基于 SDL2 的平台代码替代主机服务。游戏素材在启动时从使用者自己的光盘镜像读取，不随项目分发。这是基于 ACreTeam ac-decomp 的移植，而非与原可执行文件一致的重建。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/animal-crossing-pc-port-case/)

- [**GoldenEye 007：覆盖三个版本的一致性 Nintendo 64 反编译**](https://github.com/n64decomp/007)

  将 GoldenEye 007 的 Nintendo 64 代码重建为 C 源码，可重新构建美版、日版和 PAL 版 ROM。素材取自使用者自备的美版 ROM，日版与 PAL 版的差异部分则取自各自的 ROM；默认构建会将每个产物与记录的 SHA-1 比对。README 仍称项目在进行中，而可变的状态页报告全部 208 个文件已完成；它与另行收录的 PC 移植不同。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/goldeneye-007-matching-decomp-case/)

- [**Starship：基于反编译的 Star Fox 64 PC 移植**](https://github.com/HarbourMasters/Starship)

  Star Fox 64 的原生 PC 移植：将游戏的反编译 C 代码与 libultraship 一同编译，该 N64 移植库重新实现了 libultra，并通过 Fast3D 渲染。首次运行时借助 Torch 工具把使用者的美版 ROM 转换为素材资源包，提供 Windows、Linux、macOS 和 Switch 版本。独立的静态重编译项目 Starfox 64: Recompiled 在其 README 中称本移植为采用不同技术的姊妹项目。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/starship-sf64-pc-port-case/)

- [**CTR Turbocharged：基于 Crash Team Racing 反编译成果的 PC 移植**](https://github.com/CameronRedmore/Crash-Team-Racing-Turbocharged)

  在 Crash Team Racing: High Octane 移植版基础上扩展而成；High Octane 源自基于 CTR-ModSDK PlayStation 反编译成果的 CTR Native 移植。本分支面向 Windows 与 Linux，提供原生 3D 渲染器、可选画面比例及最高 240 FPS 帧率。反编译游戏代码仍假定 32 位指针，并从玩家自备的 NTSC-U 光盘镜像读取素材。项目附有渲染、计时和选项测试，但设备覆盖与还原度仍为项目自述。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/ctr-turbocharged-port-case/)

- [**The Darkness Recomp：配有原生 D3D11 渲染器的 Xbox 360 静态重编译**](https://github.com/portingpete/The-Darkness-Recomp)

  使用打过补丁的 XenonRecomp 将 Xbox 360 可执行文件提前转换为 C++，构建 The Darkness 的原生 Windows x64 移植。D3D11 渲染器直接使用引擎原有的几何数据、着色器源码和设备状态绘制，而不解释主机 GPU 命令包。游戏覆盖范围与 Linux 测试结果均为项目报告，作者披露开发中使用了 OpenAI Codex 辅助。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/the-darkness-recomp-case/)

- [**MarioKart 64: Recompiled：通过 N64Recomp 静态重编译实现的原生移植**](https://github.com/sonicdcer/MarioKart64Recomp)

  使用 N64Recomp 将北美版 Nintendo 64《马力欧卡丁车 64》静态重编译为 Windows、Linux 与 macOS 原生应用，并通过 RT64 渲染。README 将其与源码移植区分开：游戏代码由使用者提供的 ROM 转换而来，反编译分支中的头文件和部分函数用于实现补丁与增强。增强功能、还原度和输入延迟等说法均为项目自述。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/mariokart64-recompiled-case/)

- [**Animal Crossing：生成一致产物的 GameCube 反编译重建**](https://github.com/ACreTeam/ac-decomp)

  将 Animal Crossing 的 GameCube 代码重建为 C 与 C++ 源码，可重新构建美版的主可执行文件及 foresta.rel 模块。基于 dtk-template 的构建从使用者自备的光盘镜像读取原始二进制与素材，再用 SHA-1 哈希校验两个产物。另有原生 PC 移植以它为基础；此处的完成度数字仍为项目报告。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/animal-crossing-gamecube-decomp-case/)

- [**《王国之心 358/2 Days》：逐字节一致的 Nintendo DS 反编译重建**](https://github.com/Yokimitsuro/khdays-decomp)

  将 Nintendo DS 欧版《王国之心 358/2 Days》的 ARM9 程序及覆盖模块重建为 C 源码，以 CodeWarrior 重新编译后逐字节一致。README 报告全部 306 个模块字节一致，约 99.5% 的函数为真正的 C，库自身的汇编另行统计；ARM7 二进制不在范围内。仓库不含 ROM、游戏素材或提取的反汇编，也不生成可玩版本。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/kingdom-hearts-days-matching-decomp-case/)

- [**TonyWasAProSkater：派生自一致性反编译的 THPS1 原生移植**](https://github.com/LANCommander/TonyWasAProSkater)

  从一个仍在进行中的零售版可执行文件一致性反编译项目派生分支，将 Tony Hawk’s Pro Skater（PlayStation 美版）移植为原生 Windows 与 Linux 程序。反编译部分用 Psy-Q 工具链重新编译已重建的函数，并与使用者自备的零售可执行文件逐字节比对；移植部分则以 SDL2 和 OpenGL 服务取代 PlayStation 硬件和库。运行需使用者自备光盘镜像；一致性与可玩性结果仍为项目报告。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/thps1-decomp-native-port-case/)

- [**P.T. PC 版：基于行为重新实现、读取 PS4 数据的引擎**](https://github.com/LoreanXavier/pt-pc)

  在新的 Vulkan 引擎上用 C++ 重新实现 P.T. 的游戏逻辑，运行时从使用者自有的 PS4 版本读取关卡、模型、贴图、声音、脚本和过场动画。作者记录了逆向得出的文件格式，并以 shadPS4 模拟器作为行为与画面的对照参考。与原作的一致程度为作者报告，项目也披露使用了 AI 编程工具。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/pt-pc-port-case/)

- [**SpaghettiKart：基于反编译源码的《马力欧卡丁车 64》原生移植**](https://github.com/HarbourMasters/SpaghettiKart)

  基于沿用《马力欧卡丁车 64》反编译项目文件结构的源码，构建适用于 Windows、Linux、macOS 和 Switch 的原生移植，运行在 libultraship 重新实现的 N64 SDK 之上。随附的 Torch 提取器将使用者自备的美版 ROM 转换为素材归档，移植还增加了模组、自定义赛道和编辑器。README 未写明其上游反编译项目，也未发布一致性或还原度检查。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/spaghettikart-mk64-port-case/)

- [**Animal Crossing: Wild World：附差分运行检查的韩版 DS 一致性反编译重建**](https://github.com/banatic/acww-decomp)

  将 Animal Crossing: Wild World 韩版 DS 游戏的 ARM9 游戏代码重建为每个函数一个 C 或 C++ 源文件，并用原版 Metrowerks 编译器和链接器对照使用者自己的 ROM 校验。每个函数另有可读的 Clean 改写版本，仓库自带的 DS 解释器在录制的游玩过程中比较 ROM 代码、原生编译的源码和改写版本。数据段、ARM7 程序、链接的 SDK 库及按原始源文件重新归组仍不在重建范围内。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/animal-crossing-wild-world-decomp-case/)

- [**King Kong Recompiled：由 AI 开发的 Xbox 360 静态重编译**](https://github.com/TekRantGaming/king-kong-recompiled)

  借助 ReXGlue 静态重编译 SDK，将 Xbox 360 版 Peter Jackson's King Kong 转译为原生 Windows 代码，并加入启动器以及显示、操控和图形选项。项目代码按主机的方式完成流式光盘读取；README 称这使游戏越过了在 Xenia 中出现的开场卡死。作者披露，该移植几乎完全由 Claude Code 完成，仓库所有者负责指导和测试。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/king-kong-recompiled-case/)

- [**Mario Party 4：美版 GameCube 一致性反编译重建**](https://github.com/mariopartyrd/marioparty4)

  将 Mario Party 4 的 GameCube 主程序和 REL 模块重建为 C 源码，可重新构建两个美版发行版本。构建会分析使用者自备的光盘镜像，并按各版本的 SHA-1 清单检查每个链接产物。欧版和日版工作已停滞，也尚无 PC 移植；此处的一致性结果仍为项目报告。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/mario-party-4-decomp-case/)

- [**SpeedBreaker：对 Xbox 360 版《极品飞车：最高通缉》的静态重编译**](https://github.com/SpeedBreakerProject/speedbreaker)

  使用打过补丁的 XenonRecomp 将 Xbox 360 版《极品飞车：最高通缉》（2005）的可执行文件转换为原生 C++，并在项目自建的运行时上执行，由运行时代替主机的内核、Xenos GPU、XMA 音频和控制器。发布版面向 SteamOS、Linux 和 Apple 芯片 Mac，另有实验性的 iPhone 与 iPad 版本，所有游戏数据均来自玩家自有的美版光盘。渲染与帧节奏方面的改进均为项目自述。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/speedbreaker-nfs-most-wanted-case/)

- [**The Sims: Bustin' Out：AI 驱动的部分 GBA 一致性反编译重建**](https://github.com/DaBrown95/tsbodp)

  逐字节重建 The Sims: Bustin' Out 的 Game Boy Advance 美欧版，并逐步用 agbcc 编译、结果一致的 C 代码替换 ROM 区域。README 称这是由 AI 驱动的实验，几乎所有代码、分析与工具都由 AI 生成。ROM 的大部分仍从使用者的转储中复制，因此整个 ROM 一致并不代表游戏已完成反编译。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/sims-bustin-out-gba-decomp-case/)

- [**Destiny 2 build 86657：Sunrise／Dawn 重建研究报告**](https://github.com/isinternets/d2-research)

  一份注明版本日期的研究报告，记录已归档 Destiny 2 build 86657 客户端的 Sunrise／Dawn 重建：在本地模拟平台登录与所考察的 Bungie 服务契约，并补充重建的任务主机策略。报告把传输、解码、对象创建、呈现与游戏玩法结果分开记录，并连同所引来源保留已被推翻的结论。它记录案例本身，不提供运行时实现，也不是恢复出的 Bungie 后端；通关与原生实验结果仍为项目报告。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/destiny2-build-86657-reconstruction-report-case/)

- [**SVR2011-Recomp：借助 ReXGlue 重编译 WWE SmackDown vs. Raw 2011**](https://github.com/shaneomac1337/SVR2011-Recomp)

  借助 ReXGlue 将 WWE SmackDown vs. Raw 2011 的 Xbox 360 可执行文件提前转换为 C++，并在源自 Xenia 的 Vulkan 运行时上构建为 Windows 程序。手工维护的清单补充自动分析遗漏的函数入口，项目补丁则处理帧节奏、音乐播放器延迟和渲染管线卡顿。作者仅在一款 AMD GPU 上测试了表演赛等模式；生涯模式与在线功能仍未测试。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/svr2011-recomp-case/)

- [**Snap64 Recomp：Pokémon Snap 的静态重编译移植**](https://github.com/JackandBeans/Snap64Recomp)

  使用 N64Recomp 将 Pokémon Snap 美版 Nintendo 64 发行版静态重编译为原生 Windows、Linux、Steam Deck 和 macOS 移植，由 RT64 负责渲染。重编译器读取从一致性 ethteck/pokemonsnap 反编译项目链接出的可重定位 ELF 及使用者自备的 ROM，游戏侧补丁则是反编译函数的修改副本。作者报告借助 Claude Code 完成移植；各项结果仍为项目报告。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/snap64-recomp-case/)

- [**Dead Rising 2: Case Zero：Xbox 360 XBLA 游戏的静态重编译移植**](https://github.com/wivi514/Dead_Rising_2_Case_Zero_Xenon_Recomp)

  使用打过补丁的 XenonRecomp 静态重编译 Xbox 360 代码，并用打过补丁的 XenosRecomp 转换着色器，为 XBLA 游戏 Dead Rising 2: Case Zero 构建可在 Windows、Linux、Steam Deck 和 Apple Silicon Mac 上运行的原生移植。专门编写的运行时提供 Vulkan 渲染器、XMA 音频、键鼠输入，以及通过作者的 XenonLive 服务实现的在线合作。通关情况与各平台结果均为项目报告。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/dead-rising-2-case-zero-recomp-case/)

- [**OpenRA：重新诠释早期 Westwood 即时战略游戏的引擎重新实现**](https://github.com/OpenRA/OpenRA)

  为早期 Westwood 即时战略游戏提供以 C# 编写的引擎，并以模组形式重新诠释 Command &amp; Conquer: Red Alert、Tiberian Dawn 和 Dune 2000。它通过自己的文件系统、MiniYAML 规则和 Lua 任务层加载原游戏内容，而不是运行或恢复 Westwood 的代码。玩法和界面有意遵循 OpenRA 自身的设计，因此并非对原可执行文件的忠实重现。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/openra-engine-case/)

- [**Dead Rising 2: Case West：同系列的 Xbox 360 XBLA 静态重编译移植**](https://github.com/wivi514/Dead_Rising_2_Case_West_Xenon_Recomp)

  使用打过补丁的 XenonRecomp 静态重编译 Xbox 360 代码，并用打过补丁的 XenosRecomp 转换着色器，为 XBLA 尾声篇 Dead Rising 2: Case West 构建可在 Windows、Linux、Steam Deck 和 Apple Silicon Mac 上运行的原生移植。它与作者另一个 Case Zero 移植共用大部分运行时，在 Vulkan 上执行主机 GPU 命令流，并提供 XMA 音频和键鼠输入。通关情况与各平台结果均为项目报告。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/dead-rising-2-case-west-recomp-case/)

- [**The Simpsons Wrestling Recompiled：基于 psxrecomp 的 PlayStation 静态重编译**](https://github.com/TekRantGaming/simpsons-wrestling-recompiled)

  借助固定版本的 psxrecomp 分支，将这款 PlayStation 游戏的 MIPS 代码转换为 C，并基于其模拟硬件行为的运行时构建 Windows 与 Linux 程序，另附启动器和专用插件。插件在不修补游戏代码的前提下，实现比赛中的 16:9 画面、通过提高模拟 CPU 频率并修正移动量达到 60 FPS、跳过片头及全部解锁。需使用者自备 NTSC-U 光盘镜像；测量结果为作者报告。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/simpsons-wrestling-recompiled-case/)

- [**OpenRCT2：RollerCoaster Tycoon 2 的开源重新实现**](https://github.com/OpenRCT2/OpenRCT2)

  以 C++ 引擎重新实现原本用 x86 汇编编写的 RollerCoaster Tycoon 2，并在原游戏数据上运行。它可载入 RCT2 存档和场景，具备相应文件时也能载入 RCT1 场景，而保存时使用自己有文档说明的乐园格式。现代平台支持、界面与 AI 改动、更高上限和多人游戏都是有意扩展，并非对原版的复现。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/openrct2-engine-case/)

- [**Touhou 6：重建东方红魔乡 1.02h 版源码**](https://github.com/GensokyoClub/th06)

  为 Touhou 6：东方红魔乡 1.02h 版的 Windows 可执行文件重建 C++ 源码，目标是用原版 Visual Studio .NET 2002 与 DirectX 8 工具链精确重新构建。reccmp 和 objdiff 将重建的二进制与使用者自备的原可执行文件逐函数比较。仓库内的进度徽章报告函数已全部实现、字节准确率为 98.03%，因此不主张整个二进制完全一致。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/th06-decomp-case/)

- [**Driver Recompiled：在本地构建游戏的 psxrecomp 安装宿主**](https://github.com/alexbeavs-ps1-ports/driver-recomp)

  将 Driver（PlayStation 美版）的 psxrecomp 静态重编译项目打包为“安装宿主”：发布包含重编译器、运行时和 recomp-ui 启动器，再由玩家电脑依据使用者自备的光盘镜像生成并编译游戏。仓库只包含配置、来自 Ghidra 的函数种子和发布自动化脚本，不含游戏代码。文档记录的状态较为有限：维护者确认一个私有构建可以进入游戏，而发布包的验收门槛仍未完成。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/driver-recomp-setup-host-case/)

- [**Himuro：Fatal Frame（《零》）PS2 一致性反编译**](https://github.com/Mikompilation/Himuro)

  将 Fatal Frame（《零》）PS2 可执行文件的美版、欧版和日版重建为 C，使用原始的 EE-GCC 2.9 工具链构建，并以使用者自备可执行文件的 SHA-1 校验结果。仓库提交的 objdiff 报告显示美版和欧版代码已全部匹配、日版仅部分匹配，少数例程仍依赖汇编或字节补丁。移植到现代硬件是项目声明的后续目标，不在本仓库范围内。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/himuro-fatal-frame-decomp-case/)

- [**DOAXVB Native PC Port：对《Dead or Alive Xtreme Beach Volleyball》的静态重编译**](https://github.com/NoRain211/doaxvb-re)

  借助 xboxrecomp 的分支将原版 Xbox《Dead or Alive Xtreme Beach Volleyball》可执行文件提升为 C 代码，并与手写运行时链接，由运行时替代内核导入、音频以及关键的 Direct3D 8 和 DirectSound API。安装程序依据使用者自有的美版光盘镜像在本地构建运行程序，并按经认证配方中的哈希校验生成文件；发布包只含工具和源码。将游戏逻辑改写为可读源码的工作目前只完成了启动线程入口。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/doaxvb-native-port-case/)

- [**TH08 Web：基于重建源码的 WebAssembly 移植**](https://github.com/N0zoM1z0/th08-web)

  使用 Emscripten 将日版 Touhou 8 1.00d 的重建 C++ 源码编译为 WebAssembly，并在游戏原有的 D3D8、DirectSound 与 DirectInput 形态接口之后接入 WebGL 2 渲染、Web Audio、浏览器输入和 IndexedDB 存档。玩家在本地选择自备的正版 DAT 文件。网页构建不主张与原二进制逐字节一致，是独立于已收录 TH08 重建的移植。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/th08-web-wasm-port-case/)

- [**OpenXcom：X-COM: UFO Defense 与 Terror from the Deep 的开源克隆**](https://github.com/OpenXcom/OpenXcom)

  以 C++/SDL 引擎重新实现 MicroProse 的 UFO: Enemy Unknown（X-COM: UFO Defense）与 X-COM: Terror from the Deep，并在使用者自己的原游戏资源上运行。物品、飞行器、研究和任务等游戏数据以 YAML 规则集表达，这些规则集也承载其标准模组及更广泛的模组生态。这是复用原内容的克隆实现，而非恢复出的 MicroProse 代码。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/openxcom-engine-case/)

- [**Skate 3 Recomp：通过 ReXGlue 实现的 Xbox 360 原生重编译**](https://github.com/mchughalex/skate3recomp)

  借助 ReXGlue SDK 的 Skate 专用分支，将 Xbox 360 版《Skate 3》重编译为 Windows、Linux 与 macOS 原生版本。自 v2.0.0 起，基于 Direct3D 12 和 Vulkan、移植了游戏自身材质着色的原生渲染器取代对 Xbox 360 GPU 的模拟，模拟渲染器保留为后备。游戏文件来自使用者的光盘镜像；作者称原生渲染器尚处早期，且尚未完整测试整个游戏。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/skate3-recomp-case/)

- [**《神秘海域：内森·德雷克合集》原生 Windows 移植**](https://github.com/bc160201983/Uncharted-The-Nathan-Drake-Collection-PC-port)

  在 Windows 上原生运行 PS4 版《神秘海域：内森·德雷克合集》自身的 x86-64 可执行文件：由运行时提供 PS4 系统库，并以源自 shadPS4 的 Vulkan 渲染器执行 GPU 工作。该移植提供按游戏保存设置的启动器、分辨率补丁与现代超分辨率技术，其状态表报告三部游戏均可游玩，并列出未解决问题。这是兼容运行时移植而非反编译重建，结果仍为项目报告。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/uncharted-collection-pc-port-case/)

- [**TH095：东方文花帖 1.02a 的函数级重建**](https://github.com/N0zoM1z0/th095)

  为日版 Touhou 9.5：东方文花帖 1.02a 原可执行文件重建源码；只有使用固定版本 Visual C++ .NET 2003 构建、并与单一经哈希核验的目标进行可复现字节比较后，才认定函数级一致。整个程序也能编译链接为可游玩的 Windows i386 可执行文件，而 README 将可玩性、函数匹配与整个可执行文件一致性列为相互独立的状态。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/th095-reconstruction-case/)

- [**CorsixTH：Theme Hospital 的开源重新实现**](https://github.com/CorsixTH/CorsixTH)

  重新实现 Bullfrog 1997 年游戏 Theme Hospital 的引擎：游戏逻辑以 Lua 编写，图形、声音、影片和寻路由 C++ 处理，并建立在原游戏数据文件之上。README 报告完整战役已可通关，列出仍缺失的功能，并加入高分辨率和地图编辑器等扩展。它在原内容上重现游戏行为，而不是恢复 Bullfrog 的源码。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/corsixth-engine-case/)

- [**OpenRiseOfNations：原生 macOS 引擎重新实现**](https://github.com/ben-wright-1/OpenRiseOfNations)

  以原生 macOS 应用重新实现 Rise of Nations: Extended Edition 引擎，包含 Metal 渲染器、确定性模拟、电脑对手，以及兼容的 BigHugeScript 编译器与虚拟机；美术、地图、规则和脚本均从使用者自有的 Windows 版安装目录读取。项目依据对带调试符号的可执行文件进行 Ghidra 研究后撰写的子系统规范及 JavaScript 参考工具，在大量使用 Claude Code 的情况下编写 C++17 实现。该早期版本可游玩教程与场景，其逐位一致性检查仍为项目报告。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/openriseofnations-engine-case/)

- [**TH04：从源码重建东方幻想乡的四个 PC-98 程序**](https://github.com/N0zoM1z0/th04)

  为日版 PC-98 Touhou 4：东方幻想乡重建源码，并在 Wine 下用固定版本的 Borland 工具链重新构建全部四个 DOS 程序：MAIN.EXE、OP.EXE、MAINE.EXE 和 ZUN.COM。针对原二进制的函数认定，与在模拟器中对照原游戏比较输入、随机数、对象池和画面的回放分开记录。完整流程、原始时序与字节一致性目标仍未完成。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/th04-reconstruction-case/)

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

- [**decomp.me 协作匹配反编译平台**](https://decomp.me)

  面向匹配反编译的协作网站：其编译服务用选定平台的编译器编译候选源码，汇编目标汇编代码，并用 asm-differ 对比两个目标文件。对其 MIPS、PowerPC、ARM 和 SuperH 平台，m2c 可生成初步反编译代码。18 个平台定义涵盖 N64、PlayStation、PS2、PSP、GameCube/Wii、Wii U、DS、GBA、3DS、Switch、Saturn、Dreamcast 和 Xbox 360，以及 IRIX、Mac OS X、MS-DOS、Win32 和 Android x86。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/decomp-me/)

- [**splat 二进制拆分工具**](https://github.com/ethteck/splat)

  面向反编译与模组项目的二进制拆分工具：由 YAML 配置指定在何处、以何种方式把 N64 ROM 或 PSX、PS2、PSP 二进制切分为代码、数据和素材段。扫描阶段反汇编代码与数据，MIPS 部分由 spimdisasm 处理；拆分阶段写出文件以及用于重新构建输入文件的链接脚本。可编写自定义段类型扩展该流程。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/splat/)

- [**m2c 匹配反编译器**](https://github.com/matt-kempster/m2c)

  面向匹配反编译项目的反编译器，将 GNU as 格式的 32 位 MIPS、ARM、PowerPC 和 SuperH 汇编转换为 C 代码初稿，并部分支持 C++。目标由平台、编译器（IDO、GCC 或 MetroWerks CodeWarrior）和语言组成；上下文文件提供类型信息，还能推断未知的结构体字段并生成全局变量初始化代码。README 将它与 splat、asm-differ 和 decomp-permuter 并列使用，decomp.me 也调用它生成初步反编译结果。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/m2c/)

- [**decomp-toolkit GameCube/Wii 反编译工具包**](https://github.com/encounter/decomp-toolkit)

  面向 GameCube/Wii 匹配反编译的工具包：分析 DOL 和 REL 可执行文件，按项目配置将其拆分为可重定位目标文件，并为 CodeWarrior 链接器生成 ldscript.lcf，使反编译出的目标文件可逐个替换原有部分，同时将重新链接的二进制与原版核对。分析涵盖函数边界、Metrowerks/SDK 签名库、重定位、节区和数据对象，且无需汇编器即可直接写出目标文件。其命令行还可处理光盘镜像、归档、压缩格式、CodeWarrior 符号还原和 DWARF 转储。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/decomp-toolkit/)

- [**Cheat Engine MCP Bridge 进程内存分析桥接**](https://github.com/miscusi-peek/cheatengine-mcp-bridge)

  通过 Lua 桥接脚本和 Python MCP 服务器把 MCP 客户端连接到 Cheat Engine，使智能体能够检查用户在 Cheat Engine 下运行的进程：读取内存与扫描数值、解析指针链、剖析结构体、识别 RTTI 类名、反汇编、查找交叉引用，以及设置硬件或 DBVM 断点。另有工具组可写入内存、注入 DLL 或代码、自动化输入，并调用 Cheat Engine 的内核模式驱动。README 将其限定于教学和研究用途，并声明不支持多人游戏作弊或违反服务条款的行为。

  集成 · 独立 MCP · [使用条件与证据](https://awesomerea.org/zh/resources/cheatengine-mcp-bridge/)

- [**ido-static-recomp IRIX IDO 编译器静态重编译工具**](https://github.com/decompals/ido-static-recomp)

  将 SGI IDO 5.3 与 7.1 C 工具链中的 IRIX MIPS 程序（如 cc、cfe、uopt、ugen 和 as1）静态重编译为原生 Linux、macOS 和 Windows 可执行文件，使匹配式反编译项目能在现代主机上以原始编译器代码进行构建。它重编译的是编译器而非游戏，本身既不反编译也不转换游戏代码。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/ido-static-recomp/)

- [**PS2Recomp PlayStation 2 静态重编译器**](https://github.com/ran-j/PS2Recomp)

  实验性的静态重编译器，将 PlayStation 2 ELF 可执行文件中的 MIPS R5900 代码转换为 C++，并与随附的运行时链接。ps2xAnalyzer 或 Ghidra 导出脚本为每款游戏生成包含函数、存根、跳过项和指令补丁的 TOML 配置；ps2xRecomp 输出逐条指令的直译代码；ps2xRuntime 与 ps2xIOP 提供客户机内存、系统调用分发、带 HLE 回退的 IOP 模块执行，以及仅部分实现、大多为存根的 GS/VU 硬件。输出不是反编译源码，让游戏真正运行仍需针对每款游戏进行移植。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/ps2recomp/)

- [**Xenosaga I 反编译兼容性工具包**](https://github.com/LinuxJessi/decomp-compat-kit)

  在匹配反编译项目自身的构建之外进行检查：用未打补丁的原版 ee-gcc 2.96 及汇编器重新编译其 C 代码，再逐函数与原程序逐字节比较，并按可能的工具链原因对每处差异分类。配套脚本可将 ELF 符号表导出为 CSV，并转换为 splat 符号文件。默认配置针对 Xenosaga Episode I；README 称方法可推广，默认配置则不能。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/decomp-compat-kit/)

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

- [**Screen Studio：作者报告的 REA 自动缩放规则研究**](https://x.com/i/article/2109834677343432704)

  作者报告借助 REA 梳理 Screen Studio 的 Electron 安装包，在 Claude Code 协助下从混淆代码中读出六条自动缩放与光标规则，再让 Claude Code 依据这些规则编写独立的录屏和渲染程序。文章介绍了所用命令、证据、光标对齐检查以及复刻版的不足；复刻版和解出的代码均未公开。

  案例 · 混合工具流程 · [使用条件与证据](https://awesomerea.org/zh/resources/screen-studio-auto-zoom-case/)

- [**Claude Code 背景动画实验室：基于 REA 调查的桌面动画重新实现**](https://github.com/Henry-fan88/claude-code-background)

  将 Claude 桌面应用中 Claude Code“新会话”界面的字符风场背景，重新实现为可离线运行的 WebGL2 页面，并附带 38 个滑块的控制面板。作者报告先用 REA 对桌面外壳及其远程网页包进行静态调查，再以新编写的渲染器复用恢复出的时序与布局参数。它与原效果的视觉语言和交互方式相近，但不是逐像素一致的提取。

  案例 · 混合工具流程 · [使用条件与证据](https://awesomerea.org/zh/resources/claude-code-background-lab-case/)

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

- [**Visor：独立的 Ray-Ban Meta 眼镜客户端**](https://github.com/macedonga/visor)

  实现可替代 Meta AI 配套应用的 Android 客户端：直接使用 Ray-Ban Meta 眼镜自有的蓝牙与 Wi-Fi Direct 协议，导入媒体、提供设置，并用用户选择的模型回应“Hey Meta”。项目 wiki 记录了链路分层、加密、服务及 Meta 端的所有权流程，并列出 153 个未解问题。项目以实机试用代替测试套件，因此所述型号和固件之外的行为仍未经验证。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/visor-ray-ban-meta-client-case/)

- [**wine-uwp：在修改版 Wine 上运行打包的 Windows 商店应用**](https://github.com/designgears/wine-uwp)

  扩展 Wine 11.17，使已签名的 MSIX 商店应用（主要目标为 Shapr3D）无需源码或符号即可在 Linux 上安装运行。约 49,000 行改动新增了 DirectComposition 实现、合成交换链和应用模型宿主；微软自己的 XAML 与应用模型 DLL 则在使用者机器上从 Windows 11 镜像中提取后原样运行。作者称大部分逆向工程和代码由 Claude 完成；各应用支持程度不一，由项目回归测试检查。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/wine-uwp-store-apps-case/)

- [**RKD Telemetry Extractor：解读 Race-Keeper 赛道日录制数据**](https://github.com/sam-dumont/rkd-telemetry-extractor)

  记录 Race-Keeper “Instant Video” 记录仪所写的专有 .rkd 遥测格式（随附播放器仅支持 Windows），并以结果一致的 Python 与 Go 解析器把 GPS 和 IMU 通道导出为 Telemetry Overlay CSV 与 GPX。作者称十六进制分析和假设检验由 Claude Code 协助完成，并以已知车辆编号、赛道位置和车速作为锚点。字段含义依据作者自有录制数据的物理交叉核对得出，若干记录类型仍未完全解读。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/rkd-telemetry-extractor-case/)

- [**Elgato HDR：为 Elgato 4K X 的 10 位模式提供用户态采集通路**](https://github.com/talkaboutdesign/elgato-hdr)

  一款原生 macOS 应用，用于获取 Elgato 4K X 采集卡的 10 位 P010 视频模式；项目称苹果内置的摄像头驱动不会向应用开放该模式。一个 root 权限辅助程序卸下该驱动，通过 libusb 直接执行采集卡的 USB 视频类（UVC）串流，为 Metal HDR 预览、HDR10 录制和编辑器提供画面。延迟数据和设备覆盖范围仍为作者报告。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/elgato-hdr-uvc-capture-case/)

- [**LGwebOS-menubar：LG webOS 电视的原生 macOS 遥控器**](https://github.com/gabrielgreco1/LGwebOS-menubar)

  一款原生 macOS 菜单栏应用，通过 LG webOS 电视在局域网内的加密 WebSocket 接口完成配对，可启动应用、切换输入源、调节音量和画面设置、发送指针输入并投放所选媒体。项目称 webOS 协议行为参考了公开的 Connect SDK，并沿用 PyWebOSTV 的注册清单。测试仅覆盖一台 webOS 5.0 电视。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/lgwebos-menubar-remote-case/)

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

- [**Rizin 逆向工程框架**](https://github.com/rizinorg/rizin)

  源自 radare2 分支的命令行逆向工程框架。rizin 交互环境可分析和反汇编二进制、调试程序，并可用作可脚本化的十六进制编辑器；rz-\* 系列工具提供二进制格式信息、汇编、差异比较、哈希、模式搜索和 FLIRT 签名等功能。README 列出数十种架构、字节码格式和文件格式，从 ELF、PE、Mach-O 到 dyld 缓存和 BIOS/UEFI 镜像；可通过 rzpipe 用 Python、Rust、Go 等语言编写脚本。Cutter 是基于它的独立图形界面。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/rizin/)

- [**Decompiler Explorer 反编译器对比服务**](https://dogbolt.org)

  位于 dogbolt.org 的网络服务：将上传的单个小型可执行文件交给多款反编译器处理，并排显示它们输出的类 C 代码，自称“反向的 Compiler Explorer”。所固定版本的源码包含 angr、Binary Ninja、Boomerang、dewolf、Ghidra、Hex-Rays、Kuna、REC Studio、Reko、Relyze、RetDec、rev.ng 和 Snowman 的运行器，便于比较不同反编译器如何呈现同一段代码。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/decompiler-explorer/)

- [**pwndbg GDB/LLDB 调试增强插件**](https://github.com/pwndbg/pwndbg)

  可加载到 GDB 中、或作为 LLDB 外层 REPL 运行的 Python 插件，使运行中程序的状态更易检查。每次停下时都会打印寄存器、栈、调用帧和带注释的反汇编等上下文，并递归解引用指针；命令涵盖内存映射、搜索、内存链式查看、堆分配器和 Go 值，还借助 Capstone/Unicorn 模拟执行指令，并可与 IDA、Binary Ninja、Ghidra 和 angr-management 反编译器集成。README 列出 Linux ELF、macOS Mach-O、QEMU 用户态／系统态以及嵌入式 Cortex-M 或 RISC-V/32 调试场景。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/pwndbg/)

- [**DynamoRIO 动态二进制插桩框架**](https://github.com/DynamoRIO/dynamorio)

  运行时代码操作系统，用于构建在未修改程序运行期间观察或变换其任意部分的动态工具。其 API 与 IA-32/AMD64/ARM/AArch64 指令操作库允许任意修改应用指令，而不仅限于插入回调。发布包附带 drcov 代码覆盖率、drltrace 库调用跟踪、drstrace Windows 系统调用跟踪、drmemtrace 指令与内存访问跟踪以及 drdisas 反汇编器等工具。它是用于构建插桩工具的框架，与 Frida 对运行中进程编写脚本的方式不同。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/dynamorio/)

<a id="firmware"></a>
### Firmware and Hardware · 固件与硬件

[↑ 返回目录](#目录)

#### 案例

- [**ThinkPad IMX471：为 Linux 恢复相机调校信息**](https://github.com/cschalle/mipi-fixes-x1-aura)

  从 Intel Windows 驱动包中恢复选定的相机调校结构，用于修复一个 ThinkPad 型号在 Linux 下的图像采集。公开的 CPFF／AIQB 解析器、内核补丁及 libcamera 修改，配有作者报告的 Claude 辅助调查和有限范围的前后测量。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/thinkpad-imx471-camera-case/)

- [**flipper-telink：Tuya Zigbee 遥控器的替换固件**](https://github.com/ngxson/flipper-telink)

  一款 Flipper Zero 应用，以位操作驱动 Telink 的 SWire 调试接口，用于转储并重刷 TLSR825x Zigbee 设备；仓库还附有对转储固件的静态分析笔记，以及为其中两款设备全新编写的固件。针对 Tuya TS0044/TS0046 场景遥控器，笔记将原厂约 500 ms 的单击延迟追溯到双击判定窗口；替换固件取消该窗口，同时向 Zigbee2MQTT 呈现原厂型号标识。最新 Zigbee 版本的配对、动作及电量上报被标注为尚未验证。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/flipper-telink-tuya-remote-firmware-case/)

- [**Supermodel：Real3D Pro-1000 图像生成器的初步模拟**](https://github.com/trzy/Supermodel)

  为 Supermodel 街机模拟器加入对 Real3D Pro-1000 的模拟。Pro-1000 是通过 SCSI 连接主机的图像生成器，世嘉 Model 3 的图形硬件即由其衍生。该实现可启动使用者自备的、来自 SDK 光盘的 Pro-1000 固件，模拟板上的中断、JTAG 与 UART 硬件，并在控制台中提供固件内置的监控程序。目前尚无任何画面输出，与 SCSI 主机的通信也尚未实现。

  案例 · 独立重建 · [使用条件与证据](https://awesomerea.org/zh/resources/supermodel-real3d-pro1000-emulation-case/)

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

- [**ipsw Apple 固件研究工具包**](https://github.com/blacktop/ipsw)

  面向 Apple 固件研究与逆向工程的命令行工具包。可下载并解包 IPSW、OTA 和 KDK 并比较不同构建；检查 Mach-O 的加载命令、符号、签名和权限，并反汇编 ARM64 代码；在 dyld 共享缓存中查找符号和交叉引用、提取 dylib、导出 Objective-C 头文件并查看 Swift 元数据；提取 KEXT 并比较 kernelcache；还能解析 IMG4、解密 AEA 归档，以及检查 iBoot 和协处理器固件。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/ipsw/)

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

- [**rtl\_433 ISM 频段设备无线协议解码器**](https://github.com/merbanan/rtl_433)

  接收并解码 ISM 频段设备（如气象传感器、遥控器、门铃和报警传感器）的无线传输，可使用 RTL-SDR 或 SoapySDR 接收机，也可读取录制的 I/Q 文件，并以 JSON、CSV、MQTT 等格式输出解码字段。对内置解码器无法识别的信号，脉冲分析器会报告 OOK/FSK 时序，并给出灵活 -X 解码器的提示，用于将帧切分为比特；按其分析指南，把这些比特对应到具体数值仍需分析者依据已知读数完成。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/rtl-433/)

- [**Blackbox Protobuf 无定义 Protobuf 解码与重编码工具**](https://github.com/nccgroup/blackboxprotobuf)

  NCC Group 推出的工具集，可在没有对应 .proto 定义的情况下解码并重新编码 Protocol Buffers 报文。解码器返回报文数据，以及根据线路类型尽力推测生成、可编辑的类型定义；分析者可以为字段命名、修正类型并重新编码修改后的报文，这是 protoc --decode\_raw 做不到的。它提供 Python 库及 bbpb 命令行工具、基于 Jython 的 Burp Suite 扩展和 mitmproxy 插件，README 说明它最初用于在移动应用渗透测试中修改报文。

  工具 · [使用条件与证据](https://awesomerea.org/zh/resources/blackbox-protobuf/)

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

- [**Hermes Agent 的 REA 插件**](https://github.com/NousResearch/hermes-official-plugins/tree/main/rea)

  Nous Research 在 Hermes Agent 官方插件库中发布的 REA 插件包。一次目录安装即可注册 REA 的 MCP 服务（固定为 rea-agents 6.4.0，经 npx 以 stdio 启动），并附带为 Hermes 改编的 REA 工作流技能和独立的崩溃分诊技能。约 170 个 REA 工具通过 Hermes 的按需工具检索提供；改编技能要求在运行程序、驱动应用或改动已连接 Android 设备的工具前先征得同意。

  集成 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/hermes-rea-plugin/)

- [**crashlens 崩溃分诊工具**](https://github.com/mingleiw/crashlens)

  崩溃分诊工具，将 Linux 核心转储、运行时 panic、异常堆栈和 sanitizer 报告整理为 Markdown 缺陷报告，指出崩溃类型、首个用户代码帧和稳定签名。核心转储分析通过 REA 命令行读取崩溃记录与二进制布局，并可调用 REA 的 Ghidra 引擎为无符号函数生成伪代码；附带的 Claude Code 插件包含技能与只读 MCP 工具。它是围绕 REA 的调试集成，不是重建案例，诊断准确性仍为作者报告。

  集成 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/crashlens-rea-crash-triage/)

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

- [**ReVa 面向大模型工具设计的 Ghidra MCP 扩展**](https://github.com/cyberkaida/reverse-engineering-assistant)

  在 Ghidra 内运行 MCP 服务器的 Ghidra 扩展，为智能体提供附带命名空间与交叉引用上下文的反编译、符号、字符串、数据类型、结构体与调用图工具，以及程序比对、重命名和 PyGhidra 脚本执行。其 README 将项目的特点归于面向大模型使用的工具设计：提供许多小工具，其模式在给定结构之外也能容忍其他输入，把可纠正的错误反馈给模型，并返回附带相关信息链接的简短片段。助手模式可让多个客户端同时连接已打开的 Ghidra 项目；无界面模式则由 ReVa 自行启动 Ghidra，项目仅在会话期间存在。

  集成 · 独立 MCP · [使用条件与证据](https://awesomerea.org/zh/resources/reva-ghidra-mcp/)

- [**x64dbg-MCP Server 调试器 MCP 插件**](https://github.com/duty1g/x64dbg-mcp-server)

  以 Zig 编写、同时支持 x32dbg 与 x64dbg 的原生 x64dbg 插件，在调试器内部通过 streamable HTTP 和 SSE 提供 MCP 端点。智能体可以加载或附加进程，设置软件、硬件、内存及条件断点，单步与跟踪执行，读取寄存器、调用栈、线程、内存映射、导入表、字符串和交叉引用，并执行任意 x64dbg 命令。随附的 SKILL.md 指南要求智能体在每次操作前先确认调试器状态。

  集成 · 独立 MCP · [使用条件与证据](https://awesomerea.org/zh/resources/x64dbg-mcp-server/)

- [**mcp-windbg WinDbg 调试 MCP 服务器**](https://github.com/svnscha/mcp-windbg)

  由社区独立开发的 MCP 服务器，以无界面方式运行微软的 cdb.exe 和 kd.exe，使智能体能够打开并初步分析用户态与内核崩溃转储，连接 cdb 远程调试服务器和 KD 内核目标，并在可分别寻址的会话中执行任意调试器命令。其 README 建议希望在 WinDbg 内使用 AI 的用户选择微软官方的 WinDbg MCP，并把本项目定位为面向其他 MCP 客户端、远程 HTTP 使用和批量转储分析的替代方案；项目自称只是执行真实调试器命令的封装，而非自动修复工具。

  集成 · 独立 MCP · [使用条件与证据](https://awesomerea.org/zh/resources/mcp-windbg/)

- [**Wireshark MCP 基于 tshark 的协议解析服务器**](https://github.com/bx33661/Wireshark-MCP)

  封装 tshark 及可选的其他 Wireshark 命令行工具的 MCP 服务器，使智能体能借助 Wireshark 的解析器查询已保存的抓包文件：数据包列表与详情、流追踪、任意字段提取、协议层级与会话统计、针对非标准端口的 decode-as 规则、协议首选项、使用用户提供的密钥进行 TLS 与 WPA 解密，以及一个为 Modbus、S7comm、MQTT、Zigbee、BLE 等 25 种协议套用预设字段和过滤器的工具。解析类工具之外，另有安全启发式检测、实时抓包和抓包文件编辑等独立工具。

  集成 · 独立 MCP · [使用条件与证据](https://awesomerea.org/zh/resources/wireshark-mcp/)

- [**BINNY 逆向分析智能体框架**](https://github.com/openbin-ai/binny)

  OpenBin 推出的开源终端智能体框架，让使用者自选的托管或本地模型处理二进制分析数据。它从 OpenBin 或 OpenAPK 项目、或本地 Ghidra 容器的分析结果中读取反编译函数、字符串、导入表和数据，按分诊、调查与起草流程工作，并保存恶意软件分析或漏洞研究报告草稿供人工审阅。它是输出草稿的分析框架，而非重建项目。

  集成 · 独立智能体 · [使用条件与证据](https://awesomerea.org/zh/resources/binny-agent-harness/)

- [**decomp.wtf 智能体反编译工具**](https://github.com/i12bp8/decomp.wtf)

  一款已停止开发的本地应用与 MCP 服务，把用户自有主机游戏的函数逐个交给 AI 编程智能体，用该游戏当年的编译器编译每次提交的 C 代码，只有链接后的结果与原始字节一致才算通过。它可从 ROM 或光盘镜像新建项目，也可在 decomp.dev 所列公开反编译项目的分叉中工作，由 objdiff 判定结果。其 2026 年 10 月 15 日的最后一次提交宣布停止开发，理由是反编译社区的反对；代码仍以 MIT 许可保留，但不再修复或发布新版本。

  集成 · 独立智能体 · [使用条件与证据](https://awesomerea.org/zh/resources/decomp-wtf-agent-decompilation/)

- [**Claude Intercept 流量捕获分析工具**](https://github.com/whaesemeyer/claude-intercept)

  本地中间人代理与控制面板，捕获使用者自有电脑和设备的 HTTP/S 流量，存入 SQLite，并通过 /intercept 技能和命令行交给 Claude Code。API 文档、流量摘要等导出模式可用于调查请求模式与未公开接口。这是面向智能体、用于授权测试的抓包工具，不是重建案例，也未确立与 REA 的关联。

  集成 · 独立智能体 · [使用条件与证据](https://awesomerea.org/zh/resources/claude-intercept-traffic-capture/)

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

- [**Reversed with AI：AI 辅助逆向项目目录**](https://reversedwithai.com/)

  经人工审核的网站目录，收录游戏、固件、文件格式、API 与协议、应用及旧软件领域的 AI 辅助逆向项目。每个条目链接一手来源，记录作者报告的模型、工具、耗时、费用与结果，并标注源码公开、复现步骤、真实硬件测试和第三方确认四项检查。

  合集 · [使用条件与证据](https://awesomerea.org/zh/resources/reversed-with-ai-directory/)

- [**awesome-unofficial-pc-ports 非官方 PC 移植清单**](https://github.com/Sebastrion/awesome-unofficial-pc-ports)

  以单个 README 维护的非官方 PC 移植指南，收录基于反编译或重编译、且便于玩家安装的主机游戏移植。76 个游戏条目按 Nintendo、PlayStation、Xbox、SEGA、独立游戏和 J2ME 分组，每项推荐一个移植版并附简短安装说明，常同时链接所依据的反编译项目和其他移植版；“实用工具”部分另列两个重编译启动器。

  合集 · [使用条件与证据](https://awesomerea.org/zh/resources/awesome-unofficial-pc-ports/)

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

- [**通过 Ghidra 分析 MIPS ELF**](https://github.com/morluto/rea/blob/main/docs/ghidra-mips.md)

  说明 REA 通过 Ghidra 分析 MIPS ELF 可执行文件、可重定位目标文件与 MIPS16 共享镜像的流程，包括为缺少 ABI 记录的旧式固件可执行文件固定 32 位语言，以免 Ghidra 将其按 64 位导入。准入以文件头声明和 ABI 记录为界；验证将项目自有的测试样本与独立的 readelf 输出对照，而不执行或重新托管固件。

  文档 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-ghidra-mips-guide/)

- [**通过 Ghidra 静态分析 PSP ELF**](https://github.com/morluto/rea/blob/main/docs/ghidra-psp.md)

  说明 REA 针对静态 PSP ELF 可执行文件的受限 Ghidra 配置：Allegrex 指令、PSP 加载与调用约定交由使用者安装的 ghidra-allegrex 扩展处理，同时沿用 REA 的命令行、MCP、证据与快照流程。它仅在 Linux x64 上接受一种 PSPSDK 文件头与 ABI 声明，并在自行构建的测试样本上验证选定的静态事实，不涉及商业游戏或 PRX 模块。

  文档 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-ghidra-psp-guide/)

- [**借助 Ghidra 恢复 NativeAOT 元数据**](https://github.com/morluto/rea/blob/main/docs/ghidra-nativeaot.md)

  在 REA 的 Ghidra 分析中，从 x64 PE 可执行文件恢复 .NET 8 NativeAOT 元数据：通过内置只读解析器或可选的无界面适配器（会为 Ghidra 数据库添加注释），从 RTR 9.1 数据中取得 MethodTable 关系、虚表槽位与冻结字符串。生成的名称、推断的原型和恢复的原生伪代码，与未知的原始 C# 名称、字段和源码明确区分。

  文档 · REA · [使用条件与证据](https://awesomerea.org/zh/resources/rea-ghidra-nativeaot-guide/)

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

- [**寻找 Jingle Town：在没有调试符号时调试 N64 游戏**](https://blog.chrislewis.au/finding-jingle-town-debugging-an-n64-game-without-symbols/)

  Snowboard Kids 2 反编译项目的一篇操作说明：在一致性构建仍无法加入调试信息时，把 gdb-multiarch 接到 Ares 模拟器上。文中按 ELF 符号名在函数处设断点，再手动读取结构体中的一个字节，检验它是否决定加载哪个关卡 overlay。这是在运行时检验反编译假设的简短方法记录，而非重建成果。

  学习资源 · [使用条件与证据](https://awesomerea.org/zh/resources/finding-jingle-town-n64-debugging/)

- [**JPCERT/CC：攻击服务器上的 APK 解析与 API 探测**](https://blogs.jpcert.or.jp/ja/2026/10/web_api_attacks.html)

  JPCERT/CC 于 2026 年 10 月 15 日发布的博客文章，调查日本国内一系列不正当访问事件背后的攻击基础设施。文章报告攻击者利用 AI 扫描已知漏洞并经由 API 发动攻击，攻击服务器上存有 APK 文件、与 jadx 和 Blutter 相关的文件、APK 解包目录，以及用于探测应用 API 的 SSRF 验证脚本。这是防御方对所观察到的攻击者工具的记述并附缓解建议，而非公开的 AI 辅助分析方法或可复现的工作流程。

  学习资源 · [使用条件与证据](https://awesomerea.org/zh/resources/jpcert-apk-api-attack-infrastructure-report/)
<!-- END GENERATED CATALOG -->

<!-- BEGIN GENERATED PAPERS -->
<a id="papers"></a>
## 论文

**83 篇论文**，按主题分组，组内按年份从新到旧排列。每项均标明发表场所与状态，中文标题为译名。

[浏览论文目录](https://awesomerea.org/zh/papers/) · [完整书目 JSON](data/papers.json) · [推荐论文](https://github.com/reacher-z/Awesome-REA/issues/new?template=paper.yml)

**按主题**

- [智能体评测](#papers-agent-evaluation) (8) · [反编译](#papers-decompilation) (31) · [网站](#papers-website-reconstruction) (15)
- [游戏](#papers-game-reconstruction) (6) · [应用](#papers-app-reconstruction) (7) · [固件](#papers-firmware-analysis) (6)
- [协议](#papers-protocol-analysis) (10)

展开“范围与发表信息”查看完整研究边界。部分论文也出现在精选资源目录中，两者数量不可相加。

<a id="papers-agent-evaluation"></a>
### 逆向工程智能体评测

[↑ 论文主题](#papers) · [目录](#目录)

- [**人类与机器：AI 智能体在软件逆向工程中的对比研究**](https://arxiv.org/abs/2610.14960)

  比较人类与 LLM 智能体在相同静态逆向挑战中的理解和导航方式，并研究二进制表示如何占用上下文窗口。

  arXiv 2026 · 预印本 · [PDF](https://arxiv.org/pdf/2610.14960) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-humans-machines-sre/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 理解能力仅在两个紧凑挑战上评分；另一个包含 4,000 个二进制文件的实验测量上下文容量，并非解题准确率。接口为不含动态执行的静态 IDA/MCP，模型曾接触挑战源码的可能性仍是作者承认的有效性威胁。

  **作者:** Samuele Doria 等

  </details>

- [**智能体网络安全的下一项挑战：真实场景且无训练数据污染的逆向工程基准**](https://arxiv.org/abs/2608.11469)

  提出 SRE-Bench，使用私有编写的程序及带保护机制的二进制变体，研究智能体恢复程序语义的能力，并减少训练数据污染。

  arXiv 2026 · 预印本 · [PDF](https://arxiv.org/pdf/2608.11469) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-sre-bench/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 修订版研究报告 19 个程序、262 个二进制实例和 1,572 个评分任务。二进制与任务实例未公开发布，只能通过评估服务访问。污染控制是作者的方法论主张，并非独立保证。

  **作者:** Jeremy Spence 等

  </details>

- [**CrackMeBench：面向智能体的二进制逆向工程基准**](https://arxiv.org/abs/2605.10597)

  用可执行程序判定结果的 CrackMe 任务评估智能体：从二进制推断验证逻辑，提交可被接受的输入或产物，并记录工具使用、耗时与评分尝试。

  arXiv 2026 · 预印本 · [PDF](https://arxiv.org/pdf/2605.10597) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-crackmebench/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** v0 研究使用 12 个生成任务和 8 个公开校准任务，限定 Linux x86-64 ELF、Shell 接口和五分钟预算。紧凑的教学任务不能证明大型应用上的表现。未确认论文直接关联的公开研究产物 URL。

  **作者:** Isaac David 等

  </details>

- [**迈向抗 LLM 的软件保护：CTF 逆向工程中的智能体失败模式**](https://www.ndss-symposium.org/ndss-paper/auto-draft-657/)

  让 Claude Code、Codex CLI 与 ChatGPT-5.2 Pro 求解从 2025 年 15 场国际 CTF 赛事中选出的 24 道 crackme 类题目，并将失败归因到“观察—理解—计划”循环的各阶段，以及隐藏、复杂化与误导三类保护效果。作者从失败日志中归纳出四类反复出现的弱点：训练偏差、过度信任观察结果、上下文限制和计划固守。他们还在移除反编译器后重新运行两个命令行智能体，并将结果与赛时解题率对比。

  Workshop on Binary Analysis Research (BAR) 2026 · 会议论文 · [PDF](https://www.ndss-symposium.org/wp-content/uploads/bar2026-58.pdf) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-llm-resistant-protection/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 研究覆盖 24 道可在本地求解的 Linux x86-64 ELF crackme 题目和三个商用智能体（命令行工具使用 Claude Opus 4.5 与 GPT-5.1-Codex-Max，ChatGPT 所用模型未公开），于 2025 年 12 月在允许联网的条件下评测；查阅公开题解的运行已被排除。这些二进制相比真实软件规模较小，恶意软件分析与漏洞发现不在范围内。每种配置最多尝试三次，成功即停止，作者承认这种估计噪声较大；成功指输出正确 flag 或找到被程序接受的输入。弱点标签来自两名评估者对日志的定性分析，描述的是这些运行，并非 LLM 智能体的普遍属性。ChatGPT-5.2 Pro 在无法控制的网页沙箱中运行，未纳入反编译器对比。解题率按至少解出一题的队伍计算，其中六题没有数据，参赛队伍也可能借助 LLM。训练数据泄露仍是有效性威胁；论文未公开其整理的题目集、运行日志或代码。

  **作者:** Ryutaro Nishizaka 等

  </details>

- [**ProgramBench：语言模型能否从零重建程序？**](https://arxiv.org/abs/2605.03546)

  通过 200 项任务评估黑盒程序重建：智能体运行可执行文件进行探测并阅读文档，再独立实现代码库，由生成的测试检查其行为。

  NeurIPS 2026 · 已接收 · [PDF](https://arxiv.org/pdf/2605.03546v1) · [代码](https://github.com/facebookresearch/ProgramBench) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-programbench/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 推理阶段禁止检查二进制内容、反编译和访问互联网。通过有限测试不能证明完整行为等价或恢复了原始源码。实时榜单中的后续运行结果应与所审阅 arXiv 版本的结果区分。

  **作者:** John Yang 等

  </details>

- [**解构协同：软件逆向工程中人类与 LLM 协作的实证研究**](https://www.ndss-symposium.org/ndss-paper/decompiling-the-synergy-an-empirical-study-of-human-llm-teaming-in-software-reverse-engineering/)

  研究人类分析人员在静态软件逆向工程中如何借助 LLM 辅助开展工作。作者依据对 153 名从业者的问卷，在带插桩的 IDA Pro 插件中实现六项 LLM 功能；随后 48 名参与者（自报新手与专家各 24 名）分析两个 CTF 风格的二进制程序，其中一道随机指定的题目启用这些功能。基于评分后的解题报告、交互日志和问卷，作者报告 18 项发现：新手的理解程度提升约 98%，达到专家水平，而专家收益甚微；已知算法函数的分诊速度最高提升 2.4 倍，产物恢复量至少增加 66%；同时也出现了有害的幻觉。

  NDSS 2026 · 会议论文 · [PDF](https://www.ndss-symposium.org/wp-content/uploads/2026-f380-paper.pdf) · [代码](https://github.com/mahaloz/dec-synergy-study) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-decompiling-synergy/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 这是一项关于 LLM 辅助分析的人类研究，并非对自主智能体或 LLM 反编译准确率的评测。研究使用两个未经混淆、各含 26 个函数的 C 语言题目，仅允许在 IDA Pro 中进行静态分析（不能使用调试器或符号执行），提示词由研究团队编写，模型可在 GPT-4o、GPT-4o-Mini、GPT-4-Turbo、Claude-3-5-Sonnet 与 Gemini-Pro 中选择。2024–2025 年的实验在 51 名参与者中保留 48 名；专业水平为自报，理解程度是由两名研究人员按评分细则给解题报告打出的分数。LLM 直接生成的产物与理解程度提升无相关性；三名 LLM 用户报告了一个由 LLM 提示、实际并不存在的缓冲区溢出，而“查找漏洞”功能与理解得分呈负相关。个人观察记录、解题报告和问卷回答均不公开，也不接受申请；汇总数据仅可申请获取。

  **作者:** Zion Leonahenahe Basque 等

  </details>

- [**CREBench：评估大语言模型的密码二进制逆向工程能力**](https://openreview.net/forum?id=tLYdf8hWJB)

  通过 432 个受控挑战，评估密码二进制逆向中的算法识别、密钥或 IV 提取、包装层重建及标志恢复。

  COLM 2026 · 会议论文 · [PDF](https://arxiv.org/pdf/2604.03750v2) · [代码](https://github.com/wangyu-ovo/CREBench) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-crebench/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 语料组合 48 种算法、三类不安全密钥使用场景和三个难度等级。它不覆盖 Tigress、O-LLVM 等专业混淆器，结果不应推广到任意重度保护的二进制文件。

  **作者:** Baicheng Chen 等

  </details>

- [**EnIGMA：交互式工具显著帮助语言模型智能体发现安全漏洞**](https://proceedings.mlr.press/v267/abramovich25a.html)

  EnIGMA 在 SWE-agent 基础上面向 CTF 题目进行扩展：交互式智能体工具可在多轮之间保持 gdb 调试会话或 pwntools 服务器连接，另有反编译与反汇编命令、用于长输出的语言模型摘要器，以及按题目类别编写的示例和指导。论文使用四种语言模型，在 NYU CTF、InterCode-CTF、Cybench 及作者收集的 HackTheBox 题集共 390 道题目上评测；还对工具、摘要器和示例做消融实验，并分析解答泄露和“自言自语”（soliloquizing）现象，即模型不与环境交互而自行编写观察结果。

  ICML 2025 · 会议论文 · [PDF](https://raw.githubusercontent.com/mlresearch/v267/main/assets/abramovich25a/abramovich25a.pdf) · [代码](https://github.com/SWE-agent/SWE-agent/tree/v0.7) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-enigma/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 各基准混合了密码学、取证、二进制漏洞利用、逆向工程、Web 与杂项任务（390 道题中有 104 道为逆向工程），因此 NYU CTF 上 13.5% 等总体解题率并不等于逆向工程准确率。分类别表格报告，使用 Claude 3.5 Sonnet 时，NYU CTF 中 51 道逆向工程题的解题率为 17.65%。结果采用 pass<span>@</span>1，每道题成本上限为 3 美元，使用 2024 年的模型（GPT-4 Turbo、GPT-4o、Claude 3.5 Sonnet 与 LLaMA 3.1 405B Instruct）；NYU CTF 基线对比采用 pass<span>@</span>5。许多题目存在公开题解，作者对泄露和“自言自语”的度量属于启发式方法；在 21 道较晚发布的 CSAW 2024 题目上，最佳配置解出 2 道。解出 CTF 题目表明获得了 flag，而非恢复了程序结构或源码。

  **作者:** Talor Abramovich 等

  </details>

<a id="papers-decompilation"></a>
### 反编译与符号恢复

[↑ 论文主题](#papers) · [目录](#目录)

- [**SoK：人工智能增强的二进制逆向工程**](https://arxiv.org/abs/2606.17398)

  一篇系统化知识综述，梳理机器学习、大语言模型与智能体方法在二进制逆向中的应用。第二版通过关键词检索 11 个安全、软件工程与人工智能会议并辅以引文滚雪球，收集 2015 年以来的 246 篇论文，按推断任务归入 22 个领域：从代码边界检测，到函数名、类型与结构体布局恢复，再到代码相似性、恶意软件与漏洞分析以及反编译。其分类体系通过二进制派生的分析产物，把传统的初筛、静态分析、动态分析与安全测试同人工智能流程联系起来，并总结出 12 条洞见及若干开放方向，例如与二进制对齐的语义真值和目标驱动的智能体逆向。

  arXiv 2026 · 预印本 · [PDF](https://arxiv.org/pdf/2606.17398v2) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-sok-ai-binary-reversing/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 这是一篇文献系统化综述，不包含新的实验、基准或工具；它对已报告的结果进行分类和总结，并未复现。语料涵盖截至 2026 年 7 月 31 日可获得的论文，引用量门槛从 2015—2016 年论文的 12 次逐步降至 2025—2026 年论文的 2 次，排除推断时需要源码的方法，也不包括 Android 与解释型语言字节码。各阶段的详细表格基于 88 项顶级会议研究，而非完整语料。它是未注明发表场所的 arXiv 预印本，本条目不声称其经过同行评审。其引用的论文并不因此纳入本合集，每篇都需要单独审阅。

  **作者:** Yujeong Kwon 等

  </details>

- [**SK2Decompile：从骨架到皮肤的大语言模型两阶段二进制反编译**](https://proceedings.iclr.cc/paper_files/paper/2026/hash/9132583dd869acb0cafeb0ed25eb031a-Abstract-Conference.html)

  将 LLM 反编译分为两个阶段：结构恢复模型把反编译器伪代码转换为保留控制流和数据结构、但不含标识符的中间表示，并以编译器反馈作为强化学习奖励；标识符命名模型再以语义相似度为奖励恢复名称。作者报告，其在 HumanEval 上的平均可重新执行率比 GPT-5-mini 高 21.6%，在 GitHub2025 上的平均 R2I 比 Idioms 提升 29.4%。

  ICLR 2026 · 会议论文 · [PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/9132583dd869acb0cafeb0ed25eb031a-Paper-Conference.pdf) · [代码](https://github.com/albertan017/LLM4Decompile/tree/85b364bf093eb2ee4f3687cfe38a203fca89f23e/sk2decompile) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-sk2decompile/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 训练和主要评测均使用函数级 C 代码，以 GCC 和 Clang 在 -O0 至 -O3 下编译为 x86-64 Linux 二进制，并以 IDA Pro 伪代码作为模型输入。可重新执行率仅在 HumanEval 和 MBPP 上测量；ExeBench 与 GitHub2025 采用 R2I 可读性指标和 GPT-5-mini 评审。附录实验扩展到 BringUpBench 项目、macOS arm64 与 Windows MSVC 构建以及 Obfuscator-LLVM，但模型仅以 C 代码训练，论文预计遇到 C++ 模板等没有 C 对应物的语言特性时效果会下降。

  **作者:** Hanzhuo Tan 等

  </details>

- [**Idioms：以明确定义的类型显著增强局部神经反编译的简单有效框架**](https://www.ndss-symposium.org/ndss-paper/idioms-a-simple-and-effective-framework-for-turbo-charging-local-neural-decompilation-with-well-defined-types/)

  Idioms 微调代码语言模型，把单个目标函数的 Hex-Rays 输出转换为预测的原始 C 代码，并同时给出其中使用的用户自定义结构体、联合体和类型别名定义。输入可按调用图广度优先顺序附带相邻的反编译函数，使分散在调用者与被调用者中的类型线索能够提供给模型。作者还构建了 Realtype 数据集，包含来自已编译开源 C 仓库的 157,163 个函数及完整类型定义。其基于 CodeGemma-7b 的模型在 ExeBench 上有 54.4% 的函数通过单元测试，LLM4Decompile 为 46.3%，Nova 为 37.5%；在 Realtype 上的得分至少高出 95%。

  NDSS 2026 · 会议论文 · [PDF](https://www.ndss-symposium.org/wp-content/uploads/2026-f795-paper.pdf) · [代码](https://github.com/squaresLab/idioms) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-idioms/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 这是局部、函数级的神经反编译：每次预测只覆盖一个目标函数及其类型定义，而非可编译的完整程序。评测使用来自 GitHub 开源项目的 x86-64 Linux gcc 二进制及 ExeBench 的“real”子集；O1–O3 构建禁用内联，且只保留在所有优化级别均能反编译的函数，使 Hex-Rays 与 Ghidra 测试集分别减少 21% 和 76%。ExeBench 单元测试是偏乐观的代理指标；Realtype 没有测试，因此以依赖图等价性及名称、类型的完全匹配作为偏保守的代理指标，且 Realtype 的用户自定义类型须所有字段（递归计算平均 17.6 个）均匹配才算正确。主要模型使用专有 Hex-Rays 的输出，上下文窗口为 2,048 或 4,096 个词元。预测的名称与类型属于统计推断，并非恢复的原始信息。仍可能存在来自 GitHub 的预训练数据泄漏，且未评估混淆代码和恶意软件。

  **作者:** Luke Dramko 等

  </details>

- [**FidelityGPT：利用检索增强生成纠正反编译失真**](https://www.ndss-symposium.org/ndss-paper/fidelitygpt-correcting-decompilation-distortions-with-retrieval-augmented-generation/)

  FidelityGPT 对现有反编译器输出进行后处理：由大语言模型为代码行标注六类失真（如非常规解引用、冗余变量和令人困惑的控制流），再改写被标注的行。其提示词定义各失真类型，并从人工标注的 IDA Pro 与 Ghidra 失真代码行数据库中检索增强上下文。语义强度算法负责选择用于查询的代码行，变量依赖分析则在 50 行分块之间传递冗余变量上下文。作者在 620 对函数上报告检测准确率 89%、精确率 83%，纠正的修复率（FR）为 94%、正确修复率（CFR）为 64%，而他们运行的 DeGPT 分别为 83% 和 37%。

  NDSS 2026 · 会议论文 · [PDF](https://www.ndss-symposium.org/wp-content/uploads/2026-s989-paper.pdf) · [代码](https://github.com/ZhouZhiping045/FidelityGPT) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-fidelitygpt/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 620 对函数大多取自二进制相似性数据集中 Coreutils、curl、ImageMagick、OpenSSL、PuTTY 与 SQLite 的构建产物，经 IDA Pro 7.5 在 -O0 下反编译，覆盖 ARM-32、MIPS-32 与 x86-32，另含 x86-64 的 TheAlgorithms/C 代码；另有 -O1–-O3 与 Ghidra 数据集用于检验泛化能力。真实标签与 FR／CFR 均由作者团队依照论文标准人工评估。修复率统计的是被标为已修复的行，并非语义等价证明：作者指出修复后的代码往往无法重新编译或执行。纠正阶段以整个函数为单位，函数较长时效果可能下降；失真数据库由 150 行 IDA Pro 与 91 行 Ghidra 代码构建，可能遗漏较少见的异常。主要结果使用温度为 0.5 的 GPT-4o，仍具随机性；DeepSeek-chat 与温度为 0 的结果另行报告。无法排除这些开源项目出现在训练数据中的可能。

  **作者:** Zhiping Zhou 等

  </details>

- [**BinMetric：面向大语言模型的综合二进制代码分析基准**](https://www.ijcai.org/proceedings/2025/858)

  BinMetric 提供六类二进制分析任务共 1,000 道题目：调用点重建、反编译、函数签名恢复、二进制代码摘要、算法分类与汇编指令生成。题目取自 20 个开源 C 项目：项目针对 x86-64 编译、剥离符号并经 IDA Pro 处理，再借助 DWARF 信息与源码对齐。作者使用单样例提示评测来自五个模型家族的 12 个大语言模型，并在适用任务上与 IDA Pro 反编译器、LLM4Decompile、BinT5 和 HexT5 对比。

  IJCAI 2025 · 会议论文 · [PDF](https://www.ijcai.org/proceedings/2025/0858.pdf) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-binmetric/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 得分是针对孤立代码片段的题目级指标，并不代表端到端逆向工程流程或智能体工具使用能力。预处理需要 IDA Pro，所有二进制均是在 Ubuntu 22.04 上以各项目默认编译设置构建的 x86-64 程序；未研究其他架构、优化级别变化或混淆。多数任务以 Rouge-L、BLEU、METEOR 或 CodeBLEU 衡量文本重合度，因而并不检验语义等价；只有汇编生成任务检查能否编译及测试用例执行结果，其平均执行通过率低于 1%。摘要标签由 ChatGPT 生成后经人工审核；算法分类使用取自单一算法项目的 80 个片段。数据泄露筛查依赖网页精确匹配搜索。被评测模型均早于 2025 年（包括 gpt-3.5-turbo-16k-0613 与 gpt-4-0613），最大长度设为 8,192 个词元，因此排名只反映当时情况。

  **作者:** Xiuwei Shang 等

  </details>

- [**DecompileBench：面向真实场景的反编译器综合评测基准**](https://aclanthology.org/2025.findings-acl.1194/)

  利用真实程序中的函数、运行时行为检查，以及 LLM 辅助的代码可理解性评估，比较传统反编译器与基于 LLM 的方法。

  Findings of ACL 2025 · 会议论文 · [PDF](https://aclanthology.org/2025.findings-acl.1194.pdf) · [代码](https://github.com/vul337/DecompileBench) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-decompilebench/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 评估语料包含 130 个程序中的 23,400 个函数。基于模糊测试的检查覆盖有限，可理解性评分部分依赖 LLM 评审器。研究产物说明，重新构建的 OSS-Fuzz 项目可能与论文版本不同。

  **作者:** Zeyu Gao 等

  </details>

- [**DecLLM：借助大语言模型实现可重新编译的反编译，支持以程序化方式使用反编译代码**](https://dl.acm.org/doi/10.1145/3728958)

  DecLLM 将无法重新编译的反编译伪代码修复为可编译、可运行的 C 代码，使 CodeQL 等源码级工具能够用于二进制分析。其迭代流程把编译器错误反馈给现成的大语言模型，并回退非法输出和大段删除；随后利用重建程序与预期不符的测试输出及 AddressSanitizer 报告修复行为，最后对原始与重建的可执行文件进行模糊测试以发现行为差异。作者报告，使用 GPT-3.5 与 GPT-4 时，在 300 个 Code Contest 程序上的成功率分别为 74% 和 78.3%；在 Coreutils 与 CGC 二进制上，61.9%–70.9% 可重新编译，完全功能正常的占 48.1%–59.0%。

  Proceedings of the ACM on Software Engineering (ISSTA 2025) · 期刊论文 · [PDF](https://dl.acm.org/doi/pdf/10.1145/3728958) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-decllm/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 在 Code Contest 上，成功的含义是修复后的代码能够编译，且重建的可执行文件通过所提供的测试用例，并以 AFL++ 模糊测试作额外检查；Coreutils 与 CGC 的总体比率还计入功能异常或崩溃的重建二进制。这确立的是可编译性和基于测试的一致性，而非语义等价性，作者亦指出后者不可判定。结果依赖 IDA Pro 8.3 的输出（另以 Ghidra 10.4 重复一次实验），以及通过 API 提供、上下文上限为 4,096 个词元的 gpt-3.5-turbo-0613 与 gpt-4-0314 快照，因此所选程序须控制在该上限的一半以内。300 个 Code Contest 程序平均 112.9 行；Coreutils 9.5 与 CGC 二进制编译时未剥离符号，并逐函数修复，这种方式无法推断未定义的全局变量。约 30% 的困难案例仍然失败，主要原因包括反编译器混淆地址与数据、缓冲区大小推断错误、包含 STL 代码的过长输出，以及大语言模型以类型强制转换走捷径；测试未覆盖的行为偏差仍无法发现。对 Juliet 样本进行 CodeQL 分析时需要人工调整查询。

  **作者:** Wai Kin Wong 等

  </details>

- [**DiSCo：利用大语言模型将 EVM 字节码反编译为源代码**](https://dl.acm.org/doi/10.1145/3729373)

  DiSCo 通过提示冻结参数的大语言模型，把以太坊合约的创建字节码提升为 Solidity 源码，而不是输出反编译伪代码。它将控制流路径抽象为逻辑不变的语义单元，模拟执行从区块执行中捕获的创建字节码以恢复构造函数逻辑，并借助签名数据库与类型感知图模型推断被剥离的名称。这些单元被转写为自然语言描述，并与编码规范一起放入提示词。主要模型为 GPT-4，另测试了 Llama 3。

  Proceedings of the ACM on Software Engineering (FSE 2025) · 期刊论文 · [PDF](https://dl.acm.org/doi/pdf/10.1145/3729373) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-disco/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 真实标签来自 Etherscan 上的源码文件：200 个余额最高的合约用于全部基线，1,000 个用于自动化测试；另有独立实验使用 50 个 Vyper 合约、50 个新部署合约和 149 个闭源攻击合约。可编译率（五次采样取优约为 75%，单次运行为 46%）、差分模糊测试通过率与嵌入相似度都不能证明与已部署源码等价。模仿学习模糊测试器生成的交易近半数会回滚；人工审查认为约 28.5% 的生成合约语义一致，Vyper 输入仅为 12%。作者报告路径过多的合约会导致超时或分析不可靠，名称推断能力也仍然有限。基线是将 Panoramix、Ethervm 和 Elipmoc 的输出（多取自其网站，部分为人工反编译）交给同一大语言模型，并非独立反编译器之间的比较。结果依赖某个 GPT-4 预览版快照。攻击复现仅覆盖 2025 年 1 月的十起事件，其中四起复现成功。

  **作者:** Xing Su 等

  </details>

- [**释放生成式模型在剥离符号二进制变量名恢复中的能力**](https://www.ndss-symposium.org/ndss-paper/unleashing-the-power-of-generative-model-in-recovering-variable-names-from-stripped-binary/)

  GenNm 通过微调生成式代码模型（默认 CodeGemma-2B，另测试 CodeLlama-7B 及经 LoRA 微调的 CodeLlama-34B），为剥离符号二进制反编译代码中的占位变量建议名称。查询会加入沿调用图传播、已重命名的调用者代码与被调用者签名；类 DPO 的符号偏好优化（SymPO）抑制模型偏向训练集中高频名称，基于数据流的名称验证步骤则在多轮迭代中从候选名称里选择。作者报告，在重建的 DIRTY 与 VarCorpus 数据集上，其精确率比 VarBERT 和 ReSym 高 5.6–11.4 个百分点；对训练中未出现的名称，精确率为 22.8%，最强基线为 17.3%。

  NDSS 2025 · 会议论文 · [PDF](https://www.ndss-symposium.org/wp-content/uploads/2025-276-paper.pdf) · [代码](https://github.com/XZ-X/gennm-ndss-ae/tree/9955139b4c8d43144852a674bf317cbfaf32ed17) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-gennm/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 预测结果依据调试符号中的名称评分：一方面借助 SymLM 的词簇与规则进行词元匹配，另一方面由 GPT-4 评估器判断上下文相关性与语义准确性；两者都不能说明输出就是原始标识符，按二进制划分时整体精确率为 35.8%（DIRTY）和 41.2%（VarCorpus）。对训练中未出现的项目，精确率约为 30%，在 -O2 与 -O3 下的提升也较小。真实标签来自由 GitHub 项目或 Gentoo 软件包重建的 Linux 二进制文件中的调试信息，论文示例使用 IDA Pro 输出。GenNm 需要每个二进制的调用图，这也是重建 DIRTY 数据集的原因；VarCorpus 按函数划分的结果只使用 15% 的二进制样本，与黑盒 GPT-3.5／GPT-4 的比较使用 1,000 个抽样函数。它只恢复变量名，不恢复类型、函数名或完整的反编译代码。

  **作者:** Xiangzhe Xu 等

  </details>

- [**TypeForge：为去符号二进制合成并选择最适配的复合数据类型**](https://ieeexplore.ieee.org/document/11023499)

  TypeForge 从去符号二进制中恢复复合数据类型，包括结构体布局、联合体以及指针引用和嵌套关系。它在 Ghidra 反编译器推断出的变量之上构建全程序类型流图，传播成员偏移与大小，切断由类型转换和联合体引起的冲突边，并合成候选类型声明。大语言模型只在这些静态合成的候选中进行选择：每个候选通过反编译器的重定类型接口应用，再以双败淘汰赛比较所得伪代码的可读性。作者在 OSPREY 的 coreutils 数据集上报告复合类型识别 F1 为 81.7%、布局恢复 F1 为 88.2%、关系恢复 F1 为 72.1%。

  IEEE S&amp;P 2025 · 会议论文 · [PDF](https://noobone123.github.io/papers/typeforge-sp25.pdf) · [代码](https://github.com/noobone123/TypeForge) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-typeforge/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 恢复的是成员偏移、大小和类型间关系，而非原始类型名或成员名；由于名称不可得，关系是否正确以布局匹配判定。主要评测使用 OSPREY 的数据集，包括 GNU coreutils 与 Howard 数据集中较大的程序，涵盖超过 10,000 个函数和 11,000 个复合类型变量，优化级别为 O0–O3，真实标签取自调试信息；论文未按架构分别报告结果。基线比较中，OSPREY 的结果由其作者提供，运行时间为估算值，ReSym 的数据取自其已发表结果，因此并非所有基线均经重新运行。保守地删除冲突边可能遗漏有效成员；合并或展平成员的编译器优化会降低较高优化级别下的准确率。约 75% 的运行时间用于大语言模型选择阶段；默认模型为 GPT-4o mini，每轮比较执行三次。下游可读性与漏洞检测示例属于案例研究，不能证明语义等价。

  **作者:** Yanzhong Wang 等

  </details>

- [**Nova：结合层次注意力与对比学习的汇编代码生成式语言模型**](https://proceedings.iclr.cc/paper_files/paper/2025/hash/ef283d62b4bce30854a8d4827f331229-Abstract-Conference.html)

  Nova 是面向 x86-64 汇编的生成式大语言模型，从 DeepSeek-Coder 检查点出发，以 AnghaBench 与 The Stack 代码经 gcc -O0 至 -O3 编译、剥离符号并规范化后的汇编训练。它加入为每条指令构建摘要的层次注意力，以及对比学习目标：使同一函数的源码与 O0–O3 汇编表示彼此接近，并按优化级别排序。针对反编译微调后，Nova-1.3B 与 Nova-6.7B 在 HumanEval-Decompile 上的平均 Pass<span>@</span>1 分别为 25.17% 和 34.36%，比同规模 LLM4Decompile 高 14.84 和 12.41 个百分点；另行微调的模型在六个真实项目上的 O0 对 O3 二进制代码相似性检测中取得最高的平均 Recall<span>@</span>1。

  ICLR 2025 · 会议论文 · [PDF](https://proceedings.iclr.cc/paper_files/paper/2025/file/ef283d62b4bce30854a8d4827f331229-Paper-Conference.pdf) · [代码](https://github.com/lt-asset/nova/tree/6dfaf438fb23a8f024d0297653571615631ad8f4) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-nova/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 反编译以函数为单位，在 HumanEval-Decompile 的 164 个 C 问题上评测；每个问题在 O0–O3 下编译为 x86-64，每个函数采样 20 次并以题目测试用例运行。基于这些测试的 Pass<span>@</span>k 既不能证明整程序反编译能力，也不能证明等价性。除 LLM4Decompile 与 Nova 外，其他基线采用三样例提示而非微调。相似性结果针对 O0 查询与 O3 候选，候选池为来自 Binutils、Curl、ImageMagick、SQLite、OpenSSL 与 PuTTY 的 50–500 个函数，模型先在 BinaryCorp-3M 上微调。反编译微调使用抽样的 216 万对数据，README 称仅从 The Stack 获取 5 万个文件；论文也说明 Nova 仅支持 x86-64 汇编，模型规模限于 1.3B 和 6.7B。输入需要按论文方式规范化汇编。

  **作者:** Nan Jiang 等

  </details>

- [**Decompile-Bench：面向真实二进制反编译的百万级二进制与源码函数对**](https://papers.nips.cc/paper_files/paper/2025/hash/079cf13ae174c31f148207d94d213bdc-Abstract-Datasets_and_Benchmarks_Track.html)

  通过 Compile-Trace-Filter 流程构建 200 万组 C/C++ 二进制与源码函数对，并提供涵盖转写为 C/C++ 的 HumanEval、MBPP 任务及近期 GitHub 函数的评测集。

  NeurIPS 2025 Datasets and Benchmarks · 会议论文 · [PDF](https://papers.nips.cc/paper_files/paper/2025/file/079cf13ae174c31f148207d94d213bdc-Paper-Datasets_and_Benchmarks_Track.pdf) · [代码](https://github.com/albertan017/LLM4Decompile) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-decompile-bench/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 该工作研究函数级反编译。重新执行测试覆盖 HumanEval、MBPP；GitHub2025 未提供单元测试。内联可能使二进制与源码无法一一对应，微调实验仅使用 10% 的语料。这些结果不能证明整程序恢复能力。

  **作者:** Hanzhuo Tan 等

  </details>

- [**超越分类：借助领域适配的大语言模型推断去符号二进制中的函数名**](https://www.ndss-symposium.org/ndss-paper/beyond-classification-inferring-function-names-in-stripped-binaries-via-domain-adapted-llms/)

  SymGen 使用经 LoRA 微调的 Code Llama 模型生成去符号二进制的函数名，而不是在固定的名称词表上分类。每个去符号函数先由 Ghidra 反编译，再屏蔽其自身名称，并对被调用函数名进行归一化以便去重。微调之前，模型先以反编译代码及其对应源函数的大语言模型生成摘要进行领域适配。在 33 个 C 项目针对 x86-64、x86-32、ARM 和 MIPS 架构及 O0–O3 优化级别构建的函数上（经去重由 2,237,915 个减至 495,494 个），作者报告词级平均 F1 为 0.277（x86-64 上为 0.380），并给出混淆二进制与 Linux 恶意软件的案例研究。

  NDSS 2025 · 会议论文 · [PDF](https://www.ndss-symposium.org/wp-content/uploads/2025-797-paper.pdf) · [代码](https://github.com/OSUSecLab/SymGen) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-symgen/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 函数名被拆分为单词，并以精确率、召回率和 F1 评分，同时使用 SymLM 的 CodeWordNet 归并语义相近的词；预测结果是描述性的推测，并非恢复的原始符号。平均 F1 为 0.277，在 MIPS（0.137）和 ARM（0.262）上更低。摘要中最高 409.3%、553.5% 与 489.4% 的提升是作者报告的相对 AsmDepictor 的改进；各基线在作者去重后的数据集上重新训练，得分远低于其原论文结果，XFL 仅在 x86-64 上比较。每种架构和优化级别分别训练一个模型。所有二进制均由 GCC 9.4.0 构建，输入依赖 Ghidra 输出，且 Code Llama 的预训练数据未公开，仍可能存在数据泄漏。混淆测试对来自六个项目的 363 个二进制应用 Hikari 的三种默认混淆（F1 为 0.271–0.303）；恶意软件研究涵盖 16 个 x86-64 构建中的 812 个函数（F1 为 0.348）。

  **作者:** Linxi Jiang 等

  </details>

- [**ReSym：利用大语言模型恢复去符号二进制中的变量与数据结构符号**](https://doi.org/10.1145/3658644.3670340)

  结合两个微调语言模型与基于 Prolog 的跨函数推理，从去符号二进制的反编译结果中推断局部变量符号及用户自定义数据结构。

  ACM CCS 2024 · 会议论文 · [PDF](https://www.cs.purdue.edu/homes/lintan/publications/resym-ccs24.pdf) · [代码](https://github.com/lt-asset/resym) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-resym/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 该方法依赖底层反编译结果及针对 C/C++ 数据学习的预测。交叉检查可减少预测冲突，但不能证明恢复的名称或布局与缺失源码完全一致。公开研究产物包含模型、处理后的数据与评估代码。

  **作者:** Danning Xie 等

  </details>

- [**自构造上下文反编译与细粒度对齐增强**](https://aclanthology.org/2024.findings-emnlp.385/)

  为大语言模型将函数级 x86-64 GCC 汇编反编译为 C 的流程增加两项技术。自构造上下文反编译（sc²dec）无需微调：把模型首次生成且可编译的结果重新编译，以得到的汇编—源码对作为上下文示例再次反编译。细粒度对齐增强（FAE）利用 DWARF 调试信息构造语句级汇编—C 对齐数据，以 LoRA 微调 llm4decompile-6.7b。两者结合后，作者报告在 Decompile-Eval 上的平均可重执行率为 52.41%，基础模型为 48.60%。

  Findings of EMNLP 2024 · 会议论文 · [PDF](https://aclanthology.org/2024.findings-emnlp.385.pdf) · [代码](https://github.com/AlongWY/sccdec) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-sc2dec/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 结果为 Decompile-Eval 上的函数级可重执行率：164 道源自 HumanEval 的 C 题目，分别以 O0–O3 编译，并通过重新编译和 HumanEval 测试用例检查。通过这些测试不代表完整程序或全部输入上的等价性；论文也未评估真实二进制、其他架构或可读性。只有首次输出能够重新编译时 sc²dec 才有帮助，因此可重编译率低会限制其收益；作者报告以不匹配的优化级别构造上下文会使结果降低 1–2%，用 clang 构造的上下文得分也略低于 GCC。FAE 仅使用 10,000 个只依赖 C 标准库的 ExeBench 函数，训练一个轮次，且只基于一个 6.7B 基础模型；作者未在更大数据集或模型上验证，它还使 1-shot 结果略有下降。GPT-4 与 DeepSeek 基线是 API 快照，未必可复现。

  **作者:** Yunlong Feng 等

  </details>

- [**LLM4Decompile：使用大语言模型反编译二进制代码**](https://aclanthology.org/2024.emnlp-main.203/)

  训练语言模型将汇编反编译为 C，并改进 Ghidra 伪代码，以恢复函数能否重新编译并正确执行为评估目标。

  EMNLP 2024 · 会议论文 · [PDF](https://aclanthology.org/2024.emnlp-main.203.pdf) · [代码](https://github.com/albertan017/LLM4Decompile) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-llm4decompile/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 论文实验限定于 x86 平台的 C 代码和函数级基准。通过抽样测试重新执行，不代表整程序等价或恢复了原始源码。仓库后续版本应与 2024 年论文区分。

  **作者:** Hanzhuo Tan 等

  </details>

- [**WaDec：基于大语言模型的 WebAssembly 反编译**](https://dl.acm.org/doi/10.1145/3691620.3695020)

  WaDec 使用循环级 wat–C 代码片段对，以 LoRA 微调 CodeLlama-7b，将 WebAssembly 文本格式（wat）反编译为 C。它按依赖关系排列函数并进行切片，使每个输入至多包含一个循环，嵌套循环以标记替代。提示中补充被调用函数的声明、此前已定义的局部变量以及偏移到字符串的映射；随后重组输出，恢复字符串常量并重命名变量。训练数据来自经 Emscripten 编译的 51,768 个 the-stack-dedup 程序和 377 个 TheAlgorithms/C 程序。作者在 3,977 个 C 文件上报告，代码膨胀率为 3.34%，可重新编译率为 52.11%，可重新执行率为 43.55%，输出一致率为 27.15%，并与 Wasm2c 及 Ghidra 进行比较。

  ASE 2024 · 会议论文 · [PDF](https://arxiv.org/pdf/2406.11346v3) · [代码](https://github.com/XinyuShe/WaDec/tree/e244f7172539478a5b64bbb86e1fd03e527cb6be) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-wadec/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 所报告的比率是作者在经 Emscripten 编译为 Wasm 的 C 程序上取得的结果。约一半输出可重新编译，不到一半可重新执行，约四分之一能复现原始输出，因此反编译代码总体上并不语义等价。含 3,977 个文件的基准与训练程序来自相同的两个来源。未评估优化构建：作者既未针对 O1/O2 代码调整方法，也未用其训练模型。模型处理数据结构的能力也较弱，常将其拆成独立变量或数组。研究仅涉及 C 源码，未评估由其他语言或工具链生成的 Wasm。基线为 Wasm2c 与 Ghidra 的 Wasm 插件；由于没有大语言模型能在未经微调时反编译 Wasm 函数，此类基线被排除。切片意味着一个函数可能需多次反编译，每个提示约需 0.1 至 2 秒。

  **作者:** Xinyu She 等

  </details>

- [**StackSight：借助大语言模型与神经符号思维链反编译揭示 WebAssembly**](https://proceedings.mlr.press/v235/fang24e.html)

  StackSight 借助大语言模型提示，将 WebAssembly 文本格式（WAT）函数反编译为 C++。它先通过静态分析为每条 WAT 指令标注虚拟栈状态，在分支分叉处使用符号记法；再用单样例思维链提示，要求模型恢复变量含义、总结函数功能并写出 C++。使用 GPT-4 时，与单样例提示相比，通过全部基准测试的输出比例在 HumanEval-X 上从 19.7% 升至 36.5%，在 MBXP 上从 42.4% 升至 59.6%；论文还评估了 GPT-3.5 与 Code Llama-7B-Instruct。

  ICML 2024 · 会议论文 · [PDF](https://raw.githubusercontent.com/mlresearch/v235/main/assets/fang24e/fang24e.pdf) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-stacksight/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 输入是 HumanEval-X（164 个中 161 个可编译）与 MBXP（974 个中 773 个）C++ 子集中的简短练习函数，以 Emscripten 3.1.46 按 -Oz 编译为侧模块，通过 --profiling-funcs 保留函数名，再用 wasm2wat 1.0.33 转换；未评估经过压缩、混淆或完整应用规模的 WebAssembly。正确性指输出能够编译并通过基准测试用例的比例；测试判定器会重命名函数、插入测试并补充命名空间指令，按值传参则由人工修改。通过这些测试并不证明与原始模块等价。函数摘要以 BERTScore 和 SBERT 评分；用户研究有 15 名参与者，每个数据集 20 个代码片段。wasm2c 与一种早期神经反编译器因无法生成可编译输出而未纳入比较，结果也依赖特定版本的托管模型。

  **作者:** Weike Fang 等

  </details>

- [**SLaDe：面向优化汇编的可移植小语言模型反编译器**](https://ieeexplore.ieee.org/document/10444788)

  SLaDe 使用 200M 参数的编码器—解码器模型、面向代码的分词及 PsycheC 类型补全，将函数级汇编转换为 C。研究覆盖 x86 与 ARM 的 -O0、-O3 设置，并结合生成候选与输入／输出检查。输入是汇编文本而非原始机器字节，反汇编不属于该方法。

  IEEE/ACM CGO 2024 · 会议论文 · [PDF](https://arxiv.org/pdf/2305.12520v3) · [代码](https://zenodo.org/records/10205121) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-slade/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 评测覆盖约 4,000 个 ExeBench 函数及含 112 个程序的合成基准。束宽为 5，并选择首个通过有限输入／输出测试的候选；生成函数被放回原始调用上下文。通过这些测试不代表完整程序或全部输入上的等价性。编辑相似度只是可读性的代理指标。较长函数、外部调用及错误的类型／运算符预测仍会导致失败；模型的输入和输出窗口均为 1,024 个位置。历史基线比较的覆盖范围不同，不能据此确立当前排名。

  **作者:** Jordi Armengol-Estapé 等

  </details>

- [**“len、index 或 count，就是别叫 v1”：基于迁移学习预测反编译输出中的变量名**](https://ieeexplore.ieee.org/document/10646727)

  VarBERT 使用 BERT 式模型为 IDA Hex-Rays 与 Ghidra 的反编译输出建议变量名：模型先以来自 Debian 的 520 万个人工编写的 C 函数预训练，再以反编译代码微调；它还预测每个变量出自开发者，还是由反编译器引入。作者从 Gentoo 的 C 与 C++ 软件包构建 VarCorpus，在 O0 至 O3 下编译为 x86-64，并借助调试符号为反编译变量标注名称。在 O2 二进制的按函数划分上，IDA 与 Ghidra 的 Top-1 准确率分别为 54.43% 和 54.49%；在 IDA-O0 子集上为 50.70%，DIRE 与 DIRTY 分别为 35.94% 和 38.00%。

  IEEE S&amp;P 2024 · 会议论文 · [PDF](https://www.atipriya.com/files/papers/varbert_oakland24.pdf) · [代码](https://github.com/sefcom/VarBERT/tree/76f221a5e0af43a36169818cbbfd6e8dd3c98cdc) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-varbert/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 预测名称是模型学到的建议，以开发者原名称评分，并非恢复出的原始符号。在 O2 的按二进制划分上，Top-1 准确率降至 42.40%（IDA）与 40.49%（Ghidra）；在 IDA-O0 的按二进制划分上，其领先 DIRTY 的幅度为 4.52 个百分点。与 DIRE、DIRTY 的比较仅覆盖 O0 下的 IDA，并因 DIRE 训练耗时过长而只使用约 40 万个函数（约占 VarCorpus 的 15%）。方法只能为反编译器恢复出的变量命名，标注则依赖 IDA 与 Ghidra 在匹配调试符号时保留变量。语料来自 Linux 发行版软件包，以 x86-64 为主，另有规模较小的 AArch64 O2 实验，可能不代表 Windows 或 macOS 可执行文件；去重仅删除完全重复项。用户研究由 27 名完成全部 13 组函数的学生参与。类型、数据结构与可重新编译的代码不在其范围内。

  **作者:** Kuntal Kumar Pal 等

  </details>

- [**DeGPT：使用大语言模型优化反编译器输出**](https://www.ndss-symposium.org/ndss-paper/degpt-optimizing-decompiler-output-with-llm/)

  通过三个协同角色选择、提出并检查修改，改进已有的类 C 反编译输出。其流程简化代码结构、添加注释并重命名变量，在接受结构修改前，使用微代码片段语义计算比较模拟的符号值与调用。作者以四个代码库中的 620 个函数评估可读性与命名效果，并分别测试保留与剥离符号的版本。

  NDSS 2024 · 会议论文 · [PDF](https://www.ndss-symposium.org/wp-content/uploads/2024-401-paper.pdf) · [代码](https://github.com/PeiweiHu/DeGPT) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-degpt/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 报告的 24.4% 降幅来自保留符号版本输出的 Halstead 工作量代理指标，并非直接测得的人力节省。62.9% 的注释结果是人工判定正确的注释中，具有非平凡信息者的平均占比。MSSC 是过程内启发式检查：调用被抽象处理，循环转化为分支；解析、别名与路径增长仍有限制。其 80 个案例的人工审查报告准确率为 84%、召回率为 85%，其中漏过三处有害修改。这支持辅助理解伪代码，不能保证二进制等价、整程序可重新编译或恢复原始源码。

  **作者:** Peiwei Hu 等

  </details>

- [**XFL：基于极端多标签学习的二进制函数命名**](https://ieeexplore.ieee.org/document/10179439)

  XFL 将去符号二进制中的函数命名视为极端多标签分类：函数名被拆分为词元，再由 PfastreXML 从常见标签词表中为每个函数排序合适的词元。其 DEXTER 嵌入结合基于 angr VEX 中间表示的静态分析特征、调用图上下文和整个二进制的全局上下文，另有一个语言模型把预测的词元排列成函数名字符串。在来自 Debian 软件包、共 10,047 个 x86-64 C 二进制中的 741,724 个函数上，以 1,024 个标签的词表，作者报告精确率 0.835、召回率 0.575、F1 0.681，在精确率和 F1 上领先 Punstrip、Debin 与 Nero。

  IEEE S&amp;P 2023 · 会议论文 · [PDF](https://arxiv.org/pdf/2107.13404v4) · [代码](https://github.com/lmu-plai/xfl) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-xfl/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 预测结果是固定词表中的词元标签，经排序后可选地组合成名称；它们并非恢复的源码名称，评分也按词元而非完整名称匹配。评测使用来自 Debian 软件包、以多种编译器与优化设置构建的 x86-64 ELF C 二进制，以及规模较小的 Nero 数据集；训练所得模型仅适用于 x86-64 GNU/Linux 二进制。测试时所有工具均从符号表获取函数边界，因此不计入边界检测错误。许多测试函数名也出现在训练集中；仅考察训练中从未出现的名称时，F1 降至 0.242。混淆和对抗性二进制不在研究范围内。Nero 数据集上 Debin 与 Dire 的数据取自 Nero 论文，并未重新运行。

  **作者:** James Patrick-Evans 等

  </details>

- [**SymLM：基于上下文敏感、执行感知代码嵌入的去符号二进制函数名预测**](https://dl.acm.org/doi/10.1145/3548606.3560612)

  SymLM 将去符号二进制的函数名预测为一组名称单词。它使用在微执行轨迹上预训练的 Trex 模型编码每个函数的指令，将其与取自 Ghidra 过程间控制流图的调用者、内部被调用函数及外部库调用的嵌入融合，再由 MLP 解码器对固定词表中的单词打分；名称预处理和词嵌入模块 CodeWordNet 用于处理缩写与同义词。在 27 个项目的 16,027 个二进制、共 1,431,169 个函数上（涵盖 x86、x64、ARM 与 MIPS，O0–O3 优化级别及四种 Hikari 混淆），作者报告加权平均精确率 0.634、召回率 0.677、F1 0.655，并给出固件案例研究。

  ACM CCS 2022 · 会议论文 · [PDF](https://xinjin95.github.io/assets/pdf/SymLM_ccs2022_paper.pdf) · [代码](https://github.com/OSUSecLab/SymLM) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-symlm/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 函数名被预测为来自固定训练词表的无序单词集合，并按单词级精确率、召回率和 F1 评分，CodeWordNet 会将语义相近的单词计为匹配。这并非精确恢复源码名称，且无法生成词表外的单词。二进制由 GCC 7.5 为 Linux 构建，并在同样的 27 个项目内按二进制划分数据集。在来自 12 个未见项目的 540 个二进制上，整体表现仍然较低，作者将部分原因归于词表不匹配；后来一项 NDSS 2025 研究在去重数据上比较时，报告 SymLM 的平均 F1 为 0.105。与 NFRE 的比较仅针对 x64，与 NERO 的比较使用 NERO 的数据集。混淆实验覆盖四种 Hikari 混淆，不包括加壳或加密。固件案例中，八个 32 位 ARM 固件映像的 1,061 个函数里有 172 个得到部分正确的名称。

  **作者:** Xin Jin 等

  </details>

- [**利用学习得到的变量名称与类型增强反编译输出**](https://www.usenix.org/conference/usenixsecurity22/presentation/chen-qibin)

  提出 Transformer 模型 DIRTY，根据反编译代码和布局信息推荐变量名与类型，并提供用于训练和评估的 DIRT 语料。

  USENIX Security 2022 · 会议论文 · [PDF](https://arxiv.org/pdf/2108.06363) · [代码](https://github.com/CMUSTRUDEL/DIRTY) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-dirty/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 原始流程围绕 C 程序和 Hex-Rays 输出构建。预测名称与类型是模型推断，不保证与原始符号一致。正式论文发表于 2022 年，arXiv 预印本首次提交于 2021 年。

  **作者:** Qibin Chen 等

  </details>

- [**jTrans：面向二进制代码相似性检测的跳转感知 Transformer**](https://dl.acm.org/doi/10.1145/3533767.3534367)

  jTrans 使用 BERT 风格的 Transformer 为二进制函数生成嵌入，以支持相似性检索。其跳转感知表示让直接跳转的操作数词元与跳转目标的位置嵌入共享参数，从而无需单独的图神经网络即可将控制流引入指令序列。模型先以掩码语言建模和跳转目标预测进行预训练，再以余弦三元组目标在同一源码不同优化级别编译出的函数上微调。论文还发布了 BinaryCorp，它由 gcc 与 g++ 编译 Arch Linux 官方仓库及 AUR 中的 C/C++ 软件包构建而成。

  ACM ISSTA 2022 · 会议论文 · [PDF](https://arxiv.org/pdf/2205.12713v1) · [代码](https://github.com/vul337/jTrans) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-jtrans/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 模型仅在单一架构上训练（据论文讨论部分为 x86），未评估跨架构检索。方法只编码直接跳转，间接跳转目标不在研究范围内。反汇编与函数提取依赖 IDA Pro 7.5，上游的边界识别错误未被衡量。BinaryCorp 在 O0–O3 与 Os 之间配对 gcc／g++ 构建结果，并按项目划分训练集与测试集；它不涵盖混淆或其他编译器，只有漏洞检索实验额外加入 clang 变体。作者报告在 BinaryCorp-26M、候选池规模为 10,000 时，平均 Recall<span>@</span>1 为 62.5%，最佳基线为 32.0%；随着候选池增大，准确率仍会下降，作者也指出真实场景的候选池更大。漏洞检索实验使用八个 CVE，每个有十个变体。基线来自 2022 年，其中 Asm2Vec 与 OrderMatters 为重新实现，因此该比较不能确立当前排名。相似性排序只给出候选匹配，并不恢复源码、名称或类型。

  **作者:** Hao Wang 等

  </details>

- [**ExeBench：机器学习规模的可执行 C 函数数据集**](https://dl.acm.org/doi/10.1145/3520312.3534867)

  ExeBench 是数据集，而非反编译器。它从 GitHub 与 AnghaBench 中提取 C 函数，通过查找真实的头文件与定义或注入合成定义使其可编译，再依据函数签名生成输入／输出样例，并以 C++ 包装器运行每个函数。精确去重后，作者报告共有 4,485,817 个可编译函数和 687,843 个可执行函数，其中 124,612 个带有常量或恒等实现无法通过的丰富 IO；论文还说明每行数据附有 O0、Os 与 Ofast 下的 x86 和 ARM 汇编。SLaDe、LLM4Decompile 等反编译研究随后用它检验反编译函数能否正确重新执行。

  ACM SIGPLAN MAPS 2022 · 会议论文 · [PDF](https://dl.acm.org/doi/pdf/10.1145/3520312.3534867) · [代码](https://github.com/jordiae/exebench/tree/8b47d483c2e39ea40a304fbaac46e41a1a14272f) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-exebench/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** IO 依据函数签名生成，不考虑程序上下文：每个函数 10 对（合成定义使用三个随机种子，共 30 对），数组默认长度为 32；含指针与整数互转的函数生成成功率低于 5%，含 goto、标签及复杂控制流的函数成功率也较低，因此可执行函数整体比可编译函数更简单。合成 IO 基于注入的替代定义，而非函数的真实依赖生成；带有真实定义且具备丰富 IO 的函数仅有 4,464 个。有限的 IO 对只检验采样输入上的行为，并不证明语义等价；去重也只删除分词后完全相同的函数。运行带真实依赖的函数意味着执行不受信任的代码，作者使用了权限受限的容器。论文所用的 v1.00 原始数据仅可申请获取，公开的 v1.01 版本调整了数据划分（例如真实测试函数为 2,134 个，而非 2,232 个）。每个函数保留其来源仓库的许可证，ExeBench 新增内容采用 MIT 许可。

  **作者:** Jordi Armengol-Estapé 等

  </details>

- [**超越 C：基于神经机器翻译的可重定向反编译**](https://www.ndss-symposium.org/ndss-paper/auto-draft-298/)

  BTC（Beyond The C）将反编译视为从编译器输出的 x86-64 汇编到源码的纯文本翻译，分别在汇编与源码上训练字节对编码分词器，并使用标准 fairseq Transformer。它借助编译器输出的 CFI 与行号指令配对函数，而非依赖特定语言的解析器、编译器插件或提升器，因此同一流程可针对 Go、Fortran、OCaml 与 C 重新训练。训练集规模从小型 C、Go 与 Fortran 语料的约 10,000 个函数，到基于 Debian 软件包构建的 200 万个 C 函数不等。在大型 C 数据集上训练的最佳模型，在留出函数上的归一化平均编辑距离为 0.46。

  Workshop on Binary Analysis Research (BAR) 2022 · 会议论文 · [PDF](https://www.ndss-symposium.org/wp-content/uploads/bar2022_23009_paper.pdf) · [代码](https://figshare.com/s/2c68b9c181e80f4e3b06) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-beyond-the-c/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 评测在函数层面覆盖四种语言，仅以与原始源码的归一化编辑距离评分；未报告编译、测试或语义等价检查，也未评估完整程序的反编译。作者指出该方法无法保证语义正确，尚不能用于真实代码：即便最佳分数也意味着大约一半的函数词元需要修改。输入是保留标签与 CFI 指令的编译器生成 x86-64 汇编，因此对去符号二进制的反汇编、其他架构以及不输出此类指令的编译器均不在评测范围内。序列长度限制排除了较长函数，小型语料主要来自编程竞赛题和小型工具代码。与 Katz 等人的比较引用的是该工作在更短代码片段上报告的分数，而非在相同数据上重新运行。

  **作者:** Iman Hosseini 等

  </details>

- [**基于增强控制流图的剥离符号二进制神经逆向工程**](https://dl.acm.org/doi/10.1145/3428293)

  Nero 为剥离符号的 x86-64 Linux 可执行文件中的过程预测名称，并不生成反编译代码。它通过静态分析重建调用点（包括导入的 API 名称），并沿控制流路径为参数补充具体值与抽象值。LSTM、Transformer 与图神经网络编码器处理由此得到的增强调用点图，再由解码器以子词序列生成名称。在 GNU 软件包测试集上，作者报告 Nero-GNN 的 F1 为 45.53，改造后的 DIRE 为 35.52，Debin 为 33.66。

  Proceedings of the ACM on Programming Languages (OOPSLA 2020) · 期刊论文 · [PDF](https://arxiv.org/pdf/1902.09122v4) · [代码](https://github.com/tech-srl/Nero/tree/7dac9f5748974ea8f39b5f29bb3c7d33f971077e) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-nero/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 评测使用来自纯 C 语言 GNU 软件包、构建为 x86-64 Linux 可执行文件的 67,246 个过程；在剔除 C++ 可执行文件、测试程序、静态链接软件包及同一软件包的重复版本后，按软件包划分为 60,403／2,034／4,809 个样本。标签取自剥离前的名称，F1 按名称子词计算，因此输出是模型学到的建议，而非恢复出的原始符号。模拟 API 名称混淆（将 .dynstr 节清零）会使 Nero-GNN 的 F1 降至 38.83；论文未处理加壳和更强的混淆。每个过程至少需要一个可静态检测的调用点，内联过程无法命名。数据生成依赖已授权的 IDA Pro（测试版本 6.95）识别过程边界并导出，另需 angr 与 LLVM 10；模型代码使用 TensorFlow 1.13.1。本条不对与当前工具版本的兼容性作任何判断。

  **作者:** Yaniv David 等

  </details>

- [**DIRE：基于神经网络的反编译标识符命名方法**](https://doi.org/10.1109/ASE.2019.00064)

  结合反编译输出中的词法与结构信息预测有意义的变量名，并使用编译 C 项目构建训练和评估语料。

  ASE 2019 · 会议论文 · [PDF](https://arxiv.org/pdf/1909.09029) · [代码](https://github.com/pcyin/dire) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-dire/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 该工作研究学习式标识符命名，并非完整源码重建或自主智能体。报告结果针对 x86-64 C 代码语料，并依赖反编译器输出。原作者仓库已标记弃用，并指向后续项目。

  **作者:** Jeremy Lacomis 等

  </details>

- [**Coda：端到端神经程序反编译器**](https://proceedings.neurips.cc/paper_files/paper/2019/hash/093b60fd0557804c8ba0cbf1453da22f-Abstract.html)

  Coda 分两个阶段将短函数的汇编反编译为 C。首先由区分指令类型的 N 叉 Tree-LSTM 编码器与带注意力输入的 AST 解码器生成代码草图；随后由多个神经错误预测器的集成提出词元修正，只有当候选代码重新编译后与输入汇编的编辑距离不增加时，才保留该修正。在合成基准上，作者报告修正后的平均程序准确率为 82%，而带注意力的序列到序列基线为 12%。

  NeurIPS 2019 · 会议论文 · [PDF](https://proceedings.neurips.cc/paper_files/paper/2019/file/093b60fd0557804c8ba0cbf1453da22f-Paper.pdf) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-coda/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 训练与测试程序均为随机生成，涵盖 Karel 指令、math.h 调用及算术或逻辑表达式，分为短、长两种（平均长度 15 与 30），每项任务 50,000 对，并在不开启优化的条件下编译：主要 MIPS 结果使用 clang -O0，x86-64 附录使用 gcc -O0，且只报告草图词元准确率，平均约低 6%。真实场景检查仅包括小型 PyTorch C++ API 模型构建程序和 Hacker’s Delight 无循环程序。程序准确率要求与真实源码词元完全一致，论文正是在该指标下报告常规反编译器为 0%。错误修正假定已知编译器配置，程序变长时词元准确率下降。这些结果既不能说明优化代码、整程序或二进制等价的反编译能力，论文也未给出作者实现。

  **作者:** Cheng Fu 等

  </details>

- [**Debin：预测去符号二进制中的调试信息**](https://dl.acm.org/doi/10.1145/3243734.3243866)

  Debin 为 x86、x64 与 ARM 上去符号的 ELF 二进制预测调试信息。它先将代码提升为 BAP-IR，用极端随机树分类器判断哪些寄存器和内存偏移对应源码级变量；再借助 Nice2Predict 求解条件随机场，联合预测变量与函数的名称和类型，并将结果以 DWARF 节写回二进制。作者在每种架构 300 个留出二进制上报告，x64 名称与类型预测的精确率为 68.8%、召回率为 68.3%。

  ACM CCS 2018 · 会议论文 · [PDF](https://files.sri.inf.ethz.ch/website/papers/ccs18-debin.pdf) · [代码](https://github.com/eth-sri/debin) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-debin/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 数据集为每种架构 3,000 个未去符号的可执行文件与共享库，来自 830 个 Linux 调试符号软件包，源码为 C 语言并按各包默认设置编译，按 2,700／300 划分训练与测试。准确率评估假定函数边界已知；对于完全去符号的输入，由 BAP 的 ByteWeight 推断函数边界，论文引用其准确率约为 93%。Debin 预测 17 种类型，struct 与 union 的内部内容、行号以及 PE 等其他格式不在评测范围内。只有与原始调试信息完全相同的预测才计为正确。基于编译器生成的良性代码学习的模型，在混淆二进制、手写汇编或恶意软件上可能准确率较低。针对 35 个恶意样本的研究是对反编译输出的人工检查，由于样本缺少调试信息真实标签，未报告准确率。

  **作者:** Jingxuan He 等

  </details>

<a id="papers-website-reconstruction"></a>
### 网站重建

[↑ 论文主题](#papers) · [目录](#目录)

- [**Vision2Web：采用智能体验证的分层视觉网站开发基准**](https://proceedings.mlr.press/v306/he26n.html)

  基于视觉原型和文字需求评测网站开发，包含 100 项静态页面、66 项交互前端与 27 项全栈任务，将基于工作流的功能检查与模型进行的视觉比较结合。

  ICML 2026 · 会议论文 · [PDF](https://raw.githubusercontent.com/mlresearch/v306/main/assets/he26n/he26n.pdf) · [代码](https://github.com/zai-org/Vision2Web) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-vision2web/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 全栈层级由明确规格驱动，并非仅通过探索运行中的网站进行重建。工作流测试状态管理与增删改查结果，但有限的智能体判断不能证明后端或数据库持久性的精确等价。当前公开评测器在每个工作流内保持浏览器会话，并允许检查本地业务 API；这不构成通用的持久化证明。

  **作者:** Zehai He 等

  </details>

- [**ProgramDistill：将交互式 Web 应用转化为可验证的参考驱动软件工程任务**](https://arxiv.org/abs/2609.18805)

  评测智能体从源码不可见的运行参考中恢复 Web 应用行为的能力，提供覆盖 26 个应用的 4,063 项功能恢复任务，以及独立的 12 应用重建设置，通过重放具有依赖关系的浏览器工作流评分。

  arXiv 2026 · 预印本 · [PDF](https://arxiv.org/pdf/2609.18805v1) · [代码](https://huggingface.co/datasets/microsoft/ProgramDistill) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-programdistill/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 测试限于自包含应用（包括 SaaS 克隆）中由模型挖掘的有限行为。重放工作流可发现持久化失败，但通过测试不能证明全部后端或数据库不变量成立。被评测智能体接收不含截图的结构化浏览器观察，未衡量视觉保真度。公开验证器与参考解答也不构成抗污染测试集。

  **作者:** Jeonghye Kim 等

  </details>

- [**UI2App：评测可执行 Web 应用生成中的视觉交互推断**](https://arxiv.org/abs/2607.06306)

  UI2App 使用来自 95 个 Web 应用的 600 张截图，评测生成的可运行 React/TypeScript 应用。它通过参考交互分类体系和公开评测流水线，分别衡量构建可执行性、视觉保真度，以及包括跨路由状态在内的截图隐含交互行为。

  arXiv 2026 · 预印本 · [PDF](https://arxiv.org/pdf/2607.06306v2) · [代码](https://github.com/chenmancm169/UI2App) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-ui2app/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 静态截图无法唯一确定行为；评分规则接受多种有效实现，并不证明与原应用或后端等价。Auto IIS 在不执行工具的情况下评判生成源码和截图，人工运行验证覆盖 45 个应用的子集。跨路由状态不一定能在重新加载或会话结束后持久保存。主结果每个应用与模型组合生成一次，重复运行仅覆盖子集。

  **作者:** Grace Man Chen 等

  </details>

- [**Dashboard2Code：评估多模态模型重建交互式仪表盘的能力**](https://aclanthology.org/2026.acl-long.1750/)

  评估智能体主动探索运行中的仪表盘后，重建其外观与交互逻辑的能力。DashboardMimic 提供 180 个 Plotly+Dash 示例，并以代码语义分析和动态交互测试评估生成的实现。

  ACL 2026 · 会议论文 · [PDF](https://aclanthology.org/2026.acl-long.1750.pdf) · [代码](https://github.com/nth2000/Dashboard2Code) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-dashboard2code/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 限定于 Plotly+Dash 仪表盘，包含经模型扩充的示例。部分设置提供 DOM 信息，评估使用模型评审器。它并非通用后端恢复基准。链接的数据集需要接受访问条件并共享联系信息。

  **作者:** Tianhao Niu 等

  </details>

- [**CASCADE：谷歌基于大语言模型的 JavaScript 反混淆器**](https://doi.org/10.1145/3786583.3786873)

  利用 Gemini 定位 Obfuscator.IO 为字符串混淆插入的前置（prelude）函数，再在 JSIR 编译器中间表示上执行常量传播与内联，以确定性方式还原字符串字面量和 API 名称。

  ICSE-SEIP 2026 · 会议论文 · [PDF](https://arxiv.org/pdf/2507.17691v2) · [代码](https://github.com/google/jsir) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-cascade/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 该方法针对 Obfuscator.IO 的字符串混淆；控制流平坦化、其他混淆器及基于智能体的设计留待后续工作。评测以 Obfuscator.IO 的四种预设配置混淆 ETH 150k JavaScript 数据集中的 3,000 个程序，衡量前置函数识别、还原的字面量数量和运行时间，而非功能等价性。生产部署及扫描规模均为作者自述，生产环境的预筛选依赖一条未公开的 YARA 规则。

  **作者:** Shan Jiang 等

  </details>

- [**ScreenCoder：以模块化多模态智能体推进面向前端自动化的视觉到代码生成**](https://arxiv.org/abs/2507.22827)

  将截图到代码的生成分配给定位、规划和生成三个智能体，分别标注界面区域、构建层级布局树并编写 HTML/CSS。该流程还生成了用于监督微调和强化学习的 Screen-10K 训练数据；论文另提出包含 1,000 个网页的 ScreenBench。

  EMNLP 2026 · 已接收 · [PDF](https://arxiv.org/pdf/2507.22827v2) · [代码](https://github.com/leigest519/ScreenCoder) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-screencoder/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 输出为静态 HTML/CSS 布局，不重建交互、JavaScript 行为或后端逻辑。结果是 ScreenBench 与 Design2Code 上的视觉相似度分数（CLIP 及经 OCR 匹配的文本块），不能证明代码层面或功能上的等价。公开流程需调用托管模型 API，默认使用豆包（Doubao）。审阅文本为 arXiv v2，EMNLP 接收版本可能有所不同。

  **作者:** Yilei Jiang 等

  </details>

- [**IWR-Bench：大型视觉语言模型能否根据用户交互视频重建可交互网页？**](https://proceedings.iclr.cc/paper_files/paper/2026/hash/55bfedfd31489e5ae83c9ce8eec7b0e1-Abstract-Conference.html)

  测试模型利用用户交互视频和提供的静态资源重建可交互网页的能力。其 113 项任务通过重放标注的操作序列，评估已观察页面状态的视觉保真度与功能行为。

  ICLR 2026 · 会议论文 · [PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/55bfedfd31489e5ae83c9ce8eec7b0e1-Paper-Conference.pdf) · [代码](https://github.com/SIGMME/IWR-Bench) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-iwr-bench/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 要求输出单个 HTML 文件；论文明确要求用 JavaScript 静态数据模拟隐含的后端逻辑。轨迹覆盖和模型评审均不能证明完整网站或后端等价。

  **作者:** Yang Chen 等

  </details>

- [**JsDeObsBench：衡量与评测大语言模型的 JavaScript 反混淆能力**](https://doi.org/10.1145/3719027.3744871)

  对附带测试用例的 Project CodeNet 程序施加 JavaScript-Obfuscator 的七种混淆变换，构建可通过执行验证的 JavaScript 反混淆基准，并从语法、执行结果、代码简化程度及与原始代码的相似度评估 LLM 和现有工具的输出。

  ACM CCS 2025 · 会议论文 · [PDF](https://arxiv.org/pdf/2506.20170v1) · [代码](https://github.com/Ch3nYe/JsDeObsBench) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-jsdeobsbench/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 平均而言，LLM 输出通过执行检查的比例为 60.93%，两种现有反混淆工具基线为 83%。所有样本均由单一混淆器生成，原始程序是长度适中的编程竞赛解答。4,515 个经混淆的恶意代码样本没有测试用例，只能通过行为轨迹比较。

  **作者:** Guoqiang Chen 等

  </details>

- [**Interaction2Code：从交互原型生成网页代码的多模态大语言模型评测基准**](https://doi.org/10.1109/ASE63991.2025.00028)

  评测模型根据交互前后的截图重建可交互网页的能力。最终研究涵盖 127 个网页、374 项交互，并比较渲染外观、自动交互检查与人工可用性判断。

  ASE 2025 · 会议论文 · [PDF](https://arxiv.org/pdf/2411.03292v3) · [代码](https://github.com/WebPAI/Interaction2Code) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-interaction2code/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 输入描述单项交互的状态变化，并非自主探索完整网站。测试不能证明长流程、服务端行为或原始源码等价；交互能够被检测到，也不代表它可用。

  **作者:** Jingyu Xiao 等

  </details>

- [**WebUIBench：评估多模态大语言模型从网页界面生成代码能力的综合基准**](https://aclanthology.org/2025.findings-acl.815/)

  通过视觉感知、HTML 编程、图像与 HTML 对应理解，以及截图重建任务，诊断从网页界面生成代码的能力；利用来自真实网站的问答对，分别考察各项基础技能。

  Findings of ACL 2025 · 会议论文 · [PDF](https://aclanthology.org/2025.findings-acl.815.pdf) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-webuibench/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 主要评估视觉与 HTML 重建技能。论文虽含初步交互研究，但并非完整流程或后端等价评测。官方仓库目前提供 README 和图片，未提供说明中提及的评估脚本。

  **作者:** Zhiyu Lin 等

  </details>

- [**分而治之：从截图生成界面代码**](https://doi.org/10.1145/3729364)

  沿视觉分隔线递归切分网页截图，由多模态模型为每个叶子片段生成 HTML/CSS，再将子片段代码逐级向上组装为完整页面；评估涵盖 GPT-4o、Gemini 与 Claude 系列模型以及一项小规模开发者研究。

  Proceedings of the ACM on Software Engineering 2025 · 期刊论文 · [PDF](https://arxiv.org/pdf/2406.16386v3) · [代码](https://github.com/WebPAI/DCGen) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-dcgen/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 该方法以 HTML/CSS 重建静态视觉布局，不重建交互、JavaScript 行为或后端逻辑。测试页面是将图片替换为占位图的自包含快照；主要评测从 348 个热门网站中抽取 111 个，另加 80 个更复杂的 GitHub Pages 页面，可用性研究仅有四名参与者。分割依赖人工设定的阈值，组装阶段仍可能错排元素。

  **作者:** Yuxuan Wan 等

  </details>

- [**WebCode2M：面向网页设计稿代码生成的真实世界数据集**](https://dl.acm.org/doi/10.1145/3696410.3714889)

  WebCode2M 将约 256 万张真实网页截图与净化后的 HTML/CSS 代码及元素边界框布局树配对。数据取样自 Common Crawl 快照，经清洗（移除脚本、元数据与隐藏元素，并将样式合并为单一样式块）后用 Playwright 渲染，再由基于 10,000 条人工标注样本训练的神经评分器筛选。论文以 Pix2Struct-1.3B 微调出基线模型 WebCoder，提出衡量 DOM 结构召回率的 TreeBLEU 指标，并在短、中、长三个各含 256 个网页的测试子集上评测专用、开源及商业多模态模型。

  WWW 2025 · 会议论文 · [PDF](https://arxiv.org/pdf/2404.06369v2) · [代码](https://github.com/CGCL-codes/naturalcc/tree/main/examples/webcode2m) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-webcode2m/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 任务是根据设计图生成静态 HTML/CSS。净化过程会移除脚本，因此不重建交互、客户端行为或后端逻辑；输出以视觉得分、CLIP 相似度和 TreeBLEU 评判，而非功能等价性。论文报告，所有被评测模型都无法准确还原图像元素，且目标代码越长得分越低。768 个测试网页取自高分候选并经人工检查；评分器准确率约为 90%，训练集中仍有低质量样本，作者也提醒爬取内容可能仍含不当材料。商业模型仅以模型家族命名，约三分之一的 Gemini 测试样例因 recitation 错误失败，因此相关比较只反映当时情况。数据集卡片声明的 CC BY 4.0 许可不能清除所爬取网页代码、文本或图片的权利。

  **作者:** Yi Gui 等

  </details>

- [**Design2Code：面向自动化前端工程的多模态代码生成评测**](https://aclanthology.org/2025.naacl-long.199/)

  使用真实网页参考、视觉元素和布局指标及人工评估，测试从网页截图重建前端代码的能力。

  NAACL 2025 · 会议论文 · [PDF](https://aclanthology.org/2025.naacl-long.199.pdf) · [代码](https://github.com/NoviScl/Design2Code) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-design2code/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 该工作属于网站视觉重建，不涉及二进制反编译，也不恢复后端行为或交互工作流。主基准含 484 个使用占位图的网页，代码与数据分别采用各自的许可条款。

  **作者:** Chenglei Si 等

  </details>

- [**面向代码分析的大语言模型：LLM 真的胜任吗？**](https://www.usenix.org/conference/usenixsecurity24/presentation/fang)

  评估 GPT-3.5-turbo、GPT-4、LLaMA-2-13B、Code-LLaMA-2-13B-Instruct 与 StarChat-Beta 解释已去除注释的 JavaScript、Python 和 C 代码功能的能力，再在经 JavaScript Obfuscator（标识符重命名、死代码注入、控制流平坦化与字符串拆分）及 Wobfuscator WebAssembly 变换混淆的 JavaScript 上重复该任务。研究还要求 GPT-3.5 与 GPT-4 将 100 个 IOCCC 获奖程序改写为可读、可编译的代码。案例研究将 GPT 模型用于一个僵尸网络仓库与一个正常浏览器扩展仓库、经 JD-GUI 反编译的 Android 短信窃取程序，以及经 RetDec 反编译的 WannaCry 代码。

  USENIX Security 2024 · 会议论文 · [PDF](https://www.usenix.org/system/files/usenixsecurity24-fang.pdf) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-llm-code-analysis/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 真实标签是 GPT-4 自身生成、经四名学生人工核查的解释；其他模型则通过相似度指标与 GPT-4 评判与这些文本比较，作者也指出该评判方法若无人工校准并不可靠。正确性在解释层面判断，并非依据恢复出的行为或可执行等价性。只有 JavaScript 经过工具生成的混淆变换；两个 GPT 模型都未能解读 Wobfuscator 插入的 WebAssembly，较小模型在施加混淆后则无法给出有意义的解释。作者报告 GPT-4 在未混淆代码上的准确率为 97.4%，在混淆 JavaScript 上为 87%；在 IOCCC 去混淆任务中，GPT-3.5 约 20%、GPT-4 19% 的目标得到可编译代码，最终仅分别有 8% 和 4% 产生正确结果。恶意软件分析是针对少量样本的定性案例研究：WannaCry 需人工分块输入，上下文被拆分时会漏掉行为，僵尸网络仓库中还出现误报。模型能认出来自热门仓库的代码，因此记忆效应是混杂因素。被评测的 GPT-3.5／GPT-4 时代模型及 LLaMA-2-13B 级别模型已经过时。研究分析的是源码或已反编译的文本，并不执行二进制反编译。

  **作者:** Chongzhou Fang 等

  </details>

- [**Web2Code：面向多模态大语言模型的大规模网页转代码数据集与评估框架**](https://proceedings.nips.cc/paper_files/paper/2024/hash/cb66be286795d71f89367d596bf78ea7-Abstract-Datasets_and_Benchmarks_Track.html)

  通过指令微调和两个评测基准研究从截图重建 HTML。Web2Code 结合生成网页、经改进的 WebSight 与 pix2code 图像／代码对，以及来自 WebSRC 的问答。模型根据网页图像与指令生成 HTML，渲染输出接受视觉比较，另一个基准则测量截图理解能力。

  NeurIPS 2024 Datasets and Benchmarks · 会议论文 · [PDF](https://proceedings.neurips.cc/paper_files/paper/2024/file/cb66be286795d71f89367d596bf78ea7-Paper-Datasets_and_Benchmarks_Track.pdf) · [代码](https://github.com/MBZUAI-LLM/web2code) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-web2code/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 评估使用 1,198 张截图和 5,990 个是／否问题。WCGB 用 GPT-4V 评价渲染图像；其“用户界面与交互性”类别衡量元素外观，并不执行点击路径、持久状态或后端行为。合成与改进样本不能确立对任意真实 Web 应用的覆盖、与原始源码等价或代码质量。论文报告，在 1,000 项隐私抽样中，2.7% 存在联系信息问题，因此不能笼统宣称数据完全不含此类信息。

  **作者:** Sukmin Yun 等

  </details>

<a id="papers-game-reconstruction"></a>
### 游戏重建与逆向工程

[↑ 论文主题](#papers) · [目录](#目录)

- [**GameReplica：视觉语言智能体的黑盒视觉游戏复刻基准**](https://arxiv.org/abs/2609.22308)

  通过来自 25 款网页游戏、各设五个难度级别的 125 个任务，评估视觉语言智能体能否通过截图和主动交互推断隐藏规则，并构建可运行的单文件 HTML 游戏复刻。

  arXiv 2026 · 预印本 · [PDF](https://arxiv.org/pdf/2609.22308v1) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-gamereplica/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 任务覆盖以规则为核心的网页解谜和棋盘游戏，不代表原生或商业游戏重建能力。规则、实现和视觉评分使用 LLM 评审，不能证明行为等价。官方网站提供演示，尚未核实基准代码仓库。

  **作者:** Boyu Qiao 等

  </details>

- [**Tycho：面向 ARC-AGI-3 的程序化世界模型主动抽象**](https://arxiv.org/abs/2607.28287)

  Tycho 根据陌生 ARC-AGI-3 游戏中的动作与观察历史，构建可编辑的 Python 模型，描述游戏状态、状态转移、渲染与结果。它将模型预测与已记录的转移进行核对，并在规划时选择使用、修复或绕过这些模型。

  arXiv 2026 · 预印本 · [PDF](https://arxiv.org/pdf/2607.28287v1) · [代码](https://github.com/NIMI-research/Tycho) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-tycho/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 评估针对 25 个公开游戏、183 个关卡，每种配置仅进行一次随机运行；其中五个游戏曾用于开发智能体框架。模型可以不预测部分像素格，或接受有限的渲染变体。转移回放和游戏分数不能证明完整引擎重建、目标识别正确、未见状态保真度、未见游戏泛化或多次运行的可靠性；智能体也可以绕过建模。

  **作者:** Jens Lehmann 等

  </details>

- [**RevengeBench：通过行为实验逆向恢复代码形式的策略**](https://arxiv.org/abs/2606.26094)

  使用五种游戏环境中的 75 个合成策略，测试智能体能否通过行为轨迹和自行设计的对手探测恢复可执行决策策略，并衡量留出状态上的动作一致性及后续对抗价值。

  arXiv 2026 · 预印本 · [PDF](https://arxiv.org/pdf/2606.26094v1) · [代码](https://github.com/bethgelab/revenge-bench) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-revengebench/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 目标是固定的合成策略，不是完整游戏或自适应对手。有限评测状态上的动作一致性不能唯一确定源码，部分环境的方差较大。公开包未包含部分仅用于论文的绘图与消融实验；复现还需要 CodeClash、容器运行时和模型访问。

  **作者:** Babak Rahmani 等

  </details>

- [**SPRITE：从静态设计稿重建可用于游戏引擎的界面**](https://doi.org/10.1145/3772363.3798742)

  通过层级化 YAML、视觉定位、素材提取和 Unity UXML／USS 生成，将游戏界面截图转化为可编辑的引擎资源，并在精选游戏界面基准上评估，由三位资深 UI／UX 设计师进行审阅。

  CHI EA 2026 (poster/extended abstract) · 会议论文 · [PDF](https://baiyunshu.github.io/sprite.github.io/Source/chiea26-516.pdf) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-sprite-game-ui/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 生成的交互覆盖基本悬停、切换和点击行为，复杂时序与拖放逻辑仍不在范围内；半透明重叠元素或边界不明确的场景内界面可能处理失败。这是游戏界面原型重建，不是完整玩法重建；官方页面仍标注代码即将发布。

  **作者:** Yunshu Bai 等

  </details>

- [**WorldCoder：通过编写代码并与环境交互构建世界模型的基于模型的语言智能体**](https://papers.nips.cc/paper_files/paper/2024/hash/820c61a0cd419163ccbd2c33b268816e-Abstract-Conference.html)

  WorldCoder 根据环境交互和自然语言目标学习可执行的 Python 状态转移与奖励模型，利用已记录经验和乐观规划约束修正代码，并在 Sokoban、MiniGrid 与 ALFWorld 中研究迁移和任务求解。

  NeurIPS 2024 · 会议论文 · [PDF](https://papers.neurips.cc/paper_files/paper/2024/file/820c61a0cd419163ccbd2c33b268816e-Paper-Conference.pdf) · [代码](https://github.com/haotang1995/WorldCoder) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-worldcoder/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 假设环境动态具有确定性，状态为符号化的离散表示，并非从任意像素或二进制恢复游戏。与已观察转移一致及规划成功，不能证明完整引擎等价或所有未见状态上的正确性。评估针对有限范围的环境模型与规划，不涉及恢复原始源码或资产。

  **作者:** Hao Tang 等

  </details>

- [**通过蒙特卡洛树搜索引导大语言模型生成代码世界模型**](https://proceedings.neurips.cc/paper_files/paper/2024/hash/6f479ea488e0908ac8b1b37b27fd134c-Abstract-Conference.html)

  GIF-MCTS 根据环境的自然语言描述与离线状态转移轨迹生成可执行的 Python 状态转移和奖励模型，并利用预测反馈生成、改进和修复代码。CWMB 评估 18 个强化学习环境及后续规划；另一个实验使用简化的 Read to Fight Monsters 网格世界。

  NeurIPS 2024 · 会议论文 · [PDF](https://proceedings.neurips.cc/paper_files/paper/2024/file/6f479ea488e0908ac8b1b37b27fd134c-Paper-Conference.pdf) · [代码](https://github.com/nicoladainese96/code-world-models) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-code-world-models/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 假设环境动态具有确定性、状态完全可观测，并且描述足够详细；并非仅凭像素或二进制进行恢复。准确率使用合成过程中提供的回放转移，并结合规划回报评估，不能证明所有未见状态上的正确性或完整引擎等价。RTFM 在不同回合间固定手册内容，并让怪物保持静止。CWMB 也包含非游戏的控制与物理任务；部分规划回报未给出，复杂连续状态模型仍然困难。

  **作者:** Nicola Dainese 等

  </details>

<a id="papers-app-reconstruction"></a>
### 应用重建与分析

[↑ 论文主题](#papers) · [目录](#目录)

- [**UIOrchestra：通过多智能体系统将 UI 设计转换为高保真代码**](https://aclanthology.org/2025.findings-emnlp.150/)

  UIOrchestra 通过布局描述、代码生成及渲染图像比较三个智能体，将静态移动 UI 设计转换为 React/CSS。其 APPUI 基准包含 1,101 组经人工修订的代码与渲染图像，依据 12 类中的 165 款应用截图构建。参考代码为评测而重建，并非恢复出的原始应用源码。

  Findings of EMNLP 2025 · 会议论文 · [PDF](https://aclanthology.org/2025.findings-emnlp.150.pdf) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-uiorchestra/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 评测视觉、组件及代码相似度，不验证原生安装包执行、交互、后端行为或应用等价性。APPUI 参考图像来自对 iOS 截图所做重建的渲染结果；无法获取的图片／图标使用占位素材。人工研究由四位标注者评估 200 个样本。差异分析提示词忽略字号／字体差异及占位图像内容。未核实模型快照、渲染依赖或可复现的运行环境，亦未重新运行实验。

  **作者:** Chuhuai Yue 等

  </details>

- [**DeclarUI：以自动生成声明式界面代码连接设计与开发**](https://doi.org/10.1145/3715726)

  结合视觉组件提取、多模态模型、页面跳转图与迭代检查，从设计稿或截图重建多页面移动界面代码，并在 React Native、Flutter 和 ArkUI 上评测。

  Proceedings of the ACM on Software Engineering 2025 · 期刊论文 · [PDF](https://xinyi-hou.github.io/files/zhou2024bridging.pdf) · [代码](https://github.com/security-pride/DeclarUI) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-declarui/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 人员需审核并修正推断出的导航图。评测覆盖 50 组各含五页的界面；页面跳转覆盖率与编译成功不代表恢复了完整业务逻辑或后端。各框架结果存在差异，视觉指标也不能完全反映人眼感知的保真度。脚本与数据已公开，但核查的提交中未发现项目级许可证。

  **作者:** Ting Zhou 等

  </details>

- [**基于机器学习的移动应用图形用户界面原型生成**](https://doi.org/10.1109/TSE.2018.2844788)

  ReDraw 通过组件检测、CNN 控件类型分类及数据驱动的近邻层级组装，将截图或设计稿转换为原生 Android 图形界面原型。

  IEEE Transactions on Software Engineering 2020 · 期刊论文 · [PDF](https://arxiv.org/pdf/1802.02312v2) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-redraw/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 实现覆盖 15 类 Android 组件，每次生成单个屏幕；多屏需要人工组合，层级构建受采集时屏幕尺寸约束。评估关注外观和视图层级，不代表恢复原始应用逻辑或后端。实验以截图和重新制作的设计稿代替真实设计产物；本目录未独立复现实验。

  **作者:** Kevin Moran 等

  </details>

- [**pix2code：从图形用户界面截图生成代码**](https://doi.org/10.1145/3220134.3220135)

  学习从界面截图生成领域专用语言（DSL），再编译为原生 Android XML、iOS Storyboard 或网页 HTML/CSS 界面代码。

  EICS 2018 · 会议论文 · [PDF](https://arxiv.org/pdf/1705.07962v2) · [代码](https://github.com/tonybeltramelli/pix2code) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-pix2code/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 评测采用合成的截图与代码配对，每个平台含 1,500 个训练实例和 250 个测试实例。报告的准确率针对 DSL 词元，不代表完整应用或行为复现成功率。方法忽略文本标签内容，并以相同架构分别训练各平台模型；范围是布局、组件及其关系，不包括应用逻辑或后端恢复。仓库将其定位为教育用途的研究原型；本条目未对其较旧依赖进行运行测试。

  **作者:** Tony Beltramelli

  </details>

- [**从 UI 设计图到 GUI 骨架：辅助启动移动界面实现的神经机器翻译器**](https://doi.org/10.1145/3180155.3180240)

  UI2code 使用神经编码器—解码器，将移动 UI 图像转换为 Android 组件层级与布局骨架。论文评估了结构预测，并通过小规模开发者实验研究如何基于生成的骨架实现布局。

  ICSE 2018 · 会议论文 · [PDF](https://chunyang-chen.github.io/publication/ui2code.pdf) · [代码](https://github.com/ccywch/UI2code) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-ui2code/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 输出仅覆盖单张图像中的组件类型与层级；详细样式和文本仍需开发者补充。结构标记准确率以及针对五张截图、由八名参与者开展的实验，不能证明完整视觉保真度，也不代表恢复了导航、应用逻辑或后端。主数据集按截图划分；独立评估使用了 20 个未见应用的 1,208 张图像，提供了有限的泛化证据。

  **作者:** Chunyang Chen 等

  </details>

- [**Android 应用的统计式反混淆**](https://dl.acm.org/doi/10.1145/2976749.2978422)

  DeGuard 逆转 Android APK 中的布局混淆，为被 ProGuard 重命名的字段、方法、类和包预测原始名称。它基于 Soot 将应用表示为程序元素之间的依赖图，并保持 Android API 及其他未混淆名称不变；随后在从 1,684 个 F-Droid 应用学习的条件随机场上借助 Nice2Predict 进行 MAP 推断，并以约束保证重命名后的 APK 语义等价。在 100 个留出的、经 ProGuard 混淆的 F-Droid 应用上，与原始名称完全相同的比例从 13.3% 提升至 79.1%，第三方库预测的精确率为 91.3%、召回率为 91.0%。

  ACM CCS 2016 · 会议论文 · [PDF](https://files.sri.inf.ethz.ch/website/papers/deguard.pdf) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-deguard/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 仅处理布局（标识符）混淆。数据、控制流与密码学混淆、自定义字符串加密、反射以及基于 goto 的代码重排均不在逆转范围内；论文指出，其检查的大多数恶意样本同时使用了这些技术。基准为 100 个良性开源 F-Droid 应用，通过启用 ProGuard 且不修改其规则进行混淆，并以与原始名称完全一致作为评分标准，因此语义相近的名称也计为错误；被 ProGuard 删除的元素不计分。在其他混淆器或恶意软件上的准确率可能较低。第三方库依据包名启发式规则识别，共涵盖 133 个库，训练应用也可能导入相同的库。针对 49 个恶意软件家族的研究给出 Base64 解码器、位置信息处理等人工检查示例，未报告精确率。

  **作者:** Benjamin Bichsel 等

  </details>

- [**使用 REMAUI 逆向重建移动应用用户界面**](https://ieeexplore.ieee.org/abstract/document/7372013)

  利用 OCR、计算机视觉和布局启发式规则，从截图或设计位图重建原生 Android 界面代码，并使用来自 100 多款 Android 与 iOS 应用的 488 张截图评估视觉相似性和视图层级。

  ASE 2015 · 会议论文 · [PDF](https://c.csallner.org/papers/nguyen15reverse.pdf) · [代码](https://github.com/soumikmohianuta/pixtoapp) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-remaui/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 输出为 Android 界面代码；iOS 截图属于输入，不代表生成原生 iOS 代码。方法不恢复原始逻辑和后端行为，多屏切换当时仍属后续工作。OCR／布局启发式规则可能误识别内容。所链接的 REMAUI v2 仓库采用较旧依赖，并非已核实的 2015 年原始产物。

  **作者:** Tuan Anh Nguyen 等

  </details>

<a id="papers-firmware-analysis"></a>
### 固件分析与重托管

[↑ 论文主题](#papers) · [目录](#目录)

- [**面向 Linux 固件二进制的用户空间依赖感知重托管**](https://www.ndss-symposium.org/ndss-paper/user-space-dependency-aware-rehosting-for-linux-based-firmware-binaries/)

  FIRMWELL 通过运行初始化进程、定位阻塞依赖并修补缺失的系统层行为，重建 Linux 固件服务的执行环境。它结合容器化 QEMU-user 仿真与 QEMU-system 回退，并利用进程轨迹和二进制分析恢复目标服务所需的资源。

  NDSS 2026 · 会议论文 · [PDF](https://www.ndss-symposium.org/wp-content/uploads/2026-s249-paper.pdf) · [代码](https://github.com/qc9c/Firmwell) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-firmwell/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 评估针对选定网络服务，并非完整设备或硬件等价。HTTP 验收采用配置好的响应状态与错误内容检查；其他服务需要各自的判定标准。覆盖范围受解包、架构支持、初始化启发式规则和外设模型限制，符号执行路径爆炸、求解超时及复杂外设检查仍可能导致失败。论文中的修复策略避免补丁修改目标二进制；服务交互成功不能证明恢复了原始源码或全部设备功能。

  **作者:** Chuan Qin 等

  </details>

- [**使用 Penguin 进行以目标为中心的固件重托管**](https://www.ndss-symposium.org/ndss-paper/auto-draft-634/)

  Penguin 以提取出的固件文件系统为输入，通过静态分析生成可编辑的仿真变换配置（如文件修改、伪文件、NVRAM 值和网络接口），用于重托管嵌入式 Linux 固件。动态分析插件揭示运行失败，便于针对具体目标完善配置；配置最小化工具则找出可用的重托管所必需的变换。

  Workshop on Binary Analysis Research (BAR) 2025 · 会议论文 · [PDF](https://www.ndss-symposium.org/wp-content/uploads/bar2025-final10.pdf) · [代码](https://github.com/rehosting/penguin) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-penguin/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 面向嵌入式 Linux 固件，沿用 Firmadyne 和 FirmAE 的思路，采用替换内核的整机仿真；实现支持 x86、ARM 和 MIPS，并依赖 Linux 系统调用 ABI。与 FirmAE 对比时，判定成功的标准是有进程绑定 80 或 443 端口，更严格的检查是 HTTP 返回非空响应；作者指出两者都不代表系统功能完整。比 FirmAE 多出 75% 的结果由作者在其自建语料（13,649 个取自厂商网站的镜像）上报告。完善配置仍需分析人员参与；运行结果不完全确定，作者对配置最多重复运行十次。该工作构建的是分析环境，不代表忠实复现设备或恢复源代码。

  **作者:** Andrew Fasano 等

  </details>

- [**Fuzzware：利用精确的 MMIO 建模提升固件模糊测试效果**](https://www.usenix.org/conference/usenixsecurity22/presentation/scharnowski)

  重托管单体 ARM Cortex-M 固件以开展模糊测试，利用局部符号执行为内存映射 I/O 访问建模，使输入变异集中于影响固件逻辑的值。

  USENIX Security 2022 · 会议论文 · [PDF](https://www.usenix.org/system/files/sec22-scharnowski.pdf) · [代码](https://github.com/fuzzware-fuzzer/fuzzware) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-fuzzware/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 面向 Cortex-M3/M4 的产物需要配置内存映射，且不会自动为 DMA 建模。对硬件的抽象可能产生真实设备上不可能出现的崩溃。该工作构建分析环境，不代表恢复原始源码或忠实重建完整设备。

  **作者:** Tobias Scharnowski 等

  </details>

- [**FirmAE：面向动态分析的物联网固件大规模仿真**](https://doi.org/10.1145/3427228.3427294)

  在 Firmadyne 基础上，针对启动、网络、NVRAM、内核行为及其他运行失败加入经验性干预，使 Linux 路由器与 IP 摄像机固件的 Web 服务能够运行并接受动态分析。

  ACSAC 2020 · 会议论文 · [PDF](https://syssec.kaist.ac.kr/pub/2020/kim_acsac2020.pdf) · [代码](https://github.com/pr0v3rbs/FirmAE) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-firmae/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 仲裁式干预会有意改变执行过程，目标是运行 Web 界面，而非完整复现物理设备行为。评测覆盖路由器与 IP 摄像机的 ARM 小端、MIPS 小端及大端固件；启发式规则可能不适用于未见过的设备或配置。该方法复用固件二进制，并不恢复其源码。

  **作者:** Mingeun Kim 等

  </details>

- [**HALucinator：通过抽象层仿真实现固件重托管**](https://www.usenix.org/conference/usenixsecurity20/presentation/clements)

  HALucinator 识别单体 ARM Cortex-M 固件中的硬件抽象库函数，并用人工编写的 Python 处理函数和外设模型替换它们，从而重托管固件。LibMatch 定位库接口；QEMU/Avatar2 实现支持交互式输入输出，与论文关联的 HAL-fuzz 变体则使用 AFL-Unicorn 进行模糊测试。

  USENIX Security 2020 · 会议论文 · [PDF](https://www.usenix.org/system/files/sec20-clements.pdf) · [代码](https://github.com/embedded-sec/halucinator) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-halucinator/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** LibMatch 需要可获取的硬件抽象层或库，以及足够相似的编译环境；编译器差异与内联会限制匹配效果。重托管还需要 QEMU 支持的架构、固件内存布局、拦截地址及人工编写的处理函数和模型。未建模的直接硬件访问可能在读取时返回零、在写入时被忽略；简化的时序与外设行为不能证明硬件等价。作者的重托管与模糊测试演示不代表普遍覆盖所有固件、完整重建设备或恢复原始源代码。

  **作者:** Abraham A Clements 等

  </details>

- [**面向基于 Linux 的嵌入式固件的自动化动态分析**](https://doi.org/10.14722/ndss.2016.23415)

  Firmadyne 对路由器、IP 摄像头等联网商用设备中基于 Linux 的固件进行爬取、提取与仿真。它以预先构建并插桩的小端 ARM 及小端、大端 MIPS 内核替换厂商内核，在 QEMU 全系统仿真中配合用户态 NVRAM 库启动提取出的文件系统，推断网络配置，再运行自动化分析，包括 60 个已知漏洞利用和 14 个新发现的漏洞利用。作者从 42 家厂商的 23,035 个固件映像中提取出 9,486 个，并报告在 1,971 个网络可达映像中有 887 个至少受一个所选漏洞利用影响。

  NDSS 2016 · 会议论文 · [PDF](https://www.ndss-symposium.org/wp-content/uploads/2017/09/towards-automated-dynamic-analysis-linux-based-embedded-firmware.pdf) · [代码](https://github.com/firmadyne/firmadyne) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-firmadyne/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 该工作面向小端 ARM 及小端、大端 MIPS 上基于 Linux 的固件，这些平台占数据集的 90.8%；x86、VxWorks 及其他实时操作系统不在系统支持范围内。其预构建内核不加载厂商的树外内核模块，因此无法检查厂商内核及模块，插桩仿真也不等同于设备原有行为。仿真流程逐级大幅收窄：在初始仿真成功的 8,591 个映像中，2,797 个推断出网络配置，1,971 个能响应 ping。论文列出的原因包括 NVRAM 语义、网络接口命名，以及 ARM 平台仅仿真一个以太网设备等。系统不区分 WAN 与 LAN 端口，因此不能确认可否远程利用；结果按固件映像而非独立产品计数，并受厂商构成偏差影响。本收录中已有的 FirmAE 扩展了 Firmadyne 以解决此类仿真失败；这些 2016 年的比率并非当前的仿真数据。

  **作者:** Daming D. Chen 等

  </details>

<a id="papers-protocol-analysis"></a>
### 协议推断与分析

[↑ 论文主题](#papers) · [目录](#目录)

- [**ICEPRE：基于数据驱动混合符号执行的工控协议逆向工程**](https://dl.acm.org/doi/10.1145/3728982)

  在二进制协议解析器中沿具体报文引导的路径分析，再进行符号化重放，提取字节级数据流以推断报文字段边界。它依据保持原值的运算和相似处理轨迹合并字节。作者在四种公开工控协议、每组 1,000 条报文的数据集上，报告平均边界 F1 分数为 0.76、字段完美分割率为 0.67。

  Proceedings of the ACM on Software Engineering (ISSTA 2025) · 期刊论文 · [PDF](https://dl.acm.org/doi/pdf/10.1145/3728982) · [代码](https://github.com/QYbPtqyb/ICEPRE) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-icepre/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 恢复的是报文语法，并非字段语义、协议状态机或端点等价性。方法需要二进制、加载配置，以及正确识别的初始化、输入和解析函数；尤其在缺少符号时，仍需人工筛选。不支持加密协议和位级字段；被忽略或仅被复制的字节可能遭到错误合并。完美分割率衡量两端边界均正确的字段。量化实验使用四种公开协议的 50 条与 1,000 条报文集合；另行开展的专有协议研究覆盖五个固件目标中的三种协议，在三台设备上进行交互检查，并由人工建立真实标签。这些检查不能证明完整设备行为。

  **作者:** Yibo Qu 等

  </details>

- [**BinPRE：增强基于二进制分析的协议逆向工程中的字段推断**](https://dl.acm.org/doi/10.1145/3658644.3690299)

  根据受插桩监测的服务端二进制及输入报文，推断协议报文的字段边界与语义。BinPRE 按处理字节的指令操作符进行分组，使用检测器识别字段类型和功能，再借助相似报文细化结果。作者在八种协议、每种 50 条报文上报告平均字段完美分割率为 0.73，类型／功能推断的 F1 分数为 0.74／0.81。

  ACM CCS 2024 · 会议论文 · [PDF](https://tingsu.github.io/files/ccs24-BinPRE.pdf) · [代码](https://github.com/ecnusse/BinPRE) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-binpre/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 研究对象是字段推断，不是恢复协议状态机或端点的完整行为。方法需要能够访问并插桩的实现及运行时的报文处理；仅有被动捕获数据并不足够。完美分割率统计被精确分割的字段占全部真实字段的比例，而非完整恢复的协议比例。检测器库覆盖五种语义类型与六种功能。字节级污点分析无法准确解析位标志，也不确立未执行行为。真实标签依据 Wireshark 解析器与协议规范构建；三种二进制分析基线由作者重新实现。报告的模糊测试改进属于下游评估，不是实现等价性的证明。

  **作者:** Jiayi Jiang 等

  </details>

- [**DynPRE：基于动态推断的协议逆向工程**](https://www.ndss-symposium.org/ndss-paper/dynpre-protocol-reverse-engineering-via-dynamic-inference/)

  DynPRE 以捕获的客户端—服务端流量为起点，再与在线协议服务端交互，推断报文格式与类型。它检测 Cookie 等会话特定标识符并实时改写，使重放的请求保持有效；随后发送字节级探测请求，以服务端响应作为字段识别的语义反馈，对响应进行对齐分析，并通过请求—响应映射细化格式，同时识别报文类型。作者在 12 种协议、规模分别为 10、100 与 1,000 条报文的数据集上，报告平均字段完美分割率为 0.50、报文类型 V-measure 为 0.94，而 Netzob、NetPlier、FieldHunter、BinaryInferno 与 NEMESYS 的完美分割率为 0.15–0.31。

  NDSS 2024 · 会议论文 · [PDF](https://www.ndss-symposium.org/wp-content/uploads/2024-83-paper.pdf) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-dynpre/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 该方法需要捕获流量以及可被反复查询的可达服务端，无法仅凭被动捕获流量工作。探测会改变服务端状态：每次探测都会新建会话，但具有全局状态的协议（如 IoT 设备的开关状态）仍可能降低反馈质量。在 1,000 条报文的数据集上，单次分析平均耗时 259 分钟，平均发起 50,344 次连接、交换约 398 万条报文，因此低速或限流的服务端会降低效率。在开源评测环境中，加密与认证机制均被关闭；IoT 案例研究中的加密流量则借助设备私钥解密。带校验和的协议需要额外的校验和逆向步骤，且仅在 ICMP 上演示。格式真实标签来自 tshark 解析器，报文类型则来自人工阅读协议文档。针对五台设备的 IoT 案例研究检验生成的报文能否触发设备行为，而非规范是否完整。状态机推断沿用已有方法，并未作为贡献加以评估。

  **作者:** Zhengxiong Luo 等

  </details>

- [**从网络协议实现提取精确格式规范及其安全应用**](https://dl.acm.org/doi/10.1145/3576915.3616614)

  NetLifter 将可获取源码的 C 协议解析器静态转换为 BNF 风格的报文文法及报文字段之间的一阶逻辑约束。它分析经过标注的 LLVM 位码，结合抽象格式图、局部路径敏感分析、展开与重排序。所得字段边界、约束与名称可用于报文生成及解析器构建。

  ACM CCS 2023 · 会议论文 · [PDF](https://qingkaishi.github.io/public_pdfs/CCS23.pdf) · [代码](https://github.com/qingkaishi/netlifter) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-netlifter/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 需要源码／LLVM 中间表示及报文缓冲区、长度标注，并非对闭源二进制或仅凭流量进行恢复。论文面向常见的自顶向下 C 解析器，不支持 C++、内联汇编及缺少源码的库。指针和循环分析仍有近似；可识别校验和字段，但部分校验和约束会被省略，实现中忽略的字段也可能遗漏。精确率／召回率在选定的十种协议上进行人工核对。报告的模糊测试采用每次三小时、重复二十次的实验，并绕过校验和检查。方法推断的是格式，而非协议状态机或实现等价性的证明。

  **作者:** Qingkai Shi 等

  </details>

- [**BinaryInferno：面向二进制报文格式字段推断的语义驱动方法**](https://www.ndss-symposium.org/ndss-paper/binaryinferno-a-semantic-driven-approach-to-field-inference-for-binary-message-formats/)

  无需对可执行程序插桩，即可从静态报文样本推断部分二进制报文格式。专用检测器识别浮点数、时间戳、长度、熵边界和序列化模式，再通过基于图的集成步骤协调各自的描述。作者对十种协议的样本开展评估，在每组 1,000 条报文且不使用分析者先验的设置下，报告顶层字段边界的精确率为 0.69、召回率为 0.73、假阳性率为 0.04。

  NDSS 2023 · 会议论文 · [PDF](https://www.ndss-symposium.org/wp-content/uploads/2023/02/ndss2023_s131_paper.pdf) · [代码](https://github.com/binaryinferno/binaryinferno) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-binaryinferno/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 假设数据无错误、未经压缩或加密、按字节对齐，并推断起始偏移一致的共有字段或载荷区域。可选字段、联合类型字段及不支持的序列化模式仍未解决；样本多样性会影响结果。26 组封装载荷测试集依据已知真实报文类型预先分组，并非自动发现。真实标签合并了在整个样本中均保持常量的相邻字段；文中注明的平均值排除了没有推断结果的样本。BI+ 额外使用给定的字节序和捕获时间范围。这些是字段边界结果，不代表完整语义恢复、协议状态推断或行为等价。

  **作者:** Jared Chandler 等

  </details>

- [**越仔细观察，学到的越多：用于协议状态机学习的灰盒方法**](https://doi.org/10.1145/3548606.3559365)

  StateInspector 将主动消息查询与运行时内存快照结合起来，学习协议的 Mealy 状态机，无需目标实现的源代码。它识别可能决定状态的堆内存位置，并通过污点分析与混合执行合并状态；作者在 TLS 1.2 和 WPA/2 实现上进行了评估。

  ACM CCS 2022 · 会议论文 · [PDF](https://tomchothia.gitlab.io/Papers/greyboxstatelearning_ccs2022.pdf) · [代码](https://github.com/ChrisMcMStone/state-inspector) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-stateinspector/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 假设协议可抽象为有限 Mealy 状态机、已知输入字母表能到达相关状态，且决定状态的内存位于堆上并可由初始化查询触及。状态合并依赖所配置的搜索深度与符号执行前瞻上限。缺失的输入或存储在其他位置的状态可能导致行为未被建模；测试驱动程序构造的错误消息、响应抽象方式和超时也可能产生误导性转移。学习出的模型与有界检查不能证明实现完全等价，也不恢复未知消息格式或重建应用源代码。

  **作者:** Chris McMahon Stone 等

  </details>

- [**基于自动机学习的蓝牙设备指纹识别与分析**](https://doi.org/10.1007/s10703-023-00425-y)

  通过主动自动机学习，为实体外设上的低功耗蓝牙（BLE）协议实现推断 Mealy 状态机模型。运行 SweynTooth 衍生固件的 nRF52840 中心设备发送抽象 BLE 输入，并以错误处理、重复查询和缓存应对丢包与不确定的响应。作者学习了六款设备的连接过程模型和其中三款的传统配对（legacy pairing）模型，并利用模型差异识别各设备的 SoC。

  Formal Methods in System Design 2022 · 期刊论文 · [PDF](https://arxiv.org/pdf/2211.16074v2) · [代码](https://github.com/apferscher/ble-learning) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-ble-automata-learning/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 模型受所选抽象输入字母表限制，仅覆盖连接过程和传统配对；不推断报文格式，安全配对留待后续研究。等价性仅以每个状态少量的一致性测试近似检验，因此模型只是假设而非证明。其中一款 SoC 只能缩减输入字母表后学习，两款设备从已建立连接的状态开始学习，部分配对实验还需人工硬重置设备。所得指纹识别序列仅适用于受测 SoC。除一条会导致设备崩溃的输入序列外，作者未在学习所得模型中发现安全漏洞。

  **作者:** Andrea Pferscher 等

  </details>

- [**NetPlier：基于报文记录的概率网络协议逆向工程**](https://www.ndss-symposium.org/ndss-paper/netplier-probabilistic-network-protocol-reverse-engineering-from-message-traces/)

  通过多序列比对与概率式关键字段推断，按类型对网络报文聚类，并在十种协议上评测及开展后续格式与状态机分析。

  NDSS 2021 · 会议论文 · [PDF](https://www.ndss-symposium.org/wp-content/uploads/ndss2021_4A-5_24531_paper.pdf) · [代码](https://github.com/yapengye/NetPlier) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-netplier/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 需要未加密的报文记录，无法恢复从未出现的报文类型。较大的比对、亚字节关键字段及单向流量可能降低准确性。格式／有限状态机推断属于下游评测而非主要贡献；一个案例中的状态语义由人工标注。这些模型不能证明已完整重建应用／设备。

  **作者:** Yapeng Ye 等

  </details>

- [**无线协议自动逆向工程**](https://www.usenix.org/conference/woot19/presentation/pohl)

  从解调后的物理层捕获数据推断专有无线协议的报文格式：先依据前导码和同步字对齐报文，再结合 RSSI 与专用引擎标注长度、地址、序列号和校验和字段，并可利用已知地址或字段位置等先验信息。

  13th USENIX Workshop on Offensive Technologies (WOOT 19) 2019 · 会议论文 · [PDF](https://www.usenix.org/system/files/woot19-paper_pohl.pdf) · [代码](https://github.com/jopohl/urh) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-wireless-protocol-re/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 仅推断报文格式，即前导码、同步字、长度、地址、序列号和校验和；协议状态机推断以及开关位等载荷字段不在研究范围内。方法假设报文为紧凑的二进制格式，且每条报文只有一个前导码和同步字。准确率在 8 个生成协议上评测；3 份真实智能家居捕获（EnOcean、Homematic BidCoS 及 RWE Smarthome 使用的 eQ-3 协议）用于性能测试，作者也承认这是有限的测试集。

  **作者:** Johannes Pohl 等

  </details>

- [**NEMESYS：通过分析单条报文的内在结构逆向推断网络报文语法**](https://www.usenix.org/conference/woot18/presentation/kleber)

  根据单条二进制协议报文内比特一致性的变化，推断近似字段边界，并提出格式匹配分数，将推断的分段结果与已知协议解析器进行比较。

  12th USENIX Workshop on Offensive Technologies (WOOT 18) 2018 · 会议论文 · [PDF](https://www.usenix.org/system/files/conference/woot18/woot18-paper-kleber.pdf) · [代码](https://github.com/vs-uulm/nemesys) · [完整条目与引用](https://awesomerea.org/zh/papers/paper-nemesys/)

  <details>
  <summary>范围与发表信息</summary>

  **范围与限制:** 需要明文载荷。评测覆盖 DNS、DHCP 和 NTP，并针对各协议调节参数。方法无法推断单字节字段；全零字段、字符序列和伪随机值可能导致误差。FMS 验证需要已知字段边界。输出是近似报文分段，不是字段语义、状态机或完整应用／设备行为。

  **作者:** Stephan Kleber 等

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
