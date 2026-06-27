function appUrl(path) {
  const prefix = (document.body && document.body.dataset.urlPrefix) || '';
  return prefix + path;
}

function fmtLetters(obj) {
  if (!obj || Object.keys(obj).length === 0) return '—';
  return Object.entries(obj).map(([c, n]) => c + (n > 1 ? '×' + n : '')).join(' ');
}

function fmtNum(n) {
  return Number(n).toLocaleString('de-DE');
}

function renderSteps(steps, mode = 'encode') {
  const cls = mode === 'decode' ? 'step-item decode' : 'step-item';
  return steps.map((s) => {
    let html = `<li class="${cls}"><div class="step-title">${s.title}</div>`;
    html += `<div class="step-detail">${s.detail}</div>`;
    if (s.lines && s.lines.length) {
      html += `<div class="step-lines">${s.lines.map((l) => escapeHtml(l)).join('<br>')}</div>`;
    }
    if (s.formula) {
      html += `<div class="step-formula">${escapeHtml(s.formula)}</div>`;
    }
    if (s.extra) {
      html += `<div class="step-detail">${escapeHtml(s.extra)}</div>`;
    }
    html += '</li>';
    return html;
  }).join('');
}

function escapeHtml(str) {
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}

function showResult(el, html) {
  el.classList.remove('hidden');
  el.innerHTML = html;
}

function showError(el, msg) {
  showResult(el, `<p class="error">${escapeHtml(msg)}</p>`);
}

function showLoading(el, msg = 'Berechne…') {
  showResult(el, `<p class="loading">${msg}</p>`);
}

let lastEncodeWords = null;

function fmtBytes(n) {
  n = Number(n);
  if (n < 1024) return `${fmtNum(n)} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1).replace('.', ',')} KB`;
  return `${(n / (1024 * 1024)).toFixed(2).replace('.', ',')} MB`;
}

const SIZE_EXT_ICONS = {
  '.txt': '📄',
  '.md': '📝',
  '.pdf': '📕',
  '.html': '🌐',
  '.json': '{ }',
  '.csv': '📊',
  '.gpm': '◈',
  '.zip': '🗜',
  '.si': 'SI',
};

const SIZE_VERDICT_LABELS = {
  win: 'GPM vorteilhaft',
  tie: 'Ungefähr gleich',
  learn: 'Einordnung',
};

function renderSizeCompare(data) {
  if (!data || !data.rows) return '';
  const highlights = new Set(data.highlight_ids || []);
  const insight = data.insight || {};
  const verdict = insight.verdict || 'learn';
  const maxBytes = data.max_bytes || Math.max(...data.rows.map((r) => r.bytes), 1);
  const categories = data.categories || {};

  const byCategory = {};
  data.rows.forEach((r) => {
    const cat = r.category || 'document';
    if (!byCategory[cat]) byCategory[cat] = [];
    byCategory[cat].push(r);
  });

  const categoryBlocks = Object.keys(byCategory).map((cat) => {
    const label = categories[cat] || cat;
    const cards = byCategory[cat].map((r) => {
      const cls = ['size-card'];
      if (r.is_gpm) cls.push('size-card-gpm');
      if (highlights.has(r.id)) cls.push('size-card-highlight');
      const icon = SIZE_EXT_ICONS[r.ext] || (r.is_gpm ? '◈' : '📦');
      const barPct = Math.max(3, Math.round((r.bytes / maxBytes) * 100));
      return `
        <article class="${cls.join(' ')}">
          <div class="size-card-head">
            <span class="size-card-icon" aria-hidden="true">${icon}</span>
            <div class="size-card-titles">
              <div class="size-card-label">${escapeHtml(r.label)}${r.ext ? `<span class="size-ext">${escapeHtml(r.ext)}</span>` : ''}</div>
              <div class="size-card-human mono">${escapeHtml(r.human || fmtBytes(r.bytes))}</div>
            </div>
            <div class="size-card-bytes mono">${fmtNum(r.bytes)} B</div>
          </div>
          <div class="size-bar-track" aria-hidden="true"><div class="size-bar-fill" style="width:${barPct}%"></div></div>
          ${r.formula ? `<div class="size-card-formula">${escapeHtml(r.formula)}</div>` : ''}
          ${r.note ? `<div class="size-card-note muted">${escapeHtml(r.note)}</div>` : ''}
        </article>`;
    }).join('');
    return `
      <section class="size-category">
        <h4 class="size-category-title">${escapeHtml(label)}</h4>
        <div class="size-card-grid">${cards}</div>
      </section>`;
  }).join('');

  const points = (insight.points || []).map((p) => `<li>${escapeHtml(p)}</li>`).join('');
  const calc = (data.calculation || []).map((step) => {
    const detail = typeof step === 'string' ? step : step.detail;
    const label = typeof step === 'string' ? 'Schritt' : step.label;
    const human = typeof step === 'object' && step.human ? `<span class="mono">${escapeHtml(step.human)}</span>` : '';
    return `<li><strong>${escapeHtml(label)}</strong>, ${escapeHtml(detail || '')} ${human}</li>`;
  }).join('');

  return `
    <div class="size-compare">
      <div class="size-insight size-insight-${escapeHtml(verdict)}">
        <div class="size-insight-badge">${escapeHtml(SIZE_VERDICT_LABELS[verdict] || verdict)}</div>
        <h3 class="size-insight-headline">${escapeHtml(insight.headline || data.summary || '')}</h3>
        ${insight.baseline_human ? `<p class="size-insight-baseline">Referenz: <strong>${escapeHtml(insight.baseline_label || 'Basis')}</strong> · ${escapeHtml(insight.baseline_human)}${insight.gpm_human ? ` · .gpm <strong>${escapeHtml(insight.gpm_human)}</strong>` : ''}</p>` : ''}
        ${points ? `<ul class="size-insight-points">${points}</ul>` : ''}
      </div>
      ${categoryBlocks}
      <details class="size-details">
        <summary>Rechenschritte anzeigen</summary>
        <ol class="size-calc">${calc}</ol>
      </details>
    </div>`;
}

async function runSizeCompare(endpoint, body, containerEl, btn) {
  if (!containerEl) {
    console.error('size-compare: Ergebnis-Container fehlt', endpoint);
    return;
  }
  const oldText = btn ? btn.textContent : '';
  if (btn) {
    btn.disabled = true;
    btn.textContent = 'Rechne…';
  }
  containerEl.classList.remove('hidden');
  showLoading(containerEl, 'Speichergrößen vergleichen…');
  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    let data;
    try {
      data = await res.json();
    } catch {
      if (res.status === 404) {
        showError(
          containerEl,
          'API nicht gefunden (404). Server neu starten: stop.bat, dann start.bat.',
        );
        return;
      }
      showError(containerEl, `Server-Antwort ungültig (HTTP ${res.status}).`);
      return;
    }
    if (!res.ok) {
      showError(containerEl, data.error || 'Vergleich fehlgeschlagen.');
      return;
    }
    showResult(containerEl, renderSizeCompare(data));
  } catch (err) {
    showError(
      containerEl,
      err && err.message === 'Failed to fetch'
        ? 'Server nicht erreichbar. Läuft start.bat?'
        : 'Netzwerkfehler.',
    );
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = oldText;
    }
  }
}

function wireEncodeSizeButtons(scope) {
  scope.querySelector('#encode-batch-size-btn')?.addEventListener('click', (ev) => {
    const btn = ev.currentTarget;
    const target = scope.querySelector('#encode-batch-size-result');
    if (!lastEncodeWords || !lastEncodeWords.length) return;
    runSizeCompare(
      appUrl('/api/size/encode-batch'),
      {
        words: lastEncodeWords.map((w) => ({
          original: w.original,
          normalized: w.normalized,
          substance: w.substance,
          perm_index: w.perm_index,
        })),
      },
      target,
      btn,
    );
  });

  scope.querySelectorAll('.btn-size-word').forEach((btn) => {
    btn.addEventListener('click', () => {
      const idx = Number(btn.dataset.wordIndex);
      const w = lastEncodeWords && lastEncodeWords[idx];
      if (!w) return;
      const target = btn.closest('.word-panel-body')?.querySelector('.size-result');
      runSizeCompare(
        appUrl('/api/size/encode-word'),
        {
          original: w.original,
          normalized: w.normalized,
          substance: w.substance,
          perm_index: w.perm_index,
        },
        target,
        btn,
      );
    });
  });
}

function wireDecodeSizeButton(scope, payload) {
  scope.querySelector('#decode-size-btn')?.addEventListener('click', (ev) => {
    runSizeCompare(appUrl('/api/size/decode'), payload, scope.querySelector('#decode-size-result'), ev.currentTarget);
  });
}

function wireGpmSizeButton(scope, payload) {
  scope.querySelector('.btn-gpm-size')?.addEventListener('click', (ev) => {
    runSizeCompare(appUrl('/api/size/gpm'), payload, scope.querySelector('.gpm-size-result'), ev.currentTarget);
  });
}

/* Tabs + Browser-Zurück (History API) */
const DEFAULT_TAB = 'konzept';
let currentTab = null;

const LEGACY_TAB_HASH = {
  vergleichen: { tab: 'wortpaar', pairMode: 'compare' },
  differenz: { tab: 'wortpaar', pairMode: 'diff' },
  verschluesseln: { tab: 'gpm', scrollToId: 'gpm-cipher-section' },
};

function isValidTab(tabId) {
  return !!tabId && !!document.getElementById('tab-' + tabId);
}

function resolveTabFromHash(hash) {
  const legacy = LEGACY_TAB_HASH[hash];
  if (legacy) return { ...legacy };
  if (isValidTab(hash)) return { tab: hash };
  return { tab: DEFAULT_TAB };
}

function tabFromLocation() {
  const hash = window.location.hash.replace(/^#/, '');
  return resolveTabFromHash(hash).tab;
}

function tabUrl(tabId) {
  const base = window.location.pathname + window.location.search;
  return tabId === DEFAULT_TAB ? base : `${base}#${tabId}`;
}

function getPairMode() {
  return document.querySelector('input[name="pair-mode"]:checked')?.value || 'compare';
}

function setPairMode(mode) {
  const value = mode === 'diff' ? 'diff' : 'compare';
  const radio = document.querySelector(`input[name="pair-mode"][value="${value}"]`);
  if (radio) radio.checked = true;
  refreshPairModeUi();
}

function refreshPairModeUi() {
  const mode = getPairMode();
  const isCompare = mode === 'compare';
  document.getElementById('pair-help-compare')?.classList.toggle('hidden', !isCompare);
  document.getElementById('pair-help-diff')?.classList.toggle('hidden', isCompare);
  const submitBtn = document.getElementById('wortpaar-submit');
  if (submitBtn) {
    submitBtn.textContent = isCompare ? 'Vergleichen' : 'Differenz berechnen';
  }
}

function scrollToElementId(elementId) {
  if (!elementId) return;
  requestAnimationFrame(() => {
    document.getElementById(elementId)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
}

function activateTab(tabId, { historyMode = 'none', pairMode = null, scrollToId = null } = {}) {
  if (!isValidTab(tabId)) tabId = DEFAULT_TAB;
  const sameTab = tabId === currentTab && historyMode === 'none' && pairMode == null && !scrollToId;
  if (sameTab) return;

  document.querySelectorAll('.tab-btn').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.tab === tabId);
    btn.setAttribute('aria-selected', btn.dataset.tab === tabId ? 'true' : 'false');
  });
  document.querySelectorAll('.tab-panel').forEach((panel) => {
    const active = panel.id === 'tab-' + tabId;
    panel.classList.toggle('active', active);
    panel.hidden = !active;
  });

  currentTab = tabId;
  if (pairMode) setPairMode(pairMode);

  window.scrollTo({ top: 0, behavior: 'instant' });
  document.querySelector(`.tab-btn[data-tab="${tabId}"]`)?.scrollIntoView({
    inline: 'nearest',
    block: 'nearest',
  });

  if (scrollToId) scrollToElementId(scrollToId);

  if (historyMode === 'push') {
    history.pushState({ tab: tabId, pairMode: pairMode || null }, '', tabUrl(tabId));
  } else if (historyMode === 'replace') {
    history.replaceState({ tab: tabId, pairMode: pairMode || null }, '', tabUrl(tabId));
  }
}

function initTabs() {
  const expectedVersion = document.body.dataset.appVersion || '';
  const gpmPanel = document.getElementById('tab-gpm');
  if (!gpmPanel) {
    const warn = document.createElement('p');
    warn.className = 'error';
    warn.style.margin = '1rem';
    warn.textContent = expectedVersion
      ? `Alte UI geladen, bitte start.bat neu starten (Build ${expectedVersion} erwartet).`
      : 'Alte UI geladen, bitte start.bat neu starten und Strg+F5.';
    document.querySelector('header')?.appendChild(warn);
  }

  document.querySelectorAll('input[name="pair-mode"]').forEach((el) => {
    el.addEventListener('change', refreshPairModeUi);
  });
  refreshPairModeUi();

  const initialHash = window.location.hash.replace(/^#/, '');
  const initialResolved = resolveTabFromHash(initialHash);
  activateTab(initialResolved.tab, {
    historyMode: 'replace',
    pairMode: initialResolved.pairMode,
    scrollToId: initialResolved.scrollToId,
  });

  window.addEventListener('popstate', (event) => {
    const state = event.state || {};
    const hash = window.location.hash.replace(/^#/, '');
    const resolved = resolveTabFromHash(hash);
    activateTab(state.tab || resolved.tab, {
      pairMode: state.pairMode || resolved.pairMode,
      scrollToId: resolved.scrollToId,
    });
  });

  window.addEventListener('hashchange', () => {
    const hash = window.location.hash.replace(/^#/, '');
    const resolved = resolveTabFromHash(hash);
    if (resolved.tab !== currentTab || resolved.pairMode || resolved.scrollToId) {
      activateTab(resolved.tab, {
        pairMode: resolved.pairMode,
        scrollToId: resolved.scrollToId,
      });
    }
  });

  document.querySelectorAll('.tab-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const tab = btn.dataset.tab;
      if (tab !== currentTab) {
        activateTab(tab, { historyMode: 'push' });
        if (tab === 'datenbank') refreshDbStats();
      }
    });
  });
}

