import { t } from "../../i18n/t";

export function fmtTemplate(key: string, vars: Record<string, string | number>): string {
  return t(key, vars);
}

export function fmtEmpty(v: unknown): string {
  if (v == null || v === "") return t("ikurve.common.noValue");
  return String(v);
}

export function fmtRatio(v: unknown): string {
  if (v == null) return t("ikurve.common.noValue");
  const n = Number(v);
  return Number.isFinite(n) ? n.toFixed(4) : String(v);
}

export function fmtPct(v: unknown, format: (n: number) => string): string {
  if (v == null) return t("ikurve.common.noValue");
  const n = Number(v);
  return Number.isFinite(n) ? format(n) : t("ikurve.common.noValue");
}

export function truncateText(text: string, maxLen = 40): string {
  if (text.length <= maxLen) return text;
  return text.slice(0, maxLen) + t("ikurve.common.ellipsis");
}
