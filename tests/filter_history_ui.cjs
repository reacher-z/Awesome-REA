/* Exercise homepage Back/Forward behaviour through the real app.js with an offline session-history stack. */
const assert = require('node:assert/strict');
const {setup} = require('./protocol_target_ui.cjs');
const settle = () => new Promise(resolve => setImmediate(resolve));

// A minimal session history: push truncates forward entries, replace rewrites the current one,
// and traversal moves the location before firing popstate, as browsers do.
function application(query = '', pathname = '/') {
  const app = setup(query, {pathname});
  const {context} = app;
  const entries = [context.location.href]; let index = 0;
  app.writes = [];
  context.history = {
    pushState(_, __, next) { entries.splice(index + 1, Infinity, String(next)); index += 1; context.location.href = String(next); app.writes.push('push'); },
    replaceState(_, __, next) { entries[index] = String(next); context.location.href = String(next); app.writes.push('replace'); },
  };
  app.entries = () => entries.slice(0, index + 1);
  app.length = () => entries.length;
  app.traverse = async step => {
    index += step; assert(index >= 0 && index < entries.length, 'no history entry to traverse to');
    context.location.href = entries[index];
    app.windowListeners.popstate({state: null}); await settle();
  };
  // A fragment link (for example #contributors) adds an entry without passing through app.js.
  app.fragment = hash => { const next = new URL(context.location.href); next.hash = hash; entries.splice(index + 1, Infinity, next.href); index += 1; context.location.href = next.href; };
  return app;
}
const element = (app, selector) => app.elements.get(selector);
const param = (app, key) => app.context.location.searchParams.get(key);
const target = (app, name, source = false) => app.buttons.find(node => node.dataset[source ? 'sourceTarget' : 'target'] === name);
function change(app, selector, value, event = 'change') { element(app, selector).value = value; element(app, selector).emit(event); }
function snapshot(app) {
  const {state, sourceState} = app.api;
  return {search: app.context.location.search, mode: sourceState.mode, q: state.q, target: state.target, kind: state.kind,
    category: state.category, sourceq: sourceState.q, sourceTarget: sourceState.target, topic: sourceState.topic, sort: sourceState.sort,
    searchInput: element(app, '#search-input').value, kindSelect: element(app, '#kind-select').value,
    sourceSearch: element(app, '#source-search').value, sortSelect: element(app, '#source-sort').value,
    pressed: target(app, state.target).attrs['aria-pressed']};
}

