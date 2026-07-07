import { t } from "../../i18n/t";
import { sanitizeExportBaseName } from "../../utils/gpmFilename";

interface GpmExportBarProps {
  exportName: string;
  onExportNameChange: (name: string) => void;
  exportSuffix?: ".gpm" | ".gpc";
}

export function GpmExportBar({
  exportName,
  onExportNameChange,
  exportSuffix = ".gpm",
}: GpmExportBarProps) {
  const suffixLabel =
    exportSuffix === ".gpc" ? t("gpm.workspace.exportSuffixGpc") : t("gpm.workspace.exportSuffixGpm");

  return (
    <div className="gpm-export-bar">
      <label className="gpm-export-bar__label" htmlFor="gpm-export-name">
        {t("gpm.workspace.exportName")}
      </label>
      <div className="gpm-export-bar__field">
        <input
          id="gpm-export-name"
          className="gpm-export-bar__input"
          type="text"
          value={exportName}
          spellCheck={false}
          autoComplete="off"
          onChange={(e) => onExportNameChange(sanitizeExportBaseName(e.target.value))}
        />
        <span className="gpm-export-bar__suffix" aria-hidden="true">
          {suffixLabel}
        </span>
      </div>
    </div>
  );
}
