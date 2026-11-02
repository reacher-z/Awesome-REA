/* Offline checks that paper search matches publication venues, case-insensitively, alongside the other fields. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const search = require("../site/paper-search.js");

const base = {title_zh: "示例", description_en: "Recovers types.", description_zh: "恢复类型。", authors: ["Ada Example"],
  doi: null, arxiv_id: null, year: 2026, publication_status: "conference-accepted", targets: ["binary"]};
const papers = [
  {...base, id: "paper-venue-only", title: "Type Recovery", venue: "ICLR 2026"},
  {...base, id: "paper-other-venue", title: "Layout Recovery", venue: "EMNLP 2025", targets: ["website"], year: 2025},
  {...base, id: "paper-no-venue", title: "Legacy Record Without Venue"}
];
const records = search.readRecords({schema_version: 1, papers});
const allowed = search.allowedValues(records);
const state = query => search.readState(new URLSearchParams(query), allowed);
const found = query => records.filter(paper => search.matches(paper, state(query))).map(paper => paper.id);

// The conference name appears only in the venue field.
for (const query of ["q=ICLR", "q=iclr", "q=IcLr+2026", "q=%EF%BC%A9%EF%BC%A3%EF%BC%AC%EF%BC%B2"]) {
  assert.deepEqual(found(query), ["paper-venue-only"], query);
}
assert.deepEqual(found("q=emnlp"), ["paper-other-venue"]);
// Venue terms combine with other fields and with the target, status and year filters.
assert.deepEqual(found("q=iclr+type"), ["paper-venue-only"]);
assert.deepEqual(found("q=iclr&target=website"), []);
assert.deepEqual(found("q=emnlp&target=website&status=conference-accepted&year=2025"), ["paper-other-venue"]);
assert.deepEqual(found("q=Legacy"), ["paper-no-venue"]);
assert.deepEqual(found("q=Ada&year=2026"), ["paper-venue-only", "paper-no-venue"]);
assert.throws(() => search.readRecords({schema_version: 1, papers: [{...papers[0], venue: ["ICLR"]}]}));

// Every catalog paper whose venue names ICLR or EMNLP is found by that name, in either letter case.
const root = path.resolve(__dirname, "..");
const catalog = JSON.parse(fs.readFileSync(path.join(root, "data/papers.json"), "utf8"));
const fields = ["id", "title", "title_zh", "description_en", "description_zh", "authors", "venue", "doi", "arxiv_id", "year", "publication_status", "targets"];
const projected = search.readRecords({schema_version: 1, papers: catalog.map(paper => Object.fromEntries(fields.map(key => [key, paper[key] ?? null])))});
const catalogAllowed = search.allowedValues(projected);
for (const name of ["ICLR", "EMNLP"]) {
  const expected = catalog.filter(paper => paper.venue.includes(name)).map(paper => paper.id);
  assert(expected.length > 0, name);
  for (const query of [name, name.toLowerCase()]) {
    const matched = projected.filter(paper => search.matches(paper, search.readState(new URLSearchParams({q: query}), catalogAllowed))).map(paper => paper.id);
    for (const id of expected) assert(matched.includes(id), `${query} misses ${id}`);
  }
}
console.log("paper venue search checks passed");
