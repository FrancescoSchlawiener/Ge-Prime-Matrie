import { t } from "../../../i18n/t";

export type PairMode = "compare" | "diff" | "anagram";

export function parseMode(value: string | null): PairMode {
  if (value === "diff" || value === "anagram") return value;
  return "compare";
}

export function submitLabel(mode: PairMode): string {
  if (mode === "diff") return t("wortpaar.submitDiff");
  if (mode === "anagram") return t("wortpaar.submitAnagram");
  return t("wortpaar.submitCompare");
}

export function resultTitle(mode: PairMode): string {
  if (mode === "diff") return t("wortpaar.resultDiff");
  if (mode === "anagram") return t("wortpaar.resultAnagram");
  return t("wortpaar.resultCompare");
}

export function helpTitle(mode: PairMode): string {
  if (mode === "diff") return t("wortpaar.helpDiffTitle");
  if (mode === "anagram") return t("wortpaar.helpAnagramTitle");
  return t("wortpaar.helpCompareTitle");
}

export function helpBody(mode: PairMode): string {
  if (mode === "diff") return t("wortpaar.helpDiff");
  if (mode === "anagram") return t("wortpaar.helpAnagram");
  return t("wortpaar.helpCompare");
}

export function mapApiError(err: unknown): string {
  const msg = err instanceof Error ? err.message : String(err);
  if (msg.includes("roman_alpha_db_missing") || msg.includes("404")) {
    return t("wortpaar.anagramDbMissing");
  }
  if (msg.includes("not_roman_alpha")) {
    return t("wortpaar.anagramNotRomanAlpha");
  }
  return msg;
}
