"""Old Turkic Normalisierung — SMP-sichere Whitelist."""

from __future__ import annotations

from alphabets.old_turkic.map import CHAR_OLD_TURKIC_SET
from alphabets.unicode_utils import whitelist_codepoints


def normalize_old_turkic(text: str) -> str:
    return whitelist_codepoints(text, CHAR_OLD_TURKIC_SET)
