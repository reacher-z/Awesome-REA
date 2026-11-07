#!/usr/bin/env python3
"""Assign evidence classes to every curated catalog entry.

Reads data/rea-resources.json and data/tool-resources.json, observes public
evidence for each entry's URL (GitHub REST API, or the page itself for other
hosts), and writes data/evidence-classes.json. The automatic rubric caps at
Class 1; Class 0 needs a manual scope review:

- Class 0: a manually confirmed full software reconstruction (`kind:
  case-study`). Its scope, version and primary evidence are recorded in
  data/evidence-class-zero-reviews.json.
- Class 1: download method and non-branding image/video demo exist, but the
  documented scope is partial, or the entry is not a software reconstruction.
  This is the automatic maximum.
- Class 2: demo or download missing, but code and documentation exist.
- Class 3: no code or no documentation — notes or progress only.
- Unknown: the source was unavailable or unreadable; evidence_class is null
  rather than treating the entry as notes.

Scope, evidence strength and runtime status are separate fields. Nothing here
is a runtime verification. Observed signals stay in the output for audit. There
are no per-entry class overrides; data/evidence-class-zero-reviews.json holds
the manual Class 0 review.
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

from media_privacy import public_media_url

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / ".cache" / "evidence-scan"
OUTPUT_PATH = ROOT / "data" / "evidence-classes.json"
C0_REVIEWS_PATH = ROOT / "data" / "evidence-class-zero-reviews.json"
SPEC_VERSION = "evidence-class-v4"
README_MIN_BYTES = 400
# Very long READMEs (curated awesome lists) make the link/install regular
# expressions needlessly expensive; the first window is enough to observe
# installation, usage and demo signals.
SIGNAL_TEXT_LIMIT = 80_000
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
# A demo image is a raster screenshot, not branding, a badge wall, a progress
# chart or a chat-group invitation.
DEMO_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".apng")
DEMO_IMAGE_EXCLUDES = re.compile(
    r"logo|badge|icon|banner|sponsor|powered\s*by|qr\s*code|二维码|群号|加群|\bqq\b|qq\s*群|"
    r"微信|wechat|weixin|discord|telegram|donate|patreon|ko-?fi|star[- ]history|shields|"
    r"progress|license|\bci\b|downloads?",
    re.IGNORECASE)
DEMO_IMAGE_HOSTS = ("user-images.githubusercontent.com", "cloud.githubusercontent.com",
                    "cdn.discordapp.com", "media.discordapp.net")
MARKDOWN_IMAGE_WITH_ALT = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)")
HTML_IMAGE_TAG = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
# Files that only appear when an author ships something to run.
DOWNLOAD_EXTENSIONS = (".apk", ".exe", ".dmg", ".msi", ".appimage", ".deb", ".rpm", ".whl",
                       ".vsix", ".crx", ".xpi", ".ipa", ".tar.gz", ".7z")
PACKAGE_INSTALL = re.compile(
    r"(?:npm\s+(?:i|install)(?:\s+(?:-[gD]|--global|--save-dev|--save))*"
    r"|npx(?:\s+(?:-y|--yes))*|bunx(?:\s+(?:-y|--yes))*"
    r"|bun\s+(?:add|install|create)(?:\s+(?:-g|--global))*"
    r"|yarn\s+(?:add|dlx|global\s+add)|pnpm\s+(?:add|dlx)"
    r"|pip\s+install|pipx\s+install|uv\s+(?:tool\s+install|run)|cargo\s+install"
    r"|go\s+install|brew\s+install|gem\s+install|conda\s+install"
    r"|dotnet\s+tool\s+(?:install|update)|winget\s+install|scoop\s+install|choco\s+install"
    r"|luarocks\s+install|pacman\s+-S|apt(?:-get)?\s+install)"
    r"\s+([^\s`'\"<>|&;]+)", re.IGNORECASE)
DEMO_LINK_TEXT = re.compile(r"\b(demo|playable|live\s+preview|try\s+it\s+(?:out|online)|online\s+demo)\b", re.IGNORECASE)

SECTION_INSTALL = re.compile(r"^#{1,4}[^\n#]*\b(install|installation|build|setup|getting\s+started|get\s+started|quick\s?start|compil|prerequisit|requirement)", re.MULTILINE | re.IGNORECASE)
SECTION_USAGE = re.compile(r"^#{1,4}[^\n#]*\b(usage|use|example|how\s+to|getting\s+started|get\s+started|quick\s?start|run)", re.MULTILINE | re.IGNORECASE)
SECTION_FEATURES = re.compile(r"^#{1,4}[^\n#]*\b(features?|capabilities|功能|highlights|what\s+it\s+does)", re.MULTILINE | re.IGNORECASE)
SECTION_MEDIA = re.compile(r"^#{1,4}[^\n#]*\b(screenshots?|demo|preview|video|images?|showcase)", re.MULTILINE | re.IGNORECASE)
MARKDOWN_IMAGE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")
MARKDOWN_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)")
HTML_IMAGE = re.compile(r"<img[^>]*\bsrc=[\"']([^\"']+)", re.IGNORECASE)
# Anchor text runs long on modern pages (icon + label inside one button), so the
# captured text cap is generous; </a> still anchors the match.
HTML_LINK = re.compile(r"<a[^>]*\bhref=[\"']([^\"']+)[\"'][^>]*>([\s\S]{0,600}?)</a>", re.IGNORECASE)
HTML_TAG = re.compile(r"<[^>]+>")
CODE_BLOCK = re.compile(r"```.*?```", re.DOTALL)
DESCRIPTION_COMPLETE = re.compile(
    r"\bre-?implements?\b|\bre-?implementation\b|\bcomplete\s+(?:re)?implementation\b"
    r"|\bfull\s+(?:re)?implementation\b"
    # "clean-room Rust implementation of Word" still describes a full reconstruction.
    r"|\bclean[- ]room\s+(?:[\w-]+\s+){0,3}(?:re)?implementation\b"
    r"|\bfully\s+(?:playable|functional)\b"
    r"|\bplayable\s+(?:port|recreation|reimplementation)\b|\bfaithful\s+(?:port|recreation)\b"
    r"|\bdrop-?in\s+replacement\b|\bcompatible\s+replacement\b", re.IGNORECASE)
DESCRIPTION_PARTIAL = re.compile(
    r"\b(?:one|single|a)\s+(?:rule|function|feature|mechanic|screen|scene|routine|helper|command|aspect|level|room)\b"
    r"|\bpartial(?:ly)?\b|\bpatch(?:es|ing)?\b|\bteaching\s+case\b|\bproof\s+of\s+concept\b"
    r"|\brecover(?:s|ing|ed)?\b|\breconstruct(?:s|ing|ed)?\b|\bport(?:s|ing|ed)\b|\bsingle\s+\S+\s+(?:feature|file)\b",
    re.IGNORECASE)


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


API_ORIGINS = ("api.github.com",)


class _AuthStrippingRedirect(urllib.request.HTTPRedirectHandler):
    """Never forward credentials to a different origin after a redirect."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected is not None:
            old = urllib.parse.urlsplit(req.full_url)
            target = urllib.parse.urlsplit(newurl)
            if (old.scheme, old.hostname, old.port) != (target.scheme, target.hostname, target.port):
                for container in (redirected.headers, redirected.unredirected_hdrs):
                    container.pop("Authorization", None)
        return redirected


