"""Scalar-Lexer — Astral-Plane-sicher, nl/col_prefix/EOF (Absicherung B)."""

from __future__ import annotations

import re
import unicodedata

from alphabets.unicode_utils import assert_no_surrogates
from analysis.blocks.context import ParseContext, ParseDomain
from analysis.blocks.kinds import PointerKind
from analysis.code.envelope import BlockEnvelope, CloseRole, envelope_from_token_visual
from analysis.code.comments import find_comment_at
from analysis.code.languages import VOID_HTML_TAGS, language_for_id
from analysis.code.tokens import (
    CodeToken,
    TokenizeResult,
    extract_trailing_whitespace,
    split_leading_gap,
)

_TOKEN_CORE = re.compile(
    r"(/(?:\\.|[^/\\\r\n])+/[gimsuy]*)"
    r"|(@[\w-]+)"
    r"|(\b[\w\u0080-\U0010FFFF]+\b)"
    r"|([0-9]+n)"
    r"|([0-9]+\.[0-9]+|[0-9]+)"
    r"|([{}()\[\]])"
    r"|(=>|\?\?|\?\.|===|!==|\+\+|--|<<|>>|[+\-*/=<>!&|^%?:]+)"
    r"|([#.,;])"
)


def normalize_line_endings(source: str) -> str:
    return source.replace("\r\n", "\n").replace("\r", "\n")


def _keyword_match(value: str, spec) -> bool:
    low = value.lower()
    return low in spec.keywords_lower


_CSS_LANGS = frozenset({"css", "scss", "sass", "less"})


def classify_code_token(value: str, *, context: ParseContext, language_id: str) -> PointerKind:
    if context.domain is ParseDomain.NL:
        return PointerKind.S
    if value.startswith(('"', "'", "`")):
        return PointerKind.S
    if value.startswith("//") or value.startswith("/*") or value.startswith("--"):
        return PointerKind.C
    if re.fullmatch(r"[+-]?\d+", value):
        if language_id in _CSS_LANGS and re.fullmatch(r"0\d+", value):
            return PointerKind.S
        return PointerKind.N
    if re.fullmatch(r"[+-]?\d+n", value):
        return PointerKind.N
    if re.fullmatch(r"[+-]?\d+\.\d+", value):
        return PointerKind.D
    spec = language_for_id(language_id)
    if _keyword_match(value, spec):
        return PointerKind.C
    if value in "(){}[];,.#":
        return PointerKind.C
    if re.fullmatch(r"(=>|\?\?|\?\.|===|!==|\+\+|--|<<|>>|[+\-*/=<>!&|^%?:]+)", value):
        return PointerKind.C
    if re.fullmatch(r"/(?:\\.|[^/\\\r\n])+/[gimsuy]*", value):
        return PointerKind.C
    if language_id in _CSS_LANGS:
        return PointerKind.S
    from gpm_types.classify import PayloadKind, classify_token

    try:
        if classify_token(value) is PayloadKind.H:
            return PointerKind.H
    except ValueError:
        pass
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


def _find_next_comment(source: str, pos: int, comment_style: str) -> tuple[str, int, int] | None:
    if comment_style not in ("c", "sql"):
        return None
    n = len(source)
    p = pos
    while p < n:
        hit = find_comment_at(source, p, comment_style)
        if hit:
            text, c_start, c_end = hit
            if c_start >= pos:
                return hit
        if comment_style == "c":
            i1 = source.find("//", p + 1)
            i2 = source.find("/*", p + 1)
            candidates = [i for i in (i1, i2) if i != -1]
        else:
            i1 = source.find("--", p + 1)
            i2 = source.find("/*", p + 1)
            candidates = [i for i in (i1, i2) if i != -1]
        if not candidates:
            return None
        p = min(candidates)
    return None


def _scan_quoted_string(source: str, pos: int) -> tuple[str, int] | None:
    if pos >= len(source):
        return None
    quote = source[pos]
    if quote not in '"\'':
        return None
    i = pos + 1
    while i < len(source):
        ch = source[i]
        if ch == "\\":
            i += 2
            continue
        if ch == quote:
            return source[pos : i + 1], i + 1
        i += 1
    return None


