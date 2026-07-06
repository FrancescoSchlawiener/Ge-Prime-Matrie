import type { SummaryItem } from "../../../components/result";
import { t } from "../../../i18n/t";
import { formatBigInt } from "../../../utils/format";
import type { EncodeWordResult } from "./encodeTypes";

export function encodeSummaryItems(word: EncodeWordResult): SummaryItem[] {
  return [
    { label: t("result.summary.original"), value: word.word },
    { label: t("result.summary.normalized"), value: word.normalized },
    { label: t("result.summary.substance"), value: formatBigInt(word.substance), mono: true },
    { label: t("result.summary.index"), value: formatBigInt(word.index), mono: true },
  ];
}
