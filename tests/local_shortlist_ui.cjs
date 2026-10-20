/* The browser-local shortlist: type-keyed IDs only, shared by app.js and paper-search.js, with honest missing states. */
const assert = require('node:assert/strict');
const path = require('node:path');
const vm = require('node:vm');
const {setup} = require('./protocol_target_ui.cjs');
const {initializeShortlist, readShortlist} = require(path.join(__dirname, '../site/paper-search.js'));

const KEY = 'awesomerea-shortlist';
const settle = () => new Promise(resolve => setImmediate(resolve));
class Storage {
  constructor(entries = {}) { this.values = new Map(Object.entries(entries)); this.failWrites = false; this.writes = []; }
  getItem(key) { return this.values.has(key) ? this.values.get(key) : null; }
  setItem(key, value) { if (this.failWrites && key === KEY) throw new Error('QuotaExceededError'); this.writes.push(key); this.values.set(key, String(value)); }
  removeItem(key) { this.values.delete(key); }
  saved() { return JSON.parse(this.getItem(KEY) || 'null'); }
}
const rows = ['protocol', 'app', 'game'].map((target, index) => ({id: 'fixture-' + index, name: 'Fixture ' + index, name_zh: '测试 ' + index,
  full_name: 'Fixture/project' + index, url: 'https://github.com/Fixture/project' + index, evidence_url: 'https://github.com/Fixture/project' + index,
  description_en: '', description_zh: '', targets: [target], topics: [], category: 'dynamic-analysis', group: 'tools', kind: 'tool',
  relationship: 'foundation', requirements: ['A fixture'], requirements_zh: ['测试条件'], verified_at: '2026-01-01', scan_status: 'readme-scanned', stars: index}));
const papers = [{id: 'paper-fixture', title: 'Fixture paper', title_zh: '测试论文'}];

function descendants(element, found = []) {
  for (const child of element.children || []) { found.push(child); descendants(child, found); }
  return found;
}
function homepage(storage, {pathname = '/', papersFail = false} = {}) {
  const app = setup('', {pathname, records: rows});
  app.context.window.localStorage = storage;
  app.context.document.body = {classList: {add() {}, remove() {}}};
  const query = app.context.document.querySelectorAll;
  app.context.document.querySelectorAll = selector => selector === '.save-toggle'
    ? ['#resource-grid', '#source-results'].flatMap(id => descendants(app.elements.get(id) || {children: []})).filter(node => node.className === 'save-toggle')
    : query(selector);
  const fetch = app.context.fetch;
  app.context.fetch = async url => (new URL(url).pathname === '/papers.json'
    ? (app.requests.push(String(url)), papersFail ? {ok: false, status: 503} : {ok: true, json: async () => papers}) : fetch(url));
  const dialog = app.elements.get('#shortlist');
  dialog.showModal = () => { dialog.open = true; };
  dialog.close = () => { dialog.open = false; dialog.handlers.close?.(); };
  vm.runInContext('readShortlist(); syncShortlist();', app.context);
  app.toggles = id => descendants(app.elements.get(id)).filter(node => node.className === 'save-toggle');
  app.items = () => descendants(app.elements.get('#shortlist-items')).filter(node => node.className === 'shortlist-item');
  app.text = node => [node.textContent || '', ...descendants(node).map(child => child.textContent || '')].join('');
  return app;
}

