import { t } from "../../i18n/t";

interface CompileResultTablesProps {
  stats: Record<string, unknown>;
  segment?: "registry" | "tokens";
}

export function CompileResultTables({ stats, segment }: CompileResultTablesProps) {
  const tokens = (stats.tokens as Array<Record<string, unknown>>) ?? [];
  const header = (stats.header as Array<Record<string, unknown>>) ?? [];
  const registry = (stats.registry_entries as Array<Record<string, unknown>>) ?? [];
  const wordRows = header.length ? header : registry;

  const showRegistry = segment !== "tokens" && wordRows.length;
  const showTokens = segment !== "registry" && tokens.length;

  if (!showRegistry && !showTokens) return null;

  return (
    <div>
      {showRegistry ? (
        <>
          <h4 className="gpm-card__subtitle">{t("gpm.tables.header")}</h4>
          <div className="gpm-table-wrap">
            <table className="gpm-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>{t("gpm.tables.word")}</th>
                  <th>S</th>
                  <th>I</th>
                </tr>
              </thead>
              <tbody>
                {wordRows.slice(0, 40).map((row) => (
                  <tr key={String(row.word_id)}>
                    <td>{String(row.word_id)}</td>
                    <td>{String(row.word_normalized ?? row.word_canonical ?? "—")}</td>
                    <td className="mono">{String(row.substance ?? "—")}</td>
                    <td className="mono">{String(row.perm_index ?? "—")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : null}
      {showTokens ? (
        <>
          <h4 className="gpm-card__subtitle" style={{ marginTop: showRegistry ? "1rem" : 0 }}>
            {t("gpm.tables.tokens")}
          </h4>
          <div className="gpm-table-wrap">
            <table className="gpm-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>word_id</th>
                  <th>I</th>
                </tr>
              </thead>
              <tbody>
                {tokens.slice(0, 60).map((row, i) => (
                  <tr key={i}>
                    <td>{i}</td>
                    <td>{String(row.word_id ?? "—")}</td>
                    <td className="mono">{String(row.perm_index ?? "—")}</td>
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
