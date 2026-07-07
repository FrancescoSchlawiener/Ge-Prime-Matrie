import { computeICurve, computeLnNI, formatNI, toICurvePoints } from "../../../../lib/tensorraum";
import type { SequenceItem } from "../../../../lib/tensorraum";
import { t } from "../../../../i18n/t";

interface ResonanceSparklineProps {
  sequence: SequenceItem[];
}

const VIEW_W = 280;
const VIEW_H = 56;
const PAD = 4;

export function ResonanceSparkline({ sequence }: ResonanceSparklineProps) {
  const values = computeICurve(sequence);
  const points = toICurvePoints(values);
  const lnN = computeLnNI(sequence);
  const niLabel = formatNI(lnN);

  if (points.length < 2) {
    return (
      <div className="gpm-tensor-resonance-sparkline gpm-tensor-resonance-sparkline--empty">
        <span className="gpm-tensor-resonance-sparkline__ni">
          {t("tensorraum.redundancy.card.ni", { value: niLabel })}
        </span>
      </div>
    );
  }

  const ys = points.map((p) => p.i_ratio);
  const min = Math.min(...ys);
  const max = Math.max(...ys);
  const span = max - min || 1;
  const stepX = (VIEW_W - PAD * 2) / Math.max(1, points.length - 1);

  const d = points
    .map((p, i) => {
      const x = PAD + i * stepX;
      const y = PAD + (VIEW_H - PAD * 2) * (1 - (p.i_ratio - min) / span);
      return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");

  return (
    <div className="gpm-tensor-resonance-sparkline">
      <div className="gpm-tensor-resonance-sparkline__head">
        <span>{t("tensorraum.redundancy.card.icurve")}</span>
        <span className="gpm-tensor-resonance-sparkline__ni">
          {t("tensorraum.redundancy.card.ni", { value: niLabel })}
        </span>
      </div>
      <svg
        viewBox={`0 0 ${VIEW_W} ${VIEW_H}`}
        className="gpm-tensor-resonance-sparkline__svg"
        role="img"
        aria-label={t("tensorraum.redundancy.card.icurve")}
      >
        <path d={d} fill="none" stroke="var(--gpm-accent)" strokeWidth="1.5" />
      </svg>
    </div>
  );
}
