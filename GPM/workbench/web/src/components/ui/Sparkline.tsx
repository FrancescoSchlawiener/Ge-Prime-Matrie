export type ChartScale = "union" | "shorter";

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
  ariaLabel?: string;
  emptyLabel?: string;
}

function scaleBounds(curveA: CurvePoint[], curveB: CurvePoint[], chartScale: ChartScale) {
  const valsA = curveA.map((p) => p.i_ratio ?? 0);
  const valsB = curveB.map((p) => p.i_ratio ?? 0);
  if (chartScale === "shorter") {
    const ref = valsA.length <= valsB.length ? valsA : valsB;
    if (!ref.length) return { min: 0, max: 1 };
    return { min: Math.min(...ref), max: Math.max(...ref) };
  }
  const all = [...valsA, ...valsB];
  if (!all.length) return { min: 0, max: 1 };
  return { min: Math.min(...all), max: Math.max(...all) };
}

export function Sparkline({
  curveA,
  curveB,
  labelA = "A",
  labelB = "B",
  chartScale = "union",
  ariaLabel,
  emptyLabel = "",
}: SparklineProps) {
  const w = 640;
  const h = 120;
  const pad = 8;
  const { min, max } = scaleBounds(curveA, curveB, chartScale);
  const span = max - min || 1;

  function pathFor(points: CurvePoint[]): string {
    const vals = points.map((p) => p.i_ratio ?? 0);
    if (!vals.length) return "";
    return vals
      .map((v, i) => {
        const x = pad + (i / Math.max(vals.length - 1, 1)) * (w - pad * 2);
        const y = h - pad - ((v - min) / span) * (h - pad * 2);
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
    <figure>
      <svg className="gpm-sparkline" viewBox={`0 0 ${w} ${h}`} role="img" aria-label={ariaLabel ?? `${labelA} ${labelB}`}>
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
