<p align="center">
  <a href="https://awesomerea.org/"><img src="assets/featured-by-awesome-rea-compact.svg" alt="Featured by Awesome REA" width="200" height="48"></a>
</p>

# Awesome Reverse Engineering Anything

An independent collection of tools, case studies and research for websites, games, apps, native binaries, firmware and communication protocols.

**English** · [简体中文](README.zh-CN.md)

<a href="https://awesomerea.org/"><img src="assets/readme-banner.svg" alt="Awesome Reverse Engineering Anything — tools, cases and papers across six reverse-engineering domains" width="960"></a>

<!-- BEGIN GENERATED BADGES -->
[![resources: 289](https://img.shields.io/badge/resources-289-53309C?style=flat-square&labelColor=303447)](https://awesomerea.org/resources/) [![cases: 147](https://img.shields.io/badge/cases-147-53309C?style=flat-square&labelColor=303447)](https://awesomerea.org/cases/) [![papers: 58](https://img.shields.io/badge/papers-58-53309C?style=flat-square&labelColor=303447)](https://awesomerea.org/papers/) [![Catalog checks](https://github.com/reacher-z/Awesome-REA/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/reacher-z/Awesome-REA/actions/workflows/validate.yml) [![license: MIT](https://img.shields.io/badge/license-MIT-606779?style=flat-square&labelColor=303447)](LICENSE) [![website: awesomerea.org](https://img.shields.io/badge/website-awesomerea.org-6235B5?style=flat-square&labelColor=303447)](https://awesomerea.org/)
<!-- END GENERATED BADGES -->

**[Search & filter](https://awesomerea.org/)** · **[Browse cases](https://awesomerea.org/cases/)** · **[Research papers](https://awesomerea.org/papers/)** · **[HTML survey](https://awesomerea.org/survey/)**

**Source review does not imply runtime verification.** [Review method](https://awesomerea.org/about/)

## Contents

<!-- BEGIN GENERATED CONTENTS -->
**Tools and cases by target**

- [Website](#website) (18) · [Game](#game) (129) · [App](#app) (44)
- [Native Binary](#native-binary) (20) · [Firmware and Hardware](#firmware) (13) · [Protocol](#protocol) (12)

**Research and workflows**

- [Papers](#papers) (58) · [Agents and MCP](#agents-and-mcp) (21) · [References and Learning](#references-and-learning) (25)

**More ways to browse**

- [All cases](https://awesomerea.org/cases/) (147) · [Related Collections](#related-collections) (4) · [Full Repository Index](#full-repository-index) (2,836)
<!-- END GENERATED CONTENTS -->

## Find by task

| Task | Relevant sections |
| --- | --- |
| Inspect a website or app interface | [Websites](#website) · [Apps](#app) |
| Rebuild a game or check matching code | [Games](#game) · [Game cases](https://awesomerea.org/cases/#cases-game) |
| Analyze compiled code or recover symbols | [Native binaries](#native-binary) · [Agents and MCP](#agents-and-mcp) |
| Investigate firmware or device protocols | [Firmware](#firmware) · [Protocols](#protocol) |
| Compare methods and evaluation evidence | [Papers](#papers) · [Survey comparisons](https://awesomerea.org/survey/#comparative-studies) |

<a id="resource-catalog"></a>
## Resources

Names link to original sources. Each description is followed by its type, relationship and a “Requirements & evidence” link for prerequisites, limitations and review sources.

Each resource appears once under its main purpose. Cases reuse these entries; [papers are listed separately](#papers). [Browse the resource directory](https://awesomerea.org/resources/).

REA labels refer to the separate [upstream CLI and MCP project](https://github.com/morluto/rea). Listing does not imply REA integration. [About this independent collection](#about).

<!-- BEGIN GENERATED CATALOG -->
<a id="website"></a>
### Website

[↑ Contents](#contents)

#### Case studies

- [**Dinosaur runner: recovering one acceleration rule**](https://github.com/morluto/rea/blob/c360cfcd6d7901514b16dd6113eba2e0b0fdf422/website/evidence/calculator-and-dino.md#dinosaur-speed)

  REA’s documented teaching case inspects the HTTP t-rex-runner edition and reconstructs its speed-update rule. A separate controlled original-game check and a new demonstration compare update counts, including the floating-point step that crosses the nominal speed threshold.

  Case study · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-dinosaur-speed-case/)

- [**rauchg.com: rebuilding an RSC blog from captured Flight output**](https://github.com/boyang-hu/website-rebuild-skill/blob/ac60c9d8a2ab40045a89b5403c3457f1404e92b3/skills/website-rebuild/references/rsc-reconstruction.md)

  Documents a website-rebuild-skill case that decodes browser-delivered React Server Component Flight streams, reconstructs a buildable Next project and compares its output with a captured site. The reported rauchg.com campaign uses route-tree comparison and module-reference mapping; the new server source is inferred from observable output.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/rauchg-rsc-reconstruction-case/)

- [**BaoCut Slides: adapting an interactive web editor**](https://github.com/JimLiu/baocut/tree/b8585e0c8d7a82bdee9f0ed019cf6edb075e41c1/packages/slides-runtime)

  Documents BaoCut’s interactive slide editor, whose author says the implementation draws on Claude Slides. It adds a local deck store, HTML/CSS compiler and annotation-to-agent bridge for browser and desktop hosts; the design reports a Web-flow check, without establishing original backend recovery or full behavioral parity.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/baocut-slides-editor-case/)

- [**REA in Claude Code: an isolated static-analysis A/B trial**](https://zenn.dev/keigoly/articles/8738d8d241b5a1)

  A Japanese field report connects REA 6.4.0 to Claude Code in a separate project directory, denies 43 of its 170 tools and common shell launch forms, and compares REA-enabled and REA-disabled runs on two real tasks: an Electron terminal’s packaged files and a saved HAR capture. Both arms answered correctly, while the REA arm took up to 2.00× the time and 1.67× the API-equivalent cost. It is an analysis-evaluation and safety-configuration case, not a reconstruction.

  Case study · Mixed workflow · [Requirements & evidence](https://awesomerea.org/resources/rea-claude-code-isolated-ab-case/)

- [**BaoCut Design: porting reconstructed canvas and design-system editors**](https://github.com/JimLiu/baocut/tree/7aa049e82e1367da013b7aba80f0b79033fa04ad/packages/design-runtime)

  Documents BaoCut’s design-canvas and design-system editors, which the project says it ported 1:1 from TypeScript reconstructions of Claude Design’s editors and hosts in agent sessions with annotation and export. Its runtime notes record identifier fixes checked against the original scripts and a structural comparison matching 19,111 of 20,463 canvas main-page functions. Unreviewed differences, the unpublished reconstruction record and reuse rights remain open; no hosted-backend recovery is claimed.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/baocut-design-canvas-case/)

#### Tools, projects and integrations

- [**webcrack**](https://github.com/j4k0xb/webcrack)

  Improves JavaScript readability by reversing supported obfuscation patterns and unpacking webpack/Browserify bundles.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/webcrack/)

- [**humanify**](https://github.com/jehna/humanify)

  Rename identifiers in minified JavaScript with LLM-suggested names, applied through scope-aware AST rewriting so the program structure stays unchanged. The new names are model suggestions, not recovered original identifiers.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/humanify/)

- [**WABT**](https://github.com/WebAssembly/wabt)

  WebAssembly tools for binary-to-text conversion, section inspection, validation, interpretation and C translation.

  Tool · WebAssembly · [Requirements & evidence](https://awesomerea.org/resources/wabt/)

- [**wasm-tools**](https://github.com/bytecodealliance/wasm-tools)

  Bytecode Alliance CLI and Rust libraries for inspecting WebAssembly modules, metadata, components and WIT interfaces.

  Tool · WebAssembly · [Requirements & evidence](https://awesomerea.org/resources/wasm-tools/)

- [**Chrome DevTools MCP**](https://github.com/ChromeDevTools/chrome-devtools-mcp)

  Connect an agent to Chrome for live page inspection, network debugging, and performance traces.

  Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/chrome-devtools-mcp/)

- [**mitmproxy**](https://github.com/mitmproxy/mitmproxy)

  Inspect and record HTTP traffic with an interactive proxy, web interface, or scriptable command-line tools.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/mitmproxy/)

- [**Playwright MCP**](https://github.com/microsoft/playwright-mcp)

  Drive browser interactions through structured accessibility snapshots to investigate reproducible web behavior.

  Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/playwright-mcp/)

- [**Burp Suite MCP Server**](https://github.com/PortSwigger/mcp-server)

  PortSwigger's Burp Suite extension serves an MCP endpoint, plus a packaged stdio proxy, so agents can query proxy HTTP and WebSocket history, send HTTP/1.1 or HTTP/2 requests, and open Repeater or Intruder tabs.

  Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/burp-suite-mcp-server/)

- [**Wakaru**](https://github.com/pionxzh/wakaru)

  Recover readable modules from shipped JavaScript bundles by reversing recognized minifier and transpiler patterns. Supports bundle splitting and modern-syntax recovery for inspecting production frontend code.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/wakaru/)

- [**Spectral**](https://github.com/spectral-mcp/spectral)

  Analyze captured application HTTP traffic with an LLM to generate MCP tools, OpenAPI 3.1 specifications, or GraphQL schemas. Generated tools call the observed API directly after capture and authentication setup.

  Integration · Independent agent · [Requirements & evidence](https://awesomerea.org/resources/spectral-mcp/)

- [**jsdeob-workbench**](https://github.com/Owl4444/jsdeob-workbench)

  Inspect JavaScript ASTs and variable scopes while building visual chains of Babel transforms. Save analysis projects and reusable plugins to iteratively simplify obfuscated scripts.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/jsdeob-workbench/)

- [**Browser Reverse Engineering Toolkit**](https://github.com/Dvurechensky/Browser.Reverse.Engineering.Toolkit)

  Capture browser-session evidence, crawl websites in a persistent Chromium session, and generate offline architecture/API reports plus OpenAPI, SDK and mock-server drafts from saved captures.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/browser-reverse-engineering-toolkit/)

- [**screenshot-to-code**](https://github.com/abi/screenshot-to-code)

  Generate HTML/CSS, Tailwind, React, Vue, Bootstrap or Ionic front-end code from screenshots, mockups, Figma designs or screen recordings with multimodal models; an optional headless-browser preview lets the model check its rendered output. The result is a visual reconstruction of the interface, not recovered original source or backend behavior.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/screenshot-to-code/)

<a id="game"></a>
### Game

[↑ Contents](#contents)

#### Case studies

- [**DX-Ball: reconstruct sound panning**](https://rea.tools/showcase/dx-ball/)

  Recover one sound-pan function from instructions and constants; upstream cites 3,205 cases and a 63-byte match.

  Case study · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-dxball-case/)

- [**TH04: recover a DOS bullet-ring helper**](https://rea.tools/showcase/th04/)

  Inspect a 16-bit PC-98 DOS helper and relate its angle calculation to a pinned reconstruction and historical compiler checks.

  Case study · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-th04-case/)

- [**Super Mario 64 DS: matching decompilation with relocation checks**](https://github.com/tangosdev/sm64ds-decomp)

  Reconstructs Super Mario 64 DS functions as C/C++ and permitted assembly primitives, comparing compiled output with a user-supplied cartridge dump. Independent relocation-destination checks strengthen the matching gate; integration into the PC port is tracked separately.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/sm64ds-decomp-case/)

- [**GoldenEye 007: an agent-assisted native port from a decompilation**](https://github.com/jkdansereau/goldeneye-pc-port)

  Builds a native PC port on the existing GoldenEye 007 decompilation, with a host platform layer and assets extracted from the user’s ROM. The project documents agent collaboration, rendering comparisons, playtest scope and unresolved platform support.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/goldeneye-pc-port-case/)

- [**ssbu-recomp: static recompilation with explicit mode limits**](https://github.com/Denkishi/ssbu-recomp)

  Translates Super Smash Bros. Ultimate 13.0.4 AArch64 code ahead of time and supplies a Windows runtime with Vulkan/OpenGL rendering. It also reconstructs selected fighter scripts as editable C++ and compares translated/source behavior through differential and deterministic tests.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/ssbu-recomp-case/)

- [**KartPad: platform integration for a Mario Kart Wii recompilation**](https://github.com/chrissotraidis/kartpad)

  Builds Apple and Android integration around WiiCompiled’s ahead-of-time translation of Mario Kart Wii, with native graphics, input and optional Retro Rewind support. Its status and rights documents distinguish platform acceptance, unresolved device defects and game-content requirements.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/kartpad-case/)

- [**BattleShip: an AI-assisted Super Smash Bros. native port**](https://github.com/JRickey/BattleShip)

  Ports the existing Super Smash Bros. N64 decompilation using libultraship and Torch. The author’s earlier README describes agent-built graphics/audio comparison tools and differential debugging against emulator behavior, rather than claiming AI recovered the game from a cartridge without prior community work.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/battleship-port-case/)

- [**Agent decompilation: a byte-matching retrospective**](https://momo5502.com/posts/2026-10-09-game-decompilation/)

  Maurice Heumann describes replacing plausible-looking agent output with compiler-based checks of reconstructed functions, relocations, data and types. The retrospective reports 99% function presence and 83% of all functions byte-exact, while keeping the reconstruction code private.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/agent-decompilation-oracle-case/)

- [**Snowboard Kids 2: an LLM-assisted N64 matching decompilation**](https://github.com/cdlewis/snowboardkids2-decomp)

  A public matching decompilation of the N64 game Snowboard Kids 2, begun in 2024 with community decompilation tools. The author’s dated posts document Claude, Codex and GLM workflows, including headless one-shot loops, similarity-based function scheduling and hook-guarded, hash-checked builds, through a reported complete function match.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/snowboardkids2-decomp-case/)

- [**IsaacRecomp: translating Flash game bytecode to native C++**](https://github.com/whylurking/IsaacRecomp)

  Translates The Binding of Isaac’s Flash AVM1 bytecode into C++ functions and supplies a native rendering/input runtime. The project reads graphics and audio from the user’s original game and documents deterministic input, headless runs and screenshot regression checks.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/isaacrecomp-case/)

- [**Nanolathe: a documented Total Annihilation engine reimplementation**](https://github.com/nanolathe-gg/nanolathe)

  Reimplements a Total Annihilation-compatible strategy-game engine in Go, with public file-format research and separate gameplay profiles. It distinguishes intended retail 3.1 behavior from community-patch research and deliberate modern changes, and separates synthetic checks from tests requiring original game data.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/nanolathe-case/)

- [**TH08: exact-source reconstruction and separately tested ports**](https://github.com/N0zoM1z0/th08)

  Reconstructs the original Japanese Touhou 8 version 1.00d against its binary and original compiler, then adapts the recovered code for other platforms. Source presence, strict function matching, whole-executable identity and playable-port checks are recorded as different milestones.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/th08-reconstruction-case/)

- [**Zelda 64: Recompiled — a native Majora’s Mask port without a full source decompilation**](https://github.com/Zelda64Recomp/Zelda64Recomp)

  Uses N64Recomp to translate Majora’s Mask into a native application and RT64 for rendering. The project separates static recompilation from source decompilation while reusing decompilation headers and selected functions for patches and enhancements.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/zelda64recomp-case/)

- [**OpenGOAL: recovering GOAL code and rebuilding the Jak games**](https://github.com/open-goal/jak-project)

  Reconstructs readable GOAL code from the original Jak binaries and compiles it with a new GOAL compiler for modern PCs. Its workflow combines a specialized decompiler, manually supplied type information, asset extraction and an interactive development runtime.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/opengoal-jak-case/)

- [**LEGO Island: source reconstruction with separately reported exact rebuilds**](https://github.com/isledecomp/isle)

  Reconstructs the English LEGO Island 1.1 source for its original 32-bit Windows target. The project distinguishes function-comparison reports, ReproBit’s reported byte-identical retail rebuilds and ordinary developer builds; its modern portable adaptation is a separate repository.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/lego-island-decomp-case/)

- [**Snowball War: a bounded REA-assisted minigame reconstruction**](https://github.com/tuunanet/rea-ski-or-die-reconstruction)

  The author uses REA’s Ghidra workflow to investigate the DOS Ski or Die binary, document Snowball War rules and rebuild that one minigame in Rust with SDL2. The public notes distinguish recovered tables and mechanics from approximations and deliberate presentation changes.

  Case study · Mixed workflow · [Requirements & evidence](https://awesomerea.org/resources/snowball-war-rea-case/)

- [**SpaceCadetPinball: decompiled game logic adapted to SDL2**](https://github.com/k4zmu2a/SpaceCadetPinball)

  Converts the reverse-engineered Space Cadet pinball game into compilable C++ for desktop platforms. The README identifies the Windows XP executable and public PDB, a Full Tilt executable, and the work of recovering structures, naming variables and adapting the decompiled routines.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/space-cadet-pinball-case/)

- [**Super Mario 64: ROM reconstruction with explicit comparison gates**](https://github.com/n64decomp/sm64)

  Reconstructs Super Mario 64 source for Japanese, North American, European, Shindou and iQue releases. Its build files distinguish original-ROM hash comparison from nonmatching or modified configurations, while source naming and documentation remain ongoing.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/sm64-decomp-case/)

- [**Unleashed Recompiled: translating Xbox 360 game code and shaders**](https://github.com/hedge-dev/UnleashedRecomp)

  Builds an unofficial Sonic Unleashed PC port by statically recompiling Xbox 360 PowerPC code with XenonRecomp and Xenos shaders with XenosRecomp. The port adds modern display and modding options while documenting original-engine limits and remaining compatibility issues.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/unleashed-recompiled-case/)

- [**OpenMW: replacing Morrowind’s engine while reusing original content**](https://github.com/OpenMW/openmw)

  Provides an independent engine for playing Morrowind and an alternative editor, OpenMW-CS. It loads original game content through its own runtime and documents script and mod compatibility differences; it is an engine replacement rather than a recovered Bethesda source tree.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/openmw-engine-case/)

- [**REDRIVER2: reconstructing Driver 2 through a PlayStation compatibility layer**](https://github.com/OpenDriver2/REDRIVER2)

  Translates reverse-engineered Driver 2 MIPS routines into C/C++ and uses Psy-X/Psy-Cross to adapt PlayStation interfaces for desktop systems. The project documents symbol-assisted Ghidra/IDA work alongside intentional bug fixes and gameplay changes.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/redriver2-case/)

- [**DevilutionX: porting Diablo’s reconstructed engine**](https://github.com/diasurgical/DevilutionX)

  Builds a modern Diablo and Hellfire port on the Devilution reconstruction, with platform support, bug fixes and optional quality-of-life features. The project documents the original symbol-assisted reconstruction and includes selected dungeon-generation and saved-game regression checks.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/devilutionx-case/)

- [**Touhou reconstructions: an agent-driven method across three games**](https://rea.tools/blog/touhou-reconstruction/)

  An essay published on REA’s site, with pinned evidence notes, describes one author’s agent-driven reconstructions of TH08, TH095 and TH04. It dates milestones from public commits and progress ledgers, separates exact-comparison and playable-build oracles, and documents a TH08 check that missed wrong floating-literal data. Project results remain author-reported, and REA is credited with supplying analysis evidence, not the reconstructions themselves.

  Case study · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-touhou-reconstruction-method-case/)

- [**TicTacToe-AI: a bounded REA-fork reconstruction of one game method**](https://github.com/heaven-hm/re-agent/tree/develop/benchmarks/tictactoe)

  The author’s REA fork, posted as rea-engine and since renamed RE-Agent, decompiles the shipped .NET executable of the GPL-licensed TicTacToe-AI game, recompiles the recovered C# and resources, and repairs one decompiler error against the original IL. A differential probe runs original and rebuilt code on all 19,683 board assignments for one status method and compares six form renders. The report passes only that method; the whole game remains partial.

  Case study · Mixed workflow · [Requirements & evidence](https://awesomerea.org/resources/rea-engine-tictactoe-case/)

- [**UltraSunnyMoon: a partial, REA-led Pokémon Ultra Sun reconstruction**](https://github.com/tylergraydev/UltraSunnyMoon)

  The author uses a pinned REA build with Ghidra to analyze a user-supplied Pokémon Ultra Sun base executable, rebuild it byte for byte from split objects, and swap in two small compiled C runtime routines. Both replacements are behavior-tested but nonmatching and every other byte stays original; one recorded input movie drives the original and hybrid builds to the same bedroom movement in the Azahar emulator. Retail compiler identity, exact matching, module loading and broader gameplay remain open.

  Case study · Mixed workflow · [Requirements & evidence](https://awesomerea.org/resources/ultrasunnymoon-rea-case/)

- [**LASRecomp: Link’s Awakening static recompilation**](https://github.com/peiikai/LASRecomp)

  A native desktop reconstruction of the 2019 Switch version of Link’s Awakening using static recompilation. The author attributes most code, tooling and reverse-engineering work to Claude Code with human direction and review.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/lasrecomp/)

- [**ArkWeb: a two-game movement and collision experiment**](https://github.com/luki-1/ArkWeb)

  Runs Spider-Man Remastered and Arkham Knight together, streaming Gotham collision into Spider-Man’s physics world and compositing his rendered frame into Arkham. This experimental runtime bridge is not a recovered standalone game or new engine.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/arkweb-two-game-case/)

- [**Perfect Dark: matching Nintendo 64 decompilation**](https://github.com/n64decomp/perfect_dark)

  Reconstructs Perfect Dark’s Nintendo 64 code with a documented matching-ROM build. The project combines reconstructed source with assets from a user-supplied original ROM, then checks version-specific artifact hashes. It is a reproducible-build research case, distinct from the separate native PC port; matching results remain project-reported here.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/perfect-dark-matching-decomp-case/)

- [**Super Mario Sunshine: a native PC port from an AI-assisted decompilation**](https://github.com/chasem-dev/sms-pc-port)

  Builds a native PC port of Super Mario Sunshine’s North American release from a pinned matching-decompilation fork, adding a host platform layer for graphics, disc, audio, input and OS services. The fork’s README says AI was used extensively to reconstruct and match its code; the port documents scripted regression hashes and lockstep comparisons with retail captures. Functions that do not yet match can still behave differently from retail, and the game must come from the user’s own disc image.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/sms-pc-port-case/)

- [**Majora’s Mask: matching US N64 decompilation**](https://github.com/zeldaret/mm)

  Recreates a C source base for The Legend of Zelda: Majora’s Mask from information in the game and static or dynamic analysis, then rebuilds the US Nintendo 64 ROM. The build takes assets and assembly from a user-supplied ROM and checks the output against stored MD5 checksums. The team states it will not produce a PC port; the separately curated Zelda 64: Recompiled only credits it for headers and some functions.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/zelda-mm-decomp-case/)

- [**DLSSNR-AMD: reimplementing DLSS 5 neural rendering for RDNA4**](https://github.com/mochizuki0323/DLSSNR-AMD)

  Reimplements the neural-rendering network of NVIDIA’s DLSS 5 library as Vulkan compute shaders for AMD RX 9000 (RDNA4) cards and supplies it to games through an NGX-compatible core and ReShade or Vulkan-layer routes. The weights are not distributed: installers extract them, hash-checked, from the user’s own nvngx\_dlssnr.dll 310.9.16 or 310.8.0. The project compares its output with NVIDIA’s DLL on an RTX 5090 and reports close, not bit-identical, pictures.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/dlssnr-amd-neural-rendering-case/)

- [**Breath of the Wild: per-function matching decompilation of the Switch executable**](https://github.com/zeldaret/botw)

  Reimplements part of Breath of the Wild’s Switch v1.5.0 main executable in C++ and checks each function against the original machine code. The project calls itself a hybrid decompilation/reimplementation: it contains no assets, its ELF holds only reimplemented functions and cannot run the game, and porting is an explicit non-goal.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/botw-decomp-case/)

- [**Skyward Sword: Wii decompilation with hash-checked relinking**](https://github.com/zeldaret/ss)

  Reconstructs C++ source for The Legend of Zelda: Skyward Sword’s Wii main.dol and REL modules, starting from the user’s NTSC-U 1.0 (SOUE01) disc files. Objects marked matching are compiled from source and linked with objects split from the original, and the result is checked against SHA-1 hashes; the repository ships no assets or assembly and is not a port.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/skyward-sword-decomp-case/)

- [**2 Ship 2 Harkinian: a native Majora’s Mask port built on the decompilation**](https://github.com/2ship2harkinian/2ship2harkinian)

  Builds native Windows, Linux and macOS versions of The Legend of Zelda: Majora’s Mask from an adapted copy of the zeldaret/mm decompilation, with libultraship reimplementing N64 SDK functions. Game data comes from a user-supplied ROM and is packed into an archive that custom asset packs can override. It targets a playable PC port with enhancements, not a byte-identical ROM.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/2ship2harkinian-mm-port-case/)

- [**Ship of Harkinian: a native Ocarina of Time port built on the decompilation**](https://github.com/HarbourMasters/Shipwright)

  Builds Ocarina of Time as a native PC application from the OoT decompilation’s source, with libultraship standing in for the N64 libultra SDK and DirectX 11, OpenGL or Metal rendering. No game assets are shipped: they are converted from the user’s supported ROM into an .o2r archive, and the port adds save states, alternate and custom assets and other enhancements.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/ship-of-harkinian-oot-port-case/)

- [**The Minish Cap: a GBA decompilation targeting five ROMs**](https://github.com/zeldaret/tmc)

  Recreates a C source base for The Legend of Zelda: The Minish Cap from information in the game and static or dynamic analysis, building five Game Boy Advance ROMs: USA, EU, JP and two demos. Each version takes its assets from a user-supplied original ROM, and normal builds check the output’s SHA-1 hash. The project remains a work in progress, and some parts of the ROM may not yet be shiftable.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/zelda-tmc-decomp-case/)

- [**Ocarina of Time: decompilation with MD5-checked ROM builds for 16 versions**](https://github.com/zeldaret/oot)

  Recreates a C source base for Ocarina of Time that rebuilds 16 Nintendo 64, GameCube and iQue Player ROM versions, using information from the game and static and dynamic analysis. Assets come from the user’s own ROM and each default build is checked against that version’s MD5; README states the project is not producing a PC port and still calls the repository a work in progress.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/ocarina-of-time-decomp-case/)

- [**Project Arwing: Star Fox recompiled from a matching disassembly**](https://github.com/carlosrmz009/arwing)

  Disassembles Star Fox’s 65816 and SuperFX code from runtime coverage and recursive descent, reassembles it into the original ROM, then translates it statically to C on a from-scratch SNES runtime for Windows, macOS and Linux. Code never reached in recorded sessions, and RAM code that no longer matches the ROM, falls back to an interpreter; the README reports identical per-frame hashes for both paths. The generated C is a mechanical translation rather than hand-decompiled source, and results remain project-reported.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/project-arwing-star-fox-recomp-case/)

- [**Project Arwing (2): Star Fox 2 recompiled from a matching disassembly**](https://github.com/carlosrmz009/arwing2)

  Rebuilds Star Fox 2 from a coverage-seeded 65816 and SuperFX disassembly that reassembles to the original ROM, then translates it statically to C for native Windows, macOS and Linux builds. Unreached code and RAM code that differs from the ROM run through an interpreter, and the README reports identical per-frame hashes against interpreted runs. It accepts the SNES Classic release image, not the 1995 prototypes; results remain project-reported.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/project-arwing-2-star-fox-2-recomp-case/)

- [**Little Planet: Sonic CD recompiled from a matching disassembly**](https://github.com/carlosrmz009/littleplanet)

  Disassembles every executable file on the Sonic CD disc from runtime coverage and recursive descent, reassembles them byte-identically, and translates the code statically to C on a from-scratch Mega-CD runtime that replaces the BIOS with a high-level implementation. Recompiled blocks run only where memory still holds the code they came from, and a script compares 96 stage runs frame by frame against the interpreter. The project also patches in widescreen and per-zone saves; results remain project-reported.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/little-planet-sonic-cd-recomp-case/)

- [**vf2-decomp: differentially validated Virtua Fighter 2 recovery**](https://github.com/celsowm/vf2-decomp)

  Recovers Virtua Fighter 2 Version 2.1’s Sega Model 2A i960 program into portable, non-matching C17, accepting each recovered path only when it matches a reference i960 executor at controlled boundaries. The repository adds ROM validation, i960 and 68000 analysis tools, a bounded Model 2A hardware model and snapshot-based differential runners. README states that it is not yet a playable port; match flow, combat, physics, AI, rasterization and much of the audio remain open.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/vf2-decomp-differential-recovery-case/)

- [**z2rs: an incremental Rust reconstruction of Zelda II checked against an emulator**](https://github.com/troyedwardsjr/z2rs)

  Rebuilds Zelda II: The Adventure of Link (NES) in Rust for desktop, browser and Android by replacing the game’s 6502 routines one at a time. A built-in interpreter still runs the user’s ROM and hands ported routines to Rust, while a verifier compares RAM, sprites, palette and frames with a reference emulator. It is a behavioral, clean-room-style reconstruction guided by a community disassembly, not a decompilation or a finished standalone engine.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/z2rs-zelda2-reconstruction-case/)

- [**sm64ex: an enhanced Super Mario 64 PC port from the decompilation**](https://github.com/sm64pc/sm64ex)

  Builds native Super Mario 64 executables from decompiled source, extending the sm64-port fork of the n64decomp reconstruction with renderer, input, camera, save-format and external-data options. Game assets are extracted from the user’s own ROM at build time. It is a non-matching enhanced port, not a byte-identical ROM reconstruction.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/sm64ex-pc-port-case/)

- [**Ghostship: a libultraship native port of Super Mario 64**](https://github.com/HarbourMasters/Ghostship)

  Builds Super Mario 64 as a native PC, Switch and Android program by compiling decompilation-style game source against the libultraship platform library. A bundled extractor converts the user’s US or Japanese ROM into an O2R archive at first launch or build time. The project ships modern renderers, configuration menus and mod-archive loading, not a matching ROM.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/ghostship-sm64-port-case/)

- [**Super Mario Sunshine: an in-progress matching GameCube decompilation**](https://github.com/doldecomp/sms)

  Reconstructs Super Mario Sunshine’s C++ source so that the original Metrowerks compiler reproduces byte-identical object files for four GameCube releases and the Switch 3D All-Stars build. The target binary comes from the user’s own disc image, and objdiff compares rebuilt objects function by function. The work is incomplete, and the repository publishes contribution rules for AI agents alongside its human workflow.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/sms-matching-decomp-case/)

- [**Dusklight: a native Twilight Princess port built on the decompilation**](https://github.com/TwilitRealm/dusklight)

  Reimplements Twilight Princess as a native application for desktop and mobile platforms, building on the zeldaret/tp decompilation and the Aurora GameCube/Wii compatibility layer. It runs from the user’s own disc image with no bundled assets and aims to stay accurate to the original while adding options, enhancements and mods.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/dusklight-twilight-princess-port-case/)

- [**Metaforce: a Metroid Prime engine reimplementation rebuilt on the decompilation**](https://github.com/AxioDL/metaforce)

  Started in 2015 as a reverse-engineered reimplementation of the Metroid Prime engine, Metaforce has been rewritten on top of the PrimeDecomp matching decompilation. Its native app compiles that game code as non-matching C++ for desktop and mobile through the Aurora GameCube compatibility layer and loads a user-selected disc image. The README says builds are unavailable while the rewrite stabilizes.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/metaforce-metroid-prime-case/)

- [**Super Mario Sunshine (USA): an AI-assisted matching decompilation fork**](https://github.com/chasem-dev/sms-english)

  Extends the doldecomp Super Mario Sunshine decompilation to the North American GMSE01 release. The README says AI was used extensively, and the repository’s agent rules, work order and progress files describe batch-based Claude and Codex orchestration. Its rebuilt DOL is reported byte-identical, but unfinished objects are still linked from code extracted from the user’s disc.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/sms-english-gmse01-decomp-case/)

- [**Donkey Kong 64: Recompiled — an N64Recomp native port**](https://github.com/Rainchus/Donkey-Kong-64-Recompiled)

  Uses N64Recomp to statically recompile the US Nintendo 64 release of Donkey Kong 64 into a native port, with RT64 as the renderer. The port is not built from decompiled source, but borrows headers and some functions from the in-progress DK64 decompilation for patches and enhancements. Its recompiler configuration reads a checked-in symbol dump and the ROM rather than a decompilation ELF.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/dk64-recompiled-case/)

- [**Twilight Princess: a decompilation with fully matching GameCube code**](https://github.com/zeldaret/tp)

  Reconstructs Twilight Princess source that compiles back to binaries identical to the originals, building GameCube, Wii and Nvidia Shield releases from one codebase through conditional compilation. README reports the GameCube code as completely matching but not every translation unit linked yet, with Debug and Wii alignment ongoing; the repository ships no assets or assembly and will not produce a port.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/twilight-princess-decomp-case/)

- [**Castlevania: Symphony of the Night: matching decompilation across PlayStation, PSP and Saturn builds**](https://github.com/Xeeynamo/sotn-decomp)

  Recreates C source for Castlevania: Symphony of the Night from its PlayStation, PSP and Saturn binaries, aiming for code that compiles byte for byte to the original game files. The work-in-progress build combines decompiled code with assets and assembly extracted from a user-supplied disc image, then checks per-version SHA-1 hashes. Native PC experiments in the same tree are documented as unfinished and are not a released port.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/sotn-matching-decomp-case/)

- [**LEGO Island, portable: a multi-platform port of the decompiled source**](https://github.com/isledecomp/isle-portable)

  Adapts the LEGO Island decompilation into a portable build for desktop, mobile, console, DOS and Web targets. Windows-only subsystems are replaced with SDL3, miniaudio, iniparser and a custom Direct3D Retained Mode re-implementation, while core gameplay is meant to stay unchanged. It ports reconstructed source rather than checking byte-identical binaries, so it is distinct from the exact-rebuild decompilation case.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/lego-island-portable-case/)

- [**c1: a C port of PlayStation Crash Bandicoot**](https://github.com/wurlyfox/c1)

  Ports the original PlayStation Crash Bandicoot game code to C function by function; its coding standard labels functions with the addresses of their original implementations. Only the PC build, using OpenGL, SDL2 and FluidSynth, currently works; it loads asset files from the user’s game disc and is only partially playable.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/crash-bandicoot-c1-port-case/)

- [**Metroid Prime Port: an AI-assisted native port of the PrimeDecomp decompilation**](https://github.com/Odrannnn/MetroidPrimePort)

  Compiles the PrimeDecomp decompilation of Metroid Prime’s game and engine code as native C++20 for Linux, Windows and Android, with an experimental macOS build. Aurora supplies the GameCube SDK compatibility layer and rendering, and the port reads a user-supplied disc image at run time. The author states that parts were written with AI coding assistants under their oversight.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/metroid-prime-port-case/)

- [**The Wind Waker: a GameCube decompilation with hash-checked relinking**](https://github.com/zeldaret/tww)

  Reconstructs source for The Wind Waker’s GameCube executable and REL modules across the USA/Korea, PAL and Japanese releases and a Japanese kiosk demo. Matched units are compiled from source and linked with objects split from the user’s disc, then checked against per-version SHA-1 hashes; the repository ships no assets or assembly and covers the GameCube game, not the HD remaster.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/wind-waker-decomp-case/)

- [**Sonic Mania: a game-code decompilation for the RSDKv5 engine**](https://github.com/RSDKModding/Sonic-Mania-Decompilation)

  Reconstructs Sonic Mania’s game code in C and builds it with the separately decompiled RSDKv5 or RSDKv5U engine for Windows, Linux, Switch and Android. Assets must come from an official Sonic Mania (Plus) release; the project adds a mod loader and can build several retail versions. Its license describes the code as mostly functionally the same as the original, not byte-matching.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/sonic-mania-decomp-case/)

- [**MediEvil Recomp: a PlayStation static recompilation to C#**](https://github.com/BlackLabelHQ/MediEvilRecomp)

  Statically recompiles the North American PlayStation release of MediEvil into C# with the RecompOne recompiler and runtime. The runtime stands in for BIOS, GPU, CD-ROM and other hardware services, and project patches change rendering, widescreen and terrain behavior. README stresses that this is a recompilation, not a decompilation, and labels it an open beta.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/medievil-recomp-case/)

- [**Crash Bandicoot 2 Recompiled: a PSXRecomp native build**](https://github.com/Zumbo06/Crash2Recomp)

  A Windows launcher that uses the PSXRecomp recompiler and runtime to translate the user’s Crash Bandicoot 2: Cortex Strikes Back disc to C and compile it locally, so the game runs as native code with an emulated PlayStation hardware layer. The repository holds the launcher, a patched vendored runtime and a long bring-up log; it distributes no game code or data.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/crash2recomp-case/)

- [**Petari: a matching Super Mario Galaxy decompilation**](https://github.com/SMGCommunity/Petari)

  Reconstructs Super Mario Galaxy’s Wii code as C++ that rebuilds, object by object, against main.dol files extracted from the user’s own Japanese, North American, PAL or Korean disc. Matched objects are linked from source and checked with objdiff and a target hash. The project describes itself as a work in progress, separate from any PC port, and says it does not accept AI-generated decompilation.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/petari-smg-decomp-case/)

- [**Wind Waker HD Recomp: a native port by static recompilation of the Wii U game**](https://github.com/ZeldaWWHDRecomp/ZeldaWWHDRecomp)

  Statically recompiles The Wind Waker HD’s Wii U PowerPC code to C ahead of time, reimplements the Cafe OS libraries the game uses and implements GX2 graphics on Metal or Vulkan, producing native macOS, Linux, Windows and Android builds without a Cemu runtime. All game code and data are generated locally from the user’s own dump; an experimental macOS-only build can instead run functions from the separate ZeldaWWHDDecomp/wwhd decompilation.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/wind-waker-hd-recomp-case/)

- [**Castlevania 64: Recompiled — a beta static-recompilation port**](https://github.com/RevoSucks/CV64Recomp)

  Uses N64Recomp to statically recompile the US 1.0 Nintendo 64 release of Castlevania into a native PC port rendered with RT64. Game-specific C patches build against headers from a separate Castlevania 64 decompilation. A beta release tagged at the reviewed commit reports a working build with known issues, while the README there still describes an unfinished project.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/cv64-recompiled-case/)

- [**RSDKv5 Decompilation: reconstructing Retro Engine v5 and v5U**](https://github.com/RSDKModding/RSDKv5-Decompilation)

  Reconstructs the Retro Engine (RSDK) v5 and v5 Ultimate runtime, the engine that runs Sonic Mania’s game code, and builds it for Windows, Linux, Switch and Android. RSDKv5U can also run RSDKv3 and RSDKv4 games such as Sonic CD and Sonic 1 &amp; 2. The project adds a mod loader, a shader compiler and extra Windows backends, and ships no game data.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/rsdkv5-engine-decomp-case/)

- [**C2C: hybrid recompilation and hand decompilation of Crash Bandicoot 2**](https://github.com/ughman/c2c)

  An early reverse-engineering effort on PlayStation Crash Bandicoot 2 that converts the engine’s MIPS machine code directly into a very large C file and runs it against a modified PCSX-R emulator library for hardware I/O. Translated functions are meant to be decompiled by hand and moved into ordinary C, gradually replacing the mechanical translation.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/c2c-crash2-hybrid-recompilation-case/)

- [**MediEvil decompilation: an early checksum-gated PlayStation project**](https://github.com/MediEvilDecompilation/medievil-decomp)

  Decompiles the US PlayStation release of MediEvil toward C source that rebuilds its main executable, game executable and 26 overlays. splat splits the user's own disc files, and the default build compares all 28 outputs with SHA-1 checksums. README describes the project as a work in progress and publishes no progress figure.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/medievil-decomp-case/)

- [**Conker's Bad Fur Day: Recompiled — an N64Recomp native port**](https://github.com/sciaschi/CBFD-Recompiled)

  Statically recompiles the US Nintendo 64 release of Conker’s Bad Fur Day with N64Recomp into a native Windows, Linux and macOS port on N64ModernRuntime and RT64. Function names and boundaries come from a vendored, still mostly assembly decompilation, while the recompiled code is taken from the user’s ROM so unmatched decompiled C cannot change behavior. The author reports heavy use of Claude Code across the project.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/cbfd-recompiled-case/)

- [**ProjectCane: a native PC port of Sly Cooper and the Thievius Raccoonus**](https://github.com/theclub654/ProjectCane)

  Rebuilds the NTSC PlayStation 2 release of Sly Cooper and the Thievius Raccoonus as a native C++ game for Windows and Linux, running on data extracted from the player's own disc image. The README reports the full game as playable while work continues on accuracy and remaining differences from the original. It does not describe its reverse-engineering method or relate the port to the separate sly1 decompilation.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/projectcane-sly1-pc-port-case/)

- [**Firefighter: a decompiled DOS game ported to Rust**](https://gitlab.com/esr/firefighter)

  Eric S. Raymond’s terminal port of Firefighter, Eben Sprinsock’s 1985 DOS shareware game. The project history says ChatGPT 5.5 decompiled the DOS binary to Borland Pascal and translated it to Rust, after which Raymond modernized the interface and corrected a scoring mismatch. Unchanged gameplay is the author’s statement; the intermediate Pascal and any comparison runs are not published.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/firefighter-rust-port-case/)

- [**Kingdom Hearts 358/2 Days: native PC port built on a matching decompilation**](https://github.com/Yokimitsuro/khdays-port)

  Compiles the C of the khdays-decomp matching decompilation for Windows x64 and supplies a native platform layer for the Nintendo DS hardware, SDK services and sound driver. README reports the whole game running without an ARM interpreter; its rendering, controls, mod support and network multiplayer are the port’s own additions. This is a decompilation-based port, distinct from the byte-matching DS reconstruction it builds on.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/khdays-native-pc-port-case/)

- [**ico-pc: a native ICO port compiled from the PS2 decompilation**](https://github.com/nathanialf/ico-pc)

  Compiles the decompiled C of the PlayStation 2 game ICO natively for Windows, Linux, Android, iPhone and Apple-silicon Macs, with host code standing in for the PS2 hardware and Sony libraries. No PS2 code is interpreted or recompiled, and the program reads the player's PAL disc image on first start. It is a native port of a separately byte-matched decompilation, with documented divergences and optional enhancements.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/ico-pc-port-case/)

- [**Sly Cooper and the Thievius Raccoonus: matching PlayStation 2 decompilation**](https://github.com/TheOnlyZac/sly1)

  Reconstructs source code for SCUS\_971.98, the NTSC-U PlayStation 2 executable of Sly Cooper and the Thievius Raccoonus, as a work-in-progress matching decompilation. Functions not yet matched are still assembled from code split out of the user's own executable, and the build checks the linked ELF's SHA-1. The result runs in PCSX2 with the original disc for assets; it is not a native PC port.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/sly1-matching-decomp-case/)

- [**Pokémon Emerald: a matching Game Boy Advance decompilation**](https://github.com/pret/pokeemerald)

  Reconstructs Pokémon Emerald for the Game Boy Advance as buildable C source, with game scripts and data kept as assembler directives. The default agbcc build produces pokeemerald.gba, and make compare checks it against the SHA-1 of the original English ROM; an optional modern-GCC build is not hash-checked. Graphics and audio sources are committed in the tree, so the documented build reads no base ROM.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/pokemon-emerald-decomp-case/)

- [**Paper Mario: matching Nintendo 64 decompilation for four releases**](https://github.com/pmret/papermario)

  Reconstructs Paper Mario’s Nintendo 64 code as C source that rebuilds the US, Japanese, PAL and iQue ROMs. The build takes assets and comparison inputs from a user-supplied original ROM, then checks each output against a recorded SHA-1. Mutable project reports list no remaining nonmatching functions, while the README still calls the decompilation work in progress; it is distinct from the PaperBoat native port.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/paper-mario-matching-decomp-case/)

- [**Budokai Tenkaichi 3: a native PC port built on a matching decompilation**](https://github.com/z3xox/Tenkaichi3Decomp)

  Compiles the decompiled code of Dragon Ball Z: Budokai Tenkaichi 3 (PS2, USA release SLUS-21678) for PC on a new renderer, sound, input and platform layer rather than an emulator. The game code comes from the separate BT3-Decompiled matching decompilation, and the game's data is read from the user's own disc image. The README reports the full game loop and experimental online play and says AI helped make the project; these results remain project-reported.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/tenkaichi3-pc-port-case/)

- [**D2R Mobile: rehosting Diablo II: Resurrected’s Switch program on Apple devices**](https://github.com/jhaizhou-ops/d2r-mobile)

  Runs the Nintendo Switch release’s own aarch64 program natively on iPhone, iPad and Apple silicon Macs, rewriting only instructions that depend on the Horizon kernel and supplying its system services and the NVN graphics API on Metal. Shaders are translated offline from the user’s files, and the project adds its own touch interface and endgame features. It is a rehosting compatibility layer, not a decompilation or recompiled source.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/d2r-mobile-switch-rehost-case/)

- [**Ratchet &amp; Clank: a matching PS2 decompilation with a documented agent workflow**](https://github.com/OpenRAC/rac1-decomp)

  Reconstructs C source for SCES\_509.16, the PAL v2.00 PlayStation 2 executable of Ratchet &amp; Clank (2002), with every function linked at its retail address. Functions not yet decompiled are still built from disassembly generated from the user's own executable, and the build audits functions, layout and the whole image against retail. The project documents an LLM-agent matching workflow and written build-fidelity rules for what counts as a match.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/rac1-matching-decomp-case/)

- [**Banjo: Recompiled — an N64Recomp Banjo-Kazooie native port**](https://github.com/BanjoRecomp/BanjoRecomp)

  Uses N64Recomp to statically recompile the US 1.0 Nintendo 64 release of Banjo-Kazooie into a native port on N64ModernRuntime, rendered by RT64 and extended with mod support. Like Zelda 64: Recompiled, it is not built from decompiled source; a symbols repository generated from the Banjo-Kazooie decompilation supplies function names for locating code in the ROM and writing patches.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/banjo-recompiled-case/)

- [**Pokémon FireRed and LeafGreen: a matching Game Boy Advance decompilation**](https://github.com/pret/pokefirered)

  Reconstructs the English Game Boy Advance releases of Pokémon FireRed and LeafGreen as buildable C source, with game scripts and data kept as assembler directives. Default agbcc builds produce six ROM images, covering both games' 1.0 and 1.1 releases and two variants labeled switch, each checked against its own SHA-1 manifest. Graphics and audio sources are committed in the tree, so the documented build reads no base ROM.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/pokemon-firered-leafgreen-decomp-case/)

- [**PaperBoat: a native Paper Mario port built on the decompilation**](https://github.com/HarbourMasters/PaperBoat)

  Compiles Paper Mario decompilation sources, credited to the pmret and Paper Mario DX projects, into a native US-version application on libultraship. Torch converts the user’s own ROM into a local asset archive, and the port adds rendering backends, enhancements and archive-based mods. Desktop releases are published, while Android, iOS and web builds are documented on the development branch.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/paperboat-paper-mario-port-case/)

- [**Halo 2: an agent-assisted matching decompilation of an LTCG Xbox build**](https://github.com/kirklandsig/halo2-decompiled)

  A work-in-progress matching decompilation of Halo 2 for the original Xbox: contributors write C and C++ that the period compiler, building the whole program with link-time code generation, must turn back into the retail executable's bytes function by function. The README reports just under half of the game-function bytes matched and leaves a native port for a later stage. It discloses that much of the maintainer's work runs in Claude and Codex coding-agent lanes.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/halo2-matching-decomp-case/)

- [**DiabloWeb: a WebAssembly browser port built on Devilution**](https://github.com/d07RiV/diabloweb)

  Runs Diablo in web browsers by compiling a stripped-down fork of Devilution, the community reconstruction of the game’s original source, to WebAssembly behind a React front end. The fork removes the Storm, DiabloUI, DirectX and Windows dependencies and reworks event handling for the browser. It is a port built on a reconstruction and reports no matching or behavior-equivalence checks of its own.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/diabloweb-devilution-wasm-port-case/)

- [**pokered: a matching Pokémon Red and Blue disassembly**](https://github.com/pret/pokered)

  Reconstructs the Game Boy games Pokémon Red and Blue as RGBDS assembly, with graphics and data kept as editable source files. One tree builds the USA/Europe Red and Blue ROMs, a Blue debug build and patches for the Virtual Console releases, each checked against a recorded SHA-1. It is a full disassembly rather than a decompilation into a higher-level language.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/pokered-disassembly-case/)

- [**Lighthouse: a Banjo-Kazooie PC port built on the decompilation**](https://github.com/HarbourMasters/Lighthouse)

  A native Windows, Linux and macOS port of Banjo-Kazooie that compiles game C sources, many tagged with their Banjo-Kazooie decompilation file paths, against libultraship, a reimplementation of the N64 SDK. Torch extracts the user’s ROM into an asset archive, and the port adds Anchor multiplayer, romhack and language-pack support and a randomizer. Unlike Banjo: Recompiled, it builds from decompiled source rather than statically recompiling the ROM’s code.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/lighthouse-banjo-kazooie-port-case/)

- [**Lost Odyssey Recomp: statically recompiling an Xbox 360 RPG into native ports**](https://github.com/freefrank/LostOdysseyRecomp)

  Translates Lost Odyssey’s Xbox 360 PowerPC executable with patched XenonRecomp tooling and runs the generated code on a native runtime that renders through Direct3D 12, Vulkan or Metal. Windows, Linux, macOS and Android packages import the user’s own disc data. The maintainer documents development with Claude Code and Codex CLI and records each release separately from validation and acceptance.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/lost-odyssey-recomp-case/)

- [**Super Smash Bros. Melee: a matching GameCube decompilation with a shiftable build**](https://github.com/doldecomp/melee)

  A matching decompilation of Super Smash Bros. Melee's US 1.02 release (GALE01) that rebuilds main.dol from C with the original Metrowerks compilers and checks it against the retail SHA-1. decomp.dev reports the code fully decompiled and linked at the reviewed commit, and the README says current work is mostly naming and cleanup. Because the build can be shifted, a separate non-matching mode lets modders add code to a DOL run with their own disc dump.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/melee-matching-decomp-case/)

- [**pokecrystal: a matching Pokémon Crystal disassembly**](https://github.com/pret/pokecrystal)

  Reconstructs the Game Boy Color game Pokémon Crystal as RGBDS assembly, with graphics, maps and data stored as editable sources. One tree builds the international 1.0 and 1.1 releases, the Australian release, two debug builds and a Virtual Console patch, each checked against a recorded SHA-1. Companion documentation covers script command formats and known bugs in the original game.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/pokecrystal-disassembly-case/)

- [**Pokémon HeartGold and SoulSilver: a work-in-progress, checksum-matched DS disassembly**](https://github.com/pret/pokeheartgold)

  Rebuilds the US Nintendo DS releases of Pokémon HeartGold and SoulSilver from a work-in-progress disassembly in which part of the code has been decompiled to C. Each default build checks the ARM9 and ARM7 binaries, the filesystem and the complete ROM against per-game SHA-1 manifests. README warns that, because decompilation is incomplete, edits that change code or data layout can crash the game.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/pokemon-heartgold-soulsilver-disassembly-case/)

- [**FFTARecomp: static recompilation of Final Fantasy Tactics Advance**](https://github.com/Jorge262007/FFTARecomp)

  Recompiles the user’s Final Fantasy Tactics Advance (USA) Game Boy Advance ROM ahead of time into native code for Windows, Linux and Steam Deck, building on JRickey’s gba-recomp toolkit. ARM and Thumb code is translated to C and compiled locally, while a Rust runtime models the console’s graphics, sound, DMA, timers and BIOS calls. The port adds widescreen, zoom, fast-forward and remappable controls.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/fftarecomp-gba-static-recomp-case/)

- [**SymphonyRecomp: a RecompOne static recompilation of Symphony of the Night**](https://github.com/BlackLabelHQ/SymphonyRecomp)

  Statically recompiles the North American PlayStation release of Castlevania: Symphony of the Night into C# with BlackLabelHQ’s RecompOne, whose runtime simulates the BIOS, memory-mapped I/O, GPU and CD-ROM so the game runs natively without a console BIOS. Per-overlay function maps and patches add widescreen, quality-of-life, randomizer and cheat features. References from the SOTN decompilation help name functions, but the project stresses that it is a recompilation, not a decompilation.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/symphonyrecomp-case/)

- [**The Two Towers Recompiled: an original Xbox static-recompilation port**](https://github.com/Gumpolas/TooTawersRecomp)

  Statically recompiles the x86 code of The Lord of the Rings: The Two Towers (Xbox, USA, 2002) into C with the bundled xboxrecomp toolkit, producing native Windows, Linux and experimental macOS builds. The recompiled sources are generated locally from the player's own default.xbe, and game data comes from their disc image or extracted folder. README reports the game as fully playable, with visual, frame-rate and mod issues listed.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/two-towers-recompiled-case/)

- [**Melee Unlocked: a Windows source port and static recompilation of Melee**](https://github.com/Hero88go/melee-unlocked)

  A beta Windows build of Super Smash Bros. Melee (NTSC 1.02) with two engines: a source port that compiles the doldecomp decompilation as a native library, and a static recompilation that translates the retail DOL's PowerPC code and Slippi's Gecko codes into C++. Both run on a native runtime with Direct3D rendering, unlocked display rates and natively implemented Slippi rollback play. The user's own ISO supplies all game data, and the README says the work was AI-assisted.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/melee-unlocked-case/)

- [**pokeruby: a matching Pokémon Ruby and Sapphire decompilation**](https://github.com/pret/pokeruby)

  Reconstructs the Game Boy Advance games Pokémon Ruby and Sapphire as C source built with pret's agbcc compiler, alongside assembly data scripts and editable graphics. Matching builds cover the English 1.0, 1.1 and 1.2 revisions, debug builds and the first German editions, each checked against a stored SHA-1. A separate modern-GCC target is not expected to match.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/pokeruby-decomp-case/)

- [**Vandal Hearts: native PC port built on matching decompilations**](https://github.com/HalmyLyseas/VandalHearts-PcPort)

  Builds on shao113’s matching decompilation of PlayStation Vandal Hearts, adds a Japanese matching tree, and carries both through to a native Windows and Linux port. SDL2, OpenGL or Metal and OpenAL backends replace the console’s GPU, GTE, CD-ROM/XA, SPU, MDEC and pad interfaces, and one executable runs the USA, Asia and Japan discs. The matching builds are still checked on every change; PC-only features such as Tactical Mode and HD packs are opt-in.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/vandal-hearts-pc-port-case/)

- [**Pokémon Platinum: a checksum-matched Nintendo DS decompilation**](https://github.com/pret/pokeplatinum)

  Reconstructs the US Nintendo DS release of Pokémon Platinum as C source that rebuilds revision 1 by default and revision 0 on request. The default make target runs Meson checks of the code binaries, filesystem and complete ROM against SHA-1 manifests. README still calls the project work in progress; its contributing guide says the code is entirely C but much of it remains obfuscated, leaving documentation and tooling as the main work.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/pokemon-platinum-decomp-case/)

- [**Saints Reborn: a ReXGlue static recompilation of Saints Row**](https://github.com/whompay/SaintsReborn)

  An unofficial native Windows port of Saints Row (Xbox 360, 2006) that statically recompiles the game's PowerPC executable to C++ for x86-64 with the ReXGlue SDK, which also reimplements the console's kernel, GPU (on Direct3D 12), audio and input. A recompiler manifest, game-specific function overrides and an SDK patch make the result run, and each user builds it locally from their own disc. The README reports the game fully playable with built-in co-op and lists known issues.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/saints-reborn-recomp-case/)

- [**Pokémon Platinum PC Port: a native port built on the pret decompilation**](https://github.com/cybervisi0n/pokeplatinum)

  Builds native 64-bit Windows and Linux executables of Pokémon Platinum from a fork of pret’s decompilation, replacing NitroSDK with the author’s libntr libraries; the same tree keeps the DS ROM build and an experimental Switch target. README says the game should be playable from start to finish but may crash or show graphical bugs. Prebuilt binaries require the player’s own US ROM, and the fork’s default build no longer runs pret’s checksum tests.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/pokemon-platinum-pc-port-case/)

- [**MikuPan: a native Fatal Frame PC port built on the Himuro decompilation**](https://github.com/Mikompilation/MikuPan)

  Ports the PS2 game Fatal Frame to native PC builds without emulation; its repository description names the Himuro decompilation as its basis. Stubs replace PS2 kernel calls and a new SDL3-based layer handles rendering, audio and UI, while game data comes from the user’s own disc. The README calls the port very early work and publishes no matching or fidelity checks.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/mikupan-fatal-frame-port-case/)

- [**Starfox 64: Recompiled — an N64Recomp static-recompilation port**](https://github.com/sonicdcer/Starfox64Recomp)

  Uses N64: Recompiled to statically recompile the US 1.1 (Rev A) Nintendo 64 release of Star Fox 64 into a native port for Windows, Linux and macOS, rendered with RT64. Its patches and enhancements draw on headers and some functions from the separate sf64 decompilation, but the port is not compiled from that decompilation's source. The README reports high-frame-rate, widescreen and mod support, with assets loaded from the user's own ROM.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/starfox64-recompiled-case/)

- [**Syphon Filter: The Omega Strain — matching PS2 executable decompilation**](https://github.com/zm2283145/syphon-filter-omega-strain-decomp)

  Reconstructs much of the NTSC-U PlayStation 2 executable of Syphon Filter: The Omega Strain as C; with the remaining functions kept as split assembly, the build reproduces the retail SCUS\_972.64 byte for byte. Committed objdiff reports track per-function matching against the user’s own executable. This is a matching-decompilation case, not a PC port; progress figures remain project-reported.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/syphon-filter-omega-strain-decomp-case/)

- [**Animal Crossing: a native PC port of the GameCube decompilation**](https://github.com/flyngmt/ACGC-PC-Port)

  Runs Animal Crossing’s decompiled GameCube C code natively on 32-bit x86, replacing the GX graphics API with an OpenGL 3.3 translation layer and console services with SDL2-based platform code. Game assets are read at startup from the user’s own disc image instead of being shipped. It is a port built on ACreTeam’s ac-decomp, not a matching rebuild of the original executable.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/animal-crossing-pc-port-case/)

- [**GoldenEye 007: matching Nintendo 64 decompilation for three releases**](https://github.com/n64decomp/007)

  Reconstructs GoldenEye 007’s Nintendo 64 code as C source that rebuilds the US, Japanese and PAL ROMs. Assets come from a user-supplied US ROM, with Japanese and PAL differences taken from their own ROMs, and the default build compares each output with a recorded SHA-1. The README still calls the project work in progress, while a mutable status page reports all 208 files done; it is distinct from the separately curated PC port.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/goldeneye-007-matching-decomp-case/)

- [**Starship: a Star Fox 64 PC port built from the decompilation**](https://github.com/HarbourMasters/Starship)

  A native PC port of Star Fox 64 that compiles the game's decompiled C code against libultraship, an N64 porting library that reimplements libultra and renders through Fast3D. On first run it uses the Torch tool to turn the user's US ROM into an asset archive, and it ships for Windows, Linux, macOS and Switch. The README of the separate Starfox 64: Recompiled static recompilation calls this port its sibling, built with different technology.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/starship-sf64-pc-port-case/)

- [**CTR Turbocharged: a PC sourceport built on the Crash Team Racing decompilation**](https://github.com/CameronRedmore/Crash-Team-Racing-Turbocharged)

  Extends the Crash Team Racing: High Octane sourceport, which derives from the CTR Native port of the CTR-ModSDK PlayStation decompilation, into Windows and Linux builds with a native 3D renderer, selectable aspect ratios and frame rates up to 240 FPS. The decompiled game code still assumes 32-bit pointers and loads assets from the player’s own NTSC-U disc image. Renderer, timing and option tests exist, but device coverage and fidelity remain project-reported.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/ctr-turbocharged-port-case/)

- [**The Darkness Recomp: an Xbox 360 static recompilation with a native D3D11 renderer**](https://github.com/portingpete/The-Darkness-Recomp)

  Builds a native Windows x64 port of The Darkness by translating its Xbox 360 executable to C++ ahead of time with a patched XenonRecomp. A D3D11 renderer draws from the engine’s original geometry, shader sources and device state instead of interpreting console GPU packets. Gameplay coverage and Linux results are project-reported, and the author discloses OpenAI Codex assistance.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/the-darkness-recomp-case/)

- [**MarioKart 64: Recompiled — a native port through N64Recomp static recompilation**](https://github.com/sonicdcer/MarioKart64Recomp)

  Statically recompiles the US Nintendo 64 release of Mario Kart 64 into a native Windows, Linux and macOS application with N64Recomp, rendering through RT64. The README distinguishes this from a source port: game code is translated from the user’s ROM, while headers and some functions from a decompilation fork support patches and enhancements. Enhancement, fidelity and input-lag claims are project-reported.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/mariokart64-recompiled-case/)

- [**Animal Crossing: matching GameCube decompilation**](https://github.com/ACreTeam/ac-decomp)

  Reconstructs Animal Crossing’s GameCube code as C and C++ source that rebuilds the USA release’s main executable and its foresta.rel module. The dtk-template build reads the original binaries and assets from a user-supplied disc image, then checks both outputs against SHA-1 hashes. A separate native PC port builds on it; completeness figures remain project-reported here.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/animal-crossing-gamecube-decomp-case/)

- [**Kingdom Hearts 358/2 Days: a matching Nintendo DS decompilation**](https://github.com/Yokimitsuro/khdays-decomp)

  Reconstructs the ARM9 program and overlays of the EU Nintendo DS release of Kingdom Hearts 358/2 Days as C that recompiles byte for byte with CodeWarrior. README reports all 306 modules byte-identical, with about 99.5% of functions in real C and library assembly counted separately; the ARM7 binary is outside its scope. The repository holds no ROM, game assets or extracted disassembly and produces no playable build.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/kingdom-hearts-days-matching-decomp-case/)

- [**TonyWasAProSkater: a THPS1 native port forked from a matching decompilation**](https://github.com/LANCommander/TonyWasAProSkater)

  Ports Tony Hawk’s Pro Skater (PlayStation, USA) to native Windows and Linux builds from a fork of an in-progress matching decompilation of the retail executable. The decompilation recompiles reconstructed functions with a Psy-Q toolchain and compares them byte for byte with the user’s retail executable, while the port replaces PlayStation hardware and libraries with SDL2 and OpenGL services. Play needs the user’s own disc image; matching and gameplay results remain project-reported.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/thps1-decomp-native-port-case/)

- [**P.T. for PC: a behavior-based engine reimplementation that reads the PS4 data**](https://github.com/LoreanXavier/pt-pc)

  Reimplements P.T.’s game logic in C++ on a new Vulkan engine that reads levels, models, textures, sounds, scripts and cutscenes from the user’s own PS4 copy at run time. The author documents reverse-engineered file formats and used the shadPS4 emulator as a behavior and frame reference. Fidelity to the original is author-reported, and the use of AI coding tools is disclosed.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/pt-pc-port-case/)

- [**SpaghettiKart: a native Mario Kart 64 port built on decompiled source**](https://github.com/HarbourMasters/SpaghettiKart)

  Builds a native Mario Kart 64 port for Windows, Linux, macOS and Switch from source that keeps the Mario Kart 64 decompilation’s file layout, running on libultraship’s reimplemented N64 SDK. Its bundled Torch extractor converts the user’s US ROM into an asset archive, and the port adds mods, custom tracks and an editor. The README does not name its upstream decompilation, and no matching or fidelity checks are published.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/spaghettikart-mk64-port-case/)

- [**Animal Crossing: Wild World: matching Korean DS decompilation with differential runtime checks**](https://github.com/banatic/acww-decomp)

  Reconstructs the ARM9 game code of Animal Crossing: Wild World’s Korean DS release as one C or C++ source per function, checked against the user’s ROM with the original Metrowerks compiler and linker. Each function also has a readable Clean rewrite, and an included DS interpreter compares the ROM code, natively compiled sources and rewrites on recorded play. Data sections, the ARM7 binary, the linked SDK libraries and regrouping into original source files remain outside the reconstruction.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/animal-crossing-wild-world-decomp-case/)

#### Tools, projects and integrations

- [**RenderDoc**](https://github.com/baldurk/renderdoc)

  Inspect frame captures, draw calls, shaders, and graphics resources in your own game or graphics application.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/renderdoc/)

- [**AssetRipper**](https://github.com/AssetRipper/AssetRipper)

  Analyze Unity game files, inspect asset dependencies, and convert supported assets into Unity project formats.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/assetripper/)

- [**Cpp2IL**](https://github.com/SamboyCoding/Cpp2IL)

  Recover managed representations from Unity IL2CPP builds using binary and metadata analysis; reconstruction remains a work in progress.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/cpp2il/)

- [**Il2CppDumper**](https://github.com/Perfare/Il2CppDumper)

  Recover IL2CPP metadata and dummy assemblies, and generate helper scripts for native analysis tools; method code is not restored.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/il2cppdumper/)

- [**RenderDoc MCP**](https://github.com/scarletfantasy/renderdoc-mcp)

  Expose existing RenderDoc captures to an agent for bounded frame, pipeline, resource, and shader inspection.

  Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/renderdoc-mcp/)

- [**UndertaleModTool**](https://github.com/UnderminersTeam/UndertaleModTool)

  Browse and modify supported GameMaker data files, extract assets, and decompile or compile GML VM code. Includes room editing, scripted changes, a CLI, and the reusable UndertaleModLib library.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/undertalemodtool/)

- [**frida-il2cpp-bridge**](https://github.com/vfsfitvnm/frida-il2cpp-bridge)

  Inspect IL2CPP classes, methods, and fields in a live process, and trace or intercept method calls without supplying global-metadata.dat. Complements static IL2CPP dumpers with runtime observation.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/frida-il2cpp-bridge/)

- [**objdiff**](https://github.com/encounter/objdiff)

  Compare functions and data in reference and rebuilt object files to guide matching decompilation. Displays instruction-level differences, demangles C++ symbols, and can rebuild when source files change.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/objdiff/)

- [**decomp-permuter**](https://github.com/simonlindholm/decomp-permuter)

  Randomly or systematically permutes one C function, recompiling each variant and scoring it against a target object file to search for matching compiler output. PERM macros specify manual alternatives, and the optional permuter<span>@</span>home mode distributes runs to other workers.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/decomp-permuter/)

- [**asm-differ**](https://github.com/simonlindholm/asm-differ)

  Diffs original and rebuilt assembly for one function or ROM address to guide matching decompilation; its watch mode can rerun make when sources change. The README describes it as decomp.me’s default diff viewer and points to objdiff as a modern alternative.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/asm-differ/)

- [**UE Explorer**](https://github.com/UE-Explorer/UE-Explorer)

  Explore Unreal packages through class, property, and dependency trees; decompile and export UnrealScript classes, inspect bytecode, and examine structured binary data.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/ue-explorer/)

- [**GARbro**](https://github.com/morkt/GARbro)

  Browse recognized visual-novel resource archives as folders, preview their contents, and extract images or audio with conversion to common formats.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/garbro/)

- [**Godot RE Tools**](https://github.com/GDRETools/gdsdecomp)

  Recover supported Godot project files, GDScript and imported resources from exported games. Includes PCK inspection and extraction, script decompilation, and resource conversion for examining and rebuilding project structure.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/godot-re-tools/)

- [**UE4SS**](https://github.com/UE4SS-RE/RE-UE4SS)

  Inspect Unreal Engine games at runtime through live UObject property views, reflected C++ header dumps, property mappings and actor dumps. Lua and C++ APIs support experiments while reconstructing game structures.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/ue4ss/)

- [**FModel**](https://github.com/4sval/FModel)

  Explore Unreal Engine game archives with CUE4Parse-backed package and property inspection, asset previews and export. The 2026 summer release adds USD world export for reconstructing supported scene content.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/fmodel/)

- [**PSP Web Recomp**](https://github.com/snuri00/psp-web-recomp)

  Translate PSP MIPS executables into C++ and WebAssembly, backed by a PSP high-level emulation runtime and WebGL2 renderer. Native tracing, frame capture and audio tools support investigating missing behavior during game porting.

  Project · [Requirements & evidence](https://awesomerea.org/resources/psp-web-recomp/)

- [**N64: Recompiled**](https://github.com/N64Recomp/N64Recomp)

  Statically recompiles N64 MIPS binaries into C functions from symbol metadata, emitting function lookups and relocation macros so a runtime can handle statically linked and relocatable overlays. The output needs a runtime such as N64ModernRuntime; the repository also includes RSP microcode and mod tooling.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/n64recomp/)

- [**XenonRecomp**](https://github.com/hedge-dev/XenonRecomp)

  Converts Xbox 360 PowerPC executables into C++ that can be compiled for other platforms, with the XenonAnalyse companion detecting jump tables and function boundaries. Output is a literal instruction translation rather than decompiled code and needs a runtime that the project does not supply.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/xenonrecomp/)

- [**decomp.me**](https://decomp.me)

  Collaborative decompilation website for matching work: its compile service builds candidate source with a selected platform compiler, assembles the target assembly and diffs the two objects with asm-differ. m2c drafts initial decompilations for its MIPS, PowerPC, ARM and SuperH platforms. The 18 platform definitions span N64, PlayStation, PS2, PSP, GameCube/Wii, Wii U, DS, GBA, 3DS, Switch, Saturn, Dreamcast and Xbox 360 plus IRIX, Mac OS X, MS-DOS, Win32 and Android x86.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/decomp-me/)

<a id="app"></a>
### App

[↑ Contents](#contents)

#### Case studies

- [**Aegis: trace a login-code calculation**](https://rea.tools/showcase/aegis/)

  An official APK investigation follows TOTP methods in Aegis and publishes artifact identities and selected Evidence.

  Case study · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-aegis-case/)

- [**Notion: trace the clipboard bridge**](https://rea.tools/showcase/notion/)

  Trace a packaged Electron clipboard path using REA findings and separate source inspection; the dynamic wrapper remains a stated limit.

  Case study · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-notion-case/)

- [**PicoPrint: LX-D02 printer investigation**](https://github.com/bigtower17/picoprint)

  The author describes REA-assisted Android investigation followed by separate Hermes decompilation to support a Windows BLE printer.

  Case study · Mixed workflow · [Requirements & evidence](https://awesomerea.org/resources/picoprint-rea-investigation/)

- [**ReaCut: video-editor reconstruction**](https://github.com/Xiangyu-CAS/rea-capcut)

  An independent video editor whose authors document REA-assisted investigation of Jianying/CapCut behavior and project formats. The public implementation includes a local timeline, FFmpeg export and an experimental, lossy draft importer.

  Case study · Mixed workflow · [Requirements & evidence](https://awesomerea.org/resources/reacut-reconstruction/)

- [**CF632BLE: a local client from scale-protocol research**](https://github.com/guyru/cf632ble)

  Reimplements the CF632BLE scale’s BLE protocol and body-composition calculations from research on the vendor’s Unique Health Android app. A static Web Bluetooth client receives measurements, manages device profiles and keeps its history in browser storage.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/cf632ble-case/)

- [**zee-rp: reconstructing supported Axure RP 11 document operations**](https://github.com/LilZeeCN/zee-rp)

  Reads and rewrites supported native Axure RP 11 documents through a binary-record codec, reference-aware cloning and constrained interaction writers. CLI and MCP interfaces expose inspected edits while keeping offline structure checks separate from native application acceptance.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/zee-rp-case/)

- [**Virtual Desktop Streamer: rehosting the platform layer on Linux**](https://github.com/cudanexus/vd-streamer-linux)

  An author-reported Claude Code and REA workflow replaces the macOS streamer’s capture, encoding, audio and input layer with Linux implementations while reusing vendor protocol libraries. The documented result targets desktop streaming and video playback, not Windows-only VR game streaming.

  Case study · Mixed workflow · [Requirements & evidence](https://awesomerea.org/resources/vd-streamer-linux-case/)

- [**Open Claude UI: REA-informed interface reference components**](https://github.com/Caho1/open-claude-ui)

  Publishes React components, motion helpers and design-system notes derived from the author’s reported REA investigation of Claude Desktop. It is useful as an interface-reconstruction case, with version-specific observations rather than proof of a complete assistant application or backend clone.

  Case study · Mixed workflow · [Requirements & evidence](https://awesomerea.org/resources/open-claude-ui-case/)

- [**PlxNative: reconstructing a native webOS media-client interface**](https://github.com/GLinnik21/plx-native)

  An unofficial Plex client built after the author investigated LG webOS native media interfaces with Ghidra and coding agents. It draws its own Rust/OpenGL interface and uses the television’s decoder, with documented host, simulator and real-device test tiers.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/plx-native-case/)

- [**Windows Calculator: reconstructing percentage rules**](https://github.com/morluto/rea/blob/c360cfcd6d7901514b16dd6113eba2e0b0fdf422/website/evidence/calculator-and-dino.md#windows-calculator)

  REA’s case traces the installed Windows Calculator model DLL to explain different percentage behavior for multiplication/division and other operations. An analyst-selected function is interpreted against public Microsoft source and demonstrated with fixed browser examples.

  Case study · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-calculator-percent-case/)

- [**Feishu: an author-reported isolated second app instance**](https://benx.ai/blog/posts/rea-reverse-engineer-feishu-dual-instance/)

  The author reports using Codex and REA analysis to adapt a separate macOS Feishu copy with its own application identity, data directory and single-instance lock. The account describes local signing and separation checks while retaining the original app unchanged.

  Case study · Mixed workflow · [Requirements & evidence](https://awesomerea.org/resources/feishu-dual-instance-case/)

- [**PhotoCraft: editor workflow reconstruction and PSD round-trip boundaries**](https://github.com/storytold/photocraft)

  The authors describe this Rust image editor as a clean-room reimplementation of Photoshop-style workflows. Its document engine, UI and automation interfaces share editing commands, while the source distinguishes PSD editor round trips from byte preservation in the standalone file codec.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/photocraft-case/)

- [**WordCraft: document workflow reconstruction and bounded DOCX compatibility**](https://github.com/storytold/wordcraft)

  The authors describe WordCraft as a clean-room Rust implementation of familiar Microsoft Word workflows. It provides its own document model, layout engine and DOCX reader/writer, with desktop and browser interfaces; source tests exercise selected editing and file-preservation behavior.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/wordcraft-case/)

- [**GridCraft: spreadsheet workflow reconstruction and XLSX round-trip limits**](https://github.com/storytold/gridcraft)

  The authors describe GridCraft as a clean-room Rust implementation of Excel-style spreadsheet workflows. A workbook model, formula parser and dependency-driven recalculation are connected to XLSX I/O and a shared editing-command layer for desktop, browser and automation interfaces.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/gridcraft-case/)

- [**DeckCraft: presentation workflow reconstruction and bounded PPTX interchange**](https://github.com/storytold/deckcraft)

  The authors describe DeckCraft as a clean-room Rust implementation of PowerPoint-style presentation workflows. Its slide model, rendering and command layers support desktop/browser editing and PPTX interchange; reviewed source tests check constructed decks and selected preserved package parts.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/deckcraft-case/)

- [**Ledger Reborn: an independent accounting app informed by QuickBooks study**](https://github.com/lxistired/ledger-reborn)

  The maintainer reports using REA and Ghidra to study selected QuickBooks Desktop for Mac behavior, then independently implements a local accounting application. Its Python/SQLite engine persists double-entry journals, invoices, inventory and payments, while public synthetic fixtures test bounded accounting and rollback behavior.

  Case study · Mixed workflow · [Requirements & evidence](https://awesomerea.org/resources/ledger-reborn-accounting-case/)

- [**Pocket Tasks: reconstructing task state and persistence**](https://github.com/ShadowSwaps/REA-Reconstruction-Companion/tree/main/evals/reference/reconstruction)

  A teaching case with disclosed prior source access carries a REA-assisted investigation of a small command-line app into a separate Node implementation. It preserves observed task editing, persistence and selection behavior, then compares scoped outputs against fixed expectations and captured reference sessions.

  Case study · Mixed workflow · [Requirements & evidence](https://awesomerea.org/resources/pocket-tasks-reconstruction-case/)

- [**Open Scrantic: reconstructing the Johnny Castaway screensaver engine**](https://github.com/glauberlima/open-scrantic)

  Reconstructs the Johnny Castaway screensaver engine in Rust, with author-disclosed REA and Claude Code use. It reads original files to run recovered animation scripts and calendar-based story state on modern desktops; documented deviations and limited tests stop short of complete behavioral equivalence.

  Case study · Mixed workflow · [Requirements & evidence](https://awesomerea.org/resources/open-scrantic-screensaver-case/)

- [**LSX II Volume Fixer: reconstructing volume behavior**](https://github.com/roberdorfer/kef-lsx-volume)

  Uses measured USB-volume behavior and a macOS audio proxy to map volume keys to a KEF LSX II’s LAN control. The project reports more even steps while forwarding USB audio; the speaker firmware is unchanged.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/kef-lsx-volume-case/)

- [**UU Remote on Linux: an unofficial protocol implementation**](https://github.com/VallierDev/uu-remote-linux)

  Implements an unofficial native Linux host for NetEase UU Remote, using protocol behavior the maintainer says was recovered from official-client traffic and shipped programs. The Rust implementation connects selected desktop, input and auxiliary-tool channels to Linux services; an additional Linux viewer remains experimental. The author attributes development to Claude and Codex, without establishing REA use.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/uu-remote-linux-protocol-case/)

- [**TCLimate: reconstructing selected TCL Home cloud controls**](https://github.com/umarz317/TCLimate)

  Implements selected TCL Home air-conditioner controls and electricity reporting in a native macOS menu-bar app. It adapts earlier community protocol work and documents an Android-module investigation to recover a separate statistics request. Reported validation checks cloud state, not independent physical operation or complete device equivalence.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/tclimate-cloud-controls-case/)

- [**Browserbase plugin: re-hosting Claude in Chrome’s browser bridge**](https://github.com/browserbase/claude-code-plugin)

  Stands in for the Claude in Chrome extension side of Claude Code’s local browser bridge and runs the requested actions in Browserbase cloud browsers. The author’s thread describes the reverse-engineered framing, a 4-byte little-endian length before each JSON tool call, and the plugin maps 17 named tools onto Stagehand/CDP operations. It is an archived interoperability shim with several placeholder tools, not recovered Anthropic code or a verified equivalent of the extension.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/browserbase-claude-chrome-bridge-case/)

- [**Visor: an independent Ray-Ban Meta glasses client**](https://github.com/macedonga/visor)

  Implements an Android replacement for the Meta AI companion app that speaks the Ray-Ban Meta glasses’ own Bluetooth and Wi-Fi Direct protocol, imports media, exposes settings and answers “Hey Meta” with a model the user chooses. The project wiki documents the link layers, encryption, services and Meta-side ownership steps, and lists 153 open questions. Testing is on real glasses rather than test suites, so behavior beyond the stated model and firmware remains unverified.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/visor-ray-ban-meta-client-case/)

- [**wine-uwp: running packaged Windows Store apps on a patched Wine**](https://github.com/designgears/wine-uwp)

  Extends Wine 11.17 so that signed MSIX Store apps, with Shapr3D as the main target, install and run on Linux without their source or symbols. About 49,000 changed lines add a DirectComposition implementation, composition swap chains and an app-model host, while Microsoft’s own XAML and app-model DLLs, harvested from a Windows 11 image on the user’s machine, run unmodified. The author says Claude did most of the reverse engineering and code; app support is uneven and checked by a project regression suite.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/wine-uwp-store-apps-case/)

#### Tools, projects and integrations

- [**JADX-AI-MCP**](https://github.com/zinja-coder/jadx-ai-mcp)

  JADX plugin paired with a Python MCP server to inspect decompiled Android classes, resources, cross-references and debugger context.

  Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/jadx-ai-mcp/)

- [**apktool-mcp-server**](https://github.com/zinja-coder/apktool-mcp-server)

  Python MCP server that drives a local Apktool install so agents can decode APKs; list, read, search and edit smali and resource files; read AndroidManifest.xml and apktool.yml; and rebuild the project.

  Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/apktool-mcp-server/)

- [**frida-mcp (yfe404)**](https://github.com/yfe404/frida-mcp)

  Frida MCP server with persistent instrumentation sessions, runtime inspection and Android static-to-dynamic navigation.

  Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/frida-mcp-yfe404/)

- [**Super Trouper**](https://github.com/crissyfield/super-trouper)

  Single-binary Frida MCP server for discovering devices, managing process sessions and loading instrumentation scripts.

  Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/super-trouper/)

- [**Frida**](https://github.com/frida/frida)

  Dynamic instrumentation toolkit for observing and scripting the behavior of live native and managed processes.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/frida/)

- [**JADX**](https://github.com/skylot/jadx)

  Dex-to-Java decompiler with CLI/GUI navigation, resource decoding and cross-reference search for Android packages.

  Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/jadx/)

- [**Apktool**](https://github.com/iBotPeaches/Apktool)

  Decodes Android resources and smali into a project-like tree and can rebuild modified packages.

  Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/apktool/)

- [**Androguard**](https://github.com/androguard/androguard)

  Python toolkit for APK/DEX metadata, bytecode and reference analysis; the v5 source branch also documents agent skills and MCP.

  Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/androguard/)

- [**ILSpy**](https://github.com/icsharpcode/ILSpy)

  .NET assembly browser and C# decompiler with whole-project export, metadata inspection and a scriptable command-line frontend.

  Tool · .NET · [Requirements & evidence](https://awesomerea.org/resources/ilspy/)

- [**dnSpyEx**](https://github.com/dnSpyEx/dnSpy)

  Community continuation of dnSpy for debugging and editing .NET assemblies without the original source.

  Tool · .NET · [Requirements & evidence](https://awesomerea.org/resources/dnspyex/)

- [**<span>@</span>electron/asar**](https://github.com/electron/asar)

  Electron's archive tool lists and extracts ASAR contents so packaged JavaScript and application assets can be inspected.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/electron-asar/)

- [**Mobile Security Framework (MobSF)**](https://github.com/MobSF/Mobile-Security-Framework-MobSF)

  Inspect mobile application packages with static analysis and supported-device dynamic testing, including runtime behavior and network traffic, through a web interface and APIs.

  Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/mobsf/)

- [**objection**](https://github.com/sensepost/objection)

  Explore running Android and iOS apps with a Frida-backed command interface for inspecting app storage, memory, runtime objects, and instrumented behavior.

  Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/objection/)

- [**Grapefruit**](https://github.com/ChiChou/grapefruit)

  Inspect and hook running iOS and Android apps from a Frida-based web interface, with method and crypto-API hooks, filesystem and SQLite browsers, iOS keychain and UI-hierarchy views, and HTTP capture from common networking libraries.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/grapefruit/)

- [**Blutter**](https://github.com/worawit/blutter)

  Analyze Flutter Android ARM64 AOT binaries using the matching Dart runtime. Produces annotated assembly, object-pool dumps and a target-specific Frida script template for investigating compiled Dart application logic.

  Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/blutter/)

- [**hermes-dec**](https://github.com/P1sec/hermes-dec)

  Parse, disassemble and partially decompile React Native Hermes bytecode bundles. Makes HBC headers and instructions inspectable and emits pseudocode for understanding compiled application logic.

  Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/hermes-dec/)

- [**Recaf**](https://github.com/Col-E/Recaf)

  Inspect and modify compiled JVM applications with integrated decompilers, bytecode assembly, reference search, mappings and deobfuscation tools. The reviewed 4.0 preview also provides basic read-only Android bytecode inspection.

  Tool · JVM · [Requirements & evidence](https://awesomerea.org/resources/recaf/)

- [**nibkit**](https://github.com/tokenbleed/nibkit)

  Decode compiled iOS/macOS interface archives into object trees, Outlet/Action connections, custom classes and navigation relationships. Exports JSON or Mermaid diagrams and exposes read-only inspection commands through MCP.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/nibkit/)

- [**AOTopsy**](https://github.com/BroNils/aotopsy)

  Statically inspect Flutter/Dart AOT libapp.so files to recover available metadata, class structures, call edges and pseudocode without embedding a Dart VM or compiling a matching SDK. Supports ARM64 and x86\_64 analysis paths.

  Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/aotopsy/)

- [**hbctool**](https://github.com/bongtrop/hbctool)

  Disassemble and reassemble supported React Native Hermes bytecode bundles through HASM files, enabling bytecode inspection and editing for the explicitly supported legacy HBC versions.

  Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/hbctool/)

<a id="native-binary"></a>
### Native Binary

[↑ Contents](#contents)

#### Case studies

- [**DownUnderCTF: masked-squares flag checker**](https://rea.tools/showcase/ctf/)

  An official educational challenge investigation connects binary checks to equations and records an original-program validation.

  Case study · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-ctf-case/)

#### Tools, projects and integrations

- [**Ghidra**](https://github.com/NationalSecurityAgency/ghidra)

  Open-source analysis suite for disassembly, decompilation, graphs and Java/Python automation across executable formats.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/ghidra/)

- [**radare2**](https://github.com/radareorg/radare2)

  Scriptable command-line framework for inspecting, disassembling, debugging and modifying binaries across many architectures.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/radare2/)

- [**Cutter**](https://github.com/rizinorg/cutter)

  Rizin-powered graphical reverse-engineering workspace with extensible views and Ghidra decompiler integration.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/cutter/)

- [**Qiling**](https://github.com/qilingframework/qiling)

  Python emulation framework that adds OS, filesystem and API behavior around CPU emulation for instrumented binary analysis.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/qiling/)

- [**Unicorn Engine**](https://github.com/unicorn-engine/unicorn)

  Multi-architecture CPU emulator for executing selected instruction ranges with register, memory and hook control.

  Tool · Library · [Requirements & evidence](https://awesomerea.org/resources/unicorn/)

- [**angr**](https://github.com/angr/angr)

  Python binary-analysis framework combining control-flow recovery, symbolic execution, data-flow analysis and decompilation.

  Tool · Library · [Requirements & evidence](https://awesomerea.org/resources/angr/)

- [**LIEF**](https://github.com/lief-project/LIEF)

  Library for structured parsing and modification of executable formats including ELF, PE and Mach-O.

  Tool · Library · [Requirements & evidence](https://awesomerea.org/resources/lief/)

- [**Capstone**](https://github.com/capstone-engine/capstone)

  Disassembly library with architecture-neutral APIs and instruction details for custom binary-analysis pipelines.

  Tool · Library · [Requirements & evidence](https://awesomerea.org/resources/capstone/)

- [**ImHex**](https://github.com/WerWolv/ImHex)

  Hex editor with a binary-pattern language, structured data inspection and visual tools for understanding file formats.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/imhex/)

- [**x64dbg**](https://github.com/x64dbg/x64dbg)

  Windows binary debugger with disassembly, memory views and plugins for analyzing programs without source code.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/x64dbg/)

- [**GDB**](https://sourceware.org/gdb/)

  Native and remote debugger for controlling execution and inspecting live or crashed program state.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/gdb/)

- [**rr**](https://github.com/rr-debugger/rr)

  Records process execution and replays it under GDB, enabling repeatable inspection and reverse execution.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/rr/)

- [**Diaphora**](https://github.com/joxeankoret/diaphora)

  IDA-based binary diffing that matches functions and transfers names, comments and types between analyzed versions.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/diaphora/)

- [**BinDiff**](https://github.com/google/bindiff)

  Compares disassembled binaries to find matching functions and changed code across versions.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/bindiff/)

- [**Detect It Easy**](https://github.com/horsicq/Detect-It-Easy)

  Format-aware file identification and static inspection using parsers, signatures and programmable heuristics.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/detect-it-easy/)

- [**r2frida**](https://github.com/nowsecure/r2frida)

  Use radare2 commands and Frida instrumentation together to inspect local or remote process memory, symbols, classes, and runtime calls on desktop and mobile targets.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/r2frida/)

- [**Kaitai Struct**](https://github.com/kaitai-io/kaitai_struct)

  Turn documented binary layouts into reusable parsers for files and network packets. A .ksy specification can be inspected with visualizers and compiled to multiple languages, helping preserve reverse-engineered format knowledge in interoperable implementations.

  Tool · Library · [Requirements & evidence](https://awesomerea.org/resources/kaitai-struct/)

- [**GoReSym**](https://github.com/mandiant/GoReSym)

  Recover Go build metadata, function names and address ranges, source file and line tables, embedded types and strings from Go binaries, including stripped and some malformed unpacked samples. JSON output can be imported into IDA Pro with the included IDAPython script.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/goresym/)

- [**rev.ng**](https://github.com/revng/revng)

  Open-source decompilation pipeline that lifts x86-64, AArch64, i386, ARM and MIPS code with QEMU, runs LLVM-based analyses and emits C designed to be valid and recompilable. Data layout analysis infers structures from pointer use; an editable YAML model and Python or TypeScript wrappers support automation. Its VSCode-based UI is a separate closed-beta product, with commercial plans announced.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/revng/)

<a id="firmware"></a>
### Firmware and Hardware

[↑ Contents](#contents)

#### Case studies

- [**ThinkPad IMX471: recovering camera tuning for Linux**](https://github.com/cschalle/mipi-fixes-x1-aura)

  Recovers selected camera-tuning structures from an Intel Windows driver package and uses them to repair Linux image capture on one ThinkPad model. Public CPFF/AIQB parsers, kernel patches and libcamera changes accompany the author’s Claude-assisted investigation and bounded before/after measurements.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/thinkpad-imx471-camera-case/)

- [**flipper-telink: replacement firmware for Tuya Zigbee remotes**](https://github.com/ngxson/flipper-telink)

  A Flipper Zero app that bit-bangs Telink’s SWire debug interface to dump and reflash TLSR825x Zigbee devices, with static-analysis notes on the dumps and freshly written firmware for two of them. For Tuya TS0044/TS0046 scene remotes, the notes trace the stock \~500 ms single-click delay to a double-click window; the replacement firmware drops that window while presenting the stock model IDs to Zigbee2MQTT. The latest Zigbee build is marked unverified for pairing, actions and battery reporting.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/flipper-telink-tuya-remote-firmware-case/)

#### Tools, projects and integrations

- [**Binwalk**](https://github.com/ReFirmLabs/binwalk)

  Identifies embedded formats and optionally extracts their contents, with entropy analysis for firmware triage.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/binwalk/)

- [**unblob**](https://github.com/onekey-sec/unblob)

  Recursively extracts archives and filesystems from binary blobs while reporting chunk boundaries and unknown regions.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/unblob/)

- [**Ghidra Firmware Utilities**](https://github.com/al3xtjames/ghidra-firmware-utils)

  Ghidra loaders and helpers for PCI option ROMs, UEFI firmware volumes, Intel flash descriptors and coreboot images.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/ghidra-firmware-utils/)

- [**EMBA**](https://github.com/e-m-b-a/emba)

  Extract firmware, combine static checks with emulation-based analysis, inventory software components, and generate web reports and SBOMs for further investigation.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/emba/)

- [**Firmware Analysis and Comparison Tool (FACT)**](https://github.com/fkie-cad/FACT_core)

  Unpack and analyze firmware through an extensible platform whose web interface and HTTP API make component contents and analysis results searchable and comparable across samples.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/fact-core/)

- [**OFRAK**](https://github.com/redballoonsecurity/ofrak)

  Recursively identify, unpack, analyze, modify, and repack firmware and binary formats using a resource-tree GUI and Python API, with optional disassembler backends.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/ofrak/)

- [**FirmAE**](https://github.com/pr0v3rbs/FirmAE)

  Emulate router and IP-camera firmware to inspect network services and runtime behavior, with automated emulation checks and separate analysis, run, and debugging modes.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/firmae/)

- [**PulseView**](https://github.com/sigrokproject/pulseview)

  Examine captured logic and analog waveforms with sigrok's graphical frontend. Protocol decoders and decoder stacking expose bus messages and higher-level device operations, making hardware communication traces useful for firmware and interoperability investigations.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/pulseview/)

- [**UEFITool**](https://github.com/LongSoft/UEFITool)

  Parse UEFI firmware images into an inspectable tree and check their structure. Companion UEFIExtract and UEFIFind tools extract parsed contents and locate patterns, supporting analysis of firmware components and vendor formats.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/uefitool/)

- [**Glasgow Interface Explorer**](https://github.com/GlasgowEmbedded/glasgow)

  Use FPGA-based open hardware and Python applets to read and write SPI flash, I2C EEPROM and parallel memory chips, determine JTAG pinouts, debug supported processors and analyze UART, SPI and QSPI transactions on physical devices.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/glasgow-interface-explorer/)

- [**Penguin**](https://github.com/rehosting/penguin)

  Rehost embedded Linux firmware from an extracted root filesystem using a generated, editable configuration of emulation transformations, then refine it through a guest root shell, forwarded network services and recorded dynamic-analysis output.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/penguin/)

<a id="protocol"></a>
### Protocol

[↑ Contents](#contents)

#### Case studies

- [**open-appleremote: Siri Remote protocol reconstruction**](https://github.com/a-funk/open-appleremote)

  Reconstructs first-generation Siri Remote Bluetooth reports for Linux, decoding buttons, touch and tvOS-style gestures. The Python implementation and protocol notes distinguish measured behavior, historical reports and inferred meanings.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/open-appleremote-case/)

- [**GAMEKB-K17: reconstructing a macropad configuration protocol**](https://github.com/dvdarkin/gamekb-k17)

  Implements the vendor HID configuration protocol for the GAMEKB-K17/HCY-K017 macropad. It writes key mappings, firmware macros and RGB settings, then reads them back; protocol notes separate tested commands from unconfirmed observations and other-device findings.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/gamekb-k17-case/)

- [**cooler-lcd: a Thermalright display protocol implementation**](https://github.com/kristjaningi/cooler-lcd)

  Implements a USB picture-transfer driver for Thermalright Vision cooler displays, with a Rust dashboard replacing the vendor display application. The documented protocol sends a header and JPEG frames, with periodic resends to prevent the device reverting to its logo.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/cooler-lcd-case/)

- [**NJFE: a Soulear camera protocol bridge for desktop inspection**](https://github.com/WildweaselMS/NJFE)

  Reuses otoscope's reverse-engineered i4season/Soulear protocol in an ESP32-C3 bridge and Python desktop viewer. The author credits Claude Code for implementation and reports streaming one Hopefox Find T to a Windows PC, with recording, orientation and LED controls.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/njfe-ear-camera-bridge-case/)

- [**hw-harness: scanner USB protocol investigation**](https://github.com/cschalle/hw-harness)

  Documents an author-reported scanner investigation comparing vendor-driver USB control transfers with Linux-driver traces to infer initialization, timing and resolution parameters. The released harness organizes reference capture and comparison; it does not automatically recover a complete protocol specification.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/hw-harness-reference-case/)

#### Tools, projects and integrations

- [**Wireshark**](https://gitlab.com/wireshark/wireshark)

  Inspect captured application and device traffic as decoded protocol fields, with filtering and shared GUI/TShark dissection. Custom dissectors let an analyst encode newly understood packet formats and compare protocol implementations.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/wireshark/)

- [**Netzob**](https://github.com/netzob/netzob)

  Model communication protocols and infer message layouts from traces, with configured active learning for protocol state machines. Python APIs expose message fields, symbols and automata for parsing, traffic generation and fuzzing.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/netzob/)

- [**Scapy**](https://github.com/secdev/scapy)

  Script packet dissection, construction, request/reply matching and capture-file analysis in Python. Custom packet fields and layer bindings let analysts encode understood wire formats and investigate protocol behavior.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/scapy/)

- [**Universal Radio Hacker (URH)**](https://github.com/jopohl/urh)

  Demodulate and decode signals captured with software-defined radios, with automatic modulation-parameter detection and customizable decodings. Analysts assign protocol fields and message types by hand or review rule-based automatic field inference; a fuzzer targets stateless protocols and a simulator supports stateful exchanges.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/universal-radio-hacker/)

- [**SavvyCAN**](https://github.com/collin80/SavvyCAN)

  Capture or load CAN bus traffic and investigate frames with sniffer, graphing, file-comparison and ISO-TP/UDS decoding views; loaded or analyst-edited DBC files map raw bytes to named signals. Separate custom-sender, fuzzing and UDS-scan windows transmit frames on a live bus.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/savvycan/)

- [**AALpy**](https://github.com/DES-Lab/AALpy)

  General-purpose Python automata-learning library that infers deterministic, non-deterministic, stochastic and pushdown models of black-box systems from active queries or passive traces. Its README links a separate Bluetooth Low Energy study whose repository reports learned connection and legacy-pairing state machines; message formats are not inferred.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/aalpy/)

- [**rtl\_433**](https://github.com/merbanan/rtl_433)

  Receives and decodes transmissions from ISM-band devices such as weather sensors, remote controls, doorbells and alarm sensors, using RTL-SDR or SoapySDR receivers or recorded I/Q files, and emits decoded fields as JSON, CSV, MQTT and other outputs. For signals no built-in decoder recognizes, a pulse analyzer reports OOK/FSK timings and hints for a flexible -X decoder that slices frames into bits; its analysis guide leaves mapping those bits to values to the analyst, working from known readings.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/rtl-433/)

<a id="agents-and-mcp"></a>
### Agents and MCP

[↑ Contents](#contents)

- [**REA — Reverse Engineer Anything**](https://github.com/morluto/rea)

  The upstream CLI and MCP server for evidence-based investigations of shipped software and runtime behavior.

  Project · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-upstream/)

- [**Official reverse-engineer-anything skill**](https://github.com/morluto/rea/tree/main/.agents/skills/reverse-engineer-anything)

  Target routing, connection recovery and evidence practices for agents using REA.

  Integration · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-official-skill/)

- [**dsh-mcp-rea**](https://github.com/Ersith/dsh-mcp-rea)

  A community MCP bridge presents a smaller selected tool surface and forwards explicit commands to the REA CLI.

  Integration · REA · [Requirements & evidence](https://awesomerea.org/resources/dsh-mcp-rea/)

- [**rea-jev**](https://github.com/juan-viox/rea-jev)

  A Claude Code plugin adds Jev-based routing and evidence checks around a pinned REA MCP integration.

  Integration · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-jev/)

- [**rea-casebook**](https://github.com/pablodiazjorge/rea-casebook)

  A Claude Code mod collects received REA Evidence, tracks unknowns and records findings that cite delivered evidence IDs.

  Integration · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-casebook/)

- [**Eleven**](https://github.com/Zfinix/eleven)

  An agent-first desktop reverse-engineering app that opens Mach-O, ELF and PE binaries, Android packages and GPU kernels, and lets any Agent Client Protocol agent read code, rename functions, add notes and propose patches in a shared window. Native code is decompiled by Ghidra through a bundled REA build, with Rizin and jadx as alternative engines. It is a workbench around existing engines, not a new decompiler or a reconstruction case.

  Integration · REA · [Requirements & evidence](https://awesomerea.org/resources/eleven-agent-re-workbench/)

- [**Hex-Rays IDA MCP**](https://github.com/HexRaysSA/ida-mcp)

  Official Hex-Rays MCP server for agent access to IDA databases, with headless operation and optional GUI integration.

  Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/hex-rays-ida-mcp/)

- [**GhidraMCP**](https://github.com/LaurieWired/GhidraMCP)

  Ghidra extension and MCP bridge exposing decompilation, symbol navigation and renaming to agents, with GUI and headless modes.

  Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/ghidramcp/)

- [**Binary Ninja MCP (official)**](https://docs.binary.ninja/guide/mcp.html)

  Binary Ninja's own MCP interface exposes functions, symbols, disassembly, intermediate languages and decompiled text to agents.

  Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/binary-ninja-official-mcp/)

- [**Binary Ninja MCP (fosdickio)**](https://github.com/fosdickio/binary_ninja_mcp)

  Community Binary Ninja plugin and bridge for MCP clients, including workflows that switch among multiple open binaries.

  Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/binary-ninja-community-mcp/)

- [**IDA Pro MCP (mrexodia)**](https://github.com/mrexodia/ida-pro-mcp)

  Community IDA integration useful for existing setups and migration context; its maintainer now recommends the official Hex-Rays MCP server.

  Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/ida-pro-mcp-community/)

- [**Radare2 MCP Server**](https://github.com/radareorg/radare2-mcp)

  Native radare2 MCP server offering binary-analysis tools, reusable sessions and configurable read-only access.

  Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/radare2-mcp/)

- [**r2ai**](https://github.com/radareorg/r2ai)

  AI plugins inside radare2 for function explanations, naming suggestions and model-assisted decompilation using local or remote models.

  Integration · Independent agent · [Requirements & evidence](https://awesomerea.org/resources/r2ai/)

- [**DAILA**](https://github.com/mahaloz/DAILA)

  Decompiler-independent AI assistant for function summaries and naming across IDA, Ghidra, Binary Ninja and angr-management.

  Integration · Independent agent · [Requirements & evidence](https://awesomerea.org/resources/daila/)

- [**RevEng.AI Ghidra Plugin**](https://github.com/RevEngAI/plugin-ghidra)

  Connects Ghidra to RevEng.AI for function similarity, recovered names, AI explanations and agent-assisted annotation.

  Integration · Independent agent · [Requirements & evidence](https://awesomerea.org/resources/revengai-ghidra/)

- [**LLDB MCP**](https://lldb.llvm.org/use/mcp.html)

  LLDB's official MCP interface gives agents debugger sessions and commands for breakpoints, memory inspection and stepping.

  Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/lldb-mcp/)

- [**Claude Reverse Engineering Skill**](https://github.com/EncidXVII/claude-reverse-engineering-skill)

  Community agent skill for triage, headless exports and evidence-based RE reports; explicitly documents workflows with REA and other MCP servers.

  Integration · Independent agent · [Requirements & evidence](https://awesomerea.org/resources/claude-reverse-engineering-skill/)

- [**SpecterOps Reverse Engineering Skills**](https://github.com/SpecterOps/skills/tree/main/plugins/reverse-engineering)

  Focused Binary Ninja and Ghidra analysis skills that describe MCP tool use, analysis recipes and annotation practices.

  Integration · Independent agent · [Requirements & evidence](https://awesomerea.org/resources/specterops-re-skills/)

- [**pyghidra-mcp**](https://github.com/clearbluejar/pyghidra-mcp)

  PyGhidra-based MCP server that analyzes every binary in a Ghidra project and exposes decompilation, cross-references, call graphs, symbol and string search, indexed semantic code search, and renaming, typing and comment edits. A separate HTTP CLI client and an optional mode driving a Ghidra GUI it launches are included.

  Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/pyghidra-mcp/)

- [**LeanREA**](https://github.com/aicodeking/leanrea)

  An independent agent skill that routes application and binary investigations through ordinary command-line tools. It supplies batched triage recipes, targeted source/disassembly reading and explicit seen/inferred/unknown evidence labels, accompanied by a small author-reported comparison against an REA MCP workflow.

  Integration · Independent agent · [Requirements & evidence](https://awesomerea.org/resources/leanrea-skill/)

- [**Universal Modder**](https://github.com/rehan-remade/universal-modder)

  Packages agent skills, three role briefs, a Python CLI and preconfigured fal MCP settings for modding PC games the user owns. Its reverse-engineering guidance sends managed, native and data-format work to external decompilers and debuggers, and requires a round-trip check before a reverse-engineered file format is used; one worked example ships an Age of Empires II sprite writer built this way. It is a modding toolkit with agent-written field notes, not a game decompilation, and its example results remain project-reported.

  Integration · Independent agent · [Requirements & evidence](https://awesomerea.org/resources/universal-modder-agent-toolkit/)

<a id="related-collections"></a>
### Related Collections

[↑ Contents](#contents)

- [**Awesome Reverse Engineering**](https://github.com/morluto/awesome-reverse-engineering)

  A task-oriented reverse-engineering resource list by REA's maintainer, useful for broader tools and foundations.

  Collection · [Requirements & evidence](https://awesomerea.org/resources/morluto-awesome-re/)

- [**Awesome REA Cases**](https://github.com/songshikang0111/awesome-REA-cases)

  A bilingual collection of REA and other AI-assisted reverse engineering cases, with source links and explicit distinctions between reported and reproduced outcomes.

  Collection · [Requirements & evidence](https://awesomerea.org/resources/awesome-rea-cases/)

- [**awesome-rea (yibie): verification-focused projects and practice reports**](https://github.com/yibie/awesome-rea)

  Organizes AI-assisted game decompilation, native ports, static recompilation and tooling around stated acceptance checks, alongside a separate track of practitioner write-ups and discussions. Useful for finding primary reports and comparing how projects define correctness.

  Collection · [Requirements & evidence](https://awesomerea.org/resources/yibie-awesome-rea/)

- [**Awesome REA/Decompiled Games**](https://github.com/HaozheH3/awesome-rea-games)

  Groups game decompilations, source reconstructions, recompilations, native ports and demos by original game, with comparison rows linking related projects. It distinguishes launchers, engine work and creator-shared showcases from source-reconstruction efforts.

  Collection · [Requirements & evidence](https://awesomerea.org/resources/haozhe-awesome-rea-games/)

<a id="references-and-learning"></a>
### References and Learning

[↑ Contents](#contents)

- [**Installation and client setup**](https://github.com/morluto/rea/blob/main/docs/installation.md)

  Reviewed setup plans, client registration, provider prerequisites and scoped readiness checks.

  Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-installation/)

- [**CLI and Evidence**](https://github.com/morluto/rea/blob/main/docs/cli.md)

  CLI workflows for saving Evidence and projecting smaller views from completed analysis.

  Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-cli-evidence/)

- [**MCP contracts and generated catalog**](https://github.com/morluto/rea/blob/main/docs/mcp-contracts.md#generated-catalog)

  Canonical tool contracts, provider discovery and Evidence semantics for integration authors.

  Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-mcp-contracts/)

- [**Native binary investigation**](https://github.com/morluto/rea/blob/main/docs/native-investigation.md)

  Locate a function, inspect instructions and pseudocode, and follow references with a selected native provider.

  Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-native-workflow/)

- [**Cross-layer JavaScript application workflows**](https://github.com/morluto/rea/blob/main/docs/javascript-application-workflows.md)

  Trace features and compare authenticated JavaScript application graphs while preserving static-analysis limits.

  Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-js-workflows/)

- [**Static Android APK analysis**](https://github.com/morluto/rea/blob/main/docs/android-analysis.md)

  Inspect Android package identity, classes, methods and references through REA's JADX integration.

  Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-android-guide/)

- [**Managed-code analysis**](https://github.com/morluto/rea/blob/main/docs/managed-code-analysis.md)

  Read PE/CLI metadata and CIL, compare managed members and inspect declared native boundaries without loading the assembly.

  Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-managed-guide/)

- [**Historical web network captures**](https://github.com/morluto/rea/blob/main/docs/web-network-captures.md)

  Inspect saved web captures offline; recorded URLs are not fetched and no proxy is started.

  Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-web-captures/)

- [**Firmware analysis**](https://github.com/morluto/rea/blob/main/docs/firmware-analysis.md)

  Inspect firmware regions with Binwalk and explicitly extract with Unblob, retaining tool and artifact identity.

  Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-firmware-guide/)

- [**Recorded packet capture inspection**](https://github.com/morluto/rea/blob/main/docs/packet-captures.md)

  Select TShark fields, display filters and decode-as rules over an existing network, USB or Bluetooth capture, and look up installed field names. It does not capture traffic, open an interface or control a device.

  Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-packet-captures/)

- [**Packet capture summaries**](https://github.com/morluto/rea/blob/main/docs/pcap-analysis.md)

  Summarize a saved pcap or pcapng file’s endpoints, DNS questions and addresses, TLS SNI, protocol stacks and HTTP URIs into paged Evidence views. It does not capture traffic or fetch recorded targets.

  Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-pcap-summaries/)

- [**Recorded signal decoding**](https://github.com/morluto/rea/blob/main/docs/signal-recordings.md)

  Run caller-chosen sigrok protocol decoders, such as UART or I2C, over an existing logic-signal recording and keep annotation text with sample ranges. It does not acquire samples or communicate with hardware.

  Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-signal-recordings/)

- [**Browser observation guide**](https://rea.tools/guides/browser/)

  Follow a user-triggered export request in the supplied Notes browser example and connect it to the downloaded result.

  Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-browser-guide/)

- [**JavaScript and Electron: follow a CSV export**](https://rea.tools/guides/javascript/)

  A source-owned Notes fixture teaches the renderer, preload, IPC and CSV path with linked analysis evidence.

  Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-electron-guide/)

- [**rea-playbook**](https://github.com/jinshi666888/rea-playbook)

  An Electron practice target, Evidence extractor and MCP probe; offline fixture mode is distinguished from real REA analysis.

  Learning resource · [Requirements & evidence](https://awesomerea.org/resources/rea-playbook/)

- [**rea-lab**](https://github.com/pablodiazjorge/rea-lab)

  A Windows REA/Ghidra lab with seeded challenges, published studies, upstream contributions and recorded limitations.

  Research · [Requirements & evidence](https://awesomerea.org/resources/rea-lab/)

- [**Flutter build identification**](https://github.com/morluto/rea/blob/main/docs/flutter-analysis.md)

  Identifies a Flutter APK’s Dart snapshot hash, per-ABI library digests and engine build provenance, then inspects one ABI’s AOT snapshot sections, through REA’s pure-parsing CLI and MCP tools. The string-pool output is a bounded byte-pattern projection of package and SDK URIs, not deserialized Dart classes or recovered source.

  Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-flutter-guide/)

- [**Static HarmonyOS package inventory**](https://github.com/morluto/rea/blob/main/docs/harmony-analysis.md)

  Inventories HarmonyOS HAP, HSP and App Pack files through REA’s hardened ZIP reader and projects an execution-free application graph: component paths, IDs and hashes, Stage/FA packaging hints, runtime-family hints and path-based native-bridge hypotheses. Every claim rests on path presence; manifests, Ark bytecode, resources and signatures are not decoded or verified.

  Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-harmony-guide/)

- [**MIPS ELF analysis through Ghidra**](https://github.com/morluto/rea/blob/main/docs/ghidra-mips.md)

  Documents REA’s Ghidra lane for MIPS ELF executables, relocatable objects and MIPS16 shared images, including a pinned 32-bit language for recordless legacy firmware executables that Ghidra would otherwise import as 64-bit. Admission is bounded by declared header and ABI-record facts, and verification compares source-owned fixtures with independent readelf output rather than executing or rehosting firmware.

  Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-ghidra-mips-guide/)

- [**PSP static ELF analysis through Ghidra**](https://github.com/morluto/rea/blob/main/docs/ghidra-psp.md)

  Documents REA’s bounded Ghidra profile for static PSP ELF executables, which leaves Allegrex instructions, PSP loading and calling conventions to a caller-installed ghidra-allegrex extension while reusing REA’s CLI, MCP, Evidence and snapshot workflows. It admits one PSPSDK header and ABI declaration on Linux x64 and verifies selected static facts on a self-built fixture, not commercial games or PRX modules.

  Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-ghidra-psp-guide/)

- [**NativeAOT metadata recovery with Ghidra**](https://github.com/morluto/rea/blob/main/docs/ghidra-nativeaot.md)

  Recovers .NET 8 NativeAOT metadata from x64 PE executables during REA’s Ghidra analysis: MethodTable relationships, virtual slots and frozen strings from RTR 9.1 data, through a built-in read-only parser or an optional headless adapter that annotates the Ghidra database. Generated names, inferred prototypes and recovered native pseudocode stay separate from the unknown original C# names, fields and source.

  Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-ghidra-nativeaot-guide/)

- [**OpenSecurityTraining2**](https://ost2.fyi/)

  Free self-paced security courses with learning paths for reverse engineering, firmware and systems foundations.

  Learning resource · [Requirements & evidence](https://awesomerea.org/resources/ost2/)

- [**pwn.college: Reverse Engineering**](https://pwn.college/program-security/reverse-engineering/)

  Hands-on reverse-engineering module covering functions, data access, static tools and dynamic tools with hosted exercises.

  Learning resource · [Requirements & evidence](https://awesomerea.org/resources/pwn-college-re/)

- [**Reverse Engineering for Beginners**](https://beginners.re/)

  Dennis Yurichev's free book on understanding compiled programs and assembly, available in multiple languages.

  Learning resource · [Requirements & evidence](https://awesomerea.org/resources/re-for-beginners/)

- [**The Official Radare2 Book**](https://book.rada.re/)

  Official practical reference for radare2 analysis, disassembly, scripting, debugging and related plugins.

  Learning resource · [Requirements & evidence](https://awesomerea.org/resources/radare2-book/)
<!-- END GENERATED CATALOG -->

<!-- BEGIN GENERATED PAPERS -->
<a id="papers"></a>
## Papers

**58 papers**, grouped by topic and ordered newest first. Each entry shows its publication status.

[Browse the paper directory](https://awesomerea.org/papers/) · [Complete bibliography JSON](data/papers.json) · [Suggest a paper](https://github.com/reacher-z/Awesome-REA/issues/new?template=paper.yml)

**By topic**

- [Agent evaluation](#papers-agent-evaluation) (7) · [Decompilation](#papers-decompilation) (12) · [Websites](#papers-website-reconstruction) (13)
- [Games](#papers-game-reconstruction) (6) · [Apps](#papers-app-reconstruction) (6) · [Firmware](#papers-firmware-analysis) (5)
- [Protocols](#papers-protocol-analysis) (9)

Open “Scope and publication details” for each study’s full limitations. Some papers also appear among curated resources; counts are not additive.

<a id="papers-agent-evaluation"></a>
### Reverse-engineering agent evaluation

[↑ Paper topics](#papers) · [Contents](#contents)

- [**Humans vs. Machines: A Comparison With AI Agents in Software Reverse Engineering**](https://arxiv.org/abs/2610.14960)

  Compares human and LLM-agent understanding and navigation on the same static reverse-engineering challenges, then studies how binary representations consume context windows.

  2026 · Preprint · [PDF](https://arxiv.org/pdf/2610.14960) · [Full entry & citation](https://awesomerea.org/papers/paper-humans-machines-sre/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Understanding is graded on two compact challenges; the separate 4,000-binary study measures context capacity, not task-solving accuracy. The interface is static IDA/MCP without dynamic execution, and prior exposure to challenge source remains an acknowledged validity threat.

  **Publication:** 2026 · arXiv · Preprint · Samuele Doria et al.

  </details>

- [**The Next Challenge for Agentic Cybersecurity: A Realistic, Contamination-Free Reverse Engineering Benchmark**](https://arxiv.org/abs/2608.11469)

  Introduces SRE-Bench, with privately authored programs and protected binary variants, to study agent recovery of program semantics while reducing training-data contamination.

  2026 · Preprint · [PDF](https://arxiv.org/pdf/2608.11469) · [Full entry & citation](https://awesomerea.org/papers/paper-sre-bench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The revised study reports 19 programs, 262 binary instances, and 1,572 graded tasks. Binaries and task instances are not publicly released; access is through an evaluation service. Its contamination-control claim is the authors' methodology, not an independent guarantee.

  **Publication:** 2026 · arXiv · Preprint · Jeremy Spence et al.

  </details>

- [**CrackMeBench: Binary Reverse Engineering for Agents**](https://arxiv.org/abs/2605.10597)

  Evaluates agents on executable-checked CrackMe tasks: infer validation logic from binaries and submit an accepted input or artifact, while recording tool use, time, and scoring attempts.

  2026 · Preprint · [PDF](https://arxiv.org/pdf/2605.10597) · [Full entry & citation](https://awesomerea.org/papers/paper-crackmebench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The v0 study uses 12 generated tasks and eight public calibration tasks, Linux x86-64 ELF binaries, a shell interface, and a five-minute budget. Its compact educational tasks do not establish performance on large applications. No paper-linked public artifact URL was verified.

  **Publication:** 2026 · arXiv · Preprint · Isaac David et al.

  </details>

- [**Towards LLM-Resistant Software Protection: Agent Failure Patterns in CTF Reverse Engineering**](https://www.ndss-symposium.org/ndss-paper/auto-draft-657/)

  Runs Claude Code, Codex CLI and ChatGPT-5.2 Pro on 24 crackme-style challenges selected from 15 international CTF events held in 2025, and attributes their failures to stages of an Observe–Comprehend–Plan loop and to three protection effects: concealment, complication and misdirection. From the failure logs, the authors derive four recurring weaknesses (training bias, over-trust in observations, context limitation and plan persistence). They rerun both CLI agents without a decompiler and compare outcomes with in-competition solve rates.

  2026 · Conference paper · [PDF](https://www.ndss-symposium.org/wp-content/uploads/bar2026-58.pdf) · [Full entry & citation](https://awesomerea.org/papers/paper-llm-resistant-protection/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The study covers 24 locally solvable Linux x86-64 ELF crackmes and three commercial agents (Claude Opus 4.5 and GPT-5.1-Codex-Max in the CLI tools, and an undisclosed ChatGPT model), evaluated in December 2025 with network access; runs that consulted public write-ups were excluded. The binaries are small relative to real-world software, and malware analysis and vulnerability discovery are out of scope. Each configuration had at most three attempts with early stopping, which the authors call noisy; success means printing the correct flag or finding an accepted input. Weakness labels come from qualitative log analysis by two evaluators and describe these runs, not general properties of LLM agents. ChatGPT-5.2 Pro ran in an uncontrolled web sandbox and is excluded from the decompiler comparison. Solve rates are among teams that solved at least one challenge, unavailable for six tasks, and may include LLM-assisted teams. Training-data exposure remains a validity threat, and the paper does not publish its assembled challenge set, run logs or code.

  **Publication:** 2026 · Workshop on Binary Analysis Research (BAR) 2026 · Conference paper · Ryutaro Nishizaka et al.

  </details>

- [**ProgramBench: Can Language Models Rebuild Programs From Scratch?**](https://arxiv.org/abs/2605.03546)

  Evaluates black-box program reconstruction across 200 tasks: agents query an executable and read its documentation, then independently implement a codebase whose behavior is checked by generated tests.

  2026 · Accepted · [PDF](https://arxiv.org/pdf/2605.03546v1) · [Code](https://github.com/facebookresearch/ProgramBench) · [Full entry & citation](https://awesomerea.org/papers/paper-programbench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Binary inspection, decompilation, and internet access are forbidden during inference. Passing finite tests does not prove complete behavioral equivalence or recovery of the original source. Later live-leaderboard runs are separate from the reviewed arXiv results.

  **Publication:** 2026 · NeurIPS 2026 · Accepted · John Yang et al.

  </details>

- [**CREBench: Evaluating Large Language Models in Cryptographic Binary Reverse Engineering**](https://openreview.net/forum?id=tLYdf8hWJB)

  Benchmarks cryptographic binary reverse engineering across algorithm recognition, key or IV extraction, wrapper reconstruction, and flag recovery using 432 controlled challenges.

  2026 · Conference paper · [PDF](https://arxiv.org/pdf/2604.03750v2) · [Code](https://github.com/wangyu-ovo/CREBench) · [Full entry & citation](https://awesomerea.org/papers/paper-crebench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The corpus combines 48 algorithms, three insecure key-use scenarios, and three difficulty levels. It excludes professional-grade obfuscators such as Tigress and O-LLVM; results should not be generalized to heavily protected arbitrary binaries.

  **Publication:** 2026 · COLM 2026 · Conference paper · Baicheng Chen et al.

  </details>

- [**NYU CTF Bench: A Scalable Open-Source Benchmark Dataset for Evaluating LLMs in Offensive Security**](https://proceedings.neurips.cc/paper_files/paper/2024/hash/69d97a6493fbf016fff0a751f253ad18-Abstract-Datasets_and_Benchmarks_Track.html)

  NYU CTF Bench packages 200 manually validated challenges from CSAW CTF qualifying and final rounds held between 2017 and 2023, spanning cryptography, forensics, pwn, reverse engineering, web and miscellaneous tasks, with challenge.json metadata and Docker images for server-side challenges. The paper also presents an automated framework that gives LLMs function-calling tools for shell commands, file creation, Ghidra disassembly and decompilation, flag checking and giving up. It evaluates five LLMs and compares their scores with human teams at CSAW 2022 and 2023.

  2024 · Conference paper · [PDF](https://proceedings.neurips.cc/paper_files/paper/2024/file/69d97a6493fbf016fff0a751f253ad18-Paper-Datasets_and_Benchmarks_Track.pdf) · [Code](https://github.com/NYU-LLM-CTF/NYU_CTF_Bench) · [Full entry & citation](https://awesomerea.org/papers/paper-nyu-ctf-bench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Only 51 of the 200 challenges are reverse engineering (31 qualifying and 20 final), so overall solve rates are not reverse-engineering accuracy. All challenges come from one competition series, categories are imbalanced, and the remaining 367 of the initial 567 challenges, including incident-response tasks, are excluded pending validation. The baseline counts a challenge as solved if any of five attempts succeeds, within a 48-hour limit per model; no statistical tests were run. Among GPT-3.5, GPT-4, Claude 3, Mixtral and LLaMA, the best reverse-engineering rate was 9.80% (GPT-4), and the open models solved nothing. The human comparison uses competition scores from four CSAW events, and the public repository has continued to change after publication, so later runs may not match the paper’s challenge set or framework.

  **Publication:** 2024 · NeurIPS 2024 Datasets and Benchmarks · Conference paper · Minghao Shao et al.

  </details>

<a id="papers-decompilation"></a>
### Decompilation and symbol recovery

[↑ Paper topics](#papers) · [Contents](#contents)

- [**SK2Decompile: LLM-based Two-Phase Binary Decompilation from Skeleton to Skin**](https://proceedings.iclr.cc/paper_files/paper/2026/hash/9132583dd869acb0cafeb0ed25eb031a-Abstract-Conference.html)

  Splits LLM decompilation into two phases: a Structure Recovery model turns decompiler pseudocode into an identifier-free IR that keeps control flow and data structures, trained with compiler-based RL rewards, and an Identifier Naming model then restores names under a semantic-similarity reward. The authors report a 21.6% average re-executability gain over GPT-5-mini on HumanEval and a 29.4% average R2I improvement over Idioms on GitHub2025.

  2026 · Conference paper · [PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/9132583dd869acb0cafeb0ed25eb031a-Paper-Conference.pdf) · [Code](https://github.com/albertan017/LLM4Decompile/tree/85b364bf093eb2ee4f3687cfe38a203fca89f23e/sk2decompile) · [Full entry & citation](https://awesomerea.org/papers/paper-sk2decompile/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Training and main evaluation use function-level C compiled for x86-64 Linux with GCC and Clang at -O0 to -O3, with IDA Pro pseudocode as model input. Re-executability is measured only on HumanEval and MBPP; ExeBench and GitHub2025 use R2I readability and a GPT-5-mini judge. Appendix experiments extend to BringUpBench projects, macOS arm64 and Windows MSVC builds, and Obfuscator-LLVM, but the models are trained on C only and the paper expects them to degrade on features without C equivalents, such as C++ templates.

  **Publication:** 2026 · ICLR 2026 · Conference paper · Hanzhuo Tan et al.

  </details>

- [**DecompileBench: A Comprehensive Benchmark for Evaluating Decompilers in Real-World Scenarios**](https://aclanthology.org/2025.findings-acl.1194/)

  Evaluates traditional and LLM-based decompilers using functions from real programs, runtime behavioral checks, and an LLM-assisted assessment of analyst-facing code understandability.

  2025 · Conference paper · [PDF](https://aclanthology.org/2025.findings-acl.1194.pdf) · [Code](https://github.com/vul337/DecompileBench) · [Full entry & citation](https://awesomerea.org/papers/paper-decompilebench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The evaluated corpus has 23,400 functions from 130 programs. Fuzzing-based checks have finite coverage, and understandability scores depend partly on an LLM judge. The artifact warns that rebuilt OSS-Fuzz projects can differ from the paper's versions.

  **Publication:** 2025 · Findings of ACL 2025 · Conference paper · Zeyu Gao et al.

  </details>

- [**TypeForge: Synthesizing and Selecting Best-Fit Composite Data Types for Stripped Binaries**](https://ieeexplore.ieee.org/document/11023499)

  TypeForge recovers composite data types, including struct layouts, unions and pointer or nesting relationships, from stripped binaries. A whole-program Type Flow Graph over Ghidra’s decompiler-inferred variables propagates member offsets and sizes, cuts conflicting edges caused by casts and unions, and synthesizes candidate type declarations. An LLM only selects among these statically synthesized candidates: each is applied through the decompiler’s retype interface, and a double-elimination tournament compares the resulting pseudocode for readability. On OSPREY’s coreutils dataset the authors report F1 of 81.7% for composite-type identification, 88.2% for layout recovery and 72.1% for relationship recovery.

  2025 · Conference paper · [PDF](https://noobone123.github.io/papers/typeforge-sp25.pdf) · [Code](https://github.com/noobone123/TypeForge) · [Full entry & citation](https://awesomerea.org/papers/paper-typeforge/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Recovers member offsets, sizes and relationships, not original type or member names; relationship correctness is judged by matching layouts because names are unavailable. The main evaluation uses OSPREY’s dataset of GNU coreutils and larger Howard-dataset programs, over 10,000 functions and 11,000 composite-typed variables at O0–O3, with ground truth from debug information; the paper does not report results per architecture. In the baseline comparison, OSPREY results were supplied by its authors and its runtime is an estimate, and ReSym figures are its published results, so not every baseline was rerun. Conservative removal of conflicting edges can drop valid members, and compiler optimizations that merge or flatten members lower accuracy at higher levels. About 75% of runtime is the LLM selection stage; the default model was GPT-4o mini, with each comparison run three times. Downstream readability and vulnerability examples are case studies, not proof of semantic equivalence.

  **Publication:** 2025 · IEEE S&amp;P 2025 · Conference paper · Yanzhong Wang et al.

  </details>

- [**Decompile-Bench: Million-Scale Binary-Source Function Pairs for Real-World Binary Decompilation**](https://papers.nips.cc/paper_files/paper/2025/hash/079cf13ae174c31f148207d94d213bdc-Abstract-Datasets_and_Benchmarks_Track.html)

  Introduces two million C/C++ binary-source function pairs using a Compile-Trace-Filter pipeline, with an evaluation suite spanning translated HumanEval/MBPP tasks and recent GitHub functions.

  2025 · Conference paper · [PDF](https://papers.nips.cc/paper_files/paper/2025/file/079cf13ae174c31f148207d94d213bdc-Paper-Datasets_and_Benchmarks_Track.pdf) · [Code](https://github.com/albertan017/LLM4Decompile) · [Full entry & citation](https://awesomerea.org/papers/paper-decompile-bench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** This is function-level decompilation. Re-execution tests cover HumanEval/MBPP; GitHub2025 provides no unit tests. Inlining can prevent one-to-one source correspondence, and the fine-tuning study uses 10% of the corpus. These results do not establish whole-program recovery.

  **Publication:** 2025 · NeurIPS 2025 Datasets and Benchmarks · Conference paper · Hanzhuo Tan et al.

  </details>

- [**ReSym: Harnessing LLMs to Recover Variable and Data Structure Symbols from Stripped Binaries**](https://doi.org/10.1145/3658644.3670340)

  Combines two fine-tuned language models with Prolog-based cross-function reasoning to infer local-variable symbols and user-defined data structures from stripped-binary decompilation.

  2024 · Conference paper · [PDF](https://www.cs.purdue.edu/homes/lintan/publications/resym-ccs24.pdf) · [Code](https://github.com/lt-asset/resym) · [Full entry & citation](https://awesomerea.org/papers/paper-resym/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The method depends on underlying decompilation and learned predictions over C/C++ data. Cross-checking reduces conflicting predictions but does not prove that recovered names or layouts match the unavailable source. The public artifact includes models, processed data, and evaluation code.

  **Publication:** 2024 · ACM CCS 2024 · Conference paper · Danning Xie et al.

  </details>

- [**LLM4Decompile: Decompiling Binary Code with Large Language Models**](https://aclanthology.org/2024.emnlp-main.203/)

  Trains language models for assembly-to-C decompilation and for refining Ghidra pseudocode, evaluating whether recovered functions can be recompiled and executed correctly.

  2024 · Conference paper · [PDF](https://aclanthology.org/2024.emnlp-main.203.pdf) · [Code](https://github.com/albertan017/LLM4Decompile) · [Full entry & citation](https://awesomerea.org/papers/paper-llm4decompile/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The paper limits its experiments to C on x86 and function-level benchmarks. Re-executability on sampled tests does not establish whole-program equivalence or recovery of the original source. Later repository releases are separate from the 2024 paper.

  **Publication:** 2024 · EMNLP 2024 · Conference paper · Hanzhuo Tan et al.

  </details>

- [**SLaDe: A Portable Small Language Model Decompiler for Optimized Assembly**](https://ieeexplore.ieee.org/document/10444788)

  SLaDe translates function-level assembly into C with a 200M-parameter encoder–decoder model, code-specific tokenization and PsycheC type completion. It studies x86 and ARM at -O0 and -O3, combining generated candidates with input/output checks. The input is assembly text, not raw machine bytes; disassembly is outside the method.

  2024 · Conference paper · [PDF](https://arxiv.org/pdf/2305.12520v3) · [Code](https://zenodo.org/records/10205121) · [Full entry & citation](https://awesomerea.org/papers/paper-slade/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Evaluation covers about 4,000 ExeBench functions and a 112-program synthesis suite. Beam size 5 selects the first candidate passing finite I/O tests; generated functions are inserted into the original calling context. Passing these tests is not whole-program or all-input equivalence. Edit similarity is a readability proxy. Longer functions, external calls and incorrect type/operator predictions remain failure modes; the model has 1,024-position source and target windows. Historical baseline comparisons have different coverage and do not establish current rankings.

  **Publication:** 2024 · IEEE/ACM CGO 2024 · Conference paper · Jordi Armengol-Estapé et al.

  </details>

- [**DeGPT: Optimizing Decompiler Output with LLM**](https://www.ndss-symposium.org/ndss-paper/degpt-optimizing-decompiler-output-with-llm/)

  Refines existing C-like decompiler output through three coordinated roles that select, propose and check changes. It simplifies structures, adds comments and renames variables; Micro Snippet Semantic Calculation compares simulated symbol values and calls before accepting structural changes. The authors evaluate readability and naming on 620 functions from four codebases, with separate stripped and non-stripped variants.

  2024 · Conference paper · [PDF](https://www.ndss-symposium.org/wp-content/uploads/2024-401-paper.pdf) · [Code](https://github.com/PeiweiHu/DeGPT) · [Full entry & citation](https://awesomerea.org/papers/paper-degpt/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The reported 24.4% reduction is a Halstead-effort proxy on non-stripped output, not a measured reduction in human effort. The 62.9% comment result is the average non-trivial share among manually judged correct comments. MSSC is an intraprocedural heuristic: calls are abstracted and loops become branches; parsing, aliasing and path growth remain limitations. Its 80-case manual audit reports 84% accuracy and 85% recall, including three harmful changes missed. This supports assisted pseudocode comprehension, not guaranteed binary equivalence, recompilable whole programs or original-source recovery.

  **Publication:** 2024 · NDSS 2024 · Conference paper · Peiwei Hu et al.

  </details>

- [**Augmenting Decompiler Output with Learned Variable Names and Types**](https://www.usenix.org/conference/usenixsecurity22/presentation/chen-qibin)

  Introduces DIRTY, a Transformer model that recommends variable names and types from decompiled code and layout information, together with the DIRT corpus for training and evaluation.

  2022 · Conference paper · [PDF](https://arxiv.org/pdf/2108.06363) · [Code](https://github.com/CMUSTRUDEL/DIRTY) · [Full entry & citation](https://awesomerea.org/papers/paper-dirty/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The original pipeline is built around C programs and Hex-Rays output. Predicted names and types are learned hypotheses, not guaranteed original symbols. The published paper is from 2022, although its arXiv preprint first appeared in 2021.

  **Publication:** 2022 · USENIX Security 2022 · Conference paper · Qibin Chen et al.

  </details>

- [**DIRE: A Neural Approach to Decompiled Identifier Naming**](https://doi.org/10.1109/ASE.2019.00064)

  Combines lexical and structural information from decompiler output to predict meaningful variable names, with a training and evaluation corpus derived from compiled C projects.

  2019 · Conference paper · [PDF](https://arxiv.org/pdf/1909.09029) · [Code](https://github.com/pcyin/dire) · [Full entry & citation](https://awesomerea.org/papers/paper-dire/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** This is learned identifier naming, not complete source reconstruction or an autonomous agent. Its reported results concern an x86-64 C corpus and depend on decompiler output. The original author repository is deprecated and points to a successor.

  **Publication:** 2019 · ASE 2019 · Conference paper · Jeremy Lacomis et al.

  </details>

- [**Coda: An End-to-End Neural Program Decompiler**](https://proceedings.neurips.cc/paper_files/paper/2019/hash/093b60fd0557804c8ba0cbf1453da22f-Abstract.html)

  Coda decompiles the assembly of short functions into C in two phases. An instruction-type-aware N-ary Tree-LSTM encoder and an attention-fed AST decoder first generate a code sketch; an ensemble of neural error predictors then proposes token corrections, each kept only if recompiling the candidate does not increase its edit distance to the input assembly. On synthetic benchmarks the authors report 82% average program accuracy after correction, against 12% for a sequence-to-sequence baseline with attention.

  2019 · Conference paper · [PDF](https://proceedings.neurips.cc/paper_files/paper/2019/file/093b60fd0557804c8ba0cbf1453da22f-Paper.pdf) · [Full entry & citation](https://awesomerea.org/papers/paper-coda/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Training and test programs are randomly generated from Karel commands, math.h calls and arithmetic or logical expressions, in short and long variants (average length 15 and 30), 50,000 pairs per task, compiled without optimization: clang -O0 for the main MIPS results and gcc -O0 for an x86-64 appendix that reports sketch token accuracy only, about 6% lower on average. Real-world checks are small PyTorch C++ API model-construction and Hacker's Delight loop-free programs. Program accuracy requires an exact token match with the ground-truth source, the metric under which the paper reports 0% for conventional decompilers. Error correction assumes the compiler configuration is known, and token accuracy drops for longer programs. The results show neither optimized, whole-program nor binary-equivalent decompilation, and the paper names no author implementation.

  **Publication:** 2019 · NeurIPS 2019 · Conference paper · Cheng Fu et al.

  </details>

- [**Debin: Predicting Debug Information in Stripped Binaries**](https://dl.acm.org/doi/10.1145/3243734.3243866)

  Debin predicts debug information for stripped ELF binaries on x86, x64 and ARM. After lifting code to BAP-IR, an Extremely randomized Trees classifier decides which registers and memory offsets hold source-level variables. A conditional random field, solved with Nice2Predict, then jointly predicts names and types for variables and functions, and the result is written back as DWARF sections. On 300 held-out binaries per architecture, the authors report 68.8% precision and 68.3% recall for x64 names and types.

  2018 · Conference paper · [PDF](https://files.sri.inf.ethz.ch/website/papers/ccs18-debin.pdf) · [Code](https://github.com/eth-sri/debin) · [Full entry & citation](https://awesomerea.org/papers/paper-debin/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The dataset has 3,000 non-stripped executables and shared libraries per architecture from 830 Linux debug-symbol packages of C code built with default package settings, split 2,700/300 for training and testing. Accuracy evaluation assumes given function boundaries; for fully stripped inputs, BAP's ByteWeight infers them, which the paper cites as about 93% accurate. Debin predicts 17 types, and leaves struct and union contents, line numbers and formats such as PE outside the evaluation. A prediction counts only when it equals the original debug value. Models learned from compiler-generated, benign code may be less accurate on obfuscated binaries, hand-written assembly or malware. The 35-sample malware study is manual inspection of decompiled output with no accuracy figures, because the samples lack ground-truth debug information.

  **Publication:** 2018 · ACM CCS 2018 · Conference paper · Jingxuan He et al.

  </details>

<a id="papers-website-reconstruction"></a>
### Website reconstruction

[↑ Paper topics](#papers) · [Contents](#contents)

- [**Vision2Web: A Hierarchical Benchmark for Visual Website Development with Agent Verification**](https://proceedings.mlr.press/v306/he26n.html)

  Benchmarks website development from visual prototypes and written requirements across 100 static-page, 66 interactive-frontend and 27 full-stack tasks, combining workflow-based functional checks with model-judged visual comparison.

  2026 · Conference paper · [PDF](https://raw.githubusercontent.com/mlresearch/v306/main/assets/he26n/he26n.pdf) · [Code](https://github.com/zai-org/Vision2Web) · [Full entry & citation](https://awesomerea.org/papers/paper-vision2web/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The full-stack tier is specification-driven, not reconstruction solely by exploring a live website. Workflows test state management and CRUD outcomes, but finite agent judgments do not establish exact backend or durable-database equivalence. The current public evaluator maintains a browser session within each workflow and permits local business-API checks; this is not a universal persistence proof.

  **Publication:** 2026 · ICML 2026 · Conference paper · Zehai He et al.

  </details>

- [**ProgramDistill: From Interactive Web Apps to Verifiable Reference-Guided SWE Tasks**](https://arxiv.org/abs/2609.18805)

  Evaluates recovery of web-app behavior from a live reference with hidden source. It provides 4,063 feature-restoration tasks across 26 applications and a separate 12-application reconstruction setting, scored by replaying dependent browser workflows.

  2026 · Preprint · [PDF](https://arxiv.org/pdf/2609.18805v1) · [Code](https://huggingface.co/datasets/microsoft/ProgramDistill) · [Full entry & citation](https://awesomerea.org/papers/paper-programdistill/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Tests cover finite, model-mined behaviors in self-contained apps, including SaaS clones. Persistence failures can be detected through replayed workflows, but passing does not establish all backend or database invariants. Evaluated agents receive structured browser observations without screenshots; visual fidelity is not measured. Public verifiers and reference solutions are not a contamination-resistant test set.

  **Publication:** 2026 · arXiv · Preprint · Jeonghye Kim et al.

  </details>

- [**UI2App: Benchmarking Visual Interaction Inference in Executable Web Application Generation**](https://arxiv.org/abs/2607.06306)

  UI2App evaluates runnable React/TypeScript applications generated from 600 screenshots across 95 web applications. It separates build executability, visual fidelity and screenshot-implied interaction behavior, including cross-route state, using a reference interaction taxonomy and public evaluation pipeline.

  2026 · Preprint · [PDF](https://arxiv.org/pdf/2607.06306v2) · [Code](https://github.com/chenmancm169/UI2App) · [Full entry & citation](https://awesomerea.org/papers/paper-ui2app/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Static screenshots underdetermine behavior; the rubric accepts multiple valid implementations rather than proving equivalence to the original application or backend. Auto IIS judges generated source and screenshots without tool execution; human runtime validation covers a 45-application subset. Cross-route state is not necessarily durable persistence across reloads or sessions. Main results use one generation per application-model pair, with repeated runs on a subset.

  **Publication:** 2026 · arXiv · Preprint · Grace Man Chen et al.

  </details>

- [**Dashboard2Code: Evaluating Multimodal Models on Reconstructing Interactive Dashboards**](https://aclanthology.org/2026.acl-long.1750/)

  Evaluates agents that actively explore a running dashboard and reconstruct its appearance and interaction logic. DashboardMimic provides 180 Plotly+Dash examples, with code-semantic analysis and dynamic interaction tests for the generated implementations.

  2026 · Conference paper · [PDF](https://aclanthology.org/2026.acl-long.1750.pdf) · [Code](https://github.com/nth2000/Dashboard2Code) · [Full entry & citation](https://awesomerea.org/papers/paper-dashboard2code/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Limited to Plotly+Dash dashboards, including model-augmented examples. Some settings expose DOM information and evaluation uses model judges. This is not a general backend-recovery benchmark. The linked dataset requires accepting access conditions and sharing contact information.

  **Publication:** 2026 · ACL 2026 · Conference paper · Tianhao Niu et al.

  </details>

- [**CASCADE: LLM-powered JavaScript Deobfuscator at Google**](https://doi.org/10.1145/3786583.3786873)

  Uses Gemini to locate the prelude functions that Obfuscator.IO inserts for string obfuscation, then applies constant-propagation and inlining passes in the JSIR compiler IR to restore string literals and API names deterministically.

  2026 · Conference paper · [PDF](https://arxiv.org/pdf/2507.17691v2) · [Code](https://github.com/google/jsir) · [Full entry & citation](https://awesomerea.org/papers/paper-cascade/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The method addresses Obfuscator.IO string obfuscation; control-flow flattening, other obfuscators and an agent-based design are future work. Evaluation obfuscates 3,000 programs from the ETH 150k JavaScript dataset with four Obfuscator.IO presets and measures prelude detection, recovered literals and run time, not functional equivalence. Production deployment and scan volume are author-reported, and production pre-filtering uses a proprietary YARA rule.

  **Publication:** 2026 · ICSE-SEIP 2026 · Conference paper · Shan Jiang et al.

  </details>

- [**ScreenCoder: Advancing Visual-to-Code Generation for Front-End Automation via Modular Multimodal Agents**](https://arxiv.org/abs/2507.22827)

  Splits screenshot-to-code generation among grounding, planning and generation agents that label UI regions, build a hierarchical layout tree and write HTML/CSS. The pipeline also produces the Screen-10K training pairs used for supervised and reinforcement fine-tuning, and the paper introduces the 1,000-page ScreenBench.

  2026 · Accepted · [PDF](https://arxiv.org/pdf/2507.22827v2) · [Code](https://github.com/leigest519/ScreenCoder) · [Full entry & citation](https://awesomerea.org/papers/paper-screencoder/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Output is static HTML/CSS layout; interaction, JavaScript behavior and backend logic are not reconstructed. Results are visual-similarity scores (CLIP and OCR-matched text blocks) on ScreenBench and Design2Code, which do not establish code-level or functional equivalence. The released pipeline calls a hosted model API, Doubao by default. The reviewed text is arXiv v2; the accepted EMNLP version may differ.

  **Publication:** 2026 · EMNLP 2026 · Accepted · Yilei Jiang et al.

  </details>

- [**IWR-Bench: Can LVLMs reconstruct interactive webpage from a user interaction video?**](https://proceedings.iclr.cc/paper_files/paper/2026/hash/55bfedfd31489e5ae83c9ce8eec7b0e1-Abstract-Conference.html)

  Tests reconstruction of interactive webpages from user-interaction videos and supplied static assets. Its 113 tasks replay annotated action sequences to assess visual fidelity and functional behavior across observed page states.

  2026 · Conference paper · [PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/55bfedfd31489e5ae83c9ce8eec7b0e1-Paper-Conference.pdf) · [Code](https://github.com/SIGMME/IWR-Bench) · [Full entry & citation](https://awesomerea.org/papers/paper-iwr-bench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The required output is one HTML file; the paper explicitly instructs models to mock implied backend logic with static JavaScript data. Trajectory coverage and model-based judgments do not prove complete website or backend equivalence.

  **Publication:** 2026 · ICLR 2026 · Conference paper · Yang Chen et al.

  </details>

- [**JsDeObsBench: Measuring and Benchmarking LLMs for JavaScript Deobfuscation**](https://doi.org/10.1145/3719027.3744871)

  Builds an execution-verifiable JavaScript deobfuscation benchmark by applying seven JavaScript-Obfuscator transformations to Project CodeNet programs with test cases, then scores LLM and tool outputs for syntax, execution, code simplification and similarity to the original code.

  2025 · Conference paper · [PDF](https://arxiv.org/pdf/2506.20170v1) · [Code](https://github.com/Ch3nYe/JsDeObsBench) · [Full entry & citation](https://awesomerea.org/papers/paper-jsdeobsbench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** On average, LLM outputs passed execution checks 60.93% of the time, against 83% for the two existing deobfuscator baselines. All samples come from a single obfuscator applied to moderate-length competitive-programming solutions. The 4,515 obfuscated malware samples have no test cases and are compared only through behavior traces.

  **Publication:** 2025 · ACM CCS 2025 · Conference paper · Guoqiang Chen et al.

  </details>

- [**Interaction2Code: Benchmarking MLLM-based Interactive Webpage Code Generation from Interactive Prototyping**](https://doi.org/10.1109/ASE63991.2025.00028)

  Benchmarks reconstruction of interactive webpages from screenshots before and after an interaction. The final study covers 127 webpages and 374 interactions, comparing rendered appearance, automated interaction checks, and human usability judgments.

  2025 · Conference paper · [PDF](https://arxiv.org/pdf/2411.03292v3) · [Code](https://github.com/WebPAI/Interaction2Code) · [Full entry & citation](https://awesomerea.org/papers/paper-interaction2code/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The inputs specify individual interaction transitions, not autonomous exploration of a complete site. Its tests do not establish long-workflow, server-side, or original-source equivalence; a detectable interaction is not necessarily usable.

  **Publication:** 2025 · ASE 2025 · Conference paper · Jingyu Xiao et al.

  </details>

- [**WebUIBench: A Comprehensive Benchmark for Evaluating Multimodal Large Language Models in WebUI-to-Code**](https://aclanthology.org/2025.findings-acl.815/)

  Diagnoses webpage-to-code capability through visual perception, HTML programming, image-to-HTML understanding, and screenshot reconstruction tasks. It separates underlying skills using question-answer pairs derived from real websites.

  2025 · Conference paper · [PDF](https://aclanthology.org/2025.findings-acl.815.pdf) · [Full entry & citation](https://awesomerea.org/papers/paper-webuibench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Primarily evaluates visual and HTML reconstruction skills. The paper includes a preliminary interaction study, not a full workflow or backend-equivalence benchmark. The official repository currently exposes README and images but not the evaluation scripts described in its instructions.

  **Publication:** 2025 · Findings of ACL 2025 · Conference paper · Zhiyu Lin et al.

  </details>

- [**Divide-and-Conquer: Generating UI Code from Screenshots**](https://doi.org/10.1145/3729364)

  Recursively divides a webpage screenshot along visual separation lines, has a multimodal model generate HTML/CSS for each leaf segment, and assembles child code upward into the full page; evaluated with GPT-4o, Gemini and Claude models and a small developer study.

  2025 · Journal article · [PDF](https://arxiv.org/pdf/2406.16386v3) · [Code](https://github.com/WebPAI/DCGen) · [Full entry & citation](https://awesomerea.org/papers/paper-dcgen/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** It reconstructs static visual layout as HTML/CSS, not interaction, JavaScript behavior or backend logic. Test pages are self-contained snapshots with images replaced by placeholders; the main evaluation samples 111 of 348 top-ranked sites, adds 80 harder GitHub Pages pages, and the usefulness study has four participants. Segmentation uses manually set thresholds, and assembly can still misarrange elements.

  **Publication:** 2025 · Proceedings of the ACM on Software Engineering · Journal article · Yuxuan Wan et al.

  </details>

- [**Design2Code: Benchmarking Multimodal Code Generation for Automated Front-End Engineering**](https://aclanthology.org/2025.naacl-long.199/)

  Evaluates reconstruction of frontend code from webpage screenshots using real-world reference pages, visual-element and layout metrics, and human assessment.

  2025 · Conference paper · [PDF](https://aclanthology.org/2025.naacl-long.199.pdf) · [Code](https://github.com/NoviScl/Design2Code) · [Full entry & citation](https://awesomerea.org/papers/paper-design2code/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** This is visual website reconstruction, not binary decompilation or recovery of backend behavior and interactive workflows. The main benchmark contains 484 webpages with placeholder images; code and data have separate licensing terms.

  **Publication:** 2025 · NAACL 2025 · Conference paper · Chenglei Si et al.

  </details>

- [**Web2Code: A Large-scale Webpage-to-Code Dataset and Evaluation Framework for Multimodal LLMs**](https://proceedings.nips.cc/paper_files/paper/2024/hash/cb66be286795d71f89367d596bf78ea7-Abstract-Datasets_and_Benchmarks_Track.html)

  Studies screenshot-to-HTML reconstruction through instruction tuning and two evaluation benchmarks. Web2Code combines generated webpages, refined WebSight and pix2code image/code pairs, and WebSRC-derived question answering. Models produce HTML from a webpage image and instruction; rendered output is compared visually, while a separate benchmark measures screenshot understanding.

  2024 · Conference paper · [PDF](https://proceedings.neurips.cc/paper_files/paper/2024/file/cb66be286795d71f89367d596bf78ea7-Paper-Datasets_and_Benchmarks_Track.pdf) · [Code](https://github.com/MBZUAI-LLM/web2code) · [Full entry & citation](https://awesomerea.org/papers/paper-web2code/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Evaluation uses 1,198 screenshots and 5,990 yes/no questions. WCGB grades rendered images with GPT-4V; its User Interface and Interactivity category measures element appearance, not executed click paths, persistent state or backend behavior. Synthetic and refined examples do not establish coverage of arbitrary real web applications, original-source equivalence or code quality. The paper reports contact-information issues in 2.7% of a 1,000-item privacy sample, so a blanket claim that the data is free of such information is unsupported.

  **Publication:** 2024 · NeurIPS 2024 Datasets and Benchmarks · Conference paper · Sukmin Yun et al.

  </details>

<a id="papers-game-reconstruction"></a>
### Game reconstruction and reverse engineering

[↑ Paper topics](#papers) · [Contents](#contents)

- [**GameReplica: A Benchmark for Black-Box Visual Game Replication by Vision-Language Agents**](https://arxiv.org/abs/2609.22308)

  Evaluates whether vision-language agents can infer hidden game rules through screenshots and active interaction, then build runnable single-file HTML replicas across 125 tasks from 25 web games, each with five difficulty levels.

  2026 · Preprint · [PDF](https://arxiv.org/pdf/2609.22308v1) · [Full entry & citation](https://awesomerea.org/papers/paper-gamereplica/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The tasks cover rule-driven web puzzles and board games, not native or commercial game reconstruction. Rule, implementation, and visual scores use LLM judges and do not prove behavioral equivalence. The official site provides demos; a benchmark-code repository was not verified.

  **Publication:** 2026 · arXiv · Preprint · Boyu Qiao et al.

  </details>

- [**Tycho: Active Abstraction with Programmatic World Models for ARC-AGI-3**](https://arxiv.org/abs/2607.28287)

  Tycho constructs editable Python models of game state, transitions, rendering and outcomes from action/observation histories in unfamiliar ARC-AGI-3 games. It checks model predictions against recorded transitions and can use, repair or bypass these models during planning.

  2026 · Preprint · [PDF](https://arxiv.org/pdf/2607.28287v1) · [Code](https://github.com/NIMI-research/Tycho) · [Full entry & citation](https://awesomerea.org/papers/paper-tycho/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Evaluation uses one stochastic run per configuration on 25 public games and 183 levels; five games informed harness development. Models may abstain on cells or accept bounded rendering variants. Transition replay and game scores do not establish complete engine reconstruction, correct objectives, unseen-state fidelity, unseen-game generalization or run-to-run reliability; the agent can bypass modeling.

  **Publication:** 2026 · arXiv · Preprint · Jens Lehmann et al.

  </details>

- [**RevengeBench: Reverse Engineering Code-Space Policies from Behavioral Experiments**](https://arxiv.org/abs/2606.26094)

  Tests whether agents can recover executable decision policies from behavioral traces and self-designed opponent probes, using 75 synthetic policies across five game arenas and measuring held-out action agreement and downstream competitive value.

  2026 · Preprint · [PDF](https://arxiv.org/pdf/2606.26094v1) · [Code](https://github.com/bethgelab/revenge-bench) · [Full entry & citation](https://awesomerea.org/papers/paper-revengebench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The targets are fixed synthetic policies, not full games or adaptive adversaries. Agreement on finitely evaluated states does not uniquely identify source code, and some arenas have substantial variance. The public package omits some paper-only plotting and ablation suites; reproduction also needs CodeClash, a container runtime, and model access.

  **Publication:** 2026 · arXiv · Preprint · Babak Rahmani et al.

  </details>

- [**SPRITE: From Static Mockups to Engine-Ready Game UI**](https://doi.org/10.1145/3772363.3798742)

  Transforms game-interface screenshots into editable engine assets through hierarchical YAML, visual grounding, asset extraction, and Unity UXML/USS synthesis, with evaluation on a curated game-UI benchmark and review by three senior UI/UX designers.

  2026 · Conference paper · [PDF](https://baiyunshu.github.io/sprite.github.io/Source/chiea26-516.pdf) · [Full entry & citation](https://awesomerea.org/papers/paper-sprite-game-ui/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The generated interactions cover basic hover, toggle, and click behavior. Complex temporal and drag-and-drop logic remain outside scope, and translucent overlap or ambiguous diegetic layouts can fail. This is game-UI prototyping, not complete gameplay reconstruction; the official page still labels code as coming soon.

  **Publication:** 2026 · CHI EA 2026 (poster/extended abstract) · Conference paper · Yunshu Bai et al.

  </details>

- [**WorldCoder, a Model-Based LLM Agent: Building World Models by Writing Code and Interacting with the Environment**](https://papers.nips.cc/paper_files/paper/2024/hash/820c61a0cd419163ccbd2c33b268816e-Abstract-Conference.html)

  WorldCoder learns executable Python transition and reward models from environment interactions and natural-language goals. It refines code against recorded experiences and an optimistic planning constraint, studying transfer and task solving in Sokoban, MiniGrid and ALFWorld.

  2024 · Conference paper · [PDF](https://papers.neurips.cc/paper_files/paper/2024/file/820c61a0cd419163ccbd2c33b268816e-Paper-Conference.pdf) · [Code](https://github.com/haotang1995/WorldCoder) · [Full entry & citation](https://awesomerea.org/papers/paper-worldcoder/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Assumes deterministic dynamics and symbolic, discrete states rather than recovering a game from arbitrary pixels or binaries. Consistency with observed transitions and successful planning do not establish complete engine equivalence or correctness on every unseen state. Evaluation concerns bounded environment models and planning, not original source or asset recovery.

  **Publication:** 2024 · NeurIPS 2024 · Conference paper · Hao Tang et al.

  </details>

- [**Generating Code World Models with Large Language Models Guided by Monte Carlo Tree Search**](https://proceedings.neurips.cc/paper_files/paper/2024/hash/6f479ea488e0908ac8b1b37b27fd134c-Abstract-Conference.html)

  GIF-MCTS generates executable Python transition and reward models from natural-language environment descriptions and offline state-transition trajectories, using prediction feedback to generate, improve and repair code. CWMB evaluates 18 reinforcement-learning environments and downstream planning; a separate experiment uses a simplified Read to Fight Monsters grid world.

  2024 · Conference paper · [PDF](https://proceedings.neurips.cc/paper_files/paper/2024/file/6f479ea488e0908ac8b1b37b27fd134c-Paper-Conference.pdf) · [Code](https://github.com/nicoladainese96/code-world-models) · [Full entry & citation](https://awesomerea.org/papers/paper-code-world-models/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Assumes deterministic, fully observable dynamics and sufficiently detailed descriptions; this is not recovery from pixels or binaries alone. Accuracy uses the replay transitions supplied during synthesis, alongside planning-return evaluation, rather than proving correctness on all unseen states or full-engine equivalence. RTFM fixes the manual across episodes and keeps monsters stationary. CWMB also includes non-game control and physics tasks; some planning returns are unavailable and complex continuous-state models remain difficult.

  **Publication:** 2024 · NeurIPS 2024 · Conference paper · Nicola Dainese et al.

  </details>

<a id="papers-app-reconstruction"></a>
### App reconstruction and analysis

[↑ Paper topics](#papers) · [Contents](#contents)

- [**UIOrchestra: Generating High-Fidelity Code from UI Designs with a Multi-agent System**](https://aclanthology.org/2025.findings-emnlp.150/)

  UIOrchestra converts static mobile UI designs into React/CSS through layout-description, code-generation and rendered-image comparison agents. Its APPUI benchmark contains 1,101 human-refined code/rendering pairs based on screenshots from 165 apps across 12 categories. The reference code is reconstructed for evaluation, rather than recovered original application source.

  2025 · Conference paper · [PDF](https://aclanthology.org/2025.findings-emnlp.150.pdf) · [Full entry & citation](https://awesomerea.org/papers/paper-uiorchestra/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Tests visual, component and code similarity, not native-package execution, interaction, backend behavior or application equivalence. APPUI references are rendered reconstructions of iOS screenshots; unavailable images/icons use placeholders. A human study covers 200 samples with four annotators. The difference-analysis prompt ignores font-size/typeface differences and placeholder image content. Model snapshots, rendering dependencies and a reproducible runtime setup were not verified; experiments were not rerun.

  **Publication:** 2025 · Findings of EMNLP 2025 · Conference paper · Chuhuai Yue et al.

  </details>

- [**DeclarUI: Bridging Design and Development with Automated Declarative UI Code Generation**](https://doi.org/10.1145/3715726)

  Combines visual component extraction, multimodal models, page-transition graphs and iterative checks to reconstruct multi-page mobile UI code from designs or screenshots, evaluated with React Native, Flutter and ArkUI.

  2025 · Journal article · [PDF](https://xinyi-hou.github.io/files/zhou2024bridging.pdf) · [Code](https://github.com/security-pride/DeclarUI) · [Full entry & citation](https://awesomerea.org/papers/paper-declarui/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** People review and correct the inferred navigation graph. Evaluation covers 50 five-page UI sets; transition coverage and compilation do not establish full business-logic or backend recovery. Framework results vary, and visual metrics imperfectly reflect perceived fidelity. Public scripts and data are available, but no project-level license was found at the reviewed commit.

  **Publication:** 2025 · Proceedings of the ACM on Software Engineering · Journal article · Ting Zhou et al.

  </details>

- [**Machine Learning-Based Prototyping of Graphical User Interfaces for Mobile Apps**](https://doi.org/10.1109/TSE.2018.2844788)

  ReDraw turns screenshots or design mock-ups into native Android GUI prototypes by detecting components, classifying widget types with a CNN, and assembling a plausible view hierarchy with a data-driven nearest-neighbor method.

  2020 · Journal article · [PDF](https://arxiv.org/pdf/1802.02312v2) · [Full entry & citation](https://awesomerea.org/papers/paper-redraw/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The implementation covers 15 Android component classes and one screen at a time; multiple screens require manual combination, and hierarchy construction is tied to the mined screen size. Evaluation concerns appearance and view hierarchy, not recovery of original app logic or backends. Screenshots and reconstructed mock-ups served as proxies for real design artifacts; results were not independently reproduced here.

  **Publication:** 2020 · IEEE Transactions on Software Engineering · Journal article · Kevin Moran et al.

  </details>

- [**pix2code: Generating Code from a Graphical User Interface Screenshot**](https://doi.org/10.1145/3220134.3220135)

  Learns screenshot-to-DSL generation for native Android XML, iOS Storyboards and web HTML/CSS interfaces, then compiles the DSL into platform UI code.

  2018 · Conference paper · [PDF](https://arxiv.org/pdf/1705.07962v2) · [Code](https://github.com/tonybeltramelli/pix2code) · [Full entry & citation](https://awesomerea.org/papers/paper-pix2code/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Evaluation uses synthetic screenshot/code pairs: 1,500 training and 250 test instances per platform. Reported accuracy concerns DSL tokens, not complete apps or behavior. Text labels are ignored; platform datasets train separate models using the same architecture. The task covers layout, components and relationships, not application logic or backend recovery. The repository describes an educational research prototype; its older dependencies were not runtime-tested.

  **Publication:** 2018 · EICS 2018 · Conference paper · Tony Beltramelli

  </details>

- [**From UI Design Image to GUI Skeleton: A Neural Machine Translator to Bootstrap Mobile GUI Implementation**](https://doi.org/10.1145/3180155.3180240)

  UI2code translates a mobile UI image into an Android component hierarchy and layout skeleton using a neural encoder-decoder. The paper evaluates structural prediction and a small developer study of implementing layouts from generated skeletons.

  2018 · Conference paper · [PDF](https://chunyang-chen.github.io/publication/ui2code.pdf) · [Code](https://github.com/ccywch/UI2code) · [Full entry & citation](https://awesomerea.org/papers/paper-ui2code/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The output covers component types and hierarchy from a single image; detailed styling and text require developer work. Structural token accuracy and an eight-participant study on five screenshots do not establish complete visual fidelity, navigation, app logic or backend recovery. The main split is screenshot-based; a separate evaluation on 1,208 images from 20 unseen apps provides limited generalization evidence.

  **Publication:** 2018 · ICSE 2018 · Conference paper · Chunyang Chen et al.

  </details>

- [**Reverse Engineering Mobile Application User Interfaces with REMAUI (T)**](https://ieeexplore.ieee.org/abstract/document/7372013)

  Reconstructs native Android UI code from screenshots or design bitmaps using OCR, computer vision, and layout heuristics; evaluates visual similarity and view hierarchies on 488 screenshots from over 100 Android and iOS applications.

  2015 · Conference paper · [PDF](https://c.csallner.org/papers/nguyen15reverse.pdf) · [Code](https://github.com/soumikmohianuta/pixtoapp) · [Full entry & citation](https://awesomerea.org/papers/paper-remaui/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The output is Android UI code; iOS screenshots are inputs, not evidence of native iOS output. Original logic and backend behavior are not recovered, and multi-screen transitions were future work. OCR/layout heuristics can misidentify content. The linked REMAUI v2 repository has older dependencies and is not the exact verified 2015 artifact.

  **Publication:** 2015 · ASE 2015 · Conference paper · Tuan Anh Nguyen et al.

  </details>

<a id="papers-firmware-analysis"></a>
### Firmware analysis and rehosting

[↑ Paper topics](#papers) · [Contents](#contents)

- [**User-Space Dependency-Aware Rehosting for Linux-Based Firmware Binaries**](https://www.ndss-symposium.org/ndss-paper/user-space-dependency-aware-rehosting-for-linux-based-firmware-binaries/)

  FIRMWELL reconstructs the execution environment of Linux firmware services by running their initialization processes, locating blocking dependencies and repairing missing system-level behavior. It combines containerized QEMU-user emulation with a QEMU-system fallback, using process traces and binary analysis to recover resources needed by the target service.

  2026 · Conference paper · [PDF](https://www.ndss-symposium.org/wp-content/uploads/2026-s249-paper.pdf) · [Code](https://github.com/qc9c/Firmwell) · [Full entry & citation](https://awesomerea.org/papers/paper-firmwell/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The evaluation concerns selected network services, not complete device or hardware equivalence. HTTP acceptance uses configured response-status and error-content checks; other services need their own criteria. Coverage depends on unpacking, supported architectures, initialization heuristics and peripheral models. Symbolic path explosion, solver timeouts and complex peripheral checks remain failure modes. The paper’s recovery strategy avoids patching target binaries; successful service interaction does not establish recovery of original source code or every device function.

  **Publication:** 2026 · NDSS 2026 · Conference paper · Chuan Qin et al.

  </details>

- [**Target-Centric Firmware Rehosting with Penguin**](https://www.ndss-symposium.org/ndss-paper/auto-draft-634/)

  Penguin rehosts embedded Linux firmware from an extracted filesystem by deriving an editable configuration of emulation transformations, such as file changes, pseudofiles, NVRAM values and network interfaces, from static analysis. Dynamic-analysis plugins expose failures so the configuration can be refined for each target, and a minimizer identifies which transformations a working rehosting needs.

  2025 · Conference paper · [PDF](https://www.ndss-symposium.org/wp-content/uploads/bar2025-final10.pdf) · [Code](https://github.com/rehosting/penguin) · [Full entry & citation](https://awesomerea.org/papers/paper-penguin/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Targets embedded Linux firmware through whole-system emulation with kernel replacement, as in Firmadyne and FirmAE; the implementation covers x86, ARM and MIPS and relies on the Linux syscall ABI. In the FirmAE comparison, success means a process binds port 80 or 443; a non-empty HTTP response is a stricter check, and the authors note neither shows full functionality. The 75% gain over FirmAE is author-reported on their own corpus of 13,649 images from vendor websites. Refinement still needs an analyst, and nondeterministic runs were repeated up to ten times. It builds an analysis environment, not a faithful device reproduction or source recovery.

  **Publication:** 2025 · Workshop on Binary Analysis Research (BAR) 2025 · Conference paper · Andrew Fasano et al.

  </details>

- [**Fuzzware: Using Precise MMIO Modeling for Effective Firmware Fuzzing**](https://www.usenix.org/conference/usenixsecurity22/presentation/scharnowski)

  Rehosts monolithic ARM Cortex-M firmware for fuzzing, using locally scoped symbolic execution to model memory-mapped I/O accesses and focus input mutations on values relevant to firmware logic.

  2022 · Conference paper · [PDF](https://www.usenix.org/system/files/sec22-scharnowski.pdf) · [Code](https://github.com/fuzzware-fuzzer/fuzzware) · [Full entry & citation](https://awesomerea.org/papers/paper-fuzzware/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The Cortex-M3/M4 artifact requires memory-map configuration and does not automatically model DMA. Abstracting hardware can produce crashes that are impossible on the physical device. This is an analysis environment, not original-source recovery or faithful full-device reconstruction.

  **Publication:** 2022 · USENIX Security 2022 · Conference paper · Tobias Scharnowski et al.

  </details>

- [**FirmAE: Towards Large-Scale Emulation of IoT Firmware for Dynamic Analysis**](https://doi.org/10.1145/3427228.3427294)

  Extends Firmadyne with empirically derived interventions for boot, networking, NVRAM, kernel behavior, and other runtime failures, enabling Linux router and IP-camera firmware web services to run for dynamic analysis.

  2020 · Conference paper · [PDF](https://syssec.kaist.ac.kr/pub/2020/kim_acsac2020.pdf) · [Code](https://github.com/pr0v3rbs/FirmAE) · [Full entry & citation](https://awesomerea.org/papers/paper-firmae/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Arbitration deliberately changes execution and targets functioning web interfaces, not identical physical-device behavior. The evaluation covers ARM little-endian and MIPS little-/big-endian firmware from routers and IP cameras; heuristics may fail on unseen devices or configurations. It reuses firmware binaries rather than recovering their source.

  **Publication:** 2020 · ACSAC 2020 · Conference paper · Mingeun Kim et al.

  </details>

- [**HALucinator: Firmware Re-hosting Through Abstraction Layer Emulation**](https://www.usenix.org/conference/usenixsecurity20/presentation/clements)

  HALucinator rehosts monolithic ARM Cortex-M firmware by identifying hardware-abstraction-library functions and replacing them with authored Python handlers and peripheral models. LibMatch locates library interfaces; the QEMU/Avatar2 implementation supports interactive I/O, while the paper-associated HAL-fuzz variant uses AFL-Unicorn for fuzzing.

  2020 · Conference paper · [PDF](https://www.usenix.org/system/files/sec20-clements.pdf) · [Code](https://github.com/embedded-sec/halucinator) · [Full entry & citation](https://awesomerea.org/papers/paper-halucinator/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** LibMatch requires an available HAL/library and a sufficiently similar compilation environment; compiler variation and inlining limit matching. Rehosting also needs a QEMU-supported architecture, firmware memory layout, interception addresses and authored handlers/models. Unmodeled direct hardware accesses may return zero or ignore writes, and simplified timing and peripheral behavior do not establish hardware equivalence. The authors’ rehosting and fuzzing demonstrations are not universal firmware coverage, complete device reconstruction or original-source recovery.

  **Publication:** 2020 · USENIX Security 2020 · Conference paper · Abraham A Clements et al.

  </details>

<a id="papers-protocol-analysis"></a>
### Protocol inference and analysis

[↑ Paper topics](#papers) · [Contents](#contents)

- [**ICEPRE: ICS Protocol Reverse Engineering via Data-Driven Concolic Execution**](https://dl.acm.org/doi/10.1145/3728982)

  Infers message-field boundaries by following concrete message-guided paths through binary protocol parsers, then symbolically replaying them to extract byte-level data flow. It merges bytes using value-preserving operations and similar processing traces. For the 1,000-message datasets of four public ICS protocols, the authors report average boundary F1 of 0.76 and field perfection of 0.67.

  2025 · Journal article · [PDF](https://dl.acm.org/doi/pdf/10.1145/3728982) · [Code](https://github.com/QYbPtqyb/ICEPRE) · [Full entry & citation](https://awesomerea.org/papers/paper-icepre/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Recovers message syntax, not field semantics, protocol state machines or endpoint equivalence. It needs the binary, loader configuration and correctly identified initialization, input and parsing functions; manual filtering remains necessary, especially without symbols. Encrypted protocols and bit-level fields are unsupported, and ignored or only copied bytes can be merged incorrectly. Perfection measures fields with both boundaries correct. Quantitative tests use four public protocols with 50- and 1,000-message sets; separate proprietary studies cover three protocols in five firmware targets, with interaction checks on three devices and manually established ground truth. Those checks do not demonstrate complete device behavior.

  **Publication:** 2025 · Proceedings of the ACM on Software Engineering (ISSTA 2025) · Journal article · Yibo Qu et al.

  </details>

- [**BinPRE: Enhancing Field Inference in Binary Analysis Based Protocol Reverse Engineering**](https://dl.acm.org/doi/10.1145/3658644.3690299)

  Infers protocol-message field boundaries and semantics from instrumented server binaries and input messages. BinPRE groups bytes by the instruction operators that process them, applies detectors for field types and functions, then refines results across similar messages. On eight protocols with 50 messages each, the authors report average field perfection of 0.73 and type/function F1 scores of 0.74/0.81.

  2024 · Conference paper · [PDF](https://tingsu.github.io/files/ccs24-BinPRE.pdf) · [Code](https://github.com/ecnusse/BinPRE) · [Full entry & citation](https://awesomerea.org/papers/paper-binpre/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** This is field inference, not recovery of a protocol state machine or complete endpoint behavior. It requires an accessible, instrumentable implementation and runtime message processing; passive captures alone are insufficient. Perfection counts exactly segmented fields against all true fields, not fully recovered protocols. The detector library covers five semantic types and six functions. Byte-level taint cannot accurately resolve bit flags, and unexercised behavior is not established. Ground truth uses Wireshark dissectors and specifications; three binary-analysis baselines were author reimplementations. Reported fuzzing improvements are a downstream evaluation, not proof of implementation equivalence.

  **Publication:** 2024 · ACM CCS 2024 · Conference paper · Jiayi Jiang et al.

  </details>

- [**Lifting Network Protocol Implementation to Precise Format Specification with Security Applications**](https://dl.acm.org/doi/10.1145/3576915.3616614)

  NetLifter statically lifts source-available C protocol parsers into BNF-style message grammars and first-order constraints between packet fields. It analyzes annotated LLVM bitcode using abstract format graphs, localized path-sensitive analysis, unfolding and reordering. The resulting field boundaries, constraints and names can support packet generation and parser construction.

  2023 · Conference paper · [PDF](https://qingkaishi.github.io/public_pdfs/CCS23.pdf) · [Code](https://github.com/qingkaishi/netlifter) · [Full entry & citation](https://awesomerea.org/papers/paper-netlifter/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Requires source/LLVM IR and packet-buffer/length annotations; it is not closed-binary or traffic-only recovery. The paper targets common top-down C parsers and does not support C++, inline assembly or libraries without available code. Pointer/loop analysis remains approximate; checksum fields can be identified while some checksum constraints are omitted, and fields ignored by an implementation may be missed. Precision/recall was manually checked on ten selected protocols. The reported fuzzing evaluation used three-hour runs repeated twenty times and bypassed checksum checks. It infers formats, not protocol state machines or proof of implementation equivalence.

  **Publication:** 2023 · ACM CCS 2023 · Conference paper · Qingkai Shi et al.

  </details>

- [**BinaryInferno: A Semantic-Driven Approach to Field Inference for Binary Message Formats**](https://www.ndss-symposium.org/ndss-paper/binaryinferno-a-semantic-driven-approach-to-field-inference-for-binary-message-formats/)

  Infers partial binary-message formats from static message samples without instrumenting an executable. Specialized detectors recognize floats, timestamps, lengths, entropy boundaries and serialization patterns; a graph-based integration step reconciles their descriptions. Across samples from ten protocols, the authors report top-level field-boundary precision of 0.69, recall of 0.73 and false-positive rate of 0.04 for the 1,000-message setting without analyst priors.

  2023 · Conference paper · [PDF](https://www.ndss-symposium.org/wp-content/uploads/2023/02/ndss2023_s131_paper.pdf) · [Code](https://github.com/binaryinferno/binaryinferno) · [Full entry & citation](https://awesomerea.org/papers/paper-binaryinferno/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Assumes error-free, uncompressed, unencrypted, byte-aligned data and infers common fields or payload regions beginning at consistent offsets. It leaves optional/union fields and unsupported serialization patterns unresolved; sample diversity matters. The 26 encapsulated-payload test sets were pre-grouped using ground-truth message types, not discovered automatically. Ground truth merges adjacent fields that are constant across the sample; empty inference results are excluded from reported averages where stated. BI+ additionally uses supplied endianness and capture-time ranges. These are field-boundary results, not complete semantic recovery, protocol-state inference or behavioral equivalence.

  **Publication:** 2023 · NDSS 2023 · Conference paper · Jared Chandler et al.

  </details>

- [**The Closer You Look, The More You Learn: A Grey-box Approach to Protocol State Machine Learning**](https://doi.org/10.1145/3548606.3559365)

  StateInspector learns protocol Mealy machines by combining active message queries with snapshots of runtime memory, without requiring the target’s source code. It identifies candidate state-defining heap locations and uses taint and concolic analysis to merge states, evaluated by the authors on TLS 1.2 and WPA/2 implementations.

  2022 · Conference paper · [PDF](https://tomchothia.gitlab.io/Papers/greyboxstatelearning_ccs2022.pdf) · [Code](https://github.com/ChrisMcMStone/state-inspector) · [Full entry & citation](https://awesomerea.org/papers/paper-stateinspector/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Assumes a finite Mealy-machine abstraction, a known input alphabet that can reach the relevant states, and state-defining memory on the heap exercised by bootstrap queries. State merging depends on configured search-depth and symbolic look-ahead bounds. Missing inputs or state stored elsewhere can leave behavior unmodeled; malformed harness messages, response abstraction and timeouts can create misleading transitions. Learned models and bounded checks do not establish full implementation equivalence, recover unknown message formats or reconstruct an application’s source code.

  **Publication:** 2022 · ACM CCS 2022 · Conference paper · Chris McMahon Stone et al.

  </details>

- [**Fingerprinting and analysis of Bluetooth devices with automata learning**](https://doi.org/10.1007/s10703-023-00425-y)

  Learns Mealy-machine models of Bluetooth Low Energy implementations on physical peripherals by active automata learning. An nRF52840 central running SweynTooth-derived firmware sends abstract BLE inputs, with error handling, repeated queries and caching for lost packets and non-deterministic replies. The authors learn connection-procedure models of six devices and legacy-pairing models of three, and use model differences to fingerprint their SoCs.

  2022 · Journal article · [PDF](https://arxiv.org/pdf/2211.16074v2) · [Code](https://github.com/apferscher/ble-learning) · [Full entry & citation](https://awesomerea.org/papers/paper-ble-automata-learning/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Models are bounded by the chosen abstract alphabet and cover only connection and legacy pairing; message formats are not inferred, and secure pairing is left to future work. Equivalence was approximated with a small number of conformance tests per state, so models are hypotheses, not proofs. One SoC was learnable only with reduced alphabets, two were learned from an already-connected state, and some pairing runs needed manual hard resets. The fingerprinting sequence holds only for the tested SoCs. Apart from one crashing input sequence, the authors report no security vulnerabilities in the learned models.

  **Publication:** 2022 · Formal Methods in System Design · Journal article · Andrea Pferscher et al.

  </details>

- [**NetPlier: Probabilistic Network Protocol Reverse Engineering from Message Traces**](https://www.ndss-symposium.org/ndss-paper/netplier-probabilistic-network-protocol-reverse-engineering-from-message-traces/)

  Uses multiple sequence alignment and probabilistic keyword-field inference to cluster network messages by type, evaluated across ten protocols with downstream format and state-machine analysis.

  2021 · Conference paper · [PDF](https://www.ndss-symposium.org/wp-content/uploads/ndss2021_4A-5_24531_paper.pdf) · [Code](https://github.com/yapengye/NetPlier) · [Full entry & citation](https://awesomerea.org/papers/paper-netplier/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Requires unencrypted traces and cannot recover unseen message types. Larger alignments, sub-byte keywords and one-way traffic can reduce accuracy. Format/FSM inference is downstream evaluation rather than the main contribution; state semantics in a case study were manually annotated. These models do not establish complete application/device reconstruction.

  **Publication:** 2021 · NDSS 2021 · Conference paper · Yapeng Ye et al.

  </details>

- [**Automatic Wireless Protocol Reverse Engineering**](https://www.usenix.org/conference/woot19/presentation/pohl)

  Infers message formats of proprietary wireless protocols from demodulated physical-layer captures: it aligns messages by preamble and sync word, then uses RSSI and dedicated engines to label length, address, sequence-number and checksum fields, optionally using known addresses or field positions.

  2019 · Conference paper · [PDF](https://www.usenix.org/system/files/woot19-paper_pohl.pdf) · [Code](https://github.com/jopohl/urh) · [Full entry & citation](https://awesomerea.org/papers/paper-wireless-protocol-re/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Only message formats are inferred: preamble, sync, length, address, sequence number and checksum. State-machine inference and payload fields, such as an on/off bit, are out of scope. The method assumes length-efficient binary messages with one preamble and sync word each. Accuracy is measured on 8 generated protocols; 3 real smart-home captures (EnOcean, Homematic BidCoS and an eQ-3 protocol used by RWE Smarthome) serve for performance tests, which the authors call a limited test set.

  **Publication:** 2019 · 13th USENIX Workshop on Offensive Technologies (WOOT 19) · Conference paper · Johannes Pohl et al.

  </details>

- [**NEMESYS: Network Message Syntax Reverse Engineering by Analysis of the Intrinsic Structure of Individual Messages**](https://www.usenix.org/conference/woot18/presentation/kleber)

  Infers approximate field boundaries within individual binary-protocol messages from changes in bit congruence, and introduces Format Match Score to compare inferred segmentation with known protocol dissectors.

  2018 · Conference paper · [PDF](https://www.usenix.org/system/files/conference/woot18/woot18-paper-kleber.pdf) · [Code](https://github.com/vs-uulm/nemesys) · [Full entry & citation](https://awesomerea.org/papers/paper-nemesys/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Requires plaintext payloads. Evaluation covers DNS, DHCP and NTP with protocol-tuned parameters. Single-byte fields are not inferred; zero-filled fields, character sequences and pseudo-random values can cause errors. FMS needs known field boundaries for validation. The output is approximate segmentation, not field semantics, a state machine or complete application/device behavior.

  **Publication:** 2018 · 12th USENIX Workshop on Offensive Technologies (WOOT 18) · Conference paper · Stephan Kleber et al.

  </details>
<!-- END GENERATED PAPERS -->

<a id="search-the-catalog"></a>
## Full Repository Index

<!-- BEGIN REPOSITORY INDEX SUMMARY -->
**3,000** repository READMEs scanned; **2,836** entries available to browse. The 161 clearly out-of-scope entries and 3 whose upstream repository is no longer available remain in the scan data. This automatically discovered index is separate from the curated resources above and has not been individually execution-tested.

[Browse by category on GitHub](docs/repositories/README.md) · [Search website](https://awesomerea.org/?view=source-index&lang=en) · [Full bilingual index JSON](https://awesomerea.org/source-index.json) · [Curated catalog JSON](https://awesomerea.org/catalog.json)
<!-- END REPOSITORY INDEX SUMMARY -->

The resource list above is curated from primary sources. Detailed requirements, original evidence, and review dates are available in the [catalog data](data/README.md).

## Contributing

Help improve an entry or share a useful source. Start with the [contribution guide](CONTRIBUTING.md), then [suggest a resource](https://github.com/reacher-z/Awesome-REA/issues/new?template=resource.yml), [recommend a paper](https://github.com/reacher-z/Awesome-REA/issues/new?template=paper.yml), [correct a translation](https://github.com/reacher-z/Awesome-REA/issues/new?template=translation.yml) or [report an outdated entry](https://github.com/reacher-z/Awesome-REA/issues/new?template=broken-resource.yml).

## Contributors

[Yuxuan Zhang](https://yuxuan.world/) — **Lead**.

[Haozhe Wang](https://haozheh3.github.io/) — Game reconstruction resource collection: [awesome-rea-games](https://github.com/HaozheH3/awesome-rea-games).

## About

[REA (Reverse Engineer Anything)](https://github.com/morluto/rea) is a separate upstream CLI and MCP project. This collection's name echoes it, but it is not the REA repository; “REA” in entry tags and labels such as “Official REA documentation” refers to that project.

This is an independent community collection. Original descriptions and code are [MIT licensed](LICENSE); linked projects retain their own licenses.

To cite the collection itself, use its [citation metadata](CITATION.cff). Cite listed papers, tools and other works from their own primary sources, and give the commit or snapshot date with any scan-derived counts.

For AI-built software and agent training or evaluation resources, explore [AI Can What?](https://aicanwhat.com/) across games, websites and applications.

---

[Catalog format](data/README.md) · [Scan methodology](docs/source-scan.md) · [Build status](https://github.com/reacher-z/Awesome-REA/actions/workflows/validate.yml) · [Back to top](#awesome-reverse-engineering-anything)
