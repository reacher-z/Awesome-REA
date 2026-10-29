# Private scan worker bootstrap

The public catalog and the scheduled discovery state have different publication needs. Workflow artifacts in a public repository are downloadable by signed-in users with repository read access, so private working evidence must stay in a private repository. See [GitHub's artifact access rules](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/download-workflow-artifacts).

The [private worker entry point](../scripts/private_scan_worker.py) runs an exact public scanner revision from a separate private repository. It verifies both repository names and the private repository's numeric ID, confirms its actual visibility and default branch through GitHub, and checks the scanner and worker checkouts against their pinned revisions. Configuration, the import manifest and every compressed seed member must be tracked files whose bytes match the worker commit. Neither token values nor local paths belong in the configuration.

## Prepare a first seed

Use frozen, terminal files. The [seed packer](../scripts/scan_seed.py) accepts one global checkpoint, one selected frontier, and up to four additional frontiers retained only as evidence:

```sh
python3 scripts/scan_seed.py \
  --checkpoint .cache/frozen/checkpoint.json \
  --frontier .cache/frozen/primary-frontier.json \
  --evidence-frontier .cache/frozen/other-frontier.json \
  --output .cache/private-bootstrap
```

The output contains a manifest and explicitly named gzip files. It contains no logs, environment, credentials or README bodies. Each input passes the scanner's strict structure/privacy checks. The manifest records compressed and expanded hashes and sizes; the packer rejects inputs that change while being validated or compressed. Expanded source files retain their exact bytes, timestamps and capture objects.

Each compressed member is capped at 50 MiB. Expansion uses the existing 512 MiB checkpoint, 256 MiB frontier and 776 MiB aggregate bounds. Decompression is streamed and rejects trailing data, concatenated gzip members, header filenames, hash/size mismatches and malformed evidence. No Git LFS or external download URL is used. A larger future seed that exceeds the compressed limit needs a separate storage design; it must not be silently split or truncated.

Copy only the reviewed package into `bootstrap/` in the private worker repository. Keep its `scanner.json` limited to `schema_version`, `scanner_repository`, `scanner_revision`, `worker_repository` and `worker_repository_id`. The public repository ignores generated `scan-seed-*.json.gz` files. Do not copy a whole cache directory or force-add those files to the public catalog.

Frontier partition IDs depend on root order. The import therefore preserves one selected frontier, checks every acknowledgment against the global scan, and retains other frontier files as separately hashed evidence. Approved missing roots append as fresh partitions. Their earlier traversal is not claimed as part of the selected frontier. Discovery includes 52 explicit reverse-engineering, Website, Game and App scope roots, including broader English and Chinese README queries. Hits remain unreviewed candidates; query matches do not establish relevance or justify curated inclusion.

## Verify before scheduling

Start the private worker with manual dispatch only. The first run must explicitly choose the seed. Use `--bootstrap-only` to validate and save the pair without launching discovery or README reads. Its receipt reports zero new reads and records `manual-local-union` as the origin. The existing source checkpoint schema is unchanged: import metadata belongs in the private receipt, and original captures are never relabeled as cloud captures.

The receipt distinguishes the private workflow commit (`source_commit`) from the pinned public scanner revision (`execution_source`). Subsequent runs restore the private workflow's own validated artifact, preserve `bootstrap_origins` in the receipt, and report only the actual read delta. Restore checks still bind the artifact, run, attempt, both member hashes, acknowledgment set and counts. The workflow uploads exactly `checkpoint.json`, `frontier.json` and `receipt.json`, with seven-day retention.

This version supports only a first import. If private worker state already exists, an additional seed import fails without changing it. A later bulk-import feature must preserve existing record versions and all known IDs with explicit provenance. Until then, local bulk captures and the scheduled worker can diverge again; their totals must be reconciled by numeric ID rather than added.

Before enabling private recurring runs, verify the account's included Actions allowance and spending-stop policy. Private hosted-runner execution and artifact storage are not assumed free. Do not change billing settings as part of bootstrap. After a manual import and a subsequent restore/read run are verified, remove the public schedule before enabling the three daily times in the private worker. Never leave both schedules enabled. The current public workflow is unchanged by this helper implementation.
