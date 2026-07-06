"""Wort-Extraktion für Encode-Batch — OG-Parität (pipeline/tokenize.py)."""

from __future__ import annotations

import re
import unicodedata

MAX_ENCODE_WORDS = 50


def letters_only(token: str) -> str:
    token = unicodedata.normalize("NFC", token)
    return "".join(ch for ch in token if ch.isalpha() or ch in "ßẞ")


def extract_encode_words(
    text: str,
    *,
    max_words: int = MAX_ENCODE_WORDS,
) -> tuple[list[str], int, bool]:
    if not text or not text.strip():
        return [], 0, False

    parts = re.split(r"\s+", text.strip())
    candidates: list[str] = []
    skipped = 0

    for part in parts:
        letters = letters_only(part)
        if not letters:
            skipped += 1
            continue
        candidates.append(letters)

    truncated = len(candidates) > max_words
    return candidates[:max_words], skipped, truncated
