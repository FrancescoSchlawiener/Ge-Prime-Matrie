"""Token-I-Kurve, Zell-Geometrie und Kurvenvergleich."""

from __future__ import annotations

import math
import statistics
import unicodedata
from collections import Counter

from analysis.blocks.build import materialize_geometry
from analysis.case.apply import apply_case
from analysis.compile.reconstruct import reconstruct_text
from analysis.document.model import GpmDocument
from analysis.geom.config import DTW_SEQUENCE_LIMIT
from analysis.geom.dtw import dtw_result_payload, dtw_similarity
from analysis.algebra.i_metrics import i_ratio_similarity
from analysis.algebra.offset import classify_structural_offset, structural_twin_key
from analysis.algebra.fold import fold_lcm_span
from analysis.algebra.substance_kernel import (
    coupled_point_distance,
    empty_transition_fields,
    substance_ggt_kgv_similarity,
    substance_transition_fields,
)
from perm.multiset import perm_space

GEOMETRY_PARALLEL_THRESHOLD = 0.75
LITERAL_LOW_THRESHOLD = 0.6
STRUCTURAL_CELL_TWIN_THRESHOLD = 0.75
WORD_DTW_DIAGNOSTIC_THRESHOLD = 0.75
WORD_MAE_RIGID_THRESHOLD = 0.75
WORD_MAE_ELASTIC_THRESHOLD = 0.45
CELL_GEOMETRY_POINT_LIMIT = 50


def normalize_skeleton(frequencies) -> tuple[int, ...]:
    return tuple(int(x) for x in frequencies)


def skeleton_signature(cell: dict) -> tuple[tuple[int, ...], int, int]:
    raw = cell.get("skeleton") or cell.get("frequencies") or []
    return structural_twin_key(normalize_skeleton(raw), int(cell["perm_index"]), int(cell["perm_space"]))


def _i_ratio(perm_index: int, perm_space_val: int) -> float:
    if perm_space_val <= 1:
        return 1.0
    return perm_index / perm_space_val


def extract_i_curve(document: GpmDocument) -> list[dict]:
    materialize_geometry(document)
    points: list[dict] = []
    prev_ratio: float | None = None
    explicit_map = dict(document.explicit)

    for position, token in enumerate(document.tokens):
        entry = document.header[token.word_id]
        if position in explicit_map:
            word = explicit_map[position]
            normalized = word.upper()
        else:
            word = apply_case(entry.word_canonical, token.case_code)
            normalized = entry.word_normalized
        ps = perm_space(Counter(normalized))
        if ps <= 0:
            ps = max(1, entry.perm_index)
        ratio = _i_ratio(token.perm_index, ps)
        delta_ratio = 0.0 if prev_ratio is None else ratio - prev_ratio
        delta_index = 0 if not points else token.perm_index - points[-1]["perm_index"]

        points.append(
            {
                "position": position,
                "index": position,
                "word": word,
                "normalized": normalized,
                "substance": entry.substance,
                "perm_index": token.perm_index,
                "perm_space": ps,
                "i_ratio": round(ratio, 6),
                "delta_ratio": round(delta_ratio, 6),
                "delta_index": delta_index,
            }
        )
        prev_ratio = ratio
    return points


def extract_cell_curve(document: GpmDocument) -> list[dict]:
    return extract_cell_geometry(document)


def _cell_substance(document: GpmDocument, token_start: int, token_count: int) -> int:
    substances = [
        document.header[document.tokens[token_start + i].word_id].substance
        for i in range(token_count)
        if token_start + i < len(document.tokens)
    ]
    if not substances:
        return 1
    return fold_lcm_span(substances)


def _cell_label(document: GpmDocument, token_start: int, token_count: int) -> str:
    explicit_map = dict(document.explicit)
    words: list[str] = []
    for i in range(token_count):
        pos = token_start + i
        if pos >= len(document.tokens):
            break
        token = document.tokens[pos]
        entry = document.header[token.word_id]
        if pos in explicit_map:
            words.append(explicit_map[pos])
        else:
            words.append(apply_case(entry.word_canonical, token.case_code))
    return " ".join(words)


