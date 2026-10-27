/* Load the freshly built site in an installed headless Chrome at desktop and phone widths.
   Every non-local request is blocked; screenshots are written for people to look at, not compared. */
'use strict';
const assert = require('node:assert/strict');
const {execFileSync} = require('node:child_process');
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');

const root = path.resolve(__dirname, '../..');
const dist = path.join(root, 'dist');
const screenshots = path.join(root, '.cache/browser-smoke');
const VIEWPORTS = [{name: 'desktop', width: 1280, height: 900}, {name: 'phone', width: 390, height: 844}];
const CHROME_CANDIDATES = ['/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'];

// CI must run the test; a local checkout without Chrome or the pinned package skips it with the reason.
function unavailable(reason) {
  if (process.env.CI) { console.error(`Browser smoke test cannot run: ${reason}`); process.exit(1); }
  console.log(`Skipping browser smoke test: ${reason}`); process.exit(0);
}
const chrome = process.env.CHROME_PATH || CHROME_CANDIDATES.find(file => fs.existsSync(file));
if (!chrome) unavailable('no Chrome or Chromium executable found; set CHROME_PATH to one.');
if (!fs.existsSync(chrome)) unavailable(`CHROME_PATH ${chrome} does not exist.`);
let puppeteer;
try { puppeteer = require('puppeteer-core'); } catch (_) { unavailable('puppeteer-core is not installed; run `npm ci --prefix tests/browser --ignore-scripts`.'); }

// Cloudflare Pages applies dist/_headers; the local server applies the same rules so CSP violations surface.
function headerRules(text) {
  const rules = [];
  for (const line of text.split('\n')) {
    if (!line.trim() || line.trimStart().startsWith('#')) continue;
    if (!/^\s/.test(line)) rules.push({pattern: line.trim(), headers: {}});
    else { const colon = line.indexOf(':'); rules.at(-1).headers[line.slice(0, colon).trim()] = line.slice(colon + 1).trim(); }
  }
  return rules;
}
const TYPES = {'.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.xml': 'application/xml',
  '.txt': 'text/plain; charset=utf-8', '.bib': 'application/x-bibtex; charset=utf-8', '.woff2': 'font/woff2'};
function server(rules) {
  return http.createServer((request, response) => {
    const {pathname} = new URL(request.url, 'http://127.0.0.1');
    let file = path.join(dist, decodeURIComponent(pathname));
    if (file !== dist && !file.startsWith(dist + path.sep)) { response.writeHead(403); response.end(); return; }
    if (fs.existsSync(file) && fs.statSync(file).isDirectory()) {
      if (!pathname.endsWith('/')) { response.writeHead(301, {Location: pathname + '/'}); response.end(); return; }
      file = path.join(file, 'index.html');
    }
    const found = fs.existsSync(file) && fs.statSync(file).isFile();
    const headers = {'Content-Type': TYPES[path.extname(found ? file : '.html')] || 'application/octet-stream'};
    for (const {pattern, headers: extra} of rules) {
      if (pattern.endsWith('*') ? pathname.startsWith(pattern.slice(0, -1)) : pathname === pattern) Object.assign(headers, extra);
    }
    response.writeHead(found ? 200 : 404, headers);
    response.end(fs.readFileSync(found ? file : path.join(dist, '404.html')));
  });
}

// Statuses group digits with the browser locale; read every number they contain.
const numbers = text => (text.match(/\d+(?:[,.\s]\d{3})*/g) || []).map(value => Number(value.replace(/\D/g, '')));

