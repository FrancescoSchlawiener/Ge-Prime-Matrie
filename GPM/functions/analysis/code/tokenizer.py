"""Scalar-Lexer — Astral-Plane-sicher, nl/col_prefix/EOF (Absicherung B)."""

from __future__ import annotations

import re
import unicodedata

from alphabets.unicode_utils import assert_no_surrogates
from analysis.blocks.context import ParseContext, ParseDomain
from analysis.blocks.kinds import PointerKind
from analysis.code.comments import extract_hash_comment
from analysis.code.languages import VOID_HTML_TAGS, language_for_id
from analysis.code.tokens import (
    CodeToken,
    TokenizeResult,
    extract_trailing_whitespace,
    split_leading_gap,
)

_TOKEN_PATTERN = re.compile(
    r'("(?:\\[\s\S]|[^"\\])*"|\'(?:\\[\s\S]|[^\'\\])*\'|`(?:\\[\s\S]|[^`\\])*`)'
    r"|(//[^\n]*|/\*[\s\S]*?\*/)"
    r"|(\b[\w\u0080-\U0010FFFF]+\b)"
    r"|([0-9]+\.[0-9]+|[0-9]+)"
    r"|([{}()\[\]])"
    r"|(=>|\?\?|\?\.|===|!==|\+\+|--|<<|>>|[+\-*/=<>!&|^%?:]+)"
    r"|([.,;])"
)


def normalize_line_endings(source: str) -> str:
    return source.replace("\r\n", "\n").replace("\r", "\n")


def classify_code_token(value: str, *, context: ParseContext, language_id: str) -> PointerKind:
    if context.domain is ParseDomain.NL:
        return PointerKind.S
    if value.startswith(('"', "'", "`")):
        return PointerKind.S
    if value.startswith("//") or value.startswith("/*"):
        return PointerKind.C
    if re.fullmatch(r"[+-]?\d+", value):
        return PointerKind.N
    if re.fullmatch(r"[+-]?\d+\.\d+", value):
        return PointerKind.D
    spec = language_for_id(language_id)
    low = value.lower()
    if low in spec.keywords:
        return PointerKind.C
    if value in "(){}[];,.":
        return PointerKind.C
    if re.fullmatch(r"(=>|\?\?|\?\.|===|!==|\+\+|--|<<|>>|[+\-*/=<>!&|^%?:]+)", value):
        return PointerKind.C
    return PointerKind.S


def expand_tabs_to_columns(line: str, tab_size: int = 8) -> int:
    col = 0
    for ch in line:
        if ch == "\t":
            col += tab_size - (col % tab_size)
        elif ch == " ":
            col += 1
        else:
            break
    return col


def _emit_brace_token(
    tokens: list[CodeToken],
    val: str,
    nl: int,
    col_prefix: str,
    ctx: ParseContext,
    language_id: str,
) -> None:
    if val in "{[":
        tokens.append(CodeToken(block="open", value=val, nl=nl, col_prefix=col_prefix))
    elif val in "}]":
        tokens.append(CodeToken(block="close", value=val, nl=nl, col_prefix=col_prefix))
    elif val in "()":
        tokens.append(CodeToken(type=PointerKind.C.value, value=val, nl=nl, col_prefix=col_prefix))
    else:
        kind = classify_code_token(val, context=ctx, language_id=language_id)
        tokens.append(CodeToken(type=kind.value, value=val, nl=nl, col_prefix=col_prefix))


def tokenize_brace(source: str, language_id: str) -> TokenizeResult:
    assert_no_surrogates(source)
    source = unicodedata.normalize("NFC", normalize_line_endings(source))
    ctx = ParseContext(ParseDomain.CODE, language_id)
    tokens: list[CodeToken] = []
    last = 0
    for m in _TOKEN_PATTERN.finditer(source):
        nl, col_prefix = split_leading_gap(source, last, m.start())
        val = m.group(0)
        last = m.end()
        if not val.strip():
            continue
        _emit_brace_token(tokens, val, nl, col_prefix, ctx, language_id)
    trailing = extract_trailing_whitespace(source, last)
    return TokenizeResult(tokens=tokens, trailing_whitespace=trailing)


