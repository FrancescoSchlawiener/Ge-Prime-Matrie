"""Gestaffelter Dokument-Vergleich — Tiers 0–4 mit zero_reason-Zertifikaten."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum

from analysis.algebra.gates import (
    passes_document_relevance,
    profile_pair_gate,
    profile_symmetry_guard,
)
from analysis.algebra.log_profile import compare_profiles_sparse, log_gcd_similarity, log_jaccard_primes
from analysis.algebra.sparse_counter import counter_overlap as profile_overlap
from analysis.algebra.typed_bridge import typed_sketch_jaccard
from analysis.basis.scoring import basis_score_from_components, has_relation_sketch_pair
from analysis.basis.signature import BasisSignature, get_basis_signature
from analysis.document.model import GpmDocument
from analysis.meta.genome import build_meta_genome
from analysis.meta.compare import compare_meta_genomes
from analysis.algebra.tier_fusion import fuse_tier_scores
from analysis.algebra.fusion import fuse_curve_tier, fuse_profile_overlay, fuse_structure_tier


class CompareTier(IntEnum):
    GATE = 0
    BASIS = 1
    STRUCTURE = 2
    CURVES = 3
    FULL = 4


@dataclass
class TieredCompareResult:
    tiers_run: list[str] = field(default_factory=list)
    basis_score: float = 0.0
    structure_score: float = 0.0
    curve_score: float = 0.0
    final_score: float = 0.0
    stopped_at: CompareTier | None = None
    zero_reason: str | None = None
    shared_prime_count: int = 0
    detail: dict = field(default_factory=dict)


def _relation_sketch_similarity(a: BasisSignature, b: BasisSignature) -> float:
    if not a.relation_sketch or not b.relation_sketch:
        return 0.0
    set_a = set(a.relation_sketch)
    set_b = set(b.relation_sketch)
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def _run_signature_gates(
    sig_a: BasisSignature,
    sig_b: BasisSignature,
    *,
    use_document_relevance: bool,
) -> tuple[TieredCompareResult | None, int, list[str]]:
    """Gemeinsames Gate-Prelude — Tier 0."""
    tiers_run: list[str] = []
    ok, reason = profile_symmetry_guard(sig_a.profile, sig_b.profile)
    tiers_run.append("profile_symmetry_guard")
    if not ok:
        result = TieredCompareResult()
        result.tiers_run = tiers_run
        result.stopped_at = CompareTier.GATE
        result.zero_reason = reason
        return result, 0, tiers_run

    if use_document_relevance:
        gate = passes_document_relevance(sig_a, sig_b)
        tiers_run.append("document_relevance")
        if not gate.passed:
            result = TieredCompareResult()
            result.tiers_run = tiers_run
            result.stopped_at = CompareTier.GATE
            result.zero_reason = gate.zero_reason
            result.shared_prime_count = gate.shared_prime_count
            return result, gate.shared_prime_count, tiers_run
        return None, gate.shared_prime_count, tiers_run

    passed, gate_reason = profile_pair_gate(
        sig_a.prime_profile,
        sig_b.prime_profile,
        doc_profile_a=sig_a.profile,
        doc_profile_b=sig_b.profile,
    )
    shared = len(sig_a.prime_set & sig_b.prime_set)
    if not passed:
        result = TieredCompareResult()
        result.tiers_run = tiers_run
        result.stopped_at = CompareTier.GATE
        result.zero_reason = gate_reason
        result.shared_prime_count = shared
        return result, shared, tiers_run
    return None, shared, tiers_run


def _compute_basis_score(
    sig_a: BasisSignature,
    sig_b: BasisSignature,
    *,
    fusion_mode: str = "default",
    typed_weight: float = 0.0,
    include_profile_overlap: bool = False,
) -> tuple[float, dict]:
    log_sim = log_gcd_similarity(sig_a.prime_profile, sig_b.prime_profile)
    jaccard = log_jaccard_primes(sig_a.prime_profile, sig_b.prime_profile)
    rel_sketch = _relation_sketch_similarity(sig_a, sig_b)
    has_sketch = has_relation_sketch_pair(sig_a.has_relation_sketch, sig_b.has_relation_sketch)
    typed_sim = typed_sketch_jaccard(sig_a.typed_sketch, sig_b.typed_sketch)
    score = basis_score_from_components(
        log_sim,
        jaccard,
        rel_sketch,
        has_relation_sketch=has_sketch,
        typed_sketch=typed_sim,
        fusion_mode=fusion_mode,
        typed_weight=typed_weight,
    )
    overlap_sim = profile_overlap(sig_a.prime_profile, sig_b.prime_profile)
    if include_profile_overlap:
        score = fuse_profile_overlay(score, overlap_sim)
    return score, {
        "log_similarity": log_sim,
        "jaccard": jaccard,
        "relation_sketch": rel_sketch,
        "has_relation_sketch": has_sketch,
        "typed_sketch_similarity": typed_sim,
        "profile_overlap": overlap_sim,
    }


def compare_documents_tiered(
    doc_a: GpmDocument,
    doc_b: GpmDocument,
    *,
    max_tier: CompareTier = CompareTier.BASIS,
    weights=None,
    min_basis_score: float = 0.05,
    sig_a: BasisSignature | None = None,
    sig_b: BasisSignature | None = None,
    fusion_mode: str = "default",
    typed_weight: float = 0.0,
    include_profile_overlap: bool = False,
) -> TieredCompareResult:
    result = TieredCompareResult()
    sig_a = sig_a or get_basis_signature(doc_a)
    sig_b = sig_b or get_basis_signature(doc_b)

    gate_result, shared, gate_tiers = _run_signature_gates(sig_a, sig_b, use_document_relevance=True)
    if gate_result is not None:
        return gate_result
    result.tiers_run.extend(gate_tiers)
    result.shared_prime_count = shared

    result.basis_score, basis_detail = _compute_basis_score(
        sig_a,
        sig_b,
        fusion_mode=fusion_mode,
        typed_weight=typed_weight,
        include_profile_overlap=include_profile_overlap,
    )
    result.tiers_run.append("basis_signature")
    result.detail.update(basis_detail)

    if max_tier <= CompareTier.GATE:
        result.stopped_at = CompareTier.GATE
        result.final_score = result.basis_score
        return result

    if result.basis_score < min_basis_score:
        result.stopped_at = CompareTier.BASIS
        result.zero_reason = "basis_score_below_threshold"
        result.final_score = result.basis_score
        return result

    if max_tier <= CompareTier.BASIS:
        result.stopped_at = CompareTier.BASIS
        result.final_score = result.basis_score
        return result

    from analysis.validation.structure import _interval_bitmask_status

    from analysis.profile.relation import build_relation_profile, compare_relation_profiles

    prefilter = _interval_bitmask_status(doc_a, doc_b)
    meta_a = build_meta_genome(doc_a)
    meta_b = build_meta_genome(doc_b)
    rel_a = build_relation_profile(doc_a)
    rel_b = build_relation_profile(doc_b)
    rel_cmp = compare_relation_profiles(rel_a, rel_b)
    meta_cmp = compare_meta_genomes(meta_a, meta_b, relation_comparison=rel_cmp)
    bitmask_ok = prefilter.get("shared_prime_count", 0) > 0
    result.structure_score = fuse_structure_tier(
        meta_cmp.get("similarity_ratio", 0.0),
        rel_cmp.get("relation_score", 0.0),
        bitmask_ok,
    )
    result.tiers_run.extend(["structure_prefilter", "meta_genome", "relation_profile"])
    result.detail["prefilter"] = prefilter
    result.detail["meta_comparison"] = meta_cmp
    result.detail["profile_sparse"] = compare_profiles_sparse(
        sig_a.prime_profile,
        sig_b.prime_profile,
    )

    if max_tier <= CompareTier.STRUCTURE:
        result.stopped_at = CompareTier.STRUCTURE
        result.final_score = result.structure_score
        return result

    from analysis.align.substance_align import compare_substance_sequences, extract_substance_curve
    from analysis.curves.i_curve import compare_i_curves, extract_i_curve

    substance_a = extract_substance_curve(doc_a)
    substance_b = extract_substance_curve(doc_b)
    curve_a = extract_i_curve(doc_a)
    curve_b = extract_i_curve(doc_b)
    curve_cmp = compare_i_curves(curve_a, curve_b, document_a=doc_a, document_b=doc_b)
    subst_cmp = compare_substance_sequences(
        substance_a,
        substance_b,
        profile=doc_a.profile,
    )
    result.curve_score = fuse_curve_tier(
        curve_cmp.get("geometry_score", 0.0),
        subst_cmp.get("geometry_score", 0.0),
    )
    result.tiers_run.append("curves")
    result.detail["curve_comparison"] = curve_cmp
    result.detail["substance_comparison"] = subst_cmp
    result.detail["fused_score"] = fuse_tier_scores(
        basis=result.basis_score,
        structure=result.structure_score,
        curve=result.curve_score,
        zero_reason=result.zero_reason,
    )

    if max_tier <= CompareTier.CURVES:
        result.stopped_at = CompareTier.CURVES
        result.final_score = result.curve_score
        return result

    from analysis.curves.compare import AxisWeights, analyze_pair_full

    full = analyze_pair_full(doc_a, doc_b, weights=weights or AxisWeights.full())
    result.tiers_run.append("analyze_pair_full")
    result.final_score = full.get("geometry_score", 0.0)
    result.stopped_at = CompareTier.FULL
    result.detail["full_analysis"] = {
        "geometry_score": full.get("geometry_score"),
        "axis_scores": full.get("axis_scores"),
    }
    return result


def compare_basis_signatures_only(sig_a: BasisSignature, sig_b: BasisSignature) -> TieredCompareResult:
    """Tier 0–1 ohne GpmDocument — für Index-Ranking."""
    result = TieredCompareResult()
    gate_result, shared, gate_tiers = _run_signature_gates(sig_a, sig_b, use_document_relevance=False)
    if gate_result is not None:
        return gate_result
    result.shared_prime_count = shared
    result.tiers_run.extend(gate_tiers)

    result.basis_score, basis_detail = _compute_basis_score(sig_a, sig_b)
    result.detail.update(basis_detail)
    result.final_score = result.basis_score
    result.stopped_at = CompareTier.BASIS
    result.tiers_run.append("basis_signature")
    return result
