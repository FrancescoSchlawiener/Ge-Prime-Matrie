"""Gap-Ableitung aus Hierarchie + GAP-RLE-Abweichungen."""

from __future__ import annotations

from analysis.case.policy import DEFAULT_CASE_POLICY
from analysis.document.model import GpmDocument
from analysis.hierarchy.boundary import BOUNDARY_CHAR, BOUNDARY_NONE
from analysis.hierarchy.geom import DocumentHierarchy, build_document_hierarchy


def derive_gaps(token_count: int, hierarchy: DocumentHierarchy) -> list[str]:
    if token_count == 0:
        return [""]
    line_starts = {line.token_start for line in hierarchy.structural.lines}
    sentence_ends: dict[int, int] = {}
    for sentence in hierarchy.semantic.sentences:
        last = sentence.token_start + sentence.token_count - 1
        sentence_ends[last] = getattr(sentence, "boundary_suffix", BOUNDARY_NONE)

    gaps = [""] * (token_count + 1)
    for i in range(token_count):
        parts: list[str] = []
        suffix_code = sentence_ends.get(i, BOUNDARY_NONE)
        if suffix_code:
            parts.append(BOUNDARY_CHAR.get(suffix_code, ""))
        if i + 1 < token_count:
            next_i = i + 1
            if next_i in line_starts:
                parts.append("\n")
            elif not parts:
                parts.append(" ")
        gaps[i + 1] = "".join(parts)
    return gaps


def build_gap_rle_map(original_gaps: list[str], derived_gaps: list[str]) -> dict[int, str]:
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


def ensure_lossless_gaps(document: GpmDocument) -> dict[int, str]:
    """GAP-RLE-Abweichungen relativ zur read-seitig rekonstruierbaren Hierarchie."""
    original_gaps = document.gaps
    token_count = len(document.tokens)
    temp = GpmDocument(
        profile=document.profile,
        header=document.header,
        tokens=document.tokens,
        gaps=[""] * (token_count + 1),
        case_policy=DEFAULT_CASE_POLICY,
    )
    naive_hierarchy = build_document_hierarchy(temp)
    derived = derive_gaps(token_count, naive_hierarchy)
    return build_gap_rle_map(original_gaps, derived)
