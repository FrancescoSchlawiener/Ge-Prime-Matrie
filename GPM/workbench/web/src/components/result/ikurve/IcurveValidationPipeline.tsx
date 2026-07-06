import { t } from "../../../i18n/t";
import { pct } from "../../../utils/format";
import { fmtEmpty } from "../../../lib/ikurve/format";

type PipelineStepId =
  | "nfc_tokenization"
  | "bitmask_prefilter"
  | "geometry_curves"
  | "enjambement_phase"
  | "meta_profile_audit";

interface IcurveValidationPipelineProps {
  pipeline: Record<string, unknown> | null | undefined;
}

const DETAIL_LABELS: Record<string, string> = {
  token_count_a: "ikurve.pipeline.detail.tokenCountA",
  token_count_b: "ikurve.pipeline.detail.tokenCountB",
  word_geometry_dtw: "ikurve.pipeline.detail.wordGeometryDtw",
  word_geometry_mae: "ikurve.pipeline.detail.wordGeometryMae",
  literal_match_ratio: "ikurve.pipeline.detail.literalMatch",
  cell_geometry: "ikurve.pipeline.detail.cellGeometry",
  substance_geometry: "ikurve.pipeline.detail.substanceGeometry",
  hierarchy_sentence_dtw: "ikurve.pipeline.detail.hierarchySentenceDtw",
  hierarchy_line_dtw: "ikurve.pipeline.detail.hierarchyLineDtw",
  meta_ggt_similarity: "ikurve.pipeline.detail.metaGgtSimilarity",
  profile_overlap: "ikurve.pipeline.detail.profileOverlap",
  shared_prime_count: "ikurve.pipeline.detail.sharedPrimeCount",
  rhythm_break_count_a: "ikurve.pipeline.detail.rhythmBreakCountA",
  rhythm_break_count_b: "ikurve.pipeline.detail.rhythmBreakCountB",
  rhythm_break_delta: "ikurve.pipeline.detail.rhythmBreakDelta",
  phase_shift_detected: "ikurve.pipeline.detail.phaseShift",
  relevant: "ikurve.pipeline.detail.relevant",
  basis_overlap: "ikurve.pipeline.detail.basisOverlap",
};

function stepLabel(id: string): string {
  const labels: Record<PipelineStepId, string> = {
    nfc_tokenization: t("ikurve.pipeline.step.nfc_tokenization"),
    bitmask_prefilter: t("ikurve.pipeline.step.bitmask_prefilter"),
    geometry_curves: t("ikurve.pipeline.step.geometry_curves"),
    enjambement_phase: t("ikurve.pipeline.step.enjambement_phase"),
    meta_profile_audit: t("ikurve.pipeline.step.meta_profile_audit"),
  };
  return labels[id as PipelineStepId] ?? id;
}

function statusLabel(status: string): string {
  if (status === "warn") return t("ikurve.pipeline.status.warn");
  if (status === "skip") return t("ikurve.pipeline.status.skip");
  return t("ikurve.pipeline.status.ok");
}

function statusIcon(status: string): string {
  if (status === "warn") return "⚠";
  if (status === "skip") return "○";
  return "✓";
}

function statusClass(status: string): string {
  if (status === "warn") return "gpm-ikurve-pipe-warn";
  if (status === "skip") return "gpm-ikurve-pipe-skip";
  return "gpm-ikurve-pipe-ok";
}

function formatDetailValue(key: string, value: unknown): string {
  if (typeof value === "boolean") return value ? t("ikurve.pipeline.status.ok") : t("ikurve.pipeline.status.skip");
  if (value == null) return fmtEmpty(value);
  if (
    key.endsWith("_dtw") ||
    key.endsWith("_mae") ||
    key.endsWith("_ratio") ||
    key === "profile_overlap" ||
    key === "meta_ggt_similarity"
  ) {
    const n = Number(value);
    if (Number.isFinite(n) && n <= 1 && n >= 0) return pct(n);
  }
  return String(value);
}

function renderDetailLines(detail: Record<string, unknown>): string[] {
  const lines: string[] = [];
  for (const [key, value] of Object.entries(detail)) {
    if (value == null || key === "nfc" || typeof value === "object") continue;
    const labelKey = DETAIL_LABELS[key];
    if (!labelKey) continue;
    lines.push(`${t(labelKey)}: ${formatDetailValue(key, value)}`);
  }
  return lines;
}

export function IcurveValidationPipeline({ pipeline }: IcurveValidationPipelineProps) {
  const steps = (pipeline?.steps as Array<Record<string, unknown>>) ?? [];
  if (!steps.length) {
    return <p className="gpm-metric__hint">{t("ikurve.validation.empty")}</p>;
  }

  return (
    <div className="gpm-ikurve-validation-pipeline">
      <h4 className="gpm-ikurve-zone__title">{t("ikurve.validation.title")}</h4>
      <ol className="gpm-ikurve-pipe-list">
        {steps.map((step) => {
          const status = String(step.status ?? "ok");
          const detail = (step.detail ?? {}) as Record<string, unknown>;
          const detailLines = renderDetailLines(detail);
          return (
            <li key={String(step.id)} className={`gpm-ikurve-pipe-step ${statusClass(status)}`}>
              <span className="gpm-ikurve-pipe-icon" aria-hidden>
                {statusIcon(status)}
              </span>
              <span className="gpm-ikurve-pipe-id">{stepLabel(String(step.id ?? ""))}</span>
              <span className="gpm-metric__hint">({statusLabel(status)})</span>
              {detailLines.length ? (
                <details className="gpm-ikurve-pipe-details">
                  <summary>{t("ikurve.validation.details")}</summary>
                  <ul className="gpm-step-lines">
                    {detailLines.map((line) => (
                      <li key={line}>{line}</li>
                    ))}
                  </ul>
                </details>
              ) : null}
            </li>
          );
        })}
      </ol>
    </div>
  );
}
