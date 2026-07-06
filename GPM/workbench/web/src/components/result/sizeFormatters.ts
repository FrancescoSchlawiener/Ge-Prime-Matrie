import type { CSSProperties } from "react";
import { t } from "../../i18n/t";

export interface SizeRow {
  id: string;
  bytes: number;
  sample: string;
  is_gpm: boolean;
  ext: string;
  category: string;
  formula_id: string;
  pct_of_max: number;
}

export interface SizeInsightPoint {
  id: string;
  params?: Record<string, string | number>;
}

export interface SizeInsight {
  verdict: "win" | "tie" | "learn";
  baseline_bytes: number;
  best_gpm_bytes: number;
  saved_bytes: number;
  pct_saved: number;
  points: SizeInsightPoint[];
}

export interface SizeCalcStep {
  step_id: string;
  bytes?: number;
  detail_params?: Record<string, string | number>;
}

export interface SizeComparisonData {
  subject: string;
  rows: SizeRow[];
  insight: SizeInsight;
  highlight_ids: string[];
  max_bytes: number;
  calculation: SizeCalcStep[];
  cache_miss?: boolean;
}

export function formatBytes(num: number): string {
  if (num < 1024) return `${num} B`;
  if (num < 1024 * 1024) return `${(num / 1024).toFixed(1).replace(".", ",")} KB`;
  return `${(num / (1024 * 1024)).toFixed(2).replace(".", ",")} MB`;
}

export function interpolate(template: string, params: Record<string, string | number>): string {
  return Object.entries(params).reduce(
    (acc, [key, value]) => acc.replaceAll(`{${key}}`, String(value)),
    template,
  );
}

export function rowLabel(row: SizeRow): string {
  return t(`result.size.rows.${row.id}`, row.id);
}

export function rowSample(row: SizeRow): string {
  const key = `result.size.samples.${row.sample}`;
  const translated = t(key, "");
  return translated || row.sample;
}

export function formulaLabel(formulaId: string): string {
  if (!formulaId) return "";
  return t(`result.size.formulas.${formulaId}`, "");
}

export function insightHeadline(data: SizeComparisonData): string {
  const { insight, subject } = data;
  if (subject === "decode_word") {
    return t("result.size.headline.decode");
  }
  const verdict = insight.verdict;
  if (verdict === "win") {
    const saved = formatBytes(Math.abs(insight.saved_bytes));
    return interpolate(t("result.size.headline.win"), {
      saved,
      pct: String(insight.pct_saved),
    });
  }
  if (verdict === "tie") {
    return t("result.size.headline.tie");
  }
  if (subject === "encode_batch" && insight.saved_bytes <= 0) {
    return t("result.size.headline.learn_batch");
  }
  const extra = formatBytes(Math.abs(insight.saved_bytes));
  return interpolate(t("result.size.headline.learn"), { extra });
}

export function insightPointText(point: SizeInsightPoint, subject: string): string {
  const key = `result.size.insight.${point.id}`;
  const params = { ...(point.params ?? {}) };
  for (const [k, v] of Object.entries(params)) {
    if (typeof v === "number" && (k === "plain" || k === "gpm" || k === "bytes")) {
      params[k] = formatBytes(v);
    }
  }
  if (point.id === "baseline_vs_gpm" && subject === "encode_batch") {
    return interpolate(t("result.size.insight.baseline_vs_gpm_batch"), params as Record<string, string>);
  }
  return interpolate(t(key, point.id), params as Record<string, string | number>);
}

export function stepLabel(step: SizeCalcStep): string {
  return t(`result.size.steps.${step.step_id}`, step.step_id);
}

export function stepDetail(step: SizeCalcStep): string {
  const key = `result.size.stepDetail.${step.step_id}`;
  const params: Record<string, string | number> = { ...(step.detail_params ?? {}) };
  if (step.bytes != null) params.bytes = step.bytes;
  if (step.step_id === "binary_si_total" && step.detail_params) {
    const s = Number(step.detail_params.s_bytes ?? 0);
    const i = Number(step.detail_params.i_bytes ?? 0);
    params.total = s + i;
    params.s_bytes = s;
    params.i_bytes = i;
  }
  return interpolate(t(key, step.step_id), params);
}

export function barStyle(pct: number): CSSProperties {
  return { "--size-bar-width": `${Math.max(3, pct)}%` } as CSSProperties;
}
