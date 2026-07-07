import { t } from "../../../i18n/t";
import { SummaryStrip } from "../SummaryStrip";
import { pct } from "../../../utils/format";
import { curvePointCount } from "../../../lib/ikurve/curves";

interface IcurveResultHeroProps {
  data: Record<string, unknown>;
}

export function IcurveResultHero({ data }: IcurveResultHeroProps) {
  const structure = (data.structure_assessment ?? {}) as Record<string, unknown>;
  const comparison = (data.comparison ?? {}) as Record<string, unknown>;
  const pipeline = (data.validation_pipeline ?? {}) as Record<string, unknown>;
  const isoIndex = Number(
    structure.isomorphism_index ?? pipeline.isomorphism_index ?? structure.combined_score ?? 0,
  );
  const classification = String(structure.classification ?? pipeline.classification ?? "");

  const badges: string[] = [];
  if (structure.structural_twin) badges.push(t("ikurve.signals.structuralTwin"));
  if (structure.meta_genome_strong) badges.push(t("ikurve.signals.metaGenomeStrong"));
  if (structure.substance_parallel) badges.push(t("ikurve.signals.substanceParallel"));
  if (comparison.structural_waveform_parallel) badges.push(t("ikurve.signals.wordParallel"));

  return (
    <section className="gpm-ikurve-hero" aria-labelledby="ikurve-hero-title">
      <div className="gpm-ikurve-hero__head">
        <h2 id="ikurve-hero-title" className="gpm-ikurve-hero__label">
          {t("ikurve.hero.isomorphism")}
        </h2>
        <p className="gpm-ikurve-hero__score">{pct(isoIndex)}</p>
        {classification ? (
          <p className="gpm-ikurve-hero__classification">
            {t("ikurve.classification")}: {classification}
          </p>
        ) : null}
      </div>
      <SummaryStrip
        items={[
          {
            label: t("ikurve.metrics.tokensA"),
            value: String(curvePointCount(data.curve_a as never)),
            mono: true,
          },
          {
            label: t("ikurve.metrics.tokensB"),
            value: String(curvePointCount(data.curve_b as never)),
            mono: true,
          },
          {
            label: t("ikurve.metrics.literal"),
            value: pct(Number(comparison.literal_match_ratio ?? 0)),
          },
          {
            label: t("ikurve.metrics.fusion"),
            value: pct(Number(comparison.geometry_score ?? 0)),
          },
        ]}
      />
      {badges.length ? (
        <div className="gpm-ikurve-badges">
          {badges.map((label) => (
            <span key={label} className="gpm-ikurve-badge gpm-ikurve-badge--ok">
              {label}
            </span>
          ))}
        </div>
      ) : null}
    </section>
  );
}
