/* Evidence-score directory: client-side filtering, sorting and the audit panel.
   All displayed values come from the generated table or the JSON data file; the
   script never evaluates source text and never builds HTML from it. */
(function () {
  'use strict';

  var main = document.querySelector('[data-quality-data]');
  if (!main) return;
  var dataURL = main.getAttribute('data-quality-data');
  var checksURL = main.getAttribute('data-quality-checks') || '';
  var labels = {};
  try { labels = JSON.parse(main.getAttribute('data-labels') || '{}'); } catch (error) { labels = {}; }

  var table = document.getElementById('quality-table');
  var tbody = table ? table.tBodies[0] : null;
  var count = document.getElementById('quality-count');
  var empty = document.getElementById('quality-empty');
  var search = document.getElementById('quality-search');
  var kind = document.getElementById('quality-kind');
  var target = document.getElementById('quality-target');
  var band = document.getElementById('quality-band');
  var confidence = document.getElementById('quality-confidence');
  var sort = document.getElementById('quality-sort');
  var detail = document.getElementById('quality-detail');
  var backdrop = document.getElementById('quality-detail-backdrop');
  var detailBody = document.getElementById('quality-detail-body');
  var detailTitle = document.getElementById('quality-detail-title');
  var closeButton = document.getElementById('quality-detail-close');
  var dataPromise = null;
  var checkLabels = {};
  var checkLabelsZh = {};
  var lastFocus = null;

  function text(key, fallback) {
    return Object.prototype.hasOwnProperty.call(labels, key) ? labels[key] : fallback;
  }

  function rows() {
    return tbody ? Array.prototype.slice.call(tbody.rows) : [];
  }

  function matches(row) {
    var query = (search && search.value || '').trim().toLowerCase();
    if (query) {
      var haystack = [
        row.getAttribute('data-name') || '',
        row.getAttribute('data-name-zh') || '',
        row.getAttribute('data-id') || '',
        row.getAttribute('data-url') || '',
        row.getAttribute('data-kind') || '',
        row.getAttribute('data-targets') || ''
      ].join(' ').toLowerCase();
      if (haystack.indexOf(query) === -1) return false;
    }
    if (kind && kind.value && row.getAttribute('data-kind') !== kind.value) return false;
    if (target && target.value) {
      var targets = (row.getAttribute('data-targets') || '').split(' ');
      if (targets.indexOf(target.value) === -1) return false;
    }
    if (band && band.value && row.getAttribute('data-band') !== band.value) return false;
    if (confidence && confidence.value && row.getAttribute('data-confidence') !== confidence.value) return false;
    return true;
  }

  function compare(a, b) {
    var mode = sort && sort.value || 'score-desc';
    if (mode === 'name') {
      return (a.getAttribute('data-name') || '').localeCompare(b.getAttribute('data-name') || '');
    }
    if (mode === 'coverage') {
      return Number(b.getAttribute('data-coverage') || 0) - Number(a.getAttribute('data-coverage') || 0);
    }
    if (mode === 'confidence') {
      var order = {high: 0, medium: 1, low: 2, none: 3};
      return (order[a.getAttribute('data-confidence')] || 9) - (order[b.getAttribute('data-confidence')] || 9);
    }
    var av = a.getAttribute('data-score');
    var bv = b.getAttribute('data-score');
    if (av === '' && bv === '') return 0;
    if (av === '') return 1;
    if (bv === '') return -1;
    return mode === 'score-asc' ? Number(av) - Number(bv) : Number(bv) - Number(av);
  }

  function apply() {
    if (!tbody) return;
    var visible = 0;
    rows().forEach(function (row) {
      var show = matches(row);
      row.hidden = !show;
      if (show) visible += 1;
    });
    var ordered = rows().sort(compare);
    ordered.forEach(function (row) { tbody.appendChild(row); });
    if (count) {
      count.textContent = text('count', 'Showing') + ' ' + visible + ' / ' + rows().length;
    }
    if (empty) empty.hidden = visible !== 0;
  }

  function loadData() {
    if (dataPromise) return dataPromise;
    dataPromise = fetch(dataURL, {credentials: 'same-origin'})
      .then(function (response) {
        if (!response.ok) throw new Error('HTTP ' + response.status);
        return response.json();
      })
      .then(function (data) {
        checkLabels = (data && data.meta && data.meta.check_labels) || {};
        checkLabelsZh = (data && data.meta && data.meta.check_labels_zh) || {};
        return data;
      })
      .catch(function () { return {entries: []}; });
    return dataPromise;
  }

  function node(tag, className, value) {
    var item = document.createElement(tag);
    if (className) item.className = className;
    if (value !== undefined && value !== null) item.textContent = value;
    return item;
  }

  function mainEntry(id) {
    return loadData().then(function (data) {
      var entries = (data && data.entries) || [];
      for (var index = 0; index < entries.length; index += 1) {
        if (entries[index].id === id) return entries[index];
      }
      return null;
    });
  }

  function evidenceFor(id) {
    if (!checksURL) return mainEntry(id);
    var detailURL = checksURL + encodeURIComponent(id) + '.json';
    // Load the compact index first so check labels are available even when the
    // per-entry detail file is served from a warm cache.
    return loadData().then(function () {
      return fetch(detailURL, {credentials: 'same-origin'});
    }).then(function (response) {
      if (!response.ok) throw new Error('HTTP ' + response.status);
      return response.json();
    }).catch(function () { return mainEntry(id); });
  }

  function renderDetail(entry) {
    if (!detailBody) return;
    detailBody.textContent = '';
    if (!entry) {
      detailBody.appendChild(node('p', 'quality-note', text('detailUnavailable', 'Detail data is unavailable.')));
      return;
    }
    if (detailTitle) {
      detailTitle.textContent = entry.name_zh && document.documentElement.lang === 'zh-CN'
        ? entry.name_zh : entry.name;
    }

    var meta = node('div', 'quality-detail-meta');
    var score = entry.score === null ? '—' : Number(entry.score).toFixed(1);
    meta.appendChild(node('span', 'quality-score quality-band-' + entry.band, score));
    meta.appendChild(node('span', '', bandLabel(entry)));
    meta.appendChild(node('span', '', text('confidence', 'Confidence') + ': ' + entry.confidence));
    meta.appendChild(node('span', '', text('coverage', 'Evidence coverage') + ': ' + Number(entry.coverage).toFixed(1) + '%'));
    detailBody.appendChild(meta);

    var links = node('div', 'quality-detail-links');
    if (entry.entry_url) {
      var entryLink = node('a', '', text('openEntry', 'Open catalog entry'));
      entryLink.href = entry.entry_url;
      links.appendChild(entryLink);
    }
    if (entry.url) {
      var sourceLink = node('a', '', text('openSource', 'Open upstream source ↗'));
      sourceLink.href = entry.url;
      sourceLink.target = '_blank';
      sourceLink.rel = 'noopener';
      links.appendChild(sourceLink);
    }
    detailBody.appendChild(links);

    var dimensions = node('div', 'quality-detail-dimensions');
    (entry.dimension_details || []).forEach(function (dimension) {
      var row = node('div', 'quality-dimension' + (dimension.applicable ? '' : ' is-na'));
      row.appendChild(node('h3', '', dimension.label));
      var scoreNode = node('span', 'quality-dim-score',
        dimension.applicable ? (dimension.score === null ? '—' : Number(dimension.score).toFixed(1)) : text('notApplicable', 'N/A'));
      row.appendChild(scoreNode);
      var track = node('div', 'quality-track');
      var fill = node('span');
      fill.style.setProperty('--v', dimension.applicable ? String(dimension.score || 0) : '0');
      track.appendChild(fill);
      row.appendChild(track);
      dimensions.appendChild(row);
      if (dimension.applicable && dimension.checks && dimension.checks.length) {
        var list = node('ul', 'quality-checks');
        dimension.checks.forEach(function (check) {
          var item = node('li', 'quality-check ' + check[1]);
          item.appendChild(node('span', 'quality-check-dot'));
          var copy = node('div');
          var checkLabel = document.documentElement.lang === 'zh-CN'
            ? (checkLabelsZh[check[0]] || checkLabels[check[0]] || check[0])
            : (checkLabels[check[0]] || check[0]);
          copy.appendChild(node('strong', '', checkLabel));
          copy.appendChild(node('span', '', check[2]));
          item.appendChild(copy);
          list.appendChild(item);
        });
        row.appendChild(list);
        if (dimension.missing_count) {
          row.appendChild(node('p', 'quality-check-label',
            text('missingChecks', 'Missing checks') + ': ' + dimension.missing_count));
        }
      }
    });
    detailBody.appendChild(dimensions);

    if (entry.limitations && entry.limitations.length) {
      detailBody.appendChild(node('p', 'quality-check-label', text('limits', 'Limitations')));
      var limits = node('ul', 'quality-limits');
      entry.limitations.forEach(function (item) { limits.appendChild(node('li', '', item)); });
      detailBody.appendChild(limits);
    }
  }

  function bandLabel(entry) {
    if (document.documentElement.lang === 'zh-CN') return entry.band_zh || entry.band;
    return entry.band_en || entry.band;
  }

  function openDetail(id, focusTarget) {
    if (!detail || !detailBody) return;
    lastFocus = focusTarget || document.activeElement;
    detailBody.textContent = '';
    detailBody.appendChild(node('p', 'quality-note', text('loading', 'Loading evidence…')));
    detail.setAttribute('data-open', 'true');
    detail.setAttribute('aria-hidden', 'false');
    if (backdrop) backdrop.setAttribute('data-open', 'true');
    document.body.style.overflow = 'hidden';
    closeButton && closeButton.focus({preventScroll: true});
    evidenceFor(id).then(function (entry) {
      renderDetail(entry);
      if (closeButton) closeButton.focus({preventScroll: true});
    });
    if (history.replaceState) history.replaceState(null, '', '#' + encodeURIComponent(id));
  }

  function closeDetail() {
    if (!detail) return;
    detail.setAttribute('data-open', 'false');
    detail.setAttribute('aria-hidden', 'true');
    if (backdrop) backdrop.setAttribute('data-open', 'false');
    document.body.style.overflow = '';
    if (history.replaceState) history.replaceState(null, '', location.pathname + location.search);
    if (lastFocus && lastFocus.focus) lastFocus.focus({preventScroll: true});
  }

  if (tbody) {
    tbody.addEventListener('click', function (event) {
      var trigger = event.target.closest('[data-quality-open]');
      if (!trigger) {
        var row = event.target.closest('tr.quality-row');
        if (row && !event.target.closest('a')) trigger = row.querySelector('[data-quality-open]');
      }
      if (trigger) {
        event.preventDefault();
        openDetail(trigger.getAttribute('data-quality-open'), trigger);
      }
    });
  }
  [search, kind, target, band, confidence, sort].forEach(function (control) {
    if (control) control.addEventListener('input', apply);
    if (control) control.addEventListener('change', apply);
  });
  if (closeButton) closeButton.addEventListener('click', closeDetail);
  if (backdrop) backdrop.addEventListener('click', closeDetail);
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && detail && detail.getAttribute('data-open') === 'true') closeDetail();
  });

  apply();
  var hash = '';
  try { hash = decodeURIComponent((location.hash || '').replace(/^#/, '')); } catch (error) { hash = ''; }
  if (hash) {
    var initial = tbody && Array.prototype.slice.call(tbody.rows).filter(function (row) {
      return row.getAttribute('data-id') === hash;
    })[0];
    if (initial) openDetail(hash, initial.querySelector('[data-quality-open]'));
  }
}());
