"""Gemeinsame JSON-Payloads für Wort-APIs."""

from db.language import language_label
from ge_prime.decode import decode_word
from pipeline.normalize import denormalize_word


def word_payload(process_result) -> dict:
    p = process_result
    return {
        "original": p.word_original,
        "normalized": p.word_normalized,
        "display": denormalize_word(p.word_normalized, p.word_original),
        "substance": p.substance,
        "perm_index": p.perm_index,
        "language": p.language,
        "language_label": language_label(p.language),
        "decoded": decode_word(p.substance, p.perm_index),
    }
