# Repository automation

The repository validates changes in CI and posts a rule-based review on pull requests. It does not automatically approve or merge contributions.

## Pull request review

`Automated PR review` uses the trusted base branch's reviewer. It retrieves selected JSON files as data from the exact PR commit and checks schema, duplicate IDs and URLs, source records, bilingual coverage, scope decisions, target labels, dates, and benchmark consistency. Source-index, localization, and scope changes are checked together against unchanged dependencies from the trusted base. Automated source scans retain a separate status from curated resources.

The reviewer also checks added patch text, and the decoded string values of changed data JSON, for common credential patterns and personal filesystem paths. File names are checked against the private, generated and raw-output entries in `.gitignore`, common key and network-capture names, and licensed font files; these files are reported by path and never fetched. When GitHub omits a file's diff, the reviewer retrieves that file's text from the PR commit as size-bounded data for the same pattern checks. Files it cannot inspect, such as binary or oversized files, are listed for maintainer inspection before merging rather than reported as clean. Reports identify the file, and for data JSON the record and field where possible, without repeating suspected secrets. Pattern checks are a backstop, not a complete secret audit.

The job can write a review comment but does not check out or run the contributor's code, fetch contributor-provided external links, approve the PR, or merge it. Code and workflow changes remain subject to maintainer review. Reviews are attached to a specific head commit. Every run revalidates the data; a repeated run updates the existing bot review and preserves the current check result. Report a weakness in this automation privately under the [security policy](../SECURITY.md), not in a public issue.

## Continuous integration

