"""The evidence/scores pair is recomputed and hand edits are rejected."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import quality_scoring as scoring  # noqa: E402
import validate_quality_scoring as validator  # noqa: E402


def record():
    return {
        "id": "demo-case", "name": "Demo", "url": "https://github.com/acme/demo",
        "kind": "case-study", "targets": ["app"],
        "description_en": "A desktop editor.", "description_zh": "", "requirements": ["Rust.", "MIT."],
    }


def evidence():
    signals = {
        "sections": {"features": {"heading": "Features", "snippet": "Features and usage", "bullets": 3}},
        "heading_count": 5, "bullets": 3, "code_blocks": 1, "install_commands": ["cargo install demo"],
        "media": [{"type": "image", "url": "docs/shot.png", "alt": "Editor"}], "media_count": 1,
        "links": {"count": 2, "docs": [], "demo": []},
        "keywords": {"tests": True, "performance": False, "security": False, "ui": True,
                     "persistence": False, "concurrency": False, "formats": False, "reproducibility": True},
        "keyword_snippets": {"tests": "The suite is tested.", "performance": None, "security": None,
                             "ui": "Screenshot", "persistence": None, "concurrency": None,
                             "formats": None, "reproducibility": "Install with cargo."},
        "claims": {"not_implemented": False, "partial": False, "supported": True,
                   "tests": True, "checksum": False, "benchmark": False},
        "lines": 50,
    }
    return {
        "slug": "acme/demo", "url": "https://github.com/acme/demo",
        "observed_at": "2026-11-04T00:00:00+00:00", "status": "observed", "ref": "main", "pinned": False,
        "repository": {"license": "MIT", "archived": False, "pushed_at": "2026-10-01T00:00:00Z",
                       "description": "A desktop editor", "topics": []},
        "readme": {"path": "README.md", "ref": "main", "sha256": "a" * 64, "bytes": 1000, "signals": signals},
        "tree": {
            "path_count": 20, "truncated": False, "license": ["LICENSE"],
            "tests": ["tests/a.rs", "tests/b.rs", "tests/c.rs"], "test_count": 3, "spec_docs": [],
            "ci": [".github/workflows/ci.yml"], "docs": ["docs/guide.md"], "doc_count": 1,
            "manifests": ["Cargo.toml"], "lockfiles": ["Cargo.lock"], "benchmarks": [],
            "ui_tests": [], "security": [], "migrations": [], "docker": [], "fixtures": [],
            "formats": {".png": 1}, "source_files": 4,
            "workflow_paths": [".github/workflows/ci.yml"],
        },
        "releases": {"count": 1, "latest_tag": "v1.0.0", "latest_published_at": "2026-10-01T00:00:00Z",
                     "assets": [{"name": "demo.tar.gz", "size": 1, "download_count": 0, "tag": "v1.0.0"}],
                     "asset_count": 1, "checksums": [], "semver_tags": ["v1.0.0"],
                     "body_claims": {"checksum": False, "signature": False, "notes": True}},
        "workflows": [{"path": ".github/workflows/ci.yml", "test_commands": ["cargo test"],
                       "sha256": "b" * 64}],
    }


def documents():
    evidence_document = {
        "schema_version": 1,
        "meta": {"spec": "quality-evidence-v1", "generated_at": "2026-11-04T00:00:00+00:00",
                 "entry_count": 1, "repository_count": 1, "page_entry_count": 0,
                 "repository_observed": 1, "page_observed": 0, "limits": ["Public evidence only."]},
        "repos": {"acme/demo": evidence()},
        "pages": {},
        "entries": {"demo-case": {"id": "demo-case", "name": "Demo",
                                  "url": "https://github.com/acme/demo", "kind": "case-study",
                                  "targets": ["app"], "source": "github", "repo": "acme/demo",
                                  "page": None}},
    }
    entry = scoring.score_entry(record(), evidence())
    evaluations = scoring.evaluation_document([entry], evidence_document)
    return evidence_document, evaluations


class ValidationTests(unittest.TestCase):
    def test_a_valid_pair_passes(self):
        evidence_document, evaluations = documents()
        errors = []
        validator.validate_evidence(evidence_document, errors)
        with mock.patch.object(scoring, "load_catalog", return_value=[record()]):
            validator.validate_evaluations(evaluations, evidence_document, errors)
        self.assertEqual(errors, [])

    def test_a_hand_edited_score_is_rejected(self):
        evidence_document, evaluations = documents()
        evaluations["entries"][0]["score"] = 99.9
        errors = []
        with mock.patch.object(scoring, "load_catalog", return_value=[record()]):
            validator.validate_evaluations(evaluations, evidence_document, errors)
        self.assertTrue(any("does not match the evidence snapshot" in error for error in errors), errors)

    def test_a_repo_without_metadata_is_rejected(self):
        evidence_document, _ = documents()
        evidence_document["repos"]["acme/demo"]["repository"] = None
        errors = []
        validator.validate_evidence(evidence_document, errors)
        self.assertTrue(any("no repository metadata" in error for error in errors), errors)

    def test_a_repo_with_metadata_but_no_readme_is_allowed_and_ungraded(self):
        evidence_document, _ = documents()
        evidence_document["repos"]["acme/demo"]["readme"] = None
        evidence_document["repos"]["acme/demo"]["tree"] = None
        errors = []
        validator.validate_evidence(evidence_document, errors)
        self.assertEqual(errors, [])
        result = scoring.score_entry(record(), evidence_document["repos"]["acme/demo"])
        self.assertIsNone(result["score"])
        self.assertEqual(result["band"], "ungraded")

    def test_the_pair_is_optional_but_never_single(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with mock.patch.object(validator, "EVIDENCE_PATH", root / "evidence.json"), \
                    mock.patch.object(validator, "EVALUATIONS_PATH", root / "evaluations.json"):
                self.assertEqual(validator.validate(), [])
                (root / "evidence.json").write_text("{}", encoding="utf-8")
                errors = validator.validate()
                self.assertTrue(errors and "committed as a pair" in errors[0])

    def test_stale_meta_counts_are_rejected(self):
        evidence_document, evaluations = documents()
        evaluations["meta"]["band_counts"] = {"strong-evidence": 99}
        errors = []
        with mock.patch.object(scoring, "load_catalog", return_value=[record()]):
            validator.validate_evaluations(evaluations, evidence_document, errors)
        self.assertTrue(any("band_counts is stale" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
