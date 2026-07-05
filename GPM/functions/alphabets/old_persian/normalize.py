"""Old Persian Normalisierung — SMP-sichere Whitelist."""

from __future__ import annotations

from alphabets.old_persian.map import CHAR_OLD_PERSIAN_SET
from alphabets.unicode_utils import whitelist_codepoints


def normalize_old_persian(text: str) -> str:
    return whitelist_codepoints(text, CHAR_OLD_PERSIAN_SET)
