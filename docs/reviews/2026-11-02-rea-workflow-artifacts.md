# REA workflow artifact review — 2026-11-02 (Singapore)

Reviewed on 2026-11-01 UTC. Baseline: `ff25d8f6f0390dac8e8c3ba3f707964157bc3d6b`. [Source receipts](2026-11-02-rea-workflow-artifacts.json).

Four author-reported cases and one community integration. No upstream code, kernel module, app, device or model provider was run. No software-completeness rating is assigned.

| Entry | Evidence boundary |
| --- | --- |
| Yanyu | Selected AlphaPai workflows; summaries/automation are simulated, original backend and production/browser/device acceptance are not established. |
| AdamTerm | Ghostty metadata informs a new shell around SwiftTerm; the terminal core is reused, and multiple Ghostty features are omitted. |
| Mi TV Remote | Documented MiLink protocol recovery; real macOS tests on two models versus mobile mock tests remain separate. |
| VSL-DSP | Passive detector and vendor-library/control research; standard audio I/O and unverified bulk hardware transport are separate. |
| ReaFuse | JS/TS donor analysis and generated library/CLI test contracts, not direct closed-app or live-website reconstruction. |

Current canonical URLs, repository IDs, open issues/PRs and existing curated records were checked. No duplicate open submission was found. Mi TV Remote already has an automated baseline scan; it is promoted with a separate reviewed record, leaving the scan untouched.

## Mi TV Remote promotion worksheet

- Baseline: `scan-1419550722`, observed `2026-10-16T11:54:37.746349Z`; README blob `f928c1bbd306e444be09e2069acd92e7df09e4f1`, SHA-256 `61d8ac787889be0d2c9b779c7396bac7f1cf130827458becb869ba2fbbdd3b07`, 9,716 bytes. Stored automatic labels `app`, `binary`, `android` remain unchanged.
- Current primary review: pinned README `6aff7949de88d98a0ec9347bd132761b36ab1d99`; the protocol layout, author-reported verification and platform/mock limits were read.
- Classification: case-study / community-reported-mixed-workflow / community-case-studies, App and Protocol. APK use alone does not establish native Binary analysis, and an existing TV service does not imply a new firmware implementation.
- Decision: add the reviewed bilingual record, retaining model/platform limitations and no project-wide license grant. No TV was connected or modified.

## Core freshness

The published npm metadata and pinned upstream package.json both identify version 6.8.0 and Node `^22.23.4 || ^24.22.1 || >=26.12.1`. The existing core entry is updated as a review snapshot; matching versions/engines do not claim byte identity between npm and the repository. Other older official-guide snapshots are not silently repinned.

## Held lead

FM Season Hub’s static dossier and macOS release are not added as a full reconstruction here. Its pinned macOS documentation says the frontend uses prebuilt runtime assets and has no frontend build source; the reviewed root has no project-wide license file. Packaging checks and a DMG do not establish source/provenance or original-product parity. Retain the analysis lead for separate review.

本批收录四个有范围限定的案例和一个集成，补充许可、平台、输入与验收边界；不把组件/模拟/静态检查当成完整复现。原扫描记录不变，官方安装要求按实际发布元数据更新。
