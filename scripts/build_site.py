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

from asset_paths import fingerprinted_href, remove_unhashed_copies
from build_browse_pages import build_browse_pages
from build_discovery_pages import build_discovery_pages
from build_paper_pages import build_paper_pages
from build_readme import CATEGORIES, collection_section
from build_repository_index import CATEGORIES as REPOSITORY_CATEGORIES
from build_survey import build_survey, discussion_sections
from build_entry_pages import build_entry_pages
from build_home import build_home
from build_feed import build_feeds
from build_api import build_api, write_api_pages
from agent_formats import full_catalog_markdown
from build_discovery_pages import SECTIONS as COLLECTION_SECTIONS
from build_discoveries import llms_section, main_feed_batches, write_discoveries
from build_discovery_leads import llms_section as lead_llms_section, write_lead_exports
from build_manifest import write_build_manifest
from crawl_policy import robots_txt
from language_fragment import add_language_fragment_script
from site_shell import apply_site_shell
from data_downloads import build_data_downloads
from open_graph import website_node
from structured_data import catalog_node, organization_node
from homepage_locales import HOMEPAGE_DESTINATIONS, localized_homepage
from artifact_links import with_artifact_links, with_curated_labels
from source_browser import write_source_browser
from localization import read_localizations, localized_records
from source_scope import apply_scope, read_scope
from sitemaps import SITEMAP_INDEX, page_dates, write_sitemaps
from public_source_supplements import (PUBLISHED_FILENAME, compose_published, copy_public_evidence, json_bytes,
                                      load_supplements, project_additions, read_withdrawals,
                                      write_withdrawn_redirects)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "site"
OUTPUT = ROOT / "dist"
SITE_URL = "https://awesomerea.org"
REPOSITORY_URL = "https://github.com/reacher-z/Awesome-REA"
TARGETS = {"website", "game", "app", "binary", "firmware", "protocol"}
# Listed projects may link back to their entries with this badge, so its public URL must stay stable.
LISTED_BADGE = "featured-by-awesome-rea-inline.svg"
# Record fields the homepage needs for its first render; catalog.json keeps every field.
CATALOG_INDEX_FIELDS = ("id", "name", "name_zh", "url", "evidence_url", "description_en", "description_zh", "kind",
                        "category", "group", "relationship", "targets", "verified_at")
def catalog_index(catalog: dict) -> dict:
    """Project the complete catalog onto the lean index the homepage renders first."""
    # source_category_labels name the repository view's Category filter options, which app.js builds from this file.
    return {"meta": catalog["meta"], "topic_labels": catalog["topic_labels"], "category_labels": catalog["category_labels"],
            "source_category_labels": catalog["source_category_labels"],
            "resources": [{key: record[key] for key in CATALOG_INDEX_FIELDS if key in record} for record in catalog["resources"]]}


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


def explorer_page(html: str) -> str:
    """The old homepage as the full explorer at /explore/: its filters and repository view, out of the search index."""
    for pattern in (r'\s*<link rel="canonical"[^>]*>', r'\s*<link rel="alternate"[^>]*>', r'\s*<meta property="[^"]*"[^>]*>',
                    r'\s*<meta name="twitter:[^"]*"[^>]*>', r'\s*<script type="application/ld\+json">.*?</script>'):
        html = re.sub(pattern, '', html, flags=re.S)
    return html.replace('</title>', '</title><meta name="robots" content="noindex">', 1)


