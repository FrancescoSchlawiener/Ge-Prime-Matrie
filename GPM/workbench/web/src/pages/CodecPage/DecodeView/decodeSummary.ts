import type { SummaryItem } from "../../../components/result";
import { t } from "../../../i18n/t";
import { formatBigInt, formatLetters } from "../../../utils/format";

export function decodeSummaryItems(
  substance: number,
  index: number,
  ingredients: Record<string, number> | undefined,
  word: string,
): SummaryItem[] {
  const ingredientText = ingredients ? formatLetters(ingredients) : "—";
  return [
    { label: t("result.summary.substance"), value: formatBigInt(substance), mono: true },
    { label: t("result.summary.index"), value: formatBigInt(index), mono: true },
    { label: t("result.summary.ingredients"), value: ingredientText, mono: true },
    { label: t("result.summary.word"), value: word },
  ];
}

export interface DecodeResultData {
  word: string;
  substance: number;
  index: number;
  content_hash: string;
  ingredients?: Record<string, number>;
}
