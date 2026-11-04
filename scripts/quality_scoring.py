#!/usr/bin/env python3
"""Score every software entry from the committed public-evidence snapshot.

This is an **evidence score**, not a runtime quality verdict. It answers a
narrow question: how much of the nine evaluation areas in the project's
software-testing guide is supported by public, reproducible evidence? A test
directory, a benchmark or a security policy is evidence that the practice
exists; none of them proves that a feature works. The score is therefore
reported with coverage and confidence, and the page states the difference.

The separate collection step lives in ``scripts/collect_quality_evidence.py``.
This script is offline and deterministic over ``data/quality-evidence.json``,
so the same snapshot always yields the same scores.

Usage:
    python3 scripts/quality_scoring.py --all
    python3 scripts/quality_scoring.py --entry woxi-case --json
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_FILES = ("rea-resources.json", "tool-resources.json")
EVIDENCE_PATH = ROOT / "data" / "quality-evidence.json"
OUTPUT_PATH = ROOT / "data" / "quality-evaluations.json"
SPEC_VERSION = "quality-evidence-score-v1"
SCHEMA_VERSION = 1
SOFTWARE_KINDS = {"case-study", "project", "tool", "integration"}
TARGETS = {"website", "game", "app", "binary", "firmware", "protocol"}

DIMENSIONS = {
    "functional_coverage": ("Functional coverage", "功能覆盖"),
    "correctness": ("Correctness", "正确性"),
    "performance": ("Performance and capacity", "性能与容量"),
    "security_isolation": ("User isolation and secrets", "用户隔离与秘密保护"),
    "ui_consistency": ("UI consistency", "UI 一致性"),
    "persistence_recovery": ("Persistence and recovery", "持久化与故障恢复"),
    "concurrency": ("Concurrency and consistency", "并发与状态一致性"),
    "file_formats": ("File formats and compatibility", "文件格式与外部兼容"),
    "reproducibility": ("Reproducibility and reliability", "可复现性与可靠性"),
}
DIMENSION_ORDER = tuple(DIMENSIONS)
# The guide is nine chapters; each chapter has the same weight in the total.
DIMENSION_WEIGHT = 1.0
BANDS = (
    (75.0, "strong-evidence", "证据充分", "Strong evidence"),
    (50.0, "moderate-evidence", "证据中等", "Moderate evidence"),
    (25.0, "limited-evidence", "证据有限", "Limited evidence"),
    (0.0, "minimal-evidence", "证据很少", "Minimal evidence"),
)
CONFIDENCE = ("high", "medium", "low", "none")

WEB_WORDS = re.compile(r"\b(?:web\s*(?:app|application|site|server|ui)|browser|http\s+server|localhost|"
                       r"frontend|front-end|dashboard)\b", re.I)
CLI_WORDS = re.compile(r"\b(?:command[- ]line|cli|terminal|interpreter|shell|tui)\b", re.I)
GUI_WORDS = re.compile(r"\b(?:desktop|gui|window|editor|toolbox|game|native\s+app)\b", re.I)
SERVICE_WORDS = re.compile(r"\b(?:service|server|api|daemon|protocol|backend)\b", re.I)
SECURITY_CONTEXT = re.compile(r"\b(?:authentication|authorization|permission|role-based|tenant|"
                              r"multi-user|multi-tenant|login|session|account|secret|api\s*key|"
                              r"token|credential|zap|owasp)\b", re.I)
PERSISTENCE_CONTEXT = re.compile(r"\b(?:database|backup|restore|migration|persist(?:ence|ent)?|"
                                 r"storage\s+layer|save\s+file|project\s+file|crash\s+recovery|"
                                 r"rollback)\b", re.I)
CONCURRENCY_CONTEXT = re.compile(r"\b(?:concurren\w*|race\s+condition|parallel\s+execution|"
                                 r"async\s+task|thread\s+pool|transaction|collaborat\w*|"
                                 r"multiplayer|real[- ]time\s+sync|eventual\s+consistency)\b", re.I)
FORMAT_CONTEXT = re.compile(r"\b(?:import|export|convert|file\s+format|round[- ]?trip|"
                            r"interoperab\w*|compatib\w*)\b", re.I)
UNIT = re.compile(r"\b\d+(?:\.\d+)?\s*(?:ms|s|sec|seconds|fps|mb|gb|kb|%|x|ops/s|req/s|rps)\b", re.I)


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def load_catalog() -> list[dict]:
    records = []
    for filename in CATALOG_FILES:
        records.extend(json.loads((ROOT / "data" / filename).read_text(encoding="utf-8")))
    return records


def load_evidence(path: Path | None = None) -> dict:
    path = path or EVIDENCE_PATH
    if not path.is_file():
        raise SystemExit(f"Missing evidence snapshot: {path}. "
                         "Run scripts/collect_quality_evidence.py first.")
    return json.loads(path.read_text(encoding="utf-8"))


def software_records(records: list[dict]) -> list[dict]:
    return [record for record in records if record.get("kind") in SOFTWARE_KINDS]


def entry_text(record: dict) -> str:
    return " ".join([
        record.get("name") or "", record.get("description_en") or "",
        record.get("description_zh") or "", " ".join(record.get("requirements") or []),
    ])


def interfaces_for(record: dict, evidence: dict | None) -> list[str]:
    text = entry_text(record)
    targets = set(record.get("targets") or [])
    interfaces: set[str] = set()
    if "website" in targets or WEB_WORDS.search(text):
        interfaces.add("web")
    if CLI_WORDS.search(text):
        interfaces.add("cli")
    if "game" in targets or "game" in text.lower():
        interfaces.add("game")
    if "app" in targets or GUI_WORDS.search(text):
        interfaces.add("gui")
    if "protocol" in targets or SERVICE_WORDS.search(text):
        interfaces.add("service")
    return sorted(interfaces)


def has_context(record: dict, evidence: dict | None, pattern: re.Pattern) -> bool:
    if pattern.search(entry_text(record)):
        return True
    if evidence:
        readme = evidence.get("readme") or {}
        signals = readme.get("signals") or {}
        if any(signals.get("keywords", {}).values()):
            # Context words are also checked in the retained keyword snippets.
            snippets = " ".join(value for value in (signals.get("keyword_snippets") or {}).values() if value)
            if pattern.search(snippets):
                return True
        if pattern.search(json.dumps(evidence.get("repository") or {})):
            return True
    return False


def applicable_dimensions(record: dict, evidence: dict | None) -> dict[str, str]:
    """Return dimension -> reason. N/A dimensions are not scored."""
    targets = set(record.get("targets") or [])
    interfaces = set(interfaces_for(record, evidence))
    applicable = {dimension: "applies to every software entry" for dimension in DIMENSION_ORDER}
    if not (targets & {"website", "protocol"} or "integration" == record.get("kind")
            or interfaces & {"web", "service"} or has_context(record, evidence, SECURITY_CONTEXT)):
        applicable.pop("security_isolation")
    if not (targets & {"game", "app", "website"} or interfaces & {"gui", "web", "game"}):
        applicable.pop("ui_consistency")
    if not (targets & {"website", "protocol"} or interfaces & {"web", "service"}
            or has_context(record, evidence, PERSISTENCE_CONTEXT)):
        applicable.pop("persistence_recovery")
    if not (targets & {"website", "protocol"} or interfaces & {"web", "service"}
            or "integration" == record.get("kind") or has_context(record, evidence, CONCURRENCY_CONTEXT)):
        applicable.pop("concurrency")
    if not (targets & {"app", "game", "binary", "firmware"}
            or has_context(record, evidence, FORMAT_CONTEXT)):
        applicable.pop("file_formats")
    return applicable


def readme_signals(evidence: dict | None) -> dict:
    evidence = evidence or {}
    return ((evidence.get("readme") or {}).get("signals")
            or evidence.get("signals") or {})


def tree(evidence: dict | None) -> dict:
    return (evidence or {}).get("tree") or {}


def releases(evidence: dict | None) -> dict:
    return (evidence or {}).get("releases") or {}


def section(evidence: dict | None, key: str) -> dict | None:
    return (readme_signals(evidence).get("sections") or {}).get(key)


def keyword(evidence: dict | None, key: str) -> bool:
    return bool((readme_signals(evidence).get("keywords") or {}).get(key))


def snippet(evidence: dict | None, key: str) -> str | None:
    return (readme_signals(evidence).get("keyword_snippets") or {}).get(key)


def claims(evidence: dict | None) -> dict:
    return readme_signals(evidence).get("claims") or {}


def check(check_id: str, dimension: str, label: str, points: float, reason: str,
          evidence_items: list[str] | None = None) -> dict:
    return {
        "id": check_id,
        "dimension": dimension,
        "label": label,
        "points": round(float(points), 3),
        "status": "pass" if points >= 1 else ("partial" if points > 0 else "missing"),
        "reason": reason,
        # The full path/snippet stays in data/quality-evidence.json; the score
        # record keeps only a short audit pointer to stay reviewable in a diff.
        "evidence": [str(item)[:160] for item in (evidence_items or [])[:2] if str(item).strip()],
    }


def functional_coverage(record: dict, evidence: dict | None) -> list[dict]:
    dimension = "functional_coverage"
    signals = readme_signals(evidence)
    sections = signals.get("sections") or {}
    features = sections.get("features")
    usage = sections.get("usage")
    media_count = int(signals.get("media_count") or 0)
    doc_count = int(tree(evidence).get("doc_count") or 0)
    headings = int(signals.get("heading_count") or 0)
    results = []
    if features:
        bullets = int(features.get("bullets") or 0)
        points = 1.0 if bullets >= 3 or len(features.get("snippet") or "") >= 80 else 0.5
        results.append(check("feature-documentation", dimension, "Documented feature set", points,
                             f"README section {features.get('heading')!r}", [features.get("snippet") or ""]))
    else:
        results.append(check("feature-documentation", dimension, "Documented feature set", 0.0,
                             "No feature/capability section found"))
    if usage and (signals.get("code_blocks") or signals.get("install_commands")):
        results.append(check("usage-instructions", dimension, "Usage or command examples", 1.0,
                             f"README section {usage.get('heading')!r} with examples",
                             [usage.get("snippet") or ""]))
    elif usage:
        results.append(check("usage-instructions", dimension, "Usage or command examples", 0.5,
                             f"README section {usage.get('heading')!r} without a code example"))
    else:
        results.append(check("usage-instructions", dimension, "Usage or command examples", 0.0,
                             "No usage section found"))
    docs_links = (signals.get("links") or {}).get("docs") or []
    if doc_count >= 5 or docs_links or headings >= 8:
        results.append(check("documentation-depth", dimension, "Documentation depth", 1.0,
                             f"{doc_count} documentation paths, {headings} headings and "
                             f"{len(docs_links)} documentation links",
                             docs_links[:3]))
    elif doc_count >= 2 or headings >= 4:
        results.append(check("documentation-depth", dimension, "Documentation depth", 0.5,
                             f"{doc_count} documentation paths and {headings} headings"))
    else:
        results.append(check("documentation-depth", dimension, "Documentation depth", 0.0,
                             "Little structured documentation found"))
    if media_count >= 2:
        results.append(check("demo-media", dimension, "Screenshots or demo media", 1.0,
                             f"{media_count} demo images or videos", [item.get("url", "") for item in signals.get("media") or []]))
    elif media_count == 1:
        results.append(check("demo-media", dimension, "Screenshots or demo media", 0.5,
                             "One demo image or video", [signals["media"][0].get("url", "")]))
    else:
        results.append(check("demo-media", dimension, "Screenshots or demo media", 0.0,
                             "No non-branding demo media found"))
    roadmap = sections.get("roadmap")
    if roadmap and (claims(evidence).get("not_implemented") or claims(evidence).get("partial")):
        results.append(check("scope-limits", dimension, "Scope and limits stated", 1.0,
                             "README states current scope and known gaps", [roadmap.get("snippet") or ""]))
    elif roadmap or claims(evidence).get("not_implemented") or claims(evidence).get("partial"):
        results.append(check("scope-limits", dimension, "Scope and limits stated", 0.5,
                             "A scope, roadmap or limitation note is present"))
    else:
        results.append(check("scope-limits", dimension, "Scope and limits stated", 0.0,
                             "No explicit scope or limitation statement"))
    requirements = record.get("requirements") or []
    if len(requirements) >= 3:
        results.append(check("catalog-requirements", dimension, "Reviewed prerequisites", 1.0,
                             f"{len(requirements)} reviewed requirement items", requirements[:3]))
    elif requirements:
        results.append(check("catalog-requirements", dimension, "Reviewed prerequisites", 0.5,
                             "One or two reviewed requirement items", requirements[:3]))
    else:
        results.append(check("catalog-requirements", dimension, "Reviewed prerequisites", 0.0,
                             "No reviewed requirement items"))
    return results


def correctness(record: dict, evidence: dict | None) -> list[dict]:
    dimension = "correctness"
    signals = readme_signals(evidence)
    inventory = tree(evidence)
    test_count = int(inventory.get("test_count") or 0)
    workflows = (evidence or {}).get("workflows") or []
    workflow_commands = [command for workflow in workflows for command in workflow.get("test_commands") or []]
    tests_section = section(evidence, "tests")
    results = []
    if test_count >= 3:
        results.append(check("test-files", dimension, "Test files or suite", 1.0,
                             f"{test_count} test paths", inventory.get("tests", [])[:3]))
    elif test_count >= 1:
        results.append(check("test-files", dimension, "Test files or suite", 0.5,
                             "One or a few test paths", inventory.get("tests", [])[:3]))
    elif inventory.get("spec_docs"):
        results.append(check("test-files", dimension, "Test files or suite", 0.5,
                             "Behaviour specifications are present without test code",
                             inventory.get("spec_docs", [])[:3]))
    else:
        results.append(check("test-files", dimension, "Test files or suite", 0.0,
                             "No test path found"))
    if test_count and inventory.get("ci"):
        results.append(check("test-ci", dimension, "Tests run in CI", 1.0,
                             "Test paths and CI configuration are both present",
                             workflow_commands[:3] or inventory.get("ci", [])[:3]))
    elif workflow_commands:
        results.append(check("test-ci", dimension, "Tests run in CI", 1.0,
                             "A CI workflow names a test command", workflow_commands[:3]))
    elif inventory.get("ci"):
        results.append(check("test-ci", dimension, "Tests run in CI", 0.5,
                             "CI configuration is present without an observed test command",
                             inventory.get("ci", [])[:3]))
    else:
        results.append(check("test-ci", dimension, "Tests run in CI", 0.0,
                             "No CI configuration found"))
    if tests_section:
        results.append(check("test-documentation", dimension, "Testing or verification notes", 1.0,
                             f"README section {tests_section.get('heading')!r}", [tests_section.get("snippet") or ""]))
    elif keyword(evidence, "tests") or claims(evidence).get("tests"):
        results.append(check("test-documentation", dimension, "Testing or verification notes", 0.5,
                             "README mentions tests or verification", [snippet(evidence, "tests") or ""]))
    else:
        results.append(check("test-documentation", dimension, "Testing or verification notes", 0.0,
                             "No testing or verification note found"))
    paths_text = " ".join(inventory.get("tests", []) + inventory.get("manifests", [])).lower()
    if re.search(r"fuzz|property|hypothesis|quickcheck|proptest", paths_text + " " + (snippet(evidence, "tests") or ""), re.I):
        results.append(check("fuzz-property", dimension, "Fuzz or property-based checks", 1.0,
                             "Fuzzing or property-based testing is present"))
    elif keyword(evidence, "tests"):
        results.append(check("fuzz-property", dimension, "Fuzz or property-based checks", 0.5,
                             "Testing is mentioned; fuzzing is not established"))
    else:
        results.append(check("fuzz-property", dimension, "Fuzz or property-based checks", 0.0,
                             "No fuzz or property-based evidence"))
    fixtures = inventory.get("fixtures") or []
    if fixtures:
        results.append(check("verification-artifacts", dimension, "Fixtures or golden data", 1.0,
                             f"{len(fixtures)} fixture or example paths", fixtures[:3]))
    elif claims(evidence).get("tests"):
        results.append(check("verification-artifacts", dimension, "Fixtures or golden data", 0.5,
                             "Testing is mentioned; no fixture path is visible"))
    else:
        results.append(check("verification-artifacts", dimension, "Fixtures or golden data", 0.0,
                             "No fixture or golden data found"))
    return results


def performance(record: dict, evidence: dict | None) -> list[dict]:
    dimension = "performance"
    inventory = tree(evidence)
    benches = inventory.get("benchmarks") or []
    perf_section = section(evidence, "performance")
    results = []
    if benches:
        results.append(check("benchmarks", dimension, "Benchmark code", 1.0,
                             f"{len(benches)} benchmark paths", benches[:3]))
    elif keyword(evidence, "performance"):
        results.append(check("benchmarks", dimension, "Benchmark code", 0.5,
                             "README mentions benchmarks or performance", [snippet(evidence, "performance") or ""]))
    else:
        results.append(check("benchmarks", dimension, "Benchmark code", 0.0,
                             "No benchmark path or note found"))
    if perf_section and UNIT.search(perf_section.get("snippet") or ""):
        results.append(check("performance-numbers", dimension, "Measured performance figures", 1.0,
                             f"README section {perf_section.get('heading')!r} contains measurements",
                             [perf_section.get("snippet") or ""]))
    elif perf_section:
        results.append(check("performance-numbers", dimension, "Measured performance figures", 0.5,
                             f"README section {perf_section.get('heading')!r} without measurements"))
    elif keyword(evidence, "performance"):
        results.append(check("performance-numbers", dimension, "Measured performance figures", 0.5,
                             "Performance is discussed in the README", [snippet(evidence, "performance") or ""]))
    else:
        results.append(check("performance-numbers", dimension, "Measured performance figures", 0.0,
                             "No performance discussion found"))
    profile_text = " ".join(benches).lower() + " " + (snippet(evidence, "performance") or "").lower()
    if re.search(r"profil(?:er|ing)|flamegraph|flame\s+graph|perf\s+record|pyroscope|instruments|tracing", profile_text):
        results.append(check("profiling", dimension, "Profiling evidence", 1.0,
                             "Profiling or tracing evidence is present"))
    elif keyword(evidence, "performance"):
        results.append(check("profiling", dimension, "Profiling evidence", 0.5,
                             "Performance is discussed; profiling is not established"))
    else:
        results.append(check("profiling", dimension, "Profiling evidence", 0.0,
                             "No profiling evidence"))
    budget_text = " ".join(filter(None, [snippet(evidence, "performance"), snippet(evidence, "tests"),
                                         perf_section.get("snippet") if perf_section else ""]))
    if UNIT.search(budget_text):
        results.append(check("performance-budgets", dimension, "Budgets or thresholds", 1.0,
                             "A numeric performance threshold is documented", [budget_text[:200]]))
    elif keyword(evidence, "performance"):
        results.append(check("performance-budgets", dimension, "Budgets or thresholds", 0.5,
                             "Performance is discussed without a threshold"))
    else:
        results.append(check("performance-budgets", dimension, "Budgets or thresholds", 0.0,
                             "No performance threshold documented"))
    return results


def security_isolation(record: dict, evidence: dict | None) -> list[dict]:
    dimension = "security_isolation"
    inventory = tree(evidence)
    security_paths = inventory.get("security") or []
    security_section = section(evidence, "security")
    tests_text = " ".join(inventory.get("tests", [])).lower()
    results = []
    if any(re.search(r"security\.md", path, re.I) for path in security_paths):
        results.append(check("security-policy", dimension, "Security policy", 1.0,
                             "A security policy file is present", security_paths[:3]))
    elif security_section:
        results.append(check("security-policy", dimension, "Security policy", 0.5,
                             f"README section {security_section.get('heading')!r}",
                             [security_section.get("snippet") or ""]))
    else:
        results.append(check("security-policy", dimension, "Security policy", 0.0,
                             "No security policy found"))
    context = " ".join(filter(None, [snippet(evidence, "security"), security_section.get("snippet") if security_section else "",
                                     (security_section or {}).get("heading") or ""]))
    if re.search(r"auth|permission|role|tenant", tests_text) or re.search(r"auth|permission|role|tenant", context, re.I):
        results.append(check("authorization-evidence", dimension, "Authorization or isolation evidence", 1.0,
                             "Authentication, roles or tenant isolation are documented or tested",
                             [context[:200]]))
    else:
        results.append(check("authorization-evidence", dimension, "Authorization or isolation evidence", 0.0,
                             "No authorization or isolation evidence"))
    secret_paths = [path for path in security_paths
                    if re.search(r"gitleaks|snyk|dependabot|renovate|secret", path, re.I)]
    if secret_paths:
        results.append(check("secret-handling", dimension, "Secret and dependency handling", 1.0,
                             "Secret scanning or dependency-update automation is present",
                             secret_paths[:3]))
    elif security_section or keyword(evidence, "security"):
        results.append(check("secret-handling", dimension, "Secret and dependency handling", 0.5,
                             "Security or secret handling is discussed without automation",
                             [snippet(evidence, "security") or ""]))
    elif security_paths:
        results.append(check("secret-handling", dimension, "Secret and dependency handling", 0.5,
                             "Security-related repository files are present", security_paths[:3]))
    else:
        results.append(check("secret-handling", dimension, "Secret and dependency handling", 0.0,
                             "No secret or dependency handling evidence"))
    scan_text = " ".join(security_paths).lower() + " " + context.lower()
    if re.search(r"zap|burp|gitleaks|snyk|trivy|semgrep|codeql|owasp", scan_text):
        results.append(check("security-scanning", dimension, "Dynamic or dependency scanning", 1.0,
                             "A scanner or scan configuration is named"))
    elif security_paths:
        results.append(check("security-scanning", dimension, "Dynamic or dependency scanning", 0.5,
                             "Security automation is present but not a named scanner"))
    else:
        results.append(check("security-scanning", dimension, "Dynamic or dependency scanning", 0.0,
                             "No scanner evidence"))
    return results


def ui_consistency(record: dict, evidence: dict | None) -> list[dict]:
    dimension = "ui_consistency"
    signals = readme_signals(evidence)
    inventory = tree(evidence)
    media_count = int(signals.get("media_count") or 0)
    ui_paths = inventory.get("ui_tests") or []
    results = []
    if media_count >= 2:
        results.append(check("screenshots", dimension, "Screenshots or demo media", 1.0,
                             f"{media_count} demo images or videos",
                             [item.get("url", "") for item in signals.get("media") or []][:3]))
    elif media_count == 1:
        results.append(check("screenshots", dimension, "Screenshots or demo media", 0.5,
                             "One demo image or video", [signals["media"][0].get("url", "")]))
    else:
        results.append(check("screenshots", dimension, "Screenshots or demo media", 0.0,
                             "No non-branding demo media"))
    if any(re.search(r"playwright|cypress|storybook|visual|screenshot", path, re.I) for path in ui_paths):
        results.append(check("ui-tests", dimension, "UI or visual tests", 1.0,
                             "Playwright, Cypress, Storybook or visual tests are present", ui_paths[:3]))
    elif ui_paths:
        results.append(check("ui-tests", dimension, "UI or visual tests", 0.5,
                             "End-to-end or interface tests are present", ui_paths[:3]))
    else:
        results.append(check("ui-tests", dimension, "UI or visual tests", 0.0,
                             "No UI or visual test path found"))
    context = " ".join(filter(None, [snippet(evidence, "ui"), (section(evidence, "ui") or {}).get("snippet") or ""]))
    if re.search(r"accessibility|aria|axe|pa11y|screen reader|keyboard", context, re.I):
        results.append(check("accessibility", dimension, "Accessibility evidence", 1.0,
                             "Accessibility or keyboard support is documented", [context[:200]]))
    elif keyword(evidence, "ui"):
        results.append(check("accessibility", dimension, "Accessibility evidence", 0.5,
                             "The interface is documented without accessibility evidence"))
    else:
        results.append(check("accessibility", dimension, "Accessibility evidence", 0.0,
                             "No accessibility evidence"))
    if section(evidence, "ui"):
        results.append(check("ui-guidance", dimension, "Interface guidance", 1.0,
                             "README has an interface, screenshot or design section",
                             [(section(evidence, "ui") or {}).get("snippet") or ""]))
    elif keyword(evidence, "ui"):
        results.append(check("ui-guidance", dimension, "Interface guidance", 0.5,
                             "The README mentions the interface"))
    else:
        results.append(check("ui-guidance", dimension, "Interface guidance", 0.0,
                             "No interface guidance found"))
    return results


def persistence_recovery(record: dict, evidence: dict | None) -> list[dict]:
    dimension = "persistence_recovery"
    inventory = tree(evidence)
    migrations = inventory.get("migrations") or []
    tests_text = " ".join(inventory.get("tests", [])).lower()
    context = " ".join(filter(None, [snippet(evidence, "persistence"),
                                     (section(evidence, "persistence") or {}).get("snippet") or ""]))
    results = []
    if re.search(r"persist|backup|restore|migration|retry|idempotent|recovery", tests_text + " " + context, re.I):
        results.append(check("persistence-evidence", dimension, "Persistence or recovery evidence", 1.0,
                             "Persistence, migration or recovery is documented or tested",
                             [context[:200]]))
    elif keyword(evidence, "persistence"):
        results.append(check("persistence-evidence", dimension, "Persistence or recovery evidence", 0.5,
                             "Persistence is mentioned without a test or procedure"))
    else:
        results.append(check("persistence-evidence", dimension, "Persistence or recovery evidence", 0.0,
                             "No persistence or recovery evidence"))
    if migrations:
        results.append(check("storage-layer", dimension, "Storage or migration layer", 1.0,
                             "Database migrations or a storage schema are present", migrations[:3]))
    elif keyword(evidence, "persistence"):
        results.append(check("storage-layer", dimension, "Storage or migration layer", 0.5,
                             "Storage is discussed without a visible migration layer"))
    else:
        results.append(check("storage-layer", dimension, "Storage or migration layer", 0.0,
                             "No storage layer found"))
    failure_text = " ".join(filter(None, [snippet(evidence, "persistence"), context]))
    if re.search(r"retry|idempotent|transaction|rollback|timeout|recover(?:y|s|ed)?\b", failure_text, re.I):
        results.append(check("failure-handling", dimension, "Failure handling", 1.0,
                             "Retry, transaction or recovery behaviour is documented", [failure_text[:200]]))
    elif keyword(evidence, "persistence"):
        results.append(check("failure-handling", dimension, "Failure handling", 0.5,
                             "Persistence is discussed without failure handling"))
    else:
        results.append(check("failure-handling", dimension, "Failure handling", 0.0,
                             "No failure handling evidence"))
    if section(evidence, "persistence") and (keyword(evidence, "persistence") or migrations):
        results.append(check("recovery-documentation", dimension, "Backup or recovery documentation", 1.0,
                             "A persistence, backup or recovery section is present",
                             [(section(evidence, "persistence") or {}).get("snippet") or ""]))
    elif keyword(evidence, "persistence"):
        results.append(check("recovery-documentation", dimension, "Backup or recovery documentation", 0.5,
                             "Persistence is mentioned in the README"))
    else:
        results.append(check("recovery-documentation", dimension, "Backup or recovery documentation", 0.0,
                             "No backup or recovery documentation"))
    return results


def concurrency(record: dict, evidence: dict | None) -> list[dict]:
    dimension = "concurrency"
    inventory = tree(evidence)
    tests_text = " ".join(inventory.get("tests", [])).lower()
    context = " ".join(filter(None, [snippet(evidence, "concurrency"),
                                     (section(evidence, "concurrency") or {}).get("snippet") or ""]))
    results = []
    if re.search(r"concurren|race\s+condition|parallel\s+execution|thread\s+pool|async\s+task|"
                 r"transaction|mutex|atomic|collaborat", tests_text + " " + context, re.I):
        results.append(check("concurrency-evidence", dimension, "Concurrency evidence", 1.0,
                             "Concurrency, transactions or race handling are documented or tested",
                             [context[:200]]))
    elif keyword(evidence, "concurrency"):
        results.append(check("concurrency-evidence", dimension, "Concurrency evidence", 0.5,
                             "Concurrency is mentioned without a test"))
    else:
        results.append(check("concurrency-evidence", dimension, "Concurrency evidence", 0.0,
                             "No concurrency evidence"))
    if section(evidence, "concurrency"):
        results.append(check("consistency-documentation", dimension, "Consistency model", 1.0,
                             "A concurrency or consistency section is present",
                             [(section(evidence, "concurrency") or {}).get("snippet") or ""]))
    elif re.search(r"consisten|transaction|atomic|lock-free|idempotent|eventual", context, re.I):
        results.append(check("consistency-documentation", dimension, "Consistency model", 0.5,
                             "Consistency is discussed in the README"))
    else:
        results.append(check("consistency-documentation", dimension, "Consistency model", 0.0,
                             "No consistency model documented"))
    load_text = " ".join(inventory.get("benchmarks", [])).lower() + " " + context.lower()
    if re.search(r"k6|locust|stress|load\s+test|concurrent|parallel", load_text, re.I):
        results.append(check("load-evidence", dimension, "Load or stress evidence", 1.0,
                             "Load, stress or concurrent execution is described"))
    elif keyword(evidence, "concurrency"):
        results.append(check("load-evidence", dimension, "Load or stress evidence", 0.5,
                             "Concurrency is discussed without a load scenario"))
    else:
        results.append(check("load-evidence", dimension, "Load or stress evidence", 0.0,
                             "No load or stress evidence"))
    return results


def file_formats(record: dict, evidence: dict | None) -> list[dict]:
    dimension = "file_formats"
    inventory = tree(evidence)
    formats = inventory.get("formats") or {}
    context = " ".join(filter(None, [snippet(evidence, "formats"),
                                     (section(evidence, "formats") or {}).get("snippet") or ""]))
    results = []
    if section(evidence, "formats") or keyword(evidence, "formats"):
        results.append(check("import-export", dimension, "Import or export evidence", 1.0,
                             "Import, export or format compatibility is documented", [context[:200]]))
    else:
        results.append(check("import-export", dimension, "Import or export evidence", 0.0,
                             "No import or export evidence"))
    validator_text = " ".join(inventory.get("ci", []) + inventory.get("benchmarks", [])) + " " + context
    if re.search(r"qpdf|gltf[-_ ]?validator|pdfium|ffmpeg|imagemagick|magick|validator", validator_text, re.I):
        results.append(check("format-validators", dimension, "Format validator", 1.0,
                             "A format validator or validator configuration is named"))
    elif formats:
        results.append(check("format-validators", dimension, "Format validator", 0.5,
                             "Format-specific files are present without a validator",
                             [f"{suffix}: {count}" for suffix, count in list(formats.items())[:5]]))
    else:
        results.append(check("format-validators", dimension, "Format validator", 0.0,
                             "No format validator evidence"))
    fixtures = inventory.get("fixtures") or []
    if fixtures and formats:
        results.append(check("format-fixtures", dimension, "Format fixtures", 1.0,
                             "Fixtures and format-specific files are present", fixtures[:3]))
    elif fixtures or formats:
        results.append(check("format-fixtures", dimension, "Format fixtures", 0.5,
                             "Some format-specific files or fixtures are present"))
    else:
        results.append(check("format-fixtures", dimension, "Format fixtures", 0.0,
                             "No format fixtures"))
    if re.search(r"round.?trip|lossless|lossy|interoperab|compatib|external\s+consumer|"
                 r"imported\s+by|exported\s+to", context, re.I):
        results.append(check("roundtrip-evidence", dimension, "Round-trip or consumer check", 1.0,
                             "Round-trip or external-consumer compatibility is discussed", [context[:200]]))
    elif keyword(evidence, "formats"):
        results.append(check("roundtrip-evidence", dimension, "Round-trip or consumer check", 0.5,
                             "Formats are discussed without round-trip evidence"))
    else:
        results.append(check("roundtrip-evidence", dimension, "Round-trip or consumer check", 0.0,
                             "No round-trip evidence"))
    return results


def reproducibility(record: dict, evidence: dict | None) -> list[dict]:
    dimension = "reproducibility"
    inventory = tree(evidence)
    signals = readme_signals(evidence)
    release_data = releases(evidence)
    repository = (evidence or {}).get("repository") or {}
    results = []
    licenses = inventory.get("license") or []
    if repository.get("license") or licenses:
        results.append(check("license", dimension, "License", 1.0,
                             f"License {repository.get('license') or licenses[0]}",
                             [repository.get("license") or ""] + licenses[:2]))
    elif section(evidence, "license"):
        results.append(check("license", dimension, "License", 0.5,
                             "A license section is present but no license file was observed"))
    else:
        results.append(check("license", dimension, "License", 0.0, "No license evidence"))
    manifests = inventory.get("manifests") or []
    if manifests:
        results.append(check("build-manifest", dimension, "Build manifest", 1.0,
                             f"Build manifest(s): {', '.join(manifests[:3])}", manifests[:3]))
    elif signals.get("install_commands"):
        results.append(check("build-manifest", dimension, "Build manifest", 0.5,
                             "Install or build instructions are present without a manifest",
                             signals.get("install_commands", [])[:3]))
    else:
        results.append(check("build-manifest", dimension, "Build manifest", 0.0,
                             "No build manifest or install instructions"))
    locks = inventory.get("lockfiles") or []
    if locks:
        results.append(check("lockfile", dimension, "Dependency lockfile", 1.0,
                             f"Lockfile(s): {', '.join(locks[:3])}", locks[:3]))
    elif inventory.get("docker") or manifests:
        results.append(check("lockfile", dimension, "Dependency lockfile", 0.5,
                             "A container or manifest is present without a lockfile",
                             inventory.get("docker", [])[:3]))
    else:
        results.append(check("lockfile", dimension, "Dependency lockfile", 0.0,
                             "No dependency lock evidence"))
    if inventory.get("ci"):
        results.append(check("ci", dimension, "Continuous integration", 1.0,
                             f"CI configuration: {', '.join(inventory.get('ci', [])[:3])}",
                             inventory.get("ci", [])[:3]))
    else:
        results.append(check("ci", dimension, "Continuous integration", 0.0,
                             "No CI configuration"))
    if signals.get("install_commands") or section(evidence, "install"):
        results.append(check("install-documentation", dimension, "Installation instructions", 1.0,
                             "Install or build steps are documented",
                             signals.get("install_commands", [])[:3]))
    else:
        results.append(check("install-documentation", dimension, "Installation instructions", 0.0,
                             "No installation instructions"))
    if release_data.get("semver_tags"):
        results.append(check("versioned-release", dimension, "Versioned release", 1.0,
                             f"Versioned tags: {', '.join(release_data['semver_tags'][:3])}",
                             release_data.get("semver_tags", [])[:3]))
    elif release_data.get("count"):
        results.append(check("versioned-release", dimension, "Versioned release", 0.5,
                             f"{release_data.get('count')} release(s) without a semantic version tag"))
    else:
        results.append(check("versioned-release", dimension, "Versioned release", 0.0,
                             "No release observed"))
    package_installs = [command for command in signals.get("install_commands") or []
                        if re.match(r"^(?:npm|npx|bunx|bun|yarn|pnpm|pip|pipx|uv|cargo|go|brew|gem|"
                                    r"conda|dotnet|winget|scoop|choco|luarocks|pacman|apt)\b", command, re.I)
                        and not re.search(r"--git|--path|from\s+source", command, re.I)]
    if release_data.get("asset_count") or release_data.get("checksums") or package_installs:
        results.append(check("artifact", dimension, "Distributable artifact", 1.0,
                             "A release asset, checksum or package-registry install command is present",
                             (release_data.get("checksums") or [])[:3] + package_installs[:2]))
    elif release_data.get("count"):
        results.append(check("artifact", dimension, "Distributable artifact", 0.5,
                             "Releases exist without a visible downloadable artifact"))
    else:
        results.append(check("artifact", dimension, "Distributable artifact", 0.0,
                             "No distributable artifact observed"))
    pushed = repository.get("pushed_at")
    archived = bool(repository.get("archived"))
    if archived:
        results.append(check("maintenance", dimension, "Maintenance state", 0.0,
                             "Repository is archived"))
    elif pushed:
        try:
            pushed_at = dt.datetime.fromisoformat(pushed.replace("Z", "+00:00"))
            observed = (evidence or {}).get("observed_at")
            reference = (dt.datetime.fromisoformat(observed.replace("Z", "+00:00"))
                         if observed else dt.datetime.now(dt.timezone.utc))
            age_days = (reference - pushed_at).days
            if age_days <= 730:
                results.append(check("maintenance", dimension, "Maintenance state", 1.0,
                                     f"Last push {age_days} days before the snapshot", [pushed]))
            else:
                results.append(check("maintenance", dimension, "Maintenance state", 0.5,
                                     f"Last push {age_days} days before the snapshot", [pushed]))
        except ValueError:
            results.append(check("maintenance", dimension, "Maintenance state", 0.5,
                                 "Last push date could not be parsed"))
    else:
        results.append(check("maintenance", dimension, "Maintenance state", 0.0,
                             "No repository maintenance metadata"))
    return results


CHECK_BUILDERS = {
    "functional_coverage": functional_coverage,
    "correctness": correctness,
    "performance": performance,
    "security_isolation": security_isolation,
    "ui_consistency": ui_consistency,
    "persistence_recovery": persistence_recovery,
    "concurrency": concurrency,
    "file_formats": file_formats,
    "reproducibility": reproducibility,
}


def confidence_for(evidence: dict | None) -> str:
    if not evidence or evidence.get("status") != "observed":
        return "none"
    has_tree = bool((evidence or {}).get("tree"))
    has_readme = bool((evidence or {}).get("readme"))
    if has_tree and has_readme and not (evidence["tree"] or {}).get("truncated"):
        return "high"
    if has_tree or has_readme:
        return "medium"
    return "low"


def band_for(score: float | None) -> tuple[str, str, str]:
    if score is None:
        return ("ungraded", "未评分", "Ungraded")
    for threshold, key, zh, en in BANDS:
        if score >= threshold:
            return (key, zh, en)
    return ("minimal-evidence", "证据很少", "Minimal evidence")


def score_entry(record: dict, evidence: dict | None) -> dict:
    applicable = applicable_dimensions(record, evidence)
    dimensions = {}
    total_points = 0.0
    total_checks = 0
    evidenced_checks = 0
    for dimension in DIMENSION_ORDER:
        if dimension not in applicable:
            dimensions[dimension] = {
                "applicable": False,
                "reason": "not applicable to this software type",
                "score": None,
                "checks": [],
            }
            continue
        checks = CHECK_BUILDERS[dimension](record, evidence)
        points = sum(item["points"] for item in checks) / len(checks) if checks else 0.0
        total_points += points * DIMENSION_WEIGHT
        total_checks += len(checks)
        evidenced_checks += sum(1 for item in checks if item["points"] > 0)
        dimensions[dimension] = {
            "applicable": True,
            "reason": applicable[dimension],
            "score": round(100 * points, 1),
            "checks": checks,
        }
    applicable_count = len(applicable)
    page_only_tool = (bool(evidence) and evidence.get("source") == "page"
                      and record.get("kind") in {"tool", "integration", "project"}
                      and not evidence.get("tree") and not evidence.get("readme"))
    observed = (bool(evidence) and evidence.get("status") == "observed" and not page_only_tool
                and bool(evidence.get("readme") or evidence.get("tree") or evidence.get("signals")))
    score = round(100 * total_points / applicable_count, 1) if observed and applicable_count else None
    dimensions_with_evidence = sum(
        1 for item in dimensions.values() if item["applicable"] and item["score"] and item["score"] >= 50)
    coverage = round(100 * evidenced_checks / total_checks, 1) if observed and total_checks else 0.0
    confidence = confidence_for(evidence) if observed else "none"
    band, band_zh, band_en = band_for(score)
    limitations = []
    if not evidence or evidence.get("status") != "observed" or page_only_tool:
        limitations.append("No public repository evidence could be observed; the entry is ungraded.")
    else:
        if not evidence.get("tree"):
            limitations.append("No complete repository tree was observed; file-level checks are absent.")
        if not evidence.get("readme"):
            limitations.append("No README was observed; documentation checks are absent.")
        if not evidence.get("releases"):
            limitations.append("No release metadata was observed.")
        if confidence != "high":
            limitations.append("Source evidence is partial; compare the confidence and coverage fields.")
    limitations.append("Evidence score, not runtime verification: a test directory or README claim does not prove behaviour.")
    return {
        "id": record["id"],
        "name": record.get("name"),
        "url": record["url"],
        "kind": record.get("kind"),
        "targets": record.get("targets") or [],
        "source": (evidence or {}).get("source") or ("github" if (evidence or {}).get("slug") else "page"),
        "source_url": (evidence or {}).get("url"),
        "observed_at": (evidence or {}).get("observed_at"),
        "confidence": confidence,
        "applicable_dimensions": sorted(applicable),
        "dimensions": dimensions,
        "score": score,
        "band": band,
        "band_zh": band_zh,
        "band_en": band_en,
        "coverage": coverage,
        "dimension_coverage": round(100 * dimensions_with_evidence / applicable_count, 1) if applicable_count else 0.0,
        "limitations": limitations,
    }


def evaluation_document(entries: list[dict], evidence_document: dict) -> dict:
    counts: dict[str, int] = {}
    confidences: dict[str, int] = {}
    for entry in entries:
        counts[entry["band"]] = counts.get(entry["band"], 0) + 1
        confidences[entry["confidence"]] = confidences.get(entry["confidence"], 0) + 1
    scores = [entry["score"] for entry in entries if entry["score"] is not None]
    return {
        "schema_version": SCHEMA_VERSION,
        "meta": {
            "spec_version": SPEC_VERSION,
            "generated_at": now_utc(),
            "evidence_snapshot": evidence_document.get("meta", {}).get("generated_at"),
            "evidence_spec": evidence_document.get("meta", {}).get("spec"),
            "entry_count": len(entries),
            "score_count": len(scores),
            "median_score": round(statistics.median(scores), 1) if scores else None,
            "band_counts": dict(sorted(counts.items())),
            "confidence_counts": dict(sorted(confidences.items())),
            "dimensions": [
                {"id": key, "en": DIMENSIONS[key][0], "zh": DIMENSIONS[key][1],
                 "weight": DIMENSION_WEIGHT}
                for key in DIMENSION_ORDER
            ],
            "method": "Equal-weight mean of nine evidence dimensions. Each dimension is the mean of its "
                      "checks (pass=1, partial=0.5, missing=0); dimensions that do not apply are excluded. "
                      "Scores are evidence coverage, not runtime quality.",
            "limits": evidence_document.get("meta", {}).get("limits", []),
        },
        "entries": entries,
    }


def write_document(document: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # This file has one record per catalog software entry; compact JSON keeps the
    # generated artifact reviewable without turning every check into five lines.
    path.write_text(json.dumps(document, ensure_ascii=False, separators=(",", ":")) + "\n",
                    encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entry", action="append", help="Catalog entry ID; repeatable")
    parser.add_argument("--all", action="store_true", help="Every software entry in the catalog")
    parser.add_argument("--evidence", type=Path, default=EVIDENCE_PATH)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--json", action="store_true", help="Print the document instead of a summary")
    args = parser.parse_args()
    if not args.entry and not args.all:
        parser.error("choose --entry ID or --all")
    records = {record["id"]: record for record in software_records(load_catalog())}
    if args.entry:
        missing = [entry_id for entry_id in args.entry if entry_id not in records]
        if missing:
            parser.error("unknown software entry ID(s): " + ", ".join(missing))
        selected = [records[entry_id] for entry_id in args.entry]
    else:
        selected = list(records.values())
    evidence_document = load_evidence(args.evidence)
    evidence_entries = evidence_document.get("entries") or {}
    evidence_repos = evidence_document.get("repos") or {}
    evidence_pages = evidence_document.get("pages") or {}
    evaluated = []
    for record in selected:
        link = evidence_entries.get(record["id"]) or {}
        if link.get("source") == "github":
            evidence = dict(evidence_repos.get(link.get("repo")) or {})
        elif link.get("source") == "page":
            evidence = dict(evidence_pages.get(link.get("page")) or {})
        else:
            evidence = {}
        if evidence:
            evidence.setdefault("source", link.get("source") or ("github" if evidence.get("slug") else "page"))
        evaluated.append(score_entry(record, evidence))
    document = evaluation_document(evaluated, evidence_document)
    write_document(document, args.output)
    if args.json:
        print(json.dumps(document, ensure_ascii=False, indent=1))
    else:
        print(f"wrote {len(evaluated)} software entries to {args.output}")
        for band, count in document["meta"]["band_counts"].items():
            print(f"  {band}: {count}")
        if document["meta"]["median_score"] is not None:
            print(f"  median score: {document['meta']['median_score']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
