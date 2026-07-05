"""Glagolitic Normalisierung — NFC + upper, Whitelist."""

from __future__ import annotations

import unicodedata

from alphabets.glagolitic.map import CHAR_GLAGOLITIC_SET
from alphabets.unicode_utils import assert_no_surrogates, iter_codepoints


def normalize_glagolitic(text: str) -> str:
    text = unicodedata.normalize("NFC", text).upper()
    assert_no_surrogates(text)
    return "".join(ch for ch in iter_codepoints(text) if ch in CHAR_GLAGOLITIC_SET)
