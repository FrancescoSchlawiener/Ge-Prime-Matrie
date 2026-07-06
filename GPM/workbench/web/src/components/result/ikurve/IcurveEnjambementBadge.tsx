import { t } from "../../../i18n/t";
import { pct, formatBigInt } from "../../../utils/format";
import { fmtEmpty, fmtTemplate } from "../../../lib/ikurve/format";

interface IcurveEnjambementBadgeProps {
  crossA: Record<string, unknown> | null | undefined;
  crossB: Record<string, unknown> | null | undefined;
  pipeline: Record<string, unknown> | null | undefined;
}

function shouldShowEnjambement(cross: Record<string, unknown> | null | undefined): boolean {
  if (!cross) return false;
  const profile = cross.enjambement_profile;
  return (
    Number(cross.rhythm_break_count ?? 0) > 0 ||
    profile === "rhythm_break" ||
    profile === "enjambement_noise"
  );
}

export function IcurveEnjambementBadge({ crossA, crossB, pipeline }: IcurveEnjambementBadgeProps) {
  const phase = (pipeline?.enjambement_phase ?? {}) as Record<string, unknown>;
  const show =
    shouldShowEnjambement(crossA) ||
    shouldShowEnjambement(crossB) ||
    Boolean(phase.phase_shift_detected);
  if (!show) return null;

  const countA = Number(phase.rhythm_break_count_a ?? crossA?.rhythm_break_count ?? 0);
  const countB = Number(phase.rhythm_break_count_b ?? crossB?.rhythm_break_count ?? 0);
  const delta = Number(phase.rhythm_break_delta ?? Math.abs(countA - countB));
  const profileA = String(phase.enjambement_profile_a ?? crossA?.enjambement_profile ?? "");
  const profileB = String(phase.enjambement_profile_b ?? crossB?.enjambement_profile ?? "");
  const ratioA =
    crossA?.line_aligned_ratio != null ? pct(Number(crossA.line_aligned_ratio)) : fmtEmpty(null);
  const ratioB =
    crossB?.line_aligned_ratio != null ? pct(Number(crossB.line_aligned_ratio)) : fmtEmpty(null);

  return (
    <div className="gpm-ikurve-badge gpm-ikurve-badge--purple" role="status">
      <strong>{t("ikurve.enjambement.title")}</strong>
      <p>
        {t("ikurve.enjambement.detail")}{" "}
        {fmtTemplate("ikurve.enjambement.breaks", {
          a: formatBigInt(countA),
          b: formatBigInt(countB),
          delta: formatBigInt(delta),
        })}
      </p>
      <p className="gpm-metric__hint">
        {t("ikurve.enjambement.profile")}{" "}
        {fmtTemplate("ikurve.enjambement.profileSide", {
          side: t("ikurve.sideShort.a"),
          value: profileA || fmtEmpty(profileA),
        })}
        {t("ikurve.common.separator")}
        {fmtTemplate("ikurve.enjambement.profileSide", {
          side: t("ikurve.sideShort.b"),
          value: profileB || fmtEmpty(profileB),
        })}
        {t("ikurve.common.separator")}
        {t("ikurve.enjambement.alignment")}{" "}
        {fmtTemplate("ikurve.enjambement.alignmentSide", {
          side: t("ikurve.sideShort.a"),
          value: ratioA,
        })}
        {t("ikurve.common.separator")}
        {fmtTemplate("ikurve.enjambement.alignmentSide", {
          side: t("ikurve.sideShort.b"),
          value: ratioB,
        })}
      </p>
    </div>
  );
}
