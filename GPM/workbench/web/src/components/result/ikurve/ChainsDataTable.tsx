import { t } from "../../../i18n/t";

interface ChainsDataTableProps {
  headers: string[];
  rows: (string | number)[][];
}

export function ChainsDataTable({ headers, rows }: ChainsDataTableProps) {
  if (!rows.length) return <p className="gpm-metric__hint">{t("ikurve.chains.empty")}</p>;
  return (
    <div className="gpm-table-wrap gpm-ikurve-chains-scroll">
      <table className="gpm-table">
        <thead>
          <tr>
            {headers.map((h) => (
              <th key={h}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i}>
              {row.map((cell, j) => (
                <td key={j} className="mono">
                  {String(cell)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
