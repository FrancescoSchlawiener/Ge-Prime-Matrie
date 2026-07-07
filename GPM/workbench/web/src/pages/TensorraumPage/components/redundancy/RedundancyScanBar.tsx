import { t } from "../../../../i18n/t";
import type { TensorraumStore } from "../../hooks/useTensorraumStore";

interface RedundancyScanBarProps {
  store: TensorraumStore;
}

export function RedundancyScanBar({ store }: RedundancyScanBarProps) {
  const project = store.project;
  if (!project) return null;

  const windowLabel =
    store.windowMode === "adaptive"
      ? t("tensorraum.sidebar.windowAdaptiveRange")
      : t("tensorraum.sidebar.windowSize", { count: String(store.windowSize) });

  const structural = project.structuralOnly
    ? t("tensorraum.redundancy.scanParamsYes")
    : t("tensorraum.redundancy.scanParamsNo");

  const languages = project.crossLanguageAnalysis
    ? t("tensorraum.redundancy.scanParamsCross")
    : t("tensorraum.redundancy.scanParamsScoped");

  const scannedLabel =
    store.redundancyScan != null
      ? t("tensorraum.redundancy.scannedAt", {
          time: new Date(store.redundancyScan.scannedAt).toLocaleTimeString("de-DE"),
        })
      : null;

  return (
    <div className="gpm-tensor-resonance-scan">
      <div className="gpm-tensor-resonance-scan__copy">
        <h4>{t("tensorraum.redundancy.title")}</h4>
        <p className="gpm-metric__hint">{t("tensorraum.redundancy.lead")}</p>
        <p className="gpm-tensor-resonance-scan__params">
          {t("tensorraum.redundancy.scanParams", { window: windowLabel, structural, languages })}
        </p>
        {scannedLabel ? <p className="gpm-metric__hint">{scannedLabel}</p> : null}
      </div>
      <button type="button" className="gpm-tensor-cta" onClick={store.runRedundancyScan}>
        {store.redundancyScan ? t("tensorraum.redundancy.scanAgain") : t("tensorraum.redundancy.scan")}
      </button>
    </div>
  );
}
