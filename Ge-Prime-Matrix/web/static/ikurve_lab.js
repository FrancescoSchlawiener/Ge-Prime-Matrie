/**
 * I-Kurve v42 — Spektroskopie-Labor (Client-Cache + Drei-Zonen-Akkordeon)
 */
window.currentAnalysis = null;
window.ikurveViewState = { mode: 'semantic', depth: 'sentence', chartScale: 'union' };

// Must match ge_prime.i_curve.RESPONSE_POINT_LIMIT (500) and ge_prime/sparkline.py stride spec.
const SPARKLINE_POINT_LIMIT = 500;

const IKURVE_MODE_DEFAULTS = {
  atomic: null,
  semantic: 'sentence',
  structural: 'line',
};

const IKURVE_MODE_LABELS = {
  atomic: 'Wort & Substanz',
  semantic: 'Sinn',
  structural: 'Raum',
};

const SEMANTIC_DEPTH_CONFIG = {
  phrase: {
    dataKey: 'phrases',
    ratioKey: 'i_phrase_ratio',
    indexKey: 'phrase_index',
    dtwKey: 'phrase',
    label: 'Phrase',
  },
  sentence: {
    dataKey: 'sentences',
    ratioKey: 'i_satz_ratio',
    indexKey: 'sentence_index',
    dtwKey: 'sentence',
    label: 'Satz',
  },
  paragraph: {
    dataKey: 'paragraphs',
    ratioKey: 'i_absatz_ratio',
    indexKey: 'paragraph_index',
    dtwKey: 'paragraph',
    label: 'Absatz',
  },
};

const STRUCTURAL_DEPTH_CONFIG = {
  line: {
    dataKey: 'lines',
    ratioKey: 'i_zeile_ratio',
    indexKey: 'line_index',
    dtwKey: 'line',
    label: 'Zeile',
  },
};

function pillClass(isActive, activeClass) {
  return isActive ? ` ${activeClass}` : '';
}

function dedupeNeighbors(points) {
  if (!points?.length) return points || [];
  const out = [points[0]];
  for (let i = 1; i < points.length; i += 1) {
    if (points[i] !== out[out.length - 1]) out.push(points[i]);
  }
  return out;
}

function downsampleSparklinePoints(points, limit = SPARKLINE_POINT_LIMIT) {
  if (!points?.length || points.length <= limit) return points || [];
  const stride = Math.max(1, Math.floor(points.length / limit));
  const out = [points[0]];
  for (let i = stride; i < points.length; i += stride) {
    out.push(points[i]);
  }
  if (out[out.length - 1] !== points[points.length - 1]) {
    out.push(points[points.length - 1]);
  }
  return dedupeNeighbors(out);
}

function curvePointCount(obj) {
  if (!obj) return 0;
  if (obj.point_count != null) return obj.point_count;
  return curvePoints(obj).length;
}

function curvePoints(obj) {
  if (!obj) return [];
  if (Array.isArray(obj)) return obj;
  return obj.points || [];
}

function sparklinePoints(obj) {
  if (!obj) return [];
  if (Array.isArray(obj)) return downsampleSparklinePoints(obj);
  if (obj.sparkline_points?.length) return obj.sparkline_points;
  return [];
}

function isSparklineDownsampled(obj) {
  if (!obj) return false;
  if (obj.sparkline_downsampled != null) return Boolean(obj.sparkline_downsampled);
  const fullCount = curvePointCount(obj);
  const sparkLen = obj.sparkline_points?.length ?? 0;
  return sparkLen > 0 && sparkLen < fullCount;
}

function shouldShowEnjambement(cross) {
  if (!cross) return false;
  const profile = cross.enjambement_profile;
  return (cross.rhythm_break_count ?? 0) > 0
    || profile === 'rhythm_break'
    || profile === 'enjambement_noise';
}

