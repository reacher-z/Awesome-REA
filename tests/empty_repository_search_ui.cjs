/* Exercise the actual empty-result transition with the existing offline app VM. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {setup} = require('./protocol_target_ui.cjs');
const html = fs.readFileSync(path.resolve(__dirname, '../site/index.html'), 'utf8');

const rows = [
  {id: 'curated-tool', name: 'Fixture tool', name_zh: '测试工具', full_name: 'Example/protobuf',
    url: 'https://github.com/Example/protobuf', evidence_url: 'https://example.org/evidence',
    description_en: 'Documented fixture.', description_zh: '有文档的测试条目。',
    targets: ['protocol'], topics: ['fixtures'], category: 'dynamic-analysis', group: 'tools',
    kind: 'tool', relationship: 'foundation', requirements: ['Original input required.'],
    requirements_zh: ['需要原始输入。'], verified_at: '2026-01-01', scan_status: 'readme-scanned', stars: 1},
];
const element = (app, selector) => app.elements.get(selector);
const sourceRequests = app => app.requests.filter(url => new URL(url).pathname === '/source-browser.json');
const settle = () => new Promise(resolve => setImmediate(resolve));
const curatedState = app => Object.fromEntries(['q', 'group', 'category', 'kind', 'target', 'visible', 'lang', 'layout']
  .map(key => [key, app.api.state[key]]));

function application(query, options = {}) {
  const app = setup(query, {records: rows, pathname: options.pathname || '/'});
  const fetch = app.context.fetch;
  app.context.fetch = async (url, ...args) => {
    const response = await fetch(url, ...args);
    if (/^\/catalog(-index)?\.json$/.test(new URL(url).pathname)) {
      if (options.catalogFailure) return {ok: false, status: 503};
      const json = await response.json();
      if (options.unavailable) json.meta.source_index.resource_count = 0;
      return {ok: true, json: async () => json};
    }
    if (options.sourceFailure) return {ok: false, status: 503};
    return response;
  };
  app.api.applyLanguage();
  return app;
}

async function main() {
  // The static control is a hidden native button; no result-count preload is required.
  const markup = html.match(/<button\b[^>]*id="empty-search-repositories"[^>]*>/)[0];
  assert.match(markup, /type="button"/);
  assert.match(markup, /\bhidden\b/);
  assert.match(markup, /aria-describedby="empty-repositories-note"/);

  for (const language of ['en', 'zh']) {
    const pathname = language === 'zh' ? '/zh/' : '/';
    const query = '?q=protobuf&group=tools&category=dynamic-analysis&kind=tool&target=game'
      + '&sourceq=previous&source-target=protocol&topic=fixtures&sort=stars&layout=cards&keep=yes#catalog';
    const app = application(query, {pathname});
    await app.api.load();
    const button = element(app, '#empty-search-repositories');
    assert.equal(element(app, '#empty-state').hidden, false);
    assert.equal(button.hidden, false);
    assert.equal(element(app, '#empty-repositories-note').hidden, false);
    assert.equal(button.textContent, language === 'zh'
      ? '在自动采集的仓库中搜索“protobuf”'
      : 'Search automatically indexed repositories for “protobuf”');
    assert.equal(sourceRequests(app).length, 0, 'showing the action must not fetch the index');
    app.api.state.visible = 45;
    app.api.sourceState.visible = 72;
    const before = curatedState(app);
    const sourceBefore = Object.fromEntries(['target', 'topic', 'sort'].map(key => [key, app.api.sourceState[key]]));
    const input = element(app, '#source-search');
    let focusCount = 0;
    input.focus = () => { focusCount++; app.context.document.activeElement = input; };
    button.emit('click');
    button.emit('click'); // Hidden/repeated action must not duplicate the pending request.
    assert.equal(app.api.sourceState.mode, 'source-index');
    assert.equal(app.api.sourceState.q, 'protobuf');
    assert.equal(app.api.sourceState.visible, 24);
    assert.equal(input.value, 'protobuf');
    assert.equal(focusCount, 1);
    assert.equal(app.context.document.activeElement, input);
    assert.equal(button.hidden, true);
    assert.deepEqual(curatedState(app), before);
    assert.deepEqual(Object.fromEntries(['target', 'topic', 'sort'].map(key => [key, app.api.sourceState[key]])), sourceBefore);
    const location = app.context.location;
    assert.equal(location.pathname, pathname);
    assert.equal(location.hash, '#catalog');
    assert.equal(location.searchParams.get('view'), 'source-index');
    assert.equal(location.searchParams.get('sourceq'), 'protobuf');
    assert.equal(location.searchParams.get('q'), 'protobuf');
    assert.equal(location.searchParams.get('source-target'), 'protocol');
    assert.equal(location.searchParams.get('topic'), 'fixtures');
    assert.equal(location.searchParams.get('sort'), 'stars');
    assert.equal(location.searchParams.get('layout'), 'cards');
    assert.equal(location.searchParams.get('keep'), 'yes');
    const other = app.languageLinks.find(link => link.dataset.languageLink === (language === 'zh' ? 'en' : 'zh'));
    const counterpart = new URL(other.href, location.href);
    assert.equal(counterpart.pathname, language === 'zh' ? '/' : '/zh/');
    assert.equal(counterpart.searchParams.get('sourceq'), 'protobuf');
    assert.equal(counterpart.searchParams.get('q'), 'protobuf');
    assert.equal(counterpart.searchParams.get('target'), 'game');
    assert.equal(counterpart.searchParams.get('view'), 'source-index');
    assert.equal(counterpart.searchParams.get('layout'), 'cards');
    assert.equal(counterpart.hash, '#catalog');
    await settle();
    assert.equal(sourceRequests(app).length, 1);
    assert.equal(app.api.sourceState.loaded, true);
    assert.equal(app.api.sourceFiltered().length, 1);
    assert.equal(element(app, '#source-empty').hidden, true);
    element(app, '#mode-curated').emit('click');
    assert.deepEqual(curatedState(app), before);
    assert.equal(button.hidden, false);
    assert.equal(sourceRequests(app).length, 1);
    // A previously loaded index is reused, without a second fetch.
    button.emit('click'); await settle();
    assert.equal(sourceRequests(app).length, 1);
    assert.equal(focusCount, 2);
    element(app, '#mode-curated').emit('click');
    assert.deepEqual(curatedState(app), before);
    // Reset retains its original curated-only behavior and input focus.
    let curatedFocus = false;
    element(app, '#search-input').focus = () => { curatedFocus = true; };
    element(app, '#empty-reset').emit('click');
    assert.equal(curatedFocus, true);
    assert.equal(app.api.state.q, '');
    for (const key of ['group', 'category', 'kind', 'target']) assert.equal(app.api.state[key], 'all');
    assert.equal(app.api.state.visible, 15);
    assert.equal(button.hidden, true);
    assert.equal(element(app, '#empty-repositories-note').hidden, true);
    assert.equal(app.api.sourceState.q, 'protobuf');
    assert.deepEqual(Object.fromEntries(['target', 'topic', 'sort'].map(key => [key, app.api.sourceState[key]])), sourceBefore);
  }

  const edits = application('?q=protobuf');
  await edits.api.load();
  element(edits, '#search-input').value = 'Fixture';
  element(edits, '#search-input').emit('input');
  assert.equal(element(edits, '#empty-search-repositories').hidden, true);
  element(edits, '#search-input').value = '小程序';
  element(edits, '#search-input').emit('input');
  assert.equal(element(edits, '#empty-search-repositories').hidden, false);
  assert.equal(element(edits, '#empty-search-repositories').textContent,
    'Search automatically indexed repositories for “小程序”');
  assert.equal(sourceRequests(edits).length, 0);

  // Query text remains literal, including replacement tokens, HTML and whitespace.
  const literal = '  小程序 <img src=x onerror=bad()> $& {query}  ';
  const injected = application('?q=' + encodeURIComponent(literal), {pathname: '/zh/'});
  await injected.api.load();
  const button = element(injected, '#empty-search-repositories');
  assert.equal(button.textContent, '在自动采集的仓库中搜索“' + literal.trim() + '”');
  assert.equal(button.children.length, 0);
  let unsafeHTML = false;
  Object.defineProperty(button, 'innerHTML', {set(value) { if (String(value).includes('<img')) unsafeHTML = true; }});
  injected.api.state.lang = 'en'; injected.api.applyLanguage();
  assert.equal(button.textContent, 'Search automatically indexed repositories for “' + literal.trim() + '”');
  assert.equal(unsafeHTML, false);
  button.emit('click'); await settle();
  assert.equal(injected.api.sourceState.q, literal);
  assert.equal(element(injected, '#source-search').value, literal);
  assert.equal(injected.context.location.searchParams.get('sourceq'), literal);
  assert.equal(element(injected, '#source-empty').hidden, false, 'the transition does not promise a match');

  // Ordinary tab switching still keeps its independent repository query.
  const tabs = application('?q=protobuf&sourceq=separate');
  await tabs.api.load(); element(tabs, '#mode-sources').emit('click'); await settle();
  assert.equal(tabs.api.sourceState.q, 'separate');
  assert.equal(tabs.api.state.q, 'protobuf');

  for (const [query, options] of [
    ['?q=Fixture', {}], ['?q=', {}], ['?q=%20%20', {}],
    ['?q=protobuf', {unavailable: true}], ['?q=protobuf', {catalogFailure: true}],
  ]) {
    const app = application(query, options);
    await app.api.load();
    assert.equal(element(app, '#empty-search-repositories').hidden, true);
    assert.equal(element(app, '#empty-repositories-note').hidden, true);
    element(app, '#empty-search-repositories').emit('click'); await settle();
    assert.equal(sourceRequests(app).length, 0);
    assert.equal(app.api.sourceState.mode, 'curated');
  }

  const failure = application('?q=protobuf', {sourceFailure: true});
  await failure.api.load(); element(failure, '#empty-search-repositories').emit('click'); await settle();
  assert.equal(failure.api.sourceState.error, true);
  assert.equal(element(failure, '#source-error').hidden, false);
  assert.equal(element(failure, '#source-empty').hidden, true);
  assert.equal(failure.api.sourceState.q, 'protobuf');
  assert.equal(failure.context.location.searchParams.get('sourceq'), 'protobuf');
  assert.equal(sourceRequests(failure).length, 1);
  process.stdout.write('Curated empty-result repository transition passed\n');
}
main().catch(error => { console.error(error); process.exitCode = 1; });
