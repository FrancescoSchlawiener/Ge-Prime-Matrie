"""S(I) Codec — encode/decode OG-Pfad; perm_space getrennt von N(I)."""

from __future__ import annotations

from collections import Counter

from alphabets.profiles import AlphabetProfile
from alphabets.roman.normalize import is_valid_substrate, prepare_substrate
from perm.lut import get_permutation_lut, lut_index_of_sequence, lut_sequence_at_index
from perm.multiset import perm_decode, perm_index, perm_space
from gpm_types.si.substance import ingredients_og_alpha, substance_og_alpha


def permutation_index_og(sequence: str) -> int:
    counts = Counter(sequence)
    return perm_index(list(sequence), counts)


def permutation_index_via_lut(sequence: str) -> int:
    lut = get_permutation_lut(Counter(sequence))
    return lut_index_of_sequence(lut, sequence)


def decode_via_lut(substance: int, index: int) -> str:
    counts = ingredients_og_alpha(substance)
    lut = get_permutation_lut(counts)
    return lut_sequence_at_index(lut, index)


def perm_space_of(raw: str, profile: AlphabetProfile | str = AlphabetProfile.OG) -> int:
    seq = prepare_substrate(raw, profile)
    return perm_space(Counter(seq))


def perm_space(raw: str, profile: AlphabetProfile | str = AlphabetProfile.OG) -> int:
    """Permutationsraum-Größe N_perm — nicht N(I) Datentyp."""
    return perm_space_of(raw, profile)


N_perm = perm_space


def encode_si_og(raw: str) -> tuple[int, int]:
    seq = prepare_substrate(raw, AlphabetProfile.OG)
    if not is_valid_substrate(seq, AlphabetProfile.OG):
        raise ValueError(f"Keine gültige OG-Substrat-Sequenz: {seq!r}")
    return substance_og_alpha(seq), permutation_index_og(seq)


def decode_si_og(substance: int, index: int) -> str:
    counts = ingredients_og_alpha(substance)
    return "".join(perm_decode(counts, index))


def encode_si(
    raw: str,
    profile: AlphabetProfile | str = AlphabetProfile.OG,
) -> tuple[int, int]:
    seq = prepare_substrate(raw, profile)
    if not is_valid_substrate(seq, profile):
        raise ValueError(f"Keine gültige Substrat-Sequenz ({profile!r}): {seq!r}")
    from gpm_types.si.substance import substance_for_profile

    return substance_for_profile(raw, profile), perm_index(list(seq), Counter(seq))


get_index = permutation_index_og
encode_word = encode_si_og
decode_word = decode_si_og


def encode(raw: str) -> tuple[int, int]:
    return encode_si_og(raw)


def decode(substance: int, index: int) -> str:
    return decode_si_og(substance, index)


def I(raw: str) -> int:
    seq = prepare_substrate(raw, AlphabetProfile.OG)
    return permutation_index_og(seq)
