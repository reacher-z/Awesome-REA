#!/usr/bin/env python3
"""Build the bilingual evidence-score directory from generated evaluations."""
from __future__ import annotations

from html import escape
import json
from pathlib import Path

from asset_paths import fingerprinted_href
from build_entry_pages import entry_path
from open_graph import THEME_COLOR_META, open_graph_meta, website_reference
from site_footer import site_footer

SITE_URL = "https://awesomerea.org"
REPOSITORY_URL = "https://github.com/reacher-z/Awesome-REA"

LABELS = {
    "en": {
        "title": "Software evidence scores",
        "kicker": "PUBLIC EVIDENCE · NOT RUNTIME TESTING",
        "description": "A comparable, reproducible reading of how much of the nine evaluation areas in the "
                       "software-testing guide is supported by public evidence for each catalogued software project.",
        "breadcrumb": "Evidence scores",
        "definitionOneTitle": "Every catalogued software entry",
        "definitionOne": "Tools, integrations, reconstructions and projects are scored with the same rubric. "
                         "Dimensions that do not apply are left out, not counted as zero.",
        "definitionTwoTitle": "Nine equal dimensions",
        "definitionTwo": "Functional coverage, correctness, performance, isolation, UI, persistence, concurrency, "
                         "formats and reproducibility each contribute one ninth of the score.",
        "definitionThreeTitle": "Not a runtime verdict",
        "definitionThree": "A test directory or a README claim proves that evidence exists, not that the software "
                           "works. Read the confidence, coverage and limitations with every number.",
        "statEntries": "software entries",
        "statScored": "entries with a score",
        "statMedian": "median score",
        "statConfidence": "high-confidence entries",
        "methodTitle": "How the score is calculated",
        "methodBody": "Each dimension is the mean of its checks: pass = 1, partial = 0.5, missing = 0. "
                      "Applicable dimensions are averaged with equal weight. The score is evidence coverage, "
                      "not an estimate of product quality.",
        "methodSnapshot": "Evidence snapshot",
        "methodSource": "The snapshot is collected from public GitHub metadata, README text, repository trees, "
                        "release assets and up to two CI workflow files, or from the public page for non-GitHub "
                        "entries. No executable is downloaded or run.",
        "methodLimits": "Limits",
        "controlsSearch": "Search software",
        "controlsKind": "Type",
        "controlsTarget": "Target",
        "controlsBand": "Evidence band",
        "controlsConfidence": "Confidence",
        "controlsSort": "Sort",
        "sortScoreDesc": "Score, high to low",
        "sortScoreAsc": "Score, low to high",
        "sortName": "Name",
        "sortCoverage": "Evidence coverage",
        "sortConfidence": "Confidence",
        "all": "All",
        "tableRank": "#",
        "tableScore": "Score",
        "tableSoftware": "Software",
        "tableKind": "Type",
        "tableTargets": "Targets",
        "tableConfidence": "Confidence",
        "tableCoverage": "Coverage",
        "tableDimensions": "Nine dimensions",
        "tableBand": "Band",
        "empty": "No software matches these filters.",
        "noscript": "Filters and the audit panel require JavaScript. The table still lists every scored software entry.",
        "count": "Showing",
        "confidence": "Confidence",
        "coverage": "Evidence coverage",
        "notApplicable": "N/A",
        "missingChecks": "Missing checks",
        "limits": "Limitations",
        "loading": "Loading evidence…",
        "detailUnavailable": "Detailed evidence is unavailable.",
        "openEntry": "Open catalog entry",
        "openSource": "Open upstream source ↗",
        "close": "Close details",
        "detailTitle": "Software details",
        "download": "Download the score data ↓",
        "footerNote": "Original content: MIT. Scores describe public evidence, not runtime quality.",
        "bandStrong": "Strong evidence",
        "bandModerate": "Moderate evidence",
        "bandLimited": "Limited evidence",
        "bandMinimal": "Minimal evidence",
        "bandUngraded": "Ungraded",
        "langName": "English",
        "otherLangName": "简体中文",
        "navHome": "AwesomeREA home",
        "submit": "Submit a resource",
    },
    "zh": {
        "title": "软件证据评分",
        "kicker": "公开证据 · 不是实测",
        "description": "用同一套规则，可复现地衡量每个目录软件项目在软测指南九个评测维度上拥有多少公开证据。",
        "breadcrumb": "证据评分",
        "definitionOneTitle": "目录内全部软件条目",
        "definitionOne": "工具、集成、复刻项目和案例使用同一套评分规则；不适用的维度直接排除，不按零分计入。",
        "definitionTwoTitle": "九个维度等权",
        "definitionTwo": "功能覆盖、正确性、性能、隔离、UI、持久化、并发、文件格式和可复现性各占九分之一。",
        "definitionThreeTitle": "不是实测结论",
        "definitionThree": "测试目录或 README 声明只能证明证据存在，不能证明软件可用；请同时阅读置信度、覆盖率和局限。",
        "statEntries": "个软件条目",
        "statScored": "个条目有分数",
        "statMedian": "中位分",
        "statConfidence": "高置信条目",
        "methodTitle": "分数如何计算",
        "methodBody": "每个维度取检查项的平均值：通过 = 1，部分 = 0.5，缺失 = 0；适用维度等权平均。"
                      "分数表示证据覆盖程度，不是产品质量估计。",
        "methodSnapshot": "证据快照",
        "methodSource": "快照来自公开的 GitHub 元数据、README 文本、仓库文件树、Release 产物和最多两个 CI "
                        "工作流文件；非 GitHub 条目读取公开页面。不下载、不运行可执行文件。",
        "methodLimits": "限制",
        "controlsSearch": "搜索软件",
        "controlsKind": "类型",
        "controlsTarget": "目标",
        "controlsBand": "证据档位",
        "controlsConfidence": "置信度",
        "controlsSort": "排序",
        "sortScoreDesc": "分数从高到低",
        "sortScoreAsc": "分数从低到高",
        "sortName": "名称",
        "sortCoverage": "证据覆盖率",
        "sortConfidence": "置信度",
        "all": "全部",
        "tableRank": "#",
        "tableScore": "分数",
        "tableSoftware": "软件",
        "tableKind": "类型",
        "tableTargets": "目标",
        "tableConfidence": "置信度",
        "tableCoverage": "覆盖率",
        "tableDimensions": "九个维度",
        "tableBand": "档位",
        "empty": "没有符合筛选条件的软件。",
        "noscript": "筛选和证据面板需要 JavaScript；下表仍然列出全部评分软件。",
        "count": "显示",
        "confidence": "置信度",
        "coverage": "证据覆盖率",
        "notApplicable": "不适用",
        "missingChecks": "缺失检查",
        "limits": "局限",
        "loading": "正在加载证据…",
        "detailUnavailable": "详细的证据数据不可用。",
        "openEntry": "打开目录条目",
        "openSource": "打开上游来源 ↗",
        "close": "关闭详情",
        "detailTitle": "软件详情",
        "download": "下载评分数据 ↓",
        "footerNote": "原创内容：MIT。评分描述公开证据，不代表实测质量。",
        "bandStrong": "证据充分",
        "bandModerate": "证据中等",
        "bandLimited": "证据有限",
        "bandMinimal": "证据很少",
        "bandUngraded": "未评分",
        "langName": "简体中文",
        "otherLangName": "English",
        "navHome": "AwesomeREA 首页",
        "submit": "提交资源",
    },
}

