import { IcurveIngestPanel } from "../../../components/result/ikurve";
import { Card, TabGuide } from "../../../components/ui";
import { t } from "../../../i18n/t";
import { curvePointCount } from "../../../lib/ikurve/curves";
import { fmtEmpty } from "../../../lib/ikurve/format";
import { ICurveMatrixSection } from "./ICurveMatrixSection";
import { ICurveZonesSection } from "./ICurveZonesSection";
import { useICurveAnalysis } from "./useICurveAnalysis";

export function ICurveView() {
  const ic = useICurveAnalysis();

  return (
    <>
      <TabGuide>{t("ikurve.guide")}</TabGuide>
      <Card>
        <IcurveIngestPanel
          textA={ic.textA}
          textB={ic.textB}
          sourceA={ic.sourceA}
          sourceB={ic.sourceB}
          gpmNameA={ic.gpmNameA}
          gpmNameB={ic.gpmNameB}
          locked={ic.locked}
          loading={ic.loading}
          onTextA={ic.setTextA}
          onTextB={ic.setTextB}
          onSourceA={ic.setSourceA}
          onSourceB={ic.setSourceB}
          onGpmNameA={ic.setGpmNameA}
          onGpmNameB={ic.setGpmNameB}
          onSubmit={() => void ic.analyze()}
          onReset={ic.reset}
        />
      </Card>
      {ic.error ? <div className="gpm-error">{ic.error}</div> : null}
      {ic.data ? (
        <>
          <TabGuide>{t("ikurve.decomposition")}</TabGuide>
          <dl className="gpm-metric-grid gpm-ikurve-token-strip">
            <div className="gpm-metric">
              <dt className="gpm-metric__label">{t("ikurve.metrics.tokensA")}</dt>
              <dd className="gpm-metric__value">{fmtEmpty(curvePointCount(ic.data.curve_a as never))}</dd>
            </div>
            <div className="gpm-metric">
              <dt className="gpm-metric__label">{t("ikurve.metrics.tokensB")}</dt>
              <dd className="gpm-metric__value">{fmtEmpty(curvePointCount(ic.data.curve_b as never))}</dd>
            </div>
          </dl>
          <ICurveMatrixSection
            data={ic.data}
            curveMeta={ic.curveMeta}
            docRefA={ic.docRefA}
            docRefB={ic.docRefB}
            selA={ic.selA}
            selB={ic.selB}
            spectroA={ic.spectroA}
            spectroB={ic.spectroB}
            onSelectionA={ic.setSelA}
            onSelectionB={ic.setSelB}
            onSpectroA={() => void ic.runSpectro("a")}
            onSpectroB={() => void ic.runSpectro("b")}
          />
          <ICurveZonesSection
            data={ic.data}
            mode={ic.mode}
            depth={ic.depth}
            chartScale={ic.chartScale}
            openZone={ic.openZone}
            onOpenZone={ic.setOpenZone}
            onModeChange={ic.setMode}
            onDepthChange={ic.setDepth}
            onChartScaleChange={ic.setChartScale}
          />
        </>
      ) : (
        <p className="gpm-empty">{t("ikurve.empty")}</p>
      )}
    </>
  );
}
