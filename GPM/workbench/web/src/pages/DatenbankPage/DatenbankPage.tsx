import { t } from "../../i18n/t";
import { Button, Card, PageHead } from "../../components/ui";
import { DatenbankTable, DatenbankTotalHint } from "./DatenbankTable";
import { useDatenbankStats } from "./useDatenbankStats";

export function DatenbankPage() {
  const db = useDatenbankStats();

  return (
    <div className="gpm-page">
      <PageHead title={t("datenbank.title")} lead={t("datenbank.lead")} />
      <Card>
        <div className="gpm-form-row">
          <Button onClick={() => void db.load()} disabled={db.loading} size="sm">
            {t("datenbank.refresh")}
          </Button>
          <DatenbankTotalHint total={db.total} />
        </div>
        {!db.connected ? (
          <p className="gpm-metric__hint" style={{ marginTop: "1rem" }}>
            {t("datenbank.dbMissing")}
            {db.dbName ? ` (${db.dbName})` : ""}
          </p>
        ) : (
          <p className="gpm-metric__hint" style={{ marginTop: "1rem" }}>
            {t("datenbank.dbNote")}
          </p>
        )}
        {db.error ? <div className="gpm-error" style={{ marginTop: "1rem" }}>{db.error}</div> : null}
        <DatenbankTable rows={db.rows} />
      </Card>
    </div>
  );
}
