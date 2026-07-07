import { t } from "../../i18n/t";
import { formatBigInt } from "../../utils/format";

interface GpmDocumentMetaBarProps {
  stats: Record<string, unknown> | null;
}

export function GpmDocumentMetaBar({ stats }: GpmDocumentMetaBarProps) {
  if (!stats) return null;

  const roundtripOk = stats.roundtrip_ok;
  const showRoundtrip = typeof roundtripOk === "boolean";

  return (
    <dl className="gpm-editor-meta">
      <div>
        <dt>{t("gpm.stats")}: </dt>
        <dd className="mono">
          {formatBigInt(Number(stats.token_count ?? 0))} Token ·{" "}
          {formatBigInt(Number(stats.unique_words ?? 0))} Wörter
        </dd>
      </div>
      {showRoundtrip ? (
        <div>
          <dt>{t("gpm.workspace.roundtripLabel")}: </dt>
          <dd className={roundtripOk ? "gpm-roundtrip-ok" : "gpm-roundtrip-fail"}>
            {roundtripOk ? t("gpm.workspace.roundtripOk") : t("gpm.workspace.roundtripFail")}
          </dd>
        </div>
      ) : null}
    </dl>
  );
}
