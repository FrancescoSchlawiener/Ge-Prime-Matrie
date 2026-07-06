import type { ExplainWorkbenchStep } from "@gpm/ui-text/articles";
import { t } from "../../i18n/t";

interface ExplainWorkbenchPanelProps {
  steps?: ExplainWorkbenchStep[];
  tip?: string;
}

export function ExplainWorkbenchPanel({ steps, tip }: ExplainWorkbenchPanelProps) {
  if (!steps?.length) return null;
  return (
    <section className="gpm-explain-wb" aria-labelledby="explain-wb-title">
      <h2 id="explain-wb-title" className="gpm-explain-wb__title">
        {t("explain.workbench.title")}
      </h2>
      <div className="gpm-explain-wb__stack">
        {steps.map((s) => (
          <article key={`${s.where}-${s.action}`} className="gpm-explain-wb__card">
            <div className="gpm-explain-wb__where">{s.where}</div>
            <div className="gpm-explain-wb__action">{s.action}</div>
            <div className="gpm-explain-wb__outcome">
              <span className="gpm-explain-wb__outcome-label">{t("explain.workbench.outcome")}</span>
              {s.outcome}
            </div>
          </article>
        ))}
      </div>
      {tip ? <p className="gpm-explain-wb__tip">{tip}</p> : null}
    </section>
  );
}
