#!/usr/bin/env python3
"""Collect public OS package evidence for every curated software entry.

Reads GitHub release assets and README download links/install commands, then
maps each package to Windows, macOS, Linux, Android, iOS, Web, FreeBSD, source
or other. The output is a dated snapshot, not a claim that a package installs,
runs or matches the target. Non-GitHub entries are retained with an explicit
``not-collected`` source so coverage stays visible.

Usage:
    python3 scripts/collect_platform_packages.py
    python3 scripts/collect_platform_packages.py --fresh
"""
from __future__ import annotations

import argparse
import base64
import concurrent.futures
import datetime as dt
import hashlib
import json
import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from classify_evidence_classes import (  # noqa: E402
    CODE_BLOCK, HTML_LINK, HTML_TAG, MARKDOWN_LINK, PACKAGE_INSTALL, SIGNAL_TEXT_LIMIT,
    HttpClient, collect_target_download_links, github_repo_slug, os_environ_token,
    package_matches_target, target_package_name,
)

OUTPUT_PATH = ROOT / "data" / "platform-packages.json"
CACHE_DIR = ROOT / ".cache" / "platform-packages"
SPEC_VERSION = "platform-packages-v1"
SOFTWARE_KINDS = {"case-study", "project", "tool", "integration"}
MAX_WORKERS = 16
PLATFORM_ORDER = ("windows", "macos", "linux", "android", "ios", "web", "freebsd", "source", "other")
PLATFORMS = {
    "windows": ("Windows", "Windows"),
    "macos": ("macOS", "macOS"),
    "linux": ("Linux", "Linux"),
    "android": ("Android", "Android"),
    "ios": ("iOS", "iOS"),
    "web": ("Web", "Web"),
    "freebsd": ("FreeBSD", "FreeBSD"),
    "source": ("Source / package manager", "源码 / 包管理器"),
    "other": ("Other / unclassified", "其他 / 未分类"),
}
# Checksums, signatures, symbols and generated source archives are not user packages.
IGNORED_ASSET = re.compile(
    r"checksum|sha\d*(?:sum)?|\.sig$|\.asc$|\.minisig$|\.sbom$|sbom|\.json$|\.txt$|\.pdb$|"
    r"symbols|source code|\.nupkg\.sha|\.blockmap$|\.zsync$", re.I)
SOURCE_ARCHIVE = re.compile(r"source|src", re.I)


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def cache_path(key: str) -> Path:
    return CACHE_DIR / (hashlib.sha256(key.encode()).hexdigest() + ".json")