def retry_seconds(headers: dict) -> float | None:
    """Seconds to wait for a rate-limited request; None when it is not one."""
    retry_after = headers.get("Retry-After") or headers.get("retry-after")
    if retry_after and retry_after.isdigit():
        return float(retry_after)
    reset = headers.get("X-RateLimit-Reset") or headers.get("x-ratelimit-reset")
    if reset and reset.isdigit():
        return max(float(reset) - time.time(), 1.0)
    return None


class HttpClient:
    """Small shared client so the run stays inside the API rate budget."""

    def __init__(self, token: str | None, user_agent: str, api_origins: tuple[str, ...] = API_ORIGINS):
        self.token = token
        self.api_origins = {origin.lower() for origin in api_origins}
        self.headers = {"User-Agent": user_agent, "Accept": "application/vnd.github+json"}
        # Plain API calls stay identified; rendered pages need a browser-like
        # User-Agent because several hosts answer scripts with 403/406.
        self.page_headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                             "(KHTML, like Gecko) Chrome/126.0 Safari/537.36", "Accept": "text/html,*/*;q=0.8"}
        self.opener = urllib.request.build_opener(_AuthStrippingRedirect())

    def headers_for(self, url: str, page: bool = False) -> dict[str, str]:
        """Auth is sent only to the configured API origins, never to pages or other hosts."""
        if page:
            return dict(self.page_headers)
        headers = dict(self.headers)
        parts = urllib.parse.urlsplit(url)
        if self.token and parts.scheme == "https" and (parts.hostname or "").lower() in self.api_origins:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def get(self, url: str, timeout: int = 30, page: bool = False) -> tuple[int, bytes, dict]:
        request = urllib.request.Request(url, headers=self.headers_for(url, page))
        try:
            with self.opener.open(request, timeout=timeout) as response:
                return response.status, response.read(), dict(response.headers)
        except urllib.error.HTTPError as error:
            body = error.read() if error.fp is not None else b""
            headers = dict(error.headers or {})
            for _ in range(2):
                # Rate limits wait out their window; transient 5xx get a short
                # pause (frida/frida's releases payload, for one, 504s often).
                if error.code in (403, 429):
                    wait = retry_seconds(headers)
                elif error.code in (502, 503, 504):
                    wait = 2.0
                else:
                    wait = None
                if wait is None:
                    break
                time.sleep(min(wait, 120.0) + 1.0)
                request = urllib.request.Request(url, headers=self.headers_for(url, page))
                try:
                    with self.opener.open(request, timeout=timeout) as response:
                        return response.status, response.read(), dict(response.headers)
                except urllib.error.HTTPError as retry_error:
                    error = retry_error
                    body = retry_error.read() if retry_error.fp is not None else b""
                    headers = dict(retry_error.headers or {})
                except (urllib.error.URLError, TimeoutError, OSError):
                    return 0, b"", {}
            return error.code, body, headers
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
    cached_payload = cached("gh:v4:" + slug)
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
    if meta.get("private") or str(meta.get("visibility", "")).lower() == "private":
        # The token can read repositories the catalog may not publish; leave them
        # unobserved and uncached so no private metadata or README text is stored.
        return {"unavailable": True, "fetched_at": now_utc()}
    release_status, release_body, _ = client.get(f"https://api.github.com/repos/{slug}/releases?per_page=100")
    if release_status not in (200, 404):
        # Huge release histories (frida, for one) can 504 on the full page; a
        # smaller page still proves downloadable assets exist.
        release_status, release_body, _ = client.get(f"https://api.github.com/repos/{slug}/releases?per_page=10")
    readme_status, readme_body, _ = client.get(f"https://api.github.com/repos/{slug}/readme")
    if release_status != 200 or readme_status not in (200, 404):
        # A throttled subrequest must not record half a repository as real data:
        # miss the cache so a rerun observes the repository whole.
        return {"unavailable": True, "fetched_at": now_utc()}
    releases = json.loads(release_body.decode("utf-8", "replace")) if release_status == 200 else []
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
        "download_links": [],
        "fetched_at": now_utc(),
    }
    target = normalized_package(slug.split("/")[-1])
    markdown_links, external_links = [], []

    def readme_link(raw: str) -> str:
        # README decorations leak invisible characters into URLs; a request with
        # one would crash the client, so only clean ASCII links are followed.
        link = raw.strip().strip("<>")
        if link.isascii() and not re.search(r"\s", link):
            return link
        return ""

    def followable(link: str) -> bool:
        # Distribution pages live outside the code host: the repo's own raw
        # files and release pages are covered by the REST payload already, and
        # "raw.githubusercontent.com" does not contain "github.com" as a
        # substring, so the code-host check needs the wider exclusion.
        lowered = link.lower()
        return (link.startswith(("http://", "https://"))
                and not any(marker in lowered for marker in IMAGE_URL_EXCLUDES)
                and not any(host_part in lowered for host_part in ("github.com", "githubusercontent.com", "gitlab.com", "gitee.com")))

    for _, raw in MARKDOWN_LINK.findall(readme_text):
        link = readme_link(raw)
        if not link:
            continue
        if re.search(r"\.(md)\b", link, re.IGNORECASE):
            markdown_links.append(link)
        elif followable(link):
            external_links.append(link)
    for raw, _ in HTML_LINK.findall(readme_text):
        link = readme_link(raw)
        if not link:
            continue
        if not link.startswith(("http://", "https://")):
            if re.search(r"\.(md)\b", link, re.IGNORECASE):
                markdown_links.append(link)
        elif followable(link):
            external_links.append(link)
    # The download link often lives outside the README: in linked documents such
    # as INSTALL.md, or on the distribution page the README points at. Read the
    # linked Markdown for a stub README (the docs signal) and always scan linked
    # pages and documents for the target's own download links. Pages whose URL
    # names the target (getartcraft.com/apps/cadcraft) or that speak of
    # downloads are read first; a README that links sibling apps must not crowd
    # the target's own page out.
    def external_priority(link: str) -> tuple[int, int]:
        path_tail = urllib.parse.urlsplit(link).path.rstrip("/").rsplit("/", 1)[-1]
        names_target = 0 if artifact_basename_matches_target(path_tail, target) else 1
        speaks_download = 0 if re.search(r"download|install|releases", link.lower()) else 1
        return names_target, speaks_download

    external_links.sort(key=external_priority)
    fetched_bytes = 0
    for link in dict.fromkeys(markdown_links[:2]):
        if link.startswith(("http://", "https://")):
            if "raw.githubusercontent.com" not in link:
                continue
            link = link.split("/", 4)[-1]
        path = link.lstrip("./")
        if not re.fullmatch(r"[\w./-]+\.md", path, re.IGNORECASE):
            continue
        doc_status, doc_body, _ = client.get(f"https://raw.githubusercontent.com/{slug}/HEAD/{path}")
        if doc_status != 200:
            continue
        doc_text = doc_body.decode("utf-8", "replace")
        if 0 < payload["readme_bytes"] < README_MIN_BYTES:
            fetched_bytes += len(doc_body)
        download_links = payload["download_links"]
        download_links.extend(collect_target_download_links(
            doc_text, [(href.strip(), "") for href, _ in MARKDOWN_LINK.findall(doc_text)], target))
        payload["download_links"] = dedupe_strings(download_links)
    for page_url in dict.fromkeys(external_links[:2]):
        page_status, page_body, _ = client.get(page_url, timeout=20, page=True)
        if page_status != 200:
            continue
        html_text = page_body.decode("utf-8", "replace")
        base_url = urllib.parse.urlsplit(page_url).geturl()
        page_links = [(urllib.parse.urljoin(base_url, href.strip()), "") for href, _ in HTML_LINK.findall(html_text)]
        page_text = HTML_TAG.sub(" ", html_module.unescape(re.sub(
            r"<(script|style)[^>]*>[\s\S]*?</\1>", " ", html_text, flags=re.IGNORECASE)))
        if not fetched_bytes and 0 < payload["readme_bytes"] < README_MIN_BYTES:
            # A README that only points at a documentation site: read that page's text.
            fetched_bytes = len(re.sub(r"\s+", " ", page_text).strip().encode("utf-8"))
        download_links = payload["download_links"]
        download_links.extend(collect_target_download_links(page_text, page_links, target))
        payload["download_links"] = dedupe_strings(download_links)
    payload["linked_docs_bytes"] = fetched_bytes
    payload["download_links"] = payload["download_links"][:8]
    store_cache("gh:v4:" + slug, payload)
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


