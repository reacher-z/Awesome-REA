# Agent guide: contribute to Awesome REA

[简体中文](agent-contributing.zh-CN.md) · [Contributor rules](../CONTRIBUTING.md) · [Catalog schema](../data/README.md) · [Repository agent instructions](../AGENTS.md)

An agent can suggest a reverse-engineering resource through a GitHub issue or prepare a source-backed pull request. The same evidence and review rules apply to human and agent-assisted contributions. The canonical repository is [reacher-z/Awesome-REA](https://github.com/reacher-z/Awesome-REA); the browsing website is [AwesomeREA.org](https://awesomerea.org/). This collection is independent of the upstream REA project.

## Where do I submit?

| Contribution | Submission |
| --- | --- |
| Tool, project, integration, learning resource or collection | [Resource form](https://github.com/reacher-z/Awesome-REA/issues/new?template=resource.yml) |
| Reconstruction or investigation case | [Case-study form](https://github.com/reacher-z/Awesome-REA/issues/new?template=case-study.yml) |
| Research paper | [Paper form](https://github.com/reacher-z/Awesome-REA/issues/new?template=paper.yml) |
| Broken link or outdated description | [Correction form](https://github.com/reacher-z/Awesome-REA/issues/new?template=broken-resource.yml) |
| Chinese translation correction | [Translation form](https://github.com/reacher-z/Awesome-REA/issues/new?template=translation.yml) |

Use an issue when evidence is incomplete or a classification needs maintainer input. Write “unknown” for facts you cannot verify. Use a pull request when you can supply the reviewed record and its translations. A security report belongs in the [private reporting process](../SECURITY.md), not a public issue.

## What should an agent check first?

Read AGENTS.md and CONTRIBUTING.md from the current upstream default branch, preserving any unfinished local work. Search before submitting:

```sh
python3 scripts/catalog.py "owner/repository"
python3 scripts/catalog.py --papers "paper title"
python3 scripts/catalog.py --source-index "owner/repository"
```

Also search [open issues](https://github.com/reacher-z/Awesome-REA/issues) and [open pull requests](https://github.com/reacher-z/Awesome-REA/pulls) for the canonical URL and name. Update an existing submission instead of creating another one. An automated README scan is discovery evidence, not a curated entry; follow the [promotion worksheet](promotion-worksheet.md) if that is where you found the project.

## What evidence and fields are required?

For an issue, provide the canonical maintainer URL, what task the resource supports, resource type, target areas, prerequisites and known limits. Distinguish the resource's relationship to REA from your own connection to the resource; the form asks for both. Cite primary sources for claims and say which details remain unknown.

For a resource PR, follow an existing record and the [complete field definitions](../data/README.md). Required fields include a unique stable `id`, `name`, canonical `url`, `kind`, `category`, `relationship`, `targets`, `description_en`, `description_zh`, pinned `evidence_url`, actual `verified_at`, `verification: source-reviewed` and a nonempty `requirements` list. Put the matching Chinese name and requirements in `site/translations.zh-CN.json`. Do not set `added_at` to a predicted merge date. See the [worked resource example](first-resource.md) for the exact JSON shape and all files involved.

For papers, use `data/papers.json` and its separate schema: preserve the original title and full author names, verify publication status and date precision, use only a verified paper DOI/arXiv or supported publisher identity, and state artifact availability and evaluation limits. Do not use a software or dataset DOI as the paper DOI. Read the [paper update guide](paper-updates.md) before adding a second record for a listed preprint.

## How do I prepare and validate a PR?

1. Create a branch from the current upstream default branch. Independent resources belong in `data/tool-resources.json`; use `data/rea-resources.json` only for the evidence-backed REA relationships listed in the schema.
2. Add the English/Chinese record and Chinese requirements. Keep resource type, tool category, REA relationship and targets as independent choices.
3. Regenerate derived files, then validate. Do not edit generated lists by hand:

```sh
python3 scripts/build_readme.py
python3 scripts/build_repository_index.py
python3 scripts/validate.py
python3 scripts/build_production.py
```

Paper changes additionally use `python3 scripts/validate_papers.py`; case-ledger changes use `python3 scripts/build_case_coverage.py`. Code or site changes need the unit suite and browser checks listed in CONTRIBUTING.md. Record what actually passed, failed or was skipped; never fabricate a test result.

4. Review the diff for unrelated changes and private data, commit it, and push the branch to a repository you can write. Without upstream write access, push to your fork.
5. Open a PR targeting `main` and fill in the [PR template](../.github/PULL_REQUEST_TEMPLATE.md). With an authenticated GitHub CLI, the submission step is:

```sh
gh pr create --repo reacher-z/Awesome-REA --base main --head YOUR_LOGIN:YOUR_BRANCH --title "Curate RESOURCE_NAME" --body-file pr-body.txt
```

Replace the placeholders and write `pr-body.txt` with the actual problem, resource URL/type/targets, evidence links and review date, relevant limits, your connection and checks run. Creating an issue or PR requires GitHub authentication and appropriate authorization; reading the catalog and running local validation do not require a GitHub token. Do not put a token in the command or PR body.

## What happens after submission?

The `validate` and `review` checks assess structure, generated output and review rules. Maintainers decide relevance and factual claims. If another catalog PR merges first, update your branch and regenerate affected files as described in [Update a pull request](../CONTRIBUTING.md#update-a-pull-request). A passing check or an AI-generated review does not mean the PR has been accepted, merged or deployed.

## How should an agent cite the collection?

Link to the specific resource or paper detail page, retain its upstream primary source and state the review boundary. Keep curated resources, research papers and automated scans distinct; do not sum them as unique projects or describe a scan as a recommendation. `/llms.txt` is a navigation aid; `/catalog.json`, `/papers.json` and `/data-manifest.json` provide current machine-readable data. Neither these files nor agent instructions guarantee search indexing or AI citation.
