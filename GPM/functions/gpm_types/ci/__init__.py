"""C(I) package — Primzahl-Geometrie für Code-Struktur-/Symbol-Token."""

from gpm_types.ci.registry import checksum_c, pointer_id_c
from gpm_types.ci.substance import (
    CODE_CHAR_PRIMES,
    decode_ci,
    perm_index_c,
    perm_space_c,
    prime_for_char,
    substance_c,
)

__all__ = [
    "CODE_CHAR_PRIMES",
    "decode_ci",
    "prime_for_char",
    "substance_c",
    "perm_index_c",
    "perm_space_c",
    "checksum_c",
    "pointer_id_c",
]
