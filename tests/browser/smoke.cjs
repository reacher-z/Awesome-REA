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
    // Chrome warns when a preload is unused or its request does not match the later fetch. Without JavaScript
    // nothing can use a fetch preload, so only that warning is expected there.
    else if (/preload/i.test(message.text()) && (javascript || !/preloaded using link preload but not used/.test(message.text()))) {
      problems.push(`console ${message.type()}: ${message.text()}`);
    }
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
// Wide compact rows keep a closed details toggle directly under the row's links, however long the description is.
async function toggleDrift(page, card, links, toggle) {
  return page.$$eval(card, (cards, links, toggle) => cards.map(row => {
    const above = row.querySelector(links), below = row.querySelector(toggle);
    return above && below ? below.getBoundingClientRect().top - above.getBoundingClientRect().bottom : null;
  }).filter(gap => gap !== null), links, toggle);
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
// paper-search.js fetches the content-addressed index its page preloads, once, starting before DOMContentLoaded.
async function preloadedPaperIndex(page, label) {
  const entries = await page.evaluate(() => ({dcl: performance.getEntriesByType('navigation')[0].domContentLoadedEventStart,
    index: performance.getEntriesByType('resource').filter(entry => /^\/assets\/paper-search-index\.[0-9a-f]{16}\.json$/.test(new URL(entry.name).pathname))
      .map(entry => ({initiator: entry.initiatorType, start: entry.startTime}))}));
  assert.equal(entries.index.length, 1, `${label}: one paper search index request`);
  assert.equal(entries.index[0].initiator, 'link', `${label}: the index response comes from the preload`);
  assert(entries.index[0].start < entries.dcl, `${label}: the index request starts before DOMContentLoaded`);
}
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

// The homepage shows real rows without scripts; search in place loads its index only on first use.
async function newHomepage(page, language, viewport, data, requested, javascript = true) {
  const label = `${language} new homepage ${viewport.name}`;
  const total = data.catalog.resources.length;
  assert.equal(await text(page, 'html').then(() => page.evaluate(() => document.documentElement.lang)), language === 'zh' ? 'zh-CN' : 'en');
  assert.equal(await count(page, 'h1'), 1, `${label}: one heading`);
  assert.equal(await count(page, '[data-cards] > .card'), 7, `${label}: the drawer opens with its featured rows`);
  assert.equal(numbers(await text(page, '.hero-stats strong'))[0], total, `${label}: the stated resource count is the catalog's`);
  assert.equal(await page.$eval('[data-show-all]', link => new URL(link.href).pathname), language === 'zh' ? '/zh/resources/' : '/resources/');
  assert.equal(await page.$eval('.site-header a[hreflang]', link => link.getAttribute('href')), language === 'zh' ? '/' : '/zh/');
  await noOverflow(page, label);
  if (!javascript) return;
  const index = language === 'zh' ? 'search-index.zh.json' : 'search-index.json';
  assert.equal(requests(requested, index), 0, `${label}: the search index waits for the first search`);
  assert.equal(requests(requested, 'catalog-index.json') + requests(requested, 'catalog.json'), 0, `${label}: the collection data is not loaded`);
  await page.$eval('[data-search-input]', node => node.scrollIntoView({block: 'center', behavior: 'instant'}));
  await page.type('[data-search-input]', 'ghidra');
  await page.waitForFunction(() => document.querySelector('[data-cards] > .card') && new URL(location.href).searchParams.get('q') === 'ghidra', {timeout: 15000});
  assert.equal(requests(requested, index), 1, `${label}: one search index request`);
  await page.waitForFunction(id => document.querySelector(`[data-cards] > .card[data-id="${id}"]`), {}, 'ghidra');
  assert.equal(await page.$eval('.site-header a[hreflang]', link => new URL(link.href).search), '?q=ghidra', `${label}: the language link keeps the search`);
  await noOverflow(page, label + ' with a search');
  // Arrow keys move the selection; Escape clears; zero results offer other routes rather than a count of nothing.
  await page.waitForSelector('[data-cards] > .card.is-active');
  await page.keyboard.press('ArrowDown');
  await page.keyboard.press('ArrowUp');
  assert.equal(await count(page, '[data-cards] > .card.is-active'), 1, `${label}: one result is selected`);
  await page.keyboard.press('Escape');
  await page.waitForFunction(() => !document.querySelector('[data-search-input]').value && !new URL(location.href).searchParams.get('q'));
  assert.equal(await count(page, '[data-cards] > .card.is-active'), 0, `${label}: Escape clears the selection`);
  await page.type('[data-search-input]', 'zzzzqqqq');
  // The empty state can appear after the first few letters; wait until it describes the whole query.
  await page.waitForSelector('[data-cards] > .empty a[href*="sourceq=zzzzqqqq"]');
  assert.equal(await page.$eval('.drawer-foot', foot => foot.hidden), true, `${label}: no results, no "Show all" footer`);
  assert(await page.$eval('[data-cards] > .empty', box => !!box.querySelector('[data-empty-clear]') && !!box.querySelector('a[href*="sourceq=zzzzqqqq"]')), `${label}: the empty state offers other routes`);
  await page.click('[data-empty-clear]');
  await page.waitForFunction(() => document.querySelector('[data-cards] > .card'));
  await page.type('[data-search-input]', 'ghidra');
  await page.waitForSelector('[data-cards] > .card.is-active');
  await Promise.all([page.waitForNavigation({waitUntil: 'load'}), page.keyboard.press('Enter')]);
  assert.match(new URL(page.url()).pathname, /\/resources\/[a-z0-9-]+\/$/, `${label}: Enter opens the selected result`);
}

// The evidence-class select narrows the drawer in place, and the info button explains the classes.
async function homepageClassFilter(page, language, viewport) {
  const label = `${language} homepage evidence-class filter ${viewport.name}`;
  assert.equal(await page.$eval('[data-class-select]', select => select.options[0].value), '', `${label}: all classes is the default`);
  await page.select('[data-class-select]', '0');
  await page.waitForFunction(() => {
    const cards = [...document.querySelectorAll('[data-cards] > .card')];
    return new URL(location.href).searchParams.get('class') === '0' && cards.length && cards.every(card => card.querySelector('.card-class-0'));
  }, {timeout: 15000});
  const classes = await page.$$eval('[data-cards] > .card .card-class', nodes => nodes.map(node => node.textContent.trim()));
  assert(classes.length > 0, `${label}: rows render`);
  assert(classes.every(text => text === 'C0'), `${label}: only C0 rows remain`);
  assert.equal(await page.$eval('[data-class-select]', select => select.value), '0', `${label}: the select keeps its choice`);
  await page.click('.info-btn');
  assert.equal(await page.$eval('.info-btn', button => button.getAttribute('aria-expanded')), 'true', `${label}: the info button opens the class criteria`);
  assert.equal(await page.$eval('.info-pop', node => getComputedStyle(node).visibility), 'visible', `${label}: the criteria are visible`);
  await page.keyboard.press('Escape');
  await page.select('[data-class-select]', '');
  await page.waitForFunction(() => !new URL(location.href).searchParams.get('class') && document.querySelectorAll('[data-cards] > .card').length === 7);
}

// Past the hero field the sticky bar offers search; it opens over the page and closes back to the same place.
// /resources/ is split into static pages of at most 100 rows; filters search the whole catalog in place,
// and a record or section link finds the page that lists it.
async function resourceListing(page, language, viewport, data) {
  const label = `${language} resources ${viewport.name}`;
  const total = data.catalog.resources.length;
  const route = language === 'zh' ? '/zh/resources/' : '/resources/';
  const perPage = 100;
  const staticPages = Math.max(1, Math.ceil(total / perPage));
  const rows = () => count(page, '[data-cards] > .card');
  assert.equal(await rows(), Math.min(perPage, total), `${label}: the first page holds the first ${perPage} rows`);
  const pageMap = await page.evaluate(async url => (await fetch(url)).json(), '/resources/pages.json');
  const mapped = data.catalog.resources.map(record => pageMap[record.id]);
  assert.ok(mapped.every(number => Number.isInteger(number) && number >= 1 && number <= staticPages), `${label}: every record has a static page`);
  if (staticPages > 1) {
    assert.equal(await page.$eval('[data-pager] a[data-page="2"]', link => new URL(link.href).pathname), `${route}page/2/`, `${label}: the pager links the next static page`);
  }
  await noOverflow(page, label);
  const before = await page.$eval('[data-results-meta]', node => node.textContent);
  await press(page, '.page-head .folder[data-target="protocol"]');
  await page.waitForFunction(() => new URL(location.href).searchParams.get('target') === 'protocol', {timeout: 20000});
  // The search index loads on the first interaction, so the count changes once it arrives.
  await page.waitForFunction(text => document.querySelector('[data-results-meta]').textContent !== text, {timeout: 20000}, before)
    .catch(() => assert.fail(`${label}: the count follows the filter`));
  if (staticPages > 1) {
    const shown = await page.$$eval('[data-cards] > .card[data-id]', nodes => nodes.map(node => node.dataset.id));
    assert.ok(shown.some(id => pageMap[id] > 1), `${label}: the filter searches rows from every static page`);
  }
  await page.goto(page.url().split('?')[0] + '?target=protocol&kind=tool');
  // The static rows show first; the filtered rows replace them once the search index arrives.
  await page.waitForFunction(() => {
    const kinds = [...document.querySelectorAll('[data-cards] > .card .callno')].map(node => node.textContent);
    return kinds.length > 0 && kinds.every(text => /tool|工具/i.test(text));
  }, {timeout: 20000}).catch(() => assert.fail(`${label}: a shared link opens the same filter`));
  // On a narrowed list a section's count follows the filters, and its link filters to that many rows.
  const sectionCounts = () => page.$$eval('[data-section-link]', links => links.map(link => [link.dataset.section, Number(link.querySelector('.count').textContent.replace(/\D/g, ''))]));
  const narrowed = await sectionCounts();
  const narrowedTotal = narrowed.reduce((sum, [, number]) => sum + number, 0);
  assert.ok(narrowedTotal < total, `${label}: section counts follow the filters`);
  const [section, sectionTotal] = narrowed.find(([, number]) => number > 0);
  await page.$eval(`[data-section-link][data-section="${section}"]`, node => node.click());
  await page.waitForFunction(key => new URL(location.href).searchParams.get('section') === key, {}, section);
  assert.deepEqual(numbers(await text(page, '[data-results-meta]')).slice(-1), [sectionTotal], `${label}: the section filter shows the rows its count promised`);
  assert.equal(await page.$eval(`[data-section-link][data-section="${section}"]`, node => node.getAttribute('aria-current')), 'true', `${label}: the chosen section is marked`);
  await page.$eval(`[data-section-link][data-section="${section}"]`, node => node.click());
  await page.waitForFunction(() => !new URL(location.href).searchParams.has('section'));
  // The Evidence class select narrows to its stated count; removing its chip resets the select.
  await page.goto(page.url().split('?')[0]);
  const classOption = await page.$eval('.results-bar [data-class-select] option[value="0"]', option => Number(option.textContent.replace(/\D/g, '').slice(1)));
  await page.select('.results-bar [data-class-select]', '0');
  await page.waitForFunction(() => new URL(location.href).searchParams.get('class') === '0'
    && [...document.querySelectorAll('[data-cards] > .card')].every(card => card.querySelector('.card-class-0')), {timeout: 20000});
  assert.deepEqual(numbers(await text(page, '[data-results-meta]')).slice(-1), [classOption], `${label}: the class filter shows the rows its option promised`);
  await page.click('[data-active] [data-unset="class"]');
  await page.waitForFunction(() => !new URL(location.href).searchParams.has('class'));
  assert.equal(await page.$eval('.results-bar [data-class-select]', select => select.value), '', `${label}: removing the class chip resets the select`);
  // Clearing returns to the first static page, where a section link jumps to its heading and is shareable.
  await page.goto(page.url().split('?')[0]);
  assert.equal(await rows(), Math.min(perPage, total), `${label}: clearing the filters returns the first static page`);
  await page.$eval('[data-section-link]', node => node.click());
  await page.waitForFunction(() => location.hash.startsWith('#heading-'));
  assert.equal(new URL(page.url()).search, '', `${label}: on the static list a section link only jumps`);
  assert.equal(new URL(page.url()).pathname, route);
  assert.deepEqual(await page.evaluate(() => [[61, 1], [64, 1], [65, 1], [65, 2], [121, 2], [120, 2], [0, 1], [3, 1]].map(([rows, page]) => {
    const {pages, start, end} = window.REA_SEARCH.pageRange(rows, 60, page);
    return [pages, end - start];
  })), [[1, 61], [1, 64], [2, 60], [2, 5], [2, 61], [2, 60], [1, 0], [1, 3]], `${label}: a last page never holds under five rows`);
  // A legacy /resources/#id link opens the static page that lists that record.
  const last = data.catalog.resources[data.catalog.resources.length - 1].id;
  const lastPage = pageMap[last];
  await page.goto(`${new URL(page.url()).origin}${route}#${last}`);
  await page.waitForFunction(expected => location.pathname === expected, {timeout: 10000}, lastPage > 1 ? `${route}page/${lastPage}/` : route);
  await page.waitForFunction(() => { const node = document.getElementById(location.hash.slice(1)); if (!node) return false; const top = node.getBoundingClientRect().top; return top >= 0 && top < innerHeight; }, {timeout: 10000});
  if (staticPages > 1) assert.ok(await rows() <= perPage, `${label}: a later static page holds at most ${perPage} rows`);
}

async function homepageScrolledSearch(page, language, viewport) {
  const label = `${language} scrolled search ${viewport.name}`;
  const phone = viewport.width < 768;
  const shown = selector => page.$eval(selector, node => getComputedStyle(node).visibility === 'visible' && +getComputedStyle(node).opacity > 0 && node.getBoundingClientRect().width > 0);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForFunction(() => !document.documentElement.classList.contains('is-scrolled'));
  const before = await page.$eval('.search-trigger', node => node.getBoundingClientRect().left);
  if (!phone) assert.equal(await page.$eval('.search-trigger', node => getComputedStyle(node).visibility), 'hidden', `${label}: hidden while the hero field shows`);
  await page.evaluate(() => window.scrollTo(0, 1100));
  await page.waitForFunction(() => document.documentElement.classList.contains('is-scrolled'));
  const opener = phone ? '.mbar-search' : '.search-trigger';
  // The phone bar slides in, so wait until it has arrived before aiming at it.
  await page.waitForFunction(selector => {
    const node = document.querySelector(selector);
    return getComputedStyle(node).visibility === 'visible' && node.getBoundingClientRect().top >= 0;
  }, {}, opener);
  assert(await shown(opener), `${label}: search shows once the hero field is gone`);
  const star = phone ? '.mbar-star' : '.site-header .star-btn';
  assert(await shown(star) && await page.$eval(star, node => node.getBoundingClientRect().top >= 0), `${label}: the star stays on screen after scrolling`);
  if (!phone) assert.equal(await page.$eval('.search-trigger', node => node.getBoundingClientRect().left), before, `${label}: the header does not shift`);
  const place = await page.evaluate(() => window.scrollY);
  const box = await page.$eval(opener, node => { const rect = node.getBoundingClientRect(); return {x: rect.left + rect.width / 2, y: rect.top + rect.height / 2}; });
  await page.mouse.click(box.x, box.y);
  await page.waitForFunction(() => document.querySelector('#palette').open && document.activeElement === document.querySelector('#palette input'));
  await page.type('#palette input', 'ghidra');
  await page.waitForSelector('#palette [role="option"]');
  await page.keyboard.press('Escape');
  await page.waitForFunction(() => !document.querySelector('#palette').open);
  assert.equal(await page.evaluate(selector => document.activeElement === document.querySelector(selector), opener), true, `${label}: Escape returns focus to the button`);
  assert.equal(await page.evaluate(() => window.scrollY), place, `${label}: closing keeps the scroll position`);
  await page.keyboard.down('Control');
  await page.keyboard.press('k');
  await page.keyboard.up('Control');
  await page.waitForFunction(() => document.querySelector('#palette').open);
  await page.keyboard.press('Escape');
  await page.waitForFunction(() => !document.querySelector('#palette').open);
  await page.evaluate(() => document.activeElement.blur());
  await page.keyboard.press('/');
  await page.waitForFunction(() => document.querySelector('#palette').open);
  await page.keyboard.press('Escape');
  await page.waitForFunction(() => !document.querySelector('#palette').open);
  assert.equal(await page.evaluate(() => window.scrollY), place, `${label}: the shortcuts keep the scroll position`);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForFunction(() => !document.documentElement.classList.contains('is-scrolled'));
  await page.keyboard.press('/');
  await page.waitForFunction(() => document.activeElement && document.activeElement.matches('[data-search-input]'));
  assert.equal(await page.$eval('#palette', dialog => dialog.open), false, `${label}: "/" uses the hero field while it shows`);
}

// An old link into the collection's filters still opens them, now on the explorer.
async function oldHomepageLink(page, language) {
  await page.waitForFunction(() => location.pathname.endsWith('/explore/') && document.querySelector('#resource-grid .resource-card'), {timeout: 15000});
  const url = new URL(page.url());
  assert.equal(url.pathname, language === 'zh' ? '/zh/explore/' : '/explore/');
  assert.equal(url.searchParams.get('category'), 'game-analysis', 'the old query survives the redirect');
}

async function homepage(page, language, viewport, data, requested) {
  const label = `${language} explorer ${viewport.name}`;
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
  // Compact rows name each entry's reviewed targets at every width, beside its category.
  const targets = await page.$$eval('#resource-grid .resource-card', cards => cards.map(card => {
    const labels = card.querySelector('.card-meta > .card-targets');
    return Boolean(labels?.textContent.trim() && labels.getClientRects().length && labels.getBoundingClientRect().right <= innerWidth);
  }));
  assert(targets.length && targets.every(Boolean), `${label}: every compact row shows its target labels`);
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
  // All 30 rows, so entries with descriptions longer than the right column are checked too.
  if (viewport.width >= 1101) {
    const gaps = await toggleDrift(page, '#resource-grid .resource-card', '.card-meta', 'details.requirements:not([open]) > summary');
    assert(gaps.length && gaps.every(gap => gap >= -1 && gap <= 8), `${label}: details toggles sit under the entry links (${gaps.join(', ')} px)`);
  }
  // From 1101 px the compact layout stacks full-entry links above the details toggle; they keep 24 px targets (WCAG 2.5.8).
  if (viewport.width >= 1101) {
    const entryHeights = await page.$$eval('#resource-grid .resource-entry-link', links => links.map(link => link.getBoundingClientRect().height));
    assert(entryHeights.length && entryHeights.every(height => height >= 24), `${label}: full-entry link targets are at least 24 px tall`);
  }
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
  if (viewport.width >= 1101) {
    const gaps = await toggleDrift(page, '#source-results .source-card', '.source-card-footer', 'details.source-record-details:not([open]) > summary');
    assert(gaps.length && gaps.every(gap => gap >= -1 && gap <= 8), `${label}: repository details toggles sit under the README links (${gaps.join(', ')} px)`);
  }
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
  // Fragment navigation updates the links too; arrow keys on them never navigate (WCAG 3.2.2).
  await page.evaluate(() => { location.hash = 'catalog'; });
  await page.waitForFunction(link => document.querySelector(`[data-language-link="${link}"]`).getAttribute('href').endsWith('#catalog'), {}, other);
  const before = page.url();
  await page.focus(`[data-language-link="${other}"]`);
  for (const key of ['ArrowDown', 'ArrowUp']) await page.keyboard.press(key);
  assert.equal(page.url(), before, `${label}: arrow keys keep the page`);
  assert.equal(await page.evaluate(() => document.activeElement.dataset.languageLink), other);
  await Promise.all([page.waitForNavigation({waitUntil: 'networkidle0'}), page.keyboard.press('Enter')]);
  await loaded(page, '#resource-grid .resource-card', '#error-state');
  await preloadedCatalog(page, label + ' after switching language');
  await completeCatalog(page);
  assert.equal(requests(requested, 'catalog-index.json'), 2, `${label}: one catalog-index.json request on each homepage`);
  assert.equal(requests(requested, 'catalog.json'), 2, `${label}: one catalog.json request on each homepage`);
  const switched = new URL(page.url());
  assert.equal(switched.pathname, other === 'zh' ? '/zh/explore/' : '/explore/');
  assert.equal(switched.searchParams.get('target'), 'game', `${label}: the language switch keeps the filter`);
  assert.equal(switched.hash, '#catalog', `${label}: the language switch keeps the fragment`);
  assert.equal(await page.evaluate(() => document.documentElement.lang), other === 'zh' ? 'zh-CN' : 'en');
  assert.equal(await page.$eval('#curated-view [data-target="game"]', button => button.getAttribute('aria-pressed')), 'true');
  assert.equal(numbers(await text(page, '#results-status'))[0], games);
  await noOverflow(page, label + ' after switching language');
}

// Without scripting, the catalog's inert controls and loading text give way to the static directory links.
async function withoutScript(page, language, viewport) {
  const label = `${language} explorer without JavaScript ${viewport.name}`;
  assert(await page.$eval('[data-open-data]', link => !link.hasAttribute('download') && link.getAttribute('href') === 'https://github.com/reacher-z/Awesome-REA'), `${label}: repository access works without a dialog`);
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
  assert.deepEqual(view.links, language === 'zh' ? [['en', '/', null]] : [['zh', '/zh/', null]], `${label}: language link`);
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
  // Sources, publication details and review notes are on the entry page; each row links there with the source count.
  const footer = await page.$eval(first, card => {
    const link = card.querySelector('.paper-sources > a'), box = link.getBoundingClientRect();
    return {id: card.id, href: link.getAttribute('href'), text: link.textContent, shown: box.width > 0 && box.height > 0,
      inDetails: !!link.closest('details'), lists: card.querySelectorAll('dl, .paper-details ul, .paper-details ol').length};
  });
  assert.equal(footer.href, `${route}${footer.id}/#entry-sources`, `${label}: the sources link opens the entry page's source list`);
  assert(footer.shown && !footer.inDetails, `${label}: the sources link is visible without opening the row`);
  assert.match(footer.text, route.startsWith('/zh/') ? /^\d+ 个来源 · 复核于\s\d{4}-\d{2}-\d{2}\s→$/ : /^\d+ sources? · checked\s\d{4}-\d{2}-\d{2}\s→$/, `${label}: sources link text`);
  assert.equal(footer.lists, 0, `${label}: no source or publication-detail lists in the row`);
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
    await preloadedPaperIndex(page, label);
    // Typing a paper's ID finds that paper alone, through the fetched index.
    await press(page, '#paper-query');
    await page.type('#paper-query', footer.id);
    await page.waitForFunction(() => document.querySelectorAll('.paper-card:not([hidden])').length === 1);
    assert.deepEqual(await page.$$eval('.paper-card:not([hidden])', cards => cards.map(card => card.id)), [footer.id], `${label}: typed search`);
    assert.equal(numbers(await text(page, '#paper-results'))[0], 1);
    assert.equal(new URL(page.url()).searchParams.get('q'), footer.id);
    await press(page, '#paper-clear');
    assert.equal(await page.$$eval('.paper-card[hidden]', cards => cards.length), 0, `${label}: clearing shows every paper`);
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
    const language = new URL(await page.$eval('.site-header a[hreflang]', link => link.href));
    assert.equal(language.searchParams.get('year'), selectedYear);
    await press(page, '#paper-clear');
    await press(page, '#paper-more-filters > summary');
  }
  await noOverflow(page, label + ' compact list');
  if (viewport.name === 'desktop') await midWidthPaperRows(page, label, viewport);
}

