const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const script = fs.readFileSync("site/app.js", "utf8");
function section(start, end) {
  const a = script.indexOf(start), b = script.indexOf(end, a);
  assert(a >= 0 && b > a);
  return script.slice(a, b);
}
const nodes = new Map();
const context = {
  state: {lang: "en"},
  sourceState: {
    loaded: true, records: [], meta: {}, topic: "", topicIDs: new Set(),
    q: "", sort: "relevance", target: "all", visible: 24,
  },
  document: {createDocumentFragment: () => ({append() {}})},
  expandedRecords: () => new Set(), restoreExpanded() {}, sourceCard: () => ({}),
  // renderSources also reveals the filtered-export button; tests/filtered_export_ui.cjs covers that.
  showExport() {},
  sourceFiltered: () => context.sourceState.records,
  sourceTime: value => value, dataURL: filename => "/" + filename + "?v=test",
  t: key => ({
    downloadPublishedSourceData: context.state.lang === "zh" ? "已发布仓库索引 JSON ↓" : "Published repository index JSON ↓",
    downloadSourceData: context.state.lang === "zh" ? "仓库索引 JSON ↓" : "Repository index JSON ↓",
  }[key] || key),
  $: selector => {
    if (!nodes.has(selector)) nodes.set(selector, {
      dataset: {}, hidden: false, textContent: "", href: "",
      replaceChildren() {}, setAttribute() {}, classList: {toggle() {}},
    });
    return nodes.get(selector);
  },
  $$: () => [],
};
vm.createContext(context);
vm.runInContext(section("function sourceBrowserPayload(", "\nasync function loadSources")
  + section("function sourceDownload(", "\nfunction setIndexMode")
  + section("function renderSources(", "\nfunction sourceBrowserPayload")
  + "\nglobalThis.api = {sourceBrowserPayload,sourceDownload,renderSources};", context);

const row = {id: "scan-1", full_name: "Example/repository", scan_status: "readme-scanned"};
const scope = {scanned_count: 1, excluded_count: 0, browse_count: 1};
const published = {meta: {
  schema_version: 2, kind: "published-repository-selection", status: "published-selection",
  published_at: "2026-10-20T00:00:00Z", scope,
  full_export: "source-published.json", full_export_sha256: "a".repeat(64),
}, resources: [row]};
const legacy = {meta: {
  schema_version: 1, status: "complete", completed_at: "2026-10-16T00:00:00Z", scope,
  full_export: "source-index.json", full_export_sha256: "b".repeat(64),
}, resources: [row]};
assert.equal(context.api.sourceBrowserPayload(published), published);
assert.equal(context.api.sourceBrowserPayload(legacy), legacy);
for (const mutate of [
  data => { data.meta.schema_version = 1; },
  data => { data.meta.full_export = "source-index.json"; },
  data => { data.meta.full_export = "https://example.com/data.json"; },
  data => { data.meta.status = "complete"; },
  data => { data.meta.completed_at = data.meta.published_at; },
  data => { data.meta.published_at = "2026-10-20"; },
  data => { data.meta.published_at = "2026-10-20T00:00:00+0000"; },
  data => { data.meta.published_at = "2026-10-20T00:30:00+01:00"; },
  data => { data.meta.scope.browse_count = true; },
  data => { data.meta.scope.browse_count = 500; },
]) {
  const changed = JSON.parse(JSON.stringify(published));
  mutate(changed);
  assert.throws(() => context.api.sourceBrowserPayload(changed));
}
const wrongLegacy = JSON.parse(JSON.stringify(legacy));
wrongLegacy.meta.full_export = "source-published.json";
assert.throws(() => context.api.sourceBrowserPayload(wrongLegacy));
assert.throws(() => context.api.sourceDownload("../../private.json"));
context.api.sourceDownload("source-published.json");
assert.equal(nodes.get("#download-source-index").href, "/source-published.json?v=test");
assert.match(nodes.get("#download-source-index").textContent, /Published/);
context.sourceState.records = [row];
context.sourceState.meta = published.meta;
context.api.renderSources();
assert.match(nodes.get("#source-snapshot").textContent, /Selection published/);
assert.doesNotMatch(nodes.get("#source-snapshot").textContent, /Scan completed/);
context.state.lang = "zh";
context.api.sourceDownload("source-published.json");
context.api.renderSources();
assert.match(nodes.get("#download-source-index").textContent, /已发布/);
assert.match(nodes.get("#source-snapshot").textContent, /选集发布于/);
assert.doesNotMatch(nodes.get("#source-snapshot").textContent, /扫描完成于/);
context.state.lang = "en";
context.sourceState.meta = legacy.meta;
context.api.sourceDownload("source-index.json");
context.api.renderSources();
assert.match(nodes.get("#source-snapshot").textContent, /Scan completed/);
assert.equal(nodes.get("#download-source-index").href, "/source-index.json?v=test");
console.log("Public-source browser schema1/schema2 and publication-time tests passed");
