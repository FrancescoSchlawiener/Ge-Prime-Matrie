const DECODE_KEY = "gpm-decode-draft";
const GPM_TEXT_KEY = "gpm-editor-draft";
const GPM_EXPORT_NAME_KEY = "gpm-editor-export-name";
const WORD_PAIR_KEY = "gpm-word-pair-draft";
const ICURVE_A_KEY = "gpm-icurve-a";

export interface GpmDraft {
  text: string;
  exportName: string;
}

export function saveDecodeDraft(substance: number, index: number): void {
  sessionStorage.setItem(DECODE_KEY, `${substance}\n${index}`);
}

export function loadDecodeDraft(): { substance: string; index: string } | null {
  const raw = sessionStorage.getItem(DECODE_KEY);
  if (!raw) return null;
  const [substance, index] = raw.split("\n");
  if (!substance || !index) return null;
  return { substance, index };
}

export function saveGpmDraft(draft: GpmDraft): void {
  sessionStorage.setItem(GPM_TEXT_KEY, draft.text);
  sessionStorage.setItem(GPM_EXPORT_NAME_KEY, draft.exportName);
}

export function loadGpmDraft(): GpmDraft | null {
  const raw = sessionStorage.getItem(GPM_TEXT_KEY);
  if (raw === null) return null;
  if (raw.startsWith("{")) {
    try {
      const parsed = JSON.parse(raw) as Partial<GpmDraft>;
      return {
        text: String(parsed.text ?? ""),
        exportName: String(parsed.exportName ?? "document") || "document",
      };
    } catch {
      return { text: raw, exportName: "document" };
    }
  }
  const storedName = sessionStorage.getItem(GPM_EXPORT_NAME_KEY);
  if (storedName !== null) {
    return { text: raw, exportName: storedName || "document" };
  }
  return { text: raw, exportName: "document" };
}

export function saveWordPairDraft(wordA: string, wordB: string): void {
  sessionStorage.setItem(WORD_PAIR_KEY, `${wordA}\n${wordB}`);
}

export function loadWordPairDraft(): { wordA: string; wordB: string } | null {
  const raw = sessionStorage.getItem(WORD_PAIR_KEY);
  if (!raw) return null;
  const [wordA, wordB] = raw.split("\n");
  return { wordA: wordA ?? "", wordB: wordB ?? "" };
}

export function saveICurveSideA(text: string): void {
  sessionStorage.setItem(ICURVE_A_KEY, text);
}

export function loadICurveSideA(): string | null {
  return sessionStorage.getItem(ICURVE_A_KEY);
}
