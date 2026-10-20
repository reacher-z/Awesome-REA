# Contributing to Awesome Reverse Engineering Anything

[简体中文快速入门](CONTRIBUTING.zh-CN.md)

Help keep this collection useful, well organized, and current. Contributions can add a project, tool, case study, integration, related collection, or reference; correct an entry; or improve its category and description.

## Suggest a resource

Use the resource issue template or submit a pull request with:

- **Name and original URL** — prefer the project maintainer's repository or website.
- **Resource type** — project, tool, integration, case study, collection, documentation, learning resource, or research.
- **Target area** — Website, Game, App, Binary, Firmware, or Protocol; multiple areas are allowed.
- **Short description** — explain what the resource provides in your own words.
- **Relevant conditions** — include platform, license, release, or external-tool requirements when they affect the description.

Check the existing collection before adding a duplicate. A resource does not need a minimum number of Stars. Prefer original, maintained projects over copied forks. Claims about REA integration should be supported by the project's own documentation.

Use Protocol when primary evidence describes communication-format analysis, traffic dissection, message exchanges or protocol-state inference, including hardware buses. Generic network access, API usage or an MCP interface alone does not qualify. Binary-encoded messages do not imply executable Binary analysis. Preserve existing targets when adding another reviewed task area; do not retag historical scan records automatically.

## Update the catalog

Curated records live in `data/rea-resources.json` and `data/tool-resources.json`. Keep the English and Chinese descriptions concise. Use `kind` for the resource type and `targets` for its application areas; these are different dimensions. The website's translated names and requirements are in `site/translations.zh-CN.json`.

Record a primary source and review date. `source-reviewed` means documentation was checked; it does not claim that the project was installed, audited, or reproduced. The larger `data/source-index.json` is an automated repository index and retains its separate provenance.

Runtime and reproduction results are currently out of scope for catalog records: every curated record uses `verification: source-reviewed`, every paper keeps `runtime_tested: false`, and there is no separate format for submitting test runs. You may describe what you ran in an issue to help reviewers check a claim, but it is not published as verification. After editing records, regenerate and validate:

```sh
python3 scripts/build_readme.py
python3 scripts/build_repository_index.py
python3 scripts/validate.py
python3 scripts/build_site.py
node --check site/app.js
```

Run every test with one command from the repository root. It needs Node.js for the browser tests and makes no network requests. A single module also runs from the root, for example `python3 -m unittest tests.test_protocol_target`.

```sh
python3 -m unittest discover -s tests -v
```

