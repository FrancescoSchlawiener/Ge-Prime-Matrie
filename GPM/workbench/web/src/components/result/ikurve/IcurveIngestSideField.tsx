import { useState } from "react";
import { t } from "../../../i18n/t";
import { Button } from "../../ui";
import type { IngestSourceMode } from "../../../lib/ikurve/curves";

export interface IcurveIngestSideFieldProps {
  sideLabel: string;
  sourceLegend: string;
  source: IngestSourceMode;
  gpmName: string;
  value: string;
  placeholder: string;
  disabled: boolean;
  onSourceChange: (v: IngestSourceMode) => void;
  onChange: (v: string) => void;
  onPaste: () => void;
  onTextFile: () => void;
  onGpmFile: () => void;
  onGpmDrop: (file: File) => void;
}

export function IcurveIngestSideField({
  sideLabel,
  sourceLegend,
  source,
  gpmName,
  value,
  placeholder,
  disabled,
  onSourceChange,
  onChange,
  onPaste,
  onTextFile,
  onGpmFile,
  onGpmDrop,
}: IcurveIngestSideFieldProps) {
  const [isDragging, setIsDragging] = useState(false);

  function handleDragOver(e: React.DragEvent) {
    e.preventDefault();
    setIsDragging(true);
  }

  function handleDragLeave(e: React.DragEvent) {
    e.preventDefault();
    setIsDragging(false);
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setIsDragging(false);
    const f = e.dataTransfer.files?.[0];
    if (f) onGpmDrop(f);
  }

  return (
    <div
      className={`gpm-ikurve-side ${isDragging ? "gpm-ikurve-side--dragging" : ""}`}
      onDragOver={handleDragOver}
      onDragEnter={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <h3 className="gpm-ikurve-side__title">{sideLabel}</h3>
      <fieldset className="gpm-ikurve-source-toggle" disabled={disabled}>
        <legend>{sourceLegend}</legend>
        <label>
          <input
            type="radio"
            name={`ikurve-source-${sideLabel}`}
            checked={source === "text"}
            onChange={() => onSourceChange("text")}
          />
          {t("ikurve.ingest.sourceText")}
        </label>
        <label>
          <input
            type="radio"
            name={`ikurve-source-${sideLabel}`}
            checked={source === "gpm"}
            onChange={() => onSourceChange("gpm")}
          />
          {t("ikurve.ingest.sourceGpm")}
        </label>
      </fieldset>
      {source === "gpm" ? (
        <div
          className="gpm-ikurve-gpm-drop"
          onClick={() => !disabled && onGpmFile()}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              if (!disabled) onGpmFile();
            }
          }}
          role="button"
          tabIndex={disabled ? -1 : 0}
        >
          <span className="gpm-ikurve-gpm-drop__label">{t("ikurve.ingest.dropLabel")}</span>
          <span className="gpm-metric__hint">{gpmName || t("ikurve.ingest.dropEmpty")}</span>
        </div>
      ) : null}
      <label className="gpm-field">
        <textarea
          className="gpm-textarea"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          rows={5}
          placeholder={placeholder}
        />
        <div className="gpm-form-row" style={{ marginTop: "0.35rem" }}>
          <Button type="button" variant="ghost" size="sm" onClick={onPaste} disabled={disabled}>
            {t("ikurve.ingest.paste")}
          </Button>
          <Button type="button" variant="ghost" size="sm" onClick={onTextFile} disabled={disabled}>
            {t("ikurve.ingest.file")}
          </Button>
        </div>
      </label>
    </div>
  );
}