BAND_CLASS = {
    "strong-evidence": "quality-band-strong",
    "moderate-evidence": "quality-band-moderate",
    "limited-evidence": "quality-band-limited",
    "minimal-evidence": "quality-band-minimal",
    "ungraded": "quality-band-ungraded",
}
CONFIDENCE_ORDER = {"high": 0, "medium": 1, "low": 2, "none": 3}
CHECK_LABELS_ZH = {
    "feature-documentation": "已记录的功能集",
    "usage-instructions": "用法或命令示例",
    "documentation-depth": "文档深度",
    "demo-media": "截图或演示媒体",
    "scope-limits": "范围与限制",
    "catalog-requirements": "已复核的前提条件",
    "test-files": "测试文件或测试套件",
    "test-ci": "CI 中运行测试",
    "test-documentation": "测试或验证说明",
    "fuzz-property": "模糊测试或性质测试",
    "verification-artifacts": "fixture 或 golden 数据",
    "benchmarks": "基准测试代码",
    "performance-numbers": "实测性能数字",
    "profiling": "性能剖析证据",
    "performance-budgets": "性能预算或阈值",
    "security-policy": "安全策略",
    "authorization-evidence": "授权或隔离证据",
    "secret-handling": "秘密与依赖处理",
    "security-scanning": "动态或依赖扫描",
    "screenshots": "截图或演示媒体",
    "ui-tests": "UI 或视觉测试",
    "accessibility": "可访问性证据",
    "ui-guidance": "界面说明",
    "persistence-evidence": "持久化或恢复证据",
    "storage-layer": "存储或迁移层",
    "failure-handling": "失败处理",
    "recovery-documentation": "备份或恢复文档",
    "concurrency-evidence": "并发证据",
    "consistency-documentation": "一致性模型",
    "load-evidence": "负载或压力证据",
    "import-export": "导入或导出证据",
    "format-validators": "格式校验器",
    "format-fixtures": "格式 fixture",
    "roundtrip-evidence": "往返或消费端检查",
    "license": "许可证",
    "build-manifest": "构建清单",
    "lockfile": "依赖锁文件",
    "ci": "持续集成",
    "install-documentation": "安装说明",
    "versioned-release": "版本化发布",
    "artifact": "可分发包",
    "maintenance": "维护状态",
}


