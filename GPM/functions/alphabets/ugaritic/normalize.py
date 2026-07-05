"""Ugaritic Normalisierung — SMP-sichere Whitelist (1:1 pro Codepoint)."""

from __future__ import annotations

from alphabets.ugaritic.map import CHAR_UGARITIC_SET
from alphabets.unicode_utils import whitelist_codepoints


def normalize_ugaritic(text: str) -> str:
    return whitelist_codepoints(text, CHAR_UGARITIC_SET)