function renderEnjambementBadge(crossA, crossB, pipeline) {
  const phase = pipeline?.enjambement_phase;
  if (!shouldShowEnjambement(crossA) && !shouldShowEnjambement(crossB) && !phase?.phase_shift_detected) return '';
  const countA = phase?.rhythm_break_count_a ?? crossA?.rhythm_break_count ?? 0;
  const countB = phase?.rhythm_break_count_b ?? crossB?.rhythm_break_count ?? 0;
  const delta = phase?.rhythm_break_delta ?? Math.abs(countA - countB);
  const profileA = escapeHtml(phase?.enjambement_profile_a ?? crossA?.enjambement_profile ?? '—');
  const profileB = escapeHtml(phase?.enjambement_profile_b ?? crossB?.enjambement_profile ?? '—');
  const ratioA = crossA?.line_aligned_ratio != null ? fmtPct(crossA.line_aligned_ratio) : '—';
  const ratioB = crossB?.line_aligned_ratio != null ? fmtPct(crossB.line_aligned_ratio) : '—';
  return `<div class="ikurve-badge ikurve-badge-purple" role="status">
    <strong>Rhythmischer Zeilenbruch (Enjambement)</strong>
    <p>Satz- und Zeilenkanten asynchron. Brüche: A: ${fmtNum(countA)} | B: ${fmtNum(countB)} · Δ ${fmtNum(delta)}</p>
    <p class="muted">Profil A: ${profileA} · B: ${profileB} · Zeilen-Ausrichtung A: ${ratioA} · B: ${ratioB}</p>
  </div>`;
}

function renderMiniSvgPolyline(pointsA, pointsB, { valueKey = 'i_satz_ratio', indexKey = 'cell_index' } = {}) {
  const a = sparklinePoints(Array.isArray(pointsA) ? { points: pointsA } : pointsA);
  const b = sparklinePoints(Array.isArray(pointsB) ? { points: pointsB } : pointsB);
  if (!a.length && !b.length) return '';
  const width = 120;
  const height = 28;
  const pad = 2;
  const maxIndex = Math.max(a.at(-1)?.[indexKey] ?? 0, b.at(-1)?.[indexKey] ?? 0, 1);
  const toPoly = (pts, cls) => {
    if (!pts.length) return '';
    const poly = pts.map((p) => {
      const x = pad + (p[indexKey] / maxIndex) * (width - 2 * pad);
      const y = height - pad - (p[valueKey] ?? 0) * (height - 2 * pad);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    }).join(' ');
    return `<polyline class="${cls}" fill="none" stroke="currentColor" stroke-width="1.2" points="${poly}"/>`;
  };
  return `<svg class="ikurve-mini-sparkline" viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" aria-hidden="true">${toPoly(a, 'ikurve-line-a')}${toPoly(b, 'ikurve-line-b')}</svg>`;
}

function renderSparklineDownsampleHint(data, viewState) {
  const { mode, depth } = viewState;
  let downsampled = false;
  if (mode === 'atomic') {
    downsampled = isSparklineDownsampled(data.curve_a)
      || isSparklineDownsampled(data.curve_b)
      || isSparklineDownsampled(data.substance_a)
      || isSparklineDownsampled(data.substance_b);
  } else if (mode === 'semantic') {
    const cfg = SEMANTIC_DEPTH_CONFIG[depth] || SEMANTIC_DEPTH_CONFIG.sentence;
    downsampled = isSparklineDownsampled(data.semantic_a?.[cfg.dataKey])
      || isSparklineDownsampled(data.semantic_b?.[cfg.dataKey]);
  } else {
    const cfg = STRUCTURAL_DEPTH_CONFIG[depth] || STRUCTURAL_DEPTH_CONFIG.line;
    downsampled = isSparklineDownsampled(data.structural_a?.[cfg.dataKey])
      || isSparklineDownsampled(data.structural_b?.[cfg.dataKey]);
  }
  if (!downsampled) return '';
  return '<p class="ikurve-sparkline-hint muted">Sparkline visuell auf 500 Punkte downsampled — arithmetische Tabellen in Zone 3 sind vollständig.</p>';
}

function setIcurveMode(mode) {
  const prev = window.ikurveViewState || {};
  window.ikurveViewState = {
    mode,
    depth: IKURVE_MODE_DEFAULTS[mode] ?? null,
    chartScale: prev.chartScale || 'union',
  };
  patchIcurveLabView();
}

function setIcurveDepth(depth) {
  if (window.ikurveViewState.mode === 'atomic') return;
  window.ikurveViewState.depth = depth;
  patchIcurveLabView();
}

function setIcurveChartScale(chartScale) {
  window.ikurveViewState = {
    ...window.ikurveViewState,
    chartScale: chartScale === 'shorter' ? 'shorter' : 'union',
  };
  patchIcurveLabView();
}

