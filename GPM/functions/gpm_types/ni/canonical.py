"""N(I) — Ganzzahl-Kanonisierung."""

from __future__ import annotations


def canonical_n(raw: str) -> str:
    text = (raw or "").strip()
    if not text:
        raise ValueError("Leerer N(I)-Wert.")
    if text.startswith("+"):
        text = text[1:]
    if text.startswith("-"):
        raise ValueError("N(I) unterstützt keine negativen Ganzzahlen.")
    if not text.isdigit():
        raise ValueError(f"Keine Ganzzahl: {raw!r}")
    return text.lstrip("0") or "0"


def canonical_n_int(raw: str) -> int:
    return int(canonical_n(raw))
