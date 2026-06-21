"""Index-Vektoren (I-Kurve) — topologische Stil-Analyse aus GPM-Geometrie.

Pro Body-Token: i_ratio = I/N, delta_ratio zwischen aufeinanderfolgenden Token.
``analyze_pair`` kombiniert Kurvenvergleich mit Meta-Genom (Sprache, Domäne,
Plagiats-Heuristik). Token-Obergrenze pro Textseite: ``MAX_I_CURVE_TOKENS`` in ``ge_prime.config``.
"""

from __future__ import annotations

import math
import statistics

from ge_prime.config import MAX_I_CURVE_TOKENS, WINDOW_SEQUENCE_LIMIT
from ge_prime.compare import substance_ggt_kgv_similarity
from ge_prime.dtw import dtw_result_payload, dtw_similarity
from ge_prime.hierarchy import (
    compare_level_sequences,
    cross_analysis,
    extract_line_curve,
    extract_paragraph_curve,
    extract_phrase_curve,
    extract_sentence_curve,
    get_hierarchy,
    get_interval_index,
    serialize_viewport,
)
from ge_prime.relation_profile import serialize_relation_comparison_api
from ge_prime.meta_genome import enrich_pair_analysis
from ge_prime.substance_align import compare_substance_sequences, extract_substance_curve
from gpm.cell_geom import build_document_cells
from gpm.compiler import compile_text
from gpm.int_codec import perm_space_size
from gpm.model import GpmDocument
from pipeline.normalize import apply_case

RESPONSE_POINT_LIMIT = 500
CELL_GEOMETRY_POINT_LIMIT = 50
GEOMETRY_PARALLEL_THRESHOLD = 0.75
LITERAL_LOW_THRESHOLD = 0.6
STRUCTURAL_CELL_TWIN_THRESHOLD = 0.75
WORD_DTW_DIAGNOSTIC_THRESHOLD = 0.75
WORD_MAE_RIGID_THRESHOLD = 0.75
WORD_MAE_ELASTIC_THRESHOLD = 0.45


def normalize_skeleton(frequencies) -> tuple[int, ...]:
    """Kanonsiche Skelett-Form für vergleichbare Identität."""
    return tuple(int(x) for x in frequencies)


def skeleton_signature(cell: dict) -> tuple[tuple[int, ...], int, int]:
    """(norm_skeleton, perm_index, perm_space) — exakte Struktur-Zwillinge."""
    raw = cell.get("skeleton") or cell.get("frequencies") or []
    return (normalize_skeleton(raw), int(cell["perm_index"]), int(cell["perm_space"]))


def _i_sim(a: dict, b: dict, *, ratio_key: str = "i_ratio") -> float:
    return max(0.0, 1.0 - abs(a[ratio_key] - b[ratio_key]))


def _word_point_distance(a: dict, b: dict) -> float:
    """Gekoppelte Wort-DTW-Distanz: I_sim × S_sim."""
    i_sim = _i_sim(a, b)
    s_a = a.get("substance", 1)
    s_b = b.get("substance", 1)
    s_sim = substance_ggt_kgv_similarity(s_a, s_b)
    return 1.0 - i_sim * s_sim


def _cell_distance(a: dict, b: dict) -> float:
    """Hybrid Zell-DTW: I_Satz_sim × S_cell_sim; Skelett-Zwilling → S_sim=1."""
    i_sim = _i_sim(a, b, ratio_key="i_satz_ratio")
    twin = skeleton_signature(a) == skeleton_signature(b)
    if twin:
        s_sim = 1.0
    else:
        s_a = a.get("cell_substance", 1)
        s_b = b.get("cell_substance", 1)
        s_sim = substance_ggt_kgv_similarity(s_a, s_b)
    return 1.0 - i_sim * s_sim


def _i_ratio(perm_index: int, perm_space: int) -> float:
    if perm_space <= 1:
        return 1.0
    return perm_index / perm_space


def _cell_substance(document: GpmDocument, token_start: int, token_count: int) -> int:
    substances = [
        document.header[document.tokens[token_start + i].word_id].substance
        for i in range(token_count)
        if token_start + i < len(document.tokens)
    ]
    if not substances:
        return 1
    result = substances[0]
    for s in substances[1:]:
        result = math.lcm(result, s)
    return result


