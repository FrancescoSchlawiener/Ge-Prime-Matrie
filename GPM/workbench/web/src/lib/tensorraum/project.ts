import { SUPPORTED_LANGUAGES } from "./constants";
import { countPointers, countSpaces, createEmptyRoot } from "./registry";
import type { ProjectStats, TensorraumProject } from "./types";

export function createProject(name: string): TensorraumProject {
  const id = `proj_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
  return {
    id,
    name,
    root: createEmptyRoot(name),
    activeLanguageIds: new Set(SUPPORTED_LANGUAGES.map((l) => l.id)),
    crossLanguageAnalysis: false,
    structuralOnly: false,
  };
}

export function clearProject(project: TensorraumProject): void {
  project.root.children = [];
  project.root.header.registry = {
    S: new Map(),
    N: new Map(),
    D: new Map(),
    C: new Map(),
    H: new Map(),
  };
  project.root.header.reverseRegistry = {
    S: new Map(),
    N: new Map(),
    D: new Map(),
    C: new Map(),
    H: new Map(),
  };
  project.root.header.hSegments = new Map();
  project.root.header.dRelation = new Map();
}

export function projectStats(project: TensorraumProject): ProjectStats {
  return {
    files: project.root.children.length,
    spaces: countSpaces(project.root),
    pointers: countPointers(project.root),
    activeLanguages: project.activeLanguageIds.size,
    totalLanguages: SUPPORTED_LANGUAGES.length,
  };
}

export function exportRegistryJson(project: TensorraumProject): string {
  const reg = project.root.header.registry;
  const payload = {
    project: project.name,
    exportedAt: new Date().toISOString(),
    registry: {
      S: Object.fromEntries(reg.S),
      N: Object.fromEntries(reg.N),
      D: Object.fromEntries(reg.D),
      C: Object.fromEntries(reg.C),
      H: Object.fromEntries(reg.H),
    },
    files: project.root.children.map((f) => ({
      filename: f.filename,
      languageId: f.languageId,
      sequenceLength: f.sequence.length,
    })),
  };
  return JSON.stringify(payload, null, 2);
}
