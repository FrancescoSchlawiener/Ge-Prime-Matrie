import { t } from "../../../i18n/t";
import { pct } from "../../../utils/format";
import { scoreBarClass } from "../../../lib/ikurve/curves";

interface IcurveSignalOverviewProps {
  data: Record<string, unknown>;
}

export function IcurveSignalOverview({ data }: IcurveSignalOverviewProps) {
  const structure = (data.structure_assessment ?? {}) as Record<string, unknown>;
  const comparison = (data.comparison ?? {}) as Record<string, unknown>;
  const cellCmp = (data.cell_comparison ?? comparison.cell_geometry ?? {}) as Record<string, unknown>;
  const substCmp = (data.substance_comparison ?? comparison.substance_geometry ?? {}) as Record<
    string,
    unknown
  >;
  const relCmp = (data.relation_comparison ?? {}) as Record<string, unknown>;

  const segments = [
    { label: t("ikurve.signals.wordGeometry"), score: Number(comparison.geometry_score ?? 0) },
    {
      label: t("ikurve.signals.substanceGgt"),
      score: Number(substCmp.geometry_score ?? structure.substance_score ?? 0),
    },
    {
      label: t("ikurve.signals.cellLine"),
      score: Number(cellCmp.geometry_score ?? structure.cell_score ?? 0),
    },
    {
      label: t("ikurve.signals.relationTopology"),
      score: Number(relCmp.relation_score ?? structure.relation_score ?? 0),
    },
    { label: t("ikurve.signals.metaGgt"), score: Number(structure.meta_genome_similarity ?? 0) },
    { label: t("ikurve.signals.literalByte"), score: Number(comparison.literal_match_ratio ?? 0) },
  ];

  return (
    <div className="gpm-ikurve-signal-overview" role="group" aria-label={t("ikurve.aria.signalOverview")}>
      {segments.map((seg) => (
        <div key={seg.label} className={`gpm-ikurve-signal-segment ${scoreBarClass(seg.score)}`}>
          <span className="gpm-ikurve-signal-label">{seg.label}</span>
          <span className="gpm-ikurve-signal-value">{pct(seg.score)}</span>
          <span className="gpm-ikurve-signal-bar">
            <span style={{ width: `${Math.round(seg.score * 100)}%` }} />
          </span>
        </div>
      ))}
    </div>
  );
}
