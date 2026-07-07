import { IGNORED_SUFFIXES, SUPPORTED_LANGUAGES } from "./constants";
import type { LanguageConfig } from "./types";

export type FileDetection =
  | { status: "ok"; lang: LanguageConfig }
  | { status: "ignored" }
  | { status: "unknown" };

export function detectFileLanguage(filename: string): FileDetection {
  const basename = filename.split(/[\\/]/).pop()?.toLowerCase() ?? "";
  for (const suffix of IGNORED_SUFFIXES) {
    if (basename.endsWith(suffix)) return { status: "ignored" };
  }
  if (!basename.includes(".")) return { status: "unknown" };
  for (const lang of SUPPORTED_LANGUAGES) {
    for (const ext of lang.ext) {
      if (basename.endsWith(ext)) return { status: "ok", lang };
    }
  }
  return { status: "unknown" };
}