function replaceIcurveZone(zoneId, html) {
  const root = document.getElementById('ikurve-result');
  const old = root?.querySelector(`[data-ikurve-zone="${zoneId}"]`);
  if (!old) return false;
  const wasOpen = old.open;
  const wrap = document.createElement('div');
  wrap.innerHTML = html.trim();
  const neu = wrap.firstElementChild;
  if (!neu) return false;
  old.replaceWith(neu);
  if (wasOpen) neu.open = true;
  return true;
}

function patchIcurveLabView() {
  const analysis = window.currentAnalysis;
  const state = window.ikurveViewState;
  if (!analysis || !state) return;
  const root = document.getElementById('ikurve-result');
  if (!root?.querySelector('.ikurve-result')) {
    renderIcurveLab(analysis, state);
    return;
  }
  replaceIcurveZone('2', renderIcurveZone2(analysis, state));
  replaceIcurveZone('3', renderIcurveZone3(analysis, state));
}

function renderForeignTokenAuditCompact(metaA, metaB, p) {
  const audit = arguments.length === 1 && metaA && typeof metaA === 'object' && 'audit_status' in metaA
    ? metaA
    : null;
  const mode = audit?.db_audit_mode
    || p?.db_audit_mode
    || metaA?.language?.db_coverage?.db_audit_mode
    || 'de_en';
  if (mode === 'off') return '';
  let tokens = audit?.foreign_tokens || audit?.top_foreign_tokens || [];
  if (!tokens.length) {
    const dbA = metaA?.language?.db_coverage || p?.db_coverage_a || {};
    const dbB = metaB?.language?.db_coverage || p?.db_coverage_b || {};
    tokens = [...(dbA.foreign_tokens || []), ...(dbB.foreign_tokens || [])];
  }
  const seen = new Set();
  const unique = [];
  tokens.forEach((row) => {
    const key = `${row.normalized}:${row.detected_lang}`;
    if (seen.has(key)) return;
    seen.add(key);
    unique.push(row);
  });
  if (!unique.length) {
    return '<p class="ikurve-foreign-compact muted">Abweichende DB-Zuordnung (Richtwert): keine Treffer.</p>';
  }
  const items = unique.slice(0, 5).map((row) => {
    const word = escapeHtml(row.word || row.normalized);
    const lang = escapeHtml(String(row.detected_lang || '?').toUpperCase());
    return `${word} (${lang})`;
  }).join(', ');
  return `<p class="ikurve-foreign-compact"><strong>Abweichende DB-Zuordnung (Richtwert):</strong> ${items}</p>`;
}

function buildWordTokenRows(data) {
  const rows = [];
  const limit = Math.min(
    30,
    Math.max(curvePointCount(data.curve_a), curvePointCount(data.curve_b)),
  );
  for (let i = 0; i < limit; i += 1) {
    const a = data.curve_a.points[i];
    const b = data.curve_b.points[i];
    rows.push([
      i,
      a ? a.word : '—',
      a ? a.perm_index : '—',
      a ? a.i_ratio : '—',
      b ? b.word : '—',
      b ? b.perm_index : '—',
      b ? b.i_ratio : '—',
    ]);
  }
  return rows;
}

function buildSubstRows(data) {
  const rows = [];
  const substLimit = Math.min(
    20,
    Math.max(curvePointCount(data.substance_a), curvePointCount(data.substance_b)),
  );
  for (let i = 0; i < substLimit; i += 1) {
    const a = data.substance_a?.points?.[i];
    const b = data.substance_b?.points?.[i];
    rows.push([
      i,
      a ? a.normalized : '—',
      a ? a.substance : '—',
      a ? a.ggt : '—',
      a ? a.kgv : '—',
      a ? (a.ggt_kgv_ratio ?? a.s_ratio) : '—',
      b ? b.normalized : '—',
      b ? b.substance : '—',
      b ? b.ggt : '—',
      b ? b.kgv : '—',
      b ? (b.ggt_kgv_ratio ?? b.s_ratio) : '—',
    ]);
  }
  return rows;
}

function buildCellRows(data) {
  const rows = [];
  const cellLimit = Math.min(
    20,
    Math.max(curvePointCount(data.cell_geometry_a), curvePointCount(data.cell_geometry_b)),
  );
  for (let i = 0; i < cellLimit; i += 1) {
    const a = data.cell_geometry_a?.points?.[i];
    const b = data.cell_geometry_b?.points?.[i];
    rows.push([
      i,
      a ? `[${(a.skeleton || []).join(',')}]` : '—',
      a ? a.i_satz_ratio : '—',
      a ? a.token_count : '—',
      b ? `[${(b.skeleton || []).join(',')}]` : '—',
      b ? b.i_satz_ratio : '—',
      b ? b.token_count : '—',
    ]);
  }
  return rows;
}