def values_for(language: str) -> dict:
    return LABELS["zh" if language == "zh" else "en"]


def json_for_html(value) -> str:
    """JSON that cannot close its surrounding script element."""
    return json.dumps(value, ensure_ascii=False).replace("<", "\\u003c")


def band_label(entry: dict, language: str) -> str:
    labels = values_for(language)
    return {
        "strong-evidence": labels["bandStrong"],
        "moderate-evidence": labels["bandModerate"],
        "limited-evidence": labels["bandLimited"],
        "minimal-evidence": labels["bandMinimal"],
        "ungraded": labels["bandUngraded"],
    }.get(entry.get("band"), labels["bandUngraded"])


def sort_entries(entries: list[dict]) -> list[dict]:
    return sorted(entries, key=lambda entry: (
        entry["score"] is None,
        -(entry["score"] if entry["score"] is not None else 0),
        (entry.get("name") or "").casefold(), entry["id"],
    ))


def record_links(resources: list[dict], translations: dict) -> dict:
    links = {}
    for record in resources:
        links[record["id"]] = {
            "entry_url": entry_path("resource", record["id"], "en"),
            "entry_url_zh": entry_path("resource", record["id"], "zh"),
            "name_zh": (translations.get(record["id"]) or {}).get("name") or record.get("name"),
        }
    return links


