/* Exercise the curated Sort control through the real homepage script in the offline VM. */
const assert = require('node:assert/strict');
const {setup} = require('./protocol_target_ui.cjs');

// Twenty records: enough for Show More, with shared names and review dates to exercise tie-breaks.
const KINDS = ['case-study', 'tool', 'documentation', 'integration', 'project'];
const NAMES = [['zeta', '泽塔'], ['Alpha', '阿尔法'], ['beta', '贝塔'], ['Ghidra', '吉德拉'], ['alpha', '阿尔法']];
function records() {
  return Array.from({length: 20}, (_, index) => {
    const [name, nameZh] = NAMES[index % NAMES.length];
    const id = index === 7 ? 'ghidra' : `fixture-${String(index).padStart(2, '0')}`;
    const day = String(10 + (index % 4)).padStart(2, '0');
    return {id, name: `${name} ${index % 3}`, name_zh: `${nameZh}${index % 3}`, full_name: `Fixture/${id}`,
      url: `https://github.com/Fixture/${id}`, evidence_url: `https://github.com/Fixture/${id}`,
      description_en: 'Fixture', description_zh: '测试', targets: [index % 2 ? 'app' : 'game'], topics: [],
      category: 'dynamic-analysis', group: 'tools', kind: KINDS[index % KINDS.length], relationship: 'foundation',
      requirements: ['A fixture'], requirements_zh: ['测试条件'], scan_status: 'readme-scanned', stars: index,
      // Same calendar day, different representations: the displayed date decides the order.
      verified_at: index % 5 === 0 ? `2026-10-${day}T23:00:00Z` : `2026-10-${day}`};
  });
}
const RANK = {'tool': 0, 'integration': 1, 'project': 2, 'case-study': 3, 'collection': 4, 'research': 5, 'learning-resource': 6, 'documentation': 7};
const rank = record => record.id === 'ghidra' ? 4 : 100 + (RANK[record.kind] ?? 8);
function application(query = '', pathname = '/') {
  const app = setup(query, {pathname, records: records()});
  app.replacements = [];
  const replace = app.context.history.replaceState;
  app.context.history.replaceState = (...args) => { app.replacements.push(String(args[2])); replace(...args); };
  return app;
}
const ids = list => list.map(record => record.id);
const rendered = app => app.elements.get('#resource-grid').children.map(card => card.dataset.recordId);
const param = (app, key) => app.context.location.searchParams.get(key);
function choose(app, value) { const select = app.elements.get('#curated-sort'); select.value = value; select.emit('change'); }

