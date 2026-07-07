import { useMemo, useState } from "react";
import { t } from "../../../i18n/t";
import { REVERSIBILITY_CARD_LIMIT, verifyProjectReversibility } from "../../../lib/tensorraum";
import { ReversibilityFileCard } from "../components/reversibility/ReversibilityFileCard";
import { ReversibilityMetrics } from "../components/reversibility/ReversibilityMetrics";
import type { TensorraumStore } from "../hooks/useTensorraumStore";

interface ReversibilityViewProps {
  store: TensorraumStore;
}

export function ReversibilityView({ store }: ReversibilityViewProps) {
  const project = store.project;
  const [showAll, setShowAll] = useState(false);

  const results = useMemo(() => {
    if (!project) return [];
    return verifyProjectReversibility(project.root.children, project.root.header.registry);
  }, [project]);

  const visible = showAll ? results : results.slice(0, REVERSIBILITY_CARD_LIMIT);
  const hasMore = results.length > REVERSIBILITY_CARD_LIMIT;

  if (!project) return null;

  return (
    <div className="gpm-tensor-reversibility">
      <header className="gpm-tensor-reversibility__head">
        <div>
          <h3>{t("tensorraum.reversibility.overviewTitle")}</h3>
          <p className="gpm-metric__hint">{t("tensorraum.reversibility.lead")}</p>
          <p className="gpm-metric__hint">{t("tensorraum.reversibility.overviewHint")}</p>
        </div>
        {results.length > 0 ? <ReversibilityMetrics results={results} visibleCount={visible.length} /> : null}
      </header>

      {results.length === 0 ? (
        <p className="gpm-empty">{t("tensorraum.reversibility.emptyNoFiles")}</p>
      ) : (
        <>
          <div className="gpm-tensor-reversibility-grid">
            {visible.map((result, idx) => (
              <ReversibilityFileCard key={result.file.id} result={result} defaultOpen={idx < 3} />
            ))}
          </div>
          {hasMore ? (
            <button
              type="button"
              className="gpm-btn gpm-tensor-reversibility-more"
              onClick={() => setShowAll((v) => !v)}
            >
              {showAll
                ? t("tensorraum.reversibility.showLess")
                : t("tensorraum.reversibility.showMore", { count: String(results.length) })}
            </button>
          ) : null}
        </>
      )}
    </div>
  );
}