(async () => {
  // Without usable storage nothing is offered and nothing breaks.
  const plain = setup('', {records: rows}); await plain.api.load();
  assert.equal(plain.elements.get('#shortlist-open').hidden, true);
  assert(descendants(plain.elements.get('#resource-grid')).every(node => node.className !== 'save-toggle'));
  const blocked = homepage({getItem() { throw new Error('SecurityError'); }, setItem() { throw new Error('SecurityError'); }, removeItem() {}});
  await blocked.api.load();
  assert.equal(blocked.elements.get('#shortlist-open').hidden, true);
  assert.equal(blocked.toggles('#resource-grid').length, 0);
  const empty = homepage(new Storage()); await empty.api.load();
  assert.equal(empty.toggles('#resource-grid').length, rows.length);
  assert.equal(empty.elements.get('#shortlist-open').hidden, true, 'the Shortlist button appears once something is saved');
  assert.equal(empty.elements.get('#shortlist-count').textContent, '0');

  for (const [language, pathname] of [['en', '/'], ['zh', '/zh/']]) {
    // Stored values are validated: malformed, unknown-type and duplicate entries are ignored.
    const storage = new Storage({[KEY]: JSON.stringify(['curated:fixture-0', 'bogus', 'curated:../x', 'curated:fixture-0', 'link:fixture-1', 7])});
    const app = homepage(storage, {pathname});
    await app.api.load();
    assert.equal(app.elements.get('#shortlist-open').hidden, false);
    assert.equal(app.elements.get('#shortlist-count').textContent, '1');
    const curated = app.toggles('#resource-grid');
    assert.equal(curated.length, rows.length);
    const first = curated.find(button => button.dataset.shortlistKey === 'curated:fixture-0');
    assert.equal(first.attrs['aria-pressed'], 'true');
    assert.equal(first.type, 'button');
    assert.equal(app.text(first), (language === 'zh' ? '已收藏' : 'Saved') + (language === 'zh' ? ' 测试 0' : ' Fixture 0'));
    const second = curated.find(button => button.dataset.shortlistKey === 'curated:fixture-1');
    assert.equal(second.attrs['aria-pressed'], 'false');
    second.emit('click');
    assert.deepEqual(storage.saved(), ['curated:fixture-0', 'curated:fixture-1']);
    assert.equal(second.attrs['aria-pressed'], 'true');
    assert.equal(app.elements.get('#shortlist-count').textContent, '2');
    assert.equal(app.elements.get('#shortlist-status').textContent,
      language === 'zh' ? '已收藏 测试 1。收藏清单共 2 项。' : 'Saved Fixture 1. 2 entries in your shortlist.');

    // A repository with the same stable ID is a separate entry.
    await app.api.loadSources(); app.api.setIndexMode('source-index');
    const repository = app.toggles('#source-results').find(button => button.dataset.shortlistKey === 'repository:fixture-0');
    assert.equal(repository.attrs['aria-pressed'], 'false', 'curated:fixture-0 must not mark repository:fixture-0');
    repository.emit('click');
    assert.deepEqual(storage.saved(), ['curated:fixture-0', 'curated:fixture-1', 'repository:fixture-0']);
    assert.equal(first.attrs['aria-pressed'], 'true');

    // A paper saved elsewhere and an entry that no longer exists both appear; the missing one is not replaced.
    storage.setItem(KEY, JSON.stringify([...storage.saved(), 'paper:paper-fixture', 'curated:gone-entry', 'repository:scan-404']));
    app.windowListeners.storage({key: KEY});
    assert.equal(app.elements.get('#shortlist-count').textContent, '6');
    app.elements.get('#shortlist-open').emit('click');
    assert.equal(app.elements.get('#shortlist').open, true);
    let items = app.items().map(app.text);
    assert.match(items.find(text => text.includes('paper-fixture')), language === 'zh' ? /正在加载详情/ : /Loading details/);
    await settle(); await settle();
    items = app.items().map(app.text);
    assert.equal(items.length, 6);
    assert(items[0].startsWith(language === 'zh' ? '测试 0' : 'Fixture 0'));
    assert(items.some(text => text.startsWith(language === 'zh' ? '测试论文' : 'Fixture paper')));
    assert(items.some(text => text.startsWith('Fixture/project0')));
    assert(items.includes('gone-entry' + (language === 'zh' ? '已不在精选资源中。移除' : 'No longer in the curated collection.Remove')));
    assert(items.includes('scan-404' + (language === 'zh' ? '已不在可浏览的仓库索引中。移除' : 'No longer in the browsable repository index.Remove')));
    const links = descendants(app.elements.get('#shortlist-items')).filter(node => node.className === 'shortlist-link');
    assert.deepEqual(links.map(link => link.href), [`${language === 'zh' ? '/zh' : ''}/resources/fixture-0/`, `${language === 'zh' ? '/zh' : ''}/resources/fixture-1/`,
      'https://github.com/Fixture/project0', `${language === 'zh' ? '/zh' : ''}/papers/paper-fixture/`]);
    assert.equal(links[2].target, '_blank');
    assert(app.requests.every(url => ['/catalog.json', '/source-browser.json', '/papers.json'].includes(new URL(url).pathname) && !/fixture-|gone-entry|scan-404/.test(new URL(url).search)),
      'saved IDs never leave the browser');

    // Remove from the dialog, then a failed write keeps the list and says so, then clear all.
    const removeGone = descendants(app.elements.get('#shortlist-items')).find(node => node.className === 'shortlist-remove' && node.attrs['aria-label'].endsWith('gone-entry'));
    removeGone.emit('click');
    assert(!storage.saved().includes('curated:gone-entry'));
    storage.failWrites = true;
    first.emit('click');
    assert(storage.saved().includes('curated:fixture-0'));
    assert.equal(first.attrs['aria-pressed'], 'true');
    assert.equal(app.elements.get('#shortlist-dialog-status').textContent, language === 'zh' ? '此浏览器无法保存收藏清单。' : 'This browser couldn’t save the shortlist.');
    storage.failWrites = false;
    app.elements.get('#shortlist-clear').emit('click');
    assert.equal(storage.getItem(KEY), null);
    assert.equal(app.elements.get('#shortlist-count').textContent, '0');
    assert.equal(app.elements.get('#shortlist-empty').hidden, false);
    assert.equal(app.elements.get('#shortlist-clear').hidden, true);
    assert.equal(app.elements.get('#shortlist-open').hidden, true, 'an empty shortlist takes no room beside the tabs');
    assert.equal(app.elements.get('#shortlist-dialog-status').textContent, language === 'zh' ? '收藏清单已清空。' : 'Shortlist cleared.');
    assert(curated.every(button => button.attrs['aria-pressed'] === 'false'));
    app.elements.get('#shortlist-close').emit('click');
    assert.equal(app.elements.get('#shortlist').open, false);
  }

  // A paper list that cannot load keeps the saved ID instead of calling it gone.
  const offline = homepage(new Storage({[KEY]: JSON.stringify(['paper:paper-fixture'])}), {papersFail: true});
  await offline.api.load(); offline.elements.get('#shortlist-open').emit('click'); await settle(); await settle();
  assert.deepEqual(offline.items().map(offline.text), ['paper-fixtureDetails couldn’t load. The saved ID is kept.Remove']);

  // paper-search.js adds Save toggles to paper cards in the same storage format.
  class Element {
    constructor(tag) { this.tag = tag; this.children = []; this.dataset = {}; this.attrs = {}; this.handlers = {}; this.textContent = ''; }
    append(...nodes) { for (const node of nodes) this.children.push(typeof node === 'string' ? Object.assign(new Element('#text'), {textContent: node}) : node); }
    after(node) { this.next = node; }
    setAttribute(key, value) { this.attrs[key] = value; }
    addEventListener(type, callback) { this.handlers[type] = callback; }
    emit(type) { this.handlers[type]?.({}); }
    get firstChild() { return this.children[0]; }
  }
  function paperPage(storage, lang = 'en') {
    const actions = new Element('div');
    const cards = ['paper-fixture', 'paper-other'].map(id => {
      const card = new Element('article'); card.dataset.paperId = id; const links = new Element('nav'); const heading = new Element('h3');
      heading.textContent = id === 'paper-fixture' ? 'Fixture paper' : 'Other paper';
      card.querySelector = selector => ({'.paper-links': links, h3: heading})[selector]; card.links = links; return card;
    });
    const listeners = {};
    const document = {documentElement: {lang}, createElement: tag => new Element(tag),
      querySelector: selector => (selector === '.papers-actions' ? actions : null), querySelectorAll: selector => (selector === '[data-paper-id]' ? cards : [])};
    const browser = {localStorage: storage, addEventListener(type, callback) { listeners[type] = callback; }};
    return {result: initializeShortlist(document, browser), actions, cards, listeners};
  }
  const shared = new Storage({[KEY]: JSON.stringify(['curated:fixture-0', 'paper:paper-other'])});
  for (const lang of ['en', 'zh-CN']) {
    const page = paperPage(shared, lang);
    assert.equal(page.result, true);
    const link = page.actions.children.at(-1);
    assert.equal(link.href, lang === 'zh-CN' ? '/zh/#shortlist' : '/#shortlist');
    assert.equal(link.hidden, false);
    const buttons = page.cards.map(card => card.links.children.at(-1));
    assert.deepEqual(buttons.map(button => button.dataset.shortlistKey), ['paper:paper-fixture', 'paper:paper-other']);
    assert.equal(buttons[1].attrs['aria-pressed'], 'true');
    if (lang === 'en') {
      assert.equal(link.children[1].textContent, '2');
      buttons[0].emit('click');
      assert.deepEqual(shared.saved(), ['curated:fixture-0', 'paper:paper-other', 'paper:paper-fixture']);
      assert.equal(buttons[0].firstChild.textContent, 'Saved');
      assert.equal(buttons[0].children[1].textContent, ' Fixture paper');
      assert.equal(page.actions.next.textContent, 'Saved Fixture paper. 3 entries in your shortlist.');
    } else {
      assert.equal(buttons[0].firstChild.textContent, '已收藏');
      buttons[0].emit('click');
      assert.equal(page.actions.next.textContent, '已移除 Fixture paper。收藏清单共 2 项。');
      shared.setItem(KEY, JSON.stringify([])); page.listeners.storage({key: KEY});
      assert.equal(buttons[1].attrs['aria-pressed'], 'false');
      assert.equal(link.children[1].textContent, '0');
      assert.equal(link.hidden, true);
    }
  }
  // The homepage reads exactly what the paper directory wrote.
  shared.setItem(KEY, JSON.stringify(['paper:paper-fixture', 'curated:fixture-2']));
  assert.deepEqual(readShortlist(shared), ['paper:paper-fixture', 'curated:fixture-2']);
  const reader = homepage(shared); await reader.api.load();
  assert.equal(reader.toggles('#resource-grid').find(button => button.dataset.shortlistKey === 'curated:fixture-2').attrs['aria-pressed'], 'true');
  assert.equal(paperPage({getItem() { throw new Error('blocked'); }, setItem() { throw new Error('blocked'); }, removeItem() {}}).result, false);
  console.log('Local shortlist checks passed');
})().catch(error => { console.error(error); process.exit(1); });
