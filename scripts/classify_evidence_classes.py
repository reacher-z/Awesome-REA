#!/usr/bin/env python3
"""Assign evidence classes 0-3 to every curated catalog entry.

Reads data/rea-resources.json and data/tool-resources.json, observes public
evidence for each entry's URL (GitHub REST API, or the page itself for other
hosts), and writes data/evidence-classes.json. The class measures how strong
the public evidence is, not whether a reproduction is complete:

- Class 0: documentation covers the full feature set, plus a download method
  and an image or video demo.
- Class 1: download method and image/video demo exist, but the documented
  scope is partial — single features, patches, ports, investigations.
- Class 2: demo or download missing, but code and documentation exist;
  whether it builds is unknown.
- Class 3: no code or no documentation — progress notes or shared notebook
  entries only.

Observed signals stay in the output so a reader can audit every assignment.
data/evidence-class-overrides.json holds manual corrections; overrides win.
"""
from __future__ import annotations

import argparse
import base64
import concurrent.futures
import datetime as dt
import hashlib
import html as html_module
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / ".cache" / "evidence-scan"
OUTPUT_PATH = ROOT / "data" / "evidence-classes.json"
OVERRIDES_PATH = ROOT / "data" / "evidence-class-overrides.json"
SPEC_VERSION = "evidence-class-v1"
README_MIN_BYTES = 400
MAX_WORKERS = 8

CODE_HOSTS = {"github.com", "gitlab.com", "bitbucket.org", "codeberg.org", "gitee.com", "sourceforge.net"}
GITHUB_HOSTS = {"github.com", "www.github.com"}
# Badge-style images and package-registry icons say nothing about a demo.
IMAGE_URL_EXCLUDES = ("shields.io", "badge", "travis-ci", "codecov", "coveralls", "circleci",
                      "workflows", "logo", "snyk", "gitter", "liberapay", "opencollective",
                      "buymeacoffee", "img.shields.io", "awesome", "pr-welcome", "star-history")
VIDEO_HOSTS = ("youtube.com", "youtu.be", "vimeo.com", "bilibili.com", "b23.tv", "youku.com",
               "ixigua.com", "douyin.com")
MEDIA_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".apng", ".svg", ".mp4", ".webm", ".mov")
# Files that only appear when an author ships something to run.
DOWNLOAD_EXTENSIONS = (".apk", ".exe", ".dmg", ".msi", ".appimage", ".deb", ".rpm", ".whl",
                       ".vsix", ".crx", ".xpi", ".ipa", ".tar.gz", ".7z")
PACKAGE_COMMANDS = re.compile(
    r"(?:^|`|\s)(?:npm\s+(?:i|install|ci|exec)\s+\S+|npx\s+\S+|yarn\s+(?:add|dlx|global\s+add)\s+\S+"
    r"|pnpm\s+(?:add|dlx)\s+\S+|pip\s+install\s+\S+|pipx\s+install\s+\S+|uv\s+(?:tool\s+install|run)\s+\S+"
    r"|cargo\s+(?:install|add)\s+\S+|go\s+install\s+\S+|brew\s+install\s+\S+|docker\s+(?:pull|run)\s+\S+"
    r"|gem\s+install\s+\S+|conda\s+install\s+\S+|dotnet\s+tool\s+(?:install|update)\s+\S+"
    r"|winget\s+install\s+\S+|scoop\s+install\s+\S+|choco\s+install\s+\S+|luarocks\s+install\s+\S+"
    r"|pacman\s+-S\s+\S+|apt(?:-get)?\s+install\s+\S+)", re.IGNORECASE)
DOWNLOAD_HEADING = re.compile(r"^#{1,4}[^\n#]*\b(download|releases?|obtain)\b", re.MULTILINE | re.IGNORECASE)
DEMO_LINK_TEXT = re.compile(r"\b(demo|playable|live\s+preview|try\s+it\s+(?:out|online)|online\s+demo)\b", re.IGNORECASE)

