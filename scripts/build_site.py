#!/usr/bin/env python3
"""Build the dependency-free static site from the two source catalogs."""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "site"
OUTPUT = ROOT / "dist"
SITE_URL = "https://awesomerea.org"
REPOSITORY_URL = "https://github.com/reacher-z/Awesome-REA"
TARGETS = {"website", "game", "app", "binary", "firmware"}
FONT_AWESOME_ICONS = {
    "arrow": "arrow-right", "external": "arrow-up-right-from-square",
    "search": "magnifying-glass", "copy": "copy", "check": "check",
    "chevron": "chevron-down", "code": "code", "chip": "microchip",
    "phone": "mobile-screen", "box": "cube", "network": "diagram-project",
    "layers": "layer-group", "document": "file-lines", "book": "book-open",
    "terminal": "terminal", "github": "github",
}


def fontawesome_markup(html: str, stylesheet_url: str) -> str:
    html = html.replace('<html lang="en">', '<html lang="en" data-icon-set="fontawesome">')
    html = html.replace('<link rel="stylesheet" href="styles.css">', '<link rel="stylesheet" href="styles.css">\n  <link rel="stylesheet" href="' + stylesheet_url + '">')
    html = re.sub(r'<svg class="symbol-bank".*?</svg>', '', html, count=1, flags=re.DOTALL)

    def replace_icon(match: re.Match) -> str:
        attrs, key = match.group(1), match.group(2)
        class_match = re.search(r'class="([^"]*)"', attrs)
        classes = class_match.group(1) if class_match else "icon"
        return f'<span class="{classes} fa-symbol fa-{key}" aria-hidden="true"></span>'

    html = re.sub(r'<svg\b([^>]*)>\s*<use href="#i-([a-z-]+)"\s*/>\s*</svg>', replace_icon, html)
    credit = '<a href="https://fontawesome.com" target="_blank" rel="noopener noreferrer" data-i18n="iconsCredit">Font Awesome Pro icons ↗</a>'
    html = html.replace('<div class="footer-links">', '<div class="footer-links">' + credit)
    return html


def configure_fontawesome(html: str, licensed_package: Path | None, assets_url: str | None = None) -> str:
    """Embed licensed fonts only in ignored deployment output; keep source portable."""
    generated_css = OUTPUT / "fontawesome.css"
    font_output = OUTPUT / "fonts"
    font_names = ("fa-light-300.woff2", "fa-brands-400.woff2")
    if licensed_package is None:
        generated_css.unlink(missing_ok=True)
        for name in font_names:
            (font_output / name).unlink(missing_ok=True)
        if font_output.exists() and not any(font_output.iterdir()):
            font_output.rmdir()
        if assets_url:
            parsed = urlsplit(assets_url)
            if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or any(character.isspace() or character in '"<>' for character in assets_url):
                raise ValueError("Font Awesome assets URL must be an HTTPS base URL without credentials, query or fragment.")
            return fontawesome_markup(html, assets_url.rstrip("/") + "/fontawesome.css")
        return html

    css_files = [licensed_package / "css" / name for name in ("fontawesome.css", "brands.css", "light.css")]
    for path in css_files + [licensed_package / "webfonts" / name for name in font_names]:
        if not path.is_file():
            raise ValueError("Font Awesome input must include Classic Light, Brands, and their WOFF2 files.")
    font_css = "\n".join(path.read_text(encoding="utf-8") for path in css_files)
    codepoints = {}
    for key, icon_name in FONT_AWESOME_ICONS.items():
        match = re.search(r"\.fa-" + re.escape(icon_name) + r'\s*\{[^}]*--fa:\s*"\\([0-9a-fA-F]+)"', font_css)
        if not match:
            raise ValueError(f"Required Font Awesome icon is missing: {icon_name}")
        codepoints[key] = match.group(1)
    font_output.mkdir(exist_ok=True)
    for name in font_names:
        shutil.copy2(licensed_package / "webfonts" / name, font_output / name)
    copyright_header = "/*! Font Awesome Pro by Fonticons, Inc. https://fontawesome.com — Commercial License: https://fontawesome.com/license. Licensed website assets; do not redistribute in a public source repository. */\n"
    css = copyright_header + """
@font-face{font-family:'AwesomeREA Icons';font-style:normal;font-weight:300;font-display:block;src:url('fonts/fa-light-300.woff2') format('woff2')}
@font-face{font-family:'AwesomeREA Brands';font-style:normal;font-weight:400;font-display:block;src:url('fonts/fa-brands-400.woff2') format('woff2')}
.fa-symbol{display:inline-flex;align-items:center;justify-content:center;font-family:'AwesomeREA Icons';font-weight:300;font-style:normal;font-size:20px;line-height:1;text-rendering:auto;-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}
.fa-symbol.icon-small{font-size:14px}.fa-symbol::before{display:block;line-height:1}.fa-symbol.fa-github{font-family:'AwesomeREA Brands';font-weight:400}
.target-link>.fa-symbol{font-size:19px}.card-icon>.fa-symbol{font-size:18px}.trace-target>.fa-symbol{font-size:24px}.card-title-link .fa-symbol{font-size:11px;display:inline-block}.card-footer .fa-symbol{font-size:10px}.button>.fa-symbol{font-size:17px}.search-box>.fa-symbol{font-size:21px}
"""
    css += "\n".join('.fa-' + key + '::before{content:"\\' + codepoint + '"}' for key, codepoint in codepoints.items())
    generated_css.write_text(css + "\n", encoding="utf-8")
    return fontawesome_markup(html, "fontawesome.css")



