"""Old Italic Normalisierung — SMP-sichere Whitelist + upper."""

from __future__ import annotations

import unicodedata

from alphabets.old_italic.map import CHAR_OLD_ITALIC_SET
from alphabets.unicode_utils import assert_no_surrogates, iter_codepoints


def normalize_old_italic(text: str) -> str:
    text = unicodedata.normalize("NFC", text).upper()
    assert_no_surrogates(text)
    return "".join(ch for ch in iter_codepoints(text) if ch in CHAR_OLD_ITALIC_SET)
