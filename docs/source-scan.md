# Automated source index

The [source index](../data/source-index.json) is a separate discovery layer from the curated catalog. Its records are **automated README scans**, not individually reviewed recommendations.

New captures require the received byte length and computed Git blob SHA to match the source metadata. The REST README endpoint can return a truncated or transcoded inline body. When its size or hash disagrees, the scanner reads the advertised immutable Git blob once, verifies the original bytes, and records both `readme_api_url` and `readme_blob_api_url`. It confirms the public repository's numeric identity before requesting document bytes. Unsupported UTF-8, incomplete blobs and hash mismatches do not become successful captures.

The scheduled REST fallback budget allows up to three logical API calls per candidate: repository identity, README metadata/body, and optional immutable blob recovery. In the GraphQL pipeline, exhausted REST rate limits, server errors and network failures leave candidates pending and stop further fallback requests in that batch.

Historical records retain their original evidence. A legacy capture without `readme_git_sha_matches_content: true` is not automatically upgraded by this change. Keep counts of actual captures, explicitly verified captures, missing legacy comparison evidence and known mismatches separate; re-read uncertain records before including them in a verified-capture campaign total. Retained snapshots remain accepted for migration and review.

Initial completed snapshot: **1,600 distinct repository READMEs**, retrieved between 2026-10-16 01:34:02 and 01:37:38 UTC. The 29 queries discovered 2,020 unique candidates; 1,611 were attempted, 11 failed (10 HTTP 404 responses and one empty README), and 409 were not attempted after reaching the target. The successful scan read 16,525,491 bytes and produced 1,596 distinct content hashes. Different repositories can carry identical README content.

Second completed snapshot: **400 new successful README scans** from 405 attempts, completed on 2026-10-16 at 07:15:17 UTC. That snapshot retained **2,000 successful scans** and **16 failed attempts**. All original 1,600 records and 11 failures remain unchanged. The batch added 32 previously unscanned curated repositories and used 10 focused technology/reverse-engineering search queries. Its combined scan records contained 20,426,367 README bytes and 1,996 distinct content hashes.

Third completed batch: **500 new successful README scans** from 509 attempts, completed on 2026-10-16 at 10:48:15 UTC. That snapshot retained **2,500 successful scans** and **25 failed attempts**. All earlier 2,000 success objects and 16 failures remain unchanged. The batch resolved all 164 previously pending repository IDs, yielding 163 successful README reads; one README request failed. It also read six newly seeded curated repositories and ten bibliography-artifact repositories. Twenty-three search requests visited the first and second result pages. Across all retained records, 24,890,042 README bytes and 2,496 distinct content hashes were recorded.

Latest incremental batch: **500 new successful README scans** from 519 attempts, completed on 2026-10-16 at 11:55:19 UTC. The index now retains **3,000 successful scans** and **44 failed attempts**. All earlier 2,500 success objects and 25 failures remain unchanged. Resolving the 191 retained pending IDs yielded 190 successful README reads and one HTTP 404. Two newly referenced bibliography repositories were read, and ten first-page search requests supplied the remaining candidates. All 19 new failures were HTTP 404 responses. The retained records contain 29,399,101 README bytes and 2,991 distinct content hashes.

The current ID-backed discovery population contains 3,296 repositories, with 252 not attempted. The original 409 unattempted candidates had no saved identity list; they are not added to this union unless rediscovered. Their original counts are retained in `meta.resume_history`, alongside the original snapshot hash. `meta.current_run` records the new batch separately.

The authoritative counts and collection window are in the index's `meta` object. `successful_readme_scans` counts distinct public GitHub repositories whose README content was actually retrieved, decoded, inspected for document features, and SHA-256 hashed. Search result totals, discovered candidates, missing READMEs, and failed requests are not included in that number.

## Collection scope

The scan retains **3,000 repository records** as discovery evidence. A separate [scope review](../data/source-scope.json) excludes **164 results** from collection browsing (154 clearly unrelated results, seven duplicate README copies and three repositories whose upstream is no longer available), leaving **2,836 browsable repositories**. The latest batch reviewed 138 candidates and added 107 exclusions, chiefly physical or medical image reconstruction, biological or geophysical research, general course snapshots, ordinary apps and personal profiles. Review retained substantive reverse-engineering projects, adjacent UI comparison/capture tools and source/dependency analysis; uncertain cases remain in the discovery layer. These are scope decisions, not endorsements.