def _scan_template_literal(source: str, pos: int) -> tuple[str, int] | None:
    if pos >= len(source) or source[pos] != "`":
        return None
    i = pos + 1
    while i < len(source):
        ch = source[i]
        if ch == "\\":
            i += 2
            continue
        if ch == "`":
            return source[pos : i + 1], i + 1
        if ch == "$" and i + 1 < len(source) and source[i + 1] == "{":
            i += 2
            depth = 1
            while i < len(source) and depth > 0:
                c = source[i]
                if c == "{":
                    depth += 1
                    i += 1
                elif c == "}":
                    depth -= 1
                    i += 1
                elif c == "/":
                    reg_m = re.match(r"/(?:\\.|[^/\\\r\n])+/[gimsuy]*", source[i:])
                    if reg_m:
                        i += reg_m.end()
                    else:
                        i += 1
                elif c in '"\'':
                    hit = _scan_quoted_string(source, i)
                    if hit is None:
                        return None
                    _, i = hit
                elif c == "`":
                    hit = _scan_template_literal(source, i)
                    if hit is None:
                        return None
                    _, i = hit
                else:
                    i += 1
            continue
        i += 1
    return None


def _find_next_string_or_template(source: str, pos: int) -> tuple[str, int, int] | None:
    if pos >= len(source):
        return None
    ch = source[pos]
    if ch in '"\'':
        hit = _scan_quoted_string(source, pos)
    elif ch == "`":
        hit = _scan_template_literal(source, pos)
    else:
        return None
    if hit is None:
        return None
    text, end = hit
    return text, pos, end


_CSS_HEX_COLOR = re.compile(r"#[0-9a-fA-F]{3,8}(?![0-9a-fA-F])")


def _try_emit_css_hex_color(
    tokens: list[CodeToken],
    source: str,
    pos: int,
    last: int,
    language_id: str,
    ctx: ParseContext,
) -> int | None:
    """CSS: #RRGGBB als ein S-Token — kein isolierter Hex-Fragment-S."""
    if language_id not in _CSS_LANGS:
        return None
    m = _CSS_HEX_COLOR.match(source, pos)
    if not m:
        return None
    val = m.group(0)
    nl, col_prefix = split_leading_gap(source, last, pos)
    tokens.append(CodeToken(type=PointerKind.S.value, value=val, nl=nl, col_prefix=col_prefix))
    return m.end()


def _emit_scalar(
    tokens: list[CodeToken],
    val: str,
    nl: int,
    col_prefix: str,
    ctx: ParseContext,
    language_id: str,
) -> None:
    kind = classify_code_token(val, context=ctx, language_id=language_id)
    tokens.append(CodeToken(type=kind.value, value=val, nl=nl, col_prefix=col_prefix))


def _emit_brace_delim(
    tokens: list[CodeToken],
    val: str,
    nl: int,
    col_prefix: str,
    *,
    flat: bool,
) -> None:
    if flat:
        tokens.append(CodeToken(type=PointerKind.C.value, value=val, nl=nl, col_prefix=col_prefix))
        return
    if val == "{":
        tokens.append(
            CodeToken(
                block="open",
                value=val,
                nl=nl,
                col_prefix=col_prefix,
                envelope=BlockEnvelope.BRACE,
                open_syntax=val,
            )
        )
    elif val == "[":
        tokens.append(
            CodeToken(
                block="open",
                value=val,
                nl=nl,
                col_prefix=col_prefix,
                envelope=BlockEnvelope.BRACKET,
                open_syntax=val,
            )
        )
    elif val == "}":
        tokens.append(
            CodeToken(
                block="close",
                value=val,
                nl=nl,
                col_prefix=col_prefix,
                envelope=BlockEnvelope.BRACE,
                close_role=CloseRole.BRACE,
                close_syntax=val,
            )
        )
    elif val == "]":
        tokens.append(
            CodeToken(
                block="close",
                value=val,
                nl=nl,
                col_prefix=col_prefix,
                envelope=BlockEnvelope.BRACKET,
                close_role=CloseRole.BRACKET,
                close_syntax=val,
            )
        )
    elif val in "()":
        tokens.append(CodeToken(type=PointerKind.C.value, value=val, nl=nl, col_prefix=col_prefix))
    else:
        tokens.append(CodeToken(type=PointerKind.C.value, value=val, nl=nl, col_prefix=col_prefix))


