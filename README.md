<p align="center">
  <a href="https://awesomerea.org/"><img src="assets/featured-by-awesome-rea-compact.svg" alt="Featured by Awesome REA" width="200" height="48"></a>
</p>

# Awesome Reverse Engineering Anything

An independent collection of tools, case studies and research for websites, games, apps, native binaries, firmware and communication protocols.

**English** · [简体中文](README.zh-CN.md)

<a href="https://awesomerea.org/"><img src="assets/readme-banner.svg" alt="Awesome Reverse Engineering Anything — tools, cases and papers across six reverse-engineering domains" width="960"></a>

<!-- BEGIN GENERATED BADGES -->
[![resources: 472](https://img.shields.io/badge/resources-472-53309C?style=flat-square&labelColor=303447)](https://awesomerea.org/resources/) [![cases: 195](https://img.shields.io/badge/cases-195-53309C?style=flat-square&labelColor=303447)](https://awesomerea.org/cases/) [![papers: 87](https://img.shields.io/badge/papers-87-53309C?style=flat-square&labelColor=303447)](https://awesomerea.org/papers/) [![Catalog checks](https://github.com/reacher-z/Awesome-REA/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/reacher-z/Awesome-REA/actions/workflows/validate.yml) [![license: MIT](https://img.shields.io/badge/license-MIT-606779?style=flat-square&labelColor=303447)](LICENSE) [![website: awesomerea.org](https://img.shields.io/badge/website-awesomerea.org-6235B5?style=flat-square&labelColor=303447)](https://awesomerea.org/)
<!-- END GENERATED BADGES -->

**[Search & filter](https://awesomerea.org/)** · **[Browse cases](https://awesomerea.org/cases/)** · **[Research papers](https://awesomerea.org/papers/)** · **[HTML survey](https://awesomerea.org/survey/)**

**Source review does not imply runtime verification.** [Review method](https://awesomerea.org/about/)

## Contents

<!-- BEGIN GENERATED CONTENTS -->
**Tools and cases by target**

- [Website](#website) (27) · [Game](#game) (185) · [App](#app) (72)
- [Native Binary](#native-binary) (63) · [Firmware and Hardware](#firmware) (22) · [Protocol](#protocol) (18)

**Research and workflows**

- [Papers](#papers) (87) · [Agents and MCP](#agents-and-mcp) (44) · [References and Learning](#references-and-learning) (32)

**More ways to browse**

- [All cases](https://awesomerea.org/cases/) (195) · [Related Collections](#related-collections) (6) · [Full Repository Index](#full-repository-index) (2,836)
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
**Tags:** Official REA: published by the REA project · Community REA: third-party REA work · REA maintainer: an REA maintainer's list · Independent MCP, Independent agent, Independent reconstruction: no established REA connection · Mixed workflow: REA plus other tools, per the author · Android, .NET, JVM, WebAssembly: platform · Library: code library · type only: foundation tool or learning resource.

<a id="website"></a>
### Website

[↑ Contents](#contents)

#### Case studies

- [**Dinosaur runner: recovering one acceleration rule**](https://github.com/morluto/rea/blob/c360cfcd6d7901514b16dd6113eba2e0b0fdf422/website/evidence/calculator-and-dino.md#dinosaur-speed)

  REA’s documented teaching case inspects the HTTP t-rex-runner edition and reconstructs its speed-update rule. A separate controlled original-game check and a new demonstration compare update counts, including the floating-point step that crosses the nominal speed threshold.

  Case study · Official REA · Also: Game · [Requirements & evidence](https://awesomerea.org/resources/rea-dinosaur-speed-case/)

- [**rauchg.com: rebuilding an RSC blog from captured Flight output**](https://github.com/boyang-hu/website-rebuild-skill/blob/ac60c9d8a2ab40045a89b5403c3457f1404e92b3/skills/website-rebuild/references/rsc-reconstruction.md)

  Documents a website-rebuild-skill case that decodes browser-delivered React Server Component Flight streams, reconstructs a buildable Next project and compares its output with a captured site. The reported rauchg.com campaign uses route-tree comparison and module-reference mapping; the new server source is inferred from observable output.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/rauchg-rsc-reconstruction-case/)

- [**BaoCut Slides: adapting an interactive web editor**](https://github.com/JimLiu/baocut/tree/b8585e0c8d7a82bdee9f0ed019cf6edb075e41c1/packages/slides-runtime)

  Documents BaoCut’s interactive slide editor, whose author says the implementation draws on Claude Slides. It adds a local deck store, HTML/CSS compiler and annotation-to-agent bridge for browser and desktop hosts; the design reports a Web-flow check, without establishing original backend recovery or full behavioral parity.

  Case study · Independent reconstruction · Also: App · [Requirements & evidence](https://awesomerea.org/resources/baocut-slides-editor-case/)

- [**REA in Claude Code: an isolated static-analysis A/B trial**](https://zenn.dev/keigoly/articles/8738d8d241b5a1)

  A Japanese field report connects REA 6.4.0 to Claude Code in a separate project directory, denies 43 of its 170 tools and common shell launch forms, and compares REA-enabled and REA-disabled runs on two real tasks: an Electron terminal’s packaged files and a saved HAR capture. Both arms answered correctly, while the REA arm took up to 2.00× the time and 1.67× the API-equivalent cost. It is an analysis-evaluation and safety-configuration case, not a reconstruction.

  Case study · Mixed workflow · Also: App · [Requirements & evidence](https://awesomerea.org/resources/rea-claude-code-isolated-ab-case/)

- [**Dinosaur runner: an REA-inspected speed rule rebuilt with Codex**](https://github.com/zhxunzh84/rea-dino-reverse-engineering)

  The author uses REA’s MCP browser tools to passively capture the JavaScript loaded by wayou’s open-source T-Rex Runner page, then has Codex rebuild its acceleration rule in one self-contained HTML5 Canvas game. The report identifies the captured script by SHA-256 and separates verified source facts from reconstruction choices; only the speed rule is claimed, not full gameplay equivalence.

  Case study · Mixed workflow · Also: Game · [Requirements & evidence](https://awesomerea.org/resources/rea-dino-runner-community-case/)

- [**BaoCut Design: porting reconstructed canvas and design-system editors**](https://github.com/JimLiu/baocut/tree/7aa049e82e1367da013b7aba80f0b79033fa04ad/packages/design-runtime)

  Documents BaoCut’s design-canvas and design-system editors, which the project says it ported 1:1 from TypeScript reconstructions of Claude Design’s editors and hosts in agent sessions with annotation and export. Its runtime notes record identifier fixes checked against the original scripts and a structural comparison matching 19,111 of 20,463 canvas main-page functions. Unreviewed differences, the unpublished reconstruction record and reuse rights remain open; no hosted-backend recovery is claimed.

  Case study · Independent reconstruction · Also: App · [Requirements & evidence](https://awesomerea.org/resources/baocut-design-canvas-case/)

- [**whatsapp-web-reveng: documenting the legacy WhatsApp Web protocol**](https://github.com/sigalor/whatsapp-web-reveng)

  Documents and reimplements the WebSocket protocol WhatsApp Web used while browser sessions mirrored a paired phone: QR pairing, Curve25519/HKDF key setup, AES/HMAC-protected binary messages, the token-based node encoding and end-to-end media encryption. A Python backend, Node.js relay and browser front end decode a logged-in session’s messages into inspectable JSON, and the README lists independent reimplementations such as Baileys and go-whatsapp. This is an older protocol generation from before WhatsApp’s 2021 multi-device architecture, not a description of current WhatsApp Web.

  Case study · Independent reconstruction · Also: Protocol · [Requirements & evidence](https://awesomerea.org/resources/whatsapp-web-reveng-legacy-protocol-case/)

- [**Ruffle: a Rust reimplementation of Adobe Flash Player**](https://github.com/ruffle-rs/ruffle)

  Reimplements Adobe Flash Player in Rust so that SWF content, from ActionScript 1/2 (AVM1) to ActionScript 3 (AVM2), runs in a native desktop player or in browsers through WebAssembly, as a self-hosted script or a browser extension. Its contributor guide says behavior comes from observing Flash Player's output or from license-compatible sources such as Adobe's open avmplus code, and forbids decompiling Flash Player, Flash Professional or Animate. Regression tests run contributor-made SWFs and compare their trace output, and optionally rendered images, with captures from the official debug Flash Player.

  Case study · Independent reconstruction · Also: Game · [Requirements & evidence](https://awesomerea.org/resources/ruffle-flash-player-case/)

#### Tools, projects and integrations

- [**webcrack**](https://github.com/j4k0xb/webcrack)

  Improves JavaScript readability by reversing supported obfuscation patterns and unpacking webpack/Browserify bundles.

  Tool · Also: App · [Requirements & evidence](https://awesomerea.org/resources/webcrack/)

- [**humanify**](https://github.com/jehna/humanify)

  Rename identifiers in minified JavaScript with LLM-suggested names, applied through scope-aware AST rewriting so the program structure stays unchanged. The new names are model suggestions, not recovered original identifiers.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/humanify/)

- [**WABT**](https://github.com/WebAssembly/wabt)

  WebAssembly tools for binary-to-text conversion, section inspection, validation, interpretation and C translation.

  Tool · WebAssembly · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/wabt/)

- [**wasm-tools**](https://github.com/bytecodealliance/wasm-tools)

  Bytecode Alliance CLI and Rust libraries for inspecting WebAssembly modules, metadata, components and WIT interfaces.

  Tool · WebAssembly · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/wasm-tools/)

- [**Chrome DevTools MCP**](https://github.com/ChromeDevTools/chrome-devtools-mcp)

  Connect an agent to Chrome for live page inspection, network debugging, and performance traces.

  Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/chrome-devtools-mcp/)

- [**mitmproxy**](https://github.com/mitmproxy/mitmproxy)

  Inspect and record HTTP traffic with an interactive proxy, web interface, or scriptable command-line tools.

  Tool · Also: App, Protocol · [Requirements & evidence](https://awesomerea.org/resources/mitmproxy/)

- [**Playwright MCP**](https://github.com/microsoft/playwright-mcp)

  Drive browser interactions through structured accessibility snapshots to investigate reproducible web behavior.

  Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/playwright-mcp/)

- [**Burp Suite MCP Server**](https://github.com/PortSwigger/mcp-server)

  PortSwigger's Burp Suite extension serves an MCP endpoint, plus a packaged stdio proxy, so agents can query proxy HTTP and WebSocket history, send HTTP/1.1 or HTTP/2 requests, and open Repeater or Intruder tabs.

  Integration · Independent MCP · Also: App · [Requirements & evidence](https://awesomerea.org/resources/burp-suite-mcp-server/)

- [**Wakaru**](https://github.com/pionxzh/wakaru)

  Recover readable modules from shipped JavaScript bundles by reversing recognized minifier and transpiler patterns. Supports bundle splitting and modern-syntax recovery for inspecting production frontend code.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/wakaru/)

- [**Spectral**](https://github.com/spectral-mcp/spectral)

  Analyze captured application HTTP traffic with an LLM to generate MCP tools, OpenAPI 3.1 specifications, or GraphQL schemas. Generated tools call the observed API directly after capture and authentication setup.

  Integration · Independent agent · Also: App, Protocol · [Requirements & evidence](https://awesomerea.org/resources/spectral-mcp/)

- [**jsdeob-workbench**](https://github.com/Owl4444/jsdeob-workbench)

  Inspect JavaScript ASTs and variable scopes while building visual chains of Babel transforms. Save analysis projects and reusable plugins to iteratively simplify obfuscated scripts.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/jsdeob-workbench/)

- [**Browser Reverse Engineering Toolkit**](https://github.com/Dvurechensky/Browser.Reverse.Engineering.Toolkit)

  Capture browser-session evidence, crawl websites in a persistent Chromium session, and generate offline architecture/API reports plus OpenAPI, SDK and mock-server drafts from saved captures.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/browser-reverse-engineering-toolkit/)

- [**screenshot-to-code**](https://github.com/abi/screenshot-to-code)

  Generate HTML/CSS, Tailwind, React, Vue, Bootstrap or Ionic front-end code from screenshots, mockups, Figma designs or screen recordings with multimodal models; an optional headless-browser preview lets the model check its rendered output. The result is a visual reconstruction of the interface, not recovered original source or backend behavior.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/screenshot-to-code/)

- [**Dembrandt**](https://github.com/dembrandt/dembrandt)

  Node.js CLI that renders a website in Playwright-driven Chromium or Firefox and reads computed styles from the DOM to extract its design system: logo, color roles with the evidence behind each pick, typography, spacing, borders, shadows, motion, breakpoints and component styles such as buttons and inputs. Results export as W3C design tokens (DTCG), Tailwind v4 or shadcn/ui themes, DESIGN.md, an HTML report or a brand-guide PDF, alongside WCAG contrast checks on real DOM pairs and a CI drift gate against a committed baseline. It also runs as an MCP server for agent clients.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/dembrandt/)

- [**shuji**](https://github.com/paazmaya/shuji)

  Command-line tool that writes the original JavaScript and CSS sources embedded in source maps back out as files. It reads .map files, or JavaScript and CSS files whose sourceMappingURL holds an inline Base64 or URL-encoded map or points to a map in the same folder, and can walk directories with a regular-expression filter. Output is flattened to file names by default, or keeps the map's folder structure with --preserve.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/shuji/)

- [**Obfuscator.io Deobfuscator**](https://github.com/ben-sb/obfuscator-io-deobfuscator)

  Deobfuscator dedicated to JavaScript produced by Obfuscator.io (javascript-obfuscator), which its README says also handles most forks. Working statically on a Babel AST, it reveals strings hidden in rotated, Base64- or RC4-encoded string arrays, inlines proxy functions, simplifies objects, arithmetic and string concatenation, removes dead code and the obfuscator's anti-tamper wrappers, and reverses control-flow flattening. Its configuration is detected automatically, and the author also hosts an online version.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/obfuscator-io-deobfuscator/)

- [**javascript-deobfuscator**](https://github.com/ben-sb/javascript-deobfuscator)

  General-purpose JavaScript deobfuscator for common obfuscation patterns, published on npm as js-deobfuscator and usable as a library or CLI. It unpacks arrays of literals and replaces references to them, removes simple, array and arithmetic proxy functions, simplifies arithmetic and string concatenation, removes dead branches, turns computed member access into static properties, renames hexadecimal identifiers such as \_0xca830a and beautifies the result. The author also hosts an online version and maintains a separate deobfuscator for Obfuscator.io output.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/ben-sb-javascript-deobfuscator/)

- [**mitmproxy2swagger**](https://github.com/alufers/mitmproxy2swagger)

  Command-line tool that reverse-engineers undocumented REST APIs from captured traffic. It reads a mitmproxy flow file, or a HAR export from the browser DevTools, and generates an OpenAPI 3.0 specification describing the observed endpoints. Running it again over further captures safely merges the new data into an existing schema.

  Tool · Also: Protocol · [Requirements & evidence](https://awesomerea.org/resources/mitmproxy2swagger/)

- [**JPEXS Free Flash Decompiler (FFDec)**](https://github.com/jindrapetrik/jpexs-decompiler)

  Java desktop decompiler and editor for Adobe Flash SWF files. It decompiles ActionScript 1/2 and AS3 side by side with the P-code they came from, edits scripts as source (experimental) or through the assembler view, and exports or replaces images, shapes, sounds, video, fonts and texts, with SWF-to-FLA conversion, SWF-to-XML round trips and SVG or HTML5 Canvas output. It also opens SWC and ABC files, Scaleform GFx and 64-bit Iggy files, has an ActionScript debugger and deobfuscation passes for obfuscated AS3, and offers its parser and decompiler as the ffdec\_lib Java library and a command line.

  Tool · Also: Game · [Requirements & evidence](https://awesomerea.org/resources/jpexs-decompiler/)

<a id="game"></a>
### Game

[↑ Contents](#contents)

#### Case studies

- [**DX-Ball: reconstruct sound panning**](https://rea.tools/showcase/dx-ball/)

  Recover one sound-pan function from instructions and constants; upstream cites 3,205 cases and a 63-byte match.

  Case study · Official REA · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/rea-dxball-case/)

- [**TH04: recover a DOS bullet-ring helper**](https://rea.tools/showcase/th04/)

  Inspect a 16-bit PC-98 DOS helper and relate its angle calculation to a pinned reconstruction and historical compiler checks.

  Case study · Official REA · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/rea-th04-case/)

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

  Case study · Official REA · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/rea-touhou-reconstruction-method-case/)

- [**TicTacToe-AI: a bounded REA-fork reconstruction of one game method**](https://github.com/heaven-hm/re-agent/tree/develop/benchmarks/tictactoe)

  The author’s REA fork, posted as rea-engine and since renamed RE-Agent, decompiles the shipped .NET executable of the GPL-licensed TicTacToe-AI game, recompiles the recovered C# and resources, and repairs one decompiler error against the original IL. A differential probe runs original and rebuilt code on all 19,683 board assignments for one status method and compares six form renders. The report passes only that method; the whole game remains partial.

  Case study · Mixed workflow · [Requirements & evidence](https://awesomerea.org/resources/rea-engine-tictactoe-case/)

- [**UltraSunnyMoon: a partial, REA-led Pokémon Ultra Sun reconstruction**](https://github.com/tylergraydev/UltraSunnyMoon)

  The author uses a pinned REA build with Ghidra to analyze a user-supplied Pokémon Ultra Sun base executable, rebuild it byte for byte from split objects, and swap in two small compiled C runtime routines. Both replacements are behavior-tested but nonmatching and every other byte stays original; one recorded input movie drives the original and hybrid builds to the same bedroom movement in the Azahar emulator. Retail compiler identity, exact matching, module loading and broader gameplay remain open.

  Case study · Mixed workflow · [Requirements & evidence](https://awesomerea.org/resources/ultrasunnymoon-rea-case/)

- [**DX-Ball: an REA-guided function-level reconstruction with Codex**](https://github.com/N0zoM1z0/dx-ball)

  The author has Codex use REA’s Ghidra tools to inspect the English DX-Ball 1.07 executable and recover it as typed C/C++, then compiles each function with the original-era Visual C++ 4.0 and compares it byte for byte with the original after mapping relocations. The same source also builds a MinGW Windows game and a portable core library. Exact reconstruction is still in progress; REA’s separate sound-pan showcase covers just one function.

  Case study · Mixed workflow · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/dx-ball-rea-reconstruction-case/)

- [**re2ds: a native Nintendo DS engine for Resident Evil 2**](https://github.com/eray1605/re2ds)

  Reimplements Resident Evil 2’s PS1 game rules in a native Nintendo DS engine, with converters that turn data from the user’s own disc into DS formats. A helper wraps the PS1 executable as an ELF for REA’s Ghidra lane, analysis notes name the PS1 functions and tables each part follows, and the Reddit post linking it credits REA and Claude Code. Leon’s disc 1 is reported playable, while Claire’s disc, most enemy types and some menus remain unfinished.

  Case study · Mixed workflow · [Requirements & evidence](https://awesomerea.org/resources/re2ds-nds-engine-case/)

- [**LASRecomp: Link’s Awakening static recompilation**](https://github.com/peiikai/LASRecomp)

  A native desktop reconstruction of the 2019 Switch version of Link’s Awakening using static recompilation. The author attributes most code, tooling and reverse-engineering work to Claude Code with human direction and review.

  Case study · Independent reconstruction · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/lasrecomp/)

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

  Case study · Independent reconstruction · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/dlssnr-amd-neural-rendering-case/)

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

- [**King Kong Recompiled: an AI-developed Xbox 360 static recompilation**](https://github.com/TekRantGaming/king-kong-recompiled)

  Translates the Xbox 360 release of Peter Jackson's King Kong into native Windows code with the ReXGlue static-recompilation SDK, adding a launcher and display, control and graphics options. Project code completes streamed disc reads the way the console does, which README credits with getting past an opening freeze seen under Xenia. The author discloses that the port was made almost entirely with Claude Code, directed and tested by the repository owner.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/king-kong-recompiled-case/)

- [**Mario Party 4: matching GameCube decompilation of the USA releases**](https://github.com/mariopartyrd/marioparty4)

  Reconstructs Mario Party 4’s GameCube main executable and REL modules as C source that rebuilds both USA releases. The build analyzes the user’s own disc image and checks every linked output against version-specific SHA-1 lists. PAL and Japanese work is stale and no PC port exists yet; matching results remain project-reported here.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/mario-party-4-decomp-case/)

- [**SpeedBreaker: statically recompiling Need for Speed: Most Wanted for Xbox 360**](https://github.com/SpeedBreakerProject/speedbreaker)

  Translates the Xbox 360 executable of Need for Speed: Most Wanted (2005) into native C++ with a patched XenonRecomp and runs it on a project runtime that stands in for the console’s kernel, Xenos GPU, XMA audio and controllers. Releases target SteamOS, Linux and Apple silicon Macs, with an experimental iPhone and iPad build, while all game data comes from the player’s own US disc. Rendering and frame-pacing improvements are project-reported.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/speedbreaker-nfs-most-wanted-case/)

- [**The Sims: Bustin' Out: an AI-driven partial GBA matching decompilation**](https://github.com/DaBrown95/tsbodp)

  Rebuilds the USA/Europe Game Boy Advance release of The Sims: Bustin' Out byte for byte while gradually replacing ROM regions with matching C compiled by agbcc. The README calls it an AI-driven experiment in which almost all code, analysis and tooling are AI-generated. Most of the ROM is still copied from the user’s dump, so whole-ROM equality does not mean the game has been decompiled.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/sims-bustin-out-gba-decomp-case/)

- [**Destiny 2 build 86657: Sunrise/Dawn reconstruction research report**](https://github.com/isinternets/d2-research)

  A dated research report on the Sunrise/Dawn reconstruction of the archived Destiny 2 build 86657 client, which emulates platform sign-on and the examined Bungie service contracts locally and adds reconstructed mission host policy. It records transport, decoding, object creation, presentation and gameplay results separately, and keeps superseded conclusions with their cited sources. It documents the case rather than shipping the runtime implementation or a recovered Bungie backend; playthroughs and native results remain project-reported.

  Case study · Independent reconstruction · Also: Protocol · [Requirements & evidence](https://awesomerea.org/resources/destiny2-build-86657-reconstruction-report-case/)

- [**SVR2011-Recomp: a ReXGlue recompilation of WWE SmackDown vs. Raw 2011**](https://github.com/shaneomac1337/SVR2011-Recomp)

  Translates the Xbox 360 executable of WWE SmackDown vs. Raw 2011 to C++ ahead of time with ReXGlue and builds it as a Windows program on a Vulkan runtime derived from Xenia. A hand-maintained manifest adds function entry points the automatic pass misses, and project patches address frame pacing, a music-player delay and pipeline stalls. Exhibition play is author-tested on one AMD GPU; career mode and online remain untested.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/svr2011-recomp-case/)

- [**Snap64 Recomp: a static-recompilation port of Pokémon Snap**](https://github.com/JackandBeans/Snap64Recomp)

  Uses N64Recomp to statically recompile the US Nintendo 64 release of Pokémon Snap into a native Windows, Linux, Steam Deck and macOS port rendered with RT64. The recompiler reads a relocatable ELF linked from the matching ethteck/pokemonsnap decompilation together with the user’s ROM, and game-side patches are modified copies of decompiled functions. The author reports building the port with Claude Code; results remain project-reported.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/snap64-recomp-case/)

- [**Dead Rising 2: Case Zero — an Xbox 360 XBLA static recompilation port**](https://github.com/wivi514/Dead_Rising_2_Case_Zero_Xenon_Recomp)

  Builds a native Windows, Linux, Steam Deck and Apple Silicon port of the XBLA game Dead Rising 2: Case Zero by statically recompiling its Xbox 360 code with patched XenonRecomp and translating its shaders with patched XenosRecomp. A purpose-built runtime supplies a Vulkan renderer, XMA audio, keyboard/mouse input and online co-op through the author’s XenonLive service. Completion and platform results are project-reported.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/dead-rising-2-case-zero-recomp-case/)

- [**OpenRA: an engine reimplementation reimagining early Westwood RTS games**](https://github.com/OpenRA/OpenRA)

  Provides a C# engine for early Westwood real-time strategy games, with mods that reimagine Command &amp; Conquer: Red Alert, Tiberian Dawn and Dune 2000. It loads the original games’ content through its own file-system, MiniYAML rules and Lua mission layers rather than running or recovering Westwood code. Gameplay and interface deliberately follow OpenRA’s own design, so it is not a faithful recreation of the original executables.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/openra-engine-case/)

- [**Dead Rising 2: Case West — a sibling Xbox 360 XBLA static recompilation port**](https://github.com/wivi514/Dead_Rising_2_Case_West_Xenon_Recomp)

  Builds a native Windows, Linux, Steam Deck and Apple Silicon port of the XBLA epilogue Dead Rising 2: Case West by statically recompiling its Xbox 360 code with patched XenonRecomp and translating its shaders with patched XenosRecomp. It shares most of its runtime with the author’s separate Case Zero port, executing the console GPU command stream on Vulkan with XMA audio and keyboard/mouse input. Completion and platform results are project-reported.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/dead-rising-2-case-west-recomp-case/)

- [**The Simpsons Wrestling Recompiled: a psxrecomp PlayStation static recompilation**](https://github.com/TekRantGaming/simpsons-wrestling-recompiled)

  Translates the PlayStation game’s MIPS code to C with a pinned psxrecomp fork and builds Windows and Linux programs on its hardware-modelling runtime, with a launcher and a game-specific plugin. Without patching game code, the plugin adds 16:9 matches, 60 FPS by raising the emulated CPU clock and rescaling movement, intro skipping and unlocks. The user’s own NTSC-U disc image is required, and the measurements are author-reported.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/simpsons-wrestling-recompiled-case/)

- [**OpenRCT2: an open re-implementation of RollerCoaster Tycoon 2**](https://github.com/OpenRCT2/OpenRCT2)

  Re-implements RollerCoaster Tycoon 2, originally written in x86 assembly, as a C++ engine that runs on the original game’s data. It loads RCT2 saves and scenarios, and RCT1 scenarios when those files are present, while saving to its own documented park format. Modern-platform support, interface and AI changes, higher limits and multiplayer are deliberate extensions, not reproductions of the original.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/openrct2-engine-case/)

- [**Touhou 6: reconstructing Embodiment of Scarlet Devil 1.02h source**](https://github.com/GensokyoClub/th06)

  Reconstructs C++ source for the Windows executable of Touhou 6: Embodiment of Scarlet Devil version 1.02h, aiming at an exact rebuild with the original Visual Studio .NET 2002 and DirectX 8 toolchain. reccmp and objdiff compare the rebuilt binary with the user’s original executable function by function. The committed progress badge reports every function implemented but 98.03% byte accuracy, so whole-binary identity is not claimed.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/th06-decomp-case/)

- [**Driver Recompiled: a psxrecomp setup host that builds the game locally**](https://github.com/alexbeavs-ps1-ports/driver-recomp)

  Packages a psxrecomp static-recompilation project for Driver (PlayStation, USA) as a setup host: releases carry the recompiler, runtime and a recomp-ui launcher, and the player’s machine generates and compiles the game from the user’s own disc image. The repository holds configuration, Ghidra-derived function seeds and release automation rather than game code. Its documented status is thin: an operator-confirmed private build reaches gameplay, while package release gates remain open.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/driver-recomp-setup-host-case/)

- [**Himuro: a matching Fatal Frame PS2 decompilation**](https://github.com/Mikompilation/Himuro)

  Reconstructs Fatal Frame’s PS2 executable as C for the US, EU and Japanese releases, built with the original EE-GCC 2.9 toolchain and checked by SHA-1 against the user’s own executables. Committed objdiff reports list the US and EU code as fully matched and the Japanese code as partial, and a few routines still rely on assembly or byte patches. Porting to modern hardware is a stated later goal, not part of this repository.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/himuro-fatal-frame-decomp-case/)

- [**DOAXVB Native PC Port: statically recompiling Dead or Alive Xtreme Beach Volleyball**](https://github.com/NoRain211/doaxvb-re)

  Lifts the original Xbox executable of Dead or Alive Xtreme Beach Volleyball to C with a fork of xboxrecomp and links it with a hand-written runtime that replaces kernel imports, audio and key Direct3D 8 and DirectSound APIs. Setup builds the runner locally from the user’s USA disc image and checks generated files against hashes in an authenticated recipe; releases carry only tools and source. Rewriting game logic as readable source has so far reached only the startup thread entry.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/doaxvb-native-port-case/)

- [**TH08 Web: a WebAssembly port built from reconstructed source**](https://github.com/N0zoM1z0/th08-web)

  Compiles the reconstructed C++ source of the Japanese Touhou 8 1.00d release to WebAssembly with Emscripten, adding WebGL 2 rendering, Web Audio, browser input and IndexedDB saves behind the game’s D3D8-, DirectSound- and DirectInput-shaped interfaces. Players select their own retail DAT files locally. The web build makes no binary-exact claim and is a separate port from the curated TH08 reconstruction.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/th08-web-wasm-port-case/)

- [**OpenXcom: an open-source clone of X-COM: UFO Defense and Terror from the Deep**](https://github.com/OpenXcom/OpenXcom)

  Reimplements MicroProse’s UFO: Enemy Unknown (X-COM: UFO Defense) and X-COM: Terror from the Deep as a C++/SDL engine that runs on the user’s original game resources. Game data such as items, craft, research and missions is expressed in YAML rulesets, which also carry its standard mods and a wider modding ecosystem. It is a clone that reuses original content, not recovered MicroProse code.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/openxcom-engine-case/)

- [**Skate 3 Recomp: a native Xbox 360 recompilation through ReXGlue**](https://github.com/mchughalex/skate3recomp)

  Recompiles the Xbox 360 version of Skate 3 into native Windows, Linux and macOS builds with a Skate-specific fork of the ReXGlue SDK. Since v2.0.0 a native Direct3D 12 and Vulkan renderer with ports of the game’s own material shading replaces emulation of the Xbox 360 GPU, which remains as a fallback. Game files come from the user’s disc image; the author calls the native renderer early and has not tested the game end to end.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/skate3-recomp-case/)

- [**Uncharted: The Nathan Drake Collection native Windows port**](https://github.com/bc160201983/Uncharted-The-Nathan-Drake-Collection-PC-port)

  Runs the PS4 Uncharted: The Nathan Drake Collection’s own x86-64 executables natively on Windows: a runtime supplies the PS4 system libraries and a shadPS4-derived Vulkan renderer executes the GPU work. The port adds a per-game launcher, resolution patches and modern upscaling, and its status table reports all three games playable with listed open issues. It is a compatibility-runtime port rather than a decompilation, and its results remain project-reported.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/uncharted-collection-pc-port-case/)

- [**TH095: function-level reconstruction of Shoot the Bullet 1.02a**](https://github.com/N0zoM1z0/th095)

  Reconstructs source for the original Japanese Touhou 9.5: Shoot the Bullet 1.02a executable, accepting function exactness only through reproducible byte comparison of pinned Visual C++ .NET 2003 builds against one hash-attested target. The whole program also compiles and links into a playable Windows i386 executable, while README keeps playability, function matching and whole-executable identity as separate statuses.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/th095-reconstruction-case/)

- [**CorsixTH: an open reimplementation of Theme Hospital**](https://github.com/CorsixTH/CorsixTH)

  Reimplements the engine of Bullfrog’s 1997 Theme Hospital, with game logic in Lua and C++ for graphics, sound, movies and pathfinding, on top of the original game’s data files. The README reports that the full campaign can be completed, lists features that are still missing, and adds extensions such as high resolutions and a map editor. It recreates the game’s behaviour on original content rather than recovering Bullfrog source code.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/corsixth-engine-case/)

- [**OpenRiseOfNations: a native macOS engine reimplementation**](https://github.com/ben-wright-1/OpenRiseOfNations)

  Reimplements the Rise of Nations: Extended Edition engine as a native macOS app with a Metal renderer, a deterministic simulation, a computer opponent and a compatible BigHugeScript compiler and virtual machine, loading art, maps, rules and scripts from the user’s own Windows installation. Subsystem specifications written from Ghidra study of the symbol-bearing executable, together with JavaScript reference tools, guided a C++17 implementation built with heavy Claude Code assistance. The alpha plays tutorials and scenarios, and its bit-exactness checks remain project-reported.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/openriseofnations-engine-case/)

- [**TH04: rebuilding Lotus Land Story’s four PC-98 programs from source**](https://github.com/N0zoM1z0/th04)

  Reconstructs source for the Japanese PC-98 Touhou 4: Lotus Land Story and rebuilds all four DOS programs, MAIN.EXE, OP.EXE, MAINE.EXE and ZUN.COM, with a pinned Borland toolchain under Wine. Function acceptance against the original binaries is tracked separately from emulator replays that compare inputs, RNG, object pools and video with the original game. Complete-campaign, original-timing and byte-identity goals remain open.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/th04-reconstruction-case/)

- [**inFAMOUS Second Son native PC port**](https://github.com/HayatoG/iss_pc)

  Runs the PS4 inFAMOUS Second Son’s own x86-64 code natively on Windows and Linux: a runtime reimplements the PS4 system libraries the game uses, and a shadPS4-derived core translates its GPU commands and shaders to Vulkan. The project reports a playable, in-development port that reaches gameplay and the first chapters, with unstable performance and remaining graphics glitches. It is a compatibility-runtime port rather than a decompilation, and its results remain project-reported.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/infamous-second-son-pc-port-case/)

- [**xoreos: an open reimplementation of BioWare’s Aurora engine family**](https://github.com/xoreos/xoreos)

  Reimplements BioWare’s Aurora engine and its later derivatives as a portable C++ engine that runs on the user’s installed game data, targeting nine games from Neverwinter Nights to Dragon Age II. Resource management, many Aurora file formats, graphics and sound are in place, and every target shows partial in-game areas in a free-flying spectator mode. README states that normal gameplay is not implemented yet, so this is an early-stage engine case, not a playable replacement.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/xoreos-aurora-engine-case/)

- [**librw: a re-implementation of the RenderWare Graphics engine**](https://github.com/aap/librw)

  Re-implements a large part of the RenderWare Graphics middleware API as a portable C++ library that reads and writes its DFF model and TXD texture files for PS2, D3D8, D3D9 and Xbox and is meant to convert them between platforms. Direct3D 9 and OpenGL backends render the scenes, while PS2 rendering works only as a test. README names rendering GTA as its use; BSP world files are not supported.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/librw-renderware-reimplementation-case/)

- [**Super Mario Odyssey: per-function matching decompilation of the Switch executable**](https://github.com/MonsterDruide1/OdysseyDecomp)

  Reconstructs C++ source for Super Mario Odyssey’s Switch 1.0 main executable and checks each function against the original AArch64 machine code with the shared nx-decomp-tools checker. At the pinned commit its function list marks 18,996 of 74,171 functions matching. The README warns that the build is not a playable game, the repository ships no game assets, and Nintendo libraries such as sead and agl come from open-ead’s separate reconstructions.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/odyssey-decomp-case/)

- [**Star Fox 64: a complete matching Nintendo 64 decompilation**](https://github.com/sonicdcer/sf64)

  Reconstructs C source for the US 1.1 (Rev A) Nintendo 64 release of Star Fox 64 that, compiled with the IDO compiler through a static recompilation, rebuilds a ROM with the published MD5; the README badge counts all 2,951 functions as matching. Code and assets are split from the user’s own ROM at build time, and the repository contains no assets or assembly. The separately curated Starship PC port compiles this C code, while Starfox 64: Recompiled takes headers and some functions from it for its patches.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/sf64-matching-decomp-case/)

- [**Metroid Prime: the PrimeDecomp matching GameCube decompilation**](https://github.com/PrimeDecomp/prime)

  Reconstructs C++ source for Metroid Prime’s GameCube executable and its NES-emulator module so that CodeWarrior builds match the originals, across the USA, Korean, PAL and Japanese releases, with early configurations for demo discs and three Wii releases. Matched units are compiled from source and linked with objects split from the user’s disc, then checked against per-version SHA-1 hashes; the repository contains no game assets or assembly. The separately curated Metaforce and Metroid Prime Port build their native ports on this code.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/primedecomp-metroid-prime-decomp-case/)

- [**Batla 3D server emulator (2015 client)**](https://github.com/Serega25511s/Batla-3D-server-emu)

  C# server emulator for the 2015 Steam client of Batla 3D, covering HTTP account, shop and room services and Lidgren UDP gameplay. It includes a client-assembly patcher and protocol notes that distinguish recovered client evidence from emulator rules.

  Case study · Independent reconstruction · Also: Protocol · [Requirements & evidence](https://awesomerea.org/resources/batla-3d-server-emulator-case/)

- [**RSDKv4 Decompilation: Retro Engine v4 and the Sonic 1 &amp; 2 (2013) menus**](https://github.com/RSDKModding/RSDKv4-Decompilation)

  Decompiles Retro Engine (RSDK) v4, the engine behind Sonic the Hedgehog and Sonic the Hedgehog 2 (2013), together with the games’ natively coded menus, and builds it for Windows, Linux and Android. The engine runs the game scripts contained in the official releases’ data files, which users must supply. The project adds a script compiler, a mod loader and an experimental online mode for Sonic 2’s 2P VS; it is the predecessor of the same group’s RSDKv5 decompilation.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/rsdkv4-sonic-1-2-decomp-case/)

- [**OpenRW: an open re-implementation of the Grand Theft Auto III engine**](https://github.com/rwengine/openrw)

  Re-implements Rockstar Games’ Grand Theft Auto III (2001) as a cross-platform C++ engine that runs on the data of a legitimate PC copy. It has its own loaders for the game’s RenderWare models, textures and archives, a script machine for the original mission scripts, and an optional Qt data viewer. Playability is partial: the project’s mission tracker marks six early Portland story missions as completable.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/openrw-gta3-engine-case/)

#### Tools, projects and integrations

- [**RenderDoc**](https://github.com/baldurk/renderdoc)

  Inspect frame captures, draw calls, shaders, and graphics resources in your own game or graphics application.

  Tool · Also: App · [Requirements & evidence](https://awesomerea.org/resources/renderdoc/)

- [**AssetRipper**](https://github.com/AssetRipper/AssetRipper)

  Analyze Unity game files, inspect asset dependencies, and convert supported assets into Unity project formats.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/assetripper/)

- [**Cpp2IL**](https://github.com/SamboyCoding/Cpp2IL)

  Recover managed representations from Unity IL2CPP builds using binary and metadata analysis; reconstruction remains a work in progress.

  Tool · Also: App, Binary · [Requirements & evidence](https://awesomerea.org/resources/cpp2il/)

- [**Il2CppDumper**](https://github.com/Perfare/Il2CppDumper)

  Recover IL2CPP metadata and dummy assemblies, and generate helper scripts for native analysis tools; method code is not restored.

  Tool · Also: App, Binary · [Requirements & evidence](https://awesomerea.org/resources/il2cppdumper/)

- [**RenderDoc MCP**](https://github.com/scarletfantasy/renderdoc-mcp)

  Expose existing RenderDoc captures to an agent for bounded frame, pipeline, resource, and shader inspection.

  Integration · Independent MCP · Also: App · [Requirements & evidence](https://awesomerea.org/resources/renderdoc-mcp/)

- [**UndertaleModTool**](https://github.com/UnderminersTeam/UndertaleModTool)

  Browse and modify supported GameMaker data files, extract assets, and decompile or compile GML VM code. Includes room editing, scripted changes, a CLI, and the reusable UndertaleModLib library.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/undertalemodtool/)

- [**frida-il2cpp-bridge**](https://github.com/vfsfitvnm/frida-il2cpp-bridge)

  Inspect IL2CPP classes, methods, and fields in a live process, and trace or intercept method calls without supplying global-metadata.dat. Complements static IL2CPP dumpers with runtime observation.

  Tool · Also: App · [Requirements & evidence](https://awesomerea.org/resources/frida-il2cpp-bridge/)

- [**objdiff**](https://github.com/encounter/objdiff)

  Compare functions and data in reference and rebuilt object files to guide matching decompilation. Displays instruction-level differences, demangles C++ symbols, and can rebuild when source files change.

  Tool · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/objdiff/)

- [**decomp-permuter**](https://github.com/simonlindholm/decomp-permuter)

  Randomly or systematically permutes one C function, recompiling each variant and scoring it against a target object file to search for matching compiler output. PERM macros specify manual alternatives, and the optional permuter<span>@</span>home mode distributes runs to other workers.

  Tool · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/decomp-permuter/)

- [**asm-differ**](https://github.com/simonlindholm/asm-differ)

  Diffs original and rebuilt assembly for one function or ROM address to guide matching decompilation; its watch mode can rerun make when sources change. The README describes it as decomp.me’s default diff viewer and points to objdiff as a modern alternative.

  Tool · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/asm-differ/)

- [**UE Explorer**](https://github.com/UE-Explorer/UE-Explorer)

  Explore Unreal packages through class, property, and dependency trees; decompile and export UnrealScript classes, inspect bytecode, and examine structured binary data.

  Tool · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/ue-explorer/)

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

  Project · Also: Website · [Requirements & evidence](https://awesomerea.org/resources/psp-web-recomp/)

- [**N64: Recompiled**](https://github.com/N64Recomp/N64Recomp)

  Statically recompiles N64 MIPS binaries into C functions from symbol metadata, emitting function lookups and relocation macros so a runtime can handle statically linked and relocatable overlays. The output needs a runtime such as N64ModernRuntime; the repository also includes RSP microcode and mod tooling.

  Tool · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/n64recomp/)

- [**XenonRecomp**](https://github.com/hedge-dev/XenonRecomp)

  Converts Xbox 360 PowerPC executables into C++ that can be compiled for other platforms, with the XenonAnalyse companion detecting jump tables and function boundaries. Output is a literal instruction translation rather than decompiled code and needs a runtime that the project does not supply.

  Tool · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/xenonrecomp/)

- [**decomp.me**](https://decomp.me)

  Collaborative decompilation website for matching work: its compile service builds candidate source with a selected platform compiler, assembles the target assembly and diffs the two objects with asm-differ. m2c drafts initial decompilations for its MIPS, PowerPC, ARM and SuperH platforms. The 18 platform definitions span N64, PlayStation, PS2, PSP, GameCube/Wii, Wii U, DS, GBA, 3DS, Switch, Saturn, Dreamcast and Xbox 360 plus IRIX, Mac OS X, MS-DOS, Win32 and Android x86.

  Tool · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/decomp-me/)

- [**splat**](https://github.com/ethteck/splat)

  Binary splitter for decompilation and modding projects: a YAML config says where and how to cut an N64 ROM or PSX, PS2 or PSP binary into code, data and asset segments. A scan phase disassembles code and data, with MIPS handled by spimdisasm; a split phase writes the files and a linker script for rebuilding the input. Custom segment types can extend the pipeline.

  Tool · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/splat/)

- [**m2c**](https://github.com/matt-kempster/m2c)

  Decompiler for matching projects that turns GNU as-format 32-bit MIPS, ARM, PowerPC and SuperH assembly into draft C, with partial C++ support. A target combines platform, compiler (IDO, GCC or MetroWerks CodeWarrior) and language; context files supply types, and it can infer unknown struct fields and emit global initializers. The README places it alongside splat, asm-differ and decomp-permuter, and decomp.me calls it for initial decompilations.

  Tool · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/m2c/)

- [**decomp-toolkit**](https://github.com/encounter/decomp-toolkit)

  GameCube/Wii matching-decompilation toolkit that analyzes DOL and REL executables and, from a project configuration, splits them into relocatable objects plus an ldscript.lcf for CodeWarrior's linker, so decompiled objects can replace original ones while the relinked binary is checked against the original. Analysis covers function boundaries, a Metrowerks/SDK signature database, relocations, sections and data objects, and objects are written without an assembler. Its CLI also handles disc images, archives, compression formats, CodeWarrior demangling and DWARF dumps.

  Tool · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/decomp-toolkit/)

- [**Cheat Engine MCP Bridge**](https://github.com/miscusi-peek/cheatengine-mcp-bridge)

  Connects MCP clients to Cheat Engine through a Lua bridge script and a Python MCP server, so an agent can inspect a process the user runs under Cheat Engine: memory reads and value scans, pointer-chain resolution, structure dissection, RTTI class names, disassembly, cross-references and hardware or DBVM breakpoints. Further tool groups write memory, inject DLLs or code, automate input and use Cheat Engine's kernel-mode driver. The README limits it to educational and research use and disclaims multiplayer cheating and Terms of Service violations.

  Integration · Independent MCP · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/cheatengine-mcp-bridge/)

- [**ido-static-recomp**](https://github.com/decompals/ido-static-recomp)

  Statically recompiles the IRIX MIPS programs of SGI's IDO 5.3 and 7.1 C toolchain, such as cc, cfe, uopt, ugen and as1, into native Linux, macOS and Windows executables, so matching decompilation projects can build with the original compiler code on modern hosts. It recompiles compilers, not games: it neither decompiles nor translates game code.

  Tool · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/ido-static-recomp/)

- [**PS2Recomp**](https://github.com/ran-j/PS2Recomp)

  Experimental static recompiler that translates MIPS R5900 code from PlayStation 2 ELF executables into C++ and links it with a bundled runtime. ps2xAnalyzer or a Ghidra export script produces a per-game TOML of functions, stubs, skips and instruction patches; ps2xRecomp emits a literal instruction-by-instruction translation; ps2xRuntime and ps2xIOP supply guest memory, syscall dispatch, IOP module execution with HLE fallbacks and partial, largely stubbed GS/VU hardware. Output is not decompiled source, and getting a game to run remains per-game porting work.

  Tool · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/ps2recomp/)

- [**Xenosaga I Decomp Compatibility Kit**](https://github.com/LinuxJessi/decomp-compat-kit)

  Checks a PS2 matching decompilation from outside its own build: the C is recompiled with a stock, unpatched ee-gcc 2.96 and assembler, then each function is byte-compared against the original and every difference is classified by its likely toolchain cause. Companion scripts export ELF symbol tables to CSV and convert them to splat symbol files. Defaults target Xenosaga Episode I; the README says the method generalises but the defaults do not.

  Tool · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/decomp-compat-kit/)

- [**GB Recompiled**](https://github.com/arcanite24/gb-recompiled)

  Static recompiler that turns Game Boy and Game Boy Color ROMs into portable C projects: it decodes and analyzes banked LR35902 code, emits C with machine-readable metadata, and links it with a shared SDL2 runtime for video, audio, input, saves and hardware timing. Jump targets that static analysis missed fall back to an interpreter. The repository also carries differential, replay and frame and audio capture tooling, plus a Pokémon Crystal port that builds native features on hooks into the exact ROM.

  Tool · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/gb-recompiled/)

- [**dtk-template**](https://github.com/encounter/dtk-template)

  Project template for starting GameCube and Wii matching-decompilation repositories around decomp-toolkit. Its configure.py generates a ninja build that analyzes and splits the game's DOL and REL files from per-version config.yml, symbols.txt and splits.txt files, compiles the decompiled C/C++ with period Metrowerks compilers, relinks the result and checks it against recorded SHA-1 hashes. It also wires in objdiff for per-object diffing, progress reporting for decomp.dev and an example GitHub Actions workflow.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/dtk-template/)

- [**N64ModernRuntime**](https://github.com/N64Recomp/N64ModernRuntime)

  Runtime for N64Recomp static recompilations and traditional source ports of N64 games, made of two libraries. ultramodern reimplements core libultra services (threads, message queues, timers, controllers, audio, RSP task handling and VI timing) and leaves controller input, audio playback and the graphics renderer, with RT64 recommended, to callbacks the host project registers. librecomp bridges N64Recomp-generated code to ultramodern and adds overlay handling, PI DMA ROM reads, and EEPROM, SRAM and Flash RAM saves.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/n64modernruntime/)

- [**REDscript**](https://github.com/jac3km4/redscript)

  Compiler and decompiler toolkit for REDscript, a statically typed, object-oriented language for writing scripts for REDengine, CD Projekt's engine used in Cyberpunk 2077. Its Rust crates parse and analyze source, generate bytecode with monomorphization of generics, decompile .redscripts bytecode bundles back into REDscript source, read and write REDengine's native binary format, and provide a drop-in replacement for CD Projekt's scc script compiler plus a C API with source mapping. The CLI exposes decompile, compile, lint and format commands; the language server and debugger live in a separate redscript-ide repository.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/redscript/)

- [**Spice86**](https://github.com/OpenRakis/Spice86)

  PC emulator for executing, reverse engineering and rewriting real-mode DOS programs whose source code is unavailable. While a program runs it builds a control-flow graph, and on exit it dumps memory, execution flow, Ghidra-compatible symbols and a self-contained, runnable C# project whose generated functions override the original assembly, so analysts can rewrite them function by function into readable code while the program keeps working. It also provides a GDB remote server with custom analysis commands, a built-in debugger with a C-header structure viewer, an optional HTTP memory API and an MCP server whose tools cover CPU, memory, breakpoints, CFG and device state; an optional Ghidra plugin imports the dumps.

  Tool · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/spice86/)

- [**PS2 Web Recomp**](https://github.com/snuri00/ps2-web-recomp)

  Statically recompiles PlayStation 2 games for the browser: eerecomp translates the Emotion Engine code of a game's boot executable into C++ that is compiled to WebAssembly, and a runtime emulates the rest of the console, including a high-level EE kernel, an interpreted I/O processor running the disc's IRX modules, the vector units, SPU2 sound and the Graphics Synthesizer on WebGPU compute shaders. Its port script repeats headless runs to find functions reached through pointers and vector-unit microprograms to compile ahead of time, then builds the web page and a native runner.

  Tool · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/ps2-web-recomp/)

- [**xboxrecomp**](https://github.com/sp00nznet/xboxrecomp)

  Static-recompilation toolkit for original Xbox games: a Python pipeline parses a retail XBE, disassembles it, classifies library functions, recovers calling conventions and lifts every x86 function to C. The generated code is compiled in a separate game project that links the toolkit's runtime libraries, which stand in for the Xbox kernel and translate Direct3D 8, NV2A, audio and input to Direct3D 11 and Win32 APIs, or to SDL2 and OpenGL on Linux and macOS.

  Tool · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/xboxrecomp/)

- [**PCSX-Redux**](https://github.com/grumpycoders/pcsx-redux)

  PlayStation 1 emulator forked from PCSX and built around development and reverse engineering, with an interpreter and dynamic recompiler, software and OpenGL renderers, a MIPS debugger, VRAM viewer, SPU and GPU debugging tools, and a built-in GDB server that its documentation connects to gdb, IDA Pro and Ghidra's debugger. A LuaJIT API exposes breakpoints, memory and registers, an assembler and an ISO builder, and an optional REST web server can dump RAM and VRAM. The repository also holds the OpenBIOS replacement BIOS, PS-EXE conversion and packing tools, a Psy-Q object-file converter, Ghidra scripts for exchanging symbols and overlays with the emulator, and PS1 hardware designs.

  Tool · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/pcsx-redux/)

- [**Il2CppInspector**](https://github.com/djkaty/Il2CppInspector)

  Static analysis tool for Unity IL2CPP applications that reads an IL2CPP binary with its global-metadata.dat and outputs the application's type structure and method addresses as C# stub code, .NET assembly shim DLLs for decompilers such as ILSpy and dnSpy, IDA and Ghidra Python scripts that apply symbols and types, C++ type scaffolding and JSON address maps. Three APIs, also published as a NuGet package, and a plugin SDK expose the binary metadata, .NET type model and C++ model for custom analysis. The README states that it is not a decompiler and does not recover method source code.

  Tool · Also: App, Binary · [Requirements & evidence](https://awesomerea.org/resources/il2cppinspector/)

- [**MelonLoader**](https://github.com/LavaGang/MelonLoader)

  Mod loader for Unity games on both the Mono and IL2CPP runtimes, which loads plugins and mods from folders in a locally installed game; on Windows a proxy DLL, version.dll by default, starts it with the game. For IL2CPP games its assembly generator runs Cpp2IL and Il2CppInterop to produce managed interop assemblies, and HarmonyX and MonoMod are bundled for runtime patching. Its logs can capture Unity player output and Harmony messages, and debug options provide a Mono debug server for Mono games and a wait-for-debugger option for IL2CPP games.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/melonloader/)

- [**BepInEx**](https://github.com/BepInEx/BepInEx)

  Plugin and patching framework for Unity Mono, Unity IL2CPP and .NET Framework games such as XNA, FNA and MonoGame titles, which loads mods and analysis plugins into a locally installed game. Plugins patch methods at runtime with the bundled HarmonyX and MonoMod.RuntimeDetour, while preloader patchers rewrite managed assemblies with Mono.Cecil before the game loads them; on IL2CPP games it runs Cpp2IL and Il2CppInterop to generate interop assemblies from the game binary and global-metadata.dat. Its guides also cover configuration, logging, and debugging plugins and game assemblies with dnSpy.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/bepinex/)

- [**ReXGlue SDK**](https://github.com/rexglue/rexglue-sdk)

  Experimental SDK for statically recompiling Xbox 360 executables into portable C++23 that runs natively on Windows, Linux and macOS. Its rexglue CLI scaffolds a per-game CMake project and, from a TOML config, analyzes a XEX binary (import resolution, PDATA, block discovery, gap filling, jump resolution and call-target validation) before translating each PowerPC instruction into C++; a runtime derived from Xenia's emulator core, with D3D12 or Vulkan graphics, hosts the generated code. Generated functions are weak aliases that native C++ overrides or mid-function hooks can replace, so a port can be refined one function at a time.

  Tool · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/rexglue-sdk/)

- [**ps3recomp**](https://github.com/sp00nznet/ps3recomp)

  Toolkit and runtime for statically recompiling PlayStation 3 games into native executables. Python tools parse PS3 ELF and PRX files, find functions and firmware imports, and lift PPU and SPU code to C/C++; a project template links that code with a C/C++ runtime providing LV2 system calls, high-level emulation of the system libraries and RSX graphics translation to Direct3D 12, Metal or Vulkan.

  Tool · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/ps3recomp/)

- [**Nebula (NebulaFD)**](https://github.com/AITYunivers/NebulaFD)

  Work-in-progress decompiler for games made with Clickteam Fusion 2.5, with fixes for older Multimedia Fusion 1.5 files. Its .NET console app reads Windows executables, Android APKs, iOS IPAs, CCN data files and existing MFA projects, then runs plug-in tools: an MFA Parser that writes the game back out as an editable Fusion project, and an Asset Dumper for images, sounds, music, fonts, icons, shaders and packed files.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/nebulafd/)

<a id="app"></a>
### App

[↑ Contents](#contents)

#### Case studies

- [**Aegis: trace a login-code calculation**](https://rea.tools/showcase/aegis/)

  An official APK investigation follows TOTP methods in Aegis and publishes artifact identities and selected Evidence.

  Case study · Official REA · [Requirements & evidence](https://awesomerea.org/resources/rea-aegis-case/)

- [**Notion: trace the clipboard bridge**](https://rea.tools/showcase/notion/)

  Trace a packaged Electron clipboard path using REA findings and separate source inspection; the dynamic wrapper remains a stated limit.

  Case study · Official REA · [Requirements & evidence](https://awesomerea.org/resources/rea-notion-case/)

- [**PicoPrint: LX-D02 printer investigation**](https://github.com/bigtower17/picoprint)

  The author describes REA-assisted Android investigation followed by separate Hermes decompilation to support a Windows BLE printer.

  Case study · Mixed workflow · Also: Protocol · [Requirements & evidence](https://awesomerea.org/resources/picoprint-rea-investigation/)

- [**ReaCut: video-editor reconstruction**](https://github.com/Xiangyu-CAS/rea-capcut)

  An independent video editor whose authors document REA-assisted investigation of Jianying/CapCut behavior and project formats. The public implementation includes a local timeline, FFmpeg export and an experimental, lossy draft importer.

  Case study · Mixed workflow · [Requirements & evidence](https://awesomerea.org/resources/reacut-reconstruction/)

- [**CF632BLE: a local client from scale-protocol research**](https://github.com/guyru/cf632ble)

  Reimplements the CF632BLE scale’s BLE protocol and body-composition calculations from research on the vendor’s Unique Health Android app. A static Web Bluetooth client receives measurements, manages device profiles and keeps its history in browser storage.

  Case study · Independent reconstruction · Also: Protocol · [Requirements & evidence](https://awesomerea.org/resources/cf632ble-case/)

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

  Case study · Official REA · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/rea-calculator-percent-case/)

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

- [**Screen Studio: an author-reported REA study of auto-zoom rules**](https://x.com/i/article/2109834677343432704)

  The author reports using REA to map Screen Studio’s Electron package, reading six auto-zoom and cursor rules from its obfuscated code with Claude Code’s help, and having Claude Code write an independent recorder and renderer from those rules. The article describes the commands, evidence, a cursor-alignment check and the clone’s gaps; neither the clone nor the decoded code is published.

  Case study · Mixed workflow · [Requirements & evidence](https://awesomerea.org/resources/screen-studio-auto-zoom-case/)

- [**Claude Code background lab: an REA-informed reimplementation of a desktop animation**](https://github.com/Henry-fan88/claude-code-background)

  Reimplements the glyph-wind background of the Claude desktop app’s Claude Code New session view as an offline WebGL2 page with a 38-slider control panel. The author reports a static REA investigation of the desktop shell and its remote web bundle, followed by a newly written renderer that reuses recovered timing and layout values. It shares the original’s visual vocabulary and interaction model but is not a pixel-identical extraction.

  Case study · Mixed workflow · [Requirements & evidence](https://awesomerea.org/resources/claude-code-background-lab-case/)

- [**LSX II Volume Fixer: reconstructing volume behavior**](https://github.com/roberdorfer/kef-lsx-volume)

  Uses measured USB-volume behavior and a macOS audio proxy to map volume keys to a KEF LSX II’s LAN control. The project reports more even steps while forwarding USB audio; the speaker firmware is unchanged.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/kef-lsx-volume-case/)

- [**UU Remote on Linux: an unofficial protocol implementation**](https://github.com/VallierDev/uu-remote-linux)

  Implements an unofficial native Linux host for NetEase UU Remote, using protocol behavior the maintainer says was recovered from official-client traffic and shipped programs. The Rust implementation connects selected desktop, input and auxiliary-tool channels to Linux services; an additional Linux viewer remains experimental. The author attributes development to Claude and Codex, without establishing REA use.

  Case study · Independent reconstruction · Also: Protocol · [Requirements & evidence](https://awesomerea.org/resources/uu-remote-linux-protocol-case/)

- [**TCLimate: reconstructing selected TCL Home cloud controls**](https://github.com/umarz317/TCLimate)

  Implements selected TCL Home air-conditioner controls and electricity reporting in a native macOS menu-bar app. It adapts earlier community protocol work and documents an Android-module investigation to recover a separate statistics request. Reported validation checks cloud state, not independent physical operation or complete device equivalence.

  Case study · Independent reconstruction · Also: Protocol · [Requirements & evidence](https://awesomerea.org/resources/tclimate-cloud-controls-case/)

- [**Browserbase plugin: re-hosting Claude in Chrome’s browser bridge**](https://github.com/browserbase/claude-code-plugin)

  Stands in for the Claude in Chrome extension side of Claude Code’s local browser bridge and runs the requested actions in Browserbase cloud browsers. The author’s thread describes the reverse-engineered framing, a 4-byte little-endian length before each JSON tool call, and the plugin maps 17 named tools onto Stagehand/CDP operations. It is an archived interoperability shim with several placeholder tools, not recovered Anthropic code or a verified equivalent of the extension.

  Case study · Independent reconstruction · Also: Protocol · [Requirements & evidence](https://awesomerea.org/resources/browserbase-claude-chrome-bridge-case/)

- [**Visor: an independent Ray-Ban Meta glasses client**](https://github.com/macedonga/visor)

  Implements an Android replacement for the Meta AI companion app that speaks the Ray-Ban Meta glasses’ own Bluetooth and Wi-Fi Direct protocol, imports media, exposes settings and answers “Hey Meta” with a model the user chooses. The project wiki documents the link layers, encryption, services and Meta-side ownership steps, and lists 153 open questions. Testing is on real glasses rather than test suites, so behavior beyond the stated model and firmware remains unverified.

  Case study · Independent reconstruction · Also: Protocol · [Requirements & evidence](https://awesomerea.org/resources/visor-ray-ban-meta-client-case/)

- [**wine-uwp: running packaged Windows Store apps on a patched Wine**](https://github.com/designgears/wine-uwp)

  Extends Wine 11.17 so that signed MSIX Store apps, with Shapr3D as the main target, install and run on Linux without their source or symbols. About 49,000 changed lines add a DirectComposition implementation, composition swap chains and an app-model host, while Microsoft’s own XAML and app-model DLLs, harvested from a Windows 11 image on the user’s machine, run unmodified. The author says Claude did most of the reverse engineering and code; app support is uneven and checked by a project regression suite.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/wine-uwp-store-apps-case/)

- [**RKD Telemetry Extractor: decoding Race-Keeper track-day recordings**](https://github.com/sam-dumont/rkd-telemetry-extractor)

  Documents the proprietary .rkd telemetry format written by Race-Keeper “Instant Video” recorders, whose bundled player runs only on Windows, and implements matching Python and Go parsers that export GPS and IMU channels as Telemetry Overlay CSV and GPX. The author credits Claude Code with the hex-dump analysis and hypothesis testing, anchored by known car IDs, circuit location and speeds. Field meanings rest on physical cross-checks from the author’s own recordings, and several record types remain partly unknown.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/rkd-telemetry-extractor-case/)

- [**Elgato HDR: a userspace capture path for the Elgato 4K X’s 10-bit mode**](https://github.com/talkaboutdesign/elgato-hdr)

  A native macOS app that reaches the Elgato 4K X capture card’s 10-bit P010 video mode, which the project says Apple’s built-in webcam driver does not expose to apps. A root helper detaches that driver and runs the card’s USB Video Class streaming directly through libusb, feeding a Metal HDR viewer, an HDR10 recorder and an editor. Latency figures and device coverage remain author-reported.

  Case study · Independent reconstruction · Also: Protocol · [Requirements & evidence](https://awesomerea.org/resources/elgato-hdr-uvc-capture-case/)

- [**LGwebOS-menubar: a native macOS remote for LG webOS TVs**](https://github.com/gabrielgreco1/LGwebOS-menubar)

  A native macOS menu-bar app that pairs with an LG webOS TV over its local encrypted WebSocket interface to launch apps, switch inputs, adjust volume and picture settings, send pointer input and cast selected media. The project credits the public Connect SDK for webOS protocol behavior and reuses PyWebOSTV’s registration manifest. Testing covers one TV on webOS 5.0.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/lgwebos-menubar-remote-case/)

- [**Galaxy Buds Client: an unofficial manager built on Samsung’s earbud protocol**](https://github.com/timschneeb/GalaxyBudsClient)

  Reimplements control of Samsung Galaxy Buds over their proprietary RFCOMM serial protocol in a cross-platform desktop and Android manager. The author reports recovering the message format by analyzing the earbuds’ binary stream and disassembling Samsung’s official Android apps, and publishes partial packet notes for the 2019 Buds and the Buds+. Beyond the official app’s settings, it exposes battery statistics, diagnostics, factory self-tests, hidden debug information and firmware flashing for supported models.

  Case study · Independent reconstruction · Also: Protocol · [Requirements & evidence](https://awesomerea.org/resources/galaxy-buds-client-protocol-case/)

- [**Wino Mail: recreating Windows Mail and Calendar**](https://github.com/bkaankose/Wino-Mail)

  Native Windows client that aims to preserve the familiar Windows Mail and Calendar experience while rebuilding its functionality. The upstream README documents a WinUI 3 interface, mail and calendar providers, contacts, tasks and offline workflows.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/wino-mail-case/)

- [**ScooterLink: reconstructing Honda RoadSync’s handlebar-button protocol**](https://github.com/gdorgian/ScooterLink)

  Replaces Honda RoadSync’s Apple Music-only media control with an iOS app that pairs with a Honda PCX 2025 TFT dash over Bluetooth Low Energy and turns handlebar presses into system-wide commands for any player. The author documents the dash’s BLE services, key exchange, button registration and event bytes, reportedly worked out from the official Android app and logged traffic. Results are author-reported on one PCX125, and the protocol notes separate confirmed from unverified parts.

  Case study · Independent reconstruction · Also: Protocol · [Requirements & evidence](https://awesomerea.org/resources/scooterlink-honda-roadsync-case/)

#### Tools, projects and integrations

- [**JADX-AI-MCP**](https://github.com/zinja-coder/jadx-ai-mcp)

  JADX plugin paired with a Python MCP server to inspect decompiled Android classes, resources, cross-references and debugger context.

  Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/jadx-ai-mcp/)

- [**apktool-mcp-server**](https://github.com/zinja-coder/apktool-mcp-server)

  Python MCP server that drives a local Apktool install so agents can decode APKs; list, read, search and edit smali and resource files; read AndroidManifest.xml and apktool.yml; and rebuild the project.

  Integration · Independent MCP · [Requirements & evidence](https://awesomerea.org/resources/apktool-mcp-server/)

- [**frida-mcp (yfe404)**](https://github.com/yfe404/frida-mcp)

  Frida MCP server with persistent instrumentation sessions, runtime inspection and Android static-to-dynamic navigation.

  Integration · Independent MCP · Also: Game · [Requirements & evidence](https://awesomerea.org/resources/frida-mcp-yfe404/)

- [**Super Trouper**](https://github.com/crissyfield/super-trouper)

  Single-binary Frida MCP server for discovering devices, managing process sessions and loading instrumentation scripts.

  Integration · Independent MCP · Also: Game · [Requirements & evidence](https://awesomerea.org/resources/super-trouper/)

- [**Frida**](https://github.com/frida/frida)

  Dynamic instrumentation toolkit for observing and scripting the behavior of live native and managed processes.

  Tool · Also: Game · [Requirements & evidence](https://awesomerea.org/resources/frida/)

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

  Tool · Also: Website · [Requirements & evidence](https://awesomerea.org/resources/electron-asar/)

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

  Tool · Android · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/blutter/)

- [**hermes-dec**](https://github.com/P1sec/hermes-dec)

  Parse, disassemble and partially decompile React Native Hermes bytecode bundles. Makes HBC headers and instructions inspectable and emits pseudocode for understanding compiled application logic.

  Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/hermes-dec/)

- [**Recaf**](https://github.com/Col-E/Recaf)

  Inspect and modify compiled JVM applications with integrated decompilers, bytecode assembly, reference search, mappings and deobfuscation tools. The reviewed 4.0 preview also provides basic read-only Android bytecode inspection.

  Tool · JVM · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/recaf/)

- [**nibkit**](https://github.com/tokenbleed/nibkit)

  Decode compiled iOS/macOS interface archives into object trees, Outlet/Action connections, custom classes and navigation relationships. Exports JSON or Mermaid diagrams and exposes read-only inspection commands through MCP.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/nibkit/)

- [**AOTopsy**](https://github.com/BroNils/aotopsy)

  Statically inspect Flutter/Dart AOT libapp.so files to recover available metadata, class structures, call edges and pseudocode without embedding a Dart VM or compiling a matching SDK. Supports ARM64 and x86\_64 analysis paths.

  Tool · Android · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/aotopsy/)

- [**hbctool**](https://github.com/bongtrop/hbctool)

  Disassemble and reassemble supported React Native Hermes bytecode bundles through HASM files, enabling bytecode inspection and editing for the explicitly supported legacy HBC versions.

  Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/hbctool/)

- [**Vineflower**](https://github.com/Vineflower/vineflower)

  Fernflower-derived decompiler for Java and other JVM languages that continues the ForgeFlower, Fabric and Quiltflower forks, focused on output quality and modern Java, including records, sealed classes, switch expressions and pattern matching through Java 21+. Its command line takes a JAR, ZIP, folder or class file and writes a folder, an archive or console output, with multithreaded decompilation and automatic formatting. It can also be embedded as a library from Maven Central or used in IntelliJ IDEA through a plugin that replaces Fernflower, and the regular release JAR bundles three plugins, including Kotlin support and variable renaming.

  Tool · JVM · [Requirements & evidence](https://awesomerea.org/resources/vineflower/)

- [**Droid ASC**](https://github.com/MG1937/ASC)

  Python Android decompiler that answers queries directly against an APK instead of first unpacking and indexing it. It probes compressed DEX entries in place, uses the layout that the R8 compiler’s constant relocation and instruction deduplication leave behind to search string, type, method and field references across DEX files, and for a requested class rebuilds a minimal, self-consistent DEX in memory that a bundled copy of Androguard’s decompiler turns into Java. The droidasc CLI and Tk GUI list classes, decompile single classes, decode AndroidManifest.xml and find subclasses or interface implementations; the README presents it as a lightweight back end for agents analyzing many APKs.

  Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/droid-asc/)

- [**APKEditor**](https://github.com/REAndroid/APKEditor)

  Command-line APK editor built on ARSCLib that decodes an APK's binary resources and DEX into editable JSON, XML or smali and rebuilds a package from them, independent of aapt and aapt2. It also merges split bundles such as XAPK, APKM and APKS, refactors obfuscated resource names, and prints package information.

  Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/apkeditor/)

- [**jnitrace**](https://github.com/chame1eon/jnitrace)

  Frida-based dynamic-analysis tool that traces an Android app's use of the JNI API, similar to frida-trace or strace but for the Java Native Interface. It logs the JNI calls that native libraries make through the JNIEnv and JavaVM structures, with include and exclude filters, backtraces and optional JSON output for later post-processing. The tracing engine is also published as a separate jnitrace-engine library.

  Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/jnitrace/)

- [**AsmResolver**](https://github.com/Washi1337/AsmResolver)

  C# library for reading, modifying and rebuilding Portable Executable files, covering both native Windows images and images with .NET metadata. It offers three levels of abstraction: raw headers and sections (PEFile); interpreted data directories such as imports, exports, TLS, exceptions, debug data and Win32 resources (PEImage); and a System.Reflection-like model of .NET assemblies and modules with managed, native and dynamic method bodies. It also extracts files from AppHost/single-file bundles, supports ReadyToRun images and reads PDB and Portable PDB symbols without DIA, and upstream designs it to stay robust against malformed or obfuscated binaries.

  Tool · .NET · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/asmresolver/)

- [**CodemerxDecompile**](https://github.com/codemerx/CodemerxDecompile)

  Cross-platform desktop .NET decompiler maintained by the original JustDecompile creators as a continuation of their JustDecompile Engine, built with Mono.Cecil and an Avalonia UI. It loads assemblies into a tree of namespaces, types, members and resolved references, shows decompiled C#, VB.NET or IL with go-to-definition and back/forward navigation, and searches names, types, string literals and instructions. A create-project command exports an assembly as a Visual Studio 2015, 2017 or 2019 project.

  Tool · .NET · [Requirements & evidence](https://awesomerea.org/resources/codemerxdecompile/)

- [**wxapkg**](https://github.com/wux1an/wxapkg)

  Desktop GUI for Windows and macOS, built with Wails, that unpacks WeChat mini-program .wxapkg packages for study. It scans the mini-program package folders of local WeChat 3.x and 4.x installations, including per-user folders, or takes a file or folder the user selects; packages that the PC client stores encrypted are decrypted first. Each packaged file is written to its recorded path, with optional beautification of JSON, HTML and JavaScript.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/wux1an-wxapkg/)

- [**React Native Decompiler**](https://github.com/numandev1/react-native-decompiler)

  Alpha-stage Node.js CLI that splits a React Native JavaScript bundle (index.android.bundle or main.jsbundle), an unbundled js-modules folder, or Webpack entrypoint and chunk bundles into one readable file per module. Tagger, editor and decompiler plugins working on a Babel AST undo compilation artifacts such as Babel helpers, comma-operator chains and shortened booleans, turn element calls back into JSX and can rewrite modules as ES6 imports and exports, after which ESLint and Prettier tidy the output. Modules recognized as npm packages are skipped unless requested, and one module ID can limit output to that module and its dependencies.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/react-native-decompiler/)

- [**hermes-decomp**](https://github.com/SymbioticSec/hermes-decomp)

  Rust decompiler and analysis toolkit for Hermes bytecode (.hbc), the compiled form React Native apps ship for the Hermes engine; the README lists HBC versions 40 to 99. Its hermes-decomp CLI shows file information, disassembles, decompiles whole bundles or single functions to JavaScript, with a slower deep mode that recovers more names, and provides a terminal UI, cross-references, call graphs, control-flow graphs, Metro module and closure views and bytecode diffing. A separate hermes-mcp server exposes the read and analysis functions as MCP tools, and the hbc-decomp crate offers them as a Rust library.

  Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/hermes-decomp/)

- [**MEDUSA**](https://github.com/Ch0pin/medusa)

  Modular Frida-based framework for runtime analysis of Android and iOS apps the analyst is authorized to test. From a single coordinated script it loads plug-in modules to inspect network and WebView activity, trace API calls, examine memory and cryptographic operations, monitor malware behavior, and handle protections such as SSL pinning. The README reports it ships with over 90 reusable modules.

  Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/medusa-framework/)

- [**Android Unpinner**](https://github.com/mitmproxy/android-unpinner)

  Tool from the mitmproxy project that removes certificate pinning from an Android APK you own or are authorized to test, without a rooted device. It marks the app debuggable, touching only AndroidManifest.xml, and injects a Frida Gadget over ADB so an interception proxy can read the app's traffic, reusing HTTP Toolkit's unpinning script. It bundles the Android SDK helpers it needs and can also handle split APKs delivered as XAPK.

  Tool · Android · Also: Protocol · [Requirements & evidence](https://awesomerea.org/resources/android-unpinner/)

- [**apk-mitm**](https://github.com/niklashigi/apk-mitm)

  Command-line tool that prepares an Android APK you own or are authorized to test for HTTPS traffic inspection. It decodes the package with Apktool, adjusts the network security configuration to trust user-added certificates, disables certificate pinning, then re-encodes and signs the patched APK, so a proxy can read the app's traffic without a rooted device. App bundles supplied as .xapk or .apks are also supported.

  Tool · Android · Also: Protocol · [Requirements & evidence](https://awesomerea.org/resources/apk-mitm/)

- [**Frida Mobile Interception Scripts**](https://github.com/httptoolkit/frida-interception-and-unpinning)

  A set of Frida scripts from HTTP Toolkit for inspecting a mobile app's HTTPS traffic while analysing apps you own or are authorized to test. Injected into a running Android or iOS app, they redirect its connections to an interception proxy, add a user-supplied CA certificate to the trust stores, and disable certificate pinning and transparency checks so the proxy can read the traffic. Individual scripts can also be used on their own to hook specific behaviour.

  Tool · Android · Also: Protocol · [Requirements & evidence](https://awesomerea.org/resources/frida-interception-and-unpinning/)

- [**reFlutter**](https://github.com/Impact-I/reFlutter)

  Flutter reverse-engineering framework for apps the analyst is authorized to inspect. It repacks an app with a prebuilt patched Dart engine, or instruments the app's own engine at runtime, to emit a JSONL dump of every function's name, class, library and code offset into the Dart instructions image for Frida or IDA/Ghidra work. It can also route the app's HTTPS traffic through an inspection proxy with Flutter certificate pinning disabled.

  Tool · Android · Also: Protocol · [Requirements & evidence](https://awesomerea.org/resources/reflutter/)

- [**ddc**](https://github.com/ejfkdev/ddc)

  Rust decompiler that turns Android DEX bytecode, versions 035 to 041, from APKs, multi-dex apps and XAPK/APKS/APKM containers into Java, folding lambdas and string concatenation back into Java syntax and giving locals jadx-style names. By default every file also goes through a source-level cleanup pass, described as semantics-preserving, that inlines copy chains, recovers ternaries and for-each loops and drops dead stores; --fast skips it. Alongside full decompilation, 15 query subcommands return app and manifest information, resources, strings, cross-references, class hierarchies, disassembly or single classes and methods on demand, and the same queries are served over REST and MCP.

  Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/ddc/)

- [**Simplify**](https://github.com/CalebFenton/simplify)

  Generic Android deobfuscator built on smalivm, a sandboxed Dalvik virtual machine that executes each method and records every possible register and class value along all execution paths, taking both branches when a value such as file or network input is unknown. Simplify then repeatedly applies constant propagation, dead-code removal, unreflection and peephole optimizations to the APK or DEX, which can decrypt strings and remove reflection while keeping behaviour the same; it does not rename classes or methods. smalivm can also be used as a library, and the last release adds sdbg, a step-through Smali debugger built on it.

  Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/simplify-android-deobfuscator/)

- [**GDA (GJoy Dex Analyzer)**](https://github.com/charles2gan/GDA-android-reversing-Tool)

  Windows-native Dalvik decompiler and Android analysis workbench written in C++ that opens APK, DEX, ODEX, OAT, JAR, AAR and class files without installation. Besides Java and Smali views with cross-references, renaming and comments, it identifies packers, deobfuscates and decrypts strings, tracks data flow and taint, solves paths, runs rule-based malicious-behaviour, vulnerability and privacy-leak scans, and can dump device memory or hook methods with Frida. Shell and server CLI modes, Python and Java scripting and a sample malware-triage agent skill expose the same analysis to scripts and agents.

  Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/gda-android-decompiler/)

- [**APKLab**](https://github.com/APKLab/APKLab)

  VS Code extension that turns the editor into an Android reverse-engineering workbench around Apktool, Jadx, smali-lsp and uber-apk-signer. It decodes an APK into resources and Smali, decompiles it to Java, gives Smali go-to-definition, references and diagnostics through a language server, and rebuilds, signs and installs the modified app. It can also generate Frida hooks for Smali methods, add a Frida gadget, prepare an app for HTTPS traffic inspection with apk-mitm and produce a Quark-Engine malware-analysis report.

  Tool · Android · [Requirements & evidence](https://awesomerea.org/resources/apklab/)

- [**Fernflower**](https://github.com/JetBrains/fernflower)

  JetBrains' analytical decompiler that turns Java class files back into Java source; IntelliJ IDEA bundles it to show code when debugging or browsing class files. The standalone console decompiler takes class files, JARs, ZIPs or directories, can load library files with -e only as analysis context, and writes Java sources to an output directory. Options cover generic signatures, lambdas, inner classes, record and switch patterns, per-method time limits and renaming of ambiguous or obfuscated identifiers, optionally through a user-supplied renamer class.

  Tool · JVM · [Requirements & evidence](https://awesomerea.org/resources/fernflower/)

- [**Bytecode Viewer**](https://github.com/Konloch/bytecode-viewer)

  Desktop suite for inspecting compiled Java and Android programs: drop in a class, JAR, WAR, APK, DEX, XAPK or APKM file to browse its classes and resources, with up to three decompiler or disassembler views side by side. The README lists six bundled Java decompilers (Krakatau, CFR, Procyon, FernFlower, JADX and JD-GUI), Krakatau and Smali/baksmali disassemblers and assemblers plus javap, Dex2Jar and Enjarify for APK/DEX conversion, a built-in Java compiler for editing, and static search. Java and JavaScript plugins receive every loaded class as an ASM ClassNode for jobs such as string deobfuscation or malicious-code searches.

  Tool · JVM · [Requirements & evidence](https://awesomerea.org/resources/bytecode-viewer/)

<a id="native-binary"></a>
### Native Binary

[↑ Contents](#contents)

#### Case studies

- [**DownUnderCTF: masked-squares flag checker**](https://rea.tools/showcase/ctf/)

  An official educational challenge investigation connects binary checks to equations and records an original-program validation.

  Case study · Official REA · [Requirements & evidence](https://awesomerea.org/resources/rea-ctf-case/)

#### Tools, projects and integrations

- [**Ghidra**](https://github.com/NationalSecurityAgency/ghidra)

  Open-source analysis suite for disassembly, decompilation, graphs and Java/Python automation across executable formats.

  Tool · Also: Game, Firmware · [Requirements & evidence](https://awesomerea.org/resources/ghidra/)

- [**radare2**](https://github.com/radareorg/radare2)

  Scriptable command-line framework for inspecting, disassembling, debugging and modifying binaries across many architectures.

  Tool · Also: Game · [Requirements & evidence](https://awesomerea.org/resources/radare2/)

- [**Cutter**](https://github.com/rizinorg/cutter)

  Rizin-powered graphical reverse-engineering workspace with extensible views and Ghidra decompiler integration.

  Tool · Also: Game · [Requirements & evidence](https://awesomerea.org/resources/cutter/)

- [**Qiling**](https://github.com/qilingframework/qiling)

  Python emulation framework that adds OS, filesystem and API behavior around CPU emulation for instrumented binary analysis.

  Tool · Also: Firmware · [Requirements & evidence](https://awesomerea.org/resources/qiling/)

- [**Unicorn Engine**](https://github.com/unicorn-engine/unicorn)

  Multi-architecture CPU emulator for executing selected instruction ranges with register, memory and hook control.

  Tool · Library · Also: Game, Firmware · [Requirements & evidence](https://awesomerea.org/resources/unicorn/)

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

  Tool · Also: Game, Firmware · [Requirements & evidence](https://awesomerea.org/resources/imhex/)

- [**x64dbg**](https://github.com/x64dbg/x64dbg)

  Windows binary debugger with disassembly, memory views and plugins for analyzing programs without source code.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/x64dbg/)

- [**GDB**](https://sourceware.org/gdb/)

  Native and remote debugger for controlling execution and inspecting live or crashed program state.

  Tool · Also: Game · [Requirements & evidence](https://awesomerea.org/resources/gdb/)

- [**rr**](https://github.com/rr-debugger/rr)

  Records process execution and replays it under GDB, enabling repeatable inspection and reverse execution.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/rr/)

- [**Diaphora**](https://github.com/joxeankoret/diaphora)

  IDA-based binary diffing that matches functions and transfers names, comments and types between analyzed versions.

  Tool · Also: Game · [Requirements & evidence](https://awesomerea.org/resources/diaphora/)

- [**BinDiff**](https://github.com/google/bindiff)

  Compares disassembled binaries to find matching functions and changed code across versions.

  Tool · Also: Game · [Requirements & evidence](https://awesomerea.org/resources/bindiff/)

- [**Detect It Easy**](https://github.com/horsicq/Detect-It-Easy)

  Format-aware file identification and static inspection using parsers, signatures and programmable heuristics.

  Tool · Also: Game · [Requirements & evidence](https://awesomerea.org/resources/detect-it-easy/)

- [**r2frida**](https://github.com/nowsecure/r2frida)

  Use radare2 commands and Frida instrumentation together to inspect local or remote process memory, symbols, classes, and runtime calls on desktop and mobile targets.

  Tool · Also: App · [Requirements & evidence](https://awesomerea.org/resources/r2frida/)

- [**Kaitai Struct**](https://github.com/kaitai-io/kaitai_struct)

  Turn documented binary layouts into reusable parsers for files and network packets. A .ksy specification can be inspected with visualizers and compiled to multiple languages, helping preserve reverse-engineered format knowledge in interoperable implementations.

  Tool · Library · Also: Firmware, Protocol · [Requirements & evidence](https://awesomerea.org/resources/kaitai-struct/)

- [**GoReSym**](https://github.com/mandiant/GoReSym)

  Recover Go build metadata, function names and address ranges, source file and line tables, embedded types and strings from Go binaries, including stripped and some malformed unpacked samples. JSON output can be imported into IDA Pro with the included IDAPython script.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/goresym/)

- [**rev.ng**](https://github.com/revng/revng)

  Open-source decompilation pipeline that lifts x86-64, AArch64, i386, ARM and MIPS code with QEMU, runs LLVM-based analyses and emits C designed to be valid and recompilable. Data layout analysis infers structures from pointer use; an editable YAML model and Python or TypeScript wrappers support automation. Its VSCode-based UI is a separate closed-beta product, with commercial plans announced.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/revng/)

- [**Rizin**](https://github.com/rizinorg/rizin)

  Command-line reverse-engineering framework that began as a fork of radare2. The rizin shell analyzes and disassembles binaries, debugs programs and works as a scriptable hex editor, while rz-\* tools cover binary-format information, assembly, diffing, hashing, pattern search and FLIRT signatures. The README lists dozens of architectures, bytecode formats and file formats from ELF, PE and Mach-O to dyld caches and BIOS/UEFI images; rzpipe scripts it from Python, Rust, Go and other languages. Cutter is the separate GUI built on it.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/rizin/)

- [**Decompiler Explorer**](https://dogbolt.org)

  Web service at dogbolt.org that runs one small uploaded executable through many decompilers and shows their C-like output side by side, described as Compiler Explorer in reverse. The pinned source has runners for angr, Binary Ninja, Boomerang, dewolf, Ghidra, Hex-Rays, Kuna, REC Studio, Reko, Relyze, RetDec, rev.ng and Snowman, which helps compare how different decompilers render the same code.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/decompiler-explorer/)

- [**pwndbg**](https://github.com/pwndbg/pwndbg)

  Python plug-in that loads into GDB, or runs as a REPL around LLDB, to make live program state easier to inspect. Each stop prints a context of registers, stack, call frames and annotated disassembly with recursively dereferenced pointers; commands cover memory maps, search, telescoping, heap allocators and Go values, with Capstone/Unicorn emulation and decompiler integration for IDA, Binary Ninja, Ghidra and angr-management. The README lists Linux ELF, macOS Mach-O, QEMU user/system and embedded Cortex-M or RISC-V/32 debugging.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/pwndbg/)

- [**DynamoRIO**](https://github.com/DynamoRIO/dynamorio)

  Runtime code manipulation system for building dynamic tools that observe or transform any part of an unmodified program while it runs. Its API and IA-32/AMD64/ARM/AArch64 instruction manipulation library allow arbitrary changes to application instructions, not only inserted callouts. The release package bundles tools including drcov for code coverage, drltrace for library-call tracing, drstrace for Windows system calls, drmemtrace instruction and memory traces and the drdisas disassembler. It is a framework for building instrumentation tools, distinct from Frida's scripting of live processes.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/dynamorio/)

- [**Decompyle++ (pycdc)**](https://github.com/zrax/pycdc)

  C++ disassembler and decompiler for compiled Python bytecode that aims to support bytecode from any Python version. pycdas prints the disassembly of a .pyc file, and pycdc prints reconstructed Python source to stdout with errors on stderr; both also accept raw marshalled code objects when the Python version is given on the command line. The source carries opcode tables for Python 1.0 through 3.13.

  Tool · Also: App · [Requirements & evidence](https://awesomerea.org/resources/pycdc/)

- [**cwe\_checker**](https://github.com/fkie-cad/cwe_checker)

  Static analyzer from Fraunhofer FKIE that searches binary executables, mainly Linux and Unix ELF files, for code paths matching Common Weakness Enumeration bug classes such as buffer overflows, use-after-free and double free, NULL pointer dereferences, format strings and integer overflows. Ghidra disassembles the binary into a common intermediate representation on which its checks run, from simple heuristics to abstract-interpretation data-flow analysis, so it covers the CPU architectures Ghidra supports, including x86, ARM, MIPS and PowerPC. Warnings are printed as text or JSON, and a bundled Ghidra script annotates them in the disassembly for manual review.

  Tool · Also: Firmware · [Requirements & evidence](https://awesomerea.org/resources/cwe-checker/)

- [**FLARE-VM**](https://github.com/mandiant/flare-vm)

  Mandiant FLARE installer that sets up and maintains a Windows virtual machine for reverse engineering and malware analysis. Its PowerShell script uses Boxstarter and Chocolatey to install packages from the separate VM-Packages feed and the Chocolatey community feed, chosen in a GUI or a custom config.xml that also sets environment paths, the taskbar layout and post-install registry, service and path settings. The reviewed default configuration lists 137 packages, among them Ghidra, IDA Free, x64dbg, dnSpyEx, capa, FLOSS, PE-sieve, FakeNet-NG and Wireshark; scripts in its virtualbox folder build, snapshot and export FLARE-VM and REMnux VMs in VirtualBox.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/flare-vm/)

- [**B2R2**](https://github.com/B2R2-org/B2R2)

  Binary analysis framework written in F# for .NET by KAIST's SoftSec Lab. It parses ELF, PE, Mach-O and WebAssembly files, parses, disassembles and lifts instructions into its own IR, recovers control-flow graphs and assembles code; the README's feature table covers x86/x86-64, ARMv7/AArch64, MIPS, PowerPC, RISC-V, SPARC, S390 and other ISAs as well as CIL, EVM, eBPF, WebAssembly and Python bytecode. Its b2r2 launcher starts a readelf-like format scanner, a linear-sweep disassembler, a recursive-descent explorer with a web GUI, an IR and assembly REPL and an assembler.

  Tool · Library · [Requirements & evidence](https://awesomerea.org/resources/b2r2/)

- [**rz-ghidra**](https://github.com/rizinorg/rz-ghidra)

  Rizin plugin that embeds Ghidra's C++ decompiler and Sleigh disassembler, so no Java Ghidra installation is needed. Its pdg commands decompile the current function, optionally side by side with offsets or as XML or JSON, can return the output to Rizin as comments, and list the loaded Sleigh languages; config variables control formatting and can override the auto-detected Sleigh language. The decompiler draws on Rizin's loaded binary, types and comments, and an optional plugin brings it into the Cutter GUI.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/rz-ghidra/)

- [**dewolf**](https://github.com/fkie-cad/dewolf)

  Research decompiler from Fraunhofer FKIE, developed with Singapore's DSO National Laboratories between 2019 and 2021, that runs as a Binary Ninja plugin and starts from Binary Ninja's Medium Level IL. A pipeline of preprocessing, SSA, data-flow and control-flow stages restructures code following the DREAM/DREAM++ approach and emits C-like output. Results appear in a Binary Ninja dock widget, or decompile.py prints or writes them for a whole binary or one named function in batch use.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/dewolf/)

- [**decomp2dbg**](https://github.com/mahaloz/decomp2dbg)

  Decompiler-to-debugger bridge that serves function names, global variables, stack and register variable names and decompiled code from IDA Pro, Binary Ninja, Ghidra or angr-management to GDB over an XML-RPC connection. Synced functions and globals become ordinary GDB symbols for breakpoints and memory examination, local variables appear as convenience variables, and each breakpoint stop prints the decompiled line for the current address. It works with vanilla GDB, GEF and pwndbg, and can map a shared library's symbols once its load range is supplied.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/decomp2dbg/)

- [**E9Patch**](https://github.com/GJDuck/e9patch)

  Static binary rewriter for x86-64 Linux ELF executables and shared objects that inserts instrumentation without control-flow recovery and writes a drop-in replacement binary, following the PLDI 2020 paper Binary Rewriting without Control Flow Recovery. The e9tool front end selects instructions with a matching language over disassembly attributes and patches them with built-in trampolines, calls into C or C++ functions compiled with e9compile.sh, or hand-written plugin trampolines; the e9patch back end accepts JSON-RPC commands so other tools can drive it. Optional modes add heuristic control-flow recovery for faster rewritten binaries or SIGILL-based fallbacks for full patch coverage.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/e9patch/)

- [**Rellic**](https://github.com/lifting-bits/rellic)

  Trail of Bits implementation of the pattern-independent structuring algorithm from the No More Gotos paper, turning LLVM bitcode into goto-free C as a small, hackable decompiler back end that interoperates with LLVM and Remill. rellic-decomp translates a bitcode module to C in batch, rellic-xref serves a web interface for choosing refinement passes and linking C AST nodes to the bitcode that produced them, and rellic-headergen emits C layouts of data structures from a module's DWARF metadata. Machine code must first be lifted to bitcode by another tool; a bundled IDA script uses Anvill for that step.

  Tool · Library · [Requirements & evidence](https://awesomerea.org/resources/rellic/)

- [**ghidra-delinker-extension**](https://github.com/boricj/ghidra-delinker-extension)

  Ghidra extension that delinks a selected part of a program back into a relocatable object file. Its relocation table synthesizer analyzer reconstructs, from the Ghidra database, the relocations a linker normally discards, and its exporters write COFF (x86, x86-64), ELF (x86, x86-64, MIPS) or OMF (x86) objects with symbols and relocation tables that a toolchain can link again. The README lists binary patching through the linker, software ports, format conversion, library extraction and decompilation projects that reimplement a program one object file at a time among its uses.

  Tool · Also: Game · [Requirements & evidence](https://awesomerea.org/resources/ghidra-delinker-extension/)

- [**BinExport**](https://github.com/google/binexport)

  The exporter component of BinDiff: plugins for IDA Pro and Binary Ninja and an extension for Ghidra that write an analyzed disassembly to the Protocol Buffer format BinDiff requires. The BinExport2 schema covers instructions with their operands and expressions, basic blocks, flow graphs, the call graph, sections, strings, comments and data references; the exporter can also write a statistics text file or a text dump for debugging. Exports can be scripted through IDC or IDAPython in IDA and through a BinExport.java script that also runs in Ghidra's headless analyzer.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/binexport/)

- [**Karta**](https://github.com/CheckPointSW/Karta)

  Source-code-assisted IDA Python plugin from Check Point Research that finds and matches open-source libraries compiled into large binaries and firmware. Its identifier script reports which supported libraries, such as OpenSSL, zlib, libpng and net-snmp, are present and fingerprints their versions; the matcher then uses a JSON configuration built from that library version to locate its compiled files by their original function order, match their functions and the external libc functions they call, and export selected matches as IDA names. The bundled Thumbs Up scripts improve IDA's function analysis beforehand, including ARM/Thumb separation in firmware.

  Tool · Also: Firmware · [Requirements & evidence](https://awesomerea.org/resources/karta/)

- [**VTIL-Core**](https://github.com/vtil-project/VTIL-Core)

  C++20 core of the VTIL (Virtual-machine Translation Intermediate Language) project, an intermediate language and optimizing compiler that the README describes as built for binary de-obfuscation and de-virtualization. Unlike LLVM IR, VTIL keeps the native stack, physical registers and non-SSA form, so code from register or stack machines can be lifted into it, native instructions can stay inline, and code can be emitted back at any virtual address. The library provides the IL with routines, basic blocks and serialization, a symbolic expression engine and simplifier, optimizer passes such as dead-code elimination, propagation and stack pinning, and Capstone/Keystone-based AMD64 and ARM64 disassembly and assembly helpers.

  Tool · Library · [Requirements & evidence](https://awesomerea.org/resources/vtil-core/)

- [**Frida Workbench for VSCode**](https://github.com/ChiChou/vscode-frida)

  Unofficial Visual Studio Code extension for Frida work. A sidebar lists apps and processes on local, Apple Simulator, USB and remote devices to attach, spawn or kill, and runtime panels browse an attached process's native modules and exports and its Java and Objective-C classes, methods and protocols; selected items generate Interceptor, Objective-C or Java hook scaffolds, optionally with GitHub Copilot-inferred native signatures, and Objective-C headers or Java class stubs can be dumped. A language server completes class, selector and module names from a live target, and the extension also scaffolds Frida agent and C-module projects, script-debugging configurations, syslog streaming and Android frida-server setup.

  Tool · Also: App · [Requirements & evidence](https://awesomerea.org/resources/vscode-frida/)

- [**ghidriff**](https://github.com/clearbluejar/ghidriff)

  Command-line binary diffing engine that drives Ghidra headlessly through pyghidra: it imports and analyzes an old and a new binary, then reports added, deleted and modified functions, with patch diffing as its main use. The default VersionTrackingDiff engine combines several Ghidra Version Tracking correlators with BSim matching, alongside simpler symbol-name and structural-graph engines and a GhidraDiffEngine base class for custom differs. Results are written as JSON and Markdown with Mermaid charts and meta diffs of strings, called and calling functions and binary metadata, plus optional side-by-side HTML.

  Tool · Also: Firmware · [Requirements & evidence](https://awesomerea.org/resources/ghidriff/)

- [**Ddisasm**](https://github.com/GrammaTech/ddisasm)

  GrammaTech's Datalog disassembler, which turns ELF and PE binaries for x86-32, x86-64, ARM32, ARM64 and MIPS32 into the GTIRB intermediate representation. It decodes a superset of possible instructions, then applies Soufflé Datalog rules and weighted heuristics to infer code locations, symbolization and function boundaries; gtirb-pprinter turns the result into reassemblable assembly or a rebuilt binary, and the GTIRB APIs or gtirb-rewriting can modify it in between. User hint files add Datalog facts or change heuristic weights where inference goes wrong.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/ddisasm/)

- [**PINCE**](https://github.com/korcankaraokcu/PINCE)

  Linux front end for the GNU Debugger (GDB), focused on games but usable for other reverse engineering; the name stands for “PINCE is not Cheat Engine”. It scans process memory and pointers through libmemscan into a typed address table, and its memory view adds disassembly, an on-the-fly assembler, code dissection for referenced calls, jumps and strings, function, region and instruction searches, and structure overlays, including structures generated from Mono/IL2CPP class dissection of native Linux or Wine/Proton processes. Debugging covers chained breakpoints and watchpoints, tracking of the instructions that access an address, tracing and stack traces, alongside a GDB console and the reusable libpince Python library.

  Tool · Also: Game · [Requirements & evidence](https://awesomerea.org/resources/pince/)

- [**uncompyle6**](https://github.com/rocky/python-uncompyle6)

  Cross-version decompiler that translates Python bytecode back into equivalent Python source, accepting bytecode from Python 1.0 through 3.8 as well as some PyPy bytecode and Dropbox's Python 2.5. It disassembles code objects with the companion xdis library and parses the instruction stream into a grammar-based tree from which source is printed; it can also deparse just the fragment around a given bytecode offset, which the author's trepan debuggers use for exact location reporting. It succeeds the older decompyle, uncompyle and uncompyle2 forks.

  Tool · Also: App · [Requirements & evidence](https://awesomerea.org/resources/uncompyle6/)

- [**ret-sync**](https://github.com/bootleg/ret-sync)

  Reverse-Engineering Tools SYNChronization: plugins that keep IDA, Ghidra or Binary Ninja graph and decompiler views following a live WinDbg, GDB, LLDB, OllyDbg 1.10/2 or x64dbg session, rebasing addresses on the fly so ASLR does not break the mapping. Debugger commands push comments, labels, rebased addresses and command output into the disassembler database and resolve symbols from it, while disassembler hotkeys set breakpoints and step the debugger; several databases can be synced at once and the two sides may run on different hosts. A standalone Python library offers the same position syncing to custom tracing tools.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/ret-sync/)

- [**PyInstaller Extractor (pyinstxtractor)**](https://github.com/extremecoders-re/pyinstxtractor)

  Single-file Python script that extracts the contents of executables built with PyInstaller, including Linux ELF builds without other tools. It locates the PyInstaller archive in the executable, reports the PyInstaller and Python versions and likely entry-point scripts, and writes out the bundled CArchive files and the modules in the PYZ archive. It fixes the headers of the extracted .pyc files so that Python bytecode decompilers such as uncompyle6 and Decompyle++ (pycdc) recognize them.

  Tool · Also: App · [Requirements & evidence](https://awesomerea.org/resources/pyinstxtractor/)

- [**Binary Analysis Platform (BAP)**](https://github.com/BinaryAnalysisPlatform/bap)

  OCaml binary analysis platform from Carnegie Mellon University. Its bap command loads a program, disassembles it, lifts instructions into an architecture-neutral intermediate representation, builds the control-flow graph and runs analysis passes, while objdump, raw-loader and mc modes handle linear disassembly, raw code blobs and single encodings. The README lists x86, x86-64, ARM, MIPS and PowerPC support, an interpreter, a microexecution interpreter, a symbolic executor and the Primus Lisp language for analyses, function stubs and SMT-solver queries; analyses are written as OCaml plugins or by embedding BAP as a library, with C bindings and minimal Python support in separate repositories.

  Tool · Library · [Requirements & evidence](https://awesomerea.org/resources/bap/)

- [**Reko**](https://github.com/uxmal/reko)

  General-purpose decompiler that loads executables or raw images, scans their machine code into a machine-independent register transfer language, groups it into procedures and decompiles them into high-level C code. The reviewed source has 64 architecture directories, from 6502, Z80 and PDP-11 to ARM, MIPS, PowerPC, RISC-V and x86, and loaders for formats including ELF, PE/MZ, Mach-O, COFF, Amiga Hunk, VMS, WebAssembly, Xbox XBE and Xbox 360 XEX. It runs as a Windows Forms GUI, a command-line client or a .NET library, and project files and scripts let users add names, types and comments.

  Tool · Also: Firmware · [Requirements & evidence](https://awesomerea.org/resources/reko/)

- [**Dyninst**](https://github.com/dyninst/dyninst)

  Binary instrumentation, analysis and modification libraries from the Paradyn project. DyninstAPI inserts and changes instrumentation in a running program, or rewrites an executable or library on disk and writes the patched copy back, through one machine-independent interface that also supports static and dynamic analysis. Separately documented components handle symbol tables, line numbers and types (SymtabAPI), instruction decoding and disassembly (InstructionAPI), parsing into blocks, functions and loops (ParseAPI), dataflow analyses such as slicing (DataFlowAPI), process control, stack walking and patching.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/dyninst/)

- [**goblin**](https://github.com/m4b/goblin)

  Rust crate for zero-copy, endian-aware parsing of ELF32/64, 32/64-bit Mach-O and multi-architecture fat containers, PE32/PE32+, COFF objects, Terse Executable (TE) images and Unix/BSD archives; Object::parse picks the format from its magic bytes. Parsed structures cover ELF headers, sections, symbols, dynamic entries, relocations and notes, Mach-O load commands, imports and exports, and PE imports, exports, relocations, TLS, resources, exception and unwind data, Authenticode certificates and the .NET CLR header. Feature flags can reduce it to std-free #\[repr(C)\] struct definitions for kernels and other no\_std code.

  Tool · Library · [Requirements & evidence](https://awesomerea.org/resources/goblin/)

- [**FLOSS (FLARE Obfuscated String Solver)**](https://github.com/mandiant/flare-floss)

  Mandiant FLARE string extractor for malware analysis that is used like strings.exe but also recovers obfuscated strings. Besides static ASCII and UTF-16LE strings it extracts stack strings, tight strings and strings decoded by functions: it heuristically identifies decoding routines, recovers their arguments through control-flow analysis, emulates them and diffs memory before and after emulation. It also extracts Go and Rust strings and accepts PE, ELF and raw 32- or 64-bit shellcode; JSON results can be turned into import scripts for IDA Pro, Ghidra, Binary Ninja, radare2 and x64dbg.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/flare-floss/)

- [**Zydis**](https://github.com/zyantific/zydis)

  Lightweight C11 x86/x86-64 disassembler and code-generation library. Its decoder reports each instruction's operands, accessed CPU and FPU flags, ISA set and extension and branch type; the formatter prints Intel, MASM or AT&amp;T syntax, and the encoder assembles instructions from encoder requests, which can also be derived from decoded instructions. ZydisDisasm and ZydisInfo command-line tools are included, and the official Rust and Python 3 bindings live in separate repositories.

  Tool · Library · [Requirements & evidence](https://awesomerea.org/resources/zydis/)

- [**QBDI**](https://github.com/QBDI/QBDI)

  Quarkslab's modular dynamic binary instrumentation (DBI) framework, which JIT-recompiles a program's basic blocks inside its own process so that an instrumentation tool can register callbacks before or after instructions, on memory reads and writes, and on VM events. The engine is a library that can start an instrumented execution anywhere in a process, scripted from C, C++, Python (PyQBDI) or Frida JavaScript. It has no preferred injection method: it bundles the LD\_PRELOAD-based QBDIPreload for Linux and macOS dynamic executables and is integrated with Frida.

  Tool · Also: App · [Requirements & evidence](https://awesomerea.org/resources/qbdi/)

- [**binsider**](https://github.com/orhun/binsider)

  Terminal user interface for inspecting ELF binaries. It shows file information and linked shared libraries in the manner of stat and ldd, browses ELF headers, notes, sections, segments, symbols, dynamic symbols and relocations much like readelf, extracts strings with an adjustable minimum length, and offers a searchable hexdump view. Optional dynamic analysis runs the binary and traces its system calls like strace, with a summary of time and call counts per system call; the interface can also be embedded as a Rust library in Ratatui applications.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/binsider/)

- [**iced**](https://github.com/icedland/iced)

  x86 instruction library for 16-, 32- and 64-bit code that decodes, formats, assembles and encodes instructions, with masm, nasm, GNU AT&amp;T and Intel XED output syntaxes. Its instruction-info API reports the registers, memory operands and RFLAGS bits an instruction reads or writes, its CPUID feature flags and control-flow type, and the encoder can re-encode decoded instructions at any address. Rust, C# (.NET) and Java implementations live in one repository, with Python, JavaScript (WebAssembly) and Lua bindings built on the Rust crate.

  Tool · Library · [Requirements & evidence](https://awesomerea.org/resources/iced/)

- [**hrtng**](https://github.com/KasperskyLab/hrtng)

  IDA plugin published by Kaspersky that extends the Hex-Rays decompiler with tools its author collected for reverse-engineering work, including malware analysis. It decrypts strings, data and constants with built-in ciphers or in bulk through IDA's Appcall debugger feature, resolves API-name hashes, unflattens control flow and forces decompilation of obfuscated code, and recognizes library code through microcode signatures, inlined-function detection and PAT files built from an IDA database. Pseudocode helpers cover automatic renaming, retyping and enum substitution, structure creation, virtual and indirect call navigation, and patching.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/hrtng/)

- [**BinCAT**](https://github.com/airbus-seclab/bincat)

  Static binary code analysis toolkit designed for reverse engineers. Starting from a chosen address and initial state, it computes register and memory values, taint and reconstructed types, with forward and backward analysis and heap use-after-free and double-free detection; bits it cannot determine are shown as unknown. It is driven from an IDA plugin, where analysts can override values or taint, skip functions or replace instructions with NOPs before re-running, or from Python and an .ini configuration for automation.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/bincat/)

- [**GEF (GDB Enhanced Features)**](https://github.com/hugsy/gef)

  Single-file Python extension, gef.py, that adds dynamic-analysis commands to GDB. Each stop shows a context view of registers, stack, code, threads and call trace, and commands cover memory maps, pointer dereferencing, searching process memory for patterns, ELF and security-property information, process status and glibc heap inspection. An architecture abstraction layer covers x86-32/64, ARMv5–v7, AArch64, SPARC, MIPS and PowerPC, and gef-remote enriches remote sessions through gdbserver or the GDB stubs of qemu-user and qemu-system.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/gef/)

- [**Triton**](https://github.com/JonathanSalwan/Triton)

  C++ library with Python bindings for dynamic binary analysis of x86, x86-64, ARM32, AArch64 and RISC-V 32/64 code. Callers process instructions one at a time, optionally with concrete register and memory values; Triton builds symbolic expressions from each instruction's semantics, tracks taint and solves path constraints through Z3 or Bitwuzla. It also synthesizes and simplifies expressions and lifts them to LLVM IR or Z3 and back, for building analysis tools, automating reverse engineering, software verification or emulating code.

  Tool · Library · [Requirements & evidence](https://awesomerea.org/resources/triton/)

- [**PyLingual**](https://github.com/syssec-utd/pylingual)

  Research decompiler for CPython bytecode from Python 3.6 onward that pairs per-version transformer models with control-flow reconstruction. A segmentation model splits bytecode into statements, a statement model translates each into source, and templates rebuild loops, conditionals, exception handlers, with blocks and match statements. The result is recompiled with the target Python version and its control flow compared with the original bytecode, and failing segments are retried with alternative segmentations; the design is described in the IEEE S&amp;P 2025 paper “PyLingual: Toward Perfect Decompilation of Evolving High-Level Languages”.

  Tool · Also: App · [Requirements & evidence](https://awesomerea.org/resources/pylingual/)

- [**Miasm**](https://github.com/cea-sec/miasm)

  Python reverse-engineering framework for analyzing, modifying and generating binary programs. It reads, modifies and generates 32- and 64-bit PE and ELF files, assembles and disassembles x86, ARM, AArch64, MIPS, PowerPC, SH4, MSP430 and MeP code, and lifts it into its own intermediate language for symbolic execution, SSA and data-flow analysis, dependency graphs and expression simplification aimed at deobfuscation. Its JIT emulator runs shellcode or parts of binaries through LLVM, GCC, Clang or pure-Python backends, with Python callbacks that stand in for library functions, sandboxes with selected Windows API and Linux emulation, and dynamic symbolic execution through Z3.

  Tool · Library · [Requirements & evidence](https://awesomerea.org/resources/miasm/)

- [**HyperDbg**](https://github.com/HyperDbg/HyperDbg)

  Hypervisor-assisted Windows debugger that virtualizes the running system with Intel VT-x and Extended Page Tables to debug kernel and user mode, either locally as a tracing and introspection tool or from a host attached over a serial connection to a guest virtual machine. Its events include EPT-based hidden breakpoints and hooks, memory read, write and execute monitoring without the limits of hardware debug registers, monitoring of system calls, CPUID, MSRs, I/O ports, MMIO, exceptions and interrupts, and Intel PT and LBR branch tracing. A kernel-side script engine, PDB symbol support and an SDK automate analysis.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/hyperdbg/)

- [**Kuna**](https://github.com/Noelo-Lab/kuna)

  Agent-first decompiler written in Rust that began as a port of Ghidra’s C++ decompiler and SLEIGH compiler, and has since diverged with option-gated features, some ported from angr. A single self-contained kuna binary decompiles one function or exports a whole binary to C, header and assembly files, and the same engine runs in the browser through WebAssembly or as the decompiler backend inside Ghidra. The project calls itself an experiment in having LLM agents refine the decompiler; most code is agent-written and steered by regression and benchmark results.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/kuna/)

- [**Binary Ninja API**](https://github.com/Vector35/binaryninja-api)

  Vector 35’s public C++, Python and Rust APIs for Binary Ninja, with their documentation, examples and the open-source plugins built on them. Binary Ninja itself is a closed-source commercial application, and this repository does not contain its analysis core. The open plugins cover the x86/x86\_64, ARM64, ARMv7, PowerPC, MIPS, RISC-V and MSP430 architectures, ELF, PE/COFF, Mach-O and Apple shared-cache and kernel-cache loaders, DWARF, PDB and IDB import, and Objective-C, RTTI and SVD analysis, while the examples walk the low- and medium-level intermediate languages and extend the analysis pipeline through workflows.

  Tool · Also: Firmware · [Requirements & evidence](https://awesomerea.org/resources/binary-ninja-api/)

- [**capa**](https://github.com/mandiant/capa)

  Mandiant FLARE tool that reports what an executable can do by matching a YAML rule set against features extracted from PE, ELF and .NET files or 32/64-bit shellcode, such as API calls, imports, strings and constants. Matches are grouped into capability namespaces with ATT&amp;CK and MBC tags, and verbose output shows the function or basic-block addresses and features behind each match, pointing analysts to code worth studying. It also reads CAPE, DRAKVUF and VMRay sandbox reports for dynamic features and can use vivisect, IDA Pro, Ghidra or Binary Ninja for analysis, with explorer plugins for IDA and Ghidra and a browser viewer for its JSON results.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/capa/)

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

- [**Supermodel: initial Real3D Pro-1000 image-generator emulation**](https://github.com/trzy/Supermodel)

  Adds emulation of Real3D’s Pro-1000, the SCSI-attached image generator from which Sega’s Model 3 graphics hardware derives, to the Supermodel arcade emulator. It boots user-supplied Pro-1000 firmware from the SDK disc, emulates the board’s interrupt, JTAG and UART hardware, and exposes the firmware’s built-in monitor on the console. Nothing renders yet, and SCSI host communication is unimplemented.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/supermodel-real3d-pro1000-emulation-case/)

- [**OpenDMCUFirm: a reimplemented Wii U DMCU display firmware**](https://github.com/GaryOderNichts/OpenDMCUFirm)

  Reimplements in C the firmware of the Wii U’s DMCU, the M68HC11-compatible display microcontroller in its AMD graphics controller, which in Wii mode reads the Video Interface state and configures display output, deinterlacing, scaling and overscan. The README says the work is based on reverse engineering of the original firmware but is not a byte-for-byte matching decompilation, and calls it a work in progress. The built image replaces the stock firmware in Wii mode when loaded through the evWii plugin.

  Case study · Independent reconstruction · [Requirements & evidence](https://awesomerea.org/resources/opendmcufirm-wii-u-dmcu-firmware-case/)

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

  Tool · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/ofrak/)

- [**FirmAE**](https://github.com/pr0v3rbs/FirmAE)

  Emulate router and IP-camera firmware to inspect network services and runtime behavior, with automated emulation checks and separate analysis, run, and debugging modes.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/firmae/)

- [**PulseView**](https://github.com/sigrokproject/pulseview)

  Examine captured logic and analog waveforms with sigrok's graphical frontend. Protocol decoders and decoder stacking expose bus messages and higher-level device operations, making hardware communication traces useful for firmware and interoperability investigations.

  Tool · Also: Protocol · [Requirements & evidence](https://awesomerea.org/resources/pulseview/)

- [**UEFITool**](https://github.com/LongSoft/UEFITool)

  Parse UEFI firmware images into an inspectable tree and check their structure. Companion UEFIExtract and UEFIFind tools extract parsed contents and locate patterns, supporting analysis of firmware components and vendor formats.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/uefitool/)

- [**Glasgow Interface Explorer**](https://github.com/GlasgowEmbedded/glasgow)

  Use FPGA-based open hardware and Python applets to read and write SPI flash, I2C EEPROM and parallel memory chips, determine JTAG pinouts, debug supported processors and analyze UART, SPI and QSPI transactions on physical devices.

  Tool · Also: Protocol · [Requirements & evidence](https://awesomerea.org/resources/glasgow-interface-explorer/)

- [**Penguin**](https://github.com/rehosting/penguin)

  Rehost embedded Linux firmware from an extracted root filesystem using a generated, editable configuration of emulation transformations, then refine it through a guest root shell, forwarded network services and recorded dynamic-analysis output.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/penguin/)

- [**ipsw**](https://github.com/blacktop/ipsw)

  Command-line toolkit for Apple firmware research and reverse engineering. It downloads and unpacks IPSWs, OTAs and KDKs and compares builds; inspects Mach-O load commands, symbols, signatures and entitlements with ARM64 disassembly; finds symbols and cross-references in dyld shared caches, extracts dylibs and dumps Objective-C headers and Swift metadata; extracts KEXTs and compares kernelcaches; and parses IMG4, decrypts AEA archives and inspects iBoot and coprocessor firmware.

  Tool · Also: App, Binary · [Requirements & evidence](https://awesomerea.org/resources/ipsw/)

- [**avatar²**](https://github.com/avatartwo/avatar2)

  Python framework from EURECOM's S3 group that orchestrates emulators, debuggers and physical devices for dynamic analysis of embedded firmware. An analysis script declares targets, such as a modified QEMU, PANDA, Unicorn, a gdbserver or an OpenOCD or J-Link debug probe, then a memory layout whose ranges can forward accesses from one target to another, and an execution plan. Execution and register or memory state can move between targets, so firmware can run in an emulator while its peripheral accesses go to the real device.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/avatar2/)

- [**efiXplorer**](https://github.com/REhints/efiXplorer)

  IDA Pro plugin and loader that automate static analysis of UEFI firmware. The plugin annotates Boot, Runtime, SMM and PEI service calls, lists the EFI protocols and known GUIDs a module installs or consumes, applies protocol interface types in the Hex-Rays decompiler, flags suspected SMM callout and GetVariable out-of-bounds write patterns for review and saves a JSON report. The efiXloader module opens a whole firmware image in one IDA database, with driver entry points, navigation between drivers and a DXE driver dependency graph.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/efixplorer/)

- [**vmlinux-to-elf**](https://github.com/marin-m/vmlinux-to-elf)

  Rebuild an analyzable ELF with function and variable symbols from a Linux kernel image, whether a raw or compressed vmlinux, vmlinuz, zImage or bzImage blob, certain Android boot.img files or a stripped kernel ELF, by locating and decoding the embedded kallsyms symbol table. It detects the compression format, instruction set, endianness, word size, entry point and an approximate base address and writes an ELF for IDA Pro or Ghidra; a kallsyms-finder listing, a standalone decompressor and a GTK GUI are included.

  Tool · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/vmlinux-to-elf/)

- [**Sony-PMCA-RE**](https://github.com/ma1co/Sony-PMCA-RE)

  USB tool built from reverse engineering Sony digital cameras. On supported models it reads camera information and installs Android apps through the PlayMemories Camera Apps mechanism, while its firmware-updater and service-mode shells can dump firmware, run Linux commands and change settings. The repository's notes describe the app-installation exchange between the Sony app store, the browser plugin and the camera.

  Tool · Also: Protocol · [Requirements & evidence](https://awesomerea.org/resources/sony-pmca-re/)

- [**cpu\_rec**](https://github.com/airbus-seclab/cpu_rec)

  Statistically recognize the CPU instruction set in an arbitrary binary file, such as an unknown firmware image, by comparing Markov-chain byte statistics with a default corpus covering dozens of architectures, from 6502 and 8051 to ARM, MIPS, PowerPC, RISC-V, x86-64 and WebAssembly. It reports a match for the whole file, then the largest chunk that matches one architecture, and shows entropy so that encrypted or compressed regions can be discounted. It runs standalone, as a Python function or as a binwalk module.

  Tool · Also: Binary · [Requirements & evidence](https://awesomerea.org/resources/cpu-rec/)

- [**ME Analyzer**](https://github.com/platomav/MEAnalyzer)

  Parse Intel Management Engine (CS)ME, TXE and SPS firmware, Graphics System Controller firmware and their independent PMC, PCHC, PHY and option-ROM images to report family, version, release, SKU, platform, size and health status. Research options print flash partition, BPDT/IFWI and CSE layout tables, validate RSA signatures and checksums, and unpack the supported CSE and GSC code and file systems. A bundled database identifies known images and reports those not yet listed in the community firmware repositories.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/me-analyzer/)

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

  Tool · Also: App, Firmware · [Requirements & evidence](https://awesomerea.org/resources/wireshark/)

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

- [**Blackbox Protobuf**](https://github.com/nccgroup/blackboxprotobuf)

  NCC Group's tools for decoding and re-encoding Protocol Buffers messages without the matching .proto definition. The decoder returns the message data with an editable type definition built from best-effort guesses based on wire types; analysts can name fields, correct types and re-encode edited messages, which protoc --decode\_raw cannot do. It ships as a Python library with a bbpb CLI, a Jython Burp Suite extension and a mitmproxy addon, and its README traces it to modifying messages during mobile penetration tests.

  Tool · Also: App · [Requirements & evidence](https://awesomerea.org/resources/blackbox-protobuf/)

- [**furiousMAC Continuity**](https://github.com/furiousMAC/continuity)

  Reverse-engineering notes and a Wireshark dissector for Apple's proprietary Continuity Bluetooth LE advertisements, continuing the authors' PETS 2019 privacy study. Per-message pages document field layouts and observed values for 14 message types, including AirDrop, Handoff, Proximity Pairing, Nearby Info and Find My, and the dissector replaces Wireshark's packet-bthci\_cmd.c so captured advertisements decode into named btcommon.apple fields.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/furiousmac-continuity/)

- [**opendbc**](https://github.com/commaai/opendbc)

  comma.ai's repository of DBC files describing the CAN messages and signals of many car makes, with a Python library that parses and builds CAN messages from those definitions; its porting guide has contributors reverse engineer new messages from recorded drives in the cabana tool. Per-brand car ports built on it parse vehicle state, identify models from ECU firmware versions and generate openpilot's steering, gas and brake messages, while safety code for comma's panda interface restricts which messages can be sent.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/opendbc/)

- [**FISSURE**](https://github.com/ainfosec/FISSURE)

  GNU Radio-based RF framework that carries a signal from survey and detection through IQ capture, inspection, conditioning, feature extraction and classification into a protocol discovery workflow. Its demodulation workspace estimates symbol rates for OOK/ASK and binary FSK recordings, and the bitstream and framing stage applies Manchester or differential decoding, sync-pattern and CRC evidence and repeated-message detection to propose message boundaries. A Qt dashboard coordinates local or remote SDR sensor nodes, a library keeps protocol and packet definitions, dissectors and archived recordings, and plugins add inspection modules such as radar pulse analysis.

  Tool · [Requirements & evidence](https://awesomerea.org/resources/fissure/)

- [**friTap**](https://github.com/fkie-cad/friTap)

  Frida-based tool that hooks TLS libraries such as OpenSSL, BoringSSL, NSS and GnuTLS inside a running process and writes NSS key logs and decrypted payloads as PCAP, so analysts can inspect an application's encrypted traffic in Wireshark. For stripped or statically linked libraries it accepts byte patterns or offsets and can scan for renamed libraries, or it can recover TLS secrets by scanning heap memory instead of hooking. A terminal UI, a Python API and a Wireshark extcap integration wrap the same capture.

  Tool · Also: App · [Requirements & evidence](https://awesomerea.org/resources/fritap/)

- [**pbtk**](https://github.com/marin-m/pbtk)

  Recover Protobuf message definitions from compiled programs as readable .proto files. Extractors cover the Java runtimes in JAR, DEX and APK files (including ProGuard-obfuscated code), binaries that embed Protobuf reflection metadata, and web apps using the Protobuf-URL format. A GUI then binds a recovered message type to an HTTP endpoint, decodes hex-encoded captured samples into an editable field tree and resends edited messages, so analysts can relate each field to the response.

  Tool · Also: App · [Requirements & evidence](https://awesomerea.org/resources/pbtk/)

<a id="agents-and-mcp"></a>
### Agents and MCP

[↑ Contents](#contents)

**Also in target sections:** [Website](#website): [Chrome DevTools MCP](https://awesomerea.org/resources/chrome-devtools-mcp/), [Playwright MCP](https://awesomerea.org/resources/playwright-mcp/), [Burp Suite MCP Server](https://awesomerea.org/resources/burp-suite-mcp-server/), [Spectral](https://awesomerea.org/resources/spectral-mcp/) · [Game](#game): [RenderDoc MCP](https://awesomerea.org/resources/renderdoc-mcp/), [Cheat Engine MCP Bridge](https://awesomerea.org/resources/cheatengine-mcp-bridge/) · [App](#app): [JADX-AI-MCP](https://awesomerea.org/resources/jadx-ai-mcp/), [apktool-mcp-server](https://awesomerea.org/resources/apktool-mcp-server/), [frida-mcp (yfe404)](https://awesomerea.org/resources/frida-mcp-yfe404/), [Super Trouper](https://awesomerea.org/resources/super-trouper/)

- [**REA — Reverse Engineer Anything**](https://github.com/morluto/rea)

  The upstream CLI and MCP server for evidence-based investigations of shipped software and runtime behavior.

  Project · Official REA · Targets: Website, Game, App, Binary, Firmware · [Requirements & evidence](https://awesomerea.org/resources/rea-upstream/)

- [**Official reverse-engineer-anything skill**](https://github.com/morluto/rea/tree/main/.agents/skills/reverse-engineer-anything)

  Target routing, connection recovery and evidence practices for agents using REA.

  Integration · Official REA · Targets: Website, Game, App, Binary, Firmware · [Requirements & evidence](https://awesomerea.org/resources/rea-official-skill/)

- [**dsh-mcp-rea**](https://github.com/Ersith/dsh-mcp-rea)

  A community MCP bridge presents a smaller selected tool surface and forwards explicit commands to the REA CLI.

  Integration · Community REA · Targets: Website, Game, App, Binary, Firmware · [Requirements & evidence](https://awesomerea.org/resources/dsh-mcp-rea/)

- [**rea-jev**](https://github.com/juan-viox/rea-jev)

  A Claude Code plugin adds Jev-based routing and evidence checks around a pinned REA MCP integration.

  Integration · Community REA · Targets: Website, App · [Requirements & evidence](https://awesomerea.org/resources/rea-jev/)

- [**rea-casebook**](https://github.com/pablodiazjorge/rea-casebook)

  A Claude Code mod collects received REA Evidence, tracks unknowns and records findings that cite delivered evidence IDs.

  Integration · Community REA · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/rea-casebook/)

- [**Eleven**](https://github.com/Zfinix/eleven)

  An agent-first desktop reverse-engineering app that opens Mach-O, ELF and PE binaries, Android packages and GPU kernels, and lets any Agent Client Protocol agent read code, rename functions, add notes and propose patches in a shared window. Native code is decompiled by Ghidra through a bundled REA build, with Rizin and jadx as alternative engines. It is a workbench around existing engines, not a new decompiler or a reconstruction case.

  Integration · Community REA · Targets: App, Binary · [Requirements & evidence](https://awesomerea.org/resources/eleven-agent-re-workbench/)

- [**REA plugin for Hermes Agent**](https://github.com/NousResearch/hermes-official-plugins/tree/main/rea)

  Nous Research’s Hermes Agent plugin package for REA. One catalog install registers REA’s MCP server, pinned to rea-agents 6.4.0 and launched through npx over stdio, with REA’s workflow skill adapted for Hermes and a separate crash-triage skill. About 170 REA tools stay behind Hermes’ on-demand tool search, and the adapted skill asks before tools that run programs, drive apps or change a connected Android device.

  Integration · Community REA · Targets: Website, App, Binary, Firmware · [Requirements & evidence](https://awesomerea.org/resources/hermes-rea-plugin/)

- [**crashlens**](https://github.com/mingleiw/crashlens)

  A crash-triage tool that turns Linux core dumps, runtime panics, exception traces and sanitizer reports into Markdown bug reports naming the crash type, the first frame in the user’s code and a stable signature. Its core-dump path calls the REA CLI to read the recorded crash and the binary layout, and can ask REA’s Ghidra provider for pseudocode of stripped functions; a Claude Code plugin bundles a skill and read-only MCP tools. It is a debugging integration around REA, not a reconstruction case, and its diagnostic accuracy remains author-reported.

  Integration · Community REA · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/crashlens-rea-crash-triage/)

- [**REA Workspace Template**](https://github.com/dobest1024/rea-workspace-template)

  A clone-first Chinese workspace template for analyzing one target per workspace with REA from Claude Code or Codex. It ships project-level REA MCP settings, agent rules that require CONFIRMED/GUESS labels with evidence locations, seven task prompts and standard-library scripts that hash imported originals, stage writable copies and strip values from HAR captures. It organizes analysis rather than performing it, and its acceptance run used only synthetic samples.

  Integration · Community REA · Targets: Website, App, Binary · [Requirements & evidence](https://awesomerea.org/resources/rea-workspace-template/)

- [**Hex-Rays IDA MCP**](https://github.com/HexRaysSA/ida-mcp)

  Official Hex-Rays MCP server for agent access to IDA databases, with headless operation and optional GUI integration.

  Integration · Independent MCP · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/hex-rays-ida-mcp/)

- [**GhidraMCP**](https://github.com/LaurieWired/GhidraMCP)

  Ghidra extension and MCP bridge exposing decompilation, symbol navigation and renaming to agents, with GUI and headless modes.

  Integration · Independent MCP · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/ghidramcp/)

- [**Binary Ninja MCP (official)**](https://docs.binary.ninja/guide/mcp.html)

  Binary Ninja's own MCP interface exposes functions, symbols, disassembly, intermediate languages and decompiled text to agents.

  Integration · Independent MCP · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/binary-ninja-official-mcp/)

- [**Binary Ninja MCP (fosdickio)**](https://github.com/fosdickio/binary_ninja_mcp)

  Community Binary Ninja plugin and bridge for MCP clients, including workflows that switch among multiple open binaries.

  Integration · Independent MCP · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/binary-ninja-community-mcp/)

- [**IDA Pro MCP (mrexodia)**](https://github.com/mrexodia/ida-pro-mcp)

  Community IDA integration useful for existing setups and migration context; its maintainer now recommends the official Hex-Rays MCP server.

  Integration · Independent MCP · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/ida-pro-mcp-community/)

- [**Radare2 MCP Server**](https://github.com/radareorg/radare2-mcp)

  Native radare2 MCP server offering binary-analysis tools, reusable sessions and configurable read-only access.

  Integration · Independent MCP · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/radare2-mcp/)

- [**r2ai**](https://github.com/radareorg/r2ai)

  AI plugins inside radare2 for function explanations, naming suggestions and model-assisted decompilation using local or remote models.

  Integration · Independent agent · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/r2ai/)

- [**DAILA**](https://github.com/mahaloz/DAILA)

  Decompiler-independent AI assistant for function summaries and naming across IDA, Ghidra, Binary Ninja and angr-management.

  Integration · Independent agent · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/daila/)

- [**RevEng.AI Ghidra Plugin**](https://github.com/RevEngAI/plugin-ghidra)

  Connects Ghidra to RevEng.AI for function similarity, recovered names, AI explanations and agent-assisted annotation.

  Integration · Independent agent · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/revengai-ghidra/)

- [**LLDB MCP**](https://lldb.llvm.org/use/mcp.html)

  LLDB's official MCP interface gives agents debugger sessions and commands for breakpoints, memory inspection and stepping.

  Integration · Independent MCP · Targets: App, Binary · [Requirements & evidence](https://awesomerea.org/resources/lldb-mcp/)

- [**Claude Reverse Engineering Skill**](https://github.com/EncidXVII/claude-reverse-engineering-skill)

  Community agent skill for triage, headless exports and evidence-based RE reports; explicitly documents workflows with REA and other MCP servers.

  Integration · Independent agent · Targets: App, Binary · [Requirements & evidence](https://awesomerea.org/resources/claude-reverse-engineering-skill/)

- [**SpecterOps Reverse Engineering Skills**](https://github.com/SpecterOps/skills/tree/main/plugins/reverse-engineering)

  Focused Binary Ninja and Ghidra analysis skills that describe MCP tool use, analysis recipes and annotation practices.

  Integration · Independent agent · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/specterops-re-skills/)

- [**pyghidra-mcp**](https://github.com/clearbluejar/pyghidra-mcp)

  PyGhidra-based MCP server that analyzes every binary in a Ghidra project and exposes decompilation, cross-references, call graphs, symbol and string search, indexed semantic code search, and renaming, typing and comment edits. A separate HTTP CLI client and an optional mode driving a Ghidra GUI it launches are included.

  Integration · Independent MCP · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/pyghidra-mcp/)

- [**LeanREA**](https://github.com/aicodeking/leanrea)

  An independent agent skill that routes application and binary investigations through ordinary command-line tools. It supplies batched triage recipes, targeted source/disassembly reading and explicit seen/inferred/unknown evidence labels, accompanied by a small author-reported comparison against an REA MCP workflow.

  Integration · Independent agent · Targets: App, Binary · [Requirements & evidence](https://awesomerea.org/resources/leanrea-skill/)

- [**Universal Modder**](https://github.com/rehan-remade/universal-modder)

  Packages agent skills, three role briefs, a Python CLI and preconfigured fal MCP settings for modding PC games the user owns. Its reverse-engineering guidance sends managed, native and data-format work to external decompilers and debuggers, and requires a round-trip check before a reverse-engineered file format is used; one worked example ships an Age of Empires II sprite writer built this way. It is a modding toolkit with agent-written field notes, not a game decompilation, and its example results remain project-reported.

  Integration · Independent agent · Targets: Game · [Requirements & evidence](https://awesomerea.org/resources/universal-modder-agent-toolkit/)

- [**ReVa (Reverse Engineering Assistant)**](https://github.com/cyberkaida/reverse-engineering-assistant)

  Ghidra extension that runs an MCP server inside Ghidra, giving agents decompilation with namespace and cross-reference context, symbol, string, data-type, structure and call-graph tools, program diffing, renaming and PyGhidra scripting. Its README attributes the project's distinction to tool design for LLM use: many small tools whose schemas tolerate other input, redirect correctable mistakes and return short fragments linked to related information. Assistant mode serves an open Ghidra project to several clients at once; headless mode starts Ghidra itself with session-scoped projects.

  Integration · Independent MCP · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/reva-ghidra-mcp/)

- [**x64dbg-MCP Server**](https://github.com/duty1g/x64dbg-mcp-server)

  Native x64dbg plugin, written in Zig for both x32dbg and x64dbg, that serves an MCP endpoint over streamable HTTP and SSE from inside the debugger. Agents can load or attach to a process, set software, hardware, memory and conditional breakpoints, step and trace, read registers, call stacks, threads, memory maps, imports, strings and cross-references, and run arbitrary x64dbg commands. A bundled SKILL.md guide tells agents to confirm the debugger state before every action.

  Integration · Independent MCP · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/x64dbg-mcp-server/)

- [**mcp-windbg**](https://github.com/svnscha/mcp-windbg)

  Independent, community-built MCP server that runs Microsoft's cdb.exe and kd.exe headless, so agents can open and triage user-mode and kernel crash dumps, attach to cdb remote debug servers and KD kernel targets, and run arbitrary debugger commands in separately addressed sessions. Its README points users who want AI inside WinDbg to Microsoft's official WinDbg MCP and positions this project as an alternative for other MCP clients, remote HTTP use and batch dump triage; it calls itself a wrapper that runs real debugger commands, not an automatic fix.

  Integration · Independent MCP · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/mcp-windbg/)

- [**Wireshark MCP**](https://github.com/bx33661/Wireshark-MCP)

  MCP server that wraps tshark, and optionally other Wireshark command-line tools, so agents can query saved captures through Wireshark's dissectors: packet lists and details, stream following, arbitrary field extraction, protocol hierarchies and conversations, decode-as rules for non-standard ports, protocol preferences, TLS and WPA decryption with user-supplied keys, and one tool that applies preset fields and filters for 25 protocols such as Modbus, S7comm, MQTT, Zigbee and BLE. Separate security-heuristic, live-capture and capture-editing tools sit beside the dissection tools.

  Integration · Independent MCP · Targets: Protocol · [Requirements & evidence](https://awesomerea.org/resources/wireshark-mcp/)

- [**BINNY**](https://github.com/openbin-ai/binny)

  An open-source terminal agent harness from OpenBin that runs a user-chosen hosted or local model over binary-analysis data. It reads decompiled functions, strings, imports and data from an OpenBin or OpenAPK project or a local Ghidra container run, follows triage, investigation and drafting playbooks, and saves a draft malware-analysis or vulnerability-research report for human review. It is an analysis harness with draft outputs, not a reconstruction project.

  Integration · Independent agent · Targets: App, Binary, Firmware · [Requirements & evidence](https://awesomerea.org/resources/binny-agent-harness/)

- [**decomp.wtf**](https://github.com/i12bp8/decomp.wtf)

  A discontinued local app and MCP server that hands AI coding agents one function of a user-owned console game at a time, compiles each C attempt with the game’s period compiler and accepts it only when the linked result matches the original bytes. It can start a project from a ROM or disc image, or work inside forks of public decompilation projects listed on decomp.dev, where objdiff judges the result. Its final commit, dated 15 October 2026, marks it discontinued in response to opposition in the decompilation community; the code stays under MIT without further fixes or releases.

  Integration · Independent agent · Targets: Game · [Requirements & evidence](https://awesomerea.org/resources/decomp-wtf-agent-decompilation/)

- [**Claude Intercept**](https://github.com/whaesemeyer/claude-intercept)

  A local man-in-the-middle proxy and dashboard that captures HTTP/S traffic from the user’s own computer and devices, stores it in SQLite and hands it to Claude Code through an /intercept skill and CLI. Exports such as API documentation and traffic summaries support investigating request patterns and undocumented endpoints. It is an agent-facing capture tool for authorized testing, not a reconstruction case, and it has no established REA connection.

  Integration · Independent agent · Targets: App, Protocol · [Requirements & evidence](https://awesomerea.org/resources/claude-intercept-traffic-capture/)

- [**Ghidra MCP Server (bethington)**](https://github.com/bethington/ghidra-mcp)

  A Ghidra GUI plugin, standalone headless server and Python MCP bridge exposing a 209-tool catalog: decompilation, cross-references, renaming, typing, structures, comments and batch edits, plus P-code emulation, live debugging through Ghidra’s TraceRmi framework, shared Ghidra Server repository and version-control operations, and hash-based transfer of function documentation between binary versions. The bridge loads three tool groups on connect and lets the model search for and load the rest, while naming and type conventions are enforced in the tool layer. Its NOTICE says it began as a derivative of LaurieWired’s GhidraMCP in August 2025 and has since been substantially rewritten and extended.

  Integration · Independent MCP · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/ghidra-mcp-bethington/)

- [**DecompilerServer**](https://github.com/pardeike/DecompilerServer)

  Stdio MCP server built on the ICSharpCode.Decompiler engine that lets agents load managed .NET assemblies, including a Unity game's Assembly-CSharp.dll located from its game directory, then search symbols, string literals and attributes, read decompiled C# or IL, and trace callers, callees, usages and inheritance. Several assemblies stay loaded under aliases, so an agent can compare two versions structurally or diff individual method bodies, the README's example being RimWorld mod porting. Modding-oriented tools generate Harmony patch skeletons, detour stubs and transpiler anchor suggestions as text from the inspected members.

  Integration · Independent MCP · Targets: Game, App · [Requirements & evidence](https://awesomerea.org/resources/decompilerserver-dotnet-mcp/)

- [**Gepetto**](https://github.com/JusticeRage/Gepetto)

  IDA Pro plugin that sends Hex-Rays pseudocode to a hosted or local language model the user selects, to explain a function, comment it or propose new variable and function names, which the user picks from before they are applied. A chat console inside IDA also lets the model call tools that read disassembly, decompilation, cross-references, strings and types, rename and comment the database and run Python. The README warns that these general-purpose models may well be wrong and asks users to treat every result critically.

  Integration · Independent agent · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/gepetto/)

- [**GhidrAssistMCP**](https://github.com/symgraph/GhidrAssistMCP)

  Ghidra extension that runs an MCP server inside Ghidra over streamable HTTP and legacy SSE, with 100 explicitly named tools (93 enabled by default) for pseudocode, disassembly, P-code, control-flow and call graphs, cross-references, strings, imports and exports, plus renaming, retyping, comments and structure inference. Since version 3.0.0 the server starts with the project manager, so agents can create, open, save and close projects and open programs before a CodeBrowser exists, while one shared server tracks whichever CodeBrowser window has focus. Six program resource templates, seven analysis prompts and a bundled script for running the server under analyzeHeadless complete the package.

  Integration · Independent MCP · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/ghidrassistmcp/)

- [**Android Reverse Engineering Skill**](https://github.com/SimoneAvogadro/android-reverse-engineering-skill)

  Claude Code plugin and agent skill that drives jadx and Fernflower/Vineflower to decompile Android APK, XAPK, JAR and AAR files and document their HTTP APIs. A fingerprint pass first identifies the app's framework, HTTP stack, obfuscation level and native libraries, then shell scripts extract endpoints and authentication patterns across Retrofit, OkHttp, Volley, Ktor and Apollo/GraphQL, trace call flows from UI down to the network layer, and rebuild original Kotlin class names from the metadata R8 leaves behind. It installs through the bundled Claude Code marketplace, and its scripts also run standalone with a /decompile slash command.

  Integration · Independent agent · Targets: App · [Requirements & evidence](https://awesomerea.org/resources/android-reverse-engineering-skill/)

- [**Reverify**](https://github.com/2akouwu/reverify)

  Python CLI and stdio MCP server that checks a model’s structured claims about a binary, such as bytes or typed values at an offset, strings, imports and exports, instruction mnemonics, emulation results and tested or Z3-proved equivalence, and returns VERIFIED, REFUTED or INCONCLUSIVE with the evidence the tools observed. Grounded and refuted results are kept in a per-binary ledger on disk, so a reset or later session resumes from them instead of from a summary, and a reconstruct loop has a model propose claims until an informative set verifies. A separate rollover command replaces context compaction in Claude Code, Codex, Gemini CLI or OpenCode with file hand-offs and fresh sessions.

  Integration · Independent agent · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/reverify-claim-verifier/)

- [**DecompAI**](https://github.com/louisgthier/decompai)

  Gradio chat application whose LangGraph ReAct agent analyses an uploaded x86 Linux ELF binary: it lists and disassembles functions, decompiles them with Ghidra, drives radare2 and gdb, and runs shell commands and Python scripts in a privileged Kali Linux runner container. Workspaces are keyed by the binary’s SHA-256, so uploading the same file again restores the session. It came out of a school research project, and its CTF results are the authors’ own report.

  Integration · Independent agent · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/decompai/)

- [**Kong**](https://github.com/amruth-sn/kong)

  Command-line pipeline that runs Ghidra in-process through PyGhidra and asks Claude, OpenAI or OpenAI-compatible models to name the functions, types and parameters of a stripped binary, working bottom-up through the call graph so callers see already-named callees. It matches known library and cryptographic signatures first, sends functions whose decompilation looks obfuscated through a tool-using deobfuscation pass with z3-based simplification, applies results to the Ghidra program and exports annotated C and an analysis.json file. Its README calls it the first agentic reverse engineer; that label and its accuracy and cost figures are the author’s claims.

  Integration · Independent agent · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/kong-agentic-reverse-engineer/)

- [**Co-op Anything**](https://github.com/cranebeaker/coop-anything)

  Agent playbook, skill set and stdio MCP server for adding online or split-screen co-op to single-player games the players already have installed. Agents either revive an existing co-op mod or reverse engineer the game and engine to build one, test it with in-game bots and send their notes back, while the MCP server searches a directory of 223 co-op projects and 32 open gaps, detects a game’s engine from its install folder and records the executable’s identity. Its README and reverse-engineering skill pair it with REA for native code, and two game write-ups report observations made through REA’s Ghidra lane.

  Integration · Community REA · Targets: Game · [Requirements & evidence](https://awesomerea.org/resources/coop-anything/)

- [**DeepExtract (DeepExtractIDA)**](https://github.com/marcosd4h/DeepExtractIDA)

  IDA Pro 9.x plugin and PowerShell batch extractor that turn Windows PE files into material AI coding agents can read: a per-binary SQLite database of PE metadata, signatures, disassembly, Hex-Rays pseudocode, cross-references, strings, stack frames, loops and dangerous API calls, plus optional grouped C++ and assembly files with per-function caller, callee and string headers and JSON indexes. It runs headless over directories, file lists or the modules of a running process, or interactively on the open IDA database, keeping the analyst’s renames and comments. The agent commands that work on this output come from the separate DeepExtractRuntime project.

  Integration · Independent agent · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/deepextract-ida/)

- [**Mizuchi**](https://github.com/macabeus/mizuchi)

  Plugin pipeline for matching decompilation that loops over functions in an existing decomp project: m2c drafts C, decomp-permuter mutates it, Claude rewrites it through a compile-and-diff tool, and objdiff accepts a result only when the compiled object matches the target assembly. A local Decomp Atlas web app indexes matched and unmatched functions with call graphs and code embeddings, helps pick the next function and builds prompts, while HTML reports summarise each run. An optional integrator places matched C into a git worktree, checks the build and can commit, push or open a PR.

  Integration · Independent agent · Targets: Game, Binary · [Requirements & evidence](https://awesomerea.org/resources/mizuchi-matching-decompilation-pipeline/)

- [**ReAgent**](https://github.com/Dryxio/reagent)

  An open-source Python agent, published on PyPI as auto-re-agent, that drafts C/C++ implementations of functions in a compiled program from Ghidra evidence and has a separately configurable checker model review each draft in a bounded fix loop. A candidate is accepted only after a structural comparison with the decompile, assembly, control-flow and P-code evidence, the project’s own build, test and optional differential commands, and 11 heuristic parity signals. The README calls these gates conservative evidence, not proof of equivalence, and the tool writes candidates to an overlay rather than patching the source tree.

  Integration · Independent agent · Targets: Game, Binary · [Requirements & evidence](https://awesomerea.org/resources/reagent-cpp-reconstruction-agent/)

- [**ReverserAI**](https://github.com/mrphrazer/reverser_ai)

  Binary Ninja plugin that suggests function names from HLIL decompiler output with a language model run locally through llama.cpp; the README says it operates entirely offline once the model is downloaded. It can rename the current function, every function still carrying a default sub\_ name in call-graph post-order, or only those referencing strings and imported or library symbols. The author presents it as a research proof of concept whose only implemented task is function naming.

  Integration · Independent agent · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/reverser-ai/)

<a id="related-collections"></a>
### Related Collections

[↑ Contents](#contents)

- [**Awesome Reverse Engineering**](https://github.com/morluto/awesome-reverse-engineering)

  A task-oriented reverse-engineering resource list by REA's maintainer, useful for broader tools and foundations.

  Collection · REA maintainer · Targets: Website, Game, App, Binary, Firmware · [Requirements & evidence](https://awesomerea.org/resources/morluto-awesome-re/)

- [**Awesome REA Cases**](https://github.com/songshikang0111/awesome-REA-cases)

  A bilingual collection of REA and other AI-assisted reverse engineering cases, with source links and explicit distinctions between reported and reproduced outcomes.

  Collection · Community REA · Targets: Website, Game, App, Binary, Firmware · [Requirements & evidence](https://awesomerea.org/resources/awesome-rea-cases/)

- [**awesome-rea (yibie): verification-focused projects and practice reports**](https://github.com/yibie/awesome-rea)

  Organizes AI-assisted game decompilation, native ports, static recompilation and tooling around stated acceptance checks, alongside a separate track of practitioner write-ups and discussions. Useful for finding primary reports and comparing how projects define correctness.

  Collection · Community REA · Targets: Game, Binary · [Requirements & evidence](https://awesomerea.org/resources/yibie-awesome-rea/)

- [**Awesome REA/Decompiled Games**](https://github.com/HaozheH3/awesome-rea-games)

  Groups game decompilations, source reconstructions, recompilations, native ports and demos by original game, with comparison rows linking related projects. It distinguishes launchers, engine work and creator-shared showcases from source-reconstruction efforts.

  Collection · Community REA · Targets: Game · [Requirements & evidence](https://awesomerea.org/resources/haozhe-awesome-rea-games/)

- [**Reversed with AI**](https://reversedwithai.com/)

  A moderated website directory of AI-assisted reverse-engineering projects across games, firmware, file formats, APIs and protocols, apps and legacy software. Each entry links to its primary source and records the author-reported model, tools, time, cost and outcome, with four checks for public source, reproduction steps, real-hardware testing and third-party confirmation.

  Collection · Community REA · Targets: Game, App, Binary, Firmware, Protocol · [Requirements & evidence](https://awesomerea.org/resources/reversed-with-ai-directory/)

- [**awesome-game-decompilations**](https://github.com/CharlotteCross1998/awesome-game-decompilations)

  A single-README list of about 480 game decompilation, recompilation and disassembly projects, grouped by console from the NES and Game Boy to the Xbox 360, PC and mobile, with a large uncategorised section. Each entry is a game title linked to its project, mostly on GitHub, and entries with AI involvement are marked with a warning emoji under the maintainer’s disclosure policy.

  Collection · Targets: Game · [Requirements & evidence](https://awesomerea.org/resources/awesome-game-decompilations/)

<a id="references-and-learning"></a>
### References and Learning

[↑ Contents](#contents)

- [**Installation and client setup**](https://github.com/morluto/rea/blob/main/docs/installation.md)

  Reviewed setup plans, client registration, provider prerequisites and scoped readiness checks.

  Documentation · Official REA · Targets: Website, Game, App, Binary, Firmware · [Requirements & evidence](https://awesomerea.org/resources/rea-installation/)

- [**CLI and Evidence**](https://github.com/morluto/rea/blob/main/docs/cli.md)

  CLI workflows for saving Evidence and projecting smaller views from completed analysis.

  Documentation · Official REA · Targets: Website, Game, App, Binary, Firmware · [Requirements & evidence](https://awesomerea.org/resources/rea-cli-evidence/)

- [**MCP contracts and generated catalog**](https://github.com/morluto/rea/blob/main/docs/mcp-contracts.md#generated-catalog)

  Canonical tool contracts, provider discovery and Evidence semantics for integration authors.

  Documentation · Official REA · Targets: Website, Game, App, Binary, Firmware · [Requirements & evidence](https://awesomerea.org/resources/rea-mcp-contracts/)

- [**Native binary investigation**](https://github.com/morluto/rea/blob/main/docs/native-investigation.md)

  Locate a function, inspect instructions and pseudocode, and follow references with a selected native provider.

  Documentation · Official REA · Targets: Game, Binary · [Requirements & evidence](https://awesomerea.org/resources/rea-native-workflow/)

- [**Cross-layer JavaScript application workflows**](https://github.com/morluto/rea/blob/main/docs/javascript-application-workflows.md)

  Trace features and compare authenticated JavaScript application graphs while preserving static-analysis limits.

  Documentation · Official REA · Targets: Website, App · [Requirements & evidence](https://awesomerea.org/resources/rea-js-workflows/)

- [**Static Android APK analysis**](https://github.com/morluto/rea/blob/main/docs/android-analysis.md)

  Inspect Android package identity, classes, methods and references through REA's JADX integration.

  Documentation · Official REA · Targets: App · [Requirements & evidence](https://awesomerea.org/resources/rea-android-guide/)

- [**Managed-code analysis**](https://github.com/morluto/rea/blob/main/docs/managed-code-analysis.md)

  Read PE/CLI metadata and CIL, compare managed members and inspect declared native boundaries without loading the assembly.

  Documentation · Official REA · Targets: App · [Requirements & evidence](https://awesomerea.org/resources/rea-managed-guide/)

- [**Historical web network captures**](https://github.com/morluto/rea/blob/main/docs/web-network-captures.md)

  Inspect saved web captures offline; recorded URLs are not fetched and no proxy is started.

  Documentation · Official REA · Targets: Website, App, Protocol · [Requirements & evidence](https://awesomerea.org/resources/rea-web-captures/)

- [**Firmware analysis**](https://github.com/morluto/rea/blob/main/docs/firmware-analysis.md)

  Inspect firmware regions with Binwalk and explicitly extract with Unblob, retaining tool and artifact identity.

  Documentation · Official REA · Targets: Firmware · [Requirements & evidence](https://awesomerea.org/resources/rea-firmware-guide/)

- [**Recorded packet capture inspection**](https://github.com/morluto/rea/blob/main/docs/packet-captures.md)

  Select TShark fields, display filters and decode-as rules over an existing network, USB or Bluetooth capture, and look up installed field names. It does not capture traffic, open an interface or control a device.

  Documentation · Official REA · Targets: Protocol · [Requirements & evidence](https://awesomerea.org/resources/rea-packet-captures/)

- [**Packet capture summaries**](https://github.com/morluto/rea/blob/main/docs/pcap-analysis.md)

  Summarize a saved pcap or pcapng file’s endpoints, DNS questions and addresses, TLS SNI, protocol stacks and HTTP URIs into paged Evidence views. It does not capture traffic or fetch recorded targets.

  Documentation · Official REA · Targets: Protocol · [Requirements & evidence](https://awesomerea.org/resources/rea-pcap-summaries/)

- [**Recorded signal decoding**](https://github.com/morluto/rea/blob/main/docs/signal-recordings.md)

  Run caller-chosen sigrok protocol decoders, such as UART or I2C, over an existing logic-signal recording and keep annotation text with sample ranges. It does not acquire samples or communicate with hardware.

  Documentation · Official REA · Targets: Firmware, Protocol · [Requirements & evidence](https://awesomerea.org/resources/rea-signal-recordings/)

- [**Browser observation guide**](https://rea.tools/guides/browser/)

  Follow a user-triggered export request in the supplied Notes browser example and connect it to the downloaded result.

  Documentation · Official REA · Targets: Website · [Requirements & evidence](https://awesomerea.org/resources/rea-browser-guide/)

- [**JavaScript and Electron: follow a CSV export**](https://rea.tools/guides/javascript/)

  A source-owned Notes fixture teaches the renderer, preload, IPC and CSV path with linked analysis evidence.

  Documentation · Official REA · Targets: App · [Requirements & evidence](https://awesomerea.org/resources/rea-electron-guide/)

- [**rea-playbook**](https://github.com/jinshi666888/rea-playbook)

  An Electron practice target, Evidence extractor and MCP probe; offline fixture mode is distinguished from real REA analysis.

  Learning resource · Community REA · Targets: App · [Requirements & evidence](https://awesomerea.org/resources/rea-playbook/)

- [**rea-lab**](https://github.com/pablodiazjorge/rea-lab)

  A Windows REA/Ghidra lab with seeded challenges, published studies, upstream contributions and recorded limitations.

  Research · Community REA · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/rea-lab/)

- [**Flutter build identification**](https://github.com/morluto/rea/blob/main/docs/flutter-analysis.md)

  Identifies a Flutter APK’s Dart snapshot hash, per-ABI library digests and engine build provenance, then inspects one ABI’s AOT snapshot sections, through REA’s pure-parsing CLI and MCP tools. The string-pool output is a bounded byte-pattern projection of package and SDK URIs, not deserialized Dart classes or recovered source.

  Documentation · Official REA · Targets: App · [Requirements & evidence](https://awesomerea.org/resources/rea-flutter-guide/)

- [**Static HarmonyOS package inventory**](https://github.com/morluto/rea/blob/main/docs/harmony-analysis.md)

  Inventories HarmonyOS HAP, HSP and App Pack files through REA’s hardened ZIP reader and projects an execution-free application graph: component paths, IDs and hashes, Stage/FA packaging hints, runtime-family hints and path-based native-bridge hypotheses. Every claim rests on path presence; manifests, Ark bytecode, resources and signatures are not decoded or verified.

  Documentation · Official REA · Targets: App · [Requirements & evidence](https://awesomerea.org/resources/rea-harmony-guide/)

- [**MIPS ELF analysis through Ghidra**](https://github.com/morluto/rea/blob/main/docs/ghidra-mips.md)

  Documents REA’s Ghidra lane for MIPS ELF executables, relocatable objects and MIPS16 shared images, including a pinned 32-bit language for recordless legacy firmware executables that Ghidra would otherwise import as 64-bit. Admission is bounded by declared header and ABI-record facts, and verification compares source-owned fixtures with independent readelf output rather than executing or rehosting firmware.

  Documentation · Official REA · Targets: Binary, Firmware · [Requirements & evidence](https://awesomerea.org/resources/rea-ghidra-mips-guide/)

- [**PSP static ELF analysis through Ghidra**](https://github.com/morluto/rea/blob/main/docs/ghidra-psp.md)

  Documents REA’s bounded Ghidra profile for static PSP ELF executables, which leaves Allegrex instructions, PSP loading and calling conventions to a caller-installed ghidra-allegrex extension while reusing REA’s CLI, MCP, Evidence and snapshot workflows. It admits one PSPSDK header and ABI declaration on Linux x64 and verifies selected static facts on a self-built fixture, not commercial games or PRX modules.

  Documentation · Official REA · Targets: Game, Binary · [Requirements & evidence](https://awesomerea.org/resources/rea-ghidra-psp-guide/)

- [**NativeAOT metadata recovery with Ghidra**](https://github.com/morluto/rea/blob/main/docs/ghidra-nativeaot.md)

  Recovers .NET 8 NativeAOT metadata from x64 PE executables during REA’s Ghidra analysis: MethodTable relationships, virtual slots and frozen strings from RTR 9.1 data, through a built-in read-only parser or an optional headless adapter that annotates the Ghidra database. Generated names, inferred prototypes and recovered native pseudocode stay separate from the unknown original C# names, fields and source.

  Documentation · Official REA · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/rea-ghidra-nativeaot-guide/)

- [**OpenSecurityTraining2**](https://ost2.fyi/)

  Free self-paced security courses with learning paths for reverse engineering, firmware and systems foundations.

  Learning resource · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/ost2/)

- [**pwn.college: Reverse Engineering**](https://pwn.college/program-security/reverse-engineering/)

  Hands-on reverse-engineering module covering functions, data access, static tools and dynamic tools with hosted exercises.

  Learning resource · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/pwn-college-re/)

- [**Reverse Engineering for Beginners**](https://beginners.re/)

  Dennis Yurichev's free book on understanding compiled programs and assembly, available in multiple languages.

  Learning resource · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/re-for-beginners/)

- [**The Official Radare2 Book**](https://book.rada.re/)

  Official practical reference for radare2 analysis, disassembly, scripting, debugging and related plugins.

  Learning resource · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/radare2-book/)

- [**Finding Jingle Town: Debugging an N64 Game without Symbols**](https://blog.chrislewis.au/finding-jingle-town-debugging-an-n64-game-without-symbols/)

  A walkthrough from the Snowboard Kids 2 decompilation project on attaching gdb-multiarch to the Ares emulator while the matching build still cannot carry debug information. It breaks on a function by its ELF symbol name and reads one structure byte by hand to test whether that byte selects the level overlay. A short method note on checking decompilation hypotheses at runtime, not a reconstruction result.

  Learning resource · Targets: Game · [Requirements & evidence](https://awesomerea.org/resources/finding-jingle-town-n64-debugging/)

- [**JPCERT/CC: APK analysis and API probing on attack servers**](https://blogs.jpcert.or.jp/ja/2026/10/web_api_attacks.html)

  JPCERT/CC’s 15 October 2026 blog post on the infrastructure behind a series of unauthorized-access incidents in Japan. It reports that the attackers used AI for known-vulnerability scanning and API attacks, and that attack servers held APKs, jadx- and Blutter-related files, APK-extraction directories and an SSRF test script used to probe app APIs. It is a defender’s account of observed attacker tooling with mitigation advice, not a published AI-assisted analysis method or reproducible workflow.

  Learning resource · Targets: App · [Requirements & evidence](https://awesomerea.org/resources/jpcert-apk-api-attack-infrastructure-report/)

- [**Reverse Engineering (mytechnotalent)**](https://github.com/mytechnotalent/Reverse-Engineering)

  A free, English lesson index by mytechnotalent that grows almost daily: 490 numbered lessons, most of which have learners write small programs and then debug and patch ("hack") them, across x86, x64, 32/64-bit ARM, RISC-V and AVR. Early courses start from number systems, registers, memory and the stack; later ones cover microcontroller firmware on Raspberry Pi Pico/Pico 2, STM32F401, ESP32-C3, ATmega328P and micro:bit boards, plus Windows, Go, Rust and WebAssembly programs. The README is a table of links; the lesson text lives in a GitBook and in the author's other repositories and PDF books.

  Learning resource · Targets: Binary, Firmware · [Requirements & evidence](https://awesomerea.org/resources/mytechnotalent-reverse-engineering/)

- [**Z0FCourse Reverse Engineering**](https://github.com/0xZ0F/Z0FCourse_ReverseEngineering)

  A free English course by Z0F on reverse engineering 64-bit Windows programs, which its README pitches as taking learners from beginner to intermediate. Markdown lessons move from number systems, x64 registers, memory layout and calling conventions to x64dbg and Ghidra, then reverse small samples and an author-written DLL, recovering a Player class and calling the DLL's exports from a program of one's own. The unfinished later chapters introduce Windows internals and reverse ntdll's generic-table functions.

  Learning resource · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/z0f-reverse-engineering-course/)

- [**OWASP Mobile Application Security Testing Guide (MASTG)**](https://mas.owasp.org/MASTG/)

  OWASP’s open manual for Android and iOS app security testing and reverse engineering, published at mas.owasp.org. Chapters on platform internals, test setup and app tampering and reverse engineering sit beside modular, individually referenced tests, techniques, tool pages, knowledge articles, best practices and runnable demos, all mapped to MASVS controls and MASWE weaknesses. OWASP’s UnCrackable crackme apps serve as practice targets and examples.

  Learning resource · Targets: App · [Requirements & evidence](https://awesomerea.org/resources/owasp-mastg/)

- [**The Decompilation Wiki**](https://decompilation.wiki/)

  Community wiki explaining how decompilers work, from disassembly, lifting and control-flow recovery to type recovery, control-flow structuring, quality evaluation and neural decompilation, citing the research behind each technique. It also keeps directories of decompilers, plugins, blogs and talks, pages on applied research such as symbol recovery, code similarity and vulnerability discovery, and a table of about 240 game reconstruction projects by original platform.

  Learning resource · Targets: Game, Binary · [Requirements & evidence](https://awesomerea.org/resources/decompilation-wiki/)

- [**Frontkick vs Rikugan: a CREBench agent comparison**](https://www.synacktiv.com/en/publications/ufc-666-frontkick-vs-rikugan)

  Matthieu Breuil’s Synacktiv article explains tool-calling and code-executing agent designs and describes Frontkick, a CodeAct agent that runs generated Python inside Binary Ninja. It compares Frontkick with the open-source Rikugan plugin on two CREBench cryptographic binary tasks, then attributes most of Frontkick’s advantage to a prompt that listed installed Python libraries rather than to its architecture. It is a small evaluation write-up with per-run results, not a released tool or a general benchmark finding.

  Learning resource · Targets: Binary · [Requirements & evidence](https://awesomerea.org/resources/frontkick-rikugan-crebench-comparison/)
<!-- END GENERATED CATALOG -->

<!-- BEGIN GENERATED PAPERS -->
<a id="papers"></a>
## Papers

**87 papers**, grouped by topic and ordered newest first. Each entry shows its venue and publication status.

[Browse the paper directory](https://awesomerea.org/papers/) · [Complete bibliography JSON](data/papers.json) · [Suggest a paper](https://github.com/reacher-z/Awesome-REA/issues/new?template=paper.yml)

**By topic**

- [Agent evaluation](#papers-agent-evaluation) (9) · [Decompilation](#papers-decompilation) (34) · [Websites](#papers-website-reconstruction) (15)
- [Games](#papers-game-reconstruction) (6) · [Apps](#papers-app-reconstruction) (7) · [Firmware](#papers-firmware-analysis) (6)
- [Protocols](#papers-protocol-analysis) (10)

Open “Scope and publication details” for each study’s full limitations. Some papers also appear among curated resources; counts are not additive.

<a id="papers-agent-evaluation"></a>
### Reverse-engineering agent evaluation

[↑ Paper topics](#papers) · [Contents](#contents)

- [**Humans vs. Machines: A Comparison With AI Agents in Software Reverse Engineering**](https://arxiv.org/abs/2610.14960)

  Compares human and LLM-agent understanding and navigation on the same static reverse-engineering challenges, then studies how binary representations consume context windows.

  arXiv 2026 · Preprint · [PDF](https://arxiv.org/pdf/2610.14960) · [Full entry & citation](https://awesomerea.org/papers/paper-humans-machines-sre/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Understanding is graded on two compact challenges; the separate 4,000-binary study measures context capacity, not task-solving accuracy. The interface is static IDA/MCP without dynamic execution, and prior exposure to challenge source remains an acknowledged validity threat.

  **Authors:** Samuele Doria et al.

  </details>

- [**The Next Challenge for Agentic Cybersecurity: A Realistic, Contamination-Free Reverse Engineering Benchmark**](https://arxiv.org/abs/2608.11469)

  Introduces SRE-Bench, with privately authored programs and protected binary variants, to study agent recovery of program semantics while reducing training-data contamination.

  arXiv 2026 · Preprint · [PDF](https://arxiv.org/pdf/2608.11469) · [Full entry & citation](https://awesomerea.org/papers/paper-sre-bench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The revised study reports 19 programs, 262 binary instances, and 1,572 graded tasks. Binaries and task instances are not publicly released; access is through an evaluation service. Its contamination-control claim is the authors' methodology, not an independent guarantee.

  **Authors:** Jeremy Spence et al.

  </details>

- [**Automatically Attacking Software Reverse Engineering AI Agents**](https://papers.academic-conferences.org/index.php/eccws/article/view/4597)

  A proof of concept for indirect prompt injection against Cline/GhidraMCP binary-analysis agents. An adapted AutoDAN generates embedded strings that make the agent describe different behavior. The authors demonstrate four small C programs with Qwen3-8B and transfer the examples to GPT-OSS-120B.

  ECCWS 2026 · Conference paper · [PDF](https://papers.academic-conferences.org/index.php/eccws/article/download/4597/4412/17540) · [Full entry & citation](https://awesomerea.org/papers/paper-attacking-re-ai-agents/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Four illustrative programs, each with one or two functions; no repeated-trial success rate, realistic malware corpus or defense evaluation. The reported decompiler setting truncates strings beyond 2,048 characters. These examples do not establish general reliability across models or complex binaries.

  **Authors:** Brian Crawford et al.

  </details>

- [**CrackMeBench: Binary Reverse Engineering for Agents**](https://arxiv.org/abs/2605.10597)

  Evaluates agents on executable-checked CrackMe tasks: infer validation logic from binaries and submit an accepted input or artifact, while recording tool use, time, and scoring attempts.

  arXiv 2026 · Preprint · [PDF](https://arxiv.org/pdf/2605.10597) · [Full entry & citation](https://awesomerea.org/papers/paper-crackmebench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The v0 study uses 12 generated tasks and eight public calibration tasks, Linux x86-64 ELF binaries, a shell interface, and a five-minute budget. Its compact educational tasks do not establish performance on large applications. No paper-linked public artifact URL was verified.

  **Authors:** Isaac David et al.

  </details>

- [**Towards LLM-Resistant Software Protection: Agent Failure Patterns in CTF Reverse Engineering**](https://www.ndss-symposium.org/ndss-paper/auto-draft-657/)

  Runs Claude Code, Codex CLI and ChatGPT-5.2 Pro on 24 crackme-style challenges selected from 15 international CTF events held in 2025, and attributes their failures to stages of an Observe–Comprehend–Plan loop and to three protection effects: concealment, complication and misdirection. From the failure logs, the authors derive four recurring weaknesses (training bias, over-trust in observations, context limitation and plan persistence). They rerun both CLI agents without a decompiler and compare outcomes with in-competition solve rates.

  Workshop on Binary Analysis Research (BAR) 2026 · Conference paper · [PDF](https://www.ndss-symposium.org/wp-content/uploads/bar2026-58.pdf) · [Full entry & citation](https://awesomerea.org/papers/paper-llm-resistant-protection/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The study covers 24 locally solvable Linux x86-64 ELF crackmes and three commercial agents (Claude Opus 4.5 and GPT-5.1-Codex-Max in the CLI tools, and an undisclosed ChatGPT model), evaluated in December 2025 with network access; runs that consulted public write-ups were excluded. The binaries are small relative to real-world software, and malware analysis and vulnerability discovery are out of scope. Each configuration had at most three attempts with early stopping, which the authors call noisy; success means printing the correct flag or finding an accepted input. Weakness labels come from qualitative log analysis by two evaluators and describe these runs, not general properties of LLM agents. ChatGPT-5.2 Pro ran in an uncontrolled web sandbox and is excluded from the decompiler comparison. Solve rates are among teams that solved at least one challenge, unavailable for six tasks, and may include LLM-assisted teams. Training-data exposure remains a validity threat, and the paper does not publish its assembled challenge set, run logs or code.

  **Authors:** Ryutaro Nishizaka et al.

  </details>

- [**ProgramBench: Can Language Models Rebuild Programs From Scratch?**](https://arxiv.org/abs/2605.03546)

  Evaluates black-box program reconstruction across 200 tasks: agents query an executable and read its documentation, then independently implement a codebase whose behavior is checked by generated tests.

  NeurIPS 2026 · Accepted · [PDF](https://arxiv.org/pdf/2605.03546v1) · [Code](https://github.com/facebookresearch/ProgramBench) · [Full entry & citation](https://awesomerea.org/papers/paper-programbench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Binary inspection, decompilation, and internet access are forbidden during inference. Passing finite tests does not prove complete behavioral equivalence or recovery of the original source. Later live-leaderboard runs are separate from the reviewed arXiv results.

  **Authors:** John Yang et al.

  </details>

- [**Decompiling the Synergy: An Empirical Study of Human–LLM Teaming in Software Reverse Engineering**](https://www.ndss-symposium.org/ndss-paper/decompiling-the-synergy-an-empirical-study-of-human-llm-teaming-in-software-reverse-engineering/)

  Studies how human analysts work with LLM assistance during static software reverse engineering. A survey of 153 practitioners informed six LLM features built into an instrumented IDA Pro plugin. Then 48 participants (24 self-reported novices and 24 experts) analyzed two CTF-style binaries, with the features enabled on one randomly assigned challenge. From graded writeups, interaction logs and surveys, the authors report 18 findings: novice understanding rose by about 98% to expert levels while experts gained little, known-algorithm functions were triaged up to 2.4× faster, and artifact recovery rose by at least 66%, alongside harmful hallucinations.

  NDSS 2026 · Conference paper · [PDF](https://www.ndss-symposium.org/wp-content/uploads/2026-f380-paper.pdf) · [Code](https://github.com/mahaloz/dec-synergy-study) · [Full entry & citation](https://awesomerea.org/papers/paper-decompiling-synergy/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** A human study of LLM-assisted analysis, not an evaluation of autonomous agents or of LLM decompilation accuracy. It uses two unobfuscated C challenges of 26 functions each, static analysis in IDA Pro only (no debuggers or symbolic execution), researcher-written prompts, and a choice of GPT-4o, GPT-4o-Mini, GPT-4-Turbo, Claude-3-5-Sonnet or Gemini-Pro. The 2024–2025 sessions retain 48 of 51 participants; expertise is self-reported, and understanding is a rubric score of writeups graded by two researchers. LLM-created artifacts were not correlated with better understanding, and three LLM users reported a nonexistent buffer overflow that an LLM had suggested; the vulnerability-finding feature was negatively correlated with understanding. Individual observations, writeups and survey responses are not released, even on request; aggregated data is available only on request.

  **Authors:** Zion Leonahenahe Basque et al.

  </details>

- [**CREBench: Evaluating Large Language Models in Cryptographic Binary Reverse Engineering**](https://openreview.net/forum?id=tLYdf8hWJB)

  Benchmarks cryptographic binary reverse engineering across algorithm recognition, key or IV extraction, wrapper reconstruction, and flag recovery using 432 controlled challenges.

  COLM 2026 · Conference paper · [PDF](https://arxiv.org/pdf/2604.03750v2) · [Code](https://github.com/wangyu-ovo/CREBench) · [Full entry & citation](https://awesomerea.org/papers/paper-crebench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The corpus combines 48 algorithms, three insecure key-use scenarios, and three difficulty levels. It excludes professional-grade obfuscators such as Tigress and O-LLVM; results should not be generalized to heavily protected arbitrary binaries.

  **Authors:** Baicheng Chen et al.

  </details>

- [**EnIGMA: Interactive Tools Substantially Assist LM Agents in Finding Security Vulnerabilities**](https://proceedings.mlr.press/v267/abramovich25a.html)

  EnIGMA extends SWE-agent for capture-the-flag challenges with interactive agent tools that keep a gdb debugging session or a pwntools server connection open across turns, alongside decompile and disassemble commands, an LM summarizer for long outputs, and category-specific demonstrations and guidelines. It is evaluated with four LMs on 390 challenges from NYU CTF, InterCode-CTF, Cybench and a HackTheBox set the authors collected. The paper ablates tools, summarizers and demonstrations, and analyzes solution leakage and “soliloquizing”, where the model writes its own observations instead of acting in the environment.

  ICML 2025 · Conference paper · [PDF](https://raw.githubusercontent.com/mlresearch/v267/main/assets/abramovich25a/abramovich25a.pdf) · [Code](https://github.com/SWE-agent/SWE-agent/tree/v0.7) · [Full entry & citation](https://awesomerea.org/papers/paper-enigma/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The benchmarks mix cryptography, forensics, pwn, reverse engineering, web and miscellaneous tasks (104 of the 390 are reverse engineering), so aggregate solve rates such as 13.5% on NYU CTF are not reverse-engineering accuracy. The per-category table reports 17.65% on NYU CTF’s 51 reverse-engineering challenges with Claude 3.5 Sonnet. Results are pass<span>@</span>1 with a <span>$</span>3 per-instance cost cap and 2024 models (GPT-4 Turbo, GPT-4o, Claude 3.5 Sonnet and LLaMA 3.1 405B Instruct); the NYU CTF baseline comparison uses pass<span>@</span>5. Many challenges have public write-ups, and the authors’ leakage and soliloquy measures are heuristics; on 21 later CSAW 2024 challenges the best configurations solved 2. Solving a CTF shows a captured flag, not recovered program structure or source.

  **Authors:** Talor Abramovich et al.

  </details>

<a id="papers-decompilation"></a>
### Decompilation and symbol recovery

[↑ Paper topics](#papers) · [Contents](#contents)

- [**Decoupling is a Necessity: Transformation-Agnostic Decompiled Code Recovery under Optimization and Obfuscation**](https://arxiv.org/abs/2608.27889)

  ReSource refines decompiled functions affected by compiler optimization and obfuscation. Its stages retrieve guidance from a Semantic Distortion Database, predict a control-flow skeleton, and refine names and formatting. Evaluation measures code similarity and retrieval of the corresponding original function from a source corpus.

  arXiv 2026 · Preprint · [PDF](https://arxiv.org/pdf/2608.27889v1) · [Full entry & citation](https://awesomerea.org/papers/paper-resource/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Function-level similarity and retrieval are proxies; they do not establish compilability, executable equivalence or complete program recovery. Section 5.2 notes missing global context and untested custom obfuscation. The author-linked artifact page describes a simplified dataset and explicitly says the database-construction and control-flow-prediction modules are not yet available.

  **Authors:** Zhiping Zhou et al.

  </details>

- [**SoK: AI-Augmented Binary Reversing**](https://arxiv.org/abs/2606.17398)

  A systematization-of-knowledge survey of machine-learning, LLM and agentic approaches to binary reversing. Version 2 collects 246 papers published since 2015, found through keyword searches of 11 security, software-engineering and AI venues plus citation snowballing, and organizes them into 22 domains by inference task: from code-boundary detection and recovery of function names, types and struct layouts to code similarity, malware and vulnerability analysis, and decompilation. Its taxonomy links conventional triage, static, dynamic and security-testing analyses to AI pipelines through the binary-derived artifacts they exchange, and it derives 12 insights and open directions such as binary-aligned ground truth and goal-driven agentic reversing.

  arXiv 2026 · Preprint · [PDF](https://arxiv.org/pdf/2606.17398v2) · [Full entry & citation](https://awesomerea.org/papers/paper-sok-ai-binary-reversing/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** A literature systematization with no new experiments, benchmark or tool; it classifies and summarizes reported results without reproducing them. The corpus covers papers available up to July 31, 2026, applies citation thresholds that fall from 12 for 2015–2016 papers to 2 for 2025–2026 papers, excludes methods that need source code at inference time, and leaves out Android and interpreted-language bytecode. Detailed per-stage tables draw on 88 top-venue studies rather than the full corpus. It is an arXiv preprint with no stated venue, and this record makes no claim of peer review. Papers it cites are not thereby part of this collection; each needs its own review.

  **Authors:** Yujeong Kwon et al.

  </details>

- [**LLM Agent-Assisted Reverse Engineering with Quantitative Readability Metrics**](https://arxiv.org/abs/2606.06838)

  Uses a composite Quantitative Readability Score (QRS) to guide agents refining decompiled C. Lexical familiarity, structural simplicity and coding idioms are combined with a binary-structure similarity gate. Experiments compare refinement with and without shell access on 210 simple C binaries.

  arXiv 2026 · Preprint · [PDF](https://arxiv.org/pdf/2606.06838v1) · [Full entry & citation](https://awesomerea.org/papers/paper-qrs-readability/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Structural similarity does not prove semantic equivalence. QRS both guides and evaluates refinement; human readability validation remains future work. The selected synthetic corpus limits generalization. Recovering compilable, behaviorally correct code from difficult binaries is outside the claimed contribution.

  **Authors:** Neil Archibald et al.

  </details>

- [**SK2Decompile: LLM-based Two-Phase Binary Decompilation from Skeleton to Skin**](https://proceedings.iclr.cc/paper_files/paper/2026/hash/9132583dd869acb0cafeb0ed25eb031a-Abstract-Conference.html)

  Splits LLM decompilation into two phases: a Structure Recovery model turns decompiler pseudocode into an identifier-free IR that keeps control flow and data structures, trained with compiler-based RL rewards, and an Identifier Naming model then restores names under a semantic-similarity reward. The authors report a 21.6% average re-executability gain over GPT-5-mini on HumanEval and a 29.4% average R2I improvement over Idioms on GitHub2025.

  ICLR 2026 · Conference paper · [PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/9132583dd869acb0cafeb0ed25eb031a-Paper-Conference.pdf) · [Code](https://github.com/albertan017/LLM4Decompile/tree/85b364bf093eb2ee4f3687cfe38a203fca89f23e/sk2decompile) · [Full entry & citation](https://awesomerea.org/papers/paper-sk2decompile/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Training and main evaluation use function-level C compiled for x86-64 Linux with GCC and Clang at -O0 to -O3, with IDA Pro pseudocode as model input. Re-executability is measured only on HumanEval and MBPP; ExeBench and GitHub2025 use R2I readability and a GPT-5-mini judge. Appendix experiments extend to BringUpBench projects, macOS arm64 and Windows MSVC builds, and Obfuscator-LLVM, but the models are trained on C only and the paper expects them to degrade on features without C equivalents, such as C++ templates.

  **Authors:** Hanzhuo Tan et al.

  </details>

- [**Idioms: A Simple and Effective Framework for Turbo-Charging Local Neural Decompilation with Well-Defined Types**](https://www.ndss-symposium.org/ndss-paper/idioms-a-simple-and-effective-framework-for-turbo-charging-local-neural-decompilation-with-well-defined-types/)

  Idioms fine-tunes code language models to turn Hex-Rays output for one target function into predicted original C together with definitions of the user-defined structs, unions and typedefs it uses. Input can include neighboring decompiled functions in breadth-first call-graph order, so evidence about a type scattered across callers and callees reaches the model. The authors also build Realtype, 157,163 functions from compiled open-source C repositories with full type definitions. Their CodeGemma-7b-based model passes ExeBench unit tests for 54.4% of functions versus 46.3% for LLM4Decompile and 37.5% for Nova, and scores at least 95% higher on Realtype.

  NDSS 2026 · Conference paper · [PDF](https://www.ndss-symposium.org/wp-content/uploads/2026-f795-paper.pdf) · [Code](https://github.com/squaresLab/idioms) · [Full entry & citation](https://awesomerea.org/papers/paper-idioms/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** This is local, function-level neural decompilation: each prediction covers one target function and its type definitions, not a compilable whole program. Evaluation uses x86-64 Linux gcc binaries from open-source GitHub projects and ExeBench’s “real” subset; O1–O3 builds disable inlining, and keeping only functions that decompiled at every level removes 21% of the Hex-Rays and 76% of the Ghidra test sets. ExeBench unit tests are an optimistic proxy; Realtype has no tests, so dependency-graph equivalence and exact name and type matches serve as conservative proxies, and a Realtype user-defined type counts as correct only if all of its fields, 17.6 on average when counted recursively, match. The main models use proprietary Hex-Rays output and context windows of 2,048 or 4,096 tokens. Predicted names and types are statistical, not recovered originals. Pretraining leakage from GitHub remains possible, and obfuscated code and malware were not evaluated.

  **Authors:** Luke Dramko et al.

  </details>

- [**FidelityGPT: Correcting Decompilation Distortions with Retrieval Augmented Generation**](https://www.ndss-symposium.org/ndss-paper/fidelitygpt-correcting-decompilation-distortions-with-retrieval-augmented-generation/)

  FidelityGPT post-processes existing decompiler output: an LLM labels lines with six distortion types, such as non-conventional dereferencing, redundant variables and confusing control flow, and then rewrites the labeled lines. Its prompts define the distortion types and add retrieval-augmented context from a manually annotated database of distorted IDA Pro and Ghidra lines. A semantic-intensity algorithm chooses which lines to query, and a variable-dependency analysis carries redundant-variable context across 50-line chunks. On 620 function pairs, the authors report 89% detection accuracy and 83% precision, and correction fix rates of 94% (FR) and 64% (CFR) against 83% and 37% for their DeGPT runs.

  NDSS 2026 · Conference paper · [PDF](https://www.ndss-symposium.org/wp-content/uploads/2026-s989-paper.pdf) · [Code](https://github.com/ZhouZhiping045/FidelityGPT) · [Full entry & citation](https://awesomerea.org/papers/paper-fidelitygpt/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The 620 pairs are mostly -O0 IDA Pro 7.5 functions sampled from Coreutils, curl, ImageMagick, OpenSSL, PuTTY and SQLite builds in a binary-similarity dataset, across ARM-32, MIPS-32 and x86-32, plus x86-64 TheAlgorithms/C code; separate -O1–-O3 and Ghidra sets test generalization. Ground-truth labels and FR/CFR were assessed manually by the author team against the paper’s criteria. Fix rates count lines marked as fixed and are not semantic-equivalence proofs: the authors note that repaired code often cannot be recompiled or executed. Correction runs on whole functions and may degrade on long ones, and the distortion database, built from 150 IDA Pro and 91 Ghidra lines, may miss rarer anomalies. Main results use GPT-4o at temperature 0.5 and remain stochastic; DeepSeek-chat and temperature-0 runs are reported separately. Training-data exposure of the open-source projects cannot be ruled out.

  **Authors:** Zhiping Zhou et al.

  </details>

- [**BinMetric: A Comprehensive Binary Code Analysis Benchmark for Large Language Models**](https://www.ijcai.org/proceedings/2025/858)

  BinMetric poses 1,000 questions across six binary-analysis tasks: call-site reconstruction, decompilation, signature recovery, binary code summarization, algorithm classification and assembly instruction generation. The questions come from 20 open-source C projects compiled for x86-64, stripped and processed with IDA Pro, and aligned with source code through DWARF information. The authors evaluate 12 LLMs from five model families with one-shot prompts, alongside IDA Pro’s decompiler, LLM4Decompile, BinT5 and HexT5 where those apply.

  IJCAI 2025 · Conference paper · [PDF](https://www.ijcai.org/proceedings/2025/0858.pdf) · [Full entry & citation](https://awesomerea.org/papers/paper-binmetric/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Scores are question-level metrics on isolated snippets, not end-to-end reverse-engineering workflows or agentic tool use. Preprocessing requires IDA Pro, and all binaries are x86-64 builds with each project’s default compiler settings on Ubuntu 22.04; other architectures, optimization sweeps and obfuscation are not studied. Most tasks score text overlap with Rouge-L, BLEU, METEOR or CodeBLEU, so they do not test semantic equivalence; only assembly generation checks compilation and test-case execution, where the average execution pass rate is below 1%. Summary labels were generated by ChatGPT and then manually reviewed, and algorithm classification uses 80 snippets from a single algorithms project. Leakage screening relied on exact-match web searches. The evaluated models predate 2025 (including gpt-3.5-turbo-16k-0613 and gpt-4-0613) and ran with a maximum length of 8,192 tokens, so the rankings are historical.

  **Authors:** Xiuwei Shang et al.

  </details>

- [**DecompileBench: A Comprehensive Benchmark for Evaluating Decompilers in Real-World Scenarios**](https://aclanthology.org/2025.findings-acl.1194/)

  Evaluates traditional and LLM-based decompilers using functions from real programs, runtime behavioral checks, and an LLM-assisted assessment of analyst-facing code understandability.

  Findings of ACL 2025 · Conference paper · [PDF](https://aclanthology.org/2025.findings-acl.1194.pdf) · [Code](https://github.com/vul337/DecompileBench) · [Full entry & citation](https://awesomerea.org/papers/paper-decompilebench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The evaluated corpus has 23,400 functions from 130 programs. Fuzzing-based checks have finite coverage, and understandability scores depend partly on an LLM judge. The artifact warns that rebuilt OSS-Fuzz projects can differ from the paper's versions.

  **Authors:** Zeyu Gao et al.

  </details>

- [**DecLLM: LLM-Augmented Recompilable Decompilation for Enabling Programmatic Use of Decompiled Code**](https://dl.acm.org/doi/10.1145/3728958)

  DecLLM repairs decompiler pseudocode that does not recompile into C that compiles and runs, so source-level tools such as CodeQL can be applied to binaries. An iterative loop feeds compiler errors to an off-the-shelf LLM, reverting illegal outputs and large deletions, then uses mismatched test outputs and AddressSanitizer reports from the rebuilt program to repair behavior, and finally fuzzes the original and rebuilt executables for divergences. With GPT-3.5 and GPT-4 the authors report 74% and 78.3% success on 300 Code Contest programs; on Coreutils and CGC binaries, 61.9–70.9% recompile and 48.1–59.0% are fully functional.

  Proceedings of the ACM on Software Engineering (ISSTA 2025) · Journal article · [PDF](https://dl.acm.org/doi/pdf/10.1145/3728958) · [Full entry & citation](https://awesomerea.org/papers/paper-decllm/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** On Code Contest, success means the repaired code compiles and the rebuilt executable passes the supplied test cases, with AFL++ fuzzing as an extra check; the Coreutils and CGC overall rates also count rebuilt binaries that malfunction or crash. This establishes compilability and test-based agreement, not semantic equivalence, which the authors note is undecidable. Results depend on IDA Pro 8.3 output, with one Ghidra 10.4 repetition, and on the API-served gpt-3.5-turbo-0613 and gpt-4-0314 snapshots with a 4,096-token limit, so programs were chosen to fit within half of it. The 300 Code Contest programs average 112.9 lines; Coreutils 9.5 and CGC binaries were compiled without stripping symbols and repaired function by function, which cannot infer undefined globals. Around 30% of hard cases still fail, mainly from decompiler address/data confusion, ill-inferred buffer sizes, long outputs that include STL code and LLM type-cast shortcuts; deviations not exercised by tests remain undetected. CodeQL analysis of Juliet samples needed manual query adaptation.

  **Authors:** Wai Kin Wong et al.

  </details>

- [**DiSCo: Towards Decompiling EVM Bytecode to Source Code using Large Language Models**](https://dl.acm.org/doi/10.1145/3729373)

  DiSCo lifts Ethereum contract creation bytecode to Solidity source by prompting a frozen LLM, instead of emitting decompiler pseudocode. It abstracts control-flow paths into logic-invariant semantic units, recovers constructor logic by simulating creation bytecode captured from block execution, and infers stripped names with signature databases and a type-aware graph model. These units become natural-language descriptions plus coding specifications in the prompt. GPT-4 is the primary model; Llama 3 is also tested.

  Proceedings of the ACM on Software Engineering (FSE 2025) · Journal article · [PDF](https://dl.acm.org/doi/pdf/10.1145/3729373) · [Full entry & citation](https://awesomerea.org/papers/paper-disco/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Ground truth comes from Etherscan source files: 200 highest-balance contracts for all baselines and 1,000 for automated tests; separate studies add 50 Vyper, 50 newly deployed and 149 closed-source attack contracts. Compilability (about 75% with best-of-five sampling, 46% for a single run), differential-fuzzing pass rates and embedding similarity do not establish equivalence to deployed source. Nearly half of the imitation-learning fuzzer’s transactions revert, and manual review judged about 28.5% of generated contracts semantically consistent, and 12% for Vyper inputs. The authors report timeouts or unsound analysis on contracts with many paths, and name inference remains weak. Baselines give the same LLM output from Panoramix, Ethervm and Elipmoc, mostly taken from their websites or decompiled manually; this is not a comparison of standalone decompilers. Results depend on a GPT-4 preview snapshot. Attack reproduction covers ten January 2025 incidents, four of which were reproduced.

  **Authors:** Xing Su et al.

  </details>

- [**Unleashing the Power of Generative Model in Recovering Variable Names from Stripped Binary**](https://www.ndss-symposium.org/ndss-paper/unleashing-the-power-of-generative-model-in-recovering-variable-names-from-stripped-binary/)

  GenNm suggests names for placeholder variables in decompiled code of stripped binaries by fine-tuning generative code models (CodeGemma-2B by default; CodeLlama-7B and a LoRA-tuned CodeLlama-34B are also tested). Queries add renamed caller code and callee signatures propagated along the call graph; a DPO-style symbol-preference optimization (SymPO) counters bias toward frequent training names, and a data-flow name-validation step chooses among candidates over iterative rounds. The authors report 5.6–11.4-point precision gains over VarBERT and ReSym on rebuilt DIRTY and VarCorpus datasets, and 22.8% precision on names unseen in training against 17.3% for the strongest baseline.

  NDSS 2025 · Conference paper · [PDF](https://www.ndss-symposium.org/wp-content/uploads/2025-276-paper.pdf) · [Code](https://github.com/XZ-X/gennm-ndss-ae/tree/9955139b4c8d43144852a674bf317cbfaf32ed17) · [Full entry & citation](https://awesomerea.org/papers/paper-gennm/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Predictions are scored against debug-symbol names by token matching with SymLM's word clusters and rules, plus a GPT-4 evaluator for context relevance and semantic accuracy; neither shows that outputs are the original identifiers, and overall split-by-binary precision is 35.8% (DIRTY) and 41.2% (VarCorpus). Precision is about 30% for projects unseen in training, and gains are smaller at -O2 and -O3. Ground truth comes from debug information in Linux binaries rebuilt from GitHub projects or Gentoo packages, with IDA Pro output in the paper's examples. GenNm needs each binary's call graph, which is why the DIRTY dataset was rebuilt; split-by-function VarCorpus results use a 15% binary sample, and the black-box GPT-3.5/GPT-4 comparison uses 1,000 sampled functions. It recovers variable names only, not types, function names or full decompiled code.

  **Authors:** Xiangzhe Xu et al.

  </details>

- [**TypeForge: Synthesizing and Selecting Best-Fit Composite Data Types for Stripped Binaries**](https://ieeexplore.ieee.org/document/11023499)

  TypeForge recovers composite data types, including struct layouts, unions and pointer or nesting relationships, from stripped binaries. A whole-program Type Flow Graph over Ghidra’s decompiler-inferred variables propagates member offsets and sizes, cuts conflicting edges caused by casts and unions, and synthesizes candidate type declarations. An LLM only selects among these statically synthesized candidates: each is applied through the decompiler’s retype interface, and a double-elimination tournament compares the resulting pseudocode for readability. On OSPREY’s coreutils dataset the authors report F1 of 81.7% for composite-type identification, 88.2% for layout recovery and 72.1% for relationship recovery.

  IEEE S&amp;P 2025 · Conference paper · [PDF](https://noobone123.github.io/papers/typeforge-sp25.pdf) · [Code](https://github.com/noobone123/TypeForge) · [Full entry & citation](https://awesomerea.org/papers/paper-typeforge/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Recovers member offsets, sizes and relationships, not original type or member names; relationship correctness is judged by matching layouts because names are unavailable. The main evaluation uses OSPREY’s dataset of GNU coreutils and larger Howard-dataset programs, over 10,000 functions and 11,000 composite-typed variables at O0–O3, with ground truth from debug information; the paper does not report results per architecture. In the baseline comparison, OSPREY results were supplied by its authors and its runtime is an estimate, and ReSym figures are its published results, so not every baseline was rerun. Conservative removal of conflicting edges can drop valid members, and compiler optimizations that merge or flatten members lower accuracy at higher levels. About 75% of runtime is the LLM selection stage; the default model was GPT-4o mini, with each comparison run three times. Downstream readability and vulnerability examples are case studies, not proof of semantic equivalence.

  **Authors:** Yanzhong Wang et al.

  </details>

- [**Nova: Generative Language Models for Assembly Code with Hierarchical Attention and Contrastive Learning**](https://proceedings.iclr.cc/paper_files/paper/2025/hash/ef283d62b4bce30854a8d4827f331229-Abstract-Conference.html)

  Nova is a generative LLM for x86-64 assembly, trained from DeepSeek-Coder checkpoints on stripped, normalized gcc -O0 to -O3 assembly built from AnghaBench and The Stack. It adds hierarchical attention that builds per-instruction summaries, and contrastive objectives that keep a function's source and O0–O3 assembly close while ordering them by optimization level. Fine-tuned for decompilation, Nova-1.3B and Nova-6.7B reach 25.17% and 34.36% average Pass<span>@</span>1 on HumanEval-Decompile, 14.84 and 12.41 points above same-size LLM4Decompile; separately fine-tuned models report the highest average Recall<span>@</span>1 for O0-to-O3 binary code similarity on six real-world projects.

  ICLR 2025 · Conference paper · [PDF](https://proceedings.iclr.cc/paper_files/paper/2025/file/ef283d62b4bce30854a8d4827f331229-Paper-Conference.pdf) · [Code](https://github.com/lt-asset/nova/tree/6dfaf438fb23a8f024d0297653571615631ad8f4) · [Full entry & citation](https://awesomerea.org/papers/paper-nova/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Decompilation is evaluated function by function on the 164 HumanEval-Decompile C problems, each compiled for x86-64 at O0–O3, by running 20 samples per function against the problems' test cases; Pass<span>@</span>k on these tests is neither whole-program nor equivalence evidence. Baselines other than LLM4Decompile and Nova were prompted with three-shot examples rather than fine-tuned. Similarity results cover O0 queries against O3 candidates in pools of 50–500 functions from Binutils, Curl, ImageMagick, SQLite, OpenSSL and PuTTY, after fine-tuning on BinaryCorp-3M. Decompilation fine-tuning used a 2.16M-pair sample, the README says only 50K files came from The Stack, and the paper limits Nova to x86-64 assembly and 1.3B and 6.7B models. Inputs require the paper's assembly normalization.

  **Authors:** Nan Jiang et al.

  </details>

- [**Decompile-Bench: Million-Scale Binary-Source Function Pairs for Real-World Binary Decompilation**](https://papers.nips.cc/paper_files/paper/2025/hash/079cf13ae174c31f148207d94d213bdc-Abstract-Datasets_and_Benchmarks_Track.html)

  Introduces two million C/C++ binary-source function pairs using a Compile-Trace-Filter pipeline, with an evaluation suite spanning translated HumanEval/MBPP tasks and recent GitHub functions.

  NeurIPS 2025 Datasets and Benchmarks · Conference paper · [PDF](https://papers.nips.cc/paper_files/paper/2025/file/079cf13ae174c31f148207d94d213bdc-Paper-Datasets_and_Benchmarks_Track.pdf) · [Code](https://github.com/albertan017/LLM4Decompile) · [Full entry & citation](https://awesomerea.org/papers/paper-decompile-bench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** This is function-level decompilation. Re-execution tests cover HumanEval/MBPP; GitHub2025 provides no unit tests. Inlining can prevent one-to-one source correspondence, and the fine-tuning study uses 10% of the corpus. These results do not establish whole-program recovery.

  **Authors:** Hanzhuo Tan et al.

  </details>

- [**Beyond Classification: Inferring Function Names in Stripped Binaries via Domain Adapted LLMs**](https://www.ndss-symposium.org/ndss-paper/beyond-classification-inferring-function-names-in-stripped-binaries-via-domain-adapted-llms/)

  SymGen infers function names for stripped binaries by generating them with a LoRA-fine-tuned Code Llama model instead of classifying over a fixed name vocabulary. Ghidra decompiles each stripped function, its own name is masked, and callee names are normalized for deduplication. Before fine-tuning, the model is domain-adapted on decompiled code paired with LLM-generated summaries of the matching source functions. On functions from 33 C projects built for x86-64, x86-32, ARM and MIPS at O0–O3, deduplicated from 2,237,915 to 495,494, the authors report average word-level F1 of 0.277 (0.380 on x86-64), plus case studies on obfuscated binaries and Linux malware.

  NDSS 2025 · Conference paper · [PDF](https://www.ndss-symposium.org/wp-content/uploads/2025-797-paper.pdf) · [Code](https://github.com/OSUSecLab/SymGen) · [Full entry & citation](https://awesomerea.org/papers/paper-symgen/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Names are split into words and scored with precision, recall and F1, with SymLM’s CodeWordNet grouping similar words; predictions are descriptive guesses, not recovered original symbols. Average F1 is 0.277 and lower on MIPS (0.137) and ARM (0.262). The gains of up to 409.3%, 553.5% and 489.4% in the abstract are author-reported relative improvements over AsmDepictor; the baselines were retrained on the authors’ deduplicated dataset, where they score far below their own papers, and XFL was compared on x86-64 only. A separate model is trained for each architecture and optimization level. All binaries were built with GCC 9.4.0, inputs depend on Ghidra output, and Code Llama’s closed pretraining data leaves leakage possible. Obfuscation tests apply three default Hikari passes to 363 binaries from six projects (F1 0.271–0.303); the malware study covers 812 functions in 16 x86-64 builds (F1 0.348).

  **Authors:** Linxi Jiang et al.

  </details>

- [**ReSym: Harnessing LLMs to Recover Variable and Data Structure Symbols from Stripped Binaries**](https://doi.org/10.1145/3658644.3670340)

  Combines two fine-tuned language models with Prolog-based cross-function reasoning to infer local-variable symbols and user-defined data structures from stripped-binary decompilation.

  ACM CCS 2024 · Conference paper · [PDF](https://www.cs.purdue.edu/homes/lintan/publications/resym-ccs24.pdf) · [Code](https://github.com/lt-asset/resym) · [Full entry & citation](https://awesomerea.org/papers/paper-resym/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The method depends on underlying decompilation and learned predictions over C/C++ data. Cross-checking reduces conflicting predictions but does not prove that recovered names or layouts match the unavailable source. The public artifact includes models, processed data, and evaluation code.

  **Authors:** Danning Xie et al.

  </details>

- [**Self-Constructed Context Decompilation with Fined-grained Alignment Enhancement**](https://aclanthology.org/2024.findings-emnlp.385/)

  Adds two techniques to LLM decompilation of function-level x86-64 GCC assembly into C. Self-Constructed Context Decompilation (sc²dec) recompiles a model’s first compilable output and uses the resulting assembly–source pair as an in-context example for a second attempt, without fine-tuning. Fine-grained Alignment Enhancement (FAE) fine-tunes llm4decompile-6.7b with LoRA on statement-level assembly–C alignments derived from DWARF debug information. Combining both, the authors report 52.41% average re-executability on Decompile-Eval, against 48.60% for the base model.

  Findings of EMNLP 2024 · Conference paper · [PDF](https://aclanthology.org/2024.findings-emnlp.385.pdf) · [Code](https://github.com/AlongWY/sccdec) · [Full entry & citation](https://awesomerea.org/papers/paper-sc2dec/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Results are function-level re-executability on Decompile-Eval: 164 HumanEval-derived C problems compiled at O0–O3 and checked by recompilation and HumanEval test cases. Passing these tests is not whole-program or all-input equivalence, and the paper does not evaluate real-world binaries, other architectures or readability. sc²dec helps only when the first output recompiles, so low re-compilability limits its gains; the authors report 1–2% lower results when context is built at a mismatched optimization level, and clang-built contexts scored slightly below GCC. FAE used 10,000 ExeBench functions limited to the standard C library, one training epoch and a single 6.7B base model; the authors did not validate it on larger datasets or models, and it slightly lowered the 1-shot result. GPT-4 and DeepSeek baselines are API snapshots that may not be reproducible.

  **Authors:** Yunlong Feng et al.

  </details>

- [**LLM4Decompile: Decompiling Binary Code with Large Language Models**](https://aclanthology.org/2024.emnlp-main.203/)

  Trains language models for assembly-to-C decompilation and for refining Ghidra pseudocode, evaluating whether recovered functions can be recompiled and executed correctly.

  EMNLP 2024 · Conference paper · [PDF](https://aclanthology.org/2024.emnlp-main.203.pdf) · [Code](https://github.com/albertan017/LLM4Decompile) · [Full entry & citation](https://awesomerea.org/papers/paper-llm4decompile/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The paper limits its experiments to C on x86 and function-level benchmarks. Re-executability on sampled tests does not establish whole-program equivalence or recovery of the original source. Later repository releases are separate from the 2024 paper.

  **Authors:** Hanzhuo Tan et al.

  </details>

- [**WaDec: Decompiling WebAssembly Using Large Language Model**](https://dl.acm.org/doi/10.1145/3691620.3695020)

  WaDec decompiles WebAssembly text (wat) into C by fine-tuning CodeLlama-7b with LoRA on loop-level wat–C snippet pairs. Functions are ordered by dependency and sliced so that each input holds at most one loop, with nested loops replaced by markers. Prompts add declarations of called functions, previously defined local variables and offset-to-string mappings; the outputs are then reassembled, with string constants restored and variables renamed. Training data come from 51,768 the-stack-dedup and 377 TheAlgorithms/C programs compiled with Emscripten. On 3,977 C files, the authors report 3.34% code inflation, 52.11% recompilability, 43.55% re-execution and 27.15% output consistency, compared with Wasm2c and Ghidra.

  ASE 2024 · Conference paper · [PDF](https://arxiv.org/pdf/2406.11346v3) · [Code](https://github.com/XinyuShe/WaDec/tree/e244f7172539478a5b64bbb86e1fd03e527cb6be) · [Full entry & citation](https://awesomerea.org/papers/paper-wadec/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The reported rates are author results on C programs compiled to Wasm with Emscripten. About half of the outputs recompile, fewer than half re-execute and roughly a quarter reproduce the original output, so decompiled code is generally not semantically equivalent. The 3,977-file benchmark comes from the same two sources as the training programs. Optimized builds are not evaluated: the authors neither adapted the method to nor trained it on O1/O2 code. The model also handles data structures poorly, often flattening them into separate variables or arrays. Only C sources are studied; Wasm produced from other languages or toolchains is not evaluated. Baselines are Wasm2c and Ghidra's Wasm plugin, and LLM baselines were excluded because none could decompile Wasm functions without fine-tuning. Slicing means one function may be decompiled several times, at about 0.1 to 2 seconds per prompt.

  **Authors:** Xinyu She et al.

  </details>

- [**StackSight: Unveiling WebAssembly through Large Language Models and Neurosymbolic Chain-of-Thought Decompilation**](https://proceedings.mlr.press/v235/fang24e.html)

  StackSight decompiles WebAssembly text-format functions into C++ with LLM prompting. A static analysis annotates each WAT instruction with the virtual-stack state, using symbolic notation where branches diverge; a one-shot chain-of-thought prompt then asks the model to recover variable meanings, summarize the function and write C++. With GPT-4 the share of outputs passing all benchmark tests rises from 19.7% to 36.5% on HumanEval-X and from 42.4% to 59.6% on MBXP relative to one-shot prompting; GPT-3.5 and Code Llama-7B-Instruct are also evaluated.

  ICML 2024 · Conference paper · [PDF](https://raw.githubusercontent.com/mlresearch/v235/main/assets/fang24e/fang24e.pdf) · [Full entry & citation](https://awesomerea.org/papers/paper-stacksight/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Inputs are short exercise functions from the C++ splits of HumanEval-X (161 of 164 compiled) and MBXP (773 of 974), built as Emscripten 3.1.46 side modules at -Oz with function names kept by --profiling-funcs and converted with wasm2wat 1.0.33; minified, obfuscated or whole-application WebAssembly is not evaluated. Correctness is the share of outputs that compile and pass the benchmarks' test cases after a test oracle renames functions, inserts tests and adds namespace directives, with manual pass-by-value edits. Passing these tests is not proof of equivalence with the original module. Summaries are scored by BERTScore and SBERT; the user study had 15 participants on 20 snippets per dataset. wasm2c and an earlier neural decompiler were excluded for producing no compilable output, and results depend on specific hosted model versions.

  **Authors:** Weike Fang et al.

  </details>

- [**BinaryAI: Binary Software Composition Analysis via Intelligent Binary Source Code Matching**](https://dl.acm.org/doi/10.1145/3597503.3639100)

  BinaryAI identifies which open-source C/C++ libraries a stripped binary reuses by matching its functions to source code. Ghidra decompiles each binary function to pseudo-C, and a Pythia-410M model, trained with a CLIP-style contrastive loss on about 10 million binary–source function pairs, embeds pseudo-code and source functions in one space. Candidates retrieved from a corpus of 56,342,179 source functions from 12,013 libraries are refined with link-time locality and the call graph, and a library is reported when the share of its matched functions exceeds a threshold. The authors report 22.54% recall<span>@</span>1 against 10.75% for CodeCMR, and library-detection precision and recall of 85.84% and 64.98% against 73.36% and 59.81% for an unnamed commercial tool.

  ICSE 2024 · Conference paper · [PDF](https://arxiv.org/pdf/2401.11161v3) · [Full entry & citation](https://awesomerea.org/papers/paper-binaryai/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Training pairs come from ArchLinux and AUR packages compiled automatically with DWARF debug information, and the corpus and test set cover C/C++ projects only. The SCA test set is 150 stripped binaries the authors compiled from 85 GitHub projects, with 1,045 reused libraries labeled manually from build files, headers and license metadata; function-level ground truth covers 15 of those binaries (23,529 pairs). The recall<span>@</span>1 figures combine the model's validation set with those 15 binaries. The two commercial baselines are anonymized under confidentiality agreements, and every baseline was rebuilt on the authors' 12,013-library dataset. The 112 false positives the authors examined all trace to incomplete library-dependency data. The model, training pairs, source-function corpus and labeled test set are not public, and the hosted service the paper links may run a different model and corpus from the evaluated 2024 system. Matches identify reused source; they are not a decompilation or proof that the binary is unmodified.

  **Authors:** Ling Jiang et al.

  </details>

- [**SLaDe: A Portable Small Language Model Decompiler for Optimized Assembly**](https://ieeexplore.ieee.org/document/10444788)

  SLaDe translates function-level assembly into C with a 200M-parameter encoder–decoder model, code-specific tokenization and PsycheC type completion. It studies x86 and ARM at -O0 and -O3, combining generated candidates with input/output checks. The input is assembly text, not raw machine bytes; disassembly is outside the method.

  IEEE/ACM CGO 2024 · Conference paper · [PDF](https://arxiv.org/pdf/2305.12520v3) · [Code](https://zenodo.org/records/10205121) · [Full entry & citation](https://awesomerea.org/papers/paper-slade/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Evaluation covers about 4,000 ExeBench functions and a 112-program synthesis suite. Beam size 5 selects the first candidate passing finite I/O tests; generated functions are inserted into the original calling context. Passing these tests is not whole-program or all-input equivalence. Edit similarity is a readability proxy. Longer functions, external calls and incorrect type/operator predictions remain failure modes; the model has 1,024-position source and target windows. Historical baseline comparisons have different coverage and do not establish current rankings.

  **Authors:** Jordi Armengol-Estapé et al.

  </details>

- [**“Len or index or count, anything but v1”: Predicting Variable Names in Decompilation Output with Transfer Learning**](https://ieeexplore.ieee.org/document/10646727)

  VarBERT suggests variable names for IDA Hex-Rays and Ghidra decompiler output with a BERT-style model pre-trained on 5.2M human-written C functions from Debian and fine-tuned on decompiled code; it also predicts whether each variable came from the developer or was introduced by the decompiler. The authors build VarCorpus from Gentoo C and C++ packages compiled for x86-64 at O0–O3, labeling decompiled variables from debug symbols. On per-function splits of O2 binaries, top-1 accuracy is 54.43% for IDA and 54.49% for Ghidra; on an IDA-O0 subset it reaches 50.70%, against 35.94% for DIRE and 38.00% for DIRTY.

  IEEE S&amp;P 2024 · Conference paper · [PDF](https://www.atipriya.com/files/papers/varbert_oakland24.pdf) · [Code](https://github.com/sefcom/VarBERT/tree/76f221a5e0af43a36169818cbbfd6e8dd3c98cdc) · [Full entry & citation](https://awesomerea.org/papers/paper-varbert/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Predicted names are learned suggestions scored against developer names, not recovered originals. Top-1 accuracy drops to 42.40% (IDA) and 40.49% (Ghidra) on per-binary O2 splits, and the per-binary IDA-O0 lead over DIRTY is 4.52 points. The DIRE and DIRTY comparison covers IDA at O0 only, on about 400K functions (roughly 15% of VarCorpus), because DIRE's training time was prohibitive. The method can name only variables the decompiler recovers, and labeling relies on IDA and Ghidra preserving variables when matching debug symbols. Corpora come from Linux distribution packages, mainly x86-64 with a smaller AArch64 O2 experiment, and may not represent Windows or macOS executables; deduplication removes exact duplicates only. The user study had 27 students who completed 13 function pairs. Types, structures and recompilable code are outside its scope.

  **Authors:** Kuntal Kumar Pal et al.

  </details>

- [**DeGPT: Optimizing Decompiler Output with LLM**](https://www.ndss-symposium.org/ndss-paper/degpt-optimizing-decompiler-output-with-llm/)

  Refines existing C-like decompiler output through three coordinated roles that select, propose and check changes. It simplifies structures, adds comments and renames variables; Micro Snippet Semantic Calculation compares simulated symbol values and calls before accepting structural changes. The authors evaluate readability and naming on 620 functions from four codebases, with separate stripped and non-stripped variants.

  NDSS 2024 · Conference paper · [PDF](https://www.ndss-symposium.org/wp-content/uploads/2024-401-paper.pdf) · [Code](https://github.com/PeiweiHu/DeGPT) · [Full entry & citation](https://awesomerea.org/papers/paper-degpt/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The reported 24.4% reduction is a Halstead-effort proxy on non-stripped output, not a measured reduction in human effort. The 62.9% comment result is the average non-trivial share among manually judged correct comments. MSSC is an intraprocedural heuristic: calls are abstracted and loops become branches; parsing, aliasing and path growth remain limitations. Its 80-case manual audit reports 84% accuracy and 85% recall, including three harmful changes missed. This supports assisted pseudocode comprehension, not guaranteed binary equivalence, recompilable whole programs or original-source recovery.

  **Authors:** Peiwei Hu et al.

  </details>

- [**XFL: Naming Functions in Binaries with Extreme Multi-label Learning**](https://ieeexplore.ieee.org/document/10179439)

  XFL treats function naming in stripped binaries as extreme multi-label classification: names are split into tokens, and PfastreXML ranks which tokens from a vocabulary of frequent labels fit each function. Its DEXTER embedding combines static-analysis features built on angr’s VEX IR with call-graph and whole-binary context, and a separate language model orders predicted tokens into a name string. On 741,724 functions from 10,047 x86-64 C binaries in Debian packages, with a 1,024-label vocabulary, the authors report precision 0.835, recall 0.575 and F1 0.681, ahead of Punstrip, Debin and Nero in precision and F1.

  IEEE S&amp;P 2023 · Conference paper · [PDF](https://arxiv.org/pdf/2107.13404v4) · [Code](https://github.com/lmu-plai/xfl) · [Full entry & citation](https://awesomerea.org/papers/paper-xfl/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Predictions are token labels from a fixed vocabulary, ranked and optionally assembled into names; they are not recovered source names, and scoring matches tokens rather than exact names. Evaluation uses x86-64 ELF C binaries from Debian packages, built with mixed compilers and optimization settings, plus Nero’s smaller dataset; the trained model is specific to x86-64 GNU/Linux binaries. All tools receive function boundaries from symbol tables at test time, so boundary-detection errors are excluded. Many test names also occur in training; restricted to names never seen in training, F1 falls to 0.242. Obfuscated and adversarial binaries are out of scope. Debin and Dire figures on the Nero dataset are copied from the Nero paper rather than rerun.

  **Authors:** James Patrick-Evans et al.

  </details>

- [**SymLM: Predicting Function Names in Stripped Binaries via Context-Sensitive Execution-Aware Code Embeddings**](https://dl.acm.org/doi/10.1145/3548606.3560612)

  SymLM predicts function names for stripped binaries as sets of name words. It encodes each function’s instructions with a Trex model pretrained on micro-execution traces, fuses them with embeddings of callers, internal callees and external library calls taken from Ghidra’s interprocedural CFG, and scores words from a fixed vocabulary with an MLP decoder; name preprocessing and a word-embedding module, CodeWordNet, handle abbreviations and synonyms. On 1,431,169 functions from 16,027 binaries of 27 projects across x86, x64, ARM and MIPS, O0–O3 and four Hikari obfuscations, the authors report weighted average precision 0.634, recall 0.677 and F1 0.655, plus a firmware case study.

  ACM CCS 2022 · Conference paper · [PDF](https://xinjin95.github.io/assets/pdf/SymLM_ccs2022_paper.pdf) · [Code](https://github.com/OSUSecLab/SymLM) · [Full entry & citation](https://awesomerea.org/papers/paper-symlm/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Names are predicted as unordered word sets from a fixed training vocabulary and scored with word-level precision, recall and F1, with CodeWordNet counting semantically similar words as matches. This is not exact source-name recovery, and out-of-vocabulary words cannot be produced. Binaries were built with GCC 7.5 for Linux and split by binary within the same 27 projects. On 540 binaries from 12 unseen projects, overall performance remains lower, which the authors partly attribute to vocabulary mismatch; a later NDSS 2025 comparison on deduplicated data reports SymLM’s average F1 at 0.105. NFRE comparisons are x64-only, and NERO comparisons use NERO’s dataset. Obfuscation covers four Hikari passes, not packing or encryption. In the firmware case study, 172 of 1,061 functions in eight 32-bit ARM firmware images received partially correct names.

  **Authors:** Xin Jin et al.

  </details>

- [**Augmenting Decompiler Output with Learned Variable Names and Types**](https://www.usenix.org/conference/usenixsecurity22/presentation/chen-qibin)

  Introduces DIRTY, a Transformer model that recommends variable names and types from decompiled code and layout information, together with the DIRT corpus for training and evaluation.

  USENIX Security 2022 · Conference paper · [PDF](https://arxiv.org/pdf/2108.06363) · [Code](https://github.com/CMUSTRUDEL/DIRTY) · [Full entry & citation](https://awesomerea.org/papers/paper-dirty/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The original pipeline is built around C programs and Hex-Rays output. Predicted names and types are learned hypotheses, not guaranteed original symbols. The published paper is from 2022, although its arXiv preprint first appeared in 2021.

  **Authors:** Qibin Chen et al.

  </details>

- [**jTrans: Jump-Aware Transformer for Binary Code Similarity Detection**](https://dl.acm.org/doi/10.1145/3533767.3534367)

  jTrans embeds binary functions for similarity search with a BERT-style Transformer. Its jump-aware representation shares parameters between a direct jump’s operand token and the positional embedding of the jump target, so control flow enters the instruction sequence without a separate graph network. The model is pre-trained with masked language modeling and jump-target prediction, then fine-tuned with a cosine triplet objective on functions compiled from the same source at different optimization levels. The paper also introduces BinaryCorp, built by compiling C/C++ packages from Arch Linux’s official repositories and the AUR with gcc and g++.

  ACM ISSTA 2022 · Conference paper · [PDF](https://arxiv.org/pdf/2205.12713v1) · [Code](https://github.com/vul337/jTrans) · [Full entry & citation](https://awesomerea.org/papers/paper-jtrans/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The model is trained on a single architecture (x86, per the paper’s discussion); cross-architecture search is not evaluated. Only direct jumps are encoded, and indirect-jump targets are left out of scope. Disassembly and function extraction rely on IDA Pro 7.5, so boundary errors upstream are not measured. BinaryCorp pairs gcc/g++ builds across O0–O3 and Os, with train and test split by project; it does not cover obfuscation or other compilers, and only the vulnerability study adds clang variants. Author-reported Recall<span>@</span>1 at pool size 10,000 on BinaryCorp-26M averages 62.5% against 32.0% for the best baseline, and accuracy still falls as pools grow, which the authors note for larger real-world pools. The vulnerability search uses eight CVEs with ten variants each. Baselines date from 2022, and Asm2Vec and OrderMatters were reimplemented, so the comparison does not establish current rankings. Similarity ranking identifies candidate matches; it does not recover source code, names or types.

  **Authors:** Hao Wang et al.

  </details>

- [**ExeBench: an ML-scale dataset of executable C functions**](https://dl.acm.org/doi/10.1145/3520312.3534867)

  ExeBench is a dataset, not a decompiler. It extracts C functions from GitHub and AnghaBench, makes them compilable by locating real headers and definitions or injecting synthetic ones, and generates input/output examples from function signatures with a C++ wrapper that runs each function. After exact deduplication the authors report 4,485,817 compilable and 687,843 executable functions, of which 124,612 have rich IO that a constant or identity implementation cannot pass; the paper also describes x86 and ARM assembly at O0, Os and Ofast for each row. Decompilation studies such as SLaDe and LLM4Decompile later used it to test whether decompiled functions re-execute correctly.

  ACM SIGPLAN MAPS 2022 · Conference paper · [PDF](https://dl.acm.org/doi/pdf/10.1145/3520312.3534867) · [Code](https://github.com/jordiae/exebench/tree/8b47d483c2e39ea40a304fbaac46e41a1a14272f) · [Full entry & citation](https://awesomerea.org/papers/paper-exebench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** IO is generated from signatures without program context: 10 pairs per function (30 across three seeds of synthetic definitions), arrays default to 32 elements, and success falls below 5% for functions with pointer–integer conversions and stays low for goto, labels and complex control flow, so executable functions skew simpler than the compilable population. Synthetic IO is produced with injected stand-in definitions rather than the functions’ real dependencies; only 4,464 functions have rich IO with real definitions. Finite IO pairs test behavior on sampled inputs, not semantic equivalence, and deduplication removes exact matches after tokenization only. Running functions with real dependencies executes untrusted code; the authors used restricted containers. The paper’s exact v1.00 data is available only on request, while the public v1.01 release has revised splits (for example 2,134 instead of 2,232 real test functions). Each function keeps its source repository’s license; ExeBench additions are MIT.

  **Authors:** Jordi Armengol-Estapé et al.

  </details>

- [**Beyond the C: Retargetable Decompilation using Neural Machine Translation**](https://www.ndss-symposium.org/ndss-paper/auto-draft-298/)

  BTC (Beyond The C) treats decompilation as plain-text translation from compiler-emitted x86-64 assembly to source code. It uses byte-pair-encoding tokenizers trained separately on assembly and source, and a standard fairseq transformer. Function pairs are matched through the compiler's CFI and line directives rather than language-specific parsers, compiler plugins or lifters, so the same pipeline is retrained for Go, Fortran, OCaml and C. Training sets range from about 10,000 functions for small C, Go and Fortran corpora to 2 million C functions built from Debian packages. The best model, trained on the large C set, reaches a normalized average edit distance of 0.46 on held-out functions.

  Workshop on Binary Analysis Research (BAR) 2022 · Conference paper · [PDF](https://www.ndss-symposium.org/wp-content/uploads/bar2022_23009_paper.pdf) · [Code](https://figshare.com/s/2c68b9c181e80f4e3b06) · [Full entry & citation](https://awesomerea.org/papers/paper-beyond-the-c/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Evaluation covers four languages at function level and scores outputs only by normalized edit distance to the original source. No compilation, test-based or semantic-equivalence check is reported, and whole-program decompilation is not evaluated. The authors state that the method cannot guarantee semantic correctness and is not yet ready for practical use on real code: even the best score means changes to roughly half of a function's tokens. Input is compiler-produced x86-64 assembly with labels and CFI directives intact, so disassembly of stripped binaries, other architectures and compilers without such directives are outside the evaluation. Sequence-length limits exclude long functions, and the small corpora are mostly competitive-programming and small utility code. The comparison with Katz et al. cites that work's reported score on shorter snippets rather than rerunning it on the same data.

  **Authors:** Iman Hosseini et al.

  </details>

- [**Neural reverse engineering of stripped binaries using augmented control flow graphs**](https://dl.acm.org/doi/10.1145/3428293)

  Nero predicts names for procedures in stripped x86-64 Linux executables; it does not produce decompiled code. Static analysis reconstructs call sites, including imported API names, and augments their arguments with concrete and abstract values along control-flow paths. LSTM, Transformer and graph neural network encoders over the resulting augmented call-site graph feed a decoder that generates the name as subtokens. On a GNU-package test set the authors report 45.53 F1 for Nero-GNN, against 35.52 for an adapted DIRE and 33.66 for Debin.

  Proceedings of the ACM on Programming Languages (OOPSLA 2020) · Journal article · [PDF](https://arxiv.org/pdf/1902.09122v4) · [Code](https://github.com/tech-srl/Nero/tree/7dac9f5748974ea8f39b5f29bb3c7d33f971077e) · [Full entry & citation](https://awesomerea.org/papers/paper-nero/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Evaluation uses 67,246 procedures from C-only GNU packages built as x86-64 Linux executables, split by package into 60,403/2,034/4,809 examples after removing C++ executables, tests, statically linked packages and duplicate package versions. Labels come from names present before stripping, and F1 is measured over name subtokens, so outputs are learned suggestions rather than recovered original symbols. Simulated API-name obfuscation, which zeroes the .dynstr section, lowers Nero-GNN to 38.83 F1; packers and heavier obfuscation are not addressed. A procedure needs at least one statically detectable call site, and inlined procedures cannot be named. Data generation relied on a licensed IDA Pro (tested with 6.95) for procedure boundaries and export, plus angr and LLVM 10, and the model code uses TensorFlow 1.13.1; no claim is made about compatibility with current tool versions.

  **Authors:** Yaniv David et al.

  </details>

- [**DIRE: A Neural Approach to Decompiled Identifier Naming**](https://doi.org/10.1109/ASE.2019.00064)

  Combines lexical and structural information from decompiler output to predict meaningful variable names, with a training and evaluation corpus derived from compiled C projects.

  ASE 2019 · Conference paper · [PDF](https://arxiv.org/pdf/1909.09029) · [Code](https://github.com/pcyin/dire) · [Full entry & citation](https://awesomerea.org/papers/paper-dire/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** This is learned identifier naming, not complete source reconstruction or an autonomous agent. Its reported results concern an x86-64 C corpus and depend on decompiler output. The original author repository is deprecated and points to a successor.

  **Authors:** Jeremy Lacomis et al.

  </details>

- [**Coda: An End-to-End Neural Program Decompiler**](https://proceedings.neurips.cc/paper_files/paper/2019/hash/093b60fd0557804c8ba0cbf1453da22f-Abstract.html)

  Coda decompiles the assembly of short functions into C in two phases. An instruction-type-aware N-ary Tree-LSTM encoder and an attention-fed AST decoder first generate a code sketch; an ensemble of neural error predictors then proposes token corrections, each kept only if recompiling the candidate does not increase its edit distance to the input assembly. On synthetic benchmarks the authors report 82% average program accuracy after correction, against 12% for a sequence-to-sequence baseline with attention.

  NeurIPS 2019 · Conference paper · [PDF](https://proceedings.neurips.cc/paper_files/paper/2019/file/093b60fd0557804c8ba0cbf1453da22f-Paper.pdf) · [Full entry & citation](https://awesomerea.org/papers/paper-coda/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Training and test programs are randomly generated from Karel commands, math.h calls and arithmetic or logical expressions, in short and long variants (average length 15 and 30), 50,000 pairs per task, compiled without optimization: clang -O0 for the main MIPS results and gcc -O0 for an x86-64 appendix that reports sketch token accuracy only, about 6% lower on average. Real-world checks are small PyTorch C++ API model-construction and Hacker's Delight loop-free programs. Program accuracy requires an exact token match with the ground-truth source, the metric under which the paper reports 0% for conventional decompilers. Error correction assumes the compiler configuration is known, and token accuracy drops for longer programs. The results show neither optimized, whole-program nor binary-equivalent decompilation, and the paper names no author implementation.

  **Authors:** Cheng Fu et al.

  </details>

- [**Debin: Predicting Debug Information in Stripped Binaries**](https://dl.acm.org/doi/10.1145/3243734.3243866)

  Debin predicts debug information for stripped ELF binaries on x86, x64 and ARM. After lifting code to BAP-IR, an Extremely randomized Trees classifier decides which registers and memory offsets hold source-level variables. A conditional random field, solved with Nice2Predict, then jointly predicts names and types for variables and functions, and the result is written back as DWARF sections. On 300 held-out binaries per architecture, the authors report 68.8% precision and 68.3% recall for x64 names and types.

  ACM CCS 2018 · Conference paper · [PDF](https://files.sri.inf.ethz.ch/website/papers/ccs18-debin.pdf) · [Code](https://github.com/eth-sri/debin) · [Full entry & citation](https://awesomerea.org/papers/paper-debin/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The dataset has 3,000 non-stripped executables and shared libraries per architecture from 830 Linux debug-symbol packages of C code built with default package settings, split 2,700/300 for training and testing. Accuracy evaluation assumes given function boundaries; for fully stripped inputs, BAP's ByteWeight infers them, which the paper cites as about 93% accurate. Debin predicts 17 types, and leaves struct and union contents, line numbers and formats such as PE outside the evaluation. A prediction counts only when it equals the original debug value. Models learned from compiler-generated, benign code may be less accurate on obfuscated binaries, hand-written assembly or malware. The 35-sample malware study is manual inspection of decompiled output with no accuracy figures, because the samples lack ground-truth debug information.

  **Authors:** Jingxuan He et al.

  </details>

<a id="papers-website-reconstruction"></a>
### Website reconstruction

[↑ Paper topics](#papers) · [Contents](#contents)

- [**Vision2Web: A Hierarchical Benchmark for Visual Website Development with Agent Verification**](https://proceedings.mlr.press/v306/he26n.html)

  Benchmarks website development from visual prototypes and written requirements across 100 static-page, 66 interactive-frontend and 27 full-stack tasks, combining workflow-based functional checks with model-judged visual comparison.

  ICML 2026 · Conference paper · [PDF](https://raw.githubusercontent.com/mlresearch/v306/main/assets/he26n/he26n.pdf) · [Code](https://github.com/zai-org/Vision2Web) · [Full entry & citation](https://awesomerea.org/papers/paper-vision2web/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The full-stack tier is specification-driven, not reconstruction solely by exploring a live website. Workflows test state management and CRUD outcomes, but finite agent judgments do not establish exact backend or durable-database equivalence. The current public evaluator maintains a browser session within each workflow and permits local business-API checks; this is not a universal persistence proof.

  **Authors:** Zehai He et al.

  </details>

- [**ProgramDistill: From Interactive Web Apps to Verifiable Reference-Guided SWE Tasks**](https://arxiv.org/abs/2609.18805)

  Evaluates recovery of web-app behavior from a live reference with hidden source. It provides 4,063 feature-restoration tasks across 26 applications and a separate 12-application reconstruction setting, scored by replaying dependent browser workflows.

  arXiv 2026 · Preprint · [PDF](https://arxiv.org/pdf/2609.18805v1) · [Code](https://huggingface.co/datasets/microsoft/ProgramDistill) · [Full entry & citation](https://awesomerea.org/papers/paper-programdistill/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Tests cover finite, model-mined behaviors in self-contained apps, including SaaS clones. Persistence failures can be detected through replayed workflows, but passing does not establish all backend or database invariants. Evaluated agents receive structured browser observations without screenshots; visual fidelity is not measured. Public verifiers and reference solutions are not a contamination-resistant test set.

  **Authors:** Jeonghye Kim et al.

  </details>

- [**UI2App: Benchmarking Visual Interaction Inference in Executable Web Application Generation**](https://arxiv.org/abs/2607.06306)

  UI2App evaluates runnable React/TypeScript applications generated from 600 screenshots across 95 web applications. It separates build executability, visual fidelity and screenshot-implied interaction behavior, including cross-route state, using a reference interaction taxonomy and public evaluation pipeline.

  arXiv 2026 · Preprint · [PDF](https://arxiv.org/pdf/2607.06306v2) · [Code](https://github.com/chenmancm169/UI2App) · [Full entry & citation](https://awesomerea.org/papers/paper-ui2app/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Static screenshots underdetermine behavior; the rubric accepts multiple valid implementations rather than proving equivalence to the original application or backend. Auto IIS judges generated source and screenshots without tool execution; human runtime validation covers a 45-application subset. Cross-route state is not necessarily durable persistence across reloads or sessions. Main results use one generation per application-model pair, with repeated runs on a subset.

  **Authors:** Grace Man Chen et al.

  </details>

- [**Dashboard2Code: Evaluating Multimodal Models on Reconstructing Interactive Dashboards**](https://aclanthology.org/2026.acl-long.1750/)

  Evaluates agents that actively explore a running dashboard and reconstruct its appearance and interaction logic. DashboardMimic provides 180 Plotly+Dash examples, with code-semantic analysis and dynamic interaction tests for the generated implementations.

  ACL 2026 · Conference paper · [PDF](https://aclanthology.org/2026.acl-long.1750.pdf) · [Code](https://github.com/nth2000/Dashboard2Code) · [Full entry & citation](https://awesomerea.org/papers/paper-dashboard2code/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Limited to Plotly+Dash dashboards, including model-augmented examples. Some settings expose DOM information and evaluation uses model judges. This is not a general backend-recovery benchmark. The linked dataset requires accepting access conditions and sharing contact information.

  **Authors:** Tianhao Niu et al.

  </details>

- [**CASCADE: LLM-powered JavaScript Deobfuscator at Google**](https://doi.org/10.1145/3786583.3786873)

  Uses Gemini to locate the prelude functions that Obfuscator.IO inserts for string obfuscation, then applies constant-propagation and inlining passes in the JSIR compiler IR to restore string literals and API names deterministically.

  ICSE-SEIP 2026 · Conference paper · [PDF](https://arxiv.org/pdf/2507.17691v2) · [Code](https://github.com/google/jsir) · [Full entry & citation](https://awesomerea.org/papers/paper-cascade/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The method addresses Obfuscator.IO string obfuscation; control-flow flattening, other obfuscators and an agent-based design are future work. Evaluation obfuscates 3,000 programs from the ETH 150k JavaScript dataset with four Obfuscator.IO presets and measures prelude detection, recovered literals and run time, not functional equivalence. Production deployment and scan volume are author-reported, and production pre-filtering uses a proprietary YARA rule.

  **Authors:** Shan Jiang et al.

  </details>

- [**ScreenCoder: Advancing Visual-to-Code Generation for Front-End Automation via Modular Multimodal Agents**](https://arxiv.org/abs/2507.22827)

  Splits screenshot-to-code generation among grounding, planning and generation agents that label UI regions, build a hierarchical layout tree and write HTML/CSS. The pipeline also produces the Screen-10K training pairs used for supervised and reinforcement fine-tuning, and the paper introduces the 1,000-page ScreenBench.

  EMNLP 2026 · Accepted · [PDF](https://arxiv.org/pdf/2507.22827v2) · [Code](https://github.com/leigest519/ScreenCoder) · [Full entry & citation](https://awesomerea.org/papers/paper-screencoder/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Output is static HTML/CSS layout; interaction, JavaScript behavior and backend logic are not reconstructed. Results are visual-similarity scores (CLIP and OCR-matched text blocks) on ScreenBench and Design2Code, which do not establish code-level or functional equivalence. The released pipeline calls a hosted model API, Doubao by default. The reviewed text is arXiv v2; the accepted EMNLP version may differ.

  **Authors:** Yilei Jiang et al.

  </details>

- [**IWR-Bench: Can LVLMs reconstruct interactive webpage from a user interaction video?**](https://proceedings.iclr.cc/paper_files/paper/2026/hash/55bfedfd31489e5ae83c9ce8eec7b0e1-Abstract-Conference.html)

  Tests reconstruction of interactive webpages from user-interaction videos and supplied static assets. Its 113 tasks replay annotated action sequences to assess visual fidelity and functional behavior across observed page states.

  ICLR 2026 · Conference paper · [PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/55bfedfd31489e5ae83c9ce8eec7b0e1-Paper-Conference.pdf) · [Code](https://github.com/SIGMME/IWR-Bench) · [Full entry & citation](https://awesomerea.org/papers/paper-iwr-bench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The required output is one HTML file; the paper explicitly instructs models to mock implied backend logic with static JavaScript data. Trajectory coverage and model-based judgments do not prove complete website or backend equivalence.

  **Authors:** Yang Chen et al.

  </details>

- [**JsDeObsBench: Measuring and Benchmarking LLMs for JavaScript Deobfuscation**](https://doi.org/10.1145/3719027.3744871)

  Builds an execution-verifiable JavaScript deobfuscation benchmark by applying seven JavaScript-Obfuscator transformations to Project CodeNet programs with test cases, then scores LLM and tool outputs for syntax, execution, code simplification and similarity to the original code.

  ACM CCS 2025 · Conference paper · [PDF](https://arxiv.org/pdf/2506.20170v1) · [Code](https://github.com/Ch3nYe/JsDeObsBench) · [Full entry & citation](https://awesomerea.org/papers/paper-jsdeobsbench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** On average, LLM outputs passed execution checks 60.93% of the time, against 83% for the two existing deobfuscator baselines. All samples come from a single obfuscator applied to moderate-length competitive-programming solutions. The 4,515 obfuscated malware samples have no test cases and are compared only through behavior traces.

  **Authors:** Guoqiang Chen et al.

  </details>

- [**Interaction2Code: Benchmarking MLLM-based Interactive Webpage Code Generation from Interactive Prototyping**](https://doi.org/10.1109/ASE63991.2025.00028)

  Benchmarks reconstruction of interactive webpages from screenshots before and after an interaction. The final study covers 127 webpages and 374 interactions, comparing rendered appearance, automated interaction checks, and human usability judgments.

  ASE 2025 · Conference paper · [PDF](https://arxiv.org/pdf/2411.03292v3) · [Code](https://github.com/WebPAI/Interaction2Code) · [Full entry & citation](https://awesomerea.org/papers/paper-interaction2code/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The inputs specify individual interaction transitions, not autonomous exploration of a complete site. Its tests do not establish long-workflow, server-side, or original-source equivalence; a detectable interaction is not necessarily usable.

  **Authors:** Jingyu Xiao et al.

  </details>

- [**WebUIBench: A Comprehensive Benchmark for Evaluating Multimodal Large Language Models in WebUI-to-Code**](https://aclanthology.org/2025.findings-acl.815/)

  Diagnoses webpage-to-code capability through visual perception, HTML programming, image-to-HTML understanding, and screenshot reconstruction tasks. It separates underlying skills using question-answer pairs derived from real websites.

  Findings of ACL 2025 · Conference paper · [PDF](https://aclanthology.org/2025.findings-acl.815.pdf) · [Full entry & citation](https://awesomerea.org/papers/paper-webuibench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Primarily evaluates visual and HTML reconstruction skills. The paper includes a preliminary interaction study, not a full workflow or backend-equivalence benchmark. The official repository currently exposes README and images but not the evaluation scripts described in its instructions.

  **Authors:** Zhiyu Lin et al.

  </details>

- [**Divide-and-Conquer: Generating UI Code from Screenshots**](https://doi.org/10.1145/3729364)

  Recursively divides a webpage screenshot along visual separation lines, has a multimodal model generate HTML/CSS for each leaf segment, and assembles child code upward into the full page; evaluated with GPT-4o, Gemini and Claude models and a small developer study.

  Proceedings of the ACM on Software Engineering 2025 · Journal article · [PDF](https://arxiv.org/pdf/2406.16386v3) · [Code](https://github.com/WebPAI/DCGen) · [Full entry & citation](https://awesomerea.org/papers/paper-dcgen/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** It reconstructs static visual layout as HTML/CSS, not interaction, JavaScript behavior or backend logic. Test pages are self-contained snapshots with images replaced by placeholders; the main evaluation samples 111 of 348 top-ranked sites, adds 80 harder GitHub Pages pages, and the usefulness study has four participants. Segmentation uses manually set thresholds, and assembly can still misarrange elements.

  **Authors:** Yuxuan Wan et al.

  </details>

- [**WebCode2M: A Real-World Dataset for Code Generation from Webpage Designs**](https://dl.acm.org/doi/10.1145/3696410.3714889)

  WebCode2M pairs about 2.56 million real-world webpage screenshots with purified HTML/CSS code and element bounding-box layout trees. Pages sampled from a Common Crawl snapshot are cleaned (scripts, metadata and hidden elements removed, styles merged into one block), rendered with Playwright, and filtered by a neural scorer trained on 10,000 annotated samples. The paper fine-tunes Pix2Struct-1.3B as the WebCoder baseline, introduces TreeBLEU to measure DOM-structure recall, and benchmarks specialized, open and commercial multimodal models on short, medium and long test subsets of 256 pages each.

  WWW 2025 · Conference paper · [PDF](https://arxiv.org/pdf/2404.06369v2) · [Code](https://github.com/CGCL-codes/naturalcc/tree/main/examples/webcode2m) · [Full entry & citation](https://awesomerea.org/papers/paper-webcode2m/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The task is static HTML/CSS generation from a design image. Scripts are stripped during purification, so interaction, client-side behavior and backend logic are not reconstructed, and outputs are judged by visual score, CLIP similarity and TreeBLEU rather than functional equivalence. The paper reports that no evaluated model reproduces image elements accurately, and scores fall as target code grows longer. The 768 test pages were drawn from high-scoring candidates and manually inspected; the scorer is about 90% accurate, so low-quality training samples remain, and the authors warn that crawled content may still include inappropriate material. Commercial models are named only by family, and about one-third of Gemini test cases failed with recitation errors, so those comparisons are snapshots. The dataset card's CC BY 4.0 license does not clear rights in the crawled pages' code, text or images.

  **Authors:** Yi Gui et al.

  </details>

- [**Design2Code: Benchmarking Multimodal Code Generation for Automated Front-End Engineering**](https://aclanthology.org/2025.naacl-long.199/)

  Evaluates reconstruction of frontend code from webpage screenshots using real-world reference pages, visual-element and layout metrics, and human assessment.

  NAACL 2025 · Conference paper · [PDF](https://aclanthology.org/2025.naacl-long.199.pdf) · [Code](https://github.com/NoviScl/Design2Code) · [Full entry & citation](https://awesomerea.org/papers/paper-design2code/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** This is visual website reconstruction, not binary decompilation or recovery of backend behavior and interactive workflows. The main benchmark contains 484 webpages with placeholder images; code and data have separate licensing terms.

  **Authors:** Chenglei Si et al.

  </details>

- [**Large Language Models for Code Analysis: Do LLMs Really Do Their Job?**](https://www.usenix.org/conference/usenixsecurity24/presentation/fang)

  Evaluates GPT-3.5-turbo, GPT-4, LLaMA-2-13B, Code-LLaMA-2-13B-Instruct and StarChat-Beta on explaining what de-commented JavaScript, Python and C code does, then repeats the task on JavaScript obfuscated with JavaScript Obfuscator (identifier renaming, dead-code injection, control-flow flattening and string splitting) and with Wobfuscator’s WebAssembly transformation. GPT-3.5 and GPT-4 are also asked to rewrite 100 IOCCC winning programs as readable, compilable code. Case studies apply GPT models to a botnet and a benign browser-extension repository, an Android SMS stealer decompiled with JD-GUI, and WannaCry code decompiled with RetDec.

  USENIX Security 2024 · Conference paper · [PDF](https://www.usenix.org/system/files/usenixsecurity24-fang.pdf) · [Full entry & citation](https://awesomerea.org/papers/paper-llm-code-analysis/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Ground truth is GPT-4’s own explanations after manual checking by four students; other models are scored against those texts with similarity metrics and a GPT-4 judge, which the authors say is unreliable without manual calibration. Correctness is judged at explanation level, not by recovered behavior or executable equivalence. Only JavaScript is obfuscated with generated transformations; neither GPT model deciphered the WebAssembly that Wobfuscator inserts, and the smaller models produced no meaningful explanations once obfuscation was applied. Author-reported figures include 97.4% GPT-4 accuracy on non-obfuscated code and 87% on obfuscated JavaScript; in IOCCC de-obfuscation, about 20% of GPT-3.5’s targets and 19% of GPT-4’s yielded compilable code, and only 8% and 4% produced correct results. The malware analyses are qualitative case studies on a few samples, with manual chunking for WannaCry, missed behavior when context was split, and a false alarm in the botnet repository. Models recognized code from popular repositories, so memorization is a confound. The evaluated GPT-3.5/GPT-4-era and LLaMA-2-13B-class models are dated. The study analyzes source or already-decompiled text; it does not perform binary decompilation.

  **Authors:** Chongzhou Fang et al.

  </details>

- [**Web2Code: A Large-scale Webpage-to-Code Dataset and Evaluation Framework for Multimodal LLMs**](https://proceedings.nips.cc/paper_files/paper/2024/hash/cb66be286795d71f89367d596bf78ea7-Abstract-Datasets_and_Benchmarks_Track.html)

  Studies screenshot-to-HTML reconstruction through instruction tuning and two evaluation benchmarks. Web2Code combines generated webpages, refined WebSight and pix2code image/code pairs, and WebSRC-derived question answering. Models produce HTML from a webpage image and instruction; rendered output is compared visually, while a separate benchmark measures screenshot understanding.

  NeurIPS 2024 Datasets and Benchmarks · Conference paper · [PDF](https://proceedings.neurips.cc/paper_files/paper/2024/file/cb66be286795d71f89367d596bf78ea7-Paper-Datasets_and_Benchmarks_Track.pdf) · [Code](https://github.com/MBZUAI-LLM/web2code) · [Full entry & citation](https://awesomerea.org/papers/paper-web2code/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Evaluation uses 1,198 screenshots and 5,990 yes/no questions. WCGB grades rendered images with GPT-4V; its User Interface and Interactivity category measures element appearance, not executed click paths, persistent state or backend behavior. Synthetic and refined examples do not establish coverage of arbitrary real web applications, original-source equivalence or code quality. The paper reports contact-information issues in 2.7% of a 1,000-item privacy sample, so a blanket claim that the data is free of such information is unsupported.

  **Authors:** Sukmin Yun et al.

  </details>

<a id="papers-game-reconstruction"></a>
### Game reconstruction and reverse engineering

[↑ Paper topics](#papers) · [Contents](#contents)

- [**GameReplica: A Benchmark for Black-Box Visual Game Replication by Vision-Language Agents**](https://arxiv.org/abs/2609.22308)

  Evaluates whether vision-language agents can infer hidden game rules through screenshots and active interaction, then build runnable single-file HTML replicas across 125 tasks from 25 web games, each with five difficulty levels.

  arXiv 2026 · Preprint · [PDF](https://arxiv.org/pdf/2609.22308v1) · [Full entry & citation](https://awesomerea.org/papers/paper-gamereplica/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The tasks cover rule-driven web puzzles and board games, not native or commercial game reconstruction. Rule, implementation, and visual scores use LLM judges and do not prove behavioral equivalence. The official site provides demos; a benchmark-code repository was not verified.

  **Authors:** Boyu Qiao et al.

  </details>

- [**Tycho: Active Abstraction with Programmatic World Models for ARC-AGI-3**](https://arxiv.org/abs/2607.28287)

  Tycho constructs editable Python models of game state, transitions, rendering and outcomes from action/observation histories in unfamiliar ARC-AGI-3 games. It checks model predictions against recorded transitions and can use, repair or bypass these models during planning.

  arXiv 2026 · Preprint · [PDF](https://arxiv.org/pdf/2607.28287v1) · [Code](https://github.com/NIMI-research/Tycho) · [Full entry & citation](https://awesomerea.org/papers/paper-tycho/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Evaluation uses one stochastic run per configuration on 25 public games and 183 levels; five games informed harness development. Models may abstain on cells or accept bounded rendering variants. Transition replay and game scores do not establish complete engine reconstruction, correct objectives, unseen-state fidelity, unseen-game generalization or run-to-run reliability; the agent can bypass modeling.

  **Authors:** Jens Lehmann et al.

  </details>

- [**RevengeBench: Reverse Engineering Code-Space Policies from Behavioral Experiments**](https://arxiv.org/abs/2606.26094)

  Tests whether agents can recover executable decision policies from behavioral traces and self-designed opponent probes, using 75 synthetic policies across five game arenas and measuring held-out action agreement and downstream competitive value.

  arXiv 2026 · Preprint · [PDF](https://arxiv.org/pdf/2606.26094v1) · [Code](https://github.com/bethgelab/revenge-bench) · [Full entry & citation](https://awesomerea.org/papers/paper-revengebench/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The targets are fixed synthetic policies, not full games or adaptive adversaries. Agreement on finitely evaluated states does not uniquely identify source code, and some arenas have substantial variance. The public package omits some paper-only plotting and ablation suites; reproduction also needs CodeClash, a container runtime, and model access.

  **Authors:** Babak Rahmani et al.

  </details>

- [**SPRITE: From Static Mockups to Engine-Ready Game UI**](https://doi.org/10.1145/3772363.3798742)

  Transforms game-interface screenshots into editable engine assets through hierarchical YAML, visual grounding, asset extraction, and Unity UXML/USS synthesis, with evaluation on a curated game-UI benchmark and review by three senior UI/UX designers.

  CHI EA 2026 (poster/extended abstract) · Conference paper · [PDF](https://baiyunshu.github.io/sprite.github.io/Source/chiea26-516.pdf) · [Full entry & citation](https://awesomerea.org/papers/paper-sprite-game-ui/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The generated interactions cover basic hover, toggle, and click behavior. Complex temporal and drag-and-drop logic remain outside scope, and translucent overlap or ambiguous diegetic layouts can fail. This is game-UI prototyping, not complete gameplay reconstruction; the official page still labels code as coming soon.

  **Authors:** Yunshu Bai et al.

  </details>

- [**WorldCoder, a Model-Based LLM Agent: Building World Models by Writing Code and Interacting with the Environment**](https://papers.nips.cc/paper_files/paper/2024/hash/820c61a0cd419163ccbd2c33b268816e-Abstract-Conference.html)

  WorldCoder learns executable Python transition and reward models from environment interactions and natural-language goals. It refines code against recorded experiences and an optimistic planning constraint, studying transfer and task solving in Sokoban, MiniGrid and ALFWorld.

  NeurIPS 2024 · Conference paper · [PDF](https://papers.neurips.cc/paper_files/paper/2024/file/820c61a0cd419163ccbd2c33b268816e-Paper-Conference.pdf) · [Code](https://github.com/haotang1995/WorldCoder) · [Full entry & citation](https://awesomerea.org/papers/paper-worldcoder/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Assumes deterministic dynamics and symbolic, discrete states rather than recovering a game from arbitrary pixels or binaries. Consistency with observed transitions and successful planning do not establish complete engine equivalence or correctness on every unseen state. Evaluation concerns bounded environment models and planning, not original source or asset recovery.

  **Authors:** Hao Tang et al.

  </details>

- [**Generating Code World Models with Large Language Models Guided by Monte Carlo Tree Search**](https://proceedings.neurips.cc/paper_files/paper/2024/hash/6f479ea488e0908ac8b1b37b27fd134c-Abstract-Conference.html)

  GIF-MCTS generates executable Python transition and reward models from natural-language environment descriptions and offline state-transition trajectories, using prediction feedback to generate, improve and repair code. CWMB evaluates 18 reinforcement-learning environments and downstream planning; a separate experiment uses a simplified Read to Fight Monsters grid world.

  NeurIPS 2024 · Conference paper · [PDF](https://proceedings.neurips.cc/paper_files/paper/2024/file/6f479ea488e0908ac8b1b37b27fd134c-Paper-Conference.pdf) · [Code](https://github.com/nicoladainese96/code-world-models) · [Full entry & citation](https://awesomerea.org/papers/paper-code-world-models/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Assumes deterministic, fully observable dynamics and sufficiently detailed descriptions; this is not recovery from pixels or binaries alone. Accuracy uses the replay transitions supplied during synthesis, alongside planning-return evaluation, rather than proving correctness on all unseen states or full-engine equivalence. RTFM fixes the manual across episodes and keeps monsters stationary. CWMB also includes non-game control and physics tasks; some planning returns are unavailable and complex continuous-state models remain difficult.

  **Authors:** Nicola Dainese et al.

  </details>

<a id="papers-app-reconstruction"></a>
### App reconstruction and analysis

[↑ Paper topics](#papers) · [Contents](#contents)

- [**UIOrchestra: Generating High-Fidelity Code from UI Designs with a Multi-agent System**](https://aclanthology.org/2025.findings-emnlp.150/)

  UIOrchestra converts static mobile UI designs into React/CSS through layout-description, code-generation and rendered-image comparison agents. Its APPUI benchmark contains 1,101 human-refined code/rendering pairs based on screenshots from 165 apps across 12 categories. The reference code is reconstructed for evaluation, rather than recovered original application source.

  Findings of EMNLP 2025 · Conference paper · [PDF](https://aclanthology.org/2025.findings-emnlp.150.pdf) · [Full entry & citation](https://awesomerea.org/papers/paper-uiorchestra/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Tests visual, component and code similarity, not native-package execution, interaction, backend behavior or application equivalence. APPUI references are rendered reconstructions of iOS screenshots; unavailable images/icons use placeholders. A human study covers 200 samples with four annotators. The difference-analysis prompt ignores font-size/typeface differences and placeholder image content. Model snapshots, rendering dependencies and a reproducible runtime setup were not verified; experiments were not rerun.

  **Authors:** Chuhuai Yue et al.

  </details>

- [**DeclarUI: Bridging Design and Development with Automated Declarative UI Code Generation**](https://doi.org/10.1145/3715726)

  Combines visual component extraction, multimodal models, page-transition graphs and iterative checks to reconstruct multi-page mobile UI code from designs or screenshots, evaluated with React Native, Flutter and ArkUI.

  Proceedings of the ACM on Software Engineering 2025 · Journal article · [PDF](https://xinyi-hou.github.io/files/zhou2024bridging.pdf) · [Code](https://github.com/security-pride/DeclarUI) · [Full entry & citation](https://awesomerea.org/papers/paper-declarui/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** People review and correct the inferred navigation graph. Evaluation covers 50 five-page UI sets; transition coverage and compilation do not establish full business-logic or backend recovery. Framework results vary, and visual metrics imperfectly reflect perceived fidelity. Public scripts and data are available, but no project-level license was found at the reviewed commit.

  **Authors:** Ting Zhou et al.

  </details>

- [**Machine Learning-Based Prototyping of Graphical User Interfaces for Mobile Apps**](https://doi.org/10.1109/TSE.2018.2844788)

  ReDraw turns screenshots or design mock-ups into native Android GUI prototypes by detecting components, classifying widget types with a CNN, and assembling a plausible view hierarchy with a data-driven nearest-neighbor method.

  IEEE Transactions on Software Engineering 2020 · Journal article · [PDF](https://arxiv.org/pdf/1802.02312v2) · [Full entry & citation](https://awesomerea.org/papers/paper-redraw/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The implementation covers 15 Android component classes and one screen at a time; multiple screens require manual combination, and hierarchy construction is tied to the mined screen size. Evaluation concerns appearance and view hierarchy, not recovery of original app logic or backends. Screenshots and reconstructed mock-ups served as proxies for real design artifacts; results were not independently reproduced here.

  **Authors:** Kevin Moran et al.

  </details>

- [**pix2code: Generating Code from a Graphical User Interface Screenshot**](https://doi.org/10.1145/3220134.3220135)

  Learns screenshot-to-DSL generation for native Android XML, iOS Storyboards and web HTML/CSS interfaces, then compiles the DSL into platform UI code.

  EICS 2018 · Conference paper · [PDF](https://arxiv.org/pdf/1705.07962v2) · [Code](https://github.com/tonybeltramelli/pix2code) · [Full entry & citation](https://awesomerea.org/papers/paper-pix2code/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Evaluation uses synthetic screenshot/code pairs: 1,500 training and 250 test instances per platform. Reported accuracy concerns DSL tokens, not complete apps or behavior. Text labels are ignored; platform datasets train separate models using the same architecture. The task covers layout, components and relationships, not application logic or backend recovery. The repository describes an educational research prototype; its older dependencies were not runtime-tested.

  **Authors:** Tony Beltramelli

  </details>

- [**From UI Design Image to GUI Skeleton: A Neural Machine Translator to Bootstrap Mobile GUI Implementation**](https://doi.org/10.1145/3180155.3180240)

  UI2code translates a mobile UI image into an Android component hierarchy and layout skeleton using a neural encoder-decoder. The paper evaluates structural prediction and a small developer study of implementing layouts from generated skeletons.

  ICSE 2018 · Conference paper · [PDF](https://chunyang-chen.github.io/publication/ui2code.pdf) · [Code](https://github.com/ccywch/UI2code) · [Full entry & citation](https://awesomerea.org/papers/paper-ui2code/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The output covers component types and hierarchy from a single image; detailed styling and text require developer work. Structural token accuracy and an eight-participant study on five screenshots do not establish complete visual fidelity, navigation, app logic or backend recovery. The main split is screenshot-based; a separate evaluation on 1,208 images from 20 unseen apps provides limited generalization evidence.

  **Authors:** Chunyang Chen et al.

  </details>

- [**Statistical Deobfuscation of Android Applications**](https://dl.acm.org/doi/10.1145/2976749.2978422)

  DeGuard reverses layout obfuscation in Android APKs, predicting original names for the fields, methods, classes and packages that ProGuard renames. Built on Soot, it represents an app as a dependency graph over program elements and keeps Android API and other unobfuscated names fixed. It then runs MAP inference with Nice2Predict on a conditional random field learned from 1,684 F-Droid apps, under constraints that keep the renamed APK semantically equivalent. On 100 held-out F-Droid apps obfuscated with ProGuard, names identical to the originals rise from 13.3% to 79.1%, and third-party library prediction reaches 91.3% precision and 91.0% recall.

  ACM CCS 2016 · Conference paper · [PDF](https://files.sri.inf.ethz.ch/website/papers/deguard.pdf) · [Full entry & citation](https://awesomerea.org/papers/paper-deguard/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Only layout (identifier) obfuscation is addressed. Data, control-flow and cryptographic obfuscation, custom string encryption, reflection and goto-based code reordering are not reversed, and the paper notes that most malware samples it inspected also used such techniques. The benchmark is 100 benign, open-source F-Droid apps, obfuscated by enabling ProGuard without changing its rules and scored by exact match to the original names, so semantically close names count as errors; elements that ProGuard removed are not scored. Accuracy on other obfuscators or on malware may be lower. Libraries are identified by a package-name heuristic covering 133 libraries, and the training apps may import the same libraries. The 49-family malware study gives manual examples, such as Base64 decoders and location handling, without precision figures.

  **Authors:** Benjamin Bichsel et al.

  </details>

- [**Reverse Engineering Mobile Application User Interfaces with REMAUI (T)**](https://ieeexplore.ieee.org/abstract/document/7372013)

  Reconstructs native Android UI code from screenshots or design bitmaps using OCR, computer vision, and layout heuristics; evaluates visual similarity and view hierarchies on 488 screenshots from over 100 Android and iOS applications.

  ASE 2015 · Conference paper · [PDF](https://c.csallner.org/papers/nguyen15reverse.pdf) · [Code](https://github.com/soumikmohianuta/pixtoapp) · [Full entry & citation](https://awesomerea.org/papers/paper-remaui/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The output is Android UI code; iOS screenshots are inputs, not evidence of native iOS output. Original logic and backend behavior are not recovered, and multi-screen transitions were future work. OCR/layout heuristics can misidentify content. The linked REMAUI v2 repository has older dependencies and is not the exact verified 2015 artifact.

  **Authors:** Tuan Anh Nguyen et al.

  </details>

<a id="papers-firmware-analysis"></a>
### Firmware analysis and rehosting

[↑ Paper topics](#papers) · [Contents](#contents)

- [**User-Space Dependency-Aware Rehosting for Linux-Based Firmware Binaries**](https://www.ndss-symposium.org/ndss-paper/user-space-dependency-aware-rehosting-for-linux-based-firmware-binaries/)

  FIRMWELL reconstructs the execution environment of Linux firmware services by running their initialization processes, locating blocking dependencies and repairing missing system-level behavior. It combines containerized QEMU-user emulation with a QEMU-system fallback, using process traces and binary analysis to recover resources needed by the target service.

  NDSS 2026 · Conference paper · [PDF](https://www.ndss-symposium.org/wp-content/uploads/2026-s249-paper.pdf) · [Code](https://github.com/qc9c/Firmwell) · [Full entry & citation](https://awesomerea.org/papers/paper-firmwell/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The evaluation concerns selected network services, not complete device or hardware equivalence. HTTP acceptance uses configured response-status and error-content checks; other services need their own criteria. Coverage depends on unpacking, supported architectures, initialization heuristics and peripheral models. Symbolic path explosion, solver timeouts and complex peripheral checks remain failure modes. The paper’s recovery strategy avoids patching target binaries; successful service interaction does not establish recovery of original source code or every device function.

  **Authors:** Chuan Qin et al.

  </details>

- [**Target-Centric Firmware Rehosting with Penguin**](https://www.ndss-symposium.org/ndss-paper/auto-draft-634/)

  Penguin rehosts embedded Linux firmware from an extracted filesystem by deriving an editable configuration of emulation transformations, such as file changes, pseudofiles, NVRAM values and network interfaces, from static analysis. Dynamic-analysis plugins expose failures so the configuration can be refined for each target, and a minimizer identifies which transformations a working rehosting needs.

  Workshop on Binary Analysis Research (BAR) 2025 · Conference paper · [PDF](https://www.ndss-symposium.org/wp-content/uploads/bar2025-final10.pdf) · [Code](https://github.com/rehosting/penguin) · [Full entry & citation](https://awesomerea.org/papers/paper-penguin/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Targets embedded Linux firmware through whole-system emulation with kernel replacement, as in Firmadyne and FirmAE; the implementation covers x86, ARM and MIPS and relies on the Linux syscall ABI. In the FirmAE comparison, success means a process binds port 80 or 443; a non-empty HTTP response is a stricter check, and the authors note neither shows full functionality. The 75% gain over FirmAE is author-reported on their own corpus of 13,649 images from vendor websites. Refinement still needs an analyst, and nondeterministic runs were repeated up to ten times. It builds an analysis environment, not a faithful device reproduction or source recovery.

  **Authors:** Andrew Fasano et al.

  </details>

- [**Fuzzware: Using Precise MMIO Modeling for Effective Firmware Fuzzing**](https://www.usenix.org/conference/usenixsecurity22/presentation/scharnowski)

  Rehosts monolithic ARM Cortex-M firmware for fuzzing, using locally scoped symbolic execution to model memory-mapped I/O accesses and focus input mutations on values relevant to firmware logic.

  USENIX Security 2022 · Conference paper · [PDF](https://www.usenix.org/system/files/sec22-scharnowski.pdf) · [Code](https://github.com/fuzzware-fuzzer/fuzzware) · [Full entry & citation](https://awesomerea.org/papers/paper-fuzzware/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The Cortex-M3/M4 artifact requires memory-map configuration and does not automatically model DMA. Abstracting hardware can produce crashes that are impossible on the physical device. This is an analysis environment, not original-source recovery or faithful full-device reconstruction.

  **Authors:** Tobias Scharnowski et al.

  </details>

- [**FirmAE: Towards Large-Scale Emulation of IoT Firmware for Dynamic Analysis**](https://doi.org/10.1145/3427228.3427294)

  Extends Firmadyne with empirically derived interventions for boot, networking, NVRAM, kernel behavior, and other runtime failures, enabling Linux router and IP-camera firmware web services to run for dynamic analysis.

  ACSAC 2020 · Conference paper · [PDF](https://syssec.kaist.ac.kr/pub/2020/kim_acsac2020.pdf) · [Code](https://github.com/pr0v3rbs/FirmAE) · [Full entry & citation](https://awesomerea.org/papers/paper-firmae/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Arbitration deliberately changes execution and targets functioning web interfaces, not identical physical-device behavior. The evaluation covers ARM little-endian and MIPS little-/big-endian firmware from routers and IP cameras; heuristics may fail on unseen devices or configurations. It reuses firmware binaries rather than recovering their source.

  **Authors:** Mingeun Kim et al.

  </details>

- [**HALucinator: Firmware Re-hosting Through Abstraction Layer Emulation**](https://www.usenix.org/conference/usenixsecurity20/presentation/clements)

  HALucinator rehosts monolithic ARM Cortex-M firmware by identifying hardware-abstraction-library functions and replacing them with authored Python handlers and peripheral models. LibMatch locates library interfaces; the QEMU/Avatar2 implementation supports interactive I/O, while the paper-associated HAL-fuzz variant uses AFL-Unicorn for fuzzing.

  USENIX Security 2020 · Conference paper · [PDF](https://www.usenix.org/system/files/sec20-clements.pdf) · [Code](https://github.com/embedded-sec/halucinator) · [Full entry & citation](https://awesomerea.org/papers/paper-halucinator/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** LibMatch requires an available HAL/library and a sufficiently similar compilation environment; compiler variation and inlining limit matching. Rehosting also needs a QEMU-supported architecture, firmware memory layout, interception addresses and authored handlers/models. Unmodeled direct hardware accesses may return zero or ignore writes, and simplified timing and peripheral behavior do not establish hardware equivalence. The authors’ rehosting and fuzzing demonstrations are not universal firmware coverage, complete device reconstruction or original-source recovery.

  **Authors:** Abraham A Clements et al.

  </details>

- [**Towards Automated Dynamic Analysis for Linux-based Embedded Firmware**](https://doi.org/10.14722/ndss.2016.23415)

  Firmadyne crawls, extracts and emulates Linux-based firmware for network-connected commercial devices such as routers and IP cameras. It replaces the vendor kernel with pre-built, instrumented kernels for little-endian ARM and little- and big-endian MIPS, boots the extracted filesystem under QEMU full-system emulation with a userspace NVRAM library, infers the network configuration, then runs automated analyses including 60 known and 14 newly found exploits. From 23,035 images across 42 vendors, the authors extracted 9,486 and report 887 of the 1,971 network-reachable images vulnerable to at least one sampled exploit.

  NDSS 2016 · Conference paper · [PDF](https://www.ndss-symposium.org/wp-content/uploads/2017/09/towards-automated-dynamic-analysis-linux-based-embedded-firmware.pdf) · [Code](https://github.com/firmadyne/firmadyne) · [Full entry & citation](https://awesomerea.org/papers/paper-firmadyne/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The work targets Linux-based firmware on little-endian ARM and little- and big-endian MIPS, which made up 90.8% of the dataset; x86, VxWorks and other real-time operating systems are outside the system. Its pre-built kernels do not load vendor out-of-tree kernel modules, so vendor kernels and modules cannot be checked, and instrumented emulation is not identical device behavior. The emulation funnel narrows sharply: of 8,591 images that initially emulated, 2,797 had a network configuration inferred and 1,971 answered ping. NVRAM semantics, interface naming and a single emulated Ethernet device on ARM are among the reported causes. WAN and LAN ports are not distinguished, so remote exploitability is not established, and results count firmware images rather than unique products and are skewed by vendor composition. FirmAE, already in this bibliography, extends Firmadyne to address such emulation failures; these 2016 rates are not current emulation figures.

  **Authors:** Daming D. Chen et al.

  </details>

<a id="papers-protocol-analysis"></a>
### Protocol inference and analysis

[↑ Paper topics](#papers) · [Contents](#contents)

- [**ICEPRE: ICS Protocol Reverse Engineering via Data-Driven Concolic Execution**](https://dl.acm.org/doi/10.1145/3728982)

  Infers message-field boundaries by following concrete message-guided paths through binary protocol parsers, then symbolically replaying them to extract byte-level data flow. It merges bytes using value-preserving operations and similar processing traces. For the 1,000-message datasets of four public ICS protocols, the authors report average boundary F1 of 0.76 and field perfection of 0.67.

  Proceedings of the ACM on Software Engineering (ISSTA 2025) · Journal article · [PDF](https://dl.acm.org/doi/pdf/10.1145/3728982) · [Code](https://github.com/QYbPtqyb/ICEPRE) · [Full entry & citation](https://awesomerea.org/papers/paper-icepre/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Recovers message syntax, not field semantics, protocol state machines or endpoint equivalence. It needs the binary, loader configuration and correctly identified initialization, input and parsing functions; manual filtering remains necessary, especially without symbols. Encrypted protocols and bit-level fields are unsupported, and ignored or only copied bytes can be merged incorrectly. Perfection measures fields with both boundaries correct. Quantitative tests use four public protocols with 50- and 1,000-message sets; separate proprietary studies cover three protocols in five firmware targets, with interaction checks on three devices and manually established ground truth. Those checks do not demonstrate complete device behavior.

  **Authors:** Yibo Qu et al.

  </details>

- [**BinPRE: Enhancing Field Inference in Binary Analysis Based Protocol Reverse Engineering**](https://dl.acm.org/doi/10.1145/3658644.3690299)

  Infers protocol-message field boundaries and semantics from instrumented server binaries and input messages. BinPRE groups bytes by the instruction operators that process them, applies detectors for field types and functions, then refines results across similar messages. On eight protocols with 50 messages each, the authors report average field perfection of 0.73 and type/function F1 scores of 0.74/0.81.

  ACM CCS 2024 · Conference paper · [PDF](https://tingsu.github.io/files/ccs24-BinPRE.pdf) · [Code](https://github.com/ecnusse/BinPRE) · [Full entry & citation](https://awesomerea.org/papers/paper-binpre/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** This is field inference, not recovery of a protocol state machine or complete endpoint behavior. It requires an accessible, instrumentable implementation and runtime message processing; passive captures alone are insufficient. Perfection counts exactly segmented fields against all true fields, not fully recovered protocols. The detector library covers five semantic types and six functions. Byte-level taint cannot accurately resolve bit flags, and unexercised behavior is not established. Ground truth uses Wireshark dissectors and specifications; three binary-analysis baselines were author reimplementations. Reported fuzzing improvements are a downstream evaluation, not proof of implementation equivalence.

  **Authors:** Jiayi Jiang et al.

  </details>

- [**DynPRE: Protocol Reverse Engineering via Dynamic Inference**](https://www.ndss-symposium.org/ndss-paper/dynpre-protocol-reverse-engineering-via-dynamic-inference/)

  DynPRE starts from captured client–server traces and then interacts with a live protocol server to infer message formats and types. It detects session-specific identifiers such as cookies and rewrites them on the fly so that replayed requests stay valid. It then sends byte-level probe requests whose responses serve as semantic feedback for field identification, aligns the responses, and applies a request–response mapping refinement that also recognizes message types. On 12 protocols with 10-, 100- and 1,000-message datasets, the authors report average field perfection of 0.50 and message-type V-measure of 0.94, against 0.15–0.31 perfection for Netzob, NetPlier, FieldHunter, BinaryInferno and NEMESYS.

  NDSS 2024 · Conference paper · [PDF](https://www.ndss-symposium.org/wp-content/uploads/2024-83-paper.pdf) · [Full entry & citation](https://awesomerea.org/papers/paper-dynpre/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** The method needs captured traces plus a reachable server that it can query repeatedly; it does not work from passive captures alone. Probing changes server state: each probe opens a new session, but protocols with global state, such as IoT device power state, can still degrade feedback. On the 1,000-message datasets an analysis averaged 259 minutes, 50,344 connection attempts and about 3.98 million exchanged messages, so slow or rate-limiting servers reduce efficiency. Encryption and authentication were disabled in the open-source evaluation setups, and encrypted traffic in the IoT case studies was decrypted with device private keys. Checksummed protocols need an added checksum-reversal step, shown only on ICMP. Format ground truth comes from tshark dissectors, and message types from manual reading of protocol documents. The five-device IoT case studies test whether generated messages trigger device behaviors, not whether specifications are complete. State-machine inference reuses existing methods and is not evaluated as a contribution.

  **Authors:** Zhengxiong Luo et al.

  </details>

- [**Lifting Network Protocol Implementation to Precise Format Specification with Security Applications**](https://dl.acm.org/doi/10.1145/3576915.3616614)

  NetLifter statically lifts source-available C protocol parsers into BNF-style message grammars and first-order constraints between packet fields. It analyzes annotated LLVM bitcode using abstract format graphs, localized path-sensitive analysis, unfolding and reordering. The resulting field boundaries, constraints and names can support packet generation and parser construction.

  ACM CCS 2023 · Conference paper · [PDF](https://qingkaishi.github.io/public_pdfs/CCS23.pdf) · [Code](https://github.com/qingkaishi/netlifter) · [Full entry & citation](https://awesomerea.org/papers/paper-netlifter/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Requires source/LLVM IR and packet-buffer/length annotations; it is not closed-binary or traffic-only recovery. The paper targets common top-down C parsers and does not support C++, inline assembly or libraries without available code. Pointer/loop analysis remains approximate; checksum fields can be identified while some checksum constraints are omitted, and fields ignored by an implementation may be missed. Precision/recall was manually checked on ten selected protocols. The reported fuzzing evaluation used three-hour runs repeated twenty times and bypassed checksum checks. It infers formats, not protocol state machines or proof of implementation equivalence.

  **Authors:** Qingkai Shi et al.

  </details>

- [**BinaryInferno: A Semantic-Driven Approach to Field Inference for Binary Message Formats**](https://www.ndss-symposium.org/ndss-paper/binaryinferno-a-semantic-driven-approach-to-field-inference-for-binary-message-formats/)

  Infers partial binary-message formats from static message samples without instrumenting an executable. Specialized detectors recognize floats, timestamps, lengths, entropy boundaries and serialization patterns; a graph-based integration step reconciles their descriptions. Across samples from ten protocols, the authors report top-level field-boundary precision of 0.69, recall of 0.73 and false-positive rate of 0.04 for the 1,000-message setting without analyst priors.

  NDSS 2023 · Conference paper · [PDF](https://www.ndss-symposium.org/wp-content/uploads/2023/02/ndss2023_s131_paper.pdf) · [Code](https://github.com/binaryinferno/binaryinferno) · [Full entry & citation](https://awesomerea.org/papers/paper-binaryinferno/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Assumes error-free, uncompressed, unencrypted, byte-aligned data and infers common fields or payload regions beginning at consistent offsets. It leaves optional/union fields and unsupported serialization patterns unresolved; sample diversity matters. The 26 encapsulated-payload test sets were pre-grouped using ground-truth message types, not discovered automatically. Ground truth merges adjacent fields that are constant across the sample; empty inference results are excluded from reported averages where stated. BI+ additionally uses supplied endianness and capture-time ranges. These are field-boundary results, not complete semantic recovery, protocol-state inference or behavioral equivalence.

  **Authors:** Jared Chandler et al.

  </details>

- [**The Closer You Look, The More You Learn: A Grey-box Approach to Protocol State Machine Learning**](https://doi.org/10.1145/3548606.3559365)

  StateInspector learns protocol Mealy machines by combining active message queries with snapshots of runtime memory, without requiring the target’s source code. It identifies candidate state-defining heap locations and uses taint and concolic analysis to merge states, evaluated by the authors on TLS 1.2 and WPA/2 implementations.

  ACM CCS 2022 · Conference paper · [PDF](https://tomchothia.gitlab.io/Papers/greyboxstatelearning_ccs2022.pdf) · [Code](https://github.com/ChrisMcMStone/state-inspector) · [Full entry & citation](https://awesomerea.org/papers/paper-stateinspector/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Assumes a finite Mealy-machine abstraction, a known input alphabet that can reach the relevant states, and state-defining memory on the heap exercised by bootstrap queries. State merging depends on configured search-depth and symbolic look-ahead bounds. Missing inputs or state stored elsewhere can leave behavior unmodeled; malformed harness messages, response abstraction and timeouts can create misleading transitions. Learned models and bounded checks do not establish full implementation equivalence, recover unknown message formats or reconstruct an application’s source code.

  **Authors:** Chris McMahon Stone et al.

  </details>

- [**Fingerprinting and analysis of Bluetooth devices with automata learning**](https://doi.org/10.1007/s10703-023-00425-y)

  Learns Mealy-machine models of Bluetooth Low Energy implementations on physical peripherals by active automata learning. An nRF52840 central running SweynTooth-derived firmware sends abstract BLE inputs, with error handling, repeated queries and caching for lost packets and non-deterministic replies. The authors learn connection-procedure models of six devices and legacy-pairing models of three, and use model differences to fingerprint their SoCs.

  Formal Methods in System Design 2022 · Journal article · [PDF](https://arxiv.org/pdf/2211.16074v2) · [Code](https://github.com/apferscher/ble-learning) · [Full entry & citation](https://awesomerea.org/papers/paper-ble-automata-learning/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Models are bounded by the chosen abstract alphabet and cover only connection and legacy pairing; message formats are not inferred, and secure pairing is left to future work. Equivalence was approximated with a small number of conformance tests per state, so models are hypotheses, not proofs. One SoC was learnable only with reduced alphabets, two were learned from an already-connected state, and some pairing runs needed manual hard resets. The fingerprinting sequence holds only for the tested SoCs. Apart from one crashing input sequence, the authors report no security vulnerabilities in the learned models.

  **Authors:** Andrea Pferscher et al.

  </details>

- [**NetPlier: Probabilistic Network Protocol Reverse Engineering from Message Traces**](https://www.ndss-symposium.org/ndss-paper/netplier-probabilistic-network-protocol-reverse-engineering-from-message-traces/)

  Uses multiple sequence alignment and probabilistic keyword-field inference to cluster network messages by type, evaluated across ten protocols with downstream format and state-machine analysis.

  NDSS 2021 · Conference paper · [PDF](https://www.ndss-symposium.org/wp-content/uploads/ndss2021_4A-5_24531_paper.pdf) · [Code](https://github.com/yapengye/NetPlier) · [Full entry & citation](https://awesomerea.org/papers/paper-netplier/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Requires unencrypted traces and cannot recover unseen message types. Larger alignments, sub-byte keywords and one-way traffic can reduce accuracy. Format/FSM inference is downstream evaluation rather than the main contribution; state semantics in a case study were manually annotated. These models do not establish complete application/device reconstruction.

  **Authors:** Yapeng Ye et al.

  </details>

- [**Automatic Wireless Protocol Reverse Engineering**](https://www.usenix.org/conference/woot19/presentation/pohl)

  Infers message formats of proprietary wireless protocols from demodulated physical-layer captures: it aligns messages by preamble and sync word, then uses RSSI and dedicated engines to label length, address, sequence-number and checksum fields, optionally using known addresses or field positions.

  13th USENIX Workshop on Offensive Technologies (WOOT 19) 2019 · Conference paper · [PDF](https://www.usenix.org/system/files/woot19-paper_pohl.pdf) · [Code](https://github.com/jopohl/urh) · [Full entry & citation](https://awesomerea.org/papers/paper-wireless-protocol-re/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Only message formats are inferred: preamble, sync, length, address, sequence number and checksum. State-machine inference and payload fields, such as an on/off bit, are out of scope. The method assumes length-efficient binary messages with one preamble and sync word each. Accuracy is measured on 8 generated protocols; 3 real smart-home captures (EnOcean, Homematic BidCoS and an eQ-3 protocol used by RWE Smarthome) serve for performance tests, which the authors call a limited test set.

  **Authors:** Johannes Pohl et al.

  </details>

- [**NEMESYS: Network Message Syntax Reverse Engineering by Analysis of the Intrinsic Structure of Individual Messages**](https://www.usenix.org/conference/woot18/presentation/kleber)

  Infers approximate field boundaries within individual binary-protocol messages from changes in bit congruence, and introduces Format Match Score to compare inferred segmentation with known protocol dissectors.

  12th USENIX Workshop on Offensive Technologies (WOOT 18) 2018 · Conference paper · [PDF](https://www.usenix.org/system/files/conference/woot18/woot18-paper-kleber.pdf) · [Code](https://github.com/vs-uulm/nemesys) · [Full entry & citation](https://awesomerea.org/papers/paper-nemesys/)

  <details>
  <summary>Scope and publication details</summary>

  **Scope and limits:** Requires plaintext payloads. Evaluation covers DNS, DHCP and NTP with protocol-tuned parameters. Single-byte fields are not inferred; zero-filled fields, character sequences and pseudo-random values can cause errors. FMS needs known field boundaries for validation. The output is approximate segmentation, not field semantics, a state machine or complete application/device behavior.

  **Authors:** Stephan Kleber et al.

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
