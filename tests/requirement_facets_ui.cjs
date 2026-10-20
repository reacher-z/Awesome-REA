/* Homepage details lead each faceted requirement with its localized facet and list prerequisites first. */
const assert = require('node:assert/strict');
const {setup} = require('./protocol_target_ui.cjs');

const record = (id, changes = {}) => ({id, name: id, name_zh: id, url: 'https://github.com/fixture/' + id, evidence_url: 'https://github.com/fixture/' + id + '#readme',
  description_en: 'Fixture', description_zh: '测试', targets: ['app'], topics: [], category: 'reconstruction-cases', group: 'tools', kind: 'case-study',
  relationship: 'independent-reconstruction', requirements: ['Requirement'], requirements_zh: ['条件'], verified_at: '2026-01-01', ...changes});
const rows = [
  record('faceted', {requirements: ['Author-reported results.', 'Bring your own ROM.'], requirements_zh: ['作者报告的结果。', '自备 ROM。'], requirement_facets: ['testing', 'prerequisites']}),
  record('plain'),
];
const descendants = node => node.children.flatMap(child => [child, ...descendants(child)]);
const text = node => node.children.length ? node.children.map(text).join('') : String(node.textContent ?? '');

(async () => {
  for (const lang of ['en', 'zh']) {
    const app = setup(`?view=curated&lang=${lang}`);
    app.context.fetch = async () => ({ok: true, json: async () => ({resources: rows, topic_labels: {}, meta: {repository_url: 'https://github.com/reacher-z/Awesome-REA', source_index: {resource_count: 0}}})});
    await app.api.load(); app.api.applyLanguage();
    const cards = Object.fromEntries(app.elements.get('#resource-grid').children.map(card => [card.dataset.recordId, card]));
    const items = card => descendants(descendants(card).find(node => node.tag === 'details')).filter(node => node.tag === 'li').map(text);
    assert.deepEqual(items(cards.faceted), lang === 'zh' ? ['前提条件：自备 ROM。', '测试证据：作者报告的结果。'] : ['Prerequisites: Bring your own ROM.', 'Testing evidence: Author-reported results.']);
    assert.equal(descendants(cards.faceted).filter(node => node.className === 'requirement-facet').length, 2);
    // Records without requirement_facets keep the plain list.
    assert.deepEqual(items(cards.plain), [lang === 'zh' ? '条件' : 'Requirement']);
    assert.equal(descendants(cards.plain).filter(node => node.className === 'requirement-facet').length, 0);
  }
  process.stdout.write('Requirement facets render on homepage cards in both languages\n');
})().catch(error => { console.error(error); process.exitCode = 1; });
