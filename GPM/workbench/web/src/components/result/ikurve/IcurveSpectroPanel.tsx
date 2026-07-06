import { t } from "../../../i18n/t";
import { Button } from "../../ui";
import type { TokenSelection } from "./GeometricMatrix";
import { fmtTemplate } from "../../../lib/ikurve/format";

interface IcurveSpectroPanelProps {
  docRef: string;
  selection: TokenSelection | null;
  onAnalyze: () => void;
  loading?: boolean;
}

export function IcurveSpectroPanel({ docRef, selection, onAnalyze, loading }: IcurveSpectroPanelProps) {
  if (!docRef) {
    return <p className="gpm-metric__hint">{t("ikurve.spectroNoDoc")}</p>;
  }

  const tokenStart = selection?.token_start ?? 0;
  const tokenEnd = selection ? selection.token_start + selection.token_count - 1 : 0;

  return (
    <div className="gpm-ikurve-spectro">
      <div className="gpm-form-row">
        <Button
          type="button"
          size="sm"
          disabled={loading || !selection}
          onClick={onAnalyze}
        >
          {loading ? t("ikurve.loading") : t("ikurve.spectroAnalyze")}
        </Button>
        <span className="gpm-metric__hint mono">
          {selection
            ? fmtTemplate("ikurve.spectro.tokenRange", {
                start: tokenStart,
                end: tokenEnd,
                count: selection.token_count,
              })
            : t("ikurve.spectroEmpty")}
        </span>
      </div>
    </div>
  );
}
