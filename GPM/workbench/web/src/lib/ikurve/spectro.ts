export interface SpectroMatch {
  char_start?: number;
  char_end?: number;
  token_start?: number;
  token_end?: number;
  token_count?: number;
  layer?: string;
  mode?: string;
  className?: string;
}

export function tokenSpanToCharRange(
  tokenCharMap: Array<{ token_index?: number; char_start?: number; char_end?: number }>,
  tokenStart: number,
  tokenCount: number,
): { char_start: number; char_end: number } {
  const entries = tokenCharMap.filter((e) => {
    const idx = e.token_index ?? -1;
    return idx >= tokenStart && idx < tokenStart + tokenCount;
  });
  if (!entries.length) return { char_start: 0, char_end: 0 };
  const first = entries[0]!;
  const last = entries[entries.length - 1]!;
  return {
    char_start: first.char_start ?? 0,
    char_end: last.char_end ?? first.char_end ?? 0,
  };
}

export function expandSpectroMatches(
  matches: SpectroMatch[],
  tokenCharMap: Array<{ token_index?: number; char_start?: number; char_end?: number }>,
): SpectroMatch[] {
  return (matches ?? []).map((match) => {
    const tokenStart = match.token_start ?? 0;
    const tokenCount =
      match.token_count ?? Math.max(1, (match.token_end ?? tokenStart) - tokenStart);
    const range = tokenSpanToCharRange(tokenCharMap, tokenStart, tokenCount);
    return {
      ...match,
      token_start: tokenStart,
      token_end: tokenStart + tokenCount,
      char_start: match.char_start ?? range.char_start,
      char_end: match.char_end ?? range.char_end,
    };
  });
}

export function mergeSpectroMatches(matches: SpectroMatch[]): SpectroMatch[] {
  const sorted = [...(matches ?? [])].sort(
    (a, b) => (a.char_start ?? 0) - (b.char_start ?? 0) || (b.char_end ?? 0) - (a.char_end ?? 0),
  );
  const merged: SpectroMatch[] = [];

  for (const match of sorted) {
    const existing = merged.find(
      (m) => m.char_start === match.char_start && m.char_end === match.char_end,
    );
    if (existing) {
      if (existing.layer !== match.layer) {
        existing.className = "spectro-crossfire";
      }
    } else {
      const className =
        match.mode === "structural_twin" && match.layer === "structural"
          ? "spectro-amber-struct"
          : match.mode === "structural_twin"
            ? "spectro-amber"
            : "spectro-teal";
      merged.push({ ...match, className });
    }
  }
  return merged;
}

export function mergeClassRanges(
  textLength: number,
  mergedMatches: SpectroMatch[],
): string[] {
  const classes = new Array<string>(textLength).fill("");
  for (const match of mergedMatches) {
    const start = Math.max(0, match.char_start ?? 0);
    const end = Math.min(textLength, match.char_end ?? 0);
    const cls = match.className || "spectro-teal";
    for (let i = start; i < end; i += 1) {
      classes[i] = cls;
    }
  }
  return classes;
}
