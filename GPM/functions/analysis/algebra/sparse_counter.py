"""Sparse-Counter-Metriken — Härtungs-Invariante D-A (O(k) Schnittmenge)."""

from __future__ import annotations

import math
from collections import Counter

from alphabets import AlphabetProfile


def counter_cosine(a: Counter, b: Counter) -> float:
    """Cosine über Schnittmenge — kein Union-Keyspace für Dot-Product."""
    if not a or not b:
        return 0.0
    dot = sum(a[k] * b[k] for k in a if k in b)
    if dot <= 0:
        return 0.0
    norm_a = sum(v * v for v in a.values())
    norm_b = sum(v * v for v in b.values())
    if norm_a <= 0 or norm_b <= 0:
        return 0.0
    return min(1.0, dot / math.sqrt(norm_a * norm_b))


def counter_jaccard(a: Counter, b: Counter) -> float:
    """Exponent-gewichtetes Jaccard: sum(min) / sum(max) über keys(a)|keys(b)."""
    if not a and not b:
        return 0.0
    keys = set(a) | set(b)
    inter = sum(min(a.get(k, 0), b.get(k, 0)) for k in keys)
    union = sum(max(a.get(k, 0), b.get(k, 0)) for k in keys)
    return inter / union if union else 0.0


def counter_overlap(a: Counter, b: Counter) -> float:
    """Σ min / min(Σa, Σb) — profile_overlap Semantik."""
    if not a or not b:
        return 0.0
    keys = set(a) | set(b)
    inter = sum(min(a.get(k, 0), b.get(k, 0)) for k in keys)
    denom = min(sum(a.values()), sum(b.values()))
    return inter / denom if denom else 0.0


def weighted_channel_score(
    scores: dict[str, float],
    weights: dict[str, float],
) -> float:
    from analysis.algebra.fusion import fuse_weighted_scores

    return fuse_weighted_scores(scores, weights, clamp=True)


def counter_cosine_guarded(
    a: Counter,
    b: Counter,
    *,
    profile_a: AlphabetProfile,
    profile_b: AlphabetProfile,
) -> tuple[float, str | None]:
    from analysis.algebra.gates import profile_symmetry_guard

    ok, reason = profile_symmetry_guard(profile_a, profile_b)
    if not ok:
        return 0.0, reason
    return counter_cosine(a, b), None


def counter_jaccard_guarded(
    a: Counter,
    b: Counter,
    *,
    profile_a: AlphabetProfile,
    profile_b: AlphabetProfile,
) -> tuple[float, str | None]:
    from analysis.algebra.gates import profile_symmetry_guard

    ok, reason = profile_symmetry_guard(profile_a, profile_b)
    if not ok:
        return 0.0, reason
    return counter_jaccard(a, b), None
