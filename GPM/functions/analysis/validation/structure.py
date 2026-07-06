"""Mathematisch-strukturelle Kreuzvalidierung — 5-Schritt-Pipeline."""

from __future__ import annotations

from analysis.document.model import GpmDocument
from analysis.hierarchy.access import get_interval_index
from analysis.index.interval_index import BITSET_TOKEN_LIMIT
from analysis.index.substance_index import get_substance_index

MODERATE_AXIS_THRESHOLD = 0.35
COMBINED_ISOMORPHISM_THRESHOLD = 0.55
META_GENOME_STRONG_THRESHOLD = 0.18

STEP_IDS = (
    "nfc_tokenization",
    "bitmask_prefilter",
    "geometry_curves",
    "enjambement_phase",
    "meta_profile_audit",
)


def _step(step_id: str, status: str, detail: dict | None = None) -> dict:
    return {"id": step_id, "status": status, "detail": detail or {}}


def _interval_bitmask_status(document_a: GpmDocument, document_b: GpmDocument) -> dict:
    """IntervalIndex/Bitmask ohne Tiered-Vergleich — bricht Rekursion."""
    n_a = len(document_a.tokens)
    n_b = len(document_b.tokens)
    if n_a == 0 or n_b == 0:
        return {
            "token_count_a": n_a,
            "token_count_b": n_b,
            "interval_index_a": False,
            "interval_index_b": False,
            "bitmask_a": False,
            "bitmask_b": False,
            "shared_prime_count": 0,
        }
    idx_a = get_interval_index(document_a)
    idx_b = get_interval_index(document_b)
    bitmask_a = idx_a.line._bitmasks is not None if idx_a.line else False
    bitmask_b = idx_b.line._bitmasks is not None if idx_b.line else False
    prof_a = get_substance_index(document_a)
    prof_b = get_substance_index(document_b)
    shared_primes = len(set(prof_a.primes()) & set(prof_b.primes()))
    return {
        "token_count_a": n_a,
        "token_count_b": n_b,
        "interval_index_a": idx_a is not None,
        "interval_index_b": idx_b is not None,
        "bitmask_a": bitmask_a,
        "bitmask_b": bitmask_b,
        "bitmask_limit": BITSET_TOKEN_LIMIT,
        "shared_prime_count": shared_primes,
    }


def pair_relevance_prefilter(document_a: GpmDocument, document_b: GpmDocument) -> dict:
    """Schritt 2: Tiered-Basis-Score + IntervalIndex/Bitmask-Status."""
    interval = _interval_bitmask_status(document_a, document_b)
    if interval["token_count_a"] == 0 or interval["token_count_b"] == 0:
        return {
            **interval,
            "relevant": False,
            "basis_score": 0.0,
            "zero_reason": "empty_document",
            "structure_score": None,
        }

    from analysis.basis.compare_tiered import CompareTier, compare_documents_tiered

    tiered = compare_documents_tiered(
        document_a,
        document_b,
        max_tier=CompareTier.BASIS,
    )

    shared_primes = tiered.shared_prime_count or interval["shared_prime_count"]
    relevant = tiered.zero_reason not in ("profile_mismatch", "no_shared_primes", "empty_profile")
    if tiered.zero_reason is None:
        relevant = True
    elif tiered.zero_reason == "basis_score_below_threshold":
        relevant = tiered.basis_score > 0

    return {
        **interval,
        "relevant": relevant,
        "shared_prime_count": shared_primes,
        "basis_score": tiered.basis_score,
        "structure_score": None,
        "zero_reason": tiered.zero_reason,
        "stopped_at_tier": tiered.stopped_at.name if tiered.stopped_at else None,
    }


def compare_enjambement_phases(cross_a: dict | None, cross_b: dict | None) -> dict:
    """Schritt 4: Phasenverschiebung zwischen Satz-/Zeilenkanten A und B."""
    cross_a = cross_a or {}
    cross_b = cross_b or {}
    count_a = cross_a.get("rhythm_break_count", 0)
    count_b = cross_b.get("rhythm_break_count", 0)
    profile_a = cross_a.get("enjambement_profile", "—")
    profile_b = cross_b.get("enjambement_profile", "—")
    ratio_a = cross_a.get("line_aligned_ratio")
    ratio_b = cross_b.get("line_aligned_ratio")
    rhythm_break_delta = abs(count_a - count_b)
    profiles_match = profile_a == profile_b and profile_a not in ("—", None)
    phase_shift_detected = rhythm_break_delta > 0 or (
        profiles_match and profile_a in ("rhythm_break", "enjambement_noise")
    )
    return {
        "rhythm_break_count_a": count_a,
        "rhythm_break_count_b": count_b,
        "rhythm_break_delta": rhythm_break_delta,
        "enjambement_profile_a": profile_a,
        "enjambement_profile_b": profile_b,
        "line_aligned_ratio_a": ratio_a,
        "line_aligned_ratio_b": ratio_b,
        "profiles_match": profiles_match,
        "phase_shift_detected": phase_shift_detected,
    }


