#!/usr/bin/env python3
"""Read a curated entry's pinned README and linked documents for fidelity signals.

This is a review aid, not runtime verification. It fetches only public text from the
catalog entry's GitHub repository at the reviewed commit, follows a bounded number of
README-linked Markdown/RST/TXT documents, and prints line-addressed excerpts for five
signal families: feature coverage, end-to-end workflow, comparison or parity, stated
limits, and reconstruction route. Nothing is written into data/ and no application is
installed or run.

Usage:
    python3 scripts/fidelity_scan.py --ids storytold/lightcraft-case
    python3 scripts/fidelity_scan.py --repo owner/name --commit <sha> --path README.md
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import posixpath
import re
import sys
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from classify_evidence_classes import (  # noqa: E402
    CODE_BLOCK,
    HTML_LINK,
    HTML_TAG,
    MARKDOWN_LINK,
    SIGNAL_TEXT_LIMIT,
    HttpClient,
    os_environ_token,
)

MAX_DOCUMENTS = 5
MAX_SECOND_HOP = 2
MAX_EXCERPT = 700
DOCUMENT_SUFFIXES = (".md", ".markdown", ".rst", ".txt", ".mdx")
SIGNAL_PATTERNS = {
    "coverage": r"feature.{0,20}(?:matrix|coverage|parity)|compatibility.{0,15}(?:matrix|table)|"
                r"supported.{0,20}(?:unsupported|formats)|what works|what.{0,10}(?:missing|supported)|"
                r"coverage|功能覆盖|兼容性|支持.*不支持",
    "workflow": r"round.trip|save.{0,70}(?:load|reopen|reload|persist)|"
                r"(?:import|open).{0,100}(?:edit|export|save)|playthrough|end.to.end|"
                r"campaign.{0,40}(?:complete|finish)|start.to.finish|new game.{0,80}(?:credits|ending)|"
                r"保存.{0,30}(?:重开|恢复)|端到端|通关",
    "comparison": r"differential|oracle|byte.exact|bit.exact|byte.match|"
                  r"original.{0,70}(?:compar|match|test)|(?:compar|match|test).{0,70}(?:original|retail|reference)|"
                  r"parity|对照|差分|逐字节|等价",
    "limits": r"known (?:issues|limitations)|not (?:yet )?(?:implemented|supported|playable|complete|working)|"
              r"missing.{0,40}(?:feature|audio|sound|save|network|render)|cannot.{0,45}(?:play|save|load)|"
              r"prevent.{0,40}progress|broken|incomplete|placeholder|stubbed|only.{0,30}(?:demo|prototype|level)|"
              r"not a.{0,40}(?:clone|replacement)|未实现|不支持|尚未|缺失",
    "route": r"clean.room|from.scratch|reimplement|static recomp|decompilat|"
             r"original.{0,40}(?:code|binary|executable)|compatibility layer|wrapper|"
             r"not.{0,25}(?:emulat|recomp|clone)|重新实现|重实现|重编译|反编译|原版.*代码",
}
LINK_HINTS = (
    (r"parity|oracle|differential|fidelity|equivalen|validation|comparison|conformance|case.study|evidence|acceptance", 25),
    (r"known|limit|coverage|compatib|status|feature|roadmap|matrix|what.work", 20),
    (r"workflow|demo|showcase|walkthrough|playthrough|smoke|testing|proof|test", 15),
    (r"architecture|design|implementation|policies|engine.readme", 7),
    (r"usage|guide|manual|how.to|overview", 4),
)
LINK_EXCLUDES = re.compile(
    r"install|build|contribut|license|licence|security|changelog|funding|translation|"
    r"readme\.(?:zh|es|pt|ja|de)|\.github|node_modules", re.I)
IMAGE = re.compile(r"!\[", re.I)


class ScanError(ValueError):
    pass


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def load_records() -> dict[str, dict]:
    records = {}
    for filename in ("rea-resources.json", "tool-resources.json"):
        for record in json.loads((ROOT / "data" / filename).read_text(encoding="utf-8")):
            records[record["id"]] = record
    return records


def parse_evidence(value: str) -> tuple[str, str, str, str]:
    """owner, repo, commit and path from a pinned GitHub blob evidence URL."""
    parts = urlsplit(value or "")
    if parts.hostname not in ("github.com", "www.github.com"):
        raise ScanError("evidence_url is not a GitHub URL")
    segments = [segment for segment in parts.path.split("/") if segment]
    if len(segments) < 5 or segments[2] != "blob":
        raise ScanError("evidence_url must be a GitHub blob link at a commit")
    owner, repo, commit = segments[0], segments[1], segments[3]
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ScanError("evidence_url does not name a 40-character commit")
    return owner, repo, commit, unquote("/".join(segments[4:]))


def github_contents_url(owner: str, repo: str, commit: str, path: str) -> str:
    return f"https://api.github.com/repos/{owner}/{repo}/contents/{quote(path, safe='/')}?ref={commit}"


def fetch_text(client, owner: str, repo: str, commit: str, path: str) -> tuple[str | None, str, int]:
    """Read one public file at a commit; return (text, html_url, status)."""
    url = github_contents_url(owner, repo, commit, path)
    status, body, _ = client.get(url)
    if status != 200:
        return None, f"https://github.com/{owner}/{repo}/blob/{commit}/{path}", status
    try:
        payload = json.loads(body.decode("utf-8", "replace"))
        content = payload.get("content") if isinstance(payload, dict) else None
        if not isinstance(content, str):
            raise ValueError
        text = base64.b64decode(content).decode("utf-8", "replace")
    except (ValueError, TypeError, UnicodeError):
        return None, f"https://github.com/{owner}/{repo}/blob/{commit}/{path}", 0
    html_url = payload.get("html_url") or f"https://github.com/{owner}/{repo}/blob/{commit}/{path}"
    return text[:SIGNAL_TEXT_LIMIT], html_url, 200


def _relative_path(raw: str, base: str) -> str | None:
    if not raw:
        return None
    parts = urlsplit(raw)
    if parts.scheme or parts.netloc:
        return None
    path = unquote(parts.path)
    if not path or path.startswith("#"):
        return None
    path = posixpath.normpath(path.lstrip("/") if path.startswith("/") else posixpath.join(posixpath.dirname(base), path))
    if path.startswith("../") or not path.lower().endswith(DOCUMENT_SUFFIXES) or LINK_EXCLUDES.search(path):
        return None
    return path


def document_links(text: str, base: str) -> list[dict]:
    """README-linked documents, ranked by the evidence they are likely to carry."""
    plain = CODE_BLOCK.sub(" ", text)
    candidates = [(href.strip(), label) for label, href in MARKDOWN_LINK.findall(plain)]
    candidates += [(href.strip(), HTML_TAG.sub(" ", label)) for href, label in HTML_LINK.findall(text)]
    found = {}
    for raw, label in candidates:
        path = _relative_path(raw, base)
        if not path:
            continue
        hint = f"{label} {path}"
        score = sum(weight for pattern, weight in LINK_HINTS if re.search(pattern, hint, re.I))
        if score:
            found[path] = {"path": path, "label": " ".join(label.split())[:140], "score": score}
    return sorted(found.values(), key=lambda item: (-item["score"], item["path"]))[:MAX_DOCUMENTS]


def second_hop_links(doc: dict, text: str) -> list[dict]:
    """One extra hop only for an explicitly named comparison, result or limits document."""
    return [item for item in document_links(text, doc["path"])
            if re.search(r"parity|oracle|differential|coverage|validation|results|limitations|known", item["path"], re.I)]


def scan_signals(path: str, text: str, html_url: str) -> dict[str, list[dict]]:
    lines = text.splitlines()
    found = {name: [] for name in SIGNAL_PATTERNS}
    for index, line in enumerate(lines):
        for name, pattern in SIGNAL_PATTERNS.items():
            if re.search(pattern, line, re.I):
                start, end = max(0, index - 1), min(len(lines), index + 3)
                found[name].append({
                    "path": path,
                    "line": index + 1,
                    "url": f"{html_url.split('#')[0]}#L{index + 1}",
                    "excerpt": "\n".join(lines[start:end])[:MAX_EXCERPT],
                })
    return found


def scan_record(record: dict, client) -> dict:
    """Bounded document evidence for one catalog record. No application is run."""
    owner, repo, commit, path = parse_evidence(record.get("evidence_url", ""))
    readme_text, readme_url, status = fetch_text(client, owner, repo, commit, path)
    if readme_text is None:
        raise ScanError(f"README could not be read at the reviewed commit (HTTP {status})")
    documents = [{"path": path, "url": readme_url, "readable": True, "bytes": len(readme_text.encode("utf-8"))}]
    selected = document_links(readme_text, path)
    signals = scan_signals(path, readme_text, readme_url)
    seen = {path}
    for link in selected:
        text, url, status = fetch_text(client, owner, repo, commit, link["path"])
        documents.append({"path": link["path"], "label": link["label"], "score": link["score"],
                          "url": url, "readable": text is not None, "status": status,
                          "bytes": len(text.encode("utf-8")) if text else 0})
        if text is None:
            continue
        seen.add(link["path"])
        for name, items in scan_signals(link["path"], text, url).items():
            signals[name].extend(items)
        for extra in second_hop_links(link, text):
            if extra["path"] in seen or len(documents) >= MAX_DOCUMENTS + MAX_SECOND_HOP + 1:
                continue
            text2, url2, status2 = fetch_text(client, owner, repo, commit, extra["path"])
            documents.append({"path": extra["path"], "label": extra["label"], "score": extra["score"],
                              "url": url2, "readable": text2 is not None, "status": status2,
                              "bytes": len(text2.encode("utf-8")) if text2 else 0})
            seen.add(extra["path"])
            if text2:
                for name, items in scan_signals(extra["path"], text2, url2).items():
                    signals[name].extend(items)
    return {
        "schema_version": 1,
        "id": record.get("id"),
        "repo": f"{owner}/{repo}",
        "commit": commit,
        "readme_path": path,
        "readme_url": readme_url,
        "documents": documents,
        "signals": signals,
        "signal_counts": {name: len(items) for name, items in signals.items()},
        "scope": f"README + up to {MAX_DOCUMENTS} linked documents + up to {MAX_SECOND_HOP} targeted second-hop documents; not an exhaustive repository crawl",
        "runtime_verified": False,
        "generated_at": now_utc(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ids", help="Comma-separated curated IDs to scan")
    parser.add_argument("--repo", help="owner/name when not reading a curated record")
    parser.add_argument("--commit", help="40-character commit for --repo")
    parser.add_argument("--path", default="README.md", help="README path for --repo (default: README.md)")
    parser.add_argument("--token", help="GitHub token; defaults to GITHUB_TOKEN or gh auth token")
    parser.add_argument("--pretty", action="store_true", help="Indent the JSON output")
    args = parser.parse_args()
    if not args.ids and not (args.repo and args.commit):
        parser.error("use --ids or --repo with --commit")
    client = HttpClient(args.token or os_environ_token(), "awesome-rea-fidelity-scan")
    records = load_records()
    targets = []
    if args.ids:
        for identifier in [value.strip() for value in args.ids.split(",") if value.strip()]:
            if identifier not in records:
                targets.append((identifier, {"id": identifier, "error": "not a curated record"}))
            else:
                targets.append((identifier, records[identifier]))
    else:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repo or ""):
            parser.error("--repo must be owner/name")
        if not re.fullmatch(r"[0-9a-f]{40}", args.commit or ""):
            parser.error("--commit must be a 40-character commit")
        record = {"id": args.repo, "evidence_url": f"https://github.com/{args.repo}/blob/{args.commit}/{args.path}"}
        targets.append((args.repo, record))
    results = []
    exit_code = 0
    for identifier, record in targets:
        if "error" in record:
            results.append(record)
            exit_code = 1
            continue
        try:
            results.append(scan_record(record, client))
        except ScanError as error:
            results.append({"id": identifier, "error": str(error)})
            exit_code = 1
        except (OSError, ValueError, TypeError) as error:
            results.append({"id": identifier, "error": f"scan failed: {error}"})
            exit_code = 1
    output = results[0] if len(results) == 1 else results
    print(json.dumps(output, ensure_ascii=False, indent=2 if args.pretty else None))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
