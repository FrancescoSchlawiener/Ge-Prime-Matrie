"""Ogham Normalisierung — NFC, Whitelist."""

from __future__ import annotations

from alphabets.ogham.map import CHAR_OGHAM_SET
from alphabets.unicode_utils import whitelist_codepoints


def normalize_ogham(text: str) -> str:
    return whitelist_codepoints(text, CHAR_OGHAM_SET)
