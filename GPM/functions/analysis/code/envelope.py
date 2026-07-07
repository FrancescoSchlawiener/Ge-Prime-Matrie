"""Typisierte Block-Umschließer — kein String-Vergleich im Parser."""

from __future__ import annotations

from enum import IntEnum


class BlockEnvelope(IntEnum):
    FLAT = 0
    BRACE = 1
    BRACKET = 2
    TAG = 3
    KEYWORD = 4
    INDENT = 5


class CloseRole(IntEnum):
    BRACE = 1
    BRACKET = 2
    TAG = 3
    KEYWORD = 4
    INDENT = 5


_BLOCK_STYLE_TO_ENVELOPE: dict[str, BlockEnvelope] = {
    "flat": BlockEnvelope.FLAT,
    "brace": BlockEnvelope.BRACE,
    "tag": BlockEnvelope.TAG,
    "keyword": BlockEnvelope.KEYWORD,
    "indent": BlockEnvelope.INDENT,
}


def envelope_from_block_style(block_style: str) -> BlockEnvelope:
    return _BLOCK_STYLE_TO_ENVELOPE.get(block_style, BlockEnvelope.BRACE)


def close_role_for_envelope(envelope: BlockEnvelope) -> CloseRole | None:
    if envelope is BlockEnvelope.BRACE:
        return CloseRole.BRACE
    if envelope is BlockEnvelope.BRACKET:
        return CloseRole.BRACKET
    if envelope is BlockEnvelope.TAG:
        return CloseRole.TAG
    if envelope is BlockEnvelope.KEYWORD:
        return CloseRole.KEYWORD
    if envelope is BlockEnvelope.INDENT:
        return CloseRole.INDENT
    return None


def envelope_from_token_visual(visual_style: str | None, *, is_bracket: bool = False) -> BlockEnvelope | None:
    """Legacy-Hilfe beim Tokenizer-Übergang (visual_style → envelope)."""
    if visual_style == "tag":
        return BlockEnvelope.TAG
    if visual_style == "keyword":
        return BlockEnvelope.KEYWORD
    if visual_style == "indent":
        return BlockEnvelope.INDENT
    if visual_style == "bracket" or is_bracket:
        return BlockEnvelope.BRACKET
    if visual_style is None and not is_bracket:
        return BlockEnvelope.BRACE
    return None


def parse_envelope_meta(meta: dict) -> BlockEnvelope | None:
    raw = meta.get("envelope")
    if raw is None:
        vs = meta.get("visual_style")
        if vs == "tag":
            return BlockEnvelope.TAG
        if vs == "keyword":
            return BlockEnvelope.KEYWORD
        if vs == "indent":
            return BlockEnvelope.INDENT
        if vs == "bracket":
            return BlockEnvelope.BRACKET
        if vs == "brace" or vs is None:
            if meta.get("open_syntax") or meta.get("rule_language"):
                return BlockEnvelope.BRACE
        return None
    if isinstance(raw, BlockEnvelope):
        return raw
    if isinstance(raw, int):
        return BlockEnvelope(raw)
    name = str(raw).upper()
    if name in BlockEnvelope.__members__:
        return BlockEnvelope[name]
    return None
