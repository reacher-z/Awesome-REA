#!/usr/bin/env python3
"""Build the dependency-free static site from the two source catalogs."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlsplit
from xml.sax.saxutils import escape as xml_escape

from build_browse_pages import build_browse_pages
from build_discovery_pages import build_discovery_pages
from build_paper_pages import build_paper_pages
from build_readme import CATEGORIES
from build_survey import build_survey, discussion_sections
from build_entry_pages import build_entry_pages
from build_feed import build_feeds
from build_manifest import write_build_manifest
from data_downloads import build_data_downloads
from open_graph import website_node
from homepage_locales import HOMEPAGE_DESTINATIONS, localized_homepage
from artifact_links import with_artifact_links, with_curated_labels
from source_browser import write_source_browser
from localization import read_localizations, localized_records
from source_scope import apply_scope, read_scope
from public_source_supplements import (PUBLISHED_FILENAME, compose_published,
                                      copy_public_evidence, json_bytes, load_supplements, project_additions)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "site"
OUTPUT = ROOT / "dist"
SITE_URL = "https://awesomerea.org"
REPOSITORY_URL = "https://github.com/reacher-z/Awesome-REA"
TARGETS = {"website", "game", "app", "binary", "firmware", "protocol"}
FONT_AWESOME_ICONS = {
    "arrow": "arrow-right", "external": "arrow-up-right-from-square",
    "search": "magnifying-glass", "copy": "copy", "check": "check",
    "chevron": "chevron-down", "code": "code", "chip": "microchip",
    "phone": "mobile-screen", "box": "cube", "network": "diagram-project",
    "layers": "layer-group", "document": "file-lines", "book": "book-open",
    "terminal": "terminal", "github": "github", "globe": "globe", "gamepad": "gamepad",
}
# Brand icons are drawn from the Brands face; every other key comes from Classic Light.
FONT_AWESOME_BRANDS = {"github"}


def fontawesome_markup(html: str, stylesheet_url: str) -> str:
    html = html.replace('<html lang="en">', '<html lang="en" data-icon-set="fontawesome">')
    html = html.replace('<link rel="stylesheet" href="styles.css">', '<link rel="stylesheet" href="styles.css">\n  <link rel="stylesheet" href="' + stylesheet_url + '">')
    html = re.sub(r'<svg class="symbol-bank".*?</svg>', '', html, count=1, flags=re.DOTALL)

    def replace_icon(match: re.Match) -> str:
        attrs, key = match.group(1), match.group(2)
        class_match = re.search(r'class="([^"]*)"', attrs)
        classes = class_match.group(1) if class_match else "icon"
        return f'<span class="{classes} fa-symbol fa-{key}" aria-hidden="true"></span>'

    html = re.sub(r'<svg\b([^>]*)>\s*<use href="#i-([a-z-]+)"\s*/>\s*</svg>', replace_icon, html)
    return html


def subset_icon_font(source: Path, destination: Path, codepoints: set[int]) -> None:
    """Write a WOFF2 copy of a licensed face that keeps only the site's icon code points."""
    try:
        from fontTools import subset
        from fontTools.ttLib import TTLibError, woff2
    except ImportError:
        woff2 = None
    if woff2 is None or not woff2.haveBrotli:
        raise ValueError("Subsetting the licensed icon fonts requires fontTools with Brotli: pip install fonttools brotli")
    options = subset.Options()
    options.flavor = "woff2"
    # Keep every name record, including the copyright and license notices.
    options.name_IDs = ["*"]
    options.name_languages = ["*"]
    try:
        font = subset.load_font(str(source), options)
    except (TTLibError, OSError, AssertionError) as error:
        raise ValueError(f"Font Awesome input is not a readable font: {source.name}") from error
    with font:
        subsetter = subset.Subsetter(options)
        subsetter.populate(unicodes=codepoints)
        subsetter.subset(font)
        missing = codepoints - set(font.getBestCmap() or {})
        if missing:
            raise ValueError(f"Font Awesome subset of {source.name} is missing icons: " + ", ".join(f"U+{point:04X}" for point in sorted(missing)))
        subset.save_font(font, str(destination), options)