def _lex_scanned(
    source: str,
    language_id: str,
    *,
    flat: bool = False,
    keyword: bool = False,
) -> TokenizeResult:
    assert_no_surrogates(source)
    source = unicodedata.normalize("NFC", normalize_line_endings(source))
    spec = language_for_id(language_id)
    ctx = ParseContext(ParseDomain.CODE, language_id)
    tokens: list[CodeToken] = []
    last = 0
    pos = 0
    n = len(source)
    comment_style = spec.comment_style

    open_closers: dict[str, tuple[str, int]] = {}
    closers: dict[str, int] = {}
    if keyword:
        for pair_idx, (opener, closer) in enumerate(spec.block_pairs):
            open_closers[opener.lower()] = (closer.lower(), pair_idx)
            closers[closer.lower()] = pair_idx

    while pos < n:
        comm = _find_next_comment(source, pos, comment_style)
        str_hit = _find_next_string_or_template(source, pos)
        tok_m = _TOKEN_CORE.search(source, pos)

        if tok_m is not None and tok_m.start() > pos:
            for i in range(pos, tok_m.start()):
                if source[i] in '"\'`':
                    str_hit = _find_next_string_or_template(source, i)
                    break

        next_pos = n
        next_kind = None
        if comm is not None:
            next_pos = comm[1]
            next_kind = "comm"
        if str_hit is not None and str_hit[1] < next_pos:
            next_pos = str_hit[1]
            next_kind = "str"
        if tok_m is not None and tok_m.start() < next_pos:
            next_pos = tok_m.start()
            next_kind = "tok"

        if next_kind is None:
            break

        if language_id in _CSS_LANGS and next_kind == "tok" and source[pos : pos + 1] == "#":
            hex_end = _try_emit_css_hex_color(tokens, source, pos, last, language_id, ctx)
            if hex_end is not None:
                last = hex_end
                pos = hex_end
                continue

        if next_kind == "comm":
            text, c_start, c_end = comm
            nl, col_prefix = split_leading_gap(source, last, c_start)
            tokens.append(
                CodeToken(type=PointerKind.C.value, value=text, nl=nl, col_prefix=col_prefix)
            )
            last = c_end
            pos = c_end
            continue

        if next_kind == "str":
            text, s_start, s_end = str_hit
            nl, col_prefix = split_leading_gap(source, last, s_start)
            _emit_scalar(tokens, text, nl, col_prefix, ctx, language_id)
            last = s_end
            pos = s_end
            continue

        val = tok_m.group(0)
        if not val.strip():
            pos = tok_m.end()
            continue

        nl, col_prefix = split_leading_gap(source, last, tok_m.start())
        last = tok_m.end()
        pos = tok_m.end()

        if (
            tokens
            and tokens[-1].type == PointerKind.C.value
            and tokens[-1].value == "#"
            and re.fullmatch(r"[0-9A-Fa-f]{3,8}", val)
        ):
            prev = tokens.pop()
            tokens.append(
                CodeToken(
                    type=PointerKind.S.value,
                    value="#" + val,
                    nl=prev.nl,
                    col_prefix=prev.col_prefix,
                )
            )
            continue

        low = val.lower()
        if keyword and low in open_closers:
            _closer, pair_idx = open_closers[low]
            tokens.append(
                CodeToken(
                    block="open",
                    value=val,
                    nl=nl,
                    col_prefix=col_prefix,
                    envelope=BlockEnvelope.KEYWORD,
                    open_syntax=val,
                    meta={"pair_index": pair_idx},
                )
            )
        elif keyword and low in closers:
            tokens.append(
                CodeToken(
                    block="close",
                    value=val,
                    nl=nl,
                    col_prefix=col_prefix,
                    envelope=BlockEnvelope.KEYWORD,
                    close_role=CloseRole.KEYWORD,
                    close_syntax=val,
                    meta={"pair_index": closers[low]},
                )
            )
        elif val in "{()}[]":
            _emit_brace_delim(tokens, val, nl, col_prefix, flat=flat)
        else:
            _emit_scalar(tokens, val, nl, col_prefix, ctx, language_id)

    trailing = extract_trailing_whitespace(source, last)
    return TokenizeResult(tokens=tokens, trailing_whitespace=trailing)


def tokenize_brace(source: str, language_id: str) -> TokenizeResult:
    return _lex_scanned(source, language_id, flat=False, keyword=False)


