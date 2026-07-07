"""Einziges Nadelöhr: CodeToken → PointerRef(s) in DocumentRegistry."""

from __future__ import annotations

from analysis.blocks.context import COrigin, ParseContext
from analysis.blocks.kinds import PointerKind
from analysis.blocks.node import PointerRef
from analysis.blocks.registry import DocumentRegistry
from analysis.code.tokens import CodeToken
from gpm_types.di.relation import parse_decimal
from gpm_types.hi.segments import parse_hi_segments_code


def intern_digit(digit: int, registry: DocumentRegistry, context: ParseContext) -> int:
    if not 0 <= digit <= 9:
        raise ValueError(f"N(I) Code-Pfad: nur Ziffern 0–9, got {digit}")
    return registry.intern(PointerKind.N, digit, context=context)


def intern_n_literal(
    text: str,
    registry: DocumentRegistry,
    context: ParseContext,
) -> int:
    """Ziffernkette → atomarer oder Tupel-N-Pointer in der Registry."""
    if not text or not all(ch.isdigit() for ch in text):
        raise ValueError(f"Kein N-Literal: {text!r}")
    if len(text) == 1:
        return intern_digit(int(text), registry, context)
    digit_ptrs = tuple(intern_digit(int(ch), registry, context) for ch in text)
    return registry.intern(PointerKind.N, digit_ptrs, context=context)


def intern_n_from_int(
    value: int,
    registry: DocumentRegistry,
    context: ParseContext,
) -> int:
    return intern_n_literal(str(value), registry, context)


def intern_n_digits(
    raw: str,
    nl: int,
    col_prefix: str,
    registry: DocumentRegistry,
    context: ParseContext,
) -> list[PointerRef]:
    """11 → ein PointerRef auf Tupel-(ptr_1, ptr_1); 1 → atomarer Ziffer-Pointer."""
    text = raw or ""
    bigint = False
    if text.endswith("n") or text.endswith("N"):
        bigint = True
        text = text[:-1]
    if not text or not all(ch.isdigit() for ch in text):
        raise ValueError(f"Kein N-Literal für Ziffern-Intern: {raw!r}")
    ptr = intern_n_literal(text, registry, context)
    meta: dict = {}
    if bigint:
        meta["bigint"] = True
    return [
        PointerRef(
            kind=PointerKind.N,
            ptr_id=ptr,
            nl=nl,
            col_prefix=col_prefix,
            meta=meta,
        )
    ]


def intern_d_decimal(
    raw: str,
    nl: int,
    col_prefix: str,
    registry: DocumentRegistry,
    context: ParseContext,
) -> PointerRef:
    rel = parse_decimal(raw)
    triple_key = f"{rel.whole}:{rel.den_reduced}:{rel.ggt}"
    ptr = registry.intern_d_code(raw, triple_key, rel, context=context)
    return PointerRef(kind=PointerKind.D, ptr_id=ptr, nl=nl, col_prefix=col_prefix)


def intern_block_open(
    tok: CodeToken,
    registry: DocumentRegistry,
    context: ParseContext,
) -> PointerRef:
    value = tok.value or "OPEN"
    ptr = registry.intern(PointerKind.C, value, context=context, origin=COrigin.CODE)
    meta: dict = {"open_syntax": tok.open_syntax or tok.value}
    if tok.meta.get("pair_index") is not None:
        meta["pair_index"] = tok.meta["pair_index"]
    return PointerRef(
        kind=PointerKind.C,
        ptr_id=ptr,
        nl=tok.nl,
        col_prefix=tok.col_prefix,
        meta=meta,
    )


def intern_block_close(
    tok: CodeToken,
    registry: DocumentRegistry,
    context: ParseContext,
) -> PointerRef:
    value = tok.value or "CLOSE"
    ptr = registry.intern(PointerKind.SYS, value, context=context, origin=COrigin.CODE)
    meta: dict = {"close_syntax": tok.close_syntax or tok.value}
    if tok.meta.get("pair_index") is not None:
        meta["pair_index"] = tok.meta["pair_index"]
    return PointerRef(
        kind=PointerKind.SYS,
        ptr_id=ptr,
        nl=tok.nl,
        col_prefix=tok.col_prefix,
        meta=meta,
    )


def intern_scalar_token(
    tok: CodeToken,
    registry: DocumentRegistry,
    context: ParseContext,
) -> list[PointerRef]:
    if tok.block == "open":
        return [intern_block_open(tok, registry, context)]
    if tok.block == "close":
        return [intern_block_close(tok, registry, context)]
    kind = PointerKind(tok.type or "S")
    if kind is PointerKind.N:
        return intern_n_digits(str(tok.value), tok.nl, tok.col_prefix, registry, context)
    if kind is PointerKind.D:
        return [intern_d_decimal(str(tok.value), tok.nl, tok.col_prefix, registry, context)]
    if kind is PointerKind.H:
        ptr = registry.intern_h_code(str(tok.value), context=context)
        return [
            PointerRef(
                kind=PointerKind.H,
                ptr_id=ptr,
                nl=tok.nl,
                col_prefix=tok.col_prefix,
            )
        ]
    ptr = registry.intern(kind, tok.value, context=context)
    return [PointerRef(kind=kind, ptr_id=ptr, nl=tok.nl, col_prefix=tok.col_prefix)]
