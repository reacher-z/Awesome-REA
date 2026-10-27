/* Filtered JSON exports hold every match in display order, keep records unchanged and explain empty or failed exports. */
const assert = require('node:assert/strict');
const {setup} = require('./protocol_target_ui.cjs');

const rows = Array.from({length: 40}, (_, index) => ({id: `fixture-${index}`, name: `Fixture ${index}`, name_zh: `测试 ${index}`,
  full_name: `Fixture/project${index}`, url: `https://github.com/Fixture/project${index}`, evidence_url: `https://github.com/Fixture/project${index}`,
  description_en: index % 2 ? 'Odd decompiler fixture' : 'Even fixture', description_zh: '测试说明', targets: [index % 4 ? 'app' : 'game'],
  topics: ['fixtures'], category: 'dynamic-analysis', group: 'tools', kind: 'tool', relationship: 'foundation', requirements: ['A fixture'],
  requirements_zh: ['测试条件'], verified_at: '2026-01-01', verification: 'source-reviewed', scan_status: 'readme-scanned', stars: index}));

function application(query, pathname = '/') {
  const app = setup(query, {pathname, records: rows});
  const downloads = []; const revoked = [];
  let failure = false;
  app.context.URL = class extends URL {
    static createObjectURL(blob) { if (failure) throw new Error('Blob URLs unavailable'); downloads.push({blob}); return `blob:fixture/${downloads.length}`; }
    static revokeObjectURL(href) { revoked.push(href); }
  };
  app.context.Blob = class { constructor(parts, options) { this.text = parts.join(''); this.type = options.type; } };
  app.context.setTimeout = callback => callback();
  const createElement = app.context.document.createElement;
  app.context.document.createElement = tag => {
    const element = createElement(tag);
    if (tag === 'a') { element.click = () => { downloads[downloads.length - 1].link = element; }; element.remove = () => { element.removed = true; }; }
    return element;
  };
  app.context.document.body = {append() {}};
  app.downloads = downloads; app.revoked = revoked; app.fail = value => { failure = value; };
  app.click = selector => app.elements.get(selector).emit('click');
  app.status = selector => app.elements.get(selector).textContent;
  app.exported = () => JSON.parse(downloads[downloads.length - 1].blob.text);
  return app;
}

