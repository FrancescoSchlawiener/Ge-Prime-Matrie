import { useMemo, type CSSProperties } from "react";
import { t } from "../../../../i18n/t";
import { isFileNode, sequenceStats, type RegistryMaps, type SpaceNode } from "../../../../lib/tensorraum";
import { SequencePreview } from "./SequencePreview";

interface RegistryTreeNodeProps {
  node: SpaceNode;
  registry: RegistryMaps;
  depth?: number;
}

function accentForNode(node: SpaceNode, depth: number): string {
  if (isFileNode(node)) return "var(--gpm-muted)";
  if (depth % 3 === 0) return "var(--gpm-green)";
  return "var(--gpm-orange)";
}

export function RegistryTreeNode({ node, registry, depth = 0 }: RegistryTreeNodeProps) {
  const isModule = isFileNode(node);
  const title = isModule ? node.filename : node.id || node.openSyntax?.toUpperCase() || "space";
  const sequence = node.sequence ?? [];
  const childCount = node.children?.length ?? 0;
  const stats = useMemo(() => sequenceStats(node), [node]);
  const defaultOpen = depth < 1;
  const accent = accentForNode(node, depth);

  const pathLabel = isModule
    ? t("tensorraum.registry.tree.pathModule", { lang: node.languageId || "?" })
    : t("tensorraum.registry.tree.pathSpace", { depth: String(depth), id: node.id || "space" });

  const summaryLabel = isModule
    ? t("tensorraum.registry.tree.moduleLabel")
    : t("tensorraum.registry.tree.spaceLabel");

  return (
    <details
      className="gpm-tensor-registry-node"
      open={defaultOpen}
      style={{ "--registry-accent": accent } as CSSProperties}
    >
      <summary>
        <div className="gpm-tensor-registry-node-head">
          <strong>{title}</strong>
          <small>
            {summaryLabel} · {pathLabel}
          </small>
        </div>
        <div className="gpm-tensor-registry-node-meta">
          <span className="gpm-tensor-registry-mini">
            {t("tensorraum.registry.tree.tokensLabel", { count: String(sequence.length) })}
          </span>
          <span className="gpm-tensor-registry-mini">
            {stats.S}S · {stats.N}N · {stats.D}D · {stats.C}C
          </span>
          {childCount > 0 ? (
            <span className="gpm-tensor-registry-mini">
              {t("tensorraum.registry.tree.childrenLabel", { count: String(childCount) })}
            </span>
          ) : null}
        </div>
      </summary>
      <div className="gpm-tensor-registry-node-body">
        <SequencePreview sequence={sequence} registry={registry} />
        {childCount > 0 ? (
          <div className="gpm-tensor-registry-node-children">
            {node.children.map((child) => (
              <RegistryTreeNode key={child.id} node={child} registry={registry} depth={depth + 1} />
            ))}
          </div>
        ) : null}
      </div>
    </details>
  );
}
