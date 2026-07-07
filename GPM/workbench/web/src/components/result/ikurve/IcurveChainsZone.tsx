import { t } from "../../../i18n/t";
import { DisclosureSection } from "../../ui/DisclosureSection";
import type { IcurveMode, SemanticDepth, StructuralDepth } from "../../../lib/ikurve/curves";
import { IcurveChainsPanel } from "./IcurveChainsPanel";
import { IcurveDualPreview } from "./IcurveDualPreview";
import { IcurveMetaRow } from "./IcurveMetaRow";

interface IcurveChainsZoneProps {
  data: Record<string, unknown>;
  mode: IcurveMode;
  depth: SemanticDepth | StructuralDepth;
}

function tokenCount(data: Record<string, unknown>): number {
  const pipeline = (data.validation_pipeline ?? {}) as Record<string, unknown>;
  const steps = (pipeline.steps as Array<Record<string, unknown>>) ?? [];
  const nfc = steps.find((s) => s.id === "nfc_tokenization");
  const detail = (nfc?.detail ?? {}) as Record<string, unknown>;
  const a = Number(detail.token_count_a ?? 0);
  const b = Number(detail.token_count_b ?? 0);
  return Math.max(a, b, 0);
}

export function IcurveChainsZone({ data, mode, depth }: IcurveChainsZoneProps) {
  const count = tokenCount(data);
  const metaA = (data.meta_a ?? {}) as Record<string, unknown>;
  const metaB = (data.meta_b ?? {}) as Record<string, unknown>;

  return (
    <DisclosureSection
      title={t("ikurve.zones.chains")}
      brief={count ? t("ikurve.zones.chainsBrief", { count }) : undefined}
      defaultOpen={false}
    >
      <IcurveChainsPanel data={data} mode={mode} depth={depth} />
      <DisclosureSection
        level="nested"
        title={t("ikurve.details.metaGenome")}
        brief={t("ikurve.details.metaBrief", {
          tokensA: String(metaA.token_count ?? "—"),
          tokensB: String(metaB.token_count ?? "—"),
          uniqueA: String(metaA.unique_words ?? "—"),
          uniqueB: String(metaB.unique_words ?? "—"),
        })}
        defaultOpen={false}
      >
        <IcurveMetaRow
          metaA={metaA}
          metaB={metaB}
          metaComparison={data.meta_comparison as Record<string, unknown>}
        />
      </DisclosureSection>
      <DisclosureSection level="nested" title={t("ikurve.preview.title")} defaultOpen={false}>
        <IcurveDualPreview data={data} />
      </DisclosureSection>
    </DisclosureSection>
  );
}
