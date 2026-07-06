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
  const gpm = useGpmDocument(loadGpmDraft() ?? "");
  const cipher = useGpmCipher({
    text: gpm.text,
    loading: gpm.loading,
    setError: gpm.setError,
    readGpmBase64: gpm.readGpmBase64,
  });

  useGpmDraftPersistence(gpm.text, saveGpmDraft);

  function openInICurve() {
    saveICurveSideA(gpm.reconstructed ?? gpm.text);
    navigate("/vergleichen/ikurve");
  }

  async function handleFile(file: File) {
    const result = await gpm.loadFile(file);
    if (result.needsCipher) cipher.openDecrypt(result.base64);
  }

  return (
    <div className="gpm-page gpm-page--gpm">
      <PageHead title={t("gpm.title")} lead={t("gpm.lead")} />
      <GpmEditorWorkspace
        text={gpm.text}
        loading={gpm.loading}
        documentRef={gpm.documentRef}
        stats={gpm.stats}
        reconstructed={gpm.reconstructed}
        fileName={gpm.fileName}
        onTextChange={gpm.setText}
        onCompile={() => void gpm.compile()}
        onClear={gpm.clearDocument}
        onFile={(f) => void handleFile(f)}
        onReconstruct={() => void gpm.reconstruct()}
        onOpenICurve={openInICurve}
        onDownload={() => void gpm.downloadGpm()}
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
