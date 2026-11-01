# Describing artifact availability and license evidence

[简体中文](artifact-evidence.zh-CN.md) · [Contribution guide](../CONTRIBUTING.md) · [Catalog format](../data/README.md)

Papers and resources often point to code, data, demos or benchmarks whose availability and license are not what a quick look suggests. This guide shows how existing records describe these cases, so new records use the same neutral wording. Every statement about availability or licensing cites the public source that makes it, pinned to the reviewed revision where possible.

## Principles

- **Viewable is not licensed.** Public source code without a license file grants no stated reuse terms. A license file, a README sentence, package metadata and GitHub's detected license are separate signals, and none of them is a legal review.
- **A demo is not a benchmark.** A hosted demo, showcase page or evaluation service is not a downloadable dataset, benchmark or evaluation framework unless one is actually published.
- **Only author-provided links count as artifacts.** A paper's `code_url` and `project_url` are links the authors provide. A same-named repository that the paper does not link is not recorded as the paper's code.
- **Keep conflicts visible.** When sources disagree, attribute each signal to its source; do not collapse them into one label.
- **Keep versions apart.** A repository reviewed today, or a later release, is not the version the paper evaluated unless the authors say so.
- **Do not cross access barriers.** Describe access conditions from their public notice; do not download gated data, accept terms on the project's behalf or run the code.

For papers, availability goes in `code_url` and `project_url` (`null` when no author-provided link qualifies) and is explained in `metadata_notes` and `scope_limitations`, with their `_zh` fields. For resources, it goes in `requirements` and its Chinese translation, with license files and package metadata pinned in `additional_evidence_urls`.

## Decision table

The example wording is taken from existing records.

| Situation | What to record | Example wording | Record |
| --- | --- | --- | --- |
| The authors link public code | The author-provided link in `code_url`; the commit you reviewed | “The paper links the public code repository directly.” | `paper-dashboard2code` |
| Source is public but has no license file | That reuse terms are unstated; no license inferred from visibility | “The repository has no license file, so no reuse license is implied.” | `paper-ble-automata-learning` |
| Code is announced or promised | `code_url: null`; the announcement and where it appears | “the official page still labels code as coming soon.” | `paper-sprite-game-ui` |
| The named location does not provide the code | `code_url: null`; what the location actually contains | “code_url is therefore null, and no public implementation is claimed.” | `paper-dynpre` |
| Only a hosted demo or showcase is available | The page, described as a demo rather than a benchmark release | “The project link is a showcase with demos, not a verified release of the full evaluation framework.” | `paper-gamereplica` |
| Access is gated or on request | The public access notice and its conditions; gated files left unopened | “The linked dataset requires accepting access conditions and sharing contact information.” | `paper-dashboard2code` |
| A repository exists but the authors do not link it | `code_url: null`; why the repository is not recorded | “is not linked from the paper, so it is not recorded as author-provided code.” | `paper-binmetric` |
| License signals conflict | Each signal with its source; no single license asserted | “Licensing signals conflict: README text says CC-BY-NC-SA-4.0, Hugging Face metadata says Apache-2.0, the project page says CC BY-SA 4.0, and setup.py lists MIT while the repository has no LICENSE file. No uniform artifact license is asserted.” | `paper-vision2web` |
| A license is declared in only one place | Where the declaration appears and where it is missing | “The README’s License heading names MIT, but the pinned commit has no LICENSE file and package.json has no license field; the declaration appears only in the README.” | `frida-mcp-yfe404` |
| A later artifact version differs from the evaluated one | Which version you reviewed and how it differs | “The paper’s exact v1.00 data is available only on request, while the public v1.01 release has revised splits” | `paper-exebench` |
| The evaluated version cannot be identified | That the current pinned revision is not claimed to be the historical one | “reviewed at a current pinned commit rather than claimed to be an unchanged historical release.” | `paper-pix2code` |

Write the Chinese field with the same facts; the [Chinese version of this guide](artifact-evidence.zh-CN.md) quotes the Chinese wording of the same records. Unresolved questions stay in the record as stated uncertainty, with the sources that conflict, rather than being settled by assumption.

## When rights questions remain

Some resources raise a question the evidence cannot settle, such as committed files that the project itself says were derived from a commercial program. Describe the facts neutrally in the record, as above. Open the pull request as a draft and state the concern for maintainers at the top. Do not attach or link the questioned material beyond the project's own pages, and never include proprietary binaries or private captures in the repository.
