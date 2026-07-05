"""Zentrale Registrierung aller Alphabet-Profile."""

from __future__ import annotations

from alphabets.arabic.map import (
    ALPHA_ARABIC,
    ALPHA_ARABIC_LEX_ORDER,
    CHAR_ARABIC,
)
from alphabets.armenian.map import (
    ALPHA_ARMENIAN,
    ALPHA_ARMENIAN_LEX_ORDER,
    CHAR_ARMENIAN,
)
from alphabets.cyrillic.map import (
    ALPHA_CYRILLIC,
    ALPHA_CYRILLIC_LEX_ORDER,
    CHAR_CYRILLIC,
)
from alphabets.devanagari.map import (
    ALPHA_DEVANAGARI,
    ALPHA_DEVANAGARI_LEX_ORDER,
    CHAR_DEVANAGARI,
)
from alphabets.amharic.map import (
    ALPHA_AMHARIC,
    ALPHA_AMHARIC_LEX_ORDER,
    CHAR_AMHARIC,
)
from alphabets.coptic.map import (
    ALPHA_COPTIC,
    ALPHA_COPTIC_LEX_ORDER,
    CHAR_COPTIC,
)
from alphabets.gurmukhi.map import (
    ALPHA_GURMUKHI,
    ALPHA_GURMUKHI_LEX_ORDER,
    CHAR_GURMUKHI,
)
from alphabets.runic.map import (
    ALPHA_RUNIC,
    ALPHA_RUNIC_LEX_ORDER,
    CHAR_RUNIC,
)
from alphabets.phoenician.map import (
    ALPHA_PHOENICIAN,
    ALPHA_PHOENICIAN_LEX_ORDER,
    CHAR_PHOENICIAN,
)
from alphabets.ugaritic.map import (
    ALPHA_UGARITIC,
    ALPHA_UGARITIC_LEX_ORDER,
    CHAR_UGARITIC,
)
from alphabets.ogham.map import (
    ALPHA_OGHAM,
    ALPHA_OGHAM_LEX_ORDER,
    CHAR_OGHAM,
)
from alphabets.glagolitic.map import (
    ALPHA_GLAGOLITIC,
    ALPHA_GLAGOLITIC_LEX_ORDER,
    CHAR_GLAGOLITIC,
)
from alphabets.gothic.map import (
    ALPHA_GOTHIC,
    ALPHA_GOTHIC_LEX_ORDER,
    CHAR_GOTHIC,
)
from alphabets.mongolian.map import (
    ALPHA_MONGOLIAN,
    ALPHA_MONGOLIAN_LEX_ORDER,
    CHAR_MONGOLIAN,
)
from alphabets.thaana.map import (
    ALPHA_THAANA,
    ALPHA_THAANA_LEX_ORDER,
    CHAR_THAANA,
)
from alphabets.tifinagh.map import (
    ALPHA_TIFINAGH,
    ALPHA_TIFINAGH_LEX_ORDER,
    CHAR_TIFINAGH,
)
from alphabets.bengali.map import (
    ALPHA_BENGALI,
    ALPHA_BENGALI_LEX_ORDER,
    CHAR_BENGALI,
)
from alphabets.telugu.map import (
    ALPHA_TELUGU,
    ALPHA_TELUGU_LEX_ORDER,
    CHAR_TELUGU,
)
from alphabets.javanese.map import (
    ALPHA_JAVANESE,
    ALPHA_JAVANESE_LEX_ORDER,
    CHAR_JAVANESE,
)
from alphabets.old_persian.map import (
    ALPHA_OLD_PERSIAN,
    ALPHA_OLD_PERSIAN_LEX_ORDER,
    CHAR_OLD_PERSIAN,
)
from alphabets.aesthetic_hieroglyphs.map import (
    ALPHA_AESTHETIC_HIEROGLYPHS,
    ALPHA_AESTHETIC_HIEROGLYPHS_LEX_ORDER,
    CHAR_AESTHETIC_HIEROGLYPHS,
)
from alphabets.old_italic.map import (
    ALPHA_OLD_ITALIC,
    ALPHA_OLD_ITALIC_LEX_ORDER,
    CHAR_OLD_ITALIC,
)
from alphabets.old_turkic.map import (
    ALPHA_OLD_TURKIC,
    ALPHA_OLD_TURKIC_LEX_ORDER,
    CHAR_OLD_TURKIC,
)
from alphabets.tamil.map import (
    ALPHA_TAMIL,
    ALPHA_TAMIL_LEX_ORDER,
    CHAR_TAMIL,
)
from alphabets.georgian.map import (
    ALPHA_GEORGIAN,
    ALPHA_GEORGIAN_LEX_ORDER,
    CHAR_GEORGIAN,
)
from alphabets.greek.map import ALPHA_GREEK, ALPHA_GREEK_LEX_ORDER, CHAR_GREEK
from alphabets.hangul.map import ALPHA_HANGUL, ALPHA_HANGUL_LEX_ORDER, CHAR_HANGUL
from alphabets.hebrew.map import ALPHA_HEBREW, ALPHA_HEBREW_LEX_ORDER, CHAR_HEBREW
from alphabets.hiragana.map import (
    ALPHA_HIRAGANA,
    ALPHA_HIRAGANA_LEX_ORDER,
    CHAR_HIRAGANA,
)
from alphabets.katakana.map import (
    ALPHA_KATAKANA,
    ALPHA_KATAKANA_LEX_ORDER,
    CHAR_KATAKANA,
)
from alphabets.og.map import ALPHA_OG, ALPHA_OG_LEX_ORDER, CHAR_OG
from alphabets.profiles import AlphabetProfile
from alphabets.roman.map import ALPHA_ROMAN, ALPHA_ROMAN_LEX_ORDER, PRIME_TO_CHAR_ROMAN
from alphabets.thai.map import ALPHA_THAI, ALPHA_THAI_LEX_ORDER, CHAR_THAI

