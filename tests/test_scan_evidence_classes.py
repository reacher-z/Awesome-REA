"""Scan evidence classes: coverage, coarse rubric and the Class 0 boundary."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from classify_scan_evidence import classify  # noqa: E402


def record(**overrides):
    base = {
        "id": "scan-1",
        "full_name": "acme/tool",
        "url": "https://github.com/acme/tool",
        "scan_status": "readme-scanned",
        "readme_bytes": 1200,
        "readme_heading_count": 6,
        "readme_signals": ["installation", "usage", "license-section"],
        "observed_at": "2026-10-16T01:35:32Z",
    }
    base.update(overrides)
    return base


class ScanEvidenceClassTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads((ROOT / "data" / "scan-evidence-classes.json").read_text(encoding="utf-8"))
        self.source = json.loads((ROOT / "data" / "source-index.json").read_text(encoding="utf-8"))

    def test_covers_every_scanned_repository_once(self):
        expected = [item["id"] for item in self.source["resources"]]
        seen = set(expected)
        index_path = ROOT / "data" / "source-supplements" / "index.json"
        if index_path.is_file():
            for batch in json.loads(index_path.read_text(encoding="utf-8")).get("batches") or []:
                supplement = json.loads((index_path.parent / f"{batch}.json").read_text(encoding="utf-8"))
                for item in supplement.get("resources") or []:
                    if item.get("scan_status") == "readme-scanned" and item["id"] not in seen:
                        seen.add(item["id"])
                        expected.append(item["id"])
        actual = [entry["id"] for entry in self.document["entries"]]
        self.assertEqual(actual, expected)

    def test_metadata_counts_agree(self):
        meta = self.document["meta"]
        self.assertEqual(meta["spec_version"], "scan-evidence-class-v1")
        self.assertEqual(meta["entry_count"], len(self.document["entries"]))
        counts = {}
        unknown = 0
        for entry in self.document["entries"]:
            if entry["evidence_class"] is None:
                unknown += 1
            else:
                counts[str(entry["evidence_class"])] = counts.get(str(entry["evidence_class"]), 0) + 1
        self.assertEqual({str(value): counts.get(str(value), 0) for value in range(4)}, meta["class_counts"])
        self.assertEqual(unknown, meta["unknown_count"])

    def test_scan_metadata_never_assigns_class_zero(self):
        self.assertEqual(self.document["meta"]["class_zero_count"], 0)
        self.assertNotIn("0", {str(entry["evidence_class"]) for entry in self.document["entries"]})
        for entry in self.document["entries"]:
            self.assertFalse(entry["c0_candidate"], entry["id"])
            self.assertIsNone(entry["signals"]["demo"], entry["id"])
            self.assertIsNone(entry["signals"]["download"], entry["id"])

    def test_class_one_requires_installation_and_usage(self):
        for entry in self.document["entries"]:
            if entry["evidence_class"] != 1:
                continue
            self.assertTrue(entry["signals"]["docs"], entry["id"])
            self.assertTrue(entry["signals"]["install_documented"], entry["id"])
            self.assertTrue(entry["signals"]["usage_documented"], entry["id"])

    def test_class_three_means_no_usable_documentation(self):
        for entry in self.document["entries"]:
            if entry["evidence_class"] != 3:
                continue
            self.assertFalse(entry["signals"]["docs"], entry["id"])

    def test_unscanned_source_is_unknown_not_notes(self):
        entry = classify(record(scan_status="scan-failed"))
        self.assertIsNone(entry["evidence_class"])
        self.assertEqual(entry["evidence_status"], "unknown")
        self.assertEqual(entry["scope"], "unknown")

    def test_short_readme_is_class_three(self):
        self.assertEqual(classify(record(readme_bytes=200, readme_signals=[]))["evidence_class"], 3)

    def test_missing_usage_is_class_two(self):
        entry = classify(record(readme_signals=["installation", "license-section"]))
        self.assertEqual(entry["evidence_class"], 2)
        self.assertIn("usage", entry["reason"])

    def test_installation_and_usage_is_class_one(self):
        entry = classify(record(readme_signals=["installation", "usage"]))
        self.assertEqual(entry["evidence_class"], 1)
        self.assertEqual(entry["evidence_status"], "observed")
        self.assertEqual(entry["runtime_status"], "not-run")


if __name__ == "__main__":
    unittest.main()
