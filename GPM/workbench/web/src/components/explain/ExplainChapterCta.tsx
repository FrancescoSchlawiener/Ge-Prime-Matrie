import { useNavigate } from "react-router-dom";
import type { ExplainArticleMeta } from "@gpm/ui-text/articles";
import { t } from "../../i18n/t";
import { saveGpmDraft } from "../../utils/sessionBridge";
import { Button } from "../ui/Button";
import { TryInCompareButton } from "./TryInCompareButton";

interface ExplainChapterCtaProps {
  cta: NonNullable<ExplainArticleMeta["cta"]>;
}

export function ExplainChapterCta({ cta }: ExplainChapterCtaProps) {
  const navigate = useNavigate();

  if (cta.type === "compare") {
    return (
      <div className="gpm-explain-cta">
        <TryInCompareButton wordA={cta.wordA ?? "LISTEN"} wordB={cta.wordB ?? "SILENT"} />
      </div>
    );
  }

  if (cta.type === "gpm") {
    return (
      <div className="gpm-explain-cta">
        <Button
          variant="ghost"
          onClick={() => {
            if (cta.demoText) saveGpmDraft({ text: cta.demoText, exportName: "document" });
            navigate("/gpm");
          }}
        >
          {t("explain.cta.openGpm")}
        </Button>
      </div>
    );
  }

  if (cta.type === "ikurve") {
    return (
      <div className="gpm-explain-cta">
        <Button variant="ghost" onClick={() => navigate("/vergleichen/ikurve")}>
          {t("explain.cta.openICurve")}
        </Button>
      </div>
    );
  }

  if (cta.type === "tensorraum") {
    return (
      <div className="gpm-explain-cta">
        <Button variant="ghost" onClick={() => navigate("/tensorraum")}>
          {t("explain.cta.openTensorraum")}
        </Button>
      </div>
    );
  }

  if (cta.type === "decode") {
    return (
      <div className="gpm-explain-cta">
        <Button variant="ghost" onClick={() => navigate("/codec/decodieren")}>
          {t("explain.cta.tryDecode")}
        </Button>
      </div>
    );
  }

  return (
    <div className="gpm-explain-cta">
      <Button variant="ghost" onClick={() => navigate("/codec/encodieren")}>
        {t("explain.cta.tryEncode")}
      </Button>
    </div>
  );
}
