import { t } from "../../../../i18n/t";
import type { FileReversibilityResult } from "../../../../lib/tensorraum";
import { LineNumberedCode } from "./LineNumberedCode";

interface ReversibilityFileCardProps {
  result: FileReversibilityResult;
  defaultOpen?: boolean;
}

export function ReversibilityFileCard({ result, defaultOpen = false }: ReversibilityFileCardProps) {
  const { file, decompiled, verdict } = result;
  const ok = verdict.ok;

  return (
    <details className="gpm-tensor-reversibility-card" open={defaultOpen}>
      <summary className="gpm-tensor-reversibility-card__summary">
        <div className="gpm-tensor-reversibility-card__head">
          <strong>{file.filename}</strong>
          <span
            className={`gpm-tensor-reversibility-status${ok ? " gpm-tensor-reversibility-status--ok" : " gpm-tensor-reversibility-status--fail"}`}
          >
            {ok ? t("tensorraum.reversibility.statusOk") : t("tensorraum.reversibility.statusFail")}
          </span>
        </div>
        <div className="gpm-tensor-reversibility-card__badges">
          <span>{t("tensorraum.reversibility.card.linesOriginal", { count: String(result.originalLineCount) })}</span>
          <span>
            {t("tensorraum.reversibility.card.linesReconstructed", { count: String(result.decompiledLineCount) })}
          </span>
          <span>{t("tensorraum.reversibility.card.tokens", { count: String(result.tokenCount) })}</span>
          <span>{t("tensorraum.reversibility.card.depth", { depth: String(result.maxDepth) })}</span>
        </div>
      </summary>
      <div className="gpm-tensor-reversibility-card__body">
        {!ok && verdict.reason ? (
          <div className="gpm-tensor-reversibility-fail">
            <strong>{t("tensorraum.reversibility.card.failReason")}:</strong> {verdict.reason}
            {verdict.mismatchIndex !== undefined ? (
              <span className="gpm-metric__hint">
                {" "}
                · {t("tensorraum.reversibility.card.mismatchAt", { index: String(verdict.mismatchIndex) })}
              </span>
            ) : null}
          </div>
        ) : null}
        <div className="gpm-tensor-reversibility-compare">
          <LineNumberedCode
            code={file.normalizedCode}
            label={t("tensorraum.reversibility.original")}
            failed={!ok}
          />
          <LineNumberedCode code={decompiled} label={t("tensorraum.reversibility.reconstructed")} failed={!ok} />
        </div>
      </div>
    </details>
  );
}
