# Contributing to Awesome REA

Help a reader choose a tool, understand a behavior, or verify a finding. A focused, well-sourced addition is more useful than a large undifferentiated list.

## Add or update a resource

1. Check the existing catalog with `python3 scripts/catalog.py <keyword>`.
2. Edit `data/rea-resources.json` for REA resources or `data/tool-resources.json` for independent tools and learning resources.
3. Link the original maintainer's repository or documentation. Describe the practical task in your own English and Chinese sentences. A translation can be improved during review.
4. Record requirements and the relationship to REA. A tool that uses MCP is not automatically integrated with REA.
5. Include the exact evidence URL and the date you reviewed it. Use `source-reviewed` for documentation review. Submit runtime results as a separate reproducible lab receipt.
6. Regenerate the catalog sections and run the checks below.

```sh
python3 scripts/build_readme.py
python3 scripts/validate.py
node --test labs/electron-notes/app/csv.test.cjs
```

Use `python3 scripts/check_links.py` for a live check of catalog and benchmark URLs. Network restrictions and rate limits can produce inconclusive results; review these before declaring a link dead.

## Inclusion criteria

- A clear connection to reverse engineering with agents, or a useful supporting task.
- An original source that explains what the resource does and what it needs.
- Accurate release, platform, and commercial-license boundaries.
- A distinct purpose; prefer maintained canonical upstream projects to copied forks.
- No minimum Star count, payment, or reciprocal promotion.

If documentation redirects to a renamed project, review its current scope before keeping the old description. Mark archived or superseded tools explicitly and explain why they remain useful.

## Contribute an investigation

Keep the target small and redistributable. Include the target's origin and license, tool versions, input hash, the question, exact commands, expected evidence, and a way to check the result. Separate observations from hypotheses. State which parts are source-reviewed, locally tested, or dependent on another tool. Use the [investigation template](docs/investigation-template.md).

Do not commit local credentials, application data, raw captures containing personal information, proprietary binaries, or generated analysis with personal paths. The included lab's `output/` directory is ignored; a compact receipt records its verification.

## Review

Catalog JSON and both README sections are validated together. Contributions should preserve link provenance and avoid unsupported claims of compatibility, accuracy, or endorsement. The repository's MIT license applies to original contributions; linked work keeps its own license.

## Automated review and deployment

Pull requests receive a [rule-based catalog review](docs/automation.md) from trusted base-branch code. It checks data and flags common privacy mistakes without running contributor code or automatically approving changes. CI validates the site and original lab; maintainers review code and compatibility claims. Website build and publication details are in the [website guide](docs/website.md).
