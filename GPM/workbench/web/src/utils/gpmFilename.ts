const UNSAFE_CHARS = /[/\\:*?"<>|\x00-\x1f]/g;
const SUFFIX_PATTERN = /\.(gpm|gpc)$/i;

export function sanitizeExportBaseName(raw: string): string {
  let name = raw.replace(UNSAFE_CHARS, "").trim();
  name = name.replace(SUFFIX_PATTERN, "").trim();
  return name || "document";
}

export function normalizeGpmFilename(baseName: string, suffix: ".gpm" | ".gpc" = ".gpm"): string {
  const clean = sanitizeExportBaseName(baseName);
  return `${clean}${suffix}`;
}
