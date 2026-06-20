"""POST /api/i-curve — Index-Vektoren und Meta-Genom-Vergleich."""

from __future__ import annotations

import base64

from flask import Flask, jsonify, request
from werkzeug.datastructures import FileStorage

from ge_prime.config import API_PREVIEW_POINT_LIMIT
from ge_prime.payload_codec import compress_rhythm_breaks
from ge_prime.i_curve import (
    RESPONSE_POINT_LIMIT,
    analyze_pair,
)
from ge_prime.sparkline import build_preview_points, downsample_curve_points
from gpm.cipher_wrap import is_encrypted_gpm_blob
from gpm.format import GpmFormatError, read_gpm
from pipeline.normalize import INDEX_HELP, normalize_text_nfc
from web.handlers.gpm import MAX_GPM_UPLOAD_BYTES


def _icurve_request_data():
    content_type = request.content_type or ""
    if "multipart/form-data" in content_type:
        return request.form.to_dict(), request.files
    return request.get_json(silent=True) or {}, None


def _icurve_load_side(
    data: dict,
    side: str,
    *,
    files: dict[str, FileStorage] | None = None,
) -> tuple:
    prefix = side.lower()
    source = (data.get(f"source_{prefix}") or "text").strip().lower()
    if source == "gpm":
        file_key = f"file_{prefix}"
        upload = files.get(file_key) if files else None
        if upload and upload.filename:
            blob = upload.read()
        else:
            raw = (data.get(f"file_{prefix}_base64") or "").strip()
            if not raw:
                raise ValueError(f"Seite {side.upper()}: .gpm-Datei erforderlich.")
            blob = base64.b64decode(raw)
        if len(blob) > MAX_GPM_UPLOAD_BYTES:
            raise ValueError("Datei zu groß (max. 50 MB).")
        if is_encrypted_gpm_blob(blob):
            raise ValueError(
                "Verschlüsselte .gpm — zuerst im Tab GPM Datei mit Schlüssel lesen, "
                "danach Freitext für I-Kurve nutzen."
            )
        return read_gpm(blob), None
    text = normalize_text_nfc((data.get(f"text_{prefix}") or "").strip())
    if not text:
        raise ValueError(f"Seite {side.upper()}: Text erforderlich.")
    return None, text


def _serialize_cell_points(points: list[dict]) -> list[dict]:
    return [{k: v for k, v in point.items() if k != "skeleton_key"} for point in points]


def _points_payload(
    points: list[dict],
    *,
    preview_limit: int = API_PREVIEW_POINT_LIMIT,
) -> dict:
    full_count = len(points)
    spark = downsample_curve_points(points, limit=RESPONSE_POINT_LIMIT)
    preview, truncated = build_preview_points(points, preview_limit=preview_limit)
    return {
        "points": preview,
        "point_count": full_count,
        "sparkline_points": spark,
        "sparkline_downsampled": len(spark) < full_count,
        "points_truncated": truncated,
    }


def _level_payload(level_data: dict[str, list[dict]]) -> dict[str, dict]:
    return {key: _points_payload(values) for key, values in level_data.items()}


def _icurve_notes(comparison: dict, plagiarism: dict | None = None) -> list[str]:
    notes = [
        INDEX_HELP["limit_note"],
        INDEX_HELP["source_note"],
        INDEX_HELP["meta_genome"],
        INDEX_HELP["meta_language"],
    ]
    if plagiarism and plagiarism.get("highlight"):
        notes.append(INDEX_HELP["meta_plagiarism"])
    elif plagiarism and plagiarism.get("substance_parallel"):
        notes.append(INDEX_HELP["substance_align"])
    elif plagiarism and plagiarism.get("relation_twins"):
        notes.append(INDEX_HELP["relation_domain"])
    elif comparison.get("structural_cell_twins"):
        notes.append(INDEX_HELP["cell_twins"])
    elif comparison.get("suspicious_parallel"):
        notes.append(INDEX_HELP["plagiarism"])
        notes.append(INDEX_HELP["example"])
    elif comparison.get("geometry_score", 0) >= 0.99 and comparison.get("literal_match_ratio", 0) >= 0.99:
        notes.append("Beide Texte liefern nahezu identische I-Kurven und Token-Folge.")
    if plagiarism and plagiarism.get("signals"):
        notes.append(
            f"Meta-Genom: {plagiarism.get('domain_a')} / {plagiarism.get('domain_b')} — "
            f"ggT-Ähnlichkeit {plagiarism.get('meta_genome_similarity', 0):.3f}."
        )
    return notes


