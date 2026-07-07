import { t } from "../../../i18n/t";
import { CompileResultTables } from "../../../pages/GpmPage/CompileResultTables";

interface IcurveDualPreviewProps {
  data: Record<string, unknown>;
}

function sideStats(data: Record<string, unknown>, side: "a" | "b") {
  const genome = (data[`genome_preview_${side}`] as Array<Record<string, unknown>>) ?? [];
  const geometry = (data[`geometry_preview_${side}`] as Array<Record<string, unknown>>) ?? [];
  return { genome_preview: genome, geometry_preview: geometry };
}

export function IcurveDualPreview({ data }: IcurveDualPreviewProps) {
  const statsA = sideStats(data, "a");
  const statsB = sideStats(data, "b");
  const hasA = statsA.genome_preview.length > 0 || statsA.geometry_preview.length > 0;
  const hasB = statsB.genome_preview.length > 0 || statsB.geometry_preview.length > 0;
  if (!hasA && !hasB) return null;

  return (
    <div className="gpm-ikurve-dual-preview">
      {hasA ? (
        <div className="gpm-ikurve-dual-preview__side">
          <h4 className="gpm-ikurve-zone__title">{t("ikurve.preview.sideA")}</h4>
          <CompileResultTables stats={statsA} />
        </div>
      ) : null}
      {hasB ? (
        <div className="gpm-ikurve-dual-preview__side">
          <h4 className="gpm-ikurve-zone__title">{t("ikurve.preview.sideB")}</h4>
          <CompileResultTables stats={statsB} />
        </div>
      ) : null}
    </div>
  );
}