def extract_i_curve(document: GpmDocument) -> list[dict]:
    """I-Vektor: ein Punkt pro Body-Token."""
    explicit_map = dict(document.explicit)
    points: list[dict] = []
    prev_ratio: float | None = None

    for position, token in enumerate(document.tokens):
        if position in explicit_map:
            word = explicit_map[position]
            normalized = word.upper()
            perm_index = token.perm_index
            n = perm_space_size(normalized) if normalized else 1
            substance = document.header[token.word_id].substance if token.word_id < len(document.header) else 1
        else:
            entry = document.header[token.word_id]
            word = apply_case(entry.word_original, token.case_code)
            normalized = entry.word_normalized
            perm_index = token.perm_index
            n = perm_space_size(normalized)
            substance = entry.substance

        ratio = _i_ratio(perm_index, n)
        delta_ratio = 0.0 if prev_ratio is None else ratio - prev_ratio
        delta_index = 0 if not points else perm_index - points[-1]["perm_index"]

        points.append(
            {
                "position": position,
                "word": word,
                "normalized": normalized,
                "substance": substance,
                "perm_index": perm_index,
                "perm_space": n,
                "i_ratio": round(ratio, 6),
                "delta_ratio": round(delta_ratio, 6),
                "delta_index": delta_index,
            }
        )
        prev_ratio = ratio

    return points


def extract_i_curve_from_text(text: str) -> list[dict]:
    document, _, _ = compile_text(text)
    return extract_i_curve(document)


def extract_cell_geometry(document: GpmDocument) -> list[dict]:
    """Ein Punkt pro Zell-Geometrie (I_Satz / N_Satz) inkl. kgV pro Zelle."""
    cells = document.cells if document.cells else build_document_cells(document)
    points: list[dict] = []
    prev_cell_substance: int | None = None

    for cell_index, cell in enumerate(cells):
        ratio = _i_ratio(cell.perm_index, cell.perm_space)
        sk = normalize_skeleton(cell.frequencies)
        cell_substance = _cell_substance(document, cell.token_start, cell.token_count)

        if prev_cell_substance is None:
            ggt_kgv_ratio = 0.0
            ggt = 0
            kgv = 0
        else:
            ggt = math.gcd(prev_cell_substance, cell_substance)
            kgv = math.lcm(prev_cell_substance, cell_substance)
            ggt_kgv_ratio = round(substance_ggt_kgv_similarity(prev_cell_substance, cell_substance), 6)

        points.append(
            {
                "cell_index": cell_index,
                "token_start": cell.token_start,
                "token_count": cell.token_count,
                "category_count": len(cell.categories),
                "skeleton": list(sk),
                "skeleton_key": sk,
                "cell_substance": cell_substance,
                "ggt": ggt,
                "kgv": kgv,
                "ggt_kgv_ratio": ggt_kgv_ratio,
                "perm_index": cell.perm_index,
                "perm_space": cell.perm_space,
                "i_satz_ratio": round(ratio, 6),
            }
        )
        prev_cell_substance = cell_substance

    return points


def summarize_cell_geometry(cells: list[dict]) -> dict:
    ratios = [c["i_satz_ratio"] for c in cells]
    return {
        "cell_count": len(cells),
        "total_tokens": sum(c["token_count"] for c in cells),
        "mean_i_satz_ratio": round(statistics.mean(ratios), 6) if ratios else 0.0,
        "std_i_satz_ratio": round(statistics.pstdev(ratios), 6) if len(ratios) > 1 else 0.0,
    }


def cell_geometry_payload(document: GpmDocument, *, limit: int = CELL_GEOMETRY_POINT_LIMIT) -> dict:
    """API-Payload für Zell-Geometrie (Editor / Analyse)."""
    points = extract_cell_geometry(document)
    summary = summarize_cell_geometry(points)
    truncated = len(points) > limit
    serializable = []
    for p in points[:limit]:
        row = dict(p)
        row.pop("skeleton_key", None)
        serializable.append(row)
    return {
        "count": len(points),
        "points": serializable,
        "truncated": truncated,
        "summary": summary,
    }


