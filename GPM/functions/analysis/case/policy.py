"""Optionale Case-Speicherung beim Compile."""

from __future__ import annotations

from dataclasses import dataclass

from analysis.case.codes import CASE_LOWER


@dataclass(frozen=True)
class CaseStoragePolicy:
    store_case: bool = True
    default_on_ambiguous: int = CASE_LOWER


DEFAULT_CASE_POLICY = CaseStoragePolicy()
