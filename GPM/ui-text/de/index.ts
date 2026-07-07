import { shell } from "./shell";
import { encode } from "./encode";
import { decode } from "./decode";
import { wortpaar } from "./wortpaar";
import { ikurve } from "./ikurve";
import { gpm } from "./gpm";
import { datenbank } from "./datenbank";
import { explain } from "./explain";
import { feedback } from "./feedback";
import { result } from "./result";
import { languages } from "./languages";
import { tensorraum } from "./tensorraum";

export const uiTextDe = {
  shell,
  encode,
  decode,
  wortpaar,
  ikurve,
  gpm,
  datenbank,
  explain,
  feedback,
  result,
  languages,
  tensorraum,
} as const;

export type UiTextKeys = typeof uiTextDe;

type NestedLeaf = string;
type NestedObject = { readonly [key: string]: NestedLeaf | NestedObject };

function walk(obj: NestedObject, parts: string[]): string | undefined {
  let cur: NestedLeaf | NestedObject | undefined = obj;
  for (const part of parts) {
    if (typeof cur !== "object" || cur === null || !(part in cur)) return undefined;
    cur = cur[part];
  }
  return typeof cur === "string" ? cur : undefined;
}

function applyVars(template: string, vars?: Record<string, string | number>): string {
  if (!vars) return template;
  let out = template;
  for (const [k, v] of Object.entries(vars)) {
    out = out.replaceAll(`{${k}}`, String(v));
  }
  return out;
}

export function createTranslationEngine<T extends NestedObject>(translations: T) {
  return function t(
    key: string,
    varsOrFallback?: Record<string, string | number> | string,
    fallback?: string,
  ): string {
    let vars: Record<string, string | number> | undefined;
    let fb = fallback;
    if (typeof varsOrFallback === "string") {
      fb = varsOrFallback;
    } else if (varsOrFallback) {
      vars = varsOrFallback;
    }
    const raw = walk(translations, key.split("."));
    if (raw === undefined) return fb ?? key;
    return applyVars(raw, vars);
  };
}

export { shell, encode, decode, wortpaar, ikurve, gpm, datenbank, explain, feedback, result, languages, tensorraum };