// Between 701 and 1100 px each row keeps its links and the Scope & authors toggle on one line, and an opened panel spans the row.
async function midWidthPaperRows(page, label, viewport) {
  await page.setViewport({width: 1024, height: viewport.height});
  const rows = await page.$$eval('.paper-card:not([hidden])', cards => cards.map(card => {
    const links = card.querySelector('.paper-links').getBoundingClientRect();
    const toggle = card.querySelector('.paper-details > summary').getBoundingClientRect();
    const centre = (toggle.top + toggle.bottom) / 2;
    return centre > links.top && centre < links.bottom;
  }));
  assert(rows.length > 0 && rows.every(Boolean), `${label} at 1024px: ${rows.filter(row => !row).length} rows put the links and the Scope & authors toggle on separate lines`);
  const panel = await page.$eval('.paper-card', card => {
    const details = card.querySelector('.paper-details');
    details.open = true;
    const widths = [details.getBoundingClientRect().width, card.getBoundingClientRect().width];
    details.open = false;
    return widths;
  });
  assert(panel[0] >= panel[1] - 8, `${label} at 1024px: an opened panel spans the row (${panel[0]} of ${panel[1]}px)`);
  await noOverflow(page, label + ' at 1024px');
  await page.setViewport({width: viewport.width, height: viewport.height});
}

