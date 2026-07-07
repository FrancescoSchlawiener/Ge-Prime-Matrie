import { formatBigInt } from "./format";

export function formatSiPair(substance: number | string, permIndex: number | string): string {
  return `S = ${formatBigInt(Number(substance))} · I = ${formatBigInt(Number(permIndex))}`;
}
