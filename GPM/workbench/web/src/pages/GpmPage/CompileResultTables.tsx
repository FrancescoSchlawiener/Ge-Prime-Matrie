import { t } from "../../i18n/t";
import { formatBigInt } from "../../utils/format";
import { formatSiPair } from "../../utils/formatSi";

interface CompileResultTablesProps {
  stats: Record<string, unknown>;
  segment?: "genome" | "geometry";
}

export function CompileResultTables({ stats, segment }: CompileResultTablesProps) {
  const genomePreview = (stats.genome_preview as Array<Record<string, unknown>>) ?? [];
  const geometryPreview = (stats.geometry_preview as Array<Record<string, unknown>>) ?? [];

  const showGenome = segment !== "geometry" && genomePreview.length > 0;
  const showGeometry = segment !== "genome" && geometryPreview.length > 0;

  if (!showGenome && !showGeometry) return null;

  return (
    <div>
      {showGenome ? (
        <>
          <h4 className="gpm-card__subtitle">{t("gpm.tables.genome")}</h4>
          <div className="gpm-table-wrap">
            <table className="gpm-table">
              <thead>
                <tr>
                  <th>{t("gpm.tables.wordId")}</th>
                  <th>{t("gpm.tables.word")}</th>
                  <th>{t("gpm.tables.substance")}</th>
                </tr>
              </thead>
              <tbody>
                {genomePreview.slice(0, 40).map((row) => (
                  <tr key={String(row.word_id)}>
                    <td>{String(row.word_id)}</td>
                    <td>{String(row.word_normalized ?? row.word ?? "—")}</td>
                    <td className="mono">{formatBigInt(Number(row.substance ?? 0))}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : null}
      {showGeometry ? (
        <>
          <h4 className="gpm-card__subtitle" style={{ marginTop: showGenome ? "1rem" : 0 }}>
            {t("gpm.tables.geometry")}
          </h4>
          <div className="gpm-table-wrap">
            <table className="gpm-table">
              <thead>
                <tr>
                  <th>{t("gpm.tables.position")}</th>
                  <th>{t("gpm.tables.word")}</th>
                  <th>{t("gpm.tables.siPair")}</th>
                </tr>
              </thead>
              <tbody>
                {geometryPreview.slice(0, 60).map((row) => (
                  <tr key={String(row.position)}>
                    <td>{String(row.position)}</td>
                    <td>{String(row.word_normalized ?? row.word ?? "—")}</td>
                    <td className="mono">
                      {formatSiPair(Number(row.substance ?? 0), Number(row.perm_index ?? 0))}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : null}
    </div>
  );
}
