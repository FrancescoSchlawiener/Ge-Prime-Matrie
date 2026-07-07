import { useRef } from "react";
import { t } from "../../i18n/t";
import { GpmDocumentMetaBar } from "./GpmDocumentMetaBar";
import { GpmEditorResults } from "./GpmEditorResults";
import { GpmEditorToolbar } from "./GpmEditorToolbar";
import { GpmExportBar } from "./GpmExportBar";
import { GpmSourceEditor } from "./GpmSourceEditor";

interface GpmEditorWorkspaceProps {
  text: string;
  exportName: string;
  loading: boolean;
  cachedGpmBase64: string | null;
  stats: Record<string, unknown> | null;
  onTextChange: (v: string) => void;
  onExportNameChange: (v: string) => void;
  onCompile: () => void;
  onClear: () => void;
  onFile: (file: File) => void;
  onOpenICurve: () => void;
  onDownload: () => void;
  onCipher: () => void;
}

export function GpmEditorWorkspace({
  text,
  exportName,
  loading,
  cachedGpmBase64,
  stats,
  onTextChange,
  onExportNameChange,
  onCompile,
  onClear,
  onFile,
  onOpenICurve,
  onDownload,
  onCipher,
}: GpmEditorWorkspaceProps) {
  const fileRef = useRef<HTMLInputElement>(null);

  return (
    <div className="gpm-editor-workspace">
      <header className="gpm-editor-workspace__header">
        <strong>{t("gpm.title")}</strong>
        <span>{t("gpm.workspace.formatBadge")}</span>
      </header>
      <div className="gpm-editor-workspace__body">
        <GpmSourceEditor text={text} onTextChange={onTextChange} onFile={onFile} />
        <GpmExportBar exportName={exportName} onExportNameChange={onExportNameChange} />
        <GpmEditorToolbar
          loading={loading}
          cachedGpmBase64={cachedGpmBase64}
          onCompile={onCompile}
          onClear={onClear}
          onLoadFile={() => fileRef.current?.click()}
          onDownload={onDownload}
          onOpenICurve={onOpenICurve}
          onCipher={onCipher}
        />
        <input
          ref={fileRef}
          type="file"
          accept=".gpm,.gpc,.txt,.md,text/*"
          hidden
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) onFile(f);
          }}
        />
      </div>
      <GpmDocumentMetaBar stats={stats} />
      <GpmEditorResults stats={stats} />
    </div>
  );
}
