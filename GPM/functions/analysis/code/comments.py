"""Kommentar-Erkennung für Code-Lexer (bitgenau, PointerKind.C)."""

from __future__ import annotations

import re

_HASH_COMMENT = re.compile(r"#.*")
_LINE_COMMENT = re.compile(r"//[^\n]*")
_BLOCK_COMMENT = re.compile(r"/\*[\s\S]*?\*/")


def extract_hash_comment(line: str, after: int = 0) -> tuple[str, int] | None:
    """Hash-Kommentar ab Position *after* (Rest der Zeile inkl. #)."""
    rest = line[after:]
    m = _HASH_COMMENT.search(rest)
    if not m:
        return None
    text = m.group(0)
    if text == "#":
        return text, after + m.start()
    return text, after + m.start()


def find_c_comment(source: str, pos: int) -> tuple[str, int, int] | None:
    """Line- oder Block-Kommentar ab *pos*. Returns (text, start, end)."""
    if pos >= len(source):
        return None
    if source.startswith("//", pos):
        m = _LINE_COMMENT.match(source, pos)
        if m:
            return m.group(0), m.start(), m.end()
    if source.startswith("/*", pos):
        m = _BLOCK_COMMENT.match(source, pos)
        if m:
            return m.group(0), m.start(), m.end()
    return None
