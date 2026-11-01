<!-- Summarize what changed and why in one or two sentences. For a new or corrected resource, also give its original source URL, resource type and target areas, and say what the source documentation supports. -->

Closes #

## Validation

<!-- Tick the groups that match your change, run their commands from the repository root, and add anything else you checked. Keep documentation review separate from claims of runtime testing. -->

Curated record (`data/rea-resources.json`, `data/tool-resources.json`, `site/translations.zh-CN.json`):

- [ ] `python3 scripts/build_readme.py`
- [ ] `python3 scripts/build_repository_index.py`
- [ ] `python3 scripts/validate.py`
- [ ] `python3 scripts/build_site.py`
- [ ] `node --check site/app.js`

Research paper (`data/papers.json`):

- [ ] `python3 scripts/validate_papers.py`
- [ ] `python3 scripts/build_readme.py`
- [ ] `python3 scripts/build_production.py`

Case-ledger entry (`data/case-coverage.json`):

- [ ] `python3 scripts/build_case_coverage.py`
- [ ] `python3 scripts/validate.py`

Code or site (`scripts/`, `site/`, `tests/`, `.github/`):

- [ ] `python3 -m compileall -q scripts tests`
- [ ] `python3 -m unittest discover -s tests -v`
- [ ] `python3 scripts/build_production.py --fontawesome-assets-url https://awesome-rea.pages.dev`
- [ ] `npm ci --prefix tests/browser --ignore-scripts` and `node tests/browser/smoke.cjs`

README.md, README.zh-CN.md, docs/repositories/ and docs/case-coverage*.md are generated. Change the data or the builder and regenerate them with the commands above; do not edit them by hand.

Pull requests are public. Remove tokens, cookies, account identifiers, local filesystem paths and private captures from anything you paste, including logs and screenshots. See the [contribution guide](https://github.com/reacher-z/Awesome-REA/blob/main/CONTRIBUTING.md#review-and-publication), and report security problems privately under the [security policy](https://github.com/reacher-z/Awesome-REA/security/policy).

中文说明见[贡献指南](https://github.com/reacher-z/Awesome-REA/blob/main/CONTRIBUTING.zh-CN.md)。