initTabs();

/* Datenbank-Anzeige (live nach Encodieren aktualisieren) */
function applyDbStats(data) {
  const totalEl = document.getElementById('db-total-count');
  const statsEl = document.getElementById('db-lang-stats');
  if (!totalEl || !statsEl) return;
  totalEl.textContent = String(data.total_words ?? 0);
  if (!data.lang_stats || data.lang_stats.length === 0) {
    statsEl.innerHTML = '<p class="muted" id="db-empty-hint">Noch leer, Wörter im Tab Encodieren speichern oder <code>python scrape.py --source kevina</code></p>';
    return;
  }
  const items = data.lang_stats
    .map((row) => `<li>${escapeHtml(row.label)}: ${row.count}</li>`)
    .join('');
  statsEl.innerHTML = `<ul class="stats">${items}</ul>`;
}

async function refreshDbStats() {
  const statsEl = document.getElementById('db-lang-stats');
  if (!statsEl) return;
  try {
    const res = await fetch(appUrl('/api/db/stats'));
    if (!res.ok) {
      statsEl.innerHTML = '<p class="error">DB-Statistik nicht erreichbar, bitte <code>start.bat</code> neu starten.</p>';
      return;
    }
    applyDbStats(await res.json());
  } catch {
    statsEl.innerHTML = '<p class="error">DB-Statistik, Netzwerkfehler.</p>';
  }
}

function formatDbSaveMeta(data) {
  if (data.saved == null && data.db_duplicates == null) {
    return '<span class="error">Speichern nicht aktiv, bitte start.bat neu starten.</span>';
  }
  const parts = [];
  const saved = data.saved || 0;
  const dup = data.db_duplicates || 0;
  if (saved > 0) {
    parts.push(`<span><strong>${saved}</strong> neu in DB (${escapeHtml(data.language || 'Random / unsortiert')})</span>`);
  }
  if (dup > 0) {
    parts.push(`<span><strong>${dup}</strong> bereits vorhanden (Duplikat, Quelle web)</span>`);
  }
  if (saved === 0 && dup === 0) {
    parts.push('<span>Keine DB-Einträge (unerwartet)</span>');
  }
  if (data.db_total != null) {
    parts.push(`<span>DB gesamt: <strong>${data.db_total}</strong></span>`);
  }
  return parts.join('');
}

/* Encodieren, Batch mit Akkordeon */
document.getElementById('encode-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const el = document.getElementById('encode-result');
  showLoading(el, 'Encodiere…');
  try {
    const res = await fetch(appUrl('/api/encode'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: document.getElementById('encode-text').value }),
    });
    const data = await res.json();
    if (!res.ok) {
      showError(el, data.error || 'Fehler beim Encodieren.');
      return;
    }

    lastEncodeWords = data.words;

    let meta = `<div class="batch-meta">
      <span><strong>${data.count}</strong> Wort/Wörter encodiert</span>`;
    if (data.skipped) meta += `<span>${data.skipped} leere Token ignoriert</span>`;
    if (data.truncated) meta += `<span class="error">Nur erste ${data.max_words} Wörter (Limit)</span>`;
    meta += formatDbSaveMeta(data);
    meta += `</div>
      <div class="panel-actions">
        <button type="button" class="btn btn-secondary" id="encode-batch-size-btn">Speichergröße aller Wörter vergleichen</button>
      </div>
      <div id="encode-batch-size-result" class="size-result hidden"></div>`;

    const panels = data.words.map((w, i) => {
      const title = escapeHtml(w.display || w.original);
      const norm = escapeHtml(w.normalized);
      return `
        <details class="word-panel">
          <summary>
            <span class="word-index">#${i + 1}</span>
            <span class="word-title">${title}</span>
            <span class="word-brief">S=${fmtNum(w.substance)} · I=${fmtNum(w.perm_index)}</span>
          </summary>
          <div class="word-panel-body">
            <div class="result-summary">
              <div class="summary-box"><div class="summary-label">Original</div><div class="summary-value">${title}</div></div>
              <div class="summary-box"><div class="summary-label">Normalisiert</div><div class="summary-value">${norm}</div></div>
              <div class="summary-box"><div class="summary-label">Substanz S</div><div class="summary-value">${fmtNum(w.substance)}</div></div>
              <div class="summary-box"><div class="summary-label">Index I</div><div class="summary-value">${fmtNum(w.perm_index)}</div></div>
            </div>
            <div class="panel-actions">
              <button type="button" class="btn btn-secondary btn-copy-si" data-s="${w.substance}" data-i="${w.perm_index}">S & I zum Decodieren</button>
              <button type="button" class="btn btn-secondary btn-size-word" data-word-index="${i}">Speichergröße vergleichen</button>
            </div>
            <div class="size-result hidden"></div>
            <ul class="step-list">${renderSteps(w.steps, 'encode')}</ul>
          </div>
        </details>`;
    }).join('');

    showResult(el, meta + `<div class="word-accordion">${panels}</div>`);
    if (data.db_total != null) {
      const totalEl = document.getElementById('db-total-count');
      if (totalEl) totalEl.textContent = String(data.db_total);
    }
    refreshDbStats();

    el.querySelectorAll('.btn-copy-si').forEach((btn) => {
      btn.addEventListener('click', () => {
        document.getElementById('decode-s').value = btn.dataset.s;
        document.getElementById('decode-i').value = btn.dataset.i;
        document.querySelector('[data-tab="decodieren"]').click();
      });
    });
    wireEncodeSizeButtons(el);
  } catch {
    showError(el, 'Netzwerkfehler.');
  }
});

/* Decodieren */
document.getElementById('decode-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const el = document.getElementById('decode-result');
  showLoading(el, 'Decodiere…');
  try {
    const res = await fetch(appUrl('/api/decode'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        substance: document.getElementById('decode-s').value,
        perm_index: document.getElementById('decode-i').value,
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      showError(el, data.error || 'Fehler beim Decodieren.');
      return;
    }
    const ing = fmtLetters(data.ingredients);
    showResult(el, `
      <div class="result-summary">
        <div class="summary-box"><div class="summary-label">Substanz S</div><div class="summary-value">${fmtNum(data.substance)}</div></div>
        <div class="summary-box"><div class="summary-label">Index I</div><div class="summary-value">${fmtNum(data.perm_index)}</div></div>
        <div class="summary-box"><div class="summary-label">Zutaten</div><div class="summary-value">${ing}</div></div>
        <div class="summary-box"><div class="summary-label">Wort</div><div class="summary-value">${escapeHtml(data.word)}</div></div>
      </div>
      <div class="panel-actions">
        <button type="button" class="btn btn-secondary" id="decode-size-btn">Speichergröße vergleichen</button>
      </div>
      <div id="decode-size-result" class="size-result hidden"></div>
      <ul class="step-list">${renderSteps(data.steps, 'decode')}</ul>
    `);
    wireDecodeSizeButton(el, {
      substance: data.substance,
      perm_index: data.perm_index,
      word: data.word,
    });
  } catch {
    showError(el, 'Netzwerkfehler.');
  }
});

/* Wortpaar, Vergleichen & Differenz */
document.getElementById('wortpaar-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const word1 = document.getElementById('word1')?.value || '';
  const word2 = document.getElementById('word2')?.value || '';
  const compareEl = document.getElementById('compare-result');
  const diffEl = document.getElementById('diff-result');
  compareEl?.classList.add('hidden');
  diffEl?.classList.add('hidden');

  if (getPairMode() === 'compare') {
    showLoading(compareEl, 'Vergleiche…');
    try {
      const res = await fetch(appUrl('/api/compare'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ word1, word2 }),
      });
      const data = await res.json();
      if (!res.ok) {
        showError(compareEl, data.error || 'Fehler beim Vergleich.');
        return;
      }
      const c = data.comparison;
      const notes = (c.notes || []).map((n) => `<li>${escapeHtml(n)}</li>`).join('');
      const simPct = (c.similarity_ratio * 100).toFixed(2).replace('.', ',');
      showResult(compareEl, `
        <div class="compare-result">
          <div class="grid-2 compare-words">
            <div class="summary-box compare-word-box">
              <div class="summary-label">${escapeHtml(data.word1.display || data.word1.original)}</div>
              <div class="summary-value compare-norm mono">${escapeHtml(data.word1.normalized)}</div>
              <div class="compare-si">S = ${fmtNum(data.word1.substance)} · I = ${fmtNum(data.word1.perm_index)}</div>
            </div>
            <div class="summary-box compare-word-box">
              <div class="summary-label">${escapeHtml(data.word2.display || data.word2.original)}</div>
              <div class="summary-value compare-norm mono">${escapeHtml(data.word2.normalized)}</div>
              <div class="compare-si">S = ${fmtNum(data.word2.substance)} · I = ${fmtNum(data.word2.perm_index)}</div>
            </div>
          </div>
          <div class="compare-match-grid">
            <div class="compare-gcd-card">
              <div class="compare-gcd-label">ggT(S₁, S₂)</div>
              <div class="compare-gcd-value mono">${fmtNum(c.gcd_value)}</div>
              <div class="compare-gcd-sim">Ähnlichkeit: <strong>${simPct}&nbsp;%</strong> (ggT ÷ min(S))</div>
              <p class="compare-match-hint muted">Schnittmenge, gemeinsame Buchstaben</p>
            </div>
            <div class="compare-lcm-card">
              <div class="compare-gcd-label">kgV(S₁, S₂)</div>
              <div class="compare-gcd-value mono">${fmtNum(c.lcm_value)}</div>
              <p class="compare-match-hint muted">Vereinigung, minimale Substanz für beide Wörter</p>
              <p class="compare-union-letters"><span class="compare-letter-label">Union</span> ${fmtLetters(c.union_letters)}</p>
            </div>
          </div>
          <div class="compare-letters">
            <p><span class="compare-letter-label">Gemeinsam</span> ${fmtLetters(c.shared_letters)}</p>
            <p><span class="compare-letter-label">Nur Wort 1</span> ${fmtLetters(c.unique_to_first)}</p>
            <p><span class="compare-letter-label">Nur Wort 2</span> ${fmtLetters(c.unique_to_second)}</p>
          </div>
          ${notes ? `<ul class="compare-notes">${notes}</ul>` : ''}
        </div>
      `);
    } catch {
      showError(compareEl, 'Netzwerkfehler.');
    }
    return;
  }

  showLoading(diffEl, 'Berechne Differenz…');
  try {
    const res = await fetch(appUrl('/api/diff'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ word1, word2 }),
    });
    const data = await res.json();
    if (!res.ok) {
      showError(diffEl, data.error || 'Fehler bei der Differenz.');
      return;
    }
    const d = data.diff;
    const notes = (d.notes || []).map((n) => `<li>${escapeHtml(n)}</li>`).join('');
    showResult(diffEl, `
      <div class="diff-result">
        <p class="diff-formula mono muted">S<sub>rest</sub> = S₁ ÷ ggT(S₁, S₂)</p>
        <div class="grid-2 compare-words">
          <div class="summary-box compare-word-box">
            <div class="summary-label">${escapeHtml(data.word1.display || data.word1.original)}</div>
            <div class="summary-value compare-norm mono">${escapeHtml(data.word1.normalized)}</div>
            <div class="compare-si">S = ${fmtNum(data.word1.substance)} · I = ${fmtNum(data.word1.perm_index)}</div>
          </div>
          <div class="summary-box compare-word-box">
            <div class="summary-label">${escapeHtml(data.word2.display || data.word2.original)}</div>
            <div class="summary-value compare-norm mono">${escapeHtml(data.word2.normalized)}</div>
            <div class="compare-si">S = ${fmtNum(data.word2.substance)} · I = ${fmtNum(data.word2.perm_index)}</div>
          </div>
        </div>
        <p class="muted">ggT(S₁, S₂) = <span class="mono">${fmtNum(d.gcd_value)}</span></p>
        <div class="compare-match-grid">
          <div class="diff-rest-card">
            <div class="compare-gcd-label">S<sub>rest</sub> (Wort 1)</div>
            <div class="compare-gcd-value mono">${fmtNum(d.remainder_s1)}</div>
            <p class="compare-union-letters"><span class="compare-letter-label">Rest</span> ${fmtLetters(d.remainder_letters_s1)}</p>
            <p class="diff-badges">${diffBadge(d.is_subset_1_in_2, 'Teilmenge von Wort 2')}</p>
          </div>
          <div class="diff-rest-card">
            <div class="compare-gcd-label">S<sub>rest</sub> (Wort 2)</div>
            <div class="compare-gcd-value mono">${fmtNum(d.remainder_s2)}</div>
            <p class="compare-union-letters"><span class="compare-letter-label">Rest</span> ${fmtLetters(d.remainder_letters_s2)}</p>
            <p class="diff-badges">${diffBadge(d.is_subset_2_in_1, 'Teilmenge von Wort 1')}</p>
          </div>
        </div>
        <div class="diff-classify">
          ${diffBadge(d.is_same_substance, 'Gleiche Substanz S')}
          ${diffBadge(d.is_anagram, 'Anagramm')}
          ${diffBadge(d.is_identical, 'Identisch (S und I)')}
          ${d.same_length != null ? diffBadge(d.same_length, 'Gleiche Länge') : ''}
        </div>
        ${notes ? `<ul class="compare-notes">${notes}</ul>` : ''}
      </div>
    `);
  } catch {
    showError(diffEl, 'Netzwerkfehler.');
  }
});

