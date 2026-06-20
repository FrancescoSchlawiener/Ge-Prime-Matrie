"""Rekonstruktion und Gap-Ableitung für .gpm v7 (Separator-Absorption)."""

from __future__ import annotations

from gpm.boundary_suffix import (
    BOUNDARY_CHAR,
    BOUNDARY_NONE,
)
from gpm.hierarchy_geom import DocumentHierarchy
from gpm.model import GpmDocument
from pipeline.normalize import apply_case


def _starts_sets(hierarchy: DocumentHierarchy) -> tuple[set[int], set[int]]:
    line_starts = {line.token_start for line in hierarchy.structural.lines}
    para_starts = {para.token_start for para in hierarchy.semantic.paragraphs}
    return line_starts, para_starts


def _sentence_end_map(hierarchy: DocumentHierarchy) -> dict[int, int]:
    result: dict[int, int] = {}
    for sentence in hierarchy.semantic.sentences:
        last = sentence.token_start + sentence.token_count - 1
        result[last] = getattr(sentence, "boundary_suffix", BOUNDARY_NONE)
    return result


def _sentence_end_map_from_entries(
    entries: list[tuple[int, int, int]],
) -> dict[int, int]:
    return {start + count - 1: suffix for start, count, suffix in entries}


def derive_gaps(
    token_count: int,
    hierarchy: DocumentHierarchy,
    *,
    sentence_entries: list[tuple[int, int, int]] | None = None,
) -> list[str]:
    """Leitet gaps[] aus Hierarchie-Grenzen ab (ohne GAP-RLE-Overflow)."""
    if token_count == 0:
        return [""]
    line_starts, para_starts = _starts_sets(hierarchy)
    if sentence_entries:
        sentence_ends = _sentence_end_map_from_entries(sentence_entries)
    else:
        sentence_ends = _sentence_end_map(hierarchy)
    gaps = [""] * (token_count + 1)

    for i in range(token_count):
        parts: list[str] = []
        suffix_code = sentence_ends.get(i, BOUNDARY_NONE)
        if suffix_code:
            parts.append(BOUNDARY_CHAR.get(suffix_code, ""))

        if i + 1 < token_count:
            next_i = i + 1
            if next_i in para_starts:
                parts.append("\n\n")
            elif next_i in line_starts:
                parts.append("\n")
            elif not parts:
                parts.append(" ")

        gaps[i + 1] = "".join(parts)

    return gaps


def build_gap_rle_map(original_gaps: list[str], derived_gaps: list[str]) -> dict[int, str]:
    """Speichert nur Abweichungen zwischen Original und abgeleiteten Gaps."""
    gap_rle: dict[int, str] = {}
    for i in range(len(original_gaps)):
        if original_gaps[i] != derived_gaps[i]:
            gap_rle[i] = original_gaps[i]
    return gap_rle


def merge_gaps(derived: list[str], gap_rle: dict[int, str]) -> list[str]:
    merged = list(derived)
    for idx, gap in gap_rle.items():
        if 0 <= idx < len(merged):
            merged[idx] = gap
    return merged


def reconstruct_text_v7(document: GpmDocument) -> str:
    """Verlustfreie Rekonstruktion aus Hierarchie + GAP-RLE + Token."""
    hierarchy: DocumentHierarchy | None = getattr(document, "hierarchy", None)
    gap_rle: dict[int, str] = getattr(document, "gap_rle", None) or {}
    if hierarchy is None:
        return _reconstruct_from_gaps(document, document.gaps)

    derived = derive_gaps(len(document.tokens), hierarchy)
    gaps = merge_gaps(derived, gap_rle)
    return _reconstruct_from_gaps(document, gaps)


def _reconstruct_from_gaps(document: GpmDocument, gaps: list[str]) -> str:
    if not gaps:
        return ""
    explicit_map = dict(document.explicit)
    parts: list[str] = [gaps[0] if gaps else ""]
    for i, token in enumerate(document.tokens):
        if i in explicit_map:
            word = explicit_map[i]
        else:
            entry = document.header[token.word_id]
            word = apply_case(entry.word_original, token.case_code)
        parts.append(word)
        parts.append(gaps[i + 1] if i + 1 < len(gaps) else "")
    return "".join(parts)


def ensure_lossless_gaps(
    original_gaps: list[str],
    hierarchy: DocumentHierarchy,
) -> dict[int, str]:
    """Gesetz 2 — GAP-RLE-Fallback bis Rekonstruktion passt."""
    derived = derive_gaps(len(original_gaps) - 1, hierarchy)
    return build_gap_rle_map(original_gaps, derived)
