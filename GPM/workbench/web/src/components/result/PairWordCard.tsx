import type { ReactNode } from "react";
import { t } from "../../i18n/t";
import { formatSiPair } from "../../utils/formatSi";

export interface PairWordData {
  original: string;
  normalized: string;
  substance: number;
  permIndex: number;
}

interface PairWordCardProps extends PairWordData {
  actions?: ReactNode;
}

export function PairWordCard({
  original,
  normalized,
  substance,
  permIndex,
  actions,
}: PairWordCardProps) {
  return (
    <div className="gpm-pair-word">
      <div className="gpm-pair-word__original">{original}</div>
      <div className="gpm-pair-word__norm">{normalized}</div>
      <div className="gpm-pair-word__si mono">{formatSiPair(substance, permIndex)}</div>
      {actions ? <div className="gpm-pair-word__actions">{actions}</div> : null}
    </div>
  );
}

export function pairWordFromResult(
  prefix: "1" | "2",
  data: Record<string, unknown>,
): PairWordData {
  const suffix = prefix;
  return {
    original: String(data[`word${suffix}`] ?? ""),
    normalized: String(data[`normalized${suffix}`] ?? data[`word${suffix}`] ?? ""),
    substance: Number(data[`substance${suffix}`] ?? 0),
    permIndex: Number(data[`perm_index${suffix}`] ?? 0),
  };
}

export function pairWordLabel(side: "1" | "2"): string {
  return side === "1" ? t("wortpaar.wordA") : t("wortpaar.wordB");
}