def compact_entry(entry: dict, links: dict, dimension_meta: list[dict], *, include_checks: bool = False) -> dict:
    link = links.get(entry["id"], {})
    dimension_details = []
    for dimension in dimension_meta:
        payload = (entry.get("dimensions") or {}).get(dimension["id"]) or {}
        checks = []
        missing_count = 0
        if include_checks and payload.get("applicable"):
            for item in payload.get("checks") or []:
                if item.get("points", 0) > 0:
                    checks.append([item["id"], item["status"], (item.get("reason") or "")[:160]])
                else:
                    missing_count += 1
                    if sum(1 for check in checks if check[1] == "missing") < 2:
                        checks.append([item["id"], item["status"], (item.get("reason") or "")[:160]])
        dimension_details.append({
            "id": dimension["id"],
            "label_en": dimension["en"],
            "label_zh": dimension["zh"],
            "applicable": bool(payload.get("applicable")),
            "score": payload.get("score"),
            "checks": checks,
            "missing_count": missing_count,
        })
    return {
        "id": entry["id"],
        "name": entry.get("name"),
        "name_zh": link.get("name_zh") or entry.get("name"),
        "entry_url": link.get("entry_url"),
        "entry_url_zh": link.get("entry_url_zh"),
        "url": entry.get("url"),
        "source_url": entry.get("source_url"),
        "kind": entry.get("kind"),
        "targets": entry.get("targets") or [],
        "score": entry.get("score"),
        "band": entry.get("band"),
        "band_en": entry.get("band_en"),
        "band_zh": entry.get("band_zh"),
        "confidence": entry.get("confidence"),
        "coverage": entry.get("coverage"),
        "dimension_coverage": entry.get("dimension_coverage"),
        "observed_at": entry.get("observed_at"),
        "limitations": entry.get("limitations") or [],
        "dimension_details": dimension_details,
    }


def dimension_bars(entry: dict, dimension_meta: list[dict], language: str) -> str:
    bars = []
    for dimension in dimension_meta:
        payload = (entry.get("dimensions") or {}).get(dimension["id"]) or {}
        label = dimension["zh"] if language == "zh" else dimension["en"]
        if payload.get("applicable") and payload.get("score") is not None:
            bucket = max(0, min(100, int(round(float(payload["score"]) / 5) * 5)))
            bars.append(f'<span class="quality-bar quality-v-{bucket}" '
                        f'title="{escape(label, quote=True)}: {payload["score"]}"></span>')
        else:
            bars.append(f'<span class="quality-bar is-empty" title="{escape(label, quote=True)}: '
                        f'{escape(values_for(language)["notApplicable"], quote=True)}"></span>')
    summary = ", ".join(
        f"{dimension['zh'] if language == 'zh' else dimension['en']} "
        f"{((entry.get('dimensions') or {}).get(dimension['id']) or {}).get('score')}"
        for dimension in dimension_meta
        if ((entry.get("dimensions") or {}).get(dimension["id"]) or {}).get("applicable")
    )
    return f'<div class="quality-bars" role="img" aria-label="{escape(summary, quote=True)}">' + "".join(bars) + "</div>"


def row(entry: dict, rank: int, links: dict, dimension_meta: list[dict], language: str) -> str:
    labels = values_for(language)
    name = entry.get("name") or entry["id"]
    link = links.get(entry["id"], {})
    name_zh = link.get("name_zh") or name
    display_name = name_zh if language == "zh" else name
    entry_url = link.get("entry_url_zh" if language == "zh" else "entry_url") or (entry.get("url") or "")
    score = entry.get("score")
    score_text = "—" if score is None else f"{score:.1f}"
    band = entry.get("band") or "ungraded"
    band_class = BAND_CLASS.get(band, "quality-band-ungraded")
    targets = " ".join(entry.get("targets") or [])
    return (
        f'<tr class="quality-row" data-id="{escape(entry["id"], quote=True)}" '
        f'data-score="{"" if score is None else score}" data-kind="{escape(entry.get("kind") or "", quote=True)}" '
        f'data-targets="{escape(targets, quote=True)}" data-band="{escape(band, quote=True)}" '
        f'data-confidence="{escape(entry.get("confidence") or "", quote=True)}" '
        f'data-coverage="{escape(str(entry.get("coverage") or 0), quote=True)}" '
        f'data-name="{escape(display_name, quote=True)}" data-name-zh="{escape(name_zh, quote=True)}" '
        f'data-url="{escape(entry.get("url") or "", quote=True)}">'
        f'<td class="quality-rank">{rank}</td>'
        f'<td class="quality-score-cell"><span class="quality-score {band_class}">{score_text}</span></td>'
        f'<td><button class="quality-name" type="button" data-quality-open="{escape(entry["id"], quote=True)}" '
        f'aria-label="{escape(labels["openEntry"] + ": " + display_name, quote=True)}">{escape(display_name)}</button>'
        f'<span class="quality-sub">{escape((entry.get("url") or "").split("//")[-1][:80])}</span></td>'
        f'<td class="quality-kind-cell">{" ".join(escape(part) for part in (entry.get("kind") or "").split("-"))}</td>'
        f'<td class="quality-meta-cell"><span class="quality-chips">'
        + "".join(f'<span class="quality-chip">{escape(target)}</span>' for target in entry.get("targets") or [])
        + f'</span></td>'
        f'<td class="quality-meta-cell">{escape(entry.get("confidence") or "")}</td>'
        f'<td class="quality-meta-cell">{float(entry.get("coverage") or 0):.1f}%</td>'
        f'<td class="quality-bars-cell">{dimension_bars(entry, dimension_meta, language)}</td>'
        f'<td class="quality-band-label">{escape(band_label(entry, language))}</td>'
        f'</tr>'
    )


