import { useState } from "react";
import { t } from "../../i18n/t";
import { SegmentToggle } from "../../components/ui";
import { CompileResultTables } from "./CompileResultTables";

type ResultSegment = "genome" | "geometry";

interface GpmEditorResultsProps {
  stats: Record<string, unknown> | null;
}

export function GpmEditorResults({ stats }: GpmEditorResultsProps) {
  const [segment, setSegment] = useState<ResultSegment>("genome");

  if (!stats) return null;

  return (
    <div className="gpm-editor-results">
      <SegmentToggle
        name="gpm-results"
        value={segment}
        onChange={(v) => setSegment(v as ResultSegment)}
        options={[
          { value: "genome", label: t("gpm.results.genome") },
          { value: "geometry", label: t("gpm.results.geometry") },
        ]}
      />
      <div style={{ marginTop: "1rem" }}>
        <CompileResultTables stats={stats} segment={segment} />
      </div>
    </div>
  );
}
