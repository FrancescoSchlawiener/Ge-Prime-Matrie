import { useRef } from "react";
import { t } from "../../../../i18n/t";
import type { TensorraumStore } from "../../hooks/useTensorraumStore";

interface StorageToolbarProps {
  store: TensorraumStore;
}

export function StorageToolbar({ store }: StorageToolbarProps) {
  const fileRef = useRef<HTMLInputElement>(null);
  const hasFiles = (store.project?.root.children.length ?? 0) > 0;

  async function onImport(file: File) {
    const result = await store.importSaveFromFile(file);
    if (!result.ok) {
      window.alert(
        result.error === "PARSE" ? t("tensorraum.storage.importError") : t("tensorraum.storage.saveQuotaError"),
      );
    }
  }

  function onSave() {
    const result = store.saveActiveToStorage();
    if (!result.ok) {
      if (result.error === "NO_FILES") {
        window.alert(t("tensorraum.storage.saveNoFiles"));
      } else if (result.error === "QUOTA") {
        window.alert(t("tensorraum.storage.saveQuotaError"));
      }
    }
  }

  return (
    <div className="gpm-tensor-storage-toolbar">
      <div>
        <p className="gpm-metric__hint">{t("tensorraum.storage.lead")}</p>
        <p className="gpm-metric__hint">{t("tensorraum.storage.saveHint")}</p>
      </div>
      <div className="gpm-tensor-storage-toolbar__actions">
        <button type="button" className="gpm-tensor-cta" disabled={!hasFiles} onClick={onSave}>
          {t("tensorraum.storage.saveCurrent")}
        </button>
        <button type="button" className="gpm-btn gpm-btn--sm" onClick={() => fileRef.current?.click()}>
          {t("tensorraum.storage.importJson")}
        </button>
        <input
          ref={fileRef}
          type="file"
          accept="application/json,.json"
          className="sr-only"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) void onImport(file);
            e.target.value = "";
          }}
        />
      </div>
    </div>
  );
}
