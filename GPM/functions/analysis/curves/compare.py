"""Orthogonale DTW-Fusion — analyze_pair (Absicherung C)."""

from __future__ import annotations

from dataclasses import dataclass

from analysis.blocks.build import materialize_geometry
from analysis.blocks.walk import flatten_sequence
from analysis.curves.i_curve import extract_cell_curve, extract_i_curve
from analysis.curves.substance_curve import extract_substance_curve
from analysis.document.model import GpmDocument
from analysis.geom.dtw import dtw_similarity
from analysis.substance.compare import substance_ggt_kgv_distance, substance_ggt_kgv_similarity
from analysis.substance.diff import classify_word_pair


@dataclass(frozen=True)
class AxisWeights:
    substance: float = 0.25
    token_i: float = 0.35
    cell_i: float = 0.25
    hierarchy: float = 0.15


@dataclass
class FusionResult:
    axis_scores: dict[str, float]
    geometry_score: float
    substance_parallel: bool
    structural_twin: bool


def _token_i_distance(a: dict, b: dict) -> float:
    i_sim = 1.0 - abs(a["i_ratio"] - b["i_ratio"])
    if a["substance"] == b["substance"] and a["perm_index"] != b["perm_index"]:
        phase_penalty = 0.5
    else:
        phase_penalty = 0.0
    return 1.0 - max(0.0, i_sim - phase_penalty)


def _cell_i_distance(a: dict, b: dict) -> float:
    i_sim = 1.0 - abs(a["i_satz_ratio"] - b["i_satz_ratio"])
    sk_match = 1.0 if a["skeleton_hash"] == b["skeleton_hash"] else 0.0
    return 1.0 - (0.7 * i_sim + 0.3 * sk_match)


def fuse_axis_scores(scores: dict[str, float], weights: AxisWeights) -> float:
    total_w = weights.substance + weights.token_i + weights.cell_i + weights.hierarchy
    return (
        scores.get("substance", 0.0) * weights.substance
        + scores.get("token_i", 0.0) * weights.token_i
        + scores.get("cell_i", 0.0) * weights.cell_i
        + scores.get("hierarchy", 0.0) * weights.hierarchy
    ) / total_w


def _hierarchy_distance(a: int, b: int) -> float:
    return 0.0 if a == b else 1.0


def analyze_pair(
    doc_a: GpmDocument,
    doc_b: GpmDocument,
    *,
    weights: AxisWeights | None = None,
) -> dict:
    weights = weights or AxisWeights()
    materialize_geometry(doc_a)
    materialize_geometry(doc_b)

    sub_a = [p["substance"] for p in extract_substance_curve(doc_a)]
    sub_b = [p["substance"] for p in extract_substance_curve(doc_b)]
    sub_dtw = dtw_similarity(sub_a, sub_b, substance_ggt_kgv_distance)

    i_a = extract_i_curve(doc_a)
    i_b = extract_i_curve(doc_b)
    tok_dtw = dtw_similarity(i_a, i_b, _token_i_distance)

    cell_a = extract_cell_curve(doc_a)
    cell_b = extract_cell_curve(doc_b)
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
        para_a = [p.perm_index for p in (doc_a.hierarchy.semantic.sentences if doc_a.hierarchy else [])]
        para_b = [p.perm_index for p in (doc_b.hierarchy.semantic.sentences if doc_b.hierarchy else [])]
        if para_a and para_b:
            hier_dtw = dtw_similarity(para_a, para_b, lambda x, y: 0.0 if x == y else 1.0)
            hier_score = hier_dtw.similarity
        else:
            hier_score = 0.0

    axis_scores = {
        "substance": sub_dtw.similarity,
        "token_i": tok_dtw.similarity,
        "cell_i": cell_dtw.similarity,
        "hierarchy": hier_score,
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