// Each target section's count line adds up to the cards it heads: tagged, minus filed elsewhere, plus listed here
// without the tag. The line wraps inside the viewport.
async function sectionTargetCounts(page, label) {
  const lines = await page.$$eval('.section-target-count', nodes => nodes.map(line => ({
    target: line.dataset.sectionTarget,
    cards: line.closest('section').querySelectorAll('[data-resource-id]').length,
    stated: ['targetTagged', 'targetElsewhere', 'targetUntaggedHere'].map(key => Number(line.dataset[key])),
    right: line.getBoundingClientRect().right,
  })));
  assert(lines.length > 0, `${label}: target sections state their tag counts`);
  const width = await page.evaluate(() => document.documentElement.clientWidth);
  for (const {target, cards, stated: [tagged, elsewhere, untagged], right} of lines) {
    assert.equal(cards, tagged - elsewhere + untagged, `${label}: ${target} section holds ${cards} cards, but its line states ${tagged} - ${elsewhere} + ${untagged}`);
    assert(right <= width + 1, `${label}: the ${target} count line extends past the viewport (${right}px of ${width}px)`);
  }
}

async function staticPage(page, route, viewport) {
  const label = `${route} ${viewport.name}`;
  assert((await page.$eval('h1', heading => heading.textContent.trim())).length > 0, `${label}: visible heading`);
  await noOverflow(page, label);
  if (route === '/papers/' || route === '/zh/papers/') await paperDirectory(page, route, viewport);
  if (route === '/cases/' || route === '/zh/cases/') await sectionTargetCounts(page, label);
  if (route === '/cases/' || route === '/zh/cases/') {
    const review = await page.$eval('#review-method', section => ({
      title: section.querySelector('h2').textContent,
      dimensions: [...section.querySelectorAll('dt')].map(node => node.textContent),
      visible: section.getClientRects().length > 0 && !section.closest('details'),
    }));
    assert(review.visible && /artifact reviews|产物评审/i.test(review.title) && !review.title.includes('Beta'), `${label}: review method is visible before opening disclosures`);
    assert.equal(review.dimensions.length, 3, `${label}: separate scope, artifacts and evidence`);
  }
}