function buildHierarchyTableRows(data, depth, mode) {
  const config = mode === 'semantic'
    ? SEMANTIC_DEPTH_CONFIG[depth]
    : STRUCTURAL_DEPTH_CONFIG[depth];
  if (!config) return [];
  const prefix = mode === 'semantic' ? 'semantic' : 'structural';
  const ptsA = curvePoints(data[`${prefix}_a`]?.[config.dataKey]);
  const ptsB = curvePoints(data[`${prefix}_b`]?.[config.dataKey]);
  const limit = Math.min(30, Math.max(curvePointCount(ptsA), curvePointCount(ptsB)));
  const rows = [];
  for (let i = 0; i < limit; i += 1) {
    const a = ptsA[i];
    const b = ptsB[i];
    rows.push([
      i,
      a ? a.token_start : '—',
      a ? a.token_count : '—',
      a ? a[config.ratioKey] : '—',
      a ? a.s_level : '—',
      a ? (a.ggt_kgv_ratio ?? '—') : '—',
      b ? b.token_start : '—',
      b ? b.token_count : '—',
      b ? b[config.ratioKey] : '—',
      b ? b.s_level : '—',
      b ? (b.ggt_kgv_ratio ?? '—') : '—',
    ]);
  }
  return rows;
}

function renderZone2Charts(data, viewState) {
  const { mode, depth, chartScale = 'union' } = viewState;
  const scaleOpts = { chartScale };
  if (mode === 'atomic') {
    const wordCharts = renderPairedSparklines(
      sparklinePoints(data.curve_a),
      sparklinePoints(data.curve_b),
      'ikurve-line-a',
      'ikurve-line-b',
      {
        valueKey: 'i_ratio',
        indexKey: 'position',
        labelA: 'Kurve A (i_ratio)',
        labelB: 'Kurve B (i_ratio)',
        ...scaleOpts,
      },
    );
    const substCharts = renderPairedSparklines(
      sparklinePoints(data.substance_a),
      sparklinePoints(data.substance_b),
      'ikurve-line-a',
      'ikurve-line-b',
      {
        valueKey: 'ggt_kgv_ratio',
        indexKey: 'position',
        labelA: 'Substanz A (ggT/kgV)',
        labelB: 'Substanz B (ggT/kgV)',
        ...scaleOpts,
      },
    );
    return `${wordCharts}${substCharts}`;
  }
  if (mode === 'semantic') {
    const cfg = SEMANTIC_DEPTH_CONFIG[depth] || SEMANTIC_DEPTH_CONFIG.sentence;
    const ptsA = sparklinePoints(data.semantic_a?.[cfg.dataKey]);
    const ptsB = sparklinePoints(data.semantic_b?.[cfg.dataKey]);
    return renderPairedSparklines(ptsA, ptsB, 'ikurve-line-a', 'ikurve-line-b', {
      valueKey: cfg.ratioKey,
      indexKey: cfg.indexKey,
      labelA: `Kurve A (${cfg.label}-Rhythmus)`,
      labelB: `Kurve B (${cfg.label}-Rhythmus)`,
      ...scaleOpts,
    });
  }
  const cfg = STRUCTURAL_DEPTH_CONFIG[depth] || STRUCTURAL_DEPTH_CONFIG.line;
  const ptsA = sparklinePoints(data.structural_a?.[cfg.dataKey]);
  const ptsB = sparklinePoints(data.structural_b?.[cfg.dataKey]);
  return renderPairedSparklines(ptsA, ptsB, 'ikurve-line-a', 'ikurve-line-b', {
    valueKey: cfg.ratioKey,
    indexKey: cfg.indexKey,
    labelA: `Kurve A (${cfg.label}-Rhythmus)`,
    labelB: `Kurve B (${cfg.label}-Rhythmus)`,
    ...scaleOpts,
  });
}

