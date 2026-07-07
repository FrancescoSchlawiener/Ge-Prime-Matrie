import type { LanguageConfig } from "./types";

export const BIG_PRIME = 100000000000000003n;

export const PRIME_ALPHABET: Record<string, bigint> = {
  E: 2n,
  A: 3n,
  O: 5n,
  I: 7n,
  T: 11n,
  N: 13n,
  R: 17n,
  S: 19n,
  L: 23n,
  C: 29n,
  D: 31n,
  U: 37n,
  M: 41n,
  P: 43n,
  H: 47n,
  G: 53n,
  B: 59n,
  F: 61n,
  Y: 67n,
  W: 71n,
  K: 73n,
  V: 79n,
  X: 83n,
  Z: 89n,
  J: 97n,
  Q: 101n,
  "ẞ": 103n,
};

/** @deprecated Nur UI-Fallback bis API-Sprachen geladen — siehe lib/code/languages.ts */
export const SUPPORTED_LANGUAGES: LanguageConfig[] = [
  { id: "js", name: "JavaScript/TS", ext: [".js", ".ts", ".jsx", ".tsx"], blockStyle: "brace", commentStyle: "c" },
  { id: "py", name: "Python", ext: [".py"], blockStyle: "indent", commentStyle: "hash" },
  { id: "html", name: "HTML", ext: [".html", ".htm"], blockStyle: "tag", commentStyle: "none" },
  { id: "css", name: "CSS", ext: [".css"], blockStyle: "brace", commentStyle: "c" },
];

export const ADAPTIVE_WINDOW_SIZES = [8, 12, 16, 20, 24, 28] as const;
export const MIN_CHAIN_LENGTH = 8;
export const DEFAULT_WINDOW_SIZE = 15;
