[![Awesome Reverse Engineering Anything — understand software, build from evidence](assets/readme-banner.svg)](https://awesomerea.org)

# Awesome Reverse Engineering Anything

**A practical field guide to agent-assisted reverse engineering: choose a tool, trace a behavior, and keep the evidence.**

[![Catalog checks](https://github.com/reacher-z/Awesome-REA/actions/workflows/validate.yml/badge.svg)](https://github.com/reacher-z/Awesome-REA/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

English · [简体中文](README.zh-CN.md)

**[Explore AwesomeREA.org](https://awesomerea.org)** — browse Website, Game, App, Binary, and Firmware resources.

**81 curated resources · [1,600 scanned repository READMEs](https://awesomerea.org/?view=source-index#catalog) · 7 task workflows.** The broader source index is automatically scanned and kept separate from the curated collection. [Scan method and receipt](docs/source-scan.md).

Start with [REA — Reverse Engineer Anything](https://github.com/morluto/rea), explore independent agent integrations, or follow a focused workflow below. This is an independent community collection. Each catalog record includes its original source, requirements, relationship to REA, and review date.

**[Try the included lab](labs/electron-notes/README.md) · [Choose a workflow](docs/playbooks.md) · [Search the catalog](#search-the-catalog) · [Contribute](CONTRIBUTING.md)**

## Start with your target

| I want to understand… | Start here | What to produce |
| --- | --- | --- |
| **Website** — a browser interaction or request | [Official browser guide](https://rea.tools/guides/browser/) | An observed action, captured request, and corresponding script |
| **Game** — a calculation, asset format, or frame | [Game workflow](docs/playbooks.md#game-behavior) | A bounded behavior or rendering explanation with evidence |
| **App** — an Electron feature or IPC path | [Notes export lab](labs/electron-notes/README.md), then [official JavaScript guide](https://rea.tools/guides/javascript/) | Renderer → preload → IPC → main-process trace, with file locations |
| One function in a native binary | [Native investigation workflow](docs/playbooks.md#native-function-recovery) | Pseudocode, instruction evidence, and a small behavioral test |
| An Android APK | [Android workflow](docs/playbooks.md#android-apk) | Manifest facts and a class/method trace |
| A .NET assembly | [Managed-code workflow](docs/playbooks.md#dotnet-assembly) | Type/member inventory and CIL-backed explanation |
| Saved HTTP traffic | [Capture workflow](docs/playbooks.md#saved-network-capture) | A request sequence with capture entry references |
| A firmware image | [Firmware workflow](docs/playbooks.md#firmware-image) | Region inventory and a bounded extraction map |
| Which agent integration to use | [Agent tools in the catalog](#resource-catalog) | A choice based on engine, platform, license, and task |

## Run your first investigation

Our original [Electron-shaped Notes fixture](labs/electron-notes/README.md) is small enough to read in one sitting. Inspect the export path, then check the fixture's CSV behavior against three executable tests. No application download or commercial decompiler is needed for this static lab.

```sh
git clone https://github.com/reacher-z/Awesome-REA.git
cd Awesome-REA
node --test labs/electron-notes/app/csv.test.cjs
mkdir -p labs/electron-notes/output
npx -y rea-agents@6.5.0 analyze-javascript-application "$PWD/labs/electron-notes/app" --json > labs/electron-notes/output/rea-evidence.json
python3 scripts/verify_evidence.py labs/electron-notes/output/rea-evidence.json
```

The pinned REA release requires Node.js `^22.19.0`, `^24.11.0`, or `>=26.0.0`. The first `npx` invocation downloads REA and its dependencies. See the [lab walkthrough and recorded result](labs/electron-notes/README.md) for exactly what was verified.

To connect REA to an agent, use the separate [official installation guide](https://github.com/morluto/rea/blob/main/docs/installation.md). The command above performs a local static analysis and does not configure your agent.

## Search the catalog

Python 3.10+; standard library only:

```sh
python3 scripts/catalog.py electron
python3 scripts/catalog.py --target game
python3 scripts/catalog.py ghidra --language zh
python3 scripts/catalog.py --relationship independent-agent-integration
python3 scripts/catalog.py --list-categories
python3 scripts/catalog.py android --json
python3 scripts/catalog.py ghidra --source-index
```

The [JSON catalog](data/README.md) is the source of truth. It is also usable by an agent without installing a skill or MCP server.

## How to read the collection

- **Official REA** links document upstream capabilities and prerequisites.
- **Community REA** links describe projects or case studies that explicitly use REA; they may combine other tools.
- **Independent integrations** connect agents to their own tools. Listing them does not imply REA integration.
- **Foundation tools** and **learning resources** are selected companions for reverse engineering.

`source-reviewed` means the linked upstream documentation was inspected. It does not mean the software was installed, audited, or tested on every platform. Runtime verification is recorded separately in the lab. Star counts are not an inclusion requirement.

## Resource catalog

<!-- BEGIN GENERATED CATALOG -->
81 resources, grouped by task. These are resource entries, not a count of independent projects.

Each entry links its primary evidence and source-review date. Source review is not runtime verification; full records are in the [JSON catalog](data/README.md).

REA resources are open below. Expand an independent tool family for its entries, prerequisites, and sources, or [search every record](#search-the-catalog).

### Official REA: core and setup

- **[REA — Reverse Engineer Anything](https://github.com/morluto/rea)** — The upstream CLI and MCP server for evidence-based investigations of shipped software and runtime behavior.

  Official REA project · Website / Game / App / Binary / Firmware · [Source](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: rea-agents 6.5.0 was the published npm version at review time. Node.js ^22.19.0 || ^24.11.0 || &gt;=26.0.0; additional tools depend on the target.

- **[Official reverse-engineer-anything skill](https://github.com/morluto/rea/tree/main/.agents/skills/reverse-engineer-anything)** — Target routing, connection recovery and evidence practices for agents using REA.

  Official REA skill · Website / Game / App / Binary / Firmware · [Source](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/.agents/skills/reverse-engineer-anything/SKILL.md) · Source reviewed 2026-10-15.
  Requirements and limits: Installing the skill provides instructions; it does not by itself register MCP or install analysis engines. Use the connected server's actual tool schemas; repository main may be ahead of an installed release.

- **[Installation and client setup](https://github.com/morluto/rea/blob/main/docs/installation.md)** — Reviewed setup plans, client registration, provider prerequisites and scoped readiness checks.

  Official REA documentation · Website / Game / App / Binary / Firmware · [Source](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/docs/installation.md) · Source reviewed 2026-10-15.
  Requirements and limits: Supported Node.js and npm. Setup previews client configuration changes; native engines have separate prerequisites.

- **[CLI and Evidence](https://github.com/morluto/rea/blob/main/docs/cli.md)** — CLI workflows for saving Evidence and projecting smaller views from completed analysis.

  Official REA documentation · Website / Game / App / Binary / Firmware · [Source](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/docs/cli.md) · Source reviewed 2026-10-15.
  Requirements and limits: Installed REA CLI or an explicitly pinned package runner. CLI processes are separate; retain result files for later operations.

- **[MCP contracts and generated catalog](https://github.com/morluto/rea/blob/main/docs/mcp-contracts.md#generated-catalog)** — Canonical tool contracts, provider discovery and Evidence semantics for integration authors.

  Official REA documentation · Website / Game / App / Binary / Firmware · [Source](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/docs/mcp-contracts.md) · Source reviewed 2026-10-15.
  Requirements and limits: A compatible MCP client for live use. Discover the live catalog before relying on tools documented on main.


### Official REA: investigation guides

- **[Native binary investigation](https://github.com/morluto/rea/blob/main/docs/native-investigation.md)** — Locate a function, inspect instructions and pseudocode, and follow references with a selected native provider.

  Official REA documentation · Binary / Game · [Source](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/docs/native-investigation.md) · Source reviewed 2026-10-15.
  Requirements and limits: A target binary and a configured supported provider such as Ghidra, Hopper or IDA. Host, architecture and provider support are scoped separately; pseudocode is not original source.

- **[Cross-layer JavaScript application workflows](https://github.com/morluto/rea/blob/main/docs/javascript-application-workflows.md)** — Trace features and compare authenticated JavaScript application graphs while preserving static-analysis limits.

  Official REA documentation · Website / App · [Source](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/docs/javascript-application-workflows.md) · Source reviewed 2026-10-15.
  Requirements and limits: Evidence from analyze_javascript_application or supported runtime reconciliation. No native engine is required for the static JavaScript path; keep the complete parent Evidence.

- **[Static Android APK analysis](https://github.com/morluto/rea/blob/main/docs/android-analysis.md)** — Inspect Android package identity, classes, methods and references through REA's JADX integration.

  Official REA documentation · App · [Source](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/docs/android-analysis.md) · Source reviewed 2026-10-15.
  Requirements and limits: Full JDK 17 or newer and caller-supplied jadx-headless-mcp 0.7.1 with the documented digest check. Linux requires a procps-compatible ps for provider process ownership.

- **[Managed-code analysis](https://github.com/morluto/rea/blob/main/docs/managed-code-analysis.md)** — Read PE/CLI metadata and CIL, compare managed members and inspect declared native boundaries without loading the assembly.

  Official REA documentation · App · [Source](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/docs/managed-code-analysis.md) · Source reviewed 2026-10-15.
  Requirements and limits: A supported PE/CLI assembly; no native engine is required for metadata/CIL inspection. NativeAOT, IL2CPP and packaged single-file deployments have different boundaries.

- **[Historical web network captures](https://github.com/morluto/rea/blob/main/docs/web-network-captures.md)** — Inspect saved web captures offline; recorded URLs are not fetched and no proxy is started.

  Official REA documentation · Website / App · [Source](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/docs/web-network-captures.md) · Source reviewed 2026-10-15.
  Requirements and limits: A supported existing capture and an explicit format selection. PCAP/TShark workflows are separate and have different host/tool requirements.

- **[Firmware analysis](https://github.com/morluto/rea/blob/main/docs/firmware-analysis.md)** — Inspect firmware regions with Binwalk and explicitly extract with Unblob, retaining tool and artifact identity.

  Official REA documentation · Firmware · [Source](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/docs/firmware-analysis.md) · Source reviewed 2026-10-15.
  Requirements and limits: Caller-supplied Binwalk 3.1.x for inspection; Unblob 26.6.x for extraction. The documented verification scope is Linux x64; extraction needs a new caller-selected output directory.

- **[Browser observation guide](https://rea.tools/guides/browser/)** — Follow a user-triggered export request in the supplied Notes browser example and connect it to the downloaded result.

  Official REA guide · Website · [Source](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/website/evidence/guide-examples.md) · Source reviewed 2026-10-15.
  Requirements and limits: A user-owned Chrome-family browser, loopback CDP connection and explicitly allowed origins. The recorded upstream example used a separate controller to click; REA did not perform the click.

- **[JavaScript and Electron: follow a CSV export](https://rea.tools/guides/javascript/)** — A source-owned Notes fixture teaches the renderer, preload, IPC and CSV path with linked analysis evidence.

  Official REA guide · App · [Source](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/website/evidence/guide-examples.md) · Source reviewed 2026-10-15.
  Requirements and limits: Supported Node.js and REA; no native engine is required for this static fixture. The fixture is source-owned teaching material, not an installed Electron distribution; static findings do not prove execution.


### Official REA: case studies

- **[Aegis: trace a login-code calculation](https://rea.tools/showcase/aegis/)** — An official APK investigation follows TOTP methods in Aegis and publishes artifact identities and selected Evidence.

  Official REA case study · App · [Source](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/website/evidence/aegis-login-code.md) · Source reviewed 2026-10-15.
  Requirements and limits: Upstream case: Aegis 3.4.3, REA 6.1.0, jadx-headless-mcp 0.7.1 and OpenJDK 21 on Linux x64. Use the matching official APK for reproduction; this listing did not rerun the case.

- **[DownUnderCTF: masked-squares flag checker](https://rea.tools/showcase/ctf/)** — An official educational challenge investigation connects binary checks to equations and records an original-program validation.

  Official REA case study · Binary · [Source](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/website/evidence/ctf-masked-squares.md) · Source reviewed 2026-10-15.
  Requirements and limits: Upstream case: public DownUnderCTF 2023 challenge, REA 4.1.0 and Ghidra 12.1.4 on Linux x64. Target hash and source revision are documented; author-reported execution was not repeated here.

- **[DX-Ball: reconstruct sound panning](https://rea.tools/showcase/dx-ball/)** — Recover one sound-pan function from instructions and constants; upstream cites 3,205 cases and a 63-byte match.

  Official REA case study · Game / Binary · [Source](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/website/evidence/dx-ball-sound-pan.md) · Source reviewed 2026-10-15.
  Requirements and limits: The matching DX-Ball 1.07 executable and the documented native-analysis environment. The cited reconstruction checks concern one function, not full-game equivalence; no checks were rerun here.

- **[Notion: trace the clipboard bridge](https://rea.tools/showcase/notion/)** — Trace a packaged Electron clipboard path using REA findings and separate source inspection; the dynamic wrapper remains a stated limit.

  Official REA case study · App · [Source](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/website/evidence/notion-clipboard.md) · Source reviewed 2026-10-15.
  Requirements and limits: Upstream case uses Notion Desktop 7.6.1 packaged JavaScript and REA 4.1.0. The full clipboard route was not automatically paired or observed as a desktop execution.

- **[TH04: recover a DOS bullet-ring helper](https://rea.tools/showcase/th04/)** — Inspect a 16-bit PC-98 DOS helper and relate its angle calculation to a pinned reconstruction and historical compiler checks.

  Official REA case study · Game / Binary · [Source](https://github.com/morluto/rea/blob/808339f0b1cf3837445f392b5d5f1f362d64a27d/website/evidence/th04-bullet-ring.md) · Source reviewed 2026-10-15.
  Requirements and limits: The matching original TH04 MAIN.EXE and the documented Ghidra DOS load profile. The showcase covers one helper; full-game reconstruction claims are outside its scope.


### Community REA integrations

- **[dsh-mcp-rea](https://github.com/Ersith/dsh-mcp-rea)** — A community MCP bridge presents a smaller selected tool surface and forwards explicit commands to the REA CLI.

  Community REA integration · Website / Game / App / Binary / Firmware · [Source](https://github.com/Ersith/dsh-mcp-rea/blob/main/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: Requires REA and the relevant analysis providers; distributed as a local bundle rather than a public npm package. Use the documented REA_ENTRY mode for direct execution; PATH fallback invokes a shell. Its README's provider/platform claims may lag upstream; no installation or security audit was performed.

- **[rea-jev](https://github.com/juan-viox/rea-jev)** — A Claude Code plugin adds Jev-based routing and evidence checks around a pinned REA MCP integration.

  Community REA integration · App / Website · [Source](https://github.com/juan-viox/rea-jev/blob/main/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: Claude Code, supported Node.js and the plugin's documented macOS/Linux environment. Optional Jev service credentials enable external model calls; excerpts may be sent to that service. Hooks fail open on provider failure; they are not a security guarantee.

- **[rea-casebook](https://github.com/pablodiazjorge/rea-casebook)** — A Claude Code mod collects received REA Evidence, tracks unknowns and records findings that cite delivered evidence IDs.

  Community REA integration · Binary · [Source](https://github.com/pablodiazjorge/rea-casebook/blob/main/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: README requires Claude Code 2.1.296 or newer and an MCP server registered under the name rea. Developed with REA 6.4.0 and Ghidra 12.1 on Windows; broader behavior was not tested here. Evidence IDs being present does not itself prove a conclusion is correct.


### Community REA labs

- **[rea-playbook](https://github.com/jinshi666888/rea-playbook)** — An Electron practice target, Evidence extractor and MCP probe; offline fixture mode is distinguished from real REA analysis.

  Community REA learning resource · Binary · [Source](https://github.com/jinshi666888/rea-playbook/blob/main/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: README pins the real-analysis path to rea-agents 6.3.0 and lists supported Node.js versions. The offline demo reads bundled results without running REA; its tests were not rerun here.

- **[rea-lab](https://github.com/pablodiazjorge/rea-lab)** — A Windows REA/Ghidra lab with seeded challenges, published studies, upstream contributions and recorded limitations.

  Community REA learning resource · Binary · [Source](https://github.com/pablodiazjorge/rea-lab/blob/main/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: The documented environment uses Windows 11, REA 6.4.0 and Ghidra 12.1.4. Study results are author-reported and task/model-specific, not independently reproduced by this index. Code and documentation use different licenses; inspect the relevant repository notices.


### Community REA investigations

- **[PicoPrint: LX-D02 printer investigation](https://github.com/bigtower17/picoprint)** — The author describes REA-assisted Android investigation followed by separate Hermes decompilation to support a Windows BLE printer.

  Author-reported mixed workflow · App / Firmware · [Source](https://github.com/morluto/rea/discussions/4152) · Source reviewed 2026-10-15.
  Requirements and limits: Project README lists Windows 10/11, Bluetooth LE, an LX-D02 printer and Go 1.25+ to build. REA's stated role was readiness/device discovery and investigation framing; hermes-dec handled Hermes v98. Hardware behavior and author-reported results were not reproduced here.


### Independent MCP integrations

<details>
<summary>Browse 13 resources</summary>

- **[Hex-Rays IDA MCP](https://github.com/HexRaysSA/ida-mcp)** — Official Hex-Rays MCP server for agent access to IDA databases, with headless operation and optional GUI integration.

  Independent agent integration · Binary · [Source](https://github.com/HexRaysSA/ida-mcp/blob/main/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: IDA 9.4+ with idalib, Python 3.11+, Git and uv; the GUI plugin is optional for headless use.

- **[GhidraMCP](https://github.com/LaurieWired/GhidraMCP)** — Ghidra extension and MCP bridge exposing decompilation, symbol navigation and renaming to agents, with GUI and headless modes.

  Independent agent integration · Binary · [Source](https://github.com/LaurieWired/GhidraMCP/blob/main/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: Match the extension to the documented Ghidra release; Python 3.10+ for the bridge, with additional PyGhidra requirements for headless mode.

- **[Binary Ninja MCP (official)](https://dev-docs.binary.ninja/guide/mcp.html)** — Binary Ninja's own MCP interface exposes functions, symbols, disassembly, intermediate languages and decompiled text to agents.

  Independent agent integration · Binary · [Source](https://dev-docs.binary.ninja/guide/mcp.html) · Source reviewed 2026-10-15.
  Requirements and limits: Reviewed in the development manual: use a build containing MCP. GUI server uses HTTP; headless stdio requires Commercial or Ultimate on macOS/Linux.

- **[Binary Ninja MCP (fosdickio)](https://github.com/fosdickio/binary_ninja_mcp)** — Community Binary Ninja plugin and bridge for MCP clients, including workflows that switch among multiple open binaries.

  Independent agent integration · Binary · [Source](https://github.com/fosdickio/binary_ninja_mcp/blob/main/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: Binary Ninja, Python 3.12+ and an MCP client; install the plugin separately from the client bridge.

- **[IDA Pro MCP (mrexodia)](https://github.com/mrexodia/ida-pro-mcp)** — Community IDA integration useful for existing setups and migration context; its maintainer now recommends the official Hex-Rays MCP server.

  Independent agent integration · Binary · [Source](https://github.com/mrexodia/ida-pro-mcp/blob/main/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: IDA Pro rather than IDA Free, Python 3.11+ and an MCP client; consult the upstream migration notice before choosing a new setup.

- **[Radare2 MCP Server](https://github.com/radareorg/radare2-mcp)** — Native radare2 MCP server offering binary-analysis tools, reusable sessions and configurable read-only access.

  Independent agent integration · Binary · [Source](https://github.com/radareorg/radare2-mcp/blob/main/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: A compatible radare2 build and r2pm, plus an MCP client; advanced HTTP session features depend on the radare2 ABI.

- **[JADX-AI-MCP](https://github.com/zinja-coder/jadx-ai-mcp)** — JADX plugin paired with a Python MCP server to inspect decompiled Android classes, resources, cross-references and debugger context.

  Independent agent integration · App · [Source](https://github.com/zinja-coder/jadx-ai-mcp/blob/jadx-ai/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: JADX with the plugin and the separate JADX MCP Server component; upstream lists Java 11+ and Python 3.10+.

- **[frida-mcp (yfe404)](https://github.com/yfe404/frida-mcp)** — Frida MCP server with persistent instrumentation sessions, runtime inspection and Android static-to-dynamic navigation.

  Independent agent integration · App / Game · [Source](https://github.com/yfe404/frida-mcp/blob/main/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: Node.js 20+, Frida 17 and an accessible target; on-device operations require the documented device/frida-server setup.

- **[Super Trouper](https://github.com/crissyfield/super-trouper)** — Single-binary Frida MCP server for discovering devices, managing process sessions and loading instrumentation scripts.

  Independent agent integration · App / Game · [Source](https://github.com/crissyfield/super-trouper/blob/main/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: Published host binaries target macOS/Linux; target connectivity must support Frida. Source builds need Go, CGO and a matching Frida Core DevKit.

- **[LLDB MCP](https://lldb.llvm.org/use/mcp.html)** — LLDB's official MCP interface gives agents debugger sessions and commands for breakpoints, memory inspection and stepping.

  Independent agent integration · Binary / App · [Source](https://lldb.llvm.org/use/mcp.html) · Source reviewed 2026-10-15.
  Requirements and limits: An LLDB distribution/build containing lldb-mcp and a compatible stdio MCP client; debug-target access follows the host platform's requirements.

- **[RenderDoc MCP](https://github.com/scarletfantasy/renderdoc-mcp)** — Expose existing RenderDoc captures to an agent for bounded frame, pipeline, resource, and shader inspection.

  Independent agent integration · Game / App · [Source](https://github.com/scarletfantasy/renderdoc-mcp/blob/main/README.md) · Source reviewed 2026-10-16T01:05:01Z.
  Requirements and limits: Windows and replayable .rdc capture; maintainer baseline is RenderDoc 1.43. Optional native Python backend needs a source-built binding.

- **[Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp)** — Connect an agent to Chrome for live page inspection, network debugging, and performance traces.

  Independent agent integration · Website · [Source](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/README.md) · Source reviewed 2026-10-16T01:05:01Z.
  Requirements and limits: Supported Node.js LTS, Chrome, and an MCP client; selected browser profile and target must be available locally.

- **[Playwright MCP](https://github.com/microsoft/playwright-mcp)** — Drive browser interactions through structured accessibility snapshots to investigate reproducible web behavior.

  Independent agent integration · Website · [Source](https://github.com/microsoft/playwright-mcp/blob/main/README.md) · Source reviewed 2026-10-16T01:05:01Z.
  Requirements and limits: Node.js 18+ and an MCP client; the upstream also offers a separate CLI-and-skills approach for coding agents.

</details>


### Independent agent workflows

<details>
<summary>Browse 5 resources</summary>

- **[r2ai](https://github.com/radareorg/r2ai)** — AI plugins inside radare2 for function explanations, naming suggestions and model-assisted decompilation using local or remote models.

  Independent agent integration · Binary · [Source](https://github.com/radareorg/r2ai/blob/master/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: radare2 with the matching r2ai/decai plugins; configure a local model or the credentials required by the selected remote provider.

- **[DAILA](https://github.com/mahaloz/DAILA)** — Decompiler-independent AI assistant for function summaries and naming across IDA, Ghidra, Binary Ninja and angr-management.

  Independent agent integration · Binary · [Source](https://github.com/mahaloz/DAILA/blob/main/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: A supported decompiler and dailalib; configure a model backend. Ghidra requires the documented PyGhidra setup.

- **[RevEng.AI Ghidra Plugin](https://github.com/RevEngAI/plugin-ghidra)** — Connects Ghidra to RevEng.AI for function similarity, recovered names, AI explanations and agent-assisted annotation.

  Independent agent integration · Binary · [Source](https://github.com/RevEngAI/plugin-ghidra/blob/main/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: A compatible Ghidra/Java build and a RevEng.AI API key; creating service-side analysis uploads the selected binary.

- **[Claude Reverse Engineering Skill](https://github.com/EncidXVII/claude-reverse-engineering-skill)** — Community agent skill for triage, headless exports and evidence-based RE reports; explicitly documents workflows with REA and other MCP servers.

  Independent agent integration · App / Binary · [Source](https://github.com/EncidXVII/claude-reverse-engineering-skill/blob/main/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: An Agent Skills-compatible client and Python 3.8+ for bundled scripts; analysis engines and MCP servers are configured separately.

- **[SpecterOps Reverse Engineering Skills](https://github.com/SpecterOps/skills/tree/main/plugins/reverse-engineering)** — Focused Binary Ninja and Ghidra analysis skills that describe MCP tool use, analysis recipes and annotation practices.

  Independent agent integration · Binary · [Source](https://github.com/SpecterOps/skills/blob/main/plugins/reverse-engineering/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: Configure the chosen Binary Ninja or Ghidra MCP integration separately; the skill package does not install or wrap those servers.

</details>


### Game analysis tools

<details>
<summary>Browse 4 resources</summary>

- **[RenderDoc](https://github.com/baldurk/renderdoc)** — Inspect frame captures, draw calls, shaders, and graphics resources in your own game or graphics application.

  Foundation tool · Game / App · [Source](https://github.com/baldurk/renderdoc/blob/v1.x/README.md) · Source reviewed 2026-10-16T01:05:01Z.
  Requirements and limits: Supported graphics API and replay platform; upstream supports captures of your own, open-source, or free projects. Metal is not supported.

- **[AssetRipper](https://github.com/AssetRipper/AssetRipper)** — Analyze Unity game files, inspect asset dependencies, and convert supported assets into Unity project formats.

  Foundation tool · Game · [Source](https://github.com/AssetRipper/AssetRipper/blob/master/README.md) · Source reviewed 2026-10-16T01:05:01Z.
  Requirements and limits: Unity 3.5.0–6000.4.X coverage varies by version; GPL-3.0 open-source edition, with separate premium features.

- **[Cpp2IL](https://github.com/SamboyCoding/Cpp2IL)** — Recover managed representations from Unity IL2CPP builds using binary and metadata analysis; reconstruction remains a work in progress.

  Foundation tool · Game / App / Binary · [Source](https://github.com/SamboyCoding/Cpp2IL/blob/development/README.md) · Source reviewed 2026-10-16T01:05:01Z.
  Requirements and limits: Compatible Unity build and metadata; current development branch is a major rewrite and primarily targets .NET 9.0.

- **[Il2CppDumper](https://github.com/Perfare/Il2CppDumper)** — Recover IL2CPP metadata and dummy assemblies, and generate helper scripts for native analysis tools; method code is not restored.

  Foundation tool · Game / App / Binary · [Source](https://github.com/Perfare/Il2CppDumper/blob/master/README.md) · Source reviewed 2026-10-16T01:05:01Z.
  Requirements and limits: Matching IL2CPP executable and global-metadata.dat; documented Unity support is 5.3–2022.2.

</details>


### Website analysis tools

<details>
<summary>Browse 1 resources</summary>

- **[mitmproxy](https://github.com/mitmproxy/mitmproxy)** — Inspect and record HTTP traffic with an interactive proxy, web interface, or scriptable command-line tools.

  Foundation tool · Website / App · [Source](https://github.com/mitmproxy/mitmproxy/blob/main/README.md) · Source reviewed 2026-10-16T01:05:01Z.
  Requirements and limits: Configure the client proxy; HTTPS inspection requires the appropriate local trust configuration. Saved captures and live interception are distinct workflows.

</details>


### Native analysis tools

<details>
<summary>Browse 5 resources</summary>

- **[Ghidra](https://github.com/NationalSecurityAgency/ghidra)** — Open-source analysis suite for disassembly, decompilation, graphs and Java/Python automation across executable formats.

  Foundation tool · Binary / Game / Firmware · [Source](https://github.com/NationalSecurityAgency/ghidra/blob/master/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: An official Ghidra release and its required JDK; extension and script compatibility must match the installed release.

- **[radare2](https://github.com/radareorg/radare2)** — Scriptable command-line framework for inspecting, disassembling, debugging and modifying binaries across many architectures.

  Foundation tool · Binary / Game · [Source](https://github.com/radareorg/radare2/blob/master/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: Use the release/build for your host; decompilers and other optional functionality may require separate plugins.

- **[Cutter](https://github.com/rizinorg/cutter)** — Rizin-powered graphical reverse-engineering workspace with extensible views and Ghidra decompiler integration.

  Foundation tool · Binary / Game · [Source](https://github.com/rizinorg/cutter/blob/dev/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: Desktop builds are available for Linux, macOS and Windows; use plugins compatible with the selected Cutter release.

- **[ImHex](https://github.com/WerWolv/ImHex)** — Hex editor with a binary-pattern language, structured data inspection and visual tools for understanding file formats.

  Foundation tool · Binary / Game / Firmware · [Source](https://github.com/WerWolv/ImHex/blob/master/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: Desktop build or web edition; some data sources and features depend on the platform and selected build.

- **[Detect It Easy](https://github.com/horsicq/Detect-It-Easy)** — Format-aware file identification and static inspection using parsers, signatures and programmable heuristics.

  Foundation tool · Binary / Game · [Source](https://github.com/horsicq/Detect-It-Easy/blob/master/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: Use the project-linked DIE-engine releases for the host platform; identification results require analyst interpretation.

</details>


### Debugging and dynamic analysis

<details>
<summary>Browse 5 resources</summary>

- **[Frida](https://github.com/frida/frida)** — Dynamic instrumentation toolkit for observing and scripting the behavior of live native and managed processes.

  Foundation tool · App / Game · [Source](https://github.com/frida/frida/blob/main/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: Host bindings or CLI tools and a supported target setup; mobile/server/Gadget and signing requirements vary by platform.

- **[Qiling](https://github.com/qilingframework/qiling)** — Python emulation framework that adds OS, filesystem and API behavior around CPU emulation for instrumented binary analysis.

  Foundation tool · Binary / Firmware · [Source](https://github.com/qilingframework/qiling/blob/master/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: A supported Python environment and the target's required root filesystem/libraries; emulation coverage varies by platform.

- **[x64dbg](https://github.com/x64dbg/x64dbg)** — Windows binary debugger with disassembly, memory views and plugins for analyzing programs without source code.

  Foundation tool · Binary · [Source](https://github.com/x64dbg/x64dbg/blob/development/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: Windows; choose x32dbg or x64dbg according to the executable's architecture.

- **[GDB](https://sourceware.org/gdb/)** — Native and remote debugger for controlling execution and inspecting live or crashed program state.

  Foundation tool · Binary / Game · [Source](https://www.sourceware.org/gdb/) · Source reviewed 2026-10-15.
  Requirements and limits: A GDB build supporting the target architecture and a permitted local process, core dump, simulator or remote debug endpoint.

- **[rr](https://github.com/rr-debugger/rr)** — Records process execution and replays it under GDB, enabling repeatable inspection and reverse execution.

  Foundation tool · Binary · [Source](https://github.com/rr-debugger/rr/blob/master/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: Linux with supported CPU performance counters; VM use depends on counter virtualization and the project's hardware requirements.

</details>


### Android tools

<details>
<summary>Browse 3 resources</summary>

- **[JADX](https://github.com/skylot/jadx)** — Dex-to-Java decompiler with CLI/GUI navigation, resource decoding and cross-reference search for Android packages.

  Foundation tool · App · [Source](https://github.com/skylot/jadx/blob/master/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: 64-bit Java 11+ unless using a bundled runtime; decompilation can be incomplete and should be checked against bytecode.

- **[Apktool](https://github.com/iBotPeaches/Apktool)** — Decodes Android resources and smali into a project-like tree and can rebuild modified packages.

  Foundation tool · App · [Source](https://github.com/iBotPeaches/Apktool/blob/main/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: A supported Java runtime and the release-specific launcher; rebuilding is distinct from recovering original Java source.

- **[Androguard](https://github.com/androguard/androguard)** — Python toolkit for APK/DEX metadata, bytecode and reference analysis; the v5 source branch also documents agent skills and MCP.

  Foundation tool · App · [Source](https://github.com/androguard/androguard/blob/master/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: Version-sensitive: the reviewed README distinguishes the v5 source tree from PyPI 4.1.4; v5 extras require additional Rust/Python components.

</details>


### .NET tools

<details>
<summary>Browse 2 resources</summary>

- **[ILSpy](https://github.com/icsharpcode/ILSpy)** — .NET assembly browser and C# decompiler with whole-project export, metadata inspection and a scriptable command-line frontend.

  Foundation tool · App · [Source](https://github.com/icsharpcode/ILSpy/blob/master/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: Choose a desktop or ILSpyCmd release and its matching .NET runtime; frontend and operating-system support are release-dependent.

- **[dnSpyEx](https://github.com/dnSpyEx/dnSpy)** — Community continuation of dnSpy for debugging and editing .NET assemblies without the original source.

  Foundation tool · App · [Source](https://github.com/dnSpyEx/dnSpy/blob/master/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: Windows desktop workflow; Unity debugging requires the companion runtime setup documented by the project.

</details>


### JavaScript and Electron tools

<details>
<summary>Browse 2 resources</summary>

- **[@electron/asar](https://github.com/electron/asar)** — Electron's archive tool lists and extracts ASAR contents so packaged JavaScript and application assets can be inspected.

  Foundation tool · App / Website · [Source](https://github.com/electron/asar/blob/main/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: The reviewed release requires Node.js 22.12+; extraction reveals archive contents, not missing source maps or original source names.

- **[webcrack](https://github.com/j4k0xb/webcrack)** — Improves JavaScript readability by reversing supported obfuscation patterns and unpacking webpack/Browserify bundles.

  Foundation tool · App / Website · [Source](https://github.com/j4k0xb/webcrack/blob/master/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: The reviewed README specifies Node.js 22 or 24; results depend on the obfuscator/bundler patterns present in the input.

</details>


### WebAssembly tools

<details>
<summary>Browse 2 resources</summary>

- **[WABT](https://github.com/WebAssembly/wabt)** — WebAssembly tools for binary-to-text conversion, section inspection, validation, interpretation and C translation.

  Foundation tool · Website / Binary · [Source](https://github.com/WebAssembly/wabt/blob/main/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: Select a release supporting the module's WebAssembly features; optional proposals may require explicit flags.

- **[wasm-tools](https://github.com/bytecodealliance/wasm-tools)** — Bytecode Alliance CLI and Rust libraries for inspecting WebAssembly modules, metadata, components and WIT interfaces.

  Foundation tool · Website / Binary · [Source](https://github.com/bytecodealliance/wasm-tools/blob/main/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: Use prebuilt release artifacts or a Rust toolchain; proposal/component support depends on the selected release.

</details>


### Firmware tools

<details>
<summary>Browse 3 resources</summary>

- **[Binwalk](https://github.com/ReFirmLabs/binwalk)** — Identifies embedded formats and optionally extracts their contents, with entropy analysis for firmware triage.

  Foundation tool · Firmware · [Source](https://github.com/ReFirmLabs/binwalk/blob/master/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: The current v3 implementation is Rust-based; extraction needs the appropriate external tools or the documented container environment.

- **[unblob](https://github.com/onekey-sec/unblob)** — Recursively extracts archives and filesystems from binary blobs while reporting chunk boundaries and unknown regions.

  Foundation tool · Firmware · [Source](https://github.com/onekey-sec/unblob/blob/main/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: Python package plus external extractors, or the bundled Docker image; check the project's dependency inventory for the formats needed.

- **[Ghidra Firmware Utilities](https://github.com/al3xtjames/ghidra-firmware-utils)** — Ghidra loaders and helpers for PCI option ROMs, UEFI firmware volumes, Intel flash descriptors and coreboot images.

  Foundation tool · Firmware · [Source](https://github.com/al3xtjames/ghidra-firmware-utils/blob/master/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: The reviewed build instructions require Ghidra 12.0+ and JDK 21+; build against the same Ghidra/JRE environment used for analysis.

</details>


### Binary analysis libraries

<details>
<summary>Browse 4 resources</summary>

- **[Unicorn Engine](https://github.com/unicorn-engine/unicorn)** — Multi-architecture CPU emulator for executing selected instruction ranges with register, memory and hook control.

  Foundation tool · Binary / Game / Firmware · [Source](https://github.com/unicorn-engine/unicorn/blob/master/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: Use a supported binding and explicitly supply the CPU state and memory model; it is a CPU emulator rather than a complete OS environment.

- **[angr](https://github.com/angr/angr)** — Python binary-analysis framework combining control-flow recovery, symbolic execution, data-flow analysis and decompilation.

  Foundation tool · Binary · [Source](https://github.com/angr/angr/blob/master/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: A compatible Python 3 environment; useful results require an appropriate model of program inputs, state and external functions.

- **[LIEF](https://github.com/lief-project/LIEF)** — Library for structured parsing and modification of executable formats including ELF, PE and Mach-O.

  Foundation tool · Binary · [Source](https://github.com/lief-project/LIEF/blob/main/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: C++, Python or Rust integration; check the distinction between core and extended features for the selected distribution.

- **[Capstone](https://github.com/capstone-engine/capstone)** — Disassembly library with architecture-neutral APIs and instruction details for custom binary-analysis pipelines.

  Foundation tool · Binary · [Source](https://github.com/capstone-engine/capstone/blob/next/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: Select a library/binding release supporting the target ISA and mode; the next branch can differ from stable releases.

</details>


### Binary comparison tools

<details>
<summary>Browse 2 resources</summary>

- **[Diaphora](https://github.com/joxeankoret/diaphora)** — IDA-based binary diffing that matches functions and transfers names, comments and types between analyzed versions.

  Foundation tool · Binary / Game · [Source](https://github.com/joxeankoret/diaphora/blob/master/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: IDA with Python 3 support; richer pseudocode and microcode comparisons depend on the corresponding decompiler capabilities.

- **[BinDiff](https://github.com/google/bindiff)** — Compares disassembled binaries to find matching functions and changed code across versions.

  Foundation tool · Binary / Game · [Source](https://github.com/google/bindiff/blob/main/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: Requires a separate supported disassembler/export pipeline; upstream documents IDA Pro, Binary Ninja and Ghidra configurations.

</details>


### Learning resources

<details>
<summary>Browse 4 resources</summary>

- **[OpenSecurityTraining2](https://ost2.fyi/)** — Free self-paced security courses with learning paths for reverse engineering, firmware and systems foundations.

  Learning resource · Binary · [Source](https://ost2.fyi/Learning-Paths.html) · Source reviewed 2026-10-15.
  Requirements and limits: Browser access; choose classes according to their published prerequisites and lab requirements.

- **[pwn.college: Reverse Engineering](https://pwn.college/program-security/reverse-engineering/)** — Hands-on reverse-engineering module covering functions, data access, static tools and dynamic tools with hosted exercises.

  Learning resource · Binary · [Source](https://pwn.college/program-security/reverse-engineering/) · Source reviewed 2026-10-15.
  Requirements and limits: Browser access and the platform's account/environment setup for interactive challenges.

- **[Reverse Engineering for Beginners](https://beginners.re/)** — Dennis Yurichev's free book on understanding compiled programs and assembly, available in multiple languages.

  Learning resource · Binary · [Source](https://beginners.re/) · Source reviewed 2026-10-15.
  Requirements and limits: A browser or PDF reader; use the toolchains relevant to the exercises being followed.

- **[The Official Radare2 Book](https://book.rada.re/)** — Official practical reference for radare2 analysis, disassembly, scripting, debugging and related plugins.

  Learning resource · Binary · [Source](https://book.rada.re/) · Source reviewed 2026-10-15.
  Requirements and limits: Upstream lists radare2 5.8.x as the minimum and recommends a current release for following the examples.

</details>


### Related resource lists

- **[Awesome Reverse Engineering](https://github.com/morluto/awesome-reverse-engineering)** — A task-oriented reverse-engineering resource list by REA's maintainer, useful for broader tools and foundations.

  REA maintainer companion list · Website / Game / App / Binary / Firmware · [Source](https://github.com/morluto/awesome-reverse-engineering/blob/main/README.md) · Source reviewed 2026-10-15.
  Requirements and limits: Individual tools retain their own requirements and licenses. Inclusion in this companion list does not establish REA integration or compatibility.

- **[Awesome REA Cases](https://github.com/songshikang0111/awesome-REA-cases)** — A bilingual collection of REA and other AI-assisted reverse engineering cases, with source links and explicit distinctions between reported and reproduced outcomes.

  Community REA learning resource · Website / Game / App / Binary / Firmware · [Source](https://github.com/songshikang0111/awesome-REA-cases/blob/main/README.md) · Source reviewed 2026-10-16T01:08:16Z.
  Requirements and limits: A discovery index; review each case's original source, redistribution rights, and evidence status before reproducing it.
<!-- END GENERATED CATALOG -->

## Useful companions

For a broad index, see [morluto/awesome-reverse-engineering](https://github.com/morluto/awesome-reverse-engineering). For other REA collections, see [kaixinbaba/awesome-rea](https://github.com/kaixinbaba/awesome-rea) and [jyjyxt/awesome-rea](https://github.com/jyjyxt/awesome-rea). This collection emphasizes task selection, explicit tool relationships, and an executable starting example.

The [repository comparison](docs/benchmark-research.zh-CN.md), [REA ecosystem notes](docs/rea-ecosystem.zh-CN.md), and [tool landscape](docs/tool-landscape.zh-CN.md) contain dated research behind the initial selection. These research notes are currently in Chinese.

## Contribute a useful next step

Suggest a resource, correct an outdated requirement, or contribute a small reproducible investigation. Read the [contribution guide](CONTRIBUTING.md) and [roadmap](docs/roadmap.md). A good addition helps someone complete a concrete task and links to primary evidence.

Original descriptions, scripts, and fixtures are [MIT licensed](LICENSE). Linked projects retain their own licenses. Use targets you own or are authorized to inspect.
