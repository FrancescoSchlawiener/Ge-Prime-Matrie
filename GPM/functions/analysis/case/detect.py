"""Schreibweise-Code aus Original-Wortlauf erkennen."""

from __future__ import annotations

from analysis.case.apply import _full_upper, _lower, _title
from analysis.case.codes import CASE_EXPLICIT, CASE_LOWER, CASE_TITLE, CASE_UPPER


def detect_case(run: str) -> int:
    if not run:
        return CASE_LOWER
    if run == _lower(run):
        return CASE_LOWER
    if run == _full_upper(run):
        return CASE_UPPER
    if run == _title(run):
        return CASE_TITLE
    return CASE_EXPLICIT
