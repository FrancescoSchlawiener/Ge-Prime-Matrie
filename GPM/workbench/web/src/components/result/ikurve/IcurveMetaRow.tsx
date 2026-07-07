import { t } from "../../../i18n/t";
import { DisclosureSection } from "../../ui/DisclosureSection";
import { SummaryStrip } from "../SummaryStrip";
import { pct } from "../../../utils/format";
import { fmtEmpty } from "../../../lib/ikurve/format";

const VECTOR_BRIEF_LIMIT = 128;

interface IcurveMetaRowProps {
  metaA: Record<string, unknown>;
  metaB: Record<string, unknown>;
  metaComparison: Record<string, unknown> | null | undefined;
}

function formatVector(vector: unknown): string {
  if (Array.isArray(vector)) return vector.join(", ");
  if (vector == null) return "";
  return String(vector);
}

function vectorBrief(full: string): string {
  if (full.length <= VECTOR_BRIEF_LIMIT) return full;
  return full.slice(0, VECTOR_BRIEF_LIMIT) + t("ikurve.common.ellipsis");
}

function MetaGenomeCard({ label, meta }: { label: string; meta: Record<string, unknown> }) {
  const topWords = (meta.top_words as Array<{ word?: string; count?: number }>) ?? [];
  const fullVector = formatVector(meta.vector);

  return (
    <div className="gpm-meta-genome-card gpm-meta-genome-card--compact">
      <div className="gpm-meta-genome-card__title">{label}</div>
      <SummaryStrip
        items={[
          { label: t("ikurve.meta.letterMass"), value: fmtEmpty(meta.total_letter_mass), mono: true },
          { label: t("ikurve.meta.tokens"), value: fmtEmpty(meta.token_count), mono: true },
          { label: t("ikurve.meta.unique"), value: fmtEmpty(meta.unique_words), mono: true },
          { label: t("ikurve.meta.vectorBits"), value: fmtEmpty(meta.vector_bits), mono: true },
          { label: t("ikurve.meta.primeFactors"), value: fmtEmpty(meta.prime_factor_count), mono: true },
        ]}
      />
      {topWords.length ? (
        <div className="gpm-ikurve-word-chips">
          {topWords.map((w) => (
            <span key={`${w.word}-${w.count}`} className="gpm-ikurve-word-chip">
              {w.word ?? t("ikurve.common.unknown")}({w.count ?? 0})
            </span>
          ))}
        </div>
      ) : null}
      {fullVector ? (
        <DisclosureSection
          level="nested"
          title={t("ikurve.details.vectorTitle")}
          brief={t("ikurve.details.vectorBrief", { preview: vectorBrief(fullVector) })}
        >
          <pre className="gpm-disclosure__scroll mono">{fullVector}</pre>
        </DisclosureSection>
      ) : null}
    </div>
  );
}

export function IcurveMetaRow({ metaA, metaB, metaComparison }: IcurveMetaRowProps) {
  const mc = metaComparison ?? {};
  const sharedPrimes = mc.heavy_shared_primes as
    | Array<{ prime: number; letter: string; exponent: number }>
    | undefined;

  return (
    <div className="gpm-ikurve-meta-row">
      <div className="gpm-grid-2">
        <MetaGenomeCard label={t("ikurve.sideA")} meta={metaA} />
        <MetaGenomeCard label={t("ikurve.sideB")} meta={metaB} />
      </div>
      {sharedPrimes && sharedPrimes.length > 0 ? (
        <div style={{ marginTop: "1rem" }}>
          <h4 className="gpm-ikurve-zone__title">{t("ikurve.meta.sharedPrimes")}</h4>
          <p className="gpm-metric__hint" style={{ marginTop: "0.25rem" }}>
            {sharedPrimes
              .map((p) => `${p.letter}^${p.exponent} (${p.prime})`)
              .join(t("ikurve.common.separator"))}
          </p>
        </div>
      ) : null}
      {mc.similarity_ratio != null || mc.ggt_kgv_similarity != null ? (
        <p className="gpm-metric__hint" style={{ marginTop: "0.5rem" }}>
          {t("ikurve.meta.comparisonHint")}
          {mc.similarity_ratio != null ? `: ${pct(Number(mc.similarity_ratio))}` : ""}
          {mc.similarity_ratio != null && mc.ggt_kgv_similarity != null
            ? t("ikurve.common.separator")
            : ""}
          {mc.ggt_kgv_similarity != null
            ? `${t("ikurve.meta.ggtKgv")}: ${pct(Number(mc.ggt_kgv_similarity))}`
            : ""}
        </p>
      ) : null}
    </div>
  );
}