def configure_fontawesome(html: str, licensed_package: Path | None, assets_url: str | None = None, *, output: Path) -> str:
    """Embed licensed fonts only in ignored deployment output; keep source portable."""
    generated_css = output / "fontawesome.css"
    font_output = output / "fonts"
    font_names = ("fa-light-300.woff2", "fa-brands-400.woff2")
    if licensed_package is None:
        generated_css.unlink(missing_ok=True)
        for name in font_names:
            (font_output / name).unlink(missing_ok=True)
        if font_output.exists() and not any(font_output.iterdir()):
            font_output.rmdir()
        if assets_url:
            parsed = urlsplit(assets_url)
            if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or any(character.isspace() or character in '"<>' for character in assets_url):
                raise ValueError("Font Awesome assets URL must be an HTTPS base URL without credentials, query or fragment.")
            return fontawesome_markup(html, assets_url.rstrip("/") + "/fontawesome.css")
        return html

    css_files = [licensed_package / "css" / name for name in ("fontawesome.css", "brands.css", "light.css")]
    for path in css_files + [licensed_package / "webfonts" / name for name in font_names]:
        if not path.is_file():
            raise ValueError("Font Awesome input must include Classic Light, Brands, and their WOFF2 files.")
    font_css = "\n".join(path.read_text(encoding="utf-8") for path in css_files)
    codepoints = {}
    for key, icon_name in FONT_AWESOME_ICONS.items():
        match = re.search(r"\.fa-" + re.escape(icon_name) + r'\s*\{[^}]*--fa:\s*"\\([0-9a-fA-F]+)"', font_css)
        if not match:
            raise ValueError(f"Required Font Awesome icon is missing: {icon_name}")
        codepoints[key] = match.group(1)
    font_output.mkdir(exist_ok=True)
    # Ship only the glyphs the site draws instead of the complete faces.
    light = {int(point, 16) for key, point in codepoints.items() if key not in FONT_AWESOME_BRANDS}
    brands = {int(codepoints[key], 16) for key in FONT_AWESOME_BRANDS}
    for name, points in zip(font_names, (light, brands)):
        subset_icon_font(licensed_package / "webfonts" / name, font_output / name, points)
    copyright_header = "/*! Font Awesome Pro by Fonticons, Inc. https://fontawesome.com — Commercial License: https://fontawesome.com/license. Licensed website assets; do not redistribute in a public source repository. */\n"
    css = copyright_header + """
@font-face{font-family:'AwesomeREA Icons';font-style:normal;font-weight:300;font-display:block;src:url('fonts/fa-light-300.woff2') format('woff2')}
@font-face{font-family:'AwesomeREA Brands';font-style:normal;font-weight:400;font-display:block;src:url('fonts/fa-brands-400.woff2') format('woff2')}
.fa-symbol{display:inline-flex;align-items:center;justify-content:center;font-family:'AwesomeREA Icons';font-weight:300;font-style:normal;font-size:20px;line-height:1;text-rendering:auto;-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}
.fa-symbol.icon-small{font-size:14px}.fa-symbol::before{display:block;line-height:1}.fa-symbol.fa-github{font-family:'AwesomeREA Brands';font-weight:400}
.target-link>.fa-symbol{font-size:19px}.card-icon>.fa-symbol{font-size:18px}.trace-target>.fa-symbol{font-size:24px}.card-title-link .fa-symbol{font-size:11px;display:inline-block}.card-footer .fa-symbol{font-size:10px}.button>.fa-symbol{font-size:17px}.search-box>.fa-symbol{font-size:21px}
"""
    css += "\n".join('.fa-' + key + '::before{content:"\\' + codepoint + '"}' for key, codepoint in codepoints.items())
    generated_css.write_text(css + "\n", encoding="utf-8")
    return fontawesome_markup(html, "fontawesome.css")



def group_for(record: dict) -> str:
    relationship = record["relationship"]
    if relationship == "independent-reconstruction":
        return "cases"
    if relationship == "independent-agent-integration":
        return "agents"
    if relationship == "foundation":
        return "tools"
    if relationship in {"learning", "community-learning-resource", "upstream-maintainer-companion-list"}:
        return "learn"
    return "rea"


