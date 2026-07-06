"""Tier-Score-Fusion — thin wrapper über algebra/fusion."""

from __future__ import annotations

from analysis.algebra.fusion import fuse_weighted_scores, fuse_with_zero_reason


def fuse_tier_scores(
    *,
    basis: float,
    structure: float | None = None,
    curve: float | None = None,
    weights: dict[str, float] | None = None,
    zero_reason: str | None = None,
    fusion_mode: str = "additive",
) -> float:
    if zero_reason:
        return fuse_with_zero_reason(basis, zero_reason=zero_reason)
    w = weights or {"basis": 0.4, "structure": 0.35, "curve": 0.25}
    if fusion_mode == "replace_last" and curve is not None:
        return round(curve, 6)
    scores: dict[str, float] = {"basis": basis}
    if structure is not None:
        scores["structure"] = structure
    if curve is not None:
        scores["curve"] = curve
    return fuse_weighted_scores(scores, w, clamp=True)
