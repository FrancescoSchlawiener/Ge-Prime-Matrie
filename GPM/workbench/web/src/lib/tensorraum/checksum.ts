import { BIG_PRIME, PRIME_ALPHABET } from "./constants";

export function calculateChecksum(value: string): bigint {
  let hash = 1n;
  const strVal = String(value).toUpperCase();
  for (let i = 0; i < strVal.length; i++) {
    const char = strVal[i];
    const primeValue =
      PRIME_ALPHABET[char] !== undefined ? PRIME_ALPHABET[char] : BigInt(strVal.charCodeAt(i)) + 17n;
    hash = (hash * primeValue) % BIG_PRIME;
  }
  return hash;
}
