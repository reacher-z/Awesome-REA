#!/usr/bin/env python3
"""Route catalog entries to rule-based quality evaluation.

The evidence classifier reads public documentation and release metadata. This
scorer is the next layer: it turns those preliminary signals into an
evaluation route, acquires only the artifacts that route needs, and runs
versioned rules in a sandbox. Documentation alone never produces a quality
score.

Usage:
    python3 scripts/quality_scoring.py --plan --all
    python3 scripts/quality_scoring.py --plan --entry woxi-case --online
    python3 scripts/quality_scoring.py --score --entry woxi-case --download --allow-execution --inspect-source

Safety:
  - Downloaded files live in their own directory under .cache/quality-scan.
  - Archives are inspected without extraction; extraction is path-checked and
    never happens on the host interpreter's import path.
  - Rules run only inside a Docker container with no network, a read-only SUT
    mount and resource limits. They never run on the host.
  - A rule pack selects a local image by name; images are never pulled
    implicitly. Record the image digest in the evaluation output.

No per-entry score override exists. Rule packs contain tests, not scores; the
aggregation below is the same for every entry.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / ".cache" / "quality-scan"
OUTPUT_PATH = ROOT / "data" / "quality-evaluations.json"
CANDIDATES_PATH = ROOT / "data" / "evaluation-candidates.json"
RULE_DIR = ROOT / "quality-rules"
SPEC_VERSION = "quality-eval-v1"
SCHEMA_VERSION = 1
MAX_DOWNLOAD_BYTES = 512 * 1024 * 1024
MAX_EXTRACT_BYTES = 2 * 1024 * 1024 * 1024
MAX_ARCHIVE_ENTRIES = 20_000
MAX_XML_BYTES = 1 * 1024 * 1024

# The nine evaluation dimensions from the rule-based evaluation guide, plus
# artifact integrity, which is the minimum evidence for a downloadable build.
DIMENSIONS = {
    "artifact_integrity": "Artifact downloaded, hashed and inspected",
    "functional_coverage": "Features reached and exercised",
    "correctness": "Observed results match independent rules",
    "performance": "Latency, throughput and resource behaviour",
    "security_isolation": "User isolation, permissions and secret handling",
    "ui_consistency": "UI state and visual comparison",
    "persistence_recovery": "Data survives restart, backup and failure",
    "concurrency": "Concurrent operations keep the promised model",
    "file_formats": "Import, export and external-consumer compatibility",
    "reproducibility": "Pinned inputs, versions and repeatable runs",
}

LEVELS = (
    "L0-evidence",
    "L1-source-static",
    "L2-artifact-static",
    "L3-runtime-smoke",
    "L4-functional-rules",
    "L5-full-quality",
)
# A score is verified quality at the depth the route reached. Static evidence
# cannot produce the same ceiling as a behavioural rule pack.
LEVEL_WEIGHT = {
    "L0-evidence": 0.0,
    "L1-source-static": 0.2,
    "L2-artifact-static": 0.4,
    "L3-runtime-smoke": 0.6,
    "L4-functional-rules": 1.0,
    "L5-full-quality": 1.0,
}

SOFTWARE_KINDS = {"case-study", "project", "tool", "integration"}
STRUCTURAL_KINDS = {"documentation", "collection", "learning-resource", "research"}
DOWNLOAD_EXTENSIONS = (
    ".apk", ".appinstaller", ".appimage", ".deb", ".dmg", ".exe", ".ipa",
    ".msi", ".msix", ".msixbundle", ".pkg", ".rpm", ".tar.gz", ".tgz",
    ".vsix", ".whl", ".zip", ".7z",
)
ARCHIVE_EXTENSIONS = (".tar.gz", ".tgz", ".zip")
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)\s]+)\)")
HTML_HREF = re.compile(r"<a[^>]*\bhref=[\"']([^\"']+)[\"']", re.IGNORECASE)
PACKAGE_COMMAND = re.compile(
    r"^(?:npm\s+(?:i|install)|npx|bunx|bun\s+(?:add|install)|yarn\s+(?:add|dlx)|"
    r"pnpm\s+(?:add|dlx)|pip\s+install|pipx\s+install|uv\s+(?:tool\s+install|run)|"
    r"cargo\s+install|go\s+install|brew\s+install|gem\s+install|conda\s+install|"
    r"dotnet\s+tool\s+(?:install|update)|winget\s+install|scoop\s+install|"
    r"choco\s+install|luarocks\s+install|pacman\s+-S|apt(?:-get)?\s+install)\b",
    re.IGNORECASE,
)


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def load_candidates(path: Path | None = None) -> list[dict]:
    """Explicit non-catalog evaluation candidates.

    A candidate is not a curated catalog record and never renders on the site.
    It exists so the scorer can evaluate a named project (for example a
    tracker Class 0 candidate that has no downloadable artifact) without
    silently promoting it into the catalog.
    """
    path = path or CANDIDATES_PATH
    if not path.is_file():
        return []
    document = json.loads(path.read_text(encoding="utf-8"))
    return document.get("entries", [])


def load_catalog(candidates_path: Path | None = None) -> dict[str, dict]:
    records: dict[str, dict] = {}
    for filename in ("rea-resources.json", "tool-resources.json"):
        for record in json.loads((ROOT / "data" / filename).read_text(encoding="utf-8")):
            record = dict(record)
            record["catalog_status"] = "curated"
            records[record["id"]] = record
    for record in load_candidates(candidates_path):
        record = dict(record)
        if record["id"] in records:
            raise ValueError(f"candidate duplicates a curated ID: {record['id']}")
        record["catalog_status"] = "candidate"
        records[record["id"]] = record
    return records


def load_evidence(candidates_path: Path | None = None) -> dict[str, dict]:
    path = ROOT / "data" / "evidence-classes.json"
    evidence: dict[str, dict] = {}
    if path.is_file():
        document = json.loads(path.read_text(encoding="utf-8"))
        evidence.update({entry["id"]: entry for entry in document.get("entries", [])})
    for record in load_candidates(candidates_path):
        if record.get("evidence"):
            evidence[record["id"]] = record["evidence"]
    return evidence


def repo_slug(url: str) -> str | None:
    parts = urllib.parse.urlsplit(url)
    if (parts.hostname or "").lower() not in {"github.com", "www.github.com"}:
        return None
    path = [part for part in parts.path.split("/") if part]
    return f"{path[0]}/{path[1]}" if len(path) >= 2 else None


def platform_for_name(name: str) -> str | None:
    lowered = name.lower()
    if any(token in lowered for token in ("apple-darwin", "darwin", "macos", "osx")) or lowered.endswith((".dmg", ".pkg")):
        return "macos"
    if any(token in lowered for token in ("windows", "win32", "win64", "pc-windows")) or lowered.endswith(
            (".exe", ".msi", ".appinstaller", ".msix", ".msixbundle")):
        return "windows"
    if any(token in lowered for token in ("linux", "unknown-linux")) or lowered.endswith(
            (".appimage", ".deb", ".rpm")):
        return "linux"
    if lowered.endswith(".apk"):
        return "android"
    if lowered.endswith(".ipa"):
        return "ios"
    return None


def arch_for_name(name: str) -> str | None:
    lowered = name.lower()
    if any(token in lowered for token in ("aarch64", "arm64")):
        return "arm64"
    if any(token in lowered for token in ("x86_64", "amd64", "x64")):
        return "x64"
    if "universal" in lowered:
        return "universal"
    return None


def artifact_format(name: str) -> str:
    lowered = name.lower()
    for extension in sorted(DOWNLOAD_EXTENSIONS, key=len, reverse=True):
        if lowered.endswith(extension):
            return extension.lstrip(".")
    return "unknown"


def artifact_from_url(url: str, *, source: str, release_tag: str | None = None,
                      size: int | None = None) -> dict | None:
    path = urllib.parse.urlsplit(url).path
    name = path.rstrip("/").rsplit("/", 1)[-1]
    if not name or not any(name.lower().split("?")[0].endswith(ext) for ext in DOWNLOAD_EXTENSIONS):
        return None
    return {
        "name": name,
        "url": url,
        "source": source,
        "release_tag": release_tag,
        "platform": platform_for_name(name),
        "arch": arch_for_name(name),
        "format": artifact_format(name),
        "declared_bytes": size,
    }


def package_artifact(command: str) -> dict:
    return {
        "name": command,
        "url": None,
        "source": "package-command",
        "release_tag": None,
        "platform": "any",
        "arch": "any",
        "format": "package-command",
        "declared_bytes": None,
    }


def readme_artifact_links(record: dict) -> list[dict]:
    """Concrete artifact URLs already present in the cached README.

    The v4 classifier deliberately records only strong download evidence. The
    quality scorer needs the actual files, so it reads the same cached README
    and accepts the wider set of installer extensions (for example
    ``.appinstaller``). This is a scoring rule, not an entry override.
    """
    slug = repo_slug(record["url"])
    if not slug:
        return []
    cache_path = ROOT / ".cache" / "evidence-scan" / (
        hashlib.sha256(("gh:v3:" + slug).encode()).hexdigest() + ".json")
    if not cache_path.is_file():
        return []
    try:
        text = json.loads(cache_path.read_text(encoding="utf-8")).get("readme_text") or ""
    except (OSError, json.JSONDecodeError):
        return []
    artifacts = []
    for raw in MARKDOWN_LINK.findall(text) + HTML_HREF.findall(text):
        link = raw.strip().strip("<>")
        if not link.startswith(("http://", "https://")):
            continue
        artifact = artifact_from_url(link, source="readme-link")
        if artifact:
            artifacts.append(artifact)
    return dedupe_artifacts(artifacts)


def artifacts_from_evidence(record: dict, evidence: dict | None) -> list[dict]:
    signals = (evidence or {}).get("signals") or {}
    artifacts: list[dict] = []
    for link in signals.get("download_links") or []:
        if link.startswith(("http://", "https://")):
            artifact = artifact_from_url(link, source="download-link")
            if artifact:
                artifacts.append(artifact)
        elif PACKAGE_COMMAND.search(link):
            artifacts.append(package_artifact(link))
    artifacts.extend(readme_artifact_links(record))
    if signals.get("download") == "release-assets" and not any(
            artifact.get("source") == "release-asset" for artifact in artifacts):
        # The cached evidence records the release count but not asset names.
        # --online replaces this placeholder with the real assets.
        artifacts.append({
            "name": None, "url": None, "source": "release-assets", "release_tag": None,
            "platform": None, "arch": None, "format": "release-asset", "declared_bytes": None,
        })
    return dedupe_artifacts(artifacts)


def dedupe_artifacts(artifacts: list[dict]) -> list[dict]:
    seen: set[tuple] = set()
    result = []
    for artifact in artifacts:
        key = (artifact.get("url"), artifact.get("name"), artifact.get("source"))
        if key in seen:
            continue
        seen.add(key)
        result.append(artifact)
    return result


def infer_interfaces(record: dict, evidence: dict | None, artifacts: list[dict], rule_pack: dict | None) -> list[str]:
    if rule_pack:
        interfaces = (rule_pack.get("sut") or {}).get("sandbox", {}).get("interfaces") or []
        if interfaces:
            return sorted(set(interfaces))
    targets = set(record.get("targets") or [])
    text = " ".join([
        record.get("description_en", ""), record.get("description_zh", ""),
        " ".join(record.get("requirements") or []),
    ]).lower()
    interfaces: set[str] = set()
    if "website" in targets or any(token in text for token in ("web app", "web application", "browser", "http server", "localhost")):
        interfaces.add("web")
    if any(token in text for token in ("command line", "command-line", "cli", "terminal", "interpreter")):
        interfaces.add("cli")
    if "game" in targets:
        interfaces.add("game")
    if any(token in text for token in ("desktop", "gui", "window", "toolbox", "editor", "interface")):
        interfaces.add("gui")
    for artifact in artifacts:
        fmt = artifact.get("format")
        if fmt in {"dmg", "exe", "msi", "appinstaller", "msix", "msixbundle", "appimage"}:
            interfaces.add("gui")
        elif fmt in {"deb", "rpm", "tar.gz", "tgz"}:
            interfaces.add("cli")
        elif fmt == "whl":
            interfaces.add("library")
    if "protocol" in targets:
        interfaces.add("service")
    return sorted(interfaces)


def supports_software(record: dict) -> bool:
    return record.get("kind") in SOFTWARE_KINDS


def sandbox_for(profile: dict, rule_pack: dict | None) -> dict:
    if not rule_pack:
        return {"name": None, "supported": False, "reason": "no rule pack"}
    sandbox = (rule_pack.get("sut") or {}).get("sandbox") or {}
    image = sandbox.get("image")
    if not image:
        return {"name": None, "supported": False, "reason": "rule pack has no sandbox image"}
    return {
        "name": "docker-linux",
        "image": image,
        "network": bool(sandbox.get("network", False)),
        "timeout_seconds": int(sandbox.get("timeout_seconds", 60)),
        "supported": True,
        "reason": None,
    }


def route_entry(record: dict, evidence: dict | None, artifacts: list[dict],
                rule_pack: dict | None) -> dict:
    signals = (evidence or {}).get("signals") or {}
    if not supports_software(record):
        return {
            "level": "L0-evidence",
            "tools": ["catalog-metadata"],
            "blocked": [{"tool": "runtime", "reason": "not a software entry"}],
            "reason": "catalog entry is not software",
        }
    if (evidence or {}).get("evidence_status") == "unknown":
        return {
            "level": "L0-evidence",
            "tools": [],
            "blocked": [{"tool": "all", "reason": "source unreadable"}],
            "reason": "source unavailable; no reliable route",
        }
    interfaces = infer_interfaces(record, evidence, artifacts, rule_pack)
    sandbox = sandbox_for({}, rule_pack)
    has_code = bool(signals.get("code"))
    has_artifact = bool(artifacts)
    if rule_pack:
        if sandbox["supported"]:
            return {
                "level": "L4-functional-rules",
                "tools": ["github-metadata", "artifact-download", "archive-inspect",
                          "sandbox-runtime", "rule-pack"],
                "blocked": [],
                "reason": f"rule pack {rule_pack['entry_id']} with a sandbox",
            }
        return {
            "level": "L2-artifact-static",
            "tools": ["github-metadata", "artifact-download", "archive-inspect"],
            "blocked": [{"tool": "runtime", "reason": sandbox["reason"]}],
            "reason": "rule pack exists but no usable sandbox",
        }
    if has_artifact:
        platforms = {artifact.get("platform") for artifact in artifacts if artifact.get("platform")}
        if platforms & {"macos", "windows"}:
            reason = "requires a macOS or Windows VM sandbox; this scorer has none"
            return {
                "level": "L2-artifact-static",
                "tools": ["github-metadata", "artifact-download", "archive-inspect"],
                "blocked": [{"tool": "runtime", "reason": reason}],
                "reason": "downloadable build for another platform",
            }
        if "linux" in platforms and any(i in {"cli", "web", "service"} for i in interfaces):
            return {
                "level": "L3-runtime-smoke",
                "tools": ["github-metadata", "artifact-download", "archive-inspect", "sandbox-runtime"],
                "blocked": [{"tool": "rule-pack", "reason": "no versioned rule pack"}],
                "reason": "Linux artifact is runnable; no rule pack yet",
            }
        return {
            "level": "L2-artifact-static",
            "tools": ["github-metadata", "artifact-download", "archive-inspect"],
            "blocked": [{"tool": "runtime", "reason": "no sandbox adapter for this artifact"}],
            "reason": "downloadable artifact without a matching runtime adapter",
        }
    if has_code:
        return {
            "level": "L1-source-static",
            "tools": ["github-metadata", "source-inspection"],
            "blocked": [{"tool": "runtime", "reason": "no downloadable artifact"}],
            "reason": "source available; build and runtime are not attempted",
        }
    return {
        "level": "L0-evidence",
        "tools": ["catalog-metadata"],
        "blocked": [{"tool": "runtime", "reason": "no code or downloadable artifact"}],
        "reason": "documentation-only evidence",
    }


def build_profile(record: dict, evidence: dict | None, rule_pack: dict | None,
                  artifacts: list[dict] | None = None) -> dict:
    artifacts = artifacts if artifacts is not None else artifacts_from_evidence(record, evidence)
    signals = (evidence or {}).get("signals") or {}
    return {
        "entry_id": record["id"],
        "url": record["url"],
        "name": record.get("name"),
        "catalog_status": record.get("catalog_status", "curated"),
        "kind": record.get("kind"),
        "targets": record.get("targets") or [],
        "category": record.get("category"),
        "software": supports_software(record),
        "evidence_class": (evidence or {}).get("evidence_class"),
        "source": {
            "code": bool(signals.get("code")),
            "basis": (evidence or {}).get("basis"),
            "repo": repo_slug(record["url"]),
            "tests_declared": has_test_command(record),
            "build_manifests": [],
            "license": None,
        },
        "docs": {
            "docs": bool(signals.get("docs")),
            "docs_full": bool(signals.get("docs_full")),
            "bytes": signals.get("docs_bytes"),
        },
        "demo": signals.get("demo") or [],
        "artifacts": artifacts,
        "interfaces": infer_interfaces(record, evidence, artifacts, rule_pack),
        "sandbox": sandbox_for({}, rule_pack),
        "rule_pack": rule_pack["entry_id"] if rule_pack else None,
    }


def has_test_command(record: dict) -> bool:
    text = " ".join(record.get("requirements") or []).lower()
    return bool(re.search(r"\b(?:pytest|unittest|cargo test|npm test|go test|ctest|dotnet test|mvn test)\b", text))


def fetch_release_assets(record: dict, client=None) -> list[dict]:
    """Return release assets from the GitHub API, cached per repository."""
    slug = repo_slug(record["url"])
    if not slug:
        return []
    cache_path = CACHE_DIR / "releases" / (slug.replace("/", "__") + ".json")
    if cache_path.is_file():
        return json.loads(cache_path.read_text(encoding="utf-8")).get("assets", [])
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "awesome-rea-quality-scorer"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(f"https://api.github.com/repos/{slug}/releases?per_page=20", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            releases = json.loads(response.read().decode("utf-8", "replace"))
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
        return []
    assets = []
    for release in releases:
        for asset in release.get("assets") or []:
            artifact = artifact_from_url(
                asset.get("browser_download_url", ""), source="release-asset",
                release_tag=release.get("tag_name"), size=asset.get("size"))
            if artifact:
                assets.append(artifact)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps({"repo": slug, "assets": assets}, indent=1) + "\n", encoding="utf-8")
    return assets


TREE_MANIFESTS = {
    "Cargo.toml", "package.json", "pyproject.toml", "setup.py", "CMakeLists.txt",
    "Makefile", "go.mod", "build.gradle", "pom.xml", "Gemfile", "composer.json",
}
SOURCE_EXTENSIONS = {
    ".py", ".rs", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".c", ".cc",
    ".cpp", ".h", ".hpp", ".go", ".java", ".kt", ".cs", ".swift", ".m", ".mm",
    ".rb", ".php", ".lua", ".sh", ".zig", ".nim",
}


def github_json(url: str) -> dict | None:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "awesome-rea-quality-scorer"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8", "replace"))
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
        return None


def fetch_repo_tree(record: dict) -> dict | None:
    """Read the pinned default-branch tree; no file contents are fetched."""
    slug = repo_slug(record["url"])
    if not slug:
        return None
    cache_path = CACHE_DIR / "trees" / (slug.replace("/", "__") + ".json")
    if cache_path.is_file():
        return json.loads(cache_path.read_text(encoding="utf-8"))
    repo = github_json(f"https://api.github.com/repos/{slug}")
    if not repo:
        return None
    branch = repo.get("default_branch") or "main"
    tree = github_json(f"https://api.github.com/repos/{slug}/git/trees/"
                       f"{urllib.parse.quote(branch, safe='')}?recursive=1")
    if not tree:
        return None
    document = {
        "repo": slug,
        "branch": branch,
        "truncated": bool(tree.get("truncated")),
        "paths": [item.get("path", "") for item in tree.get("tree") or [] if item.get("path")],
    }
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(document, indent=1) + "\n", encoding="utf-8")
    return document


def source_inventory(paths: list[str]) -> dict:
    lowered = [path.lower() for path in paths]
    names = [Path(path).name for path in paths]
    manifests = sorted({name for name in names if name in TREE_MANIFESTS
                        or name.endswith((".csproj", ".sln"))
                        or (name.lower().startswith("requirements") and name.lower().endswith(".txt"))})
    return {
        "path_count": len(paths),
        "license": any(name.lower().startswith(("license", "copying", "notice")) for name in names),
        "tests": any(re.search(r"(^|/)(tests?|specs?|__tests__)(/|$)", path)
                     or re.search(r"(^|/)test_[^/]+\.py$", path)
                     or re.search(r"_test\.(py|rs|go|java|cs|js|ts|rb|php)$", path)
                     or ".test." in path or ".spec." in path for path in lowered),
        "manifests": manifests[:10],
        "ci": any(path.startswith(".github/workflows/") or path in {
            ".gitlab-ci.yml", "azure-pipelines.yml", ".circleci/config.yml"} for path in lowered),
        "docs": any(path.startswith(("docs/", "doc/")) for path in lowered),
        "source_files": sum(1 for path in lowered if Path(path).suffix in SOURCE_EXTENSIONS),
    }


def source_results(paths: list[str], truncated: bool = False) -> list[dict]:
    inventory = source_inventory(paths)
    inventory["truncated"] = truncated
    results = [{
        "id": "source-inventory", "dimension": "reproducibility", "status": "pass",
        "reason": "repository tree read", "evidence": inventory,
    }]
    for key, label in (("license", "license file"), ("tests", "test files"),
                       ("manifests", "build manifest"), ("ci", "CI configuration")):
        present = bool(inventory[key])
        results.append({
            "id": f"source-{key}", "dimension": "reproducibility",
            "status": "pass" if present else "partial",
            "reason": f"{label} present" if present else f"{label} not found",
            "evidence": {key: inventory[key]},
        })
    return results


def load_rule_packs() -> dict[str, dict]:
    packs: dict[str, dict] = {}
    if not RULE_DIR.is_dir():
        return packs
    for path in sorted(RULE_DIR.glob("*.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        validate_rule_pack(document, path)
        packs[document["entry_id"]] = document
    return packs


def validate_rule_pack(document: dict, path: Path | None = None) -> None:
    label = str(path) if path else "rule pack"
    if document.get("schema_version") != 1:
        raise ValueError(f"{label}: schema_version must be 1")
    if not document.get("entry_id"):
        raise ValueError(f"{label}: entry_id is required")
    sut = document.get("sut") or {}
    if sut.get("kind") not in {"release-artifact", "source"}:
        raise ValueError(f"{label}: sut.kind must be release-artifact or source")
    for rule in document.get("rules") or []:
        if not rule.get("id") or not rule.get("dimension") or not rule.get("command"):
            raise ValueError(f"{label}: each rule needs id, dimension and command")
        if rule["dimension"] not in DIMENSIONS:
            raise ValueError(f"{label}: unknown dimension {rule['dimension']}")
        expect = rule.get("expect") or {}
        if not any(key in expect for key in ("exit_code", "stdout_equals", "stdout_contains", "stderr_contains")):
            raise ValueError(f"{label}: rule {rule['id']} has no expectation")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", name)[-120:] or "artifact"


def download_artifact(artifact: dict, destination: Path, timeout: int = 60) -> dict:
    """Download one artifact into its own directory. Never executes it."""
    if not artifact.get("url"):
        return {"status": "blocked", "reason": "artifact has no downloadable URL", "artifact": artifact}
    parts = urllib.parse.urlsplit(artifact["url"])
    if parts.scheme != "https" or not parts.hostname:
        return {"status": "blocked", "reason": "artifact URL is not HTTPS", "artifact": artifact}
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / safe_name(artifact["name"] or parts.path.rsplit("/", 1)[-1])
    declared = artifact.get("declared_bytes")
    if target.is_file() and target.stat().st_size > 0:
        return {
            "status": "pass", "cached": True, "path": str(target.relative_to(ROOT)),
            "bytes": target.stat().st_size, "sha256": sha256_file(target),
            "artifact": artifact,
        }
    request = urllib.request.Request(artifact["url"], headers={"User-Agent": "awesome-rea-quality-scorer"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            length = response.headers.get("Content-Length")
            if length and int(length) > MAX_DOWNLOAD_BYTES:
                return {"status": "blocked", "reason": "artifact exceeds the download size cap", "artifact": artifact}
            written = 0
            with target.open("wb") as file:
                for chunk in iter(lambda: response.read(1024 * 256), b""):
                    written += len(chunk)
                    if written > MAX_DOWNLOAD_BYTES:
                        file.close()
                        target.unlink(missing_ok=True)
                        return {"status": "blocked", "reason": "artifact exceeds the download size cap", "artifact": artifact}
                    file.write(chunk)
            final_url = response.geturl()
            content_type = response.headers.get("Content-Type", "")
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return {"status": "error", "reason": str(error), "artifact": artifact}
    result = {
        "status": "pass", "cached": False, "path": str(target.relative_to(ROOT)),
        "bytes": target.stat().st_size, "sha256": sha256_file(target),
        "final_url": final_url, "content_type": content_type, "artifact": artifact,
    }
    if declared is not None and int(declared) != result["bytes"]:
        result["status"] = "fail"
        result["reason"] = "downloaded size does not match the release metadata"
    return result


def inspect_archive(path: Path) -> dict:
    lowered = path.name.lower()
    try:
        if lowered.endswith((".tar.gz", ".tgz")):
            with tarfile.open(path, mode="r:gz") as archive:
                members = archive.getmembers()
                return archive_report("tar.gz", members)
        if lowered.endswith(".zip") or lowered.endswith(".whl"):
            with zipfile.ZipFile(path) as archive:
                members = archive.infolist()
                return archive_report("zip", members)
    except (tarfile.TarError, zipfile.BadZipFile, OSError) as error:
        return {"format": artifact_format(path.name), "inspectable": False, "error": str(error), "entries": []}
    if lowered.endswith(".appinstaller"):
        return inspect_appinstaller(path)
    return {
        "format": artifact_format(path.name),
        "inspectable": False,
        "entries": [],
        "note": "no archive inspector for this format",
    }


def archive_report(fmt: str, members) -> dict:
    entries = []
    unsafe = []
    total = 0
    for member in members[:MAX_ARCHIVE_ENTRIES]:
        name = getattr(member, "name", "")
        size = getattr(member, "size", 0) or 0
        total += size
        if name.startswith("/") or ".." in Path(name).parts:
            unsafe.append(name)
        entries.append({"name": name, "bytes": size,
                        "type": "dir" if getattr(member, "isdir", lambda: False)() else "file"})
    if total > MAX_EXTRACT_BYTES:
        unsafe.append(f"total uncompressed bytes exceed {MAX_EXTRACT_BYTES}")
    return {
        "format": fmt,
        "inspectable": True,
        "entries": entries[:200],
        "entry_count": len(members),
        "uncompressed_bytes": total,
        "unsafe": unsafe,
    }


def inspect_appinstaller(path: Path) -> dict:
    raw = path.read_bytes()[:MAX_XML_BYTES]
    if b"<!DOCTYPE" in raw.upper():
        return {"format": "appinstaller", "inspectable": False, "error": "DTD is not allowed", "entries": []}
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as error:
        return {"format": "appinstaller", "inspectable": False, "error": str(error), "entries": []}
    uris = [element.text for element in root.iter() if element.tag.endswith("Uri") and element.text]
    return {
        "format": "appinstaller",
        "inspectable": True,
        "root": root.tag,
        "uris": uris[:20],
        "entries": [],
    }


def extract_archive(path: Path, destination: Path) -> dict:
    """Extract into a fresh directory with traversal and size checks."""
    destination.mkdir(parents=True, exist_ok=True)
    lowered = path.name.lower()
    try:
        if lowered.endswith((".tar.gz", ".tgz")):
            with tarfile.open(path, mode="r:gz") as archive:
                members = archive.getmembers()
                if len(members) > MAX_ARCHIVE_ENTRIES:
                    return {"status": "blocked", "reason": "too many archive entries"}
                total = sum(member.size for member in members)
                if total > MAX_EXTRACT_BYTES:
                    return {"status": "blocked", "reason": "archive expands beyond the size cap"}
                for member in members:
                    if member.name.startswith("/") or ".." in Path(member.name).parts:
                        return {"status": "blocked", "reason": f"unsafe archive member: {member.name}"}
                    if member.issym() or member.islnk():
                        continue
                archive.extractall(destination, filter="data")
                return {"status": "pass", "entries": len(members), "bytes": total}
        if lowered.endswith(".zip"):
            with zipfile.ZipFile(path) as archive:
                members = archive.infolist()
                if len(members) > MAX_ARCHIVE_ENTRIES:
                    return {"status": "blocked", "reason": "too many archive entries"}
                total = sum(member.file_size for member in members)
                if total > MAX_EXTRACT_BYTES:
                    return {"status": "blocked", "reason": "archive expands beyond the size cap"}
                for member in members:
                    if member.filename.startswith("/") or ".." in Path(member.filename).parts:
                        return {"status": "blocked", "reason": f"unsafe archive member: {member.filename}"}
                    mode = (member.external_attr >> 16) & 0o170000
                    if mode == 0o120000:
                        return {"status": "blocked", "reason": f"symlink member: {member.filename}"}
                archive.extractall(destination)
                return {"status": "pass", "entries": len(members), "bytes": total}
    except (tarfile.TarError, zipfile.BadZipFile, OSError) as error:
        return {"status": "error", "reason": str(error)}
    return {"status": "blocked", "reason": "not an archive this scorer can extract"}


def docker_available() -> dict:
    try:
        result = subprocess.run(["docker", "info", "--format", "{{.ServerVersion}} {{.OSType}} {{.Architecture}}"],
                                capture_output=True, text=True, encoding="utf-8", timeout=10)
    except (OSError, subprocess.SubprocessError) as error:
        return {"available": False, "reason": str(error)}
    if result.returncode:
        return {"available": False, "reason": (result.stderr or result.stdout).strip()}
    return {"available": True, "version": result.stdout.strip()}


def docker_image_digest(image: str) -> str | None:
    try:
        result = subprocess.run(
            ["docker", "image", "inspect", image, "--format",
             "{{if .RepoDigests}}{{index .RepoDigests 0}}{{else}}{{.Id}}{{end}}"],
            capture_output=True, text=True, encoding="utf-8", timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def run_rule_in_sandbox(rule: dict, sut_dir: Path, sandbox: dict, allow_execution: bool) -> dict:
    started = time.monotonic()
    if not allow_execution:
        return {"status": "blocked", "reason": "execution disabled; pass --allow-execution",
                "duration_ms": 0}
    docker = docker_available()
    if not docker["available"]:
        return {"status": "blocked", "reason": f"docker unavailable: {docker['reason']}",
                "duration_ms": 0}
    command = rule.get("command")
    if isinstance(command, str):
        command = shlex.split(command)
    if not isinstance(command, list) or not command:
        return {"status": "error", "reason": "rule command must be a non-empty list", "duration_ms": 0}
    image = sandbox["image"]
    image_id = docker_image_digest(image)
    if image_id is None:
        return {"status": "blocked", "reason": f"local image {image} is not available; images are never pulled implicitly",
                "duration_ms": 0}
    name = f"rea-quality-{os.getpid()}-{int(time.time() * 1000)}"
    args = [
        "docker", "run", "--rm", "--name", name,
        "--network", "none",
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges",
        "--pids-limit", "256",
        "--memory", "2g",
        "--cpus", "2",
        "--read-only",
        "--tmpfs", "/tmp:rw,size=512m",
        "--entrypoint", "sh",
        "-v", f"{sut_dir.resolve()}:/sut:ro",
        "-w", "/tmp",
        image, "-lc", shlex.join(command),
    ]
    timeout = int(sandbox.get("timeout_seconds", 60))
    try:
        result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8",
                                timeout=timeout, check=False)
        status = "pass"
        outcome = {
            "status": status,
            "exit_code": result.returncode,
            "stdout": result.stdout[-4000:],
            "stderr": result.stderr[-4000:],
            "duration_ms": int((time.monotonic() - started) * 1000),
            "image": image,
            "image_id": image_id,
        }
    except subprocess.TimeoutExpired as error:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=15)
        outcome = {
            "status": "fail",
            "exit_code": None,
            "stdout": (error.stdout or "")[-4000:] if isinstance(error.stdout, str) else "",
            "stderr": "rule timed out",
            "duration_ms": int((time.monotonic() - started) * 1000),
        }
    return outcome


def expectation_matches(expect: dict, observed: dict) -> tuple[bool, str]:
    if "exit_code" in expect and observed.get("exit_code") != expect["exit_code"]:
        return False, f"exit code {observed.get('exit_code')} != {expect['exit_code']}"
    stdout = observed.get("stdout") or ""
    stderr = observed.get("stderr") or ""
    if "stdout_equals" in expect and stdout.strip() != expect["stdout_equals"]:
        return False, f"stdout {stdout.strip()!r} != {expect['stdout_equals']!r}"
    if "stdout_contains" in expect and expect["stdout_contains"] not in stdout:
        return False, f"stdout does not contain {expect['stdout_contains']!r}"
    if "stderr_contains" in expect and expect["stderr_contains"] not in stderr:
        return False, f"stderr does not contain {expect['stderr_contains']!r}"
    return True, "expectation met"


def static_checks(rule_pack: dict, sut_dir: Path) -> list[dict]:
    results = []
    for check in rule_pack.get("static") or []:
        if check.get("check") != "file-in-artifact":
            continue
        target = (sut_dir / check.get("path", "")).resolve()
        allowed = sut_dir.resolve()
        present = target.is_file() and target.is_relative_to(allowed)
        results.append({
            "id": check["id"], "dimension": check.get("dimension", "reproducibility"),
            "status": "pass" if present else "fail",
            "reason": "file present" if present else "file missing",
            "evidence": {"path": check.get("path")},
        })
    return results


def score_results(results: list[dict], applicable: list[str], level: str = "L4-functional-rules") -> dict:
    by_dimension: dict[str, list[dict]] = {}
    for result in results:
        by_dimension.setdefault(result["dimension"], []).append(result)
    dimensions = {}
    passed = failed = blocked = 0
    evaluated = 0
    for dimension in applicable:
        items = by_dimension.get(dimension, [])
        statuses = [item["status"] for item in items]
        if not items:
            status = "not-tested"
        elif "fail" in statuses:
            status = "fail"
        elif all(status == "pass" for status in statuses):
            status = "pass"
        elif "blocked" in statuses or "error" in statuses:
            status = "blocked"
        else:
            status = "partial"
        if status in {"pass", "fail", "partial"}:
            evaluated += 1
        passed += sum(1 for item in items if item["status"] == "pass")
        failed += sum(1 for item in items if item["status"] == "fail")
        blocked += sum(1 for item in items if item["status"] in {"blocked", "error"})
        values = {"pass": 1.0, "partial": 0.5, "fail": 0.0, "blocked": 0.0, "error": 0.0}
        fraction = (sum(values.get(item["status"], 0.0) for item in items) / len(items)) if items else 0.0
        dimensions[dimension] = {
            "status": status,
            "fraction": round(fraction, 3),
            "rules": [{"id": item["id"], "status": item["status"], "reason": item.get("reason")}
                      for item in items],
        }
    coverage = round(evaluated / len(applicable), 3) if applicable else 0.0
    denominator = passed + failed
    pass_rate = round(passed / denominator, 3) if denominator else None
    # The score is verified quality, not estimated quality: a rule that did
    # not run contributes nothing, a partial check earns half, and static
    # evidence has a lower ceiling than a behavioural rule pack. Coverage is
    # reported next to it so a low score from a thin rule pack cannot be read
    # as a poor product.
    weight = LEVEL_WEIGHT.get(level, 0.0)
    quality_fraction = (sum(dimensions[dimension]["fraction"] for dimension in applicable) / len(applicable)
                        if applicable else 0.0)
    score = round(100 * quality_fraction * weight, 1) if denominator else None
    all_pass = bool(applicable) and all(dimensions[dimension]["status"] == "pass" for dimension in applicable)
    verdict = "ungraded"
    if failed:
        verdict = "failed"
    elif score is not None and all_pass and level in {"L4-functional-rules", "L5-full-quality"}:
        verdict = "verified"
    elif score is not None and all_pass and level == "L2-artifact-static":
        verdict = "artifact-verified"
    elif score is not None and all_pass and level == "L1-source-static":
        verdict = "source-inspected"
    elif score is not None:
        verdict = "partially-verified"
    elif blocked:
        verdict = "blocked"
    return {
        "score": score,
        "formula": "100 * mean(dimension_fraction) * level_weight",
        "level_weight": weight,
        "quality_fraction": round(quality_fraction, 3),
        "coverage": coverage,
        "pass_rate": pass_rate,
        "all_applicable_pass": all_pass,
        "verdict": verdict,
        "counts": {"passed": passed, "failed": failed, "blocked": blocked, "evaluated_dimensions": evaluated,
                   "applicable_dimensions": len(applicable)},
        "dimensions": dimensions,
    }


def applicable_dimensions(profile: dict, route: dict) -> list[str]:
    if route["level"] == "L0-evidence":
        return ["reproducibility"]
    interfaces = set(profile.get("interfaces") or [])
    dimensions = ["reproducibility"]
    if profile.get("artifacts"):
        dimensions.append("artifact_integrity")
    if route["level"] in {"L1-source-static", "L2-artifact-static"}:
        return sorted(set(dimensions))
    dimensions += ["correctness", "functional_coverage", "performance", "security_isolation", "file_formats"]
    if "gui" in interfaces or "web" in interfaces or "game" in interfaces:
        dimensions += ["ui_consistency", "persistence_recovery"]
    if "web" in interfaces or "service" in interfaces:
        dimensions += ["concurrency"]
    return sorted(set(dimensions))


def evaluate_entry(record: dict, evidence: dict | None, rule_pack: dict | None, *,
                   online: bool, download: bool, allow_execution: bool,
                   inspect_source: bool = False) -> dict:
    artifacts = artifacts_from_evidence(record, evidence)
    if online:
        fetched = fetch_release_assets(record)
        if fetched:
            artifacts = dedupe_artifacts(
                fetched + [artifact for artifact in artifacts if artifact.get("source") != "release-assets"])
    profile = build_profile(record, evidence, rule_pack, artifacts)
    route = route_entry(record, evidence, artifacts, rule_pack)
    results: list[dict] = []
    evidence_files: dict[str, str] = {}

    if not profile["software"] or (evidence or {}).get("evidence_status") == "unknown":
        applicable = applicable_dimensions(profile, route)
        return {
            "id": record["id"], "url": record["url"], "profile": profile, "route": route,
            "results": results, "score": score_results(results, applicable, route["level"]),
            "limitations": ["not a software entry or source unreadable"],
        }

    if download:
        sut_artifact = (select_artifact(arts=artifacts, rule_pack=rule_pack)
                        if rule_pack else choose_artifact(artifacts))
        if sut_artifact is None and artifacts:
            results.append({"id": "artifact-select", "dimension": "artifact_integrity", "status": "blocked",
                            "reason": "no downloadable artifact matched the route", "evidence": {}})
        if sut_artifact is not None:
            workdir = CACHE_DIR / "work" / record["id"]
            workdir.mkdir(parents=True, exist_ok=True)
            downloaded = download_artifact(sut_artifact, workdir / "download")
            results.append({"id": "download", "dimension": "artifact_integrity",
                            "status": downloaded["status"],
                            "reason": downloaded.get("reason") or "downloaded",
                            "evidence": {key: downloaded[key] for key in ("path", "bytes", "sha256", "cached", "final_url")
                                         if key in downloaded}})
            if downloaded["status"] == "pass":
                results.append({"id": "artifact-pin", "dimension": "reproducibility", "status": "pass",
                                "reason": "artifact content is pinned by SHA-256",
                                "evidence": {"sha256": downloaded.get("sha256"), "bytes": downloaded.get("bytes")}})
                path = ROOT / downloaded["path"]
                inspected = inspect_archive(path)
                results.append({"id": "archive-inspect", "dimension": "artifact_integrity",
                                "status": "pass" if inspected.get("inspectable") else "partial",
                                "reason": inspected.get("note") or "archive inspected",
                                "evidence": {"format": inspected.get("format"), "entries": inspected.get("entry_count"),
                                             "unsafe": inspected.get("unsafe"), "uris": inspected.get("uris")}})
                sut_dir = workdir / "sut"
                if path.name.lower().endswith(ARCHIVE_EXTENSIONS):
                    extracted = extract_archive(path, sut_dir)
                    results.append({"id": "extract", "dimension": "reproducibility",
                                    "status": extracted["status"], "reason": extracted.get("reason") or "extracted",
                                    "evidence": {"entries": extracted.get("entries")}})
                    if extracted["status"] == "pass":
                        evidence_files["sut_dir"] = str(sut_dir.relative_to(ROOT))
                        if rule_pack:
                            results.extend(static_checks(rule_pack, sut_dir))
                            for rule in rule_pack.get("rules") or []:
                                observed = run_rule_in_sandbox(rule, sut_dir, profile["sandbox"], allow_execution)
                                status = observed["status"]
                                reason = observed.get("reason")
                                if status == "pass":
                                    ok, why = expectation_matches(rule.get("expect") or {}, observed)
                                    status = "pass" if ok else "fail"
                                    reason = why
                                results.append({
                                    "id": rule["id"], "dimension": rule["dimension"], "status": status,
                                    "reason": reason, "evidence": {
                                        "command": rule.get("command"),
                                        "exit_code": observed.get("exit_code"),
                                        "stdout": observed.get("stdout"),
                                        "stderr": observed.get("stderr"),
                                        "duration_ms": observed.get("duration_ms"),
                                        "image": observed.get("image"),
                                        "image_id": observed.get("image_id"),
                                    },
                                })
                elif rule_pack:
                    results.append({"id": "extract", "dimension": "reproducibility", "status": "blocked",
                                    "reason": "rule pack needs an extractable archive", "evidence": {}})
    elif rule_pack:
        results.append({"id": "download", "dimension": "artifact_integrity", "status": "blocked",
                        "reason": "download disabled; pass --download", "evidence": {}})

    if inspect_source and profile["source"]["code"]:
        tree = fetch_repo_tree(record)
        if tree:
            results.extend(source_results(tree["paths"], bool(tree.get("truncated"))))
            evidence_files["repo_tree"] = f"{tree['repo']}@{tree['branch']}"
        else:
            results.append({"id": "source-inventory", "dimension": "reproducibility",
                            "status": "blocked", "reason": "repository tree unavailable",
                            "evidence": {}})

    applicable = applicable_dimensions(profile, route)
    score = score_results(results, applicable, route["level"])
    limitations = []
    if not rule_pack:
        limitations.append("no versioned rule pack; the route stops at static evidence")
    if not allow_execution:
        limitations.append("execution disabled; no product behaviour was observed")
    if any(item["status"] == "blocked" for item in results):
        limitations.append("at least one planned tool was blocked")
    return {
        "id": record["id"], "url": record["url"], "profile": profile, "route": route,
        "results": results, "score": score, "limitations": limitations,
        "evidence_files": evidence_files,
    }


def choose_artifact(arts: list[dict]) -> dict | None:
    """First concrete artifact for a static route; placeholders have no URL."""
    for artifact in arts:
        if artifact.get("url") and artifact.get("name"):
            return artifact
    return None


def select_artifact(arts: list[dict], rule_pack: dict) -> dict | None:
    selector = ((rule_pack.get("sut") or {}).get("artifact") or {})
    pattern = selector.get("name_pattern")
    platform = selector.get("platform")
    arch = selector.get("arch")
    for artifact in arts:
        name = artifact.get("name") or ""
        if not name or not artifact.get("url"):
            continue
        if pattern and not re.fullmatch(pattern.replace("*", ".*"), name):
            continue
        if platform and artifact.get("platform") != platform:
            continue
        if arch and artifact.get("arch") != arch:
            continue
        return artifact
    return None


def plan_document(entries: list[dict], *, online: bool) -> dict:
    planned = []
    for record in entries:
        evidence = EVIDENCE.get(record["id"])
        rule_pack = RULE_PACKS.get(record["id"])
        artifacts = artifacts_from_evidence(record, evidence)
        if online:
            fetched = fetch_release_assets(record)
            if fetched:
                artifacts = dedupe_artifacts(
                    fetched + [artifact for artifact in artifacts if artifact.get("source") != "release-assets"])
        profile = build_profile(record, evidence, rule_pack, artifacts)
        route = route_entry(record, evidence, artifacts, rule_pack)
        planned.append({"id": record["id"], "url": record["url"], "profile": profile, "route": route})
    return {
        "schema_version": SCHEMA_VERSION,
        "meta": {
            "spec_version": SPEC_VERSION,
            "generated_at": now_utc(),
            "mode": "plan",
            "entry_count": len(planned),
            "candidate_count": sum(1 for entry in planned if entry["profile"].get("catalog_status") == "candidate"),
            "route_counts": count_routes(planned),
            "method": "Preliminary evidence routes each entry to the deepest applicable tool. "
                      "Planning reads catalog and cached evidence; --online also reads GitHub release assets.",
        },
        "entries": planned,
    }


def count_routes(entries: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in entries:
        level = entry["route"]["level"]
        counts[level] = counts.get(level, 0) + 1
    return dict(sorted(counts.items()))


def evaluation_document(entries: list[dict]) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "meta": {
            "spec_version": SPEC_VERSION,
            "generated_at": now_utc(),
            "mode": "score",
            "entry_count": len(entries),
            "candidate_count": sum(1 for entry in entries if entry["profile"].get("catalog_status") == "candidate"),
            "route_counts": count_routes(entries),
            "verdict_counts": count_values(entries, "score", "verdict"),
            "method": "Rule-based quality evaluation: preliminary evidence selects a route; "
                      "only routed tools run. No entry-specific score override exists.",
        },
        "entries": entries,
    }


def count_values(entries: list[dict], section: str, key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in entries:
        value = (entry.get(section) or {}).get(key)
        if value is not None:
            counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def write_document(document: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", action="store_true", help="Write evaluation routes, run no tools")
    parser.add_argument("--score", action="store_true", help="Evaluate entries with their routed tools")
    parser.add_argument("--entry", action="append", help="Entry ID; repeatable")
    parser.add_argument("--all", action="store_true", help="All catalog entries")
    parser.add_argument("--online", action="store_true", help="Fetch GitHub release assets while planning")
    parser.add_argument("--download", action="store_true", help="Download the selected artifact")
    parser.add_argument("--allow-execution", action="store_true",
                        help="Allow rule commands to run inside the local Docker sandbox")
    parser.add_argument("--inspect-source", action="store_true",
                        help="Read the GitHub default-branch tree for license, tests, manifests and CI")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--json", action="store_true", help="Print the document instead of a summary")
    args = parser.parse_args()
    if not args.plan and not args.score:
        parser.error("choose --plan or --score")
    if not args.entry and not args.all:
        parser.error("choose --entry ID or --all")

    global EVIDENCE, RULE_PACKS
    EVIDENCE = load_evidence()
    RULE_PACKS = load_rule_packs()
    catalog = load_catalog()
    if args.entry:
        missing = [entry_id for entry_id in args.entry if entry_id not in catalog]
        if missing:
            parser.error("unknown entry ID(s): " + ", ".join(missing))
        records = [catalog[entry_id] for entry_id in args.entry]
    else:
        records = list(catalog.values())
    if args.plan:
        document = plan_document(records, online=args.online)
    else:
        evaluated = []
        for record in records:
            sys.stderr.write(f"evaluating {record['id']}\r")
            evaluated.append(evaluate_entry(
                record, EVIDENCE.get(record["id"]), RULE_PACKS.get(record["id"]),
                online=args.online, download=args.download, allow_execution=args.allow_execution,
                inspect_source=args.inspect_source))
        document = evaluation_document(evaluated)
    write_document(document, args.output)
    if args.json:
        print(json.dumps(document, ensure_ascii=False, indent=1))
    else:
        meta = document["meta"]
        try:
            shown_output = args.output.relative_to(ROOT)
        except ValueError:
            shown_output = args.output
        print(f"wrote {meta['entry_count']} entries to {shown_output}")
        for level, count in meta["route_counts"].items():
            print(f"  {level}: {count}")
        if meta.get("verdict_counts"):
            for verdict, count in meta["verdict_counts"].items():
                print(f"  {verdict}: {count}")
    return 0


EVIDENCE: dict[str, dict] = {}
RULE_PACKS: dict[str, dict] = {}


if __name__ == "__main__":
    raise SystemExit(main())
