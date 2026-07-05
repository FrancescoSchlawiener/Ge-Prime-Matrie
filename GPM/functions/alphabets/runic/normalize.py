"""Runic Normalisierung — statische Zuordnung, NFC-Stabilisierung."""

from __future__ import annotations

import unicodedata

from alphabets.runic.map import CHAR_RUNIC_SET


def normalize_runic(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    return "".join(ch for ch in text if ch in CHAR_RUNIC_SET)
