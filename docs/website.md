# Website maintenance

**Canonical address:** [https://awesomerea.org](https://awesomerea.org). The display name is **AwesomeREA.org**.

## Source and generated files

- [site/](../site/) contains the dependency-free HTML, CSS, JavaScript, favicon and social image. Update the SVG and PNG together when the illustration changes.
- [rea-resources.json](../data/rea-resources.json) and [tool-resources.json](../data/tool-resources.json) are the resource sources. Keep bilingual descriptions, evidence links, prerequisites, review dates and target labels accurate.
- [translations.zh-CN.json](../site/translations.zh-CN.json) supplies Chinese resource names and prerequisites. New records also need translations here.
- [topics.i18n.json](../site/topics.i18n.json) supplies bilingual display labels for common repository topics. Canonical upstream topic IDs remain intact for links and exact filtering.
- [source-index.json](../data/source-index.json) supplies the broader repository collection from successful automated README fetches. Its counts and review status stay separate from the curated records. [Repository locale files](../data/locales/README.md) provide English and Simplified Chinese descriptions; the generated data also preserves the original upstream text. See [scan methodology](source-scan.md).
- [source-scope.json](../data/source-scope.json) removes clearly unrelated scan matches from browsing while keeping their original scan evidence in the full downloadable JSON. The footer offers separate repository-index and curated-catalog downloads.
- [source_browser.py](../scripts/source_browser.py) generates compact `source-browser.json` for interactive search. It contains eligible records in the same order, with bilingual/original-text search, card details and evidence annotations. The full `/source-index.json` download remains complete, including excluded records, failures and discovery history. The browser payload records the full export's SHA-256 and is checked against it during the build.
- [build_site.py](../scripts/build_site.py) combines the catalogs, derives counts, copies the site assets, and generates `catalog.json`, `robots.txt`, `sitemap.xml`, `CNAME` and `.nojekyll` in `dist/`.
- [build_browse_pages.py](../scripts/build_browse_pages.py) emits 20 static category pages under `/browse/` and `/zh/browse/`. These include full localized repository content without JavaScript, reciprocal language links, canonical URLs, and sitemap entries. Counts and scope exclusions use the same data as search.
- [build_discovery_pages.py](../scripts/build_discovery_pages.py) emits bilingual `/resources/` and `/about/` pages, evidence and review dates for curated entries, structured metadata, and the optional `llms.txt` navigation index. The homepage and browse pages link to these pages.
- [validate_discovery.py](../scripts/validate_discovery.py) checks the generated site's canonical routes, language links, static record coverage, JSON-LD and crawler permissions. The production build and CI both run it. See [search discovery](search-discovery.md) for sources, submission steps, and measurement limits.
- `dist/` is ignored by Git. Rebuild it from source instead of editing generated files. The resource count is a count of catalog records, not distinct software projects.

## Build and preview

Run from the repository root with Python 3.10+ and Node.js available:

```sh
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
python3 scripts/build_site.py
node --check site/app.js
python3 -m http.server 8000 --bind 127.0.0.1 --directory dist
```

The test command runs every Python and browser test offline; CI runs the same command.

Open `http://127.0.0.1:8000`. Use HTTP rather than opening `index.html` directly, because the directory fetches `catalog.json` and `source-browser.json`. Stop the preview server with Ctrl+C.

After source, locale, or scope edits, regenerate the [GitHub browsing directory](repositories/README.md) with `python3 scripts/build_repository_index.py` before validation. It also updates the counts and directory links in both root READMEs.

The bare homepage always opens in English. Use `/zh/` or the language selector to open Chinese; old browser preferences do not override the default. Generated pages link to `/zh/` routes, while existing `?lang=zh` links still render Chinese.

Before publication, check English and Chinese at desktop and 390 px widths: search, all filter types, empty results, clearing filters, loading more, prerequisite expansion, keyboard focus and the language selector. Confirm repository descriptions change language alongside the interface, including filtered and newly loaded cards. Check translated prerequisites and empty-description fallbacks, and confirm the canonical URL, social image URLs, `CNAME`, robots and sitemap agree on `awesomerea.org`.

Review the exact `dist/` payload for credentials, account identifiers, administrative URLs, personal filesystem paths and unrelated files. The public catalog should contain public source links only. Publish generated assets, never an entire working directory or `.git` folder. `source-reviewed` describes a check of the resource's documentation; it does not assert that every listed tool has been executed.

### Optional licensed production icons

The public source provides SVG fallback icons for the collection interface. A maintainer with an appropriate Font Awesome Pro license can opt into Classic Light and Brands from a local licensed package:

```sh
python3 scripts/build_site.py --fontawesome-dir ../licensed-fontawesome-pro
```

This adds two local WOFF2 files and minimal icon CSS only to ignored `dist/` output. It does not copy the Pro package or its installation path into public source. A normal build without this option restores the fallback and removes those generated font assets. Keep licensed production outputs in the private artifact backup and authorized website deployment; do not commit Pro assets to the public repository. See [Font Awesome's Pro license](https://origin.fontawesome.com/license) and [official support guidance](https://fontawesome.com/support).

CI can instead reference the collection's existing authorized static icon deployment without downloading or copying Pro files:

```sh
python3 scripts/build_production.py --fontawesome-assets-url https://awesome-rea.pages.dev
```

`Catalog checks` runs this exact command on every pull request and push to `main`. The asset URL is only written into the generated HTML; the build does not fetch it. The local-package and asset-URL options are mutually exclusive. The asset origin must continue serving `fontawesome.css` and its two relative `fonts/` URLs with font CORS enabled. Keep that Direct Upload project available while production uses it; [site/_headers](../site/_headers) supplies the corresponding public asset headers.

## Hosting

The website uses **Cloudflare Pages**. Keep this collection's source public; `Awesome-REA/awesome-rea.github.io` is reserved for **private artifact backups**, independently of the hosting service. Confirm its visibility when maintaining that backup. GitHub Free for organizations supports Pages from public repositories; private-repository Pages requires a qualifying paid plan. [GitHub Pages availability](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages).

For automatic deployment, connect the public source repository through Pages Git integration, select the production branch, use the asset-URL build command above, and set the output directory to `dist`. The build starts at the repository root and needs Python 3.10+. Git integration can build and deploy pushed changes without storing a separate deployment token in this repository. Confirm the deployed commit and domain state after configuring the integration. [Official Git integration instructions](https://developers.cloudflare.com/pages/get-started/git-integration/).

## Direct Upload for the icon origin or a manual deployment

Build first. Cloudflare accepts a folder or ZIP through drag and drop; Wrangler accepts the asset folder. Direct Upload is a different project mode from Git integration. [Official Direct Upload instructions](https://developers.cloudflare.com/pages/get-started/direct-upload/).

To create a ZIP whose `index.html` is at the archive root:

```sh
python3 - <<'PY'
from pathlib import Path
import shutil

Path(".cache").mkdir(exist_ok=True)
shutil.make_archive(".cache/awesomerea-site", "zip", "dist")
PY
```

An authorized maintainer can open the intended Pages Direct Upload project, create a production deployment, and upload `.cache/awesomerea-site.zip` or the `dist/` folder. Do not wrap the assets in an extra `dist/` directory inside the ZIP. Alternatively, use an authenticated Wrangler session and select the intended project:

```sh
npx wrangler pages deploy dist
```

After deployment, verify the returned deployment URL, then confirm the custom-domain and DNS configuration for `awesomerea.org`. A generated `CNAME` file or a successful local build does not establish hosting, DNS or TLS status. Keep hosting credentials outside the repository; only the approved static artifacts belong in the optional backup repository.

## Homepage languages and discovery

The build writes an English homepage at `/` and a complete Chinese homepage at `/zh/`. Each has its own canonical URL, localized title and description, and reciprocal `hreflang` links. Both routes appear in the sitemap. The language control preserves query filters and the current fragment when moving between these routes; existing `?lang=zh` links remain readable.

Homepage navigation and featured collection links are ordinary HTML links, available before JavaScript runs. Search uses the curated catalog by default; `?view=source-index` explicitly opens the automated repository index. Both views share the contributor credits. Font Awesome Pro continues to load through the configured authorized asset origin; no licensed font binaries are committed.

The interactive catalog defaults to a compact list. The Layout control switches between compact rows and cards without rebuilding results, so expanded details and current filters stay in place. `?layout=cards` shares the card layout; omitting it uses the compact list. The choice travels with language links. Compact repository rows keep related entries and clickable topics inside Details; descriptions remain complete at the same reading size.
