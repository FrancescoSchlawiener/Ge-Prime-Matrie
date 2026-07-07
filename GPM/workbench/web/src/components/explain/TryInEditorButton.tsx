import { useNavigate } from "react-router-dom";
import { t } from "../../i18n/t";
import { saveGpmDraft } from "../../utils/sessionBridge";
import { Button } from "../ui/Button";

interface TryInEditorButtonProps {
  demoText: string;
}

export function TryInEditorButton({ demoText }: TryInEditorButtonProps) {
  const navigate = useNavigate();
  return (
    <Button
      variant="ghost"
      onClick={() => {
        saveGpmDraft({ text: demoText, exportName: "document" });
        navigate("/gpm");
      }}
    >
      {t("explain.cta.openGpm")}
    </Button>
  );
}
