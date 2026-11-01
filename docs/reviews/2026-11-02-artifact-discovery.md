# REA artifact discovery review — 2026-11-02 (Singapore)

Reviewed between **2026-11-01 16:36 and 16:43 UTC**. Catalog baseline: `2771f980588a45b7eb5c9a3d4195ea3406e57fe9`. [Machine-readable review receipts](2026-11-02-artifact-discovery.json).

This batch adds seven documentation-reviewed cases: four author-reported REA mixed workflows and three independent reconstruction projects. It does not assign completeness scores or report independent runtime tests. Netcat produces analysis artifacts, not a rebuilt app.

本批新增七个文档核查案例：四个有作者报告支持的 REA 混合工作流，三个独立重建项目。不评定完整度分数，也不声称独立实测。netcat 的产物是分析资料，不是重建应用。

## Discovery and duplicate checks

- GitHub: inspected the [community reconstruction list](https://github.com/kaixinbaba/awesome-rea), then pinned each project README to the reviewed commit. Search queries: `"rea-agents" reconstruction in:readme fork:false`, `"morluto/rea" rebuilt in:readme fork:false`, and `"Reverse Engineer Anything" "reimplementation" in:readme fork:false` (50 results requested per query, sorted by update time). Search hit totals overlap and include mirrors, forks not marked as forks, and resource lists; they are not artifact counts.
- Web: used the [community case directory](https://reamcp.dev/zh-cn/search) to find leads, followed Sofa’s link to the author’s [Reddit report](https://www.reddit.com/r/AndroidTVApps/comments/1xa9tv3/i_had_ai_reverseengineer_tcls_browsehere_and/), and read Untangle’s author-published [receipt](https://az9713.github.io/untangle-rebuild/receipt/rebuild-receipt.html). Secondary lists establish discovery only.
- X: keyword searches did not surface reliable primary results. Following the [directory’s X source links](https://reamcp.dev/zh-cn/types/x), all three direct post pages returned HTTP 403. A follow-up through X/Twitter’s official public `publish.twitter.com/oembed` endpoint returned HTTP 200 for all three, confirming author attribution and original excerpts; the two long posts are truncated. [Myttle](https://x.com/xmyttle/status/2110835101583966520) points to an existing official feature-tracing example; [Sojal](https://x.com/0x0SojalSec/status/2109631618088566843) and [MegaBlackLabel](https://x.com/MegaBlackLabel/status/2109620830103802283) do not identify a target or inspectable reconstruction artifact in the returned text. No new software case is promoted from these posts. The receipt JSON retains the endpoints, status, truncation flags and response-content hashes without republishing their text.
- Deduplication: searched the current curated URLs, the automated baseline, open PR titles/bodies, and exact canonical URLs in GitHub’s open issues/PR search. The seven exact-URL searches returned zero open submissions. Compared against the 34 proposed URLs in PR #2549 as well. Only Legend of Legaia already occurs in the automated baseline; its original scan object stays unchanged.

局限：GitHub 每个查询只检查所取的 50 个结果，不代表穷尽；X 直链受限，官方嵌入补查成功，但两条长帖截断；不得用转载补全未知内容或据此认定软件完整度。目录、论文、自动扫描及案例数不可相加为独立产物数。

## Review decisions

| Entry | Primary evidence | Reviewed scope and limits |
| --- | --- | --- |
| [Untangle: a browser rebuild from REA and Ghidra evidence](https://awesomerea.org/resources/untangle-rea-evidence-rebuild-case/) | [Pinned README](https://github.com/az9713/untangle-rebuild/blob/6e9925105247268befeb6faed69025dfce4778fc/README.md) | Playable single-page reconstruction, claim grading and contamination audit; author-reported fidelity. |
| [Sofa TV Browser: a remote-friendly BrowseHere alternative](https://awesomerea.org/resources/sofa-tv-browser-browsehere-case/) | [Pinned README](https://github.com/sonalder-darlene/sofa-tv-browser/blob/6b3afc9544d8e7d2893ed85f184904c8382c02fb/README.md) | A new Android TV browser inspired by a specific remote-control UX, not full BrowseHere equivalence. |
| [OpenBSD netcat: static REA and Ghidra investigation](https://awesomerea.org/resources/netcat-openbsd-rea-static-case/) | [Pinned README](https://github.com/NullLabTests/OpenBSD_netcat_REA/blob/cc1870d34e83bad0b8a6ca2489f6fa177efa6a2a/README.md) | Static investigation and pseudocode only; no reconstructed executable. |
| [OpenBattlefield2: an unfinished Refractor 2 engine reimplementation](https://awesomerea.org/resources/openbattlefield2-refractor-engine-case/) | [Pinned README](https://github.com/Moxnatiy/OpenBattlefield2/blob/1486ef18f52cb0070c8ae8ae06277a413ecb3977/README.md) | Partial engine and server interoperation; major gameplay remains unfinished. |
| [SiegeFX: a Dungeon Siege engine reimplementation in alpha](https://awesomerea.org/resources/siegefx-dungeon-siege-engine-case/) | [Pinned README](https://github.com/codingncaffeine/SiegeFX/blob/6a1a4ade725a860651a06a0d7ddb50d5a3a688d1/README.md) | Alpha engine and modding tools; campaign claims are author-reported, parity gaps remain. |
| [Legend of Legaia: a Rust port with disc-local browser tooling](https://awesomerea.org/resources/legend-of-legaia-rust-port-case/) | [Pinned README](https://github.com/AndrewAltimit/legend-of-legaia-re/blob/f801d3c319386f7686d7fde45e114e1e2ba6aff5/README.md) | Native/browser port and disc-local tools; source reports full-game ladder, disc-gated tests can skip. |
| [FastView-REA: a Rust reconstruction of Fast View 5](https://awesomerea.org/resources/fastview-rea-relay-analysis-rebuild-case/) | [Pinned README](https://github.com/dmytrobsp/fastview-rea/blob/deb89ea4134414a894ba887508ad5d320449be41/README.md) | Rust desktop reconstruction with specs and builds; .sto and pixel-level UI parity remain incomplete. |

The catalog records retain bilingual prerequisites, licenses, evidence, review dates and limits. Sofa’s REA attribution is bound to the author’s Reddit report; its current README supplies current feature gaps, which differ from the older post. Untangle’s 96.3% is an author-reported claim score with a contamination caveat, not a collection rating. OpenBattlefield2’s unfinished weapon/vehicle systems and SiegeFX’s alpha status prevent a complete-software claim.

## Promotion worksheet: Legend of Legaia

- Source ID: `scan-1229734860`, `AndrewAltimit/legend-of-legaia-re`. Observed `2026-10-16T07:15:04.753548Z`; README blob `4807db30bb2381af34c64aa3c59fce5108297b9b`, SHA-256 `9ae9592b6055f1772645956a30a06256a11a5a2a28ec1713f67e02388ad9e3c7`, 24,422 bytes. These are preserved scan facts, not current review evidence.
- Current primary evidence: [f801d3c319386f7686d7fde45e114e1e2ba6aff5 README](https://github.com/AndrewAltimit/legend-of-legaia-re/blob/f801d3c319386f7686d7fde45e114e1e2ba6aff5/README.md); reviewed README byte length/hash are in the JSON receipt.
- Classification: case-study / independent-reconstruction / reconstruction-cases / Game. The README establishes a Rust port of a named game; Ghidra research supports provenance but the result being cataloged is the game reconstruction, rather than a Binary-analysis tool.
- Inputs and limits: owned NA SCUS-94254 disc image; Rust edition 2024 for source builds; author-reported full-game ladder, enhancements differing from retail, disc-gated tests that skip without input. Unlicense/MIT covers code and docs, not original game content.
- Decision: add a separate source-reviewed record and Chinese translation. Retain the baseline automated scan unchanged; generators add the curated cross-link. Nothing upstream was installed or executed.
