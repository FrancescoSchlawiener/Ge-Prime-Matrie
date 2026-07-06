import { Outlet } from "react-router-dom";
import { SubTabNav } from "../../components/shell/SubTabNav";
import { PageHead } from "../../components/ui";
import { t } from "../../i18n/t";

const SUBTABS = [
  { to: "/vergleichen/wortpaar", labelKey: "shell.subtabs.wordPair", testId: "subtab-wortpaar" },
  { to: "/vergleichen/ikurve", labelKey: "shell.subtabs.iCurve", testId: "subtab-ikurve" },
] as const;

export function VergleichenPage() {
  return (
    <div className="gpm-page">
      <PageHead title={t("shell.tabs.compare")} lead={t("shell.leads.compare")} />
      <SubTabNav tabs={[...SUBTABS]} ariaLabelKey="shell.subtabs.compareAria" />
      <Outlet />
    </div>
  );
}
