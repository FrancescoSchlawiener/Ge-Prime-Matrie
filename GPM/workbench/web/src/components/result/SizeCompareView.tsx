import { t } from "../../i18n/t";
import {
  barStyle,
  formatBytes,
  formulaLabel,
  insightHeadline,
  insightPointText,
  rowLabel,
  rowSample,
  stepDetail,
  stepLabel,
  type SizeComparisonData,
} from "./sizeFormatters";

interface SizeCompareViewProps {
  data: SizeComparisonData;
}

const CATEGORY_ORDER = ["document", "gpm", "structured", "transport"] as const;

export function SizeCompareView({ data }: SizeCompareViewProps) {
  const highlights = new Set(data.highlight_ids ?? []);
  const insight = data.insight;
  const verdict = insight.verdict;

  const byCategory = new Map<string, typeof data.rows>();
  for (const row of data.rows) {
    const cat = row.category || "document";
    const list = byCategory.get(cat) ?? [];
    list.push(row);
    byCategory.set(cat, list);
  }

  return (
    <div className="gpm-size-compare" data-testid="size-compare">
      <div className={`gpm-size-insight gpm-size-insight--${verdict}`}>
        <div className="gpm-size-insight__badge">{t(`result.size.verdict.${verdict}`)}</div>
        <h3 className="gpm-size-insight__headline">{insightHeadline(data)}</h3>
        <p className="gpm-size-insight__baseline">
          {t("result.size.baselineRef")
            .replace("{label}", t("result.size.baselineLabel"))
            .replace("{bytes}", formatBytes(insight.baseline_bytes))}
        </p>
        {insight.points?.length ? (
          <ul className="gpm-size-insight__points">
            {insight.points.map((point) => (
              <li key={point.id}>{insightPointText(point, data.subject)}</li>
            ))}
          </ul>
        ) : null}
      </div>

      {CATEGORY_ORDER.filter((cat) => byCategory.has(cat)).map((cat) => (
        <section key={cat} className="gpm-size-category" data-testid={`size-category-${cat}`}>
          <h4 className="gpm-size-category__title">{t(`result.size.categories.${cat}`)}</h4>
          <div className="gpm-size-card-grid">
            {(byCategory.get(cat) ?? []).map((row) => {
              const cls = [
                "gpm-size-card",
                row.is_gpm ? "gpm-size-card--gpm" : "",
                highlights.has(row.id) ? "gpm-size-card--highlight" : "",
              ]
                .filter(Boolean)
                .join(" ");
              return (
                <article key={row.id} className={cls}>
                  <div className="gpm-size-card__head">
                    <div className="gpm-size-card__titles">
                      <div className="gpm-size-card__label">
                        {rowLabel(row)}
                        {row.ext ? <span className="gpm-size-card__ext">{row.ext}</span> : null}
                      </div>
                      <div className="gpm-size-card__human mono">{formatBytes(row.bytes)}</div>
                    </div>
                    <div className="gpm-size-card__bytes mono">{row.bytes} B</div>
                  </div>
                  <div className="gpm-size-bar" aria-hidden="true">
                    <div className="gpm-size-bar__fill" style={barStyle(row.pct_of_max)} />
                  </div>
                  {row.formula_id ? (
                    <div className="gpm-size-card__formula">{formulaLabel(row.formula_id)}</div>
                  ) : null}
                  {row.sample ? (
                    <div className="gpm-size-card__note">{rowSample(row)}</div>
                  ) : null}
                </article>
              );
            })}
          </div>
        </section>
      ))}

      <details className="gpm-size-details">
        <summary>{t("result.size.calcTitle")}</summary>
        <ol className="gpm-size-calc">
          {data.calculation.map((step) => (
            <li key={step.step_id}>
              <strong>{stepLabel(step)}</strong>
              {" — "}
              {stepDetail(step)}
              {step.bytes != null ? (
                <span className="mono"> {formatBytes(step.bytes)}</span>
              ) : null}
            </li>
          ))}
        </ol>
      </details>
    </div>
  );
}