SECTION_INSTALL = re.compile(r"^#{1,4}[^\n#]*\b(install|installation|build|setup|getting\s+started|quick\s?start|compil|prerequisit|requirement)", re.MULTILINE | re.IGNORECASE)
SECTION_USAGE = re.compile(r"^#{1,4}[^\n#]*\b(usage|use|example|how\s+to|getting\s+started|quick\s?start|run)", re.MULTILINE | re.IGNORECASE)
SECTION_FEATURES = re.compile(r"^#{1,4}[^\n#]*\b(features?|capabilities|功能|highlights|what\s+it\s+does)", re.MULTILINE | re.IGNORECASE)
SECTION_MEDIA = re.compile(r"^#{1,4}[^\n#]*\b(screenshots?|demo|preview|video|images?|showcase)", re.MULTILINE | re.IGNORECASE)
MARKDOWN_IMAGE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")
MARKDOWN_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)")
HTML_IMAGE = re.compile(r"<img[^>]*\bsrc=[\"']([^\"']+)", re.IGNORECASE)
HTML_LINK = re.compile(r"<a[^>]*\bhref=[\"']([^\"']+)[\"'][^>]*>([\s\S]{0,120}?)</a>", re.IGNORECASE)
HTML_TAG = re.compile(r"<[^>]+>")
CODE_BLOCK = re.compile(r"```.*?```", re.DOTALL)
DESCRIPTION_COMPLETE = re.compile(
    r"\bre-?implements?\b|\bre-?implementation\b|\bcomplete\s+(?:re)?implementation\b"
    r"|\bfull\s+(?:re)?implementation\b|\bfully\s+(?:playable|functional)\b"
    r"|\bplayable\s+(?:port|recreation|reimplementation)\b|\bfaithful\s+(?:port|recreation)\b"
    r"|\bdrop-?in\s+replacement\b|\bcompatible\s+replacement\b", re.IGNORECASE)
DESCRIPTION_PARTIAL = re.compile(
    r"\b(?:one|single|a)\s+(?:rule|function|feature|mechanic|screen|scene|routine|helper|command|aspect|level|room)\b"
    r"|\bpartial(?:ly)?\b|\bpatch(?:es|ing)?\b|\bteaching\s+case\b|\bproof\s+of\s+concept\b"
    r"|\brecover(?:s|ing|ed)?\b|\breconstruct(?:s|ing|ed)?\b|\bport(?:s|ing|ed)\b|\bsingle\s+\S+\s+(?:feature|file)\b",
    re.IGNORECASE)


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


class HttpClient:
    """Small shared client so the run stays inside the API rate budget."""

    def __init__(self, token: str | None, user_agent: str):
        self.headers = {"User-Agent": user_agent, "Accept": "application/vnd.github+json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
        # Plain API calls stay identified; rendered pages need a browser-like
        # User-Agent because several hosts answer scripts with 403/406.
        self.page_headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                             "(KHTML, like Gecko) Chrome/126.0 Safari/537.36", "Accept": "text/html,*/*;q=0.8"}

    def get(self, url: str, timeout: int = 30, page: bool = False) -> tuple[int, bytes, dict]:
        headers = self.page_headers if page else self.headers
        request = urllib.request.Request(url, headers=dict(headers))
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.status, response.read(), dict(response.headers)
        except urllib.error.HTTPError as error:
            return error.code, error.read() if error.fp is None else error.read(), dict(error.headers or {})
        except (urllib.error.URLError, TimeoutError, OSError):
            return 0, b"", {}


def cached(key: str) -> dict | None:
    path = CACHE_DIR / (hashlib.sha256(key.encode()).hexdigest() + ".json")
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
    return None


