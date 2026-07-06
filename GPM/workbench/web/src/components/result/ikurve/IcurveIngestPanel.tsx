import { useRef } from "react";
import { t } from "../../../i18n/t";
import { Button } from "../../ui";
import type { IngestSourceMode } from "../../../lib/ikurve/curves";
import { IcurveIngestSideField } from "./IcurveIngestSideField";
import { loadGpmOrText } from "./ingestLoader";

export { loadGpmOrText } from "./ingestLoader";

interface IcurveIngestPanelProps {
  textA: string;
  textB: string;
  sourceA: IngestSourceMode;
  sourceB: IngestSourceMode;
  gpmNameA: string;
  gpmNameB: string;
  locked: boolean;
  loading: boolean;
  onTextA: (v: string) => void;
  onTextB: (v: string) => void;
  onSourceA: (v: IngestSourceMode) => void;
  onSourceB: (v: IngestSourceMode) => void;
  onGpmNameA: (v: string) => void;
  onGpmNameB: (v: string) => void;
  onSubmit: () => void;
  onReset: () => void;
}

export function IcurveIngestPanel({
  textA,
  textB,
  sourceA,
  sourceB,
  gpmNameA,
  gpmNameB,
  locked,
  loading,
  onTextA,
  onTextB,
  onSourceA,
  onSourceB,
  onGpmNameA,
  onGpmNameB,
  onSubmit,
  onReset,
}: IcurveIngestPanelProps) {
  const fileARef = useRef<HTMLInputElement>(null);
  const fileBRef = useRef<HTMLInputElement>(null);
  const gpmARef = useRef<HTMLInputElement>(null);
  const gpmBRef = useRef<HTMLInputElement>(null);

  async function pasteSide(side: "a" | "b") {
    try {
      const text = await navigator.clipboard.readText();
      if (side === "a") {
        onSourceA("text");
        onTextA(text);
      } else {
        onSourceB("text");
        onTextB(text);
      }
    } catch {
      /* clipboard denied */
    }
  }

  async function loadGpmSide(side: "a" | "b", file: File) {
    const isGpm = file.name.endsWith(".gpm");
    const text = await loadGpmOrText(file);
    if (side === "a") {
      onSourceA(isGpm ? "gpm" : "text");
      if (isGpm) onGpmNameA(file.name);
      onTextA(text);
    } else {
      onSourceB(isGpm ? "gpm" : "text");
      if (isGpm) onGpmNameB(file.name);
      onTextB(text);
    }
  }

  return (
    <div className={locked ? "gpm-ikurve-ingest-locked" : undefined}>
      {locked ? (
        <p className="gpm-ikurve-ingest-lock-banner" role="status">
          {t("ikurve.ingest.lockBanner")}
        </p>
      ) : null}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit();
        }}
      >
        <div className="gpm-word-pair">
          <IcurveIngestSideField
            sideLabel={t("ikurve.sideA")}
            sourceLegend={t("ikurve.ingest.sourceLegendA")}
            source={sourceA}
            gpmName={gpmNameA}
            value={textA}
            placeholder={t("ikurve.ingest.placeholderA")}
            disabled={locked}
            onSourceChange={onSourceA}
            onChange={onTextA}
            onPaste={() => void pasteSide("a")}
            onTextFile={() => fileARef.current?.click()}
            onGpmFile={() => gpmARef.current?.click()}
            onGpmDrop={(f) => void loadGpmSide("a", f)}
          />
          <IcurveIngestSideField
            sideLabel={t("ikurve.sideB")}
            sourceLegend={t("ikurve.ingest.sourceLegendB")}
            source={sourceB}
            gpmName={gpmNameB}
            value={textB}
            placeholder={t("ikurve.ingest.placeholderB")}
            disabled={locked}
            onSourceChange={onSourceB}
            onChange={onTextB}
            onPaste={() => void pasteSide("b")}
            onTextFile={() => fileBRef.current?.click()}
            onGpmFile={() => gpmBRef.current?.click()}
            onGpmDrop={(f) => void loadGpmSide("b", f)}
          />
        </div>
        <input
          ref={fileARef}
          type="file"
          accept=".txt,.gpm,.md"
          hidden
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) void loadGpmSide("a", f);
          }}
        />
        <input
          ref={fileBRef}
          type="file"
          accept=".txt,.gpm,.md"
          hidden
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) void loadGpmSide("b", f);
          }}
        />
        <input
          ref={gpmARef}
          type="file"
          accept=".gpm"
          hidden
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) void loadGpmSide("a", f);
          }}
        />
        <input
          ref={gpmBRef}
          type="file"
          accept=".gpm"
          hidden
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) void loadGpmSide("b", f);
          }}
        />
        <div className="gpm-form-row" style={{ marginTop: "1rem" }}>
          {!locked ? (
            <Button type="submit" disabled={loading || !textA.trim() || !textB.trim()}>
              {loading ? t("ikurve.loading") : t("ikurve.submit")}
            </Button>
          ) : (
            <Button type="button" variant="ghost" onClick={onReset}>
              {t("ikurve.reset")}
            </Button>
          )}
        </div>
        {locked ? <p className="gpm-metric__hint">{t("ikurve.locked")}</p> : null}
      </form>
    </div>
  );
}