async function open(browser, origin, route, viewport, {javascript = true} = {}) {
  const page = await browser.newPage();
  await page.setJavaScriptEnabled(javascript);
  const problems = [], requested = [];
  page.setDefaultTimeout(20000);
  await page.setViewport({width: viewport.width, height: viewport.height});
  await page.setRequestInterception(true);
  page.on('request', request => {
    const url = request.url();
    if (url.startsWith(origin + '/')) requested.push(new URL(url).pathname);
    if (url.startsWith(origin + '/') || url.startsWith('data:')) request.continue();
    else { problems.push(`blocked non-local request ${url}`); request.abort('blockedbyclient'); }
  });
  page.on('console', message => {
    if (message.type() === 'error') problems.push(`console error: ${message.text()}`);
    // Chrome warns when a preload is unused or its request does not match the later fetch.
    else if (/preload/i.test(message.text())) problems.push(`console ${message.type()}: ${message.text()}`);
  });
  page.on('pageerror', error => problems.push(`uncaught exception: ${error.message}`));
  page.on('requestfailed', request => {
    if (request.url().startsWith(origin + '/')) problems.push(`failed request ${request.url()}: ${request.failure()?.errorText}`);
  });
  page.on('response', response => {
    if (response.url().startsWith(origin + '/') && response.status() >= 400) problems.push(`HTTP ${response.status()} ${response.url()}`);
  });
  if (javascript) {
    await page.exposeFunction('reportPolicyViolation', text => problems.push(`CSP violation: ${text}`));
    await page.evaluateOnNewDocument(() => document.addEventListener('securitypolicyviolation',
      event => window.reportPolicyViolation(`${event.violatedDirective} blocked ${event.blockedURI || 'inline content'}`)));
  }
  const response = await page.goto(origin + route, {waitUntil: 'networkidle0'});
  assert.equal(response.status(), 200, `${route} returned HTTP ${response.status()}`);
  return {page, problems, requested};
}
async function noOverflow(page, label) {
  const {scroll, inner} = await page.evaluate(() => ({scroll: document.scrollingElement.scrollWidth, inner: innerWidth}));
  assert(scroll <= inner, `${label}: the page scrolls horizontally (${scroll}px wide in a ${inner}px viewport)`);
}
const shot = (page, name) => page.screenshot({path: path.join(screenshots, name.replace(/[^a-z0-9]+/gi, '-').replace(/^-|-$/g, '') + '.png')});
// Report a failed assertion together with every browser problem the page logged, then close it.
async function visit(browser, origin, route, viewport, name, run, options) {
  const {page, problems, requested} = await open(browser, origin, route, viewport, options);
  let failure;
  try { await run(page, requested); } catch (error) { failure = error; }
  await shot(page, name).catch(() => {});
  await page.close();
  const messages = [failure?.message, ...problems].filter(Boolean);
  if (messages.length) throw new Error(messages.join('\n     '));
}
const count = (page, selector) => page.$$eval(selector, nodes => nodes.length);
const text = (page, selector) => page.$eval(selector, node => node.textContent);
const hidden = (page, selector) => page.$eval(selector, node => node.hidden);
const query = page => page.evaluate(() => location.search);
// Wait for the first card or the view's error state; aria-busy starts out false before any request.
const loaded = (page, cards, error) => page.waitForFunction((cards, error) => document.querySelector(cards) || !document.querySelector(error).hidden, {}, cards, error);
// Center controls instantly (the site scrolls smoothly) so the sticky header never intercepts the click.
async function press(page, selector) {
  await page.$eval(selector, node => node.scrollIntoView({block: 'center', behavior: 'instant'}));
  await page.click(selector);
}

// The deferred app.js reuses the catalog index preload, so its one request starts before DOMContentLoaded.
async function preloadedCatalog(page, label) {
  const entries = await page.evaluate(() => ({dcl: performance.getEntriesByType('navigation')[0].domContentLoadedEventStart,
    catalog: performance.getEntriesByType('resource').filter(entry => new URL(entry.name).pathname === '/catalog-index.json')
      .map(entry => ({initiator: entry.initiatorType, start: entry.startTime}))}));
  assert.equal(entries.catalog.length, 1, `${label}: one catalog request`);
  assert.equal(entries.catalog[0].initiator, 'link', `${label}: the catalog response comes from the preload`);
  assert(entries.catalog[0].start < entries.dcl, `${label}: the catalog request starts before DOMContentLoaded`);
}
const requests = (requested, file) => requested.filter(pathname => pathname === '/' + file).length;
// The complete catalog, with requirement text, is requested once right after the first render.
const completeCatalog = page => page.waitForFunction(() => performance.getEntriesByType('resource').some(entry => new URL(entry.name).pathname === '/catalog.json'));

