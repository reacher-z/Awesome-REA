# Preserved public capture evidence

This directory held one explicitly approved evidence archive. It was withdrawn
on 2026-11-05 at the maintainer's request (see "Withdrawn archives" below);
[withdrawn.json](withdrawn.json) keeps the facts that identify it:

- Original [public workflow run 39323601991](https://github.com/reacher-z/Awesome-REA/actions/runs/39323601991), attempt 1.
- Original [artifact metadata 12221864748](https://api.github.com/repos/reacher-z/Awesome-REA/actions/artifacts/12221864748).
- Source commit: `6d049e1597174f2d548fdafe0a31027c94016bf8`.
- Archive: `run-39323601991-attempt-1-d6d7cee82ca6.zip` (4,532,463 bytes).
- Exact original ZIP SHA-256: `d6d7cee82ca61ceba26f7bbf5d70ff9d7077932ee60fdc1a29022994065e7a03`.
- Checkpoint SHA-256: `17e8ce03441ffcde8971207b1d5777857f8041b0ddcc679b340f2fcbadb7cfbf`.

Until its withdrawal the ZIP was preserved byte-for-byte so that evidence would
not disappear when the original Actions artifact expired. Its only members were
`checkpoint.json`, `frontier.json`, and `receipt.json`. Admission checked their
complete schemas, privacy, CRCs, hashes, numeric identities and run bindings—not
just the selected records. The archive held capture metadata and discovery
state, not README bodies, software, fonts, account credentials, or a local
runtime directory.

The original checkpoint records 12,211 accepted captures: 9,194 have explicit
matching Git hashes, 2,999 retain legacy unknown comparison status, and 18 have
known mismatches. Those historical source counts stay intact. New publication
selections admit only explicit matching captures; they do not silently promote
the legacy or mismatched rows.

When a referencing batch is ready, the builder copies only a registered,
unwithdrawn archive to `/evidence/source-scans/`. The link appears with source
provenance, not as a primary homepage or agent ZIP action. No artifact-directory
glob, log, private campaign, environment file, or unregistered archive is copied
into the site. This archive is no longer copied: `/about/` lists run
39323601991 as withdrawn, and its old address redirects there.

Adding another evidence source requires its own public-source review and an
explicit approved descriptor pin. Public availability alone does not waive
privacy checks.

## Withdrawn archives

At the maintainer's request an archive can be withdrawn: one pull request
deletes it and adds an entry to [withdrawn.json](withdrawn.json) with its
`archive_filename`, `artifact_digest`, `run_id`, `run_attempt`, `size_in_bytes`,
the selection digest of every batch that cites it (`batch_selection_sha256`),
the UTC `withdrawn_at` date and a one-line `reason` / `reason_zh`. The automated
review accepts that deletion only when the entry names the exact digest and
size of the archive on the default branch and the selection digests of the
default branch's batches that cite it; an existing entry cannot change or
disappear, and a withdrawn archive cannot return to this directory.

The batches citing a withdrawn archive keep their exact records, selection IDs
and fingerprints: validation rejects a batch whose selection digest differs from
the one recorded at withdrawal, so a record cannot change even with a recomputed
fingerprint. The published selection keeps the archive's digests and run with
`archive_url: null` and an `archive_withdrawal` date and reason. What can no
longer be re-checked offline is each record's membership in the original
checkpoint. Nothing is copied to the site: `/about/` lists the run as withdrawn,
and the build adds redirect rules from the old archive address to that listing.
A withdrawn archive cannot back a new selection.

## 简体中文

这里曾保留上面指定的公开工作流原始 ZIP（字节不变，防止 Actions 证据到期失效），
该压缩包已于 2026-11-05 应维护者要求撤回，[withdrawn.json](withdrawn.json) 保留其运行编号、
摘要和大小。撤回前，三个 JSON 成员都要完整通过结构、隐私、CRC、哈希、仓库身份和运行来源校验。
原始采集数量不会被改成发布选集的数量；新选集只准入明确通过 Git 哈希比对的对象。
证据链接放在来源说明中，不恢复首页或智能体入口的 ZIP 主操作。

应维护者要求撤回的证据压缩包，由同一个 pull request 删除，并在
[withdrawn.json](withdrawn.json) 中记录文件名、原始摘要、运行编号与尝试次数、
字节数、引用它的每个批次的选择摘要（`batch_selection_sha256`）、UTC 撤回日期和中英文一行原因。自动审核只在记录与默认分支上的压缩包摘要和大小、
以及默认分支上引用它的批次的选择摘要完全一致时接受删除；已有记录不得修改或删除。引用该证据的批次保留原始记录、
选择编号和指纹；选择摘要与撤回时记录的不同即校验失败，因此即使重算指纹也无法改动记录。
无法再离线复核的只是记录属于原始检查点。网站不再提供下载，
`/about/` 标明该运行的证据已撤回，原下载地址重定向到那里。
