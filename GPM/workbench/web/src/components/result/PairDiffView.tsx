import { Badge } from "../ui";
import { t } from "../../i18n/t";
import { formatBigInt, formatLetters } from "../../utils/format";
import { PairWordCard, pairWordFromResult } from "./PairWordCard";
import { PairWordActions } from "./PairWordActions";

interface PairDiffViewProps {
  data: Record<string, unknown>;
  profile: string;
}

export function PairDiffView({ data, profile }: PairDiffViewProps) {
  const c = (data.classification ?? {}) as Record<string, unknown>;
  const gcd = Number(c.gcd_value ?? 0);
  const w1 = pairWordFromResult("1", data);
  const w2 = pairWordFromResult("2", data);

  return (
    <>
      <p className="mono gpm-metric__hint">{t("wortpaar.restFormula")}</p>
      <div className="gpm-grid-2" style={{ marginTop: "1rem" }}>
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
      <div className="gpm-summary-box gpm-diff-gcd" style={{ marginTop: "1rem" }}>
        <span className="gpm-summary-box__label">{t("wortpaar.gcd")}</span>
        <span className="gpm-summary-box__value mono">{formatBigInt(gcd)}</span>
      </div>
      <div className="gpm-compare-match-grid" style={{ marginTop: "1rem" }}>
        <RestCard
          title={t("wortpaar.restA")}
          value={Number(c.remainder_s1 ?? 0)}
          letters={c.remainder_letters_s1 as Record<string, number>}
          badge={Boolean(c.is_subset_1_in_2)}
          badgeLabel={t("wortpaar.badges.subset12")}
        />
        <RestCard
          title={t("wortpaar.restB")}
          value={Number(c.remainder_s2 ?? 0)}
          letters={c.remainder_letters_s2 as Record<string, number>}
          badge={Boolean(c.is_subset_2_in_1)}
          badgeLabel={t("wortpaar.badges.subset21")}
        />
      </div>
      <div className="gpm-diff-badges">
        <Badge active={Boolean(c.is_same_substance)}>{t("wortpaar.badges.sameSubstance")}</Badge>
        <Badge active={Boolean(c.is_anagram)}>{t("wortpaar.badges.anagram")}</Badge>
        <Badge active={Boolean(c.is_identical)}>{t("wortpaar.badges.identical")}</Badge>
        {c.same_length != null ? (
          <Badge active={Boolean(c.same_length)}>{t("wortpaar.badges.sameLength")}</Badge>
        ) : null}
      </div>
    </>
  );
}

function RestCard({
  title,
  value,
  letters,
  badge,
  badgeLabel,
}: {
  title: string;
  value: number;
  letters: Record<string, number>;
  badge: boolean;
  badgeLabel: string;
}) {
  return (
    <div className="gpm-diff-rest-card">
      <div className="gpm-compare-card__label">{title}</div>
      <div className="gpm-compare-card__value mono">{formatBigInt(value)}</div>
      <div className="gpm-compare-card__hint mono">{formatLetters(letters)}</div>
      <div style={{ marginTop: "0.35rem" }}>
        <Badge active={badge}>{badgeLabel}</Badge>
      </div>
    </div>
  );
}