async function dataAccess(page, language, viewport) {
  const label = `${language} data dialog ${viewport.name}`;
  // Mock writes in this isolated browser; never replace the user's clipboard during verification.
  await page.evaluate(() => Object.defineProperty(navigator, 'clipboard', {configurable: true,
    value: {writeText: async value => { window.copiedDataInstructions = value; }}}));
  await press(page, '[data-open-data]');
  assert.equal(await page.$eval('#data-dialog', dialog => dialog.open), true, `${label}: opens`);
  assert.equal(await text(page, '#data-title'), language === 'zh' ? '把资源合集带走。' : 'Take the collection with you.');
  const command = 'git clone https://github.com/reacher-z/Awesome-REA.git';
  assert.equal(await text(page, '#data-clone-command'), command);
  assert.equal(await count(page, 'a[href$=".zip"]'), 0, `${label}: no ZIP download links`);
  assert.equal(await page.$eval('#data-agent-details', details => details.open), false);
  for (let i = 0; i < 12; i++) {
    await page.keyboard.press('Tab');
    assert(await page.evaluate(() => document.querySelector('#data-dialog').contains(document.activeElement)), `${label}: focus stays inside`);
  }
  await press(page, '#data-clone-copy');
  await page.waitForFunction(() => window.copiedDataInstructions);
  assert.equal(await page.evaluate(() => window.copiedDataInstructions), command);
  assert.equal(await text(page, '#data-clone-status'), language === 'zh' ? '克隆命令已复制。' : 'Clone command copied.');
  await shot(page, label + ' clone');
  await page.evaluate(() => { navigator.clipboard.writeText = async () => { throw new Error('Unavailable'); }; });
  await press(page, '#data-clone-copy');
  await page.waitForFunction(() => document.activeElement.id === 'data-clone-command');
  assert.equal(await page.evaluate(() => window.getSelection().toString()), command);
  await page.evaluate(() => { navigator.clipboard.writeText = async value => { window.copiedDataInstructions = value; }; });
  await press(page, '#data-agent-details > summary');
  await press(page, '#data-copy');
  await page.waitForFunction(() => window.copiedDataInstructions.includes('data/README.md'));
  const instructions = await page.evaluate(() => window.copiedDataInstructions);
  assert(instructions.includes('https://github.com/reacher-z/Awesome-REA.git'));
  assert(instructions.includes('site/translations.zh-CN.json'));
  assert.equal(await text(page, '#data-copy-status'), language === 'zh' ? '指令已复制。' : 'Instructions copied.');
  await page.evaluate(() => { navigator.clipboard.writeText = async () => { throw new Error('Unavailable'); }; });
  await press(page, '#data-copy');
  await page.waitForFunction(() => document.activeElement.id === 'data-instructions');
  assert.equal(await page.evaluate(() => window.getSelection().toString()), await text(page, '#data-instructions'));
  await page.keyboard.press('/');
  assert(await page.evaluate(() => document.querySelector('#data-dialog').contains(document.activeElement)), `${label}: search shortcut leaves modal focus intact`);
  await noOverflow(page, label);
  assert(await page.$eval('#data-dialog', dialog => dialog.scrollWidth <= dialog.clientWidth), `${label}: no modal overflow`);
  await shot(page, label);
  await page.keyboard.press('Escape');
  assert.equal(await page.$eval('#data-dialog', dialog => dialog.open), false, `${label}: Escape closes`);
  assert(await page.evaluate(() => document.activeElement.matches('[data-open-data]')), `${label}: trigger regains focus`);
  await press(page, '[data-open-data]');
  assert.equal(await text(page, '#data-copy-status'), '', `${label}: old status clears`);
  assert.equal(await text(page, '#data-clone-status'), '', `${label}: old clone status clears`);
  await press(page, '#data-close');
  assert.equal(await page.$eval('#data-dialog', dialog => dialog.open), false, `${label}: close button`);
}

