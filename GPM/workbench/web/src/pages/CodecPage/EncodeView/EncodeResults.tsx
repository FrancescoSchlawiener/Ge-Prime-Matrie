import { PedagogyStepList } from "../../../components/pedagogy";
import {
  BatchMetaBar,
  FailedItem,
  PanelActions,
  ResultPanel,
  ResultStack,
  SizeComparePanel,
  SummaryStrip,
  type SizeComparisonData,
} from "../../../components/result";
import { Button, Card } from "../../../components/ui";
import { t } from "../../../i18n/t";
import { formatBigInt } from "../../../utils/format";
import { encodeSummaryItems } from "./encodeSummary";
import type { EncodeWordResult, WordSizeState } from "./encodeTypes";
import { EMPTY_WORD_SIZE } from "./encodeTypes";

interface EncodeResultsProps {
  words: EncodeWordResult[];
  failed: string[];
  skipped: number;
  truncated: boolean;
  maxWords: number;
  wordSizes: Record<number, WordSizeState>;
  batchSize: { data: SizeComparisonData | null; loading: boolean; error: string | null };
  onBatchSizeCompare: () => void;
  onWordSizeCompare: (index: number, row: EncodeWordResult) => void;
  onCopyToDecode: (substance: number, index: number) => void;
}

export function EncodeResults({
  words,
  failed,
  skipped,
  truncated,
  maxWords,
  wordSizes,
  batchSize,
  onBatchSizeCompare,
  onWordSizeCompare,
  onCopyToDecode,
}: EncodeResultsProps) {
  const batchHints: string[] = [];
  const batchWarnings: string[] = [];
  if (skipped > 0) {
    batchHints.push(t("result.batch.skipped").replace("{count}", String(skipped)));
  }
  if (truncated) {
    batchWarnings.push(t("result.batch.truncated").replace("{max}", String(maxWords)));
  }

  return (
    <Card title={t("encode.resultTitle")}>
      {words.length > 0 ? (
        <>
          <BatchMetaBar
            primary={t("result.batch.encoded").replace("{count}", String(words.length))}
            hints={batchHints}
            warnings={batchWarnings}
          />
          <PanelActions>
            <Button type="button" variant="secondary" disabled={batchSize.loading} onClick={onBatchSizeCompare}>
              {batchSize.loading ? t("result.actions.sizeLoading") : t("result.actions.sizeBatch")}
            </Button>
          </PanelActions>
          <SizeComparePanel data={batchSize.data} loading={batchSize.loading} error={batchSize.error} />
        </>
      ) : null}
      <ResultStack>
        {words.map((row, i) => {
          const sizeState = wordSizes[i] ?? EMPTY_WORD_SIZE;
          return (
            <ResultPanel
              key={`${row.word}-${i}`}
              index={i + 1}
              title={row.word}
              brief={`S = ${formatBigInt(row.substance)} · I = ${formatBigInt(row.index)}`}
              defaultOpen={i === 0}
              summary={<SummaryStrip items={encodeSummaryItems(row)} />}
              actions={
                <PanelActions>
                  <Button type="button" variant="secondary" onClick={() => onCopyToDecode(row.substance, row.index)}>
                    {t("result.actions.copySi")}
                  </Button>
                  <Button
                    type="button"
                    variant="secondary"
                    data-testid={`size-word-btn-${i}`}
                    disabled={sizeState.loading}
                    onClick={() => onWordSizeCompare(i, row)}
                  >
                    {sizeState.loading ? t("result.actions.sizeLoading") : t("result.actions.sizeWord")}
                  </Button>
                </PanelActions>
              }
              footer={
                sizeState.data || sizeState.loading || sizeState.error ? (
                  <SizeComparePanel data={sizeState.data} loading={sizeState.loading} error={sizeState.error} />
                ) : null
              }
              body={row.steps?.length ? <PedagogyStepList steps={row.steps} variant="encode" /> : null}
            />
          );
        })}
        {failed.map((token) => (
          <FailedItem key={token} label={token} message={t("encode.failedToken")} />
        ))}
      </ResultStack>
    </Card>
  );
}
