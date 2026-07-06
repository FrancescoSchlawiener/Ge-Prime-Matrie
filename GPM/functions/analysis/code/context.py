"""Markdown Fence-Scanner für Hybrid-Dokumente."""

from __future__ import annotations

import re
from dataclasses import dataclass

from analysis.blocks.context import ParseContext, ParseDomain
from analysis.code.hybrid import FenceBoundary
from analysis.code.languages import resolve_fence_language

_FENCE_RE = re.compile(r"^(```|~~~)([\w+-]*)\s*$")


@dataclass
class ScannedSegment:
    domain: ParseDomain
    body: str
    language_id: str | None = None
    fence_open: FenceBoundary | None = None
    fence_close: FenceBoundary | None = None
    source_start: int = 0
    source_end: int = 0


def _line_starts(source: str) -> list[tuple[int, int, str]]:
    lines: list[tuple[int, int, str]] = []
    pos = 0
    while pos <= len(source):
        nl = source.find("\n", pos)
        if nl == -1:
            lines.append((pos, len(source), source[pos:]))
            break
        lines.append((pos, nl, source[pos:nl]))
        pos = nl + 1
    return lines


def _parse_fence_line(line: str) -> tuple[str, str, re.Match[str]] | None:
    stripped = line.strip()
    m = _FENCE_RE.match(stripped)
    if not m:
        return None
    prefix = line[: len(line) - len(line.lstrip())]
    fence_line = line.rstrip("\r\n")
    return prefix, fence_line, m


def scan_fences_hybrid(source: str) -> list[ScannedSegment]:
    """Scan hybrid source preserving fence boundaries and inter-segment gaps."""
    segments: list[ScannedSegment] = []
    lines = _line_starts(source)
    in_code = False
    lang: str | None = None
    nl_start = 0
    code_body_start = 0
    fence_open: FenceBoundary | None = None

    for start, end, line in lines:
        parsed = _parse_fence_line(line)
        if parsed is None:
            continue
        prefix, fence_line, m = parsed
        if not in_code:
            nl_body = source[nl_start:start]
            if nl_body or not segments:
                segments.append(
                    ScannedSegment(
                        domain=ParseDomain.NL,
                        body=nl_body,
                        source_start=nl_start,
                        source_end=start,
                    )
                )
            lang = resolve_fence_language(m.group(2) or "py")
            fence_open = FenceBoundary(prefix_gap=prefix, fence_line=fence_line)
            in_code = True
            code_body_start = end + 1 if end < len(source) else end
        else:
            code_body = source[code_body_start:start]
            fence_close = FenceBoundary(prefix_gap=prefix, fence_line=fence_line)
            segments.append(
                ScannedSegment(
                    domain=ParseDomain.CODE,
                    body=code_body,
                    language_id=lang,
                    fence_open=fence_open,
                    fence_close=fence_close,
                    source_start=code_body_start,
                    source_end=start,
                )
            )
            in_code = False
            lang = None
            fence_open = None
            nl_start = end + 1 if end < len(source) else end

    if in_code:
        code_body = source[code_body_start:]
        segments.append(
            ScannedSegment(
                domain=ParseDomain.CODE,
                body=code_body,
                language_id=lang,
                fence_open=fence_open,
                source_start=code_body_start,
                source_end=len(source),
            )
        )
    elif nl_start < len(source) or not segments:
        segments.append(
            ScannedSegment(
                domain=ParseDomain.NL,
                body=source[nl_start:],
                source_start=nl_start,
                source_end=len(source),
            )
        )
    return segments


def scan_fences(lines: list[str]) -> list[tuple[str, str | None, list[str]]]:
    """Legacy line-based scanner."""
    segments: list[tuple[str, str | None, list[str]]] = []
    buf: list[str] = []
    in_code = False
    lang: str | None = None

    for line in lines:
        m = _FENCE_RE.match(line.strip())
        if m:
            if not in_code:
                if buf:
                    segments.append(("nl", None, buf))
                    buf = []
                in_code = True
                lang = resolve_fence_language(m.group(2) or "py")
            else:
                segments.append(("code", lang, buf))
                buf = []
                in_code = False
                lang = None
            continue
        buf.append(line)

    if buf:
        segments.append(("code" if in_code else "nl", lang, buf))
    return segments


def context_for_segment(domain: str, language_id: str | None) -> ParseContext:
    if domain == "code":
        return ParseContext(domain=ParseDomain.CODE, language_id=language_id or "py")
    return ParseContext(domain=ParseDomain.NL)