(async () => {
  for (const [language, pathname] of [['en', '/'], ['zh', '/zh/']]) {
    const app = application('?target=app&q=decompiler', pathname);
    assert.equal(app.elements.get('#export-matches').hidden, undefined, 'app.js reveals the button only after the catalog loads');
    await app.api.load(); await app.api.state.details;
    assert.equal(app.elements.get('#export-matches').hidden, false);
    const found = app.api.filtered();
    assert.equal(found.length, 20);
    assert.equal(app.elements.get('#resource-grid').children.length, 15, 'Show More has not revealed every match');
    app.click('#export-matches');
    assert.equal(app.downloads.length, 1);
    const {link} = app.downloads[0];
    assert.equal(link.download, 'awesomerea-curated-matches.json');
    assert.equal(link.removed, true);
    assert.deepEqual(app.revoked, [link.href]);
    assert.equal(app.downloads[0].blob.type, 'application/json');
    const data = app.exported();
    assert.deepEqual(data.resources.map(record => record.id), found.map(record => record.id), 'every match, in displayed order');
    // Records are the catalog rows themselves: no browser-only fields, nothing added or changed.
    assert.deepEqual(data.resources, found.map(record => rows.find(row => row.id === record.id)));
    assert(app.api.state.records.every(record => typeof record.search === 'string' && Number.isInteger(record.order)), 'loaded records are not mutated');
    assert.equal(data.export.collection, 'curated-catalog');
    assert.equal(data.export.record_class, 'curated-resource');
    assert.equal(data.export.subset, 'filtered');
    assert.deepEqual(data.export.filters, {q: 'decompiler', target: 'app', kind: 'all', category: 'all', group: 'all'});
    assert.equal(data.export.order, 'displayed');
    assert.equal(data.export.matched_count, 20);
    assert.equal(data.export.total_count, 40);
    assert.equal(data.export.language, language);
    assert.equal(new URL(data.export.page).searchParams.get('target'), 'app');
    assert.equal(new URL(data.export.full_download).pathname, '/catalog.json');
    assert.equal(app.status('#export-matches-status'), language === 'zh' ? '已下载 20 项匹配资源（JSON）。' : 'Downloaded 20 matching resources as JSON.');
    // The next render (here a filter change) clears the message; an empty result explains why nothing downloads.
    app.elements.get('#search-input').value = 'no such fixture'; app.elements.get('#search-input').emit('input');
    assert.equal(app.status('#export-matches-status'), '');
    app.click('#export-matches');
    assert.equal(app.downloads.length, 1);
    assert.equal(app.status('#export-matches-status'), language === 'zh' ? '没有可导出的匹配资源。' : 'No matching resources to export.');
    app.api.reset();
    app.fail(true); app.click('#export-matches');
    assert.equal(app.downloads.length, 1);
    assert.match(app.status('#export-matches-status'), language === 'zh' ? /无法生成导出文件.*精选目录 JSON/ : /couldn’t create the export\. The full curated catalog JSON/);
    app.fail(false);

    // Repository exports use the same order as the cards and describe the automatic, uncurated records.
    await app.api.loadSources(); app.api.setIndexMode('source-index');
    assert.equal(app.elements.get('#source-export-matches').hidden, false);
    app.elements.get('#source-sort').value = 'stars'; app.elements.get('#source-sort').emit('change');
    app.elements.get('#source-search').value = 'odd'; app.elements.get('#source-search').emit('input');
    const repositories = app.api.sourceFiltered();
    assert.equal(repositories.length, 20);
    assert.equal(app.elements.get('#source-results').children.length, 20);
    app.click('#source-export-matches');
    assert.equal(app.downloads.length, 2);
    assert.equal(app.downloads[1].link.download, 'awesomerea-repository-matches.json');
    const index = app.exported();
    assert.deepEqual(index.repositories.map(record => record.id), repositories.map(record => record.id));
    assert.deepEqual(index.repositories.map(record => record.stars), [...index.repositories.map(record => record.stars)].sort((a, b) => b - a));
    assert(index.repositories.every(record => !('search' in record) && !('order' in record)));
    assert.equal(index.resources, undefined, 'repository exports never present records as curated resources');
    assert.equal(index.export.collection, 'repository-index');
    assert.equal(index.export.record_class, 'automatically-indexed-repository');
    assert.match(index.export.description, /not curated, individually reviewed or executed/);
    assert.match(index.export.description, /excluded from browsing are omitted/);
    assert.deepEqual(index.export.filters, {sourceq: 'odd', 'source-target': 'all', topic: '', sort: 'stars'});
    assert.equal(index.export.order, 'stars');
    assert.equal(index.export.matched_count, 20);
    assert.equal(index.export.total_count, 40);
    assert.deepEqual(index.export.snapshot.scope, {scanned_count: 40, excluded_count: 0, browse_count: 40});
    assert.equal(index.export.snapshot.full_export_sha256, 'a'.repeat(64));
    assert.equal(new URL(index.export.full_download).pathname, '/source-index.json');
    assert.equal(app.status('#source-export-matches-status'), language === 'zh' ? '已下载 20 个匹配仓库（JSON）。' : 'Downloaded 20 matching repositories as JSON.');
    app.elements.get('#source-search').value = 'no such fixture'; app.elements.get('#source-search').emit('input');
    app.click('#source-export-matches');
    assert.equal(app.downloads.length, 2);
    assert.equal(app.status('#source-export-matches-status'), language === 'zh' ? '没有可导出的匹配仓库。' : 'No matching repositories to export.');
  }

  // A catalog that failed to load keeps the button hidden; the existing full downloads are untouched.
  const failed = application('');
  failed.context.fetch = async () => ({ok: false, status: 503});
  await failed.api.load();
  assert.equal(failed.elements.get('#export-matches').hidden, undefined);
  failed.click('#export-matches');
  assert.equal(failed.downloads.length, 0);
  assert.equal(new URL(failed.elements.get('#download-curated-catalog').href).pathname, '/catalog.json');
  // Cards render from the lean catalog-index.json; the export waits for and copies the complete catalog.json records.
  const settle = async () => { for (let i = 0; i < 5; i++) await new Promise(resolve => setImmediate(resolve)); };
  const full = rows.map(row => ({...row, additional_evidence_urls: [row.url + '#notes']}));
  const leanRows = full.map(({requirements, requirements_zh, additional_evidence_urls, ...row}) => row);
  for (const fail of [false, true]) {
    const lean = application('?target=app&q=decompiler');
    let release; const gate = new Promise(resolve => { release = resolve; });
    lean.context.fetch = async url => {
      const meta = {repository_url: 'https://github.com/reacher-z/Awesome-REA', source_index: {resource_count: 0}};
      if (new URL(url).pathname === '/catalog-index.json') return {ok: true, json: async () => ({resources: leanRows, meta, topic_labels: {}})};
      await gate; return fail ? {ok: false, status: 503} : {ok: true, json: async () => ({resources: full, meta, topic_labels: {}})};
    };
    await lean.api.load();
    lean.click('#export-matches');
    assert.equal(lean.downloads.length, 0);
    assert.equal(lean.status('#export-matches-status'), 'Loading the complete catalog…');
    release(); await settle();
    if (fail) {
      assert.equal(lean.downloads.length, 0);
      assert.equal(lean.status('#export-matches-status'), 'The complete catalog couldn’t load, so nothing was exported. The full curated catalog JSON in the footer still works.');
    } else {
      assert.equal(lean.downloads.length, 1);
      assert.deepEqual(lean.exported().resources, lean.api.filtered().map(record => full.find(row => row.id === record.id)));
      assert(lean.exported().resources.every(record => record.additional_evidence_urls && record.requirements));
    }
  }
  console.log('Filtered export checks passed');
})().catch(error => { console.error(error); process.exit(1); });
