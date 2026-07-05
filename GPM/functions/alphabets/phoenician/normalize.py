"""Phoenician Normalisierung — SMP-sichere Whitelist (1:1 pro Codepoint)."""

from __future__ import annotations

from alphabets.phoenician.map import CHAR_PHOENICIAN_SET
from alphabets.unicode_utils import whitelist_codepoints


def normalize_phoenician(text: str) -> str:
    return whitelist_codepoints(text, CHAR_PHOENICIAN_SET)
