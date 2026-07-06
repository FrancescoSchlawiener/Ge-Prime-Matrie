import { t } from "../../i18n/t";
import { Button } from "../../components/ui";

interface GpmEditorToolbarProps {
  loading: boolean;
  documentRef: string | null;
  onCompile: () => void;
  onClear: () => void;
  onLoadFile: () => void;
  onReconstruct: () => void;
  onDownload: () => void;
  onOpenICurve: () => void;
  onCipher: () => void;
}

export function GpmEditorToolbar({
  loading,
  documentRef,
  onCompile,
  onClear,
  onLoadFile,
  onReconstruct,
  onDownload,
  onOpenICurve,
  onCipher,
}: GpmEditorToolbarProps) {
  return (
    <div className="gpm-editor-toolbar">
      <div className="gpm-editor-toolbar__group">
        <Button onClick={onCompile} disabled={loading} data-testid="compile">
          {loading ? t("gpm.loading") : t("gpm.compile")}
        </Button>
        <Button variant="ghost" onClick={onClear}>
          {t("gpm.clear")}
        </Button>
      </div>
      <div className="gpm-editor-toolbar__group">
        <Button variant="ghost" onClick={onLoadFile}>
          {t("gpm.readFile")}
        </Button>
        {documentRef ? (
          <Button variant="ghost" onClick={onDownload}>
            {t("gpm.download")}
          </Button>
        ) : null}
      </div>
      {documentRef ? (
        <div className="gpm-editor-toolbar__group">
          <Button variant="ghost" onClick={onReconstruct}>
            {t("gpm.reconstruct")}
          </Button>
        </div>
      ) : null}
      <div className="gpm-editor-toolbar__group">
        <Button variant="ghost" onClick={onCipher}>
          {t("gpm.toolbar.cipher")}
        </Button>
        <Button variant="ghost" onClick={onOpenICurve}>
          {t("gpm.openInICurve")}
        </Button>
      </div>
    </div>
  );
}
