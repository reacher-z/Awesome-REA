/* Homepage continuation exercises the shipped paper directory's query contract. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {setup} = require('./protocol_target_ui.cjs');
const paperSearch = require('../site/paper-search.js');
const read = name => JSON.parse(fs.readFileSync(path.resolve(__dirname, '..', name), 'utf8'));
const papers = paperSearch.readRecords({schema_version: 1, papers: read('data/papers.json')});
const allowed = paperSearch.allowedValues(papers);
const html = fs.readFileSync(path.resolve(__dirname, '../site/index.html'), 'utf8');
const element = (app, selector) => app.elements.get(selector);
const settle = () => new Promise(resolve => setImmediate(resolve));
// The lean index renders first; the complete catalog follows for requirement text.
const CATALOG_REQUESTS = ['/catalog-index.json', '/catalog.json'];
const paths = app => app.requests.map(url => new URL(url).pathname);
const destination = app => new URL(element(app, '#empty-search-papers').href, app.context.location.href);
const targetState = app => paperSearch.readState(destination(app).searchParams, allowed);

function application(query = '', {pathname = '/', sourceMeta = 'available', failure = false, records} = {}) {
  const app = setup(query, {pathname, records});
  const fetch = app.context.fetch;
  app.context.fetch = async (...args) => {
    const response = await fetch(...args);
    if (!/^\/catalog(-index)?\.json$/.test(new URL(args[0]).pathname)) return response;
    if (failure) return {ok: false, status: 503};
    const data = await response.json();
    if (sourceMeta === 'missing') delete data.meta.source_index;
    if (sourceMeta === 'empty') data.meta.source_index.resource_count = 0;
    return {ok: true, json: async () => data};
  };
  app.api.applyLanguage();
  return app;
}
function input(app, text) {
  element(app, '#search-input').value = text;
  element(app, '#search-input').emit('input');
}
const tests = {
  async localized() {
    const opening = html.match(/<a\b[^>]*id="empty-search-papers"[^>]*>/)[0];
    assert.match(opening, /href="\/papers\/"/);
    assert.match(opening, /\bhidden\b/);
    assert.doesNotMatch(opening, /target=|role="button"|onclick=/, 'use ordinary same-tab link navigation');
    const localizations = read('site/translations.zh-CN.json');
    const records = [...read('data/rea-resources.json'), ...read('data/tool-resources.json')].map(record => ({...record,
      name_zh: localizations[record.id]?.name || record.name,
      requirements_zh: localizations[record.id]?.requirements || record.requirements}));
    const unfiltered = application('?q=DeGPT', {records});
    await unfiltered.api.load();
    assert.equal(unfiltered.api.filtered().length, 0, 'DeGPT is absent from the curated catalog, independently of filters');
    assert.equal(element(unfiltered, '#empty-search-papers').hidden, false);
    for (const [pathname, override, lang] of [['/', '', 'en'], ['/zh/', '', 'zh'], ['/', '&lang=zh', 'zh'], ['/zh/', '&lang=en', 'en']]) {
      const query = '?q=DeGPT&group=tools&target=game&kind=tool&category=dynamic-analysis'
        + '&sourceq=separate&source-target=protocol&topic=fixtures&sort=stars&layout=cards&keep=yes' + override + '#catalog';
      await check(application(query, {pathname, records}), lang);
    }
    async function check(app, lang) {
      await app.api.load();
      assert.equal(app.api.filtered().length, 0);
      const link = element(app, '#empty-search-papers');
      assert.equal(link.hidden, false);
      assert.equal(link.textContent, lang === 'zh' ? '搜索研究论文' : 'Search research papers');
      assert.equal(Object.hasOwn(link.handlers, 'click'), false, 'native links must not mutate homepage state or steal focus');
      assert.equal(destination(app).pathname, lang === 'zh' ? '/zh/papers/' : '/papers/');
      assert.equal(destination(app).search, '?q=DeGPT');
      assert.equal(destination(app).hash, '#paper-search', 'land at the paper search instead of retaining the homepage fragment');
      assert.deepEqual(targetState(app), {q: 'DeGPT', target: 'all', status: 'all', year: 'all'});
      assert(papers.filter(paper => paperSearch.matches(paper, targetState(app))).some(paper => paper.id === 'paper-degpt'));
      const before = {url: app.context.location.href, q: app.api.state.q, sourceq: app.api.sourceState.q,
        target: app.api.state.target, sourceTarget: app.api.sourceState.target, layout: app.api.state.layout};
      link.emit('click');
      assert.deepEqual({url: app.context.location.href, q: app.api.state.q, sourceq: app.api.sourceState.q,
        target: app.api.state.target, sourceTarget: app.api.sourceState.target, layout: app.api.state.layout}, before);
      assert.deepEqual(paths(app), CATALOG_REQUESTS, 'offering and following a plain link needs no homepage papers/source payload fetch');
      app.api.state.lang = lang === 'zh' ? 'en' : 'zh'; app.api.applyLanguage();
      assert.equal(destination(app).pathname, lang === 'zh' ? '/papers/' : '/zh/papers/');
      assert.equal(destination(app).searchParams.get('q'), 'DeGPT');
    }
  },
  async query() {
    const cases = [
      ['  <img src=x onerror=bad()> & "论文" $& {query}  ', '<img src=x onerror=bad()> & "论文" $& {query}'],
      ['DeGPT\u0000\n论文\u007f', 'DeGPT  论文'],
      ['a'.repeat(250), 'a'.repeat(240)],
      ['论'.repeat(245), '论'.repeat(240)],
      ['all', 'all'], ['relevance', 'relevance'],
    ];
    for (const [query, expected] of cases) {
      const app = application('?q=' + encodeURIComponent(query), {pathname: '/zh/'});
      const link = app.context.document.querySelector('#empty-search-papers');
      Object.defineProperty(link, 'innerHTML', {set() { throw new Error('query must not enter HTML'); }});
      await app.api.load();
      assert.equal(link.hidden, false);
      assert.equal(destination(app).searchParams.get('q'), query, 'carry the original query; directory owns normalization');
      assert.equal(targetState(app).q, expected);
      assert.equal(link.textContent, '搜索研究论文', 'no interpolated query or invented match count');
      assert.equal(link.children.length, 0);
      assert.equal(app.api.state.q, query, 'normalizing the destination must not edit homepage input');
      assert.deepEqual(paths(app), CATALOG_REQUESTS);
    }
    const absent = application('?q=not-a-real-paper-unknown');
    await absent.api.load();
    assert.equal(element(absent, '#empty-search-papers').hidden, false);
    assert.equal(papers.filter(paper => paperSearch.matches(paper, targetState(absent))).length, 0,
      'the action offers a search without promising a match');
  },
  async boundaries() {
    for (const sourceMeta of ['available', 'empty', 'missing']) {
      const app = application('?q=DeGPT&sourceq=previous', {sourceMeta});
      await app.api.load();
      const paper = element(app, '#empty-search-papers');
      assert.equal(paper.hidden, false, 'the paper directory does not depend on source-index metadata');
      assert.equal(element(app, '#empty-search-repositories').hidden, sourceMeta !== 'available');
      assert.deepEqual(paths(app), CATALOG_REQUESTS);
      if (sourceMeta === 'available') {
        element(app, '#empty-search-repositories').emit('click'); await settle();
        assert.equal(app.api.sourceState.q, 'DeGPT');
        assert.equal(paper.hidden, true);
        element(app, '#mode-curated').emit('click');
        assert.equal(paper.hidden, false);
      }
      input(app, 'Fixture'); assert.equal(paper.hidden, true);
      input(app, 'another missing query'); assert.equal(paper.hidden, false);
      assert.equal(destination(app).searchParams.get('q'), 'another missing query');
      let resetFocus = false;
      element(app, '#search-input').focus = () => { resetFocus = true; };
      element(app, '#empty-reset').emit('click');
      assert.equal(resetFocus, true); assert.equal(paper.hidden, true);
      assert.equal(app.api.state.q, '');
      assert.equal(app.api.sourceState.q, sourceMeta === 'available' ? 'DeGPT' : 'previous');
    }
    for (const query of ['', '  ', 'Fixture']) {
      const app = application('?q=' + encodeURIComponent(query)); await app.api.load();
      assert.equal(element(app, '#empty-search-papers').hidden, true);
      assert.deepEqual(paths(app), CATALOG_REQUESTS);
    }
    const failure = application('?q=DeGPT', {failure: true}); await failure.api.load();
    assert.equal(failure.api.state.error, true);
    assert.equal(element(failure, '#empty-search-papers').hidden, true);
    assert.equal(failure.requests.length, 1);
  },
};
(async () => {
  const selected = process.argv[2];
  assert(!selected || Object.hasOwn(tests, selected), 'unknown test group');
  for (const [name, run] of Object.entries(tests)) if (!selected || name === selected) await run();
  process.stdout.write('Empty-result paper handoff passed' + (selected ? ': ' + selected : '') + '\n');
})().catch(error => { console.error(error); process.exitCode = 1; });
