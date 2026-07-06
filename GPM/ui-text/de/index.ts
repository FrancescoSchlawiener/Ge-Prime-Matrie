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

export function createTranslationEngine<T extends NestedObject>(translations: T) {
  return function t(key: string, fallback?: string): string {
    const value = walk(translations, key.split("."));
    if (value !== undefined) return value;
    return fallback ?? key;
  };
}

export { shell, encode, decode, wortpaar, ikurve, gpm, datenbank, explain, feedback, result, languages };