const tests = {
  async discreteChangesAddEntries() {
    for (const pathname of ['/', '/zh/']) {
      const app = application('', pathname);
      await app.api.load(); await settle();
      const states = [snapshot(app)];
      target(app, 'app').emit('click'); states.push(snapshot(app));
      change(app, '#kind-select', 'tool'); states.push(snapshot(app));
      change(app, '#category-select', 'dynamic-analysis'); states.push(snapshot(app));
      element(app, '#mode-sources').emit('click'); await settle(); states.push(snapshot(app));
      target(app, 'protocol', true).emit('click'); states.push(snapshot(app));
      change(app, '#source-sort', 'stars'); states.push(snapshot(app));
      assert.deepEqual(app.writes, Array(6).fill('push'), 'each deliberate choice adds one entry');
      assert.equal(app.length(), 7);
      const writes = app.writes.length;
      for (let step = states.length - 2; step >= 0; step -= 1) {
        await app.traverse(-1);
        assert.deepEqual(snapshot(app), states[step], `Back restores step ${step} on ${pathname}`);
      }
      for (let step = 1; step < states.length; step += 1) {
        await app.traverse(1);
        assert.deepEqual(snapshot(app), states[step], `Forward restores step ${step} on ${pathname}`);
      }
      assert.equal(app.writes.length, writes, 'restoration never writes history');
      assert.equal(app.context.location.pathname, pathname);
      assert.equal(app.api.state.lang, pathname === '/zh/' ? 'zh' : 'en');
    }
  },
  async typingReplacesTheCurrentEntry() {
    const app = application();
    await app.api.load(); await settle();
    target(app, 'game').emit('click');
    for (const text of ['g', 'gh', 'ghi', 'ghid', 'ghidra']) change(app, '#search-input', text, 'input');
    assert.deepEqual(app.writes, ['push', ...Array(5).fill('replace')]);
    assert.equal(app.length(), 2, 'typing never adds entries');
    assert.equal(param(app, 'q'), 'ghidra');
    element(app, '#mode-sources').emit('click'); await settle();
    for (const text of ['p', 'pr', 'pro']) change(app, '#source-search', text, 'input');
    change(app, '#source-topic', 'fixtures', 'input');
    change(app, '#layout-select', 'cards');
    assert.equal(app.length(), 3, 'repository typing, topic typing and layout replace');
    await app.traverse(-1);
    assert.equal(app.api.sourceState.mode, 'curated');
    assert.equal(app.api.state.q, 'ghidra', 'the typed query belongs to the entry it was typed in');
    assert.equal(element(app, '#search-input').value, 'ghidra');
    assert.equal(app.api.state.layout, 'compact', 'the earlier entry keeps its own layout');
    await app.traverse(-1);
    assert.equal(app.api.state.q, ''); assert.equal(app.api.state.target, 'all');
    await app.traverse(2);
    assert.equal(app.api.sourceState.q, 'pro'); assert.equal(app.api.sourceState.topic, 'fixtures');
    assert.equal(app.api.state.layout, 'cards');
  },
  async resetsAreUndoable() {
    const app = application('?q=fixture&target=app&kind=tool#catalog');
    await app.api.load(); await settle();
    assert.deepEqual(app.writes, [], 'a canonical shared link needs no history write');
    element(app, '#clear-filters').emit('click');
    assert.equal(app.context.location.search, '');
    await app.traverse(-1);
    assert.equal(app.api.state.q, 'fixture'); assert.equal(app.api.state.target, 'app'); assert.equal(app.api.state.kind, 'tool');
    assert.equal(element(app, '#search-input').value, 'fixture');
    assert.equal(app.context.location.hash, '#catalog');
    element(app, '#mode-sources').emit('click'); await settle();
    change(app, '#source-search', 'project', 'input'); target(app, 'protocol', true).emit('click');
    element(app, '#source-clear').emit('click');
    await app.traverse(-1);
    assert.equal(app.api.sourceState.q, 'project'); assert.equal(app.api.sourceState.target, 'protocol');
    assert.equal(element(app, '#source-search').value, 'project');
  },
  async fragmentEntriesKeepResults() {
    const app = application('?target=app');
    await app.api.load(); await settle();
    app.api.state.visible = 30;
    app.fragment('#contributors');
    await app.traverse(-1);
    assert.equal(app.api.state.visible, 30, 'a fragment-only entry keeps Show More progress');
    assert.deepEqual(app.writes, []);
    const link = app.languageLinks.find(node => node.dataset.languageLink === 'zh');
    assert.equal(link.href, '/zh/?target=app', 'language links follow the restored address');
  },
  async malformedEntriesUseSafeDefaults() {
    for (const query of ['?category=bogus&kind=nope&target=moon&group=bogus&lang=invalid&view=unknown&layout=invalid&source-target=moon&sort=bogus',
      '?view=repositories&sort=updated&layout=cards']) {
      // Shared links initialize from the URL and normalize by replacement only.
      const shared = application(query);
      await shared.api.load(); await settle();
      assert(!shared.writes.includes('push'), 'normalization never adds entries');
      const app = application();
      await app.api.load(); await settle();
      app.context.history.pushState(null, '', new URL(query, app.context.location.href));
      app.writes.length = 0;
      await app.traverse(-1); await app.traverse(1);
      assert(!app.writes.includes('push'), 'restoring an entry never adds another');
      assert.deepEqual(snapshot(app), snapshot(shared), `Back/Forward and a shared link agree for ${query}`);
      for (const key of ['group', 'category', 'kind', 'target']) assert.equal(app.api.state[key], 'all');
      assert.equal(app.api.state.lang, 'en');
      assert(['relevance', 'pushed'].includes(app.api.sourceState.sort));
      assert.equal(app.api.sourceState.target, 'all');
    }
  },
};

(async () => {
  const selected = process.argv.slice(2);
  for (const name of selected.length ? selected : Object.keys(tests)) {
    if (!tests[name]) throw new Error('Unknown test group: ' + name);
    await tests[name]();
    console.log('Filter history passed: ' + name);
  }
})().catch(error => { console.error(error); process.exit(1); });
