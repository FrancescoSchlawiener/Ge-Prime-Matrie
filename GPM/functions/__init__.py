"""GPM Grundfunktionen — Phase 2."""

from alphabets.profiles import AlphabetProfile
from alphabets.roman.map import (
    ALPHA_ROMAN,
    ALPHA_ROMAN_LEX_ORDER,
    CHAR_ROMAN,
    PRIME_TO_CHAR_ROMAN,
    char_map_for_profile,
    is_roman_symbol,
    prime_map_for_profile,
    uses_roman_alpha,
)
from alphabets.greek.map import ALPHA_GREEK, CHAR_GREEK_SET
from alphabets.cyrillic.map import ALPHA_CYRILLIC, CHAR_CYRILLIC_SET
from perm.lut import (
    ALPHA_ROMAN_SINGLETON_LUTS,
    MAX_LUT_BUILD_LENGTH,
    PermutationLut,
    build_permutation_lut,
    build_permutation_lut_for_sequence,
    get_permutation_lut,
)
from perm.multiset import calc_total_perms, perm_decode, perm_fits_width, perm_index, perm_space
from alphabets.roman.normalize import (
    is_valid_og_substrate,
    is_valid_roman_substrate,
    is_valid_substrate,
    prepare_substrate,
)
from gpm_types.si.order import Lut, Sk, Sk_lut, Sp, permutation_lut_for_sequence, sequence_key_via_lut
from gpm_types.si.codec import (
    I,
    N_perm,
    decode,
    decode_si_og,
    decode_via_lut,
    decode_word,
    encode,
    encode_si,
    encode_si_og,
    encode_word,
    get_index,
    perm_space,
    perm_space_of,
    permutation_index_via_lut,
)
from gpm_types.si.substance import S, get_ingredients, get_substance, ingredients_og_alpha, substance_og_alpha
from gpm_types.ni import encode_ni, decode_ni, canonical_n, substance_n, NRegistry
from gpm_types.di import encode_di, decode_di_relation, parse_decimal, DRelation
from gpm_types.hi import encode_hi, decode_hi, hi_fingerprint, HiPayload
from gpm_types.classify import PayloadKind, classify_token

__all__ = [
    "AlphabetProfile",
    "ALPHA_ROMAN",
    "ALPHA_ROMAN_LEX_ORDER",
    "ALPHA_GREEK",
    "ALPHA_CYRILLIC",
    "CHAR_ROMAN",
    "CHAR_GREEK_SET",
    "CHAR_CYRILLIC_SET",
    "PRIME_TO_CHAR_ROMAN",
    "PayloadKind",
    "DRelation",
    "HiPayload",
    "I",
    "Lut",
    "MAX_LUT_BUILD_LENGTH",
    "NRegistry",
    "N_perm",
    "PermutationLut",
    "S",
    "Sk",
    "Sk_lut",
    "Sp",
    "build_permutation_lut",
    "canonical_n",
    "classify_token",
    "decode",
    "decode_di_relation",
    "decode_hi",
    "decode_ni",
    "decode_word",
    "encode",
    "encode_di",
    "encode_hi",
    "encode_ni",
    "encode_si",
    "encode_word",
    "get_index",
    "get_ingredients",
    "get_substance",
    "hi_fingerprint",
    "is_roman_symbol",
    "parse_decimal",
    "perm_fits_width",
    "perm_space",
    "perm_space_of",
    "prepare_substrate",
    "substance_n",
    "uses_roman_alpha",
]
