#!/usr/bin/env python3
"""Assign coarse C0–C3 evidence classes to the automatically scanned repositories.

The curated classifier in ``scripts/classify_evidence_classes.py`` reads each
entry's README, releases and demo media. The automated scan did not retain
those artifacts: ``data/source-index.json`` records README size, heading count
and section signals only. This script therefore uses the same four labels with
a deliberately coarser, documentation-only rubric:

- Class 3: the scan found no usable README documentation.
- Class 2: README documentation exists, but installation or usage is missing.
- Class 1: README documents both installation and usage.
- Class 0: never assigned here. Class 0 requires a manual curated review.

A scan class is not a curated class. It does not observe release assets, demo
media, buildability, runtime behaviour or scope, and it does not change the
scan record. The output is a separate mapping keyed by scan ID.

Usage:
    python3 scripts/classify_scan_evidence.py
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "data" / "source-index.json"
SUPPLEMENTS_PATH = ROOT / "data" / "source-supplements" / "index.json"
OUTPUT_PATH = ROOT / "data" / "scan-evidence-classes.json"
SPEC_VERSION = "scan-evidence-class-v1"
README_MIN_BYTES = 400
SECTION_SIGNALS = ("installation", "usage", "requirements", "examples", "license-section")


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def classify(record: dict) -> dict:
    """Return one scan entry; never assign Class 0 from scan metadata."""
    signals = {str(value) for value in (record.get("readme_signals") or [])}
    bytes_count = record.get("readme_bytes")
    scanned = record.get("scan_status") == "readme-scanned" and isinstance(bytes_count, int)
    heading_count = record.get("readme_heading_count")
    heading_count = heading_count if isinstance(heading_count, int) else 0
    docs = scanned and bytes_count >= README_MIN_BYTES
    install = "installation" in signals
    usage = "usage" in signals
    signal_count = len(signals & set(SECTION_SIGNALS))
    docs_full = bool(docs and install and usage and (heading_count >= 4 or signal_count >= 3))

    if not scanned:
        evidence_class = None
        evidence_status = "unknown"
        reason = "automated scan did not record a readable README"
    elif not docs:
        evidence_class = 3
        evidence_status = "observed"
        reason = "README is missing or shorter than the documentation threshold"
    elif not (install and usage):
        evidence_class = 2
        evidence_status = "observed"
        missing = " and ".join(name for name, present in (("installation", install), ("usage", usage)) if not present)
        reason = f"README documentation exists, but {missing} guidance was not found"
    else:
        evidence_class = 1
        evidence_status = "observed"
        reason = ("README documents installation and usage; release assets, demo media and "
                  "buildability were not observed by the scan")

    return {
        "id": record["id"],
        "full_name": record.get("full_name") or record.get("name") or record["id"],
        "url": record["url"],
        "evidence_class": evidence_class,
        "basis": "scan-metadata",
        "signals": {
            "code": True,
            "code_basis": "repo",
            "docs": docs,
            "docs_bytes": bytes_count if isinstance(bytes_count, int) else None,
            "docs_full": docs_full,
            "install_documented": install,
            "usage_documented": usage,
            "requirements_documented": "requirements" in signals,
            "examples_documented": "examples" in signals,
            "license_section": "license-section" in signals,
            "readme_heading_count": heading_count,
            # Recorded as not observed rather than false: the scan never looked
            # for release assets or demo media.
            "demo": None,
            "download": None,
            "demo_observed": False,
            "download_observed": False,
        },
        "reason": reason,
        "observed_at": record.get("observed_at") or record.get("metadata_observed_at"),
        "evidence_status": evidence_status,
        # Reconstruction scope is not reviewed for automatically scanned entries.
        "scope": "unknown",
        "runtime_status": "not-run",
        "c0_candidate": False,
    }


def supplement_records() -> list[dict]:
    """Published public-cloud batches add scanned repositories beyond source-index.json."""
    if not SUPPLEMENTS_PATH.is_file():
        return []
    index = json.loads(SUPPLEMENTS_PATH.read_text(encoding="utf-8"))
    records = []
    for batch in index.get("batches") or []:
        path = SUPPLEMENTS_PATH.parent / f"{batch}.json"
        if not path.is_file():
            raise SystemExit(f"Missing source supplement: {path}")
        document = json.loads(path.read_text(encoding="utf-8"))
        if document.get("publication_status") != "ready":
            continue
        records.extend(document.get("resources") or [])
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE_PATH)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()

    source = json.loads(args.source.read_text(encoding="utf-8"))
    records = source.get("resources")
    if not isinstance(records, list) or not records:
        raise SystemExit(f"{args.source} has no resource records")
    seen = {record.get("id") for record in records}
    for record in supplement_records():
        if record.get("scan_status") != "readme-scanned" or record.get("id") in seen:
            continue
        seen.add(record.get("id"))
        records.append(record)

    identifiers = [record.get("id") for record in records]
    if any(not isinstance(identifier, str) or not identifier for identifier in identifiers):
        raise SystemExit("Every scan record needs a nonempty string ID")
    if len(identifiers) != len(set(identifiers)):
        raise SystemExit("Scan record IDs must be unique")

    entries = [classify(record) for record in records]
    counts = {str(value): 0 for value in range(4)}
    unknown = 0
    for entry in entries:
        if entry["evidence_class"] is None:
            unknown += 1
        else:
            counts[str(entry["evidence_class"])] += 1

    document = {
        "schema_version": 1,
        "meta": {
            "spec_version": SPEC_VERSION,
            "generated_at": now_utc(),
            "source": "data/source-index.json",
            "source_completed_at": source.get("meta", {}).get("completed_at"),
            "entry_count": len(entries),
            "class_counts": counts,
            "unknown_count": unknown,
            "class_zero_count": 0,
            "method": ("Coarse documentation-evidence classes from the committed automated README scan. "
                       "The scan records README size, heading count and section signals, but not release "
                       "assets, demo images or runtime behaviour. This mapping does not change the scan "
                       "record and is not a curated evidence class."),
            "rubric": {
                "0": "Never assigned automatically. Class 0 requires a manual curated review.",
                "1": "README documents both installation and usage. Demo, release assets and buildability remain unobserved.",
                "2": "README documentation exists, but installation or usage guidance was not found.",
                "3": "No usable README documentation was found by the scan.",
                "unknown": "The automated scan did not record a readable README.",
            },
            "limits": [
                "Scan metadata cannot establish that a project builds, runs or matches any target application.",
                "Section signals come from README headings and keywords; they do not prove the instructions work.",
                "Release assets, demo media and reconstruction scope were not collected for the scan.",
                "A scan class is not comparable to a curated Class 0 review; Class 0 is never assigned here.",
            ],
        },
        "entries": entries,
    }
    args.output.write_text(json.dumps(document, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {len(entries)} scan classes to {args.output.relative_to(ROOT)}")
    print("  " + ", ".join(f"class {key}: {value}" for key, value in counts.items()) + f", unknown: {unknown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
