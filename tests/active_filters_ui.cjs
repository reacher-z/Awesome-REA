/* Exercise the removable active-filter chips through the real homepage script in the offline VM. */
const assert = require('node:assert/strict');
const {setup} = require('./protocol_target_ui.cjs');
const settle = () => new Promise(resolve => setImmediate(resolve));

function application(query, options = {}) {
  const app = setup(query, options);
  // Track focus: the shared fake elements accept focus() but do not record it.
  const document = app.context.document;
  Object.getPrototypeOf(app.elements.get('#search-input')).focus = function () { document.activeElement = this; };
  return app;
}
const chips = (app, selector = '#active-filters') => app.elements.get(selector).children.map(item => item.children[0]);
const texts = (app, selector) => chips(app, selector).map(chip => chip.children.slice(0, 2).map(part => part.textContent).join(' '));
const labels = (app, selector) => chips(app, selector).map(chip => chip.attrs['aria-label']);
const param = (app, key) => app.context.location.searchParams.get(key);
const focused = app => app.context.document.activeElement;

const tests = {
  async curatedChipsRemoveOneConstraint() {
    const query = '?q=%20fixture%20&target=app&kind=tool&category=dynamic-analysis&group=tools&layout=cards#catalog';
    const app = application(query);
    await app.api.load();
    assert.equal(app.elements.get('#active-filters').hidden, false);
    assert.deepEqual(texts(app), ['Search: “fixture”', 'Target: App', 'Type: Tool', 'Category: dynamic analysis', 'Group: Foundation tools']);
    assert.deepEqual(labels(app), ['Remove filter Search: “fixture”', 'Remove filter Target: App', 'Remove filter Type: Tool',
      'Remove filter Category: dynamic analysis', 'Remove filter Group: Foundation tools']);
    assert(chips(app).every(chip => chip.type === 'button'));
    app.api.state.visible = 30;
    chips(app)[2].emit('click');
    assert.equal(app.api.state.kind, 'all');
    assert.equal(app.elements.get('#kind-select').value, 'all');
    assert.equal(app.api.state.visible, 15);
    assert.equal(param(app, 'kind'), null);
    for (const [key, expected] of [['q', ' fixture '], ['target', 'app'], ['category', 'dynamic-analysis'], ['group', 'tools'], ['layout', 'cards']]) {
      assert.equal(param(app, key), expected, `removing Type keeps ${key}`);
    }
    assert.equal(app.context.location.hash, '#catalog');
    assert.equal(focused(app), chips(app)[2], 'focus moves to the chip that took its place');
    assert.equal(focused(app).attrs['aria-label'], 'Remove filter Category: dynamic analysis');
    chips(app)[3].emit('click');
    assert.equal(param(app, 'group'), null);
    assert.equal(focused(app), chips(app)[2], 'removing the last chip focuses the previous one');
    while (chips(app).length) chips(app)[0].emit('click');
    assert.equal(app.elements.get('#active-filters').hidden, true);
    assert.equal(focused(app), app.elements.get('#search-input'), 'with no chips left, focus returns to the search field');
    assert.equal(app.elements.get('#search-input').value, '');
    assert.equal(app.context.location.search, '?layout=cards');
  },
  async chineseLabelsAndLanguageSwitch() {
    const app = application('?q=fixture&target=game&kind=tool', {pathname: '/zh/'});
    await app.api.load();
    assert.deepEqual(texts(app), ['搜索： “fixture”', '领域： 游戏', '类型： 工具']);
    assert.deepEqual(labels(app), ['移除筛选条件「搜索：“fixture”」', '移除筛选条件「领域：游戏」', '移除筛选条件「类型：工具」']);
    app.api.state.lang = 'en'; app.api.applyLanguage();
    assert.deepEqual(texts(app), ['Search: “fixture”', 'Target: Game', 'Type: Tool']);
  },
  async zeroResultsKeepEveryConstraint() {
    // No curated record has a Protocol target, so its button is hidden; the URL filter stays valid and visible.
    const app = application('?q=no%20such%20fixture&target=protocol', {curatedProtocol: false});
    await app.api.load();
    assert.equal(app.buttons.find(button => button.dataset.target === 'protocol').hidden, true);
    assert.equal(app.api.filtered().length, 0);
    assert.equal(app.elements.get('#empty-state').hidden, false);
    assert.deepEqual(texts(app), ['Search: “no such fixture”', 'Target: Protocol']);
    chips(app)[0].emit('click');
    assert.equal(app.api.state.target, 'protocol', 'relaxing the query keeps the hidden target');
    assert.deepEqual(texts(app), ['Target: Protocol']);
    assert.equal(param(app, 'target'), 'protocol');
    app.api.state.q = 'again'; app.api.reset();
    for (const key of ['q', 'target']) assert.equal(param(app, key), null, 'Clear all still resets everything');
    assert.equal(app.elements.get('#active-filters').hidden, true);
  },
  async repositoryChipsKeepSortAndOtherFilters() {
    const app = application('?view=source-index&sourceq=project&source-target=protocol&topic=fixtures&sort=stars&q=kept&target=app');
    await app.api.load(); await settle();
    assert.equal(app.api.sourceState.mode, 'source-index');
    assert.deepEqual(texts(app, '#source-active-filters'), ['Search: “project”', 'Target: Protocol', 'Topic: fixtures']);
    chips(app, '#source-active-filters')[2].emit('click');
    assert.equal(app.api.sourceState.topic, '');
    assert.equal(app.elements.get('#source-topic').value, '');
    for (const [key, expected] of [['sourceq', 'project'], ['source-target', 'protocol'], ['sort', 'stars'], ['view', 'source-index'], ['q', 'kept'], ['target', 'app']]) {
      assert.equal(param(app, key), expected, `removing the topic keeps ${key}`);
    }
    assert.equal(param(app, 'topic'), null);
    assert.equal(focused(app), chips(app, '#source-active-filters')[1]);
    chips(app, '#source-active-filters')[0].emit('click');
    chips(app, '#source-active-filters')[0].emit('click');
    assert.equal(app.elements.get('#source-active-filters').hidden, true);
    assert.equal(focused(app), app.elements.get('#source-search'));
    assert.equal(app.elements.get('#source-clear').hidden, false, 'the sort is not a chip but Clear filters still resets it');
  },
};

(async () => {
  const selected = process.argv.slice(2);
  for (const name of selected.length ? selected : Object.keys(tests)) {
    if (!tests[name]) throw new Error('Unknown test group: ' + name);
    await tests[name]();
    console.log('Active filters passed: ' + name);
  }
})().catch(error => { console.error(error); process.exit(1); });
