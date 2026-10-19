# Website maintenance

**Canonical address:** [https://awesomerea.org](https://awesomerea.org). The display name is **AwesomeREA.org**. Search metadata uses one site name, **Awesome Reverse Engineering Anything**, with `AwesomeREA.org` and `Awesome REA` as alternate names in that order.

## Source and generated files

- [site/](../site/) contains the dependency-free HTML, CSS, JavaScript, favicon and social image. Update the SVG and PNG together when the illustration changes.
- [open_graph.py](../scripts/open_graph.py) writes the Open Graph and Twitter card tags for the homepage and every generated page, with `og:site_name` set to its `SITE_NAME`, with the image type and size read from `social-card.png` and a localized description of the card as its alt text. The 404 page has no `og:url`. The same module defines the WebSite node (`#website`): only the two homepages include it, and every other page's JSON-LD refers to it by `@id`. `validate_site.py` checks both against these constants.
- [rea-resources.json](../data/rea-resources.json) and [tool-resources.json](../data/tool-resources.json) are the resource sources. Keep bilingual descriptions, evidence links, prerequisites, review dates and target labels accurate.
- [translations.zh-CN.json](../site/translations.zh-CN.json) supplies Chinese resource names and prerequisites. New records also need translations here.
- [topics.i18n.json](../site/topics.i18n.json) supplies bilingual display labels for common repository topics. Canonical upstream topic IDs remain intact for links and exact filtering.
- [source-index.json](../data/source-index.json) supplies the broader repository collection from successful automated README fetches. Its counts and review status stay separate from the curated records. [Repository locale files](../data/locales/README.md) provide English and Simplified Chinese descriptions; the generated data also preserves the original upstream text. See [scan methodology](source-scan.md).
- [source-scope.json](../data/source-scope.json) removes clearly unrelated scan matches, duplicate README copies and repositories whose upstream is no longer available from browsing while keeping their original scan evidence in the full downloadable JSON. The footer offers separate repository-index and curated-catalog downloads.
- [source_browser.py](../scripts/source_browser.py) generates compact `source-browser.json` for interactive search. It contains eligible records in the same order, with bilingual/original-text search, card details and evidence annotations. The full `/source-index.json` download remains complete, including excluded records, failures and discovery history. The browser payload records the full export's SHA-256 and is checked against it during the build.
- [build_site.py](../scripts/build_site.py) combines the catalogs, derives counts, copies the site assets, and generates `catalog.json`, `robots.txt`, `sitemap.xml`, `CNAME` and `.nojekyll` in `dist/`.
- [build_browse_pages.py](../scripts/build_browse_pages.py) emits 20 static category pages under `/browse/` and `/zh/browse/`. These include full localized repository content without JavaScript, reciprocal language links, canonical URLs, and sitemap entries. Counts and scope exclusions use the same data as search.
- [build_discovery_pages.py](../scripts/build_discovery_pages.py) emits bilingual `/resources/` and `/about/` pages, evidence and review dates for curated entries, structured metadata, and the optional `llms.txt` navigation index. The homepage and browse pages link to these pages.
- [build_survey.py](../scripts/build_survey.py) renders the bilingual editorial survey at `/survey/` and `/zh/survey/`, plus repository-citation and paper-reference BibTeX downloads. The Cite action uses the collection identity and author order from `CITATION.cff`, without inventing a repository release date or version; `/survey/citation.bib` remains the compatible download URL. [survey.json](../data/survey.json) freezes its corpus and cited source records independently of future catalog updates. The survey is not a research-paper record and does not increase the paper count. Update both languages, source evidence and version together when revising its argument; the homepage, README and `llms.txt` link to it.
- [build_entry_pages.py](../scripts/build_entry_pages.py) emits one English/Chinese detail-page pair for each curated resource and paper: `/resources/<id>/`, `/papers/<id>/` and their `/zh/` counterparts. These pages retain complete reviewed descriptions, requirements or research limits, original source links and citation metadata. They describe the catalog entry; they do not replace the upstream project or paper.
- `/cases/` and `/zh/cases/` provide a compact subject index of the existing case-study records. Complete descriptions remain visible; native disclosures retain requirements, evidence and review dates. The homepage and README link directly to this bilingual collection view.
- Static collection lists and related-entry links lead to these detail pages using ordinary links. Existing `/resources/#<id>` and `/papers/#<id>` listing anchors remain available. The paper directory's Layout control keeps cards as the default; `?layout=compact` (carried by the language link) shows one row per paper and moves its authors and scope box into the bibliographic details, without duplicating them. The automated repository index continues to use category pages and does not generate individual pages for scanned repositories.
- [validate_discovery.py](../scripts/validate_discovery.py) checks the generated site's canonical routes, language links, static record coverage, JSON-LD and crawler permissions. The production build and CI both run it. See [search discovery](search-discovery.md) for sources, submission steps, and measurement limits.
- `dist/` is ignored by Git. Rebuild it from source instead of editing generated files. The resource count is a count of catalog records, not distinct software projects.
- Builds generate a fresh site in ignored `.cache/` storage before replacing `dist/`, so removed source assets do not survive a rebuild. A generation or manifest failure leaves the previous output intact. If replacement fails, the builder restores the previous directory; if restoration also fails, it reports the retained recovery directory. Treat all files inside `dist/` as generated output, not a place for unrelated files.

## Build and preview

Run from the repository root with Python 3.10+ and Node.js available:

```sh
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
python3 scripts/build_site.py
node --check site/app.js
python3 -m http.server 8000 --bind 127.0.0.1 --directory dist
```

The test command runs every Python test and the Node tests of the browser scripts offline; CI runs the same command. The [browser smoke test](#browser-smoke-test) is a separate step.

Open `http://127.0.0.1:8000`. Use HTTP rather than opening `index.html` directly, because the directory fetches `catalog.json` and `source-browser.json`. Stop the preview server with Ctrl+C.

After source, locale, scope, curated-record or paper edits, regenerate the [GitHub browsing directory](repositories/README.md) with `python3 scripts/build_repository_index.py` before validation. It also updates the counts and directory links in both root READMEs. A repository line whose exact GitHub repository is a curated entry's URL or a paper's code or project URL ends with a “Curated” or “Paper” link to that page, using the same matching as the website's related links; `--check` fails when these markers are stale.

The bare homepage always opens in English. Use `/zh/` or the header language links to open Chinese; old browser preferences do not override the default. Generated pages link to `/zh/` routes, while existing `?lang=zh` links still render Chinese.

Before publication, check English and Chinese at desktop and 390 px widths: search, all filter types, empty results, clearing filters, loading more, prerequisite expansion, keyboard focus and the language links. Confirm repository descriptions change language alongside the interface, including filtered and newly loaded cards. Check translated prerequisites and empty-description fallbacks, and confirm the canonical URL, social image URLs, `CNAME`, robots and sitemap agree on `awesomerea.org`. The browser smoke test below automates part of this list; it does not replace the review.

The validators derive the sitemap inventory from collection routes, category definitions and current curated/paper IDs. Adding or removing a reviewed entry changes two detail URLs; there is no fixed page-count limit. Checks require exact detail IDs, complete localized content, ordinary listing links, reciprocal languages, self-canonicals and source-bound structured data. The entry builder removes only obsolete pages carrying its own generated-page marker and preserves listing pages and citation downloads.

Review the exact `dist/` payload for credentials, account identifiers, administrative URLs, personal filesystem paths and unrelated files. The public catalog should contain public source links only. Publish generated assets, never an entire working directory or `.git` folder. `source-reviewed` describes a check of the resource's documentation; it does not assert that every listed tool has been executed.

### Browser smoke test

[smoke.cjs](../tests/browser/smoke.cjs) rebuilds `dist/` with the public fallback icons, serves it on `127.0.0.1` with the [site/_headers](../site/_headers) rules, and loads it in an installed headless Chrome or Chromium at 1280 px and 390 px. Requests to any other origin are blocked. Both homepages and a set of collection, about, browse and detail pages must load without console errors, Content Security Policy violations, failed local requests or horizontal page overflow. On each homepage it also checks the initial curated and repository card counts and status totals against the built JSON, a search-and-clear cycle, Show More in both views, requirement expansion, and a language switch that keeps a target filter and the fragment. It also checks that the catalog arrives through its preload in one request while `source-browser.json` waits for the Repositories view, and that arrow keys on the language links never navigate. With JavaScript disabled, both homepages must show no search or filter controls and no loading text, with the static directory links under the collection heading.

```sh
npm ci --prefix tests/browser --ignore-scripts
node tests/browser/smoke.cjs
```

The pinned `puppeteer-core` package drives the installed browser and downloads none; set `CHROME_PATH` when Chrome is not in a standard location. Without a browser or the package, the test prints the reason and skips locally, while CI fails. Screenshots are written to the ignored `.cache/browser-smoke/` directory, and CI keeps them as the `browser-smoke-screenshots` workflow artifact for 14 days. They are for people to inspect: the test does not compare images, approve the visual design, or open any linked resource.

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

The canonical host is `awesomerea.org`. The Cloudflare Single Redirect named **Canonical www to apex** matches `(http.host eq "www.awesomerea.org")` and returns **301** with the dynamic target `concat("https://awesomerea.org", http.request.uri.path)` and **Preserve query string** enabled. Keep the existing `www` DNS record proxied so the rule runs. This hostname rule is configured at the Cloudflare edge; Pages `_redirects` does not support host matching. [Single Redirects](https://developers.cloudflare.com/rules/url-forwarding/single-redirects/), [Pages domain redirect guidance](https://developers.cloudflare.com/pages/how-to/www-redirect/).

Include these checks after deployment or domain changes:

```sh
curl --head --silent 'https://www.awesomerea.org/papers/?x=1'
curl --location --silent --output /dev/null --write-out '%{http_code} %{url_effective} %{num_redirects}\n' 'http://www.awesomerea.org/'
```

The first request should return `301` and `location: https://awesomerea.org/papers/?x=1`. The second should end at `https://awesomerea.org/` with `200` in at most two redirects. Also check a localized path and repeated or encoded query parameters, and confirm the corresponding apex page still returns `200` without a hostname redirect.

[site/_headers](../site/_headers) adds site-wide security headers: a Content Security Policy, `X-Frame-Options: DENY`, a Permissions Policy that disables unused device features, and HSTS with a 30-day `max-age`. The policy allows only same-origin scripts, styles, images and JSON requests, plus the icon stylesheet and fonts from `https://awesome-rea.pages.dev`; `validate_site.py` fails the build if a page adds inline code, inline styles, frames or another asset origin. Cloudflare's same-origin email-decoding script is allowed, and so is Cloudflare Web Analytics, which the edge injects only on the production domain (its beacon from `https://static.cloudflareinsights.com` and its reports to `https://cloudflareinsights.com`); `validate_site.py` keeps both origins in the policy because built pages never show the beacon. Enabling Zaraz, JavaScript detections or any other injected script requires updating the policy first. `includeSubDomains` and `preload` need an owner decision about every subdomain before they are added.

Two absolute-URL rules in the same file add `X-Robots-Tag: noindex` to `https://:project.pages.dev/*` and `https://:version.:project.pages.dev/*`, so a project's `pages.dev` alias, its preview and branch deployments, and any Direct Upload of this build stay out of search results. They never match `awesomerea.org`, and `validate_site.py` fails if any path rule would send that header to the canonical host. [Cloudflare Pages headers](https://developers.cloudflare.com/pages/configuration/headers/).

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

### Icon origin contents

The `awesome-rea.pages.dev` project exists only to serve the licensed icon stylesheet and fonts. Deploy nothing else there: a full site copy answers every path, including unknown ones, with HTTP 200 duplicates of older pages. The deployment may contain only `fontawesome.css`, `fonts/fa-light-300.woff2`, `fonts/fa-brands-400.woff2`, a `404.html` and this build's `_headers`, which keeps the font CORS rules and adds the `pages.dev` noindex rules above. Do not redirect that host, because production pages load their icons from it. From a build made with `--fontawesome-dir`:

```sh
python3 - <<'PY'
from pathlib import Path
import shutil

origin = Path(".cache/icon-origin")
shutil.rmtree(origin, ignore_errors=True)
(origin / "fonts").mkdir(parents=True)
for name in ("fontawesome.css", "_headers", "fonts/fa-light-300.woff2", "fonts/fa-brands-400.woff2"):
    shutil.copy2(Path("dist") / name, origin / name)
(origin / "404.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="robots" content="noindex">'
                                 '<title>Not found</title><p>This host serves icon assets for <a href="https://awesomerea.org/">AwesomeREA.org</a>.</p></html>\n',
                                 encoding="utf-8")
PY
```

Replacing that deployment is a Cloudflare action: an authorized maintainer uploads `.cache/icon-origin/` to the Direct Upload project as a new production deployment. Keep the folder in the private artifact backup, never in this repository. Afterwards, `fontawesome.css` and both font URLs should return `200` with `Access-Control-Allow-Origin: *`, icons should still render on `https://awesomerea.org/`, the root, an old page path such as `/resources/ghidra/` and an unknown path should return `404`, every response should carry `X-Robots-Tag: noindex`, and `/sitemap.xml` should no longer exist there.

## Homepage languages and discovery

The build writes an English homepage at `/` and a complete Chinese homepage at `/zh/`. Each has its own canonical URL, localized title and description, and reciprocal `hreflang` links. Both routes appear in the sitemap. The header shows an English / 简体中文 link pair inside a group with a localized name; the current language has `aria-current="true"`. The build points each link at its own homepage, so switching works without JavaScript, and app.js keeps both links in step with the query, layout and fragment whenever the URL changes. Arrow keys never navigate. Existing `?lang=zh` links remain readable; the language links drop `lang`, because the path selects the language.

Homepage navigation and featured collection links are ordinary HTML links, available before JavaScript runs. Without scripting, `@media (scripting: none)` hides the search field, filters, selects, tabs and layout control, and the status lines start empty; the noscript note under the collection heading links the static repository directory, curated collection and papers instead. Each homepage preloads `/catalog.json?v=<data revision>` with `as="fetch" crossorigin`, the exact request app.js makes, so the catalog downloads while the page parses; `validate_site.py` fails if the preload and `data-catalog-revision` diverge. `source-browser.json` is not preloaded and loads only with the Repositories view. Search uses the curated catalog by default; `?view=source-index` explicitly opens the automated repository index. Both views share the contributor credits. Font Awesome Pro continues to load through the configured authorized asset origin; no licensed font binaries are committed.

When a nonblank curated query has no matches, readers can continue with the same query in the active language's paper directory or the available repository index. The paper link opens the existing bibliography search; the repository action retains its automatic-index label. Offering these actions does not fetch either collection or promise a match.

The interactive catalog defaults to a compact list. The Layout control switches between compact rows and cards without rebuilding results, so expanded details and current filters stay in place. `?layout=cards` shares the card layout; omitting it uses the compact list. The choice travels with language links. Compact repository rows keep related entries and clickable topics inside Details; descriptions remain complete at the same reading size.
