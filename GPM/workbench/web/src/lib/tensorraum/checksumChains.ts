import { BIG_PRIME, PRIME_ALPHABET } from "./constants";
import type { SequenceItem } from "./types";

function multiplyChar(checksum: bigint, char: string): bigint {
  const upper = char.toUpperCase();
  const primeValue =
    PRIME_ALPHABET[upper] !== undefined ? PRIME_ALPHABET[upper] : BigInt(char.charCodeAt(0)) + 17n;
  return (checksum * primeValue) % BIG_PRIME;
}

export function checksumOfPointerList(items: SequenceItem[]): bigint {
  let checksum = 1n;
  for (const item of items) {
    const val = "p" in item && item.p ? item.p : item.t;
    if (typeof val === "string") {
      for (let j = 0; j < val.length; j++) {
        checksum = multiplyChar(checksum, val[j]);
      }
    }
  }
  return checksum;
}

export function checksumOfTypeList(items: SequenceItem[]): bigint {
  let checksum = 1n;
  for (const item of items) {
    const val = item.t;
    for (let j = 0; j < val.length; j++) {
      checksum = multiplyChar(checksum, val[j]);
    }
  }
  return checksum;
}
