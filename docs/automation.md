# Repository automation

The repository validates changes in CI and posts a rule-based review on pull requests. It does not automatically approve or merge contributions.

## Pull request review

`Automated PR review` uses the trusted base branch's reviewer. It retrieves selected JSON files as data from the exact PR commit and checks schema, duplicate IDs and URLs, source records, target labels, dates, and benchmark consistency. Automated source scans retain a separate status from curated resources.

The reviewer also checks added patch text for common credential patterns, personal absolute paths, private configuration, raw output, and licensed font files. Reports identify the file and problem without repeating suspected secrets. Pattern checks are a backstop, not a complete secret audit.

The job can write a review comment but does not check out or run the contributor's code, fetch contributor-provided external links, approve the PR, or merge it. Code and workflow changes remain subject to maintainer review. Reviews are attached to a specific head commit. Every run revalidates the data; a repeated run updates the existing bot review and preserves the current check result.

## Continuous integration

`Catalog checks` runs on pushes and PRs. It validates curated data and local Markdown links, checks generated README sections, confirms the original lab's file hashes, runs its three behavior tests, builds the static site, and checks JavaScript syntax. The workflow has read-only repository permissions.

`Source links` runs weekly and on manual request. It distinguishes confirmed missing links from rate limits and inconclusive network responses. `Reproduce REA lab` is a manual, version-pinned integration run so routine documentation changes do not repeatedly download the REA toolchain.

## Website delivery

See [website building and publishing](website.md) for the static build and hosting setup. Production uses the public source repository while optional Font Awesome Pro assets are supplied through the licensed deployment path. Pro fonts, credentials, private configuration, raw analysis output, and deployment bundles are excluded from the public repository.
