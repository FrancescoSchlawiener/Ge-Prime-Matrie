"""Ge-Prime-Matrix Domain — Substanz S, Index I, Analyse und Verschlüsselung."""

__all__ = [
    "APP_VERSION",
    "GPM_VERSION",
    "ROOT",
    "PRIME_MAP",
    "CHAR_MAP",
    "encode_word",
    "decode_word",
    "get_substance",
    "get_ingredients",
    "compare_substances",
    "classify_word_pair",
    "analyze_pair",
    "encrypt_text",
    "decrypt_ciphertext",
    "VALID_MODES",
    "REQUIRED_API_ROUTES",
    "db_path",
]


def __getattr__(name: str):
    if name in ("APP_VERSION", "GPM_VERSION", "ROOT", "REQUIRED_API_ROUTES", "db_path", "gpm_si_storage_payload"):
        from ge_prime import config

        return getattr(config, name)
    if name in ("PRIME_MAP", "CHAR_MAP", "calc_total_perms"):
        from ge_prime import core

        return getattr(core, name)
    if name in ("encode_word", "get_substance", "get_index"):
        from ge_prime import encode

        return getattr(encode, name)
    if name in ("decode_word", "get_ingredients"):
        from ge_prime import decode

        return getattr(decode, name)
    if name == "compare_substances":
        from ge_prime.compare import compare_substances

        return compare_substances
    if name == "classify_word_pair":
        from ge_prime.diff import classify_word_pair

        return classify_word_pair
    if name == "analyze_pair":
        from ge_prime.i_curve import analyze_pair

        return analyze_pair
    if name in ("encrypt_text", "decrypt_ciphertext", "VALID_MODES"):
        from ge_prime import cipher

        return getattr(cipher, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
