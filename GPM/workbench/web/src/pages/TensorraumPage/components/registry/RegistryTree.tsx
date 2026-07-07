import { t } from "../../../../i18n/t";
import { collectTreeStats, type TensorraumProject } from "../../../../lib/tensorraum";
import { RegistryTreeNode } from "./RegistryTreeNode";

interface RegistryTreeProps {
  project: TensorraumProject;
}

export function RegistryTree({ project }: RegistryTreeProps) {
  const nodes = project.root.children;
  const stats = collectTreeStats(nodes);

  if (!nodes.length) {
    return <p className="gpm-metric__hint">{t("tensorraum.registry.tree.noBlocks")}</p>;
  }

  return (
    <div className="gpm-tensor-registry-tree-shell">
      <div className="gpm-tensor-registry-tree-overview">
        <div>
          <h4>{t("tensorraum.registry.tree.bannerTitle")}</h4>
          <p className="gpm-metric__hint">{t("tensorraum.registry.tree.bannerHint")}</p>
        </div>
        <div className="gpm-tensor-registry-tree-metrics">
          <div className="gpm-tensor-registry-tree-metric">
            <span>{t("tensorraum.registry.tree.metrics.roots")}</span>
            <strong>{stats.total}</strong>
          </div>
          <div className="gpm-tensor-registry-tree-metric">
            <span>{t("tensorraum.registry.tree.metrics.leaves")}</span>
            <strong>{stats.leaves}</strong>
          </div>
          <div className="gpm-tensor-registry-tree-metric">
            <span>{t("tensorraum.registry.tree.metrics.maxDepth")}</span>
            <strong>{stats.maxDepth}</strong>
          </div>
          <div className="gpm-tensor-registry-tree-metric">
            <span>{t("tensorraum.registry.tree.metrics.view")}</span>
            <strong>{t("tensorraum.registry.tree.metrics.viewWide")}</strong>
          </div>
        </div>
      </div>
      <div className="gpm-tensor-registry-tree-grid">
        {nodes.map((node) => (
          <RegistryTreeNode key={node.id} node={node} registry={project.root.header.registry} depth={0} />
        ))}
      </div>
    </div>
  );
}
