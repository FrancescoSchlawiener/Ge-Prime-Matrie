import { t } from "../../../i18n/t";
import { pct } from "../../../utils/format";
import { IcurveSignalOverview } from "./IcurveSignalOverview";
import { IcurveAxisScores } from "./IcurveAxisScores";
import { IcurveValidationPipeline } from "./IcurveValidationPipeline";
import { IcurveEnjambementBadge } from "./IcurveEnjambementBadge";
import { IcurveMetaRow } from "./IcurveMetaRow";

interface IcurveStructurePanelProps {
  data: Record<string, unknown>;
}

function translateSignalKey(key: string): string {
  const known: Record<string, string> = {
    word_parallel: t("ikurve.signals.keys.word_parallel"),
    relation_twins: t("ikurve.signals.keys.relation_twins"),
    meta_genome_strong: t("ikurve.signals.keys.meta_genome_strong"),
    substance_parallel: t("ikurve.signals.keys.substance_parallel"),
    structural_twin: t("ikurve.signals.keys.structural_twin"),
  };
  return known[key] ?? key;
}

export function IcurveStructurePanel({ data }: IcurveStructurePanelProps) {
  const structure = (data.structure_assessment ?? {}) as Record<string, unknown>;
  const comparison = (data.comparison ?? {}) as Record<string, unknown>;
  const pipeline = (data.validation_pipeline ?? {}) as Record<string, unknown>;
  const signals = (structure.signals as string[]) ?? [];
  const bullets = (structure.interpretation_bullets as string[]) ?? [];
  const isoIndex = Number(
    structure.isomorphism_index ?? pipeline.isomorphism_index ?? structure.combined_score ?? 0,
  );
  const classification = String(
    structure.classification ?? pipeline.classification ?? "",
  );

  return (
    <div className="gpm-ikurve-zone">
      <IcurveValidationPipeline pipeline={pipeline} />
      <IcurveSignalOverview data={data} />
      <IcurveAxisScores comparison={comparison} />

      <div className="gpm-ikurve-badges">
        {classification ? (
          <span className="gpm-ikurve-badge">
            {t("ikurve.classification")}: {classification}
          </span>
        ) : null}
        {structure.substance_parallel ? (
          <span className="gpm-ikurve-badge gpm-ikurve-badge--ok">
            {t("ikurve.signals.substanceParallel")}
          </span>
        ) : null}
        {structure.structural_twin ? (
          <span className="gpm-ikurve-badge gpm-ikurve-badge--ok">
            {t("ikurve.signals.structuralTwin")}
          </span>
        ) : null}
        {structure.relation_twins ? (
          <span className="gpm-ikurve-badge gpm-ikurve-badge--ok">
            {t("ikurve.signals.relationTwins")}
          </span>
        ) : null}
        {structure.meta_genome_strong ? (
          <span className="gpm-ikurve-badge gpm-ikurve-badge--ok">
            {t("ikurve.signals.metaGenomeStrong")}
          </span>
        ) : null}
        {comparison.structural_waveform_parallel ? (
          <span className="gpm-ikurve-badge gpm-ikurve-badge--ok">
            {t("ikurve.signals.wordParallel")}
          </span>
        ) : null}
      </div>

      <dl className="gpm-metric-grid" style={{ marginTop: "0.75rem" }}>
        <div className="gpm-metric">
          <dt className="gpm-metric__label">{t("ikurve.isomorphismIndex")}</dt>
          <dd className="gpm-metric__value">{pct(isoIndex)}</dd>
        </div>
      </dl>

      {bullets.length ? (
        <ul className="gpm-step-lines">
          {bullets.map((b) => (
            <li key={b}>{b}</li>
          ))}
        </ul>
      ) : structure.interpretation ? (
        <p>
          <strong>{String(structure.interpretation)}</strong>
        </p>
      ) : comparison.interpretation ? (
        <p>
          <strong>{String(comparison.interpretation)}</strong>
        </p>
      ) : null}

      {signals.length ? (
        <ul className="gpm-step-lines">
          {signals.map((s) => (
            <li key={s}>{translateSignalKey(s)}</li>
          ))}
        </ul>
      ) : null}

      <IcurveEnjambementBadge
        crossA={data.cross_analysis_a as Record<string, unknown>}
        crossB={data.cross_analysis_b as Record<string, unknown>}
        pipeline={pipeline}
      />

      <IcurveMetaRow
        metaA={(data.meta_a ?? {}) as Record<string, unknown>}
        metaB={(data.meta_b ?? {}) as Record<string, unknown>}
        metaComparison={data.meta_comparison as Record<string, unknown>}
      />
    </div>
  );
}
