"""SMP-sichere Codepoint-Iteration und Whitelist-Filter.

Python-3-str iteriert Unicode-Scalars (kein UTF-16-Code-Unit-Split).
Referenzimplementierung für spätere C/Bare-Metal-Ports auf 32-Bit-Codepoints.
"""

from __future__ import annotations

import unicodedata
from collections.abc import Iterator

_SURROGATE_LO = 0xD800
_SURROGATE_HI = 0xDFFF


class SurrogateCodepointError(ValueError):
    """Eingabe enthält ill-formed Surrogat-Scalars (U+D800–U+DFFF)."""


def iter_codepoints(text: str) -> Iterator[str]:
    """Ein str-Scalar pro Unicode-Codepoint."""
    yield from text


def assert_no_surrogates(text: str) -> None:
    """0xD800–0xDFFF in Eingabe ablehnen (ill-formed scalar values)."""
    for ch in text:
        cp = ord(ch)
        if _SURROGATE_LO <= cp <= _SURROGATE_HI:
            raise SurrogateCodepointError(
                f"Surrogat-Scalar U+{cp:04X} in Eingabe — kein vollständiger Codepoint."
            )


def whitelist_codepoints(text: str, allowed: frozenset[str]) -> str:
    """NFC → pro Codepoint prüfen → nur erlaubte Scalars behalten (1:1)."""
    text = unicodedata.normalize("NFC", text)
    assert_no_surrogates(text)
    return "".join(ch for ch in iter_codepoints(text) if ch in allowed)
