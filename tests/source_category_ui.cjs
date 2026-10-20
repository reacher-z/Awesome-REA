/* The repository view's Category filter: from category-page links, combined with other filters, validated and clearable. */
const assert = require('node:assert/strict');
const {setup} = require('./protocol_target_ui.cjs');

const LABELS = {'web-analysis': ['Websites', '网站'], 'game-analysis': ['Games', '游戏'], 'android': ['Apps · Android', '应用 · Android'], 'firmware': ['Firmware', '固件']};
const categories = ['android', 'android', 'android', 'firmware', 'web-analysis', 'android'];
const rows = categories.map((category, index) => ({id: `scan-${index}`, name: `project${index}`, name_zh: `项目${index}`, full_name: `Owner/project${index}`,
  url: `https://github.com/Owner/project${index}`, evidence_url: `https://github.com/Owner/project${index}`, description_en: index === 1 ? 'decompiler' : 'tool',
  description_zh: '工具', targets: [index === 2 ? 'firmware' : 'app'], topics: index === 0 ? ['apk'] : [], category, group: 'tools', kind: 'tool',
  relationship: 'foundation', requirements: ['A fixture'], requirements_zh: ['测试条件'], verified_at: '2026-01-01', scan_status: 'readme-scanned', stars: index}));

function application(query, pathname = '/') {
  const app = setup(query, {pathname, records: rows});
  app.replacements = [];
  const replace = app.context.history.replaceState;
  app.context.history.replaceState = (...args) => { app.replacements.push(String(args[2])); replace(...args); };
  const fetch = app.context.fetch;
  app.context.fetch = async url => {
    const response = await fetch(url);
    if (new URL(url).pathname !== '/catalog.json') return response;
    const data = await response.json();
    return {ok: true, json: async () => ({...data, source_category_labels: LABELS})};
  };
  return app;
}
const param = (app, key) => new URL(app.context.location.href).searchParams.get(key);
const ids = app => app.api.sourceFiltered().map(record => record.id);
const settle = () => new Promise(resolve => setImmediate(resolve));

(async () => {
  for (const [language, pathname, query] of [['en', '/', '?view=source-index&lang=en&source-category=android'], ['zh', '/zh/', '?view=source-index&source-category=android']]) {
    const app = application(query, pathname);
    await app.api.load(); await settle();
    assert.equal(app.api.sourceState.mode, 'source-index');
    assert.equal(app.api.sourceState.category, 'android');
    assert.deepEqual(ids(app), ['scan-5', 'scan-2', 'scan-1', 'scan-0'], 'a category-page link opens that category');
    assert.equal(param(app, 'source-category'), 'android');
    const select = app.elements.get('#source-category');
    assert.equal(select.value, 'android');
    // Options are the categories in use, labelled in the page language; the unused Games category is left out.
    assert.deepEqual(select.children.map(option => option.value), ['all', 'web-analysis', 'android', 'firmware']);
    assert.deepEqual(select.children.slice(1).map(option => option.textContent), language === 'zh' ? ['网站', '应用 · Android', '固件'] : ['Websites', 'Apps · Android', 'Firmware']);
    assert.equal(app.elements.get('#source-clear').hidden, false);

    // Category combines with the query, target, topic and sort.
    const input = (selector, value, event = 'input') => { app.elements.get(selector).value = value; app.elements.get(selector).emit(event); };
    input('#source-search', 'decompiler');
    assert.deepEqual(ids(app), ['scan-1']);
    input('#source-search', '');
    app.buttons.find(button => button.dataset.sourceTarget === 'firmware').emit('click');
    assert.deepEqual(ids(app), ['scan-2']);
    app.buttons.find(button => button.dataset.sourceTarget === 'all').emit('click');
    input('#source-topic', 'apk');
    assert.deepEqual(ids(app), ['scan-0']);
    input('#source-topic', '');
    input('#source-sort', 'name', 'change');
    assert.deepEqual(ids(app), ['scan-0', 'scan-1', 'scan-2', 'scan-5']);
    assert.equal(param(app, 'sort'), 'name');
    assert.equal(param(app, 'source-category'), 'android');

    // Changing the category resets paging, updates the URL and leaves every record's classification alone.
    app.api.sourceState.visible = 72;
    input('#source-category', 'firmware', 'change');
    assert.equal(app.api.sourceState.visible, 24);
    assert.deepEqual(ids(app), ['scan-3']);
    assert.equal(param(app, 'source-category'), 'firmware');
    assert.deepEqual(app.api.sourceState.records.map(record => record.category), categories);
    // It clears on its own, and with Clear filters.
    input('#source-category', 'all', 'change');
    assert.equal(param(app, 'source-category'), null);
    assert.equal(ids(app).length, rows.length);
    input('#source-category', 'web-analysis', 'change');
    app.elements.get('#source-clear').emit('click');
    assert.equal(app.api.sourceState.category, 'all');
    assert.equal(select.value, 'all');
    assert.equal(param(app, 'source-category'), null);
    assert.equal(param(app, 'sort'), null);
    // The curated view's own Category filter is untouched.
    assert.equal(app.api.state.category, 'all');
  }

  // Unknown or malformed categories fall back to all, normalizing the URL once, alongside other rejected values.
  for (const value of ['bogus', '__proto__', 'constructor', 'android/../firmware', '']) {
    const app = application(`?view=source-index&source-category=${encodeURIComponent(value)}&keep=1`);
    await app.api.load(); await settle();
    assert.equal(app.api.sourceState.category, 'all', value);
    assert.equal(param(app, 'source-category'), null);
    assert.equal(param(app, 'keep'), '1');
    assert.equal(ids(app).length, rows.length);
  }
  // Shared URLs without the parameter keep their exact form.
  const plain = application('?view=source-index&sourceq=tool&sort=stars');
  await plain.api.load(); await settle();
  assert.equal(plain.replacements.length, 0);
  assert.equal(plain.api.sourceState.category, 'all');
  // A catalog without labels (an older build) simply offers no category choices.
  const older = setup('?view=source-index&source-category=android', {records: rows});
  await older.api.load(); await settle();
  assert.equal(older.api.sourceState.category, 'all');
  console.log('Repository category checks passed');
})().catch(error => { console.error(error); process.exit(1); });
