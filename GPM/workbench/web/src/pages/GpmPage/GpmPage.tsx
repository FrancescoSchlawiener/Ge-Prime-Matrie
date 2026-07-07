import { useNavigate } from "react-router-dom";
import { t } from "../../i18n/t";
import { PageHead } from "../../components/ui";
import { loadGpmDraft, saveGpmDraft, saveICurveSideA } from "../../utils/sessionBridge";
import { GpmCipherDialog } from "./GpmCipherDialog";
import { GpmEditorWorkspace } from "./GpmEditorWorkspace";
import { GpmSearchPanel } from "./GpmSearchPanel";
import { useGpmCipher } from "./useGpmCipher";
import { useGpmDocument, useGpmDraftPersistence } from "./useGpmDocument";

export function GpmPage() {
  const navigate = useNavigate();
  const gpm = useGpmDocument(loadGpmDraft() ?? { text: "", exportName: "document" });
  const cipher = useGpmCipher({
    text: gpm.text,
    loading: gpm.loading,
    setError: gpm.setError,
    readGpmBase64: gpm.readGpmBase64,
    readGpmFile: gpm.readGpmFile,
  });

  useGpmDraftPersistence({ text: gpm.text, exportName: gpm.exportName }, saveGpmDraft);

  function openInICurve() {
    saveICurveSideA(gpm.text);
    navigate("/vergleichen/ikurve");
  }

  async function handleFile(file: File) {
    const result = await gpm.ingestFile(file);
    if (result.needsCipher) cipher.openDecryptFile(result.file);
  }

  return (
    <div className="gpm-page gpm-page--gpm">
      <PageHead title={t("gpm.title")} lead={t("gpm.lead")} />
      <GpmEditorWorkspace
        text={gpm.text}
        exportName={gpm.exportName}
        loading={gpm.loading}
        cachedGpmBase64={gpm.cachedGpmBase64}
        stats={gpm.stats}
        onTextChange={gpm.setText}
        onExportNameChange={gpm.setExportName}
        onCompile={() => void gpm.compile()}
        onClear={gpm.clearDocument}
        onFile={(f) => void handleFile(f)}
        onOpenICurve={openInICurve}
        onDownload={() => gpm.downloadGpm()}
        onCipher={cipher.openEncrypt}
      />
      <GpmSearchPanel documentRef={gpm.documentRef} />
      <GpmCipherDialog
        open={cipher.open}
        mode={cipher.mode}
        cipherMode={cipher.cipherMode}
        cipherKey={cipher.key}
        cipherOut={cipher.cipherOut}
        loading={cipher.busy}
        onModeChange={cipher.setCipherMode}
        onKeyChange={cipher.setKey}
        onSubmit={() => void cipher.submit()}
        onClose={cipher.close}
      />
      {gpm.error ? <div className="gpm-error">{gpm.error}</div> : null}
    </div>
  );
}
