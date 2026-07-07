import { calculateChecksum } from "./checksum";
import type { PointerType, ProjectRoot, SpaceNode } from "./types";

function emptyRegistry() {
  return {
    S: new Map<string, string>(),
    N: new Map<string, string>(),
    D: new Map<string, string>(),
    C: new Map<string, string>(),
    H: new Map<string, string>(),
  };
}

export function createEmptyRoot(name: string): ProjectRoot {
  return {
    id: "root",
    name,
    children: [],
    header: {
      registry: emptyRegistry(),
      reverseRegistry: emptyRegistry(),
      hSegments: new Map(),
      dRelation: new Map(),
    },
  };
}

export function registerSubstrate(root: ProjectRoot, type: PointerType, value: string): string {
  const reg = root.header.registry[type];
  const revReg = root.header.reverseRegistry[type];
  if (revReg.has(value)) return revReg.get(value)!;
  const checksum = calculateChecksum(value);
  const pointerId = `${type}_${checksum.toString()}`;
  reg.set(pointerId, value);
  revReg.set(value, pointerId);
  return pointerId;
}

export function countPointers(root: ProjectRoot): number {
  const { registry } = root.header;
  return registry.S.size + registry.N.size + registry.D.size + registry.C.size + registry.H.size;
}

export function countSpaces(root: ProjectRoot): number {
  let n = 0;
  const walk = (node: SpaceNode) => {
    for (const child of node.children) {
      n++;
      walk(child);
    }
  };
  for (const file of root.children) walk(file);
  return n;
}
