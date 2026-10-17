/* Repository-browser logic in site/app.js, run offline against a DOM stub built from site/index.html. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'site/index.html'), 'utf8');
const script = fs.readFileSync(path.join(root, 'site/app.js'), 'utf8');
const camel = name => name.replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());

class Element {
  constructor(owner, tag = 'div') {
    this.owner = owner; this.tag = tag; this.children = []; this.dataset = {}; this.attrs = {}; this.handlers = {};
    this.value = ''; this.className = ''; this.textContent = ''; this.hidden = false; this.open = false;
    const classes = new Set(); this.classes = classes;
    this.classList = {toggle(name, force) { if (force ?? !classes.has(name)) classes.add(name); else classes.delete(name); }, add: name => classes.add(name), remove: name => classes.delete(name)};
  }
  append(...nodes) { for (const node of nodes) this.children.push(...(node.tag === 'fragment' ? node.children : [node])); }
  replaceChildren(...nodes) { this.children = []; this.append(...nodes); }
  setAttribute(key, value) { this.attrs[key] = String(value); }
  getAttribute(key) { return this.attrs[key] ?? null; }
  addEventListener(event, callback) { this.handlers[event] = callback; }
  emit(event, value) { if (value !== undefined) this.value = value; this.handlers[event]?.({target: this}); }
  get options() { return this.children; }
  focus() { this.owner.activeElement = this; }
  scrollIntoView() {}
  // Cards only look up their own details element.
  querySelector(selector) {
    const match = {'details': node => node.tag === 'details', 'details[open]': node => node.tag === 'details' && node.open}[selector];
    assert(match, 'Unexpected card selector ' + selector);
    return descendants(this).find(match) || null;
  }
}
const descendants = node => node.children.flatMap(child => [child, ...descendants(child)]);
const hasClass = (node, name) => node.className.split(/\s+/).includes(name);
const byClass = (node, name) => descendants(node).filter(child => hasClass(child, name));

/* Each element with an id or data attribute in the homepage markup (plus optional extra markup) becomes a stub
   node, so querySelectorAll returns what the real page provides instead of an empty list. */