def normalized_package(value: str) -> str:
    """The package part of an install command, without version or registry prefix."""
    value = value.strip().strip("`'\"")
    if value.startswith("@"):
        _, _, value = value.partition("/")
    else:
        value = re.split(r"[@=<>~^]", value)[0]
    value = value.rsplit("/", 1)[-1]
    return re.sub(r"[^a-z0-9]", "", value.lower())


def package_matches_target(raw_package: str, target: str) -> bool:
    """Exact package name, or a package prefixed with the target token (rea-agents vs rea)."""
    value = raw_package.strip().strip("`'\"")
    if value.startswith("@"):
        _, _, value = value.partition("/")
    else:
        value = re.split(r"[@=<>~^]", value)[0]
    value = value.rsplit("/", 1)[-1]
    normalized = re.sub(r"[^a-z0-9]", "", value.lower())
    if normalized == target:
        return True
    first = re.split(r"[-_.]", value, maxsplit=1)[0]
    return re.sub(r"[^a-z0-9]", "", first.lower()) == target and len(target) >= 3


def target_package_name(record: dict) -> str | None:
    """The repository name, used to tell a target install from a build dependency."""
    url = record.get("url", "")
    slug = github_repo_slug(url)
    if slug:
        candidate = slug.split("/")[-1]
    else:
        parts = [part for part in urllib.parse.urlsplit(url).path.split("/") if part]
        if not parts:
            return None
        candidate = parts[1] if (urllib.parse.urlsplit(url).hostname or "").lower() == "gitlab.com" and len(parts) > 1 else parts[-1]
    name = normalized_package(candidate)
    return name or None


