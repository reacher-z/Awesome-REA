# REA App/Website artifact review — 2026-11-02 (Singapore)

Reviewed on 2026-11-01 UTC. Baseline: `f03202004caec7a418a044dac7525e6c4610f96a`. [Source receipts](2026-11-02-rea-app-artifacts.json).

Five source-reviewed app cases, each with an author-reported mixed workflow. README labels are checked against their research notes; none is given a software-completeness score or independent runtime status.

| Project | Reviewed boundary |
| --- | --- |
| DiskLens | Native WinDirStat findings plus public-source algorithm ports; not closed-source clean-room recovery. Several file/UI actions remain untested. |
| SoundConnect Desktop | REA inventory preceded reuse of an existing protocol engine. One tested headset model does not establish broader compatibility. |
| rec-rs | REA metadata inspection succeeded; native analysis was unavailable. Public OBS source and separate platform tools informed architecture. |
| Sketch | Paper’s local shell was studied; the hosted editor was absent, and several editor features are inferred. |
| Terminal | Public logged-out chart interaction research informed an independent interface, not recovery of TradingView/Bloomberg server code. |

Canonical identity checks include GitHub repository IDs. `michaelshimeles/terminal-rs` resolves to `michaelshimeles/terminal` (ID 1415619130); the record and pinned evidence use the canonical name. Exact canonical URL searches found no open submissions, and no baseline scan IDs match these five repositories.

## Held historical lead

sparkDash is not added as a current REA integration. Its [2026-10-22 revert](https://github.com/MiaAI-Lab/sparkDash/commit/8af0ab37eac8fb87737cf0cf0fdf2d0b15178e9e) removed the REA module; its [reviewed current README](https://github.com/MiaAI-Lab/sparkDash/blob/51daebb6aaecfd3dfaeb2ef9055e867024c84c84/README.md) and complete 707-entry tree have no matching module. This records an evidenced hold, not a claim that the project never used REA.

本批将二进制核对、源码移植、壳层推断、行为研究和协议引擎复用分别说明；不把“使用过 REA”扩大为完整软件复现。sparkDash 的历史集成已回滚，因此不作为当前集成收录。未安装、编译或运行任何上游项目，未修改自动扫描基线。
