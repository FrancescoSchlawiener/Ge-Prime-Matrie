"""Hierarchie-Analyse — Kurven, DTW, Enjambement über orthogonale Layer."""

from __future__ import annotations

import math
import statistics

from ge_prime.compare import substance_ggt_kgv_similarity
from ge_prime.dtw import dtw_result_payload, dtw_similarity
from gpm.hierarchy_geom import (
    DocumentHierarchy,
    HierarchyNode,
    TokenSpan,
    build_document_hierarchy,
    intervals_overlap,
    validate_structural_partition,
)
from gpm.interval_index import build_interval_index, nodes_intersecting_indexed
from gpm.model import GpmDocument

STRUCTURAL_TWIN_THRESHOLD = 0.75


def _transition_fields(prev_s: int, curr_s: int) -> dict:
    if prev_s <= 0 or curr_s <= 0:
        return {"ggt": 0, "kgv": 0, "ggt_kgv_ratio": 0.0}
    ggt = math.gcd(prev_s, curr_s)
    kgv = math.lcm(prev_s, curr_s)
    ratio = round(substance_ggt_kgv_similarity(prev_s, curr_s), 6)
    return {"ggt": ggt, "kgv": kgv, "ggt_kgv_ratio": ratio}


def _curve_from_nodes(
    nodes: list[HierarchyNode],
    *,
    ratio_key: str,
    index_key: str,
) -> list[dict]:
    points: list[dict] = []
    prev_s: int | None = None
    for node in nodes:
        ratio = node.perm_index / node.perm_space if node.perm_space > 1 else 1.0
        trans = _transition_fields(prev_s or 0, node.s_level) if prev_s is not None else {
            "ggt": 0,
            "kgv": 0,
            "ggt_kgv_ratio": 0.0,
        }
        if prev_s is None:
            trans = {"ggt": 0, "kgv": 0, "ggt_kgv_ratio": 0.0}
        points.append(
            {
                index_key: len(points),
                "token_start": node.token_start,
                "token_count": node.token_count,
                "s_level": node.s_level,
                ratio_key: round(ratio, 6),
                "perm_index": node.perm_index,
                "perm_space": node.perm_space,
                "skeleton": list(node.skeleton or node.frequencies),
                **trans,
            }
        )
        prev_s = node.s_level
    return points


def get_hierarchy(document: GpmDocument) -> DocumentHierarchy:
    hierarchy = getattr(document, "hierarchy", None)
    if hierarchy is not None:
        return hierarchy
    hierarchy = build_document_hierarchy(document)
    document.hierarchy = hierarchy
    return hierarchy


def get_interval_index(document: GpmDocument):
    idx = getattr(document, "interval_index", None)
    if idx is not None:
        return idx
    h = get_hierarchy(document)
    idx = build_interval_index(h, len(document.tokens))
    document.interval_index = idx
    return idx


def extract_phrase_curve(document: GpmDocument) -> list[dict]:
    h = get_hierarchy(document)
    return _curve_from_nodes(h.semantic.phrases, ratio_key="i_phrase_ratio", index_key="phrase_index")


def extract_sentence_curve(document: GpmDocument) -> list[dict]:
    h = get_hierarchy(document)
    return _curve_from_nodes(h.semantic.sentences, ratio_key="i_satz_ratio", index_key="sentence_index")


def extract_paragraph_curve(document: GpmDocument) -> list[dict]:
    h = get_hierarchy(document)
    return _curve_from_nodes(h.semantic.paragraphs, ratio_key="i_absatz_ratio", index_key="paragraph_index")


def extract_line_curve(document: GpmDocument) -> list[dict]:
    h = get_hierarchy(document)
    return _curve_from_nodes(h.structural.lines, ratio_key="i_zeile_ratio", index_key="line_index")


def extract_page_curve(document: GpmDocument) -> list[dict]:
    """Export/PDF-Hilfe — nicht Teil von analyze_pair oder Standard-Hierarchie."""
    from gpm.hierarchy_geom import build_page_nodes_for_export

    return _curve_from_nodes(
        build_page_nodes_for_export(document),
        ratio_key="i_page_ratio",
        index_key="page_index",
    )


def _node_distance(a: dict, b: dict, *, ratio_key: str) -> float:
    i_sim = max(0.0, 1.0 - abs(a[ratio_key] - b[ratio_key]))
    s_sim = substance_ggt_kgv_similarity(a.get("s_level", 1), b.get("s_level", 1))
    return 1.0 - i_sim * s_sim


def compare_level_sequences(seq_a: list[dict], seq_b: list[dict], *, ratio_key: str) -> dict:
    if not seq_a or not seq_b:
        return {
            "geometry_score": 0.0,
            "dtw_cost": None,
            "dtw_failed": True,
            "dtw_window": 0,
            "method": "dtw",
            "length_a": len(seq_a),
            "length_b": len(seq_b),
        }

    def dist(a, b):
        return _node_distance(a, b, ratio_key=ratio_key)

    dtw = dtw_similarity(seq_a, seq_b, dist)
    payload = dtw_result_payload(dtw)
    return {
        "method": "dtw",
        "length_a": len(seq_a),
        "length_b": len(seq_b),
        **payload,
    }


