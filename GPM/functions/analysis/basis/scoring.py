"""Tier-1 Basis-Score — delegiert Gewichte an fusion.py (F-B) + E-C typed default 0."""

from __future__ import annotations

from analysis.algebra.fusion import (
    fuse_basis_full,
    fuse_typed_overlay,
    log_jaccard_basis_blend,
)


def basis_score_from_components(
    log_sim: float,
    jaccard: float,
    relation_sketch: float,
    *,
    has_relation_sketch: bool,
    typed_sketch: float = 0.0,
    fusion_mode: str = "default",
    typed_weight: float = 0.0,
) -> float:
    if has_relation_sketch:
        base = fuse_basis_full(log_sim, jaccard, relation_sketch)
    else:
        base = log_jaccard_basis_blend(log_sim, jaccard)
    if fusion_mode == "typed" and typed_weight > 0:
        return fuse_typed_overlay(base, typed_sketch, typed_weight)
    return base


def has_relation_sketch_pair(sig_a_has: bool, sig_b_has: bool) -> bool:
    return sig_a_has and sig_b_has
