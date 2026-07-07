import { t } from "../../../i18n/t";
import { pct, formatBigInt } from "../../../utils/format";

interface IcurveFusionTrioProps {
  data: Record<string, unknown>;
}

function num(v: unknown): number {
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
}

export function IcurveFusionTrio({ data }: IcurveFusionTrioProps) {
  const comparison = (data.comparison ?? {}) as Record<string, unknown>;
  const substCmp = (data.substance_comparison ?? comparison.substance_geometry ?? {}) as Record<
    string,
    unknown
  >;
  const cellCmp = (data.cell_comparison ?? comparison.cell_geometry ?? {}) as Record<string, unknown>;
  const wg = (comparison.word_geometry ?? {}) as Record<string, unknown>;
  const sumA = ((data.curve_a as Record<string, unknown>)?.summary ?? {}) as Record<string, unknown>;
  const sumB = ((data.curve_b as Record<string, unknown>)?.summary ?? {}) as Record<string, unknown>;
  const cellSumA = ((data.cell_geometry_a as Record<string, unknown>)?.summary ?? {}) as Record<
    string,
    unknown
  >;
  const cellSumB = ((data.cell_geometry_b as Record<string, unknown>)?.summary ?? {}) as Record<
    string,
    unknown
  >;

  const alignHint = comparison.aligned
    ? t("ikurve.fusion.hintAligned")
    : t("ikurve.fusion.hintOffset", { offset: formatBigInt(num(comparison.best_offset)) });

  const cards = [
    {
      key: "word",
      label: t("ikurve.fusion.word"),
      score: num(comparison.geometry_score),
      hints: [
        t("ikurve.fusion.hintDtw", {
          score: pct(num(wg.dtw_score ?? comparison.geometry_score_dtw)),
          literal: pct(num(comparison.literal_match_ratio)),
        }),
        alignHint,
        t("ikurve.fusion.hintDelta", {
          deltaA: pct(num(sumA.mean_delta_ratio)),
          deltaB: pct(num(sumB.mean_delta_ratio)),
        }),
      ],
    },
    {
      key: "substance",
      label: t("ikurve.fusion.substance"),
      score: num(substCmp.geometry_score),
      hints: [
        t("ikurve.fusion.hintSubstance", {
          twins: formatBigInt(num(substCmp.substance_twin_count)),
          shadows: formatBigInt(num(substCmp.anagram_shadow_count)),
        }),
        t("ikurve.fusion.hintSubstanceLen", {
          lenA: formatBigInt(num(substCmp.length_a)),
          lenB: formatBigInt(num(substCmp.length_b)),
          mean: pct(num(substCmp.mean_similarity)),
        }),
      ],
    },
    {
      key: "cell",
      label: t("ikurve.fusion.cell"),
      score: num(cellCmp.geometry_score),
      hints: [
        t("ikurve.fusion.hintCell", {
          matches: formatBigInt(num(cellCmp.match_count)),
        }),
        t("ikurve.fusion.hintCellLen", {
          lenA: formatBigInt(num(cellCmp.length_a ?? cellSumA.cell_count)),
          lenB: formatBigInt(num(cellCmp.length_b ?? cellSumB.cell_count)),
        }),
      ],
    },
  ];

  return (
    <div className="gpm-ikurve-fusion-trio" role="group" aria-label={t("ikurve.axis.title")}>
      {cards.map((card) => (
        <article key={card.key} className="gpm-ikurve-fusion-card">
          <h3 className="gpm-ikurve-fusion-card__label">{card.label}</h3>
          <p className="gpm-ikurve-fusion-card__score">{pct(card.score)}</p>
          {card.hints.map((hint) => (
            <p key={hint} className="gpm-ikurve-fusion-card__hint gpm-metric__hint">
              {hint}
            </p>
          ))}
        </article>
      ))}
    </div>
  );
}
