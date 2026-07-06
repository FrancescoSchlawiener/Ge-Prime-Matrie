import { t } from "../../../i18n/t";
import { pct } from "../../../utils/format";
import { SegmentToggle } from "../../ui";
import { PairedSparkline } from "./PairedSparkline";
import type {
  ChartScale,
  IcurveMode,
  SemanticDepth,
  StructuralDepth,
} from "../../../lib/ikurve/curves";
import {
  SEMANTIC_DEPTH_CONFIG,
  STRUCTURAL_DEPTH_CONFIG,
} from "../../../lib/ikurve/curves";
import { fmtTemplate, fmtPct } from "../../../lib/ikurve/format";

interface IcurveLensPanelProps {
  data: Record<string, unknown>;
  mode: IcurveMode;
  depth: SemanticDepth | StructuralDepth;
  chartScale: ChartScale;
  onModeChange: (mode: IcurveMode) => void;
  onDepthChange: (depth: SemanticDepth | StructuralDepth) => void;
  onChartScaleChange: (scale: ChartScale) => void;
}

export function IcurveLensPanel({
  data,
  mode,
  depth,
  chartScale,
  onModeChange,
  onDepthChange,
  onChartScaleChange,
}: IcurveLensPanelProps) {
  const comparison = (data.comparison ?? {}) as Record<string, unknown>;
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

  return (
    <div className="gpm-ikurve-zone">
      <SegmentToggle
        name="ikurve-mode"
        value={mode}
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
          <button
            type="button"
            className="gpm-ikurve-depth-btn gpm-ikurve-depth-active"
            aria-pressed
          >
            {t("ikurve.depth.line")}
          </button>
        </div>
      ) : null}

      <div className="gpm-ikurve-chart-scale" role="group" aria-label={t("ikurve.aria.chartScale")}>
        {(["union", "shorter"] as ChartScale[]).map((key) => (
          <button
            key={key}
            type="button"
            className={`gpm-ikurve-chart-scale-btn${chartScale === key ? " gpm-ikurve-chart-scale-active" : ""}`}
            aria-pressed={chartScale === key}
            onClick={() => onChartScaleChange(key)}
          >
            {t(`ikurve.chartScale.${key}`)}
          </button>
        ))}
      </div>

      {mode !== "atomic" ? (
        <p className="gpm-metric__hint">{t("ikurve.lensHint")}</p>
      ) : null}

      {mode === "atomic" ? (
        <>
          <PairedSparkline
            payloadA={data.curve_a as Record<string, unknown>}
            payloadB={data.curve_b as Record<string, unknown>}
            labelA={t("ikurve.sideA")}
            labelB={t("ikurve.sideB")}
            chartScale={chartScale}
          />
          <PairedSparkline
            payloadA={data.substance_a as Record<string, unknown>}
            payloadB={data.substance_b as Record<string, unknown>}
            valueKey="ggt_kgv_ratio"
            labelA={t("ikurve.substanceA")}
            labelB={t("ikurve.substanceB")}
            chartScale={chartScale}
          />
          <PairedSparkline
            payloadA={data.cell_geometry_a as Record<string, unknown>}
            payloadB={data.cell_geometry_b as Record<string, unknown>}
            valueKey="i_satz_ratio"
            labelA={t("ikurve.structuralA")}
            labelB={t("ikurve.structuralB")}
            chartScale={chartScale}
          />
        </>
      ) : null}

      {mode === "semantic" ? (
        <PairedSparkline
          payloadA={
            (data.semantic_a as Record<string, Record<string, unknown>>)?.[
              SEMANTIC_DEPTH_CONFIG[depth as SemanticDepth].dataKey
            ]
          }
          payloadB={
            (data.semantic_b as Record<string, Record<string, unknown>>)?.[
              SEMANTIC_DEPTH_CONFIG[depth as SemanticDepth].dataKey
            ]
          }
          valueKey={SEMANTIC_DEPTH_CONFIG[depth as SemanticDepth].ratioKey}
          labelA={fmtTemplate("ikurve.labels.sideDepth", {
            side: t("ikurve.sideShort.a"),
            depth: t(`ikurve.depth.${depth}`),
          })}
          labelB={fmtTemplate("ikurve.labels.sideDepth", {
            side: t("ikurve.sideShort.b"),
            depth: t(`ikurve.depth.${depth}`),
          })}
          chartScale={chartScale}
        />
      ) : null}

      {mode === "structural" ? (
        <PairedSparkline
          payloadA={(data.structural_a as Record<string, Record<string, unknown>>)?.lines}
          payloadB={(data.structural_b as Record<string, Record<string, unknown>>)?.lines}
          valueKey={STRUCTURAL_DEPTH_CONFIG.line.ratioKey}
          labelA={t("ikurve.structuralA")}
          labelB={t("ikurve.structuralB")}
          chartScale={chartScale}
        />
      ) : null}

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

      <dl className="gpm-metric-grid" style={{ marginTop: "1rem" }}>
        <div className="gpm-metric">
          <dt className="gpm-metric__label">{t("ikurve.metrics.fusion")}</dt>
          <dd className="gpm-metric__value">{fmtPct(comparison.geometry_score, pct)}</dd>
        </div>
        <div className="gpm-metric">
          <dt className="gpm-metric__label">{t("ikurve.metrics.wordDtw")}</dt>
          <dd className="gpm-metric__value">{fmtPct(comparison.geometry_score_dtw, pct)}</dd>
        </div>
        <div className="gpm-metric">
          <dt className="gpm-metric__label">{t("ikurve.metrics.literal")}</dt>
          <dd className="gpm-metric__value">{fmtPct(comparison.literal_match_ratio, pct)}</dd>
        </div>
      </dl>
    </div>
  );
}
