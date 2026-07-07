import { t } from "../../../i18n/t";
import { DisclosureSection } from "../../ui";
import { AXIS_SCORE_KEYS } from "../../../lib/ikurve/curves";
import { IcurveValidationPipeline } from "./IcurveValidationPipeline";
import { IcurveSignalOverview } from "./IcurveSignalOverview";
import { IcurveAxisScores } from "./IcurveAxisScores";
import { IcurveStructurePanel } from "./IcurveStructurePanel";
import { IcurveMetaRow } from "./IcurveMetaRow";

interface IcurveExpertPanelProps {
  data: Record<string, unknown>;
}

export function IcurveExpertPanel({ data }: IcurveExpertPanelProps) {
  const pipeline = (data.validation_pipeline ?? {}) as Record<string, unknown>;
  const steps = (pipeline.steps as unknown[]) ?? [];
  const comparison = (data.comparison ?? {}) as Record<string, unknown>;
  const axisScores = (comparison.axis_scores ?? {}) as Record<string, number>;
  const hasAxis = AXIS_SCORE_KEYS.some((k) => axisScores[k] != null);
  const signalCount = 7 + (hasAxis ? AXIS_SCORE_KEYS.length : 0);
  const metaA = (data.meta_a ?? {}) as Record<string, unknown>;
  const metaB = (data.meta_b ?? {}) as Record<string, unknown>;

  return (
    <DisclosureSection
      title={t("ikurve.details.summary")}
      brief={t("ikurve.details.expertBrief", {
        steps: steps.length,
        signals: signalCount,
      })}
      defaultOpen={false}
    >
      <IcurveValidationPipeline pipeline={pipeline} />
      <DisclosureSection
        level="nested"
        title={t("ikurve.details.allSignals")}
        brief={t("ikurve.details.signalsBrief", { count: signalCount })}
      >
        <IcurveSignalOverview data={data} />
        <IcurveAxisScores comparison={comparison} />
      </DisclosureSection>
      <DisclosureSection
        level="nested"
        title={t("ikurve.details.metaGenome")}
        brief={t("ikurve.details.metaBrief", {
          tokensA: String(metaA.token_count ?? 0),
          tokensB: String(metaB.token_count ?? 0),
          uniqueA: String(metaA.unique_words ?? 0),
          uniqueB: String(metaB.unique_words ?? 0),
        })}
      >
        <IcurveMetaRow
          metaA={metaA}
          metaB={metaB}
          metaComparison={data.meta_comparison as Record<string, unknown>}
        />
      </DisclosureSection>
      <IcurveStructurePanel data={data} />
    </DisclosureSection>
  );
}
