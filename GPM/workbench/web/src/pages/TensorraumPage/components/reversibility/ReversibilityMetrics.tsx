import { t } from "../../../../i18n/t";
import type { FileReversibilityResult } from "../../../../lib/tensorraum";

interface ReversibilityMetricsProps {
  results: FileReversibilityResult[];
  visibleCount: number;
}

export function ReversibilityMetrics({ results, visibleCount }: ReversibilityMetricsProps) {
  const passed = results.filter((r) => r.verdict.ok).length;
  const maxDepth = results.reduce((m, r) => Math.max(m, r.maxDepth), 0);

  const items = [
    { key: "files", value: results.length },
    { key: "passed", value: passed },
    { key: "maxDepth", value: maxDepth },
    { key: "visible", value: `${visibleCount}/${results.length}` },
  ] as const;

  return (
    <div className="gpm-tensor-reversibility-metrics">
      {items.map((item) => (
        <div key={item.key} className="gpm-tensor-reversibility-metric">
          <span>{t(`tensorraum.reversibility.metrics.${item.key}`)}</span>
          <b>{item.value}</b>
        </div>
      ))}
    </div>
  );
}