def has_target_install(text: str, record: dict) -> bool:
    """A package command that installs the target software, not a build dependency."""
    target = target_package_name(record)
    if not target:
        return False
    return any(package_matches_target(match.group(1), target)
               for match in PACKAGE_INSTALL.finditer(text[:SIGNAL_TEXT_LIMIT]))


def artifact_basename_matches_target(basename: str, target: str | None) -> bool:
    """A name that is or starts with the target itself (cadcraft, cadcraft-0.15.1-linux.deb)."""
    if not target:
        return False
    normalized = re.sub(r"[^a-z0-9]", "", basename.lower())
    return normalized.startswith(target) and len(normalized) >= len(target)


def dedupe_strings(items: list[str]) -> list[str]:
    """First-occurrence order, empties dropped."""
    return list(dict.fromkeys(item for item in items if item))


def collect_target_download_links(text: str, links: list[tuple[str, str]], target: str | None) -> list[str]:
    """Concrete download links and install commands for the target software.

    Everything an evaluator could click or run: release-asset direct links,
    artifact files named after the target, and package commands installing it.
    Links to the project's own download pages stay out; only the links a user
    would actually download through are evidence.
    """
    if not target:
        return []
    text = text[:SIGNAL_TEXT_LIMIT]
    found: list[str] = []
    for link, _ in links:
        path = urllib.parse.urlsplit(link).path
        basename = path.rsplit("/", 1)[-1]
        lowered = link.lower().split("?")[0]
        if not basename or lowered.endswith(MEDIA_EXTENSIONS):
            continue
        if lowered.endswith(DOWNLOAD_EXTENSIONS) and artifact_basename_matches_target(basename, target):
            found.append(link)
        elif "/releases/download/" in lowered and artifact_basename_matches_target(basename, target):
            found.append(link)
    for match in PACKAGE_INSTALL.finditer(text):
        if package_matches_target(match.group(1), target):
            found.append(match.group(0).strip())
    return dedupe_strings(found)[:8]


