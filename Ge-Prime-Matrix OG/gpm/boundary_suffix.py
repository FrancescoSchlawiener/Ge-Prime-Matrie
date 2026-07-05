"""Satzgrenzen-Suffixe für .gpm v7 (Separator-Absorption)."""

from __future__ import annotations

from gpm.model import GpmDocument
from pipeline.normalize import apply_case

BOUNDARY_NONE = 0
BOUNDARY_PERIOD = 1
BOUNDARY_EXCLAMATION = 2
BOUNDARY_QUESTION = 3

_BOUNDARY_CHARS = {
    BOUNDARY_NONE: "",
    BOUNDARY_PERIOD: ".",
    BOUNDARY_EXCLAMATION: "!",
    BOUNDARY_QUESTION: "?",
}

_CHAR_TO_BOUNDARY = {v: k for k, v in _BOUNDARY_CHARS.items() if v}

BOUNDARY_CHAR = _BOUNDARY_CHARS


def boundary_suffix_from_gap(gap_after: str) -> int:
    stripped = gap_after.rstrip()
    for ch in reversed(stripped):
        if ch in _CHAR_TO_BOUNDARY:
            return _CHAR_TO_BOUNDARY[ch]
    return BOUNDARY_NONE


def boundary_suffix_for_token(document: GpmDocument, token_index: int, gap_after: str) -> int:
    suffix = boundary_suffix_from_gap(gap_after)
    if suffix != BOUNDARY_NONE:
        return suffix
    explicit_map = dict(document.explicit)
    if token_index in explicit_map:
        word = explicit_map[token_index]
    else:
        token = document.tokens[token_index]
        entry = document.header[token.word_id]
        word = apply_case(entry.word_original, token.case_code)
    stripped = word.rstrip()
    for ch in reversed(stripped):
        if ch in _CHAR_TO_BOUNDARY:
            return _CHAR_TO_BOUNDARY[ch]
    return BOUNDARY_NONE
