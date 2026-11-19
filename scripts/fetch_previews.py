#!/usr/bin/env python3
"""Download the demo preview images recorded in data/evidence-previews.json.

The site serves these same-origin, so the page never hotlinks an external image
and the Content-Security-Policy keeps `img-src 'self'`. Images are cached by the
SHA-256 of their URL: repeated builds reuse them, and a failed download is
retried on the next run instead of being cached as a miss.

Order of sources for one image: the local cache, the copy the live site already serves
(previews/sources.json and build-manifest.json name it and give its SHA-256), then the upstream host with
retries. An image the live site serves therefore stays on it when its host is slow, and a rebuild of a
deployed commit holds the same previews as the deployment. `--site-only` skips the upstream host, so the
IndexNow rebuild reproduces exactly what the site serves.

The command is best-effort. A missing or unreachable image leaves that entry
without a preview and does not stop the deployment.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from media_privacy import public_media_url  # noqa: E402

PREVIEWS_PATH = ROOT / "data" / "evidence-previews.json"
CACHE_DIR = ROOT / ".cache" / "previews"
MAX_BYTES = 8 * 1024 * 1024
TIMEOUT_SECONDS = 30
CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/apng": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
}
# A crawler-style agent that names the site. clonekeenplus.sourceforge.io answers 403 to a
# desktop-browser agent string and serves its images to this one.
SITE_URL = "https://awesomerea.org"
SOURCES_NAME = "previews/sources.json"
ATTEMPTS = 3
RETRY_SECONDS = 2
USER_AGENT = "Mozilla/5.0 (compatible; AwesomeREA-preview/1.0; +https://awesomerea.org)"


def cache_key(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def cached_path(url: str) -> Path | None:
    matches = sorted(CACHE_DIR.glob(cache_key(url) + ".*"))
    return matches[0] if matches else None


def extension_for(url: str, content_type: str) -> str | None:
    if content_type:
        media_type = content_type.split(";", 1)[0].strip().lower()
        if media_type in CONTENT_TYPES:
            return CONTENT_TYPES[media_type]
    lowered = url.lower().split("?", 1)[0]
    for suffix in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        if lowered.endswith(suffix):
            return ".jpg" if suffix == ".jpeg" else suffix
    return None


def read_site(path: str, limit: int, site: str = SITE_URL) -> bytes:
    request = urllib.request.Request(f"{site}/{path}", headers={"User-Agent": USER_AGENT, "Accept-Encoding": "identity"})
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        body = response.read(limit + 1)
    if len(body) > limit:
        raise ValueError("too large")
    return body


class SiteCopies:
    """The preview images the live site serves, each with the cache key of the URL it was downloaded from."""

    def __init__(self, sources: dict, files: dict, site: str = SITE_URL):
        self.sources, self.files, self.site = sources, files, site

    @classmethod
    def load(cls, site: str = SITE_URL) -> "SiteCopies | None":
        token = "?seed=" + hashlib.sha256(str(time.time()).encode()).hexdigest()[:12]
        try:
            sources = json.loads(read_site(SOURCES_NAME + token, 4 * 1024 * 1024, site))
            files = json.loads(read_site("build-manifest.json" + token, 8_000_000, site))["files"]
        except (OSError, ValueError, KeyError, TypeError):
            return None
        return cls(sources, files, site) if isinstance(sources, dict) and isinstance(files, dict) else None

    def fetch(self, entry_id: str, url: str) -> bool:
        """Store the live copy for URL in the cache when it was downloaded from URL; True when stored."""
        source = self.sources.get(entry_id)
        if not isinstance(source, dict) or source.get("key") != cache_key(url):
            return False
        name = "previews/" + str(source.get("file", ""))
        listed = self.files.get(name)
        if not isinstance(listed, dict) or not re.fullmatch(r"previews/[A-Za-z0-9][A-Za-z0-9._-]*", name):
            return False
        try:
            body = read_site(name, MAX_BYTES, self.site)
        except (OSError, ValueError):
            return False
        if len(body) != listed.get("bytes") or hashlib.sha256(body).hexdigest() != listed.get("sha256"):
            return False
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        (CACHE_DIR / (cache_key(url) + Path(name).suffix)).write_bytes(body)
        return True


def fetch(url: str, entry_id: str = "", site: "SiteCopies | None" = None, site_only: bool = False) -> str:
    """Make one image available in the cache; return a short status word."""
    if not public_media_url(url):
        return "private-url"
    if cached_path(url):
        return "cached"
    if site is not None and site.fetch(entry_id, url):
        return "from-site"
    if site_only:
        return "not-on-site"
    for attempt in range(ATTEMPTS):
        status = download(url)
        if status != "unreachable" or attempt == ATTEMPTS - 1:
            return status
        time.sleep(RETRY_SECONDS * (attempt + 1))
    return "unreachable"


def download(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "image/*"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            content_type = response.headers.get("Content-Type", "")
            extension = extension_for(url, content_type)
            if extension is None:
                return "unsupported-type"
            declared = response.headers.get("Content-Length")
            if declared and declared.isdigit() and int(declared) > MAX_BYTES:
                return "too-large"
            body = response.read(MAX_BYTES + 1)
            if len(body) > MAX_BYTES:
                return "too-large"
            if not body:
                return "empty"
    except (urllib.error.URLError, TimeoutError, OSError):
        return "unreachable"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / (cache_key(url) + extension)).write_bytes(body)
    return "downloaded"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fresh", action="store_true", help="Ignore cached images and download again.")
    parser.add_argument("--site-only", action="store_true",
                        help="Take images only from the live site's copies, never from the upstream hosts.")
    parser.add_argument("--no-site", action="store_true", help="Do not read the live site's copies.")
    args = parser.parse_args()

    if not PREVIEWS_PATH.is_file():
        print("No data/evidence-previews.json; the site will deploy without demo previews.")
        return 0
    import json
    entries = json.loads(PREVIEWS_PATH.read_text(encoding="utf-8"))["entries"]
    if args.fresh:
        for entry in entries:
            path = cached_path(entry["image_url"])
            if path:
                path.unlink()
    site = None if args.no_site else SiteCopies.load()
    if site is None and not args.no_site:
        if args.site_only:
            print("The live site's preview list is not readable, and --site-only never reads the upstream hosts.", file=sys.stderr)
            return 1
        print("The live site's preview list is not readable; images come from their upstream hosts.", file=sys.stderr)
    counts: dict[str, int] = {}

    def task(entry: dict) -> tuple[dict, str]:
        return entry, fetch(entry["image_url"], entry["id"], site, args.site_only)

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for index, (entry, status) in enumerate(pool.map(task, entries), start=1):
            counts[status] = counts.get(status, 0) + 1
            if status in ("unreachable", "not-on-site", "too-large", "unsupported-type", "empty", "private-url"):
                # Never echo the query string: private attachment URLs carry signed tokens.
                parts = urllib.parse.urlsplit(entry["image_url"])
                safe_url = urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
                print(f"preview skipped ({status}): {entry['id']} {safe_url}", file=sys.stderr)
            if index % 25 == 0 or index == len(entries):
                print(f"previews {index}/{len(entries)}", file=sys.stderr)
    summary = ", ".join(f"{count} {status}" for status, count in sorted(counts.items()))
    print(f"Preview images: {summary or 'none to fetch'}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
