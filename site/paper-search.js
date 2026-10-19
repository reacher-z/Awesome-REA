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

  const readLayout = params => params.get("layout") === "compact" ? "compact" : "cards";

  // Compact list (?layout=compact, cards by default): one row per paper, with the authors and the scope box moved
  // into that paper's details disclosure and back again, so nothing is duplicated and scope stays one click away.
  function initializeLayout(document, browser, cards, afterChange) {
    const control = document.getElementById("paper-layout");
    if (!control) return null;
    const moves = [];
    for (const card of cards) {
      const summary = card.querySelector(".paper-details > summary");
      if (!summary) return null;
      for (const node of card.querySelectorAll(".paper-authors, .paper-scope")) moves.push({node, parent: node.parentNode, next: node.nextSibling, summary});
    }
    function apply(layout) {
      document.documentElement.dataset.paperLayout = layout;
      control.value = layout;
      let anchor = null;
      for (const move of moves) {
        if (layout === "compact") {
          if (!anchor || anchor.summary !== move.summary) anchor = {summary: move.summary, node: move.summary};
          anchor.node.after(move.node);
          anchor.node = move.node;
        } else {
          move.parent.insertBefore(move.node, move.next);
        }
      }
    }
    control.addEventListener("change", () => {
      const url = new URL(browser.location.href);
      if (control.value === "compact") url.searchParams.set("layout", "compact"); else url.searchParams.delete("layout");
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

  if (typeof module === "object" && module.exports) module.exports = {readRecords, allowedValues, readState, matches, stateURL, initialize, initializeLayout, readLayout};
  if (typeof document !== "undefined") initialize(document, window);
}());