def store_cache(key: str, payload: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / (hashlib.sha256(key.encode()).hexdigest() + ".json")
    path.write_text(json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8")


def github_repo_slug(url: str) -> str | None:
    """owner/name for GitHub repository URLs, including blob/tree deep links."""
    try:
        parts = urllib.parse.urlsplit(url)
    except ValueError:
        return None
    if parts.hostname and parts.hostname.lower() not in GITHUB_HOSTS:
        return None
    segments = [segment for segment in parts.path.split("/") if segment]
    if len(segments) < 2 or segments[0] in ("topics", "features", "collections", "about", "orgs"):
        return None
    return segments[0] + "/" + re.sub(r"\.git$", "", segments[1])


def github_api_fetch(client: HttpClient, slug: str) -> dict:
    """One repo's meta, releases and README from the GitHub REST API."""
    cached_payload = cached("gh:v2:" + slug)
    if cached_payload:
        return cached_payload
    status, body, headers = client.get(f"https://api.github.com/repos/{slug}")
    if status in (403, 429) and headers.get("retry-after"):
        time.sleep(int(headers.get("retry-after", "60")) + 1)
        status, body, headers = client.get(f"https://api.github.com/repos/{slug}")
    if status != 200:
        # Transient failures and hard 404s both look "unavailable", so a miss is never cached:
        # a rerun retries, and a truly gone repository keeps failing honestly.
        return {"unavailable": True, "fetched_at": now_utc()}
    meta = json.loads(body.decode("utf-8", "replace"))
    release_status, release_body, _ = client.get(f"https://api.github.com/repos/{slug}/releases?per_page=100")
    releases = json.loads(release_body.decode("utf-8", "replace")) if release_status == 200 else []
    readme_status, readme_body, _ = client.get(f"https://api.github.com/repos/{slug}/readme")
    readme_text = ""
    if readme_status == 200:
        readme = json.loads(readme_body.decode("utf-8", "replace"))
        readme_text = base64.b64decode(readme.get("content", "")).decode("utf-8", "replace")
    payload = {
        "unavailable": False,
        "archived": bool(meta.get("archived")),
        "release_count": len(releases),
        "release_asset_count": sum(len(release.get("assets") or []) for release in releases),
        "readme_bytes": len(readme_text.encode("utf-8")),
        "readme_text": readme_text[:400_000],
        "linked_docs_bytes": 0,
        "fetched_at": now_utc(),
    }
    # A stub README that delegates to INSTALL.md or similar is still documentation;
    # pull the linked Markdown files so such repos are not mistaken for undocumented.
    if 0 < payload["readme_bytes"] < README_MIN_BYTES:
        fetched_bytes = 0
        markdown_links = []
        external_link = None
        for text, link in MARKDOWN_LINK.findall(readme_text):
            if re.search(r"\.(md)\b", link, re.IGNORECASE):
                markdown_links.append(link)
            elif external_link is None and link.startswith(("http://", "https://")):
                lowered = link.lower()
                if not any(marker in lowered for marker in IMAGE_URL_EXCLUDES) and "github.com" not in lowered:
                    external_link = link
        for link in markdown_links[:2]:
            if link.startswith(("http://", "https://")):
                if "raw.githubusercontent.com" not in link:
                    continue
                link = link.split("/", 4)[-1]
            path = link.lstrip("./")
            if not re.fullmatch(r"[\w./-]+\.md", path, re.IGNORECASE):
                continue
            doc_status, doc_body, _ = client.get(f"https://raw.githubusercontent.com/{slug}/HEAD/{path}")
            if doc_status == 200:
                fetched_bytes += len(doc_body)
        if not fetched_bytes and external_link:
            # A README that only points at a documentation site: read that page's text.
            page_status, page_body, _ = client.get(external_link, timeout=20, page=True)
            if page_status == 200:
                text = HTML_TAG.sub(" ", html_module.unescape(re.sub(
                    r"<(script|style)[^>]*>[\s\S]*?</\1>", " ", page_body.decode("utf-8", "replace"), flags=re.IGNORECASE)))
                fetched_bytes = len(re.sub(r"\s+", " ", text).strip().encode("utf-8"))
        payload["linked_docs_bytes"] = fetched_bytes
    store_cache("gh:v2:" + slug, payload)
    return payload


def gitlab_api_fetch(client: HttpClient, path: str) -> dict:
    """The GitLab v4 API mirror of github_api_fetch, for the few GitLab entries."""
    cached_payload = cached("gl:v2:" + path)
    if cached_payload:
        return cached_payload
    encoded = urllib.parse.quote(path, safe="")
    api = f"https://gitlab.com/api/v4/projects/{encoded}"
    status, body, _ = client.get(api)
    if status != 200:
        return {"unavailable": True, "fetched_at": now_utc()}
    project = json.loads(body.decode("utf-8", "replace"))
    branch = project.get("default_branch") or "master"
    release_status, release_body, _ = client.get(api + "/releases")
    releases = json.loads(release_body.decode("utf-8", "replace")) if release_status == 200 else []
    readme_text = ""
    readme_status, readme_body, _ = client.get(
        api + f"/repository/files/{urllib.parse.quote('README.md', safe='')}/raw?ref=" + urllib.parse.quote(branch, safe=""))
    if readme_status == 200:
        readme_text = readme_body.decode("utf-8", "replace")
    else:
        tree_status, tree_body, _ = client.get(api + f"/repository/tree?ref={urllib.parse.quote(branch, safe='')}")
        for entry in json.loads(tree_body.decode("utf-8", "replace")) if tree_status == 200 else []:
            if entry.get("name", "").upper().startswith("README."):
                raw_status, raw_body, _ = client.get(
                    api + "/repository/files/" + urllib.parse.quote(entry["name"], safe="")
                    + "/raw?ref=" + urllib.parse.quote(branch, safe=""))
                if raw_status == 200:
                    readme_text = raw_body.decode("utf-8", "replace")
                break
    asset_count = sum(len((release.get("assets") or {}).get("links") or []) for release in releases)
    payload = {
        "unavailable": False,
        "archived": bool(project.get("archived")),
        "release_count": len(releases),
        "release_asset_count": asset_count,
        "readme_bytes": len(readme_text.encode("utf-8")),
        "readme_text": readme_text[:400_000],
        "fetched_at": now_utc(),
    }
    store_cache("gl:v2:" + path, payload)
    return payload


def fetch_page(client: HttpClient, url: str) -> dict:
    """Non-GitHub URLs are observed from the rendered page itself."""
    cached_payload = cached("page:" + url)
    if cached_payload:
        return cached_payload
    status, body, _ = client.get(url, timeout=20, page=True)
    payload = {"unavailable": status == 0 or status >= 400, "http_status": status, "fetched_at": now_utc()}
    if not payload["unavailable"]:
        try:
            html_text = body.decode("utf-8", "replace")
        except UnicodeDecodeError:
            html_text = body.decode("latin-1", "replace")
        payload["html"] = html_text[:600_000]
    store_cache("page:" + url, payload)
    return payload


def page_signals(url: str, page: dict) -> dict:
    """Signals for a non-GitHub URL: does the page carry code links, docs, media?"""
    signals = {"code": False, "code_basis": None, "docs": False, "docs_bytes": 0, "docs_full": False,
               "download": None, "release_count": 0, "release_asset_count": 0,
               "demo": [], "media_count": 0, "archived": False, "unavailable": bool(page.get("unavailable"))}
    # A URL on a code host is code, even when the page itself is unreachable.
    host = (urllib.parse.urlsplit(url).hostname or "").lower()
    if host in CODE_HOSTS:
        signals["code"] = True
        signals["code_basis"] = "repo-url"
    if page.get("unavailable") or not page.get("html"):
        return signals
    html_text = page["html"]
    base = urllib.parse.urlsplit(url)
    links: list[tuple[str, str]] = []
    for href, text in HTML_LINK.findall(html_text):
        absolute = urllib.parse.urljoin(base.geturl(), href.strip())
        links.append((absolute, HTML_TAG.sub(" ", text)))
    for absolute, _ in links:
        link_host = urllib.parse.urlsplit(absolute).hostname or ""
        if link_host.lower() in CODE_HOSTS and len([part for part in urllib.parse.urlsplit(absolute).path.split("/") if part]) >= 2:
            signals["code"] = True
            signals["code_basis"] = "linked-repo"
            break
    text = HTML_TAG.sub(" ", html_module.unescape(re.sub(r"<(script|style)[^>]*>[\s\S]*?</\1>", " ", html_text, flags=re.IGNORECASE)))
    text = re.sub(r"\s+", " ", text).strip()
    signals["docs_bytes"] = len(text.encode("utf-8"))
    signals["docs"] = signals["docs_bytes"] >= README_MIN_BYTES
    demo, media_count = collect_media_signals(html_text, links)
    signals["demo"] = demo
    signals["media_count"] = media_count
    if collect_download_signals(text, links):
        signals["download"] = "file-links"
    elif PACKAGE_COMMANDS.search(text):
        signals["download"] = "package"
    return signals


def github_signals(meta: dict) -> dict:
    readme_text = meta.get("readme_text") or ""
    signals = {"code": True, "code_basis": "repo", "docs": False, "docs_bytes": meta.get("readme_bytes", 0),
               "docs_full": False, "download": None, "release_count": meta.get("release_count", 0),
               "release_asset_count": meta.get("release_asset_count", 0), "demo": [], "media_count": 0,
               "archived": bool(meta.get("archived")), "unavailable": bool(meta.get("unavailable"))}
    if meta.get("release_count"):
        signals["download"] = "release-assets" if meta.get("release_asset_count") else "release"
    if meta.get("unavailable") or not readme_text:
        return signals
    signals["docs"] = (signals["docs_bytes"] + meta.get("linked_docs_bytes", 0)) >= README_MIN_BYTES
    plain = CODE_BLOCK.sub(" ", readme_text)
    links = [(href.strip(), text) for text, href in MARKDOWN_LINK.findall(plain)]
    demo, media_count = collect_media_signals(plain, links)
    signals["demo"] = demo
    signals["media_count"] = media_count
    if signals["download"] is None and PACKAGE_COMMANDS.search(plain):
        signals["download"] = "package"
    if signals["download"] is None and (DOWNLOAD_HEADING.search(plain) or collect_download_signals(plain, links)):
        signals["download"] = "download-section"
    categories = sum(bool(pattern.search(plain)) for pattern in (SECTION_INSTALL, SECTION_USAGE, SECTION_FEATURES, SECTION_MEDIA))
    has_install_usage = bool(SECTION_INSTALL.search(plain)) and bool(SECTION_USAGE.search(plain))
    signals["docs_full"] = signals["docs"] and (has_install_usage or categories >= 3 or (signals["docs_bytes"] >= 4000 and categories >= 2))
    return signals


def collect_media_signals(text: str, links: list[tuple[str, str]]) -> tuple[list[str], int]:
    demo: list[str] = []
    media_count = 0
    image_urls = MARKDOWN_IMAGE.findall(text) + HTML_IMAGE.findall(text)
    kept_images = 0
    for image_url in image_urls:
        lowered = image_url.lower()
        if any(marker in lowered for marker in IMAGE_URL_EXCLUDES):
            continue
        if any(lowered.split("?")[0].endswith(extension) for extension in MEDIA_EXTENSIONS):
            kept_images += 1
    if kept_images:
        demo.append("image")
        media_count += kept_images
    video_hosts = sum(1 for link, _ in links if any(host in link.lower() for host in VIDEO_HOSTS))
    video_hosts += len(re.findall(r"https?://(?:www\.)?(?:youtube\.com/watch|youtu\.be/|player\.bilibili\.com)", text, re.IGNORECASE))
    if video_hosts:
        demo.append("video")
        media_count += video_hosts
    if any(DEMO_LINK_TEXT.search(link_text) or DEMO_LINK_TEXT.search(link) for link, link_text in links):
        demo.append("demo-link")
    return demo, media_count


def collect_download_signals(text: str, links: list[tuple[str, str]]) -> bool:
    for link, _ in links:
        lowered = link.lower()
        if any(lowered.split("?")[0].endswith(extension) for extension in DOWNLOAD_EXTENSIONS):
            return True
    return False


def classify(record: dict, signals: dict) -> tuple[int, str]:
    """Apply the class rubric to one entry; returns (class, reason)."""
    kind = record.get("kind", "")
    description = record.get("description_en", "") + " " + record.get("description_zh", "")
    complete_description = bool(DESCRIPTION_COMPLETE.search(description))
    partial_description = bool(DESCRIPTION_PARTIAL.search(description))
    if not signals["code"]:
        return 3, "no code behind the entry URL"
    if not signals["docs"]:
        return 3, "no usable documentation at the code source"
    has_download = bool(signals["download"])
    has_demo = bool(signals["demo"])
    if not (has_download or has_demo):
        return 2, "code and docs only: no download method and no demo"
    if not has_demo:
        return 2, "code and docs only: no demo"
    if not has_download:
        return 2, "code and docs only: no download method"
    if kind == "case-study":
        if complete_description and signals["docs_full"]:
            return 0, "case study documenting a complete reimplementation"
        return 1, "case study: download and demo exist, scope stays partial" if not complete_description else "case study demo is documented but docs do not cover the full feature set"
    if partial_description:
        return 1, "download and demo exist, but the described scope is a partial feature or patch"
    if signals["docs_full"]:
        return 0, "full-coverage docs, download method and demo all present"
    return 1, "download and demo exist, but docs do not cover the full feature set"


def load_catalog() -> list[dict]:
    records: list[dict] = []
    for filename in ("rea-resources.json", "tool-resources.json"):
        records.extend(json.loads((ROOT / "data" / filename).read_text(encoding="utf-8")))
    ids = [record["id"] for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate catalog IDs")
    return records


def load_overrides() -> dict[str, dict]:
    if not OVERRIDES_PATH.is_file():
        return {}
    document = json.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))
    return {entry["id"]: entry for entry in document.get("entries", [])}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token", help="GitHub token; defaults to the gh CLI token or GITHUB_TOKEN.")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS)
    parser.add_argument("--fresh", action="store_true", help="Ignore the local evidence cache and refetch.")
    args = parser.parse_args()

    token = args.token or os_environ_token()
    client = HttpClient(token, "awesome-rea-evidence-classifier")
    if args.fresh and CACHE_DIR.exists():
        for cached_file in CACHE_DIR.glob("*.json"):
            cached_file.unlink()

    records = load_catalog()
    overrides = load_overrides()

    fetches: dict[str, dict] = {}
    pending: dict[str, str] = {}
    for record in records:
        slug = github_repo_slug(record["url"])
        if slug:
            pending.setdefault(slug, record["id"])
        else:
            pending.setdefault(record["url"], record["id"])

    def fetch_one(target: str) -> tuple[str, dict]:
        slug = github_repo_slug(target)
        if slug:
            return target, github_api_fetch(client, slug)
        host = urllib.parse.urlsplit(target).hostname or ""
        if host.lower() == "gitlab.com":
            return target, gitlab_api_fetch(client, urllib.parse.urlsplit(target).path.strip("/"))
        return target, fetch_page(client, target)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for target, payload in pool.map(fetch_one, list(pending), chunksize=4):
            fetches[target] = payload
            sys.stderr.write(f"fetched {len(fetches)}/{len(pending)} {target}\r")

    entries = []
    counts = {0: 0, 1: 0, 2: 0, 3: 0}
    for record in records:
        slug = github_repo_slug(record["url"])
        meta = fetches[slug if slug else record["url"]]
        gitlab_path = None if slug else (
            urllib.parse.urlsplit(record["url"]).path.strip("/")
            if (urllib.parse.urlsplit(record["url"]).hostname or "").lower() == "gitlab.com" else None)
        signals = github_signals(meta) if slug or gitlab_path else page_signals(record["url"], meta)
        evidence_class, reason = classify(record, signals)
        entry = {
            "id": record["id"],
            "url": record["url"],
            "evidence_class": evidence_class,
            "basis": "github-rest" if slug else ("gitlab-rest" if gitlab_path else "page-fetch"),
            "signals": {key: value for key, value in signals.items() if key in (
                "code", "code_basis", "docs", "docs_bytes", "docs_full", "download",
                "release_count", "release_asset_count", "demo", "media_count", "archived", "unavailable")},
            "reason": reason,
            "checked_at": meta.get("fetched_at", now_utc()),
        }
        if record["id"] in overrides:
            correction = overrides[record["id"]]
            entry["evidence_class"] = int(correction["evidence_class"])
            entry["basis"] = "override"
            entry["reason"] = correction.get("note", "manual override")
        counts[entry["evidence_class"]] += 1
        entries.append(entry)

    document = {
        "schema_version": 1,
        "meta": {
            "spec_version": SPEC_VERSION,
            "generated_at": now_utc(),
            "entry_count": len(entries),
            "class_counts": {str(key): value for key, value in counts.items()},
            "override_count": sum(entry["basis"] == "override" for entry in entries),
            "method": "GitHub REST API observations (repo meta, releases, README) for GitHub URLs; page observations for other hosts. Manual corrections in data/evidence-class-overrides.json win. Classes measure public evidence strength only.",
            "rubric": {
                "0": "Documentation covers the full feature set, plus a download method and an image or video demo.",
                "1": "Download method and image/video demo exist, but the documented scope is partial: single features, patches, ports, investigations.",
                "2": "Demo or download missing; code and documentation exist, so buildability stays unknown.",
                "3": "No code or no documentation: progress notes or notebook entries only.",
            },
        },
        "entries": entries,
    }
    OUTPUT_PATH.write_text(json.dumps(document, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {len(entries)} entries to {OUTPUT_PATH.relative_to(ROOT)}")
    for class_value in sorted(counts):
        print(f"  class {class_value}: {counts[class_value]}")


def os_environ_token() -> str | None:
    import os
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    try:
        import subprocess
        result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True,
                                encoding="utf-8", timeout=10)
        return result.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


if __name__ == "__main__":
    main()
