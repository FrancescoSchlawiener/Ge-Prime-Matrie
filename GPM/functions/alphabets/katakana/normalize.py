"""Katakana Normalisierung — NFC, Dakuten→Grundzeichen."""

from __future__ import annotations

import unicodedata

_VOICED_MAP: dict[str, str] = {
    "ガ": "カ", "ギ": "キ", "グ": "ク", "ゲ": "ケ", "ゴ": "コ",
    "ザ": "サ", "ジ": "シ", "ズ": "ス", "ゼ": "セ", "ゾ": "ソ",
    "ダ": "タ", "ヂ": "チ", "ヅ": "ツ", "デ": "テ", "ド": "ト",
    "バ": "ハ", "ビ": "ヒ", "ブ": "フ", "ベ": "ヘ", "ボ": "ホ",
    "パ": "ハ", "ピ": "ヒ", "プ": "フ", "ペ": "ヘ", "ポ": "ホ",
    "ヴ": "ウ",
}


def normalize_katakana(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    return "".join(_VOICED_MAP.get(ch, ch) for ch in text if ch != "ー")
