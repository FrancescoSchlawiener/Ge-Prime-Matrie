import { useState } from "react";
import { api } from "../../api/client";
import type { CipherDialogMode, CipherMode } from "./useGpmDocument";

interface UseGpmCipherOptions {
  text: string;
  loading: boolean;
  setError: (msg: string | null) => void;
  readGpmBase64: (base64: string, key?: string) => Promise<{ needsCipher: true; base64: string } | { needsCipher: false }>;
}

export function useGpmCipher({ text, loading, setError, readGpmBase64 }: UseGpmCipherOptions) {
  const [open, setOpen] = useState(false);
  const [mode, setMode] = useState<CipherDialogMode>("encrypt");
  const [cipherMode, setCipherMode] = useState<CipherMode>("word");
  const [key, setKey] = useState("");
  const [pendingBlob, setPendingBlob] = useState<string | null>(null);
  const [cipherOut, setCipherOut] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  function openEncrypt() {
    setMode("encrypt");
    setCipherOut(null);
    setError(null);
    setOpen(true);
  }

  function openDecrypt(base64: string) {
    setMode("decrypt");
    setPendingBlob(base64);
    setCipherOut(null);
    setError(null);
    setOpen(true);
  }

  function close() {
    setOpen(false);
    setPendingBlob(null);
    setCipherOut(null);
  }

  async function submit() {
    if (!key.trim()) return;
    setBusy(true);
    setError(null);
    try {
      if (mode === "decrypt" && pendingBlob) {
        const result = await readGpmBase64(pendingBlob, key);
        if (!result.needsCipher) close();
      } else {
        const resp = await api.cipherEncrypt(text, key, cipherMode);
        const out = String((resp.result as { ciphertext?: string }).ciphertext ?? "");
        const fallback = String((resp.result as { base64?: string }).base64 ?? "");
        setCipherOut(out || fallback || "OK");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return {
    open,
    mode,
    cipherMode,
    key,
    cipherOut,
    busy: busy || loading,
    setCipherMode,
    setKey,
    openEncrypt,
    openDecrypt,
    close,
    submit,
  };
}
