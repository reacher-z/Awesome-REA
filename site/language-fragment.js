/* Keep the current card or section when a static page switches language.
   Both language versions of a page share every card and section ID, so a fragment that names an element here
   names the same element on the counterpart page. Without JavaScript the link still opens that page's top. */
(function () {
  "use strict";

  const FRAGMENT = /^#[A-Za-z0-9][A-Za-z0-9_-]{0,159}$/;

  // Returns the counterpart href with only a recognized fragment, or null for a link this script must not change.
  function languageHref(href, hash, document, base) {
    let next;
    try { next = new URL(href, base); } catch (_) { return null; }
    if (next.origin !== new URL(base).origin) return null;
    next.hash = FRAGMENT.test(hash) && document.getElementById(hash.slice(1)) ? hash : "";
    return next.pathname + next.search + next.hash;
  }

  function initialize(document, browser) {
    const links = [...document.querySelectorAll(".site-header a[hreflang]")];
    if (!links.length) return false;
    function update() {
      for (const link of links) {
        const next = languageHref(link.getAttribute("href"), browser.location.hash, document, browser.location.href);
        if (next !== null) link.setAttribute("href", next);
      }
    }
    browser.addEventListener("hashchange", update);
    // Document listeners run after the link's own, so this also normalizes the paper directory's query-preserving link.
    for (const type of ["click", "auxclick"]) {
      document.addEventListener(type, event => { if (links.some(link => link.contains(event.target))) update(); });
    }
    update();
    return true;
  }

  if (typeof module === "object" && module.exports) module.exports = {languageHref, initialize};
  if (typeof document !== "undefined") initialize(document, window);
}());