def detect_enjambement(
    sentences: list[HierarchyNode],
    lines: list[HierarchyNode],
    *,
    interval_index=None,
) -> dict:
    rhythm_breaks: list[dict] = []
    line_aligned = 0
    intersections = 0
    for sentence in sentences:
        if interval_index is not None:
            hit_lines = interval_index.query(
                "line",
                TokenSpan(sentence.token_start, sentence.token_count),
            )
        else:
            hit_lines = [
                line
                for line in lines
                if intervals_overlap(
                    sentence.token_start,
                    sentence.token_count,
                    line.token_start,
                    line.token_count,
                )
            ]
        for line in hit_lines:
            intersections += 1
            s_end = sentence.token_start + sentence.token_count
            l_end = line.token_start + line.token_count
            inter_start = max(sentence.token_start, line.token_start)
            inter_end = min(s_end, l_end)
            aligned_start = sentence.token_start == line.token_start
            aligned_end = s_end == l_end
            if aligned_start and aligned_end and sentence.token_count == line.token_count:
                line_aligned += 1
            elif not (aligned_start and aligned_end):
                rhythm_breaks.append(
                    {
                        "sentence_start": sentence.token_start,
                        "sentence_count": sentence.token_count,
                        "line_start": line.token_start,
                        "line_count": line.token_count,
                        "inter_start": inter_start,
                        "inter_end": inter_end,
                    }
                )
    total_sentences = len(sentences) or 1
    break_ratio = len(rhythm_breaks) / max(1, intersections)
    if break_ratio < 0.05 and line_aligned > total_sentences * 0.8:
        profile = "line_aligned"
    elif break_ratio > 0.35:
        profile = "enjambement_noise"
    elif rhythm_breaks:
        profile = "rhythm_break"
    else:
        profile = "prose_flow"
    return {
        "enjambement_profile": profile,
        "rhythm_break_count": len(rhythm_breaks),
        "line_aligned_count": line_aligned,
        "line_aligned_ratio": round(line_aligned / total_sentences, 6),
        "intersection_count": intersections,
        "rhythm_breaks": rhythm_breaks[:20],
    }


def cross_analysis(document: GpmDocument) -> dict:
    h = get_hierarchy(document)
    validate_structural_partition(len(document.tokens), h.structural.lines)
    idx = get_interval_index(document)
    enj = detect_enjambement(h.semantic.sentences, h.structural.lines, interval_index=idx)
    return enj


def token_char_map(document: GpmDocument) -> list[tuple[int, int, int]]:
    """Pro Token: (token_index, char_start, char_end) im rekonstruierten Text."""
    from gpm.reader import reconstruct_text

    text = reconstruct_text(document)
    mapping: list[tuple[int, int, int]] = []
    pos = 0
    for i, token in enumerate(document.tokens):
        gap = document.gaps[i] if i < len(document.gaps) else ""
        pos += len(gap)
        start = pos
        from pipeline.normalize import apply_case

        word = apply_case(document.header[token.word_id].word_original, token.case_code)
        for exp_idx, exp_word in document.explicit:
            if exp_idx == i:
                word = exp_word
                break
        pos += len(word)
        mapping.append((i, start, pos))
    if len(text) and pos > len(text):
        pass
    return mapping


def char_range_for_tokens(document: GpmDocument, token_start: int, token_count: int) -> tuple[int, int]:
    mapping = token_char_map(document)
    if token_count <= 0 or token_start >= len(mapping):
        return 0, 0
    end_idx = min(len(mapping), token_start + token_count) - 1
    return mapping[token_start][1], mapping[end_idx][2]


def serialize_viewport(document: GpmDocument) -> dict:
    """API-Payload für I-Kurve v43 GeometricMatrix + plain_gpm_base64."""
    import base64

    from gpm.format import write_gpm
    from gpm.reader import reconstruct_text

    text = reconstruct_text(document)
    hierarchy = get_hierarchy(document)
    if not document.cells:
        from gpm.cell_geom import build_document_cells

        document.cells = build_document_cells(document)

    structural_lines = [
        {
            "line_index": idx,
            "token_start": line.token_start,
            "token_count": line.token_count,
        }
        for idx, line in enumerate(hierarchy.structural.lines)
    ]
    token_map = [
        {
            "token_index": token_index,
            "char_start": char_start,
            "char_end": char_end,
        }
        for token_index, char_start, char_end in token_char_map(document)
    ]
    blob = write_gpm(document, cells=document.cells, hierarchy=hierarchy)
    return {
        "reconstructed_text": text,
        "structural_lines": structural_lines,
        "token_char_map": token_map,
        "plain_gpm_base64": base64.b64encode(blob).decode("ascii"),
    }


def nodes_for_token_span(hierarchy: DocumentHierarchy, token_start: int, token_count: int, *, interval_index=None) -> dict:
    span = TokenSpan(token_start, token_count)
    return {
        "sentences": nodes_intersecting_indexed(
            interval_index, "sentence", hierarchy.semantic.sentences, span
        ),
        "lines": nodes_intersecting_indexed(
            interval_index, "line", hierarchy.structural.lines, span
        ),
        "phrases": nodes_intersecting_indexed(
            interval_index, "phrase", hierarchy.semantic.phrases, span
        ),
    }