def read_cache(key: str) -> dict | None:
    path = cache_path(key)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def write_cache(key: str, payload: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path(key).write_text(json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8")


def usable_asset(asset: dict) -> bool:
    name = asset.get("name") or ""
    url = asset.get("url") or ""
    size = asset.get("size")
    return bool(name and url.startswith("https://") and not IGNORED_ASSET.search(name)
                and (not isinstance(size, int) or size >= 1000))


def fetch_repo(client: HttpClient, slug: str) -> dict:
    cached = read_cache(slug)
    if cached:
        return cached
    release_status, release_body, _ = client.get(f"https://api.github.com/repos/{slug}/releases?per_page=100")
    if release_status not in (200, 404):
        release_status, release_body, _ = client.get(f"https://api.github.com/repos/{slug}/releases?per_page=10")
    if release_status not in (200, 404):
        return {"unavailable": True, "fetched_at": now_utc()}
    releases = json.loads(release_body.decode("utf-8", "replace")) if release_status == 200 else []
    # Current availability: the newest stable release, plus the newest
    # prerelease only when it is newer. Do not fall back to an old release with
    # assets: a current tag without assets is not evidence of a current package.
    stable = [release for release in releases if not release.get("draft") and not release.get("prerelease")]
    prereleases = [release for release in releases if not release.get("draft") and release.get("prerelease")]
    stable_release = max(stable, key=lambda release: release.get("published_at") or release.get("created_at") or "",
                         default=None)
    prerelease_release = max(prereleases, key=lambda release: release.get("published_at") or release.get("created_at") or "",
                             default=None)
    if (prerelease_release and stable_release
            and (prerelease_release.get("published_at") or "") <= (stable_release.get("published_at") or "")):
        prerelease_release = None
    selected = [release for release in (stable_release, prerelease_release) if release]
    readme_status, readme_body, _ = client.get(f"https://api.github.com/repos/{slug}/readme")
    readme_text = ""
    if readme_status == 200:
        readme = json.loads(readme_body.decode("utf-8", "replace"))
        readme_text = base64.b64decode(readme.get("content", "")).decode("utf-8", "replace")
    payload = {
        "unavailable": False,
        "release_scope": "latest-stable+latest-prerelease",
        "topics": [],
        "releases": [
            {
                "tag_name": release.get("tag_name"),
                "published_at": release.get("published_at"),
                "prerelease": bool(release.get("prerelease")),
                "assets": [
                    {
                        "name": asset.get("name") or "",
                        "url": asset.get("browser_download_url") or "",
                        "size": asset.get("size"),
                    }
                    for asset in (release.get("assets") or [])
                    if asset.get("state", "uploaded") == "uploaded"
                ],
            }
            for release in selected
        ],
        "readme_text": readme_text[:SIGNAL_TEXT_LIMIT],
        "fetched_at": now_utc(),
    }
    write_cache(slug, payload)
    return payload


def asset_platform(name: str, url: str, topics: list[str]) -> str:
    """Map one release asset or README artifact to a platform key."""
    low = f"{name} {url}".lower()
    path = urllib.parse.urlsplit(url).path.lower()
    basename = path.rsplit("/", 1)[-1]
    # ``name`` is the asset filename for releases and the basename for README
    # links. ``basename`` is a fallback when the caller passes a label.
    match = f"{name} {basename}".lower()
    end = r"(?:\s|$)"
    # Linux package formats first: .pkg.tar.zst must not fall into macOS .pkg.
    if re.search(r"linux|ubuntu|debian|fedora|centos|rhel|appimage|alpine|"
                 r"\.deb" + end + r"|\.rpm" + end + r"|\.flatpak" + end + r"|\.snap" + end + r"|"
                 r"\.pkg\.tar\.(?:zst|xz|gz|bz2)" + end, match):
        return "linux"
    if re.search(r"mac(?:os|osx)?|osx|darwin|\.dmg" + end + r"|\.pkg" + end, match):
        return "macos"
    if re.search(r"windows|win(?:32|64)?[-_. ]|\.exe" + end + r"|\.msi" + end + r"|\.msix" + end + r"|"
                 r"\.appx" + end + r"|\.appinstaller" + end, match):
        return "windows"
    if re.search(r"\.ipa" + end + r"|\bios\b|iphone|ipad", match):
        return "ios"
    if re.search(r"\.apk" + end + r"|\.aab" + end + r"|\.xapk" + end + r"|\.apks" + end + r"|android", match):
        if "alpine" in match or "alpine" in topics:
            return "linux"
        return "android"
    if "freebsd" in match:
        return "freebsd"
    if re.search(r"wasm|webassembly|emscripten|\.wasm" + end, match):
        return "web"
    if re.search(r"(?:^|[-_.])web(?:[-_.]|$)", match):
        return "web"
    if re.search(r"\.whl" + end + r"|\.jar" + end + r"|\.nupkg" + end + r"|\.gem" + end + r"|\.crate" + end, match) \
            or SOURCE_ARCHIVE.search(match):
        return "source"
    return "other"


def command_platform(command: str) -> str:
    """Classify a package-manager command by its target OS."""
    low = command.lower()
    if re.search(r"\bbrew\b", low):
        return "macos"
    if re.search(r"\b(?:winget|choco|chocolatey|scoop)\b", low):
        return "windows"
    if re.search(r"\b(?:apt(?:-get)?|dnf|yum|pacman|zypper|flatpak|snap)\b", low) or "apk add" in low:
        return "linux"
    if re.search(r"\b(?:pip|pipx|uv|npm|npx|pnpm|yarn|bun|bunx|cargo|go|gem|conda|dotnet|luarocks)\b", low):
        return "source"
    return "other"


def descriptor(platform: str, name: str, url: str | None, kind: str,
               tag: str | None = None, published_at: str | None = None,
               prerelease: bool = False) -> dict:
    item = {"platform": platform, "name": name.strip(), "url": url or None, "kind": kind}
    if tag:
        item["tag"] = tag
    if published_at:
        item["published_at"] = published_at
    if prerelease:
        item["prerelease"] = True
    return item


def package_descriptors(record: dict, payload: dict) -> tuple[dict[str, list[dict]], str]:
    topics = payload.get("topics") or []
    found: dict[str, list[dict]] = {key: [] for key in PLATFORM_ORDER}

    def add(item: dict) -> None:
        platform = item["platform"]
        key = (platform, item["name"], item["url"])
        if not any((existing["platform"], existing["name"], existing["url"]) == key
                   for existing in found[platform]):
            found[platform].append(item)

    for release in payload.get("releases") or []:
        for asset in release.get("assets") or []:
            if not usable_asset(asset):
                continue
            name, url = asset["name"], asset["url"]
            platform = asset_platform(name, url, topics)
            add(descriptor(platform, name, url, "release-asset", release.get("tag_name"),
                           release.get("published_at"), release.get("prerelease", False)))

    readme = payload.get("readme_text") or ""
    if readme:
        plain = CODE_BLOCK.sub(" ", readme)
        links = [(href.strip(), text) for text, href in MARKDOWN_LINK.findall(plain)]
        links += [(href.strip(), HTML_TAG.sub(" ", text)) for href, text in HTML_LINK.findall(readme)]
        target = target_package_name(record)
        if target:
            for item in collect_target_download_links(readme, links, target):
                if item.startswith(("http://", "https://")):
                    basename = urllib.parse.urlsplit(item).path.rsplit("/", 1)[-1]
                    platform = asset_platform(basename, item, topics)
                    if platform in ("windows", "macos", "linux", "android", "ios", "web", "freebsd"):
                        add(descriptor(platform, basename or item, item, "readme-link"))
                else:
                    add(descriptor(command_platform(item), item, None, "install-command"))
            for match in PACKAGE_INSTALL.finditer(readme):
                if not package_matches_target(match.group(1), target):
                    continue
                command = match.group(0).strip()
                add(descriptor(command_platform(command), command, None, "install-command"))

    keys = [key for key in PLATFORM_ORDER if found[key]]
    source = "github-releases+readme"
    if keys:
        reason = (f"{sum(len(found[key]) for key in keys)} package/install signals across "
                  + ", ".join(keys))
    else:
        reason = "no release assets or target install commands were found"
    return {key: found[key] for key in keys}, reason


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token", help="GitHub token; defaults to the gh CLI token or GITHUB_TOKEN.")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS)
    parser.add_argument("--fresh", action="store_true", help="Ignore the local package cache and refetch.")
    args = parser.parse_args()

    if args.fresh and CACHE_DIR.exists():
        for path in CACHE_DIR.glob("*.json"):
            path.unlink()

    records = []
    for filename in ("rea-resources.json", "tool-resources.json"):
        records.extend(json.loads((ROOT / "data" / filename).read_text(encoding="utf-8")))
    software = [record for record in records if record.get("kind") in SOFTWARE_KINDS]
    if len({record["id"] for record in software}) != len(software):
        raise SystemExit("Curated software IDs must be unique")

    slugs = {}
    for record in software:
        slug = github_repo_slug(record["url"])
        if slug:
            slugs.setdefault(slug, record["id"])
    client = HttpClient(args.token or os_environ_token(), "awesome-rea-platform-packages")
    payloads: dict[str, dict] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(fetch_repo, client, slug): slug for slug in slugs}
        for done, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            slug = futures[future]
            try:
                payloads[slug] = future.result()
            except Exception as error:  # one bad repository must not stop the snapshot
                print(f"warning: {slug}: {error}", file=sys.stderr)
                payloads[slug] = {"unavailable": True, "fetched_at": now_utc()}
            if done % 25 == 0 or done == len(futures):
                print(f"fetched {done}/{len(futures)}", file=sys.stderr)

    entries = []
    platform_entry_counts = {key: 0 for key in PLATFORM_ORDER}
    platform_package_counts = {key: 0 for key in PLATFORM_ORDER}
    collected = 0
    unavailable = 0
    non_github = 0
    for record in software:
        slug = github_repo_slug(record["url"])
        if not slug:
            non_github += 1
            entries.append({
                "id": record["id"], "name": record["name"], "url": record["url"],
                "repo": None, "source": "not-collected", "checked_at": now_utc(),
                "platforms": {}, "platform_keys": [],
                "reason": "non-GitHub source; package collection was not attempted",
            })
            continue
        payload = payloads.get(slug) or {"unavailable": True, "fetched_at": now_utc()}
        if payload.get("unavailable"):
            unavailable += 1
            entries.append({
                "id": record["id"], "name": record["name"], "url": record["url"],
                "repo": slug, "source": "unavailable", "checked_at": payload.get("fetched_at") or now_utc(),
                "platforms": {}, "platform_keys": [],
                "reason": "repository or release metadata was unavailable; not classified as no packages",
            })
            continue
        platforms, reason = package_descriptors(record, payload)
        keys = [key for key in PLATFORM_ORDER if platforms.get(key)]
        if keys:
            collected += 1
            for key in keys:
                platform_entry_counts[key] += 1
                platform_package_counts[key] += len(platforms[key])
        entries.append({
            "id": record["id"], "name": record["name"], "url": record["url"],
            "repo": slug, "source": "github-releases+readme",
            "checked_at": payload.get("fetched_at") or now_utc(),
            "release_scope": payload.get("release_scope"),
            "platforms": platforms, "platform_keys": keys, "reason": reason,
        })

    document = {
        "schema_version": 1,
        "meta": {
            "spec_version": SPEC_VERSION,
            "generated_at": now_utc(),
            "entry_count": len(entries),
            "software_entry_count": len(software),
            "github_entry_count": len(software) - non_github,
            "collected_entry_count": collected,
            "unavailable_entry_count": unavailable,
            "non_github_entry_count": non_github,
            "platform_entry_counts": platform_entry_counts,
            "platform_package_counts": platform_package_counts,
            "release_scope": "latest-stable+latest-prerelease",
            "method": ("GitHub REST assets from the latest stable release and the latest prerelease, plus README download "
                       "links/install commands, for curated software entries. Asset names and install managers map to the "
                       "platform key. Non-GitHub entries are retained as not-collected; unavailable repositories are not "
                       "treated as having no packages."),
            "limits": [
                "A package name or install command does not prove that the package installs, runs or matches the target.",
                "Release asset names can be ambiguous; .zip/.7z without an OS hint are recorded as other.",
                "README links are only collected when they name the target software; unrelated links are ignored.",
                "Non-GitHub pages and the automated scan index were not collected in this snapshot.",
                "Collection date and per-entry checked_at describe the public metadata, not a runtime test.",
            ],
        },
        "entries": entries,
    }
    OUTPUT_PATH.write_text(json.dumps(document, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {len(entries)} entries to {OUTPUT_PATH.relative_to(ROOT)}")
    print("  platforms: " + ", ".join(f"{key}={platform_entry_counts[key]}" for key in PLATFORM_ORDER))
    print(f"  collected={collected}, unavailable={unavailable}, non-GitHub={non_github}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
