# Repository automation

The repository validates changes in CI and posts a rule-based review on pull requests. It does not automatically approve or merge contributions.

## Pull request review

`Automated PR review` uses the trusted base branch's reviewer. It retrieves selected JSON files as data from the exact PR commit and checks schema, duplicate IDs and URLs, source records, bilingual coverage, scope decisions, target labels, dates, and benchmark consistency. Source-index, localization, and scope changes are checked together against unchanged dependencies from the trusted base. Automated source scans retain a separate status from curated resources.

The reviewer also checks added patch text for common credential patterns, personal absolute paths, private configuration, raw output, and licensed font files. Reports identify the file and problem without repeating suspected secrets. Pattern checks are a backstop, not a complete secret audit.

The job can write a review comment but does not check out or run the contributor's code, fetch contributor-provided external links, approve the PR, or merge it. Code and workflow changes remain subject to maintainer review. Reviews are attached to a specific head commit. Every run revalidates the data; a repeated run updates the existing bot review and preserves the current check result.

## Continuous integration

`Catalog checks` runs on pull requests, including those from forks, and on pushes to `main`. A newer push to a pull request cancels its superseded run; runs on `main` are never cancelled. The `validate` job byte-compiles every script and test, runs the unit tests with `python3 -m unittest discover -s tests -v`, then runs the [production build command](website.md#optional-licensed-production-icons) with the Pages asset-URL option. That build validates curated data and local Markdown links, checks generated README sections and the bilingual repository directory, checks JavaScript syntax, builds the collection website, and runs the discovery and site validators. These steps need no secrets or network access. The workflow has read-only repository permissions, and every job has a time limit.

The `main` branch requires the GitHub Actions `validate` and `review` checks, an up-to-date branch, and a pull request before merging. These rules also apply to administrators; force pushes and branch deletion are disabled. No human approval count is imposed, and the bot's review comment is not an approval. Use a feature branch and merge after the required checks pass.

The localization path was exercised in [PR #2](https://github.com/reacher-z/Awesome-REA/pull/2): valid data passed, an intentionally missing Chinese description failed both jobs, and restored data passed. Rerunning the reviewer updated the same head-specific bot review.

`Source links` runs weekly and on manual request. It distinguishes confirmed missing links from rate limits and inconclusive network responses.

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
