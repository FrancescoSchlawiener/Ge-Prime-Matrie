"""Gap-Wort-Symmetrie-Invarianten."""

from __future__ import annotations

from analysis.document.model import GpmDocument


def assert_gap_symmetry(document: GpmDocument) -> None:
    if len(document.gaps) != len(document.tokens) + 1:
        raise ValueError(
            f"Gap-Symmetrie verletzt: len(gaps)={len(document.gaps)}, "
            f"len(tokens)={len(document.tokens)} (erwartet len+1)"
        )
