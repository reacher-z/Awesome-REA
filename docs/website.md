# Website maintenance

**Canonical address:** [https://awesomerea.org](https://awesomerea.org). The display name is **AwesomeREA.org**.

## Source and generated files

- [site/](../site/) contains the dependency-free HTML, CSS, JavaScript, favicon and social image. Update the SVG and PNG together when the illustration changes.
- [rea-resources.json](../data/rea-resources.json) and [tool-resources.json](../data/tool-resources.json) are the resource sources. Keep bilingual descriptions, evidence links, prerequisites, review dates and target labels accurate.
- [translations.zh-CN.json](../site/translations.zh-CN.json) supplies Chinese resource names and prerequisites. New records also need translations here.
- When [source-index.json](../data/source-index.json) is present, a separate **Source index** mode lists successful automated README fetches. Its counts stay separate from the curated guide. Upstream descriptions retain their original language, including in the Chinese interface. See [scan methodology](source-scan.md).
- [build_site.py](../scripts/build_site.py) combines the catalogs, derives counts, copies the site assets, and generates `catalog.json`, `robots.txt`, `sitemap.xml`, `CNAME` and `.nojekyll` in `dist/`.
- `dist/` is ignored by Git. Rebuild it from source instead of editing generated files. The resource count is a count of catalog records, not distinct software projects.

## Build and preview

Run from the repository root with Python 3.10+ and Node.js available:

```sh
python3 scripts/validate.py
python3 scripts/build_site.py
node --check site/app.js
python3 -m http.server 8000 --bind 127.0.0.1 --directory dist
```

Open `http://127.0.0.1:8000`. Use HTTP rather than opening `index.html` directly, because the directory loads `catalog.json` with `fetch`. Stop the preview server with Ctrl+C.

Before publication, check English and Chinese at desktop and 390 px widths: search, all filter types, empty results, clearing filters, loading more, prerequisite expansion, keyboard focus and command-copy feedback. Confirm every record has translated prerequisites, and that the canonical URL, social image URLs, `CNAME`, robots and sitemap agree on `awesomerea.org`.

Review the exact `dist/` payload for credentials, account identifiers, administrative URLs, personal filesystem paths and unrelated files. The public catalog should contain public source links only. Publish generated assets, never an entire working directory or `.git` folder. `source-reviewed` describes documentation review; the lab's CLI execution and fixture tests are separate evidence.

### Optional licensed production icons

The public source uses original SVG fallback icons. A maintainer with an appropriate Font Awesome Pro license can opt into Classic Light and Brands from a local licensed package:

```sh
python3 scripts/build_site.py --fontawesome-dir ../licensed-fontawesome-pro
```

This adds two local WOFF2 files, minimal icon CSS and a footer credit only to ignored `dist/` output. It does not copy the Pro package or its installation path into public source. A normal build without this option restores the fallback and removes those generated font assets. Keep licensed production outputs in the private artifact backup and authorized website deployment; do not commit Pro assets to the public repository. See [Font Awesome's Pro license](https://origin.fontawesome.com/license) and [official support guidance](https://fontawesome.com/support).

CI can instead reference the collection's existing authorized static icon deployment without downloading or copying Pro files:

```sh
python3 scripts/build_site.py --fontawesome-assets-url https://awesome-rea.pages.dev
```

The local-package and asset-URL options are mutually exclusive. The asset origin must continue serving `fontawesome.css` and its two relative `fonts/` URLs with font CORS enabled. Keep that Direct Upload project available while production uses it; [site/_headers](../site/_headers) supplies the corresponding public asset headers.

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
