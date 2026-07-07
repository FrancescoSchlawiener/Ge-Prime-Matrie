import type { ChartScale } from "../../lib/ikurve/curves";
import { scaleBoundsY } from "../../lib/ikurve/chartLayout";

interface CurvePoint {
  i_ratio?: number;
  position?: number;
}

interface SparklineProps {
  curveA: CurvePoint[];
  curveB: CurvePoint[];
  labelA?: string;
  labelB?: string;
  chartScale?: ChartScale;
  valueKey?: string;
  indexKey?: string;
  ariaLabel?: string;
  emptyLabel?: string;
}

const VIEW_W = 640;
const VIEW_H = 120;
const PAD = 8;

export function Sparkline({
  curveA,
  curveB,
  labelA = "A",
  labelB = "B",
  chartScale = "union",
  valueKey = "i_ratio",
  indexKey = "position",
  ariaLabel,
  emptyLabel = "",
}: SparklineProps) {
  const valsA = curveA.map((p) => Number(p.i_ratio ?? 0));
  const valsB = curveB.map((p) => Number(p.i_ratio ?? 0));
  const { min, max } = scaleBoundsY(valsA, valsB, chartScale);
  const span = max - min || 1;

  const maxIndex = Math.max(
    curveA.reduce((m, p, i) => Math.max(m, Number(p.position ?? i)), 0),
    curveB.reduce((m, p, i) => Math.max(m, Number(p.position ?? i)), 0),
    1,
  );

  function pathFor(points: CurvePoint[]): string {
    if (!points.length) return "";
    return points
      .map((p, i) => {
        const idx = Number(p[indexKey as keyof CurvePoint] ?? p.position ?? i);
        const val = Number(p[valueKey as keyof CurvePoint] ?? p.i_ratio ?? 0);
        const x = PAD + (idx / maxIndex) * (VIEW_W - PAD * 2);
        const y = VIEW_H - PAD - ((val - min) / span) * (VIEW_H - PAD * 2);
        return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(" ");
  }

  const pathA = pathFor(curveA);
  const pathB = pathFor(curveB);

  if (!pathA && !pathB) {
    return <div className="gpm-empty">{emptyLabel}</div>;
  }

  return (
    <figure className="gpm-sparkline-figure">
      <svg className="gpm-sparkline" viewBox={`0 0 ${VIEW_W} ${VIEW_H}`} role="img" aria-label={ariaLabel ?? `${labelA} ${labelB}`}>
        {pathA ? <path className="gpm-sparkline__line gpm-sparkline__line--a" d={pathA} /> : null}
        {pathB ? <path className="gpm-sparkline__line gpm-sparkline__line--b" d={pathB} /> : null}
      </svg>
      <figcaption className="gpm-metric__hint gpm-sparkline__legend">
        <span className="gpm-sparkline__legend-a">{labelA}</span>
        <span className="gpm-sparkline__legend-b">{labelB}</span>
      </figcaption>
    </figure>
  );
}
