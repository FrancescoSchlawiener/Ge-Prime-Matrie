"""H(I) Segmente — Lese-Reihenfolge, keine Sortierung nach Typ."""

from __future__ import annotations

from dataclasses import dataclass

from alphabets.roman.normalize import normalize_latin
from gpm_types.ni.canonical import canonical_n

SegmentTag = str  # "S" | "N"


@dataclass(frozen=True)
class HiSegment:
    tag: SegmentTag
    value: str


@dataclass(frozen=True)
class HiPayload:
    segments: tuple[HiSegment, ...]


def parse_hi_segments(raw: str) -> HiPayload:
    """Zerlegt gemischte Eingabe in typisierte Segmente (links → rechts)."""
    text = (raw or "").strip()
    if not text:
        raise ValueError("Leerer H(I)-Wert.")
    parts: list[HiSegment] = []
    for kind, chunk in _split_runs(text):
        if kind == "N":
            parts.append(HiSegment("N", canonical_n(chunk)))
        else:
            parts.append(HiSegment("S", normalize_latin(chunk)))
    if len(parts) < 2 or len({p.tag for p in parts}) < 2:
        raise ValueError(f"Kein gemischter H(I)-Wert: {raw!r}")
    return HiPayload(tuple(parts))


def _split_runs(text: str) -> list[tuple[str, str]]:
    runs: list[tuple[str, str]] = []
    i = 0
    while i < len(text):
        if text[i].isdigit():
            j = i + 1
            while j < len(text) and text[j].isdigit():
                j += 1
            runs.append(("N", text[i:j]))
            i = j
        elif text[i].isalpha() or text[i] in "ßẞäöüÄÖÜ":
            j = i + 1
            while j < len(text) and (text[j].isalpha() or text[j] in "ßẞäöüÄÖÜ"):
                j += 1
            runs.append(("S", text[i:j]))
            i = j
        else:
            raise ValueError(f"Ungültiges Zeichen in H(I): {text[i]!r}")
    return runs
