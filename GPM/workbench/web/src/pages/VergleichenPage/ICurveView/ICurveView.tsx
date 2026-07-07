import { TabGuide } from "../../../components/ui";
import { Card } from "../../../components/ui";
import { t } from "../../../i18n/t";
import { IcurveIngestPanel } from "../../../components/result/ikurve";
import { IcurveChainsZone } from "../../../components/result/ikurve/IcurveChainsZone";
import { IcurveLensZone } from "../../../components/result/ikurve/IcurveLensZone";
import { IcurveStructureZone } from "../../../components/result/ikurve/IcurveStructureZone";
import { ICurveMatrixSection } from "./ICurveMatrixSection";
import { useICurveAnalysis } from "./useICurveAnalysis";

export function ICurveView() {
  const ic = useICurveAnalysis();

  return (
    <>
      <TabGuide>{t("ikurve.guide")}</TabGuide>
      <p className="gpm-metric__hint">{t("ikurve.decomposition")}</p>
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
        <div id="ikurve-results" className="gpm-ikurve-results">
          <Card>
            <IcurveStructureZone data={ic.data} />
          </Card>
          <Card>
            <IcurveLensZone
              data={ic.data}
              mode={ic.mode}
              depth={ic.depth}
              chartScale={ic.chartScale}
              chartLayout={ic.chartLayout}
              disabled={ic.busy}
              onModeChange={ic.setMode}
              onDepthChange={ic.setDepth}
              onChartScaleChange={ic.setChartScale}
              onChartLayoutChange={ic.setChartLayout}
            />
          </Card>
          <ICurveMatrixSection
            data={ic.data}
            curveMeta={ic.curveMeta}
            docRefA={ic.docRefA}
            docRefB={ic.docRefB}
            selA={ic.selA}
            selB={ic.selB}
            spectroA={ic.spectroA}
            spectroB={ic.spectroB}
            spectroLoading={ic.spectroLoading}
            onSelectionA={ic.setSelA}
            onSelectionB={ic.setSelB}
            onSpectroA={() => void ic.runSpectro("a")}
            onSpectroB={() => void ic.runSpectro("b")}
          />
          <Card>
            <IcurveChainsZone data={ic.data} mode={ic.mode} depth={ic.depth} />
          </Card>
        </div>
      ) : (
        <p className="gpm-empty">{t("ikurve.empty")}</p>
      )}
    </>
  );
}