The `validate` check runs exactly these steps: it byte-compiles every script and test, runs the test command, then runs the production build with the asset-URL option used by Cloudflare Pages. That build repeats catalog validation, the JavaScript syntax check, the site build and both site validators without fetching the asset origin. Last, the [browser smoke test](docs/website.md#browser-smoke-test) rebuilds the site and loads it in headless Chrome; locally it skips with a message when Chrome or its pinned driver is missing.

```sh
python3 -m compileall -q scripts tests
python3 -m unittest discover -s tests -v
python3 scripts/build_production.py --fontawesome-assets-url https://awesome-rea.pages.dev
npm ci --prefix tests/browser --ignore-scripts
node tests/browser/smoke.cjs
```

Use `python3 scripts/check_links.py` for live source checks. Rate limits and temporary network failures are reported separately from confirmed missing links.

### Choose kind, relationship, category and targets

Choose these fields independently; apart from the [reconstruction pairing](#reconstruction-cases), one does not determine the others:

- `kind`: what is being shared, such as a tool, integration or case study?
- `relationship`: what connection to REA, an independent agent workflow, or a foundation tool does the evidence establish?
- `category`: which task or tool family fits the resource?
- `targets`: what subjects does it help analyze or reconstruct?

Use the current values in the [catalog format guide](data/README.md). These existing records show how the choices fit together; their linked evidence is documentation, not a claim that the tools were run:

- **Independent reconstruction:** [`kef-lsx-volume-case`](data/tool-resources.json) uses `kind: case-study`, `relationship: independent-reconstruction`, `category: reconstruction-cases`, and `targets: [app]`. Its [source](https://github.com/roberdorfer/kef-lsx-volume/blob/6fbd7f76c63bf6d7da0979db4a1b312a064e0b4b/README.md) describes an app using LAN control; network access alone does not make the target `protocol` or establish a REA connection.
- **Foundation tool:** [`ghidra`](data/tool-resources.json) uses `kind: tool`, `relationship: foundation`, `category: native-analysis`, and `targets: [binary, game, firmware]`. The [source](https://github.com/NationalSecurityAgency/ghidra/blob/master/README.md) supports the catalog's foundation-tool classification; no REA connection is implied. One tool-family category can serve several target domains.
- **Integration:** [`playwright-mcp`](data/tool-resources.json) uses `kind: integration`, `relationship: independent-agent-integration`, `category: agent-mcp`, and `targets: [website]`. The [source](https://github.com/microsoft/playwright-mcp/blob/main/README.md) describes an MCP interface; that alone does not establish official REA integration or protocol reverse engineering.
- **Protocol analysis:** [`netzob`](data/tool-resources.json) uses `kind: tool`, `relationship: foundation`, `category: protocol-analysis`, and `targets: [protocol]`. Its [source](https://github.com/netzob/netzob/blob/088fe769e98e0bfbd3ed99e66b3982446bf8d197/README.rst) describes analysis of communication formats and state, rather than merely using a network connection.

Choose multiple targets when the evidence supports each area. Category describes the task or tool family; targets describe its application areas. Keep existing reviewed targets rather than automatically reclassifying historical records.

Paper ordering is separate from resource classification. In [papers.json](data/papers.json), `paper-pix2code` has `targets: [app, website]`; its first target selects the App reconstruction section. The [README builder](scripts/build_readme.py) uses `targets[0]` for ordinary papers and handles its agent-evaluation papers separately. Do not sort paper targets or apply that ordering rule to resource categories.

## Suggest a research paper

Use the [paper submission form](https://github.com/reacher-z/Awesome-REA/issues/new?template=paper.yml). Include the canonical paper page or DOI, its publication status, the reverse-engineering task it studies, and links to author-provided code or data where available. An accessible paper does not imply that its benchmark or evaluation service is public.

Bibliographic records live in `data/papers.json`, separately from the tool catalog and automated scan index. For a pull request, use the paper field table in the [catalog format guide](data/README.md), follow an existing record, and preserve the original title and full author names. Supply English and Chinese titles, summaries, relevance and limitations; distinguish preprints, conference acceptance, published proceedings and journal articles. Journal articles use `journal-article` and export as BibTeX `@article`; the journal title belongs in `venue`. Record only the verified date precision: never invent a publication day or conference date. Keep `runtime_tested` false unless the catalog schema and independent reproduction evidence are explicitly extended. Run `python3 scripts/validate_papers.py`, regenerate both READMEs, then run `python3 scripts/build_production.py`.

Use a verified paper DOI or arXiv identifier whenever available. Never substitute a software or dataset DOI for a paper identifier. A published conference or workshop paper without either may use a reviewed publisher identity. Supported profiles pair a canonical USENIX Security presentation page with `/system/files/secYY-presenter.pdf`; USENIX Security 2024 instead uses `/system/files/usenixsecurity24-presenter.pdf`. A WOOT presentation page pairs with `/system/files/conference/wootYY/wootYY-paper-presenter.pdf`. WOOT 19 instead uses `/system/files/woot19-paper_presenter.pdf`; suffixed copies such as `woot19-paper_presenter_0.pdf` are not covered. The series, year and presenter must match, and both exact URLs must appear in `evidence_urls`. Other publisher profiles require a separate validator review. Preprints and accepted-but-unpublished papers still require a paper identifier. URL matching records an auditable source-review contract; reviewers must verify the actual publication, authors, date and PDF.

## Reconstruction cases

Use the [reconstruction-case form](https://github.com/reacher-z/Awesome-REA/issues/new?template=case-study.yml) in English or Simplified Chinese. Separate the original inputs, reconstructed output and evidence; partial or untested cases can be suggested.

Cases may use REA, other agents, or independent reverse-engineering tools. Use `independent-reconstruction` for a documented reconstruction project with no established REA connection, and `reconstruction-cases` as its category; validation rejects either value without the other. The `targets` describe the actual Website, Game, App, Binary, Firmware or Protocol domain. Identify author-reported results, incomplete behavior, platform limits and required original assets. Keep a pinned public source where possible; never include proprietary target binaries or private captures.

## Review and publication

Pull requests receive a [rule-based review](docs/automation.md) from trusted base-branch code. It checks catalog structure, duplicates, source fields, and common privacy mistakes without executing contributor code. Maintainers review resource relevance and factual claims. Passing automation does not automatically approve or merge a contribution.

The protected `main` branch requires the `validate` and `review` checks before merging, including for administrators. After changes reach `main`, the connected Cloudflare Pages project runs the collection checks and publishes the website. See the [website maintenance guide](docs/website.md).

Snapshot releases are tagged `vMAJOR.MINOR.PATCH` on `main` and attach the data snapshot to the GitHub release. Before tagging, a maintainer sets `version` in [CITATION.cff](CITATION.cff) to the tag without its `v`, and `date-released` to the UTC date the release is published, in the release commit itself. `validate.py` checks that both fields are present together, that `version` is a semantic version and that `date-released` is not in the future. Add a DOI or other identifier only after one has been minted.

Do not include credentials, private account details, personal filesystem paths, proprietary binaries, raw private captures, or licensed Font Awesome Pro files in the public repository. Original contributions use the repository's MIT license; linked resources retain their own licenses. The [artifact and license evidence guide](docs/artifact-evidence.md) shows how records describe unavailable or gated artifacts, demos and conflicting license signals.

Issues and pull requests are public. Remove tokens, cookies, account identifiers, local filesystem paths and private captures from anything you paste into them, including logs and screenshots. Report security problems, such as a workflow weakness, an exposed credential or a listed resource that appears compromised, privately under the [security policy](SECURITY.md).