def default_targets(record: dict) -> list[str]:
    """Conservative domain labels, never an assertion of REA compatibility."""
    category = record["category"]
    text = " ".join(str(record.get(k, "")) for k in ("id", "name", "description_en")).lower()
    if category == "core":
        # New target capabilities must not silently widen historical core labels.
        return ["app", "binary", "firmware", "game", "website"]
    found: set[str] = set()
    if category in {"javascript-electron", "android", "dotnet", "jvm"} or any(w in text for w in ("electron", "android", "aegis", "notion", "managed-code")):
        found.add("app")
    if category == "webassembly" or any(w in text for w in ("browser", "network capture", "web capture", "javascript", "webcrack")):
        found.add("website")
    if category == "firmware" or "firmware" in text:
        found.add("firmware")
    if category == "protocol-analysis":
        found.add("protocol")
    if any(w in text for w in ("dx-ball", "th04", "game", "unity")):
        found.add("game")
    if category in {"native-analysis", "dynamic-analysis", "binary-libraries", "binary-diffing", "agent-mcp", "agent-workflows", "learning"} or "native" in text:
        found.add("binary")
    return sorted(found or {"binary"})


def build_site(output: Path, *, fontawesome_dir: Path | None = None,
               fontawesome_assets_url: str | None = None) -> tuple[int, int, int]:
    """Render a complete site into a fresh, caller-owned staging directory."""
    translations = json.loads((SOURCE / "translations.zh-CN.json").read_text(encoding="utf-8"))
    papers = json.loads((ROOT / "data" / "papers.json").read_text(encoding="utf-8"))
    resources = []
    for filename in ("rea-resources.json", "tool-resources.json"):
        for original in json.loads((ROOT / "data" / filename).read_text(encoding="utf-8")):
            record = dict(original)
            if isinstance(record["requirements"], str):
                record["requirements"] = [record["requirements"]]
            translation = translations.get(record["id"], {})
            record["requirements_zh"] = record.get("requirements_zh") or translation.get("requirements", record["requirements"])
            record["name_zh"] = record.get("name_zh") or translation.get("name", record["name"])
            record["group"] = group_for(record)
            targets = record.get("targets") or default_targets(record)
            if not isinstance(targets, list) or not set(targets).issubset(TARGETS):
                raise ValueError(f"Invalid targets: {record['id']}")
            record["targets"] = sorted(set(targets))
            resources.append(record)
    ids = [r["id"] for r in resources]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate catalog IDs")
    latest_review = max(record["verified_at"] for record in resources)
    metadata = {"site_url": SITE_URL, "repository_url": REPOSITORY_URL, "resource_count": len(resources), "independent_integration_count": sum(r["group"] == "agents" for r in resources), "latest_review": latest_review, "verification_note": "Curated resource descriptions are reviewed against primary sources. The broader repository index is collected automatically."}
    output.mkdir()
    for path in SOURCE.iterdir():
        if path.name == "translations.zh-CN.json":
            continue
        if path.is_dir():
            shutil.copytree(path, output / path.name)
        else:
            shutil.copy2(path, output / path.name)
    html = (output / "index.html").read_text(encoding="utf-8")
    for key, value in {"RESOURCE_COUNT": len(resources), "INTEGRATION_COUNT": metadata["independent_integration_count"], "REVIEWED_AT": latest_review}.items():
        html = html.replace("{{" + key + "}}", str(value))
    html = configure_fontawesome(html, fontawesome_dir, fontawesome_assets_url, output=output)
    source_index_path = ROOT / "data" / "source-index.json"
    source_index_output = output / "source-index.json"
    browse_document = None
    metadata["source_index"] = {"available": False, "resource_count": 0}
    if source_index_path.is_file():
        try:
            index_data = json.loads(source_index_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print("Optional source index is not a complete JSON snapshot yet; using the curated collection only.")
        else:
            successful = [record for record in index_data.get("resources", []) if record.get("scan_status") == "readme-scanned"]
            if successful:
                repository_locales = read_localizations(ROOT)
                index_data["resources"] = apply_scope(localized_records(successful, repository_locales), read_scope(ROOT))
                link_diagnostics = []
                index_data["resources"] = with_artifact_links(index_data["resources"], papers, resources, link_diagnostics)
                index_data["resources"] = with_curated_labels(index_data["resources"], resources)
                for message in link_diagnostics:
                    print('Related entry: ' + message)
                index_data["meta"]["source_description_policy"] = index_data["meta"].get("description_policy", "")
                index_data["meta"]["description_policy"] = "English and Simplified Chinese descriptions are AI-assisted localizations of retained upstream repository text. description_original preserves retained text; oversized new descriptions are omitted with length and SHA-256 evidence in description_omission. Translation does not imply verification."
                excluded_count = sum(record.get("scope_status") == "excluded" for record in index_data["resources"])
                index_data["meta"]["scope"] = {"scanned_count": len(successful), "excluded_count": excluded_count, "browse_count": len(successful) - excluded_count}
                index_data["meta"]["localization"] = {"languages": ["en", "zh-CN"], "translated_records": sum(record["id"] in repository_locales for record in successful), "method": "AI-assisted description translation; available upstream text retained, with explicit fingerprints for oversized descriptions omitted from new captures."}
                browse_document = index_data
                index_meta = index_data.get("meta", {})
                metadata["source_index"] = {"available": True, "resource_count": len(successful) - excluded_count, "scanned_count": len(successful), "excluded_count": excluded_count, "status": index_meta.get("status", ""), "completed_at": index_meta.get("completed_at"), "verification": "automated-readme-scan"}
                source_index_output.write_text(json.dumps(index_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                canonical_export = source_index_output.read_bytes()
                supplements = load_supplements(ROOT)
                if supplements['ready']:
                    additions = project_additions(supplements)
                    additions = with_curated_labels(with_artifact_links(additions, papers, resources), resources)
                    browse_document = compose_published(canonical_export,
                        hashlib.sha256(source_index_path.read_bytes()).hexdigest(), supplements, additions)
                    published_export = json_bytes(browse_document)
                    (output / PUBLISHED_FILENAME).write_bytes(published_export)
                    copy_public_evidence(ROOT, output, supplements)
                    scope = browse_document['meta']['scope']
                    metadata['source_index'] = {
                        'available': True, 'resource_count': scope['browse_count'],
                        'scanned_count': scope['scanned_count'], 'excluded_count': scope['excluded_count'],
                        'status': 'published-selection', 'publication_schema_version': 2,
                        'published_at': browse_document['meta']['published_at'],
                        'full_export': PUBLISHED_FILENAME, 'verification': 'automated-readme-scan',
                    }
                    html = html.replace('href="source-index.json"', 'href="source-published.json"')
                    html = html.replace('data-i18n="downloadSourceData"', 'data-i18n="downloadPublishedSourceData"')
                    write_source_browser(output, published_export)
                else:
                    write_source_browser(output, canonical_export)
    if not metadata["source_index"]["available"]:
        source_index_output.unlink(missing_ok=True)
        write_source_browser(output, None)
    topic_labels_path = SOURCE / "topics.i18n.json"
    topic_labels = json.loads(topic_labels_path.read_text(encoding="utf-8")) if topic_labels_path.exists() else {}
    metadata["paper_count"] = len(papers)
    # The homepage reads category labels from here, so filters, cards and entry pages share one wording.
    category_labels = {category: list(labels) for category, labels in CATEGORIES.items()}
    catalog = {"meta": metadata, "resources": resources, "topic_labels": topic_labels, "category_labels": category_labels}
    (output / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "papers.json").write_text(json.dumps(papers, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in {"BROWSE_COUNT": metadata["source_index"]["resource_count"], "SCANNED_COUNT": metadata["source_index"].get("scanned_count", 0), "PAPER_COUNT": len(papers)}.items():
        html = html.replace("{{" + key + "}}", f"{value:,}")
    navigation = [(path, names[0]) for path, names in HOMEPAGE_DESTINATIONS.items()]
    structured = {"@context": "https://schema.org", "@graph": [
        website_node(SITE_URL, REPOSITORY_URL),
        {"@type": "CollectionPage", "@id": SITE_URL + "/#collection", "url": SITE_URL + "/", "name": "Awesome Reverse Engineering Anything", "inLanguage": "en", "isPartOf": {"@id": SITE_URL + "/#website"}, "description": "An independent collection of reverse-engineering tools, projects, case studies and research papers for websites, games, apps, binaries, firmware and communication protocols.", "mainEntity": {"@type": "ItemList", "numberOfItems": len(navigation), "itemListElement": [{"@type": "ListItem", "position": i, "name": name, "url": f"{SITE_URL}/{path}/"} for i, (path, name) in enumerate(navigation, 1)]}}
    ]}
    html = html.replace("</head>", '<script type="application/ld+json">' + json.dumps(structured, ensure_ascii=False).replace("<", "\\u003c") + '</script>\n</head>')
    asset_hrefs = {}
    for filename, attribute in (("app.js", "src"), ("styles.css", "href"), ("favicon.svg", "href")):
        revision = hashlib.sha256((output / filename).read_bytes()).hexdigest()[:16]
        asset_hrefs[filename] = f'/{filename}?v={revision}'
        html = html.replace(f'{attribute}="{filename}"', f'{attribute}="{filename}?v={revision}"')
    html = html.replace('src="favicon.svg"', f'src="{asset_hrefs["favicon.svg"]}"')
    social_revision = hashlib.sha256((output / "social-card.png").read_bytes()).hexdigest()[:16]
    html = html.replace(f'{SITE_URL}/social-card.png"', f'{SITE_URL}/social-card.png?v={social_revision}"')
    data_digest = hashlib.sha256()
    for filename in ("catalog.json", "source-index.json", "source-published.json", "source-browser.json", "papers.json"):
        path = output / filename
        if path.is_file():
            data_digest.update(filename.encode("utf-8") + b"\0" + path.read_bytes())
    data_revision = data_digest.hexdigest()[:16]
    html = html.replace('<html ', f'<html data-catalog-revision="{data_revision}" ', 1)
    # Start the catalog request while the page parses. The URL and CORS mode match app.js's
    # fetch(dataURL("catalog.json")), so that fetch reuses this response; source-browser.json stays on demand.
    script_tag = f'<script src="{asset_hrefs["app.js"].lstrip("/")}" defer></script>'
    if html.count(script_tag) != 1:
        raise ValueError("Homepage needs exactly one deferred app.js script")
    html = html.replace(script_tag, f'<link rel="preload" href="/catalog.json?v={data_revision}" as="fetch" crossorigin>\n  ' + script_tag)
    # Both entry pages contain their own language before JavaScript runs.
    app_source = (SOURCE / "app.js").read_text(encoding="utf-8")
    (output / "index.html").write_text(localized_homepage(html, app_source, "en"), encoding="utf-8")
    (output / "zh").mkdir(exist_ok=True)
    (output / "zh/index.html").write_text(localized_homepage(html, app_source, "zh"), encoding="utf-8")
    browse_revision = hashlib.sha256((output / "browse.css").read_bytes()).hexdigest()[:16]
    icon_stylesheet = "/fontawesome.css" if fontawesome_dir else (fontawesome_assets_url.rstrip("/") + "/fontawesome.css" if fontawesome_assets_url else None)
    browse_urls = build_browse_pages(
        output, browse_document, curated_count=len(resources), site_url=SITE_URL,
        repository_url=REPOSITORY_URL, styles_href=asset_hrefs["styles.css"],
        browse_styles_href=f"/browse.css?v={browse_revision}",
        favicon_href=asset_hrefs["favicon.svg"],
        social_image_href=f"{SITE_URL}/social-card.png?v={social_revision}",
        data_revision=data_revision, icon_stylesheet_href=icon_stylesheet,
    )
    discovery_paths = build_discovery_pages(output, catalog, browse_document)
    papers_revision = hashlib.sha256((output / "papers.css").read_bytes()).hexdigest()[:16]
    paper_urls = build_paper_pages(
        output, papers, site_url=SITE_URL, repository_url=REPOSITORY_URL,
        styles_href=asset_hrefs["styles.css"], papers_styles_href=f"/papers.css?v={papers_revision}",
        favicon_href=asset_hrefs["favicon.svg"], social_image_href=f"{SITE_URL}/social-card.png?v={social_revision}",
        icon_stylesheet_href=icon_stylesheet,
    )
    survey_document = json.loads((ROOT / "data/survey.json").read_text(encoding="utf-8"))
    survey_urls = build_survey(
        output, papers, resources, document=survey_document,
        site_url=SITE_URL, repository_url=REPOSITORY_URL,
        styles_href=asset_hrefs["styles.css"], favicon_href=asset_hrefs["favicon.svg"],
        social_image_href=f"{SITE_URL}/social-card.png?v={social_revision}",
        icon_stylesheet_href=icon_stylesheet,
    )
    entry_revision = hashlib.sha256((output / "entry.css").read_bytes()).hexdigest()[:16]
    entry_urls = build_entry_pages(
        output, resources, papers, site_url=SITE_URL, repository_url=REPOSITORY_URL,
        styles_href=asset_hrefs["styles.css"], entry_styles_href=f"/entry.css?v={entry_revision}",
        favicon_href=asset_hrefs["favicon.svg"], social_image_href=f"{SITE_URL}/social-card.png?v={social_revision}",
        icon_stylesheet_href=icon_stylesheet, survey_discussions=discussion_sections(survey_document),
    )
    # Feeds list inclusion dates; they link from pages written above and are not sitemap pages.
    build_feeds(output, resources, papers, site_url=SITE_URL, repository_url=REPOSITORY_URL)
    (output / ".nojekyll").write_text("", encoding="utf-8")
    (output / "CNAME").write_text("awesomerea.org\n", encoding="utf-8")
    (output / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    # Review timestamps describe sources, not every page's modification date.
    # Omit lastmod rather than advertising a fabricated build-time freshness signal.
    sitemap_urls = [SITE_URL + "/", SITE_URL + "/zh/", *browse_urls, *(SITE_URL + path for path in discovery_paths), *paper_urls, *survey_urls, *entry_urls]
    sitemap_entries = [f'<url><loc>{xml_escape(url)}</loc></url>' for url in sitemap_urls]
    (output / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(sitemap_entries) + '\n</urlset>\n', encoding="utf-8")
    build_data_downloads(output, catalog, papers,
                         (output / 'papers/references.bib').read_text(encoding='utf-8'))
    write_build_manifest(output)
    return len(resources), len(papers), len(sitemap_urls)


def check_output_directory(output: Path) -> None:
    """Never follow a deployment-directory symlink or replace a non-directory."""
    if output.is_symlink() or (output.exists() and not output.is_dir()):
        raise ValueError("Deployment output must be a directory, not a symlink or file.")


def build_staged_site(*, fontawesome_dir: Path | None = None,
                      fontawesome_assets_url: str | None = None) -> tuple[int, int, int]:
    """Keep the previous deployment intact until generation and its manifest succeed."""
    check_output_directory(OUTPUT)
    # This directory stays ignored even if an interrupted rollback needs manual recovery.
    cache = OUTPUT.parent / ".cache"
    check_output_directory(cache)
    cache.mkdir(exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix="site-build-", dir=cache))
    staged, previous = workspace / "next", workspace / "previous"
    preserve_previous = False
    try:
        counts = build_site(staged, fontawesome_dir=fontawesome_dir,
                            fontawesome_assets_url=fontawesome_assets_url)
        check_output_directory(OUTPUT)
        try:
            if OUTPUT.exists():
                OUTPUT.rename(previous)
            if OUTPUT.exists() or OUTPUT.is_symlink():
                raise FileExistsError("Deployment output changed during replacement.")
            staged.rename(OUTPUT)
        except BaseException:
            if previous.exists():
                try:
                    if OUTPUT.exists() or OUTPUT.is_symlink():
                        raise FileExistsError("Deployment output changed before rollback.")
                    previous.rename(OUTPUT)
                except BaseException as error:
                    preserve_previous = True
                    raise RuntimeError(
                        "Could not restore the prior deployment; it is preserved in "
                        + ".cache/" + workspace.name + "/previous."
                    ) from error
            raise
        return counts
    finally:
        if not preserve_previous:
            # Only remove this invocation's temporary directory, never its parent.
            shutil.rmtree(workspace)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    icons = parser.add_mutually_exclusive_group()
    icons.add_argument("--fontawesome-dir", type=Path, help="Optional local licensed Font Awesome Pro package; copied only into ignored deployment output.")
    icons.add_argument("--fontawesome-assets-url", help="Trusted HTTPS origin/path serving the authorized Font Awesome deployment; no font files are downloaded or copied.")
    args = parser.parse_args()
    resources, papers, pages = build_staged_site(
        fontawesome_dir=args.fontawesome_dir,
        fontawesome_assets_url=args.fontawesome_assets_url,
    )
    print(f"Built {resources} curated resources, {papers} papers and {pages} indexable pages in dist/ ({SITE_URL})")


if __name__ == "__main__":
    main()
