/* Exercise actual browser functions with offline payloads and a minimal DOM. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'site/index.html'), 'utf8');
const script = fs.readFileSync(path.join(root, 'site/app.js'), 'utf8');

class Element {
  constructor(tag = 'div') { this.tag = tag; this.children = []; this.dataset = {}; this.attrs = {}; this.handlers = {}; this.value = ''; this.className = ''; this.classList = {toggle() {}, add() {}, remove() {}}; }
  append(...nodes) { for (const node of nodes) this.children.push(...(node.tag === 'fragment' ? node.children : [node])); }
  replaceChildren(...nodes) { this.children = []; this.append(...nodes); }
  setAttribute(key, value) { this.attrs[key] = value; }
  addEventListener(event, callback) { this.handlers[event] = callback; }
  emit(event) { this.handlers[event]?.({target: this}); }
  get options() { return this.children; }
  focus() {}
  scrollIntoView() {}
}
function setup(query, {curatedProtocol = true, sourceProtocol = true, pathname = "/", records} = {}) {
  const elements = new Map();
  const buttons = [...html.matchAll(/<button[^>]+data-(source-target|target)="([^"]+)"[^>]*>/g)].map(match => {
    const node = new Element('button');
    node.dataset[match[1] === 'source-target' ? 'sourceTarget' : 'target'] = match[2];
    node.hidden = /\bhidden\b/.test(match[0]);
    return node;
  });
  const repositoryLinks = [...html.matchAll(/<a[^>]+data-repo-path="([^"]*)"[^>]*>/g)].map(match => {
    const node = new Element('a'); node.dataset.repoPath = match[1]; return node;
  });
  const protocolLabels = [new Element('span'), new Element('span')];
  protocolLabels.forEach(node => node.dataset.i18n = 'targetProtocol');
  const document = {baseURI: 'https://awesomerea.org/', documentElement: {dataset: {}}, activeElement: {tagName: 'BODY'},
    querySelector(selector) {
      if (selector === '[data-target="protocol"]') return buttons.find(node => node.dataset.target === 'protocol');
      if (selector === '[data-source-target="protocol"]') return buttons.find(node => node.dataset.sourceTarget === 'protocol');
      if (!elements.has(selector)) elements.set(selector, new Element()); return elements.get(selector); },
    querySelectorAll(selector) {
      if (selector === '[data-target]') return buttons.filter(node => node.dataset.target);
      if (selector === '[data-source-target]') return buttons.filter(node => node.dataset.sourceTarget);
      if (selector === '[data-i18n]') return protocolLabels;
      if (selector === '[data-repo-path]') return repositoryLinks;
      return [];
    }, createElement: tag => new Element(tag), createElementNS: (_, tag) => new Element(tag),
    createDocumentFragment: () => new Element('fragment'), addEventListener() {}};
  const rows = records || ['protocol', 'app'].map((target, index) => ({id: 'fixture-' + index, name: 'Fixture ' + index, name_zh: '测试 ' + index,
    full_name: 'Fixture/project' + index, url: 'https://github.com/Fixture/project' + index,
    evidence_url: 'https://github.com/Fixture/project' + index, description_en: '', description_zh: '',
    targets: [target], topics: index === 0 ? ["protocol-analysis", "fixtures"] : ["apps"], category: 'dynamic-analysis', group: 'tools', kind: 'tool', relationship: 'foundation',
    requirements: ['A fixture'], requirements_zh: ['测试条件'], verified_at: '2026-01-01', scan_status: 'readme-scanned', stars: index}));
  const browser = {meta: {schema_version: 1, status: 'complete', full_export: 'source-index.json', full_export_sha256: 'a'.repeat(64),
    scope: {scanned_count: rows.length, excluded_count: 0, browse_count: rows.length}}, resources: rows.map((row, i) => ({...row, targets: !i && !sourceProtocol ? ['app'] : row.targets}))};
  const curatedRows = rows.map((row, i) => ({...row, targets: !i && !curatedProtocol ? ['app'] : row.targets}));
  const location = new URL('https://awesomerea.org' + pathname + query);
  const requests = [];
  location.assign = next => { location.lastNavigation = String(next); };
  const context = {document, location, URL, URLSearchParams, console,
    history: {replaceState(_, __, next) { location.href = String(next); location.search = new URL(next).search; }},
    fetch: async url => { requests.push(String(url)); return {ok: true, json: async () => new URL(url).pathname.endsWith('catalog.json') ? {resources: curatedRows, meta: {repository_url: 'https://github.com/reacher-z/Awesome-REA', source_index: {resource_count: rows.length}}} : browser}; }};
  vm.createContext(context);
  vm.runInContext(script.replace('applyLanguage(); load();', '') + '\nglobalThis.audit = {state,sourceState,load,loadSources,filtered,sourceFiltered,applyLanguage,reset,resetSources,setIndexMode,sourceRelatedEntries};', context);
  return {api: context.audit, context, elements, buttons, protocolLabels, repositoryLinks, requests};
}
(async () => {
  for (const lang of ['en', 'zh']) {
    const app = setup(`?view=curated&target=protocol&source-target=protocol&lang=${lang}`);
    await app.api.load();
    await app.api.loadSources();
    assert.equal(app.api.state.error, false);
    assert.equal(app.api.sourceState.error, false);
    assert.equal(app.api.state.target, 'protocol');
    assert.equal(app.api.sourceState.target, 'protocol');
    app.api.applyLanguage();
    assert(app.protocolLabels.every(node => node.innerHTML === (lang === 'zh' ? '协议' : 'Protocol')));
    for (const query of ['protocol', '协议']) {
      app.api.state.q = query; app.api.sourceState.q = query;
      assert.equal(app.api.filtered().length, 1);
      assert.equal(app.api.sourceFiltered().length, 1);
    }
    app.api.state.q = ''; app.api.sourceState.q = '';
    app.api.sourceState.visible = 96;
    const sourceButton = app.buttons.find(node => node.dataset.sourceTarget === 'protocol');
    app.api.setIndexMode('source-index'); sourceButton.emit('click');
    assert.equal(app.api.sourceState.visible, 24);
    assert.equal(sourceButton.attrs['aria-pressed'], 'true');
    assert.equal(new URL(app.context.location.href).searchParams.get('source-target'), 'protocol');
    app.api.resetSources();
    assert.equal(app.api.sourceState.target, 'all');
    assert.equal(new URL(app.context.location.href).searchParams.has('source-target'), false);
    app.api.setIndexMode('curated'); app.api.state.visible = 45;
    app.buttons.find(node => node.dataset.target === 'protocol').emit('click');
    assert.equal(app.api.state.visible, 15);
    assert.equal(new URL(app.context.location.href).searchParams.get('target'), 'protocol');
    app.api.reset();
    assert.equal(app.api.state.target, 'all');
    assert.equal(new URL(app.context.location.href).searchParams.has('target'), false);
    app.api.state.q = '应用'; app.api.sourceState.q = '应用';
    assert.equal(app.api.filtered()[0].targets[0], 'app');
    assert.equal(app.api.sourceFiltered()[0].targets[0], 'app');
  }
  for (const [curatedProtocol, sourceProtocol] of [[false, false], [true, false], [false, true]]) {
    const app = setup('?view=curated&target=protocol&source-target=protocol', {curatedProtocol, sourceProtocol});
    await app.api.load(); await app.api.loadSources();
    const curatedButton = app.buttons.find(node => node.dataset.target === 'protocol');
    const sourceButton = app.buttons.find(node => node.dataset.sourceTarget === 'protocol');
    assert.equal(curatedButton.hidden, !curatedProtocol);
    assert.equal(sourceButton.hidden, !sourceProtocol);
    assert.equal(app.api.state.target, 'protocol');
    assert.equal(app.api.sourceState.target, 'protocol');
    app.api.state.q = 'no matching fixture'; app.api.sourceState.q = 'no matching fixture';
    app.api.applyLanguage();
    assert.equal(app.api.filtered().length, 0);
    assert.equal(app.api.sourceFiltered().length, 0);
    assert.equal(curatedButton.hidden, !curatedProtocol);
    assert.equal(sourceButton.hidden, !sourceProtocol);
    assert.equal(app.elements.get('#clear-filters').hidden, false);
    assert.equal(app.elements.get('#source-clear').hidden, false);
  }
  const chinese = setup('?view=curated&target=protocol#catalog', {pathname: '/zh/'});
  await chinese.api.load();
  assert.equal(chinese.api.state.lang, 'zh');
  assert(chinese.requests.every(url => !new URL(url).pathname.startsWith('/zh/')));
  const picker = chinese.elements.get('#language-select');
  picker.value = 'en'; picker.emit('change');
  const switched = new URL(chinese.context.location.lastNavigation);
  assert.equal(switched.pathname, '/');
  assert.equal(switched.searchParams.get('target'), 'protocol');
  assert.equal(switched.hash, '#catalog');
  assert.equal(switched.searchParams.has('lang'), false);
  const home = setup(''); await home.api.load();
  assert.equal(home.api.state.lang, 'en');
  // Chinese views link the Chinese contribution guide; other repository links keep their paths.
  const contribution = app => app.repositoryLinks.filter(node => node.href.includes('/CONTRIBUTING')).map(node => node.href);
  assert.deepEqual(contribution(home), ['https://github.com/reacher-z/Awesome-REA/blob/main/CONTRIBUTING.md']);
  const legacyChinese = setup('?lang=zh'); await legacyChinese.api.load();
  for (const app of [chinese, legacyChinese]) {
    assert.deepEqual(contribution(app), ['https://github.com/reacher-z/Awesome-REA/blob/main/CONTRIBUTING.zh-CN.md']);
    assert(app.repositoryLinks.some(node => node.href === 'https://github.com/reacher-z/Awesome-REA/blob/main/data/README.md'));
  }
  assert.equal(home.api.sourceState.mode, 'curated');
  for (const lang of ['en', 'zh']) {
    const linked = setup(`?lang=${lang}`); await linked.api.load();
    const card = linked.elements.get('#resource-grid').children[0];
    const details = card.children.find(child => child.className === 'requirements');
    assert(!details.open); // The full entry is available without expanding requirements.
    const metadata = card.children.find(child => child.className === 'card-meta');
    const entry = metadata.children.find(child => child.className === 'resource-entry-link');
    assert.equal(entry.href, `${lang === 'zh' ? '/zh' : ''}/resources/fixture-0/`);
    assert.equal(entry.target, undefined); // Navigation stays on the collection website.
    assert(entry.attrs['aria-label'].includes(lang === 'zh' ? '测试 0' : 'Fixture 0'));
  }
  const direct = {kind: 'paper', id: 'paper-fixture', title_en: 'Paper', title_zh: '论文',
    href_en: '/papers/paper-fixture/', href_zh: '/zh/papers/paper-fixture/'};
  const legacy = {...direct, href_en: '/papers/#paper-fixture', href_zh: '/zh/papers/#paper-fixture'};
  const accepts = row => home.api.sourceRelatedEntries({related_entries: [row]}).length;
  assert.equal(accepts(direct), 1); assert.equal(accepts(legacy), 1);
  for (const bad of [{...direct, href_en: 'https://example.com/'}, {...direct, id: '../fixture'},
    {...direct, href_en: '/papers/wrong-id/'}, {...direct, href_zh: '/papers/paper-fixture/'},
    {...direct, id: 'fixture', href_en: null, href_zh: null}]) {
    assert.equal(accepts(bad), 0);
  }
  const layouts = setup('?view=curated&sourceq=fixture&target=protocol&layout=cards#catalog');
  await layouts.api.load(); await layouts.api.loadSources(); layouts.api.setIndexMode("source-index"); layouts.api.applyLanguage();
  assert.equal(layouts.context.document.documentElement.dataset.layout, 'cards');
  const recordsBefore = layouts.api.state.records;
  const sourceRowsBefore = layouts.elements.get('#source-results').children;
  const layoutControl = layouts.elements.get('#layout-select');
  layoutControl.value = 'compact'; layoutControl.emit('change');
  assert.equal(layouts.context.document.documentElement.dataset.layout, 'compact');
  assert.strictEqual(layouts.api.state.records, recordsBefore);
  assert.strictEqual(layouts.elements.get('#source-results').children, sourceRowsBefore);
  let shared = new URL(layouts.context.location.href);
  assert.equal(shared.searchParams.get('sourceq'), 'fixture');
  assert.equal(shared.searchParams.get('view'), 'source-index');
  assert.equal(shared.searchParams.get('target'), 'protocol');
  assert.equal(shared.hash, '#catalog');
  assert.equal(shared.searchParams.has('layout'), false);
  layoutControl.value = 'cards'; layoutControl.emit('change');
  assert.equal(new URL(layouts.context.location.href).searchParams.get('layout'), 'cards');
  const sourceCard = layouts.elements.get('#source-results').children[0];
  const scanDetails = sourceCard.children.find(child => child.className === 'source-record-details');
  const compactContext = scanDetails.children.find(child => child.className === 'source-compact-context');
  const compactTopics = compactContext.children.find(child => child.className === 'source-topics');
  assert.equal(compactTopics.children.length, 2);
  compactTopics.children[0].emit('click');
  assert.equal(layouts.api.sourceState.topic, 'protocol-analysis');
  assert.equal(new URL(layouts.context.location.href).searchParams.get('topic'), 'protocol-analysis');
  assert.equal(layouts.api.sourceFiltered().length, 1);
  const unknownLayout = setup('?layout=invalid'); unknownLayout.api.applyLanguage();
  assert.equal(unknownLayout.context.document.documentElement.dataset.layout, 'compact');
  assert.equal(home.api.state.layout, 'compact');
  const invalid = setup('?view=curated&target=unrecognized&source-target=unrecognized');
  await invalid.api.load();
  assert.equal(invalid.api.state.target, 'all');
  assert.equal(invalid.api.sourceState.target, 'all');
  // Menu and repository order must not follow the process locale; the Python test runs this file under several.
  const sortRecords = [
    ['zeta/project', 'project', 'jvm', 5, '2026-03-01T00:00:00Z', ['zeta', 'aadog']],
    ['aadog/fd-back', 'tool', 'core', 5, '2026-03-01T00:00:00Z', ['aadog', 'zeta']],
    ['mid/reverse-engineering', 'integration', 'agent-mcp', 9, '2026-01-01T00:00:00Z', ['reverse-engineering']],
    ['Beta/viewer', 'case-study', 'jvm', 1, '2026-02-01T00:00:00Z', []],
    ['delta/list', 'collection', 'core', 1, '', []],
    ['echo/docs', 'documentation', 'agent-mcp', 0, '2026-02-01T00:00:00Z', []],
    ['fox/course', 'learning-resource', 'jvm', null, '', []],
    ['gamma/paper', 'research', 'core', 0, '2026-04-01T00:00:00Z', []],
  ].map(([full_name, kind, category, stars, pushed_at, topics], index) => ({id: 'sort-' + index, name: full_name, name_zh: full_name,
    full_name, url: 'https://github.com/' + full_name, evidence_url: 'https://github.com/' + full_name, description_en: '', description_zh: '',
    targets: ['app'], topics, category, group: 'tools', kind, relationship: 'foundation', requirements: [], requirements_zh: [],
    verified_at: '2026-01-01', scan_status: 'readme-scanned', stars, pushed_at}));
  const orders = {};
  for (const lang of ['en', 'zh']) {
    const sorted = setup(`?view=curated&lang=${lang}`, {records: sortRecords});
    await sorted.api.load(); await sorted.api.loadSources(); sorted.api.applyLanguage();
    assert.equal(sorted.api.sourceState.error, false);
    const menu = selector => sorted.elements.get(selector).children.slice(1).map(option => option.textContent);
    orders[lang] = {kinds: menu('#kind-select'), categories: menu('#category-select')};
    orders.topics = Array.from(sorted.api.sourceState.topicCounts, ([topic]) => topic);
    for (const sort of ['name', 'stars', 'pushed', 'relevance']) {
      sorted.api.sourceState.sort = sort; orders[sort] = Array.from(sorted.api.sourceFiltered(), record => record.full_name);
    }
  }
  assert.deepEqual(orders.en.kinds, ['Case study', 'Collection', 'Documentation', 'Integration', 'Learning resource', 'Project', 'Research', 'Tool']);
  assert.deepEqual(orders.zh.kinds, ['案例', '工具', '合集', '集成', '文档', '项目', '学习资源', '研究']);
  assert.deepEqual(orders.en.categories, ['JVM bytecode', 'MCP servers', 'REA essentials']);
  assert.deepEqual(orders.zh.categories, ['JVM 字节码', 'MCP 服务', 'REA 核心']);
  assert.deepEqual(orders.topics, ['aadog', 'zeta', 'reverse-engineering']);
  assert.deepEqual(orders.name, ['aadog/fd-back', 'Beta/viewer', 'delta/list', 'echo/docs', 'fox/course', 'gamma/paper', 'mid/reverse-engineering', 'zeta/project']);
  assert.deepEqual(orders.stars, ['mid/reverse-engineering', 'aadog/fd-back', 'zeta/project', 'Beta/viewer', 'delta/list', 'echo/docs', 'gamma/paper', 'fox/course']);
  assert.deepEqual(orders.pushed, ['gamma/paper', 'aadog/fd-back', 'zeta/project', 'Beta/viewer', 'echo/docs', 'mid/reverse-engineering', 'delta/list', 'fox/course']);
  assert.deepEqual(orders.relevance, ['mid/reverse-engineering', 'aadog/fd-back', 'zeta/project', 'Beta/viewer', 'delta/list', 'echo/docs', 'gamma/paper', 'fox/course']);
  process.stdout.write(`Protocol UI boundaries passed under ${Intl.Collator().resolvedOptions().locale}\n`);
})().catch(error => { console.error(error); process.exitCode = 1; });