def compare_cell_geometry(cells_a: list[dict], cells_b: list[dict]) -> dict:
    """Vergleicht Zell-Ketten via DTW (Segmentierung verschiebt Grenzen)."""
    if not cells_a or not cells_b:
        return {
            "match_count": 0,
            "aligned": False,
            "geometry_score": 0.0,
            "dtw_cost": None,
            "dtw_failed": True,
            "dtw_window": 0,
            "method": "dtw",
            "length_a": len(cells_a),
            "length_b": len(cells_b),
        }

    aligned = len(cells_a) == len(cells_b)
    matches = 0
    if aligned:
        for a, b in zip(cells_a, cells_b):
            if skeleton_signature(a) == skeleton_signature(b):
                matches += 1

    dtw = dtw_similarity(cells_a, cells_b, _cell_distance)
    payload = dtw_result_payload(dtw)
    return {
        "match_count": matches,
        "aligned": aligned,
        "method": "dtw",
        "length_a": len(cells_a),
        "length_b": len(cells_b),
        **payload,
    }


def summarize_curve(points: list[dict]) -> dict:
    deltas = [p["delta_ratio"] for p in points if p["position"] > 0]
    return {
        "token_count": len(points),
        "mean_delta_ratio": round(statistics.mean(deltas), 6) if deltas else 0.0,
        "std_delta_ratio": round(statistics.pstdev(deltas), 6) if len(deltas) > 1 else 0.0,
    }


