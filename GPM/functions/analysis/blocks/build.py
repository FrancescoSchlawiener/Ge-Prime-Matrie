"""Fraktalbaum aus GpmDocument + materialize_geometry."""

from __future__ import annotations

import pickle

from analysis.blocks.context import COrigin
from analysis.blocks.kinds import PointerKind
from analysis.blocks.node import BlockLevel, BlockNode, PointerRef, TokenSpan
from analysis.blocks.registry import DocumentRegistry
from analysis.cell.geom import build_document_cells
from analysis.document.model import GpmDocument, GpmHeaderEntry
from analysis.hierarchy.geom import (
    DocumentHierarchy,
    build_document_hierarchy,
    split_paragraph_spans,
    split_sentence_spans,
)


def _ensure_registry(document: GpmDocument) -> DocumentRegistry:
    if document.registry is not None:
        return document.registry
    reg = DocumentRegistry(profile=document.profile)
    for entry in document.header:
        reg.intern_s_header(entry)
    document.registry = reg
    return reg


def _cell_block(
    document: GpmDocument,
    cell,
    registry: DocumentRegistry,
    block_id: int,
    parent_id: int | None,
) -> BlockNode:
    key = pickle.dumps(
        (cell.token_start, cell.token_count, tuple(cell.frequencies), cell.perm_index),
        protocol=pickle.HIGHEST_PROTOCOL,
    )
    c_ptr = registry.intern(
        PointerKind.C,
        key,
        origin=COrigin.GEOM,
        substance=1,
        perm_index=cell.perm_index,
        perm_space=cell.perm_space,
        frequencies=list(cell.frequencies),
    )
    seq = [PointerRef(kind=PointerKind.C, ptr_id=c_ptr)]
    for cat in cell.categories:
        seq.append(PointerRef(kind=PointerKind.S, ptr_id=cat.word_id))
    return BlockNode(
        block_id=block_id,
        level=BlockLevel.CELL,
        token_span=TokenSpan(cell.token_start, cell.token_count),
        sequence=seq,
        perm_index=cell.perm_index,
        perm_space=cell.perm_space,
        parent_id=parent_id,
    )


def build_block_tree(document: GpmDocument) -> BlockNode:
    registry = _ensure_registry(document)
    if document.cells is None or not document.cells:
        document.cells = build_document_cells(document)
    if document.hierarchy is None:
        document.hierarchy = build_document_hierarchy(document)

    block_id = 0
    root = BlockNode(block_id=block_id, level=BlockLevel.DOCUMENT)
    block_id += 1

    cell_by_start = {c.token_start: c for c in document.cells}

    all_sentences = split_sentence_spans(len(document.tokens), document.gaps)

    for para_span in split_paragraph_spans(len(document.tokens), document.gaps):
        para = BlockNode(
            block_id=block_id,
            level=BlockLevel.PARAGRAPH,
            token_span=para_span,
            parent_id=root.block_id,
        )
        block_id += 1
        for sent_span in all_sentences:
            if sent_span.token_start < para_span.token_start:
                continue
            if sent_span.token_end > para_span.token_end:
                continue
            sent = BlockNode(
                block_id=block_id,
                level=BlockLevel.SENTENCE,
                token_span=sent_span,
                parent_id=para.block_id,
            )
            block_id += 1
            cursor = sent_span.token_start
            while cursor < sent_span.token_end:
                cell = cell_by_start.get(cursor)
                if cell is None:
                    cursor += 1
                    continue
                sent.children.append(
                    _cell_block(document, cell, registry, block_id, sent.block_id)
                )
                block_id += 1
                cursor = cell.token_start + cell.token_count
            para.children.append(sent)
        root.children.append(para)

    document.root_block = root
    return root


def materialize_geometry(document: GpmDocument) -> GpmDocument:
    _ensure_registry(document)
    if not document.cells:
        document.cells = build_document_cells(document)
    if document.hierarchy is None:
        document.hierarchy = build_document_hierarchy(document)
    if document.root_block is None:
        build_block_tree(document)
    return document
