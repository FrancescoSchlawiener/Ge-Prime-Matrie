import { useMemo, useState } from "react";
import { t } from "../../../../i18n/t";
import {
  entriesForType,
  sliceEntries,
  type PointerType,
  type ProjectRoot,
} from "../../../../lib/tensorraum";
import { DisclosureSection } from "../../../../components/ui/DisclosureSection";
import { Input } from "../../../../components/ui";
import { RegistryEntryRow } from "./RegistryEntryRow";

const CATEGORY_KEY: Record<PointerType, "c" | "n" | "d" | "h" | "s"> = {
  C: "c",
  N: "n",
  D: "d",
  H: "h",
  S: "s",
};

interface RegistryCategoryPanelProps {
  type: PointerType;
  root: ProjectRoot;
  showAll: boolean;
  onToggleShowAll: () => void;
}

export function RegistryCategoryPanel({ type, root, showAll, onToggleShowAll }: RegistryCategoryPanelProps) {
  const [query, setQuery] = useState("");
  const catKey = CATEGORY_KEY[type];
  const entries = entriesForType(root, type);
  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return entries;
    return entries.filter(([pointer, value]) => pointer.toLowerCase().includes(q) || value.toLowerCase().includes(q));
  }, [entries, query]);
  const { visible, hasMore, total } = sliceEntries(filtered, showAll);
  const title = t(`tensorraum.registry.categories.${catKey}.title`);
  const subtitle = t(`tensorraum.registry.categories.${catKey}.subtitle`);
  const badge = t("tensorraum.registry.entriesBadge", { count: String(entries.length) });
  const collision = root.header.collisionReport?.[type];
  const collisionBadge =
    collision && entries.length > 0
      ? collision.collision_free
        ? ` · ✓ ${t("tensorraum.registry.collisionFree")}`
        : ` · ⚠ ${t("tensorraum.registry.collisions", { count: String(collision.collisions) })}`
      : "";

  return (
    <div className="gpm-tensor-registry-section">
      <DisclosureSection title={title} brief={`${subtitle} · ${badge}${collisionBadge}`} defaultOpen>
        {entries.length === 0 ? (
          <p className="gpm-metric__hint">{t("tensorraum.registry.emptyCategory")}</p>
        ) : (
          <>
            <Input
              className="gpm-tensor-registry-search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={t("tensorraum.registry.searchPlaceholder")}
              aria-label={t("tensorraum.registry.searchPlaceholder")}
            />
            <div className="gpm-tensor-registry-table-wrap">
              <table className="gpm-tensor-registry-table">
                <tbody>
                  {visible.map(([pointer, value]) => (
                    <RegistryEntryRow
                      key={pointer}
                      type={type}
                      pointerId={pointer}
                      value={value}
                      hSegments={type === "H" ? root.header.hSegments?.get(pointer) : undefined}
                      dRelation={type === "D" ? root.header.dRelation?.get(pointer) : undefined}
                      sSubstance={type === "S" ? root.header.sSubstance?.get(pointer) : undefined}
                      cSubstance={type === "C" ? root.header.cSubstance?.get(pointer) : undefined}
                      hSubstance={type === "H" ? root.header.hSubstance?.get(pointer) : undefined}
                    />
                  ))}
                </tbody>
              </table>
            </div>
            {hasMore ? (
              <button type="button" className="gpm-btn gpm-btn--sm gpm-tensor-registry-expand-btn" onClick={onToggleShowAll}>
                {showAll
                  ? t("tensorraum.registry.showLess", { count: String(total) })
                  : t("tensorraum.registry.showAll", { count: String(total) })}
              </button>
            ) : null}
          </>
        )}
      </DisclosureSection>
    </div>
  );
}