def build_site(output: Path) -> tuple[int, int, int]:
    """Render a complete site into a fresh, caller-owned staging directory."""
    translations = json.loads((SOURCE / "translations.zh-CN.json").read_text(encoding="utf-8"))
    papers = json.loads((ROOT / "data" / "papers.json").read_text(encoding="utf-8"))
    resources = []
    for filename in ("rea-resources.json", "tool-resources.json"):
        for original in json.loads((ROOT / "data" / filename).read_text(encoding="utf-8")):
            record = dict(original)
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
    (output / "badges").mkdir()
    shutil.copy2(ROOT / "assets" / LISTED_BADGE, output / "badges" / LISTED_BADGE)
    html = (output / "index.html").read_text(encoding="utf-8")
    for key, value in {"RESOURCE_COUNT": len(resources), "INTEGRATION_COUNT": metadata["independent_integration_count"], "REVIEWED_AT": latest_review}.items():
        html = html.replace("{{" + key + "}}", str(value))
    # Unfiltered target counts and the Protocol button are in the HTML, so the first paint matches app.js's first render.
    for target in ("all", *sorted(TARGETS)):
        count = len(resources) if target == "all" else sum(target in record["targets"] for record in resources)
        html = html.replace("{{TARGET_COUNT_" + target.upper() + "}}", str(count))
    protocol_button = '<button type="button" class="target-filter" data-target="protocol" aria-pressed="false" hidden>'
    if html.count(protocol_button) != 1:
        raise ValueError("Homepage needs exactly one curated Protocol target button")
    if any("protocol" in record["targets"] for record in resources):
        html = html.replace(protocol_button, protocol_button.replace(" hidden>", ">"))
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
        html = html.replace('id="download-source-index"', 'id="download-source-index" hidden')
        write_source_browser(output, None)
    topic_labels_path = SOURCE / "topics.i18n.json"
    topic_labels = json.loads(topic_labels_path.read_text(encoding="utf-8")) if topic_labels_path.exists() else {}
    metadata["paper_count"] = len(papers)
    # The homepage reads category labels from here, so filters, cards and entry pages share one wording.
    category_labels = {category: list(labels) for category, labels in CATEGORIES.items()}
    catalog = {"meta": metadata, "resources": resources, "topic_labels": topic_labels, "category_labels": category_labels}
    # The repository view's Category filter labels the same categories as the /browse/ pages.
    catalog["source_category_labels"] = {category: list(labels) for category, labels in REPOSITORY_CATEGORIES.items()}
    (output / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Requirement lists and additional evidence stay out of the first-render index; app.js fetches catalog.json afterwards.
    (output / "catalog-index.json").write_text(json.dumps(catalog_index(catalog), ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    (output / "papers.json").write_text(json.dumps(papers, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in {"BROWSE_COUNT": metadata["source_index"]["resource_count"], "SCANNED_COUNT": metadata["source_index"].get("scanned_count", 0), "PAPER_COUNT": len(papers)}.items():
        html = html.replace("{{" + key + "}}", f"{value:,}")
    navigation = [(path, names[0]) for path, names in HOMEPAGE_DESTINATIONS.items()]
    structured = {"@context": "https://schema.org", "@graph": [
        organization_node(SITE_URL, REPOSITORY_URL),
        website_node(SITE_URL, REPOSITORY_URL),
        catalog_node(SITE_URL),
        {"@type": "CollectionPage", "@id": SITE_URL + "/#collection", "url": SITE_URL + "/", "name": "Awesome Reverse Engineering Anything", "inLanguage": "en", "isPartOf": {"@id": SITE_URL + "/#website"}, "description": "An independent collection of reverse-engineering tools, projects, case studies and research papers for websites, games, apps, binaries, firmware and communication protocols.", "mainEntity": {"@type": "ItemList", "numberOfItems": len(navigation), "itemListElement": [{"@type": "ListItem", "position": i, "name": name, "url": f"{SITE_URL}/{path}/"} for i, (path, name) in enumerate(navigation, 1)]}}
    ]}
    html = html.replace("</head>", '<script type="application/ld+json">' + json.dumps(structured, ensure_ascii=False).replace("<", "\\u003c") + '</script>\n</head>')
    # Stylesheets and scripts move to content-addressed /assets/ paths; the favicon keeps a ?v= revision.
    favicon_revision = hashlib.sha256((output / "favicon.svg").read_bytes()).hexdigest()[:16]
    asset_hrefs = {"app.js": fingerprinted_href(output, "app.js"), "styles.css": fingerprinted_href(output, "styles.css"),
                   "favicon.svg": f"/favicon.svg?v={favicon_revision}"}
    for filename, attribute in (("app.js", "src"), ("styles.css", "href"), ("favicon.svg", "href")):
        html = html.replace(f'{attribute}="{filename}"', f'{attribute}="{asset_hrefs[filename]}"')
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
    # Start the catalog index request while the page parses. The URL and CORS mode match app.js's
    # fetch(dataURL("catalog-index.json")), so that fetch reuses this response; source-browser.json stays on demand.
    script_tag = f'<script src="{asset_hrefs["app.js"]}" defer></script>'
    if html.count(script_tag) != 1:
        raise ValueError("Homepage needs exactly one deferred app.js script")
    html = html.replace(script_tag, f'<link rel="preload" href="/catalog-index.json?v={data_revision}" as="fetch" crossorigin>\n  ' + script_tag)
    # Both explorer pages contain their own language before JavaScript runs; the homepages reuse their metadata.
    app_source = (SOURCE / "app.js").read_text(encoding="utf-8")
    explorer_sources = {language: localized_homepage(html, app_source, language) for language in ("en", "zh")}
    for language, route in (("en", "explore/index.html"), ("zh", "zh/explore/index.html")):
        (output / route).parent.mkdir(parents=True, exist_ok=True)
        (output / route).write_text(explorer_page(explorer_sources[language]), encoding="utf-8")
    # Later builders read the page assets from the homepage; build_home() writes the real one last.
    (output / "index.html").write_text(explorer_sources["en"], encoding="utf-8")
    (output / "zh/index.html").write_text(explorer_sources["zh"], encoding="utf-8")
    icon_stylesheet = None
    browse_urls = build_browse_pages(
        output, browse_document, curated_count=len(resources), site_url=SITE_URL,
        repository_url=REPOSITORY_URL, styles_href=asset_hrefs["styles.css"],
        browse_styles_href=fingerprinted_href(output, "browse.css"),
        favicon_href=asset_hrefs["favicon.svg"],
        social_image_href=f"{SITE_URL}/social-card.png?v={social_revision}",
        data_revision=data_revision, icon_stylesheet_href=icon_stylesheet,
    )
    # Withdrawn evidence archives come from their registry, whatever the state of the batches citing them:
    # /about/ lists each one, and its old address redirects there.
    withdrawals = read_withdrawals(ROOT)
    write_withdrawn_redirects(output, withdrawals)
    discovery_paths = build_discovery_pages(output, catalog, browse_document, withdrawals=withdrawals)
    # The unreviewed discovery queue: its own list pages, feeds and JSON, never curated pages or counts.
    queue_paths, discovery_queue = write_discoveries(output, catalog, papers, browse_document)
    discovery_paths = [*discovery_paths, *queue_paths]
    # Followed-source leads: JSON exports only, labelled unreviewed, never pages or curated counts.
    lead_queue = write_lead_exports(output, catalog)
    # The static API reads the same records and queues; its documentation page joins the sitemap.
    api_index = build_api(output, resources=resources, papers=papers, repository_document=browse_document,
                          discovery_queue=discovery_queue, lead_queue=lead_queue, site_url=SITE_URL)
    section = llms_section(discovery_queue, SITE_URL) + lead_llms_section(lead_queue, SITE_URL)
    if section:
        llms_path = output / "llms.txt"
        llms = llms_path.read_text(encoding="utf-8")
        # The unreviewed queues come after the curated collections and data, before the optional links.
        marker = "\n## Optional\n"
        if llms.count(marker) != 1:
            raise ValueError("llms.txt needs exactly one Optional section")
        llms_path.write_text(llms.replace(marker, "\n" + section + marker), encoding="utf-8")
    # Every footer offers the same repository download as the homepage and the browse pages.
    repository_export = PUBLISHED_FILENAME if metadata["source_index"].get("full_export") == PUBLISHED_FILENAME else "source-index.json"
    discovery_paths = [*discovery_paths, *write_api_pages(output, api_index, site_url=SITE_URL, repository_url=REPOSITORY_URL,
                                                          source_export=repository_export)]
    # llms-full.txt: the whole curated catalog in Markdown, one file per language.
    for language, header in (("en", "# Awesome Reverse Engineering Anything: the full curated catalog\n\n> Every source-reviewed resource and research paper of AwesomeREA.org, with requirements, limits and sources. The navigation index is https://awesomerea.org/llms.txt; each entry also has its own Markdown page and record.json.\n"),
                             ("zh", "# Awesome Reverse Engineering Anything：完整精选目录\n\n> AwesomeREA.org 全部经来源复核的资源与研究论文，含使用条件、局限与来源。导航索引见 https://awesomerea.org/llms.txt；每个条目另有独立的 Markdown 页面与 record.json。\n")):
        target = output / ("zh/llms-full.txt" if language == "zh" else "llms-full.txt")
        target.write_text(full_catalog_markdown(resources, papers, language, site_url=SITE_URL, sections=COLLECTION_SECTIONS,
                                                section_of=collection_section, header=header), encoding="utf-8")
    paper_urls = build_paper_pages(
        output, papers, site_url=SITE_URL, repository_url=REPOSITORY_URL,
        styles_href=asset_hrefs["styles.css"], papers_styles_href=fingerprinted_href(output, "papers.css"),
        favicon_href=asset_hrefs["favicon.svg"], social_image_href=f"{SITE_URL}/social-card.png?v={social_revision}",
        icon_stylesheet_href=icon_stylesheet, repository_export=repository_export,
    )
    survey_document = json.loads((ROOT / "data/survey.json").read_text(encoding="utf-8"))
    survey_urls = build_survey(
        output, papers, resources, document=survey_document,
        site_url=SITE_URL, repository_url=REPOSITORY_URL,
        styles_href=asset_hrefs["styles.css"], favicon_href=asset_hrefs["favicon.svg"],
        social_image_href=f"{SITE_URL}/social-card.png?v={social_revision}",
        icon_stylesheet_href=icon_stylesheet, repository_export=repository_export,
    )
    entry_urls = build_entry_pages(
        output, resources, papers, site_url=SITE_URL, repository_url=REPOSITORY_URL,
        styles_href=asset_hrefs["styles.css"], entry_styles_href=fingerprinted_href(output, "entry.css"),
        favicon_href=asset_hrefs["favicon.svg"], social_image_href=f"{SITE_URL}/social-card.png?v={social_revision}",
        icon_stylesheet_href=icon_stylesheet, survey_discussions=discussion_sections(survey_document),
        repository_export=repository_export,
    )
    # Feeds list inclusion dates; they link from pages written above and are not sitemap pages.
    build_feeds(output, resources, papers, site_url=SITE_URL, repository_url=REPOSITORY_URL,
                discovery_batches=main_feed_batches(discovery_queue))
    # Static pages with a language link keep the reader's card or section on the translated page.
    add_language_fragment_script(output)
    # The homepages: masthead, search and the index-card drawer. Every other page gets the same shared chrome.
    # Their head is the one the builders above finished, feed links included.
    build_home(output, explorer_pages={"en": (output / "index.html").read_text(encoding="utf-8"), "zh": (output / "zh/index.html").read_text(encoding="utf-8")}, resources=resources, papers=papers, discovery_queue=discovery_queue,
               repository_url=REPOSITORY_URL, repository_export=repository_export)
    apply_site_shell(output, repository_url=REPOSITORY_URL, skip=frozenset({"index.html", "zh/index.html"}))
    # Every stylesheet and script now has a content-addressed copy under /assets/; drop the root copies.
    remove_unhashed_copies(output, [path.name for path in SOURCE.iterdir()])
    (output / ".nojekyll").write_text("", encoding="utf-8")
    (output / "CNAME").write_text("awesomerea.org\n", encoding="utf-8")
    (output / "robots.txt").write_text(robots_txt(SITE_URL, f"{SITE_URL}/{SITEMAP_INDEX}"), encoding="utf-8")
    sitemap_urls = [SITE_URL + "/", SITE_URL + "/zh/", *browse_urls, *(SITE_URL + path for path in discovery_paths), *paper_urls, *survey_urls, *entry_urls]
    # lastmod comes from the records each page shows, never the build time (sitemaps.page_dates).
    dates = page_dates(resources=resources, papers=papers, repository_document=browse_document,
                       discovery_batches=(discovery_queue or {}).get("batches"), lead_batches=(lead_queue or {}).get("batches"),
                       survey_date=survey_document.get("date"))
    write_sitemaps(output, SITE_URL, [url.removeprefix(SITE_URL) for url in sitemap_urls], dates)
    build_data_downloads(output, catalog, papers,
                         (output / 'papers/references.bib').read_text(encoding='utf-8'))
    write_build_manifest(output)
    return len(resources), len(papers), len(sitemap_urls)


def check_output_directory(output: Path) -> None:
    """Never follow a deployment-directory symlink or replace a non-directory."""
    if output.is_symlink() or (output.exists() and not output.is_dir()):
        raise ValueError("Deployment output must be a directory, not a symlink or file.")


def build_staged_site() -> tuple[int, int, int]:
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
        counts = build_site(staged)
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
    # Accepted and ignored: the Cloudflare Pages build command may still pass it, and the site loads no icon font now.
    parser.add_argument("--fontawesome-assets-url", help=argparse.SUPPRESS)
    parser.parse_args()
    resources, papers, pages = build_staged_site()
    print(f"Built {resources} curated resources, {papers} papers and {pages} indexable pages in dist/ ({SITE_URL})")


if __name__ == "__main__":
    main()
