"""I-Ratio-Metriken — Härtungs-Invariante E-B."""

from __future__ import annotations


def i_ratio_similarity(a: float, b: float) -> float:
    """Normiert auf [0, 1] — max-Guard schließt negative Ähnlichkeit aus."""
    return max(0.0, 1.0 - abs(a - b))


def i_ratio_distance(a: float, b: float) -> float:
    return 1.0 - i_ratio_similarity(a, b)
