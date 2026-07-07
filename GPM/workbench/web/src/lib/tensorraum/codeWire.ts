import { registerSubstrate } from "./registry";
import type { PointerType, ProjectRoot, SequenceItem, SpaceNode } from "./types";

const CODE_WIRE_VERSION = 3;
const BLOCK_TREE_V2 = 2;

export interface WirePointerRef {
  kind: PointerType | "SYS";
  ptrId: number;
  nl: number;
  colPrefix: string;
  bigint?: boolean;
  childBlockId?: number;
  closeSyntax?: string;
}

export interface WireBlockNode {
  blockId: number;
  parentId: number | null;
  level: string;
  meta: {
    trailingWhitespace?: string;
    visualStyle?: string;
    envelope?: number;
    openSyntax?: string;
    prefixNl?: number;
    prefixCol?: string;
    ruleLanguage?: string;
    embeddedLanguage?: string;
  };
  sequence: WirePointerRef[];
  children: WireBlockNode[];
}

export interface WireRegistryTables {
  profile: string;
  s: Array<{ canon: string; norm: string; substance: string; permIndex: string }>;
  n: string[];
  d: Array<{ raw: string; display: string; whole: number; denReduced: number; ggt: number }>;
  c: Array<{ origin: string; value: string }>;
  h: Array<{ raw: string; segments: Array<{ tag: string; value: string }> }>;
}

export interface DecodedCodeModule {
  module: WireBlockNode;
  tables: WireRegistryTables;
}

function readUtf16(view: DataView, offset: number): { text: string; offset: number } {
  const length = view.getUint32(offset, true);
  offset += 4;
  if (length < 0 || length > view.byteLength - offset) {
    throw new Error(`Wire-String-Länge ungültig: ${length} bei Offset ${offset}`);
  }
  const bytes = new Uint8Array(view.buffer, view.byteOffset + offset, length);
  const text = new TextDecoder().decode(bytes);
  return { text, offset: offset + length };
}

function readPointerRefV2(view: DataView, offset: number): { ref: WirePointerRef; offset: number } {
  const kindLen = view.getUint8(offset);
  const ptrId = view.getUint32(offset + 1, true);
  const nl = view.getUint32(offset + 5, true);
  const colLen = view.getUint16(offset + 9, true);
  offset += 11;
  const kindBytes = new Uint8Array(view.buffer, view.byteOffset + offset, kindLen);
  const kind = new TextDecoder().decode(kindBytes) as WirePointerRef["kind"];
  offset += kindLen;
  const colBytes = new Uint8Array(view.buffer, view.byteOffset + offset, colLen);
  const colPrefix = new TextDecoder().decode(colBytes);
  offset += colLen;
  const metaFlags = view.getUint8(offset);
  offset += 1;
  const ref: WirePointerRef = { kind, ptrId, nl, colPrefix };
  if (metaFlags & 1) ref.bigint = true;
  if (metaFlags & 2) {
    ref.childBlockId = view.getUint32(offset, true);
    offset += 4;
  }
  if (metaFlags & 4) {
    const closeLen = view.getUint16(offset, true);
    offset += 2;
    const closeBytes = new Uint8Array(view.buffer, view.byteOffset + offset, closeLen);
    ref.closeSyntax = new TextDecoder().decode(closeBytes);
    offset += closeLen;
  }
  return { ref, offset };
}

const ENVELOPE_VISUAL: Record<number, string> = {
  1: "brace",
  2: "bracket",
  3: "tag",
  4: "keyword",
  5: "indent",
};

