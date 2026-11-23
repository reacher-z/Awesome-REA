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
