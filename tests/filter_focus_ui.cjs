/* Exercise keyboard focus after topic filtering and resets through the real homepage script in the offline VM. */
const assert = require('node:assert/strict');
const {setup} = require('./protocol_target_ui.cjs');
const settle = () => new Promise(resolve => setImmediate(resolve));

async function application(query, pathname = '/') {
  const app = setup(query, {pathname});
  // Track focus: the shared fake elements accept focus() but do not record it.
  const document = app.context.document;
  Object.getPrototypeOf(app.elements.get('#search-input')).focus = function () { document.activeElement = this; };
  await app.api.load(); await settle();
  return app;
}
const BODY = {tagName: 'BODY'};
const element = (app, selector) => app.elements.get(selector);
const focused = app => app.context.document.activeElement;
function find(node, predicate) { if (predicate(node)) return node; for (const child of node.children || []) { const found = find(child, predicate); if (found) return found; } return null; }
// Keyboard activation of a button dispatches a click whose detail is 0; a pointer click counts presses from 1.
function activate(app, control, detail) { app.context.document.activeElement = control; control.handlers.click({target: control, detail}); }
const KEYBOARD = 0, POINTER = 1;

const tests = {
  async topicChipFocusesTheTopicField() {
    for (const pathname of ['/', '/zh/']) {
      const app = await application('?view=source-index', pathname);
      await app.api.loadSources(); app.api.setIndexMode('source-index'); await settle();
      const chip = () => find(element(app, '#source-results').children[0], node => node.className === 'source-topic-chip');
      const original = chip(); const topic = original.title.split(': ').pop();
      activate(app, original, KEYBOARD);
      assert.equal(app.api.sourceState.topic, topic);
      assert(!find(element(app, '#source-results'), node => node === original), 'the activated chip was replaced by the re-render');
      assert.equal(focused(app), element(app, '#source-topic'), 'focus lands on the named Topic field');
      assert.equal(element(app, '#source-topic').value, topic, 'which shows the chosen topic');
      app.api.resetSources();
      const pointer = chip();
      activate(app, pointer, POINTER);
      assert.equal(app.api.sourceState.topic, topic);
      assert.equal(focused(app), pointer, 'pointer activation keeps the browser default');
    }
  },
  async resetsReturnToTheCollectionSearch() {
    for (const pathname of ['/', '/zh/']) {
      const curated = await application('?q=fixture&kind=tool', pathname);
      activate(curated, element(curated, '#clear-filters'), KEYBOARD);
      assert.equal(curated.api.state.q, '');
      assert.equal(element(curated, '#clear-filters').hidden, true, 'Clear filters hides itself');
      assert.equal(focused(curated), element(curated, '#search-input'));
      curated.api.state.q = 'fixture'; curated.api.applyLanguage();
      activate(curated, element(curated, '#clear-filters'), POINTER);
      assert.equal(focused(curated), element(curated, '#clear-filters'), 'pointer activation keeps the browser default');
      // The curated empty state already focused its search; it still does for any activation.
      const empty = await application('?q=no-such-resource', pathname);
      assert.equal(element(empty, '#empty-state').hidden, false);
      activate(empty, element(empty, '#empty-reset'), POINTER);
      assert.equal(focused(empty), element(empty, '#search-input'));

      for (const id of ['#source-clear', '#source-reset']) {
        const app = await application('?view=source-index&sourceq=no-such-repository&topic=fixtures', pathname);
        await app.api.loadSources(); app.api.setIndexMode('source-index'); await settle();
        assert.equal(element(app, '#source-empty').hidden, false, 'a zero-result state');
        activate(app, element(app, id), KEYBOARD);
        assert.equal(app.api.sourceState.q, ''); assert.equal(app.api.sourceState.topic, '');
        assert.equal(element(app, '#source-empty').hidden, true);
        assert.equal(element(app, '#source-clear').hidden, true);
        assert.equal(focused(app), element(app, '#source-search'), `${id} returns focus to the repository search`);
      }
    }
  },
  async showMoreKeepsItsOwnBehaviour() {
    const app = await application('');
    app.context.document.activeElement = BODY;
    activate(app, element(app, '#load-more'), KEYBOARD);
    assert.notEqual(focused(app), element(app, '#search-input'), 'Show More never sends focus to the search field');
    assert.equal(app.api.state.visible, 30);
  },
};

(async () => {
  const selected = process.argv.slice(2);
  for (const name of selected.length ? selected : Object.keys(tests)) {
    if (!tests[name]) throw new Error('Unknown test group: ' + name);
    await tests[name]();
    console.log('Filter focus passed: ' + name);
  }
})().catch(error => { console.error(error); process.exit(1); });
