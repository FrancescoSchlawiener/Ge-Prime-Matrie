/**
 * Sprachen-Metadaten aus GPM/functions (GET /api/code/languages).
 * Kein paralleles TS-Sprachregister mehr.
 */

import { request } from "../../api/request";

export interface LanguageSpec {
  id: string;
  name: string;
  extensions: string[];
  block_style: string;
  comment_style: string;
  block_pairs: string[][];
  case_insensitive: boolean;
}

export interface LanguagesPayload {
  languages: LanguageSpec[];
  ignored_suffixes: string[];
}

export interface LanguageManifest {
  primary: string;
  embedded: string[];
  all: string[];
}

let cache: LanguagesPayload | null = null;

export function getLanguagesCache(): LanguagesPayload | null {
  return cache;
}

export function setLanguagesCache(payload: LanguagesPayload): void {
  cache = payload;
}

export async function fetchLanguages(): Promise<LanguagesPayload> {
  if (cache) return cache;
  const resp = await request<{ result: LanguagesPayload }>("/api/code/languages");
  cache = resp.result;
  return cache;
}

export function languageForExtension(path: string, payload: LanguagesPayload): LanguageSpec | null {
  const lower = path.toLowerCase();
  if (payload.ignored_suffixes.some((s) => lower.endsWith(s))) return null;
  const dot = path.lastIndexOf(".");
  if (dot < 0) return null;
  const ext = path.slice(dot).toLowerCase();
  return payload.languages.find((l) => l.extensions.map((e) => e.toLowerCase()).includes(ext)) ?? null;
}

const EMBEDDED_OPEN_RE = /<(script|style)\b/gi;
const HTML_EMBEDDED: Record<string, string> = { script: "js", style: "css" };

export function scanEmbeddedLanguages(source: string, primary: string): string[] {
  if (primary !== "html" && primary !== "xml") return [];
  const found = new Set<string>();
  for (const m of source.matchAll(EMBEDDED_OPEN_RE)) {
    const lang = HTML_EMBEDDED[(m[1] ?? "").toLowerCase()];
    if (lang) found.add(lang);
  }
  return [...found].sort();
}

export function buildLanguageManifest(
  source: string,
  filename: string,
  payload: LanguagesPayload,
): LanguageManifest | null {
  const spec = languageForExtension(filename, payload);
  if (!spec) return null;
  const embedded = scanEmbeddedLanguages(source, spec.id);
  const all = [...new Set([spec.id, ...embedded])].sort();
  return { primary: spec.id, embedded, all };
}

export function languageSpecToConfig(spec: LanguageSpec): import("../tensorraum/types").LanguageConfig {
  return {
    id: spec.id,
    name: spec.name,
    ext: spec.extensions,
    blockStyle: spec.block_style as import("../tensorraum/types").BlockStyle,
    commentStyle: spec.comment_style as import("../tensorraum/types").CommentStyle,
    blockPairs: spec.block_pairs.map(([open, close]) => ({ open, close })),
  };
}

export function allLanguageIds(payload: LanguagesPayload): string[] {
  return payload.languages.map((l) => l.id);
}

export async function fetchLanguageManifest(source: string, filename: string): Promise<LanguageManifest> {
  const resp = await request<{ result: LanguageManifest }>("/api/code/manifest", {
    method: "POST",
    body: JSON.stringify({ source, filename, profile: "og" }),
  });
  return resp.result;
}
