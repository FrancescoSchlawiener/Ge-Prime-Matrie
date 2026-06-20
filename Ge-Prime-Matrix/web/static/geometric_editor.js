/**
 * GeometricViewport — GPM-Tab Overlay (v40 Gesetz 3, legacy).
 * GeometricMatrix — I-Kurve v43 Read-Only Matrix (native Zell-Klassen, DOM-Selektion).
 */
(function () {
  const matrixState = new Map();

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function mergeClassRanges(text, mergedMatches) {
    const classes = new Array(text.length).fill('');
    for (const match of mergedMatches) {
      const start = Math.max(0, match.char_start || 0);
      const end = Math.min(text.length, match.char_end || 0);
      const cls = match.className || 'spectro-teal';
      for (let i = start; i < end; i += 1) {
        classes[i] = cls;
      }
    }
    return classes;
  }

  function buildCharTokenMap(text, tokenCharMap) {
    const map = new Array(text.length).fill(-1);
    for (const entry of tokenCharMap || []) {
      const start = entry.char_start ?? 0;
      const end = entry.char_end ?? start;
      const tokenIndex = entry.token_index ?? -1;
      for (let i = start; i < end && i < text.length; i += 1) {
        map[i] = tokenIndex;
      }
    }
    return map;
  }

  function renderMatrixHtml(text, charTokenMap, spectroClasses) {
    const normalized = String(text ?? '').replace(/\r\n/g, '\n').replace(/\r/g, '\n');
    const lines = normalized.split('\n');
    let offset = 0;
    const rows = [];
    for (let lineIdx = 0; lineIdx < lines.length; lineIdx += 1) {
      const line = lines[lineIdx];
      const cells = [];
      for (let col = 0; col < line.length; col += 1) {
        const pos = offset + col;
        const ch = line[col];
        const tokenIndex = charTokenMap[pos] ?? -1;
        const cls = spectroClasses?.[pos] || '';
        const tokenAttr = tokenIndex >= 0 ? ` data-token-index="${tokenIndex}"` : '';
        cells.push(
          `<span class="geo-cell${cls ? ` ${escapeHtml(cls)}` : ''}" data-char-offset="${pos}"${tokenAttr}>${escapeHtml(ch)}</span>`,
        );
      }
      rows.push(`<div class="geo-line" data-line="${lineIdx}">${cells.join('') || '<span class="geo-cell geo-empty">&nbsp;</span>'}</div>`);
      offset += line.length + 1;
    }
    if (!lines.length) {
      rows.push('<div class="geo-line geo-empty-line"><span class="geo-cell geo-empty">&nbsp;</span></div>');
    }
    return rows.join('');
  }

  function renderLines(text, classes) {
    const normalized = String(text ?? '').replace(/\r\n/g, '\n').replace(/\r/g, '\n');
    const charTokenMap = new Array(normalized.length).fill(-1);
    return renderMatrixHtml(normalized, charTokenMap, classes);
  }

  function cellFromNode(node) {
    if (!node) return null;
    const el = node.nodeType === Node.TEXT_NODE ? node.parentElement : node;
    return el?.closest?.('.geo-cell') || null;
  }

  function mountMatrix(containerId, payload) {
    const root = document.getElementById(containerId);
    if (!root || !payload) return;

    const text = payload.reconstructed_text || '';
    const charTokenMap = buildCharTokenMap(text, payload.token_char_map);
    matrixState.set(containerId, {
      text,
      charTokenMap,
      tokenCharMap: payload.token_char_map || [],
      spectroClasses: new Array(text.length).fill(''),
    });
    root.classList.add('geometric-matrix');
    root.innerHTML = renderMatrixHtml(text, charTokenMap, matrixState.get(containerId).spectroClasses);
  }

  function renderMatrixMatches(containerId, mergedMatches) {
    const state = matrixState.get(containerId);
    const root = document.getElementById(containerId);
    if (!state || !root) return;

    state.spectroClasses = mergeClassRanges(state.text, mergedMatches || []);
    const sel = window.getSelection();
    if (sel?.rangeCount) sel.removeAllRanges();
    root.innerHTML = renderMatrixHtml(state.text, state.charTokenMap, state.spectroClasses);
  }

  function clearMatrix(containerId) {
    const root = document.getElementById(containerId);
    matrixState.delete(containerId);
    if (root) {
      root.innerHTML = '';
      root.classList.remove('geometric-matrix');
    }
  }

  function getMatrixSelection(viewportId) {
    const root = document.getElementById(viewportId);
    const selection = window.getSelection();
    if (!root || !selection || selection.isCollapsed) return null;

    const anchorEl = cellFromNode(selection.anchorNode);
    const focusEl = cellFromNode(selection.focusNode);
    if (!anchorEl || !focusEl || !root.contains(anchorEl) || !root.contains(focusEl)) {
      return null;
    }

    const startRaw = anchorEl.dataset.tokenIndex;
    const endRaw = focusEl.dataset.tokenIndex;
    if (startRaw == null || endRaw == null || startRaw === '' || endRaw === '') {
      return null;
    }

    const startIdx = parseInt(startRaw, 10);
    const endIdx = parseInt(endRaw, 10);
    if (Number.isNaN(startIdx) || Number.isNaN(endIdx)) return null;

    return {
      token_start: Math.min(startIdx, endIdx),
      token_count: Math.abs(endIdx - startIdx) + 1,
    };
  }

  function onMatrixSelection(viewportId, callback, debounceMs = 300) {
    const root = document.getElementById(viewportId);
    if (!root || typeof callback !== 'function') return () => {};

    let timer = null;
    const schedule = () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        callback(getMatrixSelection(viewportId));
      }, debounceMs);
    };

    const onSelectionChange = () => {
      const sel = window.getSelection();
      if (!sel || !sel.anchorNode || !root.contains(sel.anchorNode)) return;
      schedule();
    };

    root.addEventListener('mouseup', schedule);
    document.addEventListener('selectionchange', onSelectionChange);

    return () => {
      clearTimeout(timer);
      root.removeEventListener('mouseup', schedule);
      document.removeEventListener('selectionchange', onSelectionChange);
    };
  }

  function renderInto(editorId, viewportId, text, mergedMatches) {
    const viewport = document.getElementById(viewportId);
    const editor = document.getElementById(editorId);
    if (!viewport || !editor) return;

    if (!mergedMatches || !mergedMatches.length || !text) {
      viewport.innerHTML = '';
      viewport.classList.add('hidden');
      editor.classList.remove('spectro-active');
      return;
    }

    const normalized = String(text ?? '').replace(/\r\n/g, '\n').replace(/\r/g, '\n');
    const classes = mergeClassRanges(normalized, mergedMatches);
    viewport.innerHTML = renderLines(normalized, classes);
    viewport.classList.remove('hidden');
    editor.classList.add('spectro-active');
  }

  window.GeometricMatrix = {
    mount: mountMatrix,
    renderMatches: renderMatrixMatches,
    getSelection: getMatrixSelection,
    onSelection: onMatrixSelection,
    clear: clearMatrix,
  };

  window.GeometricViewport = {
    renderInto,
    render: (text, mergedMatches) => renderInto('gpm-source-text', 'gpm-geometric-viewport', text, mergedMatches),
    clear: () => renderInto('gpm-source-text', 'gpm-geometric-viewport', '', []),
    clearInto: (editorId, viewportId) => renderInto(editorId, viewportId, '', []),
  };
})();