_PRIME_MAPS: dict[AlphabetProfile, dict[str, int]] = {
    AlphabetProfile.OG: ALPHA_OG,
    AlphabetProfile.ROMAN: ALPHA_ROMAN,
    AlphabetProfile.GREEK: ALPHA_GREEK,
    AlphabetProfile.CYRILLIC: ALPHA_CYRILLIC,
    AlphabetProfile.ARABIC: ALPHA_ARABIC,
    AlphabetProfile.HEBREW: ALPHA_HEBREW,
    AlphabetProfile.DEVANAGARI: ALPHA_DEVANAGARI,
    AlphabetProfile.THAI: ALPHA_THAI,
    AlphabetProfile.HANGUL: ALPHA_HANGUL,
    AlphabetProfile.HIRAGANA: ALPHA_HIRAGANA,
    AlphabetProfile.KATAKANA: ALPHA_KATAKANA,
    AlphabetProfile.ARMENIAN: ALPHA_ARMENIAN,
    AlphabetProfile.GEORGIAN: ALPHA_GEORGIAN,
    AlphabetProfile.GURMUKHI: ALPHA_GURMUKHI,
    AlphabetProfile.TAMIL: ALPHA_TAMIL,
    AlphabetProfile.AMHARIC: ALPHA_AMHARIC,
    AlphabetProfile.COPTIC: ALPHA_COPTIC,
    AlphabetProfile.RUNIC: ALPHA_RUNIC,
    AlphabetProfile.PHOENICIAN: ALPHA_PHOENICIAN,
    AlphabetProfile.UGARITIC: ALPHA_UGARITIC,
    AlphabetProfile.OGHAM: ALPHA_OGHAM,
    AlphabetProfile.GLAGOLITIC: ALPHA_GLAGOLITIC,
    AlphabetProfile.GOTHIC: ALPHA_GOTHIC,
    AlphabetProfile.MONGOLIAN: ALPHA_MONGOLIAN,
    AlphabetProfile.THAANA: ALPHA_THAANA,
    AlphabetProfile.TIFINAGH: ALPHA_TIFINAGH,
    AlphabetProfile.BENGALI: ALPHA_BENGALI,
    AlphabetProfile.TELUGU: ALPHA_TELUGU,
    AlphabetProfile.JAVANESE: ALPHA_JAVANESE,
    AlphabetProfile.OLD_PERSIAN: ALPHA_OLD_PERSIAN,
    AlphabetProfile.AESTHETIC_HIEROGLYPHS: ALPHA_AESTHETIC_HIEROGLYPHS,
    AlphabetProfile.OLD_ITALIC: ALPHA_OLD_ITALIC,
    AlphabetProfile.OLD_TURKIC: ALPHA_OLD_TURKIC,
}