def classify_structure_pattern(
    *,
    word_geo: float,
    substance_score: float,
    literal: float,
    combined: float,
    relation_score: float,
    enjambement_phase: dict,
    structural_waveform_parallel: bool,
) -> str:
    """Wertfreie Klassifikation der Matrix-Beziehung."""
    if literal >= 0.999 and word_geo >= 0.999:
        return "literal_identity"
    profiles_match = enjambement_phase.get("profiles_match", False)
    if (
        word_geo < MODERATE_AXIS_THRESHOLD
        and substance_score < MODERATE_AXIS_THRESHOLD
        and (profiles_match or relation_score >= 0.5)
    ):
        return "style_symmetry"
    if combined >= COMBINED_ISOMORPHISM_THRESHOLD or structural_waveform_parallel:
        return "partial_isomorphism"
    if combined < MODERATE_AXIS_THRESHOLD and not structural_waveform_parallel:
        return "independent"
    return "partial_isomorphism"


def meta_profile_audit(meta_comparison: dict | None) -> dict:
    if not meta_comparison:
        return {"audit_status": "unknown", "available": False}
    sim = meta_comparison.get("similarity_ratio", 0.0)
    return {
        "audit_status": "ok" if sim >= META_GENOME_STRONG_THRESHOLD else "low_overlap",
        "available": True,
        "similarity_ratio": sim,
        "profile_overlap_low": sim < META_GENOME_STRONG_THRESHOLD,
    }


def build_validation_pipeline(
    *,
    document_a: GpmDocument,
    document_b: GpmDocument,
    comparison: dict,
    hierarchy_comparison: dict,
    cross_a: dict,
    cross_b: dict,
    structure_assessment: dict,
    meta_comparison: dict | None = None,
) -> dict:
    """Chronologische 5-Schritt-Kreuzvalidierung für API/UI."""
    prefilter = pair_relevance_prefilter(document_a, document_b)
    enj_phase = compare_enjambement_phases(cross_a, cross_b)
    meta_cmp = meta_comparison or {}

    step1 = _step(
        "nfc_tokenization",
        "ok" if prefilter["token_count_a"] and prefilter["token_count_b"] else "skip",
        {
            "token_count_a": prefilter["token_count_a"],
            "token_count_b": prefilter["token_count_b"],
            "nfc": True,
        },
    )
    step2 = _step(
        "bitmask_prefilter",
        "ok" if prefilter["relevant"] else "warn",
        prefilter,
    )
    struct_hc = (hierarchy_comparison or {}).get("structural") or {}
    sem_hc = (hierarchy_comparison or {}).get("semantic") or {}
    step3 = _step(
        "geometry_curves",
        "ok",
        {
            "word_geometry_dtw": comparison.get("geometry_score_dtw"),
            "word_geometry_mae": comparison.get("geometry_score_mae"),
            "literal_match_ratio": comparison.get("literal_match_ratio"),
            "literal_diagnostics": comparison.get("literal_diagnostics"),
            "meta_ggt_similarity": meta_cmp.get("similarity_ratio"),
            "meta_ggt_diagnostics": meta_cmp.get("meta_ggt_diagnostics"),
            "cell_geometry": (comparison.get("cell_geometry") or {}).get("geometry_score"),
            "substance_geometry": (comparison.get("substance_geometry") or {}).get("geometry_score"),
            "hierarchy_line_dtw": (struct_hc.get("line") or {}).get("geometry_score"),
            "hierarchy_sentence_dtw": (sem_hc.get("sentence") or {}).get("geometry_score"),
        },
    )
    step4 = _step(
        "enjambement_phase",
        "ok"
        if enj_phase["phase_shift_detected"]
        or enj_phase["rhythm_break_count_a"]
        or enj_phase["rhythm_break_count_b"]
        else "skip",
        enj_phase,
    )

    similarity = meta_cmp.get("similarity_ratio")
    has_meta = similarity is not None
    if not has_meta:
        step5_status = "skip"
    elif similarity >= META_GENOME_STRONG_THRESHOLD:
        step5_status = "ok"
    elif similarity <= 0.0:
        step5_status = "warn"
    else:
        step5_status = "ok"

    step5 = _step(
        "meta_profile_audit",
        step5_status,
        {
            "profile_overlap": similarity,
            "shared_prime_count": (meta_cmp.get("meta_ggt_diagnostics") or {}).get(
                "shared_prime_count", 0
            ),
            "zero_reason": (meta_cmp.get("meta_ggt_diagnostics") or {}).get("zero_reason"),
            "same_domain": meta_cmp.get("same_domain", False),
        },
    )

    steps = [step1, step2, step3, step4, step5]
    return {
        "steps": steps,
        "enjambement_phase": enj_phase,
        "classification": structure_assessment.get("classification"),
        "isomorphism_index": structure_assessment.get("isomorphism_index"),
    }
