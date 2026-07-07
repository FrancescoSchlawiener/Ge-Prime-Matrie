import { t } from "../../../i18n/t";
import { DisclosureSection } from "../../ui/DisclosureSection";
import type {
  ChartLayout,
  ChartScale,
  IcurveMode,
  SemanticDepth,
  StructuralDepth,
} from "../../../lib/ikurve/curves";
import { IcurveLensPanel } from "./IcurveLensPanel";

interface IcurveLensZoneProps {
  data: Record<string, unknown>;
  mode: IcurveMode;
  depth: SemanticDepth | StructuralDepth;
  chartScale: ChartScale;
  chartLayout: ChartLayout;
  disabled?: boolean;
  onModeChange: (mode: IcurveMode) => void;
  onDepthChange: (depth: SemanticDepth | StructuralDepth) => void;
  onChartScaleChange: (scale: ChartScale) => void;
  onChartLayoutChange: (layout: ChartLayout) => void;
}

export function IcurveLensZone(props: IcurveLensZoneProps) {
  return (
    <DisclosureSection title={t("ikurve.zones.lens")} brief={t("ikurve.zones.lensBrief")} defaultOpen>
      <IcurveLensPanel {...props} />
    </DisclosureSection>
  );
}