async function homepage(page, language, viewport, data, requested) {
  const label = `${language} homepage ${viewport.name}`;
  const total = data.catalog.resources.length;
  await loaded(page, '#resource-grid .resource-card', '#error-state');
  await preloadedCatalog(page, label);
  await completeCatalog(page);
  assert.equal(requests(requested, 'catalog-index.json'), 1, `${label}: one catalog-index.json request per load`);
  assert.equal(requests(requested, 'catalog.json'), 1, `${label}: one catalog.json request per load`);
  assert.equal(requests(requested, 'source-browser.json'), 0, `${label}: repository data waits for the Repositories view`);
  assert.equal(await hidden(page, '#error-state'), true, `${label}: the curated catalog loads`);
  assert.equal(await count(page, '#resource-grid .resource-card'), Math.min(15, total), `${label}: initial curated cards`);
  assert(numbers(await text(page, '#results-status')).includes(total), `${label}: status names all ${total} curated resources`);
  assert(await page.$$eval('#resource-grid .card-title-link', links => links.every(link => link.textContent.trim() && link.href.startsWith('http'))));
  await noOverflow(page, label);
  await dataAccess(page, language, viewport);

  // Search, then clear: a record's own displayed name finds it among a narrower result set.
  const title = (await text(page, '#resource-grid .card-title-link')).trim();
  await page.type('#search-input', title);
  const found = numbers(await text(page, '#results-status'))[0];
  assert(found >= 1 && found < total, `${label}: searching "${title}" narrows the ${total} resources (got ${found})`);
  assert((await page.$$eval('#resource-grid .card-title-link', links => links.map(link => link.textContent.trim()))).includes(title));
  assert.equal(await hidden(page, '#clear-filters'), false);
  assert(new URLSearchParams(await query(page)).has('q'));
  await press(page, '#clear-filters');
  assert.equal(await page.$eval('#search-input', input => input.value), '');
  assert(numbers(await text(page, '#results-status')).includes(total));
  assert.equal(new URLSearchParams(await query(page)).has('q'), false);
  assert.equal(await hidden(page, '#clear-filters'), true);

  // Show More reveals the next 15 curated cards; requirements open in place.
  await press(page, '#load-more');
  assert.equal(await count(page, '#resource-grid .resource-card'), Math.min(30, total), `${label}: curated Show More`);
  assert.equal(await count(page, '#resource-grid .resource-card > .card-meta .resource-evidence-link'), 0);
  assert.equal(await count(page, '#resource-grid .resource-card details .resource-evidence-link'), Math.min(30, total));
  await press(page, '#resource-grid .resource-card details.requirements summary');
  const expanded = await page.$eval('#resource-grid .resource-card details.requirements', details => ({open: details.open,
    items: details.querySelectorAll('li:not(.requirements-pending)').length, height: details.querySelector('ul').getBoundingClientRect().height}));
  assert(expanded.open && expanded.items > 0 && expanded.height > 0, `${label}: requirements expand visibly`);
  await noOverflow(page, label + ' with requirements open');
  await shot(page, `${language} homepage ${viewport.name} curated`);

  // The repository view loads its own payload, 24 cards at a time.
  const repositories = data.browser.resources.length;
  await press(page, '#mode-sources');
  await loaded(page, '#source-results .source-card', '#source-error');
  assert.equal(requests(requested, 'source-browser.json'), 1, `${label}: the Repositories view requests its data once`);
  assert.equal(await hidden(page, '#source-error'), true, `${label}: the repository index loads`);
  assert.equal(await count(page, '#source-results .source-card'), Math.min(24, repositories), `${label}: initial repository cards`);
  assert(numbers(await text(page, '#source-status')).includes(repositories), `${label}: status names all ${repositories} repositories`);
  assert.equal(await text(page, '#source-more-count'), '+' + Math.min(24, Math.max(0, repositories - 24)));
  await press(page, '#source-more');
  assert.equal(await count(page, '#source-results .source-card'), Math.min(48, repositories), `${label}: repository Show More`);
  await press(page, '#source-results .source-card details.source-record-details > summary');
  const firstSource = await page.$eval('#source-results .source-card', card => ({id:card.dataset.recordId,
    topics:card.querySelectorAll('.source-topic-chip').length, evidenceOpen:card.querySelector('.source-scan-evidence').open}));
  const expectedSource = data.browser.resources.find(record => record.id === firstSource.id);
  assert.equal(firstSource.topics, expectedSource.topics.length, `${label}: every topic appears once`);
  assert.equal(firstSource.evidenceOpen, false);
  await press(page, '#source-results .source-card .source-scan-evidence > summary');
  const fingerprints = await page.$$eval('#source-results .source-card:first-child .source-scan-evidence code', nodes => nodes.map(node => node.textContent));
  assert(fingerprints.includes(expectedSource.readme_sha256), `${label}: complete SHA256 available`);
  if (expectedSource.readme_git_sha) assert(fingerprints.includes(expectedSource.readme_git_sha), `${label}: complete advertised Git revision available`);
  await noOverflow(page, label + ' full scan evidence');
  await press(page, '#source-results .source-card details.source-record-details > summary');
  await press(page, '#source-more');
  const restoredSource = await page.$eval('#source-results .source-card', card => ({outer:card.querySelector('.source-record-details').open, inner:card.querySelector('.source-scan-evidence').open}));
  assert.deepEqual(restoredSource, {outer:false,inner:true}, `${label}: independent disclosure states survive Show More`);
  await press(page, '#source-results .source-card details.source-record-details > summary');
  await press(page, '#source-results .source-card .source-scan-evidence > summary');
  await noOverflow(page, label + ' repositories');
  await shot(page, `${language} homepage ${viewport.name} repositories`);

  // A target filter survives the language switch, an ordinary link to the other homepage.
  await press(page, '#mode-curated');
  const games = data.catalog.resources.filter(record => (record.targets || []).includes('game')).length;
  await press(page, '#curated-view [data-target="game"]');
  assert(numbers(await text(page, '#results-status'))[0] === games, `${label}: Game filter shows ${games} resources`);
  const other = language === 'zh' ? 'en' : 'zh';
  const current = await page.$$eval('[data-language-link]', links => links.filter(link => link.getAttribute('aria-current') === 'true').map(link => link.dataset.languageLink));
  assert.deepEqual(current, [language], `${label}: the current language is marked`);
  // Fragment navigation updates the links too; arrow keys on them never navigate (WCAG 3.2.2).
  await page.evaluate(() => { location.hash = 'catalog'; });
  await page.waitForFunction(link => document.querySelector(`[data-language-link="${link}"]`).getAttribute('href').endsWith('#catalog'), {}, other);
  const before = page.url();
  for (const link of [language, other]) {
    await page.focus(`[data-language-link="${link}"]`);
    for (const key of ['ArrowDown', 'ArrowUp']) await page.keyboard.press(key);
  }
  assert.equal(page.url(), before, `${label}: arrow keys keep the page`);
  assert.equal(await page.evaluate(() => document.activeElement.dataset.languageLink), other);
  await Promise.all([page.waitForNavigation({waitUntil: 'networkidle0'}), page.keyboard.press('Enter')]);
  await loaded(page, '#resource-grid .resource-card', '#error-state');
  await preloadedCatalog(page, label + ' after switching language');
  await completeCatalog(page);
  assert.equal(requests(requested, 'catalog-index.json'), 2, `${label}: one catalog-index.json request on each homepage`);
  assert.equal(requests(requested, 'catalog.json'), 2, `${label}: one catalog.json request on each homepage`);
  const switched = new URL(page.url());
  assert.equal(switched.pathname, other === 'zh' ? '/zh/' : '/');
  assert.equal(switched.searchParams.get('target'), 'game', `${label}: the language switch keeps the filter`);
  assert.equal(switched.hash, '#catalog', `${label}: the language switch keeps the fragment`);
  assert.equal(await page.evaluate(() => document.documentElement.lang), other === 'zh' ? 'zh-CN' : 'en');
  assert.equal(await page.$eval('#curated-view [data-target="game"]', button => button.getAttribute('aria-pressed')), 'true');
  assert.equal(numbers(await text(page, '#results-status'))[0], games);
  await noOverflow(page, label + ' after switching language');
}

