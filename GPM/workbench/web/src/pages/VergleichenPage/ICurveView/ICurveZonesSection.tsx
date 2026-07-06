import {
  IcurveChainsPanel,
  IcurveLensPanel,
  IcurveStructurePanel,
} from "../../../components/result/ikurve";
import { Card, StepAccordion } from "../../../components/ui";
import { t } from "../../../i18n/t";
import type { ChartScale, IcurveMode, SemanticDepth, StructuralDepth } from "../../../lib/ikurve/curves";

interface ICurveZonesSectionProps {
  data: Record<string, unknown>;
  mode: IcurveMode;
  depth: SemanticDepth | StructuralDepth;
  chartScale: ChartScale;
  openZone: string | null;
  onOpenZone: (id: string | null) => void;
  onModeChange: (m: IcurveMode) => void;
  onDepthChange: (d: SemanticDepth | StructuralDepth) => void;
  onChartScaleChange: (s: ChartScale) => void;
}

export function ICurveZonesSection({
  data,
  mode,
  depth,
  chartScale,
  openZone,
  onOpenZone,
  onModeChange,
  onDepthChange,
  onChartScaleChange,
}: ICurveZonesSectionProps) {
  const zones = [
    {
      id: "structure",
      title: t("ikurve.zones.structure"),
      content: <IcurveStructurePanel data={data} />,
    },
    {
      id: "lens",
      title: t("ikurve.zones.lens"),
      content: (
        <IcurveLensPanel
          data={data}
          mode={mode}
          depth={depth}
          chartScale={chartScale}
          onModeChange={onModeChange}
          onDepthChange={onDepthChange}
          onChartScaleChange={onChartScaleChange}
        />
      ),
    },
    {
      id: "chains",
      title: t("ikurve.zones.chains"),
      content: <IcurveChainsPanel data={data} mode={mode} depth={depth} />,
    },
  ];

  return (
    <Card>
      <StepAccordion items={zones} openId={openZone} onToggle={(id) => onOpenZone(id || null)} />
    </Card>
  );
}
