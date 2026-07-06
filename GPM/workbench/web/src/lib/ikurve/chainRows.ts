import { curvePoints } from "./curves";
import { fmtEmpty, fmtRatio, truncateText } from "./format";

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
      textA ? truncateText(textA) : fmtEmpty(textA),
      fmtEmpty(a?.s_level),
      fmtEmpty(a?.perm_index),
      fmtEmpty(a?.perm_space),
      fmtRatio(a?.[ratioKey] ?? a?.i_ratio),
      fmtEmpty(a?.ggt),
      fmtEmpty(a?.kgv),
      textB ? truncateText(textB) : fmtEmpty(textB),
      fmtEmpty(b?.s_level),
      fmtEmpty(b?.perm_index),
      fmtEmpty(b?.perm_space),
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
      fmtEmpty(a?.word),
      fmtEmpty(a?.perm_index),
      fmtEmpty(a?.perm_space),
      fmtRatio(a?.i_ratio),
      fmtRatio(a?.delta_ratio),
      fmtEmpty(a?.delta_index),
      fmtEmpty(b?.word),
      fmtEmpty(b?.perm_index),
      fmtEmpty(b?.perm_space),
      fmtRatio(b?.i_ratio),
      fmtRatio(b?.delta_ratio),
      fmtEmpty(b?.delta_index),
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
      fmtEmpty(a?.normalized ?? a?.word),
      fmtEmpty(a?.substance),
      fmtEmpty(a?.ggt),
      fmtEmpty(a?.kgv),
      fmtRatio(a?.ggt_kgv_ratio ?? a?.s_ratio),
      fmtRatio(a?.s_ratio),
      fmtEmpty(b?.normalized ?? b?.word),
      fmtEmpty(b?.substance),
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
      fmtEmpty(a?.perm_index),
      fmtRatio(a?.i_satz_ratio ?? a?.i_ratio),
      fmtEmpty(b?.perm_index),
      fmtRatio(b?.i_satz_ratio ?? b?.i_ratio),
    ]);
  }
  return rows;
}