function renderZone2Dtw(data, viewState) {
  const { mode, depth } = viewState;
  if (mode === 'atomic') return renderZone2AtomicForensics(data);
  const hc = data.hierarchy_comparison || {};
  let score = 0;
  let label = '';
  let cmp = null;
  if (mode === 'semantic') {
    const cfg = SEMANTIC_DEPTH_CONFIG[depth] || SEMANTIC_DEPTH_CONFIG.sentence;
    cmp = hc.semantic?.[cfg.dtwKey];
    score = cmp?.geometry_score ?? 0;
    label = cfg.label;
  } else {
    const cfg = STRUCTURAL_DEPTH_CONFIG[depth] || STRUCTURAL_DEPTH_CONFIG.line;
    cmp = hc.structural?.[cfg.dtwKey];
    score = cmp?.geometry_score ?? 0;
    label = cfg.label;
  }
  return `${renderDtwFailedWarning(cmp, `${label}-DTW`)}<p class="ikurve-dtw-line muted">DTW-Score (${escapeHtml(label)}-Ebene): <strong>${fmtPct(score)}</strong></p>`;
}

function renderZone2AtomicForensics(data) {
  const c = data.comparison;
  const substCmp = data.substance_comparison || c.substance_geometry || {};
  const cellCmp = data.cell_comparison || c.cell_geometry || {};
  return [
    renderDtwFailedWarning(c, 'Wort-DTW'),
    renderDtwFailedWarning(substCmp, 'Substanz-DTW'),
    renderDtwFailedWarning(cellCmp, 'Zell-DTW'),
  ].join('');
}

function renderAtomicForensicsMetrics(data) {
  const c = data.comparison;
  const substCmp = data.substance_comparison || c.substance_geometry || {};
  const cellCmp = data.cell_comparison || c.cell_geometry || {};
  const wg = c.word_geometry || {};
  const alignHint = c.aligned
    ? 'Token ausgerichtet'
    : `Fenster-Offset ${fmtNum(c.best_offset)}`;
  const sumA = data.curve_a?.summary || {};
  const sumB = data.curve_b?.summary || {};
  const cellSumA = data.cell_geometry_a?.summary || {};
  const cellSumB = data.cell_geometry_b?.summary || {};
  return `<div class="compare-match-grid ikurve-metrics ikurve-atomic-metrics">
    <div class="ikurve-metric-card ikurve-metrics-word">
      <div class="compare-gcd-label">Wort-Geometrie</div>
      <div class="compare-gcd-value">${fmtPct(c.geometry_score ?? 0)}</div>
      <p class="muted compare-match-hint">DTW ${fmtPct(wg.dtw_score ?? c.geometry_score_dtw ?? 0)} · MAE ${fmtPct(wg.mae_score ?? c.geometry_score_mae ?? 0)}</p>
      <p class="muted compare-match-hint">Literal ${fmtPct(c.literal_match_ratio ?? 0)} · ${escapeHtml(alignHint)}</p>
      <p class="muted compare-match-hint">Δ-Mittel A/B ${fmtPct(sumA.mean_delta_ratio ?? 0)} / ${fmtPct(sumB.mean_delta_ratio ?? 0)}</p>
    </div>
    <div class="ikurve-metric-card ikurve-metrics-substance">
      <div class="compare-gcd-label">Substanz-Kette</div>
      <div class="compare-gcd-value">${fmtPct(substCmp.geometry_score ?? 0)}</div>
      <p class="muted compare-match-hint">${fmtNum(substCmp.substance_twin_count ?? 0)} Substanz-Zwillinge · ${fmtNum(substCmp.anagram_shadow_count ?? 0)} Anagramm-Schatten</p>
      <p class="muted compare-match-hint">Token A/B ${fmtNum(substCmp.length_a ?? 0)} / ${fmtNum(substCmp.length_b ?? 0)} · Ø ggT/kgV ${fmtPct(substCmp.mean_similarity ?? 0)}</p>
    </div>
    <div class="ikurve-metric-card ikurve-metrics-cell">
      <div class="compare-gcd-label">Zell-Geometrie</div>
      <div class="compare-gcd-value">${fmtPct(cellCmp.geometry_score ?? 0)}</div>
      <p class="muted compare-match-hint">${fmtNum(cellCmp.match_count ?? 0)} exakte Skelett-Treffer</p>
      <p class="muted compare-match-hint">Zellen A/B ${fmtNum(cellCmp.length_a ?? cellSumA.cell_count ?? 0)} / ${fmtNum(cellCmp.length_b ?? cellSumB.cell_count ?? 0)}</p>
    </div>
  </div>`;
}

