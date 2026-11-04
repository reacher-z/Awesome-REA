#!/usr/bin/env python3
"""Validate the evidence snapshot and the generated evidence scores.

The two files are a pair:

* ``data/quality-evidence.json`` is a dated public-source snapshot;
* ``data/quality-evaluations.json`` is generated from it by
  ``scripts/quality_scoring.py``.

The pair is optional. A repository with neither file passes; a repository with
only one fails. Every score is recomputed from the committed snapshot, so a
hand edit to a score or a check is rejected.
"""
from __future__ import annotations

import json
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import quality_scoring as scoring  # noqa: E402

EVIDENCE_PATH = ROOT / "data" / "quality-evidence.json"
EVALUATIONS_PATH = ROOT / "data" / "quality-evaluations.json"
EVIDENCE_SPEC = "quality-evidence-v1"
EVIDENCE_KEYS = {"schema_version", "meta", "repos", "pages", "entries"}
EVALUATION_KEYS = {"schema_version", "meta", "entries"}
META_KEYS = {"spec_version", "generated_at", "evidence_snapshot", "evidence_spec",
             "entry_count", "score_count", "median_score", "band_counts",
             "confidence_counts", "dimensions", "method", "limits"}
ENTRY_KEYS = {"id", "name", "url", "kind", "targets", "source", "source_url", "observed_at",
              "confidence", "applicable_dimensions", "dimensions", "score", "band",
              "band_zh", "band_en", "coverage", "dimension_coverage", "limitations"}
DIMENSION_KEYS = {"applicable", "reason", "score", "checks"}
CHECK_KEYS = {"id", "dimension", "label", "points", "status", "reason", "evidence"}
BAND_KEYS = {"strong-evidence", "moderate-evidence", "limited-evidence", "minimal-evidence", "ungraded"}
CONFIDENCES = {"high", "medium", "low", "none"}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\+00:00|Z)$")


def load_json(path: Path, errors: list[str]) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        errors.append(f"{path.name}: cannot read file ({error})")
    except json.JSONDecodeError as error:
        errors.append(f"{path.name}: invalid JSON ({error})")
    return None


def validate_evidence(document: dict, errors: list[str]) -> None:
    if set(document) != EVIDENCE_KEYS:
        errors.append(f"quality-evidence.json: top-level keys must be {sorted(EVIDENCE_KEYS)}")
        return
    if document.get("schema_version") != 1:
        errors.append("quality-evidence.json: schema_version must be 1")
    meta = document.get("meta") or {}
    for key in ("spec", "generated_at", "entry_count", "repository_count", "page_entry_count",
                "repository_observed", "page_observed", "limits"):
        if key not in meta:
            errors.append(f"quality-evidence.json: meta.{key} is required")
    if meta.get("spec") != EVIDENCE_SPEC:
        errors.append(f"quality-evidence.json: meta.spec must be {EVIDENCE_SPEC}")
    if not isinstance(meta.get("limits"), list) or not all(isinstance(item, str) for item in meta["limits"]):
        errors.append("quality-evidence.json: meta.limits must be a list of strings")
    repos = document.get("repos")
    pages = document.get("pages")
    entries = document.get("entries")
    if not isinstance(repos, dict) or not isinstance(pages, dict) or not isinstance(entries, dict):
        errors.append("quality-evidence.json: repos, pages and entries must be objects")
        return
    for slug, repo in repos.items():
        if not isinstance(repo, dict) or repo.get("slug") != slug:
            errors.append(f"quality-evidence.json: repo {slug!r} has an invalid record")
            continue
        if repo.get("status") not in {"observed", "unreachable", "error"}:
            errors.append(f"quality-evidence.json: repo {slug!r} has an unknown status")
        if repo.get("status") == "observed" and not repo.get("repository"):
            errors.append(f"quality-evidence.json: repo {slug!r} is observed but has no repository metadata")
    for entry_id, page in pages.items():
        if not isinstance(page, dict) or page.get("status") not in {"observed", "unreachable", "error"}:
            errors.append(f"quality-evidence.json: page {entry_id!r} has an invalid record")
    for entry_id, link in entries.items():
        if not isinstance(link, dict) or link.get("id") != entry_id:
            errors.append(f"quality-evidence.json: entry link {entry_id!r} is invalid")
            continue
        if link.get("source") == "github" and link.get("repo") not in repos:
            errors.append(f"quality-evidence.json: entry {entry_id!r} names an unknown repo")
        if link.get("source") == "page" and link.get("page") not in pages:
            errors.append(f"quality-evidence.json: entry {entry_id!r} names an unknown page")


