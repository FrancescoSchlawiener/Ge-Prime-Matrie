"""Arabic Normalisierung — NFC, Alef/Ya/Waw-Vereinheitlichung."""

from __future__ import annotations

import unicodedata

_ALEF_VARIANTS = {"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي", "ئ": "ي", "ؤ": "و", "ة": "ه"}
_TATWEEL = "\u0640"


def normalize_arabic(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = text.replace(_TATWEEL, "")
    result: list[str] = []
    for ch in text:
        if unicodedata.category(ch).startswith("M"):
            continue
        result.append(_ALEF_VARIANTS.get(ch, ch))
    return "".join(result)