function diffBadge(active, label) {
  const cls = active ? 'diff-badge diff-badge-yes' : 'diff-badge';
  return `<span class="${cls}">${escapeHtml(label)}: ${active ? 'ja' : 'nein'}</span>`;
}

/* .gpm Datei */
let gpmPlainBase64 = null;
let gpmLastReconstructedText = '';
let gpmPendingReadFile = null;
let gpmReadNeedsKeys = false;
const ikurveSideGpm = { a: null, b: null };
const ikurveIngestText = { a: '', b: '' };

function normalizeTextNfc(text) {
  return String(text ?? '')
    .normalize('NFC')
    .replace(/\r\n/g, '\n')
    .replace(/\r/g, '\n');
}

function mapCharPosThroughCrlfCollapse(raw, pos) {
  let normalizedIndex = 0;
  let rawIndex = 0;
  while (rawIndex < pos && rawIndex < raw.length) {
    if (raw[rawIndex] === '\r' && raw[rawIndex + 1] === '\n') {
      rawIndex += 2;
      normalizedIndex += 1;
      continue;
    }
    if (raw[rawIndex] === '\r') {
      rawIndex += 1;
      normalizedIndex += 1;
      continue;
    }
    rawIndex += 1;
    normalizedIndex += 1;
  }
  return normalizedIndex;
}

function syncEditorNormalizedText(editor) {
  if (!editor) return normalizeTextNfc('');
  const raw = editor.value ?? '';
  const normalized = normalizeTextNfc(raw);
  if (normalized === raw) return normalized;
  const selStart = editor.selectionStart ?? 0;
  const selEnd = editor.selectionEnd ?? selStart;
  editor.value = normalized;
  editor.selectionStart = mapCharPosThroughCrlfCollapse(raw, selStart);
  editor.selectionEnd = mapCharPosThroughCrlfCollapse(raw, selEnd);
  return normalized;
}

let ikurveSpectroAbort = null;
let ikurveSpectroGeneration = 0;
let gpmSpectroAbort = null;
let gpmSpectroGeneration = 0;

function abortIcurveSpectroHttp() {
  ikurveSpectroAbort?.abort();
  ikurveSpectroAbort = null;
}

function invalidateIcurveSpectroGeneration() {
  ikurveSpectroGeneration += 1;
}

function abortIcurveSpectroscope() {
  abortIcurveSpectroHttp();
  invalidateIcurveSpectroGeneration();
}

function abortGpmSpectroHttp() {
  gpmSpectroAbort?.abort();
  gpmSpectroAbort = null;
}

function invalidateGpmSpectroGeneration() {
  gpmSpectroGeneration += 1;
}

function abortGpmSpectroscope() {
  abortGpmSpectroHttp();
  invalidateGpmSpectroGeneration();
}
window.ikurveGpmCache = { a: null, b: null };

const CIPHER_MODE_META = {
  word: { label: 'Schlüssel (Wort)', placeholder: 'z. B. GEHEIM', hardcore: false },
  prime: { label: 'Schlüssel (Primzahl)', placeholder: 'z. B. prime:17 oder prime:103', hardcore: false },
  si: { label: 'Schlüssel (Wort)', placeholder: 'Längeres Wort erhöht die S+I-Trennung', hardcore: false },
  hardcore: {
    label: 'Schlüssel (kommagetrennt)',
    placeholder: 'GEHEIM, prime:17, ALPHA, prime:103',
    hardcore: true,
  },
};

function getRadioMode(radioName) {
  return document.querySelector(`input[name="${radioName}"]:checked`)?.value || 'word';
}

function refreshCipherPanel({
  radioName,
  captionId,
  keyId,
  hintId,
  submitBtnId = null,
  previewId = null,
  directionRadioName = null,
  compileBtnSelector = null,
  encryptEnabled = null,
}) {
  const mode = getRadioMode(radioName);
  const meta = CIPHER_MODE_META[mode] || CIPHER_MODE_META.word;
  const caption = captionId ? document.getElementById(captionId) : null;
  const keyInput = keyId ? document.getElementById(keyId) : null;
  const hint = hintId ? document.getElementById(hintId) : null;
  if (caption) caption.textContent = meta.label;
  if (keyInput) keyInput.placeholder = meta.placeholder;
  hint?.classList.toggle('hidden', !meta.hardcore);

  if (submitBtnId) {
    const submitBtn = document.getElementById(submitBtnId);
    if (submitBtn && directionRadioName) {
      const direction = document.querySelector(`input[name="${directionRadioName}"]:checked`)?.value || 'encrypt';
      submitBtn.textContent = direction === 'decrypt' ? 'Entschlüsseln' : 'Verschlüsseln';
    }
  }

  if (previewId) {
    const preview = document.getElementById(previewId);
    if (preview) {
      const opt = document.querySelector(`input[name="${radioName}"][value="${mode}"]`);
      const badge = opt?.closest('.cipher-mode-option')?.querySelector('.cipher-security');
      const score = badge?.dataset.score || '32';
      const level = badge?.textContent?.replace('Sicherheit: ', '') || 'niedrig';
      preview.innerHTML = `<p class="muted">Voraussichtliche Sicherheit (${mode}): <strong>${escapeHtml(level.trim())}</strong> · Basis-Score ${escapeHtml(score)}/100</p>`;
    }
  }

  if (compileBtnSelector != null) {
    const compileBtn = document.querySelector(compileBtnSelector);
    if (compileBtn) {
      const enabled = encryptEnabled == null
        ? document.getElementById('gpm-encrypt-enable')?.checked
        : encryptEnabled;
      compileBtn.textContent = enabled ? 'Verschlüsselt als .gpm kompilieren' : 'In .gpm kompilieren';
    }
  }
}

function getGpmCipherMode() {
  return getRadioMode('gpm-cipher-mode');
}

function refreshGpmEncryptPanel() {
  const enabled = document.getElementById('gpm-encrypt-enable')?.checked;
  document.getElementById('gpm-encrypt-panel')?.classList.toggle('hidden', !enabled);
  refreshCipherPanel({
    radioName: 'gpm-cipher-mode',
    captionId: 'gpm-cipher-key-caption',
    keyId: 'gpm-cipher-key',
    hintId: 'gpm-cipher-hardcore-hint',
    compileBtnSelector: '#gpm-compile-form .btn-editor-primary',
    encryptEnabled: enabled,
  });
}

document.getElementById('gpm-encrypt-enable')?.addEventListener('change', refreshGpmEncryptPanel);
document.querySelectorAll('input[name="gpm-cipher-mode"]').forEach((el) => {
  el.addEventListener('change', refreshGpmEncryptPanel);
});
refreshGpmEncryptPanel();

function showGpmDecryptPanel(show, { mode = '' } = {}) {
  const panel = document.getElementById('gpm-decrypt-panel');
  const hint = document.getElementById('gpm-read-cipher-mode-hint');
  panel?.classList.toggle('hidden', !show);
  gpmReadNeedsKeys = show;
  if (hint && show && mode) {
    hint.textContent = `Cipher-Modus in Datei: ${mode}`;
  } else if (hint) {
    hint.textContent = '';
  }
}

function renderEncryptedGpmBadge(security, mode) {
  return `<p class="gpm-encrypted-badge">🔒 Verschlüsselte .gpm (GPC) · Modus ${escapeHtml(mode)}${security ? ` · Sicherheit ${escapeHtml(security.level)}` : ''}</p>`;
}

function base64ToBlob(base64, mime = 'application/octet-stream') {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  return new Blob([bytes], { type: mime });
}

function arrayBufferToBase64(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) {
    binary += String.fromCharCode.apply(null, bytes.subarray(i, i + chunk));
  }
  return btoa(binary);
}

function isEncryptedGpmBytes(bytes) {
  return bytes.length >= 3 && bytes[0] === 0x47 && bytes[1] === 0x50 && bytes[2] === 0x43;
}

function setGpmPlainBase64(base64) {
  gpmPlainBase64 = base64 || null;
  updateIcurveGpmUi();
}

function resolveIcurveGpmFile(side) {
  const sideGpm = ikurveSideGpm[side];
  if (sideGpm?.file) {
    return {
      file: sideGpm.file,
      name: sideGpm.name || sideGpm.file.name || 'document.gpm',
    };
  }
  if (gpmPlainBase64) {
    return { file: base64ToBlob(gpmPlainBase64), name: 'workspace.gpm' };
  }
  return null;
}

function updateIcurveGpmUi() {
  const hasShared = Boolean(gpmPlainBase64);
  const workspace = document.getElementById('ikurve-gpm-workspace-status');
  if (workspace) {
    workspace.textContent = hasShared
      ? 'GPM-Arbeitskopie geladen, eigene .gpm pro Seite ablegen oder ohne eigene Datei die Arbeitskopie nutzen.'
      : 'Optional: .gpm pro Seite per Drag-and-Drop, oder im Tab GPM Datei kompilieren/lesen.';
  }
  ['a', 'b'].forEach((side) => {
    const sideGpm = ikurveSideGpm[side];
    const hasSide = Boolean(sideGpm?.file);
    const drop = document.getElementById(`ikurve-gpm-drop-${side}`);
    const status = document.getElementById(`ikurve-gpm-status-${side}`);
    const sharedHint = document.getElementById(`ikurve-gpm-shared-hint-${side}`);
    const gpmSelected = document.querySelector(`input[name="ikurve-source-${side}"]:checked`)?.value === 'gpm';
    drop?.classList.toggle('hidden', !gpmSelected);
    if (status) {
      if (hasSide) {
        status.textContent = sideGpm.name;
        status.classList.add('ready');
      } else if (gpmSelected && hasShared) {
        status.textContent = 'Arbeitskopie aus GPM-Tab';
        status.classList.add('ready');
      } else {
        status.textContent = gpmSelected ? 'Datei ablegen oder klicken' : 'Noch keine Datei';
        status.classList.remove('ready');
      }
    }
    if (sharedHint) {
      if (gpmSelected && !hasSide && hasShared) {
        sharedHint.textContent = 'Nutzt die geladene .gpm aus dem Tab GPM Datei.';
        sharedHint.classList.remove('hidden');
      } else {
        sharedHint.classList.add('hidden');
      }
    }
    const textRow = document.querySelector(`.ikurve-ingest-text-${side}`);
    textRow?.classList.toggle('hidden', gpmSelected);
  });
}

function getIcurveIngestText(side) {
  const stored = ikurveIngestText[side];
  if (stored) return stored.trim();
  return document.getElementById(`ikurve-ingest-${side}`)?.value?.trim() || '';
}

function setIcurveIngestText(side, text) {
  ikurveIngestText[side] = normalizeTextNfc(text || '');
  const input = document.getElementById(`ikurve-ingest-${side}`);
  if (input) {
    const len = ikurveIngestText[side].length;
    input.value = len > 120 ? `${ikurveIngestText[side].slice(0, 117)}…` : ikurveIngestText[side];
    input.placeholder = len > 120 ? `${len} Zeichen geladen` : input.placeholder;
  }
}

function isIcurveIngestLocked() {
  return document.getElementById('ikurve-ingest-root')?.classList.contains('ikurve-ingest-locked');
}

function lockIcurveIngest() {
  const root = document.getElementById('ikurve-ingest-root');
  if (!root) return;
  root.classList.add('ikurve-ingest-locked');
  document.getElementById('ikurve-ingest-lock-banner')?.classList.remove('hidden');
  root.querySelectorAll('input, select, textarea, button:not(.ikurve-reset-btn)').forEach((el) => {
    el.disabled = true;
  });
  root.querySelectorAll('.ikurve-gpm-drop').forEach((el) => {
    el.tabIndex = -1;
    el.setAttribute('aria-disabled', 'true');
  });
  document.getElementById('ikurve-reset-btn')?.classList.remove('hidden');
  document.getElementById('ikurve-matrix-root')?.classList.remove('hidden');
}

function unlockIcurveIngest() {
  abortIcurveSpectroscope();
  const root = document.getElementById('ikurve-ingest-root');
  if (!root) return;
  root.classList.remove('ikurve-ingest-locked');
  document.getElementById('ikurve-ingest-lock-banner')?.classList.add('hidden');
  root.querySelectorAll('input, select, textarea, button:not(.ikurve-reset-btn)').forEach((el) => {
    el.disabled = false;
  });
  root.querySelectorAll('.ikurve-gpm-drop').forEach((el) => {
    el.tabIndex = 0;
    el.removeAttribute('aria-disabled');
  });
  document.getElementById('ikurve-reset-btn')?.classList.add('hidden');
  document.getElementById('ikurve-matrix-root')?.classList.add('hidden');
  window.ikurveGpmCache = { a: null, b: null };
  window.currentAnalysis = null;
  ['a', 'b'].forEach((side) => {
    window.GeometricMatrix?.clear(`ikurve-geometric-matrix-${side}`);
    const panel = document.getElementById(`ikurve-spectro-result-${side}`);
    if (panel) {
      panel.classList.add('hidden');
      panel.textContent = '';
    }
  });
  const resultEl = document.getElementById('ikurve-result');
  if (resultEl) {
    resultEl.classList.add('hidden');
    resultEl.innerHTML = '';
  }
}

async function loadIcurveSideGpmFile(file, side) {
  if (!file) return;
  const buf = await file.arrayBuffer();
  const bytes = new Uint8Array(buf);
  if (isEncryptedGpmBytes(bytes)) {
    throw new Error(
      'Verschlüsselte .gpm, im Tab GPM Datei mit Schlüssel lesen oder eine unverschlüsselte .gpm hier ablegen.'
    );
  }
  ikurveSideGpm[side] = {
    file,
    name: file.name || 'document.gpm',
  };
  const gpmRadio = document.getElementById(`ikurve-source-${side}-gpm`);
  if (gpmRadio) gpmRadio.checked = true;
  updateIcurveGpmUi();
}

