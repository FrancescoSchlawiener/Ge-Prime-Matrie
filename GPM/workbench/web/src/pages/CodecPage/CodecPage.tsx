import { Outlet } from "react-router-dom";
import { SubTabNav } from "../../components/shell/SubTabNav";
import { PageHead } from "../../components/ui";
import { t } from "../../i18n/t";

const SUBTABS = [
  { to: "/codec/encodieren", labelKey: "shell.subtabs.encode", testId: "subtab-encode" },
  { to: "/codec/decodieren", labelKey: "shell.subtabs.decode", testId: "subtab-decode" },
] as const;

export function CodecPage() {
  return (
    <div className="gpm-page">
      <PageHead title={t("shell.tabs.codec")} lead={t("shell.leads.codec")} />
      <SubTabNav tabs={[...SUBTABS]} ariaLabelKey="shell.subtabs.codecAria" />
      <Outlet />
    </div>
  );
}
