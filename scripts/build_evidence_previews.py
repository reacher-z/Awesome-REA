#!/usr/bin/env python3
"""Collect one demo screenshot URL for every Class 0/1 entry.

Class 0 and Class 1 entries are the ones whose public sources carry an image or
video demo. This script reads those entries from data/evidence-classes.json and
records the first usable demo image for each: a README/page image, or the
YouTube thumbnail when the demo is a video. Entries without usable media are
left out, so the homepage simply shows no preview for them.

The URLs are captured here; scripts/build_site.py copies cached images into the
deployment as same-origin files. This script never downloads the images.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import re
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from classify_evidence_classes import (  # noqa: E402
    HTML_TAG, IMAGE_URL_EXCLUDES, HttpClient, github_repo_slug, os_environ_token,
)

CLASSES_PATH = ROOT / "data" / "evidence-classes.json"
OUTPUT_PATH = ROOT / "data" / "evidence-previews.json"
CACHE_DIR = ROOT / ".cache" / "preview-scan"
SPEC_VERSION = "evidence-preview-v1"
MAX_WORKERS = 8
# Only raster images render predictably as thumbnails; SVG is frequently a logo
# or a diagram, and videos are represented by their poster image.
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".apng")
# GitHub and Discord attachment URLs usually carry no file extension. The fetch
# step checks Content-Type before accepting a download, so a known image host is
# enough to treat an extension-less URL as a candidate.
IMAGE_HOSTS = ("user-images.githubusercontent.com", "cloud.githubusercontent.com",
               "cdn.discordapp.com", "media.discordapp.net")
YOUTUBE_ID = re.compile(
    r"(?:youtube\.com/(?:watch\?(?:[^#\s]*&)?v=|embed/|shorts/)|youtu\.be/)([A-Za-z0-9_-]{6,})",
    re.IGNORECASE)
YOUTUBE_THUMBNAIL = "https://i.ytimg.com/vi/{video}/hqdefault.jpg"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def cached(key: str) -> dict | None:
    path = CACHE_DIR / (hashlib.sha256(key.encode()).hexdigest() + ".json")
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def store_cache(key: str, payload: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / (hashlib.sha256(key.encode()).hexdigest() + ".json")
    path.write_text(json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8")


def usable_image(raw: str, base: str) -> str | None:
    """Resolve one markdown/HTML image reference to a thumbnail-able URL."""
    if not raw or raw.startswith(("data:", "blob:")):
        return None
    raw = raw.strip()
    if raw.startswith("/") and not raw.startswith("//") and "raw.githubusercontent.com" in base:
        # README root-relative paths mean the repository root, not the host root.
        url = base.rstrip("/") + raw
    else:
        url = urllib.parse.urljoin(base, raw)
    parts = urllib.parse.urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        return None
    lowered = url.lower().split("?", 1)[0]
    if any(marker in lowered for marker in IMAGE_URL_EXCLUDES):
        return None
    if not lowered.endswith(IMAGE_EXTENSIONS):
        host = (parts.hostname or "").lower()
        github_attachment = host == "github.com" and ("/user-attachments/" in lowered or "/assets/" in lowered)
        if host not in IMAGE_HOSTS and not github_attachment:
            return None
    return url


def image_references(text: str) -> list[tuple[str, str, int]]:
    """(src, alt, position) for every markdown or HTML image in the document."""
    references: list[tuple[str, str, int]] = []
    for match in re.finditer(r"!\[([^\]]*)\]\(([^)\s]+)", text):
        references.append((match.group(2), match.group(1), match.start()))
    for match in re.finditer(r"<img\b[^>]*>", text, re.IGNORECASE):
        tag = match.group(0)
        src = re.search(r"\bsrc=[\"']([^\"']+)[\"']", tag, re.IGNORECASE)
        alt = re.search(r"\balt=[\"']([^\"']*)[\"']", tag, re.IGNORECASE)
        if src:
            references.append((src.group(1), alt.group(1) if alt else "", match.start()))
    return references


MARKDOWN_HEADING = re.compile(r"^(#{1,4})[^\n#]*$", re.MULTILINE)
HTML_HEADING = re.compile(r"<h([1-4])[^>]*>([\s\S]*?)</h\1>", re.IGNORECASE)
PREVIEW_MEDIA_HEADING = re.compile(
    r"screenshots?|screen\s?shots?|demo|preview|video|images?|showcase|截图|演示|效果", re.IGNORECASE)
# An image under a chat-group, sponsor or contact heading is not a product demo.
PREVIEW_NEGATIVE_HEADING = re.compile(
    r"群|交流|联系|赞助|打赏|二维码|sponsor|donat|contact|chat|community|discord|telegram|wechat|微信",
    re.IGNORECASE)


def heading_before(text: str, position: int) -> str:
    """The nearest markdown or HTML heading text before a position."""
    found: list[tuple[int, str]] = []
    for match in MARKDOWN_HEADING.finditer(text, 0, position):
        found.append((match.start(), match.group(0).lstrip("#").strip()))
    for match in HTML_HEADING.finditer(text, 0, position):
        found.append((match.start(), re.sub(r"\s+", " ", HTML_TAG.sub(" ", match.group(2))).strip()))
    return max(found)[1] if found else ""


# A logo, a badge wall, a chat-group QR code or a funding button is not a demo.
PREVIEW_NEGATIVE = re.compile(
    r"logo|badge|icon|banner|sponsor|powered\s*by|qr\s*code|二维码|群号|加群|交流群|\bqq\b|qq\s*群|"
    r"微信|wechat|weixin|weibo|discord|telegram|t\.me|donate|patreon|ko-?fi|star[- ]history|badges?",
    re.IGNORECASE)
PREVIEW_ALT = re.compile(
    r"screenshot|screen\s?shot|demo|preview|gameplay|interface|\bui\b|截图|演示|界面|效果|运行", re.IGNORECASE)
PREVIEW_PATH = re.compile(
    r"screenshot|demo|preview|screen|capture|gameplay|showcase|截图|演示", re.IGNORECASE)


def preview_score(url: str, alt: str, in_media: bool) -> int:
    blob = url + " " + alt
    if PREVIEW_NEGATIVE.search(blob):
        return -10
    score = 2 if in_media else 0
    if PREVIEW_ALT.search(alt):
        score += 3
    if PREVIEW_PATH.search(url):
        score += 2
    if len(alt.strip()) >= 15:
        score += 1
    return score


def best_image(text: str, base: str) -> str | None:
    """The best-scored usable image, or None when every candidate looks like branding."""
    best: tuple[int, str] | None = None
    for raw, alt, position in image_references(text):
        url = usable_image(raw, base)
        if not url:
            continue
        heading = heading_before(text, position)
        if heading and PREVIEW_NEGATIVE_HEADING.search(heading):
            continue
        in_media = bool(heading and PREVIEW_MEDIA_HEADING.search(heading))
        score = preview_score(url, alt, in_media)
        # Zero means no positive signal but also no branding signal; the first such
        # image is still usually the README's hero screenshot rather than a logo.
        if score >= 0 and (best is None or score > best[0]):
            best = (score, url)
    return best[1] if best else None


def youtube_video(text: str) -> str | None:
    match = YOUTUBE_ID.search(text)
    return match.group(1) if match else None


def page_text(body: bytes) -> str:
    return body.decode("utf-8", "replace")


def github_preview(client: HttpClient, slug: str) -> dict | None:
    status, body, _ = client.get(f"https://api.github.com/repos/{slug}")
    if status != 200:
        return None
    repository = json.loads(body.decode("utf-8", "replace"))
    branch = repository.get("default_branch") or "HEAD"
    revision = branch
    commit_status, commit_body, _ = client.get(
        f"https://api.github.com/repos/{slug}/commits/{urllib.parse.quote(branch)}")
    if commit_status == 200:
        revision = json.loads(commit_body.decode("utf-8", "replace")).get("sha") or branch
    readme_status, readme_body, _ = client.get(f"https://api.github.com/repos/{slug}/readme")
    if readme_status != 200:
        return None
    readme = json.loads(readme_body.decode("utf-8", "replace"))
    try:
        import base64
        text = base64.b64decode(readme.get("content", "")).decode("utf-8", "replace")
    except (ValueError, TypeError):
        return None
    base = f"https://raw.githubusercontent.com/{slug}/{revision}/"
    image = best_image(text, base)
    if image:
        return {"image_url": image, "kind": "image", "basis": "readme-image",
                "source_url": f"https://github.com/{slug}", "revision": revision}
    video = youtube_video(text)
    if video:
        return {"image_url": YOUTUBE_THUMBNAIL.format(video=video), "kind": "video",
                "basis": "youtube-thumbnail",
                "source_url": f"https://github.com/{slug}", "revision": revision}
    return None


def page_preview(client: HttpClient, url: str) -> dict | None:
    status, body, _ = client.get(url, timeout=20, page=True)
    if status != 200 or not body:
        return None
    text = page_text(body)
    image = best_image(text, url)
    if image:
        return {"image_url": image, "kind": "image", "basis": "page-image",
                "source_url": url}
    video = youtube_video(HTML_TAG.sub(" ", text))
    if video:
        return {"image_url": YOUTUBE_THUMBNAIL.format(video=video), "kind": "video",
                "basis": "youtube-thumbnail", "source_url": url}
    return None


def collect(entry: dict, client: HttpClient, fresh: bool) -> dict | None:
    key = "preview:v1:" + entry["id"] + "|" + entry["url"]
    if not fresh:
        hit = cached(key)
        if hit is not None:
            return hit or None
    slug = github_repo_slug(entry["url"])
    preview = github_preview(client, slug) if slug else page_preview(client, entry["url"])
    store_cache(key, preview or {})
    return preview


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token", help="GitHub token; defaults to the gh CLI token or GITHUB_TOKEN.")
    parser.add_argument("--fresh", action="store_true", help="Ignore the local preview cache and refetch.")
    args = parser.parse_args()

    document = json.loads(CLASSES_PATH.read_text(encoding="utf-8"))
    targets = [entry for entry in document["entries"] if entry["evidence_class"] in (0, 1)]
    client = HttpClient(args.token or os_environ_token(), "awesome-rea-preview-classifier")
    previous: dict[str, dict] = {}
    if OUTPUT_PATH.is_file():
        try:
            previous = {entry["id"]: entry for entry in
                        json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))["entries"]}
        except (json.JSONDecodeError, KeyError):
            previous = {}

    entries: list[dict] = []
    missing: list[str] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(collect, entry, client, args.fresh): entry for entry in targets}
        for done, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            entry = futures[future]
            try:
                preview = future.result()
            except Exception as error:  # keep going; one bad source must not stop the run
                print(f"warning: {entry['id']}: {error}", file=sys.stderr)
                preview = None
            if preview:
                chosen = {
                    "id": entry["id"],
                    "image_url": preview["image_url"],
                    "kind": preview["kind"],
                    "basis": preview["basis"],
                    "source_url": preview["source_url"],
                    **({"revision": preview["revision"]} if preview.get("revision") else {}),
                }
                old = previous.get(entry["id"])
                unchanged = old and all(old.get(key) == value for key, value in chosen.items())
                chosen["checked_at"] = old["checked_at"] if unchanged else utc_now()
                entries.append(chosen)
            else:
                missing.append(entry["id"])
            print(f"preview {done}/{len(targets)} {entry['id']}", file=sys.stderr)

    entries.sort(key=lambda item: item["id"])
    counts = {"image": sum(item["kind"] == "image" for item in entries),
              "video": sum(item["kind"] == "video" for item in entries)}
    output = {
        "schema_version": 1,
        "meta": {
            "spec_version": SPEC_VERSION,
            "generated_at": utc_now(),
            "entry_count": len(entries),
            "class_entry_count": len(targets),
            "class_counts": counts,
            "missing_count": len(missing),
            "missing": sorted(missing),
            "method": ("First usable README/page demo image, or the YouTube poster image when the "
                       "demo is a video, for every Class 0/1 entry. URLs are resolved against the "
                       "repository revision observed at generation time. Images are downloaded at "
                       "build time and served from the site itself."),
        },
        "entries": entries,
    }
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(entries)} previews ({counts['image']} images, {counts['video']} video posters; "
          f"{len(missing)} entries without usable media) to {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
