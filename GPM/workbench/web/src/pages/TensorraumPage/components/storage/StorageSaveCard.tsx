import { t } from "../../../../i18n/t";
import type { StorageIndexEntry } from "../../../../lib/tensorraum";
import type { TensorraumStore } from "../../hooks/useTensorraumStore";

interface StorageSaveCardProps {
  entry: StorageIndexEntry;
  store: TensorraumStore;
}

export function StorageSaveCard({ entry, store }: StorageSaveCardProps) {
  const savedLabel = new Date(entry.savedAt).toLocaleString("de-DE");

  function onDelete() {
    if (!window.confirm(t("tensorraum.storage.deleteConfirm", { name: entry.projectName }))) return;
    store.deleteStorageSave(entry.saveId, entry.projectName);
  }

  return (
    <article className="gpm-tensor-storage-card">
      <header className="gpm-tensor-storage-card__head">
        <div>
          <strong>{entry.projectName}</strong>
          <span className="gpm-metric__hint">{t("tensorraum.storage.savedAt", { date: savedLabel })}</span>
        </div>
        <div className="gpm-tensor-storage-badges">
          <span>{t("tensorraum.storage.card.files", { count: String(entry.fileCount) })}</span>
          {entry.crossLanguageAnalysis ? (
            <span>{t("tensorraum.storage.card.cross")}</span>
          ) : null}
          {entry.structuralOnly ? <span>{t("tensorraum.storage.card.structural")}</span> : null}
          <span>
            {entry.windowMode === "adaptive"
              ? t("tensorraum.storage.card.windowAdaptive")
              : t("tensorraum.storage.card.windowFixed", { size: String(entry.windowSize) })}
          </span>
        </div>
      </header>
      <div className="gpm-tensor-storage-card__actions">
        <button type="button" className="gpm-tensor-cta gpm-tensor-cta--sm" onClick={() => store.loadStorageSave(entry.saveId)}>
          {t("tensorraum.storage.load")}
        </button>
        <button type="button" className="gpm-btn gpm-btn--sm" onClick={() => store.exportSaveToFile(entry.saveId)}>
          {t("tensorraum.storage.exportJson")}
        </button>
        <button type="button" className="gpm-btn gpm-btn--sm gpm-tensor-clear" onClick={onDelete}>
          {t("tensorraum.storage.delete")}
        </button>
      </div>
    </article>
  );
}
