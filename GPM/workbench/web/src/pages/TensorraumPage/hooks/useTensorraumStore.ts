import { useCallback, useMemo, useState } from "react";
import { t } from "../../../i18n/t";
import {
  ADAPTIVE_WINDOW_SIZES,
  DEFAULT_WINDOW_SIZE,
  SUPPORTED_LANGUAGES,
  StorageError,
  clearProject,
  createProject,
  deleteSave,
  exportRegistryJson,
  findChains,
  findSentenceChains,
  getSave,
  listSaves,
  loadProjectFromSave,
  parseSaveJson,
  processCode,
  projectStats,
  putSave,
  saveToJson,
  serializeProject,
  type LogEntry,
  type PointerType,
  type RedundancyScanResult,
  type RedundancySubview,
  type RegistrySubview,
  type StorageIndexEntry,
  type TensorraumProject,
  type TensorraumView,
} from "../../../lib/tensorraum";

const DEFAULT_SHOW_ALL: Record<PointerType, boolean> = {
  S: false,
  N: false,
  D: false,
  C: false,
  H: false,
};

function newLog(message: string): LogEntry {
  return { id: `${Date.now()}_${Math.random().toString(36).slice(2, 6)}`, message, at: Date.now() };
}

export function useTensorraumStore() {
  const [projects, setProjects] = useState<TensorraumProject[]>(() => [createProject("Enterprise_Codebase")]);
  const [activeProjectId, setActiveProjectId] = useState<string>(() => projects[0]?.id ?? "");
  const [view, setView] = useState<TensorraumView>("workspace");
  const [logs, setLogs] = useState<LogEntry[]>([newLog(t("tensorraum.workspace.logWaiting"))]);
  const [windowMode, setWindowMode] = useState<"fixed" | "adaptive">("fixed");
  const [windowSize, setWindowSize] = useState(DEFAULT_WINDOW_SIZE);
  const [codeInput, setCodeInput] = useState("");
  const [registrySubview, setRegistrySubview] = useState<RegistrySubview>("registry");
  const [registryShowAll, setRegistryShowAll] = useState<Record<PointerType, boolean>>(() => ({
    ...DEFAULT_SHOW_ALL,
  }));
  const [redundancySubview, setRedundancySubview] = useState<RedundancySubview>("block");
  const [redundancyScan, setRedundancyScan] = useState<RedundancyScanResult | null>(null);
  const [storageSaves, setStorageSaves] = useState<StorageIndexEntry[]>(() => listSaves());

  const toggleRegistryShowAll = useCallback((type: PointerType) => {
    setRegistryShowAll((prev) => ({ ...prev, [type]: !prev[type] }));
  }, []);

  const expandAllRegistryTypes = useCallback(() => {
    setRegistryShowAll({ S: true, N: true, D: true, C: true, H: true });
  }, []);

  const collapseAllRegistryTypes = useCallback(() => {
    setRegistryShowAll({ ...DEFAULT_SHOW_ALL });
  }, []);

  const project = useMemo(
    () => projects.find((p) => p.id === activeProjectId) ?? projects[0],
    [projects, activeProjectId],
  );

  const stats = useMemo(() => (project ? projectStats(project) : null), [project]);

  const appendLog = useCallback((message: string) => {
    setLogs((prev) => [...prev.slice(-199), newLog(message)]);
  }, []);

  const refreshProjects = useCallback(() => {
    setProjects((prev) => [...prev]);
  }, []);

  const createNewProject = useCallback(() => {
    const p = createProject(`Projekt_${projects.length + 1}`);
    setProjects((prev) => [...prev, p]);
    setActiveProjectId(p.id);
    setRedundancyScan(null);
    appendLog(t("tensorraum.log.projectCreated", { name: p.name }));
  }, [appendLog, projects.length]);

  const renameProject = useCallback(
    (name: string) => {
      if (!project) return;
      project.name = name;
      project.root.name = name;
      refreshProjects();
    },
    [project, refreshProjects],
  );

  const clearActive = useCallback(() => {
    if (!project) return;
    clearProject(project);
    refreshProjects();
    setRedundancyScan(null);
    appendLog(t("tensorraum.log.projectCleared"));
  }, [appendLog, project, refreshProjects]);

  const toggleLanguage = useCallback(
    (langId: string) => {
      if (!project) return false;
      if (project.activeLanguageIds.has(langId)) {
        if (project.activeLanguageIds.size <= 1) {
          appendLog(t("tensorraum.log.needOneLanguage"));
          return false;
        }
        project.activeLanguageIds.delete(langId);
      } else {
        project.activeLanguageIds.add(langId);
      }
      refreshProjects();
      return true;
    },
    [appendLog, project, refreshProjects],
  );

  const toggleAllLanguages = useCallback(() => {
    if (!project) return;
    const allActive = project.activeLanguageIds.size === SUPPORTED_LANGUAGES.length;
    if (allActive) {
      project.activeLanguageIds = new Set([SUPPORTED_LANGUAGES[0].id]);
    } else {
      project.activeLanguageIds = new Set(SUPPORTED_LANGUAGES.map((l) => l.id));
    }
    refreshProjects();
  }, [project, refreshProjects]);

  const canonicalizeSnippet = useCallback(async () => {
    if (!project || !codeInput.trim()) return;
    try {
      const result = await processCode(project, codeInput, "Interaktives_Snippet.js", { bypassFilter: true });
      if (!result) return;
      if ("skipped" in result) {
        if (result.reason === "ignored") appendLog(t("tensorraum.log.skippedIgnored", { file: "Snippet" }));
        else if (result.reason === "unknown") appendLog(t("tensorraum.log.skippedUnknown", { file: "Snippet" }));
        else appendLog(t("tensorraum.log.skippedLanguage", { file: "Snippet", lang: result.languageName ?? "?" }));
        return;
      }
      refreshProjects();
      appendLog(
        t("tensorraum.log.canonicalized", {
          file: result.fileNode.filename,
          len: String(result.fileNode.sequence.length),
        }),
      );
    } catch (e) {
      const message = e instanceof Error ? e.message : String(e);
      appendLog(t("tensorraum.log.canonicalizeFailed", { file: "Snippet", message }));
    }
  }, [appendLog, codeInput, project, refreshProjects]);

  const ingestFiles = useCallback(
    async (files: FileList | File[]) => {
      if (!project) return;
      let loaded = 0;
      let skipped = 0;
      let failed = 0;
      for (const file of Array.from(files)) {
        const text = await file.text();
        try {
          const result = await processCode(project, text, file.name);
          if (!result) {
            skipped++;
            continue;
          }
          if ("skipped" in result) {
            skipped++;
            if (result.reason === "ignored") appendLog(t("tensorraum.log.skippedIgnored", { file: file.name }));
            else if (result.reason === "unknown") appendLog(t("tensorraum.log.skippedUnknown", { file: file.name }));
            else
              appendLog(
                t("tensorraum.log.skippedLanguage", { file: file.name, lang: result.languageName ?? "?" }),
              );
          } else {
            loaded++;
            appendLog(
              t("tensorraum.log.canonicalized", {
                file: result.fileNode.filename,
                len: String(result.fileNode.sequence.length),
              }),
            );
          }
        } catch (e) {
          failed++;
          const message = e instanceof Error ? e.message : String(e);
          appendLog(t("tensorraum.log.canonicalizeFailed", { file: file.name, message }));
        }
      }
      refreshProjects();
      appendLog(t("tensorraum.log.filesLoaded", { count: loaded, skipped, failed: String(failed) }));
    },
    [appendLog, project, refreshProjects],
  );

  const exportRegistry = useCallback(() => {
    if (!project) return;
    const blob = new Blob([exportRegistryJson(project)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${project.name.replace(/\s+/g, "_")}_registry.json`;
    a.click();
    URL.revokeObjectURL(url);
    appendLog(t("tensorraum.log.exportDone"));
  }, [appendLog, project]);

  const windowSizes = windowMode === "adaptive" ? [...ADAPTIVE_WINDOW_SIZES] : [windowSize];

  const runRedundancyScan = useCallback(() => {
    if (!project) return;
    setRedundancyScan({
      blockChains: findChains(project),
      sentenceChains: findSentenceChains(project, windowSizes),
      scannedAt: Date.now(),
    });
  }, [project, windowSizes]);

  const selectProject = useCallback((id: string) => {
    setActiveProjectId(id);
    setRedundancyScan(null);
  }, []);

  const refreshStorageList = useCallback(() => {
    setStorageSaves(listSaves());
  }, []);

  const saveActiveToStorage = useCallback(() => {
    if (!project) return { ok: false as const, error: "NO_PROJECT" };
    if (project.root.children.length === 0) return { ok: false as const, error: "NO_FILES" };
    try {
      const save = serializeProject(project, windowMode, windowSize);
      putSave(save);
      refreshStorageList();
      appendLog(t("tensorraum.log.savedToStorage", { name: save.projectName }));
      return { ok: true as const };
    } catch (err) {
      if (err instanceof StorageError && err.code === "QUOTA_EXCEEDED") {
        return { ok: false as const, error: "QUOTA" };
      }
      throw err;
    }
  }, [appendLog, project, refreshStorageList, windowMode, windowSize]);

  const loadStorageSave = useCallback(
    async (saveId: string) => {
      const save = getSave(saveId);
      if (!save) return { ok: false as const, error: "NOT_FOUND" };
      const result = await loadProjectFromSave(save);
      setProjects((prev) => [...prev, result.project]);
      setActiveProjectId(result.project.id);
      setWindowMode(result.windowMode);
      setWindowSize(result.windowSize);
      setRedundancyScan(null);
      appendLog(
        t("tensorraum.log.loadedFromStorage", {
          name: result.project.name,
          loaded: String(result.loaded),
          skipped: String(result.skipped),
        }),
      );
      return { ok: true as const, loaded: result.loaded, skipped: result.skipped };
    },
    [appendLog],
  );

  const deleteStorageSave = useCallback(
    (saveId: string, name: string) => {
      deleteSave(saveId);
      refreshStorageList();
      appendLog(t("tensorraum.log.deletedFromStorage", { name }));
    },
    [appendLog, refreshStorageList],
  );

  const exportSaveToFile = useCallback((saveId: string) => {
    const save = getSave(saveId);
    if (!save) return;
    const blob = new Blob([saveToJson(save)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `gpm_${save.projectName.replace(/\s+/g, "_")}_${save.saveId.slice(-8)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, []);

  const importSaveFromFile = useCallback(
    async (file: File) => {
      try {
        const text = await file.text();
        const save = parseSaveJson(text);
        putSave(save);
        refreshStorageList();
        appendLog(t("tensorraum.log.importedSave", { name: save.projectName }));
        return { ok: true as const };
      } catch (err) {
        if (err instanceof StorageError && err.code === "QUOTA_EXCEEDED") {
          return { ok: false as const, error: "QUOTA" };
        }
        return { ok: false as const, error: "PARSE" };
      }
    },
    [appendLog, refreshStorageList],
  );

  return {
    project,
    projects,
    activeProjectId,
    setActiveProjectId: selectProject,
    view,
    setView,
    logs,
    codeInput,
    setCodeInput,
    stats,
    windowMode,
    setWindowMode,
    windowSize,
    setWindowSize,
    windowSizes,
    createNewProject,
    renameProject,
    clearActive,
    toggleLanguage,
    toggleAllLanguages,
    canonicalizeSnippet,
    ingestFiles,
    exportRegistry,
    registrySubview,
    setRegistrySubview,
    registryShowAll,
    toggleRegistryShowAll,
    expandAllRegistryTypes,
    collapseAllRegistryTypes,
    redundancySubview,
    setRedundancySubview,
    redundancyScan,
    runRedundancyScan,
    storageSaves,
    refreshStorageList,
    saveActiveToStorage,
    loadStorageSave,
    deleteStorageSave,
    exportSaveToFile,
    importSaveFromFile,
    setCrossLanguage: (v: boolean) => {
      if (!project) return;
      project.crossLanguageAnalysis = v;
      refreshProjects();
    },
    setStructuralOnly: (v: boolean) => {
      if (!project) return;
      project.structuralOnly = v;
      refreshProjects();
    },
  };
}

export type TensorraumStore = ReturnType<typeof useTensorraumStore>;
