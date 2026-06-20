"""Wörter aus Freitext für die Web-Encodierung extrahieren."""

import re
import unicodedata

MAX_ENCODE_WORDS = 50
MAX_DOCUMENT_WORDS = 100_000


def letters_only(token: str) -> str:
    """Behält nur Buchstaben (inkl. Umlaute, ß); Ziffern und Satzzeichen werden ignoriert."""
    token = unicodedata.normalize("NFC", token)
    return "".join(ch for ch in token if ch.isalpha() or ch in "ßẞ")


def extract_encode_words(
    text: str,
    *,
    max_words: int = MAX_ENCODE_WORDS,
) -> tuple[list[str], int, bool]:
    """
    Teilt an Leerzeichen/Zeilenumbrüchen, pro Token nur Buchstaben behalten.
    Returns: (words, skipped_empty_tokens, truncated)
    """
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


def extract_document_tokens(
    text: str,
    *,
    max_words: int = MAX_DOCUMENT_WORDS,
) -> tuple[list[str], int]:
    """Alle Wörter eines Dokuments für .gpm-Compiler (ohne Encode-Limit 50)."""
    return extract_encode_words(text, max_words=max_words)


def _is_word_char(ch: str) -> bool:
    """Buchstaben (inkl. Umlaute) und ß zählen zum Wort; alles andere ist Gap."""
    return ch.isalpha() or ch in "ßẞ"


def split_segments(text: str) -> list[tuple[str, str]]:
    """
    Zerlegt Text verlustfrei in geordnete Segmente.

    Returns: Liste aus (kind, text) mit kind ∈ {"word", "gap"}.
    - "word": maximaler Lauf aus Buchstaben/Umlauten/ß
    - "gap":  alles andere (Leerzeichen, Satzzeichen, Ziffern, Symbole, Emoji) verbatim

    Konkateniert man alle text-Teile in Reihenfolge, ergibt sich exakt der
    Originaltext (NFC-normalisiert).
    """
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

    if buf:
        segments.append(("word" if current_word else "gap", "".join(buf)))
    return segments
