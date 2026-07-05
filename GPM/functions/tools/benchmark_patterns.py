"""Deterministische Teststrings für Profil-Benchmarks."""

from __future__ import annotations

from collections import Counter

from alphabets.profiles import AlphabetProfile
from alphabets.registry import lex_order_for_profile

PATTERN_IDS: tuple[str, ...] = (
    "unique",
    "all_same",
    "pairs",
    "triple",
    "max_multiplicity",
)

SWEEP_LENGTHS: tuple[int, ...] = (
    1, 2, 3, 4, 6, 8, 10, 12, 14, 16, 20, 24, 32, 48, 64,
)

DUPLICATE_MATRIX_LENGTHS: tuple[int, ...] = (4, 8, 12, 16)


def alphabet_for_profile(profile: AlphabetProfile | str) -> tuple[str, ...]:
    return lex_order_for_profile(profile)


def multiplicity_counts(text: str) -> Counter[str]:
    return Counter(text)


def can_build_pattern(
    profile: AlphabetProfile | str,
    length: int,
    pattern_id: str,
) -> bool:
    if length < 1 or pattern_id not in PATTERN_IDS:
        return False
    lex = alphabet_for_profile(profile)
    n = len(lex)
    if n == 0:
        return False
    if pattern_id == "unique":
        return length <= n
    if pattern_id == "all_same":
        return True
    if pattern_id == "pairs":
        num_pairs = length // 2
        remainder = length % 2
        return num_pairs + remainder <= n
    if pattern_id == "triple":
        num_triples = length // 3
        remainder = length % 3
        extra = 1 if remainder else 0
        return num_triples + extra <= n
    if pattern_id == "max_multiplicity":
        if length == 1:
            return True
        others = min(length - 1, n - 1)
        return others >= 0
    return False


def build_all_same(lex: tuple[str, ...], length: int) -> str:
    return lex[0] * length


def build_unique(lex: tuple[str, ...], length: int) -> str:
    if length > len(lex):
        raise ValueError(f"unique erfordert L<={len(lex)}, got L={length}")
    return "".join(lex[:length])


def build_pairs(lex: tuple[str, ...], length: int) -> str:
    num_pairs = length // 2
    remainder = length % 2
    needed = num_pairs + remainder
    if needed > len(lex):
        raise ValueError(f"pairs: zu wenig Alphabet ({len(lex)}) für L={length}")
    chars = lex[:needed]
    parts: list[str] = []
    for i in range(num_pairs):
        parts.extend([chars[i], chars[i]])
    if remainder:
        parts.append(chars[num_pairs])
    return "".join(parts)


def build_triple(lex: tuple[str, ...], length: int) -> str:
    num_triples = length // 3
    remainder = length % 3
    extra = 1 if remainder else 0
    needed = num_triples + extra
    if needed > len(lex):
        raise ValueError(f"triple: zu wenig Alphabet ({len(lex)}) für L={length}")
    chars = lex[:needed]
    parts: list[str] = []
    for i in range(num_triples):
        parts.extend([chars[i]] * 3)
    if remainder == 1:
        parts.append(chars[num_triples])
    elif remainder == 2:
        parts.extend([chars[num_triples]] * 2)
    return "".join(parts)


def build_max_multiplicity(lex: tuple[str, ...], length: int) -> str:
    if length == 1:
        return lex[0]
    others = min(length - 1, len(lex) - 1)
    mult_first = length - others
    parts: list[str] = [lex[0]] * mult_first
    parts.extend(lex[1 : 1 + others])
    result = "".join(parts)
    if len(result) != length:
        raise ValueError(f"max_multiplicity intern: L={length}, got {len(result)}")
    return result


def build_pattern(
    profile: AlphabetProfile | str,
    length: int,
    pattern_id: str,
) -> str:
    if not can_build_pattern(profile, length, pattern_id):
        raise ValueError(
            f"Muster {pattern_id!r} für Profil {profile!r} L={length} nicht baubar."
        )
    lex = alphabet_for_profile(profile)
    if pattern_id == "unique":
        return build_unique(lex, length)
    if pattern_id == "all_same":
        return build_all_same(lex, length)
    if pattern_id == "pairs":
        return build_pairs(lex, length)
    if pattern_id == "triple":
        return build_triple(lex, length)
    if pattern_id == "max_multiplicity":
        return build_max_multiplicity(lex, length)
    raise ValueError(f"Unbekanntes Muster: {pattern_id!r}")


def build_all_same_k(lex: tuple[str, ...], length: int, k: int) -> str | None:
    """Ein Zeichen k-mal wiederholt; Rest unique aus lex[1:]. None wenn nicht baubar."""
    if k < 1 or k > length or length < 1:
        return None
    rest = length - k
    if rest > len(lex) - 1:
        return None
    return (lex[0] * k) + "".join(lex[1 : 1 + rest])