(async () => {
  execFileSync(process.env.PYTHON || 'python3', ['scripts/build_site.py'], {cwd: root, stdio: 'inherit'});
  const read = file => JSON.parse(fs.readFileSync(path.join(dist, file), 'utf8'));
  const data = {catalog: read('catalog.json'), browser: read('source-browser.json')};
  const category = fs.readdirSync(path.join(dist, 'zh/browse')).filter(name => fs.statSync(path.join(dist, 'zh/browse', name)).isDirectory()).sort()[0];
  const routes = ['/papers/', '/zh/papers/', '/resources/', '/zh/resources/', '/cases/', '/zh/cases/', '/about/', '/zh/about/', '/contribute/', '/zh/contribute/',
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
        await check(`${language} new homepage at ${viewport.width}px`, () => visit(context, origin, language === 'zh' ? '/zh/' : '/', viewport,
          `${language} new homepage ${viewport.name}`, (page, requested) => newHomepage(page, language, viewport, data, requested)));
        await check(`${language} homepage evidence-class filter at ${viewport.width}px`, () => visit(context, origin, language === 'zh' ? '/zh/' : '/', viewport,
          `${language} homepage evidence-class filter ${viewport.name}`, page => homepageClassFilter(page, language, viewport)));
        await check(`${language} scrolled homepage search at ${viewport.width}px`, () => visit(context, origin, language === 'zh' ? '/zh/' : '/', viewport,
          `${language} scrolled homepage search ${viewport.name}`, page => homepageScrolledSearch(page, language, viewport)));
        await check(`${language} new homepage without JavaScript at ${viewport.width}px`, () => visit(context, origin, language === 'zh' ? '/zh/' : '/', viewport,
          `${language} new homepage ${viewport.name} without JavaScript`, (page, requested) => newHomepage(page, language, viewport, data, requested, false), {javascript: false}));
        await check(`${language} resources at ${viewport.width}px`, () => visit(context, origin, language === 'zh' ? '/zh/resources/' : '/resources/', viewport,
          `${language} resources ${viewport.name}`, page => resourceListing(page, language, viewport, data)));
        await check(`${language} old homepage link at ${viewport.width}px`, () => visit(context, origin, (language === 'zh' ? '/zh/' : '/') + '?category=game-analysis', viewport,
          `${language} old homepage link ${viewport.name}`, page => oldHomepageLink(page, language)));
        await check(`${language} explorer at ${viewport.width}px`, () => visit(context, origin, language === 'zh' ? '/zh/explore/' : '/explore/', viewport,
          `${language} homepage ${viewport.name} switched to ${language === 'zh' ? 'en' : 'zh'}`, (page, requested) => homepage(page, language, viewport, data, requested)));
      }
      for (const language of ['en', 'zh']) {
        await check(`${language} explorer without JavaScript at ${viewport.width}px`, () => visit(context, origin, language === 'zh' ? '/zh/explore/' : '/explore/', viewport,
          `${language} homepage ${viewport.name} without JavaScript`, page => withoutScript(page, language, viewport), {javascript: false}));
      }
      for (const route of ['/papers/', '/zh/papers/']) {
        await check(`${route} without JavaScript at ${viewport.width}px`, () => visit(context, origin, route, viewport,
          `${route} ${viewport.name} without JavaScript`, page => paperDirectory(page, route, viewport, false), {javascript: false}));
      }
      for (const route of ['/cases/', '/zh/cases/']) {
        await check(`${route} without JavaScript at ${viewport.width}px`, () => visit(context, origin, route, viewport,
          `${route} ${viewport.name} without JavaScript`, page => staticPage(page, route, viewport), {javascript: false}));
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
