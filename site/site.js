/* Awesome REA: theme, header state, ⌘K palette, home drawer, /resources/ facets, /cases/ filter, copy buttons.
   Vanilla, no dependencies. The search index loads lazily (first focus, first keystroke or idle). */
(() => {
  'use strict';
  const d = document.documentElement;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const zh = d.lang.startsWith('zh');
  const P = zh ? '/zh' : '';
  const nf = new Intl.NumberFormat(zh ? 'zh-CN' : 'en-US');
  const fmt = (n) => nf.format(n);
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  // Writes markup only when it differs from what this call wrote last, so a re-render with the same result keeps the
  // nodes (and any focus or pending click on them) in place.
  const put = (el, html) => {
    if (el.__html === html && el.__first === el.firstChild) return;
    el.innerHTML = html; el.__html = html; el.__first = el.firstChild;
  };
  const ico = (n) => `<svg class="i" aria-hidden="true" focusable="false"><use href="#i-${n}"/></svg>`;
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { if (v == null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) { /* storage blocked */ } },
  };
  const T = zh ? {
    featured: '精选', theme: '颜色主题', system: '跟随系统', light: '浅色', dark: '深色', reviewed: '已复核', targets: '目标', copied: '已复制',
    showing: (a, n) => `显示 <strong>${fmt(a)}</strong> / <strong>${fmt(n)}</strong>`, range: (a, b, n) => `显示第 <strong>${fmt(a)}–${fmt(b)}</strong> 项，共 <strong>${fmt(n)}</strong> 项`,
    results: (n) => `${fmt(n)} 条结果`, more: (n) => `再显示 ${fmt(n)} 项`, all: (n) => `查看全部 ${fmt(n)} 项资源`, seeAll: (n) => `在资源页查看全部 ${fmt(n)} 条结果`,
    none: (q) => `没有与“${esc(q)}”匹配的记录。`, near: '相近名称：', noneFilters: '没有符合这些筛选条件的记录。', clearSearch: '清除搜索', sources: (q) => `在仓库目录中搜索“${esc(q)}”`, discoveries: '查看未审核的发现', keyMove: '移动', keyOpen: '打开', keyClear: '清除', suggest: '推荐收录这个资源', clear: '清除筛选', loading: '正在载入索引…', failed: '索引载入失败，请检查网络后重试。',
    recent: '最近搜索', popular: '常用入口', groups: { tool: '工具', 'case-study': '案例', integration: '集成', other: '学习与参考', paper: '论文' }, papers: '论文',
    remove: (l) => `移除筛选：${l}`, page: (a, b) => `第 ${a}/${b} 页`, shelf: (a, n) => `${fmt(a)} / ${fmt(n)} 个案例`,
    classLabel: '证据档位', classDetail: ['完整软件复现', '部分范围或分析条目', '有代码和文档，缺演示或下载', '仅笔记'],
    unknownTitle: '复核时来源不可达或不可读', previewAlt: '项目公开文档中的演示截图', previewVideoAlt: '项目公开文档中演示视频的封面', previewFull: (name) => `完整演示截图：${name}`, demoNote: '有 demo · 暂无截图',
  } : {
    featured: 'Featured', theme: 'Colour theme', system: 'system', light: 'light', dark: 'dark', reviewed: 'Reviewed', targets: 'Targets', copied: 'Copied',
    showing: (a, n) => `Showing <strong>${fmt(a)}</strong> of <strong>${fmt(n)}</strong>`, range: (a, b, n) => `Showing <strong>${fmt(a)}–${fmt(b)}</strong> of <strong>${fmt(n)}</strong>`,
    results: (n) => `${fmt(n)} result${n === 1 ? '' : 's'}`, more: (n) => `Show ${fmt(n)} more`, all: (n) => `Show all ${fmt(n)} resources`, seeAll: (n) => `See all ${fmt(n)} results on the resources page`,
    none: (q) => `Nothing in the catalogue matches “${esc(q)}”.`, near: 'Close names:', noneFilters: 'Nothing in the catalogue matches these filters.', clearSearch: 'Clear search', sources: (q) => `Search the repository directory for “${esc(q)}”`, discoveries: 'See the unreviewed discoveries', keyMove: 'move', keyOpen: 'open', keyClear: 'clear', suggest: 'Suggest this resource', clear: 'Clear filters', loading: 'Loading the index…', failed: 'The search index did not load. Check your connection and try again.',
    recent: 'Recent searches', popular: 'Popular', groups: { tool: 'Tools', 'case-study': 'Case studies', integration: 'Integrations', other: 'Learning and reference', paper: 'Papers' }, papers: 'Papers',
    remove: (l) => `Remove filter: ${l}`, page: (a, b) => `Page ${a} of ${b}`, shelf: (a, n) => `${fmt(a)} of ${fmt(n)} cases`,
    classLabel: 'Evidence class', classDetail: ['full software reconstruction', 'partial scope or analysis entry', 'code & docs, no demo or download', 'notes only'],
    unknownTitle: 'Source unavailable or unreadable at review time', previewAlt: "Demo screenshot from the project's public documentation", previewVideoAlt: "Demo video thumbnail from the project's public documentation", previewFull: (name) => `Full-size demo screenshot: ${name}`, demoNote: 'Demo available · no screenshot',
  };
  const ISSUE = 'https://github.com/reacher-z/Awesome-REA/issues/new?template=resource.yml';
  const isMac = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent);
  if (!isMac) {
    $$('[data-kbd]').forEach((k) => { k.textContent = 'Ctrl K'; });
    $$('[data-kbd-mod]').forEach((k) => { k.textContent = 'Ctrl'; });
  }

  /* ---------- theme: system → light → dark ---------- */
  const THEMES = ['system', 'light', 'dark'];
  let theme = store.get('rea-theme');
  if (!THEMES.includes(theme)) theme = 'system';
  const paintTheme = () => {
    if (theme === 'system') delete d.dataset.theme; else d.dataset.theme = theme;
    $$('[data-theme-toggle]').forEach((b) => { b.setAttribute('aria-label', `${T.theme}: ${T[theme]}`); b.title = `${T.theme}: ${T[theme]}`; });
  };
  paintTheme();
  document.addEventListener('click', (e) => {
    if (!e.target.closest('[data-theme-toggle]')) return;
    theme = THEMES[(THEMES.indexOf(theme) + 1) % THEMES.length];
    store.set('rea-theme', theme === 'system' ? null : theme);
    paintTheme();
  });

  /* ---------- header state: border, header search on home, mobile sticky bar ---------- */
  // The hero field counts as gone once it is under the sticky bar, not only once it leaves the window.
  // Wide screens stick the header; phones scroll it away and fix the shorter .mbar instead.
  const homeSearch = $('[data-home-search]');
  const stickyHeader = $('.site-header');
  const mobileBar = $('.mbar');
  const coveredTop = () => {
    const bar = mobileBar && getComputedStyle(mobileBar).position === 'fixed' ? mobileBar : stickyHeader;
    return bar ? bar.offsetHeight : 0;
  };
  const watch = homeSearch || stickyHeader;
  if (watch && 'IntersectionObserver' in window) {
    new IntersectionObserver(([en]) => d.classList.toggle('is-scrolled', !en.isIntersecting && en.boundingClientRect.top < 0),
      { rootMargin: `-${homeSearch ? coveredTop() : 8}px 0px 0px 0px` }).observe(watch);
  }

  /* ---------- relative "updated" times ---------- */
  const relTime = (iso) => {
    if (!Intl.RelativeTimeFormat) return '';
    const mins = (Date.now() - Date.parse(iso)) / 6e4;
    if (!(mins >= 0)) return '';
    const [v, u] = mins < 60 ? [Math.max(1, Math.round(mins)), 'minute'] : mins < 2880 ? [Math.round(mins / 60), 'hour'] : [Math.round(mins / 1440), 'day'];
    return new Intl.RelativeTimeFormat(zh ? 'zh-CN' : 'en', { numeric: 'auto' }).format(-v, u);
  };
  $$('time[data-rel]').forEach((t) => {
    const text = relTime(t.dateTime);
    if (text) { t.title = t.textContent; t.textContent = text; }
  });

  /* ---------- footer: last scan, from the status file the build publishes (HTML stays the same between scans) ---------- */
  const scanCell = $('[data-last-scan]');
  if (scanCell) {
    const fill = () => fetch('/discoveries/status.json').then((r) => (r.ok ? r.json() : null)).then((s) => {
      const at = s && s.last_successful_ingest_at;
      if (at) {
        const time = document.createElement('time');
        time.dateTime = at; time.textContent = relTime(at) || at.slice(0, 10); time.title = at;
        scanCell.replaceChildren(time);
      }
    }).catch(() => {});
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver((es) => { if (es.some((x) => x.isIntersecting)) { io.disconnect(); fill(); } }, { rootMargin: '400px' });
      io.observe(scanCell);
    } else fill();
  }

  /* ---------- toast + copy ---------- */
  let toastEl;
  const toast = (msg) => {
    if (!toastEl) { toastEl = document.createElement('div'); toastEl.className = 'toast'; toastEl.setAttribute('role', 'status'); document.body.append(toastEl); }
    toastEl.textContent = msg;
    toastEl.classList.add('is-on');
    clearTimeout(toast.t);
    toast.t = setTimeout(() => toastEl.classList.remove('is-on'), 1800);
  };
  // A link with data-copy-url copies the text it points to (a page's index.md twin); without the Clipboard API it stays a link.
  document.addEventListener('click', async (e) => {
    const a = e.target.closest('a[data-copy-url]');
    if (!a || !navigator.clipboard || e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
    e.preventDefault();
    const text = fetch(a.href).then((r) => (r.ok ? r.text() : Promise.reject(new Error(String(r.status)))));
    try {
      if (window.ClipboardItem && navigator.clipboard.write) {
        await navigator.clipboard.write([new ClipboardItem({ 'text/plain': text.then((t) => new Blob([t], { type: 'text/plain' })) })]);
      } else await navigator.clipboard.writeText(await text);
      a.classList.add('is-done');
      toast(a.dataset.copyLabel || T.copied);
      setTimeout(() => a.classList.remove('is-done'), 1800);
    } catch (err) { location.href = a.href; }
  });
  document.addEventListener('click', async (e) => {
    const b = e.target.closest('[data-copy]');
    if (!b) return;
    const src = $(b.dataset.copy);
    const text = (src ? (src.content || src).textContent : '').trim();
    try { await navigator.clipboard.writeText(text); } catch (err) {
      const ta = Object.assign(document.createElement('textarea'), { value: text });
      ta.style.cssText = 'position:fixed;opacity:0'; document.body.append(ta); ta.select();
      try { document.execCommand('copy'); } catch (x) { /* ignore */ } ta.remove();
    }
    b.classList.add('is-done');
    toast(b.dataset.copyLabel || T.copied);
    setTimeout(() => b.classList.remove('is-done'), 1800);
  });

  /* ---------- search index + engine ---------- */
  // Two files: search-index.json answers a search by name, alias, kind and target; search-text.json follows with the
  // descriptions, owners, evidence links and previews, and every open view renders again when it lands.
  let IDX = null;
  let idxP = null;
  let txtP = null;
  const onText = [];
  const CJK = /[㐀-鿿]/;
  const norm = (s) => String(s).toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '').replace(/[^\p{L}\p{N}]+/gu, ' ').trim();
  const tokens = (q) => [...new Set(norm(q).split(' ').filter(Boolean))];
  const own = (o, k) => Object.prototype.hasOwnProperty.call(o, k);
  const SYN = { ble: ['bluetooth'], bluetooth: ['ble'], il2cpp: ['unity'], unity: ['il2cpp'], decompiler: ['decompilation', 'decompile'],
    decompile: ['decompiler', 'decompilation'], apk: ['android'], android: ['apk', 'dex'], fw: ['firmware'], ios: ['ipa', 'iphone'],
    js: ['javascript'], wasm: ['webassembly'], webassembly: ['wasm'], disassembler: ['disassembly'], usb: ['hid'] };
  const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  const loadIndex = () => {
    if (IDX) return Promise.resolve(IDX);
    if (!idxP) {
      idxP = fetch(`/search-index${zh ? '.zh' : ''}.json`)
        .then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); })
        .then(prep)
        .catch((err) => { idxP = null; throw err; });
    }
    return idxP;
  };
  const words = (s) => s.split(' ').filter(Boolean);
  // Normalising ~5,000 records is chunked so loading the index never makes a long task (TBT).
  const yieldTask = () => new Promise((r) => setTimeout(r, 0));
  async function chunked(list, fn, size = 400) {
    const out = [];
    for (let i = 0; i < list.length; i += size) {
      for (const x of list.slice(i, i + size)) out.push(fn(x));
      await yieldTask();
    }
    return out;
  }
  // The evidence link: GitHub rows carry owner/repo/blob/<sha>/path; anything else keeps its full URL and its label.
  // The owner arrives with the text file, so a search by owner matches from then on.
  function setEvidence(r, owner, rest) {
    r.ev = owner ? `${owner}/${r.label}${rest}` : rest;
    const seg = owner ? r.ev.split('/') : null;
    r.repo = owner ? `${owner}/${r.label}` : r.label;
    r.sha = seg && /^(blob|tree)$/.test(seg[2]) ? seg[3].slice(0, 7) : '';
    r.nAlias = norm(`${r.alias} ${r.repo}`); r.aw = words(r.nAlias);
  }
  async function prep(raw) {
    const res = await chunked(raw.r, ([idc, name, k, tg, c, label, feat, al, conn, cls, st, sec, rev, added]) => {
      const targets = [...tg].map(Number);
      const base = label.split('/').pop();
      const id = typeof idc === 'string' ? idc : slug(base) + (idc === 1 ? '-case' : '');
      const alias = al === 1 ? base : al;
      const tags = [raw.kindLabels[k], raw.kindPlural[k], raw.kinds[k], raw.categoryLabels[c], ...targets.map((i) => `${raw.targetLabels[i]} ${raw.targets[i]}`)].join(' ');
      const r = { type: 'r', id, name, k, kind: raw.kinds[k], targets, c, lead: '', label, repo: label, sha: '', ev: '', rev, added, feat, alias, conn,
        sec, pin: raw.pinned.includes(id), cls, st, prev: '', prevKind: '',
        nName: norm(name), nAlias: norm(`${alias} ${label}`), nTags: norm(tags), nDesc: '' };
      r.nw = words(r.nName); r.aw = words(r.nAlias); r.tw = words(r.nTags); r.dw = [];
      return r;
    });
    const pap = await chunked(raw.p, ([id, name, year, venue, t, arxiv, section]) => {
      const r = { type: 'p', id, name, year, venue, t, arxiv, section, kind: 'paper', feat: -1,
        nName: norm(name), nAlias: norm(arxiv), nTags: norm(`${venue} ${year} ${raw.targetLabels[t]} paper papers research 论文`), nDesc: '' };
      r.nw = words(r.nName); r.aw = words(r.nAlias); r.tw = words(r.nTags); r.dw = [];
      return r;
    });
    const all = res.concat(pap);
    all.forEach((r, i) => { r.i = i; });
    // Name order is computed once: sorting then compares two integers instead of two strings per step.
    const collator = new Intl.Collator(zh ? 'zh-CN' : 'en', { sensitivity: 'base' });
    all.slice().sort((a, b) => collator.compare(a.name, b.name) || (a.id < b.id ? -1 : 1)).forEach((r, i) => { r.nr = i; });
    const X = { raw, res, pap, all };
    await vocab(X);
    // Published only once its word lists exist, so a keystroke during the build waits for the index instead.
    IDX = X;
    loadText();
    return IDX;
  }
  function loadText() {
    if (!txtP) {
      txtP = fetch(`/search-text${zh ? '.zh' : ''}.json`)
        .then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); })
        .then(async (j) => {
          if (j.n !== IDX.res.length || j.b !== IDX.raw.b) throw new Error('search text does not match the index');
          let i = 0;
          await chunked(j.t, ([lead, owner, rest, prev, prevKind, thumb]) => {
            const r = IDX.res[i++];
            r.lead = lead; r.prev = prev === 1 ? `/previews/${r.id}.png` : prev; r.prevKind = prevKind;
            r.thumb = thumb === 1 ? `/previews/thumbs/${r.id}.webp` : thumb || '';
            r.nDesc = norm(lead); r.dw = words(r.nDesc);
            setEvidence(r, owner, rest);
          });
          await vocab(IDX, ['a', 'd']);
          IDX.text = true;
          onText.forEach((f) => { try { f(); } catch (e) { /* a view that is gone */ } });
        })
        .catch(() => { txtP = null; });
    }
    return txtP;
  }
  // Each distinct word points at the records that hold it, per field, so a keystroke compares a few thousand distinct
  // words instead of every word of every record.
  const memo = new Map();
  // Builds the word lists of the given fields in slices between keystrokes, then swaps them in at once; the text file
  // only changes the alias and description fields.
  const FIELD_WORDS = { n: 'nw', a: 'aw', t: 'tw', d: 'dw' };
  async function vocab(X, fields = ['n', 'a', 't', 'd']) {
    const V = { ...X.V, keys: { ...(X.V && X.V.keys) } };
    for (const f of fields) V[f] = new Map();
    await chunked(X.all, (r) => {
      for (const f of fields) {
        for (const w of new Set(r[FIELD_WORDS[f]])) { let ids = V[f].get(w); if (!ids) V[f].set(w, ids = []); ids.push(r.i); }
      }
    }, 800);
    // Sorted words per field: the words that start with a token form one run, found by binary search.
    for (const f of fields) { V.keys[f] = [...V[f].keys()].sort(); await yieldTask(); }
    X.V = V;
    memo.clear();
  }
  function firstAtLeast(keys, t) {
    let lo = 0;
    let hi = keys.length;
    while (lo < hi) { const mid = (lo + hi) >> 1; if (keys[mid] < t) lo = mid + 1; else hi = mid; }
    return lo;
  }
  // Restricted Damerau–Levenshtein distance between a (its first al characters) and b is at most k. Three reused rows,
  // so the thousands of comparisons behind one keystroke allocate nothing.
  const D0 = new Int32Array(66);
  const D1 = new Int32Array(66);
  const D2 = new Int32Array(66);
  function near(a, b, k, al = a.length) {
    const bl = b.length;
    if (Math.abs(al - bl) > k) return false;
    if (bl > 64) return dist(a.slice(0, al), b, k) <= k;
    let p2 = D2;
    let p1 = D1;
    let cur = D0;
    for (let j = 0; j <= bl; j += 1) p1[j] = j;
    for (let i = 1; i <= al; i += 1) {
      const ca = a.charCodeAt(i - 1);
      const pa = i > 1 ? a.charCodeAt(i - 2) : -1;
      cur[0] = i;
      let best = i;
      for (let j = 1; j <= bl; j += 1) {
        const cb = b.charCodeAt(j - 1);
        let v = Math.min(p1[j] + 1, cur[j - 1] + 1, p1[j - 1] + (ca === cb ? 0 : 1));
        if (i > 1 && j > 1 && ca === b.charCodeAt(j - 2) && pa === cb) v = Math.min(v, p2[j - 2] + 1);
        cur[j] = v;
        if (v < best) best = v;
      }
      if (best > k) return false;
      const t = p2; p2 = p1; p1 = cur; cur = t;
    }
    return p1[bl] <= k;
  }
  function cjk(r, t) {
    if (r.nName.includes(t)) return 120;
    if (r.nTags.includes(t)) return 60;
    if (r.nDesc.includes(t)) return 25;
    if (t.length < 3) return 0;
    const grams = [];
    for (let i = 0; i < t.length - 1; i += 1) grams.push(t.slice(i, i + 2));
    const hay = `${r.nName} ${r.nTags} ${r.nDesc}`;
    const hit = grams.filter((g) => hay.includes(g)).length;
    if (hit / grams.length < 0.6) return 0;
    return 10 + hit * 6 + (grams.some((g) => r.nTags.includes(g)) ? 20 : 0) + (grams.some((g) => r.nName.includes(g)) ? 30 : 0);
  }
  // A token's score for every record: the first tier a record meets, in this order — name word prefix 120,
  // inside the name (6+ letters) 40, alias or repository 70, kind/category/target 45, description 18, then one typo
  // (two from 8 letters) in the name 55, alias 40, tags 30, description 8.
  function tokScores(t) {
    let a = memo.get(t);
    if (a) return a;
    if (memo.size > 300) memo.clear();
    a = new Int16Array(IDX.all.length);
    if (CJK.test(t)) {
      for (const r of IDX.all) a[r.i] = cjk(r, t);
    } else {
      const V = IDX.V;
      const mark = (field, test, val) => { for (const [w, ids] of V[field]) if (test(w)) for (const i of ids) if (!a[i]) a[i] = val; };
      const pre = (field, val) => {
        const keys = V.keys[field];
        for (let x = firstAtLeast(keys, t); x < keys.length && keys[x].startsWith(t); x += 1) for (const i of V[field].get(keys[x])) if (!a[i]) a[i] = val;
      };
      pre('n', 120);
      if (t.length >= 6) for (const r of IDX.all) if (!a[r.i] && r.nName.includes(t)) a[r.i] = 40;
      pre('a', 70);
      pre('t', 45);
      if (t.length > 2) pre('d', 18);
      if (t.length >= 4) {
        const k = t.length >= 8 ? 2 : 1;
        mark('n', (w) => near(w, t, k) || (w.length > t.length && near(w, t, k, t.length)), 55);
        mark('a', (w) => near(w, t, k), 40);
        mark('t', (w) => near(w, t, k), 30);
        mark('d', (w) => w.length >= 4 && near(w, t, k), 8);
      }
    }
    memo.set(t, a);
    return a;
  }
  const variants = (toks) => toks.map((t) => [t, ...(own(SYN, t) ? SYN[t] : [])]);
  function score(r, q, vars) {
    let s = 0;
    for (const vs of vars) {
      let best = 0;
      for (const a of vs) { const x = a[r.i]; if (x > best) best = x; }
      if (!best) return 0;
      s += best;
    }
    if (r.nName === q) s += 1000;
    else if (r.nName.startsWith(q)) s += 800;
    else if (r.aw.includes(q) || r.nAlias === q) s += 700;
    else if (q.length > 2 && ` ${r.nName}`.includes(` ${q}`)) s += 500;
    // A typo of the whole name ("radere2", "jdax") ranks that record above names that merely contain the word.
    else if (q.length >= 4 && near(r.nName, q, q.length >= 8 ? 2 : 1)) s += 400;
    if (r.type === 'r') s += 6 + (r.feat >= 0 ? 12 - r.feat : 0) + ({ tool: 4, integration: 3 }[r.kind] || 0);
    return s;
  }
  const scoreVars = (q) => variants(tokens(q)).map((vs) => vs.map(tokScores));
  const byName = (a, b) => a.nr - b.nr;
  const KIND_RANK = { tool: 0, integration: 1, project: 2, 'case-study': 3, collection: 4, research: 5, 'learning-resource': 6, documentation: 7 };
  const ORDERS = {
    featured: (a, b) => (b.pin - a.pin) || ((a.feat < 0 ? 999 : a.feat) - (b.feat < 0 ? 999 : b.feat)) || (KIND_RANK[a.kind] - KIND_RANK[b.kind]) || byName(a, b),
    reviewed: (a, b) => (b.rev > a.rev ? 1 : b.rev < a.rev ? -1 : 0) || byName(a, b),
    added: (a, b) => ((b.added || '') > (a.added || '') ? 1 : (b.added || '') < (a.added || '') ? -1 : 0) || ORDERS.featured(a, b),
    name: byName,
  };
  function search(list, q) {
    if (IDX && !IDX.text) loadText();
    const toks = tokens(q);
    if (!toks.length) return list.map((r) => ({ r, s: 0 }));
    const nq = norm(q);
    const vars = scoreVars(q);
    const out = [];
    for (const r of list) { const s = score(r, nq, vars); if (s > 0) out.push({ r, s }); }
    return out;
  }
  const hitOrder = (order, q) => (q && order === 'featured' ? (a, b) => (b.s - a.s) || byName(a.r, b.r) : (a, b) => ORDERS[order](a.r, b.r));
  const sortHits = (hits, order, q) => hits.sort(hitOrder(order, q));
  // The first n hits in the order sortHits gives, without sorting the rest.
  function topHits(hits, order, q, n) {
    if (hits.length <= n) return sortHits(hits.slice(), order, q);
    const cmp = hitOrder(order, q);
    const top = [];
    for (const h of hits) {
      if (top.length === n && cmp(h, top[n - 1]) >= 0) continue;
      let j = top.length;
      while (j && cmp(h, top[j - 1]) < 0) j -= 1;
      top.splice(j, 0, h);
      if (top.length > n) top.pop();
    }
    return top;
  }
  function hl(text, toks) {
    if (!toks.length) return esc(text);
    const low = text.toLowerCase();
    const ranges = [];
    for (const t of toks) {
      let i = low.indexOf(t);
      while (i !== -1) {
        if (CJK.test(t) || i === 0 || !/[\p{L}\p{N}]/u.test(low[i - 1])) ranges.push([i, i + t.length]);
        i = low.indexOf(t, i + t.length);
      }
    }
    if (!ranges.length) return esc(text);
    ranges.sort((a, b) => a[0] - b[0]);
    let out = '';
    let at = 0;
    for (const [a, b] of ranges) {
      if (b <= at) continue;
      const s = Math.max(a, at);
      out += `${esc(text.slice(at, s))}<mark>${esc(text.slice(s, b))}</mark>`;
      at = b;
    }
    return out + esc(text.slice(at));
  }
  function callno(r) {
    const X = IDX.raw;
    return r.type === 'p' ? `${X.targetCodes[r.t]}·PAPR` : `${X.targetCodes[r.targets[0]]}·${X.kindCodes[r.k]}`;
  }
  const href = (r) => (r.type === 'p' ? `${P}/papers/${r.id}/` : `${P}/resources/${r.id}/`);
  function classChip(r) {
    if (r.st === 'unknown') return `<span class="card-class card-class-unknown" title="${esc(T.unknownTitle)}">?</span>`;
    if (r.cls == null || r.cls < 0) return '';
    const detail = T.classDetail[r.cls] || '';
    return `<span class="card-class card-class-${r.cls}" title="${esc(`${T.classLabel} ${r.cls} · ${detail}`)}">C${r.cls}</span>`;
  }
  // On /resources/ (thumb) a row shows the small thumbnail when there is one; a screenshot thumbnail links the full image.
  function previewHTML(r, thumb) {
    if (r.prev) {
      const video = r.prevKind === 'video';
      const small = thumb && r.thumb;
      const img = `<img src="${esc(small || r.prev)}" alt="${esc(video ? T.previewVideoAlt : T.previewAlt)}" loading="lazy" decoding="async">`;
      return `<figure class="card-preview">${video ? '<span class="card-preview-play" aria-hidden="true">▶</span>' : ''}`
        + `${small && !video ? `<a class="card-preview-link" href="${esc(r.prev)}" aria-label="${esc(T.previewFull(r.name))}">${img}</a>` : img}</figure>`;
    }
    if (r.prevKind === 'demo') {
      return `<figure class="card-preview card-preview-demo"><span class="card-preview-play" aria-hidden="true">▶</span><span>${esc(T.demoNote)}</span></figure>`;
    }
    return '';
  }
  function cardHTML(r, toks, thumb = false) {
    const X = IDX.raw;
    const t0 = r.targets[0];
    const label = `${X.targetLabels[t0]} · ${X.kindLabels[r.k]}`;
    const tg = r.targets.slice(0, 3).map((i) => `<li>${ico(X.targets[i])}${esc(X.targetLabels[i])}</li>`).join('')
      + (r.targets.length > 3 ? `<li class="more">+${r.targets.length - 3}</li>` : '');
    const ev = !r.ev || /^https?:/.test(r.ev) ? r.ev : `https://github.com/${r.ev}`;
    const repo = `<span class="ev-repo">${esc(r.repo)}</span>${r.sha ? `<span class="sha">@${esc(r.sha)}</span>` : ''}`;
    return `<li class="card${r.kind === 'case-study' ? ' is-case' : ''}" id="r-${esc(r.id)}" data-id="${esc(r.id)}"><article class="card-face">`
      + `<p class="callno" title="${esc(label)}"><span class="vh">${esc(label)}: </span><span aria-hidden="true">${callno(r)}</span></p>`
      + `<h3 class="card-name"><a class="stretch" href="${href(r)}">${hl(r.name, toks)}</a>${r.pin ? `<span class="row-mark">${T.featured}</span>` : ''}${classChip(r)}</h3>`
      + `<p class="card-desc">${hl(r.lead, toks)}</p>${previewHTML(r, thumb)}`
      + `<ul class="card-targets" aria-label="${T.targets}">${tg}</ul>`
      + `<p class="stamp">${ico('check')}<span>${T.reviewed} <time datetime="${r.rev}">${r.rev}</time></span>`
      + (ev ? `<a class="ev" href="${esc(ev)}" rel="noopener">${repo}</a>` : `<span class="ev">${repo}</span>`) + '</p></article></li>';
  }
  // Damerau–Levenshtein distance, stopping once every path is past max.
  function dist(a, b, max) {
    if (Math.abs(a.length - b.length) > max) return max + 1;
    let p2 = null;
    let p1 = Array.from({ length: b.length + 1 }, (_, j) => j);
    for (let i = 1; i <= a.length; i += 1) {
      const cur = [i];
      let best = i;
      for (let j = 1; j <= b.length; j += 1) {
        let v = Math.min(p1[j] + 1, cur[j - 1] + 1, p1[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
        if (i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) v = Math.min(v, p2[j - 2] + 1);
        cur[j] = v;
        if (v < best) best = v;
      }
      if (best > max) return max + 1;
      p2 = p1; p1 = cur;
    }
    return p1[b.length];
  }
  // The four titles closest to the query by edit distance, compared over the query's length plus two letters.
  function nearNames(q, list) {
    const t = norm(q).replace(/ /g, '');
    if (!t) return [];
    // One edit for short queries, two up to eight letters, three beyond.
    const max = t.length <= 4 ? 1 : t.length <= 8 ? 2 : 3;
    return list.map((r) => [dist(t, r.nName.replace(/ /g, '').slice(0, t.length + 2), max), r])
      .filter((x) => x[0] <= max).sort((a, b) => (a[0] - b[0]) || ORDERS.featured(a[1], b[1])).slice(0, 4).map((x) => x[1]);
  }
  function emptyHTML(q, list, tag = 'div', clearable = false) {
    const close = q ? nearNames(q, list) : [];
    const chips = close.map((r) => `<a class="chip" href="${href(r)}">${esc(r.name)}</a>`).join('');
    const clear = clearable ? `<p><button class="btn" type="button" data-empty-clear>${T.clearSearch}</button></p>` : '';
    const elsewhere = q ? `<p><a href="${P}/explore/?view=source-index&sourceq=${encodeURIComponent(q)}">${T.sources(q)}</a></p><p><a href="${P}/discoveries/">${T.discoveries}</a></p>` : '';
    return `<${tag} class="empty"><p>${q ? T.none(q) : T.noneFilters}</p>${chips ? `<p>${T.near}</p><p class="near">${chips}</p>` : ''}${clear}${elsewhere}`
      + `<p><a href="${ISSUE}" rel="noopener">${T.suggest}</a></p></${tag}>`;
  }
  // Exposed for the search-quality test (tests/e2e/search_queries.json) and for debugging ranking.
  // A small remainder stays on the page before it, so a last page never holds fewer than five rows.
  const pageRange = (total, per, requested) => {
    const rest = total % per;
    const pages = Math.max(1, rest && rest < 5 ? Math.floor(total / per) : Math.ceil(total / per));
    const page = Math.min(requested, pages);
    const start = (page - 1) * per;
    return { pages, page, start, end: page === pages ? total : start + per };
  };
  window.REA_SEARCH = { loadIndex, search, tokens, norm, score: (r, q) => score(r, norm(q), scoreVars(q)), sortHits, loadText, nearNames, pageRange };
  // Warm the index once the page has loaded and gone idle (or on first focus/keystroke, whichever is first).
  const idle = (f) => {
    const go = () => (window.requestIdleCallback ? requestIdleCallback(f, { timeout: 4000 }) : setTimeout(f, 1500));
    if (document.readyState === 'complete') go(); else window.addEventListener('load', go, { once: true });
  };
  const warm = () => loadIndex().catch(() => {});

  /* ---------- ⌘K palette ---------- */
  const dlg = $('[data-palette]');
  const pal = { input: dlg && $('[data-pal-input]', dlg), list: dlg && $('[data-pal-list]', dlg), extra: dlg && $('[data-pal-extra]', dlg),
    body: dlg && $('[data-pal-body]', dlg), count: dlg && $('[data-pal-count]', dlg), items: [], active: -1, opener: null };
  // The listbox only ever holds groups of options; recent searches, empty states and "see all" live beside it.
  const palShow = (listHTML, extraHTML) => {
    put(pal.list, listHTML);
    pal.list.hidden = !listHTML;
    put(pal.extra, extraHTML);
    pal.input.setAttribute('aria-expanded', String(!!listHTML));
  };
  const recent = () => { try { const v = JSON.parse(store.get('rea-recent') || '[]'); return Array.isArray(v) ? v.filter((x) => typeof x === 'string').slice(0, 6) : []; } catch (e) { return []; } };
  // Storage writes wait for an idle moment, so a write never lands between two keystrokes.
  const whenIdle = window.requestIdleCallback ? (f) => requestIdleCallback(f, { timeout: 3000 }) : (f) => setTimeout(f, 200);
  const remember = (q) => { if (q) whenIdle(() => { const r = recent(); if (r[0] !== q) store.set('rea-recent', JSON.stringify([q, ...r.filter((x) => x !== q)].slice(0, 6))); }); };
  const POPULAR = ['Ghidra', 'Frida', 'IDA MCP', 'JADX', 'Binwalk', 'IL2CPP'];
  function palRest() {
    const rec = recent();
    const btn = (q) => `<button class="chip" type="button" data-pal-seed="${esc(q)}">${esc(q)}</button>`;
    return (rec.length ? `<div class="pal-group"><div class="pal-gh">${T.recent}</div><div class="pal-recent">${rec.map(btn).join('')}</div></div>` : '')
      + `<div class="pal-group"><div class="pal-gh">${T.popular}</div><div class="pal-recent">${POPULAR.map(btn).join('')}</div></div>`;
  }
  function palSet(i, scroll = true) {
    pal.active = i;
    $$('[role="option"]', pal.list).forEach((o) => o.setAttribute('aria-selected', String(+o.dataset.i === i)));
    if (i >= 0) pal.input.setAttribute('aria-activedescendant', `po-${i}`); else pal.input.removeAttribute('aria-activedescendant');
    if (scroll && i >= 0) { const o = $(`#po-${i}`); if (o) o.scrollIntoView({ block: 'nearest' }); }
  }
  function palRender() {
    const q = pal.input.value.trim();
    pal.items = [];
    if (!q) { palShow('', palRest()); pal.count.textContent = ''; palSet(-1); return; }
    if (!IDX) { palShow('', `<div class="pal-empty"><p>${T.loading}</p></div>`); return; }
    performance.mark('rea-search-start');
    const toks = tokens(q);
    const hits = sortHits(search(IDX.all, q), 'featured', q);
    const groups = [['tool', (h) => h.r.kind === 'tool'], ['case-study', (h) => h.r.kind === 'case-study'], ['integration', (h) => h.r.kind === 'integration'],
      ['other', (h) => h.r.type === 'r' && !['tool', 'case-study', 'integration'].includes(h.r.kind)], ['paper', (h) => h.r.type === 'p']];
    let html = '';
    let i = 0;
    // Groups follow their best hit, so the strongest match is always first ("IDA MCP" lists Integrations first).
    const ranked = groups.map(([key, test]) => [key, hits.filter(test)]).filter(([, g]) => g.length).sort((a, b) => b[1][0].s - a[1][0].s);
    for (const [key, g] of ranked) {
      html += `<div class="pal-group" role="group" aria-labelledby="pg-${key}"><div class="pal-gh" id="pg-${key}">${T.groups[key]} <span class="count">${fmt(g.length)}</span></div>`;
      for (const { r } of g.slice(0, key === 'tool' ? 6 : 4)) {
        pal.items.push(r);
        const meta = r.type === 'p' ? `${esc(r.venue)}` : esc(IDX.raw.targetLabels[r.targets[0]]);
        const desc = r.type === 'p' ? `${r.year}${r.arxiv ? ` · arXiv ${r.arxiv}` : ''}` : r.lead;
        html += `<div class="pal-opt" role="option" id="po-${i}" data-i="${i}" aria-selected="false"><span class="lt-call">${callno(r)}</span>`
          + `<span class="pal-name">${hl(r.name, toks)}</span><span class="pal-desc">${hl(desc, toks)}</span><span class="pal-meta">${meta}</span></div>`;
        i += 1;
      }
      html += '</div>';
    }
    if (hits.length) palShow(html, `<a class="pal-all" href="${P}/explore/?q=${encodeURIComponent(q)}">${T.seeAll(hits.length)}</a>`);
    else palShow('', emptyHTML(q, IDX.all, 'div').replace('class="empty"', 'class="pal-empty"'));
    pal.count.textContent = T.results(hits.length);
    palSet(pal.items.length ? 0 : -1, false);
    performance.measure('rea-search', 'rea-search-start');
  }
  // The descriptions re-render the list; the selected option stays selected.
  onText.push(() => {
    if (!dlg || !dlg.open || !pal.input.value.trim()) return;
    const was = pal.items[pal.active];
    palRender();
    const i = pal.items.indexOf(was);
    if (i > 0) palSet(i, false);
  });
  function palGo(i, newTab) {
    const r = pal.items[i];
    const q = pal.input.value.trim();
    if (!r) { if (q) location.href = `${P}/explore/?q=${encodeURIComponent(q)}`; return; }
    remember(q);
    if (newTab) window.open(href(r), '_blank', 'noopener'); else location.href = href(r);
  }
  function palOpen(seed = '') {
    if (!dlg) return;
    pal.opener = document.activeElement;
    if (!dlg.open) dlg.showModal();
    pal.input.value = seed;
    pal.input.focus();
    palRender();
    loadIndex().then(palRender).catch(() => { palShow('', `<div class="pal-empty"><p>${T.failed}</p></div>`); });
  }
  if (dlg) {
    document.addEventListener('click', (e) => { if (e.target.closest('[data-palette-open]')) palOpen(); });
    $('[data-pal-close]', dlg).addEventListener('click', () => dlg.close());
    dlg.addEventListener('click', (e) => { if (e.target === dlg) dlg.close(); });
    dlg.addEventListener('close', () => { if (pal.opener && pal.opener.focus) pal.opener.focus({ preventScroll: true }); });
    pal.input.addEventListener('input', palRender);
    pal.input.addEventListener('keydown', (e) => {
      // A search input eats the first Escape to clear itself; in the palette one press closes.
      if (e.key === 'Escape') { e.preventDefault(); dlg.close(); return; }
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        if (pal.items.length) palSet((pal.active + (e.key === 'ArrowDown' ? 1 : -1) + pal.items.length) % pal.items.length);
      } else if (e.key === 'Enter') { e.preventDefault(); palGo(pal.active, e.metaKey || e.ctrlKey); }
    });
    pal.body.addEventListener('click', (e) => {
      const seed = e.target.closest('[data-pal-seed]');
      if (seed) { pal.input.value = seed.dataset.palSeed; pal.input.focus(); palRender(); return; }
      const o = e.target.closest('[role="option"]');
      if (o) palGo(+o.dataset.i, e.metaKey || e.ctrlKey);
    });
    pal.list.addEventListener('pointermove', (e) => { const o = e.target.closest('[role="option"]'); if (o && +o.dataset.i !== pal.active) palSet(+o.dataset.i, false); });
  }
  const typing = (el) => el && (el.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName));
  document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      if (dlg && dlg.open) dlg.close(); else palOpen();
    } else if (e.key === '/' && !typing(e.target) && !(dlg && dlg.open) && !$('#search-input')) {
      const f = $('[data-search-input]') || $('[data-list-input]') || $('[data-shelf-input]') || $('[data-nf-search]');
      e.preventDefault();
      const box = f && f.getBoundingClientRect();
      if (box && f.offsetParent && box.top >= coveredTop() && box.bottom <= innerHeight) f.focus(); else palOpen();
    }
  });

  /* ---------- announcement: dismissal is remembered; the inline head script applies it before first paint ---------- */
  $$('[data-ann-close]').forEach((button) => button.addEventListener('click', () => {
    document.documentElement.classList.add('ann-off');
    try { localStorage.setItem('rea-ann-websitebench', '1'); } catch (e) { /* storage may be unavailable: it returns on the next page */ }
  }));

  /* ---------- home drawer: instant search in place, folder tabs, kind chips, sort ---------- */
  const form = $('[data-home-search]');
  // Links into the old homepage's views keep working: they open the full explorer with the same state.
  const OLD_VIEW = ['category', 'group', 'order', 'layout', 'lang', 'topic', 'sourceq', 'source-target', 'source-category'];
  const oldQuery = new URLSearchParams(location.search);
  if (form && ((oldQuery.get('view') && oldQuery.get('view') !== 'curated') || OLD_VIEW.some((k) => oldQuery.has(k)) || location.hash === '#shortlist')) {
    location.replace(`${P}/explore/${location.search}${location.hash}`);
  } else if (form) {
    const input = $('[data-search-input]', form);
    const count = $('[data-search-count]', form);
    const drawer = $('[data-drawer]');
    const list = $('[data-cards]', drawer);
    const meta = $('[data-drawer-meta]', drawer);
    const showAll = $('[data-show-all]', drawer);
    const tabs = $$('.masthead .folder');
    const chips = $$('[data-kind-chips] .chip');
    const sort = $('[data-sort]', drawer);
    const kindSel = $('[data-kind-select]', drawer);
    const classSel = $('[data-class-select]', drawer);
    const info = $('.info-btn', drawer);
    const init = { list: list.innerHTML, meta: meta.innerHTML, all: showAll.innerHTML, tabs: tabs.map((t) => $('.count', t).textContent), chips: chips.map((c) => $('.count', c).textContent) };
    const more = Object.assign(document.createElement('button'), { type: 'button', className: 'btn', hidden: true });
    list.after(more);
    const papersBox = document.createElement('div');
    papersBox.className = 'drawer-results-papers';
    papersBox.hidden = true;
    more.after(papersBox);
    const u = new URL(location.href);
    const wantedClass = u.searchParams.get('class');
    const st = { q: u.searchParams.get('q') || '', target: u.searchParams.get('target') || 'all', kinds: new Set((u.searchParams.get('kind') || '').split(',').filter(Boolean)),
      cls: ['0', '1', '2', '3', 'unknown'].includes(wantedClass) ? wantedClass : '', sort: u.searchParams.get('sort') || 'featured', shown: 10 };
    input.value = st.q;
    sort.value = st.sort;
    classSel.value = st.cls;
    const pristine = () => !st.q && st.target === 'all' && !st.kinds.size && !st.cls && st.sort === 'featured';
    const foot = $('.drawer-foot', drawer);
    $('.hs-side', form).insertAdjacentHTML('afterbegin', `<span class="hs-keys" aria-hidden="true"><kbd>↑</kbd><kbd>↓</kbd> ${T.keyMove} <kbd>↵</kbd> ${T.keyOpen} <kbd>Esc</kbd> ${T.keyClear}</span>`);
    let selected = -1;
    const select = (index, reveal) => {
      const cards = $$('.card', list);
      cards.forEach((card, i) => card.classList.toggle('is-active', i === index));
      selected = cards[index] ? index : -1;
      form.classList.toggle('has-hits', selected >= 0);
      if (selected >= 0) input.setAttribute('aria-activedescendant', cards[selected].id); else input.removeAttribute('aria-activedescendant');
      if (selected >= 0 && reveal) cards[selected].scrollIntoView({ block: 'nearest' });
    };
    const langLink = $('.site-header a[hreflang]');
    const langBase = langLink ? langLink.getAttribute('href') : '';
    const params = () => {
      const p = new URLSearchParams();
      if (st.q) p.set('q', st.q);
      if (st.kinds.size) p.set('kind', [...st.kinds].join(','));
      if (st.cls) p.set('class', st.cls);
      if (st.sort !== 'featured') p.set('sort', st.sort);
      return p;
    };
    let urlT = 0;
    let urlNext = null;
    let typingNow = false;
    const flushURL = () => { clearTimeout(urlT); if (urlNext) urlNext(); };
    const render = async () => {
      form.classList.toggle('has-query', !!st.q);
      tabs.forEach((t) => { if (t.dataset.target === st.target) t.setAttribute('aria-current', 'true'); else t.removeAttribute('aria-current'); });
      chips.forEach((c) => c.setAttribute('aria-pressed', String(st.kinds.has(c.dataset.kind))));
      kindSel.value = st.kinds.size === 1 ? [...st.kinds][0] : '';
      classSel.value = st.cls;
      const hp = params();
      if (st.target !== 'all') hp.set('target', st.target);
      // The browser URL follows once typing pauses: history.replaceState costs more than the search itself.
      const url = location.pathname + (hp.toString() ? `?${hp}` : '') + location.hash;
      clearTimeout(urlT);
      urlNext = () => { urlNext = null; if (url !== location.pathname + location.search + location.hash) history.replaceState(null, '', url); };
      if (typingNow) urlT = setTimeout(urlNext, 300); else urlNext();
      const ex = new URLSearchParams();
      if (st.q) ex.set('q', st.q);
      if (st.target !== 'all') ex.set('target', st.target);
      if (st.kinds.size) ex.set('kind', [...st.kinds].join(','));
      if (st.cls) ex.set('class', st.cls);
      if (st.sort !== 'featured') ex.set('sort', st.sort);
      if (langLink) langLink.href = langBase + (hp.toString() ? `?${hp}` : '');
      showAll.href = `${P}/resources/${ex.toString() ? `?${ex}` : ''}`;
      if (pristine()) {
        const rec = document.activeElement === input ? recent() : [];
        put(list, (rec.length ? `<li class="drawer-recent"><span class="pal-gh">${T.recent}</span> <span class="pal-recent">${rec.map((q) => `<button class="chip" type="button" data-recent="${esc(q)}">${esc(q)}</button>`).join(' ')}</span></li>` : '') + init.list);
        put(meta, init.meta); showAll.innerHTML = init.all; count.textContent = '';
        tabs.forEach((t, i) => { $('.count', t).textContent = init.tabs[i]; });
        chips.forEach((c, i) => { $('.count', c).textContent = init.chips[i]; c.disabled = false; });
        more.hidden = true; papersBox.hidden = true; foot.hidden = false;
        select(-1);
        return;
      }
      let X;
      if (!IDX) drawer.setAttribute('aria-busy', 'true');
      try { X = await loadIndex(); } catch (e) { meta.textContent = T.failed; drawer.removeAttribute('aria-busy'); return; }
      drawer.removeAttribute('aria-busy');
      performance.mark('rea-search-start');
      const toks = tokens(st.q);
      const ti = X.raw.targets.indexOf(st.target);
      const base = search(X.res, st.q);
      const kindOK = (h) => !st.kinds.size || st.kinds.has(h.r.kind);
      const classOK = (h) => !st.cls || (st.cls === 'unknown' ? h.r.st === 'unknown' : String(h.r.cls) === st.cls);
      const targetOK = (h) => st.target === 'all' || h.r.targets.includes(ti);
      // One pass counts every tab and chip.
      const perTarget = new Array(X.raw.targets.length).fill(0);
      const perKind = {};
      let inAll = 0;
      for (const h of base) {
        if (!classOK(h)) continue;
        if (kindOK(h)) { inAll += 1; for (const i of new Set(h.r.targets)) perTarget[i] += 1; }
        if (targetOK(h)) perKind[h.r.kind] = (perKind[h.r.kind] || 0) + 1;
      }
      tabs.forEach((t) => {
        const i = X.raw.targets.indexOf(t.dataset.target);
        $('.count', t).textContent = fmt(i < 0 ? inAll : perTarget[i]);
      });
      const inTarget = base.filter(targetOK);
      chips.forEach((c) => {
        const n = perKind[c.dataset.kind] || 0;
        $('.count', c).textContent = fmt(n);
        c.disabled = !n && !st.kinds.has(c.dataset.kind);
      });
      const hits = inTarget.filter((h) => kindOK(h) && classOK(h));
      const shown = topHits(hits, st.sort, st.q, st.shown);
      put(list, hits.length ? shown.map((h) => cardHTML(h.r, toks)).join('') : emptyHTML(st.q, X.res, 'li', true));
      select(st.q && hits.length ? 0 : -1);
      foot.hidden = !hits.length;
      put(meta, hits.length ? T.showing(shown.length, hits.length) : '');
      showAll.innerHTML = `${T.all(hits.length)}${ico('arrow')}`;
      count.textContent = st.q ? T.results(hits.length) : '';
      const left = hits.length - shown.length;
      more.hidden = left <= 0;
      more.textContent = T.more(Math.min(10, left));
      if (st.q) {
        const ph = search(X.pap, st.q);
        papersBox.hidden = !ph.length;
        put(papersBox, ph.length ? `<h3 class="side-h">${T.papers} <span class="count">${fmt(ph.length)}</span></h3><ol class="papers">${topHits(ph, 'featured', st.q, 3).map(({ r }) =>
          `<li class="paper"><span class="pp-date">${r.year}</span><div class="pp-body"><h4 class="pp-title"><a href="${href(r)}">${hl(r.name, toks)}</a></h4><p class="pp-meta"><span class="pp-venue">${esc(r.venue)}</span></p></div></li>`).join('')}</ol>` : '');
      } else papersBox.hidden = true;
      performance.measure('rea-search', 'rea-search-start');
    };
    onText.push(() => {
      if (pristine()) return;
      const was = selected >= 0 && $$('.card', list)[selected];
      const id = was && was.id;
      render();
      const i = id ? $$('.card', list).findIndex((c) => c.id === id) : -1;
      if (i > 0) select(i);
    });
    let settle = 0;
    // A query that stays on screen with results for 1.5 s, or that opens a result, joins the recent searches.
    const keep = () => { flushURL(); if (st.q && $('.card', list)) remember(st.q); };
    input.addEventListener('blur', flushURL);
    input.addEventListener('focus', () => { if (pristine() && recent().length) render(); });
    const clearSearch = () => { input.value = ''; st.q = ''; st.shown = 10; render(); };
    // The first character brings the search box up under the header, so the results fill the screen.
    const raiseSearch = () => {
      const bar = $('.site-header');
      const top = (bar && getComputedStyle(bar).position === 'sticky' ? bar.offsetHeight : 0) + 24;
      const gap = form.getBoundingClientRect().top - top;
      if (Math.abs(gap) < 4) return;
      const still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      window.scrollBy({ top: gap, behavior: still ? 'auto' : 'smooth' });
    };
    input.addEventListener('focus', warm, { once: true });
    // Enter opens the selected result; with none selected the results are already on the page.
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const link = selected >= 0 && $('.card-name a', $$('.card', list)[selected]);
      // Leaving for the result: the pending address-bar write is dropped, so the only navigation is to the result.
      if (link) { clearTimeout(urlT); urlNext = null; clearTimeout(settle); remember(st.q); location.href = link.href; return; }
      st.q = input.value.trim(); st.shown = 10; render();
    });
    input.addEventListener('input', () => {
      const had = !!st.q;
      // The selection belongs to the previous query until the new results render.
      select(-1);
      st.q = input.value.trim(); st.shown = 10;
      // In the same task as the keystroke, so the results paint in the next frame.
      typingNow = true; render(); typingNow = false;
      clearTimeout(settle); settle = setTimeout(keep, 1500);
      if (st.q && !had) raiseSearch();
    });
    $('[data-search-clear]', form).addEventListener('click', () => { clearSearch(); input.focus(); });
    list.addEventListener('click', (e) => {
      if (e.target.closest('[data-empty-clear]')) { clearSearch(); input.focus(); return; }
      const seed = e.target.closest('[data-recent]');
      if (seed) { input.value = seed.dataset.recent; input.dispatchEvent(new Event('input')); input.focus(); return; }
      if (e.target.closest('.card-name a')) keep();
    });
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        if (input.value) { e.preventDefault(); clearSearch(); } else input.blur();
      } else if ((e.key === 'ArrowDown' || e.key === 'ArrowUp') && selected >= 0) {
        e.preventDefault();
        select(Math.max(0, Math.min($$('.card', list).length - 1, selected + (e.key === 'ArrowDown' ? 1 : -1))), true);
      }
    });
    tabs.forEach((t) => t.addEventListener('click', (e) => {
      if (e.metaKey || e.ctrlKey || e.shiftKey) return;
      e.preventDefault(); st.target = t.dataset.target; st.shown = 10; render();
    }));
    chips.forEach((c) => c.addEventListener('click', () => {
      const k = c.dataset.kind;
      if (st.kinds.has(k)) st.kinds.delete(k); else st.kinds.add(k);
      st.shown = 10; render();
    }));
    sort.addEventListener('change', () => { st.sort = sort.value; render(); });
    kindSel.addEventListener('change', () => { st.kinds = new Set(kindSel.value ? [kindSel.value] : []); st.shown = 10; render(); });
    classSel.addEventListener('change', () => { st.cls = classSel.value; st.shown = 10; render(); });
    if (info) {
      const setInfo = (open) => info.setAttribute('aria-expanded', String(open));
      info.addEventListener('click', () => setInfo(info.getAttribute('aria-expanded') !== 'true'));
      document.addEventListener('click', (e) => { if (!e.target.closest('.info-wrap')) setInfo(false); });
      document.addEventListener('keydown', (e) => { if (e.key === 'Escape') setInfo(false); });
    }
    more.addEventListener('click', () => { st.shown += 10; render(); });
    if (!pristine()) render();
  }

  /* ---------- static listing pages: an older #fragment for a row or section on another page opens that page ---------- */
  // map names each fragment's page; a target matching placeholder is a link standing in for content on another page.
  const openPageFor = async (map, base, current, placeholder) => {
    try {
      const key = decodeURIComponent(location.hash.slice(1));
      if (!/^[a-z0-9-]+$/.test(key)) return;
      const target = document.getElementById(key);
      if (target && !target.matches(placeholder)) return;
      const page = (await (await fetch(map)).json())[key];
      if (page && String(page) !== current) location.replace(`${P}${base}${page > 1 ? `page/${page}/` : ''}#${key}`);
    } catch { /* a malformed fragment or a failed fetch leaves the page where it is */ }
  };

  /* ---------- /resources/: facets, sort, pagination, URL state ---------- */
  const listing = $('[data-listing]');
  if (listing) {
    const per = +listing.dataset.perPage || 60;
    // Before the static pages, /resources/?page=N paged 60 rows at a time in place; open the static page holding that row.
    const legacy = new URL(location.href).searchParams;
    if ([...legacy.keys()].join() === 'page') {
      const row = (Math.max(1, Math.floor(+legacy.get('page')) || 1) - 1) * 60;
      const page = Math.min(Math.floor(row / per) + 1, +listing.dataset.pages || 1);
      location.replace(`${P}/resources/${page > 1 ? `page/${page}/` : ''}${location.hash}`);
    }
    const list = $('[data-cards]', listing);
    const meta = $('[data-results-meta]', listing);
    const pagerEl = $('[data-pager]', listing);
    const sort = $('[data-sort]', listing);
    const classSel = $('[data-class-select]', listing);
    const activeEl = $('[data-active]', listing);
    const clearBtn = $('[data-clear]', listing);
    const badge = $('[data-filter-count]', listing);
    const facetsDlg = $('[data-facets]', listing);
    const facetForm = $('[data-facets-form]', listing);
    const input = $('[data-list-input]');
    const tabs = $$('.page-head .folder');
    const init = { list: list.innerHTML, meta: meta.innerHTML, pager: pagerEl.outerHTML };
    const sections = $$('[data-section-link]', listing);
    const counted = [...$$('.opt-n', facetForm), ...tabs.map((t) => $('.count', t)), ...sections.map((a) => $('.count', a))].map((el) => [el, el.textContent]);
    let narrowed = false;
    const MULTI = ['kind', 'category', 'connection', 'section'];
    const st = {};
    const read = () => {
      const u = new URL(location.href);
      st.q = u.searchParams.get('q') || '';
      st.targets = new Set((u.searchParams.get('target') || '').split(',').filter(Boolean));
      MULTI.forEach((k) => { st[k] = new Set((u.searchParams.get(k) || '').split(',').filter(Boolean)); });
      st.reviewed = u.searchParams.get('reviewed') || '';
      const cls = u.searchParams.get('class') || '';
      st.cls = ['0', '1', '2', '3', 'unknown'].includes(cls) ? cls : '';
      if (classSel) classSel.value = st.cls;
      st.sort = u.searchParams.get('sort') || 'featured';
      st.page = Math.max(1, +(u.searchParams.get('page') || 1));
      if (input) input.value = st.q;
      sort.value = st.sort;
      $$('input', facetForm).forEach((el) => {
        if (el.type === 'radio') el.checked = el.value === st.reviewed;
        else el.checked = st[el.name] && st[el.name].has(el.value);
      });
    };
    read();
    const nActive = () => MULTI.reduce((n, k) => n + st[k].size, 0) + (st.reviewed ? 1 : 0) + (st.cls ? 1 : 0) + st.targets.size;
    const pristine = () => !st.q && !nActive() && st.sort === 'featured' && st.page === 1;
    const write = (push) => {
      const p = new URLSearchParams();
      if (st.q) p.set('q', st.q);
      if (st.targets.size) p.set('target', [...st.targets].join(','));
      MULTI.forEach((k) => { if (st[k].size) p.set(k, [...st[k]].join(',')); });
      if (st.reviewed) p.set('reviewed', st.reviewed);
      if (st.cls) p.set('class', st.cls);
      if (st.sort !== 'featured') p.set('sort', st.sort);
      if (st.page > 1) p.set('page', st.page);
      // Unfiltered, a static page keeps its own address; filters always apply to the whole catalogue at /resources/.
      const url = p.toString() ? `${P}/resources/?${p}` : `${listing.dataset.base || `${P}/resources/`}${location.hash}`;
      if (push) history.pushState(null, '', url); else history.replaceState(null, '', url);
    };
    const pagerHTML = (page, pages) => {
      if (pages <= 1) return '<nav class="pager" aria-label="Pages" data-pager></nav>';
      const shown = [...new Set([1, 2, page - 1, page, page + 1, pages - 1, pages])].filter((n) => n >= 1 && n <= pages).sort((a, b) => a - b);
      let last = 0;
      let items = '';
      for (const n of shown) {
        if (n - last > 1) items += '<li class="gap" aria-hidden="true">…</li>';
        items += `<li><a href="${P}/resources/?page=${n}" data-page="${n}"${n === page ? ' aria-current="page"' : ''}>${n}</a></li>`;
        last = n;
      }
      const step = (n, label, rel) => (n >= 1 && n <= pages ? `<a class="pg-step" href="${P}/resources/?page=${n}" data-page="${n}" rel="${rel}">${label}</a>` : `<span class="pg-step" aria-disabled="true">${label}</span>`);
      return `<nav class="pager" aria-label="Pages" data-pager>${step(page - 1, zh ? '上一页' : 'Previous', 'prev')}<ol>${items}</ol>${step(page + 1, zh ? '下一页' : 'Next', 'next')}</nav>`;
    };
    const labelFor = (name, value) => {
      if (name === 'section') {
        const link = sections.find((a) => a.dataset.section === value);
        return link ? link.firstChild.textContent : value;
      }
      const el = $(`input[name="${name}"][value="${CSS.escape(value)}"]`, facetForm);
      return el ? $('.opt-l', el.closest('.opt')).textContent : value;
    };
    const render = async (push = false, scroll = false) => {
      if (classSel) classSel.value = st.cls;
      tabs.forEach((t) => {
        const on = t.dataset.target === 'all' ? !st.targets.size : st.targets.size === 1 && st.targets.has(t.dataset.target);
        if (on) t.setAttribute('aria-current', 'true'); else t.removeAttribute('aria-current');
      });
      const n = nActive();
      badge.hidden = !n; badge.textContent = n;
      clearBtn.hidden = !n && !st.q;
      write(push);
      if (pristine()) {
        if (!narrowed) return;
        narrowed = false;
        list.innerHTML = init.list; meta.innerHTML = init.meta; activeEl.hidden = true;
        $('[data-pager]', listing).outerHTML = init.pager;
        counted.forEach(([el, text]) => { el.textContent = text; });
        $$('.opt.is-zero', facetForm).forEach((opt) => opt.classList.remove('is-zero'));
        sections.forEach((a) => { a.classList.remove('is-zero'); a.removeAttribute('aria-current'); });
        listing.classList.remove('is-narrowed');
        return;
      }
      narrowed = true;
      listing.classList.add('is-narrowed');
      let X;
      try { X = await loadIndex(); } catch (e) { meta.textContent = T.failed; return; }
      // The listing shows descriptions and previews, so it renders once the text file is in.
      await loadText();
      const R = X.raw;
      const since = (days) => new Date(Date.parse(R.generated_at) - days * 864e5).toISOString().slice(0, 10);
      const tests = {
        target: (r) => !st.targets.size || [...st.targets].some((t) => r.targets.includes(R.targets.indexOf(t))),
        kind: (r) => !st.kind.size || st.kind.has(r.kind),
        category: (r) => !st.category.size || st.category.has(R.categories[r.c]),
        connection: (r) => !st.connection.size || st.connection.has(R.connections[r.conn]),
        section: (r) => !st.section.size || st.section.has(R.sections[r.sec]),
        reviewed: (r) => !st.reviewed || r.rev >= since(+st.reviewed),
        class: (r) => !st.cls || (st.cls === 'unknown' ? r.st === 'unknown' : r.cls === Number(st.cls)),
      };
      const base = search(X.res, st.q);
      const pass = (r, skip) => Object.entries(tests).every(([k, f]) => k === skip || f(r));
      $$('.opt', facetForm).forEach((opt) => {
        const el = $('input', opt);
        const nEl = $('.opt-n', opt);
        if (!nEl) return;
        const name = el.name;
        const v = el.value;
        const c = base.filter(({ r }) => pass(r, name) && (name === 'kind' ? r.kind === v : name === 'category' ? R.categories[r.c] === v
          : name === 'connection' ? R.connections[r.conn] === v : name === 'reviewed' ? r.rev >= since(+v) : true)).length;
        nEl.textContent = fmt(c);
        opt.classList.toggle('is-zero', !c);
      });
      sections.forEach((a) => {
        const v = a.dataset.section;
        const c = base.filter(({ r }) => pass(r, 'section') && R.sections[r.sec] === v).length;
        $('.count', a).textContent = fmt(c);
        a.classList.toggle('is-zero', !c);
        if (st.section.has(v)) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current');
      });
      tabs.forEach((t) => {
        const i = R.targets.indexOf(t.dataset.target);
        $('.count', t).textContent = fmt(base.filter(({ r }) => pass(r, 'target') && (i < 0 || r.targets.includes(i))).length);
      });
      const hits = sortHits(base.filter(({ r }) => pass(r)), st.sort, st.q);
      const { pages, page, start: a, end } = pageRange(hits.length, per, st.page);
      st.page = page;
      const slice = hits.slice(a, end);
      const toks = tokens(st.q);
      list.innerHTML = slice.length ? slice.map((h) => cardHTML(h.r, toks, true)).join('') : emptyHTML(st.q, X.res, 'li');
      meta.innerHTML = hits.length ? T.range(a + 1, a + slice.length, hits.length) : T.results(0);
      $('[data-pager]', listing).outerHTML = pagerHTML(st.page, pages);
      const chipsHTML = [...[...st.targets].map((v) => ['target', v, R.targetLabels[R.targets.indexOf(v)]]),
        ...MULTI.flatMap((k) => [...st[k]].map((v) => [k, v, labelFor(k, v)])),
        ...(st.reviewed ? [['reviewed', st.reviewed, labelFor('reviewed', st.reviewed)]] : []),
        ...(st.cls ? [['class', st.cls, st.cls === 'unknown' ? T.unknownTitle : `${T.classLabel} ${st.cls}`]] : [])]
        .map(([k, v, l]) => `<button class="chip" type="button" data-unset="${k}" data-v="${esc(v)}" aria-label="${esc(T.remove(l))}">${esc(l)}${ico('close')}</button>`).join('');
      activeEl.innerHTML = chipsHTML;
      activeEl.hidden = !chipsHTML;
      if (scroll) listing.scrollIntoView({ block: 'start' });
    };
    let raf = 0;
    const later = () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(() => render()); };
    facetForm.addEventListener('change', (e) => {
      const el = e.target;
      if (el.type === 'radio') st.reviewed = el.value;
      else if (el.checked) st[el.name].add(el.value); else st[el.name].delete(el.value);
      st.page = 1; render();
    });
    if (input) {
      input.addEventListener('focus', warm, { once: true });
      input.addEventListener('input', () => { st.q = input.value.trim(); st.page = 1; later(); });
      $('[data-list-search]').addEventListener('submit', (e) => { e.preventDefault(); input.blur(); });
    }
    sort.addEventListener('change', () => { st.sort = sort.value; st.page = 1; render(); });
    if (classSel) classSel.addEventListener('change', () => { st.cls = classSel.value; st.page = 1; render(); });
    tabs.forEach((t) => t.addEventListener('click', (e) => {
      if (e.metaKey || e.ctrlKey || e.shiftKey) return;
      e.preventDefault();
      st.targets = new Set(t.dataset.target === 'all' ? [] : [t.dataset.target]);
      st.page = 1; render();
    }));
    listing.addEventListener('click', (e) => {
      const a = e.target.closest('[data-page]');
      if (a && a.closest('[data-pager]')) {
        // The unfiltered list pages through its static pages; filtered results page in place.
        if (e.metaKey || e.ctrlKey || !narrowed) return;
        e.preventDefault(); st.page = +a.dataset.page; render(true, true);
        return;
      }
      const u = e.target.closest('[data-unset]');
      if (u) {
        const { unset: k, v } = u.dataset;
        if (k === 'target') st.targets.delete(v); else if (k === 'reviewed') st.reviewed = ''; else if (k === 'class') st.cls = ''; else st[k].delete(v);
        $$('input', facetForm).forEach((el) => { if (el.type === 'radio') el.checked = el.value === st.reviewed; else el.checked = st[el.name].has(el.value); });
        st.page = 1; render();
      }
    });
    const reset = () => {
      st.q = ''; if (input) input.value = '';
      st.targets.clear(); MULTI.forEach((k) => st[k].clear()); st.reviewed = ''; st.cls = ''; st.page = 1; st.sort = 'featured'; sort.value = 'featured';
      if (classSel) classSel.value = '';
      $$('input', facetForm).forEach((el) => { el.checked = el.type === 'radio' && el.value === ''; });
      render();
    };
    clearBtn.addEventListener('click', reset);
    // On the whole list a section link jumps to its heading. On a narrowed list its count promises those rows, so it filters to them.
    sections.forEach((a) => a.addEventListener('click', (e) => {
      if (pristine() || e.metaKey || e.ctrlKey || e.shiftKey) return;
      e.preventDefault();
      st.section = new Set(st.section.has(a.dataset.section) ? [] : [a.dataset.section]);
      st.page = 1; render();
    }));
    $$('[data-facets-open]').forEach((b) => b.addEventListener('click', () => facetsDlg.showModal()));
    $$('[data-facets-close]').forEach((b) => b.addEventListener('click', () => facetsDlg.close()));
    facetsDlg.addEventListener('click', (e) => { if (e.target === facetsDlg) facetsDlg.close(); });
    window.addEventListener('popstate', () => { read(); render(); });
    if (!pristine()) render();
    // Deferred card layout can move a distant fragment after the browser's initial hash jump.
    const hashTarget = () => {
      try { return document.getElementById(decodeURIComponent(location.hash.slice(1))); } catch { return null; }
    };
    const revealHash = () => {
      const target = hashTarget();
      if (!target || !list.contains(target)) return;
      let frames = 0, stopped = false;
      const stop = () => { stopped = true; };
      const inputs = ['wheel', 'touchstart', 'keydown', 'pointerdown'];
      inputs.forEach((t) => window.addEventListener(t, stop, { once: true, passive: true }));
      const settle = () => {
        if (stopped || target !== hashTarget()) return;
        const top = target.getBoundingClientRect().top;
        if (top < 0 || top >= innerHeight) target.scrollIntoView({ block: 'start', behavior: 'instant' });
        if (++frames < 120) requestAnimationFrame(settle);
        else inputs.forEach((t) => window.removeEventListener(t, stop));
      };
      requestAnimationFrame(settle);
    };
    // An older link to a row or section on another static page goes to that page.
    // A section's old fragment sits on its sidebar link until scripts open the page where the section starts.
    const findPage = () => { if (!location.search) openPageFor('/resources/pages.json', '/resources/', listing.dataset.staticPage, '[data-section-link]'); };
    findPage();
    window.addEventListener('hashchange', () => { findPage(); revealHash(); });
    if (document.readyState === 'complete') revealHash();
    else window.addEventListener('load', revealHash, { once: true });
    // The static page needs no index; it loads on the first touch, pointer or focus, before a filter can be chosen.
    ['pointerover', 'touchstart', 'focusin', 'keydown'].forEach((type) => document.addEventListener(type, warm, { once: true, passive: true }));
  }

  /* ---------- /cases/: an older link to a case or section on another static page goes to that page ---------- */
  const casePages = $('.cases-collection[data-case-page]');
  if (casePages) {
    // A section on another page keeps its old fragment on its navigation link.
    const findCasePage = () => openPageFor('/cases/pages.json', '/cases/', casePages.dataset.casePage, '.cases-nav a, .case-method-nav a');
    findCasePage();
    window.addEventListener('hashchange', findCasePage);
  }

  /* ---------- /cases/: filter the shelf in place ---------- */
  const shelfInput = $('[data-shelf-input]');
  if (shelfInput) {
    const spines = $$('[data-shelves] .shelf li');
    const counter = $('[data-shelf-count]');
    const data = spines.map((li) => norm(li.textContent));
    const run = () => {
      const toks = tokens(shelfInput.value);
      let n = 0;
      spines.forEach((li, i) => { const ok = toks.every((t) => data[i].includes(t) || (SYN[t] || []).some((v) => data[i].includes(v))); li.hidden = !ok; n += ok; });
      $$('[data-shelves] .method, [data-shelves] .case-section').forEach((s) => { s.hidden = !$$('.shelf li:not([hidden])', s).length; });
      counter.textContent = toks.length ? T.shelf(n, spines.length) : '';
    };
    shelfInput.addEventListener('input', run);
    $('[data-shelf-search]').addEventListener('submit', (e) => e.preventDefault());
  }

  /* ---------- /discoveries/: load the rest of a class from its own page, in place ---------- */
  $$('[data-discovery-more]').forEach((link) => {
    link.addEventListener('click', async (e) => {
      if (e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      e.preventDefault();
      if (link.getAttribute('aria-busy') === 'true') return;
      const section = link.closest('section');
      const list = $('.source-results', section);
      link.setAttribute('aria-busy', 'true');
      try {
        const response = await fetch(link.href);
        if (!response.ok) throw new Error(String(response.status));
        const page = new DOMParser().parseFromString(await response.text(), 'text/html');
        const have = new Set($$('article[id]', list).map((card) => card.id));
        const added = $$(`#${CSS.escape(section.id)} .source-results > article[id]`, page).filter((card) => !have.has(card.id));
        list.append(...added.map((card) => document.importNode(card, true)));
        const heading = $('h2[data-heading-all]', section);
        if (heading) heading.textContent = heading.dataset.headingAll;
        const shown = $('[data-discovery-shown]');
        if (shown) shown.textContent = fmt($$('.discovery-batch .source-results > article').length);
        const note = $('[data-shown-all]', link.closest('.load-more-row'));
        if (note) note.textContent = note.dataset.shownAll;
        const first = added.length && $('a', list.querySelector(`#${CSS.escape(added[0].id)}`));
        link.remove();
        if (first) first.focus();
      } catch (error) {
        location.assign(link.href);
      }
    });
  });
})();
