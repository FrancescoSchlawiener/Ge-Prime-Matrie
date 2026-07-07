import { t } from "../../../i18n/t";
import type { TensorraumStore } from "../hooks/useTensorraumStore";
import { RegistryAtlas } from "../components/registry/RegistryAtlas";
import { RegistryMetrics } from "../components/registry/RegistryMetrics";
import { RegistrySubviewTabs } from "../components/registry/RegistrySubviewTabs";
import { RegistryTree } from "../components/registry/RegistryTree";

interface RegistryViewProps {
  store: TensorraumStore;
}

export function RegistryView({ store }: RegistryViewProps) {
  const project = store.project;
  if (!project) return null;

  const reg = project.root.header.registry;
  const hasAny = (["S", "N", "D", "C"] as const).some((ty) => reg[ty].size > 0);
  const subview = store.registrySubview;
  const showRegistry = subview === "registry";
  const showTree = subview === "tree";

  return (
    <div className="gpm-tensor-registry" data-testid="tensorraum-registry">
      <header className="gpm-tensor-registry-headline">
        <div>
          <div className="gpm-tensor-registry-headline__title">{t("tensorraum.registry.title")}</div>
          <h4>{t("tensorraum.registry.headline")}</h4>
          <p className="gpm-metric__hint">{t("tensorraum.registry.description")}</p>
        </div>
        {hasAny ? <RegistryMetrics project={project} /> : null}
      </header>

      {hasAny ? (
        <>
          <RegistrySubviewTabs value={subview} onChange={store.setRegistrySubview} />
          {showRegistry ? (
            <RegistryAtlas
              project={project}
              showAllMap={store.registryShowAll}
              onToggleShowAll={store.toggleRegistryShowAll}
              onExpandAll={store.expandAllRegistryTypes}
            />
          ) : null}
          {showTree ? <RegistryTree project={project} /> : null}
        </>
      ) : (
        <p className="gpm-empty">{t("tensorraum.registry.empty")}</p>
      )}
    </div>
  );
}
