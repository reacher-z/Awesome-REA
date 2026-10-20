/* Copy link buttons copy allowlisted internal routes built from stable IDs, with clipboard and manual-copy paths. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {setup} = require('./protocol_target_ui.cjs');

const rows = [['ghidra', 'native-analysis'], ['jadx', 'android'], ['../escape', 'android'], ['scan-7', '../../evil'], ['scan-8', 'Bad Category']]
  .map(([id, category], index) => ({id, name: `Name ${index}`, name_zh: `名称 ${index}`, full_name: `Owner/name${index}`,
    url: index === 1 ? 'javascript:alert(1)' : `https://github.com/Owner/name${index}`, evidence_url: 'https://example.org/evidence',
    description_en: '', description_zh: '', targets: ['app'], topics: [], category, group: 'tools', kind: 'tool', relationship: 'foundation',
    requirements: ['A fixture'], requirements_zh: ['测试条件'], verified_at: '2026-01-01', scan_status: 'readme-scanned', stars: index}));
const descendants = (element, found = []) => { for (const child of element.children || []) { found.push(child); descendants(child, found); } return found; };
const copyButtons = element => descendants(element).filter(node => node.className === 'copy-link');
const settle = () => new Promise(resolve => setImmediate(resolve));

function harness(app) {
  const writes = []; let allow = true;
  app.context.navigator = {clipboard: {writeText: async text => { if (!allow) throw new Error('NotAllowedError'); writes.push(text); }}};
  app.context.setTimeout = callback => callback();
  const createElement = app.context.document.createElement;
  app.context.document.createElement = tag => {
    const element = createElement(tag);
    element.after = next => { element.nextElementSibling = next; next.inserted = (next.inserted || 0) + 1; };
    element.classList = {contains: name => element.className.split(' ').includes(name), toggle() {}, add() {}, remove() {}};
    element.focus = () => { element.focused = true; }; element.select = () => { element.selected = true; };
    return element;
  };
  return {writes, deny: () => { allow = false; }};
}

(async () => {
  for (const [language, pathname] of [['en', '/'], ['zh', '/zh/']]) {
    const prefix = language === 'zh' ? '/zh' : '';
    const app = setup('', {pathname, records: rows});
    const clipboard = harness(app);
    await app.api.load();
    const curated = copyButtons(app.elements.get('#resource-grid'));
    // The record whose ID is not a slug gets no button; an upstream javascript: URL never becomes the link.
    assert.deepEqual(curated.map(button => button.dataset.copyLink), [`https://awesomerea.org${prefix}/resources/ghidra/`,
      `https://awesomerea.org${prefix}/resources/jadx/`, `https://awesomerea.org${prefix}/resources/scan-7/`, `https://awesomerea.org${prefix}/resources/scan-8/`]);
    const label = language === 'zh' ? '复制此条目的链接：名称 0' : 'Copy link to this entry: Name 0';
    assert.equal(curated[0].attrs['aria-label'], label);
    assert.equal(curated[0].type, 'button');
    assert.equal(curated[0].title, language === 'zh' ? '复制此条目的链接' : 'Copy link to this entry');
    curated[0].emit('click'); await settle();
    assert.deepEqual(clipboard.writes, [`https://awesomerea.org${prefix}/resources/ghidra/`]);
    assert.equal(app.elements.get('#copy-link-status').textContent, language === 'zh' ? '已复制 名称 0 的链接。' : 'Link to Name 0 copied.');

    // Repository cards copy their card on the static category page; malformed IDs or categories get no button.
    await app.api.loadSources(); app.api.setIndexMode('source-index');
    const repositories = copyButtons(app.elements.get('#source-results'));
    assert.deepEqual(repositories.map(button => button.dataset.copyLink).sort(), [`https://awesomerea.org${prefix}/browse/android/#jadx`,
      `https://awesomerea.org${prefix}/browse/native-analysis/#ghidra`]);
    const repository = repositories.find(button => button.dataset.copyLink.endsWith('#jadx'));
    assert.equal(repository.attrs['aria-label'], (language === 'zh' ? '复制此仓库在分类页上的链接：' : 'Copy link to this repository on its category page: ') + 'Owner/name1');

    // Without clipboard access the link is shown selected beside the button; a second press reuses that field.
    clipboard.deny();
    repository.emit('click'); await settle();
    const field = repository.nextElementSibling;
    assert.equal(field.className, 'copy-link-fallback');
    assert.equal(field.value, `https://awesomerea.org${prefix}/browse/android/#jadx`);
    assert.equal(field.readOnly, true);
    assert(field.focused && field.selected);
    assert.equal(field.attrs['aria-label'], language === 'zh' ? 'Owner/name1 的链接' : 'Link to Owner/name1');
    assert.match(app.elements.get('#copy-link-status').textContent, language === 'zh' ? /无法直接复制。Owner\/name1 的链接已选中/ : /Copying isn’t available here\. The link to Owner\/name1 is selected/);
    repository.emit('click'); await settle();
    assert.equal(field.inserted, 1);
  }

  // The paper directory adds a Copy link after each Full entry link, for the paper's own entry page.
  class Element {
    constructor(tag) { this.tag = tag; this.children = []; this.dataset = {}; this.attrs = {}; this.handlers = {}; this.textContent = ''; }
    append(...nodes) { this.children.push(...nodes); }
    after(node) { this.next = node; this.nextElementSibling = node; }
    setAttribute(key, value) { this.attrs[key] = value; }
    addEventListener(type, callback) { this.handlers[type] = callback; }
    focus() { this.focused = true; } select() { this.selected = true; }
  }
  const script = fs.readFileSync(path.join(__dirname, '../site/paper-search.js'), 'utf8');
  for (const lang of ['en', 'zh-CN']) {
    const main = new Element('main');
    const cards = ['paper-fixture', 'Paper-Bad'].map(id => {
      const card = new Element('article'); card.dataset.paperId = id;
      const links = new Element('nav'); const entry = new Element('a'); entry.className = 'paper-link entry-detail-link'; links.append(entry);
      links.querySelector = selector => (selector === '.entry-detail-link' ? entry : null);
      card.querySelector = selector => ({'.paper-links': links, h3: {textContent: ' Fixture paper '}})[selector];
      card.entry = entry; return card;
    });
    const writes = []; let allow = true;
    const document = {documentElement: {lang}, createElement: tag => new Element(tag), getElementById: () => null,
      querySelector: selector => ({main, 'link[rel="canonical"]': {href: 'https://awesomerea.org/papers/'}})[selector] || null,
      querySelectorAll: selector => (selector === '[data-paper-id]' ? cards : [])};
    const window = {location: new URL('http://localhost:8000/papers/'), addEventListener() {},
      navigator: {clipboard: {writeText: async text => { if (!allow) throw new Error('denied'); writes.push(text); }}}};
    vm.runInNewContext(script, {document, window, URL, console});
    const zh = lang === 'zh-CN';
    const button = cards[0].entry.next;
    assert.equal(cards[1].entry.next, undefined, 'a malformed paper ID gets no button');
    assert.equal(button.className, 'paper-link copy-link');
    assert.equal(button.textContent, zh ? '复制链接' : 'Copy link');
    assert.equal(button.dataset.copyLink, `https://awesomerea.org${zh ? '/zh' : ''}/papers/paper-fixture/`, 'the canonical origin, not the preview host');
    assert.equal(button.attrs['aria-label'], zh ? '复制此论文条目的链接：Fixture paper' : "Copy link to this paper's entry: Fixture paper");
    await button.handlers.click(); 
    assert.deepEqual(writes, [button.dataset.copyLink]);
    const status = main.children[0];
    assert.equal(status.attrs.role, 'status');
    assert.equal(status.textContent, zh ? '已复制 Fixture paper 的链接。' : 'Link to Fixture paper copied.');
    allow = false; await button.handlers.click();
    assert.equal(button.next.className, 'copy-link-fallback');
    assert.equal(button.next.value, button.dataset.copyLink);
    assert(button.next.focused && button.next.selected);
  }
  console.log('Copy link checks passed');
})().catch(error => { console.error(error); process.exit(1); });
