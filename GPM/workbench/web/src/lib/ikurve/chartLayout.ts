import type { ChartScale } from "./curves";

export const SPARKLINE_VIEWBOX_W = 480;

export interface ChartCellLayout {
  maxIndex: number;
  scrollable: boolean;
  widthRatio: number;
}

export interface PairedChartLayout {
  a: ChartCellLayout;
  b: ChartCellLayout;
}

export function resolveSparklineEnd(
  points: Array<Record<string, unknown>>,
  indexKey: string,
  pointCount: number | null = null,
): number {
  if (pointCount != null && pointCount > 0) return pointCount - 1;
  if (!points.length) return 0;
  return points.reduce((max, p) => Math.max(max, Number(p[indexKey] ?? 0)), 0);
}

export function computePairedChartLayout(
  endA: number,
  endB: number,
  chartScale: ChartScale,
  spanA = 0,
  spanB = 0,
): PairedChartLayout {
  const safeMax = (end: number) => Math.max(end, 1);
  const unionLayout = (maxIndex: number): PairedChartLayout => ({
    a: { maxIndex: safeMax(maxIndex), scrollable: false, widthRatio: 1 },
    b: { maxIndex: safeMax(maxIndex), scrollable: false, widthRatio: 1 },
  });
  if (spanA <= 0 && spanB <= 0) return unionLayout(1);
  if (chartScale === "shorter" && spanA > 0 && spanB > 0 && spanA !== spanB) {
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

export function scaleBoundsY(
  valsA: number[],
  valsB: number[],
  chartScale: ChartScale,
): { min: number; max: number } {
  if (chartScale === "shorter") {
    const ref = valsA.length <= valsB.length ? valsA : valsB;
    if (!ref.length) return { min: 0, max: 1 };
    const min = Math.min(...ref);
    const max = Math.max(...ref);
    if (max - min < 0.05) return { min: Math.max(0, min - 0.025), max: Math.min(1, max + 0.025) };
    return { min, max };
  }
  const all = [...valsA, ...valsB];
  if (!all.length) return { min: 0, max: 1 };
  const min = Math.min(...all);
  const max = Math.max(...all);
  if (max - min < 0.05) return { min: Math.max(0, min - 0.025), max: Math.min(1, max + 0.025) };
  return { min, max };
}
