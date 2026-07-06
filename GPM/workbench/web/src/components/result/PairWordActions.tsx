import { useNavigate } from "react-router-dom";
import { Button } from "../ui";
import { t } from "../../i18n/t";
import { saveDecodeDraft } from "../../utils/sessionBridge";
import {
  fetchSizeEncodeWord,
  SizeComparePanel,
  useSizeCompare,
} from "./SizeCompareSlot";

interface PairWordActionsProps {
  profile: string;
  original: string;
  normalized: string;
  substance: number;
  permIndex: number;
  contentHash?: string;
}

export function PairWordActions({
  profile,
  original,
  normalized,
  substance,
  permIndex,
  contentHash,
}: PairWordActionsProps) {
  const navigate = useNavigate();
  const size = useSizeCompare();

  function copyToDecode() {
    saveDecodeDraft(substance, permIndex);
    navigate("/codec/decodieren");
  }

  async function runSize() {
    if (!contentHash) return;
    await size.run(() =>
      fetchSizeEncodeWord(contentHash, profile, {
        original,
        normalized,
        substance,
        perm_index: permIndex,
      }),
    );
  }

  return (
    <div className="gpm-pair-actions">
      <div className="gpm-panel-actions">
        <Button type="button" variant="secondary" onClick={copyToDecode}>
          {t("result.actions.copySi")}
        </Button>
        {contentHash ? (
          <Button type="button" variant="secondary" disabled={size.loading} onClick={() => void runSize()}>
            {size.loading ? t("result.actions.sizeLoading") : t("result.actions.sizeWord")}
          </Button>
        ) : null}
      </div>
      <SizeComparePanel data={size.data} loading={size.loading} error={size.error} />
    </div>
  );
}