_CHAR_MAPS: dict[AlphabetProfile, dict[int, str]] = {
    AlphabetProfile.OG: CHAR_OG,
    AlphabetProfile.ROMAN: PRIME_TO_CHAR_ROMAN,
    AlphabetProfile.GREEK: CHAR_GREEK,
    AlphabetProfile.CYRILLIC: CHAR_CYRILLIC,
    AlphabetProfile.ARABIC: CHAR_ARABIC,
    AlphabetProfile.HEBREW: CHAR_HEBREW,
    AlphabetProfile.DEVANAGARI: CHAR_DEVANAGARI,
    AlphabetProfile.THAI: CHAR_THAI,
    AlphabetProfile.HANGUL: CHAR_HANGUL,
    AlphabetProfile.HIRAGANA: CHAR_HIRAGANA,
    AlphabetProfile.KATAKANA: CHAR_KATAKANA,
    AlphabetProfile.ARMENIAN: CHAR_ARMENIAN,
    AlphabetProfile.GEORGIAN: CHAR_GEORGIAN,
    AlphabetProfile.GURMUKHI: CHAR_GURMUKHI,
    AlphabetProfile.TAMIL: CHAR_TAMIL,
    AlphabetProfile.AMHARIC: CHAR_AMHARIC,
    AlphabetProfile.COPTIC: CHAR_COPTIC,
    AlphabetProfile.RUNIC: CHAR_RUNIC,
    AlphabetProfile.PHOENICIAN: CHAR_PHOENICIAN,
    AlphabetProfile.UGARITIC: CHAR_UGARITIC,
    AlphabetProfile.OGHAM: CHAR_OGHAM,
    AlphabetProfile.GLAGOLITIC: CHAR_GLAGOLITIC,
    AlphabetProfile.GOTHIC: CHAR_GOTHIC,
    AlphabetProfile.MONGOLIAN: CHAR_MONGOLIAN,
    AlphabetProfile.THAANA: CHAR_THAANA,
    AlphabetProfile.TIFINAGH: CHAR_TIFINAGH,
    AlphabetProfile.BENGALI: CHAR_BENGALI,
    AlphabetProfile.TELUGU: CHAR_TELUGU,
    AlphabetProfile.JAVANESE: CHAR_JAVANESE,
    AlphabetProfile.OLD_PERSIAN: CHAR_OLD_PERSIAN,
    AlphabetProfile.AESTHETIC_HIEROGLYPHS: CHAR_AESTHETIC_HIEROGLYPHS,
    AlphabetProfile.OLD_ITALIC: CHAR_OLD_ITALIC,
    AlphabetProfile.OLD_TURKIC: CHAR_OLD_TURKIC,
}

