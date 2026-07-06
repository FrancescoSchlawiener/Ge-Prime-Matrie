import { useNavigate } from "react-router-dom";
import { t } from "../../i18n/t";
import { saveWordPairDraft } from "../../utils/sessionBridge";
import { Button } from "../ui/Button";

interface TryInCompareButtonProps {
  wordA: string;
  wordB: string;
}

export function TryInCompareButton({ wordA, wordB }: TryInCompareButtonProps) {
  const navigate = useNavigate();
  return (
    <Button
      variant="ghost"
      onClick={() => {
        saveWordPairDraft(wordA, wordB);
        navigate("/vergleichen/wortpaar?mode=compare");
      }}
    >
      {t("explain.cta.tryWordPair")}
    </Button>
  );
}
