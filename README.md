# Awesome Reverse Engineering Anything

Tools, reconstruction cases and research for understanding websites, games, apps, native binaries, firmware and communication protocols.

<a href="https://awesomerea.org/"><img src="assets/readme-banner.svg" alt="Awesome Reverse Engineering Anything — tools, cases and papers across six reverse-engineering domains" width="960"></a>

**[Explore the collection ↗](https://awesomerea.org/) · [Curated directory](https://awesomerea.org/resources/) · [Research papers](https://awesomerea.org/papers/) · [简体中文](README.zh-CN.md)**

An independent, source-reviewed collection. Review does not imply runtime verification. [Evidence, requirements and review method](https://awesomerea.org/about/).

[REA (Reverse Engineer Anything)](https://github.com/morluto/rea) is a separate upstream CLI and MCP project. This collection's name echoes it, but it is not the REA repository; “REA” in entry tags and labels such as “Official REA documentation” refers to that project.

## Contents

<!-- BEGIN GENERATED CONTENTS -->
- **Targets** · [Website](#website) <sub>14</sub> · [Game](#game) <sub>37</sub> · [App](#app) <sub>30</sub> · [Native Binary](#native-binary) <sub>20</sub> · [Firmware & Hardware](#firmware) <sub>12</sub> · [Protocol](#protocol) <sub>11</sub>

- [Papers](#papers) <sub>33</sub> · [Cases](https://awesomerea.org/?view=curated&kind=case-study) <sub>37</sub> · [Agents & MCP](#agents-and-mcp) <sub>18</sub> · [Collections](#related-collections) <sub>4</sub> · [Learning](#references-and-learning) <sub>17</sub> · [Repository index](#full-repository-index) <sub>2,846</sub>
<!-- END GENERATED CONTENTS -->

<a id="resource-catalog"></a>
## Resources

Browse by purpose, with case studies separated from tools and integrations. Each resource appears once, with its type at the end; research has its own [paper topics](#papers). Independent projects and [REA](https://github.com/morluto/rea) resources are included; listing does not imply REA integration.

<!-- BEGIN GENERATED CATALOG -->
<a id="website"></a>
### Website

[↑ Contents](#contents)

#### Case studies

- [**Dinosaur runner: recovering one acceleration rule**](https://github.com/morluto/rea/blob/c360cfcd6d7901514b16dd6113eba2e0b0fdf422/website/evidence/calculator-and-dino.md#dinosaur-speed) - REA’s documented teaching case inspects the HTTP t-rex-runner edition and reconstructs its speed-update rule. A separate controlled original-game check and a new demonstration compare update counts, including the floating-point step that crosses the nominal speed threshold. <sub>Case study · REA</sub>

#### Tools, projects and integrations

- [**webcrack**](https://github.com/j4k0xb/webcrack) - Improves JavaScript readability by reversing supported obfuscation patterns and unpacking webpack/Browserify bundles. <sub>Tool</sub>
- [**humanify**](https://github.com/jehna/humanify) - Rename identifiers in minified JavaScript with LLM-suggested names, applied through scope-aware AST rewriting so the program structure stays unchanged. The new names are model suggestions, not recovered original identifiers. <sub>Tool</sub>
- [**WABT**](https://github.com/WebAssembly/wabt) - WebAssembly tools for binary-to-text conversion, section inspection, validation, interpretation and C translation. <sub>Tool · WebAssembly</sub>
- [**wasm-tools**](https://github.com/bytecodealliance/wasm-tools) - Bytecode Alliance CLI and Rust libraries for inspecting WebAssembly modules, metadata, components and WIT interfaces. <sub>Tool · WebAssembly</sub>
- [**Chrome DevTools MCP**](https://github.com/ChromeDevTools/chrome-devtools-mcp) - Connect an agent to Chrome for live page inspection, network debugging, and performance traces. <sub>Integration · Independent MCP</sub>
- [**mitmproxy**](https://github.com/mitmproxy/mitmproxy) - Inspect and record HTTP traffic with an interactive proxy, web interface, or scriptable command-line tools. <sub>Tool</sub>
- [**Playwright MCP**](https://github.com/microsoft/playwright-mcp) - Drive browser interactions through structured accessibility snapshots to investigate reproducible web behavior. <sub>Integration · Independent MCP</sub>
- [**Burp Suite MCP Server**](https://github.com/PortSwigger/mcp-server) - PortSwigger's Burp Suite extension serves an MCP endpoint, plus a packaged stdio proxy, so agents can query proxy HTTP and WebSocket history, send HTTP/1.1 or HTTP/2 requests, and open Repeater or Intruder tabs. <sub>Integration · Independent MCP</sub>
- [**Wakaru**](https://github.com/pionxzh/wakaru) - Recover readable modules from shipped JavaScript bundles by reversing recognized minifier and transpiler patterns. Supports bundle splitting and modern-syntax recovery for inspecting production frontend code. <sub>Tool</sub>
- [**Spectral**](https://github.com/spectral-mcp/spectral) - Analyze captured application HTTP traffic with an LLM to generate MCP tools, OpenAPI 3.1 specifications, or GraphQL schemas. Generated tools call the observed API directly after capture and authentication setup. <sub>Integration · Independent agent</sub>
- [**jsdeob-workbench**](https://github.com/Owl4444/jsdeob-workbench) - Inspect JavaScript ASTs and variable scopes while building visual chains of Babel transforms. Save analysis projects and reusable plugins to iteratively simplify obfuscated scripts. <sub>Tool</sub>
- [**Browser Reverse Engineering Toolkit**](https://github.com/Dvurechensky/Browser.Reverse.Engineering.Toolkit) - Capture browser-session evidence, crawl websites in a persistent Chromium session, and generate offline architecture/API reports plus OpenAPI, SDK and mock-server drafts from saved captures. <sub>Tool</sub>
- [**screenshot-to-code**](https://github.com/abi/screenshot-to-code) - Generate HTML/CSS, Tailwind, React, Vue, Bootstrap or Ionic front-end code from screenshots, mockups, Figma designs or screen recordings with multimodal models; an optional headless-browser preview lets the model check its rendered output. The result is a visual reconstruction of the interface, not recovered original source or backend behavior. <sub>Tool</sub>

<a id="game"></a>
### Game

[↑ Contents](#contents)

#### Case studies

- [**DX-Ball: reconstruct sound panning**](https://rea.tools/showcase/dx-ball/) - Recover one sound-pan function from instructions and constants; upstream cites 3,205 cases and a 63-byte match. <sub>Case study · REA</sub>
- [**TH04: recover a DOS bullet-ring helper**](https://rea.tools/showcase/th04/) - Inspect a 16-bit PC-98 DOS helper and relate its angle calculation to a pinned reconstruction and historical compiler checks. <sub>Case study · REA</sub>
- [**Super Mario 64 DS: matching decompilation with relocation checks**](https://github.com/tangosdev/sm64ds-decomp) - Reconstructs Super Mario 64 DS functions as C/C++ and permitted assembly primitives, comparing compiled output with a user-supplied cartridge dump. Independent relocation-destination checks strengthen the matching gate; integration into the PC port is tracked separately. <sub>Case study · Independent reconstruction</sub>
- [**GoldenEye 007: an agent-assisted native port from a decompilation**](https://github.com/jkdansereau/goldeneye-pc-port) - Builds a native PC port on the existing GoldenEye 007 decompilation, with a host platform layer and assets extracted from the user’s ROM. The project documents agent collaboration, rendering comparisons, playtest scope and unresolved platform support. <sub>Case study · Independent reconstruction</sub>
- [**ssbu-recomp: static recompilation with explicit mode limits**](https://github.com/Denkishi/ssbu-recomp) - Translates Super Smash Bros. Ultimate 13.0.4 AArch64 code ahead of time and supplies a Windows runtime with Vulkan/OpenGL rendering. It also reconstructs selected fighter scripts as editable C++ and compares translated/source behavior through differential and deterministic tests. <sub>Case study · Independent reconstruction</sub>
- [**KartPad: platform integration for a Mario Kart Wii recompilation**](https://github.com/chrissotraidis/kartpad) - Builds Apple and Android integration around WiiCompiled’s ahead-of-time translation of Mario Kart Wii, with native graphics, input and optional Retro Rewind support. Its status and rights documents distinguish platform acceptance, unresolved device defects and game-content requirements. <sub>Case study · Independent reconstruction</sub>
- [**BattleShip: an AI-assisted Super Smash Bros. native port**](https://github.com/JRickey/BattleShip) - Ports the existing Super Smash Bros. N64 decompilation using libultraship and Torch. The author’s earlier README describes agent-built graphics/audio comparison tools and differential debugging against emulator behavior, rather than claiming AI recovered the game from a cartridge without prior community work. <sub>Case study · Independent reconstruction</sub>
- [**Agent decompilation: a byte-matching retrospective**](https://momo5502.com/posts/2026-10-09-game-decompilation/) - Maurice Heumann describes replacing plausible-looking agent output with compiler-based checks of reconstructed functions, relocations, data and types. The retrospective reports 99% function presence and 83% of all functions byte-exact, while keeping the reconstruction code private. <sub>Case study · Independent reconstruction</sub>
- [**Snowboard Kids 2: an LLM-assisted N64 matching decompilation**](https://github.com/cdlewis/snowboardkids2-decomp) - A public matching decompilation of the N64 game Snowboard Kids 2, begun in 2024 with community decompilation tools. The author’s dated posts document Claude, Codex and GLM workflows, including headless one-shot loops, similarity-based function scheduling and hook-guarded, hash-checked builds, through a reported complete function match. <sub>Case study · Independent reconstruction</sub>
- [**IsaacRecomp: translating Flash game bytecode to native C++**](https://github.com/whylurking/IsaacRecomp) - Translates The Binding of Isaac’s Flash AVM1 bytecode into C++ functions and supplies a native rendering/input runtime. The project reads graphics and audio from the user’s original game and documents deterministic input, headless runs and screenshot regression checks. <sub>Case study · Independent reconstruction</sub>
- [**Nanolathe: a documented Total Annihilation engine reimplementation**](https://github.com/nanolathe-gg/nanolathe) - Reimplements a Total Annihilation-compatible strategy-game engine in Go, with public file-format research and separate gameplay profiles. It distinguishes intended retail 3.1 behavior from community-patch research and deliberate modern changes, and separates synthetic checks from tests requiring original game data. <sub>Case study · Independent reconstruction</sub>
- [**TH08: exact-source reconstruction and separately tested ports**](https://github.com/N0zoM1z0/th08) - Reconstructs the original Japanese Touhou 8 version 1.00d against its binary and original compiler, then adapts the recovered code for other platforms. Source presence, strict function matching, whole-executable identity and playable-port checks are recorded as different milestones. <sub>Case study · Independent reconstruction</sub>
- [**Zelda 64: Recompiled — a native Majora’s Mask port without a full source decompilation**](https://github.com/Zelda64Recomp/Zelda64Recomp) - Uses N64Recomp to translate Majora’s Mask into a native application and RT64 for rendering. The project separates static recompilation from source decompilation while reusing decompilation headers and selected functions for patches and enhancements. <sub>Case study · Independent reconstruction</sub>
- [**OpenGOAL: recovering GOAL code and rebuilding the Jak games**](https://github.com/open-goal/jak-project) - Reconstructs readable GOAL code from the original Jak binaries and compiles it with a new GOAL compiler for modern PCs. Its workflow combines a specialized decompiler, manually supplied type information, asset extraction and an interactive development runtime. <sub>Case study · Independent reconstruction</sub>
- [**LEGO Island: source reconstruction with separately reported exact rebuilds**](https://github.com/isledecomp/isle) - Reconstructs the English LEGO Island 1.1 source for its original 32-bit Windows target. The project distinguishes function-comparison reports, ReproBit’s reported byte-identical retail rebuilds and ordinary developer builds; its modern portable adaptation is a separate repository. <sub>Case study · Independent reconstruction</sub>
- [**Snowball War: a bounded REA-assisted minigame reconstruction**](https://github.com/tuunanet/rea-ski-or-die-reconstruction) - The author uses REA’s Ghidra workflow to investigate the DOS Ski or Die binary, document Snowball War rules and rebuild that one minigame in Rust with SDL2. The public notes distinguish recovered tables and mechanics from approximations and deliberate presentation changes. <sub>Case study · Mixed workflow</sub>
- [**SpaceCadetPinball: decompiled game logic adapted to SDL2**](https://github.com/k4zmu2a/SpaceCadetPinball) - Converts the reverse-engineered Space Cadet pinball game into compilable C++ for desktop platforms. The README identifies the Windows XP executable and public PDB, a Full Tilt executable, and the work of recovering structures, naming variables and adapting the decompiled routines. <sub>Case study · Independent reconstruction</sub>
- [**LASRecomp: Link’s Awakening static recompilation**](https://github.com/peiikai/LASRecomp) - A native desktop reconstruction of the 2019 Switch version of Link’s Awakening using static recompilation. The author attributes most code, tooling and reverse-engineering work to Claude Code with human direction and review. <sub>Case study · Independent reconstruction</sub>
- [**ArkWeb: a two-game movement and collision experiment**](https://github.com/luki-1/ArkWeb) - Runs Spider-Man Remastered and Arkham Knight together, streaming Gotham collision into Spider-Man’s physics world and compositing his rendered frame into Arkham. This experimental runtime bridge is not a recovered standalone game or new engine. <sub>Case study · Independent reconstruction</sub>

#### Tools, projects and integrations

- [**RenderDoc**](https://github.com/baldurk/renderdoc) - Inspect frame captures, draw calls, shaders, and graphics resources in your own game or graphics application. <sub>Tool</sub>
- [**AssetRipper**](https://github.com/AssetRipper/AssetRipper) - Analyze Unity game files, inspect asset dependencies, and convert supported assets into Unity project formats. <sub>Tool</sub>
- [**Cpp2IL**](https://github.com/SamboyCoding/Cpp2IL) - Recover managed representations from Unity IL2CPP builds using binary and metadata analysis; reconstruction remains a work in progress. <sub>Tool</sub>
- [**Il2CppDumper**](https://github.com/Perfare/Il2CppDumper) - Recover IL2CPP metadata and dummy assemblies, and generate helper scripts for native analysis tools; method code is not restored. <sub>Tool</sub>
- [**RenderDoc MCP**](https://github.com/scarletfantasy/renderdoc-mcp) - Expose existing RenderDoc captures to an agent for bounded frame, pipeline, resource, and shader inspection. <sub>Integration · Independent MCP</sub>
- [**UndertaleModTool**](https://github.com/UnderminersTeam/UndertaleModTool) - Browse and modify supported GameMaker data files, extract assets, and decompile or compile GML VM code. Includes room editing, scripted changes, a CLI, and the reusable UndertaleModLib library. <sub>Tool</sub>
- [**frida-il2cpp-bridge**](https://github.com/vfsfitvnm/frida-il2cpp-bridge) - Inspect IL2CPP classes, methods, and fields in a live process, and trace or intercept method calls without supplying global-metadata.dat. Complements static IL2CPP dumpers with runtime observation. <sub>Tool</sub>
- [**objdiff**](https://github.com/encounter/objdiff) - Compare functions and data in reference and rebuilt object files to guide matching decompilation. Displays instruction-level differences, demangles C++ symbols, and can rebuild when source files change. <sub>Tool</sub>
- [**decomp-permuter**](https://github.com/simonlindholm/decomp-permuter) - Randomly or systematically permutes one C function, recompiling each variant and scoring it against a target object file to search for matching compiler output. PERM macros specify manual alternatives, and the optional permuter@home mode distributes runs to other workers. <sub>Tool</sub>
- [**asm-differ**](https://github.com/simonlindholm/asm-differ) - Diffs original and rebuilt assembly for one function or ROM address to guide matching decompilation; its watch mode can rerun make when sources change. The README describes it as decomp.me’s default diff viewer and points to objdiff as a modern alternative. <sub>Tool</sub>
- [**UE Explorer**](https://github.com/UE-Explorer/UE-Explorer) - Explore Unreal packages through class, property, and dependency trees; decompile and export UnrealScript classes, inspect bytecode, and examine structured binary data. <sub>Tool</sub>
- [**GARbro**](https://github.com/morkt/GARbro) - Browse recognized visual-novel resource archives as folders, preview their contents, and extract images or audio with conversion to common formats. <sub>Tool</sub>
- [**Godot RE Tools**](https://github.com/GDRETools/gdsdecomp) - Recover supported Godot project files, GDScript and imported resources from exported games. Includes PCK inspection and extraction, script decompilation, and resource conversion for examining and rebuilding project structure. <sub>Tool</sub>
- [**UE4SS**](https://github.com/UE4SS-RE/RE-UE4SS) - Inspect Unreal Engine games at runtime through live UObject property views, reflected C++ header dumps, property mappings and actor dumps. Lua and C++ APIs support experiments while reconstructing game structures. <sub>Tool</sub>
- [**FModel**](https://github.com/4sval/FModel) - Explore Unreal Engine game archives with CUE4Parse-backed package and property inspection, asset previews and export. The 2026 summer release adds USD world export for reconstructing supported scene content. <sub>Tool</sub>
- [**PSP Web Recomp**](https://github.com/snuri00/psp-web-recomp) - Translate PSP MIPS executables into C++ and WebAssembly, backed by a PSP high-level emulation runtime and WebGL2 renderer. Native tracing, frame capture and audio tools support investigating missing behavior during game porting. <sub>Project</sub>
- [**N64: Recompiled**](https://github.com/N64Recomp/N64Recomp) - Statically recompiles N64 MIPS binaries into C functions from symbol metadata, emitting function lookups and relocation macros so a runtime can handle statically linked and relocatable overlays. The output needs a runtime such as N64ModernRuntime; the repository also includes RSP microcode and mod tooling. <sub>Tool</sub>
- [**XenonRecomp**](https://github.com/hedge-dev/XenonRecomp) - Converts Xbox 360 PowerPC executables into C++ that can be compiled for other platforms, with the XenonAnalyse companion detecting jump tables and function boundaries. Output is a literal instruction translation rather than decompiled code and needs a runtime that the project does not supply. <sub>Tool</sub>

<a id="app"></a>
### App

[↑ Contents](#contents)

#### Case studies

- [**Aegis: trace a login-code calculation**](https://rea.tools/showcase/aegis/) - An official APK investigation follows TOTP methods in Aegis and publishes artifact identities and selected Evidence. <sub>Case study · REA</sub>
- [**Notion: trace the clipboard bridge**](https://rea.tools/showcase/notion/) - Trace a packaged Electron clipboard path using REA findings and separate source inspection; the dynamic wrapper remains a stated limit. <sub>Case study · REA</sub>
- [**ReaCut: video-editor reconstruction**](https://github.com/Xiangyu-CAS/rea-capcut) - An independent video editor whose authors document REA-assisted investigation of Jianying/CapCut behavior and project formats. The public implementation includes a local timeline, FFmpeg export and an experimental, lossy draft importer. <sub>Case study · Mixed workflow</sub>
- [**zee-rp: reconstructing supported Axure RP 11 document operations**](https://github.com/LilZeeCN/zee-rp) - Reads and rewrites supported native Axure RP 11 documents through a binary-record codec, reference-aware cloning and constrained interaction writers. CLI and MCP interfaces expose inspected edits while keeping offline structure checks separate from native application acceptance. <sub>Case study · Independent reconstruction</sub>
- [**Virtual Desktop Streamer: rehosting the platform layer on Linux**](https://github.com/cudanexus/vd-streamer-linux) - An author-reported Claude Code and REA workflow replaces the macOS streamer’s capture, encoding, audio and input layer with Linux implementations while reusing vendor protocol libraries. The documented result targets desktop streaming and video playback, not Windows-only VR game streaming. <sub>Case study · Mixed workflow</sub>
- [**Open Claude UI: REA-informed interface reference components**](https://github.com/Caho1/open-claude-ui) - Publishes React components, motion helpers and design-system notes derived from the author’s reported REA investigation of Claude Desktop. It is useful as an interface-reconstruction case, with version-specific observations rather than proof of a complete assistant application or backend clone. <sub>Case study · Mixed workflow</sub>
- [**PlxNative: reconstructing a native webOS media-client interface**](https://github.com/GLinnik21/plx-native) - An unofficial Plex client built after the author investigated LG webOS native media interfaces with Ghidra and coding agents. It draws its own Rust/OpenGL interface and uses the television’s decoder, with documented host, simulator and real-device test tiers. <sub>Case study · Independent reconstruction</sub>
- [**Windows Calculator: reconstructing percentage rules**](https://github.com/morluto/rea/blob/c360cfcd6d7901514b16dd6113eba2e0b0fdf422/website/evidence/calculator-and-dino.md#windows-calculator) - REA’s case traces the installed Windows Calculator model DLL to explain different percentage behavior for multiplication/division and other operations. An analyst-selected function is interpreted against public Microsoft source and demonstrated with fixed browser examples. <sub>Case study · REA</sub>
- [**Feishu: an author-reported isolated second app instance**](https://benx.ai/blog/posts/rea-reverse-engineer-feishu-dual-instance/) - The author reports using Codex and REA analysis to adapt a separate macOS Feishu copy with its own application identity, data directory and single-instance lock. The account describes local signing and separation checks while retaining the original app unchanged. <sub>Case study · Mixed workflow</sub>
- [**LSX II Volume Fixer: reconstructing volume behavior**](https://github.com/roberdorfer/kef-lsx-volume) - Uses measured USB-volume behavior and a macOS audio proxy to map volume keys to a KEF LSX II’s LAN control. The project reports more even steps while forwarding USB audio; the speaker firmware is unchanged. <sub>Case study · Independent reconstruction</sub>

#### Tools, projects and integrations

- [**JADX-AI-MCP**](https://github.com/zinja-coder/jadx-ai-mcp) - JADX plugin paired with a Python MCP server to inspect decompiled Android classes, resources, cross-references and debugger context. <sub>Integration · Independent MCP</sub>
- [**apktool-mcp-server**](https://github.com/zinja-coder/apktool-mcp-server) - Python MCP server that drives a local Apktool install so agents can decode APKs; list, read, search and edit smali and resource files; read AndroidManifest.xml and apktool.yml; and rebuild the project. <sub>Integration · Independent MCP</sub>
- [**frida-mcp (yfe404)**](https://github.com/yfe404/frida-mcp) - Frida MCP server with persistent instrumentation sessions, runtime inspection and Android static-to-dynamic navigation. <sub>Integration · Independent MCP</sub>
- [**Super Trouper**](https://github.com/crissyfield/super-trouper) - Single-binary Frida MCP server for discovering devices, managing process sessions and loading instrumentation scripts. <sub>Integration · Independent MCP</sub>
- [**Frida**](https://github.com/frida/frida) - Dynamic instrumentation toolkit for observing and scripting the behavior of live native and managed processes. <sub>Tool</sub>
- [**JADX**](https://github.com/skylot/jadx) - Dex-to-Java decompiler with CLI/GUI navigation, resource decoding and cross-reference search for Android packages. <sub>Tool · Android</sub>
- [**Apktool**](https://github.com/iBotPeaches/Apktool) - Decodes Android resources and smali into a project-like tree and can rebuild modified packages. <sub>Tool · Android</sub>
- [**Androguard**](https://github.com/androguard/androguard) - Python toolkit for APK/DEX metadata, bytecode and reference analysis; the v5 source branch also documents agent skills and MCP. <sub>Tool · Android</sub>
- [**ILSpy**](https://github.com/icsharpcode/ILSpy) - .NET assembly browser and C# decompiler with whole-project export, metadata inspection and a scriptable command-line frontend. <sub>Tool · .NET</sub>
- [**dnSpyEx**](https://github.com/dnSpyEx/dnSpy) - Community continuation of dnSpy for debugging and editing .NET assemblies without the original source. <sub>Tool · .NET</sub>
- [**@electron/asar**](https://github.com/electron/asar) - Electron's archive tool lists and extracts ASAR contents so packaged JavaScript and application assets can be inspected. <sub>Tool</sub>
- [**Mobile Security Framework (MobSF)**](https://github.com/MobSF/Mobile-Security-Framework-MobSF) - Inspect mobile application packages with static analysis and supported-device dynamic testing, including runtime behavior and network traffic, through a web interface and APIs. <sub>Tool · Android</sub>
- [**objection**](https://github.com/sensepost/objection) - Explore running Android and iOS apps with a Frida-backed command interface for inspecting app storage, memory, runtime objects, and instrumented behavior. <sub>Tool · Android</sub>
- [**Grapefruit**](https://github.com/ChiChou/grapefruit) - Inspect and hook running iOS and Android apps from a Frida-based web interface, with method and crypto-API hooks, filesystem and SQLite browsers, iOS keychain and UI-hierarchy views, and HTTP capture from common networking libraries. <sub>Tool</sub>
- [**Blutter**](https://github.com/worawit/blutter) - Analyze Flutter Android ARM64 AOT binaries using the matching Dart runtime. Produces annotated assembly, object-pool dumps and a target-specific Frida script template for investigating compiled Dart application logic. <sub>Tool · Android</sub>
- [**hermes-dec**](https://github.com/P1sec/hermes-dec) - Parse, disassemble and partially decompile React Native Hermes bytecode bundles. Makes HBC headers and instructions inspectable and emits pseudocode for understanding compiled application logic. <sub>Tool · Android</sub>
- [**Recaf**](https://github.com/Col-E/Recaf) - Inspect and modify compiled JVM applications with integrated decompilers, bytecode assembly, reference search, mappings and deobfuscation tools. The reviewed 4.0 preview also provides basic read-only Android bytecode inspection. <sub>Tool · JVM</sub>
- [**nibkit**](https://github.com/tokenbleed/nibkit) - Decode compiled iOS/macOS interface archives into object trees, Outlet/Action connections, custom classes and navigation relationships. Exports JSON or Mermaid diagrams and exposes read-only inspection commands through MCP. <sub>Tool</sub>
- [**AOTopsy**](https://github.com/BroNils/aotopsy) - Statically inspect Flutter/Dart AOT libapp.so files to recover available metadata, class structures, call edges and pseudocode without embedding a Dart VM or compiling a matching SDK. Supports ARM64 and x86_64 analysis paths. <sub>Tool · Android</sub>
- [**hbctool**](https://github.com/bongtrop/hbctool) - Disassemble and reassemble supported React Native Hermes bytecode bundles through HASM files, enabling bytecode inspection and editing for the explicitly supported legacy HBC versions. <sub>Tool · Android</sub>

<a id="native-binary"></a>
### Native Binary

[↑ Contents](#contents)

#### Case studies

- [**DownUnderCTF: masked-squares flag checker**](https://rea.tools/showcase/ctf/) - An official educational challenge investigation connects binary checks to equations and records an original-program validation. <sub>Case study · REA</sub>

#### Tools, projects and integrations

- [**Ghidra**](https://github.com/NationalSecurityAgency/ghidra) - Open-source analysis suite for disassembly, decompilation, graphs and Java/Python automation across executable formats. <sub>Tool</sub>
- [**radare2**](https://github.com/radareorg/radare2) - Scriptable command-line framework for inspecting, disassembling, debugging and modifying binaries across many architectures. <sub>Tool</sub>
- [**Cutter**](https://github.com/rizinorg/cutter) - Rizin-powered graphical reverse-engineering workspace with extensible views and Ghidra decompiler integration. <sub>Tool</sub>
- [**Qiling**](https://github.com/qilingframework/qiling) - Python emulation framework that adds OS, filesystem and API behavior around CPU emulation for instrumented binary analysis. <sub>Tool</sub>
- [**Unicorn Engine**](https://github.com/unicorn-engine/unicorn) - Multi-architecture CPU emulator for executing selected instruction ranges with register, memory and hook control. <sub>Tool · Library</sub>
- [**angr**](https://github.com/angr/angr) - Python binary-analysis framework combining control-flow recovery, symbolic execution, data-flow analysis and decompilation. <sub>Tool · Library</sub>
- [**LIEF**](https://github.com/lief-project/LIEF) - Library for structured parsing and modification of executable formats including ELF, PE and Mach-O. <sub>Tool · Library</sub>
- [**Capstone**](https://github.com/capstone-engine/capstone) - Disassembly library with architecture-neutral APIs and instruction details for custom binary-analysis pipelines. <sub>Tool · Library</sub>
- [**ImHex**](https://github.com/WerWolv/ImHex) - Hex editor with a binary-pattern language, structured data inspection and visual tools for understanding file formats. <sub>Tool</sub>
- [**x64dbg**](https://github.com/x64dbg/x64dbg) - Windows binary debugger with disassembly, memory views and plugins for analyzing programs without source code. <sub>Tool</sub>
- [**GDB**](https://sourceware.org/gdb/) - Native and remote debugger for controlling execution and inspecting live or crashed program state. <sub>Tool</sub>
- [**rr**](https://github.com/rr-debugger/rr) - Records process execution and replays it under GDB, enabling repeatable inspection and reverse execution. <sub>Tool</sub>
- [**Diaphora**](https://github.com/joxeankoret/diaphora) - IDA-based binary diffing that matches functions and transfers names, comments and types between analyzed versions. <sub>Tool</sub>
- [**BinDiff**](https://github.com/google/bindiff) - Compares disassembled binaries to find matching functions and changed code across versions. <sub>Tool</sub>
- [**Detect It Easy**](https://github.com/horsicq/Detect-It-Easy) - Format-aware file identification and static inspection using parsers, signatures and programmable heuristics. <sub>Tool</sub>
- [**r2frida**](https://github.com/nowsecure/r2frida) - Use radare2 commands and Frida instrumentation together to inspect local or remote process memory, symbols, classes, and runtime calls on desktop and mobile targets. <sub>Tool</sub>
- [**Kaitai Struct**](https://github.com/kaitai-io/kaitai_struct) - Turn documented binary layouts into reusable parsers for files and network packets. A .ksy specification can be inspected with visualizers and compiled to multiple languages, helping preserve reverse-engineered format knowledge in interoperable implementations. <sub>Tool · Library</sub>
- [**GoReSym**](https://github.com/mandiant/GoReSym) - Recover Go build metadata, function names and address ranges, source file and line tables, embedded types and strings from Go binaries, including stripped and some malformed unpacked samples. JSON output can be imported into IDA Pro with the included IDAPython script. <sub>Tool</sub>
- [**rev.ng**](https://github.com/revng/revng) - Open-source decompilation pipeline that lifts x86-64, AArch64, i386, ARM and MIPS code with QEMU, runs LLVM-based analyses and emits C designed to be valid and recompilable. Data layout analysis infers structures from pointer use; an editable YAML model and Python or TypeScript wrappers support automation. Its VSCode-based UI is a separate closed-beta product, with commercial plans announced. <sub>Tool</sub>

<a id="firmware"></a>
### Firmware and Hardware

[↑ Contents](#contents)

#### Case studies

- [**PicoPrint: LX-D02 printer investigation**](https://github.com/bigtower17/picoprint) - The author describes REA-assisted Android investigation followed by separate Hermes decompilation to support a Windows BLE printer. <sub>Case study · Mixed workflow</sub>

#### Tools, projects and integrations

- [**Binwalk**](https://github.com/ReFirmLabs/binwalk) - Identifies embedded formats and optionally extracts their contents, with entropy analysis for firmware triage. <sub>Tool</sub>
- [**unblob**](https://github.com/onekey-sec/unblob) - Recursively extracts archives and filesystems from binary blobs while reporting chunk boundaries and unknown regions. <sub>Tool</sub>
- [**Ghidra Firmware Utilities**](https://github.com/al3xtjames/ghidra-firmware-utils) - Ghidra loaders and helpers for PCI option ROMs, UEFI firmware volumes, Intel flash descriptors and coreboot images. <sub>Tool</sub>
- [**EMBA**](https://github.com/e-m-b-a/emba) - Extract firmware, combine static checks with emulation-based analysis, inventory software components, and generate web reports and SBOMs for further investigation. <sub>Tool</sub>
- [**Firmware Analysis and Comparison Tool (FACT)**](https://github.com/fkie-cad/FACT_core) - Unpack and analyze firmware through an extensible platform whose web interface and HTTP API make component contents and analysis results searchable and comparable across samples. <sub>Tool</sub>
- [**OFRAK**](https://github.com/redballoonsecurity/ofrak) - Recursively identify, unpack, analyze, modify, and repack firmware and binary formats using a resource-tree GUI and Python API, with optional disassembler backends. <sub>Tool</sub>
- [**FirmAE**](https://github.com/pr0v3rbs/FirmAE) - Emulate router and IP-camera firmware to inspect network services and runtime behavior, with automated emulation checks and separate analysis, run, and debugging modes. <sub>Tool</sub>
- [**PulseView**](https://github.com/sigrokproject/pulseview) - Examine captured logic and analog waveforms with sigrok's graphical frontend. Protocol decoders and decoder stacking expose bus messages and higher-level device operations, making hardware communication traces useful for firmware and interoperability investigations. <sub>Tool</sub>
- [**UEFITool**](https://github.com/LongSoft/UEFITool) - Parse UEFI firmware images into an inspectable tree and check their structure. Companion UEFIExtract and UEFIFind tools extract parsed contents and locate patterns, supporting analysis of firmware components and vendor formats. <sub>Tool</sub>
- [**Glasgow Interface Explorer**](https://github.com/GlasgowEmbedded/glasgow) - Use FPGA-based open hardware and Python applets to read and write SPI flash, I2C EEPROM and parallel memory chips, determine JTAG pinouts, debug supported processors and analyze UART, SPI and QSPI transactions on physical devices. <sub>Tool</sub>
- [**Penguin**](https://github.com/rehosting/penguin) - Rehost embedded Linux firmware from an extracted root filesystem using a generated, editable configuration of emulation transformations, then refine it through a guest root shell, forwarded network services and recorded dynamic-analysis output. <sub>Tool</sub>

<a id="protocol"></a>
### Protocols

[↑ Contents](#contents)

#### Case studies

- [**open-appleremote: Siri Remote protocol reconstruction**](https://github.com/a-funk/open-appleremote) - Reconstructs first-generation Siri Remote Bluetooth reports for Linux, decoding buttons, touch and tvOS-style gestures. The Python implementation and protocol notes distinguish measured behavior, historical reports and inferred meanings. <sub>Case study · Independent reconstruction</sub>
- [**GAMEKB-K17: reconstructing a macropad configuration protocol**](https://github.com/dvdarkin/gamekb-k17) - Implements the vendor HID configuration protocol for the GAMEKB-K17/HCY-K017 macropad. It writes key mappings, firmware macros and RGB settings, then reads them back; protocol notes separate tested commands from unconfirmed observations and other-device findings. <sub>Case study · Independent reconstruction</sub>
- [**CF632BLE: a local client from scale-protocol research**](https://github.com/guyru/cf632ble) - Reimplements the CF632BLE scale’s BLE protocol and body-composition calculations from research on the vendor’s Unique Health Android app. A static Web Bluetooth client receives measurements, manages device profiles and keeps its history in browser storage. <sub>Case study · Independent reconstruction</sub>
- [**cooler-lcd: a Thermalright display protocol implementation**](https://github.com/kristjaningi/cooler-lcd) - Implements a USB picture-transfer driver for Thermalright Vision cooler displays, with a Rust dashboard replacing the vendor display application. The documented protocol sends a header and JPEG frames, with periodic resends to prevent the device reverting to its logo. <sub>Case study · Independent reconstruction</sub>
- [**hw-harness: scanner USB protocol investigation**](https://github.com/cschalle/hw-harness) - Documents an author-reported scanner investigation comparing vendor-driver USB control transfers with Linux-driver traces to infer initialization, timing and resolution parameters. The released harness organizes reference capture and comparison; it does not automatically recover a complete protocol specification. <sub>Case study · Independent reconstruction</sub>

#### Tools, projects and integrations

- [**Wireshark**](https://gitlab.com/wireshark/wireshark) - Inspect captured application and device traffic as decoded protocol fields, with filtering and shared GUI/TShark dissection. Custom dissectors let an analyst encode newly understood packet formats and compare protocol implementations. <sub>Tool</sub>
- [**Netzob**](https://github.com/netzob/netzob) - Model communication protocols and infer message layouts from traces, with configured active learning for protocol state machines. Python APIs expose message fields, symbols and automata for parsing, traffic generation and fuzzing. <sub>Tool</sub>
- [**Scapy**](https://github.com/secdev/scapy) - Script packet dissection, construction, request/reply matching and capture-file analysis in Python. Custom packet fields and layer bindings let analysts encode understood wire formats and investigate protocol behavior. <sub>Tool</sub>
- [**Universal Radio Hacker (URH)**](https://github.com/jopohl/urh) - Demodulate and decode signals captured with software-defined radios, with automatic modulation-parameter detection and customizable decodings. Analysts assign protocol fields and message types by hand or review rule-based automatic field inference; a fuzzer targets stateless protocols and a simulator supports stateful exchanges. <sub>Tool</sub>
- [**SavvyCAN**](https://github.com/collin80/SavvyCAN) - Capture or load CAN bus traffic and investigate frames with sniffer, graphing, file-comparison and ISO-TP/UDS decoding views; loaded or analyst-edited DBC files map raw bytes to named signals. Separate custom-sender, fuzzing and UDS-scan windows transmit frames on a live bus. <sub>Tool</sub>
- [**AALpy**](https://github.com/DES-Lab/AALpy) - General-purpose Python automata-learning library that infers deterministic, non-deterministic, stochastic and pushdown models of black-box systems from active queries or passive traces. Its README links a separate Bluetooth Low Energy study whose repository reports learned connection and legacy-pairing state machines; message formats are not inferred. <sub>Tool</sub>

<a id="agents-and-mcp"></a>
### Agents and MCP

[↑ Contents](#contents)

- [**REA — Reverse Engineer Anything**](https://github.com/morluto/rea) - The upstream CLI and MCP server for evidence-based investigations of shipped software and runtime behavior. <sub>Project · REA</sub>
- [**Official reverse-engineer-anything skill**](https://github.com/morluto/rea/tree/main/.agents/skills/reverse-engineer-anything) - Target routing, connection recovery and evidence practices for agents using REA. <sub>Integration · REA</sub>
- [**dsh-mcp-rea**](https://github.com/Ersith/dsh-mcp-rea) - A community MCP bridge presents a smaller selected tool surface and forwards explicit commands to the REA CLI. <sub>Integration · REA</sub>
- [**rea-jev**](https://github.com/juan-viox/rea-jev) - A Claude Code plugin adds Jev-based routing and evidence checks around a pinned REA MCP integration. <sub>Integration · REA</sub>
- [**rea-casebook**](https://github.com/pablodiazjorge/rea-casebook) - A Claude Code mod collects received REA Evidence, tracks unknowns and records findings that cite delivered evidence IDs. <sub>Integration · REA</sub>
- [**Hex-Rays IDA MCP**](https://github.com/HexRaysSA/ida-mcp) - Official Hex-Rays MCP server for agent access to IDA databases, with headless operation and optional GUI integration. <sub>Integration · Independent MCP</sub>
- [**GhidraMCP**](https://github.com/LaurieWired/GhidraMCP) - Ghidra extension and MCP bridge exposing decompilation, symbol navigation and renaming to agents, with GUI and headless modes. <sub>Integration · Independent MCP</sub>
- [**Binary Ninja MCP (official)**](https://docs.binary.ninja/guide/mcp.html) - Binary Ninja's own MCP interface exposes functions, symbols, disassembly, intermediate languages and decompiled text to agents. <sub>Integration · Independent MCP</sub>
- [**Binary Ninja MCP (fosdickio)**](https://github.com/fosdickio/binary_ninja_mcp) - Community Binary Ninja plugin and bridge for MCP clients, including workflows that switch among multiple open binaries. <sub>Integration · Independent MCP</sub>
- [**IDA Pro MCP (mrexodia)**](https://github.com/mrexodia/ida-pro-mcp) - Community IDA integration useful for existing setups and migration context; its maintainer now recommends the official Hex-Rays MCP server. <sub>Integration · Independent MCP</sub>
- [**Radare2 MCP Server**](https://github.com/radareorg/radare2-mcp) - Native radare2 MCP server offering binary-analysis tools, reusable sessions and configurable read-only access. <sub>Integration · Independent MCP</sub>
- [**r2ai**](https://github.com/radareorg/r2ai) - AI plugins inside radare2 for function explanations, naming suggestions and model-assisted decompilation using local or remote models. <sub>Integration · Independent agent</sub>
- [**DAILA**](https://github.com/mahaloz/DAILA) - Decompiler-independent AI assistant for function summaries and naming across IDA, Ghidra, Binary Ninja and angr-management. <sub>Integration · Independent agent</sub>
- [**RevEng.AI Ghidra Plugin**](https://github.com/RevEngAI/plugin-ghidra) - Connects Ghidra to RevEng.AI for function similarity, recovered names, AI explanations and agent-assisted annotation. <sub>Integration · Independent agent</sub>
- [**LLDB MCP**](https://lldb.llvm.org/use/mcp.html) - LLDB's official MCP interface gives agents debugger sessions and commands for breakpoints, memory inspection and stepping. <sub>Integration · Independent MCP</sub>
- [**Claude Reverse Engineering Skill**](https://github.com/EncidXVII/claude-reverse-engineering-skill) - Community agent skill for triage, headless exports and evidence-based RE reports; explicitly documents workflows with REA and other MCP servers. <sub>Integration · Independent agent</sub>
- [**SpecterOps Reverse Engineering Skills**](https://github.com/SpecterOps/skills/tree/main/plugins/reverse-engineering) - Focused Binary Ninja and Ghidra analysis skills that describe MCP tool use, analysis recipes and annotation practices. <sub>Integration · Independent agent</sub>
- [**pyghidra-mcp**](https://github.com/clearbluejar/pyghidra-mcp) - PyGhidra-based MCP server that analyzes every binary in a Ghidra project and exposes decompilation, cross-references, call graphs, symbol and string search, indexed semantic code search, and renaming, typing and comment edits. A separate HTTP CLI client and an optional mode driving a Ghidra GUI it launches are included. <sub>Integration · Independent MCP</sub>

<a id="related-collections"></a>
### Related Collections

[↑ Contents](#contents)

- [**Awesome Reverse Engineering**](https://github.com/morluto/awesome-reverse-engineering) - A task-oriented reverse-engineering resource list by REA's maintainer, useful for broader tools and foundations. <sub>Collection</sub>
- [**Awesome REA Cases**](https://github.com/songshikang0111/awesome-REA-cases) - A bilingual collection of REA and other AI-assisted reverse engineering cases, with source links and explicit distinctions between reported and reproduced outcomes. <sub>Collection</sub>
- [**awesome-rea (yibie): verification-focused projects and practice reports**](https://github.com/yibie/awesome-rea) - Organizes AI-assisted game decompilation, native ports, static recompilation and tooling around stated acceptance checks, alongside a separate track of practitioner write-ups and discussions. Useful for finding primary reports and comparing how projects define correctness. <sub>Collection</sub>
- [**Awesome REA/Decompiled Games**](https://github.com/HaozheH3/awesome-rea-games) - Groups game decompilations, source reconstructions, recompilations, native ports and demos by original game, with comparison rows linking related projects. It distinguishes launchers, engine work and creator-shared showcases from source-reconstruction efforts. <sub>Collection</sub>

<a id="references-and-learning"></a>
### References and Learning

[↑ Contents](#contents)

- [**Installation and client setup**](https://github.com/morluto/rea/blob/main/docs/installation.md) - Reviewed setup plans, client registration, provider prerequisites and scoped readiness checks. <sub>Documentation · REA</sub>
- [**CLI and Evidence**](https://github.com/morluto/rea/blob/main/docs/cli.md) - CLI workflows for saving Evidence and projecting smaller views from completed analysis. <sub>Documentation · REA</sub>
- [**MCP contracts and generated catalog**](https://github.com/morluto/rea/blob/main/docs/mcp-contracts.md#generated-catalog) - Canonical tool contracts, provider discovery and Evidence semantics for integration authors. <sub>Documentation · REA</sub>
- [**Native binary investigation**](https://github.com/morluto/rea/blob/main/docs/native-investigation.md) - Locate a function, inspect instructions and pseudocode, and follow references with a selected native provider. <sub>Documentation · REA</sub>
- [**Cross-layer JavaScript application workflows**](https://github.com/morluto/rea/blob/main/docs/javascript-application-workflows.md) - Trace features and compare authenticated JavaScript application graphs while preserving static-analysis limits. <sub>Documentation · REA</sub>
- [**Static Android APK analysis**](https://github.com/morluto/rea/blob/main/docs/android-analysis.md) - Inspect Android package identity, classes, methods and references through REA's JADX integration. <sub>Documentation · REA</sub>
- [**Managed-code analysis**](https://github.com/morluto/rea/blob/main/docs/managed-code-analysis.md) - Read PE/CLI metadata and CIL, compare managed members and inspect declared native boundaries without loading the assembly. <sub>Documentation · REA</sub>
- [**Historical web network captures**](https://github.com/morluto/rea/blob/main/docs/web-network-captures.md) - Inspect saved web captures offline; recorded URLs are not fetched and no proxy is started. <sub>Documentation · REA</sub>
- [**Firmware analysis**](https://github.com/morluto/rea/blob/main/docs/firmware-analysis.md) - Inspect firmware regions with Binwalk and explicitly extract with Unblob, retaining tool and artifact identity. <sub>Documentation · REA</sub>
- [**Browser observation guide**](https://rea.tools/guides/browser/) - Follow a user-triggered export request in the supplied Notes browser example and connect it to the downloaded result. <sub>Documentation · REA</sub>
- [**JavaScript and Electron: follow a CSV export**](https://rea.tools/guides/javascript/) - A source-owned Notes fixture teaches the renderer, preload, IPC and CSV path with linked analysis evidence. <sub>Documentation · REA</sub>
- [**rea-playbook**](https://github.com/jinshi666888/rea-playbook) - An Electron practice target, Evidence extractor and MCP probe; offline fixture mode is distinguished from real REA analysis. <sub>Learning resource</sub>
- [**rea-lab**](https://github.com/pablodiazjorge/rea-lab) - A Windows REA/Ghidra lab with seeded challenges, published studies, upstream contributions and recorded limitations. <sub>Research</sub>
- [**OpenSecurityTraining2**](https://ost2.fyi/) - Free self-paced security courses with learning paths for reverse engineering, firmware and systems foundations. <sub>Learning resource</sub>
- [**pwn.college: Reverse Engineering**](https://pwn.college/program-security/reverse-engineering/) - Hands-on reverse-engineering module covering functions, data access, static tools and dynamic tools with hosted exercises. <sub>Learning resource</sub>
- [**Reverse Engineering for Beginners**](https://beginners.re/) - Dennis Yurichev's free book on understanding compiled programs and assembly, available in multiple languages. <sub>Learning resource</sub>
- [**The Official Radare2 Book**](https://book.rada.re/) - Official practical reference for radare2 analysis, disassembly, scripting, debugging and related plugins. <sub>Learning resource</sub>
<!-- END GENERATED CATALOG -->

<!-- BEGIN GENERATED PAPERS -->
<a id="papers"></a>
## Papers

A bibliography of **33 papers** on reverse-engineering agent evaluation, decompilation, protocol inference, firmware analysis, and website, game, and app reconstruction. Some papers also appear among curated resources; counts are not additive. Publication status and study scope are made explicit.

[Browse the paper directory](https://awesomerea.org/papers/) · [Complete bibliography JSON](data/papers.json) · [Suggest a paper](https://github.com/reacher-z/Awesome-REA/issues/new?template=paper.yml)

**By topic** · [Agent evaluation](#papers-agent-evaluation) <sub>5</sub> · [Decompilation](#papers-decompilation) <sub>6</sub> · [Websites](#papers-website-reconstruction) <sub>8</sub> · [Games](#papers-game-reconstruction) <sub>5</sub> · [Apps](#papers-app-reconstruction) <sub>5</sub> · [Firmware](#papers-firmware-analysis) <sub>2</sub> · [Protocols](#papers-protocol-analysis) <sub>2</sub>

Open “Scope and publication details” for each study’s full limitations. Papers are ordered newest first within each topic.

<a id="papers-agent-evaluation"></a>
### Reverse-engineering agent evaluation

[↑ Paper topics](#papers) · [Contents](#contents)

- [**Humans vs. Machines: A Comparison With AI Agents in Software Reverse Engineering**](https://arxiv.org/abs/2610.14960) · **2026 · Preprint**

  Compares human and LLM-agent understanding and navigation on the same static reverse-engineering challenges, then studies how binary representations consume context windows.

  [PDF](https://arxiv.org/pdf/2610.14960)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Understanding is graded on two compact challenges; the separate 4,000-binary study measures context capacity, not task-solving accuracy. The interface is static IDA/MCP without dynamic execution, and prior exposure to challenge source remains an acknowledged validity threat.

  **Publication:** 2026 · arXiv · Preprint · Samuele Doria et al.

  </details>

- [**The Next Challenge for Agentic Cybersecurity: A Realistic, Contamination-Free Reverse Engineering Benchmark**](https://arxiv.org/abs/2608.11469) · **2026 · Preprint**

  Introduces SRE-Bench, with privately authored programs and protected binary variants, to study agent recovery of program semantics while reducing training-data contamination.

  [PDF](https://arxiv.org/pdf/2608.11469)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The revised study reports 19 programs, 262 binary instances, and 1,572 graded tasks. Binaries and task instances are not publicly released; access is through an evaluation service. Its contamination-control claim is the authors' methodology, not an independent guarantee.

  **Publication:** 2026 · arXiv · Preprint · Jeremy Spence et al.

  </details>

- [**CrackMeBench: Binary Reverse Engineering for Agents**](https://arxiv.org/abs/2605.10597) · **2026 · Preprint**

  Evaluates agents on executable-checked CrackMe tasks: infer validation logic from binaries and submit an accepted input or artifact, while recording tool use, time, and scoring attempts.

  [PDF](https://arxiv.org/pdf/2605.10597)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The v0 study uses 12 generated tasks and eight public calibration tasks, Linux x86-64 ELF binaries, a shell interface, and a five-minute budget. Its compact educational tasks do not establish performance on large applications. No paper-linked public artifact URL was verified.

  **Publication:** 2026 · arXiv · Preprint · Isaac David et al.

  </details>

- [**ProgramBench: Can Language Models Rebuild Programs From Scratch?**](https://arxiv.org/abs/2605.03546) · **2026 · Accepted**

  Evaluates black-box program reconstruction across 200 tasks: agents query an executable and read its documentation, then independently implement a codebase whose behavior is checked by generated tests.

  [PDF](https://arxiv.org/pdf/2605.03546v1) · [Code](https://github.com/facebookresearch/ProgramBench)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Binary inspection, decompilation, and internet access are forbidden during inference. Passing finite tests does not prove complete behavioral equivalence or recovery of the original source. Later live-leaderboard runs are separate from the reviewed arXiv results.

  **Publication:** 2026 · NeurIPS 2026 · Accepted · John Yang et al.

  </details>

- [**CREBench: Evaluating Large Language Models in Cryptographic Binary Reverse Engineering**](https://openreview.net/forum?id=tLYdf8hWJB) · **2026 · Conference paper**

  Benchmarks cryptographic binary reverse engineering across algorithm recognition, key or IV extraction, wrapper reconstruction, and flag recovery using 432 controlled challenges.

  [PDF](https://arxiv.org/pdf/2604.03750v2) · [Code](https://github.com/wangyu-ovo/CREBench)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The corpus combines 48 algorithms, three insecure key-use scenarios, and three difficulty levels. It excludes professional-grade obfuscators such as Tigress and O-LLVM; results should not be generalized to heavily protected arbitrary binaries.

  **Publication:** 2026 · COLM 2026 · Conference paper · Baicheng Chen et al.

  </details>

<a id="papers-decompilation"></a>
### Decompilation and symbol recovery

[↑ Paper topics](#papers) · [Contents](#contents)

- [**DecompileBench: A Comprehensive Benchmark for Evaluating Decompilers in Real-World Scenarios**](https://aclanthology.org/2025.findings-acl.1194/) · **2025 · Conference paper**

  Evaluates traditional and LLM-based decompilers using functions from real programs, runtime behavioral checks, and an LLM-assisted assessment of analyst-facing code understandability.

  [PDF](https://aclanthology.org/2025.findings-acl.1194.pdf) · [Code](https://github.com/vul337/DecompileBench)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The evaluated corpus has 23,400 functions from 130 programs. Fuzzing-based checks have finite coverage, and understandability scores depend partly on an LLM judge. The artifact warns that rebuilt OSS-Fuzz projects can differ from the paper's versions.

  **Publication:** 2025 · Findings of ACL 2025 · Conference paper · Zeyu Gao et al.

  </details>

- [**Decompile-Bench: Million-Scale Binary-Source Function Pairs for Real-World Binary Decompilation**](https://papers.nips.cc/paper_files/paper/2025/hash/079cf13ae174c31f148207d94d213bdc-Abstract-Datasets_and_Benchmarks_Track.html) · **2025 · Conference paper**

  Introduces two million C/C++ binary-source function pairs using a Compile-Trace-Filter pipeline, with an evaluation suite spanning translated HumanEval/MBPP tasks and recent GitHub functions.

  [PDF](https://papers.nips.cc/paper_files/paper/2025/file/079cf13ae174c31f148207d94d213bdc-Paper-Datasets_and_Benchmarks_Track.pdf) · [Code](https://github.com/albertan017/LLM4Decompile)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** This is function-level decompilation. Re-execution tests cover HumanEval/MBPP; GitHub2025 provides no unit tests. Inlining can prevent one-to-one source correspondence, and the fine-tuning study uses 10% of the corpus. These results do not establish whole-program recovery.

  **Publication:** 2025 · NeurIPS 2025 Datasets and Benchmarks · Conference paper · Hanzhuo Tan et al.

  </details>

- [**ReSym: Harnessing LLMs to Recover Variable and Data Structure Symbols from Stripped Binaries**](https://doi.org/10.1145/3658644.3670340) · **2024 · Conference paper**

  Combines two fine-tuned language models with Prolog-based cross-function reasoning to infer local-variable symbols and user-defined data structures from stripped-binary decompilation.

  [PDF](https://www.cs.purdue.edu/homes/lintan/publications/resym-ccs24.pdf) · [Code](https://github.com/lt-asset/resym)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The method depends on underlying decompilation and learned predictions over C/C++ data. Cross-checking reduces conflicting predictions but does not prove that recovered names or layouts match the unavailable source. The public artifact includes models, processed data, and evaluation code.

  **Publication:** 2024 · ACM CCS 2024 · Conference paper · Danning Xie et al.

  </details>

- [**LLM4Decompile: Decompiling Binary Code with Large Language Models**](https://aclanthology.org/2024.emnlp-main.203/) · **2024 · Conference paper**

  Trains language models for assembly-to-C decompilation and for refining Ghidra pseudocode, evaluating whether recovered functions can be recompiled and executed correctly.

  [PDF](https://aclanthology.org/2024.emnlp-main.203.pdf) · [Code](https://github.com/albertan017/LLM4Decompile)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The paper limits its experiments to C on x86 and function-level benchmarks. Re-executability on sampled tests does not establish whole-program equivalence or recovery of the original source. Later repository releases are separate from the 2024 paper.

  **Publication:** 2024 · EMNLP 2024 · Conference paper · Hanzhuo Tan et al.

  </details>

- [**Augmenting Decompiler Output with Learned Variable Names and Types**](https://www.usenix.org/conference/usenixsecurity22/presentation/chen-qibin) · **2022 · Conference paper**

  Introduces DIRTY, a Transformer model that recommends variable names and types from decompiled code and layout information, together with the DIRT corpus for training and evaluation.

  [PDF](https://arxiv.org/pdf/2108.06363) · [Code](https://github.com/CMUSTRUDEL/DIRTY)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The original pipeline is built around C programs and Hex-Rays output. Predicted names and types are learned hypotheses, not guaranteed original symbols. The published paper is from 2022, although its arXiv preprint first appeared in 2021.

  **Publication:** 2022 · USENIX Security 2022 · Conference paper · Qibin Chen et al.

  </details>

- [**DIRE: A Neural Approach to Decompiled Identifier Naming**](https://doi.org/10.1109/ASE.2019.00064) · **2019 · Conference paper**

  Combines lexical and structural information from decompiler output to predict meaningful variable names, with a training and evaluation corpus derived from compiled C projects.

  [PDF](https://arxiv.org/pdf/1909.09029) · [Code](https://github.com/pcyin/dire)

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

  [PDF](https://raw.githubusercontent.com/mlresearch/v306/main/assets/he26n/he26n.pdf) · [Code](https://github.com/zai-org/Vision2Web)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The full-stack tier is specification-driven, not reconstruction solely by exploring a live website. Workflows test state management and CRUD outcomes, but finite agent judgments do not establish exact backend or durable-database equivalence. The current public evaluator maintains a browser session within each workflow and permits local business-API checks; this is not a universal persistence proof.

  **Publication:** 2026 · ICML 2026 · Conference paper · Zehai He et al.

  </details>

- [**ProgramDistill: From Interactive Web Apps to Verifiable Reference-Guided SWE Tasks**](https://arxiv.org/abs/2609.18805) · **2026 · Preprint**

  Evaluates recovery of web-app behavior from a live reference with hidden source. It provides 4,063 feature-restoration tasks across 26 applications and a separate 12-application reconstruction setting, scored by replaying dependent browser workflows.

  [PDF](https://arxiv.org/pdf/2609.18805v1) · [Code](https://huggingface.co/datasets/microsoft/ProgramDistill)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Tests cover finite, model-mined behaviors in self-contained apps, including SaaS clones. Persistence failures can be detected through replayed workflows, but passing does not establish all backend or database invariants. Evaluated agents receive structured browser observations without screenshots; visual fidelity is not measured. Public verifiers and reference solutions are not a contamination-resistant test set.

  **Publication:** 2026 · arXiv · Preprint · Jeonghye Kim et al.

  </details>

- [**UI2App: Benchmarking Visual Interaction Inference in Executable Web Application Generation**](https://arxiv.org/abs/2607.06306) · **2026 · Preprint**

  UI2App evaluates runnable React/TypeScript applications generated from 600 screenshots across 95 web applications. It separates build executability, visual fidelity and screenshot-implied interaction behavior, including cross-route state, using a reference interaction taxonomy and public evaluation pipeline.

  [PDF](https://arxiv.org/pdf/2607.06306v2) · [Code](https://github.com/chenmancm169/UI2App)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Static screenshots underdetermine behavior; the rubric accepts multiple valid implementations rather than proving equivalence to the original application or backend. Auto IIS judges generated source and screenshots without tool execution; human runtime validation covers a 45-application subset. Cross-route state is not necessarily durable persistence across reloads or sessions. Main results use one generation per application-model pair, with repeated runs on a subset.

  **Publication:** 2026 · arXiv · Preprint · Grace Man Chen et al.

  </details>

- [**Dashboard2Code: Evaluating Multimodal Models on Reconstructing Interactive Dashboards**](https://aclanthology.org/2026.acl-long.1750/) · **2026 · Conference paper**

  Evaluates agents that actively explore a running dashboard and reconstruct its appearance and interaction logic. DashboardMimic provides 180 Plotly+Dash examples, with code-semantic analysis and dynamic interaction tests for the generated implementations.

  [PDF](https://aclanthology.org/2026.acl-long.1750.pdf) · [Code](https://github.com/nth2000/Dashboard2Code)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Limited to Plotly+Dash dashboards, including model-augmented examples. Some settings expose DOM information and evaluation uses model judges. This is not a general backend-recovery benchmark. The linked dataset requires accepting access conditions and sharing contact information.

  **Publication:** 2026 · ACL 2026 · Conference paper · Tianhao Niu et al.

  </details>

- [**IWR-Bench: Can LVLMs reconstruct interactive webpage from a user interaction video?**](https://proceedings.iclr.cc/paper_files/paper/2026/hash/55bfedfd31489e5ae83c9ce8eec7b0e1-Abstract-Conference.html) · **2026 · Conference paper**

  Tests reconstruction of interactive webpages from user-interaction videos and supplied static assets. Its 113 tasks replay annotated action sequences to assess visual fidelity and functional behavior across observed page states.

  [PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/55bfedfd31489e5ae83c9ce8eec7b0e1-Paper-Conference.pdf) · [Code](https://github.com/SIGMME/IWR-Bench)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The required output is one HTML file; the paper explicitly instructs models to mock implied backend logic with static JavaScript data. Trajectory coverage and model-based judgments do not prove complete website or backend equivalence.

  **Publication:** 2026 · ICLR 2026 · Conference paper · Yang Chen et al.

  </details>

- [**Interaction2Code: Benchmarking MLLM-based Interactive Webpage Code Generation from Interactive Prototyping**](https://doi.org/10.1109/ASE63991.2025.00028) · **2025 · Conference paper**

  Benchmarks reconstruction of interactive webpages from screenshots before and after an interaction. The final study covers 127 webpages and 374 interactions, comparing rendered appearance, automated interaction checks, and human usability judgments.

  [PDF](https://arxiv.org/pdf/2411.03292v3) · [Code](https://github.com/WebPAI/Interaction2Code)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The inputs specify individual interaction transitions, not autonomous exploration of a complete site. Its tests do not establish long-workflow, server-side, or original-source equivalence; a detectable interaction is not necessarily usable.

  **Publication:** 2025 · ASE 2025 · Conference paper · Jingyu Xiao et al.

  </details>

- [**WebUIBench: A Comprehensive Benchmark for Evaluating Multimodal Large Language Models in WebUI-to-Code**](https://aclanthology.org/2025.findings-acl.815/) · **2025 · Conference paper**

  Diagnoses webpage-to-code capability through visual perception, HTML programming, image-to-HTML understanding, and screenshot reconstruction tasks. It separates underlying skills using question-answer pairs derived from real websites.

  [PDF](https://aclanthology.org/2025.findings-acl.815.pdf)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Primarily evaluates visual and HTML reconstruction skills. The paper includes a preliminary interaction study, not a full workflow or backend-equivalence benchmark. The official repository currently exposes README and images but not the evaluation scripts described in its instructions.

  **Publication:** 2025 · Findings of ACL 2025 · Conference paper · Zhiyu Lin et al.

  </details>

- [**Design2Code: Benchmarking Multimodal Code Generation for Automated Front-End Engineering**](https://aclanthology.org/2025.naacl-long.199/) · **2025 · Conference paper**

  Evaluates reconstruction of frontend code from webpage screenshots using real-world reference pages, visual-element and layout metrics, and human assessment.

  [PDF](https://aclanthology.org/2025.naacl-long.199.pdf) · [Code](https://github.com/NoviScl/Design2Code)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** This is visual website reconstruction, not binary decompilation or recovery of backend behavior and interactive workflows. The main benchmark contains 484 webpages with placeholder images; code and data have separate licensing terms.

  **Publication:** 2025 · NAACL 2025 · Conference paper · Chenglei Si et al.

  </details>

<a id="papers-game-reconstruction"></a>
### Game reconstruction and reverse engineering

[↑ Paper topics](#papers) · [Contents](#contents)

- [**GameReplica: A Benchmark for Black-Box Visual Game Replication by Vision-Language Agents**](https://arxiv.org/abs/2609.22308) · **2026 · Preprint**

  Evaluates whether vision-language agents can infer hidden game rules through screenshots and active interaction, then build runnable single-file HTML replicas across 125 tasks from 25 web games, each with five difficulty levels.

  [PDF](https://arxiv.org/pdf/2609.22308v1)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The tasks cover rule-driven web puzzles and board games, not native or commercial game reconstruction. Rule, implementation, and visual scores use LLM judges and do not prove behavioral equivalence. The official site provides demos; a benchmark-code repository was not verified.

  **Publication:** 2026 · arXiv · Preprint · Boyu Qiao et al.

  </details>

- [**Tycho: Active Abstraction with Programmatic World Models for ARC-AGI-3**](https://arxiv.org/abs/2607.28287) · **2026 · Preprint**

  Tycho constructs editable Python models of game state, transitions, rendering and outcomes from action/observation histories in unfamiliar ARC-AGI-3 games. It checks model predictions against recorded transitions and can use, repair or bypass these models during planning.

  [PDF](https://arxiv.org/pdf/2607.28287v1) · [Code](https://github.com/NIMI-research/Tycho)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Evaluation uses one stochastic run per configuration on 25 public games and 183 levels; five games informed harness development. Models may abstain on cells or accept bounded rendering variants. Transition replay and game scores do not establish complete engine reconstruction, correct objectives, unseen-state fidelity, unseen-game generalization or run-to-run reliability; the agent can bypass modeling.

  **Publication:** 2026 · arXiv · Preprint · Jens Lehmann et al.

  </details>

- [**RevengeBench: Reverse Engineering Code-Space Policies from Behavioral Experiments**](https://arxiv.org/abs/2606.26094) · **2026 · Preprint**

  Tests whether agents can recover executable decision policies from behavioral traces and self-designed opponent probes, using 75 synthetic policies across five game arenas and measuring held-out action agreement and downstream competitive value.

  [PDF](https://arxiv.org/pdf/2606.26094v1) · [Code](https://github.com/bethgelab/revenge-bench)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The targets are fixed synthetic policies, not full games or adaptive adversaries. Agreement on finitely evaluated states does not uniquely identify source code, and some arenas have substantial variance. The public package omits some paper-only plotting and ablation suites; reproduction also needs CodeClash, a container runtime, and model access.

  **Publication:** 2026 · arXiv · Preprint · Babak Rahmani et al.

  </details>

- [**SPRITE: From Static Mockups to Engine-Ready Game UI**](https://doi.org/10.1145/3772363.3798742) · **2026 · Conference paper**

  Transforms game-interface screenshots into editable engine assets through hierarchical YAML, visual grounding, asset extraction, and Unity UXML/USS synthesis, with evaluation on a curated game-UI benchmark and review by three senior UI/UX designers.

  [PDF](https://baiyunshu.github.io/sprite.github.io/Source/chiea26-516.pdf)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The generated interactions cover basic hover, toggle, and click behavior. Complex temporal and drag-and-drop logic remain outside scope, and translucent overlap or ambiguous diegetic layouts can fail. This is game-UI prototyping, not complete gameplay reconstruction; the official page still labels code as coming soon.

  **Publication:** 2026 · CHI EA 2026 (poster/extended abstract) · Conference paper · Yunshu Bai et al.

  </details>

- [**WorldCoder, a Model-Based LLM Agent: Building World Models by Writing Code and Interacting with the Environment**](https://papers.nips.cc/paper_files/paper/2024/hash/820c61a0cd419163ccbd2c33b268816e-Abstract-Conference.html) · **2024 · Conference paper**

  WorldCoder learns executable Python transition and reward models from environment interactions and natural-language goals. It refines code against recorded experiences and an optimistic planning constraint, studying transfer and task solving in Sokoban, MiniGrid and ALFWorld.

  [PDF](https://papers.neurips.cc/paper_files/paper/2024/file/820c61a0cd419163ccbd2c33b268816e-Paper-Conference.pdf) · [Code](https://github.com/haotang1995/WorldCoder)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Assumes deterministic dynamics and symbolic, discrete states rather than recovering a game from arbitrary pixels or binaries. Consistency with observed transitions and successful planning do not establish complete engine equivalence or correctness on every unseen state. Evaluation concerns bounded environment models and planning, not original source or asset recovery.

  **Publication:** 2024 · NeurIPS 2024 · Conference paper · Hao Tang et al.

  </details>

<a id="papers-app-reconstruction"></a>
### App reconstruction and analysis

[↑ Paper topics](#papers) · [Contents](#contents)

- [**DeclarUI: Bridging Design and Development with Automated Declarative UI Code Generation**](https://doi.org/10.1145/3715726) · **2025 · Journal article**

  Combines visual component extraction, multimodal models, page-transition graphs and iterative checks to reconstruct multi-page mobile UI code from designs or screenshots, evaluated with React Native, Flutter and ArkUI.

  [PDF](https://xinyi-hou.github.io/files/zhou2024bridging.pdf) · [Code](https://github.com/security-pride/DeclarUI)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** People review and correct the inferred navigation graph. Evaluation covers 50 five-page UI sets; transition coverage and compilation do not establish full business-logic or backend recovery. Framework results vary, and visual metrics imperfectly reflect perceived fidelity. Public scripts and data are available, but no project-level license was found at the reviewed commit.

  **Publication:** 2025 · Proceedings of the ACM on Software Engineering · Journal article · Ting Zhou et al.

  </details>

- [**Machine Learning-Based Prototyping of Graphical User Interfaces for Mobile Apps**](https://doi.org/10.1109/TSE.2018.2844788) · **2020 · Journal article**

  ReDraw turns screenshots or design mock-ups into native Android GUI prototypes by detecting components, classifying widget types with a CNN, and assembling a plausible view hierarchy with a data-driven nearest-neighbor method.

  [PDF](https://arxiv.org/pdf/1802.02312v2)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The implementation covers 15 Android component classes and one screen at a time; multiple screens require manual combination, and hierarchy construction is tied to the mined screen size. Evaluation concerns appearance and view hierarchy, not recovery of original app logic or backends. Screenshots and reconstructed mock-ups served as proxies for real design artifacts; results were not independently reproduced here.

  **Publication:** 2020 · IEEE Transactions on Software Engineering · Journal article · Kevin Moran et al.

  </details>

- [**pix2code: Generating Code from a Graphical User Interface Screenshot**](https://doi.org/10.1145/3220134.3220135) · **2018 · Conference paper**

  Learns screenshot-to-DSL generation for native Android XML, iOS Storyboards and web HTML/CSS interfaces, then compiles the DSL into platform UI code.

  [PDF](https://arxiv.org/pdf/1705.07962v2) · [Code](https://github.com/tonybeltramelli/pix2code)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Evaluation uses synthetic screenshot/code pairs: 1,500 training and 250 test instances per platform. Reported accuracy concerns DSL tokens, not complete apps or behavior. Text labels are ignored; platform datasets train separate models using the same architecture. The task covers layout, components and relationships, not application logic or backend recovery. The repository describes an educational research prototype; its older dependencies were not runtime-tested.

  **Publication:** 2018 · EICS 2018 · Conference paper · Tony Beltramelli

  </details>

- [**From UI Design Image to GUI Skeleton: A Neural Machine Translator to Bootstrap Mobile GUI Implementation**](https://doi.org/10.1145/3180155.3180240) · **2018 · Conference paper**

  UI2code translates a mobile UI image into an Android component hierarchy and layout skeleton using a neural encoder-decoder. The paper evaluates structural prediction and a small developer study of implementing layouts from generated skeletons.

  [PDF](https://chunyang-chen.github.io/publication/ui2code.pdf) · [Code](https://github.com/ccywch/UI2code)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The output covers component types and hierarchy from a single image; detailed styling and text require developer work. Structural token accuracy and an eight-participant study on five screenshots do not establish complete visual fidelity, navigation, app logic or backend recovery. The main split is screenshot-based; a separate evaluation on 1,208 images from 20 unseen apps provides limited generalization evidence.

  **Publication:** 2018 · ICSE 2018 · Conference paper · Chunyang Chen et al.

  </details>

- [**Reverse Engineering Mobile Application User Interfaces with REMAUI (T)**](https://ieeexplore.ieee.org/abstract/document/7372013) · **2015 · Conference paper**

  Reconstructs native Android UI code from screenshots or design bitmaps using OCR, computer vision, and layout heuristics; evaluates visual similarity and view hierarchies on 488 screenshots from over 100 Android and iOS applications.

  [PDF](https://c.csallner.org/papers/nguyen15reverse.pdf) · [Code](https://github.com/soumikmohianuta/pixtoapp)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The output is Android UI code; iOS screenshots are inputs, not evidence of native iOS output. Original logic and backend behavior are not recovered, and multi-screen transitions were future work. OCR/layout heuristics can misidentify content. The linked REMAUI v2 repository has older dependencies and is not the exact verified 2015 artifact.

  **Publication:** 2015 · ASE 2015 · Conference paper · Tuan Anh Nguyen et al.

  </details>

<a id="papers-firmware-analysis"></a>
### Firmware analysis and rehosting

[↑ Paper topics](#papers) · [Contents](#contents)

- [**Fuzzware: Using Precise MMIO Modeling for Effective Firmware Fuzzing**](https://www.usenix.org/conference/usenixsecurity22/presentation/scharnowski) · **2022 · Conference paper**

  Rehosts monolithic ARM Cortex-M firmware for fuzzing, using locally scoped symbolic execution to model memory-mapped I/O accesses and focus input mutations on values relevant to firmware logic.

  [PDF](https://www.usenix.org/system/files/sec22-scharnowski.pdf) · [Code](https://github.com/fuzzware-fuzzer/fuzzware)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The Cortex-M3/M4 artifact requires memory-map configuration and does not automatically model DMA. Abstracting hardware can produce crashes that are impossible on the physical device. This is an analysis environment, not original-source recovery or faithful full-device reconstruction.

  **Publication:** 2022 · USENIX Security 2022 · Conference paper · Tobias Scharnowski et al.

  </details>

- [**FirmAE: Towards Large-Scale Emulation of IoT Firmware for Dynamic Analysis**](https://doi.org/10.1145/3427228.3427294) · **2020 · Conference paper**

  Extends Firmadyne with empirically derived interventions for boot, networking, NVRAM, kernel behavior, and other runtime failures, enabling Linux router and IP-camera firmware web services to run for dynamic analysis.

  [PDF](https://syssec.kaist.ac.kr/pub/2020/kim_acsac2020.pdf) · [Code](https://github.com/pr0v3rbs/FirmAE)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Arbitration deliberately changes execution and targets functioning web interfaces, not identical physical-device behavior. The evaluation covers ARM little-endian and MIPS little-/big-endian firmware from routers and IP cameras; heuristics may fail on unseen devices or configurations. It reuses firmware binaries rather than recovering their source.

  **Publication:** 2020 · ACSAC 2020 · Conference paper · Mingeun Kim et al.

  </details>

<a id="papers-protocol-analysis"></a>
### Protocol inference and analysis

[↑ Paper topics](#papers) · [Contents](#contents)

- [**NetPlier: Probabilistic Network Protocol Reverse Engineering from Message Traces**](https://www.ndss-symposium.org/ndss-paper/netplier-probabilistic-network-protocol-reverse-engineering-from-message-traces/) · **2021 · Conference paper**

  Uses multiple sequence alignment and probabilistic keyword-field inference to cluster network messages by type, evaluated across ten protocols with downstream format and state-machine analysis.

  [PDF](https://www.ndss-symposium.org/wp-content/uploads/ndss2021_4A-5_24531_paper.pdf) · [Code](https://github.com/yapengye/NetPlier)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Requires unencrypted traces and cannot recover unseen message types. Larger alignments, sub-byte keywords and one-way traffic can reduce accuracy. Format/FSM inference is downstream evaluation rather than the main contribution; state semantics in a case study were manually annotated. These models do not establish complete application/device reconstruction.

  **Publication:** 2021 · NDSS 2021 · Conference paper · Yapeng Ye et al.

  </details>

- [**NEMESYS: Network Message Syntax Reverse Engineering by Analysis of the Intrinsic Structure of Individual Messages**](https://www.usenix.org/conference/woot18/presentation/kleber) · **2018 · Conference paper**

  Infers approximate field boundaries within individual binary-protocol messages from changes in bit congruence, and introduces Format Match Score to compare inferred segmentation with known protocol dissectors.

  [PDF](https://www.usenix.org/system/files/conference/woot18/woot18-paper-kleber.pdf) · [Code](https://github.com/vs-uulm/nemesys)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Requires plaintext payloads. Evaluation covers DNS, DHCP and NTP with protocol-tuned parameters. Single-byte fields are not inferred; zero-filled fields, character sequences and pseudo-random values can cause errors. FMS needs known field boundaries for validation. The output is approximate segmentation, not field semantics, a state machine or complete application/device behavior.

  **Publication:** 2018 · 12th USENIX Workshop on Offensive Technologies (WOOT 18) · Conference paper · Stephan Kleber et al.

  </details>
<!-- END GENERATED PAPERS -->

<a id="search-the-catalog"></a>
## Full Repository Index

<!-- BEGIN REPOSITORY INDEX SUMMARY -->
**3,000** repository READMEs scanned; **2,846** entries available to browse. The 154 clearly out-of-scope entries remain in the scan data. This automatically discovered index is separate from the curated resources above and has not been individually execution-tested.

[Browse by category on GitHub](docs/repositories/README.md) · [Search website](https://awesomerea.org/?view=source-index&lang=en) · [Full bilingual index JSON](https://awesomerea.org/source-index.json) · [Curated catalog JSON](https://awesomerea.org/catalog.json)
<!-- END REPOSITORY INDEX SUMMARY -->

The resource list above is curated from primary sources. Detailed requirements, original evidence, and review dates are available in the [catalog data](data/README.md).

## Contributing

Help improve an entry or share a useful source. Start with the [contribution guide](CONTRIBUTING.md), then [suggest a resource](https://github.com/reacher-z/Awesome-REA/issues/new?template=resource.yml), [recommend a paper](https://github.com/reacher-z/Awesome-REA/issues/new?template=paper.yml), [correct a translation](https://github.com/reacher-z/Awesome-REA/issues/new?template=translation.yml) or [report an outdated entry](https://github.com/reacher-z/Awesome-REA/issues/new?template=broken-resource.yml).

## Contributors

[Yuxuan Zhang](https://yuxuan.world/) — **Lead**.

[Haozhe Wang](https://haozheh3.github.io/) — Game reconstruction resource collection: [awesome-rea-games](https://github.com/HaozheH3/awesome-rea-games).

## About

This is an independent community collection. Original descriptions and code are [MIT licensed](LICENSE); linked projects retain their own licenses.

To cite the collection itself, use its [citation metadata](CITATION.cff). Cite listed papers, tools and other works from their own primary sources, and give the commit or snapshot date with any scan-derived counts.

For AI-built software and agent training or evaluation resources, explore [AI Can What?](https://aicanwhat.com/) across games, websites and applications.

---

[Catalog format](data/README.md) · [Scan methodology](docs/source-scan.md) · [Build status](https://github.com/reacher-z/Awesome-REA/actions/workflows/validate.yml) · [Back to top](#awesome-reverse-engineering-anything)
