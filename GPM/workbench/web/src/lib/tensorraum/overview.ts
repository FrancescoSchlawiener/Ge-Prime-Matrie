import { SUPPORTED_LANGUAGES } from "./constants";
import type { TensorraumProject } from "./types";

export interface RegistryOverview {
  total: number;
  files: number;
  spaces: number;
  languages: number;
  languageTotal: number;
}

function countSpaceNodes(node: { children?: { children?: unknown[] }[] }): number {
  let c = 1;
  if (node.children) {
    for (const child of node.children) {
      c += countSpaceNodes(child as { children?: { children?: unknown[] }[] });
    }
  }
  return c;
}

export function getRegistryOverview(project: TensorraumProject): RegistryOverview {
  const reg = project.root.header.registry;
  const total = (["S", "N", "D", "C", "H"] as const).reduce((sum, ty) => sum + reg[ty].size, 0);
  const spaces = project.root.children.reduce((sum, file) => sum + countSpaceNodes(file), 0);
  return {
    total,
    files: project.root.children.length,
    spaces,
    languages: project.activeLanguageIds.size,
    languageTotal: SUPPORTED_LANGUAGES.length,
  };
}
