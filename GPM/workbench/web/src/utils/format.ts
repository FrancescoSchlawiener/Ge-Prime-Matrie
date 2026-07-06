export function formatBigInt(n: number): string {
  if (!Number.isFinite(n)) return "—";
  return n.toLocaleString("de-DE");
}

export function formatLetters(letters: Record<string, number> | undefined): string {
  if (!letters || !Object.keys(letters).length) return "—";
  return Object.entries(letters)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([ch, count]) => (count > 1 ? `${ch}×${count}` : ch))
    .join(" ");
}

export function pct(ratio: number): string {
  return `${(ratio * 100).toFixed(2).replace(".", ",")} %`;
}
