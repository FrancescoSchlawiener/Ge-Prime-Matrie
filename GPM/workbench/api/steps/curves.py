"""I-Kurven-Hilfen — vollständige Paaranalyse für I-Kurve-Tab."""

from __future__ import annotations

from analysis.curves.compare import analyze_pair_full
from analysis.curves.i_curve import extract_cell_geometry, extract_i_curve, summarize_curve
from analysis.document.model import GpmDocument
from analysis.document.preview import (
    assert_referential_integrity,
    build_genome_preview,
    build_geometry_preview,
)
from analysis.hierarchy.curves import (
    extract_line_curve,
    extract_paragraph_curve,
    extract_phrase_curve,
    extract_sentence_curve,
)
from analysis.hierarchy.viewport import serialize_viewport
from analysis.ui.sparkline import downsample_curve_points
from api.helpers.json_sanitize import json_sanitize
from api.schemas.common import CurveMeta, Step

SPARKLINE_LIMIT = 512
RESPONSE_POINT_LIMIT = SPARKLINE_LIMIT
PREVIEW_POINT_LIMIT = 80
MAX_I_CURVE_TOKENS = 10_000


def _assert_icurve_dual_gateway(doc_a: GpmDocument, doc_b: GpmDocument) -> None:
    """Invariante I3-G: beide Docs synchron validieren vor Extraktion/DTW."""
    assert_referential_integrity(doc_a)
    assert_referential_integrity(doc_b)


def assert_icurve_token_limit(doc_a: GpmDocument, doc_b: GpmDocument) -> None:
    if len(doc_a.tokens) > MAX_I_CURVE_TOKENS or len(doc_b.tokens) > MAX_I_CURVE_TOKENS:
        raise ValueError("icurve_token_limit_exceeded")


def downsample_curve(points: list[dict]) -> tuple[list[dict], CurveMeta]:
    full_count = len(points)
    if full_count <= SPARKLINE_LIMIT:
        return list(points), CurveMeta(full_count=full_count, downsampled=False, limit=SPARKLINE_LIMIT)
    ds = downsample_curve_points(points, limit=SPARKLINE_LIMIT)
    return ds, CurveMeta(full_count=full_count, downsampled=True, limit=SPARKLINE_LIMIT)


def _points_payload(points: list[dict], *, preview_limit: int = PREVIEW_POINT_LIMIT) -> dict:
    full_count = len(points)
    spark = downsample_curve_points(points, limit=RESPONSE_POINT_LIMIT)
    preview = points[:preview_limit]
    return {
        "points": preview,
        "point_count": full_count,
        "sparkline_points": spark,
        "sparkline_downsampled": len(spark) < full_count,
        "points_truncated": full_count > preview_limit,
    }


def _level_payload(level_data: dict[str, list[dict]]) -> dict[str, dict]:
    return {key: _points_payload(values) for key, values in level_data.items()}


def _serialize_cell_points(points: list[dict]) -> list[dict]:
    return [{k: v for k, v in point.items() if k != "skeleton_key"} for point in points]


def _trim_meta(meta: dict) -> dict:
    return {
        "vector": meta.get("vector"),
        "total_letter_mass": meta.get("total_letter_mass"),
        "token_count": meta.get("token_count"),
        "unique_words": meta.get("unique_words"),
        "top_words": (meta.get("top_words") or [])[:8],
        "vector_bits": meta.get("vector_bits"),
        "prime_factor_count": meta.get("prime_factor_count"),
        "document_profile": meta.get("document_profile"),
    }


