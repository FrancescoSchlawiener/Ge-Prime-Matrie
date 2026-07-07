import type { CurveMeta } from "../../../api/gpm-api";
import { GeometricMatrix, IcurveSpectroPanel } from "../../../components/result/ikurve";
import type { TokenSelection } from "../../../components/result/ikurve/GeometricMatrix";
import type { SpectroMatch } from "../../../lib/ikurve/spectro";
import { fmtTemplate } from "../../../lib/ikurve/format";
import { Card } from "../../../components/ui";
import { t } from "../../../i18n/t";

interface ICurveMatrixSectionProps {
  data: Record<string, unknown>;
  curveMeta: CurveMeta | null;
  docRefA: string;
  docRefB: string;
  selA: TokenSelection | null;
  selB: TokenSelection | null;
  spectroA: SpectroMatch[];
  spectroB: SpectroMatch[];
  spectroLoading?: boolean;
  onSelectionA: (sel: TokenSelection | null) => void;
  onSelectionB: (sel: TokenSelection | null) => void;
  onSpectroA: () => void;
  onSpectroB: () => void;
}

export function ICurveMatrixSection({
  data,
  curveMeta,
  docRefA,
  docRefB,
  selA,
  selB,
  spectroA,
  spectroB,
  spectroLoading = false,
  onSelectionA,
  onSelectionB,
  onSpectroA,
  onSpectroB,
}: ICurveMatrixSectionProps) {
  return (
    <Card title={t("ikurve.matrixTitle")}>
      <p className="gpm-metric__hint">{t("ikurve.spectroLegend")}</p>
      <div className="gpm-word-pair gpm-ikurve-matrix-pair">
        <div>
          <h4 className="gpm-ikurve-zone__title">{t("ikurve.matrixSideA")}</h4>
          <GeometricMatrix
            viewport={data.viewport_a as never}
            matches={spectroA}
            label={t("ikurve.matrixSideA")}
            onSelection={onSelectionA}
          />
        </div>
        <div>
          <h4 className="gpm-ikurve-zone__title">{t("ikurve.matrixSideB")}</h4>
          <GeometricMatrix
            viewport={data.viewport_b as never}
            matches={spectroB}
            label={t("ikurve.matrixSideB")}
            onSelection={onSelectionB}
          />
        </div>
      </div>
      <div className="gpm-word-pair" style={{ marginTop: "0.75rem" }}>
        <IcurveSpectroPanel docRef={docRefA} selection={selA} loading={spectroLoading} onAnalyze={onSpectroA} />
        <IcurveSpectroPanel docRef={docRefB} selection={selB} loading={spectroLoading} onAnalyze={onSpectroB} />
      </div>
      {curveMeta?.downsampled ? (
        <p className="gpm-metric__hint" role="status">
          {fmtTemplate("ikurve.hints.downsampled", {
            limit: curveMeta.limit,
            count: curveMeta.full_count,
          })}
        </p>
      ) : null}
    </Card>
  );
}
