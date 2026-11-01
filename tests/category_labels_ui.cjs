/* Homepage category labels come from catalog.json, which build_site.py fills from build_readme.CATEGORIES. */
const assert = require('node:assert/strict');
const path = require('node:path');
const {execFileSync} = require('node:child_process');
const {setup} = require('./protocol_target_ui.cjs');

const labels = JSON.parse(execFileSync('python3', ['-c', 'import json, build_readme; print(json.dumps(build_readme.CATEGORIES))'],
  {cwd: path.join(__dirname, '../scripts'), encoding: 'utf8'}));
const record = (id, category) => ({id, name: id, name_zh: id, url: 'https://github.com/fixture/' + id, evidence_url: 'https://github.com/fixture/' + id + '#readme',
  description_en: 'Fixture', description_zh: '测试', targets: ['app'], topics: [], category, group: 'tools', kind: 'tool', relationship: 'foundation',
  requirements: ['Requirement'], requirements_zh: ['条件'], verified_at: '2026-01-01'});
const rows = [record('one', 'jvm'), record('two', 'agent-mcp'), record('three', 'core'), record('four', 'reconstruction-cases')];
const descendants = node => node.children.flatMap(child => [child, ...descendants(child)]);

async function loaded(lang, categoryLabels) {
  const app = setup(`?view=curated&lang=${lang}`);
  const catalog = {resources: rows, topic_labels: {}, meta: {repository_url: 'https://github.com/reacher-z/Awesome-REA', source_index: {resource_count: 0}}};
  if (categoryLabels) catalog.category_labels = categoryLabels;
  app.context.fetch = async () => ({ok: true, json: async () => catalog});
  await app.api.load(); app.api.applyLanguage();
  const options = app.elements.get('#category-select').children.slice(1);
  const cards = app.elements.get('#resource-grid').children;
  const cardLabels = Object.fromEntries(cards.map(card => [card.dataset.recordId, descendants(card).find(node => node.className === 'card-category').textContent]));
  return {options: options.map(option => [option.value, option.textContent]), cardLabels};
}

(async () => {
  for (const [lang, index] of [['en', 0], ['zh', 1]]) {
    const {options, cardLabels} = await loaded(lang, labels);
    // The filter, every card and the entry pages (build_entry_pages.py) show the same wording.
    for (const row of rows) assert.equal(cardLabels[row.id], labels[row.category][index]);
    // Each option also shows its live result count (one record per category here).
    const counted = text => lang === 'zh' ? `${text}（1）` : `${text} (1)`;
    assert.deepEqual(new Map(options), new Map(rows.map(row => [row.category, counted(labels[row.category][index])])));
    const collator = new Intl.Collator(lang === 'zh' ? 'zh-CN' : 'en');
    assert.deepEqual(options.map(([, text]) => text), options.map(([, text]) => text).sort(collator.compare));
  }
  // A catalog without the map still renders, falling back to the category ID.
  const {cardLabels} = await loaded('en', null);
  assert.equal(cardLabels.two, 'agent mcp');
  process.stdout.write('Category labels follow the catalog map in both languages\n');
})().catch(error => { console.error(error); process.exitCode = 1; });
