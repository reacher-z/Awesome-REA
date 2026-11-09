#!/usr/bin/env python3
"""Check the built site's crawlable routes, metadata, languages, and source coverage."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, unquote
from urllib.robotparser import RobotFileParser

from build_browse_pages import CATEGORIES
from crawl_policy import CONTENT_SIGNAL, CRAWLERS, REQUIRED_AI_CRAWLERS, TRAINING_PREFERENCE_TOKEN
from sitemaps import (SECTION_FILES, SITEMAP_INDEX, english_path, instant, language_alternates, latest,
                      normalized_date, page_dates, read_sitemaps, record_date, section_for)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dist"
ORIGIN = "https://awesomerea.org"


def expected_entry_routes(resources, papers):
    """Derive every localized detail route from reviewed IDs, never scan records."""
    routes = {}
    for kind, directory, records in (("resource", "resources", resources), ("paper", "papers", papers)):
        identifiers = [record["id"] for record in records]
        assert len(identifiers) == len(set(identifiers)), f"Duplicate {kind} detail IDs"
        for identifier in identifiers:
            assert isinstance(identifier, str) and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", identifier), "Unsafe detail ID"
            assert kind != "paper" or identifier.startswith("paper-"), "Paper detail IDs require the paper- prefix"
            for language, prefix in (("en", ""), ("zh", "/zh")):
                routes[f"{prefix}/{directory}/{identifier}/"] = (kind, identifier, language)
    return routes


def discovery_class_pages(output):
    """English paths of the per-class discovery pages that the published queue export names."""
    export = Path(output) / "discoveries.json"
    if not export.is_file():
        return []
    return [urlsplit(entry["page"]).path for entry in json.loads(export.read_text(encoding="utf-8")).get("class_pages", [])]


def validate_route_inventory(urls, resources, papers, *, include_browse=True, include_discoveries=False, discovery_classes=()):
    """Require exact sitemap coverage; unknown automatic-repository pages are refused.

    The unreviewed discovery queue adds one list page per language, plus one page per language for each Data class
    with more records than the list page shows; never a page per scan record.
    """
    routes = expected_entry_routes(resources, papers)
    expected = set(routes)
    for prefix in ("", "/zh"):
        expected.update(prefix + path for path in ("/", "/resources/", "/cases/", "/papers/", "/survey/", "/about/", "/contribute/", "/api/"))
        if include_browse:
            expected.add(prefix + "/browse/")
            expected.update(f"{prefix}/browse/{category}/" for category in CATEGORIES)
        if include_discoveries:
            expected.add(prefix + "/discoveries/")
            expected.update(prefix + path for path in discovery_classes)
    assert len(urls) == len(set(urls)), "Duplicate sitemap URLs"
    assert set(urls) == {ORIGIN + route for route in expected}, "Sitemap route inventory differs from reviewed entries and collection pages"
    return routes


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.links, self.meta, self.ids, self.resources, self.graphs = [], {}, set(), [], []
        self.language = None
        self.h1 = 0
        self.in_json = False
        self.json_parts = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.language = attrs.get("lang")
        if tag == "h1":
            self.h1 += 1
        if tag == "link":
            self.links.append(attrs)
        if tag == "meta":
            self.meta[attrs.get("name") or attrs.get("property")] = attrs.get("content", "")
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if "data-resource-id" in attrs:
            self.resources.append(attrs["data-resource-id"])
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.in_json = True
            self.json_parts = []

    def handle_data(self, data):
        if self.in_json:
            self.json_parts.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.in_json:
            self.graphs.append(json.loads("".join(self.json_parts)))
            self.in_json = False


def built_page_dates(output, records, papers):
    """Recompute every page's lastmod from the data files the build published."""
    output = Path(output)
    repository = None
    for name in ("source-published.json", "source-index.json"):
        if (output / name).is_file():
            repository = json.loads((output / name).read_text(encoding="utf-8"))
            break
    queue, leads = output / "discoveries.json", output / "discoveries/leads.json"
    batches = json.loads(queue.read_text(encoding="utf-8")).get("batches", []) if queue.is_file() else []
    lead_batches = json.loads(leads.read_text(encoding="utf-8")).get("batches", []) if leads.is_file() else []
    survey = json.loads((ROOT / "data/survey.json").read_text(encoding="utf-8"))
    return page_dates(resources=records, papers=papers, repository_document=repository,
                      discovery_batches=batches, lead_batches=lead_batches, survey_date=survey.get("date"),
                      discovery_class_pages=discovery_class_pages(output))


