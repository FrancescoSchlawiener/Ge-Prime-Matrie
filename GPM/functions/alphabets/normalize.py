"""Zentraler prepare_substrate-Dispatcher für alle Profile."""

from __future__ import annotations

import unicodedata

from alphabets.profiles import AlphabetProfile
from alphabets.roman.map import CHAR_ROMAN

_UMLAUT_MAP: dict[str, str] = {
    "ä": "ae", "ö": "oe", "ü": "ue",
    "Ä": "AE", "Ö": "OE", "Ü": "UE",
}


def _eszett_aware_upper(text: str) -> str:
    return "".join(ch if ch == "ß" else ch.upper() for ch in text)


def normalize_latin(word: str) -> str:
    word = unicodedata.normalize("NFC", word)
    for src, dst in _UMLAUT_MAP.items():
        word = word.replace(src, dst)
    word = word.replace("ẞ", "ß")
    return _eszett_aware_upper(word)


def prepare_substrate(raw: str, profile: AlphabetProfile | str = AlphabetProfile.ROMAN) -> str:
    text = unicodedata.normalize("NFC", (raw or "").strip())
    if isinstance(profile, str):
        profile = AlphabetProfile(profile)

    if profile is AlphabetProfile.GREEK:
        from alphabets.greek.normalize import normalize_greek
        return normalize_greek(text)
    if profile is AlphabetProfile.CYRILLIC:
        from alphabets.cyrillic.normalize import normalize_cyrillic
        return normalize_cyrillic(text)
    if profile is AlphabetProfile.ARABIC:
        from alphabets.arabic.normalize import normalize_arabic
        return normalize_arabic(text)
    if profile is AlphabetProfile.HEBREW:
        from alphabets.hebrew.normalize import normalize_hebrew
        return normalize_hebrew(text)
    if profile is AlphabetProfile.DEVANAGARI:
        from alphabets.devanagari.normalize import normalize_devanagari
        return normalize_devanagari(text)
    if profile is AlphabetProfile.THAI:
        from alphabets.thai.normalize import normalize_thai
        return normalize_thai(text)
    if profile is AlphabetProfile.HANGUL:
        from alphabets.hangul.normalize import normalize_hangul
        return normalize_hangul(text)
    if profile is AlphabetProfile.HIRAGANA:
        from alphabets.hiragana.normalize import normalize_hiragana
        return normalize_hiragana(text)
    if profile is AlphabetProfile.KATAKANA:
        from alphabets.katakana.normalize import normalize_katakana
        return normalize_katakana(text)
    if profile is AlphabetProfile.ARMENIAN:
        from alphabets.armenian.normalize import normalize_armenian
        return normalize_armenian(text)
    if profile is AlphabetProfile.GEORGIAN:
        from alphabets.georgian.normalize import normalize_georgian
        return normalize_georgian(text)
    if profile is AlphabetProfile.GURMUKHI:
        from alphabets.gurmukhi.normalize import normalize_gurmukhi
        return normalize_gurmukhi(text)
    if profile is AlphabetProfile.TAMIL:
        from alphabets.tamil.normalize import normalize_tamil
        return normalize_tamil(text)
    if profile is AlphabetProfile.AMHARIC:
        from alphabets.amharic.normalize import normalize_amharic
        return normalize_amharic(text)
    if profile is AlphabetProfile.COPTIC:
        from alphabets.coptic.normalize import normalize_coptic
        return normalize_coptic(text)
    if profile is AlphabetProfile.RUNIC:
        from alphabets.runic.normalize import normalize_runic
        return normalize_runic(text)
    if profile is AlphabetProfile.PHOENICIAN:
        from alphabets.phoenician.normalize import normalize_phoenician
        return normalize_phoenician(text)
    if profile is AlphabetProfile.UGARITIC:
        from alphabets.ugaritic.normalize import normalize_ugaritic
        return normalize_ugaritic(text)
    if profile is AlphabetProfile.OGHAM:
        from alphabets.ogham.normalize import normalize_ogham
        return normalize_ogham(text)
    if profile is AlphabetProfile.GLAGOLITIC:
        from alphabets.glagolitic.normalize import normalize_glagolitic
        return normalize_glagolitic(text)
    if profile is AlphabetProfile.GOTHIC:
        from alphabets.gothic.normalize import normalize_gothic
        return normalize_gothic(text)
    if profile is AlphabetProfile.MONGOLIAN:
        from alphabets.mongolian.normalize import normalize_mongolian
        return normalize_mongolian(text)
    if profile is AlphabetProfile.THAANA:
        from alphabets.thaana.normalize import normalize_thaana
        return normalize_thaana(text)
    if profile is AlphabetProfile.TIFINAGH:
        from alphabets.tifinagh.normalize import normalize_tifinagh
        return normalize_tifinagh(text)
    if profile is AlphabetProfile.BENGALI:
        from alphabets.bengali.normalize import normalize_bengali
        return normalize_bengali(text)
    if profile is AlphabetProfile.TELUGU:
        from alphabets.telugu.normalize import normalize_telugu
        return normalize_telugu(text)
    if profile is AlphabetProfile.JAVANESE:
        from alphabets.javanese.normalize import normalize_javanese
        return normalize_javanese(text)
    if profile is AlphabetProfile.OLD_PERSIAN:
        from alphabets.old_persian.normalize import normalize_old_persian
        return normalize_old_persian(text)
    if profile is AlphabetProfile.AESTHETIC_HIEROGLYPHS:
        from alphabets.aesthetic_hieroglyphs.normalize import normalize_aesthetic_hieroglyphs
        return normalize_aesthetic_hieroglyphs(text)
    if profile is AlphabetProfile.OLD_ITALIC:
        from alphabets.old_italic.normalize import normalize_old_italic
        return normalize_old_italic(text)
    if profile is AlphabetProfile.OLD_TURKIC:
        from alphabets.old_turkic.normalize import normalize_old_turkic
        return normalize_old_turkic(text)
    return normalize_latin(text)


def is_valid_substrate(text: str, profile: AlphabetProfile | str = AlphabetProfile.ROMAN) -> bool:
    if len(text) < 1:
        return False
    if profile in (AlphabetProfile.ROMAN, "roman"):
        return all(ch in CHAR_ROMAN for ch in text)
    from alphabets.registry import prime_map_for_profile

    prime_map = prime_map_for_profile(profile)
    return all(ch in prime_map for ch in text)
