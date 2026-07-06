import { TabGuide } from "../../../components/ui";
import { t } from "../../../i18n/t";
import { DecodeForm } from "./DecodeForm";
import { DecodeResultCard } from "./DecodeResult";
import { useDecodeWord } from "./useDecodeWord";

export function DecodeView() {
  const decode = useDecodeWord();

  return (
    <>
      <TabGuide>{t("decode.guide")}</TabGuide>
      <DecodeForm
        substance={decode.substance}
        index={decode.index}
        loading={decode.loading}
        onSubstanceChange={decode.setSubstance}
        onIndexChange={decode.setIndex}
        onSubmit={(e) => void decode.submit(e)}
      />
      {decode.error ? <div className="gpm-error">{decode.error}</div> : null}
      {decode.result ? (
        <DecodeResultCard
          result={decode.result}
          steps={decode.steps}
          sizeCompare={decode.sizeCompare}
          onSizeCompare={() => void decode.runSizeCompare()}
        />
      ) : (
        <p className="gpm-empty">{t("decode.empty")}</p>
      )}
    </>
  );
}
