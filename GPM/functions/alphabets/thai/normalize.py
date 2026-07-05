"""Thai Normalisierung — NFC."""

from __future__ import annotations

import unicodedata


def normalize_thai(text: str) -> str:
    return unicodedata.normalize("NFC", text)
