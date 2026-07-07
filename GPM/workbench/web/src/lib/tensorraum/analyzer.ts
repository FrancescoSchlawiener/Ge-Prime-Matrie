import { MIN_CHAIN_LENGTH } from "./constants";
import { checksumOfPointerList, checksumOfTypeList } from "./checksumChains";
import type { FileNode, SequenceItem, SpaceNode, TensorraumProject } from "./types";

export interface BlockChainOccurrence {
  node: SpaceNode;
  sequence: SequenceItem[];
  file: string;
  languageId: string;
  sigHash: string;
}

export interface SentenceChainOccurrence {
  file: string;
  languageId: string;
  sequence: SequenceItem[];
  start: number;
  windowSize: number;
  sigHash: string;
}

export interface BlockChain {
  hash: string;
  occurrences: BlockChainOccurrence[];
  chainLength: number;
}

export interface SentenceChain {
  hash: string;
  occurrences: SentenceChainOccurrence[];
  chainLength: number;
  windowSize: number;
}

export interface RedundancyScanResult {
  blockChains: BlockChain[];
  sentenceChains: SentenceChain[];
  scannedAt: number;
}

export const REDUNDANCY_CARD_LIMIT = 40;

export function flattenSequence(node: SpaceNode, out: SequenceItem[] = []): SequenceItem[] {
  for (const item of node.sequence) {
    if (item.t === "CHILD") {
      out.push({
        t: "SYS",
        p: "BLOCK_OPEN",
        nl: item.nl || 0,
      });
      flattenSequence(item.n, out);
    } else {
      out.push(item);
    }
  }
  return out;
}

function checksumFnForProject(project: TensorraumProject) {
  return project.structuralOnly ? checksumOfTypeList : checksumOfPointerList;
}

function langKeyForProject(project: TensorraumProject, languageId: string): string {
  return project.crossLanguageAnalysis ? "CROSS" : languageId;
}

export function findChains(project: TensorraumProject): BlockChain[] {
  const checksumFn = checksumFnForProject(project);
  const allNodes: BlockChainOccurrence[] = [];

  const collect = (node: SpaceNode, parentFile: string, languageId: string) => {
    if (node.sequence && node.sequence.length >= MIN_CHAIN_LENGTH) {
      const langKey = langKeyForProject(project, languageId);
      const sigHash = `${checksumFn(node.sequence).toString()}::${langKey}`;
      allNodes.push({
        node,
        sequence: node.sequence,
        file: parentFile,
        languageId,
        sigHash,
      });
    }
    if (node.children) {
      for (const child of node.children) {
        collect(child, parentFile, languageId);
      }
    }
  };

  for (const file of project.root.children) {
    collect(file, file.filename, file.languageId || "unknown");
  }

  const groups = new Map<string, BlockChainOccurrence[]>();
  for (const item of allNodes) {
    const list = groups.get(item.sigHash) ?? [];
    list.push(item);
    groups.set(item.sigHash, list);
  }

  const redundancies: BlockChain[] = [];
  groups.forEach((items, hash) => {
    if (items.length > 1) {
      redundancies.push({
        hash,
        occurrences: items,
        chainLength: items[0].sequence.length,
      });
    }
  });

  return redundancies.sort((a, b) => {
    if (b.chainLength !== a.chainLength) return b.chainLength - a.chainLength;
    return b.occurrences.length - a.occurrences.length;
  });
}

export function findSentenceChains(
  project: TensorraumProject,
  windowSizeOrSizes: number | number[],
): SentenceChain[] {
  const sizes = Array.isArray(windowSizeOrSizes) ? windowSizeOrSizes : [windowSizeOrSizes];
  const checksumFn = checksumFnForProject(project);
  const allWindows: SentenceChainOccurrence[] = [];
  const flatCache = new Map<string, SequenceItem[]>();

  for (const rawSize of sizes) {
    const W = Math.max(2, rawSize | 0);
    const stride = Math.max(1, Math.floor(W / 2));

    for (const file of project.root.children) {
      if (!flatCache.has(file.id)) {
        flatCache.set(file.id, flattenSequence(file));
      }
      const flat = flatCache.get(file.id)!;
      const langKey = langKeyForProject(project, file.languageId || "unknown");

      for (let start = 0; start + W <= flat.length; start += stride) {
        const windowItems = flat.slice(start, start + W);
        const sigHash = `${checksumFn(windowItems).toString()}::${langKey}::W${W}`;
        allWindows.push({
          file: file.filename,
          languageId: file.languageId || "unknown",
          sequence: windowItems,
          start,
          windowSize: W,
          sigHash,
        });
      }
    }
  }

  const groups = new Map<string, SentenceChainOccurrence[]>();
  for (const item of allWindows) {
    const list = groups.get(item.sigHash) ?? [];
    list.push(item);
    groups.set(item.sigHash, list);
  }

  const redundancies: SentenceChain[] = [];
  groups.forEach((items, hash) => {
    if (items.length > 1) {
      redundancies.push({
        hash,
        occurrences: items,
        chainLength: items[0].sequence.length,
        windowSize: items[0].windowSize,
      });
    }
  });

  return redundancies.sort((a, b) => {
    if (b.chainLength !== a.chainLength) return b.chainLength - a.chainLength;
    return b.occurrences.length - a.occurrences.length;
  });
}

export type { FileNode };
