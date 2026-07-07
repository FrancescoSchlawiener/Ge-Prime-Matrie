import { createEmptyRoot, countPointers, countSpaces } from "./registry";
import type { ProjectRoot, ProjectStats, TensorraumProject } from "./types";

const DEFAULT_LANGUAGE_IDS = ["js", "py", "html", "css", "c", "java", "go", "rs", "php", "rb", "cs", "swift", "kt", "sql", "sh", "xml", "json", "toml", "markdown"];

export function createProject(name: string, languageIds?: Iterable<string>): TensorraumProject {
  const id = `proj_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
  const ids = languageIds ? [...languageIds] : DEFAULT_LANGUAGE_IDS;
  return {
    id,
    name,
    root: createEmptyRoot(name),
    activeLanguageIds: new Set(ids),
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

export function projectStats(project: TensorraumProject, totalLanguages?: number): ProjectStats {
  return {
    files: project.root.children.length,
    spaces: countSpaces(project.root),
    pointers: countPointers(project.root),
    activeLanguages: project.activeLanguageIds.size,
    totalLanguages: totalLanguages ?? project.activeLanguageIds.size,
  };
}

function cloneRegistryMaps(maps: ProjectRoot["header"]["registry"]): ProjectRoot["header"]["registry"] {
  return {
    S: new Map(maps.S),
    N: new Map(maps.N),
    D: new Map(maps.D),
    C: new Map(maps.C),
    H: new Map(maps.H),
  };
}

/** Shallow snapshot so React detects registry/file changes after in-place mutation. */
export function cloneProjectSnapshot(project: TensorraumProject): TensorraumProject {
  return {
    ...project,
    activeLanguageIds: new Set(project.activeLanguageIds),
    root: {
      ...project.root,
      children: [...project.root.children],
      header: {
        ...project.root.header,
        registry: cloneRegistryMaps(project.root.header.registry),
        reverseRegistry: cloneRegistryMaps(project.root.header.reverseRegistry),
        hSegments: new Map(project.root.header.hSegments ?? []),
        dRelation: new Map(project.root.header.dRelation ?? []),
      },
    },
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
