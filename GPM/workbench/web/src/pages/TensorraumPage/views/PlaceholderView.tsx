import { t } from "../../../i18n/t";
import type { TensorraumStore } from "../hooks/useTensorraumStore";

interface PlaceholderViewProps {
  store: TensorraumStore;
  titleKey: "tensorraum.redundancy.title" | "tensorraum.reversibility.title" | "tensorraum.storage.title";
  emptyKey: "tensorraum.redundancy.empty" | "tensorraum.reversibility.empty" | "tensorraum.storage.empty";
}

export function PlaceholderView({ store, titleKey, emptyKey }: PlaceholderViewProps) {
  const hasFiles = (store.project?.root.children.length ?? 0) > 0;
  return (
    <div className="gpm-tensor-placeholder">
      <h3>{t(titleKey)}</h3>
      <p className="gpm-metric__hint">{t("tensorraum.common.phase2")}</p>
      {!hasFiles ? <p className="gpm-empty">{t(emptyKey)}</p> : null}
    </div>
  );
}
