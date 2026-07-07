"""Tensorraum-Kanonisierung — compile_source + volle Registry-Serialisierung."""

from __future__ import annotations

from typing import Any

from alphabets import AlphabetProfile
from analysis.blocks.context import COrigin
from analysis.blocks.kinds import PointerKind
from analysis.blocks.node import BlockNode, PointerRef
from analysis.blocks.registry import DocumentRegistry
from analysis.code.compile import compile_source, verify_reversibility
from analysis.code.decompile import reconstruct_source
from analysis.code.languages import language_for_extension, language_for_id
from gpm_types.di.codec import decode_di_relation
from gpm_types.di.relation import parse_decimal
from gpm_types.hi.codec import decode_hi, substance_hi


def _resolve_ref_value(ref: PointerRef, registry: DocumentRegistry) -> str:
    if ref.kind is PointerKind.S:
        return registry.s_entries[ref.ptr_id].word_canonical
    if ref.kind is PointerKind.N:
        return str(registry.n_entries[ref.ptr_id])
    if ref.kind is PointerKind.D:
        return registry.d_entries[ref.ptr_id]
    if ref.kind is PointerKind.C:
        return registry.c_entries[ref.ptr_id].key_bytes.decode("utf-8", errors="replace")
    if ref.kind is PointerKind.H:
        return decode_hi(registry.h_entries[ref.ptr_id])
    if ref.kind is PointerKind.SYS:
        close = ref.meta.get("close_syntax")
        if close:
            return close
        return registry.c_entries[ref.ptr_id].key_bytes.decode("utf-8", errors="replace")
    return ""


def _ref_to_item(ref: PointerRef, registry: DocumentRegistry) -> dict[str, Any]:
    if ref.kind is PointerKind.SYS:
        return {
            "t": "SYS",
            "p": "CLOSE_BRACKET",
            "nl": ref.nl,
            "closeSyntax": ref.meta.get("close_syntax"),
        }
    return {
        "t": ref.kind.value,
        "value": _resolve_ref_value(ref, registry),
        "nl": ref.nl,
    }


def _block_to_tree(node: BlockNode, registry: DocumentRegistry) -> dict[str, Any]:
    sequence: list[dict[str, Any]] = []
    children: list[dict[str, Any]] = []
    for ref in node.sequence:
        sequence.append(_ref_to_item(ref, registry))
    for child in node.children:
        child_tree = _block_to_tree(child, registry)
        children.append(child_tree)
        sequence.append(
            {
                "t": "CHILD",
                "nl": child.meta.get("prefix_nl", 0),
                "visualStyle": child.meta.get("visual_style"),
                "openSyntax": child.meta.get("open_syntax"),
                "node": child_tree,
            }
        )
    return {"sequence": sequence, "children": children}


def _export_registry(reg: DocumentRegistry) -> dict[str, list[dict[str, Any]]]:
    s_out = [
        {
            "value": e.word_canonical,
            "normalized": e.word_normalized,
            "substance": e.substance,
            "perm_index": e.perm_index,
        }
        for e in reg.s_entries
    ]
    n_out = [{"value": str(n)} for n in reg.n_entries]
    d_out = []
    for raw in reg.d_entries:
        rel = parse_decimal(raw)
        d_out.append(
            {
                "value": raw,
                "display": decode_di_relation(rel),
                "relation": {
                    "whole": rel.whole,
                    "den_reduced": rel.den_reduced,
                    "ggt": rel.ggt,
                },
            }
        )
    c_out = [
        {
            "value": e.key_bytes.decode("utf-8", errors="replace"),
            "origin": e.origin.value if hasattr(e.origin, "value") else str(e.origin),
        }
        for e in reg.c_entries
    ]
    h_out = []
    for payload in reg.h_entries:
        raw = decode_hi(payload)
        h_out.append(
            {
                "raw": raw,
                "segments": [{"tag": s.tag, "value": s.value} for s in payload.segments],
                "substance": substance_hi(payload),
            }
        )
    return {"S": s_out, "N": n_out, "D": d_out, "C": c_out, "H": h_out}


def canonicalize_for_tensorraum(
    source: str,
    filename: str,
    *,
    profile: AlphabetProfile | str = AlphabetProfile.OG,
) -> dict[str, Any]:
    prof = profile if isinstance(profile, AlphabetProfile) else AlphabetProfile(profile)
    spec = language_for_extension(filename)
    if spec is None:
        raise ValueError(f"Keine Sprache für Datei: {filename!r}")
    language_id = spec.id
    language_for_id(language_id)
    reg = DocumentRegistry(profile=prof)
    module = compile_source(source, language_id, reg)
    reconstructed = reconstruct_source(module, reg)
    roundtrip_ok = reconstructed == source
    tree = _block_to_tree(module, reg)
    return {
        "filename": filename,
        "language_id": language_id,
        "language_name": spec.name,
        "normalized_code": source,
        "roundtrip_ok": roundtrip_ok,
        "registry": _export_registry(reg),
        "tree": tree,
    }
