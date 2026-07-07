import { useEffect, useState } from "react";
import { api, WorkbenchError } from "../../api/client";
import { t } from "../../i18n/t";
import { base64ToUint8Array, bytesStartWithMagic } from "../../utils/binaryBase64";
import { normalizeGpmFilename } from "../../utils/gpmFilename";
import { basenameWithoutExtension, ingestGpmOrTextFile } from "../../utils/gpmIngest";
import type { GpmDraft } from "../../utils/sessionBridge";

export type CipherMode = "word" | "prime" | "si" | "hardcore";
export type CipherDialogMode = "encrypt" | "decrypt";

const GPM_MIN_BYTES = 12;

export function useGpmDocument(initialDraft: GpmDraft) {
  const [text, setText] = useState(initialDraft.text);
  const [exportName, setExportName] = useState(initialDraft.exportName);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [documentRef, setDocumentRef] = useState<string | null>(null);
  const [stats, setStats] = useState<Record<string, unknown> | null>(null);
  const [cachedGpmBase64, setCachedGpmBase64] = useState<string | null>(null);

  function cacheFromBase64(b64: string) {
    if (!b64) {
      throw new WorkbenchError("gpm_invalid_stream", t("feedback.errors.gpm_invalid_stream"));
    }
    const bytes = base64ToUint8Array(b64);
    if (bytes.length < GPM_MIN_BYTES || !bytesStartWithMagic(bytes, "GPM")) {
      throw new WorkbenchError("gpm_invalid_stream", t("feedback.errors.gpm_invalid_stream"));
    }
    setCachedGpmBase64(b64);
  }

  function applyReadResult(r: Record<string, unknown>) {
    const ref = String(r.document_ref ?? "");
    if (ref) setDocumentRef(ref);
    else setDocumentRef(null);
    if (Object.keys(r).length > 1 || ref) setStats(r);
    else setStats(null);

    const reconstructedText = String(r.reconstructed_text ?? "");
    if (reconstructedText) setText(reconstructedText);

    const b64 = String(r.base64 ?? "");
    if (b64) cacheFromBase64(b64);
  }

  function resetTextIngestState(nextText: string, file: File) {
    setText(nextText);
    setDocumentRef(null);
    setStats(null);
    setCachedGpmBase64(null);
    setExportName(basenameWithoutExtension(file.name));
    setError(null);
  }

  async function cacheGpmExport(ref: string) {
    const resp = await api.gpmWrite(ref, "og");
    const b64 = String((resp.result as { base64?: string }).base64 ?? "");
    cacheFromBase64(b64);
  }

  async function compile() {
    setLoading(true);
    setError(null);
    setStats(null);
    setCachedGpmBase64(null);
    try {
      const resp = await api.compile("nl", text, "og");
      const result = resp.result as Record<string, unknown>;
      applyReadResult(result);
      const ref = String(result.document_ref ?? "");
      if (ref) await cacheGpmExport(ref);
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
      applyReadResult(resp.result as Record<string, unknown>);
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

  async function readGpmFile(
    file: File,
    key?: string,
  ): Promise<{ needsCipher: true; file: File } | { needsCipher: false }> {
    setLoading(true);
    setError(null);
    try {
      const resp = await api.gpmReadFile(file, key);
      applyReadResult(resp.result as Record<string, unknown>);
      setExportName(basenameWithoutExtension(file.name));
      return { needsCipher: false };
    } catch (err) {
      if (err instanceof WorkbenchError && err.code === "cipher_key_required" && !key) {
        return { needsCipher: true, file };
      }
      setError(err instanceof Error ? err.message : String(err));
      return { needsCipher: false };
    } finally {
      setLoading(false);
    }
  }

  async function ingestFile(
    file: File,
    key?: string,
  ): Promise<{ needsCipher: true; file: File } | { needsCipher: false }> {
    setLoading(true);
    setError(null);
    try {
      const ingested = await ingestGpmOrTextFile(file, key);
      if (ingested.kind === "text") {
        resetTextIngestState(ingested.text, file);
        return { needsCipher: false };
      }
      applyReadResult(ingested.result);
      setExportName(basenameWithoutExtension(file.name));
      return { needsCipher: false };
    } catch (err) {
      if (err instanceof WorkbenchError && err.code === "cipher_key_required" && !key) {
        return { needsCipher: true, file };
      }
      setError(err instanceof Error ? err.message : String(err));
      return { needsCipher: false };
    } finally {
      setLoading(false);
    }
  }

  function downloadGpm(suffix: ".gpm" | ".gpc" = ".gpm") {
    if (!cachedGpmBase64) return;
    const bytes = base64ToUint8Array(cachedGpmBase64);
    if (bytes.length < GPM_MIN_BYTES || !bytesStartWithMagic(bytes, "GPM")) {
      setError(t("feedback.errors.gpm_invalid_stream"));
      return;
    }
    const blob = new Blob([Uint8Array.from(bytes)], { type: "application/octet-stream" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = normalizeGpmFilename(exportName, suffix);
    a.click();
    URL.revokeObjectURL(url);
  }

  function clearDocument() {
    setText("");
    setDocumentRef(null);
    setStats(null);
    setExportName("document");
    setCachedGpmBase64(null);
    setError(null);
  }

  return {
    text,
    setText,
    exportName,
    setExportName,
    loading,
    error,
    setError,
    documentRef,
    stats,
    cachedGpmBase64,
    compile,
    ingestFile,
    readGpmBase64,
    readGpmFile,
    downloadGpm,
    clearDocument,
  };
}

export function useGpmDraftPersistence(draft: GpmDraft, saveDraft: (draft: GpmDraft) => void) {
  useEffect(() => {
    saveDraft(draft);
  }, [draft, saveDraft]);
}
