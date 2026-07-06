"""Fold-Operationen für ggT/kgV über N Substanzen und Profile."""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Iterable

from analysis.algebra.substance_kernel import substance_covers


def fold_gcd(substances: Iterable[int]) -> int:
    result = 0
    for value in substances:
        if value < 1:
            continue
        result = value if result == 0 else math.gcd(result, value)
    return result


def fold_lcm(substances: Iterable[int]) -> int:
    result = 1
    for value in substances:
        if value < 1:
            continue
        result = math.lcm(result, value)
    return result


def fold_profile(profiles: Iterable[Counter[int]], *, mode: str = "gcd") -> Counter[int]:
    """Exponentweise min (gcd) oder max (lcm) über Profile."""
    merged: Counter[int] | None = None
    for profile in profiles:
        if not profile:
            continue
        if merged is None:
            merged = Counter(profile)
            continue
        keys = set(merged.keys()) | set(profile.keys())
        if mode == "lcm":
            merged = Counter({k: max(merged.get(k, 0), profile.get(k, 0)) for k in keys})
        else:
            merged = Counter({k: min(merged.get(k, 0), profile.get(k, 0)) for k in keys})
    return merged or Counter()


def substance_covers_batch(container: int, required_list: Iterable[int]) -> list[bool]:
    return [substance_covers(container, req) for req in required_list]


def fold_lcm_span(substances: Iterable[int]) -> int:
    """kgV-Fold über Substanz-Span — alias für fold_lcm mit Semantik-Name."""
    return fold_lcm(substances)


def passes_kgv_gate(container: int, target: int) -> bool:
    """Divisibilitäts-Gate — delegiert an substance_covers (F-1)."""
    if target <= 1:
        return True
    return substance_covers(container, target)
