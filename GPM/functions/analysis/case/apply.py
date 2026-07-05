"""Schreibweise auf Wortlauf anwenden — ß/ẞ-aware."""

from __future__ import annotations

from analysis.case.codes import CASE_TITLE, CASE_UPPER


def _lower(text: str) -> str:
    return "".join("ß" if ch in ("ß", "ẞ") else ch.lower() for ch in text)


def _full_upper(text: str) -> str:
    return "".join("ẞ" if ch == "ß" else ch.upper() for ch in text)


def _title(text: str) -> str:
    lowered = _lower(text)
    if not lowered:
        return lowered
    first = lowered[0]
    first_up = "ẞ" if first == "ß" else first.upper()
    return first_up + lowered[1:]


def apply_case(run: str, code: int) -> str:
    if code == CASE_UPPER:
        return _full_upper(run)
    if code == CASE_TITLE:
        return _title(run)
    return _lower(run)