def register(app: Flask, repo) -> None:
    @app.route("/api/i-curve", methods=["POST"])
    def api_i_curve():
        data, files = _icurve_request_data()
        try:
            doc_a, text_a = _icurve_load_side(data, "a", files=files)
            doc_b, text_b = _icurve_load_side(data, "b", files=files)
            db_audit_mode = (data.get("db_audit_mode") or "de_en").strip().lower()
            if db_audit_mode not in ("off", "de_en", "all_db"):
                raise ValueError("db_audit_mode muss off, de_en oder all_db sein.")
            result = analyze_pair(
                doc_a=doc_a,
                text_a=text_a,
                doc_b=doc_b,
                text_b=text_b,
                repo=repo,
                db_audit_mode=db_audit_mode,
            )
            comparison = result["comparison"]
            cell_cmp = comparison.get("cell_geometry") or {}
            comparison["notes"] = _icurve_notes(comparison, result.get("plagiarism_assessment"))
            cells_a = _serialize_cell_points(result["cell_geometry_a"])
            cells_b = _serialize_cell_points(result["cell_geometry_b"])
            cell_payload_a = _points_payload(cells_a)
            cell_payload_b = _points_payload(cells_b)
            cross_a = result.get("cross_analysis_a")
            cross_b = result.get("cross_analysis_b")
            if cross_a:
                cross_a = {
                    **cross_a,
                    "rhythm_breaks": compress_rhythm_breaks(cross_a.get("rhythm_breaks") or []),
                }
            if cross_b:
                cross_b = {
                    **cross_b,
                    "rhythm_breaks": compress_rhythm_breaks(cross_b.get("rhythm_breaks") or []),
                }
            return jsonify(
                {
                    "curve_a": {
                        **_points_payload(result["curve_a"]),
                        "summary": result["summary_a"],
                    },
                    "curve_b": {
                        **_points_payload(result["curve_b"]),
                        "summary": result["summary_b"],
                    },
                    "substance_a": _points_payload(result["substance_a"]),
                    "substance_b": _points_payload(result["substance_b"]),
                    "cell_geometry_a": {
                        **cell_payload_a,
                        "summary": result["cell_summary_a"],
                    },
                    "cell_geometry_b": {
                        **cell_payload_b,
                        "summary": result["cell_summary_b"],
                    },
                    "cell_comparison": cell_cmp,
                    "substance_comparison": comparison.get("substance_geometry"),
                    "comparison": comparison,
                    "meta_a": {
                        "language": result["meta_a"]["language"],
                        "domain": result["meta_a"]["domain"],
                        "token_count": result["meta_a"]["token_count"],
                        "unique_words": result["meta_a"]["unique_words"],
                        "top_words": result["meta_a"]["top_words"][:8],
                        "vector_bits": result["meta_a"]["vector_bits"],
                        "prime_factor_count": result["meta_a"]["prime_factor_count"],
                        "relation_profile": result["meta_a"].get("relation_profile"),
                    },
                    "meta_b": {
                        "language": result["meta_b"]["language"],
                        "domain": result["meta_b"]["domain"],
                        "token_count": result["meta_b"]["token_count"],
                        "unique_words": result["meta_b"]["unique_words"],
                        "top_words": result["meta_b"]["top_words"][:8],
                        "vector_bits": result["meta_b"]["vector_bits"],
                        "prime_factor_count": result["meta_b"]["prime_factor_count"],
                        "relation_profile": result["meta_b"].get("relation_profile"),
                    },
                    "meta_comparison": result["meta_comparison"],
                    "relation_comparison": result["relation_comparison"],
                    "plagiarism_assessment": result["plagiarism_assessment"],
                    "semantic_a": _level_payload(result.get("semantic_a", {})),
                    "semantic_b": _level_payload(result.get("semantic_b", {})),
                    "structural_a": _level_payload(result.get("structural_a", {})),
                    "structural_b": _level_payload(result.get("structural_b", {})),
                    "hierarchy_comparison": result.get("hierarchy_comparison"),
                    "cross_analysis_a": cross_a,
                    "cross_analysis_b": cross_b,
                    "viewport_a": result.get("viewport_a"),
                    "viewport_b": result.get("viewport_b"),
                }
            )
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except GpmFormatError as exc:
            return jsonify({"error": str(exc)}), 400
