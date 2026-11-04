"""The bilingual score directory renders from generated evaluations."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_quality_pages  # noqa: E402
import quality_scoring  # noqa: E402


def record():
    return {
        "id": "demo-case", "name": "Demo", "url": "https://github.com/acme/demo",
        "kind": "case-study", "targets": ["app"], "category": "reconstruction-cases",
        "relationship": "independent-reconstruction", "evidence_url": "https://github.com/acme/demo",
        "verified_at": "2026-11-04", "verification": "source-reviewed",
        "description_en": "A demo editor.", "description_zh": "演示编辑器。",
        "requirements": ["Rust."], "evidence_class": 1,
    }


def evidence():
    signals = {
        "sections": {"features": {"heading": "Features", "snippet": "Features", "bullets": 3}},
        "heading_count": 4, "bullets": 3, "code_blocks": 1, "install_commands": ["cargo install demo"],
        "media": [], "media_count": 0, "links": {"count": 1, "docs": [], "demo": []},
        "keywords": {key: False for key in ("tests", "performance", "security", "ui", "persistence",
                                            "concurrency", "formats", "reproducibility")},
        "keyword_snippets": {}, "claims": {}, "lines": 20,
    }
    return {
        "slug": "acme/demo", "url": "https://github.com/acme/demo", "status": "observed",
        "observed_at": "2026-11-04T00:00:00+00:00", "ref": "main", "pinned": False,
        "repository": {"license": "MIT", "archived": False, "pushed_at": "2026-10-01T00:00:00Z"},
        "readme": {"path": "README.md", "ref": "main", "sha256": "a" * 64, "bytes": 100, "signals": signals},
        "tree": {"path_count": 3, "truncated": False, "license": ["LICENSE"], "tests": [],
                 "test_count": 0, "spec_docs": [], "ci": [], "docs": [], "doc_count": 0,
                 "manifests": ["Cargo.toml"], "lockfiles": ["Cargo.lock"], "benchmarks": [],
                 "ui_tests": [], "security": [], "migrations": [], "docker": [], "fixtures": [],
                 "formats": {}, "source_files": 1, "workflow_paths": []},
        "releases": {"count": 0, "latest_tag": None, "latest_published_at": None, "assets": [],
                     "asset_count": 0, "checksums": [], "semver_tags": [], "body_claims": {}},
        "workflows": [],
    }


class PageTests(unittest.TestCase):
    def test_pages_and_per_entry_checks_are_written(self):
        evidence_document = {"meta": {"generated_at": "2026-11-04T00:00:00+00:00",
                                      "spec": "quality-evidence-v1", "limits": ["Public evidence only."]}}
        evaluations = quality_scoring.evaluation_document(
            [quality_scoring.score_entry(record(), evidence())], evidence_document)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            for name in ("quality.css", "quality.js"):
                shutil.copy2(ROOT / "site" / name, output / name)
            urls = build_quality_pages.build_quality_pages(
                output, evaluations, [record()], {},
                styles_href="/styles.css", favicon_href="/favicon.svg",
                social_image_href="https://awesomerea.org/social-card.png",
                icon_stylesheet_href=None, repository_export="source-index.json",
            )
            self.assertEqual(urls, ["https://awesomerea.org/quality/",
                                    "https://awesomerea.org/zh/quality/"])
            english = (output / "quality" / "index.html").read_text(encoding="utf-8")
            chinese = (output / "zh" / "quality" / "index.html").read_text(encoding="utf-8")
            for text in (english, chinese):
                self.assertIn("quality-table", text)
                self.assertIn("BreadcrumbList", text)
                self.assertIn("data-quality-checks", text)
                self.assertIn("site-footer", text)
            self.assertIn("Software evidence scores", english)
            self.assertIn("软件证据评分", chinese)
            compact = json.loads((output / "quality" / "quality-data.json").read_text(encoding="utf-8"))
            self.assertEqual(len(compact["entries"]), 1)
            self.assertTrue((output / "quality" / "checks" / "demo-case.json").is_file())


if __name__ == "__main__":
    unittest.main()
