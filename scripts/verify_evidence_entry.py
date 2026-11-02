#!/usr/bin/env python3
"""Verify every evidence signal for one entry URL under evidence-class-v4.

Usage:
    python3 scripts/verify_evidence_entry.py https://github.com/owner/repo
    python3 scripts/verify_evidence_entry.py https://example.org/page --fresh --json
    python3 scripts/verify_evidence_entry.py URL --kind case-study --targets game

The report shows, for the given URL:
  - code / docs / docs_full, with the detected headings;
  - download candidates: release assets, artifact links and install commands,
    including the exact command or URL and whether the frozen rule counts it;
  - demo candidates: every README/page image with alt text, heading, branding
    filter, preview score and an HTTP probe (status, content type, dimensions),
    plus video links checked through oEmbed;
  - the v4 automatic class, whether the entry is eligible for a manual Class 0
    review, and the current review status from data/evidence-class-zero-reviews.json.

It does not consult evidence-class-overrides.json: the frozen standard has no
per-entry class overrides.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_evidence_previews as previews  # noqa: E402
import classify_evidence_classes as classifier  # noqa: E402

CATALOG_FILES = ("rea-resources.json", "tool-resources.json")


def load_catalog() -> list[dict]:
    records = []
    for filename in CATALOG_FILES:
        records.extend(json.loads((ROOT / "data" / filename).read_text(encoding="utf-8")))
    return records


def find_record(url: str) -> dict | None:
    target = url.rstrip("/")
    for record in load_catalog():
        if record["url"].rstrip("/") == target:
            return record
    return None


def clear_cache(*keys: str) -> None:
    for key in keys:
        path = classifier.CACHE_DIR / (hashlib.sha256(key.encode()).hexdigest() + ".json")
        path.unlink(missing_ok=True)


def probe(client, url: str) -> dict:
    """Small HTTP check that never carries a token to a media host."""
    headers = client.headers_for(url, page=True)
    headers["Range"] = "bytes=0-4095"
    request = urllib.request.Request(url, headers=headers)
    try:
        with client.opener.open(request, timeout=15) as response:
            data = response.read(4096)
            return {
                "status": response.status,
                "content_type": response.headers.get("Content-Type", ""),
                "final_url": response.geturl(),
                "declared_bytes": response.headers.get("Content-Length"),
                "dimensions": image_dimensions(data),
            }
    except urllib.error.HTTPError as error:
        return {"status": error.code, "content_type": error.headers.get("Content-Type", "") if error.headers else ""}
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return {"status": None, "error": str(error)}


def image_dimensions(data: bytes) -> list[int] | None:
    try:
        if data[:8] == b"\x89PNG\r\n\x1a\n" and len(data) >= 24:
            width, height = struct.unpack(">II", data[16:24])
            return [width, height]
        if data[:6] in (b"GIF87a", b"GIF89a") and len(data) >= 10:
            width, height = struct.unpack("<HH", data[6:10])
            return [width, height]
        if data[:4] == b"RIFF" and data[8:12] == b"WEBP" and len(data) >= 30:
            kind = data[12:16]
            if kind == b"VP8X":
                width = int.from_bytes(data[24:27], "little") + 1
                height = int.from_bytes(data[27:30], "little") + 1
                return [width, height]
            if kind == b"VP8 ":
                width = int.from_bytes(data[26:28], "little") & 0x3FFF
                height = int.from_bytes(data[28:30], "little") & 0x3FFF
                return [width, height]
        if data[:2] == b"\xff\xd8":
            index = 2
            while index + 9 < len(data):
                if data[index] != 0xFF:
                    index += 1
                    continue
                marker = data[index + 1]
                if marker in (0xC0, 0xC1, 0xC2, 0xC3):
                    height, width = struct.unpack(">HH", data[index + 5:index + 9])
                    return [width, height]
                if marker in (0xD8, 0xD9):
                    index += 2
                    continue
                length = int.from_bytes(data[index + 2:index + 4], "big")
                index += 2 + max(length, 2)
    except (struct.error, IndexError):
        return None
    return None


def fetch(client, url: str, record: dict, fresh: bool) -> dict:
    slug = classifier.github_repo_slug(url)
    if slug:
        if fresh:
            clear_cache("gh:v3:" + slug)
        meta = classifier.github_api_fetch(client, slug)
        signals = classifier.github_signals(meta, record)
        status, body, _ = client.get(f"https://api.github.com/repos/{slug}")
        repo = json.loads(body.decode("utf-8", "replace")) if status == 200 else {}
        branch = repo.get("default_branch") or "HEAD"
        commit_status, commit_body, _ = client.get(
            f"https://api.github.com/repos/{slug}/commits/{urllib.parse.quote(branch)}")
        revision = (json.loads(commit_body.decode("utf-8", "replace")).get("sha")
                    if commit_status == 200 else branch)
        release_status, release_body, _ = client.get(
            f"https://api.github.com/repos/{slug}/releases?per_page=10")
        releases = json.loads(release_body.decode("utf-8", "replace")) if release_status == 200 else []
        return {
            "basis": "github-rest", "meta": meta, "signals": signals, "text": meta.get("readme_text") or "",
            "base": f"https://raw.githubusercontent.com/{slug}/{revision}/",
            "repo": repo, "releases": releases, "gitlab_project": None, "page_html": None,
        }
    host = (urllib.parse.urlsplit(url).hostname or "").lower()
    if host == "gitlab.com":
        path = urllib.parse.urlsplit(url).path.strip("/")
        if fresh:
            clear_cache("gl:v2:" + path)
        meta = classifier.gitlab_api_fetch(client, path)
        signals = classifier.github_signals(meta, record)
        project_status, project_body, _ = client.get(
            f"https://gitlab.com/api/v4/projects/{urllib.parse.quote(path, safe='')}")
        project = json.loads(project_body.decode("utf-8", "replace")) if project_status == 200 else {}
        branch = project.get("default_branch") or "main"
        return {
            "basis": "gitlab-rest", "meta": meta, "signals": signals, "text": meta.get("readme_text") or "",
            "base": f"https://gitlab.com/{path}/-/raw/{branch}/",
            "repo": {}, "releases": [], "gitlab_project": project, "page_html": None,
        }
    if fresh:
        clear_cache("page:" + url)
    meta = classifier.fetch_page(client, url)
    signals = classifier.page_signals(url, meta, record)
    return {
        "basis": "page-fetch", "meta": meta, "signals": signals, "text": meta.get("html") or "",
        "base": url, "repo": {}, "releases": [], "gitlab_project": None,
        "page_html": meta.get("html") or "",
    }


def markdown_links(text: str) -> list[tuple[str, str]]:
    return [(href.strip(), label) for label, href in classifier.MARKDOWN_LINK.findall(text)]


def page_links(html_text: str, base: str) -> list[tuple[str, str]]:
    return [(urllib.parse.urljoin(base, href.strip()), classifier.HTML_TAG.sub(" ", label))
            for href, label in classifier.HTML_LINK.findall(html_text)]


def image_report(fetched: dict, client) -> dict:
    text = fetched["text"]
    base = fetched["base"]
    candidates = []
    for raw, alt, position in previews.image_references(text):
        heading = previews.heading_before(text, position)
        in_media = bool(heading and previews.PREVIEW_MEDIA_HEADING.search(heading))
        url = previews.usable_image(raw, base)
        negative = bool(previews.PREVIEW_NEGATIVE.search((url or raw) + " " + alt))
        score = previews.preview_score(url, alt, in_media) if url else None
        accepted = bool(url and score is not None and score >= 0)
        entry = {
            "src": raw, "url": url, "alt": alt, "heading": heading, "in_media_section": in_media,
            "branding_filtered": negative, "preview_score": score,
            "signal_image": classifier.is_demo_image(raw, alt),
            "preview_eligible": accepted,
        }
        if accepted and not negative and len([c for c in candidates if c.get("probe")]) < 6:
            entry["probe"] = probe(client, url)
        candidates.append(entry)
    accepted_images = [c for c in candidates if c["signal_image"]]
    return {"candidates": candidates, "accepted_count": len(accepted_images),
            "signal": "image" if accepted_images else None}


def video_report(fetched: dict, client) -> list[dict]:
    text = fetched["text"]
    links = markdown_links(text) if fetched["page_html"] is None else page_links(text, fetched["base"])
    urls = [link for link, _ in links if any(host in link.lower() for host in classifier.VIDEO_HOSTS)]
    urls += re.findall(r"https?://[^\s)\]\"']*(?:youtube\.com|youtu\.be|vimeo\.com|bilibili\.com|b23\.tv)[^\s)\]\"']*",
                       text, re.IGNORECASE)
    seen = []
    for url in urls:
        if url not in seen:
            seen.append(url)
    results = []
    for url in seen[:8]:
        result = {"url": url, "provider": urllib.parse.urlsplit(url).hostname}
        match = previews.YOUTUBE_ID.search(url)
        oembed = None
        if match:
            oembed = ("https://www.youtube.com/oembed?format=json&url=https://www.youtube.com/watch?v="
                      + urllib.parse.quote(match.group(1)))
        elif "vimeo.com" in url.lower():
            oembed = "https://vimeo.com/api/oembed.json?url=" + urllib.parse.quote(url, safe="")
        if oembed:
            status, body, _ = client.get(oembed, timeout=15)
            result["oembed_status"] = status
            if status == 200:
                try:
                    data = json.loads(body.decode("utf-8", "replace"))
                    result["title"] = data.get("title")
                    result["author"] = data.get("author_name")
                except json.JSONDecodeError:
                    pass
        results.append(result)
    return results


def download_report(fetched: dict, record: dict) -> dict:
    text = fetched["text"]
    plain = classifier.CODE_BLOCK.sub(" ", text) if fetched["page_html"] is None else text
    releases = fetched["releases"]
    release_rows = []
    for release in releases[:5]:
        assets = release.get("assets") or []
        release_rows.append({
            "tag": release.get("tag_name"), "name": release.get("name"),
            "asset_count": len(assets),
            "assets": [{"name": a.get("name"), "bytes": a.get("size"), "url": a.get("browser_download_url")}
                       for a in assets[:8]],
            "counted": bool(assets),
        })
    artifact_links = []
    for href, label in markdown_links(text) + page_links(fetched["page_html"] or "", fetched["base"]):
        lowered = href.lower().split("?", 1)[0]
        if any(lowered.endswith(extension) for extension in classifier.DOWNLOAD_EXTENSIONS):
            artifact_links.append({"url": href, "label": label})
    target = classifier.target_package_name(record)
    commands = []
    for match in classifier.PACKAGE_INSTALL.finditer(text):
        package = match.group(1)
        if package.startswith("-"):
            continue
        commands.append({"command": match.group(0).strip(), "package": package,
                         "target": target, "counted": classifier.package_matches_target(package, target)})
    return {
        "value": fetched["signals"].get("download"),
        "releases": release_rows,
        "artifact_links": artifact_links,
        "install_commands": commands[:12],
        "target_package": target,
        # Target download links collected from the README, its linked documents
        # and the distribution pages it points at.
        "download_links": fetched["signals"].get("download_links") or [],
    }


def docs_report(fetched: dict) -> dict:
    signals = fetched["signals"]
    text = fetched["text"]
    if fetched["page_html"] is not None:
        plain = "\n".join("## " + classifier.HTML_TAG.sub(" ", heading).strip()
                           for heading in re.findall(r"<h[1-4][^>]*>(.*?)</h[1-4]>", text,
                                                     flags=re.IGNORECASE | re.DOTALL))
    else:
        plain = classifier.CODE_BLOCK.sub(" ", text)
    categories = []
    for name, pattern in (("install", classifier.SECTION_INSTALL), ("usage", classifier.SECTION_USAGE),
                          ("features", classifier.SECTION_FEATURES), ("media", classifier.SECTION_MEDIA)):
        headings = pattern.findall(plain)
        if headings:
            categories.append(name)
    has_install_usage = "install" in categories and "usage" in categories
    docs_bytes = signals.get("docs_bytes", 0)
    docs_full = signals.get("docs_full", False)
    return {
        "docs": signals.get("docs"), "docs_bytes": docs_bytes,
        "linked_docs_bytes": fetched["meta"].get("linked_docs_bytes", 0),
        "categories": categories, "has_install_usage": has_install_usage,
        "derivation": (has_install_usage or len(categories) >= 3
                       or (docs_bytes >= 4000 and len(categories) >= 2)),
        "docs_full": docs_full,
    }


def code_report(fetched: dict) -> dict:
    signals = fetched["signals"]
    repo = fetched["repo"] or {}
    project = fetched["gitlab_project"] or {}
    links = page_links(fetched["page_html"], fetched["base"]) if fetched["page_html"] else []
    code_links = [url for url, _ in links
                  if (urllib.parse.urlsplit(url).hostname or "").lower() in classifier.CODE_HOSTS
                  and len([p for p in urllib.parse.urlsplit(url).path.split("/") if p]) >= 2]
    return {
        "code": signals.get("code"), "code_basis": signals.get("code_basis"),
        "archived": repo.get("archived", project.get("archived")),
        "stars": repo.get("stargazers_count"),
        "default_branch": repo.get("default_branch") or project.get("default_branch"),
        "code_links": code_links[:8],
    }


def classification(fetched: dict, record: dict) -> dict:
    signals = fetched["signals"]
    unavailable = bool(signals.get("unavailable"))
    if unavailable:
        auto_class, auto_reason = None, "source unavailable or unreadable; not classified"
    else:
        auto_class, auto_reason = classifier.classify(record, signals)
    candidate = False if unavailable else classifier.is_c0_candidate(record, signals)
    eligible = False if unavailable else classifier.has_complete_evidence(record, signals)
    reviews = classifier.load_c0_reviews()
    review = reviews.get(record["id"])
    if unavailable:
        effective, status = None, "unknown"
    elif review and review.get("scope") == "full" and eligible:
        effective, status = 0, "observed"
    else:
        effective, status = auto_class, "observed"
    if effective == 0:
        scope = "full"
    elif effective == 1:
        scope = "partial" if record.get("kind") == "case-study" else "analysis"
    elif effective == 2:
        scope = "unknown"
    elif effective == 3:
        scope = "notes"
    else:
        scope = "unknown"
    return {
        "automatic_class": auto_class, "automatic_reason": auto_reason,
        "c0_candidate": candidate, "c0_evidence_eligible": eligible,
        "review": review, "effective_class": effective, "evidence_status": status,
        "scope": scope, "runtime_status": "not-run",
        "review_full_but_ineligible": bool(review and review.get("scope") == "full" and not eligible),
    }


def report_text(result: dict) -> str:
    inp = result["input"]
    src = result["source"]
    code = result["code"]
    docs = result["docs"]
    download = result["download"]
    demo = result["demo"]
    cls = result["classification"]
    lines = [
        f"=== Evidence verification: {inp['id']} ===",
        f"URL: {inp['url']}",
        f"Record: {inp['name']} | kind={inp['kind']} | targets={','.join(inp.get('targets') or []) or '-'}",
        "",
        f"SOURCE: {src['basis']} | unavailable={src['unavailable']} | archived={code['archived']} | "
        f"default branch={code['default_branch']} | README bytes={src['readme_bytes']}",
        "",
        f"CODE: {'PASS' if code['code'] else 'FAIL'} | basis={code['code_basis']} | code links={len(code['code_links'])}",
        f"DOCS: {'PASS' if docs['docs'] else 'FAIL'} | bytes={docs['docs_bytes']} (+{docs['linked_docs_bytes']} linked) | "
        f"headings={','.join(docs['categories']) or '-'} | docs_full={'PASS' if docs['docs_full'] else 'FAIL'} "
        f"(derivation={docs['derivation']})",
        "",
        f"DOWNLOAD: {'PASS' if download['value'] else 'FAIL'} | value={download['value']} | target package={download['target_package']}",
    ]
    if download["releases"]:
        for release in download["releases"]:
            asset_names = ", ".join(a["name"] for a in release["assets"]) or "-"
            lines.append(f"  release {release['tag']}: {release['asset_count']} asset(s) {asset_names} "
                         f"-> {'counted' if release['counted'] else 'TAG ONLY, not counted'}")
    else:
        lines.append("  releases: none")
    if download["artifact_links"]:
        for link in download["artifact_links"]:
            lines.append(f"  artifact link: {link['url']} -> counted (direct file link)")
    else:
        lines.append("  artifact links: none")
    if download["install_commands"]:
        for command in download["install_commands"]:
            lines.append(f"  command: {command['command']} | package={command['package']} -> "
                         f"{'counted' if command['counted'] else 'NOT counted (build dependency or different package)'}")
    else:
        lines.append("  install commands: none")
    if download["download_links"]:
        lines.append(f"  collected download links ({len(download['download_links'])}), "
                     "from README, linked docs and distribution pages:")
        for link in download["download_links"]:
            lines.append(f"    {link[:160]}")
    else:
        lines.append("  collected download links: none")
    lines += ["", f"DEMO: {'PASS' if demo['images']['accepted_count'] or demo['videos'] else 'FAIL'} | "
                  f"accepted images={demo['images']['accepted_count']} | videos={len(demo['videos'])}"]
    for image in demo["images"]["candidates"][:12]:
        probe_info = image.get("probe")
        probe_text = ""
        if probe_info:
            dims = probe_info.get("dimensions")
            probe_text = f" | HTTP {probe_info.get('status')} {probe_info.get('content_type')}" + (
                f" {dims[0]}x{dims[1]}" if dims else "")
        reason = []
        if image["branding_filtered"]:
            reason.append("branding")
        if image["preview_score"] is not None and image["preview_score"] < 0:
            reason.append("negative score")
        lines.append(f"  image {image['url'] or image['src']} | signal={'Y' if image['signal_image'] else 'N'} "
                     f"preview={'Y' if image['preview_eligible'] else 'N'} | alt={image['alt'][:40]!r} | "
                     f"heading={image['heading'][:30]!r} | score={image['preview_score']}{probe_text}"
                     + (f" | {', '.join(reason)}" if reason else ""))
    for video in demo["videos"]:
        lines.append(f"  video {video['url'][:100]} | {video.get('title') or '-'} | "
                     f"{video.get('author') or '-'} | oEmbed {video.get('oembed_status', '-')}")
    lines += [
        "",
        f"CLASS: automatic={cls['automatic_class']} ({cls['automatic_reason']})",
        f"  C0 heuristic candidate={cls['c0_candidate']} | evidence gate={cls['c0_evidence_eligible']}",
        f"  manual review={json.dumps(cls['review'], ensure_ascii=False) if cls['review'] else 'none'}",
        f"  effective={cls['effective_class']} | status={cls['evidence_status']} | scope={cls['scope']} | runtime={cls['runtime_status']}",
    ]
    if cls["review_full_but_ineligible"]:
        lines.append("  WARNING: review says scope=full but the evidence gate fails; C0 is not granted.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Entry URL to verify")
    parser.add_argument("--id", help="Catalog ID when the URL is not in the catalog")
    parser.add_argument("--kind", default="project", help="Catalog kind for an unknown URL")
    parser.add_argument("--targets", help="Comma-separated targets for an unknown URL")
    parser.add_argument("--name", help="Display name for an unknown URL")
    parser.add_argument("--fresh", action="store_true", help="Ignore the classifier cache")
    parser.add_argument("--json", action="store_true", help="Print the full JSON report")
    args = parser.parse_args()

    record = find_record(args.url)
    synthesized = record is None
    if synthesized:
        slug = classifier.github_repo_slug(args.url) or args.url
        record = {
            "id": args.id or slug, "url": args.url, "name": args.name or slug,
            "kind": args.kind or "project",
            "targets": [t.strip() for t in (args.targets or "").split(",") if t.strip()],
            "description_en": "", "description_zh": "",
        }
    client = classifier.HttpClient(classifier.os_environ_token(), "awesome-rea-evidence-verifier")
    fetched = fetch(client, args.url, record, args.fresh)
    signals = fetched["signals"]
    images = image_report(fetched, client)
    videos = video_report(fetched, client)
    result = {
        "input": {"id": record["id"], "url": args.url, "name": record.get("name"),
                  "kind": record.get("kind"), "targets": record.get("targets"),
                  "in_catalog": not synthesized},
        "source": {
            "basis": fetched["basis"], "unavailable": bool(signals.get("unavailable")),
            "readme_bytes": fetched["meta"].get("readme_bytes", 0),
            "checked_at": fetched["meta"].get("fetched_at"),
        },
        "code": code_report(fetched),
        "docs": docs_report(fetched),
        "download": download_report(fetched, record),
        "demo": {"images": images, "videos": videos, "signal": signals.get("demo")},
        "classification": classification(fetched, record),
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(report_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
