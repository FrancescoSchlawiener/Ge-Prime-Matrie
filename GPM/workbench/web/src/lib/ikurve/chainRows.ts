import { formatSiPair } from "../../utils/formatSi";
import { curvePoints } from "./curves";
import { fmtEmpty, fmtRatio, truncateText } from "./format";

/**
 * Sterile Symmetrie-Vertrag:
 * - formatSiPair: intakte API-Punkte (substance + perm_index)
 * - fmtEmpty (—): nur optische Ausrichtung bei Längen-Asymmetrie (fehlendes Gegenstück)
 * - Kein ?-Reparaturpfad, kein Header-Join
 */

function gapCell(): string {
  return fmtEmpty(null);
}

function wordCell(point: Record<string, unknown> | undefined): string {
  if (!point) return gapCell();
  const word = String(point.word ?? point.normalized ?? "");
  return word ? truncateText(word) : gapCell();
}

function siPairCell(point: Record<string, unknown> | undefined): string {
  if (!point) return gapCell();
  return formatSiPair(Number(point.substance ?? point.cell_substance ?? 0), Number(point.perm_index ?? 0));
}

export function buildHierarchyRows(
  ptsA: Array<Record<string, unknown>>,
  ptsB: Array<Record<string, unknown>>,
  ratioKey: string,
): (string | number)[][] {
  const limit = Math.min(50, Math.max(ptsA.length, ptsB.length));
  const rows: (string | number)[][] = [];
  for (let i = 0; i < limit; i += 1) {
    const a = ptsA[i];
    const b = ptsB[i];
    const textA = String(a?.text ?? a?.label ?? a?.word ?? "");
    const textB = String(b?.text ?? b?.label ?? b?.word ?? "");
    rows.push([
      i,
      textA ? truncateText(textA) : gapCell(),
      fmtEmpty(a?.s_level),
      siPairCell(a ? { substance: a.s_level, perm_index: a.perm_index } : undefined),
      fmtRatio(a?.[ratioKey] ?? a?.i_ratio),
      fmtEmpty(a?.ggt),
      fmtEmpty(a?.kgv),
      textB ? truncateText(textB) : gapCell(),
      fmtEmpty(b?.s_level),
      siPairCell(b ? { substance: b.s_level, perm_index: b.perm_index } : undefined),
      fmtRatio(b?.[ratioKey] ?? b?.i_ratio),
      fmtEmpty(b?.ggt),
      fmtEmpty(b?.kgv),
    ]);
  }
  return rows;
}

export function buildWordTokenRows(data: Record<string, unknown>): (string | number)[][] {
  const ptsA = curvePoints(data.curve_a as never);
  const ptsB = curvePoints(data.curve_b as never);
  const limit = Math.min(50, Math.max(ptsA.length, ptsB.length));
  const rows: (string | number)[][] = [];
  for (let i = 0; i < limit; i += 1) {
    const a = ptsA[i];
    const b = ptsB[i];
    rows.push([
      i,
      wordCell(a),
      siPairCell(a),
      a ? fmtRatio(a.i_ratio) : gapCell(),
      a ? fmtRatio(a.delta_ratio) : gapCell(),
      a ? String(a.delta_index ?? 0) : gapCell(),
      wordCell(b),
      siPairCell(b),
      b ? fmtRatio(b.i_ratio) : gapCell(),
      b ? fmtRatio(b.delta_ratio) : gapCell(),
      b ? String(b.delta_index ?? 0) : gapCell(),
    ]);
  }
  return rows;
}

export function buildSubstRows(data: Record<string, unknown>): (string | number)[][] {
  const ptsA = curvePoints(data.substance_a as never);
  const ptsB = curvePoints(data.substance_b as never);
  const limit = Math.min(30, Math.max(ptsA.length, ptsB.length));
  const rows: (string | number)[][] = [];
  for (let i = 0; i < limit; i += 1) {
    const a = ptsA[i];
    const b = ptsB[i];
    rows.push([
      i,
      a ? String(a.normalized ?? a.word ?? "") : gapCell(),
      a ? String(a.substance ?? "") : gapCell(),
      fmtEmpty(a?.ggt),
      fmtEmpty(a?.kgv),
      fmtRatio(a?.ggt_kgv_ratio ?? a?.s_ratio),
      fmtRatio(a?.s_ratio),
      b ? String(b.normalized ?? b.word ?? "") : gapCell(),
      b ? String(b.substance ?? "") : gapCell(),
      fmtEmpty(b?.ggt),
      fmtEmpty(b?.kgv),
      fmtRatio(b?.ggt_kgv_ratio ?? b?.s_ratio),
      fmtRatio(b?.s_ratio),
    ]);
  }
  return rows;
}

export function buildCellRows(data: Record<string, unknown>): (string | number)[][] {
  const ptsA = curvePoints(data.cell_geometry_a as never);
  const ptsB = curvePoints(data.cell_geometry_b as never);
  const limit = Math.min(30, Math.max(ptsA.length, ptsB.length));
  const rows: (string | number)[][] = [];
  for (let i = 0; i < limit; i += 1) {
    const a = ptsA[i];
    const b = ptsB[i];
    rows.push([
      i,
      a ? truncateText(String(a.label ?? "")) : gapCell(),
      siPairCell(a),
      a ? fmtRatio(a.i_satz_ratio ?? a.i_ratio) : gapCell(),
      a ? String(a.token_count ?? "") : gapCell(),
      b ? truncateText(String(b.label ?? "")) : gapCell(),
      siPairCell(b),
      b ? fmtRatio(b.i_satz_ratio ?? b.i_ratio) : gapCell(),
      b ? String(b.token_count ?? "") : gapCell(),
    ]);
  }
  return rows;
}
