/** Old slug → new slug (Erklärungen renumber 00–28). */
export const EXPLAIN_SLUG_REDIRECTS: Record<string, string> = {
  "04-normalisierung": "07-normalisierung",
  "05-profile": "08-profile",
  "06-ggt-kgv": "09-ggt-kgv",
  "07-wortpaar-diff": "10-wortpaar-diff",
  "08-gaps-dokument": "12-gaps-dokument",
  "08-wortpaar-anagramm": "11-wortpaar-anagramm",
  "09-gpm-binary": "13-gpm-binary",
  "10-case-explicit": "14-case-explicit",
  "11-registry": "15-registry",
  "12-tokens": "16-tokens",
  "13-payload-kinds": "17-payload-kinds",
  "14-blocks": "18-blocks",
  "15-cells": "19-cells",
  "16-i-curve": "20-i-curve",
  "17-corpus": "21-corpus",
  "18-redundanz": "22-redundanz",
  "19-hybrid-fences": "23-hybrid-fences",
  "20-code-blocks": "24-code-blocks",
  "21-cipher": "25-cipher",
  "22-spectroscope": "26-spectroscope",
  "23-inference-trace": "27-inference-trace",
  "24-cipher-gpc": "28-cipher-gpc",
  "25-ni-ganzzahl": "04-ni-ganzzahl",
  "26-di-dezimal": "05-di-dezimal",
  "27-hi-hybrid-identitaet": "06-hi-hybrid-identitaet",
};

export function resolveExplainSlug(slug: string): string {
  return EXPLAIN_SLUG_REDIRECTS[slug] ?? slug;
}
