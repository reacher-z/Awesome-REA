# REA output follow-up — 2026-11-02 (Singapore)

Reviewed on 2026-11-01 UTC. [Source receipts](2026-11-02-rea-output-followup.json). Baseline: `3b37e89de248d70cc1d3ca0cb7327d7fb0a6306c`.

Four additional author-reported REA mixed-workflow cases, discovered through [REA Atlas](https://github.com/jammyfu/rea-atlas) and checked against their own fixed sources. No upstream program was installed, compiled or executed. No completion or compatibility score is assigned.

| Project | Primary evidence | Decision boundary |
| --- | --- | --- |
| keen-clone: a Commander Keen 1 C/SDL2 port | [Pinned README](https://github.com/carlhako/keen-clone/blob/9c6ac72734c95c3260c23b57158ea5876abc14b3/README.md) | First episode only; original data needed; no project license file identified. |
| samp-client-re: a partial SA-MP client reconstruction | [Pinned README](https://github.com/NathanKanaeru/samp-client-re/blob/6efde5d3042ee87f0c183a6c68b7e1b26a000cac/README.md) | Partial architecture and build/smoke claims; network and graphics behaviors unresolved; no project license file identified. |
| Desktop Games Nostalgia: a macOS and browser port | [Pinned README](https://github.com/ucodia/desktop-games-nostalgia/blob/27946dfe49d4a9b522dfe017c14eefbc0ca40b2a/README.md) | Screen-image toy port with visual differences; original extracted assets and an explicit absence of a project license are disclosed. |
| GunZRs: a Rust reimplementation of GunZ: The Duel | [Pinned README](https://github.com/OpenRsG/GunZRs/blob/485575b7451912ed1d62661c388663b08dce4faf/README.md) | Own LAN protocol; no retail-server interoperation; movement parity unproven and gameplay only reported on Linux. |

All four exact canonical-URL searches returned no open issues or PRs; the current curated catalog and baseline scan also contain no matching roots. The source list itself is discovery evidence, not evidence that every subsystem used REA. GunZRs documents a generic retail-file investigation framework, so its record limits the attribution accordingly.

本批新增四个作者报告的 REA 混合工作流案例，保留局部重建、未验证兼容性和许可边界。Desktop Games 作者明确未提供项目许可，另两个仓库根目录未发现许可文件；本目录仅记录公开资料，不将它们描述为已取得开源或原始素材再分发授权的软件。记录页不提供额外许可，原始资产与代码保留各自权利。

The nearby `a-barzanti/ai-rebuilds` lead is a resource collection, not another reconstructed game; it is not counted as an artifact in this batch.