def tokenize_flat(source: str, language_id: str) -> TokenizeResult:
    return _lex_scanned(source, language_id, flat=True, keyword=False)


def tokenize_keyword(source: str, language_id: str) -> TokenizeResult:
    return _lex_scanned(source, language_id, flat=False, keyword=True)


def _scan_indent_code_part(
    source: str,
    code_part: str,
    content_start: int,
    *,
    first: bool,
    opened_this_line: bool,
    nl_for_line: int,
    col_prefix_line: str,
    tokens: list[CodeToken],
    ctx: ParseContext,
    language_id: str,
    line_last: int,
) -> tuple[bool, int, int]:
    """Robuster Scanner: Strings/Literale vor _TOKEN_CORE (kein Gap mit ")."""
    pos_abs = content_start
    end_abs = content_start + len(code_part)
    last_end = line_last
    while pos_abs < end_abs:
        str_hit = _find_next_string_or_template(source, pos_abs)
        tok_m = _TOKEN_CORE.search(source, pos_abs)
        if tok_m is not None and tok_m.start() >= end_abs:
            tok_m = None

        if tok_m is not None and tok_m.start() > pos_abs:
            for i in range(pos_abs, min(tok_m.start(), end_abs)):
                if source[i] in '"\'`':
                    str_hit = _find_next_string_or_template(source, i)
                    break

        next_kind = None
        next_abs = end_abs

        if str_hit is not None:
            _text, s_start, _s_end = str_hit
            if pos_abs <= s_start < end_abs:
                next_kind = "str"
                next_abs = s_start

        if tok_m is not None and tok_m.start() < next_abs:
            next_kind = "tok"
            next_abs = tok_m.start()

        if next_kind is None:
            break

        if next_kind == "str":
            text, s_start, s_end = str_hit
            if first and not opened_this_line:
                t_nl, t_col = nl_for_line, col_prefix_line
            elif first:
                t_nl, t_col = 0, ""
            else:
                t_nl, t_col = split_leading_gap(source, last_end, s_start)
            first = False
            _emit_scalar(tokens, text, t_nl, t_col, ctx, language_id)
            last_end = s_end
            pos_abs = s_end
            continue

        val = tok_m.group(0)
        if not val.strip():
            pos_abs = tok_m.end()
            continue
        abs_start = tok_m.start()
        abs_end = tok_m.end()
        if first and not opened_this_line:
            t_nl, t_col = nl_for_line, col_prefix_line
        elif first:
            t_nl, t_col = 0, ""
        else:
            t_nl, t_col = split_leading_gap(source, last_end, abs_start)
        first = False
        kind = classify_code_token(val, context=ctx, language_id=language_id)
        tokens.append(CodeToken(type=kind.value, value=val, nl=t_nl, col_prefix=t_col))
        last_end = abs_end
        pos_abs = abs_end

    return first, line_last if last_end == line_last else last_end, last_end


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
                    envelope=BlockEnvelope.INDENT,
                )
            )
            indent_stack.append(indent)
            opened_this_line = True
            nl_for_line = 0
        else:
            while indent < indent_stack[-1]:
                tokens.append(
                    CodeToken(block="close", nl=0, envelope=BlockEnvelope.INDENT, close_role=CloseRole.INDENT)
                )
                indent_stack.pop()

        content_start = line_start + len(raw_line) - len(trimmed)
        code_part = trimmed
        comment_text: str | None = None
        if spec.comment_style == "hash":
            from analysis.code.comments import extract_hash_comment

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
        first, line_last, last_end = _scan_indent_code_part(
            source,
            code_part,
            content_start,
            first=first,
            opened_this_line=opened_this_line,
            nl_for_line=nl_for_line,
            col_prefix_line=col_prefix_line,
            tokens=tokens,
            ctx=ctx,
            language_id=language_id,
            line_last=line_last,
        )

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
        tokens.append(
            CodeToken(block="close", nl=0, envelope=BlockEnvelope.INDENT, close_role=CloseRole.INDENT)
        )
        indent_stack.pop()

    trailing = extract_trailing_whitespace(source, last_end)
    return TokenizeResult(tokens=tokens, trailing_whitespace=trailing)


_HTML_RAWTEXT: dict[str, str] = {"script": "js", "style": "css"}
_RAWTEXT_CLOSE_RE: dict[str, re.Pattern[str]] = {
    "script": re.compile(r"</script\s*>", re.IGNORECASE),
    "style": re.compile(r"</style\s*>", re.IGNORECASE),
}