// Without scripting, the catalog's inert controls and loading text give way to the static directory links.
async function withoutScript(page, language, viewport) {
  const label = `${language} homepage without JavaScript ${viewport.name}`;
  assert(await page.$eval('[data-open-data]', link => !link.hasAttribute('download') && link.getAttribute('href') === 'https://github.com/reacher-z/Awesome-REA' && link.getClientRects().length > 0), `${label}: repository access works without a dialog`);
  const view = await page.evaluate(() => {
    const shown = selector => [...document.querySelectorAll(selector)].filter(node => node.getClientRects().length).length;
    const heading = document.querySelector('#catalog-title').getBoundingClientRect(), note = document.querySelector('.noscript-note');
    return {controls: shown('#search-input, #source-search, .target-filter, select, .index-mode, #results-status, #source-status'),
      loading: /Loading|正在加载/.test(document.body.innerText), gap: note && note.getClientRects().length ? note.getBoundingClientRect().top - heading.bottom : null,
      links: [...document.querySelectorAll('[data-language-link]')].map(link => [link.dataset.languageLink, link.getAttribute('href'), link.getAttribute('aria-current')])};
  });
  assert.equal(view.controls, 0, `${label}: no search field, filters, selects, tabs or status`);
  assert.equal(view.loading, false, `${label}: no loading text`);
  assert(view.gap !== null && view.gap >= 0 && view.gap < 100, `${label}: the static directory links follow the collection heading (gap ${view.gap})`);
  assert.deepEqual(view.links, [['en', '/', language === 'en' ? 'true' : null], ['zh', '/zh/', language === 'zh' ? 'true' : null]], `${label}: language links`);
  await noOverflow(page, label);
}