def build_i_curve_result(doc_a: GpmDocument, doc_b: GpmDocument) -> tuple[dict, list[Step], CurveMeta | None]:
    _assert_icurve_dual_gateway(doc_a, doc_b)
    curve_a = extract_i_curve(doc_a)
    curve_b = extract_i_curve(doc_b)
    comparison = analyze_pair_full(doc_a, doc_b).get("comparison", {})

    ds_a, meta_a = downsample_curve(curve_a)
    ds_b, meta_b = downsample_curve(curve_b)
    downsampled = meta_a.downsampled or meta_b.downsampled
    meta = CurveMeta(
        full_count=max(meta_a.full_count, meta_b.full_count),
        downsampled=downsampled,
        limit=SPARKLINE_LIMIT,
    )

    result = {
        "curve_a": ds_a,
        "curve_b": ds_b,
        "comparison": comparison,
    }
    steps = [
        Step(
            id="extract_curves",
            title="I-Kurven extrahieren",
            detail="Token-I-Verhältnisse pro Position werden berechnet.",
            values={"points_a": meta_a.full_count, "points_b": meta_b.full_count},
        ),
        Step(
            id="compare_curves",
            title="Kurvenvergleich",
            detail="DTW und MAE-Metriken auf I-Kurven.",
            values={
                "geometry_score": comparison.get("geometry_score", 0.0),
                "literal_match": comparison.get("literal_match_ratio", 0.0),
            },
        ),
    ]
    if downsampled:
        steps.append(
            Step(
                id="downsample",
                title="Sparkline-Downsampling",
                detail=f"Kurven auf max. {SPARKLINE_LIMIT} Punkte reduziert (Invariante B).",
                values={"limit": SPARKLINE_LIMIT, "full_count": meta.full_count},
            )
        )
    return result, steps, meta


def build_full_pair_result(doc_a: GpmDocument, doc_b: GpmDocument) -> tuple[dict, list[Step], CurveMeta | None]:
    _assert_icurve_dual_gateway(doc_a, doc_b)
    assert_icurve_token_limit(doc_a, doc_b)
    full = analyze_pair_full(doc_a, doc_b)
    comparison = full.get("comparison") or {}

    curve_a = extract_i_curve(doc_a)
    curve_b = extract_i_curve(doc_b)
    substance_a = full.get("substance_a") or []
    substance_b = full.get("substance_b") or []
    cells_a = _serialize_cell_points(extract_cell_geometry(doc_a))
    cells_b = _serialize_cell_points(extract_cell_geometry(doc_b))

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

    cell_cmp = comparison.get("cell_geometry") or {}

    result = json_sanitize(
        {
            "curve_a": {**_points_payload(curve_a), "summary": summarize_curve(curve_a)},
            "curve_b": {**_points_payload(curve_b), "summary": summarize_curve(curve_b)},
            "substance_a": _points_payload(substance_a),
            "substance_b": _points_payload(substance_b),
            "cell_geometry_a": {
                **_points_payload(cells_a),
                "summary": summarize_curve(cells_a),
            },
            "cell_geometry_b": {
                **_points_payload(cells_b),
                "summary": summarize_curve(cells_b),
            },
            "cell_comparison": cell_cmp,
            "substance_comparison": comparison.get("substance_geometry"),
            "comparison": comparison,
            "meta_a": _trim_meta(full.get("meta_a") or {}),
            "meta_b": _trim_meta(full.get("meta_b") or {}),
            "meta_comparison": full.get("meta_comparison"),
            "relation_comparison": full.get("relation_comparison"),
            "structure_assessment": full.get("structure_assessment"),
            "validation_pipeline": full.get("validation_pipeline"),
            "semantic_a": _level_payload(semantic_a),
            "semantic_b": _level_payload(semantic_b),
            "structural_a": _level_payload(structural_a),
            "structural_b": _level_payload(structural_b),
            "hierarchy_comparison": full.get("hierarchy_comparison"),
            "cross_analysis_a": full.get("cross_analysis_a"),
            "cross_analysis_b": full.get("cross_analysis_b"),
            "viewport_a": serialize_viewport(doc_a),
            "viewport_b": serialize_viewport(doc_b),
            "genome_preview_a": build_genome_preview(doc_a),
            "genome_preview_b": build_genome_preview(doc_b),
            "geometry_preview_a": build_geometry_preview(doc_a),
            "geometry_preview_b": build_geometry_preview(doc_b),
            "geometry_score": full.get("geometry_score"),
            "summary_a": full.get("summary_a"),
            "summary_b": full.get("summary_b"),
            "i_curve": {
                "curve_a": downsample_curve_points(curve_a, RESPONSE_POINT_LIMIT),
                "curve_b": downsample_curve_points(curve_b, RESPONSE_POINT_LIMIT),
                "comparison": comparison,
            },
        }
    )

    _, steps, meta = build_i_curve_result(doc_a, doc_b)
    return result, steps, meta
