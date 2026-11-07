#!/usr/bin/env python3
"""Download the demo preview images recorded in data/evidence-previews.json.

The site serves these same-origin, so the page never hotlinks an external image
and the Content-Security-Policy keeps `img-src 'self'`. Images are cached by the
SHA-256 of their URL: repeated builds reuse them, and a failed download is
retried on the next run instead of being cached as a miss.

The command is best-effort. A missing or unreachable image leaves that entry
without a preview and does not stop the deployment.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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
USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


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


def fetch(url: str) -> str:
    """Download one image; return a short status word."""
    if cached_path(url):
        return "cached"
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
    counts: dict[str, int] = {}

    def task(entry: dict) -> tuple[dict, str]:
        return entry, fetch(entry["image_url"])

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for index, (entry, status) in enumerate(pool.map(task, entries), start=1):
            counts[status] = counts.get(status, 0) + 1
            if status in ("unreachable", "too-large", "unsupported-type", "empty"):
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
