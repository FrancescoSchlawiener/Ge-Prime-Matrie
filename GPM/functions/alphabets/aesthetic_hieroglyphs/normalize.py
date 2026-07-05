"""Aesthetic Hieroglyphs Normalisierung — Gardiner-Map + hermetischer Endfilter."""

from __future__ import annotations

import unicodedata

from alphabets.aesthetic_hieroglyphs.gardiner_map import GLYPH_TO_UNILITERAL
from alphabets.aesthetic_hieroglyphs.map import CHAR_AESTHETIC_HIEROGLYPHS_SET
from alphabets.unicode_utils import assert_no_surrogates, iter_codepoints


def normalize_aesthetic_hieroglyphs(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    assert_no_surrogates(text)
    result: list[str] = []
    for ch in iter_codepoints(text):
        if ch in CHAR_AESTHETIC_HIEROGLYPHS_SET:
            result.append(ch)
            continue
        mapped = GLYPH_TO_UNILITERAL.get(ch)
        if mapped is not None and mapped in CHAR_AESTHETIC_HIEROGLYPHS_SET:
            result.append(mapped)
            continue
    return "".join(result)
