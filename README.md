# Awesome Reverse Engineering Anything

An independent collection of tools, reconstruction cases and research for websites, games, apps, native binaries, firmware and communication protocols.

<a href="https://awesomerea.org/"><img src="assets/readme-banner.svg" alt="Awesome Reverse Engineering Anything — tools, cases and papers across six reverse-engineering domains" width="960"></a>

**[Search & filter](https://awesomerea.org/)** · [Curated resources](https://awesomerea.org/resources/) · [Research papers](https://awesomerea.org/papers/) · [简体中文](README.zh-CN.md)

Choose a target below. Entries link to primary sources; **source review does not imply runtime verification**. [Review method](https://awesomerea.org/about/).

## Contents

<!-- BEGIN GENERATED CONTENTS -->
**Tools and cases by target**

- [Website](#website) (14) · [Game](#game) (42) · [App](#app) (34)
- [Native Binary](#native-binary) (20) · [Firmware and Hardware](#firmware) (13) · [Protocol](#protocol) (11)

**Research and more**

- [Papers](#papers) (46) · [All cases](https://awesomerea.org/cases/) (47) · [Full Repository Index](#full-repository-index) (2,839)
- [Agents and MCP](#agents-and-mcp) (18) · [Related Collections](#related-collections) (4) · [References and Learning](#references-and-learning) (17)
<!-- END GENERATED CONTENTS -->

<a id="resource-catalog"></a>
## Resources

Names link to original sources. “Requirements & evidence” opens prerequisites, limitations and review sources. Each resource appears once under its main purpose; [papers are listed separately](#papers).

Includes independent projects and [REA](https://github.com/morluto/rea) resources. Listing does not imply REA integration, and the cases view reuses these entries.

<!-- BEGIN GENERATED CATALOG -->
<a id="website"></a>
### Website

[↑ Contents](#contents)

#### Case studies

- [**Dinosaur runner: recovering one acceleration rule**](https://github.com/morluto/rea/blob/c360cfcd6d7901514b16dd6113eba2e0b0fdf422/website/evidence/calculator-and-dino.md#dinosaur-speed) · Case study · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-dinosaur-speed-case/)

  REA’s documented teaching case inspects the HTTP t-rex-runner edition and reconstructs its speed-update rule. A separate controlled original-game check and a new demonstration compare update counts, including the floating-point step that crosses the nominal speed threshold.

#### Tools, projects and integrations

- [**webcrack**](https://github.com/j4k0xb/webcrack) · Tool · [Requirements & evidence](https://awesomerea.org/resources/webcrack/)

  Improves JavaScript readability by reversing supported obfuscation patterns and unpacking webpack/Browserify bundles.

- [**humanify**](https://github.com/jehna/humanify) · Tool · [Requirements & evidence](https://awesomerea.org/resources/humanify/)

  Rename identifiers in minified JavaScript with LLM-suggested names, applied through scope-aware AST rewriting so the program structure stays unchanged. The new names are model suggestions, not recovered original identifiers.

- [**WABT**](https://github.com/WebAssembly/wabt) · Tool · WebAssembly · [Requirements & evidence](https://awesomerea.org/resources/wabt/)

  WebAssembly tools for binary-to-text conversion, section inspection, validation, interpretation and C translation.

- [**wasm-tools**](https://github.com/bytecodealliance/wasm-tools) · Tool · WebAssembly · [Requirements & evidence](https://awesomerea.org/resources/wasm-tools/)

  Bytecode Alliance CLI and Rust libraries for inspecting WebAssembly modules, metadata, components and WIT interfaces.

- [**Chrome DevTools MCP**](https://github.com/ChromeDevTools/chrome-devtools-mcp) · Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/chrome-devtools-mcp/)

  Connect an agent to Chrome for live page inspection, network debugging, and performance traces.

- [**mitmproxy**](https://github.com/mitmproxy/mitmproxy) · Tool · [Requirements & evidence](https://awesomerea.org/resources/mitmproxy/)

  Inspect and record HTTP traffic with an interactive proxy, web interface, or scriptable command-line tools.

- [**Playwright MCP**](https://github.com/microsoft/playwright-mcp) · Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/playwright-mcp/)

  Drive browser interactions through structured accessibility snapshots to investigate reproducible web behavior.

- [**Burp Suite MCP Server**](https://github.com/PortSwigger/mcp-server) · Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/burp-suite-mcp-server/)

  PortSwigger's Burp Suite extension serves an MCP endpoint, plus a packaged stdio proxy, so agents can query proxy HTTP and WebSocket history, send HTTP/1.1 or HTTP/2 requests, and open Repeater or Intruder tabs.

- [**Wakaru**](https://github.com/pionxzh/wakaru) · Tool · [Requirements & evidence](https://awesomerea.org/resources/wakaru/)

  Recover readable modules from shipped JavaScript bundles by reversing recognized minifier and transpiler patterns. Supports bundle splitting and modern-syntax recovery for inspecting production frontend code.

- [**Spectral**](https://github.com/spectral-mcp/spectral) · Integration · Independent agent · [Requirements & evidence](https://awesomerea.org/resources/spectral-mcp/)

  Analyze captured application HTTP traffic with an LLM to generate MCP tools, OpenAPI 3.1 specifications, or GraphQL schemas. Generated tools call the observed API directly after capture and authentication setup.

- [**jsdeob-workbench**](https://github.com/Owl4444/jsdeob-workbench) · Tool · [Requirements & evidence](https://awesomerea.org/resources/jsdeob-workbench/)

  Inspect JavaScript ASTs and variable scopes while building visual chains of Babel transforms. Save analysis projects and reusable plugins to iteratively simplify obfuscated scripts.

- [**Browser Reverse Engineering Toolkit**](https://github.com/Dvurechensky/Browser.Reverse.Engineering.Toolkit) · Tool · [Requirements & evidence](https://awesomerea.org/resources/browser-reverse-engineering-toolkit/)

  Capture browser-session evidence, crawl websites in a persistent Chromium session, and generate offline architecture/API reports plus OpenAPI, SDK and mock-server drafts from saved captures.

- [**screenshot-to-code**](https://github.com/abi/screenshot-to-code) · Tool · [Requirements & evidence](https://awesomerea.org/resources/screenshot-to-code/)

  Generate HTML/CSS, Tailwind, React, Vue, Bootstrap or Ionic front-end code from screenshots, mockups, Figma designs or screen recordings with multimodal models; an optional headless-browser preview lets the model check its rendered output. The result is a visual reconstruction of the interface, not recovered original source or backend behavior.

<a id="game"></a>
### Game

[↑ Contents](#contents)

#### Case studies

- [**DX-Ball: reconstruct sound panning**](https://rea.tools/showcase/dx-ball/) · Case study · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-dxball-case/)

  Recover one sound-pan function from instructions and constants; upstream cites 3,205 cases and a 63-byte match.

- [**TH04: recover a DOS bullet-ring helper**](https://rea.tools/showcase/th04/) · Case study · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-th04-case/)

  Inspect a 16-bit PC-98 DOS helper and relate its angle calculation to a pinned reconstruction and historical compiler checks.

- [**Super Mario 64 DS: matching decompilation with relocation checks**](https://github.com/tangosdev/sm64ds-decomp) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/sm64ds-decomp-case/)

  Reconstructs Super Mario 64 DS functions as C/C++ and permitted assembly primitives, comparing compiled output with a user-supplied cartridge dump. Independent relocation-destination checks strengthen the matching gate; integration into the PC port is tracked separately.

- [**GoldenEye 007: an agent-assisted native port from a decompilation**](https://github.com/jkdansereau/goldeneye-pc-port) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/goldeneye-pc-port-case/)

  Builds a native PC port on the existing GoldenEye 007 decompilation, with a host platform layer and assets extracted from the user’s ROM. The project documents agent collaboration, rendering comparisons, playtest scope and unresolved platform support.

- [**ssbu-recomp: static recompilation with explicit mode limits**](https://github.com/Denkishi/ssbu-recomp) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/ssbu-recomp-case/)

  Translates Super Smash Bros. Ultimate 13.0.4 AArch64 code ahead of time and supplies a Windows runtime with Vulkan/OpenGL rendering. It also reconstructs selected fighter scripts as editable C++ and compares translated/source behavior through differential and deterministic tests.

- [**KartPad: platform integration for a Mario Kart Wii recompilation**](https://github.com/chrissotraidis/kartpad) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/kartpad-case/)

  Builds Apple and Android integration around WiiCompiled’s ahead-of-time translation of Mario Kart Wii, with native graphics, input and optional Retro Rewind support. Its status and rights documents distinguish platform acceptance, unresolved device defects and game-content requirements.

- [**BattleShip: an AI-assisted Super Smash Bros. native port**](https://github.com/JRickey/BattleShip) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/battleship-port-case/)

  Ports the existing Super Smash Bros. N64 decompilation using libultraship and Torch. The author’s earlier README describes agent-built graphics/audio comparison tools and differential debugging against emulator behavior, rather than claiming AI recovered the game from a cartridge without prior community work.

- [**Agent decompilation: a byte-matching retrospective**](https://momo5502.com/posts/2026-10-09-game-decompilation/) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/agent-decompilation-oracle-case/)

  Maurice Heumann describes replacing plausible-looking agent output with compiler-based checks of reconstructed functions, relocations, data and types. The retrospective reports 99% function presence and 83% of all functions byte-exact, while keeping the reconstruction code private.

- [**Snowboard Kids 2: an LLM-assisted N64 matching decompilation**](https://github.com/cdlewis/snowboardkids2-decomp) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/snowboardkids2-decomp-case/)

  A public matching decompilation of the N64 game Snowboard Kids 2, begun in 2024 with community decompilation tools. The author’s dated posts document Claude, Codex and GLM workflows, including headless one-shot loops, similarity-based function scheduling and hook-guarded, hash-checked builds, through a reported complete function match.

- [**IsaacRecomp: translating Flash game bytecode to native C++**](https://github.com/whylurking/IsaacRecomp) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/isaacrecomp-case/)

  Translates The Binding of Isaac’s Flash AVM1 bytecode into C++ functions and supplies a native rendering/input runtime. The project reads graphics and audio from the user’s original game and documents deterministic input, headless runs and screenshot regression checks.

- [**Nanolathe: a documented Total Annihilation engine reimplementation**](https://github.com/nanolathe-gg/nanolathe) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/nanolathe-case/)

  Reimplements a Total Annihilation-compatible strategy-game engine in Go, with public file-format research and separate gameplay profiles. It distinguishes intended retail 3.1 behavior from community-patch research and deliberate modern changes, and separates synthetic checks from tests requiring original game data.

- [**TH08: exact-source reconstruction and separately tested ports**](https://github.com/N0zoM1z0/th08) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/th08-reconstruction-case/)

  Reconstructs the original Japanese Touhou 8 version 1.00d against its binary and original compiler, then adapts the recovered code for other platforms. Source presence, strict function matching, whole-executable identity and playable-port checks are recorded as different milestones.

- [**Zelda 64: Recompiled — a native Majora’s Mask port without a full source decompilation**](https://github.com/Zelda64Recomp/Zelda64Recomp) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/zelda64recomp-case/)

  Uses N64Recomp to translate Majora’s Mask into a native application and RT64 for rendering. The project separates static recompilation from source decompilation while reusing decompilation headers and selected functions for patches and enhancements.

- [**OpenGOAL: recovering GOAL code and rebuilding the Jak games**](https://github.com/open-goal/jak-project) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/opengoal-jak-case/)

  Reconstructs readable GOAL code from the original Jak binaries and compiles it with a new GOAL compiler for modern PCs. Its workflow combines a specialized decompiler, manually supplied type information, asset extraction and an interactive development runtime.

- [**LEGO Island: source reconstruction with separately reported exact rebuilds**](https://github.com/isledecomp/isle) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/lego-island-decomp-case/)

  Reconstructs the English LEGO Island 1.1 source for its original 32-bit Windows target. The project distinguishes function-comparison reports, ReproBit’s reported byte-identical retail rebuilds and ordinary developer builds; its modern portable adaptation is a separate repository.

- [**Snowball War: a bounded REA-assisted minigame reconstruction**](https://github.com/tuunanet/rea-ski-or-die-reconstruction) · Case study · Mixed workflow · [Requirements & evidence](https://awesomerea.org/resources/snowball-war-rea-case/)

  The author uses REA’s Ghidra workflow to investigate the DOS Ski or Die binary, document Snowball War rules and rebuild that one minigame in Rust with SDL2. The public notes distinguish recovered tables and mechanics from approximations and deliberate presentation changes.

- [**SpaceCadetPinball: decompiled game logic adapted to SDL2**](https://github.com/k4zmu2a/SpaceCadetPinball) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/space-cadet-pinball-case/)

  Converts the reverse-engineered Space Cadet pinball game into compilable C++ for desktop platforms. The README identifies the Windows XP executable and public PDB, a Full Tilt executable, and the work of recovering structures, naming variables and adapting the decompiled routines.

- [**Super Mario 64: ROM reconstruction with explicit comparison gates**](https://github.com/n64decomp/sm64) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/sm64-decomp-case/)

  Reconstructs Super Mario 64 source for Japanese, North American, European, Shindou and iQue releases. Its build files distinguish original-ROM hash comparison from nonmatching or modified configurations, while source naming and documentation remain ongoing.

- [**Unleashed Recompiled: translating Xbox 360 game code and shaders**](https://github.com/hedge-dev/UnleashedRecomp) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/unleashed-recompiled-case/)

  Builds an unofficial Sonic Unleashed PC port by statically recompiling Xbox 360 PowerPC code with XenonRecomp and Xenos shaders with XenosRecomp. The port adds modern display and modding options while documenting original-engine limits and remaining compatibility issues.

- [**OpenMW: replacing Morrowind’s engine while reusing original content**](https://github.com/OpenMW/openmw) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/openmw-engine-case/)

  Provides an independent engine for playing Morrowind and an alternative editor, OpenMW-CS. It loads original game content through its own runtime and documents script and mod compatibility differences; it is an engine replacement rather than a recovered Bethesda source tree.

- [**REDRIVER2: reconstructing Driver 2 through a PlayStation compatibility layer**](https://github.com/OpenDriver2/REDRIVER2) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/redriver2-case/)

  Translates reverse-engineered Driver 2 MIPS routines into C/C++ and uses Psy-X/Psy-Cross to adapt PlayStation interfaces for desktop systems. The project documents symbol-assisted Ghidra/IDA work alongside intentional bug fixes and gameplay changes.

- [**DevilutionX: porting Diablo’s reconstructed engine**](https://github.com/diasurgical/DevilutionX) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/devilutionx-case/)

  Builds a modern Diablo and Hellfire port on the Devilution reconstruction, with platform support, bug fixes and optional quality-of-life features. The project documents the original symbol-assisted reconstruction and includes selected dungeon-generation and saved-game regression checks.

- [**LASRecomp: Link’s Awakening static recompilation**](https://github.com/peiikai/LASRecomp) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/lasrecomp/)

  A native desktop reconstruction of the 2019 Switch version of Link’s Awakening using static recompilation. The author attributes most code, tooling and reverse-engineering work to Claude Code with human direction and review.

- [**ArkWeb: a two-game movement and collision experiment**](https://github.com/luki-1/ArkWeb) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/arkweb-two-game-case/)

  Runs Spider-Man Remastered and Arkham Knight together, streaming Gotham collision into Spider-Man’s physics world and compositing his rendered frame into Arkham. This experimental runtime bridge is not a recovered standalone game or new engine.

#### Tools, projects and integrations

- [**RenderDoc**](https://github.com/baldurk/renderdoc) · Tool · [Requirements & evidence](https://awesomerea.org/resources/renderdoc/)

  Inspect frame captures, draw calls, shaders, and graphics resources in your own game or graphics application.

- [**AssetRipper**](https://github.com/AssetRipper/AssetRipper) · Tool · [Requirements & evidence](https://awesomerea.org/resources/assetripper/)

  Analyze Unity game files, inspect asset dependencies, and convert supported assets into Unity project formats.

- [**Cpp2IL**](https://github.com/SamboyCoding/Cpp2IL) · Tool · [Requirements & evidence](https://awesomerea.org/resources/cpp2il/)

  Recover managed representations from Unity IL2CPP builds using binary and metadata analysis; reconstruction remains a work in progress.

- [**Il2CppDumper**](https://github.com/Perfare/Il2CppDumper) · Tool · [Requirements & evidence](https://awesomerea.org/resources/il2cppdumper/)

  Recover IL2CPP metadata and dummy assemblies, and generate helper scripts for native analysis tools; method code is not restored.

- [**RenderDoc MCP**](https://github.com/scarletfantasy/renderdoc-mcp) · Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/renderdoc-mcp/)

  Expose existing RenderDoc captures to an agent for bounded frame, pipeline, resource, and shader inspection.

- [**UndertaleModTool**](https://github.com/UnderminersTeam/UndertaleModTool) · Tool · [Requirements & evidence](https://awesomerea.org/resources/undertalemodtool/)

  Browse and modify supported GameMaker data files, extract assets, and decompile or compile GML VM code. Includes room editing, scripted changes, a CLI, and the reusable UndertaleModLib library.

- [**frida-il2cpp-bridge**](https://github.com/vfsfitvnm/frida-il2cpp-bridge) · Tool · [Requirements & evidence](https://awesomerea.org/resources/frida-il2cpp-bridge/)

  Inspect IL2CPP classes, methods, and fields in a live process, and trace or intercept method calls without supplying global-metadata.dat. Complements static IL2CPP dumpers with runtime observation.

- [**objdiff**](https://github.com/encounter/objdiff) · Tool · [Requirements & evidence](https://awesomerea.org/resources/objdiff/)

  Compare functions and data in reference and rebuilt object files to guide matching decompilation. Displays instruction-level differences, demangles C++ symbols, and can rebuild when source files change.

- [**decomp-permuter**](https://github.com/simonlindholm/decomp-permuter) · Tool · [Requirements & evidence](https://awesomerea.org/resources/decomp-permuter/)

  Randomly or systematically permutes one C function, recompiling each variant and scoring it against a target object file to search for matching compiler output. PERM macros specify manual alternatives, and the optional permuter<span>@</span>home mode distributes runs to other workers.

- [**asm-differ**](https://github.com/simonlindholm/asm-differ) · Tool · [Requirements & evidence](https://awesomerea.org/resources/asm-differ/)

  Diffs original and rebuilt assembly for one function or ROM address to guide matching decompilation; its watch mode can rerun make when sources change. The README describes it as decomp.me’s default diff viewer and points to objdiff as a modern alternative.

- [**UE Explorer**](https://github.com/UE-Explorer/UE-Explorer) · Tool · [Requirements & evidence](https://awesomerea.org/resources/ue-explorer/)

  Explore Unreal packages through class, property, and dependency trees; decompile and export UnrealScript classes, inspect bytecode, and examine structured binary data.

- [**GARbro**](https://github.com/morkt/GARbro) · Tool · [Requirements & evidence](https://awesomerea.org/resources/garbro/)

  Browse recognized visual-novel resource archives as folders, preview their contents, and extract images or audio with conversion to common formats.

- [**Godot RE Tools**](https://github.com/GDRETools/gdsdecomp) · Tool · [Requirements & evidence](https://awesomerea.org/resources/godot-re-tools/)

  Recover supported Godot project files, GDScript and imported resources from exported games. Includes PCK inspection and extraction, script decompilation, and resource conversion for examining and rebuilding project structure.

- [**UE4SS**](https://github.com/UE4SS-RE/RE-UE4SS) · Tool · [Requirements & evidence](https://awesomerea.org/resources/ue4ss/)

  Inspect Unreal Engine games at runtime through live UObject property views, reflected C++ header dumps, property mappings and actor dumps. Lua and C++ APIs support experiments while reconstructing game structures.

- [**FModel**](https://github.com/4sval/FModel) · Tool · [Requirements & evidence](https://awesomerea.org/resources/fmodel/)

  Explore Unreal Engine game archives with CUE4Parse-backed package and property inspection, asset previews and export. The 2026 summer release adds USD world export for reconstructing supported scene content.

- [**PSP Web Recomp**](https://github.com/snuri00/psp-web-recomp) · Project · [Requirements & evidence](https://awesomerea.org/resources/psp-web-recomp/)

  Translate PSP MIPS executables into C++ and WebAssembly, backed by a PSP high-level emulation runtime and WebGL2 renderer. Native tracing, frame capture and audio tools support investigating missing behavior during game porting.

- [**N64: Recompiled**](https://github.com/N64Recomp/N64Recomp) · Tool · [Requirements & evidence](https://awesomerea.org/resources/n64recomp/)

  Statically recompiles N64 MIPS binaries into C functions from symbol metadata, emitting function lookups and relocation macros so a runtime can handle statically linked and relocatable overlays. The output needs a runtime such as N64ModernRuntime; the repository also includes RSP microcode and mod tooling.

- [**XenonRecomp**](https://github.com/hedge-dev/XenonRecomp) · Tool · [Requirements & evidence](https://awesomerea.org/resources/xenonrecomp/)

  Converts Xbox 360 PowerPC executables into C++ that can be compiled for other platforms, with the XenonAnalyse companion detecting jump tables and function boundaries. Output is a literal instruction translation rather than decompiled code and needs a runtime that the project does not supply.

<a id="app"></a>
### App

[↑ Contents](#contents)

#### Case studies

- [**Aegis: trace a login-code calculation**](https://rea.tools/showcase/aegis/) · Case study · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-aegis-case/)

  An official APK investigation follows TOTP methods in Aegis and publishes artifact identities and selected Evidence.

- [**Notion: trace the clipboard bridge**](https://rea.tools/showcase/notion/) · Case study · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-notion-case/)

  Trace a packaged Electron clipboard path using REA findings and separate source inspection; the dynamic wrapper remains a stated limit.

- [**ReaCut: video-editor reconstruction**](https://github.com/Xiangyu-CAS/rea-capcut) · Case study · Mixed workflow · [Requirements & evidence](https://awesomerea.org/resources/reacut-reconstruction/)

  An independent video editor whose authors document REA-assisted investigation of Jianying/CapCut behavior and project formats. The public implementation includes a local timeline, FFmpeg export and an experimental, lossy draft importer.

- [**zee-rp: reconstructing supported Axure RP 11 document operations**](https://github.com/LilZeeCN/zee-rp) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/zee-rp-case/)

  Reads and rewrites supported native Axure RP 11 documents through a binary-record codec, reference-aware cloning and constrained interaction writers. CLI and MCP interfaces expose inspected edits while keeping offline structure checks separate from native application acceptance.

- [**Virtual Desktop Streamer: rehosting the platform layer on Linux**](https://github.com/cudanexus/vd-streamer-linux) · Case study · Mixed workflow · [Requirements & evidence](https://awesomerea.org/resources/vd-streamer-linux-case/)

  An author-reported Claude Code and REA workflow replaces the macOS streamer’s capture, encoding, audio and input layer with Linux implementations while reusing vendor protocol libraries. The documented result targets desktop streaming and video playback, not Windows-only VR game streaming.

- [**Open Claude UI: REA-informed interface reference components**](https://github.com/Caho1/open-claude-ui) · Case study · Mixed workflow · [Requirements & evidence](https://awesomerea.org/resources/open-claude-ui-case/)

  Publishes React components, motion helpers and design-system notes derived from the author’s reported REA investigation of Claude Desktop. It is useful as an interface-reconstruction case, with version-specific observations rather than proof of a complete assistant application or backend clone.

- [**PlxNative: reconstructing a native webOS media-client interface**](https://github.com/GLinnik21/plx-native) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/plx-native-case/)

  An unofficial Plex client built after the author investigated LG webOS native media interfaces with Ghidra and coding agents. It draws its own Rust/OpenGL interface and uses the television’s decoder, with documented host, simulator and real-device test tiers.

- [**Windows Calculator: reconstructing percentage rules**](https://github.com/morluto/rea/blob/c360cfcd6d7901514b16dd6113eba2e0b0fdf422/website/evidence/calculator-and-dino.md#windows-calculator) · Case study · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-calculator-percent-case/)

  REA’s case traces the installed Windows Calculator model DLL to explain different percentage behavior for multiplication/division and other operations. An analyst-selected function is interpreted against public Microsoft source and demonstrated with fixed browser examples.

- [**Feishu: an author-reported isolated second app instance**](https://benx.ai/blog/posts/rea-reverse-engineer-feishu-dual-instance/) · Case study · Mixed workflow · [Requirements & evidence](https://awesomerea.org/resources/feishu-dual-instance-case/)

  The author reports using Codex and REA analysis to adapt a separate macOS Feishu copy with its own application identity, data directory and single-instance lock. The account describes local signing and separation checks while retaining the original app unchanged.

- [**PhotoCraft: editor workflow reconstruction and PSD round-trip boundaries**](https://github.com/storytold/photocraft) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/photocraft-case/)

  The authors describe this Rust image editor as a clean-room reimplementation of Photoshop-style workflows. Its document engine, UI and automation interfaces share editing commands, while the source distinguishes PSD editor round trips from byte preservation in the standalone file codec.

- [**WordCraft: document workflow reconstruction and bounded DOCX compatibility**](https://github.com/storytold/wordcraft) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/wordcraft-case/)

  The authors describe WordCraft as a clean-room Rust implementation of familiar Microsoft Word workflows. It provides its own document model, layout engine and DOCX reader/writer, with desktop and browser interfaces; source tests exercise selected editing and file-preservation behavior.

- [**GridCraft: spreadsheet workflow reconstruction and XLSX round-trip limits**](https://github.com/storytold/gridcraft) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/gridcraft-case/)

  The authors describe GridCraft as a clean-room Rust implementation of Excel-style spreadsheet workflows. A workbook model, formula parser and dependency-driven recalculation are connected to XLSX I/O and a shared editing-command layer for desktop, browser and automation interfaces.

- [**DeckCraft: presentation workflow reconstruction and bounded PPTX interchange**](https://github.com/storytold/deckcraft) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/deckcraft-case/)

  The authors describe DeckCraft as a clean-room Rust implementation of PowerPoint-style presentation workflows. Its slide model, rendering and command layers support desktop/browser editing and PPTX interchange; reviewed source tests check constructed decks and selected preserved package parts.

- [**LSX II Volume Fixer: reconstructing volume behavior**](https://github.com/roberdorfer/kef-lsx-volume) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/kef-lsx-volume-case/)

  Uses measured USB-volume behavior and a macOS audio proxy to map volume keys to a KEF LSX II’s LAN control. The project reports more even steps while forwarding USB audio; the speaker firmware is unchanged.

#### Tools, projects and integrations

- [**JADX-AI-MCP**](https://github.com/zinja-coder/jadx-ai-mcp) · Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/jadx-ai-mcp/)

  JADX plugin paired with a Python MCP server to inspect decompiled Android classes, resources, cross-references and debugger context.

- [**apktool-mcp-server**](https://github.com/zinja-coder/apktool-mcp-server) · Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/apktool-mcp-server/)

  Python MCP server that drives a local Apktool install so agents can decode APKs; list, read, search and edit smali and resource files; read AndroidManifest.xml and apktool.yml; and rebuild the project.

- [**frida-mcp (yfe404)**](https://github.com/yfe404/frida-mcp) · Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/frida-mcp-yfe404/)

  Frida MCP server with persistent instrumentation sessions, runtime inspection and Android static-to-dynamic navigation.

- [**Super Trouper**](https://github.com/crissyfield/super-trouper) · Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/super-trouper/)

  Single-binary Frida MCP server for discovering devices, managing process sessions and loading instrumentation scripts.

- [**Frida**](https://github.com/frida/frida) · Tool · [Requirements & evidence](https://awesomerea.org/resources/frida/)

  Dynamic instrumentation toolkit for observing and scripting the behavior of live native and managed processes.

- [**JADX**](https://github.com/skylot/jadx) · Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/jadx/)

  Dex-to-Java decompiler with CLI/GUI navigation, resource decoding and cross-reference search for Android packages.

- [**Apktool**](https://github.com/iBotPeaches/Apktool) · Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/apktool/)

  Decodes Android resources and smali into a project-like tree and can rebuild modified packages.

- [**Androguard**](https://github.com/androguard/androguard) · Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/androguard/)

  Python toolkit for APK/DEX metadata, bytecode and reference analysis; the v5 source branch also documents agent skills and MCP.

- [**ILSpy**](https://github.com/icsharpcode/ILSpy) · Tool · .NET · [Requirements & evidence](https://awesomerea.org/resources/ilspy/)

  .NET assembly browser and C# decompiler with whole-project export, metadata inspection and a scriptable command-line frontend.

- [**dnSpyEx**](https://github.com/dnSpyEx/dnSpy) · Tool · .NET · [Requirements & evidence](https://awesomerea.org/resources/dnspyex/)

  Community continuation of dnSpy for debugging and editing .NET assemblies without the original source.

- [**<span>@</span>electron/asar**](https://github.com/electron/asar) · Tool · [Requirements & evidence](https://awesomerea.org/resources/electron-asar/)

  Electron's archive tool lists and extracts ASAR contents so packaged JavaScript and application assets can be inspected.

- [**Mobile Security Framework (MobSF)**](https://github.com/MobSF/Mobile-Security-Framework-MobSF) · Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/mobsf/)

  Inspect mobile application packages with static analysis and supported-device dynamic testing, including runtime behavior and network traffic, through a web interface and APIs.

- [**objection**](https://github.com/sensepost/objection) · Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/objection/)

  Explore running Android and iOS apps with a Frida-backed command interface for inspecting app storage, memory, runtime objects, and instrumented behavior.

- [**Grapefruit**](https://github.com/ChiChou/grapefruit) · Tool · [Requirements & evidence](https://awesomerea.org/resources/grapefruit/)

  Inspect and hook running iOS and Android apps from a Frida-based web interface, with method and crypto-API hooks, filesystem and SQLite browsers, iOS keychain and UI-hierarchy views, and HTTP capture from common networking libraries.

- [**Blutter**](https://github.com/worawit/blutter) · Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/blutter/)

  Analyze Flutter Android ARM64 AOT binaries using the matching Dart runtime. Produces annotated assembly, object-pool dumps and a target-specific Frida script template for investigating compiled Dart application logic.

- [**hermes-dec**](https://github.com/P1sec/hermes-dec) · Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/hermes-dec/)

  Parse, disassemble and partially decompile React Native Hermes bytecode bundles. Makes HBC headers and instructions inspectable and emits pseudocode for understanding compiled application logic.

- [**Recaf**](https://github.com/Col-E/Recaf) · Tool · JVM · [Requirements & evidence](https://awesomerea.org/resources/recaf/)

  Inspect and modify compiled JVM applications with integrated decompilers, bytecode assembly, reference search, mappings and deobfuscation tools. The reviewed 4.0 preview also provides basic read-only Android bytecode inspection.

- [**nibkit**](https://github.com/tokenbleed/nibkit) · Tool · [Requirements & evidence](https://awesomerea.org/resources/nibkit/)

  Decode compiled iOS/macOS interface archives into object trees, Outlet/Action connections, custom classes and navigation relationships. Exports JSON or Mermaid diagrams and exposes read-only inspection commands through MCP.

- [**AOTopsy**](https://github.com/BroNils/aotopsy) · Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/aotopsy/)

  Statically inspect Flutter/Dart AOT libapp.so files to recover available metadata, class structures, call edges and pseudocode without embedding a Dart VM or compiling a matching SDK. Supports ARM64 and x86\_64 analysis paths.

- [**hbctool**](https://github.com/bongtrop/hbctool) · Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/hbctool/)

  Disassemble and reassemble supported React Native Hermes bytecode bundles through HASM files, enabling bytecode inspection and editing for the explicitly supported legacy HBC versions.

<a id="native-binary"></a>
### Native Binary

[↑ Contents](#contents)

#### Case studies

- [**DownUnderCTF: masked-squares flag checker**](https://rea.tools/showcase/ctf/) · Case study · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-ctf-case/)

  An official educational challenge investigation connects binary checks to equations and records an original-program validation.

#### Tools, projects and integrations

- [**Ghidra**](https://github.com/NationalSecurityAgency/ghidra) · Tool · [Requirements & evidence](https://awesomerea.org/resources/ghidra/)

  Open-source analysis suite for disassembly, decompilation, graphs and Java/Python automation across executable formats.

- [**radare2**](https://github.com/radareorg/radare2) · Tool · [Requirements & evidence](https://awesomerea.org/resources/radare2/)

  Scriptable command-line framework for inspecting, disassembling, debugging and modifying binaries across many architectures.

- [**Cutter**](https://github.com/rizinorg/cutter) · Tool · [Requirements & evidence](https://awesomerea.org/resources/cutter/)

  Rizin-powered graphical reverse-engineering workspace with extensible views and Ghidra decompiler integration.

- [**Qiling**](https://github.com/qilingframework/qiling) · Tool · [Requirements & evidence](https://awesomerea.org/resources/qiling/)

  Python emulation framework that adds OS, filesystem and API behavior around CPU emulation for instrumented binary analysis.

- [**Unicorn Engine**](https://github.com/unicorn-engine/unicorn) · Tool · Library · [Requirements & evidence](https://awesomerea.org/resources/unicorn/)

  Multi-architecture CPU emulator for executing selected instruction ranges with register, memory and hook control.

- [**angr**](https://github.com/angr/angr) · Tool · Library · [Requirements & evidence](https://awesomerea.org/resources/angr/)

  Python binary-analysis framework combining control-flow recovery, symbolic execution, data-flow analysis and decompilation.

- [**LIEF**](https://github.com/lief-project/LIEF) · Tool · Library · [Requirements & evidence](https://awesomerea.org/resources/lief/)

  Library for structured parsing and modification of executable formats including ELF, PE and Mach-O.

- [**Capstone**](https://github.com/capstone-engine/capstone) · Tool · Library · [Requirements & evidence](https://awesomerea.org/resources/capstone/)

  Disassembly library with architecture-neutral APIs and instruction details for custom binary-analysis pipelines.

- [**ImHex**](https://github.com/WerWolv/ImHex) · Tool · [Requirements & evidence](https://awesomerea.org/resources/imhex/)

  Hex editor with a binary-pattern language, structured data inspection and visual tools for understanding file formats.

- [**x64dbg**](https://github.com/x64dbg/x64dbg) · Tool · [Requirements & evidence](https://awesomerea.org/resources/x64dbg/)

  Windows binary debugger with disassembly, memory views and plugins for analyzing programs without source code.

- [**GDB**](https://sourceware.org/gdb/) · Tool · [Requirements & evidence](https://awesomerea.org/resources/gdb/)

  Native and remote debugger for controlling execution and inspecting live or crashed program state.

- [**rr**](https://github.com/rr-debugger/rr) · Tool · [Requirements & evidence](https://awesomerea.org/resources/rr/)

  Records process execution and replays it under GDB, enabling repeatable inspection and reverse execution.

- [**Diaphora**](https://github.com/joxeankoret/diaphora) · Tool · [Requirements & evidence](https://awesomerea.org/resources/diaphora/)

  IDA-based binary diffing that matches functions and transfers names, comments and types between analyzed versions.

- [**BinDiff**](https://github.com/google/bindiff) · Tool · [Requirements & evidence](https://awesomerea.org/resources/bindiff/)

  Compares disassembled binaries to find matching functions and changed code across versions.

- [**Detect It Easy**](https://github.com/horsicq/Detect-It-Easy) · Tool · [Requirements & evidence](https://awesomerea.org/resources/detect-it-easy/)

  Format-aware file identification and static inspection using parsers, signatures and programmable heuristics.

- [**r2frida**](https://github.com/nowsecure/r2frida) · Tool · [Requirements & evidence](https://awesomerea.org/resources/r2frida/)

  Use radare2 commands and Frida instrumentation together to inspect local or remote process memory, symbols, classes, and runtime calls on desktop and mobile targets.

- [**Kaitai Struct**](https://github.com/kaitai-io/kaitai_struct) · Tool · Library · [Requirements & evidence](https://awesomerea.org/resources/kaitai-struct/)

  Turn documented binary layouts into reusable parsers for files and network packets. A .ksy specification can be inspected with visualizers and compiled to multiple languages, helping preserve reverse-engineered format knowledge in interoperable implementations.

- [**GoReSym**](https://github.com/mandiant/GoReSym) · Tool · [Requirements & evidence](https://awesomerea.org/resources/goresym/)

  Recover Go build metadata, function names and address ranges, source file and line tables, embedded types and strings from Go binaries, including stripped and some malformed unpacked samples. JSON output can be imported into IDA Pro with the included IDAPython script.

- [**rev.ng**](https://github.com/revng/revng) · Tool · [Requirements & evidence](https://awesomerea.org/resources/revng/)

  Open-source decompilation pipeline that lifts x86-64, AArch64, i386, ARM and MIPS code with QEMU, runs LLVM-based analyses and emits C designed to be valid and recompilable. Data layout analysis infers structures from pointer use; an editable YAML model and Python or TypeScript wrappers support automation. Its VSCode-based UI is a separate closed-beta product, with commercial plans announced.

<a id="firmware"></a>
### Firmware and Hardware

[↑ Contents](#contents)

#### Case studies

- [**PicoPrint: LX-D02 printer investigation**](https://github.com/bigtower17/picoprint) · Case study · Mixed workflow · [Requirements & evidence](https://awesomerea.org/resources/picoprint-rea-investigation/)

  The author describes REA-assisted Android investigation followed by separate Hermes decompilation to support a Windows BLE printer.

- [**ThinkPad IMX471: recovering camera tuning for Linux**](https://github.com/cschalle/mipi-fixes-x1-aura) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/thinkpad-imx471-camera-case/)

  Recovers selected camera-tuning structures from an Intel Windows driver package and uses them to repair Linux image capture on one ThinkPad model. Public CPFF/AIQB parsers, kernel patches and libcamera changes accompany the author’s Claude-assisted investigation and bounded before/after measurements.

#### Tools, projects and integrations

- [**Binwalk**](https://github.com/ReFirmLabs/binwalk) · Tool · [Requirements & evidence](https://awesomerea.org/resources/binwalk/)

  Identifies embedded formats and optionally extracts their contents, with entropy analysis for firmware triage.

- [**unblob**](https://github.com/onekey-sec/unblob) · Tool · [Requirements & evidence](https://awesomerea.org/resources/unblob/)

  Recursively extracts archives and filesystems from binary blobs while reporting chunk boundaries and unknown regions.

- [**Ghidra Firmware Utilities**](https://github.com/al3xtjames/ghidra-firmware-utils) · Tool · [Requirements & evidence](https://awesomerea.org/resources/ghidra-firmware-utils/)

  Ghidra loaders and helpers for PCI option ROMs, UEFI firmware volumes, Intel flash descriptors and coreboot images.

- [**EMBA**](https://github.com/e-m-b-a/emba) · Tool · [Requirements & evidence](https://awesomerea.org/resources/emba/)

  Extract firmware, combine static checks with emulation-based analysis, inventory software components, and generate web reports and SBOMs for further investigation.

- [**Firmware Analysis and Comparison Tool (FACT)**](https://github.com/fkie-cad/FACT_core) · Tool · [Requirements & evidence](https://awesomerea.org/resources/fact-core/)

  Unpack and analyze firmware through an extensible platform whose web interface and HTTP API make component contents and analysis results searchable and comparable across samples.

- [**OFRAK**](https://github.com/redballoonsecurity/ofrak) · Tool · [Requirements & evidence](https://awesomerea.org/resources/ofrak/)

  Recursively identify, unpack, analyze, modify, and repack firmware and binary formats using a resource-tree GUI and Python API, with optional disassembler backends.

- [**FirmAE**](https://github.com/pr0v3rbs/FirmAE) · Tool · [Requirements & evidence](https://awesomerea.org/resources/firmae/)

  Emulate router and IP-camera firmware to inspect network services and runtime behavior, with automated emulation checks and separate analysis, run, and debugging modes.

- [**PulseView**](https://github.com/sigrokproject/pulseview) · Tool · [Requirements & evidence](https://awesomerea.org/resources/pulseview/)

  Examine captured logic and analog waveforms with sigrok's graphical frontend. Protocol decoders and decoder stacking expose bus messages and higher-level device operations, making hardware communication traces useful for firmware and interoperability investigations.

- [**UEFITool**](https://github.com/LongSoft/UEFITool) · Tool · [Requirements & evidence](https://awesomerea.org/resources/uefitool/)

  Parse UEFI firmware images into an inspectable tree and check their structure. Companion UEFIExtract and UEFIFind tools extract parsed contents and locate patterns, supporting analysis of firmware components and vendor formats.

- [**Glasgow Interface Explorer**](https://github.com/GlasgowEmbedded/glasgow) · Tool · [Requirements & evidence](https://awesomerea.org/resources/glasgow-interface-explorer/)

  Use FPGA-based open hardware and Python applets to read and write SPI flash, I2C EEPROM and parallel memory chips, determine JTAG pinouts, debug supported processors and analyze UART, SPI and QSPI transactions on physical devices.

- [**Penguin**](https://github.com/rehosting/penguin) · Tool · [Requirements & evidence](https://awesomerea.org/resources/penguin/)

  Rehost embedded Linux firmware from an extracted root filesystem using a generated, editable configuration of emulation transformations, then refine it through a guest root shell, forwarded network services and recorded dynamic-analysis output.

<a id="protocol"></a>
### Protocol

[↑ Contents](#contents)

#### Case studies

- [**open-appleremote: Siri Remote protocol reconstruction**](https://github.com/a-funk/open-appleremote) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/open-appleremote-case/)

  Reconstructs first-generation Siri Remote Bluetooth reports for Linux, decoding buttons, touch and tvOS-style gestures. The Python implementation and protocol notes distinguish measured behavior, historical reports and inferred meanings.

- [**GAMEKB-K17: reconstructing a macropad configuration protocol**](https://github.com/dvdarkin/gamekb-k17) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/gamekb-k17-case/)

  Implements the vendor HID configuration protocol for the GAMEKB-K17/HCY-K017 macropad. It writes key mappings, firmware macros and RGB settings, then reads them back; protocol notes separate tested commands from unconfirmed observations and other-device findings.

- [**CF632BLE: a local client from scale-protocol research**](https://github.com/guyru/cf632ble) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/cf632ble-case/)

  Reimplements the CF632BLE scale’s BLE protocol and body-composition calculations from research on the vendor’s Unique Health Android app. A static Web Bluetooth client receives measurements, manages device profiles and keeps its history in browser storage.

- [**cooler-lcd: a Thermalright display protocol implementation**](https://github.com/kristjaningi/cooler-lcd) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/cooler-lcd-case/)

  Implements a USB picture-transfer driver for Thermalright Vision cooler displays, with a Rust dashboard replacing the vendor display application. The documented protocol sends a header and JPEG frames, with periodic resends to prevent the device reverting to its logo.

- [**hw-harness: scanner USB protocol investigation**](https://github.com/cschalle/hw-harness) · Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/hw-harness-reference-case/)

  Documents an author-reported scanner investigation comparing vendor-driver USB control transfers with Linux-driver traces to infer initialization, timing and resolution parameters. The released harness organizes reference capture and comparison; it does not automatically recover a complete protocol specification.

#### Tools, projects and integrations

- [**Wireshark**](https://gitlab.com/wireshark/wireshark) · Tool · [Requirements & evidence](https://awesomerea.org/resources/wireshark/)

  Inspect captured application and device traffic as decoded protocol fields, with filtering and shared GUI/TShark dissection. Custom dissectors let an analyst encode newly understood packet formats and compare protocol implementations.

- [**Netzob**](https://github.com/netzob/netzob) · Tool · [Requirements & evidence](https://awesomerea.org/resources/netzob/)

  Model communication protocols and infer message layouts from traces, with configured active learning for protocol state machines. Python APIs expose message fields, symbols and automata for parsing, traffic generation and fuzzing.

- [**Scapy**](https://github.com/secdev/scapy) · Tool · [Requirements & evidence](https://awesomerea.org/resources/scapy/)

  Script packet dissection, construction, request/reply matching and capture-file analysis in Python. Custom packet fields and layer bindings let analysts encode understood wire formats and investigate protocol behavior.

- [**Universal Radio Hacker (URH)**](https://github.com/jopohl/urh) · Tool · [Requirements & evidence](https://awesomerea.org/resources/universal-radio-hacker/)

  Demodulate and decode signals captured with software-defined radios, with automatic modulation-parameter detection and customizable decodings. Analysts assign protocol fields and message types by hand or review rule-based automatic field inference; a fuzzer targets stateless protocols and a simulator supports stateful exchanges.

- [**SavvyCAN**](https://github.com/collin80/SavvyCAN) · Tool · [Requirements & evidence](https://awesomerea.org/resources/savvycan/)

  Capture or load CAN bus traffic and investigate frames with sniffer, graphing, file-comparison and ISO-TP/UDS decoding views; loaded or analyst-edited DBC files map raw bytes to named signals. Separate custom-sender, fuzzing and UDS-scan windows transmit frames on a live bus.

- [**AALpy**](https://github.com/DES-Lab/AALpy) · Tool · [Requirements & evidence](https://awesomerea.org/resources/aalpy/)

  General-purpose Python automata-learning library that infers deterministic, non-deterministic, stochastic and pushdown models of black-box systems from active queries or passive traces. Its README links a separate Bluetooth Low Energy study whose repository reports learned connection and legacy-pairing state machines; message formats are not inferred.

<a id="agents-and-mcp"></a>
### Agents and MCP

[↑ Contents](#contents)

- [**REA — Reverse Engineer Anything**](https://github.com/morluto/rea) · Project · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-upstream/)

  The upstream CLI and MCP server for evidence-based investigations of shipped software and runtime behavior.

- [**Official reverse-engineer-anything skill**](https://github.com/morluto/rea/tree/main/.agents/skills/reverse-engineer-anything) · Integration · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-official-skill/)

  Target routing, connection recovery and evidence practices for agents using REA.

- [**dsh-mcp-rea**](https://github.com/Ersith/dsh-mcp-rea) · Integration · REA · [Requirements & evidence](https://awesomerea.org/resources/dsh-mcp-rea/)

  A community MCP bridge presents a smaller selected tool surface and forwards explicit commands to the REA CLI.

- [**rea-jev**](https://github.com/juan-viox/rea-jev) · Integration · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-jev/)

  A Claude Code plugin adds Jev-based routing and evidence checks around a pinned REA MCP integration.

- [**rea-casebook**](https://github.com/pablodiazjorge/rea-casebook) · Integration · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-casebook/)

  A Claude Code mod collects received REA Evidence, tracks unknowns and records findings that cite delivered evidence IDs.

- [**Hex-Rays IDA MCP**](https://github.com/HexRaysSA/ida-mcp) · Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/hex-rays-ida-mcp/)

  Official Hex-Rays MCP server for agent access to IDA databases, with headless operation and optional GUI integration.

- [**GhidraMCP**](https://github.com/LaurieWired/GhidraMCP) · Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/ghidramcp/)

  Ghidra extension and MCP bridge exposing decompilation, symbol navigation and renaming to agents, with GUI and headless modes.

- [**Binary Ninja MCP (official)**](https://docs.binary.ninja/guide/mcp.html) · Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/binary-ninja-official-mcp/)

  Binary Ninja's own MCP interface exposes functions, symbols, disassembly, intermediate languages and decompiled text to agents.

- [**Binary Ninja MCP (fosdickio)**](https://github.com/fosdickio/binary_ninja_mcp) · Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/binary-ninja-community-mcp/)

  Community Binary Ninja plugin and bridge for MCP clients, including workflows that switch among multiple open binaries.

- [**IDA Pro MCP (mrexodia)**](https://github.com/mrexodia/ida-pro-mcp) · Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/ida-pro-mcp-community/)

  Community IDA integration useful for existing setups and migration context; its maintainer now recommends the official Hex-Rays MCP server.

- [**Radare2 MCP Server**](https://github.com/radareorg/radare2-mcp) · Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/radare2-mcp/)

  Native radare2 MCP server offering binary-analysis tools, reusable sessions and configurable read-only access.

- [**r2ai**](https://github.com/radareorg/r2ai) · Integration · Independent agent · [Requirements & evidence](https://awesomerea.org/resources/r2ai/)

  AI plugins inside radare2 for function explanations, naming suggestions and model-assisted decompilation using local or remote models.

- [**DAILA**](https://github.com/mahaloz/DAILA) · Integration · Independent agent · [Requirements & evidence](https://awesomerea.org/resources/daila/)

  Decompiler-independent AI assistant for function summaries and naming across IDA, Ghidra, Binary Ninja and angr-management.

- [**RevEng.AI Ghidra Plugin**](https://github.com/RevEngAI/plugin-ghidra) · Integration · Independent agent · [Requirements & evidence](https://awesomerea.org/resources/revengai-ghidra/)

  Connects Ghidra to RevEng.AI for function similarity, recovered names, AI explanations and agent-assisted annotation.

- [**LLDB MCP**](https://lldb.llvm.org/use/mcp.html) · Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/lldb-mcp/)

  LLDB's official MCP interface gives agents debugger sessions and commands for breakpoints, memory inspection and stepping.

- [**Claude Reverse Engineering Skill**](https://github.com/EncidXVII/claude-reverse-engineering-skill) · Integration · Independent agent · [Requirements & evidence](https://awesomerea.org/resources/claude-reverse-engineering-skill/)

  Community agent skill for triage, headless exports and evidence-based RE reports; explicitly documents workflows with REA and other MCP servers.

- [**SpecterOps Reverse Engineering Skills**](https://github.com/SpecterOps/skills/tree/main/plugins/reverse-engineering) · Integration · Independent agent · [Requirements & evidence](https://awesomerea.org/resources/specterops-re-skills/)

  Focused Binary Ninja and Ghidra analysis skills that describe MCP tool use, analysis recipes and annotation practices.

- [**pyghidra-mcp**](https://github.com/clearbluejar/pyghidra-mcp) · Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/pyghidra-mcp/)

  PyGhidra-based MCP server that analyzes every binary in a Ghidra project and exposes decompilation, cross-references, call graphs, symbol and string search, indexed semantic code search, and renaming, typing and comment edits. A separate HTTP CLI client and an optional mode driving a Ghidra GUI it launches are included.

<a id="related-collections"></a>
### Related Collections

[↑ Contents](#contents)

- [**Awesome Reverse Engineering**](https://github.com/morluto/awesome-reverse-engineering) · Collection · [Requirements & evidence](https://awesomerea.org/resources/morluto-awesome-re/)

  A task-oriented reverse-engineering resource list by REA's maintainer, useful for broader tools and foundations.

- [**Awesome REA Cases**](https://github.com/songshikang0111/awesome-REA-cases) · Collection · [Requirements & evidence](https://awesomerea.org/resources/awesome-rea-cases/)

  A bilingual collection of REA and other AI-assisted reverse engineering cases, with source links and explicit distinctions between reported and reproduced outcomes.

- [**awesome-rea (yibie): verification-focused projects and practice reports**](https://github.com/yibie/awesome-rea) · Collection · [Requirements & evidence](https://awesomerea.org/resources/yibie-awesome-rea/)

  Organizes AI-assisted game decompilation, native ports, static recompilation and tooling around stated acceptance checks, alongside a separate track of practitioner write-ups and discussions. Useful for finding primary reports and comparing how projects define correctness.

- [**Awesome REA/Decompiled Games**](https://github.com/HaozheH3/awesome-rea-games) · Collection · [Requirements & evidence](https://awesomerea.org/resources/haozhe-awesome-rea-games/)

  Groups game decompilations, source reconstructions, recompilations, native ports and demos by original game, with comparison rows linking related projects. It distinguishes launchers, engine work and creator-shared showcases from source-reconstruction efforts.

<a id="references-and-learning"></a>
### References and Learning

[↑ Contents](#contents)

- [**Installation and client setup**](https://github.com/morluto/rea/blob/main/docs/installation.md) · Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-installation/)

  Reviewed setup plans, client registration, provider prerequisites and scoped readiness checks.

- [**CLI and Evidence**](https://github.com/morluto/rea/blob/main/docs/cli.md) · Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-cli-evidence/)

  CLI workflows for saving Evidence and projecting smaller views from completed analysis.

- [**MCP contracts and generated catalog**](https://github.com/morluto/rea/blob/main/docs/mcp-contracts.md#generated-catalog) · Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-mcp-contracts/)

  Canonical tool contracts, provider discovery and Evidence semantics for integration authors.

- [**Native binary investigation**](https://github.com/morluto/rea/blob/main/docs/native-investigation.md) · Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-native-workflow/)

  Locate a function, inspect instructions and pseudocode, and follow references with a selected native provider.

- [**Cross-layer JavaScript application workflows**](https://github.com/morluto/rea/blob/main/docs/javascript-application-workflows.md) · Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-js-workflows/)

  Trace features and compare authenticated JavaScript application graphs while preserving static-analysis limits.

- [**Static Android APK analysis**](https://github.com/morluto/rea/blob/main/docs/android-analysis.md) · Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-android-guide/)

  Inspect Android package identity, classes, methods and references through REA's JADX integration.

- [**Managed-code analysis**](https://github.com/morluto/rea/blob/main/docs/managed-code-analysis.md) · Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-managed-guide/)

  Read PE/CLI metadata and CIL, compare managed members and inspect declared native boundaries without loading the assembly.

- [**Historical web network captures**](https://github.com/morluto/rea/blob/main/docs/web-network-captures.md) · Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-web-captures/)

  Inspect saved web captures offline; recorded URLs are not fetched and no proxy is started.

- [**Firmware analysis**](https://github.com/morluto/rea/blob/main/docs/firmware-analysis.md) · Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-firmware-guide/)

  Inspect firmware regions with Binwalk and explicitly extract with Unblob, retaining tool and artifact identity.

- [**Browser observation guide**](https://rea.tools/guides/browser/) · Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-browser-guide/)

  Follow a user-triggered export request in the supplied Notes browser example and connect it to the downloaded result.

- [**JavaScript and Electron: follow a CSV export**](https://rea.tools/guides/javascript/) · Documentation · REA · [Requirements & evidence](https://awesomerea.org/resources/rea-electron-guide/)

  A source-owned Notes fixture teaches the renderer, preload, IPC and CSV path with linked analysis evidence.

- [**rea-playbook**](https://github.com/jinshi666888/rea-playbook) · Learning resource · [Requirements & evidence](https://awesomerea.org/resources/rea-playbook/)

  An Electron practice target, Evidence extractor and MCP probe; offline fixture mode is distinguished from real REA analysis.

- [**rea-lab**](https://github.com/pablodiazjorge/rea-lab) · Research · [Requirements & evidence](https://awesomerea.org/resources/rea-lab/)

  A Windows REA/Ghidra lab with seeded challenges, published studies, upstream contributions and recorded limitations.

- [**OpenSecurityTraining2**](https://ost2.fyi/) · Learning resource · [Requirements & evidence](https://awesomerea.org/resources/ost2/)

  Free self-paced security courses with learning paths for reverse engineering, firmware and systems foundations.

- [**pwn.college: Reverse Engineering**](https://pwn.college/program-security/reverse-engineering/) · Learning resource · [Requirements & evidence](https://awesomerea.org/resources/pwn-college-re/)

  Hands-on reverse-engineering module covering functions, data access, static tools and dynamic tools with hosted exercises.

- [**Reverse Engineering for Beginners**](https://beginners.re/) · Learning resource · [Requirements & evidence](https://awesomerea.org/resources/re-for-beginners/)

  Dennis Yurichev's free book on understanding compiled programs and assembly, available in multiple languages.

- [**The Official Radare2 Book**](https://book.rada.re/) · Learning resource · [Requirements & evidence](https://awesomerea.org/resources/radare2-book/)

  Official practical reference for radare2 analysis, disassembly, scripting, debugging and related plugins.
<!-- END GENERATED CATALOG -->

<!-- BEGIN GENERATED PAPERS -->
<a id="papers"></a>
## Papers

A bibliography of **46 papers** on reverse-engineering agent evaluation, decompilation, protocol inference, firmware analysis, and website, game, and app reconstruction. Some papers also appear among curated resources; counts are not additive. Publication status and study scope are made explicit.

[Browse the paper directory](https://awesomerea.org/papers/) · [Complete bibliography JSON](data/papers.json) · [Suggest a paper](https://github.com/reacher-z/Awesome-REA/issues/new?template=paper.yml)

**By topic** · [Agent evaluation](#papers-agent-evaluation) (5) · [Decompilation](#papers-decompilation) (7) · [Websites](#papers-website-reconstruction) (13) · [Games](#papers-game-reconstruction) (6) · [Apps](#papers-app-reconstruction) (5) · [Firmware](#papers-firmware-analysis) (5) · [Protocols](#papers-protocol-analysis) (5)

Open “Scope and publication details” for each study’s full limitations. Papers are ordered newest first within each topic.

<a id="papers-agent-evaluation"></a>
### Reverse-engineering agent evaluation

[↑ Paper topics](#papers) · [Contents](#contents)

- [**Humans vs. Machines: A Comparison With AI Agents in Software Reverse Engineering**](https://arxiv.org/abs/2610.14960) · **2026 · Preprint**

  Compares human and LLM-agent understanding and navigation on the same static reverse-engineering challenges, then studies how binary representations consume context windows.

  [PDF](https://arxiv.org/pdf/2610.14960) · [Full entry & citation](https://awesomerea.org/papers/paper-humans-machines-sre/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Understanding is graded on two compact challenges; the separate 4,000-binary study measures context capacity, not task-solving accuracy. The interface is static IDA/MCP without dynamic execution, and prior exposure to challenge source remains an acknowledged validity threat.

  **Publication:** 2026 · arXiv · Preprint · Samuele Doria et al.

  </details>

- [**The Next Challenge for Agentic Cybersecurity: A Realistic, Contamination-Free Reverse Engineering Benchmark**](https://arxiv.org/abs/2608.11469) · **2026 · Preprint**

  Introduces SRE-Bench, with privately authored programs and protected binary variants, to study agent recovery of program semantics while reducing training-data contamination.

  [PDF](https://arxiv.org/pdf/2608.11469) · [Full entry & citation](https://awesomerea.org/papers/paper-sre-bench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The revised study reports 19 programs, 262 binary instances, and 1,572 graded tasks. Binaries and task instances are not publicly released; access is through an evaluation service. Its contamination-control claim is the authors' methodology, not an independent guarantee.

  **Publication:** 2026 · arXiv · Preprint · Jeremy Spence et al.

  </details>

- [**CrackMeBench: Binary Reverse Engineering for Agents**](https://arxiv.org/abs/2605.10597) · **2026 · Preprint**

  Evaluates agents on executable-checked CrackMe tasks: infer validation logic from binaries and submit an accepted input or artifact, while recording tool use, time, and scoring attempts.

  [PDF](https://arxiv.org/pdf/2605.10597) · [Full entry & citation](https://awesomerea.org/papers/paper-crackmebench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The v0 study uses 12 generated tasks and eight public calibration tasks, Linux x86-64 ELF binaries, a shell interface, and a five-minute budget. Its compact educational tasks do not establish performance on large applications. No paper-linked public artifact URL was verified.

  **Publication:** 2026 · arXiv · Preprint · Isaac David et al.

  </details>

- [**ProgramBench: Can Language Models Rebuild Programs From Scratch?**](https://arxiv.org/abs/2605.03546) · **2026 · Accepted**

  Evaluates black-box program reconstruction across 200 tasks: agents query an executable and read its documentation, then independently implement a codebase whose behavior is checked by generated tests.

  [PDF](https://arxiv.org/pdf/2605.03546v1) · [Code](https://github.com/facebookresearch/ProgramBench) · [Full entry & citation](https://awesomerea.org/papers/paper-programbench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Binary inspection, decompilation, and internet access are forbidden during inference. Passing finite tests does not prove complete behavioral equivalence or recovery of the original source. Later live-leaderboard runs are separate from the reviewed arXiv results.

  **Publication:** 2026 · NeurIPS 2026 · Accepted · John Yang et al.

  </details>

- [**CREBench: Evaluating Large Language Models in Cryptographic Binary Reverse Engineering**](https://openreview.net/forum?id=tLYdf8hWJB) · **2026 · Conference paper**

  Benchmarks cryptographic binary reverse engineering across algorithm recognition, key or IV extraction, wrapper reconstruction, and flag recovery using 432 controlled challenges.

  [PDF](https://arxiv.org/pdf/2604.03750v2) · [Code](https://github.com/wangyu-ovo/CREBench) · [Full entry & citation](https://awesomerea.org/papers/paper-crebench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The corpus combines 48 algorithms, three insecure key-use scenarios, and three difficulty levels. It excludes professional-grade obfuscators such as Tigress and O-LLVM; results should not be generalized to heavily protected arbitrary binaries.

  **Publication:** 2026 · COLM 2026 · Conference paper · Baicheng Chen et al.

  </details>

<a id="papers-decompilation"></a>
### Decompilation and symbol recovery

[↑ Paper topics](#papers) · [Contents](#contents)

- [**SK2Decompile: LLM-based Two-Phase Binary Decompilation from Skeleton to Skin**](https://proceedings.iclr.cc/paper_files/paper/2026/hash/9132583dd869acb0cafeb0ed25eb031a-Abstract-Conference.html) · **2026 · Conference paper**

  Splits LLM decompilation into two phases: a Structure Recovery model turns decompiler pseudocode into an identifier-free IR that keeps control flow and data structures, trained with compiler-based RL rewards, and an Identifier Naming model then restores names under a semantic-similarity reward. The authors report a 21.6% average re-executability gain over GPT-5-mini on HumanEval and a 29.4% average R2I improvement over Idioms on GitHub2025.

  [PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/9132583dd869acb0cafeb0ed25eb031a-Paper-Conference.pdf) · [Code](https://github.com/albertan017/LLM4Decompile/tree/85b364bf093eb2ee4f3687cfe38a203fca89f23e/sk2decompile) · [Full entry & citation](https://awesomerea.org/papers/paper-sk2decompile/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Training and main evaluation use function-level C compiled for x86-64 Linux with GCC and Clang at -O0 to -O3, with IDA Pro pseudocode as model input. Re-executability is measured only on HumanEval and MBPP; ExeBench and GitHub2025 use R2I readability and a GPT-5-mini judge. Appendix experiments extend to BringUpBench projects, macOS arm64 and Windows MSVC builds, and Obfuscator-LLVM, but the models are trained on C only and the paper expects them to degrade on features without C equivalents, such as C++ templates.

  **Publication:** 2026 · ICLR 2026 · Conference paper · Hanzhuo Tan et al.

  </details>

- [**DecompileBench: A Comprehensive Benchmark for Evaluating Decompilers in Real-World Scenarios**](https://aclanthology.org/2025.findings-acl.1194/) · **2025 · Conference paper**

  Evaluates traditional and LLM-based decompilers using functions from real programs, runtime behavioral checks, and an LLM-assisted assessment of analyst-facing code understandability.

  [PDF](https://aclanthology.org/2025.findings-acl.1194.pdf) · [Code](https://github.com/vul337/DecompileBench) · [Full entry & citation](https://awesomerea.org/papers/paper-decompilebench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The evaluated corpus has 23,400 functions from 130 programs. Fuzzing-based checks have finite coverage, and understandability scores depend partly on an LLM judge. The artifact warns that rebuilt OSS-Fuzz projects can differ from the paper's versions.

  **Publication:** 2025 · Findings of ACL 2025 · Conference paper · Zeyu Gao et al.

  </details>

- [**Decompile-Bench: Million-Scale Binary-Source Function Pairs for Real-World Binary Decompilation**](https://papers.nips.cc/paper_files/paper/2025/hash/079cf13ae174c31f148207d94d213bdc-Abstract-Datasets_and_Benchmarks_Track.html) · **2025 · Conference paper**

  Introduces two million C/C++ binary-source function pairs using a Compile-Trace-Filter pipeline, with an evaluation suite spanning translated HumanEval/MBPP tasks and recent GitHub functions.

  [PDF](https://papers.nips.cc/paper_files/paper/2025/file/079cf13ae174c31f148207d94d213bdc-Paper-Datasets_and_Benchmarks_Track.pdf) · [Code](https://github.com/albertan017/LLM4Decompile) · [Full entry & citation](https://awesomerea.org/papers/paper-decompile-bench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** This is function-level decompilation. Re-execution tests cover HumanEval/MBPP; GitHub2025 provides no unit tests. Inlining can prevent one-to-one source correspondence, and the fine-tuning study uses 10% of the corpus. These results do not establish whole-program recovery.

  **Publication:** 2025 · NeurIPS 2025 Datasets and Benchmarks · Conference paper · Hanzhuo Tan et al.

  </details>

- [**ReSym: Harnessing LLMs to Recover Variable and Data Structure Symbols from Stripped Binaries**](https://doi.org/10.1145/3658644.3670340) · **2024 · Conference paper**

  Combines two fine-tuned language models with Prolog-based cross-function reasoning to infer local-variable symbols and user-defined data structures from stripped-binary decompilation.

  [PDF](https://www.cs.purdue.edu/homes/lintan/publications/resym-ccs24.pdf) · [Code](https://github.com/lt-asset/resym) · [Full entry & citation](https://awesomerea.org/papers/paper-resym/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The method depends on underlying decompilation and learned predictions over C/C++ data. Cross-checking reduces conflicting predictions but does not prove that recovered names or layouts match the unavailable source. The public artifact includes models, processed data, and evaluation code.

  **Publication:** 2024 · ACM CCS 2024 · Conference paper · Danning Xie et al.

  </details>

- [**LLM4Decompile: Decompiling Binary Code with Large Language Models**](https://aclanthology.org/2024.emnlp-main.203/) · **2024 · Conference paper**

  Trains language models for assembly-to-C decompilation and for refining Ghidra pseudocode, evaluating whether recovered functions can be recompiled and executed correctly.

  [PDF](https://aclanthology.org/2024.emnlp-main.203.pdf) · [Code](https://github.com/albertan017/LLM4Decompile) · [Full entry & citation](https://awesomerea.org/papers/paper-llm4decompile/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The paper limits its experiments to C on x86 and function-level benchmarks. Re-executability on sampled tests does not establish whole-program equivalence or recovery of the original source. Later repository releases are separate from the 2024 paper.

  **Publication:** 2024 · EMNLP 2024 · Conference paper · Hanzhuo Tan et al.

  </details>

- [**Augmenting Decompiler Output with Learned Variable Names and Types**](https://www.usenix.org/conference/usenixsecurity22/presentation/chen-qibin) · **2022 · Conference paper**

  Introduces DIRTY, a Transformer model that recommends variable names and types from decompiled code and layout information, together with the DIRT corpus for training and evaluation.

  [PDF](https://arxiv.org/pdf/2108.06363) · [Code](https://github.com/CMUSTRUDEL/DIRTY) · [Full entry & citation](https://awesomerea.org/papers/paper-dirty/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The original pipeline is built around C programs and Hex-Rays output. Predicted names and types are learned hypotheses, not guaranteed original symbols. The published paper is from 2022, although its arXiv preprint first appeared in 2021.

  **Publication:** 2022 · USENIX Security 2022 · Conference paper · Qibin Chen et al.

  </details>

- [**DIRE: A Neural Approach to Decompiled Identifier Naming**](https://doi.org/10.1109/ASE.2019.00064) · **2019 · Conference paper**

  Combines lexical and structural information from decompiler output to predict meaningful variable names, with a training and evaluation corpus derived from compiled C projects.

  [PDF](https://arxiv.org/pdf/1909.09029) · [Code](https://github.com/pcyin/dire) · [Full entry & citation](https://awesomerea.org/papers/paper-dire/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** This is learned identifier naming, not complete source reconstruction or an autonomous agent. Its reported results concern an x86-64 C corpus and depend on decompiler output. The original author repository is deprecated and points to a successor.

  **Publication:** 2019 · ASE 2019 · Conference paper · Jeremy Lacomis et al.

  </details>

<a id="papers-website-reconstruction"></a>
### Website reconstruction

[↑ Paper topics](#papers) · [Contents](#contents)

- [**Vision2Web: A Hierarchical Benchmark for Visual Website Development with Agent Verification**](https://proceedings.mlr.press/v306/he26n.html) · **2026 · Conference paper**

  Benchmarks website development from visual prototypes and written requirements across 100 static-page, 66 interactive-frontend and 27 full-stack tasks, combining workflow-based functional checks with model-judged visual comparison.

  [PDF](https://raw.githubusercontent.com/mlresearch/v306/main/assets/he26n/he26n.pdf) · [Code](https://github.com/zai-org/Vision2Web) · [Full entry & citation](https://awesomerea.org/papers/paper-vision2web/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The full-stack tier is specification-driven, not reconstruction solely by exploring a live website. Workflows test state management and CRUD outcomes, but finite agent judgments do not establish exact backend or durable-database equivalence. The current public evaluator maintains a browser session within each workflow and permits local business-API checks; this is not a universal persistence proof.

  **Publication:** 2026 · ICML 2026 · Conference paper · Zehai He et al.

  </details>

- [**ProgramDistill: From Interactive Web Apps to Verifiable Reference-Guided SWE Tasks**](https://arxiv.org/abs/2609.18805) · **2026 · Preprint**

  Evaluates recovery of web-app behavior from a live reference with hidden source. It provides 4,063 feature-restoration tasks across 26 applications and a separate 12-application reconstruction setting, scored by replaying dependent browser workflows.

  [PDF](https://arxiv.org/pdf/2609.18805v1) · [Code](https://huggingface.co/datasets/microsoft/ProgramDistill) · [Full entry & citation](https://awesomerea.org/papers/paper-programdistill/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Tests cover finite, model-mined behaviors in self-contained apps, including SaaS clones. Persistence failures can be detected through replayed workflows, but passing does not establish all backend or database invariants. Evaluated agents receive structured browser observations without screenshots; visual fidelity is not measured. Public verifiers and reference solutions are not a contamination-resistant test set.

  **Publication:** 2026 · arXiv · Preprint · Jeonghye Kim et al.

  </details>

- [**UI2App: Benchmarking Visual Interaction Inference in Executable Web Application Generation**](https://arxiv.org/abs/2607.06306) · **2026 · Preprint**

  UI2App evaluates runnable React/TypeScript applications generated from 600 screenshots across 95 web applications. It separates build executability, visual fidelity and screenshot-implied interaction behavior, including cross-route state, using a reference interaction taxonomy and public evaluation pipeline.

  [PDF](https://arxiv.org/pdf/2607.06306v2) · [Code](https://github.com/chenmancm169/UI2App) · [Full entry & citation](https://awesomerea.org/papers/paper-ui2app/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Static screenshots underdetermine behavior; the rubric accepts multiple valid implementations rather than proving equivalence to the original application or backend. Auto IIS judges generated source and screenshots without tool execution; human runtime validation covers a 45-application subset. Cross-route state is not necessarily durable persistence across reloads or sessions. Main results use one generation per application-model pair, with repeated runs on a subset.

  **Publication:** 2026 · arXiv · Preprint · Grace Man Chen et al.

  </details>

- [**Dashboard2Code: Evaluating Multimodal Models on Reconstructing Interactive Dashboards**](https://aclanthology.org/2026.acl-long.1750/) · **2026 · Conference paper**

  Evaluates agents that actively explore a running dashboard and reconstruct its appearance and interaction logic. DashboardMimic provides 180 Plotly+Dash examples, with code-semantic analysis and dynamic interaction tests for the generated implementations.

  [PDF](https://aclanthology.org/2026.acl-long.1750.pdf) · [Code](https://github.com/nth2000/Dashboard2Code) · [Full entry & citation](https://awesomerea.org/papers/paper-dashboard2code/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Limited to Plotly+Dash dashboards, including model-augmented examples. Some settings expose DOM information and evaluation uses model judges. This is not a general backend-recovery benchmark. The linked dataset requires accepting access conditions and sharing contact information.

  **Publication:** 2026 · ACL 2026 · Conference paper · Tianhao Niu et al.

  </details>

- [**CASCADE: LLM-powered JavaScript Deobfuscator at Google**](https://doi.org/10.1145/3786583.3786873) · **2026 · Conference paper**

  Uses Gemini to locate the prelude functions that Obfuscator.IO inserts for string obfuscation, then applies constant-propagation and inlining passes in the JSIR compiler IR to restore string literals and API names deterministically.

  [PDF](https://arxiv.org/pdf/2507.17691v2) · [Code](https://github.com/google/jsir) · [Full entry & citation](https://awesomerea.org/papers/paper-cascade/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The method addresses Obfuscator.IO string obfuscation; control-flow flattening, other obfuscators and an agent-based design are future work. Evaluation obfuscates 3,000 programs from the ETH 150k JavaScript dataset with four Obfuscator.IO presets and measures prelude detection, recovered literals and run time, not functional equivalence. Production deployment and scan volume are author-reported, and production pre-filtering uses a proprietary YARA rule.

  **Publication:** 2026 · ICSE-SEIP 2026 · Conference paper · Shan Jiang et al.

  </details>

- [**ScreenCoder: Advancing Visual-to-Code Generation for Front-End Automation via Modular Multimodal Agents**](https://arxiv.org/abs/2507.22827) · **2026 · Accepted**

  Splits screenshot-to-code generation among grounding, planning and generation agents that label UI regions, build a hierarchical layout tree and write HTML/CSS. The pipeline also produces the Screen-10K training pairs used for supervised and reinforcement fine-tuning, and the paper introduces the 1,000-page ScreenBench.

  [PDF](https://arxiv.org/pdf/2507.22827v2) · [Code](https://github.com/leigest519/ScreenCoder) · [Full entry & citation](https://awesomerea.org/papers/paper-screencoder/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Output is static HTML/CSS layout; interaction, JavaScript behavior and backend logic are not reconstructed. Results are visual-similarity scores (CLIP and OCR-matched text blocks) on ScreenBench and Design2Code, which do not establish code-level or functional equivalence. The released pipeline calls a hosted model API, Doubao by default. The reviewed text is arXiv v2; the accepted EMNLP version may differ.

  **Publication:** 2026 · EMNLP 2026 · Accepted · Yilei Jiang et al.

  </details>

- [**IWR-Bench: Can LVLMs reconstruct interactive webpage from a user interaction video?**](https://proceedings.iclr.cc/paper_files/paper/2026/hash/55bfedfd31489e5ae83c9ce8eec7b0e1-Abstract-Conference.html) · **2026 · Conference paper**

  Tests reconstruction of interactive webpages from user-interaction videos and supplied static assets. Its 113 tasks replay annotated action sequences to assess visual fidelity and functional behavior across observed page states.

  [PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/55bfedfd31489e5ae83c9ce8eec7b0e1-Paper-Conference.pdf) · [Code](https://github.com/SIGMME/IWR-Bench) · [Full entry & citation](https://awesomerea.org/papers/paper-iwr-bench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The required output is one HTML file; the paper explicitly instructs models to mock implied backend logic with static JavaScript data. Trajectory coverage and model-based judgments do not prove complete website or backend equivalence.

  **Publication:** 2026 · ICLR 2026 · Conference paper · Yang Chen et al.

  </details>

- [**JsDeObsBench: Measuring and Benchmarking LLMs for JavaScript Deobfuscation**](https://doi.org/10.1145/3719027.3744871) · **2025 · Conference paper**

  Builds an execution-verifiable JavaScript deobfuscation benchmark by applying seven JavaScript-Obfuscator transformations to Project CodeNet programs with test cases, then scores LLM and tool outputs for syntax, execution, code simplification and similarity to the original code.

  [PDF](https://arxiv.org/pdf/2506.20170v1) · [Code](https://github.com/Ch3nYe/JsDeObsBench) · [Full entry & citation](https://awesomerea.org/papers/paper-jsdeobsbench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** On average, LLM outputs passed execution checks 60.93% of the time, against 83% for the two existing deobfuscator baselines. All samples come from a single obfuscator applied to moderate-length competitive-programming solutions. The 4,515 obfuscated malware samples have no test cases and are compared only through behavior traces.

  **Publication:** 2025 · ACM CCS 2025 · Conference paper · Guoqiang Chen et al.

  </details>

- [**Interaction2Code: Benchmarking MLLM-based Interactive Webpage Code Generation from Interactive Prototyping**](https://doi.org/10.1109/ASE63991.2025.00028) · **2025 · Conference paper**

  Benchmarks reconstruction of interactive webpages from screenshots before and after an interaction. The final study covers 127 webpages and 374 interactions, comparing rendered appearance, automated interaction checks, and human usability judgments.

  [PDF](https://arxiv.org/pdf/2411.03292v3) · [Code](https://github.com/WebPAI/Interaction2Code) · [Full entry & citation](https://awesomerea.org/papers/paper-interaction2code/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The inputs specify individual interaction transitions, not autonomous exploration of a complete site. Its tests do not establish long-workflow, server-side, or original-source equivalence; a detectable interaction is not necessarily usable.

  **Publication:** 2025 · ASE 2025 · Conference paper · Jingyu Xiao et al.

  </details>

- [**WebUIBench: A Comprehensive Benchmark for Evaluating Multimodal Large Language Models in WebUI-to-Code**](https://aclanthology.org/2025.findings-acl.815/) · **2025 · Conference paper**

  Diagnoses webpage-to-code capability through visual perception, HTML programming, image-to-HTML understanding, and screenshot reconstruction tasks. It separates underlying skills using question-answer pairs derived from real websites.

  [PDF](https://aclanthology.org/2025.findings-acl.815.pdf) · [Full entry & citation](https://awesomerea.org/papers/paper-webuibench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Primarily evaluates visual and HTML reconstruction skills. The paper includes a preliminary interaction study, not a full workflow or backend-equivalence benchmark. The official repository currently exposes README and images but not the evaluation scripts described in its instructions.

  **Publication:** 2025 · Findings of ACL 2025 · Conference paper · Zhiyu Lin et al.

  </details>

- [**Divide-and-Conquer: Generating UI Code from Screenshots**](https://doi.org/10.1145/3729364) · **2025 · Journal article**

  Recursively divides a webpage screenshot along visual separation lines, has a multimodal model generate HTML/CSS for each leaf segment, and assembles child code upward into the full page; evaluated with GPT-4o, Gemini and Claude models and a small developer study.

  [PDF](https://arxiv.org/pdf/2406.16386v3) · [Code](https://github.com/WebPAI/DCGen) · [Full entry & citation](https://awesomerea.org/papers/paper-dcgen/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** It reconstructs static visual layout as HTML/CSS, not interaction, JavaScript behavior or backend logic. Test pages are self-contained snapshots with images replaced by placeholders; the main evaluation samples 111 of 348 top-ranked sites, adds 80 harder GitHub Pages pages, and the usefulness study has four participants. Segmentation uses manually set thresholds, and assembly can still misarrange elements.

  **Publication:** 2025 · Proceedings of the ACM on Software Engineering · Journal article · Yuxuan Wan et al.

  </details>

- [**Design2Code: Benchmarking Multimodal Code Generation for Automated Front-End Engineering**](https://aclanthology.org/2025.naacl-long.199/) · **2025 · Conference paper**

  Evaluates reconstruction of frontend code from webpage screenshots using real-world reference pages, visual-element and layout metrics, and human assessment.

  [PDF](https://aclanthology.org/2025.naacl-long.199.pdf) · [Code](https://github.com/NoviScl/Design2Code) · [Full entry & citation](https://awesomerea.org/papers/paper-design2code/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** This is visual website reconstruction, not binary decompilation or recovery of backend behavior and interactive workflows. The main benchmark contains 484 webpages with placeholder images; code and data have separate licensing terms.

  **Publication:** 2025 · NAACL 2025 · Conference paper · Chenglei Si et al.

  </details>

- [**Web2Code: A Large-scale Webpage-to-Code Dataset and Evaluation Framework for Multimodal LLMs**](https://proceedings.nips.cc/paper_files/paper/2024/hash/cb66be286795d71f89367d596bf78ea7-Abstract-Datasets_and_Benchmarks_Track.html) · **2024 · Conference paper**

  Studies screenshot-to-HTML reconstruction through instruction tuning and two evaluation benchmarks. Web2Code combines generated webpages, refined WebSight and pix2code image/code pairs, and WebSRC-derived question answering. Models produce HTML from a webpage image and instruction; rendered output is compared visually, while a separate benchmark measures screenshot understanding.

  [PDF](https://proceedings.neurips.cc/paper_files/paper/2024/file/cb66be286795d71f89367d596bf78ea7-Paper-Datasets_and_Benchmarks_Track.pdf) · [Code](https://github.com/MBZUAI-LLM/web2code) · [Full entry & citation](https://awesomerea.org/papers/paper-web2code/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Evaluation uses 1,198 screenshots and 5,990 yes/no questions. WCGB grades rendered images with GPT-4V; its User Interface and Interactivity category measures element appearance, not executed click paths, persistent state or backend behavior. Synthetic and refined examples do not establish coverage of arbitrary real web applications, original-source equivalence or code quality. The paper reports contact-information issues in 2.7% of a 1,000-item privacy sample, so a blanket claim that the data is free of such information is unsupported.

  **Publication:** 2024 · NeurIPS 2024 Datasets and Benchmarks · Conference paper · Sukmin Yun et al.

  </details>

<a id="papers-game-reconstruction"></a>
### Game reconstruction and reverse engineering

[↑ Paper topics](#papers) · [Contents](#contents)

- [**GameReplica: A Benchmark for Black-Box Visual Game Replication by Vision-Language Agents**](https://arxiv.org/abs/2609.22308) · **2026 · Preprint**

  Evaluates whether vision-language agents can infer hidden game rules through screenshots and active interaction, then build runnable single-file HTML replicas across 125 tasks from 25 web games, each with five difficulty levels.

  [PDF](https://arxiv.org/pdf/2609.22308v1) · [Full entry & citation](https://awesomerea.org/papers/paper-gamereplica/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The tasks cover rule-driven web puzzles and board games, not native or commercial game reconstruction. Rule, implementation, and visual scores use LLM judges and do not prove behavioral equivalence. The official site provides demos; a benchmark-code repository was not verified.

  **Publication:** 2026 · arXiv · Preprint · Boyu Qiao et al.

  </details>

- [**Tycho: Active Abstraction with Programmatic World Models for ARC-AGI-3**](https://arxiv.org/abs/2607.28287) · **2026 · Preprint**

  Tycho constructs editable Python models of game state, transitions, rendering and outcomes from action/observation histories in unfamiliar ARC-AGI-3 games. It checks model predictions against recorded transitions and can use, repair or bypass these models during planning.

  [PDF](https://arxiv.org/pdf/2607.28287v1) · [Code](https://github.com/NIMI-research/Tycho) · [Full entry & citation](https://awesomerea.org/papers/paper-tycho/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Evaluation uses one stochastic run per configuration on 25 public games and 183 levels; five games informed harness development. Models may abstain on cells or accept bounded rendering variants. Transition replay and game scores do not establish complete engine reconstruction, correct objectives, unseen-state fidelity, unseen-game generalization or run-to-run reliability; the agent can bypass modeling.

  **Publication:** 2026 · arXiv · Preprint · Jens Lehmann et al.

  </details>

- [**RevengeBench: Reverse Engineering Code-Space Policies from Behavioral Experiments**](https://arxiv.org/abs/2606.26094) · **2026 · Preprint**

  Tests whether agents can recover executable decision policies from behavioral traces and self-designed opponent probes, using 75 synthetic policies across five game arenas and measuring held-out action agreement and downstream competitive value.

  [PDF](https://arxiv.org/pdf/2606.26094v1) · [Code](https://github.com/bethgelab/revenge-bench) · [Full entry & citation](https://awesomerea.org/papers/paper-revengebench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The targets are fixed synthetic policies, not full games or adaptive adversaries. Agreement on finitely evaluated states does not uniquely identify source code, and some arenas have substantial variance. The public package omits some paper-only plotting and ablation suites; reproduction also needs CodeClash, a container runtime, and model access.

  **Publication:** 2026 · arXiv · Preprint · Babak Rahmani et al.

  </details>

- [**SPRITE: From Static Mockups to Engine-Ready Game UI**](https://doi.org/10.1145/3772363.3798742) · **2026 · Conference paper**

  Transforms game-interface screenshots into editable engine assets through hierarchical YAML, visual grounding, asset extraction, and Unity UXML/USS synthesis, with evaluation on a curated game-UI benchmark and review by three senior UI/UX designers.

  [PDF](https://baiyunshu.github.io/sprite.github.io/Source/chiea26-516.pdf) · [Full entry & citation](https://awesomerea.org/papers/paper-sprite-game-ui/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The generated interactions cover basic hover, toggle, and click behavior. Complex temporal and drag-and-drop logic remain outside scope, and translucent overlap or ambiguous diegetic layouts can fail. This is game-UI prototyping, not complete gameplay reconstruction; the official page still labels code as coming soon.

  **Publication:** 2026 · CHI EA 2026 (poster/extended abstract) · Conference paper · Yunshu Bai et al.

  </details>

- [**WorldCoder, a Model-Based LLM Agent: Building World Models by Writing Code and Interacting with the Environment**](https://papers.nips.cc/paper_files/paper/2024/hash/820c61a0cd419163ccbd2c33b268816e-Abstract-Conference.html) · **2024 · Conference paper**

  WorldCoder learns executable Python transition and reward models from environment interactions and natural-language goals. It refines code against recorded experiences and an optimistic planning constraint, studying transfer and task solving in Sokoban, MiniGrid and ALFWorld.

  [PDF](https://papers.neurips.cc/paper_files/paper/2024/file/820c61a0cd419163ccbd2c33b268816e-Paper-Conference.pdf) · [Code](https://github.com/haotang1995/WorldCoder) · [Full entry & citation](https://awesomerea.org/papers/paper-worldcoder/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Assumes deterministic dynamics and symbolic, discrete states rather than recovering a game from arbitrary pixels or binaries. Consistency with observed transitions and successful planning do not establish complete engine equivalence or correctness on every unseen state. Evaluation concerns bounded environment models and planning, not original source or asset recovery.

  **Publication:** 2024 · NeurIPS 2024 · Conference paper · Hao Tang et al.

  </details>

- [**Generating Code World Models with Large Language Models Guided by Monte Carlo Tree Search**](https://proceedings.neurips.cc/paper_files/paper/2024/hash/6f479ea488e0908ac8b1b37b27fd134c-Abstract-Conference.html) · **2024 · Conference paper**

  GIF-MCTS generates executable Python transition and reward models from natural-language environment descriptions and offline state-transition trajectories, using prediction feedback to generate, improve and repair code. CWMB evaluates 18 reinforcement-learning environments and downstream planning; a separate experiment uses a simplified Read to Fight Monsters grid world.

  [PDF](https://proceedings.neurips.cc/paper_files/paper/2024/file/6f479ea488e0908ac8b1b37b27fd134c-Paper-Conference.pdf) · [Code](https://github.com/nicoladainese96/code-world-models) · [Full entry & citation](https://awesomerea.org/papers/paper-code-world-models/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Assumes deterministic, fully observable dynamics and sufficiently detailed descriptions; this is not recovery from pixels or binaries alone. Accuracy uses the replay transitions supplied during synthesis, alongside planning-return evaluation, rather than proving correctness on all unseen states or full-engine equivalence. RTFM fixes the manual across episodes and keeps monsters stationary. CWMB also includes non-game control and physics tasks; some planning returns are unavailable and complex continuous-state models remain difficult.

  **Publication:** 2024 · NeurIPS 2024 · Conference paper · Nicola Dainese et al.

  </details>

<a id="papers-app-reconstruction"></a>
### App reconstruction and analysis

[↑ Paper topics](#papers) · [Contents](#contents)

- [**DeclarUI: Bridging Design and Development with Automated Declarative UI Code Generation**](https://doi.org/10.1145/3715726) · **2025 · Journal article**

  Combines visual component extraction, multimodal models, page-transition graphs and iterative checks to reconstruct multi-page mobile UI code from designs or screenshots, evaluated with React Native, Flutter and ArkUI.

  [PDF](https://xinyi-hou.github.io/files/zhou2024bridging.pdf) · [Code](https://github.com/security-pride/DeclarUI) · [Full entry & citation](https://awesomerea.org/papers/paper-declarui/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** People review and correct the inferred navigation graph. Evaluation covers 50 five-page UI sets; transition coverage and compilation do not establish full business-logic or backend recovery. Framework results vary, and visual metrics imperfectly reflect perceived fidelity. Public scripts and data are available, but no project-level license was found at the reviewed commit.

  **Publication:** 2025 · Proceedings of the ACM on Software Engineering · Journal article · Ting Zhou et al.

  </details>

- [**Machine Learning-Based Prototyping of Graphical User Interfaces for Mobile Apps**](https://doi.org/10.1109/TSE.2018.2844788) · **2020 · Journal article**

  ReDraw turns screenshots or design mock-ups into native Android GUI prototypes by detecting components, classifying widget types with a CNN, and assembling a plausible view hierarchy with a data-driven nearest-neighbor method.

  [PDF](https://arxiv.org/pdf/1802.02312v2) · [Full entry & citation](https://awesomerea.org/papers/paper-redraw/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The implementation covers 15 Android component classes and one screen at a time; multiple screens require manual combination, and hierarchy construction is tied to the mined screen size. Evaluation concerns appearance and view hierarchy, not recovery of original app logic or backends. Screenshots and reconstructed mock-ups served as proxies for real design artifacts; results were not independently reproduced here.

  **Publication:** 2020 · IEEE Transactions on Software Engineering · Journal article · Kevin Moran et al.

  </details>

- [**pix2code: Generating Code from a Graphical User Interface Screenshot**](https://doi.org/10.1145/3220134.3220135) · **2018 · Conference paper**

  Learns screenshot-to-DSL generation for native Android XML, iOS Storyboards and web HTML/CSS interfaces, then compiles the DSL into platform UI code.

  [PDF](https://arxiv.org/pdf/1705.07962v2) · [Code](https://github.com/tonybeltramelli/pix2code) · [Full entry & citation](https://awesomerea.org/papers/paper-pix2code/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Evaluation uses synthetic screenshot/code pairs: 1,500 training and 250 test instances per platform. Reported accuracy concerns DSL tokens, not complete apps or behavior. Text labels are ignored; platform datasets train separate models using the same architecture. The task covers layout, components and relationships, not application logic or backend recovery. The repository describes an educational research prototype; its older dependencies were not runtime-tested.

  **Publication:** 2018 · EICS 2018 · Conference paper · Tony Beltramelli

  </details>

- [**From UI Design Image to GUI Skeleton: A Neural Machine Translator to Bootstrap Mobile GUI Implementation**](https://doi.org/10.1145/3180155.3180240) · **2018 · Conference paper**

  UI2code translates a mobile UI image into an Android component hierarchy and layout skeleton using a neural encoder-decoder. The paper evaluates structural prediction and a small developer study of implementing layouts from generated skeletons.

  [PDF](https://chunyang-chen.github.io/publication/ui2code.pdf) · [Code](https://github.com/ccywch/UI2code) · [Full entry & citation](https://awesomerea.org/papers/paper-ui2code/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The output covers component types and hierarchy from a single image; detailed styling and text require developer work. Structural token accuracy and an eight-participant study on five screenshots do not establish complete visual fidelity, navigation, app logic or backend recovery. The main split is screenshot-based; a separate evaluation on 1,208 images from 20 unseen apps provides limited generalization evidence.

  **Publication:** 2018 · ICSE 2018 · Conference paper · Chunyang Chen et al.

  </details>

- [**Reverse Engineering Mobile Application User Interfaces with REMAUI (T)**](https://ieeexplore.ieee.org/abstract/document/7372013) · **2015 · Conference paper**

  Reconstructs native Android UI code from screenshots or design bitmaps using OCR, computer vision, and layout heuristics; evaluates visual similarity and view hierarchies on 488 screenshots from over 100 Android and iOS applications.

  [PDF](https://c.csallner.org/papers/nguyen15reverse.pdf) · [Code](https://github.com/soumikmohianuta/pixtoapp) · [Full entry & citation](https://awesomerea.org/papers/paper-remaui/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The output is Android UI code; iOS screenshots are inputs, not evidence of native iOS output. Original logic and backend behavior are not recovered, and multi-screen transitions were future work. OCR/layout heuristics can misidentify content. The linked REMAUI v2 repository has older dependencies and is not the exact verified 2015 artifact.

  **Publication:** 2015 · ASE 2015 · Conference paper · Tuan Anh Nguyen et al.

  </details>

<a id="papers-firmware-analysis"></a>
### Firmware analysis and rehosting

[↑ Paper topics](#papers) · [Contents](#contents)

- [**User-Space Dependency-Aware Rehosting for Linux-Based Firmware Binaries**](https://www.ndss-symposium.org/ndss-paper/user-space-dependency-aware-rehosting-for-linux-based-firmware-binaries/) · **2026 · Conference paper**

  FIRMWELL reconstructs the execution environment of Linux firmware services by running their initialization processes, locating blocking dependencies and repairing missing system-level behavior. It combines containerized QEMU-user emulation with a QEMU-system fallback, using process traces and binary analysis to recover resources needed by the target service.

  [PDF](https://www.ndss-symposium.org/wp-content/uploads/2026-s249-paper.pdf) · [Code](https://github.com/qc9c/Firmwell) · [Full entry & citation](https://awesomerea.org/papers/paper-firmwell/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The evaluation concerns selected network services, not complete device or hardware equivalence. HTTP acceptance uses configured response-status and error-content checks; other services need their own criteria. Coverage depends on unpacking, supported architectures, initialization heuristics and peripheral models. Symbolic path explosion, solver timeouts and complex peripheral checks remain failure modes. The paper’s recovery strategy avoids patching target binaries; successful service interaction does not establish recovery of original source code or every device function.

  **Publication:** 2026 · NDSS 2026 · Conference paper · Chuan Qin et al.

  </details>

- [**Target-Centric Firmware Rehosting with Penguin**](https://www.ndss-symposium.org/ndss-paper/auto-draft-634/) · **2025 · Conference paper**

  Penguin rehosts embedded Linux firmware from an extracted filesystem by deriving an editable configuration of emulation transformations, such as file changes, pseudofiles, NVRAM values and network interfaces, from static analysis. Dynamic-analysis plugins expose failures so the configuration can be refined for each target, and a minimizer identifies which transformations a working rehosting needs.

  [PDF](https://www.ndss-symposium.org/wp-content/uploads/bar2025-final10.pdf) · [Code](https://github.com/rehosting/penguin) · [Full entry & citation](https://awesomerea.org/papers/paper-penguin/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Targets embedded Linux firmware through whole-system emulation with kernel replacement, as in Firmadyne and FirmAE; the implementation covers x86, ARM and MIPS and relies on the Linux syscall ABI. In the FirmAE comparison, success means a process binds port 80 or 443; a non-empty HTTP response is a stricter check, and the authors note neither shows full functionality. The 75% gain over FirmAE is author-reported on their own corpus of 13,649 images from vendor websites. Refinement still needs an analyst, and nondeterministic runs were repeated up to ten times. It builds an analysis environment, not a faithful device reproduction or source recovery.

  **Publication:** 2025 · Workshop on Binary Analysis Research (BAR) 2025 · Conference paper · Andrew Fasano et al.

  </details>

- [**Fuzzware: Using Precise MMIO Modeling for Effective Firmware Fuzzing**](https://www.usenix.org/conference/usenixsecurity22/presentation/scharnowski) · **2022 · Conference paper**

  Rehosts monolithic ARM Cortex-M firmware for fuzzing, using locally scoped symbolic execution to model memory-mapped I/O accesses and focus input mutations on values relevant to firmware logic.

  [PDF](https://www.usenix.org/system/files/sec22-scharnowski.pdf) · [Code](https://github.com/fuzzware-fuzzer/fuzzware) · [Full entry & citation](https://awesomerea.org/papers/paper-fuzzware/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The Cortex-M3/M4 artifact requires memory-map configuration and does not automatically model DMA. Abstracting hardware can produce crashes that are impossible on the physical device. This is an analysis environment, not original-source recovery or faithful full-device reconstruction.

  **Publication:** 2022 · USENIX Security 2022 · Conference paper · Tobias Scharnowski et al.

  </details>

- [**FirmAE: Towards Large-Scale Emulation of IoT Firmware for Dynamic Analysis**](https://doi.org/10.1145/3427228.3427294) · **2020 · Conference paper**

  Extends Firmadyne with empirically derived interventions for boot, networking, NVRAM, kernel behavior, and other runtime failures, enabling Linux router and IP-camera firmware web services to run for dynamic analysis.

  [PDF](https://syssec.kaist.ac.kr/pub/2020/kim_acsac2020.pdf) · [Code](https://github.com/pr0v3rbs/FirmAE) · [Full entry & citation](https://awesomerea.org/papers/paper-firmae/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Arbitration deliberately changes execution and targets functioning web interfaces, not identical physical-device behavior. The evaluation covers ARM little-endian and MIPS little-/big-endian firmware from routers and IP cameras; heuristics may fail on unseen devices or configurations. It reuses firmware binaries rather than recovering their source.

  **Publication:** 2020 · ACSAC 2020 · Conference paper · Mingeun Kim et al.

  </details>

- [**HALucinator: Firmware Re-hosting Through Abstraction Layer Emulation**](https://www.usenix.org/conference/usenixsecurity20/presentation/clements) · **2020 · Conference paper**

  HALucinator rehosts monolithic ARM Cortex-M firmware by identifying hardware-abstraction-library functions and replacing them with authored Python handlers and peripheral models. LibMatch locates library interfaces; the QEMU/Avatar2 implementation supports interactive I/O, while the paper-associated HAL-fuzz variant uses AFL-Unicorn for fuzzing.

  [PDF](https://www.usenix.org/system/files/sec20-clements.pdf) · [Code](https://github.com/embedded-sec/halucinator) · [Full entry & citation](https://awesomerea.org/papers/paper-halucinator/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** LibMatch requires an available HAL/library and a sufficiently similar compilation environment; compiler variation and inlining limit matching. Rehosting also needs a QEMU-supported architecture, firmware memory layout, interception addresses and authored handlers/models. Unmodeled direct hardware accesses may return zero or ignore writes, and simplified timing and peripheral behavior do not establish hardware equivalence. The authors’ rehosting and fuzzing demonstrations are not universal firmware coverage, complete device reconstruction or original-source recovery.

  **Publication:** 2020 · USENIX Security 2020 · Conference paper · Abraham A Clements et al.

  </details>

<a id="papers-protocol-analysis"></a>
### Protocol inference and analysis

[↑ Paper topics](#papers) · [Contents](#contents)

- [**The Closer You Look, The More You Learn: A Grey-box Approach to Protocol State Machine Learning**](https://doi.org/10.1145/3548606.3559365) · **2022 · Conference paper**

  StateInspector learns protocol Mealy machines by combining active message queries with snapshots of runtime memory, without requiring the target’s source code. It identifies candidate state-defining heap locations and uses taint and concolic analysis to merge states, evaluated by the authors on TLS 1.2 and WPA/2 implementations.

  [PDF](https://tomchothia.gitlab.io/Papers/greyboxstatelearning_ccs2022.pdf) · [Code](https://github.com/ChrisMcMStone/state-inspector) · [Full entry & citation](https://awesomerea.org/papers/paper-stateinspector/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Assumes a finite Mealy-machine abstraction, a known input alphabet that can reach the relevant states, and state-defining memory on the heap exercised by bootstrap queries. State merging depends on configured search-depth and symbolic look-ahead bounds. Missing inputs or state stored elsewhere can leave behavior unmodeled; malformed harness messages, response abstraction and timeouts can create misleading transitions. Learned models and bounded checks do not establish full implementation equivalence, recover unknown message formats or reconstruct an application’s source code.

  **Publication:** 2022 · ACM CCS 2022 · Conference paper · Chris McMahon Stone et al.

  </details>

- [**Fingerprinting and analysis of Bluetooth devices with automata learning**](https://doi.org/10.1007/s10703-023-00425-y) · **2022 · Journal article**

  Learns Mealy-machine models of Bluetooth Low Energy implementations on physical peripherals by active automata learning. An nRF52840 central running SweynTooth-derived firmware sends abstract BLE inputs, with error handling, repeated queries and caching for lost packets and non-deterministic replies. The authors learn connection-procedure models of six devices and legacy-pairing models of three, and use model differences to fingerprint their SoCs.

  [PDF](https://arxiv.org/pdf/2211.16074v2) · [Code](https://github.com/apferscher/ble-learning) · [Full entry & citation](https://awesomerea.org/papers/paper-ble-automata-learning/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Models are bounded by the chosen abstract alphabet and cover only connection and legacy pairing; message formats are not inferred, and secure pairing is left to future work. Equivalence was approximated with a small number of conformance tests per state, so models are hypotheses, not proofs. One SoC was learnable only with reduced alphabets, two were learned from an already-connected state, and some pairing runs needed manual hard resets. The fingerprinting sequence holds only for the tested SoCs. Apart from one crashing input sequence, the authors report no security vulnerabilities in the learned models.

  **Publication:** 2022 · Formal Methods in System Design · Journal article · Andrea Pferscher et al.

  </details>

- [**NetPlier: Probabilistic Network Protocol Reverse Engineering from Message Traces**](https://www.ndss-symposium.org/ndss-paper/netplier-probabilistic-network-protocol-reverse-engineering-from-message-traces/) · **2021 · Conference paper**

  Uses multiple sequence alignment and probabilistic keyword-field inference to cluster network messages by type, evaluated across ten protocols with downstream format and state-machine analysis.

  [PDF](https://www.ndss-symposium.org/wp-content/uploads/ndss2021_4A-5_24531_paper.pdf) · [Code](https://github.com/yapengye/NetPlier) · [Full entry & citation](https://awesomerea.org/papers/paper-netplier/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Requires unencrypted traces and cannot recover unseen message types. Larger alignments, sub-byte keywords and one-way traffic can reduce accuracy. Format/FSM inference is downstream evaluation rather than the main contribution; state semantics in a case study were manually annotated. These models do not establish complete application/device reconstruction.

  **Publication:** 2021 · NDSS 2021 · Conference paper · Yapeng Ye et al.

  </details>

- [**Automatic Wireless Protocol Reverse Engineering**](https://www.usenix.org/conference/woot19/presentation/pohl) · **2019 · Conference paper**

  Infers message formats of proprietary wireless protocols from demodulated physical-layer captures: it aligns messages by preamble and sync word, then uses RSSI and dedicated engines to label length, address, sequence-number and checksum fields, optionally using known addresses or field positions.

  [PDF](https://www.usenix.org/system/files/woot19-paper_pohl.pdf) · [Code](https://github.com/jopohl/urh) · [Full entry & citation](https://awesomerea.org/papers/paper-wireless-protocol-re/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Only message formats are inferred: preamble, sync, length, address, sequence number and checksum. State-machine inference and payload fields, such as an on/off bit, are out of scope. The method assumes length-efficient binary messages with one preamble and sync word each. Accuracy is measured on 8 generated protocols; 3 real smart-home captures (EnOcean, Homematic BidCoS and an eQ-3 protocol used by RWE Smarthome) serve for performance tests, which the authors call a limited test set.

  **Publication:** 2019 · 13th USENIX Workshop on Offensive Technologies (WOOT 19) · Conference paper · Johannes Pohl et al.

  </details>

- [**NEMESYS: Network Message Syntax Reverse Engineering by Analysis of the Intrinsic Structure of Individual Messages**](https://www.usenix.org/conference/woot18/presentation/kleber) · **2018 · Conference paper**

  Infers approximate field boundaries within individual binary-protocol messages from changes in bit congruence, and introduces Format Match Score to compare inferred segmentation with known protocol dissectors.

  [PDF](https://www.usenix.org/system/files/conference/woot18/woot18-paper-kleber.pdf) · [Code](https://github.com/vs-uulm/nemesys) · [Full entry & citation](https://awesomerea.org/papers/paper-nemesys/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Requires plaintext payloads. Evaluation covers DNS, DHCP and NTP with protocol-tuned parameters. Single-byte fields are not inferred; zero-filled fields, character sequences and pseudo-random values can cause errors. FMS needs known field boundaries for validation. The output is approximate segmentation, not field semantics, a state machine or complete application/device behavior.

  **Publication:** 2018 · 12th USENIX Workshop on Offensive Technologies (WOOT 18) · Conference paper · Stephan Kleber et al.

  </details>
<!-- END GENERATED PAPERS -->

<a id="search-the-catalog"></a>
## Full Repository Index

<!-- BEGIN REPOSITORY INDEX SUMMARY -->
**3,000** repository READMEs scanned; **2,839** entries available to browse. The 161 clearly out-of-scope entries remain in the scan data. This automatically discovered index is separate from the curated resources above and has not been individually execution-tested.

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
