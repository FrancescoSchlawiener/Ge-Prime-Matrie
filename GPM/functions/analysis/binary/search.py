"""In-Memory Genom-Suche — Invariante B (kgV-Fold + substance_covers)."""

from __future__ import annotations

import math

from alphabets.normalize import prepare_substrate
from analysis.document.model import GpmDocument
from analysis.algebra.fold import fold_lcm
from analysis.algebra.substance_kernel import compare_substances, substance_covers
from gpm_types.si.codec import encode_si
from gpm_types.si.substance import ingredients_for_profile


def _encode_query(word: str, document: GpmDocument) -> tuple[str, int]:
    stripped = word.strip()
    if not stripped:
        raise ValueError(f"Suchwort ungültig: {word!r}")
    normalized = prepare_substrate(stripped, document.profile)
    try:
        substance, _ = encode_si(stripped, document.profile)
    except ValueError as exc:
        raise ValueError(f"Suchwort ungültig: {word!r}") from exc
    return normalized, substance


def _header_dict(entry) -> dict:
    return {
        "word_id": entry.word_id,
        "original": entry.word_canonical,
        "normalized": entry.word_normalized,
        "substance": entry.substance,
    }


def search_by_word(document: GpmDocument, query: str) -> dict:
    query_normalized, query_substance = _encode_query(query, document)
    header_hits = [
        _header_dict(entry)
        for entry in document.header
        if entry.substance == query_substance
    ]
    word_ids = {entry["word_id"] for entry in header_hits}
    positions = [
        {
            "position": idx,
            "word_id": token.word_id,
            "perm_index": token.perm_index,
        }
        for idx, token in enumerate(document.tokens)
        if token.word_id in word_ids
    ]
    return {
        "query": query,
        "query_normalized": query_normalized,
        "query_substance": query_substance,
        "found_in_header": len(header_hits) > 0,
        "header_matches": header_hits,
        "occurrences": len(positions),
        "positions": positions[:200],
    }


def search_by_gcd(document: GpmDocument, query: str) -> dict:
    _, query_substance = _encode_query(query, document)
    matches: list[dict] = []

    for entry in document.header:
        gcd_value = math.gcd(entry.substance, query_substance)
        if gcd_value <= 1:
            continue
        cmp = compare_substances(entry.substance, query_substance, document.profile)
        matches.append(
            {
                **_header_dict(entry),
                "gcd_value": gcd_value,
                "shared_letters": cmp["shared_letters"],
            }
        )

    word_ids = {row["word_id"] for row in matches}
    token_hits = sum(1 for token in document.tokens if token.word_id in word_ids)

    return {
        "query": query,
        "query_substance": query_substance,
        "matches": matches[:200],
        "unique_words": len(matches),
        "token_hits": token_hits,
    }


def search_by_lcm(document: GpmDocument, *queries: str) -> dict:
    if not queries:
        raise ValueError("Mindestens ein Suchwort erforderlich.")

    encoded = [_encode_query(q, document) for q in queries]
    substances = [s for _, s in encoded]

    search_lcm = fold_lcm(substances)

    union = (
        dict(ingredients_for_profile(search_lcm, document.profile))
        if search_lcm > 1
        else {}
    )

    matches: list[dict] = []
    for entry in document.header:
        if not substance_covers(entry.substance, search_lcm):
            continue
        matches.append({**_header_dict(entry), "covers_lcm": True})

    word_ids = {row["word_id"] for row in matches}
    token_hits = sum(1 for token in document.tokens if token.word_id in word_ids)

    result = {
        "query": queries[0],
        "query_substance": substances[0],
        "lcm_value": search_lcm,
        "union_letters": union,
        "matches": matches[:200],
        "unique_words": len(matches),
        "token_hits": token_hits,
    }
    if len(queries) >= 2:
        result["query2"] = queries[1]
        result["query2_substance"] = substances[1]
        result["query2_normalized"] = encoded[1][0]
        result["query_normalized"] = encoded[0][0]
    if len(queries) > 2:
        result["queries"] = list(queries)
        result["query_substances"] = substances
    return result