function decodeBlockTreeV2(view: DataView, offset: number): { module: WireBlockNode; offset: number } {
  const version = view.getUint8(offset);
  if (version !== BLOCK_TREE_V2) {
    throw new Error(`Block-Tree-Version ${version} nicht unterstützt`);
  }
  const count = view.getUint32(offset + 1, true);
  offset += 5;
  const nodes = new Map<number, WireBlockNode>();
  let root: WireBlockNode | null = null;
  for (let i = 0; i < count; i++) {
    const blockId = view.getUint32(offset, true);
    const parentIdRaw = view.getUint32(offset + 4, true);
    const levelLen = view.getUint16(offset + 8, true);
    const trailLen = view.getUint16(offset + 10, true);
    const flags = view.getUint8(offset + 12);
    offset += 13;
    const levelBytes = new Uint8Array(view.buffer, view.byteOffset + offset, levelLen);
    const level = new TextDecoder().decode(levelBytes);
    offset += levelLen;
    const trailBytes = new Uint8Array(view.buffer, view.byteOffset + offset, trailLen);
    const trail = new TextDecoder().decode(trailBytes);
    offset += trailLen;
    const meta: WireBlockNode["meta"] = {};
    if (trail) meta.trailingWhitespace = trail;
    if (flags & 1) {
      const envU8 = view.getUint8(offset);
      offset += 1;
      meta.envelope = envU8;
      meta.visualStyle = ENVELOPE_VISUAL[envU8] ?? "brace";
    }
    if (flags & 2) {
      const r = readUtf16(view, offset);
      meta.openSyntax = r.text;
      offset = r.offset;
    }
    if (flags & 4) {
      meta.prefixNl = view.getUint16(offset, true);
      offset += 2;
      const r = readUtf16(view, offset);
      meta.prefixCol = r.text;
      offset = r.offset;
    }
    if (flags & 8) {
      const r = readUtf16(view, offset);
      meta.ruleLanguage = r.text;
      offset = r.offset;
    }
    if (flags & 16) {
      const r = readUtf16(view, offset);
      meta.embeddedLanguage = r.text;
      offset = r.offset;
    }
    const seqLen = view.getUint16(offset, true);
    offset += 2;
    const sequence: WirePointerRef[] = [];
    for (let s = 0; s < seqLen; s++) {
      const r = readPointerRefV2(view, offset);
      sequence.push(r.ref);
      offset = r.offset;
    }
    const parentId = parentIdRaw === 0xffffffff ? null : parentIdRaw;
    const node: WireBlockNode = { blockId, parentId, level, meta, sequence, children: [] };
    nodes.set(blockId, node);
    if (parentId !== null) {
      const parent = nodes.get(parentId);
      if (parent) parent.children.push(node);
    }
    if (!root || level === "module") root = node;
  }
  return { module: root ?? { blockId: 0, parentId: null, level: "module", meta: {}, sequence: [], children: [] }, offset };
}

function decodeRegistryTables(view: DataView, offset: number): { tables: WireRegistryTables; offset: number } {
  const profileR = readUtf16(view, offset);
  offset = profileR.offset;
  const tables: WireRegistryTables = {
    profile: profileR.text,
    s: [],
    n: [],
    d: [],
    c: [],
    h: [],
  };
  let sCount = view.getUint32(offset, true);
  offset += 4;
  for (let i = 0; i < sCount; i++) {
    const canon = readUtf16(view, offset);
    offset = canon.offset;
    const norm = readUtf16(view, offset);
    offset = norm.offset;
    const substanceLo = view.getUint32(offset, true);
    const substanceHi = view.getUint32(offset + 4, true);
    const permLo = view.getUint32(offset + 8, true);
    const permHi = view.getUint32(offset + 12, true);
    offset += 16;
    const substance = (BigInt(substanceHi) << 32n) | BigInt(substanceLo);
    const permIndex = (BigInt(permHi) << 32n) | BigInt(permLo);
    tables.s.push({
      canon: canon.text,
      norm: norm.text,
      substance: substance.toString(),
      permIndex: permIndex.toString(),
    });
  }
  let nCount = view.getUint32(offset, true);
  offset += 4;
  for (let i = 0; i < nCount; i++) {
    const r = readUtf16(view, offset);
    tables.n.push(r.text);
    offset = r.offset;
  }
  let dCount = view.getUint32(offset, true);
  offset += 4;
  for (let i = 0; i < dCount; i++) {
    const raw = readUtf16(view, offset);
    offset = raw.offset;
    const display = readUtf16(view, offset);
    offset = display.offset;
    const whole = view.getUint32(offset, true);
    const denReduced = view.getUint32(offset + 4, true);
    const ggt = view.getUint32(offset + 8, true);
    offset += 12;
    const relKey = readUtf16(view, offset);
    offset = relKey.offset;
    tables.d.push({
      raw: relKey.text || raw.text,
      display: display.text,
      whole,
      denReduced,
      ggt,
    });
  }
  let cCount = view.getUint32(offset, true);
  offset += 4;
  for (let i = 0; i < cCount; i++) {
    const originLen = view.getUint8(offset);
    offset += 1;
    const originBytes = new Uint8Array(view.buffer, view.byteOffset + offset, originLen);
    const origin = new TextDecoder().decode(originBytes);
    offset += originLen;
    const value = readUtf16(view, offset);
    tables.c.push({ origin, value: value.text });
    offset = value.offset;
  }
  let hCount = view.getUint32(offset, true);
  offset += 4;
  for (let i = 0; i < hCount; i++) {
    const raw = readUtf16(view, offset);
    offset = raw.offset;
    const segCount = view.getUint16(offset, true);
    offset += 2;
    const segments: Array<{ tag: string; value: string }> = [];
    for (let s = 0; s < segCount; s++) {
      const tagLen = view.getUint8(offset);
      offset += 1;
      const tagBytes = new Uint8Array(view.buffer, view.byteOffset + offset, tagLen);
      const tag = new TextDecoder().decode(tagBytes);
      offset += tagLen;
      const val = readUtf16(view, offset);
      segments.push({ tag, value: val.text });
      offset = val.offset;
    }
    tables.h.push({ raw: raw.text, segments });
  }
  return { tables, offset };
}

