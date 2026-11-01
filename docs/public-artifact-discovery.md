# Public artifact lead discovery

[Workflow](../.github/workflows/public-artifact-discovery.yml) · [Collector](../scripts/collect_public_artifact_leads.py) · [Source review rules](agent-contributing.md)

This workflow follows public source links three times per day, at 00:17, 08:17 and 16:17 America/Los_Angeles. It can also be dispatched from the default branch. This is a separate, small discovery snapshot; the existing README scanner and its checkpoint are unchanged. GitHub schedules can be delayed and are not an exact-time service.

The snapshot follows these sources:

- Up to 30 recently updated plus 30 newly created public Discussions in `morluto/rea`, deduplicated by discussion number. Questions and project suggestions remain **unreviewed leads**.
- The current, commit-pinned README of `morluto/rea`, `jammyfu/rea-atlas` and `kaixinbaba/awesome-rea`, after checking the Git blob hash against the retrieved bytes.
- Public indexes at `reamcp.dev/zh-cn/types/x` and `madewithrea.com`, followed by at most eight linked case pages on those same sites. The budget is shared across sites and rotates in UTC eight-hour slots, so one alphabetically earlier directory cannot monopolize every run. Their current robots rules are consulted; unavailable or disallowed pages remain explicit coverage errors.
- At most six discovered X post URLs, newest post IDs first, through the public `publish.x.com/oembed` endpoint (the observed canonical target of the legacy Twitter endpoint). A valid rich response with its author URL, paragraph and matching post ID establishes that an original excerpt is available, not that a full thread, video, software artifact or claim has been reviewed. Excerpts may be truncated. Cross-origin redirects remain refused; the canonical endpoint is called directly without GitHub authentication.

This is **source following, not full-web or X keyword search**. It does not search an authenticated timeline, call paid X endpoints, expand arbitrary short links or run a model. Maintainers should continue broader web/X searches and add reviewed source strategies as coverage gaps become clear. No source directory is treated as proof that a project uses REA or completely reconstructs software.

## Read the output

Each Actions run retains `public-artifact-leads-<attempt>` for seven days, containing only:

- `leads.json`: schema version, collection time/code revision, source URLs with response hashes/byte counts or controlled error reasons, deduplicated link leads and coverage counts.
- `receipt.json`: the report's filename, byte count and SHA-256, plus its collection time/code revision and fixed `discovery-only` status.

Downloaded HTML, READMEs, post/discussion text, remote error bodies, environment variables, credentials, device captures and software are not retained. X response hashes refer to the public embed response; the response text is discarded. No code, binary, installer, target app or device is executed.

Every lead keeps `verification: discovery-only` and the source IDs that mentioned it. Questions, existing catalog entries, repository aliases and irrelevant links may appear. Counts are **unique URL leads in this bounded snapshot**, not new projects, reviewed resources, independent software, runtime reproductions or cumulative additions. Repeated snapshots can overlap. GitHub path case variants are merged, while case-sensitive website slugs stay distinct. Renames still require a canonical repository-ID check during curation.

`captured` means the bounded link snapshot has no recorded source failures; it does not certify the linked projects. `partial` means at least one source was unavailable or invalid. `empty` fails the job so a parser or coverage outage is visible. An empty/partial diagnostic can still be uploaded only after its bounded-data and privacy checks pass.

Review a lead using [AGENTS.md](../AGENTS.md), the contribution guide and the [promotion worksheet](promotion-worksheet.md) when a baseline scan exists. Check canonical identity, current primary evidence, open submissions, targets, licenses and limits. A source-reviewed catalog record is a separate contribution; this workflow never changes `data/`, the READMEs, the public website, issues or PRs.

## Bounds and credential handling

The collector starts at most 32 HTTP requests in a 240-second cooperative budget; each request has a maximum 15-second socket timeout and response reads recheck the budget. The eight-minute Actions timeout is the outer stop. Responses are capped at 2 MiB, the report at 4 MiB, and the snapshot at 3,000 URL leads. A GitHub quota reserve stops further calls when the observed remaining quota is below 100. Rate limits stop further requests to that host for the run; no fallback account, transport or credential is used.

Only approved HTTPS API/index/case/embed routes are fetched. Automatic redirects are disabled; only bounded same-origin GET redirects to approved routes are allowed. The ephemeral token is added only to requests for `api.github.com`. Public website and X embed requests receive no GitHub authentication. The workflow has read-only contents/discussions permissions, runs only from the default branch, and uploads only the two named JSON files.

Run the offline regression suite from the repository root:

```sh
python3 -m unittest tests.test_public_artifact_leads
```

The tests cover credential isolation and the actual no-redirect opener, cross-origin rejection, quotas/time/size bounds, robots denial, Git blob mismatches, partial GraphQL responses, alias deduplication, source binding, response-text omission and rejection of a fabricated `source-reviewed`/runtime-tested output. Full repository checks remain required for code changes.

中文：此任务每天三次追踪公开目录、GitHub Discussions 与可访问的 X 原帖片段，属于有边界的线索巡检，并非全网或 X 全文检索。错误与覆盖缺口保留在报告中；不保存原文，不执行上游代码，不自动收录、评分或发布。线索数量与精选资源、独立软件及复现实测数量分开理解。
