import { NavLink } from "react-router-dom";
import { t } from "../../i18n/t";

export interface SubTabItem {
  to: string;
  labelKey: string;
  testId?: string;
}

interface SubTabNavProps {
  tabs: SubTabItem[];
  ariaLabelKey: string;
}

export function SubTabNav({ tabs, ariaLabelKey }: SubTabNavProps) {
  return (
    <nav className="gpm-subtabs" aria-label={t(ariaLabelKey)}>
      {tabs.map((tab) => (
        <NavLink
          key={tab.to}
          to={tab.to}
          data-testid={tab.testId}
          className={({ isActive }) => `gpm-subtab${isActive ? " gpm-subtab--active" : ""}`}
        >
          {t(tab.labelKey)}
        </NavLink>
      ))}
    </nav>
  );
}
