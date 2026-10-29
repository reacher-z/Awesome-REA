/* Offline checks of the shipped paper-search module and DOM interactions. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const search = require("../site/paper-search.js");

const papers = [
  {id: "paper-game", title: "Game State Reconstruction", title_zh: "游戏状态重建", description_en: "Models observed transitions.", description_zh: "对已观察状态转移建模。", authors: ["Ada Example"], doi: "10.1234/game", arxiv_id: "2601.01234", year: 2026, publication_status: "preprint", targets: ["game", "website"]},
  {id: "paper-ui2code", title: "All Android Interfaces", title_zh: "全部安卓界面", description_en: "UI2code generates layout skeletons.", description_zh: "UI2code 根据截图生成布局骨架。", authors: ["Bo Researcher"], doi: "10.2345/app", arxiv_id: null, year: 2025, publication_status: "conference-accepted", targets: ["app"]},
  {id: "paper-published", title: "Protocol Formats", title_zh: "协议格式", description_en: "Infers communication fields.", description_zh: "推断通信报文字段。", authors: ["Chen Reviewer"], doi: null, arxiv_id: null, year: 2025, publication_status: "conference-paper", targets: ["protocol"]}
];
const records = search.readRecords({schema_version: 1, papers});
const allowed = search.allowedValues(records);
const state = query => search.readState(new URLSearchParams(query), allowed);
for (const query of ["reconstruction", "游戏状态", "Ada", "10.1234/game", "2601.01234"]) {
  assert.deepEqual(records.filter(paper => search.matches(paper, state("q=" + encodeURIComponent(query)))).map(paper => paper.id), ["paper-game"]);
}
for (const query of ["UI2code", "布局骨架"]) {
  assert.deepEqual(records.filter(paper => search.matches(paper, state("q=" + encodeURIComponent(query)))).map(paper => paper.id), ["paper-ui2code"]);
}
const identifierOnly = search.readRecords({schema_version: 1, papers: [{...papers[1], description_en: "Generated layout.", description_zh: "生成布局。"}]})[0];
assert(search.matches(identifierOnly, state("q=UI2code")));
const summaryOnly = search.readRecords({schema_version: 1, papers: [{...papers[1], id: "paper-summary"}]})[0];
assert(search.matches(summaryOnly, state("q=UI2code")));
assert(search.matches(records[0], state("target=website&status=preprint&year=2026&q=game")));
assert(!search.matches(records[0], state("target=website&status=conference-paper&year=2026")));
assert.deepEqual(records.filter(paper => search.matches(paper, state("status=conference-accepted"))).map(paper => paper.id), ["paper-ui2code"]);
assert.deepEqual(state("target=javascript:bad&status=published&year=2025.0"), {q: "", target: "all", status: "all", year: "all"});
assert.equal(state("q=" + "a".repeat(300)).q.length, 240);
assert.equal(search.stateURL("https://awesomerea.org/papers/?q=bad&q=duplicate&utm_source=fixture#paper-ui2code", state("q=all&year=2025")).href,
  "https://awesomerea.org/papers/?utm_source=fixture&q=all&year=2025#paper-ui2code");
for (const invalid of [{schema_version: 2, papers}, {schema_version: 1, papers: [...papers, papers[0]]}, {schema_version: 1, papers: [{...papers[0], targets: ["unknown"]}]}]) {
  assert.throws(() => search.readRecords(invalid));
}

class Element {
  constructor(dataset = {}) { this.dataset = dataset; this.hidden = false; this.value = ""; this.textContent = ""; this.handlers = {}; this.children = []; }
  addEventListener(type, callback) { this.handlers[type] = callback; }
  emit(type, extra = {}) { this.handlers[type]?.({target: this, preventDefault() {}, ...extra}); }
  querySelectorAll(selector) { return selector === "[data-paper-id]" ? this.children : []; }
  querySelector() { return this.label; }
  focus() { this.focused = true; }
}
function setup(lang = "en", query = "", invalidData = false) {
  const ids = new Map(["paper-search", "paper-search-data", "paper-query", "paper-target", "paper-status", "paper-year", "paper-results", "paper-empty", "paper-clear", "paper-empty-reset", "paper-more-filters"].map(id => [id, new Element()]));
  ids.get("paper-search-data").textContent = JSON.stringify({schema_version: invalidData ? 2 : 1, papers});
  const cards = papers.map(paper => new Element({paperId: paper.id}));
  const sections = papers.map((paper, i) => { const section = new Element({paperSection: paper.targets[0]}); section.children = [cards[i]]; section.label = new Element(); return section; });
  const topics = papers.map(paper => { const topic = new Element({paperTopic: paper.targets[0]}); topic.label = new Element(); return topic; });
  const language = new Element(); language.href = lang === "zh" ? "/papers/" : "/zh/papers/";
  const document = {documentElement: {lang: lang === "zh" ? "zh-CN" : "en"}, getElementById: id => ids.get(id),
    querySelector: selector => selector === ".papers-language" ? language : null,
    querySelectorAll: selector => ({"[data-paper-id]": cards, "[data-paper-section]": sections, "[data-paper-topic]": topics}[selector] || [])};
  const browser = {location: new URL("https://awesomerea.org" + (lang === "zh" ? "/zh/papers/" : "/papers/") + query), handlers: {}, calls: [],
    addEventListener(type, callback) { this.handlers[type] = callback; }};
  browser.history = Object.fromEntries(["replaceState", "pushState"].map(method => [method, (_, __, url) => { browser.location = new URL(url); browser.calls.push(method); }]));
  const initialized = search.initialize(document, browser);
  return {ids, cards, sections, topics, language, browser, initialized, visible: () => cards.filter(card => !card.hidden).map(card => card.dataset.paperId)};
}
for (const lang of ["en", "zh"]) {
  const app = setup(lang, "?target=website&year=2026#paper-game");
  assert(app.initialized); assert.equal(app.ids.get("paper-search").hidden, false);
  assert.deepEqual(app.visible(), ["paper-game"]);
  assert.equal(app.ids.get("paper-results").textContent, lang === "zh" ? "显示 1 / 3 篇论文" : "Showing 1 of 3 papers");
  assert.equal(new URL(app.language.href).hash, "#paper-game");
  assert.equal(new URL(app.language.href).searchParams.get("target"), "website");
  app.browser.location.hash = "#research-game";
  app.language.emit("click", {preventDefault() { throw new Error("Language link must navigate normally"); }});
  assert.equal(new URL(app.language.href).hash, "#research-game");
  assert.equal(new URL(app.language.href).searchParams.get("target"), "website");
  assert.equal(new URL(app.language.href).searchParams.get("year"), "2026");
  assert.equal(new URL(app.language.href).pathname, lang === "zh" ? "/papers/" : "/zh/papers/");
  app.ids.get("paper-clear").emit("click"); assert.equal(app.visible().length, 3); assert(app.ids.get("paper-query").focused);
  const input = app.ids.get("paper-query"); const before = app.browser.location.href;
  input.emit("compositionstart"); input.value = "游戏"; input.emit("input", {isComposing: true});
  assert.equal(app.visible().length, 3); assert.equal(app.browser.location.href, before);
  input.emit("compositionend"); assert.deepEqual(app.visible(), ["paper-game"]);
  input.value = "no matching paper"; input.emit("input"); assert.equal(app.visible().length, 0); assert.equal(app.ids.get("paper-empty").hidden, false);
  assert(app.sections.every(section => section.hidden)); assert(app.topics.every(topic => topic.hidden));
  app.ids.get("paper-empty-reset").emit("click"); assert.equal(app.visible().length, 3); assert.equal(app.ids.get("paper-empty").hidden, true);
  assert(app.sections.every(section => !section.hidden));
  app.ids.get("paper-status").value = "conference-accepted"; app.ids.get("paper-status").emit("change");
  assert.deepEqual(app.visible(), ["paper-ui2code"]); assert.equal(app.browser.calls.at(-1), "pushState");
  app.browser.location = new URL("https://awesomerea.org/papers/?q=protocol"); app.browser.handlers.popstate();
  assert.deepEqual(app.visible(), ["paper-published"]); assert.equal(app.ids.get("paper-status").value, "all");
}
const invalid = setup("en", "?status=bad&year=0&target=bad");
assert.equal(invalid.browser.location.search, ""); assert.equal(invalid.visible().length, 3);
const broken = setup("en", "?q=no-match", true);
// The form is visible in the HTML; a failed index check hides it so no inert controls remain.
assert.equal(broken.initialized, false); assert.equal(broken.ids.get("paper-search").hidden, true); assert.equal(broken.visible().length, 3);
const canonical = search.readRecords({schema_version: 1, papers: JSON.parse(fs.readFileSync(path.join(__dirname, "../data/papers.json"), "utf8"))});
const canonicalAllowed = search.allowedValues(canonical);
for (const [query, id] of [["UI2code", "paper-ui2code"], ["ReDraw", "paper-redraw"], ["布局骨架", "paper-ui2code"]]) {
  const current = search.readState(new URLSearchParams({q: query}), canonicalAllowed);
  assert(canonical.filter(paper => search.matches(paper, current)).some(paper => paper.id === id), query);
}

// Direct links must expose active advanced filters in either language.
for (const lang of ["en", "zh"]) {
  assert(!setup(lang).ids.get("paper-more-filters").open);
  for (const query of ["?year=2025", "?status=preprint", "?layout=cards"]) {
    assert.equal(setup(lang, query).ids.get("paper-more-filters").open, true);
  }
  assert(!setup(lang, "?year=invalid&status=invalid").ids.get("paper-more-filters").open);
}

// Static compact layout preserves native disclosures; the card option moves only scope, without copies.
class Node {
  constructor(name, children = []) { this.name = name; this.children = []; this.parentNode = null; this.dataset = {}; this.handlers = {}; this.value = ""; for (const child of children) this.appendChild(child); }
  appendChild(child) { child.parentNode?.removeChild(child); child.parentNode = this; this.children.push(child); return child; }
  removeChild(child) { this.children.splice(this.children.indexOf(child), 1); child.parentNode = null; }
  insertBefore(child, next) { if (child === next) return child; if (!next) return this.appendChild(child); child.parentNode?.removeChild(child); child.parentNode = this; this.children.splice(this.children.indexOf(next), 0, child); return child; }
  after(child) { const parent = this.parentNode; const next = parent.children[parent.children.indexOf(this) + 1]; parent.insertBefore(child, next || null); }
  get nextSibling() { return this.parentNode ? this.parentNode.children[this.parentNode.children.indexOf(this) + 1] || null : null; }
  all() { return this.children.flatMap(child => [child, ...child.all()]); }
  querySelector(selector) { return this.all().find(node => selector === ".paper-details > summary" ? node.name === "summary" && node.parentNode.name === "details" : node.name === ({".paper-scope": "scope", ".paper-links": "links"}[selector])) || null; }
  querySelectorAll(selector) { return selector === ".paper-authors, .paper-scope" ? this.all().filter(node => ["authors", "scope"].includes(node.name)) : []; }
  addEventListener(type, callback) { this.handlers[type] = callback; }
}
function layoutCard() {
  return new Node("article", [new Node("header", [new Node("h3"), new Node("meta")]), new Node("description"), new Node("links"), new Node("details", [new Node("summary"), new Node("scope"), new Node("authors"), new Node("why")])]);
}
const shape = card => card.children.map(child => child.children.length ? child.name + "(" + child.children.map(item => item.name).join(",") + ")" : child.name).join(" ");
const cardsShape = "header(h3,meta) description scope links details(summary,authors,why)";
const compactShape = "header(h3,meta) description links details(summary,scope,authors,why)";
for (const query of ["?layout=compact&q=game#paper-game", "?layout=cards&q=game#paper-game", "", "?layout=bogus"]) {
  const layoutCards = [layoutCard(), layoutCard()];
  const control = new Node("select");
  const document = {documentElement: {dataset: {}}, getElementById: id => id === "paper-layout" ? control : null};
  const browser = {location: new URL("https://awesomerea.org/papers/" + query), history: {replaceState(_, __, url) { browser.location = new URL(url); }}};
  let changes = 0;
  const apply = search.initializeLayout(document, browser, layoutCards, () => { changes++; });
  const compact = !query.includes("layout=cards");
  assert.equal(document.documentElement.dataset.paperLayout, compact ? "compact" : "cards");
  assert.equal(control.value, compact ? "compact" : "cards");
  assert(layoutCards.every(card => shape(card) === (compact ? compactShape : cardsShape)), shape(layoutCards[0]));
  control.value = compact ? "cards" : "compact"; control.handlers.change();
  assert.equal(changes, 1);
  assert(layoutCards.every(card => shape(card) === (compact ? cardsShape : compactShape)), shape(layoutCards[0]));
  assert.equal(browser.location.searchParams.get("layout"), compact ? "cards" : null);
  assert.equal(browser.location.searchParams.get("q"), query.includes("q=game") ? "game" : null);
  assert.equal(browser.location.hash, query.includes("#paper-game") ? "#paper-game" : "");
  apply("compact"); apply("compact"); apply("cards");
  assert(layoutCards.every(card => shape(card) === cardsShape));
}
assert.equal(search.initializeLayout({getElementById: () => null}, {}, [], () => {}), null);
assert.deepEqual(["?layout=compact", "?layout=cards", "?layout=x", ""].map(query => search.readLayout(new URLSearchParams(query))), ["compact", "cards", "compact", "compact"]);
// Filter URLs, and so the language link, keep the chosen layout.
assert.equal(search.stateURL("https://awesomerea.org/papers/?layout=compact&q=old#paper-game", state("year=2025")).href, "https://awesomerea.org/papers/?layout=compact&year=2025#paper-game");
console.log("Paper search: bilingual matching, facets, URLs, IME, history, reset, layout and static fallback passed.");
