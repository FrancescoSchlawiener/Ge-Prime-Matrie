import { fetchLanguages, getLanguagesCache, languageForExtension, languageSpecToConfig } from "../code/languages";
import type { LanguageConfig } from "./types";

export type FileDetection =
  | { status: "ok"; lang: LanguageConfig }
  | { status: "ignored" }
  | { status: "unknown" };

export function detectFileLanguage(filename: string): FileDetection {
  const payload = getLanguagesCache();
  if (!payload) return { status: "unknown" };
  const lower = filename.toLowerCase();
  if (payload.ignored_suffixes.some((s) => lower.endsWith(s))) return { status: "ignored" };
  const spec = languageForExtension(filename, payload);
  if (!spec) return { status: "unknown" };
  return { status: "ok", lang: languageSpecToConfig(spec) };
}

/** Lädt Sprachkatalog von der API (einmalig gecacht). */
export async function ensureLanguagesLoaded(): Promise<void> {
  await fetchLanguages();
}