def tokenize_indent(source: str, language_id: str) -> TokenizeResult:
    assert_no_surrogates(source)
    source = unicodedata.normalize("NFC", normalize_line_endings(source))
    spec = language_for_id(language_id)
    ctx = ParseContext(ParseDomain.CODE, language_id)
    lines = source.split("\n")
    tokens: list[CodeToken] = []
    indent_stack = [0]
    pending_nl = 0
    last_end = 0

    for line_idx, raw_line in enumerate(lines):
        line_start = sum(len(lines[i]) + 1 for i in range(line_idx))
        trimmed = raw_line.lstrip(" \t")
        col_prefix_line = raw_line[: len(raw_line) - len(trimmed)]

        if not trimmed.strip():
            pending_nl += 1
            continue

        indent = expand_tabs_to_columns(raw_line)
        nl_for_line = pending_nl + (1 if line_idx > 0 else 0)
        pending_nl = 0
        opened_this_line = False

        if indent > indent_stack[-1]:
            tokens.append(
                CodeToken(
                    block="open",
                    nl=nl_for_line,
                    col_prefix=col_prefix_line,
                    visual_style="indent",
                )
            )
            indent_stack.append(indent)
            opened_this_line = True
            nl_for_line = 0
        else:
            while indent < indent_stack[-1]:
                tokens.append(CodeToken(block="close", nl=0, visual_style="indent"))
                indent_stack.pop()

        content_start = line_start + len(raw_line) - len(trimmed)
        code_part = trimmed
        comment_text: str | None = None
        if spec.comment_style == "hash":
            found = extract_hash_comment(trimmed)
            if found:
                comment_text, rel_start = found
                in_string = False
                quote = ""
                for i, ch in enumerate(trimmed[:rel_start]):
                    if in_string:
                        if ch == quote and (i == 0 or trimmed[i - 1] != "\\"):
                            in_string = False
                    elif ch in ("'", '"'):
                        in_string = True
                        quote = ch
                if not in_string:
                    code_part = trimmed[:rel_start].rstrip()

        first = True
        line_last = content_start
        for m in _TOKEN_PATTERN.finditer(code_part):
            val = m.group(0)
            if not val.strip():
                continue
            abs_start = content_start + m.start()
            abs_end = content_start + m.end()
            if first and not opened_this_line:
                t_nl, t_col = nl_for_line, col_prefix_line
            elif first:
                t_nl, t_col = 0, ""
            else:
                t_nl, t_col = split_leading_gap(source, line_last, abs_start)
            first = False
            kind = classify_code_token(val, context=ctx, language_id=language_id)
            tokens.append(CodeToken(type=kind.value, value=val, nl=t_nl, col_prefix=t_col))
            line_last = abs_end
            last_end = abs_end

        if comment_text is not None:
            c_start = content_start + trimmed.index(comment_text)
            if first and not opened_this_line:
                c_nl, c_col = nl_for_line, col_prefix_line
            elif first:
                c_nl, c_col = 0, ""
            else:
                c_nl, c_col = split_leading_gap(source, line_last, c_start)
            tokens.append(CodeToken(type=PointerKind.C.value, value=comment_text, nl=c_nl, col_prefix=c_col))
            last_end = c_start + len(comment_text)

    while len(indent_stack) > 1:
        tokens.append(CodeToken(block="close", nl=0, visual_style="indent"))
        indent_stack.pop()

    trailing = extract_trailing_whitespace(source, last_end)
    return TokenizeResult(tokens=tokens, trailing_whitespace=trailing)


def tokenize_html(source: str) -> TokenizeResult:
    assert_no_surrogates(source)
    source = unicodedata.normalize("NFC", normalize_line_endings(source))
    tag_re = re.compile(
        r"<!--[\s\S]*?-->|<\/([A-Za-z_][\w:.\-]*)\s*>|<([A-Za-z_][\w:.\-]*)((?:\s+[^<>]*?)?)\s*(\/?)>|[^<]+"
    )
    tokens: list[CodeToken] = []
    last = 0
    pending_nl = 0
    trailing_buf = ""

    for m in tag_re.finditer(source):
        raw = m.group(0)

        if raw.strip() == "":
            if m.end() >= len(source):
                trailing_buf += raw
            else:
                pending_nl += raw.count("\n")
            last = m.end()
            continue

        nl, col_prefix = split_leading_gap(source, last, m.start())
        nl += pending_nl
        pending_nl = 0
        last = m.end()

        if raw.startswith("<!--"):
            tokens.append(
                CodeToken(type=PointerKind.C.value, value=raw, nl=nl, col_prefix=col_prefix)
            )
            continue

        if m.group(1):
            close_text = f"</{m.group(1)}>"
            tokens.append(
                CodeToken(
                    block="close",
                    value=close_text,
                    nl=nl,
                    col_prefix=col_prefix,
                    visual_style="tag",
                )
            )
        elif m.group(2):
            name = m.group(2)
            tag_text = raw.strip()
            self_close = m.group(4) == "/" or name.upper() in VOID_HTML_TAGS
            tokens.append(
                CodeToken(
                    block="open",
                    value="",
                    open_syntax=name,
                    nl=0,
                    col_prefix="",
                    visual_style="tag",
                )
            )
            tokens.append(
                CodeToken(type=PointerKind.C.value, value=tag_text, nl=nl, col_prefix=col_prefix)
            )
            if self_close:
                tokens.append(CodeToken(block="close", value="", nl=0, visual_style="tag"))
        else:
            text = raw
            if text.strip():
                tokens.append(CodeToken(type=PointerKind.S.value, value=text, nl=nl, col_prefix=col_prefix))

    trailing = trailing_buf or extract_trailing_whitespace(source, last)
    return TokenizeResult(tokens=tokens, trailing_whitespace=trailing)


def tokenize_source(source: str, language_id: str) -> TokenizeResult:
    spec = language_for_id(language_id)
    if spec.block_style == "indent":
        return tokenize_indent(source, language_id)
    if spec.block_style == "tag":
        return tokenize_html(source)
    return tokenize_brace(source, language_id)
