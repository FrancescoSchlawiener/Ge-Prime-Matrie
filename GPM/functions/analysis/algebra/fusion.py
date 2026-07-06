"""Gewichtete Score-Fusion — Härtungs-Invariante F-B: einzige Quelle der Gewichts-Literale."""

from __future__ import annotations

# --- Kanonische Gewichte (F-B) — keine Duplikate in window_fold / compare_tiered / meta/compare ---

WEIGHTS_BASIS_LOG_JACCARD = {"log": 0.67, "jaccard": 0.33}
WEIGHTS_BASIS_FULL = {"log": 0.6, "jaccard": 0.3, "relation_sketch": 0.1}
WEIGHTS_STRUCTURE_TIER = {"meta": 0.5, "relation": 0.3, "bitmask": 0.2}
WEIGHTS_CURVE_TIER = {"i_curve": 0.5, "substance": 0.5}
WEIGHTS_PROFILE_OVERLAY = {"base": 0.95, "overlap": 0.05}
WEIGHTS_ISOMORPHISM_ALIGNED = {
    "word_geo": 0.25,
    "cell": 0.20,
    "subst": 0.20,
    "rel": 0.15,
    "meta": 0.15,
    "literal": 0.05,
}
WEIGHTS_ISOMORPHISM_UNALIGNED = {
    "word_geo": 0.20,
    "cell": 0.20,
    "subst": 0.20,
    "rel": 0.20,
    "meta": 0.20,
}
WEIGHTS_CELL_I_SIM = {"i": 0.7, "skeleton": 0.3}


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def fuse_weighted_scores(
    scores: dict[str, float],
    weights: dict[str, float],
    *,
    clamp: bool = True,
) -> float:
    total_w = sum(weights.get(k, 0.0) for k in scores if weights.get(k, 0.0) > 0)
    if total_w <= 0:
        return 0.0
    blended = sum(
        (_clamp01(scores[k]) if clamp else scores[k]) * weights.get(k, 0.0)
        for k in scores
        if weights.get(k, 0.0) > 0
    )
    result = blended / total_w
    return round(_clamp01(result) if clamp else result, 6)


def fuse_with_zero_reason(score: float, *, zero_reason: str | None) -> float:
    if zero_reason:
        return round(score, 6)
    return round(score, 6)


def log_jaccard_basis_blend(log_sim: float, jaccard: float) -> float:
    return fuse_weighted_scores(
        {"log": log_sim, "jaccard": jaccard},
        WEIGHTS_BASIS_LOG_JACCARD,
    )


def fuse_basis_full(log_sim: float, jaccard: float, relation_sketch: float) -> float:
    return fuse_weighted_scores(
        {"log": log_sim, "jaccard": jaccard, "relation_sketch": relation_sketch},
        WEIGHTS_BASIS_FULL,
    )


def fuse_structure_tier(meta_sim: float, relation_score: float, bitmask_ok: bool) -> float:
    return fuse_weighted_scores(
        {
            "meta": meta_sim,
            "relation": relation_score,
            "bitmask": 1.0 if bitmask_ok else 0.0,
        },
        WEIGHTS_STRUCTURE_TIER,
    )


def fuse_curve_tier(i_curve_score: float, substance_score: float) -> float:
    return fuse_weighted_scores(
        {"i_curve": i_curve_score, "substance": substance_score},
        WEIGHTS_CURVE_TIER,
    )


def fuse_profile_overlay(base: float, overlap: float) -> float:
    return fuse_weighted_scores(
        {"base": base, "overlap": overlap},
        WEIGHTS_PROFILE_OVERLAY,
    )


def fuse_typed_overlay(base: float, typed_sketch: float, typed_weight: float) -> float:
    return fuse_weighted_scores(
        {"base": base, "typed": typed_sketch},
        {"base": 1.0 - typed_weight, "typed": typed_weight},
    )


def fuse_isomorphism_index(
    *,
    aligned: bool,
    word_geo: float,
    cell_score: float,
    subst_score: float,
    rel_score: float,
    meta_sim: float,
    literal: float,
) -> float:
    if aligned:
        return fuse_weighted_scores(
            {
                "word_geo": word_geo,
                "cell": cell_score,
                "subst": subst_score,
                "rel": rel_score,
                "meta": meta_sim,
                "literal": literal,
            },
            WEIGHTS_ISOMORPHISM_ALIGNED,
        )
    return fuse_weighted_scores(
        {
            "word_geo": word_geo,
            "cell": cell_score,
            "subst": subst_score,
            "rel": rel_score,
            "meta": meta_sim,
        },
        WEIGHTS_ISOMORPHISM_UNALIGNED,
    )


def fuse_cell_i_similarity(i_sim: float, skeleton_match: float) -> float:
    return fuse_weighted_scores(
        {"i": i_sim, "skeleton": skeleton_match},
        WEIGHTS_CELL_I_SIM,
    )
