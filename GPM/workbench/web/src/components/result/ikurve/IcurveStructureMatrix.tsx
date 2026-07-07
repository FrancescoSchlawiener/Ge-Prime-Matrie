import { t } from "../../../i18n/t";
import { pct } from "../../../utils/format";
import { scoreBarClass } from "../../../lib/ikurve/curves";

interface IcurveStructureMatrixProps {
  data: Record<string, unknown>;
}

function translateSignalKey(key: string): string {
  const known: Record<string, string> = {
    word_parallel: t("ikurve.signals.keys.word_parallel"),
    relation_twins: t("ikurve.signals.keys.relation_twins"),
    meta_genome_strong: t("ikurve.signals.keys.meta_genome_strong"),
    substance_parallel: t("ikurve.signals.keys.substance_parallel"),
    structural_twin: t("ikurve.signals.keys.structural_twin"),
    fester_offset_erkannt: t("ikurve.structureMatrix.signals.fester_offset_erkannt"),
    elastische_streckung: t("ikurve.structureMatrix.signals.elastische_streckung"),
    hybride_modifikation: t("ikurve.structureMatrix.signals.hybride_modifikation"),
  };
  return known[key] ?? key;
}

function WordGeometryBadges({
  comparison,
  structure,
}: {
  comparison: Record<string, unknown>;
  structure: Record<string, unknown>;
}) {
  const badges: Array<{ key: string; label: string; className: string }> = [];
  if (comparison.fester_offset_erkannt || structure.fester_offset_erkannt) {
    badges.push({
      key: "offset",
      label: t("ikurve.badges.offset"),
      className: "gpm-ikurve-geo-badge gpm-ikurve-geo-badge--offset",
    });
  }
  if (comparison.elastische_streckung || structure.elastische_streckung) {
    badges.push({
      key: "stretch",
      label: t("ikurve.badges.stretch"),
      className: "gpm-ikurve-geo-badge gpm-ikurve-geo-badge--stretch",
    });
  }
  if (comparison.hybride_modifikation || structure.hybride_modifikation) {
    badges.push({
      key: "hybrid",
      label: t("ikurve.badges.hybrid"),
      className: "gpm-ikurve-geo-badge gpm-ikurve-geo-badge--hybrid",
    });
  }
  if (!badges.length) return null;

  return (
    <div className="gpm-ikurve-geo-badges" role="group" aria-label={t("ikurve.badges.aria")}>
      {badges.map((b) => (
        <span key={b.key} className={b.className}>
          {b.label}
        </span>
      ))}
    </div>
  );
}

export function IcurveStructureMatrix({ data }: IcurveStructureMatrixProps) {
  const structure = (data.structure_assessment ?? {}) as Record<string, unknown>;
  const comparison = (data.comparison ?? {}) as Record<string, unknown>;
  if (!Object.keys(structure).length) return null;

  const wordScore = Number(comparison.geometry_score ?? structure.geometry_score ?? 0);
  const substScore = Number(structure.substance_score ?? 0);
  const isoIndex = Number(structure.isomorphism_index ?? structure.combined_score ?? 0);
  const bullets = (structure.interpretation_bullets as string[]) ?? [];
  const signals = (structure.signals as string[]) ?? [];
  const pipeline = (data.validation_pipeline ?? {}) as Record<string, unknown>;

  const kombi = [
    { label: t("ikurve.isomorphismIndex"), value: isoIndex },
    { label: t("ikurve.signals.cellLine"), value: Number(structure.cell_score ?? 0) },
    { label: t("ikurve.signals.relationTopology"), value: Number(structure.relation_score ?? 0) },
    { label: t("ikurve.signals.metaGgt"), value: Number(structure.meta_genome_similarity ?? 0) },
  ];

  return (
    <div className="gpm-ikurve-structure-matrix">
      <h4 className="gpm-ikurve-zone__title">{t("ikurve.structureMatrix.title")}</h4>
      <WordGeometryBadges comparison={comparison} structure={structure} />

      <div className="gpm-ikurve-plag-score-bars">
        <div className={`gpm-ikurve-plag-score-row ${scoreBarClass(wordScore)}`}>
          <span className="gpm-ikurve-plag-score-label">{t("ikurve.signals.wordGeometry")}</span>
          <span className="gpm-ikurve-plag-score-value">{pct(wordScore)}</span>
          <span className="gpm-ikurve-plag-score-bar">
            <span style={{ width: `${Math.round(wordScore * 100)}%` }} />
          </span>
        </div>
        <div className={`gpm-ikurve-plag-score-row ${scoreBarClass(substScore)}`}>
          <span className="gpm-ikurve-plag-score-label">{t("ikurve.signals.substanceGgt")}</span>
          <span className="gpm-ikurve-plag-score-value">{pct(substScore)}</span>
          <span className="gpm-ikurve-plag-score-bar">
            <span style={{ width: `${Math.round(substScore * 100)}%` }} />
          </span>
        </div>
      </div>

      {bullets.length ? (
        <ul className="gpm-step-lines gpm-ikurve-interpret-bullets">
          {bullets.map((b) => (
            <li key={b}>{b}</li>
          ))}
        </ul>
      ) : structure.interpretation ? (
        <p>
          <strong>{String(structure.interpretation)}</strong>
        </p>
      ) : null}

      <div className="gpm-ikurve-kombi-grid">
        {kombi.map((item) => (
          <div key={item.label} className="gpm-ikurve-metric-card">
            <div className="gpm-ikurve-metric-card__label">{item.label}</div>
            <div className="gpm-ikurve-metric-card__value">{pct(item.value)}</div>
          </div>
        ))}
      </div>

      {signals.length ? (
        <ul className="gpm-step-lines">
          {signals.map((s) => (
            <li key={s}>{translateSignalKey(s)}</li>
          ))}
        </ul>
      ) : null}

      {pipeline.classification ? (
        <p className="gpm-metric__hint">
          {t("ikurve.classification")}: <strong>{String(pipeline.classification)}</strong>
          {t("ikurve.common.separator")}
          {t("ikurve.isomorphismIndex")} {pct(Number(pipeline.isomorphism_index ?? isoIndex))}
        </p>
      ) : null}
    </div>
  );
}
