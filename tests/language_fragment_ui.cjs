/* Static language links keep a recognized card or section fragment and never leave the site. */
const assert = require('node:assert/strict');
const path = require('node:path');
const {languageHref, initialize} = require(path.join(__dirname, '../site/language-fragment.js'));

const ids = new Set(['scan-8859474', 'ghidra', 'paper-pix2code', 'cases-game', 'heading-website', 'entry-requirements', 'abstract']);
const page = {getElementById: id => (ids.has(id) ? {id} : null)};
const href = (link, current) => { const url = new URL(current); return languageHref(link, url.hash, page, url.href); };

// A card or section deep link survives EN -> ZH -> EN with its stable ID.
for (const [english, chinese] of [['/browse/android/#scan-8859474', '/zh/browse/android/#scan-8859474'],
  ['/resources/#ghidra', '/zh/resources/#ghidra'], ['/papers/#paper-pix2code', '/zh/papers/#paper-pix2code'],
  ['/cases/#cases-game', '/zh/cases/#cases-game'], ['/resources/#heading-website', '/zh/resources/#heading-website'],
  ['/resources/ghidra/#entry-requirements', '/zh/resources/ghidra/#entry-requirements'], ['/survey/#abstract', '/zh/survey/#abstract']]) {
  const toChinese = href(chinese.split('#')[0], 'https://awesomerea.org' + english);
  assert.equal(toChinese, chinese);
  assert.equal(href(english.split('#')[0], 'https://awesomerea.org' + toChinese), english);
}
// The paper directory's own query (and a stale fragment it copied) is kept apart from the checked fragment.
assert.equal(href('https://awesomerea.org/zh/papers/?q=agent&layout=cards#stale', 'https://awesomerea.org/papers/?q=agent#paper-pix2code'),
  '/zh/papers/?q=agent&layout=cards#paper-pix2code');
// Unknown or malformed fragments open the counterpart page without one.
for (const hash of ['', '#', '#missing', '#-ghidra', '#ghidra extra', '#%3Cscript%3E', '#javascript:alert(1)', '#../ghidra',
  '#ghidra/', '#' + 'a'.repeat(161), '#%67hidra']) {
  assert.equal(languageHref('/zh/resources/#old', hash, page, 'https://awesomerea.org/resources/' + hash), '/zh/resources/', hash);
}
// Links to another origin, or that are not URLs, are never rewritten.
for (const link of ['https://example.org/zh/', '//example.org/zh/', 'javascript:alert(1)', 'http://awesomerea.org/zh/', 'http://[']) {
  assert.equal(languageHref(link, '#ghidra', page, 'https://awesomerea.org/resources/#ghidra'), null, link);
}

// initialize() updates the header links on load, on hashchange and when one is activated.
function browser(url) {
  const listeners = {};
  return {location: new URL(url), listeners, addEventListener(type, callback) { listeners[type] = callback; }};
}
function documentWith(links) {
  const listeners = {};
  return {...page, listeners, querySelectorAll: selector => (selector === '.site-header a[hreflang]' ? links : []),
    addEventListener(type, callback) { (listeners[type] ||= []).push(callback); }};
}
function link(initial) {
  const attrs = {href: initial}; const label = {};
  return {label, getAttribute: key => attrs[key], setAttribute: (key, value) => { attrs[key] = value; },
    contains: node => node === label || node === attrs};
}
const header = link('/zh/browse/android/'); const other = link('/elsewhere/');
const view = browser('https://awesomerea.org/browse/android/#scan-8859474');
const docs = documentWith([header]);
assert.equal(initialize(docs, view), true);
assert.equal(header.getAttribute('href'), '/zh/browse/android/#scan-8859474');
view.location.hash = '#missing'; view.listeners.hashchange();
assert.equal(header.getAttribute('href'), '/zh/browse/android/');
view.location.hash = '#heading-website'; view.listeners.hashchange();
assert.equal(header.getAttribute('href'), '/zh/browse/android/#heading-website');
// Another script (the paper directory) may rewrite the href; a click on the link's label restores the checked fragment.
for (const type of ['click', 'auxclick']) {
  header.setAttribute('href', 'https://awesomerea.org/zh/browse/android/#%3Cx%3E');
  docs.listeners[type].forEach(callback => callback({target: header.label}));
  assert.equal(header.getAttribute('href'), '/zh/browse/android/#heading-website', type);
}
// Clicks elsewhere leave the link alone.
header.setAttribute('href', '/zh/browse/android/#stale');
docs.listeners.click.forEach(callback => callback({target: other.label}));
assert.equal(header.getAttribute('href'), '/zh/browse/android/#stale');
// Pages without a header language link do nothing.
assert.equal(initialize(documentWith([]), browser('https://awesomerea.org/404.html')), false);

console.log('Static language fragment checks passed');
