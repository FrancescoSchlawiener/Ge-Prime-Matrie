export type IcurveMode = "atomic" | "semantic" | "structural";
export type SemanticDepth = "phrase" | "sentence" | "paragraph";
export type StructuralDepth = "line";
export type ChartScale = "union" | "shorter";
export type ChartLayout = "overlay" | "stacked";
export type IngestSourceMode = "text" | "gpm";

export interface CurvePayload {
  points?: Array<Record<string, unknown>>;
  sparkline_points?: Array<Record<string, unknown>>;
  point_count?: number;
}

export function curvePoints(obj: CurvePayload | Array<Record<string, unknown>> | null | undefined): Array<Record<string, unknown>> {
  if (!obj) return [];
  if (Array.isArray(obj)) return obj;
  if (obj.sparkline_points?.length) return obj.sparkline_points;
  return obj.points ?? [];
}

export function curvePointCount(obj: CurvePayload | Array<Record<string, unknown>> | null | undefined): number {
  if (!obj) return 0;
  if (Array.isArray(obj)) return obj.length;
  if (obj.point_count != null) return Number(obj.point_count);
  return curvePoints(obj).length;
}

export function sparklineValue(point: Record<string, unknown>, valueKey: string): number {
  const v = point[valueKey];
  return typeof v === "number" ? v : Number(v ?? 0);
}

export const SEMANTIC_DEPTH_CONFIG = {
  phrase: {
    dataKey: "phrases",
    ratioKey: "i_phrase_ratio",
    indexKey: "phrase_index",
    dtwKey: "phrase",
    depthKey: "phrase",
  },
  sentence: {
    dataKey: "sentences",
    ratioKey: "i_satz_ratio",
    indexKey: "sentence_index",
    dtwKey: "sentence",
    depthKey: "sentence",
  },
  paragraph: {
    dataKey: "paragraphs",
    ratioKey: "i_absatz_ratio",
    indexKey: "paragraph_index",
    dtwKey: "paragraph",
    depthKey: "paragraph",
  },
} as const;

export const STRUCTURAL_DEPTH_CONFIG = {
  line: {
    dataKey: "lines",
    ratioKey: "i_zeile_ratio",
    indexKey: "line_index",
    dtwKey: "line",
    depthKey: "line",
  },
} as const;

export const AXIS_SCORE_KEYS = [
  "token_i",
  "substance",
  "cell_i",
  "hierarchy",
  "literal",
  "hierarchy_sentence",
  "hierarchy_line",
] as const;

export type AxisScoreKey = (typeof AXIS_SCORE_KEYS)[number];

export function scoreBarClass(score: number): string {
  const s = Number(score) || 0;
  if (s >= 0.75) return "gpm-ikurve-score-high";
  if (s >= 0.45) return "gpm-ikurve-score-mid";
  return "gpm-ikurve-score-low";
}