def select_options(values: list[str], all_label: str, labels: dict | None = None) -> str:
    options = [f'<option value="">{escape(all_label)}</option>']
    for value in values:
        text = (labels or {}).get(value, value)
        options.append(f'<option value="{escape(value, quote=True)}">{escape(text)}</option>')
    return "".join(options)


def page_html(*, language: str, entries: list[dict], resources: list[dict], translations: dict,
              evaluations: dict, styles_href: str, quality_styles_href: str, quality_script_href: str,
              favicon_href: str, social_image_href: str, icon_stylesheet_href: str | None,
              repository_export: str) -> str:
    labels = values_for(language)
    zh = language == "zh"
    prefix = "/zh" if zh else ""
    canonical = f"{SITE_URL}{prefix}/quality/"
    alternate_en = f"{SITE_URL}/quality/"
    alternate_zh = f"{SITE_URL}/zh/quality/"
    dimension_meta = evaluations["meta"]["dimensions"]
    links = record_links(resources, translations)
    sorted_entries = sort_entries(entries)
    meta = evaluations["meta"]
    high_confidence = sum(1 for entry in entries if entry.get("confidence") == "high")
    median = meta.get("median_score")
    rows = "".join(row(entry, rank, links, dimension_meta, language)
                   for rank, entry in enumerate(sorted_entries, 1))
    kinds = sorted({entry.get("kind") for entry in entries if entry.get("kind")})
    targets = sorted({target for entry in entries for target in entry.get("targets") or []})
    bands = ["strong-evidence", "moderate-evidence", "limited-evidence", "minimal-evidence", "ungraded"]
    band_labels = {value: band_label({"band": value}, language) for value in bands}
    kind_labels = {value: " ".join(part.capitalize() for part in value.split("-")) for value in kinds}
    target_labels = {value: value.capitalize() for value in targets}
    limits = meta.get("limits") or []
    limits_html = "".join(f"<li>{escape(item)}</li>" for item in limits)
    other = "zh" if not zh else "en"
    other_href = f"{SITE_URL}/zh/quality/" if not zh else f"{SITE_URL}/quality/"
    title = f"{labels['title']} — AwesomeREA"
    description = labels["description"]
    structured = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "@id": canonical + "#page",
                "url": canonical,
                "name": labels["title"],
                "description": description,
                "inLanguage": "zh-CN" if zh else "en",
                "isPartOf": website_reference(SITE_URL),
            },
            {
                "@type": "BreadcrumbList",
                "@id": canonical + "#breadcrumb",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": labels["navHome"],
                     "item": {"@id": f"{SITE_URL}{prefix}/"}},
                    {"@type": "ListItem", "position": 2, "name": labels["breadcrumb"],
                     "item": {"@id": canonical}},
                ],
            },
            {
                "@type": "Dataset",
                "@id": canonical + "#dataset",
                "name": labels["title"],
                "description": description,
                "url": canonical,
                "creator": {"@type": "Organization", "name": "Awesome REA", "url": REPOSITORY_URL},
                "license": "https://opensource.org/license/mit",
                "temporalCoverage": meta.get("evidence_snapshot"),
                "variableMeasured": [dimension["en"] for dimension in dimension_meta],
                "distribution": {
                    "@type": "DataDownload",
                    "contentUrl": f"{SITE_URL}/quality/quality-data.json",
                    "encodingFormat": "application/json",
                },
            },
        ],
    }
    return f"""<!doctype html>
<html lang="{'zh-CN' if zh else 'en'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description, quote=True)}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="en" href="{alternate_en}">
<link rel="alternate" hreflang="zh-CN" href="{alternate_zh}">
<link rel="alternate" hreflang="x-default" href="{alternate_en}">
{THEME_COLOR_META}
<link rel="icon" href="{escape(favicon_href, quote=True)}" type="image/svg+xml">
<link rel="stylesheet" href="{escape(styles_href, quote=True)}">
<link rel="stylesheet" href="{escape(quality_styles_href, quote=True)}">
{'' if not icon_stylesheet_href else f'<link rel="stylesheet" href="{escape(icon_stylesheet_href, quote=True)}">'}
{open_graph_meta(language=language, title=labels['title'], description=description,
                 image_url=social_image_href, url=canonical)}
<script type="application/ld+json">{json_for_html(structured)}</script>
</head>
<body>
<header class="site-header"><div class="shell header-inner quality-header-inner">
  <a class="wordmark" href="{prefix}/" aria-label="{escape(labels['navHome'], quote=True)}"><img class="brand-mark" src="{escape(favicon_href, quote=True)}" alt="" width="33" height="33" aria-hidden="true"><span>Awesome<span class="wordmark-rea">REA</span><span class="wordmark-domain">.org</span></span></a>
  <nav class="header-nav" aria-label="Main navigation">
    <a class="quality-language" href="{other_href}" lang="{'zh-CN' if other == 'zh' else 'en'}" hreflang="{'zh-CN' if other == 'zh' else 'en'}">{escape(labels['otherLangName'])}</a>
    <a class="github-link" href="{REPOSITORY_URL}" target="_blank" rel="noopener"><span>GitHub</span></a>
    <a class="submit-link" href="{REPOSITORY_URL}/issues/new?template=resource.yml" target="_blank" rel="noopener">{escape(labels['submit'])}</a>
  </nav>
</div></header>
<main class="shell quality-main" data-quality-data="/quality/quality-data.json" data-quality-checks="/quality/checks/" data-labels="{escape(json_for_html({key: labels[key] for key in (
    'count', 'confidence', 'coverage', 'notApplicable', 'limits', 'loading',
    'detailUnavailable', 'openEntry', 'openSource', 'close', 'missingChecks')}), quote=True)}">
  <nav class="quality-breadcrumbs" aria-label="Breadcrumb"><a href="{prefix}/">{escape(labels['navHome'])}</a><span aria-hidden="true">/</span><span aria-current="page">{escape(labels['breadcrumb'])}</span></nav>
  <section class="quality-hero" aria-labelledby="quality-title">
    <p class="quality-kicker">{escape(labels['kicker'])}</p>
    <h1 id="quality-title">{escape(labels['title'])}</h1>
    <p>{escape(description)}</p>
    <ul class="quality-definition">
      <li><strong>{escape(labels['definitionOneTitle'])}</strong><span>{escape(labels['definitionOne'])}</span></li>
      <li><strong>{escape(labels['definitionTwoTitle'])}</strong><span>{escape(labels['definitionTwo'])}</span></li>
      <li><strong>{escape(labels['definitionThreeTitle'])}</strong><span>{escape(labels['definitionThree'])}</span></li>
    </ul>
    <div class="quality-stats">
      <div class="quality-stat"><strong>{len(entries)}</strong><span>{escape(labels['statEntries'])}</span></div>
      <div class="quality-stat"><strong>{meta.get('score_count', 0)}</strong><span>{escape(labels['statScored'])}</span></div>
      <div class="quality-stat"><strong>{'—' if median is None else f'{median:.1f}'}</strong><span>{escape(labels['statMedian'])}</span></div>
      <div class="quality-stat"><strong>{high_confidence}</strong><span>{escape(labels['statConfidence'])}</span></div>
    </div>
    <details class="quality-method">
      <summary>{escape(labels['methodTitle'])}</summary>
      <div><p>{escape(labels['methodBody'])}</p>
      <p><strong>{escape(labels['methodSnapshot'])}:</strong> {escape(str(meta.get('evidence_snapshot') or '—'))} · {escape(labels['methodSource'])}</p>
      <p><strong>{escape(labels['methodLimits'])}:</strong></p><ul>{limits_html}</ul>
      <p><a href="/quality/quality-data.json" download="awesomerea-quality-scores.json" type="application/json">{escape(labels['download'])}</a></p></div>
    </details>
  </section>
  <section aria-labelledby="quality-directory-title">
    <h2 class="quality-sr" id="quality-directory-title">{escape(labels['tableSoftware'])}</h2>
    <div class="quality-controls">
      <label class="quality-control quality-search">{escape(labels['controlsSearch'])}
        <input id="quality-search" type="search" autocomplete="off" placeholder="{escape(labels['controlsSearch'], quote=True)}">
      </label>
      <label class="quality-control">{escape(labels['controlsKind'])}
        <select id="quality-kind">{select_options(kinds, labels['all'], kind_labels)}</select>
      </label>
      <label class="quality-control">{escape(labels['controlsTarget'])}
        <select id="quality-target">{select_options(targets, labels['all'], target_labels)}</select>
      </label>
      <label class="quality-control">{escape(labels['controlsBand'])}
        <select id="quality-band">{select_options(bands, labels['all'], band_labels)}</select>
      </label>
      <label class="quality-control">{escape(labels['controlsConfidence'])}
        <select id="quality-confidence">{select_options(['high', 'medium', 'low', 'none'], labels['all'])}</select>
      </label>
      <label class="quality-control">{escape(labels['controlsSort'])}
        <select id="quality-sort">
          <option value="score-desc">{escape(labels['sortScoreDesc'])}</option>
          <option value="score-asc">{escape(labels['sortScoreAsc'])}</option>
          <option value="name">{escape(labels['sortName'])}</option>
          <option value="coverage">{escape(labels['sortCoverage'])}</option>
          <option value="confidence">{escape(labels['sortConfidence'])}</option>
        </select>
      </label>
      <p class="quality-count" id="quality-count" aria-live="polite">{escape(labels['count'])} {len(entries)} / {len(entries)}</p>
    </div>
    <noscript><p class="quality-note">{escape(labels['noscript'])}</p></noscript>
    <div class="quality-table-wrap">
      <table class="quality-table" id="quality-table">
        <thead><tr>
          <th scope="col" class="quality-rank">{escape(labels['tableRank'])}</th>
          <th scope="col" class="quality-score-cell">{escape(labels['tableScore'])}</th>
          <th scope="col">{escape(labels['tableSoftware'])}</th>
          <th scope="col" class="quality-kind-cell">{escape(labels['tableKind'])}</th>
          <th scope="col" class="quality-meta-cell">{escape(labels['tableTargets'])}</th>
          <th scope="col" class="quality-meta-cell">{escape(labels['tableConfidence'])}</th>
          <th scope="col" class="quality-meta-cell">{escape(labels['tableCoverage'])}</th>
          <th scope="col" class="quality-bars-cell">{escape(labels['tableDimensions'])}</th>
          <th scope="col">{escape(labels['tableBand'])}</th>
        </tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    <p class="quality-empty" id="quality-empty" hidden>{escape(labels['empty'])}</p>
    <p class="quality-note">{escape(labels['footerNote'])} <a href="/quality/quality-data.json" download="awesomerea-quality-scores.json" type="application/json">{escape(labels['download'])}</a></p>
  </section>
</main>
<div class="quality-detail-backdrop" id="quality-detail-backdrop" data-open="false"></div>
<aside class="quality-detail" id="quality-detail" data-open="false" role="dialog" aria-modal="true" aria-hidden="true" aria-labelledby="quality-detail-title">
  <div class="quality-detail-head"><h2 id="quality-detail-title">{escape(labels['detailTitle'])}</h2><button class="quality-detail-close" id="quality-detail-close" type="button" aria-label="{escape(labels['close'], quote=True)}">×</button></div>
  <div id="quality-detail-body"></div>
</aside>
<script src="{escape(quality_script_href, quote=True)}" defer></script>
{site_footer(language, note=escape(labels['footerNote']), repository_url=REPOSITORY_URL, repository_export=repository_export)}
</body>
</html>
"""


