# REA firmware and report outputs — 2026-11-02 (Singapore)

Reviewed on 2026-11-01 UTC against main `fef37bd7cdb4d1a73503d263b07a8baa5eb02d9f`. [Source receipts](2026-11-02-rea-firmware-reports.json).

Discovery examined the latest 25 updated public REA Discussions. Requests to build software and general questions were not counted as completed artifacts. These three projects were followed to fixed primary sources and deduplicated against current curated URLs and open issues/PRs. No target, upstream script or device was run.

- **MXQ PRO RK3229:** a hardware-specific firmware investigation/repurposing case. REA’s documented role was inventory and Android-provider routing, not autonomous reconstruction of Android or Armbian.
- **iCSee LocalMod:** an additive stock-firmware extension for one camera. Native static analysis, fake-backend protocol tests and owner-reported physical validation remain separate; not a universal firmware replacement.
- **App X-Ray:** a community integration producing static reports, not another reconstructed app. Report-derived benchmark answers reuse the same static evidence, and network literals do not establish observed traffic.

本批增加两个案例和一个集成，不把集成、需求帖或报告参考答案当成完整重建或独立运行真值。固定 README 与补充工作流/指南保留 REA 归因、原厂依赖、硬件范围和许可边界；所有记录仍是 source-reviewed。
