/* The / search shortcut follows prefers-reduced-motion at each press and still ignores typing contexts. */
const assert = require('node:assert/strict');
const vm = require('node:vm');

// Capture app.js's document keydown listener, which the shared harness otherwise discards.
const createContext = vm.createContext;
let keydown = null;
vm.createContext = context => { context.document.addEventListener = (type, callback) => { if (type === 'keydown') keydown = callback; }; return createContext(context); };
const {setup} = require('./protocol_target_ui.cjs');
const app = setup('');
vm.createContext = createContext;
assert.equal(typeof keydown, 'function');

let reduce = true;
const queries = [];
app.context.window.matchMedia = query => { queries.push(query); return {matches: reduce && query === '(prefers-reduced-motion: reduce)'}; };
const calls = [];
for (const selector of ['#search-input', '#source-search']) {
  const field = app.elements.get(selector) || app.context.document.querySelector(selector);
  field.focus = () => calls.push([selector, 'focus']);
  field.scrollIntoView = options => calls.push([selector, {...options}]);
}
function press(overrides = {}, active = {tagName: 'BODY'}) {
  app.context.document.activeElement = active; calls.length = 0;
  let prevented = false;
  keydown({key: '/', ctrlKey: false, metaKey: false, altKey: false, preventDefault() { prevented = true; }, ...overrides});
  return prevented;
}

(async () => {
  await app.api.load();
  assert.equal(press(), true);
  assert.deepEqual(calls, [['#search-input', 'focus'], ['#search-input', {block: 'center', behavior: 'auto'}]]);
  assert.deepEqual(queries, ['(prefers-reduced-motion: reduce)']);
  // The preference is read at each press, so turning it off restores smooth scrolling.
  reduce = false; press();
  assert.deepEqual(calls[1], ['#search-input', {block: 'center', behavior: 'smooth'}]);
  reduce = true; press();
  assert.deepEqual(calls[1], ['#search-input', {block: 'center', behavior: 'auto'}]);
  // The repository view's field uses the same rule.
  await app.api.loadSources(); app.api.setIndexMode('source-index');
  press();
  assert.deepEqual(calls, [['#source-search', 'focus'], ['#source-search', {block: 'center', behavior: 'auto'}]]);
  reduce = false; press();
  assert.deepEqual(calls[1], ['#source-search', {block: 'center', behavior: 'smooth'}]);
  // Browsers without matchMedia keep the existing smooth scroll.
  delete app.context.window.matchMedia; press();
  assert.deepEqual(calls[1], ['#source-search', {block: 'center', behavior: 'smooth'}]);
  app.context.window.matchMedia = () => ({matches: true});
  // Typing, modified keys and an open data dialog are left alone.
  for (const tagName of ['INPUT', 'TEXTAREA', 'SELECT']) {
    assert.equal(press({}, {tagName}), false, tagName);
    assert.deepEqual(calls, []);
  }
  assert.equal(press({}, {tagName: 'DIV', isContentEditable: true}), false);
  for (const modifier of ['ctrlKey', 'metaKey', 'altKey']) assert.equal(press({[modifier]: true}), false, modifier);
  assert.equal(press({key: '?'}), false);
  app.context.document.querySelector('#data-dialog').open = true;
  assert.equal(press(), false);
  assert.deepEqual(calls, []);
  console.log('Search shortcut motion checks passed');
})().catch(error => { console.error(error); process.exit(1); });
