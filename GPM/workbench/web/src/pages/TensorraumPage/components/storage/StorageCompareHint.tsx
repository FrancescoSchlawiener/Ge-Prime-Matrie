import { t } from "../../../../i18n/t";

export function StorageCompareHint() {
  return (
    <div className="gpm-tensor-storage-hint">
      <strong>{t("tensorraum.storage.title")}</strong>
      <p>{t("tensorraum.storage.compareHint")}</p>
    </div>
  );
}
