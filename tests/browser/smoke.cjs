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

async function open(browser, origin, route, viewport) {
  const page = await browser.newPage();
  const problems = [];
  page.setDefaultTimeout(20000);
  await page.setViewport({width: viewport.width, height: viewport.height});
  await page.setRequestInterception(true);
  page.on('request', request => {
    const url = request.url();
    if (url.startsWith(origin + '/') || url.startsWith('data:')) request.continue();
    else { problems.push(`blocked non-local request ${url}`); request.abort('blockedbyclient'); }
  });
  page.on('console', message => { if (message.type() === 'error') problems.push(`console error: ${message.text()}`); });
  page.on('pageerror', error => problems.push(`uncaught exception: ${error.message}`));
  page.on('requestfailed', request => {
    if (request.url().startsWith(origin + '/')) problems.push(`failed request ${request.url()}: ${request.failure()?.errorText}`);
  });
  page.on('response', response => {
    if (response.url().startsWith(origin + '/') && response.status() >= 400) problems.push(`HTTP ${response.status()} ${response.url()}`);
  });
  await page.exposeFunction('reportPolicyViolation', text => problems.push(`CSP violation: ${text}`));
  await page.evaluateOnNewDocument(() => document.addEventListener('securitypolicyviolation',
    event => window.reportPolicyViolation(`${event.violatedDirective} blocked ${event.blockedURI || 'inline content'}`)));
  const response = await page.goto(origin + route, {waitUntil: 'networkidle0'});
  assert.equal(response.status(), 200, `${route} returned HTTP ${response.status()}`);
  return {page, problems};
}
async function noOverflow(page, label) {
  const {scroll, inner} = await page.evaluate(() => ({scroll: document.scrollingElement.scrollWidth, inner: innerWidth}));
  assert(scroll <= inner, `${label}: the page scrolls horizontally (${scroll}px wide in a ${inner}px viewport)`);
}
const shot = (page, name) => page.screenshot({path: path.join(screenshots, name.replace(/[^a-z0-9]+/gi, '-').replace(/^-|-$/g, '') + '.png')});
// Report a failed assertion together with every browser problem the page logged, then close it.
async function visit(browser, origin, route, viewport, name, run) {
  const {page, problems} = await open(browser, origin, route, viewport);
  let failure;
  try { await run(page); } catch (error) { failure = error; }
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

async function homepage(page, language, viewport, data) {
  const label = `${language} homepage ${viewport.name}`;
  const total = data.catalog.resources.length;
  await loaded(page, '#resource-grid .resource-card', '#error-state');
  assert.equal(await hidden(page, '#error-state'), true, `${label}: the curated catalog loads`);
  assert.equal(await count(page, '#resource-grid .resource-card'), Math.min(15, total), `${label}: initial curated cards`);
  assert(numbers(await text(page, '#results-status')).includes(total), `${label}: status names all ${total} curated resources`);
  assert(await page.$$eval('#resource-grid .card-title-link', links => links.every(link => link.textContent.trim() && link.href.startsWith('http'))));
  await noOverflow(page, label);

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
  await press(page, '#resource-grid .resource-card details.requirements summary');
  const expanded = await page.$eval('#resource-grid .resource-card details.requirements', details => ({open: details.open,
    items: details.querySelectorAll('li').length, height: details.querySelector('ul').getBoundingClientRect().height}));
  assert(expanded.open && expanded.items > 0 && expanded.height > 0, `${label}: requirements expand visibly`);
  await noOverflow(page, label + ' with requirements open');
  await shot(page, `${language} homepage ${viewport.name} curated`);

  // The repository view loads its own payload, 24 cards at a time.
  const repositories = data.browser.resources.length;
  await press(page, '#mode-sources');
  await loaded(page, '#source-results .source-card', '#source-error');
  assert.equal(await hidden(page, '#source-error'), true, `${label}: the repository index loads`);
  assert.equal(await count(page, '#source-results .source-card'), Math.min(24, repositories), `${label}: initial repository cards`);
  assert(numbers(await text(page, '#source-status')).includes(repositories), `${label}: status names all ${repositories} repositories`);
  assert.equal(await text(page, '#source-more-count'), '+' + Math.min(24, Math.max(0, repositories - 24)));
  await press(page, '#source-more');
  assert.equal(await count(page, '#source-results .source-card'), Math.min(48, repositories), `${label}: repository Show More`);
  await press(page, '#source-results .source-card details.source-record-details summary');
  await noOverflow(page, label + ' repositories');
  await shot(page, `${language} homepage ${viewport.name} repositories`);

  // A target filter survives the language switch, which loads the other homepage.
  await press(page, '#mode-curated');
  const games = data.catalog.resources.filter(record => (record.targets || []).includes('game')).length;
  await press(page, '#curated-view [data-target="game"]');
  assert(numbers(await text(page, '#results-status'))[0] === games, `${label}: Game filter shows ${games} resources`);
  const other = language === 'zh' ? 'en' : 'zh';
  await Promise.all([page.waitForNavigation({waitUntil: 'networkidle0'}), page.select('#language-select', other)]);
  await loaded(page, '#resource-grid .resource-card', '#error-state');
  const switched = new URL(page.url());
  assert.equal(switched.pathname, other === 'zh' ? '/zh/' : '/');
  assert.equal(switched.searchParams.get('target'), 'game', `${label}: the language switch keeps the filter`);
  assert.equal(await page.evaluate(() => document.documentElement.lang), other === 'zh' ? 'zh-CN' : 'en');
  assert.equal(await page.$eval('#curated-view [data-target="game"]', button => button.getAttribute('aria-pressed')), 'true');
  assert.equal(numbers(await text(page, '#results-status'))[0], games);
  await noOverflow(page, label + ' after switching language');
}

async function staticPage(page, route, viewport) {
  const label = `${route} ${viewport.name}`;
  assert((await page.$eval('h1', heading => heading.textContent.trim())).length > 0, `${label}: visible heading`);
  await noOverflow(page, label);
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
    for (const viewport of VIEWPORTS) {
      for (const language of ['en', 'zh']) {
        await check(`${language} homepage at ${viewport.width}px`, () => visit(browser, origin, language === 'zh' ? '/zh/' : '/', viewport,
          `${language} homepage ${viewport.name} switched to ${language === 'zh' ? 'en' : 'zh'}`, page => homepage(page, language, viewport, data)));
      }
      for (const route of routes) {
        await check(`${route} at ${viewport.width}px`, () => visit(browser, origin, route, viewport, `${route} ${viewport.name}`, page => staticPage(page, route, viewport)));
      }
    }
  } finally {
    await browser.close(); site.close();
  }
  console.log(`Screenshots for review: ${path.relative(root, screenshots)}/`);
  if (failures.length) { console.error(`${failures.length} browser smoke check(s) failed.`); process.exitCode = 1; }
  else console.log('Browser smoke checks passed.');
})().catch(error => { console.error(error); process.exitCode = 1; });