const tests = {
  async defaultOrderIsUnchanged() {
    const rows = records().map((row, order) => ({...row, order}));
    const expected = ids(rows.sort((a, b) => rank(a) - rank(b) || a.order - b.order));
    for (const query of ['', '?order=featured', '?order=bogus', '?order=Name']) {
      const app = application(query);
      await app.api.load();
      assert.equal(app.api.state.order, 'featured');
      assert.deepEqual(ids(app.api.filtered()), expected, `default order for ${query || 'a bare URL'}`);
      assert.equal(param(app, 'order'), null, 'default and unknown orders leave the URL');
      assert.equal(app.elements.get('#curated-sort').value, 'featured');
    }
  },
  async nameOrderFollowsTheActiveLanguage() {
    for (const [pathname, field, locale] of [['/', 'name', 'en'], ['/zh/', 'name_zh', 'zh-CN']]) {
      const app = application('?order=name', pathname);
      await app.api.load();
      const collator = new Intl.Collator(locale);
      const expected = ids(records().sort((a, b) => collator.compare(a[field], b[field]) || Intl.Collator('en').compare(a.id, b.id)));
      assert.deepEqual(ids(app.api.filtered()), expected);
      assert.equal(param(app, 'order'), 'name');
    }
    const app = application('?order=name&kind=tool');
    await app.api.load();
    const english = ids(app.api.filtered());
    app.api.state.lang = 'zh'; app.api.applyLanguage();
    const chinese = ids(app.api.filtered());
    assert.deepEqual([...chinese].sort(), [...english].sort(), 'switching language never changes which records match');
    assert(chinese.every(id => records().find(row => row.id === id).kind === 'tool'));
    // Equal names fall back to the record ID, so the order is total.
    const equal = application('?order=name', '/zh/');
    await equal.api.load();
    const order = ids(equal.api.filtered());
    const start = order.indexOf('fixture-01');
    assert.deepEqual(order.slice(start, start + 3), ['fixture-01', 'fixture-04', 'fixture-16'], 'one name, ordered by ID');
  },
  async reviewOrderIsNewestDisplayedDateFirst() {
    const app = application('?order=reviewed');
    await app.api.load();
    const found = app.api.filtered();
    const dates = found.map(record => record.verified_at.slice(0, 10));
    assert.deepEqual(dates, [...dates].sort().reverse(), 'newest displayed review date first');
    for (const day of new Set(dates)) {
      const group = found.filter(record => record.verified_at.startsWith(day));
      const expected = [...group].sort((a, b) => rank(a) - rank(b) || a.order - b.order);
      assert.deepEqual(ids(group), ids(expected), `ties on ${day} keep the default order`);
    }
  },
  async controlRoundTripsThroughTheURL() {
    const app = application('?q=fixture&target=app&kind=tool&layout=cards#catalog');
    await app.api.load();
    app.api.state.visible = 30;
    choose(app, 'reviewed');
    assert.equal(app.api.state.order, 'reviewed');
    assert.equal(app.api.state.visible, 15, 'a new order starts again from the first results');
    assert.equal(param(app, 'order'), 'reviewed');
    for (const [key, expected] of [['q', 'fixture'], ['target', 'app'], ['kind', 'tool'], ['layout', 'cards']]) assert.equal(param(app, key), expected);
    assert.equal(app.context.location.hash, '#catalog');
    const shared = application(app.context.location.search + app.context.location.hash);
    await shared.api.load();
    assert.equal(shared.api.state.order, 'reviewed');
    assert.equal(shared.elements.get('#curated-sort').value, 'reviewed');
    assert.deepEqual(ids(shared.api.filtered()), ids(app.api.filtered()));
    assert.equal(shared.replacements.length, 0, 'a valid shared order is already canonical');
    const chinese = shared.languageLinks.find(link => link.dataset.languageLink === 'zh');
    choose(shared, 'name');
    assert.equal(new URL(chinese.href, shared.context.location.href).searchParams.get('order'), 'name', 'language links carry the order');
    choose(shared, 'featured');
    assert.equal(param(shared, 'order'), null);
    choose(shared, 'not-an-order');
    assert.equal(shared.api.state.order, 'featured');
    // Clear filters resets the query and filters; the order, like the layout, is a reading preference.
    choose(shared, 'name');
    shared.api.reset();
    assert.equal(shared.api.state.order, 'name');
    assert.equal(param(shared, 'order'), 'name');
    assert.equal(param(shared, 'q'), null);
  },
  async showMoreContinuesTheChosenOrder() {
    for (const order of ['featured', 'name', 'reviewed']) {
      const app = application(order === 'featured' ? '' : `?order=${order}`);
      await app.api.load();
      const all = ids(app.api.filtered());
      assert.deepEqual(rendered(app), all.slice(0, 15));
      app.elements.get('#load-more').emit('click');
      assert.deepEqual(rendered(app), all, `Show More appends the next ${order} results`);
    }
  },
};

(async () => {
  const selected = process.argv.slice(2);
  for (const name of selected.length ? selected : Object.keys(tests)) {
    if (!tests[name]) throw new Error('Unknown test group: ' + name);
    await tests[name]();
    console.log('Curated sort passed: ' + name);
  }
})().catch(error => { console.error(error); process.exit(1); });
