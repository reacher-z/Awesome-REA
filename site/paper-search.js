/* Progressive paper discovery: filter existing HTML, never replace its evidence. */
(function () {
  "use strict";

  const STATUSES = new Set(["conference-paper", "conference-accepted", "journal-article", "preprint"]);
  const TARGETS = new Set(["binary", "website", "app", "game", "firmware", "protocol"]);
  const KEYS = ["q", "target", "status", "year"];
  const cleanQuery = value => String(value || "").replace(/[\u0000-\u001f\u007f]/g, " ").slice(0, 240).trim();
  const normalized = value => String(value).normalize("NFKC").toLowerCase();

  function readRecords(value) {
    if (!value || value.schema_version !== 1 || !Array.isArray(value.papers)) throw new Error("Invalid paper search data");
    const ids = new Set();
    return value.papers.map(paper => {
      if (!paper || typeof paper.id !== "string" || !/^[a-z0-9][a-z0-9-]*$/.test(paper.id) || ids.has(paper.id)
          || ![paper.title, paper.title_zh, paper.description_en, paper.description_zh].every(text => typeof text === "string" && text.trim())
          || !Array.isArray(paper.authors) || !paper.authors.length || !paper.authors.every(name => typeof name === "string")
          || ![paper.doi, paper.arxiv_id].every(identifier => identifier === null || typeof identifier === "string")
          || !Number.isInteger(paper.year) || paper.year < 1000 || paper.year > 9999 || !STATUSES.has(paper.publication_status)
          || !Array.isArray(paper.targets) || !paper.targets.length || !paper.targets.every(target => TARGETS.has(target))) {
        throw new Error("Invalid paper search record");
      }
      ids.add(paper.id);
      return {...paper, search: normalized([paper.id, paper.title, paper.title_zh, paper.description_en, paper.description_zh, ...paper.authors, paper.doi || "", paper.arxiv_id || ""].join(" "))};
    });
  }

  function allowedValues(records) {
    return {
      target: new Set(records.flatMap(paper => paper.targets)),
      status: new Set(records.map(paper => paper.publication_status)),
      year: new Set(records.map(paper => String(paper.year)))
    };
  }

  function readState(params, allowed) {
    const state = {q: cleanQuery(params.get("q"))};
    for (const key of ["target", "status", "year"]) {
      const value = params.get(key);
      state[key] = allowed[key].has(value) ? value : "all";
    }
    return state;
  }

  function matches(paper, state) {
    return (state.target === "all" || paper.targets.includes(state.target))
      && (state.status === "all" || paper.publication_status === state.status)
      && (state.year === "all" || String(paper.year) === state.year)
      && normalized(state.q).split(/\s+/).filter(Boolean).every(term => paper.search.includes(term));
  }

  function stateURL(href, state) {
    const url = new URL(href);
    for (const key of KEYS) {
      url.searchParams.delete(key);
      if (state[key] && (key === "q" || state[key] !== "all")) url.searchParams.set(key, state[key]);
    }
    return url;
  }

  const readLayout = params => params.get("layout") === "cards" ? "cards" : "compact";

  // The static index is already compact. Cards bring only the scope panel out;
  // full authors, original titles, citations and sources remain in native details.
  function initializeLayout(document, browser, cards, afterChange) {
    const control = document.getElementById("paper-layout");
    if (!control) return null;
    const moves = [];
    for (const card of cards) {
      const summary = card.querySelector(".paper-details > summary");
      const scope = card.querySelector(".paper-scope");
      const links = card.querySelector(".paper-links");
      if (!summary || !scope || !links) return null;
      moves.push({card, summary, scope, links});
    }
    function apply(layout) {
      document.documentElement.dataset.paperLayout = layout;
      control.value = layout;
      for (const {card, summary, scope, links} of moves) {
        if (layout === "cards") card.insertBefore(scope, links);
        else if (summary.nextSibling !== scope) summary.after(scope);
      }
    }
    control.addEventListener("change", () => {
      const url = new URL(browser.location.href);
      if (control.value === "cards") url.searchParams.set("layout", "cards"); else url.searchParams.delete("layout");
      if (url.href !== browser.location.href) browser.history.replaceState(null, "", url);
      apply(readLayout(url.searchParams));
      afterChange();
    });
    apply(readLayout(new URL(browser.location.href).searchParams));
    return apply;
  }

  function initialize(document, browser) {
    const form = document.getElementById("paper-search");
    const data = document.getElementById("paper-search-data");
    if (!form || !data) return false;
    const controls = Object.fromEntries(KEYS.map(key => [key, document.getElementById("paper-" + (key === "q" ? "query" : key))]));
    const count = document.getElementById("paper-results");
    const empty = document.getElementById("paper-empty");
    const clear = document.getElementById("paper-clear");
    const moreFilters = document.getElementById("paper-more-filters");
    const emptyReset = document.getElementById("paper-empty-reset");
    if (!count || !empty || !clear || !emptyReset || Object.values(controls).some(control => !control)) return false;
    let records;
    try { records = readRecords(JSON.parse(data.textContent)); } catch (_) { return false; }
    const cards = [...document.querySelectorAll("[data-paper-id]")];
    const cardMap = new Map(cards.map(card => [card.dataset.paperId, card]));
    if (cards.length !== records.length || cardMap.size !== records.length || records.some(paper => !cardMap.has(paper.id))) return false;
    const sections = [...document.querySelectorAll("[data-paper-section]")];
    const topics = [...document.querySelectorAll("[data-paper-topic]")];
    const languageLink = document.querySelector(".papers-language");
    const languagePath = languageLink ? new URL(languageLink.href, browser.location.href).pathname : null;
    const zh = document.documentElement.lang === "zh-CN";
    const allowed = allowedValues(records);
    let state = readState(new URL(browser.location.href).searchParams, allowed);
    let composing = false;

    function showState() {
      for (const key of KEYS) controls[key].value = state[key];
      // Active URL filters must remain visible, even before a visitor opens the panel.
      if (moreFilters && (state.status !== "all" || state.year !== "all" || readLayout(new URL(browser.location.href).searchParams) === "cards")) moreFilters.open = true;
    }

    function updateLanguageLink() {
      if (!languageLink) return;
      const next = stateURL(browser.location.href, state);
      next.pathname = languagePath;
      languageLink.href = next.href;
    }

    function render() {
      let visible = 0;
      for (const paper of records) {
        const found = matches(paper, state);
        cardMap.get(paper.id).hidden = !found;
        if (found) visible++;
      }
      const sectionCounts = new Map();
      for (const section of sections) {
        const amount = [...section.querySelectorAll("[data-paper-id]")].filter(card => !card.hidden).length;
        section.hidden = amount === 0;
        sectionCounts.set(section.dataset.paperSection, amount);
        const label = section.querySelector("[data-paper-section-count]");
        if (label) label.textContent = zh ? `${amount} 篇论文` : `${amount} ${amount === 1 ? "paper" : "papers"}`;
      }
      for (const topic of topics) {
        const amount = sectionCounts.get(topic.dataset.paperTopic) || 0;
        topic.hidden = amount === 0;
        const label = topic.querySelector("span");
        if (label) label.textContent = String(amount);
      }
      count.textContent = zh ? `显示 ${visible} / ${records.length} 篇论文` : `Showing ${visible} of ${records.length} papers`;
      empty.hidden = visible !== 0;
      clear.disabled = !state.q && state.target === "all" && state.status === "all" && state.year === "all";
      updateLanguageLink();
    }

    function update(push = false) {
      if (composing) return;
      const params = new URLSearchParams();
      for (const key of KEYS) params.set(key, controls[key].value);
      state = readState(params, allowed);
      // Keep in-progress typing intact; normalize the shared URL, not the cursor.
      for (const key of ["target", "status", "year"]) controls[key].value = state[key];
      const next = stateURL(browser.location.href, state);
      if (next.href !== browser.location.href) {
        browser.history[push ? "pushState" : "replaceState"](null, "", next);
      }
      render();
    }

    function reset() {
      composing = false;
      controls.q.value = "";
      for (const key of ["target", "status", "year"]) controls[key].value = "all";
      update(true);
      controls.q.focus();
    }

    form.addEventListener("submit", event => { event.preventDefault(); update(); });
    controls.q.addEventListener("compositionstart", () => { composing = true; });
    controls.q.addEventListener("compositionend", () => { composing = false; update(); });
    controls.q.addEventListener("input", event => { if (!event.isComposing) update(); });
    for (const key of ["target", "status", "year"]) controls[key].addEventListener("change", () => update(true));
    clear.addEventListener("click", reset);
    emptyReset.addEventListener("click", reset);
    if (languageLink) languageLink.addEventListener("click", updateLanguageLink);
    const applyLayout = initializeLayout(document, browser, cards, updateLanguageLink);
    browser.addEventListener("popstate", () => {
      composing = false;
      state = readState(new URL(browser.location.href).searchParams, allowed);
      showState(); render();
      if (applyLayout) applyLayout(readLayout(new URL(browser.location.href).searchParams));
    });
    showState();
    const canonicalState = stateURL(browser.location.href, state);
    if (canonicalState.href !== browser.location.href) browser.history.replaceState(null, "", canonicalState);
    render();
    form.hidden = false;
    return true;
  }

  // Browser-local shortlist shared with the homepage (app.js): only "type:id" keys, kept in this browser and never sent.
  const SHORTLIST_KEY = "awesomerea-shortlist";
  const SHORTLIST_ITEM = /^(curated|repository|paper):[a-z0-9]+(?:-[a-z0-9]+)*$/;
  function shortlistStorage(browser) {
    try { const storage = browser.localStorage; storage.setItem("awesomerea-storage-check", "1"); storage.removeItem("awesomerea-storage-check"); return storage; } catch (_) { return null; }
  }
  function readShortlist(storage) {
    try { const value = JSON.parse(storage.getItem(SHORTLIST_KEY) || "[]"); return Array.isArray(value) ? [...new Set(value.filter(key => typeof key === "string" && SHORTLIST_ITEM.test(key)))] : []; }
    catch (_) { return []; }
  }

  // Adds a Save toggle to each paper's links and, once something is saved, a link to the homepage shortlist.
  // Without storage nothing changes.
  function initializeShortlist(document, browser) {
    const storage = shortlistStorage(browser);
    const actions = document.querySelector(".papers-actions");
    const cards = [...document.querySelectorAll("[data-paper-id]")];
    if (!storage || !actions || !cards.length) return false;
    const zh = document.documentElement.lang === "zh-CN";
    const element = (tag, className, text) => { const node = document.createElement(tag); if (className) node.className = className; if (text !== undefined) node.textContent = text; return node; };
    const count = element("span", "mono");
    const link = element("a", "button button-outline papers-shortlist");
    link.href = (zh ? "/zh/" : "/") + "#shortlist"; link.append(element("span", "", zh ? "收藏清单" : "Shortlist"), count);
    const status = element("p", "sr-only"); status.setAttribute("role", "status"); status.setAttribute("aria-live", "polite");
    const buttons = [];
    function sync() {
      const keys = readShortlist(storage); count.textContent = String(keys.length); link.hidden = !keys.length;
      for (const button of buttons) {
        const saved = keys.includes(button.dataset.shortlistKey);
        button.setAttribute("aria-pressed", String(saved)); button.firstChild.textContent = saved ? (zh ? "已收藏" : "Saved") : (zh ? "收藏" : "Save");
      }
      return keys;
    }
    for (const card of cards) {
      const key = "paper:" + card.dataset.paperId; const links = card.querySelector(".paper-links");
      if (!SHORTLIST_ITEM.test(key) || !links) continue;
      const title = (card.querySelector("h3")?.textContent || card.dataset.paperId).trim();
      const button = element("button", "paper-link save-toggle"); button.type = "button"; button.dataset.shortlistKey = key;
      button.append(element("span"), element("span", "sr-only", " " + title));
      button.addEventListener("click", () => {
        const keys = readShortlist(storage); const saved = keys.includes(key); const next = saved ? keys.filter(item => item !== key) : [...keys, key];
        try { if (next.length) storage.setItem(SHORTLIST_KEY, JSON.stringify(next)); else storage.removeItem(SHORTLIST_KEY); }
        catch (_) { status.textContent = zh ? "此浏览器无法保存收藏清单。" : "This browser couldn’t save the shortlist."; return; }
        sync();
        status.textContent = zh ? `已${saved ? "移除" : "收藏"} ${title}。收藏清单共 ${next.length} 项。` : `${saved ? "Removed" : "Saved"} ${title}. ${next.length} ${next.length === 1 ? "entry" : "entries"} in your shortlist.`;
      });
      links.append(button); buttons.push(button);
    }
    actions.append(link); actions.after(status);
    browser.addEventListener("storage", event => { if (event.key === SHORTLIST_KEY || event.key === null) sync(); });
    sync();
    return true;
  }

  if (typeof module === "object" && module.exports) module.exports = {readRecords, allowedValues, readState, matches, stateURL, initialize, initializeLayout, readLayout, initializeShortlist, readShortlist};
  if (typeof document !== "undefined") initialize(document, window);
  if (typeof document !== "undefined") initializeShortlist(document, window);
}());
