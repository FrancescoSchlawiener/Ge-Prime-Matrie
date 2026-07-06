import { t } from "../../../i18n/t";
import { pct } from "../../../utils/format";
import { AXIS_SCORE_KEYS, scoreBarClass, type AxisScoreKey } from "../../../lib/ikurve/curves";

const AXIS_LABEL_KEYS: Record<AxisScoreKey, string> = {
  token_i: "ikurve.axis.tokenI",
  substance: "ikurve.axis.substance",
  cell_i: "ikurve.axis.cellI",
  hierarchy: "ikurve.axis.hierarchy",
  literal: "ikurve.axis.literal",
  hierarchy_sentence: "ikurve.axis.hierarchySentence",
  hierarchy_line: "ikurve.axis.hierarchyLine",
};

interface IcurveAxisScoresProps {
  comparison: Record<string, unknown> | null | undefined;
}

export function IcurveAxisScores({ comparison }: IcurveAxisScoresProps) {
  const axisScores = (comparison?.axis_scores ?? {}) as Record<string, number>;
  const hasScores = AXIS_SCORE_KEYS.some((k) => axisScores[k] != null);
  if (!hasScores) return null;

  return (
    <div className="gpm-ikurve-axis-scores" role="group" aria-label={t("ikurve.aria.axisScores")}>
      <h4 className="gpm-ikurve-zone__title">{t("ikurve.axis.title")}</h4>
      <div className="gpm-ikurve-signal-overview gpm-ikurve-signal-overview--axes">
        {AXIS_SCORE_KEYS.map((key) => {
          const score = Number(axisScores[key] ?? 0);
          return (
            <div key={key} className={`gpm-ikurve-signal-segment ${scoreBarClass(score)}`}>
              <span className="gpm-ikurve-signal-label">{t(AXIS_LABEL_KEYS[key])}</span>
              <span className="gpm-ikurve-signal-value">{pct(score)}</span>
              <span className="gpm-ikurve-signal-bar">
                <span style={{ width: `${Math.round(score * 100)}%` }} />
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
