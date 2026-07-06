"""Kommentar-Erkennung für Code-Lexer (bitgenau, PointerKind.C)."""

from __future__ import annotations

import re

_HASH_COMMENT = re.compile(r"#.*")
_LINE_COMMENT = re.compile(r"//[^\n]*")
_SQL_LINE_COMMENT = re.compile(r"--[^\n]*")
_BLOCK_COMMENT = re.compile(r"/\*[\s\S]*?\*/")


def extract_hash_comment(line: str, after: int = 0) -> tuple[str, int] | None:
    """Hash-Kommentar ab Position *after* (Rest der Zeile inkl. #)."""
    rest = line[after:]
    m = _HASH_COMMENT.search(rest)
    if not m:
        return None
    text = m.group(0)
    return text, after + m.start()


def find_block_comment(source: str, pos: int) -> tuple[str, int, int] | None:
    """Block-Kommentar /* */ ab *pos*. Returns (text, start, end). Guard B."""
    if pos >= len(source) or not source.startswith("/*", pos):
        return None
    m = _BLOCK_COMMENT.match(source, pos)
    if m:
        return m.group(0), m.start(), m.end()
    return None


def find_c_comment(source: str, pos: int) -> tuple[str, int, int] | None:
    """Line- oder Block-Kommentar (c-Stil) ab *pos*."""
    if pos >= len(source):
        return None
    if source.startswith("//", pos):
        m = _LINE_COMMENT.match(source, pos)
        if m:
            return m.group(0), m.start(), m.end()
    return find_block_comment(source, pos)


def find_sql_comment(source: str, pos: int) -> tuple[str, int, int] | None:
    """SQL-Kommentar -- oder /* */ ab *pos*."""
    if pos >= len(source):
        return None
    if source.startswith("--", pos):
        m = _SQL_LINE_COMMENT.match(source, pos)
        if m:
            return m.group(0), m.start(), m.end()
    return find_block_comment(source, pos)


def find_comment_at(source: str, pos: int, comment_style: str) -> tuple[str, int, int] | None:
    if comment_style == "c":
        return find_c_comment(source, pos)
    if comment_style == "sql":
        return find_sql_comment(source, pos)
    return None


def next_comment_start(source: str, pos: int, comment_style: str) -> tuple[str, int, int] | None:
    """Nächster Kommentar ab oder nach *pos* (nur c/sql)."""
    if comment_style not in ("c", "sql"):
        return None
    n = len(source)
    p = pos
    while p < n:
        if comment_style == "c":
            hit = find_c_comment(source, p)
        else:
            hit = find_sql_comment(source, p)
        if hit:
            return hit
        p += 1
    return None