function renderIcurveZone1(data) {
  const c = data.comparison;
  const p = data.structure_assessment || {};
  const cellCmp = data.cell_comparison || c.cell_geometry || {};
  const substCmp = data.substance_comparison || c.substance_geometry || {};
  const relCmp = data.relation_comparison || {};
  const pipeline = data.validation_pipeline || {};
  const alertClass = c.structural_waveform_parallel ? 'ikurve-alert ikurve-alert-warn' : 'ikurve-alert';
  const showInterpretation = !c.structural_cell_twins || c.structural_waveform_parallel;
  const audit = p.db_speech_audit || data.meta_a?.language?.db_speech_audit;
  let speechAuditHtml = '';
  if (audit) {
    if (audit.audit_status === 'CRITICAL_ANOMALY') {
      speechAuditHtml = `
      <div class="ikurve-badge ikurve-badge-red" role="status">
        <strong>Sprach-DB-Audit: HOHE ENTROPIE (DIFFUS)</strong>
        <span>Die Token-Substanz weist ein flaches Verteilungsmuster auf. Keine statistisch signifikante Leitsprache extrahierbar (Informationstheoretisches Rauschen).</span>
      </div>`;
    } else if (audit.language_uncertain) {
      const displayLang = audit.primary_language === 'unknown'
        ? 'UNDEFINIERTE'
        : String(audit.primary_language || '?').toUpperCase();
      speechAuditHtml = `
      <div class="ikurve-badge ikurve-badge-yellow" role="status">
        <strong>Sprach-DB-Audit: HYBRIDE / SCHWACHE MATRIX</strong>
        <span>Mischsignal detektiert. Primäre Tendenz: ${escapeHtml(displayLang)} (${Math.round((audit.confidence || 0) * 100)}% Konfidenz). Matrix-Abdeckung liegt unter dem Standard-Richtwert.</span>
      </div>`;
    } else if (audit.audit_status === 'VERIFIED') {
      speechAuditHtml = renderForeignTokenAuditCompact(audit);
    }
  }
  return `<details class="ikurve-zone word-panel" data-ikurve-zone="1" open>
    <summary>Struktur-Kreuzvalidierung</summary>
    <div class="word-panel-body ikurve-zone-body">
      ${renderValidationPipeline(pipeline)}
      ${renderSignalOverview(p, c, cellCmp, substCmp, relCmp)}
      ${renderStructureAssessment(p, c)}
      ${renderEnjambementBadge(data.cross_analysis_a, data.cross_analysis_b, pipeline)}
      ${renderSubstanceTwinsBanner(p)}
      ${renderRelationTwinsBanner(p)}
      ${renderCellTwinsBanner(c)}
      ${showInterpretation ? `<p class="${alertClass}"><strong>${escapeHtml(c.interpretation)}</strong></p>` : ''}
      ${c.structural_waveform_parallel ? '<p class="ikurve-flag">Strukturelle Wellenform-Parallelität (Wort-Ebene)</p>' : ''}
      ${speechAuditHtml}
    </div>
  </details>`;
}

