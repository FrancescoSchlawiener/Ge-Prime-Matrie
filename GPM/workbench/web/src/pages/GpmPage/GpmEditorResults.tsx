import { useState } from "react";
import { t } from "../../i18n/t";
import { SegmentToggle } from "../../components/ui";
import { CompileResultTables } from "./CompileResultTables";

type ResultSegment = "registry" | "tokens" | "reconstruct";

interface GpmEditorResultsProps {
  stats: Record<string, unknown> | null;
  reconstructed: string | null;
}

export function GpmEditorResults({ stats, reconstructed }: GpmEditorResultsProps) {
  const [segment, setSegment] = useState<ResultSegment>("registry");

  if (!stats && !reconstructed) return null;

  return (
    <div className="gpm-editor-results">
      <SegmentToggle
        name="gpm-results"
        value={segment}
        onChange={(v) => setSegment(v as ResultSegment)}
        options={[
          { value: "registry", label: t("gpm.results.registry") },
          { value: "tokens", label: t("gpm.results.tokens") },
          { value: "reconstruct", label: t("gpm.results.reconstruct") },
        ]}
      />
      <div style={{ marginTop: "1rem" }}>
        {segment === "reconstruct" ? (
          reconstructed ? (
            <p className="mono" style={{ whiteSpace: "pre-wrap" }}>
              {reconstructed}
            </p>
          ) : (
            <p className="gpm-metric__hint">{t("gpm.empty")}</p>
          )
        ) : stats ? (
          <CompileResultTables stats={stats} segment={segment} />
        ) : (
          <p className="gpm-metric__hint">{t("gpm.empty")}</p>
        )}
      </div>
    </div>
  );
}
