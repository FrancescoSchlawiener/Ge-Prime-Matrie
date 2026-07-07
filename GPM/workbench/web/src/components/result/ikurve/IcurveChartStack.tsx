import { memo } from "react";
import { t } from "../../../i18n/t";
import { Sparkline } from "../../ui";
import type { ChartLayout, ChartScale, SemanticDepth } from "../../../lib/ikurve/curves";
import {
  SEMANTIC_DEPTH_CONFIG,
  STRUCTURAL_DEPTH_CONFIG,
  curvePointCount,
  curvePoints,
  sparklineValue,
} from "../../../lib/ikurve/curves";
import { computePairedChartLayout, resolveSparklineEnd } from "../../../lib/ikurve/chartLayout";
import { fmtTemplate } from "../../../lib/ikurve/format";
import { IcurveChartCell } from "./IcurveChartCell";

interface ChartPairConfig {
  payloadA: Record<string, unknown> | null | undefined;
  payloadB: Record<string, unknown> | null | undefined;
  valueKey?: string;
  indexKey?: string;
  labelA: string;
  labelB: string;
}

interface IcurveChartStackProps {
  pairs: ChartPairConfig[];
  chartScale: ChartScale;
  chartLayout: ChartLayout;
}

function mapPoints(
  payload: Record<string, unknown> | null | undefined,
  valueKey: string,
  indexKey: string,
) {
  return curvePoints(payload as never).map((p) => ({
    value: sparklineValue(p, valueKey),
    index: Number(p[indexKey] ?? 0),
  }));
}

function StackedPair({ pair, chartScale }: { pair: ChartPairConfig; chartScale: ChartScale }) {
  const valueKey = pair.valueKey ?? "i_ratio";
  const indexKey = pair.indexKey ?? "position";
  const rawA = curvePoints(pair.payloadA as never);
  const rawB = curvePoints(pair.payloadB as never);
  const countA = curvePointCount(pair.payloadA as never);
  const countB = curvePointCount(pair.payloadB as never);
  const endA = resolveSparklineEnd(rawA, indexKey, countA || null);
  const endB = resolveSparklineEnd(rawB, indexKey, countB || null);
  const layout = computePairedChartLayout(endA, endB, chartScale, rawA.length, rawB.length);

  return (
    <div className="gpm-ikurve-chart-pair">
      <IcurveChartCell
        label={pair.labelA}
        points={rawA}
        valueKey={valueKey}
        indexKey={indexKey}
        layout={layout.a}
        side="a"
        emptyCount={countA}
      />
      <IcurveChartCell
        label={pair.labelB}
        points={rawB}
        valueKey={valueKey}
        indexKey={indexKey}
        layout={layout.b}
        side="b"
        emptyCount={countB}
      />
    </div>
  );
}

function OverlayPair({ pair, chartScale }: { pair: ChartPairConfig; chartScale: ChartScale }) {
  const valueKey = pair.valueKey ?? "i_ratio";
  const indexKey = pair.indexKey ?? "position";
  const ptsA = mapPoints(pair.payloadA, valueKey, indexKey);
  const ptsB = mapPoints(pair.payloadB, valueKey, indexKey);

  return (
    <Sparkline
      curveA={ptsA.map((p) => ({ i_ratio: p.value, position: p.index }))}
      curveB={ptsB.map((p) => ({ i_ratio: p.value, position: p.index }))}
      labelA={pair.labelA}
      labelB={pair.labelB}
      chartScale={chartScale}
      valueKey="i_ratio"
      indexKey="position"
      ariaLabel={fmtTemplate("ikurve.aria.sparklinePair", { a: pair.labelA, b: pair.labelB })}
      emptyLabel={t("ikurve.common.noValue")}
    />
  );
}

function IcurveChartStackInner({ pairs, chartScale, chartLayout }: IcurveChartStackProps) {
  const cellCount = chartLayout === "stacked" ? pairs.length * 2 : pairs.length;
  const scrollClass = cellCount > 4 ? " gpm-ikurve-charts-container--scroll" : "";

  return (
    <div className={`gpm-ikurve-charts-container${scrollClass}`}>
      <div className="gpm-ikurve-charts">
        {pairs.map((pair) =>
          chartLayout === "stacked" ? (
            <StackedPair key={`${pair.labelA}-${pair.labelB}`} pair={pair} chartScale={chartScale} />
          ) : (
            <div key={`${pair.labelA}-${pair.labelB}`} className="gpm-ikurve-chart-pair gpm-ikurve-chart-pair--overlay">
              <OverlayPair pair={pair} chartScale={chartScale} />
            </div>
          ),
        )}
      </div>
    </div>
  );
}

export const IcurveChartStack = memo(IcurveChartStackInner);

export function buildAtomicChartPairs(data: Record<string, unknown>): ChartPairConfig[] {
  return [
    {
      payloadA: data.curve_a as Record<string, unknown>,
      payloadB: data.curve_b as Record<string, unknown>,
      labelA: t("ikurve.chartLayout.curveA", { key: "i_ratio" }),
      labelB: t("ikurve.chartLayout.curveB", { key: "i_ratio" }),
    },
    {
      payloadA: data.substance_a as Record<string, unknown>,
      payloadB: data.substance_b as Record<string, unknown>,
      valueKey: "ggt_kgv_ratio",
      labelA: t("ikurve.chartLayout.curveA", { key: "ggt_kgv_ratio" }),
      labelB: t("ikurve.chartLayout.curveB", { key: "ggt_kgv_ratio" }),
    },
    {
      payloadA: data.cell_geometry_a as Record<string, unknown>,
      payloadB: data.cell_geometry_b as Record<string, unknown>,
      valueKey: "i_satz_ratio",
      indexKey: "cell_index",
      labelA: t("ikurve.chartLayout.curveA", { key: "i_satz_ratio" }),
      labelB: t("ikurve.chartLayout.curveB", { key: "i_satz_ratio" }),
    },
  ];
}

export function buildSemanticChartPair(
  data: Record<string, unknown>,
  depth: SemanticDepth,
): ChartPairConfig {
  const cfg = SEMANTIC_DEPTH_CONFIG[depth];
  return {
    payloadA: (data.semantic_a as Record<string, Record<string, unknown>>)?.[cfg.dataKey],
    payloadB: (data.semantic_b as Record<string, Record<string, unknown>>)?.[cfg.dataKey],
    valueKey: cfg.ratioKey,
    indexKey: cfg.indexKey,
    labelA: fmtTemplate("ikurve.labels.sideDepth", {
      side: t("ikurve.sideShort.a"),
      depth: t(`ikurve.depth.${depth}`),
    }),
    labelB: fmtTemplate("ikurve.labels.sideDepth", {
      side: t("ikurve.sideShort.b"),
      depth: t(`ikurve.depth.${depth}`),
    }),
  };
}

export function buildStructuralChartPair(data: Record<string, unknown>): ChartPairConfig {
  const cfg = STRUCTURAL_DEPTH_CONFIG.line;
  return {
    payloadA: (data.structural_a as Record<string, Record<string, unknown>>)?.lines,
    payloadB: (data.structural_b as Record<string, Record<string, unknown>>)?.lines,
    valueKey: cfg.ratioKey,
    indexKey: cfg.indexKey,
    labelA: t("ikurve.structuralA"),
    labelB: t("ikurve.structuralB"),
  };
}

export type { ChartPairConfig };