async function paperDirectory(page, route, viewport, javascript = true) {
  const label = `${route} ${viewport.name}`;
  const first = '.paper-card';
  const before = await page.$eval(first, card => ({scope: card.querySelector('.paper-scope').textContent,
    authors: card.querySelector('.paper-authors').textContent, citation: card.querySelector('a[type="application/x-bibtex"]').getAttribute('href')}));
  assert.equal(await page.evaluate(() => document.documentElement.dataset.paperLayout), 'compact');
  const metaBeside = await page.$$eval('.paper-card', cards => cards.filter(card =>
    card.querySelector('.paper-meta').getBoundingClientRect().top < card.querySelector('h3').getBoundingClientRect().bottom - 1).length);
  assert.equal(metaBeside, 0, `${label}: every row puts year, venue and status on their own line under the title (${metaBeside} beside it)`);
  assert.equal(await page.$eval(first + ' .paper-details', node => node.open), false);
  await press(page, first + ' .paper-details > summary');
  const expanded = await page.$eval(first + ' .paper-details', details => ({open: details.open,
    scopeVisible: details.querySelector('.paper-scope').getBoundingClientRect().height > 0,
    scope: details.querySelector('.paper-scope').textContent, authors: details.querySelector('.paper-authors').textContent,
    citation: details.querySelector('a[type="application/x-bibtex"]').getAttribute('href')}));
  assert.equal(expanded.open, true); assert.equal(expanded.scopeVisible, true);
  for (const key of ['scope', 'authors', 'citation']) assert.equal(expanded[key], before[key], `${label}: ${key} survives disclosure`);
  await noOverflow(page, label + ' expanded evidence');
  await press(page, first + ' .paper-details > summary');
  if (javascript) {
    assert.equal(await page.$eval('#paper-more-filters', node => node.open), false);
    await press(page, '#paper-more-filters > summary');
    await page.select('#paper-layout', 'cards');
    assert.equal(new URL(page.url()).searchParams.get('layout'), 'cards');
    assert.equal(await page.$eval(first, card => card.querySelector('.paper-scope').parentElement === card), true);
    await page.select('#paper-layout', 'compact');
    const restored = await page.$eval(first, card => ({scope: card.querySelector('.paper-scope').textContent,
      copies: card.querySelectorAll('.paper-scope').length, inDetails: !!card.querySelector('.paper-details > .paper-scope')}));
    assert.equal(restored.scope, before.scope); assert.equal(restored.copies, 1); assert.equal(restored.inDetails, true);
    const selectedYear = await page.$eval('#paper-year option:not([value="all"])', option => option.value);
    await page.select('#paper-year', selectedYear);
    const visibleYears = await page.$$eval('.paper-card:not([hidden]) .paper-year', nodes => nodes.map(node => node.textContent));
    assert(visibleYears.length > 0 && visibleYears.every(year => year === selectedYear));
    assert.equal(numbers(await text(page, '#paper-results'))[0], visibleYears.length);
    const language = new URL(await page.$eval('.papers-language', link => link.href));
    assert.equal(language.searchParams.get('year'), selectedYear);
    await press(page, '#paper-clear');
    await press(page, '#paper-more-filters > summary');
  }
  await noOverflow(page, label + ' compact list');
}

