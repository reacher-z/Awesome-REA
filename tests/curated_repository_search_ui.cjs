/* Curated search finds entries by the GitHub owner/repo of their URL or primary source, without showing it. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {setup} = require('./protocol_target_ui.cjs');
const read = name => JSON.parse(fs.readFileSync(path.resolve(__dirname, '..', name), 'utf8'));

function record(id, changes = {}) {
  return {id, name: id, name_zh: id, url: 'https://example.com/' + id, evidence_url: 'https://example.com/' + id + '/docs',
    description_en: 'A fixture.', description_zh: '测试条目。', category: 'fixtures', group: 'tools', kind: 'tool',
    relationship: 'foundation', targets: ['app'], requirements: ['Nothing.'], requirements_zh: ['无。'], verified_at: '2026-01-01', ...changes};
}
async function application(records, pathname = '/') {
  const app = setup('', {pathname, records});
  app.api.applyLanguage(); await app.api.load();
  return app;
}
const search = (app, query) => { app.api.state.q = query; return Array.from(app.api.filtered(), record => record.id); };
const texts = node => [node.textContent || '', ...node.children.flatMap(texts)];

const tests = {
  async fixtures() {
    for (const pathname of ['/', '/zh/']) {
      const app = await application([
        record('hosted', {url: 'https://github.com/Owner-Org/Tool-One.git', evidence_url: 'https://github.com/Owner-Org/Tool-One/blob/main/README.md'}),
        record('documented', {url: 'https://tool-two.example/', evidence_url: 'https://github.com/owner-org/tool-two/tree/v1#readme'}),
        record('elsewhere', {url: 'https://gitlab.com/owner-org/tool-three', evidence_url: 'https://www.example.org/owner-org'}),
        record('profile', {url: 'https://github.com/owner-org', evidence_url: 'https://github.com/owner-org'}),
      ], pathname);
      // An owner query finds each entry hosted under it or citing one of its repositories as the primary source.
      assert.deepEqual(search(app, 'owner-org'), ['hosted', 'documented'], pathname);
      assert.deepEqual(search(app, 'OWNER-ORG/tool-one'), ['hosted'], pathname);
      assert.deepEqual(search(app, 'owner-org/tool-two'), ['documented'], pathname);
      // Only the owner/repo is added: no host, file path, fragment or non-GitHub address becomes searchable.
      for (const query of ['github', 'github.com', 'readme', 'blob', 'gitlab', 'tool-three', 'tool-one.git']) assert.deepEqual(search(app, query), [], `${pathname} ${query}`);
      const hosted = app.api.state.records.find(entry => entry.id === 'hosted');
      assert.equal(hosted.search.split('owner-org/tool-one').length, 2, 'A repository shared by URL and source is added once');
      // Cards show no repository path, and the loaded records keep the catalog's own fields.
      app.api.state.q = ''; app.api.applyLanguage();
      const shown = app.elements.get('#resource-grid').children.flatMap(texts).join(' ');
      assert.doesNotMatch(shown.toLowerCase(), /owner-org/, pathname);
      assert.deepEqual(Object.keys(hosted).sort(), [...Object.keys(record('hosted')), 'order', 'search'].sort());
    }
  },
  async catalog() {
    // The published catalog: owner and owner/repo queries reach the curated entries hosted there on both homepages.
    const localizations = read('site/translations.zh-CN.json');
    const records = [...read('data/rea-resources.json'), ...read('data/tool-resources.json')].map(record => ({...record,
      name_zh: localizations[record.id]?.name || record.name, requirements_zh: localizations[record.id]?.requirements || record.requirements}));
    const zeldaret = records.filter(record => /^https:\/\/github\.com\/zeldaret\//i.test(record.url)).map(record => record.id);
    assert(zeldaret.length >= 7, 'The catalog keeps its zeldaret decompilations');
    for (const pathname of ['/', '/zh/']) {
      const app = await application(records, pathname);
      const owner = search(app, 'zeldaret');
      assert(zeldaret.every(id => owner.includes(id)), pathname);
      assert(search(app, 'x64dbg/x64dbg').includes('x64dbg'), pathname);
    }
  },
};

(async () => {
  const selected = process.argv.slice(2);
  for (const name of selected.length ? selected : Object.keys(tests)) {
    assert(tests[name], 'Unknown test group ' + name);
    await tests[name]();
    process.stdout.write('Curated repository search passed: ' + name + '\n');
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
