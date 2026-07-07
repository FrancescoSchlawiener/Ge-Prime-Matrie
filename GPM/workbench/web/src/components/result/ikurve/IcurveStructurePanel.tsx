import { t } from "../../../i18n/t";
import { IcurveEnjambementBadge } from "./IcurveEnjambementBadge";

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

  return (
    <div className="gpm-ikurve-zone gpm-ikurve-structure-tail">
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
    </div>
  );
}