async function staticPage(page, route, viewport) {
  const label = `${route} ${viewport.name}`;
  assert((await page.$eval('h1', heading => heading.textContent.trim())).length > 0, `${label}: visible heading`);
  await noOverflow(page, label);
  if (route === '/papers/' || route === '/zh/papers/') await paperDirectory(page, route, viewport);
}

(async () => {
  execFileSync(process.env.PYTHON || 'python3', ['scripts/build_site.py'], {cwd: root, stdio: 'inherit'});
  const read = file => JSON.parse(fs.readFileSync(path.join(dist, file), 'utf8'));
  const data = {catalog: read('catalog.json'), browser: read('source-browser.json')};
  const category = fs.readdirSync(path.join(dist, 'zh/browse')).filter(name => fs.statSync(path.join(dist, 'zh/browse', name)).isDirectory()).sort()[0];
  const routes = ['/papers/', '/zh/papers/', '/resources/', '/zh/resources/', '/cases/', '/about/', '/zh/about/',
    '/browse/', `/zh/browse/${category}/`, `/resources/${data.catalog.resources[0].id}/`];
  fs.rmSync(screenshots, {recursive: true, force: true}); fs.mkdirSync(screenshots, {recursive: true});
  const site = server(headerRules(fs.readFileSync(path.join(dist, '_headers'), 'utf8')));
  await new Promise(resolve => site.listen(0, '127.0.0.1', resolve));
  const origin = `http://127.0.0.1:${site.address().port}`;
  const browser = await puppeteer.launch({executablePath: chrome, headless: true, args: ['--lang=en-US']});
  const failures = [];
  const check = async (label, run) => {
    try { await run(); console.log(`ok   ${label}`); } catch (error) { failures.push(label); console.error(`FAIL ${label}\n     ${error.message}`); }
  };
  try {
    // Viewports are independent. Separate contexts isolate cookies, storage and
    // clipboard mocks; each viewport keeps its complete sequential interaction suite.
    const runs = await Promise.allSettled(VIEWPORTS.map(async viewport => {
      const context = await browser.createBrowserContext();
      try {
      for (const language of ['en', 'zh']) {
        await check(`${language} homepage at ${viewport.width}px`, () => visit(context, origin, language === 'zh' ? '/zh/' : '/', viewport,
          `${language} homepage ${viewport.name} switched to ${language === 'zh' ? 'en' : 'zh'}`, (page, requested) => homepage(page, language, viewport, data, requested)));
      }
      for (const language of ['en', 'zh']) {
        await check(`${language} homepage without JavaScript at ${viewport.width}px`, () => visit(context, origin, language === 'zh' ? '/zh/' : '/', viewport,
          `${language} homepage ${viewport.name} without JavaScript`, page => withoutScript(page, language, viewport), {javascript: false}));
      }
      for (const route of ['/papers/', '/zh/papers/']) {
        await check(`${route} without JavaScript at ${viewport.width}px`, () => visit(context, origin, route, viewport,
          `${route} ${viewport.name} without JavaScript`, page => paperDirectory(page, route, viewport, false), {javascript: false}));
      }
      for (const route of routes) {
        await check(`${route} at ${viewport.width}px`, () => visit(context, origin, route, viewport, `${route} ${viewport.name}`, page => staticPage(page, route, viewport)));
      }
      } finally { await context.close(); }
    }));
    for (const result of runs) if (result.status === 'rejected') throw result.reason;
  } finally {
    await browser.close(); site.close();
  }
  console.log(`Screenshots for review: ${path.relative(root, screenshots)}/`);
  if (failures.length) { console.error(`${failures.length} browser smoke check(s) failed.`); process.exitCode = 1; }
  else console.log('Browser smoke checks passed.');
})().catch(error => { console.error(error); process.exitCode = 1; });