`Catalog checks` runs on pull requests, including those from forks, and on pushes to `main`. A newer push to a pull request cancels its superseded run; runs on `main` are never cancelled. The `validate` job byte-compiles every script and test, runs the unit tests with `python3 -m unittest discover -s tests -v`, then runs the [production build command](website.md#optional-licensed-production-icons) with the Pages asset-URL option. That build validates curated data and local Markdown links, checks generated README sections and the bilingual repository directory, checks JavaScript syntax, builds the collection website, and runs the discovery and site validators. Finally it installs the pinned `puppeteer-core` package from npm and runs the [browser smoke test](website.md#browser-smoke-test) in the runner's installed Chrome, keeping its screenshots as a workflow artifact. Apart from that package installation, these steps need no secrets or network access. The workflow has read-only repository permissions, and every job has a time limit.

The `main` branch requires the GitHub Actions `validate` and `review` checks, an up-to-date branch, and a pull request before merging. These rules also apply to administrators; force pushes and branch deletion are disabled. No human approval count is imposed, and the bot's review comment is not an approval. Use a feature branch and merge after the required checks pass.

The localization path was exercised in [PR #2](https://github.com/reacher-z/Awesome-REA/pull/2): valid data passed, an intentionally missing Chinese description failed both jobs, and restored data passed. Rerunning the reviewer updated the same head-specific bot review.

`Source links` runs weekly and on manual request. It distinguishes confirmed missing links from rate limits and inconclusive network responses.

Every workflow action is pinned to a full commit SHA with its exact release version in a comment. Dependabot checks these actions weekly and groups available updates into one pull request, waiting seven days after a release before proposing it. Its pull requests run the same `validate` and `review` checks and, as workflow changes, need maintainer review.

## Triage source-link results

From the repository root, save a local report outside the checkout so it is not accidentally included in a contribution:

```sh
python3 scripts/check_links.py --json ../awesome-rea-link-report.json
```

The same checker runs in the `Source links` workflow. It saves the JSON report as a run artifact for 14 days and adds a counts summary, including when the checker reports confirmed dead links. Local runs save JSON only when `--json` is supplied. For slower or restricted connections, use `--workers 2 --timeout 30` and retry later rather than treating a timeout as removal.

Inspect `counts`, `complete`, and each result's `url`, `checked_url`, `references`, `status`, `reason`, and `attempts`. References identify the affected records and fields: `resource:<id>:<field>`, `paper:<id>:<field>`, or `benchmark:<full_name>:<field>`. Curated resources are in `data/rea-resources.json` and `data/tool-resources.json`; papers and benchmarks are in `data/papers.json` and `data/benchmarks.json`. One URL can have several references, so review all affected fields.

| Result | What it establishes | Next step |
| --- | --- | --- |
| `ok` | The final HTTP response was 2xx. | Check that the destination still describes the intended resource; an HTTP success alone does not verify its identity or claims. |
| `dead` | Two consecutive requests returned 404 or 410. | Check the original project's site, repository and release notices for a move, archival notice or removal before proposing a correction. |
| `inconclusive` | Access restrictions, rate limits, network/server failures or another response prevent a conclusion. | Leave the record in place. Inspect the attempts, retry after the restriction clears, or review the public primary source manually. Do not treat authentication walls, 403/429 responses or transient failures as confirmed removals. |

The command exits with status 1 when any link is confirmed dead. Inconclusive results alone still produce exit status 0: inspect `complete` and the counts before claiming all links passed. Do not add credentials to a report or commit raw reports to the repository.

### Verify a moved resource

The checker follows redirects and records the final URL in each HTTP attempt. Compare the original `url`, the actual `checked_url`, and `attempts[*].final_url`. GitHub blob evidence is deliberately checked through `raw.githubusercontent.com` at the same revision; that conversion is not evidence of a project move. Access restrictions such as HTTP 403 or 429 remain inconclusive. A login or access page returning HTTP 200 can still be reported as `ok`, so inspect the destination manually.

Before replacing a canonical URL, verify that the destination belongs to the same upstream resource using a maintainer announcement, a repository transfer/rename, or another primary-source statement linking the old and new locations. Check that the title, authors or owner, and relevant content agree. A redirect to a generic homepage, login page or unrelated mirror is insufficient. Preserve the stable catalog `id` and update only the affected URL/evidence fields and any review metadata supported by the new review; keep pinned evidence at a verified revision where appropriate.

### Submit a correction or retirement proposal

Open an issue or a focused pull request naming the affected IDs, old URLs, observed statuses and check date. For a move, link the public primary evidence establishing the new canonical location. For retirement or replacement, explain the loss of the original resource and the reason for the proposed catalog decision publicly; do not silently substitute an unrelated mirror or reuse an existing ID for a different resource. If the evidence remains inconclusive, report that limitation and leave the entry unchanged pending review.

For a curated catalog correction, regenerate the derived indexes and run the contributor checks:

```sh
python3 scripts/build_readme.py
python3 scripts/build_repository_index.py
python3 scripts/validate.py
python3 scripts/build_site.py
node --check site/app.js
```

For paper changes, also follow the paper-specific validation and production-build steps in [the contribution guide](../CONTRIBUTING.md#suggest-a-research-paper). Review the diff for unrelated generated changes, then include the validation commands and results in the pull request. Keep source review distinct from runtime testing of the linked project.

## Website delivery

See [website building and publishing](website.md) for the static build and hosting setup. Production uses the public source repository while optional Font Awesome Pro assets are supplied through the licensed deployment path. Pro fonts, credentials, private configuration, raw analysis output, and deployment bundles are excluded from the public repository.

The production build command runs `scripts/build_production.py`. It stops deployment if catalog validation or JavaScript syntax validation fails. Cloudflare's existing Git connection builds each change to `main` and creates PR previews; no deployment API token is stored in this repository.

## Scheduled README discovery

`Scheduled README discovery` runs at **00:17, 08:17 and 16:17 America/Los_Angeles** and can be started manually from the default branch. [GitHub's timezone-aware schedule](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule) follows daylight saving changes. GitHub can delay scheduled jobs; these are requested start times.

The scheduled collection target is **160,000 distinct README captures with an explicit Git blob hash match** (`readme_git_sha_matches_content: true`). Each run seeks at most **2,000 new verified captures**, clamped to the qualified count remaining after reconciling the published index with the last checkpoint. Legacy records without a comparison flag and known mismatches remain in the raw evidence, but consume none of this goal. A raw total of 160,000 with only 159,950 qualified captures therefore still plans 50. The child receives a raw-record target of retained records plus the planned verified additions; the parent rejects any new success without explicit verified integrity. At the qualified goal, no discovery or README requests are made. Search results, metadata lookups, failed reads and duplicate IDs do not count toward the goal. The target does not assert that this many relevant repositories exist or that the collection is complete.

The initial REST scheduler was verified with 300 new reads in its first run. The next version uses the separately verified GraphQL transport with **16 repositories per batch**, at most **360 search requests** and **200 legacy metadata lookups** per run. The candidate surplus is 10% of the planned verified additions, bounded to 50–200, so unavailable or invalid README files need not end a run just short of its target. The larger discovery budget retains the same time, GraphQL request/cost, quota-reserve and REST-fallback limits; reaching 2,000 is not guaranteed. It keeps the existing public/non-fork/non-archived scope gates and adds explicitly approved Website/Game/App queries: screenshot-to-code, website clones and reconstruction, pixel-perfect clones, game recreation/reimplementation, UI reconstruction and app clones, plus in-README queries for reverse engineering and pixel-perfect cloning. New roots append to the saved frontier without resetting previous partitions or cursors. The frontier partitions bounded UTC creation intervals instead of repeatedly taking only the first 1,000 results of a broad query. Search-hit populations overlap and do not establish how many successful or relevant resources are available; broader discoveries require separate scope review and never automatic curation.

The [public verification run](https://github.com/reacher-z/Awesome-REA/actions/runs/39315608648), limited to 120 search requests, queued 956 candidates: 948 first discovered by search and 8 from metadata seeding. It yielded 935 verified reads in about 12 minutes at 180 reported GraphQL points. The 360-request ceiling tests whether additional bounded discovery can fill the planned batch. It continues the same saved cursors and scope, and the 38-minute deadline can still produce a partial checkpoint; a larger request budget is not a promise of higher measured throughput.

Runs are serialized. The 45-minute job gives restoration and scanning a combined **38-minute budget**, reserving time for validation and artifact upload. GraphQL pauses on observed rate limits and transient backpressure; it does not evade those signals through REST. The scheduled wrapper also stops new batches after 800 reported GraphQL cost points or requests, preserves a 100-point remaining reserve, and offers at most 200 REST fallbacks, subject to observed remaining quota. Actual outcomes and available query-cost metrics are retained. Missing cost information is not treated as a measured zero-cost query.

[GitHub's repository token receives 1,000 REST requests/hour](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api) and [1,000 GraphQL points/hour](https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api), shared with other uses of that repository token. Batch size and planned increment are not throughput guarantees; rate limits, failures, search boundaries or the time budget can yield a partial run.

The workflow has only `contents: read` and `actions: read`. Its ephemeral `GITHUB_TOKEN` is supplied only to the scanner step. It does not execute upstream code, write source files, create PRs, post comments, or promote discoveries into the public catalog. README text is read, verified, summarized into document features and hashes, and discarded; it is not included in artifacts.

### Paired checkpoints

The version-2 `readme-scan-checkpoint-<run attempt>` artifact contains exactly **`checkpoint.json`, `frontier.json` and `receipt.json`**. The receipt binds both data files' SHA-256 hashes and byte sizes to the same workflow run, attempt and source commit. The next run restores a completed run of this same default-branch workflow and repository, including a validated partial checkpoint from a failed or timed-out run. Earlier attempts of a manual rerun can be resumed. A version-1 two-file artifact can seed the scan state and create a new frontier; a damaged version-2 pair is never silently downgraded.

The scanner saves actual capture evidence before acknowledging its numeric IDs in the frontier. After a timeout, the parent waits for the child to stop, validates both files, and repairs only the safe scan-saved/frontier-not-yet-acknowledged case. An acknowledged ID absent from the paired scan evidence stops restoration. The receipt is written last, and upload is enabled only after the complete pair validates. Working files, `.tmp` files, raw responses, logs and environment dumps are never uploaded.

When the published index advances, reconciliation preserves checkpoint-only captures and the pending-ID union. Success takes precedence over a failed attempt for the same ID; published successful versions take precedence over older versions. Input hashes, original counters and superseded-record hashes preserve provenance. Different numeric IDs claiming the same repository name stop for review with both validated inputs retained. Counts are recomputed from unique identities, not added across snapshots.

A checkpoint marked `in-progress` is resumable but remains rejected by the normal publication validator. Before any authentication, resuming applies the publication validator's hash, URL, repository-visibility and discovery-provenance checks to the retained evidence; completion, the population guard and the remaining fields of a finished record stay publication-only. The scheduler requests explicit incomplete-checkpoint validation without changing that status. Review relevance, source scope, attribution and bilingual descriptions separately before a normal publication PR.

### Bounds and retention

Evidence-file capacity does not relax remote-response limits. Ordinary API JSON responses remain bounded to **12 MiB**; the scan member is bounded to **512 MiB**, the frontier to **256 MiB**, and the receipt to **8 MiB**. The compressed archive is bounded to **512 MiB**, and the sum of uncompressed members to **776 MiB**. Archive downloads and member hashes are streamed; JSON is parsed once per validation, retained records are not deep-copied during reconciliation, and the parent releases full input objects before the child starts. These are enforced bounds, not a claim that a full 160k end-to-end run has been measured.

Version-2 artifacts have **7-day retention** to avoid retaining 90 days of growing full snapshots. At the target, an unchanged paired checkpoint with more than 48 hours left is reused without re-encoding or uploading another copy; a near-expiry checkpoint is renewed to maintain continuity. Canonical changes and version-1 migration can also require a fresh pair. No other artifacts are automatically deleted and repository permissions are not widened. Keep a separately verified durable milestone backup before long pauses: after retention expires, the job stops for recovery rather than silently restarting from a smaller snapshot.

The run summary reports qualified captures, raw retained captures, legacy integrity-unknown captures, known mismatches and failed attempts separately. New version-2 receipts add `goal_basis: explicit-git-blob-sha-match`, `retained_integrity_counts`, `integrity_counts` and `new_qualified_successful_scans`. Each integrity-count object partitions the raw capture count into `qualified`, `legacy_unknown` and `mismatched`; all four receipt fields must appear together. `global_target_reached` follows qualified captures, while `run_target_reached` follows the planned verified increment. Older receipts remain readable, and their global-goal flags are recomputed from retained records before scheduling. Bootstrap-only imports preserve exact raw evidence with zero new verified reads. Artifacts remain a discovery queue, separate from the reviewed public source index and search-engine indexing.

For a separate private worker that starts from reviewed local evidence, see [private scan worker bootstrap](private-scan-worker.md). This first-import path uses a pinned public scanner, a bounded gzip seed and private artifacts; it does not activate a second schedule or change the public catalog.
