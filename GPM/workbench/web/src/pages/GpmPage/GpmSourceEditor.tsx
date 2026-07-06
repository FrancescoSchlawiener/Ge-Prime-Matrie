import { useState } from "react";
import { t } from "../../i18n/t";

interface GpmSourceEditorProps {
  text: string;
  onTextChange: (v: string) => void;
  onFile: (file: File) => void;
}

export function GpmSourceEditor({ text, onTextChange, onFile }: GpmSourceEditorProps) {
  const [isDragging, setIsDragging] = useState(false);

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setIsDragging(false);
    const f = e.dataTransfer.files?.[0];
    if (f) onFile(f);
  }

  const showOverlay = isDragging || !text.trim();

  return (
    <div className="gpm-editor">
      <div className="gpm-editor__chrome">
        <span className="gpm-editor__dot gpm-editor__dot--red" />
        <span className="gpm-editor__dot gpm-editor__dot--yellow" />
        <span className="gpm-editor__dot gpm-editor__dot--green" />
        <span>{t("gpm.workspace.fileLabel")}</span>
      </div>
      <div
        className="gpm-editor__surface"
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
      >
        {showOverlay ? <div className="gpm-editor__drop-overlay">{t("gpm.workspace.dropOverlay")}</div> : null}
        <textarea
          className="gpm-editor__textarea gpm-editor__textarea--workspace"
          value={text}
          onChange={(e) => onTextChange(e.target.value)}
          placeholder={t("gpm.sourcePlaceholder")}
          spellCheck={false}
        />
      </div>
    </div>
  );
}
