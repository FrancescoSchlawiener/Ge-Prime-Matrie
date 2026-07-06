import type { Step } from "../../../api/gpm-api";
import { PedagogyStepList } from "../../../components/pedagogy";
import {
  PairAnagramView,
  PairCompareView,
  PairDiffView,
  PanelActions,
  SizeComparePanel,
  type SizeComparisonData,
} from "../../../components/result";
import { Button, Card } from "../../../components/ui";
import { t } from "../../../i18n/t";
import { resultTitle, type PairMode } from "./wortpaarMode";

interface WortpaarResultsProps {
  mode: PairMode;
  result: Record<string, unknown>;
  steps: Step[];
  profile: string;
  batchSize: { data: SizeComparisonData | null; loading: boolean; error: string | null };
  onPairSizeBatch: () => void;
}

export function WortpaarResults({
  mode,
  result,
  steps,
  profile,
  batchSize,
  onPairSizeBatch,
}: WortpaarResultsProps) {
  return (
    <Card title={resultTitle(mode)}>
      {mode !== "anagram" ? (
        <>
          <PanelActions>
            <Button type="button" variant="secondary" disabled={batchSize.loading} onClick={onPairSizeBatch}>
              {batchSize.loading ? t("result.actions.sizeLoading") : t("result.actions.sizePairBatch")}
            </Button>
          </PanelActions>
          <SizeComparePanel data={batchSize.data} loading={batchSize.loading} error={batchSize.error} />
        </>
      ) : null}
      {mode === "compare" ? <PairCompareView data={result} profile={profile} /> : null}
      {mode === "diff" ? <PairDiffView data={result} profile={profile} /> : null}
      {mode === "anagram" ? <PairAnagramView data={result} profile={profile} /> : null}
      {steps.length > 0 ? (
        <div style={{ marginTop: "1rem" }}>
          <PedagogyStepList steps={steps} variant="encode" />
        </div>
      ) : null}
    </Card>
  );
}
