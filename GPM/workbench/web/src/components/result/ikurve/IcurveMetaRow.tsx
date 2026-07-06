import { t } from "../../../i18n/t";
import { pct } from "../../../utils/format";
import { fmtEmpty } from "../../../lib/ikurve/format";

interface IcurveMetaRowProps {
  metaA: Record<string, unknown>;
  metaB: Record<string, unknown>;
  metaComparison: Record<string, unknown> | null | undefined;
}

function MetaGenomeCard({ label, meta }: { label: string; meta: Record<string, unknown> }) {
  const topWords = (meta.top_words as Array<{ word?: string; count?: number }>) ?? [];
  const vector = meta.vector as number[] | string | undefined;

  return (
    <div className="gpm-meta-genome-card">
      <div className="gpm-meta-genome-card__title">{label}</div>
      <dl className="gpm-letter-list">
        <dt>{t("ikurve.meta.vector")}</dt>
        <dd className="mono">
          {Array.isArray(vector) ? `[${vector.join(", ")}]` : fmtEmpty(vector)}
        </dd>
        <dt>{t("ikurve.meta.letterMass")}</dt>
        <dd className="mono">{fmtEmpty(meta.total_letter_mass)}</dd>
        <dt>{t("ikurve.meta.tokens")}</dt>
        <dd className="mono">{fmtEmpty(meta.token_count)}</dd>
        <dt>{t("ikurve.meta.unique")}</dt>
        <dd className="mono">{fmtEmpty(meta.unique_words)}</dd>
        <dt>{t("ikurve.meta.vectorBits")}</dt>
        <dd className="mono">{fmtEmpty(meta.vector_bits)}</dd>
        <dt>{t("ikurve.meta.primeFactors")}</dt>
        <dd className="mono">{fmtEmpty(meta.prime_factor_count)}</dd>
      </dl>
      {topWords.length ? (
        <p className="gpm-metric__hint">
          {t("ikurve.meta.topWords")}:{" "}
          {topWords
            .map((w) => `${w.word ?? t("ikurve.common.unknown")}(${w.count ?? 0})`)
            .join(t("ikurve.common.separator"))}
        </p>
      ) : null}
    </div>
  );
}

export function IcurveMetaRow({ metaA, metaB, metaComparison }: IcurveMetaRowProps) {
  const mc = metaComparison ?? {};
  const sharedPrimes = mc.heavy_shared_primes as Array<{ prime: number; letter: string; exponent: number }> | undefined;

  return (
    <div className="gpm-ikurve-meta-row">
      <div className="gpm-grid-2">
        <MetaGenomeCard label={t("ikurve.sideA")} meta={metaA} />
        <MetaGenomeCard label={t("ikurve.sideB")} meta={metaB} />
      </div>
      {sharedPrimes && sharedPrimes.length > 0 && (
        <div style={{ marginTop: "1rem" }}>
          <h4 className="gpm-ikurve-zone__title">{t("ikurve.meta.sharedPrimes")}</h4>
          <p className="gpm-metric__hint" style={{ marginTop: "0.25rem" }}>
            {sharedPrimes
              .map((p) => `${p.letter}^${p.exponent} (${p.prime})`)
              .join(t("ikurve.common.separator"))}
          </p>
        </div>
      )}
      {(mc.similarity_ratio != null || mc.ggt_kgv_similarity != null) ? (
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
