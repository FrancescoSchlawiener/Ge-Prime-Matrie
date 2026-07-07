import type { PointerType, RegistryMaps, SequenceItem, SequenceSysItem } from "./types";

export interface RegistryRowDisplay {
  type: PointerType;
  label: string;
  pointerShort: string;
  pointerFull: string;
}

export interface SequencePreviewToken {
  kind: "pointer" | "block" | "sys";
  type?: PointerType;
  label: string;
  pointerFull?: string;
}

export function shortPointerId(pointerId: string): string {
  const idx = pointerId.indexOf("_");
  if (idx < 0) return pointerId;
  const type = pointerId.slice(0, idx);
  const checksum = pointerId.slice(idx + 1);
  const tail = checksum.length > 6 ? checksum.slice(-4) : checksum;
  return `${type} ···${tail}`;
}

export function resolvePointer(registry: RegistryMaps, type: PointerType, pointerId: string): string {
  return registry[type].get(pointerId) ?? pointerId;
}

export function formatRegistryRow(type: PointerType, pointerId: string, value: string): RegistryRowDisplay {
  return {
    type,
    label: value,
    pointerShort: shortPointerId(pointerId),
    pointerFull: pointerId,
  };
}

function previewLabelForItem(item: SequenceItem, registry: RegistryMaps): SequencePreviewToken | null {
  if (item.t === "S" || item.t === "N" || item.t === "D" || item.t === "C" || item.t === "H") {
    const label = registry[item.t].get(item.p) ?? item.p;
    return { kind: "pointer", type: item.t, label, pointerFull: item.p };
  }
  if (item.t === "CHILD") {
    const open = item.openSyntax?.trim();
    return { kind: "block", label: open ? `{ ${open}` : "{" };
  }
  if (item.t === "SYS") {
    if (item.p === "CLOSE_BRACKET") {
      const close = item.closeSyntax?.trim();
      return { kind: "sys", label: close ? `${close}` : "}" };
    }
    if (item.p === "BLOCK_OPEN") {
      const blockOpen = item as SequenceSysItem & { openSyntax?: string | null };
      const open = blockOpen.openSyntax?.trim();
      return { kind: "block", label: open ? `{ ${open}` : "{" };
    }
    return { kind: "sys", label: item.p };
  }
  return null;
}

export function resolveSequencePreview(
  sequence: SequenceItem[],
  registry: RegistryMaps,
  limit = 32,
): SequencePreviewToken[] {
  const out: SequencePreviewToken[] = [];
  for (const item of sequence ?? []) {
    if (out.length >= limit) break;
    const token = previewLabelForItem(item, registry);
    if (token) out.push(token);
  }
  return out;
}

export function sequencePreviewText(tokens: SequencePreviewToken[]): string {
  return tokens.map((t) => t.label).join(" ");
}
