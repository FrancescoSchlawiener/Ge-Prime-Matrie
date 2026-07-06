import { api } from "../../../api/client";
import { arrayBufferToBase64 } from "../../../utils/binaryBase64";

export async function loadGpmOrText(file: File): Promise<string> {
  if (file.name.endsWith(".gpm")) {
    const buf = await file.arrayBuffer();
    const base64 = arrayBufferToBase64(buf);
    const resp = await api.gpmRead(base64);
    const r = resp.result as { reconstructed_text?: string; document_ref?: string };
    const direct = String(r.reconstructed_text ?? "");
    if (direct) return direct;
    const ref = String(r.document_ref ?? "");
    if (ref) {
      const recon = await api.reconstruct(ref, "nl");
      return String((recon.result as { text?: string }).text ?? "");
    }
    return "";
  }
  return file.text();
}
