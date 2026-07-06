import { t } from "../../i18n/t";
import { languageLabel } from "../../i18n/languageLabel";
import type { LangRow } from "./useDatenbankStats";

interface DatenbankTableProps {
  rows: LangRow[];
}

export function DatenbankTable({ rows }: DatenbankTableProps) {
  if (!rows.length) {
    return <p className="gpm-empty">{t("datenbank.empty")}</p>;
  }

  return (
    <table className="gpm-table" style={{ marginTop: "1rem" }}>
      <thead>
        <tr>
          <th>{t("datenbank.language")}</th>
          <th>{t("datenbank.count")}</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.language}>
            <td>{languageLabel(row.language)}</td>
            <td>{row.count}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function DatenbankTotalHint({ total }: { total: number }) {
  return (
    <span className="gpm-metric__hint">
      {t("datenbank.total")}: <strong>{total}</strong>
    </span>
  );
}
