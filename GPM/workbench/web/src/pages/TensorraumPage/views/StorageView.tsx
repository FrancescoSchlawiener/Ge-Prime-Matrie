import { useEffect } from "react";
import { t } from "../../../i18n/t";
import { StorageCompareHint } from "../components/storage/StorageCompareHint";
import { StorageSaveCard } from "../components/storage/StorageSaveCard";
import { StorageToolbar } from "../components/storage/StorageToolbar";
import type { TensorraumStore } from "../hooks/useTensorraumStore";

interface StorageViewProps {
  store: TensorraumStore;
}

export function StorageView({ store }: StorageViewProps) {
  useEffect(() => {
    store.refreshStorageList();
  }, [store.refreshStorageList]);

  const saves = store.storageSaves;

  return (
    <div className="gpm-tensor-storage">
      <StorageCompareHint />
      <StorageToolbar store={store} />

      {saves.length === 0 ? (
        <div className="gpm-tensor-storage-empty">
          <p className="gpm-empty">{t("tensorraum.storage.empty")}</p>
          <p className="gpm-metric__hint">{t("tensorraum.storage.emptyHint")}</p>
        </div>
      ) : (
        <div className="gpm-tensor-storage-list">
          {saves.map((entry) => (
            <StorageSaveCard key={entry.saveId} entry={entry} store={store} />
          ))}
        </div>
      )}
    </div>
  );
}
