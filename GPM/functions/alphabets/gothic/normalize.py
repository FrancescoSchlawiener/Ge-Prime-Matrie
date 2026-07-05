"""Gothic Normalisierung — SMP-sichere Whitelist + upper auf str-Scalars."""

from __future__ import annotations

import unicodedata

from alphabets.gothic.map import CHAR_GOTHIC_SET
from alphabets.unicode_utils import assert_no_surrogates, iter_codepoints


def normalize_gothic(text: str) -> str:
    text = unicodedata.normalize("NFC", text).upper()
    assert_no_surrogates(text)
    return "".join(ch for ch in iter_codepoints(text) if ch in CHAR_GOTHIC_SET)
