# Automated source index

The [source index](../data/source-index.json) is a separate discovery layer from the curated catalog. Its records are **automated README scans**, not individually reviewed recommendations.

Initial completed snapshot: **1,600 distinct repository READMEs**, retrieved between 2026-10-16 01:34:02 and 01:37:38 UTC. The 29 queries discovered 2,020 unique candidates; 1,611 were attempted, 11 failed (10 HTTP 404 responses and one empty README), and 409 were not attempted after reaching the target. The successful scan read 16,525,491 bytes and produced 1,596 distinct content hashes. Different repositories can carry identical README content.

The authoritative counts and collection window are in the index's `meta` object. `successful_readme_scans` counts distinct public GitHub repositories whose README content was actually retrieved, decoded, inspected for document features, and SHA-256 hashed. Search result totals, discovered candidates, missing READMEs, and failed requests are not included in that number.

## What was scanned

Queries cover reverse engineering, binary analysis, Ghidra, IDA, Frida, decompilers, disassemblers, firmware analysis, Android, game reconstruction, JavaScript deobfuscation, protocol analysis and related tools. Every executed query, page, result count, timestamp and incomplete-result flag is recorded. Repositories are deduplicated by GitHub's numeric repository ID; private repositories, forks and archived repositories are excluded.

The scanner performs a real [Get a repository README](https://docs.github.com/en/rest/repos/contents#get-a-repository-readme) request for each candidate it attempts. It records the README's URL, Git blob identifier, SHA-256 digest, byte count, line count, a bounded heading count and detected installation/usage/requirements/example/license sections. Full README bodies are discarded rather than republished. No code, installers, binaries, tests or commands from a repository are executed.

Repository descriptions remain in their original upstream language. The `description_en` field holds that source text for the shared display interface; `description_zh` currently mirrors it and is explicitly marked `not-translated`. These descriptions are attributed source text, not original editorial summaries. The heading statistic counts distinct heading-like lines up to a cap of six; six means at least six, and no heading text is retained. Upstream content keeps its own license; the index does not relicense it.

## Read the labels correctly

- `readme-scanned` means an actual readable, nonempty README was retrieved successfully.
- `automated-readme-scan` does not mean manually reviewed, installed, tested, secure, licensed for reuse or integrated with REA.
- Targets and categories are automatic metadata labels. An empty target list means there was not enough information for a conservative classification.
- Stars and license identifiers are GitHub metadata snapshots. A license identifier is not a review of a project's complete licensing terms.
- `failures` records attempted repositories that did not produce a successful README scan. `unattempted_candidates` records the discovered candidates left over after reaching the requested successful-scan target.

The curated `source-reviewed` records remain in [rea-resources.json](../data/rea-resources.json) and [tool-resources.json](../data/tool-resources.json). Promotion from this source index requires a separate human or agent editorial review under the [contribution rules](../CONTRIBUTING.md).

## Reproduce a scan

Use Python 3.10 or newer and an already authenticated GitHub CLI:

```sh
python3 scripts/scan_sources.py --target 1600 --workers 16 --requests-per-second 12
```

The default output is `data/source-index.json`. Use `--output` to write another snapshot. The script keeps authentication in process memory, sends it only to `api.github.com`, and refuses redirects that would send it elsewhere. It never writes or logs the credential.

Search calls are spaced by at least 2.1 seconds; README requests share a bounded request rate and a worker limit. HTTP rate-limit responses trigger a shared wait and retry, and progress checkpoints are saved after each 100 attempted READMEs. GitHub limits each search to at most 1,000 results, so the scanner uses distinct topical queries and records its pagination limits. See [GitHub search behavior](https://docs.github.com/en/rest/search/search#about-search) and [REST API rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api).

This is not a complete census of reverse engineering software. Search vocabulary, repository metadata, star ordering, API availability and the configured scan budget affect coverage. README URLs may change later; hashes and Git blob identifiers preserve the identity of the observed content. A successful scan is a starting point for investigation, not a product recommendation.
