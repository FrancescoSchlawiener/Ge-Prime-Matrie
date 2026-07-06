"""Substanz- und I×S-Kopplungs-Kernel — zentrale Algebra-Quelle (Härtungs-Invariante F-1)."""

from __future__ import annotations

import math

from analysis.substance.compare import (
    compare_substances,
    substance_covers,
    substance_ggt_kgv_distance,
    substance_ggt_kgv_similarity,
)
from analysis.substance.diff import substance_remainder


def coupled_point_similarity(i_sim: float, s_sim: float) -> float:
    """Härtungs-Invariante D-B: strikt multiplikativ i × s."""
    return i_sim * s_sim


def coupled_point_distance(i_sim: float, s_sim: float) -> float:
    return 1.0 - coupled_point_similarity(i_sim, s_sim)


def empty_transition_fields(*, include_s_ratio: bool = False) -> dict:
    base = {"ggt": 0, "kgv": 0, "ggt_kgv_ratio": 0.0}
    if include_s_ratio:
        base["s_ratio"] = 0.0
    return base


def substance_transition_fields(
    s_prev: int,
    s_curr: int,
    *,
    include_s_ratio: bool = False,
) -> dict:
    if s_prev <= 0 or s_curr <= 0:
        return empty_transition_fields(include_s_ratio=include_s_ratio)
    ggt = math.gcd(s_prev, s_curr)
    kgv = math.lcm(s_prev, s_curr)
    ratio = round(substance_ggt_kgv_similarity(s_prev, s_curr), 6)
    result = {"ggt": ggt, "kgv": kgv, "ggt_kgv_ratio": ratio}
    if include_s_ratio:
        result["s_ratio"] = ratio
    return result


def transition_fields(s_prev: int, s_curr: int) -> dict:
    """Schlanke API — ggt_kgv_similarity/distance (Legacy substance/transition)."""
    full = substance_transition_fields(s_prev, s_curr)
    sim = full["ggt_kgv_ratio"]
    return {
        "ggt_kgv_similarity": sim,
        "ggt_kgv_distance": round(1.0 - sim, 6),
    }


def substance_transition_similarity(s_prev: int, s_curr: int) -> float:
    return transition_fields(s_prev, s_curr)["ggt_kgv_similarity"]


__all__ = [
    "compare_substances",
    "coupled_point_distance",
    "coupled_point_similarity",
    "empty_transition_fields",
    "substance_covers",
    "substance_ggt_kgv_distance",
    "substance_ggt_kgv_similarity",
    "substance_remainder",
    "substance_transition_fields",
    "substance_transition_similarity",
    "transition_fields",
]
