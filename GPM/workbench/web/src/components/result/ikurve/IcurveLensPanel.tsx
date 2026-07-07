import { t } from "../../../i18n/t";
import type {
  ChartLayout,
  ChartScale,
  IcurveMode,
  SemanticDepth,
  StructuralDepth,
} from "../../../lib/ikurve/curves";
import {
  SEMANTIC_DEPTH_CONFIG,
  STRUCTURAL_DEPTH_CONFIG,
} from "../../../lib/ikurve/curves";
import { pct } from "../../../utils/format";
import { fmtTemplate } from "../../../lib/ikurve/format";
import { IcurveLevelMetrics } from "./IcurveLevelMetrics";
import {
  IcurveChartStack,
  buildAtomicChartPairs,
  buildSemanticChartPair,
  buildStructuralChartPair,
} from "./IcurveChartStack";
import { SegmentToggle } from "../../ui";

interface IcurveLensPanelProps {
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

export function IcurveLensPanel({
  data,
  mode,
  depth,
  chartScale,
  chartLayout,
  disabled = false,
  onModeChange,
  onDepthChange,
  onChartScaleChange,
  onChartLayoutChange,
}: IcurveLensPanelProps) {
  const hierarchy = (data.hierarchy_comparison ?? {}) as Record<
    string,
    Record<string, Record<string, unknown>>
  >;

  let dtwScore = 0;
  let dtwDepthKey = "";
  let dtwFailed = false;
  if (mode === "semantic") {
    const cfg = SEMANTIC_DEPTH_CONFIG[depth as SemanticDepth];
    const cmp = hierarchy.semantic?.[cfg.dtwKey];
    dtwScore = Number(cmp?.geometry_score ?? 0);
    dtwDepthKey = cfg.depthKey;
    dtwFailed = Boolean(cmp?.dtw_failed);
  } else if (mode === "structural") {
    const cfg = STRUCTURAL_DEPTH_CONFIG[depth as StructuralDepth];
    const cmp = hierarchy.structural?.[cfg.dtwKey];
    dtwScore = Number(cmp?.geometry_score ?? 0);
    dtwDepthKey = cfg.depthKey;
    dtwFailed = Boolean(cmp?.dtw_failed);
  }

  const depthLabel = dtwDepthKey ? t(`ikurve.depth.${dtwDepthKey}` as "ikurve.depth.phrase") : "";

  const chartPairs =
    mode === "atomic"
      ? buildAtomicChartPairs(data)
      : mode === "semantic"
        ? [buildSemanticChartPair(data, depth as SemanticDepth)]
        : [buildStructuralChartPair(data)];

  return (
    <div className="gpm-ikurve-zone">
      <IcurveLevelMetrics data={data} mode={mode} />

      <SegmentToggle
        name="ikurve-mode"
        value={mode}
        disabled={disabled}
        onChange={(v) => onModeChange(v as IcurveMode)}
        options={[
          { value: "atomic", label: t("ikurve.modes.atomic") },
          { value: "semantic", label: t("ikurve.modes.semantic") },
          { value: "structural", label: t("ikurve.modes.structural") },
        ]}
      />

      {mode === "semantic" ? (
        <div className="gpm-ikurve-depth-pills" role="group" aria-label={t("ikurve.aria.depth")}>
          {(Object.keys(SEMANTIC_DEPTH_CONFIG) as SemanticDepth[]).map((key) => (
            <button
              key={key}
              type="button"
              disabled={disabled}
              className={`gpm-ikurve-depth-btn${depth === key ? " gpm-ikurve-depth-active" : ""}`}
              aria-pressed={depth === key}
              onClick={() => onDepthChange(key)}
            >
              {t(`ikurve.depth.${key}`)}
            </button>
          ))}
        </div>
      ) : null}

      {mode === "structural" ? (
        <div className="gpm-ikurve-depth-pills" role="group" aria-label={t("ikurve.aria.depth")}>
          <button type="button" className="gpm-ikurve-depth-btn gpm-ikurve-depth-active" aria-pressed disabled>
            {t("ikurve.depth.line")}
          </button>
        </div>
      ) : null}

      <div className="gpm-ikurve-lens-controls">
        <div className="gpm-ikurve-chart-scale" role="group" aria-label={t("ikurve.aria.chartScale")}>
          {(["union", "shorter"] as ChartScale[]).map((key) => (
            <button
              key={key}
              type="button"
              disabled={disabled}
              className={`gpm-ikurve-chart-scale-btn${chartScale === key ? " gpm-ikurve-chart-scale-active" : ""}`}
              aria-pressed={chartScale === key}
              onClick={() => onChartScaleChange(key)}
            >
              {t(`ikurve.chartScale.${key}`)}
            </button>
          ))}
        </div>
        <div className="gpm-ikurve-chart-layout-toggle" role="group" aria-label={t("ikurve.chartLayout.legend")}>
          {(["overlay", "stacked"] as ChartLayout[]).map((key) => (
            <button
              key={key}
              type="button"
              disabled={disabled}
              className={`gpm-ikurve-chart-scale-btn${chartLayout === key ? " gpm-ikurve-chart-scale-active" : ""}`}
              aria-pressed={chartLayout === key}
              onClick={() => onChartLayoutChange(key)}
            >
              {t(`ikurve.chartLayout.${key}`)}
            </button>
          ))}
        </div>
      </div>

      {mode !== "atomic" ? <p className="gpm-metric__hint">{t("ikurve.lensHint")}</p> : null}

      <IcurveChartStack pairs={chartPairs} chartScale={chartScale} chartLayout={chartLayout} />

      {mode !== "atomic" ? (
        <p className="gpm-ikurve-dtw-line gpm-metric__hint">
          {dtwFailed ? (
            <span className="gpm-ikurve-dtw-failed" role="alert">
              {fmtTemplate("ikurve.labels.dtwDepth", { depth: depthLabel })}: {t("ikurve.dtw.failed")}
            </span>
          ) : (
            <>
              {t("ikurve.dtw.label")} ({depthLabel}): <strong>{pct(dtwScore)}</strong>
            </>
          )}
        </p>
      ) : null}
    </div>
  );
}
