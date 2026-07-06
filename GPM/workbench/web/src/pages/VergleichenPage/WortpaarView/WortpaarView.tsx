import { TabGuide } from "../../../components/ui";
import { t } from "../../../i18n/t";
import { useWortpaarPair } from "./useWortpaarPair";
import { WortpaarForm } from "./WortpaarForm";
import { WortpaarResults } from "./WortpaarResults";

export function WortpaarView() {
  const pair = useWortpaarPair();

  return (
    <>
      <TabGuide>{t("wortpaar.guide")}</TabGuide>
      <WortpaarForm
        mode={pair.mode}
        wordA={pair.wordA}
        wordB={pair.wordB}
        anagramWord={pair.anagramWord}
        loading={pair.loading}
        onModeChange={pair.setMode}
        onWordAChange={pair.setWordA}
        onWordBChange={pair.setWordB}
        onAnagramWordChange={pair.setAnagramWord}
        onSubmit={(e) => void pair.submit(e)}
      />
      {pair.error ? <div className="gpm-error">{pair.error}</div> : null}
      {pair.showResult && pair.result ? (
        <WortpaarResults
          mode={pair.mode}
          result={pair.result}
          steps={pair.steps}
          profile={pair.profile}
          batchSize={pair.batchSize}
          onPairSizeBatch={() => void pair.runPairSizeBatch()}
        />
      ) : null}
      {!pair.showResult && !pair.loading && !pair.error ? <p className="gpm-empty">{t("wortpaar.empty")}</p> : null}
    </>
  );
}
