"""Primzahl-Blöcke für disjunkte Alphabet-Profile."""

from __future__ import annotations

from typing import Final

_LAST_KNOWN: Final[int] = 439  # Cyrillic block ends here


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def next_prime_after(n: int) -> int:
    candidate = n + 1
    while not _is_prime(candidate):
        candidate += 1
    return candidate


def next_prime_block(count: int, after: int = _LAST_KNOWN) -> tuple[int, ...]:
    if count < 1:
        return ()
    primes: list[int] = []
    current = after
    for _ in range(count):
        current = next_prime_after(current)
        primes.append(current)
    return tuple(primes)


def last_prime_in_block(block: tuple[int, ...]) -> int:
    if not block:
        return _LAST_KNOWN
    return block[-1]
