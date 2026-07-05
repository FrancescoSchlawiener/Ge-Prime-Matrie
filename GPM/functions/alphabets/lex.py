"""LEX-Reihenfolge — selten oben, häufig unten."""

from __future__ import annotations

from typing import Iterable, Sequence


def build_lex_order(
    symbols: Iterable[str],
    frequency_desc: Sequence[str],
) -> tuple[str, ...]:
    """frequency_desc: häufig→selten; Rückgabe: selten→häufig (häufig unten)."""
    symbol_set = set(symbols)
    ordered: list[str] = []
    seen: set[str] = set()
    for sym in reversed(frequency_desc):
        if sym in symbol_set and sym not in seen:
            ordered.append(sym)
            seen.add(sym)
    for sym in sorted(symbol_set - seen):
        ordered.insert(0, sym)
    return tuple(ordered)


def lex_order_for_profile(profile) -> tuple[str, ...]:
    from alphabets.registry import lex_order_for_profile as _registry_lex

    return _registry_lex(profile)
