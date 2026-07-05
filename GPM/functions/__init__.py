"""GPM Grundfunktionen — Phase 3."""

from alphabets.profiles import AlphabetProfile
from alphabets.registry import (
    all_profiles,
    char_map_for_profile,
    lex_order_for_profile,
    prime_map_for_profile,
)
from alphabets.roman.map import (
    ALPHA_ROMAN,
    ALPHA_ROMAN_LEX_ORDER,
    CHAR_ROMAN,
    PRIME_TO_CHAR_ROMAN,
    is_roman_symbol,
    uses_roman_alpha,
)
from alphabets.greek.map import ALPHA_GREEK, CHAR_GREEK_SET
from alphabets.cyrillic.map import ALPHA_CYRILLIC, CHAR_CYRILLIC_SET
from alphabets.arabic.map import ALPHA_ARABIC, CHAR_ARABIC_SET
from alphabets.hebrew.map import ALPHA_HEBREW, CHAR_HEBREW_SET
from alphabets.gurmukhi.map import ALPHA_GURMUKHI, CHAR_GURMUKHI_SET
from alphabets.tamil.map import ALPHA_TAMIL, CHAR_TAMIL_SET
from alphabets.amharic.map import ALPHA_AMHARIC, CHAR_AMHARIC_SET
from alphabets.coptic.map import ALPHA_COPTIC, CHAR_COPTIC_SET
from alphabets.runic.map import ALPHA_RUNIC, CHAR_RUNIC_SET
from alphabets.phoenician.map import ALPHA_PHOENICIAN, CHAR_PHOENICIAN_SET
from alphabets.ugaritic.map import ALPHA_UGARITIC, CHAR_UGARITIC_SET
from alphabets.ogham.map import ALPHA_OGHAM, CHAR_OGHAM_SET
from alphabets.glagolitic.map import ALPHA_GLAGOLITIC, CHAR_GLAGOLITIC_SET
from alphabets.gothic.map import ALPHA_GOTHIC, CHAR_GOTHIC_SET
from alphabets.mongolian.map import ALPHA_MONGOLIAN, CHAR_MONGOLIAN_SET
from alphabets.thaana.map import ALPHA_THAANA, CHAR_THAANA_SET
from alphabets.tifinagh.map import ALPHA_TIFINAGH, CHAR_TIFINAGH_SET
from alphabets.bengali.map import ALPHA_BENGALI, CHAR_BENGALI_SET
from alphabets.telugu.map import ALPHA_TELUGU, CHAR_TELUGU_SET
from alphabets.javanese.map import ALPHA_JAVANESE, CHAR_JAVANESE_SET
from alphabets.old_persian.map import ALPHA_OLD_PERSIAN, CHAR_OLD_PERSIAN_SET
from alphabets.aesthetic_hieroglyphs.map import (
    ALPHA_AESTHETIC_HIEROGLYPHS,
    CHAR_AESTHETIC_HIEROGLYPHS_SET,
)
from alphabets.old_italic.map import ALPHA_OLD_ITALIC, CHAR_OLD_ITALIC_SET
from alphabets.old_turkic.map import ALPHA_OLD_TURKIC, CHAR_OLD_TURKIC_SET
from perm.lut import (
    ALPHA_ROMAN_SINGLETON_LUTS,
    MAX_LUT_BUILD_LENGTH,
    PermutationLut,
    build_permutation_lut,
    build_permutation_lut_for_sequence,
    get_permutation_lut,
    get_singleton_lut,
)
from perm.multiset import calc_total_perms, perm_decode, perm_fits_width, perm_index, perm_space
from alphabets.normalize import (
    is_valid_substrate,
    normalize_latin,
    prepare_substrate,
)
from alphabets.roman.normalize import is_valid_og_substrate, is_valid_roman_substrate
from gpm_types.si.order import Lut, Sk, Sk_lut, Sp, permutation_lut_for_sequence, sequence_key_via_lut
from gpm_types.si.codec import (
    I,
    N_perm,
    decode,
    decode_si,
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
    "ALPHA_ARABIC",
    "CHAR_ROMAN",
    "CHAR_GREEK_SET",
    "CHAR_CYRILLIC_SET",
    "CHAR_ARABIC_SET",
    "CHAR_HEBREW_SET",
    "CHAR_GURMUKHI_SET",
    "CHAR_TAMIL_SET",
    "CHAR_AMHARIC_SET",
    "CHAR_COPTIC_SET",
    "CHAR_RUNIC_SET",
    "CHAR_PHOENICIAN_SET",
    "CHAR_UGARITIC_SET",
    "CHAR_OGHAM_SET",
    "CHAR_GLAGOLITIC_SET",
    "CHAR_GOTHIC_SET",
    "CHAR_MONGOLIAN_SET",
    "CHAR_THAANA_SET",
    "CHAR_TIFINAGH_SET",
    "CHAR_BENGALI_SET",
    "CHAR_TELUGU_SET",
    "CHAR_JAVANESE_SET",
    "CHAR_OLD_PERSIAN_SET",
    "CHAR_AESTHETIC_HIEROGLYPHS_SET",
    "CHAR_OLD_ITALIC_SET",
    "CHAR_OLD_TURKIC_SET",
    "ALPHA_GURMUKHI",
    "ALPHA_TAMIL",
    "ALPHA_AMHARIC",
    "ALPHA_COPTIC",
    "ALPHA_RUNIC",
    "ALPHA_PHOENICIAN",
    "ALPHA_UGARITIC",
    "ALPHA_OGHAM",
    "ALPHA_GLAGOLITIC",
    "ALPHA_GOTHIC",
    "ALPHA_MONGOLIAN",
    "ALPHA_THAANA",
    "ALPHA_TIFINAGH",
    "ALPHA_BENGALI",
    "ALPHA_TELUGU",
    "ALPHA_JAVANESE",
    "ALPHA_OLD_PERSIAN",
    "ALPHA_AESTHETIC_HIEROGLYPHS",
    "ALPHA_OLD_ITALIC",
    "ALPHA_OLD_TURKIC",
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
    "all_profiles",
    "build_permutation_lut",
    "canonical_n",
    "char_map_for_profile",
    "classify_token",
    "decode",
    "decode_di_relation",
    "decode_hi",
    "decode_ni",
    "decode_si",
    "decode_word",
    "encode",
    "encode_di",
    "encode_hi",
    "encode_ni",
    "encode_si",
    "encode_word",
    "get_index",
    "get_ingredients",
    "get_singleton_lut",
    "get_substance",
    "hi_fingerprint",
    "is_roman_symbol",
    "lex_order_for_profile",
    "normalize_latin",
    "parse_decimal",
    "perm_fits_width",
    "perm_space",
    "perm_space_of",
    "prepare_substrate",
    "prime_map_for_profile",
    "substance_n",
    "uses_roman_alpha",
]