def _downsample_values(values: list[float], limit: int = WINDOW_SEQUENCE_LIMIT) -> list[float]:
    if len(values) <= limit:
        return values
    stride = max(1, len(values) // limit)
    out = [values[0]]
    for i in range(stride, len(values), stride):
        out.append(values[i])
    if out[-1] is not values[-1]:
        out.append(values[-1])
    return out


def _downsample_curve_dicts(points: list[dict], limit: int = WINDOW_SEQUENCE_LIMIT) -> list[dict]:
    if len(points) <= limit:
        return points
    stride = max(1, len(points) // limit)
    out = [points[0]]
    for i in range(stride, len(points), stride):
        out.append(points[i])
    if out[-1] is not points[-1]:
        out.append(points[-1])
    return out


def _prepare_document_for_analysis(document: GpmDocument) -> None:
    """Hierarchie, Interval-Index und Zellen einmalig materialisieren (nicht pro Kurve neu)."""
    if not document.cells:
        document.cells = build_document_cells(document)
    get_hierarchy(document)
    get_interval_index(document)


def _aligned_similarity(seq_a: list[float], seq_b: list[float]) -> float:
    if not seq_a or len(seq_a) != len(seq_b):
        return 0.0
    mean_diff = sum(abs(a - b) for a, b in zip(seq_a, seq_b)) / len(seq_a)
    return max(0.0, 1.0 - mean_diff)


def _best_window_similarity(short: list[float], long: list[float]) -> tuple[float, int]:
    if not short or not long or len(short) > len(long):
        return 0.0, 0
    if len(short) == len(long):
        return _aligned_similarity(short, long), 0

    best_score = 0.0
    best_offset = 0
    width = len(short)
    for offset in range(len(long) - width + 1):
        window = long[offset : offset + width]
        score = _aligned_similarity(short, window)
        if score > best_score:
            best_score = score
            best_offset = offset
    return best_score, best_offset


def _compare_sequences(seq_a: list[float], seq_b: list[float]) -> tuple[float, bool, int]:
    if len(seq_a) > WINDOW_SEQUENCE_LIMIT or len(seq_b) > WINDOW_SEQUENCE_LIMIT:
        seq_a = _downsample_values(seq_a)
        seq_b = _downsample_values(seq_b)
    if len(seq_a) == len(seq_b):
        return _aligned_similarity(seq_a, seq_b), True, 0
    if len(seq_a) < len(seq_b):
        score, offset = _best_window_similarity(seq_a, seq_b)
    else:
        score, offset = _best_window_similarity(seq_b, seq_a)
    return score, False, offset


def _substance_weighted_window_similarity(
    short: list[dict],
    long: list[dict],
    *,
    substance_short: list[dict],
    substance_long: list[dict],
) -> tuple[float, int]:
    if not short or not long or len(short) > len(long):
        return 0.0, 0
    if len(short) > WINDOW_SEQUENCE_LIMIT or len(long) > WINDOW_SEQUENCE_LIMIT:
        short = _downsample_curve_dicts(short)
        long = _downsample_curve_dicts(long)
        substance_short = _downsample_curve_dicts(substance_short)
        substance_long = _downsample_curve_dicts(substance_long)
    if len(short) == len(long):
        return _aligned_similarity([p["i_ratio"] for p in short], [p["i_ratio"] for p in long]), 0

    best_score = 0.0
    best_offset = 0
    width = len(short)
    for offset in range(len(long) - width + 1):
        window = long[offset : offset + width]
        sub_window = substance_long[offset : offset + width]
        base = _aligned_similarity(
            [p["i_ratio"] for p in short],
            [p["i_ratio"] for p in window],
        )
        if len(sub_window) == width and len(substance_short) == width:
            s_weights = [
                substance_ggt_kgv_similarity(a["substance"], b["substance"])
                for a, b in zip(substance_short, sub_window)
            ]
            s_boost = sum(s_weights) / len(s_weights)
            score = min(1.0, base * 0.7 + s_boost * 0.3)
        else:
            score = base
        if score > best_score:
            best_score = score
            best_offset = offset
    return best_score, best_offset


def compare_i_curves(
    curve_a: list[dict],
    curve_b: list[dict],
    *,
    substance_a: list[dict] | None = None,
    substance_b: list[dict] | None = None,
) -> dict:
    """Vergleicht zwei I-Kurven inkl. Literal-Match, Hybrid-Geometrie und Plagiats-Heuristik."""
    len_a = len(curve_a)
    len_b = len(curve_b)
    aligned = len_a == len_b
    substance_a = substance_a or []
    substance_b = substance_b or []

    if aligned and len_a > 0:
        literal_matches = sum(
            1 for a, b in zip(curve_a, curve_b) if a["normalized"] == b["normalized"]
        )
        literal_match_ratio = literal_matches / len_a
    else:
        literal_match_ratio = 0.0

    ratios_a = [p["i_ratio"] for p in curve_a]
    ratios_b = [p["i_ratio"] for p in curve_b]
    deltas_a = [p["delta_ratio"] for p in curve_a if p["position"] > 0]
    deltas_b = [p["delta_ratio"] for p in curve_b if p["position"] > 0]

    ratio_similarity, ratio_aligned, ratio_offset = _compare_sequences(ratios_a, ratios_b)
    delta_similarity, _, delta_offset = _compare_sequences(deltas_a, deltas_b)
    mae_score = (ratio_similarity + delta_similarity) / 2.0

    dtw = dtw_similarity(curve_a, curve_b, _word_point_distance)
    dtw_score = dtw.similarity
    dtw_payload = dtw_result_payload(dtw)

    if not ratio_aligned and substance_a and substance_b:
        if len_a <= len_b:
            sw_score, sw_offset = _substance_weighted_window_similarity(
                curve_a, curve_b, substance_short=substance_a, substance_long=substance_b
            )
        else:
            sw_score, sw_offset = _substance_weighted_window_similarity(
                curve_b, curve_a, substance_short=substance_b, substance_long=substance_a
            )
        ratio_similarity = max(ratio_similarity, sw_score)
        mae_score = (ratio_similarity + delta_similarity) / 2.0
        ratio_offset = sw_offset

    geometry_score = dtw_score
    best_offset = ratio_offset if not ratio_aligned else delta_offset

    fester_offset_erkannt = (
        aligned
        and mae_score >= WORD_MAE_RIGID_THRESHOLD
        and dtw_score >= WORD_DTW_DIAGNOSTIC_THRESHOLD
    )
    elastische_streckung = (
        dtw_score >= WORD_DTW_DIAGNOSTIC_THRESHOLD
        and mae_score < WORD_MAE_ELASTIC_THRESHOLD
    )
    hybride_modifikation = (
        dtw_score >= WORD_DTW_DIAGNOSTIC_THRESHOLD
        and WORD_MAE_ELASTIC_THRESHOLD <= mae_score < WORD_MAE_RIGID_THRESHOLD
    )

    suspicious_parallel = (
        aligned
        and dtw_score >= GEOMETRY_PARALLEL_THRESHOLD
        and literal_match_ratio < LITERAL_LOW_THRESHOLD
    )

    if len_a == len_b == 0:
        interpretation = "Keine Token zum Vergleich."
    elif aligned and literal_match_ratio >= 0.999 and geometry_score >= 0.999:
        interpretation = "Identische Token-Folge und I-Kurven."
    elif suspicious_parallel:
        interpretation = (
            "Strukturell verdächtig parallel: ähnliche I-Kurven bei unterschiedlichen Wörtern."
        )
    elif geometry_score >= 0.5:
        interpretation = "Teilweise ähnliche Satzgeometrie — weiter prüfen."
    else:
        interpretation = "Unabhängige I-Kurven — keine auffällige Parallelität."

    return {
        "geometry_score": round(geometry_score, 6),
        "geometry_score_mae": round(mae_score, 6),
        "geometry_score_dtw": round(dtw_score, 6),
        "ratio_similarity": round(ratio_similarity, 6),
        "delta_similarity": round(delta_similarity, 6),
        "literal_match_ratio": round(literal_match_ratio, 6),
        "aligned": aligned,
        "best_offset": best_offset,
        "length_a": len_a,
        "length_b": len_b,
        "suspicious_parallel": suspicious_parallel,
        "fester_offset_erkannt": fester_offset_erkannt,
        "elastische_streckung": elastische_streckung,
        "hybride_modifikation": hybride_modifikation,
        "interpretation": interpretation,
        "dtw_cost": dtw_payload["dtw_cost"],
        "dtw_failed": dtw_payload["dtw_failed"],
        "dtw_window": dtw_payload["dtw_window"],
        "word_geometry": {
            "method": "dtw_primary",
            "mae_score": round(mae_score, 6),
            "dtw_score": round(dtw_score, 6),
            "fester_offset_erkannt": fester_offset_erkannt,
            "elastische_streckung": elastische_streckung,
            "hybride_modifikation": hybride_modifikation,
            "dtw_cost": dtw_payload["dtw_cost"],
            "dtw_failed": dtw_payload["dtw_failed"],
            "dtw_window": dtw_payload["dtw_window"],
        },
    }


def _document_from_side(*, text: str | None, document: GpmDocument | None) -> GpmDocument:
    if document is not None:
        return document
    if text is None or not text.strip():
        raise ValueError("Text oder .gpm-Datei erforderlich.")
    doc, _, _ = compile_text(text)
    return doc


def analyze_pair(
    *,
    doc_a: GpmDocument | None = None,
    text_a: str | None = None,
    doc_b: GpmDocument | None = None,
    text_b: str | None = None,
    repo=None,
    db_audit_mode: str = "de_en",
) -> dict:
    """Lädt beide Seiten, extrahiert Kurven und vergleicht."""
    document_a = _document_from_side(text=text_a, document=doc_a)
    document_b = _document_from_side(text=text_b, document=doc_b)

    if len(document_a.tokens) > MAX_I_CURVE_TOKENS:
        raise ValueError(f"Seite A: maximal {MAX_I_CURVE_TOKENS:,} Token.")
    if len(document_b.tokens) > MAX_I_CURVE_TOKENS:
        raise ValueError(f"Seite B: maximal {MAX_I_CURVE_TOKENS:,} Token.")

    _prepare_document_for_analysis(document_a)
    _prepare_document_for_analysis(document_b)

    curve_a = extract_i_curve(document_a)
    curve_b = extract_i_curve(document_b)
    substance_a = extract_substance_curve(document_a)
    substance_b = extract_substance_curve(document_b)
    cells_a = extract_cell_geometry(document_a)
    cells_b = extract_cell_geometry(document_b)
    comparison = compare_i_curves(
        curve_a,
        curve_b,
        substance_a=substance_a,
        substance_b=substance_b,
    )
    cell_comparison = compare_cell_geometry(cells_a, cells_b)
    substance_comparison = compare_substance_sequences(
        substance_a,
        substance_b,
        literal_match_ratio=comparison["literal_match_ratio"],
    )
    comparison["cell_geometry"] = cell_comparison
    comparison["substance_geometry"] = substance_comparison
    comparison["substance_parallel"] = substance_comparison.get("substance_parallel", False)
    structural_cell_twins = (
        cell_comparison["geometry_score"] >= STRUCTURAL_CELL_TWIN_THRESHOLD
        and comparison["literal_match_ratio"] < LITERAL_LOW_THRESHOLD
    )
    comparison["structural_cell_twins"] = structural_cell_twins
    if structural_cell_twins and not comparison.get("suspicious_parallel"):
        comparison["interpretation"] = (
            "Strukturelle Zell-Zwillinge: gleicher Satzbau (Skelett + I_Satz), "
            "andere Wörter — typisch für Synonym-Ersatz oder strukturelle Kopie."
        )
    elif structural_cell_twins:
        comparison["interpretation"] = (
            "Strukturelle Zell-Zwillinge und parallele Wort-I-Kurven — "
            "starke Übereinstimmung in Satzbau-Schablone."
        )

    meta = enrich_pair_analysis(
        document_a,
        document_b,
        comparison,
        repo,
        db_audit_mode=db_audit_mode,
    )

    comparison["identical_text"] = (
        comparison["aligned"]
        and comparison.get("literal_match_ratio", 0.0) >= 0.999
    )

    semantic_a = {
        "paragraphs": extract_paragraph_curve(document_a),
        "sentences": extract_sentence_curve(document_a),
        "phrases": extract_phrase_curve(document_a),
    }
    semantic_b = {
        "paragraphs": extract_paragraph_curve(document_b),
        "sentences": extract_sentence_curve(document_b),
        "phrases": extract_phrase_curve(document_b),
    }
    structural_a = {
        "lines": extract_line_curve(document_a),
    }
    structural_b = {
        "lines": extract_line_curve(document_b),
    }
    hierarchy_comparison = {
        "semantic": {
            "phrase": compare_level_sequences(
                semantic_a["phrases"],
                semantic_b["phrases"],
                ratio_key="i_phrase_ratio",
            ),
            "sentence": compare_level_sequences(
                semantic_a["sentences"],
                semantic_b["sentences"],
                ratio_key="i_satz_ratio",
            ),
            "paragraph": compare_level_sequences(
                semantic_a["paragraphs"],
                semantic_b["paragraphs"],
                ratio_key="i_absatz_ratio",
            ),
        },
        "structural": {
            "line": compare_level_sequences(
                structural_a["lines"],
                structural_b["lines"],
                ratio_key="i_zeile_ratio",
            ),
        },
    }
    cross_a = cross_analysis(document_a)
    cross_b = cross_analysis(document_b)

    return {
        "curve_a": curve_a,
        "curve_b": curve_b,
        "substance_a": substance_a,
        "substance_b": substance_b,
        "cell_geometry_a": cells_a,
        "cell_geometry_b": cells_b,
        "cell_summary_a": summarize_cell_geometry(cells_a),
        "cell_summary_b": summarize_cell_geometry(cells_b),
        "summary_a": summarize_curve(curve_a),
        "summary_b": summarize_curve(curve_b),
        "comparison": comparison,
        "meta_a": meta["meta_a"],
        "meta_b": meta["meta_b"],
        "meta_comparison": meta["meta_comparison"],
        "relation_comparison": serialize_relation_comparison_api(
            meta["relation_comparison"],
            document_a,
            document_b,
        ),
        "plagiarism_assessment": meta["plagiarism_assessment"],
        "semantic_a": semantic_a,
        "semantic_b": semantic_b,
        "structural_a": structural_a,
        "structural_b": structural_b,
        "hierarchy_comparison": hierarchy_comparison,
        "cross_analysis_a": cross_a,
        "cross_analysis_b": cross_b,
        "viewport_a": serialize_viewport(document_a),
        "viewport_b": serialize_viewport(document_b),
    }


def downsample_curve_points(points: list[dict], limit: int = RESPONSE_POINT_LIMIT) -> list[dict]:
    from ge_prime.sparkline import downsample_curve_points as _downsample

    return _downsample(points, limit)
