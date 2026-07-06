"""Makro-Suche über hierarchisches Gitter mit kgV-Pruning."""

from __future__ import annotations

from analysis.blocks.node import TokenSpan
from analysis.compile.compiler import compile_text
from analysis.hierarchy.access import get_hierarchy, get_interval_index
from analysis.hierarchy.compare import compare_level_sequences
from analysis.hierarchy.curves import extract_paragraph_curve
from analysis.hierarchy.enjambement import detect_enjambement
from analysis.index.interval_index import nodes_intersecting_indexed
from analysis.span.substance_span import local_kgv
from analysis.algebra.substance_kernel import substance_covers, substance_ggt_kgv_similarity


def _target_substance(document, token_start: int, token_count: int) -> int:
    return local_kgv(document, token_start, token_count)


def hierarchy_search(
    document,
    *,
    pattern_text: str,
    level: str = "paragraph",
    zoom: bool = True,
    query: str | None = None,
    profile=None,
) -> dict:
    """Makro-Suche mit kgV-Pruning und optionalem Zoom."""
    pattern_doc, _ = compile_text(pattern_text, profile=profile or document.profile)
    hierarchy = get_hierarchy(document)
    pattern_hierarchy = get_hierarchy(pattern_doc)
    idx = get_interval_index(document)

    s_target = _target_substance(pattern_doc, 0, len(pattern_doc.tokens))

    matches: list[dict] = []
    paragraphs = hierarchy.semantic.paragraphs

    for p_idx, paragraph in enumerate(paragraphs):
        local_kgv_val = local_kgv(document, paragraph.token_start, paragraph.token_count)
        if not substance_covers(local_kgv_val, s_target):
            continue

        para_curve = extract_paragraph_curve(document)
        pat_para = extract_paragraph_curve(pattern_doc)
        cmp = compare_level_sequences(
            [para_curve[p_idx]] if p_idx < len(para_curve) else [],
            pat_para[:1] if pat_para else [],
            ratio_key="i_absatz_ratio",
        )
        score = cmp.get("geometry_score", 0.0)
        if score < 0.1 and local_kgv_val != s_target:
            continue

        match = {
            "level": "paragraph",
            "token_start": paragraph.token_start,
            "token_end": paragraph.token_start + paragraph.token_count,
            "score": score,
            "local_kgv": local_kgv_val,
            "zoom_path": ["paragraph"],
        }

        if zoom and query == "rhythm_breaks":
            enj = detect_enjambement(
                hierarchy.semantic.sentences,
                hierarchy.structural.lines,
                interval_index=idx,
            )
            match["rhythm_break_count"] = enj["rhythm_break_count"]
        elif zoom:
            sent_scores = []
            para_span = TokenSpan(paragraph.token_start, paragraph.token_count)
            for sentence in hierarchy.semantic.sentences:
                if not nodes_intersecting_indexed(idx, "sentence", [sentence], para_span):
                    continue
                pat_sent = (
                    pattern_hierarchy.semantic.sentences[0].s_level
                    if pattern_hierarchy.semantic.sentences
                    else s_target
                )
                sk = substance_ggt_kgv_similarity(sentence.s_level, pat_sent)
                sent_scores.append(sk)
            match["zoom_path"] = ["paragraph", "sentence"]
            match["sentence_mean_similarity"] = (
                sum(sent_scores) / len(sent_scores) if sent_scores else 0.0
            )

        matches.append(match)

    if query == "line_aligned":
        enj = detect_enjambement(
            hierarchy.semantic.sentences,
            hierarchy.structural.lines,
            interval_index=idx,
        )
        return {"query": query, "matches": matches, "cross_analysis": enj}

    if query == "sentences_in_line":
        line_idx = 0
        if hierarchy.structural.lines:
            line = hierarchy.structural.lines[min(line_idx, len(hierarchy.structural.lines) - 1)]
            sents = nodes_intersecting_indexed(
                idx,
                "sentence",
                hierarchy.semantic.sentences,
                TokenSpan(line.token_start, line.token_count),
            )
            return {
                "query": query,
                "line_index": line_idx,
                "matches": [
                    {
                        "token_start": s.token_start,
                        "token_end": s.token_start + s.token_count,
                        "score": 1.0,
                    }
                    for s in sents
                ],
            }

    return {
        "level": level,
        "pattern_tokens": len(pattern_doc.tokens),
        "s_target": s_target,
        "matches": matches,
        "match_count": len(matches),
    }


def hierarchy_search_from_blob(
    blob: bytes,
    *,
    pattern_text: str,
    level: str = "paragraph",
    zoom: bool = True,
    query: str | None = None,
) -> dict:
    from analysis.binary.reader import load_gpm

    document = load_gpm(blob)
    return hierarchy_search(
        document,
        pattern_text=pattern_text,
        level=level,
        zoom=zoom,
        query=query,
    )