def extract_cell_geometry(document: GpmDocument) -> list[dict]:
    materialize_geometry(document)
    points: list[dict] = []
    prev_cell_substance: int | None = None

    for cell_index, cell in enumerate(document.cells):
        ratio = _i_ratio(cell.perm_index, cell.perm_space)
        sk = normalize_skeleton(cell.frequencies)
        cell_substance = _cell_substance(document, cell.token_start, cell.token_count)

        if prev_cell_substance is None:
            trans = empty_transition_fields()
            ggt = trans["ggt"]
            kgv = trans["kgv"]
            ggt_kgv_ratio = trans["ggt_kgv_ratio"]
        else:
            trans = substance_transition_fields(prev_cell_substance, cell_substance)
            ggt = trans["ggt"]
            kgv = trans["kgv"]
            ggt_kgv_ratio = trans["ggt_kgv_ratio"]

        sk_hash = hash(sk)
        points.append(
            {
                "cell_index": cell_index,
                "token_start": cell.token_start,
                "token_count": cell.token_count,
                "label": _cell_label(document, cell.token_start, cell.token_count),
                "category_count": len(cell.categories),
                "skeleton": list(sk),
                "skeleton_hash": sk_hash,
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


def _i_sim(a: dict, b: dict, *, ratio_key: str = "i_ratio") -> float:
    return i_ratio_similarity(a[ratio_key], b[ratio_key])


def _word_point_distance(a: dict, b: dict) -> float:
    i_sim = _i_sim(a, b)
    s_sim = substance_ggt_kgv_similarity(a.get("substance", 1), b.get("substance", 1))
    return coupled_point_distance(i_sim, s_sim)


def _cell_distance(a: dict, b: dict) -> float:
    i_sim = _i_sim(a, b, ratio_key="i_satz_ratio")
    twin = skeleton_signature(a) == skeleton_signature(b)
    if twin:
        s_sim = 1.0
    else:
        s_sim = substance_ggt_kgv_similarity(
            a.get("cell_substance", 1), b.get("cell_substance", 1)
        )
    return coupled_point_distance(i_sim, s_sim)


def compare_cell_geometry(cells_a: list[dict], cells_b: list[dict]) -> dict:
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
    if len(seq_a) > DTW_SEQUENCE_LIMIT or len(seq_b) > DTW_SEQUENCE_LIMIT:
        seq_a = _downsample_values(seq_a)
        seq_b = _downsample_values(seq_b)
    if len(seq_a) == len(seq_b):
        return _aligned_similarity(seq_a, seq_b), True, 0
    if len(seq_a) < len(seq_b):
        score, offset = _best_window_similarity(seq_a, seq_b)
    else:
        score, offset = _best_window_similarity(seq_b, seq_a)
    return score, False, offset


def _downsample_values(values: list[float], limit: int = DTW_SEQUENCE_LIMIT) -> list[float]:
    if len(values) <= limit:
        return values
    stride = max(1, len(values) // limit)
    out = [values[0]]
    for i in range(stride, len(values), stride):
        out.append(values[i])
    if out[-1] is not values[-1]:
        out.append(values[-1])
    return out


def _positional_literal_ratio(curve_a: list[dict], curve_b: list[dict]) -> float:
    if len(curve_a) != len(curve_b) or not curve_a:
        return 0.0
    matches = sum(1 for a, b in zip(curve_a, curve_b) if a["normalized"] == b["normalized"])
    return matches / len(curve_a)


def _token_window_literal_ratio(curve_a: list[dict], curve_b: list[dict]) -> tuple[float, int]:
    tokens_a = [p["normalized"] for p in curve_a if "normalized" in p]
    tokens_b = [p["normalized"] for p in curve_b if "normalized" in p]
    if not tokens_a or not tokens_b:
        return 0.0, 0
    if len(tokens_a) == len(tokens_b):
        return _positional_literal_ratio(curve_a, curve_b), 0
    if len(tokens_a) < len(tokens_b):
        short, long = tokens_a, tokens_b
    else:
        short, long = tokens_b, tokens_a
    best_score = 0.0
    best_offset = 0
    width = len(short)
    for offset in range(len(long) - width + 1):
        window = long[offset : offset + width]
        matches = sum(1 for a, b in zip(short, window) if a == b)
        score = matches / width
        if score > best_score:
            best_score = score
            best_offset = offset
    return best_score, best_offset


def _byte_frequency_similarity(text_a: str, text_b: str) -> tuple[float, int]:
    bytes_a = unicodedata.normalize("NFC", text_a).encode("utf-8")
    bytes_b = unicodedata.normalize("NFC", text_b).encode("utf-8")
    if not bytes_a and not bytes_b:
        return 1.0, 0
    if not bytes_a or not bytes_b:
        return 0.0, 0
    counter_a = Counter(bytes_a)
    counter_b = Counter(bytes_b)
    intersection = sum(min(counter_a[b], counter_b[b]) for b in set(counter_a) | set(counter_b))
    return intersection / max(len(bytes_a), len(bytes_b)), intersection


def _compute_literal_metrics(
    curve_a: list[dict],
    curve_b: list[dict],
    *,
    document_a: GpmDocument | None = None,
    document_b: GpmDocument | None = None,
) -> tuple[float, dict]:
    len_a = len(curve_a)
    len_b = len(curve_b)
    aligned = len_a == len_b

    positional_ratio = _positional_literal_ratio(curve_a, curve_b) if aligned else 0.0
    window_ratio, window_offset = _token_window_literal_ratio(curve_a, curve_b)

    byte_ratio = 0.0
    byte_intersection = 0
    byte_length_a = 0
    byte_length_b = 0
    if document_a is not None and document_b is not None:
        text_a = reconstruct_text(document_a)
        text_b = reconstruct_text(document_b)
        byte_ratio, byte_intersection = _byte_frequency_similarity(text_a, text_b)
        byte_length_a = len(unicodedata.normalize("NFC", text_a).encode("utf-8"))
        byte_length_b = len(unicodedata.normalize("NFC", text_b).encode("utf-8"))

    if aligned and len_a > 0:
        literal_match_ratio = positional_ratio
        primary_method = "positional"
    else:
        if window_ratio >= byte_ratio:
            literal_match_ratio = window_ratio
            primary_method = "window"
        else:
            literal_match_ratio = byte_ratio
            primary_method = "byte"

    diagnostics = {
        "positional_ratio": round(positional_ratio, 6),
        "window_ratio": round(window_ratio, 6),
        "window_offset": window_offset,
        "byte_ratio": round(byte_ratio, 6),
        "byte_intersection_total": byte_intersection,
        "byte_length_a": byte_length_a,
        "byte_length_b": byte_length_b,
        "primary_method": primary_method,
    }
    return literal_match_ratio, diagnostics


def compare_i_curves(
    curve_a: list[dict],
    curve_b: list[dict],
    *,
    substance_a: list[dict] | None = None,
    substance_b: list[dict] | None = None,
    document_a: GpmDocument | None = None,
    document_b: GpmDocument | None = None,
) -> dict:
    len_a = len(curve_a)
    len_b = len(curve_b)
    aligned = len_a == len_b

    literal_match_ratio, literal_diagnostics = _compute_literal_metrics(
        curve_a, curve_b, document_a=document_a, document_b=document_b
    )

    ratios_a = [p["i_ratio"] for p in curve_a]
    ratios_b = [p["i_ratio"] for p in curve_b]
    deltas_a = [p["delta_ratio"] for p in curve_a if p.get("position", 0) > 0]
    deltas_b = [p["delta_ratio"] for p in curve_b if p.get("position", 0) > 0]

    ratio_similarity, ratio_aligned, ratio_offset = _compare_sequences(ratios_a, ratios_b)
    delta_similarity, _, delta_offset = _compare_sequences(deltas_a, deltas_b)
    mae_score = (ratio_similarity + delta_similarity) / 2.0

    dtw = dtw_similarity(curve_a, curve_b, _word_point_distance)
    dtw_score = dtw.similarity
    dtw_payload = dtw_result_payload(dtw)

    geometry_score = dtw_score
    best_offset = ratio_offset if not ratio_aligned else delta_offset

    structural_waveform_parallel = (
        aligned
        and dtw_score >= GEOMETRY_PARALLEL_THRESHOLD
        and literal_match_ratio < LITERAL_LOW_THRESHOLD
    )

    if len_a == len_b == 0:
        interpretation = "Keine Token zum Vergleich."
    elif aligned and literal_match_ratio >= 0.999 and geometry_score >= 0.999:
        interpretation = "Identische Token-Folge und I-Kurven."
    elif structural_waveform_parallel:
        interpretation = "Strukturelle Wellenform-Parallelität bei divergentem Literal-Vektor."
    elif geometry_score >= 0.5:
        interpretation = "Partielle I-Kurven-Überlappung — moderate Geometrie-Ähnlichkeit."
    else:
        interpretation = "Unabhängige I-Kurven — Isomorphie-Index unter Schwellwert."

    offset_class = classify_structural_offset(
        mae_score,
        dtw_score,
        literal=literal_match_ratio,
    )

    return {
        "geometry_score": round(geometry_score, 6),
        "geometry_score_mae": round(mae_score, 6),
        "geometry_score_dtw": round(dtw_score, 6),
        "ratio_similarity": round(ratio_similarity, 6),
        "delta_similarity": round(delta_similarity, 6),
        "literal_match_ratio": round(literal_match_ratio, 6),
        "literal_diagnostics": literal_diagnostics,
        "aligned": aligned,
        "best_offset": best_offset,
        "length_a": len_a,
        "length_b": len_b,
        "structural_waveform_parallel": structural_waveform_parallel,
        "structural_offset_class": offset_class,
        "interpretation": interpretation,
        "dtw_cost": dtw_payload["dtw_cost"],
        "dtw_failed": dtw_payload["dtw_failed"],
        "dtw_window": dtw_payload["dtw_window"],
    }


def summarize_curve(points: list[dict]) -> dict:
    deltas = [p["delta_ratio"] for p in points if p.get("position", 0) > 0]
    return {
        "token_count": len(points),
        "mean_delta_ratio": round(statistics.mean(deltas), 6) if deltas else 0.0,
        "std_delta_ratio": round(statistics.pstdev(deltas), 6) if len(deltas) > 1 else 0.0,
    }
