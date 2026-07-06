import { t } from "../../../i18n/t";
import { Sparkline } from "../../ui";
import type { ChartScale } from "../../../lib/ikurve/curves";
import { curvePoints, sparklineValue } from "../../../lib/ikurve/curves";
import { fmtTemplate } from "../../../lib/ikurve/format";

interface PairedSparklineProps {
  payloadA: Record<string, unknown> | null | undefined;
  payloadB: Record<string, unknown> | null | undefined;
  valueKey?: string;
  labelA?: string;
  labelB?: string;
  chartScale?: ChartScale;
}

export function PairedSparkline({
  payloadA,
  payloadB,
  valueKey = "i_ratio",
  labelA = t("ikurve.sideShort.a"),
  labelB = t("ikurve.sideShort.b"),
  chartScale = "union",
}: PairedSparklineProps) {
  const ptsA = curvePoints(payloadA as never).map((p) => ({
    i_ratio: sparklineValue(p, valueKey),
    position: Number(p.position ?? 0),
  }));
  const ptsB = curvePoints(payloadB as never).map((p) => ({
    i_ratio: sparklineValue(p, valueKey),
    position: Number(p.position ?? 0),
  }));
  return (
    <Sparkline
      curveA={ptsA}
      curveB={ptsB}
      labelA={labelA}
      labelB={labelB}
      chartScale={chartScale}
      ariaLabel={fmtTemplate("ikurve.aria.sparklinePair", { a: labelA, b: labelB })}
      emptyLabel={t("ikurve.common.noValue")}
    />
  );
}
