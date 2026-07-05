"""N(I) Registry — Toy-Stil N_<checksum>."""

from __future__ import annotations

from gpm_types.ni.canonical import canonical_n
from gpm_types.ni.substance import DIGIT_PRIMES, substance_n

BIG_PRIME = 982451653


def checksum_n(value: str) -> int:
    canon = canonical_n(value)
    h = 1
    for ch in canon:
        h = (h * DIGIT_PRIMES[ch]) % BIG_PRIME
    return h


def pointer_id_n(value: str) -> str:
    return f"N_{checksum_n(value)}"


class NRegistry:
    def __init__(self) -> None:
        self._forward: dict[str, str] = {}
        self._reverse: dict[str, str] = {}

    def register(self, raw: str) -> str:
        canon = canonical_n(raw)
        if canon in self._reverse:
            return self._reverse[canon]
        pid = pointer_id_n(canon)
        self._forward[pid] = canon
        self._reverse[canon] = pid
        return pid

    def resolve(self, pointer_id: str) -> str:
        if pointer_id not in self._forward:
            raise KeyError(f"Unbekannter N-Pointer: {pointer_id!r}")
        return self._forward[pointer_id]