function buildIcurveFormData() {
  const form = new FormData();
  ['a', 'b'].forEach((side) => {
    const source = document.querySelector(`input[name="ikurve-source-${side}"]:checked`)?.value || 'text';
    const text = getIcurveIngestText(side);
    form.append(`source_${side}`, source);
    form.append(`text_${side}`, text);
    if (source === 'gpm') {
      const gpm = resolveIcurveGpmFile(side);
      if (!gpm?.file) {
        throw new Error(
          `Seite ${side.toUpperCase()}: .gpm ablegen (Drag-and-Drop) oder im Tab GPM Datei kompilieren/lesen.`,
        );
      }
      form.append(`file_${side}`, gpm.file, gpm.name);
    }
  });
  form.append('db_audit_mode', document.getElementById('ikurve-db-audit-mode')?.value || 'de_en');
  return form;
}

const SPARKLINE_VIEWBOX_W = 480;

function resolveSparklineEnd(points, indexKey, pointCount = null) {
  if (pointCount != null && pointCount > 0) return pointCount - 1;
  if (!points?.length) return 0;
  return points.reduce((max, p) => Math.max(max, p[indexKey] ?? 0), 0);
}

function sparklineExtent(points, indexKey) {
  return resolveSparklineEnd(points, indexKey, null);
}

function computePairedChartLayout(endA, endB, chartScale, spanA = 0, spanB = 0) {
  const safeMax = (end) => Math.max(end, 1);
  const unionLayout = (maxIndex) => ({
    a: { maxIndex: safeMax(maxIndex), scrollable: false, widthRatio: 1 },
    b: { maxIndex: safeMax(maxIndex), scrollable: false, widthRatio: 1 },
  });
  if (spanA <= 0 && spanB <= 0) {
    return unionLayout(1);
  }
  if (chartScale === 'shorter' && spanA > 0 && spanB > 0 && spanA !== spanB) {
    const widthRatio = Math.max(spanA, spanB) / Math.min(spanA, spanB);
    if (spanA < spanB) {
      return {
        a: { maxIndex: safeMax(endA), scrollable: false, widthRatio: 1 },
        b: { maxIndex: safeMax(endB), scrollable: true, widthRatio },
      };
    }
    return {
      a: { maxIndex: safeMax(endA), scrollable: true, widthRatio },
      b: { maxIndex: safeMax(endB), scrollable: false, widthRatio: 1 },
    };
  }
  return unionLayout(Math.max(endA, endB, 1));
}

