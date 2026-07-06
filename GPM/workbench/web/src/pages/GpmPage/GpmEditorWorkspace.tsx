import { useRef } from "react";
import { t } from "../../i18n/t";
import { GpmDocumentMetaBar } from "./GpmDocumentMetaBar";
import { GpmEditorResults } from "./GpmEditorResults";
import { GpmEditorToolbar } from "./GpmEditorToolbar";
import { GpmSourceEditor } from "./GpmSourceEditor";

interface GpmEditorWorkspaceProps {
  text: string;
  loading: boolean;
  documentRef: string | null;
  stats: Record<string, unknown> | null;
  reconstructed: string | null;
  fileName: string | null;
  onTextChange: (v: string) => void;
  onCompile: () => void;
  onClear: () => void;
  onFile: (file: File) => void;
  onReconstruct: () => void;
  onOpenICurve: () => void;
  onDownload: () => void;
  onCipher: () => void;
}

export function GpmEditorWorkspace({
  text,
  loading,
  documentRef,
  stats,
  reconstructed,
  fileName,
  onTextChange,
  onCompile,
  onClear,
  onFile,
  onReconstruct,
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
        {fileName ? <span>{fileName}</span> : null}
      </header>
      <div className="gpm-editor-workspace__body">
        <GpmSourceEditor text={text} onTextChange={onTextChange} onFile={onFile} />
        <GpmEditorToolbar
          loading={loading}
          documentRef={documentRef}
          onCompile={onCompile}
          onClear={onClear}
          onLoadFile={() => fileRef.current?.click()}
          onReconstruct={onReconstruct}
          onDownload={onDownload}
          onOpenICurve={onOpenICurve}
          onCipher={onCipher}
        />
        <input
          ref={fileRef}
          type="file"
          accept=".gpm,.gpc"
          hidden
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) onFile(f);
          }}
        />
      </div>
      <GpmDocumentMetaBar documentRef={documentRef} stats={stats} />
      <GpmEditorResults stats={stats} reconstructed={reconstructed} />
    </div>
  );
}