export function decodeCodeModule(bytes: Uint8Array): DecodedCodeModule {
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const version = view.getUint8(0);
  if (version !== CODE_WIRE_VERSION) {
    throw new Error(`Code-Wire-Version ${version} nicht unterstützt`);
  }
  const blockLen = view.getUint32(1, true);
  const regLen = view.getUint32(5, true);
  let offset = 9;
  const blockEnd = offset + blockLen;
  const blockR = decodeBlockTreeV2(view, offset);
  const regR = decodeRegistryTables(view, blockEnd);
  if (blockEnd + regLen !== regR.offset) {
    // tolerate trailing slack from base64 decode
  }
  return { module: blockR.module, tables: regR.tables };
}

export function decodeCodeModuleBase64(b64: string): DecodedCodeModule {
  const raw = atob(b64);
  const bytes = Uint8Array.from(raw, (c) => c.charCodeAt(0));
  return decodeCodeModule(bytes);
}

function valueForRef(ref: WirePointerRef, tables: WireRegistryTables): string {
  if (ref.kind === "S") return tables.s[ref.ptrId]?.canon ?? "";
  if (ref.kind === "N") return tables.n[ref.ptrId] ?? "";
  if (ref.kind === "D") return tables.d[ref.ptrId]?.raw ?? "";
  if (ref.kind === "C") return tables.c[ref.ptrId]?.value ?? "";
  if (ref.kind === "H") return tables.h[ref.ptrId]?.raw ?? "";
  if (ref.kind === "SYS" && ref.closeSyntax) return ref.closeSyntax;
  if (ref.kind === "SYS") return tables.c[ref.ptrId]?.value ?? "";
  return "";
}

function pointerForWireValue(root: ProjectRoot, kind: PointerType, value: string): string {
  return root.header.reverseRegistry[kind].get(value) ?? registerSubstrate(root, kind, value);
}

export function syncRegistryFromWire(root: ProjectRoot, tables: WireRegistryTables): void {
  if (!root.header.sSubstance) root.header.sSubstance = new Map();
  for (const entry of tables.s) {
    const ptr = registerSubstrate(root, "S", entry.canon);
    root.header.sSubstance.set(ptr, { substance: entry.substance, permIndex: entry.permIndex });
  }
  for (const v of tables.n) registerSubstrate(root, "N", v);
  for (const d of tables.d) registerSubstrate(root, "D", d.raw);
  for (const c of tables.c) registerSubstrate(root, "C", c.value);
  for (const h of tables.h) registerSubstrate(root, "H", h.raw);
}

export function syncRegistryMetaFromWire(root: ProjectRoot, tables: WireRegistryTables): void {
  if (!root.header.hSegments) root.header.hSegments = new Map();
  if (!root.header.dRelation) root.header.dRelation = new Map();
  for (const h of tables.h) {
    const ptr = root.header.reverseRegistry.H.get(h.raw);
    if (ptr) root.header.hSegments.set(ptr, h.segments);
  }
  for (const d of tables.d) {
    const ptr = root.header.reverseRegistry.D.get(d.raw);
    if (ptr) {
      root.header.dRelation.set(ptr, {
        whole: d.whole,
        den_reduced: d.denReduced,
        ggt: d.ggt,
        display: d.display,
      });
    }
  }
}

function newId(prefix: string): string {
  return `${prefix}_${Math.random().toString(36).slice(2, 11)}`;
}

export function buildSpaceFromModule(
  root: ProjectRoot,
  node: WireBlockNode,
  tables: WireRegistryTables,
  id: string,
): SpaceNode {
  const childrenById = new Map(node.children.map((c) => [c.blockId, c]));
  const childSpaces: SpaceNode[] = [];
  const sequence: SequenceItem[] = [];
  for (const ref of node.sequence) {
    if (ref.kind === "SYS" && ref.childBlockId != null) {
      const child = childrenById.get(ref.childBlockId);
      if (child) {
        const childSpace = buildSpaceFromModule(root, child, tables, newId("space"));
        childSpaces.push(childSpace);
        sequence.push({
          t: "CHILD",
          n: childSpace,
          nl: child.meta.prefixNl ?? 0,
          colPrefix: child.meta.prefixCol,
          visualStyle: child.meta.visualStyle,
          openSyntax: child.meta.openSyntax ?? null,
        });
      }
      continue;
    }
    if (ref.kind === "SYS") {
      sequence.push({
        t: "SYS",
        p: "CLOSE_BRACKET",
        nl: ref.nl,
        colPrefix: ref.colPrefix,
        closeSyntax: ref.closeSyntax ?? null,
      });
      continue;
    }
    const value = valueForRef(ref, tables);
    const kind = ref.kind as PointerType;
    const ptr = pointerForWireValue(root, kind, value);
    sequence.push({ t: kind, p: ptr, nl: ref.nl, colPrefix: ref.colPrefix, bigint: ref.bigint });
  }
  return {
    id,
    children: childSpaces,
    sequence,
    visualStyle: node.meta.visualStyle,
    openSyntax: node.meta.openSyntax,
  };
}