function renderIcurveSparkline(points, strokeClass, { valueKey = 'i_ratio', indexKey = 'position', maxIndex = null, widthRatio = 1 } = {}) {
  if (!points?.length) {
    return '<p class="muted">Keine Kurvenpunkte.</p>';
  }
  const viewBoxW = SPARKLINE_VIEWBOX_W * widthRatio;
  const height = 90;
  const pad = 6;
  const lastIndex = points[points.length - 1][indexKey] ?? 0;
  const maxX = Math.max(maxIndex != null ? maxIndex : lastIndex, 1);
  const toXY = (p) => {
    const x = pad + ((p[indexKey] ?? 0) / maxX) * (viewBoxW - 2 * pad);
    const val = Math.max(p[valueKey] ?? 0, 0);
    const y = height - pad - val * (height - 2 * pad);
    return { x, y };
  };
  const extendedClass = widthRatio > 1 ? ' ikurve-sparkline--extended' : '';
  const styleAttr = widthRatio > 1
    ? ` style="width:${(widthRatio * 100).toFixed(4)}%;min-width:100%;"`
    : '';
  if (points.length === 1) {
    const val = Math.max(points[0][valueKey] ?? 0, 0);
    const y = height - pad - val * (height - 2 * pad);
    return `<svg class="ikurve-sparkline${extendedClass} ${strokeClass}"${styleAttr} viewBox="0 0 ${viewBoxW} ${height}" preserveAspectRatio="none" aria-hidden="true"><line x1="${pad}" y1="${y.toFixed(1)}" x2="${(viewBoxW - pad).toFixed(1)}" y2="${y.toFixed(1)}" stroke="currentColor" stroke-width="1.5"/></svg>`;
  }
  const poly = points
    .map((p) => {
      const { x, y } = toXY(p);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(' ');
  return `<svg class="ikurve-sparkline${extendedClass} ${strokeClass}"${styleAttr} viewBox="0 0 ${viewBoxW} ${height}" preserveAspectRatio="none" aria-hidden="true"><polyline fill="none" stroke="currentColor" stroke-width="1.5" points="${poly}"/></svg>`;
}

function renderPairedSparklines(pointsA, pointsB, strokeA, strokeB, opts = {}) {
  const {
    valueKey = 'i_ratio',
    indexKey = 'position',
    labelA = 'Kurve A',
    labelB = 'Kurve B',
    chartScale = 'union',
    pointCountA = null,
    pointCountB = null,
    levelLabel = 'Knoten',
    pairIndex = 0,
  } = opts;
  const endA = resolveSparklineEnd(pointsA, indexKey, pointCountA);
  const endB = resolveSparklineEnd(pointsB, indexKey, pointCountB);
  const spanA = pointCountA ?? pointsA?.length ?? 0;
  const spanB = pointCountB ?? pointsB?.length ?? 0;
  const layout = computePairedChartLayout(endA, endB, chartScale, spanA, spanB);

  const emptyCell = (side, label, pointCount) => {
    const count = pointCount ?? 0;
    return `<div class="ikurve-chart-cell" data-ikurve-side="${side}" data-ikurve-pair="${pairIndex}"><span class="ikurve-chart-label">${escapeHtml(label)}</span><p class="muted">Keine ${escapeHtml(levelLabel)}-Knoten (${fmtNum(count)}).</p></div>`;
  };

  const chartCell = (side, label, points, stroke, cellLayout, pointCount) => {
    if (!points?.length) {
      return emptyCell(side, label, pointCount);
    }
    const svg = renderIcurveSparkline(points, stroke, {
      valueKey,
      indexKey,
      maxIndex: cellLayout.maxIndex,
      widthRatio: cellLayout.widthRatio,
    });
    const scrollWrap = cellLayout.scrollable
      ? `<div class="ikurve-sparkline-scroll" data-ikurve-scroll="long" data-ikurve-side="${side}" data-ikurve-pair="${pairIndex}" tabindex="0" aria-label="Längere Kurve, horizontal scrollen">${svg}</div>`
      : svg;
    const hint = cellLayout.scrollable
      ? '<span class="ikurve-scroll-hint muted">Längere Kurve, horizontal scrollen</span>'
      : '';
    return `<div class="ikurve-chart-cell" data-ikurve-side="${side}" data-ikurve-pair="${pairIndex}"><span class="ikurve-chart-label">${escapeHtml(label)}</span>${scrollWrap}${hint}</div>`;
  };

  const cellA = chartCell('a', labelA, pointsA, strokeA, layout.a, pointCountA);
  const cellB = chartCell('b', labelB, pointsB, strokeB, layout.b, pointCountB);

  return `<div class="ikurve-charts"><div class="ikurve-chart-pair" data-ikurve-pair="${pairIndex}">${cellA}${cellB}</div></div>`;
}

function renderCellSparkline(points, strokeClass, maxIndex = null) {
  return renderIcurveSparkline(points, strokeClass, { valueKey: 'i_satz_ratio', indexKey: 'cell_index', maxIndex });
}

function fmtPct(ratio) {
  return `${(Number(ratio) * 100).toFixed(1).replace('.', ',')}\u00a0%`;
}

function renderMetaGenomeCard(side, meta) {
  if (!meta) return '';
  const lang = meta.language || {};
  const dom = meta.domain || {};
  const top = (meta.top_words || [])
    .slice(0, 5)
    .map((w) => `${escapeHtml(w.word)} (${fmtNum(w.count)})`)
    .join(', ');
  const langMethod = lang.method && lang.method !== 'patterns'
    ? ` · ${escapeHtml(lang.method)}`
    : '';
  const domConf = dom.confidence != null ? ` (${fmtPct(dom.confidence)})` : '';
  const domFallback = dom.fallback ? ' · unsicher → Allgemein' : '';
  const domKeywords = (dom.matched_keywords || []).length
    ? `<p class="muted meta-domain-keywords">Treffer: ${dom.matched_keywords.map((k) => escapeHtml(k)).join(', ')}</p>`
    : '';
  return `<div class="meta-genome-card">
    <h4>Meta-Genom ${escapeHtml(side)}</h4>
    <p><span class="compare-letter-label">Sprache</span> ${escapeHtml(lang.label || '?')} (${fmtPct(lang.confidence || 0)})${lang.has_eszett ? ' · ß-Signal' : ''}${langMethod}</p>
    <p><span class="compare-letter-label">Domäne</span> ${escapeHtml(dom.label || '?')}${domConf}${domFallback}</p>
    ${domKeywords}
    <p><span class="compare-letter-label">V</span> ${fmtNum(meta.vector_bits || 0)} Bit · ${fmtNum(meta.prime_factor_count || 0)} Primfaktoren · ${fmtNum(meta.token_count || 0)} Token</p>
    ${top ? `<p class="muted meta-top-words">Top: ${top}</p>` : ''}
  </div>`;
}

function scoreBarClass(score) {
  const s = Number(score) || 0;
  if (s >= 0.75) return 'ikurve-score-high';
  if (s >= 0.45) return 'ikurve-score-mid';
  return 'ikurve-score-low';
}

function renderWordGeometryBadges(c, p) {
  const badges = [];
  if (c?.fester_offset_erkannt || p?.fester_offset_erkannt) {
    badges.push('<span class="ikurve-geo-badge ikurve-badge-offset">Fester Offset</span>');
  }
  if (c?.elastische_streckung || p?.elastische_streckung) {
    badges.push('<span class="ikurve-geo-badge ikurve-badge-stretch">Elastische Streckung</span>');
  }
  if (c?.hybride_modifikation || p?.hybride_modifikation) {
    badges.push('<span class="ikurve-geo-badge ikurve-badge-hybrid">Teilweise Paraphrase</span>');
  }
  if (!badges.length) return '';
  return `<div class="ikurve-geo-badges" role="group" aria-label="Wort-Geometrie-Diagnose">${badges.join('')}</div>`;
}

function renderSignalOverview(p, c, cellCmp, substCmp, relCmp) {
  const segments = [
    { label: 'Wort-Geometrie (DTW)', score: c.geometry_score ?? 0 },
    { label: 'Substanz-ggT (Log)', score: substCmp.geometry_score ?? p.substance_score ?? 0 },
    { label: 'Zelle / Zeile', score: cellCmp.geometry_score ?? p.cell_score ?? 0 },
    { label: 'Relation (Topologie)', score: relCmp.relation_score ?? p.relation_score ?? 0 },
    { label: 'Meta-ggT', score: p.meta_genome_similarity ?? 0 },
    { label: 'Literal (Byte)', score: c.literal_match_ratio ?? 0 },
  ];
  return `<div class="ikurve-signal-overview" role="group" aria-label="Signal-Übersicht">
    ${segments.map((seg) => `
      <div class="ikurve-signal-segment ${scoreBarClass(seg.score)}">
        <span class="ikurve-signal-label">${escapeHtml(seg.label)}</span>
        <span class="ikurve-signal-value">${fmtPct(seg.score)}</span>
        <span class="ikurve-signal-bar"><span style="width:${Math.round(seg.score * 100)}%"></span></span>
      </div>`).join('')}
  </div>`;
}

function renderDtwFailedWarning(cmp, label) {
  if (!cmp?.dtw_failed) return '';
  return `<p class="ikurve-dtw-failed" role="alert"><strong>${escapeHtml(label)}:</strong> DTW fehlgeschlagen (Fenster-Deadlock oder leere Kurve), 0&nbsp;% ist kein Vergleichswert.</p>`;
}

function renderSubstanceTwinsBanner(p) {
  if (!p?.substance_parallel) return '';
  return `<div class="ikurve-substance-twins-banner" role="status">
    <strong>Substanz-Parallelität</strong>
    <p>Gleiche oder sehr ähnliche Substanz-Kette bei unterschiedlichen Wörtern, Buchstabenstruktur kopiert, Wörter getauscht.</p>
  </div>`;
}

function renderRelationTwinsBanner(p) {
  if (!p?.relation_twins) return '';
  return `<div class="ikurve-relation-twins-banner" role="status">
    <strong>Relations-Zwillinge</strong>
    <p>Geteilte Wort-Bigramme und Beziehungsmuster, typisch für strukturelle Umformulierung mit gleichem Satzbau-Gerüst.</p>
  </div>`;
}

function renderLanguageDbCard(metaA, metaB, p) {
  const langA = metaA?.language || {};
  const langB = metaB?.language || {};
  const dbA = langA.db_coverage || p?.db_coverage_a || {};
  const dbB = langB.db_coverage || p?.db_coverage_b || {};
  const auditMode = p?.db_audit_mode || dbA.db_audit_mode || dbB.db_audit_mode || 'de_en';
  const formatLangHeading = (side, lang, db) => {
    let text = `${side}: ${lang.label || '?'}`;
    if (lang.method && lang.method !== 'patterns') {
      text += ` (${lang.method})`;
    }
    if (db?.language_uncertain && db?.inferred_lang) {
      text += ` · DB-Audit gegen ${String(db.inferred_lang).toUpperCase()}`;
    }
    return text;
  };
  const bar = (db) => {
    if (db.available) {
      const pct = Math.round((db.coverage_ratio || 0) * 100);
      const hint = db.language_uncertain
        ? ' <span class="muted">(Leitsprache aus Score-Tendenz abgeleitet)</span>'
        : '';
      return `<div class="ikurve-db-bar-wrap">
      <div class="ikurve-db-bar"><span style="width:${pct}%"></span></div>
      <span class="muted">${pct}% bestätigt · ${fmtNum(db.confirmed_count)}/${fmtNum(db.unique_tokens)} Token</span>${hint}
    </div>`;
    }
    if (auditMode === 'off' || db.reason === 'audit_off') {
      return '<p class="muted">DB-Sprachaudit deaktiviert (Modus „Aus“).</p>';
    }
    if (db.reason === 'language_unknown') {
      return '<p class="muted">Keine de/en-Tendenz, DB-Abdeckung nicht berechenbar.</p>';
    }
    if (db.reason === 'no_repo') {
      return '<p class="muted">Wort-Datenbank nicht angebunden.</p>';
    }
    return '<p class="muted">DB-Check nicht verfügbar.</p>';
  };
  const mismatches = (db) => (db.foreign_tokens || db.sample_mismatches || []).slice(0, 3)
    .map((row) => (typeof row === 'string' ? escapeHtml(row) : escapeHtml(row.word || row.normalized)))
    .join(', ');
  return `<div class="ikurve-language-db-card">
    <h4>Sprache &amp; DB-Abdeckung (Richtwert)</h4>
    <div class="ikurve-lang-db-grid">
      <div>
        <p><strong>${escapeHtml(formatLangHeading('A', langA, dbA))}</strong></p>
        ${bar(dbA)}
        ${mismatches(dbA) ? `<p class="muted">Abweichende DB-Zuordnung (Beispiele): ${mismatches(dbA)}</p>` : ''}
      </div>
      <div>
        <p><strong>${escapeHtml(formatLangHeading('B', langB, dbB))}</strong></p>
        ${bar(dbB)}
        ${mismatches(dbB) ? `<p class="muted">Abweichende DB-Zuordnung (Beispiele): ${mismatches(dbB)}</p>` : ''}
      </div>
    </div>
    ${p?.mixed_language_suspect ? '<p class="muted ikurve-flag">Mischsignal in der DB-Matrix (≥30 %, Richtwert)</p>' : ''}
    ${p?.db_confirmed ? '<p class="muted ok">DB bestätigt beide Texte in der erkannten Sprache.</p>' : ''}
    <p class="muted ikurve-db-richtwert-note">Reiner Abgleich gegen die hinterlegte Wort-DB, statistischer Richtwert, keine forensische Bewertung.</p>
  </div>`;
}

function renderRelationOverlap(relCmp, metaA, metaB) {
  if (!relCmp) return '';
  const spans = relCmp.shared_bigram_spans || [];
  const legacy = relCmp.shared_word_bigrams || [];
  const rows = spans.length
    ? spans.slice(0, 10).map((s) => [
        `Token ${s.token_start_a}+${s.token_count} / ${s.token_start_b}+${s.token_count}`,
        s.count_a,
        s.count_b,
      ])
    : legacy.slice(0, 10).map((r) => [r.relation, r.count_a, r.count_b]);
  const domA = metaA?.domain?.label || '?';
  const domB = metaB?.domain?.label || '?';
  return `<div class="ikurve-relation-block">
    <h4>Domäne &amp; Beziehungen</h4>
    <p class="muted">${escapeHtml(domA)} / ${escapeHtml(domB)} · Relations-Score ${fmtPct(relCmp.relation_score || 0)}</p>
    <p class="muted">Wort-Bigram ${fmtPct(relCmp.word_bigram_similarity || 0)} · Substanz-Bigram ${fmtPct(relCmp.substance_bigram_similarity || 0)} · Kategorie ${fmtPct(relCmp.category_transition_similarity || 0)}</p>
    ${rows.length ? renderGpmTable(['Bigramm', 'A', 'B'], rows) : '<p class="muted">Keine geteilten Wort-Bigramme.</p>'}
  </div>`;
}

function renderCellTwinsBanner(c) {
  if (!c?.structural_cell_twins) return '';
  return `<div class="ikurve-cell-twins-banner" role="status">
    <strong>Strukturelle Zell-Zwillinge</strong>
    <p>Gleicher Satzbau (Skelett + I_Satz), andere Wörter, typisch für Synonym-Ersatz oder strukturelle Kopie.</p>
  </div>`;
}

function renderValidationPipeline(pipeline) {
  if (!pipeline || !Array.isArray(pipeline.steps)) return '';
  const labels = {
    nfc_tokenization: 'NFC-Normalisierung & Token-Parsing',
    bitmask_prefilter: 'Bitmasken-Vorfilter (_masks_overlap)',
    geometry_curves: 'Geometrische I-Kurven',
    enjambement_phase: 'Enjambement-Phasenanalyse',
    db_matrix_audit: 'Sprach-Datenbank-Matrix',
  };
  const rows = pipeline.steps.map((step) => {
    const status = step.status || 'ok';
    const cls = status === 'warn' ? 'ikurve-pipe-warn' : status === 'skip' ? 'ikurve-pipe-skip' : 'ikurve-pipe-ok';
    let detailHtml = '';
    if (step.id === 'geometry_curves' && step.detail) {
      const lit = step.detail.literal_diagnostics;
      const meta = step.detail.meta_ggt_diagnostics;
      if (lit || meta) {
        const litJson = lit ? escapeHtml(JSON.stringify(lit)) : '';
        const metaJson = meta ? escapeHtml(JSON.stringify(meta)) : '';
        detailHtml = `<details class="ikurve-pipe-detail"><summary class="muted">Metrik-Rohdaten</summary>${lit ? `<pre class="ikurve-pipe-pre">Literal: ${litJson}</pre>` : ''}${meta ? `<pre class="ikurve-pipe-pre">Meta-ggT: ${metaJson}</pre>` : ''}</details>`;
      }
    }
    return `<li class="ikurve-pipe-step ${cls}"><span class="ikurve-pipe-id">${escapeHtml(labels[step.id] || step.id)}</span> <span class="muted">(${escapeHtml(status)})</span>${detailHtml}</li>`;
  }).join('');
  const clsLabel = pipeline.classification ? `<p class="muted">Klassifikation: <strong>${escapeHtml(pipeline.classification)}</strong> · Isomorphie-Index ${fmtPct(pipeline.isomorphism_index ?? 0)}</p>` : '';
  return `<div class="ikurve-validation-pipeline">
    <h4>Validierungs-Pipeline (5 Schritte)</h4>
    <ol class="ikurve-pipe-list">${rows}</ol>
    ${clsLabel}
  </div>`;
}

function renderStructureAssessment(p, c) {
  if (!p) return '';
  const signals = (p.signals || []).map((s) => `<li>${escapeHtml(s)}</li>`).join('');
  const bullets = (p.interpretation_bullets || []).map((b) => `<li>${escapeHtml(b)}</li>`).join('');
  const wordScore = c?.geometry_score ?? p.geometry_score ?? 0;
  const substScore = p.substance_score ?? 0;
  const isoIndex = p.isomorphism_index ?? p.combined_score ?? 0;
  return `<div class="ikurve-alert ikurve-plag-assessment">
    <h4 class="ikurve-plag-head">Struktur-Matrix (Kreuzvalidierung)</h4>
    ${renderWordGeometryBadges(c, p)}
    <div class="ikurve-plag-score-bars">
      <div class="ikurve-plag-score-row ${scoreBarClass(wordScore)}">
        <span class="ikurve-plag-score-label">Wort-Geometrie (DTW)</span>
        <span class="ikurve-plag-score-value">${fmtPct(wordScore)}</span>
        <span class="ikurve-plag-score-bar"><span style="width:${Math.round(wordScore * 100)}%"></span></span>
      </div>
      <div class="ikurve-plag-score-row ${scoreBarClass(substScore)}">
        <span class="ikurve-plag-score-label">Substanz-ggT (Log)</span>
        <span class="ikurve-plag-score-value">${fmtPct(substScore)}</span>
        <span class="ikurve-plag-score-bar"><span style="width:${Math.round(substScore * 100)}%"></span></span>
      </div>
    </div>
    ${bullets ? `<ul class="ikurve-interpret-bullets">${bullets}</ul>` : `<p><strong>${escapeHtml(p.interpretation)}</strong></p>`}
    <div class="compare-match-grid ikurve-metrics meta-metrics">
      <div class="ikurve-metric-card">
        <div class="compare-gcd-label">Isomorphie-Index</div>
        <div class="compare-gcd-value">${fmtPct(isoIndex)}</div>
      </div>
      <div class="ikurve-metric-card">
        <div class="compare-gcd-label">Zelle / Zeile</div>
        <div class="compare-gcd-value">${fmtPct(p.cell_score ?? 0)}</div>
      </div>
      <div class="ikurve-metric-card">
        <div class="compare-gcd-label">Relation</div>
        <div class="compare-gcd-value">${fmtPct(p.relation_score ?? 0)}</div>
      </div>
      <div class="ikurve-metric-card">
        <div class="compare-gcd-label">Meta-ggT</div>
        <div class="compare-gcd-value">${fmtPct(p.meta_genome_similarity)}</div>
      </div>
    </div>
    ${signals ? `<ul class="compare-notes">${signals}</ul>` : ''}
  </div>`;
}

function renderPlagiarismAssessment(p, c) {
  return renderStructureAssessment(p, c);
}

const ICURVE_FETCH_TIMEOUT_MS = 120000;

async function parseJsonResponse(res) {
  const text = await res.text();
  if (!text) return {};
  try {
    return JSON.parse(text);
  } catch {
    throw new Error(`Server-Antwort ungültig (HTTP ${res.status}). Bitte start.bat neu starten.`);
  }
}

function ikurveFetchErrorMessage(err) {
  if (err?.name === 'AbortError') {
    return 'Zeitüberschreitung, Server antwortet nicht rechtzeitig. Text kürzen, DB-Audit auf „Aus“ stellen oder start.bat neu starten.';
  }
  if (err?.message === 'Failed to fetch') {
    return 'Server nicht erreichbar, läuft start.bat? Dann Seite mit Strg+F5 neu laden.';
  }
  return err?.message || 'Netzwerkfehler.';
}

async function runIcurveAnalysis() {
  const el = document.getElementById('ikurve-result');
  const submitBtn = document.querySelector('#ikurve-form button[type="submit"]');
  if (!el) return;

  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.dataset.ikurveBusy = '1';
  }
  showLoading(el, 'Analysiere I-Kurven…');

  try {
    abortIcurveSpectroscope();
    const body = buildIcurveFormData();
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), ICURVE_FETCH_TIMEOUT_MS);
    let res;
    try {
      res = await fetch(appUrl('/api/i-curve'), {
        method: 'POST',
        body,
        signal: controller.signal,
      });
    } finally {
      clearTimeout(timeoutId);
    }

    showLoading(el, 'Ergebnis wird aufbereitet…');
    const data = await parseJsonResponse(res);
    if (!res.ok) {
      showError(el, data.error || 'I-Kurven-Analyse fehlgeschlagen.');
      return;
    }

    window.ikurveGpmCache = {
      a: data.viewport_a?.plain_gpm_base64 || null,
      b: data.viewport_b?.plain_gpm_base64 || null,
    };
    window.currentAnalysis = data;
    window.ikurveViewState = { mode: 'semantic', depth: 'sentence', chartScale: 'union' };

    if (window.GeometricMatrix) {
      window.GeometricMatrix.mount('ikurve-geometric-matrix-a', data.viewport_a);
      window.GeometricMatrix.mount('ikurve-geometric-matrix-b', data.viewport_b);
    }
    lockIcurveIngest();

    await new Promise((resolve) => requestAnimationFrame(resolve));
    if (typeof renderIcurveLab !== 'function') {
      showError(el, 'UI-Modul ikurve_lab.js nicht geladen, Seite mit Strg+F5 neu laden.');
      return;
    }
    renderIcurveLab(data, window.ikurveViewState);
    el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  } catch (err) {
    showError(el, ikurveFetchErrorMessage(err));
  } finally {
    if (submitBtn && !isIcurveIngestLocked()) {
      submitBtn.disabled = false;
      delete submitBtn.dataset.ikurveBusy;
    }
  }
}

document.getElementById('ikurve-form')?.addEventListener('submit', (e) => {
  e.preventDefault();
  void runIcurveAnalysis();
});

updateIcurveGpmUi();

function initDropzone(el, { onFile, dragClass = 'drag-over' } = {}) {
  if (!el || !onFile) return;
  const activate = () => el.classList.add(dragClass);
  const deactivate = () => el.classList.remove(dragClass);
  ['dragenter', 'dragover'].forEach((evt) => {
    el.addEventListener(evt, (e) => {
      e.preventDefault();
      activate();
    });
  });
  ['dragleave', 'drop'].forEach((evt) => {
    el.addEventListener(evt, (e) => {
      e.preventDefault();
      if (evt === 'dragleave' && el.contains(e.relatedTarget)) return;
      deactivate();
    });
  });
  el.addEventListener('drop', (e) => {
    const file = e.dataTransfer?.files?.[0];
    if (file) onFile(file, e);
  });
}

