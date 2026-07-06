"""Orthogonale DTW-Fusion — analyze_pair (Absicherung C)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from dataclasses import dataclass

from analysis.align.substance_align import compare_substance_sequences, extract_substance_curve
from analysis.blocks.build import materialize_geometry
from analysis.blocks.walk import flatten_sequence
from analysis.curves.i_curve import (
    compare_cell_geometry,
    compare_i_curves,
    extract_cell_geometry,
    extract_i_curve,
    summarize_curve,
)
from analysis.document.model import GpmDocument
from analysis.geom.dtw import dtw_similarity
from analysis.hierarchy.compare import compare_level_sequences
from analysis.hierarchy.curves import (
    extract_line_curve,
    extract_paragraph_curve,
    extract_phrase_curve,
    extract_sentence_curve,
)
from analysis.hierarchy.enjambement import cross_analysis
from analysis.meta.enrich import enrich_pair_analysis
from analysis.algebra.fusion import fuse_cell_i_similarity, fuse_weighted_scores
from analysis.algebra.i_metrics import i_ratio_similarity
from analysis.algebra.substance_kernel import substance_ggt_kgv_distance, substance_ggt_kgv_similarity
from analysis.substance.diff import classify_word_pair
from analysis.ui.sparkline import downsample_curve_points
from analysis.validation.structure import build_validation_pipeline

if TYPE_CHECKING:
    from analysis.basis.signature import BasisSignature

_WEIGHT_TOLERANCE = 1e-9


@dataclass(frozen=True)
class AxisWeights:
    substance: float = 0.25
    token_i: float = 0.35
    cell_i: float = 0.25
    hierarchy: float = 0.15
    literal: float = 0.0
    hierarchy_sentence: float = 0.0
    hierarchy_line: float = 0.0

    def active_weights(self) -> dict[str, float]:
        raw = {
            "substance": self.substance,
            "token_i": self.token_i,
            "cell_i": self.cell_i,
            "hierarchy": self.hierarchy,
            "literal": self.literal,
            "hierarchy_sentence": self.hierarchy_sentence,
            "hierarchy_line": self.hierarchy_line,
        }
        return {k: v for k, v in raw.items() if v > 0}

    def validate(self, *, tol: float = 1e-9) -> None:
        total = sum(self.active_weights().values())
        if abs(total - 1.0) > tol:
            raise ValueError(f"AxisWeights müssen Summe 1.0 ergeben, got {total}")

    def normalized(self) -> dict[str, float]:
        active = self.active_weights()
        total = sum(active.values()) or 1.0
        return {k: v / total for k, v in active.items()}

    @classmethod
    def full(cls) -> AxisWeights:
        return cls(
            substance=0.18,
            token_i=0.22,
            cell_i=0.18,
            hierarchy=0.10,
            literal=0.12,
            hierarchy_sentence=0.10,
            hierarchy_line=0.10,
        )


@dataclass
class FusionResult:
    axis_scores: dict[str, float]
    geometry_score: float
    substance_parallel: bool
    structural_twin: bool


def _clamp_score(value: float) -> float:
    return max(0.0, min(1.0, value))


def _token_i_distance(a: dict, b: dict) -> float:
    i_sim = i_ratio_similarity(a["i_ratio"], b["i_ratio"])
    if a["substance"] == b["substance"] and a["perm_index"] != b["perm_index"]:
        i_sim = max(0.0, i_sim - 0.5)
    return 1.0 - i_sim


def _cell_i_distance(a: dict, b: dict) -> float:
    i_sim = i_ratio_similarity(a["i_satz_ratio"], b["i_satz_ratio"])
    sk_match = 1.0 if a.get("skeleton_hash") == b.get("skeleton_hash") else 0.0
    return 1.0 - fuse_cell_i_similarity(i_sim, sk_match)


def fuse_axis_scores(scores: dict[str, float], weights: AxisWeights) -> float:
    return fuse_weighted_scores(scores, weights.normalized(), clamp=True)


def _hierarchy_distance(a: int, b: int) -> float:
    return 0.0 if a == b else 1.0


def analyze_pair(
    doc_a: GpmDocument,
    doc_b: GpmDocument,
    *,
    weights: AxisWeights | None = None,
    basis_prefilter: bool | BasisSignature | None = None,
) -> dict:
    if basis_prefilter is not None and basis_prefilter is not False:
        from analysis.basis.compare_tiered import (
            CompareTier,
            compare_basis_signatures_only,
            compare_documents_tiered,
        )
        from analysis.basis.signature import BasisSignature as _BasisSignature

        if isinstance(basis_prefilter, _BasisSignature):
            from analysis.basis.signature import get_basis_signature

            sig_b = get_basis_signature(doc_b)
            tiered = compare_basis_signatures_only(basis_prefilter, sig_b)
        else:
            tiered = compare_documents_tiered(doc_a, doc_b, max_tier=CompareTier.BASIS)
        if tiered.zero_reason:
            return {
                "axis_scores": {},
                "geometry_score": 0.0,
                "substance_parallel": False,
                "structural_twin": False,
                "zero_reason": tiered.zero_reason,
                "basis_prefilter": True,
                "basis_score": tiered.basis_score,
            }
    weights = weights or AxisWeights()
    materialize_geometry(doc_a)
    materialize_geometry(doc_b)

    sub_a = [p["substance"] for p in extract_substance_curve(doc_a)]
    sub_b = [p["substance"] for p in extract_substance_curve(doc_b)]
    sub_dtw = dtw_similarity(sub_a, sub_b, substance_ggt_kgv_distance)

    i_a = extract_i_curve(doc_a)
    i_b = extract_i_curve(doc_b)
    tok_dtw = dtw_similarity(i_a, i_b, _token_i_distance)

    cell_a = extract_cell_geometry(doc_a)
    cell_b = extract_cell_geometry(doc_b)
    cell_dtw = dtw_similarity(cell_a, cell_b, _cell_i_distance)

    hier_a: list[int] = []
    hier_b: list[int] = []
    if doc_a.root_block is not None:
        hier_a = [r.ptr_id for r in flatten_sequence(doc_a.root_block) if r.kind.value == "C"]
    if doc_b.root_block is not None:
        hier_b = [r.ptr_id for r in flatten_sequence(doc_b.root_block) if r.kind.value == "C"]
    if hier_a or hier_b:
        hier_dtw = dtw_similarity(hier_a or [0], hier_b or [0], _hierarchy_distance)
        hier_score = hier_dtw.similarity
    else:
        para_a = [
            p.perm_index for p in (doc_a.hierarchy.semantic.sentences if doc_a.hierarchy else [])
        ]
        para_b = [
            p.perm_index for p in (doc_b.hierarchy.semantic.sentences if doc_b.hierarchy else [])
        ]
        if para_a and para_b:
            hier_dtw = dtw_similarity(para_a, para_b, lambda x, y: 0.0 if x == y else 1.0)
            hier_score = hier_dtw.similarity
        else:
            hier_score = 0.0

    axis_scores = {
        "substance": _clamp_score(sub_dtw.similarity),
        "token_i": _clamp_score(tok_dtw.similarity),
        "cell_i": _clamp_score(cell_dtw.similarity),
        "hierarchy": _clamp_score(hier_score),
    }
    geometry_score = fuse_axis_scores(axis_scores, weights)
    fusion = FusionResult(
        axis_scores=axis_scores,
        geometry_score=geometry_score,
        substance_parallel=axis_scores["substance"] >= 0.9 and axis_scores["token_i"] < 0.95,
        structural_twin=axis_scores["cell_i"] >= 0.85,
    )

    return {
        "axis_scores": fusion.axis_scores,
        "geometry_score": round(fusion.geometry_score, 6),
        "substance_parallel": fusion.substance_parallel,
        "structural_twin": fusion.structural_twin,
        "substance_dtw": sub_dtw,
        "token_i_dtw": tok_dtw,
        "cell_i_dtw": cell_dtw,
    }


def analyze_pair_full(
    doc_a: GpmDocument,
    doc_b: GpmDocument,
    *,
    weights: AxisWeights | None = None,
) -> dict:
    weights = weights or AxisWeights.full()
    weights.validate()
    materialize_geometry(doc_a)
    materialize_geometry(doc_b)

    base = analyze_pair(doc_a, doc_b, weights=AxisWeights())

    curve_a = extract_i_curve(doc_a)
    curve_b = extract_i_curve(doc_b)
    substance_a = extract_substance_curve(doc_a)
    substance_b = extract_substance_curve(doc_b)
    cells_a = extract_cell_geometry(doc_a)
    cells_b = extract_cell_geometry(doc_b)

    comparison = compare_i_curves(
        curve_a,
        curve_b,
        substance_a=substance_a,
        substance_b=substance_b,
        document_a=doc_a,
        document_b=doc_b,
    )
    cell_comparison = compare_cell_geometry(cells_a, cells_b)
    substance_comparison = compare_substance_sequences(
        substance_a,
        substance_b,
        literal_match_ratio=comparison["literal_match_ratio"],
        profile=doc_a.profile,
    )
    comparison["cell_geometry"] = cell_comparison
    comparison["substance_geometry"] = substance_comparison
    comparison["substance_parallel"] = substance_comparison.get("substance_parallel", False)
    comparison["structural_twin"] = cell_comparison.get("geometry_score", 0.0) >= 0.75

    semantic_a = {
        "paragraphs": extract_paragraph_curve(doc_a),
        "sentences": extract_sentence_curve(doc_a),
        "phrases": extract_phrase_curve(doc_a),
    }
    semantic_b = {
        "paragraphs": extract_paragraph_curve(doc_b),
        "sentences": extract_sentence_curve(doc_b),
        "phrases": extract_phrase_curve(doc_b),
    }
    structural_a = {"lines": extract_line_curve(doc_a)}
    structural_b = {"lines": extract_line_curve(doc_b)}
    hierarchy_comparison = {
        "semantic": {
            "phrase": compare_level_sequences(
                semantic_a["phrases"], semantic_b["phrases"], ratio_key="i_phrase_ratio"
            ),
            "sentence": compare_level_sequences(
                semantic_a["sentences"], semantic_b["sentences"], ratio_key="i_satz_ratio"
            ),
            "paragraph": compare_level_sequences(
                semantic_a["paragraphs"], semantic_b["paragraphs"], ratio_key="i_absatz_ratio"
            ),
        },
        "structural": {
            "line": compare_level_sequences(
                structural_a["lines"], structural_b["lines"], ratio_key="i_zeile_ratio"
            ),
        },
    }

    extended_scores = {
        **base["axis_scores"],
        "literal": _clamp_score(comparison["literal_match_ratio"]),
        "hierarchy_sentence": _clamp_score(
            hierarchy_comparison["semantic"]["sentence"].get("geometry_score", 0.0)
        ),
        "hierarchy_line": _clamp_score(
            hierarchy_comparison["structural"]["line"].get("geometry_score", 0.0)
        ),
    }
    comparison["geometry_score"] = round(fuse_axis_scores(extended_scores, weights), 6)
    comparison["axis_scores"] = extended_scores
    comparison["substance_parallel"] = extended_scores["substance"] >= 0.9 and extended_scores[
        "token_i"
    ] < 0.95
    comparison["structural_twin"] = extended_scores["cell_i"] >= 0.85

    cross_a = cross_analysis(doc_a)
    cross_b = cross_analysis(doc_b)
    meta = enrich_pair_analysis(doc_a, doc_b, comparison, cross_a=cross_a, cross_b=cross_b)
    validation_pipeline = build_validation_pipeline(
        document_a=doc_a,
        document_b=doc_b,
        comparison=comparison,
        hierarchy_comparison=hierarchy_comparison,
        cross_a=cross_a,
        cross_b=cross_b,
        structure_assessment=meta["structure_assessment"],
        meta_comparison=meta["meta_comparison"],
    )

    return {
        **base,
        "curve_a": downsample_curve_points(curve_a, 500),
        "curve_b": downsample_curve_points(curve_b, 500),
        "substance_a": substance_a,
        "substance_b": substance_b,
        "summary_a": summarize_curve(curve_a),
        "summary_b": summarize_curve(curve_b),
        "comparison": comparison,
        "hierarchy_comparison": hierarchy_comparison,
        "cross_analysis_a": cross_a,
        "cross_analysis_b": cross_b,
        "meta_a": meta["meta_a"],
        "meta_b": meta["meta_b"],
        "meta_comparison": meta["meta_comparison"],
        "relation_comparison": meta["relation_comparison"],
        "structure_assessment": meta["structure_assessment"],
        "validation_pipeline": validation_pipeline,
        "geometry_score": comparison["geometry_score"],
    }


def compare_word_pair_analysis(
    s1: int,
    s2: int,
    i1: int,
    i2: int,
    profile,
) -> dict:
    classification = classify_word_pair(s1, s2, i1, i2, profile)
    sim = substance_ggt_kgv_similarity(s1, s2)
    return {
        "classification": classification,
        "substance_similarity": round(sim, 6),
        "token_i_expected_low": classification.get("is_anagram", False),
    }
