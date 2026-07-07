import { useEffect, useMemo, useState } from "react";
import { SegmentToggle } from "../../../components/ui/SegmentToggle";
import { t } from "../../../i18n/t";
import {
  REDUNDANCY_CARD_LIMIT,
  type BlockChain,
  type SentenceChain,
} from "../../../lib/tensorraum";
import { RedundancyChainCard } from "../components/redundancy/RedundancyChainCard";
import { RedundancyScanBar } from "../components/redundancy/RedundancyScanBar";
import type { TensorraumStore } from "../hooks/useTensorraumStore";

interface RedundancyViewProps {
  store: TensorraumStore;
}

export function RedundancyView({ store }: RedundancyViewProps) {
  const project = store.project;
  const [showAll, setShowAll] = useState(false);

  const hasFiles = (project?.root.children.length ?? 0) > 0;
  const scan = store.redundancyScan;
  const mode = store.redundancySubview;

  useEffect(() => {
    setShowAll(false);
  }, [mode, scan?.scannedAt]);

  const chains = useMemo((): (BlockChain | SentenceChain)[] => {
    if (!scan) return [];
    return mode === "block" ? scan.blockChains : scan.sentenceChains;
  }, [scan, mode]);

  const visible = showAll ? chains : chains.slice(0, REDUNDANCY_CARD_LIMIT);
  const hasMore = chains.length > REDUNDANCY_CARD_LIMIT;

  if (!project) return null;

  return (
    <div className="gpm-tensor-redundancy">
      <RedundancyScanBar store={store} />

      {!hasFiles ? (
        <p className="gpm-empty">{t("tensorraum.redundancy.emptyNoFiles")}</p>
      ) : !scan ? (
        <p className="gpm-empty">{t("tensorraum.redundancy.emptyNoScan")}</p>
      ) : (
        <>
          <div className="gpm-tensor-resonance-toolbar">
            <SegmentToggle
              name="redundancy-subview"
              value={mode}
              aria-label={t("tensorraum.redundancy.subview.aria")}
              options={[
                { value: "block", label: t("tensorraum.redundancy.subview.block") },
                { value: "sentence", label: t("tensorraum.redundancy.subview.sentence") },
              ]}
              onChange={store.setRedundancySubview}
            />
            <span className="gpm-tensor-resonance-toolbar__count">
              {t("tensorraum.redundancy.resultsCount", { count: String(chains.length) })}
            </span>
          </div>

          {chains.length === 0 ? (
            <p className="gpm-empty">{t("tensorraum.redundancy.emptyNoPatterns")}</p>
          ) : (
            <>
              <div className="gpm-tensor-resonance-grid">
                {visible.map((chain, idx) => (
                  <RedundancyChainCard
                    key={chain.hash}
                    rank={idx + 1}
                    mode={mode}
                    chain={chain}
                    registry={project.root.header.registry}
                  />
                ))}
              </div>
              {hasMore ? (
                <button
                  type="button"
                  className="gpm-btn gpm-tensor-resonance-more"
                  onClick={() => setShowAll((v) => !v)}
                >
                  {showAll
                    ? t("tensorraum.redundancy.showLess")
                    : t("tensorraum.redundancy.showMore", { count: String(chains.length) })}
                </button>
              ) : null}
            </>
          )}
        </>
      )}
    </div>
  );
}
