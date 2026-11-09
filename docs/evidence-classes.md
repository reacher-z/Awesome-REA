# Evidence classes (C0–C3 + Unknown, v4)

[简体中文](evidence-classes.zh-CN.md) · [Documentation](README.md)

Status: v4 Beta, generated automatically and reviewed by hand. Spec version: `evidence-class-v4`. Curated classifier: [`scripts/classify_evidence_classes.py`](../scripts/classify_evidence_classes.py). Data: [`data/evidence-classes.json`](../data/evidence-classes.json). Class 0 reviews: [`data/evidence-class-zero-reviews.json`](../data/evidence-class-zero-reviews.json).

This guide defines the **evidence class** and **reconstruction scope** shown for every curated catalog entry and for the automatically scanned repository index. It is a public-evidence rubric. **Class 0 is reserved for a manually confirmed full software reconstruction**; the automatic rubric never goes above Class 1.

Class, scope and runtime status are separate fields:

- `evidence_class`: 0–3; null when the source is unreadable
- `scope`: `full` / `partial` / `analysis` / `unknown` / `notes`
- `runtime_status`: always `not-run`
- `evidence_status`: `observed` / `unknown`

The homepage shows `C0`–`C3` / `?` badges on curated cards, a legend under the filters and an “Evidence class” filter. Class 0/1 entries with a documented demo show a preview image; a demo without an extractable screenshot shows “Demo available · no screenshot”.

The repository view shows a separate **scan evidence class** on automatically scanned cards. Scan classes use C1–C3 only, because `data/source-index.json` records README size and section signals but not release assets, demo media or runtime behaviour. Class 0 is never assigned from scan metadata.

## 1. Curated classes

| Class | Definition | Badge |
| --- | --- | --- |
| Class 0 | **A manually confirmed full software reconstruction** (`kind: case-study`): scope, target version and primary evidence were reviewed entry by entry and recorded in `data/evidence-class-zero-reviews.json`. | C0 |
| Class 1 | **Automatic maximum**: a download method and non-branding demo exist, but the scope is partial or the entry is not a software reconstruction (a tool, integration, guide or binary-analysis entry). | C1 |
| Class 2 | Demo or download is missing, but code and documentation exist; buildability remains unknown. | C2 |
| Class 3 | No code or no documentation: notes, progress records or partial fragments only. | C3 |
| Unknown | The source was unavailable or unreadable at review time. | ? |

## 2. Curated signals

Only public content behind the entry URL is used (GitHub REST, GitLab REST or a page fetch):

| Signal | Meaning |
| --- | --- |
| `code` | The URL is a code repository, or the page links to one. |
| `docs` / `docs_full` | README or page text is at least 400 bytes; headings cover installation/build and usage. |
| `download` | Release **assets**, a direct executable artifact, or a package command that installs **the target software itself** (the package name must match the repository). |
| `download_links` | Concrete download links and install commands found in the README, linked documents such as `docs/INSTALL.md`, and the distribution pages the README points at. Project homepages alone do not count. |
| `demo` | A non-branding raster screenshot, video-platform link or demo/playable link. |

Not a download: a release tag without assets; a build dependency such as `pip install ninja` when the repository is `foo`.
Not a demo: logos, badges, chat invitations, progress charts or CI/release badges.

Decision order:

1. No code or no docs → **Class 3**
2. Code and docs, but missing demo or download → **Class 2**
3. Download and demo both exist → automatic maximum **Class 1**
4. **Class 0 is manual only**: the review file records `scope: full`, and the entry has code, docs, download, demo, `kind: case-study` and no `binary` target.

## 3. Scan classes

The scan mapping is written to [`data/scan-evidence-classes.json`](../data/scan-evidence-classes.json) by [`scripts/classify_scan_evidence.py`](../scripts/classify_scan_evidence.py). It reads the committed scan snapshot and public supplement batches without fetching anything.

| Scan class | Definition |
| --- | --- |
| Class 1 | README documents both installation and usage. Release assets, demo media and buildability remain unobserved. |
| Class 2 | README documentation exists, but installation or usage guidance was not found. |
| Class 3 | No usable README documentation was found. |
| Class 0 | Never assigned from scan metadata. |

A scan class describes README documentation.

## 4. Method and limits

- Read current distributions from the data files rather than copying them into prose:

  ```bash
  python3 - <<'PY'
  import collections, json
  curated = json.load(open('data/evidence-classes.json', encoding='utf-8'))
  scan = json.load(open('data/scan-evidence-classes.json', encoding='utf-8'))
  print('curated', curated['meta']['class_counts'], 'unknown', curated['meta']['unknown_count'])
  print('basis', collections.Counter(entry['basis'] for entry in curated['entries']))
  print('scan', scan['meta']['class_counts'], 'unknown', scan['meta']['unknown_count'])
  PY
  ```

- Class 0 is the intersection of `evidence_class == 0` and `scope: full` reviews. There are no per-entry class overrides outside the review file.
- The GitHub token is sent only to `api.github.com`; cross-origin redirects strip the authorization header. Ordinary page fetches carry no token.
- Demo filtering removes logos, badges, QR codes, chat groups and sponsorship links.
- Preview images are selected by [`scripts/build_evidence_previews.py`](../scripts/build_evidence_previews.py) into [`data/evidence-previews.json`](../data/evidence-previews.json). [`scripts/fetch_previews.py`](../scripts/fetch_previews.py) downloads them into `.cache/previews/` before the build, and `build_site.py` copies them into `previews/`; the page never hotlinks a third-party image.
- The single-entry review helper is [`scripts/verify_evidence_entry.py`](../scripts/verify_evidence_entry.py).

## 5. Regeneration

```bash
python3 scripts/classify_evidence_classes.py            # use the local evidence cache
python3 scripts/classify_evidence_classes.py --fresh    # refetch everything
python3 scripts/classify_evidence_classes.py --ids <id,...> --merge  # classify new catalog records only
python3 scripts/classify_scan_evidence.py               # deterministic over the scan snapshot
python3 scripts/build_evidence_previews.py                  # keeps an existing preview when a run finds no media
python3 scripts/build_evidence_previews.py --drop-missing   # drops previews this run did not find
python3 scripts/fetch_previews.py
python3 scripts/build_site.py
python3 scripts/verify_evidence_entry.py <entry-url>
```

`build_site.py` merges `evidence_class`, `evidence_status`, `scope`, `runtime_status`, `evidence_review` and preview fields into `catalog.json` / `catalog-index.json`, writes the compact `scan-classes.json` for the repository view, and fails when a curated entry is missing its class.
