"""Mathematisch-strukturelle Kreuzvalidierung — 5-Schritt-Pipeline ohne Plagiat-Semantik."""

from __future__ import annotations

from gpm.interval_index import BITSET_TOKEN_LIMIT
from gpm.model import GpmDocument

from ge_prime.hierarchy import get_interval_index

MODERATE_AXIS_THRESHOLD = 0.35
COMBINED_ISOMORPHISM_THRESHOLD = 0.55
META_GENOME_STRONG_THRESHOLD = 0.18

STEP_IDS = (
    "nfc_tokenization",
    "bitmask_prefilter",
    "geometry_curves",
    "enjambement_phase",
    "db_matrix_audit",
)


def _step(step_id: str, status: str, detail: dict | None = None) -> dict:
    return {"id": step_id, "status": status, "detail": detail or {}}


def pair_relevance_prefilter(document_a: GpmDocument, document_b: GpmDocument) -> dict:
    """Schritt 2: IntervalIndex/Bitmask-Status und grobe Substanz-Profil-Überlappung."""
    n_a = len(document_a.tokens)
    n_b = len(document_b.tokens)
    if n_a == 0 or n_b == 0:
        return {
            "relevant": False,
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

    prof_a = document_a.substance_index
    prof_b = document_b.substance_index
    shared_primes = 0
    if prof_a is not None and prof_b is not None:
        keys_a = set(prof_a.primes())
        keys_b = set(prof_b.primes())
        shared_primes = len(keys_a & keys_b)

    relevant = shared_primes > 0 or (n_a > 0 and n_b > 0)
    return {
        "relevant": relevant,
        "token_count_a": n_a,
        "token_count_b": n_b,
        "interval_index_a": idx_a is not None,
        "interval_index_b": idx_b is not None,
        "bitmask_a": bitmask_a,
        "bitmask_b": bitmask_b,
        "bitmask_limit": BITSET_TOKEN_LIMIT,
        "shared_prime_count": shared_primes,
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
    db_audit = structure_assessment.get("db_speech_audit") or {}

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
            "meta_ggt_similarity": (meta_comparison or {}).get("similarity_ratio"),
            "meta_ggt_diagnostics": (meta_comparison or {}).get("meta_ggt_diagnostics"),
            "cell_geometry": (comparison.get("cell_geometry") or {}).get("geometry_score"),
            "substance_geometry": (comparison.get("substance_geometry") or {}).get("geometry_score"),
            "hierarchy_line_dtw": (struct_hc.get("line") or {}).get("geometry_score"),
            "hierarchy_sentence_dtw": (sem_hc.get("sentence") or {}).get("geometry_score"),
        },
    )
    step4 = _step(
        "enjambement_phase",
        "ok" if enj_phase["phase_shift_detected"] or enj_phase["rhythm_break_count_a"] or enj_phase["rhythm_break_count_b"] else "skip",
        enj_phase,
    )
    audit_status = db_audit.get("audit_status", "unknown")
    step5_status = "skip" if audit_status == "unknown" and not db_audit else "ok"
    if db_audit.get("language_uncertain"):
        step5_status = "warn"
    elif audit_status == "CRITICAL_ANOMALY":
        step5_status = "warn"
    step5 = _step(
        "db_matrix_audit",
        step5_status,
        {
            "audit_status": audit_status,
            "primary_language": db_audit.get("primary_language"),
            "confidence": db_audit.get("confidence"),
            "language_uncertain": db_audit.get("language_uncertain"),
            "db_audit_mode": structure_assessment.get("db_audit_mode"),
        },
    )

    steps = [step1, step2, step3, step4, step5]
    return {
        "steps": steps,
        "enjambement_phase": enj_phase,
        "classification": structure_assessment.get("classification"),
        "isomorphism_index": structure_assessment.get("isomorphism_index"),
    }
