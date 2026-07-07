import type { FileNode, SequenceItem, SpaceNode } from "../types";

export interface SequenceTypeStats {
  S: number;
  N: number;
  D: number;
  C: number;
  CHILD: number;
  SYS: number;
}

export interface TreeStats {
  total: number;
  leaves: number;
  maxDepth: number;
}

export function sequenceStats(node: { sequence?: SequenceItem[]; children?: SpaceNode[] }): SequenceTypeStats {
  const stats: SequenceTypeStats = { S: 0, N: 0, D: 0, C: 0, CHILD: 0, SYS: 0 };
  const seq = node.sequence ?? [];
  for (const item of seq) {
    if (item.t in stats) stats[item.t as keyof SequenceTypeStats]++;
  }
  for (const child of node.children ?? []) {
    const sub = sequenceStats(child);
    stats.S += sub.S;
    stats.N += sub.N;
    stats.D += sub.D;
    stats.C += sub.C;
    stats.CHILD += sub.CHILD;
    stats.SYS += sub.SYS;
  }
  return stats;
}

export function collectTreeStats(nodes: FileNode[] | SpaceNode[], currentDepth = 0): TreeStats {
  let total = 0;
  let leaves = 0;
  let maxDepth = currentDepth;

  const walk = (list: SpaceNode[], depthNow: number) => {
    if (!list.length) return;
    for (const node of list) {
      total += 1;
      const childCount = node.children?.length ?? 0;
      if (childCount === 0) leaves += 1;
      if (depthNow > maxDepth) maxDepth = depthNow;
      if (childCount > 0) walk(node.children, depthNow + 1);
    }
  };

  walk(nodes as SpaceNode[], currentDepth);
  return { total, leaves, maxDepth };
}

export function isFileNode(node: SpaceNode): node is FileNode {
  return "filename" in node;
}