def _find_rawtext_close(source: str, pos: int, tag: str) -> re.Match[str]:
    pat = _RAWTEXT_CLOSE_RE[tag.lower()]
    m = pat.search(source, pos)
    if not m:
        raise ValueError(f"Unclosed <{tag}> element")
    return m


def _merge_rawtext_body(
    tokens: list[CodeToken],
    body: str,
    lang_id: str,
    *,
    first_nl: int = 0,
    first_col: str = "",
) -> str:
    """Tokenize embedded script/style body; return trailing whitespace before close tag."""
    inner = tokenize_source(body, lang_id)
    for i, tok in enumerate(inner.tokens):
        if i == 0 and (first_nl or first_col):
            tok.nl = first_nl + tok.nl
            tok.col_prefix = first_col + tok.col_prefix
        tokens.append(tok)
    return inner.trailing_whitespace


def tokenize_html(source: str) -> TokenizeResult:
    assert_no_surrogates(source)
    source = unicodedata.normalize("NFC", normalize_line_endings(source))
    tag_re = re.compile(
        r"<!--[\s\S]*?-->"
        r"|<\?[\s\S]*?\?>"
        r"|<![^>]+>"
        r"|<\/([A-Za-z_][\w:.\-]*)\s*>"
        r"|<([A-Za-z_][\w:.\-]*)((?:\s+[^<>]*?)?)\s*(\/?)>"
        r"|[^<]+"
    )
    tokens: list[CodeToken] = []
    last = 0
    trailing_buf = ""
    pos = 0
    n = len(source)

    while pos < n:
        m = tag_re.search(source, pos)
        if not m:
            tail = source[pos:]
            if tail.strip() == "":
                trailing_buf += tail
            elif tail.strip():
                nl, col_prefix = split_leading_gap(source, last, n)
                tokens.append(CodeToken(type=PointerKind.S.value, value=tail, nl=nl, col_prefix=col_prefix))
            last = n
            break

        raw = m.group(0)

        if raw.strip() == "":
            if m.end() >= n:
                trailing_buf += raw
            pos = m.end()
            continue

        nl, col_prefix = split_leading_gap(source, last, m.start())
        last = m.end()
        pos = m.end()

        if raw.startswith("<!--") or raw.startswith("<?") or raw.startswith("<!"):
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
                    envelope=BlockEnvelope.TAG,
                    close_role=CloseRole.TAG,
                    close_syntax=close_text,
                )
            )
            continue

        if m.group(2):
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
                    envelope=BlockEnvelope.TAG,
                )
            )
            tokens.append(
                CodeToken(type=PointerKind.C.value, value=tag_text, nl=nl, col_prefix=col_prefix)
            )
            if self_close:
                tokens.append(
                    CodeToken(
                        block="close",
                        value="",
                        nl=0,
                        envelope=BlockEnvelope.TAG,
                        close_role=CloseRole.TAG,
                    )
                )
                continue

            raw_lang = _HTML_RAWTEXT.get(name.lower())
            if raw_lang is not None:
                body_start = m.end()
                close_m = _find_rawtext_close(source, body_start, name)
                body = source[body_start : close_m.start()]
                if body.strip():
                    for t in reversed(tokens):
                        if t.block == "open" and t.open_syntax and t.open_syntax.lower() == name.lower():
                            t.meta["embedded_language"] = raw_lang
                            break
                    inner_trail = _merge_rawtext_body(tokens, body, raw_lang)
                else:
                    inner_trail = ""
                close_nl, close_col = split_leading_gap(source, body_start + len(body), close_m.start())
                close_nl += inner_trail.count("\n")
                close_text = source[close_m.start() : close_m.end()]
                tokens.append(
                    CodeToken(
                        block="close",
                        value=close_text,
                        nl=close_nl,
                        col_prefix=close_col,
                        envelope=BlockEnvelope.TAG,
                        close_role=CloseRole.TAG,
                        close_syntax=close_text,
                    )
                )
                last = close_m.end()
                pos = close_m.end()
            continue

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
    if spec.block_style == "keyword":
        return tokenize_keyword(source, language_id)
    if spec.block_style == "flat":
        return tokenize_flat(source, language_id)
    return tokenize_brace(source, language_id)
