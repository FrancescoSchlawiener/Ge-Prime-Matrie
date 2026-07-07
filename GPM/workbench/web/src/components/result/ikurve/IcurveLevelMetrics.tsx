import { t } from "../../../i18n/t";
import { pct, formatBigInt } from "../../../utils/format";

interface IcurveLevelMetricsProps {
  data: Record<string, unknown>;
  mode: "atomic" | "semantic" | "structural";
}

function num(v: unknown): number {
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
}

function LevelBlock({
  title,
  hint,
  tiles,
}: {
  title: string;
  hint: string;
  tiles: Array<{ label: string; value: string }>;
}) {
  return (
    <section className="gpm-ikurve-level-block">
      <header className="gpm-ikurve-level-head">
        <h4 className="gpm-ikurve-level-head__title">{title}</h4>
        <p className="gpm-metric__hint gpm-ikurve-level-head__hint">{hint}</p>
      </header>
      <div className="gpm-ikurve-level-metrics">
        {tiles.map((tile) => (
          <div key={tile.label} className="gpm-ikurve-level-metric">
            <span className="gpm-ikurve-level-metric__label">{tile.label}</span>
            <span className="gpm-ikurve-level-metric__value">{tile.value}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

export function IcurveLevelMetrics({ data, mode }: IcurveLevelMetricsProps) {
  if (mode !== "atomic") return null;

  const comparison = (data.comparison ?? {}) as Record<string, unknown>;
  const substCmp = (data.substance_comparison ?? comparison.substance_geometry ?? {}) as Record<
    string,
    unknown
  >;
  const cellCmp = (data.cell_comparison ?? comparison.cell_geometry ?? {}) as Record<string, unknown>;
  const wg = (comparison.word_geometry ?? {}) as Record<string, unknown>;
  const cellSumA = ((data.cell_geometry_a as Record<string, unknown>)?.summary ?? {}) as Record<
    string,
    unknown
  >;
  const cellSumB = ((data.cell_geometry_b as Record<string, unknown>)?.summary ?? {}) as Record<
    string,
    unknown
  >;

  return (
    <div className="gpm-ikurve-level-metrics-wrap">
      <LevelBlock
        title={t("ikurve.levels.word.title")}
        hint={t("ikurve.levels.word.hint")}
        tiles={[
          { label: t("ikurve.levels.word.dtw"), value: pct(num(comparison.geometry_score)) },
          {
            label: t("ikurve.levels.word.dtwMae"),
            value: `${pct(num(wg.dtw_score ?? comparison.geometry_score_dtw))} / ${pct(num(wg.mae_score ?? comparison.geometry_score_mae))}`,
          },
          { label: t("ikurve.levels.word.literal"), value: pct(num(comparison.literal_match_ratio)) },
        ]}
      />
      <LevelBlock
        title={t("ikurve.levels.substance.title")}
        hint={t("ikurve.levels.substance.hint")}
        tiles={[
          { label: t("ikurve.levels.substance.ggt"), value: pct(num(substCmp.geometry_score)) },
          {
            label: t("ikurve.levels.substance.twins"),
            value: formatBigInt(num(substCmp.substance_twin_count)),
          },
          {
            label: t("ikurve.levels.substance.shadows"),
            value: formatBigInt(num(substCmp.anagram_shadow_count)),
          },
        ]}
      />
      <LevelBlock
        title={t("ikurve.levels.cell.title")}
        hint={t("ikurve.levels.cell.hint")}
        tiles={[
          { label: t("ikurve.levels.cell.dtw"), value: pct(num(cellCmp.geometry_score)) },
          { label: t("ikurve.levels.cell.matches"), value: formatBigInt(num(cellCmp.match_count)) },
          {
            label: t("ikurve.levels.cell.count"),
            value: `${formatBigInt(num(cellCmp.length_a ?? cellSumA.cell_count))} / ${formatBigInt(num(cellCmp.length_b ?? cellSumB.cell_count))}`,
          },
        ]}
      />
    </div>
  );
}