def group_for(record: dict) -> str:
    relationship = record["relationship"]
    if relationship == "independent-agent-integration":
        return "agents"
    if relationship == "foundation":
        return "tools"
    if relationship in {"learning", "community-learning-resource", "upstream-maintainer-companion-list"}:
        return "learn"
    return "rea"


def default_targets(record: dict) -> list[str]:
    """Conservative domain labels, never an assertion of REA compatibility."""
    category = record["category"]
    text = " ".join(str(record.get(k, "")) for k in ("id", "name", "description_en")).lower()
    if category == "core":
        return sorted(TARGETS)
    found: set[str] = set()
    if category in {"javascript-electron", "android", "dotnet"} or any(w in text for w in ("electron", "android", "aegis", "notion", "managed-code")):
        found.add("app")
    if category == "webassembly" or any(w in text for w in ("browser", "network capture", "web capture", "javascript", "webcrack")):
        found.add("website")
    if category == "firmware" or "firmware" in text:
        found.add("firmware")
    if any(w in text for w in ("dx-ball", "th04", "game", "unity")):
        found.add("game")
    if category in {"native-analysis", "dynamic-analysis", "binary-libraries", "binary-diffing", "agent-mcp", "agent-workflows", "learning"} or "native" in text:
        found.add("binary")
    return sorted(found or {"binary"})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    icons = parser.add_mutually_exclusive_group()
    icons.add_argument("--fontawesome-dir", type=Path, help="Optional local licensed Font Awesome Pro package; copied only into ignored deployment output.")
    icons.add_argument("--fontawesome-assets-url", help="Trusted HTTPS origin/path serving the authorized Font Awesome deployment; no font files are downloaded or copied.")
    args = parser.parse_args()
    translations = json.loads((SOURCE / "translations.zh-CN.json").read_text(encoding="utf-8"))
    resources = []
    for filename in ("rea-resources.json", "tool-resources.json"):
        for original in json.loads((ROOT / "data" / filename).read_text(encoding="utf-8")):
            record = dict(original)
            if isinstance(record["requirements"], str):
                record["requirements"] = [record["requirements"]]
            translation = translations.get(record["id"], {})
            record["requirements_zh"] = record.get("requirements_zh") or translation.get("requirements", record["requirements"])
            record["name_zh"] = record.get("name_zh") or translation.get("name", record["name"])
            record["group"] = group_for(record)
            targets = record.get("targets") or default_targets(record)
            if not isinstance(targets, list) or not set(targets).issubset(TARGETS):
                raise ValueError(f"Invalid targets: {record['id']}")
            record["targets"] = sorted(set(targets))
            resources.append(record)
    ids = [r["id"] for r in resources]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate catalog IDs")
    playbooks = (ROOT / "docs" / "playbooks.md").read_text(encoding="utf-8")
    playbook_count = len(re.findall(r"^## ", playbooks, flags=re.MULTILINE))
    latest_review = max(record["verified_at"] for record in resources)
    metadata = {"site_url": SITE_URL, "repository_url": REPOSITORY_URL, "resource_count": len(resources), "independent_integration_count": sum(r["group"] == "agents" for r in resources), "playbook_count": playbook_count, "latest_review": latest_review, "verification_note": "Catalog resources are source-reviewed. One CLI run and three original-fixture tests are recorded separately in the lab."}
    OUTPUT.mkdir(exist_ok=True)
    for path in SOURCE.iterdir():
        if path.name == "translations.zh-CN.json":
            continue
        if path.is_dir():
            shutil.copytree(path, OUTPUT / path.name, dirs_exist_ok=True)
        else:
            shutil.copy2(path, OUTPUT / path.name)
    html = (OUTPUT / "index.html").read_text(encoding="utf-8")
    for key, value in {"RESOURCE_COUNT": len(resources), "INTEGRATION_COUNT": metadata["independent_integration_count"], "PLAYBOOK_COUNT": str(playbook_count).zfill(2), "REVIEWED_AT": latest_review}.items():
        html = html.replace("{{" + key + "}}", str(value))
    html = configure_fontawesome(html, args.fontawesome_dir, args.fontawesome_assets_url)
    (OUTPUT / "index.html").write_text(html, encoding="utf-8")
    source_index_path = ROOT / "data" / "source-index.json"
    source_index_output = OUTPUT / "source-index.json"
    metadata["source_index"] = {"available": False, "resource_count": 0}
    if source_index_path.is_file():
        try:
            index_data = json.loads(source_index_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print("Optional source index is not a complete JSON snapshot yet; using the curated guide only.")
        else:
            successful = [record for record in index_data.get("resources", []) if record.get("scan_status") == "readme-scanned"]
            if successful:
                index_data["resources"] = successful
                index_meta = index_data.get("meta", {})
                metadata["source_index"] = {"available": True, "resource_count": len(successful), "status": index_meta.get("status", ""), "completed_at": index_meta.get("completed_at"), "verification": "automated-readme-scan"}
                source_index_output.write_text(json.dumps(index_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not metadata["source_index"]["available"]:
        source_index_output.unlink(missing_ok=True)
    (OUTPUT / "catalog.json").write_text(json.dumps({"meta": metadata, "resources": resources}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / ".nojekyll").write_text("", encoding="utf-8")
    (OUTPUT / "CNAME").write_text("awesomerea.org\n", encoding="utf-8")
    (OUTPUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    (OUTPUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{SITE_URL}/</loc><lastmod>{latest_review}</lastmod></url></urlset>\n', encoding="utf-8")
    print(f"Built {len(resources)} resources, {playbook_count} playbooks → dist/ ({SITE_URL})")


if __name__ == "__main__":
    main()
