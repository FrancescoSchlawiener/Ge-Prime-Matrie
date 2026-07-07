import type { PointerType, ProjectRoot } from "./types";

export const REGISTRY_LIST_LIMIT = 60;

export type RegistryEntry = [pointer: string, value: string];

export function entriesForType(root: ProjectRoot, type: PointerType): RegistryEntry[] {
  return [...root.header.registry[type].entries()];
}

export function sliceEntries(
  entries: RegistryEntry[],
  showAll: boolean,
  limit = REGISTRY_LIST_LIMIT,
): { visible: RegistryEntry[]; hasMore: boolean; total: number } {
  const total = entries.length;
  if (total <= limit) {
    return { visible: entries, hasMore: false, total };
  }
  if (showAll) {
    return { visible: entries, hasMore: true, total };
  }
  return { visible: entries.slice(0, limit), hasMore: true, total };
}

export function previewValue(value: string, maxLen = 140): string {
  const s = String(value);
  return s.length > maxLen ? `${s.slice(0, maxLen)}…` : s;
}