def validate_sitemaps(output, records, papers):
    """Check the sitemap index, its section sitemaps, data-derived lastmod dates and hreflang alternates.

    Returns the listed page URLs in index order.
    """
    output = Path(output)
    sitemaps, pages = read_sitemaps(output, ORIGIN)
    expected_files = {ORIGIN + "/" + name: section for section, name in SECTION_FILES.items()}
    assert sitemaps and set(sitemaps) <= set(expected_files), "The sitemap index must list only the section sitemaps"
    dates = built_page_dates(output, records, papers)
    newest = latest(dates.values())
    for url, sitemap in sitemaps.items():
        section = expected_files[url]
        assert sitemap["urls"], f"Empty sitemaps stay out of the index: {url}"
        assert len(sitemap["urls"]) <= 50000, f"Sitemap exceeds 50,000 URLs: {url}"
        paths = [urlsplit(page).path for page in sitemap["urls"]]
        assert all(section_for(path) == section for path in paths), f"A page is listed in the wrong section sitemap: {url}"
        expected_lastmod = latest(dates.get(english_path(path)) for path in paths)
        assert sitemap["lastmod"] == expected_lastmod, f"Sitemap index lastmod must be the newest page date: {url}"
    for url, entry in pages.items():
        path = urlsplit(url).path
        assert entry["alternates"] == language_alternates(ORIGIN, path), f"Sitemap language alternates mismatch: {url}"
        lastmod, expected = entry["lastmod"], dates.get(english_path(path))
        assert lastmod == expected, f"lastmod must come from the page's recorded data dates, not the build: {url} has {lastmod}, expected {expected}"
        if lastmod is not None:
            assert normalized_date(lastmod) == lastmod and instant(lastmod) <= instant(newest), f"Invalid or future lastmod: {url}"
    # Detail pages: the later of the record's inclusion and its latest source review, checked from the record itself.
    for directory, rows in (("resources", records), ("papers", papers)):
        for row in rows:
            for prefix in ("", "/zh"):
                assert pages[f"{ORIGIN}{prefix}/{directory}/{row['id']}/"]["lastmod"] == record_date(row), f"Detail lastmod differs from its record: {row['id']}"
    return [url for sitemap in sitemaps.values() for url in sitemap["urls"]]


def validate_robots(output, urls):
    """Allow every crawler: the * group plus a named allow-all group for each listed crawler."""
    text = (Path(output) / "robots.txt").read_text(encoding="utf-8")
    assert not re.search(r"(?im)^\s*disallow\s*:", text), "robots.txt must not disallow anything"
    named = set(re.findall(r"(?im)^user-agent:\s*(\S+)\s*$", text))
    missing = [token for token in (*CRAWLERS, *REQUIRED_AI_CRAWLERS, TRAINING_PREFERENCE_TOKEN, "*") if token not in named]
    assert not missing, "robots.txt must name these crawlers: " + ", ".join(missing)
    assert text.count(f"Content-Signal: {CONTENT_SIGNAL}") == 2, "Both robots groups state the same content signals"
    robots = RobotFileParser()
    robots.parse(text.splitlines())
    for bot in (*CRAWLERS, TRAINING_PREFERENCE_TOKEN, "ExampleUnlistedBot/1.0"):
        assert all(robots.can_fetch(bot, url) for url in urls), f"Robots blocks {bot}"
    assert robots.site_maps() == [ORIGIN + "/" + SITEMAP_INDEX], "robots.txt must declare exactly the sitemap index"