def page_signals(url: str, page: dict, record: dict) -> dict:
    """Signals for a non-GitHub URL: does the page carry code links, docs, media?"""
    signals = {"code": False, "code_basis": None, "docs": False, "docs_bytes": 0, "docs_full": False,
               "download": None, "release_count": 0, "release_asset_count": 0,
               "demo": [], "media_count": 0, "download_links": [], "archived": False,
               "unavailable": bool(page.get("unavailable"))}
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
    text = re.sub(r"\s+", " ", text).strip()[:SIGNAL_TEXT_LIMIT]
    signals["docs_bytes"] = len(text.encode("utf-8"))
    signals["docs"] = signals["docs_bytes"] >= README_MIN_BYTES
    heading_lines = "\n".join(
        "## " + HTML_TAG.sub(" ", heading).strip()
        for heading in re.findall(r"<h[1-4][^>]*>(.*?)</h[1-4]>", html_text, flags=re.IGNORECASE | re.DOTALL))
    categories = sum(bool(pattern.search(heading_lines)) for pattern in
                     (SECTION_INSTALL, SECTION_USAGE, SECTION_FEATURES, SECTION_MEDIA))
    has_install_usage = bool(SECTION_INSTALL.search(heading_lines)) and bool(SECTION_USAGE.search(heading_lines))
    signals["docs_full"] = signals["docs"] and (
        has_install_usage or categories >= 3 or (signals["docs_bytes"] >= 4000 and categories >= 2))
    demo, media_count = collect_media_signals(html_text, links)
    signals["demo"] = demo
    signals["media_count"] = media_count
    if collect_download_signals(text, links):
        signals["download"] = "file-links"
    elif has_target_install(text, record):
        signals["download"] = "package"
    signals["download_links"] = collect_target_download_links(text, links, target_package_name(record))
    if signals["download"] is None and signals["download_links"]:
        signals["download"] = "artifact-links"
    return signals


