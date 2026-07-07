import { processCode } from "../code";
import { DEFAULT_WINDOW_SIZE } from "./constants";
import { createProject } from "./project";
import type { TensorraumProject } from "./types";

export const GPM_SAVE_FORMAT = 1 as const;

export interface GpmProjectSaveFile {
  filename: string;
  languageId: string;
  rawCode: string;
}

export interface GpmProjectSaveSettings {
  crossLanguageAnalysis: boolean;
  structuralOnly: boolean;
  activeLanguageIds: string[];
  windowMode: "fixed" | "adaptive";
  windowSize: number;
}

export interface GpmProjectSave {
  gpmSaveFormat: typeof GPM_SAVE_FORMAT;
  saveId: string;
  projectName: string;
  savedAt: string;
  settings: GpmProjectSaveSettings;
  files: GpmProjectSaveFile[];
}

export interface StorageIndexEntry {
  saveId: string;
  projectName: string;
  savedAt: string;
  fileCount: number;
  crossLanguageAnalysis: boolean;
  structuralOnly: boolean;
  windowMode: "fixed" | "adaptive";
  windowSize: number;
}

export interface LoadProjectResult {
  project: TensorraumProject;
  loaded: number;
  skipped: number;
  sourceSaveId: string;
  windowMode: "fixed" | "adaptive";
  windowSize: number;
}

export function createSaveId(): string {
  return `save_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

export function serializeProject(
  project: TensorraumProject,
  windowMode: "fixed" | "adaptive",
  windowSize: number,
  saveId?: string,
): GpmProjectSave {
  return {
    gpmSaveFormat: GPM_SAVE_FORMAT,
    saveId: saveId ?? createSaveId(),
    projectName: project.name,
    savedAt: new Date().toISOString(),
    settings: {
      crossLanguageAnalysis: project.crossLanguageAnalysis,
      structuralOnly: project.structuralOnly,
      activeLanguageIds: [...project.activeLanguageIds],
      windowMode,
      windowSize,
    },
    files: project.root.children.map((f) => ({
      filename: f.filename,
      languageId: f.languageId,
      rawCode: f.rawCodeOriginal,
    })),
  };
}

export function storageIndexEntry(save: GpmProjectSave): StorageIndexEntry {
  return {
    saveId: save.saveId,
    projectName: save.projectName,
    savedAt: save.savedAt,
    fileCount: save.files.length,
    crossLanguageAnalysis: save.settings.crossLanguageAnalysis,
    structuralOnly: save.settings.structuralOnly,
    windowMode: save.settings.windowMode,
    windowSize: save.settings.windowSize,
  };
}

export function validateSave(data: unknown): data is GpmProjectSave {
  if (!data || typeof data !== "object") return false;
  const o = data as Record<string, unknown>;
  if (o.gpmSaveFormat !== GPM_SAVE_FORMAT) return false;
  if (typeof o.saveId !== "string" || !o.saveId) return false;
  if (typeof o.projectName !== "string") return false;
  if (typeof o.savedAt !== "string") return false;
  if (!o.settings || typeof o.settings !== "object") return false;
  const s = o.settings as Record<string, unknown>;
  if (typeof s.crossLanguageAnalysis !== "boolean") return false;
  if (typeof s.structuralOnly !== "boolean") return false;
  if (!Array.isArray(s.activeLanguageIds)) return false;
  if (s.windowMode !== "fixed" && s.windowMode !== "adaptive") return false;
  if (typeof s.windowSize !== "number") return false;
  if (!Array.isArray(o.files)) return false;
  for (const f of o.files) {
    if (!f || typeof f !== "object") return false;
    const file = f as Record<string, unknown>;
    if (typeof file.filename !== "string") return false;
    if (typeof file.rawCode !== "string") return false;
  }
  return true;
}

export function saveToJson(save: GpmProjectSave): string {
  return JSON.stringify(save, null, 2);
}

export function parseSaveJson(text: string): GpmProjectSave {
  const data = JSON.parse(text) as unknown;
  if (!validateSave(data)) {
    throw new Error("INVALID_SAVE_FORMAT");
  }
  return data;
}

export async function loadProjectFromSave(save: GpmProjectSave): Promise<LoadProjectResult> {
  const project = createProject(save.projectName || "Geladenes_Projekt");
  project.sourceSaveId = save.saveId;

  const settings = save.settings;
  project.crossLanguageAnalysis = Boolean(settings.crossLanguageAnalysis);
  project.structuralOnly = Boolean(settings.structuralOnly);
  if (Array.isArray(settings.activeLanguageIds) && settings.activeLanguageIds.length > 0) {
    project.activeLanguageIds = new Set(settings.activeLanguageIds);
  }

  let loaded = 0;
  let skipped = 0;

  for (const f of save.files ?? []) {
    const result = await processCode(project, f.rawCode, f.filename);
    if (!result) {
      skipped++;
      continue;
    }
    if ("skipped" in result) {
      skipped++;
    } else {
      loaded++;
    }
  }

  const windowMode = settings.windowMode === "adaptive" ? "adaptive" : "fixed";
  const windowSize =
    typeof settings.windowSize === "number" && settings.windowSize >= 8
      ? settings.windowSize
      : DEFAULT_WINDOW_SIZE;

  return {
    project,
    loaded,
    skipped,
    sourceSaveId: save.saveId,
    windowMode,
    windowSize,
  };
}
