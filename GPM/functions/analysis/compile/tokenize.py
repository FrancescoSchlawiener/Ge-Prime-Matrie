"""Verlustfreie Wort/Gap-Segmentierung."""

from __future__ import annotations

import unicodedata


def _is_word_char(ch: str) -> bool:
    return ch.isalpha() or ch in "ßẞ"


def split_segments(text: str) -> list[tuple[str, str]]:
    if not text:
        return []

    text = unicodedata.normalize("NFC", text)
    segments: list[tuple[str, str]] = []
    buf: list[str] = []
    current_word = _is_word_char(text[0])

    for ch in text:
        is_word = _is_word_char(ch)
        if is_word != current_word:
            segments.append(("word" if current_word else "gap", "".join(buf)))
            buf = []
            current_word = is_word
        buf.append(ch)

    segments.append(("word" if current_word else "gap", "".join(buf)))
    return segments