def github_signals(meta: dict, record: dict) -> dict:
    readme_text = (meta.get("readme_text") or "")[:SIGNAL_TEXT_LIMIT]
    signals = {"code": True, "code_basis": "repo", "docs": False, "docs_bytes": meta.get("readme_bytes", 0),
               "docs_full": False, "download": None, "release_count": meta.get("release_count", 0),
               "release_asset_count": meta.get("release_asset_count", 0), "demo": [], "media_count": 0,
               "download_links": [], "archived": bool(meta.get("archived")),
               "unavailable": bool(meta.get("unavailable"))}
    # A release tag without an attached artifact is not a usable download.
    if meta.get("release_asset_count"):
        signals["download"] = "release-assets"
    if meta.get("unavailable") or not readme_text:
        return signals
    signals["docs"] = (signals["docs_bytes"] + meta.get("linked_docs_bytes", 0)) >= README_MIN_BYTES
    plain = CODE_BLOCK.sub(" ", readme_text)
    links = [(href.strip(), text) for text, href in MARKDOWN_LINK.findall(plain)]
    # HTML READMEs (the *craft series, for example) carry their links as tags.
    links += [(href.strip(), HTML_TAG.sub(" ", link_text)) for href, link_text in HTML_LINK.findall(readme_text)]
    demo, media_count = collect_media_signals(plain, links)
    signals["demo"] = demo
    signals["media_count"] = media_count
    # Download links are collected from the README, its linked documents and the
    # distribution pages it points at; the concrete links stay in the signals.
    download_links = collect_target_download_links(readme_text, links, target_package_name(record))
    signals["download_links"] = dedupe_strings(download_links + list(meta.get("download_links") or []))
    # Install commands count inside fenced code blocks, but only when they name the target itself.
    if signals["download"] is None and has_target_install(readme_text, record):
        signals["download"] = "package"
    if signals["download"] is None and collect_download_signals(plain, links):
        signals["download"] = "file-links"
    if signals["download"] is None and signals["download_links"]:
        signals["download"] = "artifact-links"
    categories = sum(bool(pattern.search(plain)) for pattern in (SECTION_INSTALL, SECTION_USAGE, SECTION_FEATURES, SECTION_MEDIA))
    has_install_usage = bool(SECTION_INSTALL.search(plain)) and bool(SECTION_USAGE.search(plain))
    signals["docs_full"] = signals["docs"] and (has_install_usage or categories >= 3 or (signals["docs_bytes"] >= 4000 and categories >= 2))
    return signals


def is_demo_image(src: str, alt: str) -> bool:
    """A usable demo image: raster, and not branding, a badge or a chat invite."""
    if not src or DEMO_IMAGE_EXCLUDES.search(src + " " + alt):
        return False
    if "://" in src and not public_media_url(src):
        return False
    path = src.lower().split("?", 1)[0]
    if path.endswith(DEMO_IMAGE_EXTENSIONS):
        return True
    host = (urllib.parse.urlsplit(src).hostname or "").lower()
    if host in DEMO_IMAGE_HOSTS:
        return True
    return host in ("github.com", "www.github.com") and ("/user-attachments/" in path or "/assets/" in path)


def collect_media_signals(text: str, links: list[tuple[str, str]]) -> tuple[list[str], int]:
    demo: list[str] = []
    media_count = 0
    kept_images = 0
    for alt, src in MARKDOWN_IMAGE_WITH_ALT.findall(text):
        if is_demo_image(src, alt):
            kept_images += 1
    for tag in HTML_IMAGE_TAG.findall(text):
        src = re.search(r"\bsrc=[\"']([^\"']+)[\"']", tag, re.IGNORECASE)
        alt = re.search(r"\balt=[\"']([^\"']*)[\"']", tag, re.IGNORECASE)
        if src and is_demo_image(src.group(1), alt.group(1) if alt else ""):
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


def has_complete_evidence(record: dict, signals: dict) -> bool:
    """Minimum evidence for a manually reviewed Class 0 entry."""
    return bool(signals["code"] and signals["docs"] and signals["docs_full"] and signals["download"]
                and signals["demo"] and record.get("kind") == "case-study"
                and "binary" not in (record.get("targets") or []))