_LEX_ORDERS: dict[AlphabetProfile, tuple[str, ...]] = {
    AlphabetProfile.OG: ALPHA_OG_LEX_ORDER,
    AlphabetProfile.ROMAN: ALPHA_ROMAN_LEX_ORDER,
    AlphabetProfile.GREEK: ALPHA_GREEK_LEX_ORDER,
    AlphabetProfile.CYRILLIC: ALPHA_CYRILLIC_LEX_ORDER,
    AlphabetProfile.ARABIC: ALPHA_ARABIC_LEX_ORDER,
    AlphabetProfile.HEBREW: ALPHA_HEBREW_LEX_ORDER,
    AlphabetProfile.DEVANAGARI: ALPHA_DEVANAGARI_LEX_ORDER,
    AlphabetProfile.THAI: ALPHA_THAI_LEX_ORDER,
    AlphabetProfile.HANGUL: ALPHA_HANGUL_LEX_ORDER,
    AlphabetProfile.HIRAGANA: ALPHA_HIRAGANA_LEX_ORDER,
    AlphabetProfile.KATAKANA: ALPHA_KATAKANA_LEX_ORDER,
    AlphabetProfile.ARMENIAN: ALPHA_ARMENIAN_LEX_ORDER,
    AlphabetProfile.GEORGIAN: ALPHA_GEORGIAN_LEX_ORDER,
    AlphabetProfile.GURMUKHI: ALPHA_GURMUKHI_LEX_ORDER,
    AlphabetProfile.TAMIL: ALPHA_TAMIL_LEX_ORDER,
    AlphabetProfile.AMHARIC: ALPHA_AMHARIC_LEX_ORDER,
    AlphabetProfile.COPTIC: ALPHA_COPTIC_LEX_ORDER,
    AlphabetProfile.RUNIC: ALPHA_RUNIC_LEX_ORDER,
    AlphabetProfile.PHOENICIAN: ALPHA_PHOENICIAN_LEX_ORDER,
    AlphabetProfile.UGARITIC: ALPHA_UGARITIC_LEX_ORDER,
    AlphabetProfile.OGHAM: ALPHA_OGHAM_LEX_ORDER,
    AlphabetProfile.GLAGOLITIC: ALPHA_GLAGOLITIC_LEX_ORDER,
    AlphabetProfile.GOTHIC: ALPHA_GOTHIC_LEX_ORDER,
    AlphabetProfile.MONGOLIAN: ALPHA_MONGOLIAN_LEX_ORDER,
    AlphabetProfile.THAANA: ALPHA_THAANA_LEX_ORDER,
    AlphabetProfile.TIFINAGH: ALPHA_TIFINAGH_LEX_ORDER,
    AlphabetProfile.BENGALI: ALPHA_BENGALI_LEX_ORDER,
    AlphabetProfile.TELUGU: ALPHA_TELUGU_LEX_ORDER,
    AlphabetProfile.JAVANESE: ALPHA_JAVANESE_LEX_ORDER,
    AlphabetProfile.OLD_PERSIAN: ALPHA_OLD_PERSIAN_LEX_ORDER,
    AlphabetProfile.AESTHETIC_HIEROGLYPHS: ALPHA_AESTHETIC_HIEROGLYPHS_LEX_ORDER,
    AlphabetProfile.OLD_ITALIC: ALPHA_OLD_ITALIC_LEX_ORDER,
    AlphabetProfile.OLD_TURKIC: ALPHA_OLD_TURKIC_LEX_ORDER,
}


def _coerce_profile(profile: AlphabetProfile | str) -> AlphabetProfile:
    if isinstance(profile, str):
        return AlphabetProfile(profile)
    return profile


def prime_map_for_profile(profile: AlphabetProfile | str) -> dict[str, int]:
    key = _coerce_profile(profile)
    try:
        return _PRIME_MAPS[key]
    except KeyError as exc:
        raise ValueError(f"Unbekanntes AlphabetProfile: {profile!r}") from exc


def char_map_for_profile(profile: AlphabetProfile | str) -> dict[int, str]:
    key = _coerce_profile(profile)
    try:
        return _CHAR_MAPS[key]
    except KeyError as exc:
        raise ValueError(f"Unbekanntes AlphabetProfile: {profile!r}") from exc


def lex_order_for_profile(profile: AlphabetProfile | str) -> tuple[str, ...]:
    key = _coerce_profile(profile)
    try:
        return _LEX_ORDERS[key]
    except KeyError as exc:
        raise ValueError(f"Unbekanntes AlphabetProfile: {profile!r}") from exc


def all_profiles() -> tuple[AlphabetProfile, ...]:
    return tuple(_PRIME_MAPS.keys())
