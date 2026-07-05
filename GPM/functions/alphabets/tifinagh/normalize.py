"""Tifinagh Normalisierung — NFC, Whitelist."""

from __future__ import annotations

from alphabets.tifinagh.map import CHAR_TIFINAGH_SET
from alphabets.unicode_utils import whitelist_codepoints


def normalize_tifinagh(text: str) -> str:
    return whitelist_codepoints(text, CHAR_TIFINAGH_SET)
