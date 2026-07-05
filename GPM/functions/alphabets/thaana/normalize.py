"""Thaana Normalisierung — NFC, Whitelist."""

from __future__ import annotations

from alphabets.thaana.map import CHAR_THAANA_SET
from alphabets.unicode_utils import whitelist_codepoints


def normalize_thaana(text: str) -> str:
    return whitelist_codepoints(text, CHAR_THAANA_SET)