function initIcurveGpmDropzones() {
  ['a', 'b'].forEach((side) => {
    const drop = document.getElementById(`ikurve-gpm-drop-${side}`);
    const fileInput = document.querySelector(`.ikurve-gpm-file-input[data-side="${side}"]`);
    if (!drop) return;

    initDropzone(drop, {
      dragClass: 'drag-over',
      onFile: async (file) => {
        if (isIcurveIngestLocked()) return;
        try {
          await loadIcurveSideGpmFile(file, side);
        } catch (err) {
          showError(document.getElementById('ikurve-result'), err.message || 'Datei konnte nicht geladen werden.');
        }
      },
    });

    drop.addEventListener('click', () => fileInput?.click());
    drop.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        fileInput?.click();
      }
    });
    drop.setAttribute('tabindex', '0');
    drop.setAttribute('role', 'button');

    fileInput?.addEventListener('change', async () => {
      if (isIcurveIngestLocked()) return;
      const file = fileInput.files?.[0];
      if (!file) return;
      try {
        await loadIcurveSideGpmFile(file, side);
      } catch (err) {
        showError(document.getElementById('ikurve-result'), err.message || 'Datei konnte nicht geladen werden.');
      } finally {
        fileInput.value = '';
      }
    });

    document.querySelectorAll(`input[name="ikurve-source-${side}"]`).forEach((radio) => {
      radio.addEventListener('change', updateIcurveGpmUi);
    });
  });
}

initIcurveGpmDropzones();

function getCipherMode() {
  return getRadioMode('cipher-mode');
}

function getCipherDirection() {
  return document.querySelector('input[name="cipher-direction"]:checked')?.value || 'encrypt';
}

function refreshCipherFormUi() {
  refreshCipherPanel({
    radioName: 'cipher-mode',
    captionId: 'cipher-key-caption',
    keyId: 'cipher-key',
    hintId: 'cipher-hardcore-hint',
    submitBtnId: 'cipher-submit-btn',
    previewId: 'cipher-security-preview',
    directionRadioName: 'cipher-direction',
  });
}

document.querySelectorAll('input[name="cipher-mode"], input[name="cipher-direction"]').forEach((el) => {
  el.addEventListener('change', refreshCipherFormUi);
});
refreshCipherFormUi();

function renderCipherSecurity(sec) {
  if (!sec) return '';
  const cls = sec.score >= 65 ? 'cipher-security-high' : sec.score >= 45 ? 'cipher-security-mid' : 'cipher-security-low';
  const warnings = (sec.warnings || []).map((w) => `<li>${escapeHtml(w)}</li>`).join('');
  return `<div class="cipher-security-card ${cls}">
    <div class="cipher-security-head">
      <span class="cipher-security-badge">${escapeHtml(sec.level)}</span>
      <span class="cipher-security-score">Score ${fmtNum(sec.score)}/100 · Vertrauen: ${escapeHtml(sec.confidence)}</span>
    </div>
    <p class="cipher-security-summary">${escapeHtml(sec.summary)}</p>
    ${warnings ? `<ul class="compare-notes cipher-warnings">${warnings}</ul>` : ''}
  </div>`;
}

document.getElementById('cipher-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const el = document.getElementById('cipher-result');
  const text = document.getElementById('cipher-text')?.value || '';
  const keys = document.getElementById('cipher-key')?.value || '';
  const mode = getCipherMode();
  const direction = getCipherDirection();
  const endpoint = direction === 'decrypt' ? appUrl('/api/cipher/decrypt') : appUrl('/api/cipher/encrypt');
  showLoading(el, direction === 'decrypt' ? 'Entschlüssele…' : 'Verschlüssele S(I)-Geometrie…');
  try {
    const body = direction === 'decrypt'
      ? { ciphertext: text.trim(), keys }
      : { text: text.trim(), mode, keys };
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!res.ok) {
      showError(el, data.error || 'Cipher fehlgeschlagen.');
      return;
    }
    const sec = data.security;
    if (direction === 'encrypt') {
      showResult(el, `
        <div class="cipher-result">
          ${renderCipherSecurity(sec)}
          <p><span class="compare-letter-label">Token</span> ${fmtNum(data.token_count)} · Wörter im Genom ${fmtNum(data.unique_words)}</p>
          <label class="full-width">Chiffretext (Base64)
            <textarea id="cipher-output" class="mono cipher-output" rows="5" readonly>${escapeHtml(data.ciphertext)}</textarea>
          </label>
          <button type="button" class="btn btn-secondary btn-copy" data-copy-target="cipher-output">Chiffretext kopieren</button>
          ${data.preview ? `<p class="muted">Vorschau Klartext: ${escapeHtml(data.preview)}${data.preview.length >= 120 ? '…' : ''}</p>` : ''}
        </div>
      `);
    } else {
      showResult(el, `
        <div class="cipher-result">
          ${renderCipherSecurity(sec)}
          <div class="recon-head">
            <h3>Entschlüsselter Text</h3>
            <button type="button" class="btn btn-secondary btn-copy" data-copy-target="cipher-plain-out">Kopieren</button>
          </div>
          <pre id="cipher-plain-out" class="recon-text">${escapeHtml(data.text)}</pre>
        </div>
      `);
    }
    wireCopyButtons(el);
  } catch {
    showError(el, 'Netzwerkfehler.');
  }
});

function isGpmFile(file) {
  if (!file) return false;
  const name = (file.name || '').toLowerCase();
  return name.endsWith('.gpm') || file.type === 'application/octet-stream';
}

function syncGpmReadFileLabel(file) {
  const nameEl = document.getElementById('gpm-read-file-name');
  if (!nameEl) return;
  if (file?.name) {
    nameEl.textContent = file.name;
    nameEl.classList.remove('hidden');
  } else {
    nameEl.textContent = '';
    nameEl.classList.add('hidden');
  }
}

function clearGpmEditorSpectroOverlay() {
  renderSpectroMirror('', [], { editorId: 'gpm-source-text', viewportId: 'gpm-geometric-viewport' });
}

async function ingestGpmFile(file, resultEl) {
  if (!file) return;
  if (!isGpmFile(file)) {
    showError(resultEl || document.getElementById('gpm-read-result'), 'Bitte eine .gpm-Datei wählen.');
    return;
  }
  syncGpmReadFileLabel(file);
  clearGpmEditorSpectroOverlay();
  await runGpmRead(file, resultEl || document.getElementById('gpm-read-result'));
}

function refreshGpmEditorStats(extra = {}) {
  const editor = document.getElementById('gpm-source-text');
  const statsEl = document.getElementById('gpm-editor-stats');
  if (!editor || !statsEl) return;
  const chars = editor.value.length;
  const words = (editor.value.match(/\S+/g) || []).length;
  let text = `${fmtNum(chars)} Zeichen · ${fmtNum(words)} Token`;
  if (extra.zellen != null) {
    text += ` · ${fmtNum(extra.zellen)} Zellen`;
  }
  if (extra.bodyMode) {
    text += ` · ${extra.bodyMode}`;
  }
  statsEl.textContent = text;
}

function openIcurveWithText(text) {
  setIcurveIngestText('a', text || '');
  const textRadio = document.querySelector('input[name="ikurve-source-a"][value="text"]');
  if (textRadio) textRadio.checked = true;
  updateIcurveGpmUi();
  activateTab('ikurve', { historyMode: 'push' });
}

function loadGpmIntoEditor(text, { focus = true } = {}) {
  const editor = document.getElementById('gpm-source-text');
  if (!editor) return;
  editor.value = normalizeTextNfc(text ?? '');
  refreshGpmEditorStats();
  if (focus) {
    editor.focus({ preventScroll: true });
    editor.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}

function downloadBase64File(base64, filename) {
  const bin = atob(base64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i += 1) bytes[i] = bin.charCodeAt(i);
  const blob = new Blob([bytes], { type: 'application/octet-stream' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename || 'document.gpm';
  a.click();
  URL.revokeObjectURL(url);
}

const CASE_LABELS = { 0: 'klein', 1: 'Erster groß', 2: 'GROSS', 3: 'exakt' };

function renderSiStorageStat(stats) {
  const si = stats.si_storage;
  if (!si) return '';
  const ver = si.gpm_version != null ? ` · GPM v${si.gpm_version}` : '';
  return `<div class="gpm-stat gpm-stat-wide">
    <div class="gpm-stat-label">${escapeHtml(si.label || 'Speicher S und I')}</div>
    <div class="gpm-stat-value gpm-stat-value-plain">${escapeHtml(si.summary || '')}${escapeHtml(ver)}</div>
  </div>`;
}

function renderGpmStats(stats, cellGeo) {
  const sepBytes = stats.separator_bytes ?? stats.gap_bytes ?? 0;
  const permLine = stats.separator_perm != null
    ? `<div class="gpm-stat gpm-stat-wide"><div class="gpm-stat-label">Separator-Perm</div><div class="gpm-stat-value"><span class="mono">${stats.separator_perm}</span> · ${escapeHtml(stats.separator_perm_label || 'BASE')}</div></div>`
    : '';
  const zellen = stats.zellen_anzahl ?? cellGeo?.count;
  const bodyMode = stats.body_mode;
  const meanRatio = cellGeo?.summary?.mean_i_satz_ratio;
  const cellStats = zellen != null
    ? `<div class="gpm-stat"><div class="gpm-stat-label">Zellen</div><div class="gpm-stat-value">${fmtNum(zellen)}</div></div>
       <div class="gpm-stat"><div class="gpm-stat-label">Body-Modus</div><div class="gpm-stat-value">${escapeHtml(bodyMode || '—')}</div></div>
       ${meanRatio != null ? `<div class="gpm-stat"><div class="gpm-stat-label">Ø i_satz_ratio</div><div class="gpm-stat-value mono">${meanRatio}</div></div>` : ''}`
    : '';
  return `<div class="gpm-stats">
    <div class="gpm-stat"><div class="gpm-stat-label">Quelle</div><div class="gpm-stat-value">${fmtBytes(stats.source_bytes || 0)}</div></div>
    <div class="gpm-stat"><div class="gpm-stat-label">.gpm Datei</div><div class="gpm-stat-value">${fmtBytes(stats.file_bytes)}</div></div>
    <div class="gpm-stat"><div class="gpm-stat-label">Genom</div><div class="gpm-stat-value">${fmtBytes(stats.header_bytes)}</div></div>
    <div class="gpm-stat"><div class="gpm-stat-label">Geometrie</div><div class="gpm-stat-value">${fmtBytes(stats.body_bytes)}</div></div>
    <div class="gpm-stat"><div class="gpm-stat-label">Separator-Layer</div><div class="gpm-stat-value">${fmtBytes(sepBytes)}</div></div>
    ${permLine}
    ${renderSiStorageStat(stats)}
    ${cellStats}
    <div class="gpm-stat"><div class="gpm-stat-label">Eindeutige Wörter</div><div class="gpm-stat-value">${fmtNum(stats.unique_words)}</div></div>
    <div class="gpm-stat"><div class="gpm-stat-label">Token</div><div class="gpm-stat-value">${fmtNum(stats.total_tokens)}</div></div>
    <div class="gpm-stat"><div class="gpm-stat-label">Größe vs. Text</div><div class="gpm-stat-value">${stats.compression_percent ?? '—'}%</div></div>
  </div>`;
}

function renderCellGeometryBlock(cellGeo, { title = 'Zell-Geometrie' } = {}) {
  if (!cellGeo?.points?.length) {
    return '<p class="muted">Keine Zell-Geometrie (Legacy v4 oder leer).</p>';
  }
  const rows = cellGeo.points.slice(0, 30).map((p) => [
    p.cell_index,
    `[${(p.skeleton || []).join(',')}]`,
    p.perm_index,
    p.i_satz_ratio,
    p.token_count,
    `${p.token_start}-${p.token_start + p.token_count - 1}`,
  ]);
  const trunc = cellGeo.truncated ? '<p class="muted">Tabelle gekürzt, mehr Zellen in der Datei.</p>' : '';
  return `<div class="cell-geometry-block">
    <h3 style="margin-top:1rem">${escapeHtml(title)} (${fmtNum(cellGeo.count)} Zellen)</h3>
    ${trunc}
    ${renderGpmTable(['Zelle', 'Skelett', 'I_Satz', 'i_satz_ratio', 'Token', 'Bereich'], rows)}
  </div>`;
}

function renderLosslessBadge(lossless) {
  if (lossless === true) {
    return '<p class="lossless-badge ok">✓ Exakt rekonstruierbar (verlustfrei)</p>';
  }
  if (lossless === false) {
    return '<p class="lossless-badge warn">⚠ Nicht exakt rekonstruierbar (Legacy v1 oder Sonderfall)</p>';
  }
  return '';
}

let gpmReconCounter = 0;

function renderReconstruction(text, exact) {
  const id = `gpm-recon-${gpmReconCounter += 1}`;
  return `
    <div class="recon-block">
      <div class="recon-head">
        <h3>Rekonstruierter Text${exact ? ' <span class="recon-exact">exakt</span>' : ''}</h3>
        <button type="button" class="btn btn-secondary btn-copy" data-copy-target="${id}">Kopieren</button>
      </div>
      <pre id="${id}" class="recon-text">${escapeHtml(text)}</pre>
    </div>`;
}

function wireCopyButtons(scope) {
  scope.querySelectorAll('.btn-copy').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const target = document.getElementById(btn.dataset.copyTarget);
      if (!target) return;
      try {
        await navigator.clipboard.writeText(target.textContent);
        const old = btn.textContent;
        btn.textContent = 'Kopiert ✓';
        setTimeout(() => { btn.textContent = old; }, 1500);
      } catch {
        btn.textContent = 'Strg+C zum Kopieren';
      }
    });
  });
}

