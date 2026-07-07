import { t } from "../../../../i18n/t";
import type { RegistrySubview } from "../../../../lib/tensorraum";

interface RegistrySubviewTabsProps {
  value: RegistrySubview;
  onChange: (view: RegistrySubview) => void;
}

const VIEWS: RegistrySubview[] = ["registry", "tree"];

export function RegistrySubviewTabs({ value, onChange }: RegistrySubviewTabsProps) {
  return (
    <div className="gpm-tensor-registry-subtabs" role="tablist" aria-label={t("tensorraum.registry.views.aria")}>
      {VIEWS.map((view) => (
        <button
          key={view}
          type="button"
          role="tab"
          aria-selected={value === view}
          className={`gpm-tensor-registry-subtab${value === view ? " gpm-tensor-registry-subtab--active" : ""}`}
          onClick={() => onChange(view)}
        >
          {t(`tensorraum.registry.views.${view}`)}
        </button>
      ))}
    </div>
  );
}
