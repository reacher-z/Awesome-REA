# Update a paper when it is accepted or published

[简体中文](paper-updates.zh-CN.md) · [Contribution guide](../CONTRIBUTING.md#suggest-a-research-paper) · [Paper fields](../data/README.md)

A preprint in [papers.json](../data/papers.json) may later be accepted, appear in proceedings or become a journal article. Update the existing record in place: the paper keeps its stable ID, and its preprint history stays on record. This guide follows a real update, `paper-crebench`, which changed from `conference-accepted` to `conference-paper`.

## 1. Confirm it is the same work

Compare the new publication with the record: title, full author list, abstract and the evaluation it reports. Small title variants can still be the same paper; `paper-dire` keeps a note that the publisher and arXiv titles say "Naming" while the conference program says "Renaming". If the work is the same, update the record. Never add a second record because a paper gained a DOI, proceedings pages or a journal version. The validator rejects a repeated paper ID, arXiv ID, DOI or canonical paper URL.

A genuinely different paper gets its own record. That means a new title and identifier with a new method, dataset or evaluation, such as `paper-dirty` after `paper-dire`. Leave the earlier record's identifiers, dates and artifacts where they are. If you cannot tell whether a later article is the same work, say so in the issue instead of merging or duplicating records.

## 2. Keep the ID and the preprint evidence

Keep `id` unchanged, so the `/papers/<id>/` pages and citations stay stable. Keep `arxiv_id` and `first_arxiv_date`: they record when the work first appeared and remain true after publication. `arxiv_version_reviewed` names the arXiv version you actually read; change it only when you review a newer version, and say why in `metadata_notes`. Keep the arXiv abstract in `evidence_urls`.

## 3. Add only verified publication metadata

| Field | What changes |
| --- | --- |
| `publication_status` | `conference-accepted` when acceptance is verified but published proceedings are not; `conference-paper` or `journal-article` once the published version is verified. |
| `venue` | The conference, workshop or journal; a journal article uses the journal title. |
| `doi` | The paper's own DOI, never a software or dataset DOI. It stays `null` when the publisher assigns none. |
| `url` | The canonical published page, such as the DOI link or the official proceedings or review record. |
| `citation` | Optional container, volume, pages or article number, copied only from the publisher's sources. |
| `evidence_urls` | Add the publisher, DOI or Crossref pages you checked; keep the earlier evidence. |
| `verified_at` | The date of this review. |

Update the `_zh` counterpart of every English text field you change.

## 4. Explain the date

`publication_date` and `date_precision` record only what a publication source verifies, and `date_basis` names that source. A publisher's deposited publication date can give a day or month. A conference's event dates, an acceptance announcement or a review-site timestamp are not publication dates; mention them in `metadata_notes` if useful, but do not record them as the publication date. If only the year is verified, keep `date_precision: year` and `publication_date: null`. Never invent a day.

## 5. Review the changed full text

Read the published or camera-ready version, not only its landing page. Update `description`, `scope_limitations` and `why_fits` if the method, results or scope changed, and point `pdf_url` at the version you reviewed. If you could not read the publisher's full text, say which version you read in `metadata_notes`.

## 6. Keep artifact versions apart

`code_url` and `project_url` stay the author-provided artifacts. A repository that has changed since the evaluation, or a code release published later, is not the exact artifact the paper evaluated unless the authors say so, for example by naming a tag or commit. Keep that limit in `scope_limitations` or `metadata_notes`. `paper-dire` records that its original code repository is deprecated in favor of a successor, rather than implying current support.

## Worked example: CREBench

On 2026-10-17, [PR #203](https://github.com/reacher-z/Awesome-REA/pull/203) updated `paper-crebench` after its COLM 2026 record appeared on OpenReview.

| Field | Before (reviewed 2026-10-16) | After (reviewed 2026-10-17) |
| --- | --- | --- |
| `id` | `paper-crebench` | `paper-crebench`, unchanged |
| `publication_status` | `conference-accepted` | `conference-paper` |
| `url` | `https://arxiv.org/abs/2604.03750` | `https://openreview.net/forum?id=tLYdf8hWJB` |
| `pdf_url` | `https://arxiv.org/pdf/2604.03750` | `https://arxiv.org/pdf/2604.03750v2`, the version the project calls camera-ready |
| `arxiv_id`, `first_arxiv_date`, `arxiv_version_reviewed` | `2604.03750`, `2026-04-04`, `v2` | Unchanged |
| `doi` | `null` | `null`; no DOI was verified |
| `date_precision`, `publication_date` | `year`, `null` | `year`, `null` |
| `date_basis` | Venue confirmed by arXiv comments and the author project; proceedings date not verified | Year from the official OpenReview record and its BibTeX; no finer date asserted |
| `evidence_urls` | arXiv abstract and v2 HTML, author repository and project page | OpenReview record, COLM accepted-papers and conference pages, and the arXiv v2 PDF added; the earlier links kept |

The new `metadata_notes` explain the decision. The OpenReview record matches arXiv v2 in title, seven authors and abstract. OpenReview's 2026-07-08 timestamp coincides with the acceptance announcement and is not used as a publication date. The October 6–9, 2026 conference and its poster session are event details. The repository's BibTeX still cites arXiv. No second record was added, and the year-only precision was kept because no source gave a finer publication date.

## Check and regenerate

```sh
python3 scripts/validate_papers.py
python3 scripts/build_readme.py
python3 -m unittest discover -s tests
python3 scripts/build_production.py
```

The README builder updates the paper listings in both READMEs; commit them with `data/papers.json`. The production build regenerates the paper directory, detail pages and BibTeX downloads in the ignored `dist/` directory. As for every paper record, `runtime_tested` stays `false`: the update reviews sources and does not reproduce results.
