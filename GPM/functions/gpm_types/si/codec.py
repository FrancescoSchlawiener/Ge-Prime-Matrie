"""S(I) Codec — encode/decode OG-Pfad; perm_space getrennt von N(I)."""

from __future__ import annotations

from collections import Counter

from alphabets.lex import lex_order_for_profile
from alphabets.normalize import is_valid_substrate, prepare_substrate
from alphabets.profiles import AlphabetProfile
from perm.lut import get_permutation_lut, lut_index_of_sequence, lut_sequence_at_index
from perm.multiset import perm_decode, perm_index, perm_space
from gpm_types.si.substance import ingredients_for_profile, ingredients_og_alpha, substance_og_alpha


def permutation_index_og(sequence: str) -> int:
    counts = Counter(sequence)
    lex = lex_order_for_profile(AlphabetProfile.OG)
    return perm_index(list(sequence), counts, lex_order=lex)


def permutation_index_for_profile(
    sequence: str,
    profile: AlphabetProfile | str,
) -> int:
    counts = Counter(sequence)
    lex = lex_order_for_profile(profile)
    return perm_index(list(sequence), counts, lex_order=lex)


def permutation_index_via_lut(
    sequence: str,
    profile: AlphabetProfile | str = AlphabetProfile.OG,
) -> int:
    lut = get_permutation_lut(Counter(sequence), profile)
    return lut_index_of_sequence(lut, sequence)


def decode_via_lut(
    substance: int,
    index: int,
    profile: AlphabetProfile | str = AlphabetProfile.OG,
) -> str:
    counts = ingredients_for_profile(substance, profile)
    lut = get_permutation_lut(counts, profile)
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
    return decode_si(substance, index, AlphabetProfile.OG)


def decode_si(
    substance: int,
    index: int,
    profile: AlphabetProfile | str = AlphabetProfile.OG,
) -> str:
    counts = ingredients_for_profile(substance, profile)
    lex = lex_order_for_profile(profile)
    return "".join(perm_decode(counts, index, lex_order=lex))


def encode_si(
    raw: str,
    profile: AlphabetProfile | str = AlphabetProfile.OG,
) -> tuple[int, int]:
    substance, index, _trace = encode_si_with_trace(raw, profile)
    return substance, index


def encode_si_with_trace(
    raw: str,
    profile: AlphabetProfile | str = AlphabetProfile.OG,
):
    from analysis.inference.trace import InferenceTrace
    from alphabets.registry import prime_map_for_profile
    from gpm_types.si.substance import substance_for_profile

    if isinstance(profile, str):
        profile = AlphabetProfile(profile)
    seq = prepare_substrate(raw, profile)
    if not is_valid_substrate(seq, profile):
        raise ValueError(f"Keine gültige Substrat-Sequenz ({profile!r}): {seq!r}")
    counts = Counter(seq)
    lex = lex_order_for_profile(profile)
    substance = substance_for_profile(seq, profile)
    index = perm_index(list(seq), counts, lex_order=lex)
    prime_map = prime_map_for_profile(profile)
    prime_factors: dict[int, int] = {}
    for char, exp in counts.items():
        prime = prime_map.get(char)
        if prime is not None:
            prime_factors[prime] = exp
    trace = InferenceTrace(
        raw_word=raw,
        normalized=seq,
        substance=substance,
        index=index,
        prime_factors=prime_factors,
    )
    return substance, index, trace


def decode_si_with_trace(
    substance: int,
    index: int,
    profile: AlphabetProfile | str = AlphabetProfile.OG,
):
    from analysis.inference.trace import InferenceTrace
    from gpm_types.si.substance import ingredients_for_profile

    if isinstance(profile, str):
        profile = AlphabetProfile(profile)
    word = decode_si(substance, index, profile)
    counts = ingredients_for_profile(substance, profile)
    from alphabets.registry import prime_map_for_profile

    prime_map = prime_map_for_profile(profile)
    char_to_prime = {char: prime for prime, char in prime_map.items()}
    prime_factors = {char_to_prime[char]: exp for char, exp in counts.items() if char in char_to_prime}
    trace = InferenceTrace(
        substance=substance,
        index=index,
        normalized=word,
        decoded_word=word,
        prime_factors=prime_factors,
    )
    return word, trace


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