function setup(query = '', {catalog, browser, extraMarkup = ''} = {}) {
  const document = {baseURI: 'https://awesomerea.org/', documentElement: {dataset: {}}, title: '', listeners: {}};
  const make = tag => new Element(document, tag);
  document.activeElement = make('body'); document.activeElement.tagName = 'BODY';
  const marked = [...(html + extraMarkup).matchAll(/<([a-z][a-z0-9]*)\b([^>]*)>/gi)].filter(([, , attributes]) => /\s(?:id|data-[\w-]+)=/.test(attributes)).map(([, tag, attributes]) => {
    const node = make(tag.toLowerCase());
    for (const [, name, value = ''] of attributes.matchAll(/([\w:-]+)(?:="([^"]*)")?/g)) {
      node.attrs[name] = value;
      if (name.startsWith('data-')) node.dataset[camel(name.slice(5))] = value;
      else if (name === 'id') node.id = value; else if (name === 'class') node.className = value; else if (name === 'hidden') node.hidden = true;
    }
    return node;
  });
  const ids = new Map(marked.filter(node => node.id).map(node => [node.id, node]));
  const roots = () => [...ids.values()];
  document.querySelector = selector => {
    if (selector.startsWith('meta[')) return null;
    if (selector.startsWith('#')) { if (!ids.has(selector.slice(1))) ids.set(selector.slice(1), make('div')); return ids.get(selector.slice(1)); }
    return document.querySelectorAll(selector)[0] || null;
  };
  document.querySelectorAll = selector => {
    const attribute = selector.match(/^\[data-([\w-]+)(?:="([^"]*)")?\]$/);
    if (attribute) return marked.filter(node => attribute[2] === undefined ? camel(attribute[1]) in node.dataset : node.dataset[camel(attribute[1])] === attribute[2]);
    const className = selector.match(/^\.([\w-]+)$/);
    assert(className, 'Unexpected document selector ' + selector);
    return roots().flatMap(node => byClass(node, className[1]));
  };
  document.createElement = make; document.createElementNS = (_, tag) => make(tag);
  document.createDocumentFragment = () => make('fragment');
  document.addEventListener = (event, callback) => { document.listeners[event] = callback; };

  const location = new URL('https://awesomerea.org/' + query);
  location.assign = next => { location.lastNavigation = String(next); };
  const responses = {catalog, browser};
  const context = {document, location, URL, URLSearchParams, console,
    history: {replaceState(_, __, next) { location.href = String(next); location.search = new URL(next).search; }},
    fetch: async url => {
      const body = responses[new URL(url).pathname === '/catalog.json' ? 'catalog' : 'browser'];
      return body === undefined ? {ok: false, status: 503} : {ok: true, json: async () => structuredClone(body)};
    }};
  vm.createContext(context);
  vm.runInContext(script.replace('applyLanguage(); load();', '') + '\nglobalThis.audit = {state,sourceState,load,loadSources,filtered,sourceFiltered,applyLanguage,setIndexMode,sourceBrowserPayload,sourceRelatedEntries};', context);
  const element = id => document.querySelector('#' + id);
  return {api: context.audit, document, location, responses, element, marked};
}

function curatedRecord(index, changes = {}) {
  return {id: 'curated-' + index, name: 'Curated ' + index, name_zh: '精选 ' + index, url: `https://github.com/curated/tool-${index}`,
    evidence_url: `https://github.com/curated/tool-${index}#readme`, description_en: 'Curated fixture ' + index, description_zh: '精选测试 ' + index,
    category: 'dynamic-analysis', group: 'tools', kind: 'tool', relationship: 'foundation', targets: ['app'],
    requirements: ['Requirement ' + index], requirements_zh: ['条件 ' + index], verified_at: '2026-01-02T03:04:05Z', ...changes};
}
function repository(full_name, changes = {}) {
  return {id: full_name.toLowerCase().replace(/[^a-z0-9]+/g, '-'), full_name, url: 'https://github.com/' + full_name,
    readme_url: `https://github.com/${full_name}#readme`, description_en: '', description_zh: '', topics: [], targets: ['app'],
    stars: 0, pushed_at: '', scan_status: 'readme-scanned', ...changes};
}
const catalogOf = (resources, changes = {}) => ({resources, topic_labels: {}, meta: {repository_url: 'https://github.com/reacher-z/Awesome-REA', source_index: {resource_count: 1}}, ...changes});
function browserOf(resources, excluded = 0) {
  return {meta: {schema_version: 1, status: 'complete', full_export: 'source-index.json', full_export_sha256: 'a'.repeat(64),
    completed_at: '2026-10-16T01:02:03Z', scope: {scanned_count: resources.length + excluded, excluded_count: excluded, browse_count: resources.length}}, resources};
}
// Start like the page does, then wait for the repository payload, whether or not the view requested it.
async function loaded(query, options) {
  const app = setup(query, options);
  app.api.applyLanguage(); await app.api.load(); await app.api.loadSources();
  while (app.api.sourceState.loading) await new Promise(resolve => setImmediate(resolve));
  return app;
}
const names = records => Array.from(records, record => record.full_name);
const shownNames = app => app.element('source-results').children.map(card => byClass(card, 'source-title-link')[0].children.map(part => part.textContent).join(''));
const urlParam = (app, key) => new URL(app.location.href).searchParams.get(key);

(async () => {
  // The integrity guard rejects every malformed payload, and loadSources then shows the error state.
  const valid = browserOf([repository('valid/one'), repository('valid/two')], 1);
  const curated = catalogOf([curatedRecord(1)]);
  const mutate = change => { const payload = structuredClone(valid); change(payload); return payload; };
  {
    const app = setup('', {catalog: curated, browser: valid});
    const accepted = structuredClone(valid);
    assert.strictEqual(app.api.sourceBrowserPayload(accepted), accepted);
    const unsupported = /Unsupported repository browser data/, counts = /Repository browser counts disagree/, invalid = /Invalid repository browser record/;
    const malformed = [
      ['schema version', p => { p.meta.schema_version = 2; }, unsupported], ['missing meta', p => { delete p.meta; }, unsupported],
      ['status', p => { p.meta.status = 'failed'; }, unsupported], ['resources object', p => { p.resources = {}; }, unsupported],
      ['export name', p => { p.meta.full_export = 'source-browser.json'; }, unsupported],
      ['short SHA-256', p => { p.meta.full_export_sha256 = 'a'.repeat(63); }, unsupported],
      ['uppercase SHA-256', p => { p.meta.full_export_sha256 = 'A'.repeat(64); }, unsupported],
      ['numeric SHA-256', p => { p.meta.full_export_sha256 = 1; }, unsupported],
      ['missing scope', p => { delete p.meta.scope; }, counts], ['sum', p => { p.meta.scope.scanned_count = 4; }, counts],
      ['browse count', p => { p.meta.scope.browse_count = 3; p.meta.scope.scanned_count = 4; }, counts],
      ['negative count', p => { p.meta.scope.excluded_count = -1; p.meta.scope.scanned_count = 1; }, counts],
      ['fractional count', p => { p.meta.scope.excluded_count = 0.5; p.meta.scope.scanned_count = 2.5; }, counts],
      ['string count', p => { p.meta.scope.excluded_count = '1'; }, counts],
      ['duplicate ID', p => { p.resources[1].id = p.resources[0].id; }, invalid], ['empty ID', p => { p.resources[0].id = ''; }, invalid],
      ['numeric ID', p => { p.resources[0].id = 7; }, invalid], ['null record', p => { p.resources[0] = null; }, invalid],
      ['empty name', p => { p.resources[0].full_name = ''; }, invalid],
      ['failed scan', p => { p.resources[0].scan_status = 'readme-failed'; }, invalid],
      ['excluded row', p => { p.resources[0].scope_status = 'excluded'; }, invalid],
    ];
    for (const [name, change, message] of malformed) assert.throws(() => app.api.sourceBrowserPayload(mutate(change)), message, name);
    for (const lang of ['en', 'zh']) {
      for (const [name, browser] of [...malformed.map(([name, change]) => [name, mutate(change)]), ['HTTP 503', undefined]]) {
        const failed = setup(`?lang=${lang}`, {catalog: curated, browser});
        await failed.api.load();
        failed.element('source-more-row').hidden = false; failed.element('source-empty').hidden = false;
        await failed.api.loadSources();
        assert.equal(failed.api.sourceState.error, true, name);
        assert.equal(failed.api.sourceState.loaded, false, name);
        assert.equal(failed.api.sourceState.loading, false, name);
        assert.equal(failed.element('source-error').hidden, false, name);
        assert.equal(failed.element('source-status').textContent, lang === 'zh' ? '项目仓库暂时未能加载。' : 'Repositories couldn’t load.', name);
        assert.equal(failed.element('source-results').getAttribute('aria-busy'), 'false', name);
        assert.equal(failed.element('source-empty').hidden, true, name);
        assert.equal(failed.element('source-more-row').hidden, true, name);
        assert.deepEqual(failed.element('source-results').children, [], name);
      }
    }
    // Retrying after the data is fixed clears the error and renders the repositories.
    const retried = setup('?view=source-index', {catalog: curated, browser: mutate(p => { p.meta.status = 'failed'; })});
    await retried.api.load(); await new Promise(resolve => setImmediate(resolve));
    assert.equal(retried.api.sourceState.error, true);
    retried.responses.browser = valid;
    await retried.element('source-retry').handlers.click();
    assert.equal(retried.api.sourceState.error, false);
    assert.equal(retried.element('source-error').hidden, true);
    assert.deepEqual(shownNames(retried), ['valid/one', 'valid/two']);
    assert.equal(retried.element('source-status').textContent, '2 repositories');
    assert.match(retried.element('source-snapshot').textContent, /Scanned 3 repositories; 1 outside this collection’s scope or no longer available upstream are omitted/);
  }

  // Related entries keep only exact detail or listing links for paper and curated slugs, once each.
  {
    const app = setup('', {catalog: curated, browser: valid});
    const paper = {kind: 'paper', id: 'paper-fixture', title_en: 'Paper', title_zh: '论文', href_en: '/papers/paper-fixture/', href_zh: '/zh/papers/paper-fixture/'};
    const resource = {kind: 'curated', id: 'tool-fixture', title_en: 'Tool', title_zh: '工具', href_en: '/resources/#tool-fixture', href_zh: '/zh/resources/#tool-fixture'};
    const accepted = [paper, {...paper, id: 'paper-listing', href_en: '/papers/#paper-listing', href_zh: '/zh/papers/#paper-listing'},
      resource, {...resource, id: 'tool-detail', href_en: '/resources/tool-detail/', href_zh: '/zh/resources/tool-detail/'}];
    const rejected = [
      null, 'paper-fixture', {...paper, kind: 'tool'}, {...paper, kind: undefined}, {...paper, kind: 'Paper'},
      {...resource, id: 'Tool-Fixture'}, {...resource, id: 'tool--fixture'}, {...resource, id: '-tool'}, {...resource, id: 'tool_fixture'}, {...resource, id: 7},
      {...paper, id: 'fixture', href_en: '/papers/#fixture', href_zh: '/zh/papers/#fixture'},
      {...resource, href_en: 'https://awesomerea.org/resources/#tool-fixture'}, {...resource, href_en: '/resources#tool-fixture'},
      {...resource, href_en: '/resources/#tool-fixture?x=1'}, {...resource, href_zh: '/zh/resources/#other'}, {...resource, href_zh: '/resources/#tool-fixture'},
      {...resource, href_en: '/papers/#tool-fixture', href_zh: '/zh/papers/#tool-fixture'},
      {...resource, href_zh: '/zh/resources/tool-fixture/'}, {...paper, href_en: '/papers/paper-fixture'},
      {...resource, title_en: '  '}, {...resource, title_zh: ''}, {...paper, title_zh: undefined}, {...paper, title_en: 5},
    ];
    // Copy results into this realm: entries returned from the page's VM have its Array prototype.
    const related = value => [...app.api.sourceRelatedEntries({related_entries: value})];
    assert.deepEqual(related([...accepted, ...rejected]), accepted);
    for (const entry of rejected) assert.deepEqual(related([entry]), [], JSON.stringify(entry));
    const duplicates = [paper, {...paper, href_en: '/papers/#paper-fixture', href_zh: '/zh/papers/#paper-fixture', title_en: 'Again'}, resource, resource];
    assert.deepEqual(related(duplicates), [paper, resource]);
    for (const value of [undefined, null, 'paper-fixture', {0: paper}]) assert.deepEqual(related(value), []);

    // Accepted entries render grouped localized links and their titles become searchable.
    for (const lang of ['en', 'zh']) {
      const related = await loaded(`?view=source-index&lang=${lang}`, {catalog: curated,
        browser: browserOf([repository('related/repo', {related_entries: [...accepted, {...resource, kind: 'tool'}]}), repository('plain/repo')])});
      const card = related.element('source-results').children.find(node => node.dataset.recordId === 'related-repo');
      const [groups] = byClass(card, 'source-related');
      assert.deepEqual(groups.children.map(group => byClass(group, 'source-related-label')[0].textContent), lang === 'zh' ? ['相关研究', '精选资料'] : ['Related research', 'Curated details']);
      assert.deepEqual(byClass(card, 'source-related-link').slice(0, 4).map(link => [link.textContent, link.href]),
        accepted.map(entry => [entry[`title_${lang}`], entry[`href_${lang}`]]));
      assert.equal(byClass(card, 'source-related-link').length, 8, 'Visible card and compact details both list the four entries');
      related.api.sourceState.q = lang === 'zh' ? '论文' : 'paper';
      assert.deepEqual(names(related.api.sourceFiltered()), ['related/repo']);
    }
  }

  // Curated cards render their localized fields, links and review details.
  for (const lang of ['en', 'zh']) {
    const app = await loaded(`?lang=${lang}`, {catalog: catalogOf([curatedRecord(1, {kind: 'case-study', category: 'reconstruction-cases', relationship: 'official-case-study'})]), browser: valid});
    const [card] = app.element('resource-grid').children;
    const [title] = byClass(card, 'card-title-link');
    assert.equal(title.textContent, lang === 'zh' ? '精选 1' : 'Curated 1');
    assert.deepEqual([title.href, title.target, title.rel], ['https://github.com/curated/tool-1', '_blank', 'noopener noreferrer']);
    assert.equal(byClass(card, 'resource-kind')[0].textContent, lang === 'zh' ? '案例' : 'Case study');
    assert.equal(byClass(card, 'card-description')[0].textContent, lang === 'zh' ? '精选测试 1' : 'Curated fixture 1');
    assert.equal(byClass(card, 'card-category')[0].textContent, lang === 'zh' ? '重建案例' : 'Reconstruction cases');
    const evidence = byClass(card, 'card-meta')[0].children[1];
    assert.deepEqual([evidence.textContent, evidence.href], [lang === 'zh' ? '复核来源 ↗' : 'Review source ↗', 'https://github.com/curated/tool-1#readme']);
    assert.equal(byClass(card, 'resource-entry-link')[0].href, `${lang === 'zh' ? '/zh' : ''}/resources/curated-1/`);
    const details = card.querySelector('details');
    assert.deepEqual(descendants(details).filter(node => node.tag === 'li').map(node => node.textContent), [lang === 'zh' ? '条件 1' : 'Requirement 1']);
    const context = byClass(details, 'resource-detail-meta')[0].children;
    assert.deepEqual(context.map(node => node.textContent), lang === 'zh' ? ['REA · 官方案例', '来源已复核', '复核于 2026-01-02'] : ['REA · CASE STUDY', 'Source-reviewed', 'Reviewed 2026-01-02']);
    assert.equal(context[2].dateTime, '2026-01-02T03:04:05Z');
    assert.equal(app.element('results-status').textContent, lang === 'zh' ? '1 项资源' : '1 resource');
  }

  // Repository sorts on a fixture with ties: stars, pushed and name break ties by name; relevance without a
  // query ranks curated GitHub repositories, then reverse-engineering topics or descriptions, then stars.
  const sortRows = [
    repository('plain/popular', {stars: 500, pushed_at: '2026-03-01T00:00:00Z'}),
    repository('re/ghidra-scripts', {stars: 50, topics: ['ghidra'], pushed_at: '2026-05-01T00:00:00Z'}),
    repository('curated/tool-1', {stars: 1, pushed_at: '2026-03-01T00:00:00Z'}),
    repository('re/described', {stars: 50, description_en: 'A binary-analysis helper.', pushed_at: '2026-04-01T00:00:00Z'}),
    repository('plain/unknown', {stars: null, topics: ['plugin']}),
    repository('Curated/Tool-2', {url: 'https://github.com/curated/tool-2.git', stars: 3, pushed_at: '2026-03-01T00:00:00Z'}),
    repository('plain/zero', {stars: 0, description_en: 'Mentions Ghidra in passing.', pushed_at: '2026-02-01T00:00:00Z'}),
    repository('plain/aliased', {stars: 0, topics: ['ghidra'], pushed_at: '2026-02-01T00:00:00Z'}),
  ];
  const sortCatalog = catalogOf([curatedRecord(1), curatedRecord(2), curatedRecord(3, {url: 'https://gitlab.com/curated/tool-3'})]);
  {
    const app = await loaded('?view=source-index', {catalog: sortCatalog, browser: browserOf(sortRows)});
    const order = sort => { app.api.sourceState.sort = sort; return names(app.api.sourceFiltered()); };
    assert.deepEqual(order('stars'), ['plain/popular', 're/described', 're/ghidra-scripts', 'Curated/Tool-2', 'curated/tool-1', 'plain/aliased', 'plain/zero', 'plain/unknown']);
    assert.deepEqual(order('pushed'), ['re/ghidra-scripts', 're/described', 'curated/tool-1', 'Curated/Tool-2', 'plain/popular', 'plain/aliased', 'plain/zero', 'plain/unknown']);
    assert.deepEqual(order('name'), ['curated/tool-1', 'Curated/Tool-2', 'plain/aliased', 'plain/popular', 'plain/unknown', 'plain/zero', 're/described', 're/ghidra-scripts']);
    assert.deepEqual(order('relevance'), ['Curated/Tool-2', 'curated/tool-1', 're/described', 're/ghidra-scripts', 'plain/aliased', 'plain/zero', 'plain/popular', 'plain/unknown']);
    // With a query, names score 4 and topics 2; equal scores keep the payload order.
    app.api.sourceState.q = 'ghidra';
    assert.deepEqual(order('relevance'), ['re/ghidra-scripts', 'plain/aliased', 'plain/zero']);
    app.api.sourceState.q = '';
    const sort = app.element('source-sort');
    app.api.sourceState.visible = 48; sort.emit('change', 'stars');
    assert.equal(app.api.sourceState.visible, 24);
    assert.equal(urlParam(app, 'sort'), 'stars');
    assert.deepEqual(shownNames(app), order('stars'));
    assert.equal(app.element('source-clear').hidden, false);
    app.element('source-clear').handlers.click();
    assert.equal(urlParam(app, 'sort'), null);
    assert.equal(sort.value, 'relevance');
  }
  for (const [requested, expected] of [['updated', 'pushed'], ['pushed', 'pushed'], ['stars', 'stars'], ['name', 'name'], ['random', 'relevance']]) {
    const app = setup(`?view=curated&sort=${requested}`, {catalog: sortCatalog, browser: browserOf(sortRows)});
    assert.equal(app.api.sourceState.sort, expected);
    assert.equal(app.element('source-sort').value, expected);
  }
  {
    // The legacy sort=updated link opens the pushed order.
    const app = await loaded('?view=source-index&sort=updated', {catalog: sortCatalog, browser: browserOf(sortRows)});
    assert.deepEqual(shownNames(app), ['re/ghidra-scripts', 're/described', 'curated/tool-1', 'Curated/Tool-2', 'plain/popular', 'plain/aliased', 'plain/zero', 'plain/unknown']);
    assert.equal(urlParam(app, 'sort'), 'pushed');
  }

  // Typed topics accept the canonical ID or a displayed "label · id" in either language.
  const labels = {'reverse-engineering': {en: 'Reverse engineering', zh: '逆向工程'}, 'ghidra': {en: 'Ghidra', zh: 'Ghidra'}};
  const topicRows = [repository('re/general', {topics: ['reverse-engineering', 'ghidra-plugin']}), repository('re/ghidra', {topics: ['ghidra', 'reverse-engineering']}),
    repository('re/plugin', {topics: ['ghidra-plugin']}), repository('other/web', {topics: ['web']})];
  for (const lang of ['en', 'zh']) {
    const app = await loaded(`?view=source-index&lang=${lang}`, {catalog: catalogOf([curatedRecord(1)], {topic_labels: labels}), browser: browserOf(topicRows)});
    const input = app.element('source-topic');
    for (const typed of ['reverse-engineering', 'Reverse engineering · reverse-engineering', '逆向工程 · reverse-engineering', '  REVERSE ENGINEERING · Reverse-Engineering ']) {
      app.api.sourceState.visible = 48; input.emit('input', typed);
      assert.equal(app.api.sourceState.topic, 'reverse-engineering', typed);
      assert.equal(app.api.sourceState.visible, 24);
      assert.equal(urlParam(app, 'topic'), 'reverse-engineering');
      assert.deepEqual(shownNames(app), ['re/general', 're/ghidra']);
    }
    // A known ID matches exactly; other text matches topic IDs and labels by substring.
    input.emit('input', 'ghidra');
    assert.deepEqual(shownNames(app), ['re/ghidra']);
    assert.equal(app.element('source-topic-options').children[0].value, 'Ghidra · ghidra', 'The exact topic leads the suggestions');
    input.emit('input', 'ghidra-');
    assert.equal(app.api.sourceState.topic, 'ghidra-');
    assert.deepEqual(shownNames(app), ['re/general', 're/plugin']);
    input.emit('input', lang === 'zh' ? '逆向' : 'engineering');
    assert.deepEqual(shownNames(app), ['re/general', 're/ghidra']);
    // A restored topic is shown with its localized label; unlabeled topics keep their ID.
    for (const [topic, display] of [['reverse-engineering', `${labels['reverse-engineering'][lang]} · reverse-engineering`], ['web', 'web']]) {
      const restored = await loaded(`?view=source-index&lang=${lang}&topic=${topic}`, {catalog: catalogOf([curatedRecord(1)], {topic_labels: labels}), browser: browserOf(topicRows)});
      assert.equal(restored.element('source-topic').value, display);
    }
  }

  // Show More adds 15 curated or 24 repository records and hides its row when none remain.
  for (const lang of ['en', 'zh']) {
    const app = await loaded(`?lang=${lang}`, {catalog: catalogOf(Array.from({length: 40}, (_, index) => curatedRecord(index))),
      browser: browserOf(Array.from({length: 60}, (_, index) => repository(`many/repo-${String(index).padStart(2, '0')}`, {stars: 100 - index})))});
    const curatedShown = () => [app.element('resource-grid').children.length, app.element('load-more-row').hidden, app.element('remaining-count').textContent, app.element('shown-count').textContent];
    assert.deepEqual(curatedShown(), [15, false, '+15', lang === 'zh' ? '已显示 15 / 40 项' : '15 of 40 resources shown']);
    app.element('load-more').handlers.click();
    assert.deepEqual(curatedShown(), [30, false, '+10', lang === 'zh' ? '已显示 30 / 40 项' : '30 of 40 resources shown']);
    assert.equal(app.document.activeElement, byClass(app.element('resource-grid').children[15], 'card-title-link')[0]);
    app.element('load-more').handlers.click();
    assert.deepEqual(curatedShown(), [40, true, '+0', lang === 'zh' ? '已显示 40 / 40 项' : '40 of 40 resources shown']);
    app.api.setIndexMode('source-index');
    const sourceShown = () => [app.element('source-results').children.length, app.element('source-more-row').hidden, app.element('source-more-count').textContent, app.element('source-shown').textContent];
    assert.deepEqual(sourceShown(), [24, false, '+24', lang === 'zh' ? '已显示 24 / 60 个仓库' : '24 of 60 repositories shown']);
    app.element('source-more').handlers.click();
    assert.deepEqual(sourceShown(), [48, false, '+12', lang === 'zh' ? '已显示 48 / 60 个仓库' : '48 of 60 repositories shown']);
    assert.equal(app.document.activeElement, byClass(app.element('source-results').children[24], 'source-title-link')[0]);
    app.element('source-more').handlers.click();
    assert.deepEqual(sourceShown(), [60, true, '+0', lang === 'zh' ? '已显示 60 / 60 个仓库' : '60 of 60 repositories shown']);
    // Any new filter starts again from the first page.
    app.element('source-search').emit('input', 'repo');
    assert.deepEqual(sourceShown(), [24, false, '+24', lang === 'zh' ? '已显示 24 / 60 个仓库' : '24 of 60 repositories shown']);
  }

  {
    // With exactly one more page left, the row hides as soon as the last record is shown.
    const app = await loaded('', {catalog: catalogOf(Array.from({length: 30}, (_, index) => curatedRecord(index))),
      browser: browserOf(Array.from({length: 48}, (_, index) => repository(`even/repo-${index}`)))});
    app.element('load-more').handlers.click();
    assert.deepEqual([app.element('resource-grid').children.length, app.element('load-more-row').hidden], [30, true]);
    app.api.setIndexMode('source-index'); app.element('source-more').handlers.click();
    assert.deepEqual([app.element('source-results').children.length, app.element('source-more-row').hidden], [48, true]);
  }

  // Remaining curated controls: menus, group links, the empty-state reset, mode buttons and the "/" shortcut.
  {
    const rows = [curatedRecord(1), curatedRecord(2, {kind: 'case-study', category: 'reconstruction-cases', group: 'rea'}), curatedRecord(3, {group: 'learn', kind: 'documentation'})];
    const extraMarkup = '<button data-group="all"></button><button data-group="rea"></button><span data-count="all"></span><span data-count="rea"></span>';
    const app = await loaded('?lang=zh&group=unknown', {catalog: catalogOf(rows), browser: valid, extraMarkup});
    assert.equal(app.api.state.group, 'all');
    assert.deepEqual(app.marked.filter(node => 'count' in node.dataset).map(node => node.textContent), [3, 1]);
    const localized = app.marked.filter(node => node.dataset.localePath === 'about' || node.dataset.localeFragment === 'game').map(node => node.href);
    assert.deepEqual(localized, ['/zh/about/', '/zh/resources/#game']);
    assert(app.marked.filter(node => 'i18nPlaceholder' in node.dataset).every(node => node.placeholder && node.placeholder !== node.dataset.i18nPlaceholder));
    assert(app.marked.filter(node => 'i18nAria' in node.dataset).every(node => /[一-鿿]/.test(node.attrs['aria-label'])));
    const group = app.marked.find(node => node.dataset.group === 'rea');
    app.api.state.visible = 30; group.handlers.click();
    assert.deepEqual([app.api.state.group, app.api.state.visible, urlParam(app, 'group'), group.attrs['aria-pressed'], group.classes.has('active')], ['rea', 15, 'rea', 'true', true]);
    assert.deepEqual(app.api.filtered().map(record => record.id), ['curated-2']);
    app.element('kind-select').emit('change', 'tool');
    assert.equal(urlParam(app, 'kind'), 'tool');
    assert.equal(app.element('results-status').textContent, '0 项匹配资源 · 目录共 3 项');
    assert.equal(app.element('empty-state').hidden, false);
    app.element('empty-reset').handlers.click();
    assert.deepEqual([app.api.state.group, app.api.state.kind, app.element('empty-state').hidden, urlParam(app, 'group'), urlParam(app, 'kind')], ['all', 'all', true, null, null]);
    assert.equal(app.document.activeElement, app.element('search-input'));
    app.element('category-select').emit('change', 'reconstruction-cases');
    assert.deepEqual([urlParam(app, 'category'), app.api.filtered().length, app.element('clear-filters').hidden], ['reconstruction-cases', 1, false]);
    const keydown = (key, changes = {}) => { let prevented = false; app.document.listeners.keydown({key, ctrlKey: false, metaKey: false, altKey: false, preventDefault: () => { prevented = true; }, ...changes}); return prevented; };
    app.document.activeElement = Object.assign(app.document.createElement('body'), {tagName: 'BODY'});
    assert.equal(keydown('/'), true);
    assert.equal(app.document.activeElement, app.element('search-input'));
    for (const [key, changes] of [['/', {ctrlKey: true}], ['k', {}]]) {
      app.document.activeElement = Object.assign(app.document.createElement('body'), {tagName: 'BODY'});
      assert.equal(keydown(key, changes), false);
    }
    app.document.activeElement = Object.assign(app.document.createElement('input'), {tagName: 'INPUT'});
    assert.equal(keydown('/'), false, 'Typing a slash into a field is left alone');
    app.element('mode-sources').handlers.click();
    assert.deepEqual([app.api.sourceState.mode, app.element('source-view').hidden, app.element('curated-view').hidden, urlParam(app, 'view')], ['source-index', false, true, 'source-index']);
    app.document.activeElement = Object.assign(app.document.createElement('body'), {tagName: 'BODY'});
    keydown('/');
    assert.equal(app.document.activeElement, app.element('source-search'));
    app.element('mode-curated').handlers.click();
    assert.deepEqual([app.api.sourceState.mode, app.element('mode-curated').attrs['aria-pressed'], urlParam(app, 'view')], ['curated', 'true', null], 'The default curated view stays out of the URL');
  }
  process.stdout.write('Repository browser logic passed\n');
})().catch(error => { console.error(error); process.exitCode = 1; });