A follow-up review on 2026-10-17 added 18 `game-promotion-page` exclusions for templated 2026 game-trainer, companion and save-editor READMEs. Each captured README promotes a download through badges linking to a separate github.io page and links no source files, build steps, format analysis or findings. The review read the bytes of the recorded Git blob, which matched the captured SHA-256 and the current README. It did not follow or run any download link, and its reasons describe README text only.

Of the 138 reviews, 137 matched the advertised immutable Git blob and captured SHA-256. For one repository, the current README JSON and raw endpoints reproduced the exact 419 captured bytes, while the advertised Git blob held different content. Its scope review uses the matching README bytes, and the source record explicitly retains the advertised identifier alongside the computed content identifier and mismatch evidence. No replacement bytes or extra successful scan were counted.

Each exclusion is keyed by the stable source ID and records its decision, bilingual reason, review date, exact scanned README SHA-256, and matching README URL; an `upstream-unavailable` exclusion records an [availability recheck](#recheck-availability) result instead of the URL. The [scope helper](../scripts/source_scope.py) validates those bindings and annotates generated records with `scope_status: excluded` and `scope_review`; it does not delete scan evidence. If a source snapshot changes, its scope decision must be reviewed again before reuse.

Different repositories can carry the same README. `python3 scripts/scan_sources.py --duplicate-readme-report data/source-index.json` groups successful scans by README SHA-256 offline and shows each record's scope status. Only repositories that also share a repository name receive a proposed `duplicate-readme-copy` review, citing the same-named record with the lowest GitHub repository ID; stars do not choose it, and a shared template README alone does not justify exclusion. Proposals are not applied automatically. A reviewer confirms each copy and sets `reviewed_at`, and validation requires that reason code to cite one related scanned ID with the same README hash. The current snapshot has three such groups. The three records of a Flutter course group were already excluded for other reasons. In the MobileRE-Skill and rev-skills groups, a review on 2026-10-17 confirmed through the GitHub API that each of the seven proposed copies is a non-fork repository with the same name, created after the cited record, and that its recorded Git blob and current README still hash to the captured SHA-256. All seven are excluded as `duplicate-readme-copy`, with reasons that describe only the identical README and the earlier repository. The earlier index-login/MobileRE-Skill and dslsdzc/rev-skills records remain browsable. Excluded copies remain scan records, so `successful_readme_scans` still counts distinct repositories.

The remaining 2,836 entries have not all received individual relevance or functionality review. They are a discovery collection, separate from the [curated, source-reviewed catalog](../data/README.md). Missing target tags alone do not justify exclusion: the unclassified records include game decompilations, language decompilers, and hardware protocol research. Scope decisions are also separate from licensing, safety, and REA compatibility judgments.

### Exact-README review receipts

Before writing a scope decision, re-read the captured README with the [scope review helper](../scripts/source_scope_review.py). Like the [availability recheck](#recheck-availability), it is opt-in: it needs a token in `GH_TOKEN` or `GITHUB_TOKEN`, uses the scanner's guarded API client, and no test, validator or workflow calls it. It accepts at most 50 explicitly named source IDs.

```sh
GH_TOKEN="$(gh auth token)" python3 scripts/source_scope_review.py scan-361197329 scan-1209966933 --print-readme
```

A requested ID that is not a successful scan is reported as `not-scanned` without any request. For every other ID, one [repository metadata](https://docs.github.com/en/rest/repos/repos#get-a-repository) request by numeric ID must confirm the recorded public name; a renamed, missing or private repository stops there as `identity-changed`, `unavailable` or `ineligible`. A second request reads the record's advertised immutable [Git blob](https://docs.github.com/en/rest/git/blobs#get-a-blob), whose bytes must hash to that identifier. Only when they also match the captured byte count and SHA-256 is the outcome `match`, and its receipt then carries the `readme_sha256` and `evidence_url` that a scope decision binds. A `mismatch` yields no scope evidence and is never accepted automatically: the receipt keeps the advertised identifier, the identifier computed from the captured bytes where the record stores one, and the identifier computed from the blob as separate fields. Rate limits, server errors, network failures and malformed blobs are `inconclusive`. `--print-readme` prints each verified README to standard output for the reviewer; it is untrusted upstream text and is not saved.

The receipt is written to `.cache/source-scope-review-<UTC date>.json` by default, and the helper refuses to write into `data/`. It records the source snapshot's SHA-256, the request count and, per ID, the README and blob URLs, byte counts, hashes and a short note, but no README text. No upstream code is run, and no source record or scope decision is changed; the bilingual reason and review date remain a separate reviewed change.

## What was scanned

Queries cover reverse engineering, binary analysis, Ghidra, IDA, Frida, decompilers, disassemblers, firmware analysis, Android, game reconstruction, JavaScript deobfuscation, protocol analysis and related tools. Every executed query, page, result count, timestamp and incomplete-result flag is recorded. Repositories are deduplicated by GitHub's numeric repository ID; private repositories, forks and archived repositories are excluded.

In the default REST mode, the scanner performs a real [Get a repository README](https://docs.github.com/en/rest/repos/contents#get-a-repository-readme) request for each candidate it attempts. It records the README's URL, advertised Git blob identifier, SHA-256 digest, byte count, line count, a bounded heading count and detected installation/usage/requirements/example/license sections. Full README bodies are discarded rather than republished. No code, installers, binaries, tests or commands from a repository are executed.

Retained repository descriptions remain in their original upstream language in `data/source-index.json`. New captures use `bounded-upstream-v1`: descriptions longer than 1,000 characters are omitted, leaving empty source and locale strings plus `description_omission` length and SHA-256 evidence. Three new anomalous descriptions were omitted in this batch; no full text or replacement claim is published for them. Historical source objects remain unchanged. For historical schema compatibility, `description_en` holds that source text even when it is not English, while `description_zh` mirrors it with status `not-translated`. The separate [localization files](../data/locales/README.md) supply English and Simplified Chinese descriptions for the website. Its generated source index retains available original text in `description_original` and marks the derived descriptions as AI-assisted translations. Translation does not verify a repository's claims, safety, or compatibility.

These descriptions derive from attributed upstream text, not independent editorial reviews. The heading statistic counts distinct heading-like lines up to a cap of six; six means at least six, and no heading text is retained. Upstream content keeps its own license; the index does not relicense it.

## Read the labels correctly

- `readme-scanned` means an actual readable, nonempty README was retrieved successfully.
- `automated-readme-scan` does not mean manually reviewed, installed, tested, secure, licensed for reuse or integrated with REA.
- Targets and categories use repository metadata after removing URLs and separating MCP from network-protocol signals. Main tool functions take precedence over secondary game or firmware topics. This is not a review of the full scanned repository or a REA compatibility claim. An empty target list means insufficient metadata.
- New captures use classification engine 4 and record `classification_engine_version`. Since engine 3, each topic is matched separately and an omitted description is never read, so labels depend only on the published name, description and topics, not on topic order or Python's hash seed. Engine 4 adds the `protocol` target from the same signal that selects the `protocol-analysis` category: a `protocol-analysis`, `protocol-analyser`, `packet-analysis`, `pcap`, `wireshark` or `network-forensics` topic, or pcap, Wireshark, network-protocol, protocol-analysis or protocol-reversing wording in the name, description or a single topic. Model Context Protocol wording is removed first, and REST API or mitmproxy mentions alone remain website signals, following the [target guidance](../CONTRIBUTING.md#suggest-a-resource). Retained records keep their stored labels. `python3 scripts/scan_sources.py --relabel-report data/source-index.json` lists, offline, the retained automatic labels that the current engine would derive differently, and `--protocol-report` lists only protocol target and category changes with their qualifying evidence; any relabeling is a separate reviewed change.
- Curated cross-references are derived when the site, repository directories and catalog search are built, not taken from the catalog state at scan time. Only a reviewed curated record whose URL is the exact repository root counts; a scoped documentation page contributes neither targets nor a category. Its targets are added to the recorded ones, and a mapped curated category becomes the primary category. Later curated target additions therefore propagate, while removals never erase recorded labels. Derived records have `classification_origin: curated-build-cross-reference`, the matching curated IDs in `classification_reference_ids`, and their stored labels in `scan_classification`. Records cross-referenced at scan time keep `curated-cross-reference` and their recorded labels unless a current exact match adds to them. The source objects in `data/source-index.json` are not rewritten.
- Stars and license identifiers are GitHub metadata snapshots. A license identifier is not a review of a project's complete licensing terms.
- `failures` records attempted repositories that did not produce a successful README scan. Each keeps `scan_status: failed`, a `reason` error code such as `http-404` or `empty-readme`, a timezone-aware `observed_at`, and `http_status`: the response code, or null for transport and content failures. Validation checks these fields. `unattempted_candidates` records the discovered candidates left over after reaching the requested successful-scan target.

The curated `source-reviewed` records remain in [rea-resources.json](../data/rea-resources.json) and [tool-resources.json](../data/tool-resources.json). Promotion from this source index requires a separate human or agent editorial review under the [contribution rules](../CONTRIBUTING.md).

## Run a fresh scan

Use Python 3.10 or newer and an already authenticated GitHub CLI. Write a fresh scan to the ignored `.cache/` directory:

```sh
python3 scripts/scan_sources.py --target 1600 --workers 16 --requests-per-second 12 --output .cache/source-index-fresh.json
```

Without `--output`, a fresh run writes to `data/source-index.json` and saves its progress checkpoints there, replacing the retained snapshot. A fresh scan samples a new population: live search results, repository metadata and READMEs change over time, so it does not recreate the retained snapshot's candidates or counts. Replacing the canonical snapshot is a separate, reviewed step described below.

The script keeps authentication in process memory, sends it only to `api.github.com`, and refuses redirects that would send it elsewhere. It never writes or logs the credential.

## Continue without replacing earlier evidence

Use a different output path for an incremental batch. For example, continue from the current 3,000-record snapshot toward 3,500 successful reads:

```sh
python3 scripts/scan_sources.py --resume data/source-index.json --output .cache/source-index-next.json --target 3500 --seed-curated --seed-papers --workers 32 --requests-per-second 12 --candidate-buffer 200
```

The scanner preserves earlier record objects, hashes, timestamps, failed attempts, and query observations. It skips previously attempted IDs, keeps a persisted `discovered_repository_ids` ledger, and records per-run counts and provenance. Before search, resume resolves pending numeric IDs through GitHub repository metadata; renamed repositories can be identified without inventing their previous names. These metadata lookups are recorded in `resume_observations`. Failed or ineligible lookups remain unattempted in the ledger and do not count as failed README reads. Private response names, URLs and descriptions are not retained.

`--seed-curated` uses explicit GitHub references from the curated catalogs. `--seed-papers` additionally uses GitHub repository roots from the bibliography's `code_url` and `project_url` fields; it does not guess repositories from project websites. Both pass the same public/non-fork/non-archived eligibility gates. Seed observations retain their originating resource or paper IDs; paper seeds also retain artifact URLs, separately from search-query evidence. A paper artifact link does not establish that runnable code or a public dataset is available.

Repeat `--query 'topic:javascript topic:reverse-engineering'` to supply focused search bases instead of the defaults; the public/non-fork/non-archived gates are appended automatically. The exact ordered plan and executed queries are in `meta.current_run.query_plan` and `meta.queries`. `python3 scripts/scan_sources.py --discovery-report data/source-index.json` prints, offline, a per-run summary of those observations. It splits runs by the counts each resume recorded and places observations by their `run_id`. For each query it gives requests, pages, failed searches, incomplete and capped searches, returned items, skipped candidates and the new successes whose `matched_queries` include it. Each run also shows the distinct union of query-matched successes beside the overlapping per-query memberships. README failures carry no query evidence and are never attributed to a query. Count-only legacy candidates are not reconstructed. After a checkpoint union, the report covers all retained evidence as one segment. An interrupted checkpoint can be resumed to a different output path without re-reading its completed sources.

Before replacing the canonical `data/source-index.json` with a fresh or resumed output, add both-language descriptions for every new ID, review clear scope mismatches, regenerate both repository directories, and run validation. Submit the replacement for review like any other data change. An in-progress checkpoint is not publishable. The source index keeps retained upstream text, explicit omission fingerprints and original README evidence; translation and scope decisions remain separate.

The [increment check](../scripts/check_scan_increment.py) compares a candidate with its frozen baseline offline and prints a JSON report. It exits 1 when retained evidence changed and 2 when an input cannot be read:

```sh
python3 scripts/check_scan_increment.py --baseline data/source-index.json --candidate .cache/source-index-next.json
python3 scripts/check_scan_increment.py --baseline-ref origin/main --publication
```

Every retained success and failure object, query, seed, resume, run-history and reconciliation entry must still be present unchanged; observation order may differ after a scheduled union. Two retained-record changes are accepted, and only when they can be recomputed: a `description_omission` that exactly reproduces `bounded-upstream-v1` from the retained text, and a `readme_integrity_review` on a record whose advertised Git blob did not match. The report counts the new successes, failures and discovered IDs from the recorded entries, rechecks the ledger arithmetic, and confirms any `resume_history` or `checkpoint_reconciliations` entry that names the baseline's SHA-256. A candidate without such an entry gets a warning, since a scheduled seed can be rewritten before resuming. `--publication` reads the working-tree locale shards and scope decisions. It also requires a complete run, a translation for every record with existing shard memberships and values unchanged, and scope decisions bound to the scanned README hashes. The command is not part of `validate.py`.

Search calls are spaced by at least 2.1 seconds; README requests share a bounded request rate and a worker limit. HTTP rate-limit responses trigger a shared wait and retry, and progress checkpoints are saved after each 100 attempted READMEs. GitHub limits each search to at most 1,000 results, so the scanner uses distinct topical queries and records its pagination limits. See [GitHub search behavior](https://docs.github.com/en/rest/search/search#about-search) and [REST API rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api).

This is not a complete census of reverse engineering software. Search vocabulary, repository metadata, star ordering, API availability and the configured scan budget affect coverage. README URLs may change later; the SHA-256 and byte count identify the observed content. New scanner versions also compute `readme_content_git_sha` and set `readme_git_sha_matches_content` by comparing it with the API-advertised identifier. A false flag must not be treated as proof that the advertised blob contains the captured bytes. Explicit follow-up checks can be recorded in `readme_integrity_review`. A successful scan is a starting point for investigation, not a product recommendation.

## Opt-in batched reads and persistent discovery

The collection goal is **160,000 distinct successful repository README reads**. This is a target, not a completed count or a claim that GitHub contains that many relevant projects. The authoritative progress value is `meta.successful_readme_scans`; `--target` counts retained and new successes together.

REST remains the default. To opt into GraphQL and preserve search progress in ignored cache storage:

```sh
python3 scripts/scan_sources.py \
  --resume data/source-index.json \
  --transport graphql \
  --graphql-batch-size 8 \
  --frontier .cache/scan-160000/frontier.json \
  --output .cache/scan-160000/checkpoint-01.json \
  --target 160000 \
  --search-request-budget 120 \
  --pending-metadata-budget 200
```

This uses the existing `gh` login and makes network requests. A large target does not reserve API capacity or guarantee completion in one run. Resume from the newest checkpoint with its matching frontier and a **different output path**, such as `checkpoint-02.json`. Do not pair a newer frontier with an older checkpoint: acknowledged IDs must already exist in the supplied scan evidence. Frontier storage is restricted to `.cache/`; checkpoint and frontier paths must differ.

Pending identities and page positions survive restarts. Legacy pending IDs receive a bounded metadata lookup pass, with stale identities rotated behind unchecked ones. `--search-request-budget` bounds search calls per run. `--graphql-batch-size` accepts 1–16, default 8; larger batches should follow a measured small run. GraphQL requests remain sequential and at least one second apart. `--workers` and `--requests-per-second` do not raise GraphQL concurrency.

Discovery keeps the approved reverse-engineering vocabulary and public/non-fork/non-archived gates. Repeated `--query` options explicitly choose other scope bases; a larger target never silently broadens them. The frontier fixes its initial UTC creation-time boundary and splits intervals when a query exceeds GitHub's 1,000-result cap or returns incomplete results. Unsplittable intervals remain visibly blocked. Finished traversal is not proof of complete coverage because search results change. See [GitHub search limits](https://docs.github.com/en/rest/search/search#about-search).

| Counter | Meaning |
| --- | --- |
| `successful_readme_scans` / `current_run.new_successful_readme_scans` | Actual accepted README reads across distinct repository IDs / this run's additions. |
| `failed` / `attempted_readme_scans` | Recorded README failures / successful plus failed README attempts. Search and metadata lookups are excluded. |
| `unique_repos` / `unattempted_candidates` | Persisted discovered IDs / IDs without a recorded README attempt; neither is a success count. |
| `current_run.readme_transport.outcomes` | Diagnostic results: `ok`, `fallback`, `rejected`, `retry`, `deferred`. A fallback may later succeed through REST; an `ok` payload still passes record validation. |

Read `target_reached` and the actual success count. A run can finish below its target, and separate repositories can share an identical README hash. Frontier counts describe discovery, not README reads or editorial review.

GraphQL checks the numeric repository ID and eligibility in all three phases; stored node IDs support renames. README selection follows `.github`, root, then `docs`. Directory OIDs must match the captured default-branch commit's root tree. Tree listings request names, types, modes and OIDs without measuring unrelated files. A preflight query measures only the selected README blob at that commit, then text requests are grouped within the measured byte budget. Accepted text must be untruncated UTF-8 with an exact byte count and matching Git blob SHA. Records retain SHA-256, blob/commit identifiers, document features and the actual GraphQL endpoint. Bodies are analyzed in memory and discarded.

Ambiguous selection, unsupported files, encoding/hash mismatches and conservative byte limits request the existing REST README reader; a fallback must pass that reader's checks before counting. Rate limits, access failures, network errors and server failures instead leave work pending and stop the batch. They never trigger REST to escape backpressure, and sibling fallback work is deferred too. Already verified successes can be retained. Responses are bounded to 12 MiB, with additional per-blob and aggregate budgets. Credentials stay in memory at the fixed GitHub API origin; GraphQL redirects are refused. GitHub's quota, reset time and `Retry-After` determine deferral, with at least a minute for secondary limits without another retry instruction. See [GraphQL limits](https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api) and [Git blob fields](https://docs.github.com/en/graphql/reference/git#blob).

For a later run that needs failure diagnosis, optionally add `--transport-diagnostics .cache/<existing-run-directory>/transport.jsonl`. The destination must be new, separate from scan/frontier inputs and outputs, and inside the ignored cache without symlink parents. This option is off by default and does not change retry behavior, retained evidence, request counters or admission rules.

The private JSONL file contains a UTC run header and at most 256 failure events, followed by a limit marker if more events are omitted. Events record only a closed reason code, `metadata`/`preflight`/`blob` phase, UTC time, repository count, and available HTTP status/response-byte count. `request_attempted: false` means existing backoff prevented an HTTP attempt; `true` means the opener was called, not proof that a request reached GitHub. Missing status or byte count means unknown. Metadata-validation events share their request's byte context, so event counts and bytes must not be summed as requests or unique reads. No headers, quota balances, bodies, exception messages, repository identities or local paths are retained. A write failure disables the sidecar with a fixed warning while capture continues. A process interruption may leave an incomplete final JSONL line. The sidecar is never a source checkpoint, recovery input or publication artifact, and cannot recover reasons for older runs.

These flags do not install a schedule or publish data. Translation, scope review, generation and validation remain required before updating the public source index; curated promotion requires a separate source review. Automated reads do not grant a Featured badge or establish functionality, safety or REA compatibility.

## Recheck availability

The weekly link checker covers curated, benchmark and paper URLs only, and a URL check cannot tell when a scanned name now belongs to a different repository. The [availability recheck](../scripts/source_availability.py) asks GitHub for each retained scan by its numeric repository ID instead. It is opt-in: it runs only when invoked with a token in `GH_TOKEN` or `GITHUB_TOKEN`, and no test, validator or workflow calls it.

```sh
GH_TOKEN="$(gh auth token)" python3 scripts/source_availability.py --limit 3000
```

The command reads `data/source-index.json`, checks records in numeric-ID order and writes a dated JSON report, by default `.cache/source-availability-<UTC date>.json`. It refuses to write into `data/`. Each record costs one [repository metadata](https://docs.github.com/en/rest/repos/repos#get-a-repository) request by ID; when the ID is gone or its name has changed, a second request checks the recorded name. It uses the scanner's guarded API client, so authentication stays in memory, is sent only to `api.github.com`, and rate-limit responses pause and retry. Requests are sent one at a time, at most `--requests-per-second` (default 5). A run checks at most `--limit` records (default 500), stops before the core REST quota falls below `--reserve` (default 1,000 requests), and stops after `--max-consecutive-inconclusive` failures in a row (default 10). An incomplete or partial run records `next_offset`; pass it as `--offset` to continue.

| Outcome | Meaning |
| --- | --- |
| `available` | The ID resolves to the recorded name and is still public, non-fork and non-archived. |
| `renamed` | The ID resolves under the same owner with a different repository name. |
| `transferred` | The ID resolves under a different owner login, which can also be an account rename. |
| `ineligible` | The ID resolves but is `archived`, a `fork`, `private` or of unconfirmed status. Private and unconfirmed responses record only the reason, never a name, URL or ID. |
| `not-found` | GitHub returned 404 or 410 for the ID: the repository was deleted, made private or hidden, which metadata cannot distinguish. |
| `blocked` | GitHub returned 451 for the ID. |
| `name-reassigned` | The ID is gone and the recorded name now resolves to another public repository ID, which the result names. |
| `inconclusive` | Rate limits, server errors, network failures, other HTTP statuses or unexpected metadata prevented a conclusion. These are never treated as `not-found`. |

Every changed name also gets `recorded_name_http_status` and `recorded_name_status`: `redirects-to-scanned-id`, `other-repository` (with `recorded_name_repository_id`), `not-found`, `private` (private or unconfirmed, with no ID recorded) or `inconclusive`. A renamed repository whose old name now belongs to someone else stays `renamed`, with that other ID recorded. The scanner's name-collision rule keeps such a repository out of future batches until a reviewer decides how to handle it.

The recheck reads no README and changes no source record, hash, timestamp or count. Its report is not publishable data. Annotating or excluding a record because of an outcome is a separate reviewed change, and only `not-found`, `blocked`, `name-reassigned` and `ineligible` results are candidates for one; `inconclusive` results should be rechecked later.

An upstream that no longer resolves by ID is excluded with reason code `upstream-unavailable`. In place of `evidence_url`, which would no longer serve the scanned README or would lead to another repository, the decision keeps the scanned README SHA-256 and copies the record's recheck result unchanged into `availability_check`: the scanned ID, recorded name, check timestamp, outcome, ID lookup status and name lookup status, plus the other repository's ID for a reassigned name. Validation accepts only `not-found`, `blocked` and `name-reassigned` results whose statuses match the outcome, taken after the README scan and no later than the review. Both reasons must give the check date, the IDs, the ID lookup status and the recorded name. A record whose ID still resolves, including a renamed or transferred repository, cannot use this reason and stays browsable. Archived and fork results need a separate decision.

The first full recheck of all 3,000 records, on 2026-10-17, reported three such records; its four renamed repositories, whose old names redirect to the same ID, stay browsable. A fresh check of only the three IDs later that day returned the same results. GitHub returned 404 for repository IDs 1377172300 (newliver666/apk-reverse) and 1409072094 (BAB2007/yuda-run-helper) and for both recorded names. Repository ID 1238268014 also returned 404, while its recorded name, Shellghostt/De-Caffeinator, now resolves to a different repository, ID 1244345068, which was never scanned or reviewed. All three are excluded as `upstream-unavailable`, so the website and repository directories no longer list or link them. Their scan records stay in the full export, and `successful_readme_scans` still counts them.

## Explicit delivery holds

For an administrative hold during a scanner run, repeat `--hold-repository-id 12345` with canonical positive decimal repository IDs. The scanner records sorted `scan-` IDs in `current_run.held_repository_ids`. Configuring an unseen ID as a hold does not add a discovered or pending repository. When an ID is already known or is actually discovered through public metadata/search/frontier evidence, the unattempted held ID stays known and pending. Existing capture/failure objects remain unchanged, including records whose IDs are held later.

A hold blocks candidate delivery from saved frontier entries, retained-ID metadata lookups, fresh searches and curated/paper seeds. A seed known only by repository name may need a real metadata lookup to learn its numeric ID; a `held` observation records that lookup without claiming a README attempt. Held numeric IDs do not consume the legacy metadata-lookup budget. Search skip counters count result occurrences, not distinct reads. Holds do not create failures, private-status claims, ACKs, retry attempts or backoff timestamps.

Holds apply only to the explicit run arguments. Supply them again on a resumed run to retain the administrative hold; omit an ID to release it. Historical hold lists remain in run provenance. They have no automatic expiry and cannot cancel requests already dispatched by another process. A new run rechecks held IDs and actual frontier `next_attempt_at` deadlines before dispatch, so rediscovery or a seed lookup cannot bypass a real pending backoff. Once that deadline expires, an unheld candidate becomes eligible without inventing a retry.

The REST identity preflight is metadata-only. A private, renamed or reassigned identity, or an identity-endpoint HTTP 404/410, stays pending without increasing successful, failed or attempted README counts. The identity-endpoint absence has reason `readme-repository-unavailable`; an actual README HTTP 404 remains a failed README attempt. These metadata outcomes do not pause unrelated candidates. Existing transient REST failure handling still stops sibling fallback requests. Historical ambiguous failures are retained as originally recorded.

## Scheduled checkpoints and publication

The [scheduled discovery workflow](automation.md#scheduled-readme-discovery) requests three scans per day and carries its incremental state in Actions artifacts. Each run seeks up to 2,000 new verified README reads, capped by the remaining distance to 160,000 records with explicit `readme_git_sha_matches_content: true`, using at most 360 search requests within the existing 38-minute budget. Raw records with missing legacy comparison evidence or known mismatches stay intact and are reported separately. This does not guarantee 6,000 additions per day: quota, available candidates and the time budget can lower the result. The checked-in `data/source-index.json` remains the reviewed publication baseline; scheduled results are a separate discovery queue. Inspect each receipt's `retained_integrity_counts`, `integrity_counts`, `new_qualified_successful_scans`, raw `counts`, `outcome` and `global_target_reached` fields. For manual CLI use, `--target` remains the raw accepted-record target; the scheduler translates its verified quota into retained raw records plus the planned additions. The CLI's default search budget is unchanged; this experiment changes the scheduled worker only.

Each schema-2 checkpoint artifact contains only `checkpoint.json`, `frontier.json` and `receipt.json`. The receipt binds both state files by SHA-256 to the workflow run and attempt, source commit, input reconciliation, retained counts and actual new successes. Schema-1 artifacts containing only the checkpoint and receipt remain readable: migration preserves their scan evidence and creates a frontier without inventing prior searches. The saved queue is drained in bounded pages before further discovery requests. A checkpoint marked `in-progress` can be resumed but remains rejected by the normal publication validator. The scheduler explicitly requests incomplete-checkpoint validation without rewriting the stored status.

When extending the published index from an artifact, retain the numeric repository IDs, original capture objects, README hashes and observation provenance. Review relevance, exclusions, attribution and bilingual descriptions separately; regenerate and validate the source-index browser projection and localized directory before opening a normal PR. Do not copy an entire artifact directory into the repository. Successful README retrieval is not source review, execution testing, a license permission or an endorsement.

### Explicit publication selections

The [public supplement layer](../data/source-supplements/README.md) can admit a
reviewed subset of an approved public artifact without pretending that subset
is a new complete capture. It preserves the canonical 3,000-record checkpoint
and its original counts. A ready supplement produces a separate
`source-published.json` with publication counts and per-source capture facts;
the legacy `source-index.json` remains available. Held candidates, including
those missing translations, do not enter the published selection.

The [registered evidence archive](../data/source-evidence/README.md) is retained
exactly, with every JSON member checked before an explicit provenance download
is copied into the site. This is not an import of the private capture campaign
or an automatic promotion of every row in the cloud checkpoint. Curated
resources and their machine-data bundle remain separate.
