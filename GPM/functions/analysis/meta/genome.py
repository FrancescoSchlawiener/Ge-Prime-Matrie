"""Meta-Genom — Dokumenten-Vektor V aus Header-Substanzen."""

from __future__ import annotations

from analysis.case.apply import apply_case
from analysis.case.codes import CASE_LOWER
from analysis.compile.compiler import compile_text
from analysis.document.model import GpmDocument
from analysis.meta.fingerprint import profile_vector_fields
from analysis.profile.prime_profile import build_prime_profile, word_frequencies

TOP_WORDS_LIMIT = 15


def build_meta_genome(document: GpmDocument) -> dict:
    freqs = word_frequencies(document)
    profile = build_prime_profile(document)
    vector_label, vector_bits = profile_vector_fields(profile)
    total_tokens = sum(freqs.values())

    top_rows = []
    for word_id, count in freqs.most_common(TOP_WORDS_LIMIT):
        entry = document.header[word_id]
        top_rows.append(
            {
                "word_id": word_id,
                "word": apply_case(entry.word_canonical, CASE_LOWER),
                "normalized": entry.word_normalized,
                "substance": entry.substance,
                "count": count,
                "weight": round(count / total_tokens, 6) if total_tokens else 0.0,
            }
        )

    return {
        "vector": vector_label,
        "vector_bits": vector_bits,
        "profile": {str(p): c for p, c in sorted(profile.items())},
        "prime_factor_count": len(profile),
        "total_letter_mass": sum(profile.values()),
        "unique_words": len(document.header),
        "token_count": total_tokens,
        "top_words": top_rows,
        "document_profile": document.profile.value,
    }


def build_meta_genome_from_text(text: str, profile=None) -> dict:
    from alphabets import AlphabetProfile

    if profile is None:
        profile = AlphabetProfile.OG
    document, _ = compile_text(text, profile)
    return build_meta_genome(document)
