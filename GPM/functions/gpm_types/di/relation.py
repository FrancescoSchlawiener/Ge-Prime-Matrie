"""D(I) — Dezimal als drei N-Werte (+ interne frac_red für Roundtrip)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from math import gcd

_DECIMAL_PARSE = re.compile(r"^[+-]?(\d+)([.,](\d+))?$")


@dataclass(frozen=True)
class DRelation:
    whole: int
    den_reduced: int
    ggt: int
    frac_red: int

    def as_triple(self) -> tuple[int, int, int]:
        return self.whole, self.den_reduced, self.ggt


def parse_decimal(raw: str) -> DRelation:
    """Dezimal → Relation. Beispiel 4,16 → whole=4, den_reduced=25, ggt=4."""
    text = (raw or "").strip().replace(" ", "")
    if text.startswith("+"):
        text = text[1:]
    if text.startswith("-"):
        raise ValueError("D(I) unterstützt keine negativen Dezimalwerte.")
    m = _DECIMAL_PARSE.match(text)
    if not m:
        raise ValueError(f"Kein Dezimalwert: {raw!r}")
    whole_s = m.group(1)
    frac_s = m.group(3) or ""
    whole = int(whole_s)
    if frac_s:
        num = int(whole_s + frac_s)
        den = 10 ** len(frac_s)
    else:
        num = whole
        den = 1
    g = gcd(num, den)
    den_reduced = den // g
    frac_red = num // g - whole * den_reduced
    return DRelation(whole, den_reduced, g, frac_red)


def relation_key(raw: str) -> str:
    rel = parse_decimal(raw)
    w, d, g = rel.as_triple()
    return f"{w}:{d}:{g}"


def _decimal_places(den_full: int) -> int:
    n = 0
    d = den_full
    while d > 1 and d % 10 == 0:
        d //= 10
        n += 1
    return n
