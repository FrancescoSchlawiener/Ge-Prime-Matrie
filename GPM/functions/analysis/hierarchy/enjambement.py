"""Enjambement — Schnittmenge Satz-/Zeilen-Gitter."""

from __future__ import annotations

from analysis.blocks.node import TokenSpan
from analysis.document.model import GpmDocument
from analysis.hierarchy.access import get_hierarchy, get_interval_index
from analysis.hierarchy.geom import HierarchyNode, intervals_overlap, validate_structural_partition


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
    return detect_enjambement(h.semantic.sentences, h.structural.lines, interval_index=idx)
