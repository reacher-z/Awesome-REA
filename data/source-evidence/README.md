# Preserved public capture evidence

This directory has one explicitly approved evidence archive:

- Original [public workflow run 39323601991](https://github.com/reacher-z/Awesome-REA/actions/runs/39323601991), attempt 1.
- Original [artifact metadata 12221864748](https://api.github.com/repos/reacher-z/Awesome-REA/actions/artifacts/12221864748).
- Source commit: `6d049e1597174f2d548fdafe0a31027c94016bf8`.
- Archive: `run-39323601991-attempt-1-d6d7cee82ca6.zip` (4,532,463 bytes).
- Exact original ZIP SHA-256: `d6d7cee82ca61ceba26f7bbf5d70ff9d7077932ee60fdc1a29022994065e7a03`.
- Checkpoint SHA-256: `17e8ce03441ffcde8971207b1d5777857f8041b0ddcc679b340f2fcbadb7cfbf`.

The ZIP is preserved byte-for-byte so evidence does not disappear when the
original Actions artifact expires. Its only members are `checkpoint.json`,
`frontier.json`, and `receipt.json`. Admission checks their complete schemas,
privacy, CRCs, hashes, numeric identities and run bindings—not just the selected
records. The archive contains capture metadata and discovery state, not README
bodies, software, fonts, account credentials, or a local runtime directory.

The original checkpoint records 12,211 accepted captures: 9,194 have explicit
matching Git hashes, 2,999 retain legacy unknown comparison status, and 18 have
known mismatches. Those historical source counts stay intact. New publication
selections admit only explicit matching captures; they do not silently promote
the legacy or mismatched rows.

When a referencing batch is ready, the builder copies only this registered file
to `/evidence/source-scans/run-39323601991-attempt-1-d6d7cee82ca6.zip`. The link
appears with source provenance, not as a primary homepage or agent ZIP action.
No artifact-directory glob, log, private campaign, environment file, or
unregistered archive is copied into the site.

Adding another evidence source requires its own public-source review and an
explicit approved descriptor pin. Public availability alone does not waive
privacy checks.

## 简体中文

这里只保留上面指定的公开工作流原始 ZIP，字节不变，防止 Actions 证据到期失效。
三个 JSON 成员都要完整通过结构、隐私、CRC、哈希、仓库身份和运行来源校验。
原始采集数量不会被改成发布选集的数量；新选集只准入明确通过 Git 哈希比对的对象。
证据链接放在来源说明中，不恢复首页或智能体入口的 ZIP 主操作。