def validate_evaluations(document: dict, evidence_document: dict, errors: list[str]) -> None:
    if set(document) != EVALUATION_KEYS:
        errors.append(f"quality-evaluations.json: top-level keys must be {sorted(EVALUATION_KEYS)}")
        return
    if document.get("schema_version") != 1:
        errors.append("quality-evaluations.json: schema_version must be 1")
    meta = document.get("meta") or {}
    if set(meta) != META_KEYS:
        errors.append(f"quality-evaluations.json: meta keys differ (missing={sorted(META_KEYS - set(meta))}, "
                      f"unknown={sorted(set(meta) - META_KEYS)})")
    entries = document.get("entries")
    if not isinstance(entries, list):
        errors.append("quality-evaluations.json: entries must be a list")
        return
    catalog = {record["id"]: record for record in scoring.software_records(scoring.load_catalog())}
    evidence_entries = evidence_document.get("entries") or {}
    repos = evidence_document.get("repos") or {}
    pages = evidence_document.get("pages") or {}
    seen: set[str] = set()
    bands: dict[str, int] = {}
    confidences: dict[str, int] = {}
    scores: list[float] = []
    for index, entry in enumerate(entries):
        label = f"quality-evaluations.json entries[{index}]"
        if not isinstance(entry, dict) or set(entry) != ENTRY_KEYS:
            errors.append(f"{label}: keys differ")
            continue
        entry_id = entry.get("id")
        if entry_id not in catalog:
            errors.append(f"{label}: {entry_id!r} is not a software catalog entry")
            continue
        if entry_id in seen:
            errors.append(f"{label}: duplicate entry {entry_id!r}")
            continue
        seen.add(entry_id)
        record = catalog[entry_id]
        link = evidence_entries.get(entry_id) or {}
        if link.get("source") == "github":
            evidence = dict(repos.get(link.get("repo")) or {})
        elif link.get("source") == "page":
            evidence = dict(pages.get(link.get("page")) or {})
        else:
            evidence = {}
        if evidence:
            evidence.setdefault("source", link.get("source"))
        expected = scoring.score_entry(record, evidence)
        for key in ENTRY_KEYS:
            if entry.get(key) != expected.get(key):
                errors.append(f"{label}: {entry_id} field {key!r} does not match the evidence snapshot")
                break
        if entry.get("confidence") not in CONFIDENCES:
            errors.append(f"{label}: unknown confidence {entry.get('confidence')!r}")
        if entry.get("band") not in BAND_KEYS:
            errors.append(f"{label}: unknown band {entry.get('band')!r}")
        if entry.get("score") is not None:
            if not 0 <= entry["score"] <= 100:
                errors.append(f"{label}: score must be between 0 and 100")
            else:
                scores.append(entry["score"])
        dimensions = entry.get("dimensions") or {}
        if set(dimensions) != set(scoring.DIMENSION_ORDER):
            errors.append(f"{label}: dimensions must contain exactly the nine guide dimensions")
        for dimension, payload in dimensions.items():
            if set(payload) != DIMENSION_KEYS:
                errors.append(f"{label}: dimension {dimension!r} has an invalid shape")
                continue
            if not payload.get("applicable"):
                if payload.get("score") is not None or payload.get("checks"):
                    errors.append(f"{label}: non-applicable dimension {dimension!r} must have no score or checks")
                continue
            checks = payload.get("checks") or []
            if not checks:
                errors.append(f"{label}: applicable dimension {dimension!r} has no checks")
            for item in checks:
                if set(item) != CHECK_KEYS:
                    errors.append(f"{label}: check {item.get('id')!r} has an invalid shape")
                    continue
                if item.get("dimension") != dimension:
                    errors.append(f"{label}: check {item.get('id')!r} has the wrong dimension")
                if item.get("points") not in {0.0, 0.5, 1.0}:
                    errors.append(f"{label}: check {item.get('id')!r} has invalid points")
                status = item.get("status")
                expected_status = "pass" if item.get("points") == 1.0 else (
                    "partial" if item.get("points") == 0.5 else "missing")
                if status != expected_status:
                    errors.append(f"{label}: check {item.get('id')!r} status does not match points")
                if not isinstance(item.get("evidence"), list):
                    errors.append(f"{label}: check {item.get('id')!r} evidence must be a list")
        bands[entry.get("band")] = bands.get(entry.get("band"), 0) + 1
        confidences[entry.get("confidence")] = confidences.get(entry.get("confidence"), 0) + 1
    if seen != set(catalog):
        errors.append(f"quality-evaluations.json: missing {len(set(catalog) - seen)} software entries and "
                      f"{len(seen - set(catalog))} unknown entries")
    if len(entries) != meta.get("entry_count"):
        errors.append("quality-evaluations.json: meta.entry_count does not match entries")
    if len(scores) != meta.get("score_count"):
        errors.append("quality-evaluations.json: meta.score_count does not match scored entries")
    if meta.get("band_counts") != dict(sorted(bands.items())):
        errors.append("quality-evaluations.json: meta.band_counts is stale")
    if meta.get("confidence_counts") != dict(sorted(confidences.items())):
        errors.append("quality-evaluations.json: meta.confidence_counts is stale")
    if scores:
        median = round(statistics.median(scores), 1)
        if meta.get("median_score") != median:
            errors.append("quality-evaluations.json: meta.median_score is stale")
    elif meta.get("median_score") is not None:
        errors.append("quality-evaluations.json: meta.median_score must be null when nothing is scored")


def validate() -> list[str]:
    errors: list[str] = []
    evidence_exists = EVIDENCE_PATH.is_file()
    evaluations_exists = EVALUATIONS_PATH.is_file()
    if not evidence_exists and not evaluations_exists:
        return errors
    if evidence_exists != evaluations_exists:
        return ["quality data must be committed as a pair: data/quality-evidence.json and "
                "data/quality-evaluations.json"]
    evidence_document = load_json(EVIDENCE_PATH, errors)
    evaluations_document = load_json(EVALUATIONS_PATH, errors)
    if evidence_document is not None:
        validate_evidence(evidence_document, errors)
    if evidence_document is not None and evaluations_document is not None:
        validate_evaluations(evaluations_document, evidence_document, errors)
    return errors


def main() -> int:
    errors = validate()
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        print(f"{len(errors)} quality-scoring validation error(s)", file=sys.stderr)
        return 1
    print("Quality evidence and scores are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
