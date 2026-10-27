/* Curated search ranks matches by the field a query term occurs in, without changing which records match. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {setup} = require('./protocol_target_ui.cjs');
const read = name => JSON.parse(fs.readFileSync(path.resolve(__dirname, '..', name), 'utf8'));

function record(id, changes = {}) {
  return {id, name: id, name_zh: '', url: 'https://example.com/' + id, evidence_url: 'https://example.com/' + id,
    description_en: 'A fixture.', description_zh: '测试条目。', category: 'fixtures', group: 'tools', kind: 'tool',
    relationship: 'foundation', targets: ['app'], requirements: ['Nothing.'], requirements_zh: ['无。'], verified_at: '2026-01-01', ...changes};
}
async function application(records, {pathname = '/', categoryLabels = {}} = {}) {
  const app = setup('', {pathname, records});
  const fetch = app.context.fetch;
  app.context.fetch = async (...args) => {
    const data = await (await fetch(...args)).json();
    return {ok: true, json: async () => ({...data, category_labels: categoryLabels})};
  };
  app.api.applyLanguage(); await app.api.load();
  return app;
}
function search(app, query) {
  app.api.state.q = query;
  const found = app.api.filtered();
  // Ranking only orders: the results are exactly the records that contain every term.
  const terms = query.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
  assert.equal(found.length, app.api.state.records.filter(record => terms.every(term => record.search.includes(term))).length, query);
  return Array.from(found, record => record.id);
}

const tests = {
  async english() {
    // Catalog order is the reverse of the expected ranking, and the featured Ghidra ID matches only in its requirements.
    const app = await application([
      record('ghidra', {requirements: ['Optional Ninja export.']}),
      record('requirement-only', {requirements: ['Reads Ninja databases.']}),
      record('label-match', {category: 'ninja-tools'}),
      record('description-match', {description_en: 'Imports Ninja projects.'}),
      record('inside-name', {name: 'Codeninja Kit'}),
      record('name-start', {name: 'Ninja Inspector Pro'}),
      record('whole-name', {name: 'NinjaInspector'}),
      record('unrelated'),
    ], {categoryLabels: {'ninja-tools': ['Ninja tools', '忍者工具']}});
    assert.deepEqual(search(app, 'ninja'), ['name-start', 'whole-name', 'inside-name', 'description-match', 'label-match', 'ghidra', 'requirement-only']);
    // Both words at word starts outrank one inside a word, but a query that is the whole name, spaces aside, leads.
    assert.deepEqual(search(app, 'ninja inspector'), ['whole-name', 'name-start']);
    assert.deepEqual(search(app, 'NINJA   inspector pro'), ['name-start']);
    // Without a query, featured entries lead, then kinds, then catalog order.
    assert.deepEqual(search(app, ''), ['ghidra', 'requirement-only', 'label-match', 'description-match', 'inside-name', 'name-start', 'whole-name', 'unrelated']);
    assert.deepEqual(search(app, '   '), search(app, ''));
  },
  async chinese() {
    const app = await application([
      record('ghidra', {requirements_zh: ['需要先完成反编译。']}),
      record('description-match', {description_zh: '整理反编译结果。'}),
      record('inside-name', {name: 'Scripthelper'}),
      record('name-match', {name: 'Decompiler Helper', name_zh: 'Decompiler Helper 反编译助手'}),
      record('unrelated'),
    ], {pathname: '/zh/'});
    assert.equal(app.api.state.lang, 'zh');
    assert.deepEqual(search(app, '反编译'), ['name-match', 'description-match', 'ghidra']);
    // English names still rank in the Chinese interface, and a word-start match beats one inside a word.
    assert.deepEqual(search(app, 'helper'), ['name-match', 'inside-name']);
  },
  async catalog() {
    // The published catalog: entries named after the query lead on both homepages, and no match is lost.
    const localizations = read('site/translations.zh-CN.json');
    const records = [...read('data/rea-resources.json'), ...read('data/tool-resources.json')].map(record => ({...record,
      name_zh: localizations[record.id]?.name || record.name, requirements_zh: localizations[record.id]?.requirements || record.requirements}));
    for (const pathname of ['/', '/zh/']) {
      const app = await application(records, {pathname});
      const top = (query, count) => search(app, query).slice(0, count);
      for (const id of ['binary-ninja-api', 'binary-ninja-official-mcp', 'binary-ninja-community-mcp']) assert(top('binary ninja', 5).includes(id), `${pathname} ${id}`);
      assert(top('ghidra mcp', 3).includes('ghidramcp'), pathname);
      assert.equal(top('n64', 1)[0], 'n64recomp', pathname);
      const debuggers = search(app, 'dbg');
      assert(['x64dbg', 'pwndbg', 'decomp2dbg'].every(id => debuggers.includes(id)), pathname);
    }
  },
};

(async () => {
  const selected = process.argv.slice(2);
  for (const name of selected.length ? selected : Object.keys(tests)) {
    assert(tests[name], 'Unknown test group ' + name);
    await tests[name]();
    process.stdout.write('Curated search ranking passed: ' + name + '\n');
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
