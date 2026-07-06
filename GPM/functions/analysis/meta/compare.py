"""Meta-Genom-Vergleich und Struktur-Matrix — ohne DB."""

from __future__ import annotations

from alphabets.registry import char_map_for_profile

from analysis.algebra.fusion import fuse_isomorphism_index
from analysis.meta.fingerprint import compare_profiles, profile_from_meta

DOMAIN_SIMILARITY_THRESHOLD = 0.12
META_GENOME_STRONG_THRESHOLD = 0.18
COMBINED_ISOMORPHISM_THRESHOLD = 0.55
SAME_DOMAIN_RELATIONAL_THRESHOLD = 0.35


def compare_meta_genomes(
    meta_a: dict,
    meta_b: dict,
    *,
    relation_comparison: dict | None = None,
    alphabet_profile=None,
) -> dict:
    doc_profile = alphabet_profile or meta_a.get("document_profile") or "og"
    profile_a = profile_from_meta(meta_a, document_profile=doc_profile)
    profile_b = profile_from_meta(meta_b, document_profile=doc_profile)
    cmp = compare_profiles(profile_a, profile_b, document_profile=doc_profile)
    shared_profile = cmp["shared_profile"]
    similarity = cmp["similarity_ratio"]
    rel_score = (relation_comparison or {}).get("relation_score", 0.0)
    char_map = char_map_for_profile(doc_profile)

    return {
        "gcd_value": cmp["gcd_value"],
        "similarity_ratio": similarity,
        "ggt_kgv_similarity": cmp.get("ggt_kgv_similarity", similarity),
        "relation_score": rel_score,
        "shared_letters": cmp["shared_letters"],
        "heavy_shared_primes": [
            {"prime": p, "letter": char_map.get(p, "?"), "exponent": shared_profile[p]}
            for p in sorted(shared_profile.keys(), reverse=True)[:8]
        ],
        "meta_ggt_diagnostics": {
            "log_gcd": cmp.get("log_gcd", 0.0),
            "log_a": cmp.get("log_a", 0.0),
            "log_b": cmp.get("log_b", 0.0),
            "log_lcm": cmp.get("log_lcm", 0.0),
            "shared_prime_count": cmp.get("shared_prime_count", 0),
            "shared_prime_entries": cmp.get("shared_prime_entries", []),
            "zero_reason": cmp.get("zero_reason"),
        },
    }


def assess_structure_matrix(
    *,
    icurve_comparison: dict,
    meta_a: dict,
    meta_b: dict,
    meta_comparison: dict,
    relation_comparison: dict | None = None,
    cross_a: dict | None = None,
    cross_b: dict | None = None,
) -> dict:
    from analysis.profile.relation import relation_twins
    from analysis.validation.structure import classify_structure_pattern, compare_enjambement_phases

    relation_comparison = relation_comparison or {}
    word_geo = icurve_comparison.get("geometry_score", 0.0)
    literal = icurve_comparison.get("literal_match_ratio", 0.0)
    meta_sim = meta_comparison.get("similarity_ratio", 0.0)
    aligned = icurve_comparison.get("aligned", False)

    cell_cmp = icurve_comparison.get("cell_geometry") or {}
    cell_score = cell_cmp.get("geometry_score", 0.0)
    subst_cmp = icurve_comparison.get("substance_geometry") or {}
    subst_score = subst_cmp.get("geometry_score", 0.0)
    rel_score = relation_comparison.get("relation_score", 0.0)

    word_parallel = bool(icurve_comparison.get("structural_waveform_parallel"))
    substance_parallel = bool(subst_cmp.get("substance_parallel"))
    relation_twins_flag = relation_twins(relation_comparison, literal_match_ratio=literal)
    meta_genome_strong = meta_sim >= META_GENOME_STRONG_THRESHOLD

    if aligned:
        combined = fuse_isomorphism_index(
            aligned=True,
            word_geo=word_geo,
            cell_score=cell_score,
            subst_score=subst_score,
            rel_score=rel_score,
            meta_sim=meta_sim,
            literal=literal,
        )
    else:
        combined = fuse_isomorphism_index(
            aligned=False,
            word_geo=word_geo,
            cell_score=cell_score,
            subst_score=subst_score,
            rel_score=rel_score,
            meta_sim=meta_sim,
            literal=literal,
        )

    signals: list[str] = []
    if word_parallel:
        signals.append("word_parallel")
    if substance_parallel:
        signals.append("substance_parallel")
    if relation_twins_flag:
        signals.append("relation_twins")
    if meta_genome_strong:
        signals.append("meta_genome_strong")

    bullets: list[str] = []
    if word_parallel:
        bullets.append(f"Wort-Wellenform parallel (DTW {word_geo:.0%})")
    if substance_parallel:
        bullets.append(f"Substanz-Kette deckt {subst_score:.0%}")
    if relation_twins_flag:
        bullets.append(f"Relations-Score {rel_score:.0%}")
    if meta_genome_strong:
        bullets.append(f"Meta-Genom ggT {meta_sim:.0%}")
    if not bullets:
        bullets.append("Keine auffällige Achsen-Überlappung")

    enj_phase = compare_enjambement_phases(cross_a, cross_b)
    classification = classify_structure_pattern(
        word_geo=word_geo,
        substance_score=subst_score,
        literal=literal,
        combined=combined,
        relation_score=rel_score,
        enjambement_phase=enj_phase,
        structural_waveform_parallel=word_parallel,
    )

    return {
        "isomorphism_index": round(combined, 6),
        "classification": classification,
        "combined_score": round(combined, 6),
        "geometry_score": word_geo,
        "meta_genome_similarity": meta_sim,
        "literal_match_ratio": literal,
        "signals": signals,
        "interpretation": " · ".join(bullets),
        "interpretation_bullets": bullets,
        "substance_parallel": substance_parallel,
        "relation_twins": relation_twins_flag,
        "meta_genome_strong": meta_genome_strong,
    }
