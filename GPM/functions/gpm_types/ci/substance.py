"""C(I) Substanz — Primzahl-Geometrie für Struktur-/Symbol-Token (Code).

Anders als S(I) (Buchstaben-Alphabet) oder N(I) (Ziffern) deckt C(I) den
gesamten Zeichenraum ab, der in Quellcode als Keyword, Operator, Klammer oder
Trenner auftritt. Jedes Zeichen bekommt eine feste Primzahl; die **Substanz**
ist das Primprodukt (kommutativ — welche Zeichen), der **perm_index** der
Multiset-Permutations-Rang (Reihenfolge). Zusammen sind sie eine
kollisionsfreie geometrische Identität: ``=>`` und ``>=`` teilen die Substanz,
haben aber unterschiedliche perm_index; ``[]`` und ``][`` ebenso.
"""

from __future__ import annotations

import string
from collections import Counter

from perm.multiset import perm_decode, perm_index as _perm_index
from perm.multiset import perm_space as _perm_space


def _sieve_primes(count: int) -> list[int]:
    """Erste ``count`` Primzahlen (deterministisch, reproduzierbar)."""
    primes: list[int] = []
    candidate = 2
    while len(primes) < count:
        is_prime = True
        for p in primes:
            if p * p > candidate:
                break
            if candidate % p == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(candidate)
        candidate += 1
    return primes


# Druckbarer ASCII-Bereich (Space..~) = 95 Zeichen, deterministisch nach
# Codepoint sortiert → feste Primzahl-Zuordnung. Getrennter Primblock (startet
# bewusst hinter kleinen Primen, damit Klartext-Kollisionen mit N/S unwahr-
# scheinlich bleiben; Identität ist ohnehin kategoriegetrennt).
_PRINTABLE: tuple[str, ...] = tuple(sorted(set(string.printable) - set("\t\n\r\x0b\x0c")))
_PRIMES: tuple[int, ...] = tuple(_sieve_primes(len(_PRINTABLE)))
CODE_CHAR_PRIMES: dict[str, int] = {ch: _PRIMES[i] for i, ch in enumerate(_PRINTABLE)}
_PRIME_TO_CHAR: dict[int, str] = {p: ch for ch, p in CODE_CHAR_PRIMES.items()}
_CODE_LEX_ORDER: tuple[str, ...] = _PRINTABLE

# Höchste ASCII-Prim als Basis für den deterministischen Unicode-Fallback.
_MAX_ASCII_PRIME: int = _PRIMES[-1]


def _next_prime(n: int) -> int:
    candidate = max(n, 2)
    while True:
        is_prime = candidate > 1
        d = 2
        while d * d <= candidate:
            if candidate % d == 0:
                is_prime = False
                break
            d += 1
        if is_prime:
            return candidate
        candidate += 1


def prime_for_char(ch: str) -> int:
    """Feste Primzahl für ein Zeichen (ASCII fest, sonst deterministisch)."""
    prime = CODE_CHAR_PRIMES.get(ch)
    if prime is not None:
        return prime
    # Deterministischer Fallback für seltene Unicode-Zeichen: nächste Primzahl
    # oberhalb des ASCII-Blocks, aus dem Codepoint abgeleitet. Kollisionsarm,
    # weil der Offset mit dem Codepoint monoton wächst.
    return _next_prime(_MAX_ASCII_PRIME + ord(ch))


def substance_c(text: str) -> int:
    """Primprodukt über die Zeichen eines Struktur-/Symbol-Tokens."""
    if not text:
        raise ValueError("Leerer C(I)-Wert.")
    s = 1
    for ch in text:
        s *= prime_for_char(ch)
    return s


def _counts(text: str) -> Counter[str]:
    return Counter(text)


def perm_index_c(text: str) -> int:
    """Multiset-Permutations-Rang der Zeichen (Reihenfolge → eindeutig)."""
    if not text:
        raise ValueError("Leerer C(I)-Wert.")
    counts = _counts(text)
    return _perm_index(list(text), counts)


def perm_space_c(text: str) -> int:
    """Größe des Permutationsraums der Zeichen-Multimenge."""
    if not text:
        return 1
    return _perm_space(_counts(text))


def _resolve_prime_to_char(prime: int) -> str:
    ch = _PRIME_TO_CHAR.get(prime)
    if ch is not None:
        return ch
    for candidate in range(128, 0x110000):
        if prime_for_char(chr(candidate)) == prime:
            return chr(candidate)
    raise ValueError(f"C-Primzahl {prime} konnte keinem Zeichen zugeordnet werden.")


def ingredients_c(substance: int) -> Counter[str]:
    """Faktorisiert C(I)-Substanz in Zeichen-Multimenge."""
    if substance < 1:
        raise ValueError("Substanz muss >= 1 sein.")
    counts: Counter[str] = Counter()
    remaining = substance
    for prime in sorted(_PRIME_TO_CHAR.keys(), reverse=True):
        while remaining % prime == 0:
            counts[_PRIME_TO_CHAR[prime]] += 1
            remaining //= prime
    while remaining > 1:
        prime = remaining
        for divisor in range(2, int(prime**0.5) + 1):
            if remaining % divisor == 0:
                prime = divisor
                break
        counts[_resolve_prime_to_char(prime)] += 1
        remaining //= prime
    return counts


def decode_ci(substance: int, perm_index: int) -> str:
    """Rekonstruiert Struktur-Token aus C(I)-Primgeometrie."""
    counts = ingredients_c(substance)
    space = _perm_space(counts)
    if space <= 1:
        if perm_index != 1:
            raise ValueError(f"C(I)-Index {perm_index} passt nicht zu N=1.")
        return "".join(counts.elements())
    return "".join(perm_decode(counts, perm_index, lex_order=_CODE_LEX_ORDER))
