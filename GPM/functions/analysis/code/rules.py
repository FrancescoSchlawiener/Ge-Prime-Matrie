"""Sprachgetrennte Block-Regeln — Close-Matching über Enums."""

from __future__ import annotations

from dataclasses import dataclass

from analysis.blocks.node import BlockNode
from analysis.code.envelope import (
    BlockEnvelope,
    CloseRole,
    close_role_for_envelope,
    envelope_from_block_style,
    parse_envelope_meta,
)
from analysis.code.languages import language_for_id
from analysis.code.tokens import CodeToken


@dataclass(frozen=True)
class BlockRuleContext:
    language_id: str
    envelope: BlockEnvelope
    block_pairs: tuple[tuple[str, str], ...]


_RULE_CACHE: dict[str, BlockRuleContext] = {}


def rules_for(language_id: str) -> BlockRuleContext:
    if language_id not in _RULE_CACHE:
        spec = language_for_id(language_id)
        _RULE_CACHE[language_id] = BlockRuleContext(
            language_id=language_id,
            envelope=envelope_from_block_style(spec.block_style),
            block_pairs=spec.block_pairs,
        )
    return _RULE_CACHE[language_id]


def node_envelope(node: BlockNode) -> BlockEnvelope | None:
    return parse_envelope_meta(node.meta)


def closes_matching_block(
    node: BlockNode,
    close: CodeToken,
    *,
    module_lang: str,
) -> bool:
    """True wenn dieser Close genau diesen Stack-Knoten schließt."""
    if close.close_role is None:
        return False
    env = node_envelope(node)
    if env is None:
        return False
    expected = close_role_for_envelope(env)
    if expected is None:
        return False
    if close.close_role is not expected:
        return False
    if env is BlockEnvelope.KEYWORD:
        node_pair = node.meta.get("pair_index")
        close_pair = close.meta.get("pair_index")
        if node_pair is not None and close_pair is not None:
            return node_pair == close_pair
    return True


def absorb_close_into_embedded_tag(node: BlockNode, close: CodeToken) -> bool:
    """Nicht-Tag-Close bleibt im eingebetteten Tag-CHILD (z. B. } in <script>)."""
    if close.close_role not in (CloseRole.BRACE, CloseRole.BRACKET):
        return False
    env = node_envelope(node)
    if env is not BlockEnvelope.TAG:
        return False
    return bool(node.meta.get("embedded_language") or node.meta.get("rule_language"))