def build_quality_pages(output: Path, evaluations: dict, resources: list[dict], translations: dict, *,
                        styles_href: str, favicon_href: str, social_image_href: str,
                        icon_stylesheet_href: str | None, repository_export: str) -> list[str]:
    """Write both language pages and the compact data file; return sitemap URLs."""
    output = Path(output)
    quality_dir = output / "quality"
    quality_dir.mkdir(parents=True, exist_ok=True)
    quality_styles_href = fingerprinted_href(output, "quality.css")
    quality_script_href = fingerprinted_href(output, "quality.js")
    dimension_meta = evaluations["meta"]["dimensions"]
    links = record_links(resources, translations)
    check_labels = {}
    for entry in evaluations["entries"]:
        for payload in (entry.get("dimensions") or {}).values():
            for item in payload.get("checks") or []:
                check_labels[item["id"]] = item.get("label") or item["id"]
    compact = {
        "meta": {
            "generated_at": evaluations["meta"].get("generated_at"),
            "evidence_snapshot": evaluations["meta"].get("evidence_snapshot"),
            "entry_count": evaluations["meta"].get("entry_count"),
            "score_count": evaluations["meta"].get("score_count"),
            "median_score": evaluations["meta"].get("median_score"),
            "band_counts": evaluations["meta"].get("band_counts"),
            "confidence_counts": evaluations["meta"].get("confidence_counts"),
            "method": evaluations["meta"].get("method"),
            "limits": evaluations["meta"].get("limits"),
            "dimensions": dimension_meta,
            "check_labels": dict(sorted(check_labels.items())),
            "check_labels_zh": {key: CHECK_LABELS_ZH.get(key, key) for key in sorted(check_labels)},
        },
        "entries": [compact_entry(entry, links, dimension_meta) for entry in evaluations["entries"]],
    }
    (quality_dir / "quality-data.json").write_text(
        json.dumps(compact, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    checks_dir = quality_dir / "checks"
    checks_dir.mkdir(exist_ok=True)
    for entry in evaluations["entries"]:
        detail = compact_entry(entry, links, dimension_meta, include_checks=True)
        (checks_dir / f"{entry['id']}.json").write_text(
            json.dumps(detail, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    for language in ("en", "zh"):
        directory = output / ("zh" if language == "zh" else "") / "quality"
        directory.mkdir(parents=True, exist_ok=True)
        html = page_html(
            language=language, entries=evaluations["entries"], resources=resources,
            translations=translations, evaluations=compact,
            styles_href=styles_href, quality_styles_href=quality_styles_href,
            quality_script_href=quality_script_href, favicon_href=favicon_href,
            social_image_href=social_image_href, icon_stylesheet_href=icon_stylesheet_href,
            repository_export=repository_export,
        )
        (directory / "index.html").write_text(html, encoding="utf-8")
    return [f"{SITE_URL}/quality/", f"{SITE_URL}/zh/quality/"]


if __name__ == "__main__":
    raise SystemExit("Run this through scripts/build_site.py; it needs the generated catalog and assets.")
