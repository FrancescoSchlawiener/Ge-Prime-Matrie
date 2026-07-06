const DECODE_KEY = "gpm-decode-draft";
const GPM_TEXT_KEY = "gpm-editor-draft";
const WORD_PAIR_KEY = "gpm-word-pair-draft";
const ICURVE_A_KEY = "gpm-icurve-a";

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

export function saveGpmDraft(text: string): void {
  sessionStorage.setItem(GPM_TEXT_KEY, text);
}

export function loadGpmDraft(): string | null {
  return sessionStorage.getItem(GPM_TEXT_KEY);
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
