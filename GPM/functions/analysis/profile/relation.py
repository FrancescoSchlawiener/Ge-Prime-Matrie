"""Relations-Profile — Wort-/Substanz-/Kategorie-Beziehungen zwischen Token."""

from __future__ import annotations

from collections import Counter
from functools import lru_cache

from analysis.blocks.build import materialize_geometry
from analysis.case.apply import apply_case
from analysis.compile.compiler import compile_text
from analysis.document.model import GpmDocument
from analysis.algebra.sparse_counter import counter_cosine, weighted_channel_score
from analysis.algebra.substance_kernel import substance_ggt_kgv_similarity

RELATION_TWIN_THRESHOLD = 0.4
LITERAL_LOW_THRESHOLD = 0.6
SAME_DOMAIN_RELATIONAL_THRESHOLD = 0.35

WEIGHT_WORD_BIGRAM = 0.5
WEIGHT_SUBSTANCE_BIGRAM = 0.3
WEIGHT_CATEGORY_TRANSITION = 0.2


def _substance_pair_key(s_a: int, s_b: int) -> str:
    bucket = int(substance_ggt_kgv_similarity(s_a, s_b) * 10)
    return f"{min(s_a, s_b)}:{max(s_a, s_b)}:{bucket}"


def _token_rows(document: GpmDocument) -> list[dict]:
    explicit_map = dict(document.explicit)
    rows: list[dict] = []
    for position, token in enumerate(document.tokens):
        if position in explicit_map:
            word = explicit_map[position]
            normalized = word.upper()
            substance = document.header[token.word_id].substance
        else:
            entry = document.header[token.word_id]
            word = apply_case(entry.word_canonical, token.case_code)
            normalized = entry.word_normalized
            substance = entry.substance
        rows.append(
            {
                "position": position,
                "normalized": normalized,
                "substance": substance,
            }
        )
    return rows


def _category_transitions(document: GpmDocument) -> Counter:
    materialize_geometry(document)
    transitions: Counter = Counter()
    for cell in document.cells:
        seq = cell.category_sequence
        for i in range(len(seq) - 1):
            key = f"{seq[i]}>{seq[i + 1]}"
            transitions[key] += 1
    return transitions


def build_relation_profile(document: GpmDocument) -> dict:
    """Bigramme und Übergänge als Relations-Signatur."""
    rows = _token_rows(document)
    word_bigrams: Counter = Counter()
    substance_bigrams: Counter = Counter()

    for i in range(len(rows) - 1):
        a, b = rows[i], rows[i + 1]
        wkey = f"{a['normalized']}|{b['normalized']}"
        word_bigrams[wkey] += 1
        skey = _substance_pair_key(a["substance"], b["substance"])
        substance_bigrams[skey] += 1

    category_transitions = _category_transitions(document)

    return {
        "word_bigrams": word_bigrams,
        "substance_bigrams": substance_bigrams,
        "category_transitions": category_transitions,
        "bigram_count": len(word_bigrams),
    }


def _shared_top(a: Counter, b: Counter, limit: int = 10) -> list[dict]:
    shared: list[tuple[str, int, int]] = []
    for key in set(a) & set(b):
        shared.append((key, a[key], b[key]))
    shared.sort(key=lambda item: min(item[1], item[2]), reverse=True)
    return [
        {"relation": key, "count_a": ca, "count_b": cb}
        for key, ca, cb in shared[:limit]
    ]


def _first_bigram_token_start(rows: list[dict], word_a: str, word_b: str) -> int | None:
    for i in range(len(rows) - 1):
        if rows[i]["normalized"] == word_a and rows[i + 1]["normalized"] == word_b:
            return i
    return None


def serialize_relation_comparison_api(
    relation_comparison: dict,
    doc_a: GpmDocument,
    doc_b: GpmDocument,
) -> dict:
    """API payload with span positions; keeps legacy shared_word_bigrams."""
    rows_a = _token_rows(doc_a)
    rows_b = _token_rows(doc_b)
    shared_spans: list[dict] = []
    for entry in relation_comparison.get("shared_word_bigrams") or []:
        key = entry.get("relation") or ""
        parts = key.split("|", 1)
        if len(parts) != 2:
            continue
        token_start_a = _first_bigram_token_start(rows_a, parts[0], parts[1])
        token_start_b = _first_bigram_token_start(rows_b, parts[0], parts[1])
        if token_start_a is None or token_start_b is None:
            continue
        shared_spans.append(
            {
                "token_start_a": token_start_a,
                "token_count": 2,
                "token_start_b": token_start_b,
                "count_a": entry.get("count_a", 0),
                "count_b": entry.get("count_b", 0),
            }
        )
    payload = dict(relation_comparison)
    payload["shared_bigram_spans"] = shared_spans[:10]
    return payload


def compare_relation_profiles(prof_a: dict, prof_b: dict) -> dict:
    word_sim = counter_cosine(prof_a["word_bigrams"], prof_b["word_bigrams"])
    subst_sim = counter_cosine(prof_a["substance_bigrams"], prof_b["substance_bigrams"])
    cat_sim = counter_cosine(prof_a["category_transitions"], prof_b["category_transitions"])

    relation_score = weighted_channel_score(
        {"word": word_sim, "substance": subst_sim, "category": cat_sim},
        {
            "word": WEIGHT_WORD_BIGRAM,
            "substance": WEIGHT_SUBSTANCE_BIGRAM,
            "category": WEIGHT_CATEGORY_TRANSITION,
        },
    )

    return {
        "relation_score": round(relation_score, 6),
        "word_bigram_similarity": round(word_sim, 6),
        "substance_bigram_similarity": round(subst_sim, 6),
        "category_transition_similarity": round(cat_sim, 6),
        "shared_word_bigrams": _shared_top(prof_a["word_bigrams"], prof_b["word_bigrams"]),
        "shared_substance_bigrams": _shared_top(
            prof_a["substance_bigrams"], prof_b["substance_bigrams"], limit=5
        ),
    }


def relation_twins(relation_comparison: dict, *, literal_match_ratio: float) -> bool:
    return (
        relation_comparison.get("relation_score", 0.0) >= RELATION_TWIN_THRESHOLD
        and literal_match_ratio < LITERAL_LOW_THRESHOLD
    )


@lru_cache(maxsize=64)
def domain_relation_seed_profile(seed_text: str, profile_value: str = "og") -> Counter:
    if not seed_text or not seed_text.strip():
        return Counter()
    from alphabets import AlphabetProfile

    doc, _ = compile_text(seed_text, AlphabetProfile(profile_value))
    prof = build_relation_profile(doc)
    return prof["word_bigrams"]


def score_domain_relations(domain_seed_text: str, document_profile: dict) -> float:
    seed = domain_relation_seed_profile(domain_seed_text)
    if not seed:
        return 0.0
    return counter_cosine(document_profile["word_bigrams"], seed)
