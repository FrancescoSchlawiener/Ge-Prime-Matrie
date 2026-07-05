"""Hiragana Normalisierung — NFC, Dakuten→Grundzeichen."""

from __future__ import annotations

import unicodedata

_DAKUTEN = "\u3099"
_HANDAKUTEN = "\u309A"
_VOICED_MAP: dict[str, str] = {
    "が": "か", "ぎ": "き", "ぐ": "く", "げ": "け", "ご": "こ",
    "ざ": "さ", "じ": "し", "ず": "す", "ぜ": "せ", "ぞ": "そ",
    "だ": "た", "ぢ": "ち", "づ": "つ", "で": "て", "ど": "と",
    "ば": "は", "び": "ひ", "ぶ": "ふ", "べ": "へ", "ぼ": "ほ",
    "ぱ": "は", "ぴ": "ひ", "ぷ": "ふ", "ぺ": "へ", "ぽ": "ほ",
}


def normalize_hiragana(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    return "".join(_VOICED_MAP.get(ch, ch) for ch in text)
