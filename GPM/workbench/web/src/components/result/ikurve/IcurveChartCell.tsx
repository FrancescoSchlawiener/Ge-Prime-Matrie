import { t } from "../../../i18n/t";
import {
  SPARKLINE_VIEWBOX_W,
  type ChartCellLayout,
} from "../../../lib/ikurve/chartLayout";
import { sparklineValue } from "../../../lib/ikurve/curves";

const CHART_HEIGHT = 90;
const CHART_PAD = 6;

interface IcurveChartCellProps {
  label: string;
  points: Array<Record<string, unknown>>;
  valueKey?: string;
  indexKey?: string;
  layout: ChartCellLayout;
  side: "a" | "b";
  emptyCount?: number;
}

export function IcurveChartCell({
  label,
  points,
  valueKey = "i_ratio",
  indexKey = "position",
  layout,
  side,
  emptyCount = 0,
}: IcurveChartCellProps) {
  if (!points.length) {
    return (
      <div className="gpm-ikurve-chart-cell" data-ikurve-side={side}>
        <span className="gpm-ikurve-chart-label">{label}</span>
        <p className="gpm-metric__hint">{t("ikurve.chartLayout.empty", { count: emptyCount })}</p>
      </div>
    );
  }

  const viewBoxW = SPARKLINE_VIEWBOX_W * layout.widthRatio;
  const maxX = Math.max(layout.maxIndex, 1);
  const strokeClass =
    side === "a" ? "gpm-ikurve-sparkline gpm-ikurve-sparkline--a" : "gpm-ikurve-sparkline gpm-ikurve-sparkline--b";
  const extendedClass = layout.widthRatio > 1 ? " gpm-ikurve-sparkline--extended" : "";

  function toPath(): string {
    if (points.length === 1) {
      const val = Math.max(sparklineValue(points[0], valueKey), 0);
      const y = CHART_HEIGHT - CHART_PAD - val * (CHART_HEIGHT - 2 * CHART_PAD);
      return `M${CHART_PAD},${y.toFixed(1)} L${(viewBoxW - CHART_PAD).toFixed(1)},${y.toFixed(1)}`;
    }
    return points
      .map((p, i) => {
        const x = CHART_PAD + (Number(p[indexKey] ?? i) / maxX) * (viewBoxW - 2 * CHART_PAD);
        const val = Math.max(sparklineValue(p, valueKey), 0);
        const y = CHART_HEIGHT - CHART_PAD - val * (CHART_HEIGHT - 2 * CHART_PAD);
        return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(" ");
  }

  const svg = (
    <svg
      className={`${strokeClass}${extendedClass}`}
      style={layout.widthRatio > 1 ? { width: `${layout.widthRatio * 100}%`, minWidth: "100%" } : undefined}
      viewBox={`0 0 ${viewBoxW} ${CHART_HEIGHT}`}
      preserveAspectRatio="none"
      aria-hidden
    >
      <path fill="none" stroke="currentColor" strokeWidth="1.5" d={toPath()} />
    </svg>
  );

  return (
    <div className="gpm-ikurve-chart-cell" data-ikurve-side={side}>
      <span className="gpm-ikurve-chart-label">{label}</span>
      {layout.scrollable ? (
        <div
          className="gpm-ikurve-sparkline-scroll"
          tabIndex={0}
          aria-label={t("ikurve.chartLayout.scrollHint")}
        >
          {svg}
        </div>
      ) : (
        svg
      )}
      {layout.scrollable ? (
        <span className="gpm-metric__hint gpm-ikurve-scroll-hint">{t("ikurve.chartLayout.scrollHint")}</span>
      ) : null}
    </div>
  );
}
