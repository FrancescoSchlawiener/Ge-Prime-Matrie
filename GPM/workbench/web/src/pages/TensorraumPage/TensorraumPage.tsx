import { useEffect } from "react";
import { PageHead, TabGuide } from "../../components/ui";
import { t } from "../../i18n/t";
import { ensureLanguagesLoaded } from "../../lib/tensorraum/detectLanguage";
import { TensorraumDocsPanel } from "./components/TensorraumDocsPanel";
import { TensorraumSidebar } from "./components/TensorraumSidebar";
import { TensorraumTabNav } from "./components/TensorraumTabNav";
import { useTensorraumStore } from "./hooks/useTensorraumStore";
import { RedundancyView } from "./views/RedundancyView";
import { RegistryView } from "./views/RegistryView";
import { ReversibilityView } from "./views/ReversibilityView";
import { StorageView } from "./views/StorageView";
import { WorkspaceView } from "./views/WorkspaceView";

export function TensorraumPage() {
  const store = useTensorraumStore();

  useEffect(() => {
    void ensureLanguagesLoaded();
  }, []);

  return (
    <div className="gpm-page gpm-page--tensor">
      <PageHead title={t("tensorraum.title")} lead={t("tensorraum.lead")} />
      <TabGuide>{t("tensorraum.guide")}</TabGuide>
      <TensorraumDocsPanel />
      <TensorraumTabNav view={store.view} onViewChange={store.setView} />
      <div className="gpm-tensor-layout">
        <TensorraumSidebar store={store} />
        <main className="gpm-tensor-main">
          {store.view === "workspace" ? <WorkspaceView store={store} /> : null}
          {store.view === "registry" ? <RegistryView store={store} /> : null}
          {store.view === "redundancy" ? <RedundancyView store={store} /> : null}
          {store.view === "reversibility" ? <ReversibilityView store={store} /> : null}
          {store.view === "storage" ? <StorageView store={store} /> : null}
        </main>
      </div>
    </div>
  );
}
