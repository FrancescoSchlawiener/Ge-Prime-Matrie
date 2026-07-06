"""Pädagogik-Schritte für Substanz-Vergleich — Mapping aus analyze_word_pair."""

from __future__ import annotations

from api.schemas.common import Step


def map_compare_words_steps(pair: dict) -> list[Step]:
    comparison = pair.get("comparison", {})
    return [
        Step(
            id="encode_pair",
            title="Beide Wörter kodieren",
            detail="Ein Inferenzlauf liefert (S, I) für beide Wörter.",
            values={
                "a": pair["word1"],
                "b": pair["word2"],
                "substance_a": pair["substance1"],
                "substance_b": pair["substance2"],
            },
        ),
        Step(
            id="compare_substances",
            title="Substanz-Vergleich",
            detail="ggT, kgV und Ähnlichkeitsmetriken aus dem Paar-Lauf.",
            values={
                "gcd": comparison.get("gcd_value", 0),
                "lcm": comparison.get("lcm_value", 0),
                "similarity": comparison.get("ggt_kgv_similarity", 0.0),
            },
            formula="ggT(S₁,S₂), kgV(S₁,S₂)",
        ),
        Step(
            id="classify",
            title="Klassifikation",
            detail="Wortpaar-Typ (Anagramm, Teilmenge, …).",
            values={"classification": str(pair["classification"])},
        ),
    ]


def build_compare_words_steps(a: str, b: str, profile) -> tuple[dict, list[Step]]:
    from alphabets import AlphabetProfile
    from analysis.pair.analyze_word_pair import analyze_word_pair

    if isinstance(profile, str):
        profile = AlphabetProfile(profile)
    pair = analyze_word_pair(a, b, profile)
    return pair, map_compare_words_steps(pair)
