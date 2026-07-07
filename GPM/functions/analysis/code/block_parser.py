"""Block-Parser — nur ParseDomain.CODE (Absicherung A)."""

from __future__ import annotations

from analysis.blocks.context import ParseContext, ParseDomain
from analysis.blocks.kinds import PointerKind
from analysis.blocks.node import BlockLevel, BlockNode, PointerRef
from analysis.blocks.registry import DocumentRegistry
from analysis.code.envelope import BlockEnvelope, CloseRole, envelope_from_token_visual
from analysis.code.intern import intern_scalar_token
from analysis.code.languages import language_for_id
from analysis.code.rules import absorb_close_into_embedded_tag, closes_matching_block, rules_for
from analysis.code.tokens import CodeToken
from analysis.code.tokenizer import tokenize_source


def _envelope_visual_name(env: BlockEnvelope) -> str:
    if env is BlockEnvelope.BRACKET:
        return "bracket"
    if env is BlockEnvelope.TAG:
        return "tag"
    if env is BlockEnvelope.KEYWORD:
        return "keyword"
    if env is BlockEnvelope.INDENT:
        return "indent"
    return "brace"


def _open_syntax_for_node(tok: CodeToken) -> str:
    if tok.open_syntax:
        return tok.open_syntax
    if tok.value:
        return tok.value
    return ""


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
    root.meta["rule_language"] = language_id
    stack: list[BlockNode] = [root]
    block_id = 1
    tail_attach: BlockNode | None = None

    for tok in result.tokens:
        if tail_attach is not None:
            if tok.nl == 0 and tok.block is None:
                for ref in intern_scalar_token(tok, registry, context):
                    tail_attach.sequence.append(ref)
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
            env = tok.envelope or envelope_from_token_visual(tok.visual_style)
            if env is None:
                env = rules_for(language_id).envelope
            child.meta["envelope"] = int(env)
            child.meta["visual_style"] = _envelope_visual_name(env)
            open_syn = _open_syntax_for_node(tok)
            if open_syn:
                child.meta["open_syntax"] = open_syn
            embedded = tok.meta.get("embedded_language")
            if embedded:
                child.meta["embedded_language"] = embedded
            child.meta["rule_language"] = embedded or language_id
            if tok.meta.get("pair_index") is not None:
                child.meta["pair_index"] = tok.meta["pair_index"]
            if env is BlockEnvelope.INDENT and (tok.nl or tok.col_prefix):
                child.meta["prefix_nl"] = tok.nl
                child.meta["prefix_col"] = tok.col_prefix
            if tok.value:
                for ref in intern_scalar_token(tok, registry, context):
                    child.sequence.append(ref)
            stack[-1].children.append(child)
            stack[-1].sequence.append(
                PointerRef(
                    kind=PointerKind.SYS,
                    ptr_id=0,
                    meta={"child_block_id": child.block_id},
                )
            )
            stack.append(child)
            continue

        if tok.block == "close":
            if len(stack) > 1:
                top = stack[-1]
                if closes_matching_block(top, tok, module_lang=language_id):
                    if tok.value or tok.close_role is not CloseRole.INDENT:
                        for ref in intern_scalar_token(tok, registry, context):
                            top.sequence.append(ref)
                    tail_attach = stack.pop()
                elif absorb_close_into_embedded_tag(top, tok):
                    for ref in intern_scalar_token(tok, registry, context):
                        top.sequence.append(ref)
                else:
                    for ref in intern_scalar_token(tok, registry, context):
                        top.sequence.append(ref)
                    tail_attach = stack.pop()
            continue

        for ref in intern_scalar_token(tok, registry, context):
            stack[-1].sequence.append(ref)

    return root
