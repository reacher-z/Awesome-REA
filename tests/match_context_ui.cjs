/* Exercise the hidden-field match hints through the real homepage script in the offline VM. */
const assert = require('node:assert/strict');
const {setup} = require('./protocol_target_ui.cjs');
const settle = () => new Promise(resolve => setImmediate(resolve));

const base = {url: 'https://github.com/Fixture/project', evidence_url: 'https://github.com/Fixture/project', topics: [],
  category: 'dynamic-analysis', group: 'tools', kind: 'tool', relationship: 'foundation', verified_at: '2026-01-01',
  scan_status: 'readme-scanned', targets: ['app'], stars: 1};
const RECORDS = [
  {...base, id: 'bilingual', name: 'Bytecode Lens', name_zh: '字节码透镜', full_name: 'Fixture/bytecode-lens',
    description_en: 'Inspects compiled classes.', description_zh: '查看已编译的类，并包含反编译器视图。',
    requirements: ['Needs a Java runtime.'], requirements_zh: ['需要 Java 运行时。']},
  {...base, id: 'requirements', name: 'Trace Kit', name_zh: '追踪工具包', full_name: 'Fixture/trace-kit',
    description_en: 'Records calls.', description_zh: '记录调用。',
    requirements: ['Requires a rooted handset for capture.'], requirements_zh: ['需要已获取 root 权限的手机进行抓取。']},
  {...base, id: 'unicode', name: 'Emoji Probe', name_zh: '表情探针', full_name: 'Fixture/emoji-probe',
    description_en: 'İstanbul ' + '😀'.repeat(40) + ' symbolication ' + '😀'.repeat(40),
    description_zh: '<img src=x onerror=alert(1)> ' + '😀'.repeat(40) + '符号化' + '😀'.repeat(40),
    requirements: ['None.'], requirements_zh: ['无。']},
  {...base, id: 'repository', name: 'Topic Only', name_zh: '仅主题', full_name: 'Fixture/topic-only',
    description_en: '', description_zh: '', description_original: 'Upstream wording about unpackers.',
    topics: ['protocol-analysis'], requirements: ['None.'], requirements_zh: ['无。'],
    related_entries: [{kind: 'paper', id: 'paper-fixture', title_en: 'Neural Lifting Study', title_zh: '神经提升研究',
      href_en: '/papers/paper-fixture/', href_zh: '/zh/papers/paper-fixture/'}]},
];
function flatten(element) { return typeof element === 'string' ? element : (element.textContent || '') + element.children.map(flatten).join(''); }
function find(element, predicate) { if (predicate(element)) return element; for (const child of element.children || []) { const found = find(child, predicate); if (found) return found; } return null; }
const cards = (app, selector = '#resource-grid') => app.elements.get(selector).children;
const byId = (app, id, selector) => cards(app, selector).find(card => card.dataset.recordId === id);
const hint = card => card.children.find(child => child.className === 'match-hint') || null;
async function application(query, pathname = '/') { const app = setup(query, {pathname, records: RECORDS}); await app.api.load(); await settle(); return app; }
function search(app, text, selector = '#search-input') { app.elements.get(selector).value = text; app.elements.get(selector).emit('input'); }
const LONE_SURROGATE = /[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/;

const tests = {
  async alternateLanguageMatches() {
    const english = await application('?q=反编译');
    const card = byId(english, 'bilingual');
    assert.equal(flatten(card.children.find(child => child.className === 'card-description')), 'Inspects compiled classes.', 'the main translation stays in place');
    assert.equal(flatten(hint(card)), 'Matched in Chinese description 查看已编译的类，并包含反编译器视图。');
    assert.equal(find(hint(card), node => node.tag === 'mark').textContent, '反编译');
    assert.equal(find(hint(card), node => node.tag === 'q').attrs.lang, 'zh-CN', 'the quoted Chinese text is marked as Chinese');
    const chinese = await application('?q=compiled%20java', '/zh/');
    const zhHint = hint(byId(chinese, 'bilingual'));
    assert.equal(find(zhHint, node => node.className === 'match-field').textContent, '英文简介 ');
    assert.equal(flatten(zhHint), '匹配于 英文简介 Inspects compiled classes. · 中文使用条件 需要 Java 运行时。');
    assert.deepEqual(zhHint.children.filter(node => node.tag === 'q').map(node => node.attrs.lang), ['en', 'zh-CN']);
    assert.deepEqual(zhHint.children.filter(node => node.tag === 'q').map(node => find(node, part => part.tag === 'mark').textContent), ['compiled', 'Java'],
      'each hidden term names its own field, at most two');
  },
  async requirementsAndVisibleText() {
    const app = await application('?q=rooted');
    assert.equal(flatten(hint(byId(app, 'requirements'))), 'Matched in English requirements Requires a rooted handset for capture.');
    search(app, '已获取');
    assert.equal(flatten(hint(byId(app, 'requirements'))), 'Matched in Chinese requirements 需要已获取 root 权限的手机进行抓取。');
    // Terms in the title, description, Type, Category or target labels need no hint.
    for (const query of ['trace', 'records calls', 'tool', 'dynamic', 'app', '']) {
      search(app, query);
      assert(cards(app).every(card => hint(card) === null), `no hint for visible ${JSON.stringify(query)}`);
    }
    search(app, 'foundation');
    assert(cards(app).every(card => flatten(hint(card)) === 'Matched in Relationship foundation'));
    const order = cards(app).map(card => card.dataset.recordId);
    assert.deepEqual(order, app.api.filtered().slice(0, 15).map(record => record.id), 'hints never change result order');
  },
  async unicodeAndMarkupStayText() {
    // In the Chinese view the English description is hidden: emoji context must be cut on code points.
    const app = await application('?q=symbolication', '/zh/');
    const excerpt = hint(byId(app, 'unicode')).children.find(node => node.tag === 'q');
    for (const part of excerpt.children) assert(!LONE_SURROGATE.test(part.textContent), 'excerpts never split a surrogate pair');
    assert.equal(find(excerpt, node => node.tag === 'mark').textContent, 'symbolication');
    assert(excerpt.children[0].textContent.startsWith('…') && excerpt.children[2].textContent.endsWith('…'));
    assert.equal([...excerpt.children[0].textContent].length, 31, 'thirty code points of context, not code units');
    // "İ" lower-cases to two code units; the highlight still lands on the matching characters.
    search(app, 'stanbul');
    assert.equal(find(hint(byId(app, 'unicode')), node => node.tag === 'mark').textContent, 'stanbul');
    // The hidden Chinese description contains markup-like text; it is quoted as text, never parsed.
    const english = await application('?q=符号化');
    const markup = hint(byId(english, 'unicode'));
    assert.equal(find(markup, node => node.tag === 'mark').textContent, '符号化');
    assert.equal(find(markup, node => node.tag === 'img'), null);
    search(english, '<img');
    assert.equal(find(hint(byId(english, 'unicode')), node => node.tag === 'mark').textContent, '<img');
    assert(flatten(hint(byId(english, 'unicode'))).includes('<img src=x onerror=alert(1)>'));
  },
  async repositoryCardsQuoteRealFields() {
    const app = await application('?view=source-index&sourceq=unpackers');
    await app.api.loadSources(); app.api.setIndexMode('source-index'); await settle();
    const card = byId(app, 'repository', '#source-results');
    assert.equal(flatten(card.children.find(child => child.className.startsWith('source-card-description'))), 'No description supplied by the upstream repository.',
      'an absent description is never filled from the hint');
    assert.equal(flatten(hint(card)), 'Matched in Original description Upstream wording about unpackers.');
    search(app, 'protocol-analysis', '#source-search');
    assert.equal(flatten(hint(byId(app, 'repository', '#source-results'))), 'Matched in Topics protocol-analysis');
    search(app, '神经', '#source-search');
    assert.equal(flatten(hint(byId(app, 'repository', '#source-results'))), 'Matched in Related entry 神经提升研究');
    search(app, 'topic', '#source-search');
    assert.equal(hint(byId(app, 'repository', '#source-results')), null, 'the repository name is visible');
  },
};

(async () => {
  const selected = process.argv.slice(2);
  for (const name of selected.length ? selected : Object.keys(tests)) {
    if (!tests[name]) throw new Error('Unknown test group: ' + name);
    await tests[name]();
    console.log('Match context passed: ' + name);
  }
})().catch(error => { console.error(error); process.exit(1); });