function renderGpmTable(headers, rows) {
  const head = headers.map((h) => `<th>${escapeHtml(h)}</th>`).join('');
  const body = rows.map((row) =>
    `<tr>${row.map((cell, i) => `<td class="${i >= 2 ? 'mono' : ''}">${escapeHtml(String(cell))}</td>`).join('')}</tr>`
  ).join('');
  return `<div class="gpm-table-wrap"><table class="gpm-table"><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
}

async function analyzeGpmFile(file, { cipherKeys = '' } = {}) {
  const form = new FormData();
  form.append('file', file);
  if (cipherKeys) form.append('cipher_keys', cipherKeys);
  const res = await fetch(appUrl('/api/gpm/read'), { method: 'POST', body: form });
  const data = await res.json();
  if (!res.ok) {
    const err = new Error(data.error || 'Lesen fehlgeschlagen.');
    err.encrypted = data.encrypted;
    err.needsKeys = data.needs_keys;
    err.cipherMode = data.cipher_mode;
    throw err;
  }
  return data;
}

function showGpmReadAnalysis(data, el) {
  setGpmPlainBase64(data.file_base64);
  showGpmDecryptPanel(false);
  gpmPendingReadFile = null;
  const a = data.analysis;
  gpmLastReconstructedText = a.reconstructed_text || '';
  loadGpmIntoEditor(gpmLastReconstructedText);

  const stats = {
    source_bytes: 0,
    file_bytes: a.file_bytes,
    header_bytes: a.header_bytes,
    body_bytes: a.body_bytes,
    separator_bytes: a.separator_bytes,
    separator_perm: a.separator_perm,
    separator_perm_label: a.separator_perm_label,
    gap_bytes: a.gap_bytes,
    gpm_version: a.gpm_version ?? a.version,
    si_storage: a.si_storage,
    unique_words: a.unique_words,
    total_tokens: a.total_tokens,
    compression_percent: '—',
    zellen_anzahl: a.zellen_anzahl,
    body_mode: a.body_mode,
  };
  const headerRows = a.header.map((r) => [r.word_id, r.original, r.normalized, r.substance]);
  const bodyRows = a.body_preview.map((r) => [r.position, r.word_id, r.perm_index, r.original]);

  showResult(el, `
    <p class="muted">Format-Version: <strong>v${a.version}</strong></p>
    ${data.encrypted_source ? renderEncryptedGpmBadge(a.cipher_security, a.cipher_mode || '?') + '<p class="muted">Entschlüsselt, im Speicher liegt die normale .gpm für Suche und I-Kurve.</p>' : ''}
    ${renderLosslessBadge(a.lossless)}
    <p class="lossless-badge ok">✓ Rekonstruierter Text im Editor geladen, oben bearbeiten oder neu kompilieren</p>
    <div class="gpm-actions">
      <button type="button" class="btn btn-secondary" id="gpm-reload-editor-btn">Erneut in Editor laden</button>
      <button type="button" class="btn btn-secondary btn-gpm-size">Speichergröße vergleichen</button>
      <button type="button" class="btn btn-secondary" id="gpm-to-ikurve-btn">In I-Kurve vergleichen</button>
    </div>
    <div class="size-result gpm-size-result hidden"></div>
    ${renderGpmStats(stats, a.cell_geometry)}
    ${renderReconstruction(a.reconstructed_text, a.lossless)}
    <h3 style="margin-top:1rem">Genom (${fmtNum(a.unique_words)} Wörter)</h3>
    ${renderGpmTable(['ID', 'Original', 'Normalisiert', 'S'], headerRows)}
    <h3 style="margin-top:1rem">Geometrie-Datenstrom (${fmtNum(a.total_tokens)} Token)</h3>
    ${renderGpmTable(['Pos', 'Word-ID', 'I', 'Wort'], bodyRows)}
    ${renderCellGeometryBlock(a.cell_geometry)}
  `);

  refreshGpmEditorStats({ zellen: a.zellen_anzahl ?? a.cell_geometry?.count, bodyMode: a.body_mode });
  document.getElementById('gpm-to-ikurve-btn')?.addEventListener('click', () => {
    openIcurveWithText(gpmLastReconstructedText);
  });

  document.getElementById('gpm-reload-editor-btn')?.addEventListener('click', () => {
    loadGpmIntoEditor(gpmLastReconstructedText);
  });
  wireCopyButtons(el);
  wireGpmSizeButton(el, {
    source_text: gpmLastReconstructedText,
    file_base64: gpmPlainBase64,
  });
}

async function runGpmRead(file, resultEl) {
  if (!file) {
    showError(resultEl, 'Bitte eine .gpm-Datei wählen.');
    return;
  }
  gpmPendingReadFile = file;
  showLoading(resultEl, 'Analysiere …');
  const cipherKeys = document.getElementById('gpm-read-cipher-key')?.value?.trim() || '';
  try {
    const data = await analyzeGpmFile(file, { cipherKeys });
    showGpmReadAnalysis(data, resultEl);
  } catch (err) {
    if (err.needsKeys || err.encrypted) {
      showGpmDecryptPanel(true, { mode: err.cipherMode || '' });
      showError(resultEl, err.message || 'Schlüssel erforderlich.');
      return;
    }
    showError(resultEl, err.message || 'Netzwerkfehler.');
  }
}

document.getElementById('gpm-compile-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const el = document.getElementById('gpm-compile-result');
  const encrypt = document.getElementById('gpm-encrypt-enable')?.checked;
  const cipherMode = getGpmCipherMode();
  const cipherKeys = document.getElementById('gpm-cipher-key')?.value?.trim() || '';
  if (encrypt && !cipherKeys) {
    showError(el, 'Verschlüsselung: Schlüssel eingeben.');
    return;
  }
  showLoading(el, encrypt ? 'Erzeuge verschlüsselte .gpm …' : 'Kompiliere .gpm …');
  try {
    const res = await fetch(appUrl('/api/gpm/compile'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: syncEditorNormalizedText(document.getElementById('gpm-source-text')),
        encrypt,
        cipher_mode: cipherMode,
        cipher_keys: cipherKeys,
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      showError(el, data.error || 'Kompilieren fehlgeschlagen.');
      return;
    }
    setGpmPlainBase64(data.plain_file_base64 || data.file_base64);
    if (data.encrypted) {
      showResult(el, `
        ${renderEncryptedGpmBadge(data.security, data.cipher_mode)}
        ${renderCipherSecurity(data.security)}
        <p class="muted">${escapeHtml(data.encrypt_note || '')}</p>
        <p class="muted">I-Kurve und Suche nutzen die unverschlüsselte Arbeitskopie im Speicher, Download bleibt verschlüsselt.</p>
        ${renderLosslessBadge(data.lossless)}
        ${renderGpmStats(data.stats, data.cell_geometry)}
        <div class="gpm-actions">
          <button type="button" class="btn" id="gpm-download-btn">Verschlüsselte .gpm herunterladen</button>
          <button type="button" class="btn btn-secondary" id="gpm-to-ikurve-btn">In I-Kurve vergleichen</button>
        </div>
        ${renderReconstruction(data.reconstructed_text, data.lossless)}
        ${renderCellGeometryBlock(data.cell_geometry)}
        <p class="muted">Genom- und Geometrie-Tabellen sind in der Datei verborgen. Zum Lesen Schlüssel im Bereich „Lesen, Analyse“ verwenden.</p>
      `);
      refreshGpmEditorStats({ zellen: data.stats?.zellen_anzahl, bodyMode: data.stats?.body_mode });
      document.getElementById('gpm-to-ikurve-btn')?.addEventListener('click', () => {
        openIcurveWithText(data.reconstructed_text);
      });
    } else {
      const headerRows = data.header_preview.map((r) => [r.word_id, r.original, r.normalized, r.substance]);
      const bodyRows = data.body_preview.map((r) => [r.position, r.word_id, r.perm_index, `${r.word} (${CASE_LABELS[r.case_code] ?? r.case_code})`]);
      showResult(el, `
        ${renderLosslessBadge(data.lossless)}
        ${renderGpmStats(data.stats, data.cell_geometry)}
        <div class="gpm-actions">
          <button type="button" class="btn" id="gpm-download-btn">Als .gpm herunterladen</button>
          <button type="button" class="btn btn-secondary btn-gpm-size">Speichergröße vergleichen</button>
          <button type="button" class="btn btn-secondary" id="gpm-to-ikurve-btn">In I-Kurve vergleichen</button>
        </div>
        <div class="size-result gpm-size-result hidden"></div>
        ${renderReconstruction(data.reconstructed_text, data.lossless)}
        <h3 style="margin-top:1.25rem">Genom (${fmtNum(data.stats.unique_words)} Wörter)</h3>
        ${renderGpmTable(['ID', 'Original', 'Normalisiert', 'S'], headerRows)}
        <h3 style="margin-top:1rem">Geometrie-Datenstrom (${fmtNum(data.stats.total_tokens)} Token)</h3>
        ${renderGpmTable(['Pos', 'Word-ID', 'I', 'Wort (Schreibweise)'], bodyRows)}
        ${renderCellGeometryBlock(data.cell_geometry)}
      `);
      refreshGpmEditorStats({ zellen: data.stats?.zellen_anzahl, bodyMode: data.stats?.body_mode });
      document.getElementById('gpm-to-ikurve-btn')?.addEventListener('click', () => {
        openIcurveWithText(document.getElementById('gpm-source-text')?.value || data.reconstructed_text);
      });
      wireGpmSizeButton(el, {
        source_text: document.getElementById('gpm-source-text').value,
        file_base64: data.file_base64,
      });
    }
    document.getElementById('gpm-download-btn')?.addEventListener('click', () => {
      downloadBase64File(data.file_base64, data.filename);
    });
    wireCopyButtons(el);
  } catch {
    showError(el, 'Netzwerkfehler.');
  }
});

document.getElementById('gpm-read-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const el = document.getElementById('gpm-read-result');
  const fileInput = document.getElementById('gpm-read-file');
  await runGpmRead(fileInput?.files && fileInput.files[0], el);
});

function toggleGpmSearchFields(mode) {
  const wrap = document.getElementById('gpm-search-query2-wrap');
  if (wrap) wrap.classList.toggle('hidden', mode !== 'lcm');
}

document.getElementById('gpm-search-mode')?.addEventListener('change', (e) => {
  toggleGpmSearchFields(e.currentTarget.value);
});
toggleGpmSearchFields(document.getElementById('gpm-search-mode')?.value || 'substance');

document.getElementById('gpm-search-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const el = document.getElementById('gpm-search-result');
  const query = document.getElementById('gpm-search-query').value.trim();
  const query2 = document.getElementById('gpm-search-query2')?.value.trim() || '';
  const mode = document.getElementById('gpm-search-mode').value;
  if (!gpmPlainBase64) {
    showError(el, 'Keine .gpm geladen, zuerst kompilieren oder Datei lesen.');
    return;
  }
  if (!query) {
    showError(el, 'Suchwort eingeben.');
    return;
  }
  if (mode === 'lcm' && !query2) {
    showError(el, 'Für kgV-Filter beide Wörter eingeben.');
    return;
  }
  showLoading(el, 'Suche …');
  try {
    const res = await fetch(appUrl('/api/gpm/search'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_base64: gpmPlainBase64, query, query2, mode }),
    });
    const data = await res.json();
    if (!res.ok) {
      showError(el, data.error || 'Suche fehlgeschlagen.');
      return;
    }
    const r = data.result;
    if (data.mode === 'lcm') {
      const rows = (r.matches || []).map((m) => [
        m.word_id,
        m.original,
        m.substance,
        m.covers_lcm ? 'ja' : 'nein',
      ]);
      showResult(el, `
        <p><strong>kgV-Filter</strong> für „${escapeHtml(r.query)}“ + „${escapeHtml(r.query2)}“</p>
        <p>kgV(S₁, S₂) = <span class="mono">${escapeHtml(String(r.lcm_value))}</span> · Union: ${fmtLetters(r.union_letters)}</p>
        <p>${fmtNum(r.unique_words)} Wörter decken kgV ab · ${fmtNum(r.token_hits)} Token-Treffer</p>
        ${rows.length ? renderGpmTable(['ID', 'Wort', 'S', 'deckt kgV ab'], rows) : '<p class="muted">Kein Genom-Wort enthält die Vereinigungsmenge.</p>'}
      `);
    } else if (data.mode === 'gcd') {
      const rows = (r.matches || []).map((m) => [m.word_id, m.original, m.gcd_value, JSON.stringify(m.shared_letters)]);
      showResult(el, `
        <p><strong>ggT-Filter</strong> für „${escapeHtml(r.query)}“ · S=${escapeHtml(String(r.query_substance))}</p>
        <p>${fmtNum(r.unique_words)} Wörter im Genom · ${fmtNum(r.token_hits)} Token-Treffer</p>
        ${rows.length ? renderGpmTable(['ID', 'Wort', 'ggT', 'Gemeinsam'], rows) : '<p class="muted">Keine stoffliche Überschneidung.</p>'}
      `);
    } else {
      const rows = (r.positions || []).slice(0, 50).map((p) => [p.position, p.word_id, p.perm_index]);
      showResult(el, `
        <p><strong>Substanz-Match</strong> für „${escapeHtml(r.query)}“ → ${escapeHtml(r.query_normalized)} · S=${escapeHtml(String(r.query_substance))}</p>
        <p>Im Genom: ${r.found_in_header ? 'ja' : 'nein'} · ${fmtNum(r.occurrences)} Vorkommen im Body</p>
        ${rows.length ? renderGpmTable(['Position', 'Word-ID', 'I'], rows) : '<p class="muted">Wort nicht im Dokument.</p>'}
      `);
    }
  } catch {
    showError(el, 'Netzwerkfehler.');
  }
});

function tokenSpanToCharRange(tokenCharMap, tokenStart, tokenCount) {
  if (!tokenCharMap?.length || tokenCount <= 0) {
    return { char_start: 0, char_end: 0 };
  }
  const byToken = new Map(tokenCharMap.map((entry) => [entry.token_index, entry]));
  const first = byToken.get(tokenStart);
  const last = byToken.get(tokenStart + tokenCount - 1);
  return {
    char_start: first?.char_start ?? 0,
    char_end: last?.char_end ?? first?.char_end ?? 0,
  };
}

function expandSpectroMatches(matches, tokenCharMap) {
  return (matches || []).map((match) => {
    const tokenStart = match.token_start ?? 0;
    const tokenCount = match.token_count ?? Math.max(1, (match.token_end ?? tokenStart) - tokenStart);
    const range = tokenSpanToCharRange(tokenCharMap, tokenStart, tokenCount);
    return {
      ...match,
      token_start: tokenStart,
      token_end: tokenStart + tokenCount,
      char_start: match.char_start ?? range.char_start,
      char_end: match.char_end ?? range.char_end,
    };
  });
}

function mergeSpectroMatches(matches) {
  const sorted = [...(matches || [])].sort((a, b) => a.char_start - b.char_start || b.char_end - a.char_end);
  const merged = [];

  for (const match of sorted) {
    let existing = merged.find(
      (m) => m.char_start === match.char_start && m.char_end === match.char_end,
    );

    if (existing) {
      if (existing.layer !== match.layer) {
        existing.className = 'spectro-crossfire';
        existing.score_structural = match.score_structural || existing.score_structural;
        existing.score_semantic = match.score_semantic || existing.score_semantic;
      }
    } else {
      match.className =
        match.mode === 'structural_twin' && match.layer === 'structural'
          ? 'spectro-amber-struct'
          : match.mode === 'structural_twin'
            ? 'spectro-amber'
            : 'spectro-teal';
      merged.push(match);
    }
  }
  return merged;
}

function renderSpectroMirror(text, mergedMatches, { editorId = 'gpm-source-text', viewportId = 'gpm-geometric-viewport' } = {}) {
  if (window.GeometricViewport?.renderInto) {
    window.GeometricViewport.renderInto(editorId, viewportId, text, mergedMatches);
    return;
  }
  if (window.GeometricViewport?.render && editorId === 'gpm-source-text') {
    window.GeometricViewport.render(text, mergedMatches);
  }
}

async function runSpectroscopeForEditor({
  editorId,
  viewportId,
  panelId,
  requireTab = null,
} = {}) {
  const editor = document.getElementById(editorId);
  const panel = panelId ? document.getElementById(panelId) : null;
  if (!editor) return;
  if (requireTab && currentTab !== requireTab) return;
  const text = syncEditorNormalizedText(editor);
  if (!text.trim()) {
    abortGpmSpectroscope();
    if (panel) {
      panel.classList.remove('hidden');
      panel.textContent = 'Kein Text, zuerst Inhalt einfügen.';
    }
    if (window.GeometricViewport?.clearInto) {
      window.GeometricViewport.clearInto(editorId, viewportId);
    }
    return;
  }
  const selStart = editor.selectionStart ?? 0;
  const selEnd = editor.selectionEnd ?? selStart;
  const hasSelection = selEnd > selStart;
  const selectionStart = hasSelection ? selStart : 0;
  const selectionEnd = hasSelection ? selEnd : text.length;
  abortGpmSpectroHttp();
  const gen = gpmSpectroGeneration;
  const controller = new AbortController();
  gpmSpectroAbort = controller;
  try {
    const res = await fetch(appUrl('/api/spectroscope'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      signal: controller.signal,
      body: JSON.stringify({
        source: 'text',
        text,
        selection_start: selectionStart,
        selection_end: selectionEnd,
        modes: ['substance_divisor', 'anagram_shadow', 'structural_twin'],
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || res.statusText);
    if (gen !== gpmSpectroGeneration) return;
    const expanded = expandSpectroMatches(data.matches || [], data.token_char_map || []);
    const merged = mergeSpectroMatches(expanded);
    renderSpectroMirror(text, merged, { editorId, viewportId });
    const crossfire = merged.filter((m) => m.className === 'spectro-crossfire').length;
    const scope = hasSelection ? 'Markierung' : 'Gesamter Text';
    const summary = `${scope}: ${merged.length} Treffer · ${crossfire} Kreuzfeuer`;
    if (panel) {
      panel.classList.remove('hidden');
      panel.innerHTML = `<div class="spectro-result-panel"><strong>Spektroskopie</strong>, ${escapeHtml(summary)}</div>`;
    }
  } catch (err) {
    if (err?.name === 'AbortError') return;
    if (gen !== gpmSpectroGeneration) return;
    if (panel) {
      panel.classList.remove('hidden');
      panel.textContent = err.message || 'Spektroskopie fehlgeschlagen.';
    }
  }
}

async function runGpmSpectroscope() {
  return runSpectroscopeForEditor({
    editorId: 'gpm-source-text',
    viewportId: 'gpm-geometric-viewport',
    panelId: 'gpm-spectro-result',
  });
}

/* Editor: Drag-and-Drop, Datei laden, Leeren, Zeichenzähler */
function initGpmEditor() {
  const editor = document.getElementById('gpm-source-text');
  if (!editor) return;

  const statsEl = document.getElementById('gpm-editor-stats');
  const dropzone = document.getElementById('gpm-editor-dropzone');
  const fileInput = document.getElementById('gpm-text-file');
  const gpmFileInput = document.getElementById('gpm-gpm-file');
  const loadBtn = document.getElementById('gpm-load-text-btn');
  const loadGpmBtn = document.getElementById('gpm-load-gpm-btn');
  const clearBtn = document.getElementById('gpm-clear-btn');

  function updateStats() {
    refreshGpmEditorStats();
  }

  function loadTextFile(file) {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      editor.value = normalizeTextNfc(String(reader.result || ''));
      updateStats();
    };
    reader.readAsText(file);
  }

  function handleEditorDrop(file) {
    if (!file) return;
    if (isGpmFile(file)) {
      void ingestGpmFile(file, document.getElementById('gpm-read-result'));
      return;
    }
    loadTextFile(file);
  }

  editor.addEventListener('input', updateStats);
  loadBtn?.addEventListener('click', () => fileInput?.click());
  loadGpmBtn?.addEventListener('click', () => gpmFileInput?.click());
  fileInput?.addEventListener('change', () => {
    loadTextFile(fileInput.files && fileInput.files[0]);
    if (fileInput) fileInput.value = '';
  });
  gpmFileInput?.addEventListener('change', () => {
    const file = gpmFileInput.files?.[0];
    if (file) void ingestGpmFile(file, document.getElementById('gpm-read-result'));
    if (gpmFileInput) gpmFileInput.value = '';
  });
  clearBtn?.addEventListener('click', () => {
    abortGpmSpectroscope();
    editor.value = '';
    updateStats();
    clearGpmEditorSpectroOverlay();
    editor.focus();
  });

  document.getElementById('gpm-spectro-analyze-btn')?.addEventListener('click', runGpmSpectroscope);

  editor.addEventListener('blur', () => {
    clearGpmEditorSpectroOverlay();
  });

  initDropzone(dropzone, {
    onFile: (file) => handleEditorDrop(file),
  });

  updateStats();
}

async function runIcurveSpectroscope(side) {
  if (currentTab !== 'ikurve' || !isIcurveIngestLocked()) return;
  const matrixId = `ikurve-geometric-matrix-${side}`;
  const panelId = `ikurve-spectro-result-${side}`;
  const panel = document.getElementById(panelId);
  const gpmBase64 = window.ikurveGpmCache?.[side];
  if (!gpmBase64) {
    if (panel) {
      panel.classList.remove('hidden');
      panel.textContent = 'Kein GPM-Cache, zuerst I-Kurven vergleichen.';
    }
    return;
  }

  let tokenStart = 0;
  let tokenEnd = 0;
  const selection = window.GeometricMatrix?.getSelection(matrixId);
  if (selection) {
    tokenStart = selection.token_start;
    tokenEnd = selection.token_start + selection.token_count;
  } else {
    const viewport = side === 'a' ? window.currentAnalysis?.viewport_a : window.currentAnalysis?.viewport_b;
    const map = viewport?.token_char_map || [];
    tokenEnd = map.length ? map[map.length - 1].token_index + 1 : 0;
  }

  abortIcurveSpectroHttp();
  const gen = ikurveSpectroGeneration;
  const controller = new AbortController();
  ikurveSpectroAbort = controller;
  try {
    const res = await fetch(appUrl('/api/spectroscope'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      signal: controller.signal,
      body: JSON.stringify({
        source: 'gpm',
        file_base64: gpmBase64,
        token_start: tokenStart,
        token_end: tokenEnd,
        modes: ['substance_divisor', 'anagram_shadow', 'structural_twin'],
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || res.statusText);
    if (!isIcurveIngestLocked() || gen !== ikurveSpectroGeneration) return;
    const viewport = side === 'a' ? window.currentAnalysis?.viewport_a : window.currentAnalysis?.viewport_b;
    const expanded = expandSpectroMatches(data.matches || [], viewport?.token_char_map || []);
    const merged = mergeSpectroMatches(expanded);
    window.GeometricMatrix?.renderMatches(matrixId, merged);
    const crossfire = merged.filter((m) => m.className === 'spectro-crossfire').length;
    const scope = selection ? 'Markierung' : 'Gesamter Text';
    const summary = `${scope}: ${merged.length} Treffer · ${crossfire} Kreuzfeuer`;
    if (panel) {
      panel.classList.remove('hidden');
      panel.innerHTML = `<div class="spectro-result-panel"><strong>Spektroskopie</strong>, ${escapeHtml(summary)}</div>`;
    }
  } catch (err) {
    if (err?.name === 'AbortError') return;
    if (!isIcurveIngestLocked() || gen !== ikurveSpectroGeneration) return;
    if (panel) {
      panel.classList.remove('hidden');
      panel.textContent = err.message || 'Spektroskopie fehlgeschlagen.';
    }
  }
}

function initIcurveIngestControls() {
  ['a', 'b'].forEach((side) => {
    const input = document.getElementById(`ikurve-ingest-${side}`);
    input?.addEventListener('input', () => {
      if (isIcurveIngestLocked()) return;
      ikurveIngestText[side] = input.value;
    });

    document.getElementById(`ikurve-paste-${side}`)?.addEventListener('click', async () => {
      if (isIcurveIngestLocked()) return;
      try {
        const text = await navigator.clipboard.readText();
        setIcurveIngestText(side, text);
        const textRadio = document.querySelector(`input[name="ikurve-source-${side}"][value="text"]`);
        if (textRadio) textRadio.checked = true;
        updateIcurveGpmUi();
      } catch {
        showError(document.getElementById('ikurve-result'), 'Zwischenablage nicht lesbar.');
      }
    });

    const fileBtn = document.getElementById(`ikurve-file-btn-${side}`);
    const fileInput = document.getElementById(`ikurve-file-${side}`);
    fileBtn?.addEventListener('click', () => {
      if (isIcurveIngestLocked()) return;
      fileInput?.click();
    });
    fileInput?.addEventListener('change', async () => {
      if (isIcurveIngestLocked()) return;
      const file = fileInput.files?.[0];
      if (!file) return;
      try {
        const text = await file.text();
        setIcurveIngestText(side, text);
        const textRadio = document.querySelector(`input[name="ikurve-source-${side}"][value="text"]`);
        if (textRadio) textRadio.checked = true;
        updateIcurveGpmUi();
      } catch (err) {
        showError(document.getElementById('ikurve-result'), err.message || 'Datei konnte nicht gelesen werden.');
      } finally {
        fileInput.value = '';
      }
    });
  });

  document.getElementById('ikurve-reset-btn')?.addEventListener('click', () => {
    unlockIcurveIngest();
    ikurveIngestText.a = '';
    ikurveIngestText.b = '';
    ['a', 'b'].forEach((side) => {
      const input = document.getElementById(`ikurve-ingest-${side}`);
      if (input) input.value = '';
      ikurveSideGpm[side] = null;
    });
    updateIcurveGpmUi();
  });
}

function initIcurveGeometricLab() {
  ['a', 'b'].forEach((side) => {
    document.getElementById(`ikurve-spectro-btn-${side}`)?.addEventListener('click', () => {
      void runIcurveSpectroscope(side);
    });
  });
  initIcurveIngestControls();
}

function initGpmReadDropzone() {
  const dropzone = document.getElementById('gpm-read-dropzone');
  const fileInput = document.getElementById('gpm-read-file');
  if (!dropzone || !fileInput) return;

  initDropzone(dropzone, {
    onFile: (file) => {
      void ingestGpmFile(file, document.getElementById('gpm-read-result'));
    },
  });
  fileInput.addEventListener('change', () => {
    const file = fileInput.files?.[0];
    if (file) void ingestGpmFile(file, document.getElementById('gpm-read-result'));
  });
}

initGpmEditor();
initIcurveGeometricLab();
initGpmReadDropzone();

async function checkServerHealth() {
  const expected = document.body.dataset.appVersion;
  const bannerId = 'server-health-banner';
  let banner = document.getElementById(bannerId);

  function showBanner(msg, cls = 'error') {
    if (!banner) {
      banner = document.createElement('p');
      banner.id = bannerId;
      banner.style.margin = '1rem';
      document.querySelector('header')?.appendChild(banner);
    }
    banner.className = cls;
    banner.textContent = msg;
  }

  try {
    const res = await fetch(appUrl('/api/health'));
    if (!res.ok) {
      showBanner('Server veraltet, bitte start.bat neu starten (/api/health fehlt).');
      return;
    }
    const data = await res.json();
    if (expected && data.version && data.version !== expected) {
      showBanner(`Server-Build ${data.version} ≠ Seite ${expected}, start.bat neu starten und Strg+F5.`);
      return;
    }
    if (!data.routes?.db_stats || !data.routes?.encode) {
      showBanner('Server ohne DB/Encode-API, start.bat neu starten.');
      return;
    }
    if (banner) banner.remove();
  } catch {
    showBanner('Server nicht erreichbar.');
  }
}

checkServerHealth();
if (tabFromLocation() === 'datenbank') {
  refreshDbStats();
}