function renderIcurveZone2(data, viewState) {
  const { mode, depth, chartScale = 'union' } = viewState;
  const showDepth = mode === 'semantic' || mode === 'structural';
  const depthHiddenClass = showDepth ? '' : ' hidden';
  const scaleButtons = ['union', 'shorter'].map((key) => {
    const active = key === chartScale;
    const activeClass = pillClass(active, 'ikurve-chart-scale-active');
    const pressed = active ? ' aria-pressed="true"' : ' aria-pressed="false"';
    const label = key === 'shorter' ? 'Kürzere als Maß' : 'Gemeinsame Skala';
    return `<button type="button" class="ikurve-chart-scale-btn${activeClass}" data-ikurve-chart-scale="${key}"${pressed}>${escapeHtml(label)}</button>`;
  }).join('');
  const modeButtons = Object.entries(IKURVE_MODE_LABELS).map(([key, label]) => {
    const active = key === mode;
    const activeClass = pillClass(active, 'ikurve-layer-active');
    const pressed = active ? ' aria-pressed="true"' : ' aria-pressed="false"';
    return `<button type="button" class="ikurve-layer-btn${activeClass}" data-ikurve-mode="${key}"${pressed}>${escapeHtml(label)}</button>`;
  }).join('');
  let depthButtons = '';
  if (mode === 'semantic') {
    depthButtons = Object.entries(SEMANTIC_DEPTH_CONFIG).map(([key, cfg]) => {
      const active = key === depth;
      const activeClass = pillClass(active, 'ikurve-depth-active');
      const pressed = active ? ' aria-pressed="true"' : ' aria-pressed="false"';
      return `<button type="button" class="ikurve-depth-btn${activeClass}" data-ikurve-depth="${key}"${pressed}>${escapeHtml(cfg.label)}</button>`;
    }).join('');
  } else if (mode === 'structural') {
    depthButtons = Object.entries(STRUCTURAL_DEPTH_CONFIG).map(([key, cfg]) => {
      const active = key === depth;
      const activeClass = pillClass(active, 'ikurve-depth-active');
      const pressed = active ? ' aria-pressed="true"' : ' aria-pressed="false"';
      return `<button type="button" class="ikurve-depth-btn${activeClass}" data-ikurve-depth="${key}"${pressed}>${escapeHtml(cfg.label)}</button>`;
    }).join('');
  }
  return `<details class="ikurve-zone word-panel" data-ikurve-zone="2" open>
    <summary>Geometrische Linse</summary>
    <div class="word-panel-body ikurve-zone-body">
      <div class="ikurve-layer-switch" role="group" aria-label="Hauptmodus">
        ${modeButtons}
      </div>
      <div class="ikurve-depth-pills${depthHiddenClass}" role="group" aria-label="Tiefe">
        ${depthButtons}
      </div>
      <div class="ikurve-chart-scale" role="group" aria-label="Kurven-Maßstab">
        ${scaleButtons}
      </div>
      <div class="ikurve-charts-container" aria-live="polite" aria-atomic="true">
        ${renderZone2Charts(data, viewState)}
        ${renderZone2Dtw(data, viewState)}
        ${renderSparklineDownsampleHint(data, viewState)}
      </div>
    </div>
  </details>`;
}

function renderIcurveZone3(data, viewState) {
  const c = data.comparison;
  const p = data.structure_assessment || {};
  const cellCmp = data.cell_comparison || c.cell_geometry || {};
  const relCmp = data.relation_comparison || {};
  const mc = data.meta_comparison || {};
  const notes = (c.notes || []).map((n) => `<li>${escapeHtml(n)}</li>`).join('');
  const { mode, depth } = viewState;
  let tableHtml = '';
  if (mode === 'atomic') {
    const rows = buildWordTokenRows(data);
    const substRows = buildSubstRows(data);
    const cellRows = buildCellRows(data);
    if (rows.length) {
      tableHtml += `<h4 class="ikurve-layer-head">Wort-Token</h4>${renderGpmTable(['Pos', 'Wort A', 'I', 'i_ratio', 'Wort B', 'I', 'i_ratio'], rows)}`;
    }
    if (substRows.length) {
      tableHtml += `<h4 class="ikurve-layer-head">Substanz-Kette</h4>${renderGpmTable(['Pos', 'Wort A', 'S', 'ggT', 'kgV', 'ggT/kgV', 'Wort B', 'S', 'ggT', 'kgV', 'ggT/kgV'], substRows)}`;
    }
    if (cellRows.length) {
      const miniSpark = renderMiniSvgPolyline(
        data.cell_geometry_a,
        data.cell_geometry_b,
        { valueKey: 'i_satz_ratio', indexKey: 'cell_index' },
      );
      tableHtml += `<details class="ikurve-cell-nested word-panel">
        <summary class="ikurve-zone-header">
          <span class="ikurve-zone-header-title">Arithmetische Zell-Kette (Satz-Ebene)</span>
          <span class="ikurve-mini-sparkline-container">${miniSpark}</span>
        </summary>
        <div class="word-panel-body">${renderGpmTable(['Zelle', 'Skelett A', 'I_Satz', 'Token', 'Skelett B', 'I_Satz', 'Token'], cellRows)}</div>
      </details>`;
    }
  } else if (mode === 'semantic') {
    const cfg = SEMANTIC_DEPTH_CONFIG[depth] || SEMANTIC_DEPTH_CONFIG.sentence;
    const rows = buildHierarchyTableRows(data, depth, 'semantic');
    if (rows.length) {
      tableHtml = `<h4 class="ikurve-layer-head">Sinn — ${escapeHtml(cfg.label)}</h4>${renderGpmTable(['Idx', 'start A', 'cnt A', cfg.ratioKey, 'S A', 'ggT/kgV A', 'start B', 'cnt B', cfg.ratioKey, 'S B', 'ggT/kgV B'], rows)}`;
    }
  } else {
    const cfg = STRUCTURAL_DEPTH_CONFIG[depth] || STRUCTURAL_DEPTH_CONFIG.line;
    const rows = buildHierarchyTableRows(data, depth, 'structural');
    if (rows.length) {
      tableHtml = `<h4 class="ikurve-layer-head">Raum — ${escapeHtml(cfg.label)}</h4>${renderGpmTable(['Idx', 'start A', 'cnt A', cfg.ratioKey, 'S A', 'ggT/kgV A', 'start B', 'cnt B', cfg.ratioKey, 'S B', 'ggT/kgV B'], rows)}`;
    }
  }
  if (!tableHtml) {
    tableHtml = '<p class="muted">Keine Detail-Ketten für diese Ebene.</p>';
  }
  const atomicMetrics = mode === 'atomic' ? renderAtomicForensicsMetrics(data) : '';
  const alignNote = !c.aligned
    ? `<p class="muted">Token-Anzahl unterschiedlich — bestes Fenster ab Offset ${fmtNum(c.best_offset)}.</p>`
    : '';
  const cellNote = cellCmp.method === 'dtw' && (cellCmp.length_a !== cellCmp.length_b)
    ? '<p class="muted">Zell-Ketten durch Segmentierung verschoben — Vergleich via DTW.</p>'
    : '';
  return `<details class="ikurve-zone word-panel" data-ikurve-zone="3">
    <summary>Arithmetische Detail-Ketten</summary>
    <div class="word-panel-body ikurve-zone-body">
      ${atomicMetrics}
      ${tableHtml}
      ${renderLanguageDbCard(data.meta_a, data.meta_b, p)}
      ${renderRelationOverlap(relCmp, data.meta_a, data.meta_b)}
      <div class="meta-genome-grid">
        ${renderMetaGenomeCard('A', data.meta_a)}
        ${renderMetaGenomeCard('B', data.meta_b)}
      </div>
      ${mc.same_domain_relational ? '<p class="muted">Gleiche Domäne mit geteilten Wort-Beziehungen.</p>' : mc.same_domain ? '<p class="muted">Meta-Genom: gleiche Domäne (ggT über Schwellwert).</p>' : ''}
      ${alignNote}
      ${cellNote}
      ${notes ? `<ul class="compare-notes">${notes}</ul>` : ''}
    </div>
  </details>`;
}

