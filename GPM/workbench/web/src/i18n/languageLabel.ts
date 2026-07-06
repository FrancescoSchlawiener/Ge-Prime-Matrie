import { t } from "./t";

export function languageLabel(code: string | null | undefined): string {
  const normalized = code?.trim().toLowerCase() || "random";
  const key = `languages.${normalized}`;
  const label = t(key);
  return label !== key ? label : normalized;
}
