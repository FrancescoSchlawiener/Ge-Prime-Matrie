"""Block-Parser — nur ParseDomain.CODE (Absicherung A)."""

from __future__ import annotations

from analysis.blocks.context import COrigin, ParseContext, ParseDomain
from analysis.blocks.kinds import PointerKind
from analysis.blocks.node import BlockLevel, BlockNode, PointerRef
from analysis.blocks.registry import DocumentRegistry
from analysis.code.languages import language_for_id
from analysis.code.tokens import CodeToken
from analysis.code.tokenizer import tokenize_source


def _intern_token(
    tok: CodeToken,
    registry: DocumentRegistry,
    context: ParseContext,
) -> PointerRef:
    if tok.block == "open":
        value = tok.value or "OPEN"
        ptr = registry.intern(PointerKind.C, value, context=context, origin=COrigin.CODE)
        meta = {"open_syntax": tok.open_syntax or tok.value}
        if tok.meta.get("expectedCloser"):
            meta["expectedCloser"] = tok.meta["expectedCloser"]
        return PointerRef(
            kind=PointerKind.C,
            ptr_id=ptr,
            nl=tok.nl,
            col_prefix=tok.col_prefix,
            meta=meta,
        )
    if tok.block == "close":
        value = tok.value or "CLOSE"
        ptr = registry.intern(PointerKind.SYS, value, context=context, origin=COrigin.CODE)
        return PointerRef(
            kind=PointerKind.SYS,
            ptr_id=ptr,
            nl=tok.nl,
            col_prefix=tok.col_prefix,
            meta={"close_syntax": tok.close_syntax or tok.value},
        )
    kind = PointerKind(tok.type or "S")
    if kind is PointerKind.N:
        ptr = registry.intern(kind, int(tok.value), context=context)
    else:
        ptr = registry.intern(kind, tok.value, context=context)
    return PointerRef(kind=kind, ptr_id=ptr, nl=tok.nl, col_prefix=tok.col_prefix)


def parse_code_blocks(
    source: str,
    language_id: str,
    registry: DocumentRegistry,
) -> BlockNode:
    context = ParseContext(domain=ParseDomain.CODE, language_id=language_id)
    spec = language_for_id(language_id)
    result = tokenize_source(source, language_id)
    root = BlockNode(block_id=0, level=BlockLevel.MODULE)
    root.meta["trailing_whitespace"] = result.trailing_whitespace
    stack: list[BlockNode] = [root]
    block_id = 1
    tail_attach: BlockNode | None = None

    for tok in result.tokens:
        if tail_attach is not None:
            if tok.nl == 0 and tok.block is None:
                tail_attach.sequence.append(_intern_token(tok, registry, context))
                tail_attach = None
                continue
            tail_attach = None

        if tok.block == "open":
            child = BlockNode(
                block_id=block_id,
                level=BlockLevel.CODE_BLOCK,
                parent_id=stack[-1].block_id,
            )
            block_id += 1
            child.meta["visual_style"] = tok.visual_style or spec.block_style
            if tok.open_syntax:
                child.meta["open_syntax"] = tok.open_syntax
            if tok.visual_style == "indent" and (tok.nl or tok.col_prefix):
                child.meta["prefix_nl"] = tok.nl
                child.meta["prefix_col"] = tok.col_prefix
            if tok.value:
                ref = _intern_token(tok, registry, context)
                child.sequence.append(ref)
            stack[-1].children.append(child)
            stack.append(child)
            continue
        if tok.block == "close":
            if len(stack) > 1:
                if tok.value or tok.visual_style != "indent":
                    ref = _intern_token(tok, registry, context)
                    stack[-1].sequence.append(ref)
                tail_attach = stack.pop()
            continue
        ref = _intern_token(tok, registry, context)
        stack[-1].sequence.append(ref)

    return root
