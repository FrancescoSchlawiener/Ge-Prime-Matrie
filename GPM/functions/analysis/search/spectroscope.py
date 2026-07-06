"""Spektroskopie — SubstanceIndex + Intervall-Index."""

from __future__ import annotations

import math

from analysis.blocks.node import TokenSpan
from analysis.compile.compiler import compile_text, normalize_text_nfc
from analysis.hierarchy.access import get_hierarchy, get_interval_index
from analysis.hierarchy.compare import compare_level_sequences
from analysis.hierarchy.curves import extract_line_curve, extract_sentence_curve
from analysis.hierarchy.span_utils import char_range_for_tokens, nodes_for_token_span, token_char_map
from analysis.index.interval_index import BITSET_TOKEN_LIMIT
from analysis.index.substance_index import (
    get_substance_index,
    scan_windows,
    window_fingerprint,
)
from analysis.algebra.window_fold import exponent_window_to_substance
from analysis.span.substance_span import local_kgv, passes_kgv_gate

STRUCTURAL_THRESHOLD = 0.75


def spectroscope_analyze(
    document,
    *,
    token_start: int,
    token_end: int,
    modes: list[str] | None = None,
) -> dict:
    modes = modes or ["substance_divisor", "anagram_shadow", "structural_twin"]
    token_count = max(0, token_end - token_start)
    if token_count == 0:
        token_count = len(document.tokens)
        token_start = 0
        token_end = token_count

    width = token_count
    substance_index = get_substance_index(document)
    target_fp = window_fingerprint(substance_index, token_start, token_end)

    s_target = exponent_window_to_substance(target_fp)

    hierarchy = get_hierarchy(document)
    idx = get_interval_index(document)
    affected = nodes_for_token_span(hierarchy, token_start, token_count, interval_index=idx)

    target_sentence_curve = []
    for sentence in affected["sentences"]:
        target_sentence_curve.extend(
            [p for p in extract_sentence_curve(document) if p["token_start"] == sentence.token_start]
        )
    target_line_curve = []
    for line in affected["lines"]:
        target_line_curve.extend(
            [p for p in extract_line_curve(document) if p["token_start"] == line.token_start]
        )

    matches: list[dict] = []

    if "substance_divisor" in modes or "anagram_shadow" in modes:
        scan_modes = [m for m in modes if m in ("substance_divisor", "anagram_shadow")]
        raw = scan_windows(
            substance_index,
            width,
            target_fp,
            modes=scan_modes,
            skip_start=token_start if width == token_count else None,
            profile=document.profile,
        )
        for hit in raw:
            cs, ce = char_range_for_tokens(
                document, hit["token_start"], hit["token_end"] - hit["token_start"]
            )
            matches.append(
                {
                    **hit,
                    "layer": "semantic",
                    "char_start": cs,
                    "char_end": ce,
                }
            )

    if "structural_twin" in modes:
        sentence_curve = extract_sentence_curve(document)
        line_curve = extract_line_curve(document)
        doc_span = TokenSpan(0, max(1, len(document.tokens)))
        use_bitset = len(document.tokens) <= BITSET_TOKEN_LIMIT
        if use_bitset:
            allowed_sentence = {n.token_start for n in idx.query("sentence", doc_span)}
            allowed_line = {n.token_start for n in idx.query("line", doc_span)}
        else:
            allowed_sentence = allowed_line = None
        if target_sentence_curve:
            for point in sentence_curve:
                if allowed_sentence is not None and point["token_start"] not in allowed_sentence:
                    continue
                span_count = point["token_count"]
                if span_count <= 0:
                    continue
                local = local_kgv(document, point["token_start"], span_count)
                if not passes_kgv_gate(local, s_target):
                    continue
                cmp = compare_level_sequences(
                    [point],
                    target_sentence_curve[:1],
                    ratio_key="i_satz_ratio",
                )
                score = cmp.get("geometry_score", 0.0)
                if score >= STRUCTURAL_THRESHOLD and point["token_start"] != token_start:
                    cs, ce = char_range_for_tokens(
                        document, point["token_start"], point["token_count"]
                    )
                    matches.append(
                        {
                            "mode": "structural_twin",
                            "layer": "semantic",
                            "token_start": point["token_start"],
                            "token_end": point["token_start"] + point["token_count"],
                            "char_start": cs,
                            "char_end": ce,
                            "score_semantic": round(score, 6),
                            "score": round(score, 6),
                        }
                    )
        if target_line_curve:
            for point in line_curve:
                if allowed_line is not None and point["token_start"] not in allowed_line:
                    continue
                span_count = point["token_count"]
                if span_count <= 0:
                    continue
                local = local_kgv(document, point["token_start"], span_count)
                if not passes_kgv_gate(local, s_target):
                    continue
                cmp = compare_level_sequences(
                    [point],
                    target_line_curve[:1],
                    ratio_key="i_zeile_ratio",
                )
                score = cmp.get("geometry_score", 0.0)
                if score >= STRUCTURAL_THRESHOLD and point["token_start"] != token_start:
                    cs, ce = char_range_for_tokens(
                        document, point["token_start"], point["token_count"]
                    )
                    matches.append(
                        {
                            "mode": "structural_twin",
                            "layer": "structural",
                            "token_start": point["token_start"],
                            "token_end": point["token_start"] + point["token_count"],
                            "char_start": cs,
                            "char_end": ce,
                            "score_structural": round(score, 6),
                            "score": round(score, 6),
                        }
                    )

    cs, ce = char_range_for_tokens(document, token_start, token_count)
    return {
        "target": {
            "token_start": token_start,
            "token_end": token_end,
            "char_start": cs,
            "char_end": ce,
            "substance": s_target,
            "width": width,
        },
        "matches": matches,
        "match_count": len(matches),
    }


def spectroscope_from_text(
    text: str,
    *,
    selection_start: int,
    selection_end: int,
    modes: list[str] | None = None,
    profile=None,
) -> dict:
    text = normalize_text_nfc(text)
    selection_start = max(0, min(int(selection_start), len(text)))
    selection_end = max(selection_start, min(int(selection_end), len(text)))
    document, _ = compile_text(text, profile=profile or "og")
    mapping = token_char_map(document)
    t_start, t_end = 0, len(document.tokens)
    if mapping:
        selected = [
            idx
            for idx, cs, ce in mapping
            if ce > selection_start and cs < selection_end
        ]
        if selected:
            t_start = min(selected)
            t_end = max(selected) + 1
    result = spectroscope_analyze(
        document,
        token_start=t_start,
        token_end=t_end,
        modes=modes,
    )
    result["token_char_map"] = [
        {"token_index": idx, "char_start": cs, "char_end": ce}
        for idx, cs, ce in mapping
    ]
    return result