def main():
    records = json.loads((OUTPUT / "catalog.json").read_text(encoding="utf-8"))["resources"]
    papers = json.loads((OUTPUT / "papers.json").read_text(encoding="utf-8"))
    urls = validate_sitemaps(OUTPUT, records, papers)
    entries = validate_route_inventory(urls, records, papers, include_browse=(OUTPUT / "source-index.json").is_file(),
                                       include_discoveries=(OUTPUT / "discoveries.json").is_file(),
                                       discovery_classes=discovery_class_pages(OUTPUT))
    documents = {}
    for url in urls:
        parsed = urlsplit(url)
        assert parsed.scheme + "://" + parsed.netloc == ORIGIN, url
        assert not parsed.query and not parsed.fragment, url
        path = OUTPUT / parsed.path.lstrip("/") / "index.html"
        assert path.is_file(), f"Sitemap route does not exist: {url}"
        page = Document(path.read_text(encoding="utf-8"))
        documents[url] = page
        assert page.h1 == 1, f"Expected one H1: {url}"
        assert page.meta.get("description"), f"Missing description: {url}"
        assert not {"noindex", "nosnippet", "none"}.intersection(
            page.meta.get("robots", "").lower().replace(",", " ").split()), url
        canonical = [link.get("href") for link in page.links if link.get("rel") == "canonical"]
        assert canonical == [url], f"Canonical mismatch: {url}"
        english_path = parsed.path.removeprefix("/zh") if parsed.path.startswith("/zh/") else parsed.path
        expected_alternates = {"en": ORIGIN + english_path, "zh-CN": ORIGIN + "/zh" + english_path,
                               "x-default": ORIGIN + english_path}
        alternates = [link for link in page.links if link.get("rel") == "alternate" and "hreflang" in link]
        assert len(alternates) == 3 and {link["hreflang"]: link.get("href") for link in alternates} == expected_alternates, f"Language alternatives mismatch: {url}"
        assert page.language == ("zh-CN" if parsed.path.startswith("/zh/") else "en"), url
        assert page.graphs, f"No structured metadata: {url}"
        for document in page.graphs:
            assert document.get("@context") == "https://schema.org", url
            for entity in document.get("@graph", []):
                if entity.get("@type") == "ItemList":
                    elements = entity["itemListElement"]
                    assert entity["numberOfItems"] == len(elements), url
                    assert [e["position"] for e in elements] == list(range(1, len(elements) + 1)), url
                    for item in elements:
                        destination = urlsplit(item["url"])
                        if destination.fragment and item["url"].startswith(url + "#"):
                            assert unquote(destination.fragment) in page.ids, item["url"]
    for url, page in documents.items():
        for link in page.links:
            if link.get("rel") != "alternate" or "hreflang" not in link:
                continue
            other = documents.get(link["href"])
            assert other is not None, f"Language alternative absent from sitemap: {url}"
            assert any(item.get("rel") == "alternate" and item.get("href") == url for item in other.links), url
    expected = {r["id"] for r in records}
    for path in ("/resources/", "/zh/resources/"):
        page = documents[ORIGIN + path]
        assert len(page.resources) == len(expected) and set(page.resources) == expected, path
    expected_cases = {record["id"] for record in records if record["kind"] == "case-study"}
    for path in ("/cases/", "/zh/cases/"):
        page = documents[ORIGIN + path]
        assert len(page.resources) == len(expected_cases) and set(page.resources) == expected_cases, path
    validate_robots(OUTPUT, urls)
    assert (OUTPUT / "llms.txt").is_file(), "Missing optional catalog index"
    # The transitional explorer pages are noindex, so they stay out of the sitemap.
    explorer = {OUTPUT / "explore/index.html", OUTPUT / "zh/explore/index.html"}
    assert len(urls) == len([page for page in OUTPUT.rglob("index.html") if page not in explorer]), "A generated page is absent from the sitemap"
    print(f"Discovery checks passed: {len(urls)} canonical pages in the sitemap index with data-dated lastmod and hreflang alternates, {len(entries)} localized detail pages, reciprocal languages, {len(records)} static curated entries per language, JSON-LD, and permissions for {len(CRAWLERS)} named crawlers.")


if __name__ == "__main__":
    main()
