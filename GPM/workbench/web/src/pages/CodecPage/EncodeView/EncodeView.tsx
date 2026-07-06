import { t } from "../../../i18n/t";
import { EncodeForm } from "./EncodeForm";
import { EncodeResults } from "./EncodeResults";
import { useEncodeBatch } from "./useEncodeBatch";

export function EncodeView() {
  const batch = useEncodeBatch();

  return (
    <>
      <EncodeForm
        text={batch.text}
        loading={batch.loading}
        onTextChange={batch.setText}
        onSubmit={(e) => void batch.submit(e)}
      />
      {batch.error ? <div className="gpm-error">{batch.error}</div> : null}
      {batch.hasResults ? (
        <EncodeResults
          words={batch.words}
          failed={batch.failed}
          skipped={batch.skipped}
          truncated={batch.truncated}
          maxWords={batch.maxWords}
          wordSizes={batch.wordSizes}
          batchSize={batch.batchSize}
          onBatchSizeCompare={() => void batch.runBatchSizeCompare()}
          onWordSizeCompare={(i, row) => void batch.runWordSizeCompare(i, row)}
          onCopyToDecode={batch.copyToDecode}
        />
      ) : (
        <p className="gpm-empty">{t("encode.empty")}</p>
      )}
    </>
  );
}
