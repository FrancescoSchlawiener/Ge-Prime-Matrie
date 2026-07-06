import { t } from "../../i18n/t";
import { formatBigInt, formatLetters, pct } from "../../utils/format";
import { PairWordCard, pairWordFromResult } from "./PairWordCard";
import { PairWordActions } from "./PairWordActions";

interface PairCompareViewProps {
  data: Record<string, unknown>;
  profile: string;
}

export function PairCompareView({ data, profile }: PairCompareViewProps) {
  const comparison = (data.comparison ?? {}) as Record<string, unknown>;
  const gcd = Number(comparison.gcd_value ?? 0);
  const lcm = Number(comparison.lcm_value ?? 0);
  const sim = Number(comparison.similarity_ratio ?? comparison.ggt_kgv_similarity ?? 0);
  const w1 = pairWordFromResult("1", data);
  const w2 = pairWordFromResult("2", data);

  return (
    <>
      <div className="gpm-grid-2">
        <PairWordCard
          {...w1}
          actions={
            <PairWordActions
              profile={profile}
              original={w1.original}
              normalized={w1.normalized}
              substance={w1.substance}
              permIndex={w1.permIndex}
              contentHash={String(data.content_hash1 ?? "") || undefined}
            />
          }
        />
        <PairWordCard
          {...w2}
          actions={
            <PairWordActions
              profile={profile}
              original={w2.original}
              normalized={w2.normalized}
              substance={w2.substance}
              permIndex={w2.permIndex}
              contentHash={String(data.content_hash2 ?? "") || undefined}
            />
          }
        />
      </div>
      <div className="gpm-compare-match-grid">
        <div className="gpm-compare-gcd-card">
          <span className="gpm-compare-card__label">{t("wortpaar.gcd")}</span>
          <span className="gpm-compare-card__value mono">{formatBigInt(gcd)}</span>
          <span className="gpm-compare-card__hint">{t("wortpaar.gcdHint")}</span>
          <span className="gpm-compare-card__hint">
            {t("wortpaar.similarity")}: {pct(sim)} · {t("wortpaar.similarityDetail")}
          </span>
        </div>
        <div className="gpm-compare-lcm-card">
          <span className="gpm-compare-card__label">{t("wortpaar.lcm")}</span>
          <span className="gpm-compare-card__value mono">{formatBigInt(lcm)}</span>
          <span className="gpm-compare-card__hint">{t("wortpaar.lcmHint")}</span>
          <span className="gpm-compare-card__hint mono">
            {t("wortpaar.lcmUnion")}: {formatLetters(comparison.union_letters as Record<string, number>)}
          </span>
        </div>
      </div>
      <div className="gpm-compare-letters">
        <LetterRow label={t("wortpaar.shared")} letters={comparison.shared_letters as Record<string, number>} />
        <LetterRow label={t("wortpaar.uniqueA")} letters={comparison.unique_to_first as Record<string, number>} />
        <LetterRow label={t("wortpaar.uniqueB")} letters={comparison.unique_to_second as Record<string, number>} />
        <LetterRow label={t("wortpaar.union")} letters={comparison.union_letters as Record<string, number>} />
      </div>
    </>
  );
}

function LetterRow({ label, letters }: { label: string; letters: Record<string, number> }) {
  return (
    <div className="gpm-compare-letters__row">
      <span className="gpm-compare-letters__label">{label}</span>
      <span className="gpm-compare-letters__value mono">{formatLetters(letters)}</span>
    </div>
  );
}
