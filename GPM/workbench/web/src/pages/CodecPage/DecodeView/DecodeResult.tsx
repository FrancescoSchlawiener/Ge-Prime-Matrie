import type { Step } from "../../../api/gpm-api";
import { PedagogyStepList } from "../../../components/pedagogy";
import { PanelActions, SizeComparePanel, SummaryStrip, type SizeComparisonData } from "../../../components/result";
import { Button, Card } from "../../../components/ui";
import { t } from "../../../i18n/t";
import { decodeSummaryItems, type DecodeResultData } from "./decodeSummary";

interface DecodeResultProps {
  result: DecodeResultData;
  steps: Step[];
  sizeCompare: { data: SizeComparisonData | null; loading: boolean; error: string | null };
  onSizeCompare: () => void;
}

export function DecodeResultCard({ result, steps, sizeCompare, onSizeCompare }: DecodeResultProps) {
  return (
    <Card title={t("decode.resultTitle")}>
      <SummaryStrip
        items={decodeSummaryItems(result.substance, result.index, result.ingredients, result.word)}
      />
      <PanelActions>
        <Button
          type="button"
          variant="secondary"
          data-testid="size-decode-btn"
          disabled={sizeCompare.loading}
          onClick={onSizeCompare}
        >
          {sizeCompare.loading ? t("result.actions.sizeLoading") : t("result.actions.sizeWord")}
        </Button>
      </PanelActions>
      <SizeComparePanel data={sizeCompare.data} loading={sizeCompare.loading} error={sizeCompare.error} />
      <PedagogyStepList steps={steps} variant="decode" />
    </Card>
  );
}
