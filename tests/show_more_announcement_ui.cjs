/* Show More announces how many results it added and how many now show, without repeating the unchanged total. */
const assert = require('node:assert/strict');
const {setup} = require('./protocol_target_ui.cjs');

const rows = Array.from({length: 40}, (_, index) => ({id: `fixture-${index}`, name: `Fixture ${index}`, name_zh: `测试 ${index}`,
  full_name: `Fixture/project${index}`, url: `https://github.com/Fixture/project${index}`, evidence_url: `https://github.com/Fixture/project${index}`,
  description_en: index < 35 ? 'Odd fixture' : 'Even fixture', description_zh: '测试说明', targets: ['app'], topics: [], category: 'dynamic-analysis',
  group: 'tools', kind: 'tool', relationship: 'foundation', requirements: ['A fixture'], requirements_zh: ['测试条件'], verified_at: '2026-01-01',
  scan_status: 'readme-scanned', stars: index}));

// Count every write to a live status line, as a screen reader would hear each replacement.
function watch(element) {
  let value = '';
  element.writes = 0;
  Object.defineProperty(element, 'textContent', {get: () => value, set: next => { element.writes++; value = next; }});
  return element;
}

(async () => {
  for (const [language, pathname] of [['en', '/'], ['zh', '/zh/']]) {
    const app = setup('', {pathname, records: rows});
    const status = watch(app.context.document.querySelector('#results-status'));
    const more = watch(app.context.document.querySelector('#more-status'));
    await app.api.load();
    const total = language === 'zh' ? '40 项资源' : '40 resources';
    assert.equal(status.textContent, total);
    assert.equal(more.textContent, '', 'the first render announces only the total');
    const statusWrites = status.writes;
    const button = app.elements.get('#load-more');
    button.emit('click');
    assert.equal(app.elements.get('#resource-grid').children.length, 30);
    assert.equal(more.textContent, language === 'zh' ? '又显示 15 项资源，已显示 30 / 40 项。' : '15 more resources shown: 30 of 40.');
    assert.equal(status.writes, statusWrites, 'the unchanged total is not written again');
    // The final, partial page reports what it actually added.
    button.emit('click');
    assert.equal(more.textContent, language === 'zh' ? '又显示 10 项资源，已显示 40 / 40 项。' : '10 more resources shown: 40 of 40.');
    assert.equal(status.writes, statusWrites);
    assert.equal(app.elements.get('#load-more-row').hidden, true);
    // Filtering announces the new match count once and clears the pagination message.
    const input = app.elements.get('#search-input');
    input.value = 'odd'; input.emit('input');
    assert.equal(status.textContent, language === 'zh' ? '35 项匹配资源 · 目录共 40 项' : '35 results · 40 resources');
    assert.equal(status.writes, statusWrites + 1);
    assert.equal(more.textContent, '');
    button.emit('click');
    assert.equal(more.textContent, language === 'zh' ? '又显示 15 项资源，已显示 30 / 35 项。' : '15 more resources shown: 30 of 35.');
    // Changing the query after paging starts again from the first page without a pagination message.
    input.value = 'fixture'; input.emit('input');
    assert.equal(more.textContent, '');
    assert.equal(app.elements.get('#resource-grid').children.length, 15);

    // The repository view follows the same rules with its own status lines.
    const sourceStatus = watch(app.context.document.querySelector('#source-status'));
    const sourceMore = watch(app.context.document.querySelector('#source-more-status'));
    await app.api.loadSources(); app.api.setIndexMode('source-index');
    assert.equal(sourceMore.textContent, '');
    const sourceWrites = sourceStatus.writes;
    app.elements.get('#source-more').emit('click');
    assert.equal(app.elements.get('#source-results').children.length, 40);
    assert.equal(sourceMore.textContent, language === 'zh' ? '又显示 16 个仓库，已显示 40 / 40 个。' : '16 more repositories shown: 40 of 40.');
    assert.equal(sourceStatus.writes, sourceWrites);
    const sort = app.elements.get('#source-sort');
    sort.value = 'stars'; sort.emit('change');
    assert.equal(sourceMore.textContent, '', 'a new sort order starts a new first page');
    assert.equal(app.elements.get('#source-results').children.length, 24);
    // Rendering again without paging (a language refresh) adds no message.
    app.api.applyLanguage();
    assert.equal(sourceMore.textContent, '');
    assert.equal(more.textContent, '');
  }
  console.log('Show More announcement checks passed');
})().catch(error => { console.error(error); process.exit(1); });
