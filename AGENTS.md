# Working on Awesome REA

Awesome Reverse Engineering Anything is an independent resource catalog, not the upstream REA CLI/MCP project. Read [CONTRIBUTING.md](CONTRIBUTING.md) and the [agent contribution guide](docs/agent-contributing.md) before changing records or submitting a contribution. The [catalog format](data/README.md) defines the accepted fields and vocabulary.

## Find the right task

- Suggest a resource, case, paper or correction through the existing [GitHub issue forms](https://github.com/reacher-z/Awesome-REA/issues/new/choose), or prepare a focused pull request. Do not create a second submission for an existing issue or PR.
- Search the curated catalog with `python3 scripts/catalog.py <query>`; add `--papers` for the bibliography or `--source-index` for automated discovery records. Check open issues and PRs too.
- Work from the current upstream default branch. Preserve local edits; use a separate branch or worktree when needed. Do not reset another contributor's work.

## Edit sources, then generate

- Independent resources: `data/tool-resources.json`; evidence-backed REA relationships: `data/rea-resources.json`; papers: `data/papers.json`.
- Keep English and Chinese descriptions together. Resource Chinese names and requirements live in `site/translations.zh-CN.json`, keyed by the same stable ID.
- Review public primary evidence, pin GitHub file links to the reviewed commit, and record the actual review date. Do not infer capabilities, REA use or Game/Protocol targets from a name, a secondary list or an MCP interface alone.
- `source-reviewed` means documentation review. It does not establish runtime testing, safety, complete reconstruction or compatibility. Paper records keep `runtime_tested: false`.
- Automated scans and their hashes remain separate evidence. Use the [promotion worksheet](docs/promotion-worksheet.md) when curating a scanned repository; do not upgrade or rewrite its scan object.
- Never edit generated README blocks, `docs/repositories/` or case-coverage summaries by hand. Follow the relevant generator commands in CONTRIBUTING.md. Do not add proprietary binaries, private captures, credentials or local personal paths.
- Use the repository's current schema. Submit changes to validators/vocabulary before data that depends on those new rules, because PR review runs the base branch's validators.

## Validate and submit

For resource changes, regenerate both READMEs and repository directories, then validate:

```sh
python3 scripts/build_readme.py
python3 scripts/build_repository_index.py
python3 scripts/validate.py
```

Follow CONTRIBUTING.md for paper, case-ledger, code and site checks, including `python3 scripts/build_production.py`. Run the full unit suite for code changes; do not run or install an upstream resource just to mark it source-reviewed.

Use the existing PR template. State the problem and resulting behavior, canonical resource URL, pinned evidence, review date, relevant limits and checks actually run. Push to a fork if you lack upstream write access. Creating an issue or PR is a public submission: respect the user's authorization and the target repository's contribution rules. Passing checks does not authorize merging or publication.