function renderIcurveLab(data, viewState) {
  const analysis = data ?? window.currentAnalysis;
  const state = viewState ?? window.ikurveViewState;
  const el = document.getElementById('ikurve-result');
  if (!el) return;
  if (!analysis) {
    showError(el, 'Keine Analysedaten — bitte erneut vergleichen.');
    return;
  }
  if (typeof showResult !== 'function') {
    el.classList.remove('hidden');
    el.innerHTML = '<p class="error">UI nicht vollständig geladen — Seite mit Strg+F5 neu laden.</p>';
    return;
  }
  try {
    const html = `<div class="ikurve-result">
      ${renderIcurveZone1(analysis)}
      ${renderIcurveZone2(analysis, state)}
      ${renderIcurveZone3(analysis, state)}
    </div>`;
    showResult(el, html);
  } catch (err) {
    showError(el, err?.message || 'Darstellung der I-Kurve fehlgeschlagen.');
  }
}

function initIcurveLabDelegation() {
  const root = document.getElementById('ikurve-result');
  if (!root || root.dataset.ikurveLabBound) return;
  root.dataset.ikurveLabBound = '1';
  root.addEventListener('click', (e) => {
    const modeBtn = e.target.closest('[data-ikurve-mode]');
    if (modeBtn) {
      e.preventDefault();
      setIcurveMode(modeBtn.dataset.ikurveMode);
      return;
    }
    const depthBtn = e.target.closest('[data-ikurve-depth]');
    if (depthBtn && window.ikurveViewState.mode !== 'atomic') {
      e.preventDefault();
      setIcurveDepth(depthBtn.dataset.ikurveDepth);
      return;
    }
    const scaleBtn = e.target.closest('[data-ikurve-chart-scale]');
    if (scaleBtn) {
      e.preventDefault();
      setIcurveChartScale(scaleBtn.dataset.ikurveChartScale);
    }
  });
}

initIcurveLabDelegation();
