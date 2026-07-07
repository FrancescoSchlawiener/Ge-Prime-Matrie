import { t } from "../../../../i18n/t";
import type { PointerType, TensorraumProject } from "../../../../lib/tensorraum";
import { RegistryCategoryPanel } from "./RegistryCategoryPanel";

const TYPES: PointerType[] = ["C", "N", "D", "H", "S"];

interface RegistryAtlasProps {
  project: TensorraumProject;
  showAllMap: Record<PointerType, boolean>;
  onToggleShowAll: (type: PointerType) => void;
  onExpandAll: () => void;
}

export function RegistryAtlas({ project, showAllMap, onToggleShowAll, onExpandAll }: RegistryAtlasProps) {
  return (
    <div className="gpm-tensor-registry-panel">
      <div className="gpm-tensor-registry-toolbar">
        <div>
          <div className="gpm-tensor-registry-toolbar-label">{t("tensorraum.registry.listToolbarLabel")}</div>
          <p className="gpm-metric__hint">{t("tensorraum.registry.listToolbarHint")}</p>
        </div>
        <div className="gpm-tensor-actions">
          <button type="button" className="gpm-btn gpm-btn--sm gpm-btn--secondary" onClick={onExpandAll}>
            {t("tensorraum.registry.expandAll")}
          </button>
        </div>
      </div>
      <div className="gpm-tensor-registry-categories">
        {TYPES.map((type) => (
          <RegistryCategoryPanel
            key={type}
            type={type}
            root={project.root}
            showAll={showAllMap[type]}
            onToggleShowAll={() => onToggleShowAll(type)}
          />
        ))}
      </div>
    </div>
  );
}