def is_c0_candidate(record: dict, signals: dict) -> bool:
    """The evidence heuristic suggests a complete reconstruction; still needs manual review."""
    if not has_complete_evidence(record, signals):
        return False
    description = record.get("description_en", "") + " " + record.get("description_zh", "")
    return bool(DESCRIPTION_COMPLETE.search(description)) and bool(signals["docs_full"])


def classify(record: dict, signals: dict) -> tuple[int, str]:
    """Apply the evidence rubric; the automatic result never exceeds Class 1."""
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
            return 1, "full reconstruction candidate: Class 0 requires manual scope review"
        return 1, "case study: download and demo exist, scope stays partial" if not complete_description else "case study demo is documented but docs do not cover the full feature set"
    if partial_description:
        return 1, "download and demo exist, but the described scope is a partial feature or patch"
    if signals["docs_full"]:
        return 1, "complete evidence, but this is not a software reconstruction"
    return 1, "download and demo exist, but docs do not cover the full feature set"


def load_catalog() -> list[dict]:
    records: list[dict] = []
    for filename in ("rea-resources.json", "tool-resources.json"):
        records.extend(json.loads((ROOT / "data" / filename).read_text(encoding="utf-8")))
    ids = [record["id"] for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate catalog IDs")
    return records


def load_c0_reviews() -> dict[str, dict]:
    """Manual Class 0 reviews: scope, version and primary evidence per entry."""
    if not C0_REVIEWS_PATH.is_file():
        return {}
    document = json.loads(C0_REVIEWS_PATH.read_text(encoding="utf-8"))
    return {entry["id"]: entry for entry in document.get("entries", [])}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token", help="GitHub token; defaults to the gh CLI token or GITHUB_TOKEN.")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS)
    parser.add_argument("--fresh", action="store_true", help="Ignore the local evidence cache and refetch.")
    parser.add_argument("--ids", help="Comma-separated catalog IDs to classify; default every record.")
    parser.add_argument("--merge", action="store_true",
                        help="Merge an --ids run into the existing output instead of writing a partial file.")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH,
                        help="Output path; useful for an incremental partial run.")
    args = parser.parse_args()
    if args.merge and not args.ids:
        raise SystemExit("--merge requires --ids")
    if args.ids and not args.merge and args.output == OUTPUT_PATH:
        raise SystemExit("Refusing to overwrite the full evidence classes with a partial --ids run; pass --merge.")

    token = args.token or os_environ_token()
    client = HttpClient(token, "awesome-rea-evidence-classifier")
    if args.fresh and CACHE_DIR.exists():
        for cached_file in CACHE_DIR.glob("*.json"):
            cached_file.unlink()

    records = load_catalog()
    if args.ids:
        wanted = {identifier.strip() for identifier in args.ids.split(",") if identifier.strip()}
        known = {record["id"] for record in records}
        missing = sorted(wanted - known)
        if missing:
            raise SystemExit("Unknown catalog IDs: " + ", ".join(missing))
        records = [record for record in records if record["id"] in wanted]
    c0_reviews = load_c0_reviews()

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
    unknown_count = 0
    c0_review_count = 0

    def scope_for(record: dict, evidence_class: int) -> str:
        if evidence_class == 0:
            return "full"
        if evidence_class == 1:
            return "partial" if record.get("kind") == "case-study" else "analysis"
        if evidence_class == 2:
            return "unknown"
        return "notes"

    for record in records:
        slug = github_repo_slug(record["url"])
        meta = fetches[slug if slug else record["url"]]
        gitlab_path = None if slug else (
            urllib.parse.urlsplit(record["url"]).path.strip("/")
            if (urllib.parse.urlsplit(record["url"]).hostname or "").lower() == "gitlab.com" else None)
        signals = github_signals(meta, record) if slug or gitlab_path else page_signals(record["url"], meta, record)
        basis = "github-rest" if slug else ("gitlab-rest" if gitlab_path else "page-fetch")
        candidate = is_c0_candidate(record, signals)
        unavailable = bool(signals.get("unavailable"))
        rubric_class, reason = classify(record, signals)
        entry = {
            "id": record["id"],
            "url": record["url"],
            "evidence_class": None if unavailable else rubric_class,
            "basis": basis,
            "signals": {key: value for key, value in signals.items() if key in (
                "code", "code_basis", "docs", "docs_bytes", "docs_full", "download", "download_links",
                "release_count", "release_asset_count", "demo", "media_count", "archived", "unavailable")},
            "reason": reason,
            "checked_at": meta.get("fetched_at", now_utc()),
            "evidence_status": "unknown" if unavailable else "observed",
            "scope": "unknown" if unavailable else scope_for(record, rubric_class),
            "runtime_status": "not-run",
            "c0_candidate": candidate,
        }
        if unavailable:
            entry["reason"] = "source unavailable or unreadable; not classified"
            unknown_count += 1
        else:
            evidence_class = rubric_class
            if evidence_class == 0:
                # The automatic rubric never assigns Class 0; only the manual review below may.
                evidence_class = 1
                entry["reason"] = ("full reconstruction candidate: Class 0 requires manual review"
                                   if candidate else "not a full software reconstruction: analysis entry")
            review = c0_reviews.get(record["id"])
            if review and review.get("scope") == "full" and has_complete_evidence(record, signals):
                evidence_class = 0
                entry["basis"] = "manual-review"
                entry["reason"] = review.get("note") or "manually confirmed full reconstruction"
                entry["review"] = {
                    "version": review.get("version"),
                    "primary_evidence": review.get("primary_evidence"),
                    "reviewed_at": review.get("reviewed_at"),
                    "note": review.get("note"),
                }
                c0_review_count += 1
            entry["evidence_class"] = evidence_class
            entry["scope"] = scope_for(record, evidence_class)
            counts[evidence_class] += 1
        entries.append(entry)

    if args.merge:
        existing = json.loads(args.output.read_text(encoding="utf-8"))
        merged = {entry["id"]: entry for entry in existing.get("entries", [])}
        for entry in entries:
            merged[entry["id"]] = entry
        order = [record["id"] for record in load_catalog()]
        entries = [merged[identifier] for identifier in order if identifier in merged]
        missing = [identifier for identifier in order if identifier not in merged]
        if missing:
            raise SystemExit("Merged evidence classes are missing catalog IDs: " + ", ".join(missing[:5]))
        counts = {0: 0, 1: 0, 2: 0, 3: 0}
        unknown_count = 0
        c0_review_count = 0
        for entry in entries:
            if entry["evidence_class"] is None:
                unknown_count += 1
                continue
            counts[entry["evidence_class"]] += 1
            if entry["evidence_class"] == 0:
                c0_review_count += 1

    document = {
        "schema_version": 1,
        "meta": {
            "spec_version": SPEC_VERSION,
            "generated_at": now_utc(),
            "entry_count": len(entries),
            "class_counts": {str(key): value for key, value in counts.items()},
            "unknown_count": unknown_count,
            "c0_review_count": c0_review_count,
            "c0_review_file": "data/evidence-class-zero-reviews.json",
            "method": ("GitHub REST API observations (repo meta, releases, README) for GitHub URLs; page observations for other hosts. "
                       "The automatic rubric caps at Class 1. Class 0 requires a manual review of scope, version and primary evidence in "
                       "data/evidence-class-zero-reviews.json. Unavailable or unreadable sources are marked unknown, not as notes. "
                       "Each entry keeps its own checked_at; Class 0 reviews may pin a later README commit than the signal observation."),
            "rubric": {
                "0": "A manually confirmed full software reconstruction (kind: case-study) whose scope, version and primary evidence were reviewed. The automatic rubric never assigns Class 0.",
                "1": "Automatic maximum: download and non-branding demo exist; scope may be partial, or the entry is a tool, integration, guide or binary-analysis entry.",
                "2": "Demo or download missing; code and documentation exist, so buildability stays unknown.",
                "3": "No code or no documentation: progress notes or notebook entries only.",
                "unknown": "Source unavailable or unreadable at review time; not classified.",
            },
        },
        "entries": entries,
    }
    args.output.write_text(json.dumps(document, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    try:
        shown = args.output.relative_to(ROOT)
    except ValueError:
        shown = args.output
    print(f"wrote {len(entries)} entries to {shown}")
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
