"""Public-evidence collection helpers: parsing, inventory and source identity."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import collect_quality_evidence as evidence  # noqa: E402


README = """# Demo

A small editor.

## Features

- Open a project
- Export a drawing
- Export a PDF

## Quick start

Install with `cargo install demo` or:

```sh
# This is a shell comment, not a heading.
cargo install demo
cargo test
```

## Screenshots

![Editor window](docs/editor.png)
![Export dialog](docs/export.png)

## Testing

The suite uses pytest and a differential reference implementation.

## Security

Authentication uses a session token; permissions are checked per role.

## License

MIT
"""


class MarkdownTests(unittest.TestCase):
    def test_headings_ignore_fenced_code_comments(self):
        headings = evidence.markdown_headings(README)
        texts = [text for _, text in headings]
        self.assertIn("Features", texts)
        self.assertNotIn("This is a shell comment, not a heading.", texts)

    def test_sections_keep_nested_bodies_out_of_the_parent(self):
        sections = evidence.section_ranges(README)
        by_heading = {heading: body for heading, body, _ in sections}
        self.assertIn("cargo install demo", by_heading["Quick start"])
        self.assertNotIn("Screenshots", by_heading["Quick start"])

    def test_readme_signals_detect_features_commands_media_and_keywords(self):
        parsed = evidence.readme_evidence(README)["signals"]
        self.assertIn("features", parsed["sections"])
        self.assertIn("cargo install demo", parsed["install_commands"])
        self.assertEqual(parsed["media_count"], 2)
        self.assertTrue(parsed["keywords"]["tests"])
        self.assertTrue(parsed["keywords"]["security"])
        self.assertTrue(parsed["keywords"]["ui"])
        self.assertEqual(parsed["claims"]["checksum"], False)

    def test_media_excludes_badges_and_logos(self):
        text = "![build](https://img.shields.io/badge/build-passing.svg) ![shot](docs/shot.png)"
        parsed = evidence.readme_evidence(text)["signals"]
        self.assertEqual(parsed["media_count"], 1)
        self.assertEqual(parsed["media"][0]["url"], "docs/shot.png")


class InventoryTests(unittest.TestCase):
    def test_tree_inventory_separates_tests_specs_ci_and_manifests(self):
        paths = [
            "Cargo.toml", "Cargo.lock", "LICENSE", "README.md",
            "tests/cli.rs", "src/main.rs", "re/specs/effects.md",
            ".github/workflows/ci.yml", "docs/guide.md", "docs/images/shot.png",
            "benches/render.rs", "playwright.config.ts", "SECURITY.md",
            "migrations/001_init.sql", "fixtures/sample.pdf",
        ]
        inventory = evidence.tree_inventory(paths)
        self.assertTrue(inventory["license"])
        self.assertIn("Cargo.toml", inventory["manifests"])
        self.assertIn("Cargo.lock", inventory["lockfiles"])
        self.assertIn("tests/cli.rs", inventory["tests"])
        self.assertNotIn("re/specs/effects.md", inventory["tests"])
        self.assertIn("re/specs/effects.md", inventory["spec_docs"])
        self.assertIn(".github/workflows/ci.yml", inventory["ci"])
        self.assertIn("benches/render.rs", inventory["benchmarks"])
        self.assertIn("playwright.config.ts", inventory["ui_tests"])
        self.assertIn("SECURITY.md", inventory["security"])
        self.assertIn("migrations/001_init.sql", inventory["migrations"])
        self.assertIn(".pdf", inventory["formats"])
        self.assertGreaterEqual(inventory["source_files"], 2)

    def test_release_assets_and_checksums(self):
        releases = [{
            "tag_name": "v1.2.3",
            "published_at": "2026-10-01T00:00:00Z",
            "body": "SHA-256 checksums are attached.",
            "assets": [
                {"name": "demo-linux.tar.gz", "size": 10, "download_count": 3},
                {"name": "SHA256SUMS.txt", "size": 1, "download_count": 1},
            ],
        }]
        parsed = evidence.release_evidence(releases)
        self.assertEqual(parsed["count"], 1)
        self.assertEqual(parsed["latest_tag"], "v1.2.3")
        self.assertEqual(parsed["asset_count"], 2)
        self.assertEqual(parsed["checksums"], ["SHA256SUMS.txt"])
        self.assertTrue(parsed["semver_tags"])
        self.assertTrue(parsed["body_claims"]["checksum"])


class SnapshotTests(unittest.TestCase):
    def test_trim_keeps_the_fields_the_scorer_reads(self):
        document = {
            "repos": {"acme/demo": {
                "readme": {"headings": [{"level": 1, "text": "x"}],
                           "signals": {"media": [{"url": str(i)} for i in range(8)],
                                       "sections": {"features": {"snippet": "y" * 300}}}},
                "tree": {"tests": [str(i) for i in range(15)], "formats": {f".{i}": 1 for i in range(12)}},
                "releases": {"assets": [{"name": str(i)} for i in range(8)]},
                "repository": {"topics": [str(i) for i in range(15)]},
            }},
            "pages": {},
        }
        trimmed = evidence.trim_document(document)
        repo = trimmed["repos"]["acme/demo"]
        self.assertNotIn("headings", repo["readme"])
        self.assertEqual(len(repo["readme"]["signals"]["media"]), 5)
        self.assertEqual(len(repo["readme"]["signals"]["sections"]["features"]["snippet"]), 240)
        self.assertEqual(len(repo["tree"]["tests"]), 10)
        self.assertEqual(len(repo["tree"]["formats"]), 8)
        self.assertEqual(len(repo["releases"]["assets"]), 5)
        self.assertEqual(len(repo["repository"]["topics"]), 10)


class SourceIdentityTests(unittest.TestCase):
    def test_github_slug_ignores_tree_and_blob_paths(self):
        self.assertEqual(evidence.github_slug("https://github.com/acme/demo"), "acme/demo")
        self.assertEqual(evidence.github_slug("https://github.com/acme/demo/tree/main/src"), "acme/demo")
        self.assertIsNone(evidence.github_slug("https://example.org/acme/demo"))

    def test_pinned_ref_reads_a_blob_or_tree_commit(self):
        record = {"evidence_url": "https://github.com/acme/demo/blob/abcdef1/README.md",
                  "additional_evidence_urls": []}
        self.assertEqual(evidence.pinned_ref(record), "abcdef1")
        record["evidence_url"] = "https://github.com/acme/demo/tree/main"
        self.assertIsNone(evidence.pinned_ref(record))

    def test_page_evidence_strips_markup_and_keeps_text(self):
        page = ("<html><head><title> Demo </title><meta name='description' content='An editor'>"
                "</head><body><h1>Features</h1><p>Import and export PDF.</p>"
                "<script>ignore()</script></body></html>")
        parsed = evidence.page_evidence(page)
        self.assertEqual(parsed["title"], "Demo")
        self.assertEqual(parsed["description"], "An editor")
        self.assertTrue(parsed["signals"]["keywords"]["formats"])


if __name__ == "__main__":
    unittest.main()
