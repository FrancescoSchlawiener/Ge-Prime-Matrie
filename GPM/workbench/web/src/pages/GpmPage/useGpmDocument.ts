import { useEffect, useState } from "react";
import { api, WorkbenchError } from "../../api/client";
import { t } from "../../i18n/t";
import { arrayBufferToBase64, base64ToUint8Array, bytesStartWithMagic } from "../../utils/binaryBase64";

export type CipherMode = "word" | "prime" | "si" | "hardcore";
export type CipherDialogMode = "encrypt" | "decrypt";

const GPM_MIN_BYTES = 12;

export function useGpmDocument(initialText = "") {
  const [text, setText] = useState(initialText);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [documentRef, setDocumentRef] = useState<string | null>(null);
  const [stats, setStats] = useState<Record<string, unknown> | null>(null);
  const [reconstructed, setReconstructed] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);

  async function applyReadResult(r: Record<string, unknown>) {
    const ref = String(r.document_ref ?? "");
    if (ref) setDocumentRef(ref);
    if (Object.keys(r).length > 1 || ref) setStats(r);
    let reconstructedText = String(r.reconstructed_text ?? "");
    if (!reconstructedText && ref) {
      try {
        const resp = await api.reconstruct(ref, "nl");
        reconstructedText = String((resp.result as { text?: string }).text ?? "");
      } catch {
        /* reconstruct optional fallback */
      }
    }
    if (reconstructedText) setText(reconstructedText);
  }

  async function compile() {
    setLoading(true);
    setError(null);
    setStats(null);
    setReconstructed(null);
    try {
      const resp = await api.compile("nl", text, "og");
      await applyReadResult(resp.result as Record<string, unknown>);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  async function reconstruct() {
    if (!documentRef) return;
    setLoading(true);
    try {
      const resp = await api.reconstruct(documentRef, "nl");
      setReconstructed(String((resp.result as { text?: string }).text ?? ""));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  async function readGpmBase64(
    base64: string,
    key?: string,
  ): Promise<{ needsCipher: true; base64: string } | { needsCipher: false }> {
    setLoading(true);
    setError(null);
    try {
      const resp = await api.gpmRead(base64, key);
      await applyReadResult(resp.result as Record<string, unknown>);
      return { needsCipher: false };
    } catch (err) {
      if (err instanceof WorkbenchError && err.code === "cipher_key_required" && !key) {
        return { needsCipher: true, base64 };
      }
      setError(err instanceof Error ? err.message : String(err));
      return { needsCipher: false };
    } finally {
      setLoading(false);
    }
  }

  async function loadFile(file: File): Promise<{ needsCipher: true; base64: string } | { needsCipher: false }> {
    const buf = await file.arrayBuffer();
    const bytes = new Uint8Array(buf);
    if (!bytesStartWithMagic(bytes, "GPM") && !bytesStartWithMagic(bytes, "GPC")) {
      setError(t("feedback.errors.gpm_invalid_stream"));
      return { needsCipher: false };
    }
    const base64 = arrayBufferToBase64(buf);
    setFileName(file.name);
    return readGpmBase64(base64);
  }

  async function downloadGpm() {
    if (!documentRef) return;
    setLoading(true);
    try {
      const resp = await api.gpmWrite(documentRef, "og");
      const b64 = String((resp.result as { base64?: string }).base64 ?? "");
      if (!b64) {
        setError(t("feedback.errors.gpm_invalid_stream"));
        return;
      }
      const bytes = base64ToUint8Array(b64);
      if (bytes.length < GPM_MIN_BYTES || !bytesStartWithMagic(bytes, "GPM")) {
        setError(t("feedback.errors.gpm_invalid_stream"));
        return;
      }
      const blob = new Blob([Uint8Array.from(bytes)], { type: "application/octet-stream" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = fileName?.endsWith(".gpm") ? fileName : "document.gpm";
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  function clearDocument() {
    setText("");
    setDocumentRef(null);
    setStats(null);
    setReconstructed(null);
    setFileName(null);
    setError(null);
  }

  return {
    text,
    setText,
    loading,
    error,
    setError,
    documentRef,
    stats,
    reconstructed,
    fileName,
    compile,
    reconstruct,
    loadFile,
    readGpmBase64,
    downloadGpm,
    clearDocument,
  };
}

export function useGpmDraftPersistence(text: string, saveDraft: (text: string) => void) {
  useEffect(() => {
    saveDraft(text);
  }, [text, saveDraft]);
}
