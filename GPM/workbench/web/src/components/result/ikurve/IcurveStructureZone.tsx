import { t } from "../../../i18n/t";
import { DisclosureSection } from "../../ui/DisclosureSection";
import { IcurveAxisScores } from "./IcurveAxisScores";
import { IcurveEnjambementBadge } from "./IcurveEnjambementBadge";
import { IcurveSignalOverview } from "./IcurveSignalOverview";
import { IcurveStructureMatrix } from "./IcurveStructureMatrix";
import { IcurveValidationPipeline } from "./IcurveValidationPipeline";

interface IcurveStructureZoneProps {
  data: Record<string, unknown>;
}

export function IcurveStructureZone({ data }: IcurveStructureZoneProps) {
  const pipeline = (data.validation_pipeline ?? {}) as Record<string, unknown>;
  const comparison = (data.comparison ?? {}) as Record<string, unknown>;
  const steps = (pipeline.steps as unknown[]) ?? [];

  return (
    <DisclosureSection
      title={t("ikurve.zones.structure")}
      brief={steps.length ? t("ikurve.zones.structureBrief", { steps: steps.length }) : undefined}
      defaultOpen
    >
      <IcurveValidationPipeline pipeline={pipeline} />
      <IcurveSignalOverview data={data} />
      <IcurveStructureMatrix data={data} />
      <IcurveEnjambementBadge
        crossA={data.cross_analysis_a as Record<string, unknown>}
        crossB={data.cross_analysis_b as Record<string, unknown>}
        pipeline={pipeline}
      />
      {comparison.interpretation ? (
        <p className="gpm-metric__hint">
          <strong>{String(comparison.interpretation)}</strong>
        </p>
      ) : null}
      <DisclosureSection
        level="nested"
        title={t("ikurve.axis.title")}
        brief={t("ikurve.details.signalsBrief", { count: 7 })}
        defaultOpen={false}
      >
        <IcurveAxisScores comparison={comparison} />
      </DisclosureSection>
    </DisclosureSection>
  );
}
