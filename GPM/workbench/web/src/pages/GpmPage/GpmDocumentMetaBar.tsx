import { t } from "../../i18n/t";
import { formatBigInt } from "../../utils/format";

interface GpmDocumentMetaBarProps {
  documentRef: string | null;
  stats: Record<string, unknown> | null;
}

export function GpmDocumentMetaBar({ documentRef, stats }: GpmDocumentMetaBarProps) {
  if (!stats && !documentRef) return null;

  return (
    <dl className="gpm-editor-meta">
      {stats ? (
        <div>
          <dt>{t("gpm.stats")}: </dt>
          <dd className="mono">
            {formatBigInt(Number(stats.token_count ?? 0))} Token ·{" "}
            {formatBigInt(Number(stats.unique_words ?? 0))} Wörter
          </dd>
        </div>
      ) : null}
      {documentRef ? (
        <div>
          <dt>{t("gpm.workspace.docRef")}: </dt>
          <dd className="mono">{documentRef}</dd>
        </div>
      ) : null}
    </dl>
  );
}
