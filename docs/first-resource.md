# Your first resource: a worked example

[简体中文](first-resource.zh-CN.md) · [Contribution guide](../CONTRIBUTING.md) · [Catalog format](../data/README.md)

This walkthrough follows one existing record, `r2frida` in [tool-resources.json](../data/tool-resources.json), through every file that adding a curated resource touches. It is a model to copy for your own resource. r2frida is already in the catalog, so do not add it again: give your record its own ID and its own evidence.

You need a clone of the public repository, Python 3.10 or newer and Node.js. No licensed icon files, deployment access, tokens or network access are needed for the commands below.

## 1. Check for an existing entry

Search the curated catalog and the separate automated repository index before writing anything:

```sh
python3 scripts/catalog.py r2frida
python3 scripts/catalog.py --source-index nowsecure/r2frida
```

The first command finds the curated record. If your resource is already curated, propose a correction to that record instead of a second one. The second command finds the repository in the automated index; an index record is a README scan, not a review, so curating it still needs the steps below.

## 2. Review and pin the primary source

Read the project's own documentation and record what it states. r2frida's `evidence_url` is its README at the reviewed commit, `https://github.com/nowsecure/r2frida/blob/4f1f8d7b1096ed0ca29778688d0f164461d56f05/README.md`, so the link keeps showing the text that was reviewed, while `url` stays the moving project link. `python3 scripts/validate.py` prints a non-blocking warning when GitHub evidence is a bare repository root or an unpinned wiki page. `verified_at` is the date of your review.

`verification: source-reviewed` means only that the description was checked against that documentation. It does not claim that anyone installed, audited or ran the project, and catalog records do not carry runtime results. If you did run something, you may describe it in the pull request to help reviewers; it is not published as verification.

## 3. Write the record

Records connected to REA by their evidence (the official, community and companion-list relationships) are in [rea-resources.json](../data/rea-resources.json). New independent records such as r2frida go at the end of [tool-resources.json](../data/tool-resources.json). Both files are rendered together, and an ID must be unique across both. The record:

```json
{
  "id": "r2frida",
  "name": "r2frida",
  "url": "https://github.com/nowsecure/r2frida",
  "category": "dynamic-analysis",
  "relationship": "foundation",
  "kind": "tool",
  "targets": ["app", "binary"],
  "description_en": "Use radare2 commands and Frida instrumentation together to inspect local or remote process memory, symbols, classes, and runtime calls on desktop and mobile targets.",
  "description_zh": "结合 radare2 命令与 Frida 插桩，检查桌面和移动目标中本地或远程进程的内存、符号、类及运行时调用。",
  "evidence_url": "https://github.com/nowsecure/r2frida/blob/4f1f8d7b1096ed0ca29778688d0f164461d56f05/README.md",
  "verified_at": "2026-10-16",
  "verification": "source-reviewed",
  "requirements": [
    "Install with r2pm or use a plugin build matching the radare2 major/minor ABI; the reviewed README reports CI against radare2 6.2.2 and git master.",
    "Mobile or remote operation needs a reachable Frida target, such as frida-server over USB or TCP. The plugin bundles the host Frida library; separate host frida-tools are not required."
  ]
}
```

| Field | Choice in the example |
| --- | --- |
| `id` | A lowercase slug that also becomes the detail-page path, `/resources/r2frida/`. |
| `category` | The tool family, `dynamic-analysis`; `python3 scripts/catalog.py --list-categories` prints the values in use. |
| `relationship` | `foundation`: an established tool that works independently of REA. Nothing in its documentation establishes an REA connection, so none is implied. |
| `kind` | `tool`, chosen independently of the category and relationship. |
| `targets` | `app` and `binary`, because the README covers desktop and mobile processes. |
| `description_en` / `description_zh` | Original sentences on what a reader can do with it, not copied marketing text. |
| `requirements` | Installation and platform conditions the reviewed documentation states, with the reviewed version where it matters. |

The [contribution guide](../CONTRIBUTING.md#choose-kind-relationship-category-and-targets) explains how to choose `kind`, `relationship`, `category` and `targets`, and the [catalog format](../data/README.md) lists every field and allowed value.

## 4. Add the Chinese name and requirements

The website's Chinese names and requirements live in [translations.zh-CN.json](../site/translations.zh-CN.json), keyed by the record ID. Give one Chinese `requirements` item for each English item, in the same order. `name` is optional: r2frida keeps its upstream name, and without a `name` the site shows the English one. Use the terms in the [Chinese glossary](../CONTRIBUTING.zh-CN.md#术语对照).

```json
"r2frida": {
  "requirements": [
    "通过 r2pm 安装，或使用与 radare2 主版本和次版本 ABI 匹配的插件构建；复核时 README 说明 CI 测试覆盖 radare2 6.2.2 和主分支。",
    "移动或远程操作需要可连接的 Frida 目标，例如通过 USB 或 TCP 连接的 frida-server。插件包含主机端 Frida 库，无需单独安装主机端 frida-tools。"
  ],
  "name": "r2frida"
}
```

## 5. Regenerate and check

Run these from the repository root:

```sh
python3 scripts/build_readme.py
python3 scripts/build_repository_index.py
python3 scripts/validate.py
python3 -m unittest discover -s tests
python3 scripts/build_site.py
node --check site/app.js
```

The two edited source files map to these outputs:

| Edited source | Regenerated by | Output | What changes for r2frida |
| --- | --- | --- | --- |
| `data/tool-resources.json`, `site/translations.zh-CN.json` | `build_readme.py` | `README.md`, `README.zh-CN.md` | The entry, under Native Binary with “Also: App”, and the resource counts. Its category chooses the section; the Chinese README uses the Chinese name. |
| `data/tool-resources.json` | `build_repository_index.py` | `docs/repositories/` pages and the repository counts in both READMEs | A “Curated” link on the nowsecure/r2frida line of `dynamic-analysis.md` and its Chinese page, because `url` is the exact root of a scanned repository. Other resources leave these files unchanged. |
| Both | `build_site.py` | `dist/`, ignored by Git | The homepage catalog, `/resources/r2frida/`, `/zh/resources/r2frida/` and the sitemap. |

Commit the two source files and whatever the builders changed under `README.md`, `README.zh-CN.md` and `docs/repositories/`; never commit `dist/`. A case study that also maps to the [case coverage](case-coverage.md) ledger additionally changes `data/case-coverage.json` and is summarized again by `python3 scripts/build_case_coverage.py`.

To look at the pages, serve the build with `python3 -m http.server 8000 --bind 127.0.0.1 --directory dist` and open `http://127.0.0.1:8000/resources/r2frida/` and `/zh/resources/r2frida/`. CI also runs the production build and a browser smoke test, which the [contribution guide](../CONTRIBUTING.md#update-the-catalog) lists; locally the smoke test skips when Chrome is missing.

## 6. Open the pull request

Push a branch to your fork and open a pull request against `main`. Fill in the template: the original URL, type, targets, a short description, the pinned evidence and review date, what you did not verify, and the commands you ran. A [rule-based review](automation.md#pull-request-review) from trusted base-branch code checks structure, duplicates, source fields and common privacy mistakes, and `Catalog checks` runs validation. Maintainers then review relevance and factual claims; passing checks does not approve or merge a pull request.

If a resource raises a question for maintainers, for example because it includes material derived from proprietary software, open the pull request as a draft and describe the concern at the top. Pull requests are public: remove tokens, cookies, account identifiers, local paths and private captures from anything you paste.
