import { useEffect, useRef, useState, type DragEvent, type KeyboardEvent } from "react";
import { SegmentToggle } from "../../../components/ui/SegmentToggle";
import { Input } from "../../../components/ui";
import { t } from "../../../i18n/t";
import { SUPPORTED_LANGUAGES } from "../../../lib/tensorraum";
import type { TensorraumStore } from "../hooks/useTensorraumStore";

interface TensorraumSidebarProps {
  store: TensorraumStore;
}

export function TensorraumSidebar({ store }: TensorraumSidebarProps) {
  const fileRef = useRef<HTMLInputElement>(null);
  const folderRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [draftName, setDraftName] = useState("");
  const { project, projects, stats } = store;
  const activeId = store.activeProjectId;

  useEffect(() => {
    setDraftName(project?.name ?? "");
  }, [activeId, project?.name]);

  if (!project || !stats) return null;

  function onDrop(e: DragEvent) {
    e.preventDefault();
    setDragOver(false);
    const files = e.dataTransfer.files;
    if (files.length) void store.ingestFiles(files);
  }

  function commitName() {
    const trimmed = draftName.trim();
    if (trimmed && trimmed !== project.name) {
      store.renameProject(trimmed);
    } else {
      setDraftName(project.name);
    }
  }

  function onNameKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") {
      e.currentTarget.blur();
    }
  }

  return (
    <aside className="gpm-tensor-sidebar custom-scrollbar">
      <section className="gpm-tensor-sidebar__block">
        <h2 className="gpm-tensor-sidebar__label">{t("tensorraum.sidebar.project")}</h2>
        <Input
          className="gpm-input gpm-tensor-project-name"
          value={draftName}
          placeholder={t("tensorraum.sidebar.projectNamePlaceholder")}
          aria-label={t("tensorraum.sidebar.project")}
          onChange={(e) => setDraftName(e.target.value)}
          onBlur={commitName}
          onKeyDown={onNameKeyDown}
        />
        <div className="gpm-tensor-project-list">
          {projects.map((p) => (
            <button
              key={p.id}
              type="button"
              className={`gpm-tensor-project-btn${p.id === store.activeProjectId ? " gpm-tensor-project-btn--active" : ""}`}
              onClick={() => store.setActiveProjectId(p.id)}
            >
              {p.name}
              {p.sourceSaveId ? (
                <span className="gpm-tensor-project-badge">{t("tensorraum.storage.fromStorageBadge")}</span>
              ) : null}
            </button>
          ))}
        </div>
        <div className="gpm-tensor-sidebar__row gpm-tensor-sidebar__row--actions">
          <button
            type="button"
            className="gpm-btn gpm-btn--sm gpm-btn--secondary gpm-tensor-sidebar-action"
            title={t("tensorraum.sidebar.newProject")}
            onClick={store.createNewProject}
          >
            {t("tensorraum.sidebar.newProject")}
          </button>
        </div>
      </section>

      <section className="gpm-tensor-sidebar__block">
        <h2 className="gpm-tensor-sidebar__label">{t("tensorraum.sidebar.ingest")}</h2>
        <div
          className={`gpm-tensor-drop${dragOver ? " gpm-tensor-drop--active" : ""}`}
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={onDrop}
          onClick={() => fileRef.current?.click()}
          role="button"
          tabIndex={0}
        >
          <p>{t("tensorraum.sidebar.dropHint")}</p>
          <div className="gpm-tensor-sidebar__row gpm-tensor-drop__actions">
            <button
              type="button"
              className="gpm-btn gpm-btn--sm gpm-btn--secondary"
              onClick={(e) => {
                e.stopPropagation();
                fileRef.current?.click();
              }}
            >
              {t("tensorraum.sidebar.filesBtn")}
            </button>
            <button
              type="button"
              className="gpm-btn gpm-btn--sm gpm-btn--secondary"
              onClick={(e) => {
                e.stopPropagation();
                folderRef.current?.click();
              }}
            >
              {t("tensorraum.sidebar.folderBtn")}
            </button>
          </div>
        </div>
        <input
          ref={fileRef}
          type="file"
          multiple
          className="sr-only"
          onChange={(e) => {
            if (e.target.files?.length) void store.ingestFiles(e.target.files);
            e.target.value = "";
          }}
        />
        <input
          ref={folderRef}
          type="file"
          multiple
          className="sr-only"
          {...({ webkitdirectory: "", directory: "" } as Record<string, string>)}
          onChange={(e) => {
            if (e.target.files?.length) void store.ingestFiles(e.target.files);
            e.target.value = "";
          }}
        />
      </section>

      <section className="gpm-tensor-sidebar__block">
        <div className="gpm-tensor-sidebar__row gpm-tensor-sidebar__row--between">
          <h2 className="gpm-tensor-sidebar__label">{t("tensorraum.sidebar.languageFilter")}</h2>
          <button type="button" className="gpm-btn gpm-btn--sm gpm-btn--secondary" onClick={store.toggleAllLanguages}>
            {t("tensorraum.sidebar.toggleAllLanguages")}
          </button>
        </div>
        <div className="gpm-tensor-lang-chips">
          {SUPPORTED_LANGUAGES.map((lang) => {
            const active = project.activeLanguageIds.has(lang.id);
            return (
              <button
                key={lang.id}
                type="button"
                className={`gpm-tensor-lang-chip${active ? " gpm-tensor-lang-chip--active" : ""}`}
                onClick={() => store.toggleLanguage(lang.id)}
              >
                {lang.id.toUpperCase()}
              </button>
            );
          })}
        </div>
        <label className="gpm-tensor-check">
          <input
            type="checkbox"
            checked={project.crossLanguageAnalysis}
            onChange={(e) => store.setCrossLanguage(e.target.checked)}
          />
          <span>{t("tensorraum.sidebar.crossLanguage")}</span>
        </label>
        <label className="gpm-tensor-check">
          <input
            type="checkbox"
            checked={project.structuralOnly}
            onChange={(e) => store.setStructuralOnly(e.target.checked)}
          />
          <span>{t("tensorraum.sidebar.structuralOnly")}</span>
        </label>
      </section>

      <section className="gpm-tensor-sidebar__block">
        <div className="gpm-tensor-sidebar__row gpm-tensor-sidebar__row--between">
          <h2 className="gpm-tensor-sidebar__label">{t("tensorraum.sidebar.windowTitle")}</h2>
          <span className="gpm-tensor-window-size">
            {store.windowMode === "adaptive"
              ? t("tensorraum.sidebar.windowAdaptiveRange")
              : t("tensorraum.sidebar.windowSize", { count: String(store.windowSize) })}
          </span>
        </div>
        <SegmentToggle
          name="tensor-window-mode"
          value={store.windowMode}
          options={[
            { value: "fixed", label: t("tensorraum.sidebar.windowFixed") },
            { value: "adaptive", label: t("tensorraum.sidebar.windowAdaptive") },
          ]}
          onChange={store.setWindowMode}
        />
        <div className="gpm-tensor-window-body">
          {store.windowMode === "fixed" ? (
            <>
              <input
                type="range"
                min={8}
                max={30}
                value={store.windowSize}
                onChange={(e) => store.setWindowSize(Number(e.target.value))}
                className="gpm-tensor-slider"
              />
              <p className="gpm-metric__hint">{t("tensorraum.sidebar.windowFixedHint")}</p>
            </>
          ) : (
            <p className="gpm-metric__hint">{t("tensorraum.sidebar.windowAdaptiveHint")}</p>
          )}
        </div>
      </section>

      <section className="gpm-tensor-sidebar__stats">
        <div>
          <span>{t("tensorraum.sidebar.statFiles")}</span>
          <strong>{stats.files}</strong>
        </div>
        <div>
          <span>{t("tensorraum.sidebar.statSpaces")}</span>
          <strong>{stats.spaces}</strong>
        </div>
        <div>
          <span>{t("tensorraum.sidebar.statPointers")}</span>
          <strong>{stats.pointers}</strong>
        </div>
        <div>
          <span>{t("tensorraum.sidebar.statLanguages")}</span>
          <strong>
            {stats.activeLanguages}/{stats.totalLanguages}
          </strong>
        </div>
        <button type="button" className="gpm-btn gpm-btn--sm gpm-btn--secondary gpm-tensor-export" onClick={store.exportRegistry}>
          {t("tensorraum.sidebar.exportRegistry")}
        </button>
        <button type="button" className="gpm-btn gpm-btn--sm gpm-btn--secondary gpm-tensor-clear" onClick={store.clearActive}>
          {t("tensorraum.sidebar.clearProject")}
        </button>
      </section>
    </aside>
  );
}
