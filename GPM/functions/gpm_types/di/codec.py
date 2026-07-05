"""D(I) Codec."""

from __future__ import annotations

from gpm_types.di.relation import DRelation, _decimal_places, parse_decimal


def encode_di(raw: str) -> tuple[int, int, int]:
    return parse_decimal(raw).as_triple()


def decode_di(whole: int, den_reduced: int, ggt: int, *, frac_red: int | None = None) -> str:
    den_full = den_reduced * ggt
    if den_full == 1:
        return str(whole)
    if frac_red is None:
        raise ValueError("decode_di benötigt frac_red für Roundtrip — DRelation verwenden.")
    frac_display = frac_red * ggt
    places = _decimal_places(den_full)
    frac_str = str(frac_display).zfill(places)
    return f"{whole},{frac_str.rstrip('0') or '0'}"


def decode_di_relation(rel: DRelation) -> str:
    den_full = rel.den_reduced * rel.ggt
    if den_full == 1:
        return str(rel.whole)
    frac_display = rel.frac_red * rel.ggt
    places = _decimal_places(den_full)
    frac_str = str(frac_display).zfill(places)
    return f"{rel.whole},{frac_str.rstrip('0') or '0'}"
