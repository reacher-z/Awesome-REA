/* The homepage renders from the lean catalog index, then fills requirement text from the complete catalog. */
const assert = require('node:assert/strict');
const {setup} = require('./protocol_target_ui.cjs');
const settle = async () => { for (let i = 0; i < 5; i++) await new Promise(resolve => setImmediate(resolve)); };

const rows = Array.from({length: 20}, (_, index) => ({id: 'fixture-' + index, name: 'Fixture ' + index, name_zh: '测试 ' + index,
  url: 'https://github.com/Fixture/project' + index, evidence_url: 'https://github.com/Fixture/project' + index + '#readme',
  description_en: 'Fixture ' + index, description_zh: '测试 ' + index, targets: ['app'], category: 'dynamic-analysis', group: 'tools',
  kind: 'tool', relationship: 'foundation', verified_at: '2026-01-01',
  requirements: index === 17 ? ['Builds with Turbopack.', 'Node.js 22.'] : ['Requirement ' + index],
  requirements_zh: index === 17 ? ['使用 Turbopack 构建。', 'Node.js 22。'] : ['条件 ' + index],
  ...(index === 18 ? {requirements: ['Author-reported results.', 'Bring your own ROM.'], requirements_zh: ['作者报告的结果。', '自备 ROM。'],
                      requirement_facets: ['testing', 'prerequisites']} : {})}));
const meta = {repository_url: 'https://github.com/reacher-z/Awesome-REA', source_index: {resource_count: 0}};
const lean = rows.map(({requirements, requirements_zh, requirement_facets, ...record}) => record);

function application({fail = 0} = {}) {
  const app = setup('', {records: rows});
  let release; app.release = () => release();
  const gate = new Promise(resolve => { release = resolve; });
  app.context.fetch = async url => {
    app.requests.push(String(url));
    const pathname = new URL(url).pathname;
    if (pathname === '/catalog-index.json') return {ok: true, json: async () => structuredClone({resources: lean, meta, topic_labels: {}})};
    assert.equal(pathname, '/catalog.json', 'the homepage requests only its two catalog files here');
    await gate;
    if (fail-- > 0) return {ok: false, status: 503};
    return {ok: true, json: async () => structuredClone({resources: rows, meta, topic_labels: {}})};
  };
  app.api.applyLanguage();
  app.grid = () => app.elements.get('#resource-grid').children;
  app.paths = () => app.requests.map(url => new URL(url).pathname);
  return app;
}
const details = card => card.children.find(child => child.tag === 'details');
const items = card => details(card).children.find(child => child.tag === 'ul').children.map(item => [item.className, item.textContent]);

(async () => {
  // First render: 15 cards from the index, the complete catalog requested once right after.
  const app = application();
  await app.api.load();
  assert.equal(app.grid().length, 15);
  assert.deepEqual(app.paths(), ['/catalog-index.json', '/catalog.json']);
  const first = app.grid()[0];
  assert.deepEqual(items(first), [['requirements-pending', 'Loading requirements…']]);
  // Opening details while the catalog is in flight reuses that request.
  details(first).open = true; details(first).emit('toggle');
  assert.deepEqual(app.paths(), ['/catalog-index.json', '/catalog.json']);
  // A requirement-only term finds nothing in the index, then the record once the catalog arrives.
  const search = app.elements.get('#search-input');
  search.value = 'turbopack'; search.emit('input');
  assert.equal(app.grid().length, 0);
  search.value = ''; search.emit('input');
  const reopened = app.grid()[0]; details(reopened).open = true;
  // Show more appends the next batch before the catalog arrives; earlier cards keep their pending lists.
  app.elements.get('#load-more').emit('click');
  assert.equal(app.grid().length, 20); assert.equal(app.grid()[0], reopened);
  app.release(); await settle();
  assert.deepEqual(items(app.grid()[15]), [['', 'Requirement 15']]);
  // Without a query the open card is filled in place: same element, still open, no re-render.
  assert.equal(app.grid()[0], reopened);
  assert.equal(details(reopened).open, true);
  assert.deepEqual(items(reopened), [['', 'Requirement 0']]);
  assert.deepEqual(app.paths(), ['/catalog-index.json', '/catalog.json']);
  search.value = 'turbopack'; search.emit('input');
  assert.deepEqual(app.grid().map(card => card.dataset.recordId), ['fixture-17']);
  assert.deepEqual(items(app.grid()[0]), [['', 'Builds with Turbopack.'], ['', 'Node.js 22.']]);
  app.api.state.lang = 'zh'; app.api.applyLanguage();
  assert.deepEqual(items(app.grid()[0]), [['', '使用 Turbopack 构建。'], ['', 'Node.js 22。']]);
  assert.deepEqual(app.paths(), ['/catalog-index.json', '/catalog.json'], 'the complete catalog is fetched once');
  // requirement_facets arrive with the complete catalog too, so faceted items render with their lead-ins.
  search.value = '18'; search.emit('input');
  const descendants = node => [node, ...node.children.flatMap(descendants)];
  const facets = descendants(details(app.grid()[0])).filter(node => node.className === 'requirement-facet');
  assert.deepEqual(facets.map(node => node.textContent), ['前提条件：', '测试证据：']);

  // A query typed before the catalog arrives is re-run against the requirement text.
  const early = application();
  await early.api.load();
  const earlySearch = early.elements.get('#search-input');
  earlySearch.value = 'Turbopack'; earlySearch.emit('input');
  assert.equal(early.grid().length, 0);
  early.release(); await settle();
  assert.deepEqual(early.grid().map(card => card.dataset.recordId), ['fixture-17']);
  assert.equal(early.elements.get('#results-status').textContent, '1 result · 20 resources');

  // A failed catalog request says so in pending details; reopening them retries once.
  const failing = application({fail: 1});
  await failing.api.load();
  failing.release(); await settle();
  const card = failing.grid()[2];
  assert.deepEqual(items(card), [['requirements-pending', 'Requirements couldn’t load. Close and reopen these details to try again.']]);
  details(card).open = true; details(card).emit('toggle');
  assert.deepEqual(failing.paths(), ['/catalog-index.json', '/catalog.json', '/catalog.json']);
  assert.deepEqual(items(card), [['requirements-pending', 'Loading requirements…']]);
  await settle();
  assert.deepEqual(items(card), [['', 'Requirement 2']]);
  details(card).emit('toggle');
  assert.equal(failing.paths().length, 3, 'a loaded catalog is not requested again');
  console.log('Lean catalog index: first render, in-place requirements, requirement search and retry passed.');
})().catch(error => { console.error(error); process.exitCode = 1; });
