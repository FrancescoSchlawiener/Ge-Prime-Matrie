"""Pair-Analyse anreichern — Meta-Genom ohne DB."""

from __future__ import annotations

from analysis.document.model import GpmDocument
from analysis.meta.compare import assess_structure_matrix, compare_meta_genomes
from analysis.meta.genome import build_meta_genome
from analysis.profile.relation import (
    build_relation_profile,
    compare_relation_profiles,
    relation_twins,
)


def enrich_pair_analysis(
    document_a: GpmDocument,
    document_b: GpmDocument,
    icurve_comparison: dict,
    *,
    cross_a: dict | None = None,
    cross_b: dict | None = None,
) -> dict:
    meta_a = build_meta_genome(document_a)
    meta_b = build_meta_genome(document_b)
    prof_a = build_relation_profile(document_a)
    prof_b = build_relation_profile(document_b)
    relation_comparison = compare_relation_profiles(prof_a, prof_b)
    meta_comparison = compare_meta_genomes(
        meta_a,
        meta_b,
        relation_comparison=relation_comparison,
        alphabet_profile=document_a.profile,
    )
    icurve_comparison["relation_twins"] = relation_twins(
        relation_comparison,
        literal_match_ratio=icurve_comparison.get("literal_match_ratio", 0.0),
    )
    structure = assess_structure_matrix(
        icurve_comparison=icurve_comparison,
        meta_a=meta_a,
        meta_b=meta_b,
        meta_comparison=meta_comparison,
        relation_comparison=relation_comparison,
        cross_a=cross_a,
        cross_b=cross_b,
    )
    return {
        "meta_a": meta_a,
        "meta_b": meta_b,
        "meta_comparison": meta_comparison,
        "relation_comparison": relation_comparison,
        "structure_assessment": structure,
    }
