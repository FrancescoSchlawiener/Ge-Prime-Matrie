"""Optionaler Analyse-Modus — Toy-ähnliche Kanonisierung (nicht Default-Compile)."""

from __future__ import annotations

import re
import unicodedata

from analysis.code.comments import find_block_comment, find_c_comment, find_sql_comment
from analysis.code.languages import language_for_id
from analysis.code.tokenizer import normalize_line_endings


def _strip_hash_comments(source: str) -> str:
    lines: list[str] = []
    for line in source.split("\n"):
        out: list[str] = []
        in_str = False
        quote = ""
        i = 0
        while i < len(line):
            ch = line[i]
            if in_str:
                out.append(ch)
                if ch == quote and (i == 0 or line[i - 1] != "\\"):
                    in_str = False
            elif ch in ("'", '"'):
                in_str = True
                quote = ch
                out.append(ch)
            elif ch == "#":
                break
            else:
                out.append(ch)
            i += 1
        lines.append("".join(out).rstrip())
    return "\n".join(lines)


def _strip_c_style(source: str) -> str:
    out: list[str] = []
    pos = 0
    n = len(source)
    while pos < n:
        hit = find_c_comment(source, pos)
        if hit and hit[1] == pos:
            pos = hit[2]
            if pos < n and source[pos] == "\n":
                out.append("\n")
            continue
        out.append(source[pos])
        pos += 1
    return "".join(out)


def _strip_sql_style(source: str) -> str:
    out: list[str] = []
    pos = 0
    n = len(source)
    while pos < n:
        hit = find_sql_comment(source, pos)
        if hit and hit[1] == pos:
            pos = hit[2]
            if pos < n and source[pos] == "\n":
                out.append("\n")
            continue
        out.append(source[pos])
        pos += 1
    return "".join(out)


def strip_comments_aware(source: str, language_id: str) -> str:
    spec = language_for_id(language_id)
    text = normalize_line_endings(source)
    if spec.comment_style == "hash":
        return _strip_hash_comments(text)
    if spec.comment_style == "c":
        return _strip_c_style(text)
    if spec.comment_style == "sql":
        return _strip_sql_style(text)
    return text


def canonicalize_for_analysis(source: str, language_id: str, *, uppercase: bool = False) -> str:
    """Toy-/OG-ähnliche Normalisierung nur für Redundanz-Vergleich — nicht für compile_source."""
    text = unicodedata.normalize("NFC", strip_comments_aware(source, language_id))
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    if uppercase:
        text = text.upper()
    return text


def normalize_for_tensorraum(source: str, language_id: str) -> str:
    """OG v35-Kanonisierung: Kommentare weg (sprachspezifisch), dann ß/Ä/Ö/Ü + UPPERCASE."""
    text = strip_comments_aware(source, language_id)
    text = (
        text.replace("ß", "ẞ")
        .upper()
        .replace("Ä", "AE")
        .replace("Ö", "OE")
        .replace("Ü", "UE")
    )
    text = unicodedata.normalize("NFD", text)
    return "".join(c for c in text if unicodedata.category(c) != "Mn")
