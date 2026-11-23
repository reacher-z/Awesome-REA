# Backlog curation review — 2026-11-23

This batch digests the followed-source lead backlog and adds six tool records: four Binary Ninja or IDA analysis plugins and two x64dbg automation tools. It is the first batch curated from the stored lead queue rather than from fresh scans; the followed-source workflow keeps completing without writing new batches because its sources have published nothing new since 2026-11-20.

## Selection scope

The stored queue holds 8,930 pending identities. Tool-kind leads whose descriptions mention Ghidra, IDA, Binary Ninja, x64dbg, radare, decompilation or disassembly numbered 462; nine were shortlisted for activity and license, six passed manual review. Records that only exist in a dead or superseded form (bad64 points at its replacement exarmo, rust_diff at binja_diff_view) were replaced by their living successors.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `ida-arsenal` | `native-analysis` | [khalilammarr/ida-arsenal](https://github.com/khalilammarr/ida-arsenal/blob/c36a4abc8473c5b393db5fef91f346ca64b3c96e/README.md) | `68c06aa2328c7eda6658d9ff7a6b125da6e01c9c5e20a3c50cad10ca3d725d16` |
| `binja-agent-mcp` | `agent-mcp` | [y637F9QQ2x/binja-agent-mcp](https://github.com/y637F9QQ2x/binja-agent-mcp/blob/1b954eba368897760844c6308de433ffc563a567/README.md) | `8b22e5bc70f17af0df58f03296d7599c8815253f06989a2ec24f8875a9c798f3` |
| `binja-diff-view` | `native-analysis` | [meerkatone/binja_diff_view](https://github.com/meerkatone/binja_diff_view/blob/551f3f687fdf1217a3e8153c60aaa8565f611706/README.md) | `bb1bf26a3ca10a58272d810fd241d7a0811b6181b75eda1a53940ba9b8238b21` |
| `threatray-binja` | `native-analysis` | [cod3nym/threatray-binja](https://github.com/cod3nym/threatray-binja/blob/0b0780547b97b155dd807e0e0d93f837a14a8ce7/README.md) | `4bfbe3926216aea1b51318d080b42e3aa999a5499ace4cb0c106894ecd46637e` |
| `x64dbg-automate` | `dynamic-analysis` | [dariushoule/x64dbg-automate](https://github.com/dariushoule/x64dbg-automate/blob/76421a901499fb22846127b0cba6b7c4de0ab850/README.md) | `86cc7b971a57cbeb6e71cfa770e32149148f95d4212b32bf430fc9d20a370e62` |
| `x64dbg-skills` | `agent-workflows` | [dariushoule/x64dbg-skills](https://github.com/dariushoule/x64dbg-skills/blob/0409f535af6f29389676f1d7f60f25cc83801cb8/README.md) | `a13b9902f1fe60cea4279e8b06aac397f586c57f9c5dc688eddb962468df66ab` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| yrp604/bad64 | The crate declares itself dead in favor of Vector35 exarmo; the living successor belongs upstream, not in this catalog. |
| meerkatone/rust_diff | Superseded by the same author\u0027s binja_diff_view, which is recorded instead. |
| BenMcAvoy/IDA-Plugins, overkazaf/VulnHunter4Ghidra, icsharpcode/AvaloniaILSpy | No license file recorded by the GitHub API. |

## Validation notes

All six records are `kind: tool` with `relationship: foundation`, carry Chinese requirement items in site/translations.zh-CN.json parallel to their requirement_facets, and received evidence-class entries. The evidence previews, READMEs, case indexes and site were regenerated after the catalog change.

---

# Backlog curation review, second batch — 2026-11-23

This round adds seven more tools from the stored lead queue: unidbg (Android native-library emulation), microsoft DebugMCP (a debugger MCP server for AI agents), the x64dbg DataExplorer (ImHex pattern language in the debugger), binja_wasm (a WebAssembly architecture for Binary Ninja), bninja-ps3 (a Cell PPU ELF loader), binja-blocks (Apple libclosure annotations) and GhidrAI (an AI-assisted malware pipeline for Ghidra).

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `unidbg` | `android` | [zhkl0228/unidbg](https://github.com/zhkl0228/unidbg/blob/30911d7ecf44ee8aeed2ae5e6c91bb683c8afdd4/README.md) | `d34feb56407b7ab43868f15a01880aaf520fe9a367da7665b91aa112c92878eb` |
| `debugmcp` | `agent-mcp` | [microsoft/DebugMCP](https://github.com/microsoft/DebugMCP/blob/d0b4a334a6a3d8d600c5aa75ec60d9de272af3c4/README.md) | `89275f3226e7ec2795c560db41e7fb78be30ae4042c7605f62c82d2941728ff0` |
| `dataexplorer` | `dynamic-analysis` | [x64dbg/DataExplorer](https://github.com/x64dbg/DataExplorer/blob/904b75dc41d8b5c40d89594599e11c81bc008ef5/README.md) | `bdbacb575714b478ddbfe2d4d24070189f13e971ca43bea045e20469c10df1b6` |
| `binja-wasm` | `native-analysis` | [SecondNewtonLaw/binja_wasm](https://github.com/SecondNewtonLaw/binja_wasm/blob/ab4ac166dcbf0078158470e6382bf7e579bfbf4a/README.md) | `569f853be9c94fbdee8b597aa634388df5cd26a9e48b26b33e8c53e75f7add19` |
| `bninja-ps3` | `native-analysis` | [valters-tomsons/bninja-ps3](https://github.com/valters-tomsons/bninja-ps3/blob/5e53df569359b0132f949e018d2aef74df75f71e/README.md) | `d91de03d775d5e7c9e0dde2671d86b641b39bc25657f772ec494a870a0b7e66b` |
| `binja-blocks` | `native-analysis` | [droe/binja-blocks](https://github.com/droe/binja-blocks/blob/75c8c29fcec719274ebf59cc1e29b2a759730805/README.md) | `a5730bdb4b51d4d23326095b361946fd4048bf27c0adc7486c40e67a9fccf427` |
| `ghidrai` | `agent-workflows` | [John-A0/GhidrAI](https://github.com/John-A0/GhidrAI/blob/274474a47e7db1aeb18c3bc0085d674444a5dc6f/README.md) | `f3e448c1684263700b04ece55618a7c251a32d871a7e4d719612770eb206a04a` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| idalib-rs/idalib | Rust bindings for the IDA SDK with 355 stars, but the repository records no license file. |
| psifertex/BinAssistMCP, symgraph BinAssistMCP family | Overlaps with binja-agent-mcp recorded in the first backlog batch; recorded one Binary Ninja MCP server. |
| bochs-emu/Bochs, Ircama/ELM327-emulator | General-purpose emulators outside the catalog\u0027s reverse-engineering tool scope. |

---

# Backlog curation review, third batch — 2026-11-23

This round adds eight more records from the stored lead queue: two PlayStation emulators (RPCS3 and shadPS4) and the v86 PC emulator, the MemProcFS memory-forensics file system, the XIV Animation Toolkit, the OpenJK source port of the two Jedi Knight games, and the librespot and SatDump protocol tools.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `rpcs3` | `game-analysis` | [RPCS3/rpcs3](https://github.com/RPCS3/rpcs3/blob/3bfac607760d39dcdbe77eb137ab6dbb723b3b36/README.md) | `a074616f81441f36d6a06d4ce30239bd8a6d01123eec9ebe74e8f7e2a9b7e526` |
| `shadps4` | `game-analysis` | [shadPS4-emu/shadPS4](https://github.com/shadPS4-emu/shadPS4/blob/bbc020e5d0fcc959a4fe5bd9cdaa0205b0edf405/README.md) | `6b1150aeb8744fbac86a06ab5fd1658e0af6cf601a6bacdfb3a7d4d85d999ec6` |
| `v86` | `firmware` | [copy/v86](https://github.com/copy/v86/blob/9457e7a2f6890f3133bb6ac0f749e588f63c4c36/README.md) | `3b580d883b88ad6c22e00dd74bafed216aa44eed134690541770ab5a183b6c16` |
| `memprocfs` | `dynamic-analysis` | [ufrisk/MemProcFS](https://github.com/ufrisk/MemProcFS/blob/6d30b27bcf3295088b36e289aa111aff176e993e/README.md) | `fc3e3e8597a58c824d6b6f1573d3b03d00ae3e008eb60216a0cdc75005e9f721` |
| `xat` | `game-analysis` | [Etheirys/XAT](https://github.com/Etheirys/XAT/blob/3955622dba651456efbd8ecfdaf045cb0f2423c4/README.md) | `68a20449699407e21cb86cd042a1480da4774db310123aaceb87628642a8a8c8` |
| `openjk` | `reconstruction-cases` | [JACoders/OpenJK](https://github.com/JACoders/OpenJK/blob/260c59c2907187af555a676fe0cc798893bf7757/README.md) | `617c291db3e826a630ee986c02320fd5041dc6bdba635aa204c7898005182451` |
| `librespot` | `protocol-analysis` | [librespot-org/librespot](https://github.com/librespot-org/librespot/blob/15e02e86c72d96dd39d548e3749f00abe39ffdde/README.md) | `78f78f9266aba8daeea81256e8f475b4bdaed10c3bb3d13023ab01b0bfd81bde` |
| `satdump` | `protocol-analysis` | [SatDump/SatDump](https://github.com/SatDump/SatDump/blob/9fee0793c7d42bea2d401d330422e18c33c126fa/README.md) | `704f997118da74ad48557e2a274b0ea8d86cdabf41b45b72fed581237e98ec15` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| renezander030/capcut-cli, LibreDWG/libredwg | Already curated under existing ids; the lead queue still listed them as pending. |
| openvideodev/react-video-editor | Source-available OpenVideo License restricts larger for-profit companies; no standard open-source license. |
| godotengine/godot, assimp/assimp, luanti-org/luanti | General-purpose engines and asset libraries, not reconstructions or analysis tools. |
| Etheirys/XAT sibling animation utilities | Superseded by XAT, which combines them. |

## Validation notes

All eight records carry pinned README evidence, Chinese requirements parallel to their facets where facets are present, and evidence-class entries. The batch also fixes the `WASM` spell-check finding in the previous batch by writing `WebAssembly` in the binja_wasm description, then regenerates previews, READMEs, case indexes and the site.
