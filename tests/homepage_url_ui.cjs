/* Exercise the real homepage parser, load normalization and controls offline. */
const assert = require('node:assert/strict');
const {setup} = require('./protocol_target_ui.cjs');
const settle = () => new Promise(resolve => setImmediate(resolve));
const element = (app, selector) => app.elements.get(selector);
const value = (app, key) => app.context.location.searchParams.get(key);
const languageLink = (app, language) => app.languageLinks.find(link => link.dataset.languageLink === language);
const languageTarget = (app, language) => new URL(languageLink(app, language).href, app.context.location.href);

function application(query = '', {pathname = '/', unavailable = false, catalogFailure = false} = {}) {
  const app = setup(query, {pathname});
  app.replacements = [];
  const replace = app.context.history.replaceState;
  app.context.history.replaceState = (...args) => { app.replacements.push(String(args[2])); replace(...args); };
  app.context.history.pushState = () => { throw new Error('Normalization must not add history entries'); };
  const fetch = app.context.fetch;
  app.context.fetch = async (...args) => {
    const response = await fetch(...args);
    if (new URL(args[0]).pathname !== '/catalog.json') return response;
    if (catalogFailure) return {ok: false, status: 503};
    const data = await response.json();
    if (unavailable) data.meta.source_index.resource_count = 0;
    return {ok: true, json: async () => data};
  };
  app.api.applyLanguage();
  return app;
}
function input(app, selector, text, event = 'input') {
  element(app, selector).value = text;
  element(app, selector).emit(event);
}
const tests = {
  async defaults() {
    for (const pathname of ['/', '/zh/']) {
      const app = application('', {pathname});
      await app.api.load();
      assert.equal(app.context.location.href, 'https://awesomerea.org' + pathname);
      assert.equal(app.replacements.length, 0, 'a bare canonical URL needs no history replacement');
      assert.equal(app.api.state.lang, pathname === '/zh/' ? 'zh' : 'en');
      assert.equal(app.api.sourceState.mode, 'curated');
      assert.equal(app.api.state.layout, 'compact');
      assert.equal(app.requests.length, 1, 'normalization must not fetch repository data');
      for (const query of ['应用 & UI', 'all', 'relevance', '  literal  ']) {
        input(app, '#search-input', query);
        assert.equal(value(app, 'q'), query, 'query values are not enum defaults');
        assert.equal(value(app, 'lang'), null);
        assert.equal(value(app, 'view'), null);
        assert.equal(value(app, 'layout'), null);
      }
      input(app, '#layout-select', 'cards', 'change');
      assert.equal(value(app, 'layout'), 'cards');
      input(app, '#layout-select', 'compact', 'change');
      assert.equal(value(app, 'layout'), null);
      element(app, '#empty-reset').emit('click');
      assert.equal(app.context.location.search, '');
      const count = app.replacements.length;
      app.api.setIndexMode('curated'); app.api.applyLanguage(); app.api.reset();
      assert.equal(app.replacements.length, count, 'unchanged states must not rewrite the URL');
    }
  },
  async rejected() {
    for (const pathname of ['/', '/zh/']) {
      const query = '?category=bogus&kind=nope&target=moon&group=bogus&lang=invalid'
        + '&view=unknown&layout=invalid&source-target=moon&sort=bogus&keep=one&keep=two#catalog';
      const app = application(query, {pathname});
      assert.equal(app.replacements.length, 0, 'do not remove unvalidated catalog fields before load');
      assert.equal(value(app, 'category'), 'bogus');
      await app.api.load();
      assert.equal(app.replacements.length, 1, 'all rejected values normalize in one replacement');
      assert.equal(app.context.location.href, 'https://awesomerea.org' + pathname + '?keep=one&keep=two#catalog');
      assert.deepEqual(Array.from(app.context.location.searchParams.getAll('keep')), ['one', 'two']);
      for (const key of ['group', 'category', 'kind', 'target']) assert.equal(app.api.state[key], 'all');
      assert.equal(app.api.sourceState.target, 'all');
      assert.equal(app.api.sourceState.sort, 'relevance');
      assert.equal(app.api.state.lang, pathname === '/zh/' ? 'zh' : 'en');
      app.api.applyLanguage(); await app.api.load();
      assert.equal(app.replacements.length, 1, 'render/reload after normalization is idempotent');
    }
    const defaults = application('?view=curated&layout=compact&lang=zh&group=all&category=all&kind=all&target=all'
      + '&q=&sourceq=&source-target=all&topic=&sort=relevance', {pathname: '/zh/'});
    await defaults.api.load();
    assert.equal(defaults.context.location.href, 'https://awesomerea.org/zh/');
    assert.equal(defaults.replacements.length, 1);
    const failed = application('?category=bogus&kind=nope&target=moon#catalog', {catalogFailure: true});
    const original = failed.context.location.href;
    await failed.api.load();
    assert.equal(failed.api.state.error, true);
    assert.equal(failed.context.location.href, original, 'failed fetches cannot validate data-dependent filters');
    assert.equal(failed.replacements.length, 0);
  },
  async legacy() {
    for (const [pathname, language, expectedOverride] of [
      ['/', 'zh', 'zh'], ['/zh/', 'en', 'en'], ['/', 'en', null], ['/zh/', 'zh', null],
    ]) {
      for (const view of ['repositories', 'source-index']) {
        const app = application(`?lang=${language}&view=${view}&layout=cards&sort=updated#catalog`, {pathname});
        await app.api.load(); await settle();
        assert.equal(app.api.state.lang, language);
        assert.equal(app.context.document.documentElement.lang, language === 'zh' ? 'zh-CN' : 'en');
        assert.equal(value(app, 'lang'), expectedOverride);
        assert.equal(app.api.sourceState.mode, 'source-index');
        assert.equal(value(app, 'view'), 'source-index');
        assert.equal(app.api.state.layout, 'cards');
        assert.equal(value(app, 'layout'), 'cards');
        assert.equal(app.api.sourceState.sort, 'pushed');
        assert.equal(value(app, 'sort'), 'pushed');
        assert.equal(app.api.sourceState.loaded, true);
        assert.equal(app.replacements.length, 1);
        assert.equal(app.context.location.pathname, pathname);
        assert.equal(app.context.location.hash, '#catalog');
      }
    }
    const earlyLayout = application('?view=repositories&category=dynamic-analysis&kind=tool');
    input(earlyLayout, '#layout-select', 'cards', 'change');
    assert.equal(value(earlyLayout, 'view'), 'repositories', 'an interaction before load must retain the requested view');
    await earlyLayout.api.load(); await settle();
    assert.equal(earlyLayout.api.sourceState.mode, 'source-index');
    assert.equal(value(earlyLayout, 'category'), 'dynamic-analysis');
    assert.equal(value(earlyLayout, 'kind'), 'tool');
    assert.equal(value(earlyLayout, 'layout'), 'cards');
    const canonical = application('?view=source-index&layout=cards&lang=zh');
    await canonical.api.load(); await settle();
    assert.equal(canonical.replacements.length, 0, 'working nondefault legacy language override is already canonical');
    const unavailable = application('?view=repositories&sourceq=Fixture&source-target=protocol&topic=fixtures&sort=stars', {unavailable: true});
    await unavailable.api.load();
    assert.equal(unavailable.api.sourceState.mode, 'curated');
    assert.equal(value(unavailable, 'view'), null);
    assert.equal(value(unavailable, 'sourceq'), 'Fixture');
    assert.equal(value(unavailable, 'source-target'), 'protocol');
    assert.equal(value(unavailable, 'topic'), 'fixtures');
    assert.equal(value(unavailable, 'sort'), 'stars');
    assert.equal(unavailable.requests.length, 1);
  },
  async inactive() {
    const filters = '?q=Fixture&group=tools&category=dynamic-analysis&kind=tool&target=app'
      + '&sourceq=project&source-target=protocol&topic=not-a-known-topic&sort=stars&keep=x&keep=y#details';
    for (const mode of ['curated', 'source-index']) {
      const query = mode === 'source-index' ? filters.replace('?', '?view=source-index&') : filters;
      const app = application(query, {pathname: '/zh/'});
      const original = app.context.location.href;
      await app.api.load(); await settle();
      assert.equal(app.context.location.href, original);
      assert.equal(app.replacements.length, 0);
      const curatedKeys = ['q', 'group', 'category', 'kind', 'target'];
      const sourceKeys = ['sourceq', 'source-target', 'topic', 'sort'];
      const saved = Object.fromEntries([...curatedKeys, ...sourceKeys].map(key => [key, value(app, key)]));
      app.api.setIndexMode(mode === 'curated' ? 'source-index' : 'curated'); await settle();
      for (const [key, expected] of Object.entries(saved)) assert.equal(value(app, key), expected);
      assert.equal(app.context.location.hash, '#details');
      assert.deepEqual(Array.from(app.context.location.searchParams.getAll('keep')), ['x', 'y']);
      const navigation = languageTarget(app, 'en');
      assert.equal(navigation.pathname, '/');
      assert.equal(navigation.searchParams.has('lang'), false);
      for (const [key, expected] of Object.entries(saved)) assert.equal(navigation.searchParams.get(key), expected);
      assert.equal(navigation.hash, '#details');
    }
    // Free-text repository filters may themselves equal enum default spellings.
    for (const text of ['all', 'relevance']) {
      const app = application('?sourceq=' + text + '&topic=' + text);
      await app.api.load();
      assert.equal(value(app, 'sourceq'), text);
      assert.equal(value(app, 'topic'), text);
      app.api.setIndexMode('source-index'); await settle();
      assert.equal(value(app, 'sourceq'), text);
      assert.equal(value(app, 'topic'), text);
    }
  },
  async languageLinks() {
    for (const pathname of ['/', '/zh/']) {
      const language = pathname === '/zh/' ? 'zh' : 'en';
      const app = application('?q=ghidra&target=binary#catalog', {pathname});
      assert.equal(app.languageLinks.length, 2, 'the header has one link per homepage');
      const expect = suffix => {
        assert.equal(languageLink(app, 'en').href, '/' + suffix);
        assert.equal(languageLink(app, 'zh').href, '/zh/' + suffix);
      };
      // Before the catalog loads, the links already carry the current state.
      expect('?q=ghidra&target=binary#catalog');
      for (const link of app.languageLinks) assert.equal(link.attrs['aria-current'], String(link.dataset.languageLink === language));
      await app.api.load();
      expect('?q=ghidra&target=binary#catalog');
      input(app, '#search-input', 'mitm proxy');
      input(app, '#layout-select', 'cards', 'change');
      expect('?q=mitm+proxy&target=binary&layout=cards#catalog');
      element(app, '#mode-sources').emit('click'); await settle();
      expect('?q=mitm+proxy&target=binary&layout=cards&view=source-index#catalog');
      // Fragment navigation does not pass through replaceState.
      app.context.location.hash = '#contributors'; app.windowListeners.hashchange();
      expect('?q=mitm+proxy&target=binary&layout=cards&view=source-index#contributors');
      element(app, '#mode-curated').emit('click'); element(app, '#empty-reset').emit('click');
      input(app, '#layout-select', 'compact', 'change');
      expect('#contributors');
      assert.equal(app.context.location.lastNavigation, undefined, 'the links navigate only when activated');
    }
    // A legacy ?lang override marks its own language as current; the destination paths drop it.
    for (const [pathname, override] of [['/', 'zh'], ['/zh/', 'en']]) {
      const app = application(`?lang=${override}&target=game#catalog`, {pathname});
      await app.api.load();
      for (const link of app.languageLinks) assert.equal(link.attrs['aria-current'], String(link.dataset.languageLink === override));
      assert.equal(languageLink(app, 'en').href, '/?target=game#catalog');
      assert.equal(languageLink(app, 'zh').href, '/zh/?target=game#catalog');
    }
    // Normalizing rejected filters updates the links in the same step as the address.
    const rejected = application('?category=bogus&keep=1#catalog');
    assert.equal(languageLink(rejected, 'zh').href, '/zh/?category=bogus&keep=1#catalog');
    await rejected.api.load();
    assert.equal(languageLink(rejected, 'zh').href, '/zh/?keep=1#catalog');
  },
  async handoff() {
    for (const pathname of ['/', '/zh/']) {
      const query = '  protobuf <tag> & 小程序  ';
      const app = application('?q=' + encodeURIComponent(query) + '&target=game&source-target=protocol&sort=name#catalog', {pathname});
      await app.api.load();
      assert.equal(element(app, '#empty-search-repositories').hidden, false);
      element(app, '#empty-search-repositories').emit('click'); await settle();
      assert.equal(value(app, 'q'), query); assert.equal(value(app, 'sourceq'), query);
      assert.equal(value(app, 'view'), 'source-index');
      assert.equal(value(app, 'target'), 'game'); assert.equal(value(app, 'source-target'), 'protocol');
      assert.equal(value(app, 'sort'), 'name');
      assert.equal(value(app, 'lang'), null); assert.equal(value(app, 'layout'), null);
      assert.equal(app.context.location.pathname, pathname); assert.equal(app.context.location.hash, '#catalog');
      element(app, '#mode-curated').emit('click');
      assert.equal(value(app, 'view'), null);
      assert.equal(value(app, 'sourceq'), query, 'inactive repository query is retained');
      element(app, '#empty-reset').emit('click');
      assert.equal(value(app, 'q'), null); assert.equal(value(app, 'target'), null);
      assert.equal(value(app, 'sourceq'), query); assert.equal(value(app, 'source-target'), 'protocol');
    }
  },
};
(async () => {
  const selected = process.argv[2];
  assert(!selected || Object.hasOwn(tests, selected), 'unknown test group');
  for (const [name, run] of Object.entries(tests)) if (!selected || selected === name) await run();
  process.stdout.write('Homepage URL state passed' + (selected ? ': ' + selected : '') + '\n');
})().catch(error => { console.error(error); process.exitCode = 1; });
