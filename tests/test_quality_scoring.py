"""Evidence scoring: applicability, checks, aggregation and the ungraded case."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import quality_scoring as scoring  # noqa: E402

KEYWORD_KEYS = ("tests", "performance", "security", "ui", "persistence", "concurrency",
                "formats", "reproducibility")


def record(**overrides):
    base = {
        "id": "demo-case", "name": "Demo", "url": "https://github.com/acme/demo",
        "kind": "case-study", "targets": ["app"],
        "description_en": "A desktop editor for PDF drawings.",
        "description_zh": "", "requirements": ["Rust 1.90 or newer.", "MIT license."],
    }
    base.update(overrides)
    return base


def signals(**overrides):
    base = {
        "sections": {},
        "heading_count": 6,
        "bullets": 4,
        "code_blocks": 2,
        "install_commands": ["cargo install demo"],
        "media": [{"type": "image", "url": "docs/shot.png", "alt": "Editor"}],
        "media_count": 1,
        "links": {"count": 3, "docs": [], "demo": []},
        "keywords": {key: False for key in KEYWORD_KEYS},
        "keyword_snippets": {key: None for key in KEYWORD_KEYS},
        "claims": {"not_implemented": False, "partial": False, "supported": True,
                   "tests": False, "checksum": False, "benchmark": False},
        "lines": 80,
    }
    base.update(overrides)
    return base


def evidence(**overrides):
    base = {
        "status": "observed",
        "url": "https://github.com/acme/demo",
        "observed_at": "2026-11-04T00:00:00+00:00",
        "repository": {
            "license": "MIT", "archived": False, "pushed_at": "2026-10-01T00:00:00Z",
            "description": "A desktop editor", "topics": ["editor"],
        },
        "readme": {"path": "README.md", "sha256": "a" * 64, "bytes": 1000, "signals": signals()},
        "tree": {
            "path_count": 100, "truncated": False,
            "license": ["LICENSE"], "tests": ["tests/editor.rs", "tests/pdf.rs", "tests/export.rs"],
            "test_count": 3, "spec_docs": [], "ci": [".github/workflows/ci.yml"],
            "docs": ["README.md", "docs/guide.md", "docs/format.md"], "doc_count": 3,
            "manifests": ["Cargo.toml"], "lockfiles": ["Cargo.lock"],
            "benchmarks": ["benches/render.rs"], "ui_tests": [], "security": ["SECURITY.md"],
            "migrations": [], "docker": [], "fixtures": ["fixtures/sample.pdf"],
            "formats": {".pdf": 2, ".png": 1}, "source_files": 20,
            "workflow_paths": [".github/workflows/ci.yml"],
        },
        "releases": {
            "count": 2, "latest_tag": "v1.2.0", "latest_published_at": "2026-10-01T00:00:00Z",
            "assets": [{"name": "demo-linux.tar.gz", "size": 10, "download_count": 1, "tag": "v1.2.0"}],
            "asset_count": 1, "checksums": ["SHA256SUMS.txt"], "semver_tags": ["v1.2.0"],
            "body_claims": {"checksum": True, "signature": False, "notes": True},
        },
        "workflows": [{"path": ".github/workflows/ci.yml", "test_commands": ["cargo test"],
                       "sha256": "b" * 64}],
    }
    base.update(overrides)
    return base


class ApplicabilityTests(unittest.TestCase):
    def test_desktop_app_applies_ui_and_formats_but_not_persistence_without_evidence(self):
        dimensions = scoring.applicable_dimensions(record(), evidence())
        self.assertIn("ui_consistency", dimensions)
        self.assertIn("file_formats", dimensions)
        self.assertNotIn("persistence_recovery", dimensions)
        self.assertNotIn("security_isolation", dimensions)

    def test_web_app_applies_security_concurrency_and_persistence(self):
        record_ = record(targets=["website"], description_en="A web app with login, roles and a database.")
        dimensions = scoring.applicable_dimensions(record_, evidence())
        self.assertIn("security_isolation", dimensions)
        self.assertIn("concurrency", dimensions)
        self.assertIn("persistence_recovery", dimensions)
        self.assertIn("ui_consistency", dimensions)

    def test_cli_binary_does_not_apply_ui_or_security(self):
        record_ = record(targets=["binary"], description_en="A command-line binary parser.",
                         requirements=[])
        dimensions = scoring.applicable_dimensions(record_, evidence())
        self.assertNotIn("ui_consistency", dimensions)
        self.assertNotIn("security_isolation", dimensions)
        self.assertNotIn("persistence_recovery", dimensions)
        self.assertIn("file_formats", dimensions)


class ScoreTests(unittest.TestCase):
    def test_observed_repository_produces_a_score_with_nine_dimensions(self):
        result = scoring.score_entry(record(), evidence())
        self.assertEqual(set(result["dimensions"]), set(scoring.DIMENSION_ORDER))
        self.assertIsNotNone(result["score"])
        self.assertGreater(result["score"], 0)
        self.assertEqual(result["confidence"], "high")
        self.assertIn(result["band"], {item[1] for item in scoring.BANDS})

    def test_reproducibility_sees_license_manifest_lock_ci_and_release(self):
        result = scoring.score_entry(record(), evidence())
        checks = {item["id"]: item for item in result["dimensions"]["reproducibility"]["checks"]}
        for check_id in ("license", "build-manifest", "lockfile", "ci",
                         "install-documentation", "versioned-release", "artifact"):
            self.assertEqual(checks[check_id]["points"], 1.0, check_id)

    def test_missing_evidence_is_ungraded_not_zero(self):
        result = scoring.score_entry(record(), None)
        self.assertIsNone(result["score"])
        self.assertEqual(result["band"], "ungraded")
        self.assertEqual(result["confidence"], "none")
        self.assertEqual(result["coverage"], 0.0)

    def test_unreachable_source_is_ungraded(self):
        result = scoring.score_entry(record(), {"status": "unreachable", "url": "https://github.com/acme/demo"})
        self.assertIsNone(result["score"])
        self.assertEqual(result["band"], "ungraded")

    def test_partial_checks_half_credit(self):
        incomplete = evidence()
        incomplete["tree"] = None
        incomplete["releases"] = None
        incomplete["workflows"] = []
        result = scoring.score_entry(record(), incomplete)
        dim = result["dimensions"]["reproducibility"]
        checks = {item["id"]: item for item in dim["checks"]}
        self.assertEqual(checks["license"]["points"], 1.0)
        self.assertEqual(checks["lockfile"]["points"], 0.0)
        self.assertEqual(checks["ci"]["points"], 0.0)

    def test_band_boundaries(self):
        self.assertEqual(scoring.band_for(75.0)[0], "strong-evidence")
        self.assertEqual(scoring.band_for(74.9)[0], "moderate-evidence")
        self.assertEqual(scoring.band_for(50.0)[0], "moderate-evidence")
        self.assertEqual(scoring.band_for(25.0)[0], "limited-evidence")
        self.assertEqual(scoring.band_for(0.0)[0], "minimal-evidence")
        self.assertEqual(scoring.band_for(None)[0], "ungraded")

    def test_document_counts_bands_and_median(self):
        first = scoring.score_entry(record(), evidence())
        second = scoring.score_entry(record(id="other-case"), None)
        document = scoring.evaluation_document([first, second], {"meta": {"generated_at": "x", "spec": "y", "limits": []}})
        self.assertEqual(document["meta"]["entry_count"], 2)
        self.assertEqual(document["meta"]["score_count"], 1)
        self.assertEqual(document["meta"]["band_counts"]["ungraded"], 1)
        self.assertIsNotNone(document["meta"]["median_score"])


if __name__ == "__main__":
    unittest.main()
