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
