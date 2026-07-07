import { t } from "../../i18n/t";
import { Button } from "../../components/ui";

interface GpmEditorToolbarProps {
  loading: boolean;
  cachedGpmBase64: string | null;
  onCompile: () => void;
  onClear: () => void;
  onLoadFile: () => void;
  onDownload: () => void;
  onOpenICurve: () => void;
  onCipher: () => void;
}

export function GpmEditorToolbar({
  loading,
  cachedGpmBase64,
  onCompile,
  onClear,
  onLoadFile,
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
        {cachedGpmBase64 ? (
          <Button variant="ghost" onClick={onDownload}>
            {t("gpm.download")}
          </Button>
        ) : null}
      </div>
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
