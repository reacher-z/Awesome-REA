/* Open card details survive re-rendering without relying on :has() selector support. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const script = fs.readFileSync(path.join(root, 'site/app.js'), 'utf8');

class Element {
  constructor(tag = 'div') { this.tag = tag; this.children = []; this.dataset = {}; this.attrs = {}; this.handlers = {}; this.value = ''; this.className = ''; this.open = false; this.classList = {toggle() {}, add() {}, remove() {}}; }
  append(...nodes) { for (const node of nodes) this.children.push(...(node.tag === 'fragment' ? node.children : [node])); }
  replaceChildren(...nodes) { this.children = []; this.append(...nodes); }
  setAttribute(key, value) { this.attrs[key] = value; }
  addEventListener(event, callback) { this.handlers[event] = callback; }
  emit(event) { this.handlers[event]?.({target: this}); }
  get options() { return this.children; }
  // Only the descendant selectors used for expanded details are needed here.
  querySelector(selector) {
    if (this.broken && selector === 'details') throw new Error('Detail lookup failed');
    const wanted = {'details': node => node.tag === 'details', 'details[open]': node => node.tag === 'details' && node.open}[selector];
    assert(wanted, 'Unexpected card selector ' + selector);
    const visit = node => { for (const child of node.children) { if (wanted(child)) return child; const found = visit(child); if (found) return found; } return null; };
    return visit(this);
  }
  focus() {}
  scrollIntoView() {}
}

function setup({brokenDetails = false} = {}) {
  const elements = new Map();
  const element = selector => { if (!elements.has(selector)) elements.set(selector, new Element()); return elements.get(selector); };
  const cards = (container, className) => element(container).children.filter(node => node.className === className)
    .map(node => { node.broken = brokenDetails; return node; });
  const document = {baseURI: 'https://awesomerea.org/', documentElement: {dataset: {}}, activeElement: {tagName: 'BODY'},
    querySelector: element,
    querySelectorAll(selector) {
      // Engines without :has() reject the whole selector list with a SyntaxError.
      if (selector.includes(':has(')) throw new SyntaxError(`'${selector}' is not a valid selector`);
      if (selector === '.resource-card') return cards('#resource-grid', 'resource-card');
      if (selector === '.source-card') return cards('#source-results', 'source-card');
      return [];
    }, createElement: tag => new Element(tag), createElementNS: (_, tag) => new Element(tag),
    createDocumentFragment: () => new Element('fragment'), addEventListener() {}};
  const rows = Array.from({length: 30}, (_, index) => ({id: 'fixture-' + index, name: 'Fixture ' + index, name_zh: '测试 ' + index,
    full_name: 'Fixture/project' + index, url: 'https://github.com/Fixture/project' + index,
    evidence_url: 'https://github.com/Fixture/project' + index, description_en: 'Fixture ' + index, description_zh: '测试 ' + index,
    targets: ['app'], topics: ['apps'], category: 'dynamic-analysis', group: 'tools', kind: 'tool', relationship: 'foundation',
    requirements: ['A fixture'], requirements_zh: ['测试条件'], verified_at: '2026-01-01', scan_status: 'readme-scanned', stars: index}));
  const browser = {meta: {schema_version: 1, status: 'complete', full_export: 'source-index.json', full_export_sha256: 'a'.repeat(64),
    scope: {scanned_count: rows.length, excluded_count: 0, browse_count: rows.length}}, resources: rows};
  const location = new URL('https://awesomerea.org/?view=curated');
  location.assign = () => {};
  const context = {document, location, URL, URLSearchParams, console, window: {addEventListener() {}},
    history: {replaceState(_, __, next) { location.href = String(next); location.search = new URL(next).search; }},
    fetch: async url => ({ok: true, json: async () => /^\/catalog(-index)?\.json$/.test(new URL(url).pathname) ? {resources: rows, meta: {repository_url: 'https://github.com/reacher-z/Awesome-REA', source_index: {resource_count: rows.length}}} : browser})};
  vm.createContext(context);
  vm.runInContext(script.replace('applyLanguage(); load();', '') + '\nglobalThis.audit = {state,sourceState,load,loadSources,applyLanguage,setIndexMode};', context);
  return {api: context.audit, element};
}
const details = card => card.children.find(child => child.tag === 'details');
const shown = (app, container) => app.element(container).children;
const byId = (app, container, id) => shown(app, container).find(card => card.dataset.recordId === id);

(async () => {
  const app = setup();
  await app.api.load();
  assert.equal(app.api.state.error, false, 'Rejected :has() selectors must not switch to the load error');
  assert.equal(app.element('#error-state').hidden, true);
  assert.equal(shown(app, '#resource-grid').length, 15);
  assert.equal(app.element('#mode-sources').hidden, false, 'The Repositories tab appears after curated cards render');

  details(byId(app, '#resource-grid', 'fixture-3')).open = true;
  const search = app.element('#search-input'); search.value = 'fixture'; search.emit('input');
  assert.equal(details(byId(app, '#resource-grid', 'fixture-3')).open, true, 'Filtering keeps curated details open');
  app.api.state.lang = 'zh'; app.api.applyLanguage();
  assert.equal(details(byId(app, '#resource-grid', 'fixture-3')).open, true, 'Changing language keeps curated details open');
  const layout = app.element('#layout-select'); layout.value = 'cards'; layout.emit('change');
  assert.equal(details(byId(app, '#resource-grid', 'fixture-3')).open, true, 'Changing layout keeps curated details open');
  app.element('#load-more').emit('click');
  assert.equal(shown(app, '#resource-grid').length, 30);
  assert.equal(details(byId(app, '#resource-grid', 'fixture-3')).open, true, 'Show More keeps curated details open');
  assert.equal(shown(app, '#resource-grid').filter(card => details(card).open).length, 1);

  await app.api.loadSources(); app.api.setIndexMode('source-index');
  assert.equal(app.api.sourceState.error, false);
  assert.equal(shown(app, '#source-results').length, 24);
  details(byId(app, '#source-results', 'fixture-25')).open = true;
  const sourceSearch = app.element('#source-search'); sourceSearch.value = '2'; sourceSearch.emit('input');
  assert.equal(shown(app, '#source-results').length, 12);
  assert.equal(details(byId(app, '#source-results', 'fixture-25')).open, true, 'Filtering keeps repository details open');
  sourceSearch.value = ''; sourceSearch.emit('input');
  app.api.state.lang = 'en'; app.api.applyLanguage();
  assert.equal(details(byId(app, '#source-results', 'fixture-25')).open, true, 'Changing language keeps repository details open');
  app.element('#source-more').emit('click');
  assert.equal(shown(app, '#source-results').length, 30);
  assert.equal(details(byId(app, '#source-results', 'fixture-25')).open, true, 'Show More keeps repository details open');
  assert.equal(shown(app, '#source-results').filter(card => details(card).open).length, 1);

  // Restoring fails after open details were found; reloading must still render instead of reporting a load error.
  const broken = setup({brokenDetails: true});
  await broken.api.load();
  details(byId(broken, '#resource-grid', 'fixture-2')).open = true;
  await broken.api.load();
  assert.equal(broken.api.state.error, false, 'A failed details restore must not switch to the load error');
  assert.equal(broken.element('#error-state').hidden, true);
  assert.equal(shown(broken, '#resource-grid').length, 15);
  assert.equal(broken.element('#mode-sources').hidden, false);
  await broken.api.loadSources(); broken.api.setIndexMode('source-index');
  details(byId(broken, '#source-results', 'fixture-29')).open = true;
  broken.api.applyLanguage();
  assert.equal(broken.api.sourceState.error, false);
  assert.equal(shown(broken, '#source-results').length, 24);
  process.stdout.write('Expanded details fallback passed\n');
})().catch(error => { console.error(error); process.exitCode = 1; });
